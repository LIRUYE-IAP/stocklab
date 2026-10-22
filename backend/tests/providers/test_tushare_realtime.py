from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.config import Settings
from app.providers.tushare import TushareProvider


def test_rt_min_units_and_supplier_time_are_preserved():
    provider = TushareProvider(Settings())
    now = datetime(2026, 9, 9, 14, 31, tzinfo=ZoneInfo("Asia/Shanghai"))
    rows = [{
        "ts_code": "000630.SZ", "time": "2026-09-09 14:30:00", "open": 12.1,
        "high": 12.4, "low": 12.0, "close": 12.36, "pre_close": 12.0,
        "vol": 128_630, "amount": 1_582_000,
    }]

    quote = provider._from_rows(rows, ["SZ.000630"], "minute", now)["SZ.000630"]

    assert quote.volume == 128_630
    assert quote.amount == 1_582_000
    assert quote.trade_time.isoformat() == "2026-09-09T14:30:00+08:00"
    assert quote.trading_date == "2026-09-09"
    assert "supplier_trade_time_unavailable" not in quote.quality_flags


def test_daily_fallback_normalizes_lots_and_thousand_yuan():
    provider = TushareProvider(Settings())
    now = datetime(2026, 9, 9, 18, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
    rows = [{
        "ts_code": "000630.SZ", "trade_date": "20260908", "open": 12.1,
        "high": 12.4, "low": 12.0, "close": 12.36, "pre_close": 12.0,
        "vol": 1286.3, "amount": 1582.0,
    }]

    quote = provider._from_rows(rows, ["SZ.000630"], "eod", now)["SZ.000630"]

    assert quote.volume == 128_630
    assert quote.amount == 1_582_000
    assert quote.trading_date == "2026-09-08"
    assert quote.quality_flags == ["supplier_trade_time_unavailable", "eod_fallback"]
