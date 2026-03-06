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
        Index("idx_parent_sort", "parent_id", "sort_order"),  # 复合索引优化查询
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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    position: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    creator_id: Mapped[Optional[int]] = mapped_column(Integer)
    creator_name: Mapped[Optional[str]] = mapped_column(String(100))
    approver_id: Mapped[Optional[int]] = mapped_column(Integer)
    approver_name: Mapped[Optional[str]] = mapped_column(String(100))
    approval_comment: Mapped[Optional[str]] = mapped_column(Text)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_status", "status"),
        Index("idx_creator_id", "creator_id"),
    )
