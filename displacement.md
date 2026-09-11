# Displacement Operators and Bell Basis Measurements

## Technical Summary of Conjugate Pairs Paper

In the paper [arXiv:2403.03469](https://arxiv.org/abs/2403.03469) they compute: <font color="orange">$y_{q,p}^2$</font> $\approx \sum_{a,b} $ <font color="red">$p_{a,b}$</font> <font color="blue">$e^{i \frac{2\pi}{d} (a p - b q)}$</font> (from Fourier-like inversion over Bell measurement statistics)

* <font color="orange">$y_{q,p}^2$</font>: displacement coefficient measuring how aligned the signal is with a displacement operator $D_{q,p}$ (conceptually close to Wigner function $W_\rho(q,p)$). Encodes position and momentum of signal -> this we want to estimate

* <font color="red">$p_{a,b}$</font> = $\text{Tr}[\Pi_{a,b} (\rho \otimes \rho^*)]$ probability of obtaining outcome $(a,b)$ when measuring the joint state $\rho \otimes \rho^*$ in the Bell basis (projecting onto the entangled state $|\Phi_{a,b}\rangle$)

  * $\Pi_{a,b} = |\Phi_{a,b}\rangle \langle \Phi_{a,b}|$ are Bell projectors, projecting onto entangled basis states. For example $\Pi_{0,0} = |\Phi_{0,0}\rangle \langle \Phi_{0,0}|$. And for qubits d=2 Bell basis has 4 Bell states (a,b) $\in$ (0,0), (0,1), (1,0), (1,1).

    * Each Bell state $|\Phi_{a,b}\rangle$ is an **eigenstates** of the observable 'displacement operator' $D_{q,p} \otimes D_{-q,p}$
    * Eigenvalues are **Fourier characters** $\chi_{q,p}(a,b)$ of operator spectrum obtained when measuring in Bell basis - $(a,b)$ live in dual space to position momentum space $(q,p)$ - like what time would be to frequency in Fourier - **We measure in Bell basis because it gives access to the spectrum (Fourier components) of hidden displacement operator!**
    * Measurement probabilities $p_{a,b}$ encode expectation values of dual values (a,b) ($p_{a,b}$ form **characteristic function**) - With entangled Bell measurements we measure probability of $(a,b)$ because they encode the characteristic function $\chi_{q,p}(a,b)$.
    * Applying Fourier inversion $\chi_{q,p}(a,b) = e^{i\frac{2\pi}{d}(a p - b q)}$ recovers $y_{q,p}^2$ in measurement domain to estimate displacements $(q,p)$

  * $\rho \otimes \rho^*$: conjugate pair allows access to structured correlation and commuting extensions. We use the complex conjugate to ensure that the Bell measurements access bilinear correlations between $\rho$ and $\rho^*$, which encode the squared modulus of the Fourier component — i.e., $y_{q,p}^2$.
  
    * $\rho_{q,p,r} = \frac{1}{d} \left( I + r \cdot \varepsilon \cdot E_{q,p} \right)$ is quantum state with random background and small structured deviation injected where $E_{q,p} = D_{q,p} \sigma D_{q,p}^\dagger$. From this, we construct the conjugate pair as the tensor product $\rho_{q,p,r} \otimes \rho_{q,p,r}^*$

  
* <font color="blue">$e^{i \frac{2\pi}{d} (a p - b q)}$</font> = $\chi_{q,p}(a,b)$ is the character (Fourier phase factor or fourier transform kernel) to turn our characteristic function details back into a Wigner-like $y_{q,p}^2$ position and momentum information.


<font color="blue">*Displacement Operators $D_{q,p} \otimes D_{-q,p}$ and Conjugate Pair States $\rho \otimes \rho^*$*
* <font color="blue">$\rho$</font> is single-copy quantum state whose displacement amplitudes $y_{q,p} = \text{Tr}(D_{q,p}\rho)$ we want to know
* <font color="blue">$D_{q,p}$</font> is displacement operator
  * **Problem 1**: $D_{q,p}$ non-Hermitian for $d>2$, so complex Eigenvalues $→$ cannot be directly measured on single copy $\rho$.
  * **Problem 2**: $D_{q,p}$ for different (q, p) indices do not commute with each other due to commutation relation $D_{q',p'} D_{q,p} = e^{i2\pi(q'p - qp')/d} D_{q,p} D_{q',p'}$. Incompatible observables, can't be measured simultaneously on single copy $\rho$.
* <font color="blue">$D_{q,p} \otimes D_{-q,p}$</font> is constructed Hermitian operator $O_{q,p}$
  * **Solves 1**: has real Eigenvalues on joint system (are Hermitian because operators are related by transposition and conjugation)
  * **Solves 2**: Set of all joint operators $O_{q,p}$ mutually commute $\{D_{q,p} \otimes D_{-q,p}\}$ $\rightarrow$ allows simultaneous measurement of all $O_{q,p}$ observables in shared Eigenbasis (= generalized Bell basis $\{|\Phi_{a,b}\rangle\}$)
* <font color="blue">$\rho \otimes \rho^*$</font> constructed two-copy physical state ('conjugate pair') that exists in same two-qudit composite system as observable $O_{q,p}$. Forces measured expectation value to be exactly $(y_{q,p})^2$. Works because of identity: $\text{Tr}(D_{-q,p}\rho^*) = \text{Tr}(D_{q,p}^T \rho^*) = \text{Tr}(D_{q,p}\rho)$. Meanwhile two identical copies $\rho$ does not work: $\text{Tr}(D_{-q,p}\rho) \ne \text{Tr}(D_{q,p}\rho)$ does not simplify to $(y_{q,p})^2$
* <font color="blue">$E = (D_{q,p} \otimes D_{-q,p}) (\rho \otimes \rho^*) = |y_{q,p}|^2$</font> measures expectation value, extracts real amplitude $y_{q,p}$ squared

$\begin{array}{rcl} E & = & \text{Tr}(D_{q,p}\rho) \cdot \text{Tr}(D_{-q,p}\rho^*) & \quad \text{(Separation of Trace)} \\ & = & \text{Tr}(D_{q,p}\rho) \cdot \text{Tr}(D_{q,p}^T\rho^*) & \quad \text{(Using transpose of} D_{q,p}: D_{q,p}^T = D_{-q,p} \text{ (operator identity)} \\ & = & \text{Tr}(D_{q,p}\rho) \cdot \text{Tr}(D_{q,p}\rho) & \quad \text{(Using } \text{Tr}(A^T B^*) = \text{Tr}(AB) \text{ (matrix identity)} \\ & = & (\text{Tr}(D_{q,p}\rho))^2 = (y_{q,p})^2 & \quad \text{(Symmetry at (q, p) and (-q, -p) due to $D_{q,p}^\dagger = D_{-q,-p}$)} \end{array}$

## <font color="blue">*Displacement operators*

* Commutation relations: $D_{q',p'} D_{q,p} = e^{i 2\pi (qp' - q'p)/d} D_{q,p} D_{q',p'}$
* $\{D_{q,p} \otimes D_{-q,p}\}$ mutually commute

<br>

> $
\begin{array}{ccc}
D_{q,p}^T = D_{-q,p} & p & D_{q,p} \\
\nwarrow & \uparrow & \nearrow \\
\longleftarrow & + & \longrightarrow q \\
\swarrow & \downarrow & \searrow \\
D_{q,p}^{-1} = D_{q,p}^\dagger = D_{-q,-p} &  & D_{q,p}^* = D_{q,-p}
\end{array}
$

<br>

* Shadow tomography on set of <span style="color:red">**displacement operators.**</span>
* Hilbert space $\mathbb{C}^d$.
* Unknown quantum state $\rho$.

> $
X = \begin{pmatrix}
0 & 0 & \dots & 0 & 1 \\
1 & 0 & \dots & 0 & 0 \\
\vdots & \vdots & \ddots & \vdots & \vdots \\
0 & 0 & \dots & 1 & 0
\end{pmatrix}
\quad \quad \quad
Z = \begin{pmatrix}
1 & 0 & \dots & 0 \\
0 & \omega & \dots & 0 \\
\vdots & \vdots & \ddots & \vdots \\
0 & 0 & \dots & \omega^{d-1}
\end{pmatrix}
$

* Want $\text{Tr}(D_{q,p}\rho) \pm \varepsilon$ for every $q,p$.

> $
\begin{array}{ccc}
 & p & \\
 & \uparrow & \Large{\color{red}\bullet} \normalsize \; D_{q,p} \\
 & | & \nearrow \\
\text{---} & \Large{\color{red}\bullet} & \text{------} \longrightarrow q \\
 & | &
\end{array}
$

> $
D_{q,p} = e^{i\pi qp/d} X^q Z^p
$

<br>

* Video: [Exponential learning advantages with conjugate states and minimal | King, Wan and McClean | TQC 2024](https://www.youtube.com/watch?v=koyFydFJiFQ$0)
* Video: [Complex conjugates | Imaginary and complex numbers | Precalculus | Khan Academy](https://www.youtube.com/watch?v=BZxZ_eEuJBM$0)

## <font color="blue">*Displacement Operators for Signal Detection (Magnitude and Sign)*</font>
* **Goal**: We want to use this to test at which fundamental frequency the molecule (quantum state) mainly resonates
* **What**: Resonance in each frequency is built from oscillations of different energy levels $n$ (quantum number) in molecule or state:
  * A **specific (q,p)** is one fundamental frequency. We check for all, where does the molecules resonate strongest?
  * At a specific frequency (q,p), Ground state may oscillate with contribution 4, and first excited state with contribution -2.
  * **Magnitude** is absolute sum (expectation value) of all contributions within one fundamental frequency,
  * **Sign** is direction of sum. It is weighted average (+4-2..). Shows if it aligns or anti-aligns with fundamental frequency
  * **Signal** (Trace, Expectation value) is largest, complex sum of all contributions. We do this for all p,q: $D_{3,5}$=-2, $D_{6,9}$=+8.
  * **Displacement operator $D_{q,p}$** is interferometer where each p,q represents one fundamental frequency.
* **How:** Measure quantum state overlap with each q,p.
  * $D_{q,p}$ **displaces/translates/evolves** state by $p,q$, and **measures overlap** with original (interferometry). Signal = $\langle \psi | D_{q,p} | \psi \rangle$ = $\text{Tr}(D_{q,p} \rho)$. ($D_{q,p}$ is unitary. It evolves or rotates the state. Physically: it takes the existing state and moves it in phase space.)
  * High overlap = quantum state resonates in this frequency =  **state repeats itself** if shifted by vector $(q,p)$.
  * **Magnitude**: Autocorrelation (Self-Similarity) under shifting. **Sign**: Phase of that overlap (Constructive/Destructive).
  * Result: **Displacement Map = Correlation Map** of fundamental frequencies with quantum state (not Spatial Map!)
* **Math:** Magnitude + Sign = Expectation Value. For $D_{q,p}$ and state $\sigma$, expectation value is **full complex number** $z$:
  * **$z$ is the arrow**: $z$ = $x + iy$ = $r \cdot e^{i\theta}$ = $\text{Tr}(D_{q,p} \sigma)$ = $\langle \psi | D_{q,p} | \psi \rangle$
  * **$|z|$ or $r$ is magnitude** - How long the arrow is? (absolute length of vector). Strength of whole complex number ($x+iy$)
  * **$e^{i\theta}$ is full phase** - Where arrow $z$ points? Has real + imaginary part corresponding to Hermitian parts of $D_{q,p}$:
    * **Real Part: Cosine Wave** (Quadrature:) $\text{Re}[z] = \text{Tr}(A\rho)$, where $A = \frac{1}{2}(D_{q,p} + D_{q,p}^\dagger)$.
    * **Imaginary Part: Sine Wave** (Quadrature): $\text{Im}[z] = \text{Tr}(B\rho)$, where $B = \frac{1}{2i}(D_{q,p} - D_{q,p}^\dagger)$.
  * Problem: $D_{q,p}$ is unitary (complex). But Real Part corresponds to Hermitian $S_{q,p} = \frac{1}{2}(D_{q,p} + D_{q,p}^\dagger)$ $\sim \cos(q\hat{P} - p\hat{Q})$.
  * **Sign**: Simplified to: Real part $x$ (cosine wave) in $z = x + iy$ = $\text{Tr}(D_{q,p} \sigma)$ = $r \cdot e^{i\theta}$: Is it positive or negative? (Binary) = Does state $\rho$ resonates with Cosine wave $\cos(q\hat{P} - p\hat{Q})$ of frequency $(q,p)$ in phase space? Calculated as sign of real part of expectation value: Sign $\equiv$ Sign of $(\text{Re}[z])$ = Sign of $ (\text{Re}[\text{Tr}(D_{q,p} \rho)])$ or $(\text{Re}[\langle \psi | D_{q,p} | \psi \rangle])$
* **Playground**: Displacement Operators focus on [Vibrational Spectroscopy](https://chem.libretexts.org/Courses/Providence_College/Organic_Chemistry_I/05%3A_Analytical_Methods_for_Structure_Elucidation/5.04%3A_Infrared_Spectroscopy) like IR Spectroscopy:
  * movement (vibrations) of nuclei with Stretching and Bending (C-H bond) -> atoms oscillating in natural frequency, for example $\omega = \frac{E_{n+1} - E_n}{\hbar}$ = $3000 \text{ cm}^{-1}$. System jumps between Eigenstates -> molecule in vibrational levels ($n=1, 2, 3...$) = [Franck-Condon Factors](https://de.wikipedia.org/wiki/Franck-Condon-Prinzip) (shift in nuclear equilibrium described by displacement operator).
  * Vibrational Spectroscopy measures only bond oscillation (gap) between $v=0$ and $v=1$ and one at a time (single energy transitions) in 1D map. Displacement Operators measure shape to uncover quantumness (Wigner negativity with molecule in superposition or many nodes) + many bond vibrations simultaneously on 2D topological phase-space map.
* **Approach** Displacement Operator $(q,p)$ performs Phase Space Tomography (interferometry) to reconstruct Density Operator $\rho$.  
  * Measure overlap of molecule's state with shifted version of itself. Calculates expectation value $y_{q,p} = \text{Tr}(\rho\hat{D}(q,p))$ or $\chi(q,p) = \text{Tr}(\hat{\rho} \hat{D}(q,p))$. $\chi$ is **Characteristic Function** of state. **Fourier transform is Wigner Function** $W(q,p)$ > 2D map.
  * **Laguerre polynomials** $\langle n | \hat{D}(\alpha) | n \rangle = L_n(|\alpha|^2) e^{-|\alpha|^2/2}$ (where $\alpha \propto q + ip$) determine Expectation value of a displacement operator $y_{q,p} = \text{Tr}(D_{q,p}\rho)$ for a specific energy level $n$. Laguerre polynomials $L_n$ can be positive or negative depending on the radius $|\alpha|$. High-energy states are energetic, their response to specific $(q,p)$ probe different than ground state -> signal (expectation value) is (Laguerre) polynomial than just simple constant.
