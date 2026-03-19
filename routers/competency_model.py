import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session
from database import get_db
from models import (
    CompetencyModel, CompetencyModelCondition, CompetencyDimension,
    CompetencyItem, ScoringScheme, ScoringLevelMapping,
    BehaviorAnchor, TagTriggerRule, TagTriggerCondition, TagTriggerAction,
)
from middleware import get_current_user

router = APIRouter(prefix="/api/hr/competency-model", tags=["胜任力模型"])
scoring_router = APIRouter(prefix="/api/hr/scoring-scheme", tags=["评分方案"])


# ---------- Schemas ----------

class ConditionSchema(BaseModel):
    dimension: str
    values: list
    logic: str = "AND"
    sortOrder: int = 0

    class Config:
        populate_by_name = True


class BehaviorAnchorSchema(BaseModel):
    level: str
    label: str
    behaviorDescription: str
    example: Optional[str] = None
    minScore: Optional[float] = None
    maxScore: Optional[float] = None

    class Config:
        populate_by_name = True


class IndicatorSchema(BaseModel):
    name: str
    description: Optional[str] = None
    level: str = "熟练"
    weight: float = 0
    sortOrder: int = 0
    behaviorAnchors: List[BehaviorAnchorSchema] = []

    class Config:
        populate_by_name = True


class DimensionSchema(BaseModel):
    name: str
    icon: Optional[str] = None
    color: Optional[str] = None
    weight: float = 25.0
    sortOrder: int = 0
    indicators: List[IndicatorSchema] = []

    class Config:
        populate_by_name = True


class LevelMappingSchema(BaseModel):
    level: str
    label: str
    minScore: float
    maxScore: float

    class Config:
        populate_by_name = True


class ScoringSchemeSchema(BaseModel):
    name: str
    type: str
    scale: int = 100
    description: Optional[str] = None
    levelDictType: str = "L1_L5"
    peerGroupRule: Optional[str] = None
    levelMappings: List[LevelMappingSchema] = []

    class Config:
        populate_by_name = True


class TriggerConditionSchema(BaseModel):
    type: str
    targetId: Optional[str] = None
    targetName: Optional[str] = None
    operator: str = ">="
    value: str

    class Config:
        populate_by_name = True


class TriggerActionSchema(BaseModel):
    type: str
    config: Optional[str] = None

    class Config:
        populate_by_name = True


class TagTriggerRuleSchema(BaseModel):
    tagName: str
    tagColor: str = "#1976D2"
    tagCategory: str
    ruleType: str
    logic: str = "AND"
    expireDays: Optional[int] = None
    conditions: List[TriggerConditionSchema] = []
    actions: List[TriggerActionSchema] = []

    class Config:
        populate_by_name = True


class CompetencyModelCreate(BaseModel):
    positionName: str
    positionLevel: str
    department: str
    industry: str
    version: str = "V1.0"
    status: str = "draft"
    style: Optional[str] = None
    conditions: List[ConditionSchema] = []
    dimensions: List[DimensionSchema] = []
    scoringScheme: Optional[ScoringSchemeSchema] = None
    tagTriggerRules: List[TagTriggerRuleSchema] = []

    class Config:
        populate_by_name = True


# ---------- Helper Functions ----------

def _generate_model_code(db: Session) -> str:
    """生成模型编码 CM-YYYY-NNN"""
    year = datetime.now().year
    prefix = f"CM-{year}-"
    last = db.query(CompetencyModel).filter(
        CompetencyModel.model_code.like(f"{prefix}%")
    ).order_by(CompetencyModel.model_code.desc()).first()
    if last:
        num = int(last.model_code.split("-")[-1]) + 1
    else:
        num = 1
    return f"{prefix}{num:03d}"


