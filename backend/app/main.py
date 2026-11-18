import os
import asyncio
import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func

from app.config import settings
from app.database.session import init_db, async_session_factory
from app.api.router import api_router
from app.api.websockets.alerts_ws import router as ws_router
from app.deduplication.minhash_lsh import deduplicator
from app.ingestion.service import ingestion_service
from app.models.article import Article

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("geosentinel.main")


async def scheduled_ingestion_worker():
    """Background polling loop executing multi-source ingestion and LSH window cleanup."""
    interval_seconds = max(60, settings.POLLING_INTERVAL_MINUTES * 60)
    logger.info(
        f"Background ingestion worker active (Interval: {settings.POLLING_INTERVAL_MINUTES} min)."
    )
    while True:
        try:
            await asyncio.sleep(interval_seconds)
            logger.info("Triggering scheduled background ingestion cycle...")
            deduplicator.cleanup_old_window()
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

    # Seed baseline demo dataset if empty and DEMO_MODE is enabled
    async with async_session_factory() as session:
        # Warm up MinHash LSH deduplicator with recent articles from DB
        warmed = await deduplicator.warmup_from_db(session)
        if warmed > 0:
            logger.info(f"Warmed up MinHash LSH index with {warmed} recent articles from DB.")

        count_res = await session.execute(select(func.count(Article.article_id)))
        art_count = count_res.scalar() or 0
        if art_count == 0 and settings.DEMO_MODE:
            logger.info("Database empty with DEMO_MODE=True. Seeding initial baseline OSINT dataset...")
            try:
                res = await ingestion_service.run_pipeline(session)
                logger.info(
                    f"Demo seeding complete: {res.get('unique_articles_saved')} articles saved, "
                    f"{res.get('events_created')} events created."
                )
            except Exception as e:
                logger.error(f"Seeding error: {e}")

    worker_task = None
    if settings.ENABLE_IN_APP_SCHEDULER:
        worker_task = asyncio.create_task(scheduled_ingestion_worker())
    else:
        logger.info("In-app background scheduler disabled.")

    yield

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
        "REST & WebSocket API for real-time geopolitical threat intelligence, "
        "two-stage OSINT deduplication (SHA-256 + MinHash 128 LSH), "
        "transparent mathematical country risk scoring with 7-day exponential decay, "
        "and live threshold alerting.\n\n"
        "**Scoring Formula**: R_c(t) = min(100, 100 * (1 - exp(-gamma * sum(w_i * |S_i| * c_i * exp(-lambda * delta_t)))))"
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


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    response.headers["X-Process-Time-Sec"] = f"{duration:.4f}"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
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


# Serve Production Frontend SPA if dist bundle is built
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist"))
if os.path.exists(frontend_dist) and os.path.isdir(os.path.join(frontend_dist, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/")
    async def root():
        return {
            "platform": settings.PROJECT_NAME,
            "title": settings.FULL_TITLE,
            "version": settings.VERSION,
            "documentation": "/docs",
            "health": f"{settings.API_V1_STR}/health",
            "risk_map": f"{settings.API_V1_STR}/risk/map",
            "demo_mode": settings.DEMO_MODE,
        }
