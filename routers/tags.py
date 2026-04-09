from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc, asc
from typing import Optional
from datetime import datetime
import io
import csv
import json
from database import get_db
from models import SysTag, TalentTag, SysTagTriggerRule, SysTagTriggerCondition, SysTagTriggerAction, SysTagVersion, SysTagRelation, SysTagScene
from schemas.tag import (
    TagCreate, TagUpdate, TagResponse, TagListResponse, TagStats,
    TagGraphNode, TagGraphRelation, TagGraphResponse,
    TagRuleSaveRequest, TagRuleResponse,
    TriggerRuleResponse, TriggerRuleSaveRequest, TriggerConditionItem, TriggerActionItem,
    TagRelationCreate, TagRelationResponse,
    TagSceneCreate, TagSceneResponse,
)

router = APIRouter(prefix="/api/tags", tags=["标签库"])


@router.get("", response_model=TagListResponse)
async def get_tags(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    type: Optional[str] = None,
    scene: Optional[str] = None,
    keyword: Optional[str] = None,
    sort_by: str = Query('update_time'),
    sort_order: str = Query('desc'),
    db: Session = Depends(get_db)
):
    """获取标签列表"""
    query = db.query(SysTag).filter(SysTag.del_flag == '0')

    if category:
        query = query.filter(SysTag.tag_category == category)
    if type:
        query = query.filter(SysTag.tag_type == type)
    if scene:
        # v5: 通过 sys_tag_scene 表过滤场景
        scene_tag_ids = db.query(SysTagScene.tag_id).filter(
            SysTagScene.scene_code == scene,
            SysTagScene.del_flag == '0',
            SysTagScene.status == '1'
        ).subquery()
        query = query.filter(SysTag.tag_id.in_(scene_tag_ids))
    if keyword:
        query = query.filter(
            or_(
                SysTag.tag_name.contains(keyword),
                SysTag.tag_code.contains(keyword),
                SysTag.description.contains(keyword)
            )
        )

    total = query.count()

    sort_column = getattr(SysTag, sort_by, SysTag.update_time)
    if sort_order == 'desc':
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    # 实时计算 usage_count：从 talent_tag 表统计启用的记录数
    tag_ids = [item.tag_id for item in items]
    if tag_ids:
        usage_counts = dict(
            db.query(TalentTag.tag_id, func.count(TalentTag.talent_tag_id))
            .filter(TalentTag.tag_id.in_(tag_ids), TalentTag.status == '1', TalentTag.del_flag == '0')
            .group_by(TalentTag.tag_id)
            .all()
        )
        for item in items:
            item.usage_count = usage_counts.get(item.tag_id, 0)

    return TagListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/stats", response_model=TagStats)
async def get_tag_stats(db: Session = Depends(get_db)):
    """获取标签统计数据"""
    base = db.query(SysTag).filter(SysTag.del_flag == '0')
    total = base.count()
    enabled = base.filter(SysTag.status == '1').count()
    disabled = base.filter(SysTag.status == '2').count()
    avg_activity = db.query(func.avg(SysTag.activity_rate)).filter(SysTag.del_flag == '0').scalar() or 0

    return TagStats(
        total=total,
        enabled=enabled,
        disabled=disabled,
        avg_activity=int(avg_activity)
    )


@router.get("/categories")
async def get_tag_categories(db: Session = Depends(get_db)):
    """获取标签分类列表"""
    categories = db.query(SysTag.tag_category).filter(SysTag.del_flag == '0').distinct().all()
    return {"categories": [c[0] for c in categories]}


@router.get("/scenes")
async def get_tag_scenes(db: Session = Depends(get_db)):
    """获取标签场景列表（从 sys_tag_scene 表查询）"""
    scenes = db.query(SysTagScene.scene_code, SysTagScene.scene_name).filter(
        SysTagScene.del_flag == '0', SysTagScene.status == '1'
    ).distinct().all()
    return {"scenes": [{"code": s[0], "name": s[1] or s[0]} for s in scenes]}