def _model_to_dict(obj: CompetencyModel) -> dict:
    """转换模型基本信息为字典（列表用）"""
    return {
        "id": obj.id,
        "modelCode": obj.model_code,
        "positionName": obj.position_name,
        "positionLevel": obj.position_level,
        "department": obj.department,
        "industry": obj.industry,
        "version": obj.version,
        "status": obj.status,
        "style": obj.style,
        "createdBy": obj.created_by,
        "createdAt": obj.created_at.isoformat() if obj.created_at else None,
        "updatedAt": obj.updated_at.isoformat() if obj.updated_at else None,
    }


def _get_or_404(db: Session, model_id: str) -> CompetencyModel:
    """获取模型或返回404"""
    obj = db.query(CompetencyModel).filter_by(id=model_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="胜任力模型不存在")
    return obj


def _build_detail(db: Session, obj: CompetencyModel) -> dict:
    """构建完整嵌套详情"""
    data = _model_to_dict(obj)

    # conditions
    conditions = db.query(CompetencyModelCondition).filter_by(
        model_id=obj.id
    ).order_by(CompetencyModelCondition.sort_order).all()
    data["conditions"] = [{
        "id": c.id, "dimension": c.dimension, "values": c.values,
        "logic": c.logic, "sortOrder": c.sort_order,
    } for c in conditions]

    # dimensions -> indicators -> behaviorAnchors
    dimensions = db.query(CompetencyDimension).filter_by(
        model_id=obj.id
    ).order_by(CompetencyDimension.sort_order).all()
    dim_list = []
    for dim in dimensions:
        items = db.query(CompetencyItem).filter_by(
            dimension_id=dim.id, model_id=obj.id
        ).order_by(CompetencyItem.sort_order).all()
        ind_list = []
        for item in items:
            anchors = db.query(BehaviorAnchor).filter_by(
                item_id=item.id, model_id=obj.id
            ).all()
            ind_list.append({
                "id": item.id, "name": item.name,
                "description": item.description, "level": item.level,
                "weight": float(item.weight), "sortOrder": item.sort_order,
                "behaviorAnchors": [{
                    "id": a.id, "level": a.level, "label": a.label,
                    "behaviorDescription": a.behavior_description,
                    "example": a.example,
                    "minScore": float(a.min_score) if a.min_score is not None else None,
                    "maxScore": float(a.max_score) if a.max_score is not None else None,
                } for a in anchors],
            })
        dim_list.append({
            "id": dim.id, "name": dim.name, "icon": dim.icon,
            "color": dim.color, "weight": float(dim.weight),
            "sortOrder": dim.sort_order, "indicators": ind_list,
        })
    data["dimensions"] = dim_list

    # scoringScheme -> levelMappings
    scheme = db.query(ScoringScheme).filter_by(model_id=obj.id).first()
    if scheme:
        mappings = db.query(ScoringLevelMapping).filter_by(
            scheme_id=scheme.id
        ).all()
        data["scoringScheme"] = {
            "id": scheme.id, "name": scheme.name, "type": scheme.type,
            "scale": scheme.scale, "description": scheme.description,
            "levelDictType": scheme.level_dict_type,
            "peerGroupRule": scheme.peer_group_rule,
            "levelMappings": [{
                "id": m.id, "level": m.level, "label": m.label,
                "minScore": float(m.min_score),
                "maxScore": float(m.max_score),
            } for m in mappings],
        }
    else:
        data["scoringScheme"] = None

    # tagTriggerRules -> conditions + actions
    rules = db.query(TagTriggerRule).filter_by(model_id=obj.id).all()
    rule_list = []
    for r in rules:
        conds = db.query(TagTriggerCondition).filter_by(rule_id=r.id).all()
        acts = db.query(TagTriggerAction).filter_by(rule_id=r.id).all()
        rule_list.append({
            "id": r.id, "tagName": r.tag_name, "tagColor": r.tag_color,
            "tagCategory": r.tag_category, "ruleType": r.rule_type,
            "logic": r.logic, "expireDays": r.expire_days,
            "conditions": [{
                "id": tc.id, "type": tc.type, "targetId": tc.target_id,
                "targetName": tc.target_name, "operator": tc.operator,
                "value": tc.value,
            } for tc in conds],
            "actions": [{
                "id": ta.id, "type": ta.type, "config": ta.config,
            } for ta in acts],
        })
    data["tagTriggerRules"] = rule_list

    return data


