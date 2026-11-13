"""Trotter-Zerlegung für approximation.ipynb: Zeitentwicklung einer Ising-Kette in kleinen Schritten, Fehler und Rauschen.

H = A + B mit A = −J Σ Z_i Z_{i+1} (diagonal) und B = −h Σ X_i. Ein Quantenschaltkreis kann e^{−iAt} und e^{−iBt}
einzeln bauen, aber nicht e^{−iHt}, weil A und B nicht vertauschen. Die Trotter-Formel erster Ordnung
(e^{−iBΔt} e^{−iAΔt})^n hat einen Fehler proportional zu Δt, die symmetrische Formel zweiter Ordnung
(e^{−iBΔt/2} e^{−iAΔt} e^{−iBΔt/2})^n einen proportional zu Δt². Jeder Schritt kostet 2(n−1) CNOT-Gatter; mit einem
einfachen Rauschmodell (jedes CNOT gelingt mit Wahrscheinlichkeit 1 − ε) entsteht eine optimale Schrittzahl.
Exakt gerechnet mit dichten Matrizen (8 Qubits: 256 Zustände), ohne Hardware.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import eigh


def ising(n, J=1.0, h=1.0, periodic=False):
    """Diagonale von A (als Vektor) und Matrix B für n Spins; Zustand |b₀ b₁ …⟩ mit b = 0 für Z = +1."""
    idx = np.arange(2 ** n)
    z = 1 - 2 * ((idx[:, None] >> np.arange(n)[::-1]) & 1)
    bonds = [(i, i + 1) for i in range(n - 1)] + ([(n - 1, 0)] if periodic else [])
    a = -J * sum(z[:, i] * z[:, j] for i, j in bonds).astype(float)
    B = np.zeros((2 ** n, 2 ** n))
    for q in range(n):
        B[idx ^ (1 << (n - 1 - q)), idx] = -h
    return a, B, z


class Evolution:
    """Exakte und Trotter-Zeitentwicklung für H = diag(a) + B."""

    def __init__(self, a, B):
        self.a = a
        self.wB, self.VB = eigh(B)
        self.w, self.V = eigh(np.diag(a) + B)

    def exact(self, psi, t):
        return self.V @ (np.exp(-1j * self.w * t) * (self.V.conj().T @ psi))

    def _eB(self, psi, dt):
        return self.VB @ (np.exp(-1j * self.wB * dt) * (self.VB.conj().T @ psi))

    def trotter(self, psi, t, steps, order):
        dt = t / steps
        for _ in range(steps):
            if order == 1:
                psi = self._eB(np.exp(-1j * self.a * dt) * psi, dt)
            else:
                psi = self._eB(np.exp(-1j * self.a * dt) * self._eB(psi, dt / 2), dt / 2)
        return psi


def plot_trotter(n=8, T=2.0, dt_show=0.25, steps=(1, 2, 4, 8, 16, 32, 64, 128), eps=(1e-3, 1e-4)):
    """Links die Magnetisierung exakt und mit Trotter-Schritten, rechts die Untreue bei Zeit T gegen die Schrittzahl."""
    a, B, z = ising(n)
    ev = Evolution(a, B)
    psi0 = np.full(2 ** n, 2 ** (-n / 2), complex)      # |+…+⟩: Grundzustand des Querfelds, dann die Kopplung einschalten
    corr = np.mean([z[:, i] * z[:, i + 1] for i in range(n - 1)], axis=0)   # ⟨Z_i Z_i+1⟩, gemittelt über die Kette
    comm = np.diag(a) @ B - B @ np.diag(a)
    norm_c = np.linalg.norm(comm, 2)
    cnots = 2 * (n - 1)
    print(f"Ising-Kette mit {n} Spins, J = h = 1, Start |+…+⟩; ‖[A, B]‖ = {norm_c:.1f}; "
          f"je Trotter-Schritt {cnots} CNOT-Gatter")
    psiT = ev.exact(psi0, T)
    rows = []
    for s in steps:
        r = [s]
        for order in (1, 2):
            psi = ev.trotter(psi0, T, s, order)
            r += [np.linalg.norm(psi - psiT), 1 - abs(np.vdot(psiT, psi)) ** 2]
        rows.append(r)
    rows = np.array(rows)
    print(f"Bei t = {T:g}: Abstand ‖ψ_Trotter − ψ_exakt‖ (Schranke erster Ordnung t²‖[A,B]‖/(2·Schritte)):")
    for s, d1, u1, d2, u2 in rows:
        print(f"  {int(s):3d} Schritte ({int(s) * cnots:4d} CNOT): erste Ordnung {d1:.1e} (Schranke "
              f"{T ** 2 * norm_c / (2 * s):.1e}), zweite Ordnung {d2:.1e}")
    noisy = {}
    for e in eps:
        for order, col in ((1, 2), (2, 4)):
            total = 1 - (1 - rows[:, col]) * (1 - e) ** (rows[:, 0] * cnots)
            k = int(np.argmin(total))
            noisy[(e, order)] = total
            print(f"  mit Rauschen ε = {e:g} je CNOT, {'erste' if order == 1 else 'zweite'} Ordnung: am besten "
                  f"{int(rows[k, 0])} Schritte, Untreue {total[k]:.3f}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    ax = axes[0]
    tt = np.linspace(0, 2 * T, 201)
    exact = [np.real(np.vdot(p, corr * p)) for p in (ev.exact(psi0, t) for t in tt)]
    ax.plot(tt, exact, color="black", lw=2.5, label="exakt")
    ts = np.arange(0, 2 * T + 1e-9, dt_show)
    for order, c, m in ((1, "tab:red", "s"), (2, "tab:blue", "o")):
        vals, psi = [], psi0.copy()
        for k in range(len(ts)):
            vals.append(np.real(np.vdot(psi, corr * psi)))
            psi = ev.trotter(psi, dt_show, 1, order)
        dev = np.max(np.abs(np.array(vals) - np.interp(ts, tt, exact)))
        print(f"  Korrelation mit Δt = {dt_show:g} bis t = {2 * T:g}, {'erste' if order == 1 else 'zweite'} Ordnung: "
              f"größte Abweichung {dev:.3f}")
        ax.plot(ts, vals, m + "-", color=c, ms=4, lw=1, label=f"Trotter {'erster' if order == 1 else 'zweiter'} Ordnung, Δt = {dt_show:g}")
    ax.set_xlabel("Zeit t [ħ/J]")
    ax.set_ylabel("Korrelation benachbarter Spins ⟨Z_i Z_i+1⟩")
    ax.set_title(f"Ising-Kette, {n} Spins: Kopplung eingeschaltet bei t = 0", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[1]
    ax.loglog(rows[:, 0], rows[:, 2], "s--", color="tab:red", lw=1, label="erste Ordnung, nur Trotter (∝ 1/Schritte²)")
    ax.loglog(rows[:, 0], rows[:, 4], "o--", color="tab:blue", lw=1, label="zweite Ordnung, nur Trotter (∝ 1/Schritte⁴)")
    e = eps[0]
    ax.loglog(rows[:, 0], noisy[(e, 1)], "s-", color="tab:red", lw=2, label=f"erste Ordnung mit Rauschen ε = {e:g}")
    ax.loglog(rows[:, 0], noisy[(e, 2)], "o-", color="tab:blue", lw=2, label=f"zweite Ordnung mit Rauschen ε = {e:g}")
    ax.loglog(rows[:, 0], noisy[(eps[1], 2)], "o:", color="tab:blue", lw=1.2, label=f"zweite Ordnung mit ε = {eps[1]:g}")
    ax.set_ylim(1e-7, 2)
    ax.set_xlabel("Zahl der Trotter-Schritte bis t = 2")
    ax.set_ylabel("Untreue 1 − |⟨ψ_exakt|ψ⟩|²")
    ax.set_title("Mehr Schritte: weniger Näherungsfehler, mehr Gatterrauschen", fontsize=10)
    ax.legend(fontsize=7.5, loc="lower left")
    fig.tight_layout()
    plt.show()
