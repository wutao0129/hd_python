from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import get_db
from models import (
    CompetencyModel, CompetencyDimension, CompetencyItem,
    RuleSet, DimensionWeightConfig, IndicatorRuleConfig, MatchResultLevel,
)
from middleware import get_current_user

router = APIRouter(prefix="/api/hr/matching", tags=["匹配引擎"])


# ---------- Schemas ----------

class CandidateData(BaseModel):
    id: str
    name: str
    scores: dict  # dimension -> indicator -> score

    class Config:
        populate_by_name = True


class MatchingRequest(BaseModel):
    modelId: str = Field(alias="modelId")
    ruleSetId: str = Field(alias="ruleSetId")
    candidates: List[CandidateData]

    class Config:
        populate_by_name = True


# ---------- Matching Algorithm ----------

def _calculate_matching(
    db: Session,
    model_id: str,
    rule_set_id: str,
    candidates: List[CandidateData],
) -> dict:
    """核心匹配计算，calculate 和 simulate 共用"""

    # 1. 校验模型和规则集
    model = db.query(CompetencyModel).filter_by(id=model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="胜任力模型不存在")

    rule_set = db.query(RuleSet).filter_by(id=rule_set_id).first()
    if not rule_set:
        raise HTTPException(status_code=404, detail="规则集不存在")

    # 2. 加载规则集配置
    dim_weights = db.query(DimensionWeightConfig).filter_by(
        rule_set_id=rule_set_id
    ).all()
    indicator_rules = db.query(IndicatorRuleConfig).filter_by(
        rule_set_id=rule_set_id
    ).all()
    result_levels = db.query(MatchResultLevel).filter_by(
        rule_set_id=rule_set_id
    ).order_by(MatchResultLevel.min_score.desc()).all()

    # 构建查找映射
    dim_weight_map = {dw.dimension: dw for dw in dim_weights}
    indicator_rule_map = {ir.indicator_name: ir for ir in indicator_rules}
    dim_indicator_map: dict = {}
    for ir in indicator_rules:
        dim_indicator_map.setdefault(ir.dimension, []).append(ir)

    # 3. 对每个候选人计算
    results = []
    for candidate in candidates:
        dimension_scores = []
        all_gaps = []
        total_weight_sum = 0.0
        total_weighted_score = 0.0

        for dw in dim_weights:
            dim_name = dw.dimension
            dim_weight = float(dw.weight)
            dim_min_pass = dw.min_pass_score

            dim_indicators = dim_indicator_map.get(dim_name, [])
            candidate_dim_scores = candidate.scores.get(dim_name, {})

            # 计算维度内加权平均分
            ind_weight_sum = 0.0
            ind_weighted_score = 0.0
            for ind_rule in dim_indicators:
                ind_name = ind_rule.indicator_name
                ind_weight = float(ind_rule.weight)
                actual_score = candidate_dim_scores.get(ind_name, 0)

                ind_weight_sum += ind_weight
                ind_weighted_score += actual_score * ind_weight

                # 技能差距分析
                target_score = dim_min_pass
                if actual_score < target_score:
                    gap = actual_score - target_score
                    abs_gap = abs(gap)
                    if abs_gap > 20:
                        priority = "高"
                    elif abs_gap > 10:
                        priority = "中"
                    else:
                        priority = "低"
                    if abs_gap > 15:
                        suggestion = f"建议系统性提升{ind_name}能力，差距较大需重点关注"
                    else:
                        suggestion = f"建议加强{ind_name}相关培训"
                    all_gaps.append({
                        "indicator": ind_name,
                        "dimension": dim_name,
                        "currentScore": actual_score,
                        "targetScore": target_score,
                        "gap": gap,
                        "priority": priority,
                        "suggestion": suggestion,
                    })

            dim_score = round(
                (ind_weighted_score / ind_weight_sum) if ind_weight_sum > 0 else 0.0, 1
            )
            passed = dim_score >= dim_min_pass

            dimension_scores.append({
                "dimension": dim_name,
                "weight": dim_weight,
                "score": dim_score,
                "passed": passed,
            })

            total_weight_sum += dim_weight
            total_weighted_score += dim_score * dim_weight

        # 总分
        total_score = round(
            (total_weighted_score / total_weight_sum) if total_weight_sum > 0 else 0.0, 1
        )

        # 匹配等级
        match_level = ""
        match_label = ""
        for rl in result_levels:
            if rl.min_score <= total_score <= rl.max_score:
                match_level = rl.level
                match_label = rl.label
                break
        if not match_level and result_levels:
            last = result_levels[-1]
            match_level = last.level
            match_label = last.label

        # 就绪度
        if total_score >= 90:
            readiness = "立即就绪"
        elif total_score >= 70:
            readiness = "1-2年可就绪"
        elif total_score >= 50:
            readiness = "需要3年+发展"
        else:
            readiness = "暂不匹配"

        results.append({
            "candidateId": candidate.id,
            "candidateName": candidate.name,
            "totalScore": total_score,
            "matchLevel": match_level,
            "matchLabel": match_label,
            "readiness": readiness,
            "dimensionScores": dimension_scores,
            "skillGaps": all_gaps,
        })

    # 按总分降序排列
    results.sort(key=lambda r: r["totalScore"], reverse=True)

    return {
        "modelId": model_id,
        "ruleSetId": rule_set_id,
        "results": results,
    }


# ---------- API Routes ----------

@router.post("/calculate")
def calculate(
    req: MatchingRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """计算候选人与胜任力模型的匹配度"""
    data = _calculate_matching(db, req.modelId, req.ruleSetId, req.candidates)
    return {"code": 200, "message": "success", "data": data}


@router.post("/simulate")
def simulate(
    req: MatchingRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """模拟匹配计算（不持久化结果）"""
    data = _calculate_matching(db, req.modelId, req.ruleSetId, req.candidates)
    return {"code": 200, "message": "success", "data": data}
