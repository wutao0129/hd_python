from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session
from database import get_db
from models import RecruitmentPosition
from middleware import get_current_user

router = APIRouter(prefix="/api/recruitment-position", tags=["招聘管理-岗位"])


# ---------- Schemas ----------

class PositionCreate(BaseModel):
    title: str
    department: str
    salaryRange: str
    responsibilities: str
    location: str
    headcount: int = 1
    approvalId: Optional[str] = None

    class Config:
        populate_by_name = True


class PositionUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    salaryRange: Optional[str] = None
    responsibilities: Optional[str] = None
    location: Optional[str] = None
    headcount: Optional[int] = None
    status: Optional[str] = None
    candidates: Optional[int] = None
    approvalId: Optional[str] = None
    publishedChannels: Optional[dict] = None

    class Config:
        populate_by_name = True


class PublishToChannelRequest(BaseModel):
    channelIds: List[int]


# ---------- Helper Functions ----------

def _to_dict(obj: RecruitmentPosition) -> dict:
    """转换模型为字典"""
    return {
        "id": obj.id,
        "title": obj.title,
        "department": obj.department,
        "salaryRange": obj.salary_range,
        "status": obj.status,
        "candidates": obj.candidates,
        "responsibilities": obj.responsibilities,
        "location": obj.location,
        "headcount": obj.headcount,
        "createdAt": obj.created_at.isoformat(),
        "approvalId": obj.approval_id,
        "publishedChannels": obj.published_channels,
    }


def _get_or_404(db: Session, position_id: int) -> RecruitmentPosition:
    """获取岗位或返回404"""
    obj = db.query(RecruitmentPosition).filter_by(id=position_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="岗位不存在")
    return obj


# ---------- API Routes ----------

@router.get("/list")
def get_list(
    status: Optional[str] = None,
    department: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """列表查询（支持分页、筛选、排序）"""
    query = db.query(RecruitmentPosition)

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
                RecruitmentPosition.title.like(f"%{keyword}%"),
                RecruitmentPosition.responsibilities.like(f"%{keyword}%")
            )
        )

    # 分页
    total = query.count()
    items = query.order_by(RecruitmentPosition.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

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


@router.get("/{position_id}")
def get_detail(position_id: int, db: Session = Depends(get_db)):
    """详情查询"""
    obj = _get_or_404(db, position_id)
    return {"code": 200, "message": "success", "data": _to_dict(obj)}


@router.post("")
def create(
    data: PositionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建岗位"""
    obj = RecruitmentPosition(
        title=data.title,
        department=data.department,
        salary_range=data.salaryRange,
        responsibilities=data.responsibilities,
        location=data.location,
        headcount=data.headcount,
        approval_id=data.approvalId,
        status="draft",
        candidates=0
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"code": 200, "message": "创建成功", "data": _to_dict(obj)}


@router.put("/{position_id}")
def update(
    position_id: int,
    data: PositionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新岗位"""
    obj = _get_or_404(db, position_id)

    # 更新字段
    if data.title is not None:
        obj.title = data.title
    if data.department is not None:
        obj.department = data.department
    if data.location is not None:
        obj.location = data.location
    if data.salaryRange is not None:
        obj.salary_range = data.salaryRange
    if data.responsibilities is not None:
        obj.responsibilities = data.responsibilities
    if data.headcount is not None:
        obj.headcount = data.headcount
    if data.status is not None:
        obj.status = data.status
    if data.candidates is not None:
        obj.candidates = data.candidates
    if data.approvalId is not None:
        obj.approval_id = data.approvalId
    if data.publishedChannels is not None:
        obj.published_channels = data.publishedChannels

    db.commit()
    db.refresh(obj)
    return {"code": 200, "message": "更新成功", "data": _to_dict(obj)}


@router.delete("/{position_id}")
def delete(position_id: int, db: Session = Depends(get_db)):
    """删除岗位"""
    obj = _get_or_404(db, position_id)
    db.delete(obj)
    db.commit()
    return {"code": 200, "message": "删除成功"}


@router.post("/{position_id}/publish")
def publish_to_channels(
    position_id: int,
    data: PublishToChannelRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """发布到渠道"""
    obj = _get_or_404(db, position_id)

    # 更新状态为已发布
    obj.status = "published"
    obj.published_channels = {"channelIds": data.channelIds}
    db.commit()

    # TODO: 实际发布到渠道的逻辑

    return {"code": 200, "message": f"已发布到 {len(data.channelIds)} 个渠道", "data": _to_dict(obj)}
