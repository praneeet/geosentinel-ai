# GeoSentinel AI - Deployment & Local Execution Guide

## Quickstart via Docker Compose

### Prerequisites
- Docker Engine 24+
- Docker Compose v2+

### Execution Steps
```bash
# 1. Clone repository
git clone https://github.com/praneetpravin/geosentinel-ai.git
cd geosentinel-ai

# 2. Configure environment
cp .env.example .env

# 3. Launch all services
docker compose up --build
```

### Services Launched
| Service | Internal Port | External Port | Description |
| :--- | :--- | :--- | :--- |
| **frontend** | 5173 | `http://localhost:5173` | React 18 Leaflet Intelligence Dashboard |
| **backend** | 8000 | `http://localhost:8000` | FastAPI REST API & WebSocket Server |
| **postgres** | 5432 | `localhost:5432` | PostgreSQL 15 Relational Database |
| **redis** | 6379 | `localhost:6379` | Task Queue & Caching Broker |
| **worker** | - | - | Celery Asynchronous Background Worker |

---

## Local Development (Without Docker)

### Backend
```bash
# 1. Activate virtual environment
.venv\Scripts\activate   # Windows
source .venv/bin/activate # Linux / macOS

# 2. Run test suite
pytest -v

# 3. Start development server
uvicorn backend.app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# Dashboard opens on http://localhost:5173
```
