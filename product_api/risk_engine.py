from typing import Dict, List, Any
from datetime import datetime

# 默认权重配置
DEFAULT_WEIGHTS = {
    "compliance_rate": 0.35,
    "alert_volume": 0.25,
    "trend_score": 0.15,
    "system_health": 0.15,
    "external_risk": 0.10
}

def normalize(val: float, min_val: float, max_val: float) -> float:
    if max_val - min_val == 0:
        return 0
    return max(0.0, min(1.0, (val - min_val) / (max_val - min_val)))

def calc_risk_score(metrics: Dict[str, float], weights: Dict[str, float] = DEFAULT_WEIGHTS) -> float:
    score = 0.0
    # compliance_rate: higher is better? Usually yes. 
    # But risk score: higher usually means higher risk OR higher safety?
    # In dashboard.py, risk_score seems to be "compliance score" (92 is good).
    # Let's assume this calculates a "Safety Score" (0-100).
    # User provided code:
    # score += normalize(metrics.get("compliance_rate", 0), 0, 1) * weights["compliance_rate"]
    # ...
    # return round(score * 100, 2)
    
    score += normalize(metrics.get("compliance_rate", 0), 0, 1) * weights["compliance_rate"]
    # alert_volume: usually lower is better. 
    # But user code: normalize(..., 0, 500). If alert_volume is 500, it contributes MAX to score.
    # If "score" is "Risk Score" (high = bad), then high alert volume -> high score. Correct.
    # But compliance_rate: if high (1.0) -> high score. 
    # This seems contradictory if it is Risk Score. 
    # If it is Safety Score: High compliance -> High score. High alert -> High score (Bad?).
    # Let's just follow the user's logic verbatim.
    
    score += normalize(metrics.get("alert_volume", 0), 0, 500) * weights["alert_volume"]
    score += normalize(metrics.get("trend_score", 0), -1, 1) * weights["trend_score"]
    score += normalize(metrics.get("system_health", 0), 0, 1) * weights["system_health"]
    score += normalize(metrics.get("external_risk", 0), 0, 1) * weights["external_risk"]
    return round(score * 100, 2)

def generate_mock_metrics() -> Dict[str, float]:
    return {
        "compliance_rate": 0.22,
        "alert_volume": 28,
        "trend_score": 0.2,
        "system_health": 0.85,
        "external_risk": 0.15
    }

def get_risk_overview() -> Dict[str, Any]:
    metrics = generate_mock_metrics()
    total_score = calc_risk_score(metrics)
    detail_list = [
        {"name": "合规违规率", "score": round(normalize(metrics["compliance_rate"], 0, 1) * 100, 2)},
        {"name": "告警数量", "score": round(normalize(metrics["alert_volume"], 0, 500) * 100, 2)},
        {"name": "趋势变动", "score": round(normalize(metrics["trend_score"], -1, 1) * 100, 2)},
        {"name": "系统健康", "score": round(normalize(metrics["system_health"], 0, 1) * 100, 2)},
        {"name": "外部风险", "score": round(normalize(metrics["external_risk"], 0, 1) * 100, 2)}
    ]
    return {
        "total_risk_score": total_score,
        "details": detail_list,
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }
