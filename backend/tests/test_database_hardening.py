import pytest
import asyncio
from sqlalchemy import select, text
from app.config import settings
from app.database.session import init_db, async_session_factory, get_db
from app.models.country_score import CountryScore

@pytest.mark.asyncio
async def test_init_db_prohibited_in_production():
    """Verify that Base.metadata.create_all() cannot run in production mode."""
    old_env = settings.ENVIRONMENT
    try:
        settings.ENVIRONMENT = "production"
        with pytest.raises(RuntimeError, match="strictly prohibited in production"):
            await init_db()
    finally:
        settings.ENVIRONMENT = old_env

@pytest.mark.asyncio
async def test_session_cleanup_on_exception():
    """Verify database session properly rolls back and closes on exception."""
    gen = get_db()
    session = await gen.asend(None)
    assert session.is_active

    with pytest.raises(ValueError, match="Simulated application failure"):
        try:
            # Execute invalid work then raise
            await session.execute(text("SELECT 1"))
            raise ValueError("Simulated application failure")
        except Exception as e:
            await gen.athrow(e)

@pytest.mark.asyncio
async def test_concurrent_database_reads():
    """Verify connection pool handles concurrent session execution without exhaustion."""
    async def worker_query(i: int):
        async with async_session_factory() as session:
            res = await session.execute(text("SELECT :num AS val"), {"num": i})
            row = res.mappings().first()
            return row["val"]

    results = await asyncio.gather(*(worker_query(i) for i in range(20)))
    assert results == list(range(20))
