# GeoSentinel AI - Database Architecture (3NF)

## Relational Schema (Third Normal Form)

The GeoSentinel AI persistence layer implements the 3NF relational database architecture specified in Table 2 of the Academic Synopsis.

```mermaid
erDiagram
    articles ||--o{ events : "contains"
    articles {
        string article_id PK "UUID"
        string title "VARCHAR(512)"
        string content_hash UK "CHAR(64) UNIQUE"
        string source_name "VARCHAR(128)"
        text source_url "TEXT"
        float credibility "FLOAT"
        datetime published_at "TIMESTAMPTZ"
        text body_text "TEXT"
        string language "VARCHAR(10)"
        string dedup_type "VARCHAR(32)"
        datetime created_at "TIMESTAMPTZ"
    }

    events {
        string event_id PK "UUID"
        string article_id FK "UUID -> articles.article_id"
        string category "VARCHAR(32)"
        string country_iso "CHAR(3)"
        float sentiment "FLOAT [-1.0, 1.0]"
        float severity "FLOAT [0.0, 1.0]"
        json entities "JSONB"
        datetime timestamp "TIMESTAMPTZ"
        float confidence "FLOAT"
        string model_version "VARCHAR(32)"
    }

    country_scores {
        string score_id PK "UUID"
        string country_iso "CHAR(3)"
        float risk_index "FLOAT [0.0, 100.0]"
        float decayed_agg "FLOAT"
        string risk_tier "VARCHAR(16)"
        int event_count "INTEGER"
        json contributing_factors "JSONB"
        datetime calculated_at "TIMESTAMPTZ"
    }

    summaries {
        string summary_id PK "UUID"
        string country_iso "CHAR(3)"
        json bullet_points "JSONB"
        json evidence_links "JSONB"
        datetime generated_at "TIMESTAMPTZ"
        string model_version "VARCHAR(32)"
    }

    alerts {
        string alert_id PK "UUID"
        string country_iso "CHAR(3)"
        float risk_score "FLOAT"
        string trigger_tier "VARCHAR(16)"
        string trigger_reason "VARCHAR(64)"
        json payload "JSONB"
        datetime sent_at "TIMESTAMPTZ"
    }
```

---

## Indexing & Performance Strategy
1. `articles.content_hash`: Unique B-Tree index for $O(1)$ Stage 1 exact deduplication.
2. `articles.published_at`: Descending index for rapid pagination of latest news feeds.
3. `events.country_iso`: Composite index with `timestamp` for instantaneous 30-day temporal window queries during country risk recalculation.
4. `country_scores.country_iso`: Indexed for immediate map choropleth retrieval.
5. `alerts.sent_at`: Descending index for real-time alert history drawers.
