import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database.session import init_db, async_session_factory
from app.models.event import Event
from app.models.article import Article
from app.models.corporate_asset import CorporateAssetModel
from app.models.playbook import PlaybookModel
from app.models.report import ReportModel
from app.models.risk_history import RiskScoreHistory
from sqlalchemy import select

@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()

@pytest.mark.asyncio
async def test_get_event_by_id_bug_fixed():
    """Verify GET /events/{event_id} unpacks row properly without NameError."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # First query events list to get an event_id
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
            # If no events in DB, non-existent event returns 404 cleanly
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
async def test_corporate_assets_db_persistence():
    """Verify creating, querying, and deleting assets persists in the database."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # List assets (seeds DB if empty)
        res = await client.get("/api/assets")
        assert res.status_code == 200
        assets = res.json()
        assert len(assets) >= 6

        # Create new asset
        new_payload = {
            "name": "Integration Test Defense Depot",
            "asset_type": "SUPPLY_DEPOT",
            "country_iso": "IND",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "buffer_radius_km": 180.0,
            "criticality": "TIER_1_MISSION_CRITICAL",
            "description": "Strategic logistics hub for automated verification test.",
        }
        create_res = await client.post("/api/assets", json=new_payload)
        assert create_res.status_code == 201
        created = create_res.json()
        assert created["name"] == new_payload["name"]
        asset_id = created["asset_id"]

        # Verify threat assessment detail
        detail_res = await client.get(f"/api/assets/{asset_id}/threat-assessment")
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert detail["asset"]["asset_id"] == asset_id
        assert "geofence_status" in detail

        # Verify DB model existence
        async with async_session_factory() as session:
            stmt = select(CorporateAssetModel).where(CorporateAssetModel.asset_id == asset_id)
            db_obj = (await session.execute(stmt)).scalars().first()
            assert db_obj is not None
            assert db_obj.name == new_payload["name"]

        # Delete asset
        del_res = await client.delete(f"/api/assets/{asset_id}")
        assert del_res.status_code == 200

        # Verify removed from DB
        async with async_session_factory() as session:
            stmt = select(CorporateAssetModel).where(CorporateAssetModel.asset_id == asset_id)
            db_obj = (await session.execute(stmt)).scalars().first()
            assert db_obj is None

@pytest.mark.asyncio
async def test_playbooks_db_persistence():
    """Verify playbooks are loaded from database with full action plans."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/playbooks")
        assert res.status_code == 200
        playbooks = res.json()
        assert len(playbooks) >= 3

        # Query specific playbook
        pb_id = playbooks[0]["playbook_id"]
        single_res = await client.get(f"/api/playbooks/{pb_id}")
        assert single_res.status_code == 200
        single_pb = single_res.json()
        assert single_pb["playbook_id"] == pb_id
        assert len(single_pb["prescriptive_action_plan"]) >= 3

@pytest.mark.asyncio
async def test_reports_db_persistence():
    """Verify generated intelligence dossiers are persisted in DB."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        gen_res = await client.post("/api/reports/generate", json={"country_iso": "TWN"})
        assert gen_res.status_code == 200
        dossier = gen_res.json()
        report_id = dossier["report_id"]
        assert dossier["country_iso"] == "TWN"

        # Retrieve dossier by ID
        fetch_res = await client.get(f"/api/reports/{report_id}")
        assert fetch_res.status_code == 200
        assert fetch_res.json()["report_id"] == report_id

        # Check DB table
        async with async_session_factory() as session:
            stmt = select(ReportModel).where(ReportModel.report_id == report_id)
            rep_obj = (await session.execute(stmt)).scalars().first()
            assert rep_obj is not None
            assert rep_obj.country_iso == "TWN"

@pytest.mark.asyncio
async def test_country_history_grounded_trajectory():
    """Verify country history endpoint returns structured time series with category points."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/countries/UKR/history?days=14")
        assert res.status_code == 200
        history = res.json()
        assert len(history) == 14
        for pt in history:
            assert "timestamp" in pt
            assert "risk_score" in pt
            assert "conflict_share" in pt
            assert 0.0 <= pt["risk_score"] <= 100.0

@pytest.mark.asyncio
async def test_rbac_authorization_policies():
    """Verify RBAC denies operations lacking appropriate permissions when authenticated."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Officer login (role: WATCH_OFFICER, permissions: ["read"])
        officer_login = await client.post("/api/auth/token", data={"username": "officer", "password": "officer123"})
        assert officer_login.status_code == 200
        officer_token = officer_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {officer_token}"}

        # Officer trying to trigger ingestion (requires "ingest") -> 403 Forbidden
        ingest_res = await client.post("/api/ingestion/run", headers=headers)
        assert ingest_res.status_code == 403

        # Officer trying to run simulation (requires "simulate") -> 403 Forbidden
        sim_res = await client.post(
            "/api/simulation/run",
            headers=headers,
            json={
                "country_iso": "UKR",
                "scenario_title": "Test Strike",
                "category": "CONFLICT",
                "sentiment": -0.8,
                "credibility": 0.9,
                "injected_incidents_count": 2,
            },
        )
        assert sim_res.status_code == 403

        # Admin login (role: ADMINISTRATOR, full permissions)
        admin_login = await client.post("/api/auth/token", data={"username": "admin", "password": "admin123"})
        assert admin_login.status_code == 200
        admin_token = admin_login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # Admin simulation succeeds
        admin_sim = await client.post(
            "/api/simulation/run",
            headers=admin_headers,
            json={
                "country_iso": "UKR",
                "scenario_title": "Authorized Admin Simulation",
                "category": "CONFLICT",
                "sentiment": -0.8,
                "credibility": 0.9,
                "injected_incidents_count": 2,
            },
        )
        assert admin_sim.status_code == 200

