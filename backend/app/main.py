from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.agents.booking.dependencies import build_booking_deps
from app.agents.booking.graph import build_booking_graph
from app.api.V1.chat import router as chat_router
from app.api.V1.health import router as health_router
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.booking_deps = build_booking_deps()
    app.state.booking_graph = build_booking_graph()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
