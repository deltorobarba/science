"""The BigQuery analyst: an ADK agent whose only tool is the MCP server on Cloud Run."""

from google.adk.agents import LlmAgent
from google.adk.tools.base_toolset import BaseToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset

from . import config
from .auth import cloud_run_auth_header
from .prompt import ANALYST_INSTRUCTION


def _toolset_from_url() -> McpToolset:
    return McpToolset(
        connection_params=StreamableHTTPConnectionParams(url=config.MCP_ENDPOINT, timeout=config.MCP_TIMEOUT),
        header_provider=cloud_run_auth_header,
    )


def _toolset_from_registry() -> BaseToolset:
    """Find the server in Agent Registry by its endpoint and let ADK build the connection.

    The registry stores no credentials; the ID token still comes from cloud_run_auth_header.
    Tool names get the registry display name as prefix (BigQuery_MCP_Cloud_Run_query_public_dataset).
    """
    from google.adk.integrations.agent_registry import AgentRegistry

    registry = AgentRegistry(
        project_id=config.PROJECT_ID, location=config.REGION, header_provider=cloud_run_auth_header
    )
    servers = registry.list_mcp_servers().get("mcpServers", [])
    for server in servers:
        if any(i.get("url", "").rstrip("/") == config.MCP_ENDPOINT for i in server.get("interfaces", [])):
            return registry.get_mcp_toolset(server["name"])
    raise RuntimeError(f"No MCP server with endpoint {config.MCP_ENDPOINT} in Agent Registry ({config.REGION}).")


def build_agent(discovery: str | None = None) -> LlmAgent:
    """Build a fresh agent. Deployments always build their own instance, never reuse root_agent."""
    discovery = discovery or config.MCP_DISCOVERY
    if discovery == "registry":
        toolset = _toolset_from_registry()
    elif discovery == "url":
        toolset = _toolset_from_url()
    else:
        raise ValueError(f"MCP_DISCOVERY must be 'url' or 'registry', not {discovery!r}")
    return LlmAgent(name="bigquery_analyst", model=config.MODEL, instruction=ANALYST_INSTRUCTION, tools=[toolset])


root_agent = build_agent()
