from pydantic import BaseModel
from typing import List

class RiskOverviewDetail(BaseModel):
    name: str
    score: float

class RiskOverviewResponse(BaseModel):
    total_risk_score: float
    details: List[RiskOverviewDetail]
    generated_at: str

class TrendRecord(BaseModel):
    date: str
    score: float

class RiskTrendResponse(BaseModel):
    trend: List[TrendRecord]
