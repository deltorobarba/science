
# Quantum Learning

Alexander Del Toro Barba, PhD. [Google Scholar](https://scholar.google.com/citations?hl=en&user=fddyK-wAAAAJ) $\cdot$ [LinkedIn](https://www.linkedin.com/in/deltorobarba/)


<img src="https://raw.githubusercontent.com/deltorobarba/science/main/science.JPG" alt="science">


## Learning from Quantum Experiments

### Separation: QML with Classical and Quantum Data

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


### Measurement theory vs. Learning Theory

Measurement theory answers the single-shot question: What does a measurement do to a state, and which statistics does it produce? Learning theory asks the inverse, statistical question: *What can be learned about an unknown $\rho$ from many measurements, and at what cost?* The Born rule turns the state into a sampling oracle; learning is the inverse problem.

**Definition.** Given access to copies of an unknown quantum object (state $\rho$, channel $\mathcal{E}$, Hamiltonian $H$), produced by nature, a sensor, or a quantum device: *Which* properties can a learner extract, at *what* cost in copies, classical time, and memory, and how do quantum resources (quantum memory, entangled measurements, adaptivity) change these costs?

### Objective: Triply Efficient in Sample, Time and Memory

Every quantum learning protocol is charged in three budgets, and they scale independently:
* **Access** (Sample or Query): quantum copies of $\rho$ under sampling access, oracle calls to the preparation circuit or to the process under query access (the access ladder; for processes see "What is learned"). Efficient means $\mathrm{poly}(n, \log M, 1/\epsilon)$ copies; under query access the precision term improves to $1/\epsilon$ (Heisenberg rate), the query-side version of the sample boundary.
* **Time** (classical): efficient means $\mathrm{poly}(n, M, 1/\epsilon)$ post-processing, polynomial in $M$ rather than $\log M$, since $M$ values must at least be written down.
* **Memory** (classical): efficient means $\mathrm{poly}(n)$ bits for the learned representation; a $d \times d$ hypothesis already breaks it.

**Thesis** 
* The field has charted the sample boundary in detail: exponential separations by quantum memory, adaptivity, and conjugate access are proven and partly demonstrated in hardware (see the appendix). 
* The *computational boundary* is almost uncharted, although most sample-efficient protocols fail there. 
* The reason is proof technology: Sample lower bounds come from information theory (Holevo, packing arguments) and are unconditional, hence comparatively easy to obtain. Time lower bounds need cryptographic assumptions (LWE, pseudorandom states) and are rare. One map is dense, the other nearly empty.

### What is learned: states and processes

**The object axis.** A learner can be asked about a state, a Hamiltonian, a unitary, a channel, or a classical function. This is a fourth axis next to task, access, and budgets, and it runs across the three task types rather than forming a block of its own: states appear in all three tables, and so do processes. Hamiltonians have rows in estimating for their coefficients and in searching for their structure; circuits have rows in identifying. The tables therefore carry the object as a column instead of a separate section.

**Access for processes.** Sample versus query is defined for states on the access ladder. For processes the classical distinction between random examples and membership queries supplies the definition.
* A process applied to fixed or random inputs that do not depend on earlier outcomes yields copies of a single state: the Choi state, obtained by applying the process to half of a Bell pair, or the input–output data state. That is **sample access**.
* Inputs chosen adaptively or queried in superposition, and uses of the process in controlled or inverted form, in sequences, or interleaved with control pulses, are **query access**. Heisenberg-limited learning of dynamics needs such control (Dutkiewicz, O'Brien, Schuster 2024) and is therefore query access.
* Every row sits at the **weakest access its algorithm needs**. A nonadaptive protocol on random product inputs is a sample protocol, even if the learner prepares the inputs.

**Object and access are independent.** Learning a Hamiltonian from copies of its Gibbs state learns a process from samples of a state. Learning a state through its preparation circuit learns a state by queries. Learning a channel from its Choi state learns a process from samples, with the ancilla as quantum memory.

**Where the object decides hardness: normalization.** The squared Pauli coefficients of a unitary sum to one, so Bell sampling on its Choi state returns every coefficient of size $\tau$ with probability $\tau^2$, and the heavy terms fall out directly. The squared displacement coefficients of a pure state sum to $d$, so a coefficient of size one appears with probability $1/d$. The same measurement makes searching easy for unitaries and runs into the LWE wall for states. Details in the structure-learning protocols.

### Measurement primitives as basis for Protocols for Quantum Learning

Everything protocol below is a *protocol over measurements*, not a new measurement type. The section mirrors the three tables. First the four measurement primitives from which every protocol is built, then the protocols by task type, then what cuts across all three tables: the proof technology behind the bounds, the hardness results, the learned decoders, and the surveys.

**Measurement primitives**

Four primitives, one per rung of the access ladder and one for the far end of the memory axis. Every row in the tables uses one of them.

**Single-copy randomized measurements.** Draw a random basis per copy, from single-qubit Paulis or from $n$-qubit Cliffords, measure, and store the outcome. The engine of classical shadows and of direct fidelity estimation, where Pauli expectations are importance-sampled by their weight in the target state (Flammia, Liu 2011; da Silva, Landon-Cardinal, Poulin 2011). Adaptivity is allowed, each copy is still an i.i.d. draw, and the shadow norm of the ensemble decides the cost. This is rung 1 of the access ladder and the workhorse of every hardware experiment.

**Bell sampling on two copies.** A transversal Bell measurement across two copies, $\rho\otimes\rho$ or $\rho\otimes\rho^*$, draws one Pauli or displacement operator per shot. Bell difference sampling, the XOR of two such draws from four copies, removes the unknown coset offset and is the primitive behind stabilizer learning, stabilizer testing, and agnostic tomography. Conjugate pairs turn the draw into the clean squared spectrum for every dimension $d$; on qudits with two identical copies the draw can be uniform and carry nothing. Rung 2 of the access ladder, and the primitive of this project. Details in the next subsection. Applied to the Choi state of a unitary or channel, the same measurement samples its Pauli spectrum; for processes this is the sample-access primitive.

**Collective Schur sampling.** Measure all $N$ copies at once in the Schur–Weyl basis, which projects onto irreducible representations of the symmetric and unitary groups. Spectrum estimation (Keyl, Werner 2001), spectrum testing (O'Donnell, Wright 2015), and sample-optimal tomography (Haah et al. 2017; O'Donnell, Wright 2016) live here. Quantum memory $k = N$, the far end of the memory axis, and the reason those optimal rates are not hardware rates.

**Oracle calls.** Uses of a preparation circuit $U$, its inverse and controlled versions, of the dynamics $e^{-iHt}$ interleaved with control, or of a channel in sequences or on inputs chosen adaptively or in superposition. Amplitude estimation, superposition queries, Heisenberg-limited Hamiltonian learning, and sequence-based noise learning count this budget. A process applied once to a fixed or random input is not an oracle call in this sense: it yields copies of the Choi state or of an input–output data state and belongs to the sample primitives. Rung 3 of the access ladder, where the precision rate improves to $1/\epsilon$ and where the search problems of the third table become polynomial.

### Bell sampling on two copies: the primitive behind conjugate pairs and structure learning

**Mechanism.** The $2n$-qubit Bell basis $\{(P\otimes\mathbb{1})|\Phi^+\rangle^{\otimes n}\}$ is the joint eigenbasis of all commuting $P\otimes\bar P$. A transversal Bell measurement across two copies draws one Pauli string per shot

$$P \sim \frac{|\langle\bar\psi|P|\psi\rangle|^2}{2^n}$$

A single shot carries information about the *entire* Pauli spectrum. **Subtlety:** On $\psi\otimes\psi$ one samples against the *conjugate* state $\bar\psi$. The clean spectrum $\mathrm{Tr}(P\rho)^2/2^n$ requires the pair $(\rho, \bar\rho)$. For real amplitudes both coincide (which is why demos like GHZ states).

**Consequences.** Purity and overlap $\mathrm{Tr}(\rho\sigma)$ via SWAP tests without tomography. Stabilizer states learnable from $O(n)$ Bell samples. Above all: **Pauli shadow tomography with $\Theta(n)$ copies given two-copy memory vs. $2^{\Omega(n)}$ without.** One of the strongest proven exponential quantum advantages, demonstrated in hardware. Two is the sweet spot: Almost all known gain arrives already at $k=2$.

Literature:
* **Bubeck, Chen, Li (FOCS 2020):** Entanglement necessary for optimal property testing.
* **Chen, Cotler, Huang, Li (FOCS 2021):** $\Theta(n)$ vs. $2^{\Omega(n)}$ separation with quantum memory.
* **Huang et al. (Science 2022):** Flagship separations and Sycamore demo with 40 qubits.
* **King, Wan, McClean (2024):** Exponential advantage via $(\rho, \rho^*)$ with constant memory.
* **Chen, Gong, Zhang (2024):** Separations for adaptive multi-copy shadow tomography.
* **Allcock, Doriguello, Ivanyos, Santha (2024):** Bell sampling fails on qudits, $d > 2$: the output can be uniform. Replacement measurements for stabilizer learning; the reason this project uses conjugate pairs rather than two identical copies.

**Two more separations of the same shape.** *Purity testing* (is $\rho$ pure or maximally mixed?) needs $O(1)$ copies with two-copy memory (a SWAP test) but $\Omega(2^{n/2})$ without (Chen, Cotler, Huang, Li, FOCS 2021); the memory-free lower bound also kills any single-copy route to $\mathrm{Tr}(\rho^2)$. *Pauli channel estimation*: learning all $4^n$ Pauli eigenvalues of a channel to $\pm\epsilon$ takes roughly $O(n/\epsilon^2)$ uses with ancilla-assisted entangled inputs versus $2^{\Omega(n)}$ without (Chen, Zhou, Seif, Jiang, PRA 2022), the channel version of the shadow-tomography separation. The general framework in which all of these live is **QUALM** (Aharonov, Cotler, Qi, Nat. Commun. 2022): a learner is a quantum algorithm with coherent or incoherent access to the lab, and the separations are statements about access, not about the model class.


## Searching

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

### Searching protocols

The observables are the output. Two families: structure learning from measurement data on quantum states, and the older Fourier-sampling family on quantum examples of classical functions, which shows what a favourable normalization buys.

#### Structure learning (observables as output)

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

#### Quantum PAC learning and quantum examples

The oldest access model in the field: the learner receives copies of the example state $\sum_x \sqrt{D(x)}\,\vert x, f(x)\rangle$ of a classical function $f$.

* **Bshouty, Jackson (SIAM J. Comput. 1998):** DNF learnable under the uniform distribution from quantum examples, by Fourier sampling; the first quantum learning advantage in time.
* **Servedio, Gortler (SIAM J. Comput. 2004) / Atıcı, Servedio (2005):** Equivalences and separations between quantum and classical learnability; polynomial gaps in samples, exponential gaps in time under cryptographic assumptions.
* **Aaronson (Proc. R. Soc. A 2007):** Learnability of quantum states: $O(n)$ samples to predict most measurements. **Rocchetto (2018):** stabilizer states are efficiently PAC-learnable.
* **Arunachalam, de Wolf (SIGACT 2017; JMLR 2018):** Survey, and the optimal bound $\Theta(d_{\mathrm{VC}}/\epsilon + \log(1/\delta)/\epsilon)$: quantum examples buy nothing in samples for classical concept classes.
* **Grilo, Kerenidis, Zijlstra (PRA 2019):** LWE is easy with quantum samples, via Bernstein–Vazirani on the example state.
* **Arunachalam, Grilo, Yuen (2020):** Quantum statistical queries, a rung below samples on the access ladder: the learner sees only expectation values to a tolerance.

**Where there is provably no advantage.** For PAC learning a *classical* concept class from quantum examples $\sum_x \sqrt{D(x)}\,|x, c(x)\rangle$, Arunachalam–de Wolf (JMLR 2018) showed the sample complexity is $\Theta(d_{\mathrm{VC}}/\epsilon + \log(1/\delta)/\epsilon)$, identical to the classical bound up to constants. Quantum examples buy nothing in samples for classical targets; the advantages in this document all sit in the bottom row or in *time*, never in PAC sample complexity for classical functions.


## Estimating

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

### Estimating protocols

Observables are the input. The baseline is full tomography; every protocol below exists to escape its scaling, by changing the question (shadows), by adding a resource (two-copy memory, queries), or by naming a promise (locality, a phase, a Hamiltonian family).

#### Full QST: the exponential baseline

Reconstructs all $d^2$ parameters from an informationally complete measurement set (DV: all $3^n$ Pauli bases or a single SIC-POVM; CV: homodyne scan and inverse Radon transform to the Wigner function). Cost $\Theta(d^2/\epsilon^2) = \Theta(4^n/\epsilon^2)$ even with entangled measurements. Everything else exists to escape this scaling.

* **Haah et al. / O'Donnell–Wright (STOC 2016):** $\Theta(d^2/\epsilon^2)$ optimal entangled tomography.
* **Chen et al. (2022):** $\Theta(d^3/\epsilon^2)$ single-copy lower bound, proves the gap to entangled measurements.
* **Keyl, Werner (2001) / O'Donnell, Wright (2015):** Spectrum estimation and spectrum testing by Schur sampling, the collective-measurement end of the memory axis.
* **Lowe, Nayak (2022) / Chen, Huang, Li, Liu, Sellke (FOCS 2023):** $\Omega(d^3/\epsilon^2)$ for single-copy tomography, first nonadaptive, then even adaptive: adaptivity does not help for full tomography.
* **Haah, Kothari, O'Donnell, Tang (FOCS 2023):** Unitary estimation with $\Theta(d^2/\epsilon)$ queries in diamond distance, Heisenberg rate at tomography scale.

**Structured escapes before shadows.** Two routes beat $d^2$ by *assuming* structure rather than by changing the question: **compressed-sensing tomography** (Gross, Liu, Flammia, Becker, Eisert, PRL 2010) recovers a rank-$r$ state from $O(r\,d\log^2 d)$ random Pauli expectation values via nuclear-norm minimization, and **MPS tomography** (Cramer et al., Nat. Commun. 2010) reconstructs 1D states of bounded bond dimension from local reduced density matrices in $\mathrm{poly}(n)$. Both are the tomographic analogue of the "low rank ⇒ easy" theme that also drives dequantization arguments: the exponential baseline is a worst-case statement over *all* states.

#### Shadow tomography and classical shadows (observables as input)

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

#### Continuous-variable systems: CV shadows and Gaussian learning

The displacement operators of this project are the finite Weyl–Heisenberg group; the continuous-variable Weyl group is their infinite-dimensional parent, and the characteristic function $\chi(\alpha) = \mathrm{Tr}(D(\alpha)\rho)$ is the CV displacement spectrum. Learning it is the CV version of the searching and estimating rows.

* **Homodyne tomography** (Vogel, Risken 1989; Smithey et al. 1993): a quadrature scan and an inverse Radon transform reconstruct the Wigner function, the CV baseline, with no finite dimension to count against; energy bounds take the place of $d$.
* **CV classical shadows** (Becker, Datta, Lami, Rouzé 2024; Gandhari et al. 2024): randomized Gaussian measurements with rigorous error bounds under an energy or photon-number constraint; the shadow-norm role is played by the energy.
* **Gaussian and near-Gaussian state learning** (Mele et al. 2024; Bittel et al. 2024): bosonic Gaussian states are learned from their covariance matrix and displacement vector in polynomial time in the number of modes; $t$ non-Gaussian gates cost $2^t$, the bosonic mirror of the magic dial. Fermionic Gaussian states behave the same way (Aaronson, Grewal 2023; Mele, Herasymenko 2024).
* **The bridge to this project.** Heterodyne outcomes sample the Husimi function, whose Fourier transform is the characteristic function; the CV analogue of the Bell record is therefore a heterodyne record, and the CV analogue of the search for a sparse displacement support is the search for a few dominant $\alpha$ in $\chi(\alpha)$. Whether an LWE-type wall exists there is as open as the cyclic-qudit question in the searching table.

#### Estimating processes: Hamiltonian coefficients, channels, unitaries

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


## Identifying

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

### Identifying protocols

Candidate states, or a class, are the input. Two hypotheses first, then many, then a class with or without a promise, then the one-bit tasks of testing and certification.

#### State discrimination: Helstrom vs. USD

Given $\rho_0, \rho_1$ with priors $p_0, p_1$: Which one is present? Two strategies with different notions of error.

* **Helstrom (minimum error):** Answer in every run, average error minimized. Projective measurement onto the sign spectrum of $p_0\rho_0 - p_1\rho_1$:

$$P_{\text{err}}^{\min} = \tfrac{1}{2}\Big(1 - \big\|p_0\rho_0 - p_1\rho_1\big\|_1\Big)$$

* **USD (unambiguous):** Third outcome "undecided", decided answers never wrong. Requires a genuine POVM; the price is the abstention probability, minimally $|\langle\psi_0|\psi_1\rangle|$.

**Many copies and the distance zoo.** With $n$ copies the Helstrom error decays exponentially, $P_{\mathrm{err}} \sim e^{-n\,\xi_{\mathrm{QCB}}}$ with the **quantum Chernoff exponent** $\xi_{\mathrm{QCB}} = -\log\min_{0\leq s\leq 1}\mathrm{Tr}(\rho_0^s\rho_1^{1-s})$ (Audenaert et al., PRL 2007). The single-shot quantity is the trace distance $D = \frac12\|\rho_0-\rho_1\|_1$; it is sandwiched by the fidelity via Fuchs–van de Graaf, $1 - F \leq D \leq \sqrt{1-F^2}$, which is why tomography guarantees are quoted interchangeably in either metric. ⚠️ For *learning* (many hypotheses, not two) the relevant quantity is not $D$ but the packing number of the hypothesis class in $D$; that is where the $d^2$ of full tomography comes from.

#### Property testing, certification, hypothesis selection

Tasks whose answer is one bit or one index; the identifying column.

* **Montanaro, de Wolf (2016):** Survey of quantum property testing.
* **O'Donnell, Wright (STOC 2015) / Bubeck, Chen, Li (FOCS 2020) / Chen, Cotler, Huang, Li (FOCS 2021):** Spectrum, mixedness, and purity testing; where entanglement across copies is necessary.
* **Gross, Nezami, Walter (CMP 2021):** Stabilizer testing with six copies. **Arunachalam, Dutt (2024) / Chen, Gong, Ye, Zhang (2024):** tolerant versions in polynomial time.
* **Bădescu, O'Donnell (STOC 2021):** Threshold search and hypothesis selection with $O(\log M)$ copies.
* **Huang, Preskill, Soleimanifar (FOCS 2024):** Certifying almost all states with few single-qubit measurements.

**Notes on the identification rows.** Hypothesis selection at $O(\log M)$ copies comes from the *threshold search* primitive of Bădescu–O'Donnell (STOC 2021), the same tool that improved shadow tomography to $\tilde O(\log^2 M \cdot \log d/\epsilon^4)$. Agnostic tomography is the learning-theoretic analogue of agnostic PAC learning; Grewal–Iyer–Kretschmer–Liang (2024) and Chen–Gong–Ye–Zhang ("stabilizer bootstrapping", 2024) give polynomial-time algorithms for stabilizer and near-stabilizer classes, both driven by Bell difference sampling.

#### Learning classes of states: the promise catalogue

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




## Cross-cutting: bounds, hardness, decoders, surveys

### Where the bounds come from: proof technology

The thesis of the overview, a dense sample map and a nearly empty time map, has a concrete cause: the two kinds of bounds are proved with different tools, and only one kind is unconditional.

**Sample lower bounds, unconditional.**
* *Holevo and packing.* $n$ qubits carry at most $n$ bits; a hypothesis class with $2^{\Theta(N)}$ well-separated members needs $\Omega(N)$ copies. This gives $\Omega(n)$ for stabilizer states, $\Omega(d^2/\epsilon^2)$ for full tomography, and $\Omega(d_{\mathrm{VC}}/\epsilon)$ for PAC learning from quantum examples (Arunachalam, de Wolf 2018).
* *The tree method for bounded memory.* A learner without quantum memory induces a tree of single-copy outcomes; bounding the likelihood ratio between a random hypothesis and the maximally mixed state along every root-to-leaf path gives $2^{\Omega(n)}$ for Pauli shadow tomography, purity testing, and channel learning without memory (Bubeck, Chen, Li 2020; Chen, Cotler, Huang, Li 2021; Chen, Zhou, Seif, Jiang 2022) and $\Omega(d^3/\epsilon^2)$ for single-copy tomography, adaptive or not (Lowe, Nayak 2022; Chen, Huang, Li, Liu, Sellke 2023). The method interpolates in the number $k$ of memory qubits.
* *Group theory.* Schur–Weyl duality for the unitary group gives the optimal tomography rates; Schur–Weyl duality for the Clifford group (Gross, Nezami, Walter 2021) explains why four copies expose a stabilizer group and why the characteristic distribution of a pure state is its own symplectic Fourier transform.

**Sample upper bounds.**
* *Hoeffding plus a union bound* over a candidate list: character means over a dictionary, all $d^2$ squared magnitudes from one Bell record, Hamiltonian coefficients from local marginals.
* *Median of means and the shadow norm* for classical shadows; *gentle measurement* for shadow tomography (Winter 1999; Aaronson 2004, 2018), which is the same lemma as differential privacy (Aaronson, Rothblum 2019); *threshold search* for hypothesis selection (Bădescu, O'Donnell 2021); *matrix multiplicative weights* as the hypothesis update behind shadow and online learning.
* *Fourier sampling and coset differencing*: Bell sampling, Bell difference sampling, and quantum examples deliver random elements of a subspace or coset, and Gaussian elimination finishes (Montanaro 2017; Bshouty, Jackson 1998; Simon 1994).

**Time lower bounds, conditional.** Every known one is a reduction from a cryptographic assumption. LWE gives the displacement instance of this project; LPN gives the hardness of learning output distributions with a single $T$ gate (Hinsche et al. 2023) and the classical mirror of Bell sampling; one-way functions give pseudorandom states (Ji, Liu, Song 2018; Brakerski, Shmueli 2019) and from them the hardness of learning states of bounded gate complexity (Zhao et al. 2023) and of distinguishing entanglement (Aaronson et al. 2022). No unconditional time lower bound for a natural quantum learning task is known, which is why the time map is empty where the sample map is dense.

**Time upper bounds.** Each one names the structure it uses: linear algebra over $\mathbb{F}_2$ or $\mathbb{Z}_d$ for subgroups, enumeration for dictionaries, a best-first heap for factorized spectra, the noncommutative Bohnenblust–Hille inequality for low-degree objects (Volberg, Zhang 2023), light cones for shallow circuits, cluster expansions at high temperature and a different route at any constant temperature for Gibbs-state Hamiltonian learning (Haah, Kothari, Tang 2022; Bakshi, Liu, Moitra, Tang 2024), and graph colorings of commutation structure for triply efficient shadow tomography (King, Gosset, Kothari, Babbush 2024). The learned decoder of this project is an attempt to obtain such a bound empirically where no structure has been named.

### Computational lens: hardness and pseudorandomness

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

### Machine-learned decoders

Classical neural decoders on shadow data (bottom-left quadrant) as empirical heuristics for classically hard decoding tasks.

* **Torlai et al. (Nat. Phys. 2018):** Neural-network QST.
* **Huang, Kueng, Torlai, Albert, Preskill (Science 2022):** Provable generalization bounds for ML on shadow data.
* **Huang, Preskill, Soleimanifar (2024):** State certification via single-qubit shadow relaxations.
* **Carrasquilla, Torlai, Melko, Aolita (Nat. Mach. Intell. 2019):** Generative models as state representations fit to measurement data.
* **Lewis et al. (Nat. Commun. 2024) / Onorati, Rouzé, França, Watson (2023):** Provable prediction of ground and thermal state properties within a phase, down to $O(\log n)$ training states.
* **Bausch et al. (Nature 2024):** AlphaQubit, the learned surface-code decoder.

**Representation side and the decoding target.** The representational cousin of a learned decoder is the **neural quantum state** (Carleo, Troyer, Science 2017): a network as the ansatz $\psi_\theta(s)$, trained variationally rather than from measurement data. The two meet in Torlai et al. (2018), where the network is fit to measurement statistics. On the transfer to error correction promised in the positioning section: Google's **AlphaQubit** (Bausch et al., Nature 2024) is a transformer decoder trained on syndrome data that outperforms tensor-network and matching decoders on Sycamore surface-code experiments, the existence proof that a learned decoder can beat hand-built combinatorics on real hardware data.

### Surveys and timeline

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

## Open Frontiers (Research Questions)

* **Mapping the decodable classes.** Between "subgroup-easy" (linear algebra) and "LWE-hard" lies uncharted territory. The same state moves from the easy to the hard regime by turning up a noise parameter. Open: Does the hardness reduction transfer from the tensor-product basis to the cyclic single-qudit basis?
* **What learned decoders implicitly find.** If a decoder works on a class with no known efficient algorithm, it may have found one. ML as a tool for algorithm discovery; what is missing is a metric that predicts generalization across state distributions.
* **Hardware realism with two copies.** Approximate matched filters (probe gain $\kappa < 1$, overhead $\kappa^{-2}$) make protocols graceful against preparation, crosstalk, and measurement errors. The practically most relevant axis.
* **Average case instead of worst case.** The hardness results are adversarial. Natural states (ground states of local Hamiltonians, thermal states) could be generically decodable: from the cryptography perspective to the physics perspective.
* **Memory between zero and two.** The separations are stated at $k=0$ versus $k=2$ copies. Chen–Cotler–Huang–Li also treat a learner with $k$ qubits of quantum memory and find that the sample complexity interpolates smoothly; what is missing is the *protocol* side: which structured tasks become tractable at a fixed small memory budget short of a full second copy, e.g. with a few ancilla qubits per shot as in the Pauli-channel case.


## Appendix: Reading the tables

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

## Positioning of the own project

* **Field:** Quantum advantages in learning physical systems from measurement data, with minimal quantum memory (never more than two copies).
* **Approach:** *Machine-learned decoders for quantum measurement data.* A trained model replaces hand-built combinatorics (graph coloring, matrix multiplicative weights) and exploits the structure of the state class. Transfers to Hamiltonian learning, noise characterization, error-correction decoders.
* **Contribution:** Computationally efficient **structure learning** of sparse displacement spectra from two-copy Bell measurements. Triply efficient, posed as a promise problem, with provable instances (dictionary and subgroup classes) and a provable limit (LWE hardness of generic localization).
* **Structure:** Every protocol splits into a *quantum frontend* (which measurement on how many copies) and a *classical decoder*. The error factorizes into localization and estimation. Conjugate Bell pairs in front, learned CNN decoder plus sequential sign integrator behind.
* **Cell in the quadrant:** sampling access at rung 2, searching task: the hard corner. The provable instances (dictionary, subgroup) are the two promises that make the corner decodable; the LWE limit is the statement that sparsity alone is not a third one. The conjecture places a uniformly random top-$k$ support on the decodable side without proof, and the learned decoder is its empirical candidate.


## Appendix: the axes behind the tables

The three tables are the primary object. This appendix keeps the three axes that generate them, for readers who want the coordinate system: the quadrant of access against task, the access ladder, and the measurement-power axis.

### The access-by-task quadrant

Crossing the access axis with the task axis gives four cells. All four are populated, and all four are efficient in the first budget, copies or queries: the quadrant maps only the computational boundary. Drawing them makes visible what the tables hide when read separately: computational hardness lives in exactly one cell, and it needs both restrictions at once. The rows of the three tables, grouped by access and task type, are the examples behind each cell; the identifying column is merged into estimating here because it behaves like estimating in every budget.

| | **Estimating / Identifying** (a list is given) | **Searching** (observables are output) |
| --- | --- | --- |
| **Sampling access** (i.i.d. copies, rungs 1–2) | Shadow tomography, classical shadows; with conjugate pairs the character mean over a dictionary of size $M$. *Regime 1.*<br>• **Copies**: $\mathrm{poly}(\log M, n, 1/\epsilon)$; with conjugate pairs $N = O(g^{-2}\log(M/\delta))$ for gap $g$.<br>• **Time**: $\mathrm{poly}(M)$ for an explicit list; $\exp(n)$ when a dense hypothesis is kept (general shadow tomography).<br>• **Memory**: $O(M)$ values for the list; $\exp(n)$ for the dense hypothesis. | Structure learning from Bell samples. *Regime 2 where provable.* **This project.**<br>• **Copies**: $O(\log d/\epsilon^4)$; a union bound over all $d^2$ coefficients stays logarithmic in $d$.<br>• **Time**: generic localization **LWE-hard**; polynomial under subgroup support via Gaussian elimination (Montanaro); empirical in the conjectured class.<br>• **Memory**: $O(k \log d)$ bits, the sparse list. |
| **Query access** (white-box circuit, rung 3) | Amplitude estimation.<br>• **Queries**: $O(1/\epsilon)$ at the Heisenberg rate, instead of $O(1/\epsilon^2)$ samples.<br>• **Time**: poly.<br>• **Memory**: poly. | Goldreich–Levin, Kushilevitz–Mansour, sparse FFT; Bernstein–Vazirani / QFT against LWE. *Regime 3, not available at rung 2.*<br>• **Queries**: $\tilde O(k\log\vert{}V\vert{})$, resp. $\mathrm{poly}(n, 1/\tau)$.<br>• **Time**: poly.<br>• **Memory**: $O(k)$. |

Three statements carry the synthesis.

1. **Only one cell is hard, and it is hard in time alone.** The first line of every cell is green: Hoeffding plus a union bound over all $d^2$ coefficients costs $O(\log d/\epsilon^4)$ copies, the information is there. The memory line of the hard cell is green as well: the sparse list fits. The single red entry in the table is the time line of the sampling-searching cell, and the green memory entry next to it shows that the hardness is not a representation problem but a decoder problem, a cryptographic average-case statement. This is why the budgets of the overview must be kept apart before the quadrant is read: "sample-efficient" and "hard" are statements about different budgets, and both hold in the same cell. The estimating column carries its own split, visible in its time and memory lines: an explicit polynomial-size list is efficient, which is exactly the dictionary promise, while a dense hypothesis is not.

2. **The hard cell is left to the left only by a promise, and never downward.** The row cannot be changed: nature delivers copies. The column changes only through a promise about the state. A dictionary promise moves the task to the left (Regime 1). A subgroup promise keeps the task in the cell but turns decoding into linear algebra (Regime 2). Query access would move downward (Regime 3), but it is not available at rung 2. The three provable escape routes are therefore two promises and one access change. The conjecture of this project claims that a *uniformly random* top-$k$ support is a third promise that suffices, although it falls under none of the three.

3. **Adaptivity does not change the row.** Phase 2 of the own protocol chooses probes adaptively, but each probe consumes fresh i.i.d. copies. For the diagonal LWE instance behind the hardness theorem, any measurement, adaptive or not, is classical post-processing of i.i.d. draws from a classical distribution. A reader who takes Phase 2 for query access will conclude, wrongly, that the hardness has been circumvented. It has not; it has been *promised away* for a restricted state class, which is what the promise-problem formulation of the positioning section states.

**The classical instance of the same quadrant.** Goldreich–Levin sits in the query-searching cell, Learning Parity with Noise in the sampling-searching cell (see the classical mirror below). The thirty-year-old Boolean dichotomy is the same picture with the same hard corner; LWE is its lattice generalization and Bell sampling its quantum instance.

### Access: sampling versus query

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

### Measurement power: quantum memory and adaptivity

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
