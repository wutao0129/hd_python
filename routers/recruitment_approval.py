from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session
from database import get_db
from models import RecruitmentApproval
from middleware import get_current_user

router = APIRouter(prefix="/api/recruitment-approval", tags=["recruitment-approval"])


# ---------- Schemas ----------

class RecruitmentApprovalCreate(BaseModel):
    title: str
    position: str
    department: Optional[str] = None
    description: Optional[str] = None


class RecruitmentApprovalUpdate(BaseModel):
    title: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    description: Optional[str] = None


class ApprovalAction(BaseModel):
    comment: Optional[str] = None


# ---------- Helper Functions ----------

def _to_dict(obj: RecruitmentApproval) -> dict:
    """转换模型为字典"""
    return {
        "id": obj.id,
        "title": obj.title,
        "position": obj.position,
        "department": obj.department,
        "description": obj.description,
        "status": obj.status,
        "creator_id": obj.creator_id,
        "creator_name": obj.creator_name,
        "approver_id": obj.approver_id,
        "approver_name": obj.approver_name,
        "approval_comment": obj.approval_comment,
        "submitted_at": obj.submitted_at.isoformat() if obj.submitted_at else None,
        "approved_at": obj.approved_at.isoformat() if obj.approved_at else None,
        "created_at": obj.created_at.isoformat(),
        "updated_at": obj.updated_at.isoformat(),
    }


def _get_or_404(db: Session, approval_id: int) -> RecruitmentApproval:
    """获取审批单或返回404"""
    obj = db.query(RecruitmentApproval).filter_by(id=approval_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="审批单不存在")
    return obj


# ---------- API Routes ----------

@router.get("/list")
def list_approvals(
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """列表查询（支持分页、筛选、排序）"""
    query = db.query(RecruitmentApproval)

    # 权限过滤：员工只看自己的
    if current_user["role"] == "employee":
        query = query.filter_by(creator_id=current_user["id"])

    # 状态筛选
    if status:
        query = query.filter_by(status=status)

    # 关键词搜索
    if keyword:
        query = query.filter(
            or_(
                RecruitmentApproval.title.like(f"%{keyword}%"),
                RecruitmentApproval.position.like(f"%{keyword}%")
            )
        )

    # 分页
    total = query.count()
    items = query.order_by(RecruitmentApproval.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "code": 200,
        "message": "success",
        "data": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [_to_dict(item) for item in items]
        }
    }


@router.get("/{approval_id}")
def get_approval(approval_id: int, db: Session = Depends(get_db)):
    """详情查询"""
    obj = _get_or_404(db, approval_id)
    return {"code": 200, "message": "success", "data": _to_dict(obj)}


@router.post("/{approval_id}/submit")
def submit_approval(
    approval_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """提交审批"""
    obj = _get_or_404(db, approval_id)

    if obj.status != "draft":
        raise HTTPException(status_code=400, detail="只能提交草稿状态的审批单")

    obj.status = "pending"
    obj.submitted_at = datetime.now()
    db.commit()

    return {"code": 200, "message": "提交成功", "data": _to_dict(obj)}


@router.post("/{approval_id}/withdraw")
def withdraw_approval(
    approval_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """撤回审批"""
    obj = _get_or_404(db, approval_id)

    if obj.status != "pending":
        raise HTTPException(status_code=400, detail="只能撤回待审批状态的审批单")

    obj.status = "draft"
    obj.submitted_at = None
    db.commit()

    return {"code": 200, "message": "撤回成功", "data": _to_dict(obj)}


@router.post("/{approval_id}/approve")
def approve_approval(
    approval_id: int,
    action: ApprovalAction,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """审批通过"""
    obj = _get_or_404(db, approval_id)

    if obj.status != "pending":
        raise HTTPException(status_code=400, detail="只能审批待审批状态的审批单")

    obj.status = "approved"
    obj.approver_id = current_user["id"]
    obj.approval_comment = action.comment
    obj.approved_at = datetime.now()
    db.commit()

    return {"code": 200, "message": "审批通过", "data": _to_dict(obj)}


@router.post("/{approval_id}/reject")
def reject_approval(
    approval_id: int,
    action: ApprovalAction,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """审批驳回"""
    obj = _get_or_404(db, approval_id)

    if obj.status != "pending":
        raise HTTPException(status_code=400, detail="只能审批待审批状态的审批单")

    obj.status = "rejected"
    obj.approver_id = current_user["id"]
    obj.approval_comment = action.comment
    obj.approved_at = datetime.now()
    db.commit()

    return {"code": 200, "message": "审批驳回", "data": _to_dict(obj)}


@router.delete("/{approval_id}")
def delete_approval(approval_id: int, db: Session = Depends(get_db)):
    """删除单条"""
    obj = _get_or_404(db, approval_id)
    db.delete(obj)
    db.commit()
    return {"code": 200, "message": "删除成功"}


@router.post("/batch-delete")
def batch_delete_approvals(ids: List[int], db: Session = Depends(get_db)):
    """批量删除"""
    deleted = db.query(RecruitmentApproval).filter(RecruitmentApproval.id.in_(ids)).delete(synchronize_session=False)
    db.commit()
    return {"code": 200, "message": f"成功删除 {deleted} 条记录"}
