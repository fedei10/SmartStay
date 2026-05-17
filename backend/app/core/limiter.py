from app.core.config import settings
from app.services.redis.connection import build_redis_url

try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
except ImportError:  # pragma: no cover - optional dependency.
    Limiter = None
    get_remote_address = None


def build_limiter():
    if Limiter is None or get_remote_address is None or not settings.RATE_LIMIT_ENABLED:
        return None

    return Limiter(
        key_func=get_remote_address,
        default_limits=[settings.RATE_LIMIT_DEFAULT],
        storage_uri=build_redis_url(),
    )


limiter = build_limiter()
