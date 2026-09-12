# Dequantisierung vs. echter Quantenvorteil

**Eine Landkarte — Synthese einer Forschungsdiskussion zu Quantum Machine Learning, Ewin Tangs Programm und darüber hinaus**

*Zusammenfassung und Struktursynthese · Stand 2. Juli 2026*
*Ergänzt am 12. September 2026 um die Fallstudie zu Huang et al. 2021 („Power of Data") und Zhao et al. 2026 („Massive Classical Data"); alle Ergänzungen sind als „**Ergänzung (Sept. 2026)**" markiert bzw. in Kapitel 17 gesammelt.*

---

Diese Notiz fasst eine ausführliche Diskussion zusammen, deren Ziel es war, das Terrain zwischen **Dequantisierung** (ein klassischer Algorithmus holt einen behaupteten Quantenvorteil ein) und **echtem Quantenvorteil** sauber zu strukturieren — als Vorarbeit für foundational-theoretische Forschung im Stil von Ewin Tang. Das Ergebnis ist eine mehrschichtige Landkarte mit vier Faktorgruppen in zwei Ebenen, zwei Ressourcen-Linsen (Zeit und Speicher) und einem wiederkehrenden Leitprinzip:

> **Quantenvorteil überlebt genau dann, wenn keine effiziente klassische Repräsentation die Rechnung einfängt** — und es gibt mehrere, voneinander unabhängige Orte, an denen ein solcher „Shortcut" lauern kann.

> **Ergänzung (Sept. 2026):** Die Landkarte deckt die *obere Reihe* der Daten-vs-Lerner-Matrix ab: klassische Daten, verarbeitet von klassischen oder quantenverstärkten Lernern. Die untere Reihe — Lernen aus Quantendaten (Kopien von $\rho$, Kanälen, Dynamiken) — liegt außerhalb der Karte (siehe Abschnitt 10 und Kapitel 17.1). Zu den bisherigen zwei Ressourcen-Linsen Zeit und Speicher kommt eine dritte, die *Power of Data* (2021) vermisst: **Samples / Prediction bei festem $N$** (Abschnitt 11).

---

## 1 · Ausgangspunkt: Ewin Tangs Programm

Tangs Beiträge zeigen, dass eine ganze Klasse von QML-Speedups nicht aus der Mathematik stammte, sondern aus dem **Inputmodell**. Der rote Faden: Wo ein Quantenalgorithmus low-rank-Struktur unter QRAM-Zugriff ausnutzt, kann ein klassischer Algorithmus mit „Sample-and-Query"-Zugriff (SQ) — dem klassischen Analogon zu QRAM — dasselbe in polynomieller Zeit.

- **Tang 2019 (recommendation systems):** Dequantisierung des Kerenidis–Prakash-Algorithmus; der Durchbruch.
- **Tang 2021:** Quantum-PCA und supervised clustering erreichen ihren Speedup nur wegen der State-Preparation-Annahmen.
- **Gilyén–Lloyd–Tang 2018:** low-rank-Matrixinversion (eine Low-rank-Variante von HHL).
- **CGLLTW 2020 (STOC/JACM):** das vereinheitlichende Framework — ein klassisches Analogon der QSVT (sampling-based singular value transformation), das die gesamte low-rank-QSVT-Klasse auf einen Schlag dequantisiert.
- **Bakshi–Tang 2024 (SODA):** die quantitativ scharfe Version, die die QSVT-Performance im Low-rank-Regime bis auf kleinen polynomiellen Overhead matcht.

**Konzeptioneller Kern:** Die dunkelvioletten „QRAM-basierten" QML-Speedups (recommendation, PCA, SVM, SDP, low-rank-Zerlegung) waren Artefakte des Input-Geschenks. Die sparsity-basierten Verfahren (HHL, TDA) sind eine andere Geschichte.

> **Ergänzung (Sept. 2026):** Zhao et al. 2026 drehen Tangs Befund um eine Ressource weiter. Sie beweisen eine allgemeine Relation zwischen Maschinengröße und Query-Komplexität: *Jede super-quadratische Query-Separation impliziert bereits einen exponentiellen Speicher-Vorteil.* Dequantisierte Algorithmen, die nach Tang nur noch polynomiellen Query-Speedup haben, können daher unter dem Platz-Kriterium weiterhin exponentiell vorne liegen — die Autoren schreiben wörtlich, diese Klasse sei „worth revisiting". Tang hat die Zeit-Tür geschlossen; die Speicher-Tür derselben Algorithmen steht offen (Abschnitt 13).

---

## 2 · Die drei Achsen am Problem-Interface (Ebene 2)

Der erste Strukturschritt: Dequantisierbarkeit hängt nicht an einem einzigen Merkmal. Es gibt (mindestens) drei Achsen, entlang derer ein klassischer Shortcut sitzen kann. Achse 1 und 2 gehören zur linearen Algebra (QSVT-Familie); Achse 3 zur Fourier-Familie.

| Faktor | dequantisierbar / simulierbar | resistent / echter Vorteil | Werkzeug bzw. Grenze |
|---|---|---|---|
| **Achse 1** — Zugriffsmodell (QSVT) | low-rank + SQ-Zugriff | hoher effektiver Rang (z. B. sparse HHL) | ℓ²-Sampling (Tang, CGLLTW) |
| **Achse 2** — Präzision (QSVT) | grobe relative Präzision | inverse-poly Präzision → BQP-vollständig (guided local Hamiltonian) | Monte-Carlo (Gharibian–Le Gall) |
| **Achse 3** — Härteannahme (Fourier) | Decoding klassisch lösbar / keine Struktur | Struktur + harte Decodierung (DQI+OPI, Shor) | Coding-Theorie / Gitter |
| **Achse 4** — Schaltkreis-Struktur (Ebene 1) | Clifford / Gauß / frei (Grad ≤ 2) | Magie + Verschränkung (Grad ≥ 3) | Stabilizer / Matchgate (Gottesman–Knill) |

**Das eine Leitprinzip über alle Achsen:** „Dequantisierung" heißt überall dasselbe — den klassischen Shortcut finden. Die Achsen unterscheiden sich nur darin, *wo* er lauern kann: im Input-Zugriff (1), in der Fehlertoleranz (2), in der Problemhärte (3) oder in der Schaltkreisstruktur (4, Ebene 1).

---

## 3 · Die Logik von notwendig und hinreichend (Achse 1 und 2)

Für die QSVT-Familie gilt eine präzise Konditionallogik, die oft verwechselt wird: **zwei notwendige Bedingungen, deren Konjunktion erst hinreichend ist.**

- **Hoher effektiver Rang ist notwendig** (low-rank ⇒ dequantisierbar), aber nicht hinreichend (sparse + grobe Präzision bleibt klassisch).
- **Feine (inverse-poly) Präzision ist ebenfalls notwendig** (grobe relative Präzision ist immer dequantisierbar), aber nicht hinreichend — bei low-rank ist feine Präzision billig, weil die Fehlernorm mit $\|A\|_F$ skaliert und wenige Singulärwerte die Masse tragen.
- **Erst die Konjunktion** (hoher Rang *und* feine Präzision) ist hinreichend — im guided-local-Hamiltonian-Problem sogar vollständig (schöpft ganz BQP aus).

**Die vereinheitlichende Frage:** Erlaubt das Input-Geschenk (SQ-Zugang bzw. Guiding-State) einen klassischen Shortcut, um die benötigte Spektralinformation auf die benötigte Präzision zu extrahieren — oder erzwingt die Aufgabe echte Spektralauflösung (Phasenschätzung)? Low-rank kürzt ab (wenige Eigenwerte); grobe Präzision braucht keine feine Auflösung; sparse + feine Präzision zwingt zur Nadel im exponentiell dichten Spektrum.

