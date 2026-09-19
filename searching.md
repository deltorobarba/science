# Searching

Zusammenfassungen der wichtigen Paper zum Aufgabentyp **Searching**: die Observablen sind der Output. Gegeben sind Kopien eines Zustands, Anwendungen eines Unitaries oder einer Dynamik, dazu ein Versprechen über die Struktur. Zurück kommt der Träger, also welche Adressen das Gewicht tragen, und danach ihre Werte.

Jede Zusammenfassung folgt demselben Aufbau: Einordnung in die Tabellen, Problem, Kernresultate, Methode, Bedeutung, Bezug zum eigenen Projekt, Grenzen und offene Fragen, Fragen zum Tieferbohren. Die Statusglyphen lesen sich wie in theory.md in der Reihenfolge Kopien · Zeit · Speicher.

## Übersicht

| Paper | Objekt | Was gesucht wird | Zugriff | Kosten | Status | Versprechen |
| --- | --- | --- | --- | --- | --- | --- |
| Montanaro 2017 | Zustand | die Stabilizergruppe, also der Träger des Pauli-Spektrums | Sample, Bell-Messung auf zwei Kopien | $O(n)$ Kopien, $O(n^3)$ Zeit | 🟢 🟢 🟢 | Stabilizerzustand |
| Grewal, Iyer, Kretschmer, Liang 2023 | Zustand | eine approximative Stabilizergruppe der Dimension $n-t$, dann der Rest per Tomographie | Sample, zwei Kopien oder Einzelkopien | $\mathrm{poly}(n, 2^t, 1/\epsilon)$ | 🟢 🟢 🟢 bis $t = O(\log n)$ | Stabilizerdimension $\geq n-t$ |
| Hangleiter, Gullans 2024 | Zustand aus einem Schaltkreis | Stabilizer-Nullity, Tiefe, Fidelity, und die Clifford+T-Beschreibung | Sample, Bell-Messung auf zwei Kopien | $O(n/\epsilon)$ Bell-Samples plus $O(2^t/\epsilon^2)$ für den Rest | 🟢 🟢 🟢 bis $t = O(\log n)$ | niedrige T-Zahl |
| Montanaro, Osborne 2010 | Unitary mit $f^2 = I$ | alle Pauli-Koeffizienten über einer Schwelle $\gamma$ | Query, $f$ und $f^\dagger$ | $\mathrm{poly}(n, 1/\gamma)$ | 🟢 🟢 🟢 | keines, die Normierung $\sum_s \hat f_s^2 = 1$ genügt |
| Chen, Nadimpalli, Yuen 2023 | Unitary | die $k$ relevanten Qubits, dann das $k$-Qubit-Unitary | Sample auf dem Choi-Zustand, Test mit Queries an $U, U^\dagger$ | $O(k/\epsilon + 4^k/\epsilon^2)$, unabhängig von $n$ | 🟢 🟢 🟢 | $k$-Junta |
| Bakshi, Liu, Moitra, Tang 2024 | Hamiltonian | welche der $n^{O(K)}$ lokalen Terme vorkommen, und ihre Koeffizienten | Query an die Dynamik $e^{-iHt}$ | $t_{\mathrm{total}} = O(\log(n)/\epsilon)$, $\tilde O(n^2)$ klassisch | 🟢 🟢 🟢 | $K$-Lokalität mit beschränkter lokaler Norm |

Zwei Familien. Die ersten drei Paper suchen den Träger eines *Zustands* per Bell-Sampling und leben von der Untergruppenstruktur. Die letzten drei suchen die schweren Pauli-Koeffizienten eines *Operators*; dort ist die Suche leicht, weil das Spektrum eines Unitaries auf eins normiert ist. Der Absatz zur Normierung in theory.md erklärt, warum dieselbe Messung beim Zustand gegen die LWE-Wand läuft.

---

## Learning stabilizer states by Bell sampling (arXiv:1707.04012)

Die Arbeit von **Ashley Montanaro** (Bristol, 2017) ist eine dreiseitige Notiz mit einem einzigen Satz: Ein unbekannter Stabilizerzustand auf $n$ Qubits lässt sich mit $O(n)$ Kopien identifizieren, und die dafür nötige Messung ist die denkbar einfachste, eine transversale Bell-Messung auf je zwei Kopien. Das Paper ist die Wurzel der gesamten Bell-Sampling-Literatur, auf der die beiden folgenden Zusammenfassungen und die Konjugatpaar-Methode dieses Projekts aufbauen.

### Einordnung in die Tabellen

* **Task type:** Searching. Zurück kommt der Träger des Pauli-Spektrums, also die Menge $T \subset \mathbb{F}_2^{2n}$ der Paulis mit $|\langle\psi|\sigma_t|\psi\rangle| = 1$. Erst danach werden die Vorzeichen bestimmt. Das ist genau die Zweiteilung Lokalisierung, dann Schätzung.
* **Objekt:** reiner Zustand. **Zugriff:** Sample, Kopien von $|\psi\rangle$, Bell-Messung auf zwei Kopien, Quantenspeicher zwei.
* **Status:** 🟢 🟢 🟢. Kopien $O(n)$, Zeit $O(n^3)$, Speicher $O(n^2)$ für das Tableau.
* **Versprechen:** Stabilizerzustand. Der Träger ist ein $n$-dimensionaler Unterraum, und das macht aus der Suche lineare Algebra. Das ist Regime 2 in theory.md.
* **Warum nicht Identifying:** Man kann das Ergebnis auch als Identifikation innerhalb der Stabilizerklasse lesen. Die Tabellen führen es unter Searching, weil der Output buchstäblich der Träger ist und weil die Methode, Samples aus einer Nebenklasse, XOR, Gauß-Elimination, die Vorlage für jede spätere Trägersuche mit Untergruppenversprechen ist, bis hin zu Simons Algorithmus auf der Query-Seite.

### Das Problem

Holevo erzwingt exponentiell viele Kopien für die Tomographie eines beliebigen Zustands. Der Ausweg ist eine Klasse: Aaronson und Gottesman hatten gezeigt, dass Stabilizerzustände mit $O(n)$ Kopien identifizierbar sind, allerdings mit einer kollektiven Messung über alle Kopien gleichzeitig, oder mit $O(n^2)$ Kopien bei Einzelkopienmessungen. Die Frage: Geht es mit $O(n)$ Kopien *und* mit Messungen, die nie mehr als zwei Kopien verschränken?

### Kernresultate

* **Theorem 1.** Es gibt einen Quantenalgorithmus, der einen unbekannten Stabilizerzustand aus $O(n)$ Kopien identifiziert, dabei nur Messungen über höchstens zwei Kopien gleichzeitig verwendet, in Zeit $O(n^3)$ läuft und mit exponentiell kleiner Wahrscheinlichkeit scheitert.
* **Lemma 2.** Bell-Sampling auf $|\psi\rangle^{\otimes 2}$ liefert das Ergebnis $r \in \{0,1\}^{2n}$ mit Wahrscheinlichkeit $|\langle\psi|\sigma_r|\psi^*\rangle|^2 / 2^n$. Der konjugierte Zustand steht in der Formel, obwohl nur zwei identische Kopien gemessen werden. Grund ist die Vec-Identität $|\psi\rangle|\psi\rangle = \mathrm{vec}(|\psi\rangle\langle\psi^*|)$.
* **Optimalität.** Es gibt $2^{\Theta(n^2)}$ Stabilizerzustände, also braucht jeder Algorithmus $\Omega(n)$ Kopien. Die Zeit $O(n^3)$ ist die Gauß-Elimination; $O(n^\omega)$ ist möglich, und $\Omega(n^2)$ braucht schon das Aufschreiben der Antwort.
* **Fehlerwahrscheinlichkeit** höchstens $2^{-n}$, per Union Bound über alle Unterräume der Dimension $n-1$.

### Methodischer Ansatz

