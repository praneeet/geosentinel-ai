import math
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple

class ForecastingEngine:
    """
    Experimental Trend-Based Forecasting Engine.
    Employs Holt's Linear Exponential Smoothing (Level + Trend) with dampening
    and expanding uncertainty bands for forward risk projection.
    Explicitly labeled as experimental decision-support proof-of-concept.
    """

    def __init__(self, alpha: float = 0.35, beta: float = 0.20, phi: float = 0.88):
        self.alpha = alpha  # Level smoothing factor
        self.beta = beta    # Trend smoothing factor
        self.phi = phi      # Trend dampening factor

    def _fit_holt_linear(self, series: List[float]) -> Tuple[float, float]:
        if len(series) < 2:
            return (series[-1] if series else 25.0), 0.0

        # Initialize level and trend
        level = series[0]
        trend = series[1] - series[0]

        for val in series[1:]:
            last_level = level
            level = self.alpha * val + (1 - self.alpha) * (level + trend)
            trend = self.beta * (level - last_level) + (1 - self.beta) * trend

        return level, trend

    def generate_forecast(
        self,
        current_risk: float,
        history_points: Optional[List[float]] = None,
        days: int = 7,
    ) -> List[Dict[str, Any]]:
        """
        Projects experimental risk trend for subsequent N days.
        Provides projected score and uncertainty bounds [lower_bound, upper_bound].
        """
        now = datetime.now(timezone.utc)
        results = []

        # Use historical points if available, otherwise synthesize recent momentum
        if history_points and len(history_points) >= 3:
            pts = list(history_points) + [current_risk]
            level, trend = self._fit_holt_linear(pts)
        else:
            level = current_risk
            trend = 0.40 if current_risk > 50.0 else -0.15

        cumulative_trend = 0.0
        for step in range(1, days + 1):
            future_date = now + timedelta(days=step)

            # Damped trend component
            damp_weight = (self.phi ** step)
            cumulative_trend += trend * damp_weight
            projected = level + cumulative_trend

            # Strictly bound projected risk within [0.0, 100.0]
            projected = max(0.0, min(100.0, round(projected, 2)))

            # Expanding uncertainty bounds over the forecast horizon
            uncertainty = round(1.2 * math.sqrt(step), 2)
            lower = max(0.0, round(projected - uncertainty, 2))
            upper = min(100.0, round(projected + uncertainty, 2))

            results.append({
                "timestamp": future_date.isoformat(),
                "forecast_risk": projected,
                "lower_bound": lower,
                "upper_bound": upper,
                "model_type": "Holt's Damped Linear Exponential Smoothing",
                "is_experimental": True,
            })

        return results

forecasting_engine = ForecastingEngine()
