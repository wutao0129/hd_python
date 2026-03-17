from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc, asc
from typing import Optional
from datetime import datetime

from database import get_db
from models import TalentTag, TalentTagLog, SysTag, SysEmp
from schemas.tag_record import (
    TalentTagCreate,
    TalentTagUpdate,
    TalentTagResponse,
    TalentTagListResponse,
    TalentTagStats
)

router = APIRouter(prefix="/api/tag-records", tags=["标签记录"])


@router.get("", response_model=TalentTagListResponse)
async def get_tag_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    emp_id: Optional[int] = None,
    emp_name: Optional[str] = None,
    tag_id: Optional[int] = None,
    tag_category: Optional[str] = None,
    tag_source: Optional[str] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    sort_by: str = Query('create_time'),
    sort_order: str = Query('desc'),
    db: Session = Depends(get_db)
):
    """获取标签记录列表（talent_tag JOIN sys_emp + sys_tag）"""
    query = db.query(
        TalentTag,
        SysEmp.emp_name,
        SysEmp.emp_code,
        SysEmp.dept_name,
        SysEmp.post_name,
        SysTag.tag_name,
        SysTag.tag_code,
        SysTag.tag_category,
    ).outerjoin(
        SysEmp, TalentTag.emp_id == SysEmp.emp_id
    ).outerjoin(
        SysTag, TalentTag.tag_id == SysTag.tag_id
    ).filter(
        TalentTag.del_flag == '0'
    )

    if emp_id:
        query = query.filter(TalentTag.emp_id == emp_id)
    if emp_name:
        query = query.filter(SysEmp.emp_name.contains(emp_name))
    if tag_id:
        query = query.filter(TalentTag.tag_id == tag_id)
    if tag_category:
        query = query.filter(SysTag.tag_category == tag_category)
    if tag_source:
        query = query.filter(TalentTag.tag_source == tag_source)
    if status:
        query = query.filter(TalentTag.status == status)
    if keyword:
        query = query.filter(
            or_(
                SysEmp.emp_name.contains(keyword),
                SysEmp.emp_code.contains(keyword),
                SysTag.tag_name.contains(keyword)
            )
        )

    total = query.count()

    # 排序
    sort_field_map = {
        'create_time': TalentTag.create_time,
        'emp_name': SysEmp.emp_name,
        'status': TalentTag.status,
        'tag_category': SysTag.tag_category,
        'tag_source': TalentTag.tag_source,
    }
    sort_column = sort_field_map.get(sort_by, TalentTag.create_time)
    if sort_order == 'desc':
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    offset = (page - 1) * page_size
    rows = query.offset(offset).limit(page_size).all()

    items = []
    for row in rows:
        tt = row[0]  # TalentTag object
        items.append(TalentTagResponse(
            talent_tag_id=tt.talent_tag_id,
            emp_id=tt.emp_id,
            tag_id=tt.tag_id,
            tag_source=tt.tag_source,
            score=float(tt.score) if tt.score is not None else None,
            expire_time=tt.expire_time,
            status=tt.status,
            create_time=tt.create_time,
            update_time=tt.update_time,
            emp_name=row[1],
            emp_code=row[2],
            dept_name=row[3],
            post_name=row[4],
            tag_name=row[5],
            tag_code=row[6],
            tag_category=row[7],
        ))

    return TalentTagListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/stats", response_model=TalentTagStats)
async def get_tag_record_stats(db: Session = Depends(get_db)):
    """获取标签记录统计数据"""
    base = db.query(TalentTag).filter(TalentTag.del_flag == '0')
    total = base.count()
    active = base.filter(TalentTag.status == '1').count()
    expired = base.filter(TalentTag.status == '2').count()
    removed = db.query(TalentTag).filter(TalentTag.del_flag == '2').count()
    unique_employees = base.filter(TalentTag.status == '1').with_entities(
        func.count(func.distinct(TalentTag.emp_id))
    ).scalar()

    return TalentTagStats(
        total=total,
        active=active,
        expired=expired,
        removed=removed,
        unique_employees=unique_employees or 0
    )


