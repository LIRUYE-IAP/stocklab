from fastapi.testclient import TestClient

from app.main import app


def test_websocket_ping_and_subscription_ack():
    with TestClient(app) as client:
        with client.websocket_connect("/api/v1/ws/quotes", headers={"origin": "http://127.0.0.1:5173"}) as socket:
            socket.send_json({"action": "ping"})
            assert socket.receive_json() == {"type": "pong"}
            socket.send_json({"action": "subscribe", "symbols": ["SZ.000630"]})
            assert socket.receive_json() == {"type": "ack", "symbols": ["SZ.000630"]}
