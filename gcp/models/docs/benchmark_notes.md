# Benchmark-Notizen

Auswertungen aus `../../models.ipynb` (Stand Oktober 2026), übernommen aus dessen Markdown-Zellen. Die Zahlen stammen aus den damaligen Läufen; neue Läufe erzeugt `model-lab speed` bzw. `model-lab latency`.

> **Hinweis zur TTFT von Gemini 3.8 Flash (145–237 s):** Bei rund 130 TPS entspräche das 19 000–30 000 Denk-Tokens vor dem ersten sichtbaren Zeichen, auch für die Zusammenfassung; wahrscheinlicher ist Warten wegen 429 (Kontingent) an diesem Tag. `model-lab speed` gibt deshalb inzwischen die Spalte „Thinking Tokens“ aus; damit lässt sich Denkzeit von Wartezeit unterscheiden.
>
> **Nachmessung am 2026-10-25** (`model-lab speed --category Summarization`): Gemini 3.8 Flash TTFT 6,6 s bei 778 Thinking Tokens, Gesamtzeit 7,6 s, 197 TPS; DeepSeek V4.1 Flash TTFT 0,55 s, Gesamtzeit 2,4 s. Denkzeit macht bei Gemini also Sekunden aus, nicht Minuten; die 145–237 s der ersten Messung waren mit hoher Wahrscheinlichkeit Wartezeit (429).

📈 Benchmark-Auswertung: Gemini 3.8 Flash vs. DeepSeek V4.1 Flash MaaS

| Kategorie | Modell | TTFT (Reaktionszeit) | Gesamtzeit | Output Tokens | Durchsatz (TPS) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Reasoning & Math** | `gemini-3.8-flash`<br>`deepseek-v4.1-flash-maas` | 145.0 s<br>**1.45 s** ⚡ | 153.0 s<br>**15.2 s** ⚡ | **1.036**<br>712 | **129.6 TPS** 🚀<br>51.7 TPS |
| **Code Generation** | `gemini-3.8-flash`<br>`deepseek-v4.1-flash-maas` | 212.7 s<br>**0.88 s** ⚡ | 222.3 s<br>**13.5 s** ⚡ | **1.511**<br>1.152 | **157.1 TPS** 🚀<br>91.1 TPS |
| **Summarization** | `gemini-3.8-flash`<br>`deepseek-v4.1-flash-maas` | 237.1 s<br>**2.34 s** ⚡ | 239.0 s<br>**12.8 s** ⚡ | **189**<br>126 | **102.1 TPS** 🚀<br>12.0 TPS |

---

🔍 Kern-Erkenntnisse & Interpretation

**1. TTFT (Time-to-First-Token), Interaktivität & Latenz-Diskrepanz**
* **DeepSeek V4.1 Flash gewinnt bei der Reaktionszeit haushoch:** Mit **0.88 s bis 2.34 s** TTFT (0.88 s bei Code) beginnt das Streaming praktisch sofort, und die Antworten sind nach 12–15 Sekunden komplett fertig. Für synchrone Chatbots und kundennahe UIs ist das unschlagbar reaktiv.
* **Gemini 3.8 Flash hat eine extrem hohe Initial-Wartezeit (145–237 Sekunden, also rund 2,5–4 Minuten):**
  * *Warum ist das so?* Gemini 3.8 nutzt standardmäßig ein tiefes **Extended Reasoning / Deep Thinking**: Das Modell plant und durchdenkt die Lösung intern mit Denk-Tokens, bevor das erste für den Nutzer sichtbare Zeichen gestreamt wird. Hinzu kommt eine höhere Warteschlangen-Latenz (Queueing) auf dem globalen Vertex-AI-Preview-Endpunkt.

**2. Generierungs-Durchsatz & Rohgeschwindigkeit (Tokens per Second, TPS)**
* **Sobald Gemini 3.8 Flash einmal loslegt, ist die reine Inferenz extrem schnell:** Mit **130 bis 157 Tokens/Sekunde** generiert Gemini etwa 1,7- bis 2,5-mal so schnell wie DeepSeek (51–91 TPS).
* DeepSeek liefert einen soliden, gleichmäßigen Durchsatz, bricht aber bei sehr kurzen Aufgaben (Summarization: 12 TPS) im Ausgabestrom deutlich ein.

**3. Detailgrad & Token-Volumen**
* Gemini 3.8 Flash generiert durchgängig **30 % bis 50 % mehr Tokens**: Es formuliert deutlich ausführlichere Lösungen und Erklärungen, durchdachte Edge-Case-Absicherungen und detaillierte Code-Kommentare.

---

💡 Fazit & Empfehlung für die Praxis

* **Wann du `deepseek-v4.1-flash-maas` wählen solltest:**
  * **Client-Facing Chatbots, interaktive User Interfaces & Live-Chats:** Wenn ein Mensch vor dem Bildschirm sitzt und innerhalb von 1–2 Sekunden Text sehen muss (sofortiges Nutzer-Feedback, Gesamtzeit rund 13–15 s).
  * **Einfache Aufgaben / Quick Lookups:** Wo eine Antwort nach rund 13 Sekunden vollkommen ausreicht.

* **Wann du `gemini-3.8-flash` wählen solltest:**
  * **Asynchrone Agenten-Pipelines & Complex Reasoning ([agents.ipynb](../../agents.ipynb)):** In Hintergrund-Workflows, bei denen der Nutzer nicht sekündlich zuschaut, zahlen sich die Reasoning-Tiefe, die gründliche Analyse mit tieferer logischer Verknüpfung, die Anbindung an Google Search und Vertex AI Search und der hohe Durchsatz von bis zu 157 TPS maximal aus.

