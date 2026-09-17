from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.schemas.risk import CountryRiskResponse
from app.schemas.event import EventWithArticle

class ExecutiveSummaryResponse(BaseModel):
    country_iso: str
    bullet_points: List[str]
    evidence_links: List[Dict[str, Any]]
    generated_at: datetime
    model_version: str

class CountryDetailResponse(BaseModel):
    country_iso: str
    country_name: str
    lat: float
    lon: float
    current_risk: CountryRiskResponse
    summary: Optional[ExecutiveSummaryResponse] = None
    recent_events: List[EventWithArticle] = []
    category_counts: Dict[str, int] = {}
    average_sentiment: float = 0.0
