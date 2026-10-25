"""MCP server with one BigQuery tool, served over Streamable HTTP on Cloud Run.

Run locally:  uv run uvicorn main:app --app-dir mcp_server --port 8080
Deploy:       deployment/deploy_server.sh
"""

from google.cloud import bigquery
from mcp.server.fastmcp import FastMCP

FORBIDDEN = ("DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "TRUNCATE")

# host="0.0.0.0": with the default 127.0.0.1, mcp enables DNS-rebinding protection for localhost only,
#                 and Cloud Run requests (Host: <service>.run.app) are rejected with 421 "Invalid Host header".
# stateless_http=True: every request stands alone, so Cloud Run may route it to any instance.
mcp = FastMCP("bigquery-analyst", host="0.0.0.0", stateless_http=True)


@mcp.tool()
def query_public_dataset(sql_query: str) -> str:
    """Run a read-only SQL query against BigQuery public datasets."""
    if any(cmd in sql_query.upper() for cmd in FORBIDDEN):
        return "Error: Modification queries are not allowed. Read-only access."
    try:
        client = bigquery.Client()  # runs as the Cloud Run service account (needs roles/bigquery.jobUser)
        rows = client.query(sql_query).result(max_results=20)
        results = [dict(row) for row in rows]
        return str(results) if results else "No results found."
    except Exception as e:
        return f"BigQuery Error: {e}"


# Starlette app with a single Streamable HTTP endpoint: /mcp
app = mcp.streamable_http_app()
