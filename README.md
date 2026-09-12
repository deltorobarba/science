# Quantum Learning

Alexander Del Toro Barba, PhD. [Google Scholar](https://scholar.google.com/citations?hl=en&user=fddyK-wAAAAJ) $\cdot$ [LinkedIn](https://www.linkedin.com/in/deltorobarba/)

<img src="https://raw.githubusercontent.com/deltorobarba/science/main/science.JPG" alt="science">


## 1. Was ist „Learning from Quantum Experiments"?

**Messtheorie vs. Lerntheorie.** Die Messtheorie beantwortet die Einzelschuss-Frage: Was tut eine Messung mit einem Zustand, welche Statistik erzeugt sie? Die Lerntheorie stellt die inverse, statistische Frage: *Was lässt sich aus vielen Messungen über ein unbekanntes $\rho$ herausfinden, und zu welchen Kosten?* Die Born-Regel macht den Zustand zum Sampling-Orakel; Lernen ist das Inversproblem dazu.

**Definition.** Gegeben Zugriff auf Kopien eines unbekannten Quantenobjekts (Zustand $\rho$, Kanal $\mathcal{E}$, Hamiltonian $H$), erzeugt von der Natur, einem Sensor oder einem Quantengerät: *Welche* Eigenschaften kann ein Lerner extrahieren, zu *welchen* Kosten in Kopien, klassischer Zeit und Speicher, und wie verändern Quantenressourcen (Quantenspeicher, verschränkte Messungen, Adaptivität) diese Kosten?

### Die Datenquelle entscheidet, nicht die Hardware

Das Feld ist die **untere Zeile** der Daten-vs-Lerner-Matrix:

| | Classical Learners | Quantum Enhanced Learners |
| --- | --- | --- |
| **Klassische Daten** | klassisches ML | „QML on classical data": Feature Maps, variationelle Klassifikatoren, Quantum Kernels |
| **Quantendaten** (Kopien von $\rho$ / Kanälen) | **Messprotokoll + klassische Statistik: Shadows, Bell-Sampling + klassische Decoder** | Quantenspeicher-Protokolle: kohärente Zwei-/Multi-Kopien-Messungen |

Drei Lackmustests trennen die Zeilen scharf:

1. **Wo lebt das Unbekannte?** Dichteoperator/Kanal vs. klassischer Datensatz.
2. **Ist „Anzahl der Kopien" eine sinnvolle Kostengröße?** Quantendaten sind nicht klonbar, jede Kopie kostet. Klassische Daten sind beliebig kopierbar.
3. **Binden die Informationsgrenzen?** No-Cloning, Holevo und Gentle Measurement machen Lernen aus Quantendaten nichttrivial. Auf ein CSV-File greifen sie nicht.

**Warum die Trennung wichtig ist (Power of Data).** In der oberen Zeile sind Vorteilsbehauptungen fragil: klassisches ML mit genügend Trainingsdaten holt Quantenmodelle auf klassischen Aufgaben ein (Huang et al., Nat. Commun. 2021). In der unteren Zeile stehen die *bewiesenen* exponentiellen Separationen, inklusive Hardware-Demonstration.

**Grauzonen.** (a) *Engineerte Zustände:* Ob $\rho$ von einem Molekül oder einem Prozessor stammt, ist egal; Gerätecharakterisierung und Rauschlernen gehören nativ zum Feld. (b) *Simulatoren:* Das Zugriffsmodell bleibt das eines Quantenexperiments; die Sample-Komplexität ist simulator-invariant. (c) *Hybride:* Ein neuronales Netz, das Quantenmessdaten dekodiert, sitzt unten links.

---

## 2. Perspektiven auf das Feld

### 2.1 Nach Ressourcen

| Axis | Spectrum | Key Separation / Benchmark |
| --- | --- | --- |
| **Quantum Memory** | $1 \to 2 \to k$ copies coherent | Pauli spectrum: $\Theta(n)$ copies (2-copy) vs. $2^{\Omega(n)}$ (1-copy) |
| **Adaptivity** | Fixed $\leftrightarrow$ dynamic settings | Exponential sample savings for non-local property testing |
| **Conjugate Access** | $\rho$ only $\leftrightarrow (\rho, \rho^*)$ | Clean spectrum $\mathrm{Tr}(P\rho)^2$ via conjugate pairs; constant memory |
| **Budgets** | Samples / Time / Memory | Sample-efficient with exponential classical decoders is the default |
| **Data Access** | i.i.d. draws $\leftrightarrow$ active queries | LWE-hardness: states can be sample-learnable but computationally hidden |

Die letzten beiden Achsen sind die aktuelle Front: Fast alle Separationen sind *Sample*-Aussagen. Ob die Daten auch *effizient verarbeitbar* sind, ist weit weniger kartiert. Die Sample-vs-Query-Lücke ist fundamental, nicht technisch: Unter Standard-Kryptoannahmen gibt es keine generische Konversion.

| Zugriffstyp | Status bei LWE | Ursache |
| --- | --- | --- |
| **Sampling Access** | **Hard (Post-Quantum)** | Keine Kontrolle über $\mathbf{a}_i$; algebraische Elimination führt zu Fehleranhäufung, die das Signal zerstört |
| **Query Access (Superposition)** | **Easy (Bernstein-Vazirani / QFT)** | Gezielte Superpositionen ermöglichen Interferenz via QFT; Rauschen bleibt isoliert |

### 2.2 Nach Aufgabe: Schätzen vs. Suchen

Die Rolle der Observablen trennt die Aufgaben am schärfsten:

* **Full Tomography:** „Gib mir alle $d^2$ Parameter." Wie das ganze Genom sequenzieren.
* **Schätzen** (Observablen sind *Eingabe*): „Gib mir die Werte dieser $M$ Observablen." Wie ein Panel vordefinierter SNPs.
* **Suchen** (Observablen sind *Ausgabe*): „Finde, welche Observablen überhaupt relevant sind, dann ihre Werte." Wie eine GWAS. Echt schwerer: Die Schätz-Garantien decken das nicht, und hier sitzt die LWE-Härte.

| Task | Observables | Target Output | Sample Complexity ($n$ qubits, $d=2^n$) |
| --- | --- | --- | --- |
| **Full QST** | All | Full density matrix $\rho$ | $\Theta(d^2/\epsilon^2)$ (entangled) / $\Theta(d^3/\epsilon^2)$ (single-copy) |
| **Shadow Tomography** | Input list ($M$ given) | $M$ expectation values $\mathrm{Tr}(O_i\rho)$ | $\mathrm{poly}(\log M, n, 1/\epsilon)$ |
| **Classical Shadows** | Chosen post-measurement | Arbitrary small shadow-norm $\langle O\rangle$ | $O(\log M \cdot 3^k/\epsilon^2)$ for $k$-local Paulis |
| **Bell / Pauli Sampling** | Sampled dynamically | Draws $P \sim \vert{}\langle\bar\psi\vert{}P\vert{}\psi\rangle\vert{}^2/2^n$ | $O(n)$ two-copy shots (stabilizer support) |
| **Structure Learning** | Discovered (output) | Support + values of sparse spectrum | $\mathrm{poly}(n)$ samples; classical decoding often hard |
| **State Discrimination** | 2 candidates $(\rho_0, \rho_1)$ | Identity index | Helstrom (min error) vs. USD (zero error + abort) |
| **Hypothesen-Selektion** | Liste gegeben | ein Index | $O(\log M)$ Kopien |

### 2.3 Drei Budgets, immer getrennt

Kopien (Sample-Komplexität), klassische Zeit, klassischer Speicher skalieren unabhängig. Sample-effiziente Protokolle mit exponentiellen Decodern sind die Norm; **dreifache Effizienz** ist die Ausnahme.

### 2.4 Einordnung des eigenen Projekts

* **Feld:** Quantenvorteile beim Lernen physikalischer Systeme aus Messdaten, mit minimalem Quantenspeicher (nie mehr als zwei Kopien).
* **Ansatz:** *Machine-learned decoders for quantum measurement data.* Ein trainiertes Modell ersetzt handgebaute Kombinatorik (Graph-Coloring, Matrix Multiplicative Weights) und nutzt die Struktur der Zustandsklasse. Überträgt sich auf Hamiltonian Learning, Rauschcharakterisierung, Fehlerkorrektur-Decoder.
* **Beitrag:** Computationally efficient **structure learning** dünner Displacement-Spektren aus Zwei-Kopien-Bell-Messungen. Triply efficient, als Promise-Problem, mit beweisbaren Instanzen (Dictionary-, Subgruppen-Klassen) und beweisbarer Grenze (LWE-Härte der generischen Lokalisierung).
* **Struktur:** Jedes Protokoll zerfällt in *Quantenfrontend* (welche Messung auf wie vielen Kopien) und *klassischen Decoder*. Der Fehler faktorisiert in Lokalisierung und Schätzung. Vorn konjugierte Bell-Paare, hinten gelernter CNN-Decoder plus sequentieller Vorzeichen-Integrator.

---

## 3. Die Protokolle: Technik und Literatur

Alles hier sind *Protokolle über Messungen*, keine neuen Messtypen. Sie sortieren sich entlang zweier Achsen: Kopien pro Schuss ($1, 2, k$) und Observablen als Eingabe oder Ausgabe.

### 3.1 Zustandsdiskriminierung: Helstrom vs. USD

Gegeben $\rho_0, \rho_1$ mit Prioren $p_0, p_1$: Welche liegt vor? Zwei Strategien mit unterschiedlichem Fehlerbegriff.

* **Helstrom (Minimum-Error):** Antwort in jedem Durchlauf, mittlerer Fehler minimiert. Projektive Messung auf das Vorzeichenspektrum von $p_0\rho_0 - p_1\rho_1$:

$$P_{\text{err}}^{\min} = \tfrac{1}{2}\Big(1 - \big\|p_0\rho_0 - p_1\rho_1\big\|_1\Big)$$

* **USD (Unambiguous):** Dritter Ausgang „unentschieden", entschiedene Antworten nie falsch. Erfordert eine echte POVM; Preis ist die Enthaltungswahrscheinlichkeit, minimal $|\langle\psi_0|\psi_1\rangle|$.

### 3.2 Full QST: die exponentielle Basislinie

Rekonstruiert alle $d^2$ Parameter aus einem informationsvollständigen Messsatz (DV: alle $3^n$ Pauli-Basen oder eine SIC-POVM; CV: Homodyn-Scan und inverse Radon-Transformation zur Wigner-Funktion). Kosten $\Theta(d^2/\epsilon^2) = \Theta(4^n/\epsilon^2)$ selbst mit verschränkten Messungen. Alles Weitere existiert, um dieser Skalierung zu entkommen.

* **Haah et al. / O'Donnell–Wright (STOC 2016):** $\Theta(d^2/\epsilon^2)$ optimale verschränkte Tomographie.
* **Chen et al. (2022):** $\Theta(d^3/\epsilon^2)$ Single-Copy-Untergrenze, beweist die Lücke zu verschränkten Messungen.

### 3.3 Shadow-Tomographie und Classical Shadows (Observablen als Eingabe)

* **Shadow-Tomographie (Aaronson):** $M$ Observablen auf $\pm\epsilon$ mit $\mathrm{poly}(\log M, n, 1/\epsilon)$ Kopien, $M$ darf exponentiell sein. Motor ist das Gentle-Measurement-Lemma: Fast-deterministische Schätzungen beschädigen den Zustand nur $O(\sqrt{\epsilon})$, dieselben Kopien beantworten viele Fragen. Sample-effizient, aber rechen- und speicherintensiv.
* **Classical Shadows (Huang–Kueng–Preskill):** „Randomisiere zuerst, frage später." Pro Kopie zufälliges $U$ (Pauli-Basis pro Qubit oder Clifford), messen, Schnappschuss speichern:

$$\hat\rho = \mathcal{M}^{-1}\big(U^\dagger|b\rangle\langle b|U\big), \qquad \mathbb{E}[\hat\rho] = \rho$$

  Danach beliebige Observablen per Median-of-Means: $O(\log M \cdot 3^k/\epsilon^2)$ Schüsse für $k$-lokale Paulis. Single-copy, NISQ-tauglich, der Arbeitsgaul der Praxis. Lücke: *globale* Observablen ($k \sim n$) kosten $3^n$ Schüsse. Genau die schließen Zwei-Kopien-Messungen.
* **Triple Efficiency:** Sample- *und* Zeiteffizienz mit $O(1)$-Kopien-Quantenspeicher.

Literatur:
* **Aaronson (STOC 2018):** Shadow tomography via Gentle Measurements, $\tilde{O}(\log^4 M)$ Kopien.
* **Huang, Kueng, Preskill (Nat. Phys. 2020):** Classical Shadows.
* **King, Gosset, Kothari, Babbush (2024):** Triply efficient shadow tomography für lokale fermionische und Pauli-Observablen.

### 3.4 Zwei Kopien: Bell-Sampling, konjugierte Paare, Quantenspeicher

**Mechanismus.** Die $2n$-Qubit-Bell-Basis $\{(P\otimes\mathbb{1})|\Phi^+\rangle^{\otimes n}\}$ ist die gemeinsame Eigenbasis aller kommutierenden $P\otimes\bar P$. Eine transversale Bell-Messung über zwei Kopien zieht pro Schuss einen Pauli-String

$$P \sim \frac{|\langle\bar\psi|P|\psi\rangle|^2}{2^n}$$

Ein Schuss trägt Information über das *gesamte* Pauli-Spektrum. **Subtilität:** Auf $\psi\otimes\psi$ sampelt man gegen den *konjugierten* Zustand $\bar\psi$. Das saubere Spektrum $\mathrm{Tr}(P\rho)^2/2^n$ erfordert das Paar $(\rho, \bar\rho)$. Für reelle Amplituden fallen beide zusammen (deshalb nehmen Demos gern GHZ-Zustände).

**Konsequenzen.** Reinheit und Überlapp $\mathrm{Tr}(\rho\sigma)$ via SWAP-Tests ohne Tomographie. Stabilizer-Zustände aus $O(n)$ Bell-Samples lernbar. Vor allem: **Pauli-Shadow-Tomographie mit $\Theta(n)$ Kopien bei Zwei-Kopien-Speicher vs. $2^{\Omega(n)}$ ohne.** Einer der stärksten bewiesenen exponentiellen Quantenvorteile, in Hardware demonstriert. Zwei ist der Sweet Spot: Fast der gesamte bekannte Gewinn kommt schon bei $k=2$.

Literatur:
* **Bubeck, Chen, Li (FOCS 2020):** Verschränkung notwendig für optimales Property Testing.
* **Chen, Cotler, Huang, Li (FOCS 2021):** $\Theta(n)$ vs. $2^{\Omega(n)}$ Separation mit Quantenspeicher.
* **Huang et al. (Science 2022):** Flagship-Separationen und Sycamore-Demo mit 40 Qubits.
* **King, Wan, McClean (2024):** Exponentieller Vorteil via $(\rho, \rho^*)$ mit konstantem Speicher.
* **Chen, Gong, Zhang (2024):** Separationen für adaptive Multi-Copy-Shadow-Tomographie.

### 3.5 Struktur-Lernen (Observablen als Ausgabe)

**Aufgabeninversion:** Erst die wenigen Observablen *finden*, die den Support eines dünnen Pauli-/Displacement-Spektrums tragen, dann ihre Werte schätzen (erst die Kanten, dann die Gewichte, wie beim Lernen graphischer Modelle). Das Sampling ist die leichte Hälfte: Bell-Sampling konzentriert die Züge auf den Support. **Die Decodierung ist die harte Hälfte:** i.i.d.-Samples in den Support zu verwandeln ist Sparse Recovery *ohne wählbare Queries*, generisch kryptographisch hart (LWE-artig). Subgruppen-/Stabilizer-Symmetrien sind die tractable Ausnahme.

* **Montanaro (2017):** Stabilizer-Zustände aus $O(n)$ Bell-Samples via lineare Algebra.
* **Grewal, Iyer, Kretschmer, Liang (2023):** Bell difference sampling, Zustände mit wenigen Non-Clifford-Gates.
* **Hangleiter, Gullans (PRL 2024):** Bell-Sampling als universelles Diagnostik-Framework.

### 3.6 Computational Lens: Härte und Pseudozufall

Pseudorandom States (PRS) zeigen: Zustände können statistisch lernbar, aber rechnerisch nicht von Haar-zufälligen unterscheidbar sein.

* **Regev (2005):** Learning With Errors, Fundament der Average-Case-Härte.
* **Ji, Liu, Song (CRYPTO 2018):** Pseudorandom Quantum States.
* **Kretschmer (TQC 2021):** Quanten-Pseudozufall und klassische Lernhärte.
* **Huang, Broughton et al. (Nat. Commun. 2021):** *Power of data*: klassische Daten schließen Quantenvorteile beim Lernen klassischer Funktionen.

### 3.7 Dynamik lernen: Hamiltonians, Kanäle, Schaltkreise

Unbekannte Terme und Kopplungsgraphen aus Gibbs-Zuständen oder Echtzeit-Dynamik bis zum Heisenberg-Limit; Pauli-Rauschen in Kanälen; Shallow Circuits in Polynomialzeit.

* **Flammia, Wallman (TQC 2020):** Effiziente Pauli-Kanal-Schätzung.
* **Anshu et al. (Nat. Phys. 2021) / Haah et al. (FOCS 2022):** Optimale Sample-Komplexität für Gibbs-State-Hamiltonian-Learning.
* **Huang et al. (PRL 2023):** Heisenberg-limitiertes Hamiltonian Learning aus Echtzeit-Evolution.
* **Huang et al. (STOC 2024):** Polynomialzeit-Rekonstruktion flacher Schaltkreise.

### 3.8 Machine-Learned Decoders

Klassische neuronale Decoder auf Shadow-Daten (Quadrant unten links) als empirische Heuristik für klassisch harte Decodier-Aufgaben.

* **Torlai et al. (Nat. Phys. 2018):** Neural-network QST.
* **Huang, Kueng, Torlai, Albert, Preskill (Science 2022):** Beweisbare Generalisierungsschranken für ML auf Shadow-Daten.
* **Huang, Preskill, Soleimanifar (2024):** Zustandszertifizierung via Single-Qubit-Shadow-Relaxationen.

### 3.9 Surveys und Timeline

* **Anshu, Arunachalam (Nat. Rev. Phys. 2024):** Kanonischer Survey zur State-Learning-Komplexität.
* **Gebhart et al. (Nat. Rev. Phys. 2023):** Review zum Lernen von Quantendynamik in Experimenten.
* **Arunachalam, de Wolf (SIGACT 2017):** Quantum PAC Learning.

| Zeitraum | Meilensteine |
| --- | --- |
| 1998–2007 | Quantum PAC (Bshouty–Jackson) · LWE (Regev) · State PAC learnability (Aaronson) |
| 2016 | Sample-optimale Tomographie $\Theta(d^2/\epsilon^2)$ |
| 2017–2018 | Shadow tomography · Stabilizer Bell sampling · PRS |
| 2020 | Classical shadows · Entanglement lower bounds |
| 2021–2022 | Memory-Separationen · Sycamore-Demo · Shallow circuit learning |
| 2023–2024 | Heisenberg Hamiltonian learning · Triply efficient shadows · Conjugate pairs · Agnostic tomography |
| 2025–2026 | Agnostic tomography · Noise-robust 2-copy hardware · Physical average-case decodability |

---

## 4. Offene Fronten

* **Kartierung der dekodierbaren Klassen.** Zwischen „Subgruppen-leicht" (lineare Algebra) und „LWE-hart" liegt unvermessenes Gebiet. Derselbe Zustand wandert durch Aufdrehen eines Rauschparameters vom leichten ins harte Regime. Offen: Überträgt sich die Härte-Reduktion von der Tensor-Produkt-Basis auf die zyklische Ein-Qudit-Basis?
* **Was gelernte Decoder implizit finden.** Funktioniert ein Decoder auf einer Klasse ohne bekannten effizienten Algorithmus, hat er möglicherweise einen gefunden. ML als Werkzeug der Algorithmen-Entdeckung; gesucht ist eine Metrik, die Generalisierung über Zustandsverteilungen vorhersagt.
* **Hardware-Realismus bei zwei Kopien.** Approximate matched filters (Probe-Gain $\kappa < 1$, Mehrkosten $\kappa^{-2}$) machen Protokolle graceful gegenüber Präparations-, Crosstalk- und Messfehlern. Die praktisch relevanteste Achse.
* **Average-Case statt Worst-Case.** Die Härte-Resultate sind adversarial. Natürliche Zustände (Grundzustände lokaler Hamiltonians, thermische Zustände) könnten generisch dekodierbar sein: von der Kryptographie- zur Physik-Perspektive.

---

## 5. Technik: Displacement-Operatoren und konjugierte Paare

Kern des Papers [arXiv:2403.03469](https://arxiv.org/abs/2403.03469) (King, Wan, McClean): Shadow-Tomographie auf der Menge der **Displacement-Operatoren** eines Qudits, gewünscht $\mathrm{Tr}(D_{q,p}\rho) \pm \varepsilon$ für alle $(q,p)$.

### 5.1 Heisenberg-Weyl-Operatoren

$$D_{q,p} = e^{i\pi qp/d}\, X^q Z^p, \qquad X|k\rangle = |k+1\rangle, \quad Z|k\rangle = \omega^k|k\rangle, \quad \omega = e^{2\pi i/d}$$

* Kommutation: $D_{q',p'} D_{q,p} = e^{i 2\pi (qp' - q'p)/d} D_{q,p} D_{q',p'}$
* Symmetrien im Phasenraum: $D_{q,p}^T = D_{-q,p}$, $\;D_{q,p}^* = D_{q,-p}$, $\;D_{q,p}^\dagger = D_{q,p}^{-1} = D_{-q,-p}$

### 5.2 Warum $\rho \otimes \rho^*$ und nicht $\rho \otimes \rho$

Zwei Probleme auf einer Kopie:

1. $D_{q,p}$ ist für $d>2$ **nicht hermitesch**: komplexe Eigenwerte, nicht direkt messbar.
2. Verschiedene $D_{q,p}$ **kommutieren nicht**: nicht simultan messbar.

Lösung: Der Joint-Operator $O_{q,p} = D_{q,p} \otimes D_{-q,p}$ ist hermitesch, und alle $O_{q,p}$ kommutieren untereinander. Ihre gemeinsame Eigenbasis ist die generalisierte Bell-Basis $\{|\Phi_{a,b}\rangle\}$. Auf dem konjugierten Paar liefert der Erwartungswert exakt das Quadrat:

$$E = \mathrm{Tr}(D_{q,p}\rho)\cdot\mathrm{Tr}(D_{-q,p}\rho^*) = \mathrm{Tr}(D_{q,p}\rho)\cdot\mathrm{Tr}(D_{q,p}^T\rho^*) = \mathrm{Tr}(D_{q,p}\rho)^2 = y_{q,p}^2$$

**Der entscheidende Schritt** ist keine Eigenschaft von $D$, sondern von $\rho$: Weil $\rho$ hermitesch ist, gilt $\rho^* = (\rho^\dagger)^T = \rho^T$. Damit

$$\mathrm{Tr}(D^T\rho^*) = \mathrm{Tr}(D^T\rho^T) = \mathrm{Tr}((\rho D)^T) = \mathrm{Tr}(\rho D) = \mathrm{Tr}(D\rho)$$

Mit zwei identischen Kopien $\rho\otimes\rho$ funktioniert das nicht: $\mathrm{Tr}(D_{-q,p}\rho) \neq \mathrm{Tr}(D_{q,p}\rho)$. Die komplexe Konjugation wird hier als **physikalische Ressource** genutzt: Statt $y_{q,p}$ zu schätzen und klassisch zu quadrieren (statistisch teuer), liefert die Hardware das Betragsquadrat direkt.

### 5.3 Bell-Basis als Fourier-Zugang

Die Bell-Messung auf $\rho\otimes\rho^*$ liefert Wahrscheinlichkeiten $p_{a,b} = \mathrm{Tr}[\Pi_{a,b}(\rho\otimes\rho^*)]$. Jeder Bell-Zustand $|\Phi_{a,b}\rangle$ ist Eigenzustand von $D_{q,p}\otimes D_{-q,p}$ mit Eigenwert gleich dem **Fourier-Charakter** $\chi_{q,p}(a,b) = e^{i\frac{2\pi}{d}(ap - bq)}$. Die $(a,b)$ leben im Dualraum zu $(q,p)$, wie Zeit zu Frequenz. Fourier-Inversion gibt das Spektrum zurück:

$$y_{q,p}^2 \approx \sum_{a,b} p_{a,b}\, e^{i\frac{2\pi}{d}(ap - bq)}$$

Man misst in der Bell-Basis, weil sie Zugang zum Spektrum des versteckten Displacement-Operators gibt.

### 5.4 Physikalische Lesart: Interferometer im Phasenraum

* $D_{q,p}$ **verschiebt** den Zustand um $(q,p)$ im Phasenraum; $y_{q,p} = \langle\psi|D_{q,p}|\psi\rangle$ ist der **Überlapp** mit dem verschobenen Selbst (Autokorrelation). Hoher Überlapp heißt: der Zustand „resoniert" bei dieser Frequenz.
* $y_{q,p} = r e^{i\theta}$ ist komplex. **Magnitude** $r$: Stärke der Selbstähnlichkeit. **Sign**: Vorzeichen des Realteils $\mathrm{Re}[y] = \mathrm{Tr}(A\rho)$ mit $A = \tfrac12(D + D^\dagger) \sim \cos(q\hat P - p\hat Q)$. Konstruktiv oder destruktiv?
* Die Karte $(q,p) \mapsto y_{q,p}$ ist die **charakteristische Funktion** $\chi(q,p)$ des Zustands. Ihre Fourier-Transformierte ist die **Wigner-Funktion**. Eine Displacement-Map ist also eine Korrelationskarte, keine räumliche Karte.
* Für Energie-Eigenzustände gilt $\langle n|D(\alpha)|n\rangle = L_n(|\alpha|^2)e^{-|\alpha|^2/2}$ mit **Laguerre-Polynomen**, die je nach Radius positiv oder negativ sind. Angeregte Zustände antworten anders als der Grundzustand.
* **Analogie IR-Spektroskopie:** Vibrationsspektroskopie misst einzelne Übergänge ($v=0\to1$) auf einer 1D-Achse. Displacement-Operatoren messen die *Form* im 2D-Phasenraum, inklusive Wigner-Negativität, viele Moden simultan.

### 5.5 Phasenraum als komplexe Ebene

Die $q$-Achse spielt den Realteil, die $p$-Achse den Imaginärteil ($z = q + ip$). Komplexe Konjugation des Operators ist eine Spiegelung an der $q$-Achse: $X$ ist eine reelle Permutationsmatrix ($X^* = X$), $Z$ trägt die Einheitswurzeln ($Z^* = Z^{-1}$), also

$$D_{q,p}^* \propto X^q (Z^{-1})^p = X^q Z^{-p} \propto D_{q,-p}$$

Physikalisch ist das **Zeitumkehr**: Ort bleibt, Impuls dreht um (das $i$ steckt in $\hat p = -i\hbar\,\partial_q$). Der Zustand $\rho^*$ ist der „Zeitumkehr-Zwilling". Weil $D_{q,p}\otimes D_{q,p}^*$ kommutieren, umgeht die Paarung die Heisenberg-Unschärfe zwischen $q$ und $p$.

---

## 6. Exkurs: Drei Arten von Konjugation

| Typ | Abbildung | Idee | Rolle im Projekt |
| --- | --- | --- | --- |
| **A: Gruppen-Konjugation** | $x \mapsto gxg^{-1}$ | Basiswechsel, innerer Automorphismus. Spur, Determinante, Spektrum invariant | Clifford-Gruppe $UPU^\dagger = P'$; Rotoren $RvR^\dagger$ |
| **B: Komplexe Konjugation / Adjunktion** | $z\mapsto\bar z$, $A\mapsto A^\dagger$ | Spiegelung, Involution, Zeitumkehr, kontravarianter Funktor | **Das Conjugate-Pairs-Paper:** $\rho^*$ als physikalische Ressource |
| **C: Kanonische Konjugation** | $[\hat Q,\hat P] = i\hbar$, $ZX = \omega XZ$ | Dualität, Fourier-Paarung, Pontryagin-Dualität, Stone–von Neumann | Ort/Impuls, Clock/Shift der Qudits |

Alle drei treffen sich in der Quanten-Fourier-Transformation $W$:

$$W X W^\dagger = Z^\dagger$$

Typ C (links $X$, rechts $Z$ als kanonisches Paar), Typ A (die Konjugation $W(\cdot)W^\dagger$ dreht den Phasenraum um $90^\circ$), Typ B (das Dagger spiegelt die Eigenwerte entlang der komplexen Achse).

**Warum „Clifford-Gruppe"?** Historischer Zufall plus strukturelle Analogie (Gottesman, 1990er). In der Mathematik ist die Clifford-/Lipschitz-Gruppe der Normalisator der Erzeuger-Vektoren innerhalb der Clifford-Algebra; die Quanten-Clifford-Gruppe ist der Normalisator der Pauli-Gruppe. Gleiche Definitionsfigur, gleicher Name. Bei einem Qubit passt es sogar geometrisch ($SU(2)\cong\mathrm{Spin}(3)$). Bei mehreren Qubits ist die richtige Strukturgruppe $Sp(2n,\mathbb{Z}_d)$, symplektisch. Keine Clifford-Algebra im Spiel.

---
