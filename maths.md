# Maths

Topics for single-topic notebooks: theory, derivations by hand, code and plots. How a notebook is built is described in [AGENTS.md](AGENTS.md).

## Suggested tracks

- Measurement
  - 2.3 → 2.8 → 4.8, ending at the quantum limits of gravitational-wave detectors
- Weyl–Heisenberg
  - 1.1 (groups, characters) → 1.2 (Fourier analysis on finite groups) → 2.6 → 4.3
- Dynamics and NMR
  - 3.1 → 3.3 → 3.5
- Convexity
  - 1.2 (convex analysis) → 2.4 (witnesses) → 2.3 (state discrimination as an SDP)

## 1. Mathematics by field

### 1.1 Algebra

**Linear algebra**
- Spectral theorem in finite dimensions
  - normal matrices, unitary diagonalization, functional calculus f(A).
  - Code: matrix exponential and logarithm three ways.
- Singular value decomposition
  - low-rank approximation (Eckart–Young), polar decomposition, Schmidt decomposition as an SVD.
  - Code: image compression, rank of random states.
- Tensor and Kronecker products
  - index gymnastics, vectorization, partial trace as a contraction.
  - Code: einsum for partial traces.
- Matrix norms and inequalities
  - Schatten norms, Hölder, trace norm duality, positive semidefinite order.
  - Code: numerical checks of the inequalities on random matrices.

**Groups**
- Finite groups and actions
  - cyclic groups ℤ_d, orbits and stabilizers, Burnside's lemma.
  - Code: orbits of SL(2, ℤ_d) on ℤ_d².
- Finite abelian groups
  - structure theorem, Chinese remainder theorem ℤ_d ≅ ℤ_{d1} × ℤ_{d2}, subgroups of ℤ_d².
  - Code: enumerate the subgroups and lines of ℤ_d² for prime and composite d.
- Symmetric group and permutations
  - cycle structure, sign, conjugacy classes.

**Rings, fields and number theory**
- Modular arithmetic
  - Euclid's algorithm, modular inverses, units, Euler's φ.
  - Code: modular inverses with Euclid's algorithm for large d.
- Finite fields 𝔽_p and 𝔽_{p^k}
  - construction, primitive elements, vector spaces over 𝔽_p.
- Integer matrices over ℤ_d
  - Hermite and Smith normal form, why Gaussian elimination fails for composite d.
  - Code: HNF by hand and with sympy.
- Gauss sums and quadratic residues
  - quadratic and cubic Gauss sums, the Weil bound.
  - Code: |Σ ω^{x³}| against √d.
- Continued fractions
  - convergents, period finding in Shor's algorithm.
- Lattices
  - bases, determinant, Gram–Schmidt, LLL reduction, the shortest vector problem.
  - Code: LLL on a hidden number instance.

**Representation theory**
- Characters of finite groups
  - Schur's lemma, orthogonality, character tables.
  - Code: character table of a small group.
- Fourier analysis on finite groups
  - abelian case, Plancherel, convolution theorem.
  - Code: FFT on ℤ_d and ℤ_d² as a character transform.
- Representations of SU(2)
  - spin j, Clebsch–Gordan, Wigner D-matrices.
- Schur–Weyl duality
  - symmetric subspace, permutation operators, Haar integrals over U(d).
  - Code: Monte Carlo of Haar moments against the Weingarten formula.

**Lie groups and algebras**
- Matrix Lie groups
  - exponential map, Lie algebra, adjoint action, BCH formula.
  - Code: BCH truncations against exact exp(A)exp(B).
- su(2), so(3) and the double cover
  - rotations of the Bloch sphere.
- Heisenberg group and algebra
  - [x, p] = iħ, its finite version, central extensions (README: Heisenberg–Weyl).

**Multilinear algebra**
- Tensor algebra T(V), symmetric and exterior algebra (README: Tensor Algebra)
- Clifford algebras
  - generators, Majorana operators, Jordan–Wigner.

### 1.2 Analysis

