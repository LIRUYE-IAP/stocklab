from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    data_mode: Literal["mock", "live", "hybrid"] = "mock"
    history_provider: Literal["tushare", "mock"] = "tushare"
    realtime_provider: Literal["ifind", "mock"] = "ifind"
    market_mode: Literal["auto", "ifind", "mock"] = "auto"
    allow_demo: bool = True
    database_url: str = f"sqlite:///{(Path(__file__).resolve().parents[2] / 'stocklab.db').as_posix()}"
    database_auto_create: bool = True
    ifind_base_url: str = "https://quantapi.51ifind.com/api/v1"
    ifind_refresh_token: str = ""
    ifind_access_token: str = ""
    ifind_quote_indicators: str = "open,high,low,latest"
    tushare_token: str = ""
    tushare_realtime_enabled: bool = False
    quote_cache_backend: Literal["memory", "redis"] = "memory"
    redis_url: str = "redis://127.0.0.1:6379/0"
    quote_detail_interval_seconds: float = 3
    quote_list_interval_seconds: float = 5
    quote_stale_after_seconds: int = 30
    quote_cache_ttl_seconds: int = 120
    ifind_max_qps: float = 2
    quote_timezone: str = "Asia/Shanghai"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_prefix="STOCKLAB_",
        extra="ignore",
    )

    # Provider variables intentionally keep their established external names.
    def model_post_init(self, __context: object) -> None:
        import os

        self.data_mode = os.getenv("DATA_MODE", self.data_mode)  # type: ignore[assignment]
        self.history_provider = os.getenv("HISTORY_PROVIDER", self.history_provider)  # type: ignore[assignment]
        self.realtime_provider = os.getenv("REALTIME_PROVIDER", self.realtime_provider)  # type: ignore[assignment]
        self.database_url = os.getenv("DATABASE_URL", self.database_url)
        self.database_auto_create = os.getenv("DATABASE_AUTO_CREATE", str(self.database_auto_create)).lower() == "true"
        self.ifind_refresh_token = os.getenv("IFIND_REFRESH_TOKEN", self.ifind_refresh_token)
        self.ifind_access_token = os.getenv("IFIND_ACCESS_TOKEN", self.ifind_access_token)
        self.ifind_base_url = os.getenv("IFIND_BASE_URL", self.ifind_base_url)
        self.ifind_quote_indicators = os.getenv("IFIND_QUOTE_INDICATORS", self.ifind_quote_indicators)
        self.tushare_token = os.getenv("TUSHARE_TOKEN", self.tushare_token)
        self.tushare_realtime_enabled = os.getenv("TUSHARE_REALTIME_ENABLED", str(self.tushare_realtime_enabled)).lower() == "true"
        self.redis_url = os.getenv("REDIS_URL", self.redis_url)
        self.quote_cache_backend = os.getenv("QUOTE_CACHE_BACKEND", self.quote_cache_backend)  # type: ignore[assignment]
        self.quote_detail_interval_seconds = float(os.getenv("QUOTE_DETAIL_INTERVAL_SECONDS", self.quote_detail_interval_seconds))
        self.quote_list_interval_seconds = float(os.getenv("QUOTE_LIST_INTERVAL_SECONDS", self.quote_list_interval_seconds))
        self.quote_stale_after_seconds = int(os.getenv("QUOTE_STALE_AFTER_SECONDS", self.quote_stale_after_seconds))
        self.quote_cache_ttl_seconds = int(os.getenv("QUOTE_CACHE_TTL_SECONDS", self.quote_cache_ttl_seconds))
        self.ifind_max_qps = float(os.getenv("IFIND_MAX_QPS", self.ifind_max_qps))
        self.quote_timezone = os.getenv("QUOTE_TIMEZONE", self.quote_timezone)


@lru_cache
def get_settings() -> Settings:
    return Settings()
