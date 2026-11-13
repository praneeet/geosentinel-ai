from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.models.report import ReportModel
from app.reports.dossier_generator import dossier_generator
from app.api.endpoints.auth import require_permission

router = APIRouter()

# In-memory storage for generated dossiers for immediate retrieval
_reports_cache = {}

@router.post("/reports/generate")
async def generate_report(
    country_iso: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_permission("dossier")),
):
    """Generates an on-demand, evidence-backed country intelligence dossier."""
    iso_clean = country_iso.strip().upper()
    dossier = await dossier_generator.generate_country_dossier(iso_clean, db)
    report_id = dossier["report_id"]
    _reports_cache[report_id] = dossier

    # Persist report to database
    try:
        gen_at = datetime.now(timezone.utc)
        if "generated_at" in dossier:
            try:
                gen_at = datetime.fromisoformat(dossier["generated_at"])
            except Exception:
                pass

        report_obj = ReportModel(
            report_id=report_id,
            country_iso=iso_clean,
            country_name=dossier.get("country_name", iso_clean),
            generated_at=gen_at,
            classification=dossier.get("classification", "GEOSENTINEL INTELLIGENCE BRIEFING"),
            dossier_data=dossier,
        )
        db.add(report_obj)
        await db.commit()
    except Exception:
        pass

    return dossier

@router.get("/reports")
async def list_reports(limit: int = 50, db: AsyncSession = Depends(get_db)):
    """Lists saved intelligence dossiers."""
    stmt = select(ReportModel).order_by(ReportModel.generated_at.desc()).limit(limit)
    res = await db.execute(stmt)
    reports = res.scalars().all()
    return [
        {
            "report_id": r.report_id,
            "country_iso": r.country_iso,
            "country_name": r.country_name,
            "generated_at": r.generated_at.isoformat() if r.generated_at else None,
            "classification": r.classification,
        }
        for r in reports
    ]

@router.get("/reports/{report_id}")
async def get_report(report_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves an existing generated dossier by ID."""
    if report_id in _reports_cache:
        return _reports_cache[report_id]

    stmt = select(ReportModel).where(ReportModel.report_id == report_id)
    res = await db.execute(stmt)
    report_obj = res.scalars().first()
    if report_obj and report_obj.dossier_data:
        _reports_cache[report_id] = report_obj.dossier_data
        return report_obj.dossier_data

    raise HTTPException(status_code=404, detail="Intelligence report not found")
