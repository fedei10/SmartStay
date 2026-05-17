from app.core.config import settings

try:
    from elasticsearch import AsyncElasticsearch
except ImportError:  # pragma: no cover - optional service dependency.
    AsyncElasticsearch = None


def get_elasticsearch_connection():
    if AsyncElasticsearch is None or not settings.ELASTICSEARCH_HOST:
        return None

    kwargs = {}
    if settings.ELASTICSEARCH_USER and settings.ELASTICSEARCH_PASSWORD:
        kwargs["basic_auth"] = (
            settings.ELASTICSEARCH_USER,
            settings.ELASTICSEARCH_PASSWORD,
        )

    return AsyncElasticsearch(settings.ELASTICSEARCH_HOST, **kwargs)


async def test_elasticsearch_connection() -> str:
    client = get_elasticsearch_connection()
    if client is None:
        return "Elasticsearch is not configured"

    try:
        info = await client.info()
        await client.close()
        return f"Elasticsearch connected: {info['version']['number']}"
    except Exception as exc:
        return f"Elasticsearch connection failed: {exc}"
