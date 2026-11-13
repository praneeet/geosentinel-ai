import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON
from app.database.base import Base

class ReportModel(Base):
    __tablename__ = "reports"

    report_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    country_iso = Column(String(3), nullable=False, index=True)
    country_name = Column(String(128), nullable=False)
    generated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    classification = Column(String(128), nullable=False)
    dossier_data = Column(JSON, nullable=False, default=dict)

