import json
from typing import Dict, Any, List

def format_risk_explanation(country_name: str, risk_data: Dict[str, Any], event_details: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generates a transparent, auditable breakdown of a country's risk score.
    """
    factors = risk_data.get("contributing_factors", {})
    if isinstance(factors, str):
        try:
            factors = json.loads(factors)
        except Exception:
            factors = {}
    if not isinstance(factors, dict):
        factors = {}
    risk_index = risk_data.get("risk_index", 0.0)
    risk_tier = risk_data.get("risk_tier", "Low")
    event_count = risk_data.get("event_count", 0)

    narrative = [
        f"{country_name} currently has a risk score of {risk_index:.1f}/100 ({risk_tier} Tier) derived from {event_count} active geopolitical events across the 30-day monitoring window.",
        f"Domain Contributions: Conflict (+{factors.get('conflict_score', 0):.1f} pts), Security (+{factors.get('security_score', 0):.1f} pts), Economy (+{factors.get('economy_score', 0):.1f} pts), Diplomacy (+{factors.get('diplomacy_score', 0):.1f} pts).",
        f"Temporal Decay: Applied continuous 7-day half-life decay (lambda = 0.0990 day^-1), resulting in an average temporal freshness retention of {factors.get('temporal_decay_factor', 1.0)*100:.1f}%.",
        f"Sentiment Modulation: Average absolute sentiment polarity magnitude is {factors.get('sentiment_magnitude', 0):.2f}.",
    ]

    return {
        "country_name": country_name,
        "risk_index": risk_index,
        "risk_tier": risk_tier,
        "event_count": event_count,
        "category_breakdown": {
            "Conflict": factors.get("conflict_score", 0),
            "Security": factors.get("security_score", 0),
            "Economy": factors.get("economy_score", 0),
            "Diplomacy": factors.get("diplomacy_score", 0),
        },
        "temporal_retention_pct": round(factors.get("temporal_decay_factor", 1.0) * 100, 1),
        "sentiment_magnitude": factors.get("sentiment_magnitude", 0),
        "narrative": narrative,
        "contributing_events": event_details or [],
    }
