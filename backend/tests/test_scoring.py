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
    # Closed-form Asymptotic Hazard Saturation:
    # R_c(t) = 100 * (1 - exp(-gamma * sum_decayed))
    # sum_decayed = 1.00 * 0.80 * 1.00 * 1.0 = 0.80
    # R = 100 * (1 - exp(-0.07 * 0.80)) = 5.45
    assert 4.0 <= res["risk_index"] <= 7.0
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
    engine = RiskScoringEngine(gamma=0.20)  # calibrated or high saturation scalar
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

def test_positive_vs_negative_sentiment_separation():
    """Verify positive de-escalation does not create artificial risk spikes."""
    engine = RiskScoringEngine()
    now = datetime.now(timezone.utc)

    # Positive event (peace accord, de-escalation: sentiment = +0.90)
    pos_decayed, _, _ = engine.calculate_single_event_weight(
        category="DIPLOMACY",
        sentiment=0.90,
        severity=0.80,
        credibility=1.0,
        event_time=now,
        current_time=now,
    )

    # Negative event (crisis, shelling: sentiment = -0.90)
    neg_decayed, _, _ = engine.calculate_single_event_weight(
        category="DIPLOMACY",
        sentiment=-0.90,
        severity=0.80,
        credibility=1.0,
        event_time=now,
        current_time=now,
    )

    assert neg_decayed > pos_decayed
    # Positive sentiment threat multiplier is (1 - 0.90)/2 = 0.05
    # Negative sentiment threat multiplier is (1 - (-0.90))/2 = 0.95
    assert neg_decayed / (pos_decayed + 1e-9) > 10.0

def test_future_dated_events_quarantined():
    """Verify events with future timestamps are quarantined and do not inflate risk."""
    engine = RiskScoringEngine()
    now = datetime.now(timezone.utc)
    future_time = now + timedelta(days=5.0)

    res = engine.calculate_single_event_weight(
        category="CONFLICT",
        sentiment=-1.0,
        credibility=1.0,
        event_time=future_time,
        current_time=now,
    )
    decayed, raw, _ = res
    assert decayed == 0.0
    assert raw == 0.0

def test_input_dictionary_not_mutated():
    """Verify calculate_country_risk does not mutate caller's event dictionary."""
    engine = RiskScoringEngine()
    now = datetime.now(timezone.utc)
    orig_time = now - timedelta(days=2.0)
    event_dict = {
        "event_id": "test_ev",
        "category": "SECURITY",
        "sentiment": -0.5,
        "credibility": 0.9,
        "timestamp": orig_time,
    }
    events = [event_dict]
    _ = engine.calculate_country_risk(events, current_time=now)
    assert event_dict["timestamp"] == orig_time
    assert "timestamp_utc" not in event_dict

def test_category_contributions_sum_matches_final_risk():
    """Verify sum of category contribution scores precisely matches final risk index."""
    engine = RiskScoringEngine()
    now = datetime.now(timezone.utc)
    events = [
        {"event_id": "e1", "category": "CONFLICT", "sentiment": -0.8, "severity": 0.9, "credibility": 0.9, "timestamp": now},
        {"event_id": "e2", "category": "SECURITY", "sentiment": -0.6, "severity": 0.7, "credibility": 0.85, "timestamp": now - timedelta(days=3)},
        {"event_id": "e3", "category": "ECONOMY", "sentiment": -0.4, "severity": 0.5, "credibility": 0.8, "timestamp": now - timedelta(days=5)},
        {"event_id": "e4", "category": "DIPLOMACY", "sentiment": -0.3, "severity": 0.4, "credibility": 0.9, "timestamp": now - timedelta(days=1)},
    ]
    res = engine.calculate_country_risk(events, current_time=now)
    cf = res["contributing_factors"]
    cat_sum = round(cf["conflict_score"] + cf["security_score"] + cf["economy_score"] + cf["diplomacy_score"], 2)
    assert cat_sum == res["risk_index"]

def test_invalid_and_missing_data_handled_safely():
    """Verify engine handles malformed, None, or empty event items safely."""
    engine = RiskScoringEngine()
    now = datetime.now(timezone.utc)
    malformed = [
        None,
        {},
        {"category": "INVALID", "sentiment": "bad", "timestamp": None},
        {"category": "CONFLICT", "sentiment": -0.8, "timestamp": "not-a-datetime"},
        {"category": "SECURITY", "sentiment": -0.5, "credibility": "high", "timestamp": now},
    ]
    res = engine.calculate_country_risk(malformed, current_time=now)
    assert isinstance(res["risk_index"], float)
    assert res["risk_index"] >= 0.0
    assert res["event_count"] == 1
