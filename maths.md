# <font color="blue">**Mathematics**

![science](https://raw.githubusercontent.com/deltorobarba/science/main/science.JPG)

##### <font color="blue">*Heisenberg-Weyl*

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

<font color="blue">**Tensor Algebra $T(V)$ as the Source of Four Algebras: $\Lambda$, $\mathrm{Sym}$ (classical) and $\mathrm{Cl}$, $W$ (quantized) — Fermions vs. Bosons**</font>

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
