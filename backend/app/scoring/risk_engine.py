import math
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Tuple, Optional
from app.config import settings

logger = logging.getLogger("geosentinel.scoring.risk_engine")

class RiskScoringEngine:
    """
    Implements the explainable closed-form mathematical country risk equation:
    R_c(t) = 100 * (1 - exp(-gamma * sum(w_i * S_eff,i * c_s,i * exp(-lambda * (t - t_i)))))

    Where:
      - T = 30 days sliding observation window
      - gamma = 0.07 (calibrated asymptotic crisis saturation scalar)
      - lambda = ln(2)/7 (continuous 7-day half-life decay rate ~0.099021 day^-1)
      - w_i = domain severity weight:
          Conflict: 1.00
          Security: 0.80
          Economy:  0.55
          Diplomacy: 0.35
      - S_eff,i = effective threat contribution derived from event severity Sev_i in [0.0, 1.0]
                  and sentiment polarity S_i in [-1.0, +1.0]:
                  S_eff,i = Sev_i * ((1 - S_i) / 2)
                  Negative sentiment amplifies hazard contribution.
                  Positive de-escalatory sentiment produces minimal to zero risk.
      - c_s,i = source credibility in [0.1, 1.0]
      - Bounded strictly within [0.0, 100.0] via natural exponential hazard saturation
    """

    def __init__(
        self,
        gamma: float = getattr(settings, "GAMMA_SCALAR", 0.07),
        lambda_decay: float = settings.LAMBDA_DECAY,
        window_days: int = settings.OBSERVATION_WINDOW_DAYS,
        weights: Optional[Dict[str, float]] = None,
        alpha: Optional[float] = None,
    ):
        self.gamma = gamma
        self.lambda_decay = lambda_decay
        self.window_days = window_days
        self.weights = weights or dict(settings.CATEGORY_WEIGHTS)
        self._legacy_alpha = alpha or getattr(settings, "ALPHA_SCALAR", 4.25)

    @property
    def alpha(self) -> float:
        """Maintains backwards compatibility for legacy inspection."""
        return self._legacy_alpha

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
        severity: Optional[float] = None,
    ) -> Tuple[float, float, float]:
        """
        Calculates the decayed score component for a single event:
        Returns: (decayed_contribution, raw_contribution, decay_factor)
        """
        cat_upper = category.upper() if category else "SECURITY"
        w_i = self.weights.get(cat_upper, 0.50)

        # 1. Source Credibility validation [0.1, 1.0]
        try:
            c_i = max(0.10, min(1.0, float(credibility)))
        except (ValueError, TypeError):
            c_i = 0.85

        # 2. Sentiment polarity S_i in [-1.0, +1.0]
        try:
            s_val = max(-1.0, min(1.0, float(sentiment)))
        except (ValueError, TypeError):
            s_val = -0.20

        # 3. Event Severity Sev_i in [0.0, 1.0] (defaults to 1.0 if not specified)
        if severity is not None:
            try:
                sev_val = max(0.0, min(1.0, float(severity)))
            except (ValueError, TypeError):
                sev_val = 1.0
        else:
            sev_val = 1.0

        # 4. Asymmetric threat scaling separating sentiment polarity from severity:
        # S_i = -1.0 (kinetic crisis/disaster) -> threat_multiplier = 1.0 (full severity)
        # S_i =  0.0 (neutral baseline)       -> threat_multiplier = 0.5 (half severity)
        # S_i = +1.0 (positive de-escalation) -> threat_multiplier = 0.0 (zero threat)
        threat_multiplier = max(0.0, min(1.0, (1.0 - s_val) / 2.0))
        s_eff = sev_val * threat_multiplier

        # 5. Temporal delta in fractional days (UTC normalized)
        if event_time.tzinfo is None:
            e_time = event_time.replace(tzinfo=timezone.utc)
        else:
            e_time = event_time.astimezone(timezone.utc)

        if current_time.tzinfo is None:
            c_time = current_time.replace(tzinfo=timezone.utc)
        else:
            c_time = current_time.astimezone(timezone.utc)

        delta_seconds = (c_time - e_time).total_seconds()

        # Reject or quarantine future-dated events (allow up to 60s clock skew)
        if delta_seconds < -60.0:
            logger.warning(
                f"Quarantined future-dated event: timestamp={e_time.isoformat()} "
                f"ahead of current={c_time.isoformat()} by {-delta_seconds:.1f}s"
            )
            return 0.0, 0.0, 0.0

        delta_seconds = max(0.0, delta_seconds)
        delta_days = delta_seconds / 86400.0

        # 6. Continuous 7-day half-life decay: exp(-lambda * delta_t)
        decay_factor = math.exp(-self.lambda_decay * delta_days)
        raw_component = w_i * s_eff * c_i
        decayed_component = raw_component * decay_factor

        return decayed_component, raw_component, decay_factor

    def calculate_country_risk(
        self,
        events_data: List[Dict[str, Any]],
        current_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Calculates aggregate country risk index and complete explainability factors.
        events_data item:
            {
                'event_id': str,
                'category': str,
                'sentiment': float,
                'severity': Optional[float],
                'credibility': float,
                'timestamp': datetime
            }
        """
        now = current_time or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        else:
            now = now.astimezone(timezone.utc)

        empty_result = {
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

        if not events_data:
            return empty_result

        # Filter events strictly within observation window [0, T] days without mutating input
        window_seconds = self.window_days * 86400.0
        active_events = []

        for ev in events_data:
            if not isinstance(ev, dict):
                continue
            ts = ev.get("timestamp")
            if not ts or not isinstance(ts, datetime):
                continue

            if ts.tzinfo is None:
                ts_utc = ts.replace(tzinfo=timezone.utc)
            else:
                ts_utc = ts.astimezone(timezone.utc)

            elapsed_sec = (now - ts_utc).total_seconds()
            # Discard future events beyond 60s tolerance and events older than 30 days
            if -60.0 <= elapsed_sec <= window_seconds:
                # Store normalized copy
                ev_copy = dict(ev)
                ev_copy["timestamp_utc"] = ts_utc
                active_events.append(ev_copy)

        if not active_events:
            return empty_result

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
            cat = str(ev.get("category", "SECURITY")).upper()
            decayed_c, raw_c, decay_f = self.calculate_single_event_weight(
                category=cat,
                sentiment=ev.get("sentiment", 0.0),
                severity=ev.get("severity"),
                credibility=ev.get("credibility", 0.90),
                event_time=ev["timestamp_utc"],
                current_time=now,
            )
            sum_decayed += decayed_c
            sum_raw += raw_c

            if cat in cat_sums:
                cat_sums[cat] += decayed_c
            else:
                cat_sums["SECURITY"] += decayed_c

            sentiment_mags.append(abs(float(ev.get("sentiment", 0.0))))
            decay_factors.append(decay_f)
            if ev.get("event_id"):
                event_impacts.append((ev.get("event_id"), decayed_c))

        # Closed-form Asymptotic Hazard Saturation Formulation:
        # R_c(t) = 100 * (1 - exp(-gamma * sum_decayed))
        # Mathematically guaranteed strictly in [0.0, 100.0]
        if sum_decayed <= 0.0:
            final_risk = 0.0
        else:
            final_risk = round(100.0 * (1.0 - math.exp(-self.gamma * sum_decayed)), 2)
            final_risk = max(0.0, min(100.0, final_risk))

        tier = self.get_tier(final_risk)
        critical = self.is_critical_alert(final_risk)

        # Sort top contributing event IDs
        event_impacts.sort(key=lambda x: x[1], reverse=True)
        top_ids = [eid for eid, _ in event_impacts[:5] if eid]

        # Calculate category point distributions guaranteed to sum to final_risk
        total_cat_sum = sum(cat_sums.values())
        if total_cat_sum > 0.0 and final_risk > 0.0:
            conf_pts = round((cat_sums["CONFLICT"] / total_cat_sum) * final_risk, 2)
            sec_pts = round((cat_sums["SECURITY"] / total_cat_sum) * final_risk, 2)
            econ_pts = round((cat_sums["ECONOMY"] / total_cat_sum) * final_risk, 2)
            dip_pts = round((cat_sums["DIPLOMACY"] / total_cat_sum) * final_risk, 2)

            # Reconcile any 0.01-0.02 rounding residual so category sum matches final_risk exactly
            residual = round(final_risk - (conf_pts + sec_pts + econ_pts + dip_pts), 2)
            if residual != 0.0:
                highest_cat = max(cat_sums, key=cat_sums.get)
                if highest_cat == "CONFLICT":
                    conf_pts = round(conf_pts + residual, 2)
                elif highest_cat == "SECURITY":
                    sec_pts = round(sec_pts + residual, 2)
                elif highest_cat == "ECONOMY":
                    econ_pts = round(econ_pts + residual, 2)
                else:
                    dip_pts = round(dip_pts + residual, 2)
        else:
            conf_pts = sec_pts = econ_pts = dip_pts = 0.0

        category_contributions = {
            "conflict_score": conf_pts,
            "security_score": sec_pts,
            "economy_score": econ_pts,
            "diplomacy_score": dip_pts,
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
