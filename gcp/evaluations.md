# Evaluation von LLMs und Agents

Stand: 2026-11-02. Diese Notiz sammelt die wichtigsten öffentlichen Vergleichsseiten (Leaderboards) für Sprachmodelle
und Agents, erklärt, wie man ihre Zahlen liest, und wie man selbst evaluiert. Die Zahlen stehen gesammelt in Abschnitt 5
als datierte Momentaufnahme; alles andere ändert sich langsam.

1. [Leaderboards richtig lesen](#1-leaderboards-richtig-lesen)
2. [Landkarte der Vergleichsseiten](#2-landkarte-der-vergleichsseiten)
3. [Welche Seite für welche Frage?](#3-welche-seite-für-welche-frage)
4. [Eigene Evaluation](#4-eigene-evaluation)
5. [Momentaufnahme (Stand 2026-11-02)](#5-momentaufnahme-stand-2026-11-02)
6. [Quellen](#6-quellen)
7. [Notiz: Auf dem Stand bleiben, wenn neue Modelle erscheinen](#notiz-auf-dem-stand-bleiben-wenn-neue-modelle-erscheinen)

---

## 1. Leaderboards richtig lesen

### 1.1 Agent = Modell + Harness

Das **Modell** ist das trainierte Netz: Es sagt Tokens vorher und denkt (Reasoning). Der **Harness** (das Gerüst um
das Modell) ist alles, was das Modell steuert und mit der Außenwelt verbindet.

```
Agent  =  Modell                          +  Harness
          Gewichte: Token-Vorhersage,        Systemprompt, nachgeladene Anweisungen (AGENTS.md, Skills),
          Reasoning                          Tools und MCP-Server, Kontext-Kompaktierung, Retries,
                                             Ausgabe-Parser, Sandbox, Guardrails
```

Dasselbe Modell erreicht in verschiedenen Harnesses sehr unterschiedliche Werte. Herstellerangaben mit eigenem
Scaffold sind deshalb nicht mit einem Leaderboard vergleichbar, das alle Modelle im selben Harness laufen lässt (z. B.
SWE-bench Pro bei Scale, wo alle Modelle mit mini-swe-agent laufen).

### 1.2 Vier Ebenen der Evaluation

| Ebene | Was fest, was variabel | Beispiele |
| --- | --- | --- |
| 1. Modell isoliert | ein Prompt → eine Antwort, ohne Tools und ohne Schleife | HLE, MathArena, LiveBench, GPQA |
| 2. Modell im festen Harness | Harness fest, Modell wechselt | SWE-bench Pro (SEAL), SWE-rebench, τ-Bench, MCP-Atlas, HAL |
| 3. Harness-Ablation | Modell fest, genau ein Bauteil des Harness wechselt (Systemprompt, Tool-Schema, Skill) | kein öffentliches Leaderboard; Arbeit am eigenen Agent |
| 4. Agent Ende-zu-Ende | der ganze Ablauf: Planung, Tool-Aufrufe (Trajektorie), Belegtreue (Grounding), Endzustand der Umgebung | Terminal-Bench, OSWorld, eigene Agent-Evals |

Ebene 1 sagt wenig über Agents. Ein Modell mit Bestnoten im Einzel-Prompt kann in einem Ablauf mit 25 Schritten
scheitern, weil es Tool-Parameter falsch füllt, nach einem Fehler weiterrät oder Dateien am falschen Ort ändert.

**Merksatz:** Sobald Tools im Spiel sind, ist es technisch immer eine Agent-Evaluation. Ob daraus eine Modell- oder
eine Harness-Evaluation wird, entscheidet, welchen Regler man festhält und welchen man dreht.

### 1.3 Fünf Fragen an jede Zahl

**1. Wird das Modell gerankt oder Modell plus Harness?** Herstellerangaben nutzen oft ein eigenes Scaffold, mehr
Versuche oder ein höheres Thinking-Level. Vergleichbar sind nur Werte aus demselben Harness.

**2. pass@1, pass@k oder pass^k?** Agents arbeiten zufällig, ein Lauf pro Aufgabe sagt wenig. Läuft jede Aufgabe
n-mal und gelingen c Läufe (Erfolgsquote p = c/n), gibt es zwei verschiedene Fragen:

- `pass@k`: Gelingt **mindestens einer** von k Versuchen? Das misst, was das System grundsätzlich kann, z. B. wenn man
  mehrere Patches erzeugt und per Test den besten auswählt. Näherung `pass@k ≈ 1 − (1 − p)^k`; unverzerrter Schätzer
  `1 − C(n−c, k) / C(n, k)` (aus dem Codex-Paper).
- `pass^k`: Gelingen **alle** k Versuche? Das misst die Verlässlichkeit im Betrieb, wo jeder einzelne Lauf sitzen muss.
  Näherung `pass^k ≈ p^k`; Schätzer `C(c, k) / C(n, k)` (eingeführt mit τ-Bench).

Beispiel mit p = 0,75 und k = 3:

- `pass@3 = 1 − 0,25³ = 0,984`, also 98,4 %: Fast jede Aufgabe ist für das System lösbar.
- `pass^3 = 0,75³ = 0,422`, also 42,2 %: In mehr als der Hälfte der Dreierserien scheitert mindestens ein Lauf.

Für Forschung und Best-of-n zählt pass@k, für Agents in Produktion pass^k.

**3. Was kostet es?** Kosten, Latenz und Schrittzahl nur über die **erfolgreichen** Läufe vergleichen (Kosten pro
gelöster Aufgabe). Sonst wirkt ein Agent billig und schnell, der nach einer Sekunde aufgibt. Ein höheres
Thinking-Level lohnt sich nicht immer; die Kosten-Leistungs-Grafik (Pareto-Front) zeigt, wo es sich lohnt.

**4. Ist der Unterschied größer als das Rauschen?** Der Standardfehler einer Erfolgsquote p aus n Aufgaben ist
`√(p·(1−p)/n)`, das 95-%-Intervall reicht etwa ±1,96 Standardfehler um den Wert (Pp = Prozentpunkte):

| Aufgaben n | Erfolgsquote p | Standardfehler | 95-%-Intervall |
| --- | --- | --- | --- |
| 10 | 0,8 | 12,6 Pp | ±24,8 Pp |
| 50 | 0,7 | 6,5 Pp | ±12,7 Pp |
| 500 | 0,7 | 2,0 Pp | ±4,0 Pp |

Zum Nachrechnen: HLE hat 2.500 Fragen. Bei 54,8 % ergibt das ±1,96·√(0,548·0,452/2500) = ±1,95 Pp, praktisch das
±1,94, das auf dem Leaderboard steht. Ränge mit überlappenden Intervallen sind ein Gleichstand. Dazu kommt Rauschen aus
der Infrastruktur: Zu knappe Timeouts, Speichergrenzen von Containern oder Rate Limits drücken Werte um einige
Prozentpunkte, und ein abgestürzter Container sieht im Report aus wie ein Fehler des Modells.

**5. Ist der Benchmark kontaminiert oder gesättigt?** Kontaminiert heißt: Aufgaben oder Lösungen standen in den
Trainingsdaten (Beispiel SWE-bench Verified). Gesättigt heißt: Die Spitze liegt so nah an 100 % oder am menschlichen
Wert, dass Unterschiede nichts mehr bedeuten (MMLU, GPQA Diamond, AIME). Gegenmittel sind Aufgaben, die erst nach dem
Trainingsende entstanden (LiveBench, SWE-rebench, MathArena, LiveCodeBench), und private Testsets.

---

## 2. Landkarte der Vergleichsseiten

Was jede Seite misst, wofür sie taugt und wo ihre Grenzen liegen. Zahlen stehen absichtlich nicht hier, sondern in
Abschnitt 5.

### 2.1 Menschliche Präferenz und Alltagsqualität

**Arena** (früher LMArena bzw. LMSYS Chatbot Arena) – https://arena.ai/leaderboard
- **Wofür:** Nutzer vergleichen blind zwei Antworten; daraus entsteht ein Rating nach Bradley-Terry (ähnlich Elo). Das
  Projekt hieß zuerst Chatbot Arena, nach der Ausgründung LMArena und seit Januar 2026 nur noch „Arena“.
- **Stärken:** große Datenbasis, schwer gezielt zu manipulieren, viele Unterboards: Text, WebDev (Code Arena), Agent,
  Vision, Dokumente, Suche, Bild und Video. Für Geschmack beim Coding ist das WebDev-Board nützlich.
- **Schwächen:** misst Stil, Formatierung und gefühlte Hilfsbereitschaft, kaum fachliche Korrektheit. Bei den
  Spitzenmodellen überlappen die Konfidenzintervalle stark. Neue Modelle sind anfangs als „vorläufig“ markiert, bis
  genug Stimmen da sind.

### 2.2 Reasoning und Wissen, kontaminationsresistent

**LiveBench** – https://livebench.ai
- **Wofür:** monatlich erneuerte Aufgaben (Mathematik, Code, Datenanalyse, Instruction Following), objektiv bewertet
  ohne LLM-Richter.
- **Stärken:** geringe Kontamination, breit aufgestellt.
- **Schwächen:** Die Aufgaben sind eher kurz und testen kaum agentisches Arbeiten. An der Spitze wird es zunehmend eng.

**Humanity's Last Exam (HLE)** – https://lastexam.ai · Leaderboard: https://labs.scale.com/leaderboard/humanitys_last_exam
- **Wofür:** 2.500 Fragen auf Expertenniveau aus über 100 Fachgebieten, entwickelt von Scale AI und CAIS.
- **Stärken:** noch trennscharf. Das Leaderboard zeigt auch den Kalibrierungsfehler, also wie gut ein Modell seine
  eigene Unsicherheit einschätzt.
- **Schwächen:** geschlossene Fragen mit fester Antwort, kein offenes Forschen. Manche Antworten im Datensatz sind
  umstritten. Seit 2026-09-17 gibt es zusätzlich HLE-Rolling, eine laufend erneuerte Abspaltung, und der
  Artificial-Analysis-Index nutzt eine Variante „HLE-Diamond“; Werte verschiedener Varianten nicht mischen.

**GPQA Diamond** – ⚠️ *Legacy*
- Artificial Analysis führt GPQA Diamond nur noch unter „Legacy Evaluations“, weil Frontier-Modelle den Test praktisch
  gelöst haben. GPQA gehört damit in dieselbe Schublade wie MMLU.

**ARC Prize (ARC-AGI-1/2/3)** – https://arcprize.org/leaderboard
- **Wofür:** fluide Intelligenz bei neuartigen Mustern. ARC-AGI-3 ist interaktiv: Agents müssen sich spontan an
  unbekannte Umgebungen anpassen, statt statische Gitterrätsel zu lösen.
- **Stärken:** zeigt Kosten pro Aufgabe, hat einen menschlichen Vergleichswert und lässt sich kaum auswendig lernen.
- **Schwächen:** Bei ARC-AGI-3 zählt die quadrierte Effizienz im Vergleich zu Menschen, nicht der Anteil gelöster
  Aufgaben. Die Werte sind deshalb nicht mit v1/v2 vergleichbar. Außerdem schwanken sie stark je nach Scaffolding.

### 2.3 Mathematik und Naturwissenschaft

**Epoch AI Benchmarking Hub** (mit FrontierMath und dem Epoch Capabilities Index) – https://epoch.ai/benchmarks ·
https://epoch.ai/eci
- **Wofür:** bündelt Ergebnisse vieler aussagekräftiger Benchmarks, teils von Epoch selbst gemessen, teils aus
  seriösen externen Quellen, in einer einheitlichen, durchsuchbaren Datenbank. FrontierMath enthält
  Forschungsmathematik in Tiers 1–4. Der **Epoch Capabilities Index (ECI)** fasst viele Benchmarks auf einer Skala
  zusammen (Claude 3.5 Sonnet = 130, GPT-5 = 150), mit Konfidenzintervall.
- **Stärken:** unabhängig, mit Trendanalysen. Die Rohdaten gibt es zum Download (der ECI z. B. als CSV), gut für
  eigene Auswertungen.
- **Schwächen:** Epoch hat offengelegt, dass OpenAI FrontierMath finanziert hat und Zugriff auf einen Großteil der
  Aufgaben und Lösungen hatte. Interessenkonflikt beachten.

**MathArena** (ETH Zürich) – https://matharena.ai
- **Wofür:** bewertet Modelle an Wettbewerbsaufgaben, die erst nach dem Trainingsende des jeweiligen Modells
  veröffentlicht wurden. Dazu kommen Beweisbewertung (z. B. USAMO) und ArXivMath, ein Final-Answer-Benchmark für
  Mathematik auf Forschungsniveau.
- **Stärken:** praktisch kontaminationsfrei, prüft auch das Schreiben von Beweisen. Die vollständigen Reasoning-Traces
  liegen auf Hugging Face.
- **Schwächen:** Die klassischen Final-Answer-Wettbewerbe (AIME) sind ausgereizt. Interessant sind nur noch die
  schwereren Boards.

**CritPt** (Teil des Artificial-Analysis-Index, seit v5.0 als „CritPt v2 (Hard Subset)“)
- Physik-Reasoning auf Forschungsniveau. Lohnt sich als Einzelwert für physiknahe Anwendungen, z. B. Quantendynamik.

### 2.4 Coding-Agenten

**SWE-bench (Verified / Pro)** – https://www.swebench.com · Pro: https://labs.scale.com/leaderboard/swe_bench_pro_public
- **Wofür:** echte GitHub-Issues in kompletten Repos lösen.
- **Stärken:** Pro ist mehrsprachig (Python, Go, TypeScript, JavaScript). Das SEAL-Board von Scale lässt alle Modelle
  im selben Scaffold (mini-swe-agent) laufen und ist damit fair vergleichbar.
- **Schwächen:** Verified gilt als kontaminiert, und bei vielen der schwersten ungelösten Aufgaben waren die Testfälle
  fehlerhaft. Laut Sekundärquellen berichtet OpenAI Verified deshalb nicht mehr und empfiehlt Pro. Herstellerangaben
  mit eigenem Scaffold sind nicht mit SEAL vergleichbar.

**SWE-rebench** (Nebius) – https://swe-rebench.com
- **Wofür:** Coding-Agents auf Aufgaben aus frischen GitHub-Pull-Requests. Bewertet wird nur ein aktuelles
  Zeitfenster, laufend um neue Aufgaben ergänzt.
- **Stärken:** Alle Modelle laufen im selben Scaffold, und die Aufgaben sind jünger als das Trainingsende vieler
  Modelle; damit ist es das Gegenstück zum kontaminierten SWE-bench Verified. Werte mit Fehlerangabe.
- **Schwächen:** Python-lastig und kleines Zeitfenster (Stand 2026-11: 111 Aufgaben aus 65 Repos), daher große
  Unsicherheit. Wird nicht immer zeitnah aktualisiert (letzter Eintrag 2026-07-01).

**Terminal-Bench** – https://www.tbench.ai
- **Wofür:** prüft, ob ein Agent in einem echten Terminal arbeiten kann, statt nur Patches zu erzeugen.
- **Stärken:** realistische Aufgaben aus DevOps, Systemadministration und wissenschaftlichem Rechnen in Docker; zeigt
  auch Kosten und Tokens.
- **Schwächen:** Gerankt wird die Kombination aus Agent-Harness und Modell, nicht das Modell allein. Bei den Top 10
  überlappen die Konfidenzintervalle stark. Hauptversionen (2.x, 3.0, 4.0) nicht miteinander vergleichen.

**Aider Polyglot** – https://aider.chat/docs/leaderboards/
- **Wofür:** Code-Editing in mehreren Sprachen im Aider-Workflow.
- **Stärken:** praxisnah für Pair Programming, mit Kostenangaben.
- **Schwächen:** an einen bestimmten Tool-Workflow gebunden. Die Spitze ist relativ eng.

**LiveCodeBench** – https://livecodebench.github.io
- **Wofür:** Programmieraufgaben aus Wettbewerben (LeetCode, AtCoder, Codeforces) mit Veröffentlichungsdatum; man
  wertet nur Aufgaben aus, die nach dem Trainingsende eines Modells erschienen sind.
- **Stärken:** kontaminationsarm durch das Zeitfenster.
- **Schwächen:** kurze, abgeschlossene Aufgaben ohne Repo-Kontext; sagt wenig über Agents.

### 2.5 Tool-Nutzung, MCP und Kundenagenten

**Berkeley Function-Calling Leaderboard (BFCL)** – https://gorilla.cs.berkeley.edu/leaderboard.html
- **Wofür:** zuverlässige Tool- und API-Aufrufe mit korrekten Parametern, auch mehrstufig.
- **Stärken:** direkt relevant für Agents, die APIs aufrufen.
- **Schwächen:** testet die Korrektheit einzelner Aufrufe, nicht die Qualität ganzer Abläufe. Dafür τ-Bench und
  MCP-Atlas.

**τ-Bench (τ², τ³)** (Sierra) – https://taubench.com
- **Wofür:** Agents im Kundendienst. Das Modell spricht mit einem simulierten Nutzer, ruft Tools (APIs einer Airline,
  eines Händlers, eines Telekom-Anbieters, einer Bank) und muss dabei Regeln (Policies) einhalten. Bewertet wird der
  Endzustand der Datenbank. τ³ ergänzt Banking mit Wissensabruf und Voice.
- **Stärken:** misst Verlässlichkeit über Wiederholungen (pass^k) und Regeltreue, nicht nur einzelne Tool-Aufrufe.
- **Schwächen:** Der simulierte Nutzer ist selbst ein LLM und bringt Rauschen hinein. Domänen wurden nachträglich
  korrigiert (Retail und Airline im Februar 2026); Werte vor und nach einer Korrektur nicht vergleichen.

**MCP-Atlas** (Scale) – https://labs.scale.com/leaderboard/mcp_atlas
- **Wofür:** Tool-Nutzung über echte MCP-Server: 36 Server, 220 Tools, 1.000 Aufgaben (500 öffentlich, 500 privat).
  Das Modell muss passende Tools finden, über mehrere Server hinweg kombinieren und aus den Ergebnissen antworten.
- **Stärken:** näher an echten Agent-Anwendungen als BFCL; die Hälfte der Aufgaben ist privat.
- **Schwächen:** Bewertung durch einen LLM-Judge. Im April 2026 wurde die Methodik geändert (neuer Judge, Retry bei
  vorübergehenden Tool-Fehlern, Budget von 100 Tool-Aufrufen statt 20 Runden) und alles neu bewertet; ältere Werte
  sind nicht vergleichbar.

### 2.6 Computer Use und Web-Recherche

**OSWorld (Verified, 2.0)** – https://os-world.github.io
- **Wofür:** Computer Use: Ein Agent bedient echte Programme in einer virtuellen Maschine über Bildschirm, Maus und
  Tastatur (369 Aufgaben im Original).
- **Stärken:** prüft den Endzustand per Skript und hat einen menschlichen Vergleichswert (72,36 % im Original-Paper).
- **Schwächen:** Laut Sekundärquellen liegt die Spitze bei OSWorld-Verified inzwischen über dem menschlichen Wert, der
  Test ist also fast gesättigt. Seit 2026-06-26 gibt es OSWorld 2.0, nicht mit Verified vergleichbar. Ergebnisse
  hängen stark vom Schrittlimit ab (z. B. 100 Schritte).

**BrowseComp / BrowseComp-Plus** – https://openai.com/index/browsecomp/ · Plus: https://tevatron-browsecomp-plus.hf.space
- **Wofür:** Recherche-Agents: schwer auffindbare Fakten im offenen Web finden (1.266 Fragen mit kurzen, prüfbaren
  Antworten).
- **Stärken:** Antworten sind leicht zu prüfen, aber schwer zu finden.
- **Schwächen:** Ergebnisse hängen stark von Suchwerkzeug und Produkt ab; viele Spitzenwerte stammen von Produkten,
  nicht von offenen Harnesses. Die Spitze liegt laut Sekundärquellen um 90 %. BrowseComp-Plus nutzt einen festen
  Dokumentkorpus und erlaubt so faire Vergleiche von Modell und Retriever.

### 2.7 Agents in realer Wissensarbeit

**SemiAnalysis GDPx** – https://gdpx.semianalysis.com
- **Wofür:** misst allgemeine agentische Fähigkeiten in 11 wirtschaftlich wertvollen Domänen, gebaut mit
  spezialisierten Partnern, mit Live-Leaderboard, Ergebnissen pro Domäne und Kosten pro Aufgabe. Aktuell 206 Aufgaben
  von 14 Partnern, darunter Chip-Design, Cybersecurity, Biologie, Quant-Trading, Materialwissenschaft und Recursive
  Self-Improvement.
- **Stärken:** sehr hohe Messlatte (die Spitze liegt bei rund 12 %). Es gibt eine Pareto-Grafik für Kosten und
  Leistung, und die Rollouts sind einsehbar.
- **Schwächen:** noch v1.0 mit relativ wenig Aufgaben pro Domäne, daher sind Rankings innerhalb einer Domäne
  statistisch wackelig. Die Aufgaben sind von Partnern kuratiert.

**GDPval** (OpenAI) – https://arxiv.org/abs/2510.04374
- **Wofür:** Aufgaben aus der Arbeit von 44 Berufen; Fachleute vergleichen die Ergebnisse der Modelle blind mit
  Arbeiten von Menschen. Primärquelle hinter GDPval-AA, das in früheren Versionen des Artificial-Analysis-Index steckte.
- **Stärken:** wirtschaftlich relevante Aufgaben mit echten Arbeitsergebnissen (Dokumente, Tabellen, Präsentationen).
- **Schwächen:** Bewertung durch Menschen ist teuer und langsam; der Hersteller misst eigene Modelle mit.

**METR Time Horizons** – https://metr.org/time-horizons
- **Wofür:** die einzige große Metrik in menschlicher Arbeitszeit: die Aufgabenlänge, bei der ein Modell zu 50 %
  erfolgreich ist.
- **Stärken:** anschauliches Maß für den langfristigen Trend.
- **Schwächen:** METR selbst warnt, dass Messungen über 16 Stunden mit der aktuellen Aufgabensammlung unzuverlässig
  sind; die Metrik ist faktisch am Anschlag. Die Seite wird laut eigener Angabe nicht mehr aktiv gepflegt (Stand
  2026-11-02).

**Vals AI** – https://www.vals.ai
- **Wofür:** domänenspezifische Benchmarks für Legal, Finance, Medizin und Steuern, dazu Spiegelungen von
  Terminal-Bench und SWE-bench mit Kosten und Latenz.
- **Stärken:** branchennah, gut für Gespräche mit Enterprise-Kunden.
- **Schwächen:** teils private Datensätze, daher weniger reproduzierbar.

**HAL – Holistic Agent Leaderboard** (Princeton) – https://hal.cs.princeton.edu
- **Wofür:** lässt dieselben Agent-Harnesses mit verschiedenen Modellen über viele Benchmarks laufen (Coding, Web,
  Wissenschaft, Kundendienst) und misst dabei auch die Kosten.
- **Stärken:** trennt Modell und Harness am saubersten, zeigt Kosten gegen Genauigkeit, Logs sind einsehbar.
- **Schwächen:** hinkt neuen Modellen hinterher, weil die eigenen Läufe teuer sind.

### 2.8 Faktentreue und Halluzination

**FACTS** (Google DeepMind, Google Research, Google Cloud und Kaggle) – https://www.kaggle.com/benchmarks/google/facts
- **Wofür:** Faktentreue in vier Teilen: Grounding (Antwort nur aus einem gegebenen Dokument), Parametric (Wissen ohne
  Hilfsmittel), Search (mit Websuche) und Multimodal (Bilder). Der Gesamtwert ist das Mittel der vier.
- **Stärken:** Grounding ist direkt relevant für RAG; Kaggle hält private Testsets zurück und wertet selbst aus.
- **Schwächen:** Bewertung durch LLM-Judges. Von Google mitentwickelt, also Interessenkonflikt beachten (wie bei
  FrontierMath und OpenAI).

Ergänzend: **AA-Omniscience** im Artificial-Analysis-Index misst Wissen und Halluzinationsneigung; falsche Antworten
kosten Punkte, Enthaltung nicht.

### 2.9 ML-Forschung und ML-Engineering

**MLE-bench** (OpenAI) – https://github.com/openai/mle-bench
- 75 Kaggle-Wettbewerbe: Der Agent muss Daten aufbereiten, Modelle trainieren und eine Einreichung erzeugen; gezählt
  werden Medaillen wie bei Kaggle.

**PaperBench** (OpenAI) – https://github.com/openai/preparedness
- 20 Paper der ICML 2024 von Grund auf nachbauen (Code schreiben, Experimente laufen lassen), bewertet mit
  detaillierten Rubriken.

### 2.10 Produktion: Preis, Geschwindigkeit, Meta-Indizes

**Artificial Analysis** – https://artificialanalysis.ai
- **Wofür:** Intelligence Index plus unabhängige Messungen zu Preis, Tokens pro Sekunde und Time to First Token pro
  Anbieter.
- **Stärken:** Der Index fasst eine Handvoll Evaluationen zusammen, ein großer Teil davon private, zurückgehaltene
  Testsets (Zusammensetzung der aktuellen Version in Abschnitt 5). Zusätzlich gibt es Ansichten zu Token-Effizienz
  und Kosten pro Aufgabe.
- **Schwächen:** häufige Versionswechsel (zuletzt v4.2 → v5.0) machen Zeitreihen schwierig. Der aggregierte Wert
  verdeckt Spezialstärken.

**BenchLM** – https://benchlm.ai
- **Wofür:** aggregiert Dutzende Benchmarks mit Kategoriegewichtung und kennzeichnet, welche Benchmarks in den
  Gesamtwert einfließen und welche nur zur Information angezeigt werden.
- **Stärken:** ein Ort für viele Einzel-Leaderboards, mit Datum pro Snapshot.
- **Schwächen:** spiegelt Fremddaten nur, daher mit Verzögerung. Die Gewichtung ist eine redaktionelle Entscheidung.

**Stanford HELM** – https://crfm.stanford.edu/helm/
- **Wofür:** akademischer Standard für transparente, reproduzierbare Evaluation, auch zu Sicherheit, Bias und
  Robustheit.
- **Stärken:** volle Offenlegung von Prompts und Outputs.
- **Schwächen:** hinkt den neuesten Frontier-Releases oft hinterher.

**OpenRouter Rankings** – https://openrouter.ai/rankings
- **Wofür:** welche Modelle Entwickler tatsächlich nutzen, gemessen am Token-Volumen.
- **Stärken:** zeigt echte Adoption statt Benchmark-Werte.
- **Schwächen:** verzerrt durch Preise und die Nutzerbasis von OpenRouter. Sagt nichts über Qualität aus.

**MTEB** (Embeddings) – https://huggingface.co/spaces/mteb/leaderboard
- **Wofür:** Embedding-Modelle für Retrieval, Clustering und RAG.
- **Stärken:** Standard für die Wahl von RAG-Komponenten.
- **Schwächen:** Ergebnisse übertragen sich nur begrenzt auf domänenspezifische Korpora. Eigene Evaluation bleibt
  Pflicht.

---

## 3. Welche Seite für welche Frage?

| Frage | Erste Anlaufstelle |
| --- | --- |
| Welches Modell fühlt sich im Chat am besten an? | Arena |
| Was kann die Frontier wirklich, über Domänen hinweg? | GDPx, Artificial Analysis, Epoch (ECI) |
| Wie gut ist das Modell in Mathematik und Physik? | MathArena (ArXivMath), FrontierMath, CritPt |
| Welches Modell für Coding-Agents? | SWE-bench Pro (SEAL), SWE-rebench, Terminal-Bench, Arena WebDev |
| Welches Modell für Tool-Calling, MCP oder Kundenagenten? | BFCL, τ-Bench, MCP-Atlas |
| Welches Modell für Computer Use und Web-Recherche? | OSWorld, BrowseComp (Plus) |
| Wie zuverlässig bei Fakten, wie gut für RAG? | FACTS (Grounding), AA-Omniscience, MTEB für Embeddings |
| Was bringt das Modell, was der Harness? | HAL, eigene Evaluation (Abschnitt 4) |
| Was kostet es, und wie schnell ist es in Produktion? | Artificial Analysis |
| Wie entwickelt sich der langfristige Trend? | Epoch (ECI), METR |
| Taugt es für meinen Anwendungsfall? | nur die eigene Evaluation |

**Faustregel:** Möglichst die Primärquelle nutzen statt Aggregator-Spiegel. Und immer prüfen, ob gerade das Modell oder
die Kombination aus Modell und Harness gerankt wird.

---

## 4. Eigene Evaluation

Leaderboards beantworten, wie gut ein Modell im Allgemeinen ist. Ob es für den eigenen Fall taugt, zeigt nur eine
Evaluation mit eigenem Harness und eigenen Aufgaben (Ebenen 2 bis 4 aus Abschnitt 1.2).

### 4.1 Bewerten in drei Stufen

1. **Deterministisch zuerst.** Wann immer möglich das Ergebnis prüfen, nicht den Weg dorthin: Laufen die Unit-Tests
   grün? Ist das JSON oder SQL gültig? Steht der richtige Datensatz in der Datenbank? Wurde kein verbotener Endpunkt
   aufgerufen? Solche Prüfungen sind kostenlos, schnell, reproduzierbar und bestrafen den Agent nicht, wenn er einen
   klügeren Weg findet als erwartet.
2. **Tool-Trajektorie.** Für Abläufe mit Pflichtschritten die Folge der Tool-Aufrufe prüfen. In ADK macht das
   `tool_trajectory_avg_score` mit drei Modi:
   - `EXACT` (Standard): genau diese Aufrufe in genau dieser Reihenfolge, nichts dazu. Passt für Pflichtprotokolle wie
     Vorschau → Freigabe durch einen Menschen → Löschen.
   - `IN_ORDER`: die erwarteten Aufrufe in dieser Reihenfolge, dazwischen sind weitere erlaubt (z. B. zusätzliches
     Suchen und Lesen). Der beste Standard für reale Abläufe.
   - `ANY_ORDER`: alle erwarteten Aufrufe, Reihenfolge egal. Passt für parallele Informationssuche.
3. **LLM-Judge mit Rubriken.** Wo Sprache, Vollständigkeit oder Belegtreue zu bewerten sind: keine vage Skala von 1 bis
   5, sondern einzelne Ja/Nein-Fragen („Enthält die Antwort die Bestellnummer aus dem Tool-Ergebnis?“). Pflicht- und
   Sicherheitskriterien nicht mitteln, sondern als Gate multiplizieren:
   `Gesamtwert = (g₁ · g₂ · …) × (w₁·r₁ + w₂·r₂ + …)` mit Gates gₘ ∈ {0, 1} und Rubriken rᵢ ∈ {0, 1}. Eine
   Sicherheitsverletzung setzt den Wert so auf 0, statt im Durchschnitt unterzugehen.

### 4.2 Den Judge kalibrieren

Beispiel: Ein Agent ist in 95 % der Fälle korrekt. Ein fauler Judge, der immer PASS sagt, hat dann 95 % Accuracy,
übersieht aber jeden einzelnen Fehler. Deshalb prüft man einen Judge an 50 bis 100 von Hand bewerteten Fällen (getrennt
in einen Teil zum Entwickeln und einen zurückgehaltenen Teil) mit drei Kennzahlen:

- **TPR** (Sensitivität) = TP / (TP + FN): Welchen Anteil der wirklich guten Läufe erkennt der Judge als PASS?
- **TNR** (Spezifität) = TN / (TN + FP): Welchen Anteil der fehlerhaften Läufe erkennt er als FAIL? Für Sicherheits-
  und Regressionstests die wichtigste Zahl.
- **Cohens κ** = (pₒ − pₑ) / (1 − pₑ): Übereinstimmung mit dem Menschen, bereinigt um Zufallstreffer (pₒ = beobachtete,
  pₑ = zufällig erwartete Übereinstimmung). Im Beispiel: pₒ = 0,95 und pₑ = 0,95·1 + 0,05·0 = 0,95, also κ = 0. Die
  95 % Accuracy sind wertlos. Faustregel: ab κ ≈ 0,6 brauchbar, ab 0,8 gut.

Jeder Judge-Prompt sollte drei Ausgänge haben: `PASS wenn …`, `FAIL wenn …` und `INSUFFICIENT`, wenn die Belege für ein
Urteil fehlen.

### 4.3 Angewendet auf models.ipynb

In [models.ipynb](models.ipynb) vergleichen die Zellen „Model Benchmark“ (Geschwindigkeit und LLM-as-a-Judge) und
„Model Evaluation“ (Gen AI Evaluation Service mit der Rubrik `GENERAL_QUALITY`) Gemini 3.8 Flash mit DeepSeek V4.1
Flash auf 10 Prompts mit je einem Lauf. Was sich daraus ableitet:

- **Zwei Prompts haben eine feste Antwort** und brauchen keinen Judge:
  - Zug-Aufgabe: Um 10:00 Uhr ist Zug A schon 60 Meilen gefahren, es fehlen noch 220 Meilen. Die Züge nähern sich mit
    60 + 80 = 140 mph, also dauert es 220 / 140 = 1,571 h ≈ 94 Minuten. Treffpunkt etwa **11:34 Uhr**.
  - Fibonacci-Debugging: Der Term `fibonacci(n-3)` ist zu viel, richtig ist `fibonacci(n-1) + fibonacci(n-2)`; dazu
    kommt die exponentielle Laufzeit ohne Memoization.

  Beide lassen sich deterministisch prüfen (Uhrzeit per Regex, Code per Unit-Test).
- **10 Prompts mit je einem Lauf erkennen nur große Unterschiede** (95-%-Intervall etwa ±25 Pp, Tabelle in 1.3). Besser
  sind mehr Prompts und 3 bis 5 Läufe pro Prompt; dann lassen sich auch pass^k und die Streuung angeben.
- **Den Judge vorher prüfen** (4.2), an einer kleinen, von Hand bewerteten Stichprobe.
- **Latenz und Kosten** nur über bestandene Antworten vergleichen.

Doku: [Gen AI Evaluation Service](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/evaluation-overview),
[ADK Evaluation](https://adk.dev/evaluate/) und [ADK-Kriterien](https://adk.dev/evaluate/criteria/).

---

## 5. Momentaufnahme (Stand 2026-11-02)

Am 2026-11-02 an der jeweiligen Primärseite abgelesen, außer wo „Sekundärquelle“ steht. Das ± steht so auf der Seite.
Nur dieser Abschnitt muss bei neuen Modellen aktualisiert werden.

| Board | Spitze | Wert | Dahinter / Hinweis |
| --- | --- | --- | --- |
| Arena Text | Gemini 4 Carbon (High) | 1528 ± 9 (vorläufig) | Gemini 4 Argon (High) 1520 ± 6, Claude Opus 5.5 (High) 1509 ± 7; Seite datiert 2026-10-27 |
| Arena Agent | Claude Opus 5.5 (Max) | 20,94 % | |
| Epoch ECI | GPT-6 Astra | 169,1 (KI 165,9–174,3) | Claude Opus 5.5 168,4, GPT-6.1 Terra 168,1; Intervalle überlappen, also Gleichstand. CSV vom 2026-11-02 |
| Artificial Analysis | Index v5.0 | – | 9 Evaluationen: AA-Briefcase v1.1, AutomationBench-AA, GDP.pdf, FrontierCode 2.0, Terminal-Bench 4.0, AA-Omniscience v1.1, HLE-Diamond, CritPt v2 (Hard Subset), Terminal-Bench-Science 0.1.0; 60 % der Gewichtung privat; Rangliste nicht abgelesen |
| HLE | GPT 6 Astra | 54,80 ± 1,94 % | Fable 5.1 (xhigh) 46,50 %, gemini-3.1-pro-preview (thinking high) 46,44 % |
| GDPx v1.0 | Claude Opus 5.5 | 12,0 % | Gemini 4 Carbon 10,9 %, GPT-6 Astra 9,6 % |
| SWE-bench Pro (SEAL, public) | Muse Spark 1.1 | 61,50 ± 3,10 % | gpt-5.4 (xHigh) 59,10 %; alle mit mini-swe-agent |
| SWE-rebench | Fable 5 [high] | 64,5 ± 1,41 % | Grok 4.5 [high] 63,8 %, Opus 5 [high] 63,4 %; Fenster 2026-05-15 bis 2026-07-01, seit Juli nicht aktualisiert |
| τ³-Banking (Text) | Qwen 3.8 Max | 55,2 % (pass^1) | Claude Opus 5 48,7 %, Grok 4.5x 47,9 % |
| MCP-Atlas | Muse Spark 1.1 | 88,10 ± 1,95 % | Fable 5.1 87,20 %, claude-opus-5 (xhigh) 85,80 % |
| Terminal-Bench | – | – | Leaderboard zeigt Version 4.0; Tabelle lädt dynamisch, nicht abgelesen |
| METR | – | – | Seite laut eigener Angabe nicht mehr aktiv gepflegt; Spitzenwert laut Sekundärquelle etwa 17,4 h (Claude Mythos Preview, Mai 2026) |
| OSWorld-Verified | – | – | Tabelle lädt dynamisch; laut Sekundärquellen Spitze um 85–86 % (Mensch 72,36 %). OSWorld 2.0 seit 2026-06-26 |
| BrowseComp | – | um 92 % | Sekundärquelle (BenchLM, 2026-10-29) |

---

## 6. Quellen

Primärquellen (Leaderboards, Methodik, Paper):

- Arena: https://arena.ai/leaderboard
- LiveBench: https://livebench.ai
- Humanity's Last Exam: https://lastexam.ai · Paper https://arxiv.org/abs/2501.14249 · Leaderboard https://labs.scale.com/leaderboard/humanitys_last_exam
- ARC Prize: https://arcprize.org/leaderboard · ARC-AGI-3 https://arcprize.org/arc-agi/3
- Epoch AI: https://epoch.ai/benchmarks · ECI https://epoch.ai/eci (Daten: https://epoch.ai/data/eci_scores.csv)
- MathArena: https://matharena.ai
- Artificial Analysis, Methodik des Index: https://artificialanalysis.ai/methodology/intelligence-benchmarking
- SWE-bench: https://www.swebench.com · Paper https://arxiv.org/abs/2310.06770
- SWE-bench Pro: https://labs.scale.com/leaderboard/swe_bench_pro_public · Paper https://arxiv.org/abs/2509.16941
- SWE-rebench: https://swe-rebench.com · Paper https://arxiv.org/abs/2505.20411
- Terminal-Bench: https://www.tbench.ai
- LiveCodeBench: https://livecodebench.github.io · Paper https://arxiv.org/abs/2403.07974
- τ-Bench: https://taubench.com · Paper https://arxiv.org/abs/2406.12045 · τ²-Bench https://arxiv.org/abs/2506.07982
- MCP-Atlas: https://labs.scale.com/leaderboard/mcp_atlas · Paper https://arxiv.org/abs/2602.00933
- OSWorld: https://os-world.github.io · Paper https://arxiv.org/abs/2404.07972
- BrowseComp: https://openai.com/index/browsecomp/ · Paper https://arxiv.org/abs/2504.12516 · BrowseComp-Plus https://arxiv.org/abs/2508.06600
- GDPx: https://gdpx.semianalysis.com
- GDPval: https://arxiv.org/abs/2510.04374
- METR: https://metr.org/time-horizons · Paper https://arxiv.org/abs/2503.14499
- HAL: https://hal.cs.princeton.edu
- FACTS: https://www.kaggle.com/benchmarks/google/facts · Paper https://arxiv.org/abs/2512.10791
- MLE-bench: https://arxiv.org/abs/2410.07095 · PaperBench: https://arxiv.org/abs/2504.01848
- pass@k (Codex-Paper): https://arxiv.org/abs/2107.03374

Sekundärquellen, nur für die markierten Werte in Abschnitt 5:

- OSWorld-Stand: https://www.developersdigest.tech/benchmarks/osworld
- BrowseComp-Stand: https://www.benchlm.ai/benchmarks/browsecomp
- METR-Stand: https://futuresearch.ai/app/p/a/frontier-metr-time-horizon-2029
- SWE-bench Pro vs. Verified: https://morphllm.com/swe-bench-pro

---

## Notiz: Auf dem Stand bleiben, wenn neue Modelle erscheinen

Stand 2026-11-02: ein Plan, noch nichts davon eingerichtet. Ob und wie automatisiert wird, ist offen.

### A. Checkliste bei einem neuen Modell

Die Zeitangaben sind eine Einschätzung, nicht gemessen.

1. **Am Tag der Veröffentlichung:** Model Card, System Card oder Tech Report lesen. Notieren: welche Benchmarks, welches
   Scaffold, pass@1 oder pass@k bzw. Best-of-n, welches Thinking-Level, Hinweise zu Kontamination. Herstellerzahlen
   immer mit Quelle festhalten.
2. **In den ersten Tagen:** Artificial Analysis (Index, Preis, Tokens pro Sekunde, Time to First Token), Vals AI, Epoch
   (ECI).
3. **Nach ein bis zwei Wochen:** Arena (braucht erst genug Stimmen, bis dahin „vorläufig“), SWE-bench Pro (SEAL),
   Terminal-Bench, τ-Bench, MCP-Atlas, HLE, GDPx.
4. **Nach Wochen bis Monaten:** METR (falls noch gepflegt), FrontierMath, der nächste Wettbewerb bei MathArena, HAL.
5. **Eigene Evaluation:** die Zellen in [models.ipynb](models.ipynb) mit der neuen Modell-ID laufen lassen (Latenz,
   Model Evaluation). Das ist die Ebene „Modell im festen Harness“ mit dem eigenen Harness.
6. **Abschnitt 5 aktualisieren**, mit Datum. Die alte Fassung bleibt in der Git-Historie.

### B. Automatisieren (später entscheiden)

**Was sich maschinell lesen lässt** (geprüft am 2026-11-02): Der ECI steht als CSV bereit
(`https://epoch.ai/data/eci_scores.csv`). Die Tabellen von HLE, MCP-Atlas und SWE-bench Pro (Scale), SWE-rebench,
τ-Bench, GDPx und Arena Text stehen im HTML und lassen sich als Text abrufen. Nur mit einem Browser lesbar, weil die
Daten dynamisch nachgeladen werden: Terminal-Bench, OSWorld, ARC Prize, METR. Artificial Analysis bietet seine Daten
unter eigenen Nutzungsbedingungen an; vor einer Automatisierung prüfen.

| Stufe | Wie | Aufwand | Vorteil | Nachteil |
| --- | --- | --- | --- | --- |
| 1. Erinnern | monatlicher Kalendereintrag mit Checkliste A; Blogs bzw. Newsletter der wichtigsten Leaderboards abonnieren | Minuten | nichts zu warten | alles manuell |
| 2. Skript nach Zeitplan | Python-Skript liest die ECI-CSV und die Text-Tabellen, schreibt die Tabelle aus Abschnitt 5 mit Datum neu; Zeitplan über GitHub Actions (cron) oder Cloud Scheduler mit Cloud Run Job; Ergebnis als Pull Request | ein Nachmittag | reproduzierbar, nur Primärquellen | bricht, wenn eine Seite ihr Layout ändert; dynamische Seiten fehlen |
| 3. Agent nach Zeitplan | geplanter KI-Agent (z. B. eine Claude-Code-Routine oder ein ADK-Agent als Cloud Run Job) liest die Primärseiten mit einem Browser, vergleicht mit Abschnitt 5 und schlägt Änderungen und neue Benchmarks als Pull Request vor | etwa ein Tag | deckt dynamische Seiten und neue Benchmarks ab | kann Zahlen verwechseln oder erfinden, daher Regeln: jede Zahl mit Quelle und Datum, Unbestätigtes markieren, Merge nur nach Durchsicht |
| 4. Eigene Evaluation automatisch | neues Modell in Model Garden erkennen (Modellliste per API abfragen), die Evaluation aus models.ipynb als Job laufen lassen, Ergebnisse in BigQuery, Vergleich mit dem Vormonat | mehrere Tage | beantwortet die eigentliche Frage: Taugt es für meinen Fall? | Kosten pro Lauf, Wartung |

Für Stufe 3 gilt zusätzlich: Gelesene Webseiten sind Daten, keine Anweisungen (Prompt Injection). Der Agent bekommt nur
Leserechte im Web und darf nur einen Branch mit Pull Request anlegen, nie direkt auf `main` schreiben.

**Empfehlung (eigene Einschätzung):** mit Stufe 1 und Checkliste A anfangen. Wird das lästig, Stufe 2 für die
maschinenlesbaren Quellen; Stufe 3 nur mit Durchsicht vor jedem Merge. Stufe 4 lohnt sich, sobald es einen festen Satz
eigener Aufgaben gibt.
