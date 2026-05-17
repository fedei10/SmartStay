import json
from collections import defaultdict, deque
from typing import Any

from app.core.config import settings
from app.services.redis.connection import get_redis_connection

# TTL for booking state in Redis (24 hours)
_BOOKING_STATE_TTL = 86_400


class ConversationMemory:
    """Redis-backed conversation memory with an in-process fallback."""

    def __init__(self):
        self._fallback: dict[str, deque[dict[str, Any]]] = defaultdict(
            lambda: deque(maxlen=settings.ORCHESTRATOR_MEMORY_TURNS)
        )
        self._booking_states: dict[str, dict[str, Any]] = {}

    # ── Conversation turns ────────────────────────────────────────────────────

    def _turns_key(self, conversation_id: str) -> str:
        return f"{settings.REDIS_KEY_PREFIX}:conversation:{conversation_id}:messages"

    async def get_recent(self, conversation_id: str) -> list[dict[str, Any]]:
        limit = max(settings.ORCHESTRATOR_MEMORY_TURNS, 1)
        client = get_redis_connection()
        if client is None:
            return list(self._fallback[conversation_id])[-limit:]

        try:
            values = await client.lrange(self._turns_key(conversation_id), -limit, -1)
            await client.aclose()
            return [json.loads(v) for v in values]
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
            key = self._turns_key(conversation_id)
            await client.rpush(key, json.dumps(entry, default=str))
            await client.ltrim(key, -settings.ORCHESTRATOR_MEMORY_TURNS, -1)
            await client.aclose()
        except Exception:
            return

    # ── Booking state ─────────────────────────────────────────────────────────

    def _booking_state_key(self, conversation_id: str) -> str:
        return f"{settings.REDIS_KEY_PREFIX}:booking_state:{conversation_id}"

    async def get_booking_state(self, conversation_id: str) -> dict[str, Any]:
        client = get_redis_connection()
        if client is None:
            return dict(self._booking_states.get(conversation_id, {}))

        try:
            value = await client.get(self._booking_state_key(conversation_id))
            await client.aclose()
            if value:
                return json.loads(value)
            return dict(self._booking_states.get(conversation_id, {}))
        except Exception:
            return dict(self._booking_states.get(conversation_id, {}))

    async def set_booking_state(
        self, conversation_id: str, state: dict[str, Any]
    ) -> None:
        self._booking_states[conversation_id] = state

        client = get_redis_connection()
        if client is None:
            return

        try:
            key = self._booking_state_key(conversation_id)
            await client.set(key, json.dumps(state, default=str), ex=_BOOKING_STATE_TTL)
            await client.aclose()
        except Exception:
            return
