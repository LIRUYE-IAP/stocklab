from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.core.config import Settings
from app.services.quote_service import QuoteService


def test_batch_quote_limit_and_explicit_mock_mode():
    with TestClient(app) as client:
        too_many = ",".join(["SZ.000630"] * 101)
        assert client.get("/api/v1/realtime/quotes", params={"symbols": too_many}).status_code == 400
        response = client.get("/api/v1/realtime/quotes", params={"symbols": "SZ.000630"})
        assert response.status_code == 200
        quote = response.json()["quotes"][0]
        assert quote["is_demo"] is True
        assert quote["market_status"] in {"PRE_MARKET", "OPEN", "LUNCH_BREAK", "CLOSED", "STALE"}


@pytest.mark.asyncio
async def test_live_mode_without_credentials_never_silently_returns_demo():
    service = QuoteService(Settings(data_mode="live", market_mode="auto", allow_demo=True, ifind_refresh_token="", tushare_token=""))
    quote = (await service.get_quotes(["SZ.000630"]))["SZ.000630"]
    assert quote.source == "unavailable"
    assert quote.is_demo is False
