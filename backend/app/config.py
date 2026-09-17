import math
from typing import List, Dict
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "GeoSentinel AI"
    FULL_TITLE: str = "GeoSentinel AI: AI-Powered Global Geopolitical Risk Intelligence & Forecasting Platform"
    INSTITUTION: str = "Ajay Kumar Garg Engineering College, Ghaziabad"
    DEPARTMENT: str = "Information Technology"
    PROJECT_GROUP: str = "2023-27 / CSIT-2 / GROUP-32"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "geosentinel-secret-key-super-secure-change-in-prod"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./geosentinel.db"

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Ingestion Source Keys
    NEWSAPI_KEY: str = ""
    MEDIASTACK_KEY: str = ""
    GDELT_ENABLED: bool = True
    RSS_ENABLED: bool = True
    POLLING_INTERVAL_MINUTES: int = 15

    # Demo mode
    DEMO_MODE: bool = True

    # Risk Scoring Formulation Parameters:
    # R_c(t) = min(100, (alpha / N) * sum(w_i * |S_i| * c_i * exp(-lambda * delta_t)))
    ALPHA_SCALAR: float = 4.25
    DECAY_HALF_LIFE_DAYS: float = 7.0
    LAMBDA_DECAY: float = math.log(2) / 7.0  # ~0.09902102579427789
    OBSERVATION_WINDOW_DAYS: int = 30
    ALERT_CRITICAL_THRESHOLD: float = 75.0
    ALERT_COOLDOWN_HOURS: int = 6

    # Category Weights
    CATEGORY_WEIGHTS: Dict[str, float] = {
        "CONFLICT": 1.00,
        "SECURITY": 0.80,
        "ECONOMY": 0.55,
        "DIPLOMACY": 0.35,
    }

    # Deduplication Parameters (Two-stage)
    MINHASH_PERMUTATIONS: int = 128
    LSH_THRESHOLD: float = 0.82
    DEDUP_WINDOW_HOURS: int = 48

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "allow",
    }

settings = Settings()
