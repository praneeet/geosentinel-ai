import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database.session import init_db


@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()


@pytest.mark.asyncio
async def test_get_event_by_id_bug_fixed():
    """Verify GET /events/{event_id} unpacks row properly without NameError."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/events?page=1&page_size=1")
        assert res.status_code == 200
        data = res.json()
        if data["events"]:
            eid = data["events"][0]["event_id"]
            single_res = await client.get(f"/api/events/{eid}")
            assert single_res.status_code == 200
            single_data = single_res.json()
            assert single_data["event_id"] == eid
            assert "article_title" in single_data
        else:
            single_res = await client.get("/api/events/nonexistent-id")
            assert single_res.status_code == 404


@pytest.mark.asyncio
async def test_alerts_pagination():
    """Verify alerts endpoint supports page and page_size parameters."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/alerts?page=1&page_size=5")
        assert res.status_code == 200
        data = res.json()
        assert "total" in data
        assert "alerts" in data
        assert len(data["alerts"]) <= 5


@pytest.mark.asyncio
async def test_alerts_webhook_status():
    """Verify webhook status endpoint reports real runtime configuration flags."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/alerts/webhooks/status")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data["webhooks_enabled"], bool)
        assert isinstance(data["discord_configured"], bool)
        assert isinstance(data["telegram_configured"], bool)


@pytest.mark.asyncio
async def test_country_history_grounded_trajectory():
    """Verify country history endpoint returns real persistent historical observations."""
    from app.database.session import async_session_factory
    from app.models.risk_history import RiskScoreHistory
    from datetime import datetime, timezone, timedelta
    import uuid

    # Seed real historical observations for UKR
    now = datetime.now(timezone.utc)
    async with async_session_factory() as session:
        for d in range(7, 0, -1):
            h = RiskScoreHistory(
                history_id=str(uuid.uuid4()),
                country_iso="UKR",
                risk_index=65.0 - d * 1.5,
                risk_tier="Severe" if (65.0 - d * 1.5) > 60 else "Moderate",
                event_count=5 + d,
                contributing_factors={"conflict_score": 30.0, "security_score": 15.0},
                recorded_at=now - timedelta(days=d),
            )
            session.add(h)
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/countries/UKR/history?days=14")
        assert res.status_code == 200
        history = res.json()
        assert len(history) >= 7
        for pt in history:
            assert "timestamp" in pt
            assert "risk_score" in pt
            assert "conflict_share" in pt
            assert 0.0 <= pt["risk_score"] <= 100.0


@pytest.mark.asyncio
async def test_country_forecast_endpoint():
    """Verify country forecast endpoint returns valid bounded projections."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/countries/UKR/forecast?days=7")
        assert res.status_code == 200
        points = res.json()
        assert len(points) == 7
        for pt in points:
            assert 0.0 <= pt["forecast_risk"] <= 100.0
            assert pt["lower_bound"] <= pt["forecast_risk"] <= pt["upper_bound"]
