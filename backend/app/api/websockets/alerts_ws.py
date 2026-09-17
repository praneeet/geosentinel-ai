import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.alerts.websocket import ws_dispatcher

logger = logging.getLogger("geosentinel.ws_router")
router = APIRouter()

@router.websocket("/ws/alerts")
async def websocket_alerts_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint streaming real-time critical risk alerts (R > 75)
    to connected client dashboards without requiring manual page refresh.
    """
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
