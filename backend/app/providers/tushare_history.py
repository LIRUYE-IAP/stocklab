import asyncio
from typing import Any, Callable

from app.core.config import Settings
from app.providers.base import HistoryMarketProvider, ProviderError
from app.providers.symbols import to_vendor
from app.providers.tushare_mapper import map_adj_factor, map_daily, map_daily_basic, map_price_limit, map_stock_basic, parse_date


class TushareHistoryProvider(HistoryMarketProvider):
    name = "tushare"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @property
    def configured(self) -> bool:
        return bool(self.settings.tushare_token)

    def _client(self):
        if not self.configured:
            raise ProviderError("Tushare token is not configured", retryable=False, code="not_configured")
        try:
            import tushare as ts
        except ImportError as exc:
            raise ProviderError("tushare package is not installed", retryable=False, code="dependency_missing") from exc
        return ts.pro_api(self.settings.tushare_token)

    async def _call(self, method: str, mapper: Callable[[dict[str, Any]], dict[str, Any]], **params) -> list[dict]:
        def request():
            client = self._client()
            frame = getattr(client, method)(**params)
            if frame is None or frame.empty:
                return []
            return [mapper(row) for row in frame.to_dict("records")]
        delays = (1, 3, 10)
        for attempt, delay in enumerate(delays, start=1):
            try:
                return await asyncio.to_thread(request)
            except ProviderError:
                raise
            except Exception as exc:
                message = str(exc)
                retryable = any(marker in message.lower() for marker in ("timeout", "429", "too many", "5xx", "connection"))
                if not retryable or attempt == len(delays):
                    raise ProviderError(f"Tushare {method} failed: {message}", retryable=retryable, code="request_failed") from exc
                await asyncio.sleep(delay)
        return []

    async def get_stock_basic(self, list_statuses: tuple[str, ...] = ("L", "P", "D")) -> list[dict]:
        rows: list[dict] = []
        for status in list_statuses:
            rows.extend(await self._call("stock_basic", map_stock_basic, exchange="", list_status=status, fields="ts_code,symbol,name,area,industry,market,exchange,list_status,list_date,delist_date"))
        return rows

    async def get_trade_calendar(self, start_date: str, end_date: str) -> list[dict]:
        def mapper(exchange: str):
            def apply(row: dict[str, Any]) -> dict:
                return {"exchange": exchange, "trade_date": parse_date(row.get("cal_date")), "is_open": str(row.get("is_open")) == "1", "previous_trade_date": parse_date(row.get("pretrade_date")), "source": "tushare"}
            return apply
        rows: list[dict] = []
        for vendor_exchange, exchange in (("SSE", "SH"), ("SZSE", "SZ")):
            rows.extend(await self._call("trade_cal", mapper(exchange), exchange=vendor_exchange, start_date=start_date, end_date=end_date, fields="exchange,cal_date,is_open,pretrade_date"))
        return rows

    async def get_daily(self, symbol: str, start_date: str, end_date: str) -> list[dict]:
        return await self._call("daily", map_daily, ts_code=to_vendor(symbol), start_date=start_date, end_date=end_date)

    async def get_daily_basic(self, symbol: str, start_date: str, end_date: str) -> list[dict]:
        return await self._call("daily_basic", map_daily_basic, ts_code=to_vendor(symbol), start_date=start_date, end_date=end_date)

    async def get_adj_factor(self, symbol: str, start_date: str, end_date: str) -> list[dict]:
        return await self._call("adj_factor", map_adj_factor, ts_code=to_vendor(symbol), start_date=start_date, end_date=end_date)

    async def get_price_limits(self, symbol: str, start_date: str, end_date: str) -> list[dict]:
        return await self._call("stk_limit", map_price_limit, ts_code=to_vendor(symbol), start_date=start_date, end_date=end_date)

    async def get_st_status(self, symbol: str, start_date: str, end_date: str) -> list[dict]:
        def mapper(row: dict[str, Any]) -> dict:
            name = str(row.get("name") or "")
            return {"start_date": parse_date(row.get("start_date")), "end_date": parse_date(row.get("end_date")), "stock_name": name, "is_st": "ST" in name.upper(), "source": "tushare"}
        return await self._call("namechange", mapper, ts_code=to_vendor(symbol), start_date=start_date, end_date=end_date, fields="ts_code,name,start_date,end_date,change_reason")
