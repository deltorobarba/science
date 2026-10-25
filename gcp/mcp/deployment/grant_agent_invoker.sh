#!/usr/bin/env bash
# Allow the deployed agent to call the MCP server. On Agent Runtime the agent runs as the Reasoning Engine
# service agent, not as you; without roles/run.invoker the MCP server answers 403. The role is granted on
# this one service only, not on the project (least privilege).
# Usage: deployment/grant_agent_invoker.sh
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; source .env; set +a

PROJECT="${GOOGLE_CLOUD_PROJECT:?set GOOGLE_CLOUD_PROJECT in .env}"
SERVICE="${MCP_SERVICE_NAME:-bq-mcp-analyst}"
PROJECT_NUMBER="$(gcloud projects describe "$PROJECT" --format 'value(projectNumber)')"
AGENT_SA="service-${PROJECT_NUMBER}@gcp-sa-aiplatform-re.iam.gserviceaccount.com"

gcloud run services add-iam-policy-binding "$SERVICE" --region "$REGION" --project "$PROJECT" \
  --member "serviceAccount:$AGENT_SA" --role roles/run.invoker --quiet >/dev/null
echo "✅ roles/run.invoker on $SERVICE for $AGENT_SA"
