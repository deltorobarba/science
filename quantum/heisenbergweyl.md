# Heisenberg-Weyl

## Quantum Harmonic Oscillator and Quantum Operators

![Quantum Harmonic Oscillator](https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/HarmOsziFunktionen.png/330px-HarmOsziFunktionen.png)

* **Quantum Harmonic Oscillator as Source of All Operators (Physics Basis)**
  * **Analytically:** Every smooth potential near a local minimum approximates a parabola (Taylor expansion $V(x) \approx \frac{1}{2}k x^2$). Consequently, the QHO $\hat H \propto \hat P^2 + \hat Q^2 = \hbar\omega\left(\hat a^\dagger\hat a + \tfrac12\right) = \hbar\omega(\hat n + \tfrac12)$ serves as the universal local model of any bound physical system.
  * **Algebraically:** $\hat Q^2 + \hat P^2$ is the canonical degree-2 element of the Weyl algebra ($\mathrm{Sym}^2 V \cong \mathfrak{sp}$) — the bosonic counterpart of the Dirac operator. All quantum gates and dynamical evolutions derive from this single generator evaluated at different polynomial degrees.
  * **Every quantum gate is a time evolution** $U = e^{-i\hat Ht}$. **Time evolution as phase rotation:** In $\hat U(t) = e^{-i\hat Ht/\hbar}$, the exponent is dimensionless: time is fundamentally an angle. Quantum states do not travel along classical trajectories; their phase rotates (in an energy eigenstate at angular frequency $\omega = E/\hbar$).
  * **Kinetic $\leftrightarrow$ potential swap:** At $t=0$, the state resides in $Q$; after a quarter period $t = \frac{\pi}{2\omega}$, it has rotated $90^\circ$ into $P$. **This quarter turn is Quantum Fourier Transform.**
  * **Two Fundamental State Families (States, Not Gates)** *Coherent states $\vert{}\alpha\rangle = \hat D(\alpha)\vert{}0\rangle$:* Eigenstates of the annihilation operator $\hat a$; overcomplete, generated as degree-1 displacement outputs. *Fock states $\vert{}n\rangle$:* Orthonormal eigenstates of the number operator $\hat n = \hat a^\dagger\hat a$; form the eigenbasis of the quadratic degree-2 generator.
  * **Phase Space & Why Complex Numbers**: Complex amplitude $\hat a \propto \hat Q + i\hat P$: The real axis represents position, the imaginary axis represents momentum, and unitary rotation $e^{i\omega t}$ describes time evolution. Two real canonical coordinates merge into a single complex amplitude $\alpha = x + ip$, whose magnitude is preserved under unitary phase rotations.
  * **Position basis = Computational basis:** The basis states $\vert{}k\rangle$ are eigenstates of $\hat Q$. Consequently, $Z$ (diagonal phase) is a function of position, whereas $X$ (permutation / shift) is a function of momentum.
* **Exponentiation**
  * Exponentiation generates Gates: $\hat U = e^{-i\hat G\theta}$. The factor $e^{-i\theta}$ guarantees unitarity, $\hat G$ is the Hermitian generator of the transformation, and $\theta$ scales it. When $\hat G = \hat H$, then $\theta = t/\hbar$, meaning $\hat H$ *is* time evolution itself.
  * The generator is constructed directly from $\hat Q, \hat P$ for continuous variables (CV) or from $X, Z \pmod d$ for discrete qudits, grounded in the canonical commutation relations (CCR) $[\hat x, \hat p] = i\hbar$.
  * **Gaussian (linear):** Generators of degree $\leq 2$. "Linear" refers strictly to the Heisenberg action $U^\dagger \hat r U = S\hat r + d$, not to the generator itself. Symplectic phase-space structure is preserved.
  * **Non-Gaussian (nonlinear):** Generators of degree $\geq 3$. The Heisenberg action becomes nonlinear (e.g., $\hat p \to \hat p - 3\gamma t \hat q^2$), and the Wigner quasi-probability distribution develops negative regions.
  * **From energy term to gate.** The physical energy terms are quadratic, but the **elementary gates** exponentiate the *linear* field operators $\hat P$ and $\hat Q$.
* **Conjugation**
  * An operator generates translations of its canonically conjugate variable. This mechanism enables reciprocal basis changes $X \leftrightarrow Z$ via the Fourier transform ($X = \mathrm{DFT}^\dagger \, Z \, \mathrm{DFT}$) and underlies the Weyl displacement operator: $D_{q,p} = \tau^{qp} X^q Z^p$
  * **Commutation relations:** Continuous: $[\hat x, \hat p] = i\hbar$. Discrete: Weyl relation $ZX = \zeta_d XZ$.
  * **Notation:** $\zeta_d = e^{2\pi i/d}$ is the primitive $d$-th root of unity; $\tau = e^{i\pi/d}$ is the half-phase satisfying $\tau^2 = \zeta_d$. While many texts write $\omega$ for $\zeta_d$, here $\omega$ is reserved exclusively for oscillator frequency and the symplectic form.
  * **Synthesizing elementary gates:** Physical Hamiltonian terms are quadratic ($\hat P^2, \hat Q^2$), but elementary gates exponentiate the *linear* field operators:
    * Momentum operator $\hat P$ represents momentum but generates a **position shift**: $D_{q,0} \sim X^q \implies X \approx e^{-i\hat P\delta}$ (Shift / bit-flip).
    * Position operator $\hat Q$ represents position but generates a **momentum kick**: $D_{0,p} \sim Z^p \implies Z \approx e^{i\hat Q\delta}$ (Clock / phase-flip).
  * $`X = \mathrm{DFT}^\dagger\, Z\, \mathrm{DFT}`$ - In the momentum basis, the spatial shift operator becomes diagonal and acts identically to clock operator.
