from fastapi import APIRouter
from typing import Optional
from datetime import datetime, timedelta
import random

from .models import RiskOverviewResponse, RiskTrendResponse
from .risk_engine import get_risk_overview, calc_risk_score, generate_mock_metrics

router = APIRouter(prefix="/api/v1/risk", tags=["Risk"])

@router.get("/overview", response_model=RiskOverviewResponse)
def risk_overview():
    return get_risk_overview()

@router.get("/trend", response_model=RiskTrendResponse)
def risk_trend(days: Optional[int] = 7):
    now = datetime.utcnow()
    trend_list = []
    for i in range(days):
        d = now - timedelta(days=(days - 1 - i))
        # Use mock metrics but vary slightly to show trend
        metrics = generate_mock_metrics()
        # Add some random variation
        metrics["alert_volume"] = max(0, metrics["alert_volume"] + random.randint(-10, 10))
        metrics["compliance_rate"] = max(0.0, min(1.0, metrics["compliance_rate"] + random.uniform(-0.05, 0.05)))
        
        score = calc_risk_score(metrics)
        trend_list.append({"date": d.date().isoformat(), "score": score})
    return {"trend": trend_list}
