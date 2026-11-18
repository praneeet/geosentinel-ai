from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.ingestion.service import ingestion_service
from app.config import settings

router = APIRouter()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_admin_key(api_key: str = Security(api_key_header)):
    """Verifies administrator authorization to trigger costly external ETL ingestion."""
    if settings.DEMO_MODE and not api_key:
        return True
    expected_key = getattr(settings, "ADMIN_API_KEY", "geosentinel-admin-secret")
    if not api_key or api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Valid X-API-Key header required to trigger operational ingestion.",
        )
    return True

@router.post("/ingestion/run")
async def trigger_ingestion(
    db: AsyncSession = Depends(get_db),
    _auth: bool = Depends(verify_admin_key),
):
    """
    Manually triggers an ETL ingestion and deduplication cycle across all active sources.
    Recalculates country risk indexes and broadcasts critical alerts if threshold exceeded.
    """
    result = await ingestion_service.run_pipeline(db)
    return result
