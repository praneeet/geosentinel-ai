from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class EventBase(BaseModel):
    category: str
    country_iso: str
    sentiment: float = Field(..., ge=-1.0, le=1.0)
    severity: float = Field(..., ge=0.0, le=1.0)
    entities: List[Dict[str, str]] = []
    timestamp: datetime
    confidence: float = 0.95
    model_version: str = "distilbert-geosentinel-v1"

class EventCreate(EventBase):
    article_id: str

class EventResponse(EventBase):
    event_id: str
    article_id: str
    created_at: datetime
    model_config = {"from_attributes": True}

class EventWithArticle(EventResponse):
    article_title: Optional[str] = None
    source_name: Optional[str] = None
    source_url: Optional[str] = None

class EventListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    events: List[EventWithArticle]
