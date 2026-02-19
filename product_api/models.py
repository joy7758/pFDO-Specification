from pydantic import BaseModel


class RiskOverviewDetail(BaseModel):
    name: str
    score: float

class RiskOverviewResponse(BaseModel):
    total_risk_score: float
    details: list[RiskOverviewDetail]
    generated_at: str

class TrendRecord(BaseModel):
    date: str
    score: float

class RiskTrendResponse(BaseModel):
    trend: list[TrendRecord]
