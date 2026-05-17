from typing import Any

from app.core.config import settings
from app.services.elasticsearch.connection import get_elasticsearch_connection


class OrchestrationRetriever:
    """Optional Elasticsearch-backed context retriever for routing decisions."""

    async def search(self, query: str, limit: int | None = None) -> list[dict[str, Any]]:
        if not query.strip():
            return []

        client = get_elasticsearch_connection()
        if client is None:
            return []

        size = limit or settings.ORCHESTRATOR_RETRIEVAL_LIMIT
        try:
            response = await client.search(
                index=settings.ELASTICSEARCH_INDEX,
                size=size,
                query={
                    "multi_match": {
                        "query": query,
                        "fields": ["title^2", "content", "summary", "tags"],
                    }
                },
            )
            await client.close()
        except Exception:
            return []

        hits = response.get("hits", {}).get("hits", [])
        return [
            {
                "score": hit.get("_score"),
                "source": hit.get("_source", {}),
            }
            for hit in hits
        ]