@router.get("/rule-types")
async def get_tag_rule_types(db: Session = Depends(get_db)):
    """获取标签规则类型列表"""
    tags = db.query(SysTag.rule_type).filter(SysTag.del_flag == '0', SysTag.rule_type.isnot(None)).all()
    rule_types = set()
    for tag in tags:
        if tag[0]:
            rule_types.update(tag[0])
    return {"rule_types": sorted(list(rule_types))}


@router.get("/graph", response_model=TagGraphResponse)
async def get_tag_graph(db: Session = Depends(get_db)):
    """获取标签知识图谱数据（v5: 关系从 sys_tag_relation 读取）"""
    tags = db.query(SysTag).filter(SysTag.del_flag == '0', SysTag.status == '1').all()

    # 实时计算 usage_count
    tag_ids = [tag.tag_id for tag in tags]
    if tag_ids:
        usage_counts = dict(
            db.query(TalentTag.tag_id, func.count(TalentTag.talent_tag_id))
            .filter(TalentTag.tag_id.in_(tag_ids), TalentTag.status == '1', TalentTag.del_flag == '0')
            .group_by(TalentTag.tag_id)
            .all()
        )
        for tag in tags:
            tag.usage_count = usage_counts.get(tag.tag_id, 0)

    # 计算节点层级
    def calculate_level(tid, parent_map, level_cache):
        if tid in level_cache:
            return level_cache[tid]
        if tid not in parent_map or parent_map[tid] is None:
            level_cache[tid] = 0
            return 0
        parent_level = calculate_level(parent_map[tid], parent_map, level_cache)
        level_cache[tid] = parent_level + 1
        return parent_level + 1

    parent_map = {tag.tag_id: tag.parent_id for tag in tags}
    level_cache = {}

    nodes = []
    for tag in tags:
        level = calculate_level(tag.tag_id, parent_map, level_cache)
        nodes.append(TagGraphNode(
            id=tag.tag_id,
            name=tag.tag_name,
            category=tag.tag_category,
            usage_count=tag.usage_count,
            level=level,
            description=tag.description,
            parent_id=tag.parent_id
        ))

    relations = []
    tag_id_set = set(tag_ids)
    virtual_id = -1

    # 分类虚拟节点
    category_id_map = {}
    categories = set(tag.tag_category for tag in tags)
    for cat in categories:
        cat_id = virtual_id
        category_id_map[cat] = cat_id
        nodes.append(TagGraphNode(
            id=cat_id, name=cat, category=cat,
            usage_count=0, level=0
        ))
        virtual_id -= 1

    for tag in tags:
        if not tag.parent_id and tag.tag_category in category_id_map:
            relations.append(TagGraphRelation(
                **{'from': category_id_map[tag.tag_category], 'to': tag.tag_id, 'type': '包含', 'strength': 0.8}
            ))

    # 场景虚拟节点（从 sys_tag_scene 表读取）
    scene_id_map = {}
    tag_scenes = db.query(SysTagScene).filter(
        SysTagScene.del_flag == '0', SysTagScene.status == '1',
        SysTagScene.tag_id.in_(tag_ids)
    ).all()
    for ts in tag_scenes:
        if ts.scene_name not in scene_id_map:
            scene_id_map[ts.scene_name or ts.scene_code] = virtual_id
            nodes.append(TagGraphNode(
                id=virtual_id, name=ts.scene_name or ts.scene_code, category='场景',
                usage_count=0, level=0
            ))
            virtual_id -= 1
        scene_key = ts.scene_name or ts.scene_code
        relations.append(TagGraphRelation(
            **{'from': scene_id_map[scene_key], 'to': ts.tag_id, 'type': '包含', 'strength': 0.6}
        ))

    # 从 sys_tag_relation 表读取所有关系
    RELATION_TYPE_MAP = {
        'PARENT_OF': '包含',
        'BELONGS_TO_GROUP': '包含',
        'EXCLUSIVE_WITH': '互斥',
        'SIMILAR_TO': '相似',
        'DEPENDS_ON': '依赖',
        'DERIVED_FROM': '依赖',
        'COMPONENT_OF': '包含',
        'ENHANCES': '依赖',
        'WEAKENS': '互斥',
        'EVOLVES_TO': '依赖',
        'OFTEN_COEXISTS': '相似',
        'OPPOSITE_OF': '互斥',
    }
    STRENGTH_MAP = {
        'PARENT_OF': 1.0,
        'BELONGS_TO_GROUP': 0.9,
        'EXCLUSIVE_WITH': 0.8,
        'SIMILAR_TO': 0.6,
        'DEPENDS_ON': 0.7,
        'DERIVED_FROM': 0.7,
        'COMPONENT_OF': 0.9,
        'ENHANCES': 0.5,
        'WEAKENS': 0.5,
        'EVOLVES_TO': 0.6,
        'OFTEN_COEXISTS': 0.5,
        'OPPOSITE_OF': 0.8,
    }

    tag_relations = db.query(SysTagRelation).filter(
        SysTagRelation.del_flag == '0', SysTagRelation.status == '1'
    ).all()
    for rel in tag_relations:
        if rel.source_tag_id in tag_id_set and rel.target_tag_id in tag_id_set:
            relations.append(TagGraphRelation(
                **{
                    'from': rel.source_tag_id,
                    'to': rel.target_tag_id,
                    'type': RELATION_TYPE_MAP.get(rel.relation_type, rel.relation_type),
                    'strength': STRENGTH_MAP.get(rel.relation_type, 0.5),
                }
            ))

    return TagGraphResponse(nodes=nodes, relations=relations)


