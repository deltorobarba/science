"""Synchronisation für stability.ipynb: das Kuramoto-Modell als Phasenübergang.

N Oszillatoren mit Eigenfrequenzen ω_j, jeder an die mittlere Phase gekoppelt: dθ_j/dt = ω_j + K·r·sin(ψ − θ_j) mit dem
Ordnungsparameter r·e^{iψ} = (1/N) Σ e^{iθ_j}. Bei einer Lorentz-Verteilung der Frequenzen (Breite γ) ist der
ungeordnete Zustand stabil, solange K < K_c = 2γ; sein Eigenwert ist K/2 − γ. Darüber gilt r = √(1 − K_c/K)
(exakt im Limes N → ∞, Ott und Antonsen 2008). Frequenzen deterministisch aus den Quantilen gewählt (weniger Rauschen).
"""
import numpy as np
import matplotlib.pyplot as plt


def frequencies(N, gamma):
    q = (np.arange(N) + 0.5) / N
    return gamma * np.tan(np.pi * (q - 0.5))


def simulate(K, omega, T=200.0, dt=0.02, seed=0):
    """Euler-Integration; gibt den mittleren Ordnungsparameter der zweiten Hälfte und die Endphasen zurück."""
    rng = np.random.default_rng(seed)
    theta = rng.uniform(0, 2 * np.pi, len(omega))
    steps = int(T / dt)
    rs = []
    for k in range(steps):
        z = np.mean(np.exp(1j * theta))
        theta += dt * (omega + K * np.abs(z) * np.sin(np.angle(z) - theta))
        if k >= steps // 2:
            rs.append(np.abs(z))
    return np.mean(rs), theta


def plot_kuramoto(N=2000, gamma=0.5, Ks=np.linspace(0, 4, 41), show=(0.6, 1.5, 3.0)):
    """Links die Phasen auf dem Kreis für drei Kopplungen, rechts r gegen K mit der Theorie."""
    Ks = np.asarray(Ks, float)
    omega = frequencies(N, gamma)
    Kc = 2 * gamma
    rs = [simulate(K, omega)[0] for K in Ks]
    theory = np.sqrt(np.clip(1 - Kc / np.maximum(Ks, 1e-9), 0, None))
    print(f"Kuramoto, {N} Oszillatoren, Lorentz-Frequenzen mit γ = {gamma}: kritische Kopplung K_c = 2γ = {Kc}")
    for k in sorted({int(np.argmin(np.abs(Ks - K))) for K in (0.5, 1.0, 1.5, 2.0, 3.0, 4.0)}):
        print(f"  K = {Ks[k]:.1f}: Eigenwert des ungeordneten Zustands K/2 − γ = {Ks[k] / 2 - gamma:+.2f}; "
              f"r gemessen {rs[k]:.3f}, Theorie {theory[k]:.3f}")
    fig = plt.figure(figsize=(15, 4.8))
    gs = fig.add_gridspec(1, 4, width_ratios=[1, 1, 1, 2.2])
    for i, K in enumerate(show):
        ax = fig.add_subplot(gs[0, i], projection="polar")
        r, th = simulate(K, omega, T=100)
        ax.scatter(th % (2 * np.pi), np.ones(N), s=2, alpha=0.3, color="tab:blue")
        z = np.mean(np.exp(1j * th))
        ax.annotate("", xy=(np.angle(z), np.abs(z)), xytext=(0, 0), arrowprops=dict(color="tab:red", lw=2))
        ax.set_ylim(0, 1.1)
        ax.set_yticks([])
        ax.set_xticks([])
        ax.set_title(f"K = {K:g}: r = {np.abs(z):.2f}", fontsize=10)
    ax = fig.add_subplot(gs[0, 3])
    ax.plot(Ks, rs, "o", color="black", label=f"Simulation, N = {N}")
    kk = np.linspace(0, Ks[-1], 400)
    ax.plot(kk, np.sqrt(np.clip(1 - Kc / np.maximum(kk, 1e-9), 0, None)), color="tab:red", label="Theorie √(1 − K_c/K)")
    ax.axvline(Kc, color="grey", ls=":", label=f"K_c = 2γ = {Kc:g}: Eigenwert wird null")
    ax.set_xlabel("Kopplung K")
    ax.set_ylabel("Ordnungsparameter r")
    ax.set_title("Synchronisation setzt ein, wo der ungeordnete Zustand instabil wird", fontsize=10)
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    plt.show()
    return np.array(rs)
