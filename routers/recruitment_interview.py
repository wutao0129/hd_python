from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import RecruitmentInterview
from middleware import get_current_user

router = APIRouter(prefix="/api/recruitment-interview", tags=["招聘管理-面试"])


# ---------- Schemas ----------

class InterviewCreate(BaseModel):
    resumeId: int
    positionId: int
    round: int = 1
    interviewType: str
    scheduledTime: str
    interviewerIds: Optional[str] = None
    interviewerNames: Optional[str] = None
    location: Optional[str] = None

    class Config:
        populate_by_name = True


class FeedbackSubmit(BaseModel):
    feedback: str
    score: Optional[int] = None
    result: str

    class Config:
        populate_by_name = True


# ---------- Helper Functions ----------

def _to_dict(obj: RecruitmentInterview) -> dict:
    """转换模型为字典"""
    return {
        "id": obj.id,
        "resumeId": obj.resume_id,
        "positionId": obj.position_id,
        "round": obj.round,
        "interviewType": obj.interview_type,
        "scheduledTime": obj.scheduled_time.isoformat(),
        "interviewerIds": obj.interviewer_ids,
        "interviewerNames": obj.interviewer_names,
        "location": obj.location,
        "status": obj.status,
        "feedback": obj.feedback,
        "score": obj.score,
        "result": obj.result,
        "createdAt": obj.created_at.isoformat(),
        "updatedAt": obj.updated_at.isoformat(),
    }


def _get_or_404(db: Session, interview_id: int) -> RecruitmentInterview:
    """获取面试记录或返回404"""
    obj = db.query(RecruitmentInterview).filter_by(id=interview_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="面试记录不存在")
    return obj


# ---------- API Routes ----------

@router.get("/list")
def get_list(
    resumeId: Optional[int] = None,
    positionId: Optional[int] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """列表查询（支持分页、筛选、排序）"""
    query = db.query(RecruitmentInterview)

    # 简历筛选
    if resumeId:
        query = query.filter_by(resume_id=resumeId)

    # 岗位筛选
    if positionId:
        query = query.filter_by(position_id=positionId)

    # 状态筛选
    if status:
        query = query.filter_by(status=status)

    # 分页
    total = query.count()
    items = query.order_by(RecruitmentInterview.scheduled_time.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "code": 200,
        "message": "success",
        "data": {
            "total": total,
            "page": page,
            "pageSize": page_size,
            "items": [_to_dict(item) for item in items]
        }
    }


@router.get("/{interview_id}")
def get_detail(interview_id: int, db: Session = Depends(get_db)):
    """详情查询"""
    obj = _get_or_404(db, interview_id)
    return {"code": 200, "message": "success", "data": _to_dict(obj)}


@router.post("")
def create(
    data: InterviewCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建面试记录"""
    obj = RecruitmentInterview(
        resume_id=data.resumeId,
        position_id=data.positionId,
        round=data.round,
        interview_type=data.interviewType,
        scheduled_time=datetime.fromisoformat(data.scheduledTime.replace('Z', '+00:00')),
        interviewer_ids=data.interviewerIds,
        interviewer_names=data.interviewerNames,
        location=data.location,
        status="scheduled",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"code": 200, "message": "创建成功", "data": _to_dict(obj)}


@router.post("/{interview_id}/feedback")
def submit_feedback(
    interview_id: int,
    data: FeedbackSubmit,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """提交面试反馈"""
    obj = _get_or_404(db, interview_id)

    # 更新反馈信息
    obj.feedback = data.feedback
    obj.score = data.score
    obj.result = data.result
    obj.status = "completed"
    obj.updated_at = datetime.now()
    db.commit()
    db.refresh(obj)

    return {"code": 200, "message": "反馈提交成功", "data": _to_dict(obj)}


@router.delete("/{interview_id}")
def delete(interview_id: int, db: Session = Depends(get_db)):
    """删除面试记录"""
    obj = _get_or_404(db, interview_id)
    db.delete(obj)
    db.commit()
    return {"code": 200, "message": "删除成功"}
