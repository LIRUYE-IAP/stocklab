from datetime import datetime, timezone

import httpx

from app.core.config import Settings
from app.providers.base import ProviderError
from app.providers.ifind import IFindProvider
from app.providers.mock import MockProvider
from app.providers.symbols import normalize_internal
from app.providers.tushare import TushareProvider
from app.realtime.cache import MemoryQuoteCache, RedisQuoteCache, mark_cache_quote
from app.schemas import ProviderState, Quote


class QuoteService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.ifind = IFindProvider(settings)
        self.tushare = TushareProvider(settings)
        self.mock = MockProvider(settings.quote_timezone)
        self.memory_cache = MemoryQuoteCache()
        self.cache = RedisQuoteCache(settings.redis_url, settings.quote_cache_ttl_seconds) if settings.quote_cache_backend == "redis" else self.memory_cache
        self.active_source = "unavailable"
        self.last_success_at: datetime | None = None
        self.last_error: str | None = None

    async def get_quotes(self, symbols: list[str]) -> dict[str, Quote]:
        normalized = list(dict.fromkeys(normalize_internal(symbol) for symbol in symbols))
        if self.settings.data_mode == "mock" or self.settings.realtime_provider == "mock" or self.settings.market_mode == "mock":
            quotes = await self.mock.get_quotes(normalized)
            for quote in quotes.values():
                quote.fallback_reason = "DATA_MODE=mock; live providers were not called"
            await self._cache_put(quotes)
            self._success("mock")
            return quotes
        failures: list[str] = []
        if self.ifind.configured:
            try:
                quotes = await self.ifind.get_quotes(normalized)
                available = {k: v for k, v in quotes.items() if v.availability != "unavailable"}
                if available:
                    await self._cache_put(available)
                    self._success("ifind")
                    missing = [s for s in normalized if s not in available]
                    if not missing:
                        return quotes
                    return {**quotes, **await self._fallback(missing, "iFinD returned no quote for part of the request")}
            except (ProviderError, httpx.HTTPError, ValueError) as exc:
                failures.append(f"iFinD: {exc}")
        else:
            failures.append("iFinD: not configured")
        result = await self._fallback(normalized, "; ".join(failures))
        self.last_error = "; ".join(failures) if failures else None
        return result

    async def _fallback(self, symbols: list[str], reason: str) -> dict[str, Quote]:
        cached = await self._cache_get(symbols)
        result = {s: mark_cache_quote(q, self.settings.quote_stale_after_seconds, reason) for s, q in cached.items()}
        missing = [s for s in symbols if s not in result]
        if missing and self.tushare.configured:
            try:
                tushare_quotes = await self.tushare.get_quotes(missing)
                for quote in tushare_quotes.values():
                    quote.fallback_reason = reason
                result.update(tushare_quotes)
                await self._cache_put(tushare_quotes)
                missing = [s for s in missing if s not in tushare_quotes]
                if tushare_quotes:
                    self._success("tushare")
            except Exception as exc:  # Provider errors are surfaced as state, never as fake values.
                reason = f"{reason}; Tushare: {exc}"
        if missing and self.settings.data_mode != "live" and self.settings.market_mode == "auto" and self.settings.allow_demo:
            demo = await self.mock.get_quotes(missing)
            for quote in demo.values():
                quote.fallback_reason = reason
            result.update(demo)
            self._success("mock")
        for symbol in missing:
            if symbol not in result:
                result[symbol] = Quote(symbol=symbol, source="unavailable", granularity="unknown", received_at=datetime.now(timezone.utc), availability="unavailable", fallback_reason=reason)
        return result

    def _success(self, source: str) -> None:
        self.active_source = source
        self.last_success_at = datetime.now(timezone.utc)

    async def _cache_get(self, symbols: list[str]) -> dict[str, Quote]:
        try:
            return await self.cache.get_many(symbols)
        except Exception as exc:
            self.last_error = f"Redis cache unavailable: {exc}"
            self.cache = self.memory_cache
            return await self.memory_cache.get_many(symbols)

    async def _cache_put(self, quotes: dict[str, Quote]) -> None:
        try:
            await self.cache.put_many(quotes)
        except Exception as exc:
            self.last_error = f"Redis cache unavailable: {exc}"
            self.cache = self.memory_cache
            await self.memory_cache.put_many(quotes)

    def status(self) -> ProviderState:
        capabilities = ["realtime_quotes"] if self.ifind.configured else []
        if self.tushare.configured:
            capabilities.append("tushare_minute" if self.settings.tushare_realtime_enabled else "tushare_eod")
        if self.settings.allow_demo:
            capabilities.append("demo_quotes")
        return ProviderState(
            data_mode=self.settings.data_mode, history_provider=self.settings.history_provider, realtime_provider=self.settings.realtime_provider,
            configured_mode=self.settings.market_mode, active_source=self.active_source,
            ifind_configured=self.ifind.configured, tushare_configured=self.tushare.configured,
            tushare_realtime_enabled=self.settings.tushare_realtime_enabled,
            cache_backend="redis" if isinstance(self.cache, RedisQuoteCache) else "memory", allow_demo=self.settings.allow_demo,
            last_success_at=self.last_success_at, last_error=self.last_error, capabilities=capabilities,
            database_configured=bool(self.settings.database_url),
        )
