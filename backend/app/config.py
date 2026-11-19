import os
import math
import logging
from typing import List, Dict
from pydantic_settings import BaseSettings
from pydantic import Field, model_validator

logger = logging.getLogger("geosentinel.config")

class Settings(BaseSettings):
    PROJECT_NAME: str = "GeoSentinel AI"
    FULL_TITLE: str = "GeoSentinel AI: Global Geopolitical Threat Intelligence & Risk Scoring Platform"
    INSTITUTION: str = "GeoSentinel AI"
    DEPARTMENT: str = "Threat Intelligence Operations"
    PROJECT_GROUP: str = "v2.4"
    VERSION: str = "2.4.0"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "geosentinel-dev-secret-key-change-in-production"

    # Database - Canonical project root SQLite path
    DATABASE_URL: str = f"sqlite+aiosqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '../../geosentinel.db')).replace(chr(92), '/')}"

    # Redis Broker & Cache (Optional distributed Pub/Sub)
    REDIS_URL: str = ""

    # Ingestion Source Keys
    NEWSAPI_KEY: str = ""
    MEDIASTACK_KEY: str = ""
    GDELT_ENABLED: bool = True
    RSS_ENABLED: bool = True
    POLLING_INTERVAL_MINUTES: int = 15

    # Demo mode
    DEMO_MODE: bool = True

    # Risk Scoring Formulation Parameters:
    # Closed-form Asymptotic Hazard Saturation:
    # R_c(t) = min(100, 100 * (1 - exp(-gamma * sum(w_i * S_eff_i * c_i * exp(-lambda * delta_t)))))
    GAMMA_SCALAR: float = 0.07  # Calibrated asymptotic crisis saturation scalar
    ALPHA_SCALAR: float = 4.25  # Legacy scalar retained for backwards compatibility
    DECAY_HALF_LIFE_DAYS: float = 7.0
    LAMBDA_DECAY: float = math.log(2) / 7.0  # ~0.09902102579427789
    OBSERVATION_WINDOW_DAYS: int = 30
    ALERT_CRITICAL_THRESHOLD: float = 75.0
    ALERT_COOLDOWN_HOURS: int = 6
    ADMIN_API_KEY: str = "geosentinel-dev-admin-key"
    REQUIRE_WS_AUTH: bool = False

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

    # Webhook Alert Dispatching (Discord & Telegram)
    DISCORD_WEBHOOK_URL: str = ""
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    WEBHOOKS_ENABLED: bool = False
    FRONTEND_URL: str = "http://localhost:5173"

    # Background scheduler execution (standalone mode vs Celery worker)
    ENABLE_IN_APP_SCHEDULER: bool = True

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        """Strict validation preventing insecure defaults in production deployments."""
        if self.ENVIRONMENT.lower() == "production":
            insecure_defaults = {
                "geosentinel-admin-secret",
                "geosentinel-dev-admin-key",
                "admin",
                "secret",
                "password",
            }
            if not self.ADMIN_API_KEY or self.ADMIN_API_KEY in insecure_defaults:
                raise ValueError(
                    "FATAL SECURITY VIOLATION: ADMIN_API_KEY must be explicitly set to a strong, "
                    "non-default secret in production environment."
                )
            if not self.SECRET_KEY or self.SECRET_KEY in {
                "geosentinel-dev-secret-key-akgec-2026",
                "geosentinel-dev-secret-key-change-in-production",
                "secret",
            }:
                raise ValueError(
                    "FATAL SECURITY VIOLATION: SECRET_KEY must be set to a cryptographically "
                    "secure random value in production environment."
                )
            if "*" in self.CORS_ORIGINS:
                raise ValueError(
                    "FATAL SECURITY VIOLATION: Wildcard '*' in CORS_ORIGINS is strictly prohibited in production."
                )

            if self.DEBUG:
                logger.warning("SECURITY WARNING: DEBUG=True in production. Forcing DEBUG=False.")
                self.DEBUG = False
        return self

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "allow",
    }

settings = Settings()
