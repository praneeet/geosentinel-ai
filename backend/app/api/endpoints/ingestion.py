import asyncio
import secrets
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Security, Request, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.ingestion.service import ingestion_service
from app.config import settings

logger = logging.getLogger("geosentinel.security.ingestion")

router = APIRouter()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# In-flight concurrency lock preventing overlapping ingestion runs
_ingestion_lock = asyncio.Lock()

async def verify_admin_key(
    request: Request,
    api_key: str = Security(api_key_header),
) -> bool:
    """
    Verifies administrator authorization via constant-time comparison.
    Never allows unauthenticated access or demo-mode bypass.
    Produces structured security audit logs.
    """
    client_ip = request.client.host if request.client else "unknown"
    expected_key = getattr(settings, "ADMIN_API_KEY", "")

    if not api_key:
        logger.warning(f"AUDIT [AUTH_FAILURE]: Missing X-API-Key header from IP: {client_ip} on {request.url.path}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Valid X-API-Key header required to trigger operational ingestion.",
        )

    # Constant-time comparison preventing timing attacks
    if not secrets.compare_digest(api_key.strip(), expected_key.strip()):
        logger.warning(f"AUDIT [AUTH_FAILURE]: Invalid X-API-Key provided from IP: {client_ip} on {request.url.path}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid administrator credentials.",
        )

    logger.info(f"AUDIT [AUTH_SUCCESS]: Authorized admin operation from IP: {client_ip} on {request.url.path}")
    return True

@router.post("/ingestion/run")
async def trigger_ingestion(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _auth: bool = Depends(verify_admin_key),
):
    """
    Manually triggers an ETL ingestion and deduplication cycle across all active sources.
    Recalculates country risk indexes and broadcasts critical alerts if threshold exceeded.
    Protected by admin authentication and concurrency lock.
    """
    if _ingestion_lock.locked():
        logger.warning("AUDIT [CONCURRENCY_CONFLICT]: Ingestion run requested while existing cycle is running.")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An ingestion and deduplication cycle is already actively running. Please retry once complete.",
        )

    async with _ingestion_lock:
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"AUDIT [INGESTION_TRIGGERED]: Ingestion cycle started by admin from {client_ip} at {datetime.now(timezone.utc).isoformat()}")
        result = await ingestion_service.run_pipeline(db)
        logger.info(f"AUDIT [INGESTION_COMPLETED]: Cycle finished with status: {result.get('status')}")
        return result
