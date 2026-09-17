import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Text
from sqlalchemy.orm import relationship
from app.database.base import Base

class Article(Base):
    __tablename__ = "articles"

    article_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(512), nullable=False)
    content_hash = Column(String(64), unique=True, index=True, nullable=False)
    source_name = Column(String(128), nullable=False, default="Unknown Source")
    source_url = Column(Text, nullable=False)
    credibility = Column(Float, nullable=False, default=0.90)
    published_at = Column(DateTime(timezone=True), nullable=False, index=True)
    body_text = Column(Text, nullable=False)
    language = Column(String(10), default="en")
    author = Column(String(256), nullable=True)
    country_hint = Column(String(3), nullable=True)
    status = Column(String(32), default="processed", index=True)
    dedup_type = Column(String(32), default="unique")  # unique, exact_duplicate, near_duplicate
    canonical_article_id = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    events = relationship("Event", back_populates="article", cascade="all, delete-orphan")
