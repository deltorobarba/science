"""Test settings: fixed values, so the tests neither depend on .env nor reach Google Cloud."""

import os
import sys
from pathlib import Path

os.environ["MCP_SERVER_URL"] = "https://bq-mcp-analyst-test.a.run.app"
os.environ["MCP_DISCOVERY"] = "url"
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "test-project")
os.environ.pop("GOOGLE_CLOUD_AGENT_ENGINE_ID", None)

# mcp_server/ is not a package: make main.py importable as "main"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mcp_server"))
