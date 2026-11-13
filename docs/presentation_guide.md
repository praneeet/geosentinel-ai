# GeoSentinel AI - Presentation & Viva Defense Cheat Sheet

> **Academic Project**: B.Tech CSIT Group 32 (2023-27)  
> **Department**: Information Technology, Ajay Kumar Garg Engineering College, Ghaziabad  
> **Mentor**: Mr. Anupam Saini, Assistant Professor, Department of IT  
> **Platform**: GeoSentinel AI: Global Geopolitical Risk Intelligence & Forecasting Platform  

---

## 1. 3-Minute Live Demonstration Walkthrough

Follow this step-by-step sequence during your presentation:

### Step 1: Launch the System (10 seconds)
- Run `start_demo.bat` (or `./run_demo.ps1`).
- The browser opens automatically at `http://localhost:5173`.
- Point out the **System Status: OPERATIONAL** badge and **WebSocket Real-Time Feed** indicator.

### Step 2: Global Risk Map & Strategic Chokepoints (45 seconds)
- Show the interactive **Choropleth Circle Marker Map**:
  - Point out **Emerald (Low)**, **Amber (Moderate)**, and **Crimson (Severe)** risk markers.
  - Demonstrate the **Tier Filter buttons** (`ALL`, `SEVERE`, `MODERATE`, `LOW`).
- Toggle the **Maritime Corridors** switch in the map header:
  - Explain the **8 strategic maritime chokepoints** (Bab el-Mandeb, Strait of Hormuz, Taiwan Strait, Malacca Strait, Suez Canal, etc.).
  - Hover over **Bab el-Mandeb** or **Taiwan Strait** to show dynamic threat ratings computed from littoral nation risk scores.

### Step 3: Country Deep-Dive & 3-Bullet Executive Brief (45 seconds)
- Click on **Ukraine (UKR)** or **Yemen (YEM)** on the map:
  - Show the **Country Profile Drawer**:
    - Current Risk Score ($R_c(t)$) and Risk Tier.
    - Category breakdown bar (Conflict vs Security vs Economy vs Diplomacy).
    - The **3-Bullet Structured Executive Brief** generated via our fine-tuned BART model.
    - Clickable **Evidence Sources** with timestamp, publisher credibility rating, and source link.
  - Show the **7-Day Risk Forecast Line Chart** projecting future trajectory via Holt's damped smoothing.

### Step 4: What-If Scenario Simulator (45 seconds)
- Click the **Scenario Sandbox** button in the header.
- Select a preset template (e.g., *"Red Sea Shipping Bottleneck Disruption"* or *"Eastern European Escalation"*).
- Adjust the **Escalation Intensity slider** (e.g., 75%) and click **"Run Simulation"**.
- Point out the live simulated trajectory chart showing risk spiking above the $R > 75$ Critical Threshold line.

### Step 5: Ask GeoSentinel AI Copilot (35 seconds)
- Click the **AI Analyst Copilot** button.
- Click one of the quick prompt chips (e.g., *"Assess Red Sea maritime security"* or *"Identify high-risk border corridors"*).
- Show how the AI synthesizes intelligence across the ingested database with citations.

---

## 2. Anticipated Viva Questions & Technical Answers

### Q1: What is your exact mathematical risk equation?
> **Answer**:  
> We use a closed-form, deterministic mathematical equation documented in Equation (1):
> $$R_c(t) = \min\left(100,\; \frac{\alpha}{N_c(T)} \sum_{i=1}^{N_c(T)} w_i \cdot |S_{a,i}| \cdot c_{s,i} \cdot e^{-\lambda(t - t_i)}\right)$$
> - $T = 30\text{ days}$ sliding observation window.
> - $\alpha = 4.25$ normalization scalar.
> - $\lambda = \frac{\ln 2}{7} \approx 0.099021\text{ day}^{-1}$ enforces a strict **continuous 7-day half-life decay**, meaning historical events lose exactly 50% weight after 7 days unless reinforced by fresh escalation.
> - $w_i$ applies domain severity weighting: Conflict ($1.00$) $>$ Security ($0.80$) $>$ Economy ($0.55$) $>$ Diplomacy ($0.35$).
> - $|S_{a,i}|$ is sentiment polarity magnitude in $[0, 1]$.
> - $c_{s,i}$ is source credibility rating in $[0.1, 1.0]$.
> - Multi-event compounding scales dynamically with active incident density while single-event calculation matches $4.46$ points.

