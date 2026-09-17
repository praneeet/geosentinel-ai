import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database.session import init_db

@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()

@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["project"] == "GeoSentinel AI"
        assert "status" in data

@pytest.mark.asyncio
async def test_countries_list():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/countries")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        ukr = next((c for c in data if c["country_iso"] == "UKR"), None)
        assert ukr is not None
        assert ukr["country_name"] == "Ukraine"

@pytest.mark.asyncio
async def test_risk_map_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/risk/map")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert any(item["country_iso"] == "IND" for item in data)

@pytest.mark.asyncio
async def test_trends_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/trends?days=14")
        assert response.status_code == 200
        data = response.json()
        assert "category_distribution" in data
        assert "timeline" in data
