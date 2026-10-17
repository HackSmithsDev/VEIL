import json
from typing import Any

from redis.asyncio import Redis

from app.core.config import settings

redis_client = Redis.from_url(settings.redis_url, decode_responses=True)


async def set_otp(email: str, code: str, expire_seconds: int = 600) -> None:
    await redis_client.set(f"otp:{email}", code, ex=expire_seconds)


async def get_otp(email: str) -> str | None:
    return await redis_client.get(f"otp:{email}")


async def delete_otp(email: str) -> None:
    await redis_client.delete(f"otp:{email}")


async def increment_rate_limit(key: str, expire_seconds: int) -> int:
    count = await redis_client.eval(
        """
        local count = redis.call('INCR', KEYS[1])
        if count == 1 then
            redis.call('EXPIRE', KEYS[1], ARGV[1])
        end
        return count
        """,
        1,
        key,
        expire_seconds,
    )
    return int(count)


async def set_password_reset_token(
    token_digest: str,
    email: str,
    expire_seconds: int,
) -> None:
    await redis_client.set(
        f"password-reset:{token_digest}",
        email,
        ex=expire_seconds,
    )


async def consume_password_reset_token(token_digest: str) -> str | None:
    value = await redis_client.eval(
        """
        local value = redis.call('GET', KEYS[1])
        if value then
            redis.call('DEL', KEYS[1])
        end
        return value
        """,
        1,
        f"password-reset:{token_digest}",
    )
    return value


async def set_refresh_token(user_id: str, token: str, expire_seconds: int) -> None:
    await redis_client.set(f"refresh:{user_id}", token, ex=expire_seconds)


async def get_refresh_token(user_id: str) -> str | None:
    return await redis_client.get(f"refresh:{user_id}")


async def delete_refresh_token(user_id: str) -> None:
    await redis_client.delete(f"refresh:{user_id}")


async def set_connection_token(
    connection_id: str,
    data: dict[str, Any],
    expire_seconds: int = 3600,
) -> None:
    await redis_client.set(
        f"connection:{connection_id}",
        json.dumps(data),
        ex=expire_seconds,
    )


async def get_connection_token(connection_id: str) -> dict[str, Any] | None:
    raw = await redis_client.get(f"connection:{connection_id}")
    return json.loads(raw) if raw else None


async def delete_connection_token(connection_id: str) -> None:
    await redis_client.delete(f"connection:{connection_id}")


async def set_active_controller(user_id: str, expire_seconds: int = 3600) -> None:
    await redis_client.set("active_controller", user_id, ex=expire_seconds)


async def get_active_controller() -> str | None:
    return await redis_client.get("active_controller")


async def clear_active_controller() -> None:
    await redis_client.delete("active_controller")


async def set_active_ai_model(
    model_key: str,
    metadata: dict[str, Any] | None = None,
    expire_seconds: int | None = None,
) -> None:
    value = json.dumps(metadata) if metadata is not None else "active"
    if expire_seconds is not None:
        await redis_client.set(f"ai:active_model:{model_key}", value, ex=expire_seconds)
    else:
        await redis_client.set(f"ai:active_model:{model_key}", value)


async def get_active_ai_model(model_key: str) -> Any | None:
    raw = await redis_client.get(f"ai:active_model:{model_key}")
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return raw


async def revoke_active_ai_model(model_key: str) -> None:
    await redis_client.delete(f"ai:active_model:{model_key}")


async def list_active_ai_models() -> list[str]:
    keys = [
        key async for key in redis_client.scan_iter(match="ai:active_model:*")
    ]
    return [key.removeprefix("ai:active_model:") for key in keys]


async def revoke_all_ai_models() -> None:
    keys = [
        key async for key in redis_client.scan_iter(match="ai:active_model:*")
    ]
    if keys:
        await redis_client.delete(*keys)
