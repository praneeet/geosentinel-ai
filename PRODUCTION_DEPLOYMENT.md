# GeoSentinel Enterprise Threat Operations Center (GTOC)
## Commercial Production Deployment & Operations Runbook (v2.4-ENT)

This guide documents the enterprise production architecture, security hardening, database migration lifecycle, Celery background worker orchestration, and observability stack for deploying GeoSentinel AI in commercial high-availability environments.

---

### 1. High-Level Production Architecture

```mermaid
flowchart TD
    subgraph Edge ["Edge & Reverse Proxy Tier"]
        Users["Corporate Risk Executives & Analysts"] --> Cloudflare["Cloudflare / WAF (DDoS & TLS 1.3)"]
        Cloudflare --> Nginx["Nginx Reverse Proxy / Load Balancer (Port 443)"]
    end

    subgraph Frontend ["Presentation Tier"]
        Nginx -- "Static Assets / SPA Fallback" --> ViteBuild["Compiled Vite Production Bundle (dist/)"]
    end

    subgraph API ["Application Tier (FastAPI Cluster)"]
        Nginx -- "REST API /api/*" --> Gunicorn["Gunicorn Process Manager"]
        Nginx -- "WebSocket /ws/*" --> Gunicorn
        Gunicorn --> Worker1["Uvicorn Worker #1"]
        Gunicorn --> Worker2["Uvicorn Worker #2"]
        Gunicorn --> Worker3["Uvicorn Worker #3"]
        Gunicorn --> Worker4["Uvicorn Worker #4"]
    end

    subgraph AsyncTier ["Async Ingestion & Processing Tier"]
        DedicatedWorker["Async Ingestion Worker (python -m app.worker)"]
        RedisBus["Redis 7 (Distributed Pub/Sub & Worker Sync)"]
        RedisBus -.-> DedicatedWorker
        DedicatedWorker -- "Ingest Feeds" --> ExternalFeeds["OSINT Feeds (ACLED, GDELT, RSS)"]
    end

    subgraph Storage ["Persistence Tier"]
        Worker1 & Worker2 & Worker3 & Worker4 & CeleryWorker --> PgBouncer["PgBouncer Connection Pooler"]
        PgBouncer --> Postgres["PostgreSQL 15+ (Primary)"]
        Postgres --> Replica["PostgreSQL Read Replica"]
    end

    subgraph Observability ["Telemetry & Monitoring"]
        Prometheus["Prometheus Server"] -- "Scrapes /api/metrics" --> Gunicorn
        Prometheus --> Grafana["Grafana Enterprise Dashboard"]
        Sentry["Sentry Error Tracking"]
    end
```

---

### 2. Infrastructure & Compute Sizing

| Component | Minimum Spec (Dev/Staging) | Production Enterprise Spec | Multi-Region Active/Passive |
| :--- | :--- | :--- | :--- |
| **API Server (FastAPI)** | 2 vCPU, 4 GB RAM | 4 vCPU, 8 GB RAM (2 replicas minimum) | Horizontal Pod Autoscaling (HPA) |
| **Worker (Celery)** | 1 vCPU, 2 GB RAM | 2 vCPU, 4 GB RAM (Dedicated worker node) | Autoscaling based on queue length |
| **PostgreSQL Database** | 2 vCPU, 4 GB RAM (SSD) | 4 vCPU, 16 GB RAM (Provisioned IOPS SSD) | Multi-AZ with automated failover |
| **Redis Cache/Broker** | 1 vCPU, 1 GB RAM | 2 vCPU, 4 GB RAM with AOF persistence | Redis Sentinel or AWS ElastiCache |
| **Frontend CDN** | Local Nginx | Cloudflare Enterprise / CloudFront CDN | Global Edge Caching (Brotli/HTTP3) |

---

### 3. Production Environment Configuration (`.env`)

Create `/etc/geosentinel/.env` (or load securely from AWS Secrets Manager / GCP Secret Manager / Vault):

```ini
# Core Environment
ENVIRONMENT=production
DEBUG=False
PROJECT_NAME="GeoSentinel Enterprise"
SECRET_KEY="GENERATE_CRYPTOGRAPHICALLY_SECURE_64_CHAR_HEX_KEY"

# Database - PostgreSQL Async Connection Pool
DATABASE_URL=postgresql+asyncpg://geosentinel_admin:REPLACE_WITH_STRONG_PASSWORD@postgres.internal.net:5432/geosentinel_production

# Redis & Celery Message Broker
REDIS_URL=redis://:REPLACE_WITH_REDIS_AUTH_TOKEN@redis.internal.net:6379/0
CELERY_BROKER_URL=redis://:REPLACE_WITH_REDIS_AUTH_TOKEN@redis.internal.net:6379/0
CELERY_RESULT_BACKEND=redis://:REPLACE_WITH_REDIS_AUTH_TOKEN@redis.internal.net:6379/0

# Ingestion Keys
DEMO_MODE=False
NEWSAPI_KEY=YOUR_COMMERCIAL_NEWSAPI_KEY
MEDIASTACK_KEY=YOUR_COMMERCIAL_MEDIASTACK_KEY
GDELT_ENABLED=True
RSS_ENABLED=True
POLLING_INTERVAL_MINUTES=15

# Enterprise Webhooks
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID=-100123456789
WEBHOOKS_ENABLED=True

# Strict CORS Allowed Domains
CORS_ORIGINS=["https://gtoc.yourcompany.com", "https://threats.yourcompany.com"]
```

