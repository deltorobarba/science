"""Ask the BigQuery analyst locally (as your user), without the web UI.

Usage:
    uv run python scripts/ask.py ["question"]
    MCP_DISCOVERY=registry uv run python scripts/ask.py     # find the server via Agent Registry
Interactive alternatives: `uv run adk web` (browser) or `uv run adk run bq_analyst` (terminal).
"""

import asyncio
import sys

from google.adk.runners import InMemoryRunner
from google.genai import types

from bq_analyst.agent import build_agent

DEFAULT_QUESTION = (
    "What were the top 3 most popular female names in the USA in 1980? "
    "Query the 'bigquery-public-data.usa_names.usa_1910_2013' table."
)


async def main(question: str) -> None:
    runner = InMemoryRunner(agent=build_agent(), app_name="bq_analyst")
    session = await runner.session_service.create_session(app_name="bq_analyst", user_id="dev")
    message = types.Content(role="user", parts=[types.Part(text=question)])
    async for event in runner.run_async(user_id="dev", session_id=session.id, new_message=message):
        for part in event.content.parts if event.content else []:
            if part.function_call:
                print(f"🔧 {part.function_call.name}")
            elif part.text and not part.thought:
                print(f"🕵️ {part.text}")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_QUESTION))
