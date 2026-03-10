from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session
from database import get_db
from models import RecruitmentChannel
from middleware import get_current_user

router = APIRouter(prefix="/api/recruitment-channel", tags=["招聘管理-渠道"])


# ---------- Schemas ----------

class ChannelCreate(BaseModel):
    name: str
    type: str
    contactPerson: Optional[str] = None
    contactPhone: Optional[str] = None
    contactEmail: Optional[str] = None
    cost: Optional[str] = None
    description: Optional[str] = None

    class Config:
        populate_by_name = True


class ChannelUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    contactPerson: Optional[str] = None
    contactPhone: Optional[str] = None
    contactEmail: Optional[str] = None
    cost: Optional[str] = None
    description: Optional[str] = None

    class Config:
        populate_by_name = True


# ---------- Helper Functions ----------

def _to_dict(obj: RecruitmentChannel) -> dict:
    """转换模型为字典"""
    return {
        "id": obj.id,
        "name": obj.name,
        "type": obj.type,
        "status": obj.status,
        "contactPerson": obj.contact_person,
        "contactPhone": obj.contact_phone,
        "contactEmail": obj.contact_email,
        "cost": obj.cost,
        "description": obj.description,
        "createdAt": obj.created_at.isoformat(),
        "updatedAt": obj.updated_at.isoformat(),
    }


def _get_or_404(db: Session, channel_id: int) -> RecruitmentChannel:
    """获取渠道或返回404"""
    obj = db.query(RecruitmentChannel).filter_by(id=channel_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="渠道不存在")
    return obj


# ---------- API Routes ----------

@router.get("/list")
def get_list(
    status: Optional[str] = None,
    type: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """列表查询（支持分页、筛选、排序）"""
    query = db.query(RecruitmentChannel)

    # 状态筛选
    if status:
        query = query.filter_by(status=status)

    # 类型筛选
    if type:
        query = query.filter_by(type=type)

    # 关键词搜索
    if keyword:
        query = query.filter(
            or_(
                RecruitmentChannel.name.like(f"%{keyword}%"),
                RecruitmentChannel.description.like(f"%{keyword}%")
            )
        )

    # 分页
    total = query.count()
    items = query.order_by(RecruitmentChannel.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

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


@router.get("/{channel_id}")
def get_detail(channel_id: int, db: Session = Depends(get_db)):
    """详情查询"""
    obj = _get_or_404(db, channel_id)
    return {"code": 200, "message": "success", "data": _to_dict(obj)}


@router.post("")
def create(
    data: ChannelCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建渠道"""
    obj = RecruitmentChannel(
        name=data.name,
        type=data.type,
        contact_person=data.contactPerson,
        contact_phone=data.contactPhone,
        contact_email=data.contactEmail,
        cost=data.cost,
        description=data.description,
        status="active",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"code": 200, "message": "创建成功", "data": _to_dict(obj)}


@router.put("/{channel_id}")
def update(
    channel_id: int,
    data: ChannelUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新渠道"""
    obj = _get_or_404(db, channel_id)

    # 更新字段
    if data.name is not None:
        obj.name = data.name
    if data.type is not None:
        obj.type = data.type
    if data.status is not None:
        obj.status = data.status
    if data.contactPerson is not None:
        obj.contact_person = data.contactPerson
    if data.contactPhone is not None:
        obj.contact_phone = data.contactPhone
    if data.contactEmail is not None:
        obj.contact_email = data.contactEmail
    if data.cost is not None:
        obj.cost = data.cost
    if data.description is not None:
        obj.description = data.description

    obj.updated_at = datetime.now()
    db.commit()
    db.refresh(obj)
    return {"code": 200, "message": "更新成功", "data": _to_dict(obj)}


@router.delete("/{channel_id}")
def delete(channel_id: int, db: Session = Depends(get_db)):
    """删除渠道"""
    obj = _get_or_404(db, channel_id)
    db.delete(obj)
    db.commit()
    return {"code": 200, "message": "删除成功"}
