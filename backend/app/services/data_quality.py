from typing import Any


def validate_daily_row(row: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    open_price, high, low, close = (row.get(key) for key in ("open", "high", "low", "close"))
    if high is not None and low is not None and high < low:
        errors.append("high_below_low")
    if high is not None and open_price is not None and high < open_price:
        errors.append("high_below_open")
    if high is not None and close is not None and high < close:
        errors.append("high_below_close")
    if low is not None and open_price is not None and low > open_price:
        errors.append("low_above_open")
    if low is not None and close is not None and low > close:
        errors.append("low_above_close")
    if row.get("volume_shares") is not None and row["volume_shares"] < 0:
        errors.append("negative_volume")
    if row.get("amount_cny") is not None and row["amount_cny"] < 0:
        errors.append("negative_amount")
    return errors
