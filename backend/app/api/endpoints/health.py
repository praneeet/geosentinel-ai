from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.config import settings
from app.alerts.websocket import ws_dispatcher

router = APIRouter()

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """System health and operational observability probe."""
    db_status = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy" if db_status == "ok" else "degraded",
        "project": "GeoSentinel AI",
        "platform": settings.PROJECT_NAME,
        "full_title": settings.FULL_TITLE,
        "organization": settings.INSTITUTION,
        "division": settings.DEPARTMENT,
        "edition": settings.PROJECT_GROUP,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "demo_mode": settings.DEMO_MODE,
        "database": db_status,
        "websocket_active_connections": len(ws_dispatcher.active_connections),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
