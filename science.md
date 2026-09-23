
# Quantum Learning

Alexander Del Toro Barba, PhD. [Google Scholar](https://scholar.google.com/citations?hl=en&user=fddyK-wAAAAJ) $\cdot$ [LinkedIn](https://www.linkedin.com/in/deltorobarba/)


<img src="https://raw.githubusercontent.com/deltorobarba/science/main/nature.JPG" alt="science">

<br>

Study notes quantum learning theory (learning from quantum experiments)

- [Learning from Quantum Experiments](#learning-from-quantum-experiments)
- [Searching](#searching)
- [Searching (Papers)](#searching-papers)
- [Estimating](#estimating)
- [Estimating (Papers)](#estimating-papers)
- [Identifying](#identifying)
- [Identifying (Papers)](#identifying-papers)
- [Cross-Task: Bounds, Hardness, Decoders, Surveys](#cross-task-bounds-hardness-decoders-surveys)
- [Appendix](#appendix)

---

<br>

<a id="learning-from-quantum-experiments"></a>
# Learning from Quantum Experiments

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

## Objective: Triply Efficient in Sample, Time and Memory

Every quantum learning protocol is charged in three budgets, and they scale independently:
* **Access** (Sample or Query): quantum copies of $\rho$ under sampling access, oracle calls to the preparation circuit or to the process under query access (the access ladder; for processes see "What is learned"). Efficient means $\mathrm{poly}(n, \log M, 1/\epsilon)$ copies; under query access the precision term improves to $1/\epsilon$ (Heisenberg rate), the query-side version of the sample boundary.
* **Time** (classical): efficient means $\mathrm{poly}(n, M, 1/\epsilon)$ post-processing, polynomial in $M$ rather than $\log M$, since $M$ values must at least be written down.
* **Memory** (classical): efficient means $\mathrm{poly}(n)$ bits for the learned representation; a $d \times d$ hypothesis already breaks it.

**Thesis** 
* The field has charted the sample boundary in detail: exponential separations by quantum memory, adaptivity, and conjugate access are proven and partly demonstrated in hardware (see the appendix). 
* The *computational boundary* is almost uncharted, although most sample-efficient protocols fail there. 
* The reason is proof technology: Sample lower bounds come from information theory (Holevo, packing arguments) and are unconditional, hence comparatively easy to obtain. Time lower bounds need cryptographic assumptions (LWE, pseudorandom states) and are rare. One map is dense, the other nearly empty.

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

**Oracle calls.** Uses of a preparation circuit $U$, its inverse and controlled versions, of the dynamics $e^{-iHt}$ interleaved with control, or of a channel in sequences or on inputs chosen adaptively or in superposition. Amplitude estimation, superposition queries, Heisenberg-limited Hamiltonian learning, and sequence-based noise learning count this budget. A process applied once to a fixed or random input is not an oracle call in this sense: it yields copies of the Choi state or of an input–output data state and belongs to the sample primitives. Rung 3 of the access ladder, where the precision rate improves to $1/\epsilon$ and where the search problems of the third table become polynomial.

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
* **Allcock, Doriguello, Ivanyos, Santha (2024):** Bell sampling fails on qudits, $d > 2$: the output can be uniform. Replacement measurements for stabilizer learning; the reason this project uses conjugate pairs rather than two identical copies.

**Two more separations of the same shape.** *Purity testing* (is $\rho$ pure or maximally mixed?) needs $O(1)$ copies with two-copy memory (a SWAP test) but $\Omega(2^{n/2})$ without (Chen, Cotler, Huang, Li, FOCS 2021); the memory-free lower bound also kills any single-copy route to $\mathrm{Tr}(\rho^2)$. *Pauli channel estimation*: learning all $4^n$ Pauli eigenvalues of a channel to $\pm\epsilon$ takes roughly $O(n/\epsilon^2)$ uses with ancilla-assisted entangled inputs versus $2^{\Omega(n)}$ without (Chen, Zhou, Seif, Jiang, PRA 2022), the channel version of the shadow-tomography separation. The general framework in which all of these live is **QUALM** (Aharonov, Cotler, Qi, Nat. Commun. 2022): an experiment is a quantum algorithm that calls an unknown *lab oracle*, with *coherent* access (outputs of several calls held and measured jointly) or *incoherent* access (each output measured completely before the next call, adaptivity allowed). The separations above are statements about this coherence, which is the memory axis of this document, not about the model class; which oracle nature supplies, copies of $\rho$, pairs $\rho\otimes\rho^*$, or the preparation circuit, is the separate access ladder. On qubits the SWAP test behind these separations is a coarse-grained Bell measurement: SWAP is diagonal in the Bell basis, with eigenvalue $(-1)^{\#Y}$ on the outcome $P$. On qudits with $d>2$ it is not; see the QUALM summary under Identifying (Papers).

<br>

# Searching

**Searching** (observables are *output*). Given: copies of $\rho$ and a promise about the spectrum, typically a few heavy coefficients over a flat remainder, or a structural constraint on the support; what "sparse" has to mean for the task to be hard is made precise below under "Where the wall begins". Returned: the addresses $(q,p)$ that carry the weight, and then their values. Nothing else is handed over, no list of candidates and no parametrization. Like a GWAS: first find which loci matter, then measure their effect. The error factorizes accordingly into localization and estimation, and the estimation guarantees of the next section apply only after localization has succeeded. That is why searching is genuinely harder than estimating, and it is the column in which LWE hardness sits.

**What is known.** The sample side is settled. Bell sampling on conjugate pairs estimates all $d^2$ squared magnitudes with $O(\log d/\epsilon^4)$ copies, exponentially fewer than any strategy without the conjugate copy, at constant quantum memory (King, Wan, McClean 2024). The information is therefore always there. 

* On the time side, efficient decoders exist under specific structural promises (exactly under a promise):
  * **Subgroup symmetry:** A subgroup support falls to Gaussian elimination (Montanaro 2017; Simon's algorithm under queries).
  * **Polynomial dictionaries & Locality:** Reduces the search to estimation (Quantum Juntas; locality reduces junta learning to a polynomial dictionary). Hamiltonian structure learning from real-time evolution stays Heisenberg-limited even when the interaction terms are not given (Bakshi, Liu, Moitra, Tang 2024). The classical archetype/original of all dictionary regimes is structure learning of Ising models from samples under a degree promise, in time $\tilde O(p^2)$ (Bresler 2015; Klivans, Meka 2017).
  * **Coprime factorization:** A factorized spectrum over coprime factors falls to a best-first heap (over the CRT factors).
* **Between the subgroup case and the wall (Agnostic / Approximate Subgroups):**
  * When samples are not purely algebraic but retain fidelity $\tau$ with a stabilizer state, Bell difference sampling still finds the closest stabilizer state (the stabilizer state of best fidelity $\tau$) in time $\exp(O(n/\tau^4))$ and polynomially above $\tau = \cos^2(\pi/8)$ (Grewal, Iyer, Kretschmer, Liang 2023). Stabilizer bootstrapping achieves quasipolynomial time for any $\tau$ (identifying table).
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
* (4) Where searching ends and identifying begins. A parametrized exponential class, the LWE secret, is both at once. No theorem separates the two beyond the size of the candidate list.

| Protocol or class | Object | Task type: given → returned | Copies or queries (access) | Time | Memory | Status & Condition |
| --- | --- | --- | --- | --- | --- | --- |
| **Sparse displacement spectra from Bell samples** (this project; see the structure-learning protocol) | State | Searching: sparsity promise → support and values of the spectrum | Sample: $O(\log d/\epsilon^4)$ | Generic localization LWE-hard | $O(k \log d)$ bits, the sparse list | 🟢 🔴 🟢; search too hard, **this project's cell** |
| **LWE from i.i.d. samples** (Regev 2005) and its displacement instance: a real-diagonal state whose Bell outcomes are LWE samples | Classical function; a state in the displacement instance | Searching: noisy linear samples $(\mathbf{a}_i, \langle\mathbf{a}_i,\mathbf{s}\rangle + e_i)$ → the secret $\mathbf{s}$, i.e. the hidden line that carries the support | Sample: poly, information-theoretically sufficient | Hard under the LWE assumption; classical mirror LPN, best known $2^{O(n/\log n)}$ (Blum–Kalai–Wasserman 2003) | poly, the secret | 🟢 🔴 🟢; the generic hard case, **the theorem behind this project's cell** |
| **Pseudomagic states** (Gu, Leone, Ghosh, Eisert, Yelin, Quek 2023) | State ensemble: subset phase states on $2^k$ strings | Searching in one-bit form: stabilizer entropy $\omega(\log n)$ or $\Theta(n)$, i.e. a Pauli spectrum with participation number $2^{n+\omega(\log n)}$ or $4^n$ → one bit; finding the concentrated support would decide it | Sample: poly copies suffice information-theoretically | No polynomial-time distinguisher under quantum-secure one-way functions; magic and entanglement are tunable independently | poly, the key | 🟢 🔴 🟢; the second hard endpoint of this column, from one-way functions instead of lattices; below stabilizer entropy $O(\log n)$ the class becomes distinguishable (Grewal et al. 2023), so the threshold in participation number is $2^n\mathrm{poly}(n)$ |
| **Stabilizer states** (Montanaro 2017) | State | Searching: subgroup promise → the stabilizer group, i.e. the support | Sample: $O(n)$ | $O(n^3)$, Gaussian elimination on Bell differences | $O(n^2)$, the tableau | 🟢 🟢 🟢; subgroup promise |
| **Factorized spectra over coprime factors** (Regime 3 of the own conjecture, extension G3) | State | Searching: product promise $y_{u_1\dots u_m} = \prod_j y_{u_j}(\rho_j)$ across the CRT factors of $d$ → the top-$k$ of the product from the per-factor top lists by a best-first heap | Sample: one Bell record per factor, $O(\log d_j/\epsilon^4)$ each | $\mathrm{poly}(k, \log d)$ heap operations | $O(k)$ | 🟢 🟢 🟢; factorization promise, composite $d$ only |
| **Stabilizer states on qudits, $d > 2$** (Allcock, Doriguello, Ivanyos, Santha 2024) | State | Searching: subgroup promise → the stabilizer group, where plain Bell sampling on $\rho\otimes\rho$ can be uniform and reveal nothing | Sample: $\mathrm{poly}(n, \log d)$ with the replacement measurements of that paper | poly | poly | 🟢 🟢 🟢; subgroup promise; the qudit caveat behind the conjugate-pair choice of this project |
| **Approximate stabilizer support and stabilizer fidelity** (Grewal, Iyer, Kretschmer, Liang 2023) | State | Searching: fidelity $\tau$ with some stabilizer state → the Lagrangian subspace $\mathrm{Weyl}(\vert\phi\rangle)$ of the best stabilizer state, then a stabilizer state witnessing fidelity $\geq F_S - \epsilon$; also: fewer than $n/2$ non-Clifford gates or Haar-random → one bit | Sample: Bell difference sampling, $O(n/(\epsilon^2\tau^4))$ copies; $O(n + \log n/\gamma^2)$ for $\tau \geq \cos^2(\pi/8) + \gamma$; $O(n)$ for the rank test | $\exp(O(n/\tau^4))/\epsilon^2$ via maximal cliques of the commutation graph; $O(n^3 + n^2\log n/\gamma^2)$ above $\cos^2(\pi/8)$, where the closest stabilizer state is unique and $x \in \mathrm{Weyl}(\vert\phi\rangle)$ iff $\langle\psi\vert W_x\vert\psi\rangle^2 > 1/2$ | poly | 🟢 🟢 🟢 above $\cos^2(\pi/8)$, 🟢 🔴 🟢 for small constant $\tau$; an approximate subgroup promise stays searchable because a constant fraction of the samples lies exactly in the subgroup, which is what the LWE instance destroys |
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
* **Aaronson (Proc. R. Soc. A 2007):** Learnability of quantum states: $O(n)$ samples to predict most measurements. **Rocchetto (2018):** stabilizer states are efficiently PAC-learnable.
* **Arunachalam, de Wolf (SIGACT 2017; JMLR 2018):** Survey, and the optimal bound $\Theta(d_{\mathrm{VC}}/\epsilon + \log(1/\delta)/\epsilon)$: quantum examples buy nothing in samples for classical concept classes.
* **Grilo, Kerenidis, Zijlstra (PRA 2019):** LWE is easy with quantum samples, via Bernstein–Vazirani on the example state.
* **Arunachalam, Chakraborty, Lee, Paraashar, de Wolf (ICALP 2019; Quantum 2021):** $k$-Fourier-sparse Boolean functions from $O(k^{1.5}\log^2 k)$ uniform quantum examples, independent of $n$, against $\tilde\Theta(nk)$ classical ones; $\Omega(k\log k)$ necessary. Sparsity under unit normalization is heaviness, which is why sample access suffices here and not for states.
* **Arunachalam, Grilo, Yuen (2020):** Quantum statistical queries, a rung below samples on the access ladder: the learner sees only expectation values to a tolerance.

**Where there is provably no advantage.** For PAC learning a *classical* concept class from quantum examples $\sum_x \sqrt{D(x)}\,|x, c(x)\rangle$, Arunachalam–de Wolf (JMLR 2018) showed the sample complexity is $\Theta(d_{\mathrm{VC}}/\epsilon + \log(1/\delta)/\epsilon)$, identical to the classical bound up to constants. Quantum examples buy nothing in samples for classical targets; the advantages in this document all sit in the bottom row or in *time*, never in PAC sample complexity for classical functions.

<br>

# Searching (Papers)

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
| Shin, Lee, Oh 2026 | Hamiltonian | Träger und Koeffizienten bei Sparsity $m$, ohne Kurzzeitzugriff | Query an $e^{-iHt}$, nur für $t \geq T$ | $t_{\mathrm{tot}} = \tilde O(4^m T^3/\epsilon)$, poly für $m = O(\log n)$ | 🟢 🟢 🟢 | Sparsity $m$ in der Pauli-Basis |
| Grewal, Iyer, Kretschmer, Liang 2023 (arXiv:2304.13915) | Zustand mit Stabilizer-Fidelity $\tau$ | der Lagrangesche Unterraum des besten Stabilizerzustands, dann der Zustand; Pseudozufall braucht $n/2$ nicht-Clifford-Gatter | Sample, Bell-Difference-Sampling | $O(n/(\epsilon^2\tau^4))$ Kopien, $\exp(O(n/\tau^4))/\epsilon^2$ Zeit; poly oberhalb $\cos^2(\pi/8)$ | 🟢 🟢 🟢 oberhalb $\cos^2(\pi/8)$, sonst 🟢 🔴 🟢 | approximative Untergruppe |
| Arunachalam, Chakraborty, Lee, Paraashar, de Wolf 2021 | Boolesche Funktion, $k$-Fourier-sparsam | der Fourier-Span, dann $f$ exakt | Sample, uniforme Quantenbeispiele | $O(k^{1.5}\log^2k)$, untere Schranke $\Omega(k\log k)$ | 🟢 🟢 🟢 | Sparsity $k$; Normierung eins macht sie zu Heaviness |
| Harper, Yu, Flammia 2021 | Pauli-Kanal mit $s$-sparsamen Fehlerraten | die $s$ Pauli-Fehler und ihre Raten | Query, Eigenwerte gewählter Stabilizergruppen | $O(sn)$ Abfragen, $O(n^2/\xi^2)$ Messungen, $O(sn^2)$ Zeit | 🟢 🟢 🟢 | Sparsity; gewählte Abtastpositionen |
| Nadimpalli, Parham, Vasconcelos, Yuen 2023 | QAC⁰-Kanal $n\to 1$ über den Choi-Zustand | Konzentration auf Grad $\leq k$, dann Low-Degree-Lernen | Sample, Kopien des Choi-Zustands | $n^{\mathrm{polylog}(n)}$ Kopien | 🟢 🟢 🟢 quasipolynomiell | konstante Tiefe, $\mathrm{polylog}(n)$ Hilfsqubits |
| Bresler 2015 | Ising-Modell auf $p$ Knoten | der Graph, dann die Kopplungen | Sample, i.i.d. Konfigurationen | $f(d)\log p$ Samples, $\tilde O(p^2)$ Zeit | 🟢 🟢 🟢 | Grad $\leq d$, kein Korrelationszerfall nötig |
| Klivans, Meka 2017 | Ising-Modell, $t$-weises MRF | Graph und Parameter, online | Sample, i.i.d. | $O(\lambda^2e^{O(\lambda)}\log n/\epsilon^4)$ Samples, $O(n^2N)$ Zeit; $n^{O(t)}$ für Ordnung $t$ | 🟢 🟢 🟢 | $\ell_1$-Breite $\lambda$; $n^{O(t)}$ scharf unter Sparse Parity with Noise |
| Gu, Leone, Ghosh, Eisert, Yelin, Quek 2023 | Zustandsensemble (Subset-Phasenzustände) | Stabilizer-Entropie $\omega(\log n)$ oder $\Theta(n)$, also ob das Pauli-Spektrum konzentriert ist | Sample, poly Kopien | statistisch lernbar, kein poly-Zeit-Unterscheider | 🟢 🔴 🟢 | quantensichere Einwegfunktion |

Drei Familien. Die ersten drei Paper suchen den Träger eines *Zustands* per Bell-Sampling und leben von der Untergruppenstruktur; Grewal, Iyer, Kretschmer, Liang 2023 zeigen, wie weit das trägt, wenn die Untergruppe nur approximativ gilt. Die nächsten vier suchen die schweren Pauli-Koeffizienten eines *Operators*; dort ist die Suche leicht, weil das Spektrum eines Unitaries auf eins normiert ist und Lokalität oder Sparsity den Kandidatenraum polynomiell halten. Shin, Lee, Oh setzen Bakshi et al. auf der Zugriffsachse fort: dieselbe Suche, aber ohne Kurzzeitzugriff auf die Dynamik. Die dritte Familie sind die Spiegel und Grenzen: Sparsity für Boolesche Funktionen aus Quantenbeispielen (Arunachalam et al.), gewählte Abtastung für sparsame Pauli-Kanäle (Harper, Yu, Flammia), Grad aus Tiefe für QAC⁰ (Nadimpalli et al.), das klassische Strukturlernen aus Samples unter Grad-Versprechen (Bresler; Klivans, Meka), und mit den pseudomagischen Zuständen ein zweiter harter Endpunkt, der ohne Gitterannahme auskommt. Der Absatz zur Normierung in theory.md erklärt, warum dieselbe Messung beim Zustand gegen die LWE-Wand läuft; der Abschnitt "Where the wall begins" unten sagt, welche Störung die Wand baut.

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

---

## Heisenberg-limited Hamiltonian learning without short-time control (arXiv:2604.27838)

Die Arbeit von **Myeongjin Shin, Junseo Lee und Changhun Oh** (KAIST, Seoul National University; 2026) beseitigt eine Hardware-Voraussetzung aller Heisenberg-limitierten Verfahren: den Zugriff auf beliebig kurze Evolutionszeiten. Sie zeigt, dass ein $m$-sparsamer Hamiltonian auch dann am Heisenberg-Limit gelernt werden kann, wenn jede Anfrage an $e^{-iHt}$ mindestens eine feste Dauer $T$ hat; für $m = O(\log n)$ mit polynomieller Gesamtzeit bei beliebigem konstanten $T$, für polynomielles $m$ mit einem quantitativen Tausch zwischen minimaler und gesamter Evolutionszeit. Das löst ein offenes Problem von Bakshi, Liu, Moitra und Tang.

### Einordnung in die Tabellen

* **Task type:** Searching im strengen Sinn der Tabellen: $H = \sum_{x=1}^m\alpha_xP_x$ mit unbekanntem Träger, und Algorithmus 2 heißt ausdrücklich "Coefficient and structure learning"; die Trunkierung auf $m$-Sparsity ist die Trägersuche. Die Zeile steht deshalb in der Searching-Tabelle direkt unter Bakshi, Liu, Moitra, Tang, deren offenes Problem sie löst; ihr Beitrag betrifft die Zugriffsachse (welche Evolutionszeiten das Orakel liefert), und die Estimating-Zeile von Huang, Tong, Fang, Su ist die Vorgängerin auf dieser Achse.
* **Objekt:** $m$-sparsamer, spurfreier Hamiltonian, $\Vert H\Vert_\infty\leq 1$. **Zugriff:** Query an $U(t) = e^{-iHt}$, aber nur für $t\geq T$; dazu Simulation bekannter Hamiltonians und Ancillas (halber maximal verschränkter Zustand).
* **Status:** 🟢 🟢 🟢 für $m = O(\log n)$: $t_{\mathrm{tot}} = \tilde O(\min\{4^mT^3/\epsilon, 4^mT/\epsilon^2\})$, Queries und Nachverarbeitung $\mathrm{poly}(n, 1/\epsilon)$. Für $m = \mathrm{poly}(n)$ und konstantes $T$ quasi-polynomiell.
* **Versprechen:** Sparsity $m$ in der Pauli-Basis; kein Kurzzeitzugriff nötig.

### Das Problem

Iterative Verfeinerung lernt in Runde $j$ das Residuum $\Delta H_j = H - H_j$ und braucht dafür $e^{-i\Delta H_jt}$, das per Trotter aus $e^{-iHt/N}e^{iH_jt/N}$ gebaut wird; das erzwingt $t_{\min} = \Theta(\sqrt\epsilon)$ oder $\Theta(1/m)$. Kontrollpulse haben endliche Bandbreite, Anstiegszeiten und Totzeiten, und bei vielen kurzen Segmenten dominieren Schaltfehler. Kann man Heisenberg-Skalierung mit $t_{\min}\geq T$ für konstantes $T$ erreichen?

### Kernresultate

* **Theorem 1 (logarithmisch sparsam).** $t_{\mathrm{tot}} = \tilde O(\min\{4^mT^3/\epsilon, 4^mT/\epsilon^2\})$ mit $t_{\min} = T$; für $m = O(\log n)$ effizient und Heisenberg-limitiert für jedes feste $T > 0$.
* **Theorem 2 (polynomiell sparsam).** $t_{\mathrm{tot}} = \tilde O(\min\{m^{K+2}T/\epsilon, m^KT/\epsilon^2\})$ bei $t_{\min} = T = \Theta(m^{-1/K})$, $K\in\mathbb{N}$; mit $K = \Theta(\log m)$ ist $t_{\min} = \Theta(1)$ bei $t_{\mathrm{tot}} = \tilde O(m^{2+\log m}/\epsilon)$. Erster quantitativer Tausch zwischen $t_{\min}$ und $t_{\mathrm{tot}}$.
* **Gl. (19)–(22) (Langzeit-Emulation).** $e^{-iH\tau}e^{iH_j\tau} = e^{-iH(T+\tau)}C_je^{iH_j(T+\tau)}$ mit $C_j = e^{iHT}e^{-iH_jT}$; jeder kurze Trotter-Schritt wird zu einem langen Schritt plus Korrektur. $C_j$ selbst enthält Rückwärtsentwicklung, aber $C_j^\dagger = e^{iH_jT}e^{-iHT}$ ist mit Vorwärtsentwicklung zugänglich; man lernt einen Hermiteschen Generator $W_j$ mit $C_j^\dagger = e^{-iW_j}$ und simuliert $e^{iW_j}$. Fehler $\epsilon'$ bei $\Vert W_j - \tilde W_j\Vert_F\leq\epsilon'/(2N)$.
* **Struktur von $W_j$.** Im logarithmisch sparsamen Regime ist $W_j$ auf einem Pauli-Raum der Größe $\leq 4^m$ getragen; im polynomiellen Regime dicht, aber per Baker–Campbell–Hausdorff quasi-sparsam approximierbar.
* **Koeffizientenextraktion.** $e^{-i\Delta H_jt}$ auf die Hälfte eines maximal verschränkten Zustands angewendet kodiert die Pauli-Koeffizienten von $\Delta H_j$ als Amplituden erster Ordnung; sparsame Zustandstomographie liest sie, Trunkierung erhält $m$-Sparsity und Normschranke, $\eta_{j+1} = \eta_j/2$. Frühe Runden mit großem Fehler laufen mit einer Standard-Quantenlimit-Routine.

### Methodischer Ansatz

* Der Kern ist die Umschreibung eines Produktformel-Schritts in einen langen Schritt mit fester Korrektur, und die Beobachtung, dass die Korrektur ein Hamiltonian mit kontrollierter Norm und Sparsity ist, der selbst mit langen Zeiten gelernt werden kann; das Lernen wird also zweistufig, erst $W_j$, dann $\Delta H_j$.
* Das Paper unterscheidet ausdrücklich minimale Evolutionszeit $t_{\min}$ von Zeitauflösung $\delta$ (Taktschritt der Kontrolle): Es behandelt die erste; die zweite bleibt offen.

### Bedeutung und Anwendungen

* Konzeptioneller Wechsel: Ultrakurze Pulse sind für informationstheoretisch optimales Lernen nicht nötig; lange Dynamik plus algorithmische Reduktion genügt.
* Löst das offene Problem 3 bei Bakshi et al. (beliebig große Zeitauflösung) für den logarithmisch sparsamen Fall und gibt für den Vielteilchenfall den ersten Tausch.
* Anschluss an Quantum Probe Tomography (lokale Sonden) und ancilla-freie Verfahren als nächste Schritte.

### Bezug zum eigenen Projekt

* Die Achse $t_{\min}$ ist genau die Achse, die in der Bakshi-Zusammenfassung als in der eigenen Taxonomie fehlend benannt wurde (Faktor Hardware-Realismus); dieses Paper macht sie zu einer eigenständigen Ressource mit Tauschkurve.
* Die Zweistufigkeit "Korrekturgenerator lernen, dann Residuum lernen" ist strukturell das eigene Zwei-Phasen-Schema mit einem Probe-Zustand: Das Unbekannte wird in eine Umgebung verschoben, in der die Messung erster Ordnung ist; hier heißt die Umgebung $\Delta H_j$, dort $\rho\otimes\tilde\rho^*$.
* Die Kodierung von Pauli-Koeffizienten als Amplituden erster Ordnung auf einem Bell-Paar ist Choi-Sampling; die sparsame Tomographie dahinter ist die Query-Version der Top-$k$-Lokalisierung, mit $4^m$ als Größe des Kandidatenraums.

### Grenzen und offene Fragen

* $4^m$ im logarithmisch sparsamen und $m^{K+2}$ im polynomiellen Regime; ob $\mathrm{poly}(m, T)/\epsilon$ bei $t_{\min} = T$ möglich ist, ist die zentrale offene Frage.
* Zeitauflösung $\delta$ (programmierbare Zeiten in $\delta\mathbb{N}$) nicht behandelt.
* Braucht Ancillas und globale Kontrolle; ancilla-freie und lokal-sondierende Varianten sind Ausblick.
* Timing-Ungenauigkeit $[(1-\delta)T, (1+\delta)T]$ nicht analysiert.

### Fragen zum Tieferbohren

* Wie überträgt sich die Umschreibung $e^{-iH\tau}e^{iH_j\tau} = e^{-iH(T+\tau)}C_je^{iH_j(T+\tau)}$ auf Displacement-Hamiltonians, deren Pauli-Raum durch $d^2$ Adressen ersetzt ist, und ist $W_j$ dann sparsam in der Displacement-Basis?
* Ist die sparsame Tomographie in Algorithmus 2 ein Query-Algorithmus (Goldreich–Levin-artig) oder ein Sample-Algorithmus auf dem Choi-Zustand, und wo genau sitzt die Trägersuche?
* Welche Tauschkurve $t_{\min}$ gegen Kopienzahl gibt es für Zustände, wenn "Evolutionszeit" durch "Präparationszeit pro Kopie" ersetzt wird?

Paper: [arXiv:2604.27838](https://arxiv.org/abs/2604.27838)

---

## Improved stabilizer estimation via Bell difference sampling (arXiv:2304.13915)

Die Arbeit von **Sabee Grewal, Vishnu Iyer, William Kretschmer und Daniel Liang** (UT Austin; 2023, v3 März 2024) macht aus Bell-Difference-Sampling ein Werkzeug für Zustände, die *nahe* an Stabilizerzuständen liegen, statt exakt welche zu sein. Drei Resultate: Pseudozufällige Zustände brauchen mindestens $n/2$ nicht-Clifford-Gatter, eine exponentielle Verbesserung; ein Zustand mit Stabilizer-Fidelity $\tau$ wird mit $O(n/(\epsilon^2\tau^4))$ Kopien und $\exp(O(n/\tau^4))/\epsilon^2$ Zeit durch einen Stabilizerzustand mit Fidelity $\geq F_S - \epsilon$ approximiert; oberhalb $\tau > \cos^2(\pi/8)$ wird das polynomiell. Das Werkzeug ist symplektische Fourier-Analyse der charakteristischen Verteilung $p_\psi$ und ihrer Faltung $q_\psi$.

### Einordnung in die Tabellen

* **Task type:** Searching gegen ein approximatives Untergruppen-Versprechen: Gesucht ist der Lagrangesche Unterraum $\mathrm{Weyl}(\vert\phi\rangle)$ des besten Stabilizerzustands, also der Träger, auf dem $q_\psi$ konzentriert ist; danach folgt der Zustand. Theorem 1.2 ist ein Ein-Bit-Test (Identifying), Theorem 1.5 ein toleranter Test.
* **Objekt:** reiner $n$-Qubit-Zustand. **Zugriff:** Sample; Bell-Difference-Sampling auf vier Kopien, zwei gleichzeitig; Klassische Schatten für die Fidelity-Schätzung der Kandidaten.
* **Status:** 🟢 🟢 🟢 für $\tau > \cos^2(\pi/8) + \gamma$: $O(n + \log n/\gamma^2)$ Kopien, $O(n^3 + n^2\log n/\gamma^2)$ Zeit. Für konstantes $\tau$ darunter 🟢 🔴 🟢: Kopien $O(n/(\epsilon^2\tau^4))$, Zeit $\exp(O(n/\tau^4))$, immer noch superpolynomiell besser als $2^{O(n^2)}$ Brute Force über alle Stabilizerzustände.
* **Versprechen:** Stabilizer-Fidelity $\geq\tau$; keines für den Pseudozufalls-Test.

### Das Problem

Montanaro lernt exakte Stabilizerzustände; Grewal et al. (2023, Regime der Stabilizerdimension) und die Vorgängerarbeit zur Pseudozufälligkeit zeigten nur $\omega(\log n)$ nötige nicht-Clifford-Gatter und "schwache Lernbarkeit" bei Fidelity $1/\mathrm{poly}$. Kann man aus Bell-Differenz-Samples einen Stabilizerzustand *finden*, der die beste Fidelity bezeugt, und wie viele nicht-Clifford-Gatter braucht Pseudozufall wirklich?

### Kernresultate

* **Theorem 1.2 / Korollar 4.10 (Pseudozufall).** Jede Familie von Clifford-Schaltkreisen, die pseudozufällige Zustände erzeugt, braucht mindestens $n/2$ nicht-Clifford-Einzelqubit-Gatter, bei diagonalen Gattern ($T$) mindestens $n$; bis auf Konstanten scharf, falls lineare quantensichere PRF existieren. Der Unterscheider: Bei weniger Gattern ist $q_\psi$ auf einem echten Unterraum von $\mathbb{F}_2^{2n}$ konzentriert, bei Haar-Zuständen antikonzentriert; $O(n)$ Samples und ein Rangtest genügen.
* **Theorem 1.3 / 5.10 (Stabilizer-Approximation).** Bei $F_S(\psi)\geq\tau$ liefert der Algorithmus $\vert\phi\rangle$ mit $\vert\langle\phi\vert\psi\rangle\vert^2\geq F_S(\psi)-\epsilon$ aus $O(n/(\epsilon^2\tau^4))$ Kopien in $\exp(O(n/\tau^4))/\epsilon^2$ Zeit. Mechanismus: $q_\psi$ ist gut auf $\mathrm{Weyl}(\vert\phi\rangle)$ getragen und dort auf keinem echten Unterraum konzentriert, also erzeugen genügend Samples den Unterraum; die Kandidaten sind maximale Cliquen im Kommutationsgraphen der Samples (Algorithmus von Tomita et al.), ihre Fidelities kommen aus Schatten. Per Binärsuche schätzt das $F_S$ bis auf $\epsilon$ mit $O(n/\epsilon^6)$ Kopien.
* **Theorem 1.4 / 6.7 (beschränkter Abstand).** Für $F_S\geq\cos^2(\pi/8)+\gamma$ ist der nächste Stabilizerzustand eindeutig, und $x\in\mathrm{Weyl}(\vert\phi\rangle)$ genau dann, wenn $\langle\psi\vert W_x\vert\psi\rangle^2 > 1/2$ (Korollar 6.4); ein Schwellentest ersetzt die Cliquensuche. Kopien $O(n + \log n/\gamma^2)$, Zeit $O(n^3 + n^2\log n/\gamma^2)$; Ausgabe ist der Maximierer selbst.
* **Theorem 1.5 / 7.7 (toleranter Test).** Für $\alpha_2 < (4\alpha_1^6-1)/3$ und $\gamma = \alpha_1^6 - (3\alpha_2+1)/4$ entscheiden $O(1/\gamma^2)$ Kopien und $O(n/\gamma^2)$ Zeit zwischen $F_S\geq\alpha_1$ und $F_S\leq\alpha_2$; Wiederholung des GNW-Tests mit Vollständigkeitsschranke aus der Vorgängerarbeit und Korrektheitsschranke aus GNW.
* **Theorem 1.6 / 3.1, 3.2 (Dualität).** Für einen Unterraum $T$: $\sum_{a\in T}p_\psi(a) = \tfrac{\vert T\vert}{2^n}\sum_{x\in T^\perp}p_\psi(x)$ und $\sum_{a\in T}q_\psi(a) = \vert T\vert\sum_{x\in T^\perp}p_\psi(x)^2$. Masse auf $T$ ist Masse auf dem Kommutanten $T^\perp$; für große $T$ wird eine Summe über $2^{\dim T}$ Terme zu einer über wenige.

### Methodischer Ansatz

* $p_\psi(x) = 2^{-n}\langle\psi\vert W_x\vert\psi\rangle^2$ ist eine Verteilung (Parseval), $q_\psi = p_\psi * p_\psi$ ist die Bell-Differenz-Verteilung (GNW). Alle Aussagen sind Konzentrations- oder Antikonzentrationsaussagen über $q_\psi$ auf Unterräumen, bewiesen mit der symplektischen Fourier-Transformation, deren Charaktere $(-1)^{[x, y]}$ die Kommutationsrelation sind.
* Der Sprung von "$\omega(\log n)$" auf "$n/2$" kommt daher, dass die Konzentration auf einem *Unterraum* getestet wird, nicht die Fidelity mit einem festen Zustand; der Rangtest sieht die Dimension, nicht die Amplitude.

### Bedeutung und Anwendungen

* Erster Algorithmus, der einen beliebigen Zustand mit einem Stabilizerzustand approximiert; agnostische Tomographie von Stabilizerzuständen beginnt hier, Chen–Gong–Ye–Zhang und GIKL 2024 bauen die Laufzeit auf quasipolynomiell um.
* Die Dualitätssätze und die $\tau^4$-artigen Schranken sind die Zutaten aller späteren toleranten Tests (Arunachalam–Dutt; Bao, van Dordrecht, Helsen).
* Anwendung auf Stabilizer-Zerlegungen magischer Zustände und damit auf Simulationsalgorithmen für nahezu-Clifford-Schaltkreise.

### Bezug zum eigenen Projekt

* Das Paper ist die Karte zwischen Regime 2 und der Wand: Ein *approximatives* Untergruppen-Versprechen bleibt suchbar, solange ein konstanter Anteil der Samples exakt auf der Untergruppe liegt. Die LWE-Instanz hat auch eine Untergruppe als Träger, aber jedes Sample liegt daneben; das ist der ganze Unterschied zwischen $\exp(O(n/\tau^4))$ und "kein Algorithmus". Die Dreiteilung ist im Abschnitt "Where the wall begins" ausgeführt.
* Der Rangtest für Pseudozufall ist ein Searching-Primitiv ohne Trägersuche: Er misst nur die Dimension des Trägers von $q_\psi$. Für das Displacement-Spektrum ist die Frage, ob der Rang der Bell-Records über $\mathbb{Z}_d$ dieselbe Information trägt; das wäre ein billiger Vortest, ob überhaupt ein Untergruppen-Regime vorliegt.
* Die Dualität "Masse auf $T$ gleich Masse auf $T^\perp$" ist dieselbe symplektische Fourier-Struktur, die den Charaktermittelwert des eigenen Protokolls begründet; sie gilt über $\mathbb{Z}_d$ unverändert.

### Grenzen und offene Fragen

* $\exp(O(n/\tau^4))$ ist für kleines konstantes $\tau$ exponentiell; der toleranter Test deckt nicht alle $(\alpha_1, \alpha_2)$ ab, und ein Test für beliebige Paare ist als offen genannt.
* Nur reine Zustände; gemischte Inputs kommen mit Chen–Gong–Ye–Zhang.
* Nur Qubits; die Dualitätssätze über $\mathbb{Z}_d$ sind nicht ausgeführt.

### Fragen zum Tieferbohren

* Wie genau wird "auf keinem echten Unterraum von $\mathrm{Weyl}(\vert\phi\rangle)$ konzentriert" quantifiziert, und woher kommt der Exponent $\tau^4$?
* Warum ist $\cos^2(\pi/8)$ die Schwelle der Eindeutigkeit, und ist die Displacement-Version für Qudits $\cos^2(\pi/2d)$?
* Lässt sich der Rangtest auf $\rho\otimes\rho^*$ mit einer Kopie weniger führen, weil dort $p_\psi$ statt $q_\psi$ gezogen wird?

Paper: [arXiv:2304.13915](https://arxiv.org/abs/2304.13915)

---

## Two new results about quantum exact learning (arXiv:1810.00481)

Die Arbeit von **Srinivasan Arunachalam, Sourav Chakraborty, Troy Lee, Manaswi Paraashar und Ronald de Wolf** (IBM, ISI Kolkata, UTS Sydney, QuSoft/CWI; ICALP 2019, Quantum 2021) zeigt, dass eine $k$-Fourier-sparsame Boolesche Funktion aus $O(k^{1.5}\log^2k)$ uniformen Quantenbeispielen exakt gelernt werden kann, unabhängig von $n$, gegenüber $\tilde\Theta(nk)$ klassischen Beispielen (Haviv–Regev). Zweitens: $Q$ Quanten-Membership-Queries lassen sich durch $O(Q^2\log\vert\mathcal{C}\vert/\log Q)$ klassische ersetzen. Für dieses Dokument zählt das erste Resultat: Searching mit Sample-Zugriff unter einem reinen Sparsity-Versprechen.

### Einordnung in die Tabellen

* **Task type:** Searching. Phase 1 findet den Fourier-Span (den Träger bis auf lineare Hülle) per Fourier-Sampling, Phase 2 lernt $f$ exakt; kein Heaviness-Versprechen, nur Sparsity.
* **Objekt:** Boolesche Funktion $f:\{0,1\}^n\to\{\pm 1\}$ mit $\vert\mathrm{supp}\,\hat f\vert\leq k$. **Zugriff:** Sample; uniforme Quantenbeispiele $2^{-n/2}\sum_x\vert x, f(x)\rangle$, aus denen Fourier-Sampling $S\sim\hat f(S)^2$ zieht.
* **Status:** 🟢 🟢 🟢. Kopien $O(k^{1.5}\log^2k)$, untere Schranke $\Omega(k\log k)$; Zeit polynomiell; Speicher $O(k)$ Koeffizienten.
* **Versprechen:** Sparsity $k$; die Normierung $\sum_S\hat f(S)^2 = 1$ macht daraus Heaviness.

### Das Problem

Lineare Funktionen sind der Fall $k = 1$ (Bernstein–Vazirani, ein Sample), $\ell$-Juntas der Fall $k = 2^\ell$ (Atıcı–Servedio). Klassisch brauchen $k$-sparsame Funktionen $\Theta(nk)$ uniforme Beispiele (Haviv–Regev, Theoreme 2, 3). Wie viele Quantenbeispiele braucht die Klasse, und hängt die Zahl von $n$ ab?

### Kernresultate

* **Theorem 4.** $O(k^{1.5}\log^2k)$ uniforme Quantenbeispiele genügen. **Theorem 5 / 8.** $\Omega(k\log k)$ sind nötig, über die Klasse der Indikatoren von Unterräumen der Kodimension $\log k$.
* **Theorem 6 (zwei Phasen).** Bei Fourier-Dimension $r$: Phase 1 lernt den Fourier-Span aus $O(rk)$ Fourier-Samples; Phase 2 reduziert auf $r$ Variablen und ruft Haviv–Regev mit $O(rk\log k)$ klassischen Beispielen auf. Mit $r = O(\sqrt k\log k)$ (Theorem 1, Sanyal) folgt Theorem 4.
* **Granularität (Lemma 1, Gopalan et al.).** Jeder Koeffizient einer $k$-sparsamen Booleschen Funktion ist ein Vielfaches von $2^{1-\lfloor\log k\rfloor}$; also trifft ein Fourier-Sample jeden Trägerpunkt mit Wahrscheinlichkeit $\Omega(1/k^2)$, und Coupon-Collector liefert den Träger trivial mit $O(k^2\log k)$ Samples. Die Fourier-Dimension drückt das auf $O(rk)$.
* **Theorem 9 (verbessertes Chang-Lemma).** Für $k$-sparsames $f$ mit $\hat f(0^n) = 1-2\alpha$ und Fourier-Dimension $r$: $\hat f(0^n)\leq 1 - r/(k\log k)$; damit reicht im Erwartungswert $O(k\log k/r)$ statt $O(k\log k/\sqrt r)$ Samples für einen nichttrivialen Trägerpunkt. **Vermutung 1** würde Phase 1 auf $\tilde O(k)$ drücken.
* **Theorem 10 (Queries).** $R(\mathcal{C})\leq O(Q(\mathcal{C})^2\log\vert\mathcal{C}\vert/\log Q(\mathcal{C}))$, ein $\log Q$-Faktor besser als Servedio–Gortler, über Adversary-Methode plus Entropie; scharf für lineare und für Punktfunktionen.

### Methodischer Ansatz

* Fourier-Sampling ist die Messung des Beispielzustands nach Hadamard: Man zieht $S$ mit Wahrscheinlichkeit $\hat f(S)^2$. Weil die Masse eins ist und der Träger klein, ist jeder Trägerpunkt schwer; die Suche ist damit ein Sampling-Problem, kein Dekodierproblem.
* Die Fourier-Dimension statt der Sparsity zu lernen spart, weil linear abhängige Trägerpunkte nicht einzeln gesehen werden müssen; die Basiswechsel-Lemmata 2, 3 machen daraus eine Reduktion auf $r$ Variablen.

### Bedeutung und Anwendungen

* Erstes $n$-unabhängiges Sample-Resultat für eine Sparsity-Klasse; Chang's Lemma und additive Kombinatorik erscheinen als Werkzeug der Quantenlerntheorie, bevor sie bei den toleranten Stabilizer-Tests wiederkehren.
* Die Query-Simulation grenzt ein, wie viel Quanten-Membership-Queries überhaupt sparen können: höchstens quadratisch bis auf $\log\vert\mathcal{C}\vert$.

### Bezug zum eigenen Projekt

* Das Paper ist der Beweis, dass "Sparsity" unter Normierung eins automatisch "Heaviness" ist: Granularität $2^{1-\lfloor\log k\rfloor}$ heißt Mindestgewicht $1/k^2$ pro Trägerpunkt. Für reine Zustände gilt dasselbe mit $\sum\vert y\vert^2 = d$: exakt $k$-sparsam heißt $\vert y\vert^2 = d/k$, und Bell-Sampling findet den Träger als Coupon-Collector. Das harte Regime der eigenen Arbeit ist deshalb nicht Sparsity, sondern Top-$k$ über einem flachen Rest; die Präzisierung steht in "Where the wall begins".
* Der Zwei-Phasen-Aufbau, erst Span aus Quantenbeispielen, dann klassische Verfeinerung, ist die Funktionen-Version von Phase 1 und Phase 2.
* Die untere Schranke $\Omega(k\log k)$ ist die Sample-Untergrenze der Trägersuche selbst, nicht der Schätzung; im Displacement-Fall fehlt eine solche Schranke.

### Grenzen und offene Fragen

* Lücke $k^{1.5}$ gegen $k\log k$; Vermutung 1 offen.
* Exaktes Lernen unter der Gleichverteilung; keine agnostische oder verrauschte Variante.
* Nur Boolesche Funktionen; reellwertige sparsame Funktionen klassisch bei Cheraghchi et al. mit $O(nk\log^3k)$.

### Fragen zum Tieferbohren

* Wie geht die Fourier-Dimension $r = O(\sqrt k\log k)$ (Sanyal) zustande, und gibt es ein Analogon für den symplektischen Span eines Displacement-Trägers?
* Was ist das Chang-Lemma für die charakteristische Verteilung eines Zustands, dessen Masse $d$ statt eins ist?
* Wie viel kostet Phase 1, wenn die Beispiele mit Rate $\eta$ verrauscht sind, und ab welchem $\eta$ wird daraus LPN?

Paper: [arXiv:1810.00481](https://arxiv.org/abs/1810.00481)

---

## Fast estimation of sparse quantum noise (arXiv:2007.07901)

Die Arbeit von **Robin Harper, Wenjun Yu und Steven T. Flammia** (Sydney, Tsinghua, AWS; PRX Quantum 2021) findet die $s$ nichtverschwindenden Pauli-Fehlerraten eines $n$-Qubit-Pauli-Kanals mit $O(sn)$ Abfragen eines Eigenwert-Orakels und $O(sn^2)$ klassischer Zeit, also sublinear in der Zahl $4^n$ der Adressen. Das Orakel wird mit Clifford-Schaltkreisen und Rechenbasis-Messungen realisiert, $O(n^2/\xi^2)$ Messungen für Rauschvarianz $\xi^2$. Der Decoder ist die sparse Walsh–Hadamard-Transformation von Scheibler et al. und Li et al., auf Paulis übertragen: Subsampling auf einer Stabilizergruppe, Aliasing, Peeling.

### Einordnung in die Tabellen

* **Task type:** Searching gegen ein Sparsity-Versprechen auf einem Kanal: Gesucht sind die Adressen $j\in\mathbb{F}_2^{2n}$ mit $p_j\neq 0$, dann die Raten.
* **Objekt:** Pauli-Kanal $\mathcal{E}(\rho) = \sum_jp_jP_j\rho P_j$ mit $s$-sparsamen Raten, jede $\geq\epsilon_0$. **Zugriff:** Query; die Eigenwerte $\lambda_k = 2^{-n}\mathrm{Tr}(P_k\mathcal{E}(P_k))$ einer *gewählten* Stabilizergruppe werden per Randomized-Benchmarking-artigem Experiment auf gewählten Eingabezuständen gemessen. Das ist der Zugriff, der die Suche sublinear macht.
* **Status:** 🟢 🟢 🟢. $O(sn)$ Orakelabfragen, $O(n^2/\xi^2)$ Messungen, $O(sn^2)$ Zeit, $O(s)$ Speicher; Fehler $\Vert\hat p - p\Vert_\infty\leq 2\xi/\sqrt B$ mit $B = 2^n$ Bins, Ausfallwahrscheinlichkeit $e^{-O(n)}$.
* **Versprechen:** Sparsity $s\ll 4^n$, Cutoff $\epsilon_0$, gaußsches Rauschen auf den Eigenwerten (Annahmen 1); ein zufälliger Träger für die Peeling-Analyse.

### Das Problem

Alle $4^n$ Raten zu lernen kostet $O(n2^n/\epsilon^2)$ Messungen (Flammia–Wallman); Compressed Sensing braucht nur $O(s\log 4^n)$ Messungen, aber $\mathrm{poly}(4^n)$ Zeit für die konvexe Rekonstruktion. Kushilevitz–Mansour-artige Verfahren (ebenfalls Flammia–Wallman) sind effizient, aber unpraktisch. Gesucht ist $\mathrm{poly}(s, n)$ in Messungen *und* Zeit.

### Kernresultate

* **Theorem 1.** Unter Annahmen 1 schätzen Algorithmen 2 bis 4 die $s$-sparsamen Raten bis auf $\Vert\hat p - p\Vert_\infty\leq 2\xi/\sqrt B$ mit $O(sn)$ Eigenwert-Abfragen und $O(sn^2)$ Zeit, Ausfall $\leq e^{-O(n)}$; die Abfragen kosten $O(n^2/\xi^2)$ Messungen.
* **Schritt 1 (Subsampling, Gl. 7).** Eine Stabilizergruppe $S$ mit Generatormatrix $S\in\mathbb{F}_2^{n\times 2n}$ liefert $B = 2^n$ Bins $\tilde p_j = B^{-1}\sum_v\lambda_{v\cdot S}(-1)^{j\cdot v}$, jeder eine Summe von $4^n/B$ Raten; bei $s < 2^n$ sind die meisten Bins leer oder enthalten eine Rate. Die $2^n$ kommutierenden Eigenwerte kommen aus einem einzigen Experiment mit $n$-Bit-Messung.
* **Schritt 2 (Aliasing, Gl. 8).** Verschiebung $\lambda_{m+n}\leftrightarrow(-1)^{\langle n, k\rangle}p_k$: Mit $2n+1$ verschobenen Kopien der Bins verrät das Vorzeichenmuster eines Ein-Raten-Bins die Adresse der Rate; Bitflip-Fehlererkennung macht das rauschrobust.
* **Schritt 3 (Peeling).** Gefundene Raten werden aus Mehr-Raten-Bins subtrahiert, bis alle identifiziert sind; Analyse nach Li et al. für zufällige Träger.
* **Experiment.** Auf Daten eines 14-Qubit-IBM-Geräts werden Raten bis $10^{-7}$ bei Eigenwertrauschen $10^{-3}$ bis $10^{-5}$ wiedergefunden, zwei Größenordnungen unter dem Rauschboden; künstlich eingepflanzte Vielkörper-Fehler werden mit kleinem relativen Fehler erkannt.

### Methodischer Ansatz

* Raten und Eigenwerte sind ein Walsh–Hadamard-Paar über $\mathbb{F}_2^{2n}$ mit der symplektischen Form als Bilinearform; die Eigenwerte sind das "Zeitsignal", die Raten das sparsame "Frequenzsignal". Die Wahl der Stabilizergruppe ist die Wahl der Abtastpositionen, und genau diese Wahl fehlt bei i.i.d. Samples.
* Für heutige Geräte wird die Stabilizergruppe aus einer Schicht nichtüberlappender Zwei-Qubit-Cliffords gebaut, damit die Schaltkreise flach bleiben.

### Bedeutung und Anwendungen

* Praktische Rauschcharakterisierung für 10 bis 20 Qubits mit $10^6$ bis $10^7$ Messungen; Grundlage für maßgeschneiderte Codes und Decoder.
* Für die Lerntheorie das Kanal-Beispiel der Searching-Spalte: ein sparse-FFT-Algorithmus, der funktioniert, weil der Experimentator die Abtastpositionen wählt.

### Bezug zum eigenen Projekt

* Das Paper ist die Query-Zelle des Quadranten für Kanäle. Der Decoder ist genau das, was der Bell-Record nicht erlaubt: Subsampling auf einer gewählten Untergruppe und Verschiebung um gewählte Offsets. Auf $\rho\otimes\rho^*$ könnte eine Clifford-Konjugation vor der Bell-Messung die Rolle der Stabilizergruppe spielen; die LWE-Wand sagt, dass das im Allgemeinen nicht reicht, und das Paper sagt, was es bräuchte, damit es reicht: kohärente Kontrolle über die Aliasing-Offsets.
* Die Fehlerschranke $2\xi/\sqrt B$ ist der Gewinn des Binning: Rauschen wird über $B = 2^n$ Bins gemittelt. Das ist derselbe Mechanismus wie der Charaktermittelwert, nur mit gewählten statt zufälligen Charakteren.
* Annahme "zufälliger Träger" ist die Average-Case-Annahme, die die eigene Konjektur (uniform zufälliger Top-$k$-Träger) ebenfalls macht; hier ist sie für das Peeling nötig und bewiesen ausreichend.

### Grenzen und offene Fragen

* Gilt für Pauli-Kanäle nach Twirling; kohärente Fehler sind vorab zu projizieren.
* Regime $s\ll 2^n$; bei extensiver Entropie exponentiell viele Raten.
* Der Faktor $m = O(1/\Delta)$ in der Schaltkreistiefe hängt vom Spektralgap des Kanals ab und kann groß sein.
* Peeling-Garantie für zufällige, nicht für adversarielle Träger.

### Fragen zum Tieferbohren

* Wie viele Stabilizergruppen und Offsets braucht das Peeling, wenn der Träger strukturiert statt zufällig ist?
* Lässt sich das Subsampling als Bell-Messung nach Clifford-Konjugation auf $\rho\otimes\rho^*$ schreiben, und was ersetzt dann das Eigenwert-Orakel?
* Wie verhält sich die Schranke $2\xi/\sqrt B$ zur Charaktermittelwert-Rate $O(1/\epsilon^4)$ bei gleicher Messzahl?

Paper: [arXiv:2007.07901](https://arxiv.org/abs/2007.07901)

---

## Pseudomagic quantum states (arXiv:2308.16228)

Die Arbeit von **Andi Gu, Lorenzo Leone, Soumik Ghosh, Jens Eisert, Susanne F. Yelin und Yihui Quek** (Harvard, UMass Boston, FU Berlin, Chicago; 2023) konstruiert Ensembles mit Stabilizer-Entropie $\omega(\log n)$, die von Ensembles mit Stabilizer-Entropie $\Theta(n)$ in Polynomialzeit nicht unterscheidbar sind: Nichtstabilizerheit ist eine versteckbare Eigenschaft. Die Konstruktion sind Subset-Phasenzustände auf $2^k$ Strings; Magie und Verschränkung lassen sich unabhängig einstellen. Folgerungen: verborgenes Scrambling, EFI-Paare ohne Einwegfunktionen, untere Schranken für Black-Box-Magie-Destillation.

### Einordnung in die Tabellen

* **Task type:** Searching in seiner Ein-Bit-Form: Ist das Pauli-Spektrum auf wenige Adressen konzentriert oder gespreizt? Wer den konzentrierten Träger finden könnte, könnte unterscheiden; also ist die Trägersuche für diese Klasse hart. Der zweite harte Endpunkt der Searching-Spalte, aus Einwegfunktionen statt Gittern.
* **Objekt:** Zustandsfamilien $\vert\psi_{f,S}\rangle = \vert S\vert^{-1/2}\sum_{x\in S}(-1)^{f(x)}\vert x\rangle$. **Zugriff:** Sample, polynomiell viele Kopien.
* **Status:** 🟢 🔴 🟢. Statistisch ist die Stabilizer-Entropie aus polynomiell vielen Kopien bestimmbar; kein polynomieller Unterscheider unter quantensicheren Einwegfunktionen; Schlüssel polynomiell.
* **Versprechen:** Existenz quantensicherer Einwegfunktionen (für die PRF und PRP der Konstruktion).

### Das Problem

Pseudoverschränkung (Aaronson et al.) zeigt, dass Verschränkung versteckbar ist. Gilt dasselbe für Magie, die Ressource für Quantenvorteil, Simulationshärte und Destillation? Und folgt das eine aus dem anderen?

### Kernresultate

* **Definition 1 und Lemma 1.** Ein pseudomagisches Paar hat Magie $f(n)$ gegen $g(n)$, ist aber ununterscheidbar; für die Stabilizer-Rényi-Entropie $M_\alpha = \tfrac{1}{1-\alpha}\log 2^{-n}\sum_P\mathrm{Tr}(P\psi)^{2\alpha}$ muss $g(n) = \omega(\log n)$ sein.
* **Theorem 1.** Für jedes $k\in[\omega(\log n), n]$ hat das Subset-Phasen-Ensemble mit $\vert S\vert = 2^k$ Stabilizer-Entropie $M_\alpha = O(k)$, für $\alpha\leq 2$ genau $\Theta(k)$; es ist von Haar ununterscheidbar (Lücke $\omega(\log n)$ gegen $O(n)$), und schon eine Schicht Einzelqubit-Gatter macht daraus ein Paar mit maximaler Lücke. Dasselbe gilt für Robustheit, Stabilizer-Fidelity, Extent und Max-Relativentropie mit Lücke $\Theta(n)$ gegen $\Theta(\mathrm{polylog}\,n)$.
* **Theorem 2 (verborgenes Scrambling).** Ist das Ensemble zugleich pseudozufällig, sind die $2k$-Punkt-OTOCs des erzeugenden Unitaries exponentiell vom Haar-Wert getrennt: ein nicht-scramblender Unitary erzeugt Zustände, die für jeden beschränkten Beobachter gescrambelt aussehen.
* **Theorem 3 (Kryptographie).** Pseudomagische Ensembles mit einstellbarer Entropie bilden EFI-Paare, auch in einer Welt ohne quantensichere Einwegfunktionen.
* **Theorem 4 (Destillation).** Jedes effiziente Stabilizer-Protokoll, das aus unbekanntem $\rho$ einen Zustand $\vert B\rangle$ synthetisiert, braucht $\Omega(M(B)/\log^{1+c}M(\rho))$ Kopien; aus einer Ressource mit $M = O(n)$ sind effizient nur $O(\log^{1+c}n)$ $T$-Zustände destillierbar. **Theorem 5, 6:** Verschränkung $\Theta(f)$ und Magie $\Theta(g)$ sind unabhängig einstellbar, und Vorwissen über die Magie hilft der Verschränkungsdestillation nicht.

### Methodischer Ansatz

* Die Stabilizer-Entropie ist das einzige Magiemaß ohne Minimierung und schränkt alle anderen von unten ein; deshalb genügt es, sie für Subset-Phasenzustände zu berechnen. $M_2$ misst die Teilnahmezahl der charakteristischen Verteilung: $2^{n+M_2}$ effektive Pauli-Adressen von $4^n$.
* Ununterscheidbarkeit kommt aus der Pseudozufälligkeit der Subset-Phasenzustände (Aaronson et al., Theorem 2.1); die Magie-Rechnung ist neu.

### Bedeutung und Anwendungen

* Zusammen mit Pseudoverschränkung: Ressourcenmaße sind für beschränkte Beobachter keine physikalischen Observablen; nur rechnerisch zugängliche Größen haben operationelle Bedeutung.
* EFI-Paare aus Pseudomagie stärken die These, dass EFI die fundamentale Primitive der Quantenkryptographie ist.

### Bezug zum eigenen Projekt

* Die Klasse hat ein Pauli-Spektrum mit Teilnahmezahl $2^{n+\omega(\log n)}$ statt $4^n$: Der Träger ist um einen superpolynomiellen Faktor kleiner als generisch, und trotzdem findet ihn niemand effizient. Das ist eine Härteaussage über Searching, die keine Gitterannahme braucht und die Sparsity-Schwelle benennt, unter der "kleiner Träger" nichts nützt: Erst bei $M = O(\log n)$, also Teilnahmezahl $2^n\mathrm{poly}(n)$, wird die Klasse unterscheidbar (Grewal et al.). Das ist die Instanzenleiter in der Achse "Teilnahmezahl".
* Für die Displacement-Version: Subset-Phasenzustände über $\mathbb{Z}_d$ hätten dieselbe Struktur; ihr Displacement-Spektrum ist bis auf $2^{-k}$ flach, und Bell-Sampling auf $\rho\otimes\rho^*$ sieht Haar-Statistik.
* Theorem 4 ist eine Warnung für Phase 2: Aus unbekannten Zuständen effizient Struktur zu "destillieren" ist logarithmisch begrenzt, wenn kein Klassenversprechen vorliegt.

### Grenzen und offene Fragen

* Bedingt auf Einwegfunktionen; keine unbedingte Trennung.
* Ensemble-Aussage; einzelne physikalische Zustände sind nicht betroffen.
* Die Lücke $\omega(\log n)$ gegen $O(\log n)$ (Grewal et al.) ist bis auf die Schwelle geschlossen, aber der Übergang selbst ist nicht kartiert.

### Fragen zum Tieferbohren

* Wie genau berechnet sich $M_\alpha(\psi_{f,S}) = \Theta(k)$, und welche Rolle spielt die 4-fache Unabhängigkeit von $f$?
* Ist die Teilnahmezahl der charakteristischen Verteilung mit Bell-Sampling auf $\rho\otimes\rho^*$ effizient schätzbar, und wenn ja, warum widerspricht das nicht der Ununterscheidbarkeit?
* Wo liegt für Displacement-Spektren die Schwelle, ab der ein kleiner Träger ohne Schlüssel findbar wird, in Einheiten der Teilnahmezahl?

Paper: [arXiv:2308.16228](https://arxiv.org/abs/2308.16228)

---

## On the Pauli spectrum of QAC⁰ (arXiv:2311.09631)

Die Arbeit von **Shivam Nadimpalli, Natalie Parham, Francisca Vasconcelos und Henry Yuen** (Columbia, Berkeley; 2023, STOC 2024) definiert das Pauli-Spektrum eines Schaltkreises als Pauli-Spektrum des Choi-Zustands des Kanals "Schaltkreis anwenden, alles außer dem Zielqubit ausspuren" und beweist dafür eine Quantenversion des Satzes von Linial, Mansour, Nisan: Für QAC⁰-Schaltkreise der Tiefe $d$ mit $a$ Hilfsqubits liegt die Pauli-Masse jenseits Grad $k$ unter $2^{-\Omega(k^{1/d}-a)}$. Daraus folgen Average-Case-Schranken gegen Parität und Majorität und ein Lernalgorithmus mit quasipolynomiell vielen Kopien des Choi-Zustands.

### Einordnung in die Tabellen

* **Task type:** Searching über ein Grad-Versprechen, das aus der Tiefe folgt: Der Träger des Pauli-Spektrums liegt bis auf kleine Masse auf Grad $\leq k = \mathrm{polylog}(n)$, also in einem Dictionary der Größe $n^{O(k)}$; danach ist es Estimating (Low-Degree-Lernen). Der Depth-Regler der Identifying-Tabelle bekommt hier seine spektrale Begründung.
* **Objekt:** Kanal $\mathcal{E}$ von $n$ Qubits auf ein Qubit, berechnet von einem QAC⁰-Schaltkreis (konstante Tiefe, beliebig breite Toffolis, beliebige Einzelqubit-Gatter). **Zugriff:** Sample; Kopien des normierten Choi-Zustands $\Phi_{\mathcal{E}}/N$.
* **Status:** 🟢 🟢 🟢 quasipolynomiell für $a = \mathrm{polylog}(n)$: $n^{\mathrm{polylog}(n)}\log(1/\delta)$ Kopien, Ausgabe ein Kanal mit $\sum_P(\hat\Phi_{\mathcal{E}}(P) - \hat\Phi_{\tilde{\mathcal{E}}}(P))^2\leq\epsilon$.
* **Versprechen:** Tiefe $d = O(1)$, polynomielle Größe, höchstens $\tfrac12n^{1/d}$ Hilfsqubits für die Schranken, $\mathrm{polylog}(n)$ für das Lernen.

### Das Problem

LMN: Funktionen in AC⁰ haben Fourier-Masse $\leq s\cdot 2^{-\Theta(k^{1/d})}$ jenseits Grad $k$, also lernbar in quasipolynomieller Zeit und unfähig zur Parität. Für Unitaries scheitert die naive Übertragung: $X^{\otimes n}$ hat Tiefe eins und Grad $n$. Und ob QAC⁰ Parität berechnen kann, ist seit Moore 1999 offen.

### Kernresultate

* **Definition (Pauli-Spektrum eines Kanals).** Die Pauli-Koeffizienten des Choi-Zustands $\Phi_{\mathcal{E}} = (I\otimes\mathcal{E})(\vert\mathrm{EPR}_n\rangle\langle\mathrm{EPR}_n\vert)$ auf $n+1$ Qubits; das Ausspuren der Nicht-Zielqubits löst das $X^{\otimes n}$-Problem.
* **Theorem 1 / 18 (Konzentration).** $\sum_{\vert P\vert > k}\hat\Phi_{\mathcal{E}}(P)^2\leq 2^{-\Omega(k^{1/d}-a)}$ für Tiefe $d$ und $a$ Hilfsqubits; Tabelle 1 stellt das Zeile für Zeile neben LMN.
* **Theorem 2 / 33 (Schranken).** Mit $\leq\tfrac12n^{1/d}$ Hilfsqubits: Parität höchstens auf $\tfrac12 + 2^{-\Omega(n^{1/d})}$ der Eingaben, Majorität höchstens auf $1 - \Omega(n^{-1/2})$; Average-Case, wo zuvor nur Rosenthals Schranken für Tiefe zwei und $\Omega(n/d)$ Größe bekannt waren.
* **Theorem 3 / 39 (Lernen).** Für $a = \mathrm{polylog}(n)$ und $\epsilon > 1/\mathrm{poly}(n)$: ein Kanal $\tilde{\mathcal{E}}$ mit $\ell_2$-Spektralfehler $\leq\epsilon$ aus $n^{\mathrm{polylog}(n)}\log(1/\delta)$ Kopien des Choi-Zustands; berechnet $\mathcal{E}$ eine Boolesche Funktion $f$, ist die gelernte Funktion bis auf $O(\sqrt\epsilon)$ Fehler richtig. Gilt auch für konvexe Kombinationen von QAC⁰-Kanälen (Anhang A).
* **Vermutung 1.** Konzentration für alle polynomiell großen QAC⁰-Schaltkreise ohne Hilfsqubit-Schranke; sie würde Parität aus QAC⁰ ausschließen und alle QAC⁰-Schaltkreise sample-effizient lernbar machen.

### Methodischer Ansatz

* Pauli-analytische Übertragung der LMN-Beweisstruktur; die Hilfsqubit-Schranke ersetzt das, was klassisch die Switching-Lemmata leisten, und ist der Grund, warum der allgemeine Fall offen bleibt.
* Der Lernalgorithmus ist Low-Degree-Lernen: Schätze alle Koeffizienten bis Grad $k$ aus Kopien des Choi-Zustands, setze den Rest null.

### Bedeutung und Anwendungen

* Erstes Lernresultat für QAC⁰; eine neue Definition des Pauli-Spektrums, die mit Komplexität korreliert; Werkzeuge für Schranken jenseits von Lichtkegeln, die bei breiten Gattern versagen.
* Verbindung zu Quanten-Boolesche-Funktionen (Montanaro–Osborne), Low-Degree-Lernen (Arunachalam, Dutt, Escudero Gutiérrez, Palazuelos) und Junta-Tests (Chen–Nadimpalli–Yuen).

### Bezug zum eigenen Projekt

* Das Paper liefert einen Grad-Regler, der aus einer physikalischen Eigenschaft (Tiefe) folgt, statt angenommen zu werden; das ist die Sorte Versprechen, die Regime 1 der eigenen Arbeit begründen könnte, wenn sich für Displacement-Spektren eine Konzentrationsaussage aus der Präparationstiefe beweisen ließe.
* "Grad" ist im Tensorprodukt-Phasenraum definiert; in der zyklischen Basis fehlt der Begriff. Eine Displacement-Version müsste "Grad" durch eine Norm auf $\mathbb{Z}_d\times\mathbb{Z}_d$ ersetzen, etwa den Abstand zum Ursprung, und dann wäre Konzentration auf kleine Displacements genau das, was Gauß-artige Zustände zeigen.
* Der Choi-Zustand mit ausgespurten Registern ist ein Vorbild dafür, wie man aus einem Prozessobjekt ein Zustandsobjekt macht, ohne die Normierung zu verlieren.

### Grenzen und offene Fragen

* Die Hilfsqubit-Schranke $n^{1/d}$ bzw. $\mathrm{polylog}(n)$; Vermutung 1 offen.
* Sample-effizient, aber quasipolynomiell; keine Zeitschranke jenseits der Koeffizientenschätzung.
* Nur Ein-Qubit-Output.

### Fragen zum Tieferbohren

* Wo genau geht die Hilfsqubit-Zahl $a$ in den Exponenten $k^{1/d}-a$ ein, und warum additiv?
* Wie unterscheidet sich das Choi-Spektrum eines Kanals vom Pauli-Spektrum des Unitaries, wenn kein Register ausgespurt wird?
* Gibt es ein Displacement-Analogon von Tabelle 1, also eine Zeile "Konzentration", die aus der Tiefe eines Qudit-Schaltkreises folgt?

Paper: [arXiv:2311.09631](https://arxiv.org/abs/2311.09631)

---

## Efficiently learning Ising models on arbitrary graphs (arXiv:1411.6156)

Die Arbeit von **Guy Bresler** (MIT; STOC 2015) lernt den Graphen eines Ising-Modells auf $p$ Knoten mit Maximalgrad $d$ aus $f(d)\log p$ i.i.d. Samples in Zeit $f(d)\,p^2\log p$, ohne Korrelationszerfall oder andere Annahmen außer der Identifizierbarkeit ($\alpha\leq\vert\theta_{ij}\vert\leq\beta$, $\vert\theta_i\vert\leq h$). Vorher war nicht bekannt, ob die erschöpfende Suche über $p^d$ Nachbarschaften zu schlagen ist. Der Beweis ruht auf einer Struktureigenschaft: Jeder Knoten hat einen Nachbarn mit konstantem Einfluss, auch bedingt auf beliebige Mengen.

### Einordnung in die Tabellen

* **Task type:** Searching, das klassische Original: Gegeben Samples und ein Grad-Versprechen, gesucht sind die Kanten (der Träger der Kopplungen), dann die Gewichte. Die Searching-Einleitung beruft sich auf "learning graphical models"; dies ist die Quelle.
* **Objekt:** Gibbs-Verteilung $P(x)\propto\exp(\sum\theta_{ij}x_ix_j + \sum\theta_ix_i)$ auf $\{\pm\}^p$. **Zugriff:** Sample, i.i.d. Konfigurationen.
* **Status:** 🟢 🟢 🟢. Samples $f(d)\log p$ mit $f$ doppelt exponentiell in $d$ (nur einfach exponentiell ist nötig), Zeit $\tilde O(p^2)$, Speicher $O(dp)$.
* **Versprechen:** Grad $\leq d$ und Identifizierbarkeitsschranken; kein Korrelationszerfall, gültig bei tiefen Temperaturen und stark nichtuniformen Modellen.

### Das Problem

Chow–Liu lernt Bäume in $p^2$; für Graphen mit Zyklen können Nachbarn marginal unabhängig sein und weit entfernte Knoten stärker korreliert als nahe. Alle effizienten Verfahren brauchten Korrelationszerfall oder Inkohärenzbedingungen, die bei ferromagnetischen Modellen ohne Zerfall versagen (Bento–Montanari). Ist $p^d$ die Wahrheit?

### Kernresultate

* **Proposition 1.1 / 5.3 (Struktur).** Für jeden Knoten $u$ gibt es einen Nachbarn $i$ mit bedingtem Einfluss (und damit Transinformation) mindestens einer Konstanten unabhängig von $p$, auch bedingt auf beliebige Knotenmengen.
* **Theorem 1.2 / 4.1 (Algorithmus).** Mit $n = f(d)\log p$ Samples wird der Graph in Zeit $f(d)p^2\log p$ gelernt. Verfahren: Für jeden Knoten greedy Knoten nach Einfluss hinzufügen, bis eine Pseudo-Nachbarschaft konstanter Größe entsteht, dann Nichtnachbarn prunen. Nur hinzufügen, nie entfernen: Ein einflussreicher Nichtnachbar trägt Information über viele andere Nichtnachbarn, und ein Potentialargument über die bedingte Entropie begrenzt die Größe.
* **Lemma 2.1 (bedingte Zufälligkeit).** Jede bedingte Wahrscheinlichkeit eines Spins ist mindestens $\delta = \tfrac12e^{-2(\beta d + h)}$; die Größe, die überall im Beweis auftaucht.
* **Untere Schranke (zitiert).** Samples müssen exponentiell in $d$ wachsen (Santhanam–Wainwright); die $\log p$-Abhängigkeit ist optimal.

### Methodischer Ansatz

* Die Suche wird von "Nachbarschaft raten und Unabhängigkeit testen" ($p^d$ Kandidaten) zu "Nachbarn einzeln nach Einfluss sammeln" ($p$ Kandidaten pro Schritt, konstant viele Schritte); die Struktureigenschaft garantiert, dass der Greedy-Schritt immer einen echten Nachbarn im Angebot hat.
* Verbindung zu Lerntheorie: Die bedingte Verteilung eines Knotens ist eine weiche Schwellenfunktion seiner Nachbarn; der Grad macht sie zu einer Junta, und die Struktureigenschaft ist das Analogon von "Schwellenfunktionen haben Grad-eins-Fourier-Masse".

### Bedeutung und Anwendungen

* Erste effiziente Strukturlernung für beliebige Graphen beschränkten Grades; Vorlage für Klivans–Meka (optimale Samples), Vuffray et al. (Interaction Screening) und Hamilton–Koehler–Moitra (höhere Ordnung, größere Alphabete).
* Trennung von Sampling-Komplexität und Lernkomplexität: Sampling wird ohne Korrelationszerfall NP-hart, Lernen bleibt leicht.

### Bezug zum eigenen Projekt

* Das ist Regime 1 in klassischer Form: Ein Grad-Versprechen macht das Kandidaten-Dictionary polynomiell, und die Suche zerfällt in $p$ lokale Probleme. Die Quantenversion mit bekannter Termmenge (Anshu et al.; Haah–Kothari–Tang; Bakshi et al.) erbt genau diese Logik; Bakshi et al. (Strukturlernen) ist das Quantengegenstück ohne bekannte Geometrie.
* Die Struktureigenschaft ist das, was für Displacement-Spektren fehlt: eine Aussage der Form "jede schwere Adresse hat eine lokal sichtbare Signatur". Ohne sie bleibt die Suche global, und genau dort setzt die LWE-Wand an.
* "Nur hinzufügen, nie entfernen" mit Potentialargument ist ein Muster für die Top-$k$-Lokalisierung: eine Kandidatenliste konstanter Größe pro Schritt statt einer globalen Auswahl.

### Grenzen und offene Fragen

* $f(d)$ doppelt exponentiell; Klivans–Meka erreichen einfach exponentiell.
* Nur binäre paarweise Modelle; höhere Ordnung und Alphabete in den Nachfolgern.
* Selbst bei einer einzigen Kante ist $O(p^2)$ nur über das Light-Bulb-Problem (Valiant) zu unterbieten.

### Fragen zum Tieferbohren

* Wie sieht der bedingte Einfluss genau aus, und warum liefert er eine untere Schranke an die Transinformation?
* Wo geht die doppelte Exponentialität in $d$ verloren, und was macht Klivans–Meka anders?
* Gibt es eine Quantenversion der Struktureigenschaft für Gibbs-Zustände lokaler Hamiltonians ohne bekannte Termmenge?

Paper: [arXiv:1411.6156](https://arxiv.org/abs/1411.6156)

---

## Learning graphical models using multiplicative weights (arXiv:1706.06274)

Die Arbeit von **Adam R. Klivans und Raghu Meka** (UT Austin, UCLA; FOCS 2017) gibt mit dem *Sparsitron* einen Multiplicative-Weights-Algorithmus, der Ising-Modelle mit $\ell_1$-Breite $\lambda$ aus $O(\lambda^2e^{O(\lambda)}\log(n/\rho\epsilon)/\epsilon^4)$ Samples in Zeit $O(n^2N)$ lernt, online und nahezu sample-optimal gegen die Schranke von Santhanam–Wainwright; für $t$-weise Markov-Zufallsfelder in Zeit $n^{O(t)}$, was unter der Härte von Sparse Parity with Noise bis auf Konstanten optimal ist. Zugleich das erste Verfahren für nichtbinäre Alphabete.

### Einordnung in die Tabellen

* **Task type:** Searching mit anschließendem Estimating: Erst der Abhängigkeitsgraph (Korollar 5.4), dann die Parameter (Theorem 5.2) und eine Hypothese, die in statistischem Abstand nahe ist. Das Versprechen ist eine $\ell_1$-Schranke pro Nachbarschaft statt eines Grads; das macht die Klasse breiter als bei Bresler.
* **Objekt:** Ising-Modell $D(A, \theta)$ auf $\{\pm 1\}^n$, allgemeiner $t$-weises MRF mit Faktorisierungspolynom vom Grad $t$. **Zugriff:** Sample, i.i.d.; das Verfahren läuft online.
* **Status:** 🟢 🟢 🟢. Samples $O(\lambda^2e^{O(\lambda)}\log(n/\rho\epsilon)/\epsilon^4)$ für $\Vert A - \hat A\Vert_\infty\leq\epsilon$, Graph mit $O(e^{O(\lambda)}\log(n/\rho\eta)/\eta^4)$ bei Mindestkopplung $\eta$; Zeit $O(n^2N)$; $t$-weise MRF $e^{O(t)}e^{O(\lambda t)}\log(n/\rho\eta)/\eta^4$ Samples und $O(N\cdot n^t)$ Zeit.
* **Versprechen:** $\ell_1$-Breite $\lambda$ und $\delta$-Unverzerrtheit (jede Variable ist bedingt auf alle anderen mit Wahrscheinlichkeit $\geq\delta$ auf jedem Wert), die für MRFs aus der Identifizierbarkeit folgt.

### Das Problem

Bresler braucht doppelt exponentiell viele Samples in $d$, Vuffray et al. Zeit $\tilde O(n^4)$ und Feld null; für $t$-weise Felder liefen alle Verfahren in $n^{\Omega(d)}$ und gaben keine Hypothese in statistischem Abstand. Gesucht: optimale Samples, $\tilde O(n^2)$ Zeit, höhere Ordnung, allgemeine Alphabete.

### Kernresultate

* **Theorem 3.1 (Sparsitron).** Für Beispiele $(X, Y)$ mit $\mathbb{E}[Y\vert X = x] = \sigma(w\cdot x)$, $\sigma$ monoton und Lipschitz, $\Vert w\Vert_1\leq\lambda$: ein $w'$ mit kleinem quadratischen Fehler aus $O(\lambda^2\log n)$ Samples; der Beweis ist die Regret-Schranke von Hedge (Freund–Schapire). Löst zugleich sparsame verallgemeinerte lineare Modelle.
* **Theorem 5.2 / Korollar 5.4 (Ising).** Parameter bis auf $\epsilon$ in $\ell_\infty$ bzw. Graph bei Mindestkopplung $\eta$, Samples wie oben, Zeit $O(n^2N)$, online; bis auf polynomielle Verluste an der Santhanam–Wainwright-Schranke $\Omega(e^{\lambda/4}\log n/(\eta^3\cdot 2\cdot 2))$.
* **Theorem 7.2 (t-weise MRF).** Graph aus $e^{O(t)}e^{O(\lambda t)}\log(n/\rho\eta)/\eta^4$ Samples in Zeit $O(N\cdot n^t)$; **Theorem 7.5** rekonstruiert die Parameter und eine punktweise nahe Verteilung. Die Reduktion von Bresler–Gamarnik–Shah (Sparse Parity with Noise auf $t$ Variablen) macht $n^{O(t)}$ nahezu optimal.
* **Lemmata 6.2, 6.4 (Recovery).** Unter $\delta$-Unverzerrtheit impliziert kleiner $\ell_2$-Fehler der Sigmoide kleinen $\ell_1$-Abstand der Polynome; deshalb liefert der Regressionsschritt die Koeffizienten selbst, nicht nur eine Vorhersage.
* **Theorem 8.4.** Nichtbinäre Ising-Modelle mit Alphabetgröße $k$.

### Methodischer Ansatz

* Jeder Knoten ist bedingt auf die anderen ein Sigmoid einer linearen Form (Gl. Setup); Strukturlernen wird zu $n$ überwachten GLM-Problemen. Multiplikative statt additive Updates geben Samplezahlen in $\Vert w\Vert_1$ statt $\Vert w\Vert_2$, also logarithmisch in $n$.
* Best-Experts-Lesart: Kandidatennachbarn $(j, \pm)$ stimmen ab, falsche Stimmen werden multiplikativ bestraft, Nichtnachbarn verschwinden.

### Bedeutung und Anwendungen

* Subsumiert alle Vorgänger für Ising-Modelle und gibt die ersten effizienten Verfahren für höhere Ordnung; Hamilton–Koehler–Moitra erreichen zeitgleich Ähnliches mit Breslers Methode und doppelt exponentiellen Samples.
* Die Härteaussage $n^{\Omega(t)}$ unter Sparse Parity with Noise ist die klassische Zeit-Wand der Strukturlernung: Ab Ordnung $t$ zahlt man $n^t$, und ein Sparse-LPN-Algorithmus würde das brechen.

### Bezug zum eigenen Projekt

* Der Sparsitron ist ein gelernter Decoder mit Beweis: Multiplicative Weights auf einem Kandidatenraum der Größe $2n$ pro Knoten, mit Regret-Schranke statt Kombinatorik. Er ist das Muster dafür, wie ein CNN-Decoder der eigenen Arbeit theoretisch gefasst werden könnte: Online-Lernen über einer Kandidatenliste mit einer Verlustfunktion, deren Minimum die Struktur ist.
* $n^{O(t)}$ gegen Sparse-Parity-with-Noise ist die klassische Fassung von "Regime 1 bis zur Wand": Ordnung $t$ ist ein Regler mit Kosten $n^t$, und die Wand ist kryptographisch. Für Displacement-Spektren ist der Regler die Zahl $k$ der Adressen, und die Frage ist, ob $d^{O(k)}$ die richtige Skala ist.
* $\delta$-Unverzerrtheit ist die Bedingung, die aus Vorhersagequalität Parameteridentifikation macht; das eigene Protokoll braucht ein Gegenstück, das aus Bell-Statistik-Fit Trägeridentifikation macht.

### Grenzen und offene Fragen

* $\epsilon^{-4}$ und $e^{O(\lambda)}$ sind nicht optimal; die Schranke von Santhanam–Wainwright hat $e^{\lambda/4}$.
* Unverzerrtheit ist für MRFs gegeben, für allgemeine Verteilungen nicht.
* Nur klassische Verteilungen; die Quantenversion (Gibbs-Zustände ohne bekannte Termmenge) ist offen.

### Fragen zum Tieferbohren

* Wie überträgt sich die Hedge-Regret-Schranke in eine Samplezahl in $\Vert w\Vert_1$, und warum verliert man $\epsilon^{-4}$?
* Wie sieht die Reduktion von Sparse Parity with Noise auf $t$-weise MRFs (Bresler–Gamarnik–Shah) konkret aus?
* Lässt sich der Sparsitron auf Bell-Records anwenden, indem jede Adresse ein Experte ist und der Charaktermittelwert die Vorhersage?

Paper: [arXiv:1706.06274](https://arxiv.org/abs/1706.06274)

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
| **Full QST** | State | Estimating, $M = d^2$: nothing withheld → density matrix $\rho$ | Sample: $\Theta(d^2/\epsilon^2)$ entangled, $\Theta(d^3/\epsilon^2)$ single-copy | $\mathrm{poly}(d)$ | $d^2$ entries | 🔴 🔴 🔴; baseline |
| **Shadow tomography, general** (Aaronson 2018; Bădescu–O'Donnell 2021; Chen, O'Donnell, Pelecanos, Wright 2026) | State | Estimating: list of $M$ observables → $M$ values $\mathrm{Tr}(O_i\rho)$, online against adaptively chosen observables | Sample: $\mathrm{poly}(\log M, n, 1/\epsilon)$; since 2026 the classical adaptive-data-analysis rates $O(\log M\sqrt{n}/\epsilon^3)$ and $O(\sqrt M/\epsilon^2)$, down from $\tilde O(\log^2 M\cdot n/\epsilon^4)$ | $\exp(n)$: the MMW update touches a $2^n \times 2^n$ hypothesis | $\exp(n)$: that hypothesis | 🟢 🔴 🔴; hypothesis too large |
| **PAC learning of states** (Aaronson 2007) | State | Estimating, average case: observables drawn from a distribution → predictions correct for most of them | Sample: $O(n)$ | No efficient learner in general; efficient for stabilizer states (Rocchetto 2018) | $d \times d$ hypothesis in general, poly for structured classes | 🟢 🔴 🔴; generic |
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

* **Haah et al. / O'Donnell–Wright (STOC 2016):** $\Theta(d^2/\epsilon^2)$ optimal entangled tomography.
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

The estimating tasks whose object is a process. The object axis is defined in the overview under "What is learned"; the structure of a Hamiltonian with unknown geometry is searching and sits in the structure-learning protocols, circuit descriptions under a depth promise are identifying and sit in the promise catalogue. On access: Gibbs-state learning is sample access to a state, entanglement-assisted channel learning is sample access to the Choi state, Heisenberg-limited and sequence-based protocols are query access.

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

Zusammenfassungen der wichtigen Paper zum Aufgabentyp **Estimating**: die Observablen sind der Input. Gegeben sind Kopien eines Zustands, Anwendungen eines Kanals oder einer Dynamik, dazu eine Liste von $M$ Observablen, explizit oder implizit, oder eine Verteilung, aus der sie gezogen werden. Zurück kommen die $M$ Erwartungswerte bis auf $\epsilon$. Die Liste kann polynomiell und explizit sein (ein Dictionary), implizit und exponentiell (alle Paulis), verteilungsgezogen (PAC) oder sequentiell (online). Der Aufgabentyp bleibt derselbe, die Budgets ändern sich.

Jede Zusammenfassung folgt demselben Aufbau wie in der Searching-Sektion: Einordnung in die Tabellen, Problem, Kernresultate, Methode, Bedeutung, Bezug zum eigenen Projekt, Grenzen und offene Fragen, Fragen zum Tieferbohren. Die Statusglyphen lesen sich in der Reihenfolge Kopien · Zeit · Speicher.

## Übersicht

| Paper | Objekt | Was geschätzt wird | Zugriff | Kosten | Status | Versprechen |
| --- | --- | --- | --- | --- | --- | --- |
| Aaronson 2018 | Zustand | $M$ Zwei-Ausgangs-Messungen, $M$ und $D$ exponentiell | Sample, verschränkte Messungen über alle Kopien | $\tilde O(\log^4 M \cdot \log D/\epsilon^4)$ Kopien | 🟢 🔴 🔴 | keines; Hypothese ist eine $D\times D$-Matrix |
| Aaronson 2007 | Zustand | $\mathrm{Tr}(E\rho)$ für die meisten $E \sim \mathcal{D}$ | Sample, Trainingsmessungen aus $\mathcal{D}$ | $m = \tilde O(n/(\gamma^4\epsilon^4))$ Trainingsdaten (Thm. 1.1), $\tilde O(n/(\epsilon\gamma^2))$ mit Faktor $\log^2 n$ (Thm. 1.2) | 🟢 🔴 🔴 | Zukunft gleicht Vergangenheit: $E$ i.i.d. aus $\mathcal{D}$ |
| Aaronson, Chen, Hazan, Kale, Nayak 2018 | Zustand | $\mathrm{Tr}(E_t\rho)$ für adversariell gewählte $E_t$, Runde für Runde | Sample-frei nach Feedback $b_t$ | $O(n/\epsilon^2)$ Fehler, Regret $O(\sqrt{Tn})$ | 🟢 🔴 🔴 | keines; MMW über eine $2^n\times 2^n$-Hypothese |
| Bădescu, O'Donnell 2021 | Zustand | Threshold Search, Shadow Tomography, Hypothesenauswahl | Sample, unverschränkte Kopien | $O(\log^2 m/\epsilon^2)$ für Threshold Search, $\tilde O(\log^2 m\cdot\log d/\epsilon^4)$ für Shadow Tomography | 🟢 🔴 🔴 | keines |
| Chen, O'Donnell, Pelecanos, Wright 2026 | Zustand | Online Shadow Tomography | Sample, Messung gelifteter Observablen über $n$ Kopien | $O(\log m\sqrt{\log d}/\epsilon^3)$ oder $O(\sqrt m/\epsilon^2)$, die klassischen Raten | 🟢 🔴 🔴 | keines |
| Huang, Kueng, Preskill 2020 | Zustand | $M$ lineare Funktionen, Auswahl nach der Messung | Sample, Einzelkopien, zufällige Cliffords oder Paulis | $O(\log M\cdot\max_i\Vert O_i\Vert^2_{\mathrm{shadow}}/\epsilon^2)$ | 🟢 🟢 🟢 | Lokalität oder beschränkte Hilbert–Schmidt-Norm |
| Zhang, Sun, Fang, Zhang, Yuan, Lu 2021 | Zustand, 4 Photonen-Qubits | lokale Paulis, $\langle H\rangle$, $\langle H^2\rangle$, Purities, PT-Momente | Sample, Einzelkopien, lokale Cliffords in Hardware | $N_s \leq 2000$ Messungen | 🟢 🟢 🟢 | Lokalität; derandomisierte Basen |
| Fu, Koh, Goh, Kong 2024 | Zustand | dieselben Funktionen, mit engeren Median-of-Means-Konstanten | Sample, Einzelkopien | Konstante $C$ von etwa $8$ auf $\sqrt\pi$ bzw. $\sqrt2$ | 🟢 🟢 🟢 | keines; reine Nachverarbeitung |
| Hu, Choi, You 2023 | Zustand | Fidelities und Paulis nach lokal verwürfelter Dynamik endlicher Tiefe | Sample, Einzelkopien, Schaltkreis oder Hamiltonevolution | Shadow-Norm aus dem Entanglement Feature | 🟢 🟢 🟢 | lokale Verwürfelung, $P(U) = P(UV) = P(VU)$ |
| Ippoliti 2024 | Zustand | Paulis, die zur Dimer-Überdeckung passen | Sample, Einzelkopien, Bell-Messung *innerhalb* einer Kopie | $3^{k/2}$ statt $3^k$, $(3/2)^k$ mit GHZ-Basen | 🟢 🟢 🟢 | Kompatibilität mit der Dimer-Überdeckung |
| Wan, Huggins, Lee, Babbush 2023 | Zustand | lokale fermionische Observablen, Gauß-Fidelities, Slater-Überlappe | Sample, Einzelkopien, zufällige Matchgates | Varianz $\sim n^{\vert S\vert/2}$, Pfaffians in $O(n^3)$ | 🟢 🟢 🟢 | Parität, fermionische Struktur |
| Heyraud, Chomet, Tilly 2024 | Zustand | dieselben fermionischen Größen | Sample, $\mathrm{SO}(2n)$-Ensemble oder Perfect-Matching-Unterensemble | dieselben Varianzen, gatteroptimales Sampling | 🟢 🟢 🟢 | wie oben |
| Mao, Yi, Zhu 2024 | Qudit-Zustand, $d$ ungerade Primzahl | Fidelities und Weyl-Observablen | Sample, Einzelkopien, Qudit-Cliffords plus $k$ T-Gatter | Overhead $O(d)$ gegenüber Qubits, $O(1)$ ab einem T-Gatter | 🟢 🟢 🟢 | beschränkte Hilbert–Schmidt-Norm |
| Chang, Krumtünger, Larocca, West 2026 | Zustand | Observablen nahe der Diagonale einer Basis | Sample, Einzelkopien, Ensembles aus $G/K$ | Varianz wie beim Elterngruppen-Protokoll, leicht besser auf der Diagonale | 🟢 🟢 🟢 | keines |
| King, Gosset, Kothari, Babbush 2024 | Zustand | alle $4^n$ Paulis, $k$-Körper-Fermionen | Sample, Bell-Messung auf $\rho\otimes\rho$, dann Einzelkopien | $O(n\log(n/\epsilon)/\epsilon^4)$ resp. $O(k\log n\cdot p_k(4/\epsilon^2)/\epsilon^2)$ | 🟢 🟢 🟢, Zeit $\mathrm{poly}(\vert S\vert)$ | Zwei-Kopien-Speicher |
| King, Wan, McClean 2024 | Qudit-Zustand | alle $d^2$ Displacement-Amplituden, Betrag und Vorzeichen | Sample auf $\rho\otimes\rho^*$ | $O(\log d/\epsilon^4)$; $\Omega(\sqrt d)$ auf $\rho^{\otimes K}$ | 🟢 🟢 🟢 | Konjugatzugriff |
| Gross, Liu, Flammia, Becker, Eisert 2010 | Zustand | die Dichtematrix bei Rang $r$ | Sample, $O(rd\log^2 d)$ zufällige Pauli-Erwartungswerte | konvexes Programm, SVT | 🔴 🔴 🔴 in $n$ | Rang $r \ll d$ |
| Keyl, Werner 2001 | Zustand | das Spektrum | Sample, kollektive Schur-Messung auf $\rho^{\otimes N}$ | Fehler $e^{-N\cdot I(s)}$ mit relativer Entropie $I$ | 🔴 🔴 🟢 in $n$ | keines |
| Haah, Kothari, O'Donnell, Tang 2023 | Unitary | $U$ in Diamantnorm | Query, $\Theta(d^2/\epsilon)$ Anwendungen, ein Qudit | Bootstrap von $1/\epsilon^2$ auf $1/\epsilon$ | 🔴 🔴 🔴 in $n$ | keines |
| Lewis et al. 2024 | Familie von Grundzuständen | $\mathrm{Tr}(O\rho(x))$ an neuen $x$ derselben Phase | klassische Daten $(x_\ell, y_\ell)$, Shadows | $N = \log(n/\delta)\,2^{\mathrm{polylog}(1/\epsilon)}$, Zeit $O(nN)$ | 🟢 🟢 🟢 | Gap, geometrische Lokalität, bekannte Geometrie |
| Onorati, Rouzé, França, Watson 2023 | Gibbs- und Grundzustände | Lipschitz-Observablen einer Instanz; lokale Observablen in einer Phase | Sample, Einzelkopien | $O(\mathrm{polylog}(n)/\epsilon^2)$ resp. $O(\log(M/\delta)e^{\mathrm{polylog}(1/\epsilon)})$ | 🟢 🟢 🟢 | exponentieller Korrelationszerfall, GALI |
| Huang, Chen, Preskill 2023 | Kanal | $\mathrm{Tr}(O\,\mathcal{E}(\rho))$ für $\rho\sim\mathcal{D}$ lokal flach | Sample, Produkt-Inputs, Pauli-Messungen | $N = O(\log n)$ bei konstantem $\epsilon$, Zeit $O(kn^kN)$ | 🟢 🟢 🟢 | lokal flache Verteilung, beschränkter Grad |
| Arunachalam, Dutt, Escudero Gutiérrez, Palazuelos 2024 | Kanal, Unitary, Polynom | alle Pauli-Koeffizienten bei Grad $d$ | Query an $\mathcal{E}$ resp. $U$ | $\exp(\tilde O(d^2 + d\log 1/\epsilon))$, unabhängig von $n$ | 🟢 🟢 🟢 | Grad $d = O(1)$ |
| Klein, Slote, Volberg, Zhang 2023 | Qudit-Observable, Funktion auf $\mathbb{Z}_K^n$ | Low-Degree-Approximation in $L^2$ | Sample $(\rho, \mathrm{tr}[A\rho])$ auf Produktzuständen | $O(\log n)$ Samples bei konstantem Grad | 🟢 🟢 🟢 | Grad $d$, Heisenberg–Weyl- oder Gell-Mann-Basis |
| Haah, Kothari, Tang 2022 | Hamiltonian aus Gibbs-Zustand | die Koeffizienten bekannter Terme | Sample, Kopien von $e^{-\beta H}/Z$ | $O(\log(N/\delta)/(\beta^2\epsilon^2))$, Zeit linear darin | 🟢 🟢 🟢 | $\beta < \beta_c$, Low-Intersection |
| Huang, Tong, Fang, Su 2023 | Hamiltonian aus Dynamik | die Koeffizienten bekannter Terme | Query, $e^{-iHt}$ mit Ein-Qubit-Clifford-Schichten | $T = O(\epsilon^{-1}\log\delta^{-1})$, Heisenberg-Limit | 🟢 🟢 🟢 | bekannter Wechselwirkungsgraph |
| Flammia, Wallman 2020 | Pauli-Kanal | alle $4^n$ Fehlerraten, oder $s$ ausgewählte, oder ein Markov-Feld | Query, RB-artige Sequenzen von Pauli-Gattern | $O(\epsilon^{-2}n2^n)$; $O(\epsilon^{-4}\log s\log(s/\epsilon^2))$; $O_k(\epsilon^{-2}n^2\log n)$ | 🟢 🟢 🟢 bei Sparsity | Sparsity oder $k$-lokales Faktorgraph-Modell |
| Chen, Zhou, Seif, Jiang 2022 | Pauli-Kanal | alle $4^n$ Eigenwerte | Sample auf dem Choi-Zustand mit $k$ Ancilla-Qubits | $O(n2^{n-k}/\epsilon^2)$, $O(n/\epsilon^2)$ bei $k=n$; $\Omega(2^{n/3})$ ohne Ancilla | 🟢 🟢 🟢 mit Ancilla | verschränkter Ancilla-Speicher |
| Subramanian, Kwon, Jiang 2026 | Qudit- und bosonischer Kanal | Beträge der Heisenberg–Weyl-Transfermatrix | $c$ parallele Kopien von $\mathcal{E}$ oder von $\mathcal{E}\otimes\mathcal{E}^*$ | $O(\log(M/\delta)/\epsilon^4)$ mit $\mathcal{E}^*$; $\Omega(d^{2m})$ für $c < d$; $\epsilon^{-2d}$ bei $c = d$ | 🟢 🟢 🟢 mit Konjugat | Konjugatzugriff oder $d$-Kopien-Speicher |

Sechs Familien. Die ersten fünf Paper sind die generische Shadow Tomography: sample-effizient für jede Liste, mit einer $2^n\times 2^n$-Hypothese als Preis. Die nächsten neun sind Classical Shadows und ihre Ensembles: die Shadow-Norm des Ensembles entscheidet, welche Observablen billig sind. Dann die Zwei-Kopien-Paper, die die Lücke bei globalen Paulis schließen und den Konjugatzugriff einführen, die drei Tomographie-Grenzfälle (Rang, Spektrum, Unitary), die fünf Paper zum Lernen über eine Phase und über Low-Degree-Strukturen, und schließlich Hamiltonians und Kanäle. Der rote Faden für dieses Projekt: Wo eine Zeile 🟢 🟢 🟢 ist, steht ein Versprechen oder eine Ressource daneben; Zwei-Kopien-Speicher und Konjugatzugriff sind die beiden Ressourcen, die in mehreren Zeilen zugleich auftauchen.

---
## Shadow Tomography of Quantum States (arXiv:1711.01053)

Die Arbeit von **Scott Aaronson** (UT Austin; STOC 2018, erweiterte Fassung 2018) führt das Problem ein, das dieser Tabelle den Namen gibt: Gegeben ein unbekannter $D$-dimensionaler gemischter Zustand $\rho$ und $M$ bekannte Zwei-Ausgangs-Messungen $E_1, \dots, E_M$, schätze jedes $\mathrm{Tr}(E_i\rho)$ auf $\pm\epsilon$. Das Hauptresultat: $\tilde O(\epsilon^{-4}\log^4 M\cdot\log D)$ Kopien genügen, also polynomiell viele in $n = \log D$, selbst wenn $M$ exponentiell ist. Der Name stammt von Steve Flammia: Man lernt nicht $\rho$, sondern den Schatten, den $\rho$ auf die Messungen wirft.

### Einordnung in die Tabellen

* **Task type:** Estimating im Reinformat. Die Liste der Observablen ist der Input, nichts wird gesucht, nichts identifiziert. $M$ darf exponentiell sein, und genau das unterscheidet die Zeile von der naiven Schätzung mit $O(M/\epsilon^2)$ Kopien.
* **Objekt:** gemischter Zustand. **Zugriff:** Sample; die Messung ist aber eine verschränkte Prozedur über alle $k$ Kopien gleichzeitig, mit Quantenspeicher $k$. Das ist das andere Ende der Speicherachse gegenüber Classical Shadows.
* **Status:** 🟢 🔴 🔴. Kopien polylogarithmisch; Zeit und Speicher exponentiell, weil die Hypothese eine $D\times D$-Matrix ist und die Messschaltung im schlimmsten Fall polynomiell in $M$ *und* $D$ ist. Das ist die Zeile "Shadow tomography, general" der Estimating-Tabelle.
* **Versprechen:** keines. Der Preis dafür ist die Hypothesengröße; die Zeile ist der Prototyp für "hypothesis too large" im Anhang der Tabellen.

### Das Problem

Volle Tomographie braucht $\Theta(D^2)$ Kopien (O'Donnell–Wright, Haah et al.), für $n$ Qubits also $4^n$. Aaronson hatte 2016 gefragt, ob $\mathrm{poly}(\log D, \log M)$ Kopien für *alle* $M$ Erwartungswerte reichen könnten, und die Meinungen waren geteilt. Die naheliegende Idee, Gentle Measurement, scheitert ohne Versprechenslücke: Liegt $\mathrm{Tr}(E_i\rho)$ "auf der Kante", beschädigt jede Messung von $E_i$ die Kopien schwer, und man hat nur polylogarithmisch viele davon. Die Motivation kam aus der Quantengeld-Theorie, aber die Anwendungen reichen bis zu Quantum Advice und Einweg-Kommunikation.

### Kernresultate

* **Theorem 2 (Shadow Tomography).** $k = \tilde O(\log(1/\delta)\cdot\log^4 M\cdot\log D/\epsilon^4)$ Kopien genügen; die Prozedur ist explizit. Eine frühere Version hatte $1/\epsilon^5$, der Schritt zu $1/\epsilon^4$ kommt aus dem Online-Lernalgorithmus von Aaronson, Chen, Hazan, Kale und Nayak.
* **Theorem 16 und Folgerungen (Untergrenzen).** Jede Lösung braucht $\Omega(\min\{D^2, \log M\}/\epsilon^2)$ Kopien; im klassischen Spezialfall $\Omega(\min\{D, \log M\}/\epsilon^2)$, und dort ist die Schranke scharf. Bei beliebig großem $M$ subsumiert das die $\Omega(D^2)$-Schranke der Tomographie. Ob quantenmechanisch $(\log M)^{O(1)}$ Kopien unabhängig von $D$ reichen, bleibt offen.
* **Proposition 20 (Promise-Gap-Version).** Mit einem Versprechen $\mathrm{Tr}(E_i\rho) \geq c_i$ oder $\leq c_i - \epsilon$ genügen $O(\log M/\epsilon^2)$ Kopien per Gentle Measurement; das ist der leichte Teil.
* **Quantum-Occam-Vergleich (Theorem 3).** Der PAC-Satz von 2007 gibt $\tilde O(\log D/(\gamma^4\epsilon^4))$ Kopien, aber nur für einen $1-\gamma$-Anteil der Messungen; Shadow Tomography verlangt alle.
* **Anwendungen (Abschnitt 2).** Private-Key-Quantengeld, kopiergeschützte Software, Quantum Advice, Einweg-Kommunikation; Brandão et al. reduzierten anschließend die Rechenzeit per SDP.

### Methodischer Ansatz

1. **Postselected Learning.** Starte mit der maximal gemischten Hypothese $\rho_0 = I/D$. Finde eine Messung $E_i$, auf der die aktuelle Hypothese um mehr als $\epsilon$ danebenliegt, und aktualisiere $\rho_t$ durch simulierte Postselektion auf ein Ergebnis, das mit $\rho$ verträglich ist. Weil $\rho$ Gewicht mindestens $1/D$ in $I/D$ hat, konvergiert das nach $\Theta(\log D)$ Iterationen. Das ist Boosting bzw. Multiplicative Weights in Quantensprache und stammt aus dem Beweis $\mathrm{BQP/qpoly} \subseteq \mathrm{PostBQP/poly}$.
2. **Gentle Search.** Es gibt keine Alice, die die verletzten Messungen kennt. Der Quantum-OR-Bound (Aaronson 2006, korrigiert von Harrow, Lin und Montanaro) entscheidet mit $O(\log M/\epsilon^2)$ Kopien, *ob* ein $E_i$ mit $\mathrm{Tr}(E_i\rho) \geq c$ existiert, ohne die Kopien zu zerstören.
3. **Binäre Suche** über die Liste macht aus dem Entscheidungs- ein Suchproblem; die Fehlerlücke schrumpft dabei von $\epsilon$ auf $\epsilon - \alpha$, $\epsilon - 2\alpha$ und so weiter, und das erzeugt den Faktor $\log^4 M$.

### Bedeutung und Anwendungen

* Das Paper definiert die Estimating-Spalte: Die Frage "wie viele Kopien für $M$ Fragen" ist seither das Standardmaß, und alle späteren Verbesserungen (Aaronson–Rothblum, Bădescu–O'Donnell, Chen–O'Donnell–Pelecanos–Wright) messen sich an $\log^4 M \cdot \log D/\epsilon^4$.
* Es trennt das informationstheoretische vom rechnerischen Problem und benennt die Rechenzeit ausdrücklich als offen; Classical Shadows und Triply Efficient Shadow Tomography sind Antworten auf genau diese Lücke.
* Epistemisch: Ein $n$-Qubit-Zustand enthält für jede polynomiell große Familie von Schaltkreisen nur $\mathrm{poly}(n)$ Bit lernbare Information.

### Bezug zum eigenen Projekt

* Die Zeile ist der Vergleichspunkt, gegen den die "triply efficient"-Formulierung des eigenen Papers definiert ist: sample-effizient ist hier erledigt, zeit- und speichereffizient nicht. Die Instanzenleiter in objective.md fragt genau, für welche Zustandsklassen sich die $2^n\times 2^n$-Hypothese durch ein sparsames Surrogat ersetzen lässt.
* Die Unterscheidung "alle $M$" gegen "die meisten $M$" (Shadow Tomography gegen PAC) ist dieselbe wie zwischen Worst-Case-Garantie für jedes $(q,p)$ und Average-Case-Garantie über die Top-$k$-Verteilung im eigenen Protokoll.
* Postselected Learning ist der konzeptionelle Vorläufer des MMW-Schritts, den das eigene CNN ersetzt; die $\Theta(\log D)$ Iterationen sind die Zahl der adaptiven Runden, die ein gelernter Decoder mindestens implizit durchläuft.

### Grenzen und offene Fragen

* Die Messung ist eine gemeinsame Messung über alle $k$ Kopien mit Schaltkreisen polynomieller Größe in $M$ und $D$; für Hardware ist das nicht umsetzbar.
* Die Lücke zwischen $1/\epsilon^4$ und $1/\epsilon^2$, und zwischen $\log^4 M$ und $\log M$, war beim Erscheinen offen; die $M$-Abhängigkeit hat Bădescu–O'Donnell auf $\log^2 M$ und Chen et al. 2026 auf $\log M$ gebracht.
* Ob die Soundness von Aaronsons ursprünglicher OR-Prozedur gilt, ist offen; die Fassung von Harrow, Lin und Montanaro wird verwendet.
* Keine Robustheit gegen Rauschen und keine Aussage über spezielle Observablenklassen.

### Fragen zum Tieferbohren

* Wie genau simuliert Bob Postselektion klassisch, und wo geht dabei $\log D$ Speicher hinein, den ein sparsames Surrogat vermeiden müsste?
* Gilt die Untergrenze $\Omega(\min\{D^2, \log M\}/\epsilon^2)$ auch für Listen von Displacement-Operatoren mit $M = d^2$, und was sagt sie über $\rho\otimes\rho^*$?
* Welche der Anwendungen (Quantengeld, Advice) hat eine Entsprechung in der Sprache "Zustand als Hypothese, die Vorhersagen macht"?

Paper: [arXiv:1711.01053](https://arxiv.org/abs/1711.01053)

---

## The Learnability of Quantum States (arXiv:quant-ph/0608142)

Die Arbeit von **Scott Aaronson** (Waterloo, 2006; *Proc. R. Soc. A* 2007) ist der Quantum-Occam-Satz: Ein $n$-Qubit-Zustand ist im PAC-Sinn lernbar mit einer Zahl von Trainingsmessungen, die nur linear in $n$ wächst, wenn man sich damit begnügt, die *meisten* Messungen aus einer Verteilung $\mathcal{D}$ richtig vorherzusagen. Der Autor betont, der Beitrag sei konzeptionell: Die Mathematik steht bei Bartlett–Long und bei Ambainis, Nayak, Ta-Shma und Vazirani, die Beobachtung, dass sie zusammen einen Lernsatz ergeben, ist neu.

### Einordnung in die Tabellen

* **Task type:** Estimating, Average Case. Gegeben sind Trainingsmessungen $E_1, \dots, E_m \sim \mathcal{D}$ mit ihren Werten, zurück kommt eine Hypothese $\sigma$, die $\mathrm{Tr}(E\rho)$ für einen $1-\epsilon$-Anteil der $E \sim \mathcal{D}$ auf $\gamma$ genau trifft. Die Zeile "PAC learning of states" der Estimating-Tabelle.
* **Objekt:** gemischter Zustand. **Zugriff:** Sample; jede Trainingsmessung wird auf $\Theta(\log m/\eta^2)$ Kopien wiederholt, oder in der Measure-Once-Variante (Theorem 1.3) auf genau eine.
* **Status:** 🟢 🔴 🔴. Trainingsdaten linear in $n$; das Finden einer konsistenten Hypothese ist ein QMA-Suchproblem, per SDP in $\mathrm{poly}(2^n)$ lösbar. Effizient nur für strukturierte Klassen, zuerst Stabilizerzustände (Rocchetto 2018).
* **Versprechen:** kein Versprechen über den Zustand, aber eines über die Daten: Zukunft gleicht Vergangenheit, die Testmessungen stammen aus derselben Verteilung wie die Trainingsmessungen.

### Das Problem

Tomographie braucht $4^n$ Observablen; Häffner et al. brauchten für acht Ionen 656.100 Experimente. Für tausend Teilchen wäre eine Beschreibung nicht einmal in kosmischen Zeitskalen zu gewinnen, und dann stellt sich die Frage, was der Zustand überhaupt *bedeutet*: Er sollte wenigstens eine Hypothese sein, die vergangene Beobachtungen zusammenfasst und künftige vorhersagt. Die Antwort des Papers: Für Vorhersagen genügt "pretty-good tomography".

### Kernresultate

* **Theorem 1.1.** Mit $m \geq \frac{K}{\gamma^2\epsilon^2}\big(\frac{n}{\gamma^2\epsilon^2}\log^2\frac{1}{\gamma\epsilon} + \log\frac1\delta\big)$ Trainingsmessungen ist die Trainingsmenge mit Wahrscheinlichkeit $1-\delta$ "gut": Jede Hypothese $\sigma$ mit $|\mathrm{Tr}(E_i\sigma) - \mathrm{Tr}(E_i\rho)| \leq \eta$ auf allen Trainingsdaten erfüllt $\Pr_{E\sim\mathcal{D}}[|\mathrm{Tr}(E\sigma) - \mathrm{Tr}(E\rho)| > \gamma] \leq \epsilon$, sofern $\gamma\epsilon \geq 7\eta$.
* **Theorem 1.2.** Bessere Abhängigkeit von $\gamma$ und $\epsilon$ zum Preis von $n\log^2 n$: $m \geq \frac{K}{\epsilon}\big(\frac{n}{(\gamma-\eta)^2}\log^2\frac{1}{(\gamma-\eta)\epsilon} + \log\frac1\delta\big)$; in Anhang 9 wird gezeigt, dass das nahezu optimal ist.
* **Theorem 1.3 (Measure once).** Mit einem einzigen Bit pro Messung und einer Hypothese, die den quadratischen Verlust minimiert, steigt der Bedarf von $\sim n/(\gamma^4\epsilon^4)$ auf $\sim n/(\gamma^8\epsilon^4)$: $m \geq \frac{K}{\gamma^4\epsilon^2}\big(\frac{n}{\gamma^4\epsilon^2}\log^2\frac1{\gamma\epsilon} + \log\frac1\delta\big)$.
* **Adaptive Messungen (Objection 2).** Für $r$ adaptive Runden reichen $O(nr)$ Samples, und das ist optimal.
* **Anwendungen.** $R^1(f) = O(M\,Q^1(f))$ für die Einweg-Kommunikationskomplexität jeder Booleschen Funktion; $\mathrm{HeurBQP/qpoly} \subseteq \mathrm{HeurQMA/poly}$: vertrauenswürdiger klassischer Rat verifiziert unvertrauten Quantenrat auf den meisten Eingaben.

### Methodischer Ansatz

* **Fat-Shattering-Dimension.** Die Hypothesenklasse der $n$-Qubit-Zustände, als reellwertige Funktionen $E \mapsto \mathrm{Tr}(E\rho)$, hat $\gamma$-Fat-Shattering-Dimension $O(n/\gamma^2)$. Der Beweis dreht die Untergrenze für Quantum Random Access Codes von Ambainis et al. um: Wer $k$ Bits mit Fehler $p$ in $n$ Qubits kodieren will, braucht $n \geq (1-H(p))k$; also können $n$ Qubits nicht mehr als $O(n/\gamma^2)$ Messungen "shattern".
* **Bartlett–Long.** Für reellwertige Hypothesenklassen mit beschränkter Fat-Shattering-Dimension gibt es Generalisierungsschranken; sie liefern die Formeln der Theoreme.
* **Distribution-free.** $\mathcal{D}$ muss nur existieren, nicht bekannt sein; derselbe Algorithmus funktioniert für jedes $\mathcal{D}$.

### Bedeutung und Anwendungen

* Der Beginn der Quantenlerntheorie für Zustände: Shadow Tomography (2018) und Online-Lernen (2018) sind Verallgemeinerungen dieses Satzes auf "alle Messungen" und auf adversarielle Reihenfolgen.
* Objection 3 formuliert zuerst die Frage nach zeiteffizienten Speziallfällen, die später Rocchetto (Stabilizer), Grewal et al. (wenige T-Gatter) und die Promise-Kataloge der Identifying-Tabelle beantworten; die GGM-Reduktion zeigt, dass generisch effizientes Lernen Einwegfunktionen brechen würde.
* Experimentell realisiert von Rocchetto et al. (2019).

### Bezug zum eigenen Projekt

* Die Average-Case-Formulierung ist die richtige Sprache für eine gelernte Decoder-Pipeline: Das CNN wird auf einer Verteilung von Instanzen trainiert und bewertet, und die Generalisierungsgarantie ist eine Aussage über diese Verteilung, nicht über jede Adresse $(q,p)$.
* Die Fat-Shattering-Schranke $O(n/\gamma^2)$ ist das saubere Argument dafür, warum $\mathrm{poly}(n)$ Kopien informationstheoretisch immer reichen; die Härte des eigenen Problems liegt, wie in Objection 3, allein im Finden der Hypothese.
* Objection 2 ist die Antwort auf die Frage "Phase 2 ist adaptiv, gilt der Satz noch?": Ja, mit einem Faktor $r$ in der Rundenzahl.

### Grenzen und offene Fragen

* Keine Aussage über Rechenzeit; effiziente Speziallfälle waren die ausdrückliche offene Frage.
* $k$-Ausgangs-Messungen nur per Reduktion mit Faktor $k$; eine direkte Analyse fehlt.
* Die Abhängigkeit $1/(\gamma^4\epsilon^4)$ in Theorem 1.1 ist praktisch prohibitiv; Theorem 1.2 verbessert sie gegen $n\log^2 n$.
* Die i.i.d.-Annahme über die Messungen ist genau das, was das Online-Paper später aufhebt.

### Fragen zum Tieferbohren

* Wie sieht die Fat-Shattering-Rechnung für Displacement-Observablen $D_{q,p}$ auf einem einzelnen Qudit aus, wo es kein $n$ gibt, sondern nur $\log d$?
* Lässt sich das Random-Access-Code-Argument für $\rho\otimes\rho^*$-Zugriff wiederholen, und ändert der Konjugatzugriff die effektive Dimension?
* Welche Verteilung $\mathcal{D}$ über Observablen entspricht der Top-$k$-Verteilung des eigenen Protokolls, und was ist ihre effektive Fat-Shattering-Dimension?

Paper: [arXiv:quant-ph/0608142](https://arxiv.org/abs/quant-ph/0608142)

---

## Online Learning of Quantum States (arXiv:1802.09025)

Die Arbeit von **Scott Aaronson, Xinyi Chen, Elad Hazan, Satyen Kale und Ashwin Nayak** (UT Austin, Princeton, Google AI, Waterloo; NeurIPS 2018) verallgemeinert den PAC-Satz von 2007 auf das Online-Modell: Die Messungen $E_1, E_2, \dots$ kommen nacheinander, adversariell und adaptiv, und der Lerner muss vor jeder eine Vorhersage abgeben. Ergebnis: höchstens $O(n/\epsilon^2)$ Fehler größer als $\epsilon$, und im nicht-realisierbaren Fall Regret $O(\sqrt{Tn})$. Drei Beweise, jeder mit anderen Stärken.

### Einordnung in die Tabellen

* **Task type:** Estimating, sequentiell. Die Observablen werden eine nach der anderen enthüllt, zurück kommt pro Runde eine Vorhersage. Die Zeile "Online learning of quantum states" der Estimating-Tabelle.
* **Objekt:** gemischter Zustand. **Zugriff:** Sample-frei im Kern: Nach jeder Runde wird ein Feedback $b_t$ mit $|b_t - \mathrm{Tr}(E_t\rho)| \leq \epsilon/3$ geliefert; woher es stammt (Einzelkopien-Messungen), ist dem Algorithmus egal.
* **Status:** 🟢 🔴 🔴. Fehlerzahl linear in $n$; Laufzeit pro Runde exponentiell in $n$, weil $E_t$ als $2^n\times 2^n$-Matrix vorliegt und die Hypothese $\omega_t$ ebenso groß ist. Das ist unvermeidbar, solange Input und Output explizit sind.
* **Versprechen:** keines über den Zustand, keines über die Reihenfolge der Messungen.

### Das Problem

Der PAC-Satz setzt voraus, dass Trainings- und Testmessungen i.i.d. aus derselben Verteilung stammen. Im Labor bestimmt die Natur, welche Messungen möglich sind, und die Menge wächst mit der Kontrolle; der Theoretiker wird Runde für Runde herausgefordert. Gesucht ist ein Lernalgorithmus, der ohne jede Verteilungsannahme auskommt und dessen Fehlerzahl beschränkt bleibt, wo auch immer die Fehler liegen.

### Kernresultate

* **Theorem 1 (Fehlerschranke).** Es gibt eine explizite Strategie für Hypothesen $\omega_1, \omega_2, \dots$, so dass $|\mathrm{Tr}(E_t\omega_t) - \mathrm{Tr}(E_t\rho)| > \epsilon$ höchstens $O(n/\epsilon^2)$-mal vorkommt. Das ist optimal, weil die $\epsilon$-Fat-Shattering-Dimension der Zustände $\Theta(n/\epsilon^2)$ ist.
* **Theorem 2 (Regret).** Für konvexe, $L$-Lipschitz-Verluste $\ell_t$, insbesondere $L_1$ und $L_2$, gibt es eine Strategie mit Regret $R_T = O(L\sqrt{Tn})$ gegen die beste feste Hypothese im Nachhinein, auch bei adaptivem Gegner und ohne dass die Daten von einem Zustand stammen müssen. Untergrenze $\Omega(\sqrt{Tn})$ für $L_1$.
* **Sequentielle Fat-Shattering-Dimension** der $n$-Qubit-Zustände: $O(n/\epsilon^2)$, über Nayaks Random-Access-Code-Schranke und "measurement decision trees". Damit funktioniert jeder Online-Algorithmus, der nur diese Dimension braucht, bis auf $\log^{3/2} T$.
* **Anwendung.** Als Black Box in Aaronsons Shadow Tomography verbessert Theorem 1 die Kopienzahl von $1/\epsilon^5$ auf $1/\epsilon^4$.

### Methodischer Ansatz

1. **Regularized Follow-the-Leader / Matrix Exponentiated Gradient** (Abschnitt 3). Start bei $\omega_1 = 2^{-n}I$, Regularisierung mit der von-Neumann-Entropie, Update über die Matrixexponentialfunktion des akkumulierten Gradienten; die Konvexitäts- und Taylor-Argumente werden von reellen auf komplexe Matrizen übertragen. Beste Parameter, Anschluss an die Online-Convex-Optimization-Literatur.
2. **Postselektion** (Abschnitt 4). Dieselbe Idee wie im Shadow-Tomography-Paper: Verfeinere die maximal gemischte Hypothese durch simulierte postselektierte Messungen; selbständig, aber ohne optimale Parameter und ohne Regret-Aussage.
3. **Sequentielle Fat-Shattering-Dimension** (Abschnitt 5). Gibt die Regret-Schranke über Rakhlin et al. und macht den Satz portabel auf jeden Online-Lerner mit Dimensionsgarantie.

### Bedeutung und Anwendungen

* Das ist der MMW-Motor hinter allen späteren Shadow-Tomography-Verbesserungen: Bădescu–O'Donnell reduzieren Threshold Search auf diesen Fehler-beschränkten Lerner, King, Gosset, Kothari und Babbush berechnen ihren Mimicking State damit, King, Wan und McClean übertragen ihn auf Displacement-Operatoren.
* Nur Einzelkopien-Messungen und verrauschtes Feedback: näher am Labor als optimale Tomographie oder Zertifizierung, die verschränkte Messungen über exponentiell viele Kopien brauchen.
* Die Regret-Formulierung deckt den nicht-realisierbaren Fall ab: Die Daten müssen nicht von einem Zustand stammen.

### Bezug zum eigenen Projekt

* Das ist der Algorithmus, den das eigene Paper ausdrücklich ersetzt: "the Matrix Multiplicative Weights update that drives their adaptivity". Die Hypothese $\omega_t$ ist die $d\times d$-Matrix, die im eigenen Protokoll zum sparsamen Surrogat mit $O(k)$ Gewichten geworden ist.
* Die Fehlerschranke $O(n/\epsilon^2)$ ist eine Obergrenze für die Zahl der adaptiven Runden, die eine Phase-2-Strategie braucht; sie sagt, dass der sequentielle Sign-Integrator höchstens $O(\log d/\epsilon^2)$-mal "überrascht" werden kann.
* Die exponentielle Laufzeit pro Runde ist die Zeile "hypothesis too large" der Tabellen: Speicher erzwingt Zeit. Ein CNN mit fester Eingabegröße $6\times 64\times 64$ ist der Gegenentwurf, ohne Garantie.

### Grenzen und offene Fragen

* Regret $O(\sqrt{Tn})$ gegen $\Omega(n)$ für $L_2$ im realisierbaren Fall: die Lücke bleibt.
* Laufzeit exponentiell, unvermeidbar bei expliziten Matrizen; für implizit gegebene $E_t$ (etwa Paulis) ist nichts gesagt.
* Der Postselektionsbeweis liefert keine Regret-Schranke; ob er sich dafür eignet, ist offen.
* Feedback mit Fehler $\epsilon/3$ ist vorausgesetzt; wie viele Kopien es kostet, steht außerhalb des Modells.

### Fragen zum Tieferbohren

* Wie sieht das RFTL-Update konkret aus, wenn die Hypothese auf einen Träger von $k$ Displacement-Adressen beschränkt wird, und bleibt die Fehlerschranke erhalten?
* Was ist die sequentielle Fat-Shattering-Dimension der Klasse "Zustände mit $k$-sparsamem Displacement-Spektrum"?
* Wie verhält sich der Regret, wenn das Feedback aus Bell-Messungen auf $\rho\otimes\sigma^*$ mit *bekanntem* $\sigma$ stammt, also aus genau der Messung von Phase 2?

Paper: [arXiv:1802.09025](https://arxiv.org/abs/1802.09025)

---

## Improved quantum data analysis (arXiv:2011.10908)

Die Arbeit von **Costin Bădescu und Ryan O'Donnell** (Carnegie Mellon; STOC 2021, Langfassung *TheoretiCS* 2024) verbessert die Grundroutinen der Quantendatenanalyse quadratisch und vereinfacht ihre Beweise. Der Kern ist ein Quantum-Threshold-Search-Algorithmus mit $O(\log^2 m/\epsilon^2)$ Kopien statt $\tilde O(\log^4 m)$, daraus folgen Shadow Tomography mit $\tilde O(\log^2 m\cdot\log d/\epsilon^4)$ Kopien, die zugleich beste bekannte Abhängigkeit von allen drei Parametern beim Erscheinen, und Hypothesenauswahl unter $m$ Zuständen mit derselben Kopienzahl oder alternativ $\tilde O(\log^3 m/\epsilon^2)$.

### Einordnung in die Tabellen

* **Task type:** Estimating für Threshold Search und Shadow Tomography, Identifying für die Hypothesenauswahl. Das Paper steht deshalb in zwei Tabellen: als Verbesserung der Zeile "Shadow tomography, general" und als Quelle der $O(\log M)$-Kopien in "Identification: hypothesis selection".
* **Objekt:** gemischter Zustand. **Zugriff:** Sample, unverschränkte Kopien $\rho^{\otimes n}$; die Messungen selbst sind kollektiv über die Kopien, wie bei Aaronson.
* **Status:** 🟢 🔴 🔴 für Shadow Tomography, aus demselben Grund wie dort; Threshold Search selbst ist über die Observablen $A_i$ polynomiell, aber die Reduktion auf den Online-Lerner bringt die $d\times d$-Hypothese zurück.
* **Versprechen:** keines. Neu ist die Einsicht, dass die richtige klassische Entsprechung nicht Differential Privacy, sondern *Adaptive Data Analysis* ist.

### Das Problem

Klassisch schätzt man $m$ Erwartungswerte aus $O(\log m/\epsilon^2)$ Samples, indem man dieselben Samples wiederverwendet. Quantenmechanisch verändert jede Messung den Zustand, und Wiederverwendung ist heikel. Die besten Schranken waren $\tilde O(\log^4 m\cdot\log d/\epsilon^4)$ (Aaronson) und $\tilde O(\log^2 m\cdot\log^2 d/\epsilon^8)$ (Aaronson–Rothblum, aus Differential Privacy). Die Autoren wollen den Kern der Sache, das Wiederverwenden unter Konditionierung, sauber und mit optimalen Parametern behandeln.

### Kernresultate

* **Theorem 1.1 (Threshold Search).** Gegeben Observablen $0 \leq A_i \leq 1$ und Schwellen $\theta_i$: Entweder ein $j$ mit $\mathbb{E}_\rho[A_j] > \theta_j - \epsilon$ oder die Aussage "alle $\mathbb{E}_\rho[A_i] \leq \theta_i$", mit $n = \frac{\log^2 m + \ell}{\epsilon^2}\cdot O(\ell)$ Kopien, $\ell = \log(1/\delta)$. Der Algorithmus ist *online*: Die Paare $(A_t, \theta_t)$ kommen nacheinander, und er passt oder hält an.
* **Threshold Decision** (Anhang A): nur die Existenzfrage, $O(\log(m/\delta)/\epsilon^2)$ Kopien, eine Straffung von Harrow, Lin, Montanaro.
* **Theorem 1.2 ($\chi^2$-stabiles Schwellen-Reporting).** Für $S \sim \mathrm{Binomial}(n,p)$ und unabhängiges exponentielles Rauschen $X$ mit $\mathbb{E}[X] \gg \mathrm{stddev}[S]$ ändert die Konditionierung auf "$S + X$ unter der Schwelle" die Verteilung von $S$ nur um $d_{\chi^2} \lesssim \Pr[B]\cdot\mathrm{stddev}[S]/\mathbb{E}[X]$. Das ist ein rein klassischer Satz und der technische Kern; er ist komponierbar wie der Sparse-Vector-Mechanismus.
* **Theorem 1.4 (Shadow Tomography).** $n = \frac{(\log^2 m + \ell)\log d}{\epsilon^4}\cdot O(\ell)$ Kopien, online gegen adaptiv gewählte $A_t$, über die Black-Box-Reduktion auf den fehlerbeschränkten Online-Lerner von Aaronson et al.
* **Theorem 1.5 (Hypothesenauswahl).** Unter $m$ Zuständen $\sigma_i$ finde $k$ mit $d_{\mathrm{tr}}(\rho, \sigma_k) \leq 3.01\eta + \epsilon$, $\eta = \min_i d_{\mathrm{tr}}(\rho,\sigma_i)$; Kopienzahl das Minimum aus der Shadow-Tomography-Schranke und $\tilde O(\log^3 m/\epsilon^2)$. Bei paarweise weit entfernten Hypothesen wird die klassische Optimalschranke erreicht.

### Methodischer Ansatz

* Die Schwierigkeit steckt im Fall $\epsilon = \delta = 1/4$, $\theta_j = 3/4$. Man misst jede Observable $A_t$ als verstärkte Zwei-Ausgangs-Messung auf $\rho^{\otimes n}$, addiert exponentielles Rauschen zur Zählstatistik und prüft eine Schwelle. Solange kein "über der Schwelle" eintritt, ist der Zustand nach Theorem 1.2 in $\chi^2$-Divergenz kaum verändert; die Divergenzen addieren sich über die Runden, und weil jede ein kleiner Bruchteil von $\Pr[B]^2$ ist, überlebt der Zustand bis zum ersten Treffer.
* Der Übergang zu Shadow Tomography ist die Standardreduktion: Der Online-Lerner macht höchstens $O(\log d/\epsilon^2)$ Fehler, Threshold Search findet jeden Fehler mit $\log^2 m$ Kopien, und $\log d/\epsilon^2$ Fehler mal $\log^2 m/\epsilon^2$ Kopien gibt $\log^2 m\cdot\log d/\epsilon^4$.
* Die philosophische Bemerkung der Autoren: In der Praxis ist $\log d$ klein, $\epsilon$ wichtig ($1/\epsilon^4$ ist schmerzhaft), und theoretisch ist $m$ das Interessanteste, weil $\log m$ statt $\log^2 m$ die Hypothesenauswahl auf die klassische Rate bringen würde.

### Bedeutung und Anwendungen

* Beste Shadow-Tomography-Schranke von 2021 bis 2026; die Threshold-Search-Primitive ist seither Standardwerkzeug, auch in Chen, O'Donnell, Pelecanos, Wright (2026), die dieselbe Reduktion mit neuem Schadensmaß auf $\log m$ bringen.
* Die Hypothesenauswahl mit $O(\log M)$ Kopien ist die Grundlage aller Identifying-Zeilen mit polynomieller Kandidatenliste.
* Die Perspektive "Adaptive Data Analysis statt Differential Privacy" ist die konzeptionelle Brücke, die später auch in der Efron–Stein-Sichtweise von 2026 trägt.

### Bezug zum eigenen Projekt

* Threshold Search ist die formale Version von "gibt es eine Adresse mit $|y_{q,p}| \geq \theta$?": genau die Frage, die Phase 1 für alle $d^2$ Adressen gleichzeitig beantwortet, dort aber nicht-adaptiv aus dem Bell-Record. Die Kopienzahl $O(\log^2 m/\epsilon^2)$ mit $m = d^2$ ist ein Vergleichswert für die $O(\log d/\epsilon^4)$ des Konjugatpaar-Verfahrens: besser in $\epsilon$, schlechter in $\log d$, und ohne Konjugat.
* Die Hypothesenauswahl mit $3.01\eta + \epsilon$ ist der agnostische Rahmen, in dem eine Liste von Kandidatenträgern aus dem CNN bewertet werden könnte: $M$ Surrogat-Zustände, $O(\log M)$ Kopien.
* Die $\chi^2$-Stabilität ist ein sauberes Werkzeug, um zu quantifizieren, wie viel Phase 2 die Kopien "verbraucht", wenn Probe-Messungen sequentiell auf demselben Register laufen; im eigenen Protokoll werden stattdessen frische Kopien genommen, was die Analyse trivial, aber die Kopienzahl größer macht.

### Grenzen und offene Fragen

* $\log^2 m$ statt $\log m$; von den Autoren als die interessanteste Lücke benannt und 2026 geschlossen.
* $1/\epsilon^4$ statt $1/\epsilon^2$; alle Shadow-Tomography-Resultate haben "atypische" $\epsilon$-Exponenten, wie auch in Adaptive Data Analysis.
* Keine Rechenzeit-Aussage; die Reduktion auf MMW bleibt exponentiell.
* Die $\chi^2$-Schranke gilt für Binomialstatistik, also Zwei-Ausgangs-Messungen; Mehrausgangs-Messungen brauchen eine Reduktion.

### Fragen zum Tieferbohren

* Wie überträgt sich Theorem 1.2 auf die Multinomialstatistik einer Bell-Messung mit $d^2$ Ausgängen?
* Was ist die Hypothesenauswahl-Schranke, wenn die $m$ Kandidaten selbst nur als Surrogate mit $O(k\log d)$ Bits vorliegen, und gilt $3.01\eta$ dann für die Fidelity im Displacement-Spektrum?
* Wo genau verliert die Reduktion Threshold Search $\to$ Shadow Tomography den Faktor $\log d/\epsilon^2$, und ist das der Faktor, den Chen et al. 2026 mit dem Energie-Argument einsparen?

Paper: [arXiv:2011.10908](https://arxiv.org/abs/2011.10908)

---

## Online Shadow Tomography Matching the Classical Bounds (arXiv:2607.29686)

Die Arbeit von **Sitan Chen, Ryan O'Donnell, Angelos Pelecanos und John Wright** (Harvard, CMU, Berkeley; 2026) schließt die seit 2016 offene Lücke zwischen den quantenmechanischen und den klassischen Raten der Shadow Tomography. Zwei Protokolle: $O(\log m\sqrt{\log d}/\epsilon^3)$ Kopien, das erste mit $o(\log^2 m)$ und zugleich $\mathrm{poly}(\log d/\epsilon)$, und $O(\sqrt m/\epsilon^2)$ Kopien, dimensionsfrei und optimal unter dimensionsfreien Schranken. Beide gelten online gegen adaptiv gewählte Observablen, und das Minimum der beiden ist bis auf Konstanten die klassische Rate der Adaptive Data Analysis. Das Werkzeug ist neu: Messschaden wird über die *Excitation-Zerlegung* (Pickl 2011) gemessen, die duale Form der Quanten-Efron–Stein-Zerlegung.

### Einordnung in die Tabellen

* **Task type:** Estimating, online. Die Observablen $0 \preceq A^{(t)} \preceq 1$ kommen adaptiv aufgrund des bisherigen Transkripts, jede Antwort muss $\pm\epsilon$ treffen. Offline ist der Spezialfall fester Observablen, und auch dort verbessert das Paper alle drei Exponenten.
* **Objekt:** gemischter Zustand. **Zugriff:** Sample, $n$ Kopien, gemessen mit Zwei-Ausgangs-Messungen an *gelifteten* Observablen $\bar A = \frac1n\sum_i A_i$ über alle Kopien, also mit Quantenspeicher $n$.
* **Status:** 🟢 🔴 🔴. Kopien auf klassischem Niveau; das $\log m$-Protokoll läuft über MMW mit $2^n\times 2^n$-Hypothese, das $\sqrt m$-Protokoll misst direkt, aber über $d^n$-dimensionale Projektoren.
* **Versprechen:** keines. Das ist die neue Zeile "Shadow tomography, general" mit den Raten von 2026; die Tabelle und der Absatz "What is open (1)" sind entsprechend aktualisiert.

### Das Problem

Klassisch (alle Matrizen diagonal) ist das Problem Adaptive Data Analysis mit $n = O(\min\{\log m\sqrt{\log d}/\epsilon^3, \sqrt m/\epsilon^2\})$ (Bassily et al.), und es gibt Evidenz für Optimalität (Nissim et al.; Lyu–Talwar). Quantenmechanisch standen $O(\log^2 m\cdot\log d/\epsilon^4)$ (Bădescu–O'Donnell, Bostanci–Bene Watts) und offline $O(\sqrt m\log m/\epsilon^2)$ (Sinha). Bei $d$ exponentiell in $m$ war online nichts besser als der triviale Schätzer. Die Frage: Sind die klassischen Raten quantenmechanisch erreichbar?

### Kernresultate

* **Theorem 1.2.** Online Shadow Tomography mit $n = O(\sqrt K\log(m+K)/\epsilon^2)$ Kopien, $K = \Theta(\log d/\epsilon^2)$, also $O(\log m\sqrt{\log d}/\epsilon^3)$, Erfolgswahrscheinlichkeit $9/10$.
* **Theorem 1.3.** Online Shadow Tomography mit $n = O(\sqrt m/\epsilon^2)$ Kopien, unabhängig von $d$; verbessert das beste vorherige Online-Resultat um den Faktor $\sqrt m\log m$ und Sinhas Offline-Schranke $O(\sqrt m\log m/\epsilon^2)$ um $\log m$, und entfernt nebenbei den $\log(1/\epsilon)$-Faktor der klassischen Schranke von Dagan–Kur bei konstanter Fehlerwahrscheinlichkeit.
* **Lemma 3.4 (Energie kontrolliert Schaden).** Für einen subnormierten Zustand $\tau$, der im Unterraum $|\bar A - \mathrm{Tr}(A\rho)\mathbb{1}| \geq \xi$ liegt, gilt $\mathrm{Tr}(\tau) \leq 18\,\mathcal{E}[\tau]/\xi^2$ mit der Energie $\mathcal{E}[\tau] = \frac1n\mathrm{Tr}(N\tau)$, $N = \sum_i Q_i$ der Zahloperator der Anregungen.
* **Corollary 4.6 / Lemma 5.3 (Energiezuwachs pro Runde).** Beim logistischen Zwei-Ausgangs-Test wächst die Energie um höchstens $O(\lambda^2/n^2\cdot\mathrm{Tr}(f(\bar A)\tau))$, bei der verrauschten Direktmessung um $O(1/(n^2\epsilon^2))$.
* **Anhang A.** Optimale Threshold Search über informationstheoretische Methoden.

### Methodischer Ansatz

1. **Excitation-Zerlegung.** Mit $P = |\psi\rangle\langle\psi|$ (Purifikation von $\rho$) und $Q = 1-P$ zerlegt sich jeder Vektor auf $n$ Registern orthogonal in $|\phi_S\rangle = \prod_{i\in S}Q_i\prod_{i\notin S}P_i|\phi\rangle$. Für $|\psi\rangle^{\otimes n}$ liegt alle Masse auf $S = \emptyset$; je mehr Masse auf großen $S$, desto beschädigter der Zustand. Die Energie ist die mittlere Anregungszahl, in Boolescher Sprache der totale Einfluss; formal ist die Zerlegung dual zur Quanten-Efron–Stein-Zerlegung (Pelecanos, França, Marwaha, O'Donnell 2025).
2. **Charging.** Ein "problematischer" Zustand, auf dem $\bar A$ um mehr als $\epsilon$ vom wahren Wert abweicht, hat entweder kleine Wahrscheinlichkeit oder hohe Energie (Lemma 3.4). Es genügt also, den erwarteten Energiezuwachs jeder Operation zu kontrollieren.
3. **Viele Observablen (Theorem 1.2).** Schüler–Lehrer-Spiel wie bei Aaronson: Der Schüler läuft MMW, der Lehrer testet, ob die Schätzung $\nu$ nahe ist, mit der Zwei-Ausgangs-Messung $f(\bar A)$, $f$ logistisch mit Steilheit $\lambda$. Bei falscher Schätzung ist das Ergebnis stark verzerrt, also wenig Schaden; die Summe der Energiezuwächse ist die erwartete Fehlerzahl $O(\log d/\epsilon^2)$ mal $\lambda^2/n^2$, und $\lambda = O(n\epsilon^2/\sqrt{\log d})$ plus ein Term $me^{-\Omega(\lambda\epsilon)}$ ergeben $n = \Omega(\log m\sqrt{\log d}/\epsilon^3)$.
4. **Wenige Observablen (Theorem 1.3).** Direkt messen, mit kompakt getragenem Kosinus-Rauschen der Breite $\Theta(\epsilon)$ (statt Gauß-Rauschen, um $\log m$ zu sparen); Energiezuwachs $O(1/(n^2\epsilon^2))$ pro Runde, nach $m$ Runden $m/(n^2\epsilon^2) \lesssim \epsilon^2$ gibt $n = \Omega(\sqrt m/\epsilon^2)$.

### Bedeutung und Anwendungen

* Beendet eine Lücke von zehn Jahren; die Estimating-Tabelle dieses Dokuments hat in der Spalte "Copies" jetzt die klassischen Raten stehen.
* Spezialisiert auf diagonale Matrizen liefert das Argument neue Beweise der klassischen Raten *ohne* Differential Privacy, über Fourier-Analyse auf Produkträumen: Der Efron–Stein-Blick ist auch klassisch neu.
* Für spezielle Observablenklassen bleibt Luft: Für Paulis war vor 2026 nichts Besseres als $1/\epsilon^4$ bekannt, und Chen, Gong, Ye zeigten, dass jede Verbesserung stark verschränkte Messungen braucht.

### Bezug zum eigenen Projekt

* Das Paper liefert die neue Referenzrate für die Spalte "Kopien" bei generischen Listen; der Absatz "What is open (1)" im Estimating-Kapitel war auf $1/\epsilon^4$ formuliert und ist jetzt auf $1/\epsilon^3$ mit der Lyu–Talwar-Evidenz für Optimalität gesetzt.
* Die Energie als Schadensmaß ist ein Kandidat für die Frage, wie viel Phase 2 des eigenen Protokolls die Kopien wirklich verbraucht: Die Probe-Messung auf $\rho\otimes\sigma^*$ ist eine geliftete Observable über zwei Register, und ihre Anregungsbilanz wäre direkt berechenbar.
* Die Bemerkung zu Paulis (kein besseres $\epsilon$ als $1/\epsilon^4$ ohne hohe Verschränkung) ist eine Warnung: Die $O(\log d/\epsilon^4)$ der Konjugatpaar-Magnitudenschätzung sind vermutlich nicht ohne größeren Quantenspeicher zu verbessern; eine empirisch beobachtete $\epsilon^{-3.2}$ wäre dann ein Instanzeneffekt, kein Protokollgewinn.

### Grenzen und offene Fragen

* Erfolgswahrscheinlichkeit $9/10$; die $\delta$-Abhängigkeit ist nicht ausgearbeitet.
* Beide Protokolle brauchen Quantenspeicher $n$ und Messungen im Eigenraum gelifteter Observablen; für Hardware so wenig geeignet wie Aaronsons Original.
* Optimalität: $\Omega(\log m\sqrt{\log d}/(\epsilon^2\log(1/\epsilon)))$ ist bewiesen, $\epsilon^{-3}$ nur für Algorithmen, die auch auf den empirischen Samples genau sind.
* Keine Aussage über Rechenzeit; MMW bleibt.

### Fragen zum Tieferbohren

* Wie sieht die Excitation-Zerlegung für $\rho\otimes\rho^*$ aus, wo die zwei Register verschiedene Zustände tragen, und ist die Bell-Messung eine "geliftete" Observable im Sinne des Papers?
* Kann das Energie-Argument die $1/\epsilon^4$ der Bell-Sampling-Magnitudenschätzung erklären oder verbessern, wenn man Bell-Messungen über mehr als zwei Kopien zulässt?
* Was ist die Efron–Stein-Zerlegung eines Displacement-Operators $D_{q,p}$ auf $n$ Kopien eines Qudits, und wie hängt ihr Grad mit $(q,p)$ zusammen?

Paper: [arXiv:2607.29686](https://arxiv.org/abs/2607.29686)

---
## Predicting Many Properties of a Quantum System from Very Few Measurements (arXiv:2002.08953)

Die Arbeit von **Hsin-Yuan Huang, Richard Kueng und John Preskill** (Caltech, JKU Linz; *Nature Physics* 16, 1050 (2020)) ist das Classical-Shadows-Paper. Sie verbindet Aaronsons Sichtweise (Eigenschaften vorhersagen statt den Zustand rekonstruieren) mit rigorosen Konvergenzgarantien und dem Stabilizer-Formalismus zu einem Protokoll, das mit $O(\log M)$ Einzelkopien-Messungen $M$ lineare Funktionen vorhersagt, unabhängig von der Systemgröße und mit passender informationstheoretischer Untergrenze. Die Zielobservablen dürfen nach der Messung gewählt werden.

### Einordnung in die Tabellen

* **Task type:** Estimating. Gegeben $M$ lineare Funktionen $\mathrm{Tr}(O_i\rho)$, zurück kommen ihre Werte per Median-of-Means. Die Zeilen "Classical shadows, $k$-local Paulis" und, mit Clifford-Ensemble, die Fidelity-Schätzung in der Estimating-Tabelle.
* **Objekt:** gemischter Zustand. **Zugriff:** Sample, Einzelkopien, zufällige Basis pro Kopie (Rung 1 der Zugriffsleiter, die Primitive "single-copy randomized measurements").
* **Status:** 🟢 🟢 🟢 unter dem Versprechen, das die Shadow-Norm ausdrückt: Lokalität $k$ (Pauli-Ensemble, Norm $\leq 4^k\Vert O\Vert_\infty^2$, $3^k$ bei Tensorprodukten) oder beschränkte Hilbert–Schmidt-Norm (Clifford-Ensemble, Norm $\leq 3\,\mathrm{tr}(O^2)$). Globale Paulis kosten $3^n$ bzw. $2^n$: das ist die Lücke, die Zwei-Kopien-Messungen schließen.
* **Versprechen:** kein Versprechen über den Zustand, nur über die Observablen.

### Das Problem

Tomographie skaliert exponentiell in Kopien, Speicher und Rechenzeit. MPS- und Neural-Network-Tomographie helfen nur unter Strukturannahmen. Aaronsons Shadow Tomography ist sample-effizient, braucht aber exponentiell lange Schaltkreise über alle Kopien in Quantenspeicher. Gesucht: ein Protokoll, das ebenso viele Eigenschaften vorhersagt, aber mit Einzelkopien-Messungen, effizienter Nachverarbeitung und beweisbaren Garantien.

### Kernresultate

* **Prozedur.** Pro Kopie: zufälliges $U$ aus dem Ensemble, Rechenbasis-Messung, speichere den Snapshot $\hat\rho = \mathcal{M}^{-1}(U^\dagger|\hat b\rangle\langle\hat b|U)$ mit $\mathbb{E}[\hat\rho] = \rho$. Für $n$-Qubit-Cliffords $\mathcal{M}_n^{-1}(X) = (2^n+1)X - I$, für Tensorprodukte von Ein-Qubit-Cliffords das Tensorprodukt von $\mathcal{M}_1^{-1}(X) = 3X - I$.
* **Theorem 1.** $N = O(\log M\cdot\max_i\Vert O_i\Vert_{\mathrm{shadow}}^2/\epsilon^2)$ Snapshots genügen, um alle $M$ Werte auf $\epsilon$ genau zu treffen; der Beweis läuft über Varianzschranke plus Median-of-Means ($K = 2\log(2M/\delta)$ Gruppen).
* **Theorem 2 (Untergrenze).** Jedes Einzelkopien-Verfahren braucht $\Omega(\log M\cdot\max_i\Vert O_i\Vert_{\mathrm{shadow}}^2/\epsilon^2)$ Messungen, mit der Shadow-Norm als Hilbert–Schmidt-Norm oder als exponentielle Funktion der Lokalität. Beweis über Einbettung in ein Kommunikationsprotokoll.
* **Nichtlineare Funktionen.** $\mathrm{tr}(O\rho\otimes\rho)$ per U-Statistik über Paare unabhängiger Snapshots; Rényi-2-Entropie kleiner Subsysteme, Kosten exponentiell in $|A|$, unabhängig von $n$.
* **Numerik.** Bis 160 Qubits; GHZ-Fidelity mit konstanter Shadow-Größe gegen NNQST, das linear in $n$ wächst und bei Phasenfehlern ($p \to 1$) Fidelity nahe eins meldet, wo sie null ist; Zweipunktfunktionen im 1D-TFIM (50 Sites) und im 2D-Heisenberg-Modell ($8\times 8$); Entanglement-Entropien gegen Brydges et al.; Energievarianz lokaler Hamiltonians.
* **Direct Fidelity Estimation** brauchte im schlimmsten Fall $O(2^n/\epsilon^4)$ Samples; Clifford-Shadows brauchen $O(1/\epsilon^2)$ unabhängig von $n$.

### Methodischer Ansatz

* **Der Messkanal.** $\mathcal{M}(\rho) = \mathbb{E}[U^\dagger|\hat b\rangle\langle\hat b|U]$ ist ein Quantenkanal, invertierbar genau dann, wenn das Ensemble tomographisch vollständig ist; die Inverse ist nicht physikalisch (nicht vollständig positiv), wird aber nur klassisch angewendet.
* **Die Shadow-Norm.** $\Vert O\Vert_{\mathrm{shadow}}^2 = \max_\sigma\mathbb{E}_U\sum_b\langle b|U\sigma U^\dagger|b\rangle\langle b|U\mathcal{M}^{-1}(O)U^\dagger|b\rangle^2$ ist eine Varianzschranke, die nur vom Ensemble und von $O$ abhängt. Für 3-Designs (Cliffords) ergibt sich $3\,\mathrm{tr}(O^2)$; für lokale Paulis faktorisiert sie über die Qubits.
* **Speicher.** Snapshots sind Stabilizerzustände und werden im Tableau gespeichert; für Stabilizer-Observablen (GHZ, toric code) läuft die Auswertung per Gottesman–Knill in $O(n^2)$.

### Bedeutung und Anwendungen

* Das Arbeitspferd der Praxis: NISQ-tauglich, offener Quellcode, Grundlage der randomized-measurement-Toolbox (Elben et al. 2023), der Derandomisierung (Huang, Kueng, Preskill 2021), der fermionischen, lokal verwürfelten, Bell- und symmetrischen Ensembles der folgenden Zusammenfassungen.
* Die Shadow-Norm ist die Sprache, in der alle späteren Ensemble-Papiere ihre Ergebnisse ausdrücken; Theorem 2 sagt, dass die exponentielle Lokalitätsabhängigkeit ein Naturgesetz für Einzelkopien ist, kein Artefakt.
* Der Vergleich mit NNQST ist die erste saubere Gegenüberstellung von beweisbaren und gelernten Decodern auf derselben Aufgabe.

### Bezug zum eigenen Projekt

* Theorem 2 ist die Einzelkopien-Wand, gegen die das Projekt arbeitet: Für Displacement-Operatoren auf einem Qudit ist die Shadow-Norm des verallgemeinerten Clifford-Ensembles $\Omega(d)$ (King, Wan, McClean, Theorem 31), also $\Omega(d/\epsilon^2)$ Kopien für alle $d^2$ Amplituden. Die Konjugatpaar-Messung ist der Ausweg, und dieses Paper liefert die Referenz, gegen die der Vorteil gemessen wird.
* Median-of-Means ist der Schätzer, den auch Phase 1 benutzt; die Konstanten dieses Papers sind konservativ (Fu et al. 2024).
* Die Numerik ist ein Vorbild für die Instanzenleiter: dieselben Modelle (TFIM, Heisenberg), dieselben Observablen (Zweipunktfunktionen), dieselbe Gegenüberstellung mit einem gelernten Modell.

### Grenzen und offene Fragen

* Globale Observablen: Pauli-Strings der Länge $n$ kosten $3^n$ Shadows, eine direkte Messung $1/\epsilon^2$; die Autoren nennen es selbst das "non-example".
* Für nichtlineare Funktionen gibt es keine Untergrenze.
* $n$-Qubit-Cliffords brauchen $n^2/\log n$ verschränkende Gatter; Shallow Shadows (Bertoni et al., Hu–Choi–You, Ippoliti) sind die Antwort.
* Rauschen: robuste Varianten (Chen, Yu, Zeng, Flammia 2021; Koh, Grewal 2022) kamen später.

### Fragen zum Tieferbohren

* Wie sieht die Shadow-Norm des verallgemeinerten Qudit-Clifford-Ensembles für $D_{q,p}$ konkret aus, und warum trägt sie den Faktor $d$ (Vergleich mit Theorem 31 bei King, Wan, McClean und mit Mao, Yi, Zhu)?
* Kann die U-Statistik-Konstruktion für $\mathrm{tr}(O\rho\otimes\rho)$ die Bell-Messung auf $\rho\otimes\rho$ *simulieren*, und was kostet die Simulation im Vergleich zur echten Zwei-Kopien-Messung?
* Was genau bricht bei NNQST im Fall $p = 1$, und welche Zertifikatsgröße würde einen gelernten Decoder vor demselben Fehler bewahren?

Paper: [arXiv:2002.08953](https://arxiv.org/abs/2002.08953)

---

## Experimental quantum state measurement with classical shadows (arXiv:2106.10190)

Die Arbeit von **Ting Zhang, Jinzhao Sun, Xiao-Xu Fang, Xiao-Ming Zhang, Xiao Yuan und He Lu** (Shandong, Peking, Oxford, Hongkong; *Phys. Rev. Lett.* 127, 200501 (2021)) prüft die Classical-Shadows-Familie auf einem photonischen Vier-Qubit-Prozessor unter realistischen Bedingungen: endliche Messzahlen, verrauschte Operationen. Verglichen werden uniforme, lokal verzerrte und derandomisierte Shadows mit Importance Sampling und Observablen-Gruppierung, für lineare Observablen, Hamilton-Momente und nichtlineare Größen wie Purities und PT-Momente.

### Einordnung in die Tabellen

* **Task type:** Estimating. Gegeben Listen lokaler Paulis, ein Hamiltonian, Subsystem-Purities und Momente der partiellen Transposition; zurück kommen die Werte. Neue Zeile "Classical shadows in hardware" der Estimating-Tabelle.
* **Objekt:** ein präparierter Vier-Qubit-GHZ-Zustand mit Fidelity $0.9546 \pm 0.0006$ (per QST). **Zugriff:** Sample, Einzelkopien, lokale Cliffords über Wellenplatten.
* **Status:** 🟢 🟢 🟢 bei $n = 4$; die Frage des Papers ist nicht Skalierung, sondern Konstanten und Rauschen.
* **Versprechen:** Lokalität der Observablen ($\leq 2$-lokale Paulis); die derandomisierte Variante nutzt zusätzlich die Kenntnis der Liste.

### Das Problem

Ein Molekül-Hamiltonian mit $M$ Moden hat $O(M^4)$ Terme, naive Messung kostet $O(M^8/\epsilon^2)$ Shots. Fortgeschrittene Messstrategien (Importance Sampling, Gruppierung, Shadows) sind theoretisch verstanden, aber ihre Praxistauglichkeit und ihr Verhalten unter Hardware-Rauschen waren unerprobt. Die Autoren bauen den einheitlichen Rahmen von Wu et al. nach, in dem alle Strategien Spezialfälle einer Verteilung $K(\mathcal{P})$ über Messbasen mit einer Gewichtsfunktion $f$ sind.

### Kernresultate

* **Aufbau.** Polarisationsverschränkte Photonenpaare aus einem Sagnac-Interferometer, per Beam Displacer zu einem Hyper-Verschränkungszustand $|GHZ_4\rangle = (|HhHh\rangle + |VvVv\rangle)/\sqrt2$ in Polarisation und Pfad erweitert; Pauli-Messungen und Ein-Qubit-Cliffords aus HWP/QWP-Sätzen; fünf Koinzidenzen pro Messbasis.
* **Lineare Observablen.** 50 zufällige $\leq 2$-lokale Paulis; der Maximalfehler fällt mit $N_s$ und liegt bei $N_s = 2000$ unter $0.1$ für alle Verfahren außer $\ell_1$-Sampling; bei fester $N_s$ und wachsender Observablenzahl ist derandomisiertes Shadowing am genauesten.
* **Hamiltonian.** $H = J\sum_i(Z_iZ_{i+1} + X_iY_{i+1} + Y_iZ_{i+1} + X_iZ_{i+1}) + h\sum_i X_i$ mit $J = h = 1/4$: Für $\langle H\rangle$ sind LDF-Gruppierung und derandomisierte Shadows gleichauf, für $\langle H^2\rangle$ mit vielen Termen großen Trägers sind derandomisierte Shadows deutlich besser.
* **Nichtlineare Größen.** Mit $N_s = 1000$ Shadows: Subsystem-Purities $P_A$ für alle Teilmengen per U-Statistik über Paare; $P_A < P_{AB}$ für alle $A$ zertifiziert echte Mehrteilchen-Verschränkung. PT-Momente $p_n = \mathrm{Tr}[(\rho^{T_A})^n]$ per U-Statistik über $n$-Tupel; $p_2^2 > p_3$ (Verletzung der $p_3$-PPT-Bedingung) zeigt bipartite Verschränkung auch für gemischte Zustände.
* **Fehlerskalierung.** Der Fehler von Purity und $p_2$ fällt für kleine $N_s$ wie $1/N_s$, schneller als die asymptotische $1/\sqrt{N_s}$.

### Methodischer Ansatz

* Einheitlicher Schätzer $\hat o(\mathcal{P}) = \sum_l\alpha_l f(\mathcal{P}, O_l, K)\mu(\mathcal{P}, \mathrm{supp}(O_l))$ mit Ein-Shot-Ausgängen $\mu$; die Verfahren unterscheiden sich nur in $K$ und $f$: $\ell_1$-Sampling ($K \propto|\alpha_l|$), LDF-Gruppierung (kompatible Terme in Gruppen), uniforme Shadows ($K = 3^{-n}$), lokal verzerrte Shadows (Produktverteilung), derandomisierte Shadows (greedy gewählte Basen).
* Shadows: $\hat\rho = \bigotimes_i(3U_i|b_i\rangle\langle b_i|U_i - I)$; Subsystem-Schätzer durch Einschränken des Index.
* Vergleich gegen QST als Referenz, 20 bzw. 10 Wiederholungen für Fehlerbalken.

### Bedeutung und Anwendungen

* Erste Gegenüberstellung aller aktuellen Messstrategien auf derselben Hardware; die Aussage "derandomisierte Shadows gewinnen bei vielen großen Termen" ist seither Praxiswissen für VQE-artige Anwendungen.
* Zeigt, dass Shadows nichtlineare Größen (Verschränkungsnachweise) auf echten Daten liefern, ohne Tomographie.
* Vorläuferexperimente: Struchalin et al. (optisch, uniforme Stabilizer-Messungen), Elben et al. (Ionenfallen-Daten für Verschränkungsdetektion).

### Bezug zum eigenen Projekt

* Der Faktor "Hardware-Realismus" der eigenen Taxonomie hat hier einen Datenpunkt: Bei vier Qubits und $10^3$ bis $2\cdot 10^3$ Shots liegen alle Verfahren im Fehlerbereich $10^{-1}$, und Rauschen verschiebt die Rangfolge nicht.
* Die U-Statistik-Schätzer für $p_2$ und $p_3$ sind die Einzelkopien-Simulation von Zwei- und Drei-Kopien-Observablen; der Vergleich mit einer echten Bell-Messung auf $\rho\otimes\rho$, die $\mathrm{tr}(\rho^2)$ direkt liefert, wäre das Experiment, das die Speicherachse in Hardware sichtbar macht.
* Die Feststellung, dass das Ensemble (uniform, verzerrt, derandomisiert) die Genauigkeit bei fester Shot-Zahl bestimmt, ist das Einzelkopien-Analogon der Frage, welche Zwei-Kopien-Basis (Bell auf $\rho\otimes\rho$ oder auf $\rho\otimes\rho^*$) das Spektrum am besten sichtbar macht.

### Grenzen und offene Fragen

* Vier Qubits, ein Zustand; keine Aussage über Skalierung.
* Keine Fehlerminderung; die Autoren nennen die Kombination von Shadows mit Error Mitigation als nächsten Schritt.
* Die derandomisierte Variante braucht die Observablenliste vorab und gibt damit die "measure first, ask later"-Eigenschaft auf.
* Die $1/N_s$-Skalierung bei kleinen $N_s$ ist beobachtet, nicht erklärt.

### Fragen zum Tieferbohren

* Wie viele Koinzidenzen pro Basis sind optimal, wenn die Basiswahl selbst Zeit kostet, und wie ändert das die effektive Sample-Komplexität?
* Lässt sich das $p_3$-PPT-Kriterium aus einem Bell-Record auf $\rho\otimes\rho^*$ ablesen, und was ist die Zwei-Kopien-Entsprechung der PT-Momente?
* Welche Rauschmodelle (Dephasierung in Polarisation gegen Pfad) erklären die Rangfolge der Verfahren, und ändert Randomized Compiling sie?

Paper: [arXiv:2106.10190](https://arxiv.org/abs/2106.10190)

---

## Classical Shadows with Improved Median-of-Means Estimation (arXiv:2412.03381)

Die Arbeit von **Winston Fu, Dax Enshan Koh, Siong Thye Goh und Jian Feng Kong** (A*STAR, SUTD, SMU Singapur; 2024) betrifft die Nachverarbeitung: Huang, Kueng und Preskill haben in ihrer Median-of-Means-Analyse großzügige Konstanten gewählt, und in der Praxis entscheiden Konstanten über Shot-Zahlen. Die Autoren übertragen Minskers optimale Konstanten und seinen permutationsinvarianten Schätzer (eine U-Statistik über Gruppenmittel) auf Classical Shadows, implementieren zwei unvollständige U-Statistik-Varianten und vergleichen numerisch auf einer Ising-Kette und auf GHZ-Zuständen.

### Einordnung in die Tabellen

* **Task type:** Estimating, unverändert; das Paper ändert nur den Schätzer, nicht die Messung. In der Estimating-Tabelle als Zeile "Median-of-means constants" neben den Classical-Shadows-Zeilen.
* **Objekt:** Zustand. **Zugriff:** Sample, Einzelkopien; Pauli- oder Clifford-Messungen.
* **Status:** 🟢 🟢 🟢. Die Modifikation kostet Rechenzeit $O(k^l\log k)$ für die vollständige U-Statistik und wird deshalb durch Stichproben (zufällig oder zyklisch) auf $O(m)$ gebracht.
* **Versprechen:** keines.

### Das Problem

Die Median-of-Means-Schranke $\Pr[|\hat\mu - \mu| \geq C\sigma\sqrt{t/N}] \leq 2e^{-t}$ gilt bei Huang et al. mit $C \approx 8$; sie setzen $N = 34\sigma^2 k/\epsilon^2$, $t = k/2$. Minsker zeigte $C = \sqrt\pi + o(1)$ für den gewöhnlichen Median-of-Means und $C = \sqrt2 + o(1)$ für einen modifizierten Schätzer, der den Median über alle $l$-elementigen Teilmengen der Gruppenmittel nimmt. Wie viel bringt das für Shadows, und wie rechnet man den modifizierten Schätzer für große Datensätze aus?

### Kernresultate

* **Theorem 1 (Minsker, angepasst).** $\Pr[|\hat\mu_{\mathrm{MoM}} - \mu| \geq \sigma\sqrt{t/N}] \leq 2\exp(-t/(\pi(1+o(1))))$ für $t$ in einem Fenster $[l_{k,N}, u_{k,N}]$, also $C = \sqrt\pi$; die Momentenbedingung ist bei Quantenmessungen trivial erfüllt. Aus der Union Bound folgt $t = \log(2M/\delta)$ und die Wahl $t = k/\log k$.
* **Theorem 2 (Minsker, U-Statistik).** Für den Median über alle $\binom{n}{l}$ Mittelwerte von $l$ Gruppenmitteln: Schranke $3\exp(-t/(2(1+o(1))))$, also $C = \sqrt2$.
* **Zwei praktische Implementierungen.** MomRand zieht $m$ zufällige Teilmengen; MomCyc benutzt zyklische Permutationen mit Offsets aus einem modifizierten Golomb-Lineal und hat bessere asymptotische relative Effizienz bei gleichem $m$.
* **Benchmarks.** Ising-Kette mit 50 Qubits, Pauli-Messungen (Tensornetze), Zweipunktfunktion: das einfache Mittel ist am genauesten, dann der ursprüngliche MoM; die modifizierten Schätzer überschreiten ihre Schranken bei $3.3\sigma$ und taugen hier nicht. Verrauschter GHZ-Zustand mit Clifford-Messungen, Fidelity: die modifizierten Schätzer sind besser als MoM und folgen den Schranken eng. Purity (quadratisch): das Mittel bleibt vorn.
* **Tabelle I** (Fehler $\epsilon = 0.1$): Shots nach Mean-Schranke $80\cdot 10^6$, HKP-Schranke $1.3\cdot 10^6$, Original-MoM-Schranke $58\cdot 10^3$, neue Schranke $38\cdot 10^3$.
* Die Unabhängigkeit der Shot-Zahl von $n$ (Fidelity von GHZ mit $r = 5, 10, 15, 20$) bleibt für alle Schätzer erhalten.

### Methodischer Ansatz

* Snapshots in $kl$ Gruppen, Gruppenmittel $Z_j$, dann Median über Mittel von $l$-Teilmengen; unvollständige U-Statistiken (Lee) mit Varianzformel $\mathrm{Var}\,U^{(0)} = \sigma_l^2/m + (1-1/m)\mathrm{Var}\,U$ und asymptotischer relativer Effizienz als Auswahlkriterium.
* Bewertung gegen $3.3\sigma$-Grenzen (Ausfallwahrscheinlichkeit $0.1\%$), damit numerische und theoretische Schranken bei $\delta = 10^{-3}$ direkt vergleichbar sind.

### Bedeutung und Anwendungen

* Eine Faktor-1.5-Ersparnis in der Schranke gegenüber Huang et al. und ein Faktor 34 gegenüber der HKP-Zahl, ohne Änderung am Experiment und auch auf existierenden Datensätzen anwendbar.
* Die Botschaft, dass der Schätzer zum Messensemble passen muss (Pauli: MoM oder Mittel; Clifford: modifizierter MoM), ist ein nützlicher Praxishinweis; die Normalität von $\hat o_i(N,1)$ ab $N \geq 1000$ wird bestätigt.

### Bezug zum eigenen Projekt

* Phase 1 des eigenen Protokolls schätzt $|y_{q,p}|^2$ als Mittelwert über den Bell-Record; die Konstanten der Konzentrationsschranke gehen direkt in die Zahl der Bell-Samples ein, und dieses Paper zeigt, wo die Faktoren zwischen Theorie und Praxis liegen.
* Die Beobachtung "Mittel schlägt Median-of-Means in der Praxis" ist ein Argument, empirische Skalierungsexponenten (wie $\epsilon^{-3.2}$ aus der Evaluation von 2025) nicht mit worst-case-Schätzern zu vergleichen.
* Die Wahl des Schätzers ist ein Freiheitsgrad, den ein gelernter Decoder implizit hat; die Frage, ob das CNN einen medianartigen oder mittelwertartigen Schätzer lernt, ist testbar.

### Grenzen und offene Fragen

* Nur zwei Testfälle; keine Theorie, warum die modifizierten Schätzer bei Pauli-Messungen scheitern (Appendix C diskutiert es).
* Die $o(1)$-Terme werden ignoriert; die Fensterbedingungen an $t$ sind asymptotisch.
* Für quadratische Funktionen benutzen Huang et al. Median von U-Statistiken; die Übertragung ist nicht ausgearbeitet.

### Fragen zum Tieferbohren

* Wie sieht die Konzentration der Bell-Record-Statistik aus (Multinomial über $d^2$ Ausgänge), und welche MoM-Variante ist dort optimal?
* Kann ein CNN, das auf verrauschten Bell-Records trainiert wird, die Schätzerwahl implizit an das Rauschmodell anpassen, und wie würde man das nachweisen?
* Wo liegt die Grenze zwischen "Konstanten" und "Exponenten" in der eigenen Skalierungsanalyse, wenn $d$ nur bis $64$ oder $128$ reicht?

Paper: [arXiv:2412.03381](https://arxiv.org/abs/2412.03381)

---

## Classical Shadow Tomography with Locally Scrambled Quantum Dynamics (arXiv:2107.04817)

Die Arbeit von **Hong-Ye Hu, Soonwon Choi und Yi-Zhuang You** (UC San Diego, Harvard, Berkeley, MIT; *Phys. Rev. Research* 5, 023027 (2023)) verallgemeinert Classical Shadows von 2-Design-Ensembles auf beliebige *lokal verwürfelte* Ensembles endlicher Tiefe: Verteilungen $P(U)$, die unter lokalen Basiswechseln invariant sind, $P(U) = P(UV) = P(VU)$ für Produkte $V$. Dann hängt die Rekonstruktionsabbildung nur vom *Entanglement Feature* der Snapshots ab, also von den mittleren Purities in allen Teilregionen, und Shallow Circuits sowie Hamiltonevolutionen realer Simulatoren werden zu Shadow-Ensembles mit einstellbarer Shadow-Norm.

### Einordnung in die Tabellen

* **Task type:** Estimating. Gegeben Fidelities oder Pauli-Observablen, zurück kommen die Werte; die Neuerung ist das Ensemble. Teil der Zeile "Classical shadows, other ensembles" (shallow and locally scrambled).
* **Objekt:** Zustand. **Zugriff:** Sample, Einzelkopien, Evolution unter einem Schaltkreis endlicher Tiefe oder einem lokalen Hamiltonian für endliche Zeit, dann Rechenbasis-Messung.
* **Status:** 🟢 🟢 🟢 mit Einschränkung: Es gibt $2^N$ Rekonstruktionskoeffizienten $r_A$; sie werden einmal aus dem Entanglement Feature berechnet, was für eindimensionale Systeme mit Entanglement-Feature-Dynamik effizient geht und allgemein exponentiell ist.
* **Versprechen:** lokale Verwürfelung; approximative Verwürfelung mit kontrollierbarem Bias über das lokale Frame-Potential.

### Das Problem

Die beiden Grenzfälle von Huang, Kueng und Preskill, globale Cliffords für niedrigen Rang und lokale Cliffords für lokale Observablen, sind nicht interpolierbar, und zufällige Schaltkreise sind auf Ionenfallen- und Rydberg-Simulatoren schwer zu realisieren, während eine feste verschränkende Dynamik leicht ist. Gesucht: Shadows für die Dynamik, die die Hardware hergibt, mit Rekonstruktion und Sample-Komplexität, die nicht von den Details der Dynamik abhängen.

### Kernresultate

* **Rekonstruktionsabbildung (Gl. 7, 9, 12).** Für lokal verwürfelte Snapshot-Ensembles gilt $\sigma = \mathcal{M}[\rho] = \sum_{B,C}d^{2N-|B|}\rho_B\,\mathrm{Wg}_{B,C}W^{(2)}_{\mathcal{E}_\sigma,C}$ mit Weingarten-Funktion $\mathrm{Wg}$ und dem zweiten Entanglement Feature $W^{(2)}_{C} = \mathbb{E}\,e^{-S^{(2)}_C(\hat\sigma)}$; die Inverse ist $\rho = d^N\sum_A r_A\sigma_A$ mit Koeffizienten $r_A$ aus einem linearen Gleichungssystem mit universellen Fusionskoeffizienten. Für on-site 2-Designs kommt $\bigotimes((d+1)\sigma_i - 1)$ heraus, für globale 2-Designs $(d^2+1)\sigma - 1$.
* **Sample-Komplexität (Gl. 15–23).** Die zustandsabhängige Shadow-Norm $\Vert O\Vert^2_{\mathcal{E}_\sigma|\rho}$ wird durch das dritte Entanglement Feature und Weingarten-Funktionen über $S_3^N$ ausgedrückt; die über lokale Basiswechsel gemittelte Norm $\Vert O\Vert^2_{\mathcal{E}_\sigma}$ hängt nur von den Entanglement Features von Ensemble und Observable ab.
* **Zwei-Qudit-Modell.** Mit mittlerer Ein-Qudit-Purity $w$ zwischen $1$ (Produktzustand) und $2d/(d^2+1)$ (Page) interpolieren $r_A$ und Shadow-Norm analytisch zwischen den beiden Grenzfällen; bei kurzer Zeit sind lokale Observablen billiger, bei langer Zeit sind alle gleich teuer.
* **Numerik.** Schaltkreise endlicher Tiefe und Hamiltonevolutionen einer Spinkette nach dem Vorbild von Ionenfallen und Rydberg-Arrays; die Shallow-Circuit-Messung erreicht für Fidelity- und Pauli-Aufgaben geringere Tomographie-Komplexität als Pauli- oder Clifford-Messungen; ein einziger Hamiltonian genügt für approximative Tomographie, der Bias fällt schnell auf ein kleines Plateau.

### Methodischer Ansatz

* Einfügen und Mitteln lokaler 2-Design-Basiswechsel $V$ in $\sigma = \mathbb{E}\,V^\dagger\hat\sigma V\,\mathrm{Tr}(V^\dagger\hat\sigma V\rho)d^N$ erlaubt die Weingarten-Rechnung, ohne die Dynamik zu kennen; nur Purities bleiben übrig.
* Das Entanglement Feature wird entweder aus der Definition durch Sampling des Prior-Ensembles berechnet oder für unbekannte experimentelle Ensembles aus Rényi-Entropie-Messungen geschätzt; für 1D gibt es effiziente Entanglement-Feature-Dynamik.
* Das lokale Frame-Potential quantifiziert die Abweichung von exakter Verwürfelung und damit den Bias.

### Bedeutung und Anwendungen

* Öffnet Shadows für analoge Simulatoren; parallel und unabhängig entstanden Shallow Shadows (Bertoni et al.), die Einordnung über Entanglement Features ist die allgemeinere.
* Die Aussage, dass die Rekonstruktionsabbildung nur von Purities abhängt, ist ein Strukturresultat über Messkanäle mit lokaler Symmetrie; Ippoliti benutzt sie für Bell- und GHZ-Basen.
* Der Zusammenhang Shadow-Norm $\leftrightarrow$ Entanglement Feature macht die Ensemblewahl zu einem Optimierungsproblem über die Verschränkung der Messbasis.

### Bezug zum eigenen Projekt

* Die Bell-Messung auf zwei Kopien ist eine feste, nicht zufällige Messbasis; das Paper zeigt, wie man eine feste verschränkende Dynamik trotzdem als Shadow-Ensemble behandelt, indem man lokal verwürfelt. Die Frage, ob Bell-Sampling auf $\rho\otimes\rho^*$ mit lokalen Qudit-Cliffords davor ein lokal verwürfeltes Zwei-Kopien-Ensemble wird, ist direkt anschließbar.
* Das Entanglement Feature als einzige relevante Kenngröße ist ein Kandidat für den Faktor "Mixedness/Verschränkung" der eigenen Taxonomie: Es ist messbar und bestimmt die Kosten.
* Die $2^N$ Koeffizienten $r_A$ sind ein Beispiel für "Speicher exponentiell, aber einmalig"; das eigene Coprime-Folding hat dieselbe Struktur, nur mit $d^2 \to 64\times 64$.

### Grenzen und offene Fragen

* $2^N$ Rekonstruktionskoeffizienten im Allgemeinen; effizient nur mit Zusatzstruktur.
* Der Bias approximativ verwürfelter Ensembles ist numerisch, nicht rigoros kontrolliert.
* Keine Untergrenzen; ob Shallow-Ensembles für eine Observablenklasse optimal sind, ist offen.
* Qudits sind formal enthalten, Beispiele nur für Qubits.

### Fragen zum Tieferbohren

* Wie sieht das Entanglement Feature der transversalen Bell-Basis auf $\rho\otimes\rho^*$ aus, wenn man beide Kopien als ein $2$-Qudit-System liest?
* Kann die Weingarten-Rechnung für $U(d)^N$-Twirls auf die Heisenberg–Weyl-Gruppe eines einzelnen Qudits übertragen werden, wo es kein $N$ gibt?
* Wie hängt die Shadow-Norm eines Displacement-Operators $D_{q,p}$ von der Zeit einer Hamiltonevolution ab, die vor der Messung läuft?

Paper: [arXiv:2107.04817](https://arxiv.org/abs/2107.04817)

---

## Classical shadows based on locally-entangled measurements (arXiv:2305.10723)

Die Arbeit von **Matteo Ippoliti** (UT Austin, Stanford; *Quantum* 2024) verschiebt die Verschränkung von den Kopien in die Messbasis: Statt jedes Qubit einzeln in einer zufälligen Pauli-Basis zu messen, werden Paare benachbarter Qubits *innerhalb einer Kopie* in der Bell-Basis gemessen. Für Pauli-Operatoren, die zur Dimer-Überdeckung passen, sinkt die Shadow-Norm quadratisch von $3^k$ auf $3^{k/2}$; andere Operatoren werden unlernbar. Eine Familie zwischen Pauli- und Bell-Basen ist tomographisch vollständig und behält einen Teil des Gewinns, und $n$-Qubit-GHZ-Basen erreichen $(3/2)^k$, optimal unter Stabilizer-Messungen.

### Einordnung in die Tabellen

* **Task type:** Estimating. Gegeben eine Liste von Paulis, zurück kommen ihre Werte; das Paper handelt von der Messbasis. Neue Zeile "Classical shadows, locally entangled bases" der Estimating-Tabelle.
* **Objekt:** Zustand. **Zugriff:** Sample, Einzelkopien. Wichtig für die Tabellen: Die Bell-Messung hier ist *nicht* die Zwei-Kopien-Bell-Messung der Speicherachse, sondern eine Zwei-Qubit-Messung auf einer Kopie; Quantenspeicher bleibt eins.
* **Status:** 🟢 🟢 🟢 für kompatible Operatoren; Nachverarbeitung ist ein Produkt über Dimere.
* **Versprechen:** Kompatibilität mit der gewählten Dimer-Überdeckung: Der Träger schneidet jedes Dimer in $0$ oder $2$ Sites. Das ist ein Versprechen über die Observablen, nicht über den Zustand.

### Das Problem

Zufällige Pauli-Messungen kosten $3^k$ Shots für Gewicht $k$, und das ist informationstheoretisch optimal *im Allgemeinen*. Man kann aber Genauigkeit auf einer Operatorklasse gegen Unlernbarkeit auf einer anderen tauschen; Shallow Shadows tun das über Schaltkreistiefe mit $\sim k2^k$ für zusammenhängende Träger. Gibt es einen hardware-schonenderen Tausch mit nur Zwei-Qubit-Verschränkung?

### Kernresultate

* **Bell-Shadows (Abschnitt 2).** Lokal verwürfeln, Paare in der Bell-Basis messen, Standardrekonstruktion. Der Messkanal faktorisiert in Zwei-Qubit-Kanäle mit Eigenwerten $\lambda_{\circ\circ} = 1$, $\lambda_{\circ\bullet} = \lambda_{\bullet\circ} = 0$, $\lambda_{\bullet\bullet} = 1/3$; also $\Vert P\Vert_{\mathrm{sh}}^2 = 3^{k/2}$ für kompatible $P$ und Nullen sonst (nicht tomographisch vollständig). Es genügt, ein Qubit pro Dimer zu verwürfeln (Gate-Teleportation). $10^{N/2}$ von $4^N$ Operatoren sind kompatibel.
* **Anwendungsfälle (2.3).** Stringoperatoren gerader Länge in 1D mit zwei Dimer-Überdeckungen: $2\ln(M/2)3^{k/2}/\epsilon^2$ statt $\ln M\,3^k/\epsilon^2$; hexagonale Plaquetten (Color-Code-Stabilisatoren): Vorfaktor $54$ statt $729$; $p$-Punkt-Funktionen von Zwei-Körper-Termen: $3^p$ statt $9^p$.
* **Allgemeine Zwei-Qubit-Basen (Abschnitt 3).** Mit CPhase($\phi$) statt CZ wird der Kanal über $\delta = \ln 2 - S_2^a$ deformiert: $\lambda_{\bullet\circ} \simeq \delta/3$, $\lambda_{\bullet\bullet} \simeq 1/(3+2\delta)$, tomographisch vollständig für $\delta > 0$, Shadow-Norm $\simeq(3+2\delta)^{|A|/2}(\sqrt3/\delta)^{c_A}$ mit $c_A$ der Zahl geschnittener Dimere. Bei $\delta = \ln(11/8)$ ist $\Vert P\Vert^2_{\mathrm{sh}} = 4^{k\bmod 2}\cdot 2^k$ und schlägt Shallow Shadows ($k2^k$) ab $k \gtrsim 4$. Für Träger mit "Löchern" der Dichte $\rho$ hilft Verschränkung oberhalb einer Schwelle $\rho^*(\delta)$, gegen Shallow Shadows ab $\rho^* \gtrsim 0.945$.
* **GHZ-Basen (Abschnitt 4).** $n$-Qubit-GHZ-Basen sind optimal unter Stabilizer-Messungen für kompatible Operatoren: $\Vert P\Vert^2_{\mathrm{sh}} = f_n^k$ mit $f_2 = \sqrt3$, $f_3 = 3/2^{2/3}$, $f_n \to 3/2$; die Schranke $(3/2)^k$ folgt daraus, dass eine Basis höchstens $2^n$ der $3^n$ Operatoren vollen Gewichts trifft; GHZ maximiert die Zahl voll getragener Stabilisatoren (Shor–Laflamme-Gewichtsverteilung).

### Methodischer Ansatz

* Lokale Verwürfelung macht den Kanal Pauli-diagonal; die Eigenwerte folgen aus dem Entanglement Feature der Messbasis (Hu, Choi, You; Bertoni et al.): $\lambda_A = (-1/3)^{|A|}\sum_{B\subseteq A}(-2)^{|B|}P^B$ mit $P^B$ der mittleren Subsystem-Purity der Basiszustände.
* Basis-Zählargument: Pro Dimer werden $3$ von $9$ Zwei-Qubit-Operatoren gemessen (zwei explizit, der dritte als Produkt), also Trefferwahrscheinlichkeit $3^{-k/2}$.
* Für typische Operatoren mit Löchern wird die geometrische Mittelung $e^{\mathbb{E}\ln\Vert P\Vert^2}$ verwendet, weil die Shadow-Norm über Größenordnungen schwankt.

### Bedeutung und Anwendungen

* Ein hardware-billiger Ersatz für Shallow Shadows bei Stringoperatoren, Plaquetten und Korrelationsfunktionen; Tabelle 1 des Papers ordnet Pauli-, Bell-, deformierte und GHZ-Shadows nach Skalierung und Lernbarkeit.
* Zeigt, dass "Bell-Messung" zwei ganz verschiedene Dinge bedeuten kann: über zwei Kopien (Speicherachse) oder über zwei Qubits einer Kopie (Basiswahl). Nur die erste sieht das Pauli-Spektrum global.

### Bezug zum eigenen Projekt

* Die begriffliche Klärung ist für das eigene Paper wichtig: Bell-Messungen *innerhalb* einer Kopie liefern $3^{k/2}$ und bleiben an der Einzelkopien-Wand von Theorem 2 bei Huang et al.; Bell-Messungen *über* $\rho\otimes\rho^*$ liefern $O(\log d/\epsilon^4)$ für alle $d^2$ Amplituden. Die Ressource ist der zweite Zustand, nicht das verschränkende Gatter.
* Die Idee "Genauigkeit auf einer Klasse gegen Unlernbarkeit auf einer anderen tauschen" ist eine Vorlage für Messbasen, die auf eine Promise-Klasse zugeschnitten sind; ein Dictionary-Regime könnte eine Basis wählen, die nur die Dictionary-Adressen sieht.
* Die Schranke $(3/2)^k$ über "höchstens $2^n$ von $3^n$ Operatoren pro Basis" ist ein Zählargument, das sich auf die $d^2$ Displacement-Adressen eines Qudits übertragen ließe.

### Grenzen und offene Fragen

* Bell-Shadows sind tomographisch unvollständig; die deformierte Familie zahlt mit schlechterer Asymptotik.
* GHZ-Basen brauchen Tiefe linear in $n$ oder viele Hilfsqubits; Verhalten unter Rauschen offen.
* Nur Pauli-Observablen; die Übertragung auf Nicht-Pauli-Observablen ist nicht ausgeführt.
* Qudits nicht behandelt.

### Fragen zum Tieferbohren

* Was ist die Qudit-Version: Messung in der Basis der gemeinsamen Eigenvektoren von $X\otimes X^\dagger$ und $Z\otimes Z^\dagger$ auf zwei Qudits einer Kopie, und welche Displacement-Operatoren sind dann "kompatibel"?
* Wie verhält sich die Shadow-Norm der deformierten Basis, wenn man sie auf $\rho\otimes\rho^*$ anwendet und die Dimere über die Kopien legt?
* Ist die Shor–Laflamme-Optimalität von GHZ ein Spezialfall einer Aussage über maximale Träger in einer Nebenklasse, die auch für Stabilizer-Träger im Displacement-Spektrum gilt?

Paper: [arXiv:2305.10723](https://arxiv.org/abs/2305.10723)

---
## Matchgate Shadows for Fermionic Quantum Simulation (arXiv:2207.13723)

Die Arbeit von **Kianna Wan, William J. Huggins, Joonho Lee und Ryan Babbush** (Google Quantum AI, Stanford, Columbia, Harvard; *Commun. Math. Phys.* 404, 629 (2023)) analysiert Classical Shadows aus zufälligen Matchgate-Schaltkreisen, also fermionischen Gauß-Unitaries. Hauptsatz: Die ersten drei Momente der Haar-Verteilung auf der kontinuierlichen Matchgate-Gruppe $\cong O(2n)$ stimmen mit denen der diskreten Untergruppe der Clifford-Matchgates (signierte Permutationen) überein, ein "Matchgate-3-Design". Daraus folgen effiziente Schätzer für lokale fermionische Observablen, Fidelities mit Gauß-Zuständen und Überlappe mit Slater-Determinanten, was den exponentiellen Nachverarbeitungsschritt im hybriden QC-AFQMC-Algorithmus beseitigt.

### Einordnung in die Tabellen

* **Task type:** Estimating. Gegeben lokale fermionische Operatoren $\gamma_S$, Gauß-Dichteoperatoren $\varrho$, Slater-Determinanten $|\varphi\rangle$; zurück kommen $\mathrm{tr}(\gamma_S\rho)$, $\mathrm{tr}(\varrho\rho)$, $\langle\psi|\varphi\rangle$. Zeile "Classical shadows, other ensembles (fermionic and matchgate)".
* **Objekt:** Zustand eines $n$-Moden-Fermionensystems, per Jordan–Wigner als $n$ Qubits. **Zugriff:** Sample, Einzelkopien, zufälliger Matchgate-Schaltkreis, Rechenbasis-Messung.
* **Status:** 🟢 🟢 🟢. Varianz $\sim n^{|S|/2}$ für lokale Observablen, konstant bzw. sublinear wachsend für Gauß-Fidelities und Überlappe; Nachverarbeitung in $O(n^3)$ über Pfaffians.
* **Versprechen:** Parität: der Messkanal hat Bild $\Gamma_{\mathrm{even}}$, also müssen Zustand oder Observablen gerade Operatoren sein. Das ist physikalisch fast immer gegeben.

### Das Problem

Huggins et al. hatten QC-AFQMC mit Clifford-Shadows implementiert: Der Trial-Zustand wird auf dem Quantencomputer präpariert, Shadows werden gesammelt, und die Überlappe $\langle\Psi_{\mathrm{trial}}|\varphi_i\rangle$ mit den Slater-Determinanten des Monte-Carlo-Laufs werden klassisch ausgewertet. Die Varianz ist konstant, aber die Auswertung $\langle b|U|\varphi_i\rangle$ mit Clifford-$U$ braucht exponentiell kleine Genauigkeit und skaliert exponentiell. Gesucht: ein Ensemble, dessen Shadows fermionische Größen effizient und mit polynomieller Varianz liefern.

### Kernresultate

* **Theorem 1 (drei Momente).** $\mathcal{E}^{(j)}_{M_n} = \mathcal{E}^{(j)}_{M_n\cap\mathrm{Cl}_n}$ für $j = 1, 2, 3$, mit expliziten Ausdrücken über Projektoren $|\Upsilon^{(2)}_k\rangle\!\rangle$ und $|\Upsilon^{(3)}_{k_1k_2k_3}\rangle\!\rangle$ in Liouville-Darstellung. Corollary 1: die Clifford-Matchgates bilden ein Matchgate-3-Design. Die Matchgate-Gruppe hat $2n+1$ inäquivalente Irreps, gegenüber einer nichttrivialen bei der Clifford-Gruppe.
* **Messkanal (Gl. 30, 32).** $\mathcal{M} = \sum_\ell\binom{n}{\ell}\binom{2n}{2\ell}^{-1}\mathcal{P}_{2\ell}$ mit $\mathcal{P}_k$ dem Projektor auf Produkte von $k$ Majoranas; Inverse durch Kehrwerte der Koeffizienten auf $\Gamma_{\mathrm{even}}$.
* **Varianz (Gl. 33–36).** Explizite Formel mit Koeffizienten $\alpha_{\ell_1\ell_2\ell_3}$; dank der Symmetrie darf die Majorana-Basis frei gewählt werden.
* **Lokale fermionische Observablen.** $\mathrm{tr}(\tilde\gamma_S\mathcal{M}^{-1}(U_Q^\dagger|b\rangle\langle b|U_Q)) = \binom{2n}{|S|}\binom{n}{|S|/2}^{-1}\mathrm{pf}(i(Q'Q^TC_{|b\rangle}QQ'^T)|_S)$, Varianz $\leq\binom{2n}{|S|}\binom{n}{|S|/2}^{-1}\sim n^{|S|/2}$; dieselbe Skalierung wie Zhao, Rubin, Miyake, aber in beliebiger Basis.
* **Theorem 2 (Gauß-Dichteoperatoren).** $\mathrm{tr}(\varrho_1\mathcal{P}_{2\ell}(\varrho_2))$ ist der Koeffizient von $z^\ell$ in $2^{-n}\mathrm{pf}(C_{\varrho_1})\mathrm{pf}(-C_{\varrho_1}^{-1} + zC_{\varrho_2})$; alle Koeffizienten in $O(n^3)$ (Anhang D). Varianz polynomiell beschränkt; für Gauß-Dichteoperatoren $O(\sqrt n\log n)$ (Anhang F).
* **Überlappe mit Slater-Determinanten.** Über $\rho = \frac12(|0\rangle + |\psi\rangle)(\langle 0| + \langle\psi|)$ und $\langle\psi|\varphi\rangle = 2\,\mathrm{tr}(|\varphi\rangle\langle 0|\rho)$; effizient berechenbare Varianzschranke, ausgewertet bis 1000 Qubits mit sublinearem Wachstum. Algorithmus 1 fasst das QC-AFQMC-Protokoll zusammen.
* **Allgemeiner Rahmen** für Produkte lokaler fermionischer Operatoren, Gauß-Dichteoperatoren und Gauß-Unitaries, inklusive Überlappe mit beliebigen reinen Gauß-Zuständen, ohne Varianzschranke.

### Methodischer Ansatz

* Explizite Twirl-Kanäle über die Darstellungstheorie von $O(2n)$ auf der Clifford-Algebra der Majoranas; die Gleichheit der Momente für die diskrete Untergruppe wird durch direkten Vergleich der Ausdrücke gezeigt.
* Pfaffian-Identitäten aus Wicks Theorem; für Theorem 2 ein elementarer Zugang über die Clifford-Algebra-Struktur, der sich auf den Überlapp-Fall erweitern lässt, wo Summationsformeln fehlen.
* Sampling der Ensembles in Anhang B; $n^2/\log n$-Gatter-Frage der Cliffords entfällt, Matchgates sind lineare Optik auf Fermionen.

### Bedeutung und Anwendungen

* Macht QC-AFQMC polynomiell in der Nachverarbeitung; die Autoren erweitern die Reichweite von Shadows auf globale fermionische Größen, die weder lokal noch niedrigrangig im Qubit-Sinn sind.
* Das Matchgate-3-Design ist ein Strukturresultat mit Anwendungen jenseits von Shadows; Heyraud, Chomet und Tilly verallgemeinern es auf $SO(2n)$ und vereinheitlichen alle Matchgate-Ensembles.
* Für $k$-Körper-Fermionen mit Einzelkopien ist $\Omega(n^k/\epsilon^2)$ nötig (King, Gosset, Kothari, Babbush, Theorem 3); Matchgate-Shadows erreichen das bis auf Logarithmen und sind damit die Einzelkopien-Referenz für die fermionische Zwei-Kopien-Zeile.

### Bezug zum eigenen Projekt

* Die Gauß-Unitaries sind das fermionische Gegenstück zu den Displacement-Operatoren: eine Gruppe mit expliziter Darstellungstheorie, deren Twirls sich geschlossen berechnen lassen. Das Paper ist die Vorlage dafür, wie man eine Shadow-Norm für eine strukturierte Operatorgruppe *ausrechnet*, statt sie zu schätzen.
* Die Varianz $n^{|S|/2}$ ist eine "Lokalität in der Majorana-Basis", die sich von der Pauli-Lokalität unterscheidet; das ist das Beispiel dafür, dass der Begriff "lokal" von der Basis abhängt, in der das Spektrum gelesen wird, genau wie bei Heisenberg–Weyl gegen Pauli.
* Der Trick, Überlappe über den Zustand $\frac12(|0\rangle + |\psi\rangle)(\dots)$ als Erwartungswerte zu schreiben, ist eine Einzelkopien-Umgehung des Hadamard-Tests und damit ein Vorbild für Phase 2, wo Vorzeichen über Erwartungswerte auf $\rho\otimes\sigma^*$ statt über kontrollierte Operationen gewonnen werden.

### Grenzen und offene Fragen

* Für den allgemeinen Rahmen (Produkte von Gauß-Objekten) fehlen Varianzschranken.
* Die Überlapp-Varianz ist nur numerisch bis 1000 Qubits kontrolliert; ein analytisches $O(\mathrm{poly}(n))$ fehlt.
* Nur gerade Operatoren; ungerade Sektoren brauchen Zusatzkonstruktionen (Anhang A).
* Rauschrobustheit nicht behandelt.

### Fragen zum Tieferbohren

* Warum hat die Matchgate-Gruppe $2n+1$ Irreps auf $L(\mathcal{H}_n)$, und welche Struktur hat die Heisenberg–Weyl-Gruppe eines Qudits im Vergleich?
* Lässt sich Theorem 2 (Polynom in $z$ aus zwei Pfaffians) auf Überlappe zwischen Gauß-Zuständen in der Displacement-Darstellung übertragen, wo Kovarianzmatrizen durch charakteristische Funktionen ersetzt werden?
* Was ist der Zwei-Kopien-Matchgate-Shadow: Bell-Messung auf $\rho\otimes\rho$ in der Majorana-Basis, und sieht sie das ganze fermionische Spektrum?

Paper: [arXiv:2207.13723](https://arxiv.org/abs/2207.13723)

---

## Unified Framework for Matchgate Classical Shadows (arXiv:2409.03836)

Die Arbeit von **Valentin Heyraud, Héloise Chomet und Jules Tilly** (InstaDeep Paris und London; 2024) räumt die Zoologie der fermionischen Shadow-Ensembles auf. Zhao, Rubin und Miyake benutzten signierte Permutationen, Wan et al. die volle Gruppe $O(2n)$, O'Gorman Perfect Matchings; das $SO(2n)$-Ensemble war unanalysiert, und die Beziehung der Protokolle unklar. Das Paper führt *Clifford-3-Kubaturen* ein, zeigt, dass das $SO(2n)$-Ensemble eine ist, beweist die Äquivalenz aller genannten Protokolle und leitet daraus ein gatteroptimales Sampling-Schema ab.

### Einordnung in die Tabellen

* **Task type:** Estimating, derselbe Aufgabentyp wie bei Wan et al.; das Paper ändert nur die Ensemblewahl. Eintrag in der Zeile "Classical shadows, other ensembles".
* **Objekt:** fermionischer Zustand. **Zugriff:** Sample, Einzelkopien, Matchgate-Schaltkreise aus unabhängigen zufälligen Pauli-Rotationen.
* **Status:** 🟢 🟢 🟢, mit den Varianzen von Wan et al. und weniger Gattern.
* **Versprechen:** wie bei Wan et al.

### Das Problem

Der Messkanal hängt vom 2-fach-Twirl ab, die Varianz vom 3-fach-Twirl; Ensembles mit denselben ersten drei Momenten sind für Shadows äquivalent. Wan et al. hatten das für $O(2n)$ gegen seine Clifford-Untergruppe gezeigt und die Frage nach $SO(2n)$ offen gelassen; Zhao und Miyake hatten das Fehlen bemerkt. Außerdem schienen die diskreten Ensembles eine bevorzugte Majorana-Basis auszuzeichnen, und die Beziehung der Varianzen verschiedener Unterensembles war nur teilweise bekannt.

### Kernresultate

* **Lemma 1.** Für eine Pauli-Rotation $R_\theta = e^{-i\theta Z/2}$ mit Winkel $\theta$ aus einer um die Clifford-Winkel symmetrischen Verteilung $\nu$ gilt $\mathbb{E}\,\mathcal{R}_\theta^{\otimes 3} = \frac{1-p}{2}(\mathcal{I}^{\otimes 3} + \mathcal{Z}^{\otimes 3}) + \frac p2(\mathcal{S}^{\otimes 3} + \mathcal{S}^{\dagger\otimes 3})$: Der dritte Twirl einer zufälligen Rotation ist eine konvexe Kombination von Clifford-Twirls.
* **Theorem 1.** Jedes Ensemble aus Matchgate-Schaltkreisen fester Architektur mit unabhängigen Rotationen, deren Winkelverteilungen die Symmetrie erfüllen, hat dieselben ersten drei Momente wie sein Clifford-Unterensemble: eine Clifford-3-Kubatur. Insbesondere ist das $SO(2n)$-Ensemble $M_n^+$ eine Clifford-3-Kubatur, und Proposition 2 verallgemeinert das Matchgate-3-Design von Wan et al. auf $M_n^+\cap\mathrm{Cl}_n$.
* **Propositionen 3 und 4 (Äquivalenzen).** Die Varianzen der Shadow-Schätzer sind invariant unter Reflexionen an Majorana-Operatoren (Einfügen von Vorzeichen $Q = DQ'$), und Ensembles, deren Permutationen demselben Perfect Matching entsprechen, liefern dieselben Varianzen. Damit sind die Protokolle von Zhao et al., Wan et al. und O'Gorman äquivalent.
* **Proposition 5 / Algorithmus 1.** Ein Sampling-Schema über Perfect Matchings, das in der Gatterzahl (Givens-Rotationen) optimal ist und die Garantien der vollen Ensembles erbt.
* Numerischer Vergleich der Schemata; die Autoren erwarten Anwendungen der Kubatur-Resultate in Randomized Benchmarking und variationalen Algorithmen.

### Methodischer Ansatz

* Zerlegung von $SO(2n)$-Elementen in Givens-Rotationen benachbarter Achsen, die unter Jordan–Wigner Zwei-Qubit-$XX$-Rotationen und Ein-Qubit-$Z$-Rotationen sind; die Twirl-Kanäle der Rotationen werden per Lemma 1 in Clifford-Kanäle zerlegt, und die Konvexität überträgt sich auf Produkte.
* Die Äquivalenzbeweise laufen über die Invarianzen des 3-fach-Twirls und die Struktur der generalisierten symmetrischen Gruppe $\mathbb{Z}_2\wr\mathrm{Sym}(2n)$.

### Bedeutung und Anwendungen

* Beantwortet die offene Frage von Wan et al. positiv und macht die Wahl des Ensembles zu einer reinen Hardware-Frage: Man nimmt das mit den wenigsten Gattern.
* Die Kubatur-Sicht (statt Design-Sicht) ist allgemeiner: Sie gilt für Winkelverteilungen, nicht nur für Gruppen, und ordnet Ergebnisse wie die Clifford-2-Kubaturen früherer Arbeiten ein.

### Bezug zum eigenen Projekt

* Die Botschaft "Momente entscheiden, nicht das Ensemble" gilt auch für die Bell-Messung auf $\rho\otimes\rho^*$: Zwei Zwei-Kopien-Messbasen mit denselben ersten drei Momenten sind für Magnituden- und Varianzfragen ununterscheidbar. Das ist ein Kriterium, um Varianten der eigenen Messung (etwa mit vorgeschalteten lokalen Qudit-Cliffords) ohne neue Analyse zu bewerten.
* Die Invarianz unter Reflexionen ist das fermionische Gegenstück zur Frage, ob $D_{q,p}$ und $D_{-q,p}$ (also $D$ und $D^T$) für die Statistik äquivalent sind; für $\rho\otimes\rho$ gegen $\rho\otimes\rho^*$ ist genau das der Unterschied.
* Gatteroptimale Sampling-Schemata sind der Faktor "Hardware-Realismus" auf der Messseite.

### Grenzen und offene Fragen

* Die Kubatur gilt für Schaltkreise fester Architektur; approximative Ensembles mit sublinearer Tiefe liefern nur approximative Twirls, und ein Schätzer dafür ist unklar.
* Keine neuen Varianzschranken, nur Äquivalenzen.
* Der Zusammenhang zu zufälligen phylogenetischen Bäumen (zufällige Perfect Matchings) wird als Ausblick genannt.

### Fragen zum Tieferbohren

* Wie sieht Lemma 1 für Qudit-Rotationen $e^{-i\theta Z}$ mit $Z$ dem Clock-Operator aus, und welche Winkelverteilungen ergeben Qudit-Clifford-Kubaturen?
* Gibt es eine Kubatur-Aussage für die transversale Bell-Messung mit vorgeschalteten zufälligen lokalen Cliffords auf beiden Kopien?
* Ist das Perfect-Matching-Schema das fermionische Analogon der Dimer-Überdeckung von Ippoliti, und was verbindet die beiden Zählargumente?

Paper: [arXiv:2409.03836](https://arxiv.org/abs/2409.03836)

---

## The Magic in Qudit Shadow Estimation based on the Clifford Group (arXiv:2410.13572)

Die Arbeit von **Chengsi Mao, Changhao Yi und Huangjun Zhu** (Fudan; 2024, mit Begleitpapier zu dritten Momenten von Clifford-Orbits) klärt die Sample-Komplexität von Shadow Estimation auf Qudits ungerader Primzahldimension $d$. Die Qudit-Clifford-Gruppe ist nur ein 2-Design, und die Stabilizerzustände weichen im dritten Moment exponentiell in $n$ von einem 3-Design ab; trotzdem ist der Overhead gegenüber Qubits nur $O(d)$, unabhängig von $n$. Eine Schicht aus wenigen T-Gattern, schon ein einziges, beseitigt den Overhead und macht die Fidelity-Schätzung unabhängig von $d$ und $n$.

### Einordnung in die Tabellen

* **Task type:** Estimating. Gegeben Fidelities mit Stabilizer-Projektoren, Weyl-Observablen, allgemeine spurfreie Operatoren; zurück kommen die Werte mit Shadow-Norm-Garantie. Neue Zeile "Classical shadows on qudits" der Estimating-Tabelle; zugleich die Qudit-Fortsetzung der Clifford-Zeile von Huang, Kueng, Preskill.
* **Objekt:** $n$-Qudit-Zustand, $d$ ungerade Primzahl, $D = d^n$. **Zugriff:** Sample, Einzelkopien, lokale oder globale Qudit-Cliffords, optional gefolgt von $k$ T-Gattern mit Fourier-Gattern.
* **Status:** 🟢 🟢 🟢 für Observablen beschränkter Hilbert–Schmidt-Norm; Simulation eines Shots kostet $O((n+t)^3 + t\,d^{t+1})$ mit $t$ Magic-Gattern.
* **Versprechen:** beschränkte Hilbert–Schmidt-Norm (global) oder $m$-Lokalität (lokal).

### Das Problem

Qubit-Shadows beruhen auf der 3-Design-Eigenschaft der Clifford-Gruppe. Für $d$ ungerade Primzahl ist $\mathrm{Cl}(n,d)$ kein 3-Design, und die Shadow-Norm generischer Observablen war unbekannt, obwohl Qudit-Prozessoren (Photonen, Ionen, Transmons) existieren. Wie teuer ist Qudit-Shadow-Estimation, und kann man die fehlende Design-Eigenschaft billig nachrüsten?

### Kernresultate

* **Lokale Cliffords (Proposition 1, Theorem 1).** Für $m$-lokale Weyl-Operatoren $\Vert O\Vert^2_{\mathrm{sh}} = (d+1)^m$; für $m$-lokale Operatoren allgemein $\leq d^m\Vert\tilde O\Vert_2^2$. Rekonstruktion $\bigotimes_j((d+1)U_j^\dagger|b_j\rangle\langle b_j|U_j - I)$.
* **Globale Cliffords (Theorem 2).** $\Vert O\Vert_2^2 \leq\Vert O\Vert^2_{\mathrm{sh}} \leq (2d-3)\Vert O\Vert_2^2 + 2\Vert O\Vert_\infty^2$ für spurfreie $O$; diagonal in einer Stabilizerbasis $\leq (d-1)\Vert O\Vert_2^2 + d\Vert O\Vert_\infty^2$; für $n = 1$ und diagonal exakt $(d+1)\Vert O\Vert_\infty^2$. Das Verhältnis $\Vert O\Vert^2_{\mathrm{sh}}/\Vert O\Vert_2^2 \leq 2d-1$ ist unabhängig von $n$, obwohl die Operatornorm des dritten normierten Momentenoperators von $\mathrm{Stab}(n,d)$ für $d \neq 2 \bmod 3$ exponentiell wächst.
* **Theorem 3.** Für Stabilizer-Projektoren vom Rang $K$: $\Vert O_0\Vert^2_{\mathrm{sh}}/\Vert O_0\Vert_2^2 = \frac{D+1}{D+d}(d-1-\frac dD + \frac dK)$: linear in $d$, praktisch unabhängig von $n$ ab $n \geq 5$. Stabilizerzustände sind die für Stabilizer-Messungen schwierigsten Observablen.
* **Theorem 4 (Magic).** Mit einem Clifford gefolgt von $k$ T-Gattern (diagonale Gatter der dritten Clifford-Hierarchie, $\omega^{f(b)}$ mit kubischem $f$) gilt $\Vert O_0\Vert^2_{\mathrm{sh}} \leq\gamma_{d,k}\Vert O_0\Vert_2^2$ mit $\gamma_{d,k} = 3 + 2^{k+1}/(d(d-2)^k)$ für $d \neq 1 \bmod 3$ und einer Formel derselben Gestalt sonst; $\gamma_{d,k}$ konvergiert exponentiell in $k$ gegen den 3-Design-Wert $3$, und schon $k = 1$ entfernt den Faktor $d$.
* **Numerik.** GHZ mit $n = 100$: Ohne T-Gatter ist die Steigung von $1/\langle\epsilon^2\rangle$ gegen $N$ etwa $\propto 1/d$; mit einem T-Gatter ist das Verhältnis der Steigungen über alle $d$ höchstens 3. Eine Dualität: die MSE hängt von der Gesamtzahl der T-Gatter in Präparation *und* Messung ab. Depolarisierte GHZ-Fidelity mit 5000 Samples gut geschätzt, Streuung sinkt mit $k$.

### Methodischer Ansatz

* Dritte Momente von Clifford-Orbits, insbesondere von Stabilizer- und Magic-Zuständen, aus dem Begleitpapier; der Schlüssel ist, dass die Shadow-Norm nicht die Operatornorm des Momentenoperators braucht, sondern nur bestimmte Matrixelemente.
* Für die Simulation: verallgemeinerte Tableau-Darstellung und Gadgetisierung der T-Gatter auf Qudits, kombiniert mit Clifford-Sampling.

### Bedeutung und Anwendungen

* Die Verifikation von Qudit-Systemen ist leichter als befürchtet; ein einziges Magic-Gatter schließt die Lücke zu Qubits, ein neuer Anwendungsfall für "wenig Magic als Ressource".
* Zeigt, dass Ensembles weit von 3-Designs (nach dem üblichen Maß) für Shadows genauso gut sein können; das Maß "Abstand zum 3-Design" ist für Shadows das falsche.

### Bezug zum eigenen Projekt

* Das ist die Einzelkopien-Referenz *auf Qudits*: Für ein einzelnes Qudit ($n = 1$) ist die Stabilizerbasis-Messung eine vollständige MUB-Menge, und die Shadow-Norm eines Displacement-Operators trägt den Faktor $d+1$ (Gl. 11). Zusammen mit Theorem 31 bei King, Wan, McClean ($\Omega(d)$ Varianz für Displacements) ist das die $\Omega(d/\epsilon^2)$-Wand, die Konjugatpaare unterlaufen.
* T-Gatter in der Messung sind ein neuer Freiheitsgrad, der bei Bell-Messungen fehlt: Die Frage, ob ein Magic-Gatter vor der Bell-Messung die Verteilung über die $d^2$ Adressen gleichmäßiger oder informativer macht, ist offen und testbar.
* Die Beobachtung "Stabilizerzustände sind für Stabilizer-Messungen am schwierigsten" ist das Spiegelbild von Montanaros Plateau: Wo alle Koeffizienten Betrag eins haben, ist Lokalisierung leicht und Schätzung schwer.

### Grenzen und offene Fragen

* Nur ungerade Primzahlen $d$; zusammengesetztes $d$ (kein Körper) ist außen vor, genau der Fall, der für dieses Projekt zählt.
* Theorem 2 ist eine obere Schranke; für generische Observablen ist die tatsächliche Norm oft viel kleiner und $d$-unabhängig (Fig. 2).
* Die genaue Form von $\gamma_{d,k}$ für $d = 1 \bmod 3$ ist eine andere Formel; Details im Begleitpapier.
* Rauschen und Fehlerminderung nicht behandelt.

### Fragen zum Tieferbohren

* Wie sieht Theorem 2 für $d = 4, 6, 8, 9$ aus, wo $\mathbb{Z}_d$ kein Körper ist und die Clifford-Gruppe eine andere Struktur hat?
* Was ist die Shadow-Norm von $D_{q,p}$ unter dem Clifford-plus-T-Ensemble, und fällt der Faktor $d$ auch dort?
* Gibt es ein Zwei-Kopien-Analogon der T-Gatter-Dualität, also eine Beziehung zwischen Magic des Zustands und Informationsgehalt eines Bell-Samples?

Paper: [arXiv:2410.13572](https://arxiv.org/abs/2410.13572)

---

## Classical shadows over symmetric spaces (arXiv:2605.05518)

Die Arbeit von **Rebecca Chang, Maureen Krumtünger, Martín Larocca und Maxwell West** (MIT, Los Alamos, Melbourne, Oak Ridge; 2026) verlässt die Annahme, dass das Shadow-Ensemble eine Gruppe ist: Sie untersucht Ensembles, die gleichverteilt aus den sieben unendlichen Familien kompakter symmetrischer Räume vom Typ I stammen, Quotienten $G/K$ der unitären, orthogonalen und symplektischen Gruppe nach den Fixpunktmengen einer Involution. Das Ergebnis ist eine einheitliche Theorie: Der Messkanal ist eine konvexe Kombination des Kanals der Elterngruppe, eines Dephasierungskanals und, bei symplektischem $G$, eines subleading Terms; für Observablen, die auf der bevorzugten Basis konzentriert sind, gibt es leichte Verbesserungen.

### Einordnung in die Tabellen

* **Task type:** Estimating; wieder ist die Neuerung das Ensemble. Eintrag in der Zeile "Classical shadows, other ensembles".
* **Objekt:** Zustand. **Zugriff:** Sample, Einzelkopien, $U \sim G/K$ realisiert als $\sigma(g)^{-1}g$ mit $g \sim G$.
* **Status:** 🟢 🟢 🟢; die Inversion des Kanals ist trivial, weil die Zerlegung multiplizitätsfrei ist.
* **Versprechen:** keines über den Zustand; ein Gewinn tritt nur für Observablen mit Gewicht auf der Diagonale der Messbasis $W$ auf.

### Das Problem

Shadows über kompakten Gruppen sind über Schur's Lemma gut verstanden: Der Kanal ist $G$-äquivariant und zerfällt nach Irreps. Symmetrische Räume sind keine Gruppen, der Kanal ist nicht mehr äquivariant unter allen Nebenklassenvertretern, und es war unklar, ob sich etwas Systematisches sagen lässt. Motivation: Symmetrische Räume spielen in der Kompilation eine Rolle (Cartan-Zerlegungen), und die induzierten Verteilungen auf $G$ sind nicht-uniform, also möglicherweise besser an Observablenklassen anpassbar.

### Kernresultate

* **Lemma 1.** Der Kanal $\mathcal{M}_{G/K,W}$ kommutiert mit der adjungierten Wirkung jeder Untergruppe $H \subseteq K\cap N_W$ ($N_W$ die $W$-normalisierenden Elemente), also zerfällt er nach $H$-Irreps; in allen Fällen multiplizitätsfrei, die $s_\lambda$ sind reelle Zahlen.
* **Theorem 1.** $\mathcal{M}_{G/K,W}(\rho) = (1-\alpha)\mathcal{M}_{G,W}(\rho) + \beta\mathcal{A}_W(\rho) + (\alpha-\beta)(J\mathcal{A}_W(\rho)J^\dagger - \mathcal{A}_W(\rho J)J)$, mit $\mathcal{A}_W$ dem Dephasierungskanal in $W$ und $J$ der symplektischen Form. Für AI, AII, CI, DIII ist $\alpha = O(d^{-2})$, also praktisch ohne Interesse; für AIII, BDI, CII ist $0 \leq\alpha\leq 1$ über die Signatur $s$ der Involution einstellbar. $\alpha = \beta$ außer für $G = SP$, dort $|\alpha - \beta| = O(1/d)$. Tabelle I gibt $\alpha_{G/K}$ für alle sieben Familien.
* **Konsequenzen.** Die Kanäle erben das Bild des Elternkanals, also dieselbe Menge unverzerrt schätzbarer Observablen; die Varianz hängt von der 2-Norm der Projektion der Observablen auf den diagonalen Unterraum ab; bei $d = 128$ zeigen AIII und BDI knappe Verbesserungen gegenüber unitär und orthogonal, wenn die Observablen stark auf der Diagonale konzentriert sind. AIII und CII stimmen führend überein, weil symplektische Ensembles Zustands-$k$-Designs für alle $k$ sind.
* **Sampling.** 6-Designs über die Elterngruppen genügen; für die unitäre Gruppe in logarithmischer Tiefe, für orthogonale und symplektische nicht in sublinearer Tiefe (No-go-Sätze).

### Methodischer Ansatz

* Twirls zweiter Ordnung über $G/K$ als Twirls vierter Ordnung über $G$ (Weingarten-Kalkül auf $U$, $O$, $SP$; für BDI $(11!!)^2$ Terme) oder direkt über Matsumotos Weingarten-Kalkül für symmetrische Räume. Theorem 1 macht die volle Rechnung überflüssig: Zwei Unbekannte werden aus wenigen Matrixelementen bestimmt.
* Die Sampling-Vorschrift $\sigma(g)^{-1}g$ (Duenez, Matsumoto) ist links-$K$-invariant.

### Bedeutung und Anwendungen

* Schließt die Theorie der Shadows über die klassischen kompakten Gruppen und ihre symmetrischen Räume; die Gruppen-Fälle (unitär: HKP; orthogonal: West et al. "real shadows"; symplektisch: West et al. 2024) sind Spezialfälle.
* Der Ausblick nennt allgemeine Darstellungen, etwa DIII mit $SO$ als Matchgate-Gruppe, wo $SO(2n)/U(n)$ die Mannigfaltigkeit reiner Gauß-Zustände ist: eine Brücke zu den Matchgate-Papieren.

### Bezug zum eigenen Projekt

* Das Ensemble-Denken "konvexe Kombination aus Elternkanal und Dephasierung" beschreibt auch Bell-Messungen mit unvollkommenen Gattern: Ein Rauschkanal vor der Bell-Basis wirkt wie eine Dephasierung in der Bell-Basis, und die Formel sagt, wie sich die Rekonstruktion ändert. Das ist relevant für den Faktor "Hardware-Realismus" der eigenen Taxonomie.
* Die Beobachtung, dass eine Basis-Bevorzugung nur auf der Diagonale hilft, ist ein Hinweis darauf, warum das Heisenberg–Weyl-Spektrum als *Ganzes* keine bevorzugte Einzelkopien-Basis hat: Jede Displacement-Adresse ist in jeder Stabilizerbasis gleich schlecht sichtbar.
* Die Cartan-Struktur ist das Werkzeug, mit dem man fragen könnte, ob $\rho\otimes\rho^*$ ein Punkt in einem symmetrischen Raum ist (die Konjugation ist eine Involution) und was das für Twirls über die Kopien bedeutet.

### Grenzen und offene Fragen

* Die Verbesserungen sind konstant und klein; das Paper ist primär strukturell.
* Die Operatoren $s_\lambda$ werden nicht direkt aus der Darstellungstheorie identifiziert; für Gruppen gibt es einfache Formeln, für symmetrische Räume nicht.
* Nur definierende Darstellungen; allgemeine Darstellungen sind Ausblick.

### Fragen zum Tieferbohren

* Ist die Abbildung $\rho \mapsto \rho^*$ eine Involution, deren Fixpunktmenge (reelle Zustände) einen symmetrischen Raum definiert, und was ist der zugehörige Shadow-Kanal auf $\rho\otimes\rho^*$?
* Wie sieht Theorem 1 für die Heisenberg–Weyl-Gruppe als Untergruppe von $U(d)$ aus, und welche Involutionen respektieren sie?
* Lässt sich der Dephasierungsanteil $\beta\mathcal{A}_W$ als Modell für Auslesefehler in der Bell-Basis benutzen, und wie skaliert die nötige Korrektur mit $d$?

Paper: [arXiv:2605.05518](https://arxiv.org/abs/2605.05518)

---

## Triply efficient shadow tomography (arXiv:2404.19211)

Die Arbeit von **Robbie King, David Gosset, Robin Kothari und Ryan Babbush** (Google Quantum AI, Caltech, Waterloo, Perimeter; *PRX Quantum* 6, 010336 (2025)) definiert *triple Effizienz*: sample-effizient ($\mathrm{poly}(\log|S|, 1/\epsilon)$), rechen-effizient ($\mathrm{poly}(|S|, n, 1/\epsilon)$) und Messungen auf konstant vielen Kopien zugleich, mit Gesamtspeicher $O(n)$. Sie gibt die ersten triply effizienten Protokolle für alle $4^n$ Paulis und für $k$-Körper-Fermionen, beide mit Zwei-Kopien-Clifford-Messungen, und zeigt, dass Zwei-Kopien-Messungen dafür nötig sind. Der Rahmen: Bell-Sampling reduziert das Problem auf fraktionale Färbung eines induzierten Teilgraphen des Kommutationsgraphen mit beschränkter Cliquenzahl.

### Einordnung in die Tabellen

* **Task type:** Estimating. Gegeben eine Menge $S$ von Paulis, zurück kommen alle $\mathrm{Tr}(P\rho)$; für $S = \mathcal{P}^{(n)}$ ist das die Zeile "All $4^n$ Pauli observables, two-copy", für $S = \mathcal{F}_k^{(n)}$ die fermionische Zeile.
* **Objekt:** Zustand. **Zugriff:** Sample; Bell-Messung auf $\rho\otimes\rho$ für die Magnituden (Rung 1, Quantenspeicher zwei), dann Einzelkopien-Clifford-Messungen, geführt von einer Färbung.
* **Status:** 🟢 🟢 🟢 im Sinne der Definition. ⚠️ Korrektur an der Tabelle: Für alle Paulis ist die Rechenzeit $\mathrm{poly}(2^n, 1/\epsilon)$ (Theorem 7), also $\mathrm{poly}(|S|)$ mit $|S| = 4^n$, nicht $\mathrm{poly}(n)$; polynomiell in $n$ ist nur die Abfrage einer Pauli-Erwartung aus der komprimierten Darstellung (Corollary 12). Die Zeile ist entsprechend angepasst.
* **Versprechen:** Zwei-Kopien-Speicher als Ressource; kein Versprechen über den Zustand.

### Das Problem

Allgemeine Shadow Tomography ist exponentiell in der Rechenzeit und braucht verschränkte Messungen über viele Kopien. Classical Shadows sind triply effizient für $k$-lokale Paulis, versagen aber bei hohem Gewicht. Huang, Kueng und Preskill (2021) lernen beliebige Pauli-Mengen mit $O(\log|S|/\epsilon^4)$ Kopien und $\mathrm{poly}(|S|)$ Zeit, brauchen aber Gentle Measurements auf vielen Kopien für die Vorzeichen. Für $k$-Körper-Fermionen und für alle Paulis ist sample-effiziente Einzelkopien-Tomographie unmöglich (Theorem 2 aus Chen, Cotler, Huang, Li; Theorem 3 neu: $\Omega(n^k/\epsilon^2)$). Gibt es triply effiziente Protokolle mit zwei Kopien?

### Kernresultate

* **Theorem 5 (Einzelkopien via fraktionale Färbung).** Hat der Kommutationsgraph $G(S)$ eine samplebare fraktionale Färbung der Größe $\chi$, dann lernt man alle $\mathrm{Tr}(P\rho)$ mit $O(\chi\log|S|/\epsilon^2)$ Einzelkopien-Clifford-Messungen; die Pauli-Shadows von HKP sind der Fall $\chi = 3^k$.
* **Theorem 6 (zwei Kopien, jede Menge $S$).** $O(\log|S|/\epsilon^4)$ Zwei-Kopien-Messungen: Bell-Sampling liefert $|\mathrm{Tr}(P\rho)|$ auf $\epsilon/4$, definiert $S_\epsilon = \{P: u_P \geq 3\epsilon/4\}$; ein *Mimicking State* $\sigma$ mit $|\mathrm{Tr}(\sigma P)| \geq\epsilon/4$ auf $S_\epsilon$ existiert (etwa $\rho$) und wird ohne weitere Kopien per Brute Force gefunden; Bell-Sampling auf $\rho\otimes\sigma$ liefert $\mathrm{Tr}(P\rho)\mathrm{Tr}(P\sigma)$ und damit die Vorzeichen. Sample-effizient, rechnerisch absurd.
* **Theorem 7 (alle Paulis, triply effizient).** $O(n\log(n/\epsilon)/\epsilon^4)$ Samples, Zeit $\mathrm{poly}(2^n, 1/\epsilon)$: Der Mimicking State wird per Matrix Multiplicative Weights mit zusätzlichen Einzelkopien-Messungen berechnet und mit $O(4^n)$ Gattern präpariert.
* **Lemma 8.** Die größte Clique in $G(S_\epsilon)$ hat mit hoher Wahrscheinlichkeit höchstens $4/\epsilon^2$ Knoten: Antikommutierende Observablen können nicht gleichzeitig groß sein (Unschärfe).
* **Lemma 9 und Theorem 10 ($k$-Körper-Fermionen).** Induzierte Teilgraphen von $G(\mathcal{F}_k^{(n)})$ sind $\chi$-beschränkt mit polynomieller Bindungsfunktion $p_k(\omega)$, $p_1(\omega) = \omega+1$, $p_2 = O(\omega^8)$; Sample-Komplexität $O(k\log n\cdot p_k(4/\epsilon^2)/\epsilon^2)$, für $k = 1$ also $O(\log n/\epsilon^4)$, für $k = 2, 3$ etwa $\epsilon^{-18}$ und $\epsilon^{-110}$.
* **Lemma 11 und Corollary 12 (Kompression).** Induzierte Teilgraphen von $G(\mathcal{P}^{(n)})$ haben $\chi \leq (2n+1)^{\omega-1}$ (Gyárfás, längste induzierte Pfade $\leq 2n+1$); damit lässt sich jeder Zustand für konstantes $\epsilon$ in $\mathrm{poly}(n)$ Bits komprimieren, aus denen jede Pauli-Erwartung in $\mathrm{poly}(n)$ Zeit folgt, gelernt aus $\mathrm{poly}(n)$ Kopien mit $2^{O(n)}$ Rechenzeit.
* **Conjecture 13.** Die Paulis mit $|\mathrm{Tr}(\rho P)| \geq\delta$ haben eine fraktionale Färbung der Größe $O(1/\delta^2)$; wäre sie effizient, gäbe es triply effiziente Shadow Tomography für jede Pauli-Menge.

### Methodischer Ansatz

1. **Magnituden per Bell-Sampling** in der Basis, die alle $P\otimes P$ diagonalisiert; $\mathrm{Tr}(\rho P)^2$ mit $\delta = \Theta(\epsilon^2)$, daher $\epsilon^{-4}$.
2. **Vorzeichen als Färbungsproblem.** Auf $S_\epsilon$ genügt Einzelkopien-Lernen mit einer Färbung von $G(S_\epsilon)$; die Cliquenzahl $O(1/\epsilon^2)$ und $\chi$-Beschränktheit liefern polynomielle Färbungen.
3. **Mimicking State per MMW** für alle Paulis: Die Hypothese wird so lange aktualisiert, bis sie auf $S_\epsilon$ betragsmäßig groß ist; das ist die Technik, die King, Wan, McClean für Displacement-Operatoren übernehmen.

### Bedeutung und Anwendungen

* Definiert das Effizienzziel dieses Projekts und liefert die erste Landkarte (Tabelle 2 des Papers): naiv, HKP, Bell-Sampling plus Gentle Measurement, und die neuen Zwei-Kopien-Verfahren.
* Zwei Kopien sind notwendig *und* hinreichend für Pauli- und fermionische Shadow Tomography; lokale Paulis gehen mit einer Kopie, lokale Fermionen nicht: ein sauberer Unterschied zwischen Qubit- und Fermion-Lokalität.
* Die Graphentheorie ($\chi$-Beschränktheit, Gyárfás) ist ein neues Werkzeug in der Quantenlerntheorie.

### Bezug zum eigenen Projekt

* Das eigene Paper zitiert genau dieses Papier für "triply efficient" und ersetzt zwei seiner Komponenten: die Färbung (Gruppierung inkompatibler Observablen) und das MMW. Die Sample-Komplexität $O(\log|S|/\epsilon^4)$ der Magnituden ist dieselbe wie in Phase 1; die $\epsilon^{-2}$ der Vorzeichen entspricht Phase 2.
* Lemma 8 ist eine Strukturaussage über *jeden* Zustand: Höchstens $4/\epsilon^2$ paarweise antikommutierende Adressen können gleichzeitig groß sein. Für Displacement-Operatoren mit ihrer $\omega$-Kommutation ist das Analogon eine Schranke an die Zahl großer Amplituden auf nicht-kommutierenden Adressen, ein Kandidat für ein beweisbares Versprechen im Top-$k$-Regime.
* Die Korrektur der Tabelle (Zeit $\mathrm{poly}(4^n)$ für alle Paulis) ist wichtig für die Positionierung: Das eigene Verfahren ist nicht "so effizient wie KGKB", sondern zielt auf Zeit polynomiell in $\log d$ bei einer Liste, die nur implizit gegeben ist, und genau das ist im Allgemeinen (Conjecture 13) offen.

### Grenzen und offene Fragen

* Triply effiziente Shadow Tomography für *beliebige* Pauli-Teilmengen ist offen (Conjecture 13); Lemma 11 gibt nur $n^{O(1/\epsilon^2)}$ Farben.
* Die $\epsilon$-Exponenten für Fermionen ($\epsilon^{-18}$, $\epsilon^{-110}$) sind unpraktisch; bessere Bindungsfunktionen sind offen.
* Rapid-Retrieval-Kompression für $\epsilon = 1/\mathrm{poly}(n)$ ist offen.
* Bell-Sampling auf $\rho\otimes\rho$ liefert $\mathrm{Tr}(\rho P)^2$ nur für Paulis; für Displacement-Operatoren braucht man $\rho\otimes\rho^*$.

### Fragen zum Tieferbohren

* Wie sieht der Kommutationsgraph der $d^2$ Displacement-Operatoren aus, was ist seine Cliquenzahl auf der Menge großer Amplituden, und ist die Familie seiner induzierten Teilgraphen $\chi$-beschränkt?
* Kann das CNN die Färbung *implizit* lernen, und lässt sich das an der Struktur der gelernten Filter ablesen?
* Was ist die Rapid-Retrieval-Kompression eines Qudit-Zustands mit $k$-sparsamem Spektrum: $O(k\log d)$ Bits, und ist die Abfrage in $O(\log d)$ Zeit möglich?

Paper: [arXiv:2404.19211](https://arxiv.org/abs/2404.19211)

---
## Exponential learning advantages with conjugate states and minimal quantum memory (arXiv:2403.03469)

Die Arbeit von **Robbie King, Kianna Wan und Jarrod R. McClean** (Google Quantum AI, Caltech, Stanford; *PRX Quantum* 5, 040301 (2024)) führt die Lernressource dieses Projekts ein: gemeinsame Messungen auf einem Zustand und seinem komplex Konjugierten, $\rho\otimes\rho^*$. Für die Aufgabe, alle $d^2$ Displacement-Amplituden $y_{q,p} = \mathrm{Tr}(D_{q,p}\rho)$ eines $d$-dimensionalen Zustands zu lernen, genügen $O(\log d/\epsilon^4)$ Kopien von $\rho\otimes\rho^*$, während jedes Verfahren auf $\rho^{\otimes K}$ ohne $\rho^*$ mindestens $\Omega(\sqrt d/(K^2\epsilon^2))$ Messungen braucht, selbst für $K$ bis $1/(12\epsilon)$. Die Vorzeichen folgen mit einem Hypothesenzustand und Matrix Multiplicative Weights; dazu kommen verallgemeinerte Clifford-Shadows für Qudits und der Nachweis, dass der Kommutationstrick auf Displacement-Operatoren beschränkt ist.

### Einordnung in die Tabellen

* **Task type:** Estimating. Gegeben ist die implizite Liste aller $d^2$ Displacement-Adressen, zurück kommen Beträge und Vorzeichen. Die Zeile "Displacement amplitudes over a dictionary, conjugate pairs" der Estimating-Tabelle; in der Suchtabelle ist dasselbe Paper die Grundlage der Sample-Seite.
* **Objekt:** $d$-dimensionaler Zustand, $d$ Primzahl in den Sätzen. **Zugriff:** Sample auf $\rho\otimes\rho^*$, Rung 2 der Zugriffsleiter; die Bell-Messung verschränkt genau zwei Register, Quantenspeicher konstant.
* **Status:** 🟢 🟢 🟢. Kopien logarithmisch in $d$; die Magnitudenschätzung ist rechnerisch trivial; die Vorzeichenbestimmung läuft in $\mathrm{poly}(d, 1/\epsilon)$ über eine $d\times d$-Hypothese, polynomiell im Hilbertraum eines einzelnen Qudits, im $n$-Qubit-Bild also $2^n$.
* **Versprechen:** keines über den Zustand; die Ressource ist der Zugriff. Für die Top-$k$-Variante dieses Projekts kommt das Dictionary-Versprechen hinzu (Regime 1).

### Das Problem

Zwei-Kopien-Messungen liefern exponentielle Vorteile für Pauli-Erwartungswerte (Huang et al. 2022), und die Beträge sind mit minimalem Speicher lernbar, die Vorzeichen aber nur mit aufgabenabhängig großem Speicher (Huang, Kueng, Preskill 2021). Für Qudits ist zudem bekannt, dass Bell-Sampling auf $\rho\otimes\rho$ versagen kann. Die Fragen: Gibt es eine Ressource mit konstantem Speicher, die das ganze Displacement-Spektrum liefert, was kostet ihr Fehlen, und wo ist $\rho^*$ physikalisch verfügbar?

### Kernresultate

* **Theorem 1 (Untergrenze ohne $\rho^*$).** Beträge aller Amplituden auf $\epsilon$ mit Wahrscheinlichkeit $2/3$ aus Messungen auf $\rho^{\otimes K}$, $K \leq 1/(12\epsilon)$: $\Omega(\sqrt d/(K^2\epsilon^2))$ Messungen. Mit minimalem Speicher ist die Aufgabe ohne $\rho^*$ nicht effizient.
* **Theorem 2 (Beträge).** $O(\log d/\epsilon^4)$ Samples von $\rho\otimes\rho^*$ lernen alle $y_{q,p}$ bis auf ein Vorzeichen; einfach und rechnerisch effizient.
* **Theorem 3 (Einzelkopien).** Jedes Einzelkopien-Protokoll braucht $\Omega(d/\epsilon^2)$ Kopien, auch mit Einzelkopien-Zugriff auf $\rho$ *und* $\rho^*$: Verschränkte Messung ist nötig, nicht nur das Konjugat.
* **Theorem 4 (Eindeutigkeit).** Kommutieren $U\otimes\tilde U$ und $V\otimes\tilde V$ für nicht-kommutierende $U, V$ endlicher Ordnung $d$, dann sind $U, V$ unitär äquivalent zu einer direkten Summe von Displacement-Operatoren. Der Tensor-Erweiterungstrick ist auf Heisenberg-Gruppen beschränkt (Stone–von-Neumann-artig).
* **Theorem 5 (Vorzeichen).** Alle $d^2$ Amplituden inklusive Vorzeichen mit $O(\log d/\epsilon^4)$ Samples von $\rho\otimes\rho^*$, Laufzeit $\mathrm{poly}(d, \epsilon^{-1})$: Hypothesenzustand verschiebt den Ursprung einer Magnitudenmessung, MMW findet ihn (Technik aus King, Gosset, Kothari, Babbush).
* **Theorem 6 (Qudit-Clifford-Shadows).** Alle Nebendiagonalelemente $\langle i|U^\dagger\rho U|j\rangle$ in allen Stabilizerbasen $U \in\mathrm{Cl}_d$ mit $O(\log d/\epsilon^2)$ Einzelkopien; Theorem 31 gibt die Varianz für beliebige $O$, mit Hilbert–Schmidt-Anteil plus Displacement-Überlappen; für Displacement-Operatoren ist die Varianz $\Omega(d)$, konsistent mit Theorem 3.
* **Anwendungen.** Quantendaten aus Quantenrechnung: $\rho^*$ durch Konjugation jedes Gatters, also exponentieller Vorteil von White-Box- gegenüber Black-Box-Zugriff; Quantendaten aus der Natur: Sensor-Arrays, Long-Baseline-Interferometrie, Mixedness-Testing gegen thermischen Hintergrund; bosonischer Limes $d\to\infty$ mit $x = \sqrt{\pi/d}(q,p)$.

### Methodischer Ansatz

* **Kommutativität durch Tensor-Erweiterung.** $D_{q,p}\otimes D_{q,p}^*$ kommutieren für alle $(q,p)$ und werden gemeinsam gemessen; die Ausgangsverteilung ist $|y_{q,p}|^2/d$ (Anhang B). Auf $\rho\otimes\rho$ stünde $D\otimes D$, und die kommutieren nur für Qubits.
* **Untergrenzen** (Anhang G) per Tree-Methode über eine Familie von Zuständen nahe der maximal gemischten mit einer eingeprägten Displacement-Amplitude, mit der Nicht-Kommutativität von $D_{q,p}^{\otimes K}$ auf $\rho^{\otimes K}$ als Hebel; $K$ tritt quadratisch auf.
* **Vorzeichen** (Anhang C): Bell-Messung auf $\rho\otimes\sigma^*$ mit bekanntem Hypothesenzustand $\sigma$ liefert $\mathrm{Re}(y_{q,p}\overline{\mathrm{Tr}(D\sigma)})$-artige Größen; MMW passt $\sigma$ an, bis alle großen Adressen betragsmäßig groß auf $\sigma$ sind.
* **Shadows** (Anhang H): Twirls der Qudit-Clifford-Gruppe bis zur dritten Ordnung; $\mathrm{Cl}_d$ ist Normalisator der Heisenberg–Weyl-Gruppe und enthält die QFT.

### Bedeutung und Anwendungen

* Neue Achse in der Landkarte: Der Zugriff ($\rho$, $\rho\otimes\rho^*$, Schaltkreis) ist von der Speicherachse unabhängig, und die Trennung hier ist eine zwischen zwei Orakeln bei gleichem kleinem Speicher, nicht zwischen kohärent und inkohärent (siehe QUALM-Absatz).
* Eine physikalisch motivierte Observablenfamilie mit bosonischem Limes; das Paper verbindet Quantenlerntheorie mit Sensorik.
* Theorem 4 sagt, dass für Klassen jenseits der Heisenberg-Gruppen neue Primitiven nötig sind.

### Bezug zum eigenen Projekt

* Das ist Paper 1 des Projekts: Phase 1 ist Theorem 2, Phase 2 ersetzt das MMW aus Theorem 5 durch den adaptiven Probe-Zustand $\tilde\rho$ mit CNN-Steuerung. Die Sample-Komplexität $O(\log d/\epsilon^4)$ ist das Ziel der eigenen Skalierungsmessung in $d$; die $\epsilon^{-4}$ der Magnituden und $\epsilon^{-2}$ der Vorzeichen sind die Referenz für die empirische Gesamtskalierung.
* Theorem 3 ist der Grund, warum die Pipeline überhaupt zwei Kopien braucht, und Theorem 1 der Grund, warum $\rho\otimes\rho$ nicht genügt; die Evaluation von 2025 mit $\rho\otimes\rho$ arbeitet deshalb auf reellen Zuständen (GHZ, reelle Gibbs-Zustände), wo $\rho = \rho^*$.
* Theorem 4 ist die theoretische Grenze von Objective 3 ("Verallgemeinerungen von Paulis"): Der Trick reicht genau bis zu Displacement-Operatoren, nicht weiter.
* Die Untergrenze $\Omega(\sqrt d)$ ist eine *Sample*-Aussage; die LWE-Härte des eigenen Papers ist eine *Zeit*-Aussage über dieselbe Aufgabe mit Sparsity-Versprechen. Beide zusammen bilden die Zelle "sampling access, searching" des Quadranten.

### Grenzen und offene Fragen

* $d$ Primzahl in den Beweisen; zusammengesetztes $d$ und die zyklische Ein-Qudit-Basis sind nicht behandelt.
* Die Vorzeichenbestimmung ist polynomiell in $d$, nicht in $\log d$: rechnerisch effizient nur für einzelne Qudits, nicht für $n$-Qubit-Systeme mit $d = 2^n$.
* $\rho^*$ ist nicht physikalisch aus $\rho$ herstellbar; die Verfügbarkeit hängt von der Quelle ab (Anhang D), mit Einschränkungen bei Sensoren.
* Rauschen: keine Analyse; die Bell-Messung braucht saubere Zwei-Register-Gatter.

### Fragen zum Tieferbohren

* Wie sieht die Verteilung der Bell-Messung auf $\rho\otimes\rho^*$ für zusammengesetztes $d$ aus, wo $\mathbb{Z}_d$ kein Körper ist und $D_{q,p}$ Untergruppen verschiedener Ordnung erzeugen?
* Welche Phaseninformation genau bleibt bei "bis auf ein Vorzeichen" übrig, wenn $y_{q,p}$ komplex ist: der Betrag, oder auch das Argument modulo $\pi$?
* Wo liegt in der Tree-Methode des Beweises von Theorem 1 der Term, der bei Zugriff auf $\rho^*$ verschwindet, und lässt sich daraus ein Interpolationsresultat zwischen $\rho\otimes\rho$ und $\rho\otimes\rho^*$ (etwa $\rho\otimes\tilde\rho$ mit unvollkommenem Konjugat) gewinnen?

Paper: [arXiv:2403.03469](https://arxiv.org/abs/2403.03469)

---

## Quantum state tomography via compressed sensing (arXiv:0909.3304)

Die Arbeit von **David Gross, Yi-Kai Liu, Steven T. Flammia, Stephen Becker und Jens Eisert** (Hannover, Caltech, Perimeter, Potsdam; *Phys. Rev. Lett.* 105, 150401 (2010)) überträgt Compressed Sensing und Matrix Completion auf die Tomographie: Ein Zustand vom Rang $r$ in Dimension $d$ ist aus $O(rd\log^2 d)$ zufällig gewählten Pauli-Erwartungswerten eindeutig rekonstruierbar, per Minimierung der Spurnorm unter linearen Nebenbedingungen, statt aus $d^2$ Einstellungen. Das Verfahren ist robust gegen Rauschen, zertifiziert Nähe zur Reinheit ohne Vorannahme und läuft numerisch in Minuten für acht Qubits.

### Einordnung in die Tabellen

* **Task type:** Estimating mit $M = d^2$, aber unter einem Rangversprechen; zurück kommt die Dichtematrix. Die Zeile "Low-rank tomography, compressed sensing" der Estimating-Tabelle, im Abschnitt "structured escapes before shadows".
* **Objekt:** gemischter Zustand nahe Rang $r$. **Zugriff:** Sample, Einzelkopien, $m$ zufällige Pauli-Erwartungswerte, jeder aus vielen Kopien geschätzt.
* **Status:** 🔴 🔴 🔴 in $n$: $rd\log^2 d$ ist exponentiell in $n$, aber der Faktor $d$ statt $d^2$ ist eine quadratische Ersparnis, und Zeit und Speicher sind $O(rd)$-artig statt $O(d^2)$.
* **Versprechen:** Rang $r \ll d$, etwa reine Zustände unter lokalem Rauschen mit Rate $p$: Rang $\approx d^{H(p)}$.

### Das Problem

Volle Tomographie von acht Ionen kostete Hunderttausende Messungen und Wochen Nachverarbeitung. Parameterzählung sagt, dass $O(rd)$ Einstellungen für Rang $r$ reichen könnten, aber Minimum-Rang-Probleme sind NP-hart, und die Matrix-Completion-Sätze (Candès–Recht, Candès–Tao) verlangen Matrixelemente und Inkohärenz-Annahmen, die im Labor nicht passen. Gesucht: Pauli-Messungen, beliebige Dichtematrizen, effiziente Rekonstruktion.

### Kernresultate

* **Theorem 1.** Für $\rho$ vom Rang $r$ und $m = c\,dr\log^2 d$ zufällige Pauli-Erwartungswerte ist $\rho$ die eindeutige Lösung von $\min\Vert\sigma\Vert_{\mathrm{tr}}$ unter $\mathrm{tr}\,\sigma = 1$, $\mathrm{tr}(w(A_i)\sigma) = \mathrm{tr}(w(A_i)\rho)$, mit Fehlerwahrscheinlichkeit exponentiell klein in $c$.
* **Observation 1 (Rauschen).** Ist $\rho_t$ nur $\epsilon_1$-nahe an Rang $r$ und sind die Erwartungswerte bis auf $\epsilon_2$ bekannt, dann liefert das relaxierte Programm $\min\Vert\sigma\Vert_{\mathrm{tr}}$ mit $\Vert\mathcal{R}\sigma - \mathcal{R}\omega\Vert_2 \leq\epsilon$ einen Fehler $O(\epsilon\sqrt{rd})$ in Spurnorm; die Autoren vermuten deutlich bessere Robustheit.
* **Observation 2 (Zertifizierung).** Für fast reine Zustände lässt sich Reinheit aus $O(d)$ Pauli-Werten zertifizieren und der Zustand mit expliziten Fehlerschranken aus $O(cd\log^2 d)$ Werten rekonstruieren, ohne Vorannahme über $r$ und $\delta_1$.
* **Hybridmethode.** Strukturierte Zufallswahl $w(u,v)$ für $u$ aus einer Menge der Größe $O(r\,\mathrm{polylog}\,d)$ und alle $v$: Rechenzeit $O(d)$ statt $O(d^2)$ pro Schritt, ohne die volle Garantie.
* **Numerik.** Acht Qubits, Rang 3, 5% Depolarisierung, Gauß-Rauschen $\sigma = 0.1/d$: 95% Fidelity in unter zehn Sekunden mit der Hybridmethode; auf den Daten des Acht-Ionen-Experiments 90.5% Fidelity mit einer Rang-3-Näherung aus unter 30% der Paulis in drei Minuten.
* **Prozesse:** über den Jamiołkowski-Zustand, effektiv für Kanäle mit wenigen Kraus-Operatoren.

### Methodischer Ansatz

* **Dual Certificate.** Eindeutigkeit folgt aus einem strikten Subgradienten $Y$ der Spurnorm im Bild des Sampling-Operators $\mathcal{R}$; zwei Fälle nach dem Verhältnis von $\Delta_T$ zu $\Delta_T^\perp$ (Tangentialraum $T$ der Rang-$r$-Matrizen).
* **Golfing Scheme.** Ein rekursiver Prozess $Y_i = \sum_j\mathcal{R}_jX_{j-1}$ mit $l$ unabhängigen Batches von $\kappa_0 rd$ Paulis konvergiert exponentiell gegen einen fast-Subgradienten; nichtkommutative Large-Deviation-Schranken (Ahlswede–Winter) für $\Vert\mathcal{A} - \mathbb{1}_T\Vert$. Das ist eine deutliche Vereinfachung gegenüber Candès–Recht.
* **Solver:** Singular Value Thresholding statt Interior Point.

### Bedeutung und Anwendungen

* Der erste Beweis, dass ein Strukturversprechen (Rang) die Tomographie quadratisch verbilligt, und der Beginn der Anwendung von Compressed Sensing in der Quanteninformation; Nachfolger: Fehlerschranken und Sample-Komplexität (Flammia, Gross, Liu, Eisert 2012), Prozess-Tomographie mit Compressed Sensing (Rekord bei drei Qubits, zitiert in Flammia–Wallman).
* Das Golfing Scheme wurde ein Standardwerkzeug der Matrix-Completion-Theorie.

### Bezug zum eigenen Projekt

* Rang ist das "low rank ⇒ easy"-Versprechen; das eigene Projekt arbeitet mit dem dazu orthogonalen Versprechen Sparsity im Displacement-Spektrum. Beide sind Compressed-Sensing-Strukturen, aber die eigene Aufgabe hat keine *wählbaren* Messungen: Bell-Sampling liefert i.i.d. Züge, nicht die $m$ ausgewählten Erwartungswerte. Das ist der Unterschied zwischen dieser Zeile (🔴 in Kopien, aber Query-artig in der Auswahl) und der eigenen (🟢 in Kopien, LWE-hart im Decoder).
* Die Trace-Norm-Minimierung ist das konvexe Surrogat für Rang; das $\ell_1$-Surrogat für Sparsity im Spektrum wäre die naheliegende beweisbare Alternative zum CNN, sofern ein RIP-artiges Argument für Bell-Statistik existiert.
* Zertifizierte Tomographie (Observation 2) ist ein Vorbild für ein Zertifikat der Sparsity: Aus dem Bell-Record lässt sich $\sum|y_{q,p}|^4$-artige Statistik ablesen, die die Konzentration des Spektrums misst.

### Grenzen und offene Fragen

* Exponentiell in $n$; das Rangversprechen ändert den Exponenten nicht, nur die Basis.
* Die Robustheitsschranke $O(\epsilon\sqrt{rd})$ ist grob; RIP-basierte Argumente sollten besser sein (Vermutung).
* Die Hybridmethode ist ohne Garantie.
* Jeder Pauli-Erwartungswert braucht viele Kopien; die Sample-Komplexität in Kopien wird hier nicht gezählt.

### Fragen zum Tieferbohren

* Gilt ein Golfing-Argument für die Displacement-Basis eines Qudits, die orthogonal, aber nicht Hermitesch ist?
* Was ist die Compressed-Sensing-Formulierung von "Sparsity im Displacement-Spektrum plus i.i.d. Bell-Samples", und ist die Sample-Matrix inkohärent im Sinne der RIP?
* Wie hängen Rang und Displacement-Sparsity zusammen: Hat ein Rang-$r$-Zustand ein Spektrum mit höchstens wie vielen großen Adressen?

Paper: [arXiv:0909.3304](https://arxiv.org/abs/0909.3304)

---

## Estimating the spectrum of a density operator (arXiv:quant-ph/0102027)

Die Arbeit von **Michael Keyl und Reinhard F. Werner** (TU Braunschweig; *Phys. Rev. A* 64, 052311 (2001)) ist eine vierseitige Notiz mit einem Satz, der die Speicherachse an ihrem fernen Ende definiert: Misst man $N$ Kopien von $\rho$ gemeinsam in der Zerlegung von $\mathcal{H}^{\otimes N}$ nach irreduziblen Darstellungen der symmetrischen Gruppe, also nach Young-Diagrammen $Y$, dann ist $Y/N$ ein Schätzer des Spektrums von $\rho$, und die Fehlerwahrscheinlichkeit fällt exponentiell in $N$ mit einer explizit berechneten Rate, der relativen Entropie zwischen geschätztem und wahrem Spektrum.

### Einordnung in die Tabellen

* **Task type:** Estimating. Gegeben die implizite Liste "die Eigenwerte", zurück kommt das geordnete Spektrum $r_1 \geq\dots\geq r_d$. Die Zeile "Spectrum estimation by Schur sampling".
* **Objekt:** gemischter Zustand auf $\mathbb{C}^d$. **Zugriff:** Sample, aber mit einer kollektiven Messung auf allen $N$ Kopien zugleich; Quantenspeicher $k = N$, die Primitive "Collective Schur sampling".
* **Status:** 🔴 🔴 🟢 in $n$ gemäß Tabelle: Für Präzision $\epsilon$ braucht man $N \sim d^2/\epsilon^2$ Kopien (O'Donnell, Wright 2015 für die optimalen Raten), die Messung ist eine Schur-Transformation über $N$ Register, der Output hat nur $d$ Zahlen.
* **Versprechen:** keines; das Verfahren ist basisunabhängig und braucht nicht einmal die Kenntnis der Eigenbasis.

### Das Problem

Die Dichtematrix lässt sich nur auf Ensembles schätzen (No-Cloning), und Schätzung ist ein Grenzfall von Kloning bei $M\to\infty$. Für gemischte Zustände ist unklar, welche Gütefunktion "optimal" definiert. Statt Optimalität für endliches $N$ fragen die Autoren nach dem asymptotischen Verhalten bei beliebigen, auch verschränkten Messungen auf $\rho^{\otimes N}$, für die einfachste nichttriviale Größe: das Spektrum.

### Kernresultate

* **Symmetriereduktion.** Ohne Verlust an Schätzqualität darf der Schätzer mit allen Permutationen $S_p$ und allen $U^{\otimes N}$ kommutieren; dann ist er eine Funktion der Projektoren $P_Y$ auf die Summanden $R_Y\otimes S_Y$ der Schur–Weyl-Zerlegung $\mathcal{H}^{\otimes N} \cong\bigoplus_Y R_Y\otimes S_Y$, mit $Y$ den Young-Diagrammen mit $d$ Zeilen und $N$ Kästchen.
* **Der Schätzer.** $s_N(Y) = Y/N$, die normierten Zeilenlängen. Die Wahrscheinlichkeit ist $\mathrm{tr}(\rho^{\otimes N}P_Y) = \chi_Y(\rho)\dim S_Y$ mit dem Charakter $\chi_Y$ der $GL(d)$-Darstellung; Figur 1 zeigt die Verteilung für $d = 3$, $N = 120$, $r = (0.6, 0.3, 0.1)$, scharf um das wahre Spektrum.
* **Theorem.** Der Schätzer ist asymptotisch exakt, und für jede Menge $\Delta$ mit kleinem Rand gilt $\lim_N\frac1N\ln K_N(\Delta) = -\inf_{s\in\Delta}I(s)$ mit der Ratenfunktion $I(s) = \sum_j s_j(\ln s_j - \ln r_j)$, der relativen Entropie der Wahrscheinlichkeitsvektoren $s$ und $r$.
* **Beweisskizze.** Die Laplace-Transformierte $c(\eta) = \lim\frac1N\ln\int K_N(ds)e^{N\eta\cdot s}$ wird über Gewichte der Darstellung $\pi_Y$ abgeschätzt: $Y$ ist das höchste Gewicht, also $e^{Y\cdot h} \leq\chi_Y(\rho_h) \leq\dim(R_Y)e^{Y\cdot h}$ mit polynomiellem $\dim R_Y$; daraus $c(\eta) = \ln\sum_\alpha r_\alpha e^{\eta_\alpha}$, und Legendre-Transformation gibt $I$. Regularität nach Duffield und Gärtner–Ellis.

### Methodischer Ansatz

* Große Abweichungen für Tensorpotenzen von Gruppendarstellungen (Duffield 1990), erweitert von $\rho = I/d$ auf beliebiges $\rho$ durch den Faktor $\chi_Y(\rho)/\chi_Y(I)$.
* Die Ordnung $\rhd$ auf Gewichten (Zeilenlängen absteigend) macht $Y$ zum "schnellsten Exponentialterm"; das ist der Grund, warum gerade die Zeilenlängen das Spektrum schätzen.

### Bedeutung und Anwendungen

* Begründet Schur-Sampling als Messprimitive; O'Donnell und Wright (2015, 2016) und Haah et al. (2017) bauen die optimale Tomographie ($\Theta(d^2/\epsilon^2)$) und das Spektrumtesten darauf auf. Die Darstellungstheorie der symmetrischen Gruppe wurde damit zum Standardwerkzeug der Quantenstatistik.
* Die Ratenfunktion als relative Entropie verbindet Quantenstatistik mit Sanovs Theorem; die Autoren bemerken, dass es keinen direkten Weg zur i.i.d.-Theorie gibt.
* Ausblick auf einen Schätzer für den ganzen Dichteoperator: Young-Diagramm messen, dann kovariante Messung der Eigenbasis; genau das wurde die optimale Tomographie.

### Bezug zum eigenen Projekt

* Die Zeile markiert, was "Speicher $k = N$" kostet und kauft: optimale Raten, aber eine Messung über alle Kopien. Das eigene Protokoll steht mit $k = 2$ am anderen Ende, und die Frage "was ist mit $k$ zwischen zwei und $N$ erreichbar" (offene Frage 2 der Estimating-Sektion) hat hier ihren Endpunkt.
* Das Spektrum ist basisunabhängig, das Displacement-Spektrum basisabhängig; die Schur-Messung sieht die Eigenwerte, die Bell-Messung die Koeffizienten in einer festen Operatorbasis. Purity $\mathrm{tr}(\rho^2) = \sum r_j^2$ ist die eine Größe, die beide Messungen liefern (SWAP-Test als Zwei-Kopien-Schur-Messung); sie ist der Mixedness-Faktor der eigenen Taxonomie.
* Die Beweistechnik (höchstes Gewicht dominiert die Laplace-Transformierte) ist ein Muster für Konzentrationsaussagen über i.i.d. Bell-Samples, deren Verteilung ebenfalls eine Darstellungssumme ist.

### Grenzen und offene Fragen

* Keine Aussage über Optimalität bei endlichem $N$; die Autoren fanden für verschiedene Gütekriterien verschiedene Optimalschätzer, selten den hier vorgeschlagenen.
* Nur das Spektrum, nicht die Eigenbasis.
* Die Messung ist eine Schur-Transformation über $N$ Register, für Hardware nicht realistisch.

### Fragen zum Tieferbohren

* Was ist die Zwei-Kopien-Einschränkung der Schur-Messung ($N = 2$: symmetrischer und antisymmetrischer Unterraum), und wie hängt sie mit der Y-Parität der Bell-Basis zusammen (siehe Hangleiter–Gullans)?
* Wie sieht die Ratenfunktion für Schätzer aus, die nur $k$ Kopien zugleich verschränken, und interpoliert sie zwischen $I(s)$ und der Einzelkopien-Rate?
* Lässt sich aus dem Bell-Record auf $\rho\otimes\rho^*$ die Purity ablesen, und ist das die Schur-Statistik für $N = 2$ in anderer Basis?

Paper: [arXiv:quant-ph/0102027](https://arxiv.org/abs/quant-ph/0102027)

---

## Query-optimal estimation of unitary channels in diamond distance (arXiv:2302.14066)

Die Arbeit von **Jeongwan Haah, Robin Kothari, Ryan O'Donnell und Ewin Tang** (Microsoft, Google, CMU, Washington; FOCS 2023) löst die Prozesstomographie für Unitaries in der strengsten Metrik: Ein unbekanntes $Z \in U(d)$ wird mit $O(d^2/\epsilon)$ Anwendungen auf $\epsilon$ in Diamantnorm geschätzt, mit nur einem Qudit Speicher, und $\Omega(d^2/\epsilon)$ Anwendungen sind nötig, selbst mit Zugriff auf $Z^\dagger$ und kontrollierte Versionen. Vorher: $O(d^3/\epsilon^2)$ (Standard-Prozesstomographie) oder $O(d^{2.5}/\epsilon)$ (Yang, Renner, Chiribella über Normumrechnung). Die Technik ist ein Bootstrap, der Konstant-Fehler-Schätzungen zu Heisenberg-Skalierung hochzieht.

### Einordnung in die Tabellen

* **Task type:** Estimating mit $M = d^2$: nichts wird vorenthalten, zurück kommt $U$. Die Zeile "Unitary estimation in diamond distance".
* **Objekt:** Unitary. **Zugriff:** Query, Rung 3: adaptiv gewählte Zustände $V_2(ZV_1)^pV_0|0\rangle$, also Sequenzen von Anwendungen; kein Ancilla.
* **Status:** 🔴 🔴 🔴 in $n$: Queries buchen die Rate $1/\epsilon$, nicht die Dimension.
* **Versprechen:** keines; das ist die Query-Version der vollen Tomographie.

### Das Problem

Prozesstomographie ist in vielen Metriken studiert; die operationell natürliche, die Diamantnorm (Worst-Case über alle Eingaben inklusive Ancilla), war nicht direkt behandelt. Entanglement-Infidelity ist Average-Case und um bis zu $\sqrt d$ schwächer (Proposition 1.9: $4F \leq\Vert\cdot\Vert_\diamond^2 \leq 2dF$; die kontrollierte $C^kX$ hat Infidelity $O(2^{-k})$ zur Identität, aber Diamantabstand 1). Die "Storage-and-Retrieval"-Literatur (Bisio et al., Sedlák et al., Yang–Renner–Chiribella) optimiert Parallelstrategien in Infidelity mit Speicher in der Größe der Query-Zahl. Gesucht: Diamantnorm, Heisenberg-Rate, kein Speicheroverhead, und eine passende Untergrenze.

### Kernresultate

* **Theorem 1.1.** Ein Algorithmus mit $O(d^2/\epsilon)$ Queries, einem Qudit, $\mathrm{poly}(d, 1/\epsilon)$ Gattern und klassischer Zeit, Ausgabe $\hat Z$ mit $\mathbb{E}\Vert\mathcal{U}(\hat Z) - \mathcal{U}(Z)\Vert_\diamond^2 \leq\epsilon^2$; als gemischt-unitärer Kanal $\mathcal{M}$ sogar $\Vert\mathcal{M} - \mathcal{U}(Z)\Vert_\diamond \leq\epsilon^2$.
* **Theorem 1.2.** Jeder Algorithmus mit Orakeln für $Z, Z^\dagger, cZ, cZ^\dagger$ und Fehler $\epsilon < 1/8$ braucht $\Omega(d^2/\epsilon)$ Queries: die erste gemeinsam optimale Untergrenze, für jede Funktion $\epsilon = \phi(d)$ scharf.
* **Theorem 2.1 (Basisalgorithmus).** Standard-Prozesstomographie mit Sorgfalt gibt $O(d^2/\epsilon^2)$: Zustandstomographie der Spalten $Z|i\rangle$ mit Haar-zufälligem Fehler (keine Kumulation zu $\sqrt d\epsilon$), relative Phasen aus den Spalten von $Z$ und $ZF$ mit der Fourier-Matrix $F$ (Proposition 2.3).
* **Lemma 3.1 (Wurzeln).** Sind $U, V$ $\alpha$-nahe in Diamantnorm und beide $0.01$-nahe an der Identität, dann sind $U^{1/p}, V^{1/p}$ $50\alpha/p$-nahe.
* **Theorem 3.3 (Bootstrap, Algorithmus 1).** Aus einem Basisalgorithmus mit Fehler $1/200$ wird ein Algorithmus mit Fehler $\epsilon$ bei $1/\epsilon$-fachem Query-Overhead: Schätze $(ZV_j^\dagger)^{2^j}$ mit konstantem Fehler, wobei $V_j$ die bisherige Schätzung ist ("shift to identity"), und ziehe Wurzeln.
* **Vergleich.** Yang–Renner–Chiribella: $O(d^2/\sqrt\delta)$ in Infidelity, parallel, Speicher $\Theta(d^2\log d/\sqrt\epsilon)$; van Apeldoorn et al.: $O(d^2/\epsilon\cdot\log)$ mit $cZ, cZ^\dagger$ und $\Theta(d\log)$ Speicher. Der neue Algorithmus braucht nur $Z$ und keinen Speicher.

### Methodischer Ansatz

* **Warmup** (Fig. 1): Für $Z = \mathrm{diag}(1, e^{i\phi})$ liefern Konstant-Fehler-Schätzungen von $Z^{2^k}$ die Bits von $\phi$; das ist inkohärente Phasenschätzung (robust phase estimation). Für allgemeine $Z$ scheitert das, wenn Eigenwerte nahe $-1$ liegen (Potenzen von $\pm1$ verraten nichts über Eigenvektoren); Lemma 3.1 verlangt daher Nähe zur Identität, und das Recentering $ZV_j^\dagger$ stellt sie her.
* **Untergrenze:** Kombination von Unitary-Channel-Discrimination (Bavaresco et al.) mit einer Reduktionstechnik aus der Quantenquery-Komplexität, angepasst von diagonalen auf allgemeine Unitaries.
* Median-Trick (Proposition 2.4) für Erfolgswahrscheinlichkeit $1-\eta$ bei $O(\log 1/\eta)$ Overhead; Diskretisierung per Solovay–Kitaev für endliche Präzision.

### Bedeutung und Anwendungen

* Schließt die Unitary-Tomographie in Diamantnorm ab: $\Theta(d^2/\epsilon)$ ist optimal in Queries und im Speicher.
* Qualitativ nahe an Gate Set Tomography, das Heisenberg-Skalierung durch lange Gattersequenzen erreicht; das Paper gibt dafür erstmals eine theoretische Schranke in einem verwandten Modell.
* Der Bootstrap ist ein allgemeines Werkzeug: Konstant-Fehler-Schätzer plus Wurzelziehen plus Recentering gibt Heisenberg-Rate für Objekte auf einer Lie-Gruppe.

### Bezug zum eigenen Projekt

* Die Zeile zeigt, was Query-Zugriff *nicht* kauft: die Dimension. Für die Estimating-Spalte gilt: Query verbessert $1/\epsilon^2$ zu $1/\epsilon$, Sparsity oder Rang verbessern $d^2$; beides zusammen ist die Frage nach effizienter Unitary-Schätzung unter Strukturversprechen (Low-Degree bei Arunachalam et al., Juntas bei Chen–Nadimpalli–Yuen).
* Das Recentering "shift to identity" ist konzeptionell dasselbe wie der Hypothesenzustand von King, Wan, McClean und der Probe-Zustand von Phase 2: Man verschiebt das Unbekannte in eine Umgebung, in der die Messung linear und informativ ist. Die Querverbindung zwischen "Residuum lernen" (auch bei Bakshi et al. und Shin, Lee, Oh) und "Vorzeichen per Probe" ist ein gemeinsames Muster.
* Die Unterscheidung Average-Case (Infidelity) gegen Worst-Case (Diamant) ist dieselbe wie zwischen PAC-Garantie und "alle $M$"-Garantie und sollte in der eigenen Skalierungsanalyse benannt werden: Top-$k$-Genauigkeit im Mittel über Instanzen ist Average-Case.

### Grenzen und offene Fragen

* Die Konstanten ($1/200$, $0.01$) sind unoptimiert.
* Gatterkomplexität $\mathrm{poly}(d, 1/\epsilon)$; wie klein sie sein kann, ist nicht untersucht.
* Nur Unitaries; allgemeine Kanäle in Diamantnorm bleiben bei $1/\epsilon^2$-artigen Raten.
* Keine Robustheit gegen Rauschen in $Z$ selbst.

### Fragen zum Tieferbohren

* Wie sieht Lemma 3.1 für die Heisenberg–Weyl-Gruppe aus, wo $D_{q,p}^d = I$ und Potenzen periodisch sind?
* Lässt sich der Bootstrap auf die Schätzung einer *Präparationsunitary* mit Sparsity im Displacement-Spektrum des präparierten Zustands übertragen, und was ist dann das Analogon von $d^2$?
* Warum reichen $Z$-Queries ohne Kontrolle, während van Apeldoorn et al. $cZ$ brauchen, und gilt dasselbe für Amplitudenschätzung im eigenen Query-Regime?

Paper: [arXiv:2302.14066](https://arxiv.org/abs/2302.14066)

---

## Improved machine learning algorithm for predicting ground state properties (arXiv:2301.13169)

Die Arbeit von **Laura Lewis, Hsin-Yuan Huang, Viet T. Tran, Sebastian Lehner, Richard Kueng und John Preskill** (Caltech, JKU Linz, AWS; *Nature Communications* 15, 895 (2024)) verbessert den beweisbaren ML-Algorithmus für Grundzustandseigenschaften in gapped Phasen von Huang, Kueng, Torlai, Albert und Preskill (Science 2022) dramatisch: statt $O(n^c)$ Trainingsdaten mit großem $c$ und $n^{O(1/\epsilon)}$ in der Genauigkeit reichen $N = \log(n/\delta)\,2^{\mathrm{polylog}(1/\epsilon)}$ Datenpunkte, Training und Vorhersage laufen in $O(n\log n)$, und die Verteilung über Parameter darf beliebig sein. Der Preis: Die Geometrie des Systems muss bekannt sein, und sie wird als induktiver Bias in eine Feature-Map eingebaut.

### Einordnung in die Tabellen

* **Task type:** Estimating mit Generalisierung. Gegeben Daten $(x_\ell, y_\ell \approx\mathrm{Tr}(O\rho(x_\ell)))$ für Hamiltonians $H(x)$ derselben Phase, zurück kommt $\mathrm{Tr}(O\rho(x))$ an neuen $x$. Die Zeile "Ground-state properties across a phase from shadows".
* **Objekt:** Familie von Grundzuständen $\rho(x)$ eines geometrisch lokalen gapped Hamiltonians $H(x) = \sum_j h_j(\vec x_j)$, $x\in[-1,1]^m$. **Zugriff:** klassische Daten; mit Classical Shadows der Trainingszustände (Corollary 1) auch Sample-Zugriff mit $T = \tilde O(\log n/\epsilon^2)$ Messungen pro Zustand.
* **Status:** 🟢 🟢 🟢: Daten logarithmisch, Zeit fast linear, Speicher das Gewicht $w^*$ der Dimension $m_\varphi = O(n)\cdot(1 + 2/\delta_2)^{\mathrm{poly}(\delta_1)}$.
* **Versprechen:** Gap, geometrische Lokalität von $H$ und $O$ (Summe geometrisch lokaler Terme mit $\Vert O\Vert_\infty \leq 1$), bekannte Geometrie; die $x_\ell$ aus einer beliebigen unbekannten Verteilung $\mathcal{D}$.

### Das Problem

Der Vorgänger zeigte, dass ein klassischer ML-Algorithmus mit polynomiell vielen Daten Grundzustandseigenschaften über eine Phase vorhersagen kann, und dass das ohne Daten unter Standardannahmen unmöglich ist. Aber $n^c$ mit großem $c$, $n^{O(1/\epsilon)}$ in $\epsilon$ und nur die Gleichverteilung über $[-1,1]^m$ sind praktisch unbrauchbar. Die Untergrenze $N = n^{\Omega(1/\epsilon)}$ aus dem Vorgänger gilt ohne Kenntnis der Geometrie; also ist Geometrie die Zusatzinformation, die nötig ist.

### Kernresultate

* **Theorem 1.** Mit $N = \log(n/\delta)\,2^{\mathrm{polylog}(1/\epsilon)}$ Trainingspunkten aus beliebigem $\mathcal{D}$ und $|y_\ell - \mathrm{Tr}(O\rho(x_\ell))| \leq\epsilon$ liefert LASSO über der Feature-Map $\varphi$ eine Funktion $h^* = w^*\cdot\varphi$ mit $\mathbb{E}_{x\sim\mathcal{D}}|h^*(x) - \mathrm{Tr}(O\rho(x))|^2 \leq\epsilon$, Wahrscheinlichkeit $1-\delta$, Zeit $O(nN)$. Bei $\epsilon = \Theta(1)$: $N = O(\log n)$.
* **Corollary 1.** Mit Classical Shadows $\sigma_T(\rho(x_\ell))$ aus $T = \tilde O(\log n/\epsilon^2)$ zufälligen Pauli-Messungen lernt derselbe Algorithmus eine Grundzustandsdarstellung $\hat\rho_{N,T}(x)$ mit derselben Garantie für *alle* Summen geometrisch lokaler Observablen zugleich.
* **Theorem 2 (Pauli-1-Norm).** Für Summen geometrisch lokaler Observablen gilt $\sum_Q|\alpha_Q| \leq C\Vert O\Vert_\infty$: Die $\ell_1$-Norm der Pauli-Koeffizienten ist durch die Operatornorm beschränkt, eine Aussage, die für die $\ell_2$-Norm trivial ist und für $\ell_1$ neu.
* **Proposition 1 (Härte ohne Daten).** Ein randomisierter Polynomialzeit-Algorithmus ohne Daten, der für alle glatten Familien gapped 2D-Hamiltonians Ein-Qubit-Eigenschaften im Mittel auf konstanten Fehler berechnet, löst NP-vollständige Probleme.
* **Numerik.** 2D antiferromagnetische zufällige Heisenberg-Modelle bis $9\times 5 = 45$ Qubits mit Random-Fourier-Features; Fehler fällt mit $N$ und $T$ und hängt kaum von $n$ ab; die gelernten Gewichte nutzen die lokale Geometrie (Fig. 2B).

### Methodischer Ansatz

1. **Lokale Zerlegung per Spectral Flow.** $\mathrm{Tr}(O\rho(x)) \approx\sum_{P\in S^{(\mathrm{geo})}}f_P(x)$ mit $f_P(x) = \alpha_P\mathrm{Tr}(P\rho(\chi_P(x)))$, wobei $\chi_P$ alle Koordinaten außerhalb der Umgebung $I_P$ (Radius $\delta_1 = \Theta(\log^2(1/\epsilon))$) auf null setzt; Fehler $O(\epsilon)$ wegen exponentiell zerfallender Korrelationen in gapped Grundzuständen.
2. **Diskretisierung.** Jedes glatte $f_P$ wird auf einem Gitter $X_P$ der Schrittweite $\delta_2 = \Theta(1/\epsilon)$ über den Koordinaten in $I_P$ durch Indikatorfunktionen verdickter affiner Unterräume $T_{x',P}$ approximiert; das definiert die Feature-Map $\varphi(x)_{x',P} = \mathbb{1}[x\in T_{x',P}]$.
3. **LASSO mit $\Vert w\Vert_1 \leq B$.** Es existiert $w'$ mit Trainingsfehler $\leq 0.53\epsilon$ und $\Vert w'\Vert_1 \leq C\Vert O\Vert_\infty(1 + 2/\delta_2)^{\mathrm{poly}(\delta_1)} = 2^{\mathrm{polylog}(1/\epsilon)}$ (Theorem 2 liefert die Schranke); Standard-Generalisierungstheorie gibt $\mathbb{E}|h^* - \mathrm{Tr}(O\rho)|^2 \leq$ Trainingsfehler $+ O(B\sqrt{\log(m_\varphi/\delta)/N})$, also $N = O(\log(n/\delta)2^{\mathrm{polylog}(1/\epsilon)})$.

### Bedeutung und Anwendungen

* Macht den beweisbaren ML-Zugang praktisch: logarithmische Daten, fast lineare Zeit, beliebige Verteilung. Zusammen mit Onorati et al. (die Worst-Case-Garantien und thermische Phasen liefern) der Stand der Technik für "Lernen über eine Phase".
* Die Pauli-1-Norm-Schranke ist unabhängig nützlich; verwandte Ungleichungen in Huang, Chen, Preskill (Corollary 4 dort) mit anderen Techniken.
* Die Härteaussage zeigt die "Power of Data": Daten sind eine Ressource, die NP-Härte umgeht.

### Bezug zum eigenen Projekt

* Das ist der beweisbare gelernte Decoder der Tabellen und die nächste Verwandtschaft zum eigenen CNN: eine Feature-Map mit induktivem Bias (Geometrie hier, Coprime-Folding dort), ein linearer Lerner darüber, und eine Garantie, die aus der Struktur der Zielfunktion folgt. Der Unterschied: Hier ist die Zielfunktion beweisbar glatt und lokal, dort ist die Struktur (Top-$k$-Träger im Displacement-Spektrum) eine Conjecture.
* Die Untergrenze $n^{\Omega(1/\epsilon)}$ *ohne* Geometrie gegen $\log n$ *mit* Geometrie ist das sauberste Beispiel dafür, wie ein Versprechen den Exponenten ändert; für das eigene Projekt ist die Frage, welches Zusatzwissen (Dictionary, Untergruppe, Gap) dieselbe Rolle spielt.
* Objective 4 des Projekts (Grundzustände, Gibbs-Zustände) trifft genau die Zustandsfamilien dieses Papers; die numerische Vorlage (2D-Heisenberg, 45 Qubits, RMSE gegen $N$, $T$, $n$) ist übernehmbar.

### Grenzen und offene Fragen

* $2^{\mathrm{polylog}(1/\epsilon)}$ ist quasi-polynomiell in $1/\epsilon$; polynomiell ist offen.
* Bekannte Geometrie ist nötig; ohne sie gilt die Untergrenze des Vorgängers.
* Nur gapped Grundzustände; thermische Phasen und kritische Punkte bei Onorati et al.
* Garantie im Mittel über $\mathcal{D}$, nicht punktweise.

### Fragen zum Tieferbohren

* Wie sieht die Feature-Map für Displacement-Observablen aus, deren "Geometrie" der Phasenraum $(q,p)$ ist: Was ersetzt $d_{\mathrm{qubit}}$, und ist $S^{(\mathrm{geo})}$ dann das Dictionary?
* Gilt Theorem 2 (Pauli-1-Norm) für Summen von Displacement-Operatoren mit beschränkter Operatornorm, und was folgt für die $\ell_1$-Norm des Displacement-Spektrums eines Grundzustands?
* Kann man die Spectral-Flow-Lokalität nutzen, um zu zeigen, dass Grundzustände lokaler Hamiltonians ein *sparsames* Displacement-Spektrum in einer geeigneten Basis haben?

Paper: [arXiv:2301.13169](https://arxiv.org/abs/2301.13169)

---
## Efficient learning of ground & thermal states within phases of matter (arXiv:2301.12946)

Die Arbeit von **Emilio Onorati, Cambyse Rouzé, Daniel Stilck França und James D. Watson** (TU München, ENS Lyon, Maryland; 2023) behandelt zwei Aufgaben: (a) Tomographie eines einzelnen Gibbs-Zustands bis auf Wasserstein-Distanz $n\epsilon$ aus $\mathrm{polylog}(n)$ Kopien, was alle Lipschitz-Observablen, also alle extensiven Größen inklusive Entropien, zugleich liefert; (b) Lernen lokaler Observablen über eine ganze thermische oder Grundzustandsphase aus $N = O(\log(M/\delta)e^{\mathrm{polylog}(1/\epsilon)})$ Samples mit *Worst-Case*-Garantie über den Parameterraum. Gegenüber Huang, Kueng, Torlai, Albert, Preskill ist das eine exponentielle Verbesserung in $\epsilon$, eine Erweiterung auf thermische Phasen, und punktweise statt gemittelte Garantien.

### Einordnung in die Tabellen

* **Task type:** Estimating, in zwei Varianten. Bei (a) ist die Liste "alle Lipschitz-Observablen" implizit und exponentiell, der Output eine Parametrisierung $x_0$ des Gibbs-Zustands. Bei (b) sind $M$ lokale Observablen gegeben, zurück kommen ihre Werte für alle $x$ der Phase. Zeilen "Ground-state properties across a phase" und, für (a), ein Zusatz zur Gibbs-Zeile.
* **Objekt:** Gibbs-Zustände $\sigma(\beta, x) = e^{-\beta H(x)}/\mathrm{tr}$ und Grundzustände $\psi_g(x)$ lokaler Hamiltonians auf einem $D$-dimensionalen Gitter. **Zugriff:** Sample, Einzelkopien, Classical Shadows der Trainingszustände.
* **Status:** 🟢 🟢 🟢. Kopien $\mathrm{polylog}(n)$; die Zeitkomplexität erbt die der eingesetzten Hamiltonian-Lerner (Anshu et al. für kommutierende Modelle, Haah–Kothari–Tang bei hoher Temperatur).
* **Versprechen:** exponentieller Korrelationszerfall (Gl. II.2) für (a) und thermische Phasen in (b); für Grundzustände GALI, generalisierte approximative lokale Ununterscheidbarkeit, die gapped Phasen einschließt; für (b) zusätzlich eine anti-konzentrierte Verteilung über $x$ (etwa die Gleichverteilung).

### Das Problem

Shadows lernen lokale Observablen mit $\log n$ Kopien, aber exponentiell in der Trägergröße; Hamiltonian-Lernen aus Gibbs-Zuständen (Anshu et al., Haah et al.) rekonstruiert die Parameter, aber Spurdistanz-Garantien kosten polynomiell in $n$. Rouzé und França hatten beides über Transportkostenungleichungen verbunden, jedoch nur für topologisch triviale Zustände (kommutierende Hochtemperatur-Gibbs-Zustände, flache Schaltkreise). Für das Lernen über Phasen hatte HKTAP exponentielle $\epsilon$-Abhängigkeit, nur gapped Grundzustände und nur Garantien im Mittel.

### Kernresultate

* **Theorem II.3 (Gibbs-Tomographie).** Für kommutierende Gibbs-Zustände mit exponentiellem Korrelationszerfall liefern $N = O(\log(\delta^{-1})\mathrm{polylog}(n)\epsilon^{-2})$ Kopien ein $x_0$ mit $W_1(\sigma(\beta,x), \sigma(\beta,x_0)) \leq n\epsilon$; nichtkommutierend bei $\beta < \beta_c$ ebenso, und unter uniformem Clustering plus approximativer Markov-Eigenschaft mit $\epsilon^{-4}$.
* **Stetigkeitsschranke (Gl. II.4).** $W_1(\sigma(\beta,x), \sigma(\beta,y)) = \Vert x - y\Vert_{\ell_1}O(\mathrm{polylog}\,n)$, scharf bis auf den Polylog bei $\beta = \Theta(1)$; Beweis über Quanten-Belief-Propagation. Damit reduziert sich $W_1$-Rekonstruktion auf $\ell_1$-Parameterlernen.
* **Corollary II.4 (Entropien).** Von-Neumann-Entropie, bedingte Entropie, wechselseitige und bedingte wechselseitige Information beliebig großer Regionen ändern sich nur um $\Vert x|_{S(r_S)} - y|_{S(r_S)}\Vert_{\ell_1}\mathrm{polylog}$, also sind sie aus der Parameterschätzung mit multiplikativem Fehler ablesbar; Shadows brauchen dafür exponentiell in der Region.
* **Theorem II.5 (Lernen in thermischen Phasen).** Mit $N = O(\log(M/\delta)\log(n/\delta)e^{\mathrm{polylog}(\epsilon^{-1})})$ Samples $(x_i, \tilde\sigma(\beta,x_i))$ aus der Gleichverteilung über $\Phi$ gibt es einen Schätzer mit $\sup_{x\in\Phi}|f_O(x) - \hat f_O(x)| \leq\epsilon\sum_i\Vert O_i\Vert_\infty$ für lokale $O = \sum_i O_i$.
* **Theorem II.7 (GALI).** Dieselbe Garantie für Familien von Grund- oder Gibbs-Zuständen mit generalisierter approximativer lokaler Ununterscheidbarkeit (Definition II.6): Für jede Region $S$ und Radius $r$ gibt es Parameter außerhalb von $S(r)$, deren Wahl die Erwartungswerte auf $S$ nur um $(|S|f(r) + \eta(S))\Vert O\Vert_\infty$ ändert; gapped Grundzustandsphasen erfüllen das (Lieb–Robinson, Spectral Flow).

### Methodischer Ansatz

* **Wasserstein statt Spurdistanz.** Lipschitz-Observablen $\Vert L\Vert_{\mathrm{Lip}} = \max_i\min_{L_{i^c}}2\Vert L - L_{i^c}\otimes I_i\Vert_\infty$ und die duale Distanz $W_1$; $W_1 = O(\epsilon n)$ ist für extensive Observablen dasselbe wie multiplikative Genauigkeit $\epsilon$, kostet aber exponentiell weniger als Spurdistanz $O(\epsilon)$ (schon für Produktzustände).
* **$W_1$-starke Konvexität** der Log-Zustandssumme, die linear in $n$ skaliert unter Clustering und Markov-Bedingung, als Verallgemeinerung der $\ell_2$-Konvexität bei Anshu et al.
* **Lernen in der Phase.** Trainingspunkte $Y_1, \dots, Y_N$ gleichverteilt; für jede Observable $O_i$ mit Träger $S_i$ werden die Shadows der $t\approx\log n$ Trainingszustände gemittelt, deren *lokale* Parameter nahe $x$ liegen; Belief Propagation zeigt, dass lokale Erwartungswerte bei exponentiellem Korrelationszerfall glatt in den lokalen Parametern sind. Anti-Konzentration der Verteilung garantiert, dass jede kleine Parameterregion genug Trainingspunkte enthält. Das ist Konzentration des Maßes, nicht ML im engeren Sinn.

### Bedeutung und Anwendungen

* Zusammen mit Lewis et al. der Stand der Technik für "Lernen über eine Phase": Lewis et al. haben $O(\log n)$ Daten für beliebige Verteilungen im Mittel, Onorati et al. Worst-Case-Garantien für anti-konzentrierte Verteilungen und thermische Phasen; beide sind quasi-polynomiell in $1/\epsilon$.
* Corollaries C.4 und C.6 sind auch klassisch neu ($W_1$-Lernen von Gibbs-Maßen); es gibt klassische Ising-Phasen mit Korrelationszerfall, aber ohne bekannten Sampler, und die Resultate gelten trotzdem.
* Robuste Shadow-Tomographie-Algorithmen für Gibbs- und Grundzustände und Gibbs-Approximationen lokal ununterscheidbarer Grundzustände sind Werkzeuge von eigenem Wert.

### Bezug zum eigenen Projekt

* Für Objective 4 (Gibbs- und Grundzustände) ist das die Aussage, dass diese Zustandsklassen *als Klassen* mit $\mathrm{polylog}(n)$ Kopien vollständig beschrieben werden können, sobald Korrelationen exponentiell zerfallen. Die Frage für das eigene Projekt ist, ob dieselbe Struktur ein sparsames Displacement-Spektrum impliziert, und die Stetigkeitsschranke Gl. II.4 ist ein Werkzeug, um Sparsity entlang einer Phase zu verfolgen.
* Die Unterscheidung "im Mittel" gegen "punktweise" ist dieselbe, die im eigenen Paper zwischen Skalierung über Instanzverteilungen und Garantie für jede Instanz zu treffen ist; das Paper zeigt, dass der Preis für punktweise Garantien eine Anti-Konzentrationsbedingung ist, kein Verlust in $n$.
* Der Mixedness-Faktor der eigenen Taxonomie wird hier durch $\beta$ gesteuert; die Tabelle der Bedingungen (kommutierend, Hochtemperatur, Markov, GALI) ist eine Vorlage für die Instanzenleiter.

### Grenzen und offene Fragen

* Anti-Konzentration ist nötig; Verteilungen mit großen Regionen kleiner Wahrscheinlichkeit sind ausgeschlossen (Anhang D).
* Für nichtkommutierende Gibbs-Zustände außerhalb des Hochtemperaturregimes hängt alles an Clustering plus Markov, das für viele Modelle vermutet, nicht bewiesen ist.
* $e^{\mathrm{polylog}(1/\epsilon)}$ in der Genauigkeit.
* Die Zeitkomplexität wird nicht separat bewiesen, sondern geerbt.

### Fragen zum Tieferbohren

* Ist $\Vert D_{q,p}\Vert_{\mathrm{Lip}}$ auf einem Qudit-Gitter beschränkt, und was sagt $W_1$-Nähe über die Displacement-Spektren zweier Gibbs-Zustände?
* Wie sieht die approximative Markov-Bedingung in der Displacement-Basis aus, und impliziert sie eine Faktorisierung des Spektrums, die ein Best-First-Decoder nutzen könnte?
* Lässt sich GALI als Versprechen für die Instanzenleiter operationalisieren, also messen, ohne den Hamiltonian zu kennen?

Paper: [arXiv:2301.12946](https://arxiv.org/abs/2301.12946)

---

## Learning to predict arbitrary quantum processes (arXiv:2210.14894)

Die Arbeit von **Hsin-Yuan Huang, Sitan Chen und John Preskill** (Caltech, Berkeley, AWS; *PRX Quantum* 4, 040337 (2023)) gibt einen effizienten ML-Algorithmus, der für einen *beliebigen* unbekannten $n$-Qubit-Prozess $\mathcal{E}$, auch einen mit exponentiell vielen Gattern, jede lokale Eigenschaft $\mathrm{tr}(O\mathcal{E}(\rho))$ des Outputs vorhersagt, mit kleinem mittleren Fehler über Inputzustände $\rho$ aus einer *lokal flachen* Verteilung, nach Training auf $N = O(\log n)$ Experimenten mit zufälligen Produktzuständen und zufälligen Pauli-Messungen. Der Beweis liefert eine Quanten-Bohnenblust–Hille-Ungleichung über einen verbesserten Optimierungsalgorithmus für lokale Hamiltonians.

### Einordnung in die Tabellen

* **Task type:** Estimating, Average Case über Inputs. Gegeben: Zugriff auf $\mathcal{E}$, eine Familie beschränkten Grades von Observablen $O$, eine Verteilung $\mathcal{D}$; zurück kommt $h(\rho, O)\approx\mathrm{tr}(O\mathcal{E}(\rho))$. Die Zeile "Predicting arbitrary quantum processes".
* **Objekt:** Kanal. **Zugriff:** Sample im Sinne der Tabellen: nicht-adaptive Anwendung auf zufällige Produktzustände mit Einzelkopien-Pauli-Messungen, also der Input–Output-Datenzustand; die Autoren nennen es Zugriff auf $\mathcal{E}$, aber nichts wird adaptiv oder in Superposition gewählt.
* **Status:** 🟢 🟢 🟢 für konstantes $\epsilon$: $N = \log n\cdot\min(2^{O(\log(1/\epsilon)(\log\log(1/\epsilon) + \log(1/\epsilon')))}, 2^{O(\log(1/\epsilon)\log n)})$, Zeit $O(kn^kN)$ mit $k = \Theta(\log 1/\epsilon)$; also $n^{O(\log 1/\epsilon)}$ bei $\epsilon' = 0$.
* **Versprechen:** lokal flache Verteilung $\mathcal{D}$ (invariant unter Ein-Qubit-Cliffords auf jedem Qubit) und Observablen beschränkten Grades ($O(1)$ Terme pro Qubit, $\Vert O\Vert \leq 1$). Kein Versprechen über $\mathcal{E}$.

### Das Problem

Ein CPTP-Kanal hat exponentiell viele Parameter; Covering-Argumente, Shadow Tomography und Prozesstomographie brauchen exponentiell viele Daten für beliebige $\mathcal{E}$ und $\rho$. Für polynomiell erzeugbare $\mathcal{E}$ reichen polynomiell viele Daten, aber die Rechenzeit bleibt exponentiell. Gesucht: ein Algorithmus, der beliebige $\mathcal{E}$ effizient lernt, wenn man den Fehler im Mittel über eine sinnvolle Inputverteilung misst.

### Kernresultate

* **Theorem 1.** Mit $N = O(\log n)$ Trainingsdaten $S_N(\mathcal{E})$ (Produkt-Stabilizerzustände als Input, randomisierte Pauli-Messung am Output, $O(nN)$ Bits) lernt der Algorithmus $h(\rho, O)$ mit $\mathbb{E}_{\rho\sim\mathcal{D}}|h(\rho,O) - \mathrm{tr}(O\mathcal{E}(\rho))|^2 \leq\epsilon + \max(\Vert O'\Vert^2, 1)\epsilon'$ für jede lokal flache $\mathcal{D}$ und jedes $O$ beschränkten Grades, $O'$ die Grad-$k$-Trunkierung der Heisenberg-Evolution $\mathcal{E}^\dagger(O)$.
* **Lernen von Zuständen (Abschnitt II.A).** Verbesserte Shadow-Norm: alle Observablen beschränkten Grades mit $\Vert O\Vert\leq B$ aus $N = O(\log(n)B^2/\epsilon^2)$ zufälligen Pauli-Messungen (vorher $O(n\log n\,B^2/\epsilon^2)$), mit passender Untergrenze auch für kollektive Messungen.
* **Lernen von Observablen (II.B).** Unter lokal flachen $\mathcal{D}$ ist die Grad-$k$-Trunkierung $O^{(k)}$ von $O$ mit $\Vert O\Vert = O(1)$ bis auf $e^{-\Omega(k)}$ genau (Lemma 14); es genügt, wenige große Koeffizienten zu lernen; Training auf der festen Verteilung $\mathcal{D}'$ (zufällige Produkt-Stabilizerzustände) reicht für alle lokal flachen $\mathcal{D}$.
* **Corollaries 1 und 2 (Optimierung).** Randomisierte Algorithmen in $O(n^k)$ bzw. $O(nd)$ finden Produktzustände mit Energie um $C(k)(\sum|\alpha_P|^{2k/(k+1)})^{(k+1)/2k}$ bzw. $\frac{C}{\sqrt d}\sum|\alpha_P|$ über oder unter dem Haar-Mittel, $C(k) = 1/\exp(\Theta(k\log k))$, per Polarisation statt Random Restriction.
* **Corollaries 3 und 4 (Normungleichungen).** $\frac13C(k)\Vert H\Vert_{\mathrm{Pauli},2k/(k+1)} \leq\Vert H\Vert$ für $k$-lokale $H$ (beweist die Vermutung von Rouzé, Wirth, Zhang zur Quanten-Bohnenblust–Hille-Ungleichung) und $\frac13C(k,d)\Vert H\Vert_{\mathrm{Pauli},1} \leq\Vert H\Vert$ für beschränkten Grad $d$.
* **Numerik.** Vorhersage von Quantendynamik mit Evolutionszeit bis $10^6$ und 50 Qubits.

### Methodischer Ansatz

1. **Reduktion.** $\mathrm{tr}(O\mathcal{E}(\rho)) = \mathrm{tr}(\mathcal{E}^\dagger(O)\rho)$: Der Output $\mathcal{E}(\rho_\ell)$ ist ein unbekannter Zustand (Shadows lernen ihn für beschränkten Grad), und $\mathcal{E}^\dagger(O)$ ist eine unbekannte Observable (Low-Degree-Lernen über lokal flache Verteilungen). Beides zusammen lernt den Prozess.
2. **Algorithmus (III.A).** Empirische Pauli-Koeffizienten $\hat x_P(O)$ aus den Daten für alle $|P|\leq k$, Schwellenwert $\hat\alpha_P = 3^{|P|}\hat x_P$ falls groß, sonst $0$; Vorhersage $h(\rho,O) = \sum_P\hat\alpha_P\mathrm{tr}(P\rho)$ aus den $k$-RDMs von $\rho$, die klassisch oder per Shadows vorliegen.
3. **Normungleichungen aus Optimierung.** Ein Zustand mit Energie deutlich über dem Haar-Mittel beweist eine Untergrenze an $\Vert H\Vert$ in Termen der Pauli-Koeffizienten; Polarisation (Qubits replizieren, alle bis auf die letzte Replika zufällig fixieren, letzte optimieren, mit Zufallsvorzeichen mitteln) liefert die Bohnenblust–Hille-Form.

### Bedeutung und Anwendungen

* Beliebige Prozesse werden im Average Case lernbar; der Kontrast zu Prozesstomographie und zum Worst Case ist die Aussage der "Power of Data".
* Die Quanten-Bohnenblust–Hille-Ungleichung mit Konstante $\exp(\Theta(k\log k))$ ist unabhängig wichtig; Klein, Slote, Volberg, Zhang übertragen sie auf Qudits, Arunachalam et al. auf Kanäle.
* Die observablenzentrierte Sicht auf Shadows (Lemma 1.10 bei Bakshi et al.) stammt hierher.

### Bezug zum eigenen Projekt

* Die Trunkierungsaussage "unter lokal flachen Verteilungen ist $\mathcal{E}^\dagger(O)$ effektiv low-degree" ist ein Mechanismus, der ein *implizites* Sparsity-Versprechen erzeugt: Nicht der Prozess ist sparsam, sondern das, was die Inputverteilung von ihm sieht. Für die eigene Conjecture ist das ein Vorbild dafür, dass Average-Case-Decodierbarkeit aus der Instanzverteilung kommen kann, nicht aus dem Zustand allein.
* Das Schwellenwertverfahren (große Koeffizienten behalten, kleine nullen) ist der Eskenazis–Ivanisvili-Decoder und die algorithmische Form von "Top-$k$"; die Bohnenblust–Hille-Ungleichung ist die Garantie, dass es funktioniert. Die analoge Ungleichung für Displacement-Koeffizienten wäre der beweisbare Kern des eigenen Dictionary-Regimes.
* $n^{O(\log 1/\epsilon)}$ ist quasi-polynomiell: Die Zeit skaliert mit der Zahl der Kandidaten $n^k$, was der Enumerationsstrategie des Dictionary-Regimes entspricht.

### Grenzen und offene Fragen

* Quasi-polynomielle Zeit in $1/\epsilon$; für kleine Fehler unpraktisch.
* Lokal flache Verteilungen sind eine starke Annahme über die Inputs; für Inputs aus einem festen Experiment ohne Randomisierung gilt nichts.
* Die Optimierungsalgorithmen können nicht wählen, ob sie maximieren oder minimieren.
* Keine Aussage über den Worst Case über Inputs.

### Fragen zum Tieferbohren

* Was ist eine "lokal flache" Verteilung über Qudit-Zustände, wenn die lokale Gruppe die Heisenberg–Weyl-Gruppe statt der Clifford-Gruppe ist, und gilt Lemma 14 dann für Displacement-Grad?
* Wie sieht die Polarisationstechnik für Displacement-Hamiltonians $\sum_{q,p}\alpha_{q,p}(D_{q,p} + D_{q,p}^\dagger)$ aus, und welche Bohnenblust–Hille-Konstante ergibt sich?
* Kann das eigene CNN als Lerner von $\mathcal{E}^\dagger(O)$ gelesen werden, wenn $\mathcal{E}$ die Präparation des Zustands aus einem Referenzzustand ist?

Paper: [arXiv:2210.14894](https://arxiv.org/abs/2210.14894)

---

## Learning low-degree quantum objects (arXiv:2405.10933)

Die Arbeit von **Srinivasan Arunachalam, Arkopal Dutt, Francisco Escudero Gutiérrez und Carlos Palazuelos** (IBM Quantum, QuSoft/CWI, UCM/ICMAT; 2024) lernt Quantenobjekte mit niedrigem Pauli-Grad $d$ bis auf $\ell_2$-Fehler $\epsilon$: Kanäle und Unitaries mit $\exp(\tilde O(d^2 + d\log 1/\epsilon))$ Queries, unabhängig von $n$; Polynome aus $d$-Query-Quantenalgorithmen klassisch aus $O((1/\epsilon)^d\log n)$ Zufallsbeispielen, also auch für $d = O(\log n)$; Grad-$d$-Polynome aus $O(1/\epsilon^d)$ Queries an eine Block-Encoding. Technischer Kern sind neue Bohnenblust–Hille-Ungleichungen: für vollständig beschränkte Tensoren mit Konstante $1$, für Kanäle mit Konstante $\exp(d)$.

### Einordnung in die Tabellen

* **Task type:** Estimating. Gegeben ist die implizite Liste aller Pauli-Koeffizienten bis Grad $d$, zurück kommen sie alle. Die Zeile "Low-degree quantum objects" der Estimating-Tabelle; die Tabelle nennt daneben Volberg–Zhang (2023) für die noncommutative BH-Ungleichung, während 2301.01438 (Klein, Slote, Volberg, Zhang) das Qudit-Paper ist, siehe die folgende Zusammenfassung.
* **Objekt:** Kanal $\Phi(\rho) = \sum_{x,y}\hat\Phi(x,y)\sigma_x\rho\sigma_y$, Unitary $U = \sum_x\hat U(x)\sigma_x$, klassische Polynome. **Zugriff:** Query: Der Lerner wählt Inputzustände, wendet $\Phi$ bzw. $U$ (und $\mathrm{c}U$) an und misst in beliebiger Basis. Damit steht die Zeile im Query-Block; die Warnung ⚠️ in der Tabelle ist hiermit für Kanäle und Unitaries aufgelöst.
* **Status:** 🟢 🟢 🟢 für konstantes $d$: Queries unabhängig von $n$, Zeit polynomiell; $\exp(d^2)$ ist für $d = O(\sqrt{\log n})$ noch polynomiell.
* **Versprechen:** Grad $\leq d$: $\hat\Phi(x,y) = 0$ für $|x| + |y| > d$.

### Das Problem

Linial–Mansour–Nisan lernen $\mathrm{AC}^0$ über Low-Degree-Approximation; Eskenazis–Ivanisvili brachten Low-Degree-Lernen auf $O(\log n)$ Samples, weil BH-Ungleichungen sagen, dass die meisten Koeffizienten klein sind. Für Quantenobjekte gab es BH-Ungleichungen für Observablen (Huang–Chen–Preskill, Volberg–Zhang) mit $\log n$-Abhängigkeit. Die Frage: Lassen sich Kanäle, Unitaries und Query-Algorithmen mit Komplexität polynomiell oder polylogarithmisch in $n$ lernen, und was sind die richtigen BH-Ungleichungen?

### Kernresultate

* **Theorem 12 (BH für Kanäle).** $\big(\sum_{x,y}|\hat\Phi(x,y)|^{2d/(d+1)}\big)^{(d+1)/2d} \leq\exp(d)$ für Grad-$d$-Kanäle, allgemeiner für Superoperatoren beschränkt in der $S_1\to S_\infty$-Norm; verallgemeinert die Operator-BH-Ungleichungen von Huang et al. und Volberg–Zhang.
* **Theorem 19 (BH für vollständig beschränkte Tensoren).** Konstante $1$ statt $\mathrm{poly}(d)$ für $d$-lineare Tensoren, die Amplituden von $d$-Query-Algorithmen sind (Arunachalam, Briët, Palazuelos).
* **Theorem 1 (Kanäle).** $(\epsilon,\delta)$-Lernen in $\ell_2$ mit $\exp(\tilde O(d^2 + d\log 1/\epsilon))\log(1/\delta)$ Queries; allgemeine Kanäle brauchen $\Omega(4^n)$.
* **Proposition 2 (Pauli-Kanäle).** Grad-$d$-Pauli-Kanäle in Diamantnorm mit $O(n^{2d}/\epsilon^2\cdot\log(n/\delta))$ Queries, nur Produktzustände und Pauli-Messungen; dieselbe $n$-Abhängigkeit wie Flammia–O'Donnell (Population Recovery), aber Fourier-analytisch.
* **Theorem 3 (Unitaries).** Grad-$d$-Unitaries mit $\exp(\tilde O(d^2 + d\log 1/\epsilon))\log(1/\delta)$ Anwendungen, über Montanaro–Osborne zur Koeffizientenschätzung und Volberg–Zhang zur Trunkierung. Question 4: Ist $\sum_x|\hat U(x)| \leq C(d)$? Dann wäre $1/\epsilon^2$ möglich.
* **Theorem 5 (Query-Algorithmen).** Amplituden $T(x) = \langle v|\Psi_x\rangle$ von $d$-Query-Algorithmen (etwa $k$-Forrelation) klassisch aus $O((1/\epsilon)^d\log n)$ uniformen Beispielen, exponentiell besser als Eskenazis–Ivanisvili $(d/\epsilon)^{O(d)}\log n$, polynomiell in $n$ auch für $d = \omega(\log n)$.
* **Facts 6, 7 (Boolesche Funktionen).** Grad-$d$-Boolesche Funktionen exakt aus $O(4^dd\log 1/\delta)$ Quantenbeispielen (Granularität $2^{1-d}$), klassisch $\Omega(2^d\log n)$; eine BH-artige Ungleichung für Boolesche Funktionen.
* **Bemerkung (Zustände).** Grad-$d$-Zustände in Spurnorm mit $\tilde O(n^d/\epsilon^2\log(n/\delta))$ Kopien per Classical Shadows.

### Methodischer Ansatz

1. **Kanäle.** Die Matrix $\hat\Phi$ der Pauli-Koeffizienten ist eine Dichtematrix, unitär äquivalent zum Choi-Zustand (Bao–Yao); sie wird mit einer Query präpariert. Rechenbasis-Messungen sampeln $\{\hat\Phi(x,x)\}$, $O(1/\alpha^2)$ Samples finden alle $\alpha$-großen Diagonalen; ein SWAP-Test für gemischte Zustände schätzt die großen $\hat\Phi(x,y)$; alle anderen werden null gesetzt. Mit $T\sim\exp(d^2/\epsilon^d)$ und der BH-Ungleichung ist die Ausgabe $\epsilon$-nahe in $\ell_2$.
2. **Unitaries.** Montanaro–Osbornes Goldreich–Levin-Variante schätzt große Koeffizienten; die BH-Ungleichung von Volberg–Zhang begründet die Trunkierung.
3. **Tensoren.** Die Hybridungleichung zwischen BH und Grothendieck für vollständig beschränkte Multilinearformen.

### Bedeutung und Anwendungen

* Erste $n$-unabhängige Lernresultate für strukturierte Kanäle und Unitaries; Anwendungen auf Kurzzeit-Dynamik lokaler Hamiltonians (Lieb–Robinson macht $e^{-iHt}$ low-degree) und auf Rauschmodelle mit sparsamen lokalen Paulis.
* Die BH-Ungleichung mit Konstante $1$ ist ein Beitrag zur Funktionalanalysis; die $\mathrm{poly}(d)$-gegen-$\exp(d)$-Lücke wird als inkomparabel erklärt (Tensoren gegen allgemeine Polynome).

### Bezug zum eigenen Projekt

* Der Kanal-Algorithmus ist strukturell das eigene Zwei-Phasen-Protokoll auf dem Choi-Zustand: Sampling findet die großen Diagonalen (Lokalisierung), ein SWAP-Test schätzt die Koeffizienten (Schätzung), und die BH-Ungleichung ersetzt die Conjecture. Für Zustände fehlt genau diese Ungleichung, weil die Normierung $\sum|y_{q,p}|^2 = d$ statt $1$ ist; das ist der Normierungsabsatz der Übersicht in Reinform.
* Question 4 (ist die $\ell_1$-Norm der Koeffizienten eines Grad-$d$-Unitaries beschränkt?) ist die Unitary-Version der Frage, ob das Displacement-Spektrum einer Zustandsklasse $\ell_1$-beschränkt ist; für Grundzustände lokaler Hamiltonians gibt Lewis et al. Theorem 2 eine Antwort für Observablen, nicht für Zustände.
* Die $n$-unabhängige Query-Komplexität ist die Query-Seite des Quadranten: Mit Kontrolle über den Input kollabiert die Dimension aus der Sample-Zahl, während Bell-Sampling auf Zuständen $\log d$ zahlt.

### Grenzen und offene Fragen

* $\exp(d^2)$ ist nur für $d = O(\sqrt{\log n})$ polynomiell; die Autoren vermuten $\mathrm{poly}(d)$-Abhängigkeit.
* Nur $\ell_2$-Fehler für Kanäle und Unitaries; Diamantnorm nur für Pauli-Kanäle.
* Question 4 offen; die Montanaro–Osborne-Vermutung (Grad-$d$-Unitaries sind $2^d$-Juntas) würde sie beantworten.
* Zustände sind nur als Bemerkung behandelt.

### Fragen zum Tieferbohren

* Wie sieht die BH-Ungleichung für Kanäle in der Heisenberg–Weyl-Basis eines Qudits aus (Kombination mit Klein et al.), und was ist der "Grad" eines Displacement-Kanals?
* Der SWAP-Test für gemischte Zustände als Koeffizientenschätzer: Ist er die Zwei-Kopien-Messung $\hat\Phi\otimes\hat\Phi$, und wie verhält sie sich zu Bell-Sampling auf $\hat\Phi\otimes\hat\Phi^*$?
* Lässt sich der Ausgang "Sampling der Diagonalen mit $O(1/\alpha^2)$" als Sample-Untergrenze für die Lokalisierung im eigenen Protokoll lesen, wo die Diagonale $|y_{q,p}|^2/d$ ist?

Paper: [arXiv:2405.10933](https://arxiv.org/abs/2405.10933)

---

## Quantum and classical low-degree learning via a dimension-free Remez inequality (arXiv:2301.01438)

Die Arbeit von **Ohad Klein, Joseph Slote, Alexander Volberg und Haonan Zhang** (Hebrew University, Caltech, Michigan State/Bonn, South Carolina; 2023) erweitert Low-Degree-Lernen vom Hyperwürfel und von Qubits auf Produkte zyklischer Gruppen $\mathbb{Z}_K^n$ und auf $K$-Level-Qudits. Das technische Hindernis war, dass die Standardbeweise der Bohnenblust–Hille-Ungleichung im Polarisationsschritt ein Maximumprinzip brauchen, das für die $K$-ten Einheitswurzeln nicht gilt. Die Lösung ist eine dimensionsfreie Remez-Ungleichung: Das Supremum eines Polynoms vom Grad $d$ über $\Omega_K^n$ kontrolliert sein Supremum über den ganzen Polytorus $\mathbb{T}^n$ mit Konstante $(O(\log K))^d$. Daraus folgen $O(\log n)$-Sample-Algorithmen für Qudit-Observablen in der Heisenberg–Weyl- und der Gell-Mann-Basis.

### Einordnung in die Tabellen

* **Task type:** Estimating. Gegeben Samples $(\rho, \mathrm{tr}[A\rho])$, zurück kommt eine $L^2$-Approximation der Observablen, also alle Koeffizienten bis zum relevanten Grad. Ergänzung zur Zeile "Low-degree quantum objects" um die Qudit-Variante; die Tabelle nennt jetzt Klein, Slote, Volberg, Zhang für Qudits.
* **Objekt:** Observable auf $n$ Qudits der Dimension $K$, oder Funktion $f:\mathbb{Z}_K^n\to\mathbb{C}$. **Zugriff:** Sample: zufällige Produktzustände aus einer festen Menge und ihr Erwartungswert; also Sample-Zugriff im Sinne der Tabellen, kein Query.
* **Status:** 🟢 🟢 🟢 bei konstantem Grad: Samples $O(\log n)$, Zeit polynomiell.
* **Versprechen:** Grad $\leq d$ in der gewählten Basis; für Theorem 4 keines über $A$, aber eines über die Verteilung $\mu$, unter der Low-Degree-Trunkierungen gute Approximationen sind.

### Das Problem

Eskenazis–Ivanisvili reduzieren Low-Degree-Lernen auf eine $\ell_p$-Schranke, $p < 2$, für die Fourier-Koeffizienten (BH-Ungleichung), weil dann die meisten Koeffizienten klein sind und Nullsetzen unter einer Schwelle einen $n$-unabhängigen $\ell_2$-Fehler gibt. Für Qubits existiert die BH-Ungleichung (Huang–Chen–Preskill; Volberg–Zhang). Für Qudits in der Heisenberg–Weyl-Basis (Clock und Shift, Eigenwerte $K$-te Einheitswurzeln) braucht man BH über $\mathbb{Z}_K^n$, den unstudierten Fall zwischen Hyperwürfel ($K = 2$) und Polytorus ($K = \infty$), und der Standardbeweis bricht, weil $\Omega_K$ nicht der Rand seiner konvexen Hülle ist; schon für $n = 1$, $K = 3$ gibt es $f$ mit $\Vert f\Vert_{\mathrm{conv}(\Omega_K)} > \Vert f\Vert_{\Omega_K}$.

### Kernresultate

* **Theorem 5 (dimensionsfreie Remez-Ungleichung).** Für $f$ vom Grad $d$ mit individuellem Grad $\leq K-1$: $\Vert f\Vert_{\mathbb{T}^n} \leq (O(\log K))^d\Vert f\Vert_{\Omega_K^n}$; anscheinend die erste diskrete multidimensionale Remez-Ungleichung mit dimensionsfreier Konstante.
* **Corollary 6 (zyklische BH).** $\Vert\hat f\Vert_{2d/(d+1)} \leq (O(\log K))^{d + \sqrt{d\log d}}\Vert f\Vert_{\Omega_K^n}$, direkt aus Theorem 5 und der Polytorus-BH.
* **Theorem 3 (zyklisches Low-Degree-Lernen).** Grad-$d$-Funktionen $f:\mathbb{Z}_K^n\to\mathbb{D}$ aus $(\log K)^{O(d^2)}\log(n/\delta)\epsilon^{-d-1}$ uniformen Beispielen bis auf $\Vert f - \tilde f\Vert_2^2 \leq\epsilon$ in Polynomialzeit, gegen $\mathrm{poly}(n)$ naiv.
* **Theorem 4 (Qudit-Observablen).** Für *beliebige* beschränkte Observablen $A$ auf $n$ $K$-Level-Qudits und eine Klasse von Verteilungen $\mu$ über Zuständen: $\mathbb{E}_{\rho\sim\mu}|\mathrm{tr}[A\rho] - \mathrm{tr}[\tilde A\rho]|^2 \leq\epsilon$ aus $s \leq O(\log(n/\delta)C^{\log^2(1/\epsilon)}K^{3/2}\Vert A_{\leq t}\Vert_{\mathrm{op}}^{2t})$ Samples, $t\approx\log(1/\epsilon)$, Samples von der Gleichverteilung über eine feste Menge von Produktzuständen; die Klasse der $\mu$ erweitert die lokal flachen Verteilungen von Huang, Chen, Preskill auf Qudits und liefert auch für Qubits neue Verteilungen.
* **Zwei Basen.** Gell-Mann reduziert auf die Hyperwürfel-BH; Heisenberg–Weyl auf die zyklische BH, also auf Theorem 5.

### Methodischer Ansatz

* **Lemma 7 (DFT-Interpolation).** Für $z\in\mathbb{T}$ gibt es $c$ mit $z^k = \sum_j c_j\omega^{jk}$ für $k < K$ und $\Vert c\Vert_1 \leq B\log K$, aus den DFT-Koeffizienten von $(1, z, \dots, z^{K-1})$ und der Harmonischen Zahl $H_K$. In einer Koordinate gibt Hölder sofort die Remez-Ungleichung.
* **Korrelierter Zufall.** Koordinatenweise Wiederholung würde $(\log K)^n$ kosten; stattdessen wird die Summe als Erwartung über ein komplexes Maß gelesen und die $n$ Variablen werden korreliert, so dass die Konstante nur vom Grad abhängt. Zwei Beweise existieren; der hier gegebene hat die für Lernanwendungen bessere Konstante.
* **Lernalgorithmus.** Fourier-Sampling der Koeffizienten, Nullsetzen unter der Schwelle (Eskenazis–Ivanisvili, leicht verallgemeinert), Plancherel für den $\ell_2$-Fehler.

### Bedeutung und Anwendungen

* Öffnet die Low-Degree-Lerntheorie für Qudit-Prozessoren, die in der NISQ-Ära praktische Vorteile bringen, und für Funktionen auf Hypergrids.
* Die Remez-Ungleichung ist ein Werkzeug von eigenem Wert: eine Brücke von diskreten Räumen zurück in die klassische harmonische Analysis auf dem Polytorus.
* Zeigt, dass die Heisenberg–Weyl-Basis *nicht* dieselbe Analysis hat wie die Pauli-Basis: Die Einheitswurzeln sind ein echtes Hindernis, kein technisches.

### Bezug zum eigenen Projekt

* Das ist das Paper, das die Fourier-Analysis in der Heisenberg–Weyl-Basis eines Qudits sauber macht; für ein einzelnes Qudit ($n = 1$, $K = d$) sind die Displacement-Koeffizienten $y_{q,p}$ genau die Koeffizienten in dieser Basis, und die zyklische BH-Ungleichung ist die Aussage, dass ein Operator beschränkter Norm mit "niedrigem Grad" in $(q,p)$ ein $\ell_{2d/(d+1)}$-beschränktes Spektrum hat.
* Der Grad ist hier $|\alpha| = \sum_j\alpha_j$ mit $\alpha_j\in\{0, \dots, K-1\}$, also die Größe der Verschiebung; für $n = 1$ ist "Low-Degree" gleichbedeutend mit "kleines $q$ und $p$". Das ist ein Versprechen, das in der eigenen Instanzenleiter fehlt und beweisbar wäre: Zustände mit Displacement-Spektrum nahe dem Ursprung des Phasenraums.
* Die Konstante $(\log K)^{O(d^2)}$ wächst mit $d = K$ (dem Grad bis zum vollen Phasenraum) unbrauchbar; das ist die Stelle, an der Low-Degree-Lernen aufhört und Sparsity-Lernen mit LWE-Härte anfängt.

### Grenzen und offene Fragen

* Die Konstante $(O(\log K))^d$ ist für $d\ll K$ oder sehr zusammengesetztes $K$ verbesserbar; Erweiterungen auf $L^p$ angekündigt.
* Nur uniforme Samples auf Produktzuständen; adaptive oder nicht-uniforme Zugriffe nicht behandelt.
* Theorem 4 braucht $\Vert A_{\leq t}\Vert_{\mathrm{op}}$ der Trunkierung, die für allgemeine $A$ groß sein kann.
* Zusammengesetztes $K$ ist zugelassen (zyklische Gruppe, kein Körper), aber nur für Funktionen und Observablen, nicht für Zustände.

### Fragen zum Tieferbohren

* Gilt eine zyklische BH-Ungleichung für Zustände mit der Normierung $\sum|y_{q,p}|^2 = d$, etwa nach Reskalierung $\rho\mapsto d\rho$, und was sagt sie über die Zahl großer Koeffizienten?
* Was ist der "Grad" eines Grundzustands eines Displacement-Hamiltonians, und ist er klein, wenn die Kopplungen $D_{q,p}$ nur kleine $(q,p)$ haben?
* Wie sieht die korrelierte Randomisierung des Beweises aus, wenn man sie als Sampling-Vorschrift für Probe-Zustände in Phase 2 liest?

Paper: [arXiv:2301.01438](https://arxiv.org/abs/2301.01438)

---

## Optimal learning of quantum Hamiltonians from high-temperature Gibbs states (arXiv:2108.04842)

Die Arbeit von **Jeongwan Haah, Robin Kothari und Ewin Tang** (Microsoft Quantum, Washington; FOCS 2022) löst das Lernen der Koeffizienten eines Hamiltonians aus Kopien seines Gibbs-Zustands im Hochtemperaturregime optimal: $O(\log N/(\beta^2\epsilon^2))$ Kopien für $\ell_\infty$-Fehler $\epsilon$ und Rechenzeit linear in der Datengröße, mit passender Untergrenze $\Omega(e^\beta\log N/(\beta^2\epsilon^2))$ für alle $\beta$. Der Hamiltonian darf Low-Intersection sein (keine Geometrie nötig), und fast derselbe Algorithmus lernt $H$ aus $e^{-itH}$ bei konstantem $t$.

### Einordnung in die Tabellen

* **Task type:** Estimating. Die Terme $E_a$ sind bekannt, gesucht sind die Koeffizienten $\lambda_a$. Die Zeile "Hamiltonian coefficients from Gibbs states, known terms"; das Paper ist der Grund für "polynomial at high temperature" in der Zeitspalte.
* **Objekt:** Hamiltonian, aus Kopien seines Gibbs-Zustands. **Zugriff:** Sample; jede Kopie wird in lokalen Pauli-Basen gemessen, es sind nur die lokalen Marginale nötig.
* **Status:** 🟢 🟢 🟢 bei $\beta < \beta_c$: Kopien logarithmisch, Zeit $O(SN)$, Speicher die Koeffizienten. Für tiefe Temperaturen 🔴 in der Zeit bis Bakshi, Liu, Moitra, Tang (2024).
* **Versprechen:** Low-Intersection ($O(1)$ Qubits pro Term, $O(1)$ Terme pro Qubit, keine Geometrie), $\beta$ unterhalb einer kritischen Konstante $\beta_c$, die nur von den Low-Intersection-Konstanten abhängt.

### Das Problem

Klassisch ist das Lernen von Markov-Zufallsfeldern seit 50 Jahren studiert; Parameterlernen kostet $2^{O(\beta)}\log N/(\beta^2\epsilon^2)$ Samples und ebenso viel Zeit mal $N$ (Folklore, Anhang B). Anshu, Arunachalam, Kuwahara und Soleimanifar hatten für geometrisch lokale Quanten-Hamiltonians $O(2^{\mathrm{poly}(\beta)}N^2\log N/(\beta^c\epsilon^2))$ Kopien und keine explizite Zeitschranke. Quantenmechanisch fehlt die Markov-Eigenschaft (Hammersley–Clifford), also übertragen sich klassische Algorithmen nicht. Die Fragen: die klassische Sample-Komplexität erreichen, und die Zeit.

### Kernresultate

* **Theorem 1.1.** Für Low-Intersection $H$ und $\beta < \beta_c$: $\ell_\infty$-Fehler $\epsilon$ mit $O(\log(N/\delta)/(\beta^2\epsilon^2))$ Kopien, $\ell_2$-Fehler mit $O(N\log(N/\delta)/(\beta^2\epsilon^2))$; Zeit linear in Kopienzahl mal $N$.
* **Theorem 1.2 (Untergrenze).** Für jedes $\beta$ gibt es ein 2-lokales $H$ (disjunkte Zweiqubit-Terme), das $\Omega(e^\beta\log(N/\delta)/(\beta^2\epsilon^2))$ Kopien für $\ell_\infty$ und $\Omega(e^\beta N/(\beta^2\epsilon^2))$ für $\ell_2$ erzwingt; verbessert die frühere $\Omega((\sqrt N + \log(1-\delta))/(\beta\epsilon))$ erheblich.
* **Theorem 1.3 (Echtzeit-Dynamik).** Aus $U = e^{-itH}$ mit bekanntem $t < t_c$: $O(\log(N/\delta)/(t^2\epsilon^2))$ Anwendungen, Zeit $O(N\log(N/\delta)/(t^2\epsilon^2))$; Zeitauflösung konstant statt $O(\epsilon)$, Kopien quadratisch besser als Ableitungsschätzung mit $1/\epsilon^4$.
* **Starke Konvexität.** Die Log-Zustandssumme ist $\Theta(\beta^2)$-stark konvex bei hoher Temperatur, bis auf Konstanten der wahre Wert; daraus $\mathrm{Var}(\sum v_aE_a) = \Omega(\beta^2\Vert v\Vert_2^2)$ im thermischen Gleichgewicht.
* **Vergleich.** Naive Tomographie eines Patches: quasi-polynomiell; Anshu et al.: $N^2\log N/(\beta^c\epsilon^2)$ Kopien und etwa $N^3\log N$ Zeit; hier $\log N/(\beta^2\epsilon^2)$ und $N\log N/(\beta^2\epsilon^2)$, in gewissen Regimen superpolynomiell besser.

### Methodischer Ansatz

1. **Clusterentwicklung** (Kuwahara–Saito): Die Taylorreihe von $\mathrm{Tr}(E_a\rho)$ in $\beta$ konvergiert bei $\beta < \beta_c$; $\partial_{\lambda_a}\log\mathrm{Tr}\,e^{-\beta H} = -\beta\,\mathrm{Tr}(E_a\rho)$ verbindet Erwartungswerte mit der Log-Zustandssumme. Nur $O(1/(\beta\epsilon))$ Terme im Abstand $\log(1/(\beta\epsilon))$ vom Träger von $E_a$ zählen.
2. **Explizite Berechnung** der Clusterableitungen (Proposition 3.13, Algorithmus 2) in exakter Arithmetik, weil die $E_a$ Paulis sind; frühere Arbeiten behaupteten die Berechenbarkeit nur.
3. **Polynomiales Gleichungssystem.** Die trunkierten Reihen sind Polynome in $\lambda$; die $\infty\to\infty$-Norm der inversen Jacobi-Matrix gibt die Sample-Komplexität (Theorem 4.2), Newton–Raphson mit $O(\log(1/(\beta\epsilon)))$ Iterationen löst es, und die Laufzeit wird vom Einlesen dominiert (Theorem 4.6).
4. **Untergrenze** über Fano und KL-Divergenz wie bei klassischen Markov-Feldern (Santhanam–Wainwright), $\ell_2$ per Fehlerkorrekturcodes.

### Bedeutung und Anwendungen

* Optimal in allen Parametern; die erste Zeitschranke für Quanten-Hamiltonian-Lernen aus Gibbs-Zuständen. Die Tabelle dieses Dokuments hat die Zeitspalte "🔴→🟢" genau wegen dieses Papers und seines Nachfolgers bei beliebiger konstanter Temperatur.
* Strukturlernen bleibt offen: Klassisch geht es über Parameterlernen auf allen $k$-lokalen Termen mit der Low-Intersection-Garantie, quantenmechanisch funktioniert der Algorithmus nur für $\beta < 1/\mathrm{poly}(N)$; Bakshi et al. lösen es 2024 aus der Dynamik.

### Bezug zum eigenen Projekt

* Das ist die "bekannte Terme"-Zeile, gegen die das Strukturlernen (Searching-Tabelle) definiert ist: Hier ist die Liste der Terme das Dictionary, und der Algorithmus schätzt Koeffizienten über einem Dictionary aus lokalen Marginalen. Regime 1 des eigenen Projekts ist dieselbe Struktur mit Displacement-Adressen statt Pauli-Termen.
* Die Clusterentwicklung ist eine Sparsity-Aussage über Gibbs-Zustände bei hoher Temperatur: Erwartungswerte hängen nur von wenigen nahen Termen ab. Für Objective 4 (Gibbs-Zustände) ist das der Mechanismus, der ein sparsames oder zumindest lokalisiertes Displacement-Spektrum bei hoher Temperatur erwarten lässt, und $\beta_c$ die Grenze, ab der die Instanzenleiter schwer wird.
* Die Untergrenze $e^\beta$ zeigt, dass tiefe Temperatur *Sample*-Kosten treibt, nicht nur Zeit; der Mixedness-Faktor ist also zweischneidig.

### Grenzen und offene Fragen

* $\beta < \beta_c$; tiefere Temperaturen erst 2024 (Bakshi et al.) in polynomieller Zeit, mit anderer Technik.
* Strukturlernen aus Gibbs-Zuständen ist offen.
* Die Konstante $\beta_c$ ist implizit über die Low-Intersection-Parameter; für konkrete Modelle nicht ausgerechnet.
* Theorem 1.3 braucht bekanntes, kleines $t$.

### Fragen zum Tieferbohren

* Wie sieht die Clusterentwicklung für einen Displacement-Hamiltonian auf einem einzelnen Qudit aus, wo "Intersection" über den Phasenraum statt über Qubits definiert werden muss?
* Ist die Log-Zustandssumme in der Displacement-Basis stark konvex, und was ist das Analogon von $\beta_c$ für die Instanzenleiter?
* Lässt sich Newton–Raphson auf dem sparsamen Surrogat des eigenen Protokolls als Phase-2-Alternative zu MMW verwenden?

Paper: [arXiv:2108.04842](https://arxiv.org/abs/2108.04842)

---
## Learning many-body Hamiltonians with Heisenberg-limited scaling (arXiv:2210.03030)

Die Arbeit von **Hsin-Yuan Huang, Yu Tong, Di Fang und Yuan Su** (Caltech, Berkeley, Simons Institute, Microsoft; *Phys. Rev. Lett.* 130, 200403 (2023)) gibt den ersten Algorithmus, der einen wechselwirkenden $N$-Qubit-Hamiltonian aus seiner Dynamik am Heisenberg-Limit lernt: Gesamtevolutionszeit $T = O(\epsilon^{-1}\log\delta^{-1})$ für jeden Parameter, unabhängig von $N$, mit nur $O(\mathrm{polylog}(\epsilon^{-1})\log\delta^{-1})$ Experimenten, robust gegen SPAM-Fehler, ohne Eigen- oder Gibbs-Zustände, mit einer passenden Untergrenze. Die Idee: den Hamiltonian per Quantensimulationstechniken in nicht-wechselwirkende Patches mit bekannten Eigenvektoren umformen und dort robuste Phasenschätzung laufen lassen.

### Einordnung in die Tabellen

* **Task type:** Estimating. Der Wechselwirkungsgraph (die Menge $S$ der Pauli-Terme) ist bekannt, gesucht sind die $\lambda_a$. Die Zeile "Heisenberg-limited Hamiltonian learning".
* **Objekt:** Low-Interaction-Hamiltonian $H = \sum_a\lambda_aE_a$, $|\lambda_a|\leq 1$. **Zugriff:** Query, Rung 3: verschachtelte Sequenzen $V_{K+1}U(t_K)\cdots V_1$ mit Schichten von Ein-Qubit-Clifford-Gattern, also Kontrolle zwischen den Evolutionen, die für Heisenberg-Skalierung nachweislich nötig ist (Dutkiewicz, O'Brien, Schuster).
* **Status:** 🟢 🟢 🟢. Evolutionszeit $1/\epsilon$, Experimente polylogarithmisch, klassische Zeit $O(N\mathrm{polylog}(\epsilon^{-1})\log\delta^{-1})$.
* **Versprechen:** bekannte Terme mit $O(1)$-Lokalität und $O(1)$ Termen pro Qubit; geometrische Lokalität nicht nötig, aber bei All-to-All-Wechselwirkung tritt eine $N$-Abhängigkeit in $T$ auf.

### Das Problem

Alle früheren Verfahren für Vielteilchen-Hamiltonians (Ableitungsschätzung, Gradientenverfahren, Polynominterpolation) brauchen $\epsilon^{-2}$ Experimente und Evolutionszeit, das Standard-Quantenlimit. Für einen Parameter oder ein Qubit erreicht Metrologie das Heisenberg-Limit $\epsilon^{-1}$ per verschränkter Zustände oder langer kohärenter Evolution; für Vielteilchen-Systeme zerstört das Verschränkungswachstum unter $e^{-iHt}$ den Vorteil, also blieb man bei kurzen Zeiten. Kann man das Heisenberg-Limit für Vielteilchen-Hamiltonians erreichen?

### Kernresultate

* **Theorem 1.** Ein SPAM-robuster Algorithmus mit Ein-Qubit-Clifford-Experimenten liefert nach Gesamtevolutionszeit $T = O(\epsilon^{-1}\log\delta^{-1})$ Schätzungen mit $\Pr[|\hat\lambda_a - \lambda_a|\leq\epsilon]\geq 1-\delta$ für jedes $a$; für alle Parameter zugleich $T = O(\epsilon^{-1}\log(N/\delta'))$. Zahl der Experimente $O(\mathrm{polylog}(\epsilon^{-1})\log\delta^{-1})$, Clifford-Schichten $O(\epsilon^{-1.5}\mathrm{polylog})$.
* **Theorem 2 (Untergrenze).** Jeder SPAM-robuste Algorithmus mit beliebigen adaptiven Experimenten braucht $T = \Omega(\epsilon^{-1}\log\delta^{-1})$: ein algorithmischer Beweis des Heisenberg-Limits inklusive $\delta$.
* Die Zahl der Experimente unterschreitet $\epsilon^{-1}$; das widerspricht dem Heisenberg-Limit nicht, das über die Gesamtzeit definiert ist.

### Methodischer Ansatz

1. **Reshaping.** Für Unitaries $U_k$ und Gewichte $w_k$ ist $\tilde H = \sum_kw_kU_kHU_k^\dagger$ ein neuer unbekannter Hamiltonian, unter dem man per qDRIFT oder Trotter (nur Vorwärtsentwicklung, keine höheren Ordnungen) evolvieren kann, ohne $H$ zu kennen, weil $e^{-itU_kHU_k^\dagger} = U_ke^{-itH}U_k^\dagger$.
2. **Ein Qubit.** $\frac12(H + XHX) = \lambda_xX$ löscht $Y$ und $Z$; robuste Phasenschätzung (Kimmel, Low, Yoder) mit langer kohärenter Evolution auf dem bekannten Eigenzustand von $X$ gibt $\lambda_x$ mit $O(\epsilon^{-1}\log\delta^{-1})$ Zeit.
3. **Wenige Qubits.** Mittelung über $I, X_1, Z_2, X_1Z_2$ lässt nur Terme mit $I$ oder $X$ auf Qubit 1 und $I$ oder $Z$ auf Qubit 2 stehen; die Eigenbasis $\{|\pm\rangle|0/1\rangle\}$ ist bekannt, Eigenwertdifferenzen per Phasenschätzung, Parameter per Hadamard-Transformation.
4. **Divide and Conquer.** Pauli-Twirl eines Zwischenqubits ($\frac14(H + XHX + YHY + ZHZ)$ auf Qubit 3) entkoppelt die Kette in Patches ohne Verschränkung dazwischen; alle Patches werden parallel gelernt, mit Färbungen für Kopplungsterme.
5. **Fehleranalyse** der Randomisierung und Trotterisierung (Anhänge D, F); die Untergrenze über TV-Distanz-Schranken pro Experiment (Anhang G).

### Bedeutung und Anwendungen

* Erstes Heisenberg-limitiertes Vielteilchen-Lernen; die Nachfolger (Dutkiewicz et al. über Notwendigkeit von Kontrolle; Bakshi et al. über Strukturlernen bei konstanter Zeitauflösung; Shin, Lee, Oh über Langzeitzugriff) definieren sich an dieser Arbeit.
* Praktisch attraktiv: nur Ein-Qubit-Cliffords, SPAM-robust, keine speziellen Zustände; die Präzision ist durch die Geschwindigkeit der Ein-Qubit-Gatter begrenzt.
* Anwendungen in Sensorik, Gerätecharakterisierung und Vielteilchenphysik.

### Bezug zum eigenen Projekt

* Die Zeile ist der Beleg für die Aussage der Übersicht, dass Query-Zugriff die Präzisionsrate von $1/\epsilon^2$ auf $1/\epsilon$ verbessert; das eigene Protokoll steht auf Rung 2 und hat diese Rate nicht. Ob Amplitudenschätzung auf dem Präparationsschaltkreis (Regime 3) für Displacement-Amplituden eine $1/\epsilon$-Rate gäbe, ist die Query-Version der eigenen Aufgabe.
* Reshaping ist eine Symmetrisierungstechnik: Twirls über Untergruppen der Pauli-Gruppe projizieren den Hamiltonian auf einen Kommutanten. In der Heisenberg–Weyl-Basis eines Qudits wäre das Analogon der Twirl über eine Untergruppe der Displacement-Gruppe, der das Spektrum auf eine Nebenklasse einschränkt; das ist eine mögliche Messseiten-Vorverarbeitung für Regime 2.
* Die Trennung "Experimente polylog, Zeit $1/\epsilon$" ist ein Hinweis darauf, dass die richtige Kostengröße vom Zugriff abhängt; in der eigenen Skalierungsanalyse ist die Kopienzahl das Analogon der Gesamtzeit.

### Grenzen und offene Fragen

* Bekannte Terme; Strukturlernen erst bei Bakshi et al.
* All-to-All-Wechselwirkung bringt $N$ in $T$.
* Die Zeitauflösung der Kontrollpulse muss fein sein (Trotter-Schritte); Bakshi et al. und Shin, Lee, Oh behandeln konstante Auflösung und Langzeitzugriff.
* Keine Untergrenze für die Zahl der Experimente oder Gatter.

### Fragen zum Tieferbohren

* Wie sieht Reshaping in der Displacement-Basis aus: Welche Twirls löschen welche $(q,p)$-Terme, und bleiben die Eigenbasen bekannt?
* Warum verhindert die Nichtexistenz höherer Trotter-Ordnungen ohne Rückwärtsentwicklung keine Heisenberg-Skalierung, und wo genau geht der Faktor $\epsilon^{-1.5}$ in die Gatterzahl ein?
* Was ist das Heisenberg-Limit für das Lernen eines *Zustands* (statt eines Hamiltonians) aus seinem Präparationsschaltkreis, und ist $1/\epsilon$ pro Displacement-Amplitude erreichbar?

Paper: [arXiv:2210.03030](https://arxiv.org/abs/2210.03030)

---

## Efficient estimation of Pauli channels (arXiv:1907.12976)

Die Arbeit von **Steven T. Flammia und Joel J. Wallman** (Sydney, Yale, Quantum Benchmark, Waterloo; *ACM Trans. Quantum Comput.* 1(1), 2020) gibt die erste systematische Sample-Komplexität für Pauli-Kanäle mit Garantien in *relativer* Präzision und robust gegen SPAM-Fehler: den vollen Kanal auf $n$ Qubits mit $O(\epsilon^{-2}n2^n)$ Messungen, effizient in der Hilbertraumdimension; eine beliebige Menge von $s$ Fehlerraten mit $O(\epsilon^{-4}\log s\log(s/\epsilon^2))$; und einen Kanal mit $k$-lokalen Korrelationen (Markov-Feld über bekanntem Faktorgraphen) mit $O_k(\epsilon^{-2}n^2\log n)$, effizient in $n$. Die Prozedur ist eine Variante von Randomized Benchmarking über die Pauli-Gruppe.

### Einordnung in die Tabellen

* **Task type:** Estimating. Die Liste ist die der $4^n$ Pauli-Fehlerraten $p$ oder Eigenwerte $\lambda$ (Walsh–Hadamard-Transformierte), explizit als Teilmenge $E$ oder implizit über den Faktorgraphen. Die Zeile "Pauli channel estimation, sequence-based".
* **Objekt:** Pauli-Kanal, oder die Pauli-Projektion eines beliebigen Kanals per Randomized Compiling. **Zugriff:** Query, Rung 3: wiederholte Anwendung in Sequenzen variabler Länge, verschachtelt mit zufälligen Pauli-Gattern; das kauft SPAM-Robustheit und relative Präzision.
* **Status:** 🟢 🟢 🟢 unter Sparsity ($s = \mathrm{poly}(n)$) oder Faktorgraph-Modell ($k = O(1)$); der volle Kanal ist $2^n$, effizient nur in $d$.
* **Versprechen:** "nice noise" (gatterunabhängig, stationär, markovsch, nahe ideal); für Result 3 ein bekannter Faktorgraph mit positiven Marginalen.

### Das Problem

Pauli-Kanäle sind das Standardmodell der Fehlerkorrektur und werden durch Randomized Compiling physikalisch erzwungen; Schwellen ändern sich unter verzerrtem oder korreliertem Rauschen um Faktoren bis vier. Trotzdem gab es keine Schätzverfahren jenseits voller Kanaltomographie, die zudem additive Präzision liefert und durch SPAM-Fehler systematisch verzerrt ist; bei Fehlerraten von $10^{-6}$ wären $10^{12}$ Samples nötig. Gesucht: relative Präzision, SPAM-Robustheit, Skalierung in $n$ unter realistischen Modellen.

### Kernresultate

* **Result 1 (Propositionen 8, 9).** Alle $4^n$ Fehlerraten mit $O(\epsilon^{-2}n2^n)$ Messungen, $\Vert\hat p - p\Vert_2\leq O(\epsilon)(1 - p_0)$, $p_0$ die Wahrscheinlichkeit keines Fehlers; relative Präzision ist der Kern, weil die Fehlerraten winzig sind.
* **Result 2 (Theorem 11).** Für jede Menge $E$ von $s$ Paulis $O(\epsilon^{-4}\log s\log(s/\epsilon^2))$ Messungen mit $\Vert\hat p - p\Vert_\infty\leq O(\epsilon)(1-p_0)$; das $\epsilon^{-4}$ ist ein Artefakt der Bias-Analyse der Subroutine Ratio. Anwendbar auf alle Fehler kleinen Gewichts; eine baumbasierte Suchheuristik findet sparsame Mengen, deren Ergebnis zertifizierbar ist.
* **Result 3 (Proposition 18).** Für ein Markov-Feld mit $k$-Grad-Faktorgraph und positiven Marginalen ein Tensornetzwerk-Schätzer aus $O_k(\epsilon^{-2}n^2\log n)$ Messungen mit $\Vert\hat p - p\Vert_1\leq O(\epsilon)\Vert\mathbb{1}_I - p\Vert_\infty$, berechenbar in $\mathrm{poly}(n)$.
* **Lemma 2 (Stabilizer-Überdeckungen).** Jede Menge $X$ von Paulis wird von höchstens $\min(|X|, \sqrt{|\langle X\rangle/S_X|} + 1)\leq 2^n + 1$ Stabilizergruppen überdeckt (MUB-Konstruktion), scharf für Gruppen.
* **Numerik** bis 100 Qubits und eine Implementierung auf einem 14-Qubit-Gerät (Harper, Flammia, Wallman, *Nat. Phys.* 2020).

### Methodischer Ansatz

* **RB über die Pauli-Gruppe.** Präparation und Messung in einer Stabilizerbasis, Sequenzen zufälliger Pauli-Gatter mitteln das Rauschen; die Zerfallsraten der $2^n$ gleichzeitig ausgelesenen Bits werden per Hadamard-Transformation entkoppelt, statt serieller Exponentialfits einzelner Parameter; das ist die Neuerung gegenüber Character Benchmarking. Harper et al. hatten für Clifford-RB die relative Präzision eines Parameters gezeigt; hier sind es $4^n$.
* **Symplektische Struktur.** Nur kommutierende Paulis sind gleichzeitig messbar; die Fehlerverteilung ist ein "symplektisches Markov-Feld" mit quasi-latenten Variablen, das sich von klassischen Markov-Feldern unterscheidet.
* **Hammersley–Clifford** rundet lokal geschätzte Marginale zu einer globalen Verteilung als Tensornetzwerk.

### Bedeutung und Anwendungen

* Erster Beweis von Recovery-Garantien für Kanäle in relativer Präzision ohne SPAM-Bias; erste effiziente Garantien für nichttriviale Kanalklassen auf $n$ Qubits; qualitative Änderung gegenüber dem damaligen Rekord (drei Qubits per Compressed Sensing).
* Anwendungen: Codes und Decoder auf das Rauschen zuschneiden, Fehlertoleranz anpassen, Schwellen und Overheads schätzen; die "Pauli noise learning transfer"-Idee der eigenen Positionierung.
* Chen, Zhou, Seif, Jiang zeigen später, dass gerade diese RB-artigen, ancilla-freien Protokolle für Eigenwerte $\Omega(2^{n/3})$ Runden brauchen, während ein $n$-Qubit-Ancilla $O(n)$ erlaubt.

### Bezug zum eigenen Projekt

* Die Zeile ist der Query-Block-Vertreter für Kanäle: Sequenzen kaufen Robustheit, nicht Dimension. Für die eigene Pipeline ist Randomized Compiling auf beiden Kopien die Standardmethode, kohärente Fehler in Pauli-Rauschen zu verwandeln, und dieses Paper ist die Referenz dafür, was danach lernbar ist.
* Der Übergang von Result 1 ($2^n$) zu Result 2 (Sparsity) zu Result 3 (Markov-Feld) ist die Kanal-Version der Instanzenleiter: generisch, sparsam, faktorisiert. Das eigene "factorized spectra with a best-first heap" ist das Zustands-Analogon von Result 3.
* Relative Präzision ist eine Größe, die in der eigenen Skalierungsanalyse fehlt: Top-$k$-Amplituden sind groß, aber die Signalerkennung bei kleinem Signal-Rausch-Verhältnis würde von relativer statt additiver Genauigkeit profitieren.

### Grenzen und offene Fragen

* $\epsilon^{-4}$ in Result 2 vermutlich $\epsilon^{-2}$; die Suchheuristik hat keine formale Erfolgsanalyse.
* Nur die Pauli-Projektion des Kanals; kohärente Anteile sind unsichtbar.
* Der Faktorgraph muss bekannt sein; Strukturlernen des Rauschens ist offen.
* Die Noise-Annahmen (gatterunabhängig, stationär) sind mild, aber nicht immer erfüllt.

### Fragen zum Tieferbohren

* Was ist die Heisenberg–Weyl-Version: Randomized Compiling mit Displacement-Operatoren auf Qudits, und welche Struktur hat das "symplektische Markov-Feld" der Fehlerraten über $\mathbb{Z}_d^2$?
* Wie viel der Robustheit stammt aus der Sequenzlänge (Query) und wie viel aus dem Twirl (Sample)? Gäbe es eine Sample-Version mit Choi-Zuständen und Bell-Messung?
* Lässt sich die baumbasierte Suchheuristik für sparsame Fehlermengen als Vorlage für eine Best-First-Suche im Displacement-Spektrum lesen?

Paper: [arXiv:1907.12976](https://arxiv.org/abs/1907.12976)

---

## Quantum advantages for Pauli channel estimation (arXiv:2108.08488)

Die Arbeit von **Senrui Chen, Sisi Zhou, Alireza Seif und Liang Jiang** (Chicago, Caltech; *Phys. Rev. A* 105, 032435 (2022)) beweist einen exponentiellen Vorteil verschränkter Messungen für eine praktisch relevante Aufgabe: alle $4^n$ Eigenwerte eines $n$-Qubit-Pauli-Kanals auf $\pm\epsilon$ lernen. Mit einem $n$-Qubit-Ancilla genügen $O(n/\epsilon^2)$ Anwendungen des Kanals, ohne Ancilla braucht jedes Protokoll, auch adaptiv und mit Verkettung, $\Omega(2^{n/3})$ Messrunden. Für $k$ Ancilla-Qubits gilt $\Omega(2^{(n-k)/3})$ allgemein und $\Omega(n2^{n-k})$ ohne Adaptivität und Verkettung, letzteres scharf.

### Einordnung in die Tabellen

* **Task type:** Estimating. Die implizite Liste aller $4^n$ Eigenwerte $\lambda_b$, zurück kommen sie alle. Die Zeile "Pauli channel eigenvalues, entanglement-assisted"; die Kanal-Version der Zwei-Kopien-Trennung.
* **Objekt:** Pauli-Kanal $\Lambda(\cdot) = \sum_ap_aP_a(\cdot)P_a$. **Zugriff:** Sample auf dem Choi-Zustand: $n$ Bell-Paare, eine Hälfte durch den Kanal, Bell-Messung; das Ancilla ist der Quantenspeicher. Ohne Ancilla, aber mit Verkettung (RB-artig), ist es Query-Zugriff, und der hilft nachweislich nicht.
* **Status:** 🟢 🟢 🟢 mit $n$ Ancilla-Qubits; 🔴 in den Kopien ohne.
* **Versprechen:** keines über den Kanal; die Ressource ist das verschränkte Ancilla.

### Das Problem

Die bekannten Lernvorteile (Mixedness-Testing, Unitarity-Testing, Pauli-Erwartungswerte) sind künstlich oder nicht rauschrobust implementierbar. Quantum Benchmarking ist eine echte Aufgabe; Pauli-Kanäle sind durch Randomized Compiling universell; die Sample-Komplexität ihrer Schätzung war trotz langer Literatur nicht charakterisiert, und Flammia–Wallman hatten die Frage nach Untergrenzen für RB-artige Protokolle offen gelassen.

### Kernresultate

* **Theorem 1 und Algorithmus 1.** Mit $k$ Ancilla-Qubits: $k$ Bell-Paare für ein Teilsystem, Stabilizerzustände und Syndrommessungen (Stabilizer-Überdeckung $\mathcal{O}$ von $\mathcal{P}_{n-k}$) für das andere; die Ausgangsverteilung ist die Walsh–Hadamard-Transformierte der $\lambda$, also $(-1)^{\langle u,v\rangle + \langle s,e\rangle}$ ein erwartungstreuer Schätzer; $N = O(|\mathcal{O}|n\epsilon^{-2}\log\delta^{-1})$.
* **Corollary 2.** Mit $2^{n-k}+1$ MUBs als Überdeckung: $O(n2^{n-k}\epsilon^{-2}\log\delta^{-1})$; für $k = n$ also $O(n/\epsilon^2)$; experimentell einfacher mit $3^{n-k}$ Pauli-Messungen.
* **Theorem 3 (Untergrenzen)** für Genauigkeit $1/2$: (A) $\Omega(n2^{n-k})$ nicht-adaptiv, nicht-verkettend, $k$ Ancillas, scharf; (B) $\Omega(2^{(n-k)/3})$ adaptiv, nicht-verkettend; (C) $\Omega(2^{n/3})$ Runden für adaptive, verkettende, ancilla-freie Protokolle, also für alle RB-Varianten; (D) $\Omega(n)$ für beliebig verschränkte Messungen, also ist Algorithmus 1 mit $n$ Ancillas optimal, und mehr als $n$ Ancillas helfen nicht.
* **Benchmarking-Protokoll** im Supplement: Sequenzen zufälliger Pauli-Gatter mit verrauschten Bell-Präparationen und -Messungen, SPAM-robust und exponentiell sample-effizienter als jedes ancilla-freie Verfahren, sofern das Ancilla isoliert und langlebig ist (Ionenfallen).
* Bemerkung: Die Fehlerraten $p$ in $\ell_\infty$ sind mit $O(\log n)$ unverschränkten Samples lernbar (Flammia–O'Donnell); der Vorteil betrifft die Eigenwerte.

### Methodischer Ansatz

* **Konstruktion.** Die Kanäle $\Lambda_{(a,s)} = \frac1{2^n}(I\,\mathrm{Tr}(\cdot) + sP_a\mathrm{Tr}(P_a\cdot))$, $a\in[4^n-1]$, $s = \pm1$: Ein Eigenwert-Lerner identifiziert $(a,s)$. (A) folgt informationstheoretisch, (B) und (C) per Reduktion auf Diskrimination gegen den vollständig depolarisierenden Kanal mit der Tree-Methode von Huang, Kueng, Preskill; (D) per Teleportation Stretching (Reduktion auf POVMs auf Kopien des Choi-Zustands) plus Holevo.
* Die Rolle des Ancillas: Ohne es gibt es keine Messeinstellung, die aus $p$ sampelt und alle $\lambda$ zugleich sieht; mit $n$ Bell-Paaren wird jedes $P_a$ auf einen eindeutigen Ausgang abgebildet (Superdense-Coding-Prinzip).

### Bedeutung und Anwendungen

* Erster praxisnaher, rauschrobuster Lernvorteil; die Trennung Ancilla gegen Verkettung ist neu: Das Ancilla bringt den exponentiellen Gewinn, die Sequenz nicht.
* Die $k$-Ancilla-Tauschkurve ist die erste quantitative Ressourcenaussage zwischen $k = 0$ und $k = n$ und ein Beispiel für die offene Frage (2) der Estimating-Sektion.
* Motiviert Subramanian, Kwon, Jiang (2026) zur Verallgemeinerung auf Qudit- und bosonische Kanäle mit $c$-Kopien-Zugriff und Konjugatkanal.

### Bezug zum eigenen Projekt

* Das ist die Kanal-Version der eigenen Messung: $n$ Bell-Paare, Kanal auf eine Hälfte, Bell-Messung entspricht Bell-Sampling auf dem Choi-Zustand, und die Verteilung ist die Walsh–Hadamard-Transformierte des Spektrums. Für Displacement-Kanäle auf Qudits ist die Transformation die symplektische Fourier-Transformation über $\mathbb{Z}_d^2$.
* Die Aussage, dass Verkettung (Query) nicht hilft, aber das Ancilla (Speicher) exponentiell, ist die genaue Form der Trennung der Achsen, die die eigene Übersicht postuliert: Query kauft Rate, Speicher kauft Dimension.
* Die Ergebnisse (A) und (B) zeigen, dass $o(n)$ Ancillas fast nichts bringen; für das eigene Projekt heißt das, dass ein "halber" zweiter Zustand (etwa ein unvollkommenes Konjugat auf wenigen Qudits) keinen exponentiellen Gewinn erwarten lässt, sofern die Analogie trägt.

### Grenzen und offene Fragen

* Untergrenzen für Genauigkeit $1/2$; die $\epsilon$-Abhängigkeit ist nur oben bewiesen.
* Nur Eigenwerte; für andere Eigenschaften (Fehlerraten in anderen Metriken, strukturierte Kanäle) offen.
* Das Benchmarking-Protokoll braucht ein isoliertes Ancilla; auf Plattformen mit Übersprechen ist der Vorteil fraglich.
* Experimenteller Vergleich mit ancilla-freien Verfahren steht aus.

### Fragen zum Tieferbohren

* Wie sieht Algorithmus 1 für Displacement-Kanäle auf Qudits aus, und ist die Stabilizer-Überdeckung von $\mathbb{Z}_d^{2(n-k)}$ mit $d^{n-k}+1$ MUBs für zusammengesetztes $d$ verfügbar?
* Wo genau versagt die Tree-Methode, wenn der Lerner das Konjugat $\Lambda^*$ des Kanals hat, und ist das der Mechanismus hinter Subramanian et al. Theorem IV.1?
* Ist die Aussage "mehr als $n$ Ancillas helfen nicht" das Kanal-Analogon von "zwei Kopien sind der Sweet Spot"?

Paper: [arXiv:2108.08488](https://arxiv.org/abs/2108.08488)

---

## Quantum channel learning with limited parallel access (arXiv:2608.05307)

Die Arbeit von **Mahadevan Subramanian, Hyukgun Kwon und Liang Jiang** (Chicago, Sejong; 2026) überträgt die Lernhierarchien für Zustände (Zwei-Kopien-Vorteil, $d$-Kopien-Vorteil für Qudits, Konjugatvorteil) auf Kanäle. Das Objekt ist die Heisenberg–Weyl-Transfermatrix $C_{\mathcal{E}}((q_i,p_i),(q_o,p_o)) = \mathrm{Tr}[D(q_o,p_o)\mathcal{E}(D(q_i,p_i))]/d^m$ eines Qudit-Kanals, oder ihre bosonische Version über zwei-Moden-gequetschte Choi-Zustände. Ein Master-Lemma liefert Untergrenzen für alle $c$-Kopien-Protokolle mit unbeschränkten Ancillas und Adaptivität, in jeder Dimension. Ergebnis: Mit $\mathcal{E}\otimes\mathcal{E}^*$ sind die Beträge mit $O(\log(M/\delta)/\epsilon^4)$ Messungen lernbar, und das ist scharf; ohne $\mathcal{E}^*$ ist jedes $c < d$ exponentiell in der Qudit-Zahl, bei $c = d$ wird es effizient mit $\epsilon^{-2d}$, und bosonisch bleibt es für alle $c = O(1/\epsilon)$ exponentiell.

### Einordnung in die Tabellen

* **Task type:** Estimating. Gegeben eine beschränkte Menge $Q$ von $M$ Anfragen $(q_i,p_i,q_o,p_o)$, zurück kommen die Beträge $|C_{\mathcal{E}}(Q)|$. Neue Zeile "Heisenberg–Weyl transfer matrix, limited parallel access" der Estimating-Tabelle, direkt unter Chen, Zhou, Seif, Jiang.
* **Objekt:** Kanal auf $m$ Qudits (Primzahl $d$) oder $m$ bosonischen Moden. **Zugriff:** $c$ parallele Kopien von $\mathcal{E}$ oder von $\mathcal{E}\otimes\mathcal{E}^*$ pro Messrunde, mit beliebigen Ancillas, adaptiver Zustandspräparation und POVM (auch unendlich feine); Kanalanfragen $\Theta(cT)$ bei $T$ Runden. Das ist Sample-Zugriff auf den Choi-Zustand mit Speicher $c$ Kopien, also die Speicherachse für Kanäle.
* **Status:** 🟢 🟢 🟢 mit Konjugatkanal; 🟢 in Kopien bei $c = d$ mit $\epsilon^{-2d}$; 🔴 für $c < d$ und bosonisch.
* **Versprechen:** keines über den Kanal; die Ressourcen sind $\mathcal{E}^*$ und die Parallelität $c$.

### Das Problem

Für Zustände ist bekannt: Pauli-Erwartungswerte brauchen zwei Kopien, Heisenberg–Weyl-Erwartungswerte auf Qudits $d$ Kopien, und $\rho\otimes\rho^*$ gibt einen exponentiellen Vorteil, auch bosonisch. Für Kanäle gab es die Pauli-Transfermatrix auf Qubits und die Ancilla-Trennung von Chen, Zhou, Seif, Jiang; für Qudits und Bosonen fehlte ein allgemeiner Rahmen. Kann man die Transfermatrix mit beschränkter paralleler Nutzung des Kanals effizient schätzen, und was ändert der Konjugatkanal $\mathcal{E}^*$ (mit $\mathcal{E}^*(\rho^T)^T = \mathcal{E}(\rho)$ in fester Basis)?

### Kernresultate

* **Lemma III.1 (Master-Lemma).** Untergrenze für alle $c$-Kopien-Protokolle in einer Klasse von Viele-gegen-eins-Kanaldiskriminationsaufgaben, unabhängig von Dimensionen, mit Operatornormen bestimmter Summen von Kanaloperatoren als einziger Eingabe; behandelt auch unbeschränkte Messoperatoren (Homodyn) über eine Radon–Nikodym-Konstruktion. Ein Spezialfall (Corollary B.5.2) reduziert auf Zustandslernen (Ersatzkanal) und verschärft dort bekannte Schranken.
* **Theorem IV.1 (mit Konjugat).** Einzelkopien-Zugriff auf $\mathcal{E}\otimes\mathcal{E}^*$ mit Ancilla: $O(\log(M/\delta)\epsilon^{-4})$ Messungen, nicht-adaptiv, per verallgemeinerter Bell-Messung auf $(\mathcal{E}\otimes I)(\sigma)\otimes(\mathcal{E}^*\otimes I)(\sigma^T)$ mit Bell-Paaren bzw. TMSV als $\sigma$; Theoreme IV.6/IV.7: $T = \Omega(c^{-4}\epsilon^{-4})$ für $c$-Kopien-Zugriff auf $\mathcal{E}\otimes\mathcal{E}^*$, also ist $\epsilon^{-4}$ scharf.
* **Theorem IV.2 (ohne Konjugat, Qudits).** Für $c\leq\min(d,d')-1$: $T = \Omega(d^md'^{m'}c^{-2}\epsilon^{-2})$; für $c\geq d$ (mit $d = d'$) bis auf Konstanten $T = \Omega(\min\{d^{m+m'}/(c\epsilon)^2, (d/(c\epsilon))^{2d}\})$: scharfer Übergang bei $c = d$, und $\epsilon^{-2d}$ ist scharf gegen den $d$-Kopien-Algorithmus mit $O(d(m+m')\log(d/\delta)\epsilon^{-2d})$.
* **Theorem IV.3 (ohne Konjugat, Bosonen).** $T = \Omega(d_{\mathrm{in}}^md_{\mathrm{out}}^{m'}c^{-2}\epsilon^{-2})$ für alle $c = O(1/\epsilon)$ mit effektiven Modendimensionen $d_{\mathrm{in}} = \sqrt{1 + (0.99\kappa\tanh 2r)^2}$, $d_{\mathrm{out}} = \sqrt{1 + (0.99\kappa')^2}$ bei Energieschranken $\kappa$; kein Übergang, weil die effektive Dimension mit der Genauigkeit wächst.
* **Theoreme IV.4, IV.5 (selbstkonjugiert, eine Kopie).** Selbst für $\mathcal{E} = \mathcal{E}^*$ bleibt Einzelkopien-Zugriff $\Omega(d^md'^{m'}\epsilon^{-2})$; ab $c = 2$ greift Theorem IV.1.
* **Abschnitt V (Hierarchie).** Für quadratfreies $d$ braucht man genau $d$ Kopien; für allgemeines $z$ das Produkt der Primteiler; eine Familie bosonischer Kanäle bleibt für jedes $c = O(1/\epsilon)$ hart; sequentieller Zugriff ist strikt stärker und bleibt offen.

### Methodischer Ansatz

* Die Kanaldiskriminationsfamilien $\mathcal{E}_{(q_1,p_1),(q_2,p_2)}$ mit Kraus-artigen Operatoren $\frac1{\sqrt2}(e^{i\pi/4}D + e^{-i\pi/4}D^\dagger)$ gegen das maximal gemischte Ziel; die Operatornorm von $\sum_{q,p}D(q,p)^{\otimes 2k}$ ist $d^m$ für $k\neq0\bmod d$ und $d^{2m}$ für $k = 0\bmod d$ (Lemma B.8), und genau daraus entsteht der Übergang bei $c = d$: Erst wenn $c$ Kopien der Displacement-Operatoren kommutieren, wird die Statistik informativ.
* Mit dem Konjugat sind $D\otimes D^*$ für alle Adressen kommutierend, und die Terme $k = l\bmod d$ dominieren; das gibt $\epsilon^{-4}$ ohne Dimensionsfaktor.
* Für Bosonen: TMSV-Choi-Zustände mit endlichem Squeezing $r$, damit die Transferfunktion beschränkt bleibt; die naive Transferfunktion $\mathrm{Tr}[D(\beta)\mathcal{E}(D^\dagger(\alpha))]$ ist unbeschränkt und nicht lernbar (Anhang C 1 b).

### Bedeutung und Anwendungen

* Vereinheitlicht die Zustandslern-Hierarchien in einem Kanal-Rahmen, der Qubits, Qudits und Bosonen umfasst, und benennt den Konjugatkanal als Ressource mit tight $\epsilon^{-4}$.
* Der Konjugatkanal ist verfügbar, wenn alle Kraus-Operatoren in einer Basis reell sind (reelle Stinespring-Dilatation mit selbstkonjugierter Umgebung); ein Superkanal, der $\mathcal{E}^{\otimes k}$ in $\mathcal{E}^*$ verwandelt, existiert nicht.
* Zeigt, dass die trace-distance-Beziehung zwischen TMSV-Choi-Zuständen und energiebeschränkter Diamantnorm exponentielle Vorfaktoren haben kann (Anhang C 2): ein Beitrag zur Frage nach der richtigen Metrik für bosonische Kanäle.

### Bezug zum eigenen Projekt

* Das ist die Kanalfassung von Objective 3 mit exakt dem Objekt des Projekts, $D(q,p)$ auf Qudits, und dem Konjugat als Ressource. Die Ergebnisse übersetzen sich direkt: Bell-Sampling auf $\rho\otimes\rho^*$ ist der Ersatzkanal-Spezialfall, und Corollary B.5.2 verschärft die Untergrenzen für $c$-Kopien-Zustandslernen aus dem bosonischen Konjugat-Paper exponentiell (Theorem B.22).
* Der Übergang bei $c = d$ ist die präzise Form der Aussage "Bell-Sampling auf identischen Kopien versagt für Qudits" aus der Suchtabelle: Nicht zwei, sondern $d$ Kopien machen $D^{\otimes c}$ kommutierend, und $\epsilon^{-2d}$ ist der Preis. Für zusammengesetztes $d$ zählt das Produkt der Primteiler; für die zyklische Ein-Qudit-Basis des Projekts ist das die relevante Zahl.
* $\epsilon^{-4}$ ist scharf für $\mathcal{E}\otimes\mathcal{E}^*$ mit beliebig vielen parallelen Kopien: Die $\epsilon^{-4}$ der Magnitudenschätzung in Phase 1 sind also keine Schwäche des Protokolls, sondern eine Eigenschaft der Ressource, jedenfalls für Beträge.
* Das Master-Lemma ist ein Werkzeug, um eigene Untergrenzen für die Top-$k$-Lokalisierung mit $\rho\otimes\rho^*$ zu formulieren; es braucht nur Operatornormen von Summen über die Kandidatenadressen.

### Grenzen und offene Fragen

* Nur Beträge; die Phase von $C_{\mathcal{E}}$ ist bosonisch ohne Kenntnis der Anfragen nicht schätzbar, und für Qudits nur über Hypothesenzustände wie bei King, Wan, McClean.
* Paralleler Zugriff; sequentielle Protokolle mit beschränktem Ancilla sind offen und vermutlich stärker.
* Die Konstanten ($0.75$, $0.99$, $0.11$) sind Beweisartefakte; die Grenzen gelten für "große" $m$.
* Die bosonische Aufgabe hängt von der Squeezing-Stärke $r$ und den Energieschranken ab; die Metrikfrage ist offen.

### Fragen zum Tieferbohren

* Wie sieht der Übergang bei $c = d$ für die zyklische Ein-Qudit-Basis mit zusammengesetztem $d$ konkret aus, und welche Kopienzahl braucht das eigene Protokoll ohne Konjugat für $d = 64$?
* Lässt sich das Master-Lemma auf die Aufgabe "finde die $k$ größten $|y_{q,p}|$" anwenden, um eine Sample-Untergrenze für Phase 1 mit und ohne $\rho^*$ zu gewinnen?
* Was ist die reelle Stinespring-Bedingung für Zustände statt Kanäle: Welche Präparationen liefern $\rho^*$ physikalisch, und deckt sich das mit Anhang D bei King, Wan, McClean?

Paper: [arXiv:2608.05307](https://arxiv.org/abs/2608.05307)

<br>

# Identifying

**Identifying** (candidate *states* or functions are *input*). Given: copies of $\rho$ and a list of $M$ candidate states, or a class $\mathcal{C}$ with or without the promise that $\rho \in \mathcal{C}$. Returned: one index, one object from the class, or one bit. Like matching a sample against a database of known genomes: the hypotheses exist before the data. Sub-cases by the size of the list: $M = 2$ is state discrimination, general $M$ is hypothesis selection, a class with a promise is learning that class, a class without the promise is agnostic tomography, one bit is property testing, and $M = 1$ is certification. Identifying behaves like estimating in every budget as long as the list is polynomial and the candidates are efficiently representable. Once the class is exponentially large and parametrized, the task shades into searching, which is where the hardness rows of this table come from.

**What is known.** The two-hypothesis case is solved exactly: Helstrom for minimum error, unambiguous discrimination for zero error with abstention, and the quantum Chernoff exponent for many copies. Hypothesis selection needs only $O(\log M)$ copies through threshold search. A catalogue of classes is learnable in polynomial time, each by exploiting the structure that defines it: stabilizer states and Clifford circuits by linear algebra, states with $t$ non-Clifford gates at cost $2^t$, Gaussian and near-Gaussian states, matrix product states, states of shallow circuits, phase states of bounded degree, juntas, low-degree objects. Property testing shows the memory axis at its sharpest: purity costs $O(1)$ copies with a SWAP test and $\Omega(2^{n/2})$ without, and mixedness testing with incoherent measurements costs $\Theta(d^{3/2}/\epsilon^2)$ whether or not the measurements are adaptive, against $\Theta(d/\epsilon^2)$ with entangled ones. Certification of almost all states is possible with single-qubit measurements.

**Efficiency status.** Copies: 🟢 throughout; the class results are polynomial, the testing results constant. Time and memory: 🟢 on the catalogue, and provably 🔴 outside it under cryptographic assumptions. Pseudorandom states and pseudoentanglement are statistically learnable yet computationally indistinguishable from Haar; states of polynomial gate complexity need only $\tilde\Theta(G)$ copies but admit no polynomial-time learner; output distributions of circuits become hard under LPN with a single $T$ gate. These rows are this column's version of the LWE wall in the searching column.

**What is open.**
* (1) The magic threshold. $t = O(\log n)$ non-Clifford gates is the frontier of polynomial time; whether $\mathrm{poly}(n, 2^t)$ is optimal is open.
* (2) Depth. Constant-depth circuits are learnable and polynomial-depth ones are hard; everything in between is uncharted.
* (3) Agnostic and tolerant learning beyond stabilizer-type classes.
* (4) Average-case hardness. The pseudorandomness constructions are worst-case; whether physically motivated classes sit on the easy side is the same question as in the searching column.

| Protocol or class | Object | Task type: given → returned | Copies or queries (access) | Time | Memory | Status & Condition |
| --- | --- | --- | --- | --- | --- | --- |
| **Pseudorandom states and pseudoentanglement** (Ji, Liu, Song 2018; Aaronson, Bouland, Fefferman, Ghosh, Vazirani, Zhang, Zhou 2022) | State | Identifying: pseudorandom or Haar-random, entanglement $\Theta(n)$ or $\omega(\log n)$ across every cut → one bit | Sample: poly copies, information-theoretically learnable (random phase states are phase states of high degree); $t$ copies of a random subset phase state on $K$ strings are $O(t^2/K)$-close to Haar | No polynomial-time distinguisher under quantum-secure one-way functions; MPS testing needs $\Omega(\sqrt r)$ copies | poly, the key | 🟢 🔴 🟢; hard by construction |
| **Identification**: state discrimination ($M=2$), hypothesis selection (general $M$) | State | Identifying: list of $M$ states → one index | Sample: Helstrom (min error) vs. USD (zero error + abort); $O(\log M)$ | Dominated by handling the $M$ candidates: poly for efficiently representable states, $\exp(n)$ for generic ones | The $M$ candidates, same split | 🟢 🟢* 🟢*; *for efficiently representable candidates |
| **Agnostic tomography** (Grewal, Iyer, Kretschmer, Liang 2024; Chen, Gong, Ye, Zhang 2024) | State, mixed | Identifying against a class: class $\mathcal{C}$, no promise that $\rho \in \mathcal{C}$ → $\sigma\in\mathcal{C}$ with $F(\rho,\sigma) \geq \max_{\tau\in\mathcal{C}} F(\rho,\tau) - \epsilon$ | Sample: stabilizer product states $n^{O(\log(2/\tau))}/\epsilon^2$ by Bell difference sampling (Grewal et al.), improved to $n^2(1/\tau)^{O(\log 1/\tau)}/\epsilon^2$; all stabilizer states $n(1/\tau)^{O(\log 1/\tau)} + O(\log^2(1/\tau)/\epsilon^2)$ copies by stabilizer bootstrapping; stabilizer dimension $\geq n-t$ with $n(2^t/\tau)^{O(\log 1/\epsilon)}$; lower bound $\Omega(n/\tau)$ | $O(n^2(n+1/\epsilon^2))(1/\tau)^{O(\log 1/\tau)}$, polynomial for $\tau \geq e^{-c\sqrt{\log n}}$ | poly, a tableau | 🟢 🟢 🟢 for best fidelity $\tau$ down to slightly sub-polynomial; the same algorithm estimates stabilizer fidelity, the first efficient magic estimator |
| **Purity and mixedness testing** (O'Donnell, Wright 2015; Bubeck, Chen, Li 2020; Chen, Cotler, Huang, Li 2021; Chen, Huang, Li, Liu 2022) | State | Identifying: pure or maximally mixed, $\rho = I/d$ or far from it → one bit | Sample: purity $O(1)$ copies with two-copy memory (SWAP test), $\Theta(2^{n/2})$ without; mixedness $\Theta(d/\epsilon^2)$ with entangled measurements, $\Theta(d^{3/2}/\epsilon^2)$ with incoherent ones, adaptive or not | poly | poly | 🟢 🟢 🟢 with two-copy memory; the simplest memory separation, and the proof that adaptivity does not replace memory |
| **State certification with incoherent measurements** (Chen, Huang, Li, Liu, FOCS 2022) | State, mixed, against a known $\sigma$ | Identifying, $M = 1$: $\rho = \sigma$ or $\Vert\rho - \sigma\Vert_1 > \epsilon$ → one bit | Sample, one copy at a time, adaptive allowed: between $\tilde\Omega(\sqrt{d\,\underline d_{\mathrm{eff}}}\,F(\underline\sigma, I/d)/\epsilon^2)$ and $\tilde O(\sqrt{d\,\overline d_{\mathrm{eff}}}\,F(\overline\sigma, I/d)/\epsilon^2)$, from $\Theta(1/\epsilon^2)$ for pure $\sigma$ to $\Theta(d^{3/2}/\epsilon^2)$ for $\sigma = I/d$ | poly | none | 🟢 🟢 🟢; instance-optimal in the reference state, the quantum analogue of instance-optimal identity testing |
| **Fixed-unitary and symmetry-class distinction** (Aharonov, Cotler, Qi, Nat. Commun. 2022; the QUALM paper) | Unitary, as a lab oracle | Identifying: one fixed Haar-random unitary on $\ell$ qubits applied at every call, or a fresh one per call → one bit; fixed unitary, orthogonal, or symplectic → one of three | Oracle calls on a fixed input with two-copy memory: $O(1)$ calls and a SWAP test on the outputs (a generalized SWAP test on a maximally entangled input for the symmetry class); every incoherent protocol, adaptive or not, needs $\Omega(2^{2\ell/7})$ calls | $O(\ell)$ gates | $2\ell$ qubits of quantum memory | 🟢 🟢 🟢 with coherent access; the process version of the purity separation, and the paper that defines coherent versus incoherent access |
| **Stabilizer testing** (Gross, Nezami, Walter 2021; tolerant: Arunachalam, Dutt 2024; Bao, van Dordrecht, Helsen 2024; Chen, Gong, Ye, Zhang 2024) | State | Identifying: stabilizer state or far from all of them → one bit; tolerant: stabilizer fidelity $\geq \epsilon_1$ or $\leq \epsilon_2$ | Sample: six copies per round, $O(1/\epsilon^2)$ rounds, three copies for qudits with $d \equiv 1, 5 \bmod 6$; tolerant with an unconditional polynomial gap $\epsilon_2 \leq C'\epsilon_1^{672}$ in $O(\epsilon_1^{-12})$ Bell-difference rounds | poly | $2n$ qubits | 🟢 🟢 🟢; Bell difference sampling, and a generalized uncertainty relation through the Lovász theta number for the tolerant case |
| **State certification** (Huang, Preskill, Soleimanifar 2024) | State | Identifying, $M = 1$: target $\vert\psi\rangle$ known through an amplitude model, copies of $\rho$ → accept if $\langle\psi\vert\rho\vert\psi\rangle \geq 1 - \epsilon/2\tau$, reject if $< 1 - \epsilon$ | Sample: $O(\tau^2/\epsilon^2)$ single-qubit Pauli measurements, $O(\tau/\epsilon)$ with general single-qubit measurements, where $\tau$ is the relaxation time of a hypercube walk with stationary distribution $\vert\langle x\vert\psi\rangle\vert^2$; $\tau = O(n^2)$ for all but a $2^{-\Omega(n)}$ fraction of states, $O(n)$ for phase and GHZ-like states; two model queries per copy | poly | none | 🟢 🟢 🟢; verification rather than learning, the cheapest task in the column, with a tolerance gap of $2\tau$ |
| **Clifford plus few non-Clifford gates** (Lai, Cheng 2022; Grewal, Iyer, Kretschmer, Liang 2023; Leone, Oliviero, Hamma 2024; Hangleiter, Gullans 2024) | State | Identifying against a class: at most $t$ non-Clifford gates → the state | Sample: $\mathrm{poly}(n, 2^t)$ | $\mathrm{poly}(n, 2^t)$, polynomial for $t = O(\log n)$ | poly | 🟢 🟢 🟢 up to logarithmic magic; the time budget grows as $2^t$, magic is the hardness dial |
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
* **Chen, Huang, Li, Liu (FOCS 2022):** Mixedness testing with incoherent measurements costs $\Theta(d^{3/2}/\epsilon^2)$, adaptive or not; instance-optimal bounds for certification against a known $\sigma$ in terms of $F(\sigma, I/d)$ and the effective dimension.
* **Gross, Nezami, Walter (CMP 2021):** Stabilizer testing with six copies. **Arunachalam, Dutt (2024) / Chen, Gong, Ye, Zhang (2024):** tolerant versions in polynomial time. **Bao, van Dordrecht, Helsen (2024):** an unconditional polynomial gap, $\epsilon_2 \leq C'\epsilon_1^{672}$ with $O(\epsilon_1^{-12})$ Bell-difference rounds, from a generalized uncertainty relation through the Lovász theta number.
* **Leone, Oliviero, Esposito, Hamma (PRA 2024):** Stabilizer-entropy phase transition at $t/f = 1$; in the localized phase the purity of a $t$-doped state is computable up to a factor $4^t$ with $\mathrm{poly}(n)$ resources, even when it is exponentially small.
* **White, Pollock, Hollenberg, Modi, Hill (PRX Quantum 2022):** Process-tensor tomography for non-Markovian dynamics by maximum likelihood; $O(kN^\ell)$ circuits at Markov order $\ell$ instead of $O(N^k)$.
* **Bădescu, O'Donnell (STOC 2021):** Threshold search and hypothesis selection with $O(\log M)$ copies.
* **Huang, Preskill, Soleimanifar (FOCS 2024):** Certifying almost all states with few single-qubit measurements.

**Notes on the identification rows.** Hypothesis selection at $O(\log M)$ copies comes from the *threshold search* primitive of Bădescu–O'Donnell (STOC 2021), the same tool that improved shadow tomography to $\tilde O(\log^2 M \cdot \log d/\epsilon^4)$. Agnostic tomography is the learning-theoretic analogue of agnostic PAC learning; Grewal–Iyer–Kretschmer–Liang (2024) and Chen–Gong–Ye–Zhang ("stabilizer bootstrapping", 2024) give polynomial-time algorithms for stabilizer and near-stabilizer classes, both driven by Bell difference sampling.

## Learning classes of states: the promise catalogue

Every 🟢 🟢 🟢 row in the identifying and searching tables names a class. Listed by the structure that makes decoding cheap, with the paper that proved it.

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

Zusammenfassungen der wichtigen Paper zum Aufgabentyp **Identifying**: die Kandidaten sind der Input. Gegeben sind Kopien eines Zustands, Aufrufe eines Prozesses oder klassische Samples einer Verteilung, dazu eine Liste von Hypothesen oder eine Klasse, mit oder ohne das Versprechen, dass das Unbekannte in der Klasse liegt. Zurück kommt ein Index, ein Element der Klasse oder ein Bit. Die Sektion ordnet die Paper nach der Größe der Hypothesenmenge: erst die Klassen, deren Struktur den Decoder billig macht (Stabilizer, Gauß, Matrixprodukt, flache Schaltkreise, Phasenzustände), dann die Ein-Bit-Aufgaben (Testen und Zertifizieren), zuletzt die Härteresultate, in denen die Klasse exponentiell groß und parametrisiert ist und die Aufgabe in Searching übergeht (Pseudozufall, beschränkte Gatterkomplexität, Output-Verteilungen).

Jede Zusammenfassung folgt demselben Aufbau wie in den Sektionen Searching und Estimating: Einordnung in die Tabellen, Problem, Kernresultate, Methode, Bedeutung, Bezug zum eigenen Projekt, Grenzen und offene Fragen, Fragen zum Tieferbohren. Die Statusglyphen lesen sich in der Reihenfolge Kopien · Zeit · Speicher. Zwei Paper der Identifying-Tabelle sind bereits in der Searching-Sektion zusammengefasst, weil ihr algorithmischer Kern eine Trägersuche ist: Grewal, Iyer, Kretschmer, Liang (arXiv:2305.13409) und Hangleiter, Gullans (arXiv:2306.00083); die Übersicht verweist dorthin.

## Übersicht

| Paper | Objekt | Was identifiziert wird | Zugriff | Kosten | Status | Versprechen |
| --- | --- | --- | --- | --- | --- | --- |
| Grewal, Iyer, Kretschmer, Liang 2024 (Stabilizer-Produktzustände) | gemischter Zustand | der beste Stabilizer-Produktzustand, agnostisch | Sample, Bell-Difference-Sampling plus Einzelkopien | $n^{O(\log(2/\tau))}/\epsilon^2$ | 🟢 🟢 🟢 für konstantes $\tau$ | keines; $\tau$ ist die beste Fidelity in der Klasse |
| Chen, Gong, Ye, Zhang 2024 (Stabilizer Bootstrapping) | gemischter Zustand | der beste Stabilizerzustand, agnostisch; Stabilizer-Fidelity | Sample, Ein- und Zweikopien-Messungen | $n(1/\tau)^{O(\log 1/\tau)} + O(\log^2(1/\tau)/\epsilon^2)$ Kopien, Zeit $O(n^2(n+1/\epsilon^2))(1/\tau)^{O(\log 1/\tau)}$ | 🟢 🟢 🟢 für $\tau\geq e^{-c\sqrt{\log n}}$ | keines; untere Schranke $\Omega(n/\tau)$ Kopien |
| Grewal, Iyer, Kretschmer, Liang 2023 | Zustand | Stabilizerdimension $\geq n-t$, dann Tomographie | Sample, Bell-Differenz | $\mathrm{poly}(n, 2^t, 1/\epsilon)$ | 🟢 🟢 🟢 bis $t = O(\log n)$ | siehe Searching (Papers), arXiv:2305.13409 |
| Hangleiter, Gullans 2024 | Zustand aus Schaltkreis | Clifford+T-Beschreibung, Nullity, Tiefe | Sample, Bell-Messung | $O(n/\epsilon) + O(2^t/\epsilon^2)$ | 🟢 🟢 🟢 bis $t = O(\log n)$ | siehe Searching (Papers), arXiv:2306.00083 |
| Leone, Oliviero, Esposito, Hamma 2024 | Zustand aus $t$-dotiertem Clifford-Schaltkreis | Subsystem-Purity $\mathrm{Pur}(\psi_E)$, auch wenn exponentiell klein | Query an $C_t$ (Clifford Completion), dann Stabilizer-Messungen | $\mathrm{poly}(n)\,e^{O(t)}$, polynomiell für $t = O(\log^2 n)$; Faktor $d_Y^2 = 4^t$ Unschärfe | 🟢 🟢 🟢 für $t/f\leq 1$ (lokalisierte Phase) | $t$-dotiert, $t/f\leq 1$ |
| Aaronson, Grewal 2023 | Zustand von $n$ freien Fermionen auf $m$ Moden | die Kernmatrix $K = AA^\dagger$, also den Zustand | Sample, $O(m)$ Messbasen aus Beamsplittern | $O(m^3n^2/\epsilon^4)$ Kopien, $O(m^4n^2/\epsilon^4)$ Zeit | 🟢 🟢 🟢 | teilchenzahlerhaltend gaußsch |
| Mele, Herasymenko 2024 | Zustand aus Gauß-Schaltkreis mit $t$ nicht-gaußschen Gattern | Gauß-Unitary $G$ und $t$-Qubit-Kern $\vert\phi\rangle$ | Sample, Einzelkopien | $\mathrm{poly}(n, 2^t)$; hart für $t = \tilde\omega(\log n)$ unter PRS | 🟢 🟢 🟢 bis $t = O(\log n)$ | Gauß-Nullity $\leq\kappa t$ |
| F. A. Mele, A. A. Mele, Bittel, Eisert, Giovannetti, Lami, Leone, Oliviero 2024 | CV-Zustand auf $n$ Moden | Gauß-Zustand, $t$-dotierter Gauß-Zustand; allgemein bei Energie $E$ | Sample, Homodyn/Heterodyn | Gauß $O(n^7E^4/\epsilon^4)$; $t$-dotiert $\mathrm{poly}(n) + O((nE/\epsilon)^{2\kappa t})$; allgemein $\Omega(\epsilon^{-2n})$ | 🟢 🟢 🟢 für Gauß und $\kappa t = O(1)$; 🔴 allgemein | Energieschranke, Gaußsches Versprechen |
| Cramer, Plenio, Flammia, Somma, Gross, Bartlett, Landon-Cardinal, Poulin, Liu 2010 | Zustand auf einer Kette | Matrixproduktzustand mit Bonddimension $D$ | Sample, lokale Messungen (Schema 2) oder lokale Unitaries plus Messungen (Schema 1) | linear viele Messeinstellungen, $\mathrm{poly}(N)$ Nachverarbeitung, zertifizierte Fidelity | 🟢 🟢 🟢 | MPS mit kleinem $D$; Schema 2 braucht ein gapped Parent-Hamiltonian |
| Fanizza, Galke, Lumbreras, Rouzé, Winter 2023 | translationsinvarianter Zustand auf der Kette | MPDO-Realisierung: $\rho$, $e$, Transfermatrizen $E_{k,l}$ | Sample, lokale Tomographie der Marginale auf $2s+1$ Plätzen | $\mathrm{poly}(t, m, 1/\eta, 1/\epsilon)$ Kopien, $O(m^2)$ Parameter | 🟢 🟢 🟢 | Dimension $m$, $s$-rekonstruierbar, Singulärwert $\geq\eta$ |
| Huang, Liu, Broughton, Kim, Anshu, Landau, McClean 2024 | Unitary konstanter Tiefe; Zustand $U\vert 0^n\rangle$ auf 2D-Gitter | ein Schaltkreis konstanter Tiefe | Sample auf Produkt-Inputs und Pauli-Outputs; Query; Kopien | $O(n^2\log n/\epsilon^2)$ Samples, $\mathrm{poly}(n)/\epsilon^2$ Zeit; $\Theta(1)$ Queries bei endlichem Gatterset; Zustände $2^{O(d^2)}(n/\epsilon)^{O(1)}$ Kopien | 🟢 🟢 🟢 | konstante Tiefe; 2D für Zustände |
| Landau, Liu 2024 | Zustand $U\vert 0^n\rangle$ auf $k$-dimensionalem Gitter | ein Schaltkreis der Tiefe $(2k+1)d$ | Sample, lokale Tomographie der Reduktionen | $\tilde O(n^4)2^{O(c)}/\epsilon^4$ Kopien, $c = O((3k)^{k+2}d)^k$ | 🟢 🟢 🟢 für $d = O(1)$ | Tiefe $d$ auf einem Gitter beliebiger Dimension |
| Arunachalam, Bravyi, Dutt, Yoder 2023 | Phasenzustand vom Grad $\ell$ | das Polynom $f$ | Sample, separabel oder verschränkt; Query an das Präparationsunitary | $\Theta(n^\ell)$ separabel, $\Theta(n^{\ell-1})$ verschränkt (PGM) | 🟢 🟢 🟢 separabel; PGM zeitineffizient | Grad $\ell$ über $\mathbb{F}_2$ oder $\mathbb{Z}_q$ |
| Gross, Nezami, Walter 2021 | Zustand | Stabilizer oder $\epsilon$-weit weg von allen | Sample, sechs Kopien, transversal | $O(1/\epsilon^2)$ Wiederholungen, drei Kopien für $d\equiv 1, 5 \bmod 6$ | 🟢 🟢 🟢 | keines; Ein-Bit-Test |
| Bao, van Dordrecht, Helsen 2024 | Zustand | Stabilizer-Fidelity $\geq\epsilon_1$ oder $\leq\epsilon_2$ | Sample, Bell-Difference-Sampling | $O(\epsilon_1^{-12})$ Runden bei $\epsilon_2\leq C'\epsilon_1^{672}$ | 🟢 🟢 🟢 | keines; toleranter Test |
| Chen, Cotler, Huang, Li 2021 | Zustand, Kanal | rein oder maximal gemischt; depolarisierend oder unitär; $U$, $O$ oder $Sp$ | Sample ohne Quantenspeicher (Baummodell), mit $k$ Qubits Speicher | $\Theta(2^{n/2})$ ohne Speicher, $O(1)$ mit; Shadow-Tomographie $\tilde\Theta(\min\{M, 2^n\}/\epsilon^2)$; $\Omega(2^{(n-k)/3})$ bei $k$ Qubits | 🟢 🔴 🟢 ohne Speicher | keines; Trennungen nach Speicher |
| Chen, Huang, Li, Liu 2022 | gemischter Zustand | $\rho = \sigma$ oder $\Vert\rho-\sigma\Vert_1 > \epsilon$ | Sample, inkohärent, adaptiv erlaubt | $\Theta(d^{3/2}/\epsilon^2)$ für Mixedness; instanzoptimal in $F(\sigma, I/d)$ und effektiver Dimension | 🟢 🟢 🟢 mit Kopien $d^{3/2}$; Adaptivität hilft nicht | keines |
| Aharonov, Cotler, Qi 2022 | Unitary als Lab-Orakel | fester oder frischer Haar-Unitary; $U$, $O$ oder $Sp$ | Orakel, kohärent oder inkohärent | $O(1)$ kohärent, $\Omega(2^{2\ell/7})$ inkohärent | 🟢 🟢 🟢 kohärent | keines; definiert QUALM |
| Huang, Preskill, Soleimanifar 2024 | Zustand $\rho$ gegen bekanntes $\vert\psi\rangle$ | $\langle\psi\vert\rho\vert\psi\rangle\geq 1-\epsilon$ oder $< 1-\epsilon$ | Sample, Einzelqubit-Pauli-Messungen; Query an ein Amplitudenmodell | $O(\tau^2/\epsilon^2)$, $O(n^2/\epsilon)$ für fast alle Zustände | 🟢 🟢 🟢 | Relaxationszeit $\tau = \mathrm{poly}(n)$ |
| White, Pollock, Hollenberg, Modi, Hill 2022 | nicht-Markovscher Prozess über $k$ Zeitschritte | Prozess-Tensor bei Markov-Ordnung $\ell$ | Query, Sequenzen von Kontrolloperationen | $O(N_{\mathrm{mle}}^k)$ Schaltkreise, $O(k N_{\mathrm{mle}}^\ell)$ bei Ordnung $\ell$; $d^{4k}$ Parameter | 🟢 🟢 🟢 für festes $\ell$ | endliche Markov-Ordnung |
| Ji, Liu, Song 2018 | Zustandsfamilie $\{\vert\phi_k\rangle\}$ | PRS oder Haar-zufällig | Sample, polynomiell viele Kopien | poly Kopien reichen statistisch, kein poly-Zeit-Unterscheider | 🟢 🔴 🟢 | Existenz quantensicherer PRF |
| Aaronson, Bouland, Fefferman, Ghosh, Vazirani, Zhang, Zhou 2022 | Zustandsfamilie | Verschränkung $\Theta(n)$ oder $\omega(\log n)$ über jeden Schnitt | Sample, polynomiell viele Kopien | kein poly-Zeit-Unterscheider; MPS-Test braucht $\Omega(\sqrt r)$ Kopien | 🟢 🔴 🟢 | quantensichere Einwegfunktion |
| Zhao, Lewis, Kannan, Quek, Huang, Caro 2023 | Zustand oder Unitary mit $G$ Gattern | eine $\epsilon$-nahe Approximation | Sample; Query | $\tilde\Theta(G/\epsilon^2)$ Kopien; Zeit $e^{\Omega(\min\{G, n\})}$ unter RingLWE | 🟢 🔴 🟢 | Gatterzahl $G$ |
| Hinsche, Ioannou, Nietner, Haferkamp, Quek, Hangleiter, Seifert, Eisert, Sweke 2023 | Output-Verteilung eines Schaltkreises | Generator oder Evaluator | Sample, klassische Bitstrings | Clifford: $O(n)$ Samples, poly Zeit; ein $T$-Gatter: LPN-hart | 🟢 🔴 🟢 | Clifford-Struktur |
| Nietner, Sweke, Hinsche, Ioannou, Haferkamp, Quek, Hangleiter, Seifert, Eisert 2025 | Output-Verteilung eines zufälligen Brickwork-Schaltkreises | ein $\epsilon$-naher Generator, im Mittel | Statistical Queries | $2^{\Omega(d)}$ Queries ab Tiefe $d = \Omega(\log n)$ mit konstanter Wahrscheinlichkeit; $\Omega(2^n)$ bei linearer Tiefe | 🟢 🔴 🟢 im SQ-Modell | keines; Average-Case |

Drei Familien. Die erste lernt eine Klasse, deren Struktur den Decoder trägt: Untergruppen (Stabilizer), Kovarianzmatrizen (Gauß), Transfermatrizen (Matrixprodukt), Lichtkegel (flache Schaltkreise), Polynome (Phasenzustände); die Kosten sind polynomiell, und die Härte sitzt in einem einzigen Parameter ($t$, $D$, $d$, $\ell$). Die zweite gibt ein Bit zurück, und dort entscheidet die Speicherachse: Bell-Differenz-Sampling und SWAP-Test brauchen zwei Kopien und konstant viele Runden, inkohärente Protokolle zahlen $d^{3/2}$ oder $2^{n/2}$. Die dritte beweist, dass außerhalb des Katalogs kein polynomieller Decoder existiert, jeweils bedingt auf eine kryptographische Annahme; das ist die Identifying-Version der LWE-Wand aus theory.md.

## Agnostic tomography of stabilizer product states (arXiv:2404.03813)

Die Arbeit von **Sabee Grewal, Vishnu Iyer, William Kretschmer und Daniel Liang** (UT Austin; Quantum 2026) führt das Modell der *agnostischen Tomographie* ein: Gegeben sind Kopien eines beliebigen, möglicherweise gemischten Zustands $\rho$ und eine Klasse $\mathcal{C}$; gesucht ist ein Element von $\mathcal{C}$, dessen Fidelity mit $\rho$ bis auf $\epsilon$ an das Maximum über $\mathcal{C}$ heranreicht. Für die Klasse der Stabilizer-Produktzustände geben die Autoren den ersten Algorithmus mit quasipolynomieller Laufzeit $n^{O(\log(2/\tau))}/\epsilon^2$, polynomiell sobald die beste Fidelity $\tau$ konstant ist.

### Einordnung in die Tabellen

* **Task type:** Identifying gegen eine Klasse ohne Versprechen. Die Klasse ist der Input, zurück kommt ein Element der Klasse; das Versprechen $\rho\in\mathcal{C}$ fällt weg und wird durch die Fidelity-Garantie relativ zum besten Element ersetzt. Das ist das Quantenanalogon des agnostischen PAC-Lernens.
* **Objekt:** gemischter $n$-Qubit-Zustand. **Zugriff:** Sample; Bell-Difference-Sampling auf vier Kopien plus Einzelkopien-Messungen in der Produktbasis.
* **Status:** 🟢 🟢 🟢 für konstantes $\tau$; für $\tau = o(1)$ quasipolynomiell in $n$. Kopien und Zeit $n^{O(\log(2/\tau))}/\epsilon^2$, Speicher polynomiell (ein Pauli-String und eine Basis).
* **Versprechen:** keines über $\rho$; $\tau$ ist ein Hilfsinput und lässt sich per Binärsuche finden.

### Das Problem

Realisierbares Lernen von Stabilizerzuständen (Montanaro 2017) setzt voraus, dass $\rho$ exakt in der Klasse liegt; schon schwache Depolarisierung bricht die Voraussetzung. Grewal, Iyer, Kretschmer, Liang (2023) hatten für allgemeine Stabilizerzustände einen agnostischen Algorithmus in exponentieller Zeit und einen polynomiellen nur oberhalb $\tau > \cos^2(\pi/8)$. Die Sample-Komplexität ist über Shadow-Tomographie immer polynomiell in $\log\vert\mathcal{C}\vert$; die Frage ist die Laufzeit. Schon für Produktzustände scheitert der naive Ansatz, jedes Qubit einzeln zu tomographieren: Beim GHZ-Zustand ist jede Ein-Qubit-Reduktion maximal gemischt, obwohl $\vert 0^n\rangle$ Fidelity $1/2$ hat.

### Kernresultate

* **Theorem 1.2 (agnostische Tomographie).** Für $\mathcal{C} = \{\vert 0\rangle, \vert 1\rangle, \vert +\rangle, \vert -\rangle, \vert i\rangle, \vert -i\rangle\}^{\otimes n}$ gibt es einen eigentlichen (proper) agnostischen Lerner, der ein $\vert\phi\rangle\in\mathcal{C}$ mit $\langle\phi\vert\rho\vert\phi\rangle\geq\max_{\varphi\in\mathcal{C}}\langle\varphi\vert\rho\vert\varphi\rangle - \epsilon$ ausgibt, in Zeit $n^{O(\log(2/\tau))}/\epsilon^2$, wenn das Maximum mindestens $\tau$ ist.
* **Lemma 2.1 (Entropiezählung).** Aus einer Verteilung über $\{0,1\}^n$ mit $\max_x D(x)\leq C/2^n$ zeigen $k\geq\log_{1/b}(n/\delta)$ Ziehungen mit Wahrscheinlichkeit $1-\delta$ Einsen auf allen bis auf $\log_2(C)/(1-H(b))$ Positionen. Angewandt auf Bell-Differenz-Samples aus der Stabilizergruppe $S$ heißt das: $O(\log n)$ Samples aus $S$ decken alle bis auf $O(\log(1/\tau))$ Qubits mit einem nichttrivialen Pauli ab.
* **Trägerlemma.** Die Wahrscheinlichkeit, dass ein Bell-Differenz-Sample in $S$ liegt, ist $p\geq\tau^4$; also reichen $O(\log n/\tau^4)$ Samples, damit $\Omega(\log n)$ davon aus $S$ kommen, und die Suche über alle lokal kommutierenden Teilmengen der Größe $O(\log n)$ kostet $\binom{\log n/\tau^4}{\log n}\mathrm{poly}(1/\tau)\leq n^{O(\log(2/\tau))}$.
* **Theorem 3.5 (Algorithmus 1).** Aus dem Pauli-String vollen Gewichts wird die Produktbasis $B$ gebildet, $\rho$ wird $O(\log(1/\delta)/\epsilon^2)$-mal in $B$ gemessen, und der Modus ist die Ausgabe; die Fidelity-Garantie folgt, weil $B$ orthonormal ist.

### Methodischer Ansatz

* Die Stabilizergruppe eines Produktzustands ist bis auf Phasen durch einen einzigen Pauli-String des Gewichts $n$ festgelegt; man muss jedem Qubit nur $X$, $Y$ oder $Z$ zuordnen. Bell-Differenz-Samples liefern Elemente von $S$ mit Wahrscheinlichkeit $\geq\tau^4$, und lokale Kommutativität schließt widersprüchliche Zuordnungen aus.
* Die Entropiezählung ersetzt die Suche nach $n$ unabhängigen Generatoren durch $O(\log n)$ Samples; die verbleibenden $O(\log(1/\tau))$ Qubits werden per Brute Force über $3^{O(\log(1/\tau))}$ Möglichkeiten ergänzt.
* Ein Parameter $b\in(1/2, 1)$ steuert den Tausch zwischen Samplezahl und Restqubits; die Autoren empfehlen numerische Optimierung.

### Bedeutung und Anwendungen

* Erstes Paper, das agnostische Tomographie als eigenständiges Modell formuliert und einen effizienten Fall angibt; die Folgearbeiten (Chen, Gong, Ye, Zhang 2024 für alle Stabilizerzustände und diskrete Produktzustände; Bakshi et al. für Produktzustände gemischter Form; agnostische Prozess-Tomographie) bauen darauf auf.
* Anwendungsbild: eine Ansatzklasse für einen komplizierten Laborzustand finden und dann mit dem Ansatz weiterrechnen; auch als Unterroutine für Stabilizer-Zerlegungen magischer Zustände.
* Briët und Castro-Silva haben die Ideen auf ein quadratisches Goldreich–Levin und den Gowers-Inverse-Satz übertragen: Die Brücke zur klassischen Fourier-Analyse, die dieses Dokument bei Montanaro–Osborne zieht, läuft auch rückwärts.

### Bezug zum eigenen Projekt

* Das Modell ist die richtige Sprache für Versprechensregime 3: Wenn der Zustand nicht exakt in der Klasse liegt, ist "die beste Approximation bis auf $\epsilon$" die einzige Garantie, die noch beweisbar ist. Für die Displacement-Spektren heißt das: Der Top-$k$-Träger ist agnostisch zu definieren, relativ zum besten $k$-sparsamen Spektrum.
* Bell-Difference-Sampling auf $\rho^{\otimes 4}$ ist die Vier-Kopien-Verwandte des Zwei-Kopien-Protokolls auf $\rho\otimes\rho^*$: Beide ziehen aus der charakteristischen Verteilung, das eine aus $p_\psi * p_\psi$ (Faltung), das andere aus $\vert\mathrm{Tr}(\rho D)\vert^2$ selbst. Die Faltung ist der Preis dafür, ohne konjugierte Kopie auszukommen.
* Der Faktor $\tau^4$ im Trägerlemma ist ein Vorbild dafür, wie eine Fidelity-Schwelle in eine Samplezahl übersetzt wird, wenn Phase 1 nur Beträge liefert.

### Grenzen und offene Fragen

* Laufzeit quasipolynomiell für $\tau = o(1)$; Chen, Gong, Ye, Zhang erreichen $n^2(1/\tau)^{O(\log 1/\tau)}/\epsilon^2$ mit Ein- und Zweikopien-Messungen und geben für diskrete Produktzustände ein Verfahren mit Einzelkopien.
* Nur Produktzustände; die Verallgemeinerung auf beliebige Stabilizerzustände braucht Bootstrapping.
* $\tau$ muss bekannt oder per Suche geschätzt werden.

### Fragen zum Tieferbohren

* Wie sieht die Entropiezählung aus, wenn die Samples nicht aus $\{0,1\}^n$, sondern aus $\mathbb{Z}_d^{2n}$ kommen, und was ersetzt "nichttriviales Pauli auf Qubit $j$" bei Qudits?
* Lässt sich die Schranke $p\geq\tau^4$ mit konjugierten Kopien $\rho\otimes\rho^*$ auf $\tau^2$ verbessern, weil die Faltung wegfällt?
* Welche Klassen sind "stabilizer-artig" genug für den Trick, dass ein einziger Generator die Gruppe festlegt?

Paper: [arXiv:2404.03813](https://arxiv.org/abs/2404.03813)

---

## Stabilizer bootstrapping: a recipe for efficient agnostic tomography and magic estimation (arXiv:2408.06967)

Die Arbeit von **Sitan Chen, Weiyuan Gong, Qi Ye und Zhihan Zhang** (Harvard, Tsinghua; 2024) gibt einen allgemeinen Rahmen für agnostische Tomographie, das *Stabilizer Bootstrapping*, und löst damit die offene Frage nach einem polynomiellen agnostischen Lerner für Stabilizerzustände bei beliebiger bester Fidelity $\tau$ bis hinunter zu $\tau\geq\exp(-c\sqrt{\log n})$. Nebenprodukte sind der erste effiziente Schätzer der Stabilizer-Fidelity, eine Aussage über die Optimierungslandschaft und agnostische Lerner für Zustände hoher Stabilizerdimension und diskrete Produktzustände.

### Einordnung in die Tabellen

* **Task type:** Identifying gegen eine Klasse ohne Versprechen; zusätzlich Estimating einer einzelnen Größe (Stabilizer-Fidelity, Theorem 1.3) als Korollar. Die Liste-Dekodierung (alle approximativen lokalen Maximierer) hat Searching-Charakter.
* **Objekt:** gemischter $n$-Qubit-Zustand. **Zugriff:** Sample; Ein- und Zweikopien-Messungen, Bell-Difference-Sampling für die Stabilizerfälle, nur Einzelkopien für diskrete Produktzustände.
* **Status:** 🟢 🟢 🟢 für $\tau\geq\exp(-c\sqrt{\log n})$: $n(1/\tau)^{O(\log 1/\tau)} + O(\log^2(1/\tau)/\epsilon^2)$ Kopien, Zeit $O(n^2(n + 1/\epsilon^2))(1/\tau)^{O(\log 1/\tau)}$. Untere Schranke $\Omega(n/\tau)$ Kopien für $\epsilon < \tau/3$.
* **Versprechen:** keines über $\rho$; die Klasse liefert die Struktur.

### Das Problem

Montanaro lernt exakte Stabilizerzustände, Grewal et al. agnostisch nur für $\tau > \cos^2(\pi/8)$ in polynomieller Zeit. Für $\tau = o_n(1)$ war kein polynomieller agnostischer Algorithmus für irgendeine interessante Klasse bekannt. Zugleich fehlte ein effizienter Schätzer für die Stabilizer-Fidelity $\max_{S}\langle S\vert\rho\vert S\rangle$, das natürliche Magic-Maß.

### Kernresultate

* **Theorem 1.2 (Stabilizerzustände).** Für $1\geq\tau\geq\epsilon\geq 0$ und $\max_{\phi'\in\mathcal{C}}\langle\phi'\vert\rho\vert\phi'\rangle\geq\tau$ liefert der Algorithmus einen Stabilizerzustand mit $\langle\phi\vert\rho\vert\phi\rangle\geq\tau-\epsilon$; Kosten wie oben, passend zu Montanaro im realisierbaren Fall $\tau = 1$.
* **Theorem 1.3 (Stabilizer-Fidelity).** Schätzung bis auf $\epsilon$ in Zeit $n^3(1/\epsilon)^{O(\log 1/\epsilon)}$ mit $n(1/\epsilon)^{O(\log 1/\epsilon)}$ Kopien.
* **Korollar 6.2 (Liste).** Eine Liste der Länge $(1/\tau)^{O(\log 1/\tau)}$ enthält alle Stabilizerzustände mit Fidelity $\geq\tau$, die $(1/2+\xi)$-approximative lokale Maximierer sind; es gibt also nur $(\xi\tau)^{-O(\log 1/\tau)}$ davon, für beliebige gemischte $\rho$.
* **Theorem 1.5 (Stabilizerdimension $\geq n-t$).** Kopien $n(2^t/\tau)^{O(\log 1/\epsilon)}$, Zeit $n^3(2^t/\tau)^{O(\log 1/\epsilon)}$; nahe $\tau = 1$ wieder $\mathrm{poly}(n, 2^t, 1/\epsilon)$. Erster agnostischer Lerner für dotierte Zustände, allerdings improper.
* **Theorem 1.6 (diskrete Produktzustände).** Für $\mathcal{K}^{\otimes n}$ mit paarweise $\vert\langle\phi_1\vert\phi_2\rangle\vert^2\leq 1-\mu$: $(n\vert\mathcal{K}\vert)^{O((1+\log 1/\tau)/\mu)}/\epsilon^2$ mit Einzelkopien; **Theorem 1.7** verbessert für Stabilizer-Produktzustände auf $n^2(1/\tau)^{O(\log 1/\tau)}/\epsilon^2$.
* **Theorem 1.8 (untere Schranke).** $\Omega(n/\tau)$ Kopien für agnostische Tomographie von Stabilizerzuständen, $\Omega(1/\tau)$ schon für reine $\rho$, $\Omega(1/\epsilon)$ für die Fidelity-Schätzung.

### Methodischer Ansatz

* Das Rezept: (1) eine Familie kommutierender Projektoren $\Pi$ mit $\mathrm{Tr}(\Pi\rho)\geq\Omega(1)$ sammeln ("hohe Korrelation"); (2) ist sie vollständig, in der gemeinsamen Eigenbasis messen, dann fällt $\vert\phi\rangle$ mit Wahrscheinlichkeit $\tau$; (3) sonst einen Projektor niedriger Korrelation ziehen, der $\vert\phi\rangle$ stabilisiert; (4) alle weiteren Kopien mit $\Pi_{\mathrm{low}}$ nachselektieren. Die Fidelity des nachselektierten Zustands wächst um einen konstanten Faktor, $\langle\phi\vert\rho'\vert\phi\rangle\geq c\tau$ mit $c > 1$, also endet die Rekursion nach $O(\log 1/\tau)$ Runden.
* Der Preis ist die Erfolgswahrscheinlichkeit von Schritt (3) in jeder Runde; die Laufzeit ist von der Wiederholung dominiert, deshalb $(1/\tau)^{O(\log 1/\tau)}$.
* Für Stabilizerzustände kommen die Projektoren aus Bell-Difference-Sampling; für Produktzustände aus lokalen Messungen.

### Bedeutung und Anwendungen

* Erster allgemeiner Rahmen für agnostische Tomographie mit Anwendungen auf vier Klassen; die Magic-Schätzung ist praktisch relevant für die Charakterisierung von Geräten.
* Die Landschaftsaussage (nur quasipolynomiell viele approximative lokale Maximierer) ist ein algorithmischer Beweis eines Strukturresultats über die Stabilizer-Polytope.
* Verbindung zu Kryptographie: Ein polynomieller Algorithmus für $\tau = 1/\mathrm{poly}(n)$ würde für Subset-Zustände das Finden eines $O(\log n)$-dimensionalen affinen Raums mit maximalem Schnitt lösen, verwandt mit LPN und LSN.

### Bezug zum eigenen Projekt

* Bootstrapping ist ein adaptives Zweikopien-Protokoll mit Nachselektion: Schritt (4) ist genau der "Probe"-Mechanismus von Phase 2, nur dass die Sonde ein Projektor auf den unbekannten Zustand ist und nicht ein separat präparierter Zustand. Die Fidelity-Verstärkung um $c > 1$ pro Runde ist ein Argument, das sich auf $\rho\otimes\rho^*$ übertragen lassen sollte.
* Die Liste-Dekodierung ist die Top-$k$-Lokalisierung in Klassensprache: nicht ein Element, sondern alle Elemente über einer Schwelle, und die Schranke an ihre Zahl ersetzt die Sparsity-Annahme.
* Die untere Schranke $\Omega(n/\tau)$ zeigt, dass unterhalb $\tau = 1/\mathrm{poly}(n)$ selbst die Kopienzahl bricht; für die Instanzenleiter markiert das die Stufe, ab der Regime 3 auch informationstheoretisch teuer wird.

### Grenzen und offene Fragen

* Ob $(1/\tau)^{O(\log 1/\tau)}$ nötig ist, bleibt offen; für $\tau = 1/\mathrm{poly}(n)$ gibt es keinen polynomiellen Algorithmus und keine Härtereduktion.
* Der Lerner für Stabilizerdimension ist improper: Er gibt nicht notwendig einen $t$-dotierten Zustand aus.
* Bell-Difference-Sampling braucht Zweikopien-Messungen; ob Computational-Difference-Sampling (Einzelkopien) agnostisch funktioniert, ist offen.
* Zustände beschränkten Stabilizer-Rangs sind auch realisierbar ungelöst.

### Fragen zum Tieferbohren

* Wie genau wird in Schritt (3) die Unvollständigkeit der Projektorfamilie in eine nichtvernachlässigbare Wahrscheinlichkeit übersetzt, einen Stabilisator von $\vert\phi\rangle$ zu ziehen?
* Welche Rolle spielt die Gowers-Norm oder die Uniformität von $p_\psi$ in der Analyse, und ist das die Brücke zu Arunachalam–Dutt?
* Ist die Nachselektion auf $\rho\otimes\rho^*$ mit Displacement-Projektoren $\tfrac12(I + D)$ formulierbar, wenn $D$ nicht hermitesch ist?

Paper: [arXiv:2408.06967](https://arxiv.org/abs/2408.06967)

---

## Phase transition in stabilizer entropy and efficient purity estimation (arXiv:2302.07895)

Die Arbeit von **Lorenzo Leone, Salvatore F. E. Oliviero, Gianluca Esposito und Alioscia Hamma** (UMass Boston, Napoli; Phys. Rev. A 2024) zeigt, dass die Stabilizer-Entropie eines $t$-dotierten Clifford-Zustands durch eine Clifford-Abbildung in einem Teilsystem lokalisiert und dort gelöscht werden kann, solange die Dichte $t = t/n$ der nicht-Clifford-Gatter unter der Dichte $f = n_F/n$ der Hilfsqubits liegt; bei $t/f = 1$ liegt ein Phasenübergang mit kritischem Index eins. In der lokalisierten Phase erlaubt die "Reinigung" die Schätzung exponentiell kleiner Subsystem-Puritäten mit polynomiellen Ressourcen.

### Einordnung in die Tabellen

* **Task type:** Estimating einer einzelnen Größe ($\mathrm{Pur}(\psi_E)$), aber über einen Identifying-Schritt: Zuerst wird die Clifford-Struktur des Schaltkreises gelernt (der Diagonalisierer $D$ mit $C_t = D^\dagger c_tDV$), dann rechnet der Stabilizerformalismus. Die Zeile steht bei Identifying, weil der Aufwand in der Klassenidentifikation sitzt.
* **Objekt:** Zustand $\psi_t = C_t\vert 0\rangle\langle 0\vert C_t^\dagger$ aus einem $t$-dotierten Clifford-Schaltkreis. **Zugriff:** Query an $C_t$ für die Clifford Completion (Leone, Oliviero, Hamma 2022), $\mathrm{poly}(n)\,e^{O(t)}$ Aufrufe; danach $O(n^3)$ Stabilizer-Messungen.
* **Status:** 🟢 🟢 🟢 für $t = O(\log^2 n)$ in der lokalisierten Phase; die Purität wird bis auf einen Faktor $d_Y^2 = 4^t$ bestimmt, also $\mathrm{Pur}(\psi_E) = 2^{-\alpha n + O(\log^2 n)}$.
* **Versprechen:** $t$-dotiert mit $t/f\leq 1$; Bipartition nicht exakt halb ($f < 1/2$).

### Das Problem

Der SWAP-Test schätzt eine Purität bis auf $\epsilon$ mit $O(\epsilon^{-2})$ Kopien; bei Volumengesetz-Zuständen ist $\mathrm{Pur}(\psi_E) = \Theta(e^{-\beta n})$, und der Test braucht exponentiell viele Kopien. Zugleich verteilt ein Clifford-Schaltkreis die Stabilizer-Entropie (Nichtstabilizerheit) typischerweise vollständig in das größere Teilsystem $E$ (Proposition 1: $\mathbb{E}_C[M_{\mathrm{lin}}(\psi_E^C)] = M_{\mathrm{lin}}(\psi) + O(d_F/d_E)$, $\mathbb{E}_C[M_{\mathrm{lin}}(\psi_F^C)] = O(d_F/d_E)$). Kann man $E$ von dieser Komplexität reinigen?

### Kernresultate

* **Proposition 2 (Reinigung).** Für $n_Y\leq n_F$ gibt es eine Clifford-Abbildung $\mathcal{E}(\cdot) = \mathrm{Tr}_Y W(\cdot)W^\dagger$ mit $W = T_{\pi_Y}D$, die die $t$ nicht-Clifford-Gatter in ein Teilsystem $Y\subset F$ mit $n_Y = t$ verschiebt und durch Ausspuren löscht: $M_E[\mathcal{E}(\psi_t)] = 0$.
* **Phasenübergang (Abschnitt III).** Gemittelt über Abbildungen und Stabilizer-Inputs gilt $\mathbb{E}[M_E(\mathcal{E}\circ\mathcal{C}_t[\omega])] = 0$ für $t/f\leq 1$ und $\geq g(n, t, f)$ für $t/f\geq 1$, mit $g_\infty\simeq n(1-2f)$ und $g/g_\infty\simeq\tfrac{f}{1-f}(t/f-1)$ nahe der Kritikalität.
* **Propositionen 3 und 4 (Puritätsschranken).** Der re-verschränkte Stabilizerzustand $\rho = W^\dagger(\mathcal{E}(\psi_t)\otimes d_Y^{-1}I_Y)W$ erfüllt $\mathrm{Pur}(\rho_X)\leq\mathrm{Pur}(\psi_E)\leq d_Y^2\mathrm{Pur}(\rho_X)$.
* **Protokoll.** $t = O(\log^2 n)$: Diagonalisierer lernen ($\mathrm{poly}(n)$), $\rho$ präparieren, Stabilizergruppe von $\rho$ mit $O(n^3)$ Messungen lernen, Purität exakt aus der Gruppe berechnen; dann entweder SWAP-Test mit bekannter Schusszahl (Fall $\mathrm{Pur} = \Omega(1/\mathrm{poly})$) oder direkte Schranke $2^{-\alpha n + O(\log^2 n)}$ (exponentiell kleiner Fall).

### Methodischer Ansatz

* Lemma 1 (Clifford-Mittelung): Über die Clifford-Bahn ist der Mittelwert des Verhältnisses $\mathrm{SP}/\mathrm{Pur}$ gleich dem Verhältnis der Mittelwerte bis auf relativen Fehler $O(2^{-n(1-2f)/2})$; deshalb sind die Aussagen für typische Schaltkreise scharf.
* Die Reinigung benutzt Permutationen $T_\pi$ (selbst Clifford), um das $t$-Qubit-Stück $c_t$ in ein beliebiges Teilsystem $Y$ zu verschieben.
* Die Analogie: Spreizen (Clifford-Tiefe) gegen Lokalisieren (Dichte $f$), wie ein Isolator–Supraflüssigkeits-Übergang.

### Bedeutung und Anwendungen

* Eine exponentiell kleine Purität mit polynomiellem Aufwand zu bestimmen, ist ein exponentieller Vorsprung gegenüber SWAP-Test und Klassischen Schatten für diese Klasse.
* Die Stabilizer-Entropie wird als bewegliche Ressource verstanden; das ist die operationelle Seite der Magic-Kompression, die Grewal et al. und Hangleiter–Gullans zum Lernen benutzen.

### Bezug zum eigenen Projekt

* Der Weg "erst die Clifford-Hülle identifizieren, dann im Stabilizerformalismus rechnen" ist die Identifying-Variante des Zwei-Phasen-Schemas: Phase 1 findet die Struktur, Phase 2 misst innerhalb der Struktur exakt. Der Faktor $d_Y^2 = 4^t$ ist der Preis, den die unbekannte Magic kostet; er entspricht dem $2^t$-Faktor in der Estimating-Tabelle.
* Purity ist $\sum_D\vert\mathrm{Tr}(\rho D)\vert^2/d$, also die $\ell_2$-Masse des Displacement-Spektrums; Bell-Sampling auf $\rho\otimes\rho^*$ zieht direkt aus dieser Verteilung, und die Frage nach exponentiell kleiner Purität ist die Frage nach einem sehr flachen Spektrum ohne schwere Adressen. Das Paper sagt, für dotierte Clifford-Zustände lässt sich die Flachheit exakt berechnen statt sampeln.
* Die Bipartitionsbedingung $f < 1/2$ und die Phasengrenze $t/f = 1$ sind eine Instanzenleiter für Verschränkungsgrößen.

### Grenzen und offene Fragen

* Braucht Query-Zugriff auf den Schaltkreis $C_t$, nicht nur Kopien des Zustands; die Clifford Completion kostet $e^{O(t)}$.
* Nur bis $t = O(\log^2 n)$ und in der lokalisierten Phase; für $t/f > 1$ bleibt die Entropie in $E$.
* Die Puritätsschranke hat eine Unschärfe $4^t$; im polynomiellen Fall wird der SWAP-Test trotzdem gebraucht.
* Übertragung auf Hamiltonsche Dynamik, Fehlerkorrektur und holographische Entropie sind als offene Fragen genannt.

### Fragen zum Tieferbohren

* Wie funktioniert die Clifford Completion konkret, und ist sie ein Bell-Sampling-Algorithmus auf dem Choi-Zustand von $C_t$?
* Warum ist der kritische Index eins, und ist $g(n, t, f)$ eine Aussage über Erwartungswerte oder mit Konzentration?
* Lässt sich die Reinigung mit Bell-Sampling auf $\rho\otimes\rho^*$ verifizieren, indem man prüft, ob das Spektrum des gereinigten Zustands auf einer Untergruppe konzentriert ist?

Paper: [arXiv:2302.07895](https://arxiv.org/abs/2302.07895)

---

## Efficient tomography of non-interacting fermion states (arXiv:2102.10458)

Die Arbeit von **Scott Aaronson und Sabee Grewal** (UT Austin; TQC 2023) gibt einen Tomographie-Algorithmus für Zustände von $n$ nicht wechselwirkenden Fermionen auf $m$ Moden: $O(m^3n^2\log(1/\delta)/\epsilon^4)$ Kopien, $O(m^4n^2\log(1/\delta)/\epsilon^4)$ klassische Zeit, $O(m)$ Messbasen, und die Ausgabe ist ein freier Fermionzustand mit Totalvariationsabstand $\leq\epsilon$ in der Besetzungsbasis. Der Algorithmus schätzt die Kernmatrix $K = AA^\dagger$ (Ein-Teilchen-Dichtematrix) aus Beamsplitter-Messungen und rundet sie auf eine Projektion.

### Einordnung in die Tabellen

* **Task type:** Identifying gegen eine Klasse mit Versprechen. Die Klasse der Slater-Determinanten ist durch $O(mn)$ reelle Parameter beschrieben; zurück kommt eine spaltenorthonormale Matrix $\hat A$.
* **Objekt:** reiner Zustand $\vert\Psi\rangle = \sum_S\det(A_S)\vert S\rangle$ über $\Lambda_{m,n}$. **Zugriff:** Sample; Messungen in der Besetzungsbasis nach Beamsplittern auf Modenpaaren $(i, j)$, also $O(m)$ Einstellungen mit je $O(\log(1/\delta)/\gamma^2)$ Schüssen.
* **Status:** 🟢 🟢 🟢. Kopien $O(m^3n^2/\epsilon^4)$, Zeit $O(m^4n^2/\epsilon^4)$, Speicher $O(m^2)$ für $K$.
* **Versprechen:** Teilchenzahlerhaltung und Gaußianität ($t = 0$); Mele–Herasymenko heben beides auf.

### Das Problem

Freie Fermionen sind klassisch simulierbar und durch die Kernmatrix vollständig bestimmt: Die Wahrscheinlichkeit einer Konfiguration $S$ ist der Hauptminor $\det(K_S)$, ein determinantaler Punktprozess. Kann man den Zustand aus polynomiell vielen Kopien und einfachen Messungen lernen, mit Garantie im Abstand?

### Kernresultate

* **Theorem 1.1 (Hauptresultat).** Kopien $O(m^3n^2\log(1/\delta)/\epsilon^4)$, Zeit $O(m^4n^2\log(1/\delta)/\epsilon^4)$, $O(m)$ Messbasen; Ausgabe $\vert\hat\Psi\rangle$ mit Totalvariationsabstand $\leq\epsilon$ mit Wahrscheinlichkeit $\geq 1-\delta$.
* **Theorem 1.2 / 4.3 (Störungsschranke).** Sind die Kernmatrizen zweier Zustände nahe, so sind die Zustände nahe; der Beweis geht über Weyls Ungleichung (Theorem 4.4) für die Eigenwerte von $\hat K$.
* **Abschnitt 5.** Anpassung auf Spurabstand statt Totalvariation, also konventionelle Tomographie.

### Methodischer Ansatz

* Diagonale $k_{ii}$ (Besetzungswahrscheinlichkeiten) aus der Standardbasis; $\mathrm{Re}\,k_{ij}$ und $\mathrm{Im}\,k_{ij}$ aus zwei Beamsplittern $\tfrac{1}{\sqrt2}\binom{1\ \ 1}{1\ -1}$ und $\tfrac{1}{\sqrt2}\binom{1\ \ i}{1\ -i}$ auf $(i, j)$, die $k_{ii}$ auf $\tfrac12(k_{ii} + k_{jj} + 2\mathrm{Re}\,k_{ij})$ abbilden. Alle Paare gleichzeitig in $O(m)$ Runden ("Round-Robin").
* Eigenzerlegung $\hat K = Q\Lambda Q^\dagger$, die $n$ größten Eigenvektoren bilden $\hat A$; Weyl kontrolliert, wie Fehler in $\hat K$ in $\hat A$ eingehen.
* Die Verbindung zu determinantalen Punktprozessen liefert die Interpretation der Messstatistik.

### Bedeutung und Anwendungen

* Freie Fermionen sind die Gauß-Klasse der Fermionen; das Paper ist der Referenzpunkt für Mele–Herasymenko ($t$ nicht-gaußsche Gatter, keine Teilchenzahlerhaltung) und für Matchgate-Schatten (Wan et al.).
* Chemie- und Festkörperkontext: Hartree–Fock-Zustände sind genau diese Klasse.

### Bezug zum eigenen Projekt

* Der Algorithmus ist ein Estimating-Protokoll ($O(m^2)$ Observablen der Ein-Teilchen-Dichtematrix), gefolgt von einer Rundung auf die Klasse; das ist das "Identifying über Estimating"-Muster, das in Phase 1 mit dem Displacement-Spektrum und in Phase 2 mit der Rundung auf $k$-sparsam entsteht.
* Die $O(m)$ Messbasen entsprechen einer Zerlegung der Observablen in kommutierende Familien; der Round-Robin über Modenpaare ist die fermionische Version der Kommutierungsklassen von Pauli-Strings.
* Die $\epsilon^{-4}$-Rate kommt aus der Rundung (Weyl); wo Bell-Sampling die Beträge direkt liefert, ist das der Vergleichswert für die Kosten einer nachgeschalteten Klassenprojektion.

### Grenzen und offene Fragen

* $\epsilon^{-4}$ statt $\epsilon^{-2}$; Mele et al. erreichen für Gauß-Zustände mit Kovarianzschätzung dieselbe Ordnung, und die optimale Rate ist offen.
* Nur reine, teilchenzahlerhaltende Zustände; gemischte Gauß-Zustände und Nicht-Gaußianität brauchen die Folgearbeiten.
* Keine untere Schranke im Paper.

### Fragen zum Tieferbohren

* Ist die Störungsanalyse über Weyl scharf, oder gibt die Wedin-Schranke für Eigenräume eine bessere $\epsilon$-Abhängigkeit?
* Was ist das Displacement-Analogon der Kernmatrix, also welche $O(m^2)$ Erwartungswerte bestimmen einen Gauß-Zustand im Qudit-Phasenraum?
* Wie verhält sich die Beamsplitter-Strategie zu Matchgate-Schatten, die dieselben Größen mit Zufallsbasen schätzen?

Paper: [arXiv:2102.10458](https://arxiv.org/abs/2102.10458)

---

## Efficient learning of quantum states prepared with few fermionic non-Gaussian gates (arXiv:2402.18665)

Die Arbeit von **Antonio Anna Mele und Yaroslav Herasymenko** (FU Berlin; QuSoft/CWI, QuTech; PRX Quantum 2025) überträgt die Magic-Kompression von Clifford+T auf Fermionen: Jeder Zustand aus beliebig vielen Gauß-Gattern und höchstens $t$ lokalen nicht-gaußschen Gattern lässt sich durch eine Gauß-Unitary auf die Form $G(\vert\phi\rangle\otimes\vert 0^{n-\kappa t}\rangle)$ bringen. Daraus folgt ein Lernalgorithmus mit Einzelkopien-Messungen und Kosten $\mathrm{poly}(n, 2^t)$, eine Härteschranke $\exp(\Omega(t))$ unter RingLWE ab $t = \tilde\omega(\log n)$, ein Test auf Gauß-Dimension und eine verbesserte Schaltkreiskomplexität $O(n^2 + t^3)$.

### Einordnung in die Tabellen

* **Task type:** Identifying gegen eine Klasse mit Versprechen ($t$-komprimierbar, äquivalent: Gauß-Nullity $\leq t$); dazu ein Ein-Bit-Test (nah oder fern von der Klasse) und eine Härteaussage, die die Klasse bei $t = \tilde\omega(\log n)$ in die 🔴-Zeilen schiebt.
* **Objekt:** reiner Zustand auf $n$ Fermionmoden oder, per Jordan–Wigner, $n$ Qubits aus Matchgates mit $t$ SWAP-Gattern. **Zugriff:** Sample, ausschließlich Einzelkopien-Messungen; Pauli-Basis, Gauß-Clifford-Messungen oder fermionische Schatten für die Korrelationsmatrix.
* **Status:** 🟢 🟢 🟢 bis $t = O(\log n)$: $O(n^5)$ für die Korrelationsmatrix plus $\exp(t)$ für die $t$-Qubit-Tomographie. Zeit exponentiell in $t$ notwendig (Theorem 5).
* **Versprechen:** $(t, \kappa)$-dotiert oder allgemeiner $\kappa t$-komprimierbar; auch approximativ komprimierbare und gemischte Zustände.

### Das Problem

Freie Fermionen sind lernbar (Aaronson–Grewal), $t$-dotierte Stabilizerzustände auch; Gauß-Schaltkreise mit wenigen magischen Gattern sind seit kurzem klassisch simulierbar. Sind sie lernbar, und wo liegt die Grenze in $t$?

### Kernresultate

* **Theorem 3 (Kompression).** Jeder $(t, \kappa)$-dotierte Gauß-Zustand ist $\kappa t$-komprimierbar: $\vert\psi\rangle = G(\vert\phi\rangle\otimes\vert 0^{n-\kappa t}\rangle)$. Für Unitaries $U_t = G_A(u_t\otimes I)G_B$ mit $u_t$ auf $\lceil\kappa t/2\rceil$ Qubits; teilchenzahlerhaltend bleibt erhalten. Konstruktiver Beweis über die Existenz einer symplektisch-orthogonalen $O_{\mathrm{aux}}$.
* **Theorem 4 (Lernen).** Algorithmus 1 lernt jeden $t$-komprimierbaren Zustand mit $O(\mathrm{poly}(n, 2^t))$ Einzelkopien-Messungen und Zeit bis auf Spurabstand $\epsilon$: Korrelationsmatrix mit $\lceil 256n^5\epsilon^{-4}\log(12n^2/\delta)\rceil$ Messungen, Normalform $\hat C = \hat O\hat\Lambda\hat O^T$, $\hat G^\dagger$ anwenden, letzte $n-t$ Qubits messen, auf $0^{n-t}$ nachselektieren, $t$-Qubit-Tomographie.
* **Theorem 5 (Härte).** Kann ein Quantencomputer RingLWE nicht in subexponentieller Zeit lösen, dann gibt es keinen zeiteffizienten Lerner für $\tilde\omega(\log n)$-dotierte Gauß-Zustände; Beweis durch Einbettung pseudozufälliger Zustände über eine Qubit-zu-Fermion-Abbildung mit konstantem Overhead.
* **Gl. (5) (Test).** $\tfrac12(1-\lambda_{t+1})\leq\min_{\phi\in\mathcal{G}_t}d_{\mathrm{tr}}(\psi, \phi)\leq\sqrt{\sum_{k>t}(1-\lambda_k)/2}$ mit den Normal-Eigenwerten $\lambda_k$ der Korrelationsmatrix; der Abstand zur Klasse ist aus der Korrelationsmatrix effizient schätzbar.
* **Proposition 30.** Schaltkreiskomplexität $O(n^2 + t^3)$ statt $O(n^2t)$; Grundzustände von Störstellenmodellen sind approximativ $O(\log n)$-komprimierbar.

### Methodischer Ansatz

* Gauß-Dimension = Zahl der Normal-Eigenwerte gleich eins; Gauß-Nullity $\leq t$ genau dann, wenn $t$-komprimierbar. Die Korrelationsmatrix $C(\rho)_{jk} = -\tfrac{i}{2}\mathrm{Tr}(\gamma_j\gamma_k\rho)$ ist die einzige globale Größe, die geschätzt werden muss; alles Weitere ist lokal.
* Quantum Union Bound und Chernoff für die Nachselektion; die $t$-Abhängigkeit ist optimal, weil ein beliebiger $t$-Qubit-Zustand enthalten ist.
* Für die Härte werden PRS-Konstruktionen mit lokalen nicht-gaußschen Gattern realisiert, mit $O(1)$ Overhead pro Qubit.

### Bedeutung und Anwendungen

* Dasselbe Kompressionstheorem gilt für Stabilizer, Fermionen und (Mele et al. 2024) Bosonen; die drei Theorien haben eine gemeinsame Struktur, obwohl ihre Mathematik verschieden aussieht.
* Physikalische Zielzustände: Störstellenmodelle, Zeitentwicklung unter Störstellen-Hamiltonians bis konstante Zeiten; experimentell nur einfache Fermion-Hamiltonians nötig, also für Analogsimulatoren geeignet.
* Klassische Schatten lernen $t$-dotierte Zustände mit $\mathrm{poly}(n, t)$ Kopien, aber exponentieller Zeit in $n$; hier polynomiell in $n$, exponentiell in $t$: Die Sample–Zeit-Schere ist explizit.

### Bezug zum eigenen Projekt

* Die Logik "eine globale, aber quadratisch große Größe schätzen, dann ein kleines Restproblem lösen" ist die Struktur von Phase 1 (Displacement-Beträge) und Phase 2 (Vorzeichen auf dem Träger). Die Korrelationsmatrix ist der Gauß-Fall des Displacement-Spektrums: Für Gauß-Zustände ist $\vert\mathrm{Tr}(\rho D)\vert^2$ eine Gauß-Funktion der Adresse, vollständig durch die Kovarianz bestimmt.
* Der Test auf Gauß-Dimension über die Eigenwerte $\lambda_k$ ist ein Beispiel für einen Klassentest, der aus derselben Messung wie das Lernen folgt; das ist die Rolle, die der Purity-Check aus Bell-Sampling in der eigenen Pipeline hat.
* Die Härte bei $t = \tilde\omega(\log n)$ ist die fermionische Version der LWE-Wand; sie bestätigt, dass die Instanzenleiter in $t$ ab logarithmischer Höhe abbricht.

### Grenzen und offene Fragen

* $O(n^5)$ für die Korrelationsmatrix ist vermutlich verbesserbar; $\epsilon^{-4}$ wie bei Aaronson–Grewal.
* Reine, exakt komprimierbare Zustände im Hauptteil; gemischte und approximative Fälle in der Ergänzung.
* Die Lücke zwischen $O(\log n)$ (effizient) und $\tilde\omega(\log n)$ (hart) ist bis auf polyloglog-Faktoren geschlossen.

### Fragen zum Tieferbohren

* Wie sieht die symplektisch-orthogonale $O_{\mathrm{aux}}$ konkret aus, und ist die Konstruktion numerisch stabil?
* Was ist der Displacement-Übersetzer des Kompressionstheorems für Qudits: Gibt es eine "Clifford-Kompression" von $t$ nicht-Clifford-Gattern auf $O(t)$ Qudits mit derselben Beweisidee?
* Wie schnell verlässt die Zeitentwicklung unter einem Störstellenmodell die approximative Komprimierbarkeit, und ist das eine Aussage über das Wachstum des Displacement-Trägers?

Paper: [arXiv:2402.18665](https://arxiv.org/abs/2402.18665)

---

## Learning quantum states of continuous-variable systems (arXiv:2405.01431)

Die Arbeit von **Francesco A. Mele, Antonio A. Mele, Lennart Bittel, Jens Eisert, Vittorio Giovannetti, Ludovico Lami, Lorenzo Leone und Salvatore F. E. Oliviero** (SNS Pisa, FU Berlin, Amsterdam; 2024) ist die erste systematische Untersuchung der Tomographie kontinuierlicher Variablen mit Spurabstandsgarantie. Drei Resultate: Energiebeschränkte Zustände auf $n$ Moden brauchen mindestens $\epsilon^{-2n}$ Kopien ("extreme Ineffizienz"); Gauß-Zustände sind mit $O(n^7E^4/\epsilon^4)$ Kopien lernbar; $t$-dotierte Gauß-Zustände mit $\mathrm{poly}(n) + O((nE/\epsilon)^{2\kappa t})$, effizient für $\kappa t = O(1)$.

### Einordnung in die Tabellen

* **Task type:** Identifying gegen die Klasse der Gauß- und $t$-dotierten Gauß-Zustände; für allgemeine energiebeschränkte Zustände ist es volle Tomographie mit einer unteren Schranke, also die 🔴-Referenz der CV-Welt.
* **Objekt:** Zustand auf $n$ bosonischen Moden mit $\mathrm{Tr}[\hat E_n\rho]\leq nE$. **Zugriff:** Sample; Homodyn- und Heterodyndetektion für erste Momente und Kovarianzmatrix; CV-Schatten oder optimale Tomographie für den komprimierten Kern.
* **Status:** Gauß 🟢 🟢 🟢 mit $O(n^7E^4/\epsilon^4)$ Kopien, $\mathrm{poly}(n)$ Zeit, $O(n^2)$ Parameter; $t$-dotiert 🟢 🟢 🟢 nur für $\kappa t = O(1)$; allgemein 🔴 mit $\Omega(\epsilon^{-2n})$ Kopien, schon für $n = 10$ Moden und $\epsilon = 0.1$ etwa 3000 Jahre bei einer Kopie pro Nanosekunde.
* **Versprechen:** Energieschranke $E$ (allgemein), zweites Moment (für die Kovarianzschätzung), Gaußianität oder $t$-Dotierung.

### Das Problem

Ohne Energieschranke ist CV-Tomographie sinnlos (unendlich viele Parameter); mit Energieschranke wird sie zu einer endlichen, aber wie teuren Aufgabe? Und für welche physikalischen Klassen wird sie effizient?

### Kernresultate

* **Theorem 1 und 2 (energiebeschränkt).** Reine Zustände: Sample-Komplexität skaliert wie $\epsilon^{-2n}$ mit $E^n$-Faktoren; gemischte: $O(E^{2n}/\epsilon^{3n})$ hinreichend, $\Omega(E^{2n}/\epsilon^{2n})$ notwendig. Mechanismus: Jeder energiebeschränkte Zustand ist bis auf $\epsilon$ ein Zustand der Dimension $D = O(E^n/\epsilon^{2n})$ und des Rangs $r = O(E^n/\epsilon^n)$ (Gl. 3), und endlichdimensionale Tomographie kostet $O(Dr)$. Für $k$-te Momente wird der Exponent $2n/k$.
* **Theorem 3 (Fehlerfortpflanzung).** Kennt man erstes Moment und Kovarianzmatrix bis auf $\epsilon$, ist der Spurabstand höchstens $O(\sqrt\epsilon)$ und mindestens $O(\epsilon)$; die Schranken (Theoreme 10, 11) sind eigenständige Werkzeuge.
* **Theorem 4 (Gauß).** $O(n^7E^4/\epsilon^4)$ Kopien, Ausgabe erstes Moment und Kovarianz; robust gegen kleine nicht-gaußsche Störungen (kleine relative Entropie der Nicht-Gaußianität).
* **Theorem 5 (Kompression).** $U = G(u_{\kappa t}\otimes I)G_{\mathrm{passive}}$, also $\vert\psi\rangle = G(\vert\phi_{\kappa t}\rangle\otimes\vert 0\rangle^{\otimes(n-\kappa t)})$: das bosonische Gegenstück zu Stabilizer- und Fermion-Kompression.
* **Theorem 6 ($t$-dotiert).** $\mathrm{poly}(n) + O((nE/\epsilon)^{2\kappa t})$ Kopien, gleiche Ordnung in Zeit und Speicher; effizient genau dann, wenn $\kappa t = O(1)$, anders als bei Stabilizern und Fermionen ($t = O(\log n)$), weil der Kern unendlichdimensional ist.

### Methodischer Ansatz

* Momente per Homodyn schätzen, Gauß-Unitary konstruieren, invers anwenden, die Nicht-Gaußianität auf $\kappa t$ Moden komprimieren, dort tomographieren; alle Operationen sind Standard im Quantenoptiklabor.
* Die untere Schranke kommt über die Reduktion auf endlichdimensionale Tomographie von Zuständen mit Dimension $D$ und Rang $r$; die Energiebeschränkung übersetzt sich in eine effektive Dimension.

### Bedeutung und Anwendungen

* Brücke zwischen Quantenlerntheorie und CV-Information; die Gauß-Klasse ist die Standardressource für Sensorik, Kommunikation und Rechnen mit Licht.
* Die "extreme Ineffizienz" ist ein neues Phänomen: Die Kosten hängen exponentiell in $n$ von $1/\epsilon$ ab, nicht nur von der Dimension.

### Bezug zum eigenen Projekt

* Displacement-Operatoren auf Qudits sind die diskrete Version der Weyl-Operatoren im CV-Phasenraum; ein Gauß-Zustand hat dort ein gaußsches Displacement-Spektrum, das durch die Kovarianz allein bestimmt ist. Das Paper zeigt, was "Gaußsches Versprechen" auf der Instanzenleiter kostet: $O(n^2)$ Parameter, polynomielle Kopien, kein Träger zu suchen.
* $\kappa t = O(1)$ als Effizienzgrenze ist strenger als $t = O(\log n)$; das ist ein Hinweis, dass die Höhe der Leiter vom Alphabet abhängt ($d\to\infty$ verkürzt sie).
* Die Fehlerfortpflanzung $O(\sqrt\epsilon)$ von Momenten zum Spurabstand ist derselbe Wurzelverlust wie bei der Rundung einer geschätzten Kernmatrix; Phase 2 sollte ihn einkalkulieren.

### Grenzen und offene Fragen

* $n^7E^4/\epsilon^4$ ist nicht als optimal nachgewiesen; die obere Schranke für gemischte energiebeschränkte Zustände ($\epsilon^{-3n}$) passt nicht zur unteren ($\epsilon^{-2n}$).
* Die Lernbarkeit für $\kappa t = \omega(1)$ ist nicht ausgeschlossen, nur der Algorithmus ist ineffizient.
* Keine Härteschranke wie bei Mele–Herasymenko.

### Fragen zum Tieferbohren

* Wie geht die Energieschranke in die Konstruktion der Kovarianzschätzung ein, und warum reicht sie nicht ohne das zweite Moment?
* Wie sehen die Schranken der Theoreme 10 und 11 (Spurabstand zweier Gauß-Zustände gegen Norm der Momentdifferenz) explizit aus?
* Gibt es eine Qudit-Version der "extremen Ineffizienz", wenn $d$ mit $1/\epsilon$ wächst?

Paper: [arXiv:2405.01431](https://arxiv.org/abs/2405.01431)

---

## Efficient quantum state tomography (arXiv:1101.4366)

Die Arbeit von **Marcus Cramer, Martin B. Plenio, Steven T. Flammia, Rolando Somma, David Gross, Stephen D. Bartlett, Olivier Landon-Cardinal, David Poulin und Yi-Kai Liu** (Ulm, Perimeter, Hannover, Sydney, Sherbrooke, Caltech; Nat. Commun. 2010) ist die Gründungsarbeit der Matrixprodukt-Tomographie. Zwei Schemata rekonstruieren einen Zustand auf einer Kette von $N$ Qudits, der gut durch einen MPS beschrieben ist, aus linear vielen lokalen Messeinstellungen mit polynomieller Nachverarbeitung; die Genauigkeit lässt sich ohne Annahmen über den Laborzustand zertifizieren.

### Einordnung in die Tabellen

* **Task type:** Identifying gegen eine Klasse (MPS mit Bonddimension $D$, Rang $R$ der Reduktionen) mit dem Versprechen, dass der Laborzustand nahe daran ist; das Zertifikat macht das Versprechen überprüfbar und damit zur $M = 1$-Aufgabe (Certification).
* **Objekt:** Zustand auf einer Kette; reine MPS im Hauptteil, Verallgemeinerungen angedeutet. **Zugriff:** Sample; Schema 1 braucht Unitaries auf $\kappa = \lceil\log_dR\rceil + 1$ benachbarten Qudits plus lokale Messungen, Schema 2 nur lokale Messungen auf $k$ Nachbarn.
* **Status:** 🟢 🟢 🟢. Linear viele Messeinstellungen in $N$, Nachverarbeitung $\mathrm{poly}(N)$, Speicher $O(ND^2)$; Schema 2 zusätzlich ein Fidelity-Zertifikat aus denselben Daten.
* **Versprechen:** kleine Bonddimension; für Schema 2 die Existenz eines lokalen, gapped Parent-Hamiltonians, der für generische MPS gegeben ist.

### Das Problem

Volle Tomographie skaliert exponentiell in $N$; MPS haben polynomiell viele Parameter. Kann man diese Parameter aus lokalen Daten bestimmen und die Rekonstruktion verifizieren, ohne den Laborzustand als MPS vorauszusetzen?

### Kernresultate

* **Schema 1 (Unitaries).** Tomographie der ersten $\kappa$ Plätze, Unitary $\hat U_1$, die das erste Qudit entkoppelt, Wiederholung entlang der Kette; die Folge $\hat U_1, \ldots, \hat U_{N-\kappa+1}$ ist der Präparationsschaltkreis, aus dem der MPS folgt. Fehler durch Trunkierung auf Rang $R$ und Messungenauigkeit $\epsilon$ akkumulieren höchstens linear, Gesamtfehler $N\epsilon$, direkt aus den Daten ablesbar.
* **Schema 2 (lokale Messungen).** Aus Schätzungen $\hat\sigma_i$ der Reduktionen auf $k$ Nachbarn wird per Singular Value Thresholding ein MPS $\vert\psi\rangle$ gesucht, dessen Reduktionen zu $\hat\sigma_i$ passen.
* **Gl. (3)–(4) (Zertifikat).** Ist $\vert\psi\rangle$ eindeutiger Grundzustand (Energie null) eines lokalen $\hat H = \sum_i\hat h_i$ mit Gap $\Delta E$, dann $\langle\psi\vert\hat\varrho\vert\psi\rangle\geq 1 - \tfrac{1}{\Delta E}\sum_i(\mathrm{Tr}[\hat h_i\hat\sigma_i] + \epsilon_i)$; der Hamiltonian ist ein Zeuge, und für generische MPS existiert er und ist aus dem Schätzer konstruierbar.
* **Beispiel Clusterzustand.** $k = 3$, $R = 4$, $\Delta E = 1$; Schema 1 mit $\kappa = 2$.

### Methodischer Ansatz

* Sequentielle Entkopplung: Die Rangschranke der Reduktionen erzwingt, dass ein Qudit durch eine Unitary auf $\kappa$ Plätzen abgespalten werden kann; das ist die Umkehrung der sequentiellen MPS-Präparation.
* Das Zertifikat nutzt nur lokale Erwartungswerte; die Nichtexistenz eines Zeugen (GHZ verletzt die "generische" Bedingung) wird gesondert behandelt.

### Bedeutung und Anwendungen

* Erste polynomielle Tomographie einer physikalisch relevanten Klasse mit zertifizierter Ausgabe; die Idee, die Rekonstruktion durch einen Parent-Hamiltonian zu verifizieren, kehrt bei Huang–Preskill–Soleimanifar in anderer Form wieder.
* Tensor-Netzwerk-Verallgemeinerungen (Baum, MERA) angedeutet; numerisch bis 20 Ionen demonstriert.

### Bezug zum eigenen Projekt

* Schema 1 lernt den Präparationsschaltkreis durch lokale Inversion, Qudit für Qudit; das ist die Ein-Dimensions-Version des Local-Inversion-Prinzips von Huang et al. und Landau–Liu und der Beweis, dass "eine Unitary, die ein Qudit abspaltet" ein Identifying-Primitiv ist, das ohne globale Suche auskommt.
* Das Zertifikat ist eine Untergrenze der Fidelity aus lokalen Daten; für die eigene Pipeline ist die Frage, ob das Displacement-Spektrum einen ähnlichen Zeugen liefert, etwa über die $\ell_2$-Masse auf dem gefundenen Träger.
* Die Klasse ist per Konstruktion Regime 1 (Versprechen erfüllt) mit einem eingebauten Test auf Regime 3.

### Grenzen und offene Fragen

* Keine explizite Sample-Komplexität in $D$, $\epsilon$; die erste rigorose Schranke für MPDO aus lokalen Messungen liefern Fanizza et al. (2023).
* Schema 2 braucht die Existenz eines gapped Zeugen; für nicht-generische Zustände (GHZ) zusätzliche Behandlung.
* Nur eindimensional; höhere Dimensionen führen auf die Constraint-Satisfaction-Probleme, die Landau–Liu umgehen.

### Fragen zum Tieferbohren

* Wie hängt $\kappa$ von $R$ ab, wenn der Laborzustand nur approximativ Rang $R$ hat, und wie wird die Trunkierung gewählt?
* Wie wird der Parent-Hamiltonian aus dem MPS-Schätzer konstruiert, und wie berechnet man seinen Gap effizient?
* Gibt es ein Zertifikat der Form (4) für Zustände, deren Struktur ein sparsames Displacement-Spektrum statt ein kleiner Bond-Rang ist?

Paper: [arXiv:1101.4366](https://arxiv.org/abs/1101.4366)

---

## Learning finitely correlated states: stability of the spectral reconstruction (arXiv:2312.07516)

Die Arbeit von **Marco Fanizza, Niklas Galke, Josep Lumbreras, Cambyse Rouzé und Andreas Winter** (Barcelona, Paris, Singapur; 2023) gibt die erste rigorose Sample-Komplexität für das Lernen von Matrixprodukt-Dichteoperatoren aus lokalen Messungen. Für translationsinvariante endlich korrelierte Zustände auf der unendlichen Kette wird eine Realisierung minimaler Dimension $m$ per *spektraler Rekonstruktion* aus den Marginalen auf $2s+1$ Plätzen gewonnen; der Fehler der Marginale auf $t$ Plätzen ist polynomiell in $t$, $m$, $1/\eta$ kontrolliert, wobei $\eta$ eine Schranke an den kleinsten Singulärwert der Hankel-artigen Matrix $\Omega$ ist.

### Einordnung in die Tabellen

* **Task type:** Identifying gegen eine Klasse mit Versprechen: $S(m, s, \eta)$, Zustände mit Realisierung der Dimension $\leq m$, $s$-rekonstruierbar, $\sigma_m(\Omega, s)\geq\eta$; Ausgabe sind die Parameter der Realisierung ($\rho$, $e$, $K_{k,l}$), aus denen jede Marginale in linearer Zeit folgt.
* **Objekt:** translationsinvarianter, möglicherweise gemischter Zustand auf der unendlichen Kette; auch nicht-translationsinvariante endliche Ketten (Anhang D) und Zustände mit quantenmechanischer Realisierung $S_q(d_B, s, \eta)$. **Zugriff:** Sample; beliebige Tomographie der Marginale $\omega_s$, $\omega_{2s}$, $\omega_{2s+1}$, lokal oder verschränkt.
* **Status:** 🟢 🟢 🟢. Kopien polynomiell in $t$, $m$, $1/\eta$, $1/\epsilon$ (Theoreme 2.6 bis 2.8), Zeit lineare Algebra auf Matrizen der Größe $d^{2s}$, Speicher $O(m^2d^2)$.
* **Versprechen:** endliche Korrelation mit Dimension $m$; die Parameter $s$ und $\eta$ sind Eingaben des Algorithmus, $m$ muss nicht bekannt sein.

### Das Problem

Für reine MPS gibt es zertifizierbare Tomographie (Cramer et al.), für MPDO Rekonstruktionsverfahren ohne Fehlerschranke. Klassisch liefern spektrale Algorithmen für Hidden-Markov-Modelle Garantien in Totalvariation, quadratisch in der Speichergröße. Gibt es dasselbe für Quantenzustände, deren Realisierung nicht einmal ein Quantenmodell zu sein braucht?

### Kernresultate

* **Definitionen 2.1, 2.2.** Klassen $S(m, s, \eta)$ und $S_q(d_B, s, \eta)\subseteq S(d_B^2, s, \eta)$; jeder Zustand mit Realisierung der Dimension $m$ ist $m$-rekonstruierbar, generisch $O(\mathrm{polylog}\,m)$-rekonstruierbar (Quantum-Wielandt).
* **Algorithmus 1 (LearnFCS).** Schätze $\hat\Omega(1)$, $\hat\tau\Omega$, $\hat\Omega$, $\hat\Omega_{Z_k}$ aus $\hat\omega_s$, $\hat\omega_{2s}$, $\hat\omega_{2s+1}$; SVD $\hat\Omega = \hat U\hat D\hat O^T$, Spalten mit Singulärwert $\geq\eta/2$ behalten; $\hat e = \hat U^T\hat\Omega(1)$, $\hat\rho = \hat\tau\Omega(\hat U^T\hat\Omega)^+$, $\hat K_{Z_i} = \hat U^T\hat\Omega_{Z_i}(\hat U^T\hat\Omega)^+$.
* **Theorem 2.6 (Stabilität).** Sind die Hilbert–Schmidt-Fehler der drei Marginale kleiner als $\epsilon\eta^3/(20tm\sqrt{d_A})$, dann $\tfrac12\Vert\hat\omega_t - \omega_t\Vert_1\leq\epsilon$. **Theorem 2.7:** mit Quantenrealisierung ersetzt $d_B$ das $m$. **Theorem 2.8:** daraus folgt die Sample-Komplexität aus jeder Tomographie-Routine für $d^{2s+1}$-dimensionale Zustände.
* **Anhang C, D.** Fehlerfortpflanzung über vollständig beschränkte Normen und Kontraktivität der erzeugenden Abbildung; Verallgemeinerung auf nicht-translationsinvariante Ketten.

### Methodischer Ansatz

* Die Matrix $\Omega$ ist eine Umordnung der Koeffizienten von $\omega_{[t_1, t_2]}$ in einer Produktbasis; ihr Rang ist $\leq m$ und sättigt für $-t_1\geq m-1$, $t_2\geq m$. Die Realisierung folgt durch Moore–Penrose-Inversion; die Empfindlichkeit steckt im kleinsten Singulärwert, daher $\eta$.
* Die Analyse arbeitet mit Operatorsystemen und CP-Abbildungen und deckt Realisierungen ab, für die kein endlichdimensionales Quantenmodell existiert (GPT-Speicher).

### Bedeutung und Anwendungen

* Erste Sample-Garantie für MPDO-Tomographie aus lokalen Messungen, auch für gemischte Zustände; klassische Nebenwirkung: Fehlerschranken für Hidden-Markov-Modelle jenseits der bisherigen Annahmen.
* Ausgabe ist ein generatives Modell: Erwartungswerte von Produktobservablen auf beliebigen Längen in linearer Zeit.

### Bezug zum eigenen Projekt

* Die spektrale Rekonstruktion ist ein Estimating-Schritt (Marginale) plus lineare Algebra; die Klassenstruktur (Rang $m$) macht aus $d^{2s}$ Zahlen eine Beschreibung mit $O(m^2d^2)$ Parametern. Das ist die Tensor-Netzwerk-Version von "Träger finden, dann Koeffizienten": Die Spalten von $\hat U$ mit Singulärwert $\geq\eta/2$ sind der Träger.
* $\eta$ ist eine Konditionszahl der Instanz und gehört auf die Instanzenleiter; die Faktoren $\eta^{-3}$ und $m$ zeigen, wie ein Versprechen quantitativ in Kopien übersetzt wird.
* Für Displacement-Spektren stellt sich die analoge Frage: Welche Hankel-Struktur haben Bell-Statistiken translationsinvarianter Zustände, und lässt sich ein sparsames Spektrum als niedrigrangige $\Omega$ lesen?

### Grenzen und offene Fragen

* Die Konstanten sind grob (Faktor 20, $\eta^3$); Optimalität ungeklärt.
* Übersetzung von "Rang $m$ und Singulärwert $\eta$" in physikalische Eigenschaften (Korrelationslänge, Gap) nur heuristisch.
* Höhere Dimensionen und PEPS nicht behandelt.

### Fragen zum Tieferbohren

* Wie kommt die Potenz $\eta^3$ zustande, und welcher Schritt der Fehlerfortpflanzung ist verantwortlich?
* Was leistet die Kontraktivität der erzeugenden Abbildung genau, und warum reicht sie auch für GPT-Realisierungen?
* Lässt sich das Verfahren auf Bell-Sampling-Daten anwenden, also auf die Verteilung $\vert\mathrm{Tr}(\rho D_a)\vert^2$ statt auf die Dichtematrix der Marginale?

Paper: [arXiv:2312.07516](https://arxiv.org/abs/2312.07516)

---

## Learning shallow quantum circuits (arXiv:2401.10095)

Die Arbeit von **Hsin-Yuan Huang, Yunchao Liu, Michael Broughton, Isaac Kim, Anurag Anshu, Zeph Landau und Jarrod R. McClean** (Caltech, Google Quantum AI, Berkeley, UC Davis, Harvard; STOC 2024) gibt die ersten polynomiellen Algorithmen für zwei Aufgaben: eine unbekannte Unitary konstanter Tiefe mit beliebiger Konnektivität aus klassischen Zufallsdaten bis auf Diamantabstand $\epsilon$ zu lernen, und einen Zustand $U\vert 0^n\rangle$ eines flachen Schaltkreises auf einem 2D-Gitter aus Kopien bis auf Spurabstand $\epsilon$ zu lernen. Die Technik sind lokale Inversionen, die durch einen Ancilla-SWAP-Trick zu einem globalen Schaltkreis "vernäht" werden, ohne ein Constraint-Satisfaction-Problem zu lösen.

### Einordnung in die Tabellen

* **Task type:** Identifying gegen eine Klasse mit Versprechen (konstante Tiefe). Zurück kommt ein Schaltkreis aus der Klasse, kein Träger und keine Liste von Erwartungswerten; das Versprechen begrenzt jeden Lichtkegel auf konstante Größe, daher nur polynomiell viele lokale Kandidaten, derselbe Mechanismus wie bei Juntas.
* **Objekt:** Unitary $U$ (Theoreme 1 bis 3) oder Zustand $U\vert 0^n\rangle$ (Theorem 4). **Zugriff:** Sample auf Input–Output-Paaren (zufällige Produkt-Inputs, randomisierte Pauli-Messungen, der klassische Schatten von $U$); Query an $U$ für Theorem 3; Kopien für Theorem 4.
* **Status:** 🟢 🟢 🟢. Unitary: $N = O(n^2\log n/\epsilon^2)$ Samples, $\mathrm{poly}(n)/\epsilon^2$ Zeit; endliches Gatterset $O(\log n)$ Samples, Fehler null; mit Quantenqueries $\Theta(1)$ Queries und $\Theta(n)$ Zeit, beides optimal. Zustand auf 2D: $2^{O(d^2)}(n/\epsilon)^{O(1)}$ Kopien, Zeit $(n^{d^3}/\epsilon)^{O(d^3)}$; endliches Gatterset $O(\log n)$ Kopien, $O(n\log n)$ Zeit.
* **Versprechen:** Tiefe $d = O(1)$; bis $d = \mathrm{polylog}(n)$ quasipolynomiell; $\log$-Tiefe ohne Geometrie ist exponentiell hart (Prop. 3, Grover-Orakel).

### Das Problem

Flache Schaltkreise erzeugen Verteilungen, die klassisch schwer zu sampeln sind; die Optimierungslandschaft parametrisierter flacher Schaltkreise hat keine Barren Plateaus, aber exponentiell viele suboptimale lokale Minima, an denen Gradientenverfahren scheitern. Gibt es trotzdem einen Lerner in Polynomialzeit, und aus welchen Daten?

### Kernresultate

* **Theorem 1 (allgemeine flache Schaltkreise).** $U$ mit beliebigen Zwei-Qubit-Gattern zwischen beliebigen Paaren, auch mit $m$ Ancillas, aus $O(n^2\log n/\epsilon^2)$ Samples in $\mathrm{poly}(n)/\epsilon^2$ klassischer Zeit bis auf $\Vert V - U\otimes U^\dagger\Vert_\diamond\leq\epsilon$; $V$ wirkt auf $2n$ Qubits, $U$ folgt durch Ausspuren.
* **Theorem 2 (geometrisch lokal, $k$-dimensionales Gitter).** Gleiche Samplezahl; entweder $O(n^3\log n/\epsilon^2)$ Zeit mit Tiefe $(k+1)4^{4(8kd)^k}+1$ oder $(n/\epsilon)^{O((8kd)^{k+1})}$ Zeit mit Tiefe $(k+1)(2d+1)+1$; endliches Gatterset $O(\log n)$ Samples, $O(n\log n)$ Zeit. Gilt unverändert für Quantenzellularautomaten.
* **Theorem 3 (Quantenqueries).** Endliches Gatterset: Fehler null, Fehlerwahrscheinlichkeit null, $\Theta(1)$ Queries, $\Theta(n)$ Zeit.
* **Theorem 4 (Zustände auf 2D).** Ein Schaltkreis der Tiefe $3d$, der $\vert\psi\rangle$ bis auf $\epsilon$ präpariert.
* **Prop. 3 (Grenze).** Ohne Geometrie brauchen $\log$-tiefe Schaltkreise exponentiell viele Queries im Diamantabstand.
* **Abschnitt 9 (Verifikation).** Ein effizienter Test aus denselben Daten, der den gelernten Schaltkreis im Average-Case-Abstand prüft; nützlich zur Schaltkreiskompression.

### Methodischer Ansatz

* Lokale Inversion: Für jedes Qubit $i$ existiert eine Unitary $V_i$ im Rückwärtslichtkegel mit $UV_i\approx U'\otimes I_i$; sie wird durch Enumeration über den konstant großen Suchraum und einen Test auf approximative lokale Identität gefunden. Die Menge $\mathcal{C}_i$ der gültigen Inversionen ist nicht eindeutig und Nachbarn müssen nicht konsistent sein.
* Vernähen (Gl. 1 bis 4): Beliebiges $V_1\in\mathcal{C}_1$ anwenden, Qubit 1 mit einer frischen Ancilla tauschen, $V_1^\dagger$ anwenden; der Effekt ist ein SWAP nach $U$, und der Schaltkreis vor $U$ ist "repariert", sodass Qubit 2 mit einem beliebigen $V_2\in\mathcal{C}_2$ folgen kann. Nach $n$ Schritten ist ein $2n$-Qubit-Schaltkreis $\hat U$ gelernt.
* Für Zustände dieselbe Idee mit $V_i\vert\psi\rangle\approx\vert\psi'\rangle\otimes\vert 0\rangle_i$; auf 2D wird das Gitter in 1D-Streifen entkoppelt, deren Konsistenzproblem effizient lösbar ist.

### Bedeutung und Anwendungen

* Endliche Korrelationslänge genügt, um globale Struktur aus lokalen Daten zu rekonstruieren, obwohl die Klasse klassisch nicht simulierbar ist; das unterscheidet sie von MPS und Stabilizern.
* Anwendungen: Hardware-Charakterisierung, Schaltkreiskompression mit Verifikation, Lernen von Dynamik; die Datenquelle ist der klassische Schatten des Prozesses.
* Erstes Literaturbeispiel für die Zelle Query × Identifying mit Prozessobjekt; bisher standen dort Bernstein–Vazirani und die eigene Konstruktion.

### Bezug zum eigenen Projekt

* Der Ancilla-SWAP-Trick ist eine Methode, lokale Teilinformationen zu einem globalen Objekt zu komponieren, ohne Konsistenz zu erzwingen; für die Top-$k$-Lokalisierung ist das ein Vorbild dafür, wie lokal gefundene Adressen ohne globales Matching zusammengesetzt werden können.
* Der Test auf approximative lokale Identität ist ein Zertifikat aus lokalen Messungen, verwandt mit dem Parent-Hamiltonian-Zeugen bei Cramer et al.
* Der Wechsel von Sample (Input–Output-Paare) zu Query ($\Theta(1)$ Aufrufe, Fehler null) ist die Zugriffsleiter für Prozesse in einem Paper; er bestätigt, dass Queries den Fehler, nicht die Instanzgröße kaufen.

### Grenzen und offene Fragen

* Zustände nur auf 2D; Landau–Liu heben das auf.
* Der Exponent der Laufzeit ist groß; die gelernte Tiefe kann viel größer sein als die wahre.
* Average-Case-Abstand statt Diamantabstand ist berechnungstheoretisch offen; tiefer als polylog ist nichts bekannt.

### Fragen zum Tieferbohren

* Wie genau funktioniert der Test auf approximative lokale Identität aus randomisierten Pauli-Daten, und wie viele Samples braucht er pro Kandidat?
* Warum scheitert das Vernähen bei $\log$-Tiefe: Wächst der Lichtkegel oder die Zahl der Kandidaten?
* Übertragen sich lokale Inversionen auf Qudit-Schaltkreise mit Displacement-Struktur, und ist die Adresse eines Displacement-Operators ein Lichtkegel-Begriff?

Paper: [arXiv:2401.10095](https://arxiv.org/abs/2401.10095)

---

## Learning quantum states prepared by shallow circuits in polynomial time (arXiv:2410.23618)

Die Arbeit von **Zeph Landau und Yunchao Liu** (UC Berkeley, Harvard; 2024) löst das Problem, das Huang et al. für 2D gelöst und für höhere Dimensionen offen gelassen hatten: Ein Zustand $\vert\psi\rangle = U\vert 0^n\rangle$ mit $U$ der Tiefe $d$ auf einem $k$-dimensionalen Gitter wird in Polynomialzeit gelernt, für jedes feste $k$, ohne ein Konsistenzproblem zu lösen. Die Ausgabe ist ein Schaltkreis der Tiefe $(2k+1)d$ mit $rn$ Ancillas; als Korollar ein Test auf Schaltkreiskomplexität.

### Einordnung in die Tabellen

* **Task type:** Identifying gegen eine Klasse mit Versprechen (Tiefe $d$ auf einem Gitter); Korollar 1 ist ein Ein-Bit-Test (triviale Phase oder hohe Komplexität).
* **Objekt:** reiner Zustand auf $n$ Qubits eines $k$-dimensionalen Gitters. **Zugriff:** Sample; Tomographie der Reduktionen auf konstant großen Regionen, danach rein klassische Verarbeitung.
* **Status:** 🟢 🟢 🟢 für $d = O(1)$: $M = \tilde O(n^4)2^{O(c)}/\epsilon^4$ Kopien, Zeit $M + (nkd\cdot c/\epsilon)^{O(dc)}$ mit $c = O((3k)^{k+2}d)^k$; quasipolynomiell für $d = \mathrm{polylog}(n)$.
* **Versprechen:** Geometrie und Tiefe; beliebige Zwei-Qubit-Gatter.

### Das Problem

Reduktionen ausreichender Größe bestimmen den Zustand informationstheoretisch; die Frage ist die Rechenzeit. Der naive Weg, lokale Schaltkreise für Regionen zu finden und über Konsistenz auf Überlappungen zu verkleben, ist ein Constraint-Satisfaction-Problem, in 2D und höher hart. Huang et al. reduzieren 2D auf ein effizientes 1D-Problem; ab 3D versagt das.

### Kernresultate

* **Theorem 1 / 4 (Hauptresultat).** Ausgabe eines Schaltkreises $W$ der Tiefe $(2k+1)d$, der $\vert\psi\rangle$ bis auf $\epsilon$ präpariert, mit $M$ und $T$ wie oben; $W$ nutzt $rn$ Ancillas für beliebig kleines $r > 0$.
* **Fakt 1 und 2.** Für jede Region $A$ existiert eine lokale Inversion $V$ auf $B(A, d)$ der Tiefe $d$; und $\vert\psi\rangle$ ist invariant unter jedem "Replacement-Prozess" (Inversion anwenden, $A$ durch $\vert 0\rangle$ ersetzen, Inversion rückgängig machen).
* **Theorem 2 (Überdeckung impliziert Lernen).** Existiert ein Überdeckungsschema mit $\ell$ Schichten, so dass der Rückwärtslichtkegel des Outputs vollständig von den Ersetzungsstücken überdeckt wird und nicht vom Inputzustand abhängt, dann lernt der Algorithmus.
* **Theorem 3 (Gitterüberdeckung).** Für $k$-dimensionale Gitter existiert ein $(k+1, c, d)$-Überdeckungsschema; daher Tiefe $(2k+1)d$.
* **Korollar 1 / Theorem 5 (Komplexitätstest).** Entscheide mit polynomiellen Kopien und Zeit, ob $\vert\psi\rangle$ von einem Schaltkreis der Tiefe $\leq L$ präpariert wird oder $0.01$-weit von allen Zuständen konstanter Tiefe mit $O(n)$ Ancillas ist.

### Methodischer Ansatz

* Erste Einsicht: Eine lokale Inversion anwenden und wieder rückgängig machen ändert den Zustand nicht, ersetzt aber einen Teil des unbekannten Zustands durch ein bekanntes Stück Schaltkreis. Zweite Einsicht: Mit einer geometrisch gewählten Reihenfolge von Regionen werden diese Stücke so geschichtet, dass der Rückwärtslichtkegel des Endzustands nur bekannte Stücke enthält.
* Der gelernte Schaltkreis besteht aus Teilen lokaler Inversionen und ihrer Inversen; es wird nie verlangt, dass zwei Inversionen übereinstimmen.

### Bedeutung und Anwendungen

* Zustände der trivialen Phase (konstante oder polylog Tiefe) sind in Polynomialzeit lernbar, in jeder Dimension; und die Zugehörigkeit zur trivialen Phase ist effizient testbar.
* Für NISQ-Algorithmen ein beweisbares Primitiv: einen flachen Schaltkreis für einen unbekannten Zustand finden.

### Bezug zum eigenen Projekt

* Der Replacement-Prozess ist eine Nichtstörungs-Technik: Man lernt, indem man Struktur einsetzt, die den Zustand invariant lässt; für Phase 2 ist das ein Muster, wie ein Probe-Zustand konstruiert werden kann, der die Zielgröße nicht verändert, aber die Messung linear macht.
* Der Komplexitätstest ist ein Klassentest ohne Kenntnis des Schaltkreises; die Displacement-Version wäre ein Test, ob ein Zustand ein sparsames Spektrum hat, bevor man es sucht.
* Die Exponenten $c = O((3k)^{k+2}d)^k$ zeigen, wie schnell die Konstanten mit der Geometrie wachsen; für die Instanzenleiter ist $k$ ein eigener Parameter.

### Grenzen und offene Fragen

* Konstanten und Tiefenaufblähung $(2k+1)d$; Ancillas werden gebraucht.
* Nur Gitter; allgemeine Graphen beschränkten Grades nicht behandelt.
* Keine unteren Schranken für die Zeit in $d$.

### Fragen zum Tieferbohren

* Wie sieht das $(k+1)$-schichtige Überdeckungsschema in 3D konkret aus, und warum reichen $k+1$ Schichten?
* Wie geht die approximative Inversion (Abschnitt 4) in die Fehlerakkumulation ein, und warum $\epsilon^{-4}$?
* Lässt sich der Komplexitätstest auf "Tiefe $\leq L$ nach Konjugation mit einer Displacement-Basiswahl" erweitern?

Paper: [arXiv:2410.23618](https://arxiv.org/abs/2410.23618)

---

## Optimal algorithms for learning quantum phase states (arXiv:2208.07851)

Die Arbeit von **Srinivasan Arunachalam, Sergey Bravyi, Arkopal Dutt und Theodore J. Yoder** (IBM, MIT; TQC 2023) bestimmt die Sample-Komplexität des Lernens binärer Phasenzustände $\vert\psi_f\rangle = 2^{-n/2}\sum_x(-1)^{f(x)}\vert x\rangle$ mit $\deg f\leq d$ über $\mathbb{F}_2$: $\Theta(n^d)$ Kopien mit separablen Messungen (nur Einzelqubit-Gatter und Messungen), $\Theta(n^{d-1})$ mit verschränkten Messungen über die Pretty-Good-Measurement. Dazu verallgemeinerte Phasenzustände über $\mathbb{Z}_q$, sparsame und rauschbehaftete Varianten und Query-Zugriff auf das diagonale Präparationsunitary.

### Einordnung in die Tabellen

* **Task type:** Identifying gegen eine Klasse mit Versprechen; die Klasse $P(n, d)$ hat $2^{\Theta(n^d)}$ Elemente, und die Ausgabe ist das Polynom $f$ exakt. Mit Query-Zugriff auf $C = \sum_x(-1)^{f(x)}\vert x\rangle\langle x\vert$ dieselben Zahlen, weil eine Query auf $\vert +\rangle^{\otimes n}$ eine Kopie erzeugt.
* **Objekt:** Zustand. **Zugriff:** Sample, separabel (Einzelqubit-Messungen in $X$ und $Z$) oder verschränkt (PGM auf $\vert\psi_f\rangle^{\otimes M}$); Query an $C$ oder $V$ (Abschnitt 6).
* **Status:** separabel 🟢 🟢 🟢 mit $O(n^d)$ Kopien und $O(n^{3d-2})$ Zeit; verschränkt $\Theta(n^{d-1})$ Kopien, aber Zeit $O(\exp(n^d\log 2))$, also 🟢 🔴 🟢.
* **Versprechen:** Grad $d\leq n/2$; für $d = 1$ Bernstein–Vazirani mit $\Theta(1)$, für $d = 2$ Bell-Sampling mit $O(n)$.

### Das Problem

Grad-2-Phasenzustände (Graphzustände, Clifford-Outputs) lernt man per Bell-Sampling; auf zwei Kopien eines Grad-3-Zustands liefert Bell-Sampling eine einzelne Kopie eines zufälligen Grad-2-Zustands $\vert\psi_{g_y}\rangle$, und es bräuchte $\Omega(\sqrt{2^n})$ Kopien, um davon genug zu sammeln. Was ist die richtige Sample-Komplexität, und helfen verschränkte Messungen?

### Kernresultate

* **Theorem 3 (separabel, obere Schranke).** $M = O(2^dn^d)$ Kopien: Miss alle Qubits außer dem ersten in $Z$, erhalte $y$; das erste Qubit ist $\tfrac{1}{\sqrt2}((-1)^{f(0y)}\vert 0\rangle + (-1)^{f(1y)}\vert 1\rangle)$, und eine $X$-Messung gibt die Ableitung $p_1(y) = f(0y) + f(1y)$, ein Polynom vom Grad $\leq d-1$ in $n-1$ Variablen; $O(n^{d-1})$ Punkte pro Richtung, $n$ Richtungen, dann Interpolation.
* **Theorem 5 (separabel, untere Schranke).** $\Omega(n^d)$ für beliebige Einzelkopien-Messungen: Für zufälliges $f$ ist $\mathbb{E}_f[H(x\vert f)]\geq n - O(1)$, jede Kopie liefert $O(1)$ Bit, $f$ hat $\Omega(n^d)$ Bit Entropie.
* **Theorem 4 (verschränkt).** $O((2n)^{d-1})$ Kopien per PGM: Das Ensemble ist geometrisch uniform, die PGM-Erfolgswahrscheinlichkeit ist für alle $f$ gleich, und die Gewichtsverteilung von Polynomen (Schranke von Ben-Eliezer, Hod, Lovett) kontrolliert die Überlappungen. Holevo gibt $\Omega(n^{d-1})$.
* **Theorem 8 (verallgemeinert, $\mathbb{Z}_q$).** $O(2^dq^3n^d\log q) = O(n^d)$ separabel; die POVM $\{\vert\phi_b\rangle\langle\phi_b\vert\}_{b\in\mathbb{Z}_q}$ schließt den wahren Wert $c$ mit Sicherheit aus und trifft jeden anderen mit Wahrscheinlichkeit $\Omega(q^{-3})$.
* **Theoreme 6, 7, 9, 11.** Sparsame $f$ mit $O(2^dsn)$; Fourier-Grad $d$ mit $O(2^{2d})$; globale Depolarisierung $n^{1+O(\epsilon)}$; lokale Depolarisierung $\Theta((1-\epsilon)^{-n})$.
* **Property Testing.** Lernen plus SWAP-Test testet Zugehörigkeit zu $P(n, d)$ mit $n^d$ Kopien.

### Methodischer Ansatz

* Ableitungen statt Bell-Sampling: Die Messung von $n-1$ Qubits in $Z$ reduziert den Grad um eins, und Interpolation über $\mathbb{F}_2$ setzt $f$ aus $n$ partiellen Ableitungen zusammen.
* Für die PGM eine neue Beobachtung: Bei geometrisch uniformen Ensembles ist die Erfolgswahrscheinlichkeit unabhängig vom Element.
* Die untere Schranke rechnet die Rényi-2-Entropie über eine explizite Formel für $\mathbb{E}_f[\vert\psi_f\rangle\langle\psi_f\vert^{\otimes 2}]$.

### Bedeutung und Anwendungen

* Graphzustände werden mit Einzelqubit-Operationen lernbar (bisher Bell-Messungen nötig); Grad 3 sind Hypergraphzustände für MBQC und IQP-Schaltkreise.
* Die Klasse ist die Grundlage der PRS-Konstruktionen (Ji–Liu–Song, Brakerski–Shmueli): Bei polynomiellem Grad wäre Lernen kryptographisch hart; die Grad-Skala ist die Instanzenleiter dieser Familie.
* Die Tabelle des Papers ist ein Modell dafür, wie Sample, Zeit und Messklasse getrennt zu führen sind.

### Bezug zum eigenen Projekt

* Der Vergleich separabel gegen verschränkt ist ein $n$-Faktor in den Kopien, die Zeit dreht sich um: PGM ist exponentiell. Das ist der Speicher–Zeit-Tausch der Tabellen in Reinform, und ein Warnzeichen, dass Zweikopien-Protokolle ihren Vorteil nur behalten, wenn die Nachverarbeitung linear-algebraisch bleibt (wie bei Bell-Sampling), nicht wenn sie eine PGM implementieren muss.
* Die Ableitungsmessung ist ein Probe-Mechanismus: Konditionierung auf $y$ macht die verbleibende Amplitude zu einem Ein-Qubit-Problem erster Ordnung; Phase 2 konditioniert analog auf einen Träger.
* Für $\mathbb{Z}_q$ ist die POVM, die einen Wert sicher ausschließt, ein Ausschlussdesign; für Displacement-Phasen $\omega_d^c$ ist dieselbe Konstruktion einsetzbar.

### Grenzen und offene Fragen

* Die verschränkte Variante ist zeitineffizient; ob $\Theta(n^{d-1})$ Kopien mit polynomieller Zeit erreichbar sind, ist offen.
* Verallgemeinerte Phasenzustände nur separabel behandelt.
* Nur exakte Identifikation von $f$; agnostische Varianten nicht.

### Fragen zum Tieferbohren

* Wie geht die Gewichtsschranke $\vert\{f: \mathrm{wt}(f)\leq(1-\epsilon)2^{-\ell}\}\vert\leq(1/\epsilon)^{C\ell\binom{n-\ell}{\leq d-\ell}}$ konkret in die PGM-Analyse ein?
* Warum liefert Bell-Sampling auf Grad-$d$-Zuständen genau einen Grad-Abstieg um eins, und lässt sich das iterieren, wenn man Kopien der Zwischenzustände erzeugen kann (Query-Modell)?
* Was ist die Displacement-Version eines Grad-$d$-Phasenzustands auf Qudits, und ist sein Spektrum sparsam?

Paper: [arXiv:2208.07851](https://arxiv.org/abs/2208.07851)

---

## Schur–Weyl duality for the Clifford group with applications: property testing, a robust Hudson theorem, and de Finetti representations (arXiv:1712.08628)

Die Arbeit von **David Gross, Sepehr Nezami und Michael Walter** (Köln, Stanford, Amsterdam; Commun. Math. Phys. 2021) bestimmt den Kommutanten der $t$-ten Tensorpotenz der Clifford-Gruppe: Er wird von Operatoren $R(T) = r(T)^{\otimes n}$ aufgespannt, die zu selbstdualen Codes $T\subseteq\mathbb{Z}_d^{2t}$ gehören, und seine Größe ist ab $n\geq t-1$ unabhängig von $n$. Als Anwendungen: ein Stabilizer-Test mit sechs Kopien für Qubits (Bell-Difference-Sampling), $2s$ Kopien für Qudits, drei Kopien für $d\equiv 1, 5 \bmod 6$; ein robuster Hudson-Satz; und de-Finetti-Sätze für Clifford-invariante Zustände.

### Einordnung in die Tabellen

* **Task type:** Identifying, Ein-Bit (Property Testing): Stabilizerzustand oder $\max_S\vert\langle S\vert\psi\rangle\vert^2\leq 1-\epsilon^2$. Perfekt vollständig, dimensionsunabhängig, transversal. Cliffordness von Unitaries folgt, ohne Zugriff auf die Inverse.
* **Objekt:** reiner Zustand auf $n$ Qudits. **Zugriff:** Sample; Bell-Messungen auf Kopienpaaren und Weyl-Messungen auf Einzelkopien; kohärent nur über zwei Kopien und faktorisiert über die $n$ Qudits.
* **Status:** 🟢 🟢 🟢. Sechs Kopien pro Runde, $O(1/\epsilon^2)$ Runden, $O(n)$ Gatter, Speicher $2n$ Qubits; optimal in der Kopienzahl unter perfekt vollständigen Tests.
* **Versprechen:** keines; der Test ist agnostisch in dem Sinn, dass er die Fidelity zum nächsten Stabilizerzustand misst.

### Das Problem

Zweite und dritte Momente von Stabilizerzuständen stimmen mit Haar überein, vierte sind nicht dimensionsunabhängig unterscheidbar; bisherige Tests identifizierten den Zustand und brauchten $\Omega(n)$ Kopien. Gibt es einen Test mit konstant vielen Kopien, und was ist die Symmetriestruktur, die ihn erzwingt?

### Kernresultate

* **Theorem 3.2 (Bell-Difference-Sampling).** $\mathrm{Tr}(\Pi_a\psi^{\otimes 4}) = \sum_xp_\psi(x)p_\psi(x+a)$ mit $p_\psi(a) = \vert c_a\vert^2$ der charakteristischen Verteilung; für Stabilizerzustände gleich $p_S(a)$, also gleichverteilt auf der Stabilizergruppe. Löst das Problem, dass Bell-Sampling nur für reelle Zustände die charakteristische Verteilung liefert.
* **Theorem 3.3 (Qubits).** Algorithmus 1: Bell-Differenz-Sample $a$, dann $W_a$ zweimal auf frischen Kopien messen, akzeptiere bei gleichem Ergebnis. $p_{\mathrm{accept}} = 1$ für Stabilizerzustände, $\leq 1-\epsilon^2/4$ sonst. Beweis: Hohe Akzeptanz erzwingt $p_\psi(a) > \tfrac12 2^{-n}$ auf einer großen Menge; die Unschärferelation (Fig. 1: $\vert\mathrm{Tr}\,Z\rho\vert$ und $\vert\mathrm{Tr}\,X\rho\vert$ können nicht beide $> 1/\sqrt2$ sein) erzwingt Kommutativität; also eine Stabilizer-Untergruppe.
* **Theorem 3.11 (Qudits).** $\Pi_{s, \mathrm{accept}} = \tfrac12(I + V_s)$ mit $V_s = d^{-n}\sum_x(W_x\otimes W_x^\dagger)^{\otimes s}$, $(d, s) = 1$, $2s$ Kopien; $p_{\mathrm{accept}}\leq 1 - C_{d,s}\epsilon^2$ mit $C_{d,s} = (1-(1-1/4d^2)^{s-1})/2$. **Lemma 3.10:** $\vert\mathrm{Tr}\,\psi W_x\vert^2, \vert\mathrm{Tr}\,\psi W_y\vert^2 > 1 - 1/4d^2$ erzwingt $[W_x, W_y] = 0$.
* **Theorem 8.6 (drei Kopien).** Für $d\equiv 1, 5 \bmod 6$ mit Phasenraum-Punktoperatoren $A_x$: $V = d^{-n}\sum_xA_x^{\otimes 3}$, $p_{\mathrm{accept}}\leq 1-\epsilon^2/16d^2$.
* **Struktur (Theorem 4.3 ff.).** Der Kommutant von $\mathrm{Cl}_n^{\otimes t}$ wird von $R(T)$ für selbstduale Codes $T$ aufgespannt, mit der stochastischen orthogonalen Gruppe $O_t(d)$ als Symmetrie; die Anti-Identität $R(\bar 1) = 2^{-n}(I^{\otimes t} + X^{\otimes t} + Y^{\otimes t} + Z^{\otimes t})^{\otimes n}$ ist das einfachste nichttriviale Element.

### Methodischer Ansatz

* Clifford-invariante Tests müssen im Kommutanten liegen; die Klassifikation der Kommutanten macht die Suche nach Tests zu einer Suche über Codes.
* Die Unschärferelation für Weyl-Operatoren ist das analytische Herz; sie übersetzt "viele schwere Adressen" in "kommutierende Adressen".
* Für die de-Finetti-Sätze werden die $R(T)$ als Verallgemeinerung der Permutationen behandelt.

### Bedeutung und Anwendungen

* Bell-Difference-Sampling ist seit diesem Paper das Standardprimitiv für Stabilizer-Lernen und -Testen (Grewal et al., Chen–Gong–Ye–Zhang, Arunachalam–Dutt, Bao et al.).
* Der Kommutant ist die Grundlage für Clifford-Designs, für Stabilizer-Entropie-Formeln (Leone et al.) und für Schatten-Varianzrechnungen.

### Bezug zum eigenen Projekt

* Theorem 3.2 ist die exakte Aussage, dass vier Kopien die Faltung $p_\psi * p_\psi$ liefern; zwei Kopien $\rho\otimes\rho^*$ liefern $p_\psi$ selbst. Das eigene Protokoll spart also die Faltung und die Hälfte der Kopien gegen den Preis einer konjugierten Kopie; die Unschärferelation überträgt sich direkt auf Displacement-Operatoren (Lemma 3.10 ist bereits für Qudits formuliert).
* Die Fallunterscheidung $(d, s) = 1$ und $d\equiv 1, 5 \bmod 6$ zeigt, dass die Kopienzahl vom Alphabet abhängt; für ungerade Primzahlen $d$ ist die Situation günstiger als für Qubits.
* Der Kommutant ist die Sprache, in der eine CNN-Symmetrie (Clifford-Invarianz der Bell-Statistik) formuliert werden sollte.

### Grenzen und offene Fragen

* Nur reine Zustände in den Testsätzen; gemischte Zustände und toleranter Test (Akzeptanz nahe eins) sind die Folgearbeiten.
* Die Konstante $\epsilon^2/4$ ist nicht optimiert; die Kopienzahl sechs ist für perfekte Vollständigkeit optimal, nicht für Tests mit Fehler erster Art.
* Der Kommutant für $d$ nicht prim ist nur teilweise behandelt.

### Fragen zum Tieferbohren

* Wie gehen die Codes $T$ und die Gruppe $O_t(d)$ in die Konstruktion des Sechs-Kopien-Operators $V = 2^{-n}\sum_xW_x^{\otimes 6}$ ein?
* Warum ist Bell-Sampling nur für reelle Zustände die charakteristische Verteilung, und ist die konjugierte Kopie genau das, was Komplexität behebt?
* Wie sieht der robuste Hudson-Satz aus, und ist er ein Aussage über die Sparsity der Wigner-Funktion, also ein Vorläufer für sparsame Displacement-Spektren?

Paper: [arXiv:1712.08628](https://arxiv.org/abs/1712.08628)

---

## Tolerant testing of stabilizer states with a polynomial gap via a generalized uncertainty relation (arXiv:2410.21811)

Die Arbeit von **Zongbo (Bob) Bao, Philippe van Dordrecht und Jonas Helsen** (QuSoft/CWI, Universität Amsterdam; 2024) macht den Stabilizer-Test von Gross, Nezami, Walter tolerant mit polynomieller Lücke: Hat ein Zustand Stabilizer-Fidelity $\geq\epsilon_1$ oder $\leq\epsilon_2$ mit $\epsilon_2\leq C'\epsilon_1^{672}$, dann entscheiden $O(\epsilon_1^{-12})$ Runden Bell-Difference-Sampling zwischen beiden Fällen. Das Werkzeug ist eine verallgemeinerte Unschärferelation $\sum_i\mathrm{Tr}(\psi A_i)^2\leq\vartheta(\Gamma_{\mathcal{A}})$ über die Lovász-Theta-Zahl des Antikommutationsgraphen; sie ersetzt eine Vermutung, die Arunachalam–Dutt für ihre Version brauchten.

### Einordnung in die Tabellen

* **Task type:** Identifying, Ein-Bit, tolerant: Beide Hypothesen sind Fidelity-Intervalle, keine ist "exakt in der Klasse". Das ist die Testversion der agnostischen Tomographie.
* **Objekt:** reiner $n$-Qubit-Zustand. **Zugriff:** Sample; Bell-Difference-Sampling auf vier Kopien, sonst nichts.
* **Status:** 🟢 🟢 🟢. $O(\epsilon_1^{-12})$ Runden, also $O(\epsilon_1^{-12})$ Kopien, polynomielle Zeit, Speicher $2n$ Qubits.
* **Versprechen:** keines über den Zustand; die Lücke $\epsilon_2\leq C'\epsilon_1^{672}$ ist eine Bedingung an die Fragestellung.

### Das Problem

Der Test von Gross, Nezami, Walter akzeptiert Stabilizerzustände mit Sicherheit und weist Zustände mit Fidelity $\leq 1-\epsilon^2$ mit Wahrscheinlichkeit $\geq\epsilon^2/4$ ab; er sagt nichts über Zustände, die nahe, aber nicht exakt Stabilizer sind. Arunachalam und Dutt gaben einen toleranten Test, dessen Lücke von einer Vermutung über Gowers-Normen abhing (aus einer Fehlzitierung von Viola). Lässt sich die Lücke unbedingt und polynomiell machen?

### Kernresultate

* **Theorem 1.** $\epsilon_1, \epsilon_2\in[0, 1]$, $F_S(\psi) = \max_{S}\vert\langle\psi\vert S\rangle\vert^2$ entweder $\geq\epsilon_1$ oder $\leq\epsilon_2$; falls $\epsilon_2\leq C'\epsilon_1^{672}$, unterscheiden $O(\epsilon_1^{-12})$ Bell-Difference-Runden mit Wahrscheinlichkeit $> 2/3$.
* **Lemma 15.** Für Weyl-Operatoren $\{A_i\}_{i=1}^M$ und reines $\psi$: $\sum_i\mathrm{Tr}(\psi A_i)^2\leq\Psi_0(\mathcal{A})$, das Maximum der Operatornorm normierter Hamiltonians $\sum_ia_iA_i$; der Beweis ist die Cauchy–Schwarz-Zeile (13), (14).
* **Lemma 18 (verallgemeinerte Unschärfe).** $\sum_i\mathrm{Tr}(\psi A_i)^2\leq\Psi_0(\mathcal{A})\leq\Psi(\Gamma_{\mathcal{A}})\leq\vartheta(\Gamma_{\mathcal{A}})$ mit Hastings–O'Donnell (Prop. 4.8) für den letzten Schritt; für $M$ paarweise antikommutierende Operatoren ist $\vartheta = 1$, für $\Gamma = \sqcup$ und $\boxtimes$ von Graphen ist $\vartheta$ additiv bzw. multiplikativ (Fakten 3, 4).
* **Theorem 19 (aus Arunachalam–Dutt).** $\mathbb{E}_{x\sim q_\psi}[2^np_\psi(x)]\geq\gamma$ und $2^n\geq C''\ln(C'''/\gamma)/\gamma^3$ liefern einen Unterraum $V$ mit $\sum_{x\in V}\vert\langle\psi\vert W_x\vert\psi\rangle\vert^2\geq C_1\gamma^{55}\vert V\vert$ und $\geq C_2\gamma^{57}2^n$; die Unschärferelation zeigt dann, dass eine große isotrope Untergruppe $V_0\subseteq V$ existiert, und Balog–Szemerédi–Gowers (Theorem 25) macht daraus einen Stabilizerzustand mit Fidelity $\mathrm{poly}(\gamma)$.

### Methodischer Ansatz

* Bell-Difference-Sampling akzeptiert mit Wahrscheinlichkeit, die die charakteristische Verteilung $p_\psi$ gegen ihre Faltung $q_\psi$ gewichtet; hohe Akzeptanz heißt viel Masse auf einer nahezu linearen Menge. Die Unschärferelation begrenzt, wie viel Masse auf antikommutierenden Adressen liegen kann, also ist die schwere Menge fast kommutativ.
* Die Lovász-Theta-Zahl ersetzt die Gowers-Norm-Vermutung; sie ist berechenbar und über Produkte und disjunkte Vereinigungen von Antikommutationsgraphen multiplikativ und additiv.
* Der Exponent 672 wird von den Autoren als "vermutlich stark suboptimal" bezeichnet; unabhängige Beweise (Arunachalam–Bravyi–Dutt; Mehraban–Tahmasbi) kamen kurz danach mit ähnlichen oder etwas schlechteren Graden.

### Bedeutung und Anwendungen

* Erster unbedingter toleranter Stabilizer-Test mit polynomieller Lücke; die Aufgabe, die bei Gross–Nezami–Walter perfekt vollständig war, wird robust gegen Rauschen.
* Die Unschärferelation über $\vartheta$ ist ein eigenständiges Werkzeug für Pauli-Spektren; sie quantifiziert, wie viele nichtkommutierende Erwartungswerte gleichzeitig groß sein können.

### Bezug zum eigenen Projekt

* Lemma 18 ist genau die Aussage, die Phase 1 braucht, um aus "viele große Displacement-Beträge" auf "die Adressen liegen fast in einer isotropen Untergruppe" zu schließen; die Verallgemeinerung auf Weyl-Operatoren über $\mathbb{Z}_d$ ist im Beweis von Lemma 15 nicht qubit-spezifisch.
* Die Kette "Akzeptanzwahrscheinlichkeit → Masse auf linearer Menge → Balog–Szemerédi–Gowers → Untergruppe" ist die Beweisstruktur, mit der ein toleranter Träger-Test für Displacement-Spektren aufzubauen wäre; die Exponenten (55, 57, 672) zeigen, was additive Kombinatorik gegenwärtig kostet.
* Toleranz ist Regime 3 auf der Instanzenleiter; $O(\epsilon_1^{-12})$ Kopien ist der Preis, den ein Ein-Bit-Test dort zahlt.

### Grenzen und offene Fragen

* Exponenten 672 und 12 sind weit von der vermuteten Wahrheit; das Paper nennt die Verbesserung als nächstes Ziel.
* Nur reine Zustände; gemischte Inputs und Qudits nicht behandelt.
* Keine untere Schranke.

### Fragen zum Tieferbohren

* Wo genau im Beweis geht der Faktor $\gamma^{55}$ verloren, und welcher Schritt ist BSG-bedingt?
* Gilt Lemma 18 mit derselben Konstante für Displacement-Operatoren auf Qudits, deren Antikommutation durch $\omega_d$-Kommutation ersetzt ist?
* Lässt sich der Test mit $\rho\otimes\rho^*$ statt $\rho^{\otimes 4}$ führen, sodass die Akzeptanz $p_\psi$ direkt statt der Faltung gewichtet?

Paper: [arXiv:2410.21811](https://arxiv.org/abs/2410.21811)

---

## Exponential separations between learning with and without quantum memory (arXiv:2111.05881)

Die Arbeit von **Sitan Chen, Jordan Cotler, Hsin-Yuan Huang und Jerry Li** (Berkeley, Harvard, Caltech, Microsoft; FOCS 2021) beweist scharfe untere Schranken für Lernalgorithmen ohne Quantenspeicher: Shadow-Tomographie braucht $\tilde\Theta(\min\{M, 2^n\}/\epsilon^2)$ Kopien, alle Pauli-Erwartungswerte $\Omega(2^n)$, Purity-Testing $\Theta(2^{n/2})$; mit $k$ Qubits Speicher $\Omega(2^{(n-k)/3})$ für Pauli-Beträge. Für Kanäle: Unterscheidung des vollständig depolarisierenden Kanals von einem Haar-zufälligen unitären Kanal $\Omega(2^{n/3})$, Zeitumkehrsymmetrien $\Omega(2^{2n/7})$, jeweils gegen beliebige Algorithmen ohne Speicher, auch mit Ancillas. Das Werkzeug ist die Baumdarstellung adaptiver Protokolle und eine direkte Totalvariationsschranke über einseitige Likelihood-Verhältnisse.

### Einordnung in die Tabellen

* **Task type:** Identifying, Ein-Bit (Purity, Kanaltests) und Estimating (Shadow-Tomographie); die Zeile steht bei Identifying, weil die schärfsten Aussagen Unterscheidungsprobleme sind und die Estimating-Schranken über Le Cam auf sie reduziert werden.
* **Objekt:** Zustand oder Kanal. **Zugriff:** Sample ohne Quantenspeicher (jede Kopie einzeln gemessen, adaptiv erlaubt), mit $k$ Qubits Speicher, oder mit vollem Speicher; für Kanäle beliebige Inputs mit $m > n$ Qubits und Ancillas.
* **Status:** 🟢 🔴 🟢 ohne Speicher (Kopien exponentiell), 🟢 🟢 🟢 mit $O(n)$ Qubits Speicher: $O(1)$ Kopien für Purity (SWAP-Test), $O(n)$ für alle Pauli-Beträge, $O(1)$ Aufrufe für die Kanaltests.
* **Versprechen:** keines; die Trennungen sind unbedingt und informationstheoretisch.

### Das Problem

Huang, Kueng, Preskill hatten $\Omega(M^{1/6}/\epsilon^2)$ bzw. $\Omega(2^{n/3}/\epsilon^2)$ ohne Speicher gezeigt, gegen obere Schranken $O(M\log M/\epsilon^2)$ und $\tilde O(2^n)$; Aharonov, Cotler, Qi hatten Kanaltrennungen nur ohne Ancillas. Wie groß sind die Lücken wirklich, und gilt die Trennung gegen alle speicherlosen Protokolle?

### Kernresultate

* **Theorem 1.1 (Shadow-Tomographie).** Es gibt $M$ Observablen, für die ohne Speicher $T = \tilde\Theta(\min\{M, 2^n\}/\epsilon^2)$ Kopien nötig sind; passend zur oberen Schranke aus klassischen Schatten bis auf Logarithmen. Beantwortet Aaronsons Frage.
* **Theorem 1.2 (Paulis).** Alle $\mathrm{Tr}(P\rho)$ bis auf $\epsilon$: $\Omega(2^n/\epsilon^2)$ ohne Speicher; der Beweis ist eine halbe Seite.
* **Theorem 1.3 (Purity).** Rein oder maximal gemischt: $\Omega(2^{n/2})$ ohne Speicher, mit passendem Algorithmus $O(2^{n/2})$ (Theorem 5.13); $O(1)$ mit SWAP-Test.
* **Theorem 1.4 (beschränkter Speicher).** $k$ Qubits Speicher: $\Omega(2^{(n-k)/3})$ Kopien für alle Pauli-Beträge; $O(n)$ mit $n$ Qubits Speicher.
* **Theoreme 1.5, 1.6 (Kanäle).** Depolarisierend gegen Haar-unitär $\Omega(2^{n/3})$; unitär, orthogonal oder symplektisch $\Omega(2^{2n/7})$; beides gegen beliebige speicherlose Protokolle mit Ancillas, wo Aharonov–Cotler–Qi nur ohne Ancillas gezeigt hatten.

### Methodischer Ansatz

* Le Cams Zwei-Punkt-Methode mit Nullhypothese $\rho_{\mathrm{mm}}$ und Mischung $\rho_P = 2^{-n}(I + \epsilon P)$; die Neuerung ist, direkt mit Totalvariation zu arbeiten statt mit $\chi^2$ oder KL (die für Paulis nur $\mathrm{poly}(n, 1/\epsilon)$ liefern würden) und Fakt 2.1 zu benutzen: eine einseitige Schranke $\mathbb{E}_P[q_1^P(x)]/q_0(x) > 1-\delta$ auf allen Blättern gibt $d_{\mathrm{TV}}\leq\delta$.
* Baumdarstellung (Abschnitt 2.1): Ein adaptives Protokoll ohne Speicher ist ein Baum, Knoten sind POVMs auf frischen Kopien, Blätter sind Ausgaben; die Kantenwahrscheinlichkeiten hängen vom unbekannten Zustand ab, und die Likelihood-Verhältnisse werden entlang der Pfade kontrolliert.
* Für Kanäle und beschränkten Speicher braucht es mehr (Matrixkonzentration, Martingale), weil die einseitige Schranke nicht überall gilt.

### Bedeutung und Anwendungen

* Die Schranken sind bei einigen Dutzend Qubits sichtbar; Quantencomputer mit unter hundert Qubits könnten als Speicher einen beweisbaren Vorteil beim Experimentieren liefern. Das ist die theoretische Grundlage des Sycamore-Experiments von Huang et al. (Science 2022).
* Die Baumtechnik ist seit diesem Paper das Standardwerkzeug für Schranken gegen adaptive, speicherlose Protokolle (Chen–Huang–Li–Liu; Chen–Gong–Zhang; Lowe–Nayak).

### Bezug zum eigenen Projekt

* Der Zweikopien-Vorteil des eigenen Protokolls ist in Theorem 1.2 und 1.4 quantifiziert: Ohne Speicher $\Omega(2^n)$ Kopien für alle Pauli-Beträge, mit einer gespeicherten Kopie $O(n)$. Phase 1 (Beträge des Displacement-Spektrums) ist genau die Aufgabe von Theorem 1.4, und $\rho\otimes\rho^*$ ist die $k = n$-Stufe der Speicherachse.
* Die Schranke $\Omega(2^{(n-k)/3})$ ist die Instanzenleiter in der Speicherdimension: Jeder Qubit Speicher kauft einen konstanten Faktor im Exponenten, und die Frage "Speicher zwischen null und zwei Kopien" hat hier ihre erste quantitative Antwort.
* Die Beweistechnik zeigt, welche Verteilungen hart sind: $\rho_P = 2^{-n}(I + \epsilon P)$ ist ein Displacement-Spektrum mit einer einzigen schweren Adresse; die eigene Hardness-Instanz (LWE) ist die strukturierte Version davon.

### Grenzen und offene Fragen

* Die Speicher-Kopien-Kurve ist nur nach unten bekannt; zwischen $k = 0$ und $k = n$ ist die genaue Sample-Komplexität offen.
* Die Kanaltrennungen sind unbedingt, aber nicht scharf ($2^{n/3}$, $2^{2n/7}$ gegen $O(1)$).
* Rauschen im Speicher ist nicht modelliert.

### Fragen zum Tieferbohren

* Wie sieht die halbseitige Rechnung für Theorem 1.2 aus, und was ändert sich, wenn die Mischung über Displacement-Operatoren statt Paulis läuft?
* Welche Rolle spielen Ancillas in den Kanalschranken, und warum bricht die Technik von Aharonov–Cotler–Qi schon bei einem Ancilla-Qubit?
* Ist die Schranke $\Omega(2^{(n-k)/3})$ für Beträge mit einem Protokoll erreichbar, das $k$ Qubits einer konjugierten Kopie speichert?

Paper: [arXiv:2111.05881](https://arxiv.org/abs/2111.05881)

---

## Tight bounds for quantum state certification with incoherent measurements (arXiv:2204.07155)

Die Arbeit von **Sitan Chen, Brice Huang, Jerry Li und Allen Liu** (Berkeley, MIT, Microsoft; FOCS 2022) bestimmt die Kopienzahl des Mixedness-Testing mit inkohärenten Messungen: $\Theta(d^{3/2}/\epsilon^2)$, auch wenn die Messungen adaptiv gewählt werden. Adaptivität hilft also nicht, was eine offene Frage aus Wrights Dissertation und von Bubeck, Chen, Li beantwortet. Für die allgemeine Zertifizierung gegen ein bekanntes $\sigma$ gibt das Paper instanzoptimale Schranken in der Fidelity $F(\sigma, I/d)$ und der effektiven Dimension, mit einer neuen Beweistechnik über gaußsche Störungen und Matrix-Martingale.

### Einordnung in die Tabellen

* **Task type:** Identifying, $M = 1$ (Certification): $\rho = \sigma$ oder $\Vert\rho - \sigma\Vert_1 > \epsilon$; Mixedness-Testing ist der Fall $\sigma = I/d$.
* **Objekt:** gemischter Zustand in $d$ Dimensionen. **Zugriff:** Sample, inkohärent: eine Kopie nach der anderen, beliebige POVMs, adaptiv erlaubt; kein Quantenspeicher.
* **Status:** 🟢 🟢 🟢 mit $\Theta(d^{3/2}/\epsilon^2)$ Kopien, gegenüber $\Theta(d/\epsilon^2)$ mit verschränkten Messungen (O'Donnell–Wright; Bădescu–O'Donnell–Wright); der Speichervorteil ist ein Faktor $\sqrt d = 2^{n/2}$.
* **Versprechen:** keines; $\sigma$ ist bekannt.

### Das Problem

Bubeck, Chen, Li hatten $\Theta(d^{3/2}/\epsilon^2)$ für nichtadaptive und $\Omega(d^{4/3}/\epsilon^2)$ für adaptive inkohärente Messungen gezeigt. Schließt sich die Lücke nach oben (Adaptivität hilft) oder nach unten (sie hilft nicht)? Und wie hängt die Kopienzahl vom Referenzzustand $\sigma$ ab, analog zum klassischen Identitätstest, dessen Komplexität durch die $\ell_{2/3}$-Quasinorm von $p$ bestimmt ist?

### Kernresultate

* **Theorem 1.1 / 6.1 (Mixedness).** Kopienzahl $\Theta(d^{3/2}/\epsilon^2)$ mit inkohärenten Messungen; Adaptivität ändert nur Konstanten.
* **Theorem 1.2 / 8.1 (instanzoptimal).** Für jedes $\sigma$ und kleines $\epsilon$ liegt die Kopienzahl zwischen $\tilde\Omega\big(\sqrt{d\cdot\underline d_{\mathrm{eff}}}\,F(\underline\sigma, I/d)/\epsilon^2\big)$ und $\tilde O\big(\sqrt{d\cdot\overline d_{\mathrm{eff}}}\,F(\overline\sigma, I/d)/\epsilon^2\big)$, wobei $\underline\sigma$, $\overline\sigma$ durch Abschneiden von Eigenwerten der Masse $\Theta(\epsilon^2)$ bzw. $\Theta(\epsilon)$ entstehen und $d_{\mathrm{eff}}$ ihr Rang ist; für reines $\sigma$ ist $\Theta(1/\epsilon^2)$. Die obere Schranke war von Chen, Li, O'Donnell für nichtadaptive Messungen bekannt.
* **Vermutung.** Für alle $\sigma$ stimmt die adaptive Komplexität mit der nichtadaptiven überein; bewiesen, wenn $\epsilon$ klein gegen den kleinsten Eigenwert von $\sigma$ ist.

### Methodischer Ansatz

* Statt der Paninski-Störung $I/d + \epsilon UZU^\dagger/d$ mit Haar-$U$ wird eine gaußsche Störung benutzt, deren Likelihood-Verhältnis eine selbstähnliche Form (Gl. 4) hat; das reduziert die Analyse auf die Konzentration eines Matrix-Martingals entlang des Baums und ein Matrix-Balancing-Problem.
* Anders als bei allen früheren adaptiven Schranken wird keine punktweise Schranke an das Likelihood-Verhältnis gebraucht; genau das machte Bubeck–Chen–Li lose.
* Die Technik vereinfacht auch die Rechnungen der Vorgänger deutlich und ist auf andere Probleme übertragbar.

### Bedeutung und Anwendungen

* Beantwortet "hilft Adaptivität?" für ein zentrales Testproblem negativ; die Folgearbeiten (Chen, Huang, Li, Liu, Sellke 2023 für Tomographie; Chen, Gong, Zhang 2024 für Shadow-Tomographie, wo Adaptivität hilft) benutzen dieselbe Baum-plus-Martingal-Methode.
* Für NISQ-Verifikation ist $d^{3/2}$ die Referenz: Ohne Speicher zahlt man $\sqrt d$ gegenüber verschränkten Protokollen.

### Bezug zum eigenen Projekt

* Zertifizierung gegen ein bekanntes $\sigma$ ist Phase 2 im Grenzfall einer Hypothese: Der Probe-Zustand ist $\sigma$ selbst. Die Instanzabhängigkeit über $F(\sigma, I/d)$ und $d_{\mathrm{eff}}$ ist eine Instanzenleiter für Referenzzustände, von rein ($1/\epsilon^2$) bis maximal gemischt ($d^{3/2}/\epsilon^2$).
* Die Aussage "Adaptivität hilft nicht" gilt für Einzelkopien; das eigene Protokoll ist zweikopig und nichtadaptiv in Phase 1, adaptiv in Phase 2. Dieses Paper sagt, dass der Gewinn von Phase 2 aus der zweiten Kopie kommen muss, nicht aus der Adaptivität allein.
* Die gaußsche Störung als harte Instanz ist ein dichtes, zufälliges Displacement-Spektrum; die LWE-Instanz ist ihre strukturierte Verwandte mit einem sparsamen Träger.

### Grenzen und offene Fragen

* Die instanzoptimalen Schranken klaffen für manche $\sigma$ und $\epsilon$ polynomiell; die Vermutung der Adaptivitätsfreiheit ist nicht für alle $\sigma$ bewiesen.
* Nur Testen, keine Schätzung; nur Zustände, keine Kanäle.

### Fragen zum Tieferbohren

* Wie sieht die selbstähnliche Form (4) des Likelihood-Verhältnisses aus, und warum verschwindet die Notwendigkeit punktweiser Schranken?
* Welche Rolle spielt das Matrix-Balancing, und ist es die Stelle, an der die Instanzabhängigkeit in $F(\sigma, I/d)$ entsteht?
* Wie lautet die Schranke, wenn eine Kopie von $\sigma$ (statt ihrer Beschreibung) mitgeliefert wird, also für den SWAP-Test-Zugriff?

Paper: [arXiv:2204.07155](https://arxiv.org/abs/2204.07155)

---

## Quantum algorithmic measurement (arXiv:2101.04634)

Die Arbeit von **Dorit Aharonov** (Hebrew University), **Jordan Cotler** (Harvard) und **Xiao-Liang Qi** (Stanford) stellt eine Frage, die vor jeder Lernschranke kommt: Was ist ein Experiment, formal? Die Antwort ist ein Rechenmodell, der **QUALM** (*quantum algorithmic measurement*), eine Mischung aus Black-Box-Algorithmus und interaktivem Protokoll. Mit diesem Modell beweisen die Autoren die erste exponentielle Trennung zwischen kohärenten und inkohärenten Experimenten für physikalisch motivierte Aufgaben, bei der die kohärente Seite in Aufrufen *und* Gattern effizient ist. Der Rahmen ist die gemeinsame Sprache, in der die Speicher-Trennungen der Bell-Sampling-Literatur formuliert sind.

### Einordnung in die Tabellen

* **Task type:** Identifying. Beide Theoreme sind Unterscheidungsaufgaben mit einem Bit oder einem von drei Labels als Output. Das ist Property Testing eines Prozesses, das Prozess-Gegenstück zum Purity-Test in der Identifying-Tabelle.
* **Objekt:** Unitary, als Lab-Orakel. Im ersten Problem wird gerade getestet, ob das Orakel stationär ist: derselbe Unitary bei jedem Aufruf oder jedes Mal ein neuer.
* **Zugriff:** Beide Seiten der Trennung benutzen dasselbe Orakel auf festem Input. Verschieden ist nur, ob die Outputs mehrerer Aufrufe ungemessen gehalten und gemeinsam gemessen werden dürfen. In den Begriffen dieses Dokuments ist das die Speicherachse (Anhang, *Measurement power*), nicht die Zugriffsleiter.
* **Status:** 🟢 🟢 🟢 mit kohärentem Zugriff: $O(1)$ Aufrufe, $O(\ell)$ Gatter für den SWAP-Test, $2\ell$ Qubits Quantenspeicher. Ohne Kohärenz mindestens $\Omega(2^{2\ell/7})$ Aufrufe, auch adaptiv.
* **Warum hier und nicht unter Cross-Task:** Der Rahmen selbst gilt für alle drei Aufgabentypen und steht deshalb zusätzlich im Anhang. Die beiden bewiesenen Sätze sind aber Identifying-Aufgaben, und die Zusammenfassungen folgen der Aufgabe.

### Das Problem

Ein Experiment soll eine Funktion eines physikalischen Systems berechnen, etwa die Kristallstruktur aus einem Beugungsbild. Anders als ein Algorithmus bekommt es keine klassische Beschreibung seines Inputs, sondern nur Zugriff über Wechselwirkung und Messung. Werkzeuge aus dem Quantenrechnen verbessern Experimente seit Jahren (Fehlerkorrektur in der Metrologie, Shadow-Tomographie, Compressed Sensing), aber es fehlte ein Modell, in dem man die Kosten eines Experiments definieren und Verbesserungen beweisen kann. Zwei Fragen: Wie sieht ein universelles Modell für Experimente aus? Und bringt es einen beweisbaren Vorteil, die Ausgaben eines Experiments kohärent weiterzuverarbeiten, statt jede einzeln zu messen?

### Kernresultate

* **Drei Register.** $N$ (*Nature*): die verborgenen Freiheitsgrade, auf die das Labor keinen direkten Zugriff hat, im Beispiel der Kristall. $L$ (*lab*): die zugänglichen Freiheitsgrade, die an $N$ koppeln, die Röntgenphotonen. $W$ (*work space*): Kamera und Rechner.
* **Lab-Orakel** $\mathrm{LO} = (\mathcal{E}_{NL}, \rho_N)$: ein unbekannter Kanal auf $N \otimes L$ zusammen mit dem Anfangszustand von $N$. Weil $N$ zwischen den Aufrufen erhalten bleibt, darf das System ein eigenes, unzugängliches Gedächtnis haben. Ohne $N$ wäre das Modell ein gewöhnlicher Black-Box-Algorithmus und nach Aussage der Autoren nicht allgemein genug.
* **Task** $(S_{\mathrm{in}}, S_{\mathrm{out}}, f, \mathcal{G})$: eine Funktion $f$ von Lab-Orakel und klassischen Einstellungen (etwa der Temperatur) auf einen klassischen Output oder eine Verteilung darüber, dazu die zulässigen Gatter $\mathcal{G}$ auf $L \otimes W$, die nie auf $N$ wirken.
* **QUALM:** eine Folge von Gattern aus $\mathcal{G}$ mit Platzhaltern $\square$, an denen das Orakel eingesetzt wird. Die **QUALM-Komplexität** ist Gatterzahl plus Anzahl der Aufrufe, wahlweise mit einem Gewicht $\lambda$ auf den Aufrufen. Aufrufe und Rechenzeit stehen damit in einer Zahl; die Breite von $W$ ist der Speicherparameter.
* **Universalitätshypothese:** Jedes physikalisch realisierbare Experiment lässt sich mit höchstens polynomiellem Overhead als QUALM simulieren, die Quanten-Church-Turing-These, übertragen von Berechnungen auf Experimente. Das ist eine Hypothese, kein Satz.
* **Kohärent und inkohärent** (Def. 11 und 13). Kohärent heißt: universelle Gatter auf $L \otimes W$, keine Einschränkung. Inkohärent heißt: zwischen $L$ und $W$ nur LOCC, und zwischen je zwei Aufrufen mindestens eine vollständige Messung von $L$ in einer Orthonormalbasis. Adaptivität ist in beiden Fällen erlaubt.
* **Theorem 1, Fixed-Unitary-Problem.** $\mathrm{LO}_0$ zieht einmal einen Haar-zufälligen Unitary auf $\ell$ Qubits und wendet ihn bei jedem Aufruf an. $\mathrm{LO}_1$ zieht bei jedem Aufruf einen neuen. Kohärent reichen zwei Aufrufe auf $\vert 0\rangle$ und ein SWAP-Test: Unter $\mathrm{LO}_0$ sind beide Outputs gleich und der Test akzeptiert immer, unter $\mathrm{LO}_1$ akzeptiert er im Mittel mit Wahrscheinlichkeit $\tfrac12 + \tfrac{1}{2D}$, $D = 2^\ell$. Jedes inkohärente QUALM, auch adaptiv, hat QUALM-Komplexität $\Omega(2^{2\ell/7})$.
* **Theorem 2, Symmetrieklasse.** Unterscheide einen festen Haar-zufälligen unitären, orthogonalen oder symplektischen Operator. Kohärent genügt ein verallgemeinerter SWAP-Test auf einem maximal verschränkten Zustand. Inkohärent gilt dieselbe Schranke, weil alle drei Orakel für inkohärente Protokolle von $\mathrm{LO}_1$ ununterscheidbar sind und damit auch voneinander.
* **Simon ist inkohärent.** Als QUALM gelesen greift Simons Algorithmus auf jede Probe einzeln zu, mit Produktzuständen und Messungen in einer Produktbasis. Sein Vorteil steckt in der Superpositions-Query, also im Orakel, nicht in Kohärenz über Aufrufe hinweg.
* **Abgrenzung.** Frühere Trennungen (Bacon, Childs, van Dam 2005; Huang, Kueng, Preskill 2021) zählen nur Aufrufe; dort braucht auch die kohärente Seite exponentiell viele Gatter. Hier ist die kohärente Seite in beiden Budgets effizient.

### Methodischer Ansatz

1. **Reduktion auf Simple-Measurement-QUALMs.** Zwischen zwei Aufrufen darf ein inkohärentes QUALM viele Runden klassischer Kommunikation zwischen $L$ und $W$ ausführen. Die Botschaften von $W$ an $L$ sind klassisch, also lässt sich $W$ durch einen klassischen Rechner mit Zufallsbits ersetzen. Bei festen Zufallsbits fallen alle schwachen Messungen zwischen zwei Aufrufen zu einem POVM mit Rang-1-Elementen zusammen. Jedes inkohärente QUALM ist damit eine Wahrscheinlichkeitsmischung aus Protokollen der Form präparieren, Orakel anwenden, messen, wiederholen, wobei Präparation und Messbasis von allen früheren Ergebnissen abhängen dürfen. Eine Mischung ist nie besser als ihr bestes Element.
2. **Weingarten-Kalkül.** Unter $\mathrm{LO}_1$ ist die Ergebnisverteilung eines solchen Protokolls ein einfaches Produkt, weil jeder Aufruf einen frischen Haar-Unitary sieht und jeder Output für sich maximal gemischt ist. Unter $\mathrm{LO}_0$ steht ein Haar-Integral über $U^{\otimes k} \otimes \bar U^{\otimes k}$, das die Weingarten-Funktionen $W(\tau\sigma^{-1}, D)$ als Summe über Paare von Permutationen $\sigma, \tau \in S_k$ ausdrücken.
3. **Das Adaptivitätsproblem.** Die Summe über die Ergebnisse lässt sich nicht einfach ausführen, weil spätere Präparationen und Basen von früheren Ergebnissen abhängen. Der Trick: jeden Permutationsterm in zwei Segmente zerlegen, $2\vert ab\vert \le \vert a\vert^2 + \vert b\vert^2$ anwenden und die Summe vom letzten Index $s_k$ rückwärts über die Vollständigkeitsrelation ausführen. Ergebnis: $\Vert P_k - Q_k\Vert_1 = O(k^3/2^\ell)$ im Gültigkeitsbereich der Weingarten-Abschätzung. Dieser Bereich, nicht der Term $k^3/2^\ell$, setzt den Exponenten $2/7$.

### Bedeutung und Anwendungen

* **Erster sauberer Beleg**, dass Kohärenz im Labor einen exponentiellen Ressourcenvorteil bringt, für Aufgaben mit physikalischer Motivation (Floquet-System gegen zufällige Zeitentwicklung, Symmetrieklasse einer Dynamik) und mit einem kohärenten Protokoll, das kaum mehr als ein SWAP-Test ist.
* **Vorläufer der Hardware-Demonstration.** Huang et al. (Science 2022, im Ordner als 2112.00778, mit Cotler als Koautor) zeigen solche Trennungen auf Sycamore. Die Speicher-Trennungen von Chen, Cotler, Huang, Li (2021) für Purity und Pauli-Shadow-Tomographie und von Chen, Zhou, Seif, Jiang (2022) für Pauli-Kanäle haben genau diese Form: kohärent mit kleinem Speicher gegen inkohärent.
* **Vokabular.** Das Modell trennt zwei Dinge, die in der Literatur oft beide „Zugriff“ heißen: welches Orakel die Natur liefert, und ob seine Outputs kohärent weiterverarbeitet werden. Der Anhang dieses Dokuments übernimmt diese Trennung (*Measurement power*, Tabelle der vier Kombinationen).

### Bezug zum eigenen Projekt

**Die Pipeline als QUALM.**
* Wie Phase 1 einzuordnen ist, hängt davon ab, welches Orakel man hinschreibt. Liefert die Natur pro Aufruf ein Paar $\rho \otimes \rho^*$, dann misst Phase 1 das Register $L$ sofort vollständig in der verallgemeinerten Bell-Basis, einer Orthonormalbasis von $L$: ein inkohärentes QUALM, sogar ein Simple-Measurement-QUALM. Liefert die Natur nur $\rho$ und stellt das Labor $\rho^*$ selbst her, etwa weil $\rho$ reell ist, dann muss die erste Kopie ungemessen warten, bis die zweite da ist: ein kohärentes QUALM mit einer Kopie Speicher. Dieselbe Messung, zwei Einordnungen. QUALM zwingt dazu, das Orakel explizit anzugeben, und genau das ist der Absatz *Access model*, den Jarrods Feedback eingefordert hat (Punkt A in research_objective.md).
* Phase 2 misst $\rho \otimes \sigma^*$ mit einer bekannten, vom Labor präparierten Probe. Weil $\sigma^*$ fest ist, ist das dasselbe wie ein POVM auf $\rho$ allein, mit den Elementen $\mathrm{Tr}_W[(\mathbb{1} \otimes \sigma^*)\,\Pi_u]$. Die adaptive Probe-Wahl ist damit eine adaptive Einzelkopien-Messung, und die Reduktion aus Schritt 1 der Methode ist die formale Fassung des Satzes im Quadranten, dass Adaptivität die Zeile nicht ändert.
* Die QUALM-Komplexität zählt Aufrufe und Gatter, die Breite von $W$ den Speicher. Triple Efficiency heißt Polynomialität in allen drei. Das CNN-Training steht außerhalb des Modells: Die trainierten Gewichte sind Teil der festen Gatterfolge, ein Ratschlag (*advice*), der nicht vom Orakel abhängt. Gezählt wird die Auswertung des CNN, und genau das meint „triple efficiency at inference only“.

**Bell-Messung und SWAP-Test.**
* Auf Qubits ist SWAP in der Bell-Basis diagonal. Das Singulett hat Eigenwert $-1$, die drei anderen Bell-Zustände $+1$, und transversal über $n$ Qubits hat das Bell-Ergebnis $P$ den SWAP-Eigenwert $(-1)^{\#Y(P)}$. Der SWAP-Test aus Theorem 1 ist also eine vergröberte Bell-Messung: Bell-Sample ziehen, Parität der $Y$-Faktoren ausgeben.
* Auf Qudits mit $d \ge 3$ gilt das nicht (numerisch geprüft für $d = 3, 4, 5$): $\mathrm{SWAP} = \tfrac1d\sum_v D_v \otimes D_v^\dagger$ ist in der Basis $(D_{q,p}\otimes\mathbb{1})\vert\Phi^+\rangle$ nicht diagonal. Diese Basis diagonalisiert stattdessen die $D_v \otimes \bar D_v$, und $\sum_v D_v \otimes \bar D_v = d^2\,\vert\Phi^+\rangle\langle\Phi^+\vert$ ist das $d$-fache der partiellen Transponierten von SWAP. Das passt zur Beobachtung von Allcock et al., dass Bell-Sampling auf zwei identischen Qudit-Kopien seine Qubit-Eigenschaften verliert.
* Was vom SWAP-Test übrig bleibt, ist eine Identität: Das Bell-Ergebnis $(0,0)$ hat auf $\rho \otimes \rho^*$ die Wahrscheinlichkeit $\mathrm{Tr}(\rho^2)/d$, in der Formel $P(a,b) = d^{-2}\sum_{q,p}\vert y_{q,p}\vert^2\omega^{ap-bq}$ der Term bei $(a,b) = (0,0)$. Auf zwei identischen Kopien steht dort $\mathrm{Tr}(\rho\rho^{T})/d$, und das ist für komplexes $\rho$ nicht die Reinheit (beides numerisch geprüft). Die statistische Effizienz des SWAP-Tests bleibt dabei nicht erhalten: Ein Ereignis der Wahrscheinlichkeit $O(1/d)$ als Reinheitsschätzer kostet $\Theta(d/\epsilon^2)$ Kopien. Für Phase 1 ist das unerheblich, denn dort zählen die $\vert y_v\vert^2$ einzeln, nicht ihre Summe.

**Searching und die LWE-Wand.**
* Beim Fixed-Unitary-Problem entscheidet Kohärenz alles. Beim Searching-Problem des Projekts entscheidet sie nichts, jedenfalls auf der harten Instanz aus `thm:lwe-displacement`. Der Zustand $\rho_s = \mathbb{E}\,\vert a,b\rangle\langle a,b\vert$ ist diagonal. Dephasieren in der Rechenbasis lässt $\rho_s^{\otimes k}$ unverändert, und jede dephasierte Kopie ist eine klassische LWE-Probe. Jedes kohärente QUALM auf Kopien von $\rho_s$, mit beliebig viel Quantenspeicher, lässt sich deshalb durch einen Quantenalgorithmus auf klassischen LWE-Proben simulieren, der die Basiszustände selbst neu präpariert. Die Post-Quanten-LWE-Annahme schließt einen solchen Algorithmus in Polynomialzeit aus.
* Die Härte sitzt also im Orakel, nicht in der Kohärenz. Leicht wird die Aufgabe erst mit einem anderen Orakel: Quanten-Proben in Superposition (Grilo, Kerenidis, Zijlstra 2019) oder dem Präparationsschaltkreis. Das ist die QUALM-Fassung der Aussage im Quadranten, dass die harte Zelle nur durch ein Versprechen oder durch Query-Zugriff verlassen wird.
* Für das Paper wäre das ein Satz Zusatz zu `thm:lwe-displacement`: Die Reduktion schließt nicht nur jede Verarbeitung der Bell-Outcomes aus, sondern jede kohärente Mehrkopien-Messung. Das entkräftet einen naheliegenden Einwand, nämlich dass ein Protokoll mit mehr Quantenspeicher die Wand umgehen könnte. Der Vorbehalt: Das Argument braucht Diagonalität. Für nicht-diagonale harte Instanzen, etwa in der zyklischen Einzel-Qudit-Basis (Q1), ist offen, ob Speicher hilft.

**Symmetrieklasse und Konjugat.** Theorem 2 fragt für Dynamiken, ob sie orthogonal sind, also reell und zeitumkehrsymmetrisch. In der Taxonomie der Einflussfaktoren (research_objective.md, Faktor A) ist Realität genau die Bedingung, unter der $\rho^* = \rho$ gilt und das Konjugat nichts kostet. Für Haar-zufällige Dynamik sagt das Theorem, dass sich diese Eigenschaft ohne Kohärenz nicht billig prüfen lässt. Bedingung (C1) ist deshalb eher Vorwissen aus der Physik (etwa ein reeller Hamiltonian ohne Magnetfeld) als etwas, das die Pipeline nebenbei verifiziert.

### Grenzen und offene Fragen

* **Spielzeugprobleme.** Haar-zufällige Unitaries sind selbst nicht effizient implementierbar, das Lab-Orakel ist also exponentiell komplex. Die Autoren fragen selbst nach Vorteilen mit effizienten Orakeln. Grund- und Gibbs-Zustände lokaler Hamiltonians, wie im Projekt, wären solche Orakel.
* **Rauschen.** Nach Aussage der Autoren verschwinden die exponentiellen Vorteile ihrer Beispiele unter Rauschen; ob sich QUALM-Vorteile in der NISQ-Ära zeigen lassen, ist offen.
* **Schärfe.** Der Exponent $2/7$ kommt aus dem Gültigkeitsbereich der Weingarten-Abschätzung; ob die Schranke scharf ist, lässt der Haupttext offen.
* **Adaptivität.** Ob Adaptivität im inkohärenten Fall allgemein hilft, listen die Autoren als offen; für ihre beiden Aufgaben ist die Schranke gegen adaptive Protokolle bewiesen.
* **Universalität** ist eine Hypothese, kein Satz.

### Fragen zum Tieferbohren

* Gilt die Diagonal-Reduktion auch in der zyklischen Einzel-Qudit-Basis? Konkreter: Gibt es dort eine nicht-diagonale harte Instanz, gegen die ein Protokoll mit drei oder mehr kohärent gehaltenen Kopien hilft? (Q1)
* Auf welcher Stufe der Instanzenleiter senkt mehr Speicher als das Paar zum ersten Mal die QUALM-Komplexität? Die Autoren fragen allgemein, wie viel ein größerer Arbeitsraum bringt; die offene Front *Memory between zero and two* ist dieselbe Frage von unten.
* Lässt sich Realität, Bedingung (C1), mit zwei identischen Kopien testen? Der SWAP-Test auf $\rho\otimes\rho$ liefert $\mathrm{Tr}(\rho^2)$, das Bell-Ergebnis $(0,0)$ auf $\rho\otimes\rho$ liefert $\mathrm{Tr}(\rho\rho^T)/d$, und die Differenz $\mathrm{Tr}(\rho^2)-\mathrm{Tr}(\rho\rho^T) = \tfrac12\Vert\rho-\rho^*\Vert_F^2$ verschwindet genau für reelles $\rho$. Der zweite Schätzer kostet aber $\Theta(d/\epsilon^2)$ Kopien. Gibt es einen effizienten Test, oder ist Theorem 2 ein Hinweis, dass es keinen gibt?
* Was steht in der Supplementary Information? Die formalen Definitionen, der vollständige Beweis und das Verifikationsbeispiel, das die Notwendigkeit von $N$ zeigt, liegen nicht im Ordner.

Paper: [arXiv:2101.04634](https://arxiv.org/abs/2101.04634) · [doi:10.1038/s41467-021-27922-0](https://doi.org/10.1038/s41467-021-27922-0)

---

## Certifying almost all quantum states with few single-qubit measurements (arXiv:2404.07281)

Die Arbeit von **Hsin-Yuan Huang, John Preskill und Mehdi Soleimanifar** (Caltech, Google Quantum AI; FOCS 2024) zertifiziert die Fidelity eines Laborzustands $\rho$ mit einem Zielzustand $\vert\psi\rangle$, der nur über ein Amplitudenmodell $\Psi(x)\propto\langle x\vert\psi\rangle$ zugänglich ist, aus Einzelqubit-Pauli-Messungen auf $O(\tau^2/\epsilon^2)$ Kopien; $\tau$ ist die Relaxationszeit einer Irrfahrt auf dem Hyperwürfel mit stationärer Verteilung $\vert\langle x\vert\psi\rangle\vert^2$. Für alle bis auf einen $2^{-\Omega(n)}$-Anteil der Zustände ist $\tau = O(n^2)$; Phasen- und GHZ-artige Zustände haben $\tau = O(n)$. Der Ersatzwert heißt *Shadow Overlap*.

### Einordnung in die Tabellen

* **Task type:** Identifying, $M = 1$ (Certification): Ausgabe "Certified" bei $\langle\psi\vert\rho\vert\psi\rangle\geq 1-\epsilon/(2\tau)$, "Failed" bei $< 1-\epsilon$; dazwischen keine Garantie. Die Lücke $\tau$ ist der Preis für Einzelqubit-Messungen.
* **Objekt:** gemischter $n$-Qubit-Zustand gegen ein reines, klassisch beschriebenes Ziel. **Zugriff:** Sample mit Einzelqubit-Messungen ($n-1$ Qubits in $Z$, ein zufälliges Qubit in zufälliger Pauli-Basis); Query an das Modell $\Psi$, zwei Abfragen pro Kopie.
* **Status:** 🟢 🟢 🟢 für $\tau = \mathrm{poly}(n)$: $T = O(\tau^2/\epsilon^2)$ Kopien mit Pauli-Messungen, $O(\tau/\epsilon)$ mit allgemeinen Einzelqubit-Messungen; $O(n^2/\epsilon)$ für fast alle Zustände (Theorem 2); Zeit $O(T)$ Modellabfragen; Speicher null.
* **Versprechen:** polynomielle Relaxationszeit des Ziels; kein Versprechen über $\rho$.

### Das Problem

Frühere Zertifizierungen brauchten tiefe Schaltkreise (Schatten, Spektrumschätzung), exponentiell viele Einzelqubit-Messungen (direkte Fidelity-Schätzung) oder spezielle Zielklassen (Stabilizer, MPS), oder hatten keine Garantie (Cross-Entropy-Benchmarking). Kann man die Fidelity mit einem generischen, hochverschränkten Ziel aus wenigen Einzelqubit-Messungen zertifizieren?

### Kernresultate

* **Protokoll 1.** Qubit $k$ zufällig; $Z$-Messung der übrigen ergibt $z$; Pauli-Messung von $k$ ergibt $\vert s\rangle$; Modellabfragen $\Psi(z^{(0)}), \Psi(z^{(1)})$ definieren $\vert\Psi_{k,z}\rangle$; lokaler Overlap $\omega = \langle\Psi_{k,z}\vert(3\vert s\rangle\langle s\vert - I)\vert\Psi_{k,z}\rangle$; Mittelwert $\hat\omega$ über $T$ Runden; zertifiziere bei $\hat\omega\geq 1 - 3\epsilon/(4\tau)$.
* **Gl. (1), (2).** $\mathbb{E}[\hat\omega]\geq 1-\epsilon\Rightarrow\langle\psi\vert\rho\vert\psi\rangle\geq 1-\tau\epsilon$ und $\langle\psi\vert\rho\vert\psi\rangle\geq 1-\epsilon\Rightarrow\mathbb{E}[\hat\omega]\geq 1-\epsilon$.
* **Theorem 1.** $T = O(\tau^2/\epsilon^2)$ Kopien; $O(\tau/\epsilon)$ mit allgemeinen Einzelqubit-Messungen.
* **Theorem 2.** Für alle bis auf $2^{-\Omega(n)}$ der Zustände ist $\tau\leq\tau^* = O(n^2)$, also $O(n^2/\epsilon)$ Kopien, auch für Zustände exponentieller Schaltkreiskomplexität.
* **Theoreme 4 bis 7, Anhänge D, G, H, I.** $\mathbb{E}[\omega] = \mathrm{Tr}(L\rho)$ mit $L\vert\psi\rangle = \vert\psi\rangle$ und $\langle\psi^\perp\vert L\vert\psi^\perp\rangle\leq 1-1/\tau$; $L$ hat dasselbe Spektrum wie die Übergangsmatrix $P$ der Irrfahrt (Gl. 8); Relaxationszeiten für Haar-Zustände über Mehrgüterflüsse mit "local escape property", für Phasenzustände und GHZ $O(n)$, für Grundzustände; Level-$m$-Varianten (Protokoll 2) mit $2^{2m}/\epsilon^2$ Kopien.

### Methodischer Ansatz

* Die Messung des Qubits $k$ in einer zufälligen Pauli-Basis ist ein Einzelqubit-Schatten; gemittelt ist $3\vert s\rangle\langle s\vert - I$ ein unverzerrter Schätzer der Ein-Qubit-Reduktion nach Konditionierung auf $z$, deshalb $\mathbb{E}[\omega] = 1$ für $\rho = \vert\psi\rangle\langle\psi\vert$.
* Das Modell wird nur für das bedingte Ein-Qubit-Verhältnis $\Psi(z^{(1)})/\Psi(z^{(0)})$ gebraucht; unnormierte Modelle (neuronale Netze, Tensor-Netze, Schaltkreise mit Amplitudenabfrage) genügen.
* Die Irrfahrt ist nur Analysewerkzeug; ihr Gap $1/\tau$ misst, wie stark $L$ vom Projektor abweicht.

### Bedeutung und Anwendungen

* Verifikation generischer Zustände mit dem billigsten Messprimitiv; zugleich ein Lernprimitiv: Ein Modell, das den Shadow Overlap maximiert, lernt den Zustand (Anwendungen auf neuronale und Tensor-Netz-Modelle im Paper).
* Der Nachweis, dass Zustände exponentieller Komplexität zertifizierbar sind, trennt Zertifizieren von Lernen deutlich.

### Bezug zum eigenen Projekt

* Der Shadow Overlap ist ein Zertifikat aus einer Ein-Qubit-Messung plus zwei Modellabfragen; für die eigene Pipeline ist die Frage, ob ein aus Bell-Sampling gelerntes sparsames Spektrum als Modell $\Psi$ dienen kann. Ein sparsames Displacement-Spektrum liefert Amplitudenverhältnisse in $O(k)$ Zeit, also wäre die Zertifizierung des Lernergebnisses billig.
* Die Relaxationszeit ist eine Instanzgröße, die von der Struktur des Ziels abhängt, nicht von seiner Komplexität; das ist ein Vorbild für eine Instanzenleiter, die nicht in $t$ oder $k$, sondern in Mischzeiten gemessen wird.
* Die Lücke zwischen "Certified" und "Failed" (Faktor $2\tau$) ist ein Toleranzparameter wie bei Bao et al.; beide zeigen, dass Ein-Bit-Aufgaben Toleranzlücken mit polynomiellem Faktor haben.

### Grenzen und offene Fragen

* Zustände mit exponentieller Relaxationszeit (etwa Superpositionen weit getrennter Basiszustände, wie $\vert 0^n\rangle + \vert 1^n\rangle$ ohne die Level-$m$-Variante) werden nicht abgedeckt; das Level-$m$-Protokoll kostet $2^{2m}$.
* Das Modell muss Amplituden in der Rechenbasis liefern; für Zustände, die nur als Schaltkreis vorliegen, ist die Abfrage selbst teuer.
* Die Lücke $\tau$ zwischen den beiden Schwellen ist inhärent, nicht nur eine Beweisartefakt.

### Fragen zum Tieferbohren

* Wie wird $L$ konstruiert, und warum hat es genau das Spektrum von $P$?
* Wie funktioniert die "local escape property" für Haar-Zustände, und warum reicht sie für $\tau = O(n^2)$?
* Kann Bell-Sampling auf $\rho\otimes\rho^*$ die Rolle der Einzelqubit-Messung übernehmen und die Lücke $\tau$ eliminieren, weil es den Overlap $\vert\mathrm{Tr}(\rho\sigma)\vert$ direkt sieht?

Paper: [arXiv:2404.07281](https://arxiv.org/abs/2404.07281)

---

## Non-Markovian quantum process tomography (arXiv:2106.11722)

Die Arbeit von **Gregory A. L. White, Felix A. Pollock, Lloyd C. L. Hollenberg, Kavan Modi und Charles D. Hill** (Melbourne, Monash; PRX Quantum 2022) formalisiert die Tomographie des *Prozess-Tensors*, der Verallgemeinerung der Prozess-Tomographie auf mehrzeitige Dynamik mit Gedächtnis. Sie baut eine Maximum-Likelihood-Rekonstruktion mit Positivitäts- und Kausalitätsprojektion, macht das Verfahren für Prozesse endlicher Markov-Ordnung $\ell$ effizient und zeigt auf IBM-Geräten, dass die Charakterisierung nicht-Markovscher Korrelationen die Fidelity mehrzeitiger Schaltkreise erhöht.

### Einordnung in die Tabellen

* **Task type:** Identifying gegen eine Klasse (Prozesse der Markov-Ordnung $\ell$), verwirklicht als Estimating aller Parameter des Prozess-Tensors; die Zeile steht bei Identifying, weil die Effizienz aus der Klassenwahl kommt und das Paper einen Test liefert, welche Ordnung nötig ist.
* **Objekt:** Prozess $\Upsilon_{k:0}$ über $k$ Zeitschritte auf einem Qubit, Choi-Zustand der Dimension $d^{2k+2}$. **Zugriff:** Query; Sequenzen von Kontrolloperationen aus einer überkompletten Basis ($N_{\mathrm{oc}} = 24$ pro Schritt) oder einer minimalen ($N_{\mathrm{mle}} = 10$), dann Messung.
* **Status:** 🟢 🟢 🟢 für festes $\ell$: $O(kN_{\mathrm{mle}}^\ell)$ Schaltkreise statt $O(N_{\mathrm{oc}}^k)$; ohne Gedächtnisschranke exponentiell in $k$, allgemein $O(d^{4k})$ Experimente.
* **Versprechen:** endliche Markov-Ordnung; die Verletzung ist selbst messbar (Trade-off Charakterisierungsaufwand gegen Genauigkeit).

### Das Problem

CPTP-Abbildungen beschreiben Zwei-Zeit-Fehler; reale Geräte zeigen zeitliche Korrelationen (die Wahl eines vergangenen Gatters beeinflusst das nächste), die die Summe der Gatterfehler unterschätzt und Fehlerkorrektur untergraben kann. Wie charakterisiert man einen Prozess mit Gedächtnis vollständig, statistisch robust und mit vertretbarem Aufwand?

### Kernresultate

* **Prozess-Tensor-Tomographie (Abschnitt II).** QST braucht $O(d^2)$, QPT $O(d^4)$, PTT $O(d^{4k})$ Experimente; lineare Inversion (LI-PTT) mit überkompletter Basis skaliert wie $O(N_{\mathrm{oc}}^k)$ Schaltkreise und ist empfindlich gegen Verstärkung kleiner Fehler in der Superoperatorbasis.
* **MLE-PTT (Abschnitt III).** Konvexe Log-Likelihood mit projiziertem Gradientenabstieg auf den Schnitt der Bedingungen vollständig positiv und kausal (Gl. 13, 15); die Projektion ist nichttrivial und wird gegenüber Dykstras alternierender Projektion verbessert. Reduktion auf $O(N_{\mathrm{mle}}^k)$ mit $N_{\mathrm{mle}} = 10$; Rekonstruktionsfidelity auf IBM-Hardware im Bereich $0.999$ (Abschnitt III, Abb. 5).
* **Markov-Ordnung (Abschnitt IV).** Adaptive Trunkierung schwacher Langzeitkorrelationen auf Ordnung $\ell$; Skalierung $O(kN_{\mathrm{mle}}^\ell)$; die Restabweichung quantifiziert, wie sehr ein Modell begrenzten Gedächtnisses die Vorhersage verfehlt.
* **Kontrolle (Abschnitt V).** Charakterisierung für $\ell\in\{1, 2, 3\}$ und Nutzung der Korrelationen als Ressource erhöht die Fidelity mehrzeitiger Schaltkreise; höhere Ordnung, bessere Vorhersage.

### Methodischer Ansatz

* Der Prozess-Tensor ist ein Choi-Zustand über $k+1$ Ein- und Ausgängen; kausale Bedingungen (die Zukunft beeinflusst die Vergangenheit nicht) sind affine Nebenbedingungen; unvollständige Basen ("restricted" Tensoren) sind für Vorhersagen innerhalb der Basis dennoch nützlich.
* Reconstruction Fidelity: Vergleich der Vorhersagen des rekonstruierten Tensors mit zufälligen Sequenzen, nicht mit einem Ground Truth, weil es keinen gibt.

### Bedeutung und Anwendungen

* Fehlende Kachel im Zoo der Charakterisierungsverfahren (QCVV); Grundlage für gedächtnisbewusste Kontrolle und Fehlerminderung, hardwareagnostisch.
* Für die Lerntheorie das erste Protokoll, das Query-Zugriff auf Prozesse mit Gedächtnis als Lernproblem mit expliziter Klassenannahme (Markov-Ordnung) formuliert.

### Bezug zum eigenen Projekt

* Die Markov-Ordnung ist eine Instanzenleiter für Prozesse: $\ell$ spielt die Rolle von $t$ bei Clifford+T oder $D$ bei MPS, und $O(kN^\ell)$ gegen $O(N^k)$ ist der Effizienzgewinn eines Klassenversprechens.
* Der Prozess-Tensor ist die Zeitachsen-Version eines Zustands auf $2k+2$ Registern; Bell-Sampling auf konjugierten Choi-Zuständen wäre das natürliche Zweikopien-Primitiv, um sein Displacement-Spektrum zu lernen, und die Kausalitätsbedingungen würden dort als Sparsity-Muster erscheinen.
* Die MLE-Projektion auf den physikalischen Kegel ist das, was ein CNN-Decoder implizit lernen müsste; das Paper liefert die expliziten Nebenbedingungen.

### Grenzen und offene Fragen

* Ein Qubit, kleine $k$; Skalierung bleibt exponentiell in der Systemgröße und in $k$ ohne Ordnungsschranke.
* Kontrollpulse müssen selbst hochfidel sein; SPAM-Fehler und Basisunvollständigkeit begrenzen die Rekonstruktion.
* Keine Sample-Komplexitätsgarantie im lerntheoretischen Sinn.

### Fragen zum Tieferbohren

* Wie genau wird die Projektion auf den Schnitt aus Positivität und Kausalität berechnet, und wie skaliert sie?
* Wie wird die Markov-Ordnung adaptiv gewählt, und gibt es ein Kriterium analog zur Singulärwertschwelle $\eta$ bei Fanizza et al.?
* Lässt sich ein Prozess-Tensor endlicher Ordnung als endlich korrelierter Zustand in Zeitrichtung lesen, sodass die spektrale Rekonstruktion anwendbar ist?

Paper: [arXiv:2106.11722](https://arxiv.org/abs/2106.11722)

---

## Pseudorandom quantum states (arXiv:1711.00385)

Die Arbeit von **Zhengfeng Ji, Yi-Kai Liu und Fang Song** (UTS Sydney, NIST/Maryland, Portland State; CRYPTO 2018) definiert pseudozufällige Quantenzustände (PRS): Familien $\{\vert\phi_k\rangle\}_{k\in\mathcal{K}}$, effizient präparierbar, sodass polynomiell viele Kopien für jeden polynomiellen Quantenalgorithmus von ebenso vielen Kopien eines Haar-zufälligen Zustands ununterscheidbar sind. Die Konstruktion sind zufällige Phasenzustände $\vert\phi_k\rangle = N^{-1/2}\sum_x\omega_N^{\mathrm{PRF}_k(x)}\vert x\rangle$ aus quantensicheren Pseudozufallsfunktionen; Anwendungen sind ein kryptographischer Nichtklonierungssatz und Quantengeld mit privatem Schlüssel.

### Einordnung in die Tabellen

* **Task type:** Identifying, Ein-Bit (PRS oder Haar), und damit die Härtequelle für Identifying gegen große Klassen: Wer eine Klasse lernen kann, die PRS enthält, kann sie von Haar unterscheiden. Die Zeile ist die kryptographische Referenz der Identifying-Tabelle.
* **Objekt:** Zustandsfamilie. **Zugriff:** Sample, polynomiell viele Kopien desselben $\vert\phi_k\rangle$; in der starken Variante (Theorem 4) zusätzlich Query an das Reflexionsorakel $I - 2\vert\phi_k\rangle\langle\phi_k\vert$, ohne Gewinn.
* **Status:** 🟢 🔴 🟢: Statistisch sind die Zustände mit $O(n^d)$ Kopien lernbar (Phasenzustände, siehe Arunachalam et al.), aber kein polynomieller Unterscheider existiert; der Schlüssel ist polynomiell.
* **Versprechen:** Existenz quantensicherer Einwegfunktionen (äquivalent: QPRF, QPRP).

### Das Problem

Klassische Pseudozufallsstrings sind für Quantenzustände zu schwach: Eine Familie zufälliger Basiszustände sieht in einer Kopie wie $I/2^n$ aus, ist aber trivial. Die richtige Definition muss viele Kopien zulassen. Was ist eine Familie, die auch mit polynomiell vielen Kopien Haar-zufällig aussieht, und was folgt daraus?

### Kernresultate

* **Definition 2 (PRS).** Effiziente Erzeugung $G(k) = \vert\phi_k\rangle$ und $\vert\Pr_k[A(\vert\phi_k\rangle^{\otimes m}) = 1] - \Pr_{\psi\sim\mu}[A(\vert\psi\rangle^{\otimes m}) = 1]\vert = \mathrm{negl}(\kappa)$ für alle effizienten $A$ und $m = \mathrm{poly}(\kappa)$.
* **Theorem 1.** Für jede QPRF ist die Familie der zufälligen Phasenzustände (Gl. 6) eine PRS; Präparation mit einer Abfrage der PRF (Hadamard, QFT auf $\vert 1\rangle$, Subtraktion im zweiten Register).
* **Lemma 2.** Für wahrhaft zufälliges $f$ ist $\vert f\rangle^{\otimes m}$ statistisch von Haar$^{\otimes m}$ ununterscheidbar; Beweis über die explizite Berechnung von $\rho^m = \mathbb{E}_f[\vert f\rangle\langle f\vert^{\otimes m}]$ in der Basis des symmetrischen Unterraums (Gl. 4, 5).
* **Theorem 3 (Nichtklonieren).** Für jede PRS und $m < m'$ ist die Erfolgswahrscheinlichkeit, aus $m$ Kopien $m'$ zu erzeugen, vernachlässigbar; Beweis: ein Kloner plus SWAP-Test wäre ein Unterscheider.
* **Theorem 4, 5.** Stark pseudozufällig (mit Reflexionsorakel) genau dann, wenn pseudozufällig; Orakelzugriff mit $q$ Abfragen lässt sich durch $O(q)$ Kopien simulieren.
* **Theorem 7.** Das Quantengeldschema aus PRS ist sicher.

### Methodischer Ansatz

* Drei Hybride: PRF-Phasen, wahrhaft zufällige Phasen, Haar; der erste Übergang ist die PRF-Sicherheit, der zweite Lemma 2 mit Momentenrechnung im symmetrischen Unterraum.
* Der Kern ist, dass die $m$-ten Momente zufälliger Phasenzustände die Haar-Momente bis auf $O(m^2/N)$ approximieren; das ist eine $m$-Design-Aussage über Phasenzustände.

### Bedeutung und Anwendungen

* Gründungsarbeit der Quantenpseudozufälligkeit; Brakerski–Shmueli (binäre Phasen), Kretschmer (Lernhärte aus PRS), Zhao et al. (Gatterkomplexität), Mele–Herasymenko (Fermionen) und Aaronson et al. (Pseudoverschränkung) bauen darauf auf.
* Nichtklonieren und Quantengeld ohne Verifizierung durch den Emittenten; PRS sind die minimale Annahme für vieles, was zuvor Einwegfunktionen brauchte.

### Bezug zum eigenen Projekt

* PRS sind das Beispiel für Zustände, die informationstheoretisch trivial und rechnerisch undurchdringlich sind; die eigene LWE-Instanz ist die Displacement-Version: ein Spektrum, dessen Träger sparsam ist, aber nur mit dem Schlüssel gefunden wird. Beide zeigen, dass die Lernhärte im Decoder sitzt.
* Zufällige Phasenzustände haben ein flaches Displacement-Spektrum (Betrag $\approx 2^{-n}$ auf allen Adressen); Bell-Sampling auf $\rho\otimes\rho^*$ zieht daraus nahezu gleichverteilt. Das ist der Grund, warum die Instanzenleiter bei Phasenzuständen hohen Grades endet: Es gibt keinen Träger zu finden.
* Theorem 5 (Orakelzugriff bringt nichts gegenüber Kopien) ist eine Aussage über die Zugriffsleiter: Für PRS ist Query = Sample.

### Grenzen und offene Fragen

* Sicherheit ist bedingt (QPRF); keine unbedingten Trennungen.
* PRS mit $\omega_N$-Phasen; die binäre Vereinfachung kam mit Brakerski–Shmueli.
* Pseudozufällige Unitaries (PRU) werden vorgeschlagen, aber nicht konstruiert.

### Fragen zum Tieferbohren

* Wie sieht die Momentenrechnung in Lemma 2 konkret aus, und ist die Fehlerschranke $O(m^2/N)$ scharf?
* Wie übersetzt sich Theorem 5 (Reflexionsorakel durch Kopien simulierbar) in die Sprache der Zugriffsleiter, und gilt es für nichtreflexive Orakel?
* Was ist die minimale Struktur (Grad des Phasenpolynoms), ab der Phasenzustände pseudozufällig werden, verglichen mit $\Theta(n^d)$ Kopien für Grad $d$?

Paper: [arXiv:1711.00385](https://arxiv.org/abs/1711.00385)

---

## Quantum pseudoentanglement (arXiv:2211.00747)

Die Arbeit von **Scott Aaronson, Adam Bouland, Bill Fefferman, Soumik Ghosh, Umesh Vazirani, Chenyi Zhang und Zixin Zhou** (UT Austin, Stanford, Chicago, Berkeley; ITCS 2024) konstruiert pseudozufällige Zustände mit Verschränkungsentropie $\Theta(f(n))$ über jeden Schnitt gleichzeitig, für jedes $f(n) = \omega(\log n)$, aus quantensicheren Einwegfunktionen. Daraus folgt ein pseudoverschränktes Ensemblepaar mit Lücke $\Theta(n)$ gegen $\omega(\log n)$, ununterscheidbar in Polynomialzeit; Anwendungen sind untere Schranken für MPS-Testen ($\Omega(\sqrt r)$), Schmidt-Rang-Schätzung und Verschränkungsdestillation sowie Folgerungen für AdS/CFT.

### Einordnung in die Tabellen

* **Task type:** Identifying, Ein-Bit: hohe oder niedrige Verschränkung, MPS mit Bonddimension $r$ oder weit davon. Die Aussage ist eine Härte: Der Test ist statistisch möglich, rechnerisch nicht.
* **Objekt:** Zustandsfamilien $\vert\Psi_k\rangle$, $\vert\Phi_k\rangle$ mit Schlüssel $k$. **Zugriff:** Sample, polynomiell viele Kopien.
* **Status:** 🟢 🔴 🟢; für MPS-Testen zusätzlich informationstheoretisch $\Omega(\sqrt r)$ Kopien (Theorem 3.5), also 🔴 in den Kopien bei exponentiellem $r$.
* **Versprechen:** quantensichere Einwegfunktion; die Konstruktion ist in logarithmischer Tiefe realisierbar.

### Das Problem

Ji–Liu–Song zeigen, dass PRS Verschränkung $\omega(\log n)$ über jeden Schnitt haben müssen; Gheorghiu–Hoban erreichen mit LWE eine Lücke $n$ gegen $n-k$ für konstantes $k$. Ist die maximale Lücke $\Theta(n)$ gegen $\omega(\log n)$ erreichbar, über alle Schnitte gleichzeitig, aus beliebigen Einwegfunktionen, und mit Haar-Ununterscheidbarkeit?

### Kernresultate

* **Definition (PES).** Zwei effizient präparierbare Ensembles mit Entropie $\Theta(f(n))$ bzw. $\Theta(g(n))$ über jeden Schnitt (mit Wahrscheinlichkeit $1 - 1/\mathrm{poly}$) und Ununterscheidbarkeit auf $p(n)$ Kopien.
* **Konstruktion (Abschnitt 2.1 bis 2.3).** Subset-Phasenzustände $\vert\psi_{f,p}\rangle = 2^{-k/2}\sum_{x\in\{0,1\}^k}(-1)^{f(p(x0^{n-k}))}\vert p(x0^{n-k})\rangle$ mit QPRP $p$ und QPRF $f$; Präparation: $H^{\otimes k}$, $p$, Uncompute, Phasenorakel.
* **Theorem 2.1.** Für $t < K\leq 2^n$ ist der Spurabstand zwischen $t$ Kopien eines zufälligen Subset-Phasenzustands mit $\vert S\vert = K$ und $t$ Kopien eines Haar-Zustands $O(t^2/K)$; also pseudozufällig, sobald $K = 2^{\omega(\log n)}$.
* **Theorem 2.7 / Korollare 2.6.1, 2.6.2.** Für $\omega(\log n)\leq k\leq n$ und $\vert S\vert = 2^k$ ist die Verschränkungsentropie über jeden Schnitt $(X, Y)$ mit $\vert X\vert, \vert Y\vert\geq k$ gleich $\Theta(k)$; obere Schranke aus dem Schmidt-Rang, untere über 4-fach unabhängige Phasenfunktionen (Theorem B.7).
* **Theorem 1 / Korollar 1.0.1.** PRS mit Entropie $\Theta(f(n))$ für jedes $f = \omega(\log n)$; PES mit Lücke $\Theta(n)$ gegen $\omega(\log n)$.
* **Theorem 3.5 (MPS-Testen).** Für $r\leq 2^{n/8}$ braucht ein MPS$(r)$-Tester $\Omega(\sqrt r)$ Kopien, informationstheoretisch wie rechnerisch; unvergleichbar mit Soleimanifar–Wright ($\Omega(\sqrt n)$), stärker bei großem $r$.

### Methodischer Ansatz

* Die Verschränkung eines Subset-Zustands ist durch $\log\vert S\vert$ beschränkt; Pseudozufälligkeit verlangt nur $\vert S\vert$ superpolynomiell. Die Trennung zwischen "Haar-Momente" ($t$-Design-Eigenschaft bis $t\ll\sqrt K$) und "Entropie" ($\log K$) ist der ganze Mechanismus.
* Die frühere Version (QIP 2023) reduzierte Verschränkung nur über einen Schnitt; die neue Konstruktion ist einfacher und stärker.

### Bedeutung und Anwendungen

* Verschränkung ist keine effizient beobachtbare Größe: Zwei Ensembles mit linear verschiedener Entropie sind ununterscheidbar. Für Property Testing (Schmidt-Rang, MPS), für Destillationsprotokolle über die Schur-Transformation und für die Berechenbarkeit holographischer Dualitäten.
* Grundlage für Pseudomagie (Gu, Leone, Ghosh, Eisert, Yelin, Quek 2023) und die Sample-Untergrenzen bei Chen–Gong–Ye–Zhang.

### Bezug zum eigenen Projekt

* Subset-Phasenzustände haben ein Displacement-Spektrum, das über die Größe $K$ des Trägers im Ortsraum gesteuert wird; für $K = 2^{\mathrm{polylog}}$ ist das Spektrum flach genug für Pseudozufälligkeit, aber der Zustand hat nur polylogarithmische Verschränkung. Das ist eine Instanz, bei der Sparsity im Ortsraum (Regime 1 in einer anderen Basis) rechnerisch unsichtbar bleibt: eine Warnung, dass Sparsity ohne Schlüssel keine Lernbarkeit garantiert.
* Die $\Omega(\sqrt r)$-Schranke für MPS-Testen ist eine Sample-Schranke gegen ein Klassenversprechen; sie sagt, dass die Bonddimension als Instanzparameter in die Kopienzahl eingeht, nicht nur in die Zeit.
* Pseudoverschränkung ist die Form von Härte, die kein Speicher aufhebt: Auch $\rho\otimes\rho^*$ sieht nur Haar-Momente.

### Grenzen und offene Fragen

* Die Konstruktion ist ein Ensemble, kein einzelner Zustand; Aussagen über "typische" physikalische Zustände folgen nicht.
* Die Lücke gilt für Entropie; ob dieselbe Ununterscheidbarkeit für andere Verschränkungsmaße (Negativität, Rényi-$\alpha$) gilt, wird teilweise behandelt.
* Bedingt auf Einwegfunktionen.

### Fragen zum Tieferbohren

* Wie geht die 4-fache Unabhängigkeit der Phasenfunktion in die untere Entropieschranke ein (Theorem B.7)?
* Wie sieht der Beweis von Theorem 2.1 mit der Bedingung $t < K$ aus, und was passiert bei $t\approx\sqrt K$?
* Ist das Displacement-Spektrum eines Subset-Phasenzustands mit $K = 2^k$ bis auf Faktor $2^{-k}$ flach, und was sieht Bell-Sampling auf $\rho\otimes\rho^*$ dann tatsächlich?

Paper: [arXiv:2211.00747](https://arxiv.org/abs/2211.00747)

---

## Learning quantum states and unitaries of bounded gate complexity (arXiv:2310.19882)

Die Arbeit von **Haimeng Zhao, Laura Lewis, Ishaan Kannan, Yihui Quek, Hsin-Yuan Huang und Matthias C. Caro** (Caltech, Tsinghua, Google Quantum AI, Harvard, MIT, FU Berlin; PRX Quantum 2024) bestimmt die Kosten des Lernens von Zuständen $U\vert 0^n\rangle$ und Unitaries $U$ aus $G$ Zwei-Qubit-Gattern: $\tilde\Theta(G/\epsilon^2)$ Kopien für Zustände, unabhängig von $n$; $\tilde O(G\min\{1/\epsilon^2, \sqrt{2^n}/\epsilon\})$ und $\Omega(G/\epsilon)$ Queries für Unitaries im Mittel über Inputs; $\Omega(2^{\min\{G/2C, n/2\}}/\epsilon)$ im Worst Case. Unter der Annahme, dass RingLWE quantenmechanisch nicht subexponentiell lösbar ist, braucht jeder Lerner Zeit $\exp(\Omega(\min\{G, n\}))$; $G = O(\log n)$ ist der Übergang zur Effizienz.

### Einordnung in die Tabellen

* **Task type:** Identifying gegen eine Klasse mit Versprechen (Gatterzahl $G$); die Klasse ist exponentiell groß und parametrisiert, also der Punkt, an dem Identifying in Searching übergeht. Die Sample-Schranke ist informationstheoretisch, die Zeitschranke kryptographisch: die These dieses Dokuments in einem Satz.
* **Objekt:** reiner Zustand oder Unitary. **Zugriff:** Sample (Kopien, Einzelkopien-Messungen genügen); Query an $U$, auch $U^\dagger$ und kontrolliertes $U$ in den unteren Schranken; klassisch beschriebene Input–Output-Paare (Theorem 5).
* **Status:** 🟢 🔴 🟢. Kopien $\tilde\Theta(G/\epsilon^2)$, Zeit exponentiell in $\min\{G, n\}$, Speicher polynomiell (ein Schaltkreis mit $G$ Gattern).
* **Versprechen:** Gatterzahl $G$; für $G = O(\log n)$ polynomielle Zeit über Junta-Lernen.

### Das Problem

Volle Tomographie kostet $\Theta(4^n/\epsilon^2)$; physikalische Zustände entstehen aus wenigen Gattern. Wie skalieren Kopien, Queries und Zeit mit $G$, und wo liegt die Effizienzgrenze? Und warum widersprechen Quantum-No-Free-Lunch-Sätze ($\Omega(2^n)$ Samples für generische Unitaries) nicht der linearen Schranke in $G$?

### Kernresultate

* **Theorem 1 (Zustände).** $N = \tilde\Theta(G/\epsilon^2)$ Kopien notwendig und hinreichend für Spurabstand $\epsilon$; obere Schranke über ein Überdeckungsnetz der $G$-Gatter-Zustände plus Quantum Hypothesis Selection, untere über ein Packungsnetz. Verbessert $\tilde O(nG^2/\epsilon^4)$ von Huang et al.
* **Theorem 2 (Zeit, Zustände).** Unter RingLWE-Subexponentialhärte braucht jeder Lerner für $\tilde O(G)$-Gatter-Zustände Zeit $\exp(\Omega(\min\{G, n\}))$; für $G = O(\log n)$ polynomiell.
* **Theorem 3 (Unitaries, Worst Case).** Diamantabstand: $\Omega(2^{\min\{G/2C, n/2\}}/\epsilon)$ Queries notwendig, $\tilde O(2^nG/\epsilon)$ hinreichend; Beweis über die Adversary-Methode.
* **Theorem 4 (Unitaries, Average Case).** Root-mean-square-Spurabstand über Haar-Inputs, äquivalent über jedes lokal verwürfelte Ensemble: $\tilde O(G\min\{1/\epsilon^2, \sqrt{2^n}/\epsilon\})$ Queries mit maximal verschränkten Inputs und Choi–Jamiołkowski, $\Omega(G/\epsilon)$ notwendig; ohne Hilfssysteme $\tilde O(G\min\{1/\epsilon^4, (\sqrt{2^n})^3/\epsilon\})$.
* **Theorem 5 (klassische Beschreibungen).** $O(2^n/r)$ Input–Output-Paare mit Inputs vom Rang $r$ genügen und sind nötig; das löst den scheinbaren Widerspruch zum No-Free-Lunch-Satz auf.
* **Theorem 6 (Zeit, Unitaries).** Dieselbe Härte $\exp(\Omega(\min\{G, n\}))$; damit gibt es keinen polynomiellen Lerner für Clifford+T-Schaltkreise mit $\tilde\omega(\log n)$ T-Gattern, was die fünfte Frage des Anshu–Arunachalam-Surveys verneint.
* **Theorem 7 (physikalische Funktionen).** Zum Approximieren beliebiger 1-beschränkter 1-Lipschitz-Funktionen auf $[0,1]^\nu$ braucht ein parametrisierter Schaltkreis $G\geq\tilde\Omega(\epsilon^{-\nu/2})$ Gatter und $\Omega(\epsilon^{-\nu})$ Samples; Quantenneuronale Netze umgehen den Fluch der Dimension nicht.

### Methodischer Ansatz

* Überdeckungsnetze über die Gatterparameter, Hypothesenauswahl (Bădescu–O'Donnell) für die optimale $\epsilon$-Rate; Packungsnetze für die untere Schranke.
* Härte durch PRS-Konstruktionen mit $\tilde O(G)$ Gattern, die ununterscheidbar von Haar sind: Ein effizienter Lerner wäre ein Unterscheider.
* Numerik mit flachen Clifford-Schatten bis $n = 10^4$ Qubits bestätigt die Linearität in $G$ und die Unabhängigkeit von $n$.

### Bedeutung und Anwendungen

* Eine feinkörnige Sicht auf Tomographie: Nicht die Dimension, sondern die Schaltkreiskomplexität zählt für die Kopien; die Zeit folgt einer anderen Logik.
* Die Grenze $\log n$ ist scharf für Zustände und Unitaries gleichermaßen und stimmt mit der Grenze der Clifford+T-Lerner überein.

### Bezug zum eigenen Projekt

* Die Zeile ist die formale Fassung der These "Sample-leicht, Zeit-hart": Jede Aussage der eigenen Arbeit über die LWE-Instanz muss sich an $\exp(\Omega(\min\{G, n\}))$ messen lassen. Die Displacement-Instanz hat $G = \mathrm{poly}(n)$; sie liegt also im harten Regime dieses Theorems, und die Frage ist nur, ob die zusätzliche Sparsity-Struktur das ändert.
* Theorem 5 ist die Zugriffsleiter für Prozesse: Rang $r$ der Inputs kauft einen Faktor $r$ in den Samples; das ist das Prozess-Gegenstück zur Speicherachse bei Zuständen.
* Die Sample-Schranke $\tilde\Theta(G/\epsilon^2)$ mit Einzelkopien-Messungen sagt, dass für reine Zustände kein Zweikopien-Vorteil in der Kopienzahl existiert; der Vorteil des eigenen Protokolls muss in der Zeit oder bei gemischten Zuständen liegen.

### Grenzen und offene Fragen

* Reine Zustände und Unitaries; gemischte Zustände und Kanäle brauchen andere Methoden, und dort könnten Zweikopien-Protokolle einen Kopienvorteil haben.
* Worst-Case-Härte; ob typische $G$-Gatter-Zustände hart sind, ist offen (Average-Case).
* Constant-depth mit verteilten Gattern ist effizient lernbar (Huang et al.), obwohl $G = \Theta(n)$; die Gatterzahl ist also nicht der einzige Parameter.

### Fragen zum Tieferbohren

* Wie geht die Lokal-Verwürfelungs-Äquivalenz (Theorem in [71]) in Theorem 4 ein, und gilt sie für Displacement-verwürfelte Ensembles?
* Wie wird die Adversary-Methode für Theorem 3 aufgesetzt, und wo entsteht $\min\{G/2C, n/2\}$?
* Welche PRS-Konstruktion mit $\tilde O(G)$ Gattern wird benutzt, und ist ihre Displacement-Struktur analysierbar?

Paper: [arXiv:2310.19882](https://arxiv.org/abs/2310.19882)

---

## A single T-gate makes distribution learning hard (arXiv:2207.03140)

Die Arbeit von **Marcel Hinsche, Marios Ioannou, Alexander Nietner, Jonas Haferkamp, Yihui Quek, Dominik Hangleiter, Jean-Pierre Seifert, Jens Eisert und Ryan Sweke** (FU Berlin, Maryland, TU Berlin; PRL 2023) charakterisiert die Lernbarkeit der Output-Verteilungen $P_U(x) = \vert\langle x\vert U\vert 0^n\rangle\vert^2$ lokaler Schaltkreise aus klassischen Samples. Clifford-Verteilungen sind in jeder Tiefe effizient lernbar; ein einziges $T$-Gatter macht das Lernen eines Evaluators unter LPN hart; Generatoren sind unter PRF-Annahmen ab Tiefe $n^{\Omega(1)}$ hart; und im Statistical-Query-Modell beginnt die Härte bei Tiefe $\omega(\log n)$.

### Einordnung in die Tabellen

* **Task type:** Identifying gegen eine Klasse mit Versprechen (Verteilungen einer Schaltkreisklasse); Ausgabe ist ein Generator oder ein Evaluator. Die Härte ist kryptographisch wie bei den LWE-Zeilen, aber auf der klassischen Seite der Messung.
* **Objekt:** klassische Verteilung über $\{0,1\}^n$. **Zugriff:** Sample, klassische Bitstrings; im SQ-Modell nur Erwartungswerte bis auf $\tau = \Omega(1/\mathrm{poly})$.
* **Status:** Clifford 🟢 🟢 🟢 mit $O(n)$ Samples und Gauß-Elimination; Clifford+$T$ 🟢 🔴 🟢 (Samples polynomiell, Zeit LPN-hart); allgemein 🟢 🔴 🟢 ab Tiefe $n^{\Omega(1)}$ (Generator) und $\omega(\log n)$ (SQ).
* **Versprechen:** Gatterset und Tiefe; nächste-Nachbar-Gatter in 1D.

### Das Problem

Quantum Circuit Born Machines (QCBM) sollen Verteilungen lernen, die klassisch schwer zu sampeln sind; die Hoffnung war ein beweisbarer Vorteil bei natürlichen Verteilungen. Simulierbarkeit und Lernbarkeit fallen bei Clifford zusammen; gilt das auch bei "leicht nicht-Clifford"?

### Kernresultate

* **Theorem 1.** $\mathcal{D}_{\mathrm{Cl}}$ ist für jede Tiefe effizient lernbar (Generator und Evaluator): Clifford-Verteilungen sind uniform auf affinen Unterräumen von $\mathbb{F}_2^n$, und $O(n)$ Samples plus Gauß-Elimination finden den Unterraum mit Fehler $e^{-\Omega(n)}$.
* **Theorem 2.** Unter LPN sind die Output-Verteilungen lokaler Clifford-Schaltkreise der Tiefe $n^{\Omega(1)}$ mit einem einzigen $T$-Gatter nicht effizient evaluator-lernbar; bei beliebiger Konnektivität schon in Tiefe $\Omega(1)$. Das LPN-Rauschen wird durch ein $T$-Gatter realisiert (Abb. 2); dasselbe gilt für Clifford mit Depolarisierung.
* **Korollar 1.** Dieselbe Härte für alle lokalen Schaltkreise der Tiefe $n^{\Omega(1)}$.
* **Theorem 3.** Unter klassisch- bzw. standard-sicheren PRF gibt es keinen effizienten klassischen bzw. Quantenalgorithmus für Generator-Lernen bei Tiefe $n^{\Omega(1)}$ und beliebigem universellen Gatterset; QCBM-Lerner eingeschlossen.
* **Theorem 4 (SQ).** Keine query-effiziente SQ-Lernbarkeit für $\mathcal{D}_{\mathrm{Cl}}$ ab Tiefe $\omega(\log n)$ und für $\mathcal{D}_{\mathcal{G}}$ ab Tiefe $\omega(\log^k n)$, Generator wie Evaluator; Paritäten sind SQ-hart, lineare Clifford-Tiefe realisiert sie, Reskalierung tauscht Tiefe gegen Komplexität.

### Methodischer Ansatz

* Alle Härten sind Einbettungen klassischer harter Verteilungen (Paritäten mit Rauschen, PRF-Outputs) in Schaltkreise; die Schaltkreisstruktur bestimmt nur, welche Tiefe nötig ist.
* Der scharfe Übergang bei einem $T$-Gatter kontrastiert mit der glatten Simulationskomplexität (exponentiell in der $T$-Zahl); Lernen und Simulieren trennen sich hier.

### Bedeutung und Anwendungen

* Output-Verteilungen lokaler Schaltkreise können keinen praktischen Lernvorteil von QCBMs gegenüber klassischen Lernern begründen; neue Strategien für Quantenvorteile im Lernen sind nötig.
* Das SQ-Resultat trifft alle gradientenbasierten Trainer.

### Bezug zum eigenen Projekt

* Die Klasse ist die klassische Randverteilung der Zustände, deren Displacement-Spektren die eigene Arbeit lernt; die Härte mit einem $T$-Gatter zeigt, dass schon minimale Magic auf der Verteilungsseite eine Wand baut, während auf der Zustandsseite $t = O(\log n)$ noch lernbar ist. Bell-Sampling sieht mehr als die Rechenbasis-Verteilung; das ist der quantitative Grund, warum Zweikopien-Zugriff die Instanzenleiter verlängert.
* LPN ist das $\mathbb{F}_2$-Gegenstück zu LWE; die Konstruktion "Rauschen durch ein Gatter" ist ein Rezept, harte Displacement-Instanzen aus einem Clifford-Gerüst plus einem einzigen nicht-Clifford-Element zu bauen.
* Das SQ-Modell ist die Sprache für CNN-Decoder, die nur Statistiken sehen; Theorem 4 sagt, ab welcher Tiefe solche Decoder scheitern müssen.

### Grenzen und offene Fragen

* Evaluator-Härte braucht LPN, Generator-Härte PRF; unbedingte Aussagen nur im SQ-Modell.
* Tiefe $O(\log n)$ bis $n^{\Omega(1)}$ ohne SQ-Einschränkung ist offen; die Autoren nennen Sample-Komplexität und Average-Case als nächste Fragen (Nietner et al. beantworten letztere).
* Nur Rechenbasis-Verteilungen und feste Inputs.

### Fragen zum Tieferbohren

* Wie genau realisiert ein einzelnes $T$-Gatter mit $H$-Konjugation Bernoulli-Rauschen mit konstanter Rate, und lässt sich die Rate steuern?
* Welche Reskalierung tauscht Tiefe gegen Komplexität, und warum ist sie auf $n^{\Omega(1)}$ begrenzt?
* Was sehen Bell-Samples auf $\rho\otimes\rho^*$ für den Zustand aus Abb. 2, und ist der Träger dort trotz LPN sparsam und findbar?

Paper: [arXiv:2207.03140](https://arxiv.org/abs/2207.03140)

---

## On the average-case complexity of learning output distributions of quantum circuits (arXiv:2305.05765)

Die Arbeit von **Alexander Nietner, Marios Ioannou, Ryan Sweke, Richard Kueng, Jens Eisert, Marcel Hinsche und Jonas Haferkamp** (FU Berlin, Linz, Berkeley; Quantum 2025) verlegt die Härte des Verteilungslernens vom Worst Case in den Average Case: Für zufällige Brickwork-Schaltkreise der Tiefe $d$ ist das Lernen eines $\epsilon$-nahen Generators aus Statistical Queries ab $d = \Omega(\log n)$ hart mit konstanter Wahrscheinlichkeit über die Instanz ($2^{\Omega(d)}$ Queries), bei linearer Tiefe mit Wahrscheinlichkeit $1 - O(2^{-n})$ ($\Omega(2^n)$ Queries), bei unendlicher Tiefe mit Wahrscheinlichkeit $1 - 2^{-2^{\Omega(n)}}$ ($2^{2^{\Omega(n)}}$ Queries). Nebenprodukt: Die Output-Verteilung eines zufälligen Schaltkreises ist mit Wahrscheinlichkeit $1 - O(2^{-n})$ konstant weit von jeder festen Verteilung, eine Variante der Vermutung von Aaronson und Chen.

### Einordnung in die Tabellen

* **Task type:** Identifying gegen eine Klasse, im Average Case über die Klasse und mit Erfolgswahrscheinlichkeit $\beta$ über die Instanz; das ist genau die offene Frage (4) der Identifying-Tabelle, für Verteilungen beantwortet.
* **Objekt:** klassische Verteilung eines zufälligen Brickwork-Schaltkreises. **Zugriff:** Statistical Queries mit Toleranz $\tau = \Omega(1/\mathrm{poly})$; die Schranken übertragen sich auf probabilistische und Quantenalgorithmen (Abschnitt F).
* **Status:** 🟢 🔴 🟢 im SQ-Modell: Samples polynomiell, Queries exponentiell in $d$; der Preis ist unbedingt, keine kryptographische Annahme.
* **Versprechen:** keines über die Instanz außer der Tiefe; $\beta$ interpoliert zwischen Worst Case ($\beta = 1$) und Average Case.

### Das Problem

Härte im Worst Case sagt nichts über heuristische Lerner, die auf typischen Instanzen laufen. Ist das Lernen von Output-Verteilungen für einen zufälligen Schaltkreis hart, und ab welcher Tiefe? Und wie hängt die Härte von der geforderten Erfolgswahrscheinlichkeit $\beta$ ab?

### Kernresultate

* **Informal Theorem 1.** (1) $d\to\infty$: $q = 2^{2^{\Omega(n)}}$ Queries für jedes $\beta > 2\exp(-2^{n-2}/9\pi^3)$ (Theorem 2). (2) Lineare Tiefe $d\geq d' = O(n)$: $q = \Omega(2^n)$ für $\beta > 3200\cdot 2^{-n}$ (Theorem 6). (3) Sublinear: für $c\log n\leq d\leq c(n+\log n)$ mit $c = 1/\log(5/4)$ ist $q = 2^{\Omega(d)} = 2^{\omega(\log n)}$ für $\beta > 4/5 + \epsilon + \tau$ (Theorem 12).
* **Informal Theorem 2 / Theorem 36.** Für $d\geq d' = O(n)$, $\epsilon\leq 1/225$ und jede Verteilung $Q$: $\Pr_U[d_{\mathrm{TV}}(P_U, Q) > \epsilon]\geq 1 - O(2^{-n})$.
* **SQ-Obergrenze.** Ein $\epsilon$-Netz über die Verteilungen liefert $q\leq\exp[O(nd\log(nd/\epsilon))]$ (Turnier); bei linearer Tiefe $\exp[O(n^2\log n)]$ gegen $\Omega(2^n)$, die Lücke bleibt offen.

### Methodischer Ansatz

* SQ-Dimension und Anti-Konzentration: Die Verteilungen zufälliger Schaltkreise sind ab logarithmischer Tiefe paarweise fast unkorreliert (approximative Designs), sodass jede Query nur wenige Instanzen ausschließt; die Tiefenabhängigkeit kommt aus der Design-Konvergenzrate.
* Das Maß über Instanzen ist die Schaltkreisverteilung selbst, nicht uniform über Verteilungen; das ist die natürliche Wahl für QCBM-Analysen.
* SQ-Lerner umfassen alle gradientenbasierten QCBM-Trainer (Parameter-Shift, SPSA), also trifft die Schranke die Praxis.

### Bedeutung und Anwendungen

* Das QCBM-Gegenstück zu Average-Case-Härte für tiefe neuronale Netze; heuristische Lerner können ab logarithmischer Tiefe auf typischen Instanzen nicht effizient sein.
* Die "Far from uniform"-Eigenschaft stützt Heavy-Output-Generation als Vorteilsnachweis.

### Bezug zum eigenen Projekt

* Average-Case-Härte ist die Frage, die die eigene Arbeit für Displacement-Spektren offen lässt: LWE gibt Worst-Case-Härte über eine Reduktion, dieses Paper zeigt, wie unbedingte Average-Case-Schranken im SQ-Modell aussehen; für einen CNN-Decoder, der nur Bell-Statistiken sieht, ist das SQ-Modell die richtige Abstraktion.
* Die Parameter $(d, \beta, \tau, \epsilon)$ sind eine vierdimensionale Instanzenleiter; die Trennung "konstante Wahrscheinlichkeit ab $\log n$, exponentiell nahe eins ab linearer Tiefe" ist ein Muster für die Stufen der eigenen Leiter.
* Die Design-Eigenschaft ab logarithmischer Tiefe ist dieselbe, die Displacement-Spektren flach macht: Ab dieser Tiefe gibt es typischerweise keinen sparsamen Träger.

### Grenzen und offene Fragen

* Nur SQ; Sample-Komplexität und Härte für allgemeine Lerner mit Einzel-Samples offen.
* Lücke zwischen $\Omega(2^n)$ und $\exp[O(n^2\log n)]$ bei linearer Tiefe.
* Andere Verteilungsfamilien (freie Fermionen) und die Frage, ob Simulationshärte Lernhärte impliziert, offen.

### Fragen zum Tieferbohren

* Wie genau wird die SQ-Dimension aus der Design-Konvergenz des Brickwork-Ensembles abgeleitet, und woher kommt $c = 1/\log(5/4)$?
* Wie überträgt sich die SQ-Schranke auf Quantenalgorithmen mit Einzel-Samples (Abschnitt F), und was geht dabei verloren?
* Gilt eine analoge Average-Case-Schranke für Bell-Statistiken zufälliger Schaltkreise, also für das Lernen des Displacement-Spektrums aus Zweikopien-Samples?

Paper: [arXiv:2305.05765](https://arxiv.org/abs/2305.05765)

<br>

<a id="cross-task-bounds-hardness-decoders-surveys"></a>
# Cross-Task: Bounds, Hardness, Decoders, Surveys

## Where the bounds come from: proof technology

The thesis of the overview, a dense sample map and a nearly empty time map, has a concrete cause: the two kinds of bounds are proved with different tools, and only one kind is unconditional.

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
| 2022 | Learning from experiments, Sycamore demo (Huang et al., Science) · Provable ML on shadow data (Huang et al., Science) · Pauli-channel separation (Chen–Zhou–Seif–Jiang) · QUALM (Aharonov–Cotler–Qi) · High-temperature Hamiltonian learning in polynomial time (Haah–Kothari–Tang) · Few-T learning (Lai–Cheng) · Pseudoentanglement · Output-distribution learnability (Hinsche et al.) · Nonadaptive single-copy lower bound (Lowe–Nayak) · Tight certification bounds with incoherent measurements (Chen–Huang–Li–Liu) · Non-Markovian process tensor tomography (White et al.) |
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

# Appendix

The three tables are the primary object. This appendix keeps the three axes that generate them, for readers who want the coordinate system: the quadrant of access against task, the access ladder, and the measurement-power axis.


## Reading the tables

**The pattern in the status column.** Every 🟢 🟢 🟢 row under sampling access names a promise (locality, subgroup, class structure, Gaussianity, bond dimension, light cone, low degree, a gapped phase) or a resource (two-copy memory, an entangled ancilla); every 🟢 🟢 🟢 row under query access names the access itself, sometimes together with a promise. The 🟢 🔴 rows are the generic cases. Time efficiency is never free; it is bought by a promise about the state, by a resource on the quantum side, or by a stronger access model.

Glyph order in the status column: copies · time · memory.

**Two ways to fail, which the memory column separates.**
* *Hypothesis too large.* MMW-based shadow tomography keeps a $2^n \times 2^n$ matrix. Memory is exponential, and therefore time is too: an algorithm cannot touch more memory than it has steps. This is a representation problem, and sparse surrogates solve it.
* *Search too hard.* Sparse displacement spectra need $O(k \log d)$ bits for the list. Memory is polynomial, time is LWE-hard regardless. This is a decoder problem, and no representation solves it.
* The implication runs one way only: exponential memory forces exponential time, exponential time does not force exponential memory. The project's row is the only one in the table where memory holds and time still fails. The boundary this document is about is the decoder, not the representation.
* The own pipeline crossed the memory boundary three times: the $d \times d$ histogram became a coprime fold into a fixed $64 \times 64$ tensor, the $d^2$-wide output layer became a bit vector of $2\lceil\log_2 d\rceil$ neurons, and the $d \times d$ MMW hypothesis became a sparse surrogate of $O(k)$ weights. Each replacement was necessary; none of them touched the time hardness of localization.

**What the merged tables show.**
* The object column shows that dynamics are not a separate category. States, Hamiltonians, unitaries, channels, and classical functions appear in all three tables; only the access differs, and it follows the rule of the overview: fixed or random inputs are sample access through the Choi or data state, adaptive or controlled use is query access. The object decides hardness only through the normalization of its spectrum, which is why heavy Pauli terms of a unitary are found from samples and heavy displacement terms of a state are not.
* The computational boundary, as far as it is charted, is the set of 🟢 🔴 rows: sparse displacement spectra and LWE from samples (searching); general shadow tomography, PAC learning of states, and online learning (estimating, hypothesis too large); pseudorandom states, bounded gate complexity, and output distributions of circuits (identifying, cryptographic). Every one of them is sample-efficient. The three that fail in time with polynomial memory, the LWE pair, bounded gate complexity, and the output-distribution family, are the ones where the hardness is a theorem about the decoder rather than about the size of the hypothesis.
* Every cell of the quadrant in the appendix is present with several examples, and the query rows carry no hardness for any task type. That is why the quadrant collapses to a single hard corner. Tasks that stay hard under queries, such as full tomography, are kept out of the quadrant on purpose.
* The generic hard case has its own row: LWE from i.i.d. samples, directly under the project's row in the searching table, with the same 🟢 🔴 🟢. The hardness theorem behind this project embeds one into the other, a real-diagonal displacement state whose Bell outcomes are LWE samples, so the two rows are one instance seen from two sides.
* One cell was empty in every earlier draft: query access with an identifying task. Bernstein–Vazirani fills it for functions, identification with preparation circuits for states. In the identifying column queries buy only the precision rate, because a polynomial list of candidates is already easy under sampling.
* Identifying and searching coincide when the candidate class is exponentially large and parametrized. The LWE secret indexes $q^n$ hypotheses and at the same time locates the support; the distinction carries weight only when the list is polynomial (identifying) or the support must be found in an exponential space without a parametrization (searching). The LWE rows are labeled searching for that reason; Bernstein–Vazirani, its noiseless limit, is labeled identifying because one query resolves the parameter.
* Simon and Montanaro run the same decoder: random elements of a subspace, then Gaussian elimination. The access differs, Fourier sampling of an oracle versus differences of Bell samples, and the subgroup promise makes the decoder linear on both rows. The promise, not the access, buys the time efficiency there.


## The access-by-task quadrant

Crossing the access axis with the task axis gives four cells. All four are populated, and all four are efficient in the first budget, copies or queries: the quadrant maps only the computational boundary. Drawing them makes visible what the tables hide when read separately: computational hardness lives in exactly one cell, and it needs both restrictions at once. The rows of the three tables, grouped by access and task type, are the examples behind each cell; the identifying column is merged into estimating here because it behaves like estimating in every budget.

| | **Estimating / Identifying** (a list is given) | **Searching** (observables are output) |
| --- | --- | --- |
| **Sampling access** (i.i.d. copies, rungs 1–2) | Shadow tomography, classical shadows; with conjugate pairs the character mean over a dictionary of size $M$. *Regime 1.*<br>• **Copies**: $\mathrm{poly}(\log M, n, 1/\epsilon)$; with conjugate pairs $N = O(g^{-2}\log(M/\delta))$ for gap $g$.<br>• **Time**: $\mathrm{poly}(M)$ for an explicit list; $\exp(n)$ when a dense hypothesis is kept (general shadow tomography).<br>• **Memory**: $O(M)$ values for the list; $\exp(n)$ for the dense hypothesis. | Structure learning from Bell samples. *Regime 2 where provable.* **This project.**<br>• **Copies**: $O(\log d/\epsilon^4)$; a union bound over all $d^2$ coefficients stays logarithmic in $d$.<br>• **Time**: generic localization **LWE-hard**; polynomial under subgroup support via Gaussian elimination (Montanaro); empirical in the conjectured class.<br>• **Memory**: $O(k \log d)$ bits, the sparse list. |
| **Query access** (white-box circuit, rung 3) | Amplitude estimation.<br>• **Queries**: $O(1/\epsilon)$ at the Heisenberg rate, instead of $O(1/\epsilon^2)$ samples.<br>• **Time**: poly.<br>• **Memory**: poly. | Goldreich–Levin, Kushilevitz–Mansour, sparse FFT; Bernstein–Vazirani / QFT against LWE; peeling on chosen stabilizer groups for sparse Pauli noise. *Regime 3, not available at rung 2.* Populated for functions and channels; for states with a preparation oracle only the LWE instance is known to fall, and generic localization has amplitude amplification at $O(\sqrt{d/k})$ and nothing better.<br>• **Queries**: $\tilde O(k\log\vert{}V\vert{})$, resp. $\mathrm{poly}(n, 1/\tau)$.<br>• **Time**: poly.<br>• **Memory**: $O(k)$. |

Three statements carry the synthesis.

1. **Only one cell is hard, and it is hard in time alone.** The first line of every cell is green: Hoeffding plus a union bound over all $d^2$ coefficients costs $O(\log d/\epsilon^4)$ copies, the information is there. The memory line of the hard cell is green as well: the sparse list fits. The single red entry in the table is the time line of the sampling-searching cell, and the green memory entry next to it shows that the hardness is not a representation problem but a decoder problem, a cryptographic average-case statement. This is why the budgets of the overview must be kept apart before the quadrant is read: "sample-efficient" and "hard" are statements about different budgets, and both hold in the same cell. The estimating column carries its own split, visible in its time and memory lines: an explicit polynomial-size list is efficient, which is exactly the dictionary promise, while a dense hypothesis is not.

2. **The hard cell is left to the left only by a promise, and never downward.** The row cannot be changed: nature delivers copies. The column changes only through a promise about the state. A dictionary promise moves the task to the left (Regime 1). A subgroup promise keeps the task in the cell but turns decoding into linear algebra (Regime 2). Query access would move downward (Regime 3), but it is not available at rung 2. The three provable escape routes are therefore two promises and one access change. The conjecture of this project claims that a *uniformly random* top-$k$ support is a third promise that suffices, although it falls under none of the three.

3. **Neither adaptivity nor quantum memory changes the row.** Phase 2 of the own protocol chooses probes adaptively, but each probe consumes fresh i.i.d. copies. For the diagonal LWE instance behind the hardness theorem, any measurement, adaptive or not, is classical post-processing of i.i.d. draws from a classical distribution. The same holds for coherent measurements across any number of copies. The instance $\rho_s = \mathbb{E}\,\vert a,b\rangle\langle a,b\vert$ is diagonal, so dephasing each copy in the computational basis leaves $\rho_s^{\otimes k}$ unchanged, and each dephased copy is one classical LWE sample. In QUALM terms (Aharonov, Cotler, Qi 2022), every coherent protocol on copies of $\rho_s$ is simulated, at the extra cost of re-preparing basis states, by a quantum algorithm on classical LWE samples, which the post-quantum LWE assumption rules out. The hardness sits in the lab oracle, not in the coherence of access; only a different oracle, quantum examples in superposition (Grilo, Kerenidis, Zijlstra 2019) or the preparation circuit, removes it. The argument uses diagonality and says nothing about non-diagonal hard instances, for example in the cyclic single-qudit basis. A reader who takes Phase 2 for query access will conclude, wrongly, that the hardness has been circumvented. It has not; it has been *promised away* for a restricted state class, which is what the promise-problem formulation of the positioning section states.

**The classical instance of the same quadrant.** Goldreich–Levin sits in the query-searching cell, Learning Parity with Noise in the sampling-searching cell (see the classical mirror below). The thirty-year-old Boolean dichotomy is the same picture with the same hard corner; LWE is its lattice generalization and Bell sampling its quantum instance.

## Access: sampling versus query

What the world *hands over*. Three rungs, each strictly stronger than the one below it, and each step crosses a different boundary of the overview.

| Rung | Access Type | Boundary crossed | Access | What it enables |
| --- | --- | --- | --- | --- |
| **1. Copies of $\rho$** | Sample (inefficient in copies) | Starting point | Black-box i.i.d. copies; any POVM, any adaptivity | Classical shadows, single-copy tomography; Bell sampling on $\rho\otimes\rho$, which yields the clean spectrum only for real amplitudes (see the Bell-sampling primitive) |
| **2. Copies of $\rho$ and $\rho^*$** | Sample (efficient in copies) |**Sample boundary:** $\Omega(\sqrt d)$ without the conjugate copy, $O(\log d/\epsilon^4)$ with it, at constant quantum memory | Conjugate pair as a physical resource | Clean spectrum $\vert{}\mathrm{Tr}(D_{q,p}\rho)\vert{}^2$ for every $d$ |
| **3. White-box circuit** | Query (efficient in compute) | **Computational boundary:** the LWE instance becomes polynomial by Bernstein–Vazirani on superposition queries; generic localization for states is not known to follow, see the searching refinements | $U$, $U^\dagger$, controlled-$U$ preparing $\rho$ | Amplitude estimation at the Heisenberg rate $1/\epsilon$; superposition queries; $\rho^*$ by conjugating every gate |

This project stands on rung 2: past the sample boundary, in front of the computational one.

**Processes on the same ladder.** The rungs are stated for states. A process enters them through its Choi state or its input–output data state: nonadaptive use on fixed or random inputs is rung 1 or 2, with an entangled ancilla playing the role of the second copy; adaptive, controlled, inverted, or sequential use is rung 3. See "What is learned" in the overview.

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

What the learner may *do* on the quantum side. These are the knobs that move the sample boundary of the overview; neither of them touches the computational boundary.

| Axis | Spectrum | Key Separation / Benchmark |
| --- | --- | --- |
| **Quantum Memory** | $1 \to 2 \to k$ copies coherent | Pauli spectrum: $\Theta(n)$ copies (2-copy) vs. $2^{\Omega(n)}$ (1-copy) |
| **Adaptivity** | Fixed $\leftrightarrow$ dynamic settings | Exponential sample savings for non-local property testing |

**Vocabulary: adaptivity is not query access.** 
* *Adaptivity* means that the measurement setting on the next copy may depend on the outcomes of earlier copies. Every copy is still an i.i.d. draw of $\rho$; only the POVM changes. 
* *Query access* (the access ladder) means the learner chooses the point at which a function is evaluated, or holds the circuit that prepares the state. 
* Both involve a choice by the learner; only the second changes the access model. Sparse-FFT and Goldreich–Levin decoders are often called "adaptive" because they choose their evaluation points; in the vocabulary of this document they are *query-based*. 
* The distinction matters for Phase 2 of the own protocol: the probe $\sigma$ is chosen adaptively, but each probe is measured against fresh i.i.d. copies of $\rho$, so the protocol stays on the sampling side of the access ladder.

**The formal model: QUALM** (Aharonov, Cotler, Qi, Nat. Commun. 2022). An experiment is a quantum circuit on three registers, Nature $N$ (hidden), lab $L$ (accessible and coupled to $N$), and workspace $W$, with slots for an unknown *lab oracle*, a channel on $N\otimes L$. Its cost is the number of gates plus the number of oracle calls, and the width of $W$ is the memory parameter; the three budgets of the overview are these three numbers. The two knobs of this appendix map onto two separate parts of the model:
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
* **Cell in the quadrant:** sampling access at rung 2, searching task: the hard corner. The provable instances (dictionary, subgroup) are the two promises that make the corner decodable; the LWE limit is the statement that sparsity alone is not a third one. The conjecture places a uniformly random top-$k$ support on the decodable side without proof, and the learned decoder is its empirical candidate.
