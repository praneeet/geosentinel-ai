import json
import logging
from typing import Set
from fastapi import WebSocket

logger = logging.getLogger("geosentinel.websocket")

class WebSocketAlertDispatcher:
    """Manages real-time WebSocket client connections and alert broadcasts."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast_alert(self, payload: dict):
        """Broadcasts critical alert payload to all connected clients."""
        if not self.active_connections:
            return

        message = json.dumps(payload, default=str)
        dead_connections = set()

        for conn in self.active_connections:
            try:
                await conn.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to send to client: {e}")
                dead_connections.add(conn)

        for dead in dead_connections:
            self.active_connections.discard(dead)

ws_dispatcher = WebSocketAlertDispatcher()
