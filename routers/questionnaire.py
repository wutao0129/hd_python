import uuid as uuid_lib
from datetime import datetime
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import Questionnaire, QuestionnaireQuestion

router = APIRouter(prefix="/api/questionnaires", tags=["questionnaire"])


# ---------- Schemas ----------

class QuestionIn(BaseModel):
    type: str
    title: str
    required: int = 1
    sort_order: int = 0
    options: Optional[Any] = None
    rating_max: Optional[int] = None
    rating_labels: Optional[Any] = None
    max_length: Optional[int] = None


class QuestionnaireIn(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    questions: list[QuestionIn] = []
    banner_url: Optional[str] = None
    brand_text: Optional[str] = None
    privacy_enabled: Optional[int] = 0
    privacy_title: Optional[str] = None
    privacy_items: Optional[Any] = None


# ---------- Routes ----------

@router.get("")
def list_questionnaires(db: Session = Depends(get_db)):
    rows = db.query(Questionnaire).order_by(Questionnaire.created_at.desc()).all()
    return [_q_dict(q) for q in rows]


@router.get("/{qid}")
def get_questionnaire(qid: int, db: Session = Depends(get_db)):
    q = _get_or_404(db, qid)
    questions = db.query(QuestionnaireQuestion).filter_by(questionnaire_id=qid).order_by(QuestionnaireQuestion.sort_order).all()
    data = _q_dict(q)
    data['questions'] = [
        {
            'id': qq.id, 'type': qq.type, 'title': qq.title,
            'required': qq.required, 'options': qq.options,
            'rating_max': qq.rating_max, 'rating_labels': qq.rating_labels,
            'max_length': qq.max_length, 'placeholder': None,
        }
        for qq in questions
    ]
    return data


@router.post("", status_code=201)
def create_questionnaire(body: QuestionnaireIn, db: Session = Depends(get_db)):
    q = Questionnaire(
        title=body.title,
        description=body.description,
        deadline=body.deadline,
        banner_url=body.banner_url,
        brand_text=body.brand_text,
        privacy_enabled=body.privacy_enabled,
        privacy_title=body.privacy_title,
        privacy_items=body.privacy_items
    )
    db.add(q)
    db.flush()
    for i, qq in enumerate(body.questions):
        db.add(QuestionnaireQuestion(questionnaire_id=q.id, sort_order=i, **qq.model_dump(exclude={"sort_order"})))
    db.commit()
    db.refresh(q)
    return _q_dict(q)


@router.put("/{qid}")
def update_questionnaire(qid: int, body: QuestionnaireIn, db: Session = Depends(get_db)):
    q = _get_or_404(db, qid)
    q.title = body.title
    q.description = body.description
    q.deadline = body.deadline
    q.banner_url = body.banner_url
    q.brand_text = body.brand_text
    q.privacy_enabled = body.privacy_enabled
    q.privacy_title = body.privacy_title
    q.privacy_items = body.privacy_items
    db.query(QuestionnaireQuestion).filter_by(questionnaire_id=qid).delete()
    for i, qq in enumerate(body.questions):
        db.add(QuestionnaireQuestion(questionnaire_id=qid, sort_order=i, **qq.model_dump(exclude={"sort_order"})))
    db.commit()
    return _q_dict(q)


@router.delete("/{qid}", status_code=204)
def delete_questionnaire(qid: int, db: Session = Depends(get_db)):
    q = _get_or_404(db, qid)
    db.query(QuestionnaireQuestion).filter_by(questionnaire_id=qid).delete()
    db.delete(q)
    db.commit()


@router.post("/{qid}/publish")
def publish_questionnaire(qid: int, db: Session = Depends(get_db)):
    q = _get_or_404(db, qid)
    if not q.uuid:
        q.uuid = str(uuid_lib.uuid4())
    q.status = 1
    db.commit()
    return {"uuid": q.uuid, "share_url": f"/survey/{q.uuid}"}


@router.post("/{qid}/unpublish")
def unpublish_questionnaire(qid: int, db: Session = Depends(get_db)):
    q = _get_or_404(db, qid)
    if q.status != 1:
        raise HTTPException(400, "只有进行中的问卷才能退回草稿")
    q.status = 0
    db.commit()
    return {"id": q.id, "status": q.status}


@router.get("/{qid}/results")
def get_results(qid: int, db: Session = Depends(get_db)):
    from models import QuestionnaireAnswer, QuestionnaireAnswerDetail
    _get_or_404(db, qid)
    questions = db.query(QuestionnaireQuestion).filter_by(questionnaire_id=qid).order_by(QuestionnaireQuestion.sort_order).all()
    total = db.query(QuestionnaireAnswer).filter_by(questionnaire_id=qid).count()
    result = []
    for q in questions:
        details = (
            db.query(QuestionnaireAnswerDetail.value)
            .join(QuestionnaireAnswer, QuestionnaireAnswer.id == QuestionnaireAnswerDetail.answer_id)
            .filter(QuestionnaireAnswer.questionnaire_id == qid, QuestionnaireAnswerDetail.question_id == q.id)
            .all()
        )
        values = [d.value for d in details]
        result.append({"question_id": q.id, "title": q.title, "type": q.type, "total": len(values), "values": values})
    return {"total_submissions": total, "questions": result}


# ---------- Helpers ----------

def _get_or_404(db: Session, qid: int) -> Questionnaire:
    q = db.get(Questionnaire, qid)
    if not q:
        raise HTTPException(404, "问卷不存在")
    return q


def _q_dict(q: Questionnaire) -> dict:
    return {
        "id": q.id, "title": q.title, "description": q.description,
        "status": q.status, "uuid": q.uuid,
        "deadline": q.deadline.isoformat() if q.deadline else None,
        "created_at": q.created_at.isoformat(),
        "banner_url": q.banner_url,
        "brand_text": q.brand_text,
        "privacy_enabled": q.privacy_enabled,
        "privacy_title": q.privacy_title,
        "privacy_items": q.privacy_items,
    }
