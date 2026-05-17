



from fastapi import APIRouter, Query

from app.schemas.base import success_response
from app.services.elasticsearch.connection import test_elasticsearch_connection
from app.services.gemini.connection import test_gemini_connection
from app.services.liteapi.connection import test_liteapi_connection
from app.services.postgres.connection import test_postgres_connection as run_postgres_test
from app.services.redis.connection import test_redis_connection
from app.services.swiftrouter import check_swiftrouter

router = APIRouter(prefix="/health",tags=["Health"])




@router.get("")
async def health_check():
    return success_response(
        message="healthy",
        data={"status": "healthy"},
    )

@router.get("/gemini")
def test_gemini_connections():
    return success_response(
        message="gemini health checked",
        data={"gemini": test_gemini_connection()},
    )

@router.get("/postgres")
def test_postgres_connections():
    return success_response(
        message="postgres health checked",
        data={"postgres": run_postgres_test()},
    )


@router.get("/redis")
async def test_redis_connections():
    return success_response(
        message="redis health checked",
        data={"redis": await test_redis_connection()},
    )


@router.get("/elasticsearch")
async def test_elasticsearch_connections():
    return success_response(
        message="elasticsearch health checked",
        data={"elasticsearch": await test_elasticsearch_connection()},
    )

@router.get("/swiftrouter")
async def test_swiftrouter():
    result = await check_swiftrouter()
    code = 200 if result.get("ok") else 503
    return success_response(
        code=code,
        message="SwiftRouter reachable" if result.get("ok") else "SwiftRouter unavailable",
        data={"swiftrouter": result},
    )


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
        return success_response(
            message="LiteAPI returned hotels",
            data={"liteapi": result},
        )

    return success_response(
        code=503,
        message="LiteAPI did not return hotels",
        data={"liteapi": result},
    )
