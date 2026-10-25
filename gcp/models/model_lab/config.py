"""Settings from .env and the model catalog."""

import os

from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
MODEL_LOCATION = os.environ.get("MODEL_LOCATION", "global")
DEPLOY_PROJECT = os.environ.get("DEPLOY_PROJECT") or PROJECT_ID
DEPLOY_REGION = os.environ.get("DEPLOY_REGION", "us-central1")

# Short names for Model Garden / Vertex AI model IDs. Partner models need their user agreement accepted
# once per project in the console.
MODELS = {
    # closed models
    "gemini-pro": "google/gemini-4-argon",
    "gemini-flash": "google/gemini-3.8-flash",
    "grok": "xai/grok-4.1-fast-reasoning",
    "claude": "anthropic/claude-opus-4-7",
    # open models as a service (MaaS)
    "gemma": "google/gemma-4-26b-a4b-it-maas",
    "deepseek": "deepseek-ai/deepseek-v4.1-flash-maas",
    "glm": "zai-org/glm-5.2-maas",
}


def resolve(model: str) -> str:
    """Short name -> full model ID; full IDs pass through unchanged."""
    return MODELS.get(model, model)
