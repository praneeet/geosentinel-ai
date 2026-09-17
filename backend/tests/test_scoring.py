import math
import pytest
from datetime import datetime, timezone, timedelta
from app.scoring.risk_engine import RiskScoringEngine

def test_zero_events_returns_zero_risk():
    engine = RiskScoringEngine()
    res = engine.calculate_country_risk([])
    assert res["risk_index"] == 0.0
    assert res["risk_tier"] == "Low"
    assert res["is_critical"] is False
    assert res["event_count"] == 0

def test_single_event_calculation():
    engine = RiskScoringEngine()
    now = datetime.now(timezone.utc)
    events = [{
        "event_id": "e1",
        "category": "CONFLICT",  # weight 1.00
        "sentiment": -0.80,      # |S| = 0.80
        "credibility": 1.00,
        "timestamp": now,        # delta_t = 0 => decay = 1.0
    }]
    res = engine.calculate_country_risk(events, current_time=now)
    # raw_risk = 4.25 / 1 * (1.00 * 0.80 * 1.00 * 1.0) = 3.4
    # density_multiplier = 1.0 + ln(2) * 0.45 = 1.3119
    # scaled = 3.4 * 1.3119 = 4.46
    assert 4.0 <= res["risk_index"] <= 6.0
    assert res["risk_tier"] == "Low"
    assert res["event_count"] == 1

def test_seven_day_half_life_temporal_decay():
    """
    Academic validation: Verify that lambda = ln(2)/7 yields exactly 50% decay
    after 7 days.
    """
    engine = RiskScoringEngine()
    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7.0)

    # Event at t=0
    decayed_now, raw_now, factor_now = engine.calculate_single_event_weight(
        category="CONFLICT",
        sentiment=-1.0,
        credibility=1.0,
        event_time=now,
        current_time=now,
    )
    assert factor_now == 1.0

    # Event at t - 7 days
    decayed_7d, raw_7d, factor_7d = engine.calculate_single_event_weight(
        category="CONFLICT",
        sentiment=-1.0,
        credibility=1.0,
        event_time=seven_days_ago,
        current_time=now,
    )
    # Expect factor_7d to be exactly 0.5 (within floating point margin)
    assert pytest.approx(factor_7d, rel=1e-4) == 0.50
    assert pytest.approx(decayed_7d, rel=1e-4) == 0.50 * decayed_now

def test_risk_score_bounded_between_zero_and_hundred():
    """Verify strictly bounded 0 <= R <= 100 even with extreme high event volume."""
    engine = RiskScoringEngine(alpha=100.0)  # artificially high alpha
    now = datetime.now(timezone.utc)
    huge_events = [
        {
            "event_id": f"ev_{i}",
            "category": "CONFLICT",
            "sentiment": -1.0,
            "credibility": 1.0,
            "timestamp": now,
        }
        for i in range(100)
    ]
    res = engine.calculate_country_risk(huge_events, current_time=now)
    assert res["risk_index"] <= 100.0
    assert res["risk_index"] >= 0.0
    assert res["risk_tier"] == "Severe"
    assert res["is_critical"] is True

def test_risk_tier_classification():
    engine = RiskScoringEngine()
    assert engine.get_tier(0.0) == "Low"
    assert engine.get_tier(29.9) == "Low"
    assert engine.get_tier(30.0) == "Moderate"
    assert engine.get_tier(60.0) == "Moderate"
    assert engine.get_tier(60.1) == "Severe"
    assert engine.get_tier(100.0) == "Severe"

def test_critical_alert_threshold():
    engine = RiskScoringEngine()
    assert engine.is_critical_alert(75.0) is False
    assert engine.is_critical_alert(75.1) is True
    assert engine.is_critical_alert(92.0) is True

def test_category_weight_hierarchy():
    """Verify Conflict (1.0) > Security (0.8) > Economy (0.55) > Diplomacy (0.35)."""
    engine = RiskScoringEngine()
    now = datetime.now(timezone.utc)

    c_score, _, _ = engine.calculate_single_event_weight("CONFLICT", -1.0, 1.0, now, now)
    s_score, _, _ = engine.calculate_single_event_weight("SECURITY", -1.0, 1.0, now, now)
    e_score, _, _ = engine.calculate_single_event_weight("ECONOMY", -1.0, 1.0, now, now)
    d_score, _, _ = engine.calculate_single_event_weight("DIPLOMACY", -1.0, 1.0, now, now)

    assert c_score > s_score > e_score > d_score
    assert c_score == 1.00
    assert s_score == 0.80
    assert e_score == 0.55
    assert d_score == 0.35
