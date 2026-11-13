import math
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.event import Event
from app.models.article import Article
from app.models.country_score import CountryScore
from app.models.corporate_asset import CorporateAssetModel
from app.utils.iso_countries import COUNTRY_DATABASE, get_country_info
from app.api.endpoints.auth import require_permission

router = APIRouter()

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance between two coordinates in kilometers."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)

class CorporateAsset(BaseModel):
    asset_id: str
    name: str
    asset_type: str = Field(..., description="FACILITY, MARITIME_VESSEL, PORT, DATA_CENTER, SUPPLY_DEPOT, OFFICE")
    country_iso: str
    country_name: str
    latitude: float
    longitude: float
    buffer_radius_km: float = Field(200.0, description="Geofence alert buffer radius in kilometers")
    criticality: str = Field("TIER_1_MISSION_CRITICAL", description="TIER_1_MISSION_CRITICAL, TIER_2_STRATEGIC, TIER_3_OPERATIONAL")
    threat_level: str = "NORMAL"  # NORMAL, ELEVATED, HIGH, CRITICAL
    threat_score: float = 0.0      # 0.0 to 100.0
    active_breaches_count: int = 0
    nearest_incident_distance_km: Optional[float] = None
    prescriptive_directive: str
    created_at: str

class AssetCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=120)
    asset_type: str = Field("FACILITY", description="FACILITY, MARITIME_VESSEL, PORT, DATA_CENTER, SUPPLY_DEPOT, OFFICE")
    country_iso: str = Field(..., min_length=3, max_length=3)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    buffer_radius_km: float = Field(200.0, ge=25.0, le=1000.0)
    criticality: str = Field("TIER_1_MISSION_CRITICAL")
    description: Optional[str] = None

# Default Pre-Seeded Global Enterprise Portfolio
INITIAL_CORPORATE_ASSETS: List[Dict[str, Any]] = [
    {
        "asset_id": "asset-twn-fab18",
        "name": "Hsinchu Advanced Semiconductor Fab 18",
        "asset_type": "FACILITY",
        "country_iso": "TWN",
        "latitude": 24.782,
        "longitude": 120.998,
        "buffer_radius_km": 250.0,
        "criticality": "TIER_1_MISSION_CRITICAL",
        "prescriptive_directive": "Maintain dual-sourced raw chemical precursors; execute monthly air freight diversion contingency.",
        "created_at": "2026-01-10T00:00:00Z",
    },
    {
        "asset_id": "asset-yem-lng-carrier",
        "name": "LNG Carrier 'Sentinel Pioneer' (Voyage 408)",
        "asset_type": "MARITIME_VESSEL",
        "country_iso": "YEM",
        "latitude": 12.585,
        "longitude": 43.332,
        "buffer_radius_km": 200.0,
        "criticality": "TIER_1_MISSION_CRITICAL",
        "prescriptive_directive": "Direct diversion around Cape of Good Hope if littoral drone threat exceeds Severity 0.70.",
        "created_at": "2026-02-14T00:00:00Z",
    },
    {
        "asset_id": "asset-ukr-logistics",
        "name": "Dnipro Central Freight & Cold-Chain Hub",
        "asset_type": "SUPPLY_DEPOT",
        "country_iso": "UKR",
        "latitude": 48.464,
        "longitude": 35.046,
        "buffer_radius_km": 300.0,
        "criticality": "TIER_2_STRATEGIC",
        "prescriptive_directive": "Disperse critical pharmaceutical inventory to western distribution centers in Lviv.",
        "created_at": "2026-01-15T00:00:00Z",
    },
    {
        "asset_id": "asset-nld-rotterdam",
        "name": "Port of Rotterdam Deepwater Petrochemical Terminal",
        "asset_type": "PORT",
        "country_iso": "NLD",
        "latitude": 51.956,
        "longitude": 4.132,
        "buffer_radius_km": 150.0,
        "criticality": "TIER_1_MISSION_CRITICAL",
        "prescriptive_directive": "Monitor North Sea subsea energy corridor cable security and industrial SCADA telemetry.",
        "created_at": "2026-01-20T00:00:00Z",
    },
    {
        "asset_id": "asset-sau-ras-tanura",
        "name": "Ras Tanura Hydrocarbon Offshore Pier",
        "asset_type": "FACILITY",
        "country_iso": "SAU",
        "latitude": 26.643,
        "longitude": 50.158,
        "buffer_radius_km": 250.0,
        "criticality": "TIER_1_MISSION_CRITICAL",
        "prescriptive_directive": "Synchronize with naval coalition air-defense alert feeds and activate bunker reserves.",
        "created_at": "2026-02-01T00:00:00Z",
    },
    {
        "asset_id": "asset-sgp-malacca-feeder",
        "name": "Container Feeder 'Apex Navigator' (Strait Transit)",
        "asset_type": "MARITIME_VESSEL",
        "country_iso": "SGP",
        "latitude": 1.250,
        "longitude": 103.800,
        "buffer_radius_km": 120.0,
        "criticality": "TIER_2_STRATEGIC",
        "prescriptive_directive": "Enforce anti-piracy watch protocols and maintain radar surveillance on littoral approaches.",
        "created_at": "2026-02-18T00:00:00Z",
    },
    {
        "asset_id": "asset-usa-ashburn-cloud",
        "name": "Northern Virginia Hyperscale Cloud Campus",
        "asset_type": "DATA_CENTER",
        "country_iso": "USA",
        "latitude": 39.043,
        "longitude": -77.487,
        "buffer_radius_km": 150.0,
        "criticality": "TIER_1_MISSION_CRITICAL",
        "prescriptive_directive": "Audit grid switchgear resilience and isolate critical BGP routing interconnects against APT campaigns.",
        "created_at": "2026-01-05T00:00:00Z",
    },
]

