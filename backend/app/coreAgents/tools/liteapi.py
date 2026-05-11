from langchain_mcp_adapters.client import MultiServerMCPClient

from app.core.config import settings
from app.coreAgents.mcp.liteapi import get_mcp_servers_config


def get_liteapi_mcp_client() -> MultiServerMCPClient:
    return MultiServerMCPClient(get_mcp_servers_config())


async def get_liteapi_tools():
    client = get_liteapi_mcp_client()
    tools = await client.get_tools()
    allowed_tools = settings.LITEAPI_MCP_ALLOWED_TOOLS

    if not allowed_tools:
        return tools

    return [tool for tool in tools if tool.name in allowed_tools]
