from datetime import datetime, timedelta, timezone

from app.schemas import Quote
from app.realtime.cache import mark_cache_quote
from app.services.market_status import derive_market_status


def test_cache_quote_becomes_stale_after_threshold():
    quote = Quote(symbol="SZ.000630", price=5.86, source="ifind", granularity="snapshot", received_at=datetime.now(timezone.utc) - timedelta(seconds=121))
    cached = mark_cache_quote(quote, 120, "provider timeout")
    assert cached.source == "cache"
    assert cached.is_stale is True
    assert derive_market_status(cached.trade_time, cached.received_at, 120) == "STALE"