# Runtime in-memory registry of corporate assets
_ENTERPRISE_ASSETS: Dict[str, Dict[str, Any]] = {
    a["asset_id"]: dict(a) for a in INITIAL_CORPORATE_ASSETS
}

def asset_model_to_dict(model_obj: CorporateAssetModel) -> Dict[str, Any]:
    return {
        "asset_id": model_obj.asset_id,
        "name": model_obj.name,
        "asset_type": model_obj.asset_type,
        "country_iso": model_obj.country_iso,
        "latitude": model_obj.latitude,
        "longitude": model_obj.longitude,
        "buffer_radius_km": model_obj.buffer_radius_km,
        "criticality": model_obj.criticality,
        "description": model_obj.description,
        "prescriptive_directive": model_obj.prescriptive_directive,
        "created_at": model_obj.created_at.isoformat() if hasattr(model_obj.created_at, "isoformat") else str(model_obj.created_at),
    }

async def compute_asset_threat(asset: Dict[str, Any], db: AsyncSession) -> CorporateAsset:
    """Calculates spherical proximity to active events and evaluates geofence breaches."""
    c_iso = asset["country_iso"].upper()
    country_info = get_country_info(c_iso)

    # 1. Fetch country base risk score
    score_stmt = select(CountryScore).where(CountryScore.country_iso == c_iso)
    score_res = await db.execute(score_stmt)
    c_score = score_res.scalars().first()
    base_country_risk = c_score.risk_index if c_score else 10.0

    # 2. Fetch recent events in this country or global
    ev_stmt = (
        select(Event)
        .where(Event.country_iso == c_iso)
        .order_by(Event.timestamp.desc())
        .limit(20)
    )
    ev_res = await db.execute(ev_stmt)
    events = ev_res.scalars().all()

    breaches = 0
    nearest_dist: Optional[float] = None
    proximity_severity_sum = 0.0

    # Use country centroid as event location approximation when sub-national coordinates are unspecified
    ev_lat = country_info.get("lat", asset["latitude"])
    ev_lon = country_info.get("lon", asset["longitude"])

    dist = haversine_distance_km(asset["latitude"], asset["longitude"], ev_lat, ev_lon)
    nearest_dist = dist

    for ev in events:
        if dist <= asset["buffer_radius_km"]:
            breaches += 1
            proximity_weight = max(0.2, (asset["buffer_radius_km"] - dist) / asset["buffer_radius_km"])
            proximity_severity_sum += (ev.severity or 0.5) * proximity_weight

    # Synthesize composite asset threat score
    raw_threat = (base_country_risk * 0.60) + (min(40.0, proximity_severity_sum * 12.0) * 0.40)
    threat_score = round(max(5.0, min(100.0, raw_threat)), 1)

    if threat_score >= 65.0 or breaches >= 4:
        threat_level = "CRITICAL"
    elif threat_score >= 45.0 or breaches >= 2:
        threat_level = "HIGH"
    elif threat_score >= 25.0:
        threat_level = "ELEVATED"
    else:
        threat_level = "NORMAL"

    return CorporateAsset(
        asset_id=asset["asset_id"],
        name=asset["name"],
        asset_type=asset["asset_type"],
        country_iso=c_iso,
        country_name=country_info.get("name", c_iso),
        latitude=asset["latitude"],
        longitude=asset["longitude"],
        buffer_radius_km=asset["buffer_radius_km"],
        criticality=asset["criticality"],
        threat_level=threat_level,
        threat_score=threat_score,
        active_breaches_count=breaches,
        nearest_incident_distance_km=nearest_dist,
        prescriptive_directive=asset["prescriptive_directive"],
        created_at=asset["created_at"],
    )

