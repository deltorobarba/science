"""Agent with a Google-managed remote MCP server (Developer Knowledge API).

Unlike the BigQuery server, this one is run by Google and authenticated with an API key. The key lives
in Secret Manager and is read on the first MCP request, so it never appears in code or in .env.
"""

import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset

load_dotenv()

DK_MCP_URL = "https://developerknowledge.googleapis.com/mcp"

_api_key: str | None = None


def _api_key_header(context=None) -> dict[str, str]:
    global _api_key
    if _api_key is None:
        from google.cloud import secretmanager

        name = f"projects/{os.environ['GOOGLE_CLOUD_PROJECT']}/secrets/{os.environ.get('DK_SECRET_NAME', 'mcp-dk')}/versions/latest"
        response = secretmanager.SecretManagerServiceClient().access_secret_version(request={"name": name})
        _api_key = response.payload.data.decode("utf-8")
    return {"X-Goog-Api-Key": _api_key}


root_agent = LlmAgent(
    name="google_docs_expert",
    model=os.environ.get("MODEL", "gemini-3.8-flash"),
    instruction=(
        "You are a Google Cloud expert. Use 'search_documents' or 'answer_query' to find information. "
        "List the results in a few bullet points and provide a code snippet."
    ),
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(url=DK_MCP_URL, timeout=30.0),
            header_provider=_api_key_header,
        )
    ],
)