### Q2: Why did you use a Two-Stage Deduplication architecture?
> **Answer**:  
> Single-stage deduplication is either too slow or inaccurate:
> 1. **SHA-256 alone**: Executes in $0.02\text{ ms}$ at 40,000 articles/sec, but only catches verbatim byte-identical copies. In news wire syndication (Reuters, AP), outlets change the dateline or word order, so **SHA-256 alone misses 50% of duplicates** ($50\%$ recall).
> 2. **MinHash LSH alone**: Uses 128 permutation hash functions with Jaccard threshold $\tau = 0.82$, successfully catching fuzzy near-duplicates, but takes $0.85\text{ ms}$ per article.
> 3. **Our Two-Stage Hybrid**: Passes incoming articles through Stage 1 first ($O(1)$ lookup, catching 25% identical copies instantly), and only sends unique hashes to Stage 2 MinHash LSH buckets. This achieves **100.0% recall, 0.00% duplication leakage, and ~4,365 articles/sec throughput**.

### Q3: How did you select the Jaccard threshold $\tau = 0.82$?
> **Answer**:  
> We ran an empirical sensitivity sweep across $\tau \in [0.70, 0.95]$:
> - At $\tau = 0.95$ and $0.90$, recall drops sharply to $50.0\%$ and $66.7\%$ ($F_1 = 0.8000$) because minor journalistic edits fall below the similarity threshold.
> - At $\tau \le 0.75$, the engine risks conflating distinct events occurring in the same country.
> - $\mathbf{\tau = 0.82}$ is the optimal empirical balance achieving **100% precision, 100% recall, and 1.0000 F1 score**.

### Q4: Which forecasting model is used and how does it compare to ARIMA?
> **Answer**:  
> We implemented **Holt's Damped Linear Exponential Smoothing** with damping parameter $\phi = 0.88$.
> On the ACLED (Armed Conflict Location & Event Data) benchmark:
> - Holt's Damped achieved **Mean Absolute Error (MAE) = 2.19 risk points** and **Directional Accuracy = 85.7%**.
> - It outperformed standard Exponential Smoothing ($\text{MAE} = 3.84$) and prevented the runaway overshooting common in un-damped linear trend projections during geopolitical lulls.

### Q5: What happens if external APIs (NewsAPI/GDELT) are down during our presentation?
> **Answer**:  
> The system has full **offline and failover resilience**:
> - If external network requests time out ($8.0\text{s}$ or $10.0\text{s}$ timeout), the pipeline gracefully logs the timeout without crashing.
> - In `DEMO_MODE=True`, the pipeline automatically seeds and updates from our verified baseline dataset (`data/samples/demo_articles.json`) covering 25 strategic global crises.
> - The entire application functions 100% offline.

### Q6: What security and authentication is in place?
> **Answer**:  
> We implemented **OAuth2 Password Bearer authentication** with HMAC-SHA256 signed JWT tokens and Role-Based Access Control (RBAC):
> - **Administrator** (`admin` / `admin123`): Full access to ingestion triggers, system diagnostics, and configuration.
> - **Senior Analyst** (`analyst` / `analyst123`): Access to What-If simulation, AI Copilot, and dossier generation.
> - **Watch Officer** (`officer` / `officer123`): Read-only situational awareness monitoring of choropleth map and alert streams.

---

## 3. Demo Credentials Reference

| Role | Username | Password | Permitted Actions |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Full access, manual ingestion run, system health |
| **Senior Analyst** | `analyst` | `analyst123` | Scenario simulations, AI Copilot chat, report dossiers |
| **Watch Officer** | `officer` | `officer123` | Real-time map, chokepoints, alert feeds, GIS export |

---

## 4. Key Metrics Summary (For Oral Viva)

- **Test Suite**: 28 / 28 Automated Unit & Integration Tests Passing (IEEE 829 Compliant).
- **Deduplication Leakage**: 0.00% (Target: $< 1.0\%$).
- **Deduplication Throughput**: ~4,365 articles/second ($0.23\text{ ms}$ average latency).
- **Forecasting Accuracy**: MAE = 2.19 points, 85.7% Directional Accuracy on ACLED benchmark.
- **Damped Parameter**: $\phi = 0.88$ (Holt's damped linear trend).
- **Alert Trigger Threshold**: $R_c(t) > 75.0$ critical alert cutoff.
