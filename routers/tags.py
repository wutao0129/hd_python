from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc, asc
from typing import Optional
import io
import csv
from database import get_db
from models import Tag, TagRecord, TagRule
from schemas.tag import TagCreate, TagUpdate, TagResponse, TagListResponse, TagStats, TagGraphNode, TagGraphRelation, TagGraphResponse, TagRuleSaveRequest, TagRuleResponse

router = APIRouter(prefix="/api/tags", tags=["标签库"])


@router.get("", response_model=TagListResponse)
async def get_tags(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    type: Optional[str] = None,
    scene: Optional[str] = None,
    keyword: Optional[str] = None,
    sort_by: str = Query('updated_at'),
    sort_order: str = Query('desc'),
    db: Session = Depends(get_db)
):
    """获取标签列表（支持分页、筛选、排序、搜索）"""
    query = db.query(Tag)

    # 筛选条件
    if category:
        query = query.filter(Tag.category == category)
    if type:
        query = query.filter(Tag.type == type)
    if scene:
        query = query.filter(Tag.scene.contains(scene))
    if keyword:
        query = query.filter(
            or_(
                Tag.name.contains(keyword),
                Tag.code.contains(keyword),
                Tag.description.contains(keyword)
            )
        )

    # 总数
    total = query.count()

    # 排序
    sort_column = getattr(Tag, sort_by, Tag.updated_at)
    if sort_order == 'desc':
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    # 分页
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    # 实时计算 usage_count：从 tag_records 表统计生效中的记录数
    tag_ids = [item.id for item in items]
    if tag_ids:
        usage_counts = dict(
            db.query(TagRecord.tag_id, func.count(TagRecord.id))
            .filter(TagRecord.tag_id.in_(tag_ids), TagRecord.status == '生效中')
            .group_by(TagRecord.tag_id)
            .all()
        )
        for item in items:
            item.usage_count = usage_counts.get(item.id, 0)

    return TagListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/stats", response_model=TagStats)
async def get_tag_stats(db: Session = Depends(get_db)):
    """获取标签统计数据"""
    total = db.query(func.count(Tag.id)).scalar()
    enabled = db.query(func.count(Tag.id)).filter(Tag.status == '启用').scalar()
    disabled = db.query(func.count(Tag.id)).filter(Tag.status == '禁用').scalar()
    avg_activity = db.query(func.avg(Tag.activity_rate)).scalar() or 0

    return TagStats(
        total=total,
        enabled=enabled,
        disabled=disabled,
        avg_activity=int(avg_activity)
    )


@router.get("/categories")
async def get_tag_categories(db: Session = Depends(get_db)):
    """获取标签分类列表"""
    categories = db.query(Tag.category).distinct().all()
    return {"categories": [c[0] for c in categories]}


@router.get("/scenes")
async def get_tag_scenes(db: Session = Depends(get_db)):
    """获取标签场景列表"""
    tags = db.query(Tag.scene).filter(Tag.scene.isnot(None)).all()
    scenes = set()
    for tag in tags:
        if tag[0]:
            scenes.update(tag[0])
    return {"scenes": sorted(list(scenes))}


@router.get("/rule-types")
async def get_tag_rule_types(db: Session = Depends(get_db)):
    """获取标签规则类型列表"""
    tags = db.query(Tag.rule_type).filter(Tag.rule_type.isnot(None)).all()
    rule_types = set()
    for tag in tags:
        if tag[0]:
            rule_types.update(tag[0])
    return {"rule_types": sorted(list(rule_types))}


