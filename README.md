
# Science 🎨

Alexander Del Toro Barba, PhD

[Google Scholar](https://scholar.google.com/citations?hl=en&user=fddyK-wAAAAJ) $\cdot$ [LinkedIn](https://www.linkedin.com/in/deltorobarba/)


<img src="https://raw.githubusercontent.com/deltorobarba/science/main/code/nature.JPG" alt="science">

<br>

*Working where AI Engineering, Quantum Computing, Mathematics, and Astrophysics meet. The core challenge is often identical: extracting hidden structure from incomplete, noisy measurements.*

*Organized by principle, not by field: real problems (simulating a protein, sifting a sky survey) don't come labeled with a method, so the work is to recognize the principle underneath and map the right tool to it. Three principles make the complicated simple: keep the axes that matter, compute what repeats only once, keep the leading terms. Two more ask what can be recovered from incomplete data, and where knowing stops.*

**The Trinity of Reduction (How do you make the complicated simple?):**

**Principle 1**: [Symmetries](https://github.com/deltorobarba/science/blob/main/symmetries.ipynb) ❄️ They provide you with the correct coordinates *a priori* and at no cost, even before you perform any measurements (because something repeats itself, as is the case with a ring or Clifford circuits). - What repeats needs computing only once: Fourier modes, conserved sectors in a spin chain, Clifford circuits on a laptop, the Berry phase, Mercury's perihelion, and what cosmic isotropy tells us (Planck, DESI).

**Principle 2**: [Principal Axes](https://github.com/deltorobarba/science/blob/main/principal_axes.ipynb) 🧬 Determine the relevant directions a posteriori from noisy data, in cases where symmetry is broken or unknown (ranging from LIGO whitening and Kepler telescope systematics to Schmidt decomposition). - Eigendecomposition of covariance matrices ($C = V\Lambda V^T$) separates signal from noise: LIGO whitening and the GW150914 chirp, Kepler systematics, autoencoders, quantum states, and the Pantheon+ covariance behind H₀.

**Principle 3**: [Approximation](https://github.com/deltorobarba/science/blob/main/approximation.ipynb) 🐚 If the system cannot be solved exactly—even with the correct choice of axes—you should retain the leading-order terms or select the best fit from a family of functions, while always keeping a sharp eye on when the remainder term blows up (whether due to the radius of convergence, Trotter noise, or the failure of neural networks when applied outside their training data). - Keep the leading terms and know the remainder: radii of convergence set by complex poles, Pantheon+ cosmography, post-Newtonian chirps of GW150914, Trotter steps under gate noise, variational bounds from hydrogen to VQE, and neural networks outside their training range.

**The duality of information (What can we know and reconstruct?)**

**Principle 4**: [Reconstruction](https://github.com/deltorobarba/science/blob/main/reconstruction.ipynb) (from Incomplete Measurements) 🌸 Demonstrates how to achieve the seemingly impossible (m < n—fewer measurements than unknowns) by leveraging structural knowledge as a prior—whether it be sparsity in the case of the black hole M87*, rank-1 assumptions in quantum tomography, or positivity constraints when addressing readout errors on actual quantum hardware. - Structural priors ($\ell_1$-sparsity, low rank, positivity) recover underdetermined systems ($m < n$): compressed sensing, EHT imaging of M 87*, quantum tomography, classical shadows, and a Bell state.

**Principle 5**: [Limits of Knowledge](https://github.com/deltorobarba/science/blob/main/limits_of_knowledge.ipynb) 🔬 One encounters a rigid barrier—a point beyond which even the best algorithm cannot proceed. This may be due to physical constraints imposed by nature (such as quantum Fisher information in the context of exoplanets, or the Heisenberg limit in the presence of dephasing), computational complexity (e.g., noisy parities), or simply statistical limitations inherent in everyday AI practice (such as binomial bounds when evaluating agents). - Where physics, statistics, and computation stop us: Rayleigh's curse and quantum-limited SPADE imaging of exoplanets, the Heisenberg limit under noise, learning parity with noise, and how many tasks an AI evaluation needs.

**Special Interest Notebooks**

[Multiwavelength Astronomy](https://github.com/deltorobarba/science/blob/main/multiwavelength_astronomy.ipynb) 🔭🪐 Queries SIMBAD, NASA SkyView and SDSS for any galaxy or nebula: the brightest galaxies, false-color composites from X-ray to radio, and fiber spectra with emission lines in a BPT diagram (M 51).