from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Stock(Base):
    __tablename__ = "stocks"
    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    code: Mapped[str] = mapped_column(String(8), index=True)
    name: Mapped[str] = mapped_column(String(80), index=True)
    exchange: Mapped[str] = mapped_column(String(8), index=True)
    board: Mapped[str] = mapped_column(String(16), default="UNKNOWN")
    industry: Mapped[str | None] = mapped_column(String(100))
    area: Mapped[str | None] = mapped_column(String(60))
    list_date: Mapped[date | None] = mapped_column(Date)
    list_status: Mapped[str] = mapped_column(String(4), index=True)
    delist_date: Mapped[date | None] = mapped_column(Date)
    source: Mapped[str] = mapped_column(String(20), default="tushare")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    daily: Mapped[list["StockDaily"]] = relationship(back_populates="stock")


class TradingCalendar(Base):
    __tablename__ = "trading_calendar"
    id: Mapped[int] = mapped_column(primary_key=True)
    exchange: Mapped[str] = mapped_column(String(8))
    trade_date: Mapped[date] = mapped_column(Date)
    is_open: Mapped[bool] = mapped_column(Boolean)
    previous_trade_date: Mapped[date | None] = mapped_column(Date)
    source: Mapped[str] = mapped_column(String(20), default="tushare")
    __table_args__ = (UniqueConstraint("exchange", "trade_date", name="uq_calendar_exchange_date"),)


class StockDaily(Base):
    __tablename__ = "stock_daily"
    id: Mapped[int] = mapped_column(primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), index=True)
    trade_date: Mapped[date] = mapped_column(Date, index=True)
    open: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    high: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    low: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    close: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    pre_close: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    change_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    pct_change: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    volume_shares: Mapped[Decimal | None] = mapped_column(Numeric(24, 2))
    amount_cny: Mapped[Decimal | None] = mapped_column(Numeric(24, 2))
    source: Mapped[str] = mapped_column(String(20), default="tushare")
    stock: Mapped[Stock] = relationship(back_populates="daily")
    __table_args__ = (UniqueConstraint("stock_id", "trade_date", name="uq_stock_daily_date"), Index("ix_stock_daily_date_stock", "trade_date", "stock_id"))


class StockDailyBasic(Base):
    __tablename__ = "stock_daily_basic"
    id: Mapped[int] = mapped_column(primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), index=True)
    trade_date: Mapped[date] = mapped_column(Date, index=True)
    turnover_rate: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    turnover_rate_free: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    volume_ratio: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    pe: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    pe_ttm: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    pb: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    ps: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    ps_ttm: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    total_share_shares: Mapped[Decimal | None] = mapped_column(Numeric(24, 2))
    float_share_shares: Mapped[Decimal | None] = mapped_column(Numeric(24, 2))
    free_share_shares: Mapped[Decimal | None] = mapped_column(Numeric(24, 2))
    total_market_cap_cny: Mapped[Decimal | None] = mapped_column(Numeric(24, 2))
    float_market_cap_cny: Mapped[Decimal | None] = mapped_column(Numeric(24, 2))
    source: Mapped[str] = mapped_column(String(20), default="tushare")
    __table_args__ = (UniqueConstraint("stock_id", "trade_date", name="uq_stock_daily_basic_date"),)


class StockAdjFactor(Base):
    __tablename__ = "stock_adj_factor"
    id: Mapped[int] = mapped_column(primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), index=True)
    trade_date: Mapped[date] = mapped_column(Date, index=True)
    adj_factor: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    source: Mapped[str] = mapped_column(String(20), default="tushare")
    __table_args__ = (UniqueConstraint("stock_id", "trade_date", name="uq_stock_adj_date"),)


class StockPriceLimit(Base):
    __tablename__ = "stock_price_limits"
    id: Mapped[int] = mapped_column(primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), index=True)
    trade_date: Mapped[date] = mapped_column(Date, index=True)
    up_limit: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    down_limit: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    source: Mapped[str] = mapped_column(String(20), default="tushare")
    __table_args__ = (UniqueConstraint("stock_id", "trade_date", name="uq_stock_limit_date"),)


class StockSTStatus(Base):
    __tablename__ = "stock_st_status"
    id: Mapped[int] = mapped_column(primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), index=True)
    trade_date: Mapped[date] = mapped_column(Date, index=True)
    is_st: Mapped[bool] = mapped_column(Boolean)
    stock_name: Mapped[str | None] = mapped_column(String(80))
    source: Mapped[str] = mapped_column(String(20), default="tushare")
    __table_args__ = (UniqueConstraint("stock_id", "trade_date", name="uq_stock_st_date"),)


class DataJob(Base):
    __tablename__ = "data_jobs"
    id: Mapped[int] = mapped_column(primary_key=True)
    job_type: Mapped[str] = mapped_column(String(60), index=True)
    trade_date: Mapped[date | None] = mapped_column(Date, index=True)
    source: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(16), index=True)
    expected_records: Mapped[int | None] = mapped_column(Integer)
    received_records: Mapped[int] = mapped_column(Integer, default=0)
    inserted_records: Mapped[int] = mapped_column(Integer, default=0)
    updated_records: Mapped[int] = mapped_column(Integer, default=0)
    missing_records: Mapped[int] = mapped_column(Integer, default=0)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)


class MarketDataStatus(Base):
    __tablename__ = "market_data_status"
    id: Mapped[int] = mapped_column(primary_key=True)
    dataset: Mapped[str] = mapped_column(String(60), unique=True)
    latest_trade_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(16))
    record_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    detail: Mapped[str | None] = mapped_column(Text)


class DataQualityError(Base):
    __tablename__ = "data_quality_errors"
    id: Mapped[int] = mapped_column(primary_key=True)
    dataset: Mapped[str] = mapped_column(String(60), index=True)
    symbol: Mapped[str | None] = mapped_column(String(16), index=True)
    trade_date: Mapped[date | None] = mapped_column(Date, index=True)
    rule: Mapped[str] = mapped_column(String(120))
    payload: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TechnicalDaily(Base):
    __tablename__ = "technical_daily"
    id: Mapped[int] = mapped_column(primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), index=True)
    trade_date: Mapped[date] = mapped_column(Date, index=True)
    ma5: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    ma10: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    ma20: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    ma60: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    ma120: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    ma250: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    macd_dif: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    macd_dea: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    macd_hist: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    rsi14: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    technical_score: Mapped[int | None] = mapped_column(Integer)
    algorithm_version: Mapped[str] = mapped_column(String(30), default="technical-v1")
    source_trade_date: Mapped[date] = mapped_column(Date)
    __table_args__ = (UniqueConstraint("stock_id", "trade_date", name="uq_technical_daily_date"),)


class StockPositionDaily(Base):
    __tablename__ = "stock_position_daily"
    id: Mapped[int] = mapped_column(primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), index=True)
    trade_date: Mapped[date] = mapped_column(Date, index=True)
    price_percentile_6m: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    price_percentile_1y: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    price_percentile_3y: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    distance_60d_high: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    distance_52w_high: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    distance_52w_low: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    algorithm_version: Mapped[str] = mapped_column(String(30), default="position-v1")
    __table_args__ = (UniqueConstraint("stock_id", "trade_date", name="uq_position_daily_date"),)
