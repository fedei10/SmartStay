from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response

from app.agents.booking.dependencies import build_booking_deps
from app.agents.booking.graph import build_booking_graph
from app.api.V1.bookings import router as bookings_router
from app.api.V1.chat import router as chat_router
from app.api.V1.flights import router as flights_router
from app.api.V1.health import router as health_router
from app.api.V1.hotels import router as hotels_router
from app.api.V1.users import router as users_router
from app.config import settings
from app.core.limiter import limiter
from app.core.logging import configure_logging
from app.core.metrics import metrics_response
from app.core.middleware import RequestContextMiddleware
from app.db.database import engine
from app.db.models import Base
from app.models import Booking, BookingSession, User, UserProfile

try:
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
    from psycopg_pool import AsyncConnectionPool
    _has_pg_saver = True
except ImportError:
    _has_pg_saver = False

try:
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware
    from slowapi import _rate_limit_exceeded_handler
except ImportError:  # pragma: no cover - optional dependency.
    RateLimitExceeded = None
    SlowAPIMiddleware = None
    _rate_limit_exceeded_handler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    app.state.booking_deps = build_booking_deps()

    if _has_pg_saver:
        # Build a psycopg3-style DSN (no +asyncpg driver prefix)
        db_url = (
            f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
            f"@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        )
        pool = AsyncConnectionPool(
            db_url, min_size=1, max_size=5, open=False,
            kwargs={"autocommit": True},
        )
        await pool.open()
        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.setup()
        app.state._pg_pool = pool
    else:
        from langgraph.checkpoint.memory import MemorySaver
        checkpointer = MemorySaver()
        app.state._pg_pool = None

    app.state.booking_graph = build_booking_graph(checkpointer=checkpointer)
    yield

    if getattr(app.state, "_pg_pool", None):
        await app.state._pg_pool.close()

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(RequestContextMiddleware)

if limiter is not None and SlowAPIMiddleware is not None:
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    if RateLimitExceeded is not None and _rate_limit_exceeded_handler is not None:
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(health_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(hotels_router, prefix="/api/v1")
app.include_router(flights_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(bookings_router, prefix="/api/v1")


@app.get("/metrics", include_in_schema=False)
async def prometheus_metrics():
    content, media_type = metrics_response()
    return Response(content=content, media_type=media_type)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": "request failed",
            "data": exc.detail,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "internal server error",
            "data": "An unexpected error occurred.",
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "message": "validation error",
            "data": exc.errors(),
        },
    )
