import asyncio
from collections.abc import AsyncIterator

import pytest

from app.utils import redis as redis_utils


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.expirations: dict[str, int] = {}

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        self.values[key] = value
        if ex is not None:
            self.expirations[key] = ex

    async def get(self, key: str) -> str | None:
        return self.values.get(key)

    async def delete(self, *keys: str) -> None:
        for key in keys:
            self.values.pop(key, None)

    async def scan_iter(self, match: str) -> AsyncIterator[str]:
        prefix = match.removesuffix("*")
        for key in self.values:
            if key.startswith(prefix):
                yield key


def test_otp_defaults_to_ten_minute_expiration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_redis = FakeRedis()
    monkeypatch.setattr(redis_utils, "redis_client", fake_redis)

    asyncio.run(redis_utils.set_otp("ada@example.com", "123456"))

    assert fake_redis.values["otp:ada@example.com"] == "123456"
    assert fake_redis.expirations["otp:ada@example.com"] == 600
    assert asyncio.run(redis_utils.get_otp("ada@example.com")) == "123456"


def test_active_model_listing_uses_key_scan(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_redis = FakeRedis()
    fake_redis.values["ai:active_model:local"] = "active"
    monkeypatch.setattr(redis_utils, "redis_client", fake_redis)

    assert asyncio.run(redis_utils.list_active_ai_models()) == ["local"]
