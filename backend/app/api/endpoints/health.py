from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Response
from sqlalchemy import text, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.config import settings
from app.alerts.websocket import ws_dispatcher
from app.models.article import Article
from app.models.event import Event
from app.models.alert import Alert

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

@router.get("/metrics")
async def get_metrics(db: AsyncSession = Depends(get_db)):
    """Prometheus-compatible telemetry scraping endpoint."""
    try:
        art_count = (await db.execute(select(func.count(Article.article_id)))).scalar() or 0
        ev_count = (await db.execute(select(func.count(Event.event_id)))).scalar() or 0
        al_count = (await db.execute(select(func.count(Alert.alert_id)))).scalar() or 0
        db_up = 1
    except Exception:
        art_count = ev_count = al_count = 0
        db_up = 0

    ws_conns = len(ws_dispatcher.active_connections)

    lines = [
        "# HELP geosentinel_up Boolean indicating if GeoSentinel AI API service is operational.",
        "# TYPE geosentinel_up gauge",
        "geosentinel_up 1",
        "# HELP geosentinel_database_up Boolean indicating database connectivity.",
        "# TYPE geosentinel_database_up gauge",
        f"geosentinel_database_up {db_up}",
        "# HELP geosentinel_websocket_connections_active Number of connected WebSocket clients.",
        "# TYPE geosentinel_websocket_connections_active gauge",
        f"geosentinel_websocket_connections_active {ws_conns}",
        "# HELP geosentinel_articles_total Total count of ingested intelligence articles.",
        "# TYPE geosentinel_articles_total counter",
        f"geosentinel_articles_total {art_count}",
        "# HELP geosentinel_events_total Total count of structured geopolitical threat events.",
        "# TYPE geosentinel_events_total counter",
        f"geosentinel_events_total {ev_count}",
        "# HELP geosentinel_alerts_total Total count of dispatched threshold alerts.",
        "# TYPE geosentinel_alerts_total counter",
        f"geosentinel_alerts_total {al_count}",
    ]
    return Response(
        content="\n".join(lines) + "\n",
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )
