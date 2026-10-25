"""Query the deployed agent on Agent Runtime.

Usage: uv run python deployment/test_deployment.py ["question"]

Now the MCP server is called by the Reasoning Engine service agent, not by you.
403 in the answer: deployment/grant_agent_invoker.sh missing or not yet effective (wait a few minutes).
401: wrong audience of the ID token (MCP_SERVER_URL must be exactly the service URL).
"""

import asyncio
import os
import sys

import vertexai
from dotenv import load_dotenv

load_dotenv()

DEFAULT_QUESTION = (
    "What were the top 3 most popular female names in the USA in 1980? "
    "Query the 'bigquery-public-data.usa_names.usa_1910_2013' table."
)


async def main(question: str) -> None:
    name = os.environ.get("AGENT_ENGINE_NAME", "").strip()
    if not name:
        sys.exit("AGENT_ENGINE_NAME is empty: run deployment/deploy_agent.py first and add the name to .env")
    client = vertexai.Client(project=os.environ["GOOGLE_CLOUD_PROJECT"], location=os.environ.get("REGION", "us-central1"))
    engine = client.agent_engines.get(name=name)

    session = await engine.async_create_session(user_id="dev")
    print(f"Engine: {name}\nSession: {session['id']}\n")
    async for event in engine.async_stream_query(user_id="dev", session_id=session["id"], message=question):
        for part in event.get("content", {}).get("parts", []):
            if "function_call" in part:
                print(f"🔧 {part['function_call']['name']}")
            elif "text" in part and not part.get("thought"):
                print(f"🕵️ {part['text']}")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_QUESTION))