* **Kinetic Energy ($\hat P^2$ / Momentum & Shifts)** - Exponentiation $X \approx e^{-i\hat P\delta}$
  * **Continuous-Variable (CV) Observable:** $\hat P = \frac{i}{\sqrt{2}}(\hat a^\dagger - \hat a)$, representing the differential derivative operator $\approx i(X^\dagger - X)$. **Lattice Term:** Corresponds to hopping / kinetic kinetic energy or the discrete Laplacian $\approx X + X^\dagger$ (as probed in OTOC experiments).
  * **Qudit Gate (Shift):** $X^a\vert{}j\rangle = \vert{}j+a \bmod d\rangle$, acting as an off-diagonal permutation of basis states with eigenvalues given by powers of $\zeta_d$. **Qubit Gate (Bit-Flip):** Pauli $X$, which flips computational basis states ($\vert{}0\rangle \leftrightarrow \vert{}1\rangle$) with root of unity $\zeta_2 = -1$.
  * **Matrix Representation:** Real, off-diagonal permutation matrix.
  * **Conjugation Relation:** While $X$ physically *represents* momentum, it *generates* a spatial translation/position shift ($D_{q,0} \sim X^q$).
  * **Fourier Dual Representation:** $X = \mathrm{DFT}^\dagger \, Z \, \mathrm{DFT}$ — transformed into the momentum basis via the discrete Fourier transform, the spatial shift operator becomes diagonal and acts identically to the clock operator.
* **Potential Energy ($\hat Q^2$ / Position & Clocks)** - Exponentiation $Z \approx e^{i\hat Q\delta}$.
  * **Continuous-Variable (CV) Observable:** $\hat Q = \frac{1}{\sqrt{2}}(\hat a + \hat a^\dagger)$, possessing continuous real eigenvalues corresponding directly to spatial position ($k$). **Lattice Term:** On-site potential (diagonal energy landscape).
  * **Qudit Gate (Clock):** $Z^b\vert{}k\rangle = \zeta_d^{bk}\vert{}k\rangle$, applying a diagonal phase gradient along the unit circle; unitary for all $d$, but non-Hermitian when $d > 2$. **Qubit Gate (Phase-Flip):** Pauli $Z$, mapping $\vert{}j\rangle \mapsto (-1)^j\vert{}j\rangle$; strictly both unitary *and* Hermitian, making it directly measurable as a physical observable.
  * **Matrix Representation:** Diagonal matrix composed of complex phase factors.
  * **Conjugation Relation:** While $Z$ physically *represents* position, it *generates* a momentum translation/kick ($D_{0,p} \sim Z^p$).


The physical and information-theoretic complexity of the gate is determined by the **polynomial degree of the generator $\hat H$ in the phase-space operators $\hat Q, \hat P$**, and the criterion behind the ladder is whether that degree still **closes under the commutator**. Degree 1: displacements (Pauli / Heisenberg-Weyl). Degree 2: Gaussian / Clifford, classically simulable. Degree $\geq 3$: non-Gaussian / non-Clifford, universal, quantum advantage.

