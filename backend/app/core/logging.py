import contextvars
import json
import logging
import sys
from typing import Any

from app.core.config import settings


_log_context: contextvars.ContextVar[dict[str, Any]] = contextvars.ContextVar(
    "smartstay_log_context",
    default={},
)


class ContextJsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        payload.update(_log_context.get())
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


class ContextTextFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        context = _log_context.get()
        suffix = " ".join(f"{key}={value}" for key, value in context.items())
        base = super().format(record)
        return f"{base} {suffix}".strip()


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    if settings.JSON_LOGS:
        handler.setFormatter(ContextJsonFormatter())
    else:
        handler.setFormatter(
            ContextTextFormatter("%(levelname)s %(name)s %(message)s")
        )

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(settings.LOG_LEVEL.upper())


def bind_context(**values: Any) -> None:
    context = {**_log_context.get(), **{k: v for k, v in values.items() if v is not None}}
    _log_context.set(context)


def clear_context() -> None:
    _log_context.set({})


logger = logging.getLogger("smartstay")
