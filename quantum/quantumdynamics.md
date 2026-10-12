# Quantum Dynamics

## Quantum Simulation

Every simulation method in physics and chemistry can be classified along three axes:
* **Model**: **Classical:** Neglects electrons; atoms are approximated as point masses connected by springs (empirical force fields). **Quantum:** Explicitly accounts for electrons, orbitals, and many-body correlation.
* **Computing**: Computation runs either on classical hardware (CPU/GPU/supercomputer) or on qubit processors.
* **Type**: **Static (ground state / eigenvalue problem):** $\hat{H}\vert{}\psi\rangle = E\vert{}\psi\rangle$. Energy optimization: For eigenstates, $\Psi(t) = \psi e^{-iEt/\hbar}$; probability densities $\vert{}\Psi(t)\vert{}^2$ are time-invariant. Solution approach: Search for global minima on energy hypersurfaces via the Rayleigh-Ritz variational principle or VQE. **Dynamic (time evolution):** $i\hbar\,\partial_t\Psi = \hat{H}\Psi$. Propagation: No general variational principle, no forward-in-time shortcut theorem. Required for non-equilibrium chemistry, bond breaking in collisions, non-adiabatic excitations, and quantum chaos. 

Core axiom: For static problems, QC stores information. In dynamical evolution, QC is the physical Hilbert space.

| Model / Computing | **Static** (optimization via variational principle, states) | **Dynamic** (explicit time propagation, time evolution) |
| --- | --- | --- |
| **Classical Model / Classical Hardware** | **Docking, Energy Minimization:** Geometric fitting (AutoDock, Rosetta) | **Molecular Dynamics (MD):** $F = ma$, classical trajectories via force fields (GROMACS, NAMD, AMBER) |
| **Classical Model / Quantum Hardware** | Discrete combinatorial optimization (e.g. conformational search via QAOA / annealing) | **Linear PDE Solvers:** Navier-Stokes via the HHL algorithm, flow and weather models |
| **Quantum Model / Classical Hardware** | **HF, DFT, Post-HF:** $\hat{H}\vert{}\psi\rangle = E\vert{}\psi\rangle$<br>• HF ignores correlation<br>• DFT approximates via the electron density $\rho$<br>• Post-HF (CC, CI) exact, but exponential in $N$ | **TD-DFT & Wave Packet Dynamics:** Excitations, spectra, fluorescence.<br>• Exact propagation $e^{-i\hat{H}t/\hbar}\vert{}\Psi(0)\rangle$ scales exponentially in $N$ |
| **Quantum Model / Quantum Hardware** | **VQE (NISQ) & QPE (Fault-Tolerant):** Determination of the correlation energy via parametrized entanglement / phase measurement | **Hamiltonian Simulation:** Coherent time evolution $e^{-iHt}\vert{}\psi(0)\rangle$ in the $2^n$-dimensional Hilbert space via Trotter, QSVT, or Shadow Simulation |


### Static Quantum Chemistry

* **Correlation Problem**: 
  * Only the 1-electron hydrogen atom is analytically solvable; from two electrons on, the Coulomb repulsion forces approximation methods. 
  * *Born-Oppenheimer approximation:* Nuclei are treated as fixed on electronic timescales $\implies$ potential energy surface (PES). 
  * *Rayleigh-Ritz principle:* $\langle\psi\vert{}H\vert{}\psi\rangle \geq E_0$ yields upper bounds for the ground state.
* **Strategies for static quantum chemistry**
  * **Hartree–Fock (HF)**. Treatment of Electron Correlation: Mean field; neglects correlation entirely. Scaling: Cheap: Polynomial ($O(N^4)$ to $O(N^3)$)
  * **Density Functional Theory (DFT)**. Treatment of Electron Correlation: Approximated via exchange-correlation functionals of the density $\rho$. Scaling: Cheap: Favorable polynomial scaling
  * **Post-HF (Coupled Cluster, CI)**. Treatment of Electron Correlation: Systematically exact treatment of correlation. Scaling: Exponential in $N$; FCI scales combinatorially with $\binom{M}{N}$
  * **Variational Quantum Eigensolver (VQE)**. Treatment of Electron Correlation: Directly on the qubit register via many-body entanglement. Scaling: NISQ heuristic; target: strongly correlated molecules
* **Chemical Accuracy & Scaling Limits**
  * *Target precision:* $1\text{ kcal/mol} \approx 1.6\text{ mHa} \approx 43\text{ meV}$ (needed for reaction rates at room temperature to within an order of magnitude).
  * *Limits of classical methods:* The gold standard $\text{CCSD(T)}$ scales as $O(N^7)$ and fails for strong static correlation (multireference systems, transition-metal catalysis such as FeMoco).
