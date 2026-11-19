# GeoSentinel AI — Developer Setup & Engineering Handbook

Welcome to GeoSentinel AI. This handbook provides exact, reproducible instructions for setting up, developing, testing, and validating GeoSentinel AI from source on both Windows and Linux/macOS.

---

## 1. System Requirements

Ensure the following tools are installed on your host:
- **Python**: `3.11.x` (Python 3.12+ is also supported)
- **Node.js**: `v18.0.0` or higher (`v20.x` LTS recommended)
- **npm**: `v9.x` or higher
- **Git**: `2.30+`
- **PostgreSQL** (Optional for local dev, SQLite is supported; required for production verification): `15+`
- **Redis** (Optional for local dev, in-process fallback is supported; required for distributed multi-worker WebSocket testing): `7.x+`

---

## 2. Quickstart Step-by-Step

### Step 1: Clone the Repository
```bash
git clone https://github.com/praneeet/geosentinel-ai.git
cd geosentinel-ai
```

### Step 2: Python Virtual Environment & Dependencies
Create and activate an isolated Python virtual environment:

**Windows PowerShell:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
pip install pytest pytest-asyncio httpx datasketch scikit-learn
python -m spacy download en_core_web_sm
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
pip install pytest pytest-asyncio httpx datasketch scikit-learn
python -m spacy download en_core_web_sm
```

### Step 3: Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

### Step 4: Environment Configuration
Copy the sample environment configuration file:
```bash
cp .env.example .env
```
For local development, the default values in `.env.example` point to local SQLite (`sqlite:///./geosentinel.db`) and standalone in-process WebSocket broadcasting.

---

## 3. Database Initialization & Alembic Migrations

GeoSentinel strictly manages its schema via **Alembic**. In development, you can run migrations against SQLite or PostgreSQL:

```bash
# Run all migrations up to the current revision
alembic upgrade head

# Roll back the most recent migration
alembic downgrade -1

# Re-apply migrations
alembic upgrade head
```

> **IMPORTANT**: In production (`ENVIRONMENT="production"`), `Base.metadata.create_all()` is blocked by a guard in `backend/app/database/session.py`. All production schema changes must pass through Alembic revisions.

---

## 4. Running the Development Services

### Starting the FastAPI Backend
```bash
# Windows / Linux:
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```
Once started, explore:
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc Documentation: `http://127.0.0.1:8000/redoc`
- Prometheus Metrics: `http://127.0.0.1:8000/api/metrics`
- Health Check: `http://127.0.0.1:8000/health`

### Starting the React Frontend (Vite)
In a separate terminal:
```bash
cd frontend
npm run dev
```
Open your browser at `http://localhost:5173`. Vite proxies `/api` and `/ws` calls to `http://127.0.0.1:8000`.

---

## 5. Automated Testing Suite

GeoSentinel includes comprehensive unit, integration, and security tests:

```bash
# Run the complete test suite (51 tests)
pytest -v

# Run database hardening tests specifically
pytest backend/tests/test_database_hardening.py -v

# Run distributed WebSocket and Redis synchronization tests
pytest backend/tests/test_websocket_distributed.py -v

# Run alert engine concurrency and cooldown tests
pytest backend/tests/test_alert_engine.py -v
```

---

## 6. Machine Learning & Research Evaluation Pipelines

All ML pipelines and academic benchmarks are deterministic and reproducible:

```bash
# 1. Train 4-Domain Classifier with Scenario-Disjoint Splitting
python ml/classification/train_classifier.py

# 2. Run ACLED Time-Series Forecasting Benchmark (Holt's Damped Trend vs Persistence)
python ml/forecasting/acled_benchmark.py

# 3. Evaluate LSH Deduplication Engine (Precision, Recall, F1, Throughput)
python research/evaluation/evaluate_dedup.py

# 4. Evaluate Extractive Summarizer (ROUGE-1, ROUGE-2, ROUGE-L)
python ml/summarization/evaluate_rouge.py

# 5. Execute Multi-Annotator Agreement Pipeline (Cohen's Kappa)
python research/annotation/compute_agreement.py
```

Generated reports are persisted in `research/evaluation/`:
- `classification_report.md`
- `forecasting_benchmark.md`
- `deduplication_metrics.md`
- `summarization_rouge.md`
- `multi_annotator_agreement.md`

---

## 7. Performance & Load Testing

Run the automated concurrent client benchmark:

```bash
# Executes 500 requests across 100 concurrent simulated users
python scripts/load_test.py
```

Metrics reported:
- Total requests and completion duration
- Request throughput (Requests/sec)
- Mean, median, p95, and p99 latencies
- HTTP error rates and status code distribution

---

## 8. Troubleshooting Common Issues

### Issue: `Can't subtract offset-naive and offset-aware datetimes`
**Root Cause**: SQLite returns datetimes without timezone metadata, while FastAPI/Python uses UTC-aware datetimes.  
**Resolution**: The `AlertManager._to_utc_aware()` helper automatically normalizes naive timestamps to UTC before comparison.

### Issue: `RuntimeError: Base.metadata.create_all() is strictly prohibited in production`
**Root Cause**: `ENVIRONMENT="production"` was set when initializing the database via Python.  
**Resolution**: Run `alembic upgrade head` instead to apply verified database migrations.

### Issue: WebSocket fails to connect in production with HTTP 403
**Root Cause**: Origin validation or missing JWT token.  
**Resolution**:
1. Ensure the requesting origin is in `CORS_ORIGINS`.
2. If `REQUIRE_WS_AUTH=True`, supply a valid Bearer token via `?token=<JWT>`.

### Issue: Redis connection refused
**Root Cause**: Local Redis instance is not running on port 6379.  
**Resolution**: `WebSocketAlertDispatcher` automatically falls back to in-process local broadcasting when Redis is unreachable, retrying with exponential backoff in the background without crashing the application.
