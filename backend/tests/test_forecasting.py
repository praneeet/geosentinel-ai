import pytest
from datetime import datetime, timezone
from app.forecasting.engine import ForecastingEngine

def test_forecasting_engine_basic_projection():
    engine = ForecastingEngine()
    current_risk = 65.0
    history = [55.0, 58.0, 60.0, 62.0, 65.0]

    forecast = engine.generate_forecast(current_risk, history_points=history, days=7)

    assert len(forecast) == 7
    for point in forecast:
        assert "timestamp" in point
        assert "forecast_risk" in point
        assert "lower_bound" in point
        assert "upper_bound" in point
        assert 0.0 <= point["forecast_risk"] <= 100.0
        assert point["lower_bound"] <= point["forecast_risk"] <= point["upper_bound"]
        assert point["is_experimental"] is True

def test_forecasting_engine_without_history():
    engine = ForecastingEngine()
    forecast = engine.generate_forecast(current_risk=25.0, days=5)

    assert len(forecast) == 5
    for point in forecast:
        assert 0.0 <= point["forecast_risk"] <= 100.0
        assert point["lower_bound"] <= point["forecast_risk"] <= point["upper_bound"]

def test_forecasting_engine_bounds_extremes():
    engine = ForecastingEngine()
    # Extreme high risk
    forecast_high = engine.generate_forecast(current_risk=99.0, history_points=[95.0, 97.0, 99.0], days=3)
    for point in forecast_high:
        assert point["forecast_risk"] <= 100.0
        assert point["upper_bound"] <= 100.0

    # Extreme low risk
    forecast_low = engine.generate_forecast(current_risk=1.0, history_points=[5.0, 3.0, 1.0], days=3)
    for point in forecast_low:
        assert point["forecast_risk"] >= 0.0
        assert point["lower_bound"] >= 0.0
