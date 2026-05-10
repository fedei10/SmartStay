from fastapi import FastAPI
from app.config import settings
from app.api.V1.health import router as health_router

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

app.include_router(health_router, prefix="/api/v1")