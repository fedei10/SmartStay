



from fastapi import APIRouter, Query
from app.services.gemini.connection import test_gemini_connection
from app.services.liteapi.connection import test_liteapi_connection
from app.services.postgres.connection import test_postgres_connection as run_postgres_test

router = APIRouter(prefix="/health",tags=["Health"])




@router.get("")
async def health_check():
    return {"status": "healthy"}

@router.get("/gemini")
def test_gemini_connections():
    return {
        "gemini": test_gemini_connection(),
    }

@router.get("/postgres")
def test_postgres_connections():
    return {
        "postgres": run_postgres_test(),
    }

@router.get("/liteapi")
def test_liteapi_connections(
    api_key: str | None = Query(
        default=None,
        description="LiteAPI key to test. Falls back to LITEAPI_API_KEY from .env when omitted.",
    ),
    country_code: str = Query(default="IT", description="Hotel search country code."),
    city_name: str = Query(default="Rome", description="Hotel search city name."),
):
    result = test_liteapi_connection(
        api_key=api_key,
        country_code=country_code,
        city_name=city_name,
    )

    if result.get("status") == "ok" and result.get("result_count", 0) > 0:
        return {
            "status": "success",
            "message": "LiteAPI returned hotels",
            "liteapi": result,
        }

    return {
        "status": "error",
        "message": "LiteAPI did not return hotels",
        "liteapi": result,
    }
