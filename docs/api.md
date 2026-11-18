# GeoSentinel AI - REST & WebSocket API Documentation

## Base URLs
- **REST API**: `http://localhost:8000/api`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **WebSocket Endpoint**: `ws://localhost:8000/ws/alerts`

---

## Key Endpoints

### 1. System Health
- `GET /api/health`: Operational status of FastAPI, database, active WebSockets, and environment configuration.

### 2. Articles & Deduplication
- `GET /api/articles`: Paginated list of ingested articles.
  - Query parameters: `page`, `page_size`, `country_iso`, `dedup_type`
- `GET /api/articles/{id}`: Detailed article record.

### 3. Geopolitical Events
- `GET /api/events`: Paginated structured event tuples with associated articles.
  - Query parameters: `page`, `page_size`, `country_iso`, `category`
- `GET /api/events/{id}`: Detailed event record.

### 4. Countries & Risk Index
- `GET /api/countries`: List of monitored sovereign countries with current risk index.
- `GET /api/countries/{iso}/risk`: Current risk scorecard, formula variables, and additive explainability breakdown.
- `GET /api/countries/{iso}/history`: Time-series risk history (24h / 7d / 30d).
- `GET /api/countries/{iso}/summary`: Extractive 3-bullet executive briefing with primary source citations.
- `GET /api/countries/{iso}/events`: Chronological list of events for the specified country.

### 5. Geospatial Risk Map
- `GET /api/risk/map`: Choropleth dataset with risk scores, tiers, and coordinates for map visualization.

### 6. Trends & Analytics
- `GET /api/trends`: Global event velocity and 4-domain category distribution over a configurable window.

### 7. Alerts
- `GET /api/alerts`: Historical critical risk threshold triggers ($R > 75$).
- `WS /ws/alerts`: WebSocket live stream for instant critical alerts.

### 8. Pipeline Ingestion & Reporting
- `POST /api/ingestion/run`: Manually triggers ETL cycle and risk recalculation (Requires X-API-Key header).
- `POST /api/reports/generate`: Generates an on-demand, evidence-backed intelligence dossier.
- `GET /api/reports/{id}`: Retrieves an existing generated dossier.
