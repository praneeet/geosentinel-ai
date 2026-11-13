from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.models.event import Event

router = APIRouter()

@router.get("/trends")
async def get_global_trends(days: int = Query(30, ge=7, le=90), db: AsyncSession = Depends(get_db)):
    """Aggregates global category distribution, daily event velocity, and average sentiment."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)

    # Category counts
    cat_stmt = (
        select(Event.category, func.count(Event.event_id))
        .where(Event.timestamp >= cutoff)
        .group_by(Event.category)
    )
    cat_res = await db.execute(cat_stmt)
    category_distribution = {cat: count for cat, count in cat_res.all()}

    # Ensure all four categories are present
    for c in ["CONFLICT", "SECURITY", "ECONOMY", "DIPLOMACY"]:
        category_distribution.setdefault(c, 0)

    # Sentiment average
    sent_stmt = select(func.avg(Event.sentiment)).where(Event.timestamp >= cutoff)
    sent_res = await db.execute(sent_stmt)
    avg_sent = sent_res.scalar() or -0.15

    # Daily timeline from real database events
    ev_stmt = select(Event.timestamp, Event.sentiment).where(Event.timestamp >= cutoff)
    ev_res = await db.execute(ev_stmt)
    real_days = {}
    for ts, sent in ev_res.all():
        if not ts:
            continue
        date_str = ts.strftime("%Y-%m-%d") if hasattr(ts, "strftime") else str(ts)[:10]
        if date_str not in real_days:
            real_days[date_str] = {"count": 0, "sent_sum": 0.0}
        real_days[date_str]["count"] += 1
        real_days[date_str]["sent_sum"] += (sent if sent is not None else avg_sent)

    timeline = []
    for d in range(days, 0, -1):
        dt = now - timedelta(days=d)
        date_str = dt.strftime("%Y-%m-%d")
        if date_str in real_days and real_days[date_str]["count"] > 0:
            c = real_days[date_str]["count"]
            s = real_days[date_str]["sent_sum"] / c
            timeline.append({
                "date": date_str,
                "events": c,
                "sentiment": round(s, 2),
            })
        else:
            timeline.append({
                "date": date_str,
                "events": 0,
                "sentiment": round(avg_sent, 2),
            })

    return {
        "observation_window_days": days,
        "category_distribution": category_distribution,
        "average_sentiment": round(avg_sent, 3),
        "timeline": timeline,
    }
