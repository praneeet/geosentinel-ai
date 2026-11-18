from fastapi import APIRouter
from app.api.endpoints import (
    health,
    articles,
    events,
    countries,
    risk,
    trends,
    alerts,
    ingestion,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["System Health"])
api_router.include_router(articles.router, tags=["Articles & Deduplication"])
api_router.include_router(events.router, tags=["Geopolitical Events"])
api_router.include_router(countries.router, tags=["Countries & Risk Indices"])
api_router.include_router(risk.router, tags=["Geospatial Risk Map"])
api_router.include_router(trends.router, tags=["Trends & Aggregations"])
api_router.include_router(alerts.router, tags=["Alerts & Thresholds"])
api_router.include_router(ingestion.router, tags=["ETL Ingestion Pipeline"])