@router.get("/assets", response_model=List[CorporateAsset])
async def list_corporate_assets(db: AsyncSession = Depends(get_db)):
    """
    Returns monitored enterprise corporate assets with real-time geofence threat assessments.
    Enables Fortune 500 supply chain and critical facility tracking.
    """
    stmt = select(CorporateAssetModel)
    res = await db.execute(stmt)
    db_assets = res.scalars().all()

    if not db_assets:
        # Seed initial assets into persistent DB
        for a in INITIAL_CORPORATE_ASSETS:
            db_obj = CorporateAssetModel(
                asset_id=a["asset_id"],
                name=a["name"],
                asset_type=a["asset_type"],
                country_iso=a["country_iso"],
                latitude=a["latitude"],
                longitude=a["longitude"],
                buffer_radius_km=a["buffer_radius_km"],
                criticality=a["criticality"],
                description=a.get("description"),
                prescriptive_directive=a["prescriptive_directive"],
            )
            db.add(db_obj)
        await db.commit()
        res = await db.execute(select(CorporateAssetModel))
        db_assets = res.scalars().all()

    assessed = []
    for asset_model in db_assets:
        asset_dict = asset_model_to_dict(asset_model)
        _ENTERPRISE_ASSETS[asset_dict["asset_id"]] = asset_dict
        res = await compute_asset_threat(asset_dict, db)
        assessed.append(res)
    # Sort highest threat first
    assessed.sort(key=lambda a: a.threat_score, reverse=True)
    return assessed

@router.post("/assets", response_model=CorporateAsset, status_code=status.HTTP_201_CREATED)
async def create_corporate_asset(
    req: AssetCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_permission("simulate")),
):
    """Pins a new critical corporate asset with customized geofence buffer radius."""
    c_iso = req.country_iso.upper()
    info = get_country_info(c_iso)
    if not info:
        raise HTTPException(status_code=400, detail=f"Invalid ISO-3166 alpha-3 code: {c_iso}")

    new_id = f"asset-{uuid.uuid4().hex[:8]}"
    directive = req.description or f"Active geofence monitoring established across {req.buffer_radius_km} km radius in {info.get('name')}."
    
    # Persist to database
    db_obj = CorporateAssetModel(
        asset_id=new_id,
        name=req.name,
        asset_type=req.asset_type.upper(),
        country_iso=c_iso,
        latitude=req.latitude,
        longitude=req.longitude,
        buffer_radius_km=req.buffer_radius_km,
        criticality=req.criticality,
        description=req.description,
        prescriptive_directive=directive,
    )
    db.add(db_obj)
    await db.commit()

    asset_dict = {
        "asset_id": new_id,
        "name": req.name,
        "asset_type": req.asset_type.upper(),
        "country_iso": c_iso,
        "latitude": req.latitude,
        "longitude": req.longitude,
        "buffer_radius_km": req.buffer_radius_km,
        "criticality": req.criticality,
        "prescriptive_directive": directive,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _ENTERPRISE_ASSETS[new_id] = asset_dict
    return await compute_asset_threat(asset_dict, db)

@router.delete("/assets/{asset_id}")
async def delete_corporate_asset(
    asset_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_permission("simulate")),
):
    """Removes a corporate asset from active geofence monitoring."""
    stmt = select(CorporateAssetModel).where(CorporateAssetModel.asset_id == asset_id)
    res = await db.execute(stmt)
    db_obj = res.scalars().first()
    if db_obj:
        await db.delete(db_obj)
        await db.commit()
    elif asset_id not in _ENTERPRISE_ASSETS:
        raise HTTPException(status_code=404, detail="Corporate asset not found")
        
    _ENTERPRISE_ASSETS.pop(asset_id, None)
    return {"status": "success", "message": f"Asset {asset_id} removed from tracking registry"}

@router.get("/assets/{asset_id}/threat-assessment")
async def get_asset_threat_detail(asset_id: str, db: AsyncSession = Depends(get_db)):
    """Detailed threat assessment and incident proximity breakdown for a specific enterprise asset."""
    stmt = select(CorporateAssetModel).where(CorporateAssetModel.asset_id == asset_id)
    res = await db.execute(stmt)
    db_obj = res.scalars().first()
    
    if db_obj:
        asset = asset_model_to_dict(db_obj)
    else:
        asset = _ENTERPRISE_ASSETS.get(asset_id)

    if not asset:
        raise HTTPException(status_code=404, detail="Corporate asset not found")

    threat_profile = await compute_asset_threat(asset, db)

    # Fetch recent primary events within country
    ev_stmt = (
        select(Event, Article.title, Article.source_name, Article.source_url)
        .join(Article, Event.article_id == Article.article_id)
        .where(Event.country_iso == asset["country_iso"])
        .order_by(Event.timestamp.desc())
        .limit(6)
    )
    res = await db.execute(ev_stmt)

    nearby_events = []
    for ev, title, source_name, source_url in res.all():
        nearby_events.append({
            "event_id": ev.event_id,
            "category": ev.category,
            "sentiment": ev.sentiment,
            "severity": ev.severity,
            "title": title,
            "source_name": source_name,
            "source_url": source_url,
            "timestamp": ev.timestamp.isoformat(),
        })

    return {
        "asset": threat_profile,
        "geofence_status": "BREACHED" if threat_profile.active_breaches_count > 0 else "SECURE",
        "buffer_radius_km": asset["buffer_radius_km"],
        "nearby_incidents": nearby_events,
        "mitigation_playbook": {
            "tier": threat_profile.threat_level,
            "primary_action": threat_profile.prescriptive_directive,
            "contingency_status": "STANDBY" if threat_profile.threat_score < 50 else "ACTIVATE_STAGE_1",
            "escalation_contact": "Global Threat Operations Center (GTOC) Crisis Desk",
        },
    }