@router.get("/export")
async def export_tags(
    category: Optional[str] = None,
    type: Optional[str] = None,
    scene: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """导出标签数据（CSV 格式）"""
    query = db.query(SysTag).filter(SysTag.del_flag == '0')

    if category:
        query = query.filter(SysTag.tag_category == category)
    if type:
        query = query.filter(SysTag.tag_type == type)
    if scene:
        scene_tag_ids = db.query(SysTagScene.tag_id).filter(
            SysTagScene.scene_code == scene,
            SysTagScene.del_flag == '0',
            SysTagScene.status == '1'
        ).subquery()
        query = query.filter(SysTag.tag_id.in_(scene_tag_ids))
    if keyword:
        query = query.filter(
            or_(
                SysTag.tag_name.contains(keyword),
                SysTag.tag_code.contains(keyword),
                SysTag.description.contains(keyword)
            )
        )

    tags = query.all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'ID', '标签名称', '标签编码', '分类', '类型', '应用场景',
        '规则类型', '规则详情', '描述', '状态', '父标签ID',
        '使用次数', '活跃度', '创建时间', '更新时间'
    ])

    type_map = {'0': '内置', '1': '自定义'}
    status_map = {'0': '草稿', '1': '启用', '2': '停用'}

    for tag in tags:
        writer.writerow([
            tag.tag_id,
            tag.tag_name,
            tag.tag_code,
            tag.tag_category,
            type_map.get(tag.tag_type, tag.tag_type),
            ','.join(tag.scene) if tag.scene else '',
            ','.join(tag.rule_type) if tag.rule_type else '',
            tag.rule_detail or '',
            tag.description or '',
            status_map.get(tag.status, tag.status),
            tag.parent_id or '',
            tag.usage_count,
            tag.activity_rate,
            tag.create_time.strftime('%Y-%m-%d %H:%M:%S') if tag.create_time else '',
            tag.update_time.strftime('%Y-%m-%d %H:%M:%S') if tag.update_time else '',
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue().encode('utf-8-sig')]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=tags.csv"}
    )


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """获取标签详情"""
    tag = db.query(SysTag).filter(SysTag.tag_id == tag_id, SysTag.del_flag == '0').first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    # 实时计算 usage_count
    tag.usage_count = db.query(func.count(TalentTag.talent_tag_id)).filter(
        TalentTag.tag_id == tag_id, TalentTag.status == '1', TalentTag.del_flag == '0'
    ).scalar() or 0

    return tag