---

**⏱️ Latenz-Analyse: Perzentile (P50, P90, P95, P99)**

In produktiven Systemen und API-Benchmarks ist der klassische arithmetische Durchschnitt (*Mean*) oft trügerisch, da wenige extreme Ausreißer (z. B. durch Cold Starts oder API-Queueing) den Wert verzerren. Stattdessen nutzt man **Perzentile (Quantile)**, um die reale Latenzverteilung abzubilden:

```
Schnell ◄─────────────────────────────────────────────────────────────────► Langsam
[===================== P50 =====================][====== P90 ======][= P99 =]
                 50 % der Anfragen                     40 %             9 %     1 %
           (Der typische Normalfall)                (Verzögert)               (Spitzen)
```

### Die Kennzahlen im Überblick

| Metrik | Definition | Bedeutung in der Praxis |
| :--- | :--- | :--- |
| **P50 (Median)** | **50 %** aller Anfragen waren schneller als dieser Wert. | Der **echte Normalfall**, den die Mehrheit der Nutzer erlebt (robust gegen Ausreißer). |
| **P90** | **90 %** aller Anfragen waren schneller (nur 10 % langsamer). | Erwartbare Latenz bei **erhöhter Auslastung** oder leichter Netzwerkverzögerung. |
| **P95** | **95 %** aller Anfragen waren schneller. | Gängiger **Industrie-Standard für SLAs** (Service Level Agreements). |
| **P99 (*Tail Latency*)** | **99 %** aller Anfragen waren schneller (nur das langsamste 1 % lag darüber). | Der **Worst Case** (z. B. Modell-Cold-Start, Backend-Drosselung oder Re-Routing). |


[!IMPORTANT] **Warum das für Agenten (`agents.ipynb`) entscheidend ist:**

In parallelen Workflows (wie deinem Fan-Out mit `web_agent` und `doc_agent`, die an einem `JoinNode` zusammenlaufen) bestimmt **immer der langsamste Pfad** das Gesamttempo. Selbst wenn 9 von 10 Aufrufen schnell sind (P50), wird ein paralleler Workflow durch den P90- oder P99-Ausreißer ausgebremst.

---

**Bewertung der Testergebnisse: DeepSeek V4.1 Flash MaaS**

Detaillierte Analyse des Benchmark-Laufs über 10 Iterationen:

| Metrik | TTFT (Time-To-First-Token) | Gesamtzeit (3 Sätze) | Interpretation |
| :--- | :--- | :--- | :--- |
| **Min** | **0.22 s (219 ms)** | **0.96 s** | Bestmöglicher Durchsatz bei warmem Cache & freier Queue |
| **P50 (Median)** | **0.33 s (331 ms)** | **1.74 s** | **Typisches Nutzererlebnis:** Extrem schnell und responsiv |
| **Mean (Ø)** | 0.91 s | 2.20 s | Statistisch verzerrt durch die ersten beiden Ausreißer |
| **P90** | **1.93 s** | **2.89 s** | 90 % aller Anfragen sind in unter 2,9 Sekunden fertig |
| **P95 / Max** | **4.84 s** | **6.13 s** | Tail Latency Spike (Run 2: Provider-Queue / MaaS-Allokation) |

---

Die wichtigsten Erkenntnisse:

1. **Lehrbuchbeispiel für P50 vs. Mean (Durchschnitt):**
   * Im regulären Betrieb (**Runs 3 bis 10**) reagiert DeepSeek extrem schnell: Das erste Token streamt stabil in **0.22 s bis 0.36 s** (220–360 ms) los, und die Antwort ist nach rund **1.7 s** fertig.
   * Der arithmetische Mittelwert (**Mean TTFT = 0.91 s**) ist fast dreimal so hoch wie der Median (**0.33 s**), weil Run 2 ihn nach oben zieht. Wer nur den Durchschnitt betrachtet, bekommt ein völlig falsches Bild der tatsächlichen Alltags-Performance; der Median spiegelt sie wider.

2. **Verhalten bei Kaltstart & Tail-Spikes (P90 / P95):**
   * **Run 1 (1.60 s TTFT):** Typischer Handshake- und Routing-Overhead beim ersten Verbindungsaufbau.
   * **Run 2 (4.84 s TTFT):** Ein klassischer Infrastruktur-Ausreißer auf Vertex AI MaaS, z. B. durch dynamische Container-Zuweisung und -Skalierung (Autoscaling), Instanz-Zuweisung oder kurzzeitiges API-Queueing im GCP-Cluster.

3. **Praktische Empfehlung für Produktion & Agenten:**
   * **Für Chatbots, interaktive UIs & User-Facing Frontends:** Hervorragend geeignet. 8 von 10 Anfragen beginnen in rund 300 Millisekunden zu streamen; das fühlt sich für Anwender praktisch latenzfrei, flüssig und interaktiv an.
   * **Für Agenten-Pipelines ([agents.ipynb](../../agents.ipynb)):** Wenn ein Agent mehrere Modell-Aufrufe oder Schritte nacheinander ausführt (z. B. Tool-Calls oder Verzweigungen), steigt die Wahrscheinlichkeit, irgendwann einen P90/P95-Spike zu treffen. Wichtig: HTTP- bzw. Client-Timeouts in Agent-Knoten **nicht** auf den Median (1.7 s) oder auf 2–3 s setzen, sondern mindestens **7 bis 8 Sekunden** Puffer einplanen, damit Ausreißer wie in Run 2 nicht abgebrochen werden.
