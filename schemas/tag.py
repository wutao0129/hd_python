from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==================== 标签库 Schema (sys_tag) ====================

class TagBase(BaseModel):
    tag_name: str = Field(..., max_length=100)
    tag_code: str = Field(..., max_length=100)
    tag_category: str = Field(..., max_length=50)
    tag_type: str = Field(default='1')  # 0内置 1自定义
    scene: Optional[List[str]] = None
    rule_type: Optional[List[str]] = None
    rule_detail: Optional[str] = None
    description: Optional[str] = None
    status: str = Field(default='0')  # 0草稿 1启用 2停用
    remark: Optional[str] = None
    parent_id: Optional[int] = None
    usage_count: Optional[int] = 0
    activity_rate: Optional[int] = 0
    graph_type: Optional[str] = None
    relation_name: Optional[str] = None
    similar_tags: Optional[str] = None
    exclusive_tags: Optional[str] = None


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    tag_name: Optional[str] = None
    tag_code: Optional[str] = None
    tag_category: Optional[str] = None
    tag_type: Optional[str] = None
    scene: Optional[List[str]] = None
    rule_type: Optional[List[str]] = None
    rule_detail: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    remark: Optional[str] = None
    parent_id: Optional[int] = None
    usage_count: Optional[int] = None
    activity_rate: Optional[int] = None
    graph_type: Optional[str] = None
    relation_name: Optional[str] = None
    similar_tags: Optional[str] = None
    exclusive_tags: Optional[str] = None


class TagResponse(TagBase):
    tag_id: int
    del_flag: Optional[str] = '0'
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    tenant_id: Optional[str] = None

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


# ==================== 知识图谱 Schema ====================

class TagGraphNode(BaseModel):
    id: int
    name: str
    category: str
    usage_count: int = 0
    level: int = 0
    description: Optional[str] = None
    graph_type: Optional[str] = None
    relation_name: Optional[str] = None
    parent_id: Optional[int] = None


class TagGraphRelation(BaseModel):
    source: int = Field(..., alias='from')
    target: int = Field(..., alias='to')
    type: str
    strength: float = 1.0

    class Config:
        populate_by_name = True


class TagGraphResponse(BaseModel):
    nodes: List[TagGraphNode]
    relations: List[TagGraphRelation]


# ==================== 触发规则 Schema ====================

class TriggerConditionItem(BaseModel):
    condition_id: Optional[int] = None
    type: str  # field_compare / tag_exists
    target_id: Optional[str] = None
    target_name: Optional[str] = None
    operator: str = '>='
    value: str


class TriggerActionItem(BaseModel):
    action_id: Optional[int] = None
    type: str  # add_to_talent_tag / send_notification / push_training / add_to_succession
    config: Optional[str] = None


class TriggerRuleResponse(BaseModel):
    rule_id: int
    model_id: str
    tag_name: str
    tag_color: str = '#1976D2'
    tag_category: str
    rule_type: str
    logic: str = 'AND'
    expire_days: Optional[int] = None
    status: Optional[str] = '0'
    conditions: List[TriggerConditionItem] = []
    actions: List[TriggerActionItem] = []

    class Config:
        from_attributes = True


class TriggerRuleSaveRequest(BaseModel):
    model_id: str
    tag_name: str
    tag_color: str = '#1976D2'
    tag_category: str
    rule_type: str
    logic: str = 'AND'
    expire_days: Optional[int] = None
    conditions: List[TriggerConditionItem] = []
    actions: List[TriggerActionItem] = []


# ==================== 兼容旧规则接口（前端 RuleConfigTab 使用） ====================

class TagRuleItem(BaseModel):
    id: Optional[int] = None
    left_bracket: str = ''
    condition: str
    operator: str
    value: str
    right_bracket: str = ''
    logic: str = ''


class TagRuleSaveRequest(BaseModel):
    rules: List[TagRuleItem]


class TagRuleResponse(BaseModel):
    id: int
    tag_id: int
    sort_order: int
    left_bracket: str
    condition: str
    operator: str
    value: str
    right_bracket: str
    logic: str

    class Config:
        from_attributes = True
