from app.core.config import settings

try:
    from redis import asyncio as redis
except ImportError:  # pragma: no cover - optional service dependency.
    redis = None

_client = None


def build_redis_url() -> str | None:
    if settings.REDIS_URL:
        return settings.REDIS_URL
    if not settings.REDIS_HOST:
        return None

    auth = f":{settings.REDIS_PASSWORD}@" if settings.REDIS_PASSWORD else ""
    port = settings.REDIS_PORT or 6379
    return f"redis://{auth}{settings.REDIS_HOST}:{port}/0"


def get_redis_client():
    """Return a persistent Redis client (connection pool). Never close it between calls."""
    global _client
    if redis is None:
        return None
    if _client is None:
        url = build_redis_url()
        if not url:
            return None
        _client = redis.from_url(url, decode_responses=True)
    return _client


# Legacy alias — kept so existing callers don't break.
def get_redis_connection():
    return get_redis_client()


async def test_redis_connection() -> str:
    client = get_redis_client()
    if client is None:
        return "Redis is not configured"

    try:
        await client.set(f"{settings.REDIS_KEY_PREFIX}:health", "ok")
        return "Redis connected successfully"
    except Exception as exc:
        return f"Redis connection failed: {exc}"
