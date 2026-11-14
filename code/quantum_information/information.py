"""Quanteninformationstheorie: Abstandsmaße, Datenverarbeitung, Chernoff-Exponent, Entropien, Schumacher-Kompression, Holevo-Schranke, No-Cloning, Quanten-Fisher-Information, Diamantnorm und Kanalkapazitäten.

Für quantum_information.ipynb aus quantuminformation.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: qubit_distances, fvdg_pinsker, data_processing, chernoff, entropies, schumacher, holevo_bound, no_cloning, fisher, channel_distances, capacities.
"""
import cvxpy as cp
import sys
import functools
import itertools
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq, minimize
from scipy.special import gammaln
from scipy.stats import binom


def qubit_distances():
    """21. Abstandsmaße für ein Qubit und der klassische Grenzfall (Zellen 4, 6 von quantuminformation.ipynb)."""
    global F, I2, X, Y, Z, ax, axes, bures, choi, dm, entropie, fidelity
    global fig, from_bloch, h2, hs_abstand, kanal, laenge, mfun, p, partialspur, psd_sqrt, q, r
    global rel_entropie, renyi, rho, rng, rp, rq, s, shannon, sigma, spurabstand, t, theta
    global werte, zufallskanal, zufallszustand
    rng = np.random.default_rng(2026)
    I2 = np.eye(2, dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Y = np.array([[0, -1j], [1j, 0]])
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    def dm(psi):
        """Normierte Dichtematrix |ψ><ψ|."""
        psi = np.asarray(psi, dtype=complex)
        psi = psi / np.linalg.norm(psi)
        return np.outer(psi, psi.conj())
    def from_bloch(r):
        return 0.5 * (I2 + r[0] * X + r[1] * Y + r[2] * Z)
    def mfun(A, f):
        """Matrixfunktion f(A) einer hermiteschen Matrix über die Eigenzerlegung."""
        w, V = np.linalg.eigh(A)
        return (V * f(w)) @ V.conj().T
    def psd_sqrt(A):
        return mfun(A, lambda w: np.sqrt(np.clip(w, 0, None)))
    def h2(x):
        """Binäre Entropie in Bit."""
        x = np.clip(x, 1e-300, 1)
        y = np.clip(1 - x, 1e-300, 1)
        return -(x * np.log2(x) + y * np.log2(y))
    def shannon(p):
        p = np.asarray(p, dtype=float)
        p = p[p > 1e-15]
        return -(p * np.log2(p)).sum()
    def entropie(rho):
        """Von-Neumann-Entropie in Bit."""
        return shannon(np.linalg.eigvalsh(rho))
    def renyi(rho, alpha):
        w = np.clip(np.linalg.eigvalsh(rho), 0, None)
        w = w[w > 1e-15]
        if np.isinf(alpha):
            return -np.log2(w.max())
        if np.isclose(alpha, 1):
            return shannon(w)
        return np.log2(np.sum(w ** alpha)) / (1 - alpha)
    def spurabstand(rho, sigma):
        return 0.5 * np.abs(np.linalg.eigvalsh(rho - sigma)).sum()
    def fidelity(rho, sigma):
        """F = (Tr √(√ρ σ √ρ))² = ||√ρ √σ||₁², berechnet über die Singulärwerte (numerisch stabil)."""
        return np.sum(np.linalg.svd(psd_sqrt(rho) @ psd_sqrt(sigma), compute_uv=False)) ** 2
    def bures(rho, sigma):
        return np.sqrt(max(0.0, 2 * (1 - np.sqrt(fidelity(rho, sigma)))))
    def hs_abstand(rho, sigma):
        return np.linalg.norm(rho - sigma)                         # Frobenius-Norm = Hilbert-Schmidt
    def rel_entropie(rho, sigma):
        """D(ρ||σ) in Bit; unendlich, wenn ρ Gewicht außerhalb des Trägers von σ hat."""
        ws, Vs = np.linalg.eigh(sigma)
        traeger = ws > 1e-12
        kern = Vs[:, ~traeger]
        if kern.size and np.real(np.trace(kern.conj().T @ rho @ kern)) > 1e-10:
            return np.inf
        log_sigma = (Vs[:, traeger] * np.log2(ws[traeger])) @ Vs[:, traeger].conj().T
        return -entropie(rho) - np.real(np.trace(rho @ log_sigma))
    def partialspur(rho, dims, behalten):
        """Reduzierter Zustand auf den Teilsystemen in 'behalten'."""
        n = len(dims)
        t = rho.reshape(list(dims) * 2)
        for i in sorted(set(range(n)) - set(behalten), reverse=True):
            t = np.trace(t, axis1=i, axis2=i + t.ndim // 2)
        d = int(np.prod([dims[i] for i in behalten]))
        return t.reshape(d, d)
    def zufallszustand(d, rang=None):
        """Zufälliger Zustand vom Rang 'rang' (induziertes Maß, Rang d: Hilbert-Schmidt-Maß)."""
        G = rng.normal(size=(d, rang or d)) + 1j * rng.normal(size=(d, rang or d))
        rho = G @ G.conj().T
        return rho / np.trace(rho).real
    def zufallskanal(d_ein, d_aus, n_kraus):
        """Zufälliger Kanal aus einer zufälligen Isometrie (Stinespring): Kraus-Operatoren K_k (d_aus x d_ein)."""
        n_kraus = max(n_kraus, -(-d_ein // d_aus))                 # die Isometrie braucht d_aus·n_kraus ≥ d_ein
        G = rng.normal(size=(d_aus * n_kraus, d_ein)) + 1j * rng.normal(size=(d_aus * n_kraus, d_ein))
        V, _ = np.linalg.qr(G)
        return [V[k * d_aus:(k + 1) * d_aus, :] for k in range(n_kraus)]
    def kanal(K, rho):
        return sum(k @ rho @ k.conj().T for k in K)
    def choi(K, d):
        """Choi-Matrix J = Σ_ij |i><j| ⊗ E(|i><j|) (Eingang ⊗ Ausgang)."""
        J = 0
        for i, j in itertools.product(range(d), repeat=2):
            Eij = np.zeros((d, d)); Eij[i, j] = 1
            J = J + np.kron(Eij, kanal(K, Eij))
        return J

    p, q = rng.dirichlet(np.ones(4)), rng.dirichlet(np.ones(4))
    rp, rq = np.diag(p).astype(complex), np.diag(q).astype(complex)
    print(f"Spurabstand {spurabstand(rp, rq):.6f}  | TV-Abstand {0.5 * np.abs(p - q).sum():.6f}")
    print(f"Fidelity    {fidelity(rp, rq):.6f}  | (Σ√(pq))²  {np.sum(np.sqrt(p * q)) ** 2:.6f}")
    print(f"D(ρ||σ)     {rel_entropie(rp, rq):.6f}  | KL         {np.sum(p * np.log2(p / q)):.6f}")

    sigma = dm([1, 0])
    theta = np.linspace(0, np.pi, 181)
    fig, axes = plt.subplots(1, 2, figsize=(15, 4.6), sharey=True)
    for ax, laenge in zip(axes, [1.0, 0.6]):
        werte = {k: [] for k in ["T", "sqrt(1-F)", "1-sqrt(F)", "D_B", "HS"]}
        for t in theta:
            rho = from_bloch(laenge * np.array([np.sin(t), 0, np.cos(t)]))
            F = fidelity(rho, sigma)
            werte["T"].append(spurabstand(rho, sigma)); werte["sqrt(1-F)"].append(np.sqrt(1 - F))
            werte["1-sqrt(F)"].append(1 - np.sqrt(F)); werte["D_B"].append(bures(rho, sigma))
            werte["HS"].append(hs_abstand(rho, sigma))
        ax.plot(np.degrees(theta), werte["T"], lw=3, label="Spurabstand T")
        ax.plot(np.degrees(theta), werte["sqrt(1-F)"], "--", label="√(1−F)")
        ax.plot(np.degrees(theta), werte["1-sqrt(F)"], ":", label="1−√F")
        ax.plot(np.degrees(theta), werte["D_B"], label="Bures-Abstand D_B")
        ax.plot(np.degrees(theta), werte["HS"], label="Hilbert-Schmidt ‖ρ−σ‖₂")
        ax.set_xlabel("Bloch-Winkel θ von ρ zu σ = |0⟩⟨0| [Grad]")
        ax.set_title(f"ρ mit Bloch-Vektor der Länge {laenge:g}" + (" (rein)" if laenge == 1 else " (gemischt)"))
        ax.legend()
    axes[0].set_ylabel("Abstand")
    plt.tight_layout()
    plt.show()
    r, s = 0.6 * np.array([np.sin(1.0), 0, np.cos(1.0)]), np.array([0, 0, 1.0])
    print(f"Qubit-Formel: T = {spurabstand(from_bloch(r), from_bloch(s)):.6f}, ½|r − s| = {0.5 * np.linalg.norm(r - s):.6f}")


def fvdg_pinsker():
    """22. Fuchs–van de Graaf und Pinsker an Zufallszuständen (Zellen 9 von quantuminformation.ipynb)."""
    global F, T, _, a, axes, c, d, fig, pg, pinsker, pk, pr
    global punkte_gemischt, punkte_rein, rho, rho_v, sigma, sigma_v
    punkte_gemischt, punkte_rein, pinsker = [], [], []
    for _ in range(3000):
        d = rng.integers(2, 5)
        rho, sigma = zufallszustand(d, rng.integers(1, d + 1)), zufallszustand(d, rng.integers(1, d + 1))
        punkte_gemischt.append((fidelity(rho, sigma), spurabstand(rho, sigma)))
        rho_v, sigma_v = zufallszustand(d), zufallszustand(d)                  # vollen Rangs: D ist endlich
        pinsker.append((spurabstand(rho_v, sigma_v), rel_entropie(rho_v, sigma_v)))
    for _ in range(400):
        d = rng.integers(2, 5)
        a, c = zufallszustand(d, 1), zufallszustand(d, 1)
        punkte_rein.append((fidelity(a, c), spurabstand(a, c)))
    pg, pr, pk = map(np.array, (punkte_gemischt, punkte_rein, pinsker))
    print("1 − √F ≤ T ≤ √(1−F) für alle Paare:",
          np.all(pg[:, 1] >= 1 - np.sqrt(pg[:, 0]) - 1e-9) and np.all(pg[:, 1] <= np.sqrt(1 - pg[:, 0]) + 1e-9))
    print(f"reine Paare: größte Abweichung von T = √(1−F): {np.max(abs(pr[:, 1] - np.sqrt(1 - pr[:, 0]))):.1e}")
    print(f"Pinsker: kleinstes D − 2T²/ln2 = {np.min(pk[:, 1] - 2 * pk[:, 0] ** 2 / np.log(2)):.4f} (≥ 0)")

    fig, axes = plt.subplots(1, 2, figsize=(15, 4.8))
    F = np.linspace(0, 1, 200)
    axes[0].plot(pg[:, 0], pg[:, 1], ".", ms=2, color="tab:orange", label="zufällige Paare (Rang 1 bis d)")
    axes[0].plot(pr[:, 0], pr[:, 1], ".", ms=3, color="tab:blue", label="reine Paare")
    axes[0].plot(F, np.sqrt(1 - F), "k-", label="√(1−F)")
    axes[0].plot(F, 1 - np.sqrt(F), "k--", label="1−√F")
    axes[0].set_xlabel("Fidelity F"); axes[0].set_ylabel("Spurabstand T")
    axes[0].set_title("Fuchs–van de Graaf, d = 2 bis 4"); axes[0].legend(markerscale=4)
    T = np.linspace(0, 1, 200)
    axes[1].plot(pk[:, 0], pk[:, 1], ".", ms=2, color="tab:green", label="zufällige Paare vollen Rangs")
    axes[1].plot(T, 2 * T ** 2 / np.log(2), "k-", label="Pinsker: 2T²/ln 2")
    axes[1].set_xlabel("Spurabstand T"); axes[1].set_ylabel("relative Entropie D(ρ‖σ) [Bit]")
    axes[1].set_ylim(0, 6)
    axes[1].set_title("Relative Entropie gegen Spurabstand"); axes[1].legend(markerscale=4)
    plt.tight_layout()
    plt.show()


def data_processing():
    """23. Datenverarbeitung: Kanäle machen Zustände nie unterscheidbarer (Zellen 12 von quantuminformation.ipynb)."""
    global K, _, ax, bins, d, d_aus, d_ein, fig, name, r2, rho, s2
    global sigma, v, verhaeltnis, vorher
    verhaeltnis = {"Spurabstand": [], "Bures-Abstand": [], "relative Entropie": [], "Hilbert-Schmidt": []}
    for _ in range(3000):
        d_ein, d_aus = rng.integers(2, 5), rng.integers(2, 5)
        rho, sigma = zufallszustand(d_ein), zufallszustand(d_ein)
        K = zufallskanal(d_ein, d_aus, rng.integers(2, 5))          # mindestens 2 Kraus-Operatoren: kein reiner Basiswechsel
        r2, s2 = kanal(K, rho), kanal(K, sigma)
        verhaeltnis["Spurabstand"].append(spurabstand(r2, s2) / spurabstand(rho, sigma))
        verhaeltnis["Bures-Abstand"].append(bures(r2, s2) / bures(rho, sigma))
        verhaeltnis["relative Entropie"].append(rel_entropie(r2, s2) / rel_entropie(rho, sigma))
        verhaeltnis["Hilbert-Schmidt"].append(hs_abstand(r2, s2) / hs_abstand(rho, sigma))
    for name, v in verhaeltnis.items():
        print(f"{name:18s}: größtes Verhältnis {max(v):.4f}, Anteil > 1: {np.mean(np.array(v) > 1 + 1e-9):.3f}")

    # Gegenbeispiel: Partialspur über ein maximal gemischtes System der Dimension d
    rho, sigma = zufallszustand(2), zufallszustand(2)
    for d in [2, 4, 8]:
        vorher = hs_abstand(np.kron(rho, np.eye(d) / d), np.kron(sigma, np.eye(d) / d))
        print(f"Partialspur, d = {d}: Hilbert-Schmidt nachher/vorher = {hs_abstand(rho, sigma) / vorher:.3f} (√d = {np.sqrt(d):.3f}), "
              f"Spurabstand nachher/vorher = {spurabstand(rho, sigma) / spurabstand(np.kron(rho, np.eye(d) / d), np.kron(sigma, np.eye(d) / d)):.3f}")

    fig, ax = plt.subplots(figsize=(9, 4.8))
    bins = np.linspace(0, 1.6, 81)
    for name, v in verhaeltnis.items():
        ax.hist(v, bins=bins, histtype="step", lw=2, label=name)
    ax.axvline(1, color="k", ls="--")
    ax.set_xlabel("Abstand nach dem Kanal / Abstand vorher"); ax.set_ylabel("Anzahl Paare")
    ax.set_title("3000 zufällige Paare und Kanäle (d = 2 bis 4)"); ax.legend()
    plt.show()


def chernoff():
    """24. Unterscheiden mit vielen Kopien: der Chernoff-Exponent (Zellen 15 von quantuminformation.ipynb)."""
    global F1, P_err, Q, Q_s, axes, direkt, fig, n, n_werte, p_err_kopien, rate, rho
    global s_opt, s_werte, sigma, spin_matrizen, xi
    rho = from_bloch([0, 0, 0.6])
    sigma = from_bloch([0.5, 0, 0.3])
    s_werte = np.linspace(0, 1, 1001)
    Q_s = np.array([np.trace(mfun(rho, lambda w: w ** s) @ mfun(sigma, lambda w: w ** (1 - s))).real for s in s_werte])
    Q, s_opt = Q_s.min(), s_werte[Q_s.argmin()]
    xi = -np.log(Q)
    F1 = fidelity(rho, sigma)
    print(f"T = {spurabstand(rho, sigma):.4f}, F = {F1:.4f}, Chernoff: Q = {Q:.4f} bei s = {s_opt:.3f}, ξ = {xi:.4f}")
    print(f"zum Vergleich: −ln F = {-np.log(F1):.4f}, D(ρ‖σ) = {rel_entropie(rho, sigma) * np.log(2):.4f} nat, "
          f"D(σ‖ρ) = {rel_entropie(sigma, rho) * np.log(2):.4f} nat")


    def spin_matrizen(m):
        """J_x, J_y, J_z für Spin j = m/2 in der Basis |m, i> (i Einsen, J_z = j − i)."""
        j = m / 2
        mz = j - np.arange(m + 1)
        j_plus = np.diag(np.sqrt(j * (j + 1) - mz[1:] * (mz[1:] + 1)), 1)
        return (j_plus + j_plus.T) / 2, (j_plus - j_plus.T) / 2j, np.diag(mz)


    def p_err_kopien(rho, sigma, n):
        """½(1 − T(ρ^⊗n, σ^⊗n)) über die Schur–Weyl-Blöcke. In der Eigenbasis von ρ ist Sym^m(ρ) diagonal;
    Sym^m(σ) = S diag(μ-Potenzen) S† mit S = Sym^m(U) = exp(−i 2 h·J), wenn U = exp(−i h·σ) σ in diese Basis dreht."""
        lam, Vr = np.linalg.eigh(rho)
        mu, Vs = np.linalg.eigh(sigma)
        U = Vr.conj().T @ Vs
        U = U / np.sqrt(U[0, 0] * U[1, 1] - U[0, 1] * U[1, 0])      # globale Phase weg (Determinante 1): U in SU(2)
        w, Q_ = np.linalg.eig(U)
        H = (Q_ * (1j * np.log(w))) @ np.linalg.inv(Q_)            # U = exp(−iH)
        h = [np.trace(H @ P).real / 2 for P in (X, Y, Z)]
        summe = 0.0
        for k in range(n // 2 + 1):
            m = n - 2 * k
            i = np.arange(m + 1)
            log_vielfach = np.log(float(math.comb(n, k) - (math.comb(n, k - 1) if k else 0)))
            # Wurzeln der Diagonaleinträge, Vielfachheit eingerechnet (in Logarithmen, damit nichts überläuft)
            a = np.exp(0.5 * (log_vielfach + k * np.log(lam[0] * lam[1]) + (m - i) * np.log(lam[0]) + i * np.log(lam[1])))
            b = np.exp(0.5 * (log_vielfach + k * np.log(mu[0] * mu[1]) + (m - i) * np.log(mu[0]) + i * np.log(mu[1])))
            Jx, Jy, Jz = spin_matrizen(m)
            g, W = np.linalg.eigh(2 * (h[0] * Jx + h[1] * Jy + h[2] * Jz))
            S = (W * np.exp(-1j * g)) @ W.conj().T
            A, B = np.diag(a ** 2), (S * b ** 2) @ S.conj().T
            summe += 0.25 * (a @ a + b @ b - np.abs(np.linalg.eigvalsh(A - B)).sum())
        return summe


    for n in [2, 5, 8]:
        direkt = 0.5 * (1 - spurabstand(functools.reduce(np.kron, [rho] * n), functools.reduce(np.kron, [sigma] * n)))
        print(f"n = {n}: direkt {direkt:.12f}, Blöcke {p_err_kopien(rho, sigma, n):.12f}")

    n_werte = np.array([1, 2, 3, 5, 7, 10, 15, 20, 30, 50, 75, 100, 150, 200, 300, 400])
    P_err = np.array([p_err_kopien(rho, sigma, n) for n in n_werte])
    rate = -np.log(P_err) / n_werte
    print(f"−(1/n) ln P_err: n = 10 → {rate[5]:.4f}, n = 100 → {rate[11]:.4f}, n = 400 → {rate[-1]:.4f}; ξ = {xi:.4f}")

    fig, axes = plt.subplots(1, 2, figsize=(15, 4.8))
    axes[0].semilogy(n_werte, P_err, "o-", label="exakt: ½(1 − T(ρ^⊗n, σ^⊗n))")
    axes[0].semilogy(n_werte, 0.5 * Q ** n_werte, "--", label="Chernoff-Schranke ½Qⁿ")
    axes[0].semilogy(n_werte, 0.5 * (1 - np.sqrt(1 - F1 ** n_werte)), ":", label="Fidelity-Schranke ½(1 − √(1−Fⁿ))")
    axes[0].set_xlabel("Anzahl n der Kopien"); axes[0].set_ylabel("kleinste Fehlerwahrscheinlichkeit")
    axes[0].set_title("Fehler beim Unterscheiden mit n Kopien"); axes[0].legend()
    axes[1].semilogx(n_werte, rate, "o-", label="−(1/n) ln P_err")
    axes[1].axhline(xi, color="tab:orange", ls="--", label=f"Chernoff-Exponent ξ = {xi:.3f}")
    axes[1].axhline(-np.log(F1), color="tab:green", ls=":", label=f"−ln F = {-np.log(F1):.3f}")
    axes[1].set_xlabel("Anzahl n der Kopien"); axes[1].set_ylabel("Fehlerexponent pro Kopie [nat]")
    axes[1].set_title("Der Exponent nähert sich ξ"); axes[1].legend()
    plt.tight_layout()
    plt.show()


def entropies():
    """25. Entropien: Rényi-Familie, bedingte Entropie, starke Subadditivität (Zellen 18 von quantuminformation.ipynb)."""
    global S, _, al, alphas, axes, bell, dims2, dims3, farbe, fig, linie, rang
    global rho, spektrum, ssa, werte
    fig, axes = plt.subplots(1, 3, figsize=(17, 4.6))

    alphas = np.concatenate([np.linspace(0, 0.99, 50), np.linspace(1.01, 10, 120)])
    for spektrum in [(0.25, 0.25, 0.25, 0.25), (0.7, 0.2, 0.1, 0), (0.97, 0.01, 0.01, 0.01), (1, 0, 0, 0)]:
        rho = np.diag(spektrum).astype(complex)
        linie, = axes[0].plot(alphas, [renyi(rho, a) for a in alphas], label=f"Eigenwerte {spektrum}")
        axes[0].plot(1, renyi(rho, 1), "o", color=linie.get_color())
        axes[0].axhline(renyi(rho, np.inf), color=linie.get_color(), ls=":", lw=1)
    axes[0].set_xlabel("Ordnung α"); axes[0].set_ylabel("S_α [Bit]")
    axes[0].set_title("Rényi-Entropien (Punkt: von Neumann, gepunktet: α → ∞)"); axes[0].legend(fontsize=8)

    dims2 = [2, 2]
    for rang, farbe in [(1, "tab:blue"), (2, "tab:orange"), (4, "tab:green")]:
        werte = []
        for _ in range(3000):
            rho = zufallszustand(4, rang)
            werte.append(entropie(rho) - entropie(partialspur(rho, dims2, [1])))
        axes[1].hist(werte, bins=np.linspace(-1, 1, 81), histtype="step", lw=2, color=farbe, label=f"Rang {rang}")
    bell = dm([1, 0, 0, 1])
    axes[1].axvline(entropie(bell) - entropie(partialspur(bell, dims2, [1])), color="k", ls="--", label="Bell-Zustand")
    axes[1].axvline(0, color="0.5", ls=":", label="klassische Grenze 0")
    axes[1].set_xlabel("S(A|B) [Bit]"); axes[1].set_ylabel("Anzahl Zustände")
    axes[1].set_title("Bedingte Entropie zweier Qubits"); axes[1].legend()

    dims3 = [2, 2, 2]
    ssa, al = [], []
    for _ in range(3000):
        rho = zufallszustand(8, rng.integers(1, 9))
        S = lambda behalten: entropie(partialspur(rho, dims3, behalten))
        ssa.append(S([0, 1]) + S([1, 2]) - S([0, 1, 2]) - S([1]))
        al.append(S([0, 1]) - abs(S([0]) - S([1])))
    axes[2].hist(ssa, bins=60, alpha=0.6, label="S(AB)+S(BC)−S(ABC)−S(B)")
    axes[2].hist(al, bins=60, alpha=0.6, label="Araki–Lieb: S(AB) − |S(A)−S(B)|")
    axes[2].axvline(0, color="k", ls="--")
    axes[2].set_xlabel("Abstand zur Schranke [Bit]"); axes[2].set_ylabel("Anzahl Zustände")
    axes[2].set_title("Drei Qubits, zufällige Zustände"); axes[2].legend(fontsize=9)
    plt.tight_layout()
    plt.show()
    print(f"kleinster Wert: starke Subadditivität {min(ssa):.2e}, Araki–Lieb {min(al):.2e}")


def schumacher():
    """26. Schumacher-Kompression (Zellen 21 von quantuminformation.ipynb)."""
    global S_rho, ax, dim, eps, fig, n, n_werte, p_min, qubits_pro_kopie, w
    p_min = 0.1                                                    # kleinerer Eigenwert
    S_rho = h2(p_min)


    def qubits_pro_kopie(n, eps):
        """log2(kleinste Dimension, die vom Gewicht von ρ^⊗n mindestens 1 − eps erfasst) / n.
    Die Eigenwerte (1−p)^(n−k) p^k mit Vielfachheit C(n, k) fallen mit k; man füllt von k = 0 an auf."""
        k = np.arange(n + 1)
        gewicht = binom.cdf(k, n, p_min)                           # Gewicht der Blöcke 0..k
        K = np.searchsorted(gewicht, 1 - eps)                      # erster Block, mit dem 1 − eps erreicht wird
        log_comb = gammaln(n + 1) - gammaln(k + 1) - gammaln(n - k + 1)
        log_lam = (n - K) * np.log(1 - p_min) + K * np.log(p_min)
        fehlt = (1 - eps) - (gewicht[K - 1] if K > 0 else 0)
        log_rest = np.log(fehlt) - log_lam                         # so viele Eigenvektoren braucht der angebrochene Block
        teile = list(log_comb[:K]) + [np.log(np.ceil(np.exp(log_rest))) if log_rest < 30 else log_rest]
        return np.logaddexp.reduce(teile) / np.log(2) / n


    n_werte = np.unique(np.logspace(0.5, 4, 60).astype(int))
    fig, ax = plt.subplots(figsize=(9, 4.8))
    for eps in [0.1, 0.01]:
        ax.semilogx(n_werte, [qubits_pro_kopie(n, eps) for n in n_werte], label=f"Fehler ε = {eps:g}")
    ax.axhline(S_rho, color="k", ls="--", label=f"S(ρ) = {S_rho:.3f} Bit")
    ax.axhline(1, color="0.6", ls=":", label="ohne Kompression: 1 Qubit")
    ax.set_xlabel("Anzahl n der Kopien"); ax.set_ylabel("Qubits pro Kopie")
    ax.set_title("Kleinster Unterraum mit Gewicht 1 − ε"); ax.legend()
    plt.show()

    # Kontrolle bei n = 12 durch direkte Diagonalisierung von ρ^⊗12
    n = 12
    w = np.sort(np.linalg.eigvalsh(functools.reduce(np.kron, [np.diag([1 - p_min, p_min])] * n)))[::-1]
    dim = np.searchsorted(np.cumsum(w), 1 - 0.01) + 1
    print(f"n = 12, ε = 0.01: direkt {np.log2(dim) / n:.4f} Qubits pro Kopie, Formel {qubits_pro_kopie(n, 0.01):.4f}")
    print(f"n = 10 000: ε = 0.1 → {qubits_pro_kopie(10_000, 0.1):.4f}, ε = 0.01 → {qubits_pro_kopie(10_000, 0.01):.4f} (S = {S_rho:.4f})")


def holevo_bound():
    """27. Holevo-Schranke und Accessible Information (Zellen 24 von quantuminformation.ipynb)."""
    global I_helstrom, I_scan, P_e, accessible_information, anti, axes, beschriftung, c, c_test, c_werte, chi_2, eigene
    global ergebnis, fig, halb, holevo, i, k, lab, n_tetra, n_trine, name, namen, povm_aus_parametern
    global ps, richtungen, wechselinfo, x, zust
    def wechselinfo(zustaende, ps, E):
        """I(X:Y) in Bit für das Ensemble {p_x, ρ_x} und das POVM E."""
        pxy = np.array(ps)[:, None] * np.array([[np.trace(e @ r).real for e in E] for r in zustaende])
        py = pxy.sum(axis=0)
        m = pxy > 1e-15
        return np.sum(pxy[m] * np.log2(pxy[m] / (np.array(ps)[:, None] * py[None, :])[m]))


    def holevo(zustaende, ps):
        return entropie(sum(p * r for p, r in zip(ps, zustaende))) - sum(p * entropie(r) for p, r in zip(ps, zustaende))


    def povm_aus_parametern(x, K=6, d=2):
        """Rang-1-POVM E_k = S^(−1/2) |v_k><v_k| S^(−1/2) mit S = Σ|v_k><v_k| (immer gültig)."""
        v = (x[:K * d] + 1j * x[K * d:]).reshape(K, d)
        B = [np.outer(a, a.conj()) for a in v]
        S_inv = mfun(sum(B), lambda w: 1 / np.sqrt(w))
        return [S_inv @ c @ S_inv for c in B]


    def accessible_information(zustaende, ps, starts=30):
        beste = 0
        for _ in range(starts):
            erg = minimize(lambda x: -wechselinfo(zustaende, ps, povm_aus_parametern(x)), rng.normal(size=24), method="BFGS")
            beste = max(beste, -erg.fun)
        return beste


    # (a) zwei reine Zustände mit Überlapp c
    c_werte = np.linspace(0, 1, 101)
    chi_2 = h2((1 + c_werte) / 2)
    P_e = 0.5 * (1 - np.sqrt(1 - c_werte ** 2))
    I_helstrom = 1 - h2(P_e)
    c_test, I_scan = [0.2, 0.4, 0.6, 0.8, 0.9], []
    for c in c_test:
        halb = np.arccos(c)                                        # Bloch-Winkel ±halb ergibt Überlapp c
        zust = [from_bloch([np.sin(a), 0, np.cos(a)]) for a in (halb, -halb)]
        I_scan.append(max(wechselinfo(zust, [0.5, 0.5], [from_bloch([np.sin(phi), 0, np.cos(phi)]),
                                                           from_bloch([-np.sin(phi), 0, -np.cos(phi)])])
                          for phi in np.linspace(0, np.pi, 721)))

    # (b) Trine und Tetraeder
    n_trine = [np.array([np.sin(a), 0, np.cos(a)]) for a in 2 * np.pi * np.arange(3) / 3]
    n_tetra = [np.array([0, 0, 1.0])] + [np.array([np.sqrt(8) / 3 * np.cos(b), np.sqrt(8) / 3 * np.sin(b), -1 / 3])
                                         for b in 2 * np.pi * np.arange(3) / 3]
    ergebnis = {}
    for name, richtungen in [("Trine", n_trine), ("Tetraeder", n_tetra)]:
        zust = [from_bloch(v) for v in richtungen]
        ps = [1 / len(zust)] * len(zust)
        eigene = [2 / len(zust) * r for r in zust]                 # die Zustände selbst als POVM (Trine bzw. SIC)
        anti = [2 / len(zust) * from_bloch(-v) for v in richtungen]  # die Gegenrichtungen als POVM
        ergebnis[name] = dict(chi=holevo(zust, ps), eigene=wechselinfo(zust, ps, eigene),
                              anti=wechselinfo(zust, ps, anti), numerisch=accessible_information(zust, ps))
        print(f"{name:9s}: " + ", ".join(f"{k} {v:.4f}" for k, v in ergebnis[name].items()))
    print(f"Erwartet: Trine log₂3 − 1 = {np.log2(3) - 1:.4f}, Tetraeder 2 − log₂3 = {2 - np.log2(3):.4f}")

    fig, axes = plt.subplots(1, 2, figsize=(15, 4.8))
    axes[0].plot(c_werte, chi_2, label="Holevo χ = h((1+c)/2)")
    axes[0].plot(c_werte, I_helstrom, label="Helstrom-Messung: 1 − h(P_e)")
    axes[0].plot(c_test, I_scan, "o", label="beste projektive Messung (Winkelsuche)")
    axes[0].set_xlabel("Überlapp c = |⟨ψ₀|ψ₁⟩|"); axes[0].set_ylabel("Information [Bit]")
    axes[0].set_title("Zwei reine Zustände, gleiche Priors"); axes[0].legend()
    namen = ["chi", "numerisch", "anti", "eigene"]
    beschriftung = ["Holevo χ", "Accessible Information (numerisch)", "Anti-POVM (Gegenrichtungen)", "eigene Zustände als POVM"]
    x = np.arange(2)
    for i, (k, lab) in enumerate(zip(namen, beschriftung)):
        axes[1].bar(x + (i - 1.5) * 0.2, [ergebnis[n][k] for n in ("Trine", "Tetraeder")], 0.2, label=lab)
    axes[1].axhline(1, color="k", ls="--", lw=1, label="log₂ d = 1 Bit")
    axes[1].set_ylim(0, 1.45)
    axes[1].set_xticks(x); axes[1].set_xticklabels(["Trine (3 Zustände)", "Tetraeder (4 Zustände)"])
    axes[1].set_ylabel("Information [Bit]"); axes[1].set_title("Symmetrische Ensembles eines Qubits")
    axes[1].legend(fontsize=9, ncol=2, loc="upper center")
    plt.tight_layout()
    plt.show()


def no_cloning():
    """28. No-Cloning: die beste Klonmaschine und No-Signalling (Zellen 27 von quantuminformation.ipynb)."""
    global CNOT, F_bh, F_cnot, K, P0, V, _, aus, ax, bedingt0, fig, gewicht
    global ket, nach, p0, psi, r1, r2, rho_ab, rho_b, t, theta
    # Bužek–Hillery als Isometrie: Eingang (Qubit) → Kopie 1 ⊗ Kopie 2 ⊗ Maschine
    ket = lambda *bits: np.eye(8)[int("".join(map(str, bits)), 2)]        # |Kopie 1, Kopie 2, Maschine>, Maschine 0 = ↑
    V = np.zeros((8, 2))
    V[:, 0] = np.sqrt(2 / 3) * ket(0, 0, 0) + np.sqrt(1 / 6) * (ket(0, 1, 1) + ket(1, 0, 1))
    V[:, 1] = np.sqrt(2 / 3) * ket(1, 1, 1) + np.sqrt(1 / 6) * (ket(0, 1, 0) + ket(1, 0, 0))
    print("Isometrie V†V = I:", np.allclose(V.T @ V, np.eye(2)))

    for _ in range(3):
        psi = rng.normal(size=2) + 1j * rng.normal(size=2); psi /= np.linalg.norm(psi)
        aus = dm(V @ psi)
        r1, r2 = partialspur(aus, [2, 2, 2], [0]), partialspur(aus, [2, 2, 2], [1])
        print(f"Kopie 1 = Kopie 2 = (2/3)ψ + (1/6)I: {np.allclose(r1, r2) and np.allclose(r1, 2 / 3 * dm(psi) + I2 / 6)}, "
              f"F = {np.real(psi.conj() @ r1 @ psi):.4f}")

    theta = np.linspace(0, np.pi, 181)
    F_bh, F_cnot = [], []
    CNOT = np.eye(4)[[0, 1, 3, 2]]
    for t in theta:
        psi = np.array([np.cos(t / 2), np.sin(t / 2)])
        F_bh.append(np.real(psi @ partialspur(dm(V @ psi), [2, 2, 2], [0]) @ psi))
        F_cnot.append(np.real(psi @ partialspur(dm(CNOT @ np.kron(psi, [1, 0])), [2, 2], [0]) @ psi))
    gewicht = np.sin(theta) / np.sum(np.sin(theta))                # Mittel über die Kugel
    print(f"Mittel über die Kugel: Bužek–Hillery {np.sum(gewicht * F_bh):.4f}, CNOT-Kopie {np.sum(gewicht * F_cnot):.4f}")

    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.plot(np.degrees(theta), F_bh, label="Bužek–Hillery (universell): 5/6")
    ax.plot(np.degrees(theta), F_cnot, label="CNOT-Kopie in der z-Basis: (1 + cos²θ)/2")
    ax.axhline(2 / 3, color="0.5", ls="--", label="Messen und neu präparieren, Mittel: 2/3")
    ax.set_xlabel("Bloch-Winkel θ des Eingangs [Grad]"); ax.set_ylabel("Fidelity jeder Kopie")
    ax.set_title("Klonen eines unbekannten Qubits"); ax.legend()
    plt.show()

    # No-Signalling: Alice wendet einen zufälligen Kanal an oder misst; Bobs reduzierter Zustand bleibt gleich
    rho_ab = zufallszustand(4, 1)                                  # rein, im Allgemeinen verschränkt
    rho_b = partialspur(rho_ab, [2, 2], [1])
    K = zufallskanal(2, 2, 3)
    nach = sum(np.kron(Ka, I2) @ rho_ab @ np.kron(Ka, I2).conj().T for Ka in K)
    print(f"Bob nach Alices Kanal: Spurabstand zu vorher {spurabstand(partialspur(nach, [2, 2], [1]), rho_b):.1e}")
    P0 = np.kron(dm([1, 0]), I2)
    p0 = np.trace(P0 @ rho_ab).real
    bedingt0 = partialspur(P0 @ rho_ab @ P0, [2, 2], [1]) / p0
    print(f"Alice misst σ_z: Bobs bedingter Zustand (Ergebnis 0) weicht um T = {spurabstand(bedingt0, rho_b):.3f} ab, "
          f"das Mittel über beide Ergebnisse um {spurabstand(partialspur(P0 @ rho_ab @ P0 + (np.eye(4) - P0) @ rho_ab @ (np.eye(4) - P0), [2, 2], [1]), rho_b):.1e}")


def fisher():
    """29. Quanten-Fisher-Information: Standard-Quantenlimit und Heisenberg-Limit (Zellen 30 von quantuminformation.ipynb)."""
    global G, N, N_werte, ax, bures_, dephasiert, ergebnisse, exakt, fig, formel, linie, name
    global p, psi, qfi_bures, qfi_exakt, rho
    def qfi_exakt(rho, G):
        """F_Q = 2 Σ_ij (λ_i − λ_j)²/(λ_i + λ_j) |<i|G|j>|² für ρ_θ = e^(−iθG) ρ e^(iθG)."""
        lam, V = np.linalg.eigh(rho)
        Gm = V.conj().T @ G @ V
        L = lam[:, None] + lam[None, :]
        maske = L > 1e-12
        return 2 * np.sum(((lam[:, None] - lam[None, :]) ** 2 / np.where(maske, L, 1)) * np.abs(Gm) ** 2 * maske)


    def qfi_bures(rho, G, delta=0.02):
        """F_Q aus D_B² = ¼ F_Q δ², also F_Q = 8(1 − √F)/δ²."""
        U = np.diag(np.exp(-1j * delta * np.diag(G)))              # G ist diagonal
        return 8 * (1 - np.sqrt(fidelity(rho, U @ rho @ U.conj().T))) / delta ** 2


    def dephasiert(rho, n, p):
        """Lokale Dephasierung (1−p)ρ + p ZρZ auf jedem Qubit: ρ_ab wird mit (1−2p)^Hamming(a, b) multipliziert."""
        idx = np.arange(2 ** n)
        hamming = np.array([[bin(a ^ c).count("1") for c in idx] for a in idx])
        return rho * (1 - 2 * p) ** hamming


    N_werte = np.arange(1, 9)
    ergebnisse = {}
    for p in [0.0, 0.05]:
        for name in ["Produkt", "GHZ"]:
            exakt, bures_ = [], []
            for N in N_werte:
                G = np.diag([0.5 * (N - 2 * bin(a).count("1")) for a in range(2 ** N)]).astype(complex)
                if name == "Produkt":
                    psi = functools.reduce(np.kron, [np.array([1, 1]) / np.sqrt(2)] * N)
                else:
                    psi = np.zeros(2 ** N); psi[[0, -1]] = 1 / np.sqrt(2)
                rho = dephasiert(dm(psi), N, p)
                exakt.append(qfi_exakt(rho, G)); bures_.append(qfi_bures(rho, G))
            ergebnisse[(name, p)] = (np.array(exakt), np.array(bures_))
            print(f"{name:8s} p = {p}: F_Q exakt {np.round(exakt, 3)}; größte Abweichung Bures {np.max(abs(np.array(bures_) - exakt)):.1e}")

    fig, ax = plt.subplots(figsize=(9, 4.8))
    formel = {("Produkt", 0.0): N_werte, ("GHZ", 0.0): N_werte ** 2,
              ("Produkt", 0.05): N_werte * 0.9 ** 2, ("GHZ", 0.05): N_werte ** 2 * 0.9 ** (2 * N_werte)}
    for (name, p), (exakt, bures_) in ergebnisse.items():
        linie, = ax.plot(N_werte, formel[(name, p)], "-" if p == 0 else "--", label=f"{name}, p = {p:g}: Formel")
        ax.plot(N_werte, bures_, "o", color=linie.get_color(), mfc="none", label=f"{name}, p = {p:g}: aus Bures-Abstand")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xticks(N_werte, [str(N) for N in N_werte]); ax.minorticks_off()
    ax.set_xlabel("Anzahl N der Qubits"); ax.set_ylabel("Quanten-Fisher-Information F_Q")
    ax.set_title("Phasenschätzung: F_Q = N (Produkt) gegen N² (GHZ)"); ax.legend(fontsize=8, ncol=2)
    plt.show()


def channel_distances():
    """30. Abstände zwischen Kanälen: Diamantnorm gegen mittlere Fidelity (Zellen 33 von quantuminformation.ipynb)."""
    global ID, K, ampdaempf, ax, depol, diamant_halb, ds, fehlerkanal, fig, kurven, name, ohne_ancilla
    global r, r_mittel, r_ziel, rotation, rs
    def diamant_halb(K1, K2, d=2):
        """½||E1 − E2||_◇ als SDP (Watrous): max Tr(J W) unter 0 ≤ W ≤ ρ ⊗ I, ρ Dichtematrix."""
        J = choi(K1, d) - choi(K2, d)
        W = cp.Variable((d * d, d * d), hermitian=True)
        r = cp.Variable((d, d), hermitian=True)
        nb = [W >> 0, cp.kron(r, np.eye(d)) - W >> 0, r >> 0, cp.trace(r) == 1]
        problem = cp.Problem(cp.Maximize(cp.real(cp.trace(J @ W))), nb)
        problem.solve()
        return problem.value


    def ohne_ancilla(K1, K2, gitter=60):
        """Bester Spurabstand der Ausgänge über reine Eingänge ohne Ancilla (Gitter auf der Bloch-Kugel)."""
        beste = 0
        for t in np.linspace(0, np.pi, gitter):
            for ph in np.linspace(0, 2 * np.pi, 2 * gitter, endpoint=False):
                rho = dm([np.cos(t / 2), np.exp(1j * ph) * np.sin(t / 2)])
                beste = max(beste, spurabstand(kanal(K1, rho), kanal(K2, rho)))
        return beste


    def r_mittel(K, d=2):
        F_pro = sum(abs(np.trace(k)) ** 2 for k in K) / d ** 2
        return 1 - (d * F_pro + 1) / (d + 1)


    rotation = lambda eps: [np.diag([np.exp(-1j * eps / 2), np.exp(1j * eps / 2)])]
    depol = lambda p: [np.sqrt(1 - 3 * p / 4) * I2] + [np.sqrt(p / 4) * P for P in (X, Y, Z)]
    ampdaempf = lambda g: [np.array([[1, 0], [0, np.sqrt(1 - g)]], dtype=complex), np.array([[0, np.sqrt(g)], [0, 0]], dtype=complex)]
    ID = [I2]
    print(f"Überrotation ε = 0.2: SDP {diamant_halb(ID, rotation(0.2)):.5f}, ohne Ancilla {ohne_ancilla(ID, rotation(0.2)):.5f}, "
          f"sin(ε/2) = {np.sin(0.1):.5f}")
    print(f"Depolarisation p = 0.1: SDP {diamant_halb(ID, depol(0.1)):.5f} (3p/4 = 0.075), ohne Ancilla {ohne_ancilla(ID, depol(0.1)):.5f} (p/2 = 0.05)")

    r_ziel = np.logspace(-5, -1, 13)
    kurven = {"Überrotation (kohärent)": lambda r: rotation(2 * np.arcsin(np.sqrt(1.5 * r))),
              "Depolarisation": lambda r: depol(2 * r),
              "Amplitudendämpfung": lambda r: ampdaempf(brentq(lambda g: r_mittel(ampdaempf(g)) - r, 0, 1))}
    fig, ax = plt.subplots(figsize=(9, 4.8))
    for name, fehlerkanal in kurven.items():
        rs, ds = [], []
        for r in r_ziel:
            K = fehlerkanal(r)
            rs.append(r_mittel(K)); ds.append(diamant_halb(ID, K))
        ax.loglog(rs, ds, "o-", label=name)
        print(f"{name:24s}: r = 1e-4 → ½‖·‖◇ ≈ {np.interp(np.log(1e-4), np.log(rs), ds):.2e}")
    ax.loglog(r_ziel, np.sqrt(1.5 * r_ziel), "k--", lw=1, label="√(3r/2)")
    ax.loglog(r_ziel, 1.5 * r_ziel, "k:", lw=1, label="3r/2")
    ax.set_xlabel("mittlere Fehlerrate r = 1 − F_avg"); ax.set_ylabel("½‖E − id‖◇")
    ax.set_title("Gleiche Fehlerrate, sehr verschiedene Diamantnorm"); ax.legend()
    plt.show()


def capacities():
    """31. Kanalkapazitäten (Zellen 36 von quantuminformation.ipynb)."""
    global C, CE, CE_ad, Ic, K, Q_ad, aus0, aus1, axes, ce, choi_zustand, fig
    global g, g_werte, hashing_null, ic, info_groessen, p, p_werte, werte
    def choi_zustand(K, rho_ein):
        """Gemeinsamer Zustand von Referenz R und Ausgang B, wenn eine Hälfte der Purifikation von rho_ein durch den Kanal geht."""
        w, V = np.linalg.eigh(rho_ein)
        psi = sum(np.sqrt(max(wi, 0)) * np.kron(V[:, i].conj(), V[:, i]) for i, wi in enumerate(w))   # Purifikation auf R ⊗ A
        return sum(np.kron(I2, k) @ dm(psi) @ np.kron(I2, k).conj().T for k in K)


    def info_groessen(K, rho_ein):
        rb = choi_zustand(K, rho_ein)
        S_R, S_B, S_RB = entropie(partialspur(rb, [2, 2], [0])), entropie(partialspur(rb, [2, 2], [1])), entropie(rb)
        return S_B - S_RB, S_R + S_B - S_RB                         # kohärente Information, I(R:B)


    p_werte = np.linspace(0, 1, 401)
    C, Ic, CE = [], [], []
    for p in p_werte:
        K = depol(p)
        aus0, aus1 = kanal(K, dm([1, 0])), kanal(K, dm([0, 1]))
        C.append(holevo([aus0, aus1], [0.5, 0.5]))                 # optimal: zwei orthogonale Eingänge (Symmetrie, King 2003)
        ic, ce = info_groessen(K, I2 / 2)
        Ic.append(max(ic, 0)); CE.append(ce)
    hashing_null = p_werte[np.argmax(np.array(Ic) <= 1e-9)]

    g_werte = np.linspace(0, 1, 101)
    Q_ad, CE_ad = [], []
    for g in g_werte:
        werte = [info_groessen(ampdaempf(g), np.diag([1 - q, q]).astype(complex)) for q in np.linspace(0, 1, 201)]
        Q_ad.append(max(0, max(v[0] for v in werte))); CE_ad.append(max(v[1] for v in werte))

    fig, axes = plt.subplots(1, 2, figsize=(15, 4.8))
    axes[0].plot(p_werte, CE, label="C_E: mit geteilter Verschränkung")
    axes[0].plot(p_werte, C, label="C: klassisch (Holevo, additiv)")
    axes[0].plot(p_werte, Ic, label="kohärente Information (Hashing, untere Schranke für Q)")
    axes[0].axvspan(1 / 3, 1, color="0.9", label="Q = 0 (No-Cloning, p ≥ 1/3)")
    axes[0].axvspan(hashing_null, 1 / 3, color="tab:red", alpha=0.12, label="Q unbekannt")
    axes[0].set_xlabel("Depolarisationsstärke p"); axes[0].set_ylabel("Kapazität [Bit bzw. Qubit pro Nutzung]")
    axes[0].set_title("Depolarisierender Kanal (1−p)ρ + p I/2"); axes[0].legend(fontsize=9)
    axes[1].plot(g_werte, CE_ad, label="C_E")
    axes[1].plot(g_werte, Q_ad, label="Q (exakt: degradierbar für γ ≤ ½)")
    axes[1].axvline(0.5, color="0.6", ls="--", label="γ = ½: antidegradierbar ab hier")
    axes[1].set_xlabel("Dämpfung γ"); axes[1].set_ylabel("Kapazität [Bit bzw. Qubit pro Nutzung]")
    axes[1].set_title("Amplitudendämpfung"); axes[1].legend()
    plt.tight_layout()
    plt.show()
    print(f"Hashing-Schranke wird null bei p ≈ {hashing_null:.3f}; zwischen {hashing_null:.3f} und 1/3 ist Q nicht bekannt.")
    print(f"Bei p = 0.1: C = {np.interp(0.1, p_werte, C):.3f}, C_E = {np.interp(0.1, p_werte, CE):.3f}, "
          f"kohärente Information = {np.interp(0.1, p_werte, Ic):.3f}")
    print(f"Amplitudendämpfung γ = 0.2: Q = {Q_ad[20]:.3f}, C_E = {CE_ad[20]:.3f}; γ = 0.6: Q = {Q_ad[60]:.3f}")
