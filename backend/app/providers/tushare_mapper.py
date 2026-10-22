from datetime import datetime
from math import isnan
from typing import Any

from app.providers.symbols import from_vendor


def value(row: dict[str, Any], key: str, multiplier: float = 1.0) -> float | None:
    raw = row.get(key)
    if raw is None or raw == "":
        return None
    try:
        number = float(raw)
        return None if isnan(number) else number * multiplier
    except (TypeError, ValueError):
        return None


def parse_date(raw: Any):
    if not raw:
        return None
    return datetime.strptime(str(raw), "%Y%m%d").date()


def map_board(exchange: str, market: str | None, code: str) -> str:
    market = (market or "").upper()
    if exchange == "BJ" or market in {"北交所", "BSE"}:
        return "BSE"
    if code.startswith(("300", "301")) or market in {"创业板", "CHINEXT"}:
        return "CHINEXT"
    if code.startswith("688") or market in {"科创板", "STAR"}:
        return "STAR"
    if exchange in {"SH", "SZ"} and (code.startswith(("600", "601", "603", "605", "000", "001", "002", "003")) or market in {"主板", "MAIN"}):
        return "MAIN"
    return "UNKNOWN"


def map_stock_basic(row: dict[str, Any]) -> dict[str, Any]:
    symbol = from_vendor(str(row["ts_code"]))
    exchange, code = symbol.split(".")
    return {"symbol": symbol, "code": code, "name": str(row.get("name") or ""), "exchange": exchange, "board": map_board(exchange, row.get("market"), code), "industry": row.get("industry") or None, "area": row.get("area") or None, "list_date": parse_date(row.get("list_date")), "list_status": str(row.get("list_status") or "L"), "delist_date": parse_date(row.get("delist_date")), "source": "tushare"}


def map_daily(row: dict[str, Any]) -> dict[str, Any]:
    return {"trade_date": parse_date(row.get("trade_date")), "open": value(row, "open"), "high": value(row, "high"), "low": value(row, "low"), "close": value(row, "close"), "pre_close": value(row, "pre_close"), "change_amount": value(row, "change"), "pct_change": value(row, "pct_chg"), "volume_shares": value(row, "vol", 100), "amount_cny": value(row, "amount", 1000), "source": "tushare"}


def map_daily_basic(row: dict[str, Any]) -> dict[str, Any]:
    return {"trade_date": parse_date(row.get("trade_date")), "turnover_rate": value(row, "turnover_rate"), "turnover_rate_free": value(row, "turnover_rate_f"), "volume_ratio": value(row, "volume_ratio"), "pe": value(row, "pe"), "pe_ttm": value(row, "pe_ttm"), "pb": value(row, "pb"), "ps": value(row, "ps"), "ps_ttm": value(row, "ps_ttm"), "total_share_shares": value(row, "total_share", 10_000), "float_share_shares": value(row, "float_share", 10_000), "free_share_shares": value(row, "free_share", 10_000), "total_market_cap_cny": value(row, "total_mv", 10_000), "float_market_cap_cny": value(row, "circ_mv", 10_000), "source": "tushare"}


def map_adj_factor(row: dict[str, Any]) -> dict[str, Any]:
    return {"trade_date": parse_date(row.get("trade_date")), "adj_factor": value(row, "adj_factor"), "source": "tushare"}


def map_price_limit(row: dict[str, Any]) -> dict[str, Any]:
    return {"trade_date": parse_date(row.get("trade_date")), "up_limit": value(row, "up_limit"), "down_limit": value(row, "down_limit"), "source": "tushare"}
