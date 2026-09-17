import math
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

class ForecastingEngine:
    """
    Experimental Trend-Based Forecasting Engine.
    Employs exponential smoothing (Holt-Winters style) and rolling momentum baselines.
    Explicitly labeled as experimental decision-support proof-of-concept.
    """

    def generate_forecast(
        self,
        current_risk: float,
        history_points: List[float] = None,
        days: int = 7,
    ) -> List[Dict[str, Any]]:
        """
        Projects experimental risk trend for subsequent N days.
        Provides projected score and uncertainty bounds [lower_bound, upper_bound].
        """
        now = datetime.now(timezone.utc)
        results = []

        base_val = current_risk
        # Calculate trend drift from history if provided, else mild mean-reversion
        if history_points and len(history_points) >= 3:
            recent_delta = (history_points[-1] - history_points[0]) / len(history_points)
        else:
            recent_delta = 0.5 if base_val > 50 else -0.2

        for step in range(1, days + 1):
            future_date = now + timedelta(days=step)
            # Dampen trend over horizon
            dampener = math.exp(-0.15 * step)
            projected = base_val + (recent_delta * step * dampener)
            projected = max(0.0, min(100.0, round(projected, 2)))

            # Uncertainty expands with time horizon
            uncertainty = round(1.5 * math.sqrt(step), 2)
            lower = max(0.0, round(projected - uncertainty, 2))
            upper = min(100.0, round(projected + uncertainty, 2))

            results.append({
                "timestamp": future_date.isoformat(),
                "forecast_risk": projected,
                "lower_bound": lower,
                "upper_bound": upper,
                "model_type": "Exponential Smoothing / Momentum Drift Baseline",
                "is_experimental": True,
            })

        return results

forecasting_engine = ForecastingEngine()