| Property | Degree 1: Translations (Displacements) | Degree 2: Gaussian / Clifford | Degree $\geq 3$: Non-Gaussian / Non-Clifford |
| --- | --- | --- | --- |
| **Generators ($\hat{H}$)** | Linear: $q\hat{P} - p\hat{Q}$, $\hat{a}$, $\hat{a}^\dagger$ | Purely quadratic: $\hat{Q}^2+\hat{P}^2$, $\hat{Q}^2-\hat{P}^2$, $\hat{Q}_1\hat{P}_2$ | Nonlinear: $\hat{Q}^3$, $\hat{n}^2$, many-body interactions ($n_\uparrow n_\downarrow$) |
| **Lie Algebra Closure** | Closes in $\mathfrak{h}_n$ (Heisenberg algebra, $\dim = 2n+1$); $[\hat{Q},\hat{P}]$ is central | Closes in $\mathfrak{sp}(2n,\mathbb{R})$ (symplectic); with degree 1: $\mathfrak{sp}(2n) \ltimes \mathfrak{h}_n$ | **Does not close:** $[\hat{Q}^3, \hat{P}^2] \sim \hat{Q}^2\hat{P} \implies$ generates an infinite-dimensional Lie algebra |
| **Action on Phase Space** | Rigid shift vector $(q, p)$; no change of shape or volume | Linear symplectic map: $U^\dagger \hat{r} U = S\hat{r}$ ($S \in \mathrm{Sp}(2n)$); shear, squeezing, rotation | Bends phase space nonlinearly; the Wigner function develops negative regions |
| **Continuous-Variable (CV) Gates** | **Displacement operator:** $\hat{D}(\alpha) = e^{\alpha\hat{a}^\dagger - \alpha^*\hat{a}}$ | **Rotator:** $R(\theta) = e^{-i\theta\hat{n}}$<br>**Squeezer:** $\hat{S}(r) = e^{\frac{r}{2}(\hat{a}^2 - \hat{a}^{\dagger 2})}$<br>**Beamsplitter:** $\hat{B}(\theta) = e^{\theta(\hat{a}_1^\dagger\hat{a}_2 - \hat{a}_1\hat{a}_2^\dagger)}$ | **Cubic phase gate:** $e^{i\gamma\hat{Q}^3}$<br>**Kerr nonlinearity:** $e^{i\chi\hat{n}^2}$ (basis for cat states / bosonic QEC) |
| **Discrete Qudit/Qubit Gates** | **Pauli Group $\mathcal{P}$ / HW:**<br>• $X$ (shift / bit flip)<br>• $Z$ (clock / phase flip)<br>• $Y = iXZ$ is not a new generator, but the lattice point $(1,1)$ | **Clifford Group $\mathcal{C}$:**<br>• **QFT / Hadamard ($H$):** Discrete phase rotation ($90^\circ$)<br>• **Phase ($S$):** Corresponds to a shear ($P \to P+Q$)<br>• **CNOT / C-SUM:** Two-mode entanglement ($e^{-i\hat{Q}_1\hat{P}_2}$) | **Non-Clifford:**<br>• $T$ gate ($e^{-i\frac{\pi}{8}Z}$, discrete cubic phase)<br>• Qudit $T_d$ ($\vert{}k\rangle \mapsto \zeta_d^{k^3}\vert{}k\rangle$)<br>• Toffoli, Controlled-$S$ (CS) |
| **Classification & Clifford Hierarchy** | **Level $\mathcal{C}_1$:** $\mathcal{C}_1 = \mathcal{P}$ (forms an orthogonal operator basis of the state space) | **Level $\mathcal{C}_2$:** Normalizer of the Pauli group ($\mathcal{C}/\mathcal{P} \cong \mathrm{Sp}(2n, \mathbb{Z}_d)$) | **Level $\mathcal{C}_k$ ($k \geq 3$):** $\mathcal{C}_k = \{U : U\mathcal{P}U^\dagger \subseteq \mathcal{C}_{k-1}\}$. No longer groups; Clifford+$T$ is dense in $U(2^n)$ |
| **Classical Simulability** | Exactly and efficiently simulable | **Gottesman-Knill theorem:** Polynomial in $n$ via a $2n \times 2n$ symplectic tableau / CHP algorithm | Exponential cost: Scales with the stabilizer rank $\chi \approx 2^{0.396 t}$ ($t$ = number of $T$ gates) or the Wigner negativity |
| **Fermionic Counterpart** | **None:** Parity superselection forbids odd fermionic Hamiltonians | **Matchgates / Free Fermions:** Lie algebra $\mathfrak{so}(2n) \to \mathrm{Spin}(2n)$ | **Degree 3 is missing:** Non-simulability starts strictly at **degree 4** (e.g. Hubbard interaction $U n_\uparrow n_\downarrow$) |

---

**The Gottesman-Knill Principle (Degree 2)**
* An $n$-qubit stabilizer state is determined by $n$ independent, commuting Pauli operators.
* It is represented by an $n \times 2n$ binary tableau; gate updates cost $\mathcal{O}(n)$, measurements $\mathcal{O}(n^2)$.
* The Clifford group modulo Paulis is strictly finite: $\vert{}\mathcal{C}_n / \mathcal{P}_n\vert{} = \vert{}\mathrm{Sp}(2n, \mathbb{Z}_2)\vert{} \approx 2^{2n^2+n}$. The polynomial space of this manifold explains the efficient classical simulability compared with the doubly exponential full space $U(2^n)$.

**The Origin of Quantum Advantage (Degree $\geq 3$)**
* *Operator branching:* Every gate from $\mathcal{C}_3$ (such as the $T$ gate) can formally be written as a sum of Pauli matrices, but under iterated conjugation the number of terms explodes exponentially.
* *Stabilizer rank & magic simulation:* The classical runtime scales polynomially in the number of qubits $n$, but exponentially in the number of non-Clifford gates: $\chi(\vert{}T\rangle^{\otimes t}) \lesssim 2^{0.396 t}$
* *Magic state distillation:* Universal fault-tolerant computation produces non-Clifford resources via quantum teleportation and transversal Clifford filters. The **$T$-count** thus serves as the universal currency for algorithmic computational cost.

<br>