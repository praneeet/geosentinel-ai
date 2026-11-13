import pytest
from app.api.endpoints.assets import (
    haversine_distance_km,
    INITIAL_CORPORATE_ASSETS,
    CorporateAsset,
)
from app.api.endpoints.playbooks import ENTERPRISE_PLAYBOOKS, OperationalPlaybook
from app.forecasting.engine import ForecastingEngine


def test_haversine_distance_calculation():
    """Verify haversine distance precision across global coordinates."""
    # Same point distance is 0
    assert haversine_distance_km(25.0, 121.0, 25.0, 121.0) == 0.0

    # Symmetry: dist(A, B) == dist(B, A)
    d1 = haversine_distance_km(25.033, 121.565, 31.230, 121.473) # Taipei to Shanghai
    d2 = haversine_distance_km(31.230, 121.473, 25.033, 121.565)
    assert d1 == d2
    assert 650 <= d1 <= 720  # ~685 km

    # London to Paris (~340 km)
    london_paris = haversine_distance_km(51.5074, -0.1278, 48.8566, 2.3522)
    assert 320 <= london_paris <= 360


def test_enterprise_initial_assets_schema():
    """Ensure all pre-seeded corporate assets conform to Pydantic schema."""
    assert len(INITIAL_CORPORATE_ASSETS) >= 6
    for asset in INITIAL_CORPORATE_ASSETS:
        assert "asset_id" in asset
        assert "name" in asset
        assert "asset_type" in asset
        assert "country_iso" in asset
        assert "buffer_radius_km" in asset
        assert asset["buffer_radius_km"] >= 25.0
        assert -90.0 <= asset["latitude"] <= 90.0
        assert -180.0 <= asset["longitude"] <= 180.0


def test_enterprise_playbooks_schema():
    """Verify that all prescriptive operational playbooks contain quantified impacts and legal clauses."""
    assert len(ENTERPRISE_PLAYBOOKS) >= 3
    for pb in ENTERPRISE_PLAYBOOKS:
        # Pydantic validation
        validated = OperationalPlaybook(**pb)
        assert validated.playbook_id
        assert validated.quantified_impact.schedule_variance
        assert validated.quantified_impact.total_financial_variance
        assert len(validated.prescriptive_action_plan) >= 3
        assert len(validated.bimco_legal_clauses) >= 1
        assert any(
            any(kw in clause for kw in ["WAR", "BIMCO", "FORCE", "Montreal", "ISO", "NIST"])
            for clause in validated.bimco_legal_clauses
        )


def test_holt_damped_forecaster_mathematical_guarantees():
    """Verify Holt's linear trend with additive damping bounds and convergence."""
    forecaster = ForecastingEngine(alpha=0.35, beta=0.20, phi=0.88)

    # Monotonic increasing sequence
    history = [10.0, 12.0, 14.0, 16.0, 18.0, 20.0]
    forecast = forecaster.generate_forecast(current_risk=22.0, history_points=history, days=7)

    assert len(forecast) == 7
    # Trend must be positive
    assert forecast[0]["forecast_risk"] > 22.0

    # Confidence intervals widen over time
    for i in range(1, len(forecast)):
        spread_curr = forecast[i]["upper_bound"] - forecast[i]["lower_bound"]
        spread_prev = forecast[i - 1]["upper_bound"] - forecast[i - 1]["lower_bound"]
        assert spread_curr >= spread_prev
