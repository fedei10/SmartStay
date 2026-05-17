import json
from collections import defaultdict, deque
from typing import Any

from app.core.config import settings
from app.services.redis.connection import get_redis_connection


class ConversationMemory:
    """Small Redis-backed conversation memory with an in-process fallback."""

    def __init__(self):
        self._fallback: dict[str, deque[dict[str, Any]]] = defaultdict(
            lambda: deque(maxlen=settings.ORCHESTRATOR_MEMORY_TURNS)
        )

    def _key(self, conversation_id: str) -> str:
        return f"{settings.REDIS_KEY_PREFIX}:conversation:{conversation_id}:messages"

    async def get_recent(self, conversation_id: str) -> list[dict[str, Any]]:
        limit = max(settings.ORCHESTRATOR_MEMORY_TURNS, 1)
        client = get_redis_connection()
        if client is None:
            return list(self._fallback[conversation_id])[-limit:]

        try:
            values = await client.lrange(self._key(conversation_id), -limit, -1)
            await client.aclose()
            return [json.loads(value) for value in values]
        except Exception:
            return list(self._fallback[conversation_id])[-limit:]

    async def append_interaction(
        self,
        conversation_id: str,
        *,
        user_message: str,
        assistant_message: str | None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        entry = {
            "user": user_message,
            "assistant": assistant_message,
            "metadata": metadata or {},
        }
        self._fallback[conversation_id].append(entry)

        client = get_redis_connection()
        if client is None:
            return

        try:
            key = self._key(conversation_id)
            await client.rpush(key, json.dumps(entry, default=str))
            await client.ltrim(key, -settings.ORCHESTRATOR_MEMORY_TURNS, -1)
            await client.aclose()
        except Exception:
            return
