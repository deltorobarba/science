"""Authentication towards the private Cloud Run MCP server.

Cloud Run (deployed with --no-allow-unauthenticated) expects an OIDC ID token, not an access token.
Which identity signs it depends on where the agent runs:

* Agent Runtime (GOOGLE_CLOUD_AGENT_ENGINE_ID is set): the Reasoning Engine service agent. The token
  comes from the metadata server and must carry the service URL as audience.
* Locally: your user account from ADC (`gcloud auth application-default login`). Cloud Run accepts
  user ID tokens whose audience is the ADC client ID.

The token is created on every call, so nothing token-related is pickled when the agent is deployed.
"""

import os

import google.auth
import google.auth.transport.requests
import google.oauth2.id_token

from . import config


def running_on_agent_runtime() -> bool:
    return bool(os.environ.get("GOOGLE_CLOUD_AGENT_ENGINE_ID"))


def cloud_run_id_token() -> str:
    request = google.auth.transport.requests.Request()
    if running_on_agent_runtime():
        return google.oauth2.id_token.fetch_id_token(request, config.MCP_SERVER_URL)

    credentials, _ = google.auth.default()
    credentials.refresh(request)
    token = getattr(credentials, "id_token", None)
    if not token:
        raise RuntimeError(
            "ADC returned no ID token. Run 'gcloud auth application-default login' with your user account."
        )
    return token


def cloud_run_auth_header(context=None) -> dict[str, str]:
    """header_provider for ADK: called before every MCP request (only while an agent runs)."""
    return {"Authorization": f"Bearer {cloud_run_id_token()}"}
