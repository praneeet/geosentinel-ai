import time
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Response
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.article import Article
from app.models.event import Event
from app.models.alert import Alert
from app.models.country_score import CountryScore
from app.models.corporate_asset import CorporateAssetModel
from app.alerts.websocket import ws_dispatcher
from app.api.endpoints.assets import INITIAL_CORPORATE_ASSETS

router = APIRouter()

# In-memory request counters for Prometheus exposition
HTTP_REQUESTS_TOTAL = 0
HTTP_REQUEST_DURATION_SUM = 0.0

def record_http_metric(duration_seconds: float):
    global HTTP_REQUESTS_TOTAL, HTTP_REQUEST_DURATION_SUM
    HTTP_REQUESTS_TOTAL += 1
    HTTP_REQUEST_DURATION_SUM += duration_seconds

@router.get("/metrics")
async def prometheus_metrics(db: AsyncSession = Depends(get_db)):
    """Exposes real-time Prometheus-compatible telemetry for APM & Grafana dashboards."""
    try:
        art_count = (await db.execute(select(func.count(Article.article_id)))).scalar() or 0
        evt_count = (await db.execute(select(func.count(Event.event_id)))).scalar() or 0
        alert_count = (await db.execute(select(func.count(Alert.alert_id)))).scalar() or 0
        assets_count = (await db.execute(select(func.count(CorporateAssetModel.asset_id)))).scalar() or len(INITIAL_CORPORATE_ASSETS)
    except Exception:
        art_count, evt_count, alert_count, assets_count = 0, 0, 0, len(INITIAL_CORPORATE_ASSETS)

    ws_conns = len(ws_dispatcher.active_connections)
    avg_duration = (HTTP_REQUEST_DURATION_SUM / HTTP_REQUESTS_TOTAL) if HTTP_REQUESTS_TOTAL > 0 else 0.0

    metrics_text = f"""# HELP geosentinel_http_requests_total Total number of HTTP requests processed by GeoSentinel
# TYPE geosentinel_http_requests_total counter
geosentinel_http_requests_total {HTTP_REQUESTS_TOTAL}

# HELP geosentinel_http_request_duration_seconds Total cumulative duration of HTTP requests in seconds
# TYPE geosentinel_http_request_duration_seconds counter
geosentinel_http_request_duration_seconds {HTTP_REQUEST_DURATION_SUM:.4f}

# HELP geosentinel_http_average_latency_seconds Average HTTP request latency in seconds
# TYPE geosentinel_http_average_latency_seconds gauge
geosentinel_http_average_latency_seconds {avg_duration:.4f}

# HELP geosentinel_websocket_active_connections Current active WebSocket alert subscriber connections
# TYPE geosentinel_websocket_active_connections gauge
geosentinel_websocket_active_connections {ws_conns}

# HELP geosentinel_corporate_assets_monitored_total Total corporate assets monitored under active geofences
# TYPE geosentinel_corporate_assets_monitored_total gauge
geosentinel_corporate_assets_monitored_total {assets_count}

# HELP geosentinel_articles_indexed_total Total OSINT articles stored and deduplicated
# TYPE geosentinel_articles_indexed_total gauge
geosentinel_articles_indexed_total {art_count}

# HELP geosentinel_events_classified_total Total NLP classified geopolitical events
# TYPE geosentinel_events_classified_total gauge
geosentinel_events_classified_total {evt_count}

# HELP geosentinel_alerts_triggered_total Total critical risk threshold alerts dispatched
# TYPE geosentinel_alerts_triggered_total counter
geosentinel_alerts_triggered_total {alert_count}
"""
    return Response(content=metrics_text, media_type="text/plain; version=0.0.4; charset=utf-8")