**Real and complex analysis**
- Lebesgue integral and Lᵖ spaces
  - convergence theorems, completeness.
- Complex analysis
  - residues and contour integrals for Fourier transforms and Green's functions.
  - Code: numerical contour integration.

**Fourier analysis**
- Fourier series and transform
  - Plancherel, convolution, Poisson summation.
  - Code: Poisson summation numerically.
- Discrete Fourier transform and FFT
  - aliasing, windowing, leakage, sampling theorem.
  - Code: spectral leakage with and without a window (bridge to gravitational-wave data).
- Uncertainty principles
  - Heisenberg–Weyl, Donoho–Stark for finite groups, Hardy.
  - Code: support size of f against support of its DFT.
- Sparse Fourier transforms
  - hashing, aliasing filters, why they need queries.

**Functional analysis**
- Hilbert spaces
  - orthonormal bases, projections, Riesz representation, weak convergence.
- Bounded operators
  - adjoints, compact operators, trace class and Hilbert–Schmidt, the trace.
- Spectral theorem for self-adjoint operators
  - projection-valued measures, point and continuous spectrum.
  - Code: discretized position operator and its spectrum.
- Unbounded operators
  - domains, self-adjoint extensions, the particle in a box against the half line.
- Stone's theorem
  - one-parameter unitary groups and their generators, U(t) = e^{−iHt}.
- Stone–von Neumann theorem
  - uniqueness of the canonical commutation relations, Weyl form.
- Hahn–Banach theorem
  - separation of convex sets, applied to entanglement witnesses.
- C*-algebras and states
  - GNS construction, positive maps.

**Differential equations**
- Linear ODE systems
  - matrix exponential, stability, Floquet theory for periodic driving.
  - Code: Floquet multipliers of a driven oscillator.
- Sturm–Liouville problems and special functions
  - Hermite, Legendre, Bessel.
- PDEs
  - heat, wave and Schrödinger equation, separation of variables, spectral methods.
  - Code: split-step Fourier for the Schrödinger equation.

**Convex and variational analysis**
- Convex sets and functions
  - extreme points, Carathéodory, Krein–Milman, convex hulls of states.
- Duality
  - Lagrangian, KKT conditions, weak and strong duality, Slater's condition.
- Semidefinite programming
  - primal and dual, complementary slackness.
  - Code: cvxpy for optimal state discrimination.
- Calculus of variations
  - Euler–Lagrange, Noether's theorem, brachistochrone, geodesics.
- Variational principle
  - Rayleigh–Ritz, min–max (Courant–Fischer), Hellmann–Feynman.
  - Code: variational ground state of an anharmonic oscillator.
- Optimal control
  - Pontryagin's principle, gradient-based pulse design (bridge to 3.6).

### 1.3 Geometry and topology

- Differential geometry
  - manifolds, tangent spaces, differential forms, Riemannian metric, curvature, geodesics (prerequisite for general relativity).
- Symplectic geometry
  - symplectic form, Hamiltonian flows, Poisson brackets, Liouville's theorem, symplectic matrices (README: Symplectic Form).
  - Code: symplectic against non-symplectic integrators over long times.
- Projective Hilbert space
  - ℂPⁿ, the Bloch sphere, Fubini–Study metric.
- Fibre bundles and connections
  - the Berry connection and curvature, Chern numbers.
- Topology basics
  - homotopy, fundamental group, winding numbers.
  - Code: winding number of a curve in the plane.

### 1.4 Probability, statistics and information

**Probability**
- Concentration inequalities
  - Markov, Chebyshev, Hoeffding, Chernoff, Bernstein, matrix Chernoff.
  - Code: tails of binomial counts against the bounds.
- Martingales and stopping times
  - adaptive sampling, sequential tests.
- Stochastic processes
  - Markov chains, Poisson processes, Brownian motion, Itô calculus.
  - Code: Euler–Maruyama for an Ornstein–Uhlenbeck process (bridge to continuous measurement).
