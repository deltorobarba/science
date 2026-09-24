
# Quantum Learning

Alexander Del Toro Barba, PhD


<img src="https://raw.githubusercontent.com/deltorobarba/science/main/nature.JPG" alt="science">

<br>

Study notes quantum learning theory (learning from quantum experiments)

- [Efficiency Boundaries](#efficiency-boundaries)
- [Searching](#searching)
- [Searching (Papers)](#searching-papers)
- [Identifying](#identifying)
- [Identifying (Papers)](#identifying-papers)
- [Estimating](#estimating)
- [Estimating (Papers)](#estimating-papers)
- [Appendix](#appendix)

---

<br>

# Efficiency Boundaries

## Objective: Triply Efficient in Sample, Time and Memory

Every quantum learning protocol is charged in three budgets, and they scale independently:
* **Access** (Sample or Query): quantum copies of $\rho$ under sampling access, oracle calls to the preparation circuit or to the process under query access (the access ladder; for processes see "What is learned"). Efficient means $\mathrm{poly}(n, \log M, 1/\epsilon)$ copies; under query access the precision term improves to $1/\epsilon$ (Heisenberg rate), the query-side version of the sample boundary.
* **Time** (classical): efficient means $\mathrm{poly}(n, M, 1/\epsilon)$ post-processing, polynomial in $M$ rather than $\log M$, since $M$ values must at least be written down.
* **Memory** (classical): efficient means $\mathrm{poly}(n)$ bits for the learned representation; a $d \times d$ hypothesis already breaks it.

**Thesis** 
* The field has charted the sample boundary in detail: exponential separations by quantum memory, adaptivity, and conjugate access are proven and partly demonstrated in hardware (see the appendix). 
* The *computational boundary* is almost uncharted, although most sample-efficient protocols fail there. 
* The reason is proof technology: Sample lower bounds come from information theory (Holevo, packing arguments) and are unconditional, hence comparatively easy to obtain. Time lower bounds need cryptographic assumptions (LWE, pseudorandom states) and are rare. One map is dense, the other nearly empty.

## Known Efficiency Boundaries

**Almost without exception, it is efficient special cases (under so-called *promises*) that make quantum learning efficient!** For fully arbitrary, generic quantum states without any promise, there are **hardly any general protocols that are efficient in all three budgets**.

"Time efficiency is never free; it is bought by a promise about the state, by a resource on the quantum side, or by a stronger access model." (Appendix, "Reading the tables".)

On the quantum side, two entangled copies and logarithmically many samples suffice to estimate all squared magnitudes of the Pauli or displacement spectrum of a state. Decoding the relevant operators classically from these measurement data, however, runs into the same cryptographic wall as post-quantum cryptography (LWE), unless the state class carries a decodable structure (symmetries, locality, factorization) or query access is available. Learned decoders can exploit such structure; they cannot break the wall.

Thesis: the sample boundary is almost completely charted (by information-theoretic, unconditional bounds: Holevo, packing, the tree method). The computational boundary, by contrast, is terra incognita: most sample-efficient protocols have no known time-efficient decoder, and where hardness is proven, it rests on cryptographic assumptions (LWE, LPN, pseudorandomness).



Here is the precise breakdown of why this is so, and why *searching* nevertheless holds a special position:

---

### 1. The other columns: where generic cases fail everywhere

The tables of this document show that **every generic case without a promise is red (🔴)**:

* **Full state tomography (no promise):**  
  🔴 🔴 🔴 – exponential in *all three* budgets: $\Theta(4^n/\epsilon^2)$ copies, $\exp(n)$ time, $\exp(n)$ memory.
* **General shadow tomography (estimating without a promise):**  
  🟢 🔴 🔴 – information-theoretically $\mathrm{poly}(\log M, n, 1/\epsilon)$ copies suffice, but time and memory are $\exp(n)$. The reason: the algorithm keeps and updates a $2^n \times 2^n$ hypothesis density matrix (*matrix multiplicative weights*).  
  *When does it become 🟢 🟢 🟢?* **Only in special cases:** e.g. a *locality promise* ($k$-local Paulis with classical shadows), a *dictionary promise* (a small list of $M$ observables known in advance, with conjugate pairs), or two-copy memory for Pauli observables.
* **General learning of circuits (identifying without a promise):**  
  🟢 🔴 🟢 – states prepared with $G$ gates need only $\tilde\Theta(G/\epsilon^2)$ copies, but beyond $G = \tilde\omega(\log n)$ gates they are **computationally hard to learn** (under RingLWE; Zhao et al. 2023).  
  *When does it become 🟢 🟢 🟢?* **Only for narrowly restricted classes:** stabilizer states, Gaussian states, matrix product states (bounded entanglement), or circuits of depth $O(1)$.

---

### 2. Why, then, is *searching* singled out as "the only hard cell"?

If special cases are needed everywhere: why does the quadrant in the appendix say that computational hardness sits exactly at the intersection of **sampling + searching**? The difference is between a **representation problem** and a genuine **decoder problem**:

#### A. In estimating, time fails because of memory ("hypothesis too large")
When general shadow tomography needs exponential time, this is simply because the hypothesis is a huge $2^n \times 2^n$ matrix. An algorithm cannot run faster than the size of the memory it writes. If the question is restricted to an explicit list of $M$ observables whose estimators are cheap to evaluate (a dictionary, local observables), the memory shrinks to $O(M)$ values and the problem becomes **efficient**.

#### B. In searching, time fails because of the algorithm ("search too hard")
When searching for the $k$ strongest peaks of a displacement spectrum, the answer is extremely short:
* The memory is **tiny**: a list of $k$ peaks needs only $O(k \log d)$ bits (🟢).
* The information is **there**: Bell sampling on $\rho \otimes \rho^*$ yields all squared magnitudes from $O(\log d / \epsilon^4)$ copies (🟢).
* **Yet time fails (🔴)!** Even with memory perfectly under control, generic localization of the addresses from random Bell samples contains **LWE (Learning With Errors)**, and on qubits **LPN**, as a special case: the displacement instance of `thm:lwe-displacement` embeds LWE. Under the LWE assumption, no efficient decoder exists, classical or quantum (proven in the tensor-product Weyl basis; open for the cyclic single-qudit basis).

---

### Summary: how efficiency is "bought" in the quantum world

There is no protocol that is efficient in all three budgets for arbitrary states and arbitrary questions. Efficiency in all three budgets (🟢 🟢 🟢) exists only in **special cases**, which can be enforced in three ways:

1. **By a structural promise (a special class of states):**
   * *Algebraic:* stabilizer states, including cluster and graph states (Gaussian elimination), Gaussian states (covariance matrix).
   * *Geometric:* $k$-local observables, juntas.
   * *Entanglement:* matrix product states (1D area law).
   * *Analytic and factorization promises* (spectral structure: coprime factorization, low-degree Pauli concentration (quantum LMN)).
2. **By a quantum resource:**
   * Entangled two-copy measurements (Bell sampling on $\rho \otimes \rho^*$).
3. **By a stronger access model:**
   * **Query access** (evaluation points chosen by the learner, oracle access to the preparation circuit or to the dynamics $e^{-iHt}$, including superposition queries), which enables divide-and-conquer methods (Goldreich–Levin, peeling). An adaptive choice of measurement basis is adaptivity, not query access (Appendix, "Measurement power").

> **Conclusion:** When quantum learning theory says "everything else is solved", it means: for estimating and identifying, **precise classes of promises have been identified** under which efficient protocols exist. For *searching*, by contrast, the map between the subgroup case (Montanaro) and the cryptographic LWE wall is only sparsely charted, and it is exactly in this no man's land that the author's project looks for new decodable classes.

## Deep Dive: Efficiency through a structural promise (a special class of states)

When a protocol becomes efficient through a **structural promise**, this means: the allowed class of quantum states is restricted so that a mathematical theorem applies, which abruptly reduces the exponential search space to a tractable problem. These structural promises fall into **four large families**:

---

### Group 1: Algebraic promises (symmetries)
*Here group and field theory turn exponential search into simple linear algebra.*

#### 1. Stabilizer states
* **The promise:** the state $|\psi\rangle$ is the joint eigenstate of an abelian subgroup of the Pauli group generated by $n$ independent commuting Pauli operators.
* **The phenomenon:** Bell difference sampling (two Bell measurements, $4$ copies) draws uniformly random elements of a linear subspace of $\mathbb{F}_2^{2n}$, the Lagrangian subspace that labels the stabilizer group.
* **The procedure (Montanaro 2017):**
  1. Measure $O(n)$ Bell differences.
  2. **Classical decoder:** **Gaussian elimination over $\mathbb{F}_2$** in time $O(n^3)$.  
     Once $n$ linearly independent vectors are found, they span the Lagrangian subspace, i.e. the stabilizer group up to signs; a few further measurements fix the signs, and the state is fully identified.

#### 2. Gaussian states (fermions and bosons)
* **The promise:** the state is a ground or thermal state of a free (non-interacting) quadratic Hamiltonian.
* **The phenomenon (Wick's theorem):** all higher $k$-point correlations factorize exactly into products of two-point correlations. For $n$ fermionic modes, the entire $2^n \times 2^n$ state is fully described by a small $2n \times 2n$ **covariance matrix** (for bosons, the covariance matrix plus the displacement vector).
* **The procedure (Aaronson, Grewal 2023; Mele et al. 2024):**
  1. Measure only quadratic Majorana observables $\gamma_j \gamma_k$ (e.g. in a few bases prepared by beamsplitter networks).
  2. **Classical decoder:** fill in the $2n \times 2n$ covariance matrix and reconstruct the state from its normal form by linear algebra in time $O(n^3)$.

#### 3. "Near-stabilizer" states ($t$ non-Clifford gates / magic)
* **The promise:** the state has stabilizer dimension at least $n-t$, e.g. it is prepared with at most $t = O(\log n)$ non-Clifford gates; or, in the agnostic version, it has stabilizer fidelity $\tau > 0$ with some stabilizer state.
* **The procedure (Grewal et al. 2023; stabilizer bootstrapping 2024):**
  * In Bell difference sampling, a fraction of at least $\tau^4$ of the samples still lands exactly in the Lagrangian subspace of the closest stabilizer state.
  * **Classical decoder:** build the commutation graph of the samples and search for **maximal cliques** in time $\exp(O(n/\tau^4))$ (polynomial above $\tau = \cos^2(\pi/8)$, where a threshold test replaces the clique search), or use list decoding (*stabilizer bootstrapping*, quasipolynomial for any $\tau$). For stabilizer dimension $n-t$, the subgroup is found the same way, and the remaining $t$-qubit state is learned by tomography at cost $2^{O(t)}$.

---

### Group 2: Geometric and locality promises (dictionaries)
*Here physics (spatial proximity, causality) reduces the search space from $4^n$ to a small, polynomial dictionary.*

#### 1. $k$-local observables (classical shadows)
* **The promise:** the physical observables of interest each act on at most $k$ qubits at a time ($k \ll n$, e.g. two-qubit couplings).
* **The phenomenon:** under random single-qubit Pauli measurements, the shadow norm of a $k$-local Pauli is $3^k$, independent of $n$.
* **The procedure (Huang, Kueng, Preskill 2020):**
  1. Measure each qubit in a random Pauli basis ($X$, $Y$, or $Z$).
  2. From the outcome bits, form classical snapshots $\hat{\rho}_i = \bigotimes_{j=1}^n (3U_j^\dagger|b_j\rangle\langle b_j|U_j - I)$.
  3. **Classical decoder:** evaluate $\mathrm{Tr}(O \hat{\rho}_i)$ only on the $k$ qubits involved. A **median-of-means estimator** suppresses outliers. The sample count carries the factor $3^k$, $O(3^k\log M/\epsilon^2)$ snapshots for $M$ observables; the time is polynomial.

#### 2. Quantum juntas and Hamiltonian structure
* **The promise:** a unitary process or Hamiltonian acts globally on $n$ qubits but depends only on an unknown subset of $k$ qubits (a junta), or consists only of $k$-local interactions of unknown geometry.
* **The phenomenon:** the number of $k$-qubit subsets is $\binom{n}{k} \le n^k$ (a polynomial dictionary).
* **The procedure (Chen, Nadimpalli, Yuen 2023; Bakshi et al., FOCS 2024):**
  * **Junta learning / Pauli-weight analysis:** Pauli sampling on the Choi state returns only strings supported on the junta; qubits outside the junta have zero influence. First isolate the $k$ active qubits, with a number of uses of $U$ independent of $n$, then learn only the $k$-qubit operator. For Hamiltonians with unknown geometry, Bakshi et al. find the terms with Heisenberg-limited queries to the dynamics.
  * *Classical origin (Bresler 2015; Klivans, Meka 2017 for Ising spins):* a maximum node degree $d$ restricts neighbourhoods to $\binom{p}{d}$ candidates. **Greedy conditional influence** identifies the edges in time $\tilde{O}(p^2)$.

---

### Group 3: Entanglement and causality promises (tensor networks)
*Here an area law prevents quantum information from spreading uncontrollably across the whole system.*

#### 1. Matrix product states (MPS / 1D area law)
* **The promise:** the state is a 1D quantum state (e.g. a spin chain) with bounded entanglement: the bond dimension is capped at $D$.
* **The phenomenon:** the entanglement entropy across any bipartition is at most $\log D$, independent of $n$. The state can be written exactly as a chain of $n$ tensors of size $D \times 2 \times D$ ($O(n D^2)$ parameters instead of $2^n$).
* **The procedure (Cramer et al. 2010; Fanizza et al. 2023):**
  1. Measure only local reduced density matrices (RDMs) of overlapping blocks (e.g. $2s+1$ neighbouring spins).
  2. **Classical decoder:** reconstruct the tensors block by block, via sequential disentangling (Cramer et al.) or a **singular value decomposition (SVD)** of Hankel-type matrices built from neighbouring blocks (Fanizza et al.). Time: $O(n \cdot \mathrm{poly}(D))$.

#### 2. Shallow quantum circuits (Lieb–Robinson, light cones)
* **The promise:** the state was prepared by a circuit of constant depth $d = O(1)$.
* **The phenomenon:** a causal light cone spreads only at finite speed. Each qubit is influenced only by qubits within a ball of radius $O(d)$.
* **The procedure (Huang et al., STOC 2024; Landau, Liu 2024):**
  * Invert the state locally on balls of radius $O(d)$ and sew these local inversions together classically into a global circuit. Time: polynomial in $n$ for constant depth.

#### 3. Quantum phases and the spectral gap (gapped ground states)
* **The promise:** the Hamiltonian has a spectral gap $\Delta > 0$ above the ground state.
* **The phenomenon:** correlations decay exponentially with distance, $\langle A_x B_y \rangle \sim e^{-|x-y|/\xi}$. States within the same phase depend smoothly on the coupling parameters.
* **The procedure (Huang et al., Science 2022; Lewis et al. 2024):**
  * **Provable machine learning:** take classical shadows of training states in the phase, polynomially many in Huang et al., $O(\log n)$ in Lewis et al.
  * **Classical decoder:** kernel regression (Huang et al.) or $\ell_1$-regularized regression (LASSO) over random Fourier features of local parameters (Lewis et al.) learns the ground-state properties for all other parameter values in the phase in polynomial time.

---

### Group 4: Analytic and factorization promises (spectral structure)
*Here number-theoretic or harmonic properties of the spectrum are exploited.*

#### 1. Coprime factorization (Chinese remainder theorem, CRT)
*(Regime 3 of the author's own project)*
* **The promise:** the Hilbert-space dimension factors into coprime factors $d = d_1 \cdot d_2 \cdots d_m$, and the displacement spectrum factorizes as a product: $y_{u_1 \dots u_m} = \prod_j y_{u_j}$.
* **The procedure:**
  1. Perform Bell measurements separately for each small factor $d_j$ ($O(\log d_j/\epsilon^4)$ copies each).
  2. Determine the local top lists for each factor.
  3. **Classical decoder:** a **best-first heap** combines the partial lists and finds the global top-$k$ peaks in $\mathrm{poly}(k, \log d)$ heap operations, without ever searching the $d^2$-element address space.

#### 2. Low-degree Pauli concentration (quantum LMN)
* **The promise:** the system comes from shallow circuits such as $\mathrm{QAC}^0$.
* **The phenomenon:** almost all of the spectral mass lies on Pauli strings of small weight (degree $\le k$); the mass beyond degree $k$ decays as $2^{-\Omega(k^{1/d})}$ (for few auxiliary qubits).
* **The procedure (Nadimpalli et al. 2023):**
  * Ignore all high-degree operators and search only the space of the $n^{O(k)}$ low-degree Pauli terms (the quantum analogue of the classical Linial–Mansour–Nisan theorem for Boolean circuits).

---

### Summary of the groups

| Promise family | What is physically excluded? | Mathematical trick | Typical classical decoder |
| :--- | :--- | :--- | :--- |
| **Algebraic** | Arbitrary superpositions | Finite fields / group invariance | **Gaussian elimination, clique search** |
| **Locality** | Long-range simultaneous couplings | Small $k$-subsets ($n^k$) | **Median of means, greedy search** |
| **Area law** | Volume-law entanglement (chaos) | Local tensor decomposition | **SVD (singular value decomposition)** |
| **Spectral** | Uncorrelated frequencies | Chinese remainder theorem / decay | **Best-first heap, Fourier truncation** |

Whenever this document shows green (🟢) in the time budget, one of these mechanisms is at work behind it, or a quantum resource, or a stronger access model (see the summary above). Without such a promise, no efficient decoder is known in general, and for LWE-type instances none can exist under standard cryptographic assumptions.

<br>

# Searching

**Searching** (observables are *output*). Given: copies of $\rho$ and a promise about the spectrum, typically a few heavy coefficients over a flat remainder, or a structural constraint on the support; what "sparse" has to mean for the task to be hard is made precise below under "Where the wall begins". Returned: the addresses $(q,p)$ that carry the weight, and then their values. Nothing else is handed over, no list of candidates and no parametrization. Like a GWAS: first find which loci matter, then measure their effect. The error factorizes accordingly into localization and estimation, and the estimation guarantees of the Estimating section apply only after localization has succeeded. That is why searching is genuinely harder than estimating, and it is the column in which LWE hardness sits.

**What is known.** The sample side is settled. Bell sampling on conjugate pairs estimates all $d^2$ squared magnitudes with $O(\log d/\epsilon^4)$ copies, exponentially fewer than any strategy without the conjugate copy, at constant quantum memory (King, Wan, McClean 2024). The information is therefore always there. 

* On the time side, efficient decoders exist under specific structural promises (exactly under a promise):
  * **Subgroup symmetry:** A subgroup support falls to Gaussian elimination (Montanaro 2017; Simon's algorithm under queries).
  * **Polynomial dictionaries & Locality:** Reduces the search to estimation (Quantum Juntas; locality reduces junta learning to a polynomial dictionary). Hamiltonian structure learning from real-time evolution stays Heisenberg-limited even when the interaction terms are not given (Bakshi, Liu, Moitra, Tang 2024). The classical archetype/original of all dictionary regimes is structure learning of Ising models from samples under a degree promise, in time $\tilde O(p^2)$ (Bresler 2015; Klivans, Meka 2017).
  * **Coprime factorization:** A factorized spectrum over coprime factors falls to a best-first heap (over the CRT factors).
* **Between the subgroup case and the wall (Agnostic / Approximate Subgroups):**
  * When samples are not purely algebraic but retain fidelity $\tau$ with a stabilizer state, Bell difference sampling still finds the closest stabilizer state (the stabilizer state of best fidelity $\tau$) in time $\exp(O(n/\tau^4))$ and polynomially above $\tau = \cos^2(\pi/8)$ (Grewal, Iyer, Kretschmer, Liang 2023). Stabilizer bootstrapping achieves quasipolynomial time for any $\tau$ (row "Agnostic tomography").
* **Bypassing the hardness wall (Why other objects or access modes are easy):**
  * **By Unit-Normalization (Sampling suffices):** For objects with $\sum \vert{}c\vert{}^2 = 1$, sparsity implies heaviness, so random draws hit the support directly.
    * For unitaries, no queries are needed: their Pauli spectrum is unit-normalized, and Bell sampling on the Choi state returns the heavy Pauli terms directly without queries.
    * For classical functions under quantum examples, sparsity alone suffices: $O(k^{1.5}\log^2 k)$ samples for a $k$-Fourier-sparse function, independent of $n$ (Arunachalam, Chakraborty, Lee, Paraashar, de Wolf 2021).
  * **By Query Access (Active choice replaces passive collision):** With query access, the classical sparse-Fourier toolkit applies (Goldreich–Levin, Kushilevitz–Mansour, sparse FFT, and their quantum-query versions). For Pauli channels, $s$-sparse error rates fall to a peeling decoder in $O(sn)$ eigenvalue queries on actively chosen stabilizer groups (Harper, Yu, Flammia 2021).
* **The computational wall (Generic sampling of states is hard):**
  * Without structural promises and under passive sampling alone, localization is LWE-hard: a real-diagonal displacement state whose Bell outcomes are LWE samples has a sparse, visible spectrum whose support cannot be located in polynomial time under standard assumptions (classical mirror: Learning Parity with Noise, thirty years old).
  * Without lattices, pseudomagic states form a second hard endpoint based on one-way functions: pseudomagic ensembles have a Pauli spectrum concentrated on $2^{n+\omega(\log n)}$ of the $4^n$ addresses and are indistinguishable from Haar-random states under one-way functions (Gu, Leone, Ghosh, Eisert, Yelin, Quek 2023), while below stabilizer entropy $O(\log n)$ a rank test on Bell difference samples tells them apart (Grewal et al. 2023).

**Efficiency status.** Copies: 🟢 in every row, the union bound over $d^2$ addresses stays logarithmic. Memory: 🟢 in every row, a sparse list fits. Time: 🟢 only where the status column names a promise or query access; 🔴 for the generic case, by a theorem in the tensor-product Weyl basis and by the LPN mirror on the Boolean side.

**What is open.**
* (1) Which classes of states and channels are time-efficient for structure learning? A generic state is most likely not both sample- and time-efficient in the Heisenberg–Weyl basis; the map of decodable classes between "subgroup-easy" and "LWE-hard" is the research question of this project.
* (2) What is the LWE counterpart for the conjugate-pair Bell protocol in the Heisenberg–Weyl basis? The hardness theorem lives in the tensor-product basis. A sample-efficient but computationally hard boundary most likely exists in the cyclic single-qudit basis too, but the naive transfer is the hidden number problem, against which lattice attacks exist; composite $d$ with coprime factors approaches the tensor structure via the CRT. The cleanest candidate for a hard endpoint in the cyclic basis is the dihedral hidden-shift problem over $\mathbb{Z}_N$: subexponential for quantum algorithms, $2^{O(\sqrt{\log N})}$ (Kuperberg 2005), and at least as hard as unique-SVP (Regev 2004); see refinement 4 below.
* (3) Average case. The hardness constructions are adversarial. Whether natural states, ground and Gibbs states of local Hamiltonians, are generically decodable is open in both directions; the conjecture of this project, a uniformly random top-$k$ support on the decodable side, is a claim about exactly this gap, and the learned decoder is its only evidence so far.
* (4) Where searching ends and identifying begins. A parametrized exponential class, the LWE secret, is both at once. No theorem separates the two beyond the size of the candidate list. The tables settle this with the LWE rule (Appendix, "Reading the tables"): if the parameter of the class is the location of the support, the row sits under searching; this is why the stabilizer family and its agnostic variants are here as well.
* (5) The magic threshold. $t = O(\log n)$ non-Clifford gates is the frontier of polynomial time; whether $\mathrm{poly}(n, 2^t)$ is optimal is open.

| Protocol or class | Object | Task type: given → returned | Copies or queries (access) | Time | Memory | Status & Condition |
| --- | --- | --- | --- | --- | --- | --- |
| **Sparse displacement spectra from Bell samples** (this project; see the structure-learning protocol) | State | Searching: sparsity promise → support and values of the spectrum | Sample: $O(\log d/\epsilon^4)$ | Generic localization LWE-hard | $O(k \log d)$ bits, the sparse list | 🟢 🔴 🟢; search too hard, **this project's cell** |
| **LWE from i.i.d. samples** (Regev 2005) and its displacement instance: a real-diagonal state whose Bell outcomes are LWE samples | Classical function; a state in the displacement instance | Searching: noisy linear samples $(\mathbf{a}_i, \langle\mathbf{a}_i,\mathbf{s}\rangle + e_i)$ → the secret $\mathbf{s}$, i.e. the hidden line that carries the support | Sample: poly, information-theoretically sufficient | Hard under the LWE assumption; classical mirror LPN, best known $2^{O(n/\log n)}$ (Blum–Kalai–Wasserman 2003) | poly, the secret | 🟢 🔴 🟢; the generic hard case, **the theorem behind this project's cell** |
| **Pseudomagic states** (Gu, Leone, Ghosh, Eisert, Yelin, Quek 2023) | State ensemble: subset phase states on $2^k$ strings | Searching in one-bit form: stabilizer entropy $\omega(\log n)$ or $\Theta(n)$, i.e. a Pauli spectrum with participation number $2^{n+\omega(\log n)}$ or $4^n$ → one bit; finding the concentrated support would decide it | Sample: poly copies suffice information-theoretically | No polynomial-time distinguisher under quantum-secure one-way functions; magic and entanglement are tunable independently | poly, the key | 🟢 🔴 🟢; the second hard endpoint of this column, from one-way functions instead of lattices; below stabilizer entropy $O(\log n)$ the class becomes distinguishable (Grewal et al. 2023), so the threshold in participation number is $2^n\mathrm{poly}(n)$ |
| **Stabilizer states** (Montanaro 2017) | State | Searching: subgroup promise → the stabilizer group, i.e. the support | Sample: $O(n)$ | $O(n^3)$, Gaussian elimination on Bell differences | $O(n^2)$, the tableau | 🟢 🟢 🟢; subgroup promise |
| **Factorized spectra over coprime factors** (Regime 3 of the own conjecture, extension G3) | State | Searching: product promise $y_{u_1\dots u_m} = \prod_j y_{u_j}(\rho_j)$ across the CRT factors of $d$ → the top-$k$ of the product from the per-factor top lists by a best-first heap | Sample: one Bell record per factor, $O(\log d_j/\epsilon^4)$ each | $\mathrm{poly}(k, \log d)$ heap operations | $O(k)$ | 🟢 🟢 🟢; factorization promise, composite $d$ only |
| **Stabilizer states on qudits, $d > 2$** (Allcock, Doriguello, Ivanyos, Santha 2024) | State | Searching: subgroup promise → the stabilizer group, where Bell difference sampling on $\rho^{\otimes 4}$ returns only $\mathrm{col}(V)\times\mathrm{col}(W)$ and can be uniform | Sample: $9n + 3\lceil\log_p \mathrm{rank}\,W\rceil + 4$ copies of $\vert S\rangle$, computational-basis measurements plus a coherent step on three copies that learns the quadratic phase ($d = p$ prime); $3n$ copies of $\vert S\rangle$ and $2n$ of $\vert S^*\rangle$ by Bell sampling, any $d$ | $O(n^3\,\mathrm{rank}\,W) \leq O(n^4)$; $O(n^3)$ with the conjugate | $O(n^2)$, the generators | 🟢 🟢 🟢; subgroup promise; the qudit caveat behind the conjugate-pair choice of this project |
| **Clifford plus few non-Clifford gates** (Lai, Cheng 2022; Grewal, Iyer, Kretschmer, Liang 2023; Leone, Oliviero, Hamma 2024; Hangleiter, Gullans 2024) | State | Searching by the LWE rule: stabilizer dimension $\geq n-t$, e.g. at most $t$ non-Clifford gates → a Pauli subgroup of size $2^{n-t}$ that stabilizes the state, i.e. the support, then the remainder on $t$ qubits by tomography | Sample: $\mathrm{poly}(n, 2^t)$ | $\mathrm{poly}(n, 2^t)$, polynomial for $t = O(\log n)$ | poly | 🟢 🟢 🟢 up to logarithmic magic; the time budget grows as $2^t$, magic is the hardness dial |
| **Approximate stabilizer support and stabilizer fidelity** (Grewal, Iyer, Kretschmer, Liang 2023) | State | Searching: fidelity $\tau$ with some stabilizer state → the Lagrangian subspace $\mathrm{Weyl}(\vert\phi\rangle)$ of the best stabilizer state, then a stabilizer state witnessing fidelity $\geq F_S - \epsilon$; also: fewer than $n/2$ non-Clifford gates or Haar-random → one bit | Sample: Bell difference sampling, $O(n/(\epsilon^2\tau^4))$ copies; $O(n + \log n/\gamma^2)$ for $\tau \geq \cos^2(\pi/8) + \gamma$; $O(n)$ for the rank test | $\exp(O(n/\tau^4))/\epsilon^2$ via maximal cliques of the commutation graph; $O(n^3 + n^2\log n/\gamma^2)$ above $\cos^2(\pi/8)$, where the closest stabilizer state is unique and $x \in \mathrm{Weyl}(\vert\phi\rangle)$ iff $\langle\psi\vert W_x\vert\psi\rangle^2 > 1/2$ | poly | 🟢 🟢 🟢 above $\cos^2(\pi/8)$, 🟢 🔴 🟢 for small constant $\tau$; an approximate subgroup promise stays searchable because a constant fraction of the samples lies exactly in the subgroup, which is what the LWE instance destroys |
| **Agnostic tomography** (Grewal, Iyer, Kretschmer, Liang 2024; Chen, Gong, Ye, Zhang 2024) | State, mixed | Searching by the LWE rule, agnostic: class $\mathcal{C}$ (stabilizer or stabilizer product states), no promise that $\rho \in \mathcal{C}$ → the Lagrangian subspace of the best candidate, then $\sigma\in\mathcal{C}$ with $F(\rho,\sigma) \geq \max_{\tau\in\mathcal{C}} F(\rho,\tau) - \epsilon$; by task type agnostic identifying | Sample: stabilizer product states $n^{O(\log(2/\tau))}/\epsilon^2$ by Bell difference sampling (Grewal et al.), improved to $n^2(1/\tau)^{O(\log 1/\tau)}/\epsilon^2$; all stabilizer states $n(1/\tau)^{O(\log 1/\tau)} + O(\log^2(1/\tau)/\epsilon^2)$ copies by stabilizer bootstrapping; stabilizer dimension $\geq n-t$ with $n(2^t/\tau)^{O(\log 1/\epsilon)}$; lower bound $\Omega(n/\tau)$ | $O(n^2(n+1/\epsilon^2))(1/\tau)^{O(\log 1/\tau)}$, polynomial for $\tau \geq e^{-c\sqrt{\log n}}$ | poly, a tableau | 🟢 🟢 🟢 for best fidelity $\tau$ down to slightly sub-polynomial; the same algorithm estimates stabilizer fidelity, the first efficient magic estimator; the quasipolynomial continuation of the row above |
| **Stabilizer states from noisy PAC examples** (Gollakota, Liang 2022) | State | Searching under PAC access: stabilizer promise, measurements drawn from a fixed known distribution with one-bit outcomes → a hypothesis of small squared loss, i.e. the stabilizer group; the hard instance is the hidden parity $y$ behind a computational-basis state $\vert y\rangle$, a sign pattern $(-1)^{x\cdot y}$ on a known support | Sample: classical examples $(E, Y)$, the learner does not choose $E$; poly examples suffice statistically | Noiseless: poly by Gaussian elimination (Rocchetto 2018); with classification noise at rate $\eta$ at least as hard as LPN (Cor. 4.12); statistical-query learners need $2^{\Omega(n)}$ queries under uniform parity measurements and $2^{\Omega(n^2)}$ under uniform Pauli measurements (Cor. 4.11, 4.7) | poly | 🟢 🔴 🟢 with noise; the LPN wall reached by a stabilizer class through the access model: with chosen measurements on copies the hard instance is trivial |
| **Quantum juntas** (Chen, Nadimpalli, Yuen 2023) | Unitary | Searching: the unitary acts on $k$ unknown qubits out of $n$ → those $k$ qubits, then the $k$-qubit unitary | Sample on the Choi state: $O(k/\epsilon + 4^k/\epsilon^2)$ uses of $U$, independent of $n$; the junta *test* needs $\tilde O(\sqrt k)$ queries to $U$ and $U^\dagger$ | $\mathrm{poly}(n, 4^k)$ | $O(k\log n)$ plus the $k$-qubit unitary | 🟢 🟢 🟢; junta promise, the support search at the level of qubits; lower bounds $\Omega(\sqrt k)$ and $\Omega(4^k/k)$ nearly match |
| **DNF and heavy Fourier coefficients from quantum examples** (Bshouty, Jackson 1998) | Classical function | Searching: quantum examples $\sum_x \sqrt{D(x)}\,\vert x, f(x)\rangle$ under the uniform distribution → the heavy coefficients of $f$, then a DNF | Sample: Fourier sampling of the example state returns $S$ with probability $\hat f(S)^2$; $\mathrm{poly}(n, 1/\tau)$ examples | poly | poly | 🟢 🟢 🟢; heaviness promise: a heavy Boolean coefficient carries a constant fraction of unit total weight, a displacement coefficient of size $\Theta(1)$ carries $1/d$ of it, which is why direct sampling finds the former and not the latter |
| **$k$-Fourier-sparse Boolean functions from quantum examples** (Arunachalam, Chakraborty, Lee, Paraashar, de Wolf 2021) | Classical function | Searching: sparsity promise, no heaviness promise → the Fourier span from Fourier samples, then $f$ exactly | Sample: $O(k^{1.5}\log^2k)$ uniform quantum examples, independent of $n$, against $\tilde\Theta(nk)$ classical ones; $\Omega(k\log k)$ necessary | poly | $O(k)$ | 🟢 🟢 🟢; sparsity plus unit normalization is heaviness: every nonzero coefficient is a multiple of $2^{1-\lfloor\log k\rfloor}$, so each support point is hit with probability $\Omega(1/k^2)$ per Fourier sample |
| **Heavy Pauli coefficients of a unitary** (Fourier sampling on the Choi state; operator Goldreich–Levin: Montanaro, Osborne 2010) | Unitary | Searching: threshold $\tau$ → all Pauli coefficients of $U$ above $\tau$ | Sample on the Choi state: $O(\tau^{-2}\log(1/\tau\delta))$ Bell samples, since $\sum_P \vert{}u_P\vert{}^2 = 1$ makes every heavy term appear with probability at least $\tau^2$ | poly | $O(\tau^{-2})$ terms | 🟢 🟢 🟢; unit normalization of the spectrum, the operator analogue of Bshouty–Jackson |
| **Low-degree Pauli concentration of QAC⁰ channels** (Nadimpalli, Parham, Vasconcelos, Yuen 2023) | Channel from $n$ qubits to one qubit computed by a depth-$d$ QAC⁰ circuit with $a$ auxiliary qubits, through its Choi state | Searching by a degree promise that follows from depth: Pauli mass beyond degree $k$ is at most $2^{-\Omega(k^{1/d} - a)}$, so the support sits in a dictionary of size $n^{O(k)}$ → the channel to $\ell_2$ spectral error $\epsilon$ | Sample: $n^{\mathrm{polylog}(n)}\log(1/\delta)$ copies of the Choi state for $a = \mathrm{polylog}(n)$ | quasipolynomial | quasipolynomial | 🟢 🟢 🟢 quasipolynomially; the quantum Linial–Mansour–Nisan theorem, conjectured for all polynomial-size QAC⁰, which would put parity outside the class |
| **Heavy Fourier coefficients**: Goldreich–Levin, Kushilevitz–Mansour, sparse FFT; with quantum queries Adcock, Cleve 2002 | Classical function | Searching: threshold $\tau$ → all coefficients above $\tau$ | Query: $\mathrm{poly}(n, 1/\tau)$ resp. $\tilde O(k \log \vert{}V\vert{})$ evaluations at chosen points | poly | $O(k)$ | 🟢 🟢 🟢; query access |
| **Simon's problem, hidden subgroup** | Classical function | Searching: subgroup promise → the hidden subgroup | Query: $O(n)$ superposition queries | $O(n^3)$, Gaussian elimination on Fourier samples | $O(n^2)$ | 🟢 🟢 🟢; the query-side mirror of Montanaro |
| **LWE with superposition queries** (Grilo, Kerenidis, Zijlstra 2019) | Classical function | Searching: noisy linear samples in superposition → the secret $\mathbf{s}$ | Query: poly superposition queries | poly | poly | 🟢 🟢 🟢; the instance that is LWE-hard under sampling |
| **Structure learning of Ising models and Markov random fields from samples** (Bresler 2015; Klivans, Meka 2017) | Classical Gibbs distribution on $p$ spins, interaction graph unknown | Searching: degree or $\ell_1$-width promise → the dependency graph, then the couplings | Sample: $f(d)\log p$ i.i.d. configurations for degree $d$ (Bresler, $f$ doubly exponential); $O(\lambda^2e^{O(\lambda)}\log(n/\rho\epsilon)/\epsilon^4)$ for width $\lambda$, near the Santhanam–Wainwright lower bound (Klivans, Meka); $t$-wise fields $e^{O(t)}e^{O(\lambda t)}\log n/\eta^4$ | $\tilde O(p^2)$ greedy by conditional influence (Bresler); $O(n^2N)$ online multiplicative weights, $n^{O(t)}$ for order $t$ (Klivans, Meka) | $O(dp)$ | 🟢 🟢 🟢; the classical original of Regime 1: a degree promise makes the neighbourhood dictionary polynomial and no correlation decay is needed; $n^{O(t)}$ is tight under sparse parity with noise, the classical mirror of the LPN wall at order $t$ |
| **Hamiltonian structure learning from real-time evolution** (Bakshi, Liu, Moitra, Tang, FOCS 2024) | Hamiltonian | Searching: $k$-locality promise, interaction terms *not* given → which of the $n^{O(k)}$ candidate terms are present, and their coefficients | Query to the dynamics $e^{-iHt}$: Heisenberg-limited total evolution time, $O(\log n/\epsilon)$ | poly | poly | 🟢 🟢 🟢; locality promise with unknown geometry; the searching counterpart of Heisenberg-limited coefficient learning in the estimating table |
| **Heisenberg-limited learning without short-time control** (Shin, Lee, Oh 2026) | Hamiltonian, $m$-sparse in the Pauli basis, support unknown | Searching: sparsity promise, support *not* given → the $m$ terms present and their coefficients; the continuation of the row above on the access axis | Query to $e^{-iHt}$ with every query of duration at least a fixed constant $T$: $t_{\mathrm{tot}} = \tilde O(\min\{4^m T^3/\epsilon, 4^m T/\epsilon^2\})$, polynomial for $m = O(\log n)$; for $m = \mathrm{poly}(n)$ a tradeoff $t_{\mathrm{tot}} = \tilde O(m^{K+2}T/\epsilon)$ at $T = \Theta(m^{-1/K})$ | poly | poly | 🟢 🟢 🟢 for logarithmic sparsity; short Trotter steps are rewritten as long evolutions plus a learned correction generator; resolves the open problem of Bakshi et al. on time resolution |
| **Sparse Pauli noise** (Harper, Yu, Flammia 2021) | Pauli channel with $s$-sparse error rates | Searching: sparsity promise → the $s$ Pauli errors and their rates, $\Vert\hat p - p\Vert_\infty \leq 2\xi/\sqrt{2^n}$ | Query: $O(sn)$ eigenvalue queries, each a randomized-benchmarking-style Clifford experiment on a chosen stabilizer group; $O(n^2/\xi^2)$ measurements at eigenvalue noise $\xi$ | $O(sn^2)$ classical: subsample onto $2^n$ bins, alias with $2n+1$ offsets, peel | $O(s)$ | 🟢 🟢 🟢; the sparse Walsh–Hadamard algorithm ported to Paulis; compressed sensing would need $O(s\log 4^n)$ measurements but $\mathrm{poly}(4^n)$ time, and the chosen stabilizer groups are the query access that makes localization sublinear |

## Searching protocols

The observables are the output. Two families: structure learning from measurement data on quantum states, and the older Fourier-sampling family on quantum examples of classical functions, which shows what a favourable normalization buys.

## Structure learning (observables as output)

**Task inversion:** First *find* the few observables that carry the support of a sparse Pauli/displacement spectrum, then estimate their values (first the edges, then the weights, as in learning graphical models). Sampling is the easy half: Bell sampling concentrates the draws on the support. **Decoding is the hard half:** Turning i.i.d. samples into the support is sparse recovery *without choosable queries*, generically cryptographically hard (LWE-type). Subgroup/stabilizer symmetries are the tractable exception.

* **Montanaro (2017):** Stabilizer states from $O(n)$ Bell samples via linear algebra.
* **Grewal, Iyer, Kretschmer, Liang (2023):** Bell difference sampling, states with few non-Clifford gates.
* **Grewal, Iyer, Kretschmer, Liang (2023, arXiv:2304.13915):** The approximate-subgroup case. A stabilizer state witnessing fidelity $F_S - \epsilon$ from $O(n/(\epsilon^2\tau^4))$ Bell difference samples in time $\exp(O(n/\tau^4))$, polynomial above $\cos^2(\pi/8)$, where the closest stabilizer state is unique; $n/2$ non-Clifford gates are necessary for pseudorandom states, by a rank test on $O(n)$ samples; duality $\sum_{a\in T}q_\psi(a) = \vert T\vert\sum_{x\in T^\perp}p_\psi(x)^2$ between a subspace and its commutant.
* **Grewal, Iyer, Kretschmer, Liang (2024) / Chen, Gong, Ye, Zhang (2024):** Agnostic tomography, placed here rather than under identifying by the LWE rule. The best stabilizer product state from $n^{O(\log(2/\tau))}/\epsilon^2$ copies by Bell difference sampling, improved to $n^2(1/\tau)^{O(\log 1/\tau)}/\epsilon^2$; the best stabilizer state overall by stabilizer bootstrapping from $n(1/\tau)^{O(\log 1/\tau)} + O(\log^2(1/\tau)/\epsilon^2)$ copies, polynomial for $\tau \geq e^{-c\sqrt{\log n}}$, with a lower bound of $\Omega(n/\tau)$; the same algorithm estimates the stabilizer fidelity.
* **Allcock, Doriguello, Ivanyos, Santha (2024):** The qudit case, $d = p > 2$. Bell difference sampling mixes shift and clock parts through the involution $J(v,w) = (-v,w)$ and no longer returns the stabilizer group; the group is learned instead from $O(n)$ copies in time $O(n^4)$ by computational-basis samples of the affine support and a hidden-polynomial step for the quadratic phase, or by Bell sampling on $\vert S\rangle\vert S^*\rangle$ for any $d$. Clifford circuits with $O(\log n/\log p)$ non-Clifford gates cannot prepare pseudorandom qudit states, via the stabilizer test of Gross, Nezami, Walter.
* **Gollakota, Liang (Quantum 2022):** Stabilizer states in Aaronson's PAC model with noise. Under uniform parity measurements $E_x = (I + Z^{x_1}\otimes\cdots\otimes Z^{x_n})/2$ a computational-basis state $\vert y\rangle$ answers with the parity $x\cdot y$, so learning stabilizer states with classification noise is at least as hard as LPN; statistical-query learners need $2^{\Omega(n)}$ queries there and $2^{\Omega(n^2)}$ under uniform Pauli measurements, while tolerating classification noise and global depolarizing noise by construction. The noiseless learner (Rocchetto 2018) is Gaussian elimination and not SQ, the same split as for parities.
* **Harper, Yu, Flammia (PRX Quantum 2021):** Sparse Pauli noise. The $s$ nonzero error rates of a Pauli channel from $O(sn)$ eigenvalue queries on chosen stabilizer groups and $O(sn^2)$ classical time, by subsampling, aliasing, and peeling; the sparse Walsh–Hadamard transform on the channel side, efficient because the experimenter chooses the sampling positions.
* **Bresler (STOC 2015) / Klivans, Meka (FOCS 2017):** The classical original of Regime 1. The graph of an Ising model on $p$ nodes of degree $d$ from $f(d)\log p$ samples in time $\tilde O(p^2)$ without correlation decay (Bresler, by greedy conditional influence); near-optimal samples in the $\ell_1$-width and time $O(n^2N)$ by multiplicative weights, $n^{O(t)}$ for $t$-wise fields, tight under sparse parity with noise (Klivans, Meka, the Sparsitron).
* **Nadimpalli, Parham, Vasconcelos, Yuen (2023):** The Pauli spectrum of QAC⁰, defined on the Choi state of the circuit with all but the target qubit traced out, concentrates on degree $\leq k$ up to mass $2^{-\Omega(k^{1/d}-a)}$; a degree dictionary that follows from depth, and quasipolynomial learning of such channels. The quantum Linial–Mansour–Nisan theorem, proved for few auxiliary qubits and conjectured in general.
* **Hangleiter, Gullans (PRL 2024):** Bell sampling as a universal diagnostic framework.
* **Chen, Nadimpalli, Yuen (SODA 2023):** Quantum juntas, the support search at the level of qubits, logarithmic in $n$.
* **Bakshi, Liu, Moitra, Tang (FOCS 2024):** Hamiltonian structure learning from real-time evolution. Only locality is promised, the interaction terms are not given, and the total evolution time stays Heisenberg-limited. The line between this and coefficient learning: for a geometrically local Hamiltonian on a known lattice, all local terms form a dictionary of bounded degree, and coefficient learning returns the structure as a by-product. Structure learning proper begins when the geometry is unknown, $k$-body terms among arbitrary qubits; the guarantees of the coefficient algorithms depend on the degree of the interaction graph and no longer apply directly. The coefficient papers with known terms (Anshu et al. 2021; Haah, Kothari, Tang 2022; Bakshi, Liu, Moitra, Tang, STOC 2024; Gu, Cincio, Coles 2024) are estimating protocols and sit in the dynamics subsection. Shin, Lee, Oh (2026) resolve the paper's open problem on time resolution: Heisenberg-limited learning of $m$-sparse Hamiltonians with every query of duration at least a fixed constant $T$, polynomial for $m = O(\log n)$; see the next row of the searching table.
* **Bshouty, Jackson (1998):** DNF from quantum examples by Fourier sampling, the sample-access case in which heavy coefficients are found without queries.
* **Adcock, Cleve (2002) / Montanaro, Osborne (2010):** Quantum Goldreich–Levin, for Boolean functions under quantum queries and for the Pauli spectrum of operators. For unitaries the heavy terms are already found by Bell sampling on the Choi state, a sample-access route, because the spectrum is unit-normalized; see the normalization paragraph below.

**Where Bell difference sampling comes from.** The distribution behind stabilizer learning, $p(x) \propto \sum_y \hat p_\psi(y)\,\hat p_\psi(x+y)$ over $\mathbb{F}_2^{2n}$ with $\hat p_\psi(x) = 2^{-n}|\langle\psi|P_x|\psi\rangle|^2$ the **characteristic distribution**, is a corollary of the **Schur–Weyl duality for the Clifford group** (Gross, Nezami, Walter, Commun. Math. Phys. 2021): the commutant of $U^{\otimes 4}$ over Cliffords is spanned by stabilizer codes, which is why four copies (two Bell pairs, differenced) expose the stabilizer group. This is the group-theoretic reason "subgroup/stabilizer symmetries are the tractable exception": the support of $\hat p_\psi$ for a stabilizer state is a Lagrangian subspace, and linear algebra over $\mathbb{F}_2$ recovers a subspace from $O(n)$ random elements.

**Why Fourier sampling finds heavy coefficients of functions and unitaries, and Bell sampling does not find heavy displacement coefficients of states.** For a pure state the Bell distribution on $\rho\otimes\rho^*$ is $P(z) = \vert{}y_z\vert{}^2/d$, the squared spectrum itself: the characteristic distribution of a pure state is its own symplectic Fourier transform (Gross, Nezami, Walter 2021). One might hope to read the top-$k$ off the histogram of outcomes. But $\sum_z \vert{}y_z\vert{}^2 = d$, so a coefficient of size $\Theta(1)$ has probability $\Theta(1/d)$ and is invisible in $\mathrm{poly}(n)$ shots. The character mean $\sum_z P(z)\chi_u(z)$ uses every shot for every coefficient and reaches $\vert{}y_u\vert{}^2$ with $O(1/\epsilon^4)$ shots; that is why the Fourier step is essential and why localization remains a search over $d^2$ addresses. In the Boolean case the normalization is $\sum_S \hat f(S)^2 = 1$, a heavy coefficient has probability $\tau^2$, and Fourier sampling returns it directly. That normalization is the whole difference between Bshouty–Jackson and the LWE wall. Unitaries sit on the Boolean side. For $U = \sum_P u_P P$ the coefficients satisfy $\sum_P \vert{}u_P\vert{}^2 = 1$, and the Choi state $(U\otimes I)\vert\Phi\rangle = \sum_P u_P (P\otimes I)\vert\Phi\rangle$ is written in the Bell basis with exactly these amplitudes. One Bell measurement per use of $U$ returns $P$ with probability $\vert{}u_P\vert{}^2$, so all coefficients above $\tau$ appear within $O(\tau^{-2}\log(1/\tau\delta))$ shots, from sample access alone. A pure state $\rho$ has the same Bell-basis picture with amplitudes $y_z/\sqrt d$, and the extra $1/\sqrt d$ is the whole problem. The object therefore matters for hardness through the normalization of its spectrum, not through being a state or a process.

## Where the wall begins: four refinements

The searching column has its endpoints; these four statements fix the shape of the region between them. Each one is a consequence of results already in the tables, stated here because the tables cannot carry it.

**1. The noise model separates "agnostically easy" from "LWE-hard".** The LWE instance is itself a subgroup instance: its support lies on a hidden line, the very structure that Montanaro's Gaussian elimination recovers. It is hard because every sample lies next to the line by $e_i$. The approximate-stabilizer results say the opposite for a different noise: if a constant fraction of the Bell difference samples lies exactly in the subgroup, with probability at least $\tau^4$ for stabilizer fidelity $\tau$, the support is recoverable in time $\exp(O(n/\tau^4))$ (Grewal, Iyer, Kretschmer, Liang 2023), polynomial above $\cos^2(\pi/8)$, and quasipolynomial for any $\tau$ by stabilizer bootstrapping (Chen, Gong, Ye, Zhang 2024). In coding terms: Goldreich–Levin is local list decoding of the Hadamard code with queries; stabilizer bootstrapping is list decoding from samples under erasure-type noise, where clean samples exist and only have to be identified; LPN and LWE are decoding of random linear codes under additive noise on every sample. The three are the map between Regime 2 and the wall, and they tell the instance generator which perturbation makes an instance hard: not a fraction of corrupted samples, but a small error on all of them.

**2. What "sparse" has to mean.** For a pure state $\sum_z\vert y_z\vert^2 = d$. A spectrum with exactly $k$ nonzero coefficients has $\vert y\vert^2 = d/k$ on each, a Bell draw on $\rho\otimes\rho^*$ hits the support with probability $1/k$, and coupon collecting localizes it in $O(k\log k)$ shots with no decoder at all; for a mixed state the mass is $d\,\mathrm{Tr}\rho^2$ and the argument survives as long as the purity is not tiny. The Boolean case says the same in stronger form: a $k$-Fourier-sparse Boolean function has every nonzero coefficient a multiple of $2^{1-\lfloor\log k\rfloor}$, so sparsity under unit normalization is heaviness and Fourier sampling finds the support (Arunachalam, Chakraborty, Lee, Paraashar, de Wolf 2021). The hard regime of this project is therefore not "$k$-sparse" but "$k$ coefficients of size $\Theta(1)$ over a flat remainder that carries the mass $d - k$". The remainder's mass and the purity are the dials of the instance ladder, and the promise in the first row of the table is to be read this way.

**3. The scale of the time wall, and the query cell for states.** Brute force over the $d^2$ addresses costs $O(d^2N)$, polynomial in $d$; "LWE-hard" means no algorithm in $\mathrm{poly}(\log d)$. The classical mirror is compressed sensing with random Fourier samples: with $O(k\,\mathrm{polylog}\,d)$ random rows of the Fourier matrix the restricted isometry property holds (Candès, Tao 2006; Rudelson, Vershynin 2008) and $\ell_1$ minimization recovers a $k$-sparse vector in time $\mathrm{poly}(d)$, while sublinear time needs chosen sampling positions, which is what sparse FFT uses and what the peeling decoder of Harper, Yu, Flammia uses on the channel side through chosen stabilizer groups. A Bell record delivers random positions; that is the same trichotomy as Theorem 5 of King, Wan, McClean (signs in $\mathrm{poly}(d)$) against the wall. The query cell of the quadrant is populated for functions and for Pauli channels; for a state with a preparation oracle it is not: amplitude amplification on the coherent Bell measurement finds a top-$k$ address in $O(\sqrt{d/k})$ calls, amplitude estimation makes each single address cheap at the Heisenberg rate, the LWE instance falls to superposition queries (Grilo, Kerenidis, Zijlstra 2019), and no general $\mathrm{poly}(n)$ localizer with queries is known. Rung 3 of the access ladder breaks the LWE endpoint, not the corner.

**4. The hard endpoint of the cyclic basis.** A single $\mathbb{Z}_d$ is an abelian group, and hidden shift, hidden number, and discrete logarithm inside it are abelian hidden-subgroup instances, easy for a quantum decoder by period finding. A hard endpoint in the cyclic basis therefore has to survive Shor. The candidate from the literature is the dihedral hidden-shift problem over $\mathbb{Z}_N$: Kuperberg's sieve solves it in $2^{O(\sqrt{\log N})}$ (2005), subexponential in $\log d$, and Regev (2004) reduces unique-SVP to it, so it lives in the same lattice world as LWE. The precise form of open question (2) is then: is localization in the cyclic displacement spectrum equivalent to a dihedral coset problem? If so the endpoint is neither $\mathrm{poly}(\log d)$ nor $\mathrm{poly}(d)$ but Kuperberg's exponent.

## The repaired success criterion and the three failure modes

The refinements above and the LWE row show that sparsity is not a success criterion. The displacement instance behind `thm:lwe-displacement` is sparse, its peaks lie far above the shot-noise floor, it is available from conjugate pairs, and its support still cannot be located in polynomial time. The central conjecture therefore needs a third condition, and that condition is computational rather than statistical (mentor feedback, Block C).

**Three conditions.** The pipeline finds the peaks efficiently when all three hold:

| Condition | Budget it secures | Where the tables supply it | Without it |
| --- | --- | --- | --- |
| **(i) Conjugate Bell access:** measurements on $\rho\otimes\rho^*$ | Copies: the sample boundary, rung 2 of the access ladder | King, Wan, McClean 2024, Thm. 2: all $d^2$ magnitudes from $O(\log d/\epsilon^4)$ copies at two-copy memory; free for real states, and not needed on qubits, where $P\otimes P$ already commute | $\Omega(\sqrt d/(K^2\epsilon^2))$ measurements on $\rho^{\otimes K}$ (Thm. 1); $\Omega(d/\epsilon^2)$ with single copies, even of both $\rho$ and $\rho^*$ (Thm. 3); on qudits, Bell sampling on $\rho\otimes\rho$ can be uniform (Allcock et al. 2024) |
| **(ii) Signal-to-noise and margin:** the dominant amplitudes lie above the shot-noise floor and stand out from the background | Copies: statistical detectability of each peak and of the top-$k$ boundary | Hoeffding plus a union bound over the $d^2$ addresses; a gap $g$ between the $k$-th and the $(k+1)$-th magnitude costs $N = O(g^{-2}\log(d^2/\delta))$ (the quadrant in the appendix); condition (C2a) in the table of the next subsection | Peaks sink below $1/\sqrt N$, or the top-$k$ boundary is not resolved |
| **(iii) Structural decodability:** the support comes from a family that is computationally decodable under the *actual* sample-access model | Time: the computational boundary | Polynomial dictionaries and local observables (Regime 1: Bresler; Klivans, Meka; Bakshi, Liu, Moitra, Tang; the degree promise of QAC⁰); subgroups and stabilizer groups (Regime 2: Montanaro; Allcock et al. on qudits; approximate subgroups by Grewal, Iyer, Kretschmer, Liang and by stabilizer bootstrapping); factorized spectra over coprime factors (Regime 3, the best-first heap) | The LWE displacement instance and LWE from samples; pseudomagic states; LPN as the classical mirror |

**The logical form.** The LWE instance satisfies (i) and (ii) and is still hard, so the two together are not sufficient. That is the content of Block B, and it is why (iii) is needed. With an explicit list of families, (iii) turns the criterion into a sufficiency theorem for a promise problem, the form stated in the positioning section. It is not a proven necessary condition:
* (i) is not needed on qubits or for real states.
* The approximate-subgroup rows show that the list of decodable families is open-ended.
* Under query access (rung 3) the access itself replaces (iii) for the LWE endpoint (Grilo, Kerenidis, Zijlstra 2019).

Without an explicit list, "decodable under the access model" only restates the conclusion. The conjecture of this project is then a membership claim: the uniformly random top-$k$ supports of the instance generator belong to the decodable side of (iii), although they are none of the three listed families.

**Three failure modes.** Instead of one undifferentiated error, the failures separate cleanly, each with its own kind of bound:

| Failure mode | Question | Kind of bound | Instances in the tables |
| --- | --- | --- | --- |
| **Statistical detectability** | Is the signal large enough compared with the number of samples $N$? | Information-theoretic and unconditional: Holevo and packing, the tree method, Hoeffding | Without the conjugate: King, Wan, McClean, Thms. 1 and 3; peaks below the noise floor: (C2a) |
| **Computational search** | Can the frequencies be found in $\mathrm{poly}(n)$ time, or are they cryptographically hidden as in LWE? | Computational and conditional: LWE, LPN, one-way functions | The LWE displacement instance and LWE from samples; pseudomagic states; bounded gate complexity. Escapes: the promises of (iii), or query access |
| **Identifiability at ties and plateaus** | Is "the top-$k$" a well-defined answer? | Neither: a property of the target, fixed by the output format | Stabilizer plateaus, $2^n$ equal coefficients (the linear cluster state); the mirror pair $(q,p)\leftrightarrow(q,-p)$ of real states, an exact tie for `defn:validtopk`; the threshold $\cos^2(\pi/8)$ above which the nearest stabilizer state is unique (Grewal, Iyer, Kretschmer, Liang 2023) |

A tie breaks the uniqueness of a ranking but not the physical localization of the subspace. Montanaro's decoder returns the stabilizer group, the whole plateau, and never ranks inside it. For such targets the output is a level set or a subspace, and success is measured on that set; top-$k$ accuracy with $k$ inside a plateau only measures an arbitrary tie-break.

**Relation to the two ways to fail.** The appendix separates "hypothesis too large" (memory) from "search too hard" (time). The trichotomy lives inside the sparse-list representation. Statistical detectability is the copies budget, computational search is "search too hard", and identifiability belongs to no budget because it concerns the definition of the output. The representation failure is orthogonal and is already solved by the sparse list of $O(k\log d)$ bits.

**The three blocks of the feedback in one sentence each.** A explains why standard signal processing does not carry over one-to-one to quantum samples. B shows through LWE that a sparse spectrum can still be hopelessly hard to search. C draws the consequence and names the conditions under which the pipeline provably works.

## Which spectrum? The Heisenberg–Weyl restriction and the conjugate

"A promise about the spectrum" presupposes an operator basis in which the spectrum is written. Bell sampling fixes that basis, and the conjugate pair fixes which states can be fed into it. Both restrictions come from the conjugate-pairs paper (King, Wan, McClean 2024, in the folder as 2403.03469).

**The trick and its limit.** The displacement operators $D_{q,p}$ do not commute, so no single-copy measurement reads them all at once. On two registers the products $D_{q,p}\otimes D_{-q,p}$ do commute: exchanging two of them picks up the phase $\omega^{qp'-q'p}$ on the first register and the inverse phase on the second, and the two cancel. All $d^2$ products are therefore diagonal in one basis, the generalized Bell basis, and $\mathrm{Tr}[(D_{q,p}\otimes D_{-q,p})(\rho\otimes\rho^*)] = y_{q,p}^2$. Theorem 4 of the paper shows how far this goes. If $U\otimes\tilde U$ and $V\otimes\tilde V$ commute while $U$ and $V$ do not, the commutator $UVU^{-1}V^{-1}$ must be a scalar $\omega\mathbb{1}$, because only scalars pass through a tensor factor. Such pairs generate a representation of the discrete Heisenberg group, and every irreducible representation of that group is a set of displacement operators in some basis. "Heisenberg–Weyl" is therefore not one basis but one algebraic structure, realized by the single cyclic qudit $\mathbb{Z}_d$, by tensor products of qudits, by $n$-qubit Paulis ($d = 2$ per factor), and in the limit by bosonic displacements. The authors call the result evidence: it rules out this tensor-extension trick for other operator families, not every conceivable two-copy primitive.

**A restriction on the question, not on the state.** The displacement operators form a complete operator basis, so *every* state has a displacement spectrum, and with $\rho\otimes\rho^*$ all $d^2$ squared magnitudes of *every* state are available from $O(\log d/\epsilon^4)$ copies. Searching is sample-efficient under three conditions:

| Condition | If it fails |
| --- | --- |
| The spectrum is taken in a Heisenberg–Weyl basis | No two-copy primitive is known. General shadow tomography stays sample-efficient for any list of $M$ observables, $\tilde O(\log^2 M\,\log d/\epsilon^4)$ copies (Bădescu, O'Donnell 2021), but needs large entangled measurements and exponential time. |
| The conjugate copy is available ($d > 2$) | With $K$ copies of $\rho$ held at once, $\Omega(\sqrt d/(K^2\epsilon^2))$ measurements for $d$ prime (Thm. 1 of the paper); with single copies $\Omega(d/\epsilon^2)$, even when single copies of $\rho^*$ are allowed (Thm. 3). |
| The heavy coefficients are at least $\epsilon$, with $1/\epsilon$ polynomial | They sink below the noise floor, condition (C2a). |

Sample efficiency secures neither the signs nor the search. Theorem 5 of the paper learns all signs from $O(\log d/\epsilon^4)$ copies but in time $\mathrm{poly}(d)$, exponential in $n$, which is why Phase 2 of the own protocol exists. The time of localization is the LWE question of this section.

*Outside Heisenberg–Weyl.* Coefficients in another operator basis, for example the Gell-Mann matrices of $\mathfrak{su}(d)$, are linear combinations of displacement coefficients. The squared magnitudes alone do not determine them, because the combination needs the phases. That is the practical content of the restriction: the Bell record answers questions about the Weyl spectrum and about nothing else directly.

**The conjugate: real with respect to a basis.** A state is real with respect to an orthonormal basis $\{\vert j\rangle\}$ when all its matrix elements $\langle j\vert\rho\vert k\rangle$ are real numbers. Then $\rho^* = \rho$, and two identical copies from the same source already form the pair $\rho\otimes\rho^*$; no conjugation is needed.
* *The basis matters.* Complex conjugation is defined only relative to a basis, which is one reason it is not a physical operation. The relevant basis is the one in which $X$ and $Z$ are defined, since the generalized Bell basis is built from it.
* *In general $\rho^*$ is expensive.* From copies of an unknown $\rho$, efficient conjugation would locate a real state among random ones faster than the proven $\Omega(\sqrt d)$ lower bound; from a black-box preparation unitary $U$, implementing $U^*$ takes $d-1$ calls (both arguments in Appendix D of the paper).
* *Where it is free.* Real Hamiltonians, which covers chemistry without magnetic fields and without spin-orbit coupling, XZ-type spin models, and real-space Hamiltonians without magnetic fields. Their Gibbs states are real, and their ground states can be chosen real. The second source is a known circuit: conjugating every gate prepares $\rho^*$ (rung 3 of the access ladder).
* *Time reversal and reality are not the same.* For spinless systems time reversal is complex conjugation, and time-reversal symmetry guarantees a real basis. For spin-1/2 systems with spin-orbit coupling, time reversal squares to $-1$ (Kramers), and a time-reversal-symmetric Hamiltonian need not be real in any basis.
* *Qubits need no conjugate.* For Paulis the braiding phases are $\pm 1$, so $P\otimes P$ already commute, and two identical copies give $\vert\mathrm{Tr}(P\rho)\vert^2$ (Huang et al. 2022). The conjugate requirement is specific to $d > 2$, where $\omega \neq \omega^{-1}$.

**Two Heisenberg–Weyl structures on the same Hilbert space.** For $d = 2^n$ both of the following are available, and they give different spectra of the same state:

| | Cyclic basis $\mathbb{Z}_d$ | Tensor-product basis |
| --- | --- | --- |
| System | one $d$-level qudit | $n$ qudits of dimension $q$ ($d = q^n$); Paulis for $q = 2$ |
| Generators | one pair: $X\vert j\rangle = \vert j+1\rangle$, $Z\vert j\rangle = \omega^j\vert j\rangle$ | one pair $(X_i, Z_i)$ per factor |
| Phase space | the torus $\mathbb{Z}_d\times\mathbb{Z}_d$ | $\mathbb{Z}_q^{2n}$, for qubits $\mathbb{F}_2^{2n}$ |
| Physical picture | discrete position and momentum of one particle or mode on a ring | registers of spins or qubits, quantum circuits |
| Hardness of localization | open (Q1); the naive transfer is the hidden number problem, against which lattice attacks exist | LWE-hard for prime $q$ under the LWE assumption (`thm:lwe-displacement`); for qubits the same construction rests on LPN |

This project uses the cyclic basis because its indices are the physical displacements in a two-dimensional phase space, the natural coordinates for a discretized mode, a vibrational coordinate, or a real-space sensor array.

**Sparsity is relative to the basis.** Searching presupposes a few heavy coefficients. For a pure state $\sum_{q,p}\vert y_{q,p}\vert^2 = d$, so a perfectly flat spectrum has $\vert y_{q,p}\vert = 1/\sqrt d$ everywhere, and a coefficient of size $\Theta(1)$ stands out. Which states have such coefficients depends on the basis. Numbers for $n = 6$, $d = 64$, with the participation number $(\sum\vert y\vert^2)^2/\sum\vert y\vert^4$ as the effective count of coefficients out of $4096$:
* *Linear cluster state.* In the Pauli basis exactly $64$ coefficients of magnitude one, the stabilizer group; in the cyclic basis about $776$ effective coefficients. It is a stabilizer object: a plateau of $2^n$ equal entries in its own basis, not a top-$k$ object.
* *Discrete Gaussian and coherent states.* The characteristic function is concentrated at the origin: about $128$ effective coefficients in the cyclic basis, largest at $(q,p) = (0,0)$, and identical for the Gaussian and every displaced copy of it. A displacement multiplies each $y_u$ by a phase and leaves the magnitudes unchanged. In the Pauli basis the count is about $100$ for the centred Gaussian and about $218$ after the displacement used here. Neither basis makes these states $k$-sparse. ⚠️ The Wigner function of a coherent state peaks at its phase-space position $(q_0, p_0)$; the displacement spectrum, which is the symplectic Fourier transform of the Wigner function, does not. The position of a coherent state is phase information, the object of Stufe 1 of the instance ladder, not a searching object.

**Consequence for the instance generator.** The harmonic base Hamiltonian is real, but an injection $D_{q,p}+D_{q,p}^\dagger$ with $q\neq0$ and $p\neq0$ is complex, so the generated ground and Gibbs states are complex, and `np.conjugate(rho)` in the simulation stands for white-box access. A real family needs symmetric injections, $D_{q,p}+D_{q,-p}+\mathrm{h.c.}$, since $D_{q,p}^* = D_{q,-p}$. The price is a symmetric support: for real $\rho$, $y_{q,-p} = \overline{y_{q,p}}$, and together with Hermiticity the magnitudes $\vert y_{\pm q,\pm p}\vert$ coincide exactly (checked at $d = 7$, $(q,p) = (2,3)$: all equal to $0.5876$; the complex state from a single injection gives $0.41$ and $0.19$ at $(2,\pm3)$). The conjugate deduplication handles $(q,p)\leftrightarrow(-q,-p)$ only, so the mirror pair $(q,p)\leftrightarrow(q,-p)$ arrives as an exact tie, an identifiability case for `defn:validtopk`. Real states are therefore a natural step of their own on the instance ladder: conjugate access for free, paid for with a symmetric support.

## Quantum PAC learning and quantum examples

The oldest access model in the field: the learner receives copies of the example state $\sum_x \sqrt{D(x)}\,\vert x, f(x)\rangle$ of a classical function $f$.

* **Bshouty, Jackson (SIAM J. Comput. 1998):** DNF learnable under the uniform distribution from quantum examples, by Fourier sampling; the first quantum learning advantage in time.
* **Servedio, Gortler (SIAM J. Comput. 2004) / Atıcı, Servedio (2005):** Equivalences and separations between quantum and classical learnability; polynomial gaps in samples, exponential gaps in time under cryptographic assumptions.
* **Aaronson (Proc. R. Soc. A 2007):** Learnability of quantum states: $O(n)$ samples to predict most measurements. **Rocchetto (2018):** stabilizer states are efficiently PAC-learnable. **Gollakota, Liang (Quantum 2022):** with classification noise at least as hard as LPN; statistical-query learners need $2^{\Omega(n)}$ queries.
* **Arunachalam, de Wolf (SIGACT 2017; JMLR 2018):** Survey, and the optimal bound $\Theta(d_{\mathrm{VC}}/\epsilon + \log(1/\delta)/\epsilon)$: quantum examples buy nothing in samples for classical concept classes.
* **Grilo, Kerenidis, Zijlstra (PRA 2019):** LWE is easy with quantum samples, via Bernstein–Vazirani on the example state.
* **Arunachalam, Chakraborty, Lee, Paraashar, de Wolf (ICALP 2019; Quantum 2021):** $k$-Fourier-sparse Boolean functions from $O(k^{1.5}\log^2 k)$ uniform quantum examples, independent of $n$, against $\tilde\Theta(nk)$ classical ones; $\Omega(k\log k)$ necessary. Sparsity under unit normalization is heaviness, which is why sample access suffices here and not for states.
* **Arunachalam, Grilo, Yuen (2020):** Quantum statistical queries, a rung below samples on the access ladder: the learner sees only expectation values to a tolerance.

**Where there is provably no advantage.** For PAC learning a *classical* concept class from quantum examples $\sum_x \sqrt{D(x)}\,|x, c(x)\rangle$, Arunachalam–de Wolf (JMLR 2018) showed the sample complexity is $\Theta(d_{\mathrm{VC}}/\epsilon + \log(1/\delta)/\epsilon)$, identical to the classical bound up to constants. Quantum examples buy nothing in samples for classical targets; the advantages in this document all sit in the bottom row or in *time*, never in PAC sample complexity for classical functions.

<br>

# Searching (Papers)

Summaries of the key papers on the task type **searching**: the observables are the output. Given are copies of a state, uses of a unitary or of a dynamics, and a promise about the structure. Returned is the support, i.e. which addresses carry the weight, and then their values.

Every summary follows the same structure: placement in the tables, problem, key results, method, significance, relation to this project, limitations and open questions, questions for further study. The status glyphs read as in the appendix ("Reading the tables"), in the order copies · time · memory.

## Overview

| Paper | Object | What is searched | Access | Cost | Status | Promise |
| --- | --- | --- | --- | --- | --- | --- |
| Montanaro 2017 | State | the stabilizer group, i.e. the support of the Pauli spectrum | Sample, Bell measurement on two copies | $O(n)$ copies, $O(n^3)$ time | 🟢 🟢 🟢 | stabilizer state |
| Grewal, Iyer, Kretschmer, Liang 2023 | State | an approximate stabilizer group of dimension $n-t$, then the rest by tomography | Sample, two copies or single copies | $\mathrm{poly}(n, 2^t, 1/\epsilon)$ | 🟢 🟢 🟢 up to $t = O(\log n)$ | stabilizer dimension $\geq n-t$ |
| Hangleiter, Gullans 2024 | State from a circuit | stabilizer nullity, depth, fidelity, and the Clifford+T description | Sample, Bell measurement on two copies | $O(n/\epsilon)$ Bell samples plus $O(2^t/\epsilon^2)$ for the rest | 🟢 🟢 🟢 up to $t = O(\log n)$ | low T-count |
| Montanaro, Osborne 2010 | Unitary with $f^2 = I$ | all Pauli coefficients above a threshold $\gamma$ | Query, $f$ and $f^\dagger$ | $\mathrm{poly}(n, 1/\gamma)$ | 🟢 🟢 🟢 | none, the normalization $\sum_s \hat f_s^2 = 1$ suffices |
| Chen, Nadimpalli, Yuen 2023 | Unitary | the $k$ relevant qubits, then the $k$-qubit unitary | Sample on the Choi state, test with queries to $U, U^\dagger$ | $O(k/\epsilon + 4^k/\epsilon^2)$, independent of $n$ | 🟢 🟢 🟢 | $k$-junta |
| Bakshi, Liu, Moitra, Tang 2024 | Hamiltonian | which of the $n^{O(K)}$ local terms are present, and their coefficients | Query to the dynamics $e^{-iHt}$ | $t_{\mathrm{total}} = O(\log(n)/\epsilon)$, $\tilde O(n^2)$ classical | 🟢 🟢 🟢 | $K$-locality with bounded local norm |
| Shin, Lee, Oh 2026 | Hamiltonian | support and coefficients at sparsity $m$, without short-time access | Query to $e^{-iHt}$, only for $t \geq T$ | $t_{\mathrm{tot}} = \tilde O(4^m T^3/\epsilon)$, poly for $m = O(\log n)$ | 🟢 🟢 🟢 | sparsity $m$ in the Pauli basis |
| Grewal, Iyer, Kretschmer, Liang 2023 (arXiv:2304.13915) | State with stabilizer fidelity $\tau$ | the Lagrangian subspace of the best stabilizer state, then the state; pseudorandomness needs $n/2$ non-Clifford gates | Sample, Bell difference sampling | $O(n/(\epsilon^2\tau^4))$ copies, $\exp(O(n/\tau^4))/\epsilon^2$ time; poly above $\cos^2(\pi/8)$ | 🟢 🟢 🟢 above $\cos^2(\pi/8)$, otherwise 🟢 🔴 🟢 | approximate subgroup |
| Grewal, Iyer, Kretschmer, Liang 2024 (stabilizer product states) | Mixed state | the best stabilizer product state, agnostic | Sample, Bell difference sampling plus single copies | $n^{O(\log(2/\tau))}/\epsilon^2$ | 🟢 🟢 🟢 for constant $\tau$ | none; $\tau$ is the best fidelity in the class |
| Chen, Gong, Ye, Zhang 2024 (stabilizer bootstrapping) | Mixed state | the best stabilizer state, agnostic; stabilizer fidelity | Sample, single- and two-copy measurements | $n(1/\tau)^{O(\log 1/\tau)} + O(\log^2(1/\tau)/\epsilon^2)$ copies, time $O(n^2(n+1/\epsilon^2))(1/\tau)^{O(\log 1/\tau)}$ | 🟢 🟢 🟢 for $\tau\geq e^{-c\sqrt{\log n}}$ | none; lower bound $\Omega(n/\tau)$ copies |
| Allcock, Doriguello, Ivanyos, Santha 2024 | Qudit stabilizer state, $d = p > 2$ prime | the stabilizer group, where Bell difference sampling only yields $\mathrm{col}(V)\times\mathrm{col}(W)$; Haar versus stabilizer fidelity | Sample; computational basis plus a coherent step on three copies, or Bell measurement on $\vert S\rangle\vert S^*\rangle$ | $9n + 3\lceil\log_p r\rceil + 4$ copies, $O(n^4)$ time; with the conjugate $5n$ copies, $O(n^3)$ | 🟢 🟢 🟢 | stabilizer state; the method without the conjugate only for $d$ prime |
| Gollakota, Liang 2022 | Stabilizer state under PAC access | the stabilizer group from randomly drawn measurements with one-bit outcomes; hard instance: the parity $y$ behind $\vert y\rangle$, a sign pattern on a known support | Sample, classical examples $(E, Y)$ with $E\sim D$ fixed; SQ oracle | noiseless poly (Rocchetto); with classification noise LPN-hard; SQ $2^{\Omega(n)}$ queries (parity measurements), $2^{\Omega(n^2)}$ (Pauli measurements) | 🟢 🔴 🟢 with noise | stabilizer state, fixed measurement distribution |
| Arunachalam, Chakraborty, Lee, Paraashar, de Wolf 2021 | Boolean function, $k$-Fourier-sparse | the Fourier span, then $f$ exactly | Sample, uniform quantum examples | $O(k^{1.5}\log^2k)$, lower bound $\Omega(k\log k)$ | 🟢 🟢 🟢 | sparsity $k$; unit normalization turns it into heaviness |
| Harper, Yu, Flammia 2021 | Pauli channel with $s$-sparse error rates | the $s$ Pauli errors and their rates | Query, eigenvalues of chosen stabilizer groups | $O(sn)$ queries, $O(n^2/\xi^2)$ measurements, $O(sn^2)$ time | 🟢 🟢 🟢 | sparsity; chosen sampling positions |
| Nadimpalli, Parham, Vasconcelos, Yuen 2023 | QAC⁰ channel $n\to 1$ via its Choi state | concentration on degree $\leq k$, then low-degree learning | Sample, copies of the Choi state | $n^{\mathrm{polylog}(n)}$ copies | 🟢 🟢 🟢 quasipolynomially | constant depth, $\mathrm{polylog}(n)$ auxiliary qubits |
| Bresler 2015 | Ising model on $p$ nodes | the graph, then the couplings | Sample, i.i.d. configurations | $f(d)\log p$ samples, $\tilde O(p^2)$ time | 🟢 🟢 🟢 | degree $\leq d$, no correlation decay needed |
| Klivans, Meka 2017 | Ising model, $t$-wise MRF | graph and parameters, online | Sample, i.i.d. | $O(\lambda^2e^{O(\lambda)}\log n/\epsilon^4)$ samples, $O(n^2N)$ time; $n^{O(t)}$ for order $t$ | 🟢 🟢 🟢 | $\ell_1$-width $\lambda$; $n^{O(t)}$ tight under sparse parity with noise |
| Gu, Leone, Ghosh, Eisert, Yelin, Quek 2023 | State ensemble (subset phase states) | stabilizer entropy $\omega(\log n)$ or $\Theta(n)$, i.e. whether the Pauli spectrum is concentrated | Sample, poly copies | statistically learnable, no poly-time distinguisher | 🟢 🔴 🟢 | quantum-secure one-way function |

Three families. The first papers search for the support of a *state* by Bell sampling and live on subgroup structure; Grewal, Iyer, Kretschmer, Liang 2023 show how far this carries when the subgroup holds only approximately, and agnostic tomography (Grewal, Iyer, Kretschmer, Liang 2024; Chen, Gong, Ye, Zhang 2024) pushes it to quasipolynomial time for any fidelity; Allcock, Doriguello, Ivanyos, Santha 2024 show that Bell difference sampling no longer yields the subgroup on qudits with $d > 2$, and learn it instead through the quadratic phase or with the conjugate. The next four search for the heavy Pauli coefficients of an *operator*; there the search is easy because the spectrum of a unitary is unit-normalized and locality or sparsity keeps the candidate space polynomial. Shin, Lee, Oh continue Bakshi et al. along the access axis: the same search, but without short-time access to the dynamics. The third family are the mirrors and limits: sparsity for Boolean functions from quantum examples (Arunachalam et al.), chosen sampling for sparse Pauli channels (Harper, Yu, Flammia), degree from depth for QAC⁰ (Nadimpalli et al.), classical structure learning from samples under a degree promise (Bresler; Klivans, Meka), the LPN wall for stabilizer states under noisy PAC access (Gollakota, Liang), and, with pseudomagic states, a second hard endpoint that needs no lattice assumption. The normalization paragraph in the appendix ("What is learned") explains why the same measurement runs into the LWE wall for states; the section "Where the wall begins" above says which perturbation builds the wall. By the LWE rule (Appendix, "Reading the tables"), all papers whose class parameter is the support of the Pauli spectrum sit here, even if they output a state at the end.

---

## Learning stabilizer states by Bell sampling (arXiv:1707.04012)

The paper by **Ashley Montanaro** (Bristol, 2017) is a three-page note with a single theorem: an unknown stabilizer state on $n$ qubits can be identified from $O(n)$ copies, and the measurement this requires is the simplest imaginable, a transversal Bell measurement on pairs of copies. The paper is the root of the entire Bell-sampling literature, on which the next two summaries and the conjugate-pair method of this project build.

### Placement in the tables

* **Task type:** Searching. Returned is the support of the Pauli spectrum, i.e. the set $T \subset \mathbb{F}_2^{2n}$ of Paulis with $|\langle\psi|\sigma_t|\psi\rangle| = 1$. Only afterwards are the signs determined. This is exactly the split into localization, then estimation.
* **Object:** pure state. **Access:** sample, copies of $|\psi\rangle$, Bell measurement on two copies, quantum memory two.
* **Status:** 🟢 🟢 🟢. Copies $O(n)$, time $O(n^3)$, memory $O(n^2)$ for the tableau.
* **Promise:** stabilizer state. The support is an $n$-dimensional subspace, and this turns the search into linear algebra. This is Regime 2 of the searching table.
* **Why not identifying:** the result can also be read as identification within the stabilizer class. The tables list it under searching because the output is literally the support, and because the method, samples from a coset, XOR, Gaussian elimination, is the template for every later support search under a subgroup promise, down to Simon's algorithm on the query side.

### The problem

Holevo forces exponentially many copies for tomography of an arbitrary state. The way out is a class: Aaronson and Gottesman had shown that stabilizer states can be identified from $O(n)$ copies, but with a collective measurement across all copies at once, or from $O(n^2)$ copies with single-copy measurements. The question: can it be done with $O(n)$ copies *and* with measurements that never entangle more than two copies?

### Key results

* **Theorem 1.** There is a quantum algorithm that identifies an unknown stabilizer state from $O(n)$ copies, uses only measurements on at most two copies at a time, runs in time $O(n^3)$, and fails with exponentially small probability.
* **Lemma 2.** Bell sampling on $|\psi\rangle^{\otimes 2}$ returns the outcome $r \in \{0,1\}^{2n}$ with probability $|\langle\psi|\sigma_r|\psi^*\rangle|^2 / 2^n$. The conjugate state appears in the formula although only two identical copies are measured. The reason is the vec identity $|\psi\rangle|\psi\rangle = \mathrm{vec}(|\psi\rangle\langle\psi^*|)$.
* **Optimality.** There are $2^{\Theta(n^2)}$ stabilizer states, so every algorithm needs $\Omega(n)$ copies. The time $O(n^3)$ is Gaussian elimination; $O(n^\omega)$ is possible, and writing down the answer already takes $\Omega(n^2)$.
* **Failure probability** at most $2^{-n}$, by a union bound over all subspaces of dimension $n-1$.

### Methodological approach

1. **For stabilizer states, conjugation is a Pauli operation.** From the normal form $|\psi\rangle \propto \sum_{x \in A} i^{\ell(x)} (-1)^{q(x)} |x\rangle$ with affine $A$, linear $\ell$, and quadratic $q$, it follows that $|\psi^*\rangle = \sigma_{10}^{\otimes S}|\psi\rangle$ for a fixed subset $S$. The Bell distribution therefore becomes $|\langle\psi|\sigma_r\sigma_{10}^{\otimes S}|\psi\rangle|^2/2^n$: uniform on a coset $\{t \oplus s : t \in T\}$ of the stabilizer group $T$.
2. **The unknown offset cancels under XOR.** The difference of two samples is uniform in $T$. The algorithm draws a reference sample $r_0$ and then $2n$ further samples $r$, collects $r \oplus r_0$, and determines a basis by Gaussian elimination.
3. **Signs from single copies.** For each basis element, one copy is measured in the eigenbasis of the corresponding Pauli; this decides between $M|\psi\rangle = |\psi\rangle$ and $M|\psi\rangle = -|\psi\rangle$.

The Bell measurement itself is a depth-one circuit: CNOT between corresponding qubits, Hadamard, measurement. The algorithm generalizes Rötteler's procedure for learning quadratic polynomials over $\mathbb{F}_2$ and resembles the independent graph-state algorithm of Zhao, Pérez-Delgado, and Fitzsimons.

### Significance and applications

* **The measurement primitive for everything that follows.** Bell difference sampling in Gross, Nezami, and Walter, learning with few T gates in Grewal et al., the circuit shadows of Hangleiter and Gullans, and agnostic learning by stabilizer bootstrapping all use exactly this mechanism.
* **Locality of the measurement.** The advance over Aaronson and Gottesman is not the copy count but that never more than two copies are entangled. This is the two-copy restriction under which this project also operates.
* **The plateau is not a hardness problem.** All $2^n$ coefficients on $T$ have magnitude one. The support can be reconstructed by linear algebra; only an *ordered* ranking is ill-defined. This is the content of `cor:plateau` in this project's paper.

### Relation to this project

* The algorithm is the provably correct decoder for rung 2 of the instance ladder in research.md and one of the three reference decoders for every experiment: trivial baseline, provable specialist, learned CNN.
* Bell sampling on two *identical* copies works here because $\psi^*$ is a Pauli image of $\psi$. This fails for generic states and for qudits with $d > 2$; there the conjugate pair $\rho \otimes \rho^*$ is needed (Allcock et al. 2024; King, Wan, McClean 2024). This is the justification for the measurement of Phase 1.
* The statistics here are the exception, not the rule: because the spectrum is spread over $2^n$ addresses of magnitude one, every sample sees a uniformly distributed element of the coset. For a sparse spectrum with $k$ coefficients of size $\Theta(1)$, each address has probability $\Theta(1/d)$, and the same measurement yields nothing directly readable. This is why Phase 1 needs the Fourier transform and the CNN decoder.

### Limitations and open questions

* Qubits only, exact stabilizer states only. Robustness to noise and closeness to the class come only with Grewal et al.; tolerance only with Arunachalam and Dutt and with Chen, Gong, Ye, and Zhang.
* Qudits with $d > 2$: Allcock, Doriguello, Ivanyos, and Santha show that Bell difference sampling on four copies of a stabilizer state yields only $\mathrm{col}(V)\times\mathrm{col}(W)$, the uniform distribution at full rank, which then carries no information (Theorem 39 there).
* Single-copy measurements cannot reach $O(n)$ copies: Arunachalam, Bravyi, Dutt, Yoder (arXiv:2208.07851, Theorem 5) prove $\Omega(n^2)$ for any single-copy measurement already for degree-2 phase states, a subclass of stabilizer states. This matches the $O(n^2)$ of Aaronson and Gottesman, so the single-copy question is settled at $\Theta(n^2)$ (own inference from that theorem).

### Questions for further study

* What does the coset structure of the Bell distribution look like in the cyclic qudit case, when $\mathbb{Z}_d$ is not a field? (Rank 2 instead of $n$, Hermite normal form instead of Gaussian elimination; see research.md, section "Conjecture Feedback".)
* What role does the choice $\rho \otimes \rho$ versus $\rho \otimes \rho^*$ play for the sign information that Lemma 2 makes visible?
* What is the precise relation between the union bound over subspaces here and the sample bound $N = O(g^{-2}\log(M/\delta))$ of the dictionary regime?

Paper: [arXiv:1707.04012](https://arxiv.org/abs/1707.04012)

---

## Efficient Learning of Quantum States Prepared With Few Non-Clifford Gates (arXiv:2305.13409)

The paper by **Sabee Grewal, Vishnu Iyer, William Kretschmer, and Daniel Liang** (UT Austin, 2023; published in *Quantum* 2025) generalizes Montanaro and Aaronson–Gottesman from stabilizer states to states of *stabilizer dimension* at least $n-t$, in particular to all states prepared by Clifford circuits with at most $t$ non-Clifford gates. Cost $\mathrm{poly}(n, 2^t, 1/\epsilon)$ in copies and time, hence polynomial up to $t = O(\log n)$. Two algorithms: one with Bell measurements on two copies, one with single copies only.

### Placement in the tables

* **Task type:** Searching by the LWE rule (Appendix, "Reading the tables"). The parameter of the class, a Pauli subgroup of size $2^{n-t}$ that stabilizes the state, is the support of the Pauli spectrum. The algorithm first searches for a large isotropic subspace $\hat G$ that approximately stabilizes the state; this is the support search that the paper itself calls "Tomography reduces to finding heavy subspaces". Afterwards the remaining $t$-qubit state is determined by tomography. The table row is "Clifford plus few non-Clifford gates" in the searching table.
* **Object:** pure state, mixed in Appendix B. **Access:** sample; variant 1 with Bell measurements on two copies, variant 2 with single copies and random Cliffords.
* **Status:** 🟢 🟢 🟢 for $t = O(\log n)$. Time and copies grow as $2^t$; beyond that 🔴 in time, which is unavoidable under a cryptographic assumption.
* **Promise:** stabilizer dimension $\geq n-t$, i.e. an abelian group of $2^{n-t}$ Paulis that stabilizes the state. Magic is the hardness dial.

### The problem

Optimal tomography costs $\Theta(d^2)$ copies with entangled and $\Theta(d^3)$ with single-copy measurements, $\Theta(d)$ for pure states. Classical simulators for near-Clifford circuits scale polynomially in $n$ and exponentially in the number of non-Clifford gates. Are there *learning algorithms* with the same scaling? Lai and Cheng had a heavily restricted case (a single T layer, a full-rank condition). What was needed was a procedure for arbitrary non-Clifford gates at arbitrary positions.

### Key results

* **Theorem 1.1.** For a state prepared by Cliffords and at most $t$ single-qubit non-Clifford gates, the algorithm learns $|\psi\rangle$ to trace distance $\epsilon$ in $\mathrm{poly}(n, 2^t, 1/\epsilon)$ time and copies. More generally for every state of stabilizer dimension $\geq n-t$.
* **Two-copy variant (Corollary 7.2).** $O(n/\epsilon + \log(1/\delta)/\epsilon^2)$ Bell samples to find the group, plus tomography of a $t$-qubit state with $2^{O(t)}$ copies. Time $\mathrm{poly}(n) + 2^{O(t)}$, i.e. additive rather than multiplicative, an advantage over Leone, Oliviero, and Hamma.
* **Single-copy variant (Corollary 9.7).** $O(n(n + \log 1/\delta)^2 \, 2^t/\epsilon^2)$ samples plus tomography; time $O(n^3 (n+\log 1/\delta)^2\, 2^t/\epsilon^2)$ plus tomography. The price of missing quantum memory is polynomial in $n$ and a factor $2^t$ in the samples.
* **Property test (Theorem 5.1).** Whether a state has stabilizer dimension $\geq k$ or fidelity $\leq 1-\epsilon$ with all such states: $(16n + 8\log(1/\delta))/\epsilon$ copies and $O((n^3 + n^2\log 1/\delta)/\epsilon)$ time, efficient for *every* $k$. This generalizes the result that Haar-random states can be distinguished from states with stabilizer dimension.
* **Hardness.** If linear-time constructible pseudorandom states with exponential security exist, then $t$-qubit states from circuits of size $O(t)$ cannot be learned in $2^{o(t)}$ time. The exponential dependence on $t$ is therefore likely optimal.
* **Mixed states.** Almost all results carry over without loss (Appendix B).

### Methodological approach

1. **Compressing the non-Cliffordness.** From generators of the stabilizer group $G$, Lemma 3.2 builds a Clifford $C$ with $C|\psi\rangle = |\varphi\rangle|x\rangle$: a basis state on $n-t$ qubits and a general state on $t$ qubits. Measuring then suffices for $|x\rangle$, and tomography for $|\varphi\rangle$.
2. **Robustness.** Exact stabilizers vanish under the smallest perturbations. The key contribution: it suffices to find a group $\hat G$ of size $2^{n-t}$ with $\mathbb{E}_{P \sim \hat G} |\langle\psi|P|\psi\rangle|^2 \geq 1-\epsilon$. Algorithm 2 then finds a Clifford that brings $|\psi\rangle$ approximately into product form.
3. **$\hat G$ by Bell difference sampling.** The sampled Paulis always commute with $G$; one takes the commutant of the samples. The technical core shows that after $\mathrm{poly}(n, 1/\epsilon)$ samples the state is $\epsilon$-close to a state stabilized by $\hat G$, even if $\hat G$ is larger than $G$.
4. **$\hat G$ from single copies.** Random Cliffords and *computational difference sampling*: measure $C|\psi\rangle$ twice in the computational basis and XOR the strings. This cancels the affine offset and yields elements of a subspace; with probability about $2^{-t}$ a Clifford reveals a generator. This puts the unpublished algorithm of Aaronson and Gottesman on a rigorous footing.
5. **Everything over $\mathbb{F}_2^{2n}$.** Paulis modulo phase form a symplectic vector space; commutant, isotropic subspaces, and group operations are linear algebra.

### Significance and applications

* The class is more expressive than stabilizer states: it contains $k$-designs for every constant $k$ and eigenstates of stabilizer Hamiltonians with a few non-commuting terms.
* The connection between simulability and learnability becomes quantitative: both scale with $2^t$. Magic is the common dial.
* The hardware requirements match those of classical shadows: measure Bell pairs, apply Cliffords, measure in the computational basis, tomography on $t$ qubits.
* Leone, Oliviero, Hamma and Hangleiter, Gullans appeared at the same time with similar Bell-sampling procedures; this paper is the most general one and has the additive runtime.

### Relation to this project

* This is the decoder for the rungs between "perfect crystal" and "generic" on the instance ladder: stabilizer ground states plus a few non-commuting terms. Stabilizer dimension is a measurable state property that belongs as an influencing factor in the taxonomy in research.md.
* The property test for stabilizer dimension is a tool to check, per instance class, *whether* a subgroup structure is present before the specialist decoder is applied.
* The footnote on Lai and Cheng is a warning for everyone who uses Bell difference sampling: it samples from $q_\psi = p_\psi * p_\psi$, the convolution of the characteristic distribution with itself, not from $p_\psi$.
* The hardness result shows the shape of the boundary: everything stays sample-efficient, and time explodes as $2^t$. This is the same signature as in this project's cell, only with magic instead of LWE as the cause.

### Limitations and open questions

* **No proper learning (Question 10.1).** The output circuit does not necessarily have few non-Clifford gates.
* **Is $2^t$ necessary with single copies (Question 10.2)?** The two-copy variant needs $O(n)$ Bell samples for the group, independent of $t$; the single-copy variant needs $\mathrm{poly}(n)\, 2^t$. The authors expect a separation as in Chen, Cotler, Huang, and Li.
* **Approximate stabilizer dimension.** States with high expectation for a large Pauli subgroup, without exact stabilization, are not covered.
* Tomography of the $t$-qubit remainder is the only exponential component; faster pure-state tomography improves all bounds directly.

### Questions for further study

* How exactly does Lemma 4.x guarantee that a subspace with large $p_\psi$ mass is isotropic, and what is the qudit analogue?
* How does the construction $C|\psi\rangle = |\varphi\rangle|x\rangle$ carry over to $\mathbb{Z}_d$ with composite $d$?
* Can this project's CNN read off the stabilizer dimension implicitly from the folded Bell record, and is that the mechanism at work on rung 2 of the ladder?

Paper: [arXiv:2305.13409](https://arxiv.org/abs/2305.13409)

---

## Bell sampling from quantum circuits (arXiv:2306.00083)

The paper by **Dominik Hangleiter and Michael J. Gullans** (QuICS, NIST/Maryland; *Phys. Rev. Lett.* 2024) treats Bell sampling not as a learning primitive but as a *model of computation*: two copies of a state $C|0^n\rangle$ are measured transversally in the Bell basis. The samples are classically hard to generate and at the same time a *circuit shadow* from which properties of the preparing circuit can be read off efficiently: fidelity, depth, magic, and, at low T-count, the whole state.

### Placement in the tables

* **Task type:** mixed, with a searching core. Estimating the stabilizer nullity searches, by Bell difference sampling, for the largest isotropic subspace $\mathcal{C}$, i.e. the support of the stabilizer part. The depth test and the magic test are identifying tasks with a one-bit answer; fidelity and purity are estimating. Clifford+T learning is the same procedure as in Grewal et al.; by the LWE rule the paper sits under searching, in the row "Clifford plus few non-Clifford gates" of the searching table.
* **Object:** state from a known circuit model. **Access:** sample, Bell measurement on two copies.
* **Status:** 🟢 🟢 🟢 for the diagnostics; for learning 🟢 🟢 🟢 up to $t = O(\log n)$, beyond that $2^t$ in time and copies. The authors show that $2^t$ is optimal, because a state with nullity $t$ has exactly $2^t + n - t$ real parameters.
* **Promise:** depending on the task, low T-count, a fixed architecture (depth test), or local Pauli noise (fidelity estimator).
* **Placement:** the paper belongs primarily in the primitives section, with cross-references from all three tables.

### The problem

Random circuit sampling serves as a benchmark and as a demonstration of quantum advantage, but the cross-entropy benchmark needs a classical simulation of the ideal circuit and therefore works only in the simulable regime. Computational-basis samples moreover reveal little about the state. Wanted: a model of computation whose outputs are classically hard and diagnostically rich at the same time.

### Key results

* **Bell distribution.** $P_C(r) = |\langle\bar C|\sigma_r|C\rangle|^2/2^n$ with the conjugate state $|\bar C\rangle$. The measurement is a depth-1 circuit of transversal CNOTs, Hadamards, and computational-basis measurement.
* **Universality and hardness.** Sign and magnitude of $\langle C|Z|C\rangle$ can be estimated from Bell samples of a modified circuit (Ramsey interferometry with one ancilla per copy). Approximate sampling from $P_C$ is classically intractable on average for random universal circuits with $\Omega(n^2)$ gates in a brickwork architecture, under the same conjectures as standard random circuit sampling.
* **Purity and fidelity.** The swap test is a function of the samples: the overlap $\mathrm{tr}[\rho\sigma]$ follows from the Y-parity with $O(1/\epsilon^2)$ samples. Under local Pauli noise, $\mathbb{E}_C F = \sqrt{\mathbb{E}_C P}$: the square root of the purity estimates the fidelity, independently of depth and noise strength, where XEB fails. With $E$ error locations before the measurement this extends to $F = (\mathbb{E}_C P)^{E/(2(E+2/3))}$.
* **Depth test.** Subsystem purities give Rényi-2 entropies $S_A$; since $S_A(d) \leq d\,|\partial A|$, the half cut gives a lower bound on the depth, refinable through depth-dependent Page curves.
* **Magic.** The stabilizer nullity $M(|\psi\rangle) = n - \dim(\mathcal{C})$, a magic monotone, is estimated from $O(n/\epsilon)$ Bell samples; according to the authors, the most efficient known magic measurement.
* **Clifford+T learning.** $O(n/\epsilon)$ Bell samples for the Clifford part plus $O(2^t/\epsilon^2)$ measurements for tomography of $|x\rangle|\varphi\rangle$; polynomial runtime, generalized to arbitrary non-Clifford gates.
* **Error detection.** An outcome in the antisymmetric subspace ($\pi_Y(r) = 1$) is certainly an error; discarding it roughly halves the error rate under white noise. The Bell measurement is transversal for stabilizer codes and extracts their syndromes; measurement errors do not propagate.
* **Quadratic error suppression** for diagonal two-copy observables via $\mathrm{tr}[A\rho^{\otimes 2}]/\mathrm{tr}[S\rho^{\otimes 2}]$, related to virtual distillation.

### Methodological approach

Everything follows from one observation: the Bell basis is the joint eigenbasis of all $\sigma_r \otimes \bar\sigma_r$, so all *diagonal two-copy observables* $A = \sum_r a_r |\sigma_r\rangle\langle\sigma_r|$ are functions of the samples. The swap operator is such an observable (the projector onto the symmetric minus the antisymmetric subspace), and so is every Pauli $P \otimes P$, and so are subsystem swaps. For the stabilizer part, Montanaro's coset argument applies, and Bell difference sampling yields, as in Grewal et al., a Clifford $U_{\mathcal{C}}$ that compresses $|\psi\rangle$ into $|x\rangle|\varphi\rangle$.

### Significance and applications

* **Benchmarking without simulation.** The square-root-purity estimator replaces XEB in the regimes of high noise rate and low depth, without classical simulation.
* **Bridge to error correction.** Transversal Bell measurements between code blocks; first experiments on a logical-qubit processor (Ref. 53 of the paper) came out of a collaboration with the authors.
* **A model of computation with built-in verification.** If the hardness of Bell sampling stays robust against noise, for which the authors give first indications in the supplement, this would be a scalable demonstration of quantum advantage with classical validation.

### Relation to this project

* The formula $P_C(r) = |\langle\bar C|\sigma_r|C\rangle|^2/2^n$ is the same as in Montanaro and shows the conjugate effect that this project exploits physically through $\rho \otimes \rho^*$. For real amplitudes the difference disappears, which explains why the demonstrations work with GHZ and Clifford states.
* The purity estimator from the Y-parity is a certificate that follows directly from the Bell record of Phase 1, without additional measurements. It could calibrate the noise floor and the mixedness factor A in the taxonomy in research.md.
* The nullity estimate is a measurable version of the factor "stabilizer rank / magic" from the same taxonomy.
* Hardware realism: the discussion of ion traps, Rydberg arrays, and the SWAP cost of geometrically local architectures is the most concrete description of the cost of a transversal Bell measurement among the papers in this collection.

### Limitations and open questions

* The hardness statement holds for noiseless sampling; whether it is asymptotically robust against constant noise, unlike computational-basis sampling after Gao–Duan and Aharonov et al., is open.
* The depth and magic tests are formulated for noiseless samples; noise-robust versions are missing.
* The fidelity relation assumes local Pauli noise, which can be produced by independent randomized compiling on both copies; correlated coherent errors break it.
* The learning result is formulated for T gates; the generalization to arbitrary non-Clifford gates is only claimed.

### Questions for further study

* Which diagonal two-copy observables correspond in the qudit case to the displacement quadratures $S_{q,p}$, and can they be read off from the conjugate-pair record?
* How does the nullity estimator behave under the convolution $q_\psi = p_\psi * p_\psi$ for mixed states?
* Can error detection via the antisymmetric subspace be carried over to $\rho \otimes \rho^*$, where the swap test has a different meaning?

Paper: [arXiv:2306.00083](https://arxiv.org/abs/2306.00083)

---

## Quantum boolean functions (arXiv:0810.2435)

The paper by **Ashley Montanaro and Tobias J. Osborne** (2008; *Chicago Journal of Theoretical Computer Science* 2010) carries the analysis of Boolean functions over to operators. A *quantum boolean function* is a unitary $f$ with $f^2 = I$; its Fourier expansion is the Pauli decomposition. The paper provides property tests, a quantum version of the Goldreich–Levin algorithm for finding large Pauli coefficients, an application to local dynamics, and hypercontractivity as well as FKN and KKL analogues.

### Placement in the tables

* **Task type:** Searching. The Goldreich–Levin algorithm (Theorem 26) outputs all addresses $s \in \{0,1,2,3\}^n$ with $|\hat f_s| \geq \gamma$, without a candidate list being given. The property tests (stabilizer test, locality test) are identifying with one bit.
* **Object:** unitary, specifically a Hermitian unitary. **Access:** query. Theorem 26 assumes oracle access to $f$ and $f^\dagger$; coefficient estimation (Lemma 24) needs controlled-$f$ in a Hadamard test. The simpler results (Prop. 21, 22) get by with applications of $f$ to halves of Bell pairs and a Bell measurement, i.e. with sample access to the Choi state.
* **Status:** 🟢 🟢 🟢. Time $\mathrm{poly}(n, 1/\gamma, \log 1/\delta)$; by Parseval the list has at most $1/\gamma^2$ entries.
* **Promise:** none about the structure. The normalization $\sum_s \hat f_s^2 = 1$ does the work: a heavy coefficient carries a constant fraction of the total weight.
* **In the searching table** this is the row "Heavy Pauli coefficients of a unitary" with the addition "operator Goldreich–Levin". More precisely: the GL algorithm is query access; the Choi-sampling variant is contained in Propositions 21 and 22.

### The problem

Boolean functions have a mature theory: Fourier analysis, property testing, learning algorithms (Goldreich–Levin, Kushilevitz–Mansour), hypercontractivity, KKL. Is there a quantum generalization in which a unitary plays the role of the function, the classical theorems become special cases, and quantum proofs yield new insights? The motivation extends to circuit lower bounds and a quantum PCP.

### Key results

* **Definition and Fourier analysis.** $f = \sum_s \hat f_s \chi_s$ with $\chi_s$ the $n$-qubit Paulis and $\hat f_s = 2^{-n}\mathrm{tr}(\chi_s f)$. For the phase-oracle case $f|x\rangle = f(x)|x\rangle$ these are exactly the classical Fourier coefficients (Prop. 9). Parseval: $\sum_s |\hat f_s|^2 = 1$ for quantum boolean $f$ (Prop. 10).
* **Stabilizer test (Def. 13, Prop. 14).** Apply $f$ to two sets of Bell pairs and measure the equality observable; acceptance probability $\sum_s |\hat f_s|^4$. Whoever passes with probability $1-\epsilon$ is $\epsilon$-close to $e^{i\varphi}\chi_s$. Applied classically, the test has better parameters than the original.
* **Stabilizer operators with one query (Prop. 21).** Apply $f$ to halves of Bell pairs and measure in the Bell basis: for $f = \chi_s$ the outcome is $s$ deterministically. This is Bernstein–Vazirani for operators.
* **Dominant coefficient (Prop. 22).** If $\hat f_s \geq (1+\epsilon)/\sqrt 2$, a majority vote over $O(\epsilon^{-2}\log 1/\delta)$ applications identifies $s$.
* **Single coefficients (Lemma 24).** $\hat f_s$ to $\pm\eta$ with $O(\eta^{-2}\log 1/\delta)$ queries by a Hadamard test with controlled-$f$ and controlled-$\chi_s$; amplitude amplification gives a square root.
* **Quantum Goldreich–Levin (Theorem 26).** With oracle access to $f$, $f^\dagger$ and $\gamma, \delta > 0$, a $\mathrm{poly}(n, 1/\gamma, \log 1/\delta)$ algorithm returns a list $L$ such that every $s$ with $|\hat f_s| \geq \gamma$ is in $L$, and every $s \in L$ has $|\hat f_s| \geq \gamma/2$.
* **Learning local dynamics (Prop. 41).** For one-dimensional local Hamiltonians and $t = O(\log n)$, the Heisenberg pictures $e^{-itH}\sigma_j^s e^{itH}$ can be learned with $\mathrm{poly}(n, 1/\epsilon, \log 1/\delta)$ queries to $e^{itH}$, without knowing which qubit interacts with which.
* **Further results:** quantum hypercontractivity for $1 \leq p \leq 2 \leq q$, two quantum FKN theorems, influence of qubits, KKL in special cases.

### Methodological approach

* **Branch and bound over the Pauli addresses.** The set of all $4^n$ strings is split into four parts; for each part, described by an indicator string $S$ with a prefix and wildcards, the weight $W(S) = \sum_{t \in S}|\hat f_t|^2$ is estimated (Prop. 32), parts of small weight are discarded, the others are split further. Lemma 23 bounds the number of surviving parts by $1/\gamma^2$, hence at most $16n/\gamma^2$ estimates with $O(\gamma^{-2}\log 1/\delta)$ samples each.
* **Weights as Choi statistics.** $W(S)$ is the norm of a partially reduced operator $F_{s;I}$ (Lemmas 28, 29), hence accessible from Bell-pair experiments.
* **Lieb–Robinson as a sparsity promise.** For $t = O(\log n)$ the relevant coefficients of $\sigma_j^s(t)$ lie in a light cone of size $O(|t|)$, so there are only $\mathrm{poly}(n)$ candidates; GL finds them and Lemma 24 estimates them.

### Significance and applications

* Establishes the language in which juntas (Chen, Nadimpalli, Yuen), low-degree objects (Arunachalam, Dutt, Escudero Gutiérrez), and the structure learning of Bakshi, Liu, Moitra, and Tang are later formulated: influence of qubits, Pauli spectrum, GL queries.
* Prop. 41 is the precursor of Hamiltonian learning from dynamics: locality plus Lieb–Robinson make the spectrum sparse, and a Fourier search algorithm finds it.
* The stabilizer test is the operator-side precursor of the stabilizer test of Gross, Nezami, and Walter.

### Relation to this project

* The paper is the cleanest source for the statement that organizes the searching table: for an operator, $\sum_s \hat f_s^2 = 1$, a coefficient of size $\gamma$ appears in Choi sampling with probability $\gamma^2$, and the search is polynomial. For a pure state, the squared displacement coefficients sum to $d$, and the same measurement carries only $1/d$ per address. That is the whole difference between this row and this project's LWE cell.
* The branch and bound over prefixes is structurally the same as Kushilevitz–Mansour and the bucket refinement of the sparse FFT. This project's coprime folding is the dual of it: instead of *querying* weights on prefixes, it folds the spectrum and lets the CNN decode the residues. A comparison of the two strategies would deserve its own paragraph in the paper.
* Lemma 24 is the query version of Phase 2: a Hadamard test with a controlled operator estimates a single coefficient including its sign. This project's eigenprobe achieves the same with sample access and a conjugate pair.

### Limitations and open questions

* The locality and dictator tests (Conjectures 17, 20) are not analysed.
* Hypercontractivity only for $1 \leq p \leq 2 \leq q$; the full statement is conjectural.
* A KKL theorem for general quantum boolean functions and a Nisan–Szegedy degree bound $\Omega(\log n)$ remain open; combinatorial proofs do not carry over, Fourier-analytic ones do.
* GL is formulated as a query algorithm; a pure sample version via Choi sampling with a threshold argument is not worked out explicitly, but follows from Prop. 22 and Parseval.

### Questions for further study

* How exactly does Proposition 32 estimate the weight of an indicator string, and how many Bell pairs does one estimate need?
* Does the normalization argument also hold for non-Hermitian unitaries, where $\hat f_s$ is complex, and what changes for the displacement operator $D_{q,p}$ with $D^2 \neq I$ for $d > 2$?
* What does the Lieb–Robinson sparsity argument look like in the Heisenberg–Weyl basis of a single qudit, where there is no spatial locality?

Paper: [arXiv:0810.2435](https://arxiv.org/abs/0810.2435)

---

## Testing and Learning Quantum Juntas Nearly Optimally (arXiv:2207.05898)

The paper by **Thomas Chen, Shivam Nadimpalli, and Henry Yuen** (Columbia; SODA 2023) treats $n$-qubit unitaries that act nontrivially on only $k$ unknown qubits. It gives a tester with $\tilde O(\sqrt k)$ queries and a learning algorithm with $O(4^k/\epsilon^2)$ queries, both without dependence on $n$, and nearly matching lower bounds $\Omega(\sqrt k)$ and $\Omega(4^k/k)$.

### Placement in the tables

* **Task type:** Searching for learning. The algorithm first finds the $k$ relevant qubits, which is the support search at the level of qubits, and then identifies the $k$-qubit unitary by tomography. The tester is identifying with one bit.
* **Object:** unitary. **Access:** for learning it suffices to prepare $|v(U)\rangle = (U \otimes I)|\Phi\rangle$ and measure in the Pauli basis, i.e. nonadaptive sampling on the Choi state. By the rule of "What is learned" (appendix), this is sample access, although the paper speaks of oracle access. The tester needs $U$ and $U^\dagger$ in an influence estimator and is query access.
* **Status:** 🟢 🟢 🟢. Copies $O(k/\epsilon + 4^k/\epsilon^2)$, time $\mathrm{poly}(n, 4^k)$, memory $O(k\log n)$ plus the $k$-qubit unitary.
* **Promise:** $k$-junta. Constant $k$ makes the set of candidate supports polynomial, as in every dictionary regime.

### The problem

Process tomography of an arbitrary $n$-qubit unitary needs $\Omega(4^n)$ queries. Property testing asks instead whether $U$ has a property or is far from all unitaries with that property. For Boolean functions, junta testing is a classic, with $\tilde O(k)$ classically (Blais), $\tilde O(\sqrt k)$ quantumly (Ambainis et al.), and $\Omega(\sqrt k)$ as a lower bound (Bun, Kothari, Thaler). For unitaries there was Wang's $O(k)$ tester and no learning results beyond full process tomography.

### Key results

* **Testing (Theorems 2, 20, 24).** Quantum $k$-juntas are testable with $\tilde O(\sqrt k)$ queries to $U$ and $U^\dagger$; $\Omega(\sqrt k)$ queries are necessary. Independent of $n$.
* **Learning (Theorems 3, 28).** With $O(k/\epsilon + 4^k/\epsilon^2)$ queries the algorithm finds, with probability $9/10$, a $\hat U$ with $\mathrm{dist}(U, \hat U) \leq \epsilon$.
* **Lower bound (Theorem 31).** Every learning algorithm needs $\Omega(4^k\log(1/\epsilon)/k)$ queries, via a reduction to Nayak's input-guessing game. As a by-product, this gives the first formal proof that process tomography costs $\Omega(4^n)$ queries.
* **Structural result (Prop. 25).** If a Boolean function is far from every Boolean $k$-junta, then $U_f = \mathrm{diag}((-1)^{f(x)})$ is far from every quantum $k$-junta. This transfers the classical lower bound.

### Methodological approach

* **Influence of qubits** after Montanaro and Osborne, with a new characterization and an influence estimator that lets the tester of Ambainis et al. run as a black box.
* **Pauli sampling.** Prepare $|v(U)\rangle$ and measure all qubits in the Pauli basis $\{|v(\sigma_x)\rangle\}$; the outcome $x$ appears with probability $|\hat U(x)|^2$. The union of the supports over $O(\log k/\gamma)$ rounds yields the set $S$ of qubits with high influence. This is Fourier sampling for operators, the counterpart of the subroutine of Atıcı and Servedio for Boolean juntas.
* **State preparation by postselection.** The Bell registers of the irrelevant qubits are measured; if the outcome is the identity, a $2k$-qubit state $|\psi_S\rangle$ remains that encodes the $k$-qubit unitary.
* **Pure-state tomography** on $|\psi_S\rangle$ with $O(d/\epsilon)$ copies for $d = 4^k$ (Derka, Bužek, Ekert; Bruß, Macchiavello), hence the overall term $4^k/\epsilon^2$.

### Significance and applications

* First learning result for a natural class of unitaries with cost independent of the system size; the tester is the first $\tilde O(\sqrt k)$ tester for quantum juntas.
* Table 1 of the paper places classical testing, quantum testing, and quantum learning for Boolean and quantum juntas side by side and is a compact map of the transition from functions to operators.
* Starting point for later work on low-degree objects and on junta channels.

### Relation to this project

* The support search happens here at the coarsest level, the qubits, and is therefore cheap: $\log k$ rounds of Pauli sampling. This project's search happens at the finest level, the $d^2$ addresses, and is therefore hard. Between the two lies the idea of bundling addresses hierarchically, which is exactly what the coprime folding does.
* The lower bound via input guessing is a template for a sample lower bound for the top-$k$ task: an $\epsilon$-packing of the candidate states whose size forces the copy count.
* The paper shows a genuine query-sample asymmetry within one topic: the tester needs $U^\dagger$, learning does not. In the tables these are two different rows.

### Limitations and open questions

* The $\tilde O(\sqrt k)$ bound holds for testing, not for learning; the gap $4^k/k$ versus $4^k/\epsilon^2$ remains.
* Junta channels instead of unitaries are not treated (Section 1.3).
* Tolerant testing has not been studied quantumly; classically it costs $2^{\tilde O(\sqrt k)}$.
* Whether quantum algorithms give an advantage in the distribution-free model is open.

### Questions for further study

* How many Choi preparations does the postselection in state preparation need on average, and is the factor $4^k$ or $2^k$?
* How are influence and junta defined for displacement operators on a qudit whose addresses have no tensor structure?
* Can the input-guessing argument be transferred to $\rho \otimes \rho^*$ access to obtain a copy lower bound for top-$k$ localization?

Paper: [arXiv:2207.05898](https://arxiv.org/abs/2207.05898)

---

## Structure learning of Hamiltonians from real-time evolution (arXiv:2405.00082)

The paper by **Ainesh Bakshi, Allen Liu, Ankur Moitra (MIT), and Ewin Tang (Berkeley)** (FOCS 2024) solves structure learning of local Hamiltonians from real-time evolution: given the ability to apply $e^{-iHt}$, without knowing which interaction terms are present, $H$ is reconstructed with total evolution time $O(\log(n)/\epsilon)$, i.e. Heisenberg-limited, with constant time resolution, and without the assumption of short range.

### Placement in the tables

* **Task type:** Searching. Only $K$-locality with bounded local norm is given; returned are the terms present and their coefficients. The paper explicitly sets itself apart from the coefficient methods with known terms (Huang, Tong, Fang, Su; Haah, Kothari, Tang), which sit in the estimating table.
* **Object:** Hamiltonian. **Access:** query to the dynamics. The circuits are "prepare, apply, measure" with alternating evolutions $e^{-iHt}e^{iH_0 t}$ and $\log(1/\epsilon)$ rounds of adaptivity; control of this kind is provably necessary for Heisenberg scaling (Dutkiewicz, O'Brien, Schuster).
* **Status:** 🟢 🟢 🟢. Evolution time $O(r\log(n)/\epsilon)$, experiments $\tilde O(r^2\log n\log 1/\epsilon)$, classical time $\tilde O(n^2 r^3\log 1/\epsilon)$, memory polynomial.
* **Promise:** $K = O(1)$, local norm $\|H\|_{B_1} = \max_i\sum_{a: i\in\mathrm{supp}(E_a)}|\lambda_a| \leq g$, and effective sparsity $r = \max_i\sum_a\min(1, \lambda_a^2/\epsilon^2)$. For Hamiltonians of bounded interaction degree, $r = O(1)$.

### The problem

Derivative estimation learns Hamiltonians without structural knowledge, but with $t_{\mathrm{total}} = O(\log(n)/\epsilon^3)$ and time resolution $\epsilon$. The Heisenberg-limited methods need the terms: Huang et al. reshape the Hamiltonian by decoupling pulses derived from the known interaction graph, and Haah et al. compute commutator expansions with respect to the known terms. A single unspecified long-range term breaks both. Three questions: structure learning without knowledge of the terms (Q1), without strictly bounded range (Q2), with Heisenberg scaling *and* constant time resolution (Q3).

### Key results

* **Theorem 1.1.** For $K$-local $H$ with $K = O(1)$ and $\|H\|_{B_1} = O(1)$, the algorithm outputs estimates $\hat\lambda_P$ for all $P \in \mathcal{P}_K$ with accuracy $|\hat\lambda_{E_a} - \lambda_a| < \epsilon$ and $\hat\lambda_P = 0$ otherwise, with probability $0.99$; $t_{\mathrm{total}} = O(r\log(n)/\epsilon)$; $t_{\min} = \Theta(1/r)$; $\tilde O(r^2\log n\log 1/\epsilon)$ experiments; $\tilde O(n^2 r^3\log 1/\epsilon)$ classical time.
* **Optimality in $\epsilon$.** $1/\epsilon$ evolution time, $\Omega(1)$ resolution, $O(1/\epsilon)$ interleavings, and $\log(1/\epsilon)$ experiments are optimal up to $\log\log$ factors.
* **Further properties.** $n$ qubits without ancillas; robust to SPAM errors up to $\Theta(1/r)$ per experiment; implementable in the continuous and in the discrete access model.
* **Corollary 1.5, power law.** For $\alpha$-power-law decay on a $d$-dimensional lattice with $\alpha > d$, $t_{\mathrm{total}} = O(\epsilon^{-(1+\kappa)}\log(n/\delta))$ with $\kappa = dK/(dK + \alpha - d)$: always better than $1/\epsilon^2$, approaching Heisenberg for large $\alpha$, valid down to $\alpha = d$.
* **FPT runtime.** The classical time $\tilde O(n^2)$ does not have $K$ in the exponent. Classical structure learning of Markov random fields needs $n^K$ under standard assumptions (sparse parities with noise). This is a separation between learning from dynamics and learning from the Gibbs state.

### Methodological approach

1. **Bootstrapping to Heisenberg scaling** (after Dutkiewicz, O'Brien, Schuster): recursion on the residual. From an $\eta$-good estimate $\lambda^{(j)}$, an $\eta/2$-good one is obtained with evolution time $1/\eta$ by learning $H - H(\lambda^{(j)})$ to constant error. $\log_2(1/\epsilon)$ rounds. The authors' observation: this reduction needs no knowledge of the locality structure.
2. **Term cancellation instead of dynamical decoupling.** $e^{-i(H - H_0)t}$ is built by Trotterization from $e^{-iHt}$ and $e^{iH_0 t}$, with a new bound on the Trotter error that allows alternation at *constant* time intervals (Lemma 3.1). This answers Q3.
3. **Coefficient estimation by derivatives.** For small $t$, $e^{i\hat Ht}P_a e^{-i\hat Ht} = P_a + [i\hat Ht, P_a] + O(t^2)$; a single-qubit Pauli $P_a$ with $[E_a, P_a] \neq 0$ and the initial state $(I + Q_a)/N$ give an unbiased estimator of $2\hat\lambda_a t$. Parallelizable for all coefficients with $O(\log n)$ applications.
4. **Goldreich–Levin-type queries on the Pauli spectrum (Lemmas 1.10, 4.12).** For an unknown observable $O = \sum_Q c_Q Q$ with an implementable POVM $\{(I \pm O)/2\}$, a data structure built from $O(\log n)$ queries and $O(n\log n)$ preprocessing returns, for every $X \in \mathcal{P}_K$, an estimate of $\sum_{Q \supseteq X}|c_Q|^2/6^{|\mathrm{supp}(Q)|}$ in $O(\log n)$ time. With it, the terms are searched *hierarchically*: first all Paulis of support 1, then for each survivor all extensions to support 2, deleting those of small weight. The observable is $O = Z^\dagger P Z \approx P + [-i\hat Ht, P]$; it has degree $K$ and $O(1)$ coefficients.
5. **Parallelization with coupled randomness**, so that all GL queries are answered from one data set of $O(\log n)$ experiments instead of one experiment per query.

### Significance and applications

* The first method that achieves structure learning, Heisenberg scaling, constant time resolution, and long range simultaneously; the comparison table (Fig. 2 of the paper) places derivative estimation, Caro, Odake et al., Haah et al., and Huang et al.
* Characterization of quantum devices without an assumed locality structure; benchmarking and error diagnosis.
* A new tool, the observable-centric view of classical shadows in the dual access model (Huang, Chen, Preskill), which is more efficient than the state-centric $n^K$.

### Relation to this project

* This is the most precise description of what "search under a locality promise" means: the terms form a dictionary of size $n^{O(K)}$, but the algorithm does not enumerate it; it refines weights over prefixes. This is exactly the Kushilevitz–Mansour strategy that the mentor feedback describes as the query-access regime.
* The separation "dynamics easy, Gibbs hard" in the classical case ($\tilde O(n^2)$ versus $n^K$ under sparse-parity hardness) is an example of this project's thesis that the access, not the object, shifts the computational boundary.
* The time resolution $t_{\min}$ is an axis missing from the taxonomy in research.md and would matter for hardware realism (factor F).
* The GL data structure with coupled randomness is a model for the question whether a single Bell record can answer all candidate queries; the character mean over a dictionary does exactly that, but without the hierarchical refinement.

### Limitations and open questions

* **Lower bounds.** Only $1/\epsilon$ for one parameter and $\epsilon^{-1}\log(1/\delta)$ with SPAM robustness are known. How the cost must scale with locality, system size, and effective sparsity $r$ is open.
* **A single coefficient.** Simultaneously $t_{\mathrm{total}} = O(1/\epsilon)$ and $t_{\min} = \Omega(1)$ without dependence on $n$ is not achieved: decoupling achieves the time, term cancellation the resolution.
* **Arbitrarily large time resolution** remains Question 3 of the paper.
* The gate complexity is not tracked; the evolution with the known $H_0$ dominates.

### Questions for further study

* How exactly does the Trotter bound at constant intervals work (Lemma 3.1), and why does the local norm suffice instead of geometric locality?
* What does the data structure with coupled randomness look like, and can the same idea be carried over to Bell records of a state?
* What is the analogue of the factor $6^{|\mathrm{supp}(Q)|}$ for displacement operators on a qudit?

Paper: [arXiv:2405.00082](https://arxiv.org/abs/2405.00082)

---

## Heisenberg-limited Hamiltonian learning without short-time control (arXiv:2604.27838)

The paper by **Myeongjin Shin, Junseo Lee, and Changhun Oh** (KAIST, Seoul National University; 2026) removes a hardware requirement of all Heisenberg-limited methods: access to arbitrarily short evolution times. It shows that an $m$-sparse Hamiltonian can be learned at the Heisenberg limit even when every query to $e^{-iHt}$ has at least a fixed duration $T$; for $m = O(\log n)$ with polynomial total time for any constant $T$, for polynomial $m$ with a quantitative tradeoff between minimum and total evolution time. This resolves an open problem of Bakshi, Liu, Moitra, and Tang.

### Placement in the tables

* **Task type:** Searching in the strict sense of the tables: $H = \sum_{x=1}^m\alpha_xP_x$ with unknown support, and Algorithm 2 is explicitly called "Coefficient and structure learning"; the truncation to $m$-sparsity is the support search. The row therefore sits in the searching table directly below Bakshi, Liu, Moitra, Tang, whose open problem it resolves; its contribution concerns the access axis (which evolution times the oracle supplies), and the estimating row of Huang, Tong, Fang, Su is its predecessor on this axis.
* **Object:** $m$-sparse, traceless Hamiltonian, $\Vert H\Vert_\infty\leq 1$. **Access:** query to $U(t) = e^{-iHt}$, but only for $t\geq T$; in addition simulation of known Hamiltonians and ancillas (half of a maximally entangled state).
* **Status:** 🟢 🟢 🟢 for $m = O(\log n)$: $t_{\mathrm{tot}} = \tilde O(\min\{4^mT^3/\epsilon, 4^mT/\epsilon^2\})$, queries and post-processing $\mathrm{poly}(n, 1/\epsilon)$. For $m = \mathrm{poly}(n)$ and constant $T$ quasi-polynomial.
* **Promise:** sparsity $m$ in the Pauli basis; no short-time access needed.

### The problem

Iterative refinement learns the residual $\Delta H_j = H - H_j$ in round $j$ and needs $e^{-i\Delta H_jt}$ for this, which is built by Trotterization from $e^{-iHt/N}e^{iH_jt/N}$; this forces $t_{\min} = \Theta(\sqrt\epsilon)$ or $\Theta(1/m)$. Control pulses have finite bandwidth, rise times, and dead times, and with many short segments switching errors dominate. Can Heisenberg scaling be reached with $t_{\min}\geq T$ for constant $T$?

### Key results

* **Theorem 1 (logarithmically sparse).** $t_{\mathrm{tot}} = \tilde O(\min\{4^mT^3/\epsilon, 4^mT/\epsilon^2\})$ with $t_{\min} = T$; for $m = O(\log n)$ efficient and Heisenberg-limited for every fixed $T > 0$.
* **Theorem 2 (polynomially sparse).** $t_{\mathrm{tot}} = \tilde O(\min\{m^{K+2}T/\epsilon, m^KT/\epsilon^2\})$ at $t_{\min} = T = \Theta(m^{-1/K})$, $K\in\mathbb{N}$; with $K = \Theta(\log m)$, $t_{\min} = \Theta(1)$ at $t_{\mathrm{tot}} = \tilde O(m^{2+\log m}/\epsilon)$. The first quantitative tradeoff between $t_{\min}$ and $t_{\mathrm{tot}}$.
* **Eqs. (19)–(22) (long-time emulation).** $e^{-iH\tau}e^{iH_j\tau} = e^{-iH(T+\tau)}C_je^{iH_j(T+\tau)}$ with $C_j = e^{iHT}e^{-iH_jT}$; every short Trotter step becomes a long step plus a correction. $C_j$ itself contains backward evolution, but $C_j^\dagger = e^{iH_jT}e^{-iHT}$ is accessible with forward evolution; one learns a Hermitian generator $W_j$ with $C_j^\dagger = e^{-iW_j}$ and simulates $e^{iW_j}$. Error $\epsilon'$ at $\Vert W_j - \tilde W_j\Vert_F\leq\epsilon'/(2N)$.
* **Structure of $W_j$.** In the logarithmically sparse regime, $W_j$ is supported on a Pauli space of size $\leq 4^m$; in the polynomial regime it is dense but can be approximated as quasi-sparse via Baker–Campbell–Hausdorff.
* **Coefficient extraction.** $e^{-i\Delta H_jt}$ applied to half of a maximally entangled state encodes the Pauli coefficients of $\Delta H_j$ as first-order amplitudes; sparse state tomography reads them out, truncation preserves $m$-sparsity and the norm bound, $\eta_{j+1} = \eta_j/2$. Early rounds with large error run with a standard-quantum-limit routine.

### Methodological approach

* The core is rewriting a product-formula step as a long step with a fixed correction, together with the observation that the correction is a Hamiltonian of controlled norm and sparsity that can itself be learned with long times; learning thus becomes two-stage, first $W_j$, then $\Delta H_j$.
* The paper explicitly distinguishes the minimum evolution time $t_{\min}$ from the time resolution $\delta$ (the clock step of the control): it treats the former; the latter remains open.

### Significance and applications

* A conceptual shift: ultrashort pulses are not necessary for information-theoretically optimal learning; long dynamics plus an algorithmic reduction suffice.
* Resolves open problem 3 of Bakshi et al. (arbitrarily large time resolution) for the logarithmically sparse case and gives the first tradeoff for the many-body case.
* Connections to quantum probe tomography (local probes) and ancilla-free methods as next steps.

### Relation to this project

* The axis $t_{\min}$ is exactly the axis that the Bakshi summary names as missing from the taxonomy in research.md (factor hardware realism); this paper turns it into a resource of its own with a tradeoff curve.
* The two-stage scheme "learn the correction generator, then learn the residual" is structurally this project's two-phase scheme with a probe state: the unknown is moved into an environment in which the measurement is first order; here the environment is called $\Delta H_j$, there $\rho\otimes\tilde\rho^*$.
* Encoding Pauli coefficients as first-order amplitudes on a Bell pair is Choi sampling; the sparse tomography behind it is the query version of top-$k$ localization, with $4^m$ as the size of the candidate space.

### Limitations and open questions

* $4^m$ in the logarithmically sparse and $m^{K+2}$ in the polynomial regime; whether $\mathrm{poly}(m, T)/\epsilon$ is possible at $t_{\min} = T$ is the central open question.
* Time resolution $\delta$ (programmable times in $\delta\mathbb{N}$) is not treated.
* Needs ancillas and global control; ancilla-free and locally probing variants are an outlook.
* Timing inaccuracy $[(1-\delta)T, (1+\delta)T]$ is not analysed.

### Questions for further study

* How does the rewriting $e^{-iH\tau}e^{iH_j\tau} = e^{-iH(T+\tau)}C_je^{iH_j(T+\tau)}$ carry over to displacement Hamiltonians whose Pauli space is replaced by $d^2$ addresses, and is $W_j$ then sparse in the displacement basis?
* Is the sparse tomography in Algorithm 2 a query algorithm (Goldreich–Levin-like) or a sample algorithm on the Choi state, and where exactly does the support search sit?
* Which tradeoff curve between $t_{\min}$ and copy count exists for states, when "evolution time" is replaced by "preparation time per copy"?

Paper: [arXiv:2604.27838](https://arxiv.org/abs/2604.27838)

---

## Improved stabilizer estimation via Bell difference sampling (arXiv:2304.13915)

The paper by **Sabee Grewal, Vishnu Iyer, William Kretschmer, and Daniel Liang** (UT Austin; 2023, v3 March 2024) turns Bell difference sampling into a tool for states that are *close* to stabilizer states instead of being exactly stabilizer states. Three results: pseudorandom states need at least $n/2$ non-Clifford gates, an exponential improvement; a state with stabilizer fidelity $\tau$ is approximated by a stabilizer state of fidelity $\geq F_S - \epsilon$ from $O(n/(\epsilon^2\tau^4))$ copies in $\exp(O(n/\tau^4))/\epsilon^2$ time; above $\tau > \cos^2(\pi/8)$ this becomes polynomial. The tool is symplectic Fourier analysis of the characteristic distribution $p_\psi$ and its convolution $q_\psi$.

### Placement in the tables

* **Task type:** Searching against an approximate subgroup promise: sought is the Lagrangian subspace $\mathrm{Weyl}(\vert\phi\rangle)$ of the best stabilizer state, i.e. the support on which $q_\psi$ is concentrated; the state follows afterwards. Theorem 1.2 is a one-bit test (identifying), Theorem 1.5 a tolerant test. Theorem 1.3 is agnostic tomography of stabilizer states and, like stabilizer bootstrapping, sits under searching by the LWE rule.
* **Object:** pure $n$-qubit state. **Access:** sample; Bell difference sampling on four copies, two at a time; classical shadows to estimate the fidelities of the candidates.
* **Status:** 🟢 🟢 🟢 for $\tau > \cos^2(\pi/8) + \gamma$: $O(n + \log n/\gamma^2)$ copies, $O(n^3 + n^2\log n/\gamma^2)$ time. For constant $\tau$ below that 🟢 🔴 🟢: copies $O(n/(\epsilon^2\tau^4))$, time $\exp(O(n/\tau^4))$, still superpolynomially better than $2^{O(n^2)}$ brute force over all stabilizer states.
* **Promise:** stabilizer fidelity $\geq\tau$; none for the pseudorandomness test.

### The problem

Montanaro learns exact stabilizer states; Grewal et al. (2023, the stabilizer-dimension regime) and the earlier work on pseudorandomness showed only that $\omega(\log n)$ non-Clifford gates are needed, and "weak learnability" at fidelity $1/\mathrm{poly}$. Can one *find*, from Bell difference samples, a stabilizer state that witnesses the best fidelity, and how many non-Clifford gates does pseudorandomness really need?

### Key results

* **Theorem 1.2 / Corollary 4.10 (pseudorandomness).** Every family of Clifford circuits that produces pseudorandom states needs at least $n/2$ non-Clifford single-qubit gates, at least $n$ for diagonal gates ($T$); tight up to constants if linear-time quantum-secure PRFs exist. The distinguisher: with fewer gates, $q_\psi$ is concentrated on a proper subspace of $\mathbb{F}_2^{2n}$, for Haar states it is anticoncentrated; $O(n)$ samples and a rank test suffice.
* **Theorem 1.3 / 5.10 (stabilizer approximation).** If $F_S(\psi)\geq\tau$, the algorithm returns $\vert\phi\rangle$ with $\vert\langle\phi\vert\psi\rangle\vert^2\geq F_S(\psi)-\epsilon$ from $O(n/(\epsilon^2\tau^4))$ copies in $\exp(O(n/\tau^4))/\epsilon^2$ time. Mechanism: $q_\psi$ has substantial support on $\mathrm{Weyl}(\vert\phi\rangle)$ and is not concentrated on any proper subspace of it, so enough samples generate the subspace; the candidates are maximal cliques in the commutation graph of the samples (algorithm of Tomita et al.), their fidelities come from shadows. By binary search this estimates $F_S$ to $\epsilon$ with $O(n/\epsilon^6)$ copies.
* **Theorem 1.4 / 6.7 (bounded distance).** For $F_S\geq\cos^2(\pi/8)+\gamma$ the closest stabilizer state is unique, and $x\in\mathrm{Weyl}(\vert\phi\rangle)$ if and only if $\langle\psi\vert W_x\vert\psi\rangle^2 > 1/2$ (Corollary 6.4); a threshold test replaces the clique search. Copies $O(n + \log n/\gamma^2)$, time $O(n^3 + n^2\log n/\gamma^2)$; the output is the maximizer itself.
* **Theorem 1.5 / 7.7 (tolerant test).** For $\alpha_2 < (4\alpha_1^6-1)/3$ and $\gamma = \alpha_1^6 - (3\alpha_2+1)/4$, $O(1/\gamma^2)$ copies and $O(n/\gamma^2)$ time decide between $F_S\geq\alpha_1$ and $F_S\leq\alpha_2$; a repetition of the GNW test with a completeness bound from the earlier work and a soundness bound from GNW.
* **Theorem 1.6 / 3.1, 3.2 (duality).** For a subspace $T$: $\sum_{a\in T}p_\psi(a) = \tfrac{\vert T\vert}{2^n}\sum_{x\in T^\perp}p_\psi(x)$ and $\sum_{a\in T}q_\psi(a) = \vert T\vert\sum_{x\in T^\perp}p_\psi(x)^2$. Mass on $T$ is mass on the commutant $T^\perp$; for large $T$ a sum over $2^{\dim T}$ terms becomes one over a few.

### Methodological approach

* $p_\psi(x) = 2^{-n}\langle\psi\vert W_x\vert\psi\rangle^2$ is a distribution (Parseval), and $q_\psi = p_\psi * p_\psi$ is the Bell difference distribution (GNW). All statements are concentration or anticoncentration statements about $q_\psi$ on subspaces, proved with the symplectic Fourier transform, whose characters $(-1)^{[x, y]}$ are the commutation relation.
* The jump from "$\omega(\log n)$" to "$n/2$" comes from testing concentration on a *subspace* instead of the fidelity with a fixed state; the rank test sees the dimension, not the amplitude.

### Significance and applications

* The first algorithm that approximates an arbitrary state by a stabilizer state; agnostic tomography of stabilizer states starts here, and Chen–Gong–Ye–Zhang and GIKL 2024 bring the runtime down to quasipolynomial.
* The duality theorems and the $\tau^4$-type bounds are the ingredients of all later tolerant tests (Arunachalam–Dutt; Bao, van Dordrecht, Helsen).
* Application to stabilizer decompositions of magic states and hence to simulation algorithms for near-Clifford circuits.

### Relation to this project

* The paper is the map between Regime 2 and the wall: an *approximate* subgroup promise stays searchable as long as a constant fraction of the samples lies exactly in the subgroup. The LWE instance also has a subgroup as its support, but every sample lies next to it; that is the whole difference between $\exp(O(n/\tau^4))$ and "no algorithm". The trichotomy is worked out in the section "Where the wall begins".
* The rank test for pseudorandomness is a searching primitive without support search: it measures only the dimension of the support of $q_\psi$. For the displacement spectrum, the question is whether the rank of the Bell records over $\mathbb{Z}_d$ carries the same information; that would be a cheap pre-test of whether a subgroup regime is present at all.
* The duality "mass on $T$ equals mass on $T^\perp$" is the same symplectic Fourier structure that underlies the character mean of this project's protocol; it holds over $\mathbb{Z}_d$ unchanged.

### Limitations and open questions

* $\exp(O(n/\tau^4))$ is exponential for small constant $\tau$; the tolerant test does not cover all $(\alpha_1, \alpha_2)$, and a test for arbitrary pairs is named as open.
* Pure states only; mixed inputs come with Chen–Gong–Ye–Zhang.
* Qubits only; the duality theorems over $\mathbb{Z}_d$ are not worked out.

### Questions for further study

* How exactly is "not concentrated on any proper subspace of $\mathrm{Weyl}(\vert\phi\rangle)$" quantified, and where does the exponent $\tau^4$ come from?
* Why is $\cos^2(\pi/8)$ the threshold of uniqueness, and is the displacement version for qudits $\cos^2(\pi/2d)$?
* Can the rank test be run on $\rho\otimes\rho^*$ with one copy fewer, because there $p_\psi$ instead of $q_\psi$ is sampled?

Paper: [arXiv:2304.13915](https://arxiv.org/abs/2304.13915)

---

## Agnostic tomography of stabilizer product states (arXiv:2404.03813)

The paper by **Sabee Grewal, Vishnu Iyer, William Kretschmer, and Daniel Liang** (UT Austin; Quantum 2026) introduces the model of *agnostic tomography*: given copies of an arbitrary, possibly mixed state $\rho$ and a class $\mathcal{C}$, find an element of $\mathcal{C}$ whose fidelity with $\rho$ comes within $\epsilon$ of the maximum over $\mathcal{C}$. For the class of stabilizer product states, the authors give the first algorithm with quasipolynomial runtime $n^{O(\log(2/\tau))}/\epsilon^2$, polynomial as soon as the best fidelity $\tau$ is constant.

### Placement in the tables

* **Task type:** Searching by the LWE rule (Appendix, "Reading the tables"). By task type this is identifying against a class without a promise, the quantum analogue of agnostic PAC learning: the class is the input, an element of the class is returned, and the promise $\rho\in\mathcal{C}$ is replaced by a fidelity guarantee relative to the best element. The parameter of the class, the stabilizer group of the best product state, is however the support of the Pauli spectrum, and the algorithm finds it by Bell difference sampling; this is why the paper, like Grewal et al. 2023 (arXiv:2304.13915), sits under searching.
* **Object:** mixed $n$-qubit state. **Access:** sample; Bell difference sampling on four copies plus single-copy measurements in the product basis.
* **Status:** 🟢 🟢 🟢 for constant $\tau$; quasipolynomial in $n$ for $\tau = o(1)$. Copies and time $n^{O(\log(2/\tau))}/\epsilon^2$, memory polynomial (one Pauli string and one basis).
* **Promise:** none about $\rho$; $\tau$ is an auxiliary input and can be found by binary search.

### The problem

Realizable learning of stabilizer states (Montanaro 2017) assumes that $\rho$ lies exactly in the class; even weak depolarization breaks this assumption. Grewal, Iyer, Kretschmer, Liang (2023) had an agnostic algorithm for general stabilizer states in exponential time and a polynomial one only above $\tau > \cos^2(\pi/8)$. The sample complexity is always polynomial in $\log\vert\mathcal{C}\vert$ via shadow tomography; the question is the runtime. Already for product states, the naive approach of tomographing each qubit separately fails: for the GHZ state every single-qubit reduction is maximally mixed, although $\vert 0^n\rangle$ has fidelity $1/2$.

### Key results

* **Theorem 1.2 (agnostic tomography).** For $\mathcal{C} = \{\vert 0\rangle, \vert 1\rangle, \vert +\rangle, \vert -\rangle, \vert i\rangle, \vert -i\rangle\}^{\otimes n}$ there is a proper agnostic learner that outputs a $\vert\phi\rangle\in\mathcal{C}$ with $\langle\phi\vert\rho\vert\phi\rangle\geq\max_{\varphi\in\mathcal{C}}\langle\varphi\vert\rho\vert\varphi\rangle - \epsilon$, in time $n^{O(\log(2/\tau))}/\epsilon^2$ when the maximum is at least $\tau$.
* **Lemma 2.1 (entropy counting).** From a distribution over $\{0,1\}^n$ with $\max_x D(x)\leq C/2^n$, $k\geq\log_{1/b}(n/\delta)$ draws show, with probability $1-\delta$, ones on all but $\log_2(C)/(1-H(b))$ positions. Applied to Bell difference samples from the stabilizer group $S$, this means: $O(\log n)$ samples from $S$ cover all but $O(\log(1/\tau))$ qubits with a nontrivial Pauli.
* **Support lemma.** The probability that a Bell difference sample lies in $S$ is $p\geq\tau^4$; hence $O(\log n/\tau^4)$ samples suffice for $\Omega(\log n)$ of them to come from $S$, and the search over all locally commuting subsets of size $O(\log n)$ costs $\binom{\log n/\tau^4}{\log n}\mathrm{poly}(1/\tau)\leq n^{O(\log(2/\tau))}$.
* **Theorem 3.5 (Algorithm 1).** From the full-weight Pauli string the product basis $B$ is formed, $\rho$ is measured $O(\log(1/\delta)/\epsilon^2)$ times in $B$, and the mode is the output; the fidelity guarantee follows because $B$ is orthonormal.

### Methodological approach

* The stabilizer group of a product state is fixed, up to phases, by a single Pauli string of weight $n$; one only has to assign $X$, $Y$, or $Z$ to each qubit. Bell difference samples yield elements of $S$ with probability $\geq\tau^4$, and local commutativity rules out contradictory assignments.
* Entropy counting replaces the search for $n$ independent generators by $O(\log n)$ samples; the remaining $O(\log(1/\tau))$ qubits are completed by brute force over $3^{O(\log(1/\tau))}$ possibilities.
* A parameter $b\in(1/2, 1)$ controls the tradeoff between the number of samples and the remaining qubits; the authors recommend numerical optimization.

### Significance and applications

* The first paper that formulates agnostic tomography as a model of its own and gives an efficient case; the follow-up works (Chen, Gong, Ye, Zhang 2024 for all stabilizer states and discrete product states; Bakshi et al. for product states in mixed form; agnostic process tomography) build on it.
* Application picture: find an ansatz class for a complicated laboratory state and then continue computing with the ansatz; also as a subroutine for stabilizer decompositions of magic states.
* Briët and Castro-Silva transferred the ideas to a quadratic Goldreich–Levin and the Gowers inverse theorem: the bridge to classical Fourier analysis that this document draws at Montanaro–Osborne also runs backwards.

### Relation to this project

* The model is the right language for the tolerant (agnostic) version of every promise: when the state does not lie exactly in the class, "the best approximation up to $\epsilon$" is the only guarantee that can still be proven. For displacement spectra this means: the top-$k$ support has to be defined agnostically, relative to the best $k$-sparse spectrum.
* Bell difference sampling on $\rho^{\otimes 4}$ is the four-copy relative of the two-copy protocol on $\rho\otimes\rho^*$: both draw from the characteristic distribution, the one from $p_\psi * p_\psi$ (convolution), the other from $\vert\mathrm{Tr}(\rho D)\vert^2$ itself. The convolution is the price for doing without the conjugate copy.
* The factor $\tau^4$ in the support lemma is a model for how a fidelity threshold translates into a sample count when Phase 1 delivers only magnitudes.

### Limitations and open questions

* Runtime quasipolynomial for $\tau = o(1)$; Chen, Gong, Ye, Zhang reach $n^2(1/\tau)^{O(\log 1/\tau)}/\epsilon^2$ with single- and two-copy measurements and give a single-copy procedure for discrete product states.
* Product states only; the generalization to arbitrary stabilizer states needs bootstrapping.
* $\tau$ must be known or estimated by search.

### Questions for further study

* What does entropy counting look like when the samples come not from $\{0,1\}^n$ but from $\mathbb{Z}_d^{2n}$, and what replaces "nontrivial Pauli on qubit $j$" for qudits?
* Can the bound $p\geq\tau^4$ be improved to $\tau^2$ with conjugate copies $\rho\otimes\rho^*$, because the convolution disappears?
* Which classes are "stabilizer-like" enough for the trick that a single generator fixes the group?

Paper: [arXiv:2404.03813](https://arxiv.org/abs/2404.03813)

---

## Stabilizer bootstrapping: a recipe for efficient agnostic tomography and magic estimation (arXiv:2408.06967)

The paper by **Sitan Chen, Weiyuan Gong, Qi Ye, and Zhihan Zhang** (Harvard, Tsinghua; 2024) gives a general framework for agnostic tomography, *stabilizer bootstrapping*, and with it resolves the open question of a polynomial-time agnostic learner for stabilizer states at arbitrary best fidelity $\tau$ down to $\tau\geq\exp(-c\sqrt{\log n})$. By-products are the first efficient estimator of stabilizer fidelity, a statement about the optimization landscape, and agnostic learners for states of high stabilizer dimension and for discrete product states.

### Placement in the tables

* **Task type:** Searching by the LWE rule, like arXiv:2404.03813: by task type identifying against a class without a promise, but the parameter is a Lagrangian subspace, i.e. a support, and the list decoding (all approximate local maximizers) is a support search. In addition, estimating of a single quantity (stabilizer fidelity, Theorem 1.3) as a corollary.
* **Object:** mixed $n$-qubit state. **Access:** sample; single- and two-copy measurements, Bell difference sampling for the stabilizer cases, single copies only for discrete product states.
* **Status:** 🟢 🟢 🟢 for $\tau\geq\exp(-c\sqrt{\log n})$: $n(1/\tau)^{O(\log 1/\tau)} + O(\log^2(1/\tau)/\epsilon^2)$ copies, time $O(n^2(n + 1/\epsilon^2))(1/\tau)^{O(\log 1/\tau)}$. Lower bound $\Omega(n/\tau)$ copies for $\epsilon < \tau/3$.
* **Promise:** none about $\rho$; the class supplies the structure.

### The problem

Montanaro learns exact stabilizer states, Grewal et al. agnostically only for $\tau > \cos^2(\pi/8)$ in polynomial time. For $\tau = o_n(1)$ no polynomial-time agnostic algorithm was known for any interesting class. At the same time, an efficient estimator for the stabilizer fidelity $\max_{S}\langle S\vert\rho\vert S\rangle$, the natural measure of magic, was missing.

### Key results

* **Theorem 1.2 (stabilizer states).** For $1\geq\tau\geq\epsilon\geq 0$ and $\max_{\phi'\in\mathcal{C}}\langle\phi'\vert\rho\vert\phi'\rangle\geq\tau$, the algorithm returns a stabilizer state with $\langle\phi\vert\rho\vert\phi\rangle\geq\tau-\epsilon$; cost as above, matching Montanaro in the realizable case $\tau = 1$.
* **Theorem 1.3 (stabilizer fidelity).** Estimation to $\epsilon$ in time $n^3(1/\epsilon)^{O(\log 1/\epsilon)}$ with $n(1/\epsilon)^{O(\log 1/\epsilon)}$ copies.
* **Corollary 6.2 (list).** A list of length $(1/\tau)^{O(\log 1/\tau)}$ contains all stabilizer states with fidelity $\geq\tau$ that are $(1/2+\xi)$-approximate local maximizers; hence there are only $(\xi\tau)^{-O(\log 1/\tau)}$ of them, for arbitrary mixed $\rho$.
* **Theorem 1.5 (stabilizer dimension $\geq n-t$).** Copies $n(2^t/\tau)^{O(\log 1/\epsilon)}$, time $n^3(2^t/\tau)^{O(\log 1/\epsilon)}$; near $\tau = 1$ again $\mathrm{poly}(n, 2^t, 1/\epsilon)$. The first agnostic learner for doped states, though improper.
* **Theorem 1.6 (discrete product states).** For $\mathcal{K}^{\otimes n}$ with pairwise $\vert\langle\phi_1\vert\phi_2\rangle\vert^2\leq 1-\mu$: $(n\vert\mathcal{K}\vert)^{O((1+\log 1/\tau)/\mu)}/\epsilon^2$ with single copies; **Theorem 1.7** improves this for stabilizer product states to $n^2(1/\tau)^{O(\log 1/\tau)}/\epsilon^2$.
* **Theorem 1.8 (lower bound).** $\Omega(n/\tau)$ copies for agnostic tomography of stabilizer states, $\Omega(1/\tau)$ already for pure $\rho$, $\Omega(1/\epsilon)$ for fidelity estimation.

### Methodological approach

* The recipe: (1) collect a family of commuting projectors $\Pi$ with $\mathrm{Tr}(\Pi\rho)\geq\Omega(1)$ ("high correlation"); (2) if it is complete, measure in the joint eigenbasis, and $\vert\phi\rangle$ appears with probability $\tau$; (3) otherwise draw a low-correlation projector that stabilizes $\vert\phi\rangle$; (4) postselect all further copies on $\Pi_{\mathrm{low}}$. The fidelity of the postselected state grows by a constant factor, $\langle\phi\vert\rho'\vert\phi\rangle\geq c\tau$ with $c > 1$, so the recursion ends after $O(\log 1/\tau)$ rounds.
* The price is the success probability of step (3) in each round; the runtime is dominated by the repetitions, hence $(1/\tau)^{O(\log 1/\tau)}$.
* For stabilizer states the projectors come from Bell difference sampling; for product states from local measurements.

### Significance and applications

* The first general framework for agnostic tomography, with applications to four classes; magic estimation is practically relevant for device characterization.
* The landscape statement (only quasipolynomially many approximate local maximizers) is an algorithmic proof of a structural result about the stabilizer polytope.
* Connection to cryptography: a polynomial-time algorithm for $\tau = 1/\mathrm{poly}(n)$ would, for subset states, solve finding an $O(\log n)$-dimensional affine space with maximal intersection, related to LPN and LSN.

### Relation to this project

* Bootstrapping is an adaptive two-copy protocol with postselection: step (4) is exactly the "probe" mechanism of Phase 2, except that the probe is a projector onto the unknown state rather than a separately prepared state. The fidelity amplification by $c > 1$ per round is an argument that should carry over to $\rho\otimes\rho^*$.
* List decoding is top-$k$ localization in the language of classes: not one element, but all elements above a threshold, and the bound on their number replaces the sparsity assumption.
* The lower bound $\Omega(n/\tau)$ shows that below $\tau = 1/\mathrm{poly}(n)$ even the copy count breaks down; on the instance ladder this marks the rung from which the tolerant version of the subgroup promise (Regime 2) also becomes expensive information-theoretically.

### Limitations and open questions

* Whether $(1/\tau)^{O(\log 1/\tau)}$ is necessary remains open; for $\tau = 1/\mathrm{poly}(n)$ there is neither a polynomial-time algorithm nor a hardness reduction.
* The learner for stabilizer dimension is improper: it does not necessarily output a $t$-doped state.
* Bell difference sampling needs two-copy measurements; whether computational difference sampling (single copies) works agnostically is open.
* States of bounded stabilizer rank are unsolved even in the realizable case.

### Questions for further study

* How exactly does step (3) turn the incompleteness of the projector family into a non-negligible probability of drawing a stabilizer of $\vert\phi\rangle$?
* What role do the Gowers norm or the uniformity of $p_\psi$ play in the analysis, and is that the bridge to Arunachalam–Dutt?
* Can the postselection be formulated on $\rho\otimes\rho^*$ with displacement projectors $\tfrac12(I + D)$ when $D$ is not Hermitian?

Paper: [arXiv:2408.06967](https://arxiv.org/abs/2408.06967)

---

## Beyond Bell sampling: stabilizer state learning and quantum pseudorandomness lower bounds on qudits (arXiv:2405.06357)

The paper by **Jonathan Allcock, João F. Doriguello, Gábor Ivanyos, and Miklos Santha** (Tencent Quantum Laboratory, Rényi Institute and SZTAKI Budapest, CQT Singapore, IRIF Paris; 2024) clarifies why Bell sampling fails on qudits of dimension $d = p > 2$, and replaces it in two places. Bell difference sampling on four copies of a stabilizer state does not return the stabilizer group but only $\mathrm{col}(V)\times\mathrm{col}(W)$, the uniform distribution at full rank. Nevertheless, a stabilizer state on $n$ qudits is learnable from $O(n)$ copies in time $O(n^4)$, with computational-basis measurements and a hidden-polynomial procedure for the quadratic phase; with copies of $\vert S^*\rangle$, ordinary Bell sampling suffices, for every $d$. In addition there is a pseudorandomness bound: Clifford circuits with $O(\log n/\log p)$ non-Clifford gates do not produce pseudorandom states.

### Placement in the tables

* **Task type:** Searching with a subgroup promise, as in Montanaro. Returned is the stabilizer group, i.e. the support of the Weyl spectrum, then the phases $\omega^{s_i}$ of the generators. The row "Stabilizer states on qudits, $d > 2$" of the searching table. The pseudorandomness part is a one-bit test and belongs to the row "Clifford plus few non-Clifford gates" of the searching table.
* **Object:** pure state on $(\mathbb{C}^p)^{\otimes n}$, $p > 2$ prime. **Access:** sample. Method 1: Bell measurement on $\vert S\rangle\otimes\vert S^*\rangle$, quantum memory two, conjugate access. Method 2: copies of $\vert S\rangle$ only; computational-basis measurements and a coherent circuit on three copies plus auxiliary registers.
* **Status:** 🟢 🟢 🟢. Method 2: $9n + 3\lceil\log_p r\rceil + 4$ copies with $r = \mathrm{rank}(W)$, time $O(n^3 r) \leq O(n^4)$, error $\leq 2p^{-n}$ (Theorem 41). Method 1: $3n$ copies of $\vert S\rangle$ and $2n$ of $\vert S^*\rangle$, time $O(n^3)$, error $\leq p^{-n}$ (Theorem 40). Memory $O(n^2)$ field elements for the generators.
* **Promise:** exact stabilizer state; $d = p$ prime for Method 2, arbitrary $d$ for Method 1.

### The problem

Montanaro's algorithm relies on Bell difference sampling on $\vert S\rangle^{\otimes 4}$ returning a uniformly distributed element of the stabilizer group for qubits. Gross, Nezami, and Walter had remarked that this does not carry over to $d > 2$: the transpose $\psi\mapsto\bar\psi$ is not completely positive, and the involution $x\mapsto -x$ is nontrivial on $\mathbb{Z}_d$. What exactly comes out was open, and with it whether stabilizer states on qudits can be learned from $O(n)$ copies at all, and whether the pseudorandomness bounds of Grewal, Iyer, Kretschmer, Liang hold on qudits.

### Key results

* **Lemma 34 (Bell sampling).** On $\vert\psi_1\rangle\vert\psi_2\rangle$ the generalized Bell measurement returns $x\in\mathbb{F}_p^{2n}$ with probability $p^{-n}\vert\langle\psi_1\vert W_x\vert\psi_2^*\rangle\vert^2$. On $\vert\psi\rangle\vert\psi^*\rangle$ this is the characteristic distribution $p_\psi(x) = p^{-n}\vert\langle\psi\vert W_x\vert\psi\rangle\vert^2$; on two identical copies one measures against $\psi^*$.
* **Theorem 35 (Bell difference sampling).** On $\vert\psi\rangle^{\otimes 4}$ the distribution is $b_\psi(x) = \sum_y p_\psi(y)\,p_\psi(J(x-y))$ with the involution $J(v,w) = (-v,w)$, the "involuted Weyl distribution". For qubits $J$ is the identity, and one recovers the convolution of Gross, Nezami, Walter.
* **Theorem 39 (stabilizer states).** If $M = \mathrm{col}\binom{V}{W}$ is the Lagrangian subspace of the group, then $b_S$ is uniform on $M + J(M) = \mathrm{col}(V)\times\mathrm{col}(W)$. One learns $V$ and $W$ separately up to a change of basis, but not their pairing and hence not $M$. If $V$ and $W$ have full rank, the output is uniform on $\mathbb{F}_p^{2n}$ and carries no information.
* **Lemma 22 (normal form).** Every stabilizer state is a superposition over an affine subspace $u + \mathrm{col}(W)$ with phases $\omega^{f(q)}$, and $f(q) = s^\top q + u^\top Vq + 2^{-1}q^\top V^\top Wq$ is a quadratic polynomial over $\mathbb{F}_p$.
* **Theorem 40 (with the conjugate).** $2n$ Bell samples on $\vert S\rangle\vert S^*\rangle$ are uniform on $M$; Gaussian elimination gives a basis, one measurement per generator gives the phase. Time $O(n^3)$, for every dimension $d$.
* **Theorem 41 (without the conjugate).** The stabilizer group from $9n + 3\lceil\log_p r\rceil + 4$ copies in time $O(n^3 r)$, with computational-basis measurements only. To the authors' knowledge the first direct learning procedure for qudit stabilizer states.
* **Theorem 46 (Haar versus stabilizer fidelity).** If $\vert\psi\rangle$ is Haar-random or has stabilizer fidelity $\geq 1/k$ (with $1/k\geq p^{-n/5}$), then $\lceil 72k^8\ln(2/\delta)\rceil$ copies in time $O(nk^8\log(1/\delta))$ distinguish the two cases.
* **Lemma 49, Remark 51, Corollary 52 (pseudorandomness).** A Clifford circuit with $t\leq n/2$ non-Clifford single-qudit gates has stabilizer fidelity $\geq p^{-2t}$; it can be distinguished from Haar directly with $O(p^{4t}\log(1/\delta))$ copies. For $t = O(\log n/\log p)$ this is polynomial, so such circuits do not produce pseudorandom states. For qubits, Grewal et al. had shown $n/2$ gates as the bound; on qudits it is logarithmic for now.

### Methodological approach

* **Symplectic Fourier analysis over $\mathbb{F}_p^{2n}$.** Theorems 35 and 39 follow from decomposing the projectors of the Bell difference measurement into Weyl operators and from Parseval. The decisive point is that conjugation maps $W_x$ to $W_{J(x)}$, and that for $p > 2$, $J$ mirrors the shift and clock parts against each other.
* **Hidden polynomial instead of Bell differences.** Computational-basis measurements return points of $u + \mathrm{col}(W)$; their differences span $\mathrm{col}(W)$. For $V$, three copies are shifted coherently, controlled by a register $\vert Wt\rangle$, by $\delta_i t$ each, with $\delta_1^2+\delta_2^2+\delta_3^2 = 0$, not all zero. This trick from the literature on hidden polynomial problems cancels the quadratic term in $t$; what remains is a linear phase that an inverse QFT reads out. Each round gives one linear equation for $V$; after $m = 2n + \lceil\log_p r\rceil$ rounds, $V$ follows by Gaussian elimination. The $\delta_i$ are found in time $\mathrm{poly}(\log p)$.
* **The stabilizer test of Gross, Nezami, Walter as a distinguisher.** The POVM $\Pi_{\mathrm{accept}} = \frac12\big(I + p^{-n}\sum_x (W_x\otimes W_x^\dagger)^{\otimes 2}\big)$ on four copies accepts with probability $\frac12(1 + p^n\sum_x p_\psi(x)^2)$. For Haar states, $p^n\sum_x p_\psi(x)^2$ is exponentially small by Lévy's lemma (Lemma 44), for stabilizer fidelity $1/k$ at least $k^{-4}$. The procedure needs no Bell difference sampling.

### Significance and applications

* Makes precise what "Bell sampling fails on qudits" means: not noise, but an exact algebraic mixing of the shift and clock parts by the involution $J$.
* Shows on qudits what King, Wan, McClean had observed for shadow tomography: access to $\psi^*$ makes the Bell measurement informative again (Theorem 40).
* Method 2 provides a conjugate-free route that needs only computational-basis measurements and a circuit of shifts and QFTs. This is relevant for hardware with native qudits.
* Carries the pseudorandomness bounds of Grewal et al. over to qudits, with a different tool.

### Relation to this project

* Lemma 34 and Theorem 40 are the justification of the Phase 1 measurement in formulas: on $\rho\otimes\rho^*$ the Bell distribution is the characteristic distribution, i.e. the squared displacement spectrum; on $\rho\otimes\rho$ it is the overlap with $\psi^*$. Theorem 39 shows that four identical copies do not repair the loss either. This is why the project relies on conjugate pairs rather than on more copies.
* Theorem 40 holds for every $d$, hence also for the project's single cyclic qudit with composite $d$. Under the stabilizer promise, the support there occupies $d$ of the $d^2$ addresses: the plateau, not the top-$k$ case (see Montanaro above).
* Method 2 shows a conjugate-free way out, but only under the subgroup promise and only for $d$ prime: the computational basis sees the affine support directly, and the phase is a quadratic polynomial. For the project's top-$k$ promise there is no such normal form. This supports the decision for conjugate access instead of a conjugate-free decoder.
* The involution $J$ is, up to the sign convention, the same reflection that appears in the project as $D_{q,p}^* = D_{q,-p}$ (section "Consequence for the instance generator").
* For the instance ladder: qudit states from Clifford circuits with $O(\log n/\log p)$ non-Clifford gates are distinguishable from Haar; they are no good as hard instances.

### Limitations and open questions

* Method 2 only for $d$ prime, because it needs vector spaces over $\mathbb{F}_p$; composite $d$ is the authors' first open question.
* Exact stabilizer states only; agnostic or tolerant learning on qudits is missing.
* The pseudorandomness bound is only logarithmic; the authors conjecture $O(n)$ with a better algorithm. The copy counts $k^8$ and $p^{4t}$ are high powers.
* Method 2 entangles three copies with an auxiliary register, more than the Bell measurement on two copies. The time model charges field operations and two-qudit gates at cost $O(1)$.
* Many qubit results based on Bell difference sampling are open on qudits: learning with few T gates, agnostic learning, bounds for pseudoentanglement.

### Questions for further study

* What does Theorem 39 look like for $\mathbb{Z}_d$ with composite $d$, where $M + J(M)$ is not a subspace over a field (Hermite normal form instead of Gaussian elimination)?
* Which stabilizer states are real in the computational basis, so that $\rho\otimes\rho$ already is $\rho\otimes\rho^*$ and Theorem 40 applies without conjugation (section "The conjugate: real with respect to a basis")?
* Can the $\delta$ trick, which cancels the quadratic term via $\sum\delta_i^2 = 0$, be carried over to states close to a stabilizer state?
* What does the involuted Weyl distribution $b_\psi$ of a state with a sparse displacement spectrum look like, and does it carry information about the support despite the mixing?

Paper: [arXiv:2405.06357](https://arxiv.org/abs/2405.06357)

---

## On the Hardness of PAC-learning Stabilizer States with Noise (arXiv:2102.05174)

The paper by **Aravind Gollakota and Daniel Liang** (UT Austin; Quantum 2022) shows that stabilizer states in Aaronson's PAC model have the same phase boundary as parities: efficiently learnable without noise (Rocchetto 2018, Gaussian elimination over $\mathbb{F}_2$), as hard as Learning Parity with Noise (LPN) with the simplest noise. To this end the paper introduces the statistical query (SQ) model for learning quantum states, shows that SQ learners tolerate classification noise and global depolarizing noise automatically, and proves exponential SQ lower bounds for stabilizer states. The hard instance is minimal: computational-basis states under parity measurements are literally the parity problem.

### Placement in the tables

* **Task type:** Searching under PAC access: stabilizer promise, randomly drawn measurements with one-bit outcomes → a hypothesis $\sigma$ with small squared prediction error $\mathbb{E}_{E\sim D}[(f_\sigma(E) - f_\rho(E))^2]\leq\epsilon$, in the stabilizer case the stabilizer group. The hard instance is a pure sign search: for $\vert y\rangle$ the support of the Pauli spectrum is known (all $Z$ strings), only the sign pattern $(-1)^{x\cdot y}$ is unknown, and $y$ is the LPN secret. The PAC model itself sits under estimating (row "PAC learning of states"); this paper sits under searching by the LWE rule, because the parameter of the class is the stabilizer group.
* **Object:** pure $n$-qubit stabilizer state. **Access:** classical examples $(E, Y)$ with $E\sim D$ and $Y\in\{\pm1\}$ the outcome of measuring $\rho$ with the two-outcome POVM $\{E, I-E\}$; the learner does not choose the measurements and knows $D$ (distribution-specific). In the SQ model only expectation values $\mathbb{E}[\phi(E, Y)]$ up to a tolerance $\tau$.
* **Status:** without noise 🟢 🟢 🟢 (Rocchetto). With classification noise at rate $\eta$, 🟢 🔴 🟢 under the LPN assumption: polynomially many examples suffice statistically, and the best known parity learner (Blum, Kalai, Wasserman) is slightly subexponential. In the SQ model unconditionally 🔴: $2^{\Omega(n)}$ queries under parity measurements, $2^{\Omega(n^2)}$ under Pauli measurements.
* **Promise:** stabilizer state and a fixed, known measurement distribution: uniformly random Pauli measurements $(I+P)/2$ or uniformly random parity measurements $E_x = (I + P_x)/2$ with $P_x = \sum_y(-1)^{x\cdot y}\vert y\rangle\langle y\vert = Z^{x_1}\otimes\cdots\otimes Z^{x_n}$.

### The problem

Aaronson (2007) showed that $O(n)$ examples suffice statistically to predict an arbitrary state for most measurements from $D$; this is efficient only for structured classes. Rocchetto (2018) gave the efficient learner for stabilizer states under Pauli measurements, purely algebraically via linear systems of equations. Whether this survives noise remained open. Classically the answer for parities is known: Gaussian elimination breaks down at the smallest noise rate, and the SQ model (Kearns 1998), which has noise tolerance built in, provably cannot learn parities. Does the same hold for stabilizer states?

### Key results

* **Definition 2.2, Theorem 2.4 (SQ learning of states).** States become probabilistic concepts $f_\rho(E) = 2\mathrm{Tr}(E\rho) - 1$ on the space of two-outcome measurements. A query is $\phi:\mathcal{E}\times\{\pm1\}\to[-1,1]$ with tolerance $\tau$; efficient means polynomially many queries with $\tau\geq 1/\mathrm{poly}(n)$. Lower bounds come from the statistical dimension on average (SDA) after Goel, Gollakota, Jin, Karmalkar, Klivans (2020): a learner using tolerance $\tau$ needs at least $\mathrm{SDA}(\mathcal{C}, \tau^2)$ queries.
* **Theorems 3.1, 3.2, 3.4, 3.5 (noise tolerance).** An SQ learner with $q$ queries of tolerance $\tau$ survives classification noise at rate $\eta<1/2$ with tolerance $O(\tau(1-2\eta))$ (Kearns), malicious noise at rate $\eta<\tau$ with tolerance $\tau-\eta$ (Aslam, Decatur), global depolarizing noise $\Lambda_\eta(\rho) = (1-\eta)\rho + \eta I/2^n$ for every constant $\eta<1$ with tolerance $\tau(1-\eta)$ (Theorem 3.4, from the linearity $\phi[\Lambda_\eta(\rho)] = (1-\eta)\phi[\rho] + \eta\phi[I/2^n]$), and every channel with $\Vert\Lambda - \mathrm{id}\Vert_\diamond\leq\eta$ with tolerance $\tau - 2\eta$ (Theorem 3.5). Distribution-free, every known noise is moved onto the measurements via the adjoint channel (Section 3.4).
* **Lemma 4.4, Theorem 4.6, Corollary 4.7 (uniform Pauli measurements).** For stabilizer states $\mathrm{Tr}(P\rho)\in\{0,\pm1\}$, so $\Vert f_\rho\Vert_D^2 = 2^{-n}$ and $\vert\langle f_\rho, f_{\rho'}\rangle_D\vert\leq 2^{-(n+1)}$ for $\rho\neq\rho'$ (tight for $\vert0\rangle^{\otimes n}$ versus $\vert0\rangle^{\otimes n-1}\vert+\rangle$). With $2^{\Theta(n^2)}$ stabilizer states it follows that $\mathrm{SDA}(\mathcal{C}, 2^{-n}) = 2^{\Theta(n^2)}$: every SQ learner needs $2^{\Omega(n^2)}$ queries of tolerance $2^{-O(n)}$ to reach error $2^{-O(n)}$. By Proposition 4.8, $\Vert f_\rho\Vert_D^2 = \Vert f_\rho - f_{I/2^n}\Vert_D^2 + 4^{-n}$; the bound therefore says that the maximally mixed state cannot be beaten noticeably. The introduction (Theorem 1.1) states tolerance $2^{-O(n^2)}$, the formal Corollary 4.7 states $2^{-O(n)}$; the formal version is authoritative.
* **Proposition 4.10 (embedding parities).** For a computational-basis state $\vert y\rangle$, the outcome of the parity measurement $E_x$ is deterministically the parity $x\cdot y \bmod 2$. An example $(E_x, Y)$ is therefore a parity example $(x, x\cdot y)$; the equivalence holds for every distribution on $\{0,1\}^n$ and survives classification noise. Since computational-basis states are stabilizer states, learning stabilizer states under the induced measurement distribution is at least as hard as learning parities.
* **Corollary 4.11 (SQ, parity measurements).** SQ learning under uniform parity measurements needs $2^{\Omega(n)}$ queries already for constant error $1/3$, even at tolerance $2^{-O(n)}$ (from Kearns' parity lower bound, Theorem 2.6). Here the p-concepts have norm one; the problem of the maximally mixed state disappears.
* **Corollary 4.12 (LPN, for every PAC learner).** Learning stabilizer states under uniform parity measurements with classification noise at rate $\eta$ is at least as hard as LPN at rate $\eta$, also outside the SQ model.
* **Theorem 5.5 (positive: product states).** Under the distribution "pick a qubit, measure it in a Haar-random basis", an SQ learner learns product states with $3n$ queries of tolerance $\sqrt\epsilon/n$ to squared error $\epsilon$. Lemma 5.1, $\mathbb{E}[\mathrm{sign}(\mathrm{Tr}(E\vert\psi\rangle\langle\psi\vert) - \tfrac12)(\mathrm{Tr}(E\rho) - \tfrac12)] = \tfrac14\mathrm{Tr}(P\rho)$, reads off the Bloch coordinates; the model is therefore not empty.
* **Theorems 6.2, 6.3 (differential privacy).** SQ learnability implies $\alpha$-DP PAC learnability with $\tilde O(q/(\alpha\tau) + q/\tau^2)$ examples, and in a copy variant of DP equally many copies; via Arunachalam, Quek, Smolin, online learnability and gentle shadow tomography follow.

### Methodological approach

* States as p-concepts make state learning a special case of classical SQ learning of probabilistic concepts; the lower-bound machinery (statistical dimension, Lemma 2.5 from pairwise correlations) applies directly.
* The correlations between stabilizer states are counting problems over stabilizer groups: $\langle f_\rho, f_{\rho'}\rangle_D = 4^{-n}(\vert S\cap S'\vert - \vert S\cap(-S')\vert)$, and two different groups share at most $2^{n-1}$ elements (Proposition 4.2).
* The LPN reduction is a pure re-encoding: parity measurements are $Z$ strings, computational-basis states set every label deterministically, and nothing quantum remains.
* Noise tolerance follows from the linearity of the query expectation in the state: global depolarizing noise is a known affine shift that can be subtracted.

### Significance and applications

* Learning stabilizer states is the quantum analogue of learning parities: algebraically easy without noise, presumably intractable with the simplest noise. Rocchetto's algorithm belongs to the few PAC learners outside SQ and therefore has no obvious noise-robust variant.
* The paper is the source that later stabilizer papers cite for "learning with a constant noise rate can be LPN-hard" (Grewal, Iyer, Kretschmer, Liang, arXiv:2304.13915, introduction; likewise arXiv:2404.03813).
* A critique of the PAC framework: because it reduces state learning to a classical problem, it also inherits that problem's hardness.
* The SQ model fits experiments that deliver only expectation values, and brings noise tolerance and differential privacy at no extra cost.

### Relation to this project

The following points are own conclusions, not statements of the paper.

* The hard instance is a pure sign search. For $\vert y\rangle$ all magnitudes $\vert\mathrm{Tr}(P_x\rho)\vert = 1$ on the $Z$ strings are known; only the sign pattern $(-1)^{x\cdot y}$ is unknown, and already that is LPN-hard under noisy PAC access. With copies and freely chosen measurements, $\vert y\rangle$ is trivial: one $Z$ measurement per qubit, a majority vote under readout noise. The hardness of the sign therefore depends on the access model, not on the state class, and every statement of the conjecture "magnitude and sign are efficiently learnable" needs the access model stated.
* Sharpening of refinement 1 in "Where the wall begins": it says hardness comes not from a fraction of corrupted samples but from a small error on all of them. LPN, however, is exactly a fraction $\eta$ of corrupted labels: the clean examples $(x, x\cdot y)$ lie exactly in a hyperplane of $\mathbb{F}_2^{n+1}$, a fraction $1-\eta$. What separates LPN from stabilizer bootstrapping is rather the ratio of the subspace fraction to the random fraction: there a fraction $\tau^4$ lies in an $n$-dimensional subspace of $\mathbb{F}_2^{2n}$ that a random point hits only with probability $2^{-n}$; for LPN a fraction $1-\eta$ lies in a hyperplane that a random point hits with probability $1/2$. Chen, Gong, Ye, Zhang (arXiv:2408.06967, Section 10.2) support this: finding an affine space of dimension $t$ with maximal intersection is considered LPN-hard for $t = n-1$ and LSN-hard for $t = \beta n$.
* The character mean of this project's protocol is a statistical query over Bell records. Conjecture: a decoder that only forms such averages fails on a parity-hidden support just as SQ learners fail on parities (Corollary 4.11); localization needs steps outside SQ, such as Gaussian elimination on individual samples as in Montanaro.
* Global depolarizing noise is harmless for SQ learners (Theorem 3.4); local noise is named as open. In the copy model, Arunachalam, Bravyi, Dutt, Yoder (arXiv:2208.07851, Theorem 11) show that exact identification under local depolarizing noise needs $\Omega((1-\epsilon)^{-n})$ copies already information-theoretically. On the instance ladder, qubit-wise noise is therefore the more expensive dial.

### Limitations and open questions

* Distribution-specific: the hardness holds for fixed measurement distributions. Open is whether there is a subset of $\omega(2^n)$ stabilizer states and a Pauli distribution with only polynomially small norms and exponentially small average correlation (Section 7).
* Under uniform Pauli measurements there is hardness only for exponentially small error, because $I/2^n$ is already correct up to $4^{-n}$.
* The noise model is classification noise on the labels, not noise on the state; qubit-wise depolarizing noise is open.
* The LPN hardness is conditional. Whether a noise-tolerant non-SQ learner in subexponential time exists, like Blum–Kalai–Wasserman for parities, is open.
* Classical data only: with quantum examples LPN is easy (Cross, Smith, Smolin 2015), and with copies and chosen measurements the hard instance becomes trivial.

### Questions for further study

* Why can the SDA threshold under Pauli measurements not be pushed below $2^{-(n+1)}$ (Lemma 2.5 with $\gamma = 2^{-(n+1)}$), and does that explain the discrepancy between Theorem 1.1 and Corollary 4.7?
* Does the displacement version, measurements $Z^x$ on $\vert y\rangle$ with $y\in\mathbb{Z}_d^n$ and outcome $\omega^{x\cdot y}$, lead with noise to LWE-type problems, and which noise model corresponds to the small error $e_i$?
* Is there a measurement distribution under which a large subclass of stabilizer states is SQ-learnable?
* How does the model relate to the quantum statistical queries of Arunachalam, Grilo, Yuen, which access quantum examples? The paper stresses that the models are different.

Paper: [arXiv:2102.05174](https://arxiv.org/abs/2102.05174)

---

## Two new results about quantum exact learning (arXiv:1810.00481)

The paper by **Srinivasan Arunachalam, Sourav Chakraborty, Troy Lee, Manaswi Paraashar, and Ronald de Wolf** (IBM, ISI Kolkata, UTS Sydney, QuSoft/CWI; ICALP 2019, Quantum 2021) shows that a $k$-Fourier-sparse Boolean function can be learned exactly from $O(k^{1.5}\log^2k)$ uniform quantum examples, independent of $n$, against $\tilde\Theta(nk)$ classical examples (Haviv–Regev). Second: $Q$ quantum membership queries can be replaced by $O(Q^2\log\vert\mathcal{C}\vert/\log Q)$ classical ones. For this document the first result is what counts: searching with sample access under a pure sparsity promise.

### Placement in the tables

* **Task type:** Searching. Phase 1 finds the Fourier span (the support up to linear span) by Fourier sampling, Phase 2 learns $f$ exactly; no heaviness promise, only sparsity.
* **Object:** Boolean function $f:\{0,1\}^n\to\{\pm 1\}$ with $\vert\mathrm{supp}\,\hat f\vert\leq k$. **Access:** sample; uniform quantum examples $2^{-n/2}\sum_x\vert x, f(x)\rangle$, from which Fourier sampling draws $S\sim\hat f(S)^2$.
* **Status:** 🟢 🟢 🟢. Copies $O(k^{1.5}\log^2k)$, lower bound $\Omega(k\log k)$; time polynomial; memory $O(k)$ coefficients.
* **Promise:** sparsity $k$; the normalization $\sum_S\hat f(S)^2 = 1$ turns it into heaviness.

### The problem

Linear functions are the case $k = 1$ (Bernstein–Vazirani, one sample), $\ell$-juntas the case $k = 2^\ell$ (Atıcı–Servedio). Classically, $k$-sparse functions need $\Theta(nk)$ uniform examples (Haviv–Regev, Theorems 2, 3). How many quantum examples does the class need, and does the number depend on $n$?

### Key results

* **Theorem 4.** $O(k^{1.5}\log^2k)$ uniform quantum examples suffice. **Theorem 5 / 8.** $\Omega(k\log k)$ are necessary, via the class of indicators of subspaces of codimension $\log k$.
* **Theorem 6 (two phases).** At Fourier dimension $r$: Phase 1 learns the Fourier span from $O(rk)$ Fourier samples; Phase 2 reduces to $r$ variables and calls Haviv–Regev with $O(rk\log k)$ classical examples. With $r = O(\sqrt k\log k)$ (Theorem 1, Sanyal), Theorem 4 follows.
* **Granularity (Lemma 1, Gopalan et al.).** Every coefficient of a $k$-sparse Boolean function is a multiple of $2^{1-\lfloor\log k\rfloor}$; hence a Fourier sample hits every support point with probability $\Omega(1/k^2)$, and coupon collecting trivially yields the support with $O(k^2\log k)$ samples. The Fourier dimension pushes this down to $O(rk)$.
* **Theorem 9 (improved Chang lemma).** For $k$-sparse $f$ with $\hat f(0^n) = 1-2\alpha$ and Fourier dimension $r$: $\hat f(0^n)\leq 1 - r/(k\log k)$; hence $O(k\log k/r)$ instead of $O(k\log k/\sqrt r)$ samples suffice in expectation for a nontrivial support point. **Conjecture 1** would push Phase 1 down to $\tilde O(k)$.
* **Theorem 10 (queries).** $R(\mathcal{C})\leq O(Q(\mathcal{C})^2\log\vert\mathcal{C}\vert/\log Q(\mathcal{C}))$, a $\log Q$ factor better than Servedio–Gortler, via the adversary method plus entropy; tight for linear functions and for point functions.

### Methodological approach

* Fourier sampling is the measurement of the example state after Hadamards: one draws $S$ with probability $\hat f(S)^2$. Because the total mass is one and the support is small, every support point is heavy; the search is therefore a sampling problem, not a decoding problem.
* Learning the Fourier dimension instead of the sparsity saves, because linearly dependent support points need not be seen individually; the change-of-basis Lemmas 2 and 3 turn this into a reduction to $r$ variables.

### Significance and applications

* The first $n$-independent sample result for a sparsity class; Chang's lemma and additive combinatorics appear as tools of quantum learning theory before they return in the tolerant stabilizer tests.
* The query simulation bounds how much quantum membership queries can save at all: at most quadratically, up to $\log\vert\mathcal{C}\vert$.

### Relation to this project

* The paper is the proof that "sparsity" under unit normalization is automatically "heaviness": granularity $2^{1-\lfloor\log k\rfloor}$ means a minimum weight of $1/k^2$ per support point. For pure states the same holds with $\sum\vert y\vert^2 = d$: exactly $k$-sparse means $\vert y\vert^2 = d/k$, and Bell sampling finds the support by coupon collecting. The hard regime of this project is therefore not sparsity but top-$k$ over a flat remainder; the precise statement is in "Where the wall begins".
* The two-phase structure, first the span from quantum examples, then classical refinement, is the function version of Phase 1 and Phase 2.
* The lower bound $\Omega(k\log k)$ is the sample lower bound of the support search itself, not of estimation; in the displacement case such a bound is missing.

### Limitations and open questions

* Gap $k^{1.5}$ versus $k\log k$; Conjecture 1 is open.
* Exact learning under the uniform distribution; no agnostic or noisy variant.
* Boolean functions only; real-valued sparse functions are handled classically by Cheraghchi et al. with $O(nk\log^3k)$.

### Questions for further study

* How does the Fourier dimension $r = O(\sqrt k\log k)$ (Sanyal) come about, and is there an analogue for the symplectic span of a displacement support?
* What is the Chang lemma for the characteristic distribution of a state whose mass is $d$ instead of one?
* How much does Phase 1 cost when the examples are noisy at rate $\eta$, and from which $\eta$ does this become LPN?

Paper: [arXiv:1810.00481](https://arxiv.org/abs/1810.00481)

---

## Fast estimation of sparse quantum noise (arXiv:2007.07901)

The paper by **Robin Harper, Wenjun Yu, and Steven T. Flammia** (Sydney, Tsinghua, AWS; PRX Quantum 2021) finds the $s$ nonvanishing Pauli error rates of an $n$-qubit Pauli channel with $O(sn)$ queries to an eigenvalue oracle and $O(sn^2)$ classical time, i.e. sublinear in the number $4^n$ of addresses. The oracle is realized with Clifford circuits and computational-basis measurements, $O(n^2/\xi^2)$ measurements for noise variance $\xi^2$. The decoder is the sparse Walsh–Hadamard transform of Scheibler et al. and Li et al., carried over to Paulis: subsampling on a stabilizer group, aliasing, peeling.

### Placement in the tables

* **Task type:** Searching against a sparsity promise on a channel: sought are the addresses $j\in\mathbb{F}_2^{2n}$ with $p_j\neq 0$, then the rates.
* **Object:** Pauli channel $\mathcal{E}(\rho) = \sum_jp_jP_j\rho P_j$ with $s$-sparse rates, each $\geq\epsilon_0$. **Access:** query; the eigenvalues $\lambda_k = 2^{-n}\mathrm{Tr}(P_k\mathcal{E}(P_k))$ of a *chosen* stabilizer group are measured by a randomized-benchmarking-type experiment on chosen input states. This is the access that makes the search sublinear.
* **Status:** 🟢 🟢 🟢. $O(sn)$ oracle queries, $O(n^2/\xi^2)$ measurements, $O(sn^2)$ time, $O(s)$ memory; error $\Vert\hat p - p\Vert_\infty\leq 2\xi/\sqrt B$ with $B = 2^n$ bins, failure probability $e^{-O(n)}$.
* **Promise:** sparsity $s\ll 4^n$, cutoff $\epsilon_0$, Gaussian noise on the eigenvalues (Assumptions 1); a random support for the peeling analysis.

### The problem

Learning all $4^n$ rates costs $O(n2^n/\epsilon^2)$ measurements (Flammia–Wallman); compressed sensing needs only $O(s\log 4^n)$ measurements, but $\mathrm{poly}(4^n)$ time for the convex reconstruction. Kushilevitz–Mansour-type methods (also Flammia–Wallman) are efficient but impractical. What is wanted is $\mathrm{poly}(s, n)$ in measurements *and* time.

### Key results

* **Theorem 1.** Under Assumptions 1, Algorithms 2 to 4 estimate the $s$-sparse rates to $\Vert\hat p - p\Vert_\infty\leq 2\xi/\sqrt B$ with $O(sn)$ eigenvalue queries and $O(sn^2)$ time, failure $\leq e^{-O(n)}$; the queries cost $O(n^2/\xi^2)$ measurements.
* **Step 1 (subsampling, Eq. 7).** A stabilizer group $S$ with generator matrix $S\in\mathbb{F}_2^{n\times 2n}$ yields $B = 2^n$ bins $\tilde p_j = B^{-1}\sum_v\lambda_{v\cdot S}(-1)^{j\cdot v}$, each a sum of $4^n/B$ rates; for $s < 2^n$ most bins are empty or contain one rate. The $2^n$ commuting eigenvalues come from a single experiment with an $n$-bit measurement.
* **Step 2 (aliasing, Eq. 8).** Shift $\lambda_{m+n}\leftrightarrow(-1)^{\langle n, k\rangle}p_k$: with $2n+1$ shifted copies of the bins, the sign pattern of a single-rate bin reveals the address of the rate; bit-flip error detection makes this robust to noise.
* **Step 3 (peeling).** Rates that have been found are subtracted from multi-rate bins until all are identified; analysis after Li et al. for random supports.
* **Experiment.** On data from a 14-qubit IBM device, rates down to $10^{-7}$ are recovered at eigenvalue noise $10^{-3}$ to $10^{-5}$, two orders of magnitude below the noise floor; artificially planted many-body errors are detected with small relative error.

### Methodological approach

* Rates and eigenvalues form a Walsh–Hadamard pair over $\mathbb{F}_2^{2n}$ with the symplectic form as bilinear form; the eigenvalues are the "time signal", the rates the sparse "frequency signal". The choice of stabilizer group is the choice of sampling positions, and exactly this choice is missing with i.i.d. samples.
* For today's devices, the stabilizer group is built from one layer of non-overlapping two-qubit Cliffords so that the circuits stay shallow.

### Significance and applications

* Practical noise characterization for 10 to 20 qubits with $10^6$ to $10^7$ measurements; a basis for tailored codes and decoders.
* For learning theory, the channel example of the searching column: a sparse-FFT algorithm that works because the experimenter chooses the sampling positions.

### Relation to this project

* The paper is the query cell of the quadrant for channels. The decoder is exactly what the Bell record does not allow: subsampling on a chosen subgroup and shifting by chosen offsets. On $\rho\otimes\rho^*$, a Clifford conjugation before the Bell measurement could play the role of the stabilizer group; the LWE wall says that this does not suffice in general, and the paper says what it would take for it to suffice: coherent control over the aliasing offsets.
* The error bound $2\xi/\sqrt B$ is the gain of binning: noise is averaged over $B = 2^n$ bins. This is the same mechanism as the character mean, only with chosen instead of random characters.
* The assumption "random support" is the average-case assumption that this project's conjecture (a uniformly random top-$k$ support) also makes; here it is needed for peeling and proven sufficient.

### Limitations and open questions

* Holds for Pauli channels after twirling; coherent errors have to be projected out beforehand.
* Regime $s\ll 2^n$; at extensive entropy there are exponentially many rates.
* The factor $m = O(1/\Delta)$ in the circuit depth depends on the spectral gap of the channel and can be large.
* Peeling guarantee for random, not for adversarial supports.

### Questions for further study

* How many stabilizer groups and offsets does peeling need when the support is structured instead of random?
* Can the subsampling be written as a Bell measurement after Clifford conjugation on $\rho\otimes\rho^*$, and what then replaces the eigenvalue oracle?
* How does the bound $2\xi/\sqrt B$ compare with the character-mean rate $O(1/\epsilon^4)$ at the same number of measurements?

Paper: [arXiv:2007.07901](https://arxiv.org/abs/2007.07901)

---

## Pseudomagic quantum states (arXiv:2308.16228)

The paper by **Andi Gu, Lorenzo Leone, Soumik Ghosh, Jens Eisert, Susanne F. Yelin, and Yihui Quek** (Harvard, UMass Boston, FU Berlin, Chicago; 2023) constructs ensembles with stabilizer entropy $\omega(\log n)$ that cannot be distinguished in polynomial time from ensembles with stabilizer entropy $\Theta(n)$: nonstabilizerness is a property that can be hidden. The construction is subset phase states on $2^k$ strings; magic and entanglement can be tuned independently. Consequences: hidden scrambling, EFI pairs without one-way functions, lower bounds for black-box magic distillation.

### Placement in the tables

* **Task type:** Searching in its one-bit form: is the Pauli spectrum concentrated on few addresses or spread out? Whoever could find the concentrated support could distinguish; hence the support search is hard for this class. The second hard endpoint of the searching column, from one-way functions instead of lattices.
* **Object:** state families $\vert\psi_{f,S}\rangle = \vert S\vert^{-1/2}\sum_{x\in S}(-1)^{f(x)}\vert x\rangle$. **Access:** sample, polynomially many copies.
* **Status:** 🟢 🔴 🟢. Statistically, the stabilizer entropy can be determined from polynomially many copies; there is no polynomial-time distinguisher under quantum-secure one-way functions; the key is polynomial.
* **Promise:** existence of quantum-secure one-way functions (for the PRF and PRP of the construction).

### The problem

Pseudoentanglement (Aaronson et al.) shows that entanglement can be hidden. Does the same hold for magic, the resource for quantum advantage, simulation hardness, and distillation? And does the one follow from the other?

### Key results

* **Definition 1 and Lemma 1.** A pseudomagic pair has magic $f(n)$ versus $g(n)$ but is indistinguishable; for the stabilizer Rényi entropy $M_\alpha = \tfrac{1}{1-\alpha}\log 2^{-n}\sum_P\mathrm{Tr}(P\psi)^{2\alpha}$, $g(n) = \omega(\log n)$ is required.
* **Theorem 1.** For every $k\in[\omega(\log n), n]$, the subset phase ensemble with $\vert S\vert = 2^k$ has stabilizer entropy $M_\alpha = O(k)$, exactly $\Theta(k)$ for $\alpha\leq 2$; it is indistinguishable from Haar (gap $\omega(\log n)$ versus $O(n)$), and already one layer of single-qubit gates turns it into a pair with maximal gap. The same holds for robustness, stabilizer fidelity, extent, and max-relative entropy with gap $\Theta(n)$ versus $\Theta(\mathrm{polylog}\,n)$.
* **Theorem 2 (hidden scrambling).** If the ensemble is also pseudorandom, the $2k$-point OTOCs of the generating unitary are exponentially separated from the Haar value: a non-scrambling unitary produces states that look scrambled to every bounded observer.
* **Theorem 3 (cryptography).** Pseudomagic ensembles with tunable entropy form EFI pairs, even in a world without quantum-secure one-way functions.
* **Theorem 4 (distillation).** Every efficient stabilizer protocol that synthesizes a state $\vert B\rangle$ from an unknown $\rho$ needs $\Omega(M(B)/\log^{1+c}M(\rho))$ copies; from a resource with $M = O(n)$, only $O(\log^{1+c}n)$ $T$ states can be distilled efficiently. **Theorems 5, 6:** entanglement $\Theta(f)$ and magic $\Theta(g)$ can be tuned independently, and prior knowledge of the magic does not help entanglement distillation.

### Methodological approach

* The stabilizer entropy is the only magic measure without a minimization and bounds all others from below; it therefore suffices to compute it for subset phase states. $M_2$ measures the participation number of the characteristic distribution: $2^{n+M_2}$ effective Pauli addresses out of $4^n$.
* Indistinguishability comes from the pseudorandomness of subset phase states (Aaronson et al., Theorem 2.1); the magic computation is new.

### Significance and applications

* Together with pseudoentanglement: for bounded observers, resource measures are not physical observables; only computationally accessible quantities have operational meaning.
* EFI pairs from pseudomagic strengthen the thesis that EFI is the fundamental primitive of quantum cryptography.

### Relation to this project

* The class has a Pauli spectrum with participation number $2^{n+\omega(\log n)}$ instead of $4^n$: the support is smaller than generic by a superpolynomial factor, and still nobody finds it efficiently. This is a hardness statement about searching that needs no lattice assumption and names the sparsity threshold below which "small support" does not help: only at $M = O(\log n)$, i.e. participation number $2^n\mathrm{poly}(n)$, does the class become distinguishable (Grewal et al.). This is the instance ladder along the axis "participation number".
* For the displacement version: subset phase states over $\mathbb{Z}_d$ would have the same structure; their displacement spectrum is flat up to $2^{-k}$, and Bell sampling on $\rho\otimes\rho^*$ sees Haar statistics.
* Theorem 4 is a warning for Phase 2: efficiently "distilling" structure from unknown states is logarithmically limited when there is no class promise.

### Limitations and open questions

* Conditional on one-way functions; no unconditional separation.
* An ensemble statement; individual physical states are not affected.
* The gap $\omega(\log n)$ versus $O(\log n)$ (Grewal et al.) is closed up to the threshold, but the transition itself is not charted.

### Questions for further study

* How exactly is $M_\alpha(\psi_{f,S}) = \Theta(k)$ computed, and what role does the 4-wise independence of $f$ play?
* Can the participation number of the characteristic distribution be estimated efficiently with Bell sampling on $\rho\otimes\rho^*$, and if so, why does this not contradict indistinguishability?
* Where, for displacement spectra, is the threshold at which a small support becomes findable without the key, in units of the participation number?

Paper: [arXiv:2308.16228](https://arxiv.org/abs/2308.16228)

---

## On the Pauli spectrum of QAC⁰ (arXiv:2311.09631)

The paper by **Shivam Nadimpalli, Natalie Parham, Francisca Vasconcelos, and Henry Yuen** (Columbia, Berkeley; 2023, STOC 2024) defines the Pauli spectrum of a circuit as the Pauli spectrum of the Choi state of the channel "apply the circuit, trace out everything except the target qubit", and proves for it a quantum version of the theorem of Linial, Mansour, and Nisan: for QAC⁰ circuits of depth $d$ with $a$ auxiliary qubits, the Pauli mass beyond degree $k$ is below $2^{-\Omega(k^{1/d}-a)}$. From this follow average-case bounds against parity and majority and a learning algorithm with quasipolynomially many copies of the Choi state.

### Placement in the tables

* **Task type:** Searching via a degree promise that follows from depth: the support of the Pauli spectrum lies, up to small mass, on degree $\leq k = \mathrm{polylog}(n)$, i.e. in a dictionary of size $n^{O(k)}$; after that it is estimating (low-degree learning). The depth dial of the identifying table gets its spectral justification here.
* **Object:** channel $\mathcal{E}$ from $n$ qubits to one qubit, computed by a QAC⁰ circuit (constant depth, arbitrarily wide Toffolis, arbitrary single-qubit gates). **Access:** sample; copies of the normalized Choi state $\Phi_{\mathcal{E}}/N$.
* **Status:** 🟢 🟢 🟢 quasipolynomially for $a = \mathrm{polylog}(n)$: $n^{\mathrm{polylog}(n)}\log(1/\delta)$ copies, output a channel with $\sum_P(\hat\Phi_{\mathcal{E}}(P) - \hat\Phi_{\tilde{\mathcal{E}}}(P))^2\leq\epsilon$.
* **Promise:** depth $d = O(1)$, polynomial size, at most $\tfrac12n^{1/d}$ auxiliary qubits for the bounds, $\mathrm{polylog}(n)$ for learning.

### The problem

LMN: functions in AC⁰ have Fourier mass $\leq s\cdot 2^{-\Theta(k^{1/d})}$ beyond degree $k$, hence are learnable in quasipolynomial time and cannot compute parity. For unitaries the naive transfer fails: $X^{\otimes n}$ has depth one and degree $n$. And whether QAC⁰ can compute parity has been open since Moore 1999.

### Key results

* **Definition (Pauli spectrum of a channel).** The Pauli coefficients of the Choi state $\Phi_{\mathcal{E}} = (I\otimes\mathcal{E})(\vert\mathrm{EPR}_n\rangle\langle\mathrm{EPR}_n\vert)$ on $n+1$ qubits; tracing out the non-target qubits resolves the $X^{\otimes n}$ problem.
* **Theorem 1 / 18 (concentration).** $\sum_{\vert P\vert > k}\hat\Phi_{\mathcal{E}}(P)^2\leq 2^{-\Omega(k^{1/d}-a)}$ for depth $d$ and $a$ auxiliary qubits; Table 1 sets this line by line beside LMN.
* **Theorem 2 / 33 (bounds).** With $\leq\tfrac12n^{1/d}$ auxiliary qubits: parity on at most $\tfrac12 + 2^{-\Omega(n^{1/d})}$ of the inputs, majority on at most $1 - \Omega(n^{-1/2})$; average-case, where previously only Rosenthal's bounds for depth two and size $\Omega(n/d)$ were known.
* **Theorem 3 / 39 (learning).** For $a = \mathrm{polylog}(n)$ and $\epsilon > 1/\mathrm{poly}(n)$: a channel $\tilde{\mathcal{E}}$ with $\ell_2$ spectral error $\leq\epsilon$ from $n^{\mathrm{polylog}(n)}\log(1/\delta)$ copies of the Choi state; if $\mathcal{E}$ computes a Boolean function $f$, the learned function is correct up to $O(\sqrt\epsilon)$ error. Also holds for convex combinations of QAC⁰ channels (Appendix A).
* **Conjecture 1.** Concentration for all polynomial-size QAC⁰ circuits without a bound on auxiliary qubits; it would exclude parity from QAC⁰ and make all QAC⁰ circuits sample-efficiently learnable.

### Methodological approach

* A Pauli-analytic transfer of the LMN proof structure; the bound on auxiliary qubits replaces what the switching lemmas do classically, and it is the reason the general case remains open.
* The learning algorithm is low-degree learning: estimate all coefficients up to degree $k$ from copies of the Choi state, set the rest to zero.

### Significance and applications

* The first learning result for QAC⁰; a new definition of the Pauli spectrum that correlates with complexity; tools for bounds beyond light cones, which fail for wide gates.
* Connection to quantum boolean functions (Montanaro–Osborne), low-degree learning (Arunachalam, Dutt, Escudero Gutiérrez, Palazuelos), and junta tests (Chen–Nadimpalli–Yuen).

### Relation to this project

* The paper provides a degree dial that follows from a physical property (depth) instead of being assumed; this is the kind of promise that could justify Regime 1 of this project, if a concentration statement for displacement spectra could be proven from the preparation depth.
* "Degree" is defined in the tensor-product phase space; in the cyclic basis the notion is missing. A displacement version would have to replace "degree" by a norm on $\mathbb{Z}_d\times\mathbb{Z}_d$, for instance the distance to the origin, and then concentration on small displacements would be exactly what Gaussian-like states show.
* The Choi state with traced-out registers is a model for how to turn a process object into a state object without losing the normalization.

### Limitations and open questions

* The bound on auxiliary qubits, $n^{1/d}$ or $\mathrm{polylog}(n)$; Conjecture 1 is open.
* Sample-efficient but quasipolynomial; no time bound beyond coefficient estimation.
* Single-qubit output only.

### Questions for further study

* Where exactly does the number $a$ of auxiliary qubits enter the exponent $k^{1/d}-a$, and why additively?
* How does the Choi spectrum of a channel differ from the Pauli spectrum of the unitary when no register is traced out?
* Is there a displacement analogue of Table 1, i.e. a "concentration" row that follows from the depth of a qudit circuit?

Paper: [arXiv:2311.09631](https://arxiv.org/abs/2311.09631)

---

## Efficiently learning Ising models on arbitrary graphs (arXiv:1411.6156)

The paper by **Guy Bresler** (MIT; STOC 2015) learns the graph of an Ising model on $p$ nodes with maximum degree $d$ from $f(d)\log p$ i.i.d. samples in time $f(d)\,p^2\log p$, without correlation decay or any assumption other than identifiability ($\alpha\leq\vert\theta_{ij}\vert\leq\beta$, $\vert\theta_i\vert\leq h$). Before, it was not known whether the exhaustive search over $p^d$ neighbourhoods could be beaten. The proof rests on a structural property: every node has a neighbour of constant influence, even conditioned on arbitrary sets.

### Placement in the tables

* **Task type:** Searching, the classical original: given samples and a degree promise, sought are the edges (the support of the couplings), then the weights. The searching introduction invokes "learning graphical models"; this is the source.
* **Object:** Gibbs distribution $P(x)\propto\exp(\sum\theta_{ij}x_ix_j + \sum\theta_ix_i)$ on $\{\pm\}^p$. **Access:** sample, i.i.d. configurations.
* **Status:** 🟢 🟢 🟢. Samples $f(d)\log p$ with $f$ doubly exponential in $d$ (only singly exponential is necessary), time $\tilde O(p^2)$, memory $O(dp)$.
* **Promise:** degree $\leq d$ and identifiability bounds; no correlation decay, valid at low temperatures and for strongly nonuniform models.

### The problem

Chow–Liu learns trees in $p^2$; for graphs with cycles, neighbours can be marginally independent and distant nodes more strongly correlated than close ones. All efficient methods needed correlation decay or incoherence conditions, which fail for ferromagnetic models without decay (Bento–Montanari). Is $p^d$ the truth?

### Key results

* **Proposition 1.1 / 5.3 (structure).** For every node $u$ there is a neighbour $i$ with conditional influence (and hence mutual information) at least a constant independent of $p$, even conditioned on arbitrary sets of nodes.
* **Theorem 1.2 / 4.1 (algorithm).** With $n = f(d)\log p$ samples, the graph is learned in time $f(d)p^2\log p$. Procedure: for each node, greedily add nodes by influence until a pseudo-neighbourhood of constant size arises, then prune the non-neighbours. Only add, never remove: an influential non-neighbour carries information about many other non-neighbours, and a potential argument over the conditional entropy bounds the size.
* **Lemma 2.1 (conditional randomness).** Every conditional probability of a spin is at least $\delta = \tfrac12e^{-2(\beta d + h)}$; the quantity that appears everywhere in the proof.
* **Lower bound (cited).** The number of samples must grow exponentially in $d$ (Santhanam–Wainwright); the $\log p$ dependence is optimal.

### Methodological approach

* The search changes from "guess a neighbourhood and test independence" ($p^d$ candidates) to "collect neighbours one by one by influence" ($p$ candidates per step, constantly many steps); the structural property guarantees that the greedy step always has a true neighbour on offer.
* Connection to learning theory: the conditional distribution of a node is a soft threshold function of its neighbours; the degree bound makes it a junta, and the structural property is the analogue of "threshold functions have degree-one Fourier mass".

### Significance and applications

* The first efficient structure learning for arbitrary graphs of bounded degree; the template for Klivans–Meka (optimal samples), Vuffray et al. (interaction screening), and Hamilton–Koehler–Moitra (higher order, larger alphabets).
* Separation of sampling complexity and learning complexity: sampling becomes NP-hard without correlation decay, learning stays easy.

### Relation to this project

* This is Regime 1 in classical form: a degree promise makes the candidate dictionary polynomial, and the search decomposes into $p$ local problems. The quantum version with a known set of terms (Anshu et al.; Haah–Kothari–Tang; Bakshi et al.) inherits exactly this logic; Bakshi et al. (structure learning) is the quantum counterpart without known geometry.
* The structural property is what is missing for displacement spectra: a statement of the form "every heavy address has a locally visible signature". Without it the search stays global, and that is exactly where the LWE wall sets in.
* "Only add, never remove" with a potential argument is a pattern for top-$k$ localization: a candidate list of constant size per step instead of a global selection.

### Limitations and open questions

* $f(d)$ is doubly exponential; Klivans–Meka achieve singly exponential.
* Binary pairwise models only; higher order and alphabets in the successors.
* Even for a single edge, $O(p^2)$ can only be beaten via the light-bulb problem (Valiant).

### Questions for further study

* What exactly does the conditional influence look like, and why does it give a lower bound on the mutual information?
* Where does the double exponential in $d$ get lost, and what do Klivans–Meka do differently?
* Is there a quantum version of the structural property for Gibbs states of local Hamiltonians without a known set of terms?

Paper: [arXiv:1411.6156](https://arxiv.org/abs/1411.6156)

---

## Learning graphical models using multiplicative weights (arXiv:1706.06274)

The paper by **Adam R. Klivans and Raghu Meka** (UT Austin, UCLA; FOCS 2017) gives, with the *Sparsitron*, a multiplicative-weights algorithm that learns Ising models of $\ell_1$-width $\lambda$ from $O(\lambda^2e^{O(\lambda)}\log(n/\rho\epsilon)/\epsilon^4)$ samples in time $O(n^2N)$, online and nearly sample-optimal against the bound of Santhanam–Wainwright; for $t$-wise Markov random fields in time $n^{O(t)}$, which is optimal up to constants under the hardness of sparse parity with noise. It is also the first method for non-binary alphabets.

### Placement in the tables

* **Task type:** Searching followed by estimating: first the dependency graph (Corollary 5.4), then the parameters (Theorem 5.2) and a hypothesis that is close in statistical distance. The promise is an $\ell_1$ bound per neighbourhood instead of a degree bound; this makes the class broader than in Bresler.
* **Object:** Ising model $D(A, \theta)$ on $\{\pm 1\}^n$, more generally a $t$-wise MRF with a factorization polynomial of degree $t$. **Access:** sample, i.i.d.; the procedure runs online.
* **Status:** 🟢 🟢 🟢. Samples $O(\lambda^2e^{O(\lambda)}\log(n/\rho\epsilon)/\epsilon^4)$ for $\Vert A - \hat A\Vert_\infty\leq\epsilon$, the graph with $O(e^{O(\lambda)}\log(n/\rho\eta)/\eta^4)$ at minimum coupling $\eta$; time $O(n^2N)$; $t$-wise MRF $e^{O(t)}e^{O(\lambda t)}\log(n/\rho\eta)/\eta^4$ samples and $O(N\cdot n^t)$ time.
* **Promise:** $\ell_1$-width $\lambda$ and $\delta$-unbiasedness (every variable, conditioned on all others, takes every value with probability $\geq\delta$), which follows from identifiability for MRFs.

### The problem

Bresler needs doubly exponentially many samples in $d$, Vuffray et al. time $\tilde O(n^4)$ and zero field; for $t$-wise fields, all methods ran in $n^{\Omega(d)}$ and gave no hypothesis in statistical distance. Wanted: optimal samples, $\tilde O(n^2)$ time, higher order, general alphabets.

### Key results

* **Theorem 3.1 (Sparsitron).** For examples $(X, Y)$ with $\mathbb{E}[Y\vert X = x] = \sigma(w\cdot x)$, $\sigma$ monotone and Lipschitz, $\Vert w\Vert_1\leq\lambda$: a $w'$ with small squared error from $O(\lambda^2\log n)$ samples; the proof is the regret bound of Hedge (Freund–Schapire). It also solves sparse generalized linear models.
* **Theorem 5.2 / Corollary 5.4 (Ising).** Parameters to $\epsilon$ in $\ell_\infty$, or the graph at minimum coupling $\eta$, samples as above, time $O(n^2N)$, online; up to polynomial losses at the Santhanam–Wainwright bound $\Omega(e^{\lambda/4}\log n/(\eta^3\cdot 2\cdot 2))$.
* **Theorem 7.2 (t-wise MRF).** The graph from $e^{O(t)}e^{O(\lambda t)}\log(n/\rho\eta)/\eta^4$ samples in time $O(N\cdot n^t)$; **Theorem 7.5** reconstructs the parameters and a pointwise close distribution. The reduction of Bresler–Gamarnik–Shah (sparse parity with noise on $t$ variables) makes $n^{O(t)}$ nearly optimal.
* **Lemmas 6.2, 6.4 (recovery).** Under $\delta$-unbiasedness, small $\ell_2$ error of the sigmoids implies small $\ell_1$ distance of the polynomials; this is why the regression step yields the coefficients themselves, not just a prediction.
* **Theorem 8.4.** Non-binary Ising models with alphabet size $k$.

### Methodological approach

* Every node, conditioned on the others, is a sigmoid of a linear form; structure learning becomes $n$ supervised GLM problems. Multiplicative instead of additive updates give sample counts in $\Vert w\Vert_1$ instead of $\Vert w\Vert_2$, hence logarithmic in $n$.
* Best-experts reading: candidate neighbours $(j, \pm)$ vote, wrong votes are penalized multiplicatively, non-neighbours disappear.

### Significance and applications

* Subsumes all predecessors for Ising models and gives the first efficient methods for higher order; Hamilton–Koehler–Moitra achieve something similar at the same time with Bresler's method and doubly exponential samples.
* The hardness statement $n^{\Omega(t)}$ under sparse parity with noise is the classical time wall of structure learning: from order $t$ on one pays $n^t$, and a sparse-LPN algorithm would break it.

### Relation to this project

* The Sparsitron is a learned decoder with a proof: multiplicative weights on a candidate space of size $2n$ per node, with a regret bound instead of combinatorics. It is the pattern for how a CNN decoder of this project could be framed theoretically: online learning over a candidate list with a loss function whose minimum is the structure.
* $n^{O(t)}$ against sparse parity with noise is the classical form of "Regime 1 up to the wall": order $t$ is a dial with cost $n^t$, and the wall is cryptographic. For displacement spectra the dial is the number $k$ of addresses, and the question is whether $d^{O(k)}$ is the right scale.
* $\delta$-unbiasedness is the condition that turns prediction quality into parameter identification; this project's protocol needs a counterpart that turns a fit to Bell statistics into support identification.

### Limitations and open questions

* $\epsilon^{-4}$ and $e^{O(\lambda)}$ are not optimal; the bound of Santhanam–Wainwright has $e^{\lambda/4}$.
* Unbiasedness is given for MRFs, not for general distributions.
* Classical distributions only; the quantum version (Gibbs states without a known set of terms) is open.

### Questions for further study

* How does the Hedge regret bound translate into a sample count in $\Vert w\Vert_1$, and why does one lose $\epsilon^{-4}$?
* What does the reduction from sparse parity with noise to $t$-wise MRFs (Bresler–Gamarnik–Shah) look like concretely?
* Can the Sparsitron be applied to Bell records, with every address an expert and the character mean the prediction?

Paper: [arXiv:1706.06274](https://arxiv.org/abs/1706.06274)

<br>

# Identifying

**Identifying** (candidate *states* or functions are *input*). Given: copies of $\rho$ and a list of $M$ candidate states, or a class $\mathcal{C}$ with or without the promise that $\rho \in \mathcal{C}$. Returned: one index, one object from the class, or one bit. Like matching a sample against a database of known genomes: the hypotheses exist before the data. Sub-cases by the size of the list: $M = 2$ is state discrimination, general $M$ is hypothesis selection, a class with a promise is learning that class, a class without the promise is agnostic tomography, one bit is property testing, and $M = 1$ is certification. Identifying behaves like estimating in every budget as long as the list is polynomial and the candidates are efficiently representable. Once the class is exponentially large and parametrized, the task shades into searching, which is where the hardness rows of this table come from. This is why identifying follows searching directly in this document: where the parameter of the class is the location of the support, the LWE rule (Appendix, "Reading the tables") decides for searching. In its budgets, by contrast, identifying behaves like estimating, and that is how the quadrant in the appendix groups it.

**What is known.** The two-hypothesis case is solved exactly: Helstrom for minimum error, unambiguous discrimination for zero error with abstention, and the quantum Chernoff exponent for many copies. Hypothesis selection needs only $O(\log M)$ copies through threshold search. A catalogue of classes is learnable in polynomial time, each by exploiting the structure that defines it: stabilizer states and Clifford circuits by linear algebra, states with $t$ non-Clifford gates at cost $2^t$, Gaussian and near-Gaussian states, matrix product states, states of shallow circuits, phase states of bounded degree, juntas, low-degree objects. The stabilizer family among them sits in the searching table by the LWE rule (Appendix, "Reading the tables"), because its parameter is the support of the Pauli spectrum. Property testing shows the memory axis at its sharpest: purity costs $O(1)$ copies with a SWAP test and $\Omega(2^{n/2})$ without, and mixedness testing with incoherent measurements costs $\Theta(d^{3/2}/\epsilon^2)$ whether or not the measurements are adaptive, against $\Theta(d/\epsilon^2)$ with entangled ones. Certification of almost all states is possible with single-qubit measurements.

**Efficiency status.** Copies: 🟢 throughout; the class results are polynomial, the testing results constant. Time and memory: 🟢 on the catalogue, and provably 🔴 outside it under cryptographic assumptions. Pseudorandom states and pseudoentanglement are statistically learnable yet computationally indistinguishable from Haar; states of polynomial gate complexity need only $\tilde\Theta(G)$ copies but admit no polynomial-time learner; output distributions of circuits become hard under LPN with a single $T$ gate. These rows are this column's version of the LWE wall in the searching column.

**What is open.**
* (1) Depth. Constant-depth circuits are learnable and polynomial-depth ones are hard; everything in between is uncharted.
* (2) Agnostic and tolerant learning beyond stabilizer-type classes.
* (3) Average-case hardness. The pseudorandomness constructions are worst-case; whether physically motivated classes sit on the easy side is the same question as in the searching column.

| Protocol or class | Object | Task type: given → returned | Copies or queries (access) | Time | Memory | Status & Condition |
| --- | --- | --- | --- | --- | --- | --- |
| **Pseudorandom states and pseudoentanglement** (Ji, Liu, Song 2018; Aaronson, Bouland, Fefferman, Ghosh, Vazirani, Zhang, Zhou 2022) | State | Identifying: pseudorandom or Haar-random, entanglement $\Theta(n)$ or $\omega(\log n)$ across every cut → one bit | Sample: poly copies, information-theoretically learnable (random phase states are phase states of high degree); $t$ copies of a random subset phase state on $K$ strings are $O(t^2/K)$-close to Haar | No polynomial-time distinguisher under quantum-secure one-way functions; MPS testing needs $\Omega(\sqrt r)$ copies | poly, the key | 🟢 🔴 🟢; hard by construction |
| **Identification**: state discrimination ($M=2$), hypothesis selection (general $M$) | State | Identifying: list of $M$ states → one index | Sample: Helstrom (min error) vs. USD (zero error + abort); $O(\log M)$ | Dominated by handling the $M$ candidates: poly for efficiently representable states, $\exp(n)$ for generic ones | The $M$ candidates, same split | 🟢 🟢* 🟢*; *for efficiently representable candidates |
| **Purity and mixedness testing** (O'Donnell, Wright 2015; Bubeck, Chen, Li 2020; Chen, Cotler, Huang, Li 2021; Chen, Huang, Li, Liu 2022) | State | Identifying: pure or maximally mixed, $\rho = I/d$ or far from it → one bit | Sample: purity $O(1)$ copies with two-copy memory (SWAP test), $\Theta(2^{n/2})$ without; mixedness $\Theta(d/\epsilon^2)$ with entangled measurements, $\Theta(d^{3/2}/\epsilon^2)$ with incoherent ones, adaptive or not | poly | poly | 🟢 🟢 🟢 with two-copy memory; the simplest memory separation, and the proof that adaptivity does not replace memory |
| **State certification with incoherent measurements** (Chen, Huang, Li, Liu, FOCS 2022) | State, mixed, against a known $\sigma$ | Identifying, $M = 1$: $\rho = \sigma$ or $\Vert\rho - \sigma\Vert_1 > \epsilon$ → one bit | Sample, one copy at a time, adaptive allowed: between $\tilde\Omega(\sqrt{d\,\underline d_{\mathrm{eff}}}\,F(\underline\sigma, I/d)/\epsilon^2)$ and $\tilde O(\sqrt{d\,\overline d_{\mathrm{eff}}}\,F(\overline\sigma, I/d)/\epsilon^2)$, from $\Theta(1/\epsilon^2)$ for pure $\sigma$ to $\Theta(d^{3/2}/\epsilon^2)$ for $\sigma = I/d$ | poly | none | 🟢 🟢 🟢; instance-optimal in the reference state, the quantum analogue of instance-optimal identity testing |
| **Fixed-unitary and symmetry-class distinction** (Aharonov, Cotler, Qi, Nat. Commun. 2022; the QUALM paper) | Unitary, as a lab oracle | Identifying: one fixed Haar-random unitary on $\ell$ qubits applied at every call, or a fresh one per call → one bit; fixed unitary, orthogonal, or symplectic → one of three | Oracle calls on a fixed input with two-copy memory: $O(1)$ calls and a SWAP test on the outputs (a generalized SWAP test on a maximally entangled input for the symmetry class); every incoherent protocol, adaptive or not, needs $\Omega(2^{2\ell/7})$ calls | $O(\ell)$ gates | $2\ell$ qubits of quantum memory | 🟢 🟢 🟢 with coherent access; the process version of the purity separation, and the paper that defines coherent versus incoherent access; time-reversal symmetric against general unitaries demonstrated on Sycamore with 20 system and 20 memory qubits (Huang et al., Science 2022) |
| **Stabilizer testing** (Gross, Nezami, Walter 2021; tolerant: Arunachalam, Dutt 2024; Bao, van Dordrecht, Helsen 2024; Chen, Gong, Ye, Zhang 2024) | State | Identifying: stabilizer state or far from all of them → one bit; tolerant: stabilizer fidelity $\geq \epsilon_1$ or $\leq \epsilon_2$ | Sample: six copies per round, $O(1/\epsilon^2)$ rounds, three copies for qudits with $d \equiv 1, 5 \bmod 6$; tolerant with an unconditional polynomial gap $\epsilon_2 \leq C'\epsilon_1^{672}$ in $O(\epsilon_1^{-12})$ Bell-difference rounds | poly | $2n$ qubits | 🟢 🟢 🟢; Bell difference sampling, and a generalized uncertainty relation through the Lovász theta number for the tolerant case |
| **State certification** (Huang, Preskill, Soleimanifar 2024) | State | Identifying, $M = 1$: target $\vert\psi\rangle$ known through an amplitude model, copies of $\rho$ → accept if $\langle\psi\vert\rho\vert\psi\rangle \geq 1 - \epsilon/2\tau$, reject if $< 1 - \epsilon$ | Sample: $O(\tau^2/\epsilon^2)$ single-qubit Pauli measurements, $O(\tau/\epsilon)$ with general single-qubit measurements, where $\tau$ is the relaxation time of a hypercube walk with stationary distribution $\vert\langle x\vert\psi\rangle\vert^2$; $\tau = O(n^2)$ for all but a $2^{-\Omega(n)}$ fraction of states, $O(n)$ for phase and GHZ-like states; two model queries per copy | poly | none | 🟢 🟢 🟢; verification rather than learning, the cheapest task in the column, with a tolerance gap of $2\tau$ |
| **Subsystem purity of $t$-doped states** (Leone, Oliviero, Esposito, Hamma 2024) | State from a $t$-doped Clifford circuit, bipartition $E \vert F$ with $f = n_F/n$ | Identifying the Clifford hull, then estimating: $\mathrm{Pur}(\psi_E)$, possibly exponentially small → the value up to a factor $4^t$ | Query to the circuit for the Clifford completion, $\mathrm{poly}(n)\,e^{O(t)}$, then $O(n^3)$ stabilizer measurements | poly for $t = O(\log^2 n)$ | poly | 🟢 🟢 🟢 in the localized phase $t/f \leq 1$; a stabilizer-entropy phase transition at $t/f = 1$ separates the regime where the magic can be cleansed from $E$ |
| **Gaussian and near-Gaussian states** (fermionic: Aaronson, Grewal 2023; Mele, Herasymenko 2024; bosonic and continuous-variable: Mele et al. 2024) | State | Identifying against a class: Gaussian, Gaussian plus $t$ non-Gaussian gates, or energy-bounded CV states → the state | Sample: free fermions $O(m^3n^2/\epsilon^4)$ copies in $O(m)$ beamsplitter bases; $t$ non-Gaussian gates $\mathrm{poly}(n, 2^t)$ single-copy measurements; CV Gaussian $O(n^7E^4/\epsilon^4)$, $t$-doped $\mathrm{poly}(n) + O((nE/\epsilon)^{2\kappa t})$; generic energy-bounded CV states need $\Omega(\epsilon^{-2n})$ | poly, resp. $\mathrm{poly}(n, 2^t)$; time $e^{\Omega(t)}$ necessary under RingLWE for $t = \tilde\omega(\log n)$ | poly | 🟢 🟢 🟢; Gaussianity promise, the continuous-variable cousin of the stabilizer rows; the same compression theorem holds for stabilizers, fermions, and bosons |
| **Matrix product and finitely correlated states** (Cramer et al. 2010; Fanizza, Galke, Lumbreras, Rouzé, Winter 2023) | State | Identifying against a class: bond dimension $D$ in one dimension → the state; a realization of dimension $m$ for translation-invariant states on the infinite chain | Sample: linearly many local measurement settings with a certified fidelity bound (Cramer et al.); $\mathrm{poly}(t, m, 1/\eta, 1/\epsilon)$ copies of marginals on $2s+1$ sites, $\eta$ the smallest singular value of the Hankel-type matrix (Fanizza et al.) | poly | $O(nD^2)$, resp. $O(m^2d^2)$ | 🟢 🟢 🟢; entanglement-area promise; the first sample guarantee for matrix product density operators from local measurements |
| **States prepared by shallow circuits** (Huang, Liu, Broughton, Kim, Anshu, Landau, McClean, STOC 2024; Landau, Liu 2024) | State | Identifying against a class: $\vert\psi\rangle = U\vert 0^n\rangle$ with $U$ of depth $d$ → a preparation circuit close in trace distance; on a 2D lattice in Huang et al., on any $k$-dimensional lattice in Landau, Liu | Sample: $2^{O(d^2)}(n/\epsilon)^{O(1)}$ copies with single-qubit measurements (2D); $\tilde O(n^4)2^{O(c)}/\epsilon^4$ copies with $c = O((3k)^{k+2}d)^k$ on a $k$-dimensional lattice | poly for $d = O(1)$, quasipolynomial for $d = \mathrm{polylog}(n)$ | poly | 🟢 🟢 🟢; light-cone promise; the replacement process of Landau, Liu avoids every constraint-satisfaction step and gives a polynomial test for the trivial phase |
| **Shallow circuits as unitaries** (Huang, Liu, Broughton, Kim, Anshu, Landau, McClean, STOC 2024) | Unitary | Identifying against a class: unknown constant-depth $U$ of arbitrary architecture → a circuit close to $U$ in diamond distance, via local inversions sewn into a global inverse | Sample on input–output pairs: $O(n^2\log n/\epsilon^2)$ random product inputs with single-qubit Pauli measurements on the outputs, nonadaptive; finite gate set $O(\log n)$ samples with zero error; Query: $\Theta(1)$ uses of $U$ and $\Theta(n)$ time, both optimal | $\mathrm{poly}(n)/\epsilon^2$; $O(n^3\log n/\epsilon^2)$ on a lattice | poly | 🟢 🟢 🟢; light-cone promise; constant depth bounds every light cone, so finding them is a polynomial dictionary, as for juntas; log depth without geometry is exponentially hard |
| **Non-Markovian processes of bounded memory** (White, Pollock, Hollenberg, Modi, Hill, PRX Quantum 2022) | Process over $k$ time steps, its process tensor | Identifying against a class: Markov order $\ell$ → the process tensor, positive and causal, by maximum likelihood | Query: sequences of control operations, $O(N_{\mathrm{oc}}^k)$ circuits by linear inversion with an overcomplete basis, $O(N_{\mathrm{mle}}^k)$ with maximum likelihood, $O(kN_{\mathrm{mle}}^\ell)$ at Markov order $\ell$; $O(d^{4k})$ parameters in general | poly for fixed $\ell$ | $d^{2k+2}$ entries, truncated by $\ell$ | 🟢 🟢 🟢 for finite Markov order; memory length is the dial, and its violation is itself measurable |
| **Phase states of degree $\ell$** (Arunachalam, Bravyi, Dutt, Yoder 2023) | State; also through its preparation circuit | Identifying against a class: $\sum_x (-1)^{f(x)}\vert x\rangle$ with $\deg f \leq \ell$ → the polynomial $f$, exactly | Sample: $\Theta(n^\ell)$ copies with separable measurements (single-qubit $X$ and $Z$), $\Theta(n^{\ell-1})$ with entangled measurements (pretty-good measurement); queries to the preparation circuit give the same counts; $O(n^\ell)$ for $\mathbb{Z}_q$-valued phases | $O(n^{3\ell-2})$ separable; exponential for the pretty-good measurement | poly | 🟢 🟢 🟢 with separable measurements; a proven separable-versus-entangled gap of a factor $n$ in the first budget, paid for with exponential time |
| **Bounded gate complexity** (Zhao, Lewis, Kannan, Quek, Huang, Caro 2023) | State or unitary | Identifying against a class: states or unitaries with at most $G$ gates → an approximation | Sample: $\tilde\Theta(G/\epsilon^2)$ copies, independent of $n$, single-copy measurements suffice; Query: $\tilde O(G\min\{1/\epsilon^2, \sqrt{2^n}/\epsilon\})$ and $\Omega(G/\epsilon)$ for average-case unitary learning, $\Omega(2^{\min\{G/2C, n/2\}}/\epsilon)$ in diamond distance | $e^{\Omega(\min\{G, n\})}$ under RingLWE, already for $G = \tilde\omega(\log n)$; polynomial for $G = O(\log n)$ | poly | 🟢 🔴 🟢; the thesis of this document in one theorem, with $\log n$ gates as the transition point |
| **Output distributions of quantum circuits** (Hinsche et al. 2022; PRL 2023; Nietner et al., Quantum 2025) | Classical distribution of a circuit | Identifying against a class: classical samples of $\vert\langle x\vert U\vert 0\rangle\vert^2$ → a generator or an evaluator for the distribution | Sample (classical outcomes of the circuit): $O(n)$ for Clifford circuits; poly in general | Polynomial for Clifford circuits by Gaussian elimination; hard under LPN for an evaluator once a single $T$ gate is allowed, under pseudorandom functions for a generator at depth $n^{\Omega(1)}$; in the statistical-query model unconditionally $2^{\Omega(d)}$ queries from depth $d = \Omega(\log n)$, on average over random brickwork circuits with constant probability | poly | 🟢 🔴 🟢; the same cryptographic wall as the LWE rows, on the classical side of the measurement, and the only row with an unconditional average-case hardness result |
| **Bernstein–Vazirani** | Classical function | Identifying: the class of $2^n$ linear functions → the label $\mathbf{s}$ | Query: one superposition query | $O(n)$ | $O(n)$ | 🟢 🟢 🟢; the noiseless limit of LWE |
| **Identification with preparation circuits** | State, through its preparation circuit | Identifying: $M$ candidate circuits and a circuit for the unknown → one index, via overlaps on a SWAP test | Query: $\tilde O(M/\epsilon)$ calls at overlap precision $\epsilon$ by amplitude estimation | $\mathrm{poly}(M)$ | $\mathrm{poly}(M)$ | 🟢 🟢 🟢; queries buy the rate in $\epsilon$, not in $M$: copies alone need only $O(\log M/\epsilon^2)$ |

## Identifying protocols

Candidate states, or a class, are the input. Two hypotheses first, then many, then a class with or without a promise, then the one-bit tasks of testing and certification.

## State discrimination: Helstrom vs. USD

Given $\rho_0, \rho_1$ with priors $p_0, p_1$: Which one is present? Two strategies with different notions of error.

* **Helstrom (minimum error):** Answer in every run, average error minimized. Projective measurement onto the sign spectrum of $p_0\rho_0 - p_1\rho_1$:

$$P_{\text{err}}^{\min} = \tfrac{1}{2}\Big(1 - \big\|p_0\rho_0 - p_1\rho_1\big\|_1\Big)$$

* **USD (unambiguous):** Third outcome "undecided", decided answers never wrong. Requires a genuine POVM; the price is the abstention probability, minimally $|\langle\psi_0|\psi_1\rangle|$.

**Many copies and the distance zoo.** With $n$ copies the Helstrom error decays exponentially, $P_{\mathrm{err}} \sim e^{-n\,\xi_{\mathrm{QCB}}}$ with the **quantum Chernoff exponent** $\xi_{\mathrm{QCB}} = -\log\min_{0\leq s\leq 1}\mathrm{Tr}(\rho_0^s\rho_1^{1-s})$ (Audenaert et al., PRL 2007). The single-shot quantity is the trace distance $D = \frac12\|\rho_0-\rho_1\|_1$; it is sandwiched by the fidelity via Fuchs–van de Graaf, $1 - F \leq D \leq \sqrt{1-F^2}$, which is why tomography guarantees are quoted interchangeably in either metric. ⚠️ For *learning* (many hypotheses, not two) the relevant quantity is not $D$ but the packing number of the hypothesis class in $D$; that is where the $d^2$ of full tomography comes from.

## Property testing, certification, hypothesis selection

Tasks whose answer is one bit or one index; the identifying column.

* **Montanaro, de Wolf (2016):** Survey of quantum property testing.
* **O'Donnell, Wright (STOC 2015) / Bubeck, Chen, Li (FOCS 2020) / Chen, Cotler, Huang, Li (FOCS 2021):** Spectrum, mixedness, and purity testing; where entanglement across copies is necessary.
* **Huang, Broughton, Cotler, Chen, Li, Mohseni, Neven, Babbush, Kueng, Preskill, McClean (Science 2022):** The memory separations in hardware: $\vert\mathrm{Tr}(P\rho)\vert$ for a Pauli named after the measurement, $O(1)$ copies with two-copy Bell measurements against $\Omega(2^n)$ without memory, even for unentangled $\rho$; quantum PCA $O(1)$ against $\Omega(2^{n/2})$; time-reversal symmetry of an unknown circuit by unsupervised learning; up to 40 qubits on Sycamore.
* **Chen, Huang, Li, Liu (FOCS 2022):** Mixedness testing with incoherent measurements costs $\Theta(d^{3/2}/\epsilon^2)$, adaptive or not; instance-optimal bounds for certification against a known $\sigma$ in terms of $F(\sigma, I/d)$ and the effective dimension.
* **Gross, Nezami, Walter (CMP 2021):** Stabilizer testing with six copies. **Arunachalam, Dutt (2024) / Chen, Gong, Ye, Zhang (2024):** tolerant versions in polynomial time. **Bao, van Dordrecht, Helsen (2024):** an unconditional polynomial gap, $\epsilon_2 \leq C'\epsilon_1^{672}$ with $O(\epsilon_1^{-12})$ Bell-difference rounds, from a generalized uncertainty relation through the Lovász theta number.
* **Leone, Oliviero, Esposito, Hamma (PRA 2024):** Stabilizer-entropy phase transition at $t/f = 1$; in the localized phase the purity of a $t$-doped state is computable up to a factor $4^t$ with $\mathrm{poly}(n)$ resources, even when it is exponentially small.
* **White, Pollock, Hollenberg, Modi, Hill (PRX Quantum 2022):** Process-tensor tomography for non-Markovian dynamics by maximum likelihood; $O(kN^\ell)$ circuits at Markov order $\ell$ instead of $O(N^k)$.
* **Bădescu, O'Donnell (STOC 2021):** Threshold search and hypothesis selection with $O(\log M)$ copies.
* **Huang, Preskill, Soleimanifar (FOCS 2024):** Certifying almost all states with few single-qubit measurements.

**Notes on the identification rows.** Hypothesis selection at $O(\log M)$ copies comes from the *threshold search* primitive of Bădescu–O'Donnell (STOC 2021), the same tool that improved shadow tomography to $\tilde O(\log^2 M \cdot \log d/\epsilon^4)$. Agnostic tomography is the learning-theoretic analogue of agnostic PAC learning; Grewal–Iyer–Kretschmer–Liang (2024) and Chen–Gong–Ye–Zhang ("stabilizer bootstrapping", 2024) give polynomial-time algorithms for stabilizer and near-stabilizer classes, both driven by Bell difference sampling. By the LWE rule, their row and their summaries sit under searching.

## Learning classes of states: the promise catalogue

Every 🟢 🟢 🟢 row in the identifying and searching tables names a class. Listed by the structure that makes decoding cheap, with the paper that proved it. The first three items, the stabilizer family, sit in the searching table by the LWE rule.

* **Stabilizer states** (subgroup structure): Aaronson, Gottesman (2004) with $O(n)$ collective or $O(n^2)$ single-copy measurements; Montanaro (2017) with $O(n)$ two-copy Bell samples; Rocchetto (2018) in the PAC model; Low (2009) for Clifford unitaries; Allcock, Doriguello, Ivanyos, Santha (2024) on qudits, where Bell sampling breaks.
* **Few non-Clifford gates** (magic as the dial): Lai, Cheng (2022); Grewal, Iyer, Kretschmer, Liang (2023); Leone, Oliviero, Hamma (Quantum 2024); Hangleiter, Gullans (PRL 2024). Cost $\mathrm{poly}(n, 2^t)$ in copies and time.
* **Agnostic and tolerant versions**: Grewal, Iyer, Kretschmer, Liang (2024) for stabilizer product states; Chen, Gong, Ye, Zhang (2024), stabilizer bootstrapping; Arunachalam, Dutt (2024) and Bao, van Dordrecht, Helsen (2024), tolerant stabilizer testing in polynomial time. All driven by Bell difference sampling, whose group-theoretic origin is the Clifford Schur–Weyl duality of Gross, Nezami, Walter (2021).
* **Gaussian and near-Gaussian states** (the continuous-variable analogue of stabilizer structure): Aaronson, Grewal (2023) for free fermions; Mele, Herasymenko (2024) with $t$ non-Gaussian gates; Mele et al. (2024) for bosonic and continuous-variable states with bounded energy. Displacement operators are the discrete shadow of this family.
* **Matrix product and finitely correlated states** (area-law entanglement): Cramer et al. (Nat. Commun. 2010); Fanizza, Galke, Lumbreras, Rouzé, Winter (2023) with stability guarantees, the first sample bound for matrix product density operators from local measurements.
* **Processes with finite Markov order** (memory length as the dial): White, Pollock, Hollenberg, Modi, Hill (PRX Quantum 2022), process-tensor tomography with maximum likelihood, efficient once long-time correlations are truncated at order $\ell$.
* **Shallow-circuit states and circuits** (light cones): Huang, Liu, Broughton, Kim, Anshu, Landau, McClean (STOC 2024) learn states $U\vert 0^n\rangle$ from copies with single-qubit measurements, and unknown constant-depth unitaries of arbitrary architecture from random product inputs, which is sample access to input–output pairs; both in polynomial time. The technique is local inversion: learn, for each qubit, a local unitary that undoes $U$ there, then sew these into a global inverse; the landscape of each local problem is benign, which is what makes the time budget polynomial. Landau, Liu (2024) extend the state result beyond the 2D lattice.
* **Phase states of bounded degree** (algebraic structure): Arunachalam, Bravyi, Dutt, Yoder (TQC 2023), $\Theta(n^\ell)$ copies with separable measurements against $\Theta(n^{\ell-1})$ with entangled ones (pretty-good measurement); queries to the preparation circuit give the same counts, so the proven gap is between measurement classes, not between sample and query access.
* **Juntas and low-degree objects** (few relevant qubits, few relevant Paulis): Chen, Nadimpalli, Yuen (SODA 2023); Arunachalam, Dutt, Escudero Gutiérrez (2024).
* **Bounded gate complexity** (the class that is sample-easy and time-hard): Zhao, Lewis, Kannan, Quek, Huang, Caro (PRX Quantum 2024).

The catalogue reads as a list of promises, and that is the point of the tables: outside of it, no polynomial-time learner is known, and the LWE, pseudorandomness, and gate-complexity results say that none should be expected in general.

<br>

# Identifying (Papers)

Summaries of the key papers on the task type **identifying**: the candidates are the input. Given are copies of a state, calls to a process, or classical samples of a distribution, together with a list of hypotheses or a class, with or without the promise that the unknown lies in the class. Returned is an index, an element of the class, or one bit. The section orders the papers by the size of the hypothesis set: first the classes whose structure makes the decoder cheap (Gaussian, matrix product, shallow circuits, phase states), then the one-bit tasks (testing and certification), finally the hardness results, in which the class is exponentially large and parametrized and the task shades into searching (pseudorandomness, bounded gate complexity, output distributions).

Every summary follows the same structure as in the searching and estimating sections: placement in the tables, problem, key results, method, significance, relation to this project, limitations and open questions, questions for further study. The status glyphs read in the order copies · time · memory. The stabilizer family, including few non-Clifford gates (arXiv:2305.13409, arXiv:2306.00083) and agnostic tomography (arXiv:2404.03813, arXiv:2408.06967), sits in the searching section by the LWE rule (Appendix, "Reading the tables").

## Overview

| Paper | Object | What is identified | Access | Cost | Status | Promise |
| --- | --- | --- | --- | --- | --- | --- |
| Leone, Oliviero, Esposito, Hamma 2024 | State from a $t$-doped Clifford circuit | subsystem purity $\mathrm{Pur}(\psi_E)$, even when exponentially small | Query to $C_t$ (Clifford completion), then stabilizer measurements | $\mathrm{poly}(n)\,e^{O(t)}$, polynomial for $t = O(\log^2 n)$; uncertainty factor $d_Y^2 = 4^t$ | 🟢 🟢 🟢 for $t/f\leq 1$ (localized phase) | $t$-doped, $t/f\leq 1$ |
| Aaronson, Grewal 2023 | State of $n$ free fermions on $m$ modes | the kernel matrix $K = AA^\dagger$, i.e. the state | Sample, $O(m)$ measurement bases from beamsplitters | $O(m^3n^2/\epsilon^4)$ copies, $O(m^4n^2/\epsilon^4)$ time | 🟢 🟢 🟢 | particle-number-preserving Gaussian |
| Mele, Herasymenko 2024 | State from a Gaussian circuit with $t$ non-Gaussian gates | Gaussian unitary $G$ and $t$-qubit core $\vert\phi\rangle$ | Sample, single copies | $\mathrm{poly}(n, 2^t)$; hard for $t = \tilde\omega(\log n)$ under PRS | 🟢 🟢 🟢 up to $t = O(\log n)$ | Gaussian nullity $\leq\kappa t$ |
| F. A. Mele, A. A. Mele, Bittel, Eisert, Giovannetti, Lami, Leone, Oliviero 2024 | CV state on $n$ modes | Gaussian state, $t$-doped Gaussian state; general at energy $E$ | Sample, homodyne/heterodyne | Gaussian $O(n^7E^4/\epsilon^4)$; $t$-doped $\mathrm{poly}(n) + O((nE/\epsilon)^{2\kappa t})$; general $\Omega(\epsilon^{-2n})$ | 🟢 🟢 🟢 for Gaussian and $\kappa t = O(1)$; 🔴 in general | energy bound, Gaussian promise |
| Cramer, Plenio, Flammia, Somma, Gross, Bartlett, Landon-Cardinal, Poulin, Liu 2010 | State on a chain | matrix product state of bond dimension $D$ | Sample, local measurements (scheme 2) or local unitaries plus measurements (scheme 1) | linearly many measurement settings, $\mathrm{poly}(N)$ post-processing, certified fidelity | 🟢 🟢 🟢 | MPS with small $D$; scheme 2 needs a gapped parent Hamiltonian |
| Fanizza, Galke, Lumbreras, Rouzé, Winter 2023 | Translation-invariant state on the chain | MPDO realization: $\rho$, $e$, transfer matrices $E_{k,l}$ | Sample, local tomography of the marginals on $2s+1$ sites | $\mathrm{poly}(t, m, 1/\eta, 1/\epsilon)$ copies, $O(m^2)$ parameters | 🟢 🟢 🟢 | dimension $m$, $s$-reconstructible, singular value $\geq\eta$ |
| Huang, Liu, Broughton, Kim, Anshu, Landau, McClean 2024 | Constant-depth unitary; state $U\vert 0^n\rangle$ on a 2D lattice | a constant-depth circuit | Sample on product inputs and Pauli outputs; query; copies | $O(n^2\log n/\epsilon^2)$ samples, $\mathrm{poly}(n)/\epsilon^2$ time; $\Theta(1)$ queries for a finite gate set; states $2^{O(d^2)}(n/\epsilon)^{O(1)}$ copies | 🟢 🟢 🟢 | constant depth; 2D for states |
| Landau, Liu 2024 | State $U\vert 0^n\rangle$ on a $k$-dimensional lattice | a circuit of depth $(2k+1)d$ | Sample, local tomography of the reductions | $\tilde O(n^4)2^{O(c)}/\epsilon^4$ copies, $c = O((3k)^{k+2}d)^k$ | 🟢 🟢 🟢 for $d = O(1)$ | depth $d$ on a lattice of arbitrary dimension |
| Arunachalam, Bravyi, Dutt, Yoder 2023 | Phase state of degree $\ell$ | the polynomial $f$ | Sample, separable or entangled; query to the preparation unitary | $\Theta(n^\ell)$ separable, $\Theta(n^{\ell-1})$ entangled (PGM) | 🟢 🟢 🟢 separable; PGM time-inefficient | degree $\ell$ over $\mathbb{F}_2$ or $\mathbb{Z}_q$ |
| Gross, Nezami, Walter 2021 | State | stabilizer or $\epsilon$-far from all of them | Sample, six copies, transversal | $O(1/\epsilon^2)$ repetitions, three copies for $d\equiv 1, 5 \bmod 6$ | 🟢 🟢 🟢 | none; one-bit test |
| Bao, van Dordrecht, Helsen 2024 | State | stabilizer fidelity $\geq\epsilon_1$ or $\leq\epsilon_2$ | Sample, Bell difference sampling | $O(\epsilon_1^{-12})$ rounds at $\epsilon_2\leq C'\epsilon_1^{672}$ | 🟢 🟢 🟢 | none; tolerant test |
| Chen, Cotler, Huang, Li 2021 | State, channel | pure or maximally mixed; depolarizing or unitary; $U$, $O$, or $Sp$ | Sample without quantum memory (tree model), with $k$ qubits of memory | $\Theta(2^{n/2})$ without memory, $O(1)$ with; shadow tomography $\tilde\Theta(\min\{M, 2^n\}/\epsilon^2)$; $\Omega(2^{(n-k)/3})$ at $k$ qubits | 🟢 🔴 🟢 without memory | none; separations by memory |
| Huang, Broughton, Cotler, Chen, Li, Mohseni, Neven, Babbush, Kueng, Preskill, McClean 2022 | State, process, unitary | $\vert\mathrm{Tr}(P\rho)\vert$ for a Pauli named afterwards; property of the principal component; symmetry class ($T$-symmetric or general) | Sample with two-copy Bell measurement; for dynamics two calls with $n$ memory qubits; hardware up to 40 qubits | $O(1)$ against $\Omega(2^n)$ resp. $\Omega(2^{n/2})$ without memory; processes $\tilde O(\mathrm{poly}(n)/\epsilon^4)$ without a time guarantee | 🟢 🟢 🟢 with memory | none; instance $2^{-n}(I + 0.9sP)$, unentangled |
| Chen, Huang, Li, Liu 2022 | Mixed state | $\rho = \sigma$ or $\Vert\rho-\sigma\Vert_1 > \epsilon$ | Sample, incoherent, adaptive allowed | $\Theta(d^{3/2}/\epsilon^2)$ for mixedness; instance-optimal in $F(\sigma, I/d)$ and the effective dimension | 🟢 🟢 🟢 with $d^{3/2}$ copies; adaptivity does not help | none |
| Aharonov, Cotler, Qi 2022 | Unitary as a lab oracle | fixed or fresh Haar unitary; $U$, $O$, or $Sp$ | Oracle, coherent or incoherent | $O(1)$ coherent, $\Omega(2^{2\ell/7})$ incoherent | 🟢 🟢 🟢 coherent | none; defines QUALM |
| Huang, Preskill, Soleimanifar 2024 | State $\rho$ against a known $\vert\psi\rangle$ | $\langle\psi\vert\rho\vert\psi\rangle\geq 1-\epsilon$ or $< 1-\epsilon$ | Sample, single-qubit Pauli measurements; query to an amplitude model | $O(\tau^2/\epsilon^2)$, $O(n^2/\epsilon)$ for almost all states | 🟢 🟢 🟢 | relaxation time $\tau = \mathrm{poly}(n)$ |
| White, Pollock, Hollenberg, Modi, Hill 2022 | Non-Markovian process over $k$ time steps | process tensor at Markov order $\ell$ | Query, sequences of control operations | $O(N_{\mathrm{mle}}^k)$ circuits, $O(k N_{\mathrm{mle}}^\ell)$ at order $\ell$; $d^{4k}$ parameters | 🟢 🟢 🟢 for fixed $\ell$ | finite Markov order |
| Ji, Liu, Song 2018 | State family $\{\vert\phi_k\rangle\}$ | PRS or Haar-random | Sample, polynomially many copies | poly copies suffice statistically, no poly-time distinguisher | 🟢 🔴 🟢 | existence of quantum-secure PRFs |
| Aaronson, Bouland, Fefferman, Ghosh, Vazirani, Zhang, Zhou 2022 | State family | entanglement $\Theta(n)$ or $\omega(\log n)$ across every cut | Sample, polynomially many copies | no poly-time distinguisher; MPS testing needs $\Omega(\sqrt r)$ copies | 🟢 🔴 🟢 | quantum-secure one-way function |
| Zhao, Lewis, Kannan, Quek, Huang, Caro 2023 | State or unitary with $G$ gates | an $\epsilon$-close approximation | Sample; query | $\tilde\Theta(G/\epsilon^2)$ copies; time $e^{\Omega(\min\{G, n\})}$ under RingLWE | 🟢 🔴 🟢 | gate count $G$ |
| Hinsche, Ioannou, Nietner, Haferkamp, Quek, Hangleiter, Seifert, Eisert, Sweke 2023 | Output distribution of a circuit | generator or evaluator | Sample, classical bit strings | Clifford: $O(n)$ samples, poly time; one $T$ gate: LPN-hard | 🟢 🔴 🟢 | Clifford structure |
| Nietner, Sweke, Hinsche, Ioannou, Haferkamp, Quek, Hangleiter, Seifert, Eisert 2025 | Output distribution of a random brickwork circuit | an $\epsilon$-close generator, on average | Statistical queries | $2^{\Omega(d)}$ queries from depth $d = \Omega(\log n)$ with constant probability; $\Omega(2^n)$ at linear depth | 🟢 🔴 🟢 in the SQ model | none; average case |

Three families. The first learns a class whose structure carries the decoder: subgroups (here only the Clifford hull of $t$-doped states; stabilizer learning itself sits under searching by the LWE rule), covariance matrices (Gaussian), transfer matrices (matrix product), light cones (shallow circuits), polynomials (phase states); the costs are polynomial, and the hardness sits in a single parameter ($t$, $D$, $d$, $\ell$). The second returns one bit, and there the memory axis decides: Bell difference sampling and the SWAP test need two copies and constantly many rounds, incoherent protocols pay $d^{3/2}$ or $2^{n/2}$. The third proves that outside the catalogue no polynomial-time decoder exists, each conditional on a cryptographic assumption; this is the identifying version of the LWE wall from the searching table.

## Phase transition in stabilizer entropy and efficient purity estimation (arXiv:2302.07895)

The paper by **Lorenzo Leone, Salvatore F. E. Oliviero, Gianluca Esposito, and Alioscia Hamma** (UMass Boston, Napoli; Phys. Rev. A 2024) shows that the stabilizer entropy of a $t$-doped Clifford state can be localized in a subsystem by a Clifford map and erased there, as long as the density $t/n$ of non-Clifford gates stays below the density $f = n_F/n$ of the auxiliary qubits; at $t/f = 1$ there is a phase transition with critical exponent one. In the localized phase, this "purification" allows the estimation of exponentially small subsystem purities with polynomial resources.

### Placement in the tables

* **Task type:** Estimating of a single quantity ($\mathrm{Pur}(\psi_E)$), but via an identifying step: first the Clifford structure of the circuit is learned (the diagonalizer $D$ with $C_t = D^\dagger c_tDV$), then the stabilizer formalism does the computation. The row sits under identifying because the effort lies in identifying the class.
* **Object:** state $\psi_t = C_t\vert 0\rangle\langle 0\vert C_t^\dagger$ from a $t$-doped Clifford circuit. **Access:** query to $C_t$ for the Clifford completion (Leone, Oliviero, Hamma 2022), $\mathrm{poly}(n)\,e^{O(t)}$ calls; afterwards $O(n^3)$ stabilizer measurements.
* **Status:** 🟢 🟢 🟢 for $t = O(\log^2 n)$ in the localized phase; the purity is determined up to a factor $d_Y^2 = 4^t$, i.e. $\mathrm{Pur}(\psi_E) = 2^{-\alpha n + O(\log^2 n)}$.
* **Promise:** $t$-doped with $t/f\leq 1$; the bipartition is not exactly half ($f < 1/2$).

### The problem

The SWAP test estimates a purity to $\epsilon$ with $O(\epsilon^{-2})$ copies; for volume-law states $\mathrm{Pur}(\psi_E) = \Theta(e^{-\beta n})$, and the test needs exponentially many copies. At the same time, a Clifford circuit typically spreads the stabilizer entropy (nonstabilizerness) completely into the larger subsystem $E$ (Proposition 1: $\mathbb{E}_C[M_{\mathrm{lin}}(\psi_E^C)] = M_{\mathrm{lin}}(\psi) + O(d_F/d_E)$, $\mathbb{E}_C[M_{\mathrm{lin}}(\psi_F^C)] = O(d_F/d_E)$). Can $E$ be purified of this complexity?

### Key results

* **Proposition 2 (purification).** For $n_Y\leq n_F$ there is a Clifford map $\mathcal{E}(\cdot) = \mathrm{Tr}_Y W(\cdot)W^\dagger$ with $W = T_{\pi_Y}D$ that moves the $t$ non-Clifford gates into a subsystem $Y\subset F$ with $n_Y = t$ and erases them by tracing out: $M_E[\mathcal{E}(\psi_t)] = 0$.
* **Phase transition (Section III).** Averaged over maps and stabilizer inputs, $\mathbb{E}[M_E(\mathcal{E}\circ\mathcal{C}_t[\omega])] = 0$ for $t/f\leq 1$ and $\geq g(n, t, f)$ for $t/f\geq 1$, with $g_\infty\simeq n(1-2f)$ and $g/g_\infty\simeq\tfrac{f}{1-f}(t/f-1)$ near criticality.
* **Propositions 3 and 4 (purity bounds).** The re-entangled stabilizer state $\rho = W^\dagger(\mathcal{E}(\psi_t)\otimes d_Y^{-1}I_Y)W$ satisfies $\mathrm{Pur}(\rho_X)\leq\mathrm{Pur}(\psi_E)\leq d_Y^2\mathrm{Pur}(\rho_X)$.
* **Protocol.** $t = O(\log^2 n)$: learn the diagonalizer ($\mathrm{poly}(n)$), prepare $\rho$, learn the stabilizer group of $\rho$ with $O(n^3)$ measurements, compute the purity exactly from the group; then either a SWAP test with a known shot count (case $\mathrm{Pur} = \Omega(1/\mathrm{poly})$) or the direct bound $2^{-\alpha n + O(\log^2 n)}$ (exponentially small case).

### Methodological approach

* Lemma 1 (Clifford averaging): over the Clifford orbit, the average of the ratio $\mathrm{SP}/\mathrm{Pur}$ equals the ratio of the averages up to a relative error $O(2^{-n(1-2f)/2})$; this is why the statements are sharp for typical circuits.
* The purification uses permutations $T_\pi$ (themselves Clifford) to move the $t$-qubit piece $c_t$ into an arbitrary subsystem $Y$.
* The analogy: spreading (Clifford depth) against localizing (density $f$), like an insulator–superfluid transition.

### Significance and applications

* Determining an exponentially small purity with polynomial effort is an exponential advantage over the SWAP test and classical shadows for this class.
* Stabilizer entropy is understood as a movable resource; this is the operational side of the magic compression that Grewal et al. and Hangleiter–Gullans use for learning.

### Relation to this project

* The route "first identify the Clifford hull, then compute in the stabilizer formalism" is the identifying variant of the two-phase scheme: Phase 1 finds the structure, Phase 2 measures exactly within the structure. The factor $d_Y^2 = 4^t$ is the price of the unknown magic; it corresponds to the $2^t$ factor in the searching table (row "Clifford plus few non-Clifford gates").
* Purity is $\sum_D\vert\mathrm{Tr}(\rho D)\vert^2/d$, i.e. the $\ell_2$ mass of the displacement spectrum; Bell sampling on $\rho\otimes\rho^*$ draws directly from this distribution, and the question of exponentially small purity is the question of a very flat spectrum without heavy addresses. The paper says that for doped Clifford states the flatness can be computed exactly instead of sampled.
* The bipartition condition $f < 1/2$ and the phase boundary $t/f = 1$ form an instance ladder for entanglement quantities.

### Limitations and open questions

* Needs query access to the circuit $C_t$, not just copies of the state; the Clifford completion costs $e^{O(t)}$.
* Only up to $t = O(\log^2 n)$ and in the localized phase; for $t/f > 1$ the entropy stays in $E$.
* The purity bound has an uncertainty of $4^t$; in the polynomial case the SWAP test is still needed.
* Transfer to Hamiltonian dynamics, error correction, and holographic entropy are named as open questions.

### Questions for further study

* How does the Clifford completion work concretely, and is it a Bell-sampling algorithm on the Choi state of $C_t$?
* Why is the critical exponent one, and is $g(n, t, f)$ a statement about expectation values or one with concentration?
* Can the purification be verified with Bell sampling on $\rho\otimes\rho^*$, by checking whether the spectrum of the purified state is concentrated on a subgroup?

Paper: [arXiv:2302.07895](https://arxiv.org/abs/2302.07895)

---

## Efficient tomography of non-interacting fermion states (arXiv:2102.10458)

The paper by **Scott Aaronson and Sabee Grewal** (UT Austin; TQC 2023) gives a tomography algorithm for states of $n$ non-interacting fermions on $m$ modes: $O(m^3n^2\log(1/\delta)/\epsilon^4)$ copies, $O(m^4n^2\log(1/\delta)/\epsilon^4)$ classical time, $O(m)$ measurement bases, and the output is a free-fermion state within total variation distance $\leq\epsilon$ in the occupation basis. The algorithm estimates the kernel matrix $K = AA^\dagger$ (the one-particle density matrix) from beamsplitter measurements and rounds it to a projection.

### Placement in the tables

* **Task type:** Identifying against a class with a promise. The class of Slater determinants is described by $O(mn)$ real parameters; returned is a column-orthonormal matrix $\hat A$.
* **Object:** pure state $\vert\Psi\rangle = \sum_S\det(A_S)\vert S\rangle$ over $\Lambda_{m,n}$. **Access:** sample; measurements in the occupation basis after beamsplitters on mode pairs $(i, j)$, i.e. $O(m)$ settings with $O(\log(1/\delta)/\gamma^2)$ shots each.
* **Status:** 🟢 🟢 🟢. Copies $O(m^3n^2/\epsilon^4)$, time $O(m^4n^2/\epsilon^4)$, memory $O(m^2)$ for $K$.
* **Promise:** particle-number conservation and Gaussianity ($t = 0$); Mele–Herasymenko lift both.

### The problem

Free fermions are classically simulable and fully determined by the kernel matrix: the probability of a configuration $S$ is the principal minor $\det(K_S)$, a determinantal point process. Can the state be learned from polynomially many copies and simple measurements, with a guarantee in distance?

### Key results

* **Theorem 1.1 (main result).** Copies $O(m^3n^2\log(1/\delta)/\epsilon^4)$, time $O(m^4n^2\log(1/\delta)/\epsilon^4)$, $O(m)$ measurement bases; output $\vert\hat\Psi\rangle$ within total variation distance $\leq\epsilon$ with probability $\geq 1-\delta$.
* **Theorem 1.2 / 4.3 (perturbation bound).** If the kernel matrices of two states are close, the states are close; the proof goes through Weyl's inequality (Theorem 4.4) for the eigenvalues of $\hat K$.
* **Section 5.** Adaptation to trace distance instead of total variation, i.e. conventional tomography.

### Methodological approach

* Diagonal entries $k_{ii}$ (occupation probabilities) from the standard basis; $\mathrm{Re}\,k_{ij}$ and $\mathrm{Im}\,k_{ij}$ from two beamsplitters $\tfrac{1}{\sqrt2}\binom{1\ \ 1}{1\ -1}$ and $\tfrac{1}{\sqrt2}\binom{1\ \ i}{1\ -i}$ on $(i, j)$, which map $k_{ii}$ to $\tfrac12(k_{ii} + k_{jj} + 2\mathrm{Re}\,k_{ij})$. All pairs simultaneously in $O(m)$ rounds ("round robin").
* Eigendecomposition $\hat K = Q\Lambda Q^\dagger$; the $n$ leading eigenvectors form $\hat A$; Weyl controls how errors in $\hat K$ enter $\hat A$.
* The connection to determinantal point processes gives the interpretation of the measurement statistics.

### Significance and applications

* Free fermions are the Gaussian class of fermions; the paper is the reference point for Mele–Herasymenko ($t$ non-Gaussian gates, no particle-number conservation) and for matchgate shadows (Wan et al.).
* Chemistry and condensed-matter context: Hartree–Fock states are exactly this class.

### Relation to this project

* The algorithm is an estimating protocol ($O(m^2)$ observables of the one-particle density matrix), followed by rounding onto the class; this is the "identifying via estimating" pattern that arises in Phase 1 with the displacement spectrum and in Phase 2 with the rounding to $k$-sparse.
* The $O(m)$ measurement bases correspond to a decomposition of the observables into commuting families; the round robin over mode pairs is the fermionic version of the commutation classes of Pauli strings.
* The $\epsilon^{-4}$ rate comes from the rounding (Weyl); where Bell sampling delivers the magnitudes directly, this is the reference value for the cost of a subsequent class projection.

### Limitations and open questions

* $\epsilon^{-4}$ instead of $\epsilon^{-2}$; Mele et al. reach the same order for Gaussian states with covariance estimation, and the optimal rate is open.
* Pure, particle-number-conserving states only; mixed Gaussian states and non-Gaussianity need the follow-up works.
* No lower bound in the paper.

### Questions for further study

* Is the perturbation analysis via Weyl tight, or does the Wedin bound for eigenspaces give a better $\epsilon$ dependence?
* What is the displacement analogue of the kernel matrix, i.e. which $O(m^2)$ expectation values determine a Gaussian state in the qudit phase space?
* How does the beamsplitter strategy compare with matchgate shadows, which estimate the same quantities with random bases?

Paper: [arXiv:2102.10458](https://arxiv.org/abs/2102.10458)

---

## Efficient learning of quantum states prepared with few fermionic non-Gaussian gates (arXiv:2402.18665)

The paper by **Antonio Anna Mele and Yaroslav Herasymenko** (FU Berlin; QuSoft/CWI, QuTech; PRX Quantum 2025) carries the magic compression of Clifford+T over to fermions: every state prepared by arbitrarily many Gaussian gates and at most $t$ local non-Gaussian gates can be brought by a Gaussian unitary into the form $G(\vert\phi\rangle\otimes\vert 0^{n-\kappa t}\rangle)$. From this follow a learning algorithm with single-copy measurements and cost $\mathrm{poly}(n, 2^t)$, a hardness bound $\exp(\Omega(t))$ under RingLWE from $t = \tilde\omega(\log n)$ on, a test for the Gaussian dimension, and an improved circuit complexity $O(n^2 + t^3)$.

### Placement in the tables

* **Task type:** Identifying against a class with a promise ($t$-compressible, equivalently Gaussian nullity $\leq t$); in addition a one-bit test (close to or far from the class) and a hardness statement that pushes the class into the 🔴 rows at $t = \tilde\omega(\log n)$.
* **Object:** pure state on $n$ fermionic modes or, via Jordan–Wigner, on $n$ qubits prepared by matchgates with $t$ SWAP gates. **Access:** sample, single-copy measurements only; Pauli basis, Gaussian Clifford measurements, or fermionic shadows for the correlation matrix.
* **Status:** 🟢 🟢 🟢 up to $t = O(\log n)$: $O(n^5)$ for the correlation matrix plus $\exp(t)$ for the $t$-qubit tomography. Time exponential in $t$ is necessary (Theorem 5).
* **Promise:** $(t, \kappa)$-doped, or more generally $\kappa t$-compressible; also approximately compressible and mixed states.

### The problem

Free fermions are learnable (Aaronson–Grewal), and so are $t$-doped stabilizer states; Gaussian circuits with few magic gates have recently become classically simulable. Are they learnable, and where is the boundary in $t$?

### Key results

* **Theorem 3 (compression).** Every $(t, \kappa)$-doped Gaussian state is $\kappa t$-compressible: $\vert\psi\rangle = G(\vert\phi\rangle\otimes\vert 0^{n-\kappa t}\rangle)$. For unitaries $U_t = G_A(u_t\otimes I)G_B$ with $u_t$ on $\lceil\kappa t/2\rceil$ qubits; particle-number conservation is preserved. Constructive proof via the existence of a symplectic-orthogonal $O_{\mathrm{aux}}$.
* **Theorem 4 (learning).** Algorithm 1 learns every $t$-compressible state with $O(\mathrm{poly}(n, 2^t))$ single-copy measurements and time to trace distance $\epsilon$: correlation matrix from $\lceil 256n^5\epsilon^{-4}\log(12n^2/\delta)\rceil$ measurements, normal form $\hat C = \hat O\hat\Lambda\hat O^T$, apply $\hat G^\dagger$, measure the last $n-t$ qubits, postselect on $0^{n-t}$, $t$-qubit tomography.
* **Theorem 5 (hardness).** If a quantum computer cannot solve RingLWE in subexponential time, there is no time-efficient learner for $\tilde\omega(\log n)$-doped Gaussian states; proof by embedding pseudorandom states via a qubit-to-fermion map with constant overhead.
* **Eq. (5) (test).** $\tfrac12(1-\lambda_{t+1})\leq\min_{\phi\in\mathcal{G}_t}d_{\mathrm{tr}}(\psi, \phi)\leq\sqrt{\sum_{k>t}(1-\lambda_k)/2}$ with the normal eigenvalues $\lambda_k$ of the correlation matrix; the distance to the class can be estimated efficiently from the correlation matrix.
* **Proposition 30.** Circuit complexity $O(n^2 + t^3)$ instead of $O(n^2t)$; ground states of impurity models are approximately $O(\log n)$-compressible.

### Methodological approach

* Gaussian dimension = number of normal eigenvalues equal to one; Gaussian nullity $\leq t$ if and only if $t$-compressible. The correlation matrix $C(\rho)_{jk} = -\tfrac{i}{2}\mathrm{Tr}(\gamma_j\gamma_k\rho)$ is the only global quantity that has to be estimated; everything else is local.
* Quantum union bound and Chernoff for the postselection; the $t$ dependence is optimal, because an arbitrary $t$-qubit state is contained.
* For the hardness, PRS constructions are realized with local non-Gaussian gates, with $O(1)$ overhead per qubit.

### Significance and applications

* The same compression theorem holds for stabilizers, fermions, and (Mele et al. 2024) bosons; the three theories share a common structure although their mathematics looks different.
* Physical target states: impurity models, time evolution under impurity Hamiltonians up to constant times; experimentally only simple fermion Hamiltonians are needed, hence suited to analogue simulators.
* Classical shadows learn $t$-doped states with $\mathrm{poly}(n, t)$ copies but time exponential in $n$; here polynomial in $n$, exponential in $t$: the sample–time gap is explicit.

### Relation to this project

* The logic "estimate one global but quadratically large quantity, then solve a small residual problem" is the structure of Phase 1 (displacement magnitudes) and Phase 2 (signs on the support). The correlation matrix is the Gaussian case of the displacement spectrum: for Gaussian states, $\vert\mathrm{Tr}(\rho D)\vert^2$ is a Gaussian function of the address, fully determined by the covariance.
* The test for Gaussian dimension via the eigenvalues $\lambda_k$ is an example of a class test that follows from the same measurement as learning; this is the role that the purity check from Bell sampling plays in this project's pipeline.
* The hardness at $t = \tilde\omega(\log n)$ is the fermionic version of the LWE wall; it confirms that the instance ladder in $t$ breaks off at logarithmic height.

### Limitations and open questions

* $O(n^5)$ for the correlation matrix can presumably be improved; $\epsilon^{-4}$ as in Aaronson–Grewal.
* Pure, exactly compressible states in the main part; mixed and approximate cases in the supplement.
* The gap between $O(\log n)$ (efficient) and $\tilde\omega(\log n)$ (hard) is closed up to polyloglog factors.

### Questions for further study

* What does the symplectic-orthogonal $O_{\mathrm{aux}}$ look like concretely, and is the construction numerically stable?
* What is the displacement translation of the compression theorem for qudits: is there a "Clifford compression" of $t$ non-Clifford gates onto $O(t)$ qudits with the same proof idea?
* How fast does the time evolution under an impurity model leave approximate compressibility, and is that a statement about the growth of the displacement support?

Paper: [arXiv:2402.18665](https://arxiv.org/abs/2402.18665)

---

## Learning quantum states of continuous-variable systems (arXiv:2405.01431)

The paper by **Francesco A. Mele, Antonio A. Mele, Lennart Bittel, Jens Eisert, Vittorio Giovannetti, Ludovico Lami, Lorenzo Leone, and Salvatore F. E. Oliviero** (SNS Pisa, FU Berlin, Amsterdam; 2024) is the first systematic study of continuous-variable tomography with a trace-distance guarantee. Three results: energy-constrained states on $n$ modes need at least $\epsilon^{-2n}$ copies ("extreme inefficiency"); Gaussian states are learnable from $O(n^7E^4/\epsilon^4)$ copies; $t$-doped Gaussian states from $\mathrm{poly}(n) + O((nE/\epsilon)^{2\kappa t})$, efficient for $\kappa t = O(1)$.

### Placement in the tables

* **Task type:** Identifying against the class of Gaussian and $t$-doped Gaussian states; for general energy-constrained states it is full tomography with a lower bound, i.e. the 🔴 reference of the CV world.
* **Object:** state on $n$ bosonic modes with $\mathrm{Tr}[\hat E_n\rho]\leq nE$. **Access:** sample; homodyne and heterodyne detection for first moments and the covariance matrix; CV shadows or optimal tomography for the compressed core.
* **Status:** Gaussian 🟢 🟢 🟢 with $O(n^7E^4/\epsilon^4)$ copies, $\mathrm{poly}(n)$ time, $O(n^2)$ parameters; $t$-doped 🟢 🟢 🟢 only for $\kappa t = O(1)$; general 🔴 with $\Omega(\epsilon^{-2n})$ copies, already for $n = 10$ modes and $\epsilon = 0.1$ about 3000 years at one copy per nanosecond.
* **Promise:** energy bound $E$ (general), second moment (for the covariance estimation), Gaussianity or $t$-doping.

### The problem

Without an energy bound, CV tomography is meaningless (infinitely many parameters); with an energy bound it becomes a finite task, but how expensive? And for which physical classes does it become efficient?

### Key results

* **Theorems 1 and 2 (energy-constrained).** Pure states: the sample complexity scales as $\epsilon^{-2n}$ with $E^n$ factors; mixed: $O(E^{2n}/\epsilon^{3n})$ sufficient, $\Omega(E^{2n}/\epsilon^{2n})$ necessary. Mechanism: every energy-constrained state is, up to $\epsilon$, a state of dimension $D = O(E^n/\epsilon^{2n})$ and rank $r = O(E^n/\epsilon^n)$ (Eq. 3), and finite-dimensional tomography costs $O(Dr)$. For $k$-th moments the exponent becomes $2n/k$.
* **Theorem 3 (error propagation).** If the first moment and covariance matrix are known to $\epsilon$, the trace distance is at most $O(\sqrt\epsilon)$ and at least $O(\epsilon)$; the bounds (Theorems 10, 11) are tools in their own right.
* **Theorem 4 (Gaussian).** $O(n^7E^4/\epsilon^4)$ copies, output the first moment and covariance; robust against small non-Gaussian perturbations (small relative entropy of non-Gaussianity).
* **Theorem 5 (compression).** $U = G(u_{\kappa t}\otimes I)G_{\mathrm{passive}}$, hence $\vert\psi\rangle = G(\vert\phi_{\kappa t}\rangle\otimes\vert 0\rangle^{\otimes(n-\kappa t)})$: the bosonic counterpart of stabilizer and fermion compression.
* **Theorem 6 ($t$-doped).** $\mathrm{poly}(n) + O((nE/\epsilon)^{2\kappa t})$ copies, the same order in time and memory; efficient exactly when $\kappa t = O(1)$, unlike stabilizers and fermions ($t = O(\log n)$), because the core is infinite-dimensional.

### Methodological approach

* Estimate the moments by homodyne detection, construct the Gaussian unitary, apply its inverse, compress the non-Gaussianity onto $\kappa t$ modes, tomograph there; all operations are standard in a quantum optics laboratory.
* The lower bound comes via the reduction to finite-dimensional tomography of states of dimension $D$ and rank $r$; the energy constraint translates into an effective dimension.

### Significance and applications

* A bridge between quantum learning theory and CV information; the Gaussian class is the standard resource for sensing, communication, and computing with light.
* The "extreme inefficiency" is a new phenomenon: the cost depends on $1/\epsilon$ exponentially in $n$, not only on the dimension.

### Relation to this project

* Displacement operators on qudits are the discrete version of the Weyl operators in the CV phase space; a Gaussian state there has a Gaussian displacement spectrum determined by the covariance alone. The paper shows what the "Gaussian promise" costs on the instance ladder: $O(n^2)$ parameters, polynomially many copies, no support to search.
* $\kappa t = O(1)$ as the efficiency boundary is stricter than $t = O(\log n)$; this suggests that the height of the ladder depends on the alphabet ($d\to\infty$ shortens it).
* The error propagation $O(\sqrt\epsilon)$ from moments to trace distance is the same square-root loss as in the rounding of an estimated kernel matrix; Phase 2 should account for it.

### Limitations and open questions

* $n^7E^4/\epsilon^4$ is not shown to be optimal; the upper bound for mixed energy-constrained states ($\epsilon^{-3n}$) does not match the lower bound ($\epsilon^{-2n}$).
* Learnability for $\kappa t = \omega(1)$ is not ruled out; only the algorithm is inefficient.
* No hardness bound as in Mele–Herasymenko.

### Questions for further study

* How does the energy bound enter the construction of the covariance estimate, and why does it not suffice without the second moment?
* What do the bounds of Theorems 10 and 11 (trace distance of two Gaussian states against the norm of the moment difference) look like explicitly?
* Is there a qudit version of the "extreme inefficiency" when $d$ grows with $1/\epsilon$?

Paper: [arXiv:2405.01431](https://arxiv.org/abs/2405.01431)

---

## Efficient quantum state tomography (arXiv:1101.4366)

The paper by **Marcus Cramer, Martin B. Plenio, Steven T. Flammia, Rolando Somma, David Gross, Stephen D. Bartlett, Olivier Landon-Cardinal, David Poulin, and Yi-Kai Liu** (Ulm, Perimeter, Hannover, Sydney, Sherbrooke, Caltech; Nat. Commun. 2010) is the founding paper of matrix product tomography. Two schemes reconstruct a state on a chain of $N$ qudits that is well described by an MPS from linearly many local measurement settings with polynomial post-processing; the accuracy can be certified without assumptions about the laboratory state.

### Placement in the tables

* **Task type:** Identifying against a class (MPS of bond dimension $D$, rank $R$ of the reductions) with the promise that the laboratory state is close to it; the certificate makes the promise checkable and thereby turns it into an $M = 1$ task (certification).
* **Object:** state on a chain; pure MPS in the main part, generalizations indicated. **Access:** sample; scheme 1 needs unitaries on $\kappa = \lceil\log_dR\rceil + 1$ neighbouring qudits plus local measurements, scheme 2 only local measurements on $k$ neighbours.
* **Status:** 🟢 🟢 🟢. Linearly many measurement settings in $N$, post-processing $\mathrm{poly}(N)$, memory $O(ND^2)$; scheme 2 additionally gives a fidelity certificate from the same data.
* **Promise:** small bond dimension; for scheme 2 the existence of a local, gapped parent Hamiltonian, which exists for generic MPS.

### The problem

Full tomography scales exponentially in $N$; MPS have polynomially many parameters. Can these parameters be determined from local data and the reconstruction be verified, without assuming that the laboratory state is an MPS?

### Key results

* **Scheme 1 (unitaries).** Tomography of the first $\kappa$ sites, a unitary $\hat U_1$ that decouples the first qudit, repetition along the chain; the sequence $\hat U_1, \ldots, \hat U_{N-\kappa+1}$ is the preparation circuit, from which the MPS follows. Errors from truncation to rank $R$ and measurement inaccuracy $\epsilon$ accumulate at most linearly, total error $N\epsilon$, readable directly from the data.
* **Scheme 2 (local measurements).** From estimates $\hat\sigma_i$ of the reductions on $k$ neighbours, singular value thresholding searches for an MPS $\vert\psi\rangle$ whose reductions match $\hat\sigma_i$.
* **Eqs. (3)–(4) (certificate).** If $\vert\psi\rangle$ is the unique ground state (energy zero) of a local $\hat H = \sum_i\hat h_i$ with gap $\Delta E$, then $\langle\psi\vert\hat\varrho\vert\psi\rangle\geq 1 - \tfrac{1}{\Delta E}\sum_i(\mathrm{Tr}[\hat h_i\hat\sigma_i] + \epsilon_i)$; the Hamiltonian is a witness, and for generic MPS it exists and can be constructed from the estimator.
* **Cluster state example.** $k = 3$, $R = 4$, $\Delta E = 1$; scheme 1 with $\kappa = 2$.

### Methodological approach

* Sequential decoupling: the rank bound on the reductions forces that a qudit can be split off by a unitary on $\kappa$ sites; this is the inverse of sequential MPS preparation.
* The certificate uses only local expectation values; the non-existence of a witness (GHZ violates the "generic" condition) is treated separately.

### Significance and applications

* The first polynomial-time tomography of a physically relevant class with certified output; the idea of verifying the reconstruction through a parent Hamiltonian returns in a different form in Huang–Preskill–Soleimanifar.
* Tensor network generalizations (tree, MERA) indicated; demonstrated numerically up to 20 ions.

### Relation to this project

* Scheme 1 learns the preparation circuit by local inversion, qudit by qudit; this is the one-dimensional version of the local-inversion principle of Huang et al. and Landau–Liu, and proof that "a unitary that splits off one qudit" is an identifying primitive that needs no global search.
* The certificate is a lower bound on the fidelity from local data; for this project's pipeline the question is whether the displacement spectrum supplies a similar witness, for instance via the $\ell_2$ mass on the support found.
* The class is a promise class by construction (the MPS promise is assumed), and the certificate is a built-in test of whether the promise actually holds for the lab state.

### Limitations and open questions

* No explicit sample complexity in $D$, $\epsilon$; the first rigorous bound for MPDOs from local measurements is given by Fanizza et al. (2023).
* Scheme 2 needs the existence of a gapped witness; non-generic states (GHZ) require additional treatment.
* One-dimensional only; higher dimensions lead to the constraint satisfaction problems that Landau–Liu avoid.

### Questions for further study

* How does $\kappa$ depend on $R$ when the laboratory state has rank $R$ only approximately, and how is the truncation chosen?
* How is the parent Hamiltonian constructed from the MPS estimator, and how is its gap computed efficiently?
* Is there a certificate of the form (4) for states whose structure is a sparse displacement spectrum instead of a small bond rank?

Paper: [arXiv:1101.4366](https://arxiv.org/abs/1101.4366)

---

## Learning finitely correlated states: stability of the spectral reconstruction (arXiv:2312.07516)

The paper by **Marco Fanizza, Niklas Galke, Josep Lumbreras, Cambyse Rouzé, and Andreas Winter** (Barcelona, Paris, Singapore; 2023) gives the first rigorous sample complexity for learning matrix product density operators from local measurements. For translation-invariant finitely correlated states on the infinite chain, a realization of minimal dimension $m$ is obtained by *spectral reconstruction* from the marginals on $2s+1$ sites; the error of the marginals on $t$ sites is controlled polynomially in $t$, $m$, $1/\eta$, where $\eta$ is a bound on the smallest singular value of the Hankel-type matrix $\Omega$.

### Placement in the tables

* **Task type:** Identifying against a class with a promise: $S(m, s, \eta)$, states with a realization of dimension $\leq m$, $s$-reconstructible, $\sigma_m(\Omega, s)\geq\eta$; the output is the parameters of the realization ($\rho$, $e$, $K_{k,l}$), from which every marginal follows in linear time.
* **Object:** translation-invariant, possibly mixed state on the infinite chain; also non-translation-invariant finite chains (Appendix D) and states with a quantum realization $S_q(d_B, s, \eta)$. **Access:** sample; arbitrary tomography of the marginals $\omega_s$, $\omega_{2s}$, $\omega_{2s+1}$, local or entangled.
* **Status:** 🟢 🟢 🟢. Copies polynomial in $t$, $m$, $1/\eta$, $1/\epsilon$ (Theorems 2.6 to 2.8), time linear algebra on matrices of size $d^{2s}$, memory $O(m^2d^2)$.
* **Promise:** finite correlation of dimension $m$; the parameters $s$ and $\eta$ are inputs of the algorithm, $m$ need not be known.

### The problem

For pure MPS there is certifiable tomography (Cramer et al.), for MPDOs reconstruction procedures without an error bound. Classically, spectral algorithms for hidden Markov models give guarantees in total variation, quadratic in the memory size. Is there the same for quantum states whose realization need not even be a quantum model?

### Key results

* **Definitions 2.1, 2.2.** Classes $S(m, s, \eta)$ and $S_q(d_B, s, \eta)\subseteq S(d_B^2, s, \eta)$; every state with a realization of dimension $m$ is $m$-reconstructible, generically $O(\mathrm{polylog}\,m)$-reconstructible (quantum Wielandt).
* **Algorithm 1 (LearnFCS).** Estimate $\hat\Omega(1)$, $\hat\tau\Omega$, $\hat\Omega$, $\hat\Omega_{Z_k}$ from $\hat\omega_s$, $\hat\omega_{2s}$, $\hat\omega_{2s+1}$; SVD $\hat\Omega = \hat U\hat D\hat O^T$, keep the columns with singular value $\geq\eta/2$; $\hat e = \hat U^T\hat\Omega(1)$, $\hat\rho = \hat\tau\Omega(\hat U^T\hat\Omega)^+$, $\hat K_{Z_i} = \hat U^T\hat\Omega_{Z_i}(\hat U^T\hat\Omega)^+$.
* **Theorem 2.6 (stability).** If the Hilbert–Schmidt errors of the three marginals are smaller than $\epsilon\eta^3/(20tm\sqrt{d_A})$, then $\tfrac12\Vert\hat\omega_t - \omega_t\Vert_1\leq\epsilon$. **Theorem 2.7:** with a quantum realization, $d_B$ replaces $m$. **Theorem 2.8:** from this, the sample complexity follows from any tomography routine for $d^{2s+1}$-dimensional states.
* **Appendices C, D.** Error propagation via completely bounded norms and contractivity of the generating map; generalization to non-translation-invariant chains.

### Methodological approach

* The matrix $\Omega$ is a reordering of the coefficients of $\omega_{[t_1, t_2]}$ in a product basis; its rank is $\leq m$ and saturates for $-t_1\geq m-1$, $t_2\geq m$. The realization follows by Moore–Penrose inversion; the sensitivity lies in the smallest singular value, hence $\eta$.
* The analysis works with operator systems and CP maps and covers realizations for which no finite-dimensional quantum model exists (GPT memory).

### Significance and applications

* The first sample guarantee for MPDO tomography from local measurements, including mixed states; a classical side effect: error bounds for hidden Markov models beyond the previous assumptions.
* The output is a generative model: expectation values of product observables at arbitrary lengths in linear time.

### Relation to this project

* The spectral reconstruction is an estimating step (marginals) plus linear algebra; the class structure (rank $m$) turns $d^{2s}$ numbers into a description with $O(m^2d^2)$ parameters. This is the tensor-network version of "find the support, then the coefficients": the columns of $\hat U$ with singular value $\geq\eta/2$ are the support.
* $\eta$ is a condition number of the instance and belongs on the instance ladder; the factors $\eta^{-3}$ and $m$ show how a promise translates quantitatively into copies.
* For displacement spectra, the analogous question arises: which Hankel structure do Bell statistics of translation-invariant states have, and can a sparse spectrum be read as a low-rank $\Omega$?

### Limitations and open questions

* The constants are crude (factor 20, $\eta^3$); optimality is unclear.
* The translation of "rank $m$ and singular value $\eta$" into physical properties (correlation length, gap) is only heuristic.
* Higher dimensions and PEPS are not treated.

### Questions for further study

* Where does the power $\eta^3$ come from, and which step of the error propagation is responsible?
* What exactly does the contractivity of the generating map achieve, and why does it suffice even for GPT realizations?
* Can the procedure be applied to Bell-sampling data, i.e. to the distribution $\vert\mathrm{Tr}(\rho D_a)\vert^2$ instead of the density matrix of the marginals?

Paper: [arXiv:2312.07516](https://arxiv.org/abs/2312.07516)

---

## Learning shallow quantum circuits (arXiv:2401.10095)

The paper by **Hsin-Yuan Huang, Yunchao Liu, Michael Broughton, Isaac Kim, Anurag Anshu, Zeph Landau, and Jarrod R. McClean** (Caltech, Google Quantum AI, Berkeley, UC Davis, Harvard; STOC 2024) gives the first polynomial-time algorithms for two tasks: learning an unknown constant-depth unitary of arbitrary connectivity from classical random data to diamond distance $\epsilon$, and learning a state $U\vert 0^n\rangle$ of a shallow circuit on a 2D lattice from copies to trace distance $\epsilon$. The technique is local inversions, "sewn" into a global circuit by an ancilla-SWAP trick without solving a constraint satisfaction problem.

### Placement in the tables

* **Task type:** Identifying against a class with a promise (constant depth). Returned is a circuit from the class, not a support and not a list of expectation values; the promise limits every light cone to constant size, hence only polynomially many local candidates, the same mechanism as for juntas.
* **Object:** unitary $U$ (Theorems 1 to 3) or state $U\vert 0^n\rangle$ (Theorem 4). **Access:** sample on input–output pairs (random product inputs, randomized Pauli measurements, the classical shadow of $U$); query to $U$ for Theorem 3; copies for Theorem 4.
* **Status:** 🟢 🟢 🟢. Unitary: $N = O(n^2\log n/\epsilon^2)$ samples, $\mathrm{poly}(n)/\epsilon^2$ time; finite gate set $O(\log n)$ samples, zero error; with quantum queries $\Theta(1)$ queries and $\Theta(n)$ time, both optimal. State in 2D: $2^{O(d^2)}(n/\epsilon)^{O(1)}$ copies, time $(n^{d^3}/\epsilon)^{O(d^3)}$; finite gate set $O(\log n)$ copies, $O(n\log n)$ time.
* **Promise:** depth $d = O(1)$; quasipolynomial up to $d = \mathrm{polylog}(n)$; $\log$ depth without geometry is exponentially hard (Prop. 3, Grover oracle).

### The problem

Shallow circuits produce distributions that are classically hard to sample; the optimization landscape of parametrized shallow circuits has no barren plateaus, but exponentially many suboptimal local minima at which gradient methods fail. Is there nevertheless a polynomial-time learner, and from which data?

### Key results

* **Theorem 1 (general shallow circuits).** $U$ with arbitrary two-qubit gates between arbitrary pairs, also with $m$ ancillas, from $O(n^2\log n/\epsilon^2)$ samples in $\mathrm{poly}(n)/\epsilon^2$ classical time to $\Vert V - U\otimes U^\dagger\Vert_\diamond\leq\epsilon$; $V$ acts on $2n$ qubits, and $U$ follows by tracing out.
* **Theorem 2 (geometrically local, $k$-dimensional lattice).** The same sample count; either $O(n^3\log n/\epsilon^2)$ time with depth $(k+1)4^{4(8kd)^k}+1$, or $(n/\epsilon)^{O((8kd)^{k+1})}$ time with depth $(k+1)(2d+1)+1$; finite gate set $O(\log n)$ samples, $O(n\log n)$ time. Holds unchanged for quantum cellular automata.
* **Theorem 3 (quantum queries).** Finite gate set: zero error, zero failure probability, $\Theta(1)$ queries, $\Theta(n)$ time.
* **Theorem 4 (states in 2D).** A circuit of depth $3d$ that prepares $\vert\psi\rangle$ to $\epsilon$.
* **Prop. 3 (limit).** Without geometry, $\log$-depth circuits need exponentially many queries in diamond distance.
* **Section 9 (verification).** An efficient test from the same data that checks the learned circuit in average-case distance; useful for circuit compression.

### Methodological approach

* Local inversion: for every qubit $i$ there exists a unitary $V_i$ in the backward light cone with $UV_i\approx U'\otimes I_i$; it is found by enumeration over the constant-size search space and a test for approximate local identity. The set $\mathcal{C}_i$ of valid inversions is not unique, and neighbours need not be consistent.
* Sewing (Eqs. 1 to 4): apply an arbitrary $V_1\in\mathcal{C}_1$, swap qubit 1 with a fresh ancilla, apply $V_1^\dagger$; the effect is a SWAP after $U$, and the circuit before $U$ is "repaired", so that qubit 2 can follow with an arbitrary $V_2\in\mathcal{C}_2$. After $n$ steps a $2n$-qubit circuit $\hat U$ has been learned.
* For states the same idea with $V_i\vert\psi\rangle\approx\vert\psi'\rangle\otimes\vert 0\rangle_i$; in 2D the lattice is decoupled into 1D strips whose consistency problem is efficiently solvable.

### Significance and applications

* A finite correlation length suffices to reconstruct global structure from local data, although the class is not classically simulable; this distinguishes it from MPS and stabilizers.
* Applications: hardware characterization, circuit compression with verification, learning dynamics; the data source is the classical shadow of the process.
* The first literature example for the cell query × identifying with a process object; previously that cell held Bernstein–Vazirani and the document's own construction.

### Relation to this project

* The ancilla-SWAP trick is a method for composing local pieces of information into a global object without enforcing consistency; for top-$k$ localization it is a model of how locally found addresses can be assembled without global matching.
* The test for approximate local identity is a certificate from local measurements, related to the parent-Hamiltonian witness of Cramer et al.
* The switch from sample (input–output pairs) to query ($\Theta(1)$ calls, zero error) is the access ladder for processes within one paper; it confirms that queries buy the error, not the instance size.

### Limitations and open questions

* States only in 2D; Landau–Liu remove this restriction.
* The exponent of the runtime is large; the learned depth can be much larger than the true one.
* Average-case distance instead of diamond distance is computationally open; nothing is known beyond polylog depth.

### Questions for further study

* How exactly does the test for approximate local identity work from randomized Pauli data, and how many samples does it need per candidate?
* Why does sewing fail at $\log$ depth: does the light cone grow, or the number of candidates?
* Do local inversions carry over to qudit circuits with displacement structure, and is the address of a displacement operator a light-cone notion?

Paper: [arXiv:2401.10095](https://arxiv.org/abs/2401.10095)

---

## Learning quantum states prepared by shallow circuits in polynomial time (arXiv:2410.23618)

The paper by **Zeph Landau and Yunchao Liu** (UC Berkeley, Harvard; 2024) solves the problem that Huang et al. had solved for 2D and left open for higher dimensions: a state $\vert\psi\rangle = U\vert 0^n\rangle$ with $U$ of depth $d$ on a $k$-dimensional lattice is learned in polynomial time, for every fixed $k$, without solving a consistency problem. The output is a circuit of depth $(2k+1)d$ with $rn$ ancillas; as a corollary, a test of circuit complexity.

### Placement in the tables

* **Task type:** Identifying against a class with a promise (depth $d$ on a lattice); Corollary 1 is a one-bit test (trivial phase or high complexity).
* **Object:** pure state on $n$ qubits of a $k$-dimensional lattice. **Access:** sample; tomography of the reductions on constant-size regions, followed by purely classical processing.
* **Status:** 🟢 🟢 🟢 for $d = O(1)$: $M = \tilde O(n^4)2^{O(c)}/\epsilon^4$ copies, time $M + (nkd\cdot c/\epsilon)^{O(dc)}$ with $c = O((3k)^{k+2}d)^k$; quasipolynomial for $d = \mathrm{polylog}(n)$.
* **Promise:** geometry and depth; arbitrary two-qubit gates.

### The problem

Reductions of sufficient size determine the state information-theoretically; the question is the computation time. The naive route, finding local circuits for regions and gluing them via consistency on the overlaps, is a constraint satisfaction problem, hard in 2D and above. Huang et al. reduce 2D to an efficient 1D problem; from 3D on this fails.

### Key results

* **Theorem 1 / 4 (main result).** Output a circuit $W$ of depth $(2k+1)d$ that prepares $\vert\psi\rangle$ to $\epsilon$, with $M$ and $T$ as above; $W$ uses $rn$ ancillas for arbitrarily small $r > 0$.
* **Facts 1 and 2.** For every region $A$ there exists a local inversion $V$ on $B(A, d)$ of depth $d$; and $\vert\psi\rangle$ is invariant under every "replacement process" (apply the inversion, replace $A$ by $\vert 0\rangle$, undo the inversion).
* **Theorem 2 (covering implies learning).** If a covering scheme with $\ell$ layers exists such that the backward light cone of the output is covered completely by the replacement pieces and does not depend on the input state, then the algorithm learns.
* **Theorem 3 (lattice covering).** For $k$-dimensional lattices a $(k+1, c, d)$ covering scheme exists; hence depth $(2k+1)d$.
* **Corollary 1 / Theorem 5 (complexity test).** Decide with polynomially many copies and polynomial time whether $\vert\psi\rangle$ is prepared by a circuit of depth $\leq L$ or is $0.01$-far from all constant-depth states with $O(n)$ ancillas.

### Methodological approach

* First insight: applying a local inversion and undoing it does not change the state, but replaces part of the unknown state by a known piece of circuit. Second insight: with a geometrically chosen order of regions, these pieces are layered such that the backward light cone of the final state contains only known pieces.
* The learned circuit consists of parts of local inversions and their inverses; it is never required that two inversions agree.

### Significance and applications

* States of the trivial phase (constant or polylog depth) are learnable in polynomial time, in every dimension; and membership in the trivial phase is efficiently testable.
* For NISQ algorithms a provable primitive: find a shallow circuit for an unknown state.

### Relation to this project

* The replacement process is a non-disturbance technique: one learns by inserting structure that leaves the state invariant; for Phase 2 this is a pattern for constructing a probe state that does not change the target quantity but makes the measurement linear.
* The complexity test is a class test without knowledge of the circuit; the displacement version would be a test of whether a state has a sparse spectrum, before searching for it.
* The exponents $c = O((3k)^{k+2}d)^k$ show how quickly the constants grow with the geometry; for the instance ladder, $k$ is a parameter of its own.

### Limitations and open questions

* Constants and depth blow-up $(2k+1)d$; ancillas are needed.
* Lattices only; general graphs of bounded degree are not treated.
* No lower bounds on the time in $d$.

### Questions for further study

* What does the $(k+1)$-layer covering scheme look like concretely in 3D, and why do $k+1$ layers suffice?
* How does the approximate inversion (Section 4) enter the error accumulation, and why $\epsilon^{-4}$?
* Can the complexity test be extended to "depth $\leq L$ after conjugation with a choice of displacement basis"?

Paper: [arXiv:2410.23618](https://arxiv.org/abs/2410.23618)

---

## Optimal algorithms for learning quantum phase states (arXiv:2208.07851)

The paper by **Srinivasan Arunachalam, Sergey Bravyi, Arkopal Dutt, and Theodore J. Yoder** (IBM, MIT; TQC 2023) determines the sample complexity of learning binary phase states $\vert\psi_f\rangle = 2^{-n/2}\sum_x(-1)^{f(x)}\vert x\rangle$ with $\deg f\leq d$ over $\mathbb{F}_2$: $\Theta(n^d)$ copies with separable measurements (only single-qubit gates and measurements), $\Theta(n^{d-1})$ with entangled measurements via the pretty-good measurement. In addition: generalized phase states over $\mathbb{Z}_q$, sparse and noisy variants, and query access to the diagonal preparation unitary.

### Placement in the tables

* **Task type:** Identifying against a class with a promise; the class $P(n, d)$ has $2^{\Theta(n^d)}$ elements, and the output is the polynomial $f$ exactly. With query access to $C = \sum_x(-1)^{f(x)}\vert x\rangle\langle x\vert$ the same numbers, because a query on $\vert +\rangle^{\otimes n}$ produces a copy.
* **Object:** state. **Access:** sample, separable (single-qubit measurements in $X$ and $Z$) or entangled (PGM on $\vert\psi_f\rangle^{\otimes M}$); query to $C$ or $V$ (Section 6).
* **Status:** separable 🟢 🟢 🟢 with $O(n^d)$ copies and $O(n^{3d-2})$ time; entangled $\Theta(n^{d-1})$ copies, but time $O(\exp(n^d\log 2))$, i.e. 🟢 🔴 🟢.
* **Promise:** degree $d\leq n/2$; for $d = 1$ Bernstein–Vazirani with $\Theta(1)$, for $d = 2$ Bell sampling with $O(n)$.

### The problem

Degree-2 phase states (graph states, Clifford outputs) are learned by Bell sampling; on two copies of a degree-3 state, Bell sampling yields a single copy of a random degree-2 state $\vert\psi_{g_y}\rangle$, and it would take $\Omega(\sqrt{2^n})$ copies to collect enough of them. What is the right sample complexity, and do entangled measurements help?

### Key results

* **Theorem 3 (separable, upper bound).** $M = O(2^dn^d)$ copies: measure all qubits except the first in $Z$ and obtain $y$; the first qubit is $\tfrac{1}{\sqrt2}((-1)^{f(0y)}\vert 0\rangle + (-1)^{f(1y)}\vert 1\rangle)$, and an $X$ measurement gives the derivative $p_1(y) = f(0y) + f(1y)$, a polynomial of degree $\leq d-1$ in $n-1$ variables; $O(n^{d-1})$ points per direction, $n$ directions, then interpolation.
* **Theorem 5 (separable, lower bound).** $\Omega(n^d)$ for arbitrary single-copy measurements: for random $f$, $\mathbb{E}_f[H(x\vert f)]\geq n - O(1)$, every copy yields $O(1)$ bits, and $f$ has $\Omega(n^d)$ bits of entropy.
* **Theorem 4 (entangled).** $O((2n)^{d-1})$ copies by PGM: the ensemble is geometrically uniform, the PGM success probability is the same for all $f$, and the weight distribution of polynomials (bound of Ben-Eliezer, Hod, Lovett) controls the overlaps. Holevo gives $\Omega(n^{d-1})$.
* **Theorem 8 (generalized, $\mathbb{Z}_q$).** $O(2^dq^3n^d\log q) = O(n^d)$ separable; the POVM $\{\vert\phi_b\rangle\langle\phi_b\vert\}_{b\in\mathbb{Z}_q}$ rules out the true value $c$ with certainty and hits every other value with probability $\Omega(q^{-3})$.
* **Theorems 6, 7, 9, 11.** Sparse $f$ with $O(2^dsn)$; Fourier degree $d$ with $O(2^{2d})$; global depolarizing noise $n^{1+O(\epsilon)}$; local depolarizing noise $\Omega((1-\epsilon)^{-n})$ copies, already information-theoretically: the GHZ pair $\vert 0^n\rangle\pm\vert 1^n\rangle$ is, up to $R_x^{\otimes n}$, a pair of degree-2 phase states, after the noise $k$ copies have trace distance at most $2k(1-\epsilon)^n$, and Helstrom gives the bound. The theorem statement reads $\Omega((1-\epsilon)^n)$, a typo that the proof (p. 31) corrects; Table 1 of the paper writes $\Theta$, but no matching upper bound is proven.
* **Property testing.** Learning plus a SWAP test tests membership in $P(n, d)$ with $n^d$ copies.

### Methodological approach

* Derivatives instead of Bell sampling: measuring $n-1$ qubits in $Z$ reduces the degree by one, and interpolation over $\mathbb{F}_2$ assembles $f$ from $n$ partial derivatives.
* For the PGM a new observation: for geometrically uniform ensembles, the success probability does not depend on the element.
* The lower bound computes the Rényi-2 entropy via an explicit formula for $\mathbb{E}_f[\vert\psi_f\rangle\langle\psi_f\vert^{\otimes 2}]$.

### Significance and applications

* Graph states become learnable with single-qubit operations (Bell measurements were needed before); degree 3 gives hypergraph states for MBQC and IQP circuits.
* The class is the basis of the PRS constructions (Ji–Liu–Song, Brakerski–Shmueli): at polynomial degree, learning would be cryptographically hard; the degree scale is the instance ladder of this family.
* The paper's table is a model for keeping samples, time, and measurement class separate.

### Relation to this project

* Separable against entangled is a factor $n$ in the copies, and the time turns around: the PGM is exponential. This is the memory–time tradeoff of the tables in pure form, and a warning that two-copy protocols keep their advantage only if the post-processing stays linear-algebraic (as in Bell sampling), not if it has to implement a PGM.
* The derivative measurement is a probe mechanism: conditioning on $y$ turns the remaining amplitude into a first-order single-qubit problem; Phase 2 conditions analogously on a support.
* For $\mathbb{Z}_q$, the POVM that rules out one value with certainty is an exclusion design; the same construction can be used for displacement phases $\omega_d^c$.

### Limitations and open questions

* The entangled variant is time-inefficient; whether $\Theta(n^{d-1})$ copies are achievable in polynomial time is open.
* Generalized phase states are treated only in the separable setting.
* Exact identification of $f$ only; no agnostic variants.

### Questions for further study

* How exactly does the weight bound $\vert\{f: \mathrm{wt}(f)\leq(1-\epsilon)2^{-\ell}\}\vert\leq(1/\epsilon)^{C\ell\binom{n-\ell}{\leq d-\ell}}$ enter the PGM analysis?
* Why does Bell sampling on degree-$d$ states yield exactly one step down in degree, and can this be iterated if copies of the intermediate states can be produced (query model)?
* What is the displacement version of a degree-$d$ phase state on qudits, and is its spectrum sparse?

Paper: [arXiv:2208.07851](https://arxiv.org/abs/2208.07851)

---

## Schur–Weyl duality for the Clifford group with applications: property testing, a robust Hudson theorem, and de Finetti representations (arXiv:1712.08628)

The paper by **David Gross, Sepehr Nezami, and Michael Walter** (Cologne, Stanford, Amsterdam; Commun. Math. Phys. 2021) determines the commutant of the $t$-th tensor power of the Clifford group: it is spanned by operators $R(T) = r(T)^{\otimes n}$ that belong to self-dual codes $T\subseteq\mathbb{Z}_d^{2t}$, and its size is independent of $n$ for $n\geq t-1$. Applications: a stabilizer test with six copies for qubits (Bell difference sampling), $2s$ copies for qudits, three copies for $d\equiv 1, 5 \bmod 6$; a robust Hudson theorem; and de Finetti theorems for Clifford-invariant states.

### Placement in the tables

* **Task type:** Identifying, one bit (property testing): stabilizer state or $\max_S\vert\langle S\vert\psi\rangle\vert^2\leq 1-\epsilon^2$. Perfectly complete, dimension-independent, transversal. Cliffordness of unitaries follows, without access to the inverse.
* **Object:** pure state on $n$ qudits. **Access:** sample; Bell measurements on pairs of copies and Weyl measurements on single copies; coherent only across two copies and factorized over the $n$ qudits.
* **Status:** 🟢 🟢 🟢. Six copies per round, $O(1/\epsilon^2)$ rounds, $O(n)$ gates, memory $2n$ qubits; optimal in the copy count among perfectly complete tests.
* **Promise:** none; the test is agnostic in the sense that it measures the fidelity with the nearest stabilizer state.

### The problem

Second and third moments of stabilizer states agree with Haar, and fourth moments cannot be distinguished independently of the dimension; previous tests identified the state and needed $\Omega(n)$ copies. Is there a test with constantly many copies, and what is the symmetry structure that enforces it?

### Key results

* **Theorem 3.2 (Bell difference sampling).** $\mathrm{Tr}(\Pi_a\psi^{\otimes 4}) = \sum_xp_\psi(x)p_\psi(x+a)$ with $p_\psi(a) = \vert c_a\vert^2$ the characteristic distribution; for stabilizer states equal to $p_S(a)$, i.e. uniform on the stabilizer group. This solves the problem that Bell sampling yields the characteristic distribution only for real states.
* **Theorem 3.3 (qubits).** Algorithm 1: draw a Bell difference sample $a$, then measure $W_a$ twice on fresh copies, accept if the outcomes agree. $p_{\mathrm{accept}} = 1$ for stabilizer states, $\leq 1-\epsilon^2/4$ otherwise. Proof: high acceptance forces $p_\psi(a) > \tfrac12 2^{-n}$ on a large set; the uncertainty relation (Fig. 1: $\vert\mathrm{Tr}\,Z\rho\vert$ and $\vert\mathrm{Tr}\,X\rho\vert$ cannot both exceed $1/\sqrt2$) forces commutativity; hence a stabilizer subgroup.
* **Theorem 3.11 (qudits).** $\Pi_{s, \mathrm{accept}} = \tfrac12(I + V_s)$ with $V_s = d^{-n}\sum_x(W_x\otimes W_x^\dagger)^{\otimes s}$, $(d, s) = 1$, $2s$ copies; $p_{\mathrm{accept}}\leq 1 - C_{d,s}\epsilon^2$ with $C_{d,s} = (1-(1-1/4d^2)^{s-1})/2$. **Lemma 3.10:** $\vert\mathrm{Tr}\,\psi W_x\vert^2, \vert\mathrm{Tr}\,\psi W_y\vert^2 > 1 - 1/4d^2$ forces $[W_x, W_y] = 0$.
* **Theorem 8.6 (three copies).** For $d\equiv 1, 5 \bmod 6$ with phase-space point operators $A_x$: $V = d^{-n}\sum_xA_x^{\otimes 3}$, $p_{\mathrm{accept}}\leq 1-\epsilon^2/16d^2$.
* **Structure (Theorem 4.3 ff.).** The commutant of $\mathrm{Cl}_n^{\otimes t}$ is spanned by $R(T)$ for self-dual codes $T$, with the stochastic orthogonal group $O_t(d)$ as symmetry; the anti-identity $R(\bar 1) = 2^{-n}(I^{\otimes t} + X^{\otimes t} + Y^{\otimes t} + Z^{\otimes t})^{\otimes n}$ is the simplest nontrivial element.

### Methodological approach

* Clifford-invariant tests must lie in the commutant; the classification of the commutants turns the search for tests into a search over codes.
* The uncertainty relation for Weyl operators is the analytic heart; it translates "many heavy addresses" into "commuting addresses".
* For the de Finetti theorems, the $R(T)$ are treated as a generalization of permutations.

### Significance and applications

* Since this paper, Bell difference sampling is the standard primitive for stabilizer learning and testing (Grewal et al., Chen–Gong–Ye–Zhang, Arunachalam–Dutt, Bao et al.).
* The commutant is the basis for Clifford designs, for stabilizer entropy formulas (Leone et al.), and for shadow variance calculations.

### Relation to this project

* Theorem 3.2 is the exact statement that four copies deliver the convolution $p_\psi * p_\psi$; two copies $\rho\otimes\rho^*$ deliver $p_\psi$ itself. This project's protocol therefore saves the convolution and half of the copies at the price of a conjugate copy; the uncertainty relation carries over directly to displacement operators (Lemma 3.10 is already formulated for qudits).
* The case distinctions $(d, s) = 1$ and $d\equiv 1, 5 \bmod 6$ show that the copy count depends on the alphabet; for odd primes $d$ the situation is more favourable than for qubits.
* The commutant is the language in which a CNN symmetry (Clifford invariance of the Bell statistics) should be formulated.

### Limitations and open questions

* Pure states only in the testing theorems; mixed states and the tolerant test (acceptance close to one) are the follow-up works.
* The constant $\epsilon^2/4$ is not optimized; six copies are optimal for perfect completeness, not for tests with type-I error.
* The commutant for non-prime $d$ is treated only partially.

### Questions for further study

* How do the codes $T$ and the group $O_t(d)$ enter the construction of the six-copy operator $V = 2^{-n}\sum_xW_x^{\otimes 6}$?
* Why is Bell sampling the characteristic distribution only for real states, and is the conjugate copy exactly what fixes complex amplitudes?
* What does the robust Hudson theorem say, and is it a statement about the sparsity of the Wigner function, i.e. a precursor for sparse displacement spectra?

Paper: [arXiv:1712.08628](https://arxiv.org/abs/1712.08628)

---

## Tolerant testing of stabilizer states with a polynomial gap via a generalized uncertainty relation (arXiv:2410.21811)

The paper by **Zongbo (Bob) Bao, Philippe van Dordrecht, and Jonas Helsen** (QuSoft/CWI, University of Amsterdam; 2024) makes the stabilizer test of Gross, Nezami, Walter tolerant with a polynomial gap: if a state has stabilizer fidelity $\geq\epsilon_1$ or $\leq\epsilon_2$ with $\epsilon_2\leq C'\epsilon_1^{672}$, then $O(\epsilon_1^{-12})$ rounds of Bell difference sampling decide between the two cases. The tool is a generalized uncertainty relation $\sum_i\mathrm{Tr}(\psi A_i)^2\leq\vartheta(\Gamma_{\mathcal{A}})$ via the Lovász theta number of the anticommutation graph; it replaces a conjecture that Arunachalam–Dutt needed for their version.

### Placement in the tables

* **Task type:** Identifying, one bit, tolerant: both hypotheses are fidelity intervals, neither is "exactly in the class". This is the testing version of agnostic tomography.
* **Object:** pure $n$-qubit state. **Access:** sample; Bell difference sampling on four copies, nothing else.
* **Status:** 🟢 🟢 🟢. $O(\epsilon_1^{-12})$ rounds, hence $O(\epsilon_1^{-12})$ copies, polynomial time, memory $2n$ qubits.
* **Promise:** none about the state; the gap $\epsilon_2\leq C'\epsilon_1^{672}$ is a condition on the question.

### The problem

The test of Gross, Nezami, Walter accepts stabilizer states with certainty and rejects states of fidelity $\leq 1-\epsilon^2$ with probability $\geq\epsilon^2/4$; it says nothing about states that are close to, but not exactly, stabilizer states. Arunachalam and Dutt gave a tolerant test whose gap depended on a conjecture about Gowers norms (from a miscitation of Viola). Can the gap be made unconditional and polynomial?

### Key results

* **Theorem 1.** $\epsilon_1, \epsilon_2\in[0, 1]$, $F_S(\psi) = \max_{S}\vert\langle\psi\vert S\rangle\vert^2$ either $\geq\epsilon_1$ or $\leq\epsilon_2$; if $\epsilon_2\leq C'\epsilon_1^{672}$, then $O(\epsilon_1^{-12})$ Bell difference rounds distinguish the two with probability $> 2/3$.
* **Lemma 15.** For Weyl operators $\{A_i\}_{i=1}^M$ and pure $\psi$: $\sum_i\mathrm{Tr}(\psi A_i)^2\leq\Psi_0(\mathcal{A})$, the maximum operator norm of normalized Hamiltonians $\sum_ia_iA_i$; the proof is the Cauchy–Schwarz lines (13), (14).
* **Lemma 18 (generalized uncertainty).** $\sum_i\mathrm{Tr}(\psi A_i)^2\leq\Psi_0(\mathcal{A})\leq\Psi(\Gamma_{\mathcal{A}})\leq\vartheta(\Gamma_{\mathcal{A}})$, with Hastings–O'Donnell (Prop. 4.8) for the last step; for $M$ pairwise anticommuting operators $\vartheta = 1$, and for $\Gamma = \sqcup$ and $\boxtimes$ of graphs $\vartheta$ is additive and multiplicative, respectively (Facts 3, 4).
* **Theorem 19 (from Arunachalam–Dutt).** $\mathbb{E}_{x\sim q_\psi}[2^np_\psi(x)]\geq\gamma$ and $2^n\geq C''\ln(C'''/\gamma)/\gamma^3$ yield a subspace $V$ with $\sum_{x\in V}\vert\langle\psi\vert W_x\vert\psi\rangle\vert^2\geq C_1\gamma^{55}\vert V\vert$ and $\geq C_2\gamma^{57}2^n$; the uncertainty relation then shows that a large isotropic subgroup $V_0\subseteq V$ exists, and Balog–Szemerédi–Gowers (Theorem 25) turns it into a stabilizer state of fidelity $\mathrm{poly}(\gamma)$.

### Methodological approach

* Bell difference sampling accepts with a probability that weights the characteristic distribution $p_\psi$ against its convolution $q_\psi$; high acceptance means much mass on a nearly linear set. The uncertainty relation bounds how much mass can lie on anticommuting addresses, so the heavy set is almost commutative.
* The Lovász theta number replaces the Gowers-norm conjecture; it is computable and is multiplicative and additive over products and disjoint unions of anticommutation graphs.
* The authors call the exponent 672 "probably highly suboptimal"; independent proofs (Arunachalam–Bravyi–Dutt; Mehraban–Tahmasbi) followed shortly after with similar or somewhat worse degrees.

### Significance and applications

* The first unconditional tolerant stabilizer test with a polynomial gap; the task that was perfectly complete in Gross–Nezami–Walter becomes robust against noise.
* The uncertainty relation via $\vartheta$ is a tool in its own right for Pauli spectra; it quantifies how many non-commuting expectation values can be large simultaneously.

### Relation to this project

* Lemma 18 is exactly the statement that Phase 1 needs to conclude from "many large displacement magnitudes" that "the addresses lie almost in an isotropic subgroup"; in the proof of Lemma 15, the generalization to Weyl operators over $\mathbb{Z}_d$ is not qubit-specific.
* The chain "acceptance probability → mass on a linear set → Balog–Szemerédi–Gowers → subgroup" is the proof structure with which a tolerant support test for displacement spectra would have to be built; the exponents (55, 57, 672) show what additive combinatorics currently costs.
* Tolerance, closeness to the class instead of exact membership, is the agnostic version of the subgroup promise (Regime 2); $O(\epsilon_1^{-12})$ copies is the price a one-bit test pays there.

### Limitations and open questions

* The exponents 672 and 12 are far from the conjectured truth; the paper names their improvement as the next goal.
* Pure states only; mixed inputs and qudits are not treated.
* No lower bound.

### Questions for further study

* Where exactly in the proof is the factor $\gamma^{55}$ lost, and which step is due to BSG?
* Does Lemma 18 hold with the same constant for displacement operators on qudits, whose anticommutation is replaced by $\omega_d$-commutation?
* Can the test be run with $\rho\otimes\rho^*$ instead of $\rho^{\otimes 4}$, so that the acceptance weights $p_\psi$ directly instead of the convolution?

Paper: [arXiv:2410.21811](https://arxiv.org/abs/2410.21811)

---

## Exponential separations between learning with and without quantum memory (arXiv:2111.05881)

The paper by **Sitan Chen, Jordan Cotler, Hsin-Yuan Huang, and Jerry Li** (Berkeley, Harvard, Caltech, Microsoft; FOCS 2021) proves sharp lower bounds for learning algorithms without quantum memory: shadow tomography needs $\tilde\Theta(\min\{M, 2^n\}/\epsilon^2)$ copies, all Pauli expectation values $\Omega(2^n)$, purity testing $\Theta(2^{n/2})$; with $k$ qubits of memory, $\Omega(2^{(n-k)/3})$ for Pauli magnitudes. For channels: distinguishing the completely depolarizing channel from a Haar-random unitary channel $\Omega(2^{n/3})$, time-reversal symmetries $\Omega(2^{2n/7})$, each against arbitrary algorithms without memory, even with ancillas. The tool is the tree representation of adaptive protocols and a direct total variation bound via one-sided likelihood ratios.

### Placement in the tables

* **Task type:** Identifying, one bit (purity, channel tests) and estimating (shadow tomography); the row sits under identifying because the sharpest statements are distinguishing problems, and the estimating bounds are reduced to them via Le Cam.
* **Object:** state or channel. **Access:** sample without quantum memory (every copy measured individually, adaptivity allowed), with $k$ qubits of memory, or with full memory; for channels arbitrary inputs with $m > n$ qubits and ancillas.
* **Status:** 🟢 🔴 🟢 without memory (copies exponential), 🟢 🟢 🟢 with $O(n)$ qubits of memory: $O(1)$ copies for purity (SWAP test), $O(n)$ for all Pauli magnitudes, $O(1)$ calls for the channel tests.
* **Promise:** none; the separations are unconditional and information-theoretic.

### The problem

Huang, Kueng, Preskill had shown $\Omega(M^{1/6}/\epsilon^2)$ and $\Omega(2^{n/3}/\epsilon^2)$ without memory, against upper bounds $O(M\log M/\epsilon^2)$ and $\tilde O(2^n)$; Aharonov, Cotler, Qi had channel separations only without ancillas. How large are the gaps really, and does the separation hold against all memoryless protocols?

### Key results

* **Theorem 1.1 (shadow tomography).** There are $M$ observables for which $T = \tilde\Theta(\min\{M, 2^n\}/\epsilon^2)$ copies are needed without memory; matching the upper bound from classical shadows up to logarithms. Answers Aaronson's question.
* **Theorem 1.2 (Paulis).** All $\mathrm{Tr}(P\rho)$ to $\epsilon$: $\Omega(2^n/\epsilon^2)$ without memory; the proof is half a page.
* **Theorem 1.3 (purity).** Pure or maximally mixed: $\Omega(2^{n/2})$ without memory, with a matching algorithm $O(2^{n/2})$ (Theorem 5.13); $O(1)$ with a SWAP test.
* **Theorem 1.4 (bounded memory).** $k$ qubits of memory: $\Omega(2^{(n-k)/3})$ copies for all Pauli magnitudes; $O(n)$ with $n$ qubits of memory.
* **Theorems 1.5, 1.6 (channels).** Depolarizing versus Haar-unitary $\Omega(2^{n/3})$; unitary, orthogonal, or symplectic $\Omega(2^{2n/7})$; both against arbitrary memoryless protocols with ancillas, where Aharonov–Cotler–Qi had shown it only without ancillas.

### Methodological approach

* Le Cam's two-point method with null hypothesis $\rho_{\mathrm{mm}}$ and mixture $\rho_P = 2^{-n}(I + \epsilon P)$; the innovation is to work directly with total variation instead of $\chi^2$ or KL (which would give only $\mathrm{poly}(n, 1/\epsilon)$ for Paulis) and to use Fact 2.1: a one-sided bound $\mathbb{E}_P[q_1^P(x)]/q_0(x) > 1-\delta$ on all leaves gives $d_{\mathrm{TV}}\leq\delta$.
* Tree representation (Section 2.1): an adaptive protocol without memory is a tree whose nodes are POVMs on fresh copies and whose leaves are outputs; the edge probabilities depend on the unknown state, and the likelihood ratios are controlled along the paths.
* For channels and bounded memory more is needed (matrix concentration, martingales), because the one-sided bound does not hold everywhere.

### Significance and applications

* The bounds are visible at a few dozen qubits; quantum computers with fewer than a hundred qubits could provide a provable advantage in experimentation as memory. This is the theoretical basis of the Sycamore experiment of Huang et al. (Science 2022).
* Since this paper, the tree technique is the standard tool for bounds against adaptive memoryless protocols (Chen–Huang–Li–Liu; Chen–Gong–Zhang; Lowe–Nayak).

### Relation to this project

* The two-copy advantage of this project's protocol is quantified in Theorems 1.2 and 1.4: without memory $\Omega(2^n)$ copies for all Pauli magnitudes, with one stored copy $O(n)$. Phase 1 (magnitudes of the displacement spectrum) is exactly the task of Theorem 1.4, and $\rho\otimes\rho^*$ is the $k = n$ rung of the memory axis.
* The bound $\Omega(2^{(n-k)/3})$ is the instance ladder in the memory dimension: every qubit of memory buys a constant factor in the exponent, and the question "memory between zero and two copies" gets its first quantitative answer here.
* The proof technique shows which distributions are hard: $\rho_P = 2^{-n}(I + \epsilon P)$ is a displacement spectrum with a single heavy address; this project's hardness instance (LWE) is the structured version of it.

### Limitations and open questions

* The memory–copies curve is known only from below; between $k = 0$ and $k = n$ the exact sample complexity is open.
* The channel separations are unconditional but not tight ($2^{n/3}$, $2^{2n/7}$ against $O(1)$).
* Noise in the memory is not modelled.

### Questions for further study

* What does the half-page calculation for Theorem 1.2 look like, and what changes when the mixture runs over displacement operators instead of Paulis?
* What role do ancillas play in the channel bounds, and why does the technique of Aharonov–Cotler–Qi break down already with one ancilla qubit?
* Is the bound $\Omega(2^{(n-k)/3})$ for magnitudes achievable with a protocol that stores $k$ qubits of a conjugate copy?

Paper: [arXiv:2111.05881](https://arxiv.org/abs/2111.05881)

---

## Quantum advantage in learning from experiments (arXiv:2112.00778)

The paper by **Hsin-Yuan Huang, Michael Broughton, Jordan Cotler, Sitan Chen, Jerry Li, Masoud Mohseni, Hartmut Neven, Ryan Babbush, Richard Kueng, John Preskill, and Jarrod R. McClean** (Caltech, Google Quantum AI, Harvard, Berkeley, Microsoft, JKU Linz, AWS; *Science* 2022) distinguishes two kinds of experiments. In *conventional* ones, every copy is measured individually and processed classically. In *quantum-enhanced* ones, copies are collected in a quantum memory and processed jointly. For three classes of tasks the authors prove an exponential advantage of the second kind: predicting observables, principal component analysis of noisy states, and learning processes. They demonstrate two tasks on the Sycamore processor with up to 40 qubits and 1300 gates; the advantage remains clearly visible despite hardware noise.

### Placement in the tables

* **Task type:** mixed. Theorem 1 is estimating: the magnitude $\vert\mathrm{Tr}(O\rho)\vert$ of a Pauli observable that is named only after the measurement. Theorem 2 estimates a property of the principal component, Theorem 3 the outputs of a process on average. The second experiment is identifying: the symmetry class of a unitary. The paper sits under identifying next to Chen, Cotler, Huang, Li, because all lower bounds run through distinguishing tasks. For the estimating row "All $4^n$ Pauli observables, two-copy" it provides the hardware evidence of the two-copy separation, for the row "Fixed-unitary and symmetry-class distinction" that of the coherence separation for processes.
* **Object:** state, channel, or unitary. **Access:** sample. Conventionally, every copy is measured individually, adaptivity allowed. Quantum-enhanced, Theorem 1 measures two copies jointly in the Bell basis, and Theorem 2 gets by with $O(1)$ copies. In the dynamics experiment, the unitary is applied twice per experiment, entangled with $n$ memory qubits; in the sense of the access ladder these are oracle calls.
* **Status:** Theorems 1 and 2: 🟢 🟢 🟢 with two-copy memory; without memory the copies are 🔴, $\Omega(2^n)$ and $\Omega(2^{n/2})$ respectively. Theorem 3: $\tilde O(\mathrm{poly}(n)\log(1/\delta)/\epsilon^4)$ uses, but without a time guarantee, because hypothesis selection runs over a covering net of all polynomial-size processes.
* **Promise:** no class of states. The separating instance is $\rho = 2^{-n}(I + 0.9sP)$, unentangled. Theorem 2 assumes a constant eigenvalue gap of the principal component, Theorem 3 a process of polynomial circuit size and prediction on average over an input distribution.

### The problem

Chen, Cotler, Huang, Li (2021) and Huang, Kueng, Preskill (2021) had proven exponential memory separations, but for tasks with exponentially many observables that no experiment can query. Aharonov, Cotler, Qi had formulated separations for distinguishing tasks on unitaries. Three things were open: whether a separation holds already for a single observable named afterwards, whether it survives the noise of today's hardware, and whether quantum PCA (Lloyd, Mohseni, Rebentrost) is provably advantageous against all conventional methods.

### Key results

* **Theorem 1 (observables; formally Theorem 6).** By Definition 2, with probability $1/2$ $\rho = I/2^n$ and $O$ is a random Pauli, otherwise $\rho = 2^{-n}(I + 0.9sP)$ and $O = P$. Predicting the magnitude $\vert\mathrm{Tr}(O\rho)\vert$ to $0.25$ with probability $0.8$ costs $\Omega(2^n)$ copies conventionally and $O(1)$ quantum-enhanced: one Bell measurement qubit by qubit on two copies. The state is unentangled, a mixture of product states.
* **Theorem 7 (comparison task).** Which of two named Paulis $Q_1, Q_2$ has the larger magnitude? Conventionally at least $\frac{2^n+1}{0.8505}\log\frac{2}{1+2\delta}$ experiments are needed. This is the task of the hardware experiment.
* **Theorem 2 (quantum PCA; formally Theorems 8 and 9).** At constant eigenvalue gap of the principal component $\vert\varphi\rangle$, $\langle\varphi\vert Z_1\vert\varphi\rangle$ or the near-term variant $\mathrm{Tr}(Z_1\rho^2)/\mathrm{Tr}(\rho^2)$ (virtual distillation) can be estimated to $0.25$: conventionally with $\Omega(2^{n/2})$ copies, quantum-enhanced with $O(1)$. Theorem 10 gives a computationally bounded variant with pseudorandom states: no polynomial-time conventional method distinguishes the two hypotheses.
* **Theorem 3 (processes; formally Theorem 11 and Corollary 2).** For every input distribution $\mathcal{D}$, a quantum-enhanced method learns a model $\tilde{\mathcal{E}}$ of a polynomial-size process with $\mathbb{E}_{\sigma\sim\mathcal{D}}\Vert\tilde{\mathcal{E}}(\sigma)-\mathcal{E}(\sigma)\Vert_1\leq\epsilon$ from $\tilde O(\mathrm{poly}(n)\log(1/\delta)/\epsilon^4)$ uses. Conventionally, already a process that always outputs a state from Definition 2 needs $\Omega(2^n)$ uses.
* **Theorem 13 (bounded memory).** With registers of $n + k$ qubits, every method needs $\Omega(2^{(n-k)/3})$ copies for $\vert\mathrm{Tr}(O\rho)\vert$; the memory therefore has to grow with $n$.
* **Theorem 5 (noise).** A noisy conventional protocol is again a protocol with different POVMs; the lower bound stays valid. Noise does not help the conventional learner.
* **Experiment 1 (states).** $\rho = 2^{-n}(I + \alpha P)$ with $\alpha = \pm 0.95$ on $n = 8$ to $20$ system qubits, plus equally many memory qubits. The Bell snapshots go into a recurrent neural network (GRU), trained on noiseless simulations with $n < 8$. Conventionally, with random Pauli measurements, the success rate from $n\geq 10$ on is practically at guessing level with 1000 experiments, and 70 % is not reached even with 5000 experiments. Quantum-enhanced, the required number lies far below the proven lower bound for any conventional method.
* **Experiment 2 (dynamics).** Unknown 1D or 2D circuits, either time-reversal symmetric (real orthogonal) or general unitary. Conventionally, $U$ is applied to $\vert 0\rangle^{\otimes n}$ and each qubit is measured in the $Y$ basis; under $T$ symmetry the amplitudes are real and $\langle Y\rangle = 0$. Quantum-enhanced, $n$ memory qubits are entangled, then $U$ is applied, system and memory are swapped, $U$ is applied again, and $n$ Bell measurements are performed. Kernel PCA without labels separates the two classes cleanly on the quantum-enhanced data, not on the conventional data.

### Methodological approach

* **Learning trees.** As in Chen, Cotler, Huang, Li, every conventional adaptive protocol is represented as a tree whose nodes are POVMs on single copies. The lower bounds follow from total variation bounds for distinguishing tasks: many-versus-one (observables), many-versus-many (PCA), and partially revealed, when the Pauli is named only after the measurement.
* **Two-copy Bell measurement.** On qubits, all $P\otimes P$ commute. A transversal Bell measurement on $\rho\otimes\rho$ therefore gives estimators of $\mathrm{Tr}(P\rho)^2$ for all $P$ at once; for the magnitude of the named observable, $N_Q = \Theta(\log(1/\delta)/\epsilon^2)$ snapshots suffice (Lemma 1).
* **Processes.** A covering net of the polynomial-size processes and quantum hypothesis selection (Bădescu, O'Donnell) on a data set in quantum memory.
* **Machine learning as the decoder.** The hardware data are evaluated by a GRU (supervised, states) or by kernel PCA (unsupervised, dynamics). The guarantees of the theorems do not depend on these models.

### Significance and applications

* The first hardware demonstration of a provably exponential memory separation in learning from quantum data. The section "Bell sampling on two copies" and the separation thesis in the appendix ("Separation: QML with Classical and Quantum Data") rest on it.
* Shifts the question of quantum advantage from computational tasks with known input to learning tasks about an unknown physical system. The application picture is quantum sensors that transduce their signal into a quantum memory.
* Settles the dequantization debate for quantum PCA (Tang; Chia et al.): their classical algorithms assume access to entries with exponential precision, and that itself costs exponentially many experiments.
* The advantage occurs for unentangled states. Its source is the incompatibility of the observables, not the entanglement of the state.

### Relation to this project

* Phase 1 of the project is the qudit version of Experiment 1: Bell measurement on two copies, snapshots into a neural network trained on small systems and applied to larger ones. Training on noiseless simulations for small $n$ and testing on larger instances is a model for the generalization of the CNN decoder across $d$.
* The difference: here two identical copies suffice, because on qubits all $P\otimes P$ commute; for $d > 2$ one needs $\rho\otimes\rho^*$ (King, Wan, McClean; Allcock et al.). The hardware evidence of this paper therefore does not carry over automatically to the conjugate pair.
* The task here is estimating with a single heavy address $P$ that is revealed after the measurement. The project has to find the address itself (searching). The instance $\rho = 2^{-n}(I + 0.9sP)$ is a spectrum with exactly one heavy coefficient, the lowest rung of the instance ladder.
* In Experiment 2, time-reversal symmetry means real amplitudes. This is the same condition under which the conjugate is free in the project (section "The conjugate: real with respect to a basis").
* Theorem 5 holds for every bound in the tree model, hence also for the single-copy bounds of King, Wan, McClean on which Phase 1 relies: noise does not make single-copy protocols better.

### Limitations and open questions

* The quantum data are generated in the processor, not transduced from an external system; the authors themselves speak of a proof of principle.
* The separating instances are constructed (random Paulis, Haar states). How large the advantage is for natural states remains open.
* The ML decoders are heuristic. The comparison is with a proven lower bound, but the performance of the GRU itself has no guarantee.
* Theorem 3 is sample-efficient but not time-efficient.
* The separation in Definition 2 needs an amplitude strictly smaller than one ($0.9$). For $(I + sP)/2^n$, according to a footnote of the authors, it is unclear whether the technical difficulty is fundamental.
* Noise in the quantum memory reduces the advantage; Theorem 5 protects only the lower bound, not the upper one.

### Questions for further study

* How many experiments does the GRU decoder actually need at $n = 20$, and how does this scale against the lower bound from Theorem 7?
* Can Experiment 1 be repeated for a qudit with $\rho\otimes\rho^*$, for instance with a real state for which the conjugate is free?
* What changes in the proof of Theorem 6 if $P$ is not named, i.e. the learner has to find the heavy address itself? Does this become the project's LWE question?
* What does the near-term PCA $\mathrm{Tr}(Z\rho^2)/\mathrm{Tr}(\rho^2)$ look like in the displacement picture? Is purification by virtual distillation a way to damp the flat remainder?

Paper: [arXiv:2112.00778](https://arxiv.org/abs/2112.00778)

---

## Tight bounds for quantum state certification with incoherent measurements (arXiv:2204.07155)

The paper by **Sitan Chen, Brice Huang, Jerry Li, and Allen Liu** (Berkeley, MIT, Microsoft; FOCS 2022) determines the copy complexity of mixedness testing with incoherent measurements: $\Theta(d^{3/2}/\epsilon^2)$, even if the measurements are chosen adaptively. Adaptivity therefore does not help, which answers an open question from Wright's thesis and from Bubeck, Chen, Li. For general certification against a known $\sigma$, the paper gives instance-optimal bounds in the fidelity $F(\sigma, I/d)$ and the effective dimension, with a new proof technique based on Gaussian perturbations and matrix martingales.

### Placement in the tables

* **Task type:** Identifying, $M = 1$ (certification): $\rho = \sigma$ or $\Vert\rho - \sigma\Vert_1 > \epsilon$; mixedness testing is the case $\sigma = I/d$.
* **Object:** mixed state in $d$ dimensions. **Access:** sample, incoherent: one copy after another, arbitrary POVMs, adaptivity allowed; no quantum memory.
* **Status:** 🟢 🟢 🟢 with $\Theta(d^{3/2}/\epsilon^2)$ copies, against $\Theta(d/\epsilon^2)$ with entangled measurements (O'Donnell–Wright; Bădescu–O'Donnell–Wright); the memory advantage is a factor $\sqrt d = 2^{n/2}$.
* **Promise:** none; $\sigma$ is known.

### The problem

Bubeck, Chen, Li had shown $\Theta(d^{3/2}/\epsilon^2)$ for nonadaptive and $\Omega(d^{4/3}/\epsilon^2)$ for adaptive incoherent measurements. Does the gap close from above (adaptivity helps) or from below (it does not)? And how does the copy count depend on the reference state $\sigma$, analogous to classical identity testing, whose complexity is governed by the $\ell_{2/3}$ quasinorm of $p$?

### Key results

* **Theorem 1.1 / 6.1 (mixedness).** Copy complexity $\Theta(d^{3/2}/\epsilon^2)$ with incoherent measurements; adaptivity changes only constants.
* **Theorem 1.2 / 8.1 (instance-optimal).** For every $\sigma$ and small $\epsilon$, the copy count lies between $\tilde\Omega\big(\sqrt{d\cdot\underline d_{\mathrm{eff}}}\,F(\underline\sigma, I/d)/\epsilon^2\big)$ and $\tilde O\big(\sqrt{d\cdot\overline d_{\mathrm{eff}}}\,F(\overline\sigma, I/d)/\epsilon^2\big)$, where $\underline\sigma$, $\overline\sigma$ arise by removing eigenvalues of mass $\Theta(\epsilon^2)$ and $\Theta(\epsilon)$ respectively, and $d_{\mathrm{eff}}$ is their rank; for pure $\sigma$ it is $\Theta(1/\epsilon^2)$. The upper bound was known from Chen, Li, O'Donnell for nonadaptive measurements.
* **Conjecture.** For all $\sigma$ the adaptive complexity equals the nonadaptive one; proven when $\epsilon$ is small compared with the smallest eigenvalue of $\sigma$.

### Methodological approach

* Instead of the Paninski perturbation $I/d + \epsilon UZU^\dagger/d$ with Haar $U$, a Gaussian perturbation is used whose likelihood ratio has a self-similar form (Eq. 4); this reduces the analysis to the concentration of a matrix martingale along the tree and a matrix balancing problem.
* Unlike all earlier adaptive bounds, no pointwise bound on the likelihood ratio is needed; exactly that made Bubeck–Chen–Li loose.
* The technique also simplifies the calculations of the predecessors considerably and carries over to other problems.

### Significance and applications

* Answers "does adaptivity help?" negatively for a central testing problem; the follow-up works (Chen, Huang, Li, Liu, Sellke 2023 for tomography; Chen, Gong, Zhang 2024 for shadow tomography, where adaptivity does help) use the same tree-plus-martingale method.
* For NISQ verification, $d^{3/2}$ is the reference: without memory one pays $\sqrt d$ relative to entangled protocols.

### Relation to this project

* Certification against a known $\sigma$ is Phase 2 in the limiting case of a single hypothesis: the probe state is $\sigma$ itself. The instance dependence via $F(\sigma, I/d)$ and $d_{\mathrm{eff}}$ is an instance ladder for reference states, from pure ($1/\epsilon^2$) to maximally mixed ($d^{3/2}/\epsilon^2$).
* The statement "adaptivity does not help" holds for single copies; this project's protocol is two-copy and nonadaptive in Phase 1, adaptive in Phase 2. This paper says that the gain of Phase 2 has to come from the second copy, not from adaptivity alone.
* The Gaussian perturbation as a hard instance is a dense, random displacement spectrum; the LWE instance is its structured relative with a sparse support.

### Limitations and open questions

* The instance-optimal bounds differ polynomially for some $\sigma$ and $\epsilon$; the conjecture that adaptivity does not help is not proven for all $\sigma$.
* Testing only, no estimation; states only, no channels.

### Questions for further study

* What does the self-similar form (4) of the likelihood ratio look like, and why does the need for pointwise bounds disappear?
* What role does the matrix balancing play, and is it where the instance dependence on $F(\sigma, I/d)$ arises?
* What is the bound if a copy of $\sigma$ (instead of its description) is supplied, i.e. for SWAP-test access?

Paper: [arXiv:2204.07155](https://arxiv.org/abs/2204.07155)

---

## Quantum algorithmic measurement (arXiv:2101.04634)

The paper by **Dorit Aharonov** (Hebrew University), **Jordan Cotler** (Harvard), and **Xiao-Liang Qi** (Stanford) asks a question that comes before every learning bound: what is an experiment, formally? The answer is a model of computation, the **QUALM** (*quantum algorithmic measurement*), a mixture of black-box algorithm and interactive protocol. With this model the authors prove the first exponential separation between coherent and incoherent experiments for physically motivated tasks in which the coherent side is efficient in calls *and* gates. The framework is the common language in which the memory separations of the Bell-sampling literature are formulated.

### Placement in the tables

* **Task type:** Identifying. Both theorems are distinguishing tasks with one bit or one of three labels as output. This is property testing of a process, the process counterpart of the purity test in the identifying table.
* **Object:** unitary, as a lab oracle. In the first problem, what is being tested is precisely whether the oracle is stationary: the same unitary at every call, or a new one each time.
* **Access:** both sides of the separation use the same oracle on a fixed input. The only difference is whether the outputs of several calls may be held unmeasured and measured jointly. In the terms of this document, this is the memory axis (appendix, *Measurement power*), not the access ladder.
* **Status:** 🟢 🟢 🟢 with coherent access: $O(1)$ calls, $O(\ell)$ gates for the SWAP test, $2\ell$ qubits of quantum memory. Without coherence at least $\Omega(2^{2\ell/7})$ calls, even adaptively.
* **Promise:** the oracle comes from one of the named ensembles (fixed versus fresh Haar unitary; unitary, orthogonal, or symplectic class); no structural promise beyond that. The resource that separates the two sides is coherence, i.e. quantum memory.
* **Why here and not in the appendix:** the framework itself applies to all three task types and therefore also appears in the appendix. The two proven theorems are, however, identifying tasks, and the summaries follow the task.

### The problem

An experiment is supposed to compute a function of a physical system, for instance the crystal structure from a diffraction image. Unlike an algorithm, it does not receive a classical description of its input, only access through interaction and measurement. Tools from quantum computing have improved experiments for years (error correction in metrology, shadow tomography, compressed sensing), but a model was missing in which the cost of an experiment can be defined and improvements can be proven. Two questions: what does a universal model for experiments look like? And does processing the outputs of an experiment coherently, instead of measuring each one individually, bring a provable advantage?

### Key results

* **Three registers.** $N$ (*nature*): the hidden degrees of freedom to which the laboratory has no direct access, in the example the crystal. $L$ (*lab*): the accessible degrees of freedom that couple to $N$, the X-ray photons. $W$ (*work space*): camera and computer.
* **Lab oracle** $\mathrm{LO} = (\mathcal{E}_{NL}, \rho_N)$: an unknown channel on $N \otimes L$ together with the initial state of $N$. Because $N$ persists between calls, the system may have its own inaccessible memory. Without $N$, the model would be an ordinary black-box algorithm and, according to the authors, not general enough.
* **Task** $(S_{\mathrm{in}}, S_{\mathrm{out}}, f, \mathcal{G})$: a function $f$ from the lab oracle and classical settings (for instance the temperature) to a classical output or a distribution over outputs, together with the admissible gates $\mathcal{G}$ on $L \otimes W$, which never act on $N$.
* **QUALM:** a sequence of gates from $\mathcal{G}$ with slots $\square$ into which the oracle is inserted. The **QUALM complexity** is the number of gates plus the number of calls, optionally with a weight $\lambda$ on the calls. Calls and computation time thus appear in one number; the width of $W$ is the memory parameter.
* **Universality hypothesis:** every physically realizable experiment can be simulated as a QUALM with at most polynomial overhead, the quantum Church–Turing thesis carried over from computations to experiments. This is a hypothesis, not a theorem.
* **Coherent and incoherent** (Defs. 11 and 13). Coherent means: universal gates on $L \otimes W$, no restriction. Incoherent means: only LOCC between $L$ and $W$, and between any two calls at least one complete measurement of $L$ in an orthonormal basis. Adaptivity is allowed in both cases.
* **Theorem 1, fixed-unitary problem.** $\mathrm{LO}_0$ draws a Haar-random unitary on $\ell$ qubits once and applies it at every call. $\mathrm{LO}_1$ draws a new one at every call. Coherently, two calls on $\vert 0\rangle$ and a SWAP test suffice: under $\mathrm{LO}_0$ both outputs are equal and the test always accepts, under $\mathrm{LO}_1$ it accepts on average with probability $\tfrac12 + \tfrac{1}{2D}$, $D = 2^\ell$. Every incoherent QUALM, even adaptive, has QUALM complexity $\Omega(2^{2\ell/7})$.
* **Theorem 2, symmetry class.** Distinguish a fixed Haar-random unitary, orthogonal, or symplectic operator. Coherently, a generalized SWAP test on a maximally entangled state suffices. Incoherently, the same bound holds, because all three oracles are indistinguishable from $\mathrm{LO}_1$ for incoherent protocols, and hence also from each other.
* **Simon is incoherent.** Read as a QUALM, Simon's algorithm accesses each sample individually, with product states and measurements in a product basis. Its advantage lies in the superposition query, i.e. in the oracle, not in coherence across calls.
* **Delimitation.** Earlier separations (Bacon, Childs, van Dam 2005; Huang, Kueng, Preskill 2021) count only calls; there the coherent side also needs exponentially many gates. Here the coherent side is efficient in both budgets.

### Methodological approach

1. **Reduction to simple-measurement QUALMs.** Between two calls, an incoherent QUALM may run many rounds of classical communication between $L$ and $W$. The messages from $W$ to $L$ are classical, so $W$ can be replaced by a classical computer with random bits. For fixed random bits, all weak measurements between two calls collapse into one POVM with rank-1 elements. Every incoherent QUALM is thus a probabilistic mixture of protocols of the form prepare, apply the oracle, measure, repeat, where preparation and measurement basis may depend on all earlier outcomes. A mixture is never better than its best element.
2. **Weingarten calculus.** Under $\mathrm{LO}_1$, the outcome distribution of such a protocol is a simple product, because every call sees a fresh Haar unitary and every output is maximally mixed on its own. Under $\mathrm{LO}_0$ there is a Haar integral over $U^{\otimes k} \otimes \bar U^{\otimes k}$, which the Weingarten functions $W(\tau\sigma^{-1}, D)$ express as a sum over pairs of permutations $\sigma, \tau \in S_k$.
3. **The adaptivity problem.** The sum over the outcomes cannot simply be carried out, because later preparations and bases depend on earlier outcomes. The trick: split each permutation term into two segments, apply $2\vert ab\vert \le \vert a\vert^2 + \vert b\vert^2$, and carry out the sum backwards from the last index $s_k$ via the completeness relation. Result: $\Vert P_k - Q_k\Vert_1 = O(k^3/2^\ell)$ within the range of validity of the Weingarten estimate. This range, not the term $k^3/2^\ell$, sets the exponent $2/7$.

### Significance and applications

* **The first clean evidence** that coherence in the laboratory brings an exponential resource advantage, for tasks with a physical motivation (Floquet system versus random time evolution, symmetry class of a dynamics) and with a coherent protocol that is hardly more than a SWAP test.
* **Precursor of the hardware demonstration.** Huang et al. (Science 2022, in the folder as 2112.00778, with Cotler as coauthor) show such separations on Sycamore. The memory separations of Chen, Cotler, Huang, Li (2021) for purity and Pauli shadow tomography and of Chen, Zhou, Seif, Jiang (2022) for Pauli channels have exactly this form: coherent with small memory against incoherent.
* **Vocabulary.** The model separates two things that in the literature are often both called "access": which oracle nature supplies, and whether its outputs are processed coherently. The appendix of this document adopts this separation (*Measurement power*, the table of the four combinations).

### Relation to this project

**The pipeline as a QUALM.**
* How Phase 1 is classified depends on which oracle one writes down. If nature supplies a pair $\rho \otimes \rho^*$ per call, Phase 1 measures the register $L$ completely and immediately in the generalized Bell basis, an orthonormal basis of $L$: an incoherent QUALM, even a simple-measurement QUALM. If nature supplies only $\rho$ and the laboratory produces $\rho^*$ itself, for instance because $\rho$ is real, the first copy has to wait unmeasured until the second one is there: a coherent QUALM with one copy of memory. The same measurement, two classifications. QUALM forces one to state the oracle explicitly, and that is exactly the paragraph *Access model* that Jarrod's feedback demanded (point A in research.md).
* Phase 2 measures $\rho \otimes \sigma^*$ with a known probe prepared by the laboratory. Because $\sigma^*$ is fixed, this is the same as a POVM on $\rho$ alone, with elements $\mathrm{Tr}_W[(\mathbb{1} \otimes \sigma^*)\,\Pi_u]$. The adaptive choice of probe is therefore an adaptive single-copy measurement, and the reduction from step 1 of the method is the formal version of the statement in the quadrant that adaptivity does not change the row.
* The QUALM complexity counts calls and gates, and the width of $W$ counts the memory. Triple efficiency means polynomiality in all three. CNN training lies outside the model: the trained weights are part of the fixed gate sequence, an *advice* that does not depend on the oracle. What counts is the evaluation of the CNN, and that is exactly what "triple efficiency at inference only" means.

**Bell measurement and SWAP test.**
* On qubits, SWAP is diagonal in the Bell basis. The singlet has eigenvalue $-1$, the three other Bell states $+1$, and transversally over $n$ qubits the Bell outcome $P$ has SWAP eigenvalue $(-1)^{\#Y(P)}$. The SWAP test from Theorem 1 is therefore a coarse-grained Bell measurement: draw a Bell sample, output the parity of the $Y$ factors.
* On qudits with $d \ge 3$ this does not hold (checked numerically for $d = 3, 4, 5$): $\mathrm{SWAP} = \tfrac1d\sum_v D_v \otimes D_v^\dagger$ is not diagonal in the basis $(D_{q,p}\otimes\mathbb{1})\vert\Phi^+\rangle$. This basis instead diagonalizes the $D_v \otimes \bar D_v$, and $\sum_v D_v \otimes \bar D_v = d^2\,\vert\Phi^+\rangle\langle\Phi^+\vert$ is $d$ times the partial transpose of SWAP. This fits the observation of Allcock et al. that Bell sampling on two identical qudit copies loses its qubit properties.
* What remains of the SWAP test is an identity: the Bell outcome $(0,0)$ has probability $\mathrm{Tr}(\rho^2)/d$ on $\rho \otimes \rho^*$, the term at $(a,b) = (0,0)$ in the formula $P(a,b) = d^{-2}\sum_{q,p}\vert y_{q,p}\vert^2\omega^{ap-bq}$. On two identical copies, $\mathrm{Tr}(\rho\rho^{T})/d$ appears there instead, and for complex $\rho$ that is not the purity (both checked numerically). The statistical efficiency of the SWAP test is not preserved: an event of probability $O(1/d)$ used as a purity estimator costs $\Theta(d/\epsilon^2)$ copies. For Phase 1 this is irrelevant, because there the $\vert y_v\vert^2$ count individually, not their sum.

**Searching and the LWE wall.**
* In the fixed-unitary problem, coherence decides everything. In the project's searching problem it decides nothing, at least on the hard instance from `thm:lwe-displacement`. The state $\rho_s = \mathbb{E}\,\vert a,b\rangle\langle a,b\vert$ is diagonal. Dephasing in the computational basis leaves $\rho_s^{\otimes k}$ unchanged, and every dephased copy is a classical LWE sample. Every coherent QUALM on copies of $\rho_s$, with arbitrarily much quantum memory, can therefore be simulated by a quantum algorithm on classical LWE samples that re-prepares the basis states itself. The post-quantum LWE assumption rules out such an algorithm in polynomial time.
* The hardness therefore sits in the oracle, not in the coherence. The task becomes easy only with a different oracle: quantum samples in superposition (Grilo, Kerenidis, Zijlstra 2019) or the preparation circuit. This is the QUALM version of the statement in the quadrant that the hard cell is left only by a promise or by query access.
* For the paper, this would be a one-sentence addition to `thm:lwe-displacement`: the reduction rules out not only every processing of the Bell outcomes, but every coherent multi-copy measurement. This defuses an obvious objection, namely that a protocol with more quantum memory could circumvent the wall. The caveat: the argument needs diagonality. For non-diagonal hard instances, for instance in the cyclic single-qudit basis (Q1), it is open whether memory helps.

**Symmetry class and the conjugate.** Theorem 2 asks for dynamics whether they are orthogonal, i.e. real and time-reversal symmetric. In the taxonomy of influencing factors (research.md, factor A), reality is exactly the condition under which $\rho^* = \rho$ holds and the conjugate costs nothing. For Haar-random dynamics, the theorem says that this property cannot be checked cheaply without coherence. Condition (C1) is therefore rather prior knowledge from physics (for instance a real Hamiltonian without a magnetic field) than something the pipeline verifies on the side.

### Limitations and open questions

* **Toy problems.** Haar-random unitaries are themselves not efficiently implementable, so the lab oracle is exponentially complex. The authors themselves ask for advantages with efficient oracles. Ground and Gibbs states of local Hamiltonians, as in the project, would be such oracles.
* **Noise.** According to the authors, the exponential advantages of their examples disappear under noise; whether QUALM advantages can be shown in the NISQ era is open.
* **Tightness.** The exponent $2/7$ comes from the range of validity of the Weingarten estimate; the main text leaves open whether the bound is tight.
* **Adaptivity.** Whether adaptivity helps in general in the incoherent case is listed by the authors as open; for their two tasks the bound is proven against adaptive protocols.
* **Universality** is a hypothesis, not a theorem.

### Questions for further study

* Does the diagonal reduction also hold in the cyclic single-qudit basis? More concretely: is there a non-diagonal hard instance there against which a protocol with three or more coherently held copies helps? (Q1)
* At which rung of the instance ladder does more memory than the pair first lower the QUALM complexity? The authors ask in general how much a larger work space brings; the open frontier *Memory between zero and two* is the same question from below.
* Can reality, condition (C1), be tested with two identical copies? The SWAP test on $\rho\otimes\rho$ gives $\mathrm{Tr}(\rho^2)$, the Bell outcome $(0,0)$ on $\rho\otimes\rho$ gives $\mathrm{Tr}(\rho\rho^T)/d$, and the difference $\mathrm{Tr}(\rho^2)-\mathrm{Tr}(\rho\rho^T) = \tfrac12\Vert\rho-\rho^*\Vert_F^2$ vanishes exactly for real $\rho$. The second estimator, however, costs $\Theta(d/\epsilon^2)$ copies. Is there an efficient test, or is Theorem 2 a hint that there is none?
* What is in the Supplementary Information? The formal definitions, the complete proof, and the verification example that shows the necessity of $N$ are not in the folder.

Paper: [arXiv:2101.04634](https://arxiv.org/abs/2101.04634) · [doi:10.1038/s41467-021-27922-0](https://doi.org/10.1038/s41467-021-27922-0)

---

## Certifying almost all quantum states with few single-qubit measurements (arXiv:2404.07281)

The paper by **Hsin-Yuan Huang, John Preskill, and Mehdi Soleimanifar** (Caltech, Google Quantum AI; FOCS 2024) certifies the fidelity of a laboratory state $\rho$ with a target state $\vert\psi\rangle$, which is accessible only through an amplitude model $\Psi(x)\propto\langle x\vert\psi\rangle$, from single-qubit Pauli measurements on $O(\tau^2/\epsilon^2)$ copies; $\tau$ is the relaxation time of a random walk on the hypercube with stationary distribution $\vert\langle x\vert\psi\rangle\vert^2$. For all but a $2^{-\Omega(n)}$ fraction of states, $\tau = O(n^2)$; phase and GHZ-like states have $\tau = O(n)$. The surrogate quantity is called the *shadow overlap*.

### Placement in the tables

* **Task type:** Identifying, $M = 1$ (certification): output "Certified" at $\langle\psi\vert\rho\vert\psi\rangle\geq 1-\epsilon/(2\tau)$, "Failed" at $< 1-\epsilon$; no guarantee in between. The gap $\tau$ is the price of single-qubit measurements.
* **Object:** mixed $n$-qubit state against a pure, classically described target. **Access:** sample with single-qubit measurements ($n-1$ qubits in $Z$, one random qubit in a random Pauli basis); query to the model $\Psi$, two queries per copy.
* **Status:** 🟢 🟢 🟢 for $\tau = \mathrm{poly}(n)$: $T = O(\tau^2/\epsilon^2)$ copies with Pauli measurements, $O(\tau/\epsilon)$ with general single-qubit measurements; $O(n^2/\epsilon)$ for almost all states (Theorem 2); time $O(T)$ model queries; memory none.
* **Promise:** polynomial relaxation time of the target; no promise about $\rho$.

### The problem

Earlier certification methods needed deep circuits (shadows, spectrum estimation), exponentially many single-qubit measurements (direct fidelity estimation), or special target classes (stabilizer, MPS), or came without a guarantee (cross-entropy benchmarking). Can the fidelity with a generic, highly entangled target be certified from few single-qubit measurements?

### Key results

* **Protocol 1.** Pick qubit $k$ at random; a $Z$ measurement of the others gives $z$; a Pauli measurement of $k$ gives $\vert s\rangle$; the model queries $\Psi(z^{(0)}), \Psi(z^{(1)})$ define $\vert\Psi_{k,z}\rangle$; local overlap $\omega = \langle\Psi_{k,z}\vert(3\vert s\rangle\langle s\vert - I)\vert\Psi_{k,z}\rangle$; average $\hat\omega$ over $T$ rounds; certify if $\hat\omega\geq 1 - 3\epsilon/(4\tau)$.
* **Eqs. (1), (2).** $\mathbb{E}[\hat\omega]\geq 1-\epsilon\Rightarrow\langle\psi\vert\rho\vert\psi\rangle\geq 1-\tau\epsilon$ and $\langle\psi\vert\rho\vert\psi\rangle\geq 1-\epsilon\Rightarrow\mathbb{E}[\hat\omega]\geq 1-\epsilon$.
* **Theorem 1.** $T = O(\tau^2/\epsilon^2)$ copies; $O(\tau/\epsilon)$ with general single-qubit measurements.
* **Theorem 2.** For all but $2^{-\Omega(n)}$ of the states, $\tau\leq\tau^* = O(n^2)$, hence $O(n^2/\epsilon)$ copies, even for states of exponential circuit complexity.
* **Theorems 4 to 7, Appendices D, G, H, I.** $\mathbb{E}[\omega] = \mathrm{Tr}(L\rho)$ with $L\vert\psi\rangle = \vert\psi\rangle$ and $\langle\psi^\perp\vert L\vert\psi^\perp\rangle\leq 1-1/\tau$; $L$ has the same spectrum as the transition matrix $P$ of the random walk (Eq. 8); relaxation times for Haar states via multicommodity flows with a "local escape property", $O(n)$ for phase states and GHZ, and for ground states; level-$m$ variants (Protocol 2) with $2^{2m}/\epsilon^2$ copies.

### Methodological approach

* Measuring qubit $k$ in a random Pauli basis is a single-qubit shadow; averaged, $3\vert s\rangle\langle s\vert - I$ is an unbiased estimator of the single-qubit reduction after conditioning on $z$, hence $\mathbb{E}[\omega] = 1$ for $\rho = \vert\psi\rangle\langle\psi\vert$.
* The model is needed only for the conditional single-qubit ratio $\Psi(z^{(1)})/\Psi(z^{(0)})$; unnormalized models (neural networks, tensor networks, circuits with amplitude queries) suffice.
* The random walk is only an analysis tool; its gap $1/\tau$ measures how far $L$ deviates from the projector.

### Significance and applications

* Verification of generic states with the cheapest measurement primitive; at the same time a learning primitive: a model that maximizes the shadow overlap learns the state (applications to neural and tensor network models in the paper).
* The proof that states of exponential complexity are certifiable clearly separates certification from learning.

### Relation to this project

* The shadow overlap is a certificate from a single-qubit measurement plus two model queries; for this project's pipeline, the question is whether a sparse spectrum learned from Bell sampling can serve as the model $\Psi$. A sparse displacement spectrum delivers amplitude ratios in $O(k)$ time, so certification of the learning result would be cheap.
* The relaxation time is an instance quantity that depends on the structure of the target, not on its complexity; this is a model for an instance ladder measured not in $t$ or $k$ but in mixing times.
* The gap between "Certified" and "Failed" (factor $2\tau$) is a tolerance parameter as in Bao et al.; both show that one-bit tasks have tolerance gaps with a polynomial factor.

### Limitations and open questions

* States with exponential relaxation time (for instance superpositions of widely separated basis states, like $\vert 0^n\rangle + \vert 1^n\rangle$ without the level-$m$ variant) are not covered; the level-$m$ protocol costs $2^{2m}$.
* The model has to supply amplitudes in the computational basis; for states given only as a circuit, the query itself is expensive.
* The gap $\tau$ between the two thresholds is inherent, not just a proof artefact.

### Questions for further study

* How is $L$ constructed, and why does it have exactly the spectrum of $P$?
* How does the "local escape property" work for Haar states, and why does it suffice for $\tau = O(n^2)$?
* Can Bell sampling on $\rho\otimes\rho^*$ take over the role of the single-qubit measurement and eliminate the gap $\tau$, because it sees the overlap $\vert\mathrm{Tr}(\rho\sigma)\vert$ directly?

Paper: [arXiv:2404.07281](https://arxiv.org/abs/2404.07281)

---

## Non-Markovian quantum process tomography (arXiv:2106.11722)

The paper by **Gregory A. L. White, Felix A. Pollock, Lloyd C. L. Hollenberg, Kavan Modi, and Charles D. Hill** (Melbourne, Monash; PRX Quantum 2022) formalizes tomography of the *process tensor*, the generalization of process tomography to multi-time dynamics with memory. It builds a maximum-likelihood reconstruction with a projection onto positivity and causality, makes the procedure efficient for processes of finite Markov order $\ell$, and shows on IBM devices that characterizing non-Markovian correlations increases the fidelity of multi-time circuits.

### Placement in the tables

* **Task type:** Identifying against a class (processes of Markov order $\ell$), realized as estimating all parameters of the process tensor; the row sits under identifying because the efficiency comes from the choice of class and the paper supplies a test for which order is needed.
* **Object:** process $\Upsilon_{k:0}$ over $k$ time steps on one qubit, a Choi state of dimension $d^{2k+2}$. **Access:** query; sequences of control operations from an overcomplete basis ($N_{\mathrm{oc}} = 24$ per step) or a minimal one ($N_{\mathrm{mle}} = 10$), then measurement.
* **Status:** 🟢 🟢 🟢 for fixed $\ell$: $O(kN_{\mathrm{mle}}^\ell)$ circuits instead of $O(N_{\mathrm{oc}}^k)$; without a memory bound exponential in $k$, in general $O(d^{4k})$ experiments.
* **Promise:** finite Markov order; its violation is itself measurable (tradeoff between characterization effort and accuracy).

### The problem

CPTP maps describe two-time errors; real devices show temporal correlations (the choice of a past gate influences the next one), which the sum of gate errors underestimates and which can undermine error correction. How can a process with memory be characterized completely, statistically robustly, and at reasonable cost?

### Key results

* **Process tensor tomography (Section II).** QST needs $O(d^2)$, QPT $O(d^4)$, PTT $O(d^{4k})$ experiments; linear inversion (LI-PTT) with an overcomplete basis scales as $O(N_{\mathrm{oc}}^k)$ circuits and is sensitive to the amplification of small errors in the superoperator basis.
* **MLE-PTT (Section III).** A convex log-likelihood with projected gradient descent onto the intersection of the constraints completely positive and causal (Eqs. 13, 15); the projection is nontrivial and improves on Dykstra's alternating projection. Reduction to $O(N_{\mathrm{mle}}^k)$ with $N_{\mathrm{mle}} = 10$; reconstruction fidelity on IBM hardware around $0.999$ (Section III, Fig. 5).
* **Markov order (Section IV).** Adaptive truncation of weak long-time correlations to order $\ell$; scaling $O(kN_{\mathrm{mle}}^\ell)$; the residual deviation quantifies how much a model with bounded memory misses in its predictions.
* **Control (Section V).** Characterization for $\ell\in\{1, 2, 3\}$ and using the correlations as a resource increases the fidelity of multi-time circuits; higher order, better prediction.

### Methodological approach

* The process tensor is a Choi state over $k+1$ inputs and outputs; causality constraints (the future does not influence the past) are affine constraints; incomplete bases ("restricted" tensors) are nevertheless useful for predictions within the basis.
* Reconstruction fidelity: the predictions of the reconstructed tensor are compared with random sequences, not with a ground truth, because none exists.

### Significance and applications

* A missing piece in the zoo of characterization methods (QCVV); a basis for memory-aware control and error mitigation, hardware-agnostic.
* For learning theory, the first protocol that formulates query access to processes with memory as a learning problem with an explicit class assumption (Markov order).

### Relation to this project

* The Markov order is an instance ladder for processes: $\ell$ plays the role of $t$ for Clifford+T or of $D$ for MPS, and $O(kN^\ell)$ against $O(N^k)$ is the efficiency gain of a class promise.
* The process tensor is the time-axis version of a state on $2k+2$ registers; Bell sampling on conjugate Choi states would be the natural two-copy primitive to learn its displacement spectrum, and the causality constraints would appear there as sparsity patterns.
* The MLE projection onto the physical cone is what a CNN decoder would have to learn implicitly; the paper supplies the explicit constraints.

### Limitations and open questions

* One qubit, small $k$; the scaling stays exponential in the system size, and in $k$ without an order bound.
* The control pulses must themselves be of high fidelity; SPAM errors and basis incompleteness limit the reconstruction.
* No sample complexity guarantee in the learning-theoretic sense.

### Questions for further study

* How exactly is the projection onto the intersection of positivity and causality computed, and how does it scale?
* How is the Markov order chosen adaptively, and is there a criterion analogous to the singular value threshold $\eta$ in Fanizza et al.?
* Can a process tensor of finite order be read as a finitely correlated state along the time direction, so that the spectral reconstruction applies?

Paper: [arXiv:2106.11722](https://arxiv.org/abs/2106.11722)

---

## Pseudorandom quantum states (arXiv:1711.00385)

The paper by **Zhengfeng Ji, Yi-Kai Liu, and Fang Song** (UTS Sydney, NIST/Maryland, Portland State; CRYPTO 2018) defines pseudorandom quantum states (PRS): families $\{\vert\phi_k\rangle\}_{k\in\mathcal{K}}$ that are efficiently preparable and such that polynomially many copies are indistinguishable, for every polynomial-time quantum algorithm, from equally many copies of a Haar-random state. The construction uses random phase states $\vert\phi_k\rangle = N^{-1/2}\sum_x\omega_N^{\mathrm{PRF}_k(x)}\vert x\rangle$ built from quantum-secure pseudorandom functions; applications are a cryptographic no-cloning theorem and private-key quantum money.

### Placement in the tables

* **Task type:** Identifying, one bit (PRS or Haar), and with that the source of hardness for identifying against large classes: whoever can learn a class that contains PRS can distinguish it from Haar. The row is the cryptographic reference of the identifying table.
* **Object:** family of states. **Access:** sample, polynomially many copies of the same $\vert\phi_k\rangle$; in the strong variant (Theorem 4) additionally query access to the reflection oracle $I - 2\vert\phi_k\rangle\langle\phi_k\vert$, without any gain.
* **Status:** 🟢 🔴 🟢: statistically, the family is learnable from polynomially many copies, since it has only $\vert\mathcal{K}\vert = 2^{\mathrm{poly}(\kappa)}$ members (hypothesis selection), but no polynomial-time distinguisher exists; the key is polynomial.
* **Promise:** existence of quantum-secure one-way functions (equivalently: QPRFs, QPRPs).

### The problem

Classical pseudorandom strings are too weak for quantum states: a family of random basis states looks like $I/2^n$ on one copy but is trivial. The right definition has to allow many copies. What is a family that looks Haar-random even on polynomially many copies, and what follows from it?

### Key results

* **Definition 2 (PRS).** Efficient generation $G(k) = \vert\phi_k\rangle$ and $\vert\Pr_k[A(\vert\phi_k\rangle^{\otimes m}) = 1] - \Pr_{\psi\sim\mu}[A(\vert\psi\rangle^{\otimes m}) = 1]\vert = \mathrm{negl}(\kappa)$ for all efficient $A$ and $m = \mathrm{poly}(\kappa)$.
* **Theorem 1.** For every QPRF, the family of random phase states (Eq. 6) is a PRS; preparation with one query to the PRF (Hadamard, QFT on $\vert 1\rangle$, subtraction in the second register).
* **Lemma 2.** For a truly random $f$, $\vert f\rangle^{\otimes m}$ is statistically indistinguishable from Haar$^{\otimes m}$; the proof computes $\rho^m = \mathbb{E}_f[\vert f\rangle\langle f\vert^{\otimes m}]$ explicitly in the basis of the symmetric subspace (Eqs. 4, 5).
* **Theorem 3 (no-cloning).** For every PRS and $m < m'$, the success probability of producing $m'$ copies from $m$ is negligible; proof: a cloner plus a SWAP test would be a distinguisher.
* **Theorems 4, 5.** Strongly pseudorandom (with reflection oracle) if and only if pseudorandom; oracle access with $q$ queries can be simulated with $O(q)$ copies.
* **Theorem 7.** The quantum money scheme built from PRS is secure.

### Methodological approach

* Three hybrids: PRF phases, truly random phases, Haar; the first transition is PRF security, the second is Lemma 2 with a moment calculation in the symmetric subspace.
* The core is that the $m$-th moments of random phase states approximate the Haar moments up to $O(m^2/N)$; this is an approximate $m$-design statement about phase states.

### Significance and applications

* The founding paper of quantum pseudorandomness; Brakerski–Shmueli (binary phases), Kretschmer (learning hardness from PRS), Zhao et al. (gate complexity), Mele–Herasymenko (fermions), and Aaronson et al. (pseudoentanglement) build on it.
* No-cloning and quantum money without verification by the issuer; PRS are the minimal assumption for much of what previously required one-way functions.

### Relation to this project

* PRS are the example of states that are information-theoretically trivial and computationally impenetrable; this project's LWE instance is the displacement version: a spectrum whose support is sparse but can be found only with the key. Both show that the learning hardness sits in the decoder.
* Random phase states have a flat displacement spectrum (magnitude $\approx 2^{-n}$ on all addresses); Bell sampling on $\rho\otimes\rho^*$ samples from it almost uniformly. This is why the instance ladder ends at phase states of high degree: there is no support to find.
* Theorem 5 (oracle access gives nothing beyond copies) is a statement about the access ladder: for PRS, query = sample.

### Limitations and open questions

* Security is conditional (QPRF); no unconditional separations.
* PRS with $\omega_N$ phases; the binary simplification came with Brakerski–Shmueli.
* Pseudorandom unitaries (PRU) are proposed but not constructed.

### Questions for further study

* What does the moment calculation in Lemma 2 look like concretely, and is the error bound $O(m^2/N)$ tight?
* How does Theorem 5 (reflection oracle simulable by copies) translate into the language of the access ladder, and does it hold for non-reflection oracles?
* What is the minimal structure (degree of the phase polynomial) at which phase states become pseudorandom, compared with $\Theta(n^d)$ copies for degree $d$?

Paper: [arXiv:1711.00385](https://arxiv.org/abs/1711.00385)

---

## Quantum pseudoentanglement (arXiv:2211.00747)

The paper by **Scott Aaronson, Adam Bouland, Bill Fefferman, Soumik Ghosh, Umesh Vazirani, Chenyi Zhang, and Zixin Zhou** (UT Austin, Stanford, Chicago, Berkeley; ITCS 2024) constructs pseudorandom states with entanglement entropy $\Theta(f(n))$ across every cut simultaneously, for every $f(n) = \omega(\log n)$, from quantum-secure one-way functions. This yields a pseudoentangled pair of ensembles with a gap of $\Theta(n)$ versus $\omega(\log n)$ that is indistinguishable in polynomial time; applications are lower bounds for MPS testing ($\Omega(\sqrt r)$), Schmidt rank estimation, and entanglement distillation, as well as consequences for AdS/CFT.

### Placement in the tables

* **Task type:** Identifying, one bit: high or low entanglement, MPS with bond dimension $r$ or far from it. The statement is a hardness result: the test is statistically possible but computationally not.
* **Object:** families of states $\vert\Psi_k\rangle$, $\vert\Phi_k\rangle$ with key $k$. **Access:** sample, polynomially many copies.
* **Status:** 🟢 🔴 🟢; for MPS testing, additionally $\Omega(\sqrt r)$ copies information-theoretically (Theorem 3.5), hence 🔴 in the copies for exponential $r$.
* **Promise:** quantum-secure one-way function; the construction can be realized in logarithmic depth.

### The problem

Ji–Liu–Song show that PRS must have entanglement $\omega(\log n)$ across every cut; Gheorghiu–Hoban achieve, from LWE, a gap of $n$ versus $n-k$ for constant $k$. Is the maximal gap $\Theta(n)$ versus $\omega(\log n)$ achievable, across all cuts simultaneously, from arbitrary one-way functions, and with Haar indistinguishability?

### Key results

* **Definition (PES).** Two efficiently preparable ensembles with entropy $\Theta(f(n))$ and $\Theta(g(n))$ respectively across every cut (with probability $1 - 1/\mathrm{poly}$), and indistinguishability on $p(n)$ copies.
* **Construction (Sections 2.1 to 2.3).** Subset phase states $\vert\psi_{f,p}\rangle = 2^{-k/2}\sum_{x\in\{0,1\}^k}(-1)^{f(p(x0^{n-k}))}\vert p(x0^{n-k})\rangle$ with a QPRP $p$ and a QPRF $f$; preparation: $H^{\otimes k}$, $p$, uncompute, phase oracle.
* **Theorem 2.1.** For $t < K\leq 2^n$, the trace distance between $t$ copies of a random subset phase state with $\vert S\vert = K$ and $t$ copies of a Haar state is $O(t^2/K)$; hence pseudorandom as soon as $K = 2^{\omega(\log n)}$.
* **Theorem 2.7 / Corollaries 2.6.1, 2.6.2.** For $\omega(\log n)\leq k\leq n$ and $\vert S\vert = 2^k$, the entanglement entropy across every cut $(X, Y)$ with $\vert X\vert, \vert Y\vert\geq k$ is $\Theta(k)$; the upper bound follows from the Schmidt rank, the lower bound from 4-wise independent phase functions (Theorem B.7).
* **Theorem 1 / Corollary 1.0.1.** PRS with entropy $\Theta(f(n))$ for every $f = \omega(\log n)$; PES with gap $\Theta(n)$ versus $\omega(\log n)$.
* **Theorem 3.5 (MPS testing).** For $r\leq 2^{n/8}$, an MPS$(r)$ tester needs $\Omega(\sqrt r)$ copies, information-theoretically as well as computationally; incomparable with Soleimanifar–Wright ($\Omega(\sqrt n)$), stronger for large $r$.

### Methodological approach

* The entanglement of a subset state is bounded by $\log\vert S\vert$; pseudorandomness only requires $\vert S\vert$ to be superpolynomial. The separation between "Haar moments" ($t$-design property up to $t\ll\sqrt K$) and "entropy" ($\log K$) is the whole mechanism.
* The earlier version (QIP 2023) reduced entanglement across only one cut; the new construction is simpler and stronger.

### Significance and applications

* Entanglement is not an efficiently observable quantity: two ensembles with linearly different entropy are indistinguishable. Relevant for property testing (Schmidt rank, MPS), for distillation protocols via the Schur transform, and for the computability of holographic dualities.
* Basis for pseudomagic (Gu, Leone, Ghosh, Eisert, Yelin, Quek 2023) and for the sample lower bounds in Chen–Gong–Ye–Zhang.

### Relation to this project

* Subset phase states have a displacement spectrum that is controlled by the size $K$ of the support in the computational basis; for $K = 2^{\mathrm{polylog}}$ the spectrum is flat enough for pseudorandomness, but the state has only polylogarithmic entanglement. This is an instance in which sparsity in the computational basis, without a dictionary that names the support, remains computationally invisible: a warning that sparsity without the key does not guarantee learnability.
* The $\Omega(\sqrt r)$ bound for MPS testing is a sample bound against a class promise; it says that the bond dimension enters the copy count as an instance parameter, not only the time.
* Pseudoentanglement is the kind of hardness that no memory removes: even $\rho\otimes\rho^*$ sees only Haar moments.

### Limitations and open questions

* The construction is an ensemble, not a single state; statements about "typical" physical states do not follow.
* The gap holds for entropy; whether the same indistinguishability holds for other entanglement measures (negativity, Rényi-$\alpha$) is treated partially.
* Conditional on one-way functions.

### Questions for further study

* How does the 4-wise independence of the phase function enter the lower entropy bound (Theorem B.7)?
* What does the proof of Theorem 2.1 with the condition $t < K$ look like, and what happens at $t\approx\sqrt K$?
* Is the displacement spectrum of a subset phase state with $K = 2^k$ flat up to a factor $2^{-k}$, and what does Bell sampling on $\rho\otimes\rho^*$ then actually see?

Paper: [arXiv:2211.00747](https://arxiv.org/abs/2211.00747)

---

## Learning quantum states and unitaries of bounded gate complexity (arXiv:2310.19882)

The paper by **Haimeng Zhao, Laura Lewis, Ishaan Kannan, Yihui Quek, Hsin-Yuan Huang, and Matthias C. Caro** (Caltech, Tsinghua, Google Quantum AI, Harvard, MIT, FU Berlin; PRX Quantum 2024) determines the cost of learning states $U\vert 0^n\rangle$ and unitaries $U$ built from $G$ two-qubit gates: $\tilde\Theta(G/\epsilon^2)$ copies for states, independent of $n$; $\tilde O(G\min\{1/\epsilon^2, \sqrt{2^n}/\epsilon\})$ and $\Omega(G/\epsilon)$ queries for unitaries on average over inputs; $\Omega(2^{\min\{G/2C, n/2\}}/\epsilon)$ in the worst case. Under the assumption that RingLWE cannot be solved by quantum computers in subexponential time, every learner needs time $\exp(\Omega(\min\{G, n\}))$; $G = O(\log n)$ is the transition to efficiency.

### Placement in the tables

* **Task type:** Identifying against a class with a promise (gate count $G$); the class is exponentially large and parametrized, so this is the point at which identifying turns into searching. The sample bound is information-theoretic, the time bound cryptographic: the thesis of this document in one sentence.
* **Object:** pure state or unitary. **Access:** sample (copies; single-copy measurements suffice); query access to $U$, also $U^\dagger$ and controlled $U$ in the lower bounds; classically described input–output pairs (Theorem 5).
* **Status:** 🟢 🔴 🟢. Copies $\tilde\Theta(G/\epsilon^2)$, time exponential in $\min\{G, n\}$, memory polynomial (one circuit with $G$ gates).
* **Promise:** gate count $G$; for $G = O(\log n)$ polynomial time via junta learning.

### The problem

Full tomography costs $\Theta(4^n/\epsilon^2)$; physical states arise from few gates. How do copies, queries, and time scale with $G$, and where is the efficiency boundary? And why do quantum no-free-lunch theorems ($\Omega(2^n)$ samples for generic unitaries) not contradict the bound that is linear in $G$?

### Key results

* **Theorem 1 (states).** $N = \tilde\Theta(G/\epsilon^2)$ copies are necessary and sufficient for trace distance $\epsilon$; upper bound via a covering net of the $G$-gate states plus quantum hypothesis selection, lower bound via a packing net. Improves $\tilde O(nG^2/\epsilon^4)$ of Huang et al.
* **Theorem 2 (time, states).** Under subexponential hardness of RingLWE, every learner for $\tilde O(G)$-gate states needs time $\exp(\Omega(\min\{G, n\}))$; for $G = O(\log n)$ polynomial.
* **Theorem 3 (unitaries, worst case).** Diamond distance: $\Omega(2^{\min\{G/2C, n/2\}}/\epsilon)$ queries necessary, $\tilde O(2^nG/\epsilon)$ sufficient; proof via the adversary method.
* **Theorem 4 (unitaries, average case).** Root-mean-square trace distance over Haar inputs, equivalently over any locally scrambled ensemble: $\tilde O(G\min\{1/\epsilon^2, \sqrt{2^n}/\epsilon\})$ queries with maximally entangled inputs and Choi–Jamiołkowski, $\Omega(G/\epsilon)$ necessary; without ancillas $\tilde O(G\min\{1/\epsilon^4, (\sqrt{2^n})^3/\epsilon\})$.
* **Theorem 5 (classical descriptions).** $O(2^n/r)$ input–output pairs with inputs of rank $r$ suffice and are necessary; this resolves the apparent contradiction with the no-free-lunch theorem.
* **Theorem 6 (time, unitaries).** The same hardness $\exp(\Omega(\min\{G, n\}))$; hence there is no polynomial-time learner for Clifford+T circuits with $\tilde\omega(\log n)$ T gates, which answers the fifth question of the Anshu–Arunachalam survey in the negative.
* **Theorem 7 (physical functions).** To approximate arbitrary 1-bounded 1-Lipschitz functions on $[0,1]^\nu$, a parametrized circuit needs $G\geq\tilde\Omega(\epsilon^{-\nu/2})$ gates and $\Omega(\epsilon^{-\nu})$ samples; quantum neural networks do not evade the curse of dimensionality.

### Methodological approach

* Covering nets over the gate parameters, hypothesis selection (Bădescu–O'Donnell, here with classical shadows) for the optimal $\epsilon$ rate; packing nets for the lower bound.
* Hardness through PRS constructions with $\tilde O(G)$ gates that are indistinguishable from Haar: an efficient learner would be a distinguisher.
* Numerics with shallow Clifford shadows up to $n = 10^4$ qubits confirm the linearity in $G$ and the independence of $n$.

### Significance and applications

* A fine-grained view of tomography: for the copies, what counts is not the dimension but the circuit complexity; the time follows a different logic.
* The boundary $\log n$ is sharp for states and unitaries alike and coincides with the boundary of the Clifford+T learners.

### Relation to this project

* The row is the formal version of the thesis "sample-easy, time-hard": every statement of this project about the LWE instance has to be measured against $\exp(\Omega(\min\{G, n\}))$. The displacement instance has $G = \mathrm{poly}(n)$; it therefore lies in the hard regime of this theorem, and the only question is whether the additional sparsity structure changes that.
* Theorem 5 is the access ladder for processes: rank $r$ of the inputs buys a factor $r$ in the samples; this is the process counterpart of the memory axis for states.
* The sample bound $\tilde\Theta(G/\epsilon^2)$ with single-copy measurements says that for pure states there is no two-copy advantage in the copy count; the advantage of this project's protocol has to lie in the time or in mixed states.

### Limitations and open questions

* Pure states and unitaries only; mixed states and channels need other methods, and there two-copy protocols could have a copy advantage.
* Worst-case hardness; whether typical $G$-gate states are hard is open (average case).
* Constant depth with spread-out gates is efficiently learnable (Huang et al.), although $G = \Theta(n)$; the gate count is therefore not the only parameter.

### Questions for further study

* How does the equivalence for locally scrambled ensembles (theorem in [71]) enter Theorem 4, and does it hold for displacement-scrambled ensembles?
* How is the adversary method set up for Theorem 3, and where does $\min\{G/2C, n/2\}$ come from?
* Which PRS construction with $\tilde O(G)$ gates is used, and is its displacement structure analyzable?

Paper: [arXiv:2310.19882](https://arxiv.org/abs/2310.19882)

---

## A single T-gate makes distribution learning hard (arXiv:2207.03140)

The paper by **Marcel Hinsche, Marios Ioannou, Alexander Nietner, Jonas Haferkamp, Yihui Quek, Dominik Hangleiter, Jean-Pierre Seifert, Jens Eisert, and Ryan Sweke** (FU Berlin, Maryland, TU Berlin; PRL 2023) characterizes the learnability of the output distributions $P_U(x) = \vert\langle x\vert U\vert 0^n\rangle\vert^2$ of local circuits from classical samples. Clifford distributions are efficiently learnable at any depth; a single $T$ gate makes learning an evaluator hard under LPN; generators are hard under PRF assumptions from depth $n^{\Omega(1)}$ on; and in the statistical query model, hardness begins at depth $\omega(\log n)$.

### Placement in the tables

* **Task type:** Identifying against a class with a promise (distributions of a circuit class); the output is a generator or an evaluator. The hardness is cryptographic as in the LWE rows, but on the classical side of the measurement.
* **Object:** classical distribution over $\{0,1\}^n$. **Access:** sample, classical bit strings; in the SQ model only expectation values up to tolerance $\tau = \Omega(1/\mathrm{poly})$.
* **Status:** Clifford 🟢 🟢 🟢 with $O(n)$ samples and Gaussian elimination; Clifford+$T$ 🟢 🔴 🟢 (samples polynomial, time LPN-hard); general 🟢 🔴 🟢 from depth $n^{\Omega(1)}$ (generator) and $\omega(\log n)$ (SQ).
* **Promise:** gate set and depth; nearest-neighbor gates in 1D.

### The problem

Quantum circuit Born machines (QCBMs) are meant to learn distributions that are classically hard to sample; the hope was a provable advantage for natural distributions. For Clifford circuits, simulability and learnability coincide; does this also hold for "slightly non-Clifford" circuits?

### Key results

* **Theorem 1.** $\mathcal{D}_{\mathrm{Cl}}$ is efficiently learnable at any depth (generator and evaluator): Clifford distributions are uniform on affine subspaces of $\mathbb{F}_2^n$, and $O(n)$ samples plus Gaussian elimination find the subspace with failure probability $e^{-\Omega(n)}$.
* **Theorem 2.** Under LPN, the output distributions of local Clifford circuits of depth $n^{\Omega(1)}$ with a single $T$ gate are not efficiently evaluator-learnable; with arbitrary connectivity already at depth $\Omega(1)$. The LPN noise is realized by a $T$ gate (Fig. 2); the same holds for Clifford circuits with depolarizing noise.
* **Corollary 1.** The same hardness for all local circuits of depth $n^{\Omega(1)}$.
* **Theorem 3.** Under classical-secure and standard-secure PRFs respectively, there is no efficient classical or quantum algorithm for generator learning at depth $n^{\Omega(1)}$ and any universal gate set; QCBM learners included.
* **Theorem 4 (SQ).** No query-efficient SQ learnability for $\mathcal{D}_{\mathrm{Cl}}$ from depth $\omega(\log n)$ on and for $\mathcal{D}_{\mathcal{G}}$ from depth $\omega(\log^k n)$ on, generator and evaluator alike; parities are SQ-hard, linear Clifford depth realizes them, and rescaling trades depth for complexity.

### Methodological approach

* All hardness results are embeddings of classically hard distributions (noisy parities, PRF outputs) into circuits; the circuit structure only determines which depth is needed.
* The sharp transition at a single $T$ gate contrasts with the smooth simulation complexity (exponential in the $T$ count); here learning and simulation separate.

### Significance and applications

* Output distributions of local circuits cannot justify a practical learning advantage of QCBMs over classical learners; new strategies for quantum advantages in learning are needed.
* The SQ result applies to all gradient-based trainers.

### Relation to this project

* The class is the classical marginal distribution of the states whose displacement spectra this project learns; the hardness with a single $T$ gate shows that even minimal magic builds a wall on the distribution side, while on the state side $t = O(\log n)$ is still learnable. Bell sampling sees more than the computational-basis distribution; this is the quantitative reason why two-copy access extends the instance ladder.
* LPN is the $\mathbb{F}_2$ counterpart of LWE; the construction "noise from a gate" is a recipe for building hard displacement instances from a Clifford scaffold plus a single non-Clifford element.
* The SQ model is the language for CNN decoders that see only statistics; Theorem 4 says from which depth on such decoders must fail.

### Limitations and open questions

* Evaluator hardness needs LPN, generator hardness PRFs; unconditional statements only in the SQ model.
* Depth $O(\log n)$ to $n^{\Omega(1)}$ without the SQ restriction is open; the authors name sample complexity and the average case as next questions (Nietner et al. answer the latter).
* Computational-basis distributions and fixed inputs only.

### Questions for further study

* How exactly does a single $T$ gate with $H$ conjugation realize Bernoulli noise at a constant rate, and can the rate be controlled?
* Which rescaling trades depth for complexity, and why is it limited to $n^{\Omega(1)}$?
* What do Bell samples on $\rho\otimes\rho^*$ look like for the state from Fig. 2, and is the support there sparse and findable despite LPN?

Paper: [arXiv:2207.03140](https://arxiv.org/abs/2207.03140)

---

## On the average-case complexity of learning output distributions of quantum circuits (arXiv:2305.05765)

The paper by **Alexander Nietner, Marios Ioannou, Ryan Sweke, Richard Kueng, Jens Eisert, Marcel Hinsche, and Jonas Haferkamp** (FU Berlin, Linz, Berkeley; Quantum 2025) moves the hardness of distribution learning from the worst case to the average case: for random brickwork circuits of depth $d$, learning an $\epsilon$-close generator from statistical queries is hard from $d = \Omega(\log n)$ on with constant probability over the instance ($2^{\Omega(d)}$ queries), at linear depth with probability $1 - O(2^{-n})$ ($\Omega(2^n)$ queries), and at infinite depth with probability $1 - 2^{-2^{\Omega(n)}}$ ($2^{2^{\Omega(n)}}$ queries). A by-product: the output distribution of a random circuit is, with probability $1 - O(2^{-n})$, a constant distance away from every fixed distribution, a variant of the conjecture of Aaronson and Chen.

### Placement in the tables

* **Task type:** Identifying against a class, in the average case over the class and with success probability $\beta$ over the instance; this is exactly open question (4) of the identifying table, answered for distributions.
* **Object:** classical distribution of a random brickwork circuit. **Access:** statistical queries with tolerance $\tau = \Omega(1/\mathrm{poly})$; the bounds carry over to probabilistic and quantum algorithms (Section F).
* **Status:** 🟢 🔴 🟢 in the SQ model: samples polynomial, queries exponential in $d$; the price is unconditional, with no cryptographic assumption.
* **Promise:** none about the instance except the depth; $\beta$ interpolates between the worst case ($\beta = 1$) and the average case.

### The problem

Worst-case hardness says nothing about heuristic learners that run on typical instances. Is learning output distributions hard for a random circuit, and from which depth on? And how does the hardness depend on the required success probability $\beta$?

### Key results

* **Informal Theorem 1.** (1) $d\to\infty$: $q = 2^{2^{\Omega(n)}}$ queries for every $\beta > 2\exp(-2^{n-2}/9\pi^3)$ (Theorem 2). (2) Linear depth $d\geq d' = O(n)$: $q = \Omega(2^n)$ for $\beta > 3200\cdot 2^{-n}$ (Theorem 6). (3) Sublinear: for $c\log n\leq d\leq c(n+\log n)$ with $c = 1/\log(5/4)$, $q = 2^{\Omega(d)} = 2^{\omega(\log n)}$ for $\beta > 4/5 + \epsilon + \tau$ (Theorem 12).
* **Informal Theorem 2 / Theorem 36.** For $d\geq d' = O(n)$, $\epsilon\leq 1/225$, and every distribution $Q$: $\Pr_U[d_{\mathrm{TV}}(P_U, Q) > \epsilon]\geq 1 - O(2^{-n})$.
* **SQ upper bound.** An $\epsilon$-net over the distributions gives $q\leq\exp[O(nd\log(nd/\epsilon))]$ (tournament); at linear depth $\exp[O(n^2\log n)]$ against $\Omega(2^n)$, and the gap remains open.

### Methodological approach

* SQ dimension and anticoncentration: from logarithmic depth on, the distributions of random circuits are pairwise almost uncorrelated (approximate designs), so every query rules out only few instances; the depth dependence comes from the design convergence rate.
* The measure over instances is the circuit distribution itself, not uniform over distributions; this is the natural choice for QCBM analyses.
* SQ learners include all gradient-based QCBM trainers (parameter shift, SPSA), so the bound applies to practice.

### Significance and applications

* The QCBM counterpart of average-case hardness for deep neural networks; heuristic learners cannot be efficient on typical instances from logarithmic depth on.
* The "far from uniform" property supports heavy output generation as a proof of advantage.

### Relation to this project

* Average-case hardness is the question this project leaves open for displacement spectra: LWE gives worst-case hardness via a reduction, and this paper shows what unconditional average-case bounds look like in the SQ model; for a CNN decoder that sees only Bell statistics, the SQ model is the right abstraction.
* The parameters $(d, \beta, \tau, \epsilon)$ are a four-dimensional instance ladder; the separation "constant probability from $\log n$ on, exponentially close to one from linear depth on" is a pattern for the rungs of this project's ladder.
* The design property from logarithmic depth on is the same one that makes displacement spectra flat: from this depth on there is typically no sparse support.

### Limitations and open questions

* SQ only; sample complexity and hardness for general learners with single samples are open.
* Gap between $\Omega(2^n)$ and $\exp[O(n^2\log n)]$ at linear depth.
* Other families of distributions (free fermions) and the question whether simulation hardness implies learning hardness are open.

### Questions for further study

* How exactly is the SQ dimension derived from the design convergence of the brickwork ensemble, and where does $c = 1/\log(5/4)$ come from?
* How does the SQ bound carry over to quantum algorithms with single samples (Section F), and what is lost in the process?
* Does an analogous average-case bound hold for Bell statistics of random circuits, i.e. for learning the displacement spectrum from two-copy samples?

Paper: [arXiv:2305.05765](https://arxiv.org/abs/2305.05765)

<br>

# Estimating

**Estimating** (observables are *input*). Given: copies of $\rho$ and a list of $M$ observables, explicit or implicit. Returned: the $M$ expectation values to precision $\epsilon$. Like a panel of predefined SNPs: the loci are fixed in advance, only their values are unknown. Full tomography is the limit $M = d^2$, sequencing the whole genome. The list can be explicit and polynomial (a dictionary), implicit and exponential (all Paulis), drawn from a distribution (PAC learning and average-case prediction), or revealed one observable at a time (online learning). The task type is the same in each case; the budgets differ.

**What is known.** This is the best-charted column of the field, almost entirely on the sample side. Full tomography costs $\Theta(d^2/\epsilon^2)$ copies with entangled measurements and $\Theta(d^3/\epsilon^2)$ with single copies, adaptivity included. Shadow tomography answers $M$ questions with $\mathrm{poly}(\log M, n, 1/\epsilon)$ copies, since 2026 at the classical adaptive-data-analysis rates $O(\log M\sqrt{\log d}/\epsilon^3)$ and $O(\sqrt M/\epsilon^2)$ (Chen, O'Donnell, Pelecanos, Wright), down from $\tilde O(\log^2 M \cdot \log d/\epsilon^4)$ (Bădescu, O'Donnell 2021); classical shadows do it with single-copy random measurements at a cost set by the shadow norm, cheap for local observables and exponential for global ones. Two-copy memory closes that gap: $\Theta(n)$ copies for all Pauli expectations against $2^{\Omega(n)}$ without memory, the strongest proven separation in the field, demonstrated in hardware. Conjugate pairs deliver the clean squared spectrum at constant memory. Under query access the precision rate improves from $1/\epsilon^2$ to $1/\epsilon$, for observables, for unitaries, and for Hamiltonian couplings.

**Efficiency status.** Copies: 🟢 everywhere except full tomography and its low-rank and unitary variants, which stay exponential in $n$ by dimension counting. Time and memory: 🔴 for general shadow tomography, because its hypothesis is a $2^n\times 2^n$ matrix, and likewise for PAC and online learning of states. 🟢 🟢 🟢 exactly where a promise or a resource is named: locality (classical shadows), two-copy memory (all Paulis), a dictionary (conjugate pairs), a gapped phase (ground-state prediction), locality of the Hamiltonian (Gibbs and real-time learning, time-efficient at any constant temperature only since 2024).

**What is open.**
* (1) The precision exponent. Shadow tomography reached $O(\log M\sqrt{\log d}/\epsilon^3)$ in 2026 (Chen, O'Donnell, Pelecanos, Wright), the classical adaptive-data-analysis rate, with a lower bound of $\Omega(\log M\sqrt{\log d}/(\epsilon^2\log(1/\epsilon)))$ and evidence that $1/\epsilon^3$ is tight (Lyu, Talwar 2025); the dimension-free $O(\sqrt M/\epsilon^2)$ is optimal. For Pauli observables nothing better than $1/\epsilon^4$ is known, and any improvement needs highly entangled measurements (Chen, Gong, Ye 2024).
* (2) Memory between zero and two. The sample complexity interpolates smoothly with $k$ qubits of memory (Chen, Cotler, Huang, Li), but no protocol family is known that uses a fixed small memory budget for structured observable sets.
* (3) Triply efficient schemes beyond Paulis and local fermionic observables, and whether a learned decoder can replace the graph-coloring step on which the current schemes rely.
* (4) Noise. The two-copy separations are stated for ideal Bell measurements; robustness to preparation, crosstalk, and readout errors is the practically decisive axis, and the first empirical evaluation of a two-copy triply efficient scheme dates from 2025.

| Protocol or class | Object | Task type: given → returned | Copies or queries (access) | Time | Memory | Status & Condition |
| --- | --- | --- | --- | --- | --- | --- |
| **Full QST** (entangled: O'Donnell, Wright 2016; Haah, Harrow, Ji, Wu, Yu 2017) | State | Estimating, $M = d^2$: nothing withheld → density matrix $\rho$ | Sample: $\Theta(d^2/\epsilon^2)$ entangled up to $\log d$, $O(rd/\epsilon^2)$ at rank $r$; $\Theta(d^3/\epsilon^2)$ single-copy | $\mathrm{poly}(d)$ | $d^2$ entries | 🔴 🔴 🔴; baseline; by Keyl's measurement after weak Schur sampling, which also gives the top-$k$ eigenvalues from $O(k^2/\epsilon^2)$ copies, independent of $d$ |
| **Shadow tomography, general** (Aaronson 2018; Bădescu–O'Donnell 2021; Chen, O'Donnell, Pelecanos, Wright 2026) | State | Estimating: list of $M$ observables → $M$ values $\mathrm{Tr}(O_i\rho)$, online against adaptively chosen observables | Sample: $\mathrm{poly}(\log M, n, 1/\epsilon)$; since 2026 the classical adaptive-data-analysis rates $O(\log M\sqrt{n}/\epsilon^3)$ and $O(\sqrt M/\epsilon^2)$, down from $\tilde O(\log^2 M\cdot n/\epsilon^4)$ | $\exp(n)$: the MMW update touches a $2^n \times 2^n$ hypothesis | $\exp(n)$: that hypothesis | 🟢 🔴 🔴; hypothesis too large |
| **PAC learning of states** (Aaronson 2007) | State | Estimating, average case: observables drawn from a distribution → predictions correct for most of them | Sample: $O(n)$ | No efficient learner in general; efficient for stabilizer states (Rocchetto 2018), but LPN-hard with classification noise (Gollakota, Liang 2022, searching table) | $d \times d$ hypothesis in general, poly for structured classes | 🟢 🔴 🔴; generic |
| **Classical shadows, $k$-local Paulis** | State | Estimating: list of $M$ local observables, chosen after measurement → $M$ values | Sample: $O(\log M \cdot 3^k/\epsilon^2)$ | poly | $O(Nn)$, one stabilizer product per snapshot | 🟢 🟢 🟢; locality promise |
| **Classical shadows in hardware** (Zhang, Sun, Fang, Zhang, Yuan, Lu, PRL 2021) | State, a four-qubit photonic GHZ state | Estimating: 50 local Paulis, $\langle H\rangle$, $\langle H^2\rangle$, subsystem purities, PT-moments → values, compared across importance sampling, grouping, uniform, biased, and derandomized shadows | Sample: $N_s \leq 2000$ single-copy local-Clifford measurements | poly | poly | 🟢 🟢 🟢; locality; derandomized shadows win when many large-support terms are present |
| **Median-of-means constants** (Fu, Koh, Goh, Kong 2024) | State | Estimating: the same functions, with Minsker's optimal constants and a U-statistic median → values | Sample: the constant $C$ in $\Pr[\vert\hat\mu-\mu\vert \geq C\sigma\sqrt{t/N}] \leq 2e^{-t}$ drops from about $8$ to $\sqrt\pi$ (median of means) or $\sqrt2$ (U-statistic); shots for $\epsilon = 0.1$ from $58\cdot 10^3$ to $38\cdot 10^3$ | poly, incomplete U-statistics via random or cyclic designs | poly | 🟢 🟢 🟢; post-processing only; the plain mean is best in practice for Pauli measurements, the modified estimators for Clifford measurements |
| **All $4^n$ Pauli observables, two-copy** (King, Gosset, Kothari, Babbush 2024) | State | Estimating: all $4^n$ Paulis → any value on demand | Sample: $O(n\log(n/\epsilon)/\epsilon^4)$, two copies at a time; $2^{\Omega(n)}$ with single copies (Chen, Cotler, Huang, Li 2021) | $\mathrm{poly}(4^n, 1/\epsilon)$ to learn, i.e. $\mathrm{poly}(\vert S\vert)$, the paper's definition of time efficiency; $\mathrm{poly}(n)$ per query from the compressed representation at constant $\epsilon$ (Cor. 12) | $\mathrm{poly}(n)$, the compressed representation | 🟢 🟢 🟢 in the paper's sense; two-copy memory; triply efficient learning of an arbitrary subset of Paulis in time $\mathrm{poly}(\vert S\vert, n)$ is open (Conjecture 13) |
| **Displacement amplitudes over a dictionary, conjugate pairs** (King, Wan, McClean 2024) | State | Estimating: list of $M$ candidate $(q,p)$ → magnitudes of $y_{q,p}$ from Bell sampling, signs by the adaptive eigenprobe | Sample on $\rho\otimes\rho^*$: $O(\log d/\epsilon^4)$ for all magnitudes, $N = O(g^{-2}\log(M/\delta))$ for the top-$k$ over the list; $\Omega(\sqrt d)$ without the conjugate copy | $\mathrm{poly}(M)$ character means on one Bell record | $O(M)$ values | 🟢 🟢 🟢; conjugate access plus dictionary promise, *Regime 1* |
| **Low-rank tomography, compressed sensing** (Gross, Liu, Flammia, Becker, Eisert 2010) | State | Estimating, $M = d^2$ with a rank-$r$ promise → the state | Sample: $O(rd\log^2 d)$ Pauli expectation values instead of $d^2$ | $\mathrm{poly}(d)$, nuclear-norm minimization | $O(rd)$ | 🔴 🔴 🔴 in $n$; the rank promise cuts $d^2$ to $rd$ |
| **Spectrum estimation by Schur sampling** (Keyl, Werner 2001; O'Donnell, Wright 2015) | State | Estimating: the eigenvalues of $\rho$ → the spectrum | Sample: $O(d^2/\epsilon^2)$ copies measured collectively, quantum memory $k = N$ | $\mathrm{poly}(d)$ | $O(d)$ | 🔴 🔴 🟢 in $n$; the far end of the memory axis, all copies entangled at once |
| **Online learning of quantum states** (Aaronson, Chen, Hazan, Kale, Nayak 2018) | State | Estimating, sequential: observables arrive one at a time → a prediction each, regret $O(\sqrt{Tn})$, at most $O(n/\epsilon^2)$ mistakes | Sample-free: the true value $\mathrm{Tr}(E_t\rho)$ is fed back after each round | $\exp(n)$: MMW over a $2^n\times 2^n$ hypothesis | $\exp(n)$ | 🟢 🔴 🔴; hypothesis too large, the online cousin of shadow tomography |
| **Classical shadows, other ensembles** (fermionic and matchgate: Zhao, Rubin, Miyake 2021; Wan, Huggins, Lee, Babbush 2023; unified with a gate-optimal sampling scheme: Heyraud, Chomet, Tilly 2024; shallow and locally scrambled: Bertoni et al. 2024; Hu, Choi, You 2023; derandomized: Huang, Kueng, Preskill 2021; symmetric spaces $G/K$: Chang, Krumtünger, Larocca, West 2026) | State | Estimating: fermionic observables, or local observables under shallow randomization → values | Sample: poly, the shadow norm of the chosen ensemble decides the constant; the first three moments of the ensemble decide the protocol, so ensembles with equal moments are interchangeable | poly | poly | 🟢 🟢 🟢; the promise moves with the ensemble |
| **Classical shadows, locally entangled bases** (Ippoliti 2024) | State | Estimating: Paulis compatible with a dimer covering → values; Bell measurements on qubit pairs *within* one copy, quantum memory still one | Sample: shadow norm $3^{k/2}$ instead of $3^k$, $(3/2)^k$ with $n$-qubit GHZ bases, optimal among stabilizer measurements; incompatible Paulis unlearnable; a deformed family is tomographically complete with $\sim 4^{k \bmod 2}\, 2^k$ | poly | poly | 🟢 🟢 🟢; compatibility with the covering, a promise on the observables, not on the state |
| **Classical shadows on qudits** (Mao, Yi, Zhu 2024; qudit Clifford shadows for off-diagonal elements: King, Wan, McClean 2024) | State on $n$ qudits, $d$ an odd prime | Estimating: fidelities and Weyl observables → values | Sample: shadow norm $\leq (2d-3)\Vert O\Vert_2^2 + 2\Vert O\Vert_\infty^2$ under global Cliffords, an $O(d)$ overhead over qubits independent of $n$ although the qudit Clifford group is only a 2-design; one T gate after the Clifford removes the overhead; $(d+1)^m$ for $m$-local Weyl operators under local Cliffords | poly, simulation $O((n+t)^3 + t d^{t+1})$ | poly | 🟢 🟢 🟢; bounded Hilbert–Schmidt norm; a displacement operator on a single qudit carries the factor $d+1$, the single-copy wall of the conjugate-pair row |
| **Ground-state properties across a phase from shadows** (Huang, Kueng, Torlai, Albert, Preskill 2022; Lewis et al. 2024; Onorati, Rouzé, França, Watson 2023) | Family of states $\rho(x)$ | Estimating, generalization: shadows of $\rho(x)$ at training parameters $x$ → $\mathrm{Tr}(O\rho(x'))$ at new $x'$ in the same phase | Sample: $\mathrm{poly}(n)$ training states, $O(\log n)$ in the improved version | poly | poly | 🟢 🟢 🟢; gapped phase plus locality, the provable machine-learned decoder |
| **Hamiltonian coefficients from Gibbs states, known terms** (Anshu, Arunachalam, Kuwahara, Soleimanifar 2021) | Hamiltonian, from copies of its Gibbs state | Estimating: known interaction terms → their coefficients | Sample: $\mathrm{poly}(n, 1/\epsilon)$ copies of the Gibbs state | Not efficient in the original algorithm; polynomial at high temperature (Haah, Kothari, Tang 2022) and at any constant temperature (Bakshi, Liu, Moitra, Tang 2024) | poly | 🟢 🔴→🟢 🟢; the time budget was the open half for three years |
| **Low-degree quantum objects** (Arunachalam, Dutt, Escudero Gutiérrez, Palazuelos 2024; qudits and cyclic groups via a dimension-free Remez inequality: Klein, Slote, Volberg, Zhang 2023) | Observable, unitary, channel | Estimating: Pauli degree at most $\ell$ → all $n^{O(\ell)}$ coefficients | Channels and unitaries: query, $\exp(\tilde O(\ell^2 + \ell\log 1/\epsilon))$ uses independent of $n$; observables: sample, $O(\log n)$ random product-state inputs for constant degree, via noncommutative Bohnenblust–Hille inequalities; on $K$-level qudits in the Heisenberg–Weyl basis the same with constant $(\log K)^{O(\ell^2)}$ | poly | poly | 🟢 🟢 🟢; low-degree promise, a dictionary of size $n^{O(\ell)}$ |
| **Predicting arbitrary quantum processes** (Huang, Chen, Preskill 2023) | Channel | Estimating, average case: unknown channel $\mathcal{E}$, inputs from a distribution → $\mathrm{Tr}(O\,\mathcal{E}(\rho))$ for most inputs | Sample: $\mathrm{poly}(n)$ uses of the channel on random inputs | poly | poly | 🟢 🟢 🟢; average case plus locality of $O$ |
| **Pauli channel eigenvalues, entanglement-assisted** (Chen, Zhou, Seif, Jiang 2022) | Channel | Estimating: all $4^n$ Pauli eigenvalues of a channel → any eigenvalue on demand | Sample on the Choi state: channel applied once per shot to half of a Bell pair, $O(n/\epsilon^2)$ with the entangled ancilla as quantum memory, $2^{\Omega(n)}$ without | poly per eigenvalue, from one Bell record | poly, the Bell record | 🟢 🟢 🟢 with ancilla memory; the channel version of the two-copy separation |
| **Heisenberg–Weyl transfer matrix, limited parallel access** (Subramanian, Kwon, Jiang 2026) | Channel on $m$ qudits ($d$ prime) or $m$ bosonic modes | Estimating: a bounded query set of entries $\mathrm{Tr}[D(q_o,p_o)\mathcal{E}(D(q_i,p_i))]/d^m$ → their magnitudes | Sample on the Choi state with $c$ parallel channel uses per round: $O(\log(M/\delta)/\epsilon^4)$ with one use of $\mathcal{E}\otimes\mathcal{E}^*$, tight in $\epsilon$; without the conjugate channel $\Omega(d^{m+m'}/(c^2\epsilon^2))$ for every $c < d$, efficient only at $c = d$ with $\epsilon^{-2d}$; bosonic channels exponential for all $c = O(1/\epsilon)$ | poly | poly | 🟢 🟢 🟢 with conjugate access; the channel version of the conjugate-pair row and of the $d$-copy hierarchy for qudits |
| **Amplitude estimation** | State, through its preparation circuit | Estimating: one observable → its value | Query: $O(1/\epsilon)$ calls to the preparation circuit | poly | poly | 🟢 🟢 🟢; Heisenberg rate |
| **Heisenberg-limited Hamiltonian learning** (Huang et al. PRL 2023) | Hamiltonian | Estimating: known interaction graph → the coupling values | Query to the dynamics $e^{-iHt}$: total evolution time $T \sim 1/\epsilon$ | poly | poly | 🟢 🟢 🟢; locality promise plus queries to the dynamics |
| **Pauli channel estimation, sequence-based** (Flammia, Wallman 2020; Harper, Flammia, Wallman 2020) | Channel | Estimating: Pauli eigenvalues of a noise channel under a sparse or local model → values | Query: repeated application of the channel in sequences of varying length, interleaved with random Pauli twirls | poly for sparse or local noise | poly | 🟢 🟢 🟢; sparse or local noise model; sequential use buys robustness against state-preparation and measurement errors |
| **Unitary estimation in diamond distance** (Haah, Kothari, O'Donnell, Tang 2023) | Unitary | Estimating, $M = d^2$: unknown unitary → $U$ to error $\epsilon$ | Query: $\Theta(d^2/\epsilon)$ uses of $U$, the Heisenberg rate at tomography scale | $\mathrm{poly}(d)$ | $d^2$ | 🔴 🔴 🔴 in $n$; queries buy $1/\epsilon$, not the dimension |

## Estimating protocols

Observables are the input. The baseline is full tomography; every protocol below exists to escape its scaling, by changing the question (shadows), by adding a resource (two-copy memory, queries), or by naming a promise (locality, a phase, a Hamiltonian family).

## Full QST: the exponential baseline

Reconstructs all $d^2$ parameters from an informationally complete measurement set (DV: all $3^n$ Pauli bases or a single SIC-POVM; CV: homodyne scan and inverse Radon transform to the Wigner function). Cost $\Theta(d^2/\epsilon^2) = \Theta(4^n/\epsilon^2)$ even with entangled measurements. Everything else exists to escape this scaling.

* **O'Donnell, Wright (STOC 2016) / Haah, Harrow, Ji, Wu, Yu (IEEE Trans. Inf. Theory 2017):** $\Theta(d^2/\epsilon^2)$ optimal entangled tomography, $O(rd/\epsilon^2)$ at rank $r$; O'Donnell–Wright by Keyl's measurement after weak Schur sampling, Haah et al. by a different measurement and with the matching lower bound up to $\log$. O'Donnell–Wright add quantum PCA from $O(kd/\epsilon^2)$ copies and the top-$k$ eigenvalues from $O(k^2/\epsilon^2)$, independent of $d$.
* **Chen et al. (2022):** $\Theta(d^3/\epsilon^2)$ single-copy lower bound, proves the gap to entangled measurements.
* **Keyl, Werner (2001) / O'Donnell, Wright (2015):** Spectrum estimation and spectrum testing by Schur sampling, the collective-measurement end of the memory axis.
* **Lowe, Nayak (2022) / Chen, Huang, Li, Liu, Sellke (FOCS 2023):** $\Omega(d^3/\epsilon^2)$ for single-copy tomography, first nonadaptive, then even adaptive: adaptivity does not help for full tomography.
* **Haah, Kothari, O'Donnell, Tang (FOCS 2023):** Unitary estimation with $\Theta(d^2/\epsilon)$ queries in diamond distance, Heisenberg rate at tomography scale.

**Structured escapes before shadows.** Two routes beat $d^2$ by *assuming* structure rather than by changing the question: **compressed-sensing tomography** (Gross, Liu, Flammia, Becker, Eisert, PRL 2010) recovers a rank-$r$ state from $O(r\,d\log^2 d)$ random Pauli expectation values via nuclear-norm minimization, and **MPS tomography** (Cramer et al., Nat. Commun. 2010) reconstructs 1D states of bounded bond dimension from local reduced density matrices in $\mathrm{poly}(n)$. Both are the tomographic analogue of the "low rank ⇒ easy" theme that also drives dequantization arguments: the exponential baseline is a worst-case statement over *all* states.

## Shadow tomography and classical shadows (observables as input)

* **Shadow tomography (Aaronson):** $M$ observables to $\pm\epsilon$ with $\mathrm{poly}(\log M, n, 1/\epsilon)$ copies, $M$ may be exponential. The engine is the gentle-measurement lemma: Near-deterministic estimates damage the state only by $O(\sqrt{\epsilon})$, so the same copies answer many questions. Sample-efficient, but compute- and memory-intensive.
* **Classical shadows (Huang–Kueng–Preskill):** "Randomize first, ask later." Per copy, draw a random $U$ (Pauli basis per qubit or Clifford), measure, store the snapshot:

$$\hat\rho = \mathcal{M}^{-1}\big(U^\dagger|b\rangle\langle b|U\big), \qquad \mathbb{E}[\hat\rho] = \rho$$

  Afterwards estimate arbitrary observables via median-of-means: $O(\log M \cdot 3^k/\epsilon^2)$ shots for $k$-local Paulis. Single-copy, NISQ-ready, the workhorse of practice. The gap: *global* observables ($k \sim n$) cost $3^n$ shots. Exactly this gap is closed by two-copy measurements.
* **Triple efficiency:** Sample *and* time efficiency with $O(1)$-copy quantum memory.

Literature:
* **Aaronson (STOC 2018):** Shadow tomography via gentle measurements, $\tilde{O}(\log^4 M)$ copies.
* **Huang, Kueng, Preskill (Nat. Phys. 2020):** Classical shadows.
* **King, Gosset, Kothari, Babbush (2024):** Triply efficient shadow tomography for local fermionic and Pauli observables.
* **Aaronson, Rothblum (STOC 2019):** Gentle measurement and differential privacy are the same lemma; the cleanest account of why shadow tomography is sample-efficient.
* **Aaronson, Chen, Hazan, Kale, Nayak (NeurIPS 2018):** Online learning of quantum states, regret $O(\sqrt{Tn})$, mistake bound $O(n/\epsilon^2)$, MMW inside.
* **Zhao, Rubin, Miyake (PRL 2021) / Wan, Huggins, Lee, Babbush (2023):** Fermionic and matchgate shadows. **Bertoni et al. (PRL 2024) / Hu, Choi, You (PRL 2023):** shallow and locally scrambled shadows.
* **Volberg, Zhang (2023) / Arunachalam, Dutt, Escudero Gutiérrez (2024):** Noncommutative Bohnenblust–Hille inequality and learning of low-degree quantum objects: a polynomial dictionary in disguise.
* **Chen, O'Donnell, Pelecanos, Wright (2026):** Online shadow tomography at the classical rates, $O(\log M\sqrt{\log d}/\epsilon^3)$ and $O(\sqrt M/\epsilon^2)$, via the excitation (quantum Efron–Stein) decomposition as a measure of measurement damage.
* **Klein, Slote, Volberg, Zhang (2023):** A dimension-free Remez inequality gives Bohnenblust–Hille inequalities over cyclic groups and hence $O(\log n)$-sample low-degree learning on $K$-level qudits in the Heisenberg–Weyl basis.
* **Zhang, Sun, Fang, Zhang, Yuan, Lu (PRL 2021):** Classical shadows on a four-qubit photonic processor; uniform, biased, and derandomized shadows against importance sampling and grouping, plus purities and PT-moments from U-statistics.
* **Fu, Koh, Goh, Kong (2024):** Minsker's optimal median-of-means constants and a U-statistic median for classical shadows; the estimator should match the measurement ensemble.
* **Ippoliti (Quantum 2024):** Bell and locally entangled measurement bases within one copy: $3^{k/2}$ for compatible Paulis, $(3/2)^k$ with GHZ bases, at the price of unlearnable operators.
* **Heyraud, Chomet, Tilly (2024):** Clifford-3-cubatures; the $SO(2n)$ matchgate ensemble and all discrete matchgate ensembles in the literature give equivalent shadows, with a gate-optimal sampling scheme.
* **Mao, Yi, Zhu (2024):** Qudit shadows from the Clifford group cost only an $O(d)$ overhead independent of $n$; a single T gate removes it.
* **Chang, Krumtünger, Larocca, West (2026):** Shadows over compact symmetric spaces $G/K$: the channel is a convex combination of the parent-group channel and a dephasing channel.

**The variance bound that decides the ensemble.** The shot count of classical shadows is governed by the **shadow norm** $\|O\|_{\mathrm{shadow}}^2$, which depends on the unitary ensemble: for random single-qubit Pauli measurements, $\|P\|_{\mathrm{shadow}}^2 = 3^{k}$ for a $k$-local Pauli $P$ (local observables cheap, global ones exponential); for random $n$-qubit Cliffords, $\|O\|_{\mathrm{shadow}}^2 \leq 3\,\mathrm{Tr}(O^2)$, so *fidelity* with any pure state costs $O(1/\epsilon^2)$ shots independent of $n$, while a global Pauli still costs $\Theta(2^n)$. Neither ensemble handles global Paulis; that is the gap two-copy Bell measurements close. Two follow-ups worth knowing: **derandomization** (Huang, Kueng, Preskill, PRL 2021) picks the measurement bases greedily against a fixed observable list and beats random shadows by constant factors in practice; **Bădescu–O'Donnell** (STOC 2021) brought shadow tomography proper down to $\tilde O(\log^2 M\cdot\log d/\epsilon^4)$ copies. Chen, O'Donnell, Pelecanos, Wright (2026) then reached the classical rates $O(\log M\sqrt{\log d}/\epsilon^3)$ and $O(\sqrt M/\epsilon^2)$, online, by tracking measurement damage as the energy of an excitation decomposition.

## Continuous-variable systems: CV shadows and Gaussian learning

The displacement operators of this project are the finite Weyl–Heisenberg group; the continuous-variable Weyl group is their infinite-dimensional parent, and the characteristic function $\chi(\alpha) = \mathrm{Tr}(D(\alpha)\rho)$ is the CV displacement spectrum. Learning it is the CV version of the searching and estimating rows.

* **Homodyne tomography** (Vogel, Risken 1989; Smithey et al. 1993): a quadrature scan and an inverse Radon transform reconstruct the Wigner function, the CV baseline, with no finite dimension to count against; energy bounds take the place of $d$.
* **CV classical shadows** (Becker, Datta, Lami, Rouzé 2024; Gandhari et al. 2024): randomized Gaussian measurements with rigorous error bounds under an energy or photon-number constraint; the shadow-norm role is played by the energy.
* **Gaussian and near-Gaussian state learning** (Mele et al. 2024; Bittel et al. 2024): bosonic Gaussian states are learned from their covariance matrix and displacement vector in polynomial time in the number of modes; $t$ non-Gaussian gates cost $2^t$, the bosonic mirror of the magic dial. Fermionic Gaussian states behave the same way (Aaronson, Grewal 2023; Mele, Herasymenko 2024).
* **The bridge to this project.** Heterodyne outcomes sample the Husimi function, whose Fourier transform is the characteristic function; the CV analogue of the Bell record is therefore a heterodyne record, and the CV analogue of the search for a sparse displacement support is the search for a few dominant $\alpha$ in $\chi(\alpha)$. Whether an LWE-type wall exists there is as open as the cyclic-qudit question in the searching table.

## Estimating processes: Hamiltonian coefficients, channels, unitaries

Coupling values of Hamiltonians from Gibbs states or real-time dynamics, up to the Heisenberg limit; Pauli noise in channels; predictions for processes.

The estimating tasks whose object is a process. The object axis is defined in the appendix under "What is learned"; the structure of a Hamiltonian with unknown geometry is searching and sits in the structure-learning protocols, circuit descriptions under a depth promise are identifying and sit in the promise catalogue. On access: Gibbs-state learning is sample access to a state, entanglement-assisted channel learning is sample access to the Choi state, Heisenberg-limited and sequence-based protocols are query access.

* **Flammia, Wallman (TQC 2020):** Efficient Pauli channel estimation.
* **Anshu et al. (Nat. Phys. 2021) / Haah et al. (FOCS 2022):** Optimal sample complexity for Gibbs-state Hamiltonian learning.
* **Huang et al. (PRL 2023):** Heisenberg-limited Hamiltonian learning from real-time evolution.
* **Bakshi, Liu, Moitra, Tang (STOC 2024) / Rouzé, França (Quantum 2024):** Gibbs-state Hamiltonian learning at any constant temperature in polynomial time; few-copy variants.
* **Dutkiewicz, O'Brien, Schuster (2024) / Gu, Cincio, Coles (Nat. Commun. 2024) / Li, Zou, Tong (PRL 2024) / Möbus et al. (2023):** Heisenberg-limited learning needs control; practical protocols; bosons; dissipation-enabled learning.
* **Harper, Flammia, Wallman (Nat. Phys. 2020) / Chen, Zhou, Seif, Jiang (PRA 2022) / Caro (2024):** Pauli-noise learning in practice, the entangled-ancilla separation, the Pauli transfer matrix as the channel analogue of the Pauli spectrum.
* **Chung, Lin (2021) / Huang, Chen, Preskill (PRX Quantum 2023):** PAC learning of channels; predicting arbitrary processes on average with polynomial data.
* **Subramanian, Kwon, Jiang (2026):** Heisenberg–Weyl transfer matrices of qudit and bosonic channels under $c$-copy parallel access: efficient with the conjugate channel $\mathcal{E}\otimes\mathcal{E}^*$ at a tight $\epsilon^{-4}$, exponential for $c < d$ without it, a master lower bound for all $c$-copy protocols.

**Two practical anchors.** *Heisenberg limit* means total evolution time $T \sim 1/\epsilon$ for precision $\epsilon$ on a coupling, versus the standard quantum limit $T \sim 1/\epsilon^2$ of incoherent repetition; the PRL 2023 protocol reaches it with product-state inputs plus a decoupling pulse sequence, no entangled probes. On the noise side, the field-standard protocols are **randomized benchmarking** (Emerson et al. 2005; Magesan et al. 2011), which extracts an average gate fidelity from the exponential decay of survival probability under random Cliffords, and **gate set tomography** (Blume-Kohout et al. 2013; Nielsen et al. 2021), the self-consistent full characterization; Flammia–Wallman's Pauli channel estimation is the sparse, scalable middle ground and the one that maps onto the noise-learning transfer named in the positioning section.

<br>

# Estimating (Papers)

Summaries of the key papers on the task type **estimating**: the observables are the input. Given are copies of a state, applications of a channel or a dynamics, together with a list of $M$ observables, explicit or implicit, or a distribution from which they are drawn. Returned are the $M$ expectation values up to $\epsilon$. The list can be polynomial and explicit (a dictionary), implicit and exponential (all Paulis), drawn from a distribution (PAC), or sequential (online). The task type stays the same; the budgets change.

Every summary follows the same structure as in the searching section: placement in the tables, problem, key results, method, significance, relation to this project, limitations and open questions, questions for further study. The status glyphs read in the order copies · time · memory.

## Overview

| Paper | Object | What is estimated | Access | Cost | Status | Promise |
| --- | --- | --- | --- | --- | --- | --- |
| Aaronson 2018 | State | $M$ two-outcome measurements, $M$ and $D$ exponential | Sample, entangled measurements across all copies | $\tilde O(\log^4 M \cdot \log D/\epsilon^4)$ copies | 🟢 🔴 🔴 | none; the hypothesis is a $D\times D$ matrix |
| Aaronson 2007 | State | $\mathrm{Tr}(E\rho)$ for most $E \sim \mathcal{D}$ | Sample, training measurements from $\mathcal{D}$ | $m = \tilde O(n/(\gamma^4\epsilon^4))$ training examples (Thm. 1.1), $\tilde O(n/(\epsilon\gamma^2))$ with a factor $\log^2 n$ (Thm. 1.2) | 🟢 🔴 🔴 | future resembles the past: $E$ i.i.d. from $\mathcal{D}$ |
| Aaronson, Chen, Hazan, Kale, Nayak 2018 | State | $\mathrm{Tr}(E_t\rho)$ for adversarially chosen $E_t$, round by round | sample-free, after feedback $b_t$ | $O(n/\epsilon^2)$ mistakes, regret $O(\sqrt{Tn})$ | 🟢 🔴 🔴 | none; MMW over a $2^n\times 2^n$ hypothesis |
| Bădescu, O'Donnell 2021 | State | threshold search, shadow tomography, hypothesis selection | Sample, unentangled copies | $O(\log^2 m/\epsilon^2)$ for threshold search, $\tilde O(\log^2 m\cdot\log d/\epsilon^4)$ for shadow tomography | 🟢 🔴 🔴 | none |
| Chen, O'Donnell, Pelecanos, Wright 2026 | State | online shadow tomography | Sample, measurement of lifted observables across $n$ copies | $O(\log m\sqrt{\log d}/\epsilon^3)$ or $O(\sqrt m/\epsilon^2)$, the classical rates | 🟢 🔴 🔴 | none |
| Huang, Kueng, Preskill 2020 | State | $M$ linear functions, chosen after the measurement | Sample, single copies, random Cliffords or Paulis | $O(\log M\cdot\max_i\Vert O_i\Vert^2_{\mathrm{shadow}}/\epsilon^2)$ | 🟢 🟢 🟢 | locality or bounded Hilbert–Schmidt norm |
| Zhang, Sun, Fang, Zhang, Yuan, Lu 2021 | State, 4 photonic qubits | local Paulis, $\langle H\rangle$, $\langle H^2\rangle$, purities, PT moments | Sample, single copies, local Cliffords in hardware | $N_s \leq 2000$ measurements | 🟢 🟢 🟢 | locality; derandomized bases |
| Fu, Koh, Goh, Kong 2024 | State | the same functions, with tighter median-of-means constants | Sample, single copies | constant $C$ from about $8$ to $\sqrt\pi$ and $\sqrt2$ respectively | 🟢 🟢 🟢 | none; pure post-processing |
| Hu, Choi, You 2023 | State | fidelities and Paulis after locally scrambled dynamics of finite depth | Sample, single copies, circuit or Hamiltonian evolution | shadow norm from the entanglement feature | 🟢 🟢 🟢 | local scrambling, $P(U) = P(UV) = P(VU)$ |
| Ippoliti 2024 | State | Paulis compatible with the dimer covering | Sample, single copies, Bell measurement *within* one copy | $3^{k/2}$ instead of $3^k$, $(3/2)^k$ with GHZ bases | 🟢 🟢 🟢 | compatibility with the dimer covering |
| Wan, Huggins, Lee, Babbush 2023 | State | local fermionic observables, Gaussian fidelities, Slater overlaps | Sample, single copies, random matchgates | variance $\sim n^{\vert S\vert/2}$, Pfaffians in $O(n^3)$ | 🟢 🟢 🟢 | parity, fermionic structure |
| Heyraud, Chomet, Tilly 2024 | State | the same fermionic quantities | Sample, $\mathrm{SO}(2n)$ ensemble or perfect-matching subensemble | the same variances, gate-optimal sampling | 🟢 🟢 🟢 | as above |
| Mao, Yi, Zhu 2024 | Qudit state, $d$ an odd prime | fidelities and Weyl observables | Sample, single copies, qudit Cliffords plus $k$ T gates | overhead $O(d)$ relative to qubits, $O(1)$ from one T gate on | 🟢 🟢 🟢 | bounded Hilbert–Schmidt norm |
| Chang, Krumtünger, Larocca, West 2026 | State | observables close to the diagonal of a basis | Sample, single copies, ensembles from $G/K$ | variance as for the parent-group protocol, slightly better on the diagonal | 🟢 🟢 🟢 | none |
| King, Gosset, Kothari, Babbush 2024 | State | all $4^n$ Paulis, $k$-body fermions | Sample, Bell measurement on $\rho\otimes\rho$, then single copies | $O(n\log(n/\epsilon)/\epsilon^4)$ and $O(k\log n\cdot p_k(4/\epsilon^2)/\epsilon^2)$ respectively | 🟢 🟢 🟢, time $\mathrm{poly}(\vert S\vert)$ | two-copy memory |
| King, Wan, McClean 2024 | Qudit state | all $d^2$ displacement amplitudes, magnitude and sign | Sample on $\rho\otimes\rho^*$ | $O(\log d/\epsilon^4)$; $\Omega(\sqrt d)$ on $\rho^{\otimes K}$ | 🟢 🟢 🟢 | conjugate access |
| Gross, Liu, Flammia, Becker, Eisert 2010 | State | the density matrix at rank $r$ | Sample, $O(rd\log^2 d)$ random Pauli expectation values | convex program, SVT | 🔴 🔴 🔴 in $n$ | rank $r \ll d$ |
| Keyl, Werner 2001 | State | the spectrum | Sample, collective Schur measurement on $\rho^{\otimes N}$ | error $e^{-N\cdot I(s)}$ with relative entropy $I$ | 🔴 🔴 🟢 in $n$ | none |
| O'Donnell, Wright 2016 | State | the density matrix; rank-$k$ approximation (PCA); the $k$ largest eigenvalues | Sample, weak Schur sampling plus Keyl's covariant measurement on $\rho^{\otimes N}$ | $O(d/\epsilon^2)$ Frobenius, $O(rd/\epsilon^2)$ trace distance; PCA $O(kd/\epsilon^2)$; top-$k$ eigenvalues $O(k^2/\epsilon^2)$ | 🔴 🔴 🔴 in $n$ | none |
| Haah, Kothari, O'Donnell, Tang 2023 | Unitary | $U$ in diamond norm | Query, $\Theta(d^2/\epsilon)$ applications, one qudit | bootstrap from $1/\epsilon^2$ to $1/\epsilon$ | 🔴 🔴 🔴 in $n$ | none |
| Lewis et al. 2024 | Family of ground states | $\mathrm{Tr}(O\rho(x))$ at new $x$ in the same phase | classical data $(x_\ell, y_\ell)$, shadows | $N = \log(n/\delta)\,2^{\mathrm{polylog}(1/\epsilon)}$, time $O(nN)$ | 🟢 🟢 🟢 | gap, geometric locality, known geometry |
| Onorati, Rouzé, França, Watson 2023 | Gibbs and ground states | Lipschitz observables of one instance; local observables across a phase | Sample, single copies | $O(\mathrm{polylog}(n)/\epsilon^2)$ and $O(\log(M/\delta)e^{\mathrm{polylog}(1/\epsilon)})$ respectively | 🟢 🟢 🟢 | exponential decay of correlations, GALI |
| Huang, Chen, Preskill 2023 | Channel | $\mathrm{Tr}(O\,\mathcal{E}(\rho))$ for locally flat $\rho\sim\mathcal{D}$ | Sample, product inputs, Pauli measurements | $N = O(\log n)$ at constant $\epsilon$, time $O(kn^kN)$ | 🟢 🟢 🟢 | locally flat distribution, bounded degree |
| Arunachalam, Dutt, Escudero Gutiérrez, Palazuelos 2024 | Channel, unitary, polynomial | all Pauli coefficients at degree $d$ | Query to $\mathcal{E}$ or $U$ | $\exp(\tilde O(d^2 + d\log 1/\epsilon))$, independent of $n$ | 🟢 🟢 🟢 | degree $d = O(1)$ |
| Klein, Slote, Volberg, Zhang 2023 | Qudit observable, function on $\mathbb{Z}_K^n$ | low-degree approximation in $L^2$ | Sample $(\rho, \mathrm{tr}[A\rho])$ on product states | $O(\log n)$ samples at constant degree | 🟢 🟢 🟢 | degree $d$, Heisenberg–Weyl or Gell-Mann basis |
| Haah, Kothari, Tang 2022 | Hamiltonian from a Gibbs state | the coefficients of known terms | Sample, copies of $e^{-\beta H}/Z$ | $O(\log(N/\delta)/(\beta^2\epsilon^2))$, time linear in that | 🟢 🟢 🟢 | $\beta < \beta_c$, low intersection |
| Huang, Tong, Fang, Su 2023 | Hamiltonian from dynamics | the coefficients of known terms | Query, $e^{-iHt}$ interleaved with layers of single-qubit Cliffords | $T = O(\epsilon^{-1}\log\delta^{-1})$, Heisenberg limit | 🟢 🟢 🟢 | known interaction graph |
| Flammia, Wallman 2020 | Pauli channel | all $4^n$ error rates, or $s$ selected ones, or a Markov field | Query, RB-type sequences of Pauli gates | $O(\epsilon^{-2}n2^n)$; $O(\epsilon^{-4}\log s\log(s/\epsilon^2))$; $O_k(\epsilon^{-2}n^2\log n)$ | 🟢 🟢 🟢 under sparsity | sparsity or $k$-local factor-graph model |
| Chen, Zhou, Seif, Jiang 2022 | Pauli channel | all $4^n$ eigenvalues | Sample on the Choi state with $k$ ancilla qubits | $O(n2^{n-k}/\epsilon^2)$, $O(n/\epsilon^2)$ at $k=n$; $\Omega(2^{n/3})$ without ancilla | 🟢 🟢 🟢 with ancilla | entangled ancilla memory |
| Subramanian, Kwon, Jiang 2026 | Qudit and bosonic channel | magnitudes of the Heisenberg–Weyl transfer matrix | $c$ parallel copies of $\mathcal{E}$ or of $\mathcal{E}\otimes\mathcal{E}^*$ | $O(\log(M/\delta)/\epsilon^4)$ with $\mathcal{E}^*$; $\Omega(d^{2m})$ for $c < d$; $\epsilon^{-2d}$ at $c = d$ | 🟢 🟢 🟢 with conjugate | conjugate access or $d$-copy memory |

Six families. The first five papers are generic shadow tomography: sample-efficient for every list, with a $2^n\times 2^n$ hypothesis as the price. The next nine are classical shadows and their ensembles: the shadow norm of the ensemble decides which observables are cheap. Then come the two-copy papers, which close the gap for global Paulis and introduce conjugate access; the four tomography limiting cases (rank, spectrum, full tomography, unitary); the five papers on learning across a phase and on low-degree structure; and finally Hamiltonians and channels. The common thread for this project: wherever a row is 🟢 🟢 🟢, a promise or a resource stands next to it; two-copy memory and conjugate access are the two resources that appear in several rows at once.

---
## Shadow Tomography of Quantum States (arXiv:1711.01053)

The paper by **Scott Aaronson** (UT Austin; STOC 2018, extended version 2018) introduces the problem that gives this table its name: given an unknown $D$-dimensional mixed state $\rho$ and $M$ known two-outcome measurements $E_1, \dots, E_M$, estimate each $\mathrm{Tr}(E_i\rho)$ to within $\pm\epsilon$. The main result: $\tilde O(\epsilon^{-4}\log^4 M\cdot\log D)$ copies suffice, i.e. polynomially many in $n = \log D$, even if $M$ is exponential. The name is due to Steve Flammia: one does not learn $\rho$, but the shadow that $\rho$ casts on the measurements.

### Placement in the tables

* **Task type:** Estimating in pure form. The list of observables is the input; nothing is searched, nothing identified. $M$ may be exponential, and exactly this distinguishes the row from naive estimation with $O(M/\epsilon^2)$ copies.
* **Object:** mixed state. **Access:** sample; the measurement, however, is an entangled procedure across all $k$ copies at once, with quantum memory $k$. This is the other end of the memory axis from classical shadows.
* **Status:** 🟢 🔴 🔴. Copies polylogarithmic; time and memory exponential, because the hypothesis is a $D\times D$ matrix and the measurement circuit is, in the worst case, polynomial in $M$ *and* $D$. This is the row "Shadow tomography, general" of the estimating table.
* **Promise:** none. The price for that is the size of the hypothesis; the row is the prototype of "hypothesis too large" in the appendix to the tables.

### The problem

Full tomography needs $\Theta(D^2)$ copies (O'Donnell–Wright, Haah et al.), i.e. $4^n$ for $n$ qubits. In 2016 Aaronson had asked whether $\mathrm{poly}(\log D, \log M)$ copies could suffice for *all* $M$ expectation values, and opinions were divided. The obvious idea, gentle measurement, fails without a promise gap: if $\mathrm{Tr}(E_i\rho)$ lies "on the edge", every measurement of $E_i$ damages the copies badly, and one has only polylogarithmically many of them. The motivation came from the theory of quantum money, but the applications extend to quantum advice and one-way communication.

### Key results

* **Theorem 2 (shadow tomography).** $k = \tilde O(\log(1/\delta)\cdot\log^4 M\cdot\log D/\epsilon^4)$ copies suffice; the procedure is explicit. An earlier version had $1/\epsilon^5$; the step to $1/\epsilon^4$ comes from the online learning algorithm of Aaronson, Chen, Hazan, Kale, and Nayak.
* **Theorem 16 and corollaries (lower bounds).** Every solution needs $\Omega(\min\{D^2, \log M\}/\epsilon^2)$ copies; in the classical special case $\Omega(\min\{D, \log M\}/\epsilon^2)$, and there the bound is tight. For arbitrarily large $M$ this subsumes the $\Omega(D^2)$ bound of tomography. Whether, quantumly, $(\log M)^{O(1)}$ copies suffice independently of $D$ remains open.
* **Proposition 20 (promise-gap version).** With a promise $\mathrm{Tr}(E_i\rho) \geq c_i$ or $\leq c_i - \epsilon$, $O(\log M/\epsilon^2)$ copies suffice via gentle measurement; this is the easy part.
* **Comparison with quantum Occam (Theorem 3).** The PAC theorem of 2007 gives $\tilde O(\log D/(\gamma^4\epsilon^4))$ copies, but only for a $1-\gamma$ fraction of the measurements; shadow tomography demands all of them.
* **Applications (Section 2).** Private-key quantum money, copy-protected software, quantum advice, one-way communication; Brandão et al. subsequently reduced the running time via SDPs.

### Methodological approach

1. **Postselected learning.** Start with the maximally mixed hypothesis $\rho_0 = I/D$. Find a measurement $E_i$ on which the current hypothesis is off by more than $\epsilon$, and update $\rho_t$ by simulated postselection on an outcome that is consistent with $\rho$. Because $\rho$ has weight at least $1/D$ in $I/D$, this converges after $\Theta(\log D)$ iterations. This is boosting, or multiplicative weights, in quantum language, and it originates in the proof of $\mathrm{BQP/qpoly} \subseteq \mathrm{PostBQP/poly}$.
2. **Gentle search.** There is no Alice who knows the violated measurements. The quantum OR bound (Aaronson 2006, corrected by Harrow, Lin, and Montanaro) decides with $O(\log M/\epsilon^2)$ copies *whether* an $E_i$ with $\mathrm{Tr}(E_i\rho) \geq c$ exists, without destroying the copies.
3. **Binary search** over the list turns the decision problem into a search problem; the error gap shrinks from $\epsilon$ to $\epsilon - \alpha$, $\epsilon - 2\alpha$, and so on, and this produces the factor $\log^4 M$.

### Significance and applications

* The paper defines the estimating column: the question "how many copies for $M$ questions" has been the standard measure ever since, and all later improvements (Aaronson–Rothblum, Bădescu–O'Donnell, Chen–O'Donnell–Pelecanos–Wright) are measured against $\log^4 M \cdot \log D/\epsilon^4$.
* It separates the information-theoretic from the computational problem and names the running time explicitly as open; classical shadows and triply efficient shadow tomography are answers to exactly this gap.
* Epistemically: for every polynomial-size family of circuits, an $n$-qubit state contains only $\mathrm{poly}(n)$ bits of learnable information.

### Relation to this project

* The row is the reference point against which the "triply efficient" formulation of this project's paper is defined: sample efficiency is settled here, time and memory efficiency are not. The instance ladder in research.md asks precisely for which classes of states the $2^n\times 2^n$ hypothesis can be replaced by a sparse surrogate.
* The distinction "all $M$" versus "most $M$" (shadow tomography versus PAC) is the same as that between a worst-case guarantee for every $(q,p)$ and an average-case guarantee over the top-$k$ distribution in this project's protocol.
* Postselected learning is the conceptual precursor of the MMW step that this project's CNN replaces; the $\Theta(\log D)$ iterations are the number of adaptive rounds that a learned decoder has to go through at least implicitly.

### Limitations and open questions

* The measurement is a joint measurement across all $k$ copies, with circuits of size polynomial in $M$ and $D$; this cannot be implemented in hardware.
* The gap between $1/\epsilon^4$ and $1/\epsilon^2$, and between $\log^4 M$ and $\log M$, was open at publication; Bădescu–O'Donnell brought the $M$ dependence down to $\log^2 M$ and Chen et al. 2026 to $\log M$.
* Whether the soundness of Aaronson's original OR procedure holds is open; the version of Harrow, Lin, and Montanaro is used.
* No robustness against noise and no statement about special classes of observables.

### Questions for further study

* How exactly does Bob simulate postselection classically, and where does the $\log D$ memory enter that a sparse surrogate would have to avoid?
* Does the lower bound $\Omega(\min\{D^2, \log M\}/\epsilon^2)$ also hold for lists of displacement operators with $M = d^2$, and what does it say about $\rho\otimes\rho^*$?
* Which of the applications (quantum money, advice) has a counterpart in the language "the state as a hypothesis that makes predictions"?

Paper: [arXiv:1711.01053](https://arxiv.org/abs/1711.01053)

---

## The Learnability of Quantum States (arXiv:quant-ph/0608142)

The paper by **Scott Aaronson** (Waterloo, 2006; *Proc. R. Soc. A* 2007) is the quantum Occam's razor theorem: an $n$-qubit state is PAC-learnable from a number of training measurements that grows only linearly in $n$, if one is content to predict *most* measurements from a distribution $\mathcal{D}$ correctly. The author stresses that the contribution is conceptual: the mathematics is in Bartlett–Long and in Ambainis, Nayak, Ta-Shma, and Vazirani; the observation that together they yield a learning theorem is new.

### Placement in the tables

* **Task type:** Estimating, average case. Given are training measurements $E_1, \dots, E_m \sim \mathcal{D}$ with their values; returned is a hypothesis $\sigma$ that matches $\mathrm{Tr}(E\rho)$ to within $\gamma$ for a $1-\epsilon$ fraction of the $E \sim \mathcal{D}$. The row "PAC learning of states" of the estimating table.
* **Object:** mixed state. **Access:** sample; each training measurement is repeated on $\Theta(\log m/\eta^2)$ copies, or, in the measure-once variant (Theorem 1.3), on exactly one.
* **Status:** 🟢 🔴 🔴. Training data linear in $n$; finding a consistent hypothesis is a QMA search problem, solvable by SDP in $\mathrm{poly}(2^n)$. Efficient only for structured classes, first for stabilizer states (Rocchetto 2018).
* **Promise:** no promise about the state, but one about the data: the future resembles the past; the test measurements come from the same distribution as the training measurements.

### The problem

Tomography needs $4^n$ observables; Häffner et al. needed 656,100 experiments for eight ions. For a thousand particles, a description could not be obtained even on cosmological time scales, and then the question arises what the state *means* at all: it should at least be a hypothesis that summarizes past observations and predicts future ones. The paper's answer: for predictions, "pretty-good tomography" suffices.

### Key results

* **Theorem 1.1.** With $m \geq \frac{K}{\gamma^2\epsilon^2}\big(\frac{n}{\gamma^2\epsilon^2}\log^2\frac{1}{\gamma\epsilon} + \log\frac1\delta\big)$ training measurements, the training set is "good" with probability $1-\delta$: every hypothesis $\sigma$ with $|\mathrm{Tr}(E_i\sigma) - \mathrm{Tr}(E_i\rho)| \leq \eta$ on all training data satisfies $\Pr_{E\sim\mathcal{D}}[|\mathrm{Tr}(E\sigma) - \mathrm{Tr}(E\rho)| > \gamma] \leq \epsilon$, provided $\gamma\epsilon \geq 7\eta$.
* **Theorem 1.2.** Better dependence on $\gamma$ and $\epsilon$ at the price of $n\log^2 n$: $m \geq \frac{K}{\epsilon}\big(\frac{n}{(\gamma-\eta)^2}\log^2\frac{1}{(\gamma-\eta)\epsilon} + \log\frac1\delta\big)$; Appendix 9 shows that this is nearly optimal.
* **Theorem 1.3 (measure once).** With a single bit per measurement and a hypothesis that minimizes the quadratic loss, the requirement rises from $\sim n/(\gamma^4\epsilon^4)$ to $\sim n/(\gamma^8\epsilon^4)$: $m \geq \frac{K}{\gamma^4\epsilon^2}\big(\frac{n}{\gamma^4\epsilon^2}\log^2\frac1{\gamma\epsilon} + \log\frac1\delta\big)$.
* **Adaptive measurements (Objection 2).** For $r$ adaptive rounds, $O(nr)$ samples suffice, and this is optimal.
* **Applications.** $R^1(f) = O(M\,Q^1(f))$ for the one-way communication complexity of every Boolean function; $\mathrm{HeurBQP/qpoly} \subseteq \mathrm{HeurQMA/poly}$: trusted classical advice verifies untrusted quantum advice on most inputs.

### Methodological approach

* **Fat-shattering dimension.** The hypothesis class of $n$-qubit states, as real-valued functions $E \mapsto \mathrm{Tr}(E\rho)$, has $\gamma$-fat-shattering dimension $O(n/\gamma^2)$. The proof turns around the lower bound for quantum random access codes by Ambainis et al.: whoever wants to encode $k$ bits with error $p$ into $n$ qubits needs $n \geq (1-H(p))k$; hence $n$ qubits cannot "shatter" more than $O(n/\gamma^2)$ measurements.
* **Bartlett–Long.** For real-valued hypothesis classes with bounded fat-shattering dimension there are generalization bounds; they supply the formulas of the theorems.
* **Distribution-free.** $\mathcal{D}$ only has to exist, not to be known; the same algorithm works for every $\mathcal{D}$.

### Significance and applications

* The beginning of quantum learning theory for states: shadow tomography (2018) and online learning (2018) generalize this theorem to "all measurements" and to adversarial orderings.
* Objection 3 first raises the question of time-efficient special cases, which Rocchetto (stabilizer), Grewal et al. (few T gates), and the promise catalogs of the searching and identifying tables later answer; the GGM reduction shows that generically efficient learning would break one-way functions.
* Realized experimentally by Rocchetto et al. (2019).

### Relation to this project

* The average-case formulation is the right language for a learned decoder pipeline: the CNN is trained and evaluated on a distribution of instances, and the generalization guarantee is a statement about this distribution, not about every address $(q,p)$.
* The fat-shattering bound $O(n/\gamma^2)$ is the clean argument for why $\mathrm{poly}(n)$ copies always suffice information-theoretically; as in Objection 3, the hardness of this project's problem lies solely in finding the hypothesis.
* Objection 2 is the answer to the question "Phase 2 is adaptive; does the theorem still hold?": yes, with a factor $r$ for the number of rounds.

### Limitations and open questions

* No statement about running time; efficient special cases were the explicit open question.
* $k$-outcome measurements only via a reduction with a factor $k$; a direct analysis is missing.
* The dependence $1/(\gamma^4\epsilon^4)$ in Theorem 1.1 is prohibitive in practice; Theorem 1.2 improves it at the cost of $n\log^2 n$.
* The i.i.d. assumption about the measurements is exactly what the online paper later removes.

### Questions for further study

* What does the fat-shattering calculation look like for displacement observables $D_{q,p}$ on a single qudit, where there is no $n$, only $\log d$?
* Can the random access code argument be repeated for $\rho\otimes\rho^*$ access, and does conjugate access change the effective dimension?
* Which distribution $\mathcal{D}$ over observables corresponds to the top-$k$ distribution of this project's protocol, and what is its effective fat-shattering dimension?

Paper: [arXiv:quant-ph/0608142](https://arxiv.org/abs/quant-ph/0608142)

---

## Online Learning of Quantum States (arXiv:1802.09025)

The paper by **Scott Aaronson, Xinyi Chen, Elad Hazan, Satyen Kale, and Ashwin Nayak** (UT Austin, Princeton, Google AI, Waterloo; NeurIPS 2018) generalizes the PAC theorem of 2007 to the online model: the measurements $E_1, E_2, \dots$ arrive one after another, adversarially and adaptively, and the learner has to make a prediction before each one. Result: at most $O(n/\epsilon^2)$ mistakes larger than $\epsilon$, and in the non-realizable case regret $O(\sqrt{Tn})$. Three proofs, each with different strengths.

### Placement in the tables

* **Task type:** Estimating, sequential. The observables are revealed one after the other; returned is one prediction per round. The row "Online learning of quantum states" of the estimating table.
* **Object:** mixed state. **Access:** sample-free at its core: after each round, feedback $b_t$ with $|b_t - \mathrm{Tr}(E_t\rho)| \leq \epsilon/3$ is supplied; where it comes from (single-copy measurements) does not matter to the algorithm.
* **Status:** 🟢 🔴 🔴. Number of mistakes linear in $n$; running time per round exponential in $n$, because $E_t$ is given as a $2^n\times 2^n$ matrix and the hypothesis $\omega_t$ is equally large. This is unavoidable as long as input and output are explicit.
* **Promise:** none about the state, none about the order of the measurements.

### The problem

The PAC theorem assumes that training and test measurements are i.i.d. from the same distribution. In the lab, nature determines which measurements are possible, and the set grows with the degree of control; the theorist is challenged round by round. What is sought is a learning algorithm that needs no distributional assumption at all and whose number of mistakes stays bounded, wherever the mistakes occur.

### Key results

* **Theorem 1 (mistake bound).** There is an explicit strategy for hypotheses $\omega_1, \omega_2, \dots$ such that $|\mathrm{Tr}(E_t\omega_t) - \mathrm{Tr}(E_t\rho)| > \epsilon$ occurs at most $O(n/\epsilon^2)$ times. This is optimal, because the $\epsilon$-fat-shattering dimension of states is $\Theta(n/\epsilon^2)$.
* **Theorem 2 (regret).** For convex, $L$-Lipschitz losses $\ell_t$, in particular $L_1$ and $L_2$, there is a strategy with regret $R_T = O(L\sqrt{Tn})$ against the best fixed hypothesis in hindsight, even against an adaptive adversary and without the data having to come from a state. Lower bound $\Omega(\sqrt{Tn})$ for $L_1$.
* **Sequential fat-shattering dimension** of $n$-qubit states: $O(n/\epsilon^2)$, via Nayak's random access code bound and "measurement decision trees". With it, every online algorithm that needs only this dimension works, up to $\log^{3/2} T$.
* **Application.** Used as a black box in Aaronson's shadow tomography, Theorem 1 improves the copy count from $1/\epsilon^5$ to $1/\epsilon^4$.

### Methodological approach

1. **Regularized follow-the-leader / matrix exponentiated gradient** (Section 3). Start at $\omega_1 = 2^{-n}I$, regularize with the von Neumann entropy, update via the matrix exponential of the accumulated gradient; the convexity and Taylor arguments are carried over from real to complex matrices. Best parameters, connection to the online convex optimization literature.
2. **Postselection** (Section 4). The same idea as in the shadow tomography paper: refine the maximally mixed hypothesis by simulated postselected measurements; self-contained, but without optimal parameters and without a regret statement.
3. **Sequential fat-shattering dimension** (Section 5). Gives the regret bound via Rakhlin et al. and makes the theorem portable to every online learner with a dimension guarantee.

### Significance and applications

* This is the MMW engine behind all later improvements of shadow tomography: Bădescu–O'Donnell reduce threshold search to this mistake-bounded learner, King, Gosset, Kothari, and Babbush compute their mimicking state with it, and King, Wan, and McClean carry it over to displacement operators.
* Only single-copy measurements and noisy feedback: closer to the lab than optimal tomography or certification, which need entangled measurements across exponentially many copies.
* The regret formulation covers the non-realizable case: the data do not have to come from a state.

### Relation to this project

* This is the algorithm that this project's paper explicitly replaces: "the Matrix Multiplicative Weights update that drives their adaptivity". The hypothesis $\omega_t$ is the $d\times d$ matrix that has become the sparse surrogate with $O(k)$ weights in this project's protocol.
* The mistake bound $O(n/\epsilon^2)$ is an upper bound on the number of adaptive rounds a Phase 2 strategy needs; it says that the sequential sign integrator can be "surprised" at most $O(\log d/\epsilon^2)$ times.
* The exponential running time per round is the failure mode "hypothesis too large" in the appendix to the tables: memory forces time. A CNN with fixed input size $6\times 64\times 64$ is the counter-design, without a guarantee.

### Limitations and open questions

* Regret $O(\sqrt{Tn})$ versus $\Omega(n)$ for $L_2$ in the realizable case: the gap remains.
* Running time exponential, unavoidable for explicit matrices; nothing is said about implicitly given $E_t$ (Paulis, for instance).
* The postselection proof yields no regret bound; whether it can be made to do so is open.
* Feedback with error $\epsilon/3$ is assumed; how many copies it costs lies outside the model.

### Questions for further study

* What does the RFTL update look like concretely if the hypothesis is restricted to a support of $k$ displacement addresses, and is the mistake bound preserved?
* What is the sequential fat-shattering dimension of the class "states with a $k$-sparse displacement spectrum"?
* How does the regret behave if the feedback comes from Bell measurements on $\rho\otimes\sigma^*$ with *known* $\sigma$, i.e. from exactly the measurement of Phase 2?

Paper: [arXiv:1802.09025](https://arxiv.org/abs/1802.09025)

---

## Improved quantum data analysis (arXiv:2011.10908)

The paper by **Costin Bădescu and Ryan O'Donnell** (Carnegie Mellon; STOC 2021, full version *TheoretiCS* 2024) improves the basic routines of quantum data analysis quadratically and simplifies their proofs. The core is a quantum threshold search algorithm with $O(\log^2 m/\epsilon^2)$ copies instead of $\tilde O(\log^4 m)$. From it follow shadow tomography with $\tilde O(\log^2 m\cdot\log d/\epsilon^4)$ copies, at publication the best known dependence on all three parameters simultaneously, and hypothesis selection among $m$ states with the same copy count or, alternatively, $\tilde O(\log^3 m/\epsilon^2)$.

### Placement in the tables

* **Task type:** Estimating for threshold search and shadow tomography, identifying for hypothesis selection. The paper therefore appears in two tables: as an improvement of the row "Shadow tomography, general" and as the source of the polylogarithmic-in-$M$ copy count in "Identification: hypothesis selection".
* **Object:** mixed state. **Access:** sample, unentangled copies $\rho^{\otimes n}$; the measurements themselves are collective across the copies, as in Aaronson.
* **Status:** 🟢 🔴 🔴 for shadow tomography, for the same reason as there; threshold search itself is polynomial in the observables $A_i$, but the reduction to the online learner brings back the $d\times d$ hypothesis.
* **Promise:** none. What is new is the insight that the right classical counterpart is not differential privacy but *adaptive data analysis*.

### The problem

Classically, one estimates $m$ expectation values from $O(\log m/\epsilon^2)$ samples by reusing the same samples. Quantumly, every measurement changes the state, and reuse is delicate. The best bounds were $\tilde O(\log^4 m\cdot\log d/\epsilon^4)$ (Aaronson) and $\tilde O(\log^2 m\cdot\log^2 d/\epsilon^8)$ (Aaronson–Rothblum, from differential privacy). The authors want to treat the core of the matter, reuse under conditioning, cleanly and with optimal parameters.

### Key results

* **Theorem 1.1 (threshold search).** Given observables $0 \leq A_i \leq 1$ and thresholds $\theta_i$: output either a $j$ with $\mathbb{E}_\rho[A_j] > \theta_j - \epsilon$ or the statement "all $\mathbb{E}_\rho[A_i] \leq \theta_i$", with $n = \frac{\log^2 m + \ell}{\epsilon^2}\cdot O(\ell)$ copies, $\ell = \log(1/\delta)$. The algorithm is *online*: the pairs $(A_t, \theta_t)$ arrive one after another, and it passes or halts.
* **Threshold decision** (Appendix A): only the existence question, $O(\log(m/\delta)/\epsilon^2)$ copies, a streamlining of Harrow, Lin, Montanaro.
* **Theorem 1.2 ($\chi^2$-stable threshold reporting).** For $S \sim \mathrm{Binomial}(n,p)$ and independent exponential noise $X$ with $\mathbb{E}[X] \geq \mathrm{stddev}[S]$, conditioning on "$S + X$ below the threshold" changes the distribution of $S$ only by $d_{\chi^2} \lesssim \big(\Pr[B]\cdot\mathrm{stddev}[S]/\mathbb{E}[X]\big)^2 \leq \Pr[B]^2\cdot n/\mathbb{E}[X]^2$, where $B$ is the event "above the threshold". This is a purely classical theorem and the technical core; it composes like the sparse vector mechanism.
* **Theorem 1.4 (shadow tomography).** $n = \frac{(\log^2 m + \ell)\log d}{\epsilon^4}\cdot O(\ell)$ copies, online against adaptively chosen $A_t$, via the black-box reduction to the mistake-bounded online learner of Aaronson et al.
* **Theorem 1.5 (hypothesis selection).** Among $m$ states $\sigma_i$, find $k$ with $d_{\mathrm{tr}}(\rho, \sigma_k) \leq 3.01\eta + \epsilon$, $\eta = \min_i d_{\mathrm{tr}}(\rho,\sigma_i)$; the copy count is the minimum of the shadow tomography bound and $\tilde O(\log^3 m/\epsilon^2)$. For pairwise far-apart hypotheses, the classical optimal bound is reached.

### Methodological approach

* The difficulty lies in the case $\epsilon = \delta = 1/4$, $\theta_j = 3/4$. Each observable $A_t$ is measured as an amplified two-outcome measurement on $\rho^{\otimes n}$, exponential noise is added to the count statistic, and a threshold is checked. As long as no "above threshold" occurs, the state is, by Theorem 1.2, hardly changed in $\chi^2$ divergence; the divergences add up over the rounds, and because each is a small fraction of $\Pr[B]^2$, the state survives until the first hit.
* The step to shadow tomography is the standard reduction: the online learner makes at most $O(\log d/\epsilon^2)$ mistakes, threshold search finds each mistake with $\log^2 m/\epsilon^2$ copies, and $\log d/\epsilon^2$ mistakes times $\log^2 m/\epsilon^2$ copies gives $\log^2 m\cdot\log d/\epsilon^4$.
* The authors' philosophical remark: in practice $\log d$ is small and $\epsilon$ matters ($1/\epsilon^4$ hurts), and theoretically $m$ is the most interesting, because $\log m$ instead of $\log^2 m$ would bring hypothesis selection to the classical rate.

### Significance and applications

* Best shadow tomography bound from 2021 to 2026; the threshold search primitive has been a standard tool ever since, also in Chen, O'Donnell, Pelecanos, Wright (2026), who bring the same reduction down to $\log m$ with a new damage measure.
* Hypothesis selection with polylogarithmically many copies in $M$ is the basis of all identifying rows with a polynomial list of candidates.
* The perspective "adaptive data analysis instead of differential privacy" is the conceptual bridge that also carries the Efron–Stein view of 2026.

### Relation to this project

* Threshold search is the formal version of "is there an address with $|y_{q,p}| \geq \theta$?": exactly the question that Phase 1 answers for all $d^2$ addresses simultaneously, but there non-adaptively from the Bell record. The copy count $O(\log^2 m/\epsilon^2)$ with $m = d^2$ is a reference value for the $O(\log d/\epsilon^4)$ of the conjugate-pair method: better in $\epsilon$, worse in $\log d$, and without the conjugate.
* Hypothesis selection with $3.01\eta + \epsilon$ is the agnostic framework in which a list of candidate supports from the CNN could be evaluated: $M$ surrogate states, $\mathrm{polylog}(M)$ copies.
* The $\chi^2$ stability is a clean tool for quantifying how much Phase 2 "uses up" the copies when probe measurements run sequentially on the same register; this project's protocol takes fresh copies instead, which makes the analysis trivial but the copy count larger.

### Limitations and open questions

* $\log^2 m$ instead of $\log m$; named by the authors as the most interesting gap, and closed in 2026.
* $1/\epsilon^4$ instead of $1/\epsilon^2$; all shadow tomography results have "atypical" $\epsilon$ exponents, as in adaptive data analysis.
* No statement about running time; the reduction to MMW remains exponential.
* The $\chi^2$ bound holds for binomial statistics, i.e. two-outcome measurements; multi-outcome measurements need a reduction.

### Questions for further study

* How does Theorem 1.2 carry over to the multinomial statistics of a Bell measurement with $d^2$ outcomes?
* What is the hypothesis selection bound if the $m$ candidates are themselves available only as surrogates with $O(k\log d)$ bits, and does $3.01\eta$ then hold for the fidelity in the displacement spectrum?
* Where exactly does the reduction threshold search $\to$ shadow tomography lose the factor $\log d/\epsilon^2$, and is this the factor that Chen et al. 2026 save with the energy argument?

Paper: [arXiv:2011.10908](https://arxiv.org/abs/2011.10908)

---

## Online Shadow Tomography Matching the Classical Bounds (arXiv:2607.29686)

The paper by **Sitan Chen, Ryan O'Donnell, Angelos Pelecanos, and John Wright** (Harvard, CMU, Berkeley; 2026) closes the gap, open since 2016, between the quantum and the classical rates of shadow tomography. Two protocols: $O(\log m\sqrt{\log d}/\epsilon^3)$ copies, the first with $o(\log^2 m)$ and at the same time $\mathrm{poly}(\log d/\epsilon)$, and $O(\sqrt m/\epsilon^2)$ copies, dimension-free and optimal among dimension-free bounds. Both hold online against adaptively chosen observables, and the minimum of the two is, up to constants, the classical rate of adaptive data analysis. The tool is new: measurement damage is measured via the *excitation decomposition* (Pickl 2011), the dual form of the quantum Efron–Stein decomposition.

### Placement in the tables

* **Task type:** Estimating, online. The observables $0 \preceq A^{(t)} \preceq 1$ arrive adaptively based on the transcript so far, and every answer has to be within $\pm\epsilon$. Offline is the special case of fixed observables, and there too the paper improves all three exponents.
* **Object:** mixed state. **Access:** sample, $n$ copies, measured with two-outcome measurements of *lifted* observables $\bar A = \frac1n\sum_i A_i$ across all copies, i.e. with quantum memory $n$.
* **Status:** 🟢 🔴 🔴. Copies at the classical level; the $\log m$ protocol runs via MMW with a $2^n\times 2^n$ hypothesis, the $\sqrt m$ protocol measures directly, but via $d^n$-dimensional projectors.
* **Promise:** none. This is the new row "Shadow tomography, general" with the rates of 2026; the table and the paragraph "What is open (1)" have been updated accordingly.

### The problem

Classically (all matrices diagonal), the problem is adaptive data analysis with $n = O(\min\{\log m\sqrt{\log d}/\epsilon^3, \sqrt m/\epsilon^2\})$ (Bassily et al.), and there is evidence of optimality (Nissim et al.; Lyu–Talwar). Quantumly, the state of the art was $O(\log^2 m\cdot\log d/\epsilon^4)$ (Bădescu–O'Donnell, Bostanci–Bene Watts) and, offline, $O(\sqrt m\log m/\epsilon^2)$ (Sinha). For $d$ exponential in $m$, nothing online was better than the trivial estimator. The question: are the classical rates achievable quantumly?

### Key results

* **Theorem 1.2.** Online shadow tomography with $n = O(\sqrt K\log(m+K)/\epsilon^2)$ copies, $K = \Theta(\log d/\epsilon^2)$, i.e. $O(\log m\sqrt{\log d}/\epsilon^3)$, success probability $9/10$.
* **Theorem 1.3.** Online shadow tomography with $n = O(\sqrt m/\epsilon^2)$ copies, independent of $d$; improves the best previous online result by a factor $\sqrt m\log m$ and Sinha's offline bound $O(\sqrt m\log m/\epsilon^2)$ by $\log m$, and removes, along the way, the $\log(1/\epsilon)$ factor of the classical bound of Dagan–Kur at constant failure probability.
* **Lemma 3.4 (energy controls damage).** For a subnormalized state $\tau$ that lies in the subspace $|\bar A - \mathrm{Tr}(A\rho)\mathbb{1}| \geq \xi$, $\mathrm{Tr}(\tau) \leq 18\,\mathcal{E}[\tau]/\xi^2$ with the energy $\mathcal{E}[\tau] = \frac1n\mathrm{Tr}(N\tau)$, where $N = \sum_i Q_i$ is the number operator of the excitations.
* **Corollary 4.6 / Lemma 5.3 (energy increase per round).** In the logistic two-outcome test, the energy grows by at most $O(\lambda^2/n^2\cdot\mathrm{Tr}(f(\bar A)\tau))$, in the noisy direct measurement by $O(1/(n^2\epsilon^2))$.
* **Appendix A.** Optimal threshold search via information-theoretic methods.

### Methodological approach

1. **Excitation decomposition.** With $P = |\psi\rangle\langle\psi|$ (purification of $\rho$) and $Q = 1-P$, every vector on $n$ registers decomposes orthogonally into $|\phi_S\rangle = \prod_{i\in S}Q_i\prod_{i\notin S}P_i|\phi\rangle$. For $|\psi\rangle^{\otimes n}$ all mass lies on $S = \emptyset$; the more mass on large $S$, the more damaged the state. The energy is the mean number of excitations, in Boolean language the total influence; formally the decomposition is dual to the quantum Efron–Stein decomposition (Pelecanos, França, Marwaha, O'Donnell 2025).
2. **Charging.** A "problematic" state, on which $\bar A$ deviates from the true value by more than $\epsilon$, has either small probability or high energy (Lemma 3.4). It therefore suffices to control the expected energy increase of each operation.
3. **Many observables (Theorem 1.2).** A student–teacher game as in Aaronson: the student runs MMW, the teacher tests whether the estimate $\nu$ is close, with the two-outcome measurement $f(\bar A)$, $f$ logistic with steepness $\lambda$. If the estimate is wrong, the outcome is strongly biased, hence little damage; the sum of the energy increases is the expected number of mistakes $O(\log d/\epsilon^2)$ times $\lambda^2/n^2$, and $\lambda = O(n\epsilon^2/\sqrt{\log d})$ plus a term $me^{-\Omega(\lambda\epsilon)}$ give $n = \Omega(\log m\sqrt{\log d}/\epsilon^3)$.
4. **Few observables (Theorem 1.3).** Measure directly, with compactly supported cosine noise of width $\Theta(\epsilon)$ (instead of Gaussian noise, to save $\log m$); energy increase $O(1/(n^2\epsilon^2))$ per round; after $m$ rounds, $m/(n^2\epsilon^2) \lesssim \epsilon^2$ gives $n = \Omega(\sqrt m/\epsilon^2)$.

### Significance and applications

* Ends a ten-year gap; the estimating table of this document now lists the classical rates in the column "Copies".
* Specialized to diagonal matrices, the argument gives new proofs of the classical rates *without* differential privacy, via Fourier analysis on product spaces: the Efron–Stein view is new classically as well.
* For special classes of observables there is room left: for Paulis nothing better than $1/\epsilon^4$ was known before 2026, and Chen, Gong, Ye showed that any improvement needs highly entangled measurements.

### Relation to this project

* The paper supplies the new reference rate for the column "Copies" for generic lists; the paragraph "What is open (1)" in the estimating section was formulated for $1/\epsilon^4$ and now states $1/\epsilon^3$ with the Lyu–Talwar evidence for optimality.
* Energy as a damage measure is a candidate for the question of how much Phase 2 of this project's protocol really uses up the copies: the probe measurement on $\rho\otimes\sigma^*$ is a lifted observable across two registers, and its excitation balance would be directly computable.
* The remark on Paulis (no better $\epsilon$ dependence than $1/\epsilon^4$ without highly entangled measurements) is a warning: the $O(\log d/\epsilon^4)$ of conjugate-pair magnitude estimation can probably not be improved without larger quantum memory; an empirically observed $\epsilon^{-3.2}$ would then be an instance effect, not a gain of the protocol.

### Limitations and open questions

* Success probability $9/10$; the $\delta$ dependence is not worked out.
* Both protocols need quantum memory $n$ and measurements in the eigenspaces of lifted observables; as unsuitable for hardware as Aaronson's original.
* Optimality: $\Omega(\log m\sqrt{\log d}/(\epsilon^2\log(1/\epsilon)))$ is proven, $\epsilon^{-3}$ only for algorithms that are also accurate on the empirical samples.
* No statement about running time; MMW remains.

### Questions for further study

* What does the excitation decomposition look like for $\rho\otimes\rho^*$, where the two registers carry different states, and is the Bell measurement a "lifted" observable in the sense of the paper?
* Can the energy argument explain or improve the $1/\epsilon^4$ of Bell-sampling magnitude estimation if Bell measurements across more than two copies are allowed?
* What is the Efron–Stein decomposition of a displacement operator $D_{q,p}$ on $n$ copies of a qudit, and how is its degree related to $(q,p)$?

Paper: [arXiv:2607.29686](https://arxiv.org/abs/2607.29686)

---
## Predicting Many Properties of a Quantum System from Very Few Measurements (arXiv:2002.08953)

The paper by **Hsin-Yuan Huang, Richard Kueng, and John Preskill** (Caltech, JKU Linz; *Nature Physics* 16, 1050 (2020)) is the classical shadows paper. It combines Aaronson's viewpoint (predict properties instead of reconstructing the state) with rigorous convergence guarantees and the stabilizer formalism into a protocol that predicts $M$ linear functions from $O(\log M)$ single-copy measurements, independent of the system size and with a matching information-theoretic lower bound. The target observables may be chosen after the measurement.

### Placement in the tables

* **Task type:** Estimating. Given $M$ linear functions $\mathrm{Tr}(O_i\rho)$, their values are returned via median of means. The rows "Classical shadows, $k$-local Paulis" and, with the Clifford ensemble, fidelity estimation in the estimating table.
* **Object:** mixed state. **Access:** sample, single copies, a random basis per copy (rung 1 of the access ladder, the primitive "single-copy randomized measurements").
* **Status:** 🟢 🟢 🟢 under the promise expressed by the shadow norm: locality $k$ (Pauli ensemble, norm $\leq 4^k\Vert O\Vert_\infty^2$, $3^k$ for tensor products of Paulis) or bounded Hilbert–Schmidt norm (Clifford ensemble, norm $\leq 3\,\mathrm{tr}(O^2)$). Global Paulis cost $3^n$ and $2^n$ respectively: this is the gap that two-copy measurements close.
* **Promise:** no promise about the state, only about the observables.

### The problem

Tomography scales exponentially in copies, memory, and running time. MPS and neural network tomography help only under structural assumptions. Aaronson's shadow tomography is sample-efficient but needs exponentially long circuits across all copies in quantum memory. What is sought: a protocol that predicts just as many properties, but with single-copy measurements, efficient post-processing, and provable guarantees.

### Key results

* **Procedure.** Per copy: a random $U$ from the ensemble, a computational-basis measurement, store the snapshot $\hat\rho = \mathcal{M}^{-1}(U^\dagger|\hat b\rangle\langle\hat b|U)$ with $\mathbb{E}[\hat\rho] = \rho$. For $n$-qubit Cliffords $\mathcal{M}_n^{-1}(X) = (2^n+1)X - I$, for tensor products of single-qubit Cliffords the tensor product of $\mathcal{M}_1^{-1}(X) = 3X - I$.
* **Theorem 1.** $N = O(\log M\cdot\max_i\Vert O_i\Vert_{\mathrm{shadow}}^2/\epsilon^2)$ snapshots suffice to get all $M$ values to within $\epsilon$; the proof uses a variance bound plus median of means ($K = 2\log(2M/\delta)$ groups).
* **Theorem 2 (lower bound).** Every single-copy procedure needs $\Omega(\log M\cdot\max_i\Vert O_i\Vert_{\mathrm{shadow}}^2/\epsilon^2)$ measurements, with the shadow norm as the Hilbert–Schmidt norm or as an exponential function of the locality. The proof embeds the task into a communication protocol.
* **Nonlinear functions.** $\mathrm{tr}(O\rho\otimes\rho)$ via U-statistics over pairs of independent snapshots; Rényi-2 entropy of small subsystems, cost exponential in $|A|$, independent of $n$.
* **Numerics.** Up to 160 qubits; GHZ fidelity with constant shadow size against NNQST, which grows linearly in $n$ and, for phase errors ($p \to 1$), reports a fidelity close to one where it is zero; two-point functions in the 1D TFIM (50 sites) and in the 2D Heisenberg model ($8\times 8$); entanglement entropies against Brydges et al.; energy variance of local Hamiltonians.
* **Direct fidelity estimation** needed $O(2^n/\epsilon^4)$ samples in the worst case; Clifford shadows need $O(1/\epsilon^2)$, independent of $n$.

### Methodological approach

* **The measurement channel.** $\mathcal{M}(\rho) = \mathbb{E}[U^\dagger|\hat b\rangle\langle\hat b|U]$ is a quantum channel, invertible if and only if the ensemble is tomographically complete; the inverse is not physical (not completely positive), but it is only applied classically.
* **The shadow norm.** $\Vert O\Vert_{\mathrm{shadow}}^2 = \max_\sigma\mathbb{E}_U\sum_b\langle b|U\sigma U^\dagger|b\rangle\langle b|U\mathcal{M}^{-1}(O)U^\dagger|b\rangle^2$ is a variance bound that depends only on the ensemble and on $O$. For 3-designs (Cliffords) it gives $3\,\mathrm{tr}(O^2)$; for local Paulis it factorizes over the qubits.
* **Memory.** Snapshots are stabilizer states and are stored as tableaus; for stabilizer observables (GHZ, toric code), evaluation via Gottesman–Knill takes $O(n^2)$.

### Significance and applications

* The workhorse of practice: NISQ-compatible, open-source code, the basis of the randomized measurement toolbox (Elben et al. 2023), of derandomization (Huang, Kueng, Preskill 2021), and of the fermionic, locally scrambled, Bell, and symmetric ensembles in the following summaries.
* The shadow norm is the language in which all later ensemble papers express their results; Theorem 2 says that the exponential dependence on locality is a law of nature for single copies, not an artefact.
* The comparison with NNQST is the first clean side-by-side of provable and learned decoders on the same task.

### Relation to this project

* Theorem 2 is the single-copy wall against which the project works: for displacement operators on a qudit, the shadow norm of the generalized Clifford ensemble is $\Omega(d)$ (King, Wan, McClean, Theorem 31), hence $\Omega(d/\epsilon^2)$ copies for all $d^2$ amplitudes. The conjugate-pair measurement is the way out, and this paper supplies the reference against which the advantage is measured.
* Median of means is the estimator that Phase 1 also uses; the constants of this paper are conservative (Fu et al. 2024).
* The numerics are a model for the instance ladder: the same models (TFIM, Heisenberg), the same observables (two-point functions), the same comparison with a learned model.

### Limitations and open questions

* Global observables: Pauli strings of length $n$ cost $3^n$ shadows, a direct measurement $1/\epsilon^2$; the authors themselves call it the "non-example".
* There is no lower bound for nonlinear functions.
* $n$-qubit Cliffords need $n^2/\log n$ entangling gates; shallow shadows (Bertoni et al., Hu–Choi–You, Ippoliti) are the answer.
* Noise: robust variants (Chen, Yu, Zeng, Flammia 2021; Koh, Grewal 2022) came later.

### Questions for further study

* What does the shadow norm of the generalized qudit Clifford ensemble look like concretely for $D_{q,p}$, and why does it carry the factor $d$ (compare Theorem 31 in King, Wan, McClean and Mao, Yi, Zhu)?
* Can the U-statistics construction for $\mathrm{tr}(O\rho\otimes\rho)$ *simulate* the Bell measurement on $\rho\otimes\rho$, and what does the simulation cost compared with a genuine two-copy measurement?
* What exactly breaks in NNQST in the case $p = 1$, and which certificate size would protect a learned decoder from the same error?

Paper: [arXiv:2002.08953](https://arxiv.org/abs/2002.08953)

---

## Experimental quantum state measurement with classical shadows (arXiv:2106.10190)

The paper by **Ting Zhang, Jinzhao Sun, Xiao-Xu Fang, Xiao-Ming Zhang, Xiao Yuan, and He Lu** (Shandong, Peking, Oxford, Hong Kong; *Phys. Rev. Lett.* 127, 200501 (2021)) tests the classical shadows family on a photonic four-qubit processor under realistic conditions: finite numbers of measurements, noisy operations. It compares uniform, locally biased, and derandomized shadows with importance sampling and observable grouping, for linear observables, Hamiltonian moments, and nonlinear quantities such as purities and PT moments.

### Placement in the tables

* **Task type:** Estimating. Given are lists of local Paulis, a Hamiltonian, subsystem purities, and moments of the partial transpose; their values are returned. New row "Classical shadows in hardware" of the estimating table.
* **Object:** a prepared four-qubit GHZ state with fidelity $0.9546 \pm 0.0006$ (by QST). **Access:** sample, single copies, local Cliffords via wave plates.
* **Status:** 🟢 🟢 🟢 at $n = 4$; the question of the paper is not scaling but constants and noise.
* **Promise:** locality of the observables ($\leq 2$-local Paulis); the derandomized variant additionally uses knowledge of the list.

### The problem

A molecular Hamiltonian with $M$ modes has $O(M^4)$ terms; naive measurement costs $O(M^8/\epsilon^2)$ shots. Advanced measurement strategies (importance sampling, grouping, shadows) are understood theoretically, but their practicality and their behavior under hardware noise were untested. The authors implement the unified framework of Wu et al., in which all strategies are special cases of a distribution $K(\mathcal{P})$ over measurement bases with a weight function $f$.

### Key results

* **Setup.** Polarization-entangled photon pairs from a Sagnac interferometer, extended via a beam displacer to a hyperentangled state $|GHZ_4\rangle = (|HhHh\rangle + |VvVv\rangle)/\sqrt2$ in polarization and path; Pauli measurements and single-qubit Cliffords from HWP/QWP sets; five coincidences per measurement basis.
* **Linear observables.** 50 random $\leq 2$-local Paulis; the maximal error decreases with $N_s$ and is below $0.1$ at $N_s = 2000$ for all methods except $\ell_1$ sampling; at fixed $N_s$ and a growing number of observables, derandomized shadowing is the most accurate.
* **Hamiltonian.** $H = J\sum_i(Z_iZ_{i+1} + X_iY_{i+1} + Y_iZ_{i+1} + X_iZ_{i+1}) + h\sum_i X_i$ with $J = h = 1/4$: for $\langle H\rangle$, LDF grouping and derandomized shadows are on par; for $\langle H^2\rangle$, with many terms of large support, derandomized shadows are clearly better.
* **Nonlinear quantities.** With $N_s = 1000$ shadows: subsystem purities $P_A$ for all subsets via U-statistics over pairs; $P_A < P_{AB}$ for all $A$ certifies genuine multipartite entanglement. PT moments $p_n = \mathrm{Tr}[(\rho^{T_A})^n]$ via U-statistics over $n$-tuples; $p_2^2 > p_3$ (violation of the $p_3$-PPT condition) shows bipartite entanglement, also for mixed states.
* **Error scaling.** The error of the purity and of $p_2$ falls like $1/N_s$ for small $N_s$, faster than the asymptotic $1/\sqrt{N_s}$.

### Methodological approach

* A unified estimator $\hat o(\mathcal{P}) = \sum_l\alpha_l f(\mathcal{P}, O_l, K)\mu(\mathcal{P}, \mathrm{supp}(O_l))$ with single-shot outcomes $\mu$; the methods differ only in $K$ and $f$: $\ell_1$ sampling ($K \propto|\alpha_l|$), LDF grouping (compatible terms in groups), uniform shadows ($K = 3^{-n}$), locally biased shadows (product distribution), derandomized shadows (greedily chosen bases).
* Shadows: $\hat\rho = \bigotimes_i(3U_i^\dagger|b_i\rangle\langle b_i|U_i - I)$; subsystem estimators by restricting the index.
* Comparison against QST as the reference, 20 and 10 repetitions respectively for error bars.

### Significance and applications

* First side-by-side comparison of all current measurement strategies on the same hardware; the statement "derandomized shadows win for many large terms" has been practical knowledge for VQE-type applications ever since.
* Shows that shadows deliver nonlinear quantities (entanglement witnesses) on real data, without tomography.
* Precursor experiments: Struchalin et al. (optical, uniform stabilizer measurements), Elben et al. (trapped-ion data for entanglement detection).

### Relation to this project

* The factor "hardware realism" of this project's taxonomy has a data point here: at four qubits and $10^3$ to $2\cdot 10^3$ shots, all methods lie in the error range $10^{-1}$, and noise does not change the ranking.
* The U-statistics estimators for $p_2$ and $p_3$ are the single-copy simulation of two- and three-copy observables; the comparison with a genuine Bell measurement on $\rho\otimes\rho$, which yields $\mathrm{tr}(\rho^2)$ directly, would be the experiment that makes the memory axis visible in hardware.
* The finding that the ensemble (uniform, biased, derandomized) determines the accuracy at a fixed number of shots is the single-copy analogue of the question which two-copy basis (Bell on $\rho\otimes\rho$ or on $\rho\otimes\rho^*$) makes the spectrum most visible.

### Limitations and open questions

* Four qubits, one state; no statement about scaling.
* No error mitigation; the authors name the combination of shadows with error mitigation as the next step.
* The derandomized variant needs the list of observables in advance and thereby gives up the "measure first, ask later" property.
* The $1/N_s$ scaling at small $N_s$ is observed, not explained.

### Questions for further study

* How many coincidences per basis are optimal when the choice of basis itself costs time, and how does that change the effective sample complexity?
* Can the $p_3$-PPT criterion be read off from a Bell record on $\rho\otimes\rho^*$, and what is the two-copy counterpart of the PT moments?
* Which noise models (dephasing in polarization versus path) explain the ranking of the methods, and does randomized compiling change it?

Paper: [arXiv:2106.10190](https://arxiv.org/abs/2106.10190)

---

## Classical Shadows with Improved Median-of-Means Estimation (arXiv:2412.03381)

The paper by **Winston Fu, Dax Enshan Koh, Siong Thye Goh, and Jian Feng Kong** (A*STAR, SUTD, SMU Singapore; 2024) concerns the post-processing: Huang, Kueng, and Preskill chose generous constants in their median-of-means analysis, and in practice constants decide the number of shots. The authors carry over Minsker's optimal constants and his permutation-invariant estimator (a U-statistic over group means) to classical shadows, implement two incomplete U-statistic variants, and compare them numerically on an Ising chain and on GHZ states.

### Placement in the tables

* **Task type:** Estimating, unchanged; the paper changes only the estimator, not the measurement. In the estimating table as the row "Median-of-means constants" next to the classical shadows rows.
* **Object:** state. **Access:** sample, single copies; Pauli or Clifford measurements.
* **Status:** 🟢 🟢 🟢. The modification costs running time $O(k^l\log k)$ for the complete U-statistic and is therefore brought down to $O(m)$ by subsampling (random or cyclic).
* **Promise:** none.

### The problem

The median-of-means bound $\Pr[|\hat\mu - \mu| \geq C\sigma\sqrt{t/N}] \leq 2e^{-t}$ holds in Huang et al. with $C \approx 8$; they set $N = 34\sigma^2 k/\epsilon^2$, $t = k/2$. Minsker showed $C = \sqrt\pi + o(1)$ for the ordinary median of means and $C = \sqrt2 + o(1)$ for a modified estimator that takes the median over all $l$-element subsets of the group means. How much does this gain for shadows, and how does one compute the modified estimator for large data sets?

### Key results

* **Theorem 1 (Minsker, adapted).** $\Pr[|\hat\mu_{\mathrm{MoM}} - \mu| \geq \sigma\sqrt{t/N}] \leq 2\exp(-t/(\pi(1+o(1))))$ for $t$ in a window $[l_{k,N}, u_{k,N}]$, i.e. $C = \sqrt\pi$; the moment condition is trivially satisfied for quantum measurements. The union bound gives $t = \log(2M/\delta)$ and the choice $t = k/\log k$.
* **Theorem 2 (Minsker, U-statistic).** For the median over all $\binom{n}{l}$ means of $l$ group means: bound $3\exp(-t/(2(1+o(1))))$, i.e. $C = \sqrt2$.
* **Two practical implementations.** MomRand draws $m$ random subsets; MomCyc uses cyclic permutations with offsets from a modified Golomb ruler and has better asymptotic relative efficiency at the same $m$.
* **Benchmarks.** Ising chain with 50 qubits, Pauli measurements (tensor networks), two-point function: the plain mean is the most accurate, then the original MoM; the modified estimators exceed their bounds at $3.3\sigma$ and are not suitable here. Noisy GHZ state with Clifford measurements, fidelity: the modified estimators are better than MoM and follow the bounds closely. Purity (quadratic): the mean stays ahead.
* **Table I** (error $\epsilon = 0.1$): shots by the mean bound $80\cdot 10^6$, by the HKP bound $1.3\cdot 10^6$, by the original MoM bound $58\cdot 10^3$, by the new bound $38\cdot 10^3$.
* The independence of the number of shots from $n$ (fidelity of GHZ with $r = 5, 10, 15, 20$) is preserved for all estimators.

### Methodological approach

* Snapshots in $kl$ groups, group means $Z_j$, then the median over means of $l$-subsets; incomplete U-statistics (Lee) with the variance formula $\mathrm{Var}\,U^{(0)} = \sigma_l^2/m + (1-1/m)\mathrm{Var}\,U$ and asymptotic relative efficiency as the selection criterion.
* Evaluation against $3.3\sigma$ limits (failure probability $0.1\%$), so that numerical and theoretical bounds are directly comparable at $\delta = 10^{-3}$.

### Significance and applications

* A saving of a factor 1.5 in the bound relative to the plain median of means with Minsker's constant, and a factor 34 relative to the HKP figure, without any change to the experiment and applicable to existing data sets as well.
* The message that the estimator has to match the measurement ensemble (Pauli: MoM or mean; Clifford: modified MoM) is a useful practical hint; normality of $\hat o_i(N,1)$ from $N \geq 1000$ on is confirmed.

### Relation to this project

* Phase 1 of this project's protocol estimates $|y_{q,p}|^2$ as a mean over the Bell record; the constants of the concentration bound enter the number of Bell samples directly, and this paper shows where the factors between theory and practice lie.
* The observation "the mean beats median of means in practice" is an argument not to compare empirical scaling exponents (such as $\epsilon^{-3.2}$ from the 2025 evaluation) with worst-case estimators.
* The choice of estimator is a degree of freedom that a learned decoder has implicitly; the question whether the CNN learns a median-like or a mean-like estimator is testable.

### Limitations and open questions

* Only two test cases; no theory of why the modified estimators fail for Pauli measurements (Appendix C discusses it).
* The $o(1)$ terms are ignored; the window conditions on $t$ are asymptotic.
* For quadratic functions, Huang et al. use the median of U-statistics; the transfer is not worked out.

### Questions for further study

* What does the concentration of the Bell record statistics look like (multinomial over $d^2$ outcomes), and which MoM variant is optimal there?
* Can a CNN trained on noisy Bell records implicitly adapt the choice of estimator to the noise model, and how would one demonstrate that?
* Where is the boundary between "constants" and "exponents" in this project's scaling analysis when $d$ only goes up to $64$ or $128$?

Paper: [arXiv:2412.03381](https://arxiv.org/abs/2412.03381)

---

## Classical Shadow Tomography with Locally Scrambled Quantum Dynamics (arXiv:2107.04817)

The paper by **Hong-Ye Hu, Soonwon Choi, and Yi-Zhuang You** (UC San Diego, Harvard, Berkeley, MIT; *Phys. Rev. Research* 5, 023027 (2023)) generalizes classical shadows from 2-design ensembles to arbitrary *locally scrambled* ensembles of finite depth: distributions $P(U)$ that are invariant under local basis changes, $P(U) = P(UV) = P(VU)$ for products $V$. The reconstruction map then depends only on the *entanglement feature* of the snapshots, i.e. on the mean purities in all subregions, and shallow circuits as well as Hamiltonian evolutions of real simulators become shadow ensembles with a tunable shadow norm.

### Placement in the tables

* **Task type:** Estimating. Given fidelities or Pauli observables, their values are returned; the novelty is the ensemble. Part of the row "Classical shadows, other ensembles" (shallow and locally scrambled).
* **Object:** state. **Access:** sample, single copies, evolution under a circuit of finite depth or a local Hamiltonian for finite time, then a computational-basis measurement.
* **Status:** 🟢 🟢 🟢 with a caveat: there are $2^N$ reconstruction coefficients $r_A$; they are computed once from the entanglement feature, which is efficient for one-dimensional systems with entanglement feature dynamics and exponential in general.
* **Promise:** local scrambling; approximate scrambling with a controllable bias via the local frame potential.

### The problem

The two limiting cases of Huang, Kueng, and Preskill, global Cliffords for low rank and local Cliffords for local observables, cannot be interpolated, and random circuits are hard to realize on trapped-ion and Rydberg simulators, while a fixed entangling dynamics is easy. What is sought: shadows for the dynamics the hardware provides, with a reconstruction and a sample complexity that do not depend on the details of the dynamics.

### Key results

* **Reconstruction map (Eqs. 7, 9, 12).** For locally scrambled snapshot ensembles, $\sigma = \mathcal{M}[\rho] = \sum_{B,C}d^{2N-|B|}\rho_B\,\mathrm{Wg}_{B,C}W^{(2)}_{\mathcal{E}_\sigma,C}$ with the Weingarten function $\mathrm{Wg}$ and the second entanglement feature $W^{(2)}_{C} = \mathbb{E}\,e^{-S^{(2)}_C(\hat\sigma)}$; the inverse is $\rho = d^N\sum_A r_A\sigma_A$ with coefficients $r_A$ from a linear system with universal fusion coefficients. For on-site 2-designs one obtains $\bigotimes((d+1)\sigma_i - 1)$, for global 2-designs $(d^N+1)\sigma - 1$, i.e. $(d^2+1)\sigma - 1$ in the two-qudit model.
* **Sample complexity (Eqs. 15–23).** The state-dependent shadow norm $\Vert O\Vert^2_{\mathcal{E}_\sigma|\rho}$ is expressed through the third entanglement feature and Weingarten functions over $S_3^N$; the norm averaged over local basis changes, $\Vert O\Vert^2_{\mathcal{E}_\sigma}$, depends only on the entanglement features of the ensemble and of the observable.
* **Two-qudit model.** With the mean single-qudit purity $w$ between $1$ (product state) and $2d/(d^2+1)$ (Page), $r_A$ and the shadow norm interpolate analytically between the two limiting cases; at short times local observables are cheaper, at long times all are equally expensive.
* **Numerics.** Circuits of finite depth and Hamiltonian evolutions of a spin chain modeled on trapped ions and Rydberg arrays; the shallow-circuit measurement achieves a lower tomography complexity than Pauli or Clifford measurements for fidelity and Pauli tasks; a single Hamiltonian suffices for approximate tomography, and the bias falls quickly to a small plateau.

### Methodological approach

* Inserting and averaging local 2-design basis changes $V$ in $\sigma = \mathbb{E}\,V^\dagger\hat\sigma V\,\mathrm{Tr}(V^\dagger\hat\sigma V\rho)d^N$ allows the Weingarten calculation without knowing the dynamics; only purities remain.
* The entanglement feature is either computed from the definition by sampling the prior ensemble or, for unknown experimental ensembles, estimated from Rényi entropy measurements; in 1D there are efficient entanglement feature dynamics.
* The local frame potential quantifies the deviation from exact scrambling and hence the bias.

### Significance and applications

* Opens shadows to analog simulators; shallow shadows (Bertoni et al.) emerged in parallel and independently, and the classification via entanglement features is the more general one.
* The statement that the reconstruction map depends only on purities is a structural result about measurement channels with local symmetry; Ippoliti uses it for Bell and GHZ bases.
* The relation shadow norm $\leftrightarrow$ entanglement feature turns the choice of ensemble into an optimization problem over the entanglement of the measurement basis.

### Relation to this project

* The Bell measurement on two copies is a fixed, non-random measurement basis; the paper shows how to treat a fixed entangling dynamics as a shadow ensemble anyway, by scrambling locally. The question whether Bell sampling on $\rho\otimes\rho^*$ preceded by local qudit Cliffords becomes a locally scrambled two-copy ensemble connects directly.
* The entanglement feature as the only relevant characteristic is a candidate for the factor "mixedness/entanglement" of this project's taxonomy: it is measurable and determines the cost.
* The $2^N$ coefficients $r_A$ are an example of "memory exponential, but only once"; this project's coprime folding has the same structure, only with $d^2 \to 64\times 64$.

### Limitations and open questions

* $2^N$ reconstruction coefficients in general; efficient only with additional structure.
* The bias of approximately scrambled ensembles is controlled numerically, not rigorously.
* No lower bounds; whether shallow ensembles are optimal for a class of observables is open.
* Qudits are formally included, examples only for qubits.

### Questions for further study

* What does the entanglement feature of the transversal Bell basis on $\rho\otimes\rho^*$ look like if both copies are read as one $2$-qudit system?
* Can the Weingarten calculation for $U(d)^N$ twirls be carried over to the Heisenberg–Weyl group of a single qudit, where there is no $N$?
* How does the shadow norm of a displacement operator $D_{q,p}$ depend on the duration of a Hamiltonian evolution that runs before the measurement?

Paper: [arXiv:2107.04817](https://arxiv.org/abs/2107.04817)

---

## Classical shadows based on locally-entangled measurements (arXiv:2305.10723)

The paper by **Matteo Ippoliti** (UT Austin, Stanford; *Quantum* 2024) moves the entanglement from the copies into the measurement basis: instead of measuring each qubit individually in a random Pauli basis, pairs of neighboring qubits *within one copy* are measured in the Bell basis. For Pauli operators compatible with the dimer covering, the shadow norm drops quadratically from $3^k$ to $3^{k/2}$; other operators become unlearnable. A family between Pauli and Bell bases is tomographically complete and keeps part of the gain, and $n$-qubit GHZ bases reach $(3/2)^k$, optimal among stabilizer measurements.

### Placement in the tables

* **Task type:** Estimating. Given a list of Paulis, their values are returned; the paper is about the measurement basis. New row "Classical shadows, locally entangled bases" of the estimating table.
* **Object:** state. **Access:** sample, single copies. Important for the tables: the Bell measurement here is *not* the two-copy Bell measurement of the memory axis, but a two-qubit measurement on one copy; the quantum memory stays one.
* **Status:** 🟢 🟢 🟢 for compatible operators; post-processing is a product over dimers.
* **Promise:** compatibility with the chosen dimer covering: the support intersects every dimer in $0$ or $2$ sites. This is a promise about the observables, not about the state.

### The problem

Random Pauli measurements cost $3^k$ shots for weight $k$, and this is information-theoretically optimal *in general*. One can, however, trade accuracy on one class of operators for unlearnability on another; shallow shadows do this via circuit depth, with $\sim k2^k$ for contiguous supports. Is there a trade that is gentler on hardware, with only two-qubit entanglement?

### Key results

* **Bell shadows (Section 2).** Scramble locally, measure pairs in the Bell basis, standard reconstruction. The measurement channel factorizes into two-qubit channels with eigenvalues $\lambda_{\circ\circ} = 1$, $\lambda_{\circ\bullet} = \lambda_{\bullet\circ} = 0$, $\lambda_{\bullet\bullet} = 1/3$; hence $\Vert P\Vert_{\mathrm{sh}}^2 = 3^{k/2}$ for compatible $P$ and zeros otherwise (not tomographically complete). It suffices to scramble one qubit per dimer (gate teleportation). $10^{N/2}$ of the $4^N$ operators are compatible.
* **Use cases (2.3).** String operators of even length in 1D with two dimer coverings: $2\ln(M/2)3^{k/2}/\epsilon^2$ instead of $\ln M\,3^k/\epsilon^2$; hexagonal plaquettes (color code stabilizers): prefactor $54$ instead of $729$; $p$-point functions of two-body terms: $3^p$ instead of $9^p$.
* **General two-qubit bases (Section 3).** With CPhase($\phi$) instead of CZ, the channel is deformed via $\delta = \ln 2 - S_2^a$: $\lambda_{\bullet\circ} \simeq \delta/3$, $\lambda_{\bullet\bullet} \simeq 1/(3+2\delta)$, tomographically complete for $\delta > 0$, shadow norm $\simeq(3+2\delta)^{|A|/2}(\sqrt3/\delta)^{c_A}$ with $c_A$ the number of cut dimers. At $\delta = \ln(11/8)$, $\Vert P\Vert^2_{\mathrm{sh}} = 4^{k\bmod 2}\cdot 2^k$, which beats shallow shadows ($k2^k$) from $k \gtrsim 4$ on. For supports with "holes" of density $\rho$, entanglement helps above a threshold $\rho^*(\delta)$, against shallow shadows from $\rho^* \gtrsim 0.945$ on.
* **GHZ bases (Section 4).** $n$-qubit GHZ bases are optimal among stabilizer measurements for compatible operators: $\Vert P\Vert^2_{\mathrm{sh}} = f_n^k$ with $f_2 = \sqrt3$, $f_3 = 3/2^{2/3}$, $f_n \to 3/2$; the bound $(3/2)^k$ follows from the fact that a basis hits at most $2^n$ of the $3^n$ full-weight operators; GHZ maximizes the number of fully supported stabilizers (Shor–Laflamme weight distribution).

### Methodological approach

* Local scrambling makes the channel Pauli-diagonal; the eigenvalues follow from the entanglement feature of the measurement basis (Hu, Choi, You; Bertoni et al.): $\lambda_A = (-1/3)^{|A|}\sum_{B\subseteq A}(-2)^{|B|}P^B$ with $P^B$ the mean subsystem purity of the basis states.
* Basis counting argument: per dimer, $3$ of the $9$ two-qubit operators are measured (two explicitly, the third as their product), hence a hit probability of $3^{-k/2}$.
* For typical operators with holes, the geometric average $e^{\mathbb{E}\ln\Vert P\Vert^2}$ is used, because the shadow norm fluctuates over orders of magnitude.

### Significance and applications

* A hardware-cheap replacement for shallow shadows for string operators, plaquettes, and correlation functions; Table 1 of the paper ranks Pauli, Bell, deformed, and GHZ shadows by scaling and learnability.
* Shows that "Bell measurement" can mean two quite different things: across two copies (memory axis) or across two qubits of one copy (choice of basis). Only the first sees the Pauli spectrum globally.

### Relation to this project

* The conceptual clarification matters for this project's paper: Bell measurements *within* one copy give $3^{k/2}$ and remain at the single-copy wall of Theorem 2 in Huang et al.; Bell measurements *across* $\rho\otimes\rho^*$ give $O(\log d/\epsilon^4)$ for all $d^2$ amplitudes. The resource is the second state, not the entangling gate.
* The idea "trade accuracy on one class for unlearnability on another" is a template for measurement bases tailored to a promise class; a dictionary regime could choose a basis that sees only the dictionary addresses.
* The bound $(3/2)^k$ via "at most $2^n$ of $3^n$ operators per basis" is a counting argument that could be carried over to the $d^2$ displacement addresses of a qudit.

### Limitations and open questions

* Bell shadows are tomographically incomplete; the deformed family pays with worse asymptotics.
* GHZ bases need depth linear in $n$ or many ancilla qubits; behavior under noise is open.
* Pauli observables only; the extension to non-Pauli observables is not worked out.
* Qudits are not treated.

### Questions for further study

* What is the qudit version: measurement in the basis of joint eigenvectors of $X\otimes X^\dagger$ and $Z\otimes Z^\dagger$ on two qudits of one copy, and which displacement operators are then "compatible"?
* How does the shadow norm of the deformed basis behave if it is applied to $\rho\otimes\rho^*$ with the dimers placed across the copies?
* Is the Shor–Laflamme optimality of GHZ a special case of a statement about maximal supports in a coset, which also holds for stabilizer supports in the displacement spectrum?

Paper: [arXiv:2305.10723](https://arxiv.org/abs/2305.10723)

---
## Matchgate Shadows for Fermionic Quantum Simulation (arXiv:2207.13723)

The paper by **Kianna Wan, William J. Huggins, Joonho Lee, and Ryan Babbush** (Google Quantum AI, Stanford, Columbia, Harvard; *Commun. Math. Phys.* 404, 629 (2023)) analyzes classical shadows from random matchgate circuits, i.e. fermionic Gaussian unitaries. Main theorem: the first three moments of the Haar distribution on the continuous matchgate group $\cong O(2n)$ coincide with those of the discrete subgroup of Clifford matchgates (signed permutations), a "matchgate 3-design". From this follow efficient estimators for local fermionic observables, fidelities with Gaussian states, and overlaps with Slater determinants, which removes the exponential post-processing step in the hybrid QC-AFQMC algorithm.

### Placement in the tables

* **Task type:** Estimating. Given local fermionic operators $\gamma_S$, Gaussian density operators $\varrho$, Slater determinants $|\varphi\rangle$; returned are $\mathrm{tr}(\gamma_S\rho)$, $\mathrm{tr}(\varrho\rho)$, $\langle\psi|\varphi\rangle$. Row "Classical shadows, other ensembles (fermionic and matchgate)".
* **Object:** state of an $n$-mode fermionic system, via Jordan–Wigner as $n$ qubits. **Access:** sample, single copies, random matchgate circuit, computational-basis measurement.
* **Status:** 🟢 🟢 🟢. Variance $\sim n^{|S|/2}$ for local observables, constant or sublinearly growing for Gaussian fidelities and overlaps; post-processing in $O(n^3)$ via Pfaffians.
* **Promise:** parity: the measurement channel has image $\Gamma_{\mathrm{even}}$, so the state or the observables must be even operators. Physically this is almost always the case.

### The problem

Huggins et al. had implemented QC-AFQMC with Clifford shadows: the trial state is prepared on the quantum computer, shadows are collected, and the overlaps $\langle\Psi_{\mathrm{trial}}|\varphi_i\rangle$ with the Slater determinants of the Monte Carlo run are evaluated classically. The variance is constant, but evaluating $\langle b|U|\varphi_i\rangle$ with Clifford $U$ needs exponentially fine precision and scales exponentially. What is sought: an ensemble whose shadows deliver fermionic quantities efficiently and with polynomial variance.

### Key results

* **Theorem 1 (three moments).** $\mathcal{E}^{(j)}_{M_n} = \mathcal{E}^{(j)}_{M_n\cap\mathrm{Cl}_n}$ for $j = 1, 2, 3$, with explicit expressions via projectors $|\Upsilon^{(2)}_k\rangle\!\rangle$ and $|\Upsilon^{(3)}_{k_1k_2k_3}\rangle\!\rangle$ in the Liouville representation. Corollary 1: the Clifford matchgates form a matchgate 3-design. The matchgate group has $2n+1$ inequivalent irreps, compared with a single nontrivial one for the Clifford group.
* **Measurement channel (Eqs. 30, 32).** $\mathcal{M} = \sum_\ell\binom{n}{\ell}\binom{2n}{2\ell}^{-1}\mathcal{P}_{2\ell}$ with $\mathcal{P}_k$ the projector onto products of $k$ Majoranas; the inverse is given by the reciprocals of the coefficients on $\Gamma_{\mathrm{even}}$.
* **Variance (Eqs. 33–36).** Explicit formula with coefficients $\alpha_{\ell_1\ell_2\ell_3}$; thanks to the symmetry, the Majorana basis may be chosen freely.
* **Local fermionic observables.** $\mathrm{tr}(\tilde\gamma_S\mathcal{M}^{-1}(U_Q^\dagger|b\rangle\langle b|U_Q)) = \binom{2n}{|S|}\binom{n}{|S|/2}^{-1}\mathrm{pf}(i(Q'Q^TC_{|b\rangle}QQ'^T)|_S)$, variance $\leq\binom{2n}{|S|}\binom{n}{|S|/2}^{-1}\sim n^{|S|/2}$; the same scaling as Zhao, Rubin, Miyake, but in an arbitrary basis.
* **Theorem 2 (Gaussian density operators).** $\mathrm{tr}(\varrho_1\mathcal{P}_{2\ell}(\varrho_2))$ is the coefficient of $z^\ell$ in $2^{-n}\mathrm{pf}(C_{\varrho_1})\mathrm{pf}(-C_{\varrho_1}^{-1} + zC_{\varrho_2})$; all coefficients in $O(n^3)$ (Appendix D). Variance polynomially bounded; for Gaussian density operators $O(\sqrt n\log n)$ (Appendix F).
* **Overlaps with Slater determinants.** Via $\rho = \frac12(|0\rangle + |\psi\rangle)(\langle 0| + \langle\psi|)$ and $\langle\psi|\varphi\rangle = 2\,\mathrm{tr}(|\varphi\rangle\langle 0|\rho)$; an efficiently computable variance bound, evaluated up to 1000 qubits with sublinear growth. Algorithm 1 summarizes the QC-AFQMC protocol.
* **General framework** for products of local fermionic operators, Gaussian density operators, and Gaussian unitaries, including overlaps with arbitrary pure Gaussian states, without a variance bound.

### Methodological approach

* Explicit twirl channels via the representation theory of $O(2n)$ on the Clifford algebra of the Majoranas; the equality of the moments for the discrete subgroup is shown by direct comparison of the expressions.
* Pfaffian identities from Wick's theorem; for Theorem 2 an elementary approach via the Clifford algebra structure that extends to the overlap case, where summation formulas are missing.
* Sampling of the ensembles in Appendix B; the question of $n^2/\log n$ gates for Cliffords disappears, since matchgates are linear optics for fermions.

### Significance and applications

* Makes QC-AFQMC polynomial in the post-processing; the authors extend the reach of shadows to global fermionic quantities that are neither local nor low-rank in the qubit sense.
* The matchgate 3-design is a structural result with applications beyond shadows; Heyraud, Chomet, and Tilly generalize it to $SO(2n)$ and unify all matchgate ensembles.
* For $k$-body fermionic observables with single copies, $\Omega(n^k/\epsilon^2)$ is necessary (King, Gosset, Kothari, Babbush, Theorem 3); matchgate shadows reach this up to logarithms and are therefore the single-copy reference for the fermionic two-copy row.

### Relation to this project

* The Gaussian unitaries are the fermionic counterpart of the displacement operators: a group with explicit representation theory whose twirls can be computed in closed form. The paper is the template for how to *compute* a shadow norm for a structured operator group instead of estimating it.
* The variance $n^{|S|/2}$ is a "locality in the Majorana basis" that differs from Pauli locality; this is the example showing that the notion "local" depends on the basis in which the spectrum is read, just as for Heisenberg–Weyl versus Pauli.
* The trick of writing overlaps as expectation values via the state $\frac12(|0\rangle + |\psi\rangle)(\dots)$ is a single-copy way around the Hadamard test and thus a model for Phase 2, where signs are obtained from expectation values on $\rho\otimes\sigma^*$ instead of from controlled operations.

### Limitations and open questions

* Variance bounds are missing for the general framework (products of Gaussian objects).
* The overlap variance is controlled only numerically, up to 1000 qubits; an analytic $O(\mathrm{poly}(n))$ is missing.
* Even operators only; odd sectors need additional constructions (Appendix A).
* Robustness to noise is not treated.

### Questions for further study

* Why does the matchgate group have $2n+1$ irreps on $L(\mathcal{H}_n)$, and what structure does the Heisenberg–Weyl group of a qudit have in comparison?
* Can Theorem 2 (a polynomial in $z$ from two Pfaffians) be carried over to overlaps between Gaussian states in the displacement representation, where covariance matrices are replaced by characteristic functions?
* What is the two-copy matchgate shadow: a Bell measurement on $\rho\otimes\rho$ in the Majorana basis, and does it see the whole fermionic spectrum?

Paper: [arXiv:2207.13723](https://arxiv.org/abs/2207.13723)

---

## Unified Framework for Matchgate Classical Shadows (arXiv:2409.03836)

The paper by **Valentin Heyraud, Héloise Chomet, and Jules Tilly** (InstaDeep Paris and London; 2024) tidies up the zoo of fermionic shadow ensembles. Zhao, Rubin, and Miyake used signed permutations, Wan et al. the full group $O(2n)$, O'Gorman perfect matchings; the $SO(2n)$ ensemble was unanalyzed, and the relation between the protocols unclear. The paper introduces *Clifford 3-cubatures*, shows that the $SO(2n)$ ensemble is one, proves the equivalence of all the protocols mentioned, and derives from this a gate-optimal sampling scheme.

### Placement in the tables

* **Task type:** Estimating, the same task type as in Wan et al.; the paper changes only the choice of ensemble. Entry in the row "Classical shadows, other ensembles".
* **Object:** fermionic state. **Access:** sample, single copies, matchgate circuits built from independent random Pauli rotations.
* **Status:** 🟢 🟢 🟢, with the variances of Wan et al. and fewer gates.
* **Promise:** as in Wan et al.

### The problem

The measurement channel depends on the 2-fold twirl, the variance on the 3-fold twirl; ensembles with the same first three moments are equivalent for shadows. Wan et al. had shown this for $O(2n)$ versus its Clifford subgroup and left the question for $SO(2n)$ open; Zhao and Miyake had noted the gap. In addition, the discrete ensembles seemed to single out a preferred Majorana basis, and the relation between the variances of different subensembles was only partially known.

### Key results

* **Lemma 1.** For a Pauli rotation $R_\theta = e^{-i\theta Z/2}$ with angle $\theta$ drawn from a distribution $\nu$ that is symmetric about the Clifford angles, $\mathbb{E}\,\mathcal{R}_\theta^{\otimes 3} = \frac{1-p}{2}(\mathcal{I}^{\otimes 3} + \mathcal{Z}^{\otimes 3}) + \frac p2(\mathcal{S}^{\otimes 3} + \mathcal{S}^{\dagger\otimes 3})$: the third twirl of a random rotation is a convex combination of Clifford twirls.
* **Theorem 1.** Every ensemble of matchgate circuits with fixed architecture and independent rotations whose angle distributions satisfy the symmetry has the same first three moments as its Clifford subensemble: a Clifford 3-cubature. In particular, the $SO(2n)$ ensemble $M_n^+$ is a Clifford 3-cubature, and Proposition 2 generalizes the matchgate 3-design of Wan et al. to $M_n^+\cap\mathrm{Cl}_n$.
* **Propositions 3 and 4 (equivalences).** The variances of the shadow estimators are invariant under reflections at Majorana operators (inserting signs, $Q = DQ'$), and ensembles whose permutations correspond to the same perfect matching give the same variances. Hence the protocols of Zhao et al., Wan et al., and O'Gorman are equivalent.
* **Proposition 5 / Algorithm 1.** A sampling scheme over perfect matchings that is optimal in the gate count (Givens rotations) and inherits the guarantees of the full ensembles.
* Numerical comparison of the schemes; the authors expect applications of the cubature results in randomized benchmarking and variational algorithms.

### Methodological approach

* Decomposition of $SO(2n)$ elements into Givens rotations of neighboring axes, which under Jordan–Wigner are two-qubit $XX$ rotations and single-qubit $Z$ rotations; the twirl channels of the rotations are decomposed into Clifford channels via Lemma 1, and convexity carries over to products.
* The equivalence proofs use the invariances of the 3-fold twirl and the structure of the generalized symmetric group $\mathbb{Z}_2\wr\mathrm{Sym}(2n)$.

### Significance and applications

* Answers the open question of Wan et al. in the affirmative and turns the choice of ensemble into a pure hardware question: one takes the one with the fewest gates.
* The cubature view (instead of the design view) is more general: it holds for angle distributions, not only for groups, and places results such as the Clifford 2-cubatures of earlier work in context.

### Relation to this project

* The message "the moments decide, not the ensemble" also holds for the Bell measurement on $\rho\otimes\rho^*$: two two-copy measurement bases with the same first three moments are indistinguishable for questions about magnitudes and variances. This is a criterion for evaluating variants of this project's measurement (for instance with local qudit Cliffords applied beforehand) without a new analysis.
* The invariance under reflections is the fermionic counterpart of the question whether $D_{q,p}$ and $D_{-q,p}$ (i.e. $D$ and $D^T$) are equivalent for the statistics; for $\rho\otimes\rho$ versus $\rho\otimes\rho^*$, that is exactly the difference.
* Gate-optimal sampling schemes are the factor "hardware realism" on the measurement side.

### Limitations and open questions

* The cubature holds for circuits with fixed architecture; approximate ensembles of sublinear depth give only approximate twirls, and an estimator for them is unclear.
* No new variance bounds, only equivalences.
* The connection to random phylogenetic trees (random perfect matchings) is mentioned as an outlook.

### Questions for further study

* What does Lemma 1 look like for qudit rotations $e^{-i\theta Z}$ with $Z$ the clock operator, and which angle distributions give qudit Clifford cubatures?
* Is there a cubature statement for the transversal Bell measurement with random local Cliffords applied beforehand on both copies?
* Is the perfect-matching scheme the fermionic analogue of Ippoliti's dimer covering, and what connects the two counting arguments?

Paper: [arXiv:2409.03836](https://arxiv.org/abs/2409.03836)

---

## The Magic in Qudit Shadow Estimation based on the Clifford Group (arXiv:2410.13572)

The paper by **Chengsi Mao, Changhao Yi, and Huangjun Zhu** (Fudan; 2024, with a companion paper on third moments of Clifford orbits) settles the sample complexity of shadow estimation on qudits of odd prime dimension $d$. The qudit Clifford group is only a 2-design, and the stabilizer states deviate from a 3-design in the third moment exponentially in $n$; nevertheless the overhead relative to qubits is only $O(d)$, independent of $n$. A layer of a few T gates, even a single one, removes the overhead and makes fidelity estimation independent of $d$ and $n$.

### Placement in the tables

* **Task type:** Estimating. Given fidelities with stabilizer projectors, Weyl observables, general traceless operators; their values are returned with a shadow norm guarantee. New row "Classical shadows on qudits" of the estimating table; at the same time the qudit continuation of the Clifford row of Huang, Kueng, Preskill.
* **Object:** $n$-qudit state, $d$ an odd prime, $D = d^n$. **Access:** sample, single copies, local or global qudit Cliffords, optionally followed by $k$ T gates with Fourier gates.
* **Status:** 🟢 🟢 🟢 for observables of bounded Hilbert–Schmidt norm; simulating one shot costs $O((n+t)^3 + t\,d^{t+1})$ with $t$ magic gates.
* **Promise:** bounded Hilbert–Schmidt norm (global) or $m$-locality (local).

### The problem

Qubit shadows rely on the 3-design property of the Clifford group. For $d$ an odd prime, $\mathrm{Cl}(n,d)$ is not a 3-design, and the shadow norm of generic observables was unknown, although qudit processors (photons, ions, transmons) exist. How expensive is qudit shadow estimation, and can the missing design property be retrofitted cheaply?

### Key results

* **Local Cliffords (Proposition 1, Theorem 1).** For $m$-local Weyl operators $\Vert O\Vert^2_{\mathrm{sh}} = (d+1)^m$; for $m$-local operators in general $\leq d^m\Vert\tilde O\Vert_2^2$. Reconstruction $\bigotimes_j((d+1)U_j^\dagger|b_j\rangle\langle b_j|U_j - I)$.
* **Global Cliffords (Theorem 2).** $\Vert O\Vert_2^2 \leq\Vert O\Vert^2_{\mathrm{sh}} \leq (2d-3)\Vert O\Vert_2^2 + 2\Vert O\Vert_\infty^2$ for traceless $O$; diagonal in a stabilizer basis $\leq (d-1)\Vert O\Vert_2^2 + d\Vert O\Vert_\infty^2$; for $n = 1$ and diagonal exactly $(d+1)\Vert O\Vert_\infty^2$. The ratio $\Vert O\Vert^2_{\mathrm{sh}}/\Vert O\Vert_2^2 \leq 2d-1$ is independent of $n$, although the operator norm of the third normalized moment operator of $\mathrm{Stab}(n,d)$ grows exponentially for $d \neq 2 \bmod 3$.
* **Theorem 3.** For stabilizer projectors of rank $K$: $\Vert O_0\Vert^2_{\mathrm{sh}}/\Vert O_0\Vert_2^2 = \frac{D+1}{D+d}(d-1-\frac dD + \frac dK)$: linear in $d$, practically independent of $n$ from $n \geq 5$ on. Stabilizer states are the hardest observables for stabilizer measurements.
* **Theorem 4 (magic).** With a Clifford followed by $k$ T gates (diagonal gates of the third level of the Clifford hierarchy, $\omega^{f(b)}$ with cubic $f$), $\Vert O_0\Vert^2_{\mathrm{sh}} \leq\gamma_{d,k}\Vert O_0\Vert_2^2$ with $\gamma_{d,k} = 3 + 2^{k+1}/(d(d-2)^k)$ for $d \neq 1 \bmod 3$ and a formula of the same form otherwise; $\gamma_{d,k}$ converges exponentially in $k$ to the 3-design value $3$, and already $k = 1$ removes the factor $d$.
* **Numerics.** GHZ with $n = 100$: without T gates, the slope of $1/\langle\epsilon^2\rangle$ against $N$ is roughly $\propto 1/d$; with one T gate, the ratio of the slopes is at most 3 across all $d$. A duality: the MSE depends on the total number of T gates in preparation *and* measurement. Depolarized GHZ fidelity estimated well with 5000 samples; the spread decreases with $k$.

### Methodological approach

* Third moments of Clifford orbits, in particular of stabilizer and magic states, from the companion paper; the key is that the shadow norm does not need the operator norm of the moment operator, only certain matrix elements.
* For the simulation: a generalized tableau representation and gadgetization of the T gates on qudits, combined with Clifford sampling.

### Significance and applications

* Verification of qudit systems is easier than feared; a single magic gate closes the gap to qubits, a new use case for "a little magic as a resource".
* Shows that ensembles far from 3-designs (by the usual measure) can be just as good for shadows; the measure "distance to a 3-design" is the wrong one for shadows.

### Relation to this project

* This is the single-copy reference *on qudits*: for a single qudit ($n = 1$), the stabilizer-basis measurement is a complete set of MUBs, and the shadow norm of a displacement operator carries the factor $d+1$ (Eq. 11). Together with Theorem 31 in King, Wan, McClean ($\Omega(d)$ variance for displacements), this is the $\Omega(d/\epsilon^2)$ wall that conjugate pairs get around.
* T gates in the measurement are a new degree of freedom that is missing in Bell measurements: whether a magic gate before the Bell measurement makes the distribution over the $d^2$ addresses more uniform or more informative is open and testable.
* The observation "stabilizer states are the hardest for stabilizer measurements" is the mirror image of Montanaro's plateau: where all coefficients have magnitude one, localization is easy and estimation is hard.

### Limitations and open questions

* Odd primes $d$ only; composite $d$ ($\mathbb{Z}_d$ not a field) is left out, and that is exactly the case that matters for this project.
* Theorem 2 is an upper bound; for generic observables the actual norm is often much smaller and independent of $d$ (Fig. 2).
* The exact form of $\gamma_{d,k}$ for $d = 1 \bmod 3$ is a different formula; details in the companion paper.
* Noise and error mitigation are not treated.

### Questions for further study

* What does Theorem 2 look like for $d = 4, 6, 8, 9$, where $\mathbb{Z}_d$ is not a field and the Clifford group has a different structure?
* What is the shadow norm of $D_{q,p}$ under the Clifford-plus-T ensemble, and does the factor $d$ disappear there as well?
* Is there a two-copy analogue of the T-gate duality, i.e. a relation between the magic of the state and the information content of a Bell sample?

Paper: [arXiv:2410.13572](https://arxiv.org/abs/2410.13572)

---

## Classical shadows over symmetric spaces (arXiv:2605.05518)

The paper by **Rebecca Chang, Maureen Krumtünger, Martín Larocca, and Maxwell West** (MIT, Los Alamos, Melbourne, Oak Ridge; 2026) drops the assumption that the shadow ensemble is a group: it studies ensembles drawn uniformly from the seven infinite families of compact symmetric spaces of type I, quotients $G/K$ of the unitary, orthogonal, and symplectic groups by the fixed-point sets of an involution. The result is a unified theory: the measurement channel is a convex combination of the channel of the parent group, a dephasing channel, and, for symplectic $G$, a subleading term; for observables concentrated on the preferred basis there are slight improvements.

### Placement in the tables

* **Task type:** Estimating; again the novelty is the ensemble. Entry in the row "Classical shadows, other ensembles".
* **Object:** state. **Access:** sample, single copies, $U \sim G/K$ realized as $\sigma(g)^{-1}g$ with $g \sim G$.
* **Status:** 🟢 🟢 🟢; inverting the channel is trivial because the decomposition is multiplicity-free.
* **Promise:** none about the state; a gain occurs only for observables with weight on the diagonal of the measurement basis $W$.

### The problem

Shadows over compact groups are well understood via Schur's lemma: the channel is $G$-equivariant and decomposes according to irreps. Symmetric spaces are not groups, the channel is no longer equivariant under all coset representatives, and it was unclear whether anything systematic can be said. Motivation: symmetric spaces play a role in compilation (Cartan decompositions), and the induced distributions on $G$ are non-uniform, hence possibly easier to adapt to classes of observables.

### Key results

* **Lemma 1.** The channel $\mathcal{M}_{G/K,W}$ commutes with the adjoint action of every subgroup $H \subseteq K\cap N_W$ ($N_W$ the elements normalizing $W$), hence it decomposes according to $H$-irreps; in all cases multiplicity-free, and the $s_\lambda$ are real numbers.
* **Theorem 1.** $\mathcal{M}_{G/K,W}(\rho) = (1-\alpha)\mathcal{M}_{G,W}(\rho) + \beta\mathcal{A}_W(\rho) + (\alpha-\beta)(J\mathcal{A}_W(\rho)J^\dagger - \mathcal{A}_W(\rho J)J)$, with $\mathcal{A}_W$ the dephasing channel in $W$ and $J$ the symplectic form. For AI, AII, CI, DIII, $\alpha = O(d^{-2})$, so practically of no interest; for AIII, BDI, CII, $0 \leq\alpha\leq 1$ is tunable via the signature $s$ of the involution. $\alpha = \beta$ except for $G = SP$, where $|\alpha - \beta| = O(1/d)$. Table I gives $\alpha_{G/K}$ for all seven families.
* **Consequences.** The channels inherit the image of the parent channel, hence the same set of observables that can be estimated without bias; the variance depends on the 2-norm of the projection of the observable onto the diagonal subspace; at $d = 128$, AIII and BDI show slight improvements over unitary and orthogonal when the observables are strongly concentrated on the diagonal. AIII and CII agree to leading order, because symplectic ensembles are state $k$-designs for all $k$.
* **Sampling.** 6-designs over the parent groups suffice; for the unitary group in logarithmic depth, for the orthogonal and symplectic groups not in sublinear depth (no-go theorems).

### Methodological approach

* Second-order twirls over $G/K$ as fourth-order twirls over $G$ (Weingarten calculus on $U$, $O$, $SP$; for BDI $(11!!)^2$ terms), or directly via Matsumoto's Weingarten calculus for symmetric spaces. Theorem 1 makes the full calculation unnecessary: two unknowns are determined from a few matrix elements.
* The sampling rule $\sigma(g)^{-1}g$ (Duenez, Matsumoto) is left-$K$-invariant.

### Significance and applications

* Completes the theory of shadows over the classical compact groups and their symmetric spaces; the group cases (unitary: HKP; orthogonal: West et al. "real shadows"; symplectic: West et al. 2024) are special cases.
* The outlook names general representations, for instance DIII with $SO$ as the matchgate group, where $SO(2n)/U(n)$ is the manifold of pure Gaussian states: a bridge to the matchgate papers.

### Relation to this project

* The ensemble view "convex combination of the parent channel and dephasing" also describes Bell measurements with imperfect gates: a noise channel before the Bell basis acts like dephasing in the Bell basis, and the formula says how the reconstruction changes. This is relevant for the factor "hardware realism" of this project's taxonomy.
* The observation that a preferred basis helps only on the diagonal hints at why the Heisenberg–Weyl spectrum as a *whole* has no preferred single-copy basis: every displacement address is equally poorly visible in every stabilizer basis.
* The Cartan structure is the tool with which one could ask whether $\rho\otimes\rho^*$ is a point in a symmetric space (conjugation is an involution) and what that means for twirls across the copies.

### Limitations and open questions

* The improvements are constant and small; the paper is primarily structural.
* The operators $s_\lambda$ are not identified directly from representation theory; for groups there are simple formulas, for symmetric spaces there are not.
* Defining representations only; general representations are an outlook.

### Questions for further study

* Is the map $\rho \mapsto \rho^*$ an involution whose fixed-point set (real states) defines a symmetric space, and what is the corresponding shadow channel on $\rho\otimes\rho^*$?
* What does Theorem 1 look like for the Heisenberg–Weyl group as a subgroup of $U(d)$, and which involutions respect it?
* Can the dephasing part $\beta\mathcal{A}_W$ be used as a model for readout errors in the Bell basis, and how does the required correction scale with $d$?

Paper: [arXiv:2605.05518](https://arxiv.org/abs/2605.05518)

---

## Triply efficient shadow tomography (arXiv:2404.19211)

The paper by **Robbie King, David Gosset, Robin Kothari, and Ryan Babbush** (Google Quantum AI, Caltech, Waterloo, Perimeter; *PRX Quantum* 6, 010336 (2025)) defines *triple efficiency*: sample-efficient ($\mathrm{poly}(\log|S|, 1/\epsilon)$), computationally efficient ($\mathrm{poly}(|S|, n, 1/\epsilon)$), and with measurements on a constant number of copies at a time, with total memory $O(n)$. It gives the first triply efficient protocols for all $4^n$ Paulis and for $k$-body fermionic observables, both with two-copy Clifford measurements, and shows that two-copy measurements are necessary for this. The framework: Bell sampling reduces the problem to fractional coloring of an induced subgraph of the commutation graph with bounded clique number.

### Placement in the tables

* **Task type:** Estimating. Given a set $S$ of Paulis, all $\mathrm{Tr}(P\rho)$ are returned; for $S = \mathcal{P}^{(n)}$ this is the row "All $4^n$ Pauli observables, two-copy", for $S = \mathcal{F}_k^{(n)}$ the fermionic row.
* **Object:** state. **Access:** sample; Bell measurement on $\rho\otimes\rho$ for the magnitudes (rung 1, quantum memory two), then single-copy Clifford measurements guided by a coloring.
* **Status:** 🟢 🟢 🟢 in the sense of the definition. ⚠️ Correction to the table: for all Paulis the running time is $\mathrm{poly}(2^n, 1/\epsilon)$ (Theorem 7), i.e. $\mathrm{poly}(|S|)$ with $|S| = 4^n$, not $\mathrm{poly}(n)$; only the query of one Pauli expectation value from the compressed representation is polynomial in $n$ (Corollary 12). The row has been adjusted accordingly.
* **Promise:** two-copy memory as a resource; no promise about the state.

### The problem

General shadow tomography is exponential in running time and needs entangled measurements across many copies. Classical shadows are triply efficient for $k$-local Paulis but fail at high weight. Huang, Kueng, and Preskill (2021) learn arbitrary sets of Paulis with $O(\log|S|/\epsilon^4)$ copies and $\mathrm{poly}(|S|)$ time, but need gentle measurements on many copies for the signs. For $k$-body fermionic observables and for all Paulis, sample-efficient single-copy tomography is impossible (Theorem 2 from Chen, Cotler, Huang, Li; Theorem 3, new: $\Omega(n^k/\epsilon^2)$). Are there triply efficient protocols with two copies?

### Key results

* **Theorem 5 (single copies via fractional coloring).** If the commutation graph $G(S)$ has a samplable fractional coloring of size $\chi$, then all $\mathrm{Tr}(P\rho)$ can be learned with $O(\chi\log|S|/\epsilon^2)$ single-copy Clifford measurements; the Pauli shadows of HKP are the case $\chi = 3^k$.
* **Theorem 6 (two copies, any set $S$).** $O(\log|S|/\epsilon^4)$ two-copy measurements: Bell sampling gives $|\mathrm{Tr}(P\rho)|$ to within $\epsilon/4$ and defines $S_\epsilon = \{P: u_P \geq 3\epsilon/4\}$; a *mimicking state* $\sigma$ with $|\mathrm{Tr}(\sigma P)| \geq\epsilon/4$ on $S_\epsilon$ exists ($\rho$, for instance) and is found by brute force without further copies; Bell sampling on $\rho\otimes\sigma$ gives $\mathrm{Tr}(P\rho)\mathrm{Tr}(P\sigma)$ and hence the signs. Sample-efficient, computationally absurd.
* **Theorem 7 (all Paulis, triply efficient).** $O(n\log(n/\epsilon)/\epsilon^4)$ samples, time $\mathrm{poly}(2^n, 1/\epsilon)$: the mimicking state is computed via matrix multiplicative weights with additional single-copy measurements and prepared with $O(4^n)$ gates.
* **Lemma 8.** With high probability, the largest clique in $G(S_\epsilon)$ has at most $4/\epsilon^2$ vertices: anticommuting observables cannot all be large at the same time (uncertainty).
* **Lemma 9 and Theorem 10 ($k$-body fermions).** Induced subgraphs of $G(\mathcal{F}_k^{(n)})$ are $\chi$-bounded with a polynomial binding function $p_k(\omega)$, $p_1(\omega) = \omega+1$, $p_2 = O(\omega^8)$; sample complexity $O(k\log n\cdot p_k(4/\epsilon^2)/\epsilon^2)$, hence $O(\log n/\epsilon^4)$ for $k = 1$ and roughly $\epsilon^{-18}$ and $\epsilon^{-110}$ for $k = 2, 3$.
* **Lemma 11 and Corollary 12 (compression).** Induced subgraphs of $G(\mathcal{P}^{(n)})$ have $\chi \leq (2n+1)^{\omega-1}$ (Gyárfás, longest induced paths $\leq 2n+1$); hence, for constant $\epsilon$, every state can be compressed into $\mathrm{poly}(n)$ bits from which every Pauli expectation value follows in $\mathrm{poly}(n)$ time, learned from $\mathrm{poly}(n)$ copies with $2^{O(n)}$ running time.
* **Conjecture 13.** The Paulis with $|\mathrm{Tr}(\rho P)| \geq\delta$ have a fractional coloring of size $O(1/\delta^2)$; if it were efficient, there would be triply efficient shadow tomography for every set of Paulis.

### Methodological approach

1. **Magnitudes via Bell sampling** in the basis that diagonalizes all $P\otimes P$; $\mathrm{Tr}(\rho P)^2$ with $\delta = \Theta(\epsilon^2)$, hence $\epsilon^{-4}$.
2. **Signs as a coloring problem.** On $S_\epsilon$, single-copy learning with a coloring of $G(S_\epsilon)$ suffices; the clique number $O(1/\epsilon^2)$ and $\chi$-boundedness give polynomial colorings.
3. **Mimicking state via MMW** for all Paulis: the hypothesis is updated until it is large in magnitude on $S_\epsilon$; this is the technique that King, Wan, McClean adopt for displacement operators.

### Significance and applications

* Defines the efficiency goal of this project and provides the first map (Table 2 of the paper): naive, HKP, Bell sampling plus gentle measurement, and the new two-copy methods.
* Two copies are necessary *and* sufficient for Pauli and fermionic shadow tomography; local Paulis work with one copy, local fermionic observables do not: a clean difference between qubit locality and fermionic locality.
* The graph theory ($\chi$-boundedness, Gyárfás) is a new tool in quantum learning theory.

### Relation to this project

* This project's paper cites exactly this paper for "triply efficient" and replaces two of its components: the coloring (grouping of incompatible observables) and the MMW. The sample complexity $O(\log|S|/\epsilon^4)$ of the magnitudes is the same as in Phase 1; the $\epsilon^{-2}$ of the signs corresponds to Phase 2.
* Lemma 8 is a structural statement about *every* state: at most $4/\epsilon^2$ pairwise anticommuting addresses can be large at the same time. For displacement operators with their $\omega$-commutation, the analogue is a bound on the number of large amplitudes on non-commuting addresses, a candidate for a provable promise in the top-$k$ regime.
* The correction to the table (time $\mathrm{poly}(4^n)$ for all Paulis) matters for the positioning: this project's method is not "as efficient as KGKB" but aims at time polynomial in $\log d$ for a list that is given only implicitly, and exactly this is open in general (Conjecture 13).

### Limitations and open questions

* Triply efficient shadow tomography for *arbitrary* subsets of Paulis is open (Conjecture 13); Lemma 11 gives only $n^{O(1/\epsilon^2)}$ colors.
* The $\epsilon$ exponents for fermions ($\epsilon^{-18}$, $\epsilon^{-110}$) are impractical; better binding functions are open.
* Rapid-retrieval compression for $\epsilon = 1/\mathrm{poly}(n)$ is open.
* Bell sampling on $\rho\otimes\rho$ gives $\mathrm{Tr}(\rho P)^2$ only for Paulis; for displacement operators one needs $\rho\otimes\rho^*$.

### Questions for further study

* What does the commutation graph of the $d^2$ displacement operators look like, what is its clique number on the set of large amplitudes, and is the family of its induced subgraphs $\chi$-bounded?
* Can the CNN learn the coloring *implicitly*, and can this be read off from the structure of the learned filters?
* What is the rapid-retrieval compression of a qudit state with a $k$-sparse spectrum: $O(k\log d)$ bits, and is a query possible in $O(\log d)$ time?

Paper: [arXiv:2404.19211](https://arxiv.org/abs/2404.19211)

---
## Exponential learning advantages with conjugate states and minimal quantum memory (arXiv:2403.03469)

The paper by **Robbie King, Kianna Wan, and Jarrod R. McClean** (Google Quantum AI, Caltech, Stanford; *PRX Quantum* 5, 040301 (2024)) introduces the learning resource of this project: joint measurements on a state and its complex conjugate, $\rho\otimes\rho^*$. For the task of learning all $d^2$ displacement amplitudes $y_{q,p} = \mathrm{Tr}(D_{q,p}\rho)$ of a $d$-dimensional state, $O(\log d/\epsilon^4)$ copies of $\rho\otimes\rho^*$ suffice, while every procedure on $\rho^{\otimes K}$ without $\rho^*$ needs at least $\Omega(\sqrt d/(K^2\epsilon^2))$ measurements, even for $K$ up to $1/(12\epsilon)$. The signs follow with a hypothesis state and matrix multiplicative weights; in addition there are generalized Clifford shadows for qudits and the proof that the commutation trick is restricted to displacement operators.

### Placement in the tables

* **Task type:** Estimating. Given is the implicit list of all $d^2$ displacement addresses; returned are magnitudes and signs. The row "Displacement amplitudes over a dictionary, conjugate pairs" of the estimating table; in the searching table the same paper is the basis of the sample side.
* **Object:** $d$-dimensional state, $d$ prime in the theorems. **Access:** sample on $\rho\otimes\rho^*$, rung 2 of the access ladder; the Bell measurement entangles exactly two registers, constant quantum memory.
* **Status:** 🟢 🟢 🟢. Copies logarithmic in $d$; magnitude estimation is computationally trivial; sign determination runs in $\mathrm{poly}(d, 1/\epsilon)$ via a $d\times d$ hypothesis, polynomial in the Hilbert space of a single qudit, hence $2^n$ in the $n$-qubit picture.
* **Promise:** none about the state; the resource is the access. For this project's top-$k$ variant, the dictionary promise is added (Regime 1).

### The problem

Two-copy measurements give exponential advantages for Pauli expectation values (Huang et al. 2022), and the magnitudes can be learned with minimal memory, but the signs only with task-dependent large memory (Huang, Kueng, Preskill 2021). For qudits it is also known that Bell sampling on $\rho\otimes\rho$ can fail. The questions: is there a resource with constant memory that delivers the whole displacement spectrum, what does its absence cost, and where is $\rho^*$ physically available?

### Key results

* **Theorem 1 (lower bound without $\rho^*$).** Magnitudes of all amplitudes to within $\epsilon$ with probability $2/3$ from measurements on $\rho^{\otimes K}$, $K \leq 1/(12\epsilon)$: $\Omega(\sqrt d/(K^2\epsilon^2))$ measurements. With minimal memory, the task is not efficient without $\rho^*$.
* **Theorem 2 (magnitudes).** $O(\log d/\epsilon^4)$ samples of $\rho\otimes\rho^*$ learn all $y_{q,p}$ up to a sign; simple and computationally efficient.
* **Theorem 3 (single copies).** Every single-copy protocol needs $\Omega(d/\epsilon^2)$ copies, even with single-copy access to $\rho$ *and* $\rho^*$: an entangled measurement is necessary, not only the conjugate.
* **Theorem 4 (uniqueness).** If $U\otimes\tilde U$ and $V\otimes\tilde V$ commute for non-commuting $U, V$ of finite order $d$, then $U, V$ are unitarily equivalent to a direct sum of displacement operators. The tensor extension trick is restricted to Heisenberg groups (Stone–von Neumann type).
* **Theorem 5 (signs).** All $d^2$ amplitudes including signs with $O(\log d/\epsilon^4)$ samples of $\rho\otimes\rho^*$, running time $\mathrm{poly}(d, \epsilon^{-1})$: a hypothesis state shifts the origin of a magnitude measurement, and MMW finds it (technique from King, Gosset, Kothari, Babbush).
* **Theorem 6 (qudit Clifford shadows).** All off-diagonal elements $\langle i|U^\dagger\rho U|j\rangle$ in all stabilizer bases $U \in\mathrm{Cl}_d$ with $O(\log d/\epsilon^2)$ single copies; Theorem 31 gives the variance for arbitrary $O$, with a Hilbert–Schmidt part plus displacement overlaps; for displacement operators the variance is $\Omega(d)$, consistent with Theorem 3.
* **Applications.** Quantum data from quantum computation: $\rho^*$ by conjugating every gate, hence an exponential advantage of white-box over black-box access; quantum data from nature: sensor arrays, long-baseline interferometry, mixedness testing against a thermal background; bosonic limit $d\to\infty$ with $x = \sqrt{\pi/d}(q,p)$.

### Methodological approach

* **Commutativity via tensor extension.** The operators $D_{q,p}\otimes D_{q,p}^*$ commute for all $(q,p)$ and are measured jointly in the Bell basis. For pure states the outcome distribution is $|y_{q,p}|^2/d$; in general $|y_{q,p}|^2$ is the Fourier coefficient $\mathbb{E}_{(a,b)}\exp(i2\pi(ap-bq)/d)$ of the outcome distribution (Appendix B, Eqs. B8, B9). On $\rho\otimes\rho$ one would have $D\otimes D$, and these commute only for qubits.
* **Lower bounds** (Appendix G) via the tree method over a family of states close to the maximally mixed state with one imprinted displacement amplitude, with the non-commutativity of $D_{q,p}^{\otimes K}$ on $\rho^{\otimes K}$ as the lever; $K$ appears quadratically.
* **Signs** (Appendix C): a Bell measurement on $\rho\otimes\sigma^*$ with a known hypothesis state $\sigma$ gives quantities of the type $\mathrm{Re}(y_{q,p}\overline{\mathrm{Tr}(D\sigma)})$; MMW adjusts $\sigma$ until all large addresses are large in magnitude on $\sigma$.
* **Shadows** (Appendix H): twirls of the qudit Clifford group up to third order; $\mathrm{Cl}_d$ is the normalizer of the Heisenberg–Weyl group and contains the QFT.

### Significance and applications

* A new axis in the map: the access ($\rho$, $\rho\otimes\rho^*$, circuit) is independent of the memory axis, and the separation here is one between two oracles at the same small memory, not between coherent and incoherent (see the QUALM paragraph).
* A physically motivated family of observables with a bosonic limit; the paper connects quantum learning theory with sensing.
* Theorem 4 says that new primitives are needed for classes beyond the Heisenberg groups.

### Relation to this project

* This is Paper 1 of the project: Phase 1 is Theorem 2, and Phase 2 replaces the MMW of Theorem 5 by the adaptive probe state $\tilde\rho$ with CNN control. The sample complexity $O(\log d/\epsilon^4)$ is the target of this project's scaling measurement in $d$; the $\epsilon^{-4}$ of the magnitudes and the $\epsilon^{-2}$ of the signs are the reference for the empirical overall scaling.
* Theorem 3 is the reason why the pipeline needs two copies at all, and Theorem 1 the reason why $\rho\otimes\rho$ does not suffice; the 2025 evaluation with $\rho\otimes\rho$ therefore works with real states (GHZ, real Gibbs states), where $\rho = \rho^*$.
* Theorem 4 is the theoretical limit of Objective 3 ("generalizations of Paulis"): the trick reaches exactly as far as displacement operators, no further.
* The lower bound $\Omega(\sqrt d)$ is a *sample* statement; the LWE hardness of this project's paper is a *time* statement about the same task with a sparsity promise. Together they form the cell "sampling access, searching" of the quadrant.

### Limitations and open questions

* $d$ prime in the proofs; composite $d$ and the cyclic single-qudit basis are not treated.
* Sign determination is polynomial in $d$, not in $\log d$: computationally efficient only for single qudits, not for $n$-qubit systems with $d = 2^n$.
* $\rho^*$ cannot be produced physically from $\rho$; availability depends on the source (Appendix D), with restrictions for sensors.
* Noise: no analysis; the Bell measurement needs clean two-register gates.

### Questions for further study

* What does the distribution of the Bell measurement on $\rho\otimes\rho^*$ look like for composite $d$, where $\mathbb{Z}_d$ is not a field and the $D_{q,p}$ generate subgroups of different orders?
* Which phase information exactly remains in "up to a sign" when $y_{q,p}$ is complex: only the magnitude, or also the argument modulo $\pi$?
* Where in the tree-method proof of Theorem 1 is the term that vanishes with access to $\rho^*$, and can an interpolation result between $\rho\otimes\rho$ and $\rho\otimes\rho^*$ (for instance $\rho\otimes\tilde\rho$ with an imperfect conjugate) be obtained from it?

Paper: [arXiv:2403.03469](https://arxiv.org/abs/2403.03469)

---

## Quantum state tomography via compressed sensing (arXiv:0909.3304)

The paper by **David Gross, Yi-Kai Liu, Steven T. Flammia, Stephen Becker, and Jens Eisert** (Hannover, Caltech, Perimeter, Potsdam; *Phys. Rev. Lett.* 105, 150401 (2010)) carries compressed sensing and matrix completion over to tomography: a state of rank $r$ in dimension $d$ can be reconstructed uniquely from $O(rd\log^2 d)$ randomly chosen Pauli expectation values, by minimizing the trace norm under linear constraints, instead of from $d^2$ settings. The method is robust against noise, certifies closeness to purity without prior assumptions, and runs numerically in minutes for eight qubits.

### Placement in the tables

* **Task type:** Estimating with $M = d^2$, but under a rank promise; the density matrix is returned. The row "Low-rank tomography, compressed sensing" of the estimating table, in the section "structured escapes before shadows".
* **Object:** mixed state close to rank $r$. **Access:** sample, single copies, $m$ random Pauli expectation values, each estimated from many copies.
* **Status:** 🔴 🔴 🔴 in $n$: $rd\log^2 d$ is exponential in $n$, but the factor $d$ instead of $d^2$ is a quadratic saving, and time and memory are of order $O(rd)$ instead of $O(d^2)$.
* **Promise:** rank $r \ll d$, for instance pure states under local noise with rate $p$: rank $\approx d^{H(p)}$.

### The problem

Full tomography of eight ions cost hundreds of thousands of measurements and weeks of post-processing. Parameter counting says that $O(rd)$ settings could suffice for rank $r$, but minimum-rank problems are NP-hard, and the matrix completion theorems (Candès–Recht, Candès–Tao) require matrix elements and incoherence assumptions that do not fit the lab. What is sought: Pauli measurements, arbitrary density matrices, efficient reconstruction.

### Key results

* **Theorem 1.** For $\rho$ of rank $r$ and $m = c\,dr\log^2 d$ random Pauli expectation values, $\rho$ is the unique solution of $\min\Vert\sigma\Vert_{\mathrm{tr}}$ subject to $\mathrm{tr}\,\sigma = 1$, $\mathrm{tr}(w(A_i)\sigma) = \mathrm{tr}(w(A_i)\rho)$, with failure probability exponentially small in $c$.
* **Observation 1 (noise).** If $\rho_t$ is only $\epsilon_1$-close to rank $r$ and the expectation values are known up to $\epsilon_2$, then the relaxed program $\min\Vert\sigma\Vert_{\mathrm{tr}}$ with $\Vert\mathcal{R}\sigma - \mathcal{R}\omega\Vert_2 \leq\epsilon$ gives an error $O(\epsilon\sqrt{rd})$ in trace norm; the authors conjecture considerably better robustness.
* **Observation 2 (certification).** For almost pure states, purity can be certified from $O(d)$ Pauli values, and the state can be reconstructed with explicit error bounds from $O(cd\log^2 d)$ values, without prior assumptions about $r$ and $\delta_1$.
* **Hybrid method.** Structured random choice $w(u,v)$ for $u$ from a set of size $O(r\,\mathrm{polylog}\,d)$ and all $v$: running time $O(d)$ instead of $O(d^2)$ per step, without the full guarantee.
* **Numerics.** Eight qubits, rank 3, 5% depolarization, Gaussian noise $\sigma = 0.1/d$: 95% fidelity in under ten seconds with the hybrid method; on the data of the eight-ion experiment, 90.5% fidelity with a rank-3 approximation from under 30% of the Paulis in three minutes.
* **Processes:** via the Jamiołkowski state, effective for channels with few Kraus operators.

### Methodological approach

* **Dual certificate.** Uniqueness follows from a strict subgradient $Y$ of the trace norm in the range of the sampling operator $\mathcal{R}$; two cases depending on the ratio of $\Delta_T$ to $\Delta_T^\perp$ (tangent space $T$ of the rank-$r$ matrices).
* **Golfing scheme.** A recursive process $Y_i = \sum_j\mathcal{R}_jX_{j-1}$ with $l$ independent batches of $\kappa_0 rd$ Paulis converges exponentially fast to an approximate subgradient; noncommutative large-deviation bounds (Ahlswede–Winter) for $\Vert\mathcal{A} - \mathbb{1}_T\Vert$. This is a considerable simplification compared with Candès–Recht.
* **Solver:** singular value thresholding instead of interior-point methods.

### Significance and applications

* The first proof that a structural promise (rank) makes tomography quadratically cheaper, and the beginning of compressed sensing in quantum information; successors: error bounds and sample complexity (Flammia, Gross, Liu, Eisert 2012), process tomography with compressed sensing (record at three qubits, cited in Flammia–Wallman).
* The golfing scheme became a standard tool of matrix completion theory.

### Relation to this project

* Rank is the "low rank ⇒ easy" promise; this project works with the orthogonal promise of sparsity in the displacement spectrum. Both are compressed sensing structures, but this project's task has no *choosable* measurements: Bell sampling delivers i.i.d. draws, not the $m$ selected expectation values. That is the difference between this row (🔴 in copies, but query-like in the selection) and this project's own (🟢 in copies, LWE-hard in the decoder).
* Trace norm minimization is the convex surrogate for rank; the $\ell_1$ surrogate for sparsity in the spectrum would be the obvious provable alternative to the CNN, provided an RIP-type argument exists for Bell statistics.
* Certified tomography (Observation 2) is a model for a certificate of sparsity: statistics of the type $\sum|y_{q,p}|^4$, which measure the concentration of the spectrum, can be read off from the Bell record.

### Limitations and open questions

* Exponential in $n$; the rank promise does not change the exponent, only the base.
* The robustness bound $O(\epsilon\sqrt{rd})$ is crude; RIP-based arguments should do better (conjecture).
* The hybrid method comes without a guarantee.
* Every Pauli expectation value needs many copies; the sample complexity in copies is not counted here.

### Questions for further study

* Does a golfing argument hold for the displacement basis of a qudit, which is orthogonal but not Hermitian?
* What is the compressed sensing formulation of "sparsity in the displacement spectrum plus i.i.d. Bell samples", and is the sampling matrix incoherent in the sense of the RIP?
* How are rank and displacement sparsity related: at most how many large addresses does the spectrum of a rank-$r$ state have?

Paper: [arXiv:0909.3304](https://arxiv.org/abs/0909.3304)

---

## Estimating the spectrum of a density operator (arXiv:quant-ph/0102027)

The paper by **Michael Keyl and Reinhard F. Werner** (TU Braunschweig; *Phys. Rev. A* 64, 052311 (2001)) is a four-page note with a theorem that defines the memory axis at its far end: if $N$ copies of $\rho$ are measured jointly according to the decomposition of $\mathcal{H}^{\otimes N}$ into irreducible representations of the symmetric group, i.e. according to Young diagrams $Y$, then $Y/N$ is an estimator of the spectrum of $\rho$, and the failure probability falls exponentially in $N$ with an explicitly computed rate, the relative entropy between the estimated and the true spectrum.

### Placement in the tables

* **Task type:** Estimating. Given the implicit list "the eigenvalues", the ordered spectrum $r_1 \geq\dots\geq r_d$ is returned. The row "Spectrum estimation by Schur sampling".
* **Object:** mixed state on $\mathbb{C}^d$. **Access:** sample, but with a collective measurement on all $N$ copies at once; quantum memory $k = N$, the primitive "Collective Schur sampling".
* **Status:** 🔴 🔴 🟢 in $n$ according to the table: for precision $\epsilon$ one needs $N \sim d^2/\epsilon^2$ copies (O'Donnell, Wright 2015 for the optimal rates), the measurement is a Schur transform across $N$ registers, and the output has only $d$ numbers.
* **Promise:** none; the method is basis-independent and does not even need to know the eigenbasis.

### The problem

The density matrix can only be estimated on ensembles (no-cloning), and estimation is a limiting case of cloning at $M\to\infty$. For mixed states it is unclear which figure of merit defines "optimal". Instead of optimality at finite $N$, the authors ask about the asymptotic behavior under arbitrary, including entangled, measurements on $\rho^{\otimes N}$, for the simplest nontrivial quantity: the spectrum.

### Key results

* **Symmetry reduction.** Without loss of estimation quality, the estimator may commute with all permutations $S_p$ and all $U^{\otimes N}$; it is then a function of the projectors $P_Y$ onto the summands $R_Y\otimes S_Y$ of the Schur–Weyl decomposition $\mathcal{H}^{\otimes N} \cong\bigoplus_Y R_Y\otimes S_Y$, with $Y$ ranging over the Young diagrams with $d$ rows and $N$ boxes.
* **The estimator.** $s_N(Y) = Y/N$, the normalized row lengths. The probability is $\mathrm{tr}(\rho^{\otimes N}P_Y) = \chi_Y(\rho)\dim S_Y$ with the character $\chi_Y$ of the $GL(d)$ representation; Figure 1 shows the distribution for $d = 3$, $N = 120$, $r = (0.6, 0.3, 0.1)$, sharply peaked around the true spectrum.
* **Theorem.** The estimator is asymptotically exact, and for every set $\Delta$ with small boundary, $\lim_N\frac1N\ln K_N(\Delta) = -\inf_{s\in\Delta}I(s)$ with the rate function $I(s) = \sum_j s_j(\ln s_j - \ln r_j)$, the relative entropy of the probability vectors $s$ and $r$.
* **Proof sketch.** The Laplace transform $c(\eta) = \lim\frac1N\ln\int K_N(ds)e^{N\eta\cdot s}$ is estimated via weights of the representation $\pi_Y$: $Y$ is the highest weight, hence $e^{Y\cdot h} \leq\chi_Y(\rho_h) \leq\dim(R_Y)e^{Y\cdot h}$ with polynomial $\dim R_Y$; from this $c(\eta) = \ln\sum_\alpha r_\alpha e^{\eta_\alpha}$, and the Legendre transform gives $I$. Regularity follows Duffield and Gärtner–Ellis.

### Methodological approach

* Large deviations for tensor powers of group representations (Duffield 1990), extended from $\rho = I/d$ to arbitrary $\rho$ by the factor $\chi_Y(\rho)/\chi_Y(I)$.
* The order $\rhd$ on weights (row lengths in decreasing order) makes $Y$ the "fastest exponential term"; this is why precisely the row lengths estimate the spectrum.

### Significance and applications

* Establishes Schur sampling as a measurement primitive; O'Donnell and Wright (2015, 2016) and Haah et al. (2017) build optimal tomography ($\Theta(d^2/\epsilon^2)$) and spectrum testing on it. The representation theory of the symmetric group thereby became a standard tool of quantum statistics.
* The rate function as a relative entropy connects quantum statistics with Sanov's theorem; the authors remark that there is no direct route to the i.i.d. theory.
* Outlook on an estimator for the whole density operator: measure the Young diagram, then perform a covariant measurement of the eigenbasis; exactly this became optimal tomography.

### Relation to this project

* The row marks what "memory $k = N$" costs and buys: optimal rates, but a measurement across all copies. This project's protocol sits at the other end with $k = 2$, and the question "what is achievable with $k$ between two and $N$" (open question 2 of the estimating section) has its end point here.
* The spectrum is basis-independent, the displacement spectrum basis-dependent; the Schur measurement sees the eigenvalues, the Bell measurement the coefficients in a fixed operator basis. The purity $\mathrm{tr}(\rho^2) = \sum r_j^2$ is the one quantity that both measurements deliver (the SWAP test as the two-copy Schur measurement); it is the mixedness factor of this project's taxonomy.
* The proof technique (the highest weight dominates the Laplace transform) is a pattern for concentration statements about i.i.d. Bell samples, whose distribution is also a sum over representations.

### Limitations and open questions

* No statement about optimality at finite $N$; for different figures of merit the authors found different optimal estimators, rarely the one proposed here.
* Only the spectrum, not the eigenbasis.
* The measurement is a Schur transform across $N$ registers, not realistic for hardware.

### Questions for further study

* What is the two-copy restriction of the Schur measurement ($N = 2$: symmetric and antisymmetric subspace), and how is it related to the Y parity of the Bell basis (see Hangleiter–Gullans)?
* What does the rate function look like for estimators that entangle only $k$ copies at a time, and does it interpolate between $I(s)$ and the single-copy rate?
* Can the purity be read off from the Bell record on $\rho\otimes\rho^*$, and is that the Schur statistics for $N = 2$ in a different basis?

Paper: [arXiv:quant-ph/0102027](https://arxiv.org/abs/quant-ph/0102027)

---

## Efficient quantum tomography (arXiv:1508.01907)

The paper by **Ryan O'Donnell and John Wright** (Carnegie Mellon; STOC 2016) shows that full tomography gets by with a number of copies linear in the dimension: $O(d/\epsilon^2)$ copies for Frobenius error $\epsilon$, $O(rd/\epsilon^2)$ for trace distance $\epsilon$ at rank $r$, i.e. $O(d^2/\epsilon^2)$ in the general case, compared with $O(d^3/\epsilon^2)$ before. The procedure is Keyl's measurement: first weak Schur sampling as in Keyl–Werner, then a covariant measurement of the eigenbasis. In addition there is principal component analysis: the best rank-$k$ approximation from $O(kd/\epsilon^2)$ copies, the $k$ largest eigenvalues from $O(k^2/\epsilon^2)$, independent of $d$. Simultaneously and independently, Haah, Harrow, Ji, Wu, and Yu (arXiv:1508.01797) reached the same copy count up to a logarithm with a different measurement and proved the matching lower bound. Together the two papers give the $\Theta(d^2/\epsilon^2)$ of the row "Full QST".

### Placement in the tables

* **Task type:** Estimating with $M = d^2$, nothing withheld; the density matrix is returned. The row "Full QST" of the estimating table, in the section "Full QST: the exponential baseline". The spectrum estimation (Theorems 1.1 and 1.7) improves the row "Spectrum estimation by Schur sampling".
* **Object:** mixed state on $\mathbb{C}^d$. **Access:** sample, one collective measurement on all $N$ copies $\rho^{\otimes N}$; quantum memory $k = N$, the primitive "Collective Schur sampling".
* **Status:** 🔴 🔴 🔴 in $n$: $d^2 = 4^n$ copies, $\mathrm{poly}(d)$ classical post-processing, $d^2$ entries. Within the exponential regime, the copy count is optimal up to $\log d$.
* **Promise:** none. Rank $r$ lowers the copy count in trace distance from $d^2$ to $rd$.

### The problem

For twenty years the best method needed $O(d^4)$ copies for constant error, then in early 2015 $O(d^3)$ (Kueng, Rauhut, Terstiege). Spectrum estimation needed $O(r^2\log(r/\epsilon)/\epsilon^2)$ copies. The optimal dependence on $d$ was, according to Harrow, "shockingly unknown"; Holevo gives only $\tilde\Omega(rd)$. Is full tomography more expensive than spectrum estimation?

### Key results

With $N$ copies, spectrum $\alpha_1\geq\dots\geq\alpha_d$, and the Young diagram $\lambda$, normalized to $\bar\lambda = \lambda/N$:

* **Theorem 1.1 (spectrum in $\ell_2$).** $\mathbb{E}\Vert\bar\lambda - \alpha\Vert_2^2\leq d/N$; the procedure depends only on the rank, so even $r/N$. Corollary 1.3: the spectrum to within $\epsilon$ in $\ell_2$ with $O(r/\epsilon^2)$ copies, in total variation with $O(r^2/\epsilon^2)$, without the logarithm of the earlier bounds.
* **Theorem 1.2 (tomography).** Keyl's estimator $\hat\rho = U\,\mathrm{diag}(\bar\lambda)\,U^\dagger$ satisfies $\mathbb{E}\Vert\hat\rho - \rho\Vert_F^2\leq(4d-3)/N$. Corollary 1.4: $O(d/\epsilon^2)$ copies for Frobenius error $\epsilon$, $O(rd/\epsilon^2)$ for trace distance $\epsilon$. Up to a small factor, full tomography is no more expensive than spectrum estimation.
* **Theorem 1.5 (PCA).** If only the $k$ largest entries are output, $U\,\mathrm{diag}^{(k)}(\bar\lambda)\,U^\dagger$, the trace-norm error is at most $\alpha_{k+1}+\dots+\alpha_d + 6\sqrt{kd/N}$. With $O(kd/\epsilon^2)$ copies the output is therefore at most $\epsilon$ worse than the best rank-$k$ approximation, even if $\rho$ does not have low rank.
* **Theorem 1.7 (the largest eigenvalues).** $\mathbb{E}\,d_{\mathrm{TV}}^{(k)}(\bar\lambda,\alpha)\leq(1.92k + 0.5)/\sqrt N$. The $k$ largest eigenvalues cost $O(k^2/\epsilon^2)$ copies, independent of $d$ and of the rank.
* **Theorem 1.11 (coupling for RSK).** If $\beta$ majorizes the distribution $\alpha$, there is a coupling of the Schur–Weyl distributions $\mathrm{SW}^N(\alpha)$ and $\mathrm{SW}^N(\beta)$ in which the diagram for $\beta$ always dominates the one for $\alpha$. A purely combinatorial result about the Robinson–Schensted–Knuth algorithm.
* **Lower bounds (cited).** $\tilde\Omega(rd)$ for constant trace distance, $\tilde\Omega(d)$ for constant Frobenius error already at rank one, $\tilde\Omega(d^2)$ at Frobenius error $\Theta(1/\sqrt d)$. For constant $\epsilon$ the bounds are therefore optimal up to $O(\log d)$.

### Methodological approach

* **Two measurement stages from representation theory.** Weak Schur sampling projects $\rho^{\otimes N}$ onto the isotypic components of $(\mathbb{C}^d)^{\otimes N}\cong\bigoplus_\lambda\mathrm{Sp}_\lambda\otimes V_\lambda^d$ and yields $\lambda$ with the Schur–Weyl distribution, which depends only on the spectrum. Then Keyl's covariant POVM in the space $V_\lambda^d$ measures a $U\in U(d)$, with density proportional to $\langle T_\lambda\vert\pi_\lambda(U^\dagger\rho U)\vert T_\lambda\rangle$, where $T_\lambda$ is the highest-weight vector.
* **Combinatorics instead of large deviations.** The Schur–Weyl distribution is the distribution of the RSK shape of a random word with i.i.d. letters from $\alpha$; $\lambda_1$ is the longest increasing subsequence. The authors control the expectation values via majorization, Schur polynomials, and generalized power functions from principal minors, not via the asymptotic rates of Keyl–Werner.
* **From Frobenius to trace norm.** For a rank-$r$ estimator, Cauchy–Schwarz on the singular values of the difference gives $\Vert\cdot\Vert_1\leq\sqrt{2r}\,\Vert\cdot\Vert_F$; hence the factor $r$.

### Significance and applications

* Together with Haah et al., answers the question of the optimal copy count of tomography with entangled measurements: $\Theta(d^2/\epsilon^2)$ up to logarithms. With single copies it is $\Theta(d^3/\epsilon^2)$, even adaptively (Lowe, Nayak; Chen, Huang, Li, Liu, Sellke). The gap $d$ is the price of the memory axis for full tomography.
* Turns Keyl–Werner's asymptotic statement into a non-asymptotic one with explicit constants, and Keyl's measurement into an optimal procedure.
* Quantum PCA with a provable copy count. Learning a property of the principal component instead of reconstructing it completely is later separated by Huang et al. (Science 2022): $O(1)$ copies against $\Omega(2^{n/2})$ without memory.

### Relation to this project

* The row marks the base price the project competes against. All $d^2$ displacement coefficients are contained in $\rho$, and full tomography delivers them with $\Theta(d^2/\epsilon^2)$ copies and a measurement across all copies. The project wants, with memory two and $O(\log d/\epsilon^4)$ copies, only the magnitudes and then the top-$k$ support; the gain is exponential in the copies, paid for with a restricted question.
* Theorem 1.7 is dimension-free: the $k$ largest eigenvalues cost $O(k^2/\epsilon^2)$ copies, independent of $d$. This is the spectral analogue of the top-$k$ question, but in the eigenbasis. There the Schur measurement makes the top-$k$ list accessible independently of the basis; in the displacement spectrum it is tied to the fixed operator basis, and the normalization $\sum\vert y\vert^2 = d$ prevents reading it off directly.
* Theorem 1.5 is the pattern for an agnostic guarantee: error equals the mass outside the top $k$ plus a statistical term. A guarantee for the top-$k$ decoder would have this form if the flat remainder carries the mass $d - k$.
* On the copy axis, the project sits between $\Theta(d^2)$ entangled and $\Theta(d^3)$ single-copy, with memory two, but on a different task.

### Limitations and open questions

* Exponential in $n$; the procedure is a reference, not a practical method for many qubits.
* The measurement is a Schur transform across all $N$ registers plus a continuous covariant POVM. The authors do not analyze running time or implementation.
* Optimal only up to $\log d$ and only for constant $\epsilon$. The bounds hold in expectation; high probability costs a factor $\log(1/\delta)$.
* PCA in Frobenius norm gives, by the authors' argument, no gain over full tomography (Section 6).

### Questions for further study

* What does Keyl's measurement give for $N = 2$, and how is it related to the Bell measurement on $\rho\otimes\rho^*$, which is also a two-copy measurement?
* Is there an analogue of Theorem 1.7 for the displacement spectrum, i.e. the $k$ largest $\vert y_{q,p}\vert$ with a copy count independent of $d$? The normalization $\sum\vert y\vert^2 = d$ argues against it, but in which access model exactly?
* What does the Schur–Weyl distribution look like for a state with a few large eigenvalues above a flat remainder, the spectral counterpart of this project's instances?

Paper: [arXiv:1508.01907](https://arxiv.org/abs/1508.01907)

---

## Query-optimal estimation of unitary channels in diamond distance (arXiv:2302.14066)

The paper by **Jeongwan Haah, Robin Kothari, Ryan O'Donnell, and Ewin Tang** (Microsoft, Google, CMU, Washington; FOCS 2023) solves process tomography for unitaries in the strictest metric: an unknown $Z \in U(d)$ is estimated to within $\epsilon$ in diamond norm with $O(d^2/\epsilon)$ applications, using only one qudit of memory, and $\Omega(d^2/\epsilon)$ applications are necessary, even with access to $Z^\dagger$ and controlled versions. Before: $O(d^3/\epsilon^2)$ (standard process tomography) or $O(d^{2.5}/\epsilon)$ (Yang, Renner, Chiribella via norm conversion). The technique is a bootstrap that lifts constant-error estimates to Heisenberg scaling.

### Placement in the tables

* **Task type:** Estimating with $M = d^2$: nothing is withheld; $U$ is returned. The row "Unitary estimation in diamond distance".
* **Object:** unitary. **Access:** query, rung 3: adaptively chosen states $V_2(ZV_1)^pV_0|0\rangle$, i.e. sequences of applications; no ancilla.
* **Status:** 🔴 🔴 🔴 in $n$: queries buy the rate $1/\epsilon$, not the dimension.
* **Promise:** none; this is the query version of full tomography.

### The problem

Process tomography has been studied in many metrics; the operationally natural one, the diamond norm (worst case over all inputs including ancillas), had not been treated directly. Entanglement infidelity is average-case and weaker by up to $\sqrt d$ (Proposition 1.9: $4F \leq\Vert\cdot\Vert_\diamond^2 \leq 2dF$; the controlled $C^kX$ has infidelity $O(2^{-k})$ to the identity, but diamond distance 1). The "storage-and-retrieval" literature (Bisio et al., Sedlák et al., Yang–Renner–Chiribella) optimizes parallel strategies in infidelity, with memory of the size of the number of queries. What is sought: diamond norm, Heisenberg rate, no memory overhead, and a matching lower bound.

### Key results

* **Theorem 1.1.** An algorithm with $O(d^2/\epsilon)$ queries, one qudit, $\mathrm{poly}(d, 1/\epsilon)$ gates and classical time, output $\hat Z$ with $\mathbb{E}\Vert\mathcal{U}(\hat Z) - \mathcal{U}(Z)\Vert_\diamond^2 \leq\epsilon^2$; as a mixed-unitary channel $\mathcal{M}$ even $\Vert\mathcal{M} - \mathcal{U}(Z)\Vert_\diamond \leq\epsilon^2$.
* **Theorem 1.2.** Every algorithm with oracles for $Z, Z^\dagger, cZ, cZ^\dagger$ and error $\epsilon < 1/8$ needs $\Omega(d^2/\epsilon)$ queries: the first lower bound that is optimal in both parameters jointly, tight for every function $\epsilon = \phi(d)$.
* **Theorem 2.1 (base algorithm).** Standard process tomography done carefully gives $O(d^2/\epsilon^2)$: state tomography of the columns $Z|i\rangle$ with Haar-random error (no accumulation to $\sqrt d\epsilon$), relative phases from the columns of $Z$ and $ZF$ with the Fourier matrix $F$ (Proposition 2.3).
* **Lemma 3.1 (roots).** If $U, V$ are $\alpha$-close in diamond norm and both $0.01$-close to the identity, then $U^{1/p}, V^{1/p}$ are $50\alpha/p$-close.
* **Theorem 3.3 (bootstrap, Algorithm 1).** A base algorithm with error $1/200$ becomes an algorithm with error $\epsilon$ at a query overhead of $1/\epsilon$: estimate $(ZV_j^\dagger)^{2^j}$ with constant error, where $V_j$ is the current estimate ("shift to identity"), and take roots.
* **Comparison.** Yang–Renner–Chiribella: $O(d^2/\sqrt\delta)$ in infidelity, parallel, memory $\Theta(d^2\log d/\sqrt\epsilon)$; van Apeldoorn et al.: $O(d^2/\epsilon\cdot\log)$ with $cZ, cZ^\dagger$ and $\Theta(d\log)$ memory. The new algorithm needs only $Z$ and no memory.

### Methodological approach

* **Warm-up** (Fig. 1): for $Z = \mathrm{diag}(1, e^{i\phi})$, constant-error estimates of $Z^{2^k}$ give the bits of $\phi$; this is incoherent phase estimation (robust phase estimation). For general $Z$ this fails when eigenvalues lie close to $-1$ (powers of $\pm1$ reveal nothing about eigenvectors); Lemma 3.1 therefore requires closeness to the identity, and recentering $ZV_j^\dagger$ establishes it.
* **Lower bound:** a combination of unitary channel discrimination (Bavaresco et al.) with a reduction technique from quantum query complexity, adapted from diagonal to general unitaries.
* Median trick (Proposition 2.4) for success probability $1-\eta$ at $O(\log 1/\eta)$ overhead; discretization via Solovay–Kitaev for finite precision.

### Significance and applications

* Settles unitary tomography in diamond norm: $\Theta(d^2/\epsilon)$ is optimal in queries and in memory.
* Qualitatively close to gate set tomography, which reaches Heisenberg scaling through long gate sequences; the paper gives the first theoretical bound for this in a related model.
* The bootstrap is a general tool: constant-error estimators plus root extraction plus recentering give the Heisenberg rate for objects on a Lie group.

### Relation to this project

* The row shows what query access does *not* buy: the dimension. For the estimating column: queries improve $1/\epsilon^2$ to $1/\epsilon$, sparsity or rank improve $d^2$; both together is the question of efficient unitary estimation under structural promises (low degree in Arunachalam et al., juntas in Chen–Nadimpalli–Yuen).
* The recentering "shift to identity" is conceptually the same as the hypothesis state of King, Wan, McClean and the probe state of Phase 2: the unknown is shifted into a neighborhood in which the measurement is linear and informative. The link between "learning the residual" (also in Bakshi et al. and Shin, Lee, Oh) and "signs via a probe" is a common pattern.
* The distinction average case (infidelity) versus worst case (diamond) is the same as that between a PAC guarantee and an "all $M$" guarantee and should be named in this project's scaling analysis: top-$k$ accuracy on average over instances is average-case.

### Limitations and open questions

* The constants ($1/200$, $0.01$) are not optimized.
* Gate complexity $\mathrm{poly}(d, 1/\epsilon)$; how small it can be is not investigated.
* Unitaries only; general channels in diamond norm remain at rates of the type $1/\epsilon^2$.
* No robustness against noise in $Z$ itself.

### Questions for further study

* What does Lemma 3.1 look like for the Heisenberg–Weyl group, where $D_{q,p}^d = I$ and powers are periodic?
* Can the bootstrap be carried over to the estimation of a *preparation unitary* with sparsity in the displacement spectrum of the prepared state, and what is then the analogue of $d^2$?
* Why do $Z$ queries without control suffice, while van Apeldoorn et al. need $cZ$, and does the same hold for amplitude estimation in this project's query regime?

Paper: [arXiv:2302.14066](https://arxiv.org/abs/2302.14066)

---

## Improved machine learning algorithm for predicting ground state properties (arXiv:2301.13169)

The paper by **Laura Lewis, Hsin-Yuan Huang, Viet T. Tran, Sebastian Lehner, Richard Kueng, and John Preskill** (Caltech, JKU Linz, AWS; *Nature Communications* 15, 895 (2024)) dramatically improves the provable ML algorithm for ground-state properties in gapped phases of Huang, Kueng, Torlai, Albert, and Preskill (Science 2022): instead of $O(n^c)$ training data with large $c$ and $n^{O(1/\epsilon)}$ in the accuracy, $N = \log(n/\delta)\,2^{\mathrm{polylog}(1/\epsilon)}$ data points suffice, training and prediction run in $O(n\log n)$, and the distribution over parameters may be arbitrary. The price: the geometry of the system must be known, and it is built into a feature map as an inductive bias.

### Placement in the tables

* **Task type:** Estimating with generalization. Given data $(x_\ell, y_\ell \approx\mathrm{Tr}(O\rho(x_\ell)))$ for Hamiltonians $H(x)$ of the same phase, $\mathrm{Tr}(O\rho(x))$ is returned at new $x$. The row "Ground-state properties across a phase from shadows".
* **Object:** family of ground states $\rho(x)$ of a geometrically local gapped Hamiltonian $H(x) = \sum_j h_j(\vec x_j)$, $x\in[-1,1]^m$. **Access:** classical data; with classical shadows of the training states (Corollary 1) also sample access with $T = \tilde O(\log n/\epsilon^2)$ measurements per state.
* **Status:** 🟢 🟢 🟢: data logarithmic, time almost linear, memory the weight vector $w^*$ of dimension $m_\varphi = O(n)\cdot(1 + 2/\delta_2)^{\mathrm{poly}(\delta_1)}$.
* **Promise:** gap, geometric locality of $H$ and $O$ (a sum of geometrically local terms with $\Vert O\Vert_\infty \leq 1$), known geometry; the $x_\ell$ come from an arbitrary unknown distribution $\mathcal{D}$.

### The problem

The predecessor showed that a classical ML algorithm with polynomially many data can predict ground-state properties across a phase, and that this is impossible without data under standard assumptions. But $n^c$ with large $c$, $n^{O(1/\epsilon)}$ in $\epsilon$, and only the uniform distribution over $[-1,1]^m$ are practically unusable. The lower bound $N = n^{\Omega(1/\epsilon)}$ from the predecessor holds without knowledge of the geometry; so geometry is the additional information that is needed.

### Key results

* **Theorem 1.** With $N = \log(n/\delta)\,2^{\mathrm{polylog}(1/\epsilon)}$ training points from an arbitrary $\mathcal{D}$ and $|y_\ell - \mathrm{Tr}(O\rho(x_\ell))| \leq\epsilon$, LASSO over the feature map $\varphi$ yields a function $h^* = w^*\cdot\varphi$ with $\mathbb{E}_{x\sim\mathcal{D}}|h^*(x) - \mathrm{Tr}(O\rho(x))|^2 \leq\epsilon$, with probability $1-\delta$, in time $O(nN)$. At $\epsilon = \Theta(1)$: $N = O(\log n)$.
* **Corollary 1.** With classical shadows $\sigma_T(\rho(x_\ell))$ from $T = \tilde O(\log n/\epsilon^2)$ random Pauli measurements, the same algorithm learns a ground-state representation $\hat\rho_{N,T}(x)$ with the same guarantee for *all* sums of geometrically local observables at once.
* **Theorem 2 (Pauli 1-norm).** For sums of geometrically local observables, $\sum_Q|\alpha_Q| \leq C\Vert O\Vert_\infty$: the $\ell_1$ norm of the Pauli coefficients is bounded by the operator norm, a statement that is trivial for the $\ell_2$ norm and new for $\ell_1$.
* **Proposition 1 (hardness without data).** A randomized polynomial-time algorithm without data that computes single-qubit properties on average to constant error for all smooth families of gapped 2D Hamiltonians would solve NP-complete problems.
* **Numerics.** 2D antiferromagnetic random Heisenberg models up to $9\times 5 = 45$ qubits with random Fourier features; the error falls with $N$ and $T$ and hardly depends on $n$; the learned weights exploit the local geometry (Fig. 2B).

### Methodological approach

1. **Local decomposition via spectral flow.** $\mathrm{Tr}(O\rho(x)) \approx\sum_{P\in S^{(\mathrm{geo})}}f_P(x)$ with $f_P(x) = \alpha_P\mathrm{Tr}(P\rho(\chi_P(x)))$, where $\chi_P$ sets all coordinates outside the neighborhood $I_P$ (radius $\delta_1 = \Theta(\log^2(1/\epsilon))$) to zero; error $O(\epsilon)$ because of exponentially decaying correlations in gapped ground states.
2. **Discretization.** Each smooth $f_P$ is approximated on a grid $X_P$ over the coordinates in $I_P$ by indicator functions of thickened affine subspaces $T_{x',P}$; the grid step is $\delta_2 = 1/\lceil C'\sqrt{|I_P|}/\epsilon\rceil$ (Eq. A.57; the main text writes $\delta_2 = \Theta(1/\epsilon)$, which is the number of grid points per coordinate). This defines the feature map $\varphi(x)_{x',P} = \mathbb{1}[x\in T_{x',P}]$.
3. **LASSO with $\Vert w\Vert_1 \leq B$.** There exists $w'$ with training error $\leq 0.53\epsilon$ and $\Vert w'\Vert_1 \leq C\Vert O\Vert_\infty(1 + 2/\delta_2)^{\mathrm{poly}(\delta_1)} = 2^{\mathrm{polylog}(1/\epsilon)}$ (Theorem 2 supplies the bound); standard generalization theory gives $\mathbb{E}|h^* - \mathrm{Tr}(O\rho)|^2 \leq$ training error $+ O(B\sqrt{\log(m_\varphi/\delta)/N})$, hence $N = O(\log(n/\delta)2^{\mathrm{polylog}(1/\epsilon)})$.

### Significance and applications

* Makes the provable ML approach practical: logarithmic data, almost linear time, arbitrary distribution. Together with Onorati et al. (who provide worst-case guarantees and thermal phases), the state of the art for "learning across a phase".
* The Pauli 1-norm bound is useful independently; related inequalities appear in Huang, Chen, Preskill (Corollary 4 there) with other techniques.
* The hardness statement shows the "power of data": data are a resource that circumvents NP-hardness.

### Relation to this project

* This is the provable learned decoder of the tables and the closest relative of this project's CNN: a feature map with an inductive bias (geometry here, coprime folding there), a linear learner on top, and a guarantee that follows from the structure of the target function. The difference: here the target function is provably smooth and local; there the structure (top-$k$ support in the displacement spectrum) is a conjecture.
* The lower bound $n^{\Omega(1/\epsilon)}$ *without* geometry versus $\log n$ *with* geometry is the cleanest example of how a promise changes the exponent; for this project the question is which additional knowledge (dictionary, subgroup, gap) plays the same role.
* Objective 4 of the project (ground states, Gibbs states) hits exactly the families of states of this paper; the numerical template (2D Heisenberg, 45 qubits, RMSE against $N$, $T$, $n$) can be adopted.

### Limitations and open questions

* $2^{\mathrm{polylog}(1/\epsilon)}$ is quasi-polynomial in $1/\epsilon$; polynomial is open.
* Known geometry is necessary; without it, the lower bound of the predecessor applies.
* Gapped ground states only; thermal phases and critical points in Onorati et al.
* Guarantee on average over $\mathcal{D}$, not pointwise.

### Questions for further study

* What does the feature map look like for displacement observables, whose "geometry" is the phase space $(q,p)$: what replaces $d_{\mathrm{qubit}}$, and is $S^{(\mathrm{geo})}$ then the dictionary?
* Does Theorem 2 (Pauli 1-norm) hold for sums of displacement operators with bounded operator norm, and what follows for the $\ell_1$ norm of the displacement spectrum of a ground state?
* Can spectral-flow locality be used to show that ground states of local Hamiltonians have a *sparse* displacement spectrum in a suitable basis?

Paper: [arXiv:2301.13169](https://arxiv.org/abs/2301.13169)

---
## Efficient learning of ground & thermal states within phases of matter (arXiv:2301.12946)

The paper by **Emilio Onorati, Cambyse Rouzé, Daniel Stilck França, and James D. Watson** (TU Munich, ENS Lyon, Maryland; 2023) treats two tasks: (a) tomography of a single Gibbs state to within Wasserstein distance $n\epsilon$ from $\mathrm{polylog}(n)$ copies, which yields all Lipschitz observables, i.e. all extensive quantities including entropies, at once; (b) learning local observables across an entire thermal or ground-state phase from $N = O(\log(M/\delta)e^{\mathrm{polylog}(1/\epsilon)})$ samples with a *worst-case* guarantee over the parameter space. Compared with Huang, Kueng, Torlai, Albert, Preskill, this is an exponential improvement in $\epsilon$, an extension to thermal phases, and pointwise instead of averaged guarantees.

### Placement in the tables

* **Task type:** Estimating, in two variants. In (a) the list "all Lipschitz observables" is implicit and exponential, and the output is a parametrization $x_0$ of the Gibbs state. In (b), $M$ local observables are given, and their values are returned for all $x$ in the phase. Rows "Ground-state properties across a phase from shadows" and, for (a), an addition to the Gibbs row.
* **Object:** Gibbs states $\sigma(\beta, x) = e^{-\beta H(x)}/\mathrm{tr}$ and ground states $\psi_g(x)$ of local Hamiltonians on a $D$-dimensional lattice. **Access:** sample, single copies, classical shadows of the training states.
* **Status:** 🟢 🟢 🟢. Copies $\mathrm{polylog}(n)$; the time complexity is inherited from the Hamiltonian learners used (Anshu et al. for commuting models, Haah–Kothari–Tang at high temperature).
* **Promise:** exponential decay of correlations (Eq. II.2) for (a) and thermal phases in (b); for ground states GALI, generalized approximate local indistinguishability, which includes gapped phases; for (b) additionally an anticoncentrated distribution over $x$ (for instance the uniform one).

### The problem

Shadows learn local observables with $\log n$ copies, but exponentially in the size of the support; Hamiltonian learning from Gibbs states (Anshu et al., Haah et al.) reconstructs the parameters, but trace-distance guarantees cost polynomially in $n$. Rouzé and França had connected the two via transportation cost inequalities, but only for topologically trivial states (commuting high-temperature Gibbs states, shallow circuits). For learning across phases, HKTAP had exponential $\epsilon$ dependence, only gapped ground states, and only guarantees on average.

### Key results

* **Theorem II.3 (Gibbs tomography).** For commuting Gibbs states with exponential decay of correlations, $N = O(\log(\delta^{-1})\mathrm{polylog}(n)\epsilon^{-2})$ copies give an $x_0$ with $W_1(\sigma(\beta,x), \sigma(\beta,x_0)) \leq n\epsilon$; non-commuting at $\beta < \beta_c$ likewise, and under uniform clustering plus an approximate Markov property with $\epsilon^{-4}$.
* **Continuity bound (Eq. II.4).** $W_1(\sigma(\beta,x), \sigma(\beta,y)) = \Vert x - y\Vert_{\ell_1}O(\mathrm{polylog}\,n)$, tight up to the polylog at $\beta = \Theta(1)$; the proof uses quantum belief propagation. With this, $W_1$ reconstruction reduces to $\ell_1$ parameter learning.
* **Corollary II.4 (entropies).** The von Neumann entropy, conditional entropy, mutual information, and conditional mutual information of arbitrarily large regions change only by $\Vert x|_{S(r_S)} - y|_{S(r_S)}\Vert_{\ell_1}\mathrm{polylog}$, so they can be read off from the parameter estimate with multiplicative error; shadows need a cost exponential in the region for this.
* **Theorem II.5 (learning in thermal phases).** With $N = O(\log(M/\delta)\log(n/\delta)e^{\mathrm{polylog}(\epsilon^{-1})})$ samples $(x_i, \tilde\sigma(\beta,x_i))$ from the uniform distribution over $\Phi$ there is an estimator with $\sup_{x\in\Phi}|f_O(x) - \hat f_O(x)| \leq\epsilon\sum_i\Vert O_i\Vert_\infty$ for local $O = \sum_i O_i$.
* **Theorem II.7 (GALI).** The same guarantee for families of ground or Gibbs states with generalized approximate local indistinguishability (Definition II.6): for every region $S$ and radius $r$ there are parameters outside $S(r)$ whose choice changes the expectation values on $S$ only by $(|S|f(r) + \eta(S))\Vert O\Vert_\infty$; gapped ground-state phases satisfy this (Lieb–Robinson, spectral flow).

### Methodological approach

* **Wasserstein instead of trace distance.** Lipschitz observables $\Vert L\Vert_{\mathrm{Lip}} = \max_i\min_{L_{i^c}}2\Vert L - L_{i^c}\otimes I_i\Vert_\infty$ and the dual distance $W_1$; $W_1 = O(\epsilon n)$ is, for extensive observables, the same as multiplicative accuracy $\epsilon$, but costs exponentially less than trace distance $O(\epsilon)$ (already for product states).
* **$W_1$ strong convexity** of the log-partition function, which scales linearly in $n$ under clustering and the Markov condition, as a generalization of the $\ell_2$ convexity in Anshu et al.
* **Learning in the phase.** Training points $Y_1, \dots, Y_N$ uniformly distributed; for each observable $O_i$ with support $S_i$, the shadows of the $t\approx\log n$ training states whose *local* parameters are close to $x$ are averaged; belief propagation shows that local expectation values are smooth in the local parameters under exponential decay of correlations. Anticoncentration of the distribution guarantees that every small parameter region contains enough training points. This is concentration of measure, not ML in the narrow sense.

### Significance and applications

* Together with Lewis et al., the state of the art for "learning across a phase": Lewis et al. have $O(\log n)$ data for arbitrary distributions on average, Onorati et al. worst-case guarantees for anticoncentrated distributions and thermal phases; both are quasi-polynomial in $1/\epsilon$.
* Corollaries C.4 and C.6 are new classically as well ($W_1$ learning of Gibbs measures); there are classical Ising phases with decay of correlations but without a known sampler, and the results hold nonetheless.
* Robust shadow tomography algorithms for Gibbs and ground states and Gibbs approximations of locally indistinguishable ground states are tools of independent value.

### Relation to this project

* For Objective 4 (Gibbs and ground states), this is the statement that these classes of states can be described completely *as classes* with $\mathrm{polylog}(n)$ copies as soon as correlations decay exponentially. The question for this project is whether the same structure implies a sparse displacement spectrum, and the continuity bound Eq. II.4 is a tool for tracking sparsity along a phase.
* The distinction "on average" versus "pointwise" is the same one this project's paper has to make between scaling over instance distributions and a guarantee for every instance; the paper shows that the price of pointwise guarantees is an anticoncentration condition, not a loss in $n$.
* The mixedness factor of this project's taxonomy is controlled here by $\beta$; the table of conditions (commuting, high temperature, Markov, GALI) is a template for the instance ladder.

### Limitations and open questions

* Anticoncentration is necessary; distributions with large regions of small probability are excluded (Appendix D).
* For non-commuting Gibbs states outside the high-temperature regime, everything hinges on clustering plus the Markov property, which is conjectured for many models but not proven.
* $e^{\mathrm{polylog}(1/\epsilon)}$ in the accuracy.
* The time complexity is not proven separately but inherited.

### Questions for further study

* Is $\Vert D_{q,p}\Vert_{\mathrm{Lip}}$ bounded on a qudit lattice, and what does $W_1$ closeness say about the displacement spectra of two Gibbs states?
* What does the approximate Markov condition look like in the displacement basis, and does it imply a factorization of the spectrum that a best-first decoder could exploit?
* Can GALI be operationalized as a promise for the instance ladder, i.e. measured without knowing the Hamiltonian?

Paper: [arXiv:2301.12946](https://arxiv.org/abs/2301.12946)

---

## Learning to predict arbitrary quantum processes (arXiv:2210.14894)

The paper by **Hsin-Yuan Huang, Sitan Chen, and John Preskill** (Caltech, Berkeley, AWS; *PRX Quantum* 4, 040337 (2023)) gives an efficient ML algorithm that, for an *arbitrary* unknown $n$-qubit process $\mathcal{E}$, even one with exponentially many gates, predicts every local property $\mathrm{tr}(O\mathcal{E}(\rho))$ of the output with small mean error over input states $\rho$ from a *locally flat* distribution, after training on $N = O(\log n)$ experiments with random product states and random Pauli measurements. The proof yields a quantum Bohnenblust–Hille inequality via an improved optimization algorithm for local Hamiltonians.

### Placement in the tables

* **Task type:** Estimating, average case over inputs. Given: access to $\mathcal{E}$, a family of observables $O$ of bounded degree, a distribution $\mathcal{D}$; returned is $h(\rho, O)\approx\mathrm{tr}(O\mathcal{E}(\rho))$. The row "Predicting arbitrary quantum processes".
* **Object:** channel. **Access:** sample in the sense of the tables: non-adaptive application to random product states with single-copy Pauli measurements, i.e. the input–output data state; the authors call it access to $\mathcal{E}$, but nothing is chosen adaptively or in superposition.
* **Status:** 🟢 🟢 🟢 for constant $\epsilon$: $N = \log n\cdot\min(2^{O(\log(1/\epsilon)(\log\log(1/\epsilon) + \log(1/\epsilon')))}, 2^{O(\log(1/\epsilon)\log n)})$, time $O(kn^kN)$ with $k = \Theta(\log 1/\epsilon)$; hence $n^{O(\log 1/\epsilon)}$ at $\epsilon' = 0$.
* **Promise:** a locally flat distribution $\mathcal{D}$ (invariant under single-qubit Cliffords on every qubit) and observables of bounded degree ($O(1)$ terms per qubit, $\Vert O\Vert \leq 1$). No promise about $\mathcal{E}$.

### The problem

A CPTP channel has exponentially many parameters; covering arguments, shadow tomography, and process tomography need exponentially many data for arbitrary $\mathcal{E}$ and $\rho$. For polynomially generated $\mathcal{E}$, polynomially many data suffice, but the running time stays exponential. What is sought: an algorithm that learns arbitrary $\mathcal{E}$ efficiently if the error is measured on average over a sensible input distribution.

### Key results

* **Theorem 1.** With $N = O(\log n)$ training data $S_N(\mathcal{E})$ (product stabilizer states as input, randomized Pauli measurement at the output, $O(nN)$ bits), the algorithm learns $h(\rho, O)$ with $\mathbb{E}_{\rho\sim\mathcal{D}}|h(\rho,O) - \mathrm{tr}(O\mathcal{E}(\rho))|^2 \leq\epsilon + \max(\Vert O'\Vert^2, 1)\epsilon'$ for every locally flat $\mathcal{D}$ and every $O$ of bounded degree, with $O'$ the degree-$k$ truncation of the Heisenberg-evolved $\mathcal{E}^\dagger(O)$.
* **Learning states (Section II.A).** An improved shadow norm: all observables of bounded degree with $\Vert O\Vert\leq B$ from $N = O(\log(n)B^2/\epsilon^2)$ random Pauli measurements (previously $O(n\log n\,B^2/\epsilon^2)$), with a matching lower bound, also for collective measurements.
* **Learning observables (II.B).** Under locally flat $\mathcal{D}$, the degree-$k$ truncation $O^{(k)}$ of $O$ with $\Vert O\Vert = O(1)$ is accurate up to $e^{-\Omega(k)}$ (Lemma 14); it suffices to learn a few large coefficients; training on the fixed distribution $\mathcal{D}'$ (random product stabilizer states) suffices for all locally flat $\mathcal{D}$.
* **Corollaries 1 and 2 (optimization).** Randomized algorithms running in $O(n^k)$ and $O(nd)$ respectively find product states with energy $C(k)(\sum|\alpha_P|^{2k/(k+1)})^{(k+1)/2k}$ and $\frac{C}{\sqrt d}\sum|\alpha_P|$ respectively above or below the Haar average, $C(k) = 1/\exp(\Theta(k\log k))$, via polarization instead of random restriction.
* **Corollaries 3 and 4 (norm inequalities).** $\frac13C(k)\Vert H\Vert_{\mathrm{Pauli},2k/(k+1)} \leq\Vert H\Vert$ for $k$-local $H$ (proves the conjecture of Rouzé, Wirth, Zhang on the quantum Bohnenblust–Hille inequality) and $\frac13C(k,d)\Vert H\Vert_{\mathrm{Pauli},1} \leq\Vert H\Vert$ for bounded degree $d$.
* **Numerics.** Prediction of quantum dynamics with evolution times up to $10^6$ and 50 qubits.

### Methodological approach

1. **Reduction.** $\mathrm{tr}(O\mathcal{E}(\rho)) = \mathrm{tr}(\mathcal{E}^\dagger(O)\rho)$: the output $\mathcal{E}(\rho_\ell)$ is an unknown state (shadows learn it for bounded degree), and $\mathcal{E}^\dagger(O)$ is an unknown observable (low-degree learning over locally flat distributions). Together, the two learn the process.
2. **Algorithm (III.A).** Empirical Pauli coefficients $\hat x_P(O)$ from the data for all $|P|\leq k$, thresholding $\hat\alpha_P = 3^{|P|}\hat x_P$ if large, otherwise $0$; prediction $h(\rho,O) = \sum_P\hat\alpha_P\mathrm{tr}(P\rho)$ from the $k$-RDMs of $\rho$, which are available classically or via shadows.
3. **Norm inequalities from optimization.** A state with energy clearly above the Haar average proves a lower bound on $\Vert H\Vert$ in terms of the Pauli coefficients; polarization (replicate the qubits, fix all but the last replica at random, optimize the last one, average with random signs) yields the Bohnenblust–Hille form.

### Significance and applications

* Arbitrary processes become learnable in the average case; the contrast with process tomography and with the worst case is the statement of the "power of data".
* The quantum Bohnenblust–Hille inequality with constant $\exp(\Theta(k\log k))$ matters independently; Klein, Slote, Volberg, Zhang carry it over to qudits, Arunachalam et al. to channels.
* The observable-centered view of shadows (Lemma 1.10 in Bakshi et al.) originates here.

### Relation to this project

* The truncation statement "under locally flat distributions, $\mathcal{E}^\dagger(O)$ is effectively low-degree" is a mechanism that produces an *implicit* sparsity promise: not the process is sparse, but what the input distribution sees of it. For this project's conjecture, this is a model for how average-case decodability can come from the instance distribution, not from the state alone.
* The thresholding procedure (keep large coefficients, zero out small ones) is the Eskenazis–Ivanisvili decoder and the algorithmic form of "top-$k$"; the Bohnenblust–Hille inequality is the guarantee that it works. The analogous inequality for displacement coefficients would be the provable core of this project's dictionary regime.
* $n^{O(\log 1/\epsilon)}$ is quasi-polynomial: the time scales with the number of candidates $n^k$, which corresponds to the enumeration strategy of the dictionary regime.

### Limitations and open questions

* Quasi-polynomial time in $1/\epsilon$; impractical for small errors.
* Locally flat distributions are a strong assumption about the inputs; nothing holds for inputs from a fixed experiment without randomization.
* The optimization algorithms cannot choose whether they maximize or minimize.
* No statement about the worst case over inputs.

### Questions for further study

* What is a "locally flat" distribution over qudit states if the local group is the Heisenberg–Weyl group instead of the Clifford group, and does Lemma 14 then hold for the displacement degree?
* What does the polarization technique look like for displacement Hamiltonians $\sum_{q,p}\alpha_{q,p}(D_{q,p} + D_{q,p}^\dagger)$, and which Bohnenblust–Hille constant results?
* Can this project's CNN be read as a learner of $\mathcal{E}^\dagger(O)$ if $\mathcal{E}$ is the preparation of the state from a reference state?

Paper: [arXiv:2210.14894](https://arxiv.org/abs/2210.14894)

---

## Learning low-degree quantum objects (arXiv:2405.10933)

The paper by **Srinivasan Arunachalam, Arkopal Dutt, Francisco Escudero Gutiérrez, and Carlos Palazuelos** (IBM Quantum, QuSoft/CWI, UCM/ICMAT; 2024) learns quantum objects of low Pauli degree $d$ to within $\ell_2$ error $\epsilon$: channels and unitaries with $\exp(\tilde O(d^2 + d\log 1/\epsilon))$ queries, independent of $n$; polynomials from $d$-query quantum algorithms classically from $O((1/\epsilon)^d\log n)$ random examples, hence also for $d = O(\log n)$; degree-$d$ polynomials from $O(1/\epsilon^d)$ queries to a block encoding. The technical core consists of new Bohnenblust–Hille inequalities: for completely bounded tensors with constant $1$, for channels with constant $\exp(d)$.

### Placement in the tables

* **Task type:** Estimating. Given is the implicit list of all Pauli coefficients up to degree $d$; all of them are returned. The row "Low-degree quantum objects" of the estimating table; next to it the table names Volberg–Zhang (2023) for the noncommutative BH inequality, while 2301.01438 (Klein, Slote, Volberg, Zhang) is the qudit paper, see the following summary.
* **Object:** channel $\Phi(\rho) = \sum_{x,y}\hat\Phi(x,y)\sigma_x\rho\sigma_y$, unitary $U = \sum_x\hat U(x)\sigma_x$, classical polynomials. **Access:** query: the learner chooses input states, applies $\Phi$ or $U$ (and $\mathrm{c}U$), and measures in an arbitrary basis. The row therefore sits in the query block; the warning ⚠️ in the table is hereby resolved for channels and unitaries.
* **Status:** 🟢 🟢 🟢 for constant $d$: queries independent of $n$, time polynomial; $\exp(d^2)$ is still polynomial for $d = O(\sqrt{\log n})$.
* **Promise:** degree $\leq d$: $\hat\Phi(x,y) = 0$ for $|x| + |y| > d$.

### The problem

Linial–Mansour–Nisan learn $\mathrm{AC}^0$ via low-degree approximation; Eskenazis–Ivanisvili brought low-degree learning down to $O(\log n)$ samples, because BH inequalities say that most coefficients are small. For quantum objects there were BH inequalities for observables (Huang–Chen–Preskill, Volberg–Zhang) with $\log n$ dependence. The question: can channels, unitaries, and query algorithms be learned with complexity polynomial or polylogarithmic in $n$, and what are the right BH inequalities?

### Key results

* **Theorem 12 (BH for channels).** $\big(\sum_{x,y}|\hat\Phi(x,y)|^{2d/(d+1)}\big)^{(d+1)/2d} \leq\exp(d)$ for degree-$d$ channels, more generally for superoperators bounded in the $S_1\to S_\infty$ norm; generalizes the operator BH inequalities of Huang et al. and Volberg–Zhang.
* **Theorem 19 (BH for completely bounded tensors).** Constant $1$ instead of $\mathrm{poly}(d)$ for $d$-linear tensors that are amplitudes of $d$-query algorithms (Arunachalam, Briët, Palazuelos).
* **Theorem 1 (channels).** $(\epsilon,\delta)$-learning in $\ell_2$ with $\exp(\tilde O(d^2 + d\log 1/\epsilon))\log(1/\delta)$ queries; general channels need $\Omega(4^n)$.
* **Proposition 2 (Pauli channels).** Degree-$d$ Pauli channels in diamond norm with $O(n^{2d}/\epsilon^2\cdot\log(n/\delta))$ queries, using only product states and Pauli measurements; the same $n$ dependence as Flammia–O'Donnell (population recovery), but Fourier-analytic.
* **Theorem 3 (unitaries).** Degree-$d$ unitaries with $\exp(\tilde O(d^2 + d\log 1/\epsilon))\log(1/\delta)$ applications, via Montanaro–Osborne for coefficient estimation and Volberg–Zhang for truncation. Question 4: is $\sum_x|\hat U(x)| \leq C(d)$? Then $1/\epsilon^2$ would be possible.
* **Theorem 5 (query algorithms).** Amplitudes $T(x) = \langle v|\Psi_x\rangle$ of $d$-query algorithms (for instance $k$-Forrelation) classically from $O((1/\epsilon)^d\log n)$ uniform examples, exponentially better than Eskenazis–Ivanisvili's $(d/\epsilon)^{O(d)}\log n$, polynomial in $n$ even for $d = \omega(\log n)$.
* **Facts 6, 7 (Boolean functions).** Degree-$d$ Boolean functions exactly from $O(4^dd\log 1/\delta)$ quantum examples (granularity $2^{1-d}$), classically $\Omega(2^d\log n)$; a BH-type inequality for Boolean functions.
* **Remark (states).** Degree-$d$ states in trace norm with $\tilde O(n^d/\epsilon^2\log(n/\delta))$ copies via classical shadows.

### Methodological approach

1. **Channels.** The matrix $\hat\Phi$ of Pauli coefficients is a density matrix, unitarily equivalent to the Choi state (Bao–Yao); it is prepared with one query. Computational-basis measurements sample $\{\hat\Phi(x,x)\}$, and $O(1/\alpha^2)$ samples find all $\alpha$-large diagonal entries; a SWAP test for mixed states estimates the large $\hat\Phi(x,y)$; all others are set to zero. With $T\sim\exp(d^2/\epsilon^d)$ and the BH inequality, the output is $\epsilon$-close in $\ell_2$.
2. **Unitaries.** Montanaro–Osborne's variant of Goldreich–Levin estimates large coefficients; the BH inequality of Volberg–Zhang justifies the truncation.
3. **Tensors.** The hybrid inequality between BH and Grothendieck for completely bounded multilinear forms.

### Significance and applications

* The first $n$-independent learning results for structured channels and unitaries; applications to short-time dynamics of local Hamiltonians (Lieb–Robinson makes $e^{-iHt}$ low-degree) and to noise models with sparse local Paulis.
* The BH inequality with constant $1$ is a contribution to functional analysis; the $\mathrm{poly}(d)$ versus $\exp(d)$ gap is explained as incomparable (tensors versus general polynomials).

### Relation to this project

* The channel algorithm is structurally this project's two-phase protocol on the Choi state: sampling finds the large diagonal entries (localization), a SWAP test estimates the coefficients (estimation), and the BH inequality replaces the conjecture. For states exactly this inequality is missing, because the normalization is $\sum|y_{q,p}|^2 = d$ instead of $1$; this is the normalization paragraph in the appendix ("What is learned") in pure form.
* Question 4 (is the $\ell_1$ norm of the coefficients of a degree-$d$ unitary bounded?) is the unitary version of the question whether the displacement spectrum of a class of states is $\ell_1$-bounded; for ground states of local Hamiltonians, Lewis et al. Theorem 2 gives an answer for observables, not for states.
* The $n$-independent query complexity is the query side of the quadrant: with control over the input, the dimension drops out of the sample count, while Bell sampling on states pays $\log d$.

### Limitations and open questions

* $\exp(d^2)$ is polynomial only for $d = O(\sqrt{\log n})$; the authors conjecture a $\mathrm{poly}(d)$ dependence.
* Only $\ell_2$ error for channels and unitaries; diamond norm only for Pauli channels.
* Question 4 is open; the Montanaro–Osborne conjecture (degree-$d$ unitaries are $2^d$-juntas) would answer it.
* States are treated only in a remark.

### Questions for further study

* What does the BH inequality for channels look like in the Heisenberg–Weyl basis of a qudit (combined with Klein et al.), and what is the "degree" of a displacement channel?
* The SWAP test for mixed states as a coefficient estimator: is it the two-copy measurement $\hat\Phi\otimes\hat\Phi$, and how does it relate to Bell sampling on $\hat\Phi\otimes\hat\Phi^*$?
* Can the step "sampling the diagonal with $O(1/\alpha^2)$" be read as a sample lower bound for localization in this project's protocol, where the diagonal is $|y_{q,p}|^2/d$?

Paper: [arXiv:2405.10933](https://arxiv.org/abs/2405.10933)

---

## Quantum and classical low-degree learning via a dimension-free Remez inequality (arXiv:2301.01438)

The paper by **Ohad Klein, Joseph Slote, Alexander Volberg, and Haonan Zhang** (Hebrew University, Caltech, Michigan State/Bonn, South Carolina; 2023) extends low-degree learning from the hypercube and from qubits to products of cyclic groups $\mathbb{Z}_K^n$ and to $K$-level qudits. The technical obstacle was that the standard proofs of the Bohnenblust–Hille inequality need, in the polarization step, a maximum principle that does not hold for the $K$-th roots of unity. The solution is a dimension-free Remez inequality: the supremum of a degree-$d$ polynomial over $\Omega_K^n$ controls its supremum over the whole polytorus $\mathbb{T}^n$ with constant $(O(\log K))^d$. From this follow $O(\log n)$-sample algorithms for qudit observables in the Heisenberg–Weyl and the Gell-Mann basis.

### Placement in the tables

* **Task type:** Estimating. Given samples $(\rho, \mathrm{tr}[A\rho])$, an $L^2$ approximation of the observable is returned, i.e. all coefficients up to the relevant degree. An addition to the row "Low-degree quantum objects" with the qudit variant; the table now names Klein, Slote, Volberg, Zhang for qudits.
* **Object:** observable on $n$ qudits of dimension $K$, or a function $f:\mathbb{Z}_K^n\to\mathbb{C}$. **Access:** sample: random product states from a fixed set and their expectation values; hence sample access in the sense of the tables, not query.
* **Status:** 🟢 🟢 🟢 at constant degree: samples $O(\log n)$, time polynomial.
* **Promise:** degree $\leq d$ in the chosen basis; for Theorem 4 none about $A$, but one about the distribution $\mu$, under which low-degree truncations are good approximations.

### The problem

Eskenazis–Ivanisvili reduce low-degree learning to an $\ell_p$ bound, $p < 2$, on the Fourier coefficients (BH inequality), because then most coefficients are small and zeroing out below a threshold gives an $n$-independent $\ell_2$ error. For qubits the BH inequality exists (Huang–Chen–Preskill; Volberg–Zhang). For qudits in the Heisenberg–Weyl basis (clock and shift, eigenvalues $K$-th roots of unity) one needs BH over $\mathbb{Z}_K^n$, the unstudied case between the hypercube ($K = 2$) and the polytorus ($K = \infty$), and the standard proof breaks because $\Omega_K$ is not the boundary of its convex hull; already for $n = 1$, $K = 3$ there is an $f$ with $\Vert f\Vert_{\mathrm{conv}(\Omega_K)} > \Vert f\Vert_{\Omega_K}$.

### Key results

* **Theorem 5 (dimension-free Remez inequality).** For $f$ of degree $d$ with individual degree $\leq K-1$: $\Vert f\Vert_{\mathbb{T}^n} \leq (O(\log K))^d\Vert f\Vert_{\Omega_K^n}$; apparently the first discrete multidimensional Remez inequality with a dimension-free constant.
* **Corollary 6 (cyclic BH).** $\Vert\hat f\Vert_{2d/(d+1)} \leq (O(\log K))^{d + \sqrt{d\log d}}\Vert f\Vert_{\Omega_K^n}$, directly from Theorem 5 and the polytorus BH.
* **Theorem 3 (cyclic low-degree learning).** Degree-$d$ functions $f:\mathbb{Z}_K^n\to\mathbb{D}$ from $(\log K)^{O(d^2)}\log(n/\delta)\epsilon^{-d-1}$ uniform examples to within $\Vert f - \tilde f\Vert_2^2 \leq\epsilon$ in polynomial time, against $\mathrm{poly}(n)$ naively.
* **Theorem 4 (qudit observables).** For *arbitrary* bounded observables $A$ on $n$ $K$-level qudits and a class of distributions $\mu$ over states: $\mathbb{E}_{\rho\sim\mu}|\mathrm{tr}[A\rho] - \mathrm{tr}[\tilde A\rho]|^2 \leq\epsilon$ from $s \leq O(\log(n/\delta)C^{\log^2(1/\epsilon)}K^{3/2}\Vert A_{\leq t}\Vert_{\mathrm{op}}^{2t})$ samples, $t\approx\log(1/\epsilon)$, drawn from the uniform distribution over a fixed set of product states; the class of $\mu$ extends the locally flat distributions of Huang, Chen, Preskill to qudits and yields new distributions for qubits as well.
* **Two bases.** Gell-Mann reduces to the hypercube BH; Heisenberg–Weyl to the cyclic BH, hence to Theorem 5.

### Methodological approach

* **Lemma 7 (DFT interpolation).** For $z\in\mathbb{T}$ there is a $c$ with $z^k = \sum_j c_j\omega^{jk}$ for $k < K$ and $\Vert c\Vert_1 \leq B\log K$, from the DFT coefficients of $(1, z, \dots, z^{K-1})$ and the harmonic number $H_K$. In one coordinate, Hölder immediately gives the Remez inequality.
* **Correlated randomness.** Coordinate-wise repetition would cost $(\log K)^n$; instead the sum is read as an expectation over a complex measure and the $n$ variables are correlated, so that the constant depends only on the degree. Two proofs exist; the one given here has the better constant for learning applications.
* **Learning algorithm.** Fourier sampling of the coefficients, zeroing out below the threshold (Eskenazis–Ivanisvili, slightly generalized), Plancherel for the $\ell_2$ error.

### Significance and applications

* Opens low-degree learning theory to qudit processors, which bring practical advantages in the NISQ era, and to functions on hypergrids.
* The Remez inequality is a tool of independent value: a bridge from discrete spaces back to classical harmonic analysis on the polytorus.
* Shows that the Heisenberg–Weyl basis does *not* have the same analysis as the Pauli basis: the roots of unity are a genuine obstacle, not a technical one.

### Relation to this project

* This is the paper that makes Fourier analysis in the Heisenberg–Weyl basis of a qudit rigorous; for a single qudit ($n = 1$, $K = d$), the displacement coefficients $y_{q,p}$ are exactly the coefficients in this basis, and the cyclic BH inequality is the statement that an operator of bounded norm with "low degree" in $(q,p)$ has an $\ell_{2d/(d+1)}$-bounded spectrum.
* The degree here is $|\alpha| = \sum_j\alpha_j$ with $\alpha_j\in\{0, \dots, K-1\}$, i.e. the size of the shift; for $n = 1$, "low degree" means "small $q$ and $p$". This is a promise that is missing from this project's instance ladder and would be provable: states with a displacement spectrum close to the origin of phase space.
* The constant $(\log K)^{O(d^2)}$ becomes useless as the degree approaches $K$ (the full phase space); this is the point at which low-degree learning stops and sparsity learning with LWE hardness begins.

### Limitations and open questions

* The constant $(O(\log K))^d$ can be improved for $d\ll K$ or highly composite $K$; extensions to $L^p$ are announced.
* Only uniform samples on product states; adaptive or non-uniform access is not treated.
* Theorem 4 needs $\Vert A_{\leq t}\Vert_{\mathrm{op}}$ of the truncation, which can be large for general $A$.
* Composite $K$ is allowed (cyclic group, not a field), but only for functions and observables, not for states.

### Questions for further study

* Does a cyclic BH inequality hold for states with the normalization $\sum|y_{q,p}|^2 = d$, for instance after rescaling $\rho\mapsto d\rho$, and what does it say about the number of large coefficients?
* What is the "degree" of a ground state of a displacement Hamiltonian, and is it small when the couplings $D_{q,p}$ have only small $(q,p)$?
* What does the correlated randomization of the proof look like when read as a sampling rule for probe states in Phase 2?

Paper: [arXiv:2301.01438](https://arxiv.org/abs/2301.01438)

---

## Optimal learning of quantum Hamiltonians from high-temperature Gibbs states (arXiv:2108.04842)

The paper by **Jeongwan Haah, Robin Kothari, and Ewin Tang** (Microsoft Quantum, Washington; FOCS 2022) solves the learning of the coefficients of a Hamiltonian from copies of its Gibbs state in the high-temperature regime optimally: $O(\log N/(\beta^2\epsilon^2))$ copies for $\ell_\infty$ error $\epsilon$ and running time linear in the data size, with a matching lower bound $\Omega(e^\beta\log N/(\beta^2\epsilon^2))$ for all $\beta$. The Hamiltonian may be low-intersection (no geometry needed), and almost the same algorithm learns $H$ from $e^{-itH}$ at constant $t$.

### Placement in the tables

* **Task type:** Estimating. The terms $E_a$ are known; the coefficients $\lambda_a$ are sought. The row "Hamiltonian coefficients from Gibbs states, known terms"; the paper is the reason for "polynomial at high temperature" in the time column.
* **Object:** Hamiltonian, from copies of its Gibbs state. **Access:** sample; each copy is measured in local Pauli bases, and only the local marginals are needed.
* **Status:** 🟢 🟢 🟢 at $\beta < \beta_c$: copies logarithmic, time $O(SN)$, memory the coefficients. For low temperatures 🔴 in time until Bakshi, Liu, Moitra, Tang (2024).
* **Promise:** low intersection ($O(1)$ qubits per term, $O(1)$ terms per qubit, no geometry), $\beta$ below a critical constant $\beta_c$ that depends only on the low-intersection constants.

### The problem

Classically, learning Markov random fields has been studied for 50 years; parameter learning costs $2^{O(\beta)}\log N/(\beta^2\epsilon^2)$ samples and as much time times $N$ (folklore, Appendix B). Anshu, Arunachalam, Kuwahara, and Soleimanifar had, for geometrically local quantum Hamiltonians, $O(2^{\mathrm{poly}(\beta)}N^2\log N/(\beta^c\epsilon^2))$ copies and no explicit time bound. Quantumly the Markov property (Hammersley–Clifford) is missing, so classical algorithms do not carry over. The questions: reach the classical sample complexity, and the time.

### Key results

* **Theorem 1.1.** For low-intersection $H$ and $\beta < \beta_c$: $\ell_\infty$ error $\epsilon$ with $O(\log(N/\delta)/(\beta^2\epsilon^2))$ copies, $\ell_2$ error with $O(N\log(N/\delta)/(\beta^2\epsilon^2))$; time linear in the number of copies times $N$.
* **Theorem 1.2 (lower bound).** For every $\beta$ there is a 2-local $H$ (disjoint two-qubit terms) that forces $\Omega(e^\beta\log(N/\delta)/(\beta^2\epsilon^2))$ copies for $\ell_\infty$ and $\Omega(e^\beta N/(\beta^2\epsilon^2))$ for $\ell_2$; this considerably improves the earlier $\Omega((\sqrt N + \log(1-\delta))/(\beta\epsilon))$.
* **Theorem 1.3 (real-time dynamics).** From $U = e^{-itH}$ with known $t < t_c$: $O(\log(N/\delta)/(t^2\epsilon^2))$ applications, time $O(N\log(N/\delta)/(t^2\epsilon^2))$; constant time resolution instead of $O(\epsilon)$, copies quadratically better than derivative estimation with $1/\epsilon^4$.
* **Strong convexity.** The log-partition function is $\Theta(\beta^2)$-strongly convex at high temperature, the true value up to constants; hence $\mathrm{Var}(\sum v_aE_a) = \Omega(\beta^2\Vert v\Vert_2^2)$ in thermal equilibrium.
* **Comparison.** Naive tomography of a patch: quasi-polynomial; Anshu et al.: $N^2\log N/(\beta^c\epsilon^2)$ copies and roughly $N^3\log N$ time; here $\log N/(\beta^2\epsilon^2)$ and $N\log N/(\beta^2\epsilon^2)$, superpolynomially better in certain regimes.

### Methodological approach

1. **Cluster expansion** (Kuwahara–Saito): the Taylor series of $\mathrm{Tr}(E_a\rho)$ in $\beta$ converges for $\beta < \beta_c$; $\partial_{\lambda_a}\log\mathrm{Tr}\,e^{-\beta H} = -\beta\,\mathrm{Tr}(E_a\rho)$ connects expectation values with the log-partition function. Only $O(1/(\beta\epsilon))$ terms within distance $\log(1/(\beta\epsilon))$ of the support of $E_a$ count.
2. **Explicit computation** of the cluster derivatives (Proposition 3.13, Algorithm 2) in exact arithmetic, because the $E_a$ are Paulis; earlier work only claimed computability.
3. **Polynomial system of equations.** The truncated series are polynomials in $\lambda$; the $\infty\to\infty$ norm of the inverse Jacobian gives the sample complexity (Theorem 4.2), Newton–Raphson with $O(\log(1/(\beta\epsilon)))$ iterations solves it, and the running time is dominated by reading the input (Theorem 4.6).
4. **Lower bound** via Fano and KL divergence as for classical Markov fields (Santhanam–Wainwright), $\ell_2$ via error-correcting codes.

### Significance and applications

* Optimal in all parameters; the first time bound for quantum Hamiltonian learning from Gibbs states. The table of this document has "🔴→🟢" in the time entry of the Gibbs row precisely because of this paper and its successor at arbitrary constant temperature.
* Structure learning remains open: classically it works via parameter learning on all $k$-local terms with the low-intersection guarantee; quantumly the algorithm works only for $\beta < 1/\mathrm{poly}(N)$; Bakshi et al. solve it in 2024 from the dynamics.

### Relation to this project

* This is the "known terms" row against which structure learning (searching table) is defined: here the list of terms is the dictionary, and the algorithm estimates coefficients over a dictionary from local marginals. Regime 1 of this project is the same structure with displacement addresses instead of Pauli terms.
* The cluster expansion is a sparsity statement about Gibbs states at high temperature: expectation values depend only on a few nearby terms. For Objective 4 (Gibbs states), this is the mechanism that makes a sparse, or at least localized, displacement spectrum plausible at high temperature, and $\beta_c$ is the boundary from which the instance ladder becomes hard.
* The lower bound $e^\beta$ shows that low temperature drives *sample* cost, not only time; the mixedness factor therefore cuts both ways.

### Limitations and open questions

* $\beta < \beta_c$; lower temperatures in polynomial time only in 2024 (Bakshi et al.), with a different technique.
* Structure learning from Gibbs states is open.
* The constant $\beta_c$ is implicit via the low-intersection parameters; it is not computed for concrete models.
* Theorem 1.3 needs a known, small $t$.

### Questions for further study

* What does the cluster expansion look like for a displacement Hamiltonian on a single qudit, where "intersection" has to be defined over phase space instead of over qubits?
* Is the log-partition function strongly convex in the displacement basis, and what is the analogue of $\beta_c$ for the instance ladder?
* Can Newton–Raphson on the sparse surrogate of this project's protocol be used as a Phase 2 alternative to MMW?

Paper: [arXiv:2108.04842](https://arxiv.org/abs/2108.04842)

---
## Learning many-body Hamiltonians with Heisenberg-limited scaling (arXiv:2210.03030)

The paper by **Hsin-Yuan Huang, Yu Tong, Di Fang, and Yuan Su** (Caltech, Berkeley, Simons Institute, Microsoft; *Phys. Rev. Lett.* 130, 200403 (2023)) gives the first algorithm that learns an interacting $N$-qubit Hamiltonian from its dynamics at the Heisenberg limit: total evolution time $T = O(\epsilon^{-1}\log\delta^{-1})$ for every parameter, independent of $N$, with only $O(\mathrm{polylog}(\epsilon^{-1})\log\delta^{-1})$ experiments, robust against SPAM errors, without eigenstates or Gibbs states, and with a matching lower bound. The idea: reshape the Hamiltonian with quantum simulation techniques into non-interacting patches with known eigenvectors and run robust phase estimation there.

### Placement in the tables

* **Task type:** Estimating. The interaction graph (the set $S$ of Pauli terms) is known; the $\lambda_a$ are sought. The row "Heisenberg-limited Hamiltonian learning".
* **Object:** low-interaction Hamiltonian $H = \sum_a\lambda_aE_a$, $|\lambda_a|\leq 1$. **Access:** query, rung 3: interleaved sequences $V_{K+1}U(t_K)\cdots V_1$ with layers of single-qubit Clifford gates, i.e. control between the evolutions, which is provably necessary for Heisenberg scaling (Dutkiewicz, O'Brien, Schuster).
* **Status:** 🟢 🟢 🟢. Evolution time $1/\epsilon$, experiments polylogarithmic, classical time $O(N\mathrm{polylog}(\epsilon^{-1})\log\delta^{-1})$.
* **Promise:** known terms with $O(1)$ locality and $O(1)$ terms per qubit; geometric locality is not needed, but all-to-all interaction introduces an $N$ dependence in $T$.

### The problem

All earlier methods for many-body Hamiltonians (derivative estimation, gradient methods, polynomial interpolation) need $\epsilon^{-2}$ experiments and evolution time, the standard quantum limit. For one parameter or one qubit, metrology reaches the Heisenberg limit $\epsilon^{-1}$ via entangled states or long coherent evolution; for many-body systems, entanglement growth under $e^{-iHt}$ destroys the advantage, so one stayed at short times. Can the Heisenberg limit be reached for many-body Hamiltonians?

### Key results

* **Theorem 1.** A SPAM-robust algorithm with single-qubit Clifford experiments yields, after total evolution time $T = O(\epsilon^{-1}\log\delta^{-1})$, estimates with $\Pr[|\hat\lambda_a - \lambda_a|\leq\epsilon]\geq 1-\delta$ for every $a$; for all parameters simultaneously $T = O(\epsilon^{-1}\log(N/\delta'))$. Number of experiments $O(\mathrm{polylog}(\epsilon^{-1})\log\delta^{-1})$, Clifford layers $O(\epsilon^{-1.5}\mathrm{polylog})$.
* **Theorem 2 (lower bound).** Every SPAM-robust algorithm with arbitrary adaptive experiments needs $T = \Omega(\epsilon^{-1}\log\delta^{-1})$: an algorithmic proof of the Heisenberg limit including $\delta$.
* The number of experiments falls below $\epsilon^{-1}$; this does not contradict the Heisenberg limit, which is defined via the total time.

### Methodological approach

1. **Reshaping.** For unitaries $U_k$ and weights $w_k$, $\tilde H = \sum_kw_kU_kHU_k^\dagger$ is a new unknown Hamiltonian under which one can evolve via qDRIFT or Trotter (forward evolution only, no higher orders) without knowing $H$, because $e^{-itU_kHU_k^\dagger} = U_ke^{-itH}U_k^\dagger$.
2. **One qubit.** $\frac12(H + XHX) = \lambda_xX$ removes $Y$ and $Z$; robust phase estimation (Kimmel, Low, Yoder) with long coherent evolution on the known eigenstate of $X$ gives $\lambda_x$ in time $O(\epsilon^{-1}\log\delta^{-1})$.
3. **A few qubits.** Averaging over $I, X_1, Z_2, X_1Z_2$ leaves only terms with $I$ or $X$ on qubit 1 and $I$ or $Z$ on qubit 2; the eigenbasis $\{|\pm\rangle|0/1\rangle\}$ is known, eigenvalue differences come from phase estimation, parameters from a Hadamard transform.
4. **Divide and conquer.** A Pauli twirl of an intermediate qubit ($\frac14(H + XHX + YHY + ZHZ)$ on qubit 3) decouples the chain into patches without entanglement between them; all patches are learned in parallel, with colorings for the coupling terms.
5. **Error analysis** of randomization and Trotterization (Appendices D, F); the lower bound via TV distance bounds per experiment (Appendix G).

### Significance and applications

* The first Heisenberg-limited many-body learning; the successors (Dutkiewicz et al. on the necessity of control; Bakshi et al. on structure learning at constant time resolution; Shin, Lee, Oh on long-time access) define themselves against this work.
* Practically attractive: only single-qubit Cliffords, SPAM-robust, no special states; the precision is limited by the speed of the single-qubit gates.
* Applications in sensing, device characterization, and many-body physics.

### Relation to this project

* The row is the evidence for the statement in the appendix ("The access-by-task quadrant") that query access improves the precision rate from $1/\epsilon^2$ to $1/\epsilon$; this project's protocol sits at rung 2 and does not have this rate. Whether amplitude estimation on the preparation circuit (the query route) would give a $1/\epsilon$ rate for displacement amplitudes is the query version of this project's task.
* Reshaping is a symmetrization technique: twirls over subgroups of the Pauli group project the Hamiltonian onto a commutant. In the Heisenberg–Weyl basis of a qudit, the analogue would be the twirl over a subgroup of the displacement group, which restricts the spectrum to a coset; this is a possible measurement-side preprocessing for Regime 2.
* The separation "experiments polylog, time $1/\epsilon$" indicates that the right cost measure depends on the access; in this project's scaling analysis, the number of copies is the analogue of the total time.

### Limitations and open questions

* Known terms; structure learning only in Bakshi et al.
* All-to-all interaction brings $N$ into $T$.
* The time resolution of the control pulses must be fine (Trotter steps); Bakshi et al. and Shin, Lee, Oh treat constant resolution and long-time access.
* No lower bound on the number of experiments or gates.

### Questions for further study

* What does reshaping look like in the displacement basis: which twirls remove which $(q,p)$ terms, and do the eigenbases stay known?
* Why does the absence of higher Trotter orders without backward evolution not prevent Heisenberg scaling, and where exactly does the factor $\epsilon^{-1.5}$ enter the gate count?
* What is the Heisenberg limit for learning a *state* (instead of a Hamiltonian) from its preparation circuit, and is $1/\epsilon$ per displacement amplitude achievable?

Paper: [arXiv:2210.03030](https://arxiv.org/abs/2210.03030)

---

## Efficient estimation of Pauli channels (arXiv:1907.12976)

The paper by **Steven T. Flammia and Joel J. Wallman** (Sydney, Yale, Quantum Benchmark, Waterloo; *ACM Trans. Quantum Comput.* 1(1), 2020) gives the first systematic sample complexity for Pauli channels with guarantees in *relative* precision and robust against SPAM errors: the full channel on $n$ qubits with $O(\epsilon^{-2}n2^n)$ measurements, efficient in the Hilbert space dimension; an arbitrary set of $s$ error rates with $O(\epsilon^{-4}\log s\log(s/\epsilon^2))$; and a channel with $k$-local correlations (a Markov field over a known factor graph) with $O_k(\epsilon^{-2}n^2\log n)$, efficient in $n$. The procedure is a variant of randomized benchmarking over the Pauli group.

### Placement in the tables

* **Task type:** Estimating. The list is that of the $4^n$ Pauli error rates $p$ or eigenvalues $\lambda$ (Walsh–Hadamard transform), explicit as a subset $E$ or implicit via the factor graph. The row "Pauli channel estimation, sequence-based".
* **Object:** Pauli channel, or the Pauli projection of an arbitrary channel via randomized compiling. **Access:** query, rung 3: repeated application in sequences of variable length, interleaved with random Pauli gates; this buys SPAM robustness and relative precision.
* **Status:** 🟢 🟢 🟢 under sparsity ($s = \mathrm{poly}(n)$) or the factor-graph model ($k = O(1)$); the full channel costs $2^n$, efficient only in $d$.
* **Promise:** "nice noise" (gate-independent, stationary, Markovian, close to ideal); for Result 3 a known factor graph with positive marginals.

### The problem

Pauli channels are the standard model of error correction and are enforced physically by randomized compiling; thresholds change by factors of up to four under biased or correlated noise. Nevertheless there were no estimation methods beyond full channel tomography, which moreover gives additive precision and is systematically biased by SPAM errors; at error rates of $10^{-6}$, $10^{12}$ samples would be needed. What is sought: relative precision, SPAM robustness, scaling in $n$ under realistic models.

### Key results

* **Result 1 (Propositions 8, 9).** All $4^n$ error rates with $O(\epsilon^{-2}n2^n)$ measurements, $\Vert\hat p - p\Vert_2\leq O(\epsilon)(1 - p_0)$, with $p_0$ the probability of no error; relative precision is the core, because the error rates are tiny.
* **Result 2 (Theorem 11).** For every set $E$ of $s$ Paulis, $O(\epsilon^{-4}\log s\log(s/\epsilon^2))$ measurements with $\Vert\hat p - p\Vert_\infty\leq O(\epsilon)(1-p_0)$; the $\epsilon^{-4}$ is an artefact of the bias analysis of the subroutine Ratio. Applicable to all errors of small weight; a tree-based search heuristic finds sparse sets whose result can be certified.
* **Result 3 (Proposition 18).** For a Markov field with a degree-$k$ factor graph and positive marginals, a tensor network estimator from $O_k(\epsilon^{-2}n^2\log n)$ measurements with $\Vert\hat p - p\Vert_1\leq O(\epsilon)\Vert\mathbb{1}_I - p\Vert_\infty$, computable in $\mathrm{poly}(n)$.
* **Lemma 2 (stabilizer coverings).** Every set $X$ of Paulis is covered by at most $\min(|X|, \sqrt{|\langle X\rangle/S_X|} + 1)\leq 2^n + 1$ stabilizer groups (MUB construction), tight for groups.
* **Numerics** up to 100 qubits and an implementation on a 14-qubit device (Harper, Flammia, Wallman, *Nat. Phys.* 2020).

### Methodological approach

* **RB over the Pauli group.** Preparation and measurement in a stabilizer basis, sequences of random Pauli gates average the noise; the decay rates of the $2^n$ simultaneously read-out bits are decoupled by a Hadamard transform instead of serial exponential fits of individual parameters; this is the novelty relative to character benchmarking. Harper et al. had shown relative precision of one parameter for Clifford RB; here it is $4^n$.
* **Symplectic structure.** Only commuting Paulis can be measured simultaneously; the error distribution is a "symplectic Markov field" with quasi-latent variables, which differs from classical Markov fields.
* **Hammersley–Clifford** rounds locally estimated marginals to a global distribution in the form of a tensor network.

### Significance and applications

* The first proof of recovery guarantees for channels in relative precision without SPAM bias; the first efficient guarantees for nontrivial channel classes on $n$ qubits; a qualitative change relative to the record at the time (three qubits via compressed sensing).
* Applications: tailoring codes and decoders to the noise, adapting fault tolerance, estimating thresholds and overheads; the "Pauli noise learning transfer" idea of this project's positioning.
* Chen, Zhou, Seif, Jiang later show that precisely these RB-type, ancilla-free protocols need $\Omega(2^{n/3})$ rounds for eigenvalues, while an $n$-qubit ancilla allows $O(n)$.

### Relation to this project

* The row is the query-block representative for channels: sequences buy robustness, not dimension. For this project's pipeline, randomized compiling on both copies is the standard method for turning coherent errors into Pauli noise, and this paper is the reference for what is learnable afterwards.
* The progression from Result 1 ($2^n$) to Result 2 (sparsity) to Result 3 (Markov field) is the channel version of the instance ladder: generic, sparse, factorized. This project's "factorized spectra with a best-first heap" is the state analogue of Result 3.
* Relative precision is a quantity missing from this project's scaling analysis: top-$k$ amplitudes are large, but signal detection at a small signal-to-noise ratio would benefit from relative instead of additive accuracy.

### Limitations and open questions

* $\epsilon^{-4}$ in Result 2 is presumably $\epsilon^{-2}$; the search heuristic has no formal success analysis.
* Only the Pauli projection of the channel; coherent parts are invisible.
* The factor graph must be known; structure learning of the noise is open.
* The noise assumptions (gate-independent, stationary) are mild but not always satisfied.

### Questions for further study

* What is the Heisenberg–Weyl version: randomized compiling with displacement operators on qudits, and what structure does the "symplectic Markov field" of the error rates over $\mathbb{Z}_d^2$ have?
* How much of the robustness comes from the sequence length (query) and how much from the twirl (sample)? Would there be a sample version with Choi states and a Bell measurement?
* Can the tree-based search heuristic for sparse error sets be read as a template for a best-first search in the displacement spectrum?

Paper: [arXiv:1907.12976](https://arxiv.org/abs/1907.12976)

---

## Quantum advantages for Pauli channel estimation (arXiv:2108.08488)

The paper by **Senrui Chen, Sisi Zhou, Alireza Seif, and Liang Jiang** (Chicago, Caltech; *Phys. Rev. A* 105, 032435 (2022)) proves an exponential advantage of entangled measurements for a practically relevant task: learning all $4^n$ eigenvalues of an $n$-qubit Pauli channel to within $\pm\epsilon$. With an $n$-qubit ancilla, $O(n/\epsilon^2)$ applications of the channel suffice; without an ancilla, every protocol, even adaptive and with concatenation, needs $\Omega(2^{n/3})$ measurement rounds. For $k$ ancilla qubits, $\Omega(2^{(n-k)/3})$ holds in general and $\Omega(n2^{n-k})$ without adaptivity and concatenation, the latter tight.

### Placement in the tables

* **Task type:** Estimating. The implicit list of all $4^n$ eigenvalues $\lambda_b$; all of them are returned. The row "Pauli channel eigenvalues, entanglement-assisted"; the channel version of the two-copy separation.
* **Object:** Pauli channel $\Lambda(\cdot) = \sum_ap_aP_a(\cdot)P_a$. **Access:** sample on the Choi state: $n$ Bell pairs, one half through the channel, Bell measurement; the ancilla is the quantum memory. Without an ancilla but with concatenation (RB-type), it is query access, and that provably does not help.
* **Status:** 🟢 🟢 🟢 with $n$ ancilla qubits; 🔴 in the copies without.
* **Promise:** none about the channel; the resource is the entangled ancilla.

### The problem

The known learning advantages (mixedness testing, unitarity testing, Pauli expectation values) are artificial or cannot be implemented robustly against noise. Quantum benchmarking is a genuine task; Pauli channels are universal via randomized compiling; the sample complexity of their estimation had not been characterized despite a long literature, and Flammia–Wallman had left the question of lower bounds for RB-type protocols open.

### Key results

* **Theorem 1 and Algorithm 1.** With $k$ ancilla qubits: $k$ Bell pairs for one subsystem, stabilizer states and syndrome measurements (a stabilizer covering $\mathcal{O}$ of $\mathcal{P}_{n-k}$) for the other; the outcome distribution is the Walsh–Hadamard transform of $\lambda$, so $(-1)^{\langle u,v\rangle + \langle s,e\rangle}$ is an unbiased estimator; $N = O(|\mathcal{O}|n\epsilon^{-2}\log\delta^{-1})$.
* **Corollary 2.** With $2^{n-k}+1$ MUBs as the covering: $O(n2^{n-k}\epsilon^{-2}\log\delta^{-1})$; for $k = n$ therefore $O(n/\epsilon^2)$; experimentally simpler with $3^{n-k}$ Pauli measurements.
* **Theorem 3 (lower bounds)** for accuracy $1/2$: (A) $\Omega(n2^{n-k})$ non-adaptive, non-concatenating, $k$ ancillas, tight; (B) $\Omega(2^{(n-k)/3})$ adaptive, non-concatenating; (C) $\Omega(2^{n/3})$ rounds for adaptive, concatenating, ancilla-free protocols, hence for all RB variants; (D) $\Omega(n)$ for arbitrarily entangled measurements, so Algorithm 1 with $n$ ancillas is optimal, and more than $n$ ancillas do not help.
* **Benchmarking protocol** in the supplement: sequences of random Pauli gates with noisy Bell preparations and measurements, SPAM-robust and exponentially more sample-efficient than any ancilla-free method, provided the ancilla is isolated and long-lived (trapped ions).
* Remark: the error rates $p$ in $\ell_\infty$ can be learned from $O(\log n)$ unentangled samples (Flammia–O'Donnell); the advantage concerns the eigenvalues.

### Methodological approach

* **Construction.** The channels $\Lambda_{(a,s)} = \frac1{2^n}(I\,\mathrm{Tr}(\cdot) + sP_a\mathrm{Tr}(P_a\cdot))$, $a\in[4^n-1]$, $s = \pm1$: an eigenvalue learner identifies $(a,s)$. (A) follows information-theoretically, (B) and (C) by reduction to discrimination against the completely depolarizing channel with the tree method of Huang, Kueng, Preskill; (D) by teleportation stretching (reduction to POVMs on copies of the Choi state) plus Holevo.
* The role of the ancilla: without it there is no measurement setting that samples from $p$ and sees all $\lambda$ at once; with $n$ Bell pairs, every $P_a$ is mapped to a unique outcome (the superdense coding principle).

### Significance and applications

* The first practically relevant, noise-robust learning advantage; the separation ancilla versus concatenation is new: the ancilla brings the exponential gain, the sequence does not.
* The $k$-ancilla tradeoff curve is the first quantitative resource statement between $k = 0$ and $k = n$ and an example of open question (2) of the estimating section.
* Motivates Subramanian, Kwon, Jiang (2026) to generalize to qudit and bosonic channels with $c$-copy access and the conjugate channel.

### Relation to this project

* This is the channel version of this project's measurement: $n$ Bell pairs, the channel on one half, and the Bell measurement correspond to Bell sampling on the Choi state, and the distribution is the Walsh–Hadamard transform of the spectrum. For displacement channels on qudits, the transform is the symplectic Fourier transform over $\mathbb{Z}_d^2$.
* The statement that concatenation (query) does not help but the ancilla (memory) helps exponentially is the precise form of the separation of axes that the appendix of this document postulates: query buys rate, memory buys dimension.
* Results (A) and (B) show that $o(n)$ ancillas bring almost nothing; for this project this means that a "half" second state (for instance an imperfect conjugate on a few qudits) should not be expected to give an exponential gain, provided the analogy holds.

### Limitations and open questions

* Lower bounds for accuracy $1/2$; the $\epsilon$ dependence is proven only for the upper bound.
* Eigenvalues only; open for other properties (error rates in other metrics, structured channels).
* The benchmarking protocol needs an isolated ancilla; on platforms with crosstalk the advantage is questionable.
* An experimental comparison with ancilla-free methods is pending.

### Questions for further study

* What does Algorithm 1 look like for displacement channels on qudits, and is the stabilizer covering of $\mathbb{Z}_d^{2(n-k)}$ with $d^{n-k}+1$ MUBs available for composite $d$?
* Where exactly does the tree method fail when the learner has the conjugate $\Lambda^*$ of the channel, and is that the mechanism behind Subramanian et al. Theorem IV.1?
* Is the statement "more than $n$ ancillas do not help" the channel analogue of "two copies are the sweet spot"?

Paper: [arXiv:2108.08488](https://arxiv.org/abs/2108.08488)

---

## Quantum channel learning with limited parallel access (arXiv:2608.05307)

The paper by **Mahadevan Subramanian, Hyukgun Kwon, and Liang Jiang** (Chicago, Sejong; 2026) carries the learning hierarchies for states (two-copy advantage, $d$-copy advantage for qudits, conjugate advantage) over to channels. The object is the Heisenberg–Weyl transfer matrix $C_{\mathcal{E}}((q_i,p_i),(q_o,p_o)) = \mathrm{Tr}[D(q_o,p_o)\mathcal{E}(D(q_i,p_i))]/d^m$ of a qudit channel, or its bosonic version via two-mode squeezed Choi states. A master lemma gives lower bounds for all $c$-copy protocols with unbounded ancillas and adaptivity, in every dimension. Result: with $\mathcal{E}\otimes\mathcal{E}^*$ the magnitudes can be learned with $O(\log(M/\delta)/\epsilon^4)$ measurements, and this is tight; without $\mathcal{E}^*$ every $c < d$ is exponential in the number of qudits, at $c = d$ it becomes efficient with $\epsilon^{-2d}$, and bosonically it stays exponential for all $c = O(1/\epsilon)$.

### Placement in the tables

* **Task type:** Estimating. Given a bounded set $Q$ of $M$ queries $(q_i,p_i,q_o,p_o)$, the magnitudes $|C_{\mathcal{E}}(Q)|$ are returned. New row "Heisenberg–Weyl transfer matrix, limited parallel access" of the estimating table, directly below Chen, Zhou, Seif, Jiang.
* **Object:** channel on $m$ qudits (prime $d$) or $m$ bosonic modes. **Access:** $c$ parallel copies of $\mathcal{E}$ or of $\mathcal{E}\otimes\mathcal{E}^*$ per measurement round, with arbitrary ancillas, adaptive state preparation, and POVMs (including infinitely fine ones); $\Theta(cT)$ channel queries for $T$ rounds. This is sample access to the Choi state with memory of $c$ copies, i.e. the memory axis for channels.
* **Status:** 🟢 🟢 🟢 with the conjugate channel; 🟢 in copies at $c = d$ with $\epsilon^{-2d}$; 🔴 for $c < d$ and bosonically.
* **Promise:** none about the channel; the resources are $\mathcal{E}^*$ and the parallelism $c$.

### The problem

For states it is known that Pauli expectation values need two copies, Heisenberg–Weyl expectation values on qudits $d$ copies, and $\rho\otimes\rho^*$ gives an exponential advantage, bosonically too. For channels there was the Pauli transfer matrix on qubits and the ancilla separation of Chen, Zhou, Seif, Jiang; for qudits and bosons a general framework was missing. Can the transfer matrix be estimated efficiently with bounded parallel use of the channel, and what does the conjugate channel $\mathcal{E}^*$ (with $\mathcal{E}^*(\rho^T)^T = \mathcal{E}(\rho)$ in a fixed basis) change?

### Key results

* **Lemma III.1 (master lemma).** A lower bound for all $c$-copy protocols for a class of many-versus-one channel discrimination tasks, independent of dimensions, with operator norms of certain sums of channel operators as the only input; it also handles unbounded measurement operators (homodyne) via a Radon–Nikodym construction. A special case (Corollary B.5.2) reduces to state learning (a surrogate channel) and sharpens known bounds there.
* **Theorem IV.1 (with conjugate).** Single-copy access to $\mathcal{E}\otimes\mathcal{E}^*$ with ancilla: $O(\log(M/\delta)\epsilon^{-4})$ measurements, non-adaptive, via a generalized Bell measurement on $(\mathcal{E}\otimes I)(\sigma)\otimes(\mathcal{E}^*\otimes I)(\sigma^T)$ with Bell pairs or TMSV states as $\sigma$; Theorems IV.6/IV.7: $T = \Omega(c^{-4}\epsilon^{-4})$ for $c$-copy access to $\mathcal{E}\otimes\mathcal{E}^*$, so $\epsilon^{-4}$ is tight.
* **Theorem IV.2 (without conjugate, qudits).** For $c\leq\min(d,d')-1$: $T = \Omega(d^md'^{m'}c^{-2}\epsilon^{-2})$; for $c\geq d$ (with $d = d'$), up to constants, $T = \Omega(\min\{d^{m+m'}/(c\epsilon)^2, (d/(c\epsilon))^{2d}\})$: a sharp transition at $c = d$, and $\epsilon^{-2d}$ is tight against the $d$-copy algorithm with $O(d(m+m')\log(d/\delta)\epsilon^{-2d})$.
* **Theorem IV.3 (without conjugate, bosons).** $T = \Omega(d_{\mathrm{in}}^md_{\mathrm{out}}^{m'}c^{-2}\epsilon^{-2})$ for all $c = O(1/\epsilon)$ with effective mode dimensions $d_{\mathrm{in}} = \sqrt{1 + (0.99\kappa\tanh 2r)^2}$, $d_{\mathrm{out}} = \sqrt{1 + (0.99\kappa')^2}$ under energy bounds $\kappa$; no transition, because the effective dimension grows with the accuracy.
* **Theorems IV.4, IV.5 (self-conjugate, one copy).** Even for $\mathcal{E} = \mathcal{E}^*$, single-copy access stays at $\Omega(d^md'^{m'}\epsilon^{-2})$; from $c = 2$ on, Theorem IV.1 applies.
* **Section V (hierarchy).** For square-free $d$, exactly $d$ copies are needed; for general $z$, the product of the prime divisors; a family of bosonic channels stays hard for every $c = O(1/\epsilon)$; sequential access is strictly stronger and remains open.

### Methodological approach

* The channel discrimination families $\mathcal{E}_{(q_1,p_1),(q_2,p_2)}$ with Kraus-type operators $\frac1{\sqrt2}(e^{i\pi/4}D + e^{-i\pi/4}D^\dagger)$ against the maximally mixed target; the operator norm of $\sum_{q,p}D(q,p)^{\otimes 2k}$ is $d^m$ for $k\neq0\bmod d$ and $d^{2m}$ for $k = 0\bmod d$ (Lemma B.8), and exactly this produces the transition at $c = d$: only when $c$ copies of the displacement operators commute does the statistic become informative.
* With the conjugate, the $D\otimes D^*$ commute for all addresses, and the terms $k = l\bmod d$ dominate; this gives $\epsilon^{-4}$ without a dimension factor.
* For bosons: TMSV Choi states with finite squeezing $r$, so that the transfer function stays bounded; the naive transfer function $\mathrm{Tr}[D(\beta)\mathcal{E}(D^\dagger(\alpha))]$ is unbounded and not learnable (Appendix C 1 b).

### Significance and applications

* Unifies the state-learning hierarchies in a channel framework that covers qubits, qudits, and bosons, and names the conjugate channel as a resource with a tight $\epsilon^{-4}$.
* The conjugate channel is available if all Kraus operators are real in some basis (a real Stinespring dilation with a self-conjugate environment); a superchannel that turns $\mathcal{E}^{\otimes k}$ into $\mathcal{E}^*$ does not exist.
* Shows that the relation between TMSV Choi states in trace distance and the energy-constrained diamond norm can have exponential prefactors (Appendix C 2): a contribution to the question of the right metric for bosonic channels.

### Relation to this project

* This is the channel version of Objective 3, with exactly the project's object, $D(q,p)$ on qudits, and the conjugate as a resource. The results translate directly: Bell sampling on $\rho\otimes\rho^*$ is the surrogate-channel special case, and Corollary B.5.2 sharpens the lower bounds for $c$-copy state learning from the bosonic conjugate paper exponentially (Theorem B.22).
* The transition at $c = d$ is the precise form of the statement "Bell sampling on identical copies fails for qudits" from the searching table: not two but $d$ copies make $D^{\otimes c}$ commute, and $\epsilon^{-2d}$ is the price. For composite $d$ the product of the prime divisors counts; for the project's cyclic single-qudit basis this is the relevant number.
* $\epsilon^{-4}$ is tight for $\mathcal{E}\otimes\mathcal{E}^*$ with arbitrarily many parallel copies: the $\epsilon^{-4}$ of magnitude estimation in Phase 1 is therefore not a weakness of the protocol but a property of the resource, at least for magnitudes.
* The master lemma is a tool for formulating this project's own lower bounds for top-$k$ localization with $\rho\otimes\rho^*$; it needs only operator norms of sums over the candidate addresses.

### Limitations and open questions

* Magnitudes only; the phase of $C_{\mathcal{E}}$ cannot be estimated bosonically without knowledge of the queries, and for qudits only via hypothesis states as in King, Wan, McClean.
* Parallel access; sequential protocols with bounded ancilla are open and presumably stronger.
* The constants ($0.75$, $0.99$, $0.11$) are proof artefacts; the bounds hold for "large" $m$.
* The bosonic task depends on the squeezing strength $r$ and the energy bounds; the metric question is open.

### Questions for further study

* What does the transition at $c = d$ look like concretely for the cyclic single-qudit basis with composite $d$, and how many copies does this project's protocol need without the conjugate for $d = 64$?
* Can the master lemma be applied to the task "find the $k$ largest $|y_{q,p}|$" to obtain a sample lower bound for Phase 1 with and without $\rho^*$?
* What is the real Stinespring condition for states instead of channels: which preparations deliver $\rho^*$ physically, and does this coincide with Appendix D of King, Wan, McClean?

Paper: [arXiv:2608.05307](https://arxiv.org/abs/2608.05307)


<br>

# Appendix

## Separation: QML with Classical and Quantum Data

The data source decides, not the hardware. Quantum Learning is the bottom row of the following data-vs-learner matrix. **Why the separation matters (Power of Data).** In the top row, advantage claims are fragile: classical ML with enough training data catches up with quantum models on classical tasks (Huang et al., Nat. Commun. 2021). In the bottom row stand the *proven* exponential separations, including hardware demonstration.

| | Classical Learners | Quantum Enhanced Learners |
| --- | --- | --- |
| **Classical data** | classical ML | "QML on classical data": feature maps, variational classifiers, quantum kernels |
| **Quantum data** <br>(copies of $\rho$ / channels) | **Measurement protocol + classical statistics: shadows, Bell sampling + classical decoders** | Quantum-memory protocols: coherent two-/multi-copy measurements |

Three litmus tests separate the rows sharply:

1. **Where does the unknown live?** Density operator/channel vs. classical dataset.
2. **Is "number of copies" a meaningful cost?** Quantum data cannot be cloned, every copy costs. Classical data can be copied at will.
3. **Do the information bounds bind?** No-cloning, Holevo, and gentle measurement are what make learning from quantum data nontrivial. They do not apply to a CSV file. 

The three bounds are: **No-cloning:** no CPTP map sends $\rho \mapsto \rho\otimes\rho$ for all $\rho$ (linearity forbids it). > The first bound makes copies a budget. **Holevo:** $n$ qubits carry at most $n$ bits of accessible classical information, $I(X{:}Y) \leq S(\bar\rho) - \sum_x p_x S(\rho_x) \leq n$. > the second bound caps what one shot can reveal. **Gentle measurement** (Winter 1999; Aaronson 2004): if a two-outcome measurement accepts $\rho$ with probability $\geq 1-\epsilon$, the post-measurement state is within trace distance $O(\sqrt{\epsilon})$ of $\rho$. > the third bound is the loophole that lets many near-deterministic questions share the same copies (shadow tomography).


## Measurement theory vs. Learning Theory

Measurement theory answers the single-shot question: What does a measurement do to a state, and which statistics does it produce? Learning theory asks the inverse, statistical question: *What can be learned about an unknown $\rho$ from many measurements, and at what cost?* The Born rule turns the state into a sampling oracle; learning is the inverse problem.

**Definition.** Given access to copies of an unknown quantum object (state $\rho$, channel $\mathcal{E}$, Hamiltonian $H$), produced by nature, a sensor, or a quantum device: *Which* properties can a learner extract, at *what* cost in copies, classical time, and memory, and how do quantum resources (quantum memory, entangled measurements, adaptivity) change these costs?


## What is learned: states and processes

**The object axis.** A learner can be asked about a state, a Hamiltonian, a unitary, a channel, or a classical function. This is a fourth axis next to task, access, and budgets, and it runs across the three task types rather than forming a block of its own: states appear in all three tables, and so do processes. Hamiltonians have rows in estimating for their coefficients and in searching for their structure; circuits have rows in identifying. The tables therefore carry the object as a column instead of a separate section.

**Access for processes.** Sample versus query is defined for states on the access ladder. For processes the classical distinction between random examples and membership queries supplies the definition.
* A process applied to fixed or random inputs that do not depend on earlier outcomes yields copies of a single state: the Choi state, obtained by applying the process to half of a Bell pair, or the input–output data state. That is **sample access**.
* Inputs chosen adaptively or queried in superposition, and uses of the process in controlled or inverted form, in sequences, or interleaved with control pulses, are **query access**. Heisenberg-limited learning of dynamics needs such control (Dutkiewicz, O'Brien, Schuster 2024) and is therefore query access.
* Every row sits at the **weakest access its algorithm needs**. A nonadaptive protocol on random product inputs is a sample protocol, even if the learner prepares the inputs.

**Object and access are independent.** Learning a Hamiltonian from copies of its Gibbs state learns a process from samples of a state. Learning a state through its preparation circuit learns a state by queries. Learning a channel from its Choi state learns a process from samples, with the ancilla as quantum memory.

**Where the object decides hardness: normalization.** The squared Pauli coefficients of a unitary sum to one, so Bell sampling on its Choi state returns every coefficient of size $\tau$ with probability $\tau^2$, and the heavy terms fall out directly. The squared displacement coefficients of a pure state sum to $d$, so a coefficient of size one appears with probability $1/d$. The same measurement makes searching easy for unitaries and runs into the LWE wall for states. Details in the structure-learning protocols.

## Measurement primitives as basis for Protocols for Quantum Learning

Everything protocol below is a *protocol over measurements*, not a new measurement type. The section mirrors the three tables. First the four measurement primitives from which every protocol is built, then the protocols by task type, then what cuts across all three tables: the proof technology behind the bounds, the hardness results, the learned decoders, and the surveys.

**Measurement primitives**

Four primitives, one per rung of the access ladder and one for the far end of the memory axis. Every row in the tables uses one of them.

**Single-copy randomized measurements.** Draw a random basis per copy, from single-qubit Paulis or from $n$-qubit Cliffords, measure, and store the outcome. The engine of classical shadows and of direct fidelity estimation, where Pauli expectations are importance-sampled by their weight in the target state (Flammia, Liu 2011; da Silva, Landon-Cardinal, Poulin 2011). Adaptivity is allowed, each copy is still an i.i.d. draw, and the shadow norm of the ensemble decides the cost. This is rung 1 of the access ladder and the workhorse of every hardware experiment.

**Bell sampling on two copies.** A transversal Bell measurement across two copies, $\rho\otimes\rho$ or $\rho\otimes\rho^*$, draws one Pauli or displacement operator per shot. Bell difference sampling, the XOR of two such draws from four copies, removes the unknown coset offset and is the primitive behind stabilizer learning, stabilizer testing, and agnostic tomography. Conjugate pairs turn the draw into the clean squared spectrum for every dimension $d$; on qudits with two identical copies the draw can be uniform and carry nothing. Rung 2 of the access ladder, and the primitive of this project. Details in the next subsection. Applied to the Choi state of a unitary or channel, the same measurement samples its Pauli spectrum; for processes this is the sample-access primitive.

**Collective Schur sampling.** Measure all $N$ copies at once in the Schur–Weyl basis, which projects onto irreducible representations of the symmetric and unitary groups. Spectrum estimation (Keyl, Werner 2001), spectrum testing (O'Donnell, Wright 2015), and sample-optimal tomography (Haah et al. 2017; O'Donnell, Wright 2016) live here. Quantum memory $k = N$, the far end of the memory axis, and the reason those optimal rates are not hardware rates.

**Oracle calls.** Uses of a preparation circuit $U$, its inverse and controlled versions, of the dynamics $e^{-iHt}$ interleaved with control, or of a channel in sequences or on inputs chosen adaptively or in superposition. Amplitude estimation, superposition queries, Heisenberg-limited Hamiltonian learning, and sequence-based noise learning count this budget. A process applied once to a fixed or random input is not an oracle call in this sense: it yields copies of the Choi state or of an input–output data state and belongs to the sample primitives. Rung 3 of the access ladder, where the precision rate improves to $1/\epsilon$ and where the search problems of the searching table become polynomial.

## Bell sampling on two copies: the primitive behind conjugate pairs and structure learning

**Mechanism.** The $2n$-qubit Bell basis $\{(P\otimes\mathbb{1})|\Phi^+\rangle^{\otimes n}\}$ is the joint eigenbasis of all commuting $P\otimes\bar P$. A transversal Bell measurement across two copies draws one Pauli string per shot

$$P \sim \frac{|\langle\bar\psi|P|\psi\rangle|^2}{2^n}$$

A single shot carries information about the *entire* Pauli spectrum. **Subtlety:** On $\psi\otimes\psi$ one samples against the *conjugate* state $\bar\psi$. The clean spectrum $\mathrm{Tr}(P\rho)^2/2^n$ requires the pair $(\rho, \bar\rho)$. For real amplitudes both coincide (which is why demos like GHZ states).

**Consequences.** Purity and overlap $\mathrm{Tr}(\rho\sigma)$ via SWAP tests without tomography. Stabilizer states learnable from $O(n)$ Bell samples. Above all: **Pauli shadow tomography with $\Theta(n)$ copies given two-copy memory vs. $2^{\Omega(n)}$ without.** One of the strongest proven exponential quantum advantages, demonstrated in hardware. Two is the sweet spot: Almost all known gain arrives already at $k=2$.

Literature:
* **Bubeck, Chen, Li (FOCS 2020):** Entanglement necessary for optimal property testing.
* **Chen, Cotler, Huang, Li (FOCS 2021):** $\Theta(n)$ vs. $2^{\Omega(n)}$ separation with quantum memory.
* **Aharonov, Cotler, Qi (Nat. Commun. 2022):** QUALM, the formal model of an experiment as a quantum algorithm with coherent or incoherent access to a lab oracle; exponential separation of the two for physically motivated distinction tasks, with a SWAP test on two oracle outputs as the coherent protocol.
* **Huang et al. (Science 2022):** Flagship separations and Sycamore demo with 40 qubits.
* **King, Wan, McClean (2024):** Exponential advantage via $(\rho, \rho^*)$ with constant memory.
* **Chen, Gong, Zhang (2024):** Separations for adaptive multi-copy shadow tomography.
* **Allcock, Doriguello, Ivanyos, Santha (2024):** Bell sampling fails on qudits, $d > 2$: Bell difference sampling on four copies of a stabilizer state returns only $\mathrm{col}(V)\times\mathrm{col}(W)$, uniform when both have full rank. With the conjugate, Bell sampling on $\vert S\rangle\vert S^*\rangle$ learns the state from $O(n)$ copies for every $d$; without it, a hidden-quadratic-phase algorithm does for $d$ prime. The reason this project uses conjugate pairs rather than two identical copies.

**Two more separations of the same shape.** *Purity testing* (is $\rho$ pure or maximally mixed?) needs $O(1)$ copies with two-copy memory (a SWAP test) but $\Omega(2^{n/2})$ without (Chen, Cotler, Huang, Li, FOCS 2021); the memory-free lower bound also kills any single-copy route to $\mathrm{Tr}(\rho^2)$. *Pauli channel estimation*: learning all $4^n$ Pauli eigenvalues of a channel to $\pm\epsilon$ takes roughly $O(n/\epsilon^2)$ uses with ancilla-assisted entangled inputs versus $2^{\Omega(n)}$ without (Chen, Zhou, Seif, Jiang, PRA 2022), the channel version of the shadow-tomography separation. The general framework in which all of these live is **QUALM** (Aharonov, Cotler, Qi, Nat. Commun. 2022): an experiment is a quantum algorithm that calls an unknown *lab oracle*, with *coherent* access (outputs of several calls held and measured jointly) or *incoherent* access (each output measured completely before the next call, adaptivity allowed). The separations above are statements about this coherence, which is the memory axis of this document, not about the model class; which oracle nature supplies, copies of $\rho$, pairs $\rho\otimes\rho^*$, or the preparation circuit, is the separate access ladder. On qubits the SWAP test behind these separations is a coarse-grained Bell measurement: SWAP is diagonal in the Bell basis, with eigenvalue $(-1)^{\#Y}$ on the outcome $P$. On qudits with $d>2$ it is not; see the QUALM summary under Identifying (Papers).


<br>

## Where the bounds come from: proof technology

The thesis stated under Efficiency Boundaries, a dense sample map and a nearly empty time map, has a concrete cause: the two kinds of bounds are proved with different tools, and only one kind is unconditional.

**Sample lower bounds, unconditional.**
* *Holevo and packing.* $n$ qubits carry at most $n$ bits; a hypothesis class with $2^{\Theta(N)}$ well-separated members needs $\Omega(N)$ copies. This gives $\Omega(n)$ for stabilizer states, $\Omega(d^2/\epsilon^2)$ for full tomography, and $\Omega(d_{\mathrm{VC}}/\epsilon)$ for PAC learning from quantum examples (Arunachalam, de Wolf 2018).
* *The tree method for bounded memory.* A learner without quantum memory induces a tree of single-copy outcomes; bounding the likelihood ratio between a random hypothesis and the maximally mixed state along every root-to-leaf path gives $2^{\Omega(n)}$ for Pauli shadow tomography, purity testing, and channel learning without memory (Bubeck, Chen, Li 2020; Chen, Cotler, Huang, Li 2021; Chen, Zhou, Seif, Jiang 2022) and $\Omega(d^3/\epsilon^2)$ for single-copy tomography, adaptive or not (Lowe, Nayak 2022; Chen, Huang, Li, Liu, Sellke 2023). The method interpolates in the number $k$ of memory qubits.
* *Reduction plus Weingarten calculus for Haar-random oracles.* Every incoherent protocol, adaptive or not, is a probabilistic mixture of simple prepare–apply–measure protocols, because the classical messages from the workspace can be generated by a classical computer with random bits. For those, the outcome distributions under a fixed and under a fresh Haar-random unitary are compared term by term in the Weingarten expansion, summing over outcomes backwards from the last call. This gives $\Omega(2^{2\ell/7})$ for the fixed-unitary and symmetry-class problems (Aharonov, Cotler, Qi 2022), the process-side counterpart of the tree method.
* *Group theory.* Schur–Weyl duality for the unitary group gives the optimal tomography rates; Schur–Weyl duality for the Clifford group (Gross, Nezami, Walter 2021) explains why four copies expose a stabilizer group and why the characteristic distribution of a pure state is its own symplectic Fourier transform.

**Sample upper bounds.**
* *Hoeffding plus a union bound* over a candidate list: character means over a dictionary, all $d^2$ squared magnitudes from one Bell record, Hamiltonian coefficients from local marginals.
* *Median of means and the shadow norm* for classical shadows; *gentle measurement* for shadow tomography (Winter 1999; Aaronson 2004, 2018), which is the same lemma as differential privacy (Aaronson, Rothblum 2019); *threshold search* for hypothesis selection (Bădescu, O'Donnell 2021); *matrix multiplicative weights* as the hypothesis update behind shadow and online learning.
* *Fourier sampling and coset differencing*: Bell sampling, Bell difference sampling, and quantum examples deliver random elements of a subspace or coset, and Gaussian elimination finishes (Montanaro 2017; Bshouty, Jackson 1998; Simon 1994).

**Time lower bounds, conditional.** Every known one is a reduction from a cryptographic assumption. LWE gives the displacement instance of this project; LPN gives the hardness of learning output distributions with a single $T$ gate (Hinsche et al. 2023) and the classical mirror of Bell sampling; one-way functions give pseudorandom states (Ji, Liu, Song 2018; Brakerski, Shmueli 2019) and from them the hardness of learning states of bounded gate complexity (Zhao et al. 2023) and of distinguishing entanglement (Aaronson et al. 2022). No unconditional time lower bound for a natural quantum learning task is known, which is why the time map is empty where the sample map is dense.

**Time upper bounds.** Each one names the structure it uses: linear algebra over $\mathbb{F}_2$ or $\mathbb{Z}_d$ for subgroups, enumeration for dictionaries, a best-first heap for factorized spectra, the noncommutative Bohnenblust–Hille inequality for low-degree objects (Volberg, Zhang 2023), light cones for shallow circuits, cluster expansions at high temperature and a different route at any constant temperature for Gibbs-state Hamiltonian learning (Haah, Kothari, Tang 2022; Bakshi, Liu, Moitra, Tang 2024), and graph colorings of commutation structure for triply efficient shadow tomography (King, Gosset, Kothari, Babbush 2024). The learned decoder of this project is an attempt to obtain such a bound empirically where no structure has been named.

## Computational lens: hardness and pseudorandomness

Pseudorandom states (PRS) show: States can be statistically learnable yet computationally indistinguishable from Haar-random ones.

* **Regev (2005):** Learning With Errors, foundation of average-case hardness.
* **Ji, Liu, Song (CRYPTO 2018):** Pseudorandom quantum states.
* **Kretschmer (TQC 2021):** Quantum pseudorandomness and classical learning hardness.
* **Huang, Broughton et al. (Nat. Commun. 2021):** *Power of data*: classical data closes quantum advantages in learning classical functions.
* **Brakerski, Shmueli (TCC 2019):** Scalable pseudorandom states from one-way functions.
* **Aaronson, Bouland, Fefferman, Ghosh, Vazirani, Zhang, Zhou (ITCS 2024):** Pseudoentanglement: low and high entanglement, computationally indistinguishable.
* **Gu, Leone, Ghosh, Eisert, Yelin, Quek (2023):** Pseudomagic: stabilizer entropy $\omega(\log n)$ versus $\Theta(n)$, computationally indistinguishable; magic is hideable like entanglement, the two are tunable independently, and black-box magic distillation is limited to $O(\log^{1+c} n)$ $T$ states. For the searching column a second hard endpoint from one-way functions.
* **Zhao, Lewis, Kannan, Quek, Huang, Caro (PRX Quantum 2024):** States and unitaries of bounded gate complexity: $\tilde\Theta(G)$ copies suffice, but learning is computationally hard under cryptographic assumptions.
* **Hinsche et al. (2022; PRL 2023, "One $T$ gate makes distribution learning hard") / Nietner et al. (2023):** Output distributions of circuits: learnable for Clifford, hard under LPN with a single non-Clifford gate, also on average.

**The average-case counterpart.** Huang, Kueng, Preskill, "Information-theoretic bounds on quantum advantage in machine learning" (PRL 2021): for predicting $\mathrm{Tr}(O\,\mathcal{E}(\rho_x))$ on inputs drawn from a distribution, a classical learner with measurement data needs only polynomially more samples than a fully quantum one in the *average-case* prediction error, while for *worst-case* prediction the gap can be exponential. Read together with PRS: computational indistinguishability and average-case learnability are different axes, and most "quantum advantage in learning" claims live on the worst-case one.

## Machine-learned decoders

Classical neural decoders on shadow data (bottom-left quadrant) as empirical heuristics for classically hard decoding tasks.

* **Torlai et al. (Nat. Phys. 2018):** Neural-network QST.
* **Huang, Kueng, Torlai, Albert, Preskill (Science 2022):** Provable generalization bounds for ML on shadow data.
* **Huang, Preskill, Soleimanifar (2024):** State certification via single-qubit shadow relaxations.
* **Carrasquilla, Torlai, Melko, Aolita (Nat. Mach. Intell. 2019):** Generative models as state representations fit to measurement data.
* **Lewis et al. (Nat. Commun. 2024) / Onorati, Rouzé, França, Watson (2023):** Provable prediction of ground and thermal state properties within a phase, down to $O(\log n)$ training states.
* **Bausch et al. (Nature 2024):** AlphaQubit, the learned surface-code decoder.

**Representation side and the decoding target.** The representational cousin of a learned decoder is the **neural quantum state** (Carleo, Troyer, Science 2017): a network as the ansatz $\psi_\theta(s)$, trained variationally rather than from measurement data. The two meet in Torlai et al. (2018), where the network is fit to measurement statistics. On the transfer to error correction promised in the positioning section: Google's **AlphaQubit** (Bausch et al., Nature 2024) is a transformer decoder trained on syndrome data that outperforms tensor-network and matching decoders on Sycamore surface-code experiments, the existence proof that a learned decoder can beat hand-built combinatorics on real hardware data.

## Surveys and timeline

* **Anshu, Arunachalam (Nat. Rev. Phys. 2024):** Canonical survey on state-learning complexity.
* **Gebhart et al. (Nat. Rev. Phys. 2023):** Review on learning quantum dynamics in experiments.
* **Elben et al. (Nat. Rev. Phys. 2023):** The randomized measurement toolbox, shadows in practice.
* **Kliesch, Roth (PRX Quantum 2021):** Theory of quantum system certification, a tutorial.
* **Montanaro, de Wolf (2016):** Survey of quantum property testing.
* **Arunachalam, de Wolf (SIGACT 2017):** Quantum PAC learning.

| Period | Milestones |
| --- | --- |
| 1973–1997 | Holevo bound (1973) · Bernstein–Vazirani (1993) and Simon (1994): Fourier sampling and hidden subgroups, the query-side primitives · DNF from quantum examples (Bshouty–Jackson 1995) |
| 1998–2004 | Gentle measurement (Winter 1999; Aaronson 2004) · Spectrum estimation by Schur sampling (Keyl–Werner 2001) · Quantum Goldreich–Levin (Adcock–Cleve 2002) · Stabilizer identification (Aaronson–Gottesman 2004) · Quantum vs. classical learnability (Servedio–Gortler 2004) |
| 2005–2010 | LWE (Regev 2005) · State PAC learnability (Aaronson 2007) · Clifford learning (Low 2009) · Compressed-sensing and MPS tomography (2010) · Quantum Boolean functions and operator Goldreich–Levin (Montanaro–Osborne 2010) |
| 2011–2014 | Direct fidelity estimation by Pauli importance sampling (Flammia–Liu; da Silva, Landon-Cardinal, Poulin 2011) · Sparse FFT (Hassanieh, Indyk, Katabi, Price 2012) |
| 2015–2017 | Spectrum testing (O'Donnell–Wright 2015) · Sample-optimal tomography $\Theta(d^2/\epsilon^2)$ (2016) · Property-testing survey (Montanaro–de Wolf 2016) · Stabilizer Bell sampling (Montanaro 2017) · Quantum PAC survey (Arunachalam–de Wolf 2017) · Ising structure learning in $\tilde O(p^2)$ without correlation decay (Bresler 2015) · Sparsitron, near-optimal MRF structure learning by multiplicative weights (Klivans–Meka 2017) |
| 2018–2019 | Shadow tomography (Aaronson) · Online learning of states · Pseudorandom states (Ji–Liu–Song) · Neural-network tomography (Torlai et al.) · Stabilizer PAC learning (Rocchetto) · Gentle measurement and differential privacy (Aaronson–Rothblum) · LWE easy with quantum samples (Grilo–Kerenidis–Zijlstra) · Scalable PRS (Brakerski–Shmueli) · $k$-Fourier-sparse functions from $O(k^{1.5}\log^2 k)$ quantum examples (Arunachalam–Chakraborty–Lee–Paraashar–de Wolf) |
| 2020 | Classical shadows (Huang–Kueng–Preskill) · Entanglement necessary for property testing (Bubeck–Chen–Li) · Pauli channel estimation (Flammia–Wallman; Harper–Flammia–Wallman) · Quantum statistical queries (Arunachalam–Grilo–Yuen) · Sparse Pauli noise by peeling on chosen stabilizer groups (Harper–Yu–Flammia) |
| 2021 | Memory separations (Chen–Cotler–Huang–Li) · Clifford Schur–Weyl duality and stabilizer testing (Gross–Nezami–Walter) · Improved shadow tomography and threshold search (Bădescu–O'Donnell) · Gibbs-state Hamiltonian learning (Anshu et al.) · Power of data and information-theoretic bounds (Huang et al.) · Pseudorandomness and learning hardness (Kretschmer) · Derandomized and fermionic shadows · Experimental classical shadows on four photonic qubits (Zhang et al.) · Certification tutorial (Kliesch–Roth) |
| 2022 | Learning from experiments, Sycamore demo (Huang et al., Science) · Provable ML on shadow data (Huang et al., Science) · Pauli-channel separation (Chen–Zhou–Seif–Jiang) · QUALM (Aharonov–Cotler–Qi) · High-temperature Hamiltonian learning in polynomial time (Haah–Kothari–Tang) · Few-T learning (Lai–Cheng) · Pseudoentanglement · Output-distribution learnability (Hinsche et al.) · Nonadaptive single-copy lower bound (Lowe–Nayak) · Tight certification bounds with incoherent measurements (Chen–Huang–Li–Liu) · Non-Markovian process tensor tomography (White et al.) · Noisy stabilizer PAC learning as hard as LPN (Gollakota–Liang) |
| 2023 | Heisenberg-limited Hamiltonian learning (Huang–Tong–Fang–Su) · Adaptivity does not help tomography (Chen et al.) · Unitary estimation at the Heisenberg rate (Haah–Kothari–O'Donnell–Tang) · Phase states (Arunachalam–Bravyi–Dutt–Yoder) · Juntas (Chen–Nadimpalli–Yuen) · Predicting processes (Huang–Chen–Preskill) · Bounded gate complexity (Zhao et al.) · One $T$ gate makes distribution learning hard (Hinsche et al.) · Few non-Clifford gates (Grewal–Iyer–Kretschmer–Liang) · Free-fermion tomography (Aaronson–Grewal) · Noncommutative Bohnenblust–Hille (Volberg–Zhang) · Qudit low-degree learning via a dimension-free Remez inequality (Klein–Slote–Volberg–Zhang) · Matchgate shadows (Wan–Huggins–Lee–Babbush) · Locally scrambled shadows (Hu–Choi–You) · Randomized-measurement review (Elben et al.) · Stabilizer-entropy phase transition and purity estimation (Leone et al.) · Learning finitely correlated states (Fanizza et al.) · Average-case hardness of learning circuit output distributions (Nietner et al.) · Linear T-count for pseudorandomness and approximate stabilizer support from Bell difference sampling (Grewal–Iyer–Kretschmer–Liang) · Pseudomagic (Gu–Leone–Ghosh–Eisert–Yelin–Quek) · Pauli spectrum of QAC⁰, the quantum LMN (Nadimpalli–Parham–Vasconcelos–Yuen) |
| 2024 | Triply efficient shadows (King–Gosset–Kothari–Babbush) · Conjugate pairs (King–Wan–McClean) · Adaptivity separations for shadow tomography (Chen–Gong–Zhang) · Agnostic tomography and stabilizer bootstrapping · Tolerant stabilizer testing (Arunachalam–Dutt) · Any-temperature Hamiltonian learning (Bakshi–Liu–Moitra–Tang) · Hamiltonian structure learning from real-time evolution (Bakshi–Liu–Moitra–Tang) · Shallow circuits in polynomial time (Huang et al.; Landau–Liu) · Qudit stabilizer learning beyond Bell sampling (Allcock et al.) · Low-degree objects · Certification with single-qubit measurements (Huang–Preskill–Soleimanifar) · Gaussian and CV state learning (Mele et al.) · AlphaQubit · Bell and locally entangled shadows (Ippoliti) · Matchgate ensemble unification (Heyraud–Chomet–Tilly) · Qudit shadows with a magic gate (Mao–Yi–Zhu) · Tighter median-of-means constants (Fu et al.) · State-learning survey (Anshu–Arunachalam) · Tolerant stabilizer testing with a polynomial gap (Bao–van Dordrecht–Helsen) · Fermionic states with few non-Gaussian gates (Mele–Herasymenko) |
| 2025–2026 | First empirical evaluation of a two-copy triply efficient scheme (arXiv:2508.11744) · Noise-robust two-copy hardware · Physical average-case decodability · Learned decoders as algorithm discovery · Online shadow tomography at the classical rates (Chen–O'Donnell–Pelecanos–Wright) · Heisenberg-limited Hamiltonian learning without short-time control (Shin–Lee–Oh) · Shadows over symmetric spaces (Chang et al.) · Channel learning with limited parallel access and the conjugate channel (Subramanian–Kwon–Jiang) |

<br>

## Open Frontiers (Research Questions)

* **Mapping the decodable classes.** Between "subgroup-easy" (linear algebra) and "LWE-hard" lies uncharted territory. The same state moves from the easy to the hard regime by turning up a noise parameter. Open: Does the hardness reduction transfer from the tensor-product basis to the cyclic single-qudit basis?
* **What learned decoders implicitly find.** If a decoder works on a class with no known efficient algorithm, it may have found one. ML as a tool for algorithm discovery; what is missing is a metric that predicts generalization across state distributions.
* **Hardware realism with two copies.** Approximate matched filters (probe gain $\kappa < 1$, overhead $\kappa^{-2}$) make protocols graceful against preparation, crosstalk, and measurement errors. The practically most relevant axis.
* **Average case instead of worst case.** The hardness results are adversarial. Natural states (ground states of local Hamiltonians, thermal states) could be generically decodable: from the cryptography perspective to the physics perspective.
* **Memory between zero and two.** The separations are stated at $k=0$ versus $k=2$ copies. Chen–Cotler–Huang–Li also treat a learner with $k$ qubits of quantum memory and find that the sample complexity interpolates smoothly; what is missing is the *protocol* side: which structured tasks become tractable at a fixed small memory budget short of a full second copy, e.g. with a few ancilla qubits per shot as in the Pauli-channel case.

<br>

## Reading the tables

The three tables are the primary object. This appendix keeps the three axes that generate them, for readers who want the coordinate system: the quadrant of access against task, the access ladder, and the measurement-power axis.



**The pattern in the status column.** Every 🟢 🟢 🟢 row under sampling access names a promise (locality, subgroup, class structure, Gaussianity, bond dimension, light cone, low degree, a gapped phase) or a resource (two-copy memory, an entangled ancilla); every 🟢 🟢 🟢 row under query access names the access itself, sometimes together with a promise. The 🟢 🔴 rows are the generic cases. Time efficiency is never free; it is bought by a promise about the state, by a resource on the quantum side, or by a stronger access model.

Glyph order in the status column: copies · time · memory.

**Two ways to fail, which the memory column separates.**
* *Hypothesis too large.* MMW-based shadow tomography keeps a $2^n \times 2^n$ matrix. Memory is exponential, and therefore time is too: an algorithm cannot touch more memory than it has steps. This is a representation problem, and sparse surrogates solve it.
* *Search too hard.* Sparse displacement spectra need $O(k \log d)$ bits for the list. Memory is polynomial, time is LWE-hard regardless. This is a decoder problem, and no representation solves it.
* The implication runs one way only: exponential memory forces exponential time, exponential time does not force exponential memory. The project's row is the only one in the table where memory holds and time still fails. The boundary this document is about is the decoder, not the representation.
* The own pipeline crossed the memory boundary three times: the $d \times d$ histogram became a coprime fold into a fixed $64 \times 64$ tensor, the $d^2$-wide output layer became a bit vector of $2\lceil\log_2 d\rceil$ neurons, and the $d \times d$ MMW hypothesis became a sparse surrogate of $O(k)$ weights. Each replacement was necessary; none of them touched the time hardness of localization.

**What the merged tables show.**
* The object column shows that dynamics are not a separate category. States, Hamiltonians, unitaries, channels, and classical functions appear in all three tables; only the access differs, and it follows the rule of "What is learned": fixed or random inputs are sample access through the Choi or data state, adaptive or controlled use is query access. The object decides hardness only through the normalization of its spectrum, which is why heavy Pauli terms of a unitary are found from samples and heavy displacement terms of a state are not.
* The computational boundary, as far as it is charted, is the set of 🟢 🔴 rows: sparse displacement spectra and LWE from samples (searching); general shadow tomography, PAC learning of states, and online learning (estimating, hypothesis too large); pseudorandom states, bounded gate complexity, and output distributions of circuits (identifying, cryptographic). Every one of them is sample-efficient. The three that fail in time with polynomial memory, the LWE pair, bounded gate complexity, and the output-distribution family, are the ones where the hardness is a theorem about the decoder rather than about the size of the hypothesis.
* Every cell of the quadrant in the appendix is present with several examples, and the query rows carry no hardness for any task type. That is why the quadrant collapses to a single hard corner. Tasks that stay hard under queries, such as full tomography, are kept out of the quadrant on purpose.
* The generic hard case has its own row: LWE from i.i.d. samples, directly under the project's row in the searching table, with the same 🟢 🔴 🟢. The hardness theorem behind this project embeds one into the other, a real-diagonal displacement state whose Bell outcomes are LWE samples, so the two rows are one instance seen from two sides.
* One cell was empty in every earlier draft: query access with an identifying task. Bernstein–Vazirani fills it for functions, identification with preparation circuits for states. In the identifying column queries buy only the precision rate, because a polynomial list of candidates is already easy under sampling.
* Identifying and searching coincide when the candidate class is exponentially large and parametrized. The LWE secret indexes $q^n$ hypotheses and at the same time locates the support; the distinction carries weight only when the list is polynomial (identifying) or the support must be found in an exponential space without a parametrization (searching). The LWE rows are labeled searching for that reason; Bernstein–Vazirani, its noiseless limit, is labeled identifying because one query resolves the parameter. This **LWE rule** applies to all tables: if the parameter of an exponential class is the location of the support in the Pauli or Weyl spectrum, the row sits under searching, even if a state is output at the end. This is why stabilizer states, stabilizer dimension $\geq n-t$ (few non-Clifford gates), and agnostic stabilizer learning sit under searching; stabilizer testing (one bit) and phase states of higher degree stay under identifying.
* Simon and Montanaro run the same decoder: random elements of a subspace, then Gaussian elimination. The access differs, Fourier sampling of an oracle versus differences of Bell samples, and the subgroup promise makes the decoder linear on both rows. The promise, not the access, buys the time efficiency there.


## The access-by-task quadrant

Crossing the access axis with the task axis gives four cells. All four are populated, and all four are efficient in the first budget, copies or queries: the quadrant maps only the computational boundary. Drawing them makes visible what the tables hide when read separately: computational hardness lives in exactly one cell, and it needs both restrictions at once. The rows of the three tables, grouped by access and task type, are the examples behind each cell; the identifying column is merged into estimating here because it behaves like estimating in every budget.

| | **Estimating / Identifying** (a list is given) | **Searching** (observables are output) |
| --- | --- | --- |
| **Sampling access** (i.i.d. copies, rungs 1–2) | Shadow tomography, classical shadows; with conjugate pairs the character mean over a dictionary of size $M$. *Regime 1.*<br>• **Copies**: $\mathrm{poly}(\log M, n, 1/\epsilon)$; with conjugate pairs $N = O(g^{-2}\log(M/\delta))$ for gap $g$.<br>• **Time**: $\mathrm{poly}(M)$ for an explicit list; $\exp(n)$ when a dense hypothesis is kept (general shadow tomography).<br>• **Memory**: $O(M)$ values for the list; $\exp(n)$ for the dense hypothesis. | Structure learning from Bell samples. *Regime 2 where provable.* **This project.**<br>• **Copies**: $O(\log d/\epsilon^4)$; a union bound over all $d^2$ coefficients stays logarithmic in $d$.<br>• **Time**: generic localization **LWE-hard**; polynomial under subgroup support via Gaussian elimination (Montanaro); empirical in the conjectured class.<br>• **Memory**: $O(k \log d)$ bits, the sparse list. |
| **Query access** (white-box circuit, rung 3) | Amplitude estimation.<br>• **Queries**: $O(1/\epsilon)$ at the Heisenberg rate, instead of $O(1/\epsilon^2)$ samples.<br>• **Time**: poly.<br>• **Memory**: poly. | Goldreich–Levin, Kushilevitz–Mansour, sparse FFT; Bernstein–Vazirani / QFT against LWE; peeling on chosen stabilizer groups for sparse Pauli noise. *The query route, not available at rung 2.* Populated for functions and channels; for states with a preparation oracle only the LWE instance is known to fall, and generic localization has amplitude amplification at $O(\sqrt{d/k})$ and nothing better.<br>• **Queries**: $\tilde O(k\log\vert{}V\vert{})$, resp. $\mathrm{poly}(n, 1/\tau)$.<br>• **Time**: poly.<br>• **Memory**: $O(k)$. |

Three statements carry the synthesis.

1. **Only one cell is hard, and it is hard in time alone.** The first line of every cell is green: Hoeffding plus a union bound over all $d^2$ coefficients costs $O(\log d/\epsilon^4)$ copies, the information is there. The memory line of the hard cell is green as well: the sparse list fits. The single red entry in the table is the time line of the sampling-searching cell, and the green memory entry next to it shows that the hardness is not a representation problem but a decoder problem, a cryptographic average-case statement. This is why the three budgets (Efficiency Boundaries) must be kept apart before the quadrant is read: "sample-efficient" and "hard" are statements about different budgets, and both hold in the same cell. The estimating column carries its own split, visible in its time and memory lines: an explicit polynomial-size list is efficient, which is exactly the dictionary promise, while a dense hypothesis is not.

2. **The hard cell is left to the left only by a promise, and never downward.** The row cannot be changed: nature delivers copies. The column changes only through a promise about the state. A dictionary promise moves the task to the left (Regime 1). A subgroup promise keeps the task in the cell but turns decoding into linear algebra (Regime 2). A factorization promise over coprime factors keeps it in the cell as well and turns decoding into a best-first merge of the per-factor top lists (Regime 3, composite $d$ only). Query access would move downward (the query route), but it is not available at rung 2. The provable escape routes are therefore three promises and one access change. The conjecture of this project claims that a *uniformly random* top-$k$ support is a further promise that suffices, although it falls under none of the three regimes.

3. **Neither adaptivity nor quantum memory changes the row.** Phase 2 of the own protocol chooses probes adaptively, but each probe consumes fresh i.i.d. copies. For the diagonal LWE instance behind the hardness theorem, any measurement, adaptive or not, is classical post-processing of i.i.d. draws from a classical distribution. The same holds for coherent measurements across any number of copies. The instance $\rho_s = \mathbb{E}\,\vert a,b\rangle\langle a,b\vert$ is diagonal, so dephasing each copy in the computational basis leaves $\rho_s^{\otimes k}$ unchanged, and each dephased copy is one classical LWE sample. In QUALM terms (Aharonov, Cotler, Qi 2022), every coherent protocol on copies of $\rho_s$ is simulated, at the extra cost of re-preparing basis states, by a quantum algorithm on classical LWE samples, which the post-quantum LWE assumption rules out. The hardness sits in the lab oracle, not in the coherence of access; only a different oracle, quantum examples in superposition (Grilo, Kerenidis, Zijlstra 2019) or the preparation circuit, removes it. The argument uses diagonality and says nothing about non-diagonal hard instances, for example in the cyclic single-qudit basis. A reader who takes Phase 2 for query access will conclude, wrongly, that the hardness has been circumvented. It has not; it has been *promised away* for a restricted state class, which is what the promise-problem formulation of the positioning section states.

**The classical instance of the same quadrant.** Goldreich–Levin sits in the query-searching cell, Learning Parity with Noise in the sampling-searching cell (see the classical mirror below). The thirty-year-old Boolean dichotomy is the same picture with the same hard corner; LWE is its lattice generalization and Bell sampling its quantum instance.

## Access: sampling versus query

What the world *hands over*. Three rungs, each strictly stronger than the one below it, and each step crosses a different boundary named under Efficiency Boundaries.

| Rung | Access Type | Boundary crossed | Access | What it enables |
| --- | --- | --- | --- | --- |
| **1. Copies of $\rho$** | Sample (inefficient in copies) | Starting point | Black-box i.i.d. copies; any POVM, any adaptivity | Classical shadows, single-copy tomography; Bell sampling on $\rho\otimes\rho$, which yields the clean spectrum only for real amplitudes (see the Bell-sampling primitive) |
| **2. Copies of $\rho$ and $\rho^*$** | Sample (efficient in copies) |**Sample boundary:** $\Omega(\sqrt d)$ without the conjugate copy, $O(\log d/\epsilon^4)$ with it, at constant quantum memory | Conjugate pair as a physical resource | Clean spectrum $\vert{}\mathrm{Tr}(D_{q,p}\rho)\vert{}^2$ for every $d$ |
| **3. White-box circuit** | Query (efficient in compute) | **Computational boundary:** the LWE instance becomes polynomial by Bernstein–Vazirani on superposition queries; generic localization for states is not known to follow, see the searching refinements | $U$, $U^\dagger$, controlled-$U$ preparing $\rho$ | Amplitude estimation at the Heisenberg rate $1/\epsilon$; superposition queries; $\rho^*$ by conjugating every gate |

This project stands on rung 2: past the sample boundary, in front of the computational one.

**Processes on the same ladder.** The rungs are stated for states. A process enters them through its Choi state or its input–output data state: nonadaptive use on fixed or random inputs is rung 1 or 2, with an entangled ancilla playing the role of the second copy; adaptive, controlled, inverted, or sequential use is rung 3. See "What is learned" above in this appendix.

**The primitive of rungs 1 and 2 is Bell sampling.** A transversal Bell measurement across two copies draws one operator per shot, $P \sim \vert{}\langle\bar\psi\vert{}P\vert{}\psi\rangle\vert{}^2/2^n$ on qubits and the displacement analogue on qudits (see the Bell-sampling primitive). It serves estimating (Pauli shadow tomography with $\Theta(n)$ copies) and searching (support of a sparse spectrum, $O(n)$ shots for stabilizer states) alike, which is why it is listed here as an access primitive and carries no task type in the three tables.

Rung 3 contains rung 2: whoever holds the circuit conjugates each gate and prepares $\rho^*$. Rung 2 does not contain rung 3: conjugate pairs still arrive as i.i.d. draws, and no choice of probe or shot count turns a draw into a query. The line that decides *computational* hardness runs between rungs 2 and 3, that is between **sampling access** and **query access**:

| Access type | Status under LWE | Cause |
| --- | --- | --- |
| **Sampling Access** | **Hard (Post-Quantum)** | No control over $\mathbf{a}_i$; algebraic elimination leads to error accumulation that destroys the signal |
| **Query Access (Superposition)** | **Easy (Bernstein-Vazirani / QFT)** | Targeted superpositions enable interference via QFT; noise stays isolated |

This gap is the current frontier. Almost all separations in the field are *sample* statements; whether the data can also be *processed efficiently* is far less charted. The sample-vs-query gap is fundamental, not technical: under standard cryptographic assumptions there is no generic conversion, and a state can be sample-learnable yet computationally hidden.

**The classical mirror of the sample-vs-query gap.** The same dichotomy is thirty years old in Boolean learning: 

* with *membership queries*, Goldreich–Levin (1989) finds all heavy Fourier coefficients of a function in polynomial time; 
* with *random examples only*, the same task becomes Learning Parity with Noise, for which the best known algorithm (Blum–Kalai–Wasserman 2003) runs in $2^{O(n/\log n)}$ and whose hardness is a standard cryptographic assumption. LWE is the lattice generalization of LPN. 
* Bell sampling hands you random examples of the Pauli spectrum, never queries; that is exactly why the decoder, not the measurement, is the hard half (see the structure-learning protocol).

## Measurement power: quantum memory and adaptivity

What the learner may *do* on the quantum side. These are the knobs that move the sample boundary (Efficiency Boundaries); neither of them touches the computational boundary.

| Axis | Spectrum | Key Separation / Benchmark |
| --- | --- | --- |
| **Quantum Memory** | $1 \to 2 \to k$ copies coherent | Pauli spectrum: $\Theta(n)$ copies (2-copy) vs. $2^{\Omega(n)}$ (1-copy) |
| **Adaptivity** | Fixed $\leftrightarrow$ dynamic settings | Exponential sample savings for non-local property testing |

**Vocabulary: adaptivity is not query access.** 
* *Adaptivity* means that the measurement setting on the next copy may depend on the outcomes of earlier copies. Every copy is still an i.i.d. draw of $\rho$; only the POVM changes. 
* *Query access* (the access ladder) means the learner chooses the point at which a function is evaluated, or holds the circuit that prepares the state. 
* Both involve a choice by the learner; only the second changes the access model. Sparse-FFT and Goldreich–Levin decoders are often called "adaptive" because they choose their evaluation points; in the vocabulary of this document they are *query-based*. 
* The distinction matters for Phase 2 of the own protocol: the probe $\sigma$ is chosen adaptively, but each probe is measured against fresh i.i.d. copies of $\rho$, so the protocol stays on the sampling side of the access ladder.

**The formal model: QUALM** (Aharonov, Cotler, Qi, Nat. Commun. 2022). An experiment is a quantum circuit on three registers, Nature $N$ (hidden), lab $L$ (accessible and coupled to $N$), and workspace $W$, with slots for an unknown *lab oracle*, a channel on $N\otimes L$. Its cost is the number of gates plus the number of oracle calls, and the width of $W$ is the memory parameter; the three budgets of Efficiency Boundaries are these three numbers. The two knobs of this appendix map onto two separate parts of the model:
* *The access ladder is the choice of lab oracle.* Copies of $\rho$, pairs $\rho\otimes\rho^*$, and the preparation circuit with superposition inputs are three different oracles.
* *The memory axis is coherent versus incoherent access.* Incoherent means LOCC between $L$ and $W$ and a complete measurement of $L$ between any two calls, with adaptivity allowed; coherent means no restriction. Every incoherent protocol is a probabilistic mixture of simple prepare–apply–measure protocols, which is the formal content of "adaptivity is a choice of POVM, not of access".

The two parts are independent, and all four combinations occur:

| | **Incoherent** (each call measured before the next) | **Coherent** (outputs of several calls held jointly) |
| --- | --- | --- |
| **Sample oracle** (copies of $\rho$, pairs $\rho\otimes\rho^*$, a process on fixed inputs) | Classical shadows; Phase 1 of the own protocol under a pair oracle, since the Bell measurement completes on each pair; Phase 2, equivalent to an adaptive single-copy POVM because the probe $\sigma^*$ is known | Bell sampling on $\rho\otimes\rho$ or $\rho\otimes\rho^*$ from a single-copy oracle, the first copy waiting for the second; SWAP and purity tests; the fixed-unitary problem |
| **Query oracle** (preparation circuit, superposition inputs) | Simon's algorithm, each call measured on its own (read as a QUALM in the paper) | Amplitude estimation and Grover search, sequential calls without intermediate measurement |

The same Bell measurement is therefore incoherent or coherent depending on the oracle written down, which is why the access model has to be stated explicitly. King, Wan, McClean (2024) is a separation between two oracles at the same small memory, not between coherent and incoherent access.


## Positioning of the own project

* **Field:** Quantum advantages in learning physical systems from measurement data, with minimal quantum memory (never more than two copies).
* **Approach:** *Machine-learned decoders for quantum measurement data.* A trained model replaces hand-built combinatorics (graph coloring, matrix multiplicative weights) and exploits the structure of the state class. Transfers to Hamiltonian learning, noise characterization, error-correction decoders.
* **Contribution:** Computationally efficient **structure learning** of sparse displacement spectra from two-copy Bell measurements. Triply efficient, posed as a promise problem, with provable instances (dictionary and subgroup classes) and a provable limit (LWE hardness of generic localization).
* **Structure:** Every protocol splits into a *quantum frontend* (which measurement on how many copies) and a *classical decoder*. The error factorizes into localization and estimation. Conjugate Bell pairs in front, learned CNN decoder plus sequential sign integrator behind.
* **Success criterion:** Conjugate Bell access, a signal-to-noise margin, and structural decodability under sample access. The first two secure the copies, only the third secures the time. Failures separate into statistical detectability, computational search, and identifiability at ties (see "The repaired success criterion" under Searching).
* **Cell in the quadrant:** sampling access at rung 2, searching task: the hard corner. The provable instances (dictionary, subgroup, factorized spectra over coprime factors; Regimes 1 to 3) are the promises that make the corner decodable; the LWE limit is the statement that sparsity alone is not a further one. The conjecture places a uniformly random top-$k$ support on the decodable side without proof, and the learned decoder is its empirical candidate.
