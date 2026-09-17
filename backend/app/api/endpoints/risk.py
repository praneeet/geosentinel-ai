from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
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
