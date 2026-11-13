from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, JSON
from app.database.base import Base

class PlaybookModel(Base):
    __tablename__ = "playbooks"

    playbook_id = Column(String(64), primary_key=True)
    title = Column(String(256), nullable=False)
    category = Column(String(64), nullable=False)
    trigger_threshold = Column(Text, nullable=False)
    threat_theater = Column(Text, nullable=False)
    executive_summary = Column(Text, nullable=False)
    quantified_impact = Column(JSON, nullable=False, default=dict)
    recommended_option = Column(Text, nullable=False)
    prescriptive_action_plan = Column(JSON, nullable=False, default=list)
    bimco_legal_clauses = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

