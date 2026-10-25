"""Deploy the BigQuery analyst to Agent Runtime (create, or update if AGENT_ENGINE_NAME is set).

Usage (from the project root):
    uv run python deployment/deploy_agent.py --dry-run   # show the configuration only
    uv run python deployment/deploy_agent.py

The agent is pickled locally and unpickled in the cloud. Therefore:
* the package bq_analyst/ is shipped as code (extra_packages) and pickled by reference,
* the requirements pin exactly the versions installed in this environment (.venv),
* the agent is built fresh here (never the root_agent a local run may have used),
* the ID token is created at call time in the cloud (bq_analyst/auth.py), nothing token-related is pickled.
"""

import argparse
import json
import logging
import os
import sys
from importlib.metadata import version
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.chdir(PROJECT_ROOT)  # extra_packages are resolved relative to the working directory

import vertexai  # noqa: E402
from vertexai.agent_engines import AdkApp  # noqa: E402

from bq_analyst import config  # noqa: E402
from bq_analyst.agent import build_agent  # noqa: E402

DISPLAY_NAME = "bq-mcp-analyst-project"
PACKAGES = ["google-cloud-aiplatform", "google-adk", "google-genai", "mcp", "cloudpickle", "pydantic"]


def requirements() -> list[str]:
    pins = {name: version(name) for name in PACKAGES}
    pins["google-cloud-aiplatform[agent_engines,adk]"] = pins.pop("google-cloud-aiplatform")
    return [f"{name}=={v}" for name, v in pins.items()]


def engine_config() -> dict:
    return {
        "display_name": DISPLAY_NAME,
        "description": "BigQuery analyst that calls the private Cloud Run MCP server (Streamable HTTP, OIDC)",
        "staging_bucket": os.environ["STAGING_BUCKET"],
        "gcs_dir_name": "bq_mcp_analyst_project",  # own folder; pickles of other deployments stay untouched
        "requirements": requirements(),
        "extra_packages": ["bq_analyst"],
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",  # same as the pickling side
        "env_vars": {
            "GOOGLE_CLOUD_LOCATION": "global",  # Gemini 3.x
            "MODEL": config.MODEL,
            "MCP_SERVER_URL": config.MCP_SERVER_URL,
            "MCP_DISCOVERY": "url",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true", help="print the configuration, do not deploy")
    args = parser.parse_args()

    cfg = engine_config()
    engine_name = os.environ.get("AGENT_ENGINE_NAME", "").strip()
    print(("Update " + engine_name) if engine_name else "Create a new engine", "with:")
    print(json.dumps(cfg, indent=2))
    if args.dry_run:
        return

    # Show the SDK's progress (it logs LRO and resource name at INFO)
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("vertexai_genai.agentengines").setLevel(logging.INFO)

    vertexai.init(project=config.PROJECT_ID, location=config.REGION)
    client = vertexai.Client(project=config.PROJECT_ID, location=config.REGION)
    app = AdkApp(agent=build_agent(discovery="url"))  # fresh instance, fixed URL (no registry lookup at deploy time)

    if engine_name:
        client.agent_engines.update(name=engine_name, agent=app, config=cfg)
        print(f"\n✅ Engine updated: {engine_name}")
    else:
        engine = client.agent_engines.create(agent=app, config=cfg)
        engine_name = engine.api_resource.name
        print(f"\n✅ Engine created: {engine_name}\n   Add to .env:  AGENT_ENGINE_NAME={engine_name}")
    print("Identity:", client.agent_engines.get(name=engine_name).api_resource.spec.effective_identity)


if __name__ == "__main__":
    main()
