from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

MarketStatus = Literal["PRE_MARKET", "OPEN", "LUNCH_BREAK", "CLOSED", "STALE", "OFFLINE", "UNKNOWN", "open", "closed", "delayed", "unknown"]


class Quote(BaseModel):
    symbol: str
    instrument_type: Literal["stock", "index"] = "stock"
    name: str | None = None
    price: float | None = None
    pre_close: float | None = None
    change: float | None = None
    change_pct: float | None = None
    open: float | None = None
    high: float | None = None
    low: float | None = None
    volume: float | None = None
    amount: float | None = None
    bid_price_1: float | None = None
    ask_price_1: float | None = None
    bid_volume_1: float | None = None
    ask_volume_1: float | None = None
    source: Literal["ifind", "tushare", "mock", "cache", "unavailable"]
    granularity: Literal["snapshot", "minute", "eod", "demo", "unknown"]
    trade_time: datetime | None = None
    received_at: datetime
    trading_date: str | None = None
    market_status: MarketStatus = "unknown"
    is_stale: bool = False
    is_demo: bool = False
    availability: Literal["available", "partial", "unavailable"] = "available"
    fallback_reason: str | None = None
    quality_flags: list[str] = Field(default_factory=list)
    currency: str = "CNY"
    price_unit: str = "yuan"
    volume_unit: str = "share"
    amount_unit: str = "yuan"


class MinuteBar(BaseModel):
    symbol: str
    time: datetime
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: float | None = None
    amount: float | None = None
    source: Literal["ifind", "tushare", "mock"]
    is_demo: bool = False


class ProviderState(BaseModel):
    data_mode: str = "mock"
    history_provider: str = "tushare"
    realtime_provider: str = "ifind"
    configured_mode: str
    active_source: str
    ifind_configured: bool
    tushare_configured: bool
    tushare_realtime_enabled: bool
    cache_backend: str
    allow_demo: bool
    last_success_at: datetime | None = None
    last_error: str | None = None
    capabilities: list[str] = Field(default_factory=list)
    database_configured: bool = False
