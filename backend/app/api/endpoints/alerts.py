from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.database.session import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertResponse, AlertListResponse

router = APIRouter()

@router.get("/alerts/webhooks/status")
async def get_webhook_status():
    """Returns actual runtime configuration status for external alert webhooks."""
    discord_configured = bool(settings.DISCORD_WEBHOOK_URL and settings.DISCORD_WEBHOOK_URL.strip())
    telegram_configured = bool(
        settings.TELEGRAM_BOT_TOKEN
        and settings.TELEGRAM_BOT_TOKEN.strip()
        and settings.TELEGRAM_CHAT_ID
        and settings.TELEGRAM_CHAT_ID.strip()
    )
    return {
        "webhooks_enabled": bool(settings.WEBHOOKS_ENABLED),
        "discord_configured": discord_configured,
        "telegram_configured": telegram_configured,
    }

@router.get("/alerts", response_model=AlertListResponse)
async def list_alerts(
    page: int = Query(1, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=100),
    limit: Optional[int] = Query(None, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Returns past triggered alerts above critical threshold R > 75 with pagination support."""
    effective_limit = page_size or limit or 20
    offset = (page - 1) * effective_limit

    count_stmt = select(func.count(Alert.alert_id))
    count_res = await db.execute(count_stmt)
    total = count_res.scalar() or 0

    stmt = select(Alert).order_by(Alert.sent_at.desc()).offset(offset).limit(effective_limit)
    res = await db.execute(stmt)
    alerts = res.scalars().all()

    return {
        "total": total,
        "alerts": alerts,
    }
