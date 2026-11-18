import asyncio
import logging
import signal
from app.config import settings
from app.database.session import async_session_factory, init_db
from app.ingestion.service import ingestion_service
from app.deduplication.minhash_lsh import deduplicator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("geosentinel.worker")

async def run_standalone_worker():
    """
    Dedicated background worker process.
    Isolates periodic OSINT ingestion and LSH memory management from web worker processes.
    """
    logger.info("Initializing GeoSentinel database schema in worker process...")
    await init_db()

    # 1. Warm up MinHash LSH deduplicator index
    async with async_session_factory() as session:
        warmed = await deduplicator.warmup_from_db(session)
        logger.info(f"LSH deduplicator warmed with {warmed} recent articles from DB.")

    interval_seconds = max(60, settings.POLLING_INTERVAL_MINUTES * 60)
    logger.info(f"Dedicated ingestion worker active (Interval: {settings.POLLING_INTERVAL_MINUTES} min).")

    stop_event = asyncio.Event()

    def _signal_handler():
        logger.info("Worker received termination signal. Shutting down gracefully...")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (getattr(signal, "SIGINT", None), getattr(signal, "SIGTERM", None)):
        if sig:
            try:
                loop.add_signal_handler(sig, _signal_handler)
            except (NotImplementedError, RuntimeError):
                pass  # Windows event loop may not support all signals

    while not stop_event.is_set():
        try:
            logger.info("Executing scheduled multi-source OSINT ingestion cycle...")
            deduplicator.cleanup_old_window()
            async with async_session_factory() as session:
                res = await ingestion_service.run_pipeline(session)
                logger.info(
                    f"Cycle completed: {res.get('raw_articles_fetched', 0)} fetched, "
                    f"{res.get('unique_articles_saved', 0)} saved, "
                    f"{res.get('events_created', 0)} events created."
                )
        except Exception as e:
            logger.error(f"Error in background ingestion cycle: {e}", exc_info=True)

        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval_seconds)
        except asyncio.TimeoutError:
            continue

    logger.info("GeoSentinel standalone worker exited.")

if __name__ == "__main__":
    asyncio.run(run_standalone_worker())