1. **Konjugation ist bei Stabilizerzuständen eine Pauli-Operation.** Aus der Normalform $|\psi\rangle \propto \sum_{x \in A} i^{\ell(x)} (-1)^{q(x)} |x\rangle$ mit affinem $A$, linearem $\ell$ und quadratischem $q$ folgt $|\psi^*\rangle = \sigma_{10}^{\otimes S}|\psi\rangle$ für eine feste Teilmenge $S$. Damit wird die Bell-Verteilung zu $|\langle\psi|\sigma_r\sigma_{10}^{\otimes S}|\psi\rangle|^2/2^n$: gleichverteilt auf einer Nebenklasse $\{t \oplus s : t \in T\}$ der Stabilizergruppe $T$.
2. **Der unbekannte Versatz fällt beim XOR heraus.** Die Differenz zweier Samples ist gleichverteilt in $T$. Der Algorithmus zieht ein Referenz-Sample $r_0$ und dann $2n$ weitere Samples $r$, sammelt $r \oplus r_0$, und bestimmt eine Basis per Gauß-Elimination.
3. **Vorzeichen per Einzelkopie.** Für jedes Basiselement wird eine Kopie in der Eigenbasis des zugehörigen Pauli gemessen; das entscheidet zwischen $M|\psi\rangle = |\psi\rangle$ und $M|\psi\rangle = -|\psi\rangle$.

Die Bell-Messung selbst ist eine Schaltung der Tiefe eins: CNOT zwischen den korrespondierenden Qubits, Hadamard, Messung. Der Algorithmus verallgemeinert Röttelers Verfahren zum Lernen quadratischer Polynome über $\mathbb{F}_2$ und ähnelt dem unabhängigen Graph-State-Algorithmus von Zhao, Pérez-Delgado und Fitzsimons.

### Bedeutung und Anwendungen

* **Die Messprimitive für alles Folgende.** Bell difference sampling bei Gross, Nezami und Walter, das Lernen mit wenigen T-Gattern bei Grewal et al., die Circuit Shadows von Hangleiter und Gullans und das agnostische Lernen per Stabilizer Bootstrapping benutzen genau diesen Mechanismus.
* **Lokalität der Messung.** Der Fortschritt gegenüber Aaronson und Gottesman ist nicht die Kopienzahl, sondern dass nie mehr als zwei Kopien verschränkt werden. Das ist die Zwei-Kopien-Beschränkung, unter der auch dieses Projekt arbeitet.
* **Das Plateau ist kein Härteproblem.** Alle $2^n$ Koeffizienten auf $T$ haben Betrag eins. Der Träger ist per linearer Algebra rekonstruierbar, nur eine *geordnete* Rangliste ist ill-definiert. Das ist die Aussage von `cor:plateau` im Paper dieses Projekts.

### Bezug zum eigenen Projekt

* Der Algorithmus ist der beweisbar richtige Decoder für Stufe 2 der Instanzenleiter in objective.md und einer der drei Vergleichsdecoder für jedes Experiment: triviale Baseline, beweisbarer Spezialist, gelerntes CNN.
* Bell-Sampling auf zwei *identischen* Kopien funktioniert hier, weil $\psi^*$ ein Pauli-Bild von $\psi$ ist. Für generische Zustände und für Qudits mit $d > 2$ gilt das nicht; dort braucht man das Konjugatpaar $\rho \otimes \rho^*$ (Allcock et al. 2024, King, Wan, McClean 2024). Das ist die Begründung für die Messung von Phase 1.
* Die Statistik hier ist die Ausnahme, nicht die Regel: Weil das Spektrum auf $2^n$ Adressen mit Betrag eins verteilt ist, sieht jedes Sample ein gleichverteiltes Element der Nebenklasse. Bei einem sparsamen Spektrum mit $k$ Koeffizienten der Größe $\Theta(1)$ hat jede Adresse Wahrscheinlichkeit $\Theta(1/d)$, und dieselbe Messung liefert nichts direkt Lesbares. Das ist der Grund, warum Phase 1 die Fouriertransformation und den CNN-Decoder braucht.

### Grenzen und offene Fragen

* Nur qubits, nur exakte Stabilizerzustände. Robustheit gegen Rauschen und Nähe zur Klasse liefert erst Grewal et al.; Toleranz erst Arunachalam und Dutt sowie Chen, Gong, Ye und Zhang.
* Qudits mit $d > 2$: Allcock, Doriguello, Ivanyos und Santha zeigen, dass die Bell-Verteilung auf $\rho \otimes \rho$ uniform sein kann und dann keine Information trägt.
* Die Frage nach $O(n)$ Kopien mit *Einzelkopien*-Messungen bleibt offen; Aaronson und Gottesman haben $O(n^2)$.

### Fragen zum Tieferbohren

* Wie sieht die Nebenklassenstruktur der Bell-Verteilung im zyklischen Qudit-Fall aus, wenn $\mathbb{Z}_d$ kein Körper ist? (Rang 2 statt $n$, Hermite-Normalform statt Gauß, siehe conjecture.md.)
* Welche Rolle spielt die Wahl $\rho \otimes \rho$ gegen $\rho \otimes \rho^*$ für die Vorzeichen-Information, die Lemma 2 sichtbar macht?
* Was ist der genaue Zusammenhang zwischen dem Union Bound über Unterräume hier und der Sample-Schranke $N = O(g^{-2}\log(M/\delta))$ des Dictionary-Regimes?

