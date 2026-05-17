from app.core.config import settings

try:
    from redis import asyncio as redis
except ImportError:  # pragma: no cover - optional service dependency.
    redis = None


def build_redis_url() -> str | None:
    if settings.REDIS_URL:
        return settings.REDIS_URL
    if not settings.REDIS_HOST:
        return None

    auth = f":{settings.REDIS_PASSWORD}@" if settings.REDIS_PASSWORD else ""
    port = settings.REDIS_PORT or 6379
    return f"redis://{auth}{settings.REDIS_HOST}:{port}/0"


def get_redis_connection():
    if redis is None:
        return None

    redis_url = build_redis_url()
    if not redis_url:
        return None

    return redis.from_url(redis_url, decode_responses=True)


async def test_redis_connection() -> str:
    client = get_redis_connection()
    if client is None:
        return "Redis is not configured"

    try:
        await client.set(f"{settings.REDIS_KEY_PREFIX}:health", "ok")
        await client.aclose()
        return "Redis connected successfully"
    except Exception as exc:
        return f"Redis connection failed: {exc}"
