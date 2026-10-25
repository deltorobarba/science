"""Check the MCP server without an LLM: registry entry, then tools/list over Streamable HTTP.

Usage: uv run python scripts/check_mcp.py

Uses a static Authorization header here: ADK calls header_provider only while an agent runs.
"""

import asyncio

from google.adk.integrations.agent_registry import AgentRegistry
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset

from bq_analyst import config
from bq_analyst.auth import cloud_run_auth_header


def show_registry_entry() -> None:
    registry = AgentRegistry(project_id=config.PROJECT_ID, location=config.REGION)
    for server in registry.list_mcp_servers().get("mcpServers", []):
        urls = [i.get("url") for i in server.get("interfaces", [])]
        if config.MCP_ENDPOINT in [u.rstrip("/") for u in urls]:
            print(f"Agent Registry: {server.get('displayName')} -> {urls}")
            return
    print(f"Agent Registry: no entry for {config.MCP_ENDPOINT} (run deployment/register_mcp.sh)")


async def list_tools() -> None:
    toolset = McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=config.MCP_ENDPOINT, headers=cloud_run_auth_header(), timeout=config.MCP_TIMEOUT
        )
    )
    try:
        tools = await toolset.get_tools()
        print(f"MCP server {config.MCP_ENDPOINT}: tools = {[t.name for t in tools]}")
    finally:
        await toolset.close()


if __name__ == "__main__":
    show_registry_entry()
    asyncio.run(list_tools())
