import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_auth_login_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/auth/token",
            data={"username": "admin", "password": "admin123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "ADMINISTRATOR"
        assert data["username"] == "admin"


@pytest.mark.asyncio
async def test_auth_login_invalid_credentials():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/auth/token",
            data={"username": "admin", "password": "wrongpassword"},
        )
        assert resp.status_code == 401


@pytest.mark.asyncio
async def test_auth_roles_directory():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/auth/roles")
        assert resp.status_code == 200
        roles = resp.json()
        assert len(roles) == 3
        role_names = [r["role"] for r in roles]
        assert "ADMINISTRATOR" in role_names
        assert "SENIOR_ANALYST" in role_names
        assert "WATCH_OFFICER" in role_names


@pytest.mark.asyncio
async def test_export_risk_geojson():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/risk/export/geojson")
        assert resp.status_code == 200
        geojson = resp.json()
        assert geojson["type"] == "FeatureCollection"
        assert "features" in geojson
        assert len(geojson["features"]) > 0
        first = geojson["features"][0]
        assert first["type"] == "Feature"
        assert first["geometry"]["type"] == "Point"
        assert "properties" in first
        assert "country_iso" in first["properties"]
        assert "risk_index" in first["properties"]

@pytest.mark.asyncio
async def test_export_events_csv():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/events/export/csv")
        assert resp.status_code == 200
        assert "text/csv" in resp.headers.get("content-type", "")
        csv_text = resp.text
        assert "event_id,timestamp,country_iso,category" in csv_text
