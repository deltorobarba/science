"""Wigner-Funktionen für heisenbergweyl.ipynb: die Grad-Leiter im Phasenraum, kontinuierlich und für ein Qutrit.

Kontinuierlich: W(x, p) = (1/π) ∫ ψ*(x+y) ψ(x−y) e^(2ipy) dy auf einem Gitter (ħ = 1), für Zustände, die Erzeuger vom Grad
1 (Verschiebung), 2 (Quetschung), 3 (kubische Phase e^(iγx³)) und 4 (Kerr e^(−iχt n²)) aus dem Grundzustand machen.
Negativität δ = ∫|W| − 1 (Kenfack und Życzkowski 2004). Satz von Hudson (1974): Ein reiner Zustand hat genau dann W ≥ 0,
wenn er gaußsch ist. Diskret (Qutrit, d = 3): Wigner-Funktion aus `weyl.py`; nach Gross (2006) hat ein reiner Zustand
genau dann W ≥ 0, wenn er ein Stabilisatorzustand ist. Mana = ln Σ|W| misst die Negativität als Ressource („Magie“).
"""
import numpy as np
import matplotlib.pyplot as plt

import oscillator
import weyl


def wigner_grid(psi, x, p):
    """W(x, p) eines reinen Zustands ψ(x) auf dem Gitter x; p beliebig."""
    n, dx = len(x), x[1] - x[0]
    K = n // 2
    k = np.arange(-K, K + 1)
    F = np.exp(2j * np.outer(p, k) * dx)
    W = np.zeros((len(p), n))
    for j in range(n):
        a, b = j + k, j - k
        ok = (a >= 0) & (a < n) & (b >= 0) & (b < n)
        f = np.zeros(len(k), complex)
        f[ok] = np.conj(psi[a[ok]]) * psi[b[ok]]
        W[:, j] = np.real(F @ f) * dx / np.pi
    return W


def states(x, x0=2.0, r=0.8, gamma=0.15, alpha=2.2):
    """Vier reine Zustände als ψ(x), jeweils normiert; Schlüssel nennt den Grad des Erzeugers."""
    dx = x[1] - x[0]
    norm = lambda f: f / np.sqrt(np.sum(np.abs(f) ** 2) * dx)
    phi = oscillator.hermite_functions(x, 60)
    n = np.arange(60)
    logc = -abs(alpha) ** 2 / 2 + n * np.log(alpha) - 0.5 * np.array([np.sum(np.log(np.arange(1, m + 1))) for m in n])
    kerr = (np.exp(logc) * np.exp(-1j * np.pi / 2 * n ** 2)) @ phi           # e^(−iχt n²) mit χt = π/2
    return {"Grad 1: kohärent (verschobenes |0⟩)": norm(np.exp(-(x - x0) ** 2 / 2)),
            f"Grad 2: gequetscht, r = {r}": norm(np.exp(-np.exp(2 * r) * x ** 2 / 2)),
            f"Grad 3: kubische Phase, γ = {gamma}": norm(np.exp(-np.exp(-1.0) * x ** 2 / 2 + 1j * gamma * x ** 3)),
            "Grad 4: Kerr, e^(−iπn²/2)|α⟩ (Katze)": norm(kerr)}


def qutrit_states():
    d = 3
    F = weyl.fourier(d)
    e = np.eye(d)
    z9 = np.exp(2j * np.pi / 9)
    T = np.diag([1, z9, 1 / z9])              # T-Gatter eines Qutrits; ζ₃^(k³) = ζ₃^k wäre nur Z (Clifford)
    return {"Stabilisator |0⟩": e[0], "Stabilisator F|0⟩": F @ e[0],
            "T-Zustand T F|0⟩, T = diag(1, ζ₉, ζ₉⁻¹)": T @ F @ e[0], "strange state (|1⟩ − |2⟩)/√2": (e[1] - e[2]) / np.sqrt(2)}


def plot_wigner(r=0.8, gamma=0.15, alpha=2.2, x0=2.0, L=8.0, n=320, p_max=8.0, n_p=260, random_states=2000, seed=0):
    """Oben vier kontinuierliche Wigner-Funktionen, unten vier Qutrit-Zustände."""
    x = np.linspace(-L, L, n)
    p = np.linspace(-p_max, p_max, n_p)
    dxdp = (x[1] - x[0]) * (p[1] - p[0])
    cont = {k: wigner_grid(v, x, p) for k, v in states(x, x0=x0, r=r, gamma=gamma, alpha=alpha).items()}
    print("Kontinuierlich: Normierung ∫W, Negativität δ = ∫|W| − 1, kleinster Wert von W")
    for k, W in cont.items():
        print(f"  {k:40s}: ∫W = {W.sum() * dxdp:.4f}, δ = {np.round(np.abs(W).sum() * dxdp - 1, 4) + 0.0:.4f}, "
              f"min W = {np.round(W.min(), 3) + 0.0:+.3f}")
    d = 3
    stab = weyl.stabilizer_states(d)
    ws = [weyl.wigner(s, d) for s in stab]
    print(f"Qutrit (d = 3): alle {len(stab)} Stabilisatorzustände haben W ≥ 0 (kleinster Wert {min(w.min() for w in ws):+.1e}), Mana 0")
    disc = {k: weyl.wigner(v, d) for k, v in qutrit_states().items()}
    for k, W in disc.items():
        print(f"  {k:40s}: min W = {np.round(W.min(), 3) + 0.0:+.3f}, Mana = ln Σ|W| = {weyl.mana(W):.3f}")
    rng = np.random.default_rng(seed)
    mins = []
    for _ in range(random_states):
        v = rng.normal(size=d) + 1j * rng.normal(size=d)
        mins.append(weyl.wigner(v / np.linalg.norm(v), d).min())
    mins = np.array(mins)
    print(f"  {random_states} zufällige reine Zustände: {np.mean(mins < -1e-9):.1%} mit negativem W, im Mittel min W = {mins.mean():+.3f}")

    fig, axes = plt.subplots(2, 4, figsize=(16, 7.6))
    for ax, (k, W) in zip(axes[0], cont.items()):
        m = np.abs(W).max()
        ax.pcolormesh(x, p, W, cmap="RdBu_r", vmin=-m, vmax=m, shading="auto")
        ax.set_xlim(-4.5, 4.5)
        ax.set_ylim(-5, 5)
        ax.set_title(f"{k}\nδ = {np.round(np.abs(W).sum() * dxdp - 1, 3) + 0.0:.3f}", fontsize=9)
        ax.set_xlabel("x")
        ax.set_aspect("equal")
    axes[0, 0].set_ylabel("p")
    for ax, (k, W) in zip(axes[1], disc.items()):
        ax.imshow(W.T, origin="lower", cmap="RdBu_r", vmin=-1 / 3, vmax=1 / 3)
        for q in range(d):
            for pp in range(d):
                ax.text(q, pp, f"{np.round(W[q, pp], 2) + 0.0:+.2f}", ha="center", va="center", fontsize=9,
                        color="white" if abs(W[q, pp]) > 0.22 else "black")
        ax.set_xticks(range(d))
        ax.set_yticks(range(d))
        ax.set_xlabel("q")
        ax.set_title(f"{k}\nMana {weyl.mana(W):.3f}", fontsize=9)
    axes[1, 0].set_ylabel("p")
    fig.suptitle("Wigner-Funktionen: rot positiv, blau negativ. Oben kontinuierlich (Grad 1 bis 4), unten ein Qutrit", fontsize=11)
    fig.tight_layout()
    plt.show()
    return cont, disc