def _save_related_data(db: Session, model_id: str, data: CompetencyModelCreate):
    """保存模型关联数据（conditions, dimensions, items, anchors, scoring, tags）"""
    # conditions
    for i, c in enumerate(data.conditions):
        db.add(CompetencyModelCondition(
            model_id=model_id, dimension=c.dimension, values=c.values,
            logic=c.logic, sort_order=c.sortOrder or i,
        ))

    # dimensions -> indicators -> behaviorAnchors
    for di, dim in enumerate(data.dimensions):
        dim_obj = CompetencyDimension(
            model_id=model_id, name=dim.name, icon=dim.icon,
            color=dim.color, weight=dim.weight, sort_order=dim.sortOrder or di,
        )
        db.add(dim_obj)
        db.flush()  # get dim_obj.id

        for ii, ind in enumerate(dim.indicators):
            item_obj = CompetencyItem(
                dimension_id=dim_obj.id, model_id=model_id,
                name=ind.name, description=ind.description,
                level=ind.level, weight=ind.weight,
                sort_order=ind.sortOrder or ii,
            )
            db.add(item_obj)
            db.flush()  # get item_obj.id

            for anchor in ind.behaviorAnchors:
                db.add(BehaviorAnchor(
                    item_id=item_obj.id, model_id=model_id,
                    level=anchor.level, label=anchor.label,
                    behavior_description=anchor.behaviorDescription,
                    example=anchor.example,
                    min_score=anchor.minScore, max_score=anchor.maxScore,
                ))

    # scoringScheme -> levelMappings
    if data.scoringScheme:
        s = data.scoringScheme
        scheme_id = str(uuid.uuid4())
        db.add(ScoringScheme(
            id=scheme_id, model_id=model_id, name=s.name, type=s.type,
            scale=s.scale, description=s.description,
            level_dict_type=s.levelDictType, peer_group_rule=s.peerGroupRule,
        ))
        for lm in s.levelMappings:
            db.add(ScoringLevelMapping(
                scheme_id=scheme_id, level=lm.level, label=lm.label,
                min_score=lm.minScore, max_score=lm.maxScore,
            ))

    # tagTriggerRules -> conditions + actions
    for rule in data.tagTriggerRules:
        rule_obj = TagTriggerRule(
            model_id=model_id, tag_name=rule.tagName,
            tag_color=rule.tagColor, tag_category=rule.tagCategory,
            rule_type=rule.ruleType, logic=rule.logic,
            expire_days=rule.expireDays,
        )
        db.add(rule_obj)
        db.flush()  # get rule_obj.id

        for tc in rule.conditions:
            db.add(TagTriggerCondition(
                rule_id=rule_obj.id, type=tc.type,
                target_id=tc.targetId, target_name=tc.targetName,
                operator=tc.operator, value=tc.value,
            ))
        for ta in rule.actions:
            db.add(TagTriggerAction(
                rule_id=rule_obj.id, type=ta.type, config=ta.config,
            ))


def _delete_related_data(db: Session, model_id: str):
    """删除模型所有关联数据"""
    # 按依赖顺序删除（子表先删）
    db.query(BehaviorAnchor).filter_by(model_id=model_id).delete()
    db.query(CompetencyItem).filter_by(model_id=model_id).delete()
    db.query(CompetencyDimension).filter_by(model_id=model_id).delete()
    db.query(CompetencyModelCondition).filter_by(model_id=model_id).delete()
    # scoring: need scheme_id first
    scheme = db.query(ScoringScheme).filter_by(model_id=model_id).first()
    if scheme:
        db.query(ScoringLevelMapping).filter_by(scheme_id=scheme.id).delete()
        db.delete(scheme)
    # tag rules
    rules = db.query(TagTriggerRule).filter_by(model_id=model_id).all()
    rule_ids = [r.id for r in rules]
    if rule_ids:
        db.query(TagTriggerCondition).filter(
            TagTriggerCondition.rule_id.in_(rule_ids)
        ).delete(synchronize_session=False)
        db.query(TagTriggerAction).filter(
            TagTriggerAction.rule_id.in_(rule_ids)
        ).delete(synchronize_session=False)
    db.query(TagTriggerRule).filter_by(model_id=model_id).delete()


