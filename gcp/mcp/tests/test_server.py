"""The MCP server answers over Streamable HTTP even with the Host header Cloud Run sends.

No BigQuery call: initialize and tools/list only.
"""

import asyncio

import httpx
from mcp.server.fastmcp import FastMCP

import main

CLOUD_RUN_HOST = "bq-mcp-analyst-622694106880.us-central1.run.app"
HEADERS = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json", "Host": CLOUD_RUN_HOST}
INITIALIZE = {
    "jsonrpc": "2.0", "id": 1, "method": "initialize",
    "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "test", "version": "0"}},
}
TOOLS_LIST = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}


async def _post(server: FastMCP, app, *payloads) -> list[httpx.Response]:
    async with server.session_manager.run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return [await client.post("/mcp", json=p, headers=HEADERS) for p in payloads]


def test_streamable_http_with_cloud_run_host():
    init, tools = asyncio.run(_post(main.mcp, main.app, INITIALIZE, TOOLS_LIST))
    assert init.status_code == 200
    assert tools.status_code == 200
    assert "query_public_dataset" in tools.text


def test_default_host_would_reject_cloud_run():
    """Why main.py sets host="0.0.0.0": the default 127.0.0.1 enables DNS-rebinding protection."""
    server = FastMCP("default-host", stateless_http=True)
    (init,) = asyncio.run(_post(server, server.streamable_http_app(), INITIALIZE))
    assert init.status_code == 421


def test_write_queries_are_refused():
    assert main.query_public_dataset("DROP TABLE x").startswith("Error:")
