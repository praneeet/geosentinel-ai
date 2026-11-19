import json
import uuid
import asyncio
import logging
from typing import Set, Optional
from fastapi import WebSocket
from app.config import settings

logger = logging.getLogger("geosentinel.websocket")

class WebSocketAlertDispatcher:
    """
    Manages real-time WebSocket client connections and alert broadcasts.
    Supports local in-memory dispatching with automatic Redis Pub/Sub backplane
    synchronization for multi-worker / multi-container deployments.
    """

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.instance_id: str = str(uuid.uuid4())
        self._redis = None
        self._listener_task: Optional[asyncio.Task] = None
        self._pubsub_started: bool = False

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total connections: {len(self.active_connections)}")

    async def init_redis_pubsub(self):
        """Initializes optional Redis Pub/Sub listener if REDIS_URL is configured."""
        if self._pubsub_started or not settings.REDIS_URL:
            return
        self._pubsub_started = True

        try:
            import redis.asyncio as aioredis
            self._redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            pubsub = self._redis.pubsub()
            await pubsub.subscribe("geosentinel:alerts")
            logger.info("Connected to Redis Pub/Sub channel 'geosentinel:alerts' for multi-worker sync.")

            async def _listen():
                try:
                    async for message in pubsub.listen():
                        if message and message.get("type") == "message":
                            try:
                                data = json.loads(message["data"])
                                if data.get("source_id") != self.instance_id:
                                    payload = data.get("payload")
                                    if payload:
                                        await self._send_to_local_clients(payload)
                            except Exception as parse_err:
                                logger.warning(f"Error parsing Redis alert message: {parse_err}")
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    logger.warning(f"Redis Pub/Sub listener disconnected: {e}")

            self._listener_task = asyncio.create_task(_listen())
        except Exception as e:
            logger.info(f"Redis Pub/Sub not available ({e}). Running in standalone in-memory mode.")
            self._redis = None

    async def _send_to_local_clients(self, payload: dict):
        if not self.active_connections:
            return
        message = json.dumps(payload, default=str)
        dead_connections = set()
        for conn in self.active_connections:
            try:
                await conn.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to send alert to client: {e}")
                dead_connections.add(conn)
        for dead in dead_connections:
            self.active_connections.discard(dead)

    async def broadcast_alert(self, payload: dict):
        """Broadcasts critical alert to local clients and publishes to Redis channel."""
        # 1. Send to local connected clients
        await self._send_to_local_clients(payload)

        # 2. Publish to Redis channel for other worker processes if connected
        if self._redis is not None:
            try:
                msg = json.dumps({
                    "source_id": self.instance_id,
                    "payload": payload,
                }, default=str)
                await self._redis.publish("geosentinel:alerts", msg)
            except Exception as e:
                logger.warning(f"Failed to publish alert to Redis: {e}")

ws_dispatcher = WebSocketAlertDispatcher()
