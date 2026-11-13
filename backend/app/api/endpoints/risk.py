from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.config import settings
from app.models.country_score import CountryScore
from app.schemas.risk import CountryRiskMapItem
from app.utils.iso_countries import COUNTRY_DATABASE

router = APIRouter()

@router.get("/risk/map", response_model=List[CountryRiskMapItem])
async def get_risk_map_data(db: AsyncSession = Depends(get_db)):
    """Returns geospatial choropleth dataset with risk scores and tiers for all countries."""
    stmt = select(CountryScore)
    res = await db.execute(stmt)
    scores = {s.country_iso: s for s in res.scalars().all()}

    items = []
    for iso, info in COUNTRY_DATABASE.items():
        score_obj = scores.get(iso)
        risk_val = score_obj.risk_index if score_obj else 0.0
        tier = score_obj.risk_tier if score_obj else "Low"
        event_cnt = score_obj.event_count if score_obj else 0

        items.append(
            CountryRiskMapItem(
                country_iso=iso,
                country_name=info["name"],
                risk_index=risk_val,
                risk_tier=tier,
                event_count=event_cnt,
                lat=info["lat"],
                lon=info["lon"],
            )
        )
    return items

@router.get("/risk/export/geojson")
async def export_risk_geojson(db: AsyncSession = Depends(get_db)):
    """
    Exports country risk indices and coordinates as a standard RFC 7946 GeoJSON FeatureCollection
    for external GIS platforms (QGIS, ArcGIS, Google Earth).
    """
    stmt = select(CountryScore)
    res = await db.execute(stmt)
    scores = {s.country_iso: s for s in res.scalars().all()}

    features = []
    import json
    for iso, info in COUNTRY_DATABASE.items():
        score_obj = scores.get(iso)
        risk_val = score_obj.risk_index if score_obj else 0.0
        tier = score_obj.risk_tier if score_obj else "Low"
        event_cnt = score_obj.event_count if score_obj else 0
        contributing = score_obj.contributing_factors if score_obj else {}
        if isinstance(contributing, str):
            try:
                contributing = json.loads(contributing)
            except Exception:
                contributing = {}
        if not isinstance(contributing, dict):
            contributing = {}

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [info["lon"], info["lat"]],
            },
            "properties": {
                "country_iso": iso,
                "country_name": info["name"],
                "region": info["region"],
                "risk_index": risk_val,
                "risk_tier": tier,
                "event_count": event_cnt,
                "conflict_score": contributing.get("conflict_score", 0.0),
                "security_score": contributing.get("security_score", 0.0),
                "economy_score": contributing.get("economy_score", 0.0),
                "diplomacy_score": contributing.get("diplomacy_score", 0.0),
                "attribution": f"{settings.PROJECT_NAME} • {settings.DEPARTMENT}",
            },
        })

    return {
        "type": "FeatureCollection",
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"},
        },
        "features": features,
    }