* **Fault-Tolerant Quantum Phase Estimation (QPE)**
  * Replaces VQE on fault-tolerant hardware; uses block-encoded Hamiltonians.
  * Achieves Heisenberg-limited precision with respect to oracle queries.
  * **The Overlap Bottleneck:** If the overlap between the classical initial state $\vert{}\phi\rangle$ and the ground state $\vert{}\psi_0\rangle$ is exponentially small ($\vert{}\langle\phi\vert{}\psi_0\rangle\vert{}^2 \leq 2^{-\Omega(n)}$), QPE requires exponentially many repetitions (Guided Local Hamiltonian Problem).

### Dynamic Simulation on Quantum Computers

* **Fundamental Problem**
  * Nature switches on all terms simultaneously; quantum gates run sequentially.
  * Since terms do not commute ($[A, B] \neq 0$), we have: $e^{-i(A+B)t} \neq e^{-iAt}e^{-iBt}$.
* **Propagation Strategies**
  * **Trotter-Suzuki** (and qDRIFT) to Discretize Time. Decomposed Element: Physical time $t$ split into $r$ time steps. Ideal for **NISQ** (low depth, no ancillas).
  * **Qubitization** (and QSVT) to transform the Spectrum*. Decomposed Element: Continuous energy spectrum mapped to rotation angles ($E_k = \lambda\cos\theta_k$). Ideal for **Fault-Tolerant** (ancilla register, block encoding).
  * **Shadow Simulation** to reduce the space. Decomposed Element: Full state space ($2^n$) projected onto $M$ observable expectation values. Ideal for **NISQ & Fault-Tolerant** (requires algebraic closure).
* **Bounds & Fast-Forwarding**
  * *No-fast-forwarding theorem:* The linear dependence of the runtime on the time $t$ is strictly optimal for generic Hamiltonians; additive term $\log(1/\epsilon)$ for function approximations.
  * *Exceptions:* Fast-forwarding ($t \ll \Vert{}H\Vert{}t$) is only possible for special structures (e.g. commuting terms, quadratic fermionic systems).
**Open Quantum Systems: Non-Unitary Dynamics**
* **From Unitaries to Quantum Channels**
  * Isolated systems: Unitary evolution via the Schrödinger equation ($U^\dagger U = \mathbb{1}$, reversibility, purity is preserved).
  * Coupled systems (bath, measurement, dissipation): Non-unitary; described by **CPTP maps** (completely positive, trace-preserving maps).
  * *Kraus representation:* $\mathcal{E}(\rho) = \sum_k K_k \rho K_k^\dagger$ with $\sum_k K_k^\dagger K_k = \mathbb{1}$.
  * *Stinespring dilation:* Embeds any CPTP dynamics unitarily into a larger total space (system + ancilla environment).
* **GKSL-Lindblad Master Equation (Markovian Regime)** $\frac{d\rho}{dt} = -i[H,\rho] + \sum_k \gamma_k \left( L_k \rho L_k^\dagger - \frac{1}{2}\{L_k^\dagger L_k, \rho\} \right)$
  * *Coherent term ($-i[H,\rho]$):* Unitary evolution generated by the system Hamiltonian.
  * *Dissipative term ($L_k$):* Lindblad jump operators model relaxation processes:
    * $T_1$ (energy relaxation / amplitude damping, e.g. spontaneous emission).
    * $T_2$ (phase damping / elastic scattering).
* **Hardware Realization of Open Dynamics**
  * *NISQ:* Quantum trajectories / Monte Carlo wavefunction (MCWF) with stochastic collapses and mid-circuit resets.
  * *Fault-Tolerant:* Block encoding of Kraus and Lindblad operators via LCU methods (Linear Combinations of Unitaries); scales in time as $\mathcal{O}(t\,\mathrm{polylog}(t/\epsilon))$.
  * *Non-Markovian dynamics:* Environments with memory effects and strong entanglement fall outside the Lindblad formalism and form a current research frontier.

<br>

## Quantum Dynamics (Chaos, Scrambling & OTOCs)

### Fundamentals & Core Concepts

* **Operator Growth in the Heisenberg Picture**
  * Time evolution: $W(t) = e^{iHt}We^{-iHt}$ spreads from a local operator into a highly non-local superposition of Pauli strings.
  * Chaos diagnostics require the exact unitary dynamics; without $e^{-iHt}$, neither $W(t)$ nor OTOCs exist.
  * Growth proceeds along three dimensions: **Rate** (time), **Reach** (space), and **Depth** (operator space).
