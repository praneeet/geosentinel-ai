import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.base import Base

class Event(Base):
    __tablename__ = "events"

    event_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String(36), ForeignKey("articles.article_id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(32), nullable=False, index=True)  # CONFLICT, SECURITY, ECONOMY, DIPLOMACY
    country_iso = Column(String(3), nullable=False, index=True)
    sentiment = Column(Float, nullable=False, default=0.0)  # [-1.0, +1.0]
    severity = Column(Float, nullable=False, default=0.5)   # [0.0, 1.0]
    entities = Column(JSON, default=list)  # extracted GPE, LOC, ORG, PERSON
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    confidence = Column(Float, default=0.95)
    model_version = Column(String(32), default="tfidf-logistic-v1")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    article = relationship("Article", back_populates="events")
