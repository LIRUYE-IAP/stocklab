from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo


def derive_market_status(trade_time: datetime | None, received_at: datetime, stale_after_seconds: int, timezone_name: str = "Asia/Shanghai", is_trade_day: bool | None = None) -> str:
    now_utc = datetime.now(timezone.utc)
    if (now_utc - received_at.astimezone(timezone.utc)).total_seconds() > stale_after_seconds:
        return "STALE"
    now = now_utc.astimezone(ZoneInfo(timezone_name))
    if is_trade_day is False or (is_trade_day is None and now.weekday() >= 5):
        return "CLOSED"
    local_time = now.time()
    if local_time < time(9, 15): return "PRE_MARKET"
    if time(9, 15) <= local_time <= time(11, 30) or time(13, 0) <= local_time <= time(15, 0): return "OPEN"
    if time(11, 30) < local_time < time(13, 0): return "LUNCH_BREAK"
    return "CLOSED"
