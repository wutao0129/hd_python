import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session
from database import get_db
from models import RuleSet, DimensionWeightConfig, IndicatorRuleConfig, MatchResultLevel
from middleware import get_current_user

router = APIRouter(prefix="/api/hr/rule-set", tags=["规则集"])


# ---------- Schemas ----------

class DimensionWeightSchema(BaseModel):
    dimension: str
    dimensionLabel: str
    weight: float
    minPassScore: int = 60
    scoringScheme: Optional[str] = None
    isRequired: bool = False

    class Config:
        populate_by_name = True


class IndicatorRuleSchema(BaseModel):
    indicatorId: Optional[int] = None
    indicatorName: str
    dimension: str
    weight: float
    matchFormula: str = "level_match"
    thresholdLevel: str = "L3"
    minAcceptLevel: str = "L1"
    deviationPenalty: float = 5.0
    isKeyIndicator: bool = False

    class Config:
        populate_by_name = True


class MatchResultLevelSchema(BaseModel):
    level: str
    label: str
    minScore: int
    maxScore: int
    color: str
    description: Optional[str] = None

    class Config:
        populate_by_name = True


class RuleSetCreate(BaseModel):
    name: str
    scenarios: list
    status: str = "draft"
    scoreFormula: str = "weighted_average"
    passScore: int = 60
    effectiveType: Optional[str] = None
    effectiveDate: Optional[str] = None
    version: str = "V1.0"
    remark: Optional[str] = None
    dimensionWeights: List[DimensionWeightSchema] = []
    indicatorRules: List[IndicatorRuleSchema] = []
    resultLevels: List[MatchResultLevelSchema] = []

    class Config:
        populate_by_name = True


# ---------- Helper Functions ----------

def _to_dict(obj: RuleSet) -> dict:
    return {
        "id": obj.id,
        "name": obj.name,
        "scenarios": obj.scenarios,
        "status": obj.status,
        "scoreFormula": obj.score_formula,
        "passScore": obj.pass_score,
        "effectiveType": obj.effective_type,
        "effectiveDate": obj.effective_date.isoformat() if obj.effective_date else None,
        "version": obj.version,
        "remark": obj.remark,
        "createdBy": obj.created_by,
        "createdAt": obj.created_at.isoformat() if obj.created_at else None,
        "updatedAt": obj.updated_at.isoformat() if obj.updated_at else None,
    }


def _get_or_404(db: Session, rule_set_id: str) -> RuleSet:
    obj = db.query(RuleSet).filter_by(id=rule_set_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="规则集不存在")
    return obj


def _build_detail(db: Session, obj: RuleSet) -> dict:
    data = _to_dict(obj)

    weights = db.query(DimensionWeightConfig).filter_by(rule_set_id=obj.id).all()
    data["dimensionWeights"] = [{
        "id": w.id,
        "dimension": w.dimension,
        "dimensionLabel": w.dimension_label,
        "weight": float(w.weight),
        "minPassScore": w.min_pass_score,
        "scoringScheme": w.scoring_scheme,
        "isRequired": w.is_required,
    } for w in weights]

    rules = db.query(IndicatorRuleConfig).filter_by(rule_set_id=obj.id).all()
    data["indicatorRules"] = [{
        "id": r.id,
        "indicatorId": r.indicator_id,
        "indicatorName": r.indicator_name,
        "dimension": r.dimension,
        "weight": float(r.weight),
        "matchFormula": r.match_formula,
        "thresholdLevel": r.threshold_level,
        "minAcceptLevel": r.min_accept_level,
        "deviationPenalty": float(r.deviation_penalty),
        "isKeyIndicator": r.is_key_indicator,
    } for r in rules]

    levels = db.query(MatchResultLevel).filter_by(
        rule_set_id=obj.id
    ).order_by(MatchResultLevel.min_score).all()
    data["resultLevels"] = [{
        "id": lv.id,
        "level": lv.level,
        "label": lv.label,
        "minScore": lv.min_score,
        "maxScore": lv.max_score,
        "color": lv.color,
        "description": lv.description,
    } for lv in levels]

    return data


