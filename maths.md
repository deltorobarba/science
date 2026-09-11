# <font color="blue">**Mathematics**

![science](https://raw.githubusercontent.com/deltorobarba/science/main/science.JPG)

## Quantum Learning

<font color="blue">**Learning from Quantum Experiments**

1. *Wie hängen Quantenmessung und Quantum Learning zusammen?*

* Die kürzeste Fassung: Lerntheorie ist die Ressourcentheorie, die auf der Messtheorie aufsetzt.
  * Die **Messtheorie** (deine Teile I–II) beantwortet die Einzelschuss-Frage: Was tut eine Messung mit einem Zustand, welche Statistik erzeugt sie?
  * Die **Lerntheorie** stellt die inverse, statistische Frage: *Was lässt sich aus vielen Messungen über ein unbekanntes ρ herausfinden — und zu welchen Kosten, optimal?*
* Die Born-Regel verwandelt den Zustand in ein Sampling-Orakel; Lernen ist das Inversproblem dazu.

2. *Begriffsklärung: die Datenquelle entscheidet, nicht die Hardware*

* **Learning from quantum experiments** ist die Disziplin, die fragt: Gegeben Zugriff auf Kopien eines unbekannten Quantensystems — eines Zustands $\rho$, eines Prozesses/Kanals $\mathcal{E}$, einer Dynamik —, erzeugt von der Natur, einem Sensor oder einem Quantengerät: *welche* Eigenschaften kann ein Lerner extrahieren, zu *welchen* Kosten in Kopien, klassischer Zeit und klassischem Speicher, und wie verändern Quantenressourcen (Quantenspeicher, verschränkte Messungen, Adaptivität) diese Kosten?
* *What properties of unknown state $\rho$, channel $\mathcal{E}$, Hamiltonian $H$ can be learned from physical copies — and at what Pareto-optimal budget in copies, classical runtime, and quantum memory?*

3. *Differentiations by Data and Learners*

* The quantum learing from experiments is strictly the **bottom row** of the data-vs-learner matrix (quantum data):

| | Classical Learners | Quantum Enhanced Learners |
| --- | --- | --- |
| **klassische Daten** | klassisches ML | „QML on classical data": Feature Maps, <br>variationelle Klassifikatoren, Quantum Kernels |
| **Quantendaten** <br>(Kopien von $\rho$ / Kanälen) | **Messprotokoll + klassische Statistik: <br>Shadows, Bell-Sampling + classical decoders** | Quantenspeicher-Protokolle (Quantum Memory): <br>Coherent two/multi-copy / quantum memory protocols |

* **Scope criteria:** The unknown is a physical quantum object; sample budget (copy count) is a physical constraint bounded by no-cloning and Holevo.
* **Advantage gap (Power of Data):** Advantage on classical data (top row) is fragile — with sufficient classical data, classical ML matches quantum models on classical tasks (*Huang et al., Nat. Commun. 2021*); provable exponential separations exist natively on quantum data (bottom row).
* **Abgrenzung nach oben (klassische Daten auf Quantenhardware).** Finanzdaten per Feature Map in einen Schaltkreis laden, prozessieren, auslesen ist *nicht* learning from quantum experiments: Das Unbekannte ist eine klassische Funktion bzw. Verteilung; der Quantencomputer ist Rechensubstrat, kein Untersuchungsgegenstand; die Messung am Ende ist Auslese des eigenen Modells, kein Experiment an einem unbekannten System. Drei Lackmustests trennen scharf:
  1. **Wo lebt da Unbekannte?** Dichteoperator/Kanal ↔ klassischer Datensatz.
  2. **Ist „Anzahl der Kopien" eine sinnvolle Kostengröße?** Quantendaten sind nicht klonbar — jede Kopie kostet; klassische Daten sind beliebig kopierbar — die Frage ist sinnlos.
  3. **Binden die Informationsgrenzen aus Abschnitt 8?** No-Cloning, Holevo und Gentle Measurement sind genau das, was Lernen aus Quantendaten nichttrivial macht; auf ein CSV-File greifen sie nicht.
* Wissenschaftlich ist die Trennung wichtig: In der oberen Zeile sind Vorteilsbehauptungen fragil (die „Power of data"-Linie: **klassisches ML mit ausreichend Trainingsdaten holt Quantenmodelle auf klassischen Aufgaben häufig ein)**, in der unteren Zeile stehen die *bewiesenen* exponentiellen Separationen — inklusive Hardware-Demonstration.
* **Grauzonen, sauber aufgelöst.**
  * (a) *Engineerte Zustände:* Ob $\rho$ von einem Molekül oder einem Quantenprozessor präpariert wurde, ist dem Feld gleichgültig — entscheidend ist, dass das Unbekannte ein Quantenobjekt ist, auf das nur per Messung zugegriffen wird. Gerätecharakterisierung, Rauschlernen und Kalibrierung sind daher nativ Teil des Feldes.
  * (b) *Simulatoren:* Läuft das Experiment auf einem klassischen Simulator (wie im eigenen Projekt), bleibt das *Zugriffsmodell* das eines Quantenexperiments — i.i.d.-Messoutcomes, Kopien als Kosten; die Sample-Komplexität ist die simulator-invariante Größe.
  * (c) *Hybride:* Ein klassisches neuronales Netz, das Quantenmessdaten dekodiert, sitzt unten links — die Quantennatur steckt in den Daten, nicht im Lerner.


4. *Differentiations by Ressources*

* Die Protokolle ordnen sich entlang weniger Achsen, auf denen die bewiesenen Separationen leben:

| Axis | Spectrum | Key Separation / Benchmark |
| --- | --- | --- |
| **Quantum Memory** | $1 \to 2 \to k$ copies coherent | Pauli spectrum: $\Theta(n)$ copies (2-copy) vs. $2^{\Omega(n)}$ (1-copy) |
| **Adaptivity** | Fixed $\leftrightarrow$ Dynamic settings | Exponential sample savings for non-local property testing |
| **Conjugate Access** | $\rho$ only $\leftrightarrow (\rho, \rho^*)$ | Clean spectrum $\mathrm{Tr}(P\rho)^2$ via conjugate pairs; constant memory |
| **Budgets** | Samples / Time / Memory | Sample-efficient with exponential classical decoders is the default |
| **Data Access** | i.i.d. draws $\leftrightarrow$ Active queries | LWE-hardness: states can be sample-learnable but computationally hidden |

* Die letzten beiden Achsen markieren die aktuelle Front des Feldes: Fast alle klassischen Separationen sind *Sample*-Aussagen („mit Quantenspeicher braucht man exponentiell weniger Kopien"); die Frage, ob die gewonnenen Daten auch *effizient verarbeitbar* sind, ist deutlich weniger kartiert.
* Die Sample-vs-Query-Lücke ist dabei keine technische, sondern eine fundamentale: Es existiert (unter Standard-Kryptoannahmen) keine generische Konversion — Zustände können ein dünnes, weit über dem Rauschboden liegendes Spektrum tragen und trotzdem rechnerisch versteckt sein.
* Zusatztabelle aus anderen Notizen:

| Zugriffstyp | Status bei LWE | Ursache |
| --- | --- | --- |
| **Sampling Access** | **Hard (Post-Quantum)** | Keine Kontrolle über $\mathbf{a}_i$; algebraische Eliminationen führen zur<br> **Fehleranhäufung**, die das Signal zerstört. |
| **Query Access (Superposition)** | **Easy (BDP / Bernstein-Vazirani / QFT)** | Gezielte Superpositionen ermöglichen Interferenz via QFT; <br>keine algebraische Zeilenreduktion nötig, Rauschen bleibt isoliert. |

<br>

5. *Differentiations by Task: Tomography vs Strukturlernen*

* Die Aufgaben des Feldes trennt am schärfsten die Rolle der Observablen (vgl. Tabelle in Teil V):
  * Basis: **Full Tomography**: „Gib mir alle d² Parameter von ρ." Wie das komplette Genom sequenzieren. Danach kannst du jede beliebige Frage rechnerisch beantworten, ohne nochmal ins Labor zu gehen.
  * **Schätzen** (Observablen sind *Eingabe* — **Shadow-Tomographie**, Classical Shadows) Gib mir die Werte dieser M vorgegebenen Observablen." Wie ein Panel von 500 vordefinierten SNPs testen. Die Fragen stehen vorher fest. VERSUS
  * **Suchen** (Observablen sind *Ausgabe* — **Struktur-Lernen**: erst den Träger des dünnen Spektrums finden, dann die Werte). „Finde heraus, welche Observablen überhaupt relevant sind, und gib mir deren Werte." Wie eine GWAS: Du weißt vorher nicht, welche Marker etwas bedeuten.
* Die Suchaufgabe ist echt schwerer: Die Schätz-Garantien decken sie nicht, und auf ihr sitzt die LWE-Härte.


| Task | Observables | Target Output | Sample Complexity ($n$ qubits, $d=2^n$) |
| --- | --- | --- | --- |
| **Full QST** | All | Full density matrix $\rho$ | $\Theta(d^2/\epsilon^2)$ (entangled) / $\Theta(d^3/\epsilon^2)$ (single-copy) |
| **Shadow Tomography** | Input list ($M$ given) | $M$ expectation values $\mathrm{Tr}(O_i\rho)$ | $\mathrm{poly}(\log M, n, 1/\epsilon)$ |
| **Classical Shadows** | Chosen post-measurement | Arbitrary small shadow-norm $\langle O\rangle$ | $O(\log M \cdot 3^k/\epsilon^2)$ for $k$-local Paulis |
| **Bell / Pauli Sampling** | Sampled dynamically | Draws $P \sim \vert{}\langle\bar\psi\vert{}P\vert{}\psi\rangle\vert{}^2/2^n$ | $O(n)$ two-copy shots (stabilizer support) |
| **Structure Learning** | Discovered (output) | Support + values of sparse spectrum | $\mathrm{poly}(n)$ samples; classical decoding often hard |
| **State Discrimination** | 2 candidates $(\rho_0, \rho_1)$ | Identity index (Helstrom / USD) | Helstrom (min error) vs. USD (zero error + abort) |
| **Hypothesen-Selektion** | Liste gegeben | ein Index | $O(\log M)$ Kopien |

Drei Auflösungsstufen:
- **Feld:** Learning from quantum experiments — Quantenvorteile beim Lernen physikalischer Systeme aus Messdaten, mit Fokus auf minimalem Quantenspeicher (nie mehr als zwei Kopien).
- **Ansatz (die eigene Signatur):** *Machine-learned decoders for quantum measurement data* — ein trainiertes Modell ersetzt die handgebaute Kombinatorik (Graph-Coloring, Matrix Multiplicative Weights) und nutzt die Struktur der Zustandsklasse, um unter Worst-Case-Komplexität zu operieren. Diese Idee ist nicht an Displacement-Operatoren gebunden; sie überträgt sich auf Hamiltonian Learning, Rauschcharakterisierung, Fehlerkorrektur-Decoder.
- **Beitrag:** Computationally efficient **structure learning** dünner Displacement-Spektren aus Zwei-Kopien-Bell-Messungen — triply efficient (Samples, Zeit, Speicher simultan polylogarithmisch), als Promise-Problem gestellt, mit beweisbaren Instanzen (Dictionary-, Subgruppen-Klassen) und beweisbarer Grenze (LWE-Härte der generischen Lokalisierung).
- **Summary:** Strukturell zerfällt jedes solche Protokoll in *Quantenfrontend* (welche Messung auf wie vielen Kopien) und *klassischen Decoder* (welcher Schätzer auf den Outcomes) — und der End-to-End-Fehler faktorisiert entsprechend in Lokalisierung und Schätzung. Das Projekt besetzt beide Hälften mit je einem nichttrivialen Baustein: konjugierte Bell-Paare vorn, gelernter CNN-Decoder plus sequentieller Vorzeichen-Integrator hinten.

**Auswertungs- und Lernprotokolle (Quantum Learning!)**
* Alles in diesem Teil sind *Protokolle über Messungen*, keine neuen Messtypen:
* Sie kombinieren die Primitiven mit klassischer Nachverarbeitung, um Fragen über $\rho$ zu beantworten.
* Die lerntheoretische Sicht sortiert sie entlang zweier Ressourcenachsen: **wie viele Kopien pro Schuss kohärent verarbeitet werden** ($1, 2, k$ — "Quantenspeicher") und **ob die Observablen Eingabe oder Ausgabe** des Protokolls sind (Schätzen vs. Suchen).

6. *Fünf Mehrwerte von Strukturlernen*

**Kernregel:** Die Pipeline liefert nie eine bestellte Observable, immer nur „die stärksten Stellen". Nützlich ist sie dort, wo die **Art** der Antwort vorher bekannt ist, aber nicht die **Adresse**. Struktureller Prior ja, Koordinaten-Prior nein. Fehlt der strukturelle Prior, ist das Ergebnis tatsächlich ein Überraschungsei.

* **1. Hamiltonian-Lernen** (wissenschaftlich stärkster Fall). Hier ist H *unbekannt*. Bei nicht zu kalter Temperatur: ρ_β ≈ (1/d)(1 − βH), also **y_u ∝ h_u** mit Faktor −β/d. Der Träger des Zustands ist der Träger von H; die Rangfolge der |y_u| ist die Rangfolge der Kopplungsstärken; das Vorzeichen sagt ferro/antiferro. β geht nur als Gesamtfaktor ein → relative Kopplungen ohne Temperaturkenntnis. Zweite Ordnung: Kombinationstöne auf Summen u+v. Der Kompromiss: heiß = treu aber unter dem Rauschboden (M4/P2), kalt = groß aber nichtlinear; βΔE = 2,5 ist die Mitte → **physikalische Motivation der Gibbs-Klasse über „realistischer Testfall" hinaus**. Abgrenzung zur Literatur (Anshu et al., Haah et al.): Die setzen den Träger als bekannt voraus (Regime 1) und suchen nur Koeffizienten. Struktur-Lernen ist die Stufe darüber. Bild: Kommunikationsmuster im Ruhezustand = Organigramm.

* **2. Verifikation, nicht Entdeckung.** Sollzustand bekannt, Istzustand gemessen. Fidelity ist eine Prüfsumme (verändert ja/nein), Struktur-Lernen ist ein Diff. Drei Befunde: alles ok / erwartete Linie fehlt (Dekohärenz) / **unerwartete Linie da** (kohärenter Fehler). Der dritte Fall ist für Listen-basierte Methoden prinzipiell unerreichbar. Die Adresse der Überraschung ist diagnostisch, weil Hardwarefehler selbst strukturiert sind (Crosstalk → ZZ auf dem Paar, Über-Rotation → bestimmte Leckage). Vgl. Hangleiter–Gullans. Fehlende Linien nutzen die *bewiesene* Hälfte der Pipeline (nur Präzision nötig), zusätzliche Linien die vermutete.

* **3. Die Form des Supports.** Symplektische Constraint (lem:symplecticconstraint): D_v ρ D_v† = ρ ⟹ Träger ⊆ S(ρ)^⊥. Ein Träger, der in einem Komplement liegt, *ist* eine entdeckte Symmetrie/Erhaltungsgröße. Flaches Plateau auf einer Untergruppe ⟹ Stabilizer-Zustand, Untergruppe = Stabilisatorgruppe (Montanaro, fällt als Nebenprodukt ab). Kohärenz-Lesart: y_{q,p} = Σ_k ω^{pk} ρ_{k,k+q}, also q = Abstand zur Diagonalen, p = Fourier-Index darauf. Alles bei q=0 ⟹ klassisches Gemisch; Signal bei q≠0 ⟹ zertifizierte Kohärenz. Gewichtsprofil ⟹ Lokalität ohne Vorannahme.

* **4. Leere Antwort als Ergebnis.** Parseval: Σ|y_u|² = d·Tr(ρ²), die Masse kann nicht verschwinden, nur verteilt werden. Mit einem Reinheitstest (SWAP, gleiche Hardware) unterscheidbar: Tr(ρ²) klein ⟹ gemischt/thermisch; Tr(ρ²) ≈ 1 ⟹ **gescrambelt**, alles bei |y| ~ 1/√d. Letzteres ist die Thermalisierungs-Signatur (ETH vs. integrabel vs. MBL). Dritter Fall, ehrlich zu nennen: M6/LWE — Struktur da, rechnerisch versteckt, von außen ununterscheidbar. Deshalb heißt das Ergebnis korrekt „nichts gefunden", nicht „nichts da".

* **5. Der blinde Fleck gezielter Methoden.** Classical Shadows treffen einen Pauli-String vom Gewicht w nur mit Wahrscheinlichkeit 3^{−w} → 3^w/ε² Schüsse. Untere Schranke (Chen–Cotler–Huang–Li): *jedes* Einzelkopie-Protokoll braucht 2^{Ω(n)}, mit zwei Kopien genügen Θ(n). **Präzise Abgrenzung:** Für einen *bekannten* globalen Korrelator gilt das nicht (gezielte Basisrotation, O(1/ε²), gewichtsunabhängig). Die Schranke beißt genau im Schnittpunkt **global × unbekannte Lage**. Physikalische Beispiele: String-Ordnung der Haldane-Phase, Wilson-Schleifen, makroskopische Superpositionen mit unbekanntem Paar, unbekannte Symmetriesektoren.


<font color="blue">**Typen von Lernprotokollen für Quantum Experiments**


1. **Estimating: Tomography to Triple Efficiency (Observables as Input)**

* **Full QST:** Reconstructs all $d^2$ parameters; bounded by $\Theta(d^2/\epsilon^2)$ (entangled) or $\Theta(d^3/\epsilon^2)$ (single-copy).
* **Shadow Tomography:** Predicts $M$ target observables via gentle measurement / threshold search in $\mathrm{poly}(\log M)$ copies; compute- and memory-intensive.
* **Classical Shadows (HKP):** Snapshot state $\hat\rho = \mathcal{M}^{-1}(U^\dagger\vert{}b\rangle\langle b\vert{}U)$ under random Clifford/Pauli unitaries; predicts $M$ properties offline via median-of-means in $O(\log M \cdot 3^k/\epsilon^2)$ single-copy shots.
* **Triple Efficiency:** Achieving sample *and* time efficiency using only $O(1)$-copy quantum memory.
* *Key Literature:*
  * **Haah et al. / O'Donnell–Wright (STOC 2016):** $\Theta(d^2/\epsilon^2)$ optimal entangled tomography baseline.
  * **Aaronson (STOC 2018):** Shadow tomography formulation via gentle measurements ($\tilde{O}(\log^4 M)$ copies).
  * **Huang, Kueng, Preskill (Nat. Phys. 2020):** Classical shadows framework for offline property estimation.
  * **Chen et al. (2022):** $\Theta(d^3/\epsilon^2)$ single-copy lower bound proving the entangled-measurement gap.
  * **King, Gosset, Kothari, Babbush (2024):** Triply efficient shadow tomography for local fermionic & Pauli observables.

2. **Quantum Memory, Conjugate Access & Adaptivity**

* **Two-copy mechanism:** Measuring across $\rho^{\otimes 2}$ in the $2n$-qubit Bell basis $\{(P\otimes\mathbb{1})\vert{}\Phi^+\rangle^{\otimes n}\}$ samples Pauli strings $P$ globally from a single shot.
* **Conjugate pairs:** Access to $(\rho, \rho^*)$ isolates the clean product spectrum $\mathrm{Tr}(P\rho)^2/2^n$ with constant quantum memory.
* **Memory hierarchy:** Most exponential advantage arrives at $k=2$ copies; single-copy strategies require $2^{\Omega(n)}$ shots for identical global tasks.
* *Key Literature:*
  * **Bubeck, Chen, Li (FOCS 2020):** Entanglement necessary for optimal quantum property testing.
  * **Chen, Cotler, Huang, Li (FOCS 2021):** $\Theta(n)$ vs. $2^{\Omega(n)}$ exponential separation with quantum memory.
  * **Huang et al. (Science 2022):** Flagship theoretical separations and Sycamore 40-qubit hardware demo.
  * **King, Wan, McClean (2024):** Exponential advantage via $(\rho, \rho^*)$ conjugate access with constant memory.
  * **Chen, Gong, Zhang (2024):** Exponential separations proven for adaptive multi-copy shadow tomography.

3. **Searching: Structure Learning & Agnostic Tomography (Observables as Output)**

* **Task:** Discover the unknown sparse support of $\rho$ before estimating values (analogous to graphical model learning).
* **Computational barrier:** While Bell sampling easily concentrates draws onto the support, reconstructing the generators without active queries is generically cryptographically hard (LWE-type). Subgroup/stabilizer symmetries form the primary tractable exception.
* *Key Literature:*
  * **Montanaro (2017):** Learning stabilizer states from $O(n)$ Bell samples via linear algebra.
  * **Grewal, Iyer, Kretschmer, Liang (2023):** Bell difference sampling and learning states with few non-Clifford gates.
  * **Hangleiter, Gullans (PRL 2024):** Bell sampling as a universal diagnostic framework for quantum circuits.

4. **Computational Lens: Three Budgets & Hardness**

* **Budget decoupling:** Copy complexity, classical time, and quantum memory scale independently. Sample-efficient protocols routinely hit exponential classical decoding barriers.
* **Pseudorandomness:** Pseudorandom states (PRS) prove that quantum states can be statistically learnable yet computationally indistinguishable from Haar-random states.
* *Key Literature:*
  * **Regev (2005):** Learning With Errors (LWE) — bedrock for average-case classical learning hardness.
  * **Ji, Liu, Song (CRYPTO 2018):** Formulation of pseudorandom quantum states (PRS).
  * **Kretschmer (TQC 2021):** Connecting quantum pseudorandomness to classical learning hardness.
  * **Huang, Broughton et al. (Nat. Commun. 2021):** *Power of data in quantum machine learning* — proves that access to classical data closes potential quantum speedups for learning classical functions, delineating classical vs. quantum data advantages.

5. **Learning Dynamics: Hamiltonians, Channels & Circuits**

* **Hamiltonians:** Learning unknown terms and coupling graphs from thermal Gibbs states or real-time dynamics up to the Heisenberg limit.
* **Circuits & Channels:** Bounding Pauli channel noise; learning constant-depth shallow circuits in polynomial time.
* *Key Literature:*
  * **Flammia, Wallman (TQC 2020):** Efficient Pauli channel estimation protocols.
  * **Anshu et al. (Nat. Phys. 2021) / Haah et al. (FOCS 2022):** Optimal sample complexity for Gibbs-state Hamiltonian learning.
  * **Huang et al. (PRL 2023):** Heisenberg-limited Hamiltonian learning from real-time evolution.
  * **Huang et al. (STOC 2024):** Polynomial-time reconstruction of shallow quantum circuits.

6. **Machine-Learned Decoders (ML on Quantum Data)**

* **Role:** Classical neural decoders processing shadow data (bottom-left matrix quadrant) act as empirical heuristics for classically hard decoding tasks.
* *Key Literature:*
  * **Torlai et al. (Nat. Phys. 2018):** Neural-network quantum state tomography.
  * **Huang, Kueng, Torlai, Albert, Preskill (Science 2022):** Provable generalization bounds for classical ML trained on quantum shadow data.
  * **Huang, Preskill, Soleimanifar (2024):** Rigorous state certification via single-qubit shadow relaxations.

7. **Surveys & Timeline**

* **Anshu, Arunachalam (Nat. Rev. Phys. 2024):** Canonical survey on state learning complexity.
* **Gebhart et al. (Nat. Rev. Phys. 2023):** Comprehensive review on learning quantum dynamics in experimental setups.
* **Arunachalam, de Wolf (SIGACT 2017):** Foundational survey on quantum PAC learning.
* **1998–2007:** Quantum PAC foundations (Bshouty–Jackson) · LWE (Regev) · State PAC learnability (Aaronson)
* **2016:** Sample-optimal full tomography baseline $\Theta(d^2/\epsilon^2)$ (Haah et al.; O'Donnell–Wright)
* **2017–2018:** Shadow tomography (Aaronson) · Stabilizer Bell sampling (Montanaro) · PRS (Ji–Liu–Song)
* **2020:** Classical shadows (HKP) · Entanglement lower bounds (Bubeck–Chen–Li)
* **2021–2022:** Flagship memory separations (Chen et al.) · Sycamore demo (Science 2022) · Shallow circuit learning
* **2023–2024:** Heisenberg Hamiltonian learning · Triply efficient shadows · Conjugate-pair advantages · Agnostic tomography
* **2025–mid 2026:** Agnostic tomography consolidation · Noise-robust 2-copy hardware protocols · Physical average-case decodability

8. **Open Frontiers**

* **Tractable Islands:** Delineating the boundary between subgroup-tractable classes and cryptographically hard spectra under varying noise: **Kartierung der dekodierbaren Klassen - Zwischen „Subgruppen-leicht" (lineare Algebra) und „LWE-hart" liegt ein unvermessenes Gebiet**; derselbe Zustand wandert durch bloßes Aufdrehen eines Rauschparameters vom leichten ins harte Regime — ein Übergang, der nach systematischer Vermessung verlangt. Offen ist auch, ob die Härte-Reduktion von der Tensor-Produkt-Basis auf die zyklische Ein-Qudit-Basis übertragbar ist.
* **Was gelernte Decoder implizit finden.** Funktioniert ein trainierter Decoder auf einer Klasse ohne bekannten effizienten Algorithmus, hat er möglicherweise einen gefunden — ML als Werkzeug der Algorithmen-Entdeckung, mit der offenen Frage nach einer Metrik, die Generalisierung über Zustandsverteilungen vorhersagt.
* **Hardware-Realistic Multi-Copy:** Scaling 2-copy protocols under realistic preparation, crosstalk, and measurement noise. - **Konstanter Quantenspeicher und Hardware-Realismus.** Wie weit trägt die Zwei-Kopien-Disziplin? Approximate matched filters (Probe-Gain $\kappa < 1$, Mehrkosten $\kappa^{-2}$) machen die Protokolle graceful gegenüber Präparationsfehlern — die praktisch relevanteste Achse für Geräte der nächsten Jahre.
* **Average-Case Physics:** Replacing adversarial worst-case cryptography bounds with physically natural ground-state priors. - **Average-Case statt Worst-Case.** Die Härte-Resultate sind adversarial; natürlich vorkommende Zustände (Grundzustände lokaler Hamiltonians, thermische Zustände) könnten generisch dekodierbar sein — der Übergang von der Kryptographie-Perspektive zur Physik-Perspektive auf dieselbe Frage.

<font color="blue">**Entwicklung der Lernprotokolle für Quantum Experiments**


1. Zustandsdiskriminierung: Helstrom vs. USD

Gegeben eine von zwei bekannten Präparationen $\rho_0, \rho_1$ (a priori $p_0, p_1$) — welche liegt vor? Da nicht-orthogonale Zustände nicht perfekt unterscheidbar sind (Abschnitt 4), gibt es zwei kanonische Strategien mit unterschiedlichem Fehlerbegriff:

**Helstrom-Messung (Minimum-Error).** Erzwinge eine Antwort in jedem Durchlauf und minimiere den *mittleren Fehler*. Die optimale Messung ist eine projektive Messung auf das Vorzeichenspektrum von $p_0\rho_0 - p_1\rho_1$, mit der Helstrom-Schranke

$$P_{\text{err}}^{\min} = \frac{1}{2}\Big(1 - \big\|p_0\rho_0 - p_1\rho_1\big\|_1\Big),$$

für reine Zustände mit gleichen Prioren $P_{\text{err}}^{\min} = \frac{1}{2}\big(1 - \sqrt{1 - |\langle\psi_0|\psi_1\rangle|^2}\big)$. Funktioniert für reine *und* gemischte Zustände — das Standardverfahren, wenn Fehler tolerierbar, Enthaltung aber nicht.

**Unambiguous State Discrimination (USD).** Erlaube einen dritten Ausgang "unentschieden" und verlange, dass die entschiedenen Antworten *nie* falsch sind. Für nicht-orthogonale Zustände erzwingt das eine echte POVM (drei Effekte auf einem Qubit — mit Projektoren unmöglich); der Preis ist die Enthaltungswahrscheinlichkeit, minimal $|\langle\psi_0|\psi_1\rangle|$ bei gleichen Prioren. Fehlerfreiheit gegen Auskunftsverweigerung — die komplementäre Währung zu Helstrom.

2. Tomographie: die exponentielle Basislinie

**Quantum State Tomography (QST)** rekonstruiert alle $d^2$ Parameter von $\rho$ aus einem *informationsvollständigen* Messsatz. Bei DV: alle $3^n$ Pauli-Basen (rotate-then-read in jeder Kombination) oder eine einzige SIC-POVM. Bei CV: Homodyn-Messungen der Quadratur-Randverteilungen $p(x_\theta)$ über einen Scan der LO-Phase $\theta$, aus denen die **Wigner-Funktion** $W(x,p)$ per inverser Radon-Transformation rekonstruiert wird (die Heterodyn-Statistik liefert direkt die glattere $Q$-Funktion). Die Sample-Komplexität ist das Problem: $\Theta(d^2/\epsilon^2) = \Theta(4^n/\epsilon^2)$ Kopien *selbst mit* kollektiven (verschränkten) Messungen über viele Kopien — exponentiell in $n$. Alles Weitere in diesem Teil existiert, um dieser Skalierung zu entkommen, wenn man gar nicht ganz $\rho$ braucht.

3. Shadow-Tomographie und Classical Shadows

**Shadow-Tomographie (Aaronson).** Aufgabenstellung: Gegeben $M$ Zwei-Ausgangs-Observablen, gib alle $\mathrm{Tr}(E_i\rho)$ auf $\pm\epsilon$ genau aus — mit nur $\mathrm{poly}(\log M, n, 1/\epsilon)$ Kopien, wobei $M$ exponentiell sein darf. Der Motor ist das Gentle-Measurement-Lemma (Abschnitt 6): Jede fast-deterministische Schätzung beschädigt den Zustand nur $O(\sqrt{\epsilon})$, also können *dieselben* Kopien viele Fragen beantworten. Sample-effizient — aber die Originalprotokolle sind rechenintensiv und brauchen großen kohärenten Quantenspeicher: Die drei Budgets (Kopien / Zeit / Speicher) fallen hier auseinander.

**Classical Shadows (Huang–Kueng–Preskill): "randomisiere zuerst, frage später".** Pro Kopie: zufälliges $U$ ziehen (zufällige Pauli-Basis pro Qubit oder zufälliger Clifford), messen, den klassischen Schnappschuss

$$\hat\rho = \mathcal{M}^{-1}\big(U^\dagger|b\rangle\langle b|U\big)$$

speichern. Der invertierte Messkanal $\mathcal{M}^{-1}$ (für zufällige Pauli-Basen pro Qubit: $\hat\rho_q = 3\,U^\dagger|b\rangle\langle b|U - \mathbb{1}$) macht den Schätzer unverzerrt, $\mathbb{E}[\hat\rho] = \rho$ — Schüsse in der "falschen" Basis mitteln sich heraus. *Danach* beliebige Observablen mit kleiner Shadow-Norm per Median-of-Means schätzen: $O(\log M \cdot 3^k/\epsilon^2)$ Schüsse für $k$-lokale Paulis (Pauli-Ensemble), $O(\mathrm{Tr}\,O^2)$-artige Kosten für Fidelitäten (Clifford-Ensemble). Single-copy, kein Quantenspeicher, NISQ-tauglich — der Arbeitsgaul der Praxis. Die Lücke: *globale* Observablen ($k \sim n$, z. B. beliebige Pauli-Strings) kosten $3^n$ Schüsse — exponentiell. Genau diese Lücke schließen Zwei-Kopien-Messungen.

4. Zwei-Kopien-Messungen: Bell-Sampling, konjugierte Paare, Struktur-Lernen

**Mechanismus.** Die $2n$-Qubit-Bell-Basis $\{(P\otimes\mathbb{1})|\Phi^+\rangle^{\otimes n}\}$ ist die gemeinsame Eigenbasis aller kommutierenden Operatoren $P\otimes\bar P$ (mit $\bar P$ der komplex konjugierten Pauli). Eine transversale Bell-Messung (BSM auf jedem Qubit-Paar) über *zwei Kopien* des Zustands zieht daher pro Schuss einen Pauli-String

$$P \;\sim\; \frac{|\langle\bar\psi|P|\psi\rangle|^2}{2^n}$$

— ein einziger Schuss trägt Information über das *gesamte* Pauli-Spektrum gleichzeitig. **Subtilität der konjugierten Paare:** Auf $\psi\otimes\psi$ sampelt man gegen den *konjugierten* Zustand $\bar\psi$; das saubere Spektrum $\mathrm{Tr}(P\rho)^2/2^n$ erfordert das Paar $(\rho, \bar\rho)$. Für Zustände mit reellen Amplituden fallen beide zusammen (weshalb Demos gern GHZ-Zustände nehmen).

**Konsequenzen.** Reinheit und Überlapp $\mathrm{Tr}(\rho\sigma)$ via Zwei-Kopien-(SWAP-Typ-)Tests — der direkte Messzugang zur Rein/Gemischt-Frage aus Abschnitt 2, ohne Tomographie. Stabilizer-Zustände sind aus $O(n)$ Bell-Samples lernbar (Montanaro). Und vor allem: **Pauli-Shadow-Tomographie mit $\Theta(n)$ Kopien bei Zwei-Kopien-Speicher vs. $2^{\Omega(n)}$ ohne** (Huang–Kueng–Preskill; Chen–Cotler–Huang–Li) — eine der stärksten *bewiesenen* exponentiellen Quantenvorteile, bereits in Hardware demonstriert. Zwei ist der Sweet Spot: Die Ressourcenachse läuft single-copy → two-copy → $k$-copy, und fast der gesamte bekannte Gewinn kommt schon bei 2.

**Struktur-Lernen: Observablen als *Ausgabe*.** Aufgabeninversion — nicht *gegebene* Observablen schätzen, sondern erst die wenigen Observablen *finden*, die die Struktur tragen (den Support eines dünn besetzten Pauli-/Verschiebungsspektrums), dann deren Werte schätzen (erst die Kanten, dann die Gewichte, wie beim Lernen graphischer Modelle). Das Sampling ist die leichte Hälfte: Bell-/Pauli-Sampling konzentriert die Züge genau auf den Support, wenige dominante Strings tauchen nach polynomial vielen Schüssen auf. **Die Decodierung ist die harte Hälfte:** i.i.d.-Samples in den Support zu verwandeln ist Sparse Recovery *ohne wählbare Queries* — und diese Sample-vs-Query-Lücke kann rechnerisch hart sein (LWE-artige Härte), außer auf strukturierten Promise-Klassen (Untergruppen-/Stabilizer-artig → effiziente Decoder). Daher die Disziplin: **immer drei Budgets getrennt angeben** — Kopien (Sample-Komplexität), klassische Zeit, klassischer Speicher. Sample-effiziente Protokolle mit exponentiellen Decodern sind die Norm; dreifache Effizienz ist die Ausnahme.

## <font color="blue">Heisenberg-Weyl

<font color="blue">**Physics: Quantum Operators from Quantum Harmonic Oscillator (via Exponentiation of Generators $\hat{Q}$, $\hat{P}$ and its Degree)**</font>

![Quantum Harmonic Oscillator](https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/HarmOsziFunktionen.png/330px-HarmOsziFunktionen.png)

<font color="blue">***Quantum Harmonic Oscillator*** *and the Hamiltonian $\hat{H}$*</font>

* $\hat{H} \propto \hat{P}^2 + \hat{Q}^2 = \hbar\omega\left(\hat{a}^\dagger\hat{a} + \tfrac12\right) = \hbar\omega(\hat n + \tfrac12)$ — generator of basis-state rotations in phase space ($Q/P$).
* **Why the harmonic oscillator is *the* starting point** — two reasons, both structural:
  * **Analytically:** every smooth potential near a minimum is quadratic to leading order (Taylor), so the QHO is the universal local model of any bound system.
  * **Algebraically:** $\hat Q^2 + \hat P^2$ is *the* canonical degree-2 element of the Weyl algebra — the same $\mathrm{Sym}^2V\cong\mathfrak{sp}$ that appeared as the symmetry algebra of the bosonic branch above. It is the bosonic counterpart of the Dirac operator on the fermionic side. Everything below is this one generator, read at different degrees.
* **Ladder-operator form** $\hat H = \hbar\omega(a^\dagger a + \tfrac12)$: $\hat a,\hat a^\dagger$ jump down and up the energy ladder; $\hat Q,\hat P$ are linear combinations of them, and their sum of squares gives the number operator $\hat n$ (total energy).
* **Position/momentum form** $\hat H = \frac{p^2}{2m} + \frac12 m\omega^2x^2$: the [QHO](https://en.wikipedia.org/wiki/Quantum_harmonic_oscillator) describes the physical swap kinetic $\leftrightarrow$ potential = time evolution. At $t = 0$ the state sits in position $Q$; after $t = \frac{\pi}{2\omega}$ it has rotated $90°$ into momentum $P$ $\rightarrow$ that **is** the QFT.
* Everything in quantum physics can be mapped onto a ['phase space'](https://en.wikipedia.org/wiki/Phase_space) of position $Q$ and momentum $P$ ([formulation](https://en.wikipedia.org/wiki/Phase-space_formulation)).
* ⚠️ **Position basis = computational basis.** The identification the whole dictionary hangs on: $|k\rangle$ are the eigenstates of $\hat Q$ — which is why $Z$ (diagonal) is a function of position and $X$ (permutation) a function of momentum.
* **In QM, time is an angle.** In $e^{-i\theta}$, $\theta$ must be dimensionless (radians); in $\hat U(t) = e^{-i\hat Ht/\hbar}$ the quantity $\hat Ht/\hbar$ plays that role. States don't move along a trajectory like a baseball — their complex phase rotates. **In an energy eigenstate (stationary state) with energy $E$ the state stays put, but its phase spins at frequency $\omega = E/\hbar$.**

<font color="blue">***Unit Circle*** *(Why Complex Numbers?)*</font>

* A [harmonic oscillator](https://en.wikipedia.org/wiki/Simple_harmonic_motion) moves back and forth, $x(t) = \cos\omega t$, described by two real numbers (position $x$, velocity $v$) — combined into one complex amplitude $\alpha = x + ip$. Rotation preserves the structure (unitary): it turns without changing magnitude.
* The annihilation operator does the same for operators: $\hat a \propto \hat Q + i\hat P$. Real axis = position $\cos\omega t$, imaginary axis = momentum $i\sin\omega t$, rotation = time $e^{i\omega t}$ — oscillation between $Q$ and $P$.
* Multiplying $\hat a$ by $e^{-i\omega t}$ rotates the vector in the complex plane: horizontal (real) = maximum position $Q$, vertical (imaginary) = maximum momentum $P$. **The 90° switch from $X$ to $Z$ is the QFT.**

<font color="blue">***Exponentiation:*** *raise $e$ to the power of position and momentum, $e^{-i\hat G\theta}$, to get from the QHO to quantum operators*</font>

* $\hat U = e^{-i\hat G\theta}$ is the general form describing how a state moves in terms of the fundamental operators $\hat Q,\hat P$:
  * $e^{i\theta}$ is a point on the unit circle and keeps it unitary ($U^\dagger U = I$);
  * the $-i$ makes it a rotation in Hilbert space, preserving the norm of the state vector;
  * $\hat G$ is the transformation, $\theta$ scales it. If $\hat G$ is the energy $\hat H$, then $\hat U = e^{-i\hat Ht/\hbar}$ and $\theta$ is the duration $t/\hbar$, because $\hat H$ *is* time evolution.
* **Exponentiation is what produces the gates.** One builds a generator $\hat G$ from the fundamental operators $\hat Q + \hat P$ (or $\hat a,\hat a^\dagger$), or from $\hat X,\hat Z$ (mod $d$) for qudits/qubits from the HW group. The exponential is defined on top of $[\hat x,\hat p] = i\hbar$ (CCR).
* **Linear (Gaussian) transformations** — generator of degree $\le 2$. ⚠️ "Linear" refers to the *Heisenberg action*, not to the generator: $U^\dagger\hat rU = S\hat r + d$ is linear in the quadratures even though $\hat H$ is quadratic. The symplectic structure is preserved.
* **Non-linear (non-Gaussian) transformations** — generator of degree $\ge 3$. The Heisenberg action itself becomes nonlinear ($\hat p \to \hat p - 3\gamma t\hat q^2$) and the Wigner function goes negative.
* ⚠️ **Don't confuse this with the two families of *states*:** coherent states $|\alpha\rangle = \hat D(\alpha)|0\rangle$ are eigenstates of $\hat a$, non-orthogonal and overcomplete (the displaced vacuum — degree-1 output); Fock states $|n\rangle$ are eigenstates of $\hat n = \hat a^\dagger\hat a$ and orthonormal (the eigenbasis of the degree-2 generator).

<font color="blue">***Conjugate relation:*** *an operator generates the translation of its conjugate variable — this is what allows the basis change $X \leftrightarrow Z$*</font>

* Connected via the **Fourier transform**, used in $D_{q,p} = \tau^{qp}X^qZ^p$; based on the commutation relation $[\hat x,\hat p] = i\hbar$ (continuous) resp. the Weyl relation $ZX = \zeta_d XZ$ with $\zeta_d = e^{2\pi i/d}$ (discrete — ⚠️ note $\zeta_d$ rather than $\omega$, which is already the oscillator frequency here). Same mechanism in: characteristic function $\chi(\xi)$ $\leftrightarrow$ Wigner function.
* **Note on notation:** $\zeta_d = e^{2\pi i/d}$ is a primitive $d$-th **root of unity** — the discrete phase appearing in $ZX = \zeta_d XZ$ and $Z|k\rangle = \zeta_d^{\,k}|k\rangle$. ⚠️ Many texts write $\omega$ for this, but $\omega$ is already taken twice here: oscillator frequency ($\hbar\omega$, $\cos\omega t$) and symplectic form ($W(V,\omega)$). The half-phase in $D_{q,p}$ is $\tau = e^{i\pi/d}$, so $\tau^2 = \zeta_d$.

<font color="blue">***Kinetic Energy:*** *$\hat{P}^2$ $\rightarrow$ momentum $\hat{P} = \frac{i}{\sqrt2}(\hat a^\dagger - \hat a)$ $\rightarrow$ shift operator $X = e^{-i\hat P\delta}$ $\rightarrow$ bit flip / Pauli $X$. The energy term is quadratic, but the **gate** exponentiates the linear part $\hat P$*</font>

* **Kinetic energy $\hat P^2$** corresponds to the hopping term / Laplacian $\approx (X + X^\dagger)$ (real, symmetric) — as used in Google's OTOC.
* **Gaussian: momentum** $\hat P = \frac{i}{\sqrt2}(\hat a^\dagger - \hat a)$ corresponds to the derivative $\approx i(X^\dagger - X)$ (complex/imaginary, antisymmetric).
* **Clifford (qudit): shift** $\hat X^a|j\rangle = |j + a \bmod d\rangle$, i.e. $|0\rangle\to|1\rangle\to\dots\to|d-1\rangle\to|0\rangle$. Its eigenvalues are powers of $\zeta_d$ (via Fourier): in the *momentum basis* the shift is diagonal and looks like the clock matrix, because $X = \mathrm{DFT}^\dagger\, Z\, \mathrm{DFT}$.
* **Clifford (qubit): Pauli $X$** $\sigma_x|j\rangle = |j+1 \bmod 2\rangle$ swaps $0\leftrightarrow1$; $ZX = -XZ$ since $\zeta_2 = e^{i2\pi/2} = -1$; eigenvalues $\pm1$.
* **Conjugation:** the shift $X$ *represents* momentum (kinetic) but *generates* a position shift — $D_{q,0}\sim X^q$ moves to a new position. The matrix $X$ is real and off-diagonal (a permutation matrix of 0s and 1s). Shift = exponentiated momentum, $X \approx e^{-i\hat P\delta_x}$.

<font color="blue">***Potential Energy:*** *$\hat{Q}^2$ $\rightarrow$ position $\hat{Q} = \frac{1}{\sqrt2}(\hat a + \hat a^\dagger)$ $\rightarrow$ clock operator $Z = e^{i\hat Q\delta}$ $\rightarrow$ phase flip / Pauli $Z$. Again: quadratic energy, but the **gate** exponentiates the linear part $\hat Q$*</font>

* **Gaussian: position** $\hat Q = \frac{1}{\sqrt2}(\hat a + \hat a^\dagger)$ is an observable with real eigenvalues (the location index $k$).
* **Clifford (qudit): clock** $\hat Z^b|k\rangle = \zeta_d^{\,bk}|k\rangle$ with $\zeta_d = e^{2\pi i/d}$ — a phase gradient built from the primitive $d$-th root of unity (which supplies the eigenvalues). Its powers $\zeta_d^0,\zeta_d^1,\dots,\zeta_d^{\,d-1}$ tag each basis state $k$ with a phase on the unit circle. For $d = 3$: $\zeta_3 = e^{i2\pi/3}$ (unitary but *not* Hermitian).
* **Clifford (qubit): phase flip / Pauli $Z$.** For $d = 2$ the primitive root is $\zeta_2 = e^{i\pi} = -1$, so $\sigma_z|j\rangle = (-1)^j|j\rangle$ — the mod-2 version of the Weyl relation, $ZX = -XZ$. It leaves $|0\rangle$ alone and flips the sign of $|1\rangle$. ⚠️ Pauli $Z$ is both unitary (preserves probabilities) **and** Hermitian (its own conjugate) — so it can be observed directly.
* **Conjugation:** the clock $Z$ *represents* position (potential) but *generates* a momentum kick — $D_{0,p}\sim Z^p$ makes it move faster. The matrix $Z$ is diagonal with complex eigenvalues (phases on the unit circle), whereas the operator $\hat Q$ has real eigenvalues (location).

<font color="blue">**Groups: From Heisenberg–Weyl Algebra to Quantum Gates (by Degree of the Generator $\hat{H}$)**</font>

> Every quantum gate is a time evolution $U = e^{-i\hat{H}t}$. The physical and information-theoretic complexity of the gate is completely determined by the **polynomial degree of the generator $\hat{H}$ in the phase-space operators** — and the criterion behind the ladder is whether that degree still **closes under the commutator**.

<font color="blue">***Degree 1 (linear): Displacements*** — *generator $\hat{H} = q\hat{P} - p\hat{Q}$; the base lattice of phase space*</font>

* **Lie algebra ✅ closes trivially:** the $(2n+1)$-dimensional **Heisenberg algebra $\mathfrak{h}_n$**; $[\hat Q,\hat P] = i\hbar\mathbf{1}$ is central (commutes with everything).
* **Action:** pure displacements — the state is *slid* to a new location $(q,p)$, not rotated about the origin and not changed in shape. $H \propto \hat P$ generates a shift in $Q$; $H \propto \hat Q$ generates a shift in $P$.
* **CV — Displacement operator:** $\hat D(q,p) = e^{-\frac{i}{\hbar}(q\hat P - p\hat Q)}$, equivalently $\hat D(\alpha) = e^{\alpha\hat a^\dagger - \alpha^*\hat a}$.
* **Discrete — Heisenberg–Weyl group:** shift $X$ (bit flip, position), clock $Z$ (phase flip, momentum), $D_{q,p} = \tau^{qp}X^qZ^p = e^{i\pi qp/d}X^qZ^p$. The phase factor is required because $X$ and $Z$ do not commute (Aharonov–Bohm effect in phase space). For $d = 2$: the Pauli group $\mathcal{P}$.
* **⚠️ Pauli-$Y$ is not an independent operator**, just a product: $\sigma_y = i\sigma_x\sigma_z$. For $d = 2$, $X^1Z^1 \propto Y$ — the $(1,1)$ point on the grid. For $d = 3$ ($XZ$, $XZ^2$, $X^2Z$, …) none is uniquely "$Y$": it simply becomes one of the many $D_{q,p}$ with $q,p \neq 0$.
* **Hierarchy & simulability:** level $\mathcal{C}_1$. Pure lattice displacements, serving as an orthogonal basis for the entire operator space.
* **Fermionic mirror: there is no fermionic analogue of a displacement gate.** Algebraically degree $\le 1$ does not close under the commutator ($[\gamma_i,\gamma_j] = 2\gamma_i\gamma_j$ lands in degree 2); only the *anti*commutator closes ($\{\gamma_i,\gamma_j\} = 2\delta_{ij}\mathbf{1}$ — a Lie superalgebra). Physically, parity superselection forbids odd Hamiltonians; fermionic coherent states exist only formally, over anticommuting Grassmann numbers.

<font color="blue">***Degree 2 (quadratic): Rotations, Shears, Entanglement*** — *generator $\hat{H} \propto \hat{Q}^2 + \hat{P}^2$, $\hat{Q}^2 - \hat{P}^2$, $\hat{Q}_1\hat{P}_2$; symmetries that map the lattice onto itself*</font>

* **Lie algebra ✅ closes:** the commutator of two quadratic terms stays quadratic ($[\hat Q^2,\hat P^2] \propto \hat Q\hat P + \hat P\hat Q$) → **symplectic algebra $\mathfrak{sp}(2n,\mathbb{R})$**; together with degree $\le 1$ the semidirect product $\mathfrak{sp}(2n)\ltimes\mathfrak{h}_n$ (Gaussian operations).
* **Action:** a strictly **linear transformation of the coordinates**, $U^\dagger\hat rU = S\hat r$ with $S \in \mathrm{Sp}(2n)$ — rotations around the origin of phase space, shears, and entanglement. The structure of phase space is not bent, only mapped onto itself.
* **CV — metaplectic group $\mathrm{Mp}(2n)$ (Gaussian unitaries):**
  * **Phase shifter / rotator** $R(\theta) = e^{-i\theta\hat n}$, $H \propto \hat Q^2 + \hat P^2$: rotates the state by $\theta$. The $\hat Q$–$\hat P$ swap is potential and kinetic energy switching back and forth forever = basis change. At $\theta = \pi/2$ (quarter turn, 90°) this **is** the Fourier transform — and note that *the angle is time* in this setting.
  * **Squeezer** $\hat S(r) = e^{-\frac{ir}{2\hbar}(\hat Q^2 - \hat P^2)}$, generator $\hat Q\hat P + \hat P\hat Q$: scales the axes, multiplying position by $e^{-r}$ and momentum by $e^{r}$.
  * **Beam splitter** $\hat B(\theta) = e^{-i\theta(\hat Q_1\hat P_2 - \hat Q_2\hat P_1)}$ — the angular momentum operator in phase space, a passive rotation between two modes. At $\theta = \pi/4$ (50:50): $\hat a_1 \to \frac{\hat a_1 + \hat a_2}{\sqrt2}$, $\hat a_2 \to \frac{\hat a_1 - \hat a_2}{\sqrt2}$.
  * **Quadratic phase (shear)**, $H \propto \hat Q^2$: preserves position $Q$, shears momentum $P \to P + Q$.
  * **Squeezer + beam splitter = entanglement $\approx$ CNOT:** squeeze the state into an ellipse, then rotate it 45° with the beam splitter → the noise becomes correlated between the two axes, which *is* entanglement.
* **Discrete — Clifford group $\mathcal{C}$**, the normalizer of the Pauli group, $\mathcal{C} = \{U : U\mathcal{P}U^\dagger = \mathcal{P}\}$; modulo phases $\mathcal{C}/\mathcal{P} \cong \mathrm{Sp}(2n,\mathbb{Z}_d)$:
  * **QFT (qudit)** = exactly the quarter period $\theta = \pi/2$, rotating the $Z$-eigenbasis (position) into the $X$-eigenbasis (momentum) via the conjugate relation: $\mathrm{QFT}_d|j\rangle = \frac{1}{\sqrt d}\sum_{k=0}^{d-1}\omega^{jk}|k\rangle$ — a localized basis state becomes a uniform superposition tagged with phases. $WXW^\dagger = Z$ (QFT diagonalizes the shift $X$), $WZW^\dagger = X^\dagger$. The qudit $Z$ applies $\omega^j = e^{2\pi ij/d}$ based on the *single* index $j$.
  * **Hadamard (qubit):** the same basis change $Z \leftrightarrow X$ via equal superposition, $H|0\rangle = |+\rangle$.
  * **Phase gate $S$ (qubit)** = the discrete shear: $Z \to Z$, $X \to Y \sim XZ$; diagonal, $S = \mathrm{diag}(1,i,\dots)$, adding a quadratic phase $k^2$ to the wavefunction.
  * **C-SUM / $CX$ (qudit)** $= e^{-i\hat Q_1\hat P_2}$: $|c\rangle|t\rangle \to |c\rangle|t \oplus c \bmod d\rangle$, coupling the position of particle 1 to the momentum (shift) of particle 2. Built as beam splitter + squeezing + inverse beam splitter. **CNOT (qubit)** is the same thing mod 2.
* **Hierarchy & simulability:** level $\mathcal{C}_2$. **Gottesman–Knill / Gaussian simulation** — classically efficient in polynomial time, since one only tracks the $2n\times2n$ symplectic matrix $S$ instead of $2^n$ complex amplitudes.
* **Fermionic mirror — free fermions & matchgates:** quadratic fermionic Hamiltonians close under the commutator onto $\mathfrak{so}(2n) \cong \Lambda^2V$, exponentiating to $\mathrm{Spin}(2n)$. **Matchgates (Valiant) are the exact fermionic counterpart of Gottesman–Knill** — $SO(2n)$/Spin instead of $\mathrm{Sp}(2n)$/Mp, orthogonal rotors instead of symplectic shears. Via Jordan–Wigner they can be written as Pauli matrices, but the *reason* for their simulability is spinorial, not symplectic.

<font color="blue">***Degree $\geq$ 3 (cubic & higher): Nonlinear Distortion and Quantum Advantage*** — *generator $\hat{H} \propto \hat{Q}^3$, $\hat{n}^2 \sim (\hat{Q}^2+\hat{P}^2)^2$, or many-body interactions*</font>

* **Lie algebra ❌ does NOT close:** commutators climb indefinitely — $[\text{cubic},\text{cubic}]$ generates degree 4, that generates degree 5, and so on. No finite-dimensional Lie algebra; the generated group is infinite-dimensional.
* **Action:** phase space is **curved nonlinearly** — the Heisenberg evolution becomes $\hat p \to \hat p - 3\gamma t\hat q^2$. One falls out of $\mathrm{Sp}(2n)$; the construction is no longer structure-preserving. ⚠️ The HW language stays formally valid but loses its usefulness: one *can* write $T$ as a Pauli sum, but the number of terms grows under nesting — and that is precisely where classical simulation breaks down.
* **CV — non-Gaussian unitaries:**
  * **Cubic phase** $V(\gamma) = e^{i\gamma\hat Q^3}$: distorts phase space, a coherent-state circle becomes a "banana" with negative Wigner regions — the signature of non-classicality.
  * **Kerr** $e^{i\chi\hat n^2}$ with $\hat n = \hat a^\dagger\hat a$, generator $\propto (\hat Q^2 + \hat P^2)^2$ (quartic): a medium whose refractive index depends on intensity; used to build cat states (macroscopic superpositions), the basis of bosonic codes.
* **Discrete — non-Clifford gates:**
  * **$T$ gate (qubit)**, the $\pi/8$ gate $\hat T = e^{-i\frac{\pi}{8}\hat Z}$ — the cubic phase in discrete phase space (mod 2).
  * **Discrete cubic phase (qudit) $\hat T_d$:** $T_d|k\rangle = \omega^{k^3}|k\rangle$, i.e. diagonal phases $e^{i\frac{2\pi}{d^3}k^3}$ — exactly analogous to $V(\gamma) = e^{i\gamma\hat x^3}$.
  * **Toffoli (CCNOT)** and **CS**; general high-order phase gates for qudits.
  * ⚠️ They lie in $M_d(\mathbb{C})$ as matrices, but belong neither to the discrete HW group nor to the Clifford group.
* **Hierarchy & simulability:** $\mathcal{C}_k = \{U : U\mathcal{P}U^\dagger \subset \mathcal{C}_{k-1}\}$ — ⚠️ for $k \ge 3$ these are no longer groups under multiplication. Clifford $+$ $T$ generates a dense subgroup of $U(2^n)$ (**universal quantum computing**), no longer efficiently simulable classically. **Magic states and quantum advantage start here.**
* **Fermionic mirror — degree 3 is missing:** parity superselection forbids cubic fermionic interactions, so genuine non-simulability begins on that side only at **degree 4** (quartic, e.g. the Hubbard $U$ term $n_\uparrow n_\downarrow$). And no $2\times2$ grid is needed there: for $n$ modes the Clifford algebra is finite-dimensional by nature ($\cong M_{2^n}(\mathbb{C})$ via Jordan–Wigner) — no trace problem for anticommutators.

## Tensor Algebra $T(V)$

Tensor Algebra $T(V)$ as the Source of Four Algebras: $\Lambda$, $\mathrm{Sym}$ (classical) and $\mathrm{Cl}$, $W$ (quantized) — Fermions vs. Bosons


*One recipe, one knob. The recipe: quotient the tensor algebra by a two-sided ideal generated in degree 2. The knob: the **parity of the bilinear form** you put into that ideal — symmetric ($g$, $Q$) or antisymmetric ($\omega$) — plus whether you switch its value on at all. Four combinations, four algebras:*

| | **Symmetric form $Q$** | **Antisymmetric form $\omega$** |
| :--- | :--- | :--- |
| **Form off** (classical) | $\Lambda(V)$ — exterior | $\mathrm{Sym}(V)$ — symmetric |
| **Form on** (quantized) | $\mathrm{Cl}(V,Q)$ — **fermions**, CAR | $W(V,\omega)$ — **bosons**, CCR |

<font color="blue">***Step 0 — the common source:*** *$T(V) = \bigoplus_k V^{\otimes k}$, associative and non-commutative, with no relations at all*</font>

* Nothing is identified in $T(V)$: $v\otimes w$ and $w\otimes v$ are simply different elements. **Every relation below is introduced by hand, as the generator of an ideal.** That is the entire mechanism — all four algebras are $T(V)/I$ and differ only in $I$.

<font color="blue">***Step 1 — homogeneous ideal ⇒ the two classical algebras*** *(degree 2 = 0, nothing else)*</font>

* **$\Lambda(V) = T(V)/\langle v\otimes v\rangle \;\Rightarrow\; v\wedge w = -\,w\wedge v$.** Demand that squares vanish; polarization does the rest: $0 = (v+w)\wedge(v+w) = v\wedge w + w\wedge v$. Antisymmetry — hence orientation, differential forms, cohomology.
* **$\mathrm{Sym}(V) = T(V)/\langle v\otimes w - w\otimes v\rangle \;\Rightarrow\; vw = wv$.** Demand that order be irrelevant. Polynomials — the classical observables, functions on phase space.
* ⚠️ **Both ideals are homogeneous** (pure degree 2, right-hand side $= 0$), so the quotient keeps the $\mathbb{Z}$-grading. These are the *undeformed* algebras: $\Lambda = \mathrm{Cl}$ with $Q = 0$, $\mathrm{Sym} = W$ with $\omega = 0$.

<font color="blue">***Step 2 — switch the bilinear form on ⇒ the two quantized algebras*** *(the right-hand side becomes a number — this is quantization)*</font>

* **$\mathrm{Cl}(V,Q) = T(V)/\langle v\otimes v - Q(v)\mathbf{1}\rangle \;\Rightarrow\; vw + wv = 2Q(v,w)$.** A vector squares to its own length, $v^2 = \lVert v\rVert^2$.
* **$W(V,\omega) = T(V)/\langle v\otimes w - w\otimes v - \omega(v,w)\mathbf{1}\rangle \;\Rightarrow\; [v,w] = \omega(v,w)$.** The commutator is no longer zero but a number — the Poisson bracket of the linear functions: $[\hat q,\hat p] = i\hbar\mathbf{1}$.
* ⚠️ **The one mechanism behind both:** the ideal becomes **inhomogeneous** (it mixes degree 2 with degree 0), so the $\mathbb{Z}$-grading collapses to a **filtration** ($\mathbb{Z}_2$-grading survives; on the bosonic side: Bernstein filtration). *Grading → filtration is exactly what "quantization" means algebraically.*
* ⚠️ **The deformation changes the product, not the space.** Check with $\dim V = 2$: both $\Lambda(\mathbb{R}^2)$ and $\mathrm{Cl}(\mathbb{R}^2,Q)$ have dimension 4, basis $\{1,e_1,e_2,e_1e_2\}$ — same skeleton, different multiplication table ($e_1\wedge e_1 = 0$ vs. $e_1e_1 = Q(e_1)$). No subset relation. Same on the right: PBW monomials $\hat q^a\hat p^b$ are a basis of $W$ just as they are of $\mathrm{Sym}$.

<font color="blue">***⚠️ The Twist — parity flips between input and output*** *(the least intuitive and most important line in the whole table)*</font>

* **Symmetric input $\to$ anticommuting output:** $g \in \mathrm{Sym}^2V^*$ builds $\mathrm{Cl}(V,g)$, whose degree-2 part is the **exterior** square, $\mathfrak{so}\cong\Lambda^2V$ (via $\tfrac14[e_i,e_j]$) → Spin → **fermions**, $\Lambda$-Fock.
* **Antisymmetric input $\to$ commuting output:** $\omega \in \Lambda^2V^*$ builds $W(V,\omega)$, whose degree-2 part is the **symmetric** square, $\mathfrak{sp}\cong\mathrm{Sym}^2V$ (via $\tfrac12\{\hat r_i,\hat r_j\}$) → metaplectic → **bosons**, $\mathrm{Sym}$-Fock.
* So the labels cross: the *fermionic* algebra is built from a *symmetric* form and its symmetry algebra is the *exterior* square, and vice versa. In supersymmetry both are one construction on $\mathbb{Z}_2$-graded spaces.

<font color="blue">***Step 3 — the way back ($\mathrm{gr}$):*** *dequantization = keep only the top-degree part of each relation*</font>

* $\mathrm{gr}\,\mathrm{Cl}(V,Q) \cong \Lambda(V)$ (**Chevalley**), classical limit $Q\to0$ · $\mathrm{gr}\,W(V,\omega)\cong\mathrm{Sym}(V)$ (**PBW**), classical limit $\hbar\to0$.
* ⚠️ These are **one theorem**: super-PBW on $\mathbb{Z}_2$-graded spaces *is* Chevalley. Taking $\mathrm{gr}$ throws away exactly the inhomogeneous part of the ideal — i.e. it turns the knob back to zero.

<font color="blue">***Second road to the same ideal — the Lie route*** *(both roads meet, which is why it's called a "PBW deformation")*</font>

* $U(\mathfrak{g}) = T(\mathfrak{g})/\langle x\otimes y - y\otimes x - [x,y]\rangle$ — an enveloping algebra is *also* a tensor-algebra quotient, with the same shape of ideal.
* **Fermionic:** Heisenberg *super*algebra $\mathfrak{h}^{\mathrm{super}}$ (odd part $V$, even centre $Z$, bracket = **anti**commutator $\{v,w\} = 2Q(v,w)Z$) → $\mathrm{Cl}(V,Q) = U(\mathfrak{h}^{\mathrm{super}})/(Z-1)$.
* **Bosonic:** Heisenberg algebra $\mathfrak{h}_n$ ($[Q_i,P_j] = \delta_{ij}Z$, $Z$ central, $\dim = 2n+1$ — here one may not yet *multiply* $\hat Q\cdot\hat P$) → $U(\mathfrak{h}_n)$ supplies the products → $A_n = U(\mathfrak{h}_n)/(Z-1)$, the same ideal as the deformation route.

<font color="blue">***What each side becomes — physics, symmetry, computing*** *(read the pairs across)*</font>

* **Statistics:** CAR $\{a_i,a_j^\dagger\} = \delta_{ij}$, $\{\gamma_\mu,\gamma_\nu\} = 2g_{\mu\nu}$ ↔ CCR $[a_i,a_j^\dagger] = \delta_{ij}$, $[\hat x,\hat p] = i\hbar$.
* **Size — the sharpest asymmetry:** $\dim\mathrm{Cl} = 2^n$ (the relation truncates powers, $v^2$ is a scalar) ↔ $\dim W = \infty$ (nothing truncates). Consequence: $W$ has **no finite-dimensional representation** ($\mathrm{tr}[A,B] = 0$ but $\mathrm{tr}(i\hbar\mathbf 1)\neq0$), so bosons need unbounded operators on an infinite-dimensional space, while $\mathrm{Cl}$ acts on a finite spinor space. *(This is the trace argument that later forbids a discrete additive Weyl algebra.)*
* **Uniqueness:** unique spinor module ↔ **Stone–von Neumann** (unique irreducible rep for $\hbar\neq0$) — same statement on both sides.
* **In analysis:** Dirac operator $\nabla = d+\delta$, $\nabla^2 = \Delta$ ↔ oscillator $H = \tfrac12(\hat p^2+\hat q^2) = \hbar(a^\dagger a+\tfrac12)$; each is the canonical degree-2 square of its branch (Moyal star product = the same deformation written on $\mathrm{Sym}$-functions).
* **Symmetry tower** (group preserves the form; Lie algebra = degree-2 elements; double cover acts on Fock space): $\mathrm{O}(V,g) \supset \mathfrak{so}(n)$, $\dim\tfrac{n(n-1)}2$, series $B_n/D_n$, cover $\mathrm{Spin}(n)$ ↔ $\mathrm{Sp}(2n)\supset\mathfrak{sp}(2n)$, $\dim n(2n+1)$, series $C_n$, cover $\mathrm{Mp}(2n)$.
* **QC bridge:** matchgates / free fermions (Valiant), degree 2 in $\mathrm{Cl}$ = rotor in $\mathrm{Spin}(2n)$; non-free only from **degree 4** (parity superselection allows only even degrees) ↔ Clifford / Gaussian (Gottesman–Knill), degree 2 in $W$ = symplectic action; magic from **degree 3**. ⚠️ **Structurally one theorem**, once for $SO$/Spin, once for $Sp$/Mp.

<font color="blue">***From Weyl algebra to Heisenberg–Weyl:*** *how the bosonic side reaches actual qubits (additive → multiplicative, continuous → discrete)*</font>

* **Additive / continuous — the Weyl algebra $A_n = W(V,\omega)$.** All polynomials in $\hat q,\hat p$, $\dim = \infty$; composition = addition + Lie bracket. This is the algebra built two steps above, the home of Hamiltonians and the degree filter.
* **Additive / discrete — ⚠️ does not exist.** *Trace argument:* on $d\times d$ matrices $\mathrm{Tr}([\hat q,\hat p]) = 0$, but $\mathrm{Tr}(i\hbar\mathbf 1) = i\hbar d \neq 0$. So $[\hat q,\hat p] = i\hbar$ has no finite-dimensional realization — qubits cannot inherit the additive relation. This is the $\dim W = \infty$ bullet from above, now with consequences.
* **Multiplicative / continuous — Heisenberg group $H_n$ / CCR $C^*$-algebra.** The exponentiated version: displacements $D(\alpha)$, composition = operator product, $W(z)W(z') = e^{-\frac i2\omega(z,z')}W(z+z')$. Linked back to $A_n$ by **Stone–von Neumann**.
* **Multiplicative / discrete — HW algebra $M_d(\mathbb{C}) \cong \mathbb{C}_\omega[\mathbb{Z}_d\times\mathbb{Z}_d]$**, spanned by the $d^2$ shift–clock matrices $X^qZ^p$. ⚠️ **Why exponentiating rescues what the additive box forbids — trace vs. determinant:** at group level the test uses $\det$, and $\det(ZXZ^{-1}X^{-1}) = 1$ must equal $\det(\zeta_d\mathbf 1) = \zeta_d^{\,d} = 1$ ✓. The additive constraint is *unsatisfiable*, the multiplicative one *automatically satisfied* — which is why $ZX = \zeta_d XZ$ exists in exact $d\times d$ matrices. **That is the whole route from Weyl algebra to Heisenberg–Weyl.**
* **Moving between the boxes:** upward $\mathfrak{h}_n \xrightarrow{\exp} H_n$ (BCH terminates because $[\hat Q,\hat P]$ is central — the additive bracket becomes a multiplicative phase); back down by differentiating at the identity; sideways $G \xrightarrow{\mathrm{span}} M_d(\mathbb{C})$ (group algebra, *not* $\exp$ — ⚠️ **algebras are not exponentiated**); and $d\to\infty$ turns $ZX = \zeta_d XZ$ back into $[\hat Q,\hat P] = i\hbar\mathbf 1$.

<font color="blue">*Differential Forms and the Symplectic Form*</font>

* **Forms vs. Maps:** While general maps output vectors or functions, a **form evaluates to a scalar**. A $k$-form is a multilinear map ($0$-form = function, $1$-form = covector, $2$-form = bilinear form).
* **Differential Forms:** Smooth sections of the exterior algebra bundle, $\Omega^k(M) = \Gamma(\Lambda^k T^*M)$, assigning an alternating form to each point's tangent space via the wedge product ($\alpha \wedge \beta = -\beta \wedge \alpha$). Forms naturally integrate over oriented geometric submanifolds without coordinates—$1$-forms over curves (work), $2$-forms over surfaces (flux/oriented area), and $n$-forms over volumes.
* **The Symplectic Form ($\omega$):** A $2$-form defined by three core properties: **Alternating:** Pointwise antisymmetric bilinear form. **Closed ($d\omega = 0$):** Eliminates local curvature invariants (Darboux). **Non-degenerate ($\omega(v,w)=0 \ \forall w \implies v=0$):** Forces an **even dimension** ($2n$, matching positions and momenta) and yields the non-vanishing **Liouville volume form** $\omega^n$.


<font color="blue">*Riemannian vs. Symplectic Geometry on Manifolds: Can a geometric field be made locally "flat" through a choice of coordinates?*</font>

* **Riemannian Geometry: Local Information (Gravity / GR) and local curvature (tensors)**
  * **Riemannian:** $g$ becomes $g_{\mu\nu}(x)$; comparing tangent spaces needs a connection, curvature is its non-commutativity → **local curvature exists, information is local** → tensor analysis.
  * **Setup:** The metric $g = g_{\mu\nu}(x) dx^\mu \otimes dx^\nu$ is a symmetric tensor field. Comparing different tangent spaces requires a connection $\nabla$.
  * **Local Flatness:** In normal coordinates at a point $p$, $g_{\mu\nu}(p) = \delta_{\mu\nu}$ and $\partial_\lambda g_{\mu\nu}(p) = 0$, but the **second derivatives** $\partial^2 g$ cannot be eliminated.
  * **Consequence:** Genuine, measurable **local curvature** exists (Riemann tensor $R^\rho_{\sigma\mu\nu}$). Physics is governed by **local field equations and tensor analysis** (e.g., Einstein equations).
* **Symplectic Geometry: Global Information (Phase Space / Mechanics) and global topology (cohomology)**
  * **Symplectic:** $\omega$ becomes a closed 2-form; by Darboux there are no local invariants → **information is global** → globalization runs into topology and quantization.
  * **Setup:** The symplectic form $\omega = \frac{1}{2}\omega_{\mu\nu}(x) dx^\mu \wedge dx^\nu$ is alternating, non-degenerate, and **closed** ($d\omega = 0$).
  * **Darboux's Theorem:** Because $d\omega = 0$, local coordinates always exist around any point such that $\omega = \sum dp_i \wedge dq^i$ holds across an entire neighborhood.
  * **Consequence:** There are **no local invariants** (no analog to the Riemann tensor; every point looks locally like flat $\mathbb{R}^{2n}$). All meaningful geometric and physical features are **global and topological** (de Rham cohomology $[\omega] \in H^2_{\mathrm{dR}}(M)$, global quantization conditions $\frac{1}{2\pi\hbar}\int_\Sigma \omega \in \mathbb{Z}$).
 

