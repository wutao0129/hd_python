from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TagBase(BaseModel):
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=100)
    category: str = Field(..., max_length=50)
    type: str = Field(default='自定义')
    scene: Optional[List[str]] = None
    rule_type: Optional[List[str]] = None
    rule_detail: Optional[str] = None
    description: Optional[str] = None
    status: str = Field(default='启用')
    parent_id: Optional[int] = None
    usage_count: Optional[int] = 0
    activity_rate: Optional[int] = 0
    graph_type: Optional[str] = None
    relation_name: Optional[str] = None


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    category: Optional[str] = None
    type: Optional[str] = None
    scene: Optional[List[str]] = None
    rule_type: Optional[List[str]] = None
    rule_detail: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    parent_id: Optional[int] = None
    usage_count: Optional[int] = None
    activity_rate: Optional[int] = None
    graph_type: Optional[str] = None
    relation_name: Optional[str] = None


class TagResponse(TagBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TagListResponse(BaseModel):
    items: List[TagResponse]
    total: int
    page: int
    page_size: int


class TagStats(BaseModel):
    total: int
    enabled: int
    disabled: int
    avg_activity: int