# ---------- API Routes ----------

@router.get("")
def get_list(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    status: Optional[str] = None,
    industry: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """列表查询（分页、筛选、搜索）"""
    query = db.query(CompetencyModel)

    if status:
        query = query.filter(CompetencyModel.status == status)
    if industry:
        query = query.filter(CompetencyModel.industry == industry)
    if search:
        query = query.filter(or_(
            CompetencyModel.position_name.like(f"%{search}%"),
            CompetencyModel.department.like(f"%{search}%"),
            CompetencyModel.model_code.like(f"%{search}%"),
        ))

    total = query.count()
    items = query.order_by(CompetencyModel.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return {
        "code": 200, "message": "success",
        "data": {
            "total": total, "page": page, "pageSize": page_size,
            "items": [_model_to_dict(m) for m in items],
        },
    }


@router.get("/{model_id}")
def get_detail(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """详情查询（完整嵌套数据）"""
    obj = _get_or_404(db, model_id)
    return {"code": 200, "message": "success", "data": _build_detail(db, obj)}


@router.post("")
def create(
    data: CompetencyModelCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """创建胜任力模型（含全部关联数据）"""
    model_id = str(uuid.uuid4())
    model_code = _generate_model_code(db)

    obj = CompetencyModel(
        id=model_id,
        model_code=model_code,
        position_name=data.positionName,
        position_level=data.positionLevel,
        department=data.department,
        industry=data.industry,
        version=data.version,
        status=data.status,
        style=data.style,
        created_by=str(current_user.get("id") or ""),
    )
    db.add(obj)
    db.flush()

    _save_related_data(db, model_id, data)
    db.commit()
    db.refresh(obj)

    return {"code": 200, "message": "创建成功", "data": _build_detail(db, obj)}


@router.put("/{model_id}")
def update(
    model_id: str,
    data: CompetencyModelCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """更新胜任力模型（删除旧关联数据后重新插入）"""
    obj = _get_or_404(db, model_id)

    # 更新基本字段
    obj.position_name = data.positionName
    obj.position_level = data.positionLevel
    obj.department = data.department
    obj.industry = data.industry
    obj.version = data.version
    obj.status = data.status
    obj.style = data.style

    # 删除旧关联数据，重新插入
    _delete_related_data(db, model_id)
    db.flush()
    _save_related_data(db, model_id, data)

    db.commit()
    db.refresh(obj)
    return {"code": 200, "message": "更新成功", "data": _build_detail(db, obj)}


@router.delete("/{model_id}")
def delete(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """删除胜任力模型及所有关联数据"""
    obj = _get_or_404(db, model_id)
    _delete_related_data(db, model_id)
    db.delete(obj)
    db.commit()
    return {"code": 200, "message": "删除成功"}


@router.post("/{model_id}/copy")
def copy_model(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """深拷贝胜任力模型及所有关联数据"""
    src = _get_or_404(db, model_id)
    new_id = str(uuid.uuid4())
    new_code = _generate_model_code(db)

    new_obj = CompetencyModel(
        id=new_id,
        model_code=new_code,
        position_name=src.position_name + "（副本）",
        position_level=src.position_level,
        department=src.department,
        industry=src.industry,
        version=src.version,
        status="draft",
        style=src.style,
        created_by=str(current_user.get("id") or ""),
    )
    db.add(new_obj)
    db.flush()

    # 复制 conditions
    for c in db.query(CompetencyModelCondition).filter_by(model_id=model_id).all():
        db.add(CompetencyModelCondition(
            model_id=new_id, dimension=c.dimension, values=c.values,
            logic=c.logic, sort_order=c.sort_order,
        ))

    # 复制 dimensions -> items -> anchors
    for dim in db.query(CompetencyDimension).filter_by(model_id=model_id).all():
        new_dim = CompetencyDimension(
            model_id=new_id, name=dim.name, icon=dim.icon,
            color=dim.color, weight=dim.weight, sort_order=dim.sort_order,
        )
        db.add(new_dim)
        db.flush()

        for item in db.query(CompetencyItem).filter_by(
            dimension_id=dim.id, model_id=model_id
        ).all():
            new_item = CompetencyItem(
                dimension_id=new_dim.id, model_id=new_id,
                name=item.name, description=item.description,
                level=item.level, weight=item.weight,
                sort_order=item.sort_order,
            )
            db.add(new_item)
            db.flush()

            for a in db.query(BehaviorAnchor).filter_by(
                item_id=item.id, model_id=model_id
            ).all():
                db.add(BehaviorAnchor(
                    item_id=new_item.id, model_id=new_id,
                    level=a.level, label=a.label,
                    behavior_description=a.behavior_description,
                    example=a.example,
                    min_score=a.min_score, max_score=a.max_score,
                ))

    # 复制 scoringScheme -> levelMappings
    old_scheme = db.query(ScoringScheme).filter_by(model_id=model_id).first()
    if old_scheme:
        new_scheme_id = str(uuid.uuid4())
        db.add(ScoringScheme(
            id=new_scheme_id, model_id=new_id, name=old_scheme.name,
            type=old_scheme.type, scale=old_scheme.scale,
            description=old_scheme.description,
            level_dict_type=old_scheme.level_dict_type,
            peer_group_rule=old_scheme.peer_group_rule,
        ))
        for lm in db.query(ScoringLevelMapping).filter_by(
            scheme_id=old_scheme.id
        ).all():
            db.add(ScoringLevelMapping(
                scheme_id=new_scheme_id, level=lm.level, label=lm.label,
                min_score=lm.min_score, max_score=lm.max_score,
            ))

    # 复制 tagTriggerRules -> conditions + actions
    for rule in db.query(TagTriggerRule).filter_by(model_id=model_id).all():
        new_rule = TagTriggerRule(
            model_id=new_id, tag_name=rule.tag_name,
            tag_color=rule.tag_color, tag_category=rule.tag_category,
            rule_type=rule.rule_type, logic=rule.logic,
            expire_days=rule.expire_days,
        )
        db.add(new_rule)
        db.flush()

        for tc in db.query(TagTriggerCondition).filter_by(rule_id=rule.id).all():
            db.add(TagTriggerCondition(
                rule_id=new_rule.id, type=tc.type,
                target_id=tc.target_id, target_name=tc.target_name,
                operator=tc.operator, value=tc.value,
            ))
        for ta in db.query(TagTriggerAction).filter_by(rule_id=rule.id).all():
            db.add(TagTriggerAction(
                rule_id=new_rule.id, type=ta.type, config=ta.config,
            ))

    db.commit()
    db.refresh(new_obj)
    return {"code": 200, "message": "复制成功", "data": _build_detail(db, new_obj)}


# ---------- 评分方案预置模板接口 (Issue #74) ----------

@scoring_router.get("/presets")
def get_scoring_presets(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """查询预置评分方案模板（含等级映射）"""
    schemes = db.query(ScoringScheme).filter(
        ScoringScheme.model_id.is_(None)
    ).all()

    result = []
    for s in schemes:
        mappings = db.query(ScoringLevelMapping).filter_by(
            scheme_id=s.id
        ).order_by(ScoringLevelMapping.min_score).all()
        result.append({
            "id": s.id,
            "name": s.name,
            "type": s.type,
            "scale": s.scale,
            "description": s.description,
            "levelDictType": s.level_dict_type,
            "peerGroupRule": s.peer_group_rule,
            "levelMappings": [{
                "id": m.id,
                "level": m.level,
                "label": m.label,
                "minScore": float(m.min_score),
                "maxScore": float(m.max_score),
            } for m in mappings],
        })

    return {
        "code": 200, "message": "success",
        "data": {
            "total": len(result),
            "items": result,
        },
    }


# ---------- AI 生成维度指标接口 (Issue #81) ----------

class AIGenerateRequest(BaseModel):
    positionName: str
    positionLevel: str   # "初级", "中级", "高级", "专家"
    industry: str        # "互联网", "金融", "制造", "医疗", "教育", "其他"

    class Config:
        populate_by_name = True


# 基础维度定义
_BASE_DIMENSIONS = [
    {"name": "业务能力", "icon": "ri-briefcase-line", "color": "#1976D2"},
    {"name": "专业技能", "icon": "ri-tools-line",     "color": "#388E3C"},
    {"name": "领导力",   "icon": "ri-team-line",      "color": "#F57C00"},
    {"name": "个人特质", "icon": "ri-user-star-line",  "color": "#7B1FA2"},
]

# 各级别维度权重分配: {level: [业务能力, 专业技能, 领导力, 个人特质]}
_LEVEL_WEIGHTS = {
    "初级": [20, 40, 10, 30],
    "中级": [25, 35, 15, 25],
    "高级": [30, 25, 25, 20],
    "专家": [35, 20, 30, 15],
}

# 各级别对应的指标等级
_LEVEL_INDICATOR_MAP = {
    "初级": "入门",
    "中级": "熟练",
    "高级": "精通",
    "专家": "专家",
}

# 行业 + 维度 -> 指标列表 (name, description)
_INDUSTRY_INDICATORS = {
    "互联网": {
        "业务能力": [
            ("产品思维", "能够从用户需求出发，设计和优化产品方案"),
            ("数据驱动", "善于利用数据分析支撑业务决策和效果评估"),
            ("用户体验", "关注用户体验，持续优化交互流程和满意度"),
            ("商业洞察", "具备商业敏感度，能识别市场机会和竞争态势"),
        ],
        "专业技能": [
            ("技术架构", "能够设计合理的系统架构，保障可扩展性和稳定性"),
            ("编程能力", "熟练掌握核心编程语言，编写高质量代码"),
            ("系统设计", "具备系统设计能力，能进行模块划分和接口设计"),
            ("问题排查", "能够快速定位和解决线上问题，保障系统稳定运行"),
        ],
        "领导力": [
            ("团队管理", "能够有效管理团队，合理分配任务和资源"),
            ("项目推动", "具备项目推动能力，确保项目按时高质量交付"),
            ("跨部门协作", "善于跨部门沟通协调，推动跨团队合作"),
            ("人才培养", "重视团队成员成长，提供指导和发展机会"),
        ],
        "个人特质": [
            ("学习能力", "保持学习热情，快速掌握新技术和新知识"),
            ("创新思维", "善于突破常规思维，提出创新性解决方案"),
            ("抗压能力", "能够在高压环境下保持高效工作和积极心态"),
            ("沟通表达", "具备清晰的表达能力，能有效传递信息和观点"),
        ],
    },
    "金融": {
        "业务能力": [
            ("风险管理", "能够识别、评估和控制各类金融风险"),
            ("合规意识", "熟悉金融法规，确保业务操作合规合法"),
            ("市场分析", "具备市场分析能力，准确判断市场趋势"),
            ("客户服务", "以客户为中心，提供专业的金融服务方案"),
        ],
        "专业技能": [
            ("财务分析", "熟练运用财务分析工具，进行深度财务诊断"),
            ("投资评估", "能够对投资项目进行全面评估和风险定价"),
            ("数据建模", "具备金融数据建模能力，支撑量化分析决策"),
            ("法规解读", "能够准确解读金融法规政策，指导业务实践"),
        ],
        "领导力": [
            ("团队管理", "能够有效管理团队，合理分配任务和资源"),
            ("决策能力", "具备果断决策能力，在复杂环境中做出正确判断"),
            ("危机处理", "能够冷静应对突发危机，制定有效应对方案"),
            ("战略规划", "具备战略视野，能制定中长期发展规划"),
        ],
        "个人特质": [
            ("严谨细致", "工作严谨细致，注重数据准确性和流程规范"),
            ("诚信正直", "坚守职业道德，诚实守信，公正客观"),
            ("抗压能力", "能够在高压环境下保持高效工作和积极心态"),
            ("沟通表达", "具备清晰的表达能力，能有效传递信息和观点"),
        ],
    },
    "制造": {
        "业务能力": [
            ("生产管理", "能够高效组织和管理生产流程，保障产能和交期"),
            ("质量控制", "建立和维护质量管理体系，确保产品质量达标"),
            ("供应链管理", "具备供应链管理能力，优化采购和物流效率"),
            ("成本优化", "善于分析和控制生产成本，提升经营效益"),
        ],
        "专业技能": [
            ("工艺技术", "熟悉生产工艺流程，能进行工艺优化和改进"),
            ("设备管理", "具备设备管理能力，保障设备高效稳定运行"),
            ("安全管理", "熟悉安全生产规范，建立和执行安全管理制度"),
            ("精益生产", "掌握精益生产方法，持续消除浪费提升效率"),
        ],
        "领导力": [
            ("团队管理", "能够有效管理团队，合理分配任务和资源"),
            ("现场管理", "具备现场管理能力，维护生产秩序和工作环境"),
            ("跨部门协作", "善于跨部门沟通协调，推动跨团队合作"),
            ("持续改进", "推动持续改进文化，带领团队不断优化流程"),
        ],
        "个人特质": [
            ("执行力", "具备强执行力，能够高效落实工作计划和目标"),
            ("责任心", "工作认真负责，对结果负责，勇于担当"),
            ("安全意识", "始终将安全放在首位，严格遵守安全规范"),
            ("学习能力", "保持学习热情，快速掌握新技术和新知识"),
        ],
    },
    "医疗": {
        "业务能力": [
            ("临床管理", "能够有效管理临床业务流程，提升医疗服务质量"),
            ("患者服务", "以患者为中心，提供优质的医疗服务体验"),
            ("医疗质量", "建立和维护医疗质量管理体系，保障医疗安全"),
            ("科研能力", "具备科研素养，能开展临床研究和学术探索"),
        ],
        "专业技能": [
            ("专业知识", "具备扎实的医学专业知识，持续更新知识体系"),
            ("诊疗技术", "熟练掌握诊疗技术，能准确诊断和有效治疗"),
            ("医疗设备", "熟悉医疗设备操作和维护，保障设备正常使用"),
            ("循证医学", "运用循证医学方法，基于证据制定诊疗方案"),
        ],
        "领导力": [
            ("团队管理", "能够有效管理团队，合理分配任务和资源"),
            ("医患沟通", "具备良好的医患沟通能力，建立信任关系"),
            ("应急处理", "能够冷静应对医疗突发事件，快速有效处置"),
            ("教学带教", "重视医学教育，能有效指导和培养年轻医师"),
        ],
        "个人特质": [
            ("同理心", "具备同理心，能理解和关怀患者的身心需求"),
            ("责任心", "工作认真负责，对患者生命健康高度负责"),
            ("学习能力", "保持学习热情，快速掌握新技术和新知识"),
            ("抗压能力", "能够在高压环境下保持高效工作和积极心态"),
        ],
    },
    "教育": {
        "业务能力": [
            ("教学设计", "能够设计科学合理的教学方案，提升教学效果"),
            ("课程开发", "具备课程开发能力，设计符合需求的课程体系"),
            ("学生管理", "善于管理学生，营造积极向上的学习氛围"),
            ("教育研究", "具备教育研究能力，探索教育教学规律和方法"),
        ],
        "专业技能": [
            ("学科知识", "具备深厚的学科专业知识，能准确传授核心内容"),
            ("教学方法", "掌握多种教学方法，能因材施教提升学习效果"),
            ("教育技术", "熟练运用教育技术工具，丰富教学手段和形式"),
            ("评估设计", "能够设计科学的评估方案，准确衡量学习成效"),
        ],
        "领导力": [
            ("团队协作", "善于与同事协作，共同推进教学和科研工作"),
            ("家校沟通", "具备良好的家校沟通能力，形成教育合力"),
            ("活动组织", "能够策划和组织各类教育活动，丰富校园文化"),
            ("导师指导", "能有效指导学生成长，提供学业和职业发展建议"),
        ],
        "个人特质": [
            ("耐心", "具备耐心，能够细致地引导和帮助每位学生"),
            ("创新思维", "善于突破常规思维，探索新的教学方式和理念"),
            ("学习能力", "保持学习热情，快速掌握新技术和新知识"),
            ("表达能力", "具备出色的语言表达能力，能清晰生动地讲解"),
        ],
    },
}

# 通用行业指标（用于"其他"或未匹配的行业）
_DEFAULT_INDICATORS = {
    "业务能力": [
        ("战略思维", "能够从全局视角分析问题，制定长期发展策略"),
        ("业务规划", "具备业务规划能力，能制定可执行的工作计划"),
        ("客户导向", "以客户需求为导向，持续提升服务质量和满意度"),
        ("结果导向", "注重工作成果，以目标为驱动推进各项工作"),
    ],
    "专业技能": [
        ("专业知识", "具备扎实的专业知识基础，能解决领域内核心问题"),
        ("工具应用", "熟练使用专业工具和软件，提升工作效率"),
        ("分析能力", "具备数据分析和逻辑推理能力，支撑科学决策"),
        ("问题解决", "能够快速识别问题根因，提出有效解决方案"),
    ],
    "领导力": [
        ("团队管理", "能够有效管理团队，合理分配任务和资源"),
        ("沟通协调", "善于沟通协调，推动跨团队和跨部门合作"),
        ("决策能力", "具备果断决策能力，在复杂环境中做出正确判断"),
        ("人才发展", "重视团队成员成长，提供指导和发展机会"),
    ],
    "个人特质": [
        ("学习能力", "保持学习热情，快速掌握新技术和新知识"),
        ("责任心", "工作认真负责，对结果负责，勇于担当"),
        ("抗压能力", "能够在高压环境下保持高效工作和积极心态"),
        ("沟通表达", "具备清晰的表达能力，能有效传递信息和观点"),
    ],
}


def _generate_dimensions(req: AIGenerateRequest) -> list:
    """根据岗位信息生成推荐维度和指标"""
    weights = _LEVEL_WEIGHTS.get(req.positionLevel, _LEVEL_WEIGHTS["中级"])
    indicator_level = _LEVEL_INDICATOR_MAP.get(req.positionLevel, "熟练")
    industry_data = _INDUSTRY_INDICATORS.get(req.industry, _DEFAULT_INDICATORS)

    dimensions = []
    for idx, base in enumerate(_BASE_DIMENSIONS):
        dim_name = base["name"]
        # 获取该行业该维度的指标，找不到则用默认
        raw_indicators = industry_data.get(dim_name, _DEFAULT_INDICATORS.get(dim_name, []))
        ind_count = len(raw_indicators) or 1
        ind_weight = round(100 / ind_count)

        indicators = []
        for i, (name, desc) in enumerate(raw_indicators):
            indicators.append({
                "name": name,
                "description": desc,
                "level": indicator_level,
                "weight": ind_weight,
                "sortOrder": i,
            })

        dimensions.append({
            "name": dim_name,
            "icon": base["icon"],
            "color": base["color"],
            "weight": weights[idx],
            "sortOrder": idx,
            "indicators": indicators,
        })

    return dimensions


@router.post("/ai-generate")
def ai_generate(
    req: AIGenerateRequest,
    current_user: dict = Depends(get_current_user),
):
    """AI 生成推荐维度和指标（基于模板匹配）"""
    dimensions = _generate_dimensions(req)
    return {
        "code": 200,
        "message": "success",
        "data": {"dimensions": dimensions},
    }
