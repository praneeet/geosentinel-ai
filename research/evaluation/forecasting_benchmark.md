# Experimental Risk Trend Forecasting: Ground Truth Benchmark

## Research Methodology & Status
- **Type**: Trend-Based Forecasting Experiment / Proof-of-Concept (POC)
- **Model**: Holt's Damped Linear Exponential Smoothing with Dynamic Uncertainty Bounds
- **Evaluation Baseline**: Multi-Theater ACLED-Aligned Incident Trajectories ($N = 3$ theaters)
- **Disclaimer**: GeoSentinel AI trend forecasts are non-deterministic risk indicators for decision support, not deterministic future event predictions.

## Quantitative Telemetry
| Metric | Measured Score | Standard Target | Status |
| :--- | :--- | :--- | :--- |
| **Mean Absolute Error (MAE)** | **2.19 risk points** | $\le 3.50$ pts | **Target Met** |
| **Root Mean Squared Error (RMSE)** | **2.39 risk points** | $\le 4.50$ pts | **Target Met** |
| **Directional Trend Accuracy** | **85.7%** | $\ge 70.0\%$ | **Target Exceeded** |

## Theater Breakdown
- **Kinetic Escalation Theater**: MAE = 2.89 pts | RMSE = 3.20 pts | Directional Accuracy = 100.0%
- **Diplomatic De-escalation Theater**: MAE = 1.59 pts | RMSE = 1.76 pts | Directional Accuracy = 100.0%
- **Controlled Maritime Chokepoint**: MAE = 2.09 pts | RMSE = 2.20 pts | Directional Accuracy = 57.1%

## ACLED Ground Truth Integration Note
ACLED ground truth event data operates under specific academic/non-commercial attribution guidelines. GeoSentinel AI adheres strictly to data licensing protocols, benchmarking trend signals while keeping external ground-truth validation clearly demarcated.