@router.post("", response_model=TagResponse)
async def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    """创建标签"""
    existing = db.query(SysTag).filter(SysTag.tag_code == tag.tag_code, SysTag.del_flag == '0').first()
    if existing:
        raise HTTPException(status_code=400, detail="标签编码已存在")

    if tag.parent_id:
        parent = db.query(SysTag).filter(SysTag.tag_id == tag.parent_id, SysTag.del_flag == '0').first()
        if not parent:
            raise HTTPException(status_code=400, detail="父标签不存在")

    now = datetime.now()
    db_tag = SysTag(**tag.model_dump(), create_time=now, update_time=now)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(tag_id: int, tag: TagUpdate, db: Session = Depends(get_db)):
    """更新标签"""
    db_tag = db.query(SysTag).filter(SysTag.tag_id == tag_id, SysTag.del_flag == '0').first()
    if not db_tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    if tag.tag_code and tag.tag_code != db_tag.tag_code:
        existing = db.query(SysTag).filter(SysTag.tag_code == tag.tag_code, SysTag.del_flag == '0').first()
        if existing:
            raise HTTPException(status_code=400, detail="标签编码已存在")

    if tag.parent_id:
        parent = db.query(SysTag).filter(SysTag.tag_id == tag.parent_id, SysTag.del_flag == '0').first()
        if not parent:
            raise HTTPException(status_code=400, detail="父标签不存在")

    for field, value in tag.model_dump(exclude_unset=True).items():
        setattr(db_tag, field, value)

    db_tag.update_time = datetime.now()
    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.delete("/{tag_id}")
async def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """删除标签（软删除）"""
    db_tag = db.query(SysTag).filter(SysTag.tag_id == tag_id, SysTag.del_flag == '0').first()
    if not db_tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    if db_tag.tag_type == '0':
        raise HTTPException(status_code=400, detail="内置标签不能删除")

    db_tag.del_flag = '2'
    db_tag.update_time = datetime.now()
    db.commit()
    return {"message": "删除成功"}


@router.patch("/{tag_id}/status", response_model=TagResponse)
async def toggle_tag_status(tag_id: int, db: Session = Depends(get_db)):
    """切换标签状态（启用↔停用）"""
    db_tag = db.query(SysTag).filter(SysTag.tag_id == tag_id, SysTag.del_flag == '0').first()
    if not db_tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    db_tag.status = '2' if db_tag.status == '1' else '1'
    db_tag.update_time = datetime.now()
    db.commit()
    db.refresh(db_tag)
    return db_tag


# ==================== 标签关系接口 ====================

@router.get("/{tag_id}/relations")
async def get_tag_relations(tag_id: int, db: Session = Depends(get_db)):
    """获取标签的所有关系"""
    relations = db.query(SysTagRelation).filter(
        or_(SysTagRelation.source_tag_id == tag_id, SysTagRelation.target_tag_id == tag_id),
        SysTagRelation.del_flag == '0'
    ).all()

    # 收集关联的标签ID
    related_ids = set()
    for r in relations:
        related_ids.add(r.source_tag_id)
        related_ids.add(r.target_tag_id)
    related_ids.discard(tag_id)

    # 查询关联标签名称
    tag_name_map = {}
    if related_ids:
        related_tags = db.query(SysTag.tag_id, SysTag.tag_name).filter(
            SysTag.tag_id.in_(related_ids), SysTag.del_flag == '0'
        ).all()
        tag_name_map = {t[0]: t[1] for t in related_tags}

    return {"relations": [
        {
            "relation_id": r.relation_id,
            "source_tag_id": r.source_tag_id,
            "source_tag_name": tag_name_map.get(r.source_tag_id, '') if r.source_tag_id != tag_id else None,
            "target_tag_id": r.target_tag_id,
            "target_tag_name": tag_name_map.get(r.target_tag_id, '') if r.target_tag_id != tag_id else None,
            "relation_type": r.relation_type,
            "relation_meta": r.relation_meta,
            "is_bidirectional": r.is_bidirectional,
            "relation_source": r.relation_source,
            "status": r.status,
        }
        for r in relations
    ]}