@router.get("/graph", response_model=TagGraphResponse)
async def get_tag_graph(db: Session = Depends(get_db)):
    """获取标签知识图谱数据（节点和关系）"""
    # 查询所有启用的标签作为节点
    tags = db.query(Tag).filter(Tag.status == '启用').all()

    # 实时计算 usage_count
    tag_ids = [tag.id for tag in tags]
    if tag_ids:
        usage_counts = dict(
            db.query(TagRecord.tag_id, func.count(TagRecord.id))
            .filter(TagRecord.tag_id.in_(tag_ids), TagRecord.status == '生效中')
            .group_by(TagRecord.tag_id)
            .all()
        )
        for tag in tags:
            tag.usage_count = usage_counts.get(tag.id, 0)

    # 计算节点层级（基于 parent_id）
    def calculate_level(tag_id, parent_map, level_cache):
        if tag_id in level_cache:
            return level_cache[tag_id]
        if tag_id not in parent_map or parent_map[tag_id] is None:
            level_cache[tag_id] = 0
            return 0
        parent_level = calculate_level(parent_map[tag_id], parent_map, level_cache)
        level_cache[tag_id] = parent_level + 1
        return parent_level + 1

    parent_map = {tag.id: tag.parent_id for tag in tags}
    level_cache = {}

    # 构建节点列表
    nodes = []
    for tag in tags:
        level = calculate_level(tag.id, parent_map, level_cache)
        nodes.append(TagGraphNode(
            id=tag.id,
            name=tag.name,
            category=tag.category,
            usage_count=tag.usage_count,
            level=level,
            description=tag.description,
            graph_type=tag.graph_type,
            relation_name=tag.relation_name,
            parent_id=tag.parent_id
        ))

    # 构建关系列表
    relations = []
    name_to_id = {tag.name: tag.id for tag in tags}
    existing_ids = set(tag.id for tag in tags)
    virtual_id = -1

    # 0. 分类包含关系：为每个分类创建虚拟节点，分类 → 标签
    category_id_map = {}
    categories = set(tag.category for tag in tags)
    for cat in categories:
        cat_id = virtual_id
        category_id_map[cat] = cat_id
        nodes.append(TagGraphNode(
            id=cat_id, name=cat, category=cat,
            usage_count=0, level=0, graph_type='分类'
        ))
        virtual_id -= 1

    for tag in tags:
        # 没有 parent_id 的标签，挂到分类节点下
        if not tag.parent_id and tag.category in category_id_map:
            relations.append(TagGraphRelation(
                **{'from': category_id_map[tag.category], 'to': tag.id, 'type': '包含', 'strength': 0.8}
            ))

    # 0.5 场景包含关系：为每个场景创建虚拟节点，场景 → 标签
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
                    **{'from': scene_id_map[scene_name], 'to': tag.id, 'type': '包含', 'strength': 0.6}
                ))

    for tag in tags:
        # 1. 包含关系（parent_id）
        if tag.parent_id:
            relations.append(TagGraphRelation(
                **{'from': tag.parent_id, 'to': tag.id, 'type': '包含', 'strength': 1.0}
            ))

        # 2. 相似关系（similar_tags）
        if tag.similar_tags:
            for name in [n.strip() for n in tag.similar_tags.split(',') if n.strip()]:
                target_id = name_to_id.get(name)
                if target_id is None:
                    # 虚拟节点
                    target_id = virtual_id
                    name_to_id[name] = virtual_id
                    nodes.append(TagGraphNode(
                        id=virtual_id, name=name, category='未知',
                        usage_count=0, level=0
                    ))
                    virtual_id -= 1
                relations.append(TagGraphRelation(
                    **{'from': tag.id, 'to': target_id, 'type': '相似', 'strength': 0.6}
                ))

        # 3. 互斥关系（exclusive_tags）
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
                    **{'from': tag.id, 'to': target_id, 'type': '互斥', 'strength': 0.8}
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
    query = db.query(Tag)

    # 筛选条件
    if category:
        query = query.filter(Tag.category == category)
    if type:
        query = query.filter(Tag.type == type)
    if scene:
        query = query.filter(Tag.scene.contains(scene))
    if keyword:
        query = query.filter(
            or_(
                Tag.name.contains(keyword),
                Tag.code.contains(keyword),
                Tag.description.contains(keyword)
            )
        )

    tags = query.all()

    # 生成 CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # 写入表头
    writer.writerow([
        'ID', '标签名称', '标签编码', '分类', '类型', '应用场景',
        '规则类型', '规则详情', '描述', '状态', '父标签ID',
        '使用次数', '活跃度', '图谱类型', '关系名称', '创建时间', '更新时间'
    ])

    # 写入数据
    for tag in tags:
        writer.writerow([
            tag.id,
            tag.name,
            tag.code,
            tag.category,
            tag.type,
            ','.join(tag.scene) if tag.scene else '',
            ','.join(tag.rule_type) if tag.rule_type else '',
            tag.rule_detail or '',
            tag.description or '',
            tag.status,
            tag.parent_id or '',
            tag.usage_count,
            tag.activity_rate,
            tag.graph_type or '',
            tag.relation_name or '',
            tag.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            tag.updated_at.strftime('%Y-%m-%d %H:%M:%S')
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
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    # 实时计算 usage_count
    tag.usage_count = db.query(func.count(TagRecord.id)).filter(
        TagRecord.tag_id == tag_id, TagRecord.status == '生效中'
    ).scalar() or 0

    return tag


@router.post("", response_model=TagResponse)
async def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    """创建标签"""
    # 检查编码唯一性
    existing = db.query(Tag).filter(Tag.code == tag.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="标签编码已存在")

    # 检查父标签有效性
    if tag.parent_id:
        parent = db.query(Tag).filter(Tag.id == tag.parent_id).first()
        if not parent:
            raise HTTPException(status_code=400, detail="父标签不存在")

    db_tag = Tag(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(tag_id: int, tag: TagUpdate, db: Session = Depends(get_db)):
    """更新标签"""
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    # 检查编码唯一性
    if tag.code and tag.code != db_tag.code:
        existing = db.query(Tag).filter(Tag.code == tag.code).first()
        if existing:
            raise HTTPException(status_code=400, detail="标签编码已存在")

    # 检查父标签有效性
    if tag.parent_id:
        parent = db.query(Tag).filter(Tag.id == tag.parent_id).first()
        if not parent:
            raise HTTPException(status_code=400, detail="父标签不存在")

    # 更新字段
    for field, value in tag.model_dump(exclude_unset=True).items():
        setattr(db_tag, field, value)

    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.delete("/{tag_id}")
async def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """删除标签（仅自定义类型）"""
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    if db_tag.type == '内置':
        raise HTTPException(status_code=400, detail="内置标签不能删除")

    db.delete(db_tag)
    db.commit()
    return {"message": "删除成功"}


@router.patch("/{tag_id}/status", response_model=TagResponse)
async def toggle_tag_status(tag_id: int, db: Session = Depends(get_db)):
    """切换标签状态"""
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    db_tag.status = '禁用' if db_tag.status == '启用' else '启用'
    db.commit()
    db.refresh(db_tag)
    return db_tag


# ==================== 标签规则接口 ====================

@router.get("/{tag_id}/rules")
async def get_tag_rules(tag_id: int, db: Session = Depends(get_db)):
    """获取标签的计算规则列表"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    rules = db.query(TagRule).filter(TagRule.tag_id == tag_id).order_by(TagRule.sort_order).all()
    return {"rules": rules}


@router.post("/{tag_id}/rules")
async def save_tag_rules(tag_id: int, request: TagRuleSaveRequest, db: Session = Depends(get_db)):
    """保存标签的计算规则（全量替换）"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    # 删除旧规则
    db.query(TagRule).filter(TagRule.tag_id == tag_id).delete()

    # 插入新规则
    for idx, rule in enumerate(request.rules):
        db_rule = TagRule(
            tag_id=tag_id,
            sort_order=idx,
            left_bracket=rule.left_bracket,
            condition=rule.condition,
            operator=rule.operator,
            value=rule.value,
            right_bracket=rule.right_bracket,
            logic=rule.logic,
        )
        db.add(db_rule)

    db.commit()

    rules = db.query(TagRule).filter(TagRule.tag_id == tag_id).order_by(TagRule.sort_order).all()
    return {"rules": rules}
