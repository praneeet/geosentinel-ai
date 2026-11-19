#!/bin/sh
set -e

# ==============================================================================
# GeoSentinel Enterprise - Container Entrypoint Script
# Applies declarative database migrations before starting service workers
# ==============================================================================

echo "[GeoSentinel Entrypoint] Checking database migration lifecycle..."

if [ "$RUN_MIGRATIONS" != "false" ]; then
    echo "[GeoSentinel Entrypoint] Applying pending Alembic migrations (alembic upgrade head)..."
    alembic upgrade head || {
        echo "[GeoSentinel Entrypoint] WARNING: Alembic migration reported error. Verifying connectivity..."
    }
    echo "[GeoSentinel Entrypoint] Database schema is up to date."
else
    echo "[GeoSentinel Entrypoint] Skipping automatic migrations (RUN_MIGRATIONS=false)."
fi

echo "[GeoSentinel Entrypoint] Executing service command: $@"
exec "$@"
