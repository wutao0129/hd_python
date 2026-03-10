from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session
from database import get_db
from models import RecruitmentQuestionBank
from middleware import get_current_user

router = APIRouter(prefix="/api/recruitment-question-bank", tags=["招聘管理-题库"])


# ---------- Schemas ----------

class QuestionCreate(BaseModel):
    category: str
    question: str
    answer: Optional[str] = None
    difficulty: str
    tags: Optional[str] = None

    class Config:
        populate_by_name = True


class QuestionUpdate(BaseModel):
    category: Optional[str] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    difficulty: Optional[str] = None
    tags: Optional[str] = None

    class Config:
        populate_by_name = True


# ---------- Helper Functions ----------

def _to_dict(obj: RecruitmentQuestionBank) -> dict:
    """转换模型为字典"""
    return {
        "id": obj.id,
        "category": obj.category,
        "question": obj.question,
        "answer": obj.answer,
        "difficulty": obj.difficulty,
        "tags": obj.tags,
        "createdAt": obj.created_at.isoformat(),
        "updatedAt": obj.updated_at.isoformat(),
    }


def _get_or_404(db: Session, question_id: int) -> RecruitmentQuestionBank:
    """获取题目或返回404"""
    obj = db.query(RecruitmentQuestionBank).filter_by(id=question_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="题目不存在")
    return obj


# ---------- API Routes ----------

@router.get("/list")
def get_list(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """列表查询（支持分页、筛选、排序）"""
    query = db.query(RecruitmentQuestionBank)

    # 分类筛选
    if category:
        query = query.filter_by(category=category)

    # 难度筛选
    if difficulty:
        query = query.filter_by(difficulty=difficulty)

    # 关键词搜索
    if keyword:
        query = query.filter(
            or_(
                RecruitmentQuestionBank.question.like(f"%{keyword}%"),
                RecruitmentQuestionBank.answer.like(f"%{keyword}%"),
                RecruitmentQuestionBank.tags.like(f"%{keyword}%")
            )
        )

    # 分页
    total = query.count()
    items = query.order_by(RecruitmentQuestionBank.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "code": 200,
        "message": "success",
        "data": {
            "total": total,
            "page": page,
            "pageSize": page_size,
            "items": [_to_dict(item) for item in items]
        }
    }


@router.get("/{question_id}")
def get_detail(question_id: int, db: Session = Depends(get_db)):
    """详情查询"""
    obj = _get_or_404(db, question_id)
    return {"code": 200, "message": "success", "data": _to_dict(obj)}


@router.post("")
def create(
    data: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建题目"""
    obj = RecruitmentQuestionBank(
        category=data.category,
        question=data.question,
        answer=data.answer,
        difficulty=data.difficulty,
        tags=data.tags,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"code": 200, "message": "创建成功", "data": _to_dict(obj)}


@router.put("/{question_id}")
def update(
    question_id: int,
    data: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新题目"""
    obj = _get_or_404(db, question_id)

    # 更新字段
    if data.category is not None:
        obj.category = data.category
    if data.question is not None:
        obj.question = data.question
    if data.answer is not None:
        obj.answer = data.answer
    if data.difficulty is not None:
        obj.difficulty = data.difficulty
    if data.tags is not None:
        obj.tags = data.tags

    obj.updated_at = datetime.now()
    db.commit()
    db.refresh(obj)
    return {"code": 200, "message": "更新成功", "data": _to_dict(obj)}


@router.delete("/{question_id}")
def delete(question_id: int, db: Session = Depends(get_db)):
    """删除题目"""
    obj = _get_or_404(db, question_id)
    db.delete(obj)
    db.commit()
    return {"code": 200, "message": "删除成功"}
