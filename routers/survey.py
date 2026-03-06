import hashlib
import json
from datetime import datetime
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import Questionnaire, QuestionnaireAnswer, QuestionnaireAnswerDetail, QuestionnaireQuestion

router = APIRouter(prefix="/api/survey", tags=["survey"])


class AnswerItem(BaseModel):
    question_id: int
    value: Any  # 字符串或列表


class UserInfo(BaseModel):
    name: str
    company: str
    position: str
    phone: str
    email: str


class SubmitBody(BaseModel):
    submit_token: str  # 前端 localStorage 生成的唯一 token
    user_info: UserInfo
    answers: list[AnswerItem]


@router.get("/{uuid}")
def get_survey(uuid: str, db: Session = Depends(get_db)):
    q = db.query(Questionnaire).filter_by(uuid=uuid).first()
    if not q:
        raise HTTPException(404, "问卷不存在")
    if q.status == 2 or (q.deadline and q.deadline < datetime.now()):
        raise HTTPException(410, "问卷已结束")
    questions = (
        db.query(QuestionnaireQuestion)
        .filter_by(questionnaire_id=q.id)
        .order_by(QuestionnaireQuestion.sort_order)
        .all()
    )
    return {
        "id": q.id,
        "title": q.title,
        "description": q.description,
        "deadline": q.deadline.isoformat() if q.deadline else None,
        "banner_url": q.banner_url,
        "brand_text": q.brand_text,
        "privacy_enabled": q.privacy_enabled,
        "privacy_title": q.privacy_title,
        "privacy_items": q.privacy_items,
        "questions": [
            {
                "id": qq.id, "type": qq.type, "title": qq.title,
                "required": qq.required, "options": qq.options,
                "rating_max": qq.rating_max, "rating_labels": qq.rating_labels,
                "max_length": qq.max_length,
            }
            for qq in questions
        ],
    }


@router.post("/{uuid}/submit", status_code=201)
def submit_survey(uuid: str, body: SubmitBody, db: Session = Depends(get_db)):
    q = db.query(Questionnaire).filter_by(uuid=uuid).first()
    if not q:
        raise HTTPException(404, "问卷不存在")
    if q.status == 2 or (q.deadline and q.deadline < datetime.now()):
        raise HTTPException(410, "问卷已结束")
    if db.query(QuestionnaireAnswer).filter_by(submit_token=body.submit_token).first():
        raise HTTPException(409, "已提交过")

    answer = QuestionnaireAnswer(
        questionnaire_id=q.id,
        submit_token=body.submit_token,
        user_name=body.user_info.name,
        user_company=body.user_info.company,
        user_position=body.user_info.position,
        user_phone=body.user_info.phone,
        user_email=body.user_info.email
    )
    db.add(answer)
    db.flush()
    for item in body.answers:
        value = json.dumps(item.value, ensure_ascii=False) if isinstance(item.value, list) else str(item.value)
        db.add(QuestionnaireAnswerDetail(answer_id=answer.id, question_id=item.question_id, value=value))
    db.commit()
    return {"message": "提交成功"}
