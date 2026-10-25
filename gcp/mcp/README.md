# BigQuery-MCP-Projekt

Ein eigener MCP-Server mit einem BigQuery-Tool auf Cloud Run und ADK-Agents, die ihn nutzen: lokal, über die Agent Registry und als deployter Agent auf Agent Runtime. Dazu ein zweiter Agent mit Googles verwaltetem Developer-Knowledge-MCP. Inhaltlich dasselbe wie `../mcp.ipynb`, aber als Projekt aufgebaut, wie man es in einer Entwicklungsumgebung macht: Python-Pakete statt Notebook-Zellen, eine `uv`-Umgebung, Konfiguration in `.env`, Tests mit `pytest`, Deploy-Schritte als Skripte.

## Aufbau

```
mcp/
├── pyproject.toml            Abhängigkeiten (uv); uv.lock hält die genauen Versionen fest
├── .python-version           3.12, gleich wie beim Deploy (das Pickle muss passen)
├── .env.example / .env       Konfiguration (.env bleibt lokal)
├── bq_analyst/               ADK-Agent (adk web / adk run / Deploy)
│   ├── agent.py              root_agent, build_agent(); Verbindung per URL oder über die Registry
│   ├── auth.py               ID-Token für Cloud Run: lokal dein User, deployed der Service Agent
│   ├── config.py             Einstellungen aus der Umgebung
│   └── prompt.py             Anweisung an den Analysten
├── docs_expert/              ADK-Agent mit Googles Developer-Knowledge-MCP (API-Key aus Secret Manager)
├── mcp_server/               der MCP-Server für Cloud Run (main.py, requirements.txt, Procfile)
├── deployment/
│   ├── deploy_server.sh      Cloud Run deployen + IAM (Dienstkonto, bigquery.jobUser, run.invoker)
│   ├── register_mcp.sh       Agent Registry: anlegen oder aktualisieren
│   ├── grant_agent_invoker.sh  run.invoker für den Service Agent von Agent Runtime
│   ├── deploy_agent.py       bq_analyst auf Agent Runtime (create oder update)
│   └── test_deployment.py    den deployten Agent abfragen
├── scripts/
│   ├── ask.py                Agent lokal mit einer Frage starten
│   └── check_mcp.py          Registry-Eintrag und tools/list prüfen, ohne LLM
└── tests/                    pytest: Server, Agent, Token-Logik, Pickle
```

## Vom Notebook zum Projekt

| `mcp.ipynb` | Projekt |
|---|---|
| Installs, Imports | `pyproject.toml`, `uv sync` |
| Environmental Variables | `.env`, `bq_analyst/config.py` |
| Create files for Cloud Run Deployment | `mcp_server/` |
| Set Permissions and Deploy | `deployment/deploy_server.sh` |
| Agent Registry: registrieren oder aktualisieren | `deployment/register_mcp.sh` |
| Test MCP connection | `scripts/check_mcp.py` |
| Test MCP server (lokaler Agent) | `scripts/ask.py`, `adk web`, `adk run` |
| Agent Registry: finden und nutzen | `MCP_DISCOVERY=registry` (in `bq_analyst/agent.py`) |
| Special: Developer Knowledge | `docs_expert/` |
| UC1a (Agent definieren) | `bq_analyst/agent.py`, `bq_analyst/auth.py` |
| UC1b (lokaler Test) | `scripts/ask.py` |
| UC1c (run.invoker für den Service Agent) | `deployment/grant_agent_invoker.sh` |
| UC1d, UC1e (Deploy, Test) | `deployment/deploy_agent.py`, `deployment/test_deployment.py` |
| Erklärzellen | dieser README, Abschnitt „Wie die Teile zusammenhängen“ |

## Einrichten

```bash
cd gcp/mcp
uv sync                                   # Python 3.12 + alle Pakete in .venv, genau nach uv.lock
gcloud auth application-default login     # ADC: lokal läuft alles als dein User
```

`.env` ist schon ausgefüllt (Vorlage: `.env.example`). `uv run <befehl>` führt einen Befehl in dieser Umgebung aus; aktivieren muss man sie nicht.

## Lokal entwickeln

```bash
uv run pytest                                  # Tests, ohne Google Cloud
uv run python scripts/check_mcp.py             # Registry-Eintrag + tools/list des Cloud-Run-Servers
uv run python scripts/ask.py "Welche Namen …"  # bq_analyst einmal fragen
MCP_DISCOVERY=registry uv run python scripts/ask.py   # dasselbe, Server über die Agent Registry gefunden
uv run python scripts/ask.py --agent docs_expert "…" # docs_expert einmal fragen
uv run adk web                                 # Browser-Oberfläche: bq_analyst oder docs_expert wählen
uv run adk run bq_analyst                      # Chat im Terminal (ebenso: adk run docs_expert; Ende mit exit)
```

`python bq_analyst/agent.py` startet nichts: Die Datei *definiert* den Agent (`root_agent`) nur. Ausgeführt wird er über `adk run`, `adk web` oder `scripts/ask.py`. Mit aktivierter Umgebung (`source .venv/bin/activate`) entfällt jeweils das `uv run`.

Den MCP-Server kann man auch lokal starten (`uv run uvicorn main:app --app-dir mcp_server --port 8080`) und mit `MCP_SERVER_URL=http://localhost:8080` dagegen arbeiten; BigQuery läuft dann als dein User.

## In die Cloud

