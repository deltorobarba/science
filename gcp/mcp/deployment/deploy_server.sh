#!/usr/bin/env bash
# Deploy the MCP server (mcp_server/) to Cloud Run as a private service and set the IAM it needs.
# Usage: deployment/deploy_server.sh        (re-run after changes to mcp_server/; creates a new revision)
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; source .env; set +a

PROJECT="${GOOGLE_CLOUD_PROJECT:?set GOOGLE_CLOUD_PROJECT in .env}"
SERVICE="${MCP_SERVICE_NAME:-bq-mcp-analyst}"
SA="${SERVICE}@${PROJECT}.iam.gserviceaccount.com"

# 1. Runtime identity of the server: its own service account (created once)
if ! gcloud iam service-accounts describe "$SA" --project "$PROJECT" >/dev/null 2>&1; then
  gcloud iam service-accounts create "$SERVICE" --project "$PROJECT" --display-name "BigQuery MCP server"
fi

# 2. The server starts BigQuery jobs as this account. Without the role: "403 ... bigquery.jobs.create"
gcloud projects add-iam-policy-binding "$PROJECT" --member "serviceAccount:$SA" \
  --role roles/bigquery.jobUser --condition None --quiet >/dev/null
echo "✅ roles/bigquery.jobUser for $SA"

# 3. Build from source (buildpacks read requirements.txt and Procfile) and deploy as a private service
gcloud run deploy "$SERVICE" --source mcp_server --region "$REGION" --project "$PROJECT" \
  --service-account "$SA" --no-allow-unauthenticated --quiet

# 4. Who may call it: your user. Project owners can call it anyway; an org policy may reject @gmail.com members.
USER_EMAIL="$(gcloud config get-value account 2>/dev/null)"
gcloud run services add-iam-policy-binding "$SERVICE" --region "$REGION" --project "$PROJECT" \
  --member "user:$USER_EMAIL" --role roles/run.invoker --quiet >/dev/null \
  && echo "✅ roles/run.invoker for $USER_EMAIL" \
  || echo "ℹ️  invoker binding for $USER_EMAIL rejected (e.g. org policy); project owners can call the service anyway"

echo "Service URLs (use one of them as MCP_SERVER_URL in .env):"
gcloud run services describe "$SERVICE" --region "$REGION" --project "$PROJECT" \
  --format 'value(metadata.annotations."run.googleapis.com/urls")'