Paper: [arXiv:1707.04012](https://arxiv.org/abs/1707.04012)

---

## Efficient Learning of Quantum States Prepared With Few Non-Clifford Gates (arXiv:2305.13409)

Die Arbeit von **Sabee Grewal, Vishnu Iyer, William Kretschmer und Daniel Liang** (UT Austin, 2023; erschienen in *Quantum* 2025) verallgemeinert Montanaro und Aaronson–Gottesman von Stabilizerzuständen auf Zustände mit *Stabilizerdimension* mindestens $n-t$, insbesondere auf alle Zustände aus Clifford-Schaltkreisen mit höchstens $t$ Nicht-Clifford-Gattern. Kosten $\mathrm{poly}(n, 2^t, 1/\epsilon)$ in Kopien und Zeit, polynomiell also bis $t = O(\log n)$. Zwei Algorithmen: einer mit Bell-Messungen auf zwei Kopien, einer nur mit Einzelkopien.

### Einordnung in die Tabellen

* **Task type:** Searching für den Kern, Identifying für den Rest. Der Algorithmus sucht zuerst einen großen isotropen Unterraum $\hat G$, der den Zustand approximativ stabilisiert; das ist die Trägersuche, die das Paper selbst "Tomography reduces to finding heavy subspaces" nennt. Danach wird der verbleibende $t$-Qubit-Zustand per Tomographie identifiziert. In theory.md steht die Zeile "Clifford plus few non-Clifford gates" in der Identifying-Tabelle, weil der Output ein Zustand aus einer Klasse ist; die Datei liegt hier im Searching-Ordner, weil der Mechanismus die Trägersuche ist. Beide Lesarten sind vertretbar; die Tabellen sollten Montanaro und dieses Paper konsistent behandeln.
* **Objekt:** reiner Zustand, im Anhang B auch gemischt. **Zugriff:** Sample; Variante 1 mit Bell-Messungen auf zwei Kopien, Variante 2 mit Einzelkopien und zufälligen Cliffords.
* **Status:** 🟢 🟢 🟢 für $t = O(\log n)$. Zeit und Kopien wachsen wie $2^t$; darüber 🔴 in der Zeit, und das ist unter einer kryptographischen Annahme unvermeidbar.
* **Versprechen:** Stabilizerdimension $\geq n-t$, also eine abelsche Gruppe von $2^{n-t}$ Paulis, die den Zustand stabilisiert. Magic ist der Härteregler.

### Das Problem

Optimale Tomographie kostet $\Theta(d^2)$ Kopien mit verschränkten und $\Theta(d^3)$ mit Einzelkopienmessungen, für reine Zustände $\Theta(d)$. Klassische Simulatoren für nahezu-Clifford-Schaltkreise skalieren polynomiell in $n$ und exponentiell in der Zahl der Nicht-Clifford-Gatter. Gibt es *Lernalgorithmen* mit derselben Skalierung? Lai und Cheng hatten einen stark eingeschränkten Fall (eine einzige T-Schicht, Vollrangbedingung). Gesucht war ein Verfahren für beliebige Nicht-Clifford-Gatter an beliebiger Stelle.

### Kernresultate

* **Theorem 1.1.** Für einen Zustand aus Cliffords und höchstens $t$ Ein-Qubit-Nicht-Clifford-Gattern lernt der Algorithmus $|\psi\rangle$ bis auf Spurdistanz $\epsilon$ mit $\mathrm{poly}(n, 2^t, 1/\epsilon)$ Zeit und Kopien. Allgemeiner für jeden Zustand mit Stabilizerdimension $\geq n-t$.
* **Zwei-Kopien-Variante (Korollar 7.2).** $O(n/\epsilon + \log(1/\delta)/\epsilon^2)$ Bell-Samples zum Finden der Gruppe, dazu die Tomographie eines $t$-Qubit-Zustands mit $2^{O(t)}$ Kopien. Zeit $\mathrm{poly}(n) + 2^{O(t)}$, also additiv statt multiplikativ, ein Vorteil gegenüber Leone, Oliviero und Hamma.
* **Einzelkopien-Variante (Korollar 9.7).** $O(n(n + \log 1/\delta)^2 \, 2^t/\epsilon^2)$ Samples plus Tomographie; Zeit $O(n^3 (n+\log 1/\delta)^2\, 2^t/\epsilon^2)$ plus Tomographie. Der Preis für fehlenden Quantenspeicher ist polynomiell in $n$ und ein Faktor $2^t$ in den Samples.
* **Property Test (Theorem 5.1).** Ob ein Zustand Stabilizerdimension $\geq k$ hat oder Fidelity $\leq 1-\epsilon$ mit allen solchen Zuständen: $(16n + 8\log(1/\delta))/\epsilon$ Kopien und $O((n^3 + n^2\log 1/\delta)/\epsilon)$ Zeit, für *jedes* $k$ effizient. Verallgemeinert das Resultat, dass Haar-zufällige Zustände von Zuständen mit Stabilizerdimension unterscheidbar sind.
* **Härte.** Existieren in Linearzeit konstruierbare pseudozufällige Zustände mit exponentieller Sicherheit, dann sind $t$-Qubit-Zustände aus Schaltkreisen der Größe $O(t)$ nicht in $2^{o(t)}$ Zeit lernbar. Die exponentielle Abhängigkeit von $t$ ist also wahrscheinlich optimal.
* **Gemischte Zustände.** Fast alle Resultate übertragen sich ohne Verlust (Anhang B).

### Methodischer Ansatz

1. **Kompression der Nicht-Cliffordness.** Aus Generatoren der Stabilizergruppe $G$ baut Lemma 3.2 einen Clifford $C$ mit $C|\psi\rangle = |\varphi\rangle|x\rangle$: ein Basiszustand auf $n-t$ Qubits, ein allgemeiner Zustand auf $t$ Qubits. Dann genügt Messen für $|x\rangle$ und Tomographie für $|\varphi\rangle$.
2. **Robustheit.** Exakte Stabilizer verschwinden unter kleinsten Störungen. Der Schlüsselbeitrag: Es genügt eine Gruppe $\hat G$ der Größe $2^{n-t}$ mit $\mathbb{E}_{P \sim \hat G} |\langle\psi|P|\psi\rangle|^2 \geq 1-\epsilon$. Algorithmus 2 findet dann einen Clifford, der $|\psi\rangle$ approximativ in die Produktform bringt.
3. **$\hat G$ per Bell difference sampling.** Die gezogenen Paulis kommutieren stets mit $G$; man nimmt den Kommutanten der Samples. Der technische Kern zeigt, dass nach $\mathrm{poly}(n, 1/\epsilon)$ Samples der Zustand $\epsilon$-nahe an einem Zustand ist, der von $\hat G$ stabilisiert wird, selbst wenn $\hat G$ größer ist als $G$.
4. **$\hat G$ per Einzelkopien.** Zufällige Cliffords und *computational difference sampling*: zweimal $C|\psi\rangle$ in der Rechenbasis messen, XOR der Strings. Das löscht den affinen Versatz und liefert Elemente eines Unterraums; mit Wahrscheinlichkeit etwa $2^{-t}$ verrät ein Clifford einen Generator. Das setzt den unveröffentlichten Algorithmus von Aaronson und Gottesman auf ein rigoroses Fundament.
5. **Alles über $\mathbb{F}_2^{2n}$.** Paulis modulo Phase als symplektischer Vektorraum; Kommutant, isotrope Unterräume und Gruppenoperationen sind lineare Algebra.

### Bedeutung und Anwendungen

* Die Klasse ist ausdrucksstärker als Stabilizerzustände: Sie enthält $k$-Designs für jedes konstante $k$ und Eigenzustände von Stabilizer-Hamiltonians mit wenigen nicht kommutierenden Termen.
* Der Zusammenhang zwischen Simulierbarkeit und Lernbarkeit wird quantitativ: Beide skalieren mit $2^t$. Magic ist der gemeinsame Regler.
* Die Hardware-Anforderungen entsprechen denen der Classical Shadows: Bell-Paare messen, Cliffords anwenden, Rechenbasis messen, Tomographie auf $t$ Qubits.
* Gleichzeitig entstanden Leone, Oliviero, Hamma und Hangleiter, Gullans mit ähnlichen Bell-Sampling-Verfahren; dieses Paper ist das allgemeinste und hat die additive Laufzeit.

### Bezug zum eigenen Projekt

* Das ist der Decoder für die Stufen zwischen "perfekter Kristall" und "generisch" in der Instanzenleiter: Stabilizer-Grundzustände plus wenige nicht kommutierende Terme. Die Stabilizerdimension ist eine messbare Zustandseigenschaft, die als Einflussfaktor in die Taxonomie von objective.md gehört.
* Der Property Test für Stabilizerdimension ist ein Werkzeug, um pro Instanzklasse zu prüfen, *ob* eine Untergruppenstruktur vorliegt, bevor man den Spezialdecoder ansetzt.
* Die Fußnote zu Lai und Cheng ist eine Warnung für alle, die Bell difference sampling benutzen: Es zieht aus $q_\psi = p_\psi * p_\psi$, der Faltung der charakteristischen Verteilung mit sich selbst, nicht aus $p_\psi$.
* Der Härtebeleg zeigt die Struktur der Grenze: sample-effizient bleibt alles, die Zeit explodiert mit $2^t$. Das ist dieselbe Signatur wie in eurer Zelle, nur mit Magic statt LWE als Ursache.

### Grenzen und offene Fragen

* **Kein proper learning (Frage 10.1).** Der ausgegebene Schaltkreis hat nicht notwendig wenige Nicht-Clifford-Gatter.
* **Ist $2^t$ mit Einzelkopien nötig (Frage 10.2)?** Die Zwei-Kopien-Variante braucht $O(n)$ Bell-Samples unabhängig von $t$ für die Gruppe, die Einzelkopien-Variante $\mathrm{poly}(n)\, 2^t$. Die Autoren erwarten eine Trennung wie bei Chen, Cotler, Huang und Li.
* **Approximative Stabilizerdimension.** Zustände mit hoher Erwartung für eine große Pauli-Untergruppe, ohne exakte Stabilisierung, sind nicht abgedeckt.
* Die Tomographie des $t$-Qubit-Rests ist die einzige exponentielle Komponente; schnellere reine Tomographie verbessert alle Schranken direkt.

### Fragen zum Tieferbohren

* Wie genau garantiert Lemma 4.x, dass ein Unterraum mit großer $p_\psi$-Masse isotrop ist, und was ist das Qudit-Analogon?
* Wie überträgt sich die Konstruktion $C|\psi\rangle = |\varphi\rangle|x\rangle$ auf $\mathbb{Z}_d$ mit zusammengesetztem $d$?
* Kann das CNN dieses Projekts die Stabilizerdimension implizit aus dem gefalteten Bell-Record ablesen, und ist das der Mechanismus, der auf Stufe 2 der Leiter greift?

Paper: [arXiv:2305.13409](https://arxiv.org/abs/2305.13409)

---

## Bell sampling from quantum circuits (arXiv:2306.00083)

Die Arbeit von **Dominik Hangleiter und Michael J. Gullans** (QuICS, NIST/Maryland; *Phys. Rev. Lett.* 2024) betrachtet Bell-Sampling nicht als Lernprimitive, sondern als *Rechenmodell*: Zwei Kopien eines Zustands $C|0^n\rangle$ werden transversal in der Bell-Basis gemessen. Die Samples sind klassisch schwer zu erzeugen und zugleich ein *Circuit Shadow*, aus dem sich Eigenschaften des präparierenden Schaltkreises effizient ablesen lassen: Fidelity, Tiefe, Magic, und bei niedriger T-Zahl der ganze Zustand.

### Einordnung in die Tabellen

* **Task type:** gemischt, mit einem Searching-Kern. Die Schätzung der Stabilizer-Nullity sucht per Bell difference sampling den größten isotropen Unterraum $\mathcal{C}$, also den Träger des Stabilizer-Anteils. Der Tiefentest und der Magic-Test sind Identifying-Aufgaben mit einem Bit als Antwort; Fidelity und Purity sind Estimating. Das Clifford+T-Lernen ist dasselbe Verfahren wie bei Grewal et al.
* **Objekt:** Zustand aus einem bekannten Schaltkreismodell. **Zugriff:** Sample, Bell-Messung auf zwei Kopien.
* **Status:** 🟢 🟢 🟢 für die Diagnostik; für das Lernen 🟢 🟢 🟢 bis $t = O(\log n)$, danach $2^t$ in Zeit und Kopien. Die Autoren zeigen, dass $2^t$ optimal ist, weil ein Zustand mit Nullity $t$ genau $2^t + n - t$ reelle Parameter hat.
* **Versprechen:** je nach Aufgabe niedrige T-Zahl, feste Architektur (Tiefentest), oder lokales Pauli-Rauschen (Fidelity-Schätzer).
* **Einordnung in theory.md:** Das Paper gehört primär in den Primitiven-Abschnitt, mit Querverweisen aus allen drei Tabellen.

### Das Problem

Zufallsschaltkreis-Sampling dient als Benchmark und Vorteilsdemonstration, aber der Cross-Entropy-Benchmark braucht eine klassische Simulation des idealen Schaltkreises und funktioniert deshalb nur im simulierbaren Regime. Computational-Basis-Samples verraten außerdem wenig über den Zustand. Gesucht: ein Rechenmodell, dessen Ausgaben zugleich klassisch schwer und diagnostisch reich sind.

### Kernresultate

* **Bell-Verteilung.** $P_C(r) = |\langle\bar C|\sigma_r|C\rangle|^2/2^n$ mit dem konjugierten Zustand $|\bar C\rangle$. Die Messung ist eine Tiefe-1-Schaltung aus transversalen CNOTs, Hadamards und Rechenbasis-Messung.
* **Universalität und Härte.** Vorzeichen und Betrag von $\langle C|Z|C\rangle$ sind aus Bell-Samples eines modifizierten Schaltkreises schätzbar (Ramsey-Interferometrie mit einer Ancilla pro Kopie). Approximatives Sampling aus $P_C$ ist für zufällige universelle Schaltkreise mit $\Omega(n^2)$ Gattern in Brickwork-Architektur im Mittel klassisch intraktabel, unter denselben Vermutungen wie beim Standard-Zufallsschaltkreis-Sampling.
* **Purity und Fidelity.** Der Swap-Test ist eine Funktion der Samples: Der Überlapp $\mathrm{tr}[\rho\sigma]$ folgt aus der Y-Parität mit $O(1/\epsilon^2)$ Samples. Unter lokalem Pauli-Rauschen gilt $\mathbb{E}_C F = \sqrt{\mathbb{E}_C P}$: Die Wurzel der Purity schätzt die Fidelity, und zwar unabhängig von Tiefe und Rauschstärke, wo XEB versagt. Mit $E$ Fehlerorten vor der Messung erweitert sich das zu $F = (\mathbb{E}_C P)^{E/(2(E+2/3))}$.
* **Tiefentest.** Subsystem-Purities liefern Rényi-2-Entropien $S_A$; wegen $S_A(d) \leq d\,|\partial A|$ gibt der Halbschnitt eine untere Schranke an die Tiefe, verfeinerbar über tiefenabhängige Page-Kurven.
* **Magic.** Die Stabilizer-Nullity $M(|\psi\rangle) = n - \dim(\mathcal{C})$, ein Magic-Monoton, wird mit $O(n/\epsilon)$ Bell-Samples geschätzt; laut den Autoren die effizienteste bekannte Magic-Messung.
* **Clifford+T-Lernen.** $O(n/\epsilon)$ Bell-Samples für den Clifford-Anteil plus $O(2^t/\epsilon^2)$ Messungen für die Tomographie von $|x\rangle|\varphi\rangle$; Laufzeit polynomiell, verallgemeinert auf beliebige Nicht-Clifford-Gatter.
* **Fehlererkennung.** Ein Ergebnis im antisymmetrischen Unterraum ($\pi_Y(r) = 1$) ist sicher ein Fehler; Verwerfen halbiert die Fehlerrate bei weißem Rauschen etwa. Die Bell-Messung ist transversal für Stabilizercodes und extrahiert deren Syndrome; Messfehler breiten sich nicht aus.
* **Quadratische Fehlerunterdrückung** für diagonale Zwei-Kopien-Observablen über $\mathrm{tr}[A\rho^{\otimes 2}]/\mathrm{tr}[S\rho^{\otimes 2}]$, verwandt mit virtueller Destillation.

### Methodischer Ansatz

Alles folgt aus einer Beobachtung: Die Bell-Basis ist die gemeinsame Eigenbasis aller $\sigma_r \otimes \bar\sigma_r$, also sind alle *diagonalen Zwei-Kopien-Observablen* $A = \sum_r a_r |\sigma_r\rangle\langle\sigma_r|$ Funktionen der Samples. Der Swap-Operator ist eine solche Observable (Projektor auf den symmetrischen minus antisymmetrischen Unterraum), ebenso jeder Pauli $P \otimes P$, und ebenso Subsystem-Swaps. Für den Stabilizer-Anteil gilt Montanaros Nebenklassen-Argument, und Bell difference sampling liefert wie bei Grewal et al. einen Clifford $U_{\mathcal{C}}$, der $|\psi\rangle$ in $|x\rangle|\varphi\rangle$ komprimiert.

### Bedeutung und Anwendungen

* **Benchmarking ohne Simulation.** Der Wurzel-Purity-Schätzer ersetzt XEB in den Regimen hoher Rauschrate und niedriger Tiefe, ohne klassische Simulation.
* **Brücke zur Fehlerkorrektur.** Transversale Bell-Messungen zwischen Codeblöcken; erste Experimente auf einem Logik-Qubit-Prozessor (Ref. 53 des Papers) entstanden in Zusammenarbeit der Autoren.
* **Ein Rechenmodell mit eingebauter Verifikation.** Wenn die Härte des Bell-Samplings gegen Rauschen robust bleibt, was die Autoren mit ersten Hinweisen im Supplement stützen, wäre das eine skalierbare Vorteilsdemonstration mit klassischer Validierung.

### Bezug zum eigenen Projekt

* Die Formel $P_C(r) = |\langle\bar C|\sigma_r|C\rangle|^2/2^n$ ist dieselbe wie bei Montanaro und zeigt den Konjugat-Effekt, den dieses Projekt über $\rho \otimes \rho^*$ physikalisch nutzt. Für reelle Amplituden fällt der Unterschied weg, was erklärt, warum die Demos mit GHZ- und Clifford-Zuständen arbeiten.
* Der Purity-Schätzer aus der Y-Parität ist ein Zertifikat, das direkt aus dem Bell-Record von Phase 1 folgt, ohne zusätzliche Messungen. Er könnte den Noise Floor und den Mixedness-Faktor A in der Taxonomie von objective.md kalibrieren.
* Die Nullity-Schätzung ist eine messbare Version des Faktors "Stabilizer-Rank / Magic" aus derselben Taxonomie.
* Hardware-Realismus: Die Diskussion zu Ionenfallen, Rydberg-Arrays und den SWAP-Kosten geometrisch lokaler Architekturen ist die konkreteste Beschreibung der Kosten einer transversalen Bell-Messung, die in den Papern dieser Sammlung vorkommt.

### Grenzen und offene Fragen

* Die Hardness-Aussage gilt für rauschfreies Sampling; ob sie asymptotisch gegen konstantes Rauschen robust ist, anders als beim Computational-Basis-Sampling nach Gao–Duan und Aharonov et al., ist offen.
* Tiefen- und Magic-Test sind für rauschfreie Samples formuliert; rauschrobuste Versionen fehlen.
* Die Fidelity-Beziehung setzt lokales Pauli-Rauschen voraus, herstellbar per unabhängigem Randomized Compiling auf beiden Kopien; korrelierte kohärente Fehler brechen sie.
* Das Lernresultat ist für T-Gatter formuliert, die Verallgemeinerung auf beliebige Nicht-Clifford-Gatter wird nur behauptet.

### Fragen zum Tieferbohren

* Welche diagonalen Zwei-Kopien-Observablen entsprechen im Qudit-Fall den Displacement-Quadraturen $S_{q,p}$, und sind sie aus dem Konjugatpaar-Record ablesbar?
* Wie verhält sich der Nullity-Schätzer unter der Faltung $q_\psi = p_\psi * p_\psi$ bei gemischten Zuständen?
* Lässt sich die Fehlererkennung über den antisymmetrischen Unterraum auf $\rho \otimes \rho^*$ übertragen, wo der Swap-Test eine andere Bedeutung hat?

Paper: [arXiv:2306.00083](https://arxiv.org/abs/2306.00083)

---

## Quantum boolean functions (arXiv:0810.2435)

Die Arbeit von **Ashley Montanaro und Tobias J. Osborne** (2008; *Chicago Journal of Theoretical Computer Science* 2010) überträgt die Analyse Boolescher Funktionen auf Operatoren. Eine *quantum boolean function* ist ein Unitary $f$ mit $f^2 = I$; ihre Fourier-Entwicklung ist die Pauli-Zerlegung. Das Paper liefert Property Tests, eine Quantenversion des Goldreich–Levin-Algorithmus zum Auffinden großer Pauli-Koeffizienten, eine Anwendung auf lokale Dynamik, und Hyperkontraktivität sowie FKN- und KKL-Analoga.

### Einordnung in die Tabellen

* **Task type:** Searching. Der Goldreich–Levin-Algorithmus (Theorem 26) gibt alle Adressen $s \in \{0,1,2,3\}^n$ mit $|\hat f_s| \geq \gamma$ aus, ohne dass eine Kandidatenliste gegeben wäre. Die Property Tests (Stabilizer-Test, Lokalitätstest) sind Identifying mit einem Bit.
* **Objekt:** Unitary, speziell Hermitesches Unitary. **Zugriff:** Query. Theorem 26 setzt Orakelzugriff auf $f$ und $f^\dagger$ voraus; die Koeffizientenschätzung (Lemma 24) braucht kontrolliertes $f$ in einem Hadamard-Test. Die einfacheren Resultate (Prop. 21, 22) kommen mit Anwendungen von $f$ auf halbe Bell-Paare und einer Bell-Messung aus, also mit Sample-Zugriff auf den Choi-Zustand.
* **Status:** 🟢 🟢 🟢. Zeit $\mathrm{poly}(n, 1/\gamma, \log 1/\delta)$; die Liste hat nach Parseval höchstens $1/\gamma^2$ Einträge.
* **Versprechen:** keines über die Struktur. Die Normierung $\sum_s \hat f_s^2 = 1$ tut die Arbeit: Ein schwerer Koeffizient trägt einen konstanten Anteil des Gesamtgewichts.
* **In theory.md** ist das die Zeile "Heavy Pauli coefficients of a unitary" mit dem Zusatz "operator Goldreich–Levin". Genauer: Der GL-Algorithmus ist Query-Zugriff; die Choi-Sampling-Variante steckt in Proposition 21 und 22.

### Das Problem

Boolesche Funktionen haben eine reife Theorie: Fourier-Analyse, Property Testing, Lernalgorithmen (Goldreich–Levin, Kushilevitz–Mansour), Hyperkontraktivität, KKL. Gibt es eine Quantenverallgemeinerung, in der ein Unitary die Rolle der Funktion spielt, die klassischen Sätze Spezialfälle werden und quantenmechanische Beweise neue Einsichten liefern? Die Motivation reicht bis zu Schaltkreis-Untergrenzen und einem Quanten-PCP.

### Kernresultate

* **Definition und Fourier-Analyse.** $f = \sum_s \hat f_s \chi_s$ mit $\chi_s$ den $n$-Qubit-Paulis und $\hat f_s = 2^{-n}\mathrm{tr}(\chi_s f)$. Für den Phasenorakel-Fall $f|x\rangle = f(x)|x\rangle$ sind das genau die klassischen Fourier-Koeffizienten (Prop. 9). Parseval: $\sum_s |\hat f_s|^2 = 1$ für quantum boolean $f$ (Prop. 10).
* **Stabilizer-Test (Def. 13, Prop. 14).** $f$ auf zwei Sätze von Bell-Paaren anwenden, Gleichheits-Observable messen; Akzeptanzwahrscheinlichkeit $\sum_s |\hat f_s|^4$. Wer mit Wahrscheinlichkeit $1-\epsilon$ besteht, ist $\epsilon$-nahe an $e^{i\varphi}\chi_s$. Klassisch angewendet hat der Test bessere Parameter als das Original.
* **Stabilizer-Operatoren mit einer Query (Prop. 21).** $f$ auf halbe Bell-Paare anwenden, in der Bell-Basis messen: Bei $f = \chi_s$ ist das Ergebnis $s$ deterministisch. Das ist Bernstein–Vazirani für Operatoren.
* **Dominanter Koeffizient (Prop. 22).** Gilt $\hat f_s \geq (1+\epsilon)/\sqrt 2$, dann identifiziert Mehrheitsentscheid über $O(\epsilon^{-2}\log 1/\delta)$ Anwendungen das $s$.
* **Einzelne Koeffizienten (Lemma 24).** $\hat f_s$ auf $\pm\eta$ mit $O(\eta^{-2}\log 1/\delta)$ Queries per Hadamard-Test mit kontrolliertem $f$ und kontrolliertem $\chi_s$; Amplitudenverstärkung gibt eine Wurzel.
* **Quantum Goldreich–Levin (Theorem 26).** Mit Orakelzugriff auf $f$, $f^\dagger$ und $\gamma, \delta > 0$ liefert ein $\mathrm{poly}(n, 1/\gamma, \log 1/\delta)$-Algorithmus eine Liste $L$ mit: jedes $s$ mit $|\hat f_s| \geq \gamma$ liegt in $L$, und jedes $s \in L$ hat $|\hat f_s| \geq \gamma/2$.
* **Lernen lokaler Dynamik (Prop. 41).** Für eindimensionale lokale Hamiltonians und $t = O(\log n)$ lassen sich die Heisenberg-Bilder $e^{-itH}\sigma_j^s e^{itH}$ mit $\mathrm{poly}(n, 1/\epsilon, \log 1/\delta)$ Queries an $e^{itH}$ lernen, ohne zu wissen, welches Qubit mit welchem wechselwirkt.
* **Weiteres:** Quanten-Hyperkontraktivität für $1 \leq p \leq 2 \leq q$, zwei Quanten-FKN-Sätze, Einfluss von Qubits, KKL in Spezialfällen.

### Methodischer Ansatz

* **Branch and Bound über die Pauli-Adressen.** Die Menge aller $4^n$ Strings wird in vier Teile zerlegt; für jeden Teil, beschrieben durch einen Indikatorstring $S$ mit Präfix und Wildcards, wird das Gewicht $W(S) = \sum_{t \in S}|\hat f_t|^2$ geschätzt (Prop. 32), Teile mit kleinem Gewicht werden verworfen, die anderen weiter geteilt. Lemma 23 begrenzt die Zahl der überlebenden Teile durch $1/\gamma^2$, daher höchstens $16n/\gamma^2$ Schätzungen mit je $O(\gamma^{-2}\log 1/\delta)$ Samples.
* **Gewichte als Choi-Statistik.** $W(S)$ ist die Norm eines partiell reduzierten Operators $F_{s;I}$ (Lemma 28, 29), also aus Bell-Paar-Experimenten zugänglich.
* **Lieb–Robinson als Sparsity-Versprechen.** Für $t = O(\log n)$ liegen die relevanten Koeffizienten von $\sigma_j^s(t)$ in einem Lichtkegel der Größe $O(|t|)$, also gibt es nur $\mathrm{poly}(n)$ Kandidaten; GL findet sie, Lemma 24 schätzt sie.

### Bedeutung und Anwendungen

* Begründet die Sprache, in der später Juntas (Chen, Nadimpalli, Yuen), Low-Degree-Objekte (Arunachalam, Dutt, Escudero Gutiérrez) und das Strukturlernen von Bakshi, Liu, Moitra und Tang formuliert sind: Einfluss von Qubits, Pauli-Spektrum, GL-Queries.
* Prop. 41 ist der Vorläufer des Hamiltonian Learning aus Dynamik: Lokalität plus Lieb–Robinson machen das Spektrum sparsam, und ein Fourier-Suchalgorithmus findet es.
* Der Stabilizer-Test ist der operatorseitige Vorläufer des Stabilizer-Tests von Gross, Nezami und Walter.

### Bezug zum eigenen Projekt

* Das Paper ist die sauberste Quelle für den Satz, der die Searching-Tabelle organisiert: Beim Operator gilt $\sum_s \hat f_s^2 = 1$, ein Koeffizient der Größe $\gamma$ erscheint beim Choi-Sampling mit Wahrscheinlichkeit $\gamma^2$, und die Suche ist polynomiell. Beim reinen Zustand summieren die quadrierten Displacement-Koeffizienten zu $d$, und dieselbe Messung trägt pro Adresse nur $1/d$. Das ist der ganze Unterschied zwischen dieser Zeile und eurer LWE-Zelle.
* Der Branch-and-Bound über Präfixe ist strukturell dasselbe wie Kushilevitz–Mansour und die Bucket-Verfeinerung der Sparse FFT. Euer Coprime-Folding ist das Duale davon: Statt Gewichte auf Präfixen zu *erfragen*, faltet ihr das Spektrum und lasst das CNN die Reste dekodieren. Der Vergleich beider Strategien wäre ein eigener Absatz im Paper wert.
* Lemma 24 ist die Query-Version eurer Phase 2: Ein Hadamard-Test mit kontrolliertem Operator schätzt einen einzelnen Koeffizienten inklusive Vorzeichen. Eure Eigenprobe leistet dasselbe mit Sample-Zugriff und einem Konjugatpaar.

### Grenzen und offene Fragen

* Die Lokalitäts- und Diktatortests (Vermutungen 17, 20) sind nicht analysiert.
* Hyperkontraktivität nur für $1 \leq p \leq 2 \leq q$; die volle Aussage ist Vermutung.
* Ein KKL-Satz für allgemeine quantum boolean functions und eine Nisan–Szegedy-Gradschranke $\Omega(\log n)$ bleiben offen; kombinatorische Beweise übertragen sich nicht, Fourier-analytische schon.
* GL ist als Query-Algorithmus formuliert; eine reine Sample-Version über Choi-Sampling mit Schwellenwertargument wird nicht explizit ausgeführt, folgt aber aus Prop. 22 und Parseval.

### Fragen zum Tieferbohren

* Wie genau schätzt Proposition 32 das Gewicht eines Indikatorstrings, und wie viele Bell-Paare braucht eine Schätzung?
* Gilt das Normierungsargument auch für nicht-Hermitesche Unitaries, wo $\hat f_s$ komplex ist, und was ändert sich beim Displacement-Operator $D_{q,p}$ mit $D^2 \neq I$ für $d > 2$?
* Wie sieht das Lieb–Robinson-Sparsity-Argument in der Heisenberg–Weyl-Basis eines einzelnen Qudits aus, wo es keine räumliche Lokalität gibt?

Paper: [arXiv:0810.2435](https://arxiv.org/abs/0810.2435)

---

## Testing and Learning Quantum Juntas Nearly Optimally (arXiv:2207.05898)

Die Arbeit von **Thomas Chen, Shivam Nadimpalli und Henry Yuen** (Columbia; SODA 2023) behandelt $n$-Qubit-Unitaries, die nur auf $k$ unbekannten Qubits nichttrivial wirken. Sie gibt einen Tester mit $\tilde O(\sqrt k)$ Queries und einen Lernalgorithmus mit $O(4^k/\epsilon^2)$ Queries, beide ohne Abhängigkeit von $n$, und nahezu passende Untergrenzen $\Omega(\sqrt k)$ und $\Omega(4^k/k)$.

### Einordnung in die Tabellen

* **Task type:** Searching für das Lernen. Der Algorithmus findet zuerst die $k$ relevanten Qubits, das ist die Trägersuche auf der Ebene der Qubits, und identifiziert danach das $k$-Qubit-Unitary per Tomographie. Der Tester ist Identifying mit einem Bit.
* **Objekt:** Unitary. **Zugriff:** Für das Lernen genügt es, $|v(U)\rangle = (U \otimes I)|\Phi\rangle$ zu präparieren und in der Pauli-Basis zu messen, also nicht-adaptives Sampling auf dem Choi-Zustand. Nach der Regel in theory.md ist das Sample-Zugriff, obwohl das Paper von Orakelzugriff spricht. Der Tester braucht $U$ und $U^\dagger$ in einem Einfluss-Schätzer und ist Query-Zugriff.
* **Status:** 🟢 🟢 🟢. Kopien $O(k/\epsilon + 4^k/\epsilon^2)$, Zeit $\mathrm{poly}(n, 4^k)$, Speicher $O(k\log n)$ plus das $k$-Qubit-Unitary.
* **Versprechen:** $k$-Junta. Konstantes $k$ macht die Menge der Kandidatenträger polynomiell, wie bei jedem Dictionary-Regime.

### Das Problem

Prozesstomographie eines beliebigen $n$-Qubit-Unitaries braucht $\Omega(4^n)$ Queries. Property Testing fragt stattdessen, ob $U$ eine Eigenschaft hat oder weit von allen Unitaries mit dieser Eigenschaft ist. Für Boolesche Funktionen ist das Junta-Testen ein Klassiker mit $\tilde O(k)$ klassisch (Blais), $\tilde O(\sqrt k)$ quantenmechanisch (Ambainis et al.) und $\Omega(\sqrt k)$ als Untergrenze (Bun, Kothari, Thaler). Für Unitaries gab es Wangs $O(k)$-Tester und keine Lernresultate jenseits voller Prozesstomographie.

### Kernresultate

* **Testen (Theorem 2, 20, 24).** Quantum $k$-Juntas sind mit $\tilde O(\sqrt k)$ Queries an $U$ und $U^\dagger$ testbar; $\Omega(\sqrt k)$ Queries sind nötig. Unabhängig von $n$.
* **Lernen (Theorem 3, 28).** Mit $O(k/\epsilon + 4^k/\epsilon^2)$ Queries findet der Algorithmus mit Wahrscheinlichkeit $9/10$ ein $\hat U$ mit $\mathrm{dist}(U, \hat U) \leq \epsilon$.
* **Untergrenze (Theorem 31).** Jeder Lernalgorithmus braucht $\Omega(4^k\log(1/\epsilon)/k)$ Queries, über eine Reduktion auf Nayaks Input-Guessing-Spiel. Nebenbei liefert das den ersten formalen Beweis, dass Prozesstomographie $\Omega(4^n)$ Queries kostet.
* **Strukturresultat (Prop. 25).** Ist eine Boolesche Funktion weit von jeder Booleschen $k$-Junta, dann ist $U_f = \mathrm{diag}((-1)^{f(x)})$ weit von jeder Quantum-$k$-Junta. Das überträgt die klassische Untergrenze.

### Methodischer Ansatz

* **Einfluss von Qubits** nach Montanaro und Osborne, mit einer neuen Charakterisierung und einem Schätzer (Influence-Estimator), der den Tester von Ambainis et al. als Black Box fahren lässt.
* **Pauli-Sampling.** $|v(U)\rangle$ präparieren und alle Qubits in der Pauli-Basis $\{|v(\sigma_x)\rangle\}$ messen; das Ergebnis $x$ erscheint mit Wahrscheinlichkeit $|\hat U(x)|^2$. Die Vereinigung der Träger über $O(\log k/\gamma)$ Runden liefert die Menge $S$ der Qubits mit hohem Einfluss. Das ist Fourier-Sampling für Operatoren, das Gegenstück zur Subroutine von Atıcı und Servedio für Boolesche Juntas.
* **Zustandspräparation durch Postselektion.** Die Bell-Register der irrelevanten Qubits werden gemessen; ist das Ergebnis die Identität, bleibt ein $2k$-Qubit-Zustand $|\psi_S\rangle$, der das $k$-Qubit-Unitary kodiert.
* **Reine Tomographie** auf $|\psi_S\rangle$ mit $O(d/\epsilon)$ Kopien für $d = 4^k$ (Derka, Bužek, Ekert; Bruß, Macchiavello), daher der Term $4^k/\epsilon^2$ insgesamt.

### Bedeutung und Anwendungen

* Erstes Lernresultat für eine natürliche Unitary-Klasse mit Kosten unabhängig von der Systemgröße; der Tester ist der erste $\tilde O(\sqrt k)$-Tester für Quantum-Juntas.
* Die Tabelle 1 des Papers stellt klassisches Testen, Quanten-Testen und Quanten-Lernen für Boolesche und Quantum-Juntas nebeneinander und ist eine kompakte Landkarte für den Übergang Funktion → Operator.
* Ausgangspunkt für spätere Arbeiten zu Low-Degree-Objekten und zu Junta-Kanälen.

### Bezug zum eigenen Projekt

* Die Trägersuche geschieht hier auf der gröbsten Ebene, den Qubits, und ist deshalb billig: $\log k$ Runden Pauli-Sampling. Eure Suche geschieht auf der feinsten Ebene, den $d^2$ Adressen, und ist deshalb hart. Zwischen beiden liegt die Idee, Adressen hierarchisch zu bündeln, genau das, was euer Coprime-Folding tut.
* Die Untergrenze über Input Guessing ist eine Vorlage für eine Sample-Untergrenze eurer Top-$k$-Aufgabe: eine $\epsilon$-Packung der Kandidatenzustände, deren Größe die Kopienzahl erzwingt.
* Das Paper zeigt eine echte Query-Sample-Asymmetrie innerhalb eines Themas: Der Tester braucht $U^\dagger$, das Lernen nicht. In eurer Tabelle sind das zwei verschiedene Zeilen.

### Grenzen und offene Fragen

* Die $\tilde O(\sqrt k)$-Schranke gilt für Testen, nicht für Lernen; die Lücke $4^k/k$ gegen $4^k/\epsilon^2$ bleibt.
* Junta-Kanäle statt Unitaries sind unbearbeitet (Abschnitt 1.3).
* Tolerantes Testen ist quantenmechanisch nicht untersucht; klassisch kostet es $2^{\tilde O(\sqrt k)}$.
* Ob Quantenalgorithmen im verteilungsfreien Modell einen Vorteil bringen, ist offen.

### Fragen zum Tieferbohren

* Wie viele Choi-Präparationen braucht die Postselektion in Quantum-State-Preparation im Mittel, und ist der Faktor $4^k$ oder $2^k$?
* Wie definiert man Einfluss und Junta für Displacement-Operatoren auf einem Qudit, dessen Adressen keine Tensorstruktur haben?
* Lässt sich das Input-Guessing-Argument auf $\rho \otimes \rho^*$-Zugriff übertragen, um eine Kopien-Untergrenze für Top-$k$-Lokalisierung zu bekommen?

Paper: [arXiv:2207.05898](https://arxiv.org/abs/2207.05898)

---

## Structure learning of Hamiltonians from real-time evolution (arXiv:2405.00082)

Die Arbeit von **Ainesh Bakshi, Allen Liu, Ankur Moitra (MIT) und Ewin Tang (Berkeley)** (FOCS 2024) löst das Strukturlernen lokaler Hamiltonians aus Echtzeit-Evolution: Gegeben die Fähigkeit, $e^{-iHt}$ anzuwenden, ohne zu wissen, welche Wechselwirkungsterme vorkommen, wird $H$ mit gesamter Evolutionszeit $O(\log(n)/\epsilon)$ rekonstruiert, also Heisenberg-limitiert, mit konstanter Zeitauflösung und ohne die Annahme kurzer Reichweite.

### Einordnung in die Tabellen

* **Task type:** Searching. Gegeben ist nur die $K$-Lokalität mit beschränkter lokaler Norm; zurück kommen die vorhandenen Terme und ihre Koeffizienten. Das Paper grenzt sich ausdrücklich von den Koeffizienten-Verfahren mit bekannten Termen ab (Huang, Tong, Fang, Su; Haah, Kothari, Tang), die in der Estimating-Tabelle stehen.
* **Objekt:** Hamiltonian. **Zugriff:** Query an die Dynamik. Die Schaltkreise sind "prepare, apply, measure" mit alternierenden Evolutionen $e^{-iHt}e^{iH_0 t}$ und $\log(1/\epsilon)$ Runden Adaptivität; Steuerung dieser Art ist für Heisenberg-Skalierung nachweislich nötig (Dutkiewicz, O'Brien, Schuster).
* **Status:** 🟢 🟢 🟢. Evolutionszeit $O(r\log(n)/\epsilon)$, Experimente $\tilde O(r^2\log n\log 1/\epsilon)$, klassische Zeit $\tilde O(n^2 r^3\log 1/\epsilon)$, Speicher polynomiell.
* **Versprechen:** $K = O(1)$, lokale Norm $\|H\|_{B_1} = \max_i\sum_{a: i\in\mathrm{supp}(E_a)}|\lambda_a| \leq g$, und effektive Sparsity $r = \max_i\sum_a\min(1, \lambda_a^2/\epsilon^2)$. Bei Hamiltonians mit beschränktem Wechselwirkungsgrad ist $r = O(1)$.

### Das Problem

Ableitungsschätzung lernt Hamiltonians ohne Strukturwissen, aber mit $t_{\mathrm{total}} = O(\log(n)/\epsilon^3)$ und Zeitauflösung $\epsilon$. Die Heisenberg-limitierten Verfahren brauchen die Terme: Huang et al. reshapen den Hamiltonian per Entkopplungspulsen aus dem bekannten Wechselwirkungsgraphen, Haah et al. rechnen Kommutatorentwicklungen bezüglich der bekannten Terme. Ein einziger unspezifizierter Fernterm bricht beide. Drei Fragen: Strukturlernen ohne Termwissen (Q1), ohne strikt beschränkte Reichweite (Q2), mit Heisenberg-Skalierung *und* konstanter Zeitauflösung (Q3).

### Kernresultate

* **Theorem 1.1.** Für $K$-lokales $H$ mit $K = O(1)$ und $\|H\|_{B_1} = O(1)$ gibt der Algorithmus Schätzungen $\hat\lambda_P$ für alle $P \in \mathcal{P}_K$ aus mit: Genauigkeit $|\hat\lambda_{E_a} - \lambda_a| < \epsilon$ und $\hat\lambda_P = 0$ sonst, mit Wahrscheinlichkeit $0.99$; $t_{\mathrm{total}} = O(r\log(n)/\epsilon)$; $t_{\min} = \Theta(1/r)$; $\tilde O(r^2\log n\log 1/\epsilon)$ Experimente; $\tilde O(n^2 r^3\log 1/\epsilon)$ klassische Zeit.
* **Optimalität in $\epsilon$.** $1/\epsilon$ Evolutionszeit, $\Omega(1)$ Auflösung, $O(1/\epsilon)$ Verschachtelungen und $\log(1/\epsilon)$ Experimente sind bis auf $\log\log$ optimal.
* **Weitere Eigenschaften.** $n$ Qubits ohne Ancillas; robust gegen SPAM-Fehler bis $\Theta(1/r)$ pro Experiment; implementierbar im kontinuierlichen und im diskreten Zugriffsmodell.
* **Korollar 1.5, Potenzgesetz.** Für $\alpha$-Potenzgesetz-Zerfall auf einem $d$-dimensionalen Gitter mit $\alpha > d$ gilt $t_{\mathrm{total}} = O(\epsilon^{-(1+\kappa)}\log(n/\delta))$ mit $\kappa = dK/(dK + \alpha - d)$: immer besser als $1/\epsilon^2$, gegen Heisenberg für große $\alpha$, gültig bis $\alpha = d$.
* **FPT-Laufzeit.** Die klassische Zeit $\tilde O(n^2)$ hängt nicht mit $K$ im Exponenten ab. Klassisches Strukturlernen von Markov-Zufallsfeldern braucht $n^K$ unter Standardannahmen (sparse parities with noise). Das ist eine Trennung zwischen Lernen aus Dynamik und Lernen aus dem Gibbs-Zustand.

### Methodischer Ansatz

1. **Bootstrapping zur Heisenberg-Skalierung** (nach Dutkiewicz, O'Brien, Schuster): Rekursion auf dem Residuum. Aus einer $\eta$-guten Schätzung $\lambda^{(j)}$ wird eine $\eta/2$-gute mit Evolutionszeit $1/\eta$, indem $H - H(\lambda^{(j)})$ zu konstantem Fehler gelernt wird. $\log_2(1/\epsilon)$ Runden. Die Beobachtung der Autoren: Diese Reduktion braucht kein Lokalitätswissen.
2. **Termauslöschung statt dynamischer Entkopplung.** $e^{-i(H - H_0)t}$ wird per Trotterisierung aus $e^{-iHt}$ und $e^{iH_0 t}$ gebaut, mit einer neuen Schranke für Trotter-Fehler, die Alternieren in *konstanten* Zeitintervallen erlaubt (Lemma 3.1). Das liefert Q3.
3. **Koeffizientenschätzung durch Ableitung.** Für kleines $t$ gilt $e^{i\hat Ht}P_a e^{-i\hat Ht} = P_a + [i\hat Ht, P_a] + O(t^2)$; ein Ein-Qubit-Pauli $P_a$ mit $[E_a, P_a] \neq 0$ und der Anfangszustand $(I + Q_a)/N$ geben einen erwartungstreuen Schätzer für $2\hat\lambda_a t$. Parallelisierbar für alle Koeffizienten mit $O(\log n)$ Anwendungen.
4. **Goldreich–Levin-artige Queries auf dem Pauli-Spektrum (Lemma 1.10, 4.12).** Für eine unbekannte Observable $O = \sum_Q c_Q Q$ mit anwendbarer POVM $\{(I \pm O)/2\}$ liefert eine Datenstruktur aus $O(\log n)$ Queries und $O(n\log n)$ Vorverarbeitung für jedes $X \in \mathcal{P}_K$ eine Schätzung von $\sum_{Q \supseteq X}|c_Q|^2/6^{|\mathrm{supp}(Q)|}$ in $O(\log n)$ Zeit. Damit werden die Terme *hierarchisch* gesucht: erst alle Paulis mit Träger 1, dann für jeden überlebenden alle Erweiterungen auf Träger 2, Löschen bei kleinem Gewicht. Die Observable ist $O = Z^\dagger P Z \approx P + [-i\hat Ht, P]$, sie hat Grad $K$ und $O(1)$ Koeffizienten.
5. **Parallelisierung mit gekoppeltem Zufall**, damit alle GL-Queries aus einem Datensatz von $O(\log n)$ Experimenten beantwortet werden, statt einem Experiment pro Query.

### Bedeutung und Anwendungen

* Erstes Verfahren, das Strukturlernen, Heisenberg-Skalierung, konstante Zeitauflösung und Langreichweite gleichzeitig erreicht; die Vergleichstabelle (Fig. 2 des Papers) ordnet Ableitungsschätzung, Caro, Odake et al., Haah et al. und Huang et al. ein.
* Charakterisierung von Quantengeräten ohne vorausgesetzte Lokalitätsstruktur; Benchmarking und Fehlerdiagnose.
* Ein neues Werkzeug, die observablenzentrierte Sicht auf Classical Shadows im dualen Zugriffsmodell (Huang, Chen, Preskill), das effizienter ist als das zustandszentrierte $n^K$.

### Bezug zum eigenen Projekt

* Das ist die genaueste Beschreibung dessen, was "Suche mit Lokalitätsversprechen" bedeutet: Die Terme sind ein Dictionary der Größe $n^{O(K)}$, aber der Algorithmus zählt es nicht auf, sondern verfeinert Gewichte über Präfixe. Genau das ist die Kushilevitz–Mansour-Strategie, die euer Feedback als Regime 3 unter Query-Zugriff beschreibt.
* Die Trennung "Dynamik leicht, Gibbs schwer" im klassischen Fall ($\tilde O(n^2)$ gegen $n^K$ unter sparse-parity-Härte) ist ein Beispiel für eure These, dass der Zugriff, nicht das Objekt, die Rechen-Grenze verschiebt.
* Die Zeitauflösung $t_{\min}$ ist eine Achse, die in eurer Taxonomie fehlt und für Hardware-Realismus (Faktor F) wichtig wäre.
* Die GL-Datenstruktur mit gekoppeltem Zufall ist ein Vorbild für die Frage, ob ein einziger Bell-Record alle Kandidaten-Queries beantworten kann; euer Charakter-Mittelwert über ein Dictionary tut genau das, aber ohne die hierarchische Verfeinerung.

### Grenzen und offene Fragen

* **Untergrenzen.** Bekannt ist nur $1/\epsilon$ für einen Parameter und $\epsilon^{-1}\log(1/\delta)$ mit SPAM-Robustheit. Wie die Kosten mit Lokalität, Systemgröße und effektiver Sparsity $r$ skalieren müssen, ist offen.
* **Ein Koeffizient.** Gleichzeitig $t_{\mathrm{total}} = O(1/\epsilon)$ und $t_{\min} = \Omega(1)$ ohne Abhängigkeit von $n$ ist nicht erreicht: Entkopplung schafft die Zeit, Termauslöschung die Auflösung.
* **Beliebig große Zeitauflösung** bleibt Frage 3 des Papers.
* Die Gatterkomplexität wird nicht verfolgt; dominant ist die Evolution mit dem bekannten $H_0$.

### Fragen zum Tieferbohren

* Wie genau funktioniert die Trotter-Schranke bei konstanten Intervallen (Lemma 3.1), und warum reicht die lokale Norm statt geometrischer Lokalität?
* Wie sieht die Datenstruktur mit gekoppeltem Zufall aus, und lässt sich dieselbe Idee auf Bell-Records eines Zustands übertragen?
* Was ist das Analogon des Faktors $6^{|\mathrm{supp}(Q)|}$ für Displacement-Operatoren auf einem Qudit?

Paper: [arXiv:2405.00082](https://arxiv.org/abs/2405.00082)
