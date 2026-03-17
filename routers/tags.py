from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc, asc
from typing import Optional
from datetime import datetime
import io
import csv
from database import get_db
from models import SysTag, TalentTag, SysTagTriggerRule, SysTagTriggerCondition, SysTagTriggerAction
from schemas.tag import (
    TagCreate, TagUpdate, TagResponse, TagListResponse, TagStats,
    TagGraphNode, TagGraphRelation, TagGraphResponse,
    TagRuleSaveRequest, TagRuleResponse,
    TriggerRuleResponse, TriggerRuleSaveRequest, TriggerConditionItem, TriggerActionItem,
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
        query = query.filter(SysTag.scene.contains(scene))
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
    """获取标签场景列表"""
    tags = db.query(SysTag.scene).filter(SysTag.del_flag == '0', SysTag.scene.isnot(None)).all()
    scenes = set()
    for tag in tags:
        if tag[0]:
            scenes.update(tag[0])
    return {"scenes": sorted(list(scenes))}


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
    """获取标签知识图谱数据"""
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
            graph_type=tag.graph_type,
            relation_name=tag.relation_name,
            parent_id=tag.parent_id
        ))

    relations = []
    name_to_id = {tag.tag_name: tag.tag_id for tag in tags}
    virtual_id = -1

    # 分类包含关系
    category_id_map = {}
    categories = set(tag.tag_category for tag in tags)
    for cat in categories:
        cat_id = virtual_id
        category_id_map[cat] = cat_id
        nodes.append(TagGraphNode(
            id=cat_id, name=cat, category=cat,
            usage_count=0, level=0, graph_type='分类'
        ))
        virtual_id -= 1

    for tag in tags:
        if not tag.parent_id and tag.tag_category in category_id_map:
            relations.append(TagGraphRelation(
                **{'from': category_id_map[tag.tag_category], 'to': tag.tag_id, 'type': '包含', 'strength': 0.8}
            ))

    # 场景包含关系
    scene_id_map = {}
    for tag in tags:
        if tag.scene:
            scenes = tag.scene if isinstance(tag.scene, list) else []
            for scene_name in scenes:
                if scene_name not in scene_id_map:
                    scene_id_map[scene_name] = virtual_id
                    nodes.append(TagGraphNode(
                        id=virtual_id, name=scene_name, category='场景',
                        usage_count=0, level=0, graph_type='场景'
                    ))
                    virtual_id -= 1
                relations.append(TagGraphRelation(
                    **{'from': scene_id_map[scene_name], 'to': tag.tag_id, 'type': '包含', 'strength': 0.6}
                ))

    for tag in tags:
        # 包含关系（parent_id）
        if tag.parent_id:
            relations.append(TagGraphRelation(
                **{'from': tag.parent_id, 'to': tag.tag_id, 'type': '包含', 'strength': 1.0}
            ))

        # 相似关系
        if tag.similar_tags:
            for name in [n.strip() for n in tag.similar_tags.split(',') if n.strip()]:
                target_id = name_to_id.get(name)
                if target_id is None:
                    target_id = virtual_id
                    name_to_id[name] = virtual_id
                    nodes.append(TagGraphNode(
                        id=virtual_id, name=name, category='未知',
                        usage_count=0, level=0
                    ))
                    virtual_id -= 1
                relations.append(TagGraphRelation(
                    **{'from': tag.tag_id, 'to': target_id, 'type': '相似', 'strength': 0.6}
                ))

        # 互斥关系
        if tag.exclusive_tags:
            for name in [n.strip() for n in tag.exclusive_tags.split(',') if n.strip()]:
                target_id = name_to_id.get(name)
                if target_id is None:
                    target_id = virtual_id
                    name_to_id[name] = virtual_id
                    nodes.append(TagGraphNode(
                        id=virtual_id, name=name, category='未知',
                        usage_count=0, level=0
                    ))
                    virtual_id -= 1
                relations.append(TagGraphRelation(
                    **{'from': tag.tag_id, 'to': target_id, 'type': '互斥', 'strength': 0.8}
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
        query = query.filter(SysTag.scene.contains(scene))
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
        '使用次数', '活跃度', '图谱类型', '关系名称', '创建时间', '更新时间'
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
            tag.graph_type or '',
            tag.relation_name or '',
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


# ==================== 触发规则接口 ====================

@router.get("/{tag_id}/rules")
async def get_tag_rules(tag_id: int, db: Session = Depends(get_db)):
    """获取标签的触发规则（兼容前端 RuleConfigTab 格式）"""
    tag = db.query(SysTag).filter(SysTag.tag_id == tag_id, SysTag.del_flag == '0').first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    # 查找以该标签名称关联的触发规则
    rules = db.query(SysTagTriggerRule).filter(
        SysTagTriggerRule.tag_name == tag.tag_name,
        SysTagTriggerRule.del_flag == '0'
    ).all()

    if not rules:
        return {"rules": []}

    # 将触发条件转换为前端 RuleConfigTab 兼容格式
    result_rules = []
    for rule in rules:
        conditions = db.query(SysTagTriggerCondition).filter(
            SysTagTriggerCondition.rule_id == rule.rule_id,
            SysTagTriggerCondition.del_flag == '0'
        ).all()

        for idx, cond in enumerate(conditions):
            result_rules.append({
                "id": cond.condition_id,
                "sort_order": idx,
                "left_bracket": "",
                "condition": cond.target_id or cond.target_name or cond.type,
                "operator": cond.operator,
                "value": cond.value,
                "right_bracket": "",
                "logic": rule.logic if idx < len(conditions) - 1 else "",
            })

    return {"rules": result_rules}


@router.post("/{tag_id}/rules")
async def save_tag_rules(tag_id: int, request: TagRuleSaveRequest, db: Session = Depends(get_db)):
    """保存标签的计算规则（兼容前端格式，写入触发规则三张表）"""
    tag = db.query(SysTag).filter(SysTag.tag_id == tag_id, SysTag.del_flag == '0').first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    # 查找或创建触发规则
    existing_rule = db.query(SysTagTriggerRule).filter(
        SysTagTriggerRule.tag_name == tag.tag_name,
        SysTagTriggerRule.del_flag == '0'
    ).first()

    now = datetime.now()

    if existing_rule:
        # 删除旧条件
        db.query(SysTagTriggerCondition).filter(
            SysTagTriggerCondition.rule_id == existing_rule.rule_id
        ).update({"del_flag": "2"})
        rule_id = existing_rule.rule_id
        # 从规则中提取 logic
        logic = request.rules[0].logic if request.rules else 'AND'
        existing_rule.logic = logic or 'AND'
        existing_rule.update_time = now
    else:
        logic = request.rules[0].logic if request.rules else 'AND'
        new_rule = SysTagTriggerRule(
            model_id='manual',
            tag_name=tag.tag_name,
            tag_category=tag.tag_category,
            rule_type='single_indicator' if len(request.rules) <= 1 else 'multi_indicator',
            logic=logic or 'AND',
            create_time=now,
            update_time=now,
        )
        db.add(new_rule)
        db.flush()
        rule_id = new_rule.rule_id

    # 插入新条件
    for rule_item in request.rules:
        db_cond = SysTagTriggerCondition(
            rule_id=rule_id,
            type='field_compare',
            target_id=rule_item.condition,
            target_name=rule_item.condition,
            operator=rule_item.operator,
            value=rule_item.value,
            create_time=now,
            update_time=now,
        )
        db.add(db_cond)

    db.commit()

    # 返回更新后的规则
    conditions = db.query(SysTagTriggerCondition).filter(
        SysTagTriggerCondition.rule_id == rule_id,
        SysTagTriggerCondition.del_flag == '0'
    ).all()

    return {"rules": [
        {
            "id": c.condition_id,
            "sort_order": idx,
            "left_bracket": "",
            "condition": c.target_id or c.type,
            "operator": c.operator,
            "value": c.value,
            "right_bracket": "",
            "logic": logic if idx < len(conditions) - 1 else "",
        }
        for idx, c in enumerate(conditions)
    ]}