* **Model System: Mixed-Field Ising Model (MFIM)**
  * Hamiltonian: $H = \sum_i Z_i Z_{i+1} + h_x\sum_i X_i + h_z\sum_i Z_i$.
  * Integrable limit ($h_z = 0$): Ballistic wave packets, Poincaré recurrence, no scrambling.
  * Chaotic case ($h_z \neq 0$, e.g. $0.5$): Breaks integrability, leads to diffusive operator scrambling.
  * Simulation setup: OTOC probe ($Z$ operator per lattice site) vs. butterfly perturbation ($X$ gate at the edge) for a direct comparison of ballistic spreading and chaotic decay.

### Out-of-Time-Order Correlator (OTOC)

* **Definition as a Four-Point Function**
  * $C(t) = \big\langle [W(t), V(0)]^\dagger [W(t), V(0)] \big\rangle = 2\big(1 - \mathrm{Re}\,F(t)\big)$
  * Correlator: $F(t) = \langle W^\dagger(t) V^\dagger W(t) V \rangle$
* **Physical Meaning & Mechanism**
  * Measures the **non-commutation** of two operators that still commuted at $t = 0$ ($[W(0), V(0)] = 0$).
  * Scrambling corresponds to the decay $F(t) \to 0$.
  * As soon as the support of $W(t)$ reaches the site of $V$, the commutator grows.
* **Why "Out-of-Time-Order"?**
  * The time contour runs through $t \to 0 \to t \to 0$.
  * Standard 2-point functions already decay on the local thermalization timescale $t_{\text{therm}}$ and are blind to scrambling into many-body entanglement.
* **Measurement via the Loschmidt Echo Protocol** (Only non-commutativity survives unitary forward-backward cancellation)
  1. Forward evolution under $e^{-iHt}$.
  2. Apply the butterfly perturbation $V$ (e.g. a local Pauli-$X$).
  3. Backward evolution under $e^{+iHt}$ (implemented on quantum hardware via phase reversal).
  4. Projective overlap measurement with probe $W$.

### Three Dimensions of Operator Growth

* **Rate (Time):**
  * **Metric:** Quantum Lyapunov exponent $\lambda_L$
  * **Growth Law:** $C(t) \sim \frac{1}{N}e^{\lambda_L t}$
  * **Bound / Universality:** **MSS bound:** $\lambda_L \leq \frac{2\pi k_B T}{\hbar} = \frac{2\pi}{\beta}$
  * **Semiclassical limit:** $-\langle[x(t), p(0)]^2\rangle \to \hbar^2 \{x(t), p(0)\}_{\text{PB}}^2 \sim \hbar^2 e^{2\lambda_{\text{cl}}t}$; $\lambda_L$ is the quantum analogue of the classical Lyapunov exponent.
  * **Timescale hierarchy:** $t_{\text{therm}} \sim \mathcal{O}(1) < t_* \sim \lambda_L^{-1}\ln N$ (scrambling time) $< t_K \sim e^S$ (Poincaré time).
  * **Numerical measurability:** In finite 1D spin chains, spatial front $v_B$ can be measured numerically much more robustly than $\lambda_L$.
* **Reach (Space):**
  * **Metric:** Butterfly velocity $v_B$
  * **Growth Law:** Front: $C(t,x) \sim \frac{1}{N}\exp[\lambda_L(t - x/v_B)]$
  * **Bound / Universality:** **Lieb-Robinson bound:** $\Vert{}[A(t), B]\Vert{} \leq C e^{-\mu(d - v_{LR}t)}$, $v_B \leq v_{LR}$
  * **State dependence:** $v_{LR}$ is a state-independent norm bound ("light cone"), whereas $v_B$ depends on the state and the temperature.
  * **Circuit depth:** Determines the minimum depth of quantum circuits for generating global entanglement ($d \sim n$ in 1D, $d \sim \sqrt{n}$ in 2D, $d \sim \log n$ for all-to-all).
  * **Front fluctuations:** Fluctuations of the wavefront follow KPZ universality (Kardar-Parisi-Zhang) with broadening $\sigma(t) \sim t^{1/3}$; entropy growth $S(t) = v_E t$ with $v_E \leq v_B$.
