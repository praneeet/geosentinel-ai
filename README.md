# GeoSentinel AI
### AI-Powered Global Geopolitical Risk Intelligence & Forecasting Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

---

## 1. Project Identity & Institutional Metadata

- **Institution**: Ajay Kumar Garg Engineering College, Ghaziabad
- **Department**: Department of Information Technology
- **Degree**: Bachelor of Technology in Computer Science and Information Technology
- **Project Group**: 2023–27 / CSIT-2 / GROUP-32
- **Faculty Mentor**: Mr. Anupam Saini, Assistant Professor, Department of IT
- **Student Team**:
  1. **Praneet Pravin** (Roll No. 2300270110087) — *Data Engineering & Ingestion Pipeline*
  2. **Rishabh Dwivedi** (Roll No. 2300270110097) — *Backend Architecture & Risk Engine*
  3. **Rudra Vikram Singh** (Roll No. 2300270110101) — *AI / Transformer NLP & Forecasting*
  4. **Sumit Sharma** (Roll No. 2300270110123) — *Frontend & Geospatial Visual Analytics*

- **UN Sustainable Development Goals (SDGs)**:
  - **SDG 16**: Peace, Justice, and Strong Institutions
  - **SDG 9**: Industry, Innovation, and Infrastructure

---

## 2. Core Architecture Pipeline

```text
GLOBAL NEWS SOURCES (NewsAPI, MediaStack, Curated RSS, GDELT 2.0, Demo OSINT)
                           ↓
                ASYNC INGESTION ENGINE
                           ↓
          NORMALIZATION & UNICODE SANITIZATION
                           ↓
        STAGE 1: EXACT DEDUPLICATION (SHA-256)
                           ↓
     STAGE 2: NEAR-DUPLICATE DETECTION (MinHash 128 + LSH, τ >= 0.82)
                           ↓
          PERSISTENCE: 3NF RELATIONAL STORE (PostgreSQL 15 / SQLite)
                           ↓
                   NLP PROCESSING ENGINE
        ├── Event Classification (DistilBERT: Conflict, Security, Economy, Diplomacy)
        ├── Named Entity Recognition (spaCy: GPE, LOC, ORG, PERSON)
        ├── Country Mapping (ISO-3166-1 Alpha-3 with Aliasing)
        ├── Sentiment Analysis (VADER / RoBERTa Polarity: [-1.0, +1.0])
        └── Executive Summarization (BART 3-Bullet Decision-Maker Briefs)
                           ↓
               STRUCTURED GEOPOLITICAL EVENTS
                           ↓
            EXPLAINABLE RISK SCORING ENGINE (Eq. 1)
                           ↓
           CONTINUOUS TEMPORAL DECAY: λ = ln(2)/7 (7-Day Half-Life)
                           ↓
             RISK TIERS: Low (<30), Moderate (30-60), Severe (>60)
                           ↓
            CRITICAL THRESHOLD (R > 75) ALERT ENGINE
                           ↓
               FASTAPI REST APIS & WEBSOCKET DISPATCHER
                           ↓
        REACT 18 INTELLIGENCE DASHBOARD (Leaflet Choropleth, Recharts)
```

---

## 3. Mathematical Country Risk Formulation

To eliminate black-box opacity, country risk is calculated via the closed-form mathematical equation with continuous temporal decay:

$$R_c(t) = \min\left(100,\; \frac{\alpha}{N_c(T)} \sum_{i=1}^{N_c(T)} w_i \cdot |S_{a,i}| \cdot c_{s,i} \cdot e^{-\lambda(t - t_i)}\right)$$

Where:
- $T = 30\text{ days}$ (observation sliding window)
- $\alpha = 4.25$ (normalization scalar)
- $\lambda = \frac{\ln 2}{7} \approx 0.099021\text{ day}^{-1}$ (exact 7-day half-life decay)
- $w_i$: Conflict ($1.00$), Security ($0.80$), Economy ($0.55$), Diplomacy ($0.35$)
- $|S_{a,i}| \in [0.0, 1.0]$: absolute sentiment polarity magnitude
- $c_{s,i} \in [0.1, 1.0]$: primary source credibility
- Bounded strictly within $0 \le R_c(t) \le 100$

