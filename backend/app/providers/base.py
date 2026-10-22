from abc import ABC, abstractmethod

from app.schemas import MinuteBar, Quote


class ProviderError(RuntimeError):
    def __init__(self, message: str, *, retryable: bool = True, code: str = "provider_error") -> None:
        super().__init__(message)
        self.retryable = retryable
        self.code = code


class ProviderUnavailable(ProviderError):
    def __init__(self, message: str, *, code: str = "provider_unavailable") -> None:
        super().__init__(message, retryable=True, code=code)


class HistoryMarketProvider(ABC):
    name: str

    @property
    @abstractmethod
    def configured(self) -> bool: ...

    @abstractmethod
    async def get_stock_basic(self, list_statuses: tuple[str, ...] = ("L", "P", "D")) -> list[dict]: ...

    @abstractmethod
    async def get_trade_calendar(self, start_date: str, end_date: str) -> list[dict]: ...

    @abstractmethod
    async def get_daily(self, symbol: str, start_date: str, end_date: str) -> list[dict]: ...

    @abstractmethod
    async def get_daily_basic(self, symbol: str, start_date: str, end_date: str) -> list[dict]: ...

    @abstractmethod
    async def get_adj_factor(self, symbol: str, start_date: str, end_date: str) -> list[dict]: ...

    @abstractmethod
    async def get_price_limits(self, symbol: str, start_date: str, end_date: str) -> list[dict]: ...

    @abstractmethod
    async def get_st_status(self, symbol: str, start_date: str, end_date: str) -> list[dict]: ...


class RealtimeMarketProvider(ABC):
    name: str

    @property
    @abstractmethod
    def configured(self) -> bool: ...

    @abstractmethod
    async def get_quotes(self, symbols: list[str]) -> dict[str, Quote]: ...

    async def get_minutes(self, symbol: str, date: str | None = None) -> list[MinuteBar]:
        return []
