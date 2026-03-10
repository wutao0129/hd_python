from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import RecruitmentJobProfile
from middleware import get_current_user

router = APIRouter(prefix="/api/recruitment-job-profile", tags=["招聘管理-岗位画像"])


# ---------- Schemas ----------

class JobProfileCreate(BaseModel):
    positionId: int
    education: str
    workYears: str
    skills: str
    certifications: Optional[str] = None
    personality: Optional[str] = None

    class Config:
        populate_by_name = True


class JobProfileUpdate(BaseModel):
    education: Optional[str] = None
    workYears: Optional[str] = None
    skills: Optional[str] = None
    certifications: Optional[str] = None
    personality: Optional[str] = None

    class Config:
        populate_by_name = True


# ---------- Helper Functions ----------

def _to_dict(obj: RecruitmentJobProfile) -> dict:
    """转换模型为字典"""
    return {
        "id": obj.id,
        "positionId": obj.position_id,
        "education": obj.education,
        "workYears": obj.work_years,
        "skills": obj.skills,
        "certifications": obj.certifications,
        "personality": obj.personality,
        "createdAt": obj.created_at.isoformat(),
        "updatedAt": obj.updated_at.isoformat(),
    }


def _get_or_404(db: Session, profile_id: int) -> RecruitmentJobProfile:
    """获取岗位画像或返回404"""
    obj = db.query(RecruitmentJobProfile).filter_by(id=profile_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="岗位画像不存在")
    return obj


# ---------- API Routes ----------

@router.get("/list")
def get_list(
    positionId: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """列表查询（支持分页、筛选、排序）"""
    query = db.query(RecruitmentJobProfile)

    # 岗位筛选
    if positionId:
        query = query.filter_by(position_id=positionId)

    # 分页
    total = query.count()
    items = query.order_by(RecruitmentJobProfile.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

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


@router.get("/{profile_id}")
def get_detail(profile_id: int, db: Session = Depends(get_db)):
    """详情查询"""
    obj = _get_or_404(db, profile_id)
    return {"code": 200, "message": "success", "data": _to_dict(obj)}


@router.post("")
def create(
    data: JobProfileCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建岗位画像"""
    obj = RecruitmentJobProfile(
        position_id=data.positionId,
        education=data.education,
        work_years=data.workYears,
        skills=data.skills,
        certifications=data.certifications,
        personality=data.personality,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"code": 200, "message": "创建成功", "data": _to_dict(obj)}


@router.put("/{profile_id}")
def update(
    profile_id: int,
    data: JobProfileUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新岗位画像"""
    obj = _get_or_404(db, profile_id)

    # 更新字段
    if data.education is not None:
        obj.education = data.education
    if data.workYears is not None:
        obj.work_years = data.workYears
    if data.skills is not None:
        obj.skills = data.skills
    if data.certifications is not None:
        obj.certifications = data.certifications
    if data.personality is not None:
        obj.personality = data.personality

    obj.updated_at = datetime.now()
    db.commit()
    db.refresh(obj)
    return {"code": 200, "message": "更新成功", "data": _to_dict(obj)}
