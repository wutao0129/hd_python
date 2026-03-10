from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc, asc
from typing import Optional
from datetime import datetime

from database import get_db
from models import TagRecord, Tag
from schemas.tag_record import (
    TagRecordCreate,
    TagRecordUpdate,
    TagRecordResponse,
    TagRecordListResponse,
    TagRecordStats
)

router = APIRouter(prefix="/api/tag-records", tags=["标签记录"])


@router.get("", response_model=TagRecordListResponse)
async def get_tag_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    employee_id: Optional[str] = None,
    employee_name: Optional[str] = None,
    tag_id: Optional[int] = None,
    tag_category: Optional[str] = None,
    source: Optional[str] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    sort_by: str = Query('tagged_at'),
    sort_order: str = Query('desc'),
    db: Session = Depends(get_db)
):
    """获取标签记录列表（支持分页、筛选、搜索）"""
    query = db.query(TagRecord)

    if employee_id:
        query = query.filter(TagRecord.employee_id == employee_id)
    if employee_name:
        query = query.filter(TagRecord.employee_name.contains(employee_name))
    if tag_id:
        query = query.filter(TagRecord.tag_id == tag_id)
    if tag_category:
        query = query.filter(TagRecord.tag_category == tag_category)
    if source:
        query = query.filter(TagRecord.source == source)
    if status:
        query = query.filter(TagRecord.status == status)
    if keyword:
        query = query.filter(
            or_(
                TagRecord.employee_name.contains(keyword),
                TagRecord.employee_id.contains(keyword),
                TagRecord.tag_name.contains(keyword)
            )
        )

    total = query.count()

    allowed_sort = {'tagged_at', 'employee_name', 'created_at', 'status', 'tag_category', 'source'}
    sort_column = getattr(TagRecord, sort_by if sort_by in allowed_sort else 'tagged_at')
    if sort_order == 'desc':
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    return TagRecordListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/stats", response_model=TagRecordStats)
async def get_tag_record_stats(db: Session = Depends(get_db)):
    """获取标签记录统计数据"""
    total = db.query(func.count(TagRecord.id)).scalar()
    active = db.query(func.count(TagRecord.id)).filter(TagRecord.status == '生效中').scalar()
    expired = db.query(func.count(TagRecord.id)).filter(TagRecord.status == '已过期').scalar()
    removed = db.query(func.count(TagRecord.id)).filter(TagRecord.status == '已移除').scalar()
    unique_employees = db.query(func.count(func.distinct(TagRecord.employee_id))).filter(
        TagRecord.status == '生效中'
    ).scalar()

    return TagRecordStats(
        total=total,
        active=active,
        expired=expired,
        removed=removed,
        unique_employees=unique_employees
    )


@router.get("/{record_id}", response_model=TagRecordResponse)
async def get_tag_record(record_id: int, db: Session = Depends(get_db)):
    """获取标签记录详情"""
    record = db.query(TagRecord).filter(TagRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="标签记录不存在")
    return record


@router.post("", response_model=TagRecordResponse)
async def create_tag_record(record: TagRecordCreate, db: Session = Depends(get_db)):
    """创建标签记录"""
    tag = db.query(Tag).filter(Tag.id == record.tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    db_record = TagRecord(
        **record.model_dump(),
        tag_name=tag.name,
        tag_code=tag.code,
        tag_category=tag.category,
        tagged_at=datetime.now(),
        status='生效中'
    )

    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return db_record


@router.put("/{record_id}", response_model=TagRecordResponse)
async def update_tag_record(
    record_id: int,
    record: TagRecordUpdate,
    db: Session = Depends(get_db)
):
    """更新标签记录"""
    db_record = db.query(TagRecord).filter(TagRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="标签记录不存在")

    for field, value in record.model_dump(exclude_unset=True).items():
        setattr(db_record, field, value)

    db.commit()
    db.refresh(db_record)
    return db_record


@router.delete("/{record_id}")
async def delete_tag_record(
    record_id: int,
    remove_reason: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """移除标签（软删除）"""
    db_record = db.query(TagRecord).filter(TagRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="标签记录不存在")

    db_record.status = '已移除'
    db_record.removed_at = datetime.now()
    db_record.removed_by = 'system'
    db_record.remove_reason = remove_reason

    db.commit()
    return {"message": "标签已移除"}