@router.get("/{record_id}", response_model=TalentTagResponse)
async def get_tag_record(record_id: int, db: Session = Depends(get_db)):
    """获取标签记录详情"""
    row = db.query(
        TalentTag,
        SysEmp.emp_name,
        SysEmp.emp_code,
        SysEmp.dept_name,
        SysEmp.post_name,
        SysTag.tag_name,
        SysTag.tag_code,
        SysTag.tag_category,
    ).outerjoin(
        SysEmp, TalentTag.emp_id == SysEmp.emp_id
    ).outerjoin(
        SysTag, TalentTag.tag_id == SysTag.tag_id
    ).filter(
        TalentTag.talent_tag_id == record_id,
        TalentTag.del_flag == '0'
    ).first()

    if not row:
        raise HTTPException(status_code=404, detail="标签记录不存在")

    tt = row[0]
    return TalentTagResponse(
        talent_tag_id=tt.talent_tag_id,
        emp_id=tt.emp_id,
        tag_id=tt.tag_id,
        tag_source=tt.tag_source,
        score=float(tt.score) if tt.score is not None else None,
        expire_time=tt.expire_time,
        status=tt.status,
        create_time=tt.create_time,
        update_time=tt.update_time,
        emp_name=row[1],
        emp_code=row[2],
        dept_name=row[3],
        post_name=row[4],
        tag_name=row[5],
        tag_code=row[6],
        tag_category=row[7],
    )


@router.post("", response_model=TalentTagResponse)
async def create_tag_record(record: TalentTagCreate, db: Session = Depends(get_db)):
    """创建标签记录"""
    tag = db.query(SysTag).filter(SysTag.tag_id == record.tag_id, SysTag.del_flag == '0').first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    emp = db.query(SysEmp).filter(SysEmp.emp_id == record.emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="员工不存在")

    # 检查是否已存在
    existing = db.query(TalentTag).filter(
        TalentTag.emp_id == record.emp_id,
        TalentTag.tag_id == record.tag_id,
        TalentTag.del_flag == '0'
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该员工已有此标签")

    now = datetime.now()
    db_record = TalentTag(
        **record.model_dump(),
        status='1',
        create_time=now,
        update_time=now,
    )
    db.add(db_record)
    db.flush()

    # 写入操作日志
    log = TalentTagLog(
        emp_id=record.emp_id,
        tag_id=record.tag_id,
        action='add',
        action_source=record.tag_source,
        action_reason=record.remark,
        create_time=now,
        update_time=now,
    )
    db.add(log)
    db.commit()
    db.refresh(db_record)

    return TalentTagResponse(
        talent_tag_id=db_record.talent_tag_id,
        emp_id=db_record.emp_id,
        tag_id=db_record.tag_id,
        tag_source=db_record.tag_source,
        score=float(db_record.score) if db_record.score is not None else None,
        expire_time=db_record.expire_time,
        status=db_record.status,
        create_time=db_record.create_time,
        update_time=db_record.update_time,
        emp_name=emp.emp_name,
        emp_code=emp.emp_code,
        dept_name=emp.dept_name,
        post_name=emp.post_name,
        tag_name=tag.tag_name,
        tag_code=tag.tag_code,
        tag_category=tag.tag_category,
    )


@router.put("/{record_id}", response_model=TalentTagResponse)
async def update_tag_record(
    record_id: int,
    record: TalentTagUpdate,
    db: Session = Depends(get_db)
):
    """更新标签记录"""
    db_record = db.query(TalentTag).filter(
        TalentTag.talent_tag_id == record_id,
        TalentTag.del_flag == '0'
    ).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="标签记录不存在")

    for field, value in record.model_dump(exclude_unset=True).items():
        setattr(db_record, field, value)

    db_record.update_time = datetime.now()
    db.commit()
    db.refresh(db_record)

    # 重新查询带 JOIN 的完整数据
    return await get_tag_record(record_id, db)


@router.delete("/{record_id}")
async def delete_tag_record(
    record_id: int,
    remove_reason: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """移除标签（软删除）"""
    db_record = db.query(TalentTag).filter(
        TalentTag.talent_tag_id == record_id,
        TalentTag.del_flag == '0'
    ).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="标签记录不存在")

    now = datetime.now()
    db_record.del_flag = '2'
    db_record.update_time = now

    # 写入操作日志
    log = TalentTagLog(
        emp_id=db_record.emp_id,
        tag_id=db_record.tag_id,
        action='remove',
        action_source='manual',
        action_reason=remove_reason,
        create_time=now,
        update_time=now,
    )
    db.add(log)
    db.commit()

    return {"message": "标签已移除"}
