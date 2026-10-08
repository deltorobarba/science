
# Science 🎨

Alexander Del Toro Barba, PhD. [Google Scholar](https://scholar.google.com/citations?hl=en&user=fddyK-wAAAAJ) $\cdot$ [LinkedIn](https://www.linkedin.com/in/deltorobarba/)


<img src="https://raw.githubusercontent.com/deltorobarba/science/main/gcp/nature.JPG" alt="science">

<br>

## Quantum Computing 🪼
* https://deltorobarba.github.io/science/ 
* [Quantum Dynamics](https://github.com/deltorobarba/science/blob/main/dynamics.ipynb) - research code
* [Quantum Computing](https://github.com/deltorobarba/science/blob/main/circuit.ipynb) - research code

## Astrophysics 🔭
* [Galaxies and Nebulae](https://github.com/deltorobarba/science/blob/main/galaxies.ipynb) 🧬 research code
* [Exoplanets](https://github.com/deltorobarba/science/blob/main/exoplanets.ipynb) 🪐 research code
* [Gravitational Waves](https://github.com/deltorobarba/science/blob/main/gravitationalwaves.ipynb) 🛰️ research code
* [Stars and Solar](https://github.com/deltorobarba/science/blob/main/stars.ipynb) ✨ research code

<br>

## Heisenberg-Weyl


### Heisenberg-Weyl

> Every quantum gate is a time evolution $U = e^{-i\hat Ht}$. The physical and information-theoretic complexity of the gate is determined by the **polynomial degree of the generator $\hat H$ in the phase-space operators $\hat Q, \hat P$**, and the criterion behind the ladder is whether that degree still **closes under the commutator**. Degree 1: displacements (Pauli / Heisenberg-Weyl). Degree 2: Gaussian / Clifford, classically simulable. Degree $\geq 3$: non-Gaussian / non-Clifford, universal, quantum advantage.

---

#### Physics: Quantum Harmonic Oscillator as Source of All Operators

![Quantum Harmonic Oscillator](https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/HarmOsziFunktionen.png/330px-HarmOsziFunktionen.png)

**Why the QHO $\hat H \propto \hat P^2 + \hat Q^2 = \hbar\omega\left(\hat a^\dagger\hat a + \tfrac12\right) = \hbar\omega(\hat n + \tfrac12)$ is *the* starting point.** Analytically, every smooth potential near a minimum is quadratic (Taylor expansion), so the QHO is the universal local model of any bound physical system. Algebraically, $\hat Q^2 + \hat P^2$ is *the* canonical degree-2 element of the Weyl algebra ($\mathrm{Sym}^2 V \cong \mathfrak{sp}$), the bosonic counterpart of the Dirac operator. Everything below is this one single generator, read at different polynomial degrees.

* **Time evolution = swap kinetic $\leftrightarrow$ potential.** At $t=0$ the state sits in $`Q`$; after a quarter period $t = \frac{\pi}{2\omega}$ it has rotated $90°$ into $P$. **That quarter turn is the QFT.** In $\hat U(t) = e^{-i\hat Ht/\hbar}$ the exponent is dimensionless: time is fundamentally an angle. States do not move along classical trajectories; their phase rotates, in an energy eigenstate at the angular frequency $\omega = E/\hbar$.
* **Why complex numbers.** $\hat a \propto \hat Q + i\hat P$: the real axis represents position, the imaginary axis represents momentum, and the rotation $e^{i\omega t}$ represents time evolution. Two real canonical coordinates merge into one complex amplitude $\alpha = x + ip$; unitary phase rotation preserves its magnitude.
* ⚠️ **Position basis = computational basis.** $\vert{}k\rangle$ are eigenstates of $\hat Q$. Hence $Z$ (diagonal phase) is a function of position, while $X$ (permutation / shift) is a function of momentum.
* ⚠️ **Two families of *states*, not gates:**
* Coherent states $\vert{}\alpha\rangle = \hat D(\alpha)\vert{}0\rangle$ (eigenstates of the annihilation operator $\hat a$, overcomplete, generated as a degree-1 output).
* Fock states $\vert{}n\rangle$ (eigenstates of the number operator $\hat n$, orthonormal, forming the eigenbasis of the quadratic degree-2 generator).

**Exponentiation produces the gates.** Every unitary gate takes the form: $\hat U = e^{-i\hat G\theta}$

Here, $e^{-i\theta}$ guarantees unitarity, $\hat G$ is the Hermitian generator of the transformation, and $\theta$ scales it. If $\hat G = \hat H$, then $\theta = t/\hbar$, meaning $\hat H$ *is* time evolution itself. The generator is built directly from $\hat Q, \hat P$ for continuous variables (CV) or from $X, Z \pmod d$ for discrete qudits, grounded on the canonical commutation relations (CCR) $[\hat x,\hat p] = i\hbar$.

* **Gaussian (linear):** Generator of degree $\leq 2$. ⚠️ "Linear" refers strictly to the *Heisenberg action* $U^\dagger \hat r U = S\hat r + d$, not to the generator itself. Symplectic phase-space structure is preserved.
* **Non-Gaussian (non-linear):** Generator of degree $\geq 3$. The Heisenberg action itself becomes nonlinear (e.g., $\hat p \to \hat p - 3\gamma t \hat q^2$), and the Wigner function develops negative regions.

**The conjugate relation.** An operator generates the translation of its canonically conjugate variable. This mechanism enables the reciprocal basis change $X \leftrightarrow Z$ via Fourier transform and underlies the Weyl displacement operator $D_{q,p} = \tau^{qp} X^q Z^p$.

* Continuous: $[\hat x, \hat p] = i\hbar$.
* Discrete: Weyl relation $ZX = \zeta_d XZ$.

*Notation:* $\zeta_d = e^{2\pi i/d}$ is the primitive $d$-th root of unity; $\tau = e^{i\pi/d}$ is the half-phase satisfying $\tau^2 = \zeta_d$. ⚠️ Many texts write $`\omega`$ for $\zeta_d$, but here $`\omega`$ is reserved exclusively for the oscillator frequency and the symplectic form.

**From energy term to gate.** The physical energy terms are quadratic, but the **elementary gates** exponentiate the *linear* field operators $\hat P$ and $\hat Q$.

| Feature | Kinetic energy $\hat P^2$ | Potential energy $\hat Q^2$ |
| --- | --- | --- |
| **CV observable** | $\hat P = \frac{i}{\sqrt2}(\hat a^\dagger - \hat a)$, derivative $\approx i(X^\dagger - X)$ | $\hat Q = \frac{1}{\sqrt2}(\hat a + \hat a^\dagger)$, real eigenvalues (location $k$) |
| **Lattice term** | Hopping / Laplacian $\approx X + X^\dagger$ (Google OTOC) | On-site potential (diagonal) |
| **Qudit gate** | **Shift** $X^a\vert{}j\rangle = \vert{}j+a \bmod d\rangle$, real off-diagonal permutation of 0s and 1s, eigenvalues powers of $\zeta_d$ | **Clock** $Z^b\vert{}k\rangle = \zeta_d^{bk}\vert{}k\rangle$, diagonal phase gradient on the unit circle; for $`d>2`$ unitary but not Hermitian |
| **Qubit gate** | **Pauli $X$**, bit flip, $\zeta_2 = -1$ | **Pauli $Z$**, phase flip, $(-1)^j$; unitary *and* Hermitian, so directly observable |
| **Matrix form** | Real, off-diagonal permutation matrix | Diagonal matrix of complex phases |
| **Gate as exponential** | $X \approx e^{-i\hat P\delta}$ | $Z \approx e^{i\hat Q\delta}$ |
| **Conjugation twist** | $X$ *represents* momentum but *generates* a position shift: $D_{q,0} \sim X^q$ | $Z$ *represents* position but *generates* a momentum kick: $D_{0,p} \sim Z^p$ |

> $`X = \mathrm{DFT}^\dagger\, Z\, \mathrm{DFT}`$ - In the momentum basis, the spatial shift operator becomes diagonal and acts identically to the clock operator.

---

#### From Heisenberg-Weyl Algebra to Quantum Gates ( Degree Ladder)

| Property | Degree 1: Displacements | Degree 2: Gaussian / Clifford | Degree $\geq 3$: Non-Gaussian / Non-Clifford |
| --- | --- | --- | --- |
| **Generator** | $\hat H = q\hat P - p\hat Q$ | $\hat Q^2 + \hat P^2$, $\hat Q^2 - \hat P^2$, $\hat Q_1\hat P_2$ | $\hat Q^3$, $\hat n^2 \sim (\hat Q^2 + \hat P^2)^2$, many-body interactions |
| **Lie algebra** | ✅ Heisenberg $\mathfrak{h}_n$, $\dim 2n+1$, $[\hat Q,\hat P]$ is central | ✅ Symplectic $\mathfrak{sp}(2n,\mathbb{R})$; combined with degree 1: semidirect product $\mathfrak{sp}(2n) \ltimes \mathfrak{h}_n$ | ❌ Does not close: cubic $`\to`$ quartic $`\to`$ quintic $\to \dots$, generating an infinite-dimensional algebra |
| **Action on phase space** | Rigid *slide* to $(q,p)$: no rotation, no volume/shape deformation | *Linear* symplectic map $U^\dagger \hat r U = S\hat r$ with $S \in \mathrm{Sp}(2n)$: rotations, shears, squeezing, entanglement | Phase space is *curved* nonlinearly; falls completely out of $\mathrm{Sp}(2n)$ |
| **Continuous variables (CV)** | Displacement operator $\hat D(\alpha) = e^{\alpha\hat a^\dagger - \alpha^*\hat a}$ | Metaplectic group $\mathrm{Mp}(2n)$: phase rotator, squeezer, beam splitter, shear | Cubic phase gate $e^{i\gamma\hat Q^3}$, Kerr non-linearity $e^{i\chi\hat n^2}$ |
| **Discrete systems** | Heisenberg-Weyl group: $D_{q,p} = \tau^{qp}X^qZ^p$; for $d=2$: Pauli group $\mathcal{P}$ | Clifford group $`\mathcal{C} = \{U : U\mathcal{P}U^\dagger = \mathcal{P}\}`$, quotient $\mathcal{C}/\mathcal{P} \cong \mathrm{Sp}(2n,\mathbb{Z}_d)$: QFT, Hadamard, $S$, C-SUM/CNOT | $T$, qudit $T_d$, Toffoli, CS. Contained in $M_d(\mathbb{C})$, but lies outside both HW and Clifford groups |
| **Hierarchy classification** | Level $\mathcal{C}_1$: forms an orthogonal operator basis of state space | Level $\mathcal{C}_2$: **Gottesman–Knill theorem** applies; efficient tracking of $2n\times 2n$ symplectic $S$ instead of $2^n$ amplitudes | Levels $\mathcal{C}_k$ for $k\geq 3$ are no longer groups; Clifford $+T$ is dense in $U(2^n)$: **universal, magic begins here** |
| **Fermionic mirror** | **None.** Degree 1 closes only under the *anti*commutator; fermionic parity superselection forbids odd Hamiltonians | **Free fermions / matchgates** (Valiant): $\mathfrak{so}(2n) \to \mathrm{Spin}(2n)$, same theorem as Gottesman–Knill with $SO$/Spin in place of $Sp$/Mp | **Degree 3 missing** due to parity constraints; classical non-simulability begins strictly at **degree 4** (e.g. Hubbard interaction $n_\uparrow n_\downarrow$) |

##### Degree 1

* The phase factor $\tau^{qp}$ in $D_{q,p} = \tau^{qp}X^qZ^p$ is required because $X$ and $Z$ do not commute; it represents an Aharonov–Bohm geometric phase effect directly on discrete phase space.
* ⚠️ **Pauli $`Y`$ is not independent:** $\sigma_y = i\sigma_x\sigma_z$ is merely the $(1,1)$ grid point on the discrete phase space. For $d=3$, none of $XZ, XZ^2, X^2Z, \dots$ is uniquely "$`Y`$"; they simply represent the generic displacement operators $D_{q,p}$ with $q,p \neq 0$.

##### Degree 2

Gaussian continuous gates and discrete Clifford gates represent the exact same algebraic generators viewed through continuous versus discrete lenses:

| CV (Gaussian) | Generator | Action | Discrete (Clifford) |
| --- | --- | --- | --- |
| **Rotator** $R(\theta) = e^{-i\theta\hat n}$ | $\hat Q^2 + \hat P^2$ | Phase rotation; at $\theta = \pi/2$ this **is** the Fourier transform | **QFT** $\vert{}j\rangle \to \frac{1}{\sqrt d}\sum_k \zeta_d^{jk}\vert{}k\rangle$, fulfilling $WXW^\dagger = Z$; **Hadamard** for $d=2$ |
| **Squeezer** $\hat S(r)$ | $\hat Q^2 - \hat P^2$ | Anisotropic scaling: $Q \to e^{-r}Q$, $P \to e^{r}P$ | — |
| **Shear** | $\hat Q^2$ | Momentum translation dependent on position: $P \to P + Q$ | **Phase gate $S$** $= \mathrm{diag}(1,i,\dots)$: maps $X \to Y \sim XZ$, imparts quadratic phase $k^2$ |
| **Beam splitter** $\hat B(\theta)$ | $\hat Q_1\hat P_2 - \hat Q_2\hat P_1$ | Passive energy-preserving mode rotation; $\theta = \pi/4$ yields 50:50 ratio | — |
| **Squeezer + beam splitter** | — | Ellipse rotated by $45°$: noise correlated across canonical axes = **entanglement** | **C-SUM / CNOT** $= e^{-i\hat Q_1\hat P_2}$: maps $\vert{}c\rangle\vert{}t\rangle \to \vert{}c\rangle\vert{}t\oplus c\rangle$ |

* **Gottesman–Knill, quantitatively:** A stabilizer state on $`n`$ qubits is uniquely specified by $`n`$ independent, commuting Pauli operators. This state is represented by an $n\times 2n$ binary tableau plus phases. The CHP simulator (Aaronson, Gottesman, PRA 2004) updates this structure in $O(n)$ time per Clifford gate and $O(n^2)$ time per measurement. The underlying tracked group is strictly finite:
```math
\vert{}\mathcal{C}_n/\mathcal{P}_n\vert{} = \vert{}\mathrm{Sp}(2n,\mathbb{Z}_2)\vert{} = 2^{n^2}\prod_{j=1}^n(4^j-1) \approx 2^{2n^2+n}
```


Contrasting this with an $\epsilon$-net covering the full unitary space $U(2^n)$ of size $\exp(\Theta(4^n\log(1/\epsilon)))$, that polynomial-to-double-exponential ratio *is* the formal simulability statement: only polynomially many classical bits are needed to characterize the entire reachable Clifford sub-manifold.

##### Degree $\geq 3$

* **Cubic phase** transforms a circular Gaussian coherent state into a non-Gaussian "banana" distribution exhibiting negative Wigner quasi-probability regions—the canonical signature of quantum non-classicality.
* **Kerr non-linearity** (quartic, degree 4) creates superposition cat states, serving as the physical foundation for continuous-variable bosonic quantum error-correcting codes.
* **$T$ gate** ($e^{-i\frac{\pi}{8}\hat Z}$) is the discrete cubic phase mod 2. Its qudit analogue $T_d\vert{}k\rangle = \zeta_d^{k^3}\vert{}k\rangle$ matches the continuous cubic potential $V(\gamma) = e^{i\gamma\hat x^3}$.
* ⚠️ The Heisenberg-Weyl operator basis remains formally valid (a $T$ gate *can* be expressed as a linear combination of Pauli operators), but the number of operator terms blows up exponentially under nested commutators/conjugations. This branching expansion is the exact mathematical locus where efficient classical simulation breaks down.
* **The Clifford hierarchy, defined:**
```math
\mathcal{C}_1 = \mathcal{P}, \quad \mathcal{C}_k = \{U : U P U^\dagger \in \mathcal{C}_{k-1}\ \forall P\in\mathcal{P}\} \quad \text{(Gottesman, Chuang, Nature 1999)}
```


The $T$ gate belongs to level $\mathcal{C}_3$. Operationally, any gate residing in $\mathcal{C}_k$ can be implemented via gate teleportation utilizing a dedicated resource state accompanied solely by feed-forward Clifford corrections drawn from level $k-1$. This inductive property is why the $T$ gate is the canonical "one step beyond" stabilizer circuits. For $k\geq 3$, the sets $\mathcal{C}_k$ are no longer groups (closure under operator products fails), mirroring the non-closing Lie brackets of degree $\geq 3$ generators.
* **Classical simulation overhead of magic:** The **stabilizer rank** $\chi$ of $\vert{}T\rangle^{\otimes t}$ is defined as the minimal number of pure stabilizer states required to express that tensor product state. Bravyi & Gosset (PRL 2016) established $\chi \lesssim 2^{0.47t}$, refined to $\approx 2^{0.396t}$ by Bravyi, Browne, Calpin, Campbell, Gosset, and Howard (Quantum 2019). The simulation runtime scale is strictly polynomial in the qubit count $`n`$ and linear/polynomial in $\chi$, meaning the simulation cost is exponential *only in the count of non-Clifford magic gates*, not in the physical qubit number.
* **Continuous-variable mirror:** Gaussian circuits are classically simulable in polynomial time (Bartlett, Sanders, Braunstein, Nemoto, PRL 2002). Classical simulation via quasiprobability sampling (Pashayan, Wallman, Bartlett, PRL 2015) scales exponentially with the total integrated Wigner negativity, which acts as the continuous non-Gaussian resource budget.
* **Magic state distillation** (Bravyi, Kitaev, PRA 2005) is the fault-tolerant inverse: consuming multiple noisy copies of magic states $\vert{}T\rangle$ via strictly transversal Clifford operations purifies them into high-fidelity target states. Consequently, the **$T$-count** serves as the universal computational cost currency for fault-tolerant quantum compilers.

**Structural Trajectory of the Framework:** The polynomial degree of a generator in the phase-space operators $\hat Q, \hat P$ (or $X, Z \pmod d$) serves as the unifying organizational principle across the theory:

* **Degree $\leq 2$** closes under the commutator algebra, preserving symplectic phase space geometry and remaining efficiently simulable classically.
* **Degree $\geq 3$** breaks algebraic closure, producing operator growth that unlocks universality, quantum magic, and genuine computational advantage.
* **Chapter 1** derives this entire ladder from the quantum harmonic oscillator and the Weyl tensor algebra.
* **Chapter 2** encounters this ladder again as the foundational exception enabling cheap Hamiltonian simulation (shadow simulation, fast-forwarding of linear/quadratic models) and identifies degree $\geq 3$ as the root driver of chaotic scrambling dynamics (out-of-time-ordered correlators, OTOCs).
* **Chapter 3** leverages this hierarchy as the tunable magic dial for learnable quantum state classes, using the degree-1 Heisenberg-Weyl displacements $D_{q,p}$ as the operator basis through which two-copy Bell measurements reconstruct unknown quantum spectra.

<br>

### Tensor Algebra $T(V)$ 

**Tensor Algebra is Basis for Exterior, Symmetric, Clifford and Weyl algebra**

*The recipe: quotient the tensor algebra by a two-sided ideal generated in degree 2. The knob: the **parity of the bilinear form** in that ideal (symmetric $`Q`$ or antisymmetric $`\omega`$), plus whether you switch its value on at all.*

```mermaid
flowchart TD
    T["T(V) = ⊕ V^⊗k<br/>free, no relations"]
    T -->|"v⊗v = 0"| L["Λ(V) exterior algebra<br/>differential forms"]
    T -->|"v⊗w − w⊗v = 0"| S["Sym(V) symmetric algebra<br/>classical observables"]
    T -->|"v⊗v = Q(v)·1"| Cl["Cl(V,Q) Clifford algebra<br/>fermions, CAR"]
    T -->|"v⊗w − w⊗v = ω(v,w)·1"| W["W(V,ω) Weyl algebra<br/>bosons, CCR"]
    Cl -.->|"gr: Chevalley, Q → 0"| L
    W -.->|"gr: PBW, ħ → 0"| S
    Cl --> F["degree 2 = Λ²V ≅ so(2n) → Spin(2n)<br/>matchgates, free fermions"]
    W --> B["degree 2 = Sym²V ≅ sp(2n) → Mp(2n)<br/>Clifford / Gaussian"]

```

*Solid arrows: quotient by the ideal on the label (upper two homogeneous, lower two inhomogeneous, i.e. quantized). Dashed arrows: the associated-graded functor, dequantization. Note the parity crossing: the symmetric form lands in the exterior square, the antisymmetric form in the symmetric square.*

|  | **Symmetric form $`Q`$** | **Antisymmetric form $`\omega`$** |
| --- | --- | --- |
| **Form off** (classical) | $\Lambda(V)$, exterior | $\mathrm{Sym}(V)$, symmetric |
| **Form on** (quantized) | $\mathrm{Cl}(V,Q)$, **fermions**, CAR | $W(V,\omega)$, **bosons**, CCR |


**Step 0, the source.** $T(V) = \bigoplus_k V^{\otimes k}$: 
* associative, non-commutative, no relations. Every relation below is introduced by hand as the generator of an ideal; 
* all four algebras are $T(V)/I$ and differ only in the ideal $I$.

**Step 1, homogeneous ideal (degree 2 $= 0$).**
* $\Lambda(V) = T(V)/\langle v\otimes v\rangle \implies v\wedge w = -w\wedge v$: differential forms, cohomology.
* $\mathrm{Sym}(V) = T(V)/\langle v\otimes w - w\otimes v\rangle \implies vw = wv$: polynomials, classical observables on phase space.
* The $\mathbb{Z}$-grading survives; these correspond to $\mathrm{Cl}$ with $Q=0$ and $W$ with $\omega = 0$.


**Step 2, switch the form on (the right-hand side becomes a number: this is quantization).**
* $\mathrm{Cl}(V,Q) = T(V)/\langle v\otimes v - Q(v)\mathbf{1}\rangle \implies vw + wv = 2Q(v,w)$: a vector squares to its length.
* $W(V,\omega) = T(V)/\langle v\otimes w - w\otimes v - \omega(v,w)\mathbf{1}\rangle \implies [v,w] = \omega(v,w)$: the commutator is a number, $[\hat q,\hat p] = i\hbar\mathbf{1}$.
* ⚠️ The ideal is now **inhomogeneous** (degree 2 mixed with degree 0), so the $\mathbb{Z}$-grading collapses to a **filtration**: *grading $`\to`$ filtration is what quantization means algebraically.*
* ⚠️ The deformation changes the product, not the space: $\Lambda(\mathbb{R}^2)$ and $\mathrm{Cl}(\mathbb{R}^2,Q)$ share the vector space basis $`\{1, e_1, e_2, e_1e_2\}`$ with different multiplication tables; PBW monomials $\hat q^a\hat p^b$ form a common basis of both $\mathrm{Sym}$ and $W$.
* **⚠️ The twist: parity flips between input and output.**
* A symmetric input $g$ builds $\mathrm{Cl}(V,g)$, whose degree-2 part is the **exterior** square $\mathfrak{so} \cong \Lambda^2 V$ (via $\frac14[e_i,e_j]$) $`\to`$ Spin $`\to`$ **fermions**.
* An antisymmetric input $`\omega`$ builds $W(V,\omega)$, whose degree-2 part is the **symmetric** square $\mathfrak{sp} \cong \mathrm{Sym}^2 V$ (via $`\frac12\{\hat r_i,\hat r_j\}`$) $`\to`$ metaplectic $`\to`$ **bosons**.
* The labels cross. In supersymmetry both unify into one single construction on $\mathbb{Z}_2$-graded spaces.


**Step 3, the way back ($\mathrm{gr}$).** 
* Dequantization keeps only the top-degree part of each relation: $`\mathrm{gr}\,\mathrm{Cl}(V,Q) \cong \Lambda(V)`$ (**Chevalley**, $Q \to 0$) and $`\mathrm{gr}\,W(V,\omega) \cong \mathrm{Sym}(V)`$ (**PBW**, $\hbar \to 0$). ⚠️ These are **one theorem**: super-PBW on $\mathbb{Z}_2$-graded spaces *is* Chevalley.
* **Second road, the Lie route.** $U(\mathfrak{g}) = T(\mathfrak{g})/\langle x\otimes y - y\otimes x - [x,y]\rangle$ has the identical shape of ideal (hence "PBW deformation").
* Bosonic: $A_n = U(\mathfrak{h}_n)/(Z-1)$, where the universal enveloping algebra $U(\mathfrak{h}_n)$ supplies the products that the Lie algebra $\mathfrak{h}_n$ alone lacks.
* Fermionic: $\mathrm{Cl}(V,Q) = U(\mathfrak{h}^{\mathrm{super}})/(Z-1)$ with anticommutator bracket.



##### What each side becomes

| Property | Fermions: $\mathrm{Cl}(V,Q)$ | Bosons: $W(V,\omega)$ |
| --- | --- | --- |
| **Statistics** | CAR $`\{a_i,a_j^\dagger\} = \delta_{ij}`$, $`\{\gamma_\mu,\gamma_\nu\} = 2g_{\mu\nu}`$ | CCR $[a_i,a_j^\dagger] = \delta_{ij}$, $[\hat x,\hat p] = i\hbar$ |
| **Size** | $\dim = 2^n$, the relation truncates powers | $\dim = \infty$, nothing truncates. **No finite-dimensional rep**: $\mathrm{tr}[A,B] = 0$ but $\mathrm{tr}(i\hbar\mathbf{1}) \neq 0$ |
| **Uniqueness** | Unique spinor module | **Stone–von Neumann** |
| **Canonical degree-2 square** | Dirac $\nabla = d + \delta$, $\nabla^2 = \Delta$ | Oscillator $H = \frac12(\hat p^2 + \hat q^2)$; Moyal star product |
| **Symmetry tower** | $\mathrm{O}(V,g) \supset \mathfrak{so}(n)$, $\dim \frac{n(n-1)}{2}$, Cartan types $B_n/D_n$, cover $\mathrm{Spin}(n)$ | $\mathrm{Sp}(2n) \supset \mathfrak{sp}(2n)$, $\dim n(2n+1)$, Cartan type $C_n$, cover $\mathrm{Mp}(2n)$ |
| **QC bridge** | Matchgates / free fermions = rotor in $\mathrm{Spin}(2n)$; non-free from **degree 4** | Clifford / Gaussian = symplectic action; magic from **degree 3** |

⚠️ The QC bridge is **structurally one theorem**, once for $SO$/Spin, once for $Sp$/Mp. The size asymmetry is the sharpest physical difference: bosons require unbounded operators on infinite-dimensional Hilbert spaces, while fermions act naturally on a finite spinor space.

---

#### From Weyl Algebra to Heisenberg-Weyl: How Bosons Reach Actual Qubits / Qudits

| Level | Continuous | Discrete |
| --- | --- | --- |
| **Additive** (Lie bracket) | Weyl algebra $A_n = W(V,\omega)$: all polynomials in $\hat q,\hat p$, home of Hamiltonians and the degree filter | ⚠️ **Does not exist.** Trace argument: $\mathrm{Tr}([\hat q,\hat p]) = 0$ but $\mathrm{Tr}(i\hbar\mathbf{1}) = i\hbar d \neq 0$ |
| **Multiplicative** (operator product) | Heisenberg group $H_n$ / CCR $C^*$-algebra: $W(z)W(z') = e^{-\frac{i}{2}\omega(z,z')}W(z+z')$, linked to $A_n$ by Stone–von Neumann | HW algebra $M_d(\mathbb{C}) \cong \mathbb{C}_\omega[\mathbb{Z}_d \times \mathbb{Z}_d]$, spanned by the $d^2$ matrices $X^qZ^p$ |

**Why exponentiating rescues what the additive box forbids: trace vs. determinant.** At the group level the test uses $\det$: $\det(ZXZ^{-1}X^{-1}) = 1$ must equal $\det(\zeta_d\mathbf{1}) = \zeta_d^d = 1$ ✓. The additive constraint is *unsatisfiable* in finite dimensions, but the multiplicative one is *automatically satisfied*. That is why the discrete Weyl relation $ZX = \zeta_d XZ$ exists in exact $d\times d$ complex matrices, providing the complete pathway from the continuous Weyl algebra to the discrete Heisenberg-Weyl algebra.

**Moving between the boxes.**

* **Up:** $\mathfrak{h}_n \xrightarrow{\exp} H_n$ (BCH series terminates cleanly because $[\hat Q,\hat P]$ is central; the additive Lie bracket maps into a multiplicative phase factor).
* **Down:** Differentiate at the identity along one-parameter subgroups.
* **Sideways:** $G \xrightarrow{\mathrm{span}} M_d(\mathbb{C})$ via the group algebra (linear span of group elements, ⚠️ *not* by $\exp$; algebras themselves are not exponentiated).
* **Limit:** The asymptotic regime $d \to \infty$ turns $ZX = \zeta_d XZ$ continuously back into $[\hat Q,\hat P] = i\hbar\mathbf{1}$.

**Stone–von Neumann, stated.** Every irreducible, strongly continuous unitary representation of the Weyl relations

$$W(z)W(z') = e^{-\frac i2\omega(z,z')}W(z+z')$$

for *finitely many* degrees of freedom is unitarily equivalent to the Schrödinger representation on $L^2(\mathbb{R}^n)$.

*Consequences:*

1. Position and momentum representations describe identical physics in different coordinates, with the Fourier transform serving as the intertwining operator.
2. The discrete analogue is unique in precisely the same way: $M_d(\mathbb{C})$ has, up to unitary equivalence, exactly one irreducible representation of $ZX = \zeta_d XZ$, explaining why "the" qudit clock and shift operators are canonical.
3. ⚠️ The theorem **fails** for infinitely many degrees of freedom (quantum field theory, thermodynamic limit): inequivalent representations exist, which is Haag's theorem and the structural origin of superselection sectors. Finite-$`n`$ uniqueness is what makes phase-space methods and the operator degree ladder unambiguous.

---

### Symplectic Form

A **form** evaluates to a scalar:

* $0$-form = scalar function
* $1$-form = covector field
* $2$-form = bilinear form

Differential forms $\Omega^k(M) = \Gamma(\Lambda^k T^*M)$ integrate intrinsically over oriented submanifolds without coordinate choices ($1$-forms over curves yield work; $2$-forms over surfaces yield flux).

The **symplectic form $`\omega`$** is a differential $2$-form defined by three properties:

* **Alternating:** Pointwise antisymmetric, $\omega(u,v) = -\omega(v,u)$.
* **Closed:** $d\omega = 0$, guaranteeing the absence of local curvature invariants (Darboux's theorem).
* **Non-degenerate:** Forces an **even dimension** $2n$ (coordinates naturally pair into positions $q_i$ and momenta $p_i$) and produces the nowhere-vanishing **Liouville volume form** $\omega^n$.

**Two consequences used in the [quantum learning notes](https://deltorobarba.github.io/science/).**

* **Darboux's Theorem:** Locally, every symplectic manifold is symplectomorphic to standard phase space $(\mathbb{R}^{2n}, \sum_{i=1}^n dq_i \wedge dp_i)$. Because there are no local invariants, the only geometric structure a Gaussian/Clifford operation can preserve is $`\omega`$ itself. This is why $\mathrm{Sp}(2n)$ (continuous) and $\mathrm{Sp}(2n,\mathbb{Z}_d)$ (discrete, with symplectic product $\omega(z,z') = qp' - q'p \pmod d$) act as the universal structure groups of degree 2.
* **Liouville's Theorem:** The phase-space volume $\omega^n$ is invariant under Hamiltonian flows, and its quantum shadow is unitarity. The Wigner function utilized in quantum learning is precisely a quasi-probability density evaluated against this Liouville volume form, and Hudson's theorem dictates that dynamics generated by Hamiltonians of degree $\leq 2$ preserve the non-negativity of Gaussian Wigner distributions.

## Quantum Simulation

### Differentiation: Model, Computation and Type

> Every simulation technique in chemistry and physics sits on three axes: **Model** (classical vs. quantum), **Type** (static vs. dynamic), and **Computing** (classical vs. quantum). *Quantum dynamics* is the cell "quantum model, dynamic type", and its hard core is propagating $\vert{}\psi(t)\rangle = e^{-iHt}\vert{}\psi(0)\rangle$ in a $2^n$-dimensional Hilbert space. Static problems are **optimized** (variational principle); dynamic problems must be **propagated** (no forward theorem). On a quantum computer, propagation follows one of three structural strategies: decompose *time* (Trotter), transform the *spectrum* (Qubitization / QSVT), or shrink the *space* (Shadow Simulation).

* **Model:** Classical models ignore electrons and treat atoms as spheres connected by springs (empirical force fields). Quantum models explicitly bring electrons, orbitals, and many-body correlation into play.
* **Type:** Static (ground state, eigenvalue problem $\hat H\vert{}\psi\rangle = E\vert{}\psi\rangle$) vs. dynamic (time evolution $`i\hbar\,\partial_t\Psi = \hat H\Psi`$).
* **Computing:** Classical hardware vs. quantum hardware.

| Model / Computing | **Static** (state, ground state) | **Dynamic** (time evolution) |
| --- | --- | --- |
| **Classical / Classical** | **Docking, energy minimization:** geometric fitting (AutoDock, Rosetta) | **Molecular dynamics:** $F = ma$, atoms as classical mass points with empirical force fields (GROMACS, NAMD, AMBER) |
| **Quantum / Classical** | **HF, DFT, Post-HF:** $\hat H\vert{}\psi\rangle = E\vert{}\psi\rangle$. HF ignores correlation, DFT approximates it via electron density $\rho$, Post-HF (CC, CI) is exact but scales exponentially in electron number $`N`$ | **TD-DFT:** excitations, spectra, fluorescence. Exact propagation $e^{-i\hat Ht/\hbar}\vert{}\Psi(0)\rangle$ scales exponentially in $`N`$ |
| **Quantum / Quantum** | **VQE (NISQ):** correlation energy via parametrized entanglement, optimization condition $\delta\langle H\rangle = 0$ | **Hamiltonian simulation:** coherent unitary exponentiation in a $2^n$-dimensional Hilbert space via Trotter, Qubitization/QSVT, or Shadow Simulation |

*Perspective, not part of quantum dynamics:* Quantum computers used for *classical* dynamics—such as solving the Navier–Stokes equations via the HHL algorithm for linear systems, or weather forecasting on a fine 100 m grid. Same quantum hardware, entirely different computational application.

#### Static vs. Dynamic

* **Static = Energy optimization.** If $\psi$ is an eigenstate of $\hat H$, time evolution is strictly stationary: $\Psi(t) = \psi e^{-iEt/\hbar}$, and the probability density $\vert{}\Psi(t)\vert{}^2$ remains constant over time. Finding binding energies reduces to searching for global minima across an energy landscape using the Rayleigh–Ritz variational principle or NISQ-era VQE.
* **Dynamic = Propagation.** Dynamical problems feature no general variational principle and no forward-in-time shortcut theorem. Simulating non-equilibrium chemical reaction dynamics, bond breaking during atomic collisions, non-adiabatic electronic excitations, and quantum chaotic scrambling cannot be framed as an optimization task; states must be explicitly propagated under $e^{-iHt}$.
* **Fundamental Axiom.** In static problems, the quantum computer merely *stores* and updates state information. In full dynamical evolution, it stores nothing: **it *is* the physical Hilbert space.**

#### Unitaries vs Channels

Der Begriff „Unitaries“ meint zwar dynamische Transformationen bzw. Prozesse im Gegensatz zu statischen Zuständen (States), bezieht sich aber ausschließlich auf geschlossene Quantensysteme (closed quantum dynamics).

Hier ist die genaue begriffliche Einordnung:

⚬ Unitaries (U): Stehen für unitäre Operatoren (U^\dagger U = I). Sie beschreiben die reversible, informationserhaltende Zeitentwicklung eines perfekt isolierten (geschlossenen) Systems:
  
  $$\rho \mapsto U \rho U^\dagger \quad \text{bzw.} \quad \vert{}\psi\rangle \mapsto U \vert{}\psi\rangle$$
  
  Typische Beispiele sind Quantengatter (wie Hadamard, CNOT) oder die kontinuierliche Schrödinger-Dynamik unter einem hermiteschen Hamiltonoperator (U = e^{-iHt/\hbar}).
⚬ Open Quantum Dynamics (Offene Systeme): Wenn ein System mit einer Umgebung wechselwirkt (Rauschen, Dekohärenz, Dissipation), ist der Prozess im Allgemeinen nicht mehr unitär. Man spricht hier nicht von Unitaries, sondern von:
  ⚬ Quantum Channels (vollständig positive, spurerhaltende Abbildungen bzw. CPTP maps)
  ⚬ Dynamical Maps / Superoperatoren
  ⚬ Kraus-Operatoren (\rho \mapsto \sum_k K_k \rho K_k^\dagger)
  ⚬ Lindblad-Mastergleichungen für kontinuierliche dissipative Dynamik

Das Begriffspaar im Überblick

Dimension	Geschlossene Systeme (Closed)	Offene Systeme (Open)
Statisch	Reine Zustände (Ket \vert{}\psi\rangle) / Dichtematrizen \rho	Gemischte Zustände / Dichtematrizen \rho
Dynamisch	Unitaries (U)	Quantum Channels / CPTP Maps (\mathcal{E})

Wenn man die Dichotomie zwischen „Zuständen“ und „Prozessen“ allgemein ausdrücken möchte (einschließlich Rauschen und offener Systeme), spricht man meist von States vs. Channels (oder States vs. Operations). Sagt jemand explizit States vs. Unitaries, wird die Welt der fehlerfreien, idealisierten bzw. streng geschlossenen Quantengatter und -zeitentwicklungen fokussiert.

---

### Static Quantum Chemistry: The Approximation Stack

**Why only tiny systems are solvable analytically.** The Schrödinger equation is analytically solvable only for the one-electron hydrogen atom. Introducing a second electron adds Coulomb repulsion, producing a non-integrable quantum three-body problem. Every electronic structure method is an approximation stack built upon foundational simplifications:

1. **Born–Oppenheimer Approximation:** Nuclei are treated as clamped on electronic timescales due to large mass differences, defining the classical potential energy surface (PES).
2. **Rayleigh–Ritz Variational Principle:** Minimizing the energy expectation value $\langle\psi\vert{}H\vert{}\psi\rangle$ yields upper bounds on the true ground-state energy.
3. **Correlation Energy:** The remaining central difficulty of modern quantum chemistry:

| Method | Correlation Treatment | Computational Cost |
| --- | --- | --- |
| **Hartree–Fock (HF)** | Mean-field approximation, neglects electron correlation entirely | Cheap: polynomial scaling ($O(N^4)$ down to $`O(N^3)`$) |
| **Density Functional Theory (DFT)** | Approximated via exchange-correlation functionals of the electron density $\rho$ (the exact universal functional is unknown and must be approximated) | Cheap: favorable polynomial scaling |
| **Post-HF (Coupled Cluster, CI)** | Systematically exact recovery of electronic correlation | Exponential scaling in electron number $`N`$; restricted to small molecular systems |
| **Variational Quantum Eigensolver (VQE)** | Captured directly on hardware through multi-qubit entanglement | Central NISQ method targeting larger molecules where classical Post-HF methods fail |

* **Chemical Model Frameworks:** Valence Bond Theory (orbital hybridization, localized electron-pair bonds) vs. Molecular Orbital (MO) Theory (spatial delocalization, HOMO/LUMO frontiers, Linear Combination of Atomic Orbitals / LCAO). Electron spin ($m_s = \pm\frac12$) does not emerge from the non-relativistic Schrödinger equation (which yields only quantum numbers $n, l, m_l$), but arises from unifying quantum mechanics with special relativity via the Dirac equation (1928).
* **Numbers and the Fault-Tolerant Counterpart:**
* **Chemical Accuracy** is defined as $1\text{ kcal/mol} \approx 1.6\text{ mHa} \approx 43\text{ meV}$, the energetic precision required to predict room-temperature chemical reaction rates to within one order of magnitude. This threshold fixes the target error $\epsilon$ in all quantum resource estimates.
* **Classical Scaling Limits:** Full Configuration Interaction (FCI) is numerically exact within a chosen basis set but scales combinatorially as $\binom{M}{N}$ in spin-orbitals $M$ and electrons $`N`$. Coupled Cluster with single, double, and perturbative triple excitations—$`\text{CCSD(T)}`$, the classical "gold standard"—scales as $O(N^7)$ and breaks down in strongly correlated, multi-reference systems (e.g., transition metal complexes, bond-breaking pathways), precisely the regime targeted for quantum advantage.
* **Fault-Tolerant QPE:** The fault-tolerant successor to VQE is **Quantum Phase Estimation (QPE)** applied to a block-encoded Hamiltonian $H$. By preparing an initial guiding state with non-negligible ground-state overlap, $E_0$ is read out as an eigenvalue phase with Heisenberg-limited precision in oracle queries.
* **FeMoco Resource Estimates:** Benchmark quantum resource studies focus on the catalytic iron-molybdenum cofactor of nitrogenase (FeMoco). Initial estimates by Reiher et al. (PNAS 2017) and tensor hypercontraction implementations by Lee et al. (PRX Quantum 2021) established requirements on the order of $10^6$ physical qubits and multiple days of runtime. These estimates have dropped by orders of magnitude primarily through advanced Hamiltonian representations with reduced 1-norms $\lambda$, rather than through relaxed hardware assumptions.
* ⚠️ **The Overlap Bottleneck:** If the overlap between the classically prepared guiding state $\vert{}\phi\rangle$ and the true ground state $\vert{}\psi_0\rangle$ is exponentially suppressed ($\lvert\langle\phi\vert{}\psi_0\rangle\rvert^2 \leq 2^{-\Omega(n)}$), QPE requires exponentially many repetitions, eliminating quantum speedup over classical heuristics (the *guided local Hamiltonian* problem).



---

### Dynamic Simulation on a Quantum Computer

**The Problem.** In nature, a physical system evolves under all governing Hamiltonian terms simultaneously. In contrast, quantum computing hardware executes discrete elementary quantum gates sequentially. Because non-commuting Hamiltonian terms satisfy $[A, B] \neq 0$, the Lie product formula does not factorize trivially:

$$e^{-i(A+B)t} \neq e^{-iAt}e^{-iBt}$$

| Strategy | Method | Decomposed Entity | Target Hardware Regime |
| --- | --- | --- | --- |
| **Decompose Time** | Trotter–Suzuki product formulas, qDRIFT | Physical duration $t$ discretized into $r$ time slices | NISQ (shallow depth, zero ancillas) |
| **Transform Spectrum** | Qubitization / Quantum Singular Value Transformation (QSVT) | Continuous energy spectrum mapped into discrete rotation angles: $E_k = \lambda\cos\theta_k$ | Fault-Tolerant (ancilla-assisted block encodings) |
| **Shrink Space** | Shadow Simulation | Full state space ($2^n$ complex amplitudes) projected into $M$ operator expectation values | Both NISQ and Fault-Tolerant regimes |

```mermaid
flowchart TD
    H["Task: implement e^{-iHt} to precision ε"] --> A{"Do H and an operator set S<br/>close a small Lie algebra?"}
    A -->|"yes: free fermions, free bosons,<br/>Pauli/Clifford sets"| SH["Shadow simulation<br/>evolve M expectation values, dim H_S ≪ 2^n"]
    A -->|"no"| R{"Hardware regime?"}
    R -->|"NISQ: shallow, no ancillas"| TR["Trotter–Suzuki or qDRIFT<br/>decompose time, error ∝ commutators"]
    R -->|"fault-tolerant: ancillas + oracles"| BE["LCU block encoding<br/>PREPARE, SELECT, 1-norm λ"]
    BE --> QB["Qubitization walk<br/>E_k = λ cos θ_k"]
    QB --> QS["QSP / QSVT polynomial in θ<br/>cost O(λt + log 1/ε)"]

```

*The three strategies as an operational decision tree: shrink the state space if algebraic closure permits; otherwise, choose between slicing time or mapping the spectrum based on available hardware fault tolerance.*

---

### Trotterization

$$e^{-iHt} \approx \Big(\prod_j e^{-iH_j t/r}\Big)^r$$

* **Mechanism:** Decompose $H = \sum_{j=1}^L H_j$ into simple, individually exponentiable terms (e.g., local Pauli strings) and interleave them across $r$ small time slices.
* **Commutator Scaling:** Operator non-commutativity sets the error budget. First-order Trotterization leaves an algorithmic error of $\mathcal{O}(t^2/r)$, bounded by the sum of pairwise operator commutators:
```math
\epsilon \le \frac{t^2}{2r} \sum_{j < k} \Vert{}[H_j, H_k]\Vert{}
```


Higher-order symmetric Suzuki formulas systematically eliminate lower-order error terms at the cost of increasing circuit depth.
* **Hardware Profile:** Structurally native to hardware; requires zero ancilla qubits and no coherent oracle circuits. Its primary computational limitation is a polynomial error scaling in $1/\epsilon$.
* **Commutator Bounds and Randomized Product Formulas:**
* **Nested Commutator Scaling:** Childs, Su, Tran, Wiebe, and Zhu (PRX 2021) demonstrated that the asymptotic error of a $p$-th order formula is rigorously bounded by nested commutators of the form $\sum \Vert{}[H_{j_{p+1}}, \dots, [H_{j_2}, H_{j_1}]]\Vert{}$. For geometrically local lattice Hamiltonians, this bound scales as $O(n)$ with system size rather than the loose, naive scaling in the number of terms $L^{p+1}$. This explains why high-order product formulas remain competitive in realistic gate-level resource benchmarks (Childs, Maslov, Nam, Ross, Su, PNAS 2018).
* **Randomized Compilation via qDRIFT:** Campbell (PRL 2019) introduced quantum Stochastic Drift Protocol (qDRIFT), which avoids deterministic term orderings by stochastically sampling individual terms $H_j$ with probability $p_j = \alpha_j / \lambda$ (where $\lambda = \sum_j \alpha_j$). The gate count scales as $O(\lambda^2 t^2 / \epsilon)$, completely independent of the total term count $L$ and free from operator commutators, though at the expense of an $\epsilon^{-1}$ error overhead.
* **Application Rule of Thumb:** Hamiltonians with numerous small-norm interaction terms and modest precision targets favor qDRIFT; systems composed of fewer, dominant terms or demanding high precision favor high-order Suzuki product formulas.

---

### Qubitization

* Qubitization: Walk Through the Eigenvalues
* **Linear Combinations of Unitaries (LCU) & Block Encoding:** Express the system Hamiltonian as a linear combination of unitaries:
$$H = \sum_{l=1}^L \alpha_l U_l \quad \text{with 1-norm } \lambda = \sum_{l=1}^L \vert{}\alpha_l\vert{}$$


Using coherent $\text{PREPARE}$ and $`\text{SELECT}`$ subroutines, embed the normalized Hamiltonian operator $H/\lambda$ as the upper-left diagonal block of an expanded unitary matrix $U_H$:
```math
U_H = \begin{pmatrix} H/\lambda & \cdot \\ \cdot & \cdot \end{pmatrix}
```


* **Quantum Walk: Energy to Angle:** Introducing a state reflection operator $R = 2\vert{}\bar{0}\rangle\langle\bar{0}\vert{} - \mathbb{1}$ transforms the composite quantum walk operator $W = R \cdot U_H$ into an exact 2D planar rotation on invariant subspaces spanned by the eigenstates of $H$, possessing eigenvalues $e^{\pm i \arccos(E_k / \lambda)}$:
$$E_k = \lambda\cos\theta_k$$


Scalar energies are translated into geometric rotation angles. Time evolution is synthesized not by slicing time, but by executing an optimal polynomial transformation of these phases via **Quantum Signal Processing (QSP)** and the **Quantum Singular Value Transformation (QSVT)** using Jacobi–Anger and Chebyshev expansions (Low & Chuang, PRL 2017, Quantum 2019; Gilyén, Su, Low, & Wiebe, STOC 2019).
* **Performance Profile:** Achieves an asymptotically optimal query complexity of:
$$\mathcal{O}\left(\lambda t + \log(1/\epsilon)\right)$$


The physical trade-off involves coherent ancilla registers, multi-qubit controlled oracle calls, and an algorithmic dependency on the Hamiltonian 1-norm $\lambda$.
* **Scrambling & OTOC Diagnostics:** By inverting the quantum walk sequence (reversing the reflection operators and oracle circuits), operator scrambling and out-of-time-ordered correlators (OTOCs) can be measured directly via relative phase shifts on the ancilla register.
* **Fundamental Query Bounds & Fast-Forwarding:** The linear query dependence on time $t$ is tight and matches the fundamental **no-fast-forwarding theorem** for generic quantum Hamiltonians (Berry, Ahokas, Cleve, Sanders 2007; Atia & Aharonov, Nat. Commun. 2017). The additive $\log(1/\epsilon)$ term reflects the optimal polynomial degree required to approximate trigonometric time evolution functions.
* ⚠️ **Fast-Forwarding Exceptions:** Sub-linear or constant-time fast-forwarding ($t \ll \Vert{}H\Vert{}t$) remains physically possible for specific structured Hamiltonians (e.g., mutually commuting terms, non-interacting quadratic fermionic systems belonging to degree $\leq 2$ of the operator ladder)—the exact algebraic exception enabling shadow simulation.

---

### Shadow Simulation: Shrink the Space

Shadow Simulation: Shrink the Space. Proposed by Somma et al. (2024/2025), shadow simulation circumvents the exponential $2^n$-dimensional Hilbert space by tracking the dynamics of an observable subspace. It maps the evolution of $\vert{}\psi(t)\rangle$ into a compressed **shadow quantum state** whose amplitudes correspond to the expectation values of an operator set $`S = \{O_1, \dots, O_M\}`$ (e.g., 1-RDMs, 2-RDMs, or structured Pauli strings):

```math
\vert{}\rho(t);S\rangle = \frac{1}{\sqrt A}\sum_{m=1}^M \langle O_m(t)\rangle\,\vert{}m\rangle
```

* **Algebraic Invariance (Theorem 1):** If the Hamiltonian $H$ and the operator basis $S$ satisfy a closed Lie algebra commutator relation:
$$[H, O_m] = -\sum_{m'=1}^M h_{mm'} O_{m'}$$


the shadow state **itself satisfies an exact effective Schrödinger equation**:
$$\frac{d}{dt}\vert{}\rho(t);S\rangle = -iH_S\vert{}\rho(t);S\rangle$$


where $H_S$ is an effective $M \times M$ matrix governed by the structure coefficients $h_{mm'}$.
* **Domains of Exact Closure:** This condition holds rigorously for systems generated by degree-2 operators on the canonical operator ladder:

| System | Lie Algebra | Operator Basis $S$ | Complexity Gain |
| --- | --- | --- | --- |
| **Free Fermions** | $\mathfrak{so}(2n)$ | Majorana quadratic pairs $c_j c_k$ | $N = 2^r$ physical modes simulated using only $\mathcal{O}(\log N)$ qubits |
| **Free Bosons** | $\mathfrak{sp}(2n)$ | Canonical variables $\hat P_j, \hat Q_j$ | Simulates $2^n$ coupled harmonic oscillators (generalizing Babbush et al.; BQP-complete dynamics) |
| **Qubit Systems** | Pauli strings / Clifford hierarchy | Operator pairs $P_{ij}$ | Direct state realization $\vert{}\rho;S\rangle = V_S(\vert{}\psi\rangle\otimes\vert{}\bar\psi\rangle)$ achieved via transversal Bell-basis rotations |

* **Computational Efficiency:** The effective matrix $H_S$ is propagated using QSP block-encoding techniques. Because $\dim H_S = M \ll 2^n$ and $H_S$ is typically highly sparse, its block encoding is exponentially more compact than that of the original physical Hamiltonian $H$.
* **Heisenberg Picture Representation:** Two-time correlation functions $\langle O_1(t) O_2(t')\rangle$ are directly mapped to quantum amplitude tensors (Theorem 2). A time-dependent operator $Z(t) = \sum_m z_m(t) O_m$ is encoded as a state vector $\vert{}Z(t)\rangle \propto \sum_m z_m(t)\vert{}m\rangle$. Evaluating Hamming-weight projections $\langle Z(t)\vert{}W\vert{}Z(t)\rangle$ yields operator spreading dynamics and **OTOC scrambling rates** without ever constructing the underlying $2^n$-dimensional state vector.

---

### Open Quantum Systems: Non-Unitary Dynamics

Coupling a quantum system to an unobserved thermal environment or measurement apparatus introduces energy dissipation and phase decoherence. The state evolution on the primary Hilbert space $\mathcal{H}_S$ ceases to be unitary and is described by a completely positive trace-preserving (**CPTP**) dynamical map ($\mathcal{E} \otimes \mathcal{I}_n \geq 0$).

Under the standard Born–Markov approximations (weak coupling, memoryless bath), the open dynamics obey the **Gorini–Kossakowski–Sudarshan–Lindblad (GKSL) master equation** (1976):

```math
\frac{d\rho}{dt} = -i[H,\rho] + \sum_k \gamma_k\Big(L_k\rho L_k^\dagger - \tfrac12\{L_k^\dagger L_k,\rho\}\Big)
```

* **Coherent vs. Dissipative Terms:** The first term accounts for unitary evolution generated by $H$. The second term captures environmental dissipation via **Lindblad jump operators** $L_k$, which model processes such as spontaneous photon emission and spin flips ($T_1$ energy relaxation / amplitude damping) as well as elastic scattering and dephasing ($T_2$ phase damping).
* **Mathematical Structure:** The GKSL equation is the most general generator of a Markovian CPTP dynamical semigroup. Globally, any CPTP map admits an operator-sum **Kraus representation**:
$$\mathcal{E}(\rho) = \sum_k K_k\rho K_k^\dagger \quad \text{with} \quad \sum_k K_k^\dagger K_k = \mathbb{1}$$


The **Stinespring dilation theorem** embeds this non-unitary process into a higher-dimensional unitary evolution acting jointly across the system and an auxiliary environment.
* **Hardware Implementations:**
* **NISQ:** Simulated via the Monte-Carlo Wavefunction (MCWF) / quantum trajectory formalism, implementing continuous coherent drive punctuated by stochastic wavefunction collapses and mid-circuit ancilla resets.
* **Fault-Tolerant:** Implemented by block-encoding non-unitary Kraus and jump operators into unitary matrices using LCU methods or Stinespring ancilla registers. Cleve and Wang (ICALP 2017) demonstrated that Lindblad dynamics can be simulated fault-tolerantly in time:
```math
\mathcal{O}\big(t\,\mathrm{polylog}(t/\epsilon)\big)
```


matching the optimal time scaling of closed-system Hamiltonian simulation up to poly-logarithmic factors.


* ⚠️ **Non-Markovian Dynamics:** Environments exhibiting memory effects, structured environmental spectral densities, or strong system-bath entanglement fall completely outside the Lindblad framework and represent a primary frontier for quantum simulation algorithms.
<br><br>

### Chaos, Scrambling and OTOCs

> A local operator under chaotic dynamics in the Heisenberg picture, $W(t) = e^{iHt}We^{-iHt}$, grows in three directions, each with its own metric and its own bound: **rate** $\lambda_L$ (time), **reach** $v_B$ (space), and **depth** $K(t)$ (operator space). Without the Schrödinger solution $e^{-iHt}$ there is no $`W(t)`$ and no OTOC: chaos diagnostics *are* quantum dynamics.

**Model system.** Mixed-field Ising model:

$$H = \sum_i Z_iZ_{i+1} + h_x\sum_i X_i + h_z\sum_i Z_i$$

The longitudinal field $h_z$ breaks integrability:

* $h_z = 0$: Integrable; yields Poincaré recurrence, ballistic echoes, and non-scrambling dynamics.
* $h_z \neq 0$ (e.g., $h_z = 0.5$): Non-integrable and chaotic; produces diffusive operator scrambling.
* **Simulation setup:** The OTOC of a local $Z$ probe on every site against an $X$ butterfly perturbation on the first site on a Trotterized spin chain directly contrasts ballistic spread ($h_z = 0$) against chaotic, diffusive scrambling ($h_z = 0.5$).

---

##### Object: OTOC as a Four-Point Function

```math
C(t) = \big\langle[W(t),V(0)]^\dagger[W(t),V(0)]\big\rangle = 2\big(1 - \mathrm{Re}\,F(t)\big), \qquad F(t) = \langle W^\dagger(t)V^\dagger W(t)V\rangle
```

* **Physical meaning:** Measures how strongly two operators that initially commute at $t=0$ ($[W(0), V(0)] = 0$) **fail to commute** after time evolution. Scrambling corresponds to the decay $F(t) \to 0$.
* **Mechanism:** $`W(t)`$ starts as a strictly local observable, expands under the Heisenberg dynamics into an extensive, non-local superposition of Pauli strings, reaches the spatial support of $`V`$, and causes the commutator norm to lift off zero.
* **Why out-of-time-order:** The operator sequence traverses the contour $t \to 0 \to t \to 0$. Standard time-ordered two-point functions decay on the thermalization timescale $t_{\text{therm}}$ and are blind to information scrambling.
* **Measurement via Loschmidt Echo:**
1. Forward propagation under $e^{-iHt}$.
2. Butterfly perturbation $`V`$ (e.g., a local $X$ gate).
3. Backward propagation under $e^{+iHt}$.
4. Projective overlap measurement with probe observable $W$.

```mermaid
flowchart LR
    P["prepare ρ"] --> F["forward<br/>e^{-iHt}"] --> V["butterfly<br/>V = local X"] --> B["backward<br/>e^{+iHt}"] --> W["measure probe W<br/>F(t) = ⟨W†(t) V† W(t) V⟩"]

```

*The Loschmidt-echo protocol for an OTOC: only the non-commutativity of $`W(t)`$ and $`V`$ survives the forward-backward unitary cancellation. On fault-tolerant hardware, "backward" is implemented directly as the exact inverse quantum walk (reversing reflection and oracle phases), exploiting the fact that time evolution is synthesized as an angle.*

* **Experimental Verifications & The 2025 Hardware Milestone:** Verified across NMR platforms, trapped-ion processors, and superconducting circuits. In Google's "Quantum Echoes" (Abanin et al., *Nature*, October 2025), a second-order OTOC was measured on the 65-qubit Willow processor, demonstrating a $`\sim\!13{,}000\times`$ speedup over state-of-the-art classical tensor network and HPC simulations on the Frontier supercomputer. This was framed as the first *verifiable* quantum advantage: unlike random circuit cross-entropy benchmarking, the OTOC is a deterministic physical observable that an independent quantum platform can reproduce, and its companion experiment maps the echo decay directly to an NMR molecular-structure observable. The constructive-interference signal is extracted against an explicit decoherence baseline, because bare decay $F(t) \to 0$ cannot distinguish unitary scrambling from environmental damping.

---

##### Three Directions of Operator Growth

| Direction | Metric | Growth Law | Bound / Universality |
| --- | --- | --- | --- |
| **Rate** (time) | Quantum Lyapunov exponent $\lambda_L$ | $C(t) \sim \frac{1}{N}e^{\lambda_L t}$; operator size $n(t) \sim e^{\lambda_L t}$ | **MSS Bound:** $\lambda_L \leq \frac{2\pi k_B T}{\hbar} = \frac{2\pi}{\beta}$ |
| **Reach** (space) | Butterfly velocity $v_B$ | Operator front light cone: $C(t,x) \sim \frac1N\exp[\lambda_L(t - x/v_B)]$ | **Lieb–Robinson Bound:** $\Vert{}[A(t),B]\Vert{} \leq C e^{-\mu(d - v_{LR}t)}$, with $v_B \leq v_{LR}$ |
| **Depth** (operator space) | Krylov complexity $K(t)$ | Free systems: $K \sim t$<br>

<br>Integrable: $K \sim t^2$<br>

<br>Chaotic: $K \sim e^{2\alpha t}$ | **UOGH Hypothesis:** Lanczos coefficients grow as $b_n \sim \alpha n$, where $\alpha \leq \frac{\pi}{\beta}$ |

* **Rate (Time):** Semiclassically (Larkin & Ovchinnikov 1969), the quantum commutator maps to a classical Poisson bracket:
```math
-\langle[x(t), p(0)]^2\rangle \;\longrightarrow\; \hbar^2 \{x(t), p(0)\}_{\text{PB}}^2 \sim \hbar^2 e^{2\lambda_{cl}t}
```


Thus, $\lambda_L$ is the direct quantum descendant of the classical Lyapunov exponent.
*Hierarchical timescales:*
```math
t_{\text{therm}} \sim \mathcal{O}(1) \quad < \quad t_* \sim \lambda_L^{-1}\ln N \quad < \quad t_K \sim e^S
```


where $t_{\text{therm}}$ is local dissipation, $t_*$ is the Hayden–Preskill / Sekino–Susskind scrambling time, and $t_K$ is the Poincaré recurrence time.
⚠️ Extracting a clean exponential window requires a large-system limit ($N \gg 1$); in finite 1D qubit chains, spatial butterfly velocity $v_B$ is extracted far more reliably than $\lambda_L$.
* **Reach (Space):** The Lieb–Robinson velocity $v_{LR}$ is a state-independent operator-norm bound setting a strict relativistic-like speed limit in non-relativistic lattice systems (Lieb & Robinson 1972). In contrast, the butterfly velocity $v_B$ is state- and temperature-dependent. This spatial limit dictates:
1. The slope of the OTOC light-cone wavefront.
2. The minimum circuit depth required to generate global entanglement across $`n`$ qubits ($d \sim n$ in 1D, $d \sim \sqrt{n}$ on 2D architectures, $d \sim \log n$ in all-to-all connectivity).
3. Front dynamics in random circuits: operator spreading forms a ballistic front governed by Kardar–Parisi–Zhang (KPZ) fluctuations with front broadening $\sigma(t) \sim t^{1/3}$ (Nahum, Vijay, Haah, PRX 2018; von Keyserlingk et al., PRX 2018), and entanglement entropy grows as $S(t) = v_E t$ with entanglement velocity bounded by $v_E \leq v_B$ (Mezei & Stanford, JHEP 2017).


* **Depth (Operator Space):** The Liouvillian superoperator $\mathcal{L} = [H, \cdot]$ acts on the operator Hilbert space equipped with the Frobenius/Wightman inner product. The Liouville–Lanczos algorithm tridiagonalizes $\mathcal{L}$ over the Krylov chain:
```math
\mathcal{K} = \text{span}\{W, [H,W], [H,[H,W]], \dots\}
```


governed by the recurrence $\mathcal{L}\vert{}O_n) = b_{n+1}\vert{}O_{n+1}) + b_n\vert{}O_{n-1})$. The **Krylov complexity** measures the mean operator position along this chain:
```math
K(t) = \sum_{n} n\,\vert{}\varphi_n(t)\vert{}^2
```


(Parker, Cao, Avdoshkin, Scaffidi, Altman, PRX 2019).

---

##### Logical Stack of Bounds: KMS $\implies$ UOGH $\implies$ MSS

```math
\text{KMS thermal analyticity in strip } 0 \leq \mathrm{Im}(t) \leq \beta \;\implies\; \alpha \leq \frac{\pi}{\beta} \;\implies\; \lambda_L \leq \frac{2\pi k_BT}{\hbar}
```

* **Universal Operator Growth Hypothesis (UOGH):** In chaotic many-body systems at finite temperature, the Lanczos sequence $b_n$ grows maximally linearly ($b_n \sim \alpha n$ with $\alpha \leq \pi/\beta$), setting an upper bound on operator complexity growth.
* **Maldacena–Shenker–Stanford (MSS) Bound:** Analyticity of out-of-time-ordered four-point correlation functions under Kubo–Martin–Schwinger (KMS) thermal boundary conditions bounds the growth rate by $\lambda_L \leq 2\pi k_B T / \hbar$ (JHEP 2016).
* **Sachdev–Ye–Kitaev (SYK) Model:** $`N`$ Majorana fermions with all-to-all random four-body interactions (Kitaev 2015; Maldacena & Stanford, PRD 2016). Exactly solvable in the large-$`N`$ limit and holographically dual to Jackiw–Teitelboim (JT) gravity in $\mathrm{AdS}_2$. It **saturates the MSS bound** ($\lambda_L = 2\pi/\beta$), demonstrating that black holes behave as the fastest and most efficient information scramblers in nature.

**Reference Stack:**

* Lieb–Robinson bound: Lieb, Robinson, *Commun. Math. Phys.* (1972).
* Semiclassical OTOC foundation: Larkin, Ovchinnikov, *JETP* (1969).
* Fast scrambling conjecture: Sekino, Susskind, *JHEP* (2008).
* Chaos bound: Maldacena, Shenker, Stanford, *JHEP* (2016).
* SYK model: Kitaev, KITP talks (2015); Maldacena, Stanford, *PRD* (2016).
* Krylov complexity & UOGH: Parker, Cao, Avdoshkin, Scaffidi, Altman, *PRX* (2019).
* Random-circuit operator spreading & KPZ universality: Nahum, Vijay, Haah, *PRX* (2018); von Keyserlingk, Rakovszky, Pollmann, Sondhi, *PRX* (2018).
* Entanglement velocity bound: Mezei, Stanford, *JHEP* (2017).
* Information retrieval: Hayden, Preskill, *JHEP* (2007); Yoshida, Kitaev, *arXiv:1710.03363*.
* Barren plateaus in variational circuits: McClean, Boixo, Smelyanskiy, Babbush, Neven, *Nat. Commun.* (2018); review Larocca et al., *Nat. Rev. Phys.* (2025).

---

##### Static Fingerprints: ETH and Spectral Statistics

* **Eigenstate Thermalization Hypothesis (ETH, Srednicki):**
$$A_{mn} = \mathcal{A}(\bar E)\delta_{mn} + e^{-S(\bar E)/2}f_A(\bar E,\omega)R_{mn}$$


A *single* chaotic energy eigenstate behaves locally like a microcanonical thermal ensemble. The global system remains pure while local subsystems thermalize via entanglement with the rest of the spectrum.
* *Chaotic dynamics:* Satisfy ETH $\implies$ local thermalization.
* *Integrable systems:* Constrained by extensive local conserved quantities $\implies$ Generalized Gibbs Ensemble (GGE).
* *Many-Body Localization (MBL):* Strong disorder preserves local integrals of motion (LIOMs / $l$-bits) $\implies$ breakdown of thermalization.


* **Random Matrix Theory (BGS Conjecture / Bohigas–Giannoni–Schmit):**
* Chaotic quantum spectra display Wigner–Dyson energy-level repulsion characterized by Dyson ensembles with mean adjacent gap ratio $\langle r\rangle \approx 0.53$.
* Integrable spectra lack level repulsion and exhibit Poissonian statistics with $\langle r\rangle \approx 0.39$.


* **Spectral Form Factor (SFF):**
$$K(\tau) = \langle\vert{}\mathrm{Tr}(e^{-iHt})\vert{}^2\rangle$$


Exhibits a diagnostic **dip–ramp–plateau** profile at late times $`t > t_*`$, revealing discrete energy level correlations long after the spatial OTOC has fully saturated.

---

##### Scrambling vs. Decoherence

| Diagnostic Feature | Unitary Scrambling | Lindblad Open Decoherence |
| --- | --- | --- |
| **Information Dynamics** | Delocalized reversibly into non-local multi-party entanglement; reconstructible from global operators | Dissipated irreversibly into external bath degrees of freedom |
| **Entropy Scaling** | Local subsystem entanglement entropy grows; global state remains strictly pure ($S_{\text{vN}}(\rho_{\text{global}}) = 0$) | Global von Neumann entropy $S_{\text{vN}}(\rho)$ increases non-unitarily |
| **OTOC Response** | $F(t) \to 0$ driven by true non-commutative many-body operator growth | $F(t) \to 0$ driven by environment-induced dephasing and amplitude damping |
| **Diagnostic Risk** | Reflects intrinsic many-body quantum chaos | Can mimic operator spreading and generate a **false Lyapunov exponent $\lambda_L$** |

Quantitative experimental extraction requires error-mitigated echo protocols and baseline normalization to decouple unitary scrambling from non-unitary CPTP channel noise. Modeling and bounding non-Markovian and CPTP noise impacts on OTOCs, alongside fault-tolerant simulation of open-system Lindbladians, remains an active research frontier.

---

##### Consequences: Black Holes $\longleftrightarrow$ Quantum Computing

* **Scrambling as a Resource (Hayden–Preskill Protocol):** A black hole acts as an optimal information mirror. An unknown quantum state thrown into a scrambling black hole after its Page time can be reconstructed from a few emitted Hawking radiation quanta collected alongside the historical radiation in time $\mathcal{O}(\ln N)$. The **Yoshida–Kitaev decoding circuit** achieves a state-reconstruction fidelity directly proportional to the OTOC value and operates with maximum efficiency at the theoretical chaos bound (experimentally verifiable via two-copy Bell state sampling).
* **Scrambling as an Obstacle (Barren Plateaus):** Deep parametrized quantum circuits that scramble rapidly form approximate unitary $t$-designs on $U(2^n)$. Haar integration concentrates observable gradients exponentially with qubit count:
```math
\mathrm{Var}_{\theta}[\partial_\theta \langle H \rangle] \sim 2^{-n}
```


(McClean et al. 2018). As a consequence, randomly initialized variational quantum algorithms (VQAs) encounter flat cost landscapes that are classically and quantumly untrainable. In Hamiltonian simulation, scrambling dynamics also impose an algorithmic complexity bound scaling as $\mathcal{O}(nt\cdot\mathrm{polylog}(1/\epsilon))$.
* **Random Circuit Sampling (RCS):** The Porter–Thomas distribution:
$$P(p) \approx N e^{-Np}$$


acts as the static fingerprint of Haar-random state generation. The circuit depth required to enter the Porter–Thomas regime corresponds precisely to the geometric scrambling time ($d \sim n$ in 1D architectures, $d \sim \sqrt{n}$ on 2D planar chips), reflecting the time needed for the Lieb–Robinson light cone to traverse the physical processor.
<br>

### Observation of constructive interference at the edge of quantum ergodicity

Im Nature-Paper von Oktober 2025 (**„Observation of constructive interference at the edge of quantum ergodicity“**, Google Quantum AI, *Nature* 646, 825–829, DOI: [10.1038/s41586-025-09526-6](https://doi.org/10.1038/s41586-025-09526-6)) geht es um einen **fundamentalen quantenmechanischen Benchmark**, der zeigt, wie wiederholte Zeitumkehrungen (**OTOCs höherer Ordnung**, speziell $k=2$) die mikroskopischen Details chaotischer Vielteilchendynamik sichtbar halten und warum dies klassisch extrem schwer zu simulieren ist.

---

#### 1. Das physikalische Kernproblem: Ergodizität und Scrambling
In isolierten Quanten-Vielteilchensystemen führt die schnelle Entstehung von Verschränkung (Scrambling / Quanten-Ergodizität) dazu, dass lokale Quanteninformation rasch in exponentiell vielen Freiheitsgraden des Hilbertraums „versteckt“ wird:
* **Herkömmliche Observablen und zeitgeordnete Korrelatoren (TOCs, $\langle M(t)M \rangle$)** zerfallen exponentiell schnell. Nach wenigen Gatter-Zyklen ($t \approx 9$) sind sie praktisch im statistischen Rauschen verschwunden und „blind“ für mikroskopische Details der Dynamik.
* Um solche Prozesse dennoch zu untersuchen, braucht man **Echosequenzen mit Zeitumkehr** (wie beim klassischen Out-of-Time-Order Correlator, OTOC / $C^{(2)}$).

---

#### 2. Das neue Konzept: OTOC zweiter Ordnung ($\text{OTOC}(2)$ bzw. $C^{(4)}$)
Das Nature-Paper erweitert das Echo-Prinzip auf ein **Interferometer mit mehreren Armen / wiederholter Zeitumkehr**:
```math
\mathcal{U}_k(t) = B(t)\,[M\,B(t)]^{k-1}, \qquad C^{(2k)} = \langle \mathcal{U}_k^\dagger M \mathcal{U}_k M \rangle = \langle (B(t)M)^{2k} \rangle
```

* Während der Standard-OTOC ($k=1$) aus **zwei Evolutionsblöcken** ($U(t)$ vorwärts, $U^\dagger(t)$ rückwärts) besteht, nutzt **$\text{OTOC}(2)$ ($k=2$) vier Evolutionsblöcke** ($U, U^\dagger, U, U^\dagger$).
* **Heisenberg-Bild & Pauli-Pfade:** Entwickelt man den zeitentwickelten Butterfly-Operator $B(t)$ in Multi-Qubit-Pauli-Strings $P_n$, zerfällt $C^{(4)}$ in:
  $$C^{(4)} = \sum_{\alpha,\beta,\gamma,\delta} c_{\alpha\beta\gamma\delta} \frac{\mathrm{Tr}[P_\alpha P_\beta P_\gamma P_\delta]}{2^N}$$
  Damit die Spur nicht verschwindet, muss das Produkt der vier Strings die Identität ergeben (geschlossene Schleife im Konfigurationsraum):
  1. **Diagonale Beiträge ($C^{(4)}_{\text{diag}}$):** $\alpha = \beta$ und $\gamma = \delta$ („kleine Schleifen“, Fläche null). Diese existieren bereits im Standard-OTOC $C^{(2)}$.
  2. **Off-diagonale Beiträge ($C^{(4)}_{\text{off-diag}}$):** Vier *paarweise verschiedene* Strings ($\alpha \neq \beta \neq \gamma \neq \delta$), deren Produkt dennoch $I$ ergibt (**„große Schleifen“**). Diese existieren **nur ab $k \ge 2$**.

---

#### 3. Experimenteller Nachweis der konstruktiven Interferenz
Auf supraleitenden Quantenprozessoren (Willow-Architektur) von Google Quantum AI wurde bewiesen, dass dieser off-diagonale Interferenzmechanismus real und dominant ist:
* **Pauli-Insertion-Protokoll:** Werden während der Vorwärts- und Rückwärtsentwicklung zufällige Pauli-Gatter eingefügt, randomisiert dies die Vorzeichen/Phasen der Pauli-Strings, ohne deren Amplituden zu verändern.
* **Ergebnis:** Während diagonale Anteile unbeeinflusst bleiben, löscht sich die Off-Diagonale destruktiv aus (die Pearson-Korrelation zwischen Messung und Simulation bricht von **$\rho = 0{,}998$** auf **$\rho = 0{,}555$** ein). Das belegt eindeutig **konstruktive Interferenz großer Schleifen** im ungestörten System.
* **Algebraischer statt exponentieller Sensitivitätszerfall:** Die Fluktuation $\sigma[C^{(4)}]$ über Schaltkreisinstanzen fällt nur algebraisch (Power-Law) ab und bleibt selbst jenseits von 20 Zyklen hochsensitiv für mikroskopische Parameter.

---

#### 4. Klassische Simulationskomplexität & Beyond-Classical Regime
Genau die Eigenschaft, die dem $\text{OTOC}(2)$ seine Sensitivität verleiht (die Vielwege-Interferenz der großen Schleifen), macht ihn für klassische Algorithmen extrem teuer:
* Gängige approximative Monte-Carlo- und Pauli-Path-Heuristiken (z. B. Cached Monte Carlo, CMC), die für $C^{(2)}$ noch passable Ergebnisse liefern ($\text{SNR} \approx 5{,}3$), versagen bei $C^{(4)}_{\text{off-diag}}$ völlig ($\text{SNR} \approx 1{,}1$ vs. Quantenprozessor $\text{SNR} \approx 3{,}9$ bei 40 Qubits).
* **65-Qubit-Experiment:** Für 65 Qubits und 23 Zyklen benötigt eine klassische Tensor-Netzwerk-Kontraktion auf dem US-Supercomputer **Frontier** geschätzt **~3,2 Jahre**, während der Quantenprozessor die Daten in **2,1 Stunden pro Schaltkreis** erfasst (ein Laufzeitunterschied von etwa **Faktor 13.000**).

---

#### 5. Praktischer Machbarkeitsnachweis: Hamiltonian Learning
Um zu zeigen, wozu diese Sensitivität nützlich ist, demonstrieren die Autoren ein **Hamiltonian-Learning-Experiment** (auf 34 Qubits):
* Eine unbekannte Phase $\xi$ eines Zweiqubit-Gatters ($\xi/\pi = 0{,}6$) in einem Netzwerk wird gelernt, indem experimentelle $\text{OTOC}(2)$-Kurven mit simulierten Kurven abgeglichen werden. Die Kostenfunktion minimiert exakt beim Sollwert.

---

#### 6. Wichtige Abgrenzung: drei verwandte Arbeiten
Drei eng verwandte, aber strikt zu trennende Arbeiten:

| Paper / Artefakt | Typ | Wesentliche Merkmale |
| :--- | :--- | :--- |
| **Science 374, 1479 (2021)**, [arXiv:2101.08870](https://arxiv.org/abs/2101.08870) | Historische Baseline | Standard-OTOC ($k=1$, 2 Blöcke) auf Sycamore; trennt *operator spreading* von *operator entanglement*. |
| **Nature 646, 825 (2025)**, [DOI](https://doi.org/10.1038/s41586-025-09526-6) | **Dieses Paper** (abstrakter Benchmark) | **$\text{OTOC}(2)$ ($k=2$, 4 Blöcke)** auf 2D-Zufallsschaltkreisen (bis 65Q); Entdeckung der konstruktiven Interferenz großer Schleifen; Demonstration von Beyond-Classical-Laufzeitvorteil. |
| **[arXiv:2510.19550](https://arxiv.org/abs/2510.19550) (2025)** | Chemische Anwendung | Reale chemische Anwendung (**NMR-OTOC** zur Strukturaufklärung von Toluol/9Q und DMBP/15Q). Nutzt wieder einen **Standard-OTOC ($k=1$, 2 Blöcke)** unter der TARDIS-Sequenz. |

<br>

### Quantum computation of molecular geometry via many-body nuclear spin echoes

Verständnisleitfaden zu arXiv:2510.19550 (NMR-OTOC)

*Erklärt alle Begriffe des Papers von Grund auf. Stand: 2026-10-02.*

Dieser Leitfaden setzt voraus, was du aus dem Quantencomputing kennst: Qubits, Pauli-Matrizen $X, Y, Z$, Hamiltonians als Summen von Pauli-Termen, unitäre Zeitentwicklung $U = e^{-iHt}$, Dichtematrizen, Erwartungswerte, Schaltkreise. Physik- oder Chemiewissen setzt er nicht voraus. Die wichtigste Brücke vorweg:

> **Ein Kernspin ist ein Qubit.** Ein Molekül mit 9 „magnetisch aktiven“ Kernen ist ein Quantenregister mit 9 Qubits, und ein NMR-Spektrometer ist ein (sehr spezieller) Quantencomputer, der dieses Register steuert und ausliest.

Fast alles Weitere lässt sich auf diesen Satz zurückführen.

**Lesehilfe.** Quellenangaben in eckigen Klammern beziehen sich auf das Paper (z. B. [SI III.E] = Supplementary Information, Abschnitt III.E). Mit *(Intuition)* markierte Stellen sind eigene Bilder oder Vereinfachungen, keine Aussagen des Papers. Teil A bis D erklären das NMR-Experiment, Teil E den OTOC, Teil F den Weg auf den Quantenchip, Teil G das Lernen der Molekülstruktur. Am Ende stehen ein Glossar und Selbsttest-Fragen.

---

#### 0. Die ganze Geschichte in zehn Sätzen

1. Chemiker wollen wissen, wie Moleküle räumlich aufgebaut sind, also wie weit bestimmte Atome voneinander entfernt sind.
2. Die Kerne bestimmter Atome (Wasserstoff, das Isotop Kohlenstoff-13) sind winzige Magnete, und zwei solche Magnete spüren einander umso stärker, je näher sie sich sind.
3. Diese Wechselwirkung („dipolare Kopplung“) fällt mit dem Abstand hoch drei ab; ab etwa 6 Å ist sie mit den üblichen Methoden nicht mehr messbar.
4. Die Idee des Papers: Statt einzelne Kopplungen zu messen, lässt man eine Information (die Ausrichtung des Kohlenstoff-13-Kerns) durch das ganze Netz der Kopplungen wandern; wie schnell und auf welchen Wegen sie wandert, hängt von allen Abständen gleichzeitig ab, auch von den schwachen.
5. Damit die Moleküle ihre Kopplungen nicht durch wildes Herumwirbeln wegmitteln, löst man sie in einem Flüssigkristall, der sie teilweise ausrichtet.
6. Eine raffinierte Pulsfolge („TARDIS“) lässt die Kopplungen erst vorwärts wirken und dann rückwärts, wie ein zurückgespulter Film.
7. Dazwischen stört man gezielt eine entfernte Gruppe von Kernen (die Methylgruppe, den „Butterfly“); kommt nach dem Zurückspulen weniger zurück als losgeschickt wurde, war die Information bis zur Methylgruppe gelangt. Dieses Maß heißt OTOC.
8. Die OTOC-Kurve über der Zeit ist ein Fingerabdruck der Molekülgeometrie; um sie zu deuten, muss man sie für Kandidaten-Geometrien vorhersagen.
9. Diese Vorhersage ist eine Quantensimulation, die klassisch exponentiell teuer wird; das Paper führt sie auf Googles Willow-Prozessor aus (9 und 15 Qubits, noch klassisch prüfbar).
10. Ergebnis: Ein Abstand in Toluol und ein Verdrehwinkel in DMBP lassen sich so bestimmen, mit einer Genauigkeit wie bei etablierten Methoden.

Der Quantencomputer kommt nur in Schritt 9 ins Spiel: bei der Quantensimulation.

---

#### Teil A: Physik der Kernspins

##### A1. Atome, Kerne und „magnetisch aktive Kernspins“

Ein Atom besteht aus einem winzigen Kern (Protonen und Neutronen) und einer Elektronenhülle. Viele Kerne besitzen einen **Kernspin**, einen quantenmechanischen Eigendrehimpuls, und damit verbunden ein **magnetisches Moment**: Der Kern verhält sich wie eine winzige Kompassnadel.

Die Spinquantenzahl $I$ bestimmt, wie viele Zustände der Kernspin hat:
- $I = 0$: kein Spin, kein Magnet, für NMR unsichtbar.
- $I = 1/2$: genau zwei Zustände („Spin up“, „Spin down“ entlang eines Magnetfelds). **Das ist ein Qubit.**
- $I = 1$ oder mehr: mehr als zwei Zustände (Qutrit usw.), zusätzlich elektrische Effekte (Quadrupol), die die Sache kompliziert machen.

| Kern | Spin $I$ | Natürlicher Anteil | Rolle im Paper |
| :--- | :--- | :--- | :--- |
| $`^1`$H (Proton, „Wasserstoff“) | 1/2 | ≈ 99,98 % | 8 bzw. 14 Qubits pro Molekül |
| $`^{12}`$C (normaler Kohlenstoff) | 0 | ≈ 98,9 % | unsichtbar, kein Qubit |
| $`^{13}`$C (Kohlenstoff-13) | 1/2 | ≈ 1,1 % | genau 1 Qubit pro Molekül, das Messqubit |
| $`^2`$H (Deuterium, „schwerer Wasserstoff“) | 1 | ≈ 0,015 % | ersetzt im Kontrollexperiment die Methylprotonen |

**„Magnetisch aktive Kernspins“** heißt also: Kerne mit $I = 1/2$, die als Qubits zählen. Deshalb hat Toluol (C$`_7`$H$`_8`$, 15 Atome) nur 9 Qubits: die 8 Wasserstoffkerne plus ein einziges $`^{13}`$C. Die anderen sechs Kohlenstoffatome sind $`^{12}`$C und tragen nichts bei. Bei DMBP (C$`_{14}`$H$`_{14}`$, 28 Atome) sind es entsprechend 14 + 1 = 15 Qubits.

**Isotopenmarkierung.** Weil $`^{13}`$C natürlich nur zu 1,1 % vorkommt, synthetisieren die Chemiker die Moleküle gezielt so, dass an genau einer Position ein $`^{13}`$C sitzt. Die Notation **[4-$`^{13}`$C]-Toluol** heißt: Kohlenstoff Nummer 4 des Toluols ist ein $`^{13}`$C (die Nummerierung beginnt beim Kohlenstoff, der die Methylgruppe trägt; Nummer 4 liegt ihm gegenüber). **[1-$`^{13}`$C]-DMBP** heißt entsprechend: Kohlenstoff Nummer 1 ist markiert. Genau ein $`^{13}`$C pro Molekül ist wichtig, weil es dadurch ein eindeutiges Messqubit gibt und das Messsignal eine einzige Spektrallinie ist (siehe A6).

##### A2. Spin im Magnetfeld: Zeeman-Aufspaltung, Präzession, Larmor-Frequenz

Das Experiment läuft in einem supraleitenden Magneten mit einem sehr starken, sehr gleichmäßigen Feld $B_0 = 11{,}75$ Tesla (zum Vergleich: ein Kühlschrankmagnet hat etwa 0,005 T) [Methods]. Legt man ein Feld entlang $z$ an, haben die beiden Spinzustände unterschiedliche Energie (**Zeeman-Aufspaltung**). In Qubit-Sprache ist der Hamiltonian eines einzelnen Kernspins

$$H = -\tfrac{\omega_0}{2} Z, \qquad \omega_0 = \gamma B_0,$$

also einfach eine $Z$-Rotation. $\gamma$ ist das **gyromagnetische Verhältnis**, eine Naturkonstante je Kernsorte. Ein Spin, der nicht genau entlang $z$ zeigt, kreiselt deshalb um die $z$-Achse wie ein schräg stehender Kreisel; das heißt **Präzession**, ihre Frequenz **Larmor-Frequenz** $\nu_0 = \omega_0/2\pi$.

Bei 11,75 T beträgt sie für $`^1`$H etwa **500 MHz** (deshalb „500-MHz-Spektrometer“ [Methods]) und für $`^{13}`$C etwa **126 MHz**. Das ist die „Qubit-Frequenz“, wie bei supraleitenden Qubits einige GHz.

**Zwei Kanäle.** Weil Protonen und $`^{13}`$C so unterschiedliche Frequenzen haben, lassen sie sich getrennt ansteuern: Das Spektrometer hat einen **Protonenkanal** ($`^1`$H) und einen **Kohlenstoffkanal** ($`^{13}`$C). In der NMR-Notation heißen die Protonen-Spinoperatoren $I$ (z. B. $I_z^i$ für Proton $i$) und die des seltenen Kerns $S$ (also $S_x$, $S_z$ für den $`^{13}`$C) [SI III.A]. Es gilt $I = \sigma/2$, also z. B. $I_x = X/2$.

##### A3. Rotierendes Bezugssystem und chemische Verschiebung

Die 500 MHz Präzession ist für die eigentliche Physik uninteressant. Man beschreibt alles in einem Bezugssystem, das mit der Larmor-Frequenz mitrotiert (**rotating frame**). Das ist dasselbe wie das Wechselwirkungsbild bezüglich der Qubit-Frequenz bei supraleitenden Qubits: Der große $Z$-Term verschwindet, übrig bleiben kleine Abweichungen und die Kopplungen.

Die wichtigste kleine Abweichung ist die **chemische Verschiebung** (chemical shift). Die Elektronen um einen Kern schirmen das äußere Feld ein klein wenig ab, je nach chemischer Umgebung unterschiedlich stark. Deshalb präzedieren Protonen an verschiedenen Stellen des Moleküls minimal unterschiedlich schnell. Gemessen wird das in **ppm** (parts per million) der Larmor-Frequenz; bei 500 MHz entspricht 1 ppm = 500 Hz.

Für das Paper wichtig: Die drei **Methylprotonen** (in der CH$`_3`$-Gruppe) liegen gut 2 kHz neben den **Ringprotonen** (in Tab. III: Methyl bei −2348 Hz, Ringprotonen zwischen −111 und +19 Hz, jeweils relativ zu einer Referenzfrequenz). Dieser Frequenzunterschied erlaubt es, die Methylprotonen gezielt zu drehen, ohne die Ringprotonen nennenswert zu bewegen. Das ist der Mechanismus des Butterfly-Pulses (D3). In Tab. III heißen diese Werte $\omega_i/2\pi$.

**Einheiten.** Frequenzen stehen in der NMR fast immer in Hz (Schwingungen pro Sekunde). Im Hamiltonian braucht man Kreisfrequenzen in rad/s; der Umrechnungsfaktor ist $2\pi$. Deshalb tauchen in den Formeln des Papers ständig Ausdrücke wie $\bar H/2\pi$ auf, und deshalb muss eine Simulation die Kopplungen von Hz in rad/s umrechnen.

##### A4. Radiofrequenz-Pulse sind Ein-Qubit-Gatter

Ein **RF-Puls** (Radiofrequenz-Puls) ist ein kurzes magnetisches Wechselfeld bei der Larmor-Frequenz, erzeugt von einer Spule um die Probe. Im rotierenden Bezugssystem sieht dieses Wechselfeld wie ein statisches Feld in der $xy$-Ebene aus, und die Spins drehen sich um diese Achse. Ein RF-Puls ist also eine Ein-Qubit-Rotation.

- Die **Phase** des Pulses bestimmt die Drehachse in der $xy$-Ebene: Phase $`x`$ heißt Drehung um $`x`$, Phase $y$ um $y$, Phase $\bar y$ (gesprochen „minus y“) um $-y$.
- Die **Dauer** (bei fester Stärke) bestimmt den Drehwinkel.
- **Notation:** $`(\pi/2)_y`$ ist eine Drehung um 90° um die $y$-Achse, $\pi_y$ eine Drehung um 180° um $y$. Im Paper dauert ein $\pi/2$-Puls $`t_p = 10{,}5\,\mu`$s [SI III.D].

**Der große Unterschied zum Quantenchip:** Ein Puls auf dem Protonenkanal wirkt auf alle Protonen gleichzeitig. Einzelne Qubits gezielt anzusprechen geht nur indirekt, etwa über die chemische Verschiebung. Deshalb braucht die NMR raffinierte Pulsfolgen, um gewünschte effektive Hamiltonians herzustellen (Teil D).

##### A5. Das thermische Ensemble und die „unendliche Temperatur“

Eine NMR-Probe ist kein einzelnes Molekül, sondern eine Flüssigkeit mit unvorstellbar vielen identischen Molekülen. Jedes Molekül ist ein eigenes, unabhängiges 9-Qubit-Register; gemessen wird immer der Mittelwert über alle. *(Intuition: Es laufen gleichzeitig Trillionen identischer Kopien desselben Quantencomputers, und man sieht nur den Durchschnitt.)*

Im Magnetfeld bevorzugen die Spins minimal die energetisch günstigere Richtung. Wie minimal, sagt die Boltzmann-Statistik: Bei 500 MHz und Raumtemperatur ist die **Polarisation** etwa $\hbar\omega_0 / 2k_BT \approx 4\cdot10^{-5}$. Von 100 000 Protonen zeigen also nur etwa 4 mehr nach oben als nach unten. Die Dichtematrix eines Moleküls ist deshalb fast die Einheitsmatrix:

$$\rho \approx \frac{1}{2^n}\left(\mathbb{1} + \epsilon \cdot (\text{kleine Korrektur})\right), \qquad \epsilon \sim 10^{-5}.$$

Der Anteil $\mathbb{1}/2^n$ ist der **maximal gemischte Zustand**: alle $2^n$ Basiszustände gleich wahrscheinlich. Physikalisch ist das der Zustand bei **unendlich hoher Temperatur**. Er ändert sich unter keiner Zeitentwicklung ($U\mathbb{1}U^\dagger = \mathbb{1}$) und liefert kein Signal. Interessant ist nur die kleine Korrektur, die **Abweichungsdichtematrix** (deviation density matrix).

**Warum das für die Simulation wichtig ist.** Weil der Hintergrund maximal gemischt ist, ist das NMR-Signal eine Spur über alle Zustände, geteilt durch $2^n$, also ein Mittelwert über alle Basiszustände. Genau das berechnet eine exakte Simulation als $\mathrm{Tr}[\dots]/2^n$. Auf dem Quantenchip lässt sich eine solche Spur durch Mittelung über zufällige Anfangszustände schätzen (das Prinzip heißt **Typikalität**). Daher kommen die zufälligen Bitstrings im Schätzer und die 250 Zufallszustände bei der AlphaEvolve-Bewertung [Methods].

##### A6. Signal auslesen: FID, Spektrum, Entkopplung

Zeigt die Magnetisierung (die Summe der Spin-Erwartungswerte über alle Moleküle) in die $xy$-Ebene, präzediert sie und induziert in der Spule eine winzige Wechselspannung. Diese klingt mit der Zeit ab und heißt **FID** (*free induction decay*). Eine Fourier-Transformation macht daraus ein **Spektrum** mit Linien bei den Präzessionsfrequenzen.

- Die Form einer Linie ist typischerweise eine **Lorentz-Kurve**; ihre Fläche bzw. Amplitude ist proportional zu $\langle S_x \rangle$ des $`^{13}`$C.
- **Protonenentkopplung** (proton decoupling): Während der Aufnahme bestrahlt man die Protonen kräftig. Dadurch mitteln sich ihre Kopplungen zum $`^{13}`$C weg, und das $`^{13}`$C-Signal fällt zu einer einzigen scharfen Linie zusammen.
- Weil jedes Molekül genau ein $`^{13}`$C hat, gibt es genau eine Linie; deren gefittete Amplitude ist der OTOC-Wert [SI III.G].

*(Intuition in QC-Sprache: Das ist eine Messung von $`\langle X\rangle`$ auf dem Messqubit, allerdings nicht als einzelne Shots mit 0/1-Ergebnissen, sondern direkt als Erwartungswert, weil über Trillionen Kopien gemittelt wird.)*

#### A7. Gradientenpulse und Sättigung

- **Gradientenpuls:** Für kurze Zeit wird das Magnetfeld ortsabhängig gemacht (stärker oben, schwächer unten). Spins an verschiedenen Orten präzedieren dann unterschiedlich schnell, ihre Phasen laufen auseinander, und die Summe über die Probe mittelt sich zu null. Damit kann man unerwünschte Kohärenzen gezielt zerstören („spoilen“).
- **Sättigung** (saturation): Die Besetzung von „up“ und „down“ wird gleich gemacht, die Polarisation ist danach null. Für die Protonen heißt das: Sie sind im maximal gemischten Zustand, tragen also keinerlei Anfangsinformation.

---

#### Teil B: Wechselwirkungen zwischen Kernspins

##### B1. Dipolare Kopplung: zwei winzige Stabmagnete

Jeder Kernspin ist ein kleiner Magnet und erzeugt um sich herum ein Magnetfeld, ein **Dipolfeld** (so wie ein Stabmagnet: Feldlinien vom Nordpol zum Südpol, nach außen schnell schwächer werdend). Ein zweiter Kernspin in der Nähe spürt dieses Feld. Das ist die **dipolare Kopplung** $D_{ij}$ zwischen den Spins $i$ und $j$. Ihre Stärke hängt von zwei Dingen ab:

1. **Abstand:** $D_{ij} \propto 1/r_{ij}^3$. Halber Abstand heißt achtfache Kopplung, doppelter Abstand ein Achtel. Zwei Protonen im Abstand 1 Å koppeln mit etwa 120 kHz, bei 2,5 Å nur noch mit etwa 8 kHz.
2. **Winkel:** Die Kopplung ist proportional zu $(3\cos^2\theta - 1)$, wobei $\theta$ der Winkel zwischen der Verbindungslinie der beiden Kerne und dem Magnetfeld ist. Dieser Faktor kann positiv, negativ oder null sein (null beim „magischen Winkel“ 54,7°).

Genau das macht die dipolare Kopplung für die Strukturaufklärung wertvoll: **Wer $D_{ij}$ kennt, kennt (bei bekannter Orientierung) den Abstand.** Und genau das ist zugleich ihr Problem: Wegen $1/r^3$ verschwindet sie bei größeren Abständen schnell im Rauschen. Das Paper nennt als Grenze etablierter Methoden etwa 6 Å für Kohlenstoff-Kohlenstoff-Abstände [Haupttext, Einleitung].

**Wie die Kopplung als Hamiltonian aussieht.** Hier kommt ein Detail, das später wichtig wird:
- Zwischen zwei **gleichartigen** Kernen (Proton–Proton, „homonuklear“) enthält die Kopplung einen $ZZ$-Anteil und einen **Flip-Flop-Anteil** $\propto (X_iX_j + Y_iY_j)$. Der Flip-Flop-Term tauscht $\lvert\uparrow\downarrow\rangle \leftrightarrow \lvert\downarrow\uparrow\rangle$. Das ist erlaubt, weil beide Spins dieselbe Frequenz haben und der Tausch keine Energie kostet.
- Zwischen **verschiedenartigen** Kernen ($`^{13}`$C–Proton, „heteronuklear“) bleibt nur der $ZZ$-Anteil. Ein Flip-Flop würde ein 126-MHz-Quant gegen ein 500-MHz-Quant tauschen; die Energie passt nicht, der Term mittelt sich im rotierenden Bezugssystem weg (**säkulare Näherung**).

Deshalb koppelt im Paper der $`^{13}`$C nur über $Z_C Z_i$-Terme an die Protonen, und deshalb braucht ein Simulationsmodell für den Kohlenstoff nur $ZZ$-Kopplungen und keine Doppelquanten-Terme.

##### B2. Skalare J-Kopplung

Neben der direkten magnetischen Kopplung durch den Raum gibt es eine indirekte, die über die chemischen Bindungen läuft: Die Elektronen der Bindung vermitteln zwischen den Kernspins. Das ist die **J-Kopplung** (skalare Kopplung). Sie ist meist klein (wenige Hz bis etwa 150 Hz für direkt gebundenes C–H) und richtungsunabhängig (isotrop).

Im Paper spielt sie nur für die C–H-Paare eine Rolle, und zwar immer in der Kombination $D_{Ci} + \tfrac12 J_{Ci}$. Der auffällig große Wert $J_{C1} = 559$ Hz in Tab. III ist kein physikalischer Wert, sondern ein Fit-Artefakt: Er kompensiert eine ungenaue Koordinate des $`^{13}`$C, und weil nur die Kombination $D_{C1} + \tfrac12 J_{C1}$ zählt, schadet das nicht [Tab. III, Fußnote b; Tab. II, Fußnote a].

#### B3. Warum Kopplungen in normalen Flüssigkeiten verschwinden

Moleküle in einer Flüssigkeit drehen sich extrem schnell in alle Richtungen (*tumbling*, Milliarden Mal pro Sekunde). Dabei durchläuft der Winkel $\theta$ aus B1 alle Werte, und der Mittelwert von $(3\cos^2\theta - 1)$ über alle Raumrichtungen ist exakt null. **In einer normalen Flüssigkeit mitteln sich die dipolaren Kopplungen also vollständig weg.** Übrig bleiben chemische Verschiebung und J-Kopplung.

In einem **Festkörper** ist es umgekehrt: Nichts dreht sich, alle Kopplungen wirken voll, auch zwischen benachbarten Molekülen. Dann ist jeder Spin mit sehr vielen anderen gekoppelt, die Spektrallinien werden breit und unübersichtlich, und es gibt kein sauber abgegrenztes Spinsystem mehr.

##### B4. Flüssigkristalle: der Mittelweg („nematisch“)

Ein **Flüssigkristall** ist ein Zustand zwischen Flüssigkeit und Kristall. Er fließt wie eine Flüssigkeit, aber seine (meist stäbchenförmigen) Moleküle haben eine gemeinsame Vorzugsrichtung. Bei der **nematischen** Phase ist das die einzige Ordnung: Die Stäbchen zeigen im Mittel in dieselbe Richtung, den **Direktor**, ihre Positionen sind aber völlig ungeordnet und beweglich. *(Intuition: Baumstämme, die einen Fluss hinuntertreiben, liegen alle grob längs zur Strömung, schwimmen aber wild durcheinander.)* Flüssigkristalle kennt man aus LCD-Displays.

Das Paper verwendet zwei klassische nematische Flüssigkristalle als Lösungsmittel: **EBBA** (für Toluol, bei 295 K) und **5CB** (für DMBP, bei 289 K) [Methods]. Die Temperaturen liegen im nematischen Bereich; oberhalb einer Übergangstemperatur wird der Flüssigkristall zu einer normalen (isotropen) Flüssigkeit.

Löst man ein kleines Molekül wie Toluol darin, wird es von den Stäbchen ringsum ein wenig mit ausgerichtet. Es dreht sich zwar weiterhin schnell, aber nicht mehr völlig gleichmäßig in alle Richtungen, sondern bevorzugt eine. Dann ist der Mittelwert von $(3\cos^2\theta - 1)$ nicht mehr null, und es bleibt eine verkleinerte, aber messbare **Restkopplung** (residual dipolar coupling) übrig. Kopplungen zu anderen Molekülen mitteln sich trotzdem weg, weil die Moleküle aneinander vorbeidiffundieren.

**Ergebnis:** Jedes gelöste Molekül ist ein sauber abgegrenztes Spinsystem mit wohldefinierten, mittelstarken Kopplungen innerhalb des Moleküls. Genau das braucht man für ein „molekulares Quantenregister“.

##### B5. Der Saupe-Ordnungstensor

Wie stark und in welcher Weise ein Molekül im Mittel ausgerichtet ist, beschreibt der **Saupe-Ordnungstensor** $S_{ab}$. Man legt in das Molekül ein Achsenkreuz ($x, y, z$; bei Toluol ist $z$ die Längsachse durch Methylgruppe und $`^{13}`$C, $`x`$ steht senkrecht auf der Ringebene [Fig. S7]). Dann ist zum Beispiel

$$S_{zz} = \left\langle \tfrac{3\cos^2\theta_z - 1}{2} \right\rangle,$$

wobei $\theta_z$ der Winkel zwischen der Molekülachse $z$ und dem Magnetfeld ist und die spitzen Klammern über die Bewegung mitteln. Werte:
- $S_{zz} = 1$: Achse $z$ zeigt immer exakt entlang des Feldes (perfekte Ordnung).
- $S_{zz} = 0$: keine Vorzugsrichtung (wie in normaler Flüssigkeit).
- $S_{zz} = -1/2$: Achse $z$ steht immer senkrecht zum Feld.

Allgemein ist $S$ eine symmetrische $3\times3$-Matrix mit Spur null. Bei Toluol verschwinden aus Symmetriegründen die Nebendiagonalelemente, und wegen der Spur null bleiben zwei unabhängige Zahlen: $S_{yy} = -0{,}0176$ und $S_{zz} = 0{,}1758$ [Tab. III]. Die Längsachse von Toluol ist also schwach entlang des Feldes ausgerichtet, mit etwa 18 % der maximal möglichen Ordnung.

**Wozu man ihn braucht.** Jede dipolare Kopplung ist (Konstante $`/\,r_{ij}^3`$) mal ein Winkelfaktor, und dieser Winkelfaktor ergibt sich aus der Molekülgeometrie und dem Saupe-Tensor. Kennt man die Geometrie (Tab. II: Atomkoordinaten) und $S$, kann man alle $D_{ij}$ ausrechnen. Genau so sind die $D_{ij}$ in Tab. III entstanden [Tab. III, Überschrift]. Für die Methylprotonen kommt hinzu, dass die CH$`_3`$-Gruppe schnell um ihre Achse rotiert; darüber wird zusätzlich gemittelt [SI III.B, Gl. S10–S11].

Das **Strukturlernen** ist das umgekehrte Problem: Aus gemessenen Signalen (hier den OTOC-Kurven) auf die Geometrie zurückschließen.

---

#### Teil C: Die beiden Moleküle

##### C1. Toluol

Toluol ist ein Benzolring (sechs Kohlenstoffatome im Sechseck) mit einer **Methylgruppe** (CH$`_3`$) an einer Ecke. An den anderen fünf Ecken sitzt je ein Wasserstoff. Positionen am Ring relativ zu einem Substituenten heißen **ortho** (direkt daneben), **meta** (eine Position weiter) und **para** (gegenüber).

Die Nummerierung im Paper [Fig. S7]:
- **C** ($`^{13}`$C): an der para-Position gegenüber der Methylgruppe.
- **H1**: direkt an den $`^{13}`$C gebunden (Abstand 1,09 Å, Tab. II). Deshalb ist $D_{C1}$ mit −4139 Hz bei weitem die stärkste C–H-Kopplung.
- **H2, H3**: neben dem $`^{13}`$C; **H4, H5**: neben der Methylgruppe.
- **H6, H7, H8**: die Methylprotonen, die Butterfly-Spins.

Der Strukturparameter $z_{om}$ ist der Abstand zwischen einem ortho- und einem meta-Proton (z. B. H2–H4), etwa 2,46 Å.

**Drei Cluster** [SI III.L]: Die Spins zerfallen in drei Gruppen, innerhalb derer die Kopplungen 3- bis 10-mal stärker sind als zwischen den Gruppen: (1) $`^{13}`$C mit H1, (2) die vier Ringprotonen H2–H5, (3) die Methylprotonen. Innerhalb der Cluster bilden sich gebundene Zustände. Das Paper erklärt damit den auffälligen Buckel der OTOC-Kurve um 1,5 ms: Die Information pendelt im C–H1-Cluster schnell hin und her (Oszillation), und der Ringproton-Cluster wirkt wie eine Barriere zum Rest des Moleküls.

##### C2. DMBP (3',5'-Dimethylbiphenyl)

**Biphenyl** sind zwei Benzolringe, die über eine Einfachbindung verbunden sind. Die Ringe können sich um diese Bindung gegeneinander verdrehen; der Verdrehwinkel heißt **Diederwinkel** $\varphi$ (dihedral angle). Bei DMBP trägt der zweite Ring (Positionen mit Strich, 3' und 5') zwei Methylgruppen. Der $`^{13}`$C sitzt an Position 1, also genau an der Verbindungsstelle der Ringe; an ihm hängt kein Wasserstoff. Nummerierung [Fig. S7]: H1–H5 am unsubstituierten Ring, H6–H8 am substituierten Ring, H9–H11 und H12–H14 die beiden Methylgruppen.

*(Intuition, aus dem Paper abgeleitet: Weil am $`^{13}`$C kein Wasserstoff hängt, fehlt die sehr starke direkte C–H-Kopplung, und deshalb reicht für DMBP die einfachere Sequenz TARDIS-1; TARDIS-2 ist laut Paper für Fälle wie Toluol gedacht, in denen der $`^{13}`$C direkt an ein Proton gebunden ist [SI III.D.2].)*

Der Diederwinkel ist die eigentliche Lernaufgabe bei DMBP (G2).

**d$`_6`$-DMBP**: eine Variante, in der die sechs Methylprotonen durch Deuterium ($`^2`$H) ersetzt sind. Deuterium ist für das Protonenexperiment unsichtbar; das vereinfacht das Kontrollexperiment (G3).

---

#### Teil D: Das NMR-Experiment Schritt für Schritt

Das Protokoll hat fünf Stufen [SI III.C, Fig. S8]: Präparation, Vorwärtsentwicklung, Störung, Rückwärtsentwicklung, Auslesen.

##### D1. Präparation, Satz für Satz

> *„Nach der Thermalisierung im 11,75-Tesla-Magneten …“*

Die Probe wird in den Magneten gebracht und eine Weile gewartet, bis sich das thermische Gleichgewicht eingestellt hat (A5): winzige Polarisation aller Kerne entlang des Feldes.

> *„… werden alle Protonen selektiv gesättigt …“*

Mit Pulsen und Gradienten auf dem Protonenkanal wird die Protonenpolarisation zerstört (A7). Danach sind alle Protonen maximal gemischt. Der $`^{13}`$C wird dabei nicht angefasst („selektiv“) und behält seine Polarisation entlang $z$.

> *„… und ein $`(\pi/2)_y`$-Puls bringt den $`^{13}`$C-Spin in einen $`x`$-polarisierten Zustand.“*

Eine 90°-Drehung um die $y$-Achse kippt die $z$-Polarisation des $`^{13}`$C in die $`x`$-Richtung (A4).

> *„Der Anfangszustand ist also $`\rho_0 \propto S_x`$.“*

Zusammen heißt das: Die Abweichungsdichtematrix des Moleküls ist proportional zu $S_x = X_C/2$, also „$`^{13}`$C zeigt in $`x`$-Richtung, alle Protonen völlig zufällig“. Das Zeichen $\propto$ heißt „proportional zu“; der riesige Einheitsmatrix-Anteil und der winzige Vorfaktor $\epsilon$ werden weggelassen, weil sie für das Signal keine Rolle spielen. In QC-Sprache: Messqubit in $\lvert+\rangle$, alle anderen Qubits im maximal gemischten Zustand, und das bei unendlicher Temperatur (A5).

> *„Zusätzlich läuft ein ‚RF-Filter‘, der ein Subensemble mit engerer Verteilung der Radiofrequenzamplitude auswählt, da die RF-Feldstärke über das Probenvolumen nicht perfekt homogen ist.“*

Die Spule erzeugt das RF-Feld nicht überall in der Probe gleich stark (**RF-Inhomogenität**). Ein nominaler 90°-Puls ist dann am Rand der Probe vielleicht ein 87°-Puls und in der Mitte ein 91°-Puls. Bei einem einzelnen Puls ist das harmlos, aber TARDIS besteht aus Hunderten von Pulsen, und die Fehler summieren sich. Der Filter funktioniert so [SI III.E]: Man lässt 10 TARDIS-Zyklen vorwärts und 10 rückwärts laufen. Moleküle in Bereichen mit gutem RF-Feld kommen dabei sauber zurück, solche mit stark abweichendem Feld nicht. Danach zerstören Gradienten und zufällige Protonenpulse alles, was nicht saubere $`^{13}`$C-$`x`$-Magnetisierung ist. Übrig bleibt ein **Subensemble** (eine Teilmenge der Moleküle), das in einem gleichmäßigeren RF-Feld sitzt. Der Vorgang wird zweimal wiederholt. *(Intuition: Wie ein Sieb, das nur die Moleküle durchlässt, bei denen die Pulse zuverlässig funktionieren.)*

##### D2. Vorwärtsentwicklung mit TARDIS

**Das Problem.** Der natürliche dipolare Hamiltonian ist da und lässt sich nicht abschalten oder umpolen; es gibt keinen Knopf, der $H$ in $-H$ verwandelt. Für ein Echo braucht man aber genau das.

**Die Lösung: Average Hamiltonian Theory (AHT).** Man feuert sehr schnell hintereinander eine periodische Folge von Pulsen ab. Zwischen und während der Pulse wirkt der natürliche Hamiltonian, aber „von wechselnden Richtungen gesehen“, weil die Pulse die Spins ständig drehen. Über einen ganzen Zyklus der Länge $t_c$ betrachtet, wirkt dann ein **effektiver** (mittlerer) Hamiltonian $\bar H$:

$$U(t_c) = e^{-i\bar H t_c}, \qquad \bar H = \bar H^{(0)} + \bar H^{(1)} + \bar H^{(2)} + \dots$$

Diese Reihe heißt **Magnus-Entwicklung**. $\bar H^{(0)}$ ist schlicht der zeitliche Mittelwert; die höheren Terme sind Korrekturen aus Kommutatoren, je kleiner, desto kürzer der Zyklus. *(Intuition: Das ist eng verwandt mit der Trotter-Zerlegung beziehungsweise der Baker-Campbell-Hausdorff-Formel; $`\bar H^{(1)}`$ entspricht dem Trotter-Fehler erster Ordnung.)* Periodisch getriebene Systeme heißen in der Physik **Floquet-Systeme**; daher spricht das Paper von „double-resonance Floquet driving protocols“. Achtung, Namensgleichheit: Die „Floquet-Kalibrierung“ der Gatter in F5 ist etwas ganz anderes.

**TARDIS** (*Time-Accurate Reversal of Dipolar InteractionS*) ist eine im Paper neu entwickelte Pulsfolge, deren $\bar H^{(0)}$ ein **Doppelquanten-Hamiltonian** ist und die sich umkehren lässt.

**Was „Doppelquanten“ (double quantum, DQ) heißt.** Der Term

$$X_iX_j - Y_iY_j = 2(\sigma_i^+\sigma_j^+ + \sigma_i^-\sigma_j^-)$$

dreht zwei Spins **gleichzeitig in dieselbe Richtung**: $\lvert\downarrow\downarrow\rangle \leftrightarrow \lvert\uparrow\uparrow\rangle$. Die Gesamtmagnetisierung ändert sich dabei um zwei Einheiten, um „zwei Quanten“. Der natürliche Flip-Flop-Term $X_iX_j + Y_iY_j$ tauscht dagegen nur ($\lvert\uparrow\downarrow\rangle \leftrightarrow \lvert\downarrow\uparrow\rangle$, „Nullquanten“). Im Paper steht die DQ-Form für Toluol als $I_y^iI_y^j - I_x^iI_x^j$ (TARDIS-2, Gl. S25) und für DMBP als $I_x^iI_y^j + I_y^iI_x^j$ (TARDIS-1, Gl. S22); beides ist dieselbe Struktur, nur um 45° um $z$ gedreht.

**Der Trick mit der Zeitumkehr** *(eigene Erklärung, algebraisch geprüft)*. Eine Drehung aller Protonen um 90° um die $z$-Achse macht $X \to Y$ und $Y \to -X$. Damit wird

```math
X_iX_j - Y_iY_j \;\longrightarrow\; Y_iY_j - X_iX_j = -(X_iX_j - Y_iY_j).
```

Der DQ-Hamiltonian wechselt also sein Vorzeichen. Eine solche $z$-Drehung lässt sich in der NMR sehr einfach realisieren: Man verschiebt die **Phase** aller Protonenpulse um 90° (statt um $`x`$ wird um $y$ gedreht usw.). Das ist der Kern der Rückwärtsentwicklung. Der heteronukleare Term $I_zS_z$ bleibt bei einer $z$-Drehung unverändert; er wird durch zusätzliche $\pi$-Pulse auf dem Kohlenstoffkanal umgedreht ($S_z \to -S_z$). Beides zusammen ergibt $`\bar H^{(0)}_\leftarrow = -\bar H^{(0)}_\rightarrow`$ [SI III.D, Gl. S23 und S26]. Mit dem natürlichen Flip-Flop-Term ginge das nicht: $X_iX_j + Y_iY_j$ ist unter $z$-Drehungen invariant. Das ist der Grund, warum man überhaupt den Umweg über den DQ-Hamiltonian geht.

**Bausteine und Skalierungsfaktoren.** TARDIS-2 setzt sich aus Blöcken zusammen, die von der klassischen **Baum-Pines-Sequenz** (einer Multiquanten-NMR-Sequenz aus den 1980ern; BP-Blöcke) und von **Doppelresonanz-Blöcken** (DR, Pulse auf beiden Kanälen gleichzeitig) abgeleitet sind [SI III.D.2]. Weil die Pulse die Wechselwirkung nur einen Teil der Zeit „in der gewünschten Richtung“ wirken lassen, ist der effektive Hamiltonian schwächer als der natürliche. Das beschreiben die **Skalierungsfaktoren** $\eta$: für TARDIS-2 $\eta_\text{heter} = 2/9$ (C–H-Term) und $\eta_\text{homo} = 1$ (H–H-Term), für TARDIS-1 $2/3$ und $1/\pi$. Diese Faktoren gehören in die Umrechnung der Kopplungen.

##### D3. Die Störung: der Butterfly-Puls $V_H$

Der Name kommt vom **Schmetterlingseffekt**: Eine kleine lokale Störung kann in einem chaotischen System später große Wirkung haben. Hier wird gezielt nur die Methylgruppe gedreht [SI III.F, Gl. S14]:

```math
V_H = \exp\Big(-i\theta\, \vec n \cdot \sum_{i \in \text{Methyl}} \vec I^{\,i}\Big),
```

also eine Drehung um den Winkel $\theta$ um die Achse $\vec n$, angewendet auf jedes Methylproton.

**Wie man nur die Methylprotonen dreht**, obwohl jeder Puls auf alle Protonen wirkt: Man verwendet die Sequenz **BLEW-12** (nach Burum, Linder und Ernst). Sie schaltet die Proton-Proton-Kopplungen effektiv ab, sodass jedes Proton nur noch mit seiner chemischen Verschiebung (A3) präzediert. Stellt man die Trägerfrequenz auf die Ringprotonen ein, präzedieren diese kaum, die Methylprotonen (gut 2 kHz daneben) aber deutlich. Ergebnis: eine selektive Drehung der Methylgruppe. $\pi$-Pulse auf dem $`^{13}`$C zwischen zwei BLEW-12-Blöcken heben die Wirkung der C–H-Kopplungen während dieser Zeit auf [SI III.F]. Die effektive Drehachse ist $\vec n = (0,2,1)/\sqrt5$ [Gl. S34].

*Offene Frage:* Achse und Mechanismus stehen im Paper, der Winkel $\theta$ ist dort aber nicht eindeutig angegeben.

##### D4. Rückwärtsentwicklung

Dieselbe Dauer $t$ unter dem umgedrehten effektiven Hamiltonian, also (näherungsweise) $U^\dagger(t)$ [Gl. S15].

##### D5. Auslesen

Die Dichtematrix wird noch einmal gefiltert, sodass nur ihr $S_x$-Anteil übrig bleibt (wie in D1). Dann wird der FID des $`^{13}`$C unter Protonenentkopplung aufgenommen; die gefittete Linienamplitude ist der OTOC-Wert (A6) [SI III.G]. Die Werte werden auf den Wert bei $t = 0$ normiert, deshalb beginnt jede Kurve bei 1.

##### D6. Die Kontrolle: das Loschmidt-Echo

Lässt man den Butterfly weg ($V_H = I$), müsste nach Vorwärts- und Rückwärtsentwicklung exakt der Anfangszustand zurückkommen: Signal = 1. Dieses Experiment heißt **Loschmidt-Echo** (nach Josef Loschmidt, der im 19. Jahrhundert mit dem Gedanken der Zeitumkehr gegen Boltzmanns Thermodynamik argumentierte).

Im echten Experiment fällt das Loschmidt-Echo trotzdem langsam ab (gelbe Kurve in Fig. 2c), weil die Umkehr nicht perfekt ist: Die höheren Magnus-Terme $\bar H^{(1)}, \bar H^{(2)}$ kehren sich nicht exakt mit um, und die RF-Inhomogeneität (D1) bleibt teilweise bestehen. Das Loschmidt-Echo zeigt also, wie gut die Zeitumkehr funktioniert, und dient zur Bewertung des OTOC. In einer rauschfreien Simulation ist es exakt 1; das eignet sich als Test.

---

#### Teil E: Was ein OTOC ist (in Quantencomputing-Sprache)

##### E1. Heisenberg-Bild und Operator-Wachstum

Normalerweise denkt man, dass sich Zustände zeitlich entwickeln (Schrödinger-Bild). Gleichwertig kann man die Operatoren entwickeln (**Heisenberg-Bild**): $`B(t) = U^\dagger(t)\, B\, U(t)`$.

Ein lokaler Operator, etwa $Z$ auf einem Qubit, wächst dabei: Nach kurzer Zeit ist $B(t)$ eine Summe von Pauli-Strings, die auch Nachbarqubits betreffen, nach längerer Zeit Strings über viele Qubits:

```math
B(t) = \sum_\alpha w_\alpha(t)\, P_\alpha, \qquad P_\alpha \in \{I, X, Y, Z\}^{\otimes n}.
```

Bei lokalen Wechselwirkungen (oder Gattern zwischen Nachbarn) breitet sich dieser „Träger“ höchstens mit endlicher Geschwindigkeit aus. Im Raum-Zeit-Diagramm entsteht ein Kegel, der **Lichtkegel**; seine Geschwindigkeit heißt **Butterfly-Geschwindigkeit** $v_B$. Außerhalb des Lichtkegels hat ein Gatter keinen Einfluss auf das Messergebnis, und genau darauf beruht die Lichtkegel-Filterung (F6).

##### E2. Der OTOC als „Lineal“

Die Größe, die das Paper misst, ist [Gl. S13]

```math
C(t) = \mathrm{Tr}\left\{S_x\, U^\dagger V_H U\, S_x\, U^\dagger V_H^\dagger U\right\},
```

normiert auf $C(0) = 1$. Mit $W = U^\dagger V_H U$ (das ist der Butterfly im Heisenberg-Bild, also $`V_H(t)`$) ist das $\mathrm{Tr}[S_x W S_x W^\dagger]$. Der Name **OTOC** (*out-of-time-order correlator*) kommt daher, dass die Operatoren nicht in zeitlicher Reihenfolge stehen: Es wird vorwärts und rückwärts in der Zeit gesprungen.

**Die Intuition** *(eigene Erklärung)*. Der $`^{13}`$C startet mit einer Information (Ausrichtung in $`x`$). Unter $U(t)$ breitet sich diese Information über das Kopplungsnetz aus, also $S_x(t)$ wächst.
- Hat sie die Methylgruppe zur Zeit $t$ noch **nicht** erreicht, berührt der Butterfly nur Spins, die mit der Information nichts zu tun haben. Nach dem Zurückspulen kommt alles zurück: $C(t) = 1$.
- Hat sie die Methylgruppe **erreicht**, stört der Butterfly genau die Teile, in denen die Information inzwischen steckt. Das Zurückspulen klappt dann nicht mehr vollständig: $`C(t) < 1`$.

$C(t)$ misst also, *wie viel* der Information *wann* an der Methylgruppe angekommen ist. Das hängt von allen Kopplungen auf allen Wegen ab, auch von den schwachen. Eine Kopplung, die für sich allein zu schwach zum Messen wäre, verändert trotzdem die kollektive Ausbreitung. Deshalb spricht das Paper vom „längeren molekularen Lineal“ [Fig. 1].

**Warum nicht einfacher?** Ein gewöhnlicher, zeitgeordneter Korrelator (**TOC**, z. B. $\langle S_x(t) S_x\rangle$, „wie viel Signal ist nach Zeit $t$ noch am $`^{13}`$C“) zerfällt schnell, weil die Information sich verteilt und nicht zurückkommt. Dann ist das Signal im Rauschen verschwunden und mit ihm die Information über die Kopplungen. Die Zeitumkehr holt den Großteil zurück und lässt nur die Wirkung der Störung übrig.

##### E3. Scrambling, Ergodizität, Konzentration

- **Scrambling** („Verrühren“): Eine anfangs lokale Information verteilt sich über das ganze System, sodass sie mit lokalen Messungen nicht mehr zugänglich ist. Sie ist nicht verloren (die Dynamik ist unitär), aber in komplizierten Vielteilchen-Korrelationen versteckt. Der OTOC ist das Standardmaß dafür.
- **Ergodizität**: Ein System ist ergodisch, wenn es im Lauf der Zeit „alle erlaubten Konfigurationen gleichmäßig durchwandert“. Ergodische Quantensysteme scrambeln schnell und vergessen dabei die Details ihres Anfangszustands.
- **Konzentration** (*concentration of measure*): In sehr großen Hilberträumen liegen die Erwartungswerte fast aller Zustände sehr nahe am Mittelwert. Ein Signal, das in diesen Bereich gerät, trägt kaum noch unterscheidbare Information, es ist „blind“ für die Mikrophysik. Das ist gemeint, wenn man sagt, eine Observable „konzentriere“.

##### E4. Das 2021er Paper: operator spreading und operator entanglement

Das Science-Paper von 2021 (arXiv:2101.08870) zeigt, dass Scrambling aus zwei Zutaten besteht:
- **Operator spreading**: Die Pauli-Strings in $B(t)$ werden räumlich größer (der Lichtkegel wächst). Das ist auch klassisch billig zu berechnen.
- **Operator entanglement**: Die *Anzahl* der beitragenden Pauli-Strings explodiert. Das macht die klassische Simulation teuer.

Um beides zu trennen, verglich das Paper **Clifford-Schaltkreise** (aus einer speziellen Gattermenge; nach dem Gottesman-Knill-Theorem klassisch effizient simulierbar, ein Pauli-String bleibt dort immer ein einzelner Pauli-String) mit **Nicht-Clifford-Schaltkreisen**. Der *Mittelwert* von $C(t)$ über viele zufällige Schaltkreise zeigt vor allem den Lichtkegel, also das Spreading. Die *Schwankung* von Schaltkreis zu Schaltkreis zeigt das Entanglement, und hier unterscheiden sich Clifford und Nicht-Clifford deutlich.

**Ancilla-Interferometrie**: Ein zusätzliches Hilfsqubit (Ancilla) wird so mit dem Schaltkreis verschränkt, dass seine Messung den OTOC direkt liefert, ähnlich einem Hadamard-Test. Zur Normierung misst man zusätzlich den Fall ohne Butterfly ($B = I$), der Rauscheffekte herausrechnet. Das öffentliche OTOC-Tutorial in Googles ReCirq-Bibliothek implementiert genau dieses Protokoll; im molekularen Paper wird es nicht verwendet.

##### E5. Das Nature-Paper 2025: OTOC höherer Ordnung

Die Verallgemeinerung mit mehreren Zeitumkehrungen [Nature 646, 825]:

```math
C^{(2k)} = \langle (B(t)\, M)^{2k} \rangle.
```

- $k = 1$: der gewöhnliche OTOC (eine Zeitumkehr, zwei Evolutionsblöcke $U$, $U^\dagger$). Das ist der Fall des molekularen Papers.
- $k = 2$: **OTOC(2)**, mit vier Evolutionsblöcken ($U, U^\dagger, U, U^\dagger$).

**Diagonale und Off-Diagonale.** Setzt man die Pauli-Entwicklung aus E1 ein, wird $C^{(4)}$ eine Summe über Produkte von vier Pauli-Strings, deren Produkt die Identität ergeben muss, damit die Spur nicht verschwindet. Die „harmlosen“ Beiträge sind solche, in denen die Strings paarweise gleich sind (Diagonale, **kleine Schleifen**). Neu bei $k = 2$ sind Beiträge mit vier *verschiedenen* Strings, deren Produkt trotzdem die Identität ist (Off-Diagonale, **große Schleifen**). Diese Beiträge interferieren konstruktiv und halten das Signal länger am Leben („constructive interference at the edge of quantum ergodicity“).

**Nachweis:** Fügt man während der Entwicklung zufällige Pauli-Operatoren ein, werden die Phasen der einzelnen Strings zufällig. Die Diagonale bleibt davon unberührt, die Off-Diagonale löscht sich aus. Die Übereinstimmung zwischen Messung und Vorhersage fällt dabei von 0,998 auf 0,555 [Nature, Fig. 3].

**Klassische Härte:** Genau diese Off-Diagonal-Struktur macht die gängigen klassischen Näherungsverfahren unbrauchbar. Übrig bleibt **Tensornetzwerk-Kontraktion**, für die das Paper auf dem Supercomputer **Frontier** etwa 3,2 Jahre schätzt, gegenüber etwa 13 000-mal kürzerer Messzeit. Die größte Konfiguration hat 65 Qubits, mit einem projizierten Signal-Rausch-Verhältnis (**SNR**) zwischen 2 und 3.

Wichtig für die Einordnung: Das ist ein anderes Experiment (Zufallsschaltkreise, $k = 2$) und darf nicht mit dem molekularen Paper vermischt werden.

---

#### Teil F: Vom Molekül auf den Quantenchip

##### F1. Wozu überhaupt ein Quantencomputer?

Die OTOC-Messung selbst ist reine NMR am Spektrometer. Um aus der gemessenen Kurve eine Geometrie zu lernen, muss man die Kurve für Kandidaten-Geometrien *vorhersagen* und vergleichen. Diese Vorhersage ist die Zeitentwicklung eines Systems aus $`n`$ gekoppelten Spins, also klassisch ein Problem der Größe $2^n$. Für 9 und 15 Spins geht das klassisch noch (das Paper nutzt das zur Validierung). Für größere Moleküle, etwa Proteinfragmente, wird es exponentiell teuer; dort soll der Quantencomputer übernehmen. **Das Quantenargument ist ein Skalierungsargument**, kein Vorteil bei 9 oder 15 Qubits.

##### F2. Stufe 1: Magnus-Näherung

Simuliert wird nur $\bar H^{(0)}$, der DQ-Hamiltonian (D2), nicht die vollständige Pulsfolge. Das ist ein Teil der Abweichung zwischen Simulation und NMR-Experiment.

##### F3. Stufe 2: Wechselwirkungsbild bezüglich der C–H1-Kopplung

Die C–H1-Kopplung ist bei Toluol rund hundertmal stärker als die übrigen C–H-Kopplungen [SI VIII.B]. Deshalb behält man nur sie und behandelt sie gesondert (**Wechselwirkungsbild**, interaction picture: Man rechnet in einem Bezugssystem, das die Wirkung dieses einen Terms bereits enthält, sodass der Rest als Störung dazukommt). Die übrigen C–H-Kopplungen werden vernachlässigt. Ein Vergleich mit der exakten Rechnung zeigt (eigene Rechnung), dass das die ersten sechs Zeitpunkte um weniger als 0,02 ändert.

##### F4. Stufe 3: Trotterisierung

$e^{-iHt}$ für einen Hamiltonian aus vielen Termen wird als Produkt der Exponentiale der Einzelterme genähert (**Trotter-Formel erster Ordnung**), mit möglichst wenigen Schritten (ein Trotter-Schritt pro NMR-Zeitpunkt, $\delta t = 0{,}375$ ms [SI VIII.E]), weil jeder Schritt Gatter und damit Fehler kostet. *(Intuition: Weil der Rückwärtsblock exakt die Inverse des Vorwärtsblocks ist, hebt sich ein Teil des Trotter-Fehlers im OTOC auf; ohne Butterfly sogar vollständig.)*

##### F5. Stufe 4: Swap-Netzwerk und Gatter

- **All-to-all-Problem:** Im Molekül koppelt jedes Proton mit jedem; auf dem Chip gibt es nur Gatter zwischen Nachbarn auf einer Linie.
- **Swap-Netzwerk:** Man kombiniert jedes Wechselwirkungsgatter mit einem SWAP. In einem Ziegelmuster („brick wall“) über $`N`$ Lagen wandert dadurch jeder Spinzustand einmal an jedem anderen vorbei, und jedes Paar wechselwirkt genau einmal. Das ist optimal: so viele Gatter wie Paare [SI VIII.B].
- **fSim-Gatter** (*fermionic simulation*): das native Zwei-Qubit-Gatter von Googles Prozessoren mit zwei Winkeln, dem Swap-Winkel $\theta$ und der bedingten Phase $\phi$. Wechselwirkung plus SWAP ergibt bis auf Ein-Qubit-Gatter genau ein fSim-Gatter [SI VIII.C–D].
- **Composite fSim** und **Floquet-Kalibrierung:** Für Toluol brauchte man 80 verschiedene Winkelkombinationen. Jede wurde aus zwei Pulsen zusammengesetzt und mit einem Verfahren kalibriert, das das Gatter vielfach periodisch wiederholt, um kleine Winkelfehler zu verstärken und messbar zu machen (daher „Floquet“) [SI VIII.E].
- **CZ und KAK:** Für DMBP wurden die Schaltkreise in CZ-Gatter zerlegt. Die **KAK-Zerlegung** zeigt, dass jedes Zwei-Qubit-Gatter mit höchstens drei CZ plus Ein-Qubit-Gattern darstellbar ist; damit zählt man die CZ-Kosten.
- **AlphaEvolve:** ein KI-System, das *Programme* weiterentwickelt. Es bekam ein einfaches Trotter-Programm als Startpunkt und verbesserte es so lange, bis die erzeugten 15Q-Schaltkreise den exakten OTOC viel genauer trafen (mittlerer Fehler von 10,4 % auf 0,82 %), bei höchstens 792 CZ-Gattern [Methods].

##### F6. Lichtkegel-Filterung

Gatter, die außerhalb der Lichtkegel von Messqubit und Butterfly liegen (E1), können das Ergebnis nicht beeinflussen und werden gestrichen. „Doppelseitig“, weil der Kegel vom Messoperator und vom Butterfly aus gerechnet wird. Die genannten Zahlen (326 Momente, 540 fSim-Gatter; 484 Momente, 792 CZ) zählen nur die verbleibenden Gatter [Methods].

##### F7. Fehlerminderung (nur zur Einordnung)

- **ZNE** (*zero-noise extrapolation*): Man misst bei künstlich verstärktem Rauschen und extrapoliert zurück auf null Rauschen.
- **Pauli-Pfade und Hamming-Gewicht:** Schreibt man die Entwicklung als Summe über Folgen von Pauli-Strings („Pfade“), dämpft Rauschen jeden Pfad umso stärker, je mehr Nicht-Identitäts-Paulis er unterwegs ansammelt (sein **Hamming-Gewicht** $H$). Das gemessene Signal ist dann ein gewichteter Mittelwert $\sum c(H) e^{-\lambda H}$, mathematisch eine **Laplace-Transformierte** der Gewichtsverteilung $c(H)$. Das Paper nähert $c(H)$ durch eine Gaußkurve und leitet daraus die Extrapolationsformel ab [Methods, Gl. 2].
- **DD** (*dynamical decoupling*): Pulsfolgen in Wartezeiten, die unerwünschte Drift mitteln; dieselbe Idee wie die AHT in der NMR.
- **Twirling**: zufällige Gatter vor und nach einer Operation, die kohärente Fehler in zufällige Pauli-Fehler verwandeln, die sich besser behandeln lassen.

---

#### Teil G: Die Struktur lernen

##### G1. Toluol: ein Abstand

Man simuliert die OTOC-Kurve für verschiedene Werte von $z_{om}$ (der Ring wird künstlich zwischen ortho- und meta-Kohlenstoff gestreckt) und vergleicht mit der Messung. Als Maß dient ein **kovarianzgewichteter Fehler**: Abweichungen werden mit den Messunsicherheiten gewichtet, und Korrelationen zwischen den Messpunkten werden berücksichtigt. Das Minimum dieses Fehlers liefert $z_{om} = 2{,}47 \pm 0{,}01$ Å; der Literaturwert ist $2{,}46 \pm 0{,}01$ Å [Fig. 2e]. Die Fehlerbalken stammen aus **Bootstrapping**: Man zieht viele Male zufällig Teilstichproben der Daten und schaut, wie stark das Ergebnis schwankt. Mit den Willow-Daten statt der klassischen Simulation ergibt sich $2{,}44 \pm 0{,}04$ Å.

##### G2. DMBP: ein Verdrehwinkel

Bei DMBP ist der Diederwinkel $\varphi$ zwischen den Ringen nicht fest, sondern schwankt thermisch. Beschrieben wird das durch das **Potential of Mean Force** $\mathrm{PMF}(\varphi)$: die effektive freie Energie als Funktion des Winkels, in der die Umgebung (Lösungsmittel, Flüssigkristall) bereits gemittelt ist. Die Wahrscheinlichkeit eines Winkels ist dann $\propto e^{-\mathrm{PMF}(\varphi)/k_BT}$ (**Boltzmann-Gewicht**), und jede gemessene Kopplung ist ein Mittelwert über diese Verteilung:

```math
D_{ij} = \frac{\int d\varphi\; e^{-\beta\,\mathrm{PMF}(\varphi)}\, D_{ij}(\varphi)}{\int d\varphi\; e^{-\beta\,\mathrm{PMF}(\varphi)}}, \qquad \beta = 1/k_BT.
```

Woher kommt das PMF? Aus Rechenmodellen, die sich widersprechen:
- **MD/MM** (*molecular dynamics* mit *molecular mechanics*): Atome als Kugeln mit Federn (ein klassisches „Kraftfeld“), deren Bewegung über die Zeit simuliert wird. Schnell, aber nur so gut wie das Kraftfeld. Minimum bei $\varphi = 32{,}4°$.
- **DFT** (Dichtefunktionaltheorie): quantenchemische Rechnung der Elektronenstruktur, hier im Vakuum (ohne Flüssigkristall). Minimum bei $41{,}8°$.
- Ein künstliches **Doppelmuldenpotential** (zwei Minima) mit Minimum bei 50°.

Das Paper interpoliert neun **Kandidaten-PMFs** zwischen diesen drei Kurven [Fig. S33] und fragt: Welcher Kandidat erklärt die gemessene OTOC-Kurve am besten? Ergebnis mit Willow: $\varphi_\text{QC} = 40° \pm 3°$, klassische Referenz $41{,}5° \pm 0{,}2°$ [Haupttext]. Das Lernen war also eine Auswahl unter neun Kandidaten, keine freie Optimierung, und der Großteil der Struktur wurde als bekannt vorausgesetzt.

##### G3. Unabhängige Kontrollen: HMQC und MQC

- **HMQC** (*heteronuclear multiple-quantum coherence*): ein zweidimensionales NMR-Experiment, das Protonen- und Kohlenstoffsignale miteinander korreliert. Daraus wurden für Toluol Saupe-Tensor, Kopplungen und chemische Verschiebungen gefittet: Tab. III ist „HMQC-estimated“.
- **MQC-Spektroskopie** (*multiple-quantum coherence*): Man misst, wie viele Spins gemeinsam an einer Kohärenz beteiligt sind (die „Ordnung“ der Kohärenz). Für DMBP wurde das an der deuterierten Variante gemacht: Das MQC-Signal nimmt mit wachsender Ordnung schnell ab, und mit 15 Spins wäre das direkte Experiment nicht praktikabel [SI III.J]. Die Messung dient als unabhängige Kontrolle; das gelernte PMF verbessert den MQC-Fehler um den Faktor 4 gegenüber der reinen MD-Rechnung [Haupttext].

##### G4. Was das Paper nicht behauptet

1. Der Quantencomputer *misst* nichts am Molekül; die Messung ist NMR. Er *berechnet* die Vorhersagen, mit denen man die Messung deutet.
2. Bei 9 und 15 Spins wäre das klassisch noch machbar; der Vorteil ist ein Versprechen für größere Systeme.
3. Gelernt wurden ein Abstand (Toluol) und eine Auswahl unter neun Kandidaten (DMBP), keine vollständige Struktur.

---

#### Teil H: Glossar

| Begriff | Kurz erklärt | Abschnitt |
| :--- | :--- | :--- |
| AHT (Average Hamiltonian Theory) | Effektiver Hamiltonian einer schnellen periodischen Pulsfolge | D2 |
| AlphaEvolve | KI-System, das Programme evolviert; hier Generator der 15Q-Schaltkreise | F5 |
| Ancilla | Hilfsqubit, im 2021er Paper als Interferometer | E4 |
| Å (Ångström) | $10^{-10}$ m; typische Atomabstände 1–3 Å | B1 |
| Baum-Pines-Sequenz | Klassische Multiquanten-Pulsfolge, Baustein von TARDIS-2 | D2 |
| BLEW-12 | Pulsfolge, die H–H-Kopplungen abschaltet; erzeugt den Butterfly | D3 |
| Bootstrapping | Fehlerabschätzung durch wiederholtes Ziehen von Teilstichproben | G1 |
| Butterfly ($V_H$) | Gezielte lokale Störung, hier Drehung der Methylprotonen | D3 |
| Chemische Verschiebung | Kleine Frequenzverschiebung durch die Elektronenhülle | A3 |
| Clifford-Schaltkreis | Klassisch effizient simulierbare Gattermenge | E4 |
| Diederwinkel $\varphi$ | Verdrehwinkel zwischen zwei Molekülteilen | C2 |
| Dipolare Kopplung $D_{ij}$ | Magnetische Wechselwirkung zweier Kernspins, $\propto 1/r^3$ | B1 |
| Dipolfeld | Magnetfeld eines winzigen Stabmagneten (Kernspin) | B1 |
| Direktor | Vorzugsrichtung eines Flüssigkristalls | B4 |
| Doppelquanten-Hamiltonian | Dreht Spinpaare gleichsinnig, $XX - YY$; umkehrbar | D2 |
| DFT | Quantenchemische Rechnung der Elektronenstruktur | G2 |
| Deuterium ($`^2`$H) | Schwerer Wasserstoff, Spin 1, für Protonen-NMR unsichtbar | A1, C2 |
| EBBA, 5CB | Nematische Flüssigkristalle (Lösungsmittel) | B4 |
| Ensemble | Riesige Zahl identischer Moleküle, gemessen wird der Mittelwert | A5 |
| Ergodizität | System durchläuft alle Konfigurationen, vergisst Details | E3 |
| FID | Abklingendes Spulensignal der präzedierenden Magnetisierung | A6 |
| Floquet | Periodisch getrieben (Pulsfolgen); auch Name einer Gatterkalibrierung | D2, F5 |
| fSim | Natives Zwei-Qubit-Gatter (Swap-Winkel, bedingte Phase) | F5 |
| Gradientenpuls | Ortsabhängiges Feld, zerstört Kohärenzen | A7 |
| gyromagnetisches Verhältnis $\gamma$ | Naturkonstante: Frequenz pro Tesla je Kernsorte | A2 |
| Hamming-Gewicht | Zahl der Nicht-Identitäts-Paulis eines Pfads | F7 |
| Heisenberg-Bild | Operatoren statt Zustände entwickeln sich | E1 |
| heteronuklear / homonuklear | Zwischen verschiedenen / gleichen Kernsorten | B1 |
| HMQC | 2D-NMR-Experiment, korreliert $`^1`$H und $`^{13}`$C | G3 |
| Isotopenmarkierung | Gezielter Einbau von $`^{13}`$C an einer Position | A1 |
| J-Kopplung | Indirekte Kopplung über chemische Bindungen | B2 |
| KAK-Zerlegung | Jedes Zwei-Qubit-Gatter mit ≤ 3 CZ darstellbar | F5 |
| Larmor-Frequenz | Präzessionsfrequenz eines Kernspins im Feld (500 MHz für $`^1`$H) | A2 |
| Lichtkegel | Bereich, in dem ein Gatter das Ergebnis beeinflussen kann | E1, F6 |
| Loschmidt-Echo | Vorwärts-rückwärts ohne Störung; ideal = 1 | D6 |
| Lorentz-Kurve | Typische Form einer Spektrallinie | A6 |
| Magnus-Entwicklung | Reihe für den effektiven Hamiltonian ($\bar H^{(0)}$, $`\bar H^{(1)}`$, …) | D2 |
| maximal gemischter Zustand | $\mathbb{1}/2^n$, „unendliche Temperatur“ | A5 |
| MD/MM | Molekulardynamik mit klassischem Kraftfeld | G2 |
| Methylgruppe | CH$`_3`$-Gruppe; ihre Protonen sind die Butterfly-Spins | C1 |
| MQC | Spektroskopie der Mehrquanten-Kohärenzen; misst Clustergröße | G3 |
| nematisch | Flüssigkristallphase mit Richtungs-, ohne Positionsordnung | B4 |
| ortho / meta / para | Ringpositionen: daneben / übernächste / gegenüber | C1 |
| OTOC | Out-of-time-order correlator, Maß für Informationsausbreitung | E2 |
| OTOC(2) | OTOC höherer Ordnung mit vier Evolutionsblöcken | E5 |
| Pauli-String | Tensorprodukt von $I, X, Y, Z$ über alle Qubits | E1 |
| Phase (eines Pulses) | Drehachse in der $xy$-Ebene | A4 |
| PMF (Potential of Mean Force) | Effektive freie Energie entlang einer Koordinate | G2 |
| Polarisation | Überschuss von „up“ gegenüber „down“, hier ~$`10^{-5}`$ | A5 |
| ppm | Millionstel der Larmor-Frequenz; 1 ppm = 500 Hz bei 500 MHz | A3 |
| Präzession | Kreiseln eines Spins um die Feldachse | A2 |
| Protonenentkopplung | Bestrahlung der Protonen, damit das $`^{13}`$C-Signal eine Linie wird | A6 |
| RF-Filter | Echo-basierte Auswahl der Moleküle mit gutem RF-Feld | D1 |
| RF-Inhomogenität | Ungleich starkes Pulsfeld über die Probe | D1 |
| RF-Puls | Kurzes Wechselfeld, wirkt als Ein-Qubit-Rotation | A4 |
| rotierendes Bezugssystem | Mitrotierendes Koordinatensystem; entfernt den großen $Z$-Term | A3 |
| Saupe-Ordnungstensor | Beschreibt die mittlere Ausrichtung eines Moleküls | B5 |
| Sättigung | Polarisation auf null bringen | A7 |
| säkulare Näherung | Weglassen schnell oszillierender Terme | B1 |
| Scrambling | Verteilung lokaler Information über das ganze System | E3 |
| Skalierungsfaktor $\eta$ | Wie stark ein Term im effektiven Hamiltonian wirkt | D2 |
| SNR | Signal-Rausch-Verhältnis | E5 |
| Swap-Netzwerk | Ziegelmuster aus SWAP-Gattern für all-to-all auf einer Linie | F5 |
| TARDIS | Pulsfolge mit umkehrbarem DQ-Hamiltonian (Varianten 1 und 2) | D2 |
| Tesla | Einheit der magnetischen Flussdichte; hier 11,75 T | A2 |
| Tensornetzwerk | Klassische Simulationsmethode für Quantenschaltkreise | E5 |
| TOC | Zeitgeordneter Korrelator, zerfällt schnell | E2 |
| Trotterisierung | Näherung von $e^{-iHt}$ durch Produkte einfacher Exponentiale | F4 |
| Tumbling | Schnelle Rotation von Molekülen in Flüssigkeit | B3 |
| Typikalität | Spur durch Mittelung über Zufallszustände schätzen | A5 |
| Wechselwirkungsbild | Bezugssystem, das einen Teil des Hamiltonians schon enthält | F3 |
| Zeeman-Aufspaltung | Energieunterschied der Spinzustände im Magnetfeld | A2 |
| ZNE | Extrapolation von verstärktem Rauschen auf null Rauschen | F7 |
| $z_{om}$ | Abstand ortho- zu meta-Proton in Toluol | C1, G1 |

---

#### Teil I: Selbsttest

Erst selbst beantworten, dann aufklappen.

**1. Warum hat Toluol 15 Atome, aber nur 9 Qubits?**
<details class="answer">

Nur Kerne mit Spin 1/2 zählen: die 8 Protonen und das eine gezielt eingebaute $`^{13}`$C. Die übrigen sechs Kohlenstoffatome sind $`^{12}`$C (Spin 0) und magnetisch unsichtbar (A1).

</details>

**2. Was bedeutet $`\rho_0 \propto S_x`$ in Qubit-Sprache?**
<details class="answer">

Messqubit in $\lvert+\rangle$, alle anderen Qubits maximal gemischt; der riesige Einheitsmatrix-Anteil und der winzige Vorfaktor werden weggelassen, weil sie kein Signal liefern (A5, D1).

</details>

**3. Warum mitteln sich dipolare Kopplungen in normalen Flüssigkeiten weg, in Flüssigkristallen aber nicht vollständig?**
<details class="answer">

In der Flüssigkeit dreht sich das Molekül gleichmäßig in alle Richtungen, und der Mittelwert von $3\cos^2\theta - 1$ ist null. Im nematischen Flüssigkristall bevorzugt es eine Richtung (beschrieben durch den Saupe-Tensor), sodass eine verkleinerte Restkopplung bleibt (B3–B5).

</details>

**4. Warum koppelt der $`^{13}`$C nur über $ZZ$-Terme an die Protonen?**
<details class="answer">

Ein Flip-Flop zwischen $`^{13}`$C (126 MHz) und $`^1`$H (500 MHz) würde Energiequanten verschiedener Größe tauschen; dieser Term mittelt sich im rotierenden Bezugssystem weg (säkulare Näherung). Übrig bleibt $I_zS_z$ (B1).

</details>

**5. Warum geht man den Umweg über den Doppelquanten-Hamiltonian?**
<details class="answer">

Weil er sich umkehren lässt: Eine 90°-Drehung um $z$ (in der NMR eine Phasenverschiebung der Pulse um 90°) macht aus $XX - YY$ den Term $-(XX - YY)$. Der natürliche Flip-Flop-Term $XX + YY$ ist unter dieser Drehung invariant (D2).

</details>

**6. Was misst $C(t)$ anschaulich, und warum ist $C(t) = 1$, solange die Information die Methylgruppe nicht erreicht hat?**
<details class="answer">

Wie viel der vom $`^{13}`$C ausgehenden Information zur Zeit $t$ bei der Methylgruppe angekommen ist. Solange dort nichts angekommen ist, stört der Butterfly nur unbeteiligte Spins, und die Zeitumkehr bringt alles zurück (E2).

</details>

**7. Warum fällt das Loschmidt-Echo im Experiment ab, in einer exakten Simulation aber nicht?**
<details class="answer">

Im Experiment kehren sich die höheren Magnus-Terme nicht exakt um, und die RF-Inhomogenität bleibt teilweise. In der Simulation ist der Rückwärtsblock exakt die Inverse des Vorwärtsblocks (D6).

</details>

**8. Wozu braucht man den Quantencomputer, wenn die Messung doch NMR ist?**
<details class="answer">

Um die OTOC-Kurven für Kandidaten-Geometrien vorherzusagen; das ist eine Quantensimulation, die klassisch mit $2^n$ skaliert. Bei 9 und 15 Spins geht es noch klassisch; der Vorteil ist ein Skalierungsargument (F1, G4).

</details>

**9. Was ist der Unterschied zwischen operator spreading und operator entanglement?**
<details class="answer">

Spreading: Die Pauli-Strings des entwickelten Operators werden räumlich größer (Lichtkegel), klassisch billig. Entanglement: Die Anzahl der beitragenden Strings explodiert, klassisch teuer (E4).

</details>

**10. Was unterscheidet OTOC(2) vom OTOC des molekularen Papers?**
<details class="answer">

OTOC(2) hat vier statt zwei Evolutionsblöcke und enthält Off-Diagonal-Beiträge („große Schleifen“), die konstruktiv interferieren und klassische Näherungen brechen. Das molekulare Paper nutzt den gewöhnlichen OTOC mit einer Zeitumkehr (E5).

</details>

**11. Warum wird bei DMBP über den Diederwinkel gemittelt, und was ist ein PMF?**
<details class="answer">

Die Ringe verdrehen sich thermisch; jede gemessene Kopplung ist ein Boltzmann-gewichteter Mittelwert über die Winkelverteilung. Das PMF ist die effektive freie Energie als Funktion des Winkels, die diese Verteilung festlegt (G2).

</details>

**12. Wie wird nur die Methylgruppe gedreht, obwohl jeder Puls auf alle Protonen wirkt?**
<details class="answer">

BLEW-12 schaltet die H–H-Kopplungen ab, sodass jedes Proton nur mit seiner chemischen Verschiebung präzediert. Mit der Trägerfrequenz auf den Ringprotonen drehen sich praktisch nur die Methylprotonen, die gut 2 kHz daneben liegen (D3).

</details>
