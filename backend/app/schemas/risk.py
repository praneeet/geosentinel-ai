from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ContributingFactors(BaseModel):
    conflict_score: float = 0.0
    security_score: float = 0.0
    economy_score: float = 0.0
    diplomacy_score: float = 0.0
    temporal_decay_factor: float = 1.0
    sentiment_magnitude: float = 0.0
    active_event_count: int = 0
    top_event_ids: List[str] = []

class CountryRiskResponse(BaseModel):
    country_iso: str
    country_name: str
    risk_index: float = Field(..., ge=0.0, le=100.0)
    risk_tier: str  # Low, Moderate, Severe
    decayed_agg: float
    event_count: int
    calculated_at: datetime
    contributing_factors: ContributingFactors
    latitude: float
    longitude: float

class CountryRiskMapItem(BaseModel):
    country_iso: str
    country_name: str
    risk_index: float
    risk_tier: str
    event_count: int
    lat: float
    lon: float

class RiskHistoryPoint(BaseModel):
    timestamp: datetime
    risk_score: float
    event_volume: int
    sentiment: float
    conflict_share: float
    security_share: float
    economy_share: float
    diplomacy_share: float

class RiskForecastPoint(BaseModel):
    timestamp: datetime
    forecast_risk: float
    lower_bound: float
    upper_bound: float
    model_type: str
    is_experimental: bool = True
