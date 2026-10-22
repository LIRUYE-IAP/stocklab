from collections.abc import Sequence


def _ma(values: Sequence[float], period: int) -> float | None:
    return sum(values[-period:]) / period if len(values) >= period else None


def _ema_series(values: Sequence[float], period: int) -> list[float]:
    if not values:
        return []
    alpha = 2 / (period + 1)
    result = [values[0]]
    for value in values[1:]:
        result.append(alpha * value + (1 - alpha) * result[-1])
    return result


def _rsi(values: Sequence[float], period: int = 14) -> float | None:
    if len(values) <= period:
        return None
    changes = [values[index] - values[index - 1] for index in range(len(values) - period, len(values))]
    gains = sum(max(change, 0) for change in changes) / period
    losses = sum(max(-change, 0) for change in changes) / period
    if losses == 0:
        return 100.0
    return 100 - 100 / (1 + gains / losses)


def calculate_technical(closes: Sequence[float]) -> dict:
    if not closes:
        return {}
    ema12, ema26 = _ema_series(closes, 12), _ema_series(closes, 26)
    dif = [a - b for a, b in zip(ema12, ema26)]
    dea = _ema_series(dif, 9)
    ma5, ma10, ma20, ma60, ma120, ma250 = (_ma(closes, n) for n in (5, 10, 20, 60, 120, 250))
    rsi14 = _rsi(closes)
    score = 50
    latest = closes[-1]
    for average, points in ((ma5, 5), (ma10, 5), (ma20, 8), (ma60, 8)):
        if average is not None:
            score += points if latest >= average else -points
    if dif and dea:
        score += 10 if dif[-1] >= dea[-1] else -10
    if rsi14 is not None and rsi14 > 80:
        score -= 8
    return {"ma5": ma5, "ma10": ma10, "ma20": ma20, "ma60": ma60, "ma120": ma120, "ma250": ma250, "macd_dif": dif[-1] if dif else None, "macd_dea": dea[-1] if dea else None, "macd_hist": (dif[-1] - dea[-1]) * 2 if dif and dea else None, "rsi14": rsi14, "technical_score": max(0, min(100, score)), "algorithm_version": "technical-v1"}


def _percentile(values: Sequence[float], current: float) -> float | None:
    if not values:
        return None
    low, high = min(values), max(values)
    return 50.0 if high == low else (current - low) / (high - low) * 100


def calculate_position(closes: Sequence[float]) -> dict:
    if not closes:
        return {}
    current = closes[-1]
    values60, values126, values250, values750 = closes[-60:], closes[-126:], closes[-250:], closes[-750:]
    high60, high52, low52 = max(values60), max(values250), min(values250)
    return {"price_percentile_6m": _percentile(values126, current), "price_percentile_1y": _percentile(values250, current), "price_percentile_3y": _percentile(values750, current), "distance_60d_high": (current / high60 - 1) * 100, "distance_52w_high": (current / high52 - 1) * 100, "distance_52w_low": (current / low52 - 1) * 100, "algorithm_version": "position-v1"}
