"""Model Garden: deployment options of an open model and deploying it to a Vertex AI endpoint.

A deployed endpoint costs money for as long as it exists (GPU per hour), whether it is used or not.

Choosing hardware for Gemma 4 26B (from the notebook):
* Model Garden recommends NVIDIA RTX Pro 6000 (Blackwell, 96 GB VRAM).
* An NVIDIA L4 (24 GB) is cheaper, but the 26B model in BF16 needs about 52 GB for its weights alone.
  With 4-bit quantization (AWQ, INT4) the weights take about 15-18 GB and fit on one L4, at the price of
  a much shorter context window (e.g. 8K-16K instead of 256K).
"""

import vertexai
from vertexai import model_garden

from . import config

DEFAULT_DEPLOYMENT = {
    "machine_type": "g4-standard-48",
    "accelerator_type": "NVIDIA_RTX_PRO_6000",
    "accelerator_count": 1,
    "serving_container_image_uri": "us-docker.pkg.dev/vertex-ai/vertex-vision-model-garden-dockers/pytorch-vllm-serve:gemma4",
}


def deploy_options(model_id: str) -> str:
    vertexai.init(project=config.DEPLOY_PROJECT, location=config.DEPLOY_REGION)
    return model_garden.OpenModel(model_id).list_deploy_options(concise=True)


def deploy(model_id: str, machine_type: str, accelerator_type: str, accelerator_count: int,
           serving_container_image_uri: str, endpoint_display_name: str):
    vertexai.init(project=config.DEPLOY_PROJECT, location=config.DEPLOY_REGION)
    return model_garden.OpenModel(model_id).deploy(
        accept_eula=True,
        machine_type=machine_type,
        accelerator_type=accelerator_type,
        accelerator_count=accelerator_count,
        serving_container_image_uri=serving_container_image_uri,
        endpoint_display_name=endpoint_display_name,
        use_dedicated_endpoint=True,
        reservation_affinity_type="NO_RESERVATION",
    )
