from urllib.parse import urlencode

from app.core.config import settings


LITEAPI_MCP_BASE_URL = "https://mcp.liteapi.travel/api/mcp"


def get_liteapi_mcp_server_config() -> dict:
    if not settings.LITEAPI_API_KEY:
        raise ValueError("LITEAPI_API_KEY is not configured")

    query = urlencode({"apiKey": settings.LITEAPI_API_KEY})
    return {
        "url": f"{LITEAPI_MCP_BASE_URL}?{query}",
        "transport": "streamable_http",
    }


def get_mcp_servers_config() -> dict:
    return {
        "liteapi": get_liteapi_mcp_server_config(),
    }