Reihenfolge, jeweils aus `gcp/mcp/`:

```bash
deployment/deploy_server.sh                        # 1. MCP-Server auf Cloud Run + IAM (nach Änderungen an mcp_server/ erneut)
deployment/register_mcp.sh                         # 2. Eintrag in der Agent Registry (anlegen oder aktualisieren)
deployment/grant_agent_invoker.sh                  # 3. der deployte Agent darf den Server aufrufen
uv run python deployment/deploy_agent.py --dry-run # 4a. Konfiguration ansehen
uv run python deployment/deploy_agent.py           # 4b. Agent auf Agent Runtime; den ausgegebenen Namen als AGENT_ENGINE_NAME in .env eintragen
uv run python deployment/test_deployment.py        # 5. den deployten Agent fragen
```

`deploy_agent.py` legt eine eigene Engine `bq-mcp-analyst-project` an, unabhängig von der Engine aus dem Notebook. Steht `AGENT_ENGINE_NAME` in `.env`, aktualisiert es diese Engine stattdessen.

## Wie die Teile zusammenhängen

```
Du ──▶ Agent Runtime: Agent "bigquery_analyst"            läuft als Reasoning-Engine-Service-Agent
          │  MCP tools/call (Streamable HTTP, POST /mcp)   ID-Token vom Metadata-Server, Audience = Dienst-URL
          ▼
       Cloud Run: MCP-Server bq-mcp-analyst                prüft Token und roles/run.invoker
          │  SQL-Job                                       als Dienstkonto bq-mcp-analyst@… (roles/bigquery.jobUser)
          ▼
       BigQuery: bigquery-public-data
```

| Schritt | Wer ruft wen | Token | Nötige Rolle | Wo im Projekt |
|---|---|---|---|---|
| Registry lesen | du / Agent → `agentregistry.googleapis.com` | Access-Token aus ADC | Leserecht auf die Registry | `bq_analyst/agent.py` (Modus `registry`) |
| MCP aufrufen | du lokal bzw. Service Agent deployed → Cloud Run | **ID-Token** (OIDC) | `roles/run.invoker` | `bq_analyst/auth.py`, `deployment/grant_agent_invoker.sh` |
| BigQuery abfragen | Dienstkonto des Servers → BigQuery | Access-Token des Dienstkontos | `roles/bigquery.jobUser` | `mcp_server/main.py`, `deployment/deploy_server.sh` |

Die Entscheidungen im Code, jeweils mit Grund:

* **Streamable HTTP statt SSE** (`mcp.streamable_http_app()`, Endpunkt `/mcp`): ein normaler POST pro Nachricht, die Antwort im selben Response. ADKs Registry-Client baut nur Streamable-HTTP-Verbindungen.
* **`host="0.0.0.0"`** im Server: Mit dem Standard `127.0.0.1` schaltet `mcp` einen Schutz gegen DNS-Rebinding ein und lehnt den Cloud-Run-Hostnamen mit 421 ab (`tests/test_server.py` prüft beides).
* **`stateless_http=True`**: Jede Anfrage steht für sich, Cloud Run darf sie auf beliebige Instanzen verteilen.
* **Token erst beim Aufruf** (`auth.cloud_run_auth_header`): ADK ruft die Funktion vor jedem MCP-Aufruf eines laufenden Agents. Sie erkennt Agent Runtime an `GOOGLE_CLOUD_AGENT_ENGINE_ID` und holt dann ein Token mit der Dienst-URL als Audience; lokal nimmt sie dein User-Token. Im Pickle landet kein Token (`tests/test_agent.py`).
* **`header_provider` nur mit Agent-Kontext:** Ein `get_tools()` außerhalb eines Agents schickt kein Token (Cloud Run: 403). `scripts/check_mcp.py` gibt den Header deshalb direkt mit.
* **`timeout=30`**: Platz für einen Kaltstart von Cloud Run (Standard 5 s).
* **Deploy mit `extra_packages=["bq_analyst"]`**: Der Code wird als Paket mitgeschickt und per Referenz gepickelt; die Requirements nennen genau die Versionen aus `.venv`, inklusive `mcp` (bringt `google-adk` nicht mit).

## Aufräumen

```bash
uv run python -c "import vertexai,os; from dotenv import load_dotenv; load_dotenv(); vertexai.Client(project=os.environ['GOOGLE_CLOUD_PROJECT'], location=os.environ['REGION']).agent_engines.delete(name=os.environ['AGENT_ENGINE_NAME'], force=True)"
gcloud storage rm -r gs://deltorobarba-agent-staging/bq_mcp_analyst_project
```

Server, Registry-Eintrag und IAM teilt sich das Projekt mit `../mcp.ipynb`; die bleiben stehen, solange das Notebook sie nutzt.

## Hinweise

* **iCloud:** Der Ordner liegt in iCloud Drive. Die Umgebung liegt deshalb in `.venv.nosync` (iCloud synchronisiert Ordner mit der Endung `.nosync` nicht), `.venv` ist ein Verweis darauf. Nach einem frischen Klonen: `mkdir .venv.nosync && ln -s .venv.nosync .venv && uv sync`.
* **Git:** Unterordner von `gcp/` stehen nicht auf der Whitelist in `../../.git/info/exclude`; dieses Projekt bleibt lokal. Vor einer Veröffentlichung müssten `.env`, `.venv` und `.venv.nosync` ausgeschlossen bleiben.
