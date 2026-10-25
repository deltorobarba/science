#!/usr/bin/env bash
# Register the MCP server in Agent Registry, or update the entry if it exists (create-or-update).
# The entry holds only metadata (URL, name, protocol), no credentials. A new Cloud Run revision keeps
# the URL, so re-running is only needed when these fields change.
# Usage: deployment/register_mcp.sh
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; source .env; set +a

PROJECT="${GOOGLE_CLOUD_PROJECT:?set GOOGLE_CLOUD_PROJECT in .env}"
ID="${MCP_REGISTRY_ID:-bq-mcp-analyst}"
FLAGS=(
  --display-name "BigQuery MCP (Cloud Run)"
  --description "FastMCP server with query_public_dataset; private Cloud Run, OIDC"
  --mcp-server-spec-type no-spec
  --interfaces "url=${MCP_SERVER_URL%/}/mcp,protocolBinding=jsonrpc"   # Streamable HTTP endpoint
)

if gcloud agent-registry services describe "$ID" --project "$PROJECT" --location "$REGION" >/dev/null 2>&1; then
  gcloud agent-registry services update "$ID" --project "$PROJECT" --location "$REGION" "${FLAGS[@]}" >/dev/null
  echo "🔄 '$ID' updated"
else
  gcloud agent-registry services create "$ID" --project "$PROJECT" --location "$REGION" "${FLAGS[@]}" >/dev/null
  echo "✅ '$ID' created"
fi

gcloud agent-registry mcp-servers list --location "$REGION" --project "$PROJECT" \
  --format "table(displayName,interfaces[0].url,interfaces[0].protocolBinding)"
