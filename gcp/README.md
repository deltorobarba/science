# Generative AI on Google Cloud

Working notebooks for building and running generative AI on Google Cloud: models, agents, MCP, evaluation and the authentication paths between them. Two notebooks cover neighbouring tools (Google AI Studio, Hugging Face). Comments and notes are mostly in German.

| File | What it covers | Main services |
|---|---|---|
| [models.ipynb](models.ipynb) | Calling models three ways (Google GenAI SDK, OpenAI SDK, LiteLLM): Gemini, Gemma and partner/open models as a service (DeepSeek, Qwen, Kimi, MiniMax, GLM, Grok); choosing hardware and deploying Gemma to an endpoint | Vertex AI, Model Garden |
| [agents.ipynb](agents.ipynb) | Multi-agent pipeline with ADK: parallel retrieval (Google Search, Vertex AI Search, URL context), analyst with memory, summarizer; deployment, single- and multi-turn tests, Memory Bank | ADK, Agent Engine, Vertex AI Search |
| [evaluation.ipynb](evaluation.ipynb) | Agent evaluation and model evaluation: computed metrics (ROUGE, BLEU), rubric-based quality, comparison of open models | Gen AI evaluation service |
| [mcp.ipynb](mcp.ipynb) | BigQuery MCP server on a private Cloud Run service, called from an ADK agent with an OIDC ID token; managed MCP server (Developer Knowledge API); comparison with `claude.ipynb` | Cloud Run, BigQuery, MCP |
| [claude.ipynb](claude.ipynb) | "Repo Intelligence": combines `agents.ipynb` and `mcp.ipynb` into one system that uses every authentication path once: ADC, Agent Identity (SPIFFE), Auth Manager, agent-to-agent (A2A), private Cloud Run, Agent Registry, Gemini Enterprise | Agent Engine, A2A, Agent Identity |
| [googleaistudio.ipynb](googleaistudio.ipynb) | Gemini API with an AI Studio key: image generation (Gemini 3.1 Flash Image) and music generation (Lyria 3) | Google AI Studio |
| [huggingface.ipynb](huggingface.ipynb) | Running Mistral-7B-Instruct with `transformers`, including 4-bit quantization (bitsandbytes) | Hugging Face Hub, Colab |
| [sdlc.md](sdlc.md) | Study notes: authentication and authorization for agents on Google Cloud, and a twelve-module agenda "AI for Software Engineering" | – |

## Reading order

`models` → `agents` → `evaluation` → `mcp` → `claude`. The last notebook builds on the deployed agent from `agents.ipynb` and the Cloud Run service from `mcp.ipynb`; the security part of `sdlc.md` explains the concepts behind it.

## Before running

* **Project:** the setup cell of each notebook sets project ID, region and bucket. Replace them with your own project and authenticate with `gcloud auth application-default login`.
* **Secrets:** no notebook contains keys. `googleaistudio.ipynb` reads `GEMINI_API_KEY` from a local `.env` file next to the notebook (never committed) or asks for it; `huggingface.ipynb` reads `HF_TOKEN` from Colab secrets; `claude.ipynb` asks for a GitHub token once and stores it in Auth Manager.
* **Costs:** cells marked "⚠️ once only" create cloud resources (API enablement, Cloud Run services, agent and model deployments). Endpoints and deployed agents keep costing money until they are deleted.
