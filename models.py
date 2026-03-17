from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import BigInteger, DateTime, Integer, JSON, String, Text, func, ForeignKey, Boolean, Enum as SQLEnum, Index, CHAR, DECIMAL, Date, UniqueConstraint
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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 申请人信息
    applicant_id: Mapped[int] = mapped_column(Integer, nullable=False)
    applicant_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # 部门信息
    department_id: Mapped[int] = mapped_column(Integer, nullable=False)
    department_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # 职位信息
    position_name: Mapped[str] = mapped_column(String(200), nullable=False)
    position_code: Mapped[str] = mapped_column(String(50), nullable=False)
    recruit_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    position_type: Mapped[str] = mapped_column(String(50), nullable=False)
    work_location: Mapped[str] = mapped_column(String(200), nullable=False)
    position_level: Mapped[str] = mapped_column(String(50), nullable=False)
    expected_onboard_date: Mapped[str] = mapped_column(String(20), nullable=False)
    recruit_reason: Mapped[str] = mapped_column(Text, nullable=False)

    # 审批状态
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    reject_reason: Mapped[Optional[str]] = mapped_column(Text)

    # 审批人信息
    approver_id: Mapped[Optional[int]] = mapped_column(Integer)
    approver_name: Mapped[Optional[str]] = mapped_column(String(100))

    # 时间戳
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    withdrawn_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    __table_args__ = (
        Index("idx_status", "status"),
        Index("idx_applicant_id", "applicant_id"),
        Index("idx_department_id", "department_id"),
    )


# ==================== 员工表（只读，用于 JOIN） ====================

class SysEmp(Base):
    """员工信息表（只读）"""
    __tablename__ = "sys_emp"

    emp_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    emp_code: Mapped[Optional[str]] = mapped_column(String(50))
    emp_name: Mapped[str] = mapped_column(String(50), nullable=False)
    emp_status: Mapped[Optional[str]] = mapped_column(CHAR(1), default='0')
    dept_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    dept_name: Mapped[Optional[str]] = mapped_column(String(100))
    post_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    post_name: Mapped[Optional[str]] = mapped_column(String(100))
    job_level: Mapped[Optional[str]] = mapped_column(String(10))
    del_flag: Mapped[Optional[str]] = mapped_column(CHAR(1), default='0')
    tenant_id: Mapped[Optional[str]] = mapped_column(String(30))


# ==================== 标签库主表 ====================

class SysTag(Base):
    """标签库表 (sys_tag)"""
    __tablename__ = "sys_tag"

    tag_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    tag_name: Mapped[str] = mapped_column(String(100), nullable=False)
    tag_code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    tag_category: Mapped[str] = mapped_column(String(50), nullable=False)
    tag_type: Mapped[Optional[str]] = mapped_column(String(10), default='1')  # 0内置 1自定义
    scene: Mapped[Optional[dict]] = mapped_column(JSON)
    rule_type: Mapped[Optional[list]] = mapped_column(JSON)
    rule_detail: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[str]] = mapped_column(CHAR(1), default='0')  # 0草稿 1启用 2停用
    del_flag: Mapped[Optional[str]] = mapped_column(CHAR(1), default='0')  # 0存在 2删除
    remark: Mapped[Optional[str]] = mapped_column(String(500))
    parent_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    activity_rate: Mapped[int] = mapped_column(Integer, default=0)
    graph_type: Mapped[Optional[str]] = mapped_column(String(10))
    relation_name: Mapped[Optional[str]] = mapped_column(String(100))
    similar_tags: Mapped[Optional[str]] = mapped_column(Text)
    exclusive_tags: Mapped[Optional[str]] = mapped_column(Text)
    create_dept: Mapped[Optional[int]] = mapped_column(BigInteger)
    create_by: Mapped[Optional[int]] = mapped_column(BigInteger)
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime)
    update_by: Mapped[Optional[int]] = mapped_column(BigInteger)
    update_time: Mapped[Optional[datetime]] = mapped_column(DateTime)
    tenant_id: Mapped[Optional[str]] = mapped_column(String(30))

    __table_args__ = (
        Index("idx_sys_tag_tag_category", "tag_category"),
        Index("idx_sys_tag_tag_type", "tag_type"),
        Index("idx_sys_tag_status", "status"),
        Index("idx_sys_tag_parent_id", "parent_id"),
        Index("idx_sys_tag_tenant_id", "tenant_id"),
    )


# 别名，减少路由改动
Tag = SysTag


# ==================== 标签触发规则表 ====================

class SysTagTriggerRule(Base):
    """标签触发规则表"""
    __tablename__ = "sys_tag_trigger_rule"

    rule_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    model_id: Mapped[str] = mapped_column(String(36), nullable=False)
    tag_name: Mapped[str] = mapped_column(String(50), nullable=False)
    tag_color: Mapped[str] = mapped_column(String(20), nullable=False, default='#1976D2')
    tag_category: Mapped[str] = mapped_column(String(30), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(30), nullable=False)
    logic: Mapped[str] = mapped_column(String(5), nullable=False, default='AND')
    expire_days: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[Optional[str]] = mapped_column(CHAR(1), default='0')
    del_flag: Mapped[Optional[str]] = mapped_column(CHAR(1), default='0')
    remark: Mapped[Optional[str]] = mapped_column(String(500))
    tenant_id: Mapped[Optional[str]] = mapped_column(String(20))
    create_dept: Mapped[Optional[int]] = mapped_column(BigInteger)
    create_by: Mapped[Optional[int]] = mapped_column(BigInteger)
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime)
    update_by: Mapped[Optional[int]] = mapped_column(BigInteger)
    update_time: Mapped[Optional[datetime]] = mapped_column(DateTime)

    __table_args__ = (
        Index("idx_sys_tag_trigger_rule_model_id", "model_id"),
        Index("idx_sys_tag_trigger_rule_tenant_id", "tenant_id"),
    )


