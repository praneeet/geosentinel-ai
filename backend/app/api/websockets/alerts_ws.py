import secrets
import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from app.alerts.websocket import ws_dispatcher
from app.config import settings

logger = logging.getLogger("geosentinel.ws_router")
router = APIRouter()

MAX_WS_CONNECTIONS = 500

def _is_valid_token(token: Optional[str]) -> bool:
    """Validates provided token against configured admin key or secret key."""
    if not token or not token.strip():
        return False
    expected_admin = getattr(settings, "ADMIN_API_KEY", "")
    if expected_admin and secrets.compare_digest(token.strip(), expected_admin.strip()):
        return True
    expected_secret = getattr(settings, "SECRET_KEY", "")
    if expected_secret and secrets.compare_digest(token.strip(), expected_secret.strip()):
        return True
    return False

@router.websocket("/ws/alerts")
async def websocket_alerts_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
):
    """
    WebSocket endpoint streaming real-time critical risk alerts (R > 75)
    to connected client dashboards.
    Implements origin validation, token authentication, connection limits, and keep-alive ping/pong.
    """
    # 1. Connection capacity guard
    if len(ws_dispatcher.active_connections) >= MAX_WS_CONNECTIONS:
        logger.warning("Rejected WebSocket connection: maximum connection capacity reached.")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Server connection capacity reached")
        return

    # 2. Origin validation in production
    origin = websocket.headers.get("origin")
    if settings.ENVIRONMENT.lower() == "production" and origin:
        allowed = [o.rstrip("/") for o in settings.CORS_ORIGINS]
        if origin.rstrip("/") not in allowed and "*" not in allowed:
            logger.warning(f"Rejected WebSocket connection from unauthorized origin: {origin}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Cross-origin access rejected")
            return

    # 3. Authentication & Authorization guard
    require_auth = getattr(settings, "REQUIRE_WS_AUTH", False)
    if require_auth or (token is not None):
        if not _is_valid_token(token):
            logger.warning("Rejected unauthorized WebSocket connection: invalid or missing authentication token.")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Unauthorized WebSocket credentials")
            return

    await ws_dispatcher.connect(websocket)
    try:
        while True:
            # Keep-alive ping/pong listener
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_dispatcher.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket client error: {e}")
        ws_dispatcher.disconnect(websocket)
