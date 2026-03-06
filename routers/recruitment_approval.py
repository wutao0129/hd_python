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
    applicantId: int
    applicantName: str
    departmentId: int
    departmentName: str
    positionName: str
    positionCode: str
    recruitCount: int = 1
    positionType: str
    workLocation: str
    positionLevel: str
    expectedOnboardDate: str
    recruitReason: str
    positionDescription: Optional[str] = None
    requirements: Optional[str] = None
    remarks: Optional[str] = None

    class Config:
        # 允许使用别名
        populate_by_name = True


class RecruitmentApprovalUpdate(BaseModel):
    departmentId: Optional[int] = None
    departmentName: Optional[str] = None
    positionName: Optional[str] = None
    positionCode: Optional[str] = None
    recruitCount: Optional[int] = None
    positionType: Optional[str] = None
    workLocation: Optional[str] = None
    positionLevel: Optional[str] = None
    expectedOnboardDate: Optional[str] = None
    recruitReason: Optional[str] = None
    positionDescription: Optional[str] = None
    requirements: Optional[str] = None
    remarks: Optional[str] = None

    class Config:
        # 允许使用别名
        populate_by_name = True


class ApprovalAction(BaseModel):
    comment: Optional[str] = None


# ---------- Helper Functions ----------

def _to_dict(obj: RecruitmentApproval) -> dict:
    """转换模型为字典"""
    return {
        "id": obj.id,
        "applicantId": obj.applicant_id,
        "applicantName": obj.applicant_name,
        "departmentId": obj.department_id,
        "departmentName": obj.department_name,
        "positionName": obj.position_name,
        "positionCode": obj.position_code,
        "recruitCount": obj.recruit_count,
        "positionType": obj.position_type,
        "workLocation": obj.work_location,
        "positionLevel": obj.position_level,
        "expectedOnboardDate": obj.expected_onboard_date,
        "recruitReason": obj.recruit_reason,
        "status": obj.status,
        "rejectReason": obj.reject_reason,
        "approverId": obj.approver_id,
        "approverName": obj.approver_name,
        "approvedAt": obj.approved_at.isoformat() if obj.approved_at else None,
        "createdAt": obj.created_at.isoformat(),
        "updatedAt": obj.updated_at.isoformat(),
        "submittedAt": obj.submitted_at.isoformat() if obj.submitted_at else None,
        "withdrawnAt": obj.withdrawn_at.isoformat() if obj.withdrawn_at else None,
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
        query = query.filter_by(applicant_id=current_user["id"])

    # 状态筛选
    if status:
        query = query.filter_by(status=status)

    # 关键词搜索
    if keyword:
        query = query.filter(
            or_(
                RecruitmentApproval.position_name.like(f"%{keyword}%"),
                RecruitmentApproval.applicant_name.like(f"%{keyword}%")
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


@router.post("")
def create_approval(
    data: RecruitmentApprovalCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建草稿"""
    obj = RecruitmentApproval(
        applicant_id=data.applicantId,
        applicant_name=data.applicantName,
        department_id=data.departmentId,
        department_name=data.departmentName,
        position_name=data.positionName,
        position_code=data.positionCode,
        recruit_count=data.recruitCount,
        position_type=data.positionType,
        work_location=data.workLocation,
        position_level=data.positionLevel,
        expected_onboard_date=data.expectedOnboardDate,
        recruit_reason=data.recruitReason,
        status="draft",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"code": 200, "message": "创建成功", "data": _to_dict(obj)}


@router.get("/{approval_id}")
def get_approval(approval_id: int, db: Session = Depends(get_db)):
    """详情查询"""
    obj = _get_or_404(db, approval_id)
    return {"code": 200, "message": "success", "data": _to_dict(obj)}


@router.put("/{approval_id}")
def update_approval(
    approval_id: int,
    data: RecruitmentApprovalUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新草稿"""
    obj = _get_or_404(db, approval_id)

    if obj.status != "draft":
        raise HTTPException(status_code=400, detail="只能更新草稿状态的审批单")

    # 更新字段
    if data.departmentId is not None:
        obj.department_id = data.departmentId
    if data.departmentName is not None:
        obj.department_name = data.departmentName
    if data.positionName is not None:
        obj.position_name = data.positionName
    if data.positionCode is not None:
        obj.position_code = data.positionCode
    if data.recruitCount is not None:
        obj.recruit_count = data.recruitCount
    if data.positionType is not None:
        obj.position_type = data.positionType
    if data.workLocation is not None:
        obj.work_location = data.workLocation
    if data.positionLevel is not None:
        obj.position_level = data.positionLevel
    if data.expectedOnboardDate is not None:
        obj.expected_onboard_date = data.expectedOnboardDate
    if data.recruitReason is not None:
        obj.recruit_reason = data.recruitReason

    obj.updated_at = datetime.now()
    db.commit()
    db.refresh(obj)
    return {"code": 200, "message": "更新成功", "data": _to_dict(obj)}


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

    obj.status = "withdrawn"
    obj.withdrawn_at = datetime.now()
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
    obj.approver_name = current_user.get("name", "")
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
    obj.approver_name = current_user.get("name", "")
    obj.reject_reason = action.comment
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