* **Depth (Operator Space):**
  * **Metric:** Krylov complexity $K(t)$
  * **Growth Law:** Free: $t$ | Integrable: $t^2$ | Chaotic: $e^{2\alpha t}$
  * **Bound / Universality:** **UOGH hypothesis:** $b_n \sim \alpha n$ with $\alpha \leq \frac{\pi}{\beta}$
  * **Krylov space:** The Liouvillian $\mathcal{L} = [H, \cdot]$ tridiagonalizes the Krylov space $\mathcal{K} = \text{span}\{W, [H,W], [H,[H,W]], \dots\}$ via the Lanczos coefficients $b_n$.
  * **Operator wave:** Krylov complexity: $K(t) = \sum_n n \vert{}\varphi_n(t)\vert{}^2$ measures the mean position of the operator wave on the chain.

### Bounds, Dualities & Models

* **Logical Stack of Bounds**
  * $\text{KMS condition} \implies \text{UOGH } (\alpha \leq \pi/\beta) \implies \text{MSS bound } (\lambda_L \leq 2\pi/\beta)$.
  * **UOGH:** Maximal linear growth of the Lanczos coefficients ($b_n \sim \alpha n$) in thermal chaotic systems.
  * **MSS bound:** Follows from analyticity in the thermal strip $0 \leq \mathrm{Im}(t) \leq \beta$.
* **Sachdev-Ye-Kitaev (SYK) Model**
  * $N$ Majorana fermions with random all-to-all 4-body interactions.
  * Exactly solvable at large $N$, holographically dual to JT gravity in $\mathrm{AdS}_2$.
  * **Saturates the MSS bound** ($\lambda_L = 2\pi/\beta$): Black holes are the fastest scramblers in nature.

### Static Signatures: ETH & Spectral Statistics

* **Eigenstate Thermalization Hypothesis (ETH)**
  * Matrix elements: $A_{mn} = \mathcal{A}(\bar{E})\delta_{mn} + e^{-S(\bar{E})/2}f_A(\bar{E},\omega)R_{mn}$.
  * A single energy eigenstate behaves like a thermal ensemble for local observables.
  * Integrable systems relax to the *Generalized Gibbs Ensemble (GGE)*; *Many-Body Localization (MBL)* prevents thermalization via local integrals of motion (LIOMs).
* **Random Matrices & Level Repulsion (BGS Conjecture)**
  * Chaos: Wigner-Dyson level repulsion with mean gap ratio $\langle r \rangle \approx 0.53$.
  * Integrability: Poisson statistics without level repulsion with $\langle r \rangle \approx 0.39$.
* **Spectral Form Factor (SFF)**
  * $K(\tau) = \langle \vert{}\mathrm{Tr}(e^{-iHt})\vert{}^2 \rangle$.
  * The characteristic **Dip–Ramp–Plateau** profile at late times ($t > t_*$) reveals discrete level correlations long after spatial OTOCs have saturated.

### Scrambling vs. Decoherence

* **Unitary Scrambling**
  * **Information**: Reversibly delocalized into many-body entanglement; globally reconstructible
  * **Entropy**: Local subsystem entropy rises; global state stays pure ($S_{\text{vN}} = 0$)
  * **OTOC Response**: $F(t) \to 0$ through genuine operator growth
  * **Risk**: Genuine quantum chaos
* **Lindblad Decoherence (Open)**
  * **Information**: Irreversibly dissipated into bath degrees of freedom
  * **Entropy**: Global von Neumann entropy $S_{\text{vN}}(\rho)$ grows non-unitarily
  * **OTOC Response**: $F(t) \to 0$ through phase/amplitude damping
  * **Risk**: Noise mimics a **false Lyapunov exponent** $\lambda_L$

### Applications: Black Holes & Quantum Computing

* **Scrambling as a Resource: Hayden-Preskill & Yoshida-Kitaev**
  * Black holes act as optimal information mirrors: After the Page time, infalling quantum states can be reconstructed from a few Hawking quanta in time $\mathcal{O}(\ln N)$.
  * The Yoshida-Kitaev decoding circuit achieves a reconstruction fidelity proportional to the OTOC value.
* **Scrambling as an Obstacle: Barren Plateaus**
  * Deeply entangling quantum circuits approximate unitary $t$-designs on $U(2^n)$.
  * Haar integration leads to exponentially vanishing gradients: $\mathrm{Var}_{\theta}[\partial_\theta \langle H \rangle] \sim 2^{-n}$.
  * Makes randomly initialized variational algorithms (VQAs) untrainable.
* **Random Circuit Sampling (RCS)**
  * Entering the Porter-Thomas distribution ($P(p) \approx N e^{-Np}$) requires a minimum circuit depth that corresponds to the geometric scrambling time ($d \sim n$ in 1D, $d \sim \sqrt{n}$ in 2D).