- U-statistics
  - variance of statistics over all pairs of samples.

**Statistics**
- Estimation theory
  - maximum likelihood, Fisher information, Cramér–Rao bound, efficiency.
  - Code: MLE variance against 1/(N·I) for a coin and a Gaussian.
- Bayesian inference
  - priors, posteriors, evidence, credible intervals (bridge to gravitational-wave parameter estimation).
- Sampling
  - MCMC (Metropolis–Hastings, HMC), nested sampling.
  - Code: nested sampling for a two-mode posterior.
- Hypothesis testing and multiple comparisons
  - p-values, Bonferroni, false discovery rate, look-elsewhere effect.
- Bootstrap and resampling

**Random matrices and high dimensions**
- Gaussian ensembles
  - GOE and GUE, Wigner semicircle, Marchenko–Pastur.
  - Code: eigenvalue histograms.
- Level spacing statistics
  - Poisson against Wigner–Dyson, the spectral form factor.
- Haar measure and concentration of measure
  - Lévy's lemma, typical states.
  - Code: entanglement of random states against the Page curve.

**Information theory**
- Shannon and Rényi entropies, relative entropy, mutual information
- Data processing inequality and sufficient statistics
- Channel capacity and coding
  - the binary symmetric channel, typical sets.

### 1.5 Discrete mathematics and computation

- Graph theory
  - adjacency and Laplacian spectra, expanders, graph colouring.
- Boolean functions and Fourier analysis on the hypercube
  - influences, Goldreich–Levin, Kushilevitz–Mansour.
- Complexity theory
  - P, NP, BPP, BQP, reductions, average-case hardness, query complexity.
- Learning theory
  - PAC learning, VC dimension, statistical-query model, lower bounds via Fano and Le Cam.
- Lattice problems in cryptography
  - SVP, LWE, hidden number problem, dihedral coset problem.
- Numerical linear algebra
  - Lanczos and Krylov methods, sparse matrices, randomized SVD.
  - Code: Lanczos ground state of a spin chain.
- Tensor networks
  - matrix product states, SVD truncation, DMRG basics.
- Optimization
  - gradient descent, stochastic gradients, Adam, landscape pathologies.

## 2. Mathematical foundations of quantum mechanics

### 2.1 States
- Density operators
  - pure and mixed states, the Bloch ball, purification, convexity of the state space.
  - Code: random states (Haar, Hilbert–Schmidt, Bures) and their purity distributions.
- Generalized Bloch vectors for qudits
  - Gell-Mann and Weyl operator bases, why the qudit state space is not a ball.

### 2.2 Observables and spectral theory
- Observables as self-adjoint operators
  - commuting sets, simultaneous diagonalization, compatible measurements.
- Position and momentum
  - unbounded operators, the Fourier transform as a change of basis.
  - Code: finite-difference x and p, convergence of their spectra.

### 2.3 Measurement
- Projective measurement and the Born rule
  - from the spectral theorem.
  - Plot: frequencies against shot number converging to the Born probabilities.
- POVMs and Naimark dilation
  - every generalized measurement is projective in a larger space.
  - Plot: trine and SIC POVMs on the Bloch sphere.
- Post-measurement states
  - Kraus operators, Lüders rule, quantum instruments.
- State discrimination
  - Helstrom bound P_err = ½(1 − ‖p₀ρ₀ − p₁ρ₁‖₁), pretty-good measurement, unambiguous discrimination, the SDP for several states.
  - Plot: error against overlap; cvxpy for three states.
- Uncertainty relations
  - Robertson–Schrödinger, entropic (Maassen–Uffink), mutually unbiased bases, H(X) + H(Z) ≥ log d.
  - Plot: entropy sum over the Bloch sphere.
- Weak and continuous measurement
  - quantum trajectories, stochastic master equation, collapse as a diffusion.
  - Plot: trajectories of ⟨σ_z⟩.
- Quantum Zeno effect and quantum non-demolition measurement
  - Plot: survival probability against the number of measurements.
