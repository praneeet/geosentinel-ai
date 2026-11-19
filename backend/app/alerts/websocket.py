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
    Includes automated reconnection, subscription recovery, and graceful fallback.
    """

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.instance_id: str = str(uuid.uuid4())
        self._redis = None
        self._pubsub = None
        self._listener_task: Optional[asyncio.Task] = None
        self._is_running: bool = False
        self._reconnect_delay: float = 1.0

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total connections: {len(self.active_connections)}")

    async def init_redis_pubsub(self):
        """Initializes continuous Redis Pub/Sub listener with auto-reconnection and recovery."""
        if self._is_running or not settings.REDIS_URL:
            return
        self._is_running = True
        self._listener_task = asyncio.create_task(self._pubsub_manager_loop())

    async def _pubsub_manager_loop(self):
        """Persistent supervisor loop ensuring Redis connection recovery and subscription resilience."""
        import redis.asyncio as aioredis

        while self._is_running:
            try:
                logger.info(f"Connecting to Redis Pub/Sub at {settings.REDIS_URL}...")
                self._redis = aioredis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=3.0,
                    socket_keepalive=True,
                )
                await self._redis.ping()
                self._pubsub = self._redis.pubsub()
                await self._pubsub.subscribe("geosentinel:alerts")
                logger.info("Successfully subscribed to Redis Pub/Sub channel 'geosentinel:alerts'.")
                self._reconnect_delay = 1.0

                async for message in self._pubsub.listen():
                    if not self._is_running:
                        break
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
                break
            except Exception as e:
                logger.warning(
                    f"Redis Pub/Sub connection failure or drop: {e}. "
                    f"Retrying in {self._reconnect_delay:.1f}s (Graceful standalone fallback active)..."
                )
                await self._cleanup_redis()
                if self._is_running:
                    await asyncio.sleep(self._reconnect_delay)
                    self._reconnect_delay = min(15.0, self._reconnect_delay * 1.5)

        await self._cleanup_redis()

    async def _cleanup_redis(self):
        """Safely cleans up pubsub and redis connection objects."""
        if self._pubsub:
            try:
                await self._pubsub.unsubscribe("geosentinel:alerts")
                if hasattr(self._pubsub, "aclose"):
                    await self._pubsub.aclose()
                else:
                    await self._pubsub.close()
            except Exception:
                pass
            self._pubsub = None

        if self._redis:
            try:
                if hasattr(self._redis, "aclose"):
                    await self._redis.aclose()
                else:
                    await self._redis.close()
            except Exception:
                pass
            self._redis = None

    async def close(self):
        """Gracefully shuts down dispatcher, closing Redis and tasks."""
        self._is_running = False
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
            self._listener_task = None
        await self._cleanup_redis()

    async def _send_to_local_clients(self, payload: dict):
        if not self.active_connections:
            return
        message = json.dumps(payload, default=str)
        dead_connections = set()
        for conn in list(self.active_connections):
            try:
                await conn.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to send alert to client: {e}")
                dead_connections.add(conn)
        for dead in dead_connections:
            self.active_connections.discard(dead)

    async def broadcast_alert(self, payload: dict):
        """Broadcasts critical alert to local clients and publishes to Redis channel."""
        # 1. Immediate local dispatch to all connected dashboard browsers
        await self._send_to_local_clients(payload)

        # 2. Publish to Redis channel for cross-worker / cross-container synchronization
        if self._redis is not None and self._is_running:
            try:
                msg = json.dumps({
                    "source_id": self.instance_id,
                    "payload": payload,
                }, default=str)
                await self._redis.publish("geosentinel:alerts", msg)
            except Exception as e:
                logger.warning(f"Failed to publish alert to Redis: {e}. Graceful local delivery preserved.")

ws_dispatcher = WebSocketAlertDispatcher()
