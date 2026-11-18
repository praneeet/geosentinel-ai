import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


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
