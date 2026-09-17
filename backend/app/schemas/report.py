from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.schemas.country import CountryDetailResponse
from app.schemas.risk import RiskHistoryPoint, RiskForecastPoint

class IntelligenceDossier(BaseModel):
    report_id: str
    country_iso: str
    country_name: str
    generated_at: datetime
    classification: str = "OPEN-SOURCE INTELLIGENCE (OSINT) - UNCLASSIFIED"
    disclaimer: str = (
        "GeoSentinel AI decision-support intelligence dossier. "
        "Risk scores and trend forecasts are model-derived indicators and do not represent "
        "official government assessments or deterministic event predictions."
    )
    current_risk: float
    risk_tier: str
    risk_trend: str
    contributing_breakdown: Dict[str, float]
    executive_briefing: List[str]
    recent_events: List[Dict[str, Any]]
    evidence_citations: List[Dict[str, Any]]
    experimental_forecast: Optional[List[RiskForecastPoint]] = None
    model_versions: Dict[str, str]
