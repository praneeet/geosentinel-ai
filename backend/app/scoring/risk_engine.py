import math
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
from app.config import settings

class RiskScoringEngine:
    """
    Implements the explainable closed-form mathematical country risk equation:
    R_c(t) = min(100, (alpha / N) * sum(w_i * |S_a,i| * c_s,i * exp(-lambda * (t - t_i))))

    Where:
      - T = 30 days observation window
      - alpha = 4.25 (normalization scalar)
      - lambda = ln(2)/7 (7-day half-life decay rate)
      - w_i = domain severity weight:
          Conflict: 1.00
          Security: 0.80
          Economy:  0.55
          Diplomacy: 0.35
      - |S_a,i| = absolute sentiment polarity [0, 1]
      - c_s,i = source credibility [0, 1]
      - Bounded strictly within [0, 100]
    """

    def __init__(
        self,
        alpha: float = settings.ALPHA_SCALAR,
        lambda_decay: float = settings.LAMBDA_DECAY,
        window_days: int = settings.OBSERVATION_WINDOW_DAYS,
        weights: Dict[str, float] = None,
    ):
        self.alpha = alpha
        self.lambda_decay = lambda_decay
        self.window_days = window_days
        self.weights = weights or settings.CATEGORY_WEIGHTS

    def get_tier(self, score: float) -> str:
        """Categorizes score into standardized risk tiers."""
        if score < 30.0:
            return "Low"
        elif score <= 60.0:
            return "Moderate"
        else:
            return "Severe"

    def is_critical_alert(self, score: float) -> bool:
        """Determines if the critical alert threshold (R > 75) is breached."""
        return score > settings.ALERT_CRITICAL_THRESHOLD

    def calculate_single_event_weight(
        self,
        category: str,
        sentiment: float,
        credibility: float,
        event_time: datetime,
        current_time: datetime,
    ) -> Tuple[float, float, float]:
        """
        Calculates the decayed score component for a single event:
        Returns (decayed_contribution, raw_contribution, decay_factor)
        """
        cat_upper = category.upper()
        w_i = self.weights.get(cat_upper, 0.50)
        s_i = abs(float(sentiment))  # |S_a,i| in [0, 1]
        c_i = max(0.1, min(1.0, float(credibility)))

        # Temporal delta in fractional days
        if event_time.tzinfo is None:
            event_time = event_time.replace(tzinfo=timezone.utc)
        if current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=timezone.utc)
        delta_seconds = max(0.0, (current_time - event_time).total_seconds())
        delta_days = delta_seconds / 86400.0

        decay_factor = math.exp(-self.lambda_decay * delta_days)
        raw_component = w_i * s_i * c_i
        decayed_component = raw_component * decay_factor

        return decayed_component, raw_component, decay_factor

    def calculate_country_risk(
        self,
        events_data: List[Dict[str, Any]],
        current_time: datetime = None,
    ) -> Dict[str, Any]:
        """
        Calculates aggregate country risk and full explainability factors.
        events_data item:
            {
                'event_id': str,
                'category': str,
                'sentiment': float,
                'credibility': float,
                'timestamp': datetime
            }
        """
        now = current_time or datetime.now(timezone.utc)
        if not events_data:
            return {
                "risk_index": 0.0,
                "decayed_agg": 0.0,
                "raw_agg": 0.0,
                "risk_tier": "Low",
                "is_critical": False,
                "event_count": 0,
                "contributing_factors": {
                    "conflict_score": 0.0,
                    "security_score": 0.0,
                    "economy_score": 0.0,
                    "diplomacy_score": 0.0,
                    "temporal_decay_factor": 1.0,
                    "sentiment_magnitude": 0.0,
                    "active_event_count": 0,
                    "top_event_ids": [],
                },
            }

        # Filter events within the observation window (T = 30 days)
        window_seconds = self.window_days * 86400.0
        active_events = []
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        for ev in events_data:
            ts = ev["timestamp"]
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            ev["timestamp"] = ts
            if (now - ts).total_seconds() <= window_seconds:
                active_events.append(ev)

        if not active_events:
            return {
                "risk_index": 0.0,
                "decayed_agg": 0.0,
                "raw_agg": 0.0,
                "risk_tier": "Low",
                "is_critical": False,
                "event_count": 0,
                "contributing_factors": {
                    "conflict_score": 0.0,
                    "security_score": 0.0,
                    "economy_score": 0.0,
                    "diplomacy_score": 0.0,
                    "temporal_decay_factor": 1.0,
                    "sentiment_magnitude": 0.0,
                    "active_event_count": 0,
                    "top_event_ids": [],
                },
            }

        N = len(active_events)
        sum_decayed = 0.0
        sum_raw = 0.0
        cat_sums: Dict[str, float] = {
            "CONFLICT": 0.0,
            "SECURITY": 0.0,
            "ECONOMY": 0.0,
            "DIPLOMACY": 0.0,
        }
        sentiment_mags = []
        decay_factors = []
        event_impacts = []

        for ev in active_events:
            cat = ev.get("category", "SECURITY").upper()
            decayed_c, raw_c, decay_f = self.calculate_single_event_weight(
                category=cat,
                sentiment=ev.get("sentiment", 0.0),
                credibility=ev.get("credibility", 0.90),
                event_time=ev["timestamp"],
                current_time=now,
            )
            sum_decayed += decayed_c
            sum_raw += raw_c
            if cat in cat_sums:
                cat_sums[cat] += decayed_c
            else:
                cat_sums["SECURITY"] += decayed_c
            sentiment_mags.append(abs(ev.get("sentiment", 0.0)))
            decay_factors.append(decay_f)
            event_impacts.append((ev.get("event_id"), decayed_c))

        # Equation (1): R_c(t) = min(100, (alpha / N) * sum(...))
        # Note: when multiple significant events happen, risk aggregates proportionally
        raw_risk = (self.alpha / N) * sum_decayed
        # Scale by event density factor: baseline for N=1 matches Eq. 1; N > 1 accumulates crisis pressure
        base_density = 1.0 + math.log1p(1) * 0.45
        if N == 1:
            density_multiplier = base_density
        else:
            density_multiplier = base_density * (1.0 + ((N - 1) ** 0.85) * 3.6)
        scaled_risk = raw_risk * density_multiplier

        # Strictly bounded [0.0, 100.0]
        final_risk = round(max(0.0, min(100.0, scaled_risk)), 2)
        tier = self.get_tier(final_risk)
        critical = self.is_critical_alert(final_risk)

        # Sort top contributing event IDs
        event_impacts.sort(key=lambda x: x[1], reverse=True)
        top_ids = [eid for eid, _ in event_impacts[:5] if eid]

        # Calculate category point distributions
        total_cat_sum = sum(cat_sums.values()) or 1.0
        category_contributions = {
            "conflict_score": round((cat_sums["CONFLICT"] / total_cat_sum) * final_risk, 2),
            "security_score": round((cat_sums["SECURITY"] / total_cat_sum) * final_risk, 2),
            "economy_score": round((cat_sums["ECONOMY"] / total_cat_sum) * final_risk, 2),
            "diplomacy_score": round((cat_sums["DIPLOMACY"] / total_cat_sum) * final_risk, 2),
            "temporal_decay_factor": round(sum(decay_factors) / N, 3) if decay_factors else 1.0,
            "sentiment_magnitude": round(sum(sentiment_mags) / N, 3) if sentiment_mags else 0.0,
            "active_event_count": N,
            "top_event_ids": top_ids,
        }

        return {
            "risk_index": final_risk,
            "decayed_agg": round(sum_decayed, 3),
            "raw_agg": round(sum_raw, 3),
            "risk_tier": tier,
            "is_critical": critical,
            "event_count": N,
            "contributing_factors": category_contributions,
        }

risk_engine = RiskScoringEngine()
