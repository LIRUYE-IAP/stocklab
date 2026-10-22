from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.db.models import Base, Stock, StockDaily, StockDailyBasic
from app.providers.base import HistoryMarketProvider
from app.services.history_sync import HistorySyncService
from app.services.stock_data import stock_daily, stock_detail


class FixtureHistoryProvider(HistoryMarketProvider):
    name = "fixture"
    configured = True

    async def get_stock_basic(self, list_statuses=("L", "P", "D")):
        return [{"symbol": "SZ.000630", "code": "000630", "name": "铜陵有色", "exchange": "SZ", "board": "MAIN", "industry": "有色金属", "area": "安徽", "list_date": date(1996, 11, 20), "list_status": "L", "delist_date": None, "source": "fixture"}]

    async def get_trade_calendar(self, start_date, end_date):
        return [{"exchange": "SZ", "trade_date": date(2026, 9, 7), "is_open": True, "previous_trade_date": date(2026, 9, 4), "source": "fixture"}]

    def rows(self):
        start = date(2026, 7, 1)
        return [(start + timedelta(days=index), 5 + index * .01) for index in range(70)]

    async def get_daily(self, symbol, start_date, end_date):
        return [{"trade_date": day, "open": price, "high": price + .1, "low": price - .1, "close": price + .03, "pre_close": price - .01, "change_amount": .04, "pct_change": .8, "volume_shares": 1_000_000, "amount_cny": 5_000_000, "source": "fixture"} for day, price in self.rows()]

    async def get_daily_basic(self, symbol, start_date, end_date):
        return [{"trade_date": day, "turnover_rate": 2.1, "turnover_rate_free": 3.0, "volume_ratio": 1.2, "pe": 18, "pe_ttm": 19, "pb": 1.7, "ps": 1, "ps_ttm": 1, "total_share_shares": 1_000_000_000, "float_share_shares": 900_000_000, "free_share_shares": 800_000_000, "total_market_cap_cny": 6_000_000_000, "float_market_cap_cny": 5_000_000_000, "source": "fixture"} for day, _ in self.rows()]

    async def get_adj_factor(self, symbol, start_date, end_date):
        return [{"trade_date": day, "adj_factor": 1 + index * .001, "source": "fixture"} for index, (day, _) in enumerate(self.rows())]

    async def get_price_limits(self, symbol, start_date, end_date):
        return [{"trade_date": day, "up_limit": price * 1.1, "down_limit": price * .9, "source": "fixture"} for day, price in self.rows()]

    async def get_st_status(self, symbol, start_date, end_date): return []


@pytest.mark.asyncio
async def test_copper_history_pipeline_is_idempotent_and_queryable():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        sync = HistorySyncService(FixtureHistoryProvider(), session)
        await sync.sync_stock_basic(); await sync.sync_trade_calendar("20260901", "20260908")
        await sync.sync_symbol_range("SZ.000630", "20260701", "20260908")
        await sync.sync_symbol_range("SZ.000630", "20260701", "20260908")
        session.commit()
        assert session.scalar(select(func.count()).select_from(Stock)) == 1
        assert session.scalar(select(func.count()).select_from(StockDaily)) == 70
        assert session.scalar(select(func.count()).select_from(StockDailyBasic)) == 70
        detail = stock_detail(session, "SZ.000630")
        history = stock_daily(session, "SZ.000630", None, None, "qfq")
        assert detail and detail["name"] == "铜陵有色"
        assert detail["technical"]["ma60"] is not None
        assert len(history["bars"]) == 70
        assert history["bars"][-1]["volume_shares"] == 1_000_000