class SysTagTriggerCondition(Base):
    """标签触发条件表"""
    __tablename__ = "sys_tag_trigger_condition"

    condition_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    rule_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    target_id: Mapped[Optional[str]] = mapped_column(String(36))
    target_name: Mapped[Optional[str]] = mapped_column(String(100))
    operator: Mapped[str] = mapped_column(String(5), nullable=False, default='>=')
    value: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[Optional[str]] = mapped_column(CHAR(1), default='0')
    del_flag: Mapped[Optional[str]] = mapped_column(CHAR(1), default='0')
    remark: Mapped[Optional[str]] = mapped_column(String(500))
    tenant_id: Mapped[Optional[str]] = mapped_column(String(20))
    create_dept: Mapped[Optional[int]] = mapped_column(BigInteger)
    create_by: Mapped[Optional[int]] = mapped_column(BigInteger)
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime)
    update_by: Mapped[Optional[int]] = mapped_column(BigInteger)
    update_time: Mapped[Optional[datetime]] = mapped_column(DateTime)

    __table_args__ = (
        Index("idx_sys_tag_trigger_condition_rule_id", "rule_id"),
        Index("idx_sys_tag_trigger_condition_tenant_id", "tenant_id"),
    )


class SysTagTriggerAction(Base):
    """标签触发动作表"""
    __tablename__ = "sys_tag_trigger_action"

    action_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    rule_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    config: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[str]] = mapped_column(CHAR(1), default='0')
    del_flag: Mapped[Optional[str]] = mapped_column(CHAR(1), default='0')
    remark: Mapped[Optional[str]] = mapped_column(String(500))
    tenant_id: Mapped[Optional[str]] = mapped_column(String(20))
    create_dept: Mapped[Optional[int]] = mapped_column(BigInteger)
    create_by: Mapped[Optional[int]] = mapped_column(BigInteger)
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime)
    update_by: Mapped[Optional[int]] = mapped_column(BigInteger)
    update_time: Mapped[Optional[datetime]] = mapped_column(DateTime)

    __table_args__ = (
        Index("idx_sys_tag_trigger_action_rule_id", "rule_id"),
        Index("idx_sys_tag_trigger_action_tenant_id", "tenant_id"),
    )


# ==================== 人才标签业务表 ====================

class TalentTag(Base):
    """人才关联标签表"""
    __tablename__ = "talent_tag"

    talent_tag_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    emp_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tag_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tag_source: Mapped[str] = mapped_column(String(10), nullable=False, default='manual')
    score: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(5, 2))
    expire_time: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[Optional[str]] = mapped_column(CHAR(1), default='1')  # 0草稿 1启用 2停用
    del_flag: Mapped[Optional[str]] = mapped_column(CHAR(1), default='0')
    remark: Mapped[Optional[str]] = mapped_column(String(500))
    tenant_id: Mapped[Optional[str]] = mapped_column(String(20))
    create_dept: Mapped[Optional[int]] = mapped_column(BigInteger)
    create_by: Mapped[Optional[int]] = mapped_column(BigInteger)
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime)
    update_by: Mapped[Optional[int]] = mapped_column(BigInteger)
    update_time: Mapped[Optional[datetime]] = mapped_column(DateTime)

    __table_args__ = (
        UniqueConstraint("emp_id", "tag_id", name="uk_talent_tag_emp_tag"),
        Index("idx_talent_tag_emp_id", "emp_id"),
        Index("idx_talent_tag_tag_id", "tag_id"),
        Index("idx_talent_tag_tag_source", "tag_source"),
        Index("idx_talent_tag_tenant_id", "tenant_id"),
    )


# 别名
TagRecord = TalentTag


class TalentTagLog(Base):
    """人才标签操作记录表"""
    __tablename__ = "talent_tag_log"

    log_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    emp_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tag_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    action: Mapped[str] = mapped_column(String(10), nullable=False)  # add/remove
    action_source: Mapped[str] = mapped_column(String(10), nullable=False)  # auto/manual
    action_reason: Mapped[Optional[str]] = mapped_column(String(500))
    rule_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    status: Mapped[Optional[str]] = mapped_column(CHAR(1), default='1')
    del_flag: Mapped[Optional[str]] = mapped_column(CHAR(1), default='0')
    remark: Mapped[Optional[str]] = mapped_column(String(500))
    tenant_id: Mapped[Optional[str]] = mapped_column(String(20))
    create_dept: Mapped[Optional[int]] = mapped_column(BigInteger)
    create_by: Mapped[Optional[int]] = mapped_column(BigInteger)
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime)
    update_by: Mapped[Optional[int]] = mapped_column(BigInteger)
    update_time: Mapped[Optional[datetime]] = mapped_column(DateTime)

    __table_args__ = (
        Index("idx_talent_tag_log_emp_id", "emp_id"),
        Index("idx_talent_tag_log_tag_id", "tag_id"),
        Index("idx_talent_tag_log_action", "action"),
        Index("idx_talent_tag_log_rule_id", "rule_id"),
        Index("idx_talent_tag_log_tenant_id", "tenant_id"),
    )
