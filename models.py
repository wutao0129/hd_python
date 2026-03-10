from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, DateTime, Integer, JSON, String, Text, func, ForeignKey, Boolean, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Questionnaire(Base):
    __tablename__ = "questionnaire"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[int] = mapped_column(Integer, default=0)  # 0=草稿 1=进行中 2=已截止
    uuid: Mapped[Optional[str]] = mapped_column(String(36), unique=True)
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # V2增强：Banner图配置
    banner_url: Mapped[Optional[str]] = mapped_column(String(500))
    brand_text: Mapped[Optional[str]] = mapped_column(String(100))

    # V2增强：隐私声明配置
    privacy_enabled: Mapped[int] = mapped_column(Integer, default=0)  # 0=禁用 1=启用
    privacy_title: Mapped[Optional[str]] = mapped_column(String(100))
    privacy_items: Mapped[Optional[dict]] = mapped_column(JSON)  # 存储隐私条款列表

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class QuestionnaireQuestion(Base):
    __tablename__ = "questionnaire_question"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    questionnaire_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    required: Mapped[int] = mapped_column(Integer, default=1)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    options: Mapped[Optional[dict]] = mapped_column(JSON)
    rating_max: Mapped[Optional[int]] = mapped_column(Integer)
    rating_labels: Mapped[Optional[dict]] = mapped_column(JSON)
    max_length: Mapped[Optional[int]] = mapped_column(Integer)


class QuestionnaireAnswer(Base):
    __tablename__ = "questionnaire_answer"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    questionnaire_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    submit_token: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    # 用户基础信息
    user_name: Mapped[Optional[str]] = mapped_column(String(100))
    user_company: Mapped[Optional[str]] = mapped_column(String(200))
    user_position: Mapped[Optional[str]] = mapped_column(String(100))
    user_phone: Mapped[Optional[str]] = mapped_column(String(20))
    user_email: Mapped[Optional[str]] = mapped_column(String(100))

    submitted_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class QuestionnaireAnswerDetail(Base):
    __tablename__ = "questionnaire_answer_detail"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    answer_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    question_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    value: Mapped[Optional[str]] = mapped_column(Text)


# 菜单系统模型
class Menu(Base):
    """菜单主表"""
    __tablename__ = "menus"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("menus.id", ondelete="CASCADE"))
    menu_type: Mapped[str] = mapped_column(String(20), nullable=False, default="menu")
    menu_name: Mapped[str] = mapped_column(String(100), nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(String(100))
    route_path: Mapped[Optional[str]] = mapped_column(String(200))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_parent_id", "parent_id"),
        Index("idx_sort_order", "sort_order"),
    )


class MenuI18n(Base):
    """菜单多语言表"""
    __tablename__ = "menu_i18n"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    menu_id: Mapped[int] = mapped_column(Integer, ForeignKey("menus.id", ondelete="CASCADE"), nullable=False)
    language_code: Mapped[str] = mapped_column(String(10), nullable=False)
    menu_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("uk_menu_lang", "menu_id", "language_code", unique=True),
    )


class SysRole(Base):
    """角色表"""
    __tablename__ = "sys_role"

    ROLE_ID: Mapped[int] = mapped_column("ROLE_ID", Integer, primary_key=True, autoincrement=True)
    ROLE_CODE: Mapped[Optional[str]] = mapped_column("ROLE_CODE", String(50))
    ROLE_NAME: Mapped[Optional[str]] = mapped_column("ROLE_NAME", String(100))
    ROLE_DESC: Mapped[Optional[str]] = mapped_column("ROLE_DESC", String(512))
    ROLE_TYPE: Mapped[Optional[str]] = mapped_column("ROLE_TYPE", String(30))
    ROLE_STATUS: Mapped[Optional[str]] = mapped_column("ROLE_STATUS", String(20))
    DELETE_MARK: Mapped[Optional[str]] = mapped_column("DELETE_MARK", String(3))


