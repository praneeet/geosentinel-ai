import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.session import init_db, async_session_factory
from app.api.router import api_router
from app.api.websockets.alerts_ws import router as ws_router
from app.ingestion.service import ingestion_service
from app.models.article import Article
from app.models.corporate_asset import CorporateAssetModel
from app.models.playbook import PlaybookModel
from app.api.endpoints.assets import INITIAL_CORPORATE_ASSETS
from app.api.endpoints.playbooks import ENTERPRISE_PLAYBOOKS
from sqlalchemy import select, func

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("geosentinel.main")

import asyncio

async def scheduled_ingestion_worker():
    """Background polling loop executing multi-source ingestion every N minutes."""
    interval_seconds = max(60, settings.POLLING_INTERVAL_MINUTES * 60)
    logger.info(f"Background ingestion worker active (Interval: {settings.POLLING_INTERVAL_MINUTES} min).")
    while True:
        try:
            await asyncio.sleep(interval_seconds)
            logger.info("Triggering scheduled background ingestion cycle...")
            async with async_session_factory() as session:
                await ingestion_service.run_pipeline(session)
        except asyncio.CancelledError:
            logger.info("Background ingestion worker task cancelled.")
            break
        except Exception as e:
            logger.error(f"Error in background ingestion scheduler: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup & shutdown events."""
    logger.info("Initializing GeoSentinel AI schema...")
    await init_db()
    logger.info("Database schema initialized successfully.")

    # In DEMO_MODE or clean startup, seed demo data if empty
    async with async_session_factory() as session:
        # Seed default corporate assets if empty
        try:
            asset_cnt = (await session.execute(select(func.count(CorporateAssetModel.asset_id)))).scalar() or 0
            if asset_cnt == 0:
                for a in INITIAL_CORPORATE_ASSETS:
                    session.add(CorporateAssetModel(
                        asset_id=a["asset_id"],
                        name=a["name"],
                        asset_type=a["asset_type"],
                        country_iso=a["country_iso"],
                        latitude=a["latitude"],
                        longitude=a["longitude"],
                        buffer_radius_km=a["buffer_radius_km"],
                        criticality=a["criticality"],
                        description=a.get("description"),
                        prescriptive_directive=a["prescriptive_directive"],
                    ))
                await session.commit()
                logger.info("Initialized corporate assets registry in database.")
        except Exception as e:
            logger.warning(f"Asset seeding note: {e}")

        # Seed default operational playbooks if empty
        try:
            pb_cnt = (await session.execute(select(func.count(PlaybookModel.playbook_id)))).scalar() or 0
            if pb_cnt == 0:
                for p in ENTERPRISE_PLAYBOOKS:
                    session.add(PlaybookModel(
                        playbook_id=p["playbook_id"],
                        title=p["title"],
                        category=p["category"],
                        trigger_threshold=p["trigger_threshold"],
                        threat_theater=p["threat_theater"],
                        executive_summary=p["executive_summary"],
                        quantified_impact=p["quantified_impact"],
                        recommended_option=p["recommended_option"],
                        prescriptive_action_plan=p["prescriptive_action_plan"],
                        bimco_legal_clauses=p["bimco_legal_clauses"],
                    ))
                await session.commit()
                logger.info("Initialized operational playbooks registry in database.")
        except Exception as e:
            logger.warning(f"Playbook seeding note: {e}")

        count_res = await session.execute(select(func.count(Article.article_id)))
        art_count = count_res.scalar() or 0
        if art_count == 0 and settings.DEMO_MODE:
            logger.info("Database empty with DEMO_MODE=True. Seeding initial baseline OSINT dataset...")
            try:
                res = await ingestion_service.run_pipeline(session)
                logger.info(f"Demo seeding complete: {res.get('unique_articles_saved')} articles saved, {res.get('events_created')} events created.")
            except Exception as e:
                logger.error(f"Seeding error: {e}")

    # Launch background autonomous ingestion worker conditionally
    worker_task = None
    if settings.ENABLE_IN_APP_SCHEDULER and (settings.ENVIRONMENT != "production" or settings.DEMO_MODE):
        worker_task = asyncio.create_task(scheduled_ingestion_worker())
    else:
        logger.info("In-app background scheduler disabled. Celery worker manages periodic ingestion.")

    yield

    # Clean shutdown
    if worker_task:
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass
    logger.info("GeoSentinel AI shutting down.")

app = FastAPI(
    title=settings.FULL_TITLE,
    description=(
        "Enterprise-grade REST & WebSocket API for real-time geopolitical threat "
        "intelligence, corporate asset geofencing, transparent mathematical risk scoring, "
        "and automated decision-maker playbooks.\n\n"
        "**Platform**: GeoSentinel Enterprise Threat Operations Center (GTOC)\n"
        "**Core Capabilities**: Asset Proximity Monitoring, Maritime Chokepoint Defense, "
        "Two-Stage Deduplication (SHA-256 + MinHash 128 LSH), 7-Day Half-Life Decay Scoring, "
        "and Actionable Supply Chain Continuity Playbooks.\n"
        "**Scoring Formula**: R_c(t) = min(100, (alpha / N) * sum(w_i * |S_i| * c_i * exp(-lambda * delta_t)))"
    ),
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import time
from app.api.endpoints.metrics import record_http_metric

@app.middleware("http")
async def security_and_telemetry_middleware(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Record Prometheus telemetry metrics
    record_http_metric(duration)
    
    # Security Compliance Headers
    response.headers["X-Process-Time-Sec"] = f"{duration:.4f}"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(self), camera=(), microphone=()"
    if settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' data: https: blob:; "
            "style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline'; "
            "connect-src 'self' ws: wss: http: https:;"
        )
        
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    if settings.ENVIRONMENT == "production" and not settings.DEBUG:
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal operational error occurred. Please contact system administrator."},
        )
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

# Mount REST API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount WebSocket Router
app.include_router(ws_router)

@app.get("/")
async def root():
    return {
        "platform": settings.PROJECT_NAME,
        "title": settings.FULL_TITLE,
        "edition": settings.PROJECT_GROUP,
        "documentation": "/docs",
        "health": f"{settings.API_V1_STR}/health",
        "metrics": f"{settings.API_V1_STR}/metrics",
        "risk_map": f"{settings.API_V1_STR}/risk/map",
        "demo_mode": settings.DEMO_MODE,
    }
