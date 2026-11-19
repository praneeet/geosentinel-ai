import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from app.alerts.websocket import ws_dispatcher
from app.config import settings

logger = logging.getLogger("geosentinel.ws_router")
router = APIRouter()

MAX_WS_CONNECTIONS = 500

@router.websocket("/ws/alerts")
async def websocket_alerts_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
):
    """
    WebSocket endpoint streaming real-time critical risk alerts (R > 75)
    to connected client dashboards.
    Implements origin validation, connection concurrency limits, and keep-alive ping/pong.
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