@router.post("/{tag_id}/relations", response_model=TagRelationResponse)
async def create_tag_relation(tag_id: int, data: TagRelationCreate, db: Session = Depends(get_db)):
    """创建标签关系"""
    # 验证源标签和目标标签存在
    for tid in [data.source_tag_id, data.target_tag_id]:
        if not db.query(SysTag).filter(SysTag.tag_id == tid, SysTag.del_flag == '0').first():
            raise HTTPException(status_code=400, detail=f"标签 {tid} 不存在")

    now = datetime.now()
    db_rel = SysTagRelation(**data.model_dump(), create_time=now, update_time=now)
    db.add(db_rel)
    db.commit()
    db.refresh(db_rel)
    return db_rel


@router.delete("/{tag_id}/relations/{relation_id}")
async def delete_tag_relation(tag_id: int, relation_id: int, db: Session = Depends(get_db)):
    """删除标签关系（软删除）"""
    rel = db.query(SysTagRelation).filter(
        SysTagRelation.relation_id == relation_id, SysTagRelation.del_flag == '0'
    ).first()
    if not rel:
        raise HTTPException(status_code=404, detail="关系不存在")

    rel.del_flag = '2'
    rel.update_time = datetime.now()
    db.commit()
    return {"message": "删除成功"}


# ==================== 标签场景接口 ====================

@router.get("/{tag_id}/scenes")
async def get_tag_scenes_by_tag(tag_id: int, db: Session = Depends(get_db)):
    """获取标签关联的场景"""
    scenes = db.query(SysTagScene).filter(
        SysTagScene.tag_id == tag_id, SysTagScene.del_flag == '0'
    ).all()
    return {"scenes": [
        {
            "id": s.id,
            "scene_code": s.scene_code,
            "scene_name": s.scene_name,
            "relevance": s.relevance,
            "sort_order": s.sort_order,
            "status": s.status,
        }
        for s in scenes
    ]}


@router.post("/{tag_id}/scenes", response_model=TagSceneResponse)
async def create_tag_scene(tag_id: int, data: TagSceneCreate, db: Session = Depends(get_db)):
    """为标签添加场景关联"""
    if not db.query(SysTag).filter(SysTag.tag_id == tag_id, SysTag.del_flag == '0').first():
        raise HTTPException(status_code=404, detail="标签不存在")

    now = datetime.now()
    db_scene = SysTagScene(**data.model_dump(), create_time=now, update_time=now)
    db.add(db_scene)
    db.commit()
    db.refresh(db_scene)
    return db_scene


@router.delete("/{tag_id}/scenes/{scene_id}")
async def delete_tag_scene(tag_id: int, scene_id: int, db: Session = Depends(get_db)):
    """删除标签场景关联（软删除）"""
    scene = db.query(SysTagScene).filter(
        SysTagScene.id == scene_id, SysTagScene.del_flag == '0'
    ).first()
    if not scene:
        raise HTTPException(status_code=404, detail="场景关联不存在")

    scene.del_flag = '2'
    scene.update_time = datetime.now()
    db.commit()
    return {"message": "删除成功"}


# ==================== 触发规则接口 ====================

