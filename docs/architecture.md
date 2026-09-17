# GeoSentinel AI - System Architecture Document

## Overview
**GeoSentinel AI** is an AI-powered global geopolitical risk intelligence and trend-forecasting decision-support platform designed and implemented for the final year B.Tech capstone at Ajay Kumar Garg Engineering College, Ghaziabad (Department of Information Technology, CSIT Group 32).

The platform transforms high-velocity, unstructured Open-Source Intelligence (OSINT) into structured geopolitical event tuples, explainable country risk scores ($0 - 100$), real-time alerts, interactive geospatial visualizations, and exportable intelligence dossiers.

---

## 5-Tier Modular Architecture

```mermaid
graph TD
    subgraph "Layer 1: Multi-Source Ingestion & Deduplication"
        A1[NewsAPI] & A2[MediaStack] & A3[Curated RSS] & A4[GDELT 2.0] & A5[Verified Demo Source] --> B[Async Ingestion Service]
        B --> C[Normalization: HTML Strip, NFKC, Whitespace]
        C --> D[Stage 1: SHA-256 Exact Hash]
        D --> E[Stage 2: MinHash 128-Perm + LSH tau >= 0.82]
    end

    subgraph "Layer 2: AI / NLP Processing Engine"
        E --> F1[DistilBERT 4-Class Event Classifier]
        E --> F2[spaCy NER + ISO-3166-1 Alpha-3 Resolver]
        E --> F3[Sentiment & Severity Scorer in -1.0, 1.0]
        E --> F4[BART 3-Bullet Decision-Maker Summarizer]
        F1 & F2 & F3 & F4 --> G[Structured Event Tuples: c, k, Sa, wi, timestamp]
    end

    subgraph "Layer 3: Explainable Risk Scoring Engine"
        G --> H["R_c(t) = min(100, (alpha / N) * sum(w_i * |S_i| * c_i * e^(-lambda * delta_t)))"]
        H --> I["Continuous 7-Day Half-Life Decay: lambda = ln(2)/7"]
        I --> J[Risk Tiers: Low <30, Moderate 30-60, Severe >60]
    end

    subgraph "Layer 4: Persistence & Asynchronous Dispatch"
        H --> K[(PostgreSQL 15 / SQLite Async 3NF DB)]
        H --> L{Threshold Check: R > 75?}
        L -- Yes --> M[Alert Manager with 6-Hour Cooldown]
        M --> N[WebSocket Live Broadcast /ws/alerts]
        K --> O[FastAPI ASGI Async Engine]
    end

    subgraph "Layer 5: Presentation & Analytical Layer"
        O & N --> P[React 18 Leaflet Choropleth Map]
        O --> Q[Recharts Longitudinal Trend Trajectories]
        O --> R[OSINT News Explorer & Search]
        O --> S[Strategic Intelligence Dossier Generator]
        O --> T[Experimental Trend-Based Forecasting POC]
    end
```

---

## Key Distinguishing Contributions

1. **Explainable Scoring**: Transparent mathematical country-risk formula with exponential decay instead of black-box commercial heuristics.
2. **Two-Stage Deduplication**: SHA-256 exact matching combined with 128-permutation MinHash LSH ($\tau \ge 0.82$) achieving $< 1\%$ duplicate leakage.
3. **Automated Executive Briefings**: In-pipeline abstractive summarization delivering structured 3-bullet decision-maker briefings.
4. **Full-Stack Open Architecture**: FastAPI + PostgreSQL/SQLite + React 18 + Leaflet with real-time WebSocket situational awareness.
