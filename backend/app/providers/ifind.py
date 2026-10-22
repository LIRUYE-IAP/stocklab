import asyncio
import time
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

import httpx

from app.core.config import Settings
from app.providers.base import ProviderError, RealtimeMarketProvider
from app.providers.ifind_auth import IFindTokenManager
from app.providers.symbols import from_vendor, to_vendor
from app.schemas import Quote


def _number(value: Any) -> float | None:
    try:
        if value in (None, "", "--", "null"):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


class IFindProvider(RealtimeMarketProvider):
    name = "ifind"

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self.settings = settings
        self.client = client or httpx.AsyncClient(timeout=httpx.Timeout(8, connect=4))
        self.tokens = IFindTokenManager(self.client, settings.ifind_base_url, settings.ifind_refresh_token, settings.ifind_access_token)
        self._request_lock = asyncio.Lock()
        self._last_request = 0.0

    @property
    def configured(self) -> bool:
        return self.tokens.configured

    async def get_quotes(self, symbols: list[str]) -> dict[str, Quote]:
        if not symbols:
            return {}
        payload = await self._request(symbols)
        return self._parse(payload, symbols)

    async def _request(self, symbols: list[str], retry_auth: bool = True) -> dict[str, Any]:
        async with self._request_lock:
            minimum_gap = 1 / max(self.settings.ifind_max_qps, 0.1)
            remaining = minimum_gap - (time.monotonic() - self._last_request)
            if remaining > 0:
                await asyncio.sleep(remaining)
            self._last_request = time.monotonic()
        token = await self.tokens.get()
        response = await self.client.post(
            f"{self.settings.ifind_base_url.rstrip('/')}/real_time_quotation",
            headers={"Content-Type": "application/json", "access_token": token, "ifindlang": "cn"},
            json={"codes": ",".join(to_vendor(s) for s in symbols), "indicators": self.settings.ifind_quote_indicators},
        )
        if response.status_code in (401, 403) and retry_auth:
            self.tokens.invalidate()
            return await self._request(symbols, retry_auth=False)
        response.raise_for_status()
        data = response.json()
        error_code = data.get("errorcode", data.get("error_code", 0)) if isinstance(data, dict) else -1
        if error_code not in (0, "0", None):
            message = str(data.get("errmsg") or data.get("message") or "iFinD business error")
            auth_error = "token" in message.lower() or str(error_code) in {"-1302", "-1303"}
            if auth_error and retry_auth:
                self.tokens.invalidate()
                return await self._request(symbols, retry_auth=False)
            raise ProviderError(message, retryable=not any(x in message for x in ("权限", "到期", "IP")), code=str(error_code))
        return data

    def _parse(self, payload: dict[str, Any], requested: list[str]) -> dict[str, Quote]:
        raw = payload.get("data", payload)
        tables = raw.get("tables") if isinstance(raw, dict) else None
        if tables is None and isinstance(payload.get("tables"), list):
            tables = payload["tables"]
        if not isinstance(tables, list):
            raise ProviderError("Unrecognized iFinD quote response shape", retryable=False, code="schema_error")
        now = datetime.now(timezone.utc)
        result: dict[str, Quote] = {}
        for table in tables:
            if not isinstance(table, dict):
                continue
            codes = table.get("thscode") or table.get("codes") or table.get("code")
            values = table.get("table", table.get("data", {}))
            code_list = codes if isinstance(codes, list) else [codes]
            if not isinstance(values, dict):
                continue
            for index, vendor_code in enumerate(code_list):
                if not vendor_code:
                    continue
                try:
                    symbol = from_vendor(str(vendor_code))
                except ValueError:
                    continue
                def pick(*keys: str) -> Any:
                    for key in keys:
                        value = values.get(key)
                        if isinstance(value, list):
                            return value[index] if index < len(value) else None
                        if value is not None:
                            return value
                    return None
                price = _number(pick("latest", "close", "price"))
                pre_close = _number(pick("preClose", "pre_close", "preclose"))
                change = price - pre_close if price is not None and pre_close is not None else None
                change_pct = change / pre_close * 100 if change is not None and pre_close else None
                raw_time = pick("time", "tradeTime", "trade_time", "datetime")
                trade_time = None
                if raw_time:
                    try:
                        trade_time = datetime.fromisoformat(str(raw_time).replace("Z", "+00:00"))
                        if trade_time.tzinfo is None:
                            trade_time = trade_time.replace(tzinfo=ZoneInfo(self.settings.quote_timezone))
                    except ValueError:
                        pass
                result[symbol] = Quote(
                    symbol=symbol, price=price, pre_close=pre_close, change=change, change_pct=change_pct,
                    open=_number(pick("open")), high=_number(pick("high")), low=_number(pick("low")),
                    volume=_number(pick("volume", "vol")), amount=_number(pick("amount")),
                    bid_price_1=_number(pick("bidPrice1", "bid_price_1", "bid1")), ask_price_1=_number(pick("askPrice1", "ask_price_1", "ask1")),
                    bid_volume_1=_number(pick("bidVolume1", "bid_volume_1", "bidVol1")), ask_volume_1=_number(pick("askVolume1", "ask_volume_1", "askVol1")),
                    source="ifind", granularity="snapshot", received_at=now,
                    trade_time=trade_time, trading_date=trade_time.date().isoformat() if trade_time else None, market_status="unknown",
                    availability="available" if price is not None else "partial",
                    quality_flags=([] if trade_time else ["supplier_trade_time_unavailable"]) + ([] if price is not None else ["missing_latest"]),
                )
        missing = set(requested) - set(result)
        for symbol in missing:
            result[symbol] = Quote(symbol=symbol, source="unavailable", granularity="unknown", received_at=now, availability="unavailable", quality_flags=["missing_symbol"])
        return result
