import io
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from sqlalchemy.orm import Session
from database import get_db
from models import Questionnaire, QuestionnaireAnswer, QuestionnaireAnswerDetail, QuestionnaireQuestion

router = APIRouter(prefix="/api/questionnaires", tags=["export"])


@router.get("/{qid}/export")
def export_excel(qid: int, db: Session = Depends(get_db)):
    q = db.get(Questionnaire, qid)
    if not q:
        raise HTTPException(404, "问卷不存在")

    questions = (
        db.query(QuestionnaireQuestion)
        .filter_by(questionnaire_id=qid)
        .order_by(QuestionnaireQuestion.sort_order)
        .all()
    )
    answers = db.query(QuestionnaireAnswer).filter_by(questionnaire_id=qid).all()

    wb = Workbook()
    ws = wb.active
    ws.title = "答题数据"

    # 表头
    headers = ["提交时间", "submit_token"] + [f"Q{i+1}: {qq.title}" for i, qq in enumerate(questions)]
    ws.append(headers)

    # 数据行
    for ans in answers:
        details = {d.question_id: d.value for d in db.query(QuestionnaireAnswerDetail).filter_by(answer_id=ans.id).all()}
        row = [ans.submitted_at.isoformat(), ans.submit_token]
        for qq in questions:
            val = details.get(qq.id, "")
            try:
                parsed = json.loads(val)
                row.append(", ".join(parsed) if isinstance(parsed, list) else val)
            except Exception:
                row.append(val or "")
        ws.append(row)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    filename = f"questionnaire_{qid}.xlsx"
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
