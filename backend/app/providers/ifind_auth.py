import asyncio
from datetime import datetime, timedelta, timezone

import httpx

from app.providers.base import ProviderError


class IFindTokenManager:
    def __init__(self, client: httpx.AsyncClient, base_url: str, refresh_token: str, access_token: str = "") -> None:
        self.client = client
        self.base_url = base_url.rstrip("/")
        self.refresh_token = refresh_token
        self._access_token: str | None = access_token or None
        self._refresh_after: datetime | None = datetime.now(timezone.utc) + timedelta(hours=12) if access_token else None
        self._lock = asyncio.Lock()

    @property
    def configured(self) -> bool:
        return bool(self.refresh_token or self._access_token)

    def invalidate(self) -> None:
        self._access_token = None
        self._refresh_after = None

    async def get(self) -> str:
        now = datetime.now(timezone.utc)
        if self._access_token and self._refresh_after and now < self._refresh_after:
            return self._access_token
        async with self._lock:
            now = datetime.now(timezone.utc)
            if self._access_token and self._refresh_after and now < self._refresh_after:
                return self._access_token
            if not self.refresh_token:
                raise ProviderError("iFinD refresh token is not configured", retryable=False, code="not_configured")
            response = await self.client.post(
                f"{self.base_url}/get_access_token",
                headers={"Content-Type": "application/json", "refresh_token": self.refresh_token},
            )
            response.raise_for_status()
            payload = response.json()
            token = ((payload.get("data") or {}).get("access_token") if isinstance(payload, dict) else None)
            if not token:
                raise ProviderError("iFinD access token response did not contain a token", retryable=False, code="auth_failed")
            self._access_token = str(token)
            # Official docs currently describe a seven-day token; refresh locally sooner.
            self._refresh_after = now + timedelta(days=6, hours=12)
            return self._access_token
