import json
from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import DataJob, DataQualityError, MarketDataStatus, Stock, StockAdjFactor, StockDaily, StockDailyBasic, StockPositionDaily, StockPriceLimit, StockSTStatus, TechnicalDaily, TradingCalendar
from app.providers.base import HistoryMarketProvider, ProviderError
from app.providers.symbols import normalize_internal
from app.services.data_quality import validate_daily_row
from app.services.technical import calculate_position, calculate_technical


MODEL_BY_DATASET = {
    "daily": StockDaily,
    "daily_basic": StockDailyBasic,
    "adj_factor": StockAdjFactor,
    "price_limits": StockPriceLimit,
    "st_status": StockSTStatus,
}


def _upsert(session: Session, model, keys: dict[str, Any], values: dict[str, Any]) -> bool:
    row = session.scalar(select(model).filter_by(**keys))
    if row is None:
        session.add(model(**keys, **values))
        return True
    for key, value in values.items():
        setattr(row, key, value)
    return False


class HistorySyncService:
    def __init__(self, provider: HistoryMarketProvider, session: Session) -> None:
        self.provider = provider
        self.session = session

    def _job(self, job_type: str, trade_date: date | None = None) -> DataJob:
        job = DataJob(job_type=job_type, trade_date=trade_date, source=self.provider.name, status="RUNNING", received_records=0, inserted_records=0, updated_records=0, missing_records=0, retry_count=0)
        self.session.add(job); self.session.flush()
        return job

    def _finish(self, job: DataJob, status: str, error: str | None = None) -> None:
        job.status = status; job.error_message = error; job.finished_at = datetime.now(timezone.utc)
        self.session.flush()

    def _status(self, dataset: str, latest: date | None, status: str, count: int, detail: str | None = None) -> None:
        _upsert(self.session, MarketDataStatus, {"dataset": dataset}, {"latest_trade_date": latest, "status": status, "record_count": count, "detail": detail})

    async def sync_stock_basic(self) -> DataJob:
        job = self._job("stock_basic")
        try:
            rows = await self.provider.get_stock_basic()
            job.received_records = len(rows)
            for row in rows:
                values = dict(row); symbol = values.pop("symbol")
                inserted = _upsert(self.session, Stock, {"symbol": symbol}, values)
                job.inserted_records += int(inserted); job.updated_records += int(not inserted)
            self._status("stock_basic", None, "SUCCESS" if rows else "PARTIAL", len(rows), None if rows else "provider returned no rows")
            self._finish(job, "SUCCESS" if rows else "PARTIAL")
        except Exception as exc:
            self._finish(job, "FAILED", str(exc)); raise
        return job

    async def sync_trade_calendar(self, start_date: str, end_date: str) -> DataJob:
        job = self._job("trade_calendar")
        try:
            rows = await self.provider.get_trade_calendar(start_date, end_date)
            job.received_records = len(rows)
            for row in rows:
                values = dict(row); keys = {"exchange": values.pop("exchange"), "trade_date": values.pop("trade_date")}
                inserted = _upsert(self.session, TradingCalendar, keys, values)
                job.inserted_records += int(inserted); job.updated_records += int(not inserted)
            latest = max((row["trade_date"] for row in rows if row.get("is_open")), default=None)
            self._status("trading_calendar", latest, "SUCCESS" if rows else "PARTIAL", len(rows))
            self._finish(job, "SUCCESS" if rows else "PARTIAL")
        except Exception as exc:
            self._finish(job, "FAILED", str(exc)); raise
        return job

    async def sync_symbol_range(self, symbol: str, start_date: str, end_date: str) -> list[DataJob]:
        symbol = normalize_internal(symbol)
        stock = self.session.scalar(select(Stock).where(Stock.symbol == symbol))
        if stock is None:
            raise ProviderError(f"Stock {symbol} is not in stocks; run sync_stock_basic first", retryable=False, code="stock_missing")
        payloads = [
            ("daily", await self.provider.get_daily(symbol, start_date, end_date)),
            ("daily_basic", await self.provider.get_daily_basic(symbol, start_date, end_date)),
            ("adj_factor", await self.provider.get_adj_factor(symbol, start_date, end_date)),
            ("price_limits", await self.provider.get_price_limits(symbol, start_date, end_date)),
        ]
        jobs: list[DataJob] = []
        valid_dates: list[date] = []
        for dataset, rows in payloads:
            job = self._job(dataset); jobs.append(job); job.received_records = len(rows)
            model = MODEL_BY_DATASET[dataset]
            for row in rows:
                if dataset == "daily":
                    errors = validate_daily_row(row)
                    if errors:
                        self.session.add(DataQualityError(dataset="daily", symbol=symbol, trade_date=row.get("trade_date"), rule=",".join(errors), payload=json.dumps(row, ensure_ascii=False, default=str)))
                        job.missing_records += 1
                        continue
                    valid_dates.append(row["trade_date"])
                values = dict(row); trade_date = values.pop("trade_date")
                inserted = _upsert(self.session, model, {"stock_id": stock.id, "trade_date": trade_date}, values)
                job.inserted_records += int(inserted); job.updated_records += int(not inserted)
            status = "SUCCESS" if rows and job.missing_records == 0 else "PARTIAL"
            latest = max((row["trade_date"] for row in rows if row.get("trade_date")), default=None)
            self._status(dataset, latest, status, len(rows), f"{symbol}; rejected={job.missing_records}")
            self._finish(job, status)
        st_rows = await self.provider.get_st_status(symbol, start_date, end_date)
        st_job = self._job("st_status"); jobs.append(st_job); st_job.received_records = len(st_rows)
        for trade_date in valid_dates:
            match = next((row for row in st_rows if (row.get("start_date") is None or row["start_date"] <= trade_date) and (row.get("end_date") is None or trade_date <= row["end_date"])), None)
            values = {"is_st": bool(match and match.get("is_st")), "stock_name": match.get("stock_name") if match else stock.name, "source": self.provider.name}
            inserted = _upsert(self.session, StockSTStatus, {"stock_id": stock.id, "trade_date": trade_date}, values)
            st_job.inserted_records += int(inserted); st_job.updated_records += int(not inserted)
        self._status("st_status", max(valid_dates, default=None), "SUCCESS" if valid_dates else "PARTIAL", len(valid_dates), f"{symbol}; interval records={len(st_rows)}")
        self._finish(st_job, "SUCCESS" if valid_dates else "PARTIAL")
        self.session.flush()
        self.compute_derived(stock)
        return jobs

    def compute_derived(self, stock: Stock) -> None:
        rows = list(self.session.scalars(select(StockDaily).where(StockDaily.stock_id == stock.id).order_by(StockDaily.trade_date)))
        if not rows:
            return
        factors = {row.trade_date: float(row.adj_factor) for row in self.session.scalars(select(StockAdjFactor).where(StockAdjFactor.stock_id == stock.id))}
        latest_factor = factors.get(rows[-1].trade_date) or (list(factors.values())[-1] if factors else 1.0)
        closes = [float(row.close) * factors.get(row.trade_date, latest_factor) / latest_factor for row in rows if row.close is not None]
        if not closes:
            return
        technical = calculate_technical(closes); position = calculate_position(closes); latest_date = rows[-1].trade_date
        _upsert(self.session, TechnicalDaily, {"stock_id": stock.id, "trade_date": latest_date}, {**technical, "source_trade_date": latest_date})
        _upsert(self.session, StockPositionDaily, {"stock_id": stock.id, "trade_date": latest_date}, position)
        self._status("technical_daily", latest_date, "SUCCESS", int(self.session.scalar(select(func.count()).select_from(TechnicalDaily)) or 0))
        self._status("stock_position_daily", latest_date, "SUCCESS", int(self.session.scalar(select(func.count()).select_from(StockPositionDaily)) or 0))
