import asyncio
import json
import pytest
from app.alerts.websocket import WebSocketAlertDispatcher

class MockWebSocket:
    """Mock WebSocket client tracking received messages and state."""
    def __init__(self):
        self.accepted = False
        self.closed = False
        self.messages = []
        self.close_code = None
        self.close_reason = None

    async def accept(self):
        self.accepted = True

    async def close(self, code=1000, reason=""):
        self.closed = True
        self.close_code = code
        self.close_reason = reason

    async def send_text(self, text: str):
        self.messages.append(text)

@pytest.mark.asyncio
async def test_distributed_websocket_cross_instance_alert():
    """
    Spawns two independent backend dispatcher instances connected to real Redis Pub/Sub.
    Verifies that an alert broadcast from Instance 1 is received by a WebSocket client
    connected exclusively to Instance 2.
    """
    disp1 = WebSocketAlertDispatcher()
    disp2 = WebSocketAlertDispatcher()

    # Ensure unique instance IDs
    assert disp1.instance_id != disp2.instance_id

    # Connect both to real Redis Pub/Sub
    await disp1.init_redis_pubsub()
    await disp2.init_redis_pubsub()

    # Wait for Redis subscriptions to establish
    await asyncio.sleep(0.5)

    client1 = MockWebSocket()
    client2 = MockWebSocket()

    await disp1.connect(client1)
    await disp2.connect(client2)

    try:
        test_alert = {
            "country": "UKR",
            "country_name": "Ukraine",
            "risk_score": 88.5,
            "tier": "Severe",
            "trigger": "critical_threshold",
            "evidence": ["ev-101", "ev-102"],
        }

        # Broadcast from Instance 1
        await disp1.broadcast_alert(test_alert)

        # Wait briefly for Redis Pub/Sub message propagation
        await asyncio.sleep(0.5)

        # Verify client on Instance 1 received message locally
        assert len(client1.messages) >= 1
        data1 = json.loads(client1.messages[0])
        assert data1["country"] == "UKR"
        assert data1["risk_score"] == 88.5

        # Verify client on Instance 2 received message through Redis synchronization!
        assert len(client2.messages) >= 1
        data2 = json.loads(client2.messages[0])
        assert data2["country"] == "UKR"
        assert data2["risk_score"] == 88.5

    finally:
        await disp1.close()
        await disp2.close()

@pytest.mark.asyncio
async def test_websocket_graceful_fallback_without_redis():
    """
    Verifies that when Redis is disconnected or unavailable,
    broadcast_alert continues to function gracefully for all locally connected clients.
    """
    disp = WebSocketAlertDispatcher()
    # No Redis initialized
    client = MockWebSocket()
    await disp.connect(client)

    try:
        test_alert = {
            "country": "TWN",
            "country_name": "Taiwan",
            "risk_score": 79.2,
            "tier": "Severe",
        }

        # Must not raise an error
        await disp.broadcast_alert(test_alert)

        assert len(client.messages) == 1
        data = json.loads(client.messages[0])
        assert data["country"] == "TWN"
    finally:
        await disp.close()

@pytest.mark.asyncio
async def test_websocket_dead_connection_pruning():
    """Verifies that disconnecting or failing clients are pruned automatically."""
    disp = WebSocketAlertDispatcher()
    client_live = MockWebSocket()

    class FailingWebSocket(MockWebSocket):
        async def send_text(self, text: str):
            raise ConnectionResetError("Connection dropped by remote peer")

    client_failing = FailingWebSocket()

    await disp.connect(client_live)
    await disp.connect(client_failing)
    assert len(disp.active_connections) == 2

    # Broadcast triggers prune of failing connection
    await disp.broadcast_alert({"test": "data"})

    assert len(disp.active_connections) == 1
    assert client_live in disp.active_connections
    assert client_failing not in disp.active_connections
    await disp.close()

@pytest.mark.asyncio
async def test_websocket_origin_validation_production():
    """Verify that unauthorized origins are rejected in production environment."""
    from app.api.websockets.alerts_ws import websocket_alerts_endpoint
    from app.config import settings

    old_env = settings.ENVIRONMENT
    old_origins = settings.CORS_ORIGINS
    try:
        settings.ENVIRONMENT = "production"
        settings.CORS_ORIGINS = ["http://localhost:5173"]

        mock_ws = MockWebSocket()
        mock_ws.headers = {"origin": "http://malicious-site.com"}

        await websocket_alerts_endpoint(mock_ws)
        assert mock_ws.closed is True
        assert mock_ws.close_code == 1008
        assert "Cross-origin" in mock_ws.close_reason
    finally:
        settings.ENVIRONMENT = old_env
        settings.CORS_ORIGINS = old_origins

@pytest.mark.asyncio
async def test_websocket_unauthorized_token_rejection():
    """Verify that an invalid authentication token is rejected with WS 1008."""
    from app.api.websockets.alerts_ws import websocket_alerts_endpoint
    mock_ws = MockWebSocket()
    mock_ws.headers = {}

    await websocket_alerts_endpoint(mock_ws, token="invalid-forged-token")
    assert mock_ws.closed is True
    assert mock_ws.close_code == 1008
    assert "Unauthorized" in mock_ws.close_reason

@pytest.mark.asyncio
async def test_websocket_max_connections_guard():
    """Verify that connection requests exceeding MAX_WS_CONNECTIONS are rejected."""
    from app.api.websockets.alerts_ws import websocket_alerts_endpoint, MAX_WS_CONNECTIONS
    from app.alerts.websocket import ws_dispatcher

    old_conns = set(ws_dispatcher.active_connections)
    try:
        # Simulate pool at max capacity
        dummy_conns = {MockWebSocket() for _ in range(MAX_WS_CONNECTIONS)}
        ws_dispatcher.active_connections = dummy_conns

        mock_ws = MockWebSocket()
        mock_ws.headers = {}
        await websocket_alerts_endpoint(mock_ws)
        assert mock_ws.closed is True
        assert mock_ws.close_code == 1008
        assert "capacity" in mock_ws.close_reason
    finally:
        ws_dispatcher.active_connections = old_conns
