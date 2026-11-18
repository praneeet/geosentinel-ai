import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON
from app.database.base import Base

class Summary(Base):
    __tablename__ = "summaries"

    summary_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    country_iso = Column(String(3), nullable=False, index=True)
    bullet_points = Column(JSON, nullable=False, default=list)  # [Key development, Why it matters, Implication]
    evidence_links = Column(JSON, nullable=False, default=list)  # [{title, url, source, published_at}]
    generated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    model_version = Column(String(32), default="extractive-heuristics-v1")
