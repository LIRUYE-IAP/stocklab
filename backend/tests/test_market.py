from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.providers.ifind import IFindProvider
from app.providers.symbols import from_vendor, normalize_internal, to_vendor
from app.main import app


def test_symbol_round_trip_and_exchange_identity():
    assert to_vendor("SZ.000630") == "000630.SZ"
    assert from_vendor("000001.SH") == "SH.000001"
    assert normalize_internal("000001.SZ") == "SZ.000001"
    assert normalize_internal("000001.SH") != normalize_internal("000001.SZ")
    with pytest.raises(ValueError):
        normalize_internal("000630")


def test_ifind_contract_parser_maps_by_code_not_request_order():
    provider = IFindProvider(Settings())
    payload = {
        "errorcode": 0,
        "data": {"tables": [{
            "thscode": ["002155.SZ", "000630.SZ"],
            "table": {"latest": [24.31, 5.86], "open": [23.46, 5.66], "high": [24.55, 5.92], "low": [23.31, 5.61]},
        }]},
    }
    result = provider._parse(payload, ["SZ.000630", "SZ.002155"])
    assert result["SZ.000630"].price == 5.86
    assert result["SZ.002155"].price == 24.31
    assert result["SZ.000630"].change is None
    assert "supplier_trade_time_unavailable" in result["SZ.000630"].quality_flags


def test_ifind_contract_parser_marks_partial_and_missing():
    provider = IFindProvider(Settings())
    payload = {"errorcode": 0, "data": {"tables": [{"thscode": "000630.SZ", "table": {"latest": None}}]}}
    result = provider._parse(payload, ["SZ.000630", "SZ.002155"])
    assert result["SZ.000630"].availability == "partial"
    assert result["SZ.002155"].availability == "unavailable"


def test_api_without_credentials_is_explicit_demo_and_rejects_ambiguous_code():
    client = TestClient(app)
    response = client.get("/api/v1/realtime/quotes", params={"symbols": "SZ.000630"})
    assert response.status_code == 200
    quote = response.json()["quotes"][0]
    assert quote["source"] == "mock"
    assert quote["is_demo"] is True
    assert quote["fallback_reason"] == "DATA_MODE=mock; live providers were not called"
    assert client.get("/api/v1/realtime/quotes/000630").status_code == 422