- Covariant measurements and Bell measurements
  - the Bell basis of qudits, measurements built from a group orbit.

### 2.4 Composite systems and entanglement
- Tensor products and partial trace
  - reduced states, Schmidt decomposition, entanglement entropy.
- Entanglement criteria
  - PPT (Peres–Horodecki), entanglement witnesses as separating hyperplanes (Hahn–Banach), negativity, concurrence.
  - Plot: Werner states, where PPT holds.
- Bell inequalities
  - CHSH, Tsirelson bound as an SDP, nonlocal games.
- LOCC and entanglement transformations
  - Nielsen's majorization theorem.

### 2.5 Quantum channels
- Completely positive maps
  - Kraus form, Choi–Jamiołkowski isomorphism, Stinespring dilation.
- Standard noise channels
  - depolarizing, dephasing, amplitude damping, their action on the Bloch ball.
  - Plot: deformed Bloch balls.
- Distances between channels
  - diamond norm, process fidelity, channel discrimination.

### 2.6 Symmetry and groups in quantum mechanics
- Pauli and Weyl–Heisenberg groups
  - X, Z, ω, displacement operators D_{q,p} for qudits, commutation via the symplectic form.
- Clifford group and the symplectic group
  - Sp(2n), SL(2, ℤ_d), the Weil representation, circuits from Euclid's algorithm.
- Stabilizer formalism
  - stabilizer states and codes, Gottesman–Knill theorem.
- Discrete Wigner function and Hudson's theorem
  - negativity as magic.
  - Plot: Wigner functions of stabilizer against cubic phase states.
- Angular momentum
  - SU(2) representations, Clebsch–Gordan, spin coherent states.
- Unitary designs and Haar integrals
  - Weingarten calculus, 2-designs from the Clifford group.

### 2.7 Phase space and continuous variables
- Harmonic oscillator and ladder operators
  - number states, coherent states (README: Quantum Harmonic Oscillator).
- Wigner, Husimi Q and Glauber P functions
  - Plot: Wigner functions of Fock, coherent, cat and squeezed states.
- Gaussian states and symplectic transformations
  - squeezing, beam splitters, Williamson's theorem.

### 2.8 Distances, entropies and information
- Trace distance and fidelity
  - Uhlmann's theorem, Fuchs–van de Graaf inequalities.
- Von Neumann entropy and quantum relative entropy
  - Klein's inequality, data processing.
- Strong subadditivity
  - statement, Lieb's concavity theorem, consequences.
- Holevo bound
  - why n qubits carry at most n classical bits.
- Quantum Fisher information and the Bures metric (bridge to 4.8)

### 2.9 Geometry and topology of quantum states
- Berry phase and the adiabatic theorem
  - Plot: Berry phase of a spin in a rotating field against the solid angle.
- Topological band theory
  - Chern number of a two-band model (Qi–Wu–Zhang).
  - Plot: Berry curvature on the Brillouin zone.

### 2.10 Foundations proper (optional)
- No-cloning, no-signalling, no-deleting
- Gleason's theorem and the Kochen–Specker theorem
  - contextuality.

### 2.11 Many particles (optional)
- Second quantization
  - Fock space, bosons and fermions, Jordan–Wigner transformation.

## 3. Quantum dynamics

### 3.1 Closed systems
- Schrödinger equation and unitary evolution
  - time-independent and time-dependent H, interaction picture, Dyson series, Magnus expansion.
- Two-level dynamics
  - Rabi oscillations, rotating-wave approximation, Bloch equations.
  - Plot: Rabi chevron (detuning against time).
- Adiabatic evolution
  - adiabatic theorem, Landau–Zener transitions.
  - Plot: transition probability against sweep rate.
- Time-periodic driving
  - Floquet theory, effective Hamiltonians, high-frequency expansion.

### 3.2 Simulation algorithms
- Trotter–Suzuki product formulas
  - first and second order, commutator error bounds.
  - Plot: error against step size and order.
  - See also: README, Quantum Simulation (in part)
