"""
招聘管理模块数据库表创建脚本
执行此脚本将创建所有招聘管理相关的数据库表
"""

from database import engine, Base
from models import (
    RecruitmentApproval,
    RecruitmentPosition,
    RecruitmentResume,
    RecruitmentChannel,
    RecruitmentInterview,
    RecruitmentOffer,
    RecruitmentQuestionBank,
    RecruitmentJobProfile
)

def create_recruitment_tables():
    """创建招聘管理模块的所有表"""
    print("开始创建招聘管理模块数据库表...")

    # 创建所有表
    Base.metadata.create_all(bind=engine)

    print("✅ 数据库表创建完成！")
    print("\n已创建的表：")
    print("  - recruitment_approvals (招聘审批单)")
    print("  - recruitment_positions (招聘岗位)")
    print("  - recruitment_resumes (简历)")
    print("  - recruitment_channels (招聘渠道)")
    print("  - recruitment_interviews (面试记录)")
    print("  - recruitment_offers (Offer)")
    print("  - recruitment_question_bank (题库)")
    print("  - recruitment_job_profiles (岗位画像)")

if __name__ == "__main__":
    create_recruitment_tables()
