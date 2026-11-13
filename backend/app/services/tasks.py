"""
GeoSentinel Enterprise - Background Task Worker (Celery & Async)
Provides background tasks for automated scheduled news ingestion,
deduplication window signature purging, and periodic risk recalculation.
GeoSentinel Global Threat Operations Center (GTOC)
"""
import asyncio
import logging
from typing import Dict, Any

from app.config import settings

logger = logging.getLogger("geosentinel.tasks")

# Initialize Celery app
try:
    from celery import Celery
    celery_app = Celery(
        "geosentinel",
        broker=settings.CELERY_BROKER_URL,
        backend=settings.CELERY_RESULT_BACKEND,
    )
    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )
except ImportError:
    celery_app = None
    logger.warning("Celery not installed or unavailable. Background worker will operate in standalone async mode.")

def run_async(coro):
    """Utility helper to execute async coroutines inside synchronous Celery worker threads."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

async def _async_ingestion_task() -> Dict[str, Any]:
    from app.database.session import async_session_factory
    from app.ingestion.service import ingestion_service
    async with async_session_factory() as session:
        result = await ingestion_service.run_pipeline(session)
        logger.info(f"Ingestion cycle complete: {result}")
        return result

async def _async_cleanup_task() -> Dict[str, Any]:
    from app.deduplication.minhash_lsh import deduplicator
    deduplicator.cleanup_old_window()
    logger.info("MinHash LSH signature window cleaned up successfully.")
    return {"status": "success", "action": "cleanup_old_window"}

if celery_app:
    @celery_app.task(name="app.services.tasks.run_ingestion_cycle")
    def run_ingestion_cycle():
        """Celery task: Executes scheduled multi-source ingestion & risk scoring."""
        logger.info("[Celery Worker] Triggering automated ingestion cycle...")
        return run_async(_async_ingestion_task())

    @celery_app.task(name="app.services.tasks.cleanup_old_dedup_signatures")
    def cleanup_old_dedup_signatures():
        """Celery task: Purges signatures older than 48 hours."""
        logger.info("[Celery Worker] Purging expired LSH deduplication signatures...")
        return run_async(_async_cleanup_task())
else:
    def run_ingestion_cycle():
        return run_async(_async_ingestion_task())

    def cleanup_old_dedup_signatures():
        return run_async(_async_cleanup_task())
