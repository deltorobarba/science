"""The agent is wired to the Streamable HTTP endpoint and can be deployed safely."""

import cloudpickle
import google.auth
import google.oauth2.id_token
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from vertexai.agent_engines import AdkApp

from bq_analyst import auth, config
from bq_analyst.agent import build_agent


def test_agent_uses_mcp_endpoint():
    agent = build_agent(discovery="url")
    (toolset,) = agent.tools
    assert isinstance(toolset, McpToolset)
    assert config.MCP_ENDPOINT == "https://bq-mcp-analyst-test.a.run.app/mcp"


def test_pickle_contains_no_credentials():
    """What deploy_agent.py uploads must not carry tokens; they are created at call time in the cloud."""
    blob = cloudpickle.dumps(AdkApp(agent=build_agent(discovery="url")))
    assert b"refresh_token" not in blob
    assert b"eyJ" not in blob  # start of a JWT (ID token)


def test_token_on_agent_runtime_uses_service_url_as_audience(monkeypatch):
    seen = {}

    def fake_fetch_id_token(request, audience):
        seen["audience"] = audience
        return "runtime-token"

    monkeypatch.setenv("GOOGLE_CLOUD_AGENT_ENGINE_ID", "123")
    monkeypatch.setattr(google.oauth2.id_token, "fetch_id_token", fake_fetch_id_token)
    assert auth.cloud_run_auth_header() == {"Authorization": "Bearer runtime-token"}
    assert seen["audience"] == config.MCP_SERVER_URL


def test_token_locally_comes_from_user_adc(monkeypatch):
    class FakeCredentials:
        id_token = "user-token"

        def refresh(self, request):
            pass

    monkeypatch.delenv("GOOGLE_CLOUD_AGENT_ENGINE_ID", raising=False)
    monkeypatch.setattr(google.auth, "default", lambda: (FakeCredentials(), "test-project"))
    assert auth.cloud_run_auth_header() == {"Authorization": "Bearer user-token"}
