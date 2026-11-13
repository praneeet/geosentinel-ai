from fastapi import APIRouter
from app.api.endpoints import (
    health,
    metrics,
    auth,
    articles,
    events,
    countries,
    risk,
    trends,
    alerts,
    ingestion,
    reports,
    simulation,
    chat,
    assets,
    playbooks,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["System Health & Diagnostics"])
api_router.include_router(metrics.router, tags=["Prometheus Telemetry & Metrics"])
api_router.include_router(auth.router, tags=["Authentication & RBAC"])
api_router.include_router(assets.router, tags=["Corporate Assets & Geofencing"])
api_router.include_router(playbooks.router, tags=["Operational Mitigation Playbooks"])
api_router.include_router(articles.router, tags=["Articles & Deduplication"])
api_router.include_router(events.router, tags=["Geopolitical Events"])
api_router.include_router(countries.router, tags=["Countries & Risk Indices"])
api_router.include_router(risk.router, tags=["Geospatial Risk Map"])
api_router.include_router(trends.router, tags=["Trends & Aggregations"])
api_router.include_router(alerts.router, tags=["Alerts & Thresholds"])
api_router.include_router(ingestion.router, tags=["ETL Ingestion Pipeline"])
api_router.include_router(reports.router, tags=["Intelligence Dossiers"])
api_router.include_router(simulation.router, tags=["What-If Scenario Simulation"])
api_router.include_router(chat.router, tags=["AI Intelligence Copilot"])