def _save_related(db: Session, rule_set_id: str, data: RuleSetCreate):
    for w in data.dimensionWeights:
        db.add(DimensionWeightConfig(
            rule_set_id=rule_set_id, dimension=w.dimension,
            dimension_label=w.dimensionLabel, weight=w.weight,
            min_pass_score=w.minPassScore, scoring_scheme=w.scoringScheme,
            is_required=w.isRequired,
        ))
    for r in data.indicatorRules:
        db.add(IndicatorRuleConfig(
            rule_set_id=rule_set_id, indicator_id=r.indicatorId,
            indicator_name=r.indicatorName, dimension=r.dimension,
            weight=r.weight, match_formula=r.matchFormula,
            threshold_level=r.thresholdLevel, min_accept_level=r.minAcceptLevel,
            deviation_penalty=r.deviationPenalty, is_key_indicator=r.isKeyIndicator,
        ))
    for lv in data.resultLevels:
        db.add(MatchResultLevel(
            rule_set_id=rule_set_id, level=lv.level, label=lv.label,
            min_score=lv.minScore, max_score=lv.maxScore,
            color=lv.color, description=lv.description,
        ))


def _delete_related(db: Session, rule_set_id: str):
    db.query(DimensionWeightConfig).filter_by(rule_set_id=rule_set_id).delete()
    db.query(IndicatorRuleConfig).filter_by(rule_set_id=rule_set_id).delete()
    db.query(MatchResultLevel).filter_by(rule_set_id=rule_set_id).delete()


# ---------- API Routes ----------

@router.get("")
def get_list(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """规则集列表"""
    query = db.query(RuleSet)
    if status:
        query = query.filter(RuleSet.status == status)
    if keyword:
        query = query.filter(RuleSet.name.like(f"%{keyword}%"))

    total = query.count()
    items = query.order_by(RuleSet.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return {
        "code": 200, "message": "success",
        "data": {
            "total": total, "page": page, "pageSize": page_size,
            "items": [_to_dict(r) for r in items],
        },
    }


@router.get("/{rule_set_id}")
def get_detail(
    rule_set_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """规则集详情"""
    obj = _get_or_404(db, rule_set_id)
    return {"code": 200, "message": "success", "data": _build_detail(db, obj)}


@router.post("")
def create(
    data: RuleSetCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """创建规则集"""
    rule_set_id = str(uuid.uuid4())
    obj = RuleSet(
        id=rule_set_id, name=data.name, scenarios=data.scenarios,
        status=data.status, score_formula=data.scoreFormula,
        pass_score=data.passScore, effective_type=data.effectiveType,
        version=data.version, remark=data.remark,
        created_by=str(current_user.get("id") or ""),
    )
    if data.effectiveDate:
        from datetime import date as date_type
        obj.effective_date = date_type.fromisoformat(data.effectiveDate)
    db.add(obj)
    db.flush()
    _save_related(db, rule_set_id, data)
    db.commit()
    db.refresh(obj)
    return {"code": 200, "message": "创建成功", "data": _build_detail(db, obj)}


@router.put("/{rule_set_id}")
def update(
    rule_set_id: str,
    data: RuleSetCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """更新规则集"""
    obj = _get_or_404(db, rule_set_id)
    obj.name = data.name
    obj.scenarios = data.scenarios
    obj.status = data.status
    obj.score_formula = data.scoreFormula
    obj.pass_score = data.passScore
    obj.effective_type = data.effectiveType
    obj.version = data.version
    obj.remark = data.remark
    if data.effectiveDate:
        from datetime import date as date_type
        obj.effective_date = date_type.fromisoformat(data.effectiveDate)

    _delete_related(db, rule_set_id)
    db.flush()
    _save_related(db, rule_set_id, data)
    db.commit()
    db.refresh(obj)
    return {"code": 200, "message": "更新成功", "data": _build_detail(db, obj)}


@router.delete("/{rule_set_id}")
def delete(
    rule_set_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """删除规则集"""
    obj = _get_or_404(db, rule_set_id)
    _delete_related(db, rule_set_id)
    db.delete(obj)
    db.commit()
    return {"code": 200, "message": "删除成功"}