from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class AlertPayload(BaseModel):
    country: str
    country_name: str
    risk_score: float
    tier: str
    trigger: str = "critical_threshold"
    timestamp: datetime
    top_contributors: List[Dict[str, Any]] = []
    evidence: List[Dict[str, Any]] = []

class AlertResponse(BaseModel):
    alert_id: str
    country_iso: str
    risk_score: float
    trigger_tier: str
    trigger_reason: str
    payload: Dict[str, Any]
    sent_at: datetime
    model_config = {"from_attributes": True}

class AlertListResponse(BaseModel):
    total: int
    alerts: List[AlertResponse]
