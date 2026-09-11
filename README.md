# Quantum Learning

Alexander Del Toro Barba, PhD, AI and Quantum Computing at Google. I ❤️ Maths

[Google Scholar](https://scholar.google.com/citations?hl=en&user=fddyK-wAAAAJ) $\cdot$ [LinkedIn](https://www.linkedin.com/in/deltorobarba/)


<img src="https://raw.githubusercontent.com/deltorobarba/science/main/science.JPG" alt="science"> 


## Learning from Quantum Experiments

### 1. Wie hängen Quantenmessung und Quantum Learning zusammen?

* Die kürzeste Fassung: Lerntheorie ist die Ressourcentheorie, die auf der Messtheorie aufsetzt.
  * Die **Messtheorie** (deine Teile I–II) beantwortet die Einzelschuss-Frage: Was tut eine Messung mit einem Zustand, welche Statistik erzeugt sie?
  * Die **Lerntheorie** stellt die inverse, statistische Frage: *Was lässt sich aus vielen Messungen über ein unbekanntes ρ herausfinden — und zu welchen Kosten, optimal?*
* Die Born-Regel verwandelt den Zustand in ein Sampling-Orakel; Lernen ist das Inversproblem dazu.

### 2. Begriffsklärung: die Datenquelle entscheidet, nicht die Hardware

* **Learning from quantum experiments** ist die Disziplin, die fragt: Gegeben Zugriff auf Kopien eines unbekannten Quantensystems — eines Zustands $\rho$, eines Prozesses/Kanals $\mathcal{E}$, einer Dynamik —, erzeugt von der Natur, einem Sensor oder einem Quantengerät: *welche* Eigenschaften kann ein Lerner extrahieren, zu *welchen* Kosten in Kopien, klassischer Zeit und klassischem Speicher, und wie verändern Quantenressourcen (Quantenspeicher, verschränkte Messungen, Adaptivität) diese Kosten?
* *What properties of unknown state $\rho$, channel $\mathcal{E}$, Hamiltonian $H$ can be learned from physical copies — and at what Pareto-optimal budget in copies, classical runtime, and quantum memory?*

### 3. Differentiations by Data and Learners

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


### 4. Differentiations by Ressources

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

### 5. Differentiations by Task: Tomography vs Strukturlernen

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


## Typen von Lernprotokollen für Quantum Experiments


### 1. Estimating: Tomography to Triple Efficiency (Observables as Input)

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

### 2. Quantum Memory, Conjugate Access & Adaptivity

* **Two-copy mechanism:** Measuring across $\rho^{\otimes 2}$ in the $2n$-qubit Bell basis $\{(P\otimes\mathbb{1})\vert{}\Phi^+\rangle^{\otimes n}\}$ samples Pauli strings $P$ globally from a single shot.
* **Conjugate pairs:** Access to $(\rho, \rho^*)$ isolates the clean product spectrum $\mathrm{Tr}(P\rho)^2/2^n$ with constant quantum memory.
* **Memory hierarchy:** Most exponential advantage arrives at $k=2$ copies; single-copy strategies require $2^{\Omega(n)}$ shots for identical global tasks.
* *Key Literature:*
  * **Bubeck, Chen, Li (FOCS 2020):** Entanglement necessary for optimal quantum property testing.
  * **Chen, Cotler, Huang, Li (FOCS 2021):** $\Theta(n)$ vs. $2^{\Omega(n)}$ exponential separation with quantum memory.
  * **Huang et al. (Science 2022):** Flagship theoretical separations and Sycamore 40-qubit hardware demo.
  * **King, Wan, McClean (2024):** Exponential advantage via $(\rho, \rho^*)$ conjugate access with constant memory.
  * **Chen, Gong, Zhang (2024):** Exponential separations proven for adaptive multi-copy shadow tomography.

### 3. Searching: Structure Learning & Agnostic Tomography (Observables as Output)

* **Task:** Discover the unknown sparse support of $\rho$ before estimating values (analogous to graphical model learning).
* **Computational barrier:** While Bell sampling easily concentrates draws onto the support, reconstructing the generators without active queries is generically cryptographically hard (LWE-type). Subgroup/stabilizer symmetries form the primary tractable exception.
* *Key Literature:*
  * **Montanaro (2017):** Learning stabilizer states from $O(n)$ Bell samples via linear algebra.
  * **Grewal, Iyer, Kretschmer, Liang (2023):** Bell difference sampling and learning states with few non-Clifford gates.
  * **Hangleiter, Gullans (PRL 2024):** Bell sampling as a universal diagnostic framework for quantum circuits.

### 4. Computational Lens: Three Budgets & Hardness

* **Budget decoupling:** Copy complexity, classical time, and quantum memory scale independently. Sample-efficient protocols routinely hit exponential classical decoding barriers.
* **Pseudorandomness:** Pseudorandom states (PRS) prove that quantum states can be statistically learnable yet computationally indistinguishable from Haar-random states.
* *Key Literature:*
  * **Regev (2005):** Learning With Errors (LWE) — bedrock for average-case classical learning hardness.
  * **Ji, Liu, Song (CRYPTO 2018):** Formulation of pseudorandom quantum states (PRS).
  * **Kretschmer (TQC 2021):** Connecting quantum pseudorandomness to classical learning hardness.
  * **Huang, Broughton et al. (Nat. Commun. 2021):** *Power of data in quantum machine learning* — proves that access to classical data closes potential quantum speedups for learning classical functions, delineating classical vs. quantum data advantages.

### 5. Learning Dynamics: Hamiltonians, Channels & Circuits

* **Hamiltonians:** Learning unknown terms and coupling graphs from thermal Gibbs states or real-time dynamics up to the Heisenberg limit.
* **Circuits & Channels:** Bounding Pauli channel noise; learning constant-depth shallow circuits in polynomial time.
* *Key Literature:*
  * **Flammia, Wallman (TQC 2020):** Efficient Pauli channel estimation protocols.
  * **Anshu et al. (Nat. Phys. 2021) / Haah et al. (FOCS 2022):** Optimal sample complexity for Gibbs-state Hamiltonian learning.
  * **Huang et al. (PRL 2023):** Heisenberg-limited Hamiltonian learning from real-time evolution.
  * **Huang et al. (STOC 2024):** Polynomial-time reconstruction of shallow quantum circuits.

### 6. Machine-Learned Decoders (ML on Quantum Data)

* **Role:** Classical neural decoders processing shadow data (bottom-left matrix quadrant) act as empirical heuristics for classically hard decoding tasks.
* *Key Literature:*
  * **Torlai et al. (Nat. Phys. 2018):** Neural-network quantum state tomography.
  * **Huang, Kueng, Torlai, Albert, Preskill (Science 2022):** Provable generalization bounds for classical ML trained on quantum shadow data.
  * **Huang, Preskill, Soleimanifar (2024):** Rigorous state certification via single-qubit shadow relaxations.

### 7. Surveys & Timeline

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

### 8. Open Frontiers

* **Tractable Islands:** Delineating the boundary between subgroup-tractable classes and cryptographically hard spectra under varying noise: **Kartierung der dekodierbaren Klassen - Zwischen „Subgruppen-leicht" (lineare Algebra) und „LWE-hart" liegt ein unvermessenes Gebiet**; derselbe Zustand wandert durch bloßes Aufdrehen eines Rauschparameters vom leichten ins harte Regime — ein Übergang, der nach systematischer Vermessung verlangt. Offen ist auch, ob die Härte-Reduktion von der Tensor-Produkt-Basis auf die zyklische Ein-Qudit-Basis übertragbar ist.
* **Was gelernte Decoder implizit finden.** Funktioniert ein trainierter Decoder auf einer Klasse ohne bekannten effizienten Algorithmus, hat er möglicherweise einen gefunden — ML als Werkzeug der Algorithmen-Entdeckung, mit der offenen Frage nach einer Metrik, die Generalisierung über Zustandsverteilungen vorhersagt.
* **Hardware-Realistic Multi-Copy:** Scaling 2-copy protocols under realistic preparation, crosstalk, and measurement noise. - **Konstanter Quantenspeicher und Hardware-Realismus.** Wie weit trägt die Zwei-Kopien-Disziplin? Approximate matched filters (Probe-Gain $\kappa < 1$, Mehrkosten $\kappa^{-2}$) machen die Protokolle graceful gegenüber Präparationsfehlern — die praktisch relevanteste Achse für Geräte der nächsten Jahre.
* **Average-Case Physics:** Replacing adversarial worst-case cryptography bounds with physically natural ground-state priors. - **Average-Case statt Worst-Case.** Die Härte-Resultate sind adversarial; natürlich vorkommende Zustände (Grundzustände lokaler Hamiltonians, thermische Zustände) könnten generisch dekodierbar sein — der Übergang von der Kryptographie-Perspektive zur Physik-Perspektive auf dieselbe Frage.

## Entwicklung der Lernprotokolle für Quantum Experiment


### 1. Zustandsdiskriminierung: Helstrom vs. USD

Gegeben eine von zwei bekannten Präparationen $\rho_0, \rho_1$ (a priori $p_0, p_1$) — welche liegt vor? Da nicht-orthogonale Zustände nicht perfekt unterscheidbar sind (Abschnitt 4), gibt es zwei kanonische Strategien mit unterschiedlichem Fehlerbegriff:

**Helstrom-Messung (Minimum-Error).** Erzwinge eine Antwort in jedem Durchlauf und minimiere den *mittleren Fehler*. Die optimale Messung ist eine projektive Messung auf das Vorzeichenspektrum von $p_0\rho_0 - p_1\rho_1$, mit der Helstrom-Schranke

$$P_{\text{err}}^{\min} = \frac{1}{2}\Big(1 - \big\|p_0\rho_0 - p_1\rho_1\big\|_1\Big),$$

für reine Zustände mit gleichen Prioren $P_{\text{err}}^{\min} = \frac{1}{2}\big(1 - \sqrt{1 - |\langle\psi_0|\psi_1\rangle|^2}\big)$. Funktioniert für reine *und* gemischte Zustände — das Standardverfahren, wenn Fehler tolerierbar, Enthaltung aber nicht.

**Unambiguous State Discrimination (USD).** Erlaube einen dritten Ausgang "unentschieden" und verlange, dass die entschiedenen Antworten *nie* falsch sind. Für nicht-orthogonale Zustände erzwingt das eine echte POVM (drei Effekte auf einem Qubit — mit Projektoren unmöglich); der Preis ist die Enthaltungswahrscheinlichkeit, minimal $|\langle\psi_0|\psi_1\rangle|$ bei gleichen Prioren. Fehlerfreiheit gegen Auskunftsverweigerung — die komplementäre Währung zu Helstrom.

### 2. Tomographie: die exponentielle Basislinie

**Quantum State Tomography (QST)** rekonstruiert alle $d^2$ Parameter von $\rho$ aus einem *informationsvollständigen* Messsatz. Bei DV: alle $3^n$ Pauli-Basen (rotate-then-read in jeder Kombination) oder eine einzige SIC-POVM. Bei CV: Homodyn-Messungen der Quadratur-Randverteilungen $p(x_\theta)$ über einen Scan der LO-Phase $\theta$, aus denen die **Wigner-Funktion** $W(x,p)$ per inverser Radon-Transformation rekonstruiert wird (die Heterodyn-Statistik liefert direkt die glattere $Q$-Funktion). Die Sample-Komplexität ist das Problem: $\Theta(d^2/\epsilon^2) = \Theta(4^n/\epsilon^2)$ Kopien *selbst mit* kollektiven (verschränkten) Messungen über viele Kopien — exponentiell in $n$. Alles Weitere in diesem Teil existiert, um dieser Skalierung zu entkommen, wenn man gar nicht ganz $\rho$ braucht.

### 3. Shadow-Tomographie und Classical Shadows

**Shadow-Tomographie (Aaronson).** Aufgabenstellung: Gegeben $M$ Zwei-Ausgangs-Observablen, gib alle $\mathrm{Tr}(E_i\rho)$ auf $\pm\epsilon$ genau aus — mit nur $\mathrm{poly}(\log M, n, 1/\epsilon)$ Kopien, wobei $M$ exponentiell sein darf. Der Motor ist das Gentle-Measurement-Lemma (Abschnitt 6): Jede fast-deterministische Schätzung beschädigt den Zustand nur $O(\sqrt{\epsilon})$, also können *dieselben* Kopien viele Fragen beantworten. Sample-effizient — aber die Originalprotokolle sind rechenintensiv und brauchen großen kohärenten Quantenspeicher: Die drei Budgets (Kopien / Zeit / Speicher) fallen hier auseinander.

**Classical Shadows (Huang–Kueng–Preskill): "randomisiere zuerst, frage später".** Pro Kopie: zufälliges $U$ ziehen (zufällige Pauli-Basis pro Qubit oder zufälliger Clifford), messen, den klassischen Schnappschuss

$$\hat\rho = \mathcal{M}^{-1}\big(U^\dagger|b\rangle\langle b|U\big)$$

speichern. Der invertierte Messkanal $\mathcal{M}^{-1}$ (für zufällige Pauli-Basen pro Qubit: $\hat\rho_q = 3\,U^\dagger|b\rangle\langle b|U - \mathbb{1}$) macht den Schätzer unverzerrt, $\mathbb{E}[\hat\rho] = \rho$ — Schüsse in der "falschen" Basis mitteln sich heraus. *Danach* beliebige Observablen mit kleiner Shadow-Norm per Median-of-Means schätzen: $O(\log M \cdot 3^k/\epsilon^2)$ Schüsse für $k$-lokale Paulis (Pauli-Ensemble), $O(\mathrm{Tr}\,O^2)$-artige Kosten für Fidelitäten (Clifford-Ensemble). Single-copy, kein Quantenspeicher, NISQ-tauglich — der Arbeitsgaul der Praxis. Die Lücke: *globale* Observablen ($k \sim n$, z. B. beliebige Pauli-Strings) kosten $3^n$ Schüsse — exponentiell. Genau diese Lücke schließen Zwei-Kopien-Messungen.

### 4. Zwei-Kopien-Messungen: Bell-Sampling, konjugierte Paare, Struktur-Lernen

**Mechanismus.** Die $2n$-Qubit-Bell-Basis $\{(P\otimes\mathbb{1})|\Phi^+\rangle^{\otimes n}\}$ ist die gemeinsame Eigenbasis aller kommutierenden Operatoren $P\otimes\bar P$ (mit $\bar P$ der komplex konjugierten Pauli). Eine transversale Bell-Messung (BSM auf jedem Qubit-Paar) über *zwei Kopien* des Zustands zieht daher pro Schuss einen Pauli-String

$$P \;\sim\; \frac{|\langle\bar\psi|P|\psi\rangle|^2}{2^n}$$

— ein einziger Schuss trägt Information über das *gesamte* Pauli-Spektrum gleichzeitig. **Subtilität der konjugierten Paare:** Auf $\psi\otimes\psi$ sampelt man gegen den *konjugierten* Zustand $\bar\psi$; das saubere Spektrum $\mathrm{Tr}(P\rho)^2/2^n$ erfordert das Paar $(\rho, \bar\rho)$. Für Zustände mit reellen Amplituden fallen beide zusammen (weshalb Demos gern GHZ-Zustände nehmen).

**Konsequenzen.** Reinheit und Überlapp $\mathrm{Tr}(\rho\sigma)$ via Zwei-Kopien-(SWAP-Typ-)Tests — der direkte Messzugang zur Rein/Gemischt-Frage aus Abschnitt 2, ohne Tomographie. Stabilizer-Zustände sind aus $O(n)$ Bell-Samples lernbar (Montanaro). Und vor allem: **Pauli-Shadow-Tomographie mit $\Theta(n)$ Kopien bei Zwei-Kopien-Speicher vs. $2^{\Omega(n)}$ ohne** (Huang–Kueng–Preskill; Chen–Cotler–Huang–Li) — eine der stärksten *bewiesenen* exponentiellen Quantenvorteile, bereits in Hardware demonstriert. Zwei ist der Sweet Spot: Die Ressourcenachse läuft single-copy → two-copy → $k$-copy, und fast der gesamte bekannte Gewinn kommt schon bei 2.

**Struktur-Lernen: Observablen als *Ausgabe*.** Aufgabeninversion — nicht *gegebene* Observablen schätzen, sondern erst die wenigen Observablen *finden*, die die Struktur tragen (den Support eines dünn besetzten Pauli-/Verschiebungsspektrums), dann deren Werte schätzen (erst die Kanten, dann die Gewichte, wie beim Lernen graphischer Modelle). Das Sampling ist die leichte Hälfte: Bell-/Pauli-Sampling konzentriert die Züge genau auf den Support, wenige dominante Strings tauchen nach polynomial vielen Schüssen auf. **Die Decodierung ist die harte Hälfte:** i.i.d.-Samples in den Support zu verwandeln ist Sparse Recovery *ohne wählbare Queries* — und diese Sample-vs-Query-Lücke kann rechnerisch hart sein (LWE-artige Härte), außer auf strukturierten Promise-Klassen (Untergruppen-/Stabilizer-artig → effiziente Decoder). Daher die Disziplin: **immer drei Budgets getrennt angeben** — Kopien (Sample-Komplexität), klassische Zeit, klassischer Speicher. Sample-effiziente Protokolle mit exponentiellen Decodern sind die Norm; dreifache Effizienz ist die Ausnahme.

## Bell Basis Measurements

**Technical Summary of Conjugate Pairs Paper**

In [arXiv:2403.03469](https://arxiv.org/abs/2403.03469) they compute: $y_{q,p}^2$ $\approx \sum_{a,b} $ $p_{a,b}$ $e^{i \frac{2\pi}{d} (a p - b q)}$ (from Fourier-like inversion over Bell measurement statistics)

* $y_{q,p}^2$: displacement coefficient measuring how aligned the signal is with a displacement operator $D_{q,p}$ (conceptually close to Wigner function $W_\rho(q,p)$). Encodes position and momentum of signal -> this we want to estimate

* $p_{a,b}$ = $\text{Tr}[\Pi_{a,b} (\rho \otimes \rho^*)]$ probability of obtaining outcome $(a,b)$ when measuring the joint state $\rho \otimes \rho^*$ in the Bell basis (projecting onto the entangled state $|\Phi_{a,b}\rangle$)

  * $\Pi_{a,b} = |\Phi_{a,b}\rangle \langle \Phi_{a,b}|$ are Bell projectors, projecting onto entangled basis states. For example $\Pi_{0,0} = |\Phi_{0,0}\rangle \langle \Phi_{0,0}|$. And for qubits d=2 Bell basis has 4 Bell states (a,b) $\in$ (0,0), (0,1), (1,0), (1,1).

    * Each Bell state $|\Phi_{a,b}\rangle$ is an **eigenstates** of the observable 'displacement operator' $D_{q,p} \otimes D_{-q,p}$
    * Eigenvalues are **Fourier characters** $\chi_{q,p}(a,b)$ of operator spectrum obtained when measuring in Bell basis - $(a,b)$ live in dual space to position momentum space $(q,p)$ - like what time would be to frequency in Fourier - **We measure in Bell basis because it gives access to the spectrum (Fourier components) of hidden displacement operator!**
    * Measurement probabilities $p_{a,b}$ encode expectation values of dual values (a,b) ($p_{a,b}$ form **characteristic function**) - With entangled Bell measurements we measure probability of $(a,b)$ because they encode the characteristic function $\chi_{q,p}(a,b)$.
    * Applying Fourier inversion $\chi_{q,p}(a,b) = e^{i\frac{2\pi}{d}(a p - b q)}$ recovers $y_{q,p}^2$ in measurement domain to estimate displacements $(q,p)$

  * $\rho \otimes \rho^*$: conjugate pair allows access to structured correlation and commuting extensions. We use the complex conjugate to ensure that the Bell measurements access bilinear correlations between $\rho$ and $\rho^*$, which encode the squared modulus of the Fourier component — i.e., $y_{q,p}^2$.
  
    * $\rho_{q,p,r} = \frac{1}{d} \left( I + r \cdot \varepsilon \cdot E_{q,p} \right)$ is quantum state with random background and small structured deviation injected where $E_{q,p} = D_{q,p} \sigma D_{q,p}^\dagger$. From this, we construct the conjugate pair as the tensor product $\rho_{q,p,r} \otimes \rho_{q,p,r}^*$

  
* $e^{i \frac{2\pi}{d} (a p - b q)}$ = $\chi_{q,p}(a,b)$ is the character (Fourier phase factor or fourier transform kernel) to turn our characteristic function details back into a Wigner-like $y_{q,p}^2$ position and momentum information.


## Displacement Operators $D_{q,p} \otimes D_{-q,p}$ and Conjugate Pair States $\rho \otimes \rho^*$

* $\rho$ is single-copy quantum state whose displacement amplitudes $y_{q,p} = \text{Tr}(D_{q,p}\rho)$ we want to know
* $D_{q,p}$ is displacement operator
  * **Problem 1**: $D_{q,p}$ non-Hermitian for $d>2$, so complex Eigenvalues $→$ cannot be directly measured on single copy $\rho$.
  * **Problem 2**: $D_{q,p}$ for different (q, p) indices do not commute with each other due to commutation relation $D_{q',p'} D_{q,p} = e^{i2\pi(q'p - qp')/d} D_{q,p} D_{q',p'}$. Incompatible observables, can't be measured simultaneously on single copy $\rho$.
* $D_{q,p} \otimes D_{-q,p}$ is constructed Hermitian operator $O_{q,p}$
  * **Solves 1**: has real Eigenvalues on joint system (are Hermitian because operators are related by transposition and conjugation)
  * **Solves 2**: Set of all joint operators $O_{q,p}$ mutually commute $\{D_{q,p} \otimes D_{-q,p}\}$ $\rightarrow$ allows simultaneous measurement of all $O_{q,p}$ observables in shared Eigenbasis (= generalized Bell basis $\{|\Phi_{a,b}\rangle\}$)
* $\rho \otimes \rho^*$ constructed two-copy physical state ('conjugate pair') that exists in same two-qudit composite system as observable $O_{q,p}$. Forces measured expectation value to be exactly $(y_{q,p})^2$. Works because of identity: $\text{Tr}(D_{-q,p}\rho^*) = \text{Tr}(D_{q,p}^T \rho^*) = \text{Tr}(D_{q,p}\rho)$. Meanwhile two identical copies $\rho$ does not work: $\text{Tr}(D_{-q,p}\rho) \ne \text{Tr}(D_{q,p}\rho)$ does not simplify to $(y_{q,p})^2$
* $E = (D_{q,p} \otimes D_{-q,p}) (\rho \otimes \rho^*) = |y_{q,p}|^2$ measures expectation value, extracts real amplitude $y_{q,p}$ squared

$\begin{array}{rcl} E & = & \text{Tr}(D_{q,p}\rho) \cdot \text{Tr}(D_{-q,p}\rho^*) & \quad \text{(Separation of Trace)} \\ & = & \text{Tr}(D_{q,p}\rho) \cdot \text{Tr}(D_{q,p}^T\rho^*) & \quad \text{(Using transpose of} D_{q,p}: D_{q,p}^T = D_{-q,p} \text{ (operator identity)} \\ & = & \text{Tr}(D_{q,p}\rho) \cdot \text{Tr}(D_{q,p}\rho) & \quad \text{(Using } \text{Tr}(A^T B^*) = \text{Tr}(AB) \text{ (matrix identity)} \\ & = & (\text{Tr}(D_{q,p}\rho))^2 = (y_{q,p})^2 & \quad \text{(Symmetry at (q, p) and (-q, -p) due to $D_{q,p}^\dagger = D_{-q,-p}$)} \end{array}$

## Displacement Operators

* Commutation relations: $D_{q',p'} D_{q,p} = e^{i 2\pi (qp' - q'p)/d} D_{q,p} D_{q',p'}$
* $\{D_{q,p} \otimes D_{-q,p}\}$ mutually commute

<br>

$
\begin{array}{ccc}
D_{q,p}^T = D_{-q,p} & p & D_{q,p} \\
\nwarrow & \uparrow & \nearrow \\
\longleftarrow & + & \longrightarrow q \\
\swarrow & \downarrow & \searrow \\
D_{q,p}^{-1} = D_{q,p}^\dagger = D_{-q,-p} &  & D_{q,p}^* = D_{q,-p}
\end{array}
$

<br>

* Shadow tomography on set of **displacement operators.**
* Hilbert space $\mathbb{C}^d$.
* Unknown quantum state $\rho$.

$
X = \begin{pmatrix}
0 & 0 & \dots & 0 & 1 \\
1 & 0 & \dots & 0 & 0 \\
\vdots & \vdots & \ddots & \vdots & \vdots \\
0 & 0 & \dots & 1 & 0
\end{pmatrix}
\quad \quad \quad
Z = \begin{pmatrix}
1 & 0 & \dots & 0 \\
0 & \omega & \dots & 0 \\
\vdots & \vdots & \ddots & \vdots \\
0 & 0 & \dots & \omega^{d-1}
\end{pmatrix}
$

* Want $\text{Tr}(D_{q,p}\rho) \pm \varepsilon$ for every $q,p$.

$
\begin{array}{ccc}
 & p & \\
 & \uparrow & \Large{\color{red}\bullet} \normalsize \; D_{q,p} \\
 & | & \nearrow \\
\text{---} & \Large{\color{red}\bullet} & \text{------} \longrightarrow q \\
 & | &
\end{array}
$

$
D_{q,p} = e^{i\pi qp/d} X^q Z^p
$

* Video: [Exponential learning advantages with conjugate states and minimal | King, Wan and McClean | TQC 2024](https://www.youtube.com/watch?v=koyFydFJiFQ$0)
* Video: [Complex conjugates | Imaginary and complex numbers | Precalculus | Khan Academy](https://www.youtube.com/watch?v=BZxZ_eEuJBM$0)

## Displacement Operators for Signal Detection (Magnitude and Sign)

* **Goal**: We want to use this to test at which fundamental frequency the molecule (quantum state) mainly resonates
* **What**: Resonance in each frequency is built from oscillations of different energy levels $n$ (quantum number) in molecule or state:
  * A **specific (q,p)** is one fundamental frequency. We check for all, where does the molecules resonate strongest?
  * At a specific frequency (q,p), Ground state may oscillate with contribution 4, and first excited state with contribution -2.
  * **Magnitude** is absolute sum (expectation value) of all contributions within one fundamental frequency,
  * **Sign** is direction of sum. It is weighted average (+4-2..). Shows if it aligns or anti-aligns with fundamental frequency
  * **Signal** (Trace, Expectation value) is largest, complex sum of all contributions. We do this for all p,q: $D_{3,5}$=-2, $D_{6,9}$=+8.
  * **Displacement operator $D_{q,p}$** is interferometer where each p,q represents one fundamental frequency.
* **How:** Measure quantum state overlap with each q,p.
  * $D_{q,p}$ **displaces/translates/evolves** state by $p,q$, and **measures overlap** with original (interferometry). Signal = $\langle \psi | D_{q,p} | \psi \rangle$ = $\text{Tr}(D_{q,p} \rho)$. ($D_{q,p}$ is unitary. It evolves or rotates the state. Physically: it takes the existing state and moves it in phase space.)
  * High overlap = quantum state resonates in this frequency =  **state repeats itself** if shifted by vector $(q,p)$.
  * **Magnitude**: Autocorrelation (Self-Similarity) under shifting. **Sign**: Phase of that overlap (Constructive/Destructive).
  * Result: **Displacement Map = Correlation Map** of fundamental frequencies with quantum state (not Spatial Map!)
* **Math:** Magnitude + Sign = Expectation Value. For $D_{q,p}$ and state $\sigma$, expectation value is **full complex number** $z$:
  * **$z$ is the arrow**: $z$ = $x + iy$ = $r \cdot e^{i\theta}$ = $\text{Tr}(D_{q,p} \sigma)$ = $\langle \psi | D_{q,p} | \psi \rangle$
  * **$|z|$ or $r$ is magnitude** - How long the arrow is? (absolute length of vector). Strength of whole complex number ($x+iy$)
  * **$e^{i\theta}$ is full phase** - Where arrow $z$ points? Has real + imaginary part corresponding to Hermitian parts of $D_{q,p}$:
    * **Real Part: Cosine Wave** (Quadrature:) $\text{Re}[z] = \text{Tr}(A\rho)$, where $A = \frac{1}{2}(D_{q,p} + D_{q,p}^\dagger)$.
    * **Imaginary Part: Sine Wave** (Quadrature): $\text{Im}[z] = \text{Tr}(B\rho)$, where $B = \frac{1}{2i}(D_{q,p} - D_{q,p}^\dagger)$.
  * Problem: $D_{q,p}$ is unitary (complex). But Real Part corresponds to Hermitian $S_{q,p} = \frac{1}{2}(D_{q,p} + D_{q,p}^\dagger)$ $\sim \cos(q\hat{P} - p\hat{Q})$.
  * **Sign**: Simplified to: Real part $x$ (cosine wave) in $z = x + iy$ = $\text{Tr}(D_{q,p} \sigma)$ = $r \cdot e^{i\theta}$: Is it positive or negative? (Binary) = Does state $\rho$ resonates with Cosine wave $\cos(q\hat{P} - p\hat{Q})$ of frequency $(q,p)$ in phase space? Calculated as sign of real part of expectation value: Sign $\equiv$ Sign of $(\text{Re}[z])$ = Sign of $ (\text{Re}[\text{Tr}(D_{q,p} \rho)])$ or $(\text{Re}[\langle \psi | D_{q,p} | \psi \rangle])$
* **Playground**: Displacement Operators focus on [Vibrational Spectroscopy](https://chem.libretexts.org/Courses/Providence_College/Organic_Chemistry_I/05%3A_Analytical_Methods_for_Structure_Elucidation/5.04%3A_Infrared_Spectroscopy) like IR Spectroscopy:
  * movement (vibrations) of nuclei with Stretching and Bending (C-H bond) -> atoms oscillating in natural frequency, for example $\omega = \frac{E_{n+1} - E_n}{\hbar}$ = $3000 \text{ cm}^{-1}$. System jumps between Eigenstates -> molecule in vibrational levels ($n=1, 2, 3...$) = [Franck-Condon Factors](https://de.wikipedia.org/wiki/Franck-Condon-Prinzip) (shift in nuclear equilibrium described by displacement operator).
  * Vibrational Spectroscopy measures only bond oscillation (gap) between $v=0$ and $v=1$ and one at a time (single energy transitions) in 1D map. Displacement Operators measure shape to uncover quantumness (Wigner negativity with molecule in superposition or many nodes) + many bond vibrations simultaneously on 2D topological phase-space map.
* **Approach** Displacement Operator $(q,p)$ performs Phase Space Tomography (interferometry) to reconstruct Density Operator $\rho$.  
  * Measure overlap of molecule's state with shifted version of itself. Calculates expectation value $y_{q,p} = \text{Tr}(\rho\hat{D}(q,p))$ or $\chi(q,p) = \text{Tr}(\hat{\rho} \hat{D}(q,p))$. $\chi$ is **Characteristic Function** of state. **Fourier transform is Wigner Function** $W(q,p)$ > 2D map.
  * **Laguerre polynomials** $\langle n | \hat{D}(\alpha) | n \rangle = L_n(|\alpha|^2) e^{-|\alpha|^2/2}$ (where $\alpha \propto q + ip$) determine Expectation value of a displacement operator $y_{q,p} = \text{Tr}(D_{q,p}\rho)$ for a specific energy level $n$. Laguerre polynomials $L_n$ can be positive or negative depending on the radius $|\alpha|$. High-energy states are energetic, their response to specific $(q,p)$ probe different than ground state -> signal (expectation value) is (Laguerre) polynomial than just simple constant.
