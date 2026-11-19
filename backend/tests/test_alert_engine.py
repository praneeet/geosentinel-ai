import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func
from app.config import settings
from app.database.session import async_session_factory, init_db
from app.alerts.manager import alert_manager, AlertManager
from app.alerts.websocket import ws_dispatcher
from app.models.alert import Alert

@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()

@pytest.mark.asyncio
async def test_simultaneous_alert_generation_mutex():
    """
    Verify simultaneous concurrent alert triggers for the same country
    generate exactly ONE persistent alert and suppress all duplicate race conditions.
    """
    iso = "UKR"
    factors = {"conflict_score": 50.0, "security_score": 35.0, "top_event_ids": ["ev1"]}

    # Clean prior alerts for UKR in DB and memory
    async with async_session_factory() as session:
        from sqlalchemy import delete
        await session.execute(delete(Alert).where(Alert.country_iso == iso))
        await session.commit()
        alert_manager._last_alerted.pop(iso, None)

    async def trigger_task():
        async with async_session_factory() as session:
            return await alert_manager.check_and_trigger(
                country_iso=iso,
                risk_score=85.0,
                tier="Severe",
                contributing_factors=factors,
                session=session,
            )

    # Launch 10 concurrent requests simultaneously
    results = await asyncio.gather(*(trigger_task() for _ in range(10)))

    # Exactly one request must succeed; 9 must return None
    triggered = [r for r in results if r is not None]
    assert len(triggered) == 1
    assert triggered[0]["country"] == iso
    assert triggered[0]["risk_score"] == 85.0

    # Verify database contains only 1 alert for this window
    async with async_session_factory() as session:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=settings.ALERT_COOLDOWN_HOURS)
        stmt = select(func.count(Alert.alert_id)).where(Alert.country_iso == iso, Alert.sent_at >= cutoff)
        count = (await session.execute(stmt)).scalar()
        assert count == 1

@pytest.mark.asyncio
async def test_sub_threshold_risk_suppressed():
    """Verify scores at or below critical threshold (R <= 75.0) do not generate alerts."""
    iso = "FRA"
    factors = {"conflict_score": 10.0, "security_score": 10.0}

    async with async_session_factory() as session:
        res = await alert_manager.check_and_trigger(
            country_iso=iso,
            risk_score=75.0,
            tier="Moderate",
            contributing_factors=factors,
            session=session,
        )
        assert res is None

@pytest.mark.asyncio
async def test_cooldown_enforcement_across_restarts():
    """Verify cooldown is strictly enforced even if in-memory cache is wiped (persistent DB check)."""
    iso = "TWN"
    factors = {"conflict_score": 45.0, "security_score": 35.0}

    async with async_session_factory() as session:
        from sqlalchemy import delete
        await session.execute(delete(Alert).where(Alert.country_iso == iso))
        await session.commit()
        alert_manager._last_alerted.pop(iso, None)
        res1 = await alert_manager.check_and_trigger(
            country_iso=iso,
            risk_score=82.0,
            tier="Severe",
            contributing_factors=factors,
            session=session,
        )
        assert res1 is not None

        # Wipe in-memory cache simulating process restart
        alert_manager._last_alerted.pop(iso, None)

        # Immediate second trigger should be suppressed by database check
        res2 = await alert_manager.check_and_trigger(
            country_iso=iso,
            risk_score=83.0,
            tier="Severe",
            contributing_factors=factors,
            session=session,
        )
        assert res2 is None

@pytest.mark.asyncio
async def test_database_transaction_failure_does_not_broadcast():
    """Verify database failure during alert creation prevents broadcast and releases lock."""
    iso = "ISR"
    factors = {"conflict_score": 50.0}

    mock_session = AsyncMock()
    mock_session.add = lambda x: None
    mock_session.execute = AsyncMock(side_effect=Exception("Database write failure"))
    mock_session.commit = AsyncMock(side_effect=Exception("Commit error"))

    with patch.object(ws_dispatcher, "broadcast_alert", new_callable=AsyncMock) as mock_broadcast:
        with pytest.raises(Exception):
            await alert_manager.check_and_trigger(
                country_iso=iso,
                risk_score=88.0,
                tier="Severe",
                contributing_factors=factors,
                session=mock_session,
            )
        # broadcast must NEVER have been called if DB commit fails
        mock_broadcast.assert_not_called()

    # Mutex lock must be released
    assert not alert_manager._lock.locked()
