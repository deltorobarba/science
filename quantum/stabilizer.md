# Die algebraische Promise von Stabilisatorzuständen

Die Stabilisator-Promise (Promise) ist der Prototyp von Regime 2 in der Spalte *Suchen*: Der Träger des Pauli-Spektrums ist ein Unterraum, und die Lokalisierung wird zu linearer Algebra. Dieser Anhang leitet die Promise Schritt für Schritt her, von der Gruppendefinition bis zum Decoder, und endet mit einem durchgerechneten Zwei-Qubit-Beispiel und den Stellen, an denen die Promise bricht. Quellen: Montanaro (arXiv:1707.04012: Theorem 1, Lemma 2, Algorithmus 1), die Normalform von Dehaene und De Moor in der dort zitierten Form, Gross, Nezami, Walter (arXiv:1712.08628) sowie Grewal, Iyer, Kretschmer, Liang (arXiv:2305.13409, arXiv:2304.13915). Mit *eigene Rechnung*, *eigene Prüfung* oder *eigene Erläuterung* markierte Schritte stehen nicht in den Arbeiten. Kurzfassungen desselben Materials: [M1](https://deltorobarba.github.io/science/#m1-bell-sampling-one-shot-the-whole-pauli-spectrum), [M2](https://deltorobarba.github.io/science/#m2-bell-difference-sampling-and-gaussian-elimination), [Kontrastpaar 1](https://deltorobarba.github.io/science/#1-one-copy-or-two-learning-stabilizer-states). Am Ende folgt als Kontext eine gekürzte Zusammenfassung zweier SciencePedia-Artikel.

## 1. Die Promise

**Pauli-Operatoren.** Auf einem Qubit

$$I=\begin{pmatrix}1&0\\0&1\end{pmatrix},\quad X=\begin{pmatrix}0&1\\1&0\end{pmatrix},\quad Y=\begin{pmatrix}0&-i\\i&0\end{pmatrix},\quad Z=\begin{pmatrix}1&0\\0&-1\end{pmatrix}.$$

Ein $n$-Qubit-Pauli-Operator ist ein Tensorprodukt aus $n$ davon. Eine Buchstabenfolge bezeichnet ein Tensorprodukt ($XZ$ für $X\otimes Z$ auf zwei Qubits); auf einem einzelnen Qubit ist $ZX$ das Matrixprodukt. Einzelqubit-Paulis antikommutieren ($XZ=-ZX$ als Matrizen), Tensorprodukte können aber kommutieren: $X\otimes X$ und $Z\otimes Z$ kommutieren, weil das Vorzeichen auf jedem Qubit einmal kippt und $(-1)^2=+1$.

**Definition.** $|\psi\rangle$ ist ein Stabilisatorzustand, wenn es eine Untergruppe $G$ der $n$-Qubit-Pauli-Gruppe gibt mit

* $G$ abelsch und $-I\notin G$;
* $|G|=2^n$, d. h. $n$ unabhängige Erzeuger $g_1,\dots,g_n$;
* $g|\psi\rangle=|\psi\rangle$ für alle $g\in G$.

Der Zustand ist durch die Operatoren definiert, die ihn festhalten, nicht durch seinen Amplitudenvektor.

**Beispiele auf zwei Qubits.**

| Zustand | Erzeuger von $G$ |
| --- | --- |
| $\vert 00\rangle$ | $ZI$, $IZ$ |
| $\vert{+}{+}\rangle$ | $XI$, $IX$ |
| $(\vert 00\rangle+\vert 11\rangle)/\sqrt2$ | $XX$, $ZZ$ |
| $(\vert 01\rangle+\vert 10\rangle)/\sqrt2$ | $XX$, $-ZZ$ |
| $(\vert 00\rangle+i\vert 11\rangle)/\sqrt2$ | $ZZ$, $XY$ (das durchgerechnete Beispiel in Abschnitt 7) |

**Was der Lerner nicht weiß.** Die Promise besagt, dass eine solche Gruppe existiert, nicht welche. Für einen unbekannten Zwei-Qubit-Stabilisatorzustand könnten die Erzeuger $XX, ZZ$ oder $XI, IZ$ oder $YY, ZZ$ sein, jeweils mit beiden Vorzeichen. Die Gruppe zu finden heißt, den Ort des Trägers des Pauli-Spektrums zu suchen; deshalb stehen die Stabilisator-Zeilen nach der LWE-Regel unter *Suchen*.

**Rechnung 1: Die Promise legt genau einen Zustand fest.** Jedes $(I+g_i)/2$ ist ein Projektor ($g_i^2=I$), und die Projektoren kommutieren. Beim Ausmultiplizieren tritt wegen der Unabhängigkeit jedes Gruppenelement genau einmal auf:

$$\Pi=\prod_{i=1}^n\frac{I+g_i}{2}=\frac{1}{2^n}\sum_{g\in G}g .$$

Jeder Pauli-Operator außer $\pm I$ ist spurfrei, und $-I$ ist ausgeschlossen, also $\mathrm{Tr}\,\Pi=2^{-n}\,\mathrm{Tr}\,I=1$. Der gemeinsame $+1$-Eigenraum ist eindimensional, und $\Pi=|\psi\rangle\langle\psi|$. Dieselbe Zählung mit den ersten $k$ Erzeugern liefert die Spur $2^{n-k}$: Jeder unabhängige Erzeuger halbiert den Raum, und $n$ davon lassen einen einzigen Zustand übrig. Zwei Varianten zeigen, dass die Bedingungen nötig sind:

* Mit $-I\in G$ wird kein von null verschiedener Vektor stabilisiert, da $-I|\psi\rangle=|\psi\rangle$ zu $|\psi\rangle=0$ zwingt.
* Mit $n-t$ Erzeugern ist die Spur $2^t$: ein Coderaum der Dimension $2^t$ statt eines Zustands. Das ist die Promise „Clifford plus wenige Nicht-Clifford-Gatter“ (Stabilisatordimension mindestens $n-t$): Die Gruppe legt den Zustand bis auf einen $t$-Qubit-Rest fest, der $2^{O(t)}$ Tomographie kostet.

## 2. Der algebraische Kern: Übersetzung in einen symplektischen Vektorraum

Jeder Pauli-Operator ist bis auf die Phase durch ein Label $a=(z|x)\in\mathbb{F}_2^{2n}$ festgelegt, ein $Z$-Bit und ein $X$-Bit pro Qubit: $00\mapsto I$, $01\mapsto X$, $10\mapsto Z$, $11\mapsto Y$ (erstes Bit $Z$, zweites Bit $X$, wie bei Montanaro). $W_a$ bezeichnet den hermiteschen Pauli-Operator mit Label $a$.

**Rechnung 2: Produkt und Kommutator.** Aus $XZ=-ZX$ folgt $X^xZ^{z'}=(-1)^{xz'}Z^{z'}X^x$, also

$$(Z^zX^x)(Z^{z'}X^{x'})=(-1)^{xz'}Z^{z+z'}X^{x+x'},\qquad (Z^{z'}X^{x'})(Z^zX^x)=(-1)^{x'z}Z^{z+z'}X^{x+x'} .$$

Über alle Qubits genommen:

* Ein Produkt von Paulis ist die Summe ihrer Labels, $W_aW_b\propto W_{a+b}$, mit einer Phase aus $\{\pm1,\pm i\}$;
* der Kommutator ist die symplektische Form, $W_aW_b=(-1)^{[a,b]}W_bW_a$ mit $[a,b]=z\cdot x'+x\cdot z' \bmod 2$.

Jede Bedingung an die Gruppe wird zu einer Bedingung an die Labelmenge $T=\{a:\pm W_a\in G\}$:

| Bedingung an $G$ | Bedingung an $T\subset\mathbb{F}_2^{2n}$ |
| --- | --- |
| Untergruppe | linearer Unterraum |
| abelsch | isotrop: $[a,b]=0$ für alle $a,b\in T$, d. h. $T\subseteq T^\perp$ |
| $\lvert G\rvert=2^n$ | $\dim T=n$ |

Die Form ist nicht ausgeartet, also $\dim T+\dim T^\perp=2n$. Zusammen mit $T\subseteq T^\perp$ folgt $T=T^\perp$: **$T$ ist ein Lagrange-Unterraum**, ein maximal isotroper. Physikalisch: Jeder Pauli-Operator, der mit ganz $G$ kommutiert, liegt bis aufs Vorzeichen bereits in $G$.

## 3. Wie viel die Promise festlegt

**Rechnung 3.** Die Anzahl der Lagrange-Unterräume von $`\mathbb{F}_2^{2n}`$ ist $`\prod_{k=1}^n(2^k+1)`$, und jeder trägt $`2^n`$ Vorzeichenwahlen für seine Erzeuger:

$$\#\{\text{Stabilisatorzustände auf } n \text{ Qubits}\}=2^n\prod_{k=1}^n(2^k+1).$$

Das ist die Standardzählung (Aaronson, Gottesman 2004). *Eigene Prüfung* per Brute Force über $\mathbb{F}_2^{2n}$: 3, 15 und 135 Lagrange-Unterräume für $n=1,2,3$, also 6, 60 und 1080 Zustände; für $n=1$ sind das die Eigenzustände von $\pm X$, $\pm Y$, $\pm Z$.

Logarithmiert legen etwa $n^2/2$ Bits den *Ort* $T$ fest und nur $n$ Bits die *Vorzeichen*. Eine Kopie von $n$ Qubits trägt höchstens $n$ Bits (Holevo), also braucht jede Strategie $\Omega(n)$ Kopien; das ist Montanaros Optimalitätsbemerkung.

## 4. Was die Promise mit dem Pauli-Spektrum macht

**Rechnung 4.** Aus $\rho=2^{-n}\sum_{g\in G}g$ und $\mathrm{Tr}(W_aW_b)=2^n\delta_{ab}$ bis auf die Phase folgt

$$\mathrm{Tr}(W_a\rho)=\begin{cases}\pm1 & a\in T,\\ 0 & a\notin T.\end{cases}$$

Probe mit Parseval: $\sum_a\mathrm{Tr}(W_a\rho)^2=2^n\,\mathrm{Tr}\rho^2=2^n$, genau $2^n$ Einträge vom Betrag eins. Die charakteristische Verteilung $p_\psi(a)=\mathrm{Tr}(W_a\psi)^2/2^n$ ist gleichverteilt auf $T$.

**Minimaler Träger** (*eigene Erläuterung*, ein Standardargument). Für jeden reinen Zustand summiert sich das quadrierte Pauli-Spektrum zu $`2^n`$, und jeder Eintrag hat höchstens Betrag eins; also hat jeder reine Zustand mindestens $`2^n`$ von null verschiedene Pauli-Erwartungswerte. Gleichheit gilt genau für Stabilisatorzustände. Bei genau $`2^n`$ von null verschiedenen Einträgen haben alle Betrag eins, also hält jedes $`\pm W_a`$ den Zustand $`|\psi\rangle`$ fest. Zwei Operatoren, die denselben Vektor mit Eigenwerten $`\pm1`$ festhalten, können nicht antikommutieren; also bilden diese Operatoren eine abelsche Gruppe der Größe $`2^n`$. Stabilisatorzustände sind der Extremfall: kleinstmöglicher Träger und ein flaches Plateau. Die Beträge tragen keine Information, ein Top-$`k`$-Ranking ist wegen der Gleichstände undefiniert (der Identifizierbarkeits-Fehlermodus in [den drei Fehlermodi](https://deltorobarba.github.io/science/#the-repaired-success-criterion-and-the-three-failure-modes)), und die gesamte Information steckt in Ort und Vorzeichen.

**Rechnung 5: Die Vorzeichen sind kein freies Muster.** Für $a,b\in T$ gilt $W_aW_b=c_{ab}W_{a+b}$ mit bekanntem $c_{ab}\in\{\pm1\}$; es ist reell, weil beide Seiten hermitesch sind, wenn $W_a$ und $W_b$ kommutieren. Angewandt auf $|\psi\rangle$:

$$\lambda_{a+b}=c_{ab}\,\lambda_a\lambda_b,\qquad \lambda_a=\langle\psi|W_a|\psi\rangle\in\{\pm1\}.$$

Die $2^n$ Vorzeichen auf $T$ folgen aus den $n$ Vorzeichen der Erzeuger, was zur Zählung in Rechnung 3 passt.

## 5. Warum Bell-Sampling den Träger sieht

**Rechnung 6 (Montanaro, Lemma 2).** Qubit $k$ der ersten Kopie wird mit Qubit $k$ der zweiten gepaart. Die Bell-Basis ist $|\Phi_r\rangle=(\sigma_r\otimes I)|\Phi\rangle$ mit $|\Phi\rangle=2^{-n/2}\sum_x|x\rangle|x\rangle$. Die vec-Identität lautet

$$|\psi\rangle|\psi\rangle=\sum_{x,y}\psi_x\psi_y|x\rangle|y\rangle=2^{n/2}(M\otimes I)|\Phi\rangle,\qquad M=|\psi\rangle\langle\psi^*|,$$

denn $\langle\psi^*|=\sum_y\psi_y\langle y|$. Mit $\langle\Phi|(B\otimes I)|\Phi\rangle=\mathrm{Tr}B/2^n$ folgt

$$\langle\Phi_r|\psi\psi\rangle=2^{-n/2}\langle\psi^*|\sigma_r^\dagger|\psi\rangle\quad\Rightarrow\quad p(r)=\frac{|\langle\psi|\sigma_r|\psi^*\rangle|^2}{2^n}.$$

Die Konjugierte erscheint, obwohl zwei identische Kopien gemessen werden.

**Rechnung 7: Für Stabilisatorzustände ist $\psi^*$ ein Pauli-Bild von $\psi$.** Jeder Stabilisatorzustand hat die Normalform

$$|\psi\rangle=\frac{1}{\sqrt{|A|}}\sum_{x\in A}i^{\ell(x)}(-1)^{q(x)}|x\rangle$$

mit $A\subseteq\mathbb{F}_2^n$ affin, $\ell$ linear und $q$ quadratisch. Konjugation lässt $(-1)^{q(x)}$ unverändert und macht aus $i^{\ell(x)}$ den Faktor $(-i)^{\ell(x)}=(-1)^{\ell(x)}\,i^{\ell(x)}$. Mit $\ell(x)=s\cdot x$ ist der Faktor $(-1)^{s\cdot x}$ genau die Wirkung von $Z^s$, also $|\psi^*\rangle=Z^s|\psi\rangle$. Eingesetzt in Lemma 2:

$$p(r)=\frac{|\langle\psi|W_{r+\tilde s}|\psi\rangle|^2}{2^n}=\begin{cases}2^{-n} & r\in T+\tilde s,\\ 0 & \text{sonst,}\end{cases}\qquad \tilde s=(s|0).$$

Bell-Samples sind **gleichverteilt auf einer Nebenklasse von $T$**: $2^n$ erlaubte Ergebnisse mit je Wahrscheinlichkeit $2^{-n}$.

*Bemerkung zur Normalform (eigene Prüfung).* Montanaro schreibt $i^{\ell(x)}$ als $\prod_{k\in S}i^{x_k}$. Wird $\ell$ modulo 2 genommen und ist $w=\sum_{k\in S}x_k$, gilt das nur bis auf den Faktor $(-1)^{w(w-1)/2}$, einen quadratischen Term, der sich in $q$ absorbieren lässt. Die Schlussfolgerung ist davon nicht betroffen, und das obige Argument braucht die Umschreibung nicht.

**Spezialfälle.**

* Reelle Amplituden, zum Beispiel Graphzustände $\propto\sum_x(-1)^{\sum_{(u,v)\in E}x_ux_v}|x\rangle$: $\ell=0$, $s=0$, und Bell-Samples liegen direkt in $T$.
* Konjugierte Paare $\psi\otimes\psi^*$: $p(r)=\mathrm{Tr}(W_r\psi)^2/2^n$, die charakteristische Verteilung selbst, gleichverteilt auf $T$ ohne Verschiebung (*eigene Folgerung* aus M1; auf Quditen ist das der Weg von Allcock et al., arXiv:2405.06357).

**Was gesampelt wird und was nicht verrauscht ist.** Bell-Sampling zieht aus der charakteristischen Verteilung, dem quadrierten Pauli-Spektrum; es sampelt keine Wigner-Funktion. Das Wigner-Bild gehört zu ungeradem $d$: Dort ist die Wigner-Funktion eines reinen Stabilisatorzustands gleichverteilt auf einem affinen Lagrange-Unterraum, und die reinen Zustände mit nichtnegativer Wigner-Funktion sind genau die Stabilisatorzustände (diskreter Hudson-Satz, Gross 2006; Gross, Nezami, Walter, arXiv:1712.08628, Gl. 2.18, mit einer robusten Version in Theorem 8.4). Nur für ungerades $d$ transformiert die Wigner-Funktion kovariant unter der Clifford-Gruppe; der Qubit-Algorithmus benutzt sie nie. Und für einen exakten Stabilisatorzustand tragen die Samples kein Rauschen: Jede Differenz zweier Bell-Samples liegt exakt in $T$. Diese Exaktheit lässt die Gauß-Elimination funktionieren. Die Beziehung zu LWE tritt erst auf, wenn sie gebrochen wird (Abschnitt 8).

## 6. Der Decoder

**Die Verschiebung hebt sich weg.** $r_1=t_1+\tilde s$ und $r_2=t_2+\tilde s$ ergeben $r_1+r_2=t_1+t_2$, gleichverteilt auf $T$ und frei vom unbekannten $\tilde s$.

**Rechnung 8: Anzahl der Samples.** $m$ Differenzen spannen $T$ genau dann nicht auf, wenn sie alle in einer Hyperebene von $T$ liegen, einem Unterraum der Dimension $n-1$. $T$ hat $2^n-1$ Hyperebenen, und ein gleichverteiltes Element von $T$ liegt mit Wahrscheinlichkeit $1/2$ in einer festen davon. Die Union Bound liefert

$$\Pr[\text{Fehlschlag}]\le(2^n-1)\,2^{-m}<2^{n-m}=2^{-n}\qquad\text{für } m=2n.$$

Montanaros Algorithmus 1 zieht ein Referenz-Sample $r_0$ und $2n$ weitere Samples, benutzt die Differenzen $r\oplus r_0$ (unabhängig und gleichverteilt auf $T$ gegeben $r_0$) und fügt $n$ Einzelkopien für die Vorzeichen hinzu: $2(2n+1)+n=5n+2$ Kopien.

**Gauß-Elimination** über $\mathbb{F}_2$ liefert eine Basis von $T$ in Zeit $O(n^3)$; $O(n^\omega)$ ist möglich, und schon das Hinschreiben der Antwort kostet $\Omega(n^2)$.

**Vorzeichen.** Für jeden Basisvektor $t_j$ wird eine frische Kopie in der Eigenbasis von $W_{t_j}$ gemessen. Da $|\psi\rangle$ Eigenzustand von $\pm W_{t_j}$ ist, ist das Ergebnis deterministisch. Die übrigen Vorzeichen folgen aus Rechnung 5.

## 7. Durchgerechnetes Beispiel auf zwei Qubits

Sei $|\psi\rangle=(|00\rangle+i|11\rangle)/\sqrt2$; die Phase $i$ macht die Verschiebung sichtbar. *Eigene Rechnung*, numerisch geprüft.

* **Stabilisatoren.** $XY|00\rangle=i|11\rangle$ und $XY|11\rangle=-i|00\rangle$, also $XY|\psi\rangle=(i|11\rangle+|00\rangle)/\sqrt2=|\psi\rangle$; außerdem $ZZ|\psi\rangle=|\psi\rangle$. Ihr Produkt ist $(ZX)\otimes(ZY)=(iY)\otimes(-iX)=Y\otimes X$. Also $G=\{II,ZZ,XY,YX\}$: Genau diese vier haben $\langle P\rangle=+1$, die übrigen zwölf Pauli-Strings haben $\langle P\rangle=0$.
* **Labels.** $T=\{00\,00,\;10\,10,\;01\,11,\;11\,01\}$ für $II$, $ZZ$, $XY$, $YX$ (hier qubitweise als $z_1x_1\,z_2x_2$ notiert). Isotropie-Probe für $XY$ und $YX$: $z\cdot x'+x\cdot z'=(0\cdot1+1\cdot1)+(1\cdot1+1\cdot0)=0 \bmod 2$.
* **Normalform.** $A=\{00,11\}$, $\ell(x)=x_1$, $q=0$, also $s=(1,0)$ und $\psi^*=(Z\otimes I)\psi$.
* **Bell-Verteilung.** Die Nebenklasse ist $ZI\cdot T\propto\{ZI,IZ,YY,XX\}$, jeweils mit Wahrscheinlichkeit $1/4$; eine direkte Rechnung in der Bell-Basis liefert dieselbe Verteilung wie Lemma 2. $II$ tritt nie auf: Ein einzelnes Bell-Sample liegt nie in $T$.
* **Ein Durchlauf.** Referenz $r_0=XX=01\,01$. Die weiteren Samples $ZI$, $YY$, $XX$ liefern die Differenzen $11\,01=YX$, $10\,10=ZZ$ und $00\,00$, die nichts trägt. Der Rang ist $2=n$, also $T=\mathrm{span}\{YX,ZZ\}$, und das dritte von null verschiedene Element ist $YX+ZZ=01\,11=XY$.
* **Vorzeichen.** Je eine Kopie, gemessen in der $ZZ$-Basis und in der $YX$-Basis, liefert jeweils $+1$. Da $(Z\otimes Z)(Y\otimes X)=(ZY)\otimes(ZX)=(-iX)\otimes(iY)=X\otimes Y$, ist $c=+1$ und $\lambda_{XY}=+1$. Der Zustand ist der eindeutige gemeinsame $+1$-Eigenzustand von $ZZ$ und $YX$; der Durchlauf brauchte 8 Kopien für das Bell-Sampling und 2 für die Vorzeichen.

## 8. Was die Promise einbringt und wo sie bricht

| Budget | Mit der Promise | Grund |
| --- | --- | --- |
| Kopien | $\Theta(n)$, Bell-Messungen auf zwei Kopien | Holevo liefert $\Omega(n)$; ein Bell-Sample ist auf $2^n$ von $4^n$ Ergebnissen beschränkt und trägt etwa $n$ Bits |
| Zeit | $O(n^3)$ | Dekodieren ist ein lineares Gleichungssystem über einem Körper |
| Speicher | $O(n^2)$ | das Stabilisator-Tableau |

Mit Einzelkopie-Messungen beträgt die Anzahl $\Theta(n^2)$: $O(n^2)$ nach Aaronson und Gottesman, und $\Omega(n^2)$ schon für Phasenzustände vom Grad 2 (Arunachalam, Bravyi, Dutt, Yoder, arXiv:2208.07851, Theorem 5); siehe [Kontrastpaar 1](https://deltorobarba.github.io/science/#1-one-copy-or-two-learning-stabilizer-states).

**Ob ein verborgener Unterraum leicht oder schwer zu finden ist, hängt vom Rauschmodell ab, nicht vom Unterraum.** Die Promise bricht auf vier Arten:

1. **Additives Rauschen auf jedem Sample** (LWE, LPN). Auch dort ist der Träger ein Unterraum, die verborgene Gerade der Displacement-Instanz, aber jedes Sample liegt um einen kleinen Fehler daneben, und Gauß-Elimination akkumuliert die Fehler. Stabilisatorzustände unter verrauschtem PAC-Zugriff sind LPN-schwer (Gollakota, Liang, arXiv:2102.05174).
2. **Rauschen auf einem Bruchteil der Samples.** Bei Stabilisator-Fidelität $\tau$ liegt ein Anteil von mindestens $\tau^4$ der Differenz-Samples *exakt* in $T$ (Grewal, Iyer, Kretschmer, Liang, arXiv:2304.13915). Saubere Samples existieren und müssen nur identifiziert werden: maximale Cliquen in Zeit $\exp(O(n/\tau^4))$, polynomiell oberhalb von $\cos^2(\pi/8)$, und quasipolynomiell für jedes $\tau$ durch Stabilizer Bootstrapping (arXiv:2408.06967).
3. **Eine kleinere Gruppe, Stabilisatordimension $n-t$.** Die Differenz-Samples liegen in $T^\perp$ der Dimension $n+t$ (arXiv:2305.13409, Fact 2.18); dessen symplektisches Komplement liefert $T$ zurück, und der $t$-Qubit-Rest kostet $2^{O(t)}$. Für $t=0$ ist $T^\perp=T$, und das ist der obige Fall.
4. **Qudits, $`d>2`$.** $`Z^*=Z^{-1}\neq Z`$, also ist $`\psi^*`$ kein Pauli-Bild von $`\psi`$ mehr. Bell-Differenz-Sampling auf vier Kopien liefert nur $`\mathrm{col}(V)\times\mathrm{col}(W)`$, gleichverteilt bei vollem Rang (Allcock, Doriguello, Ivanyos, Santha, arXiv:2405.06357, Theorem 39). Auswege sind das konjugierte Paar $`\rho\otimes\rho^*`$, gleichverteilt auf $`T`$ für jedes $`d`$, oder ein Hidden-Polynomial-Schritt für die quadratische Phase bei primem $`d`$. Für zusammengesetztes $`d`$ ist $`\mathbb{Z}_d`$ kein Körper, und die Hermite-Normalform ersetzt die Gauß-Elimination.

---

## Kontext: Zusammenfassung zweier SciencePedia-Artikel

Quellen: Bohrium SciencePedia, [Stabilizer States](https://www.bohrium.com/en/sciencepedia/feynman/keyword/stabilizer_states) und [Stabilizer Codes and Their Properties](https://www.bohrium.com/en/sciencepedia/feynman/quantum_information_quantum_computation-stabilizer_codes_and_their_properties) (Stil „Popular Science“). Beide Seiten sind laut Metadaten KI-generiert. Alle hier übernommenen Rechnungen wurden numerisch nachgeprüft; Abweichungen von der Quelle sind als **Korrektur** markiert, Ergänzungen als *eigene Anmerkung*. Notation wie oben: Labels $(z|x)$ mit $I\mapsto00$, $X\mapsto01$, $Z\mapsto10$, $Y\mapsto11$; $\mathcal S$ ist die Stabilisatorgruppe.

### A. Stabilisatorzustände

**A1. Leitbild: Eigenschaften statt Foto.** Einen Menschen kann man fotografieren, bis auf jede Pore (das entspricht dem vollen Zustandsvektor mit $2^n$ Amplituden), oder durch wenige feste Merkmale beschreiben. Der Stabilisatorformalismus wählt die zweite Art: Ein Zustand wird durch die $n$ Operatoren beschrieben, die ihn unverändert lassen. Ein Stabilisator wirkt wie ein geheimer Handschlag; antwortet der Zustand mit dem Faktor $+1$, ist er identifiziert.

**A2. Beispiel.** $g_1=X_1$, $g_2=X_2$, $g_3=Z_3$. $Z_3$ erzwingt $|0\rangle$ auf Qubit 3, $X_1$ und $X_2$ erzwingen $|+\rangle$ auf Qubit 1 und 2:
$$|\psi\rangle=|{+}{+}0\rangle=\tfrac12\big(|000\rangle+|010\rangle+|100\rangle+|110\rangle\big).$$

**A3. Messvorhersage ohne Zustandsvektor.** Für die Messung eines Pauli-Operators $M$ gibt es zwei Fälle:

* $M$ kommutiert mit allen $g_i$: Das Ergebnis ist deterministisch, $+1$ falls $M\in\mathcal S$, $-1$ falls $-M\in\mathcal S$ (vgl. Abschnitt 2: dann liegt $\pm M$ automatisch in $\mathcal S$).
* $M$ antikommutiert mit einem $g_k$: $\langle M\rangle=0$, das Ergebnis ist gleichverteilt. Beweis in einer Zeile, da $g_k$ hermitesch ist und $\psi$ stabilisiert: $\langle M\rangle=\langle\psi|Mg_k|\psi\rangle=-\langle\psi|g_kM|\psi\rangle=-\langle M\rangle$.

Faustregel: Zwei Pauli-Strings kommutieren genau dann, wenn sie auf einer geraden Anzahl von Positionen antikommutieren.

*Beispiel.* $g_1=X_1X_2$, $g_2=X_2X_3$, $g_3=Z_1Z_2Z_3$, gemessen wird $M=Y_1Y_2Z_3$. $M$ kommutiert mit allen drei Erzeugern (jeweils zwei antikommutierende Positionen). Mit $XZ=-iY$:
$$g_1g_3=(X_1Z_1)(X_2Z_2)Z_3=(-iY_1)(-iY_2)Z_3=-Y_1Y_2Z_3=-M,$$
also $-M\in\mathcal S$, und das Ergebnis ist mit Sicherheit $-1$. Diese Buchführung ist der Kern des Gottesman-Knill-Theorems.

**A4. Dynamik: Clifford-Gatter und Messungen.**

* Clifford-Gatter ($`H`$, $`S`$, CNOT) bilden Paulis auf Paulis ab (bis auf eine Phase), z. B. $`\mathrm{CNOT}_{c\to t}`$: $`X_c\mapsto X_cX_t`$, $`Z_t\mapsto Z_cZ_t`$. Man aktualisiert die $`n`$ Erzeuger statt des Vektors; die Quelle sagt: Man verfolgt nicht den Schauspieler, sondern sein Drehbuch.
* Messung eines antikommutierenden $M$ mit Ergebnis $\pm1$: Ein antikommutierender Erzeuger wird durch $\pm M$ ersetzt, die kommutierenden bleiben. **Korrektur:** Die Quelle sagt, *alle* antikommutierenden Erzeuger würden verworfen. Das stimmt nur, wenn genau einer antikommutiert. Allgemein multipliziert man zuerst jeden weiteren antikommutierenden Erzeuger mit dem ersten (danach kommutiert er mit $M$) und ersetzt nur diesen ersten; sonst gingen Erzeuger verloren und der Rang fiele unter $n$.
* *Beispiel GHZ.* $|\mathrm{GHZ}_3\rangle=(|000\rangle+|111\rangle)/\sqrt2$ mit Erzeugern $X_1X_2X_3$, $Z_1Z_2$, $Z_2Z_3$. Messung von $X_1$ mit Ergebnis $+1$ (Wahrscheinlichkeit $1/2$): Nur $Z_1Z_2$ antikommutiert und wird durch $X_1$ ersetzt. Neue Erzeuger $X_1$, $X_1X_2X_3$, $Z_2Z_3$, gleichwertig $X_1$, $X_2X_3$, $Z_2Z_3$; das ist der Zustand $|+\rangle\otimes(|00\rangle+|11\rangle)/\sqrt2$ (*eigene Ergänzung*).
* Genau dieses Herausmeißeln eines Zielzustands aus einem großen verschränkten Cluster-Zustand durch Messungen ist das Prinzip des messungsbasierten Quantenrechnens (MBQC).

**A5. Verschränkung als Zählproblem.** Für eine Bipartition $A|B$ eines Stabilisatorzustands gilt (in Bits)
$$S_A=n_A-k_A,$$
wobei $k_A$ die Anzahl unabhängiger Elemente von $\mathcal S$ ist, die nur auf $A$ wirken („lokale Gesetze“). Jedes lokale Gesetz nimmt $A$ einen Freiheitsgrad, den es sonst mit $B$ teilen könnte.

* Produktzustand $|\psi_A\rangle\otimes|\psi_B\rangle$: $k_A=n_A$, also $S_A=0$. Von den 60 Zwei-Qubit-Stabilisatorzuständen sind $36=6\cdot6$ Produktzustände.
* $g_1=Z_1X_2X_3$, $g_2=X_1Z_2X_3$, $g_3=X_1X_2Z_3$. Die Gruppe ist $\{III,\,g_1,\,g_2,\,g_3,\,Y_1Y_2,\,Y_1Y_3,\,Y_2Y_3,\,-Z_1Z_2Z_3\}$; kein Element wirkt nur auf Qubit 1, also $k_1=0$ und $S_1=1$. Qubit 1 ist maximal mit dem Rest verschränkt ($\rho_1=I/2$), ohne dass eine Amplitude berechnet wurde.

Merksatz der Quelle: Verschränkung ist das Fehlen lokaler Gesetze.

**A6. Anwendungen.**

* *Gottesman-Knill, die „klassische Insel“.* Clifford-Schaltkreise auf Stabilisatorzuständen sind klassisch effizient simulierbar; Evolution und Messung werden zu Matrixalgebra über $\mathbb F_2$. Beispiel der Quelle: Die Messwahrscheinlichkeiten der ersten Qubits eines Steane-codierten Zustands folgen aus dem Rang einer Teilmatrix des Tableaus.
* *Korrelationen in Cluster-Zuständen* liest man über Kommutation ab. *Eigene Anmerkung:* Für den linearen 4-Qubit-Cluster mit $K_1=X_1Z_2$, $K_2=Z_1X_2Z_3$, $K_3=Z_2X_3Z_4$, $K_4=Z_3X_4$ gilt $X_1Z_2Z_3X_4=K_1K_4\in\mathcal S$, also $\langle X_1Z_2Z_3X_4\rangle=+1$.
* *Fehlerkorrektur* (ausführlich in Teil B). Beim 5-Qubit-Code verletzt jeder Einzelqubitfehler die Stabilisatoren in einem eigenen Muster. Die Information ist delokalisiert: Für $A=\{q_1\}$, $B=\{q_2,q_3\}$, $C=\{q_4,q_5\}$ ist die bedingte Transinformation $I(A{:}C\,|\,B)=1$ Bit.
* *MBQC.* Ein großer Cluster-Zustand ist die Ressource; die Rechnung läuft allein über Einzelqubit-Messungen. Die Wahl der Messbasen ist das Programm, zufällige Ergebnisse steuern die Basen späterer Messungen.

**A7. Am Rand der Karte: Magie.** Gottesman-Knill ist zweischneidig: Was effizient simulierbar ist, kann keinen exponentiellen Vorteil liefern. Universelles Rechnen braucht Nicht-Clifford-Ressourcen, „Magie“.

* *T-Gatter.* $T=\mathrm{diag}(1,e^{i\pi/4})$ auf $|+\rangle$:
  $$|\langle +|T|+\rangle|^2=\frac{|1+e^{i\pi/4}|^2}{4}=\frac{2+\sqrt2}{4}=\cos^2(\pi/8)\approx0.854.$$
  *Eigene Anmerkung:* Das ist zugleich die maximale Stabilisator-Fidelität von $T|+\rangle$ ($|+\rangle$ und $|{+i}\rangle$ liegen gleich nah), also genau die Schwelle $\cos^2(\pi/8)$ aus Abschnitt 8, Punkt 2.
* *Stabilisatorrang* $\chi$ = minimale Anzahl von Stabilisatorzuständen in einer Superposition. Für $\mathrm{CCZ}|{+}{+}{+}\rangle$ gilt $\sum_x(-1)^{x_1x_2x_3}|x\rangle=\sum_x|x\rangle-2|111\rangle$, also $\chi=2$. Zeitentwicklung unter geeigneten Hamiltonoperatoren erzeugt ebenfalls Zustände mit $\chi=2$.
* *Kohärente Fehler.* $T_j=e^{i\pi/8}\big(\cos\tfrac\pi8\,I-i\sin\tfrac\pi8\,Z_j\big)$. Auf einen logischen Zustand des 5-Qubit-Codes angewandt entsteht eine Superposition zweier Stabilisatorzustände, $\chi=2$. Magie ist also Ressource und zugleich besonders tückischer Fehler.
* *Stabilisator-Fidelität* (Maximum der Fidelität über alle Stabilisatorzustände) misst Magie stetig. Beispiel der Quelle: $e^{-i\theta Z_1Z_2}$ mit $\theta=\pi/16$ ist nicht Clifford, der erzeugte Zustand liegt aber nahe an der Stabilisatormenge. *Eigene Rechnung:* Auf $|{+}{+}\rangle$ angewandt beträgt die Stabilisator-Fidelität $\cos^2(\pi/16)\approx0.962$.

**A8. Was Stabilisatoren über die Quantenmechanik zeigen.**

* *Klonen.* Der optimale symmetrische universelle Kloner erreicht die mittlere Fidelität $5/6$. Laut Quelle fällt sie mit nur Clifford-Gattern und Stabilisator-Ankillas auf $2/3$, genau den Wert der klassischen Strategie „messen und präparieren“. Der Quantenvorteil beim Klonen hängt an der Magie.
* *Typische Stabilisatorzustände sind hochverschränkt.* Die Wahrscheinlichkeit, dass ein festes Qubit eines zufälligen $n$-Qubit-Stabilisatorzustands unverschränkt ist, beträgt exakt (*eigene Rechnung* mit $N(n)=2^n\prod_{k=1}^n(2^k+1)$ aus Rechnung 3)
  $$\frac{6\,N(n-1)}{N(n)}=\frac{3}{2^n+1},$$
  Probe $n=2$: $36/60=3/5$. Die Quelle nennt nur die Skalierung $\sim2^{-n}$.

### B. Stabilisatorcodes

**B1. Leitbild: das verteilte Geheimnis.** Ein Geheimnis, in Stücke zerlegt und auf vertraute Freunde verteilt, steckt in keiner einzelnen Person, sondern in den Beziehungen zwischen ihnen; der Verrat eines Einzelnen schadet nicht. Ebenso steckt ein logisches Qubit in den Korrelationen vieler physikalischer Qubits. Die Rolle der Freunde übernimmt ein „Geheimbund“ kommutierender Pauli-Operatoren. Der Coderaum ist ihr gemeinsamer $+1$-Eigenraum, $S|\psi\rangle=|\psi\rangle$ für alle $S\in\mathcal S$ (der geheime Handschlag). Kommutieren ist Pflicht: Gilt $S_1S_2=-S_2S_1$, kann kein Zustand $+1$-Eigenzustand beider sein.

**B2. Binärsprache.** Mit der Kodierung aus Abschnitt 2 werden Kommutatoren zu Arithmetik, $v_a\odot v_b=z_a\cdot x_b+x_a\cdot z_b \bmod 2$ (0: kommutieren, 1: antikommutieren). Beispiel auf 4 Qubits: $S_1=Y_1Z_2X_3\mapsto(1100|1010)$, $S_2=X_1Z_2Z_4\mapsto(0101|1000)$. Es ist $z_1\cdot x_2=1$ und $x_1\cdot z_2=0$, also $v_1\odot v_2=1$: Sie antikommutieren (direkt: nur auf Qubit 1 stehen sich $Y$ und $X$ gegenüber). Redundante Erzeugerlisten reduziert man per Gauß-Elimination auf $m$ unabhängige.

**B3. Größe des Coderaums.** Jeder unabhängige Erzeuger halbiert den Raum: $\dim\mathcal C=2^{n-m}$, also $k=n-m$ logische Qubits; Stabilität kostet Redundanz. Geometrisch: $P_{\mathcal C}=\frac1{|\mathcal S|}\sum_{s\in\mathcal S}s$ projiziert auf den Coderaum (Zustände außerhalb löschen sich durch destruktive Interferenz aus), und $\mathrm{Tr}\,P_{\mathcal C}=2^{n-m}$. Das ist Rechnung 1 mit $m$ statt $n$ Erzeugern.

**B4. Detektivarbeit: das Syndrom.** Nach einem Fehler $E$ gilt $g_iE|\psi\rangle=\pm E|\psi\rangle$, je nachdem ob $E$ mit $g_i$ kommutiert ($+1$, kein Alarm) oder antikommutiert ($-1$, Alarm). Die Alarm-Bits aller Erzeuger bilden das Syndrom; die codierte Information wird dabei nie gemessen. Beispiel [[5,1,3]]-Code mit
$$g_1=XZZXI,\quad g_2=IXZZX,\quad g_3=XIXZZ,\quad g_4=ZXIXZ.$$
$Z_1$ antikommutiert mit $g_1$ und $g_3$ (dort steht $X$ auf Qubit 1), also Syndrom $(1,0,1,0)$. Alle 15 Einzelqubitfehler liefern verschiedene, von null verschiedene Syndrome. Korrigiert wird durch nochmaliges Anwenden des erkannten Fehlers ($Z_1Z_1=I$), eine Art Quanten-Rechtschreibprüfung.

**B5. Stille Fehler, logische Operatoren, Distanz.** Kommutiert $E$ mit allen Erzeugern (Syndrom null), gibt es zwei Fälle:

* $E\in\mathcal S$: ein harmloser Geist, der auf dem Coderaum als Identität wirkt.
* $E\notin\mathcal S$: ein logischer Operator, der „Meisterdieb“; er verändert die Information ohne Alarm, z. B. $|\bar0\rangle\mapsto|\bar1\rangle$.

Die Distanz $d$ ist das minimale Gewicht eines logischen Operators; $d\ge2t+1$ erlaubt die Korrektur von $t$ Fehlern. Decodiert wird mit dem Fehler kleinsten Gewichts zum gemessenen Syndrom.

**Korrektur zur Begriffswahl:** Die Quelle nennt es „Degeneriertheit“, dass beim Steane-Code ein Einzelfehler $Z_k$ und ein Zweifachfehler $Z_iZ_j$ dasselbe Syndrom haben (dort $Z_1$ und $Z_2Z_7$, je nach Spaltennummerierung; mit $h_j=\mathrm{bin}(j)$ etwa $Z_1$ und $Z_2Z_3$). Die beiden unterscheiden sich aber um $Z_iZ_jZ_k$, einen logischen Operator vom Gewicht 3, nicht um einen Stabilisator. Das ist genau der Mechanismus einer Fehlkorrektur. Degeneriertheit im Fachsinn meint Fehler, die sich um ein Stabilisatorelement unterscheiden und deshalb gleich wirken.

**B6. Konstruktion und Grenzen.**

* *CSS-Konstruktion.* Aus zwei klassischen linearen Codes baut man $X$-Stabilisatoren aus den Prüfzeilen des einen und $Z$-Stabilisatoren aus denen des anderen; Bedingung ist $H_XH_Z^{\top}=0$ (jede $X$-Prüfzeile orthogonal zu jeder $Z$-Prüfzeile). Die logischen Operatoren entsprechen klassischen Codewörtern. Der Steane-Code ist CSS aus dem Hamming-Code $[7,4,3]$.
* *Quanten-Hamming-Schranke* (für nichtdegenerierte Codes):
  $$2^k\sum_{j=0}^{t}\binom nj3^j\le2^n.$$
  Für $k=t=1$ wird daraus $2(1+3n)\le2^n$; $n=4$ liefert $26>16$, $n=5$ liefert $32=32$. Der [[5,1,3]]-Code erreicht die Schranke mit Gleichheit, ist also *perfekt*: Die $2^4=16$ Syndrome entsprechen genau „kein Fehler“ plus den 15 Einzelqubitfehlern. Zugleich erfüllt er die Quanten-Singleton-Schranke $n-k\ge2(d-1)$ mit Gleichheit ($4=4$).
* *Logische Zustände sind hochverschränkt.* $|\bar0\rangle$ des Steane-Codes ist die gleichgewichtete Superposition der 8 Codewörter des dualen Hamming-Codes $[7,3]$ (Gewichte 0 und 4); jedes einzelne Qubit ist maximal gemischt. Die Information sitzt im Netz der Verschränkung, nicht in einem Qubit.

**B7. Werkzeugkasten für fehlertolerantes Rechnen.**

* *Torischer Code.* Ein $Z$-Fehler kippt die beiden Stern-Stabilisatoren an seinen Enden (zwei Anregungen). Decodieren heißt, den kürzesten Weg zwischen den angeregten Ecken zu finden (Manhattan-Abstand auf dem Gitter) und dort $Z$ anzuwenden; die codierte Information wird dabei nie angesehen.
* *Transversale Gatter.* Ein Gatter auf jedem Qubit einzeln breitet Fehler nicht innerhalb des Blocks aus. **Korrektur:** Beim Steane-Code wirkt $S^{\otimes7}$ als logisches $\bar S^\dagger$, nicht als $\bar S$ wie in der Quelle, denn $|\bar1\rangle$ besteht aus Codewörtern vom Gewicht 3 und 7, und $i^3=i^7=-i$. Das logische $\bar S$ erhält man mit $(S^\dagger)^{\otimes7}$.
* *Fehlerausbreitung.* Ein CNOT mit Crosstalk kann einen Einzelfehler im Kontrollblock in einen Zweifachfehler verwandeln; das Syndrom führt dann zur falschen Korrektur, und es bleibt ein logischer Fehler. Solche Pfade zu analysieren ist das Tagesgeschäft fehlertoleranter Architektur.
* *Verkettung.* Jedes physikalische Qubit eines äußeren Codes wird mit einem inneren Code codiert; die Distanzen multiplizieren sich, $d=d_1d_2$, und Fehler lassen sich im Prinzip beliebig unterdrücken. Weitere Konstruktionen sind Hypergraph-Produkt-Codes und Bicycle-Codes; Symmetrien wie die Hadamard-Dualität verbinden Codes miteinander.

**B8. Codes als Materie.** Der Hamiltonoperator $H=-\sum_iS_i$ hat den Coderaum als Grundzustandsraum; Stabilisatorcodes werden so zu exakt lösbaren Modellen neuer Phasen.

* *Topologische Ordnung* (torischer Code). Auf dem Torus ist der Grundzustand vierfach entartet, und die vier Zustände sind lokal ununterscheidbar: ein geschützter Speicher. Die Verschränkung zwischen zwei Regionen skaliert mit der Randlänge minus einer universellen Konstante; für eine Zylinderpartition ist die logarithmische Negativität $`E_N=L_y-1`$. Das „$`-1`$“ ist die topologische Verschränkungsentropie (1 Bit).
* *Fraktonphasen* (X-Cube-Modell in 3D). Fraktonen sind unbeweglich, Lineonen nur entlang einer Linie, Planonen nur in einer Ebene beweglich. Die Grundzustandsentartung hängt auf komplizierte Weise von der Systemgröße ab.
* *Frakton-Elastizitäts-Dualität.* Lineonen entsprechen Versetzungen in einem klassischen Kristall. Ein Lineon, das um eine Schraubenversetzung herumgeführt wird, erhält eine Phase, analog zum Aharonov-Bohm-Effekt.

**B9. Synthese: Defekte flechten.** Die Anyonen $e$ und $m$ des torischen Codes sind abelsch; Flechten liefert nur Phasen. Ausweg ohne neues Material: Twist-Defekte im Oberflächencode, also Versetzungen im Gewebe des Codes, an denen Stern- und Plakettenstabilisatoren die Rollen tauschen. Sie binden Majorana-Nullmoden und verhalten sich nicht-abelsch; Flechten ergibt geschützte logische Gatter, allerdings nur bis auf ein Pauli-Nebenprodukt, das ein klassischer Pauli-Rahmen mitführt (projektive Statistik). *Eigene Anmerkung:* Ising-artiges Flechten dieser Defekte erzeugt nur Clifford-Gatter; für Universalität braucht man weiterhin Magie (A7).

**B10. Übungen der Quelle, nachgerechnet.**

1. *[[3,1]]-Spielzeugcode*, $S_1=X_1Z_2$, $S_2=Z_2X_3$, $\bar Z=Z_2$. Gesucht ist $|\langle100|\bar0\rangle|^2$. $Z_2=+1$ erzwingt $q_2=0$; darauf wirken $S_1$ und $S_2$ wie $X_1$ und $X_3$. Also
   $$|\bar0\rangle=|{+}\rangle|0\rangle|{+}\rangle=\tfrac12\big(|000\rangle+|001\rangle+|100\rangle+|101\rangle\big),\qquad|\langle100|\bar0\rangle|^2=\tfrac14.$$
   *Eigene Anmerkung:* Da $\bar Z=Z_2$ Gewicht 1 hat, ist $d=1$; der Code korrigiert nichts und dient nur der Übung.
2. *[[5,1,3]], Fehler $`X_1`$, falsche Korrektur $`Z_2`$.* $`|\langle\bar0|Z_2X_1|\bar0\rangle|^2=0`$, denn $`X_1Z_2`$ antikommutiert mit $`g_2=IXZZX`$ (auf Qubit 2 stehen sich $`Z`$ und $`X`$ gegenüber), und nach A3 verschwindet dann der Erwartungswert. Der Endzustand liegt im $`-1`$-Eigenraum von $`g_2`$, also orthogonal zum gesamten Coderaum; das Syndrom zeigt die misslungene Korrektur an.
3. *Steane-Code, alle 189 Fehler vom Gewicht 2, Minimalgewicht-Decoder.* Die Quelle zählt 63 logische Fehler: Die 21 Fehler jedes reinen Typs $X_iX_j$, $Z_iZ_j$, $Y_iY_j$ haben das Syndrom eines Einzelfehlers am Qubit $k$ mit $h_k=h_i+h_j$, und die Korrektur ergänzt sie zu einem logischen Operator vom Gewicht 3.
   **Korrektur:** Die 126 gemischten Fehler fallen in 42 Syndromklassen zu je drei Fehlern vom Gewicht 2, nämlich $X_iZ_j$, $Y_iZ_m$, $Y_jX_m$ mit $h_m=h_i+h_j$. Diese unterscheiden sich paarweise um logische Operatoren, z. B. $X_iZ_j\cdot Y_iZ_m\propto Z_iZ_jZ_m$. Ein deterministischer Decoder korrigiert in jeder Klasse höchstens einen, also scheitern mindestens $63+84=147$ der 189 Fehler. Der übliche CSS-Decoder ($X$- und $Z$-Teil getrennt) erreicht genau 147: Er korrigiert die 42 Fehler vom Typ $XZ$ und scheitert an allen Fehlern der Typen $XY$ und $YZ$. Die Zahl 63 setzt stillschweigend voraus, dass der Decoder bei Gleichstand den wahren Fehler errät; sie zählt nur die Fehler, die bei *jeder* Wahl scheitern.
