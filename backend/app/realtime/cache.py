import json
from datetime import datetime, timezone

from app.schemas import Quote


class MemoryQuoteCache:
    def __init__(self) -> None:
        self._quotes: dict[str, Quote] = {}

    async def get_many(self, symbols: list[str]) -> dict[str, Quote]:
        return {symbol: self._quotes[symbol].model_copy(deep=True) for symbol in symbols if symbol in self._quotes}

    async def put_many(self, quotes: dict[str, Quote]) -> None:
        self._quotes.update({key: value.model_copy(deep=True) for key, value in quotes.items() if value.availability != "unavailable"})


class RedisQuoteCache:
    def __init__(self, url: str, ttl: int) -> None:
        import redis.asyncio as redis

        self.client = redis.from_url(url, decode_responses=True)
        self.ttl = ttl

    async def get_many(self, symbols: list[str]) -> dict[str, Quote]:
        keys = [f"quote:{symbol}" for symbol in symbols]
        values = await self.client.mget(keys)
        return {symbol: Quote.model_validate_json(value) for symbol, value in zip(symbols, values) if value}

    async def put_many(self, quotes: dict[str, Quote]) -> None:
        pipeline = self.client.pipeline()
        for symbol, quote in quotes.items():
            if quote.availability != "unavailable":
                pipeline.setex(f"quote:{symbol}", self.ttl, quote.model_dump_json())
        await pipeline.execute()


def mark_cache_quote(quote: Quote, stale_after: int, reason: str) -> Quote:
    age = (datetime.now(timezone.utc) - quote.received_at.astimezone(timezone.utc)).total_seconds()
    return quote.model_copy(update={"source": "cache", "is_stale": age > stale_after, "fallback_reason": reason, "quality_flags": [*quote.quality_flags, "last_known_quote"]})
