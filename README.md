
# Science 🎨

Alexander Del Toro Barba, PhD

[Google Scholar](https://scholar.google.com/citations?hl=en&user=fddyK-wAAAAJ) $\cdot$ [LinkedIn](https://www.linkedin.com/in/deltorobarba/)


<img src="https://raw.githubusercontent.com/deltorobarba/science/main/code/nature.JPG" alt="science">

<br>

*Working where AI Engineering, Quantum Computing, Mathematics, and Astrophysics meet. The core challenge is often identical: extracting hidden structure from incomplete, noisy measurements. At the same time, real problems (simulating a protein, sifting a sky survey) are <u>not</u> organized by field or tool, but by principle. So the work is to recognize the first principle underneath and map the right tool to it. The arc: use structure a priori → filter structure from data → approximate complexity under control → reconstruct what is missing with prior knowledge → accept fundamental limits → ask whether a small disturbance grows or dies out.*

**Trinity of Reduction (How do you make the complicated simple?)**

* **Principle 1**: [Symmetries](https://github.com/deltorobarba/science/blob/main/symmetries.ipynb) ❄️ What repeats needs computing only once: a symmetry hands you the right coordinates *a priori*, before any measurement. Examples: Fourier modes on a ring, conserved sectors in a spin chain, Clifford circuits on a laptop, the Berry phase, Mercury's perihelion, and what cosmic isotropy tells us (Planck, DESI).
* **Principle 2**: [Principal Axes](https://github.com/deltorobarba/science/blob/main/principal_axes.ipynb) 🧬 Where symmetry is broken or unknown, find the relevant directions *a posteriori* from noisy data: the eigendecomposition of a covariance matrix ($C = V\Lambda V^T$) separates signal from noise. Examples: LIGO whitening and the GW150914 chirp, Kepler systematics, autoencoders, entangled quantum states, and the Pantheon+ covariance behind H₀.
* **Principle 3**: [Approximation](https://github.com/deltorobarba/science/blob/main/approximation.ipynb) 🐚 If a system cannot be solved exactly, even in the right axes, keep the leading terms or pick the best member of a family, and watch where the remainder blows up. Examples: radii of convergence set by complex poles, Pantheon+ cosmography, post-Newtonian chirps of GW150914, Trotter error under gate noise, variational bounds from hydrogen to VQE, and neural networks outside their training range.

**Duality of Information (What can we know and reconstruct?)**

* **Principle 4**: [Reconstruction from Incomplete Measurements](https://github.com/deltorobarba/science/blob/main/reconstruction.ipynb) 🌸 Recover more unknowns than measurements ($m < n$) by using structure as a prior: sparsity ($\ell_1$), low rank, positivity. Examples: compressed sensing, EHT imaging of M 87\*, quantum tomography, classical shadows, and a readout-corrected Bell state on IBM hardware.
* **Principle 5**: [Limits of Knowledge](https://github.com/deltorobarba/science/blob/main/limits_of_knowledge.ipynb) 🔬 Some barriers no algorithm can cross, whether physical, statistical, or computational. Examples: Rayleigh's curse and quantum-limited SPADE imaging of exoplanets, the Heisenberg limit under dephasing, learning parity with noise, and how many tasks an AI agent evaluation needs.

**Dynamics (How does a system evolve?)**

* **Principle 6**: [Stability](https://github.com/deltorobarba/science/blob/main/stability.ipynb) 🦋 Does a small disturbance grow or die out? The sign of one eigenvalue decides whether a system stays predictable, forgets its past, or remembers it. Examples: Lyapunov exponents from the logistic map to Lorenz, chaotic star orbits and the Kirkwood gaps, scrambling (OTOCs) and many-body localization, Kuramoto synchronization, the neutron freeze-out that set the cosmic helium abundance, and feedback from adaptive optics to learning rates, and optimal control at the unstable Lagrange point L2, learned model-free by Q-learning.

**Special Interest Notebooks**

* **Astrophysics**: [Multiwavelength Astronomy](https://github.com/deltorobarba/science/blob/main/multiwavelength_astronomy.ipynb) 🔭🪐 Queries SIMBAD, NASA SkyView and SDSS for any galaxy or nebula: the brightest galaxies, false-color composites from X-ray to radio, and fiber spectra with emission lines in a BPT diagram (M 51).
* **Quantum Information**: [Heisenberg-Weyl & Quantum Dynamics](https://github.com/deltorobarba/science/blob/main/heisenbergweyl.ipynb)