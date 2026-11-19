import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Integer, JSON
from app.database.base import Base

class CountryScore(Base):
    __tablename__ = "country_scores"

    score_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    country_iso = Column(String(3), nullable=False, unique=True, index=True)
    risk_index = Column(Float, nullable=False)  # [0.0, 100.0]
    decayed_agg = Column(Float, nullable=False)
    risk_tier = Column(String(16), nullable=False, index=True)  # Low, Moderate, Severe
    event_count = Column(Integer, default=0)
    contributing_factors = Column(JSON, default=dict)  # category weights, sentiment factor, decay breakdown
    calculated_at = Column(DateTime(timezone=True), nullable=False, index=True, default=lambda: datetime.now(timezone.utc))
