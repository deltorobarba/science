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

The theory of quantum chaos and scrambling (operator growth, OTOCs, quantum Lyapunov exponent, butterfly velocity and Lieb-Robinson bound, Krylov complexity, MSS bound and SYK model, spectral statistics and ETH, scrambling vs. decoherence, Hayden-Preskill and the Page curve, barren plateaus and random circuit sampling) is in the notebook [Quantum Chaos and Scrambling](https://github.com/deltorobarba/science/blob/main/quantum/quantumchaos.ipynb), together with simulations of OTOC light cones in Ising chains, the butterfly velocity of random circuits, the Hayden-Preskill protocol and the Page curve.

### Seven Perspectives on Quantum Chaos

* **Spreading:** Lieb-Robinson bound, quasiparticles, quenches, entanglement growth. Notebook: [Quantum Chaos and Scrambling](https://github.com/deltorobarba/science/blob/main/quantum/quantumchaos.ipynb).
* **Operator growth and scrambling:** OTOCs, butterfly velocity, quantum Lyapunov exponent, Krylov complexity, random circuits. Notebook: [Quantum Chaos and Scrambling](https://github.com/deltorobarba/science/blob/main/quantum/quantumchaos.ipynb).
* **Spectral statistics:** level repulsion, the gap ratio $r$, the spectral form factor, random-matrix theory. Notebook: [Spektralstatistik und Quantenchaos](https://github.com/deltorobarba/science/blob/main/quantum/chaos_spectra.ipynb) (German).
* **Eigenstates and thermalization:** eigenstate thermalization hypothesis (ETH), generalized Gibbs ensemble.
* **When thermalization fails:** integrability, many-body localization, quantum many-body scars, Hilbert-space fragmentation.
* **Information and gravity:** Hayden-Preskill protocol, Page curve, SYK model, MSS bound on chaos. Notebook: [Quantum Chaos and Scrambling](https://github.com/deltorobarba/science/blob/main/quantum/quantumchaos.ipynb).
* **Measurement and driving:** measurement-induced phase transitions, Floquet systems, time crystals.
