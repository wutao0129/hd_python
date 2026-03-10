from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import RecruitmentOffer
from middleware import get_current_user

router = APIRouter(prefix="/api/recruitment-offer", tags=["招聘管理-Offer"])


# ---------- Schemas ----------

class OfferCreate(BaseModel):
    resumeId: int
    positionId: int
    candidateName: str
    positionTitle: str
    salary: str
    startDate: str
    notes: Optional[str] = None

    class Config:
        populate_by_name = True


class OfferApprove(BaseModel):
    action: str  # approve / reject
    reason: Optional[str] = None

    class Config:
        populate_by_name = True


# ---------- Helper Functions ----------

def _to_dict(obj: RecruitmentOffer) -> dict:
    """转换模型为字典"""
    return {
        "id": obj.id,
        "resumeId": obj.resume_id,
        "positionId": obj.position_id,
        "candidateName": obj.candidate_name,
        "positionTitle": obj.position_title,
        "salary": obj.salary,
        "startDate": obj.start_date,
        "status": obj.status,
        "offerDate": obj.offer_date.isoformat() if obj.offer_date else None,
        "acceptDate": obj.accept_date.isoformat() if obj.accept_date else None,
        "rejectReason": obj.reject_reason,
        "notes": obj.notes,
        "createdAt": obj.created_at.isoformat(),
        "updatedAt": obj.updated_at.isoformat(),
    }


def _get_or_404(db: Session, offer_id: int) -> RecruitmentOffer:
    """获取Offer或返回404"""
    obj = db.query(RecruitmentOffer).filter_by(id=offer_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Offer不存在")
    return obj


# ---------- API Routes ----------

@router.get("/list")
def get_list(
    status: Optional[str] = None,
    positionId: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """列表查询（支持分页、筛选、排序）"""
    query = db.query(RecruitmentOffer)

    # 状态筛选
    if status:
        query = query.filter_by(status=status)

    # 岗位筛选
    if positionId:
        query = query.filter_by(position_id=positionId)

    # 分页
    total = query.count()
    items = query.order_by(RecruitmentOffer.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

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


@router.get("/{offer_id}")
def get_detail(offer_id: int, db: Session = Depends(get_db)):
    """详情查询"""
    obj = _get_or_404(db, offer_id)
    return {"code": 200, "message": "success", "data": _to_dict(obj)}


@router.post("")
def create(
    data: OfferCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建Offer"""
    obj = RecruitmentOffer(
        resume_id=data.resumeId,
        position_id=data.positionId,
        candidate_name=data.candidateName,
        position_title=data.positionTitle,
        salary=data.salary,
        start_date=data.startDate,
        notes=data.notes,
        status="draft",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"code": 200, "message": "创建成功", "data": _to_dict(obj)}


@router.post("/{offer_id}/approve")
def approve(
    offer_id: int,
    data: OfferApprove,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """审批Offer"""
    obj = _get_or_404(db, offer_id)

    if data.action == "approve":
        obj.status = "approved"
        obj.updated_at = datetime.now()
    elif data.action == "reject":
        obj.status = "rejected"
        obj.reject_reason = data.reason
        obj.updated_at = datetime.now()
    else:
        raise HTTPException(status_code=400, detail="无效的操作")

    db.commit()
    db.refresh(obj)
    return {"code": 200, "message": "审批成功", "data": _to_dict(obj)}


@router.post("/{offer_id}/send")
def send_offer(
    offer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """发放Offer"""
    obj = _get_or_404(db, offer_id)

    if obj.status != "approved":
        raise HTTPException(status_code=400, detail="只能发放已审批的Offer")

    obj.status = "sent"
    obj.offer_date = datetime.now()
    obj.updated_at = datetime.now()
    db.commit()
    db.refresh(obj)

    return {"code": 200, "message": "Offer已发放", "data": _to_dict(obj)}
