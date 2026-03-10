from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session
from database import get_db
from models import RecruitmentResume
from middleware import get_current_user

router = APIRouter(prefix="/api/recruitment-resume", tags=["招聘管理-简历"])


# ---------- Schemas ----------

class ResumeCreate(BaseModel):
    name: str
    age: int
    school: str
    degree: str
    experience: int
    currentCompany: str
    skills: dict
    scores: dict
    appliedPosition: str
    department: str

    class Config:
        populate_by_name = True


class ResumeUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    school: Optional[str] = None
    degree: Optional[str] = None
    experience: Optional[int] = None
    currentCompany: Optional[str] = None
    skills: Optional[dict] = None
    scores: Optional[dict] = None
    appliedPosition: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None

    class Config:
        populate_by_name = True


class ScheduleInterviewRequest(BaseModel):
    interviewType: str
    scheduledTime: str
    interviewerIds: Optional[str] = None
    interviewerNames: Optional[str] = None
    location: Optional[str] = None


class RejectRequest(BaseModel):
    reason: str


# ---------- Helper Functions ----------

def _to_dict(obj: RecruitmentResume) -> dict:
    """转换模型为字典"""
    return {
        "id": obj.id,
        "name": obj.name,
        "age": obj.age,
        "school": obj.school,
        "degree": obj.degree,
        "experience": obj.experience,
        "status": obj.status,
        "appliedAt": obj.applied_at.isoformat(),
        "currentCompany": obj.current_company,
        "skills": obj.skills,
        "scores": obj.scores,
        "appliedPosition": obj.applied_position,
        "department": obj.department,
    }


def _get_or_404(db: Session, resume_id: int) -> RecruitmentResume:
    """获取简历或返回404"""
    obj = db.query(RecruitmentResume).filter_by(id=resume_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="简历不存在")
    return obj


# ---------- API Routes ----------

@router.get("/list")
def get_list(
    appliedPosition: Optional[str] = None,
    status: Optional[str] = None,
    department: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """列表查询（支持分页、筛选、排序）"""
    query = db.query(RecruitmentResume)

    # 岗位筛选
    if appliedPosition:
        query = query.filter_by(applied_position=appliedPosition)

    # 状态筛选
    if status:
        query = query.filter_by(status=status)

    # 部门筛选
    if department:
        query = query.filter_by(department=department)

    # 关键词搜索
    if keyword:
        query = query.filter(
            or_(
                RecruitmentResume.name.like(f"%{keyword}%"),
                RecruitmentResume.school.like(f"%{keyword}%"),
                RecruitmentResume.current_company.like(f"%{keyword}%")
            )
        )

    # 分页
    total = query.count()
    items = query.order_by(RecruitmentResume.applied_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

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


@router.get("/{resume_id}")
def get_detail(resume_id: int, db: Session = Depends(get_db)):
    """详情查询"""
    obj = _get_or_404(db, resume_id)
    return {"code": 200, "message": "success", "data": _to_dict(obj)}


@router.post("")
def create(
    data: ResumeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建简历"""
    obj = RecruitmentResume(
        name=data.name,
        age=data.age,
        school=data.school,
        degree=data.degree,
        experience=data.experience,
        current_company=data.currentCompany,
        skills=data.skills,
        scores=data.scores,
        applied_position=data.appliedPosition,
        department=data.department,
        status="pending",
        applied_at=datetime.now()
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"code": 200, "message": "创建成功", "data": _to_dict(obj)}


@router.put("/{resume_id}")
def update(
    resume_id: int,
    data: ResumeUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新简历"""
    obj = _get_or_404(db, resume_id)

    # 更新字段
    if data.name is not None:
        obj.name = data.name
    if data.age is not None:
        obj.age = data.age
    if data.school is not None:
        obj.school = data.school
    if data.degree is not None:
        obj.degree = data.degree
    if data.experience is not None:
        obj.experience = data.experience
    if data.currentCompany is not None:
        obj.current_company = data.currentCompany
    if data.skills is not None:
        obj.skills = data.skills
    if data.scores is not None:
        obj.scores = data.scores
    if data.appliedPosition is not None:
        obj.applied_position = data.appliedPosition
    if data.department is not None:
        obj.department = data.department
    if data.status is not None:
        obj.status = data.status

    db.commit()
    db.refresh(obj)
    return {"code": 200, "message": "更新成功", "data": _to_dict(obj)}


@router.delete("/{resume_id}")
def delete(resume_id: int, db: Session = Depends(get_db)):
    """删除简历"""
    obj = _get_or_404(db, resume_id)
    db.delete(obj)
    db.commit()
    return {"code": 200, "message": "删除成功"}


@router.post("/{resume_id}/schedule-interview")
def schedule_interview(
    resume_id: int,
    data: ScheduleInterviewRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """安排面试"""
    obj = _get_or_404(db, resume_id)

    # 更新简历状态
    obj.status = "interviewing"
    db.commit()

    # TODO: 创建面试记录

    return {"code": 200, "message": "面试安排成功", "data": _to_dict(obj)}


@router.post("/{resume_id}/reject")
def reject(
    resume_id: int,
    data: RejectRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """淘汰候选人"""
    obj = _get_or_404(db, resume_id)

    # 更新简历状态
    obj.status = "rejected"
    db.commit()

    return {"code": 200, "message": "已淘汰", "data": _to_dict(obj)}
