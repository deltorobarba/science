"""Ask one of the agents locally (as your user), without the web UI.

Usage:
    uv run python scripts/ask.py ["question"]                        # bq_analyst
    uv run python scripts/ask.py --agent docs_expert ["question"]    # docs_expert
    MCP_DISCOVERY=registry uv run python scripts/ask.py              # bq_analyst finds the server via Agent Registry
Interactive alternatives: `uv run adk web` (browser) or `uv run adk run <agent>` (terminal chat).
"""

import argparse
import asyncio
import importlib

from google.adk.runners import InMemoryRunner
from google.genai import types

DEFAULT_QUESTIONS = {
    "bq_analyst": (
        "What were the top 3 most popular female names in the USA in 1980? "
        "Query the 'bigquery-public-data.usa_names.usa_1910_2013' table."
    ),
    "docs_expert": "How does 'config=' need to look like if I want to deploy an agent with Agent Identity?",
}


async def main(agent_name: str, question: str) -> None:
    agent = importlib.import_module(f"{agent_name}.agent").root_agent
    runner = InMemoryRunner(agent=agent, app_name=agent_name)
    session = await runner.session_service.create_session(app_name=agent_name, user_id="dev")
    message = types.Content(role="user", parts=[types.Part(text=question)])
    async for event in runner.run_async(user_id="dev", session_id=session.id, new_message=message):
        for part in event.content.parts if event.content else []:
            if part.function_call:
                print(f"🔧 {part.function_call.name}")
            elif part.text and not part.thought:
                print(f"🕵️ {part.text}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ask an agent of this project once.")
    parser.add_argument("question", nargs="?", help="default: an example question for the chosen agent")
    parser.add_argument("--agent", choices=DEFAULT_QUESTIONS, default="bq_analyst")
    args = parser.parse_args()
    asyncio.run(main(args.agent, args.question or DEFAULT_QUESTIONS[args.agent]))