@router.get("/{tag_id}/rules")
async def get_tag_rules(tag_id: int, db: Session = Depends(get_db)):
    """获取标签的触发规则（兼容前端 RuleConfigTab 格式）"""
    tag = db.query(SysTag).filter(SysTag.tag_id == tag_id, SysTag.del_flag == '0').first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    # 优先用 tag_id 查询，兼容旧数据回退到 tag_name
    rule = db.query(SysTagTriggerRule).filter(
        SysTagTriggerRule.tag_id == tag_id,
        SysTagTriggerRule.del_flag == '0'
    ).first()
    if not rule:
        rule = db.query(SysTagTriggerRule).filter(
            SysTagTriggerRule.tag_name == tag.tag_name,
            SysTagTriggerRule.del_flag == '0'
        ).first()

    if not rule:
        return {"rules": []}

    conditions = db.query(SysTagTriggerCondition).filter(
        SysTagTriggerCondition.rule_id == rule.rule_id,
        SysTagTriggerCondition.del_flag == '0'
    ).order_by(SysTagTriggerCondition.sort_order).all()

    result_rules = []
    for idx, cond in enumerate(conditions):
        # 使用正式字段，不再从 remark 解析
        lb = cond.left_bracket or ''
        rb = cond.right_bracket or ''
        lg = cond.logic or ''

        # 兼容旧数据：如果正式字段为空但 remark 有数据，降级读取
        if not lb and not rb and not lg and cond.remark and '|' in cond.remark:
            parts = cond.remark.split('|')
            lb = parts[0] if len(parts) > 0 else ''
            rb = parts[1] if len(parts) > 1 else ''
            lg = parts[2] if len(parts) > 2 else ''

        # 如果 logic 仍为空且不是最后一条，用 rule 的全局 logic
        if not lg and idx < len(conditions) - 1:
            lg = rule.logic or 'AND'

        result_rules.append({
            "id": cond.condition_id,
            "sort_order": cond.sort_order,
            "left_bracket": lb,
            "condition": cond.target_id or cond.target_name or cond.type,
            "operator": cond.operator,
            "value": cond.value,
            "right_bracket": rb,
            "logic": lg if idx < len(conditions) - 1 else "",
        })

    return {"rules": result_rules}