---

### 4. Database Schema Lifecycle & Alembic Migrations

GeoSentinel uses declarative schema versioning via **Alembic**. Never invoke `Base.metadata.create_all()` in production.

#### Applying Migrations:
```bash
# Run latest database migrations before rolling out new containers
alembic upgrade head
```

#### Creating New Schema Changes:
```bash
# Generate automatic diff from SQLAlchemy models
alembic revision --autogenerate -m "add_enterprise_custom_fields"

# Review migration script under backend/alembic/versions/
# Commit and deploy through CI/CD
```

---

### 5. Deployment Commands

#### Option A: Docker Compose Production Stack
```bash
# 1. Ensure .env is populated with production credentials
cp .env.example .env

# 2. Build and launch isolated containers in detached mode
docker compose -f docker-compose.prod.yml up -d --build

# 3. Verify health status across all services
docker compose -f docker-compose.prod.yml ps

# 4. View real-time logs
docker compose -f docker-compose.prod.yml logs -f backend
```

#### Option B: Standalone Linux Host Deployment (systemd + Nginx)

1. **Gunicorn Systemd Service** (`/etc/systemd/system/geosentinel-api.service`):
```ini
[Unit]
Description=GeoSentinel Enterprise GTOC FastAPI Service
After=network.target postgresql.service redis.service

[Service]
User=geosentinel
Group=geosentinel
WorkingDirectory=/opt/geosentinel/backend
EnvironmentFile=/etc/geosentinel/.env
ExecStart=/opt/geosentinel/.venv/bin/gunicorn app.main:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    --timeout 120 \
    --access-logfile /var/log/geosentinel/access.log \
    --error-logfile /var/log/geosentinel/error.log
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

2. **Background Ingestion Worker Service** (`/etc/systemd/system/geosentinel-worker.service`):
```ini
[Unit]
Description=GeoSentinel Dedicated Ingestion & LSH Deduplication Worker
After=network.target postgresql.service redis.service

[Service]
User=geosentinel
Group=geosentinel
WorkingDirectory=/opt/geosentinel/backend
EnvironmentFile=/etc/geosentinel/.env
ExecStart=/opt/geosentinel/.venv/bin/python -m app.worker
Restart=always
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

3. **Start Services**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now geosentinel-api geosentinel-worker
```

---

### 6. Prometheus Telemetry & APM Monitoring

GeoSentinel exposes live Prometheus telemetry at:
```http
GET http://127.0.0.1:8000/api/metrics
```

#### Metrics Catalog:
* `geosentinel_http_requests_total`: Monotonically increasing HTTP counter.
* `geosentinel_http_request_duration_seconds`: Cumulative response latency.
* `geosentinel_http_average_latency_seconds`: Real-time request response speed.
* `geosentinel_websocket_active_connections`: Live connected tactical watch officers.
* `geosentinel_corporate_assets_monitored_total`: Total geofenced corporate facilities.
* `geosentinel_articles_indexed_total`: Total OSINT articles stored & deduplicated.
* `geosentinel_events_classified_total`: Active NLP-classified threat events.
* `geosentinel_alerts_triggered_total`: Critical threshold alerts sent.

#### Prometheus Scrape Config (`prometheus.yml`):
```yaml
scrape_configs:
  - job_name: 'geosentinel_gtoc'
    scrape_interval: 15s
    metrics_path: '/api/metrics'
    static_configs:
      - targets: ['api.internal.net:8000']
```

---

### 7. Security Hardening Checklist

- [x] **Non-Root Containers**: `Dockerfile.prod` runs under UID 10001 (`appuser`).
- [x] **Security Headers**: HSTS, CSP, X-Frame-Options (`DENY`), X-Content-Type-Options (`nosniff`).
- [x] **Rate Limiting & Timing**: Process time calculation and request limits to prevent volumetric DoS.
- [x] **Error Isolation**: UI ErrorBoundary intercepts runtime errors without crashing the dashboard.
- [x] **TLS 1.3 & Reverse Proxy**: Nginx config terminates SSL and reverse proxies WebSocket feeds cleanly.
- [x] **Alembic Versioning**: All schema migrations versioned under `backend/alembic/versions/`.

