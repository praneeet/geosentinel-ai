# GeoSentinel AI - Trend-Based Forecasting Experiments

## Research Purpose & Disclaimers

> [!WARNING]
> **Forecasting Status**: The forecasting module is strictly an **experimental decision-support proof-of-concept (POC)**. It predicts projected future **risk trends**, NOT deterministic certainty regarding future geopolitical crises.

---

## Baseline Methodologies
1. **Holt-Winters Exponential Smoothing**: Captures level and trend dampening over multi-day horizons.
2. **Rolling Momentum Drift**: Uses recent trajectory derivatives while incorporating mean-reversion pull.
3. **Dynamic Uncertainty Envelopes**: Bounds expand with the forecast horizon ($h$ days):
   $$\text{Uncertainty}(h) = \pm 1.5 \cdot \sqrt{h}$$

---

## ACLED Ground-Truth Benchmarking
- The system benchmarks trend direction and volatility against ACLED-aligned historical conflict event patterns.
- **Evaluation Metrics**:
  - Mean Absolute Error (MAE)
  - Root Mean Squared Error (RMSE)
  - Directional Trend Accuracy (%)
