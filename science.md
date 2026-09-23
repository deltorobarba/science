
# Quantum Learning

**Learning from Quantum Experiments**

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
* **Allcock, Doriguello, Ivanyos, Santha (2024):** Bell sampling fails on qudits, $d > 2$: Bell difference sampling on four copies of a stabilizer state returns only $\mathrm{col}(V)\times\mathrm{col}(W)$, uniform when both have full rank. With the conjugate, Bell sampling on $\vert S\rangle\vert S^*\rangle$ learns the state from $O(n)$ copies for every $d$; without it, a hidden-quadratic-phase algorithm does for $d$ prime. The reason this project uses conjugate pairs rather than two identical copies.

**Two more separations of the same shape.** *Purity testing* (is $\rho$ pure or maximally mixed?) needs $O(1)$ copies with two-copy memory (a SWAP test) but $\Omega(2^{n/2})$ without (Chen, Cotler, Huang, Li, FOCS 2021); the memory-free lower bound also kills any single-copy route to $\mathrm{Tr}(\rho^2)$. *Pauli channel estimation*: learning all $4^n$ Pauli eigenvalues of a channel to $\pm\epsilon$ takes roughly $O(n/\epsilon^2)$ uses with ancilla-assisted entangled inputs versus $2^{\Omega(n)}$ without (Chen, Zhou, Seif, Jiang, PRA 2022), the channel version of the shadow-tomography separation. The general framework in which all of these live is **QUALM** (Aharonov, Cotler, Qi, Nat. Commun. 2022): an experiment is a quantum algorithm that calls an unknown *lab oracle*, with *coherent* access (outputs of several calls held and measured jointly) or *incoherent* access (each output measured completely before the next call, adaptivity allowed). The separations above are statements about this coherence, which is the memory axis of this document, not about the model class; which oracle nature supplies, copies of $\rho$, pairs $\rho\otimes\rho^*$, or the preparation circuit, is the separate access ladder. On qubits the SWAP test behind these separations is a coarse-grained Bell measurement: SWAP is diagonal in the Bell basis, with eigenvalue $(-1)^{\#Y}$ on the outcome $P$. On qudits with $d>2$ it is not; see the QUALM summary under Identifying (Papers).


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
* **Success criterion:** Conjugate Bell access, a signal-to-noise margin, and structural decodability under sample access. The first two secure the copies, only the third secures the time. Failures separate into statistical detectability, computational search, and identifiability at ties (see "The repaired success criterion" under Searching).
* **Cell in the quadrant:** sampling access at rung 2, searching task: the hard corner. The provable instances (dictionary, subgroup) are the two promises that make the corner decodable; the LWE limit is the statement that sparsity alone is not a third one. The conjecture places a uniformly random top-$k$ support on the decodable side without proof, and the learned decoder is its empirical candidate.

