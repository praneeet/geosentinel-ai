from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertResponse, AlertListResponse

router = APIRouter()

@router.get("/alerts", response_model=AlertListResponse)
async def list_alerts(limit: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db)):
    """Returns past triggered alerts above critical threshold R > 75."""
    count_stmt = select(func.count(Alert.alert_id))
    count_res = await db.execute(count_stmt)
    total = count_res.scalar() or 0

    stmt = select(Alert).order_by(Alert.sent_at.desc()).limit(limit)
    res = await db.execute(stmt)
    alerts = res.scalars().all()

    return {
        "total": total,
        "alerts": alerts,
    }
