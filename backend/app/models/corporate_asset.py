import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Text
from app.database.base import Base

class CorporateAssetModel(Base):
    __tablename__ = "corporate_assets"

    asset_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(120), nullable=False)
    asset_type = Column(String(32), nullable=False, default="FACILITY")
    country_iso = Column(String(3), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    buffer_radius_km = Column(Float, nullable=False, default=200.0)
    criticality = Column(String(32), nullable=False, default="TIER_1_MISSION_CRITICAL")
    description = Column(Text, nullable=True)
    prescriptive_directive = Column(Text, nullable=False, default="")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

