
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
- [Identifying (Paper)](#identifying-paper)
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

**Two more separations of the same shape.** *Purity testing* (is $\rho$ pure or maximally mixed?) needs $O(1)$ copies with two-copy memory (a SWAP test) but $\Omega(2^{n/2})$ without (Chen, Cotler, Huang, Li, FOCS 2021); the memory-free lower bound also kills any single-copy route to $\mathrm{Tr}(\rho^2)$. *Pauli channel estimation*: learning all $4^n$ Pauli eigenvalues of a channel to $\pm\epsilon$ takes roughly $O(n/\epsilon^2)$ uses with ancilla-assisted entangled inputs versus $2^{\Omega(n)}$ without (Chen, Zhou, Seif, Jiang, PRA 2022), the channel version of the shadow-tomography separation. The general framework in which all of these live is **QUALM** (Aharonov, Cotler, Qi, Nat. Commun. 2022): an experiment is a quantum algorithm that calls an unknown *lab oracle*, with *coherent* access (outputs of several calls held and measured jointly) or *incoherent* access (each output measured completely before the next call, adaptivity allowed). The separations above are statements about this coherence, which is the memory axis of this document, not about the model class; which oracle nature supplies, copies of $\rho$, pairs $\rho\otimes\rho^*$, or the preparation circuit, is the separate access ladder. On qubits the SWAP test behind these separations is a coarse-grained Bell measurement: SWAP is diagonal in the Bell basis, with eigenvalue $(-1)^{\#Y}$ on the outcome $P$. On qudits with $d>2$ it is not; see the QUALM summary under Identifying (Paper).

<br>

# Searching

**Searching** (observables are *output*). Given: copies of $\rho$ and a promise about the spectrum, typically sparsity or a structural constraint on the support. Returned: the addresses $(q,p)$ that carry the weight, and then their values. Nothing else is handed over, no list of candidates and no parametrization. Like a GWAS: first find which loci matter, then measure their effect. The error factorizes accordingly into localization and estimation, and the estimation guarantees of the next section apply only after localization has succeeded. That is why searching is genuinely harder than estimating, and it is the column in which LWE hardness sits.

**What is known.** The sample side is settled. Bell sampling on conjugate pairs estimates all $d^2$ squared magnitudes with $O(\log d/\epsilon^4)$ copies, exponentially fewer than any strategy without the conjugate copy, at constant quantum memory (King, Wan, McClean 2024). The information is therefore always there. On the time side, efficient decoders exist exactly under a promise: a subgroup support falls to Gaussian elimination (Montanaro 2017, and Simon's algorithm under queries), a polynomial dictionary reduces the search to estimation, locality reduces junta learning to a polynomial dictionary, Hamiltonian structure learning from real-time evolution stays Heisenberg-limited even when the interaction terms are not given (Bakshi, Liu, Moitra, Tang 2024), and a factorized spectrum over coprime factors falls to a best-first heap. Under query access the classical sparse-Fourier toolkit applies: Goldreich–Levin, Kushilevitz–Mansour, sparse FFT, and their quantum-query versions. For unitaries no queries are needed: their Pauli spectrum is unit-normalized, and Bell sampling on the Choi state returns the heavy terms directly. Without any promise and with sampling access alone, localization is LWE-hard: a real-diagonal displacement state whose Bell outcomes are LWE samples has a sparse, visible spectrum whose support cannot be located in polynomial time under standard assumptions. The classical mirror is Learning Parity with Noise, thirty years old.

**Efficiency status.** Copies: 🟢 in every row, the union bound over $d^2$ addresses stays logarithmic. Memory: 🟢 in every row, a sparse list fits. Time: 🟢 only where the status column names a promise or query access; 🔴 for the generic case, by a theorem in the tensor-product Weyl basis and by the LPN mirror on the Boolean side.

**What is open.**
* (1) Which classes of states and channels are time-efficient for structure learning? A generic state is most likely not both sample- and time-efficient in the Heisenberg–Weyl basis; the map of decodable classes between "subgroup-easy" and "LWE-hard" is the research question of this project.
* (2) What is the LWE counterpart for the conjugate-pair Bell protocol in the Heisenberg–Weyl basis? The hardness theorem lives in the tensor-product basis. A sample-efficient but computationally hard boundary most likely exists in the cyclic single-qudit basis too, but the naive transfer is the hidden number problem, against which lattice attacks exist; composite $d$ with coprime factors approaches the tensor structure via the CRT.
* (3) Average case. The hardness constructions are adversarial. Whether natural states, ground and Gibbs states of local Hamiltonians, are generically decodable is open in both directions; the conjecture of this project, a uniformly random top-$k$ support on the decodable side, is a claim about exactly this gap, and the learned decoder is its only evidence so far.
* (4) Where searching ends and identifying begins. A parametrized exponential class, the LWE secret, is both at once. No theorem separates the two beyond the size of the candidate list.

| Protocol or class | Object | Task type: given → returned | Copies or queries (access) | Time | Memory | Status & Condition |
| --- | --- | --- | --- | --- | --- | --- |
| **Sparse displacement spectra from Bell samples** (this project; see the structure-learning protocol) | State | Searching: sparsity promise → support and values of the spectrum | Sample: $O(\log d/\epsilon^4)$ | Generic localization LWE-hard | $O(k \log d)$ bits, the sparse list | 🟢 🔴 🟢; search too hard, **this project's cell** |
| **LWE from i.i.d. samples** (Regev 2005) and its displacement instance: a real-diagonal state whose Bell outcomes are LWE samples | Classical function; a state in the displacement instance | Searching: noisy linear samples $(\mathbf{a}_i, \langle\mathbf{a}_i,\mathbf{s}\rangle + e_i)$ → the secret $\mathbf{s}$, i.e. the hidden line that carries the support | Sample: poly, information-theoretically sufficient | Hard under the LWE assumption; classical mirror LPN, best known $2^{O(n/\log n)}$ (Blum–Kalai–Wasserman 2003) | poly, the secret | 🟢 🔴 🟢; the generic hard case, **the theorem behind this project's cell** |
| **Stabilizer states** (Montanaro 2017) | State | Searching: subgroup promise → the stabilizer group, i.e. the support | Sample: $O(n)$ | $O(n^3)$, Gaussian elimination on Bell differences | $O(n^2)$, the tableau | 🟢 🟢 🟢; subgroup promise |
| **Factorized spectra over coprime factors** (Regime 3 of the own conjecture, extension G3) | State | Searching: product promise $y_{u_1\dots u_m} = \prod_j y_{u_j}(\rho_j)$ across the CRT factors of $d$ → the top-$k$ of the product from the per-factor top lists by a best-first heap | Sample: one Bell record per factor, $O(\log d_j/\epsilon^4)$ each | $\mathrm{poly}(k, \log d)$ heap operations | $O(k)$ | 🟢 🟢 🟢; factorization promise, composite $d$ only |
| **Stabilizer states on qudits, $d > 2$** (Allcock, Doriguello, Ivanyos, Santha 2024) | State | Searching: subgroup promise → the stabilizer group, where plain Bell sampling on $\rho\otimes\rho$ can be uniform and reveal nothing | Sample: $\mathrm{poly}(n, \log d)$ with the replacement measurements of that paper | poly | poly | 🟢 🟢 🟢; subgroup promise; the qudit caveat behind the conjugate-pair choice of this project |
| **Quantum juntas** (Chen, Nadimpalli, Yuen 2023) | Unitary | Searching: the unitary acts on $k$ unknown qubits out of $n$ → those $k$ qubits, then the $k$-qubit unitary | Sample on the Choi state: $O(k/\epsilon + 4^k/\epsilon^2)$ uses of $U$, independent of $n$; the junta *test* needs $\tilde O(\sqrt k)$ queries to $U$ and $U^\dagger$ | $\mathrm{poly}(n, 4^k)$ | $O(k\log n)$ plus the $k$-qubit unitary | 🟢 🟢 🟢; junta promise, the support search at the level of qubits; lower bounds $\Omega(\sqrt k)$ and $\Omega(4^k/k)$ nearly match |
| **DNF and heavy Fourier coefficients from quantum examples** (Bshouty, Jackson 1998) | Classical function | Searching: quantum examples $\sum_x \sqrt{D(x)}\,\vert x, f(x)\rangle$ under the uniform distribution → the heavy coefficients of $f$, then a DNF | Sample: Fourier sampling of the example state returns $S$ with probability $\hat f(S)^2$; $\mathrm{poly}(n, 1/\tau)$ examples | poly | poly | 🟢 🟢 🟢; heaviness promise: a heavy Boolean coefficient carries a constant fraction of unit total weight, a displacement coefficient of size $\Theta(1)$ carries $1/d$ of it, which is why direct sampling finds the former and not the latter |
| **Heavy Pauli coefficients of a unitary** (Fourier sampling on the Choi state; operator Goldreich–Levin: Montanaro, Osborne 2010) | Unitary | Searching: threshold $\tau$ → all Pauli coefficients of $U$ above $\tau$ | Sample on the Choi state: $O(\tau^{-2}\log(1/\tau\delta))$ Bell samples, since $\sum_P \vert{}u_P\vert{}^2 = 1$ makes every heavy term appear with probability at least $\tau^2$ | poly | $O(\tau^{-2})$ terms | 🟢 🟢 🟢; unit normalization of the spectrum, the operator analogue of Bshouty–Jackson |
| **Heavy Fourier coefficients**: Goldreich–Levin, Kushilevitz–Mansour, sparse FFT; with quantum queries Adcock, Cleve 2002 | Classical function | Searching: threshold $\tau$ → all coefficients above $\tau$ | Query: $\mathrm{poly}(n, 1/\tau)$ resp. $\tilde O(k \log \vert{}V\vert{})$ evaluations at chosen points | poly | $O(k)$ | 🟢 🟢 🟢; query access |
| **Simon's problem, hidden subgroup** | Classical function | Searching: subgroup promise → the hidden subgroup | Query: $O(n)$ superposition queries | $O(n^3)$, Gaussian elimination on Fourier samples | $O(n^2)$ | 🟢 🟢 🟢; the query-side mirror of Montanaro |
| **LWE with superposition queries** (Grilo, Kerenidis, Zijlstra 2019) | Classical function | Searching: noisy linear samples in superposition → the secret $\mathbf{s}$ | Query: poly superposition queries | poly | poly | 🟢 🟢 🟢; the instance that is LWE-hard under sampling |
| **Hamiltonian structure learning from real-time evolution** (Bakshi, Liu, Moitra, Tang, FOCS 2024) | Hamiltonian | Searching: $k$-locality promise, interaction terms *not* given → which of the $n^{O(k)}$ candidate terms are present, and their coefficients | Query to the dynamics $e^{-iHt}$: Heisenberg-limited total evolution time, $O(\log n/\epsilon)$ | poly | poly | 🟢 🟢 🟢; locality promise with unknown geometry; the searching counterpart of Heisenberg-limited coefficient learning in the estimating table |

## Searching protocols

The observables are the output. Two families: structure learning from measurement data on quantum states, and the older Fourier-sampling family on quantum examples of classical functions, which shows what a favourable normalization buys.

## Structure learning (observables as output)

**Task inversion:** First *find* the few observables that carry the support of a sparse Pauli/displacement spectrum, then estimate their values (first the edges, then the weights, as in learning graphical models). Sampling is the easy half: Bell sampling concentrates the draws on the support. **Decoding is the hard half:** Turning i.i.d. samples into the support is sparse recovery *without choosable queries*, generically cryptographically hard (LWE-type). Subgroup/stabilizer symmetries are the tractable exception.

* **Montanaro (2017):** Stabilizer states from $O(n)$ Bell samples via linear algebra.
* **Grewal, Iyer, Kretschmer, Liang (2023):** Bell difference sampling, states with few non-Clifford gates.
* **Hangleiter, Gullans (PRL 2024):** Bell sampling as a universal diagnostic framework.
* **Chen, Nadimpalli, Yuen (SODA 2023):** Quantum juntas, the support search at the level of qubits, logarithmic in $n$.
* **Bakshi, Liu, Moitra, Tang (FOCS 2024):** Hamiltonian structure learning from real-time evolution. Only locality is promised, the interaction terms are not given, and the total evolution time stays Heisenberg-limited. The line between this and coefficient learning: for a geometrically local Hamiltonian on a known lattice, all local terms form a dictionary of bounded degree, and coefficient learning returns the structure as a by-product. Structure learning proper begins when the geometry is unknown, $k$-body terms among arbitrary qubits; the guarantees of the coefficient algorithms depend on the degree of the interaction graph and no longer apply directly. The coefficient papers with known terms (Anshu et al. 2021; Haah, Kothari, Tang 2022; Bakshi, Liu, Moitra, Tang, STOC 2024; Gu, Cincio, Coles 2024) are estimating protocols and sit in the dynamics subsection.
* **Bshouty, Jackson (1998):** DNF from quantum examples by Fourier sampling, the sample-access case in which heavy coefficients are found without queries.
* **Adcock, Cleve (2002) / Montanaro, Osborne (2010):** Quantum Goldreich–Levin, for Boolean functions under quantum queries and for the Pauli spectrum of operators. For unitaries the heavy terms are already found by Bell sampling on the Choi state, a sample-access route, because the spectrum is unit-normalized; see the normalization paragraph below.

**Where Bell difference sampling comes from.** The distribution behind stabilizer learning, $p(x) \propto \sum_y \hat p_\psi(y)\,\hat p_\psi(x+y)$ over $\mathbb{F}_2^{2n}$ with $\hat p_\psi(x) = 2^{-n}|\langle\psi|P_x|\psi\rangle|^2$ the **characteristic distribution**, is a corollary of the **Schur–Weyl duality for the Clifford group** (Gross, Nezami, Walter, Commun. Math. Phys. 2021): the commutant of $U^{\otimes 4}$ over Cliffords is spanned by stabilizer codes, which is why four copies (two Bell pairs, differenced) expose the stabilizer group. This is the group-theoretic reason "subgroup/stabilizer symmetries are the tractable exception": the support of $\hat p_\psi$ for a stabilizer state is a Lagrangian subspace, and linear algebra over $\mathbb{F}_2$ recovers a subspace from $O(n)$ random elements.

**Why Fourier sampling finds heavy coefficients of functions and unitaries, and Bell sampling does not find heavy displacement coefficients of states.** For a pure state the Bell distribution on $\rho\otimes\rho^*$ is $P(z) = \vert{}y_z\vert{}^2/d$, the squared spectrum itself: the characteristic distribution of a pure state is its own symplectic Fourier transform (Gross, Nezami, Walter 2021). One might hope to read the top-$k$ off the histogram of outcomes. But $\sum_z \vert{}y_z\vert{}^2 = d$, so a coefficient of size $\Theta(1)$ has probability $\Theta(1/d)$ and is invisible in $\mathrm{poly}(n)$ shots. The character mean $\sum_z P(z)\chi_u(z)$ uses every shot for every coefficient and reaches $\vert{}y_u\vert{}^2$ with $O(1/\epsilon^4)$ shots; that is why the Fourier step is essential and why localization remains a search over $d^2$ addresses. In the Boolean case the normalization is $\sum_S \hat f(S)^2 = 1$, a heavy coefficient has probability $\tau^2$, and Fourier sampling returns it directly. That normalization is the whole difference between Bshouty–Jackson and the LWE wall. Unitaries sit on the Boolean side. For $U = \sum_P u_P P$ the coefficients satisfy $\sum_P \vert{}u_P\vert{}^2 = 1$, and the Choi state $(U\otimes I)\vert\Phi\rangle = \sum_P u_P (P\otimes I)\vert\Phi\rangle$ is written in the Bell basis with exactly these amplitudes. One Bell measurement per use of $U$ returns $P$ with probability $\vert{}u_P\vert{}^2$, so all coefficients above $\tau$ appear within $O(\tau^{-2}\log(1/\tau\delta))$ shots, from sample access alone. A pure state $\rho$ has the same Bell-basis picture with amplitudes $y_z/\sqrt d$, and the extra $1/\sqrt d$ is the whole problem. The object therefore matters for hardness through the normalization of its spectrum, not through being a state or a process.

## Quantum PAC learning and quantum examples

The oldest access model in the field: the learner receives copies of the example state $\sum_x \sqrt{D(x)}\,\vert x, f(x)\rangle$ of a classical function $f$.

* **Bshouty, Jackson (SIAM J. Comput. 1998):** DNF learnable under the uniform distribution from quantum examples, by Fourier sampling; the first quantum learning advantage in time.
* **Servedio, Gortler (SIAM J. Comput. 2004) / Atıcı, Servedio (2005):** Equivalences and separations between quantum and classical learnability; polynomial gaps in samples, exponential gaps in time under cryptographic assumptions.
* **Aaronson (Proc. R. Soc. A 2007):** Learnability of quantum states: $O(n)$ samples to predict most measurements. **Rocchetto (2018):** stabilizer states are efficiently PAC-learnable.
* **Arunachalam, de Wolf (SIGACT 2017; JMLR 2018):** Survey, and the optimal bound $\Theta(d_{\mathrm{VC}}/\epsilon + \log(1/\delta)/\epsilon)$: quantum examples buy nothing in samples for classical concept classes.
* **Grilo, Kerenidis, Zijlstra (PRA 2019):** LWE is easy with quantum samples, via Bernstein–Vazirani on the example state.
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

<br>

# Estimating

**Estimating** (observables are *input*). Given: copies of $\rho$ and a list of $M$ observables, explicit or implicit. Returned: the $M$ expectation values to precision $\epsilon$. Like a panel of predefined SNPs: the loci are fixed in advance, only their values are unknown. Full tomography is the limit $M = d^2$, sequencing the whole genome. The list can be explicit and polynomial (a dictionary), implicit and exponential (all Paulis), drawn from a distribution (PAC learning and average-case prediction), or revealed one observable at a time (online learning). The task type is the same in each case; the budgets differ.

**What is known.** This is the best-charted column of the field, almost entirely on the sample side. Full tomography costs $\Theta(d^2/\epsilon^2)$ copies with entangled measurements and $\Theta(d^3/\epsilon^2)$ with single copies, adaptivity included. Shadow tomography answers $M$ questions with $\mathrm{poly}(\log M, n, 1/\epsilon)$ copies, currently $\tilde O(\log^2 M \cdot \log d/\epsilon^4)$; classical shadows do it with single-copy random measurements at a cost set by the shadow norm, cheap for local observables and exponential for global ones. Two-copy memory closes that gap: $\Theta(n)$ copies for all Pauli expectations against $2^{\Omega(n)}$ without memory, the strongest proven separation in the field, demonstrated in hardware. Conjugate pairs deliver the clean squared spectrum at constant memory. Under query access the precision rate improves from $1/\epsilon^2$ to $1/\epsilon$, for observables, for unitaries, and for Hamiltonian couplings.

**Efficiency status.** Copies: 🟢 everywhere except full tomography and its low-rank and unitary variants, which stay exponential in $n$ by dimension counting. Time and memory: 🔴 for general shadow tomography, because its hypothesis is a $2^n\times 2^n$ matrix, and likewise for PAC and online learning of states. 🟢 🟢 🟢 exactly where a promise or a resource is named: locality (classical shadows), two-copy memory (all Paulis), a dictionary (conjugate pairs), a gapped phase (ground-state prediction), locality of the Hamiltonian (Gibbs and real-time learning, time-efficient at any constant temperature only since 2024).

**What is open.**
* (1) The precision exponent. Shadow tomography sits at $1/\epsilon^4$, the lower bound at $1/\epsilon^2$; whether the gap closes at polylogarithmic cost in $M$ is open.
* (2) Memory between zero and two. The sample complexity interpolates smoothly with $k$ qubits of memory (Chen, Cotler, Huang, Li), but no protocol family is known that uses a fixed small memory budget for structured observable sets.
* (3) Triply efficient schemes beyond Paulis and local fermionic observables, and whether a learned decoder can replace the graph-coloring step on which the current schemes rely.
* (4) Noise. The two-copy separations are stated for ideal Bell measurements; robustness to preparation, crosstalk, and readout errors is the practically decisive axis, and the first empirical evaluation of a two-copy triply efficient scheme dates from 2025.

| Protocol or class | Object | Task type: given → returned | Copies or queries (access) | Time | Memory | Status & Condition |
| --- | --- | --- | --- | --- | --- | --- |
| **Full QST** | State | Estimating, $M = d^2$: nothing withheld → density matrix $\rho$ | Sample: $\Theta(d^2/\epsilon^2)$ entangled, $\Theta(d^3/\epsilon^2)$ single-copy | $\mathrm{poly}(d)$ | $d^2$ entries | 🔴 🔴 🔴; baseline |
| **Shadow tomography, general** (Aaronson 2018; Bădescu–O'Donnell 2021) | State | Estimating: list of $M$ observables → $M$ values $\mathrm{Tr}(O_i\rho)$ | Sample: $\mathrm{poly}(\log M, n, 1/\epsilon)$ | $\exp(n)$: the MMW update touches a $2^n \times 2^n$ hypothesis | $\exp(n)$: that hypothesis | 🟢 🔴 🔴; hypothesis too large |
| **PAC learning of states** (Aaronson 2007) | State | Estimating, average case: observables drawn from a distribution → predictions correct for most of them | Sample: $O(n)$ | No efficient learner in general; efficient for stabilizer states (Rocchetto 2018) | $d \times d$ hypothesis in general, poly for structured classes | 🟢 🔴 🔴; generic |
| **Classical shadows, $k$-local Paulis** | State | Estimating: list of $M$ local observables, chosen after measurement → $M$ values | Sample: $O(\log M \cdot 3^k/\epsilon^2)$ | poly | $O(Nn)$, one stabilizer product per snapshot | 🟢 🟢 🟢; locality promise |
| **All $4^n$ Pauli observables, two-copy** (King, Gosset, Kothari, Babbush 2024) | State | Estimating: all $4^n$ Paulis → any value on demand | Sample: $\mathrm{poly}(n)$, two copies at a time; $2^{\Omega(n)}$ with single copies (Chen, Cotler, Huang, Li 2021) | $\mathrm{poly}(n)$ | $\mathrm{poly}(n)$, the compressed representation | 🟢 🟢 🟢; two-copy memory |
| **Displacement amplitudes over a dictionary, conjugate pairs** (King, Wan, McClean 2024) | State | Estimating: list of $M$ candidate $(q,p)$ → magnitudes of $y_{q,p}$ from Bell sampling, signs by the adaptive eigenprobe | Sample on $\rho\otimes\rho^*$: $O(\log d/\epsilon^4)$ for all magnitudes, $N = O(g^{-2}\log(M/\delta))$ for the top-$k$ over the list; $\Omega(\sqrt d)$ without the conjugate copy | $\mathrm{poly}(M)$ character means on one Bell record | $O(M)$ values | 🟢 🟢 🟢; conjugate access plus dictionary promise, *Regime 1* |
| **Low-rank tomography, compressed sensing** (Gross, Liu, Flammia, Becker, Eisert 2010) | State | Estimating, $M = d^2$ with a rank-$r$ promise → the state | Sample: $O(rd\log^2 d)$ Pauli expectation values instead of $d^2$ | $\mathrm{poly}(d)$, nuclear-norm minimization | $O(rd)$ | 🔴 🔴 🔴 in $n$; the rank promise cuts $d^2$ to $rd$ |
| **Spectrum estimation by Schur sampling** (Keyl, Werner 2001; O'Donnell, Wright 2015) | State | Estimating: the eigenvalues of $\rho$ → the spectrum | Sample: $O(d^2/\epsilon^2)$ copies measured collectively, quantum memory $k = N$ | $\mathrm{poly}(d)$ | $O(d)$ | 🔴 🔴 🟢 in $n$; the far end of the memory axis, all copies entangled at once |
| **Online learning of quantum states** (Aaronson, Chen, Hazan, Kale, Nayak 2018) | State | Estimating, sequential: observables arrive one at a time → a prediction each, regret $O(\sqrt{Tn})$, at most $O(n/\epsilon^2)$ mistakes | Sample-free: the true value $\mathrm{Tr}(E_t\rho)$ is fed back after each round | $\exp(n)$: MMW over a $2^n\times 2^n$ hypothesis | $\exp(n)$ | 🟢 🔴 🔴; hypothesis too large, the online cousin of shadow tomography |
| **Classical shadows, other ensembles** (fermionic and matchgate: Zhao, Rubin, Miyake 2021; Wan, Huggins, Lee, Babbush 2023; shallow and locally scrambled: Bertoni et al. 2024; Hu, Choi, You 2023; derandomized: Huang, Kueng, Preskill 2021) | State | Estimating: fermionic observables, or local observables under shallow randomization → values | Sample: poly, the shadow norm of the chosen ensemble decides the constant | poly | poly | 🟢 🟢 🟢; the promise moves with the ensemble |
| **Ground-state properties across a phase from shadows** (Huang, Kueng, Torlai, Albert, Preskill 2022; Lewis et al. 2024; Onorati, Rouzé, França, Watson 2023) | Family of states $\rho(x)$ | Estimating, generalization: shadows of $\rho(x)$ at training parameters $x$ → $\mathrm{Tr}(O\rho(x'))$ at new $x'$ in the same phase | Sample: $\mathrm{poly}(n)$ training states, $O(\log n)$ in the improved version | poly | poly | 🟢 🟢 🟢; gapped phase plus locality, the provable machine-learned decoder |
| **Hamiltonian coefficients from Gibbs states, known terms** (Anshu, Arunachalam, Kuwahara, Soleimanifar 2021) | Hamiltonian, from copies of its Gibbs state | Estimating: known interaction terms → their coefficients | Sample: $\mathrm{poly}(n, 1/\epsilon)$ copies of the Gibbs state | Not efficient in the original algorithm; polynomial at high temperature (Haah, Kothari, Tang 2022) and at any constant temperature (Bakshi, Liu, Moitra, Tang 2024) | poly | 🟢 🔴→🟢 🟢; the time budget was the open half for three years |
| **Low-degree quantum objects** (Arunachalam, Dutt, Escudero Gutiérrez 2024; Volberg, Zhang 2023) | Observable, unitary, channel | Estimating: Pauli degree at most $\ell$ → all $n^{O(\ell)}$ coefficients | Sample: polynomial in $n$ for constant degree, via the noncommutative Bohnenblust–Hille inequality. ⚠️ Access model unverified: with random product inputs the row stays in the sample block, with adaptively chosen inputs it moves to the query block | poly | poly | 🟢 🟢 🟢; low-degree promise, a dictionary of size $n^{O(\ell)}$ |
| **Predicting arbitrary quantum processes** (Huang, Chen, Preskill 2023) | Channel | Estimating, average case: unknown channel $\mathcal{E}$, inputs from a distribution → $\mathrm{Tr}(O\,\mathcal{E}(\rho))$ for most inputs | Sample: $\mathrm{poly}(n)$ uses of the channel on random inputs | poly | poly | 🟢 🟢 🟢; average case plus locality of $O$ |
| **Pauli channel eigenvalues, entanglement-assisted** (Chen, Zhou, Seif, Jiang 2022) | Channel | Estimating: all $4^n$ Pauli eigenvalues of a channel → any eigenvalue on demand | Sample on the Choi state: channel applied once per shot to half of a Bell pair, $O(n/\epsilon^2)$ with the entangled ancilla as quantum memory, $2^{\Omega(n)}$ without | poly per eigenvalue, from one Bell record | poly, the Bell record | 🟢 🟢 🟢 with ancilla memory; the channel version of the two-copy separation |
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

**The variance bound that decides the ensemble.** The shot count of classical shadows is governed by the **shadow norm** $\|O\|_{\mathrm{shadow}}^2$, which depends on the unitary ensemble: for random single-qubit Pauli measurements, $\|P\|_{\mathrm{shadow}}^2 = 3^{k}$ for a $k$-local Pauli $P$ (local observables cheap, global ones exponential); for random $n$-qubit Cliffords, $\|O\|_{\mathrm{shadow}}^2 \leq 3\,\mathrm{Tr}(O^2)$, so *fidelity* with any pure state costs $O(1/\epsilon^2)$ shots independent of $n$, while a global Pauli still costs $\Theta(2^n)$. Neither ensemble handles global Paulis; that is the gap two-copy Bell measurements close. Two follow-ups worth knowing: **derandomization** (Huang, Kueng, Preskill, PRL 2021) picks the measurement bases greedily against a fixed observable list and beats random shadows by constant factors in practice; **Bădescu–O'Donnell** (STOC 2021) brought shadow tomography proper down to $\tilde O(\log^2 M\cdot\log d/\epsilon^4)$ copies.

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

**Two practical anchors.** *Heisenberg limit* means total evolution time $T \sim 1/\epsilon$ for precision $\epsilon$ on a coupling, versus the standard quantum limit $T \sim 1/\epsilon^2$ of incoherent repetition; the PRL 2023 protocol reaches it with product-state inputs plus a decoupling pulse sequence, no entangled probes. On the noise side, the field-standard protocols are **randomized benchmarking** (Emerson et al. 2005; Magesan et al. 2011), which extracts an average gate fidelity from the exponential decay of survival probability under random Cliffords, and **gate set tomography** (Blume-Kohout et al. 2013; Nielsen et al. 2021), the self-consistent full characterization; Flammia–Wallman's Pauli channel estimation is the sparse, scalable middle ground and the one that maps onto the noise-learning transfer named in the positioning section.

<br>

# Estimating (Papers)

(content pending)

<br>

# Identifying

**Identifying** (candidate *states* or functions are *input*). Given: copies of $\rho$ and a list of $M$ candidate states, or a class $\mathcal{C}$ with or without the promise that $\rho \in \mathcal{C}$. Returned: one index, one object from the class, or one bit. Like matching a sample against a database of known genomes: the hypotheses exist before the data. Sub-cases by the size of the list: $M = 2$ is state discrimination, general $M$ is hypothesis selection, a class with a promise is learning that class, a class without the promise is agnostic tomography, one bit is property testing, and $M = 1$ is certification. Identifying behaves like estimating in every budget as long as the list is polynomial and the candidates are efficiently representable. Once the class is exponentially large and parametrized, the task shades into searching, which is where the hardness rows of this table come from.

**What is known.** The two-hypothesis case is solved exactly: Helstrom for minimum error, unambiguous discrimination for zero error with abstention, and the quantum Chernoff exponent for many copies. Hypothesis selection needs only $O(\log M)$ copies through threshold search. A catalogue of classes is learnable in polynomial time, each by exploiting the structure that defines it: stabilizer states and Clifford circuits by linear algebra, states with $t$ non-Clifford gates at cost $2^t$, Gaussian and near-Gaussian states, matrix product states, states of shallow circuits, phase states of bounded degree, juntas, low-degree objects. Property testing shows the memory axis at its sharpest: purity costs $O(1)$ copies with a SWAP test and $\Omega(2^{n/2})$ without. Certification of almost all states is possible with single-qubit measurements.

**Efficiency status.** Copies: 🟢 throughout; the class results are polynomial, the testing results constant. Time and memory: 🟢 on the catalogue, and provably 🔴 outside it under cryptographic assumptions. Pseudorandom states and pseudoentanglement are statistically learnable yet computationally indistinguishable from Haar; states of polynomial gate complexity need only $\tilde\Theta(G)$ copies but admit no polynomial-time learner; output distributions of circuits become hard under LPN with a single $T$ gate. These rows are this column's version of the LWE wall in the searching column.

**What is open.**
* (1) The magic threshold. $t = O(\log n)$ non-Clifford gates is the frontier of polynomial time; whether $\mathrm{poly}(n, 2^t)$ is optimal is open.
* (2) Depth. Constant-depth circuits are learnable and polynomial-depth ones are hard; everything in between is uncharted.
* (3) Agnostic and tolerant learning beyond stabilizer-type classes.
* (4) Average-case hardness. The pseudorandomness constructions are worst-case; whether physically motivated classes sit on the easy side is the same question as in the searching column.

| Protocol or class | Object | Task type: given → returned | Copies or queries (access) | Time | Memory | Status & Condition |
| --- | --- | --- | --- | --- | --- | --- |
| **Pseudorandom states and pseudoentanglement** (Ji, Liu, Song 2018; Aaronson, Bouland, Fefferman, Ghosh, Vazirani, Zhang, Zhou 2022) | State | Identifying: pseudorandom or Haar-random, low or high entanglement → one bit | Sample: poly, information-theoretically learnable | No polynomial-time distinguisher from Haar | poly, the key | 🟢 🔴 🟢; hard by construction |
| **Identification**: state discrimination ($M=2$), hypothesis selection (general $M$) | State | Identifying: list of $M$ states → one index | Sample: Helstrom (min error) vs. USD (zero error + abort); $O(\log M)$ | Dominated by handling the $M$ candidates: poly for efficiently representable states, $\exp(n)$ for generic ones | The $M$ candidates, same split | 🟢 🟢* 🟢*; *for efficiently representable candidates |
| **Agnostic tomography** (Grewal–Iyer–Kretschmer–Liang 2024; Chen–Gong–Ye–Zhang 2024) | State | Identifying against a class: class $\mathcal{C}$, no promise that $\rho \in \mathcal{C}$ → $\sigma\in\mathcal{C}$ with $F(\rho,\sigma) \geq \max_{\tau\in\mathcal{C}} F(\rho,\tau) - \epsilon$ | Sample: $\mathrm{poly}(n)$ for stabilizer and near-stabilizer classes | poly | poly, a tableau | 🟢 🟢 🟢; class structure |
| **Purity and mixedness testing** (O'Donnell, Wright 2015; Bubeck, Chen, Li 2020; Chen, Cotler, Huang, Li 2021) | State | Identifying: pure or maximally mixed, $\rho = I/d$ or far from it → one bit | Sample: $O(1)$ copies with two-copy memory (SWAP test), $\Omega(2^{n/2})$ without | poly | poly | 🟢 🟢 🟢 with two-copy memory; the simplest memory separation |
| **Fixed-unitary and symmetry-class distinction** (Aharonov, Cotler, Qi, Nat. Commun. 2022; the QUALM paper) | Unitary, as a lab oracle | Identifying: one fixed Haar-random unitary on $\ell$ qubits applied at every call, or a fresh one per call → one bit; fixed unitary, orthogonal, or symplectic → one of three | Oracle calls on a fixed input with two-copy memory: $O(1)$ calls and a SWAP test on the outputs (a generalized SWAP test on a maximally entangled input for the symmetry class); every incoherent protocol, adaptive or not, needs $\Omega(2^{2\ell/7})$ calls | $O(\ell)$ gates | $2\ell$ qubits of quantum memory | 🟢 🟢 🟢 with coherent access; the process version of the purity separation, and the paper that defines coherent versus incoherent access |
| **Stabilizer testing** (Gross, Nezami, Walter 2021; tolerant: Arunachalam, Dutt 2024; Chen, Gong, Ye, Zhang 2024) | State | Identifying: stabilizer state or far from all of them → one bit | Sample: $O(1)$ copies, six in the original test | poly | poly | 🟢 🟢 🟢; Bell difference sampling |
| **State certification** (Huang, Preskill, Soleimanifar 2024) | State | Identifying, $M = 1$: target $\vert\psi\rangle$ known, copies of $\rho$ → accept if close, reject if far | Sample: $\mathrm{poly}(n)$ single-qubit measurements, for almost all target states | poly | poly | 🟢 🟢 🟢; verification rather than learning, the cheapest task in the column |
| **Clifford plus few non-Clifford gates** (Lai, Cheng 2022; Grewal, Iyer, Kretschmer, Liang 2023; Leone, Oliviero, Hamma 2024; Hangleiter, Gullans 2024) | State | Identifying against a class: at most $t$ non-Clifford gates → the state | Sample: $\mathrm{poly}(n, 2^t)$ | $\mathrm{poly}(n, 2^t)$, polynomial for $t = O(\log n)$ | poly | 🟢 🟢 🟢 up to logarithmic magic; the time budget grows as $2^t$, magic is the hardness dial |
| **Gaussian and near-Gaussian states** (fermionic: Aaronson, Grewal 2023; Mele, Herasymenko 2024; bosonic and continuous-variable: Mele et al. 2024) | State | Identifying against a class: Gaussian, Gaussian plus $t$ non-Gaussian gates, or energy-bounded CV states → the state | Sample: $\mathrm{poly}(n, 2^t)$, resp. polynomial in modes and energy | poly | poly | 🟢 🟢 🟢; Gaussianity promise, the continuous-variable cousin of the stabilizer rows |
| **Matrix product and finitely correlated states** (Cramer et al. 2010; Fanizza, Galke, Lumbreras, Muñoz-Gil, Winter 2023) | State | Identifying against a class: bond dimension $D$ in one dimension → the state | Sample: $\mathrm{poly}(n, D)$ copies, local measurements only | poly | $O(nD^2)$ | 🟢 🟢 🟢; entanglement-area promise |
| **States prepared by shallow circuits** (Huang, Liu, Broughton, Kim, Anshu, Landau, McClean, STOC 2024; Landau, Liu 2024) | State | Identifying against a class: $\vert\psi\rangle = U\vert 0^n\rangle$ with $U$ of constant depth → a preparation circuit close in trace distance; on a 2D lattice in Huang et al., beyond that geometry in Landau, Liu | Sample: $\mathrm{poly}(n)$ copies, single-qubit measurements only | poly | poly | 🟢 🟢 🟢; light-cone promise |
| **Shallow circuits as unitaries** (Huang, Liu, Broughton, Kim, Anshu, Landau, McClean, STOC 2024) | Unitary | Identifying against a class: unknown constant-depth $U$ of arbitrary architecture → a circuit close to $U$ in diamond distance, via local inversions sewn into a global inverse | Sample on input–output pairs: $\mathrm{poly}(n)$ applications of $U$ to random product inputs, nonadaptive, single-qubit measurements on the outputs | poly | poly | 🟢 🟢 🟢; light-cone promise; constant depth bounds every light cone, so finding them is a polynomial dictionary, as for juntas |
| **Phase states of degree $\ell$** (Arunachalam, Bravyi, Dutt, Yoder 2023) | State; also through its preparation circuit | Identifying against a class: $\sum_x (-1)^{f(x)}\vert x\rangle$ with $\deg f \leq \ell$ → the polynomial $f$ | Sample: $\Theta(n^\ell)$ copies; Query: $O(n^{\ell-1})$ uses of the preparation circuit | poly | poly | 🟢 🟢 🟢; a proven sample-versus-query gap in the first budget |
| **Bounded gate complexity** (Zhao, Lewis, Kannan, Quek, Huang, Caro 2023) | State or unitary | Identifying against a class: states or unitaries with at most $G$ gates → an approximation | Sample: $\tilde\Theta(G)$ copies, information-theoretically | Computationally hard under cryptographic assumptions, already for polynomial $G$ | poly | 🟢 🔴 🟢; the thesis of this document in one theorem |
| **Output distributions of quantum circuits** (Hinsche et al. 2022, 2023; Nietner et al. 2023) | Classical distribution of a circuit | Identifying against a class: classical samples of $\vert\langle x\vert U\vert 0\rangle\vert^2$ → a generator for the distribution | Sample (classical outcomes of the circuit): poly | Polynomial for Clifford circuits; hard under LPN once a single $T$ gate is allowed, also on average | poly | 🟢 🔴 🟢; the same cryptographic wall as the LWE rows, on the classical side of the measurement |
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
* **Gross, Nezami, Walter (CMP 2021):** Stabilizer testing with six copies. **Arunachalam, Dutt (2024) / Chen, Gong, Ye, Zhang (2024):** tolerant versions in polynomial time.
* **Bădescu, O'Donnell (STOC 2021):** Threshold search and hypothesis selection with $O(\log M)$ copies.
* **Huang, Preskill, Soleimanifar (FOCS 2024):** Certifying almost all states with few single-qubit measurements.

**Notes on the identification rows.** Hypothesis selection at $O(\log M)$ copies comes from the *threshold search* primitive of Bădescu–O'Donnell (STOC 2021), the same tool that improved shadow tomography to $\tilde O(\log^2 M \cdot \log d/\epsilon^4)$. Agnostic tomography is the learning-theoretic analogue of agnostic PAC learning; Grewal–Iyer–Kretschmer–Liang (2024) and Chen–Gong–Ye–Zhang ("stabilizer bootstrapping", 2024) give polynomial-time algorithms for stabilizer and near-stabilizer classes, both driven by Bell difference sampling.

## Learning classes of states: the promise catalogue

Every 🟢 🟢 🟢 row in the identifying and searching tables names a class. Listed by the structure that makes decoding cheap, with the paper that proved it.

* **Stabilizer states** (subgroup structure): Aaronson, Gottesman (2004) with $O(n)$ collective or $O(n^2)$ single-copy measurements; Montanaro (2017) with $O(n)$ two-copy Bell samples; Rocchetto (2018) in the PAC model; Low (2009) for Clifford unitaries; Allcock, Doriguello, Ivanyos, Santha (2024) on qudits, where Bell sampling breaks.
* **Few non-Clifford gates** (magic as the dial): Lai, Cheng (2022); Grewal, Iyer, Kretschmer, Liang (2023); Leone, Oliviero, Hamma (Quantum 2024); Hangleiter, Gullans (PRL 2024). Cost $\mathrm{poly}(n, 2^t)$ in copies and time.
* **Agnostic and tolerant versions**: Grewal, Iyer, Kretschmer, Liang (2024) for stabilizer product states; Chen, Gong, Ye, Zhang (2024), stabilizer bootstrapping; Arunachalam, Dutt (2024), tolerant stabilizer testing in polynomial time. Both driven by Bell difference sampling, whose group-theoretic origin is the Clifford Schur–Weyl duality of Gross, Nezami, Walter (2021).
* **Gaussian and near-Gaussian states** (the continuous-variable analogue of stabilizer structure): Aaronson, Grewal (2023) for free fermions; Mele, Herasymenko (2024) with $t$ non-Gaussian gates; Mele et al. (2024) for bosonic and continuous-variable states with bounded energy. Displacement operators are the discrete shadow of this family.
* **Matrix product and finitely correlated states** (area-law entanglement): Cramer et al. (Nat. Commun. 2010); Fanizza, Galke, Lumbreras, Muñoz-Gil, Winter (2023) with stability guarantees.
* **Shallow-circuit states and circuits** (light cones): Huang, Liu, Broughton, Kim, Anshu, Landau, McClean (STOC 2024) learn states $U\vert 0^n\rangle$ from copies with single-qubit measurements, and unknown constant-depth unitaries of arbitrary architecture from random product inputs, which is sample access to input–output pairs; both in polynomial time. The technique is local inversion: learn, for each qubit, a local unitary that undoes $U$ there, then sew these into a global inverse; the landscape of each local problem is benign, which is what makes the time budget polynomial. Landau, Liu (2024) extend the state result beyond the 2D lattice.
* **Phase states of bounded degree** (algebraic structure): Arunachalam, Bravyi, Dutt, Yoder (TQC 2023), $\Theta(n^\ell)$ copies against $O(n^{\ell-1})$ queries, the cleanest proven sample-versus-query separation.
* **Juntas and low-degree objects** (few relevant qubits, few relevant Paulis): Chen, Nadimpalli, Yuen (SODA 2023); Arunachalam, Dutt, Escudero Gutiérrez (2024).
* **Bounded gate complexity** (the class that is sample-easy and time-hard): Zhao, Lewis, Kannan, Quek, Huang, Caro (PRX Quantum 2024).

The catalogue reads as a list of promises, and that is the point of the tables: outside of it, no polynomial-time learner is known, and the LWE, pseudorandomness, and gate-complexity results say that none should be expected in general.

<br>

# Identifying (Paper)

## Learning Shallow Quantum Circuits (arXiv:2305.13409v5)

Die Arbeit von **Hsin-Yuan Huang et al.**, erschienen unter dem Titel *„Learning Shallow Quantum Circuits“* auf dem Symposium on Theory of Computing (STOC 2024), stellt einen bedeutenden Durchbruch in der Quantenkomplexitätstheorie und dem Quanten-Maschinellen-Lernen dar. Die Autoren präsentieren den ersten **effizienten klassischen Algorithmus in Polynomialzeit**, um die vollständige Beschreibung unbekannter, flacher Quantenschaltkreise (engl. *shallow quantum circuits*) zu rekonstruieren.

### Das Problem

Bisherige klassische Algorithmen scheiterten daran, flache Quantenschaltkreise (Schaltkreise mit konstanter Tiefe) effizient zu lernen. Da solche Schaltkreise Quantenzustände und Verteilungen erzeugen können, die klassisch extrem schwer zu simulieren oder zu sampeln sind, war unklar, ob ein Rekonstruktionsalgorithmus mit polynomieller Laufzeit überhaupt existieren kann.

* Gegeben ist ein Klassenversprechen, nämlich konstante Tiefe. Zurück kommt ein Schaltkreis aus dieser Klasse. Das ist dieselbe Form wie bei Stabilizerzuständen, Matrixproduktzuständen oder wenigen T-Gattern.
* Estimating ist es nicht, weil keine Liste von Observablen gegeben ist. Die Einzelqubit-Messdaten sind das Messprimitiv, nicht die Aufgabe.
* Searching im Sinn der Tabellen ist es auch nicht, weil kein dünner Träger zurückkommt. Bei unbekannter Architektur steckt zwar eine Suche darin: welche Qubits in welchem Lichtkegel liegen. Konstante Tiefe begrenzt aber jeden Lichtkegel auf konstante Größe. Damit gibt es nur polynomiell viele Kandidaten, derselbe Mechanismus wie bei Juntas.
* Das Paper enthält zwei Resultate mit unterschiedlichem Zugriff. Zustände aus Kopien zu lernen ist Sample-Zugriff. Ein Unitary auf selbstgewählte Produktzustände anzuwenden ist Query-Zugriff auf den Prozess. Das zweite Resultat ist damit ein echtes Literaturbeispiel für die Zelle Query × Identifying. Dort standen bisher nur Bernstein–Vazirani und meine eigene Konstruktion.

### Kernresultate der Arbeit

Das Paper liefert zwei zentrale polynomielle Algorithmen basierend auf einfachen, lokalen Messdaten:
* **Rekonstruktion des Schaltkreises (Unitary):** Ein klassischer Algorithmus lernt die mathematische Beschreibung eines völlig unbekannten $n$-Qubit-Schaltkreises $U$ mit beliebiger Architektur. Gemessen an der *Diamond Distance* erzielt der Algorithmus eine präzise Annäherung. Als Input nutzt er lediglich Single-Qubit-Messdaten der Schaltkreis-Ausgänge.
* **Zustandsrekonstruktion (State Learning):** Ein klassischer Algorithmus lernt die Beschreibung eines unbekannten $n$-Qubit-Quantenzustands $\vert{}\psi\rangle = U\vert{}0^n\rangle$, welcher durch einen flachen Schaltkreis auf einem 2D-Gitter präpariert wurde. Die Annäherung erfolgt hierbei innerhalb einer kleinen *Trace Distance* unter der Nutzung lokaler Single-Qubit-Messungen (wie z. B. Pauli-Messungen).

### Methodischer Ansatz: Lokale Inversion und „Circuit Sewing“

Die größte Herausforderung beim Lernen von Quantenschaltkreisen ist die oft nicht-konvexe Optimierungslandschaft. Huang et al. umgehen dieses Problem durch zwei innovative Techniken:

1. **Lokale Inversionen (Local Inversions):** Der Algorithmus versucht nicht, den globalen Schaltkreis auf einmal zu lösen. Stattdessen lernt er lokale Operatoren, die die Wirkung des Schaltkreises in kleinen, isolierten Regionen lokal „rückgängig machen“ (invertieren).
2. **Circuit Sewing (Schaltkreis-Vernähung):** Diese lokalen Inversionen werden mathematisch über eine clevere Methode zu einer konsistenten globalen Beschreibung des gesamten inversen Schaltkreises „zusammengenäht“.

Dadurch entsteht eine mathematische Optimierungslandschaft, die sich nachweislich **effizient und ohne lokale Minima** (Plateaus) navigieren lässt.

### Bedeutung und Anwendungen

Die Arbeit zeigt, dass die physikalische Eigenschaft der **endlichen Korrelationslänge** in flachen Schaltkreisen ausreicht, um globale Quantenstrukturen aus rein lokalen Observablen effizient zu rekonstruieren. Wichtige Anwendungsbereiche sind:

* **Charakterisierung von Quantenhardware:** Effizientes Benchmarking und die Verifizierung von Quantencomputern (Schatten-Tomographie).
* **Schaltkreiskompression (Circuit Compression):** Die Reduzierung tieferer, verrauschter Schaltkreise in äquivalente, flachere Strukturen.
* **Lernen von Quantendynamiken:** Das Verstehen komplexer Quanten-Mehrkörpersysteme durch klassische Algorithmen.

Das Paper ist im **ACM Digital Library Eintrag zu STOC 2024** sowie als Vorabversion direkt auf [arXiv:2401.10095](https://arxiv.org/abs/2401.10095?utm_source=gemini) einsehbar.

### Fragen zum Tieferbohren:

* Den genauen **Laufzeit- und Sample-Komplexitäten** (Abhängigkeiten von $n$ und der Fehlerschranke $\varepsilon$)
* Einer genaueren Erklärung der mathematischen Funktionsweise des **Circuit Sewing**
* Einem Vergleich zu nachfolgenden Arbeiten, die das Prinzip auf komplexere Gates (wie $\text{QAC}^0$) erweitert haben

---

## Quantum algorithmic measurement (Nat. Commun. 13:887, 2022)

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

Paper: [doi:10.1038/s41467-021-27922-0](https://doi.org/10.1038/s41467-021-27922-0)

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
| 2015–2017 | Spectrum testing (O'Donnell–Wright 2015) · Sample-optimal tomography $\Theta(d^2/\epsilon^2)$ (2016) · Property-testing survey (Montanaro–de Wolf 2016) · Stabilizer Bell sampling (Montanaro 2017) · Quantum PAC survey (Arunachalam–de Wolf 2017) |
| 2018–2019 | Shadow tomography (Aaronson) · Online learning of states · Pseudorandom states (Ji–Liu–Song) · Neural-network tomography (Torlai et al.) · Stabilizer PAC learning (Rocchetto) · Gentle measurement and differential privacy (Aaronson–Rothblum) · LWE easy with quantum samples (Grilo–Kerenidis–Zijlstra) · Scalable PRS (Brakerski–Shmueli) |
| 2020 | Classical shadows (Huang–Kueng–Preskill) · Entanglement necessary for property testing (Bubeck–Chen–Li) · Pauli channel estimation (Flammia–Wallman; Harper–Flammia–Wallman) · Quantum statistical queries (Arunachalam–Grilo–Yuen) |
| 2021 | Memory separations (Chen–Cotler–Huang–Li) · Clifford Schur–Weyl duality and stabilizer testing (Gross–Nezami–Walter) · Improved shadow tomography and threshold search (Bădescu–O'Donnell) · Gibbs-state Hamiltonian learning (Anshu et al.) · Power of data and information-theoretic bounds (Huang et al.) · Pseudorandomness and learning hardness (Kretschmer) · Derandomized and fermionic shadows · Certification tutorial (Kliesch–Roth) |
| 2022 | Learning from experiments, Sycamore demo (Huang et al., Science) · Provable ML on shadow data (Huang et al., Science) · Pauli-channel separation (Chen–Zhou–Seif–Jiang) · QUALM (Aharonov–Cotler–Qi) · High-temperature Hamiltonian learning in polynomial time (Haah–Kothari–Tang) · Few-T learning (Lai–Cheng) · Pseudoentanglement · Output-distribution learnability (Hinsche et al.) · Nonadaptive single-copy lower bound (Lowe–Nayak) |
| 2023 | Heisenberg-limited Hamiltonian learning (Huang–Tong–Fang–Su) · Adaptivity does not help tomography (Chen et al.) · Unitary estimation at the Heisenberg rate (Haah–Kothari–O'Donnell–Tang) · Phase states (Arunachalam–Bravyi–Dutt–Yoder) · Juntas (Chen–Nadimpalli–Yuen) · Predicting processes (Huang–Chen–Preskill) · Bounded gate complexity (Zhao et al.) · One $T$ gate makes distribution learning hard (Hinsche et al.) · Few non-Clifford gates (Grewal–Iyer–Kretschmer–Liang) · Free-fermion tomography (Aaronson–Grewal) · Noncommutative Bohnenblust–Hille (Volberg–Zhang) · Randomized-measurement review (Elben et al.) |
| 2024 | Triply efficient shadows (King–Gosset–Kothari–Babbush) · Conjugate pairs (King–Wan–McClean) · Adaptivity separations for shadow tomography (Chen–Gong–Zhang) · Agnostic tomography and stabilizer bootstrapping · Tolerant stabilizer testing (Arunachalam–Dutt) · Any-temperature Hamiltonian learning (Bakshi–Liu–Moitra–Tang) · Hamiltonian structure learning from real-time evolution (Bakshi–Liu–Moitra–Tang) · Shallow circuits in polynomial time (Huang et al.; Landau–Liu) · Qudit stabilizer learning beyond Bell sampling (Allcock et al.) · Low-degree objects · Certification with single-qubit measurements (Huang–Preskill–Soleimanifar) · Gaussian and CV state learning (Mele et al.) · AlphaQubit · State-learning survey (Anshu–Arunachalam) |
| 2025–2026 | First empirical evaluation of a two-copy triply efficient scheme (arXiv:2508.11744) · Noise-robust two-copy hardware · Physical average-case decodability · Learned decoders as algorithm discovery |

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
| **Query access** (white-box circuit, rung 3) | Amplitude estimation.<br>• **Queries**: $O(1/\epsilon)$ at the Heisenberg rate, instead of $O(1/\epsilon^2)$ samples.<br>• **Time**: poly.<br>• **Memory**: poly. | Goldreich–Levin, Kushilevitz–Mansour, sparse FFT; Bernstein–Vazirani / QFT against LWE. *Regime 3, not available at rung 2.*<br>• **Queries**: $\tilde O(k\log\vert{}V\vert{})$, resp. $\mathrm{poly}(n, 1/\tau)$.<br>• **Time**: poly.<br>• **Memory**: $O(k)$. |

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
| **3. White-box circuit** | Query (efficient in compute) | **Computational boundary:** LWE-hard localization becomes polynomial | $U$, $U^\dagger$, controlled-$U$ preparing $\rho$ | Amplitude estimation at the Heisenberg rate $1/\epsilon$; superposition queries; $\rho^*$ by conjugating every gate |

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
