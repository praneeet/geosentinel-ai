from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.ingestion.service import ingestion_service

router = APIRouter()

@router.post("/ingestion/run")
async def trigger_ingestion(db: AsyncSession = Depends(get_db)):
    """
    Manually triggers an ETL ingestion and deduplication cycle across all active sources.
    Recalculates country risk indexes and broadcasts critical alerts if threshold exceeded.
    """
    result = await ingestion_service.run_pipeline(db)
    return result
