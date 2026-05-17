from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool

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


class LiteAPIMCPToolProvider:
    def __init__(self):
        self._tools: list[BaseTool] | None = None

    async def get_tools(self) -> list[BaseTool]:
        if self._tools is None:
            self._tools = await get_liteapi_tools()
        return self._tools

    async def get_tool_names(self) -> list[str]:
        return [tool.name for tool in await self.get_tools()]

    async def get_tool(self, name: str) -> BaseTool | None:
        tools = await self.get_tools()
        return next((tool for tool in tools if tool.name == name), None)

    async def ainvoke(self, name: str, args: dict):
        tool = await self.get_tool(name)
        if tool is None:
            raise ValueError(f"LiteAPI MCP tool '{name}' is not available")
        return await tool.ainvoke(args)
