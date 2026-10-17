import asyncio
from collections.abc import AsyncIterator

import pytest

from app.utils import redis as redis_utils


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.expirations: dict[str, int] = {}
        self.counters: dict[str, int] = {}

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        self.values[key] = value
        if ex is not None:
            self.expirations[key] = ex

    async def get(self, key: str) -> str | None:
        return self.values.get(key)

    async def delete(self, *keys: str) -> None:
        for key in keys:
            self.values.pop(key, None)

    async def eval(
        self,
        script: str,
        _number_of_keys: int,
        key: str,
        *arguments: int,
    ) -> int | str | None:
        if "INCR" in script:
            self.counters[key] = self.counters.get(key, 0) + 1
            if self.counters[key] == 1:
                self.expirations[key] = arguments[0]
            return self.counters[key]

        return self.values.pop(key, None)

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


def test_password_reset_token_is_stored_and_consumed_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_redis = FakeRedis()
    monkeypatch.setattr(redis_utils, "redis_client", fake_redis)

    asyncio.run(
        redis_utils.set_password_reset_token("digest", "ada@example.com", 1800)
    )

    assert fake_redis.values["password-reset:digest"] == "ada@example.com"
    assert fake_redis.expirations["password-reset:digest"] == 1800
    assert (
        asyncio.run(redis_utils.consume_password_reset_token("digest"))
        == "ada@example.com"
    )
    assert asyncio.run(redis_utils.consume_password_reset_token("digest")) is None


def test_rate_limit_counter_sets_expiration_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_redis = FakeRedis()
    monkeypatch.setattr(redis_utils, "redis_client", fake_redis)

    assert asyncio.run(redis_utils.increment_rate_limit("requests", 3600)) == 1
    assert asyncio.run(redis_utils.increment_rate_limit("requests", 3600)) == 2
    assert fake_redis.expirations["requests"] == 3600
