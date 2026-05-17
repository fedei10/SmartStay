import time
import uuid
from collections.abc import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import settings
from app.core.logging import bind_context, clear_context, logger
from app.core.metrics import http_request_duration_seconds, http_requests_total


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get(settings.REQUEST_ID_HEADER) or str(uuid.uuid4())
        clerk_user_id = request.headers.get("X-Clerk-User-Id")
        bind_context(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            clerk_user_id=clerk_user_id,
        )
        request.state.request_id = request_id
        request.state.clerk_user_id = clerk_user_id

        start = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration = time.perf_counter() - start
            if settings.ENABLE_METRICS:
                if http_requests_total is not None:
                    http_requests_total.labels(
                        method=request.method,
                        path=request.url.path,
                        status_code=str(status_code),
                    ).inc()
                if http_request_duration_seconds is not None:
                    http_request_duration_seconds.labels(
                        method=request.method,
                        path=request.url.path,
                    ).observe(duration)

            logger.info(
                "request_completed status_code=%s duration_ms=%.2f",
                status_code,
                duration * 1000,
            )
            clear_context()
