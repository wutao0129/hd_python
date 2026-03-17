from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==================== 人才标签 Schema (talent_tag) ====================

class TalentTagCreate(BaseModel):
    """创建人才标签关联"""
    emp_id: int
    tag_id: int
    tag_source: str = Field(default='manual', max_length=10)  # auto/manual
    score: Optional[float] = None
    expire_time: Optional[datetime] = None
    remark: Optional[str] = None


class TalentTagUpdate(BaseModel):
    """更新人才标签"""
    tag_source: Optional[str] = None
    score: Optional[float] = None
    expire_time: Optional[datetime] = None
    status: Optional[str] = None
    remark: Optional[str] = None


class TalentTagResponse(BaseModel):
    """人才标签响应（含 JOIN 的员工和标签信息）"""
    talent_tag_id: int
    emp_id: int
    tag_id: int
    tag_source: str
    score: Optional[float] = None
    expire_time: Optional[datetime] = None
    status: Optional[str] = '1'
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    # JOIN sys_emp
    emp_name: Optional[str] = None
    emp_code: Optional[str] = None
    dept_name: Optional[str] = None
    post_name: Optional[str] = None
    # JOIN sys_tag
    tag_name: Optional[str] = None
    tag_code: Optional[str] = None
    tag_category: Optional[str] = None

    class Config:
        from_attributes = True


class TalentTagListResponse(BaseModel):
    """人才标签列表响应"""
    items: List[TalentTagResponse]
    total: int
    page: int
    page_size: int


class TalentTagStats(BaseModel):
    """人才标签统计"""
    total: int
    active: int
    expired: int
    removed: int
    unique_employees: int


# ==================== 人才标签日志 Schema (talent_tag_log) ====================

class TalentTagLogResponse(BaseModel):
    """标签操作日志响应"""
    log_id: int
    emp_id: int
    tag_id: int
    action: str  # add/remove
    action_source: str  # auto/manual
    action_reason: Optional[str] = None
    rule_id: Optional[int] = None
    create_time: Optional[datetime] = None
    # JOIN
    emp_name: Optional[str] = None
    tag_name: Optional[str] = None

    class Config:
        from_attributes = True


# ==================== 兼容旧接口别名 ====================

TagRecordCreate = TalentTagCreate
TagRecordUpdate = TalentTagUpdate
TagRecordResponse = TalentTagResponse
TagRecordListResponse = TalentTagListResponse
TagRecordStats = TalentTagStats
