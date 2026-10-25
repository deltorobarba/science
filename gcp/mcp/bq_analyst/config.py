"""Settings from environment variables.

Locally they come from .env (found by walking up from this file); on Agent Runtime they come from
the env_vars set in deployment/deploy_agent.py. Explicit environment variables always win over .env.
"""

import os

from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Environment variable {name} is not set (see .env.example).")
    return value


PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
REGION = os.environ.get("REGION", "us-central1")
MODEL = os.environ.get("MODEL", "gemini-3.8-flash")

# Cloud Run URL of the MCP server, without path. It is also the audience of the ID token.
MCP_SERVER_URL = _require("MCP_SERVER_URL").rstrip("/")
MCP_ENDPOINT = f"{MCP_SERVER_URL}/mcp"  # Streamable HTTP endpoint of FastMCP
MCP_TIMEOUT = float(os.environ.get("MCP_TIMEOUT", "30"))  # 30 s: room for a Cloud Run cold start

# "url": connect to MCP_ENDPOINT directly. "registry": look the server up in Agent Registry.
MCP_DISCOVERY = os.environ.get("MCP_DISCOVERY", "url").strip().lower()
