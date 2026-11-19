import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, JSON, Index
from app.database.base import Base

class Alert(Base):
    __tablename__ = "alerts"

    alert_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    country_iso = Column(String(3), nullable=False, index=True)
    risk_score = Column(Float, nullable=False)
    trigger_tier = Column(String(16), nullable=False)
    trigger_reason = Column(String(64), default="critical_threshold")
    payload = Column(JSON, default=dict)
    sent_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    __table_args__ = (
        Index("ix_alerts_country_sent_at", "country_iso", "sent_at"),
    )
