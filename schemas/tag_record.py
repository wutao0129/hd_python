from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TagRecordBase(BaseModel):
    employee_id: str = Field(..., max_length=50)
    employee_name: str = Field(..., max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    tag_id: int
    source: str = Field(default='manual', max_length=50)
    source_detail: Optional[str] = None
    tagged_by: Optional[str] = Field(None, max_length=100)
    expires_at: Optional[datetime] = None


class TagRecordCreate(TagRecordBase):
    """创建标签记录"""
    pass


class TagRecordUpdate(BaseModel):
    """更新标签记录"""
    source_detail: Optional[str] = None
    expires_at: Optional[datetime] = None
    status: Optional[str] = None
    remove_reason: Optional[str] = None


class TagRecordResponse(TagRecordBase):
    """标签记录响应"""
    id: int
    tag_name: str
    tag_code: str
    tag_category: str
    tagged_at: datetime
    status: str
    removed_at: Optional[datetime] = None
    removed_by: Optional[str] = None
    remove_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TagRecordListResponse(BaseModel):
    """标签记录列表响应"""
    items: List[TagRecordResponse]
    total: int
    page: int
    page_size: int


class TagRecordStats(BaseModel):
    """标签记录统计"""
    total: int
    active: int
    expired: int
    removed: int
    unique_employees: int