---

## 4. Quickstart Guide

### Option A: Complete Docker Compose Stack
```bash
# Clone the repository
git clone https://github.com/praneetpravin/geosentinel-ai.git
cd geosentinel-ai

# Configure environment
cp .env.example .env

# Launch all 5 microservices
docker compose up --build
```
- **Frontend Dashboard**: `http://localhost:5173`
- **FastAPI Interactive API Docs**: `http://localhost:8000/docs`
- **WebSocket Alert Stream**: `ws://localhost:8000/ws/alerts`

---

### Option B: Local Developer Mode (Zero External Dependencies)

#### 1. Backend Setup
```bash
# Activate virtual environment
.venv\Scripts\activate       # Windows PowerShell
source .venv/bin/activate     # Linux / macOS

# Run backend test suite (17/17 tests passing)
pytest -v

# Start FastAPI server
uvicorn backend.app.main:app --reload --port 8000
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
# Dashboard launches on http://localhost:5173
```

---

## 5. Research & Evaluation Metrics

| Metric | Target Specification | Measured Telemetry | Validation Script |
| :--- | :--- | :--- | :--- |
| **Event Classification** | Macro F1 $\ge 0.85$ | Macro F1: $1.0000$ (Holdout) | `ml/classification/train_classifier.py` |
| **Executive Summarization** | ROUGE-L $\ge 0.40$ | ROUGE-L: $0.3221$ (Baseline) | `ml/summarization/evaluate_rouge.py` |
| **Deduplication Leakage** | Duplication $< 1\%$ | $0.00\%$ Leakage ($100\%$ Dups Filtered) | `research/evaluation/evaluate_dedup.py` |
| **Forecasting Accuracy** | POC Baseline vs ACLED | MAE: $1.09$ pts, Dir. Acc: $83.3\%$ | `ml/forecasting/acled_benchmark.py` |
| **Decay Half-Life** | $50\%$ decay at $7\text{ days}$ | Analytical Match ($\pm 0.0001$) | `backend/tests/test_scoring.py` |

---

## 6. Monorepo Structure

```text
geosentinel-ai/
├── backend/
│   ├── app/
│   │   ├── api/           # REST endpoints & WebSockets
│   │   ├── database/      # Async SQLAlchemy & engine
│   │   ├── models/        # 3NF tables (articles, events, scores, summaries, alerts)
│   │   ├── ingestion/     # Adapters: NewsAPI, MediaStack, RSS, GDELT, Demo
│   │   ├── deduplication/ # Two-stage: SHA-256 + MinHash 128 LSH
│   │   ├── nlp/           # DistilBERT, spaCy NER, VADER, BART
│   │   ├── scoring/       # Closed-form formula with 7-day half-life decay
│   │   ├── alerts/        # Critical threshold (R > 75) & cooldown manager
│   │   ├── reports/       # Intelligence briefing dossier generator
│   │   └── utils/         # ISO-3166 alpha-3 resolver and geo-coordinates
│   └── tests/             # Unit and integration test suite
├── frontend/
│   ├── src/
│   │   ├── components/    # WorldRiskMap, CountryDetails, TrendCharts, NewsExplorer
│   │   ├── hooks/         # useWebSocketAlerts
│   │   ├── api/           # Client API layer
│   │   └── App.jsx        # Main situational awareness UI
├── ml/
│   ├── classification/    # Classifier training & evaluation
│   ├── summarization/     # BART ROUGE evaluation
│   └── forecasting/       # Experimental forecasting experiments & ACLED benchmark
├── data/
│   └── samples/           # Verified demo OSINT dataset
├── docs/                  # Architecture, DB, API, scoring, and deployment docs
└── research/              # Academic experiment logs and evaluation reports
```

---

## 7. Important Disclaimers

1. **Model-Derived Indicators**: All country risk indices are mathematically formulated analytical indicators derived from open-source reporting and do NOT represent official governmental or military intelligence determinations.
2. **Experimental Forecasting**: Forecasting components are non-deterministic trend experiments (proof-of-concept) and do not claim deterministic prediction of future geopolitical incidents.
3. **Traceability**: Every risk score is directly traceable to primary events, articles, and verifiable open-source URLs.
