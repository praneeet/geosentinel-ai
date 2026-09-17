from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.reports.dossier_generator import dossier_generator

router = APIRouter()

# In-memory storage for generated dossiers for immediate retrieval
_reports_cache = {}

@router.post("/reports/generate")
async def generate_report(
    country_iso: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
):
    """Generates an on-demand, evidence-backed country intelligence dossier."""
    iso_clean = country_iso.strip().upper()
    dossier = await dossier_generator.generate_country_dossier(iso_clean, db)
    report_id = dossier["report_id"]
    _reports_cache[report_id] = dossier
    return dossier

@router.get("/reports/{report_id}")
async def get_report(report_id: str):
    """Retrieves an existing generated dossier by ID."""
    if report_id in _reports_cache:
        return _reports_cache[report_id]
    raise HTTPException(status_code=404, detail="Intelligence report not found")
