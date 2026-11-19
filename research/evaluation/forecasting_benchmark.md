# Forecasting Engine Benchmark: ACLED-Calibrated Historical Trajectories

## Research Methodology & Setup
- **Model**: Holt's Damped Linear Exponential Smoothing ($lpha=0.35, \beta=0.20, \phi=0.88$) with dynamic horizon uncertainty bounds ($1.2\sqrt{h}$).
- **Baseline Model**: Naive Persistence Random Walk ($R_{t+h} = R_t$).
- **Benchmark Corpus**: 5 historical theater trajectories calibrated against ACLED (Armed Conflict Location & Event Data Project) published weekly incident counts.
- **Horizon**: 7-day forward rolling evaluation ($h = 1 \dots 7$).

## Aggregate Benchmark Results
| Metric | Holt's Damped Trend | Naive Persistence Baseline | Relative Improvement |
| :--- | :---: | :---: | :---: |
| **Mean Absolute Error (MAE)** | **2.54 pts** | 4.82 pts | **+47.3% reduction** |
| **Root Mean Squared Error (RMSE)** | **2.82 pts** | 5.17 pts | **+45.5% reduction** |
| **Directional Trend Accuracy** | **77.1%** | 0.0% (Zero delta) | **Exceeds 70% threshold** |

## Theater-by-Theater Breakdown

### 1. Eastern Europe / Donbas Frontline (Kinetic Escalation Phase) (UKR)
- **Reference**: ACLED Regional Conflict Tracking: Weekly Armed Clashes & Artillery Events
- **Holt's Damped Trend**: MAE = `0.38` pts | RMSE = `0.43` pts | Directional Accuracy = `100.0%`
- **Naive Baseline**: MAE = `6.46` pts | RMSE = `6.99` pts
- **Error Reduction**: `+94.1%`

### 2. Red Sea & Gulf of Aden Maritime Corridor (Drone/Missile Activity) (YEM)
- **Reference**: ACLED Maritime Incident Data: Anti-Ship Cruise & USV Strikes
- **Holt's Damped Trend**: MAE = `6.59` pts | RMSE = `7.52` pts | Directional Accuracy = `100.0%`
- **Naive Baseline**: MAE = `8.49` pts | RMSE = `8.96` pts
- **Error Reduction**: `+22.4%`

### 3. Central Sahel / Border Tri-Junction (Insurgent Volatility) (MLI)
- **Reference**: ACLED West Africa Conflict Monitor: Insurgency vs State Forces
- **Holt's Damped Trend**: MAE = `2.44` pts | RMSE = `2.51` pts | Directional Accuracy = `42.9%`
- **Naive Baseline**: MAE = `0.96` pts | RMSE = `1.08` pts
- **Error Reduction**: `-154.6%`

### 4. South Caucasus Border Zone (Post-Accord De-escalation Phase) (ARM)
- **Reference**: ACLED Caucasus Monitor: Ceasefire Demarcation & Incident Reduction
- **Holt's Damped Trend**: MAE = `1.42` pts | RMSE = `1.74` pts | Directional Accuracy = `100.0%`
- **Naive Baseline**: MAE = `7.83` pts | RMSE = `8.41` pts
- **Error Reduction**: `+81.9%`

### 5. Taiwan Strait ADIZ & Maritime Patrols (Controlled Standoff Baseline) (TWN)
- **Reference**: Regional Defense Dispatches & Surveillance Aircraft Incursions
- **Holt's Damped Trend**: MAE = `1.88` pts | RMSE = `1.90` pts | Directional Accuracy = `42.9%`
- **Naive Baseline**: MAE = `0.36` pts | RMSE = `0.42` pts
- **Error Reduction**: `-426.0%`

## Academic Context & Data Attribution
ACLED (Armed Conflict Location & Event Data Project) data is referenced under academic and research guidelines. The trajectories evaluate the mathematical dampening heuristic against real-world kinetic escalation, de-escalation, and maritime crisis curves.
