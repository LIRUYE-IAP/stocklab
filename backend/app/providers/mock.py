import math
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from app.providers.base import RealtimeMarketProvider
from app.schemas import Quote

BASE = {
    "SH.000001": ("上证指数", 3915.28, 3883.44),
    "SZ.399001": ("深证成指", 12486.71, 12335.02),
    "SZ.399006": ("创业板指", 2782.46, 2736.76),
    "SH.000688": ("科创50", 1186.34, 1190.63),
    "SZ.000630": ("铜陵有色", 5.86, 5.68),
    "SZ.002155": ("湖南黄金", 24.31, 23.43),
    "SZ.002716": ("湖南白银", 4.72, 4.78),
    "SH.688256": ("寒武纪", 623.80, 609.30),
    "SZ.300750": ("宁德时代", 312.45, 310.04),
    "SH.603019": ("中科曙光", 78.62, 74.23),
    "SZ.000858": ("五粮液", 136.28, 137.71),
    "SH.601899": ("紫金矿业", 28.76, 28.24),
    "SZ.002230": ("科大讯飞", 58.43, 59.55),
    "SH.600036": ("招商银行", 43.86, 43.77),
}


class MockProvider(RealtimeMarketProvider):
    name = "mock"

    def __init__(self, timezone_name: str = "Asia/Shanghai") -> None:
        self.timezone = ZoneInfo(timezone_name)

    @property
    def configured(self) -> bool:
        return True

    async def get_quotes(self, symbols: list[str]) -> dict[str, Quote]:
        now = datetime.now(self.timezone)
        result: dict[str, Quote] = {}
        wave = math.sin(time.time() / 18) * 0.0015
        for symbol in symbols:
            item = BASE.get(symbol)
            if not item:
                result[symbol] = Quote(symbol=symbol, source="unavailable", granularity="unknown", received_at=now, availability="unavailable", is_demo=True, quality_flags=["unknown_demo_symbol"])
                continue
            name, base, pre_close = item
            price = round(base * (1 + wave), 2)
            change = round(price - pre_close, 2)
            result[symbol] = Quote(
                symbol=symbol, instrument_type="index" if symbol in {"SH.000001", "SZ.399001", "SZ.399006", "SH.000688"} else "stock", name=name, price=price, pre_close=pre_close, change=change,
                change_pct=round(change / pre_close * 100, 2), open=round(pre_close * 0.997, 2),
                high=round(max(price, base) * 1.009, 2), low=round(min(price, base) * 0.988, 2),
                volume=42_180_000, amount=246_000_000, source="mock", granularity="demo",
                trade_time=now, received_at=now, trading_date=now.date().isoformat(), market_status="unknown",
                is_demo=True, quality_flags=["synthetic_demo_quote"],
            )
        return result