class MenuPermission(Base):
    """菜单权限表"""
    __tablename__ = "menu_permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(Integer, nullable=False)
    menu_id: Mapped[int] = mapped_column(Integer, ForeignKey("menus.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("uk_role_menu", "role_id", "menu_id", unique=True),
        Index("idx_role_id", "role_id"),
    )


class RecruitmentApproval(Base):
    """招聘审批单表"""
    __tablename__ = "recruitment_approvals"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # 申请人信息
    applicant_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    applicant_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # 部门信息
    department_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    department_name: Mapped[str] = mapped_column(String(200), nullable=False)

    # 职位信息
    position_name: Mapped[str] = mapped_column(String(200), nullable=False)
    position_code: Mapped[Optional[str]] = mapped_column(String(50))
    recruit_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    position_type: Mapped[str] = mapped_column(String(50), nullable=False)
    work_location: Mapped[str] = mapped_column(String(200), nullable=False)
    position_level: Mapped[Optional[str]] = mapped_column(String(50))
    expected_onboard_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    recruit_reason: Mapped[str] = mapped_column(String(50), nullable=False)

    # 审批状态
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    reject_reason: Mapped[Optional[str]] = mapped_column(Text)

    # 审批人信息
    approver_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    approver_name: Mapped[Optional[str]] = mapped_column(String(100))

    # 时间戳
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    withdrawn_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    __table_args__ = (
        Index("idx_status", "status"),
        Index("idx_applicant_id", "applicant_id"),
        Index("idx_department_id", "department_id"),
    )


class RecruitmentPosition(Base):
    """招聘岗位表"""
    __tablename__ = "recruitment_positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[str] = mapped_column(String(50), nullable=False)
    salary_range: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    candidates: Mapped[int] = mapped_column(Integer, nullable=False)
    responsibilities: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    headcount: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    approval_id: Mapped[Optional[str]] = mapped_column(String(50))
    published_channels: Mapped[Optional[dict]] = mapped_column(JSON)

    __table_args__ = (
        Index("idx_status", "status"),
        Index("idx_department", "department"),
    )


class RecruitmentResume(Base):
    """招聘简历表"""
    __tablename__ = "recruitment_resumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    school: Mapped[str] = mapped_column(String(100), nullable=False)
    degree: Mapped[str] = mapped_column(String(20), nullable=False)
    experience: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    applied_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    current_company: Mapped[str] = mapped_column(String(100), nullable=False)
    skills: Mapped[dict] = mapped_column(JSON, nullable=False)
    scores: Mapped[dict] = mapped_column(JSON, nullable=False)
    applied_position: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[str] = mapped_column(String(50), nullable=False)

    __table_args__ = (
        Index("idx_status", "status"),
        Index("idx_applied_position", "applied_position"),
    )


class RecruitmentChannel(Base):
    """招聘渠道表"""
    __tablename__ = "recruitment_channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_status", "status"),
        Index("idx_type", "type"),
    )


class RecruitmentInterview(Base):
    """面试记录表"""
    __tablename__ = "recruitment_interviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    resume_id: Mapped[int] = mapped_column(Integer, nullable=False)
    candidate_name: Mapped[str] = mapped_column(String(50), nullable=False)
    position_id: Mapped[int] = mapped_column(Integer, nullable=False)
    position_name: Mapped[str] = mapped_column(String(100), nullable=False)
    interviewer: Mapped[str] = mapped_column(String(50), nullable=False)
    interview_date: Mapped[str] = mapped_column(String(20), nullable=False)
    interview_method: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    feedback: Mapped[Optional[str]] = mapped_column(Text)
    score: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_resume_id", "resume_id"),
        Index("idx_position_id", "position_id"),
        Index("idx_status", "status"),
    )


class RecruitmentOffer(Base):
    """Offer表"""
    __tablename__ = "recruitment_offers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    resume_id: Mapped[int] = mapped_column(Integer, nullable=False)
    candidate_name: Mapped[str] = mapped_column(String(50), nullable=False)
    position_id: Mapped[int] = mapped_column(Integer, nullable=False)
    position_name: Mapped[str] = mapped_column(String(100), nullable=False)
    offer_salary: Mapped[str] = mapped_column(String(50), nullable=False)
    offer_date: Mapped[str] = mapped_column(String(20), nullable=False)
    expected_onboard_date: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_resume_id", "resume_id"),
        Index("idx_position_id", "position_id"),
        Index("idx_status", "status"),
    )


class RecruitmentQuestionBank(Base):
    """题库表"""
    __tablename__ = "recruitment_question_bank"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    tags: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_type", "type"),
        Index("idx_difficulty", "difficulty"),
    )