**Die schärfste Pointe von Gharibian–Le Gall** (und den Verfeinerungen von Cade et al.): Die BQP-Härte bleibt bei 2-lokalen Hamiltonians und bei Overlap bis zu $1 - 1/\mathrm{poly}(n)$ bestehen. Selbst ein fast perfekter Guiding-State rettet die klassische Seite nicht. Damit ist der Quantenkern lokalisiert: nicht in der Zustandspräparation (die darf geschenkt sein), sondern in der feinen Spektraltransformation. Offen bleibt die konstante additive Präzision (chemische Genauigkeit) im hochrangigen Regime — dort entscheidet sich, ob der GLH-Vorteil praktisch real oder ein Normierungsartefakt ist.

---

## 4 · LLMs auf Quantencomputern

Die Kritik überträgt sich, aber aus präzisen Gründen. Der exponentielle Zeit-Speedup für low-rank-ML ist tot; für LLMs kommen jedoch **drei unabhängige Hürden** hinzu, die schon ohne Dequantisierung greifen:

- **I/O- und Auslese-Engpass** (Aaronsons „read the fine print"): Gewichte laden und die volle Token-Verteilung auslesen frisst jeden polylog-Vorteil.
- **Nichtlinearität:** Quantenmechanik ist linear; Transformer leben von Softmax und Aktivierungen.
- **Dense/hochrangig:** Transformer-Matrizen sind generisch hochrangig — genau die Struktur, für die es keinen exponentiellen Quantenvorteil gibt.

Empirisch bestätigt: Quanten-Transformer sind entweder QLA-basiert (dequantisierungs-anfällig plus Auslese-Problem) oder variational/PQC ohne bewiesene Expressivitäts- oder Laufzeit-Separation. Dequantisierung ist hier nicht der Grund, sondern die saubere Linse, die erklärt, warum das „QRAM + lineare Algebra → ML-Speedup"-Programm überoptimistisch war.

**Die methodische Konsequenz ist eine Verschiebung der Beweislast:** Jeder QML-Vorteil muss drei Tests bestehen — Input nicht billig samplebar, Output nicht durch Auslese zerstört, Struktur klassisch wirklich hart.

> **Ergänzung (Sept. 2026):** Der zweite Test („Output nicht durch Auslese zerstört") ist *ressourcenrelativ*. Zhao et al. 2026 zeigen, dass das Auslese-Argument unter der Speicher-Linse wegfällt: Eine speichereffiziente klassische Maschine mit $\mathrm{poly}(\log N)$ Bits leidet an exakt demselben Readout-Problem — auch aus ihr lassen sich nur $\mathrm{poly}(\log N)$ Bits ziehen —, und jede Eigenschaft, die aus einer $\mathrm{poly}(\log N)$-Bit-Maschine effizient extrahierbar ist, ist es auch aus einer $\mathrm{poly}(\log N)$-Qubit-Maschine. Die Zielgrößen müssen dann nicht mehr „quantenfreundlich" sein. Technisch gelöst wird die vorzeichenerhaltende Auslese durch *interferometric classical shadows* (Hadamard-Test + Clifford-Shadows). Der Auslese-Test beißt also beim Zeit-Vorteil, nicht beim Speicher-Vorteil. Für LLMs bleibt die Hürde trotzdem, weil dort die *Zeit* der Engpass ist und die Nichtlinearität ohnehin unberührt bleibt.

---

## 5 · DQI und die dritte Achse

**Decoded Quantum Interferometry (DQI)** löst Optimierung (max-LINSAT, optimal polynomial intersection) mit behauptetem exponentiellem Speedup. Es gehört *nicht* in den Präzisions-Bucket, sondern ist Reinform der Achse 3. Die QFT reduziert das Optimierungsproblem auf ein Decoding-Problem; der Speedup entsteht, weil sich die algebraische Struktur im Decoding spiegelt. Der Input ist kompakt (keine Datenmatrix zum Sketchen → Tangs Tür fehlt), der Output diskret-exakt (keine Präzisionsachse). Der Vorteil hängt allein an der klassischen Härte des Decoding-Problems — der kryptografische Modus, wie bei Shor.

**Aktueller Stand (Anfang 2026):** Der OPI-Speedup steht — er wurde nicht klassisch eingeholt, sondern wird als führender verifizierbarer Advantage-Kandidat gehandelt. Die kritische Literatur (Anschuetz–Gamarnik–Lu, „DQI requires structure"; Marwaha et al.) zielt auf Achse 3 selbst: Der Vorteil ist an algebraische Struktur gebunden; für unstrukturierte Instanzen schlägt DQI spezialisierte klassische Algorithmen nicht.

---

## 6 · Die zwei Ebenen: Schaltkreis vs. Problem

Ein zweiter, kategorial verschiedener Strukturschnitt. Es gibt zwei Bedeutungen von „Dequantisierung", die verschiedene Objekte betreffen:

- **Ebene 2 — Problem-Interface (die drei Achsen):** *algorithmische* Dequantisierung — löse das Problem anders (Tangs ℓ²-Sampling simuliert den Schaltkreis nie).
- **Ebene 1 — Schaltkreis-intern (die Quantumness-Säulen):** *simulationsbasierte* Dequantisierung — simuliere den Schaltkreis selbst (Stabilizer-Tableau, Gauß-Kovarianzmatrix, Matchgate-Pfaffian).

Sie sind **komplementär, nicht geschachtelt.** Der Zeuge: QRAM-basierte QML-Schaltkreise sind hoch in Verschränkung und Magie (als Schaltkreis nicht simulierbar), doch Tang dequantisierte die *Probleme*. Damit gilt: hohe Schaltkreis-Quantumness impliziert nicht Problem-Vorteil. Niedrig auf irgendeiner Säule ⇒ Schaltkreis simulierbar ⇒ kein Vorteil (eine unbedingte Route). Hoch auf allen ⇒ noch kein Vorteil.

---

## 7 · Was ist „Quantumness"? Drei Säulen und der Grad-Knopf

Die Simulierbarkeits-Literatur kennt drei Ressourcen, jede an eine mathematische Sprache gebunden:

- **Verschränkung** (Jozsa): Schmidt-Rang; Schrödinger-Sprache. Niedrige Verschränkung → MPS/Tensornetz.
- **Magie** (Gottesman–Knill, Bravyi–Gosset): Nichtstabilizität; Heisenberg-Sprache. Der Knopf ist der **Polynomgrad des Generators** in der Heisenberg-Weyl-Algebra — Grad ≤ 2 (symplektische Gruppe, Gauß/Clifford) ist simulierbar (Wigner $W \geq 0$); Grad ≥ 3 (das T-Gate, cubic phase) verlässt die Gruppe, erzeugt $W < 0$ und schaltet den echten Quantencomputer frei.
- **Fermionische Magie** (Valiant, Terhal–DiVincenzo): Nicht-Gaußianität freier Fermionen; der orthogonale Ast. Bilineare (Grad-2) fermionische Hamiltonians sind frei; quartische Terme (Swap-Gates) sind die Ressource.

Der Grad-Knopf vereinheitlicht zwei der drei Säulen: Magie (symplektisch/bosonisch) und fermionische Magie (orthogonal/fermionisch) sind zwei Gesichter desselben Musters „quadratischer Kern frei, höherer Grad ist die Ressource". Verschränkung ist die Ausnahme (Tensorstruktur, kein Gradfilter) — genau deshalb gibt es kein einzelnes Quantumness-Skalar.

---

## 8 · Die Vereinheitlichung: verschiedene Ränge

Der tiefste Synthesepunkt: **Klassische Behandelbarkeit = niedriger Rang in irgendeiner Zerlegung.** Beide Ebenen-Obstruktionen sind im Kern „der Rang ist zu hoch zum Sketchen" — nur bedeutet „Rang" jedes Mal etwas anderes.

| Rahmen | Zerlegung / Rang | niedriger Rang ⇒ leicht (Satz) |
|---|---|---|
| Achse 1 / Tang (Zeit) | Matrixrang (SVD) | ℓ²-Sampling / CGLLTW |
| Magie / Achse 4 | Stabilizer-Rang $\chi$ | Bravyi–Gosset |
| Verschränkung | Schmidt-Rang / MPS-Bonddimension | Jozsa, Vidal |
| Fermionische Magie | fermionischer Gauß-Rang (Pfaffian) | Valiant |

Die Obstruktionen sind unabhängig, weil sie Hochrangigkeit in verschiedenen Basen messen. QRAM-QML ist niedrig im Matrixrang (Tang knackt es), aber hoch im Stabilizer-Rang (Gottesman–Knill scheitert). Trägt man Magie gegen ℓ²-Sketchbarkeit in einer 2×2-Matrix auf, sind alle vier Felder besetzt — der formale Beweis der Unabhängigkeit. Die Richtung „niedriger Rang ⇒ leicht" ist in jedem Rahmen ein Satz; die Richtung „hoher Rang in allen Zerlegungen ⇒ Vorteil" ist kein Satz (es könnte eine unbekannte Zerlegung geben) — das ist die offene Front.

**Bonus-Brücke:** Stabilizer-Rang lebt in der Higher-Order-Fourier-Analyse (für $p > 2$ sind Stabilizer-Zustände quadratische Polynome; Magie = Fourier-Struktur vom Grad ≥ 3) — das verschweißt den Grad-Knopf mit der Fourier-Welt der Achse 3.

---

## 9 · Die algebraische Struktur von Shor und DQI

Warum sind Shor und DQI (vermutlich) nicht dequantisierbar? Der Kern ist darstellungstheoretisch. Shor ist das abelsche Hidden-Subgroup-Problem: Eine auf Nebenklassen einer verborgenen Untergruppe $H$ konstante Funktion hat ihre Fourier-Masse exakt auf dem Annihilator $H^\perp$ (Pontryagin-Dualität); die QFT ist der Basiswechsel in die Charaktere, und eine Messung sampelt in einem Schuss aus $H^\perp$. DQI hat dasselbe Skelett, nur ist das duale Objekt ein Code (Reed-Solomon-nah), und ein klassisch effizienter Decoder liest die Lösung aus.

**Das gemeinsame Gesetz:** Eine darstellungstheoretische Transformation (Gruppen- oder Körper-Fourier) bildet eine global verborgene algebraische Invariante auf einen sampelbaren dualen Träger ab — und das klassische Extrahieren dieser Invariante ist ein konjekturales Einweg-Problem. Die nötige Reichheit ist eine Falltür-Balance: genug Struktur, dass die Transformation greift, aber genug Härte, dass kein klassisches Inverses existiert.

**Generalisierung über HSP:** Abelsches HSP ist gelöst (Shor); nicht-abelsches HSP ist auch quantenmechanisch schwer, weil hochdimensionale Irreps das Standard-Fourier-Sampling aushungern. Dihedrales HSP ist zu Gitterproblemen äquivalent (Regev), symmetrisches HSP zu Graphisomorphie. Die Irrep-Dimension ist der algebraische Knopf für die quantenmechanische Lösbarkeit — so wie der Polynomgrad der Knopf für die Simulierbarkeit war.

Zwei entscheidende Unterschiede zur Magie: Achse 3 ist **nicht monoton** (Goldilocks — zu viel Struktur wird klassisch leicht), und sie ist **bedingt** (kryptografische Vermutung) statt unbedingt (Satz). Das beweisbare Skelett dieser Familie ist Forrelation (Aaronson–Ambainis): eine Quantenabfrage gegen $\sqrt{N}$ klassische — aber nur als Orakel-Trennung; bei expliziter Funktion (Shor, DQI) bleibt die Vermutung.

---

## 10 · Was bleibt für QML? Drei aktuelle Arbeiten (2026)

Relativieren die jüngsten Ergebnisse die Kritik? Ja — aber chirurgisch, genau wie das Gerüst es vorhersagt. Sie besetzen spezifische Zellen, statt die Karte umzuwerfen. Was tot bleibt: der exponentielle Zeit-Speedup für low-rank-ML im queryable Modell via QRAM.

| Tür | Was sie gibt | Vorbehalt |
|---|---|---|
| Exp. ZEIT-Speedup, low-rank ML via QRAM | — | geschlossen: dequantisiert (Tang, CGLLTW) |
| Versteckte Struktur (Achse 3) | beweisbarer ZEIT-Vorteil im QSQ-Modell (periodische Neuronen; Lewis–Gilboa–McClean 2026) | strukturierte Funktionsklasse, kein generisches ML; SQ-unbedingt statt kryptografisch |
| Speicher im Streaming | exp. SPEICHER-Vorteil, informationstheoretisch, auf echten Daten (Zhao–Preskill–Huang–McClean 2026) | ZEIT = klassisch, $\tilde O(N)$; Oracle Sketching umgeht QRAM ganz |
| Lernen aus Quantendaten | bewiesene Separation (Huang et al.) | Input ist quantum, nicht klassisch — außerhalb der Karte |

Das QRAM-Resultat (Zhejiang, bucket-brigade, 4–8 Bit, 60–81 % Fidelity) adressiert den I/O-Engpass, belebt die dequantisierte low-rank-ML aber nicht — diese fiel bereits im idealisierten QRAM-Regime, in dem Tang der klassischen Seite das SQ-Äquivalent schenkt und trotzdem matcht.

> **Ergänzung (Sept. 2026) — die Grenze der Karte scharf gezogen.** „Außerhalb der Karte" lässt sich mit drei Lackmustests operationalisieren (aus den Quantum-Learning-Notizen, Kapitel 17.1):
> 1. **Wo lebt das Unbekannte?** Dichteoperator/Kanal (unten) ↔ klassische Funktion/Verteilung/Datensatz (oben).
> 2. **Ist „Anzahl der Kopien" eine sinnvolle Kostengröße?** Quantendaten sind nicht klonbar; klassische Samples sind beliebig kopierbar.
> 3. **Binden No-Cloning, Holevo und Gentle Measurement als Lernschranken?** Auf ein CSV-File greifen sie nicht.
>
> Beide in Kapitel 17 analysierten Papers liegen nach allen drei Tests *innerhalb* der Karte — auch *Power of Data*, obwohl es seine Testfälle selbst „quantum data sets" nennt: Die Eingaben sind klassische PCA-Vektoren, quantenmechanisch ist nur der Labelgenerator. Und beide benutzen Classical Shadows, ohne dadurch in die untere Reihe zu rutschen: Shadows auf einen *selbst präparierten* Zustand sind Auslese des eigenen Modells, kein Experiment an einem unbekannten Quantenobjekt. **Bottom-Row-Technik in einem Top-Row-Problem** ändert die Zuordnung nicht.

---

## 11 · Zwei neue Differenzierungen: Ressource und Modell

Die drei Arbeiten schärfen die Karte um zwei Dimensionen, die vorher im Querschnitt zusammengefaltet waren: die **Ressource** (Zeit vs. Speicher) und das **Modell** (queryable/Batch vs. Streaming). Die scheinbare Spannung „Tang tötet PCA / Preskill gibt PCA-Vorteil" löst sich exakt hier auf: Tang dequantisiert die *Zeit* im queryable Modell; Zhao et al. geben einen *Speicher*-Vorteil im Streaming-Modell. Dieselbe Aufgabe, andere Ressource, anderes Modell — kein Widerspruch. Der I/O-Querschnitt, als reine Obstruktion gezeichnet, hat also einen Vorteil in sich versteckt — aber einen Speicher-, keinen Zeitvorteil.

> **Ergänzung (Sept. 2026) — die dritte Ressource: Samples / Prediction.** Neben Zeit und Speicher gibt es eine dritte Linse, die *Power of Data* (Huang, Broughton, Mohseni, Babbush, Boixo, Neven, McClean 2021) vermisst: **Prediction-Vorteil bei festem Trainingsumfang $N$.** Der Befund dort ist die Fragilitätsaussage der oberen Reihe: Mit genügend klassischen Trainingsdaten holt klassisches ML Quantenmodelle auf klassischen Aufgaben ein, selbst wenn der Labelgenerator klassisch nicht simulierbar ist (Proposition 1: könnte man ihn ohne Daten effizient berechnen, wäre BPP = BQP — mit Daten geht es trotzdem). Der Diskriminator ist die **geometrische Differenz** $g_{CQ} = \sqrt{\|\sqrt{K_Q}K_C^{-1}\sqrt{K_Q}\|_\infty}$ zwischen klassischem und Quantenkernel; kleines $g_{CQ}$ ⇒ klassisches ML garantiert gleich gut, unabhängig von den Labels.
>
> Damit stehen drei Ressourcen mit drei verschiedenen Knöpfen nebeneinander:
>
> | Ressource | Diskriminator | Regime des Vorteils | Referenz |
> |---|---|---|---|
> | Zeit | Matrixrang | hoher Rang + feine Präzision | Tang, CGLLTW, Gharibian–Le Gall |
> | Speicher | Output-Dimension | Streaming, hochdimensionales kohärentes Objekt | Zhao et al. 2026 |
> | Samples / Prediction | geometrische Differenz $g_{CQ}$, effektive Dimension $d$ | großes $g$, kleines $N$; schrumpft mit $N \to \infty$ | Huang et al. 2021 |
>
> **Die schärfste Querverbindung:** Die Sample-Linse sagt „mehr Daten schließen die Lücke" (Fig. 7 in *Power of Data* zeigt das explizit). Die Speicher-Linse sagt das Gegenteil, sobald die klassische Maschine in der Größe beschränkt ist: Zhao et al. beweisen, dass klassische Maschinen, die exponentiell größer als die Quantenmaschine, aber unterhalb der nötigen Größe sind, *superpolynomial* mehr Samples und Zeit brauchen. Die Konvergenz aus 2021 setzt also stillschweigend unbeschränkten klassischen Speicher voraus. Unter Speicherbeschränkung gilt sie nicht.

---

## 12 · Speicher-Vorteil hat zwei Quellen

„Speicher-Vorteil" ist kein einheitlicher Achsen-Slice, sondern zerfällt in zwei verschiedene Mechanismen:

| Quelle | Mechanismus | Wo in der Karte |
|---|---|---|
| **A — Zustandskomplexität** | klassisch exp. Speicher, um hochverschränkte/magische Zustände zu repräsentieren; klassischer Ausweg nur bei niedriger Achse-4-Ressource (MPS, Stabilizer, frei) | Quantensimulation = Achse 2 (Zeit) × Achse 4 (Speicher); Feynman 1981 |
| **B — Datenkompression** | strömende klassische Daten kohärent in einen kleinen Zustand skizzieren (Oracle Sketching) | Achse-1-ML im Streaming (Zhao–Preskill–Huang–McClean) |

**Wichtige Konsequenzen:** (i) Die Achse-2-Speicherzelle war nie wirklich offen — Simulationsprobleme erben ihren Speicher-Vorteil aus Quelle A (Achse 4). (ii) Achse 3 hat keinen Speicher-Hebel: Shor braucht nur $O(n)$ Qubits für eine $n$-Bit-Zahl. (iii) Quantensimulation ist klassischer Input (ein spezifizierter Hamiltonian) und gehört voll in die Karte — sie ist *nicht* die Quantendaten-Ausnahme; diese betrifft nur extern gelieferte Quantenzustände.

> **Ergänzung (Sept. 2026) — die Rolle von Holevo bei Quelle B.** Holevo taucht bei Zhao et al. in einer Rolle auf, die man nicht mit der Lernschranke aus der unteren Reihe verwechseln darf. Dort ist Holevo (mit No-Cloning und Gentle Measurement) die *Informationsgrenze gegenüber einem unbekannten Quantenobjekt*. Hier ist Holevo der *a-priori-Einwand gegen den Speichervorteil selbst*: $n$ Qubits speichern nur $n$ klassische Bits, also sollte eine kleine Quantenmaschine nichts Wesentliches über einen großen Datensatz behalten können. Die Umgehung: Die Maschine speichert den Datensatz nie. Jedes Sample wird einmal verarbeitet und verworfen; Oracle Sketching baut inkrementell ein *approximatives Orakel* auf, nicht eine Repräsentation der Daten. Die Zahl der klassischen Samples skaliert quadratisch mit der Zahl der Quanten-Queries — beweisbar optimal, und der Grund ist die Born-Regel (Amplitude vs. Wahrscheinlichkeit). Holevo bindet danach nur noch die Auslese des *eigenen* Zustands, und diese Bindung fällt im Vergleich mit gleich speicherbeschränkten klassischen Maschinen weg (Abschnitt 4).

---

## 13 · Achse 1 voll aufgeschlüsselt (Ressource × Modell)

Vierteilt man Achse 1, kristallisiert sich der schärfste Einzelbefund heraus: **Der Knopf wechselt.** In der Zeit ist der Diskriminator der Rang; im Speicher ist er die Dimensionalität dessen, was repräsentiert/ausgegeben werden muss.

| | Batch (queryable) | Streaming |
|---|---|---|
| **ZEIT** | Tangs Regime. Knopf: Rang. low-rank → dequantisiert (ℓ²); high-rank → Achse 2. | Kein Zeit-Vorteil. Quantum $\tilde O(N)$ = klassisch. Oracle Sketching hilft hier nicht. |
| **SPEICHER** | Schwächer / murky. Daten schon gespeichert ($N$ Platz bezahlt); Vorteil nur in Arbeits-/Output-Platz. Eigenes offenes Feld. | Oracle Sketching. Exp. Speicher-Vorteil, informationstheoretisch (Zhao et al.). Knopf: Output-Dimension, nicht Rang. |

**Antworten auf die drei Fragen**

- **(c) Oracle Sketching in der Zeit?** Nein — reiner Speicher-Mechanismus; Zhao et al. sagen selbst, Quantenzeit = $\tilde O(N)$ = klassisch. Die einzige Zeit-Geschichte unter Achse 1 bleibt Tangs rang-basierte Dequantisierung.
- **(b) low-rank vs. high-rank auch im Speicher?** Nein — Rang ist der Zeit-Knopf. Im Speicher gewinnt Quanten auch bei low-rank, weil Amplitudenkodierung einen $N$-dimensionalen Vektor in $\log N$ Qubits packt (eine Aussage über die Dimension, nicht den Rang). Dasselbe low-rank-lineare-System ist zeitlich dequantisierbar (Tang), aber im Speicher vorteilhaft (Zhao).
- **(a) Wann Dequantisierung im Speicher/Streaming?** Wenn die nötige Repräsentation niedrigdimensional ist (Skalar, Summary) und ein klassisches lineares Sketch (Johnson–Lindenstrauss, Frequent Directions) sie klein hält. Der Quanten-Vorteil überlebt nur, wo ein hochdimensionales kohärentes Objekt gebraucht wird, das kein klassischer Sketch komprimieren kann.

**Die Symmetrie:** In der Zeit lautet die Frage „reicht ein ℓ²-Sample (Rang niedrig)?", im Speicher „reicht ein lineares Sketch (Output niederdimensional)?" — zwei Sketches, zwei Knöpfe, dieselbe Logik.

> **Ergänzung (Sept. 2026) — Statuseinordnung der Streaming-Speicher-Zelle.** Die Härte bei Zhao et al. ist *unbedingt*: Die klassischen unteren Schranken laufen über eine Relation Maschinengröße ↔ Query-Komplexität (Kommunikationsargument), gelten bei unbegrenzter klassischer Zeit und selbst wenn BPP = BQP, und hängen nur an der Gültigkeit der Quantenmechanik. Damit gehört diese Zelle in dieselbe Statusklasse wie Achse-1/2-Resistenz (Satz), nicht wie Achse-3-Resistenz (kryptografische Vermutung) — vgl. Kernprinzip 3. Die Autoren ziehen daraus die Konsequenz, dass eine experimentelle Bestätigung oder Widerlegung ein Test der Quantenmechanik an der Komplexitätsfront wäre, analog zu Bell-Ungleichungen.

---

## 14 · Offene Forschungsrichtungen (das Radar)

Die integrierte Karte macht leere und unterbeleuchtete Zellen sichtbar — Projektkandidaten im Tang-Stil:

- **TDA / Simplex-Sampling-Grenze:** präzise charakterisieren, welche Input-Access-Annahme topologische Datenanalyse dequantisierbar macht (der Flaschenhals ist die Zustandspräparation — Achse 1 in Verkleidung).
- **Gaussian-Process-Regression [ZFF19]** unter verschiedenen Kernmatrix-Strukturen sauber dequantisieren (zugänglicher Einstieg).
- **Guided-local-Hamiltonian-Phasendiagramm** in (Präzision, Overlap, Lokalität); insbesondere die konstante additive Präzision (chemische Genauigkeit) im hochrangigen Regime.
- **Klassische untere Schranken im SQ-Modell** — ist die polynomielle Abhängigkeit von Bakshi–Tang optimal?
- **Die „dritte Matrixklasse"** jenseits von low-rank und sparse (hierarchische/HSS-Matrizen, abklingende Singulärwerte, spezielle Graph-Laplace-Operatoren).
- **Die Brücke zwischen Problem-Interface-Matrixrang und Schaltkreis-Stabilizer-Rang** — ein Rahmen, der SVD-Sketchbarkeit und Stabilizer-Rang auf dieselbe Bühne stellt. Soweit erkennbar unbearbeitet; sitzt genau am Schnittpunkt der beiden Ebenen.
- **Strukturiertes Lernen × Speicher** — hat der periodische-Neuronen-Vorteil zusätzlich eine Speicher-Geschichte, oder nur die Zeit-Geschichte? Die Kreuzung der beiden neuen Achsen ist unbesetzt.
- **Achse 4 als Speicher-Maß durchdekliniert** (Verschränkung → Bonddimension, Magie → Stabilizer-Rang, Fermionen → Pfaffian) — Quelle A verfeinert.
- **Achse 2 voll aufschlüsseln (Ressource × Modell)** — testen, ob „der Knopf wechselt" eine Eigenheit von Achse 1 ist oder ein allgemeines Prinzip.
- **Welche Streaming-Aufgaben sind speicher-dequantisierbar?** — die Nahtstelle zwischen klassischer Sketching-Theorie und den unteren Schranken von Zhao et al.
- **Formale No-go-Synthese für LLMs** — die drei Hürden zu einer Schranke für Architektureigenschaften zusammenziehen.

> **Ergänzung (Sept. 2026) — drei weitere Radar-Punkte aus der Fallstudie:**
> - **Speicherbeschränktes Power-of-Data.** Wie verhalten sich geometrische Differenz $g_{CQ}$ und Modellkomplexität $s_K(N)$, wenn die klassische Maschine in der Größe beschränkt ist? Die Kernel-Generalisierungstheorie (2021) und die Query-/Kommunikationshärte (2026) sprechen zwei verschiedene Sprachen über dieselbe Aufgabe; eine Brücke fehlt.
> - **Adversarial vs. natürlich.** 2021 musste der Vorteil über engineerte Labels erzwungen werden (Appendix G: verallgemeinertes Eigenwertproblem, das $s_C = g^2 s_Q$ saturiert); 2026 tritt er auf IMDb und PBMC-scRNA-seq auf. Welche Struktur natürlicher Daten trägt den Speichervorteil — und ist sie dieselbe, die $g_{CQ}$ groß macht?
> - **Dequantisierte Algorithmen unter der Platz-Linse revisited.** Die Relation „super-quadratische Query-Separation ⇒ exponentieller Speichervorteil" ist ein Programm: Welche der von Tang/CGLLTW zeitlich dequantisierten Algorithmen (PCA, SVM, recommendation, low-rank-Inversion) behalten im Streaming-Speichermodell eine exponentielle Separation, und welche fallen einem klassischen linearen Sketch zum Opfer?

---

## 15 · Kernprinzipien in einem Satz

1. **Quantenvorteil überlebt genau dann, wenn keine effiziente klassische Repräsentation die Rechnung einfängt** — und es gibt mehrere unabhängige Orte, an denen ein Shortcut lauern kann (Input-Zugriff, Präzision, Härte, Schaltkreisstruktur).
2. **Behandelbarkeit = niedriger Rang in irgendeiner Zerlegung** (Matrix-, Stabilizer-, Schmidt-, fermionischer Rang). Vorteil = irreduzibel hoher Rang über alle bekannten Zerlegungen (ein offenes Programm, kein Satz).
3. **Achse-1/2-Resistenz ist unbedingt** (Satz bzw. BQP-Vollständigkeit); **Achse-3-Resistenz ist bedingt** (kryptografische Vermutung). Deshalb wandert DQIs Status, während ein Clifford-Schaltkreis für immer simulierbar bleibt.
4. **Ressource und Modell sind eigene Dimensionen:** Der Zeit-Diskriminator ist der Rang, der Speicher-Diskriminator die Output-Dimension; Speicher-Vorteil hat zwei Quellen (Zustandskomplexität via Achse 4; Datenkompression via Oracle Sketching), und für Achse 3 spielt Speicher keine Rolle.
5. **Für ML gilt:** Der exponentielle Zeit-Speedup für low-rank-Probleme via QRAM ist tot, aber es existieren beweisbare Vorteile in strukturiertem Lernen (Zeit, QSQ) und im Speicher (Streaming) — die Kritik ist geschärft, nicht widerlegt.

> **Ergänzung (Sept. 2026):**
> 6. **Drei Ressourcen, drei Knöpfe:** Zeit (Rang), Speicher (Output-Dimension), Samples/Prediction (geometrische Differenz). Die Fragilitätsaussage der oberen Reihe („klassisches ML holt mit genug Daten auf") ist eine Aussage über die Sample- und die Zeit-Linse — nicht über die Speicher-Linse, wo die Separation unbedingt ist und mit $N$ nicht schrumpft.
> 7. **Die Grenze der Karte ist das Zugriffsmodell, nicht die Technik:** Ein Paper gehört zur oberen Reihe, wenn das Unbekannte klassisch ist, Kopien keine Kosten sind und No-Cloning/Holevo nicht als Lernschranken binden — unabhängig davon, ob es Classical Shadows, Bell-Messungen oder Quantenkernel verwendet. Bottom-Row-Werkzeuge in Top-Row-Problemen sind die Regel, nicht die Ausnahme.

---

## 16 · Referenzen

*Hinweis: Autorlisten und Venues sind nach bestem Wissen wiedergegeben; einige arXiv-Nummern der 2025/2026-Arbeiten sollten bei Gelegenheit verifiziert werden. Zwei Einträge wurden am 12. September 2026 gegen die vorliegenden PDFs korrigiert (markiert).*

- E. Tang, „A quantum-inspired classical algorithm for recommendation systems", STOC 2019. arXiv:1807.04271.
- E. Tang, „Quantum principal component analysis only achieves an exponential speedup because of its state preparation assumptions", Phys. Rev. Lett. 127, 060503 (2021). arXiv:1811.00414.
- A. Gilyén, S. Lloyd, E. Tang, „Quantum-inspired low-rank stochastic regression with logarithmic dependence on the dimension", arXiv:1811.04909 (2018).
- N.-H. Chia, A. Gilyén, T. Li, H.-H. Lin, E. Tang, C. Wang, „Sampling-based sublinear low-rank matrix arithmetic framework for dequantizing quantum machine learning", STOC 2020 / JACM 2022. arXiv:1910.06151.
- A. Bakshi, E. Tang, „An improved classical singular value transformation for quantum machine learning", SODA 2024. arXiv:2303.01492.
- E. Tang, K. Tian, „A CS guide to the quantum singular value transformation", SOSA 2024. arXiv:2302.14324.
- S. Gharibian, F. Le Gall, „Dequantizing the quantum singular value transformation: hardness and applications to quantum chemistry and the quantum PCP conjecture", STOC 2022 / SICOMP 2023. arXiv:2111.09079.
- C. Cade, M. Folkertsma, S. Gharibian, R. Hayakawa, F. Le Gall, T. Morimae, J. Weggemans, „Improved hardness results for the guided local Hamiltonian problem", ICALP 2023.
- S. Jordan, N. Shutty, M. Wootters, A. Zalcman, A. Schmidhuber, R. King, S. Isakov, T. Khattar, R. Babbush, „Optimization by Decoded Quantum Interferometry", Nature (2025). arXiv:2408.08292.
- E. Anschuetz, D. Gamarnik, B. Lu, „Decoded quantum interferometry requires structure", arXiv:2509.14509 (2025).
- A. Marwaha, B. Fefferman, A. Gheorghiu, V. Havlíček, „On the complexity of decoded quantum interferometry", arXiv:2509.14443 (2025).
- S. Bravyi, D. Gosset, „Improved classical simulation of quantum circuits dominated by Clifford gates", Phys. Rev. Lett. 116, 250501 (2016).
- D. Gottesman, „The Heisenberg representation of quantum computers" (1998); Gottesman–Knill-Theorem.
- L. G. Valiant, „Quantum circuits that can be simulated classically in polynomial time", SIAM J. Comput. (2002); B. M. Terhal, D. P. DiVincenzo, „Classical simulation of noninteracting-fermion quantum circuits", Phys. Rev. A (2002).
- „Stabilizer rank and higher-order Fourier analysis", arXiv:2107.10551.
- A. Schmidhuber, S. Lloyd, „Complexity-theoretic limitations on quantum algorithms for topological data analysis", PRX Quantum (2023). arXiv:2209.14286.
- S. Apers, S. Gribling, S. Sen, D. Szabó, „A (simple) classical algorithm for estimating Betti numbers", Quantum (2023).
- S. Aaronson, A. Ambainis, „Forrelation: a problem that optimally separates quantum from classical computing", STOC 2015.
- O. Regev, „Quantum computation and lattice problems", FOCS 2002 (dihedrales HSP und Gitter).
- Y. Liu, S. Arunachalam, K. Temme, „A rigorous and robust quantum speed-up in supervised machine learning", Nature Physics (2021).
- H.-Y. Huang et al., „Quantum advantage in learning from experiments", Science 376, 1182 (2022).
- L. Lewis, D. Gilboa, J. R. McClean, „Quantum advantage for learning shallow neural networks with natural data distributions", Nature Communications 17, 1341 (2026). arXiv:2503.20879.
- H. Zhao, A. Zlokapa, H. Neven, R. Babbush, J. Preskill, J. R. McClean, H.-Y. Huang, „Exponential quantum advantage in processing massive classical data", arXiv:2604.07639 (8. April 2026). *[Autorliste korrigiert gegen das arXiv-PDF: Neven fehlte.]*
- Zhejiang-University-Team, „Experimental demonstration of a bucket-brigade QRAM architecture on a superconducting processor", Nature Physics (2026).
- J. Cotler, H.-Y. Huang, J. R. McClean, „Revisiting dequantization and quantum advantage in learning tasks", arXiv:2112.00811 (2021). *[Korrigiert: McClean statt „McArdle"; bei Gelegenheit gegen arXiv verifizieren.]*

*Neu aufgenommen (Sept. 2026):*

- H.-Y. Huang, M. Broughton, M. Mohseni, R. Babbush, S. Boixo, H. Neven, J. R. McClean, „Power of data in quantum machine learning", Nature Communications 12, 2631 (2021). arXiv:2011.01938.
- H.-Y. Huang, R. Kueng, J. Preskill, „Predicting many properties of a quantum system from very few measurements", Nature Physics 16, 1050 (2020) — Classical Shadows; Werkzeug in beiden Fallstudien-Papers.
- H.-Y. Huang, R. Kueng, J. Preskill, „Information-theoretic bounds on quantum advantage in machine learning", Phys. Rev. Lett. 126, 190505 (2021). arXiv:2101.02464 — Folgearbeit zu *Power of Data* mit oberen/unteren Schranken für klassisches vs. Quanten-ML beim Lernen von Quantenmodellen.

---

## 17 · Fallstudie: Zwei Buchdeckel derselben Reihe — *Power of Data* (2021) und *Massive Classical Data* (2026)

> **Dieses Kapitel ist eine Ergänzung vom 12. September 2026** und fasst die Analyse zweier Papers aus derselben Google-Quantum-AI/Caltech-Gruppe zusammen (gemeinsame Autoren: Huang, Babbush, Neven, McClean). Beide sitzen in der oberen Reihe der Daten-vs-Lerner-Matrix, markieren aber die beiden Enden dessen, was dort möglich ist. Die Einzelbefunde sind in den Abschnitten 1, 4, 10–15 eingearbeitet; hier steht die Argumentation im Zusammenhang.

### 17.1 Die Daten-vs-Lerner-Matrix als Rahmen der Karte

Die Landkarte dieser Notiz und die Quantum-Learning-Notizen („Learning from Quantum Experiments") teilen sich ein Koordinatensystem:

| | Klassische Lerner | Quantenverstärkte Lerner |
|---|---|---|
| **Klassische Daten** | klassisches ML | „QML on classical data": Feature Maps, variationelle Klassifikatoren, Quantenkernel — **Gebiet dieser Landkarte** |
| **Quantendaten** (Kopien von $\rho$ / Kanälen) | Messprotokoll + klassische Statistik: Shadows, Bell-Sampling + classical decoders | Quantenspeicher-Protokolle: coherent two/multi-copy — **außerhalb der Karte** |

Die Zeilengrenze ist das *Zugriffsmodell*, nicht die Hardware. Drei Lackmustests trennen scharf:

1. **Wo lebt das Unbekannte?** Dichteoperator/Kanal ↔ klassischer Datensatz, klassische Funktion, klassische Verteilung.
2. **Ist „Anzahl der Kopien" eine sinnvolle Kostengröße?** Quantendaten sind nicht klonbar — jede Kopie kostet. Klassische Daten sind beliebig kopierbar — die Frage ist sinnlos.
3. **Binden No-Cloning, Holevo und Gentle Measurement als Lernschranken?** Genau diese drei machen Lernen aus Quantendaten nichttrivial; auf klassische Daten greifen sie nicht.

Drei Grauzonen sind damit sauber aufgelöst: (a) *engineerte Zustände* — ob $\rho$ von einem Molekül oder einem Prozessor stammt, ist gleichgültig, solange das Unbekannte ein Quantenobjekt ist; (b) *Simulatoren* — das Zugriffsmodell bleibt das eines Quantenexperiments; (c) *hybride Decoder* — ein neuronales Netz auf Messdaten sitzt unten links, die Quantennatur steckt in den Daten. Und die für dieses Kapitel entscheidende vierte: (d) *Bottom-Row-Werkzeuge in Top-Row-Problemen* — Classical Shadows, Bell-Messungen oder Quantenkernel, angewandt auf einen selbst präparierten Zustand, sind Auslese des eigenen Modells. Sie verschieben ein Paper nicht in die untere Reihe.

Wissenschaftlich ist die Trennung wichtig, weil die Vorteilsbehauptungen in den beiden Reihen einen verschiedenen Status haben: unten stehen die *bewiesenen* exponentiellen Separationen inklusive Hardware-Demonstration (Huang et al., Science 2022; $\Theta(n)$ vs. $2^{\Omega(n)}$ Kopien mit/ohne Quantenspeicher); oben sind die Vorteilsbehauptungen historisch fragil — und genau diese Fragilität ist das Thema der beiden Papers.

### 17.2 *Power of Data in Quantum Machine Learning* (Huang et al., Nat. Commun. 2021)

**Was das Paper zeigt.**

- **Die Grundbeobachtung.** Ein Labelgenerator $f(x) = \langle x | U_{\text{QNN}}^\dagger O U_{\text{QNN}} | x \rangle$ kann klassisch nicht berechenbar sein (Proposition 1: ginge es effizient ohne Daten, wäre BPP = BQP) und trotzdem aus Trainingsdaten leicht *lernbar*. Für Amplitudenkodierung ist $f$ eine quadratische Form mit $p^2$ Koeffizienten; $N \propto p^2/\epsilon^2$ Samples genügen einem klassischen Kernelmodell.
- **Komplexitätsklasse BPP/samp** (Appendix B): klassische Algorithmen mit polynomiell vielen gelabelten Samples aus einer samplebaren Verteilung. Es gilt $\mathrm{BPP} \subsetneq \mathrm{BPP/samp} \subseteq \mathrm{P/poly}$ (Adleman-artiges Mehrheitsargument). Daten sind eine eingeschränkte Form von Advice; stammen sie aus BQP, gibt es keine Separation mehr zwischen BPP/samp und BQP.
- **Prediction-Error-Bound.** Für jedes kernelbasierte Modell (explizit oder implizit via Neural Tangent Kernel) gilt $\mathbb{E}_x |h(x) - f(x)| \leq c\sqrt{s_K(N)/N}$ mit der Modellkomplexität $s_K(N) = \sum_{ij} (K^{-1})_{ij}\, \mathrm{Tr}(O^U\rho(x_i))\, \mathrm{Tr}(O^U\rho(x_j)) = \|w\|^2$.
- **Geometrische Differenz.** $g_{12} = \sqrt{\|\sqrt{K_2}K_1^{-1}\sqrt{K_2}\|_\infty}$ liefert $s_{K_1} \leq g_{12}^2\, s_{K_2}$. Für $g_{CQ}$ klein ist klassisches ML *labelunabhängig* garantiert mindestens so gut wie das Quantenmodell — ein funktionsunabhängiger Vortest. Für $g_{CQ}$ groß existiert ein Datensatz, der die Ungleichung saturiert, und er ist konstruktiv (Appendix G: verallgemeinertes Eigenwertproblem, $y = \sqrt{K_Q}v$).
- **Effektive Dimension.** Für den Quantenkernel $\mathrm{Tr}(\rho(x_i)\rho(x_j))$ ist $s_Q \leq \min(d, \mathrm{Tr}(O^2))$ mit $d = \mathrm{rank}(K^Q) \leq N$. Untere Schranke $N \geq \Omega(\mathrm{Tr}(O^2)/\epsilon^2)$ für *jeden* Lerner (Appendix H, Fano + Data Processing) — der Quantenkernel ist dafür optimal, aber $\mathrm{Tr}(O^2)$ ist für Pauli-Observablen exponentiell, also ist $d$ die relevante Größe.
- **Die Krankheit des naiven Quantenkernels.** In exponentiell großem Hilbertraum sind alle Eingaben maximal weit voneinander entfernt, $K^Q \to I$, $d \to N$, $g_{CQ} \to$ klein. Appendix I: eine triviale lineare Funktion $f(x) = 2x_n - \pi$ braucht mit dem Fidelity-Kernel $N \geq (1-\epsilon)2^n$ Samples, mit linearer Regression $n$.
- **Projected Quantum Kernels** als Therapie: den Zustand auf 1-RDMs (oder alle RDM-Ordnungen via Classical Shadows, Appendix J, U-Statistik-Schätzer) zurückprojizieren, dann einen Gauß-Kernel im klassischen Raum bilden. Das erhöht $g_{CQ}$ *statt* es zu senken, bleibt aber klassisch schwer auszuwerten, weil der Weg durch den Hilbertraum führt.
- **Numerik bis 30 Qubits** (fashion-MNIST, PCA-Vektoren; Embeddings E1 separabel, E2 IQP, E3 Heisenberg-Trotter). Auf den ungestellten Datensätzen ist klassisches ML konkurrenzfähig oder besser; nur bei E3 + projiziertem Kernel ein milder Vorteil. Auf engineerten Datensätzen > 20 % Accuracy-Vorsprung bei großem $g$ — robust auch gegen klassische Modelle ohne Kernel (Random Forest, Gradient Boosting).
- **Der Vorteil schrumpft mit $N$** (Fig. 7): Mit wachsender Datenmenge verbessern sich alle Modelle, die Separation verschwindet.
- **Appendix K:** das Diskreter-Logarithmus-Lernproblem von Liu–Arunachalam–Temme wird mit einem projizierten Kernel $k^{PQ}(x_i,x_j) = (\log_g x_i/p)(\log_g x_j/p) + 1$ auf VC-Dimension 3 reduziert — $N = O(\log(1/\epsilon)/\epsilon^2)$, unabhängig von $n$.

**Einordnung.** Obere Reihe, und zwar *auf der Trennlinie zwischen den beiden oberen Zellen*: Das Paper vergleicht klassisches ML (links) mit Quantenkernel/QNN (rechts) und liefert mit $g_{CQ}$ den Schiedsrichter. Alle drei Lackmustests fallen eindeutig aus:

1. Das Unbekannte ist eine klassische Funktion $f: \mathbb{R}^n \to \mathbb{R}$. Dass sie über einen Schaltkreis definiert ist, ändert das Zugriffsmodell nicht — der Lerner sieht Paare $(x_i, y_i)$, nie eine Kopie von $\rho$.
2. Kosten sind $N$ Trainingspunkte, beliebig kopierbar. Die $\Theta(N)$ physikalischen Experimente, die zur *Erzeugung* der Labels nötig wären, sind Datenerhebung, nicht Lernressource.
3. Die Schranken sind $g_{CQ}$, $d$ und $\mathrm{Tr}(O^2)$ — Kernel- und Generalisierungsgrößen. Die einzige informationstheoretische Schranke (Appendix H) ist eine Aussage über Trainingsdatenmenge, nicht über Messzugriff.

**Die Terminologiefalle.** Das Paper nennt seine Testfälle „Dataset (Q, E1/E2/E3)" und spricht von *quantum data sets*. Das sind keine Quantendaten im Sinn der Matrix: Die Eingaben sind klassische PCA-Vektoren, quantenmechanisch ist nur der Labelgenerator. Wer die Matrix mit der paper-internen Sprache abgleicht, landet in der falschen Zeile.

### 17.3 *Exponential Quantum Advantage in Processing Massive Classical Data* (Zhao et al., arXiv 2604.07639, April 2026)

**Was das Paper zeigt.**

- **Das Setting.** Eine Maschine sieht klassische Samples $z$ einzeln (Funktionswerte $(x, f(x))$, Matrixeinträge $(i, j, A_{ij})$, Feature-Label-Paare), verarbeitet jedes einmal, aktualisiert ihren Speicher, verwirft es. Der Datenerzeugungsprozess darf zeitlich driften (Refreshing-Zeit $\tau$, Wiederholungszahl $R$; Sample-Komplexität skaliert linear in $R$). Verglichen wird die *Maschinengröße* — logische Qubits gegen Floating-Point-Zahlen — bei gleicher Prediction-Performance.
- **Theorem 1 (lineare Systeme).** Mit $\tilde O(N)$ Samples löst eine Quantenmaschine der Größe $\mathrm{poly}(\log N)$ die Aufgabe (quadratische Form $\vec x^T M \vec x$ aus gesampelten Einträgen eines dünn besetzten, gut konditionierten $A\vec x = \vec b$), während keine klassische Maschine der Größe $O(N^{0.99})$ das kann; der Exponent 0.99 ist beliebig < 1. Dynamische Variante mit superpolynomialer Separation. Analoge Sätze für Klassifikation und Dimensionsreduktion.
- **Die zweite Schranke.** Klassische Maschinen, die exponentiell größer als die Quantenmaschine, aber unterhalb der nötigen Größe sind, brauchen *superpolynomial* mehr Samples und Zeit.
- **Quantum Oracle Sketching** ersetzt QRAM: Aus dem Sample-Strom wird inkrementell ein approximatives Orakel (State-Preparation-Unitaries für Vektoren, Block-Encodings für Matrizen) aufgebaut. Die Zahl der klassischen Samples skaliert quadratisch mit der Zahl der Quanten-Queries — beweisbar optimal, Ursache ist die Born-Regel. Rauschen und Korrelationen in den Daten werden nativ verkraftet.
- **Interferometric Classical Shadows** (Thm. F.16): Hadamard-Test kombiniert mit Clifford-Shadows, um Vorzeicheninformation zu erhalten und aus dem Quantenzustand ein vollständig *klassisches* Modell zu extrahieren, das beliebig viele dünn besetzte Testpunkte vorhersagen kann.
- **Härte via Größe ↔ Queries.** Für jedes Orakelproblem mit exponentieller klassischer Query-Komplexität, das in polynomiellem Quantenraum mit etwas mehr als quadratischem Query-Vorteil lösbar ist, existiert eine Lernaufgabe auf zufälligen klassischen Samples, bei der jede klassische Maschine exponentiell größer sein muss. Die Schranke ist informationstheoretisch, unbedingt, gilt bei unbegrenzter klassischer Zeit und selbst wenn BPP = BQP.
- **Empirie.** IMDb-Sentiment und PBMC-scRNA-seq: 4–6 Größenordnungen kleinere Maschine als klassische Sparse-Matrix-, QRAM-basierte und Streaming-Algorithmen, mit < 60 logischen Qubits. JAX-Implementierung.
- **Related Work, explizit.** Bisherige rigorose Top-Row-Vorteile beruhten auf „contrived" Aufgaben, in die Quanten- oder Kryptostruktur eingebettet wurde (dort Refs. 20–28); Vorteile auf *Quantendaten* (Refs. 109–115) seien bewiesen, aber zu spezialisiert für den Alltag. Dequantisierung (Tang, Refs. 29–31) reduziere exponentielle auf polynomielle Zeit-Vorteile — aber jede super-quadratische Query-Separation ergebe einen exponentiellen Speichervorteil, weshalb dequantisierte Algorithmen „worth revisiting" seien.

**Einordnung.** Obere Reihe, rechte Zelle. Alle drei Lackmustests eindeutig:

1. Das Unbekannte ist ein klassischer Datenerzeugungsprozess $\mathcal D$ bzw. eine Matrix $A$, ein Vektor $\vec b$.
2. Kosten sind Samples $M$, Maschinengröße, Zeit. „Jedes Sample einmal verarbeitet, dann verworfen" ist eine Streaming-Restriktion, nicht No-Cloning.
3. Holevo taucht auf — aber als *a-priori-Einwand* gegen den Speichervorteil und als Readout-Schranke für den *eigenen* Zustand, nicht als Informationsgrenze gegenüber einem unbekannten Objekt (Abschnitt 12).

### 17.4 Das Verhältnis der beiden Papers

**Dieselbe Reihe, entgegengesetzte Botschaft.** *Power of Data* sagt: Auf klassischen Daten ist ein Prediction-Vorteil fragil; er braucht großes $g_{CQ}$, musste über adversarial engineerte Labels erzwungen werden und verschwindet mit wachsendem $N$. *Massive Classical Data* sagt: Auf denselben klassischen Daten gibt es eine exponentielle, unbedingte, informationstheoretische Separation, auf natürlichen Datensätzen, die mit mehr Daten *nicht* verschwindet. Der scheinbare Widerspruch löst sich in der **Ressourcenachse** auf:

| | *Power of Data* (2021) | *Massive Classical Data* (2026) |
|---|---|---|
| Gemessene Ressource | Prediction-Error bei festem $N$ | Maschinengröße bei fester Prediction-Performance |
| Modell | Batch: Trainingsmenge liegt vor | Streaming: ein Sample nach dem anderen |
| Diskriminator | geometrische Differenz $g_{CQ}$, effektive Dimension $d$ | Output-Dimension; Größe ↔ Query-Komplexität |
| Status der Separation | empirisch (30 Qubits), kernel-theoretisch begründet, auf engineerten Labels | Satz, unbedingt, auf natürlichen Daten (IMDb, PBMC) |
| Verhalten für $N \to \infty$ | Vorteil schrumpft (Fig. 7) | Vorteil bleibt; unterhalb der Größenschwelle superpoly Sample-Bedarf |
| Rolle klassischer Shadows | Projected Quantum Kernel über alle RDM-Ordnungen (Appendix J) | Interferometric Classical Shadows für vorzeichenerhaltende Auslese (Thm. F.16) |
| Rolle kryptographischer Struktur | Appendix K: Diskreter Logarithmus als rigoroser Vorteil | Refs. 20–28: genau diese Konstruktionen als „contrived" abgegrenzt |

**Der direkte Bezug.** Appendix K von *Power of Data* löst das Diskreter-Logarithmus-Lernproblem mit einem projizierten Kernel — ein rigoroser Top-Row-Speedup, aber einer der Klasse „kryptographisch eingebettet". Das 2026er Paper grenzt sich von genau dieser Klasse ab. Die eigene frühere Lösung wird zum Negativbeispiel für das, was man eigentlich sucht: breite, natürliche Aufgaben statt versteckter Falltüren.

**Die schärfste Konsequenz.** Die $N \to \infty$-Konvergenz aus 2021 setzt stillschweigend unbeschränkten klassischen Speicher voraus. Die zweite Schranke aus 2026 zeigt, dass sie unter Speicherbeschränkung nicht gilt: Die klassische Maschine kann die Lücke nicht durch mehr Daten schließen, wenn sie zu klein ist, um das nötige hochdimensionale Objekt zu repräsentieren. Damit ist die Fragilitätsaussage der oberen Reihe präzise skopiert: Sie gilt für die Sample- und die Zeit-Linse, nicht für die Speicher-Linse.

### 17.5 Konsequenzen für die Landkarte und für die Quantum-Learning-Notizen

*Für diese Landkarte* (eingearbeitet in den Abschnitten 1, 4, 10–15):

- Drei Ressourcen statt zwei: Zeit (Rang), Speicher (Output-Dimension), Samples/Prediction (geometrische Differenz).
- Der Auslese-Test aus Abschnitt 4 ist ressourcenrelativ — er beißt beim Zeit-, nicht beim Speichervorteil.
- Die Streaming-Speicher-Zelle hat den Status „unbedingt" (Kernprinzip 3), nicht „kryptografisch bedingt".
- Die Kartengrenze ist über die drei Lackmustests operationalisiert; Classical Shadows als Werkzeug verschieben nichts.
- Drei neue Radar-Punkte (Abschnitt 14).

*Für die Quantum-Learning-Notizen:*

- Die Aussage „Vorteilsbehauptungen in der oberen Zeile sind fragil (Power-of-Data-Linie)" ist zu qualifizieren: fragil sind *Sample-* und *Zeit*-Vorteile. Die Platzachse ist eine eigene Separationsachse mit unbedingter Separation; sie war in der Ressourcentabelle (Abschnitt 4 der Notizen) bisher nur als klassischer Speicher im Decoder-Budget präsent.
- *Power of Data* ist dort unter „Computational Lens: Three Budgets & Hardness" neben Regev, Ji–Liu–Song und Kretschmer einsortiert. Die Härte in diesem Abschnitt ist LWE/PRS; die Härte bei *Power of Data* ist die Klasse BPP/samp und ihre Einbettung zwischen BPP und P/poly. Der natürliche Platz ist Abschnitt 3 der Notizen bei der Daten-vs-Lerner-Matrix, wo das Paper ohnehin als Advantage-Gap-Beleg zitiert wird.
- Die Terminologiefalle „quantum data sets" (17.2) sollte als vierte Grauzone neben engineerte Zustände, Simulatoren und hybride Decoder in die Notizen aufgenommen werden.
