# Model Lab

Modelle auf Google Cloud aufrufen, vergleichen, bewerten und deployen: Gemini, Partner-Modelle (Grok, Claude) und offene Modelle als Service (Gemma, DeepSeek, GLM). Inhaltlich dasselbe wie `../models.ipynb`, aber als Projekt mit einer Kommandozeile `model-lab`.

## Aufbau

```
models/
├── pyproject.toml, uv.lock, .python-version   uv-Projekt (Python 3.12); definiert den Befehl model-lab
├── .env.example / .env                        Projekt, Modell-Region, Deploy-Projekt (.env bleibt lokal)
├── model_lab/
│   ├── cli.py          die Kommandozeile (models, ask, speed, latency, evaluate, garden)
│   ├── config.py       Einstellungen und Modellkatalog (Kurznamen → Modell-IDs)
│   ├── clients.py      zwei Wege zum Modell: Google GenAI SDK und OpenAI SDK
│   ├── benchmark.py    TTFT, Gesamtzeit, Tokens, TPS; Perzentile; Plot
│   ├── evaluation.py   LLM-as-a-Judge (paarweise) und Rubrik-Evaluation
│   └── garden.py       Model Garden: Deploy-Optionen und Deploy
├── docs/benchmark_notes.md   Auswertungen der Benchmarks aus dem Notebook
└── tests/                    pytest, ohne Google Cloud
```

| `models.ipynb` | Projekt |
|---|---|
| Installs, Imports, Environmental Variables | `pyproject.toml`, `uv sync`, `.env`, `model_lab/config.py` |
| Models on Google Cloud (Katalog) | `model-lab models` |
| Google SDK (Fast Track / Full Track) | `model-lab ask MODELL "…"` / `… --tuned --system "…"` |
| OpenAI SDK for LLMs on Google Cloud | `model-lab ask MODELL "…" --sdk openai` |
| Model Benchmark (Speed) & LLM-as-a-Judge | `model-lab speed` / `… --judge gemini-3.8-flash` |
| Single-Model Latency Benchmark | `model-lab latency` (Plot in `results/`) |
| Model Evaluation (Rubriken) | `model-lab evaluate` |
| Deployment Recommendation / Deployment Script | `model-lab garden options` / `model-lab garden deploy … --yes` |
| Markdown-Auswertungen | `docs/benchmark_notes.md` |

## Einrichten

```bash
cd ~/science/gcp/models
uv sync                                   # Umgebung in .venv (→ .venv.nosync, nicht in iCloud)
gcloud auth application-default login     # ADC: alles läuft als dein User
```

Partner-Modelle (Claude, Grok, DeepSeek, GLM …) brauchen einmal pro Projekt die Zustimmung zu ihren Nutzungsbedingungen in der Console (Model Garden).

## Benutzen

```bash
uv run model-lab --help                                  # alle Befehle; je Befehl: uv run model-lab speed --help
uv run model-lab models                                  # Kurznamen und Modell-IDs
uv run model-lab ask gemma "Welche Fähigkeiten hast du?"
uv run model-lab ask gemini-pro "Wer bist du?" --tuned --system "Answer briefly."
uv run model-lab ask deepseek "Which LLM are you?" --sdk openai
uv run model-lab speed                                   # gemini-3.8-flash gegen deepseek, 3 Kategorien
uv run model-lab speed --category "Code Generation" --judge gemini-3.8-flash
uv run model-lab latency --model deepseek --runs 10      # Tabelle + results/latency_<modell>_<zeit>.png
uv run model-lab evaluate --limit 3                      # Rubrik-Vergleich mit 3 der 10 Prompts
uv run model-lab garden options                          # Hardware-Optionen für Gemma 4 26B
uv run pytest                                            # Tests
```

Mit aktivierter Umgebung (`source .venv/bin/activate`) entfällt das `uv run`.

## Was man wissen sollte

* **Zwei SDKs, ein Endpunkt-Modell:** Das Google GenAI SDK meldet sich über ADC selbst an und erneuert Tokens. Das OpenAI SDK spricht Vertex AIs OpenAI-kompatiblen Endpunkt an; sein „API-Key“ ist ein Google-Access-Token, das nach etwa einer Stunde abläuft. `clients.openai_client()` holt deshalb bei jedem Aufruf ein frisches.
* **TTFT** ist die Zeit bis zum ersten gestreamten Chunk. Bei Modellen, die vor der Antwort „denken“, steckt die Denkzeit darin; `speed` gibt deshalb auch die **Thinking Tokens** aus. Wartezeit durch 429 (Kontingent) steckt ebenfalls in der TTFT und lässt sich so von Denkzeit unterscheiden.
* **Perzentile statt Mittelwert:** Ein einzelner Ausreißer zieht den Mittelwert hoch; der Median (P50) zeigt den typischen Lauf, P90/P95 die Ausreißer, für die man Timeouts auslegt (siehe `docs/benchmark_notes.md`).
* **Kosten:** `evaluate` ruft pro Prompt mehrere Modelle auf (Rubriken, Antworten, Bewertung), daher `--limit`. `garden deploy` legt einen Endpoint mit GPU an, der stündlich kostet, bis er gelöscht ist; ohne `--yes` zeigt der Befehl nur, was er täte.
* **Hardware für Gemma 4 26B:** Model Garden empfiehlt RTX Pro 6000 (96 GB). Eine L4 (24 GB) reicht nur mit 4-Bit-Quantisierung (AWQ/INT4, ~15–18 GB) und deutlich kürzerem Kontextfenster (siehe `model_lab/garden.py`).

## Hinweise

* **iCloud:** Die Umgebung liegt in `.venv.nosync` (iCloud synchronisiert `.nosync`-Ordner nicht), `.venv` ist ein Verweis darauf. Auf einem anderen Mac: `mkdir .venv.nosync && ln -s .venv.nosync .venv && uv sync`.
* **LiteLLM:** Das Notebook installierte und importierte LiteLLM, benutzte es aber nicht; das Projekt verzichtet darauf. Es kommt trotzdem als Abhängigkeit des Evaluation-Extras von `google-cloud-aiplatform` mit.
