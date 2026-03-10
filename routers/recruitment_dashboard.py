from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import get_db
from models import (
    RecruitmentPosition,
    RecruitmentResume,
    RecruitmentInterview,
    RecruitmentOffer
)
from middleware import get_current_user

router = APIRouter(prefix="/api/recruitment-dashboard", tags=["招聘管理-仪表板"])


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取统计数据"""

    # 岗位统计
    total_positions = db.query(func.count(RecruitmentPosition.id)).scalar()
    active_positions = db.query(func.count(RecruitmentPosition.id)).filter(
        RecruitmentPosition.status == "published"
    ).scalar()

    # 简历统计
    total_resumes = db.query(func.count(RecruitmentResume.id)).scalar()
    pending_resumes = db.query(func.count(RecruitmentResume.id)).filter(
        RecruitmentResume.status == "pending"
    ).scalar()

    # 面试统计
    total_interviews = db.query(func.count(RecruitmentInterview.id)).scalar()
    scheduled_interviews = db.query(func.count(RecruitmentInterview.id)).filter(
        RecruitmentInterview.status == "scheduled"
    ).scalar()

    # Offer统计
    total_offers = db.query(func.count(RecruitmentOffer.id)).scalar()
    sent_offers = db.query(func.count(RecruitmentOffer.id)).filter(
        RecruitmentOffer.status == "sent"
    ).scalar()

    # 按来源统计简历
    resume_by_source = db.query(
        RecruitmentResume.source,
        func.count(RecruitmentResume.id).label("count")
    ).group_by(RecruitmentResume.source).all()

    # 按状态统计简历
    resume_by_status = db.query(
        RecruitmentResume.status,
        func.count(RecruitmentResume.id).label("count")
    ).group_by(RecruitmentResume.status).all()

    # 按部门统计岗位
    position_by_department = db.query(
        RecruitmentPosition.department,
        func.count(RecruitmentPosition.id).label("count")
    ).group_by(RecruitmentPosition.department).all()

    return {
        "code": 200,
        "message": "success",
        "data": {
            "overview": {
                "totalPositions": total_positions,
                "activePositions": active_positions,
                "totalResumes": total_resumes,
                "pendingResumes": pending_resumes,
                "totalInterviews": total_interviews,
                "scheduledInterviews": scheduled_interviews,
                "totalOffers": total_offers,
                "sentOffers": sent_offers,
            },
            "resumeBySource": [
                {"source": item[0], "count": item[1]}
                for item in resume_by_source
            ],
            "resumeByStatus": [
                {"status": item[0], "count": item[1]}
                for item in resume_by_status
            ],
            "positionByDepartment": [
                {"department": item[0], "count": item[1]}
                for item in position_by_department
            ],
        }
    }
