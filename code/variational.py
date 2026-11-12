"""Variationsprinzip für approximation.ipynb: Wasserstoff mit Gauß-Funktionen und ein Variationsschaltkreis für die Ising-Kette.

Für jeden Versuchszustand ψ gilt ⟨ψ|H|ψ⟩/⟨ψ|ψ⟩ ≥ E₀: Die beste Funktion aus einer eingeschränkten Familie gibt eine obere
Schranke für die Grundzustandsenergie (Rayleigh-Ritz). Teil 1: das Wasserstoffatom mit K Gauß-Funktionen e^{−αr²}
(Hartree-Einheiten, Matrixelemente analytisch, Exponenten optimiert), wie in der Quantenchemie. Teil 2: der
Hamiltonsche Variationsansatz für die Ising-Kette im kritischen Querfeld mit periodischem Rand, p Lagen aus
e^{−iγ H_ZZ} e^{−iβ H_X} auf |+…+⟩, optimiert mit BFGS; nach Ho und Hsieh (SciPost Phys. 6, 029, 2019) wird er bei
p = n/2 exakt.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import eigh
from scipy.optimize import minimize

import trotter


# ---- Teil 1: Wasserstoff mit Gauß-Funktionen

def hydrogen(alphas):
    """Kleinste Energie [Hartree] und Koeffizienten für Gauß-Funktionen mit den Exponenten alphas (verallgemeinertes Eigenproblem)."""
    a = np.asarray(alphas)
    s = a[:, None] + a[None, :]
    S = (np.pi / s) ** 1.5
    T = 3 * a[:, None] * a[None, :] / s * S
    V = -2 * np.pi / s
    w, c = eigh(T + V, S)
    return w[0], c[:, 0]


def optimize_hydrogen(K, starts=6, seed=0):
    rng = np.random.default_rng(seed + K)
    best = None
    for _ in range(starts):
        x0 = np.log(np.geomspace(0.1, 30 * K, K)) + rng.normal(0, 0.3, K)
        r = minimize(lambda la: hydrogen(np.exp(la))[0], x0, method="Nelder-Mead" if K == 1 else "BFGS")
        if best is None or r.fun < best.fun:
            best = r
    return np.sort(np.exp(best.x)), best.fun


def radial(alphas, r):
    """Wellenfunktion ψ(r) aus der Lösung von `hydrogen`; eigh normiert c so, dass cᵀSc = ∫|ψ|² d³r = 1."""
    _, c = hydrogen(alphas)
    psi = (c[None, :] * np.exp(-np.asarray(alphas)[None, :] * r[:, None] ** 2)).sum(axis=1)
    return np.sign(psi[0]) * psi


# ---- Teil 2: Variationsschaltkreis für die Ising-Kette

class HVA:
    """Hamiltonscher Variationsansatz für H = −Σ Z_i Z_{i+1} − h Σ X_i auf einem Ring aus n Spins."""

    def __init__(self, n, h=1.0):
        self.n, self.h = n, h
        a, B, _ = trotter.ising(n, 1.0, h, periodic=True)
        self.a = a                                      # Diagonale von H_ZZ
        self.wX, self.VX = eigh(B)                      # H_X = B
        w, V = eigh(np.diag(a) + B)
        self.E0, self.ground = w[0], V[:, 0]
        self.H = np.diag(a) + B

    def state(self, params):
        p = len(params) // 2
        psi = np.full(2 ** self.n, 2 ** (-self.n / 2), complex)    # |+…+⟩, Grundzustand von H_X
        for g, b in zip(params[:p], params[p:]):
            psi = np.exp(-1j * g * self.a) * psi
            psi = self.VX @ (np.exp(-1j * b * self.wX) * (self.VX.conj().T @ psi))
        return psi

    def energy(self, params):
        psi = self.state(params)
        return float(np.real(np.vdot(psi, self.H @ psi)))

    def optimize(self, p, starts=10, seed=0):
        rng = np.random.default_rng(seed + p)
        best = None
        for _ in range(starts):
            r = minimize(self.energy, rng.uniform(0, np.pi / 2, 2 * p), method="BFGS")
            if best is None or r.fun < best.fun:
                best = r
        return best.x, best.fun


def plot_variational(Ks=range(1, 9), n=8, layers=range(1, 6), show_K=(1, 2, 4)):
    """Links ψ(r) am Kern, rechts der relative Energiefehler gegen die Zahl der Parameter für beide Familien."""
    print("Wasserstoff, exakt −0.5 Hartree; K Gauß-Funktionen mit optimierten Exponenten:")
    h_res = {}
    for K in Ks:
        al, E = optimize_hydrogen(K)
        h_res[K] = (al, E)
        print(f"  K = {K}: E = {E:.6f} Hartree, Fehler {E + 0.5:.1e}" + (f" (α = {al[0]:.4f}; analytisch 8/(9π) = "
              f"{8 / (9 * np.pi):.4f} und E = −4/(3π) = {-4 / (3 * np.pi):.6f})" if K == 1 else ""))
    model = HVA(n)
    print(f"Ising-Ring mit {n} Spins bei h = 1: E₀ = {model.E0:.6f}; Variationsschaltkreis mit p Lagen (2p Winkel):")
    v_res = {}
    for p in layers:
        th, E = model.optimize(p)
        F = abs(np.vdot(model.ground, model.state(th))) ** 2
        v_res[p] = E
        print(f"  p = {p}: E = {E:.6f}, Fehler {E - model.E0:.1e}, Überlapp mit dem Grundzustand {F:.6f}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    ax = axes[0]
    r = np.linspace(0, 3, 600)
    ax.plot(r, np.exp(-r) / np.sqrt(np.pi), color="black", lw=2.5, label="exakt: e^(−r)/√π, Spitze am Kern")
    for K, c in zip([k for k in show_K if k in h_res], ["tab:orange", "tab:green", "tab:blue"]):
        ax.plot(r, radial(h_res[K][0], r), color=c, lw=1.3, label=f"{K} Gauß-Funktion{'en' if K > 1 else ''}: "
                f"E = {h_res[K][1]:.4f}")
    ax.set_xlabel("Abstand vom Kern r [Bohr-Radien]")
    ax.set_ylabel("ψ(r) [Bohr^(−3/2)]")
    ax.set_title("Wasserstoff: Gauß-Funktionen sind am Kern immer flach", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[1]
    Kx = np.array(list(h_res))
    ax.semilogy(2 * Kx, [(h_res[k][1] + 0.5) / 0.5 for k in Kx], "o-", color="tab:green",
                label="Wasserstoff, K Gauß-Funktionen (K Exponenten, K Koeffizienten)")
    px = np.array(list(v_res))
    ax.semilogy(2 * px, [max((v_res[p] - model.E0) / abs(model.E0), 1e-16) for p in px], "s-", color="tab:purple",
                label=f"Ising-Ring, {n} Spins, p Lagen (2p Winkel)")
    ax.axvline(n, color="tab:purple", ls=":", lw=1)
    ax.text(n + 0.2, 1e-9, f"p = n/2 = {n // 2}", color="tab:purple", fontsize=8)
    ax.set_xlabel("Zahl der Variationsparameter")
    ax.set_ylabel("relativer Fehler (E − E₀)/|E₀|, nie negativ")
    ax.set_title("Die beste Funktion einer Familie liegt immer über der wahren Energie", fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()
