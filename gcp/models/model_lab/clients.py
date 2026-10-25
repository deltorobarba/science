"""Two ways to call models on Vertex AI: the Google GenAI SDK and the OpenAI SDK.

GenAI SDK: authenticates itself through Application Default Credentials and refreshes tokens.
OpenAI SDK: talks to Vertex AI's OpenAI-compatible endpoint; its "API key" is a Google access token,
which expires after about an hour. openai_client() fetches a fresh one on every call.
"""

import google.auth
import google.auth.transport.requests
from google import genai
from google.genai import types
from openai import OpenAI

from . import config


def genai_client() -> genai.Client:
    return genai.Client(vertexai=True, project=config.PROJECT_ID, location=config.MODEL_LOCATION)


def openai_client() -> OpenAI:
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    credentials.refresh(google.auth.transport.requests.Request())
    base_url = (
        f"https://aiplatform.googleapis.com/v1/projects/{config.PROJECT_ID}"
        f"/locations/{config.MODEL_LOCATION}/endpoints/openapi"
    )
    return OpenAI(base_url=base_url, api_key=credentials.token)


def tuned_config(system_instruction: str | None = None) -> types.GenerateContentConfig:
    """All common generation parameters set explicitly (the 'Full Track' of the notebook)."""
    return types.GenerateContentConfig(
        temperature=0.4,
        top_p=0.95,
        top_k=20,
        candidate_count=1,
        seed=5,
        max_output_tokens=120,
        stop_sequences=["STOP!"],
        presence_penalty=0.0,
        frequency_penalty=0.0,
        system_instruction=system_instruction,
    )


def ask_genai(model: str, prompt: str, tuned: bool = False, system_instruction: str | None = None) -> str:
    cfg = tuned_config(system_instruction) if tuned else None
    client = genai_client()  # keep a reference: a discarded Client closes its connection while the request runs
    response = client.models.generate_content(model=config.resolve(model), contents=prompt, config=cfg)
    return response.text or ""


def ask_openai(model: str, prompt: str, temperature: float = 0.2) -> str:
    response = openai_client().chat.completions.create(
        model=config.resolve(model),
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return response.choices[0].message.content or ""
