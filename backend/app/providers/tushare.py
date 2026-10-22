import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.config import Settings
from app.providers.base import ProviderError, RealtimeMarketProvider
from app.providers.symbols import to_vendor
from app.schemas import Quote


class TushareProvider(RealtimeMarketProvider):
    name = "tushare"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.timezone = ZoneInfo(settings.quote_timezone)

    @property
    def configured(self) -> bool:
        return bool(self.settings.tushare_token)

    async def get_quotes(self, symbols: list[str]) -> dict[str, Quote]:
        if not self.configured:
            raise ProviderError("Tushare token is not configured", retryable=False, code="not_configured")
        if self.settings.tushare_realtime_enabled:
            return await asyncio.to_thread(self._minute_quotes, symbols)
        return await asyncio.to_thread(self._eod_quotes, symbols)

    def _client(self):
        try:
            import tushare as ts
        except ImportError as exc:
            raise ProviderError("tushare package is not installed", retryable=False, code="dependency_missing") from exc
        return ts.pro_api(self.settings.tushare_token)

    def _minute_quotes(self, symbols: list[str]) -> dict[str, Quote]:
        pro = self._client()
        frame = pro.rt_min(ts_code=",".join(to_vendor(s) for s in symbols), freq="1MIN")
        return self._from_frame(frame, symbols, "minute")

    def _eod_quotes(self, symbols: list[str]) -> dict[str, Quote]:
        pro = self._client()
        now = datetime.now(self.timezone)
        rows = []
        for symbol in symbols:
            frame = pro.daily(ts_code=to_vendor(symbol), start_date="20200101")
            if frame is not None and not frame.empty:
                rows.append(frame.iloc[0].to_dict())
        return self._from_rows(rows, symbols, "eod", now)

    def _from_frame(self, frame, symbols: list[str], granularity: str) -> dict[str, Quote]:
        now = datetime.now(self.timezone)
        rows = [] if frame is None else frame.to_dict("records")
        latest: dict[str, dict] = {}
        for row in rows:
            latest[row.get("ts_code") or row.get("code")] = row
        return self._from_rows(list(latest.values()), symbols, granularity, now)

    def _from_rows(self, rows: list[dict], symbols: list[str], granularity: str, now: datetime) -> dict[str, Quote]:
        by_code = {str(row.get("ts_code") or row.get("code")): row for row in rows}
        result: dict[str, Quote] = {}
        for symbol in symbols:
            row = by_code.get(to_vendor(symbol))
            if not row:
                continue
            price = float(row.get("close")) if row.get("close") is not None else None
            pre_close = float(row.get("pre_close")) if row.get("pre_close") is not None else None
            change = price - pre_close if price is not None and pre_close is not None else None
            trade_time = self._parse_trade_time(row.get("time")) if granularity == "minute" else None
            # Tushare rt_min already returns shares/yuan. The daily endpoint returns
            # lots (100 shares) and thousand yuan, so only EOD fallback needs scaling.
            volume = self._number(row.get("vol"))
            amount = self._number(row.get("amount"))
            if granularity == "eod":
                volume = volume * 100 if volume is not None else None
                amount = amount * 1_000 if amount is not None else None
            quality_flags = []
            if trade_time is None:
                quality_flags.append("supplier_trade_time_unavailable")
            if granularity == "eod":
                quality_flags.append("eod_fallback")
            result[symbol] = Quote(
                symbol=symbol, price=price, pre_close=pre_close, change=change,
                change_pct=change / pre_close * 100 if change is not None and pre_close else None,
                open=row.get("open"), high=row.get("high"), low=row.get("low"), volume=volume, amount=amount,
                source="tushare", granularity=granularity, trade_time=trade_time, received_at=now,
                trading_date=(trade_time.date().isoformat() if trade_time else self._format_trade_date(row.get("trade_date"))),
                market_status="unknown", quality_flags=quality_flags,
            )
        return result

    @staticmethod
    def _number(value) -> float | None:
        return float(value) if value is not None else None

    def _parse_trade_time(self, value) -> datetime | None:
        if value is None:
            return None
        raw = str(value).strip()
        for pattern in (None, "%Y%m%d%H%M%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                parsed = datetime.fromisoformat(raw) if pattern is None else datetime.strptime(raw, pattern)
                return parsed.replace(tzinfo=parsed.tzinfo or self.timezone)
            except ValueError:
                continue
        return None

    @staticmethod
    def _format_trade_date(value) -> str | None:
        raw = str(value or "").strip()
        if len(raw) == 8 and raw.isdigit():
            return f"{raw[:4]}-{raw[4:6]}-{raw[6:]}"
        return raw or None