@router.post("/{tag_id}/rules")
async def save_tag_rules(tag_id: int, request: TagRuleSaveRequest, db: Session = Depends(get_db)):
    """保存标签的计算规则（使用正式字段存储括号/logic，写入版本历史）"""
    tag = db.query(SysTag).filter(SysTag.tag_id == tag_id, SysTag.del_flag == '0').first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    # 优先用 tag_id 查询，兼容旧数据回退到 tag_name
    existing_rule = db.query(SysTagTriggerRule).filter(
        SysTagTriggerRule.tag_id == tag_id,
        SysTagTriggerRule.del_flag == '0'
    ).first()
    if not existing_rule:
        existing_rule = db.query(SysTagTriggerRule).filter(
            SysTagTriggerRule.tag_name == tag.tag_name,
            SysTagTriggerRule.del_flag == '0'
        ).first()

    now = datetime.now()

    # ── 快照旧版本（从正式字段读取，兼容 remark 旧数据）──
    old_snapshot = None
    if existing_rule:
        old_conditions = db.query(SysTagTriggerCondition).filter(
            SysTagTriggerCondition.rule_id == existing_rule.rule_id,
            SysTagTriggerCondition.del_flag == '0'
        ).order_by(SysTagTriggerCondition.sort_order).all()
        old_snapshot = []
        for c in old_conditions:
            lb = c.left_bracket or ''
            rb = c.right_bracket or ''
            lg = c.logic or ''
            # 兼容旧 remark 数据
            if not lb and not rb and not lg and c.remark and '|' in c.remark:
                parts = c.remark.split('|')
                lb = parts[0] if len(parts) > 0 else ''
                rb = parts[1] if len(parts) > 1 else ''
                lg = parts[2] if len(parts) > 2 else ''
            old_snapshot.append({
                "left_bracket": lb,
                "condition": c.target_id or c.type,
                "operator": c.operator,
                "value": c.value,
                "right_bracket": rb,
                "logic": lg,
            })

    # ── 确定主 logic ──
    main_logic = 'AND'
    for r in request.rules:
        if r.logic and r.logic.strip():
            main_logic = r.logic.strip().upper()
            break

    if existing_rule:
        # 软删除旧条件
        db.query(SysTagTriggerCondition).filter(
            SysTagTriggerCondition.rule_id == existing_rule.rule_id,
            SysTagTriggerCondition.del_flag == '0'
        ).update({"del_flag": "2", "update_time": now})
        rule_id = existing_rule.rule_id
        existing_rule.tag_id = tag_id  # 确保 tag_id 已填充
        existing_rule.logic = main_logic
        existing_rule.rule_type = 'single_indicator' if len(request.rules) <= 1 else 'multi_indicator'
        existing_rule.update_time = now
    else:
        new_rule = SysTagTriggerRule(
            tag_id=tag_id,
            model_id='manual',
            tag_name=tag.tag_name,
            tag_category=tag.tag_category,
            rule_type='single_indicator' if len(request.rules) <= 1 else 'multi_indicator',
            logic=main_logic,
            create_time=now,
            update_time=now,
        )
        db.add(new_rule)
        db.flush()
        rule_id = new_rule.rule_id

    # ── 插入新条件（使用正式字段，不再写 remark）──
    for idx, rule_item in enumerate(request.rules):
        db_cond = SysTagTriggerCondition(
            rule_id=rule_id,
            sort_order=idx,
            left_bracket=rule_item.left_bracket or '',
            type='field_compare',
            target_id=rule_item.condition,
            target_name=rule_item.condition,
            operator=rule_item.operator,
            value=rule_item.value,
            right_bracket=rule_item.right_bracket or '',
            logic=rule_item.logic or '',
            create_time=now,
            update_time=now,
        )
        db.add(db_cond)

    # ── 写入版本历史 ──
    new_snapshot = [
        {
            "left_bracket": r.left_bracket or "",
            "condition": r.condition,
            "operator": r.operator,
            "value": r.value,
            "right_bracket": r.right_bracket or "",
            "logic": r.logic or "",
        }
        for r in request.rules
    ]

    max_version = db.query(func.max(SysTagVersion.version)).filter(
        SysTagVersion.rule_id == rule_id
    ).scalar() or 0

    if max_version == 0 and old_snapshot:
        v1 = SysTagVersion(
            rule_id=rule_id,
            version=1,
            rule_snapshot=json.dumps(old_snapshot, ensure_ascii=False),
            change_summary="初始版本（从已有规则导入）",
            effective_date=existing_rule.create_time if existing_rule else now,
            expire_date=now,
            create_time=existing_rule.create_time if existing_rule else now,
        )
        db.add(v1)
        max_version = 1

    # 仅当规则有变更时才写入新版本
    has_change = old_snapshot is None or json.dumps(old_snapshot, ensure_ascii=False, sort_keys=True) != json.dumps(new_snapshot, ensure_ascii=False, sort_keys=True)

    if has_change:
        new_version = SysTagVersion(
            rule_id=rule_id,
            version=max_version + 1,
            rule_snapshot=json.dumps(new_snapshot, ensure_ascii=False),
            change_summary=f"规则更新：{len(request.rules)} 个条件",
            effective_date=now,
            create_time=now,
        )
        db.add(new_version)

        if max_version > 0:
            prev = db.query(SysTagVersion).filter(
                SysTagVersion.rule_id == rule_id,
                SysTagVersion.version == max_version
            ).first()
            if prev:
                prev.expire_date = now

    db.commit()

    # ── 返回更新后的规则 ──
    conditions = db.query(SysTagTriggerCondition).filter(
        SysTagTriggerCondition.rule_id == rule_id,
        SysTagTriggerCondition.del_flag == '0'
    ).order_by(SysTagTriggerCondition.sort_order).all()

    return {"rules": [
        {
            "id": c.condition_id,
            "sort_order": c.sort_order,
            "left_bracket": c.left_bracket or '',
            "condition": c.target_id or c.type,
            "operator": c.operator,
            "value": c.value,
            "right_bracket": c.right_bracket or '',
            "logic": c.logic or '',
        }
        for c in conditions
    ]}


