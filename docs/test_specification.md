# Software Test Specification & Verification Matrix (IEEE 829 Standard)

### GeoSentinel AI — AI-Powered Global Geopolitical Risk Intelligence & Forecasting Platform
- **Institution**: Ajay Kumar Garg Engineering College, Ghaziabad
- **Department**: Department of Information Technology (B.Tech CSIT Group 32)
- **Student Team**: Praneet Pravin, Rishabh Dwivedi, Rudra Vikram Singh, Sumit Sharma
- **Faculty Mentor**: Mr. Anupam Saini, Assistant Professor, Department of IT
- **Test Framework**: `pytest 9.1+` with `asyncio`, `httpx`, and `scikit-learn`
- **Current Test Suite Status**: **23 / 23 Tests Passing (100% Pass Rate)**

---

## 1. System Test Verification Matrix

| Test ID | Module | Objective / Description | Input Vector | Expected Output | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-01** | `test_api.py` | System health check and diagnostics probe | `GET /api/health` | HTTP 200, status `healthy`, timestamp ISO-8601 | **PASS** |
| **TC-02** | `test_api.py` | Monitored country list with coordinates & risk scores | `GET /api/countries` | HTTP 200, list containing 18+ valid ISO-3166 entries | **PASS** |
| **TC-03** | `test_api.py` | Geospatial choropleth risk map endpoint | `GET /api/risk/map` | HTTP 200, array of `CountryRiskMapItem` with lat/lon | **PASS** |
| **TC-04** | `test_api.py` | Longitudinal timeline and sentiment velocity | `GET /api/trends?days=30` | HTTP 200, category distribution with 4 domains, 30d timeline | **PASS** |
| **TC-05** | `test_dedup.py` | Stage 1 exact duplicate detection via SHA-256 | Exact identical string and HTML-stripped text | Identical 64-char hash digest; second submission flagged | **PASS** |
| **TC-06** | `test_dedup.py` | Stage 2 near-duplicate wire syndication via MinHash LSH | Syndicated wire release with minor synonym edit | MinHash Jaccard $\ge 0.82$; status `near_duplicate` | **PASS** |
| **TC-07** | `test_forecast.py`| 7-day Holt's damped linear trend projection | Current risk $65.0$, history $[55, 58, 60, 62, 65]$ | 7 daily points; $lower \le forecast \le upper$; $0 \le R \le 100$ | **PASS** |
| **TC-08** | `test_forecast.py`| Projection handling without historical points | Current risk $25.0$, empty history | 5 valid projections with baseline momentum drift | **PASS** |
| **TC-09** | `test_forecast.py`| Extreme upper and lower bound confinement | Current risk $99.0$ and $1.0$ | Forecast and bounds strictly confined within $[0.0, 100.0]$ | **PASS** |
| **TC-10** | `test_nlp.py` | ISO-3166-1 alpha-3 resolution and country aliases | `"United States"`, `"US"`, `"U.S.A."` | Resolves strictly to `"USA"` | **PASS** |
| **TC-11** | `test_nlp.py` | 4-Domain geopolitical category classification | Conflict, Economy, and Diplomacy news text | Matches corresponding domain with confidence $> 0.60$ | **PASS** |
| **TC-12** | `test_nlp.py` | Sentiment polarity bounding & directionality | Positive cooperation vs violent kinetic strikes | Bounded within $[-1.0, 1.0]$; positive score $>$ negative score | **PASS** |
| **TC-13** | `test_nlp.py` | BART executive 3-bullet briefing structure | Title, body, category, and country name | 3 bullets starting with `Key development:`, `Strategic significance:`, `Geopolitical implication:` | **PASS** |
| **TC-14** | `test_scoring.py` | Zero active events returns baseline zero risk | Empty event list `[]` | $R_c(t) = 0.0$, Tier = `"Low"`, $Critical = \text{False}$ | **PASS** |
| **TC-15** | `test_scoring.py` | Single event calculation via closed-form equation | 1 event: Conflict, $|S|=0.80$, Credibility $1.0$ | Expected $4.0 \le R \le 6.0$; matches Eq. 1 with scalar $\alpha=4.25$ | **PASS** |
| **TC-16** | `test_scoring.py` | 7-day continuous half-life temporal decay ($\lambda$) | Event at $t=0$ vs event at $t - 7\text{ days}$ | Decay factor matches analytical half-life $0.50 \pm 0.0001$ | **PASS** |
| **TC-17** | `test_scoring.py` | Mathematical upper bound confinement ($0 \le R \le 100$) | 100 concurrent high-severity kinetic strikes | Strict saturation at $R_c(t) \le 100.0$, Tier = `"Severe"` | **PASS** |
| **TC-18** | `test_scoring.py` | Standard risk tier classification | $R = 29.9$, $30.0$, $60.0$, $60.1$ | Correctly maps to `Low` ($<30$), `Moderate` ($30-60$), `Severe` ($>60$) | **PASS** |
| **TC-19** | `test_scoring.py` | Critical threshold alert trigger ($R > 75$) | $R = 75.0$ vs $R = 75.1$ | False for $75.0$, True for $75.1$ | **PASS** |
| **TC-20** | `test_scoring.py` | Category severity weight hierarchy | Conflict ($1.0$), Security ($0.8$), Economy ($0.55$), Diplomacy ($0.35$) | Strictly enforces $w_{conflict} > w_{security} > w_{economy} > w_{diplomacy}$ | **PASS** |
| **TC-21** | `test_sim.py` | What-If scenario simulation templates | `GET /api/simulation/templates` | HTTP 200, 4 curated scenarios (Red Sea, Frontline, Semiconductors, Grid) | **PASS** |
| **TC-22** | `test_sim.py` | Scenario simulation execution & spillover | `POST /api/simulation/run` with injected events | HTTP 200, calculated risk delta $\Delta R$, 7-day forecast, regional spillover | **PASS** |
| **TC-23** | `test_sim.py` | AI Intelligence Copilot RAG briefing | `POST /api/chat` with natural language inquiry | HTTP 200, structured markdown briefing with primary source citations | **PASS** |
| **TC-24** | `test_auth.py`| Analyst OAuth2 JWT login authentication | `POST /api/auth/token` with admin credentials | HTTP 200, signed HMAC-SHA256 JWT token, role `ADMINISTRATOR` | **PASS** |
| **TC-25** | `test_auth.py`| Invalid credential rejection | `POST /api/auth/token` with bad password | HTTP 401 Unauthorized error response | **PASS** |
| **TC-26** | `test_auth.py`| Role hierarchy & capability directory | `GET /api/auth/roles` | HTTP 200, 3 defined tiers: Administrator, Senior Analyst, Watch Officer | **PASS** |
| **TC-27** | `test_export.py`| RFC 7946 GeoJSON FeatureCollection GIS export | `GET /api/risk/export/geojson` | HTTP 200, valid GeoJSON FeatureCollection with Point geometry & risk props | **PASS** |
| **TC-28** | `test_export.py`| Structured CSV event telemetry download | `GET /api/events/export/csv` | HTTP 200, `text/csv` attachment with complete event attribute headers | **PASS** |

---

## 2. Test Execution Command
To run the automated test suite locally:
```bash
pytest -v
```
To run continuous integration remotely on GitHub:
Configured via [.github/workflows/ci.yml](../.github/workflows/ci.yml).
