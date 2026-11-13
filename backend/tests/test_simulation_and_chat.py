import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_simulation_templates_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/simulation/templates")
        assert resp.status_code == 200
        templates = resp.json()
        assert len(templates) >= 4
        assert any(t["country_iso"] == "YEM" for t in templates)
        assert any(t["category"] == "CONFLICT" for t in templates)

@pytest.mark.asyncio
async def test_run_simulation_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "country_iso": "YEM",
            "scenario_title": "Red Sea Missile Strike Simulation",
            "category": "CONFLICT",
            "sentiment": -0.90,
            "credibility": 0.95,
            "injected_incidents_count": 4,
            "spillover_countries": ["SAU", "EGY"],
        }
        resp = await client.post("/api/simulation/run", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["country_iso"] == "YEM"
        assert "simulated_risk" in data
        assert "risk_delta" in data
        assert len(data["projected_trajectory"]) == 7
        assert len(data["spillover_effects"]) == 2

@pytest.mark.asyncio
async def test_ai_chat_copilot_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "query": "What are the latest defense developments in Ukraine?",
            "context_country_iso": "UKR",
        }
        resp = await client.post("/api/chat", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "response_markdown" in data
        assert "Tactical Intelligence Briefing" in data["response_markdown"]
        assert "suggested_followups" in data
        assert len(data["suggested_followups"]) > 0