# ==================== 版本历史接口 ====================

@router.get("/{tag_id}/versions")
async def get_tag_versions(tag_id: int, db: Session = Depends(get_db)):
    """获取标签规则的版本历史"""
    tag = db.query(SysTag).filter(SysTag.tag_id == tag_id, SysTag.del_flag == '0').first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    # 优先用 tag_id 查询
    rule = db.query(SysTagTriggerRule).filter(
        SysTagTriggerRule.tag_id == tag_id,
        SysTagTriggerRule.del_flag == '0'
    ).first()
    if not rule:
        rule = db.query(SysTagTriggerRule).filter(
            SysTagTriggerRule.tag_name == tag.tag_name,
            SysTagTriggerRule.del_flag == '0'
        ).first()

    if not rule:
        return {"versions": []}

    versions = db.query(SysTagVersion).filter(
        SysTagVersion.rule_id == rule.rule_id
    ).order_by(desc(SysTagVersion.version)).all()

    return {"versions": [
        {
            "id": v.version_id,
            "version": v.version,
            "snapshot": json.loads(v.rule_snapshot) if v.rule_snapshot else [],
            "changeSummary": v.change_summary,
            "effectiveDate": v.effective_date.isoformat() if v.effective_date else None,
            "expireDate": v.expire_date.isoformat() if v.expire_date else None,
            "createdAt": v.create_time.isoformat() if v.create_time else None,
        }
        for v in versions
    ]}


@router.post("/{tag_id}/versions/{version_id}/rollback")
async def rollback_tag_version(tag_id: int, version_id: int, db: Session = Depends(get_db)):
    """回滚到指定版本"""
    tag = db.query(SysTag).filter(SysTag.tag_id == tag_id, SysTag.del_flag == '0').first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    version = db.query(SysTagVersion).filter(SysTagVersion.version_id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="版本不存在")

    rule = db.query(SysTagTriggerRule).filter(
        SysTagTriggerRule.rule_id == version.rule_id,
        SysTagTriggerRule.del_flag == '0'
    ).first()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")

    now = datetime.now()
    snapshot = json.loads(version.rule_snapshot) if version.rule_snapshot else []

    db.query(SysTagTriggerCondition).filter(
        SysTagTriggerCondition.rule_id == rule.rule_id,
        SysTagTriggerCondition.del_flag == '0'
    ).update({"del_flag": "2", "update_time": now})

    for idx, item in enumerate(snapshot):
        db_cond = SysTagTriggerCondition(
            rule_id=rule.rule_id,
            sort_order=idx,
            left_bracket=item.get('left_bracket', ''),
            type='field_compare',
            target_id=item.get('condition', ''),
            target_name=item.get('condition', ''),
            operator=item.get('operator', '>='),
            value=item.get('value', ''),
            right_bracket=item.get('right_bracket', ''),
            logic=item.get('logic', ''),
            create_time=now,
            update_time=now,
        )
        db.add(db_cond)

    max_version = db.query(func.max(SysTagVersion.version)).filter(
        SysTagVersion.rule_id == rule.rule_id
    ).scalar() or 0

    rollback_version = SysTagVersion(
        rule_id=rule.rule_id,
        version=max_version + 1,
        rule_snapshot=version.rule_snapshot,
        change_summary=f"回滚至 v{version.version}",
        effective_date=now,
        create_time=now,
    )
    db.add(rollback_version)

    rule.update_time = now
    db.commit()

    return {"message": f"已回滚至 v{version.version}"}
