import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.session import init_db, async_session_factory
from app.api.router import api_router
from app.api.websockets.alerts_ws import router as ws_router
from app.ingestion.service import ingestion_service
from app.models.article import Article
from sqlalchemy import select, func

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("geosentinel.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup & shutdown events."""
    logger.info("Initializing GeoSentinel AI schema...")
    await init_db()
    logger.info("Database schema initialized successfully.")

    # In DEMO_MODE or clean startup, seed demo data if empty
    async with async_session_factory() as session:
        count_res = await session.execute(select(func.count(Article.article_id)))
        art_count = count_res.scalar() or 0
        if art_count == 0 and settings.DEMO_MODE:
            logger.info("Database empty with DEMO_MODE=True. Seeding initial baseline OSINT dataset...")
            try:
                res = await ingestion_service.run_pipeline(session)
                logger.info(f"Demo seeding complete: {res.get('unique_articles_saved')} articles saved, {res.get('events_created')} events created.")
            except Exception as e:
                logger.error(f"Seeding error: {e}")

    yield
    logger.info("GeoSentinel AI shutting down.")

app = FastAPI(
    title=settings.FULL_TITLE,
    description=(
        "Research-grade API for AI-powered geopolitical risk intelligence, "
        "transparent mathematical risk scoring, two-stage deduplication, "
        "and real-time alert dispatching.\n\n"
        "**Institution**: Ajay Kumar Garg Engineering College, Ghaziabad\n"
        "**Department**: Information Technology (CSIT Group 32)\n"
        "**Team**: Praneet Pravin, Rishabh Dwivedi, Rudra Vikram Singh, Sumit Sharma\n"
        "**Mentor**: Mr. Anupam Saini, Assistant Professor, IT\n"
        "**Formula**: R_c(t) = min(100, (alpha / N) * sum(w_i * |S_i| * c_i * exp(-lambda * delta_t)))"
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

# Mount REST API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount WebSocket Router
app.include_router(ws_router)

@app.get("/")
async def root():
    return {
        "platform": settings.PROJECT_NAME,
        "title": settings.FULL_TITLE,
        "group": settings.PROJECT_GROUP,
        "documentation": "/docs",
        "health": f"{settings.API_V1_STR}/health",
        "risk_map": f"{settings.API_V1_STR}/risk/map",
        "demo_mode": settings.DEMO_MODE,
    }