- Randomized and advanced methods
  - qDRIFT, linear combination of unitaries, qubitization and quantum signal processing.
- Variational simulation
  - VQE, variational imaginary time evolution.

### 3.3 Open systems
- Lindblad (GKSL) master equation
  - derivation sketch (Born–Markov), T1 and T2, steady states.
  - Plot: Bloch vector relaxation.
- Quantum trajectories as an unravelling of the master equation (bridge to 2.3, continuous measurement)
- Non-Markovian dynamics
  - spectral densities, memory kernels, spin–boson model.

### 3.4 Many-body dynamics, chaos and scrambling
- Lieb–Robinson bounds and light cones
  - Plot: commutator growth in a spin chain.
- Out-of-time-order correlators and scrambling
  - See also: dynamics.ipynb
- Operator growth
  - Pauli weight distribution, butterfly velocity.
- Chaos and spectral statistics
  - level spacing, spectral form factor, integrable against chaotic Ising.
  - See also: dynamics.ipynb (in part)
- Eigenstate thermalization hypothesis
  - diagonal and off-diagonal matrix elements.
- Information scrambling and black holes
  - Hayden–Preskill, Page curve.
  - See also: dynamics.ipynb
- Many-body localization and integrability

### 3.5 Spin dynamics and NMR
- Spin Hamiltonians
  - Zeeman, dipolar coupling, secular approximation, rotating frame.
- Pulse sequences and average Hamiltonian theory
  - Magnus expansion in practice, WAHUHA.
- Time reversal
  - Loschmidt echo, magic echo, sign reversal of the dipolar Hamiltonian.
- Multiple-quantum coherences
  - coherence order, cluster size, the link to OTOCs.

### 3.6 Control
- Dynamical decoupling
  - spin echo, CPMG, filter functions.
  - Plot: filter functions of different sequences.
- Optimal control
  - GRAPE, robust pulses.

### 3.7 Further topics
- Quantum walks
  - continuous and discrete, spreading against classical random walks.
- Driven many-body systems
  - prethermalization, discrete time crystals.

## 4. Quantum learning

### 4.1 Tomography
- State tomography
  - linear inversion, maximum likelihood, sample complexity, the d² barrier.
  - Plot: error against copies for both estimators.
- Compressed-sensing tomography for low-rank states; process tomography

### 4.2 Classical shadows
- Random Pauli and Clifford measurements, median-of-means, the shadow norm
  - Plot: error against snapshots for local and global observables.

### 4.3 Bell sampling and stabilizer learning
- Bell sampling and Bell difference sampling for qubits; stabilizer testing (Gross, Nezami, Walter)
- Learning stabilizer states (Montanaro) and states with few non-Clifford gates
- Qudit Bell bases and conjugate states (King, Wan, McClean)

### 4.4 Learning sparse spectra
- Heavy Fourier and Pauli coefficients
  - Goldreich–Levin, Kushilevitz–Mansour, sparse FFT; queries against samples.
- Pauli channel estimation and the role of quantum memory (exponential separations)

### 4.5 Hamiltonian learning
- From dynamics, from Gibbs states, Heisenberg-limited learning

### 4.6 Hardness of learning
- Pseudorandom states and pseudomagic
- LWE and DCP as lower bounds; statistical-query lower bounds

### 4.7 Property testing
- Swap test, purity and overlap estimation, testing entanglement and stabilizer-ness

### 4.8 Quantum metrology
- Quantum Fisher information, quantum Cramér–Rao bound, standard quantum limit 1/√N against Heisenberg limit 1/N
  - Plot: phase estimation error with product and GHZ states.
- Squeezed states in interferometry
  - shot noise against radiation-pressure noise, the standard quantum limit of LIGO, frequency-dependent squeezing (bridge to astrophysics.md, gravitational waves).

### 4.9 Quantum machine learning models
- Variational circuits and barren plateaus
  - Plot: gradient variance against qubit number.
- Quantum kernels and dequantization (Tang)
