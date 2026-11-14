"""Dynamische Systeme und Chaos: Phasenraum des Pendels, logistische Abbildung und Feigenbaum, Lorenz-System, Lyapunov-Spektrum und fraktale Dimension.

Für dynamics.ipynb aus chaos.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, pendulum, logistic_map, lorenz_system, lyapunov_spectrum, fractal_dimension.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.optimize import brentq


def load():
    """16. Daten (Zellen 4 von chaos.ipynb)."""
    global BETA, RHO, SIGMA, box_counting, logistic, lorenz, lorenz_jacobian, rk4_step
    # Alles hier (numpy, scipy, matplotlib) ist in Colab vorinstalliert

    def rk4_step(f, x, dt):
        k1 = f(x)
        k2 = f(x + dt / 2 * k1)
        k3 = f(x + dt / 2 * k2)
        k4 = f(x + dt * k3)
        return x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)

    logistic = lambda r, x: r * x * (1 - x)

    SIGMA, RHO, BETA = 10.0, 28.0, 8.0 / 3.0
    def lorenz(s):
        x, y, z = s
        return np.array([SIGMA * (y - x), x * (RHO - z) - y, x * y - BETA * z])

    def lorenz_jacobian(s):
        x, y, z = s
        return np.array([[-SIGMA, SIGMA, 0.0], [RHO - z, -1.0, -x], [y, x, -BETA]])

    def box_counting(points, epsilons, shift=0.37):
        """Anzahl der belegten Kästchen der Kantenlänge ε für jede ε (Punkte als Array (N, 2)).
    Das Gitter ist um shift·ε verschoben, damit keine Ecken der Menge genau auf Kästchenrändern liegen."""
        p = (points - points.min(axis=0)) / np.ptp(points, axis=0).max()          # in das Einheitsquadrat
        return np.array([len(np.unique(np.floor((p + shift * eps) / eps).astype(np.int64), axis=0)) for eps in epsilons])

    print("Funktionen bereit")


def pendulum():
    """17. Phasenraum des Pendels und eine Lyapunov-Funktion (Zellen 6 von chaos.ipynb)."""
    global GAMMA, J0, Jpi, OM, TH, V, ax, axes, fig, pend, sol, th0
    GAMMA = 0.3
    pend = lambda g: (lambda t, s: [s[1], -np.sin(s[0]) - g * s[1]])
    V = lambda s: 0.5 * s[1] ** 2 + 1 - np.cos(s[0])        # Energie = Lyapunov-Funktion

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.8))
    TH, OM = np.meshgrid(np.linspace(-2 * np.pi, 2 * np.pi, 400), np.linspace(-3, 3, 300))
    axes[0].contour(TH, OM, 0.5 * OM ** 2 + 1 - np.cos(TH), levels=np.linspace(0.1, 4, 14), colors="grey", linewidths=0.8)
    axes[0].contour(TH, OM, 0.5 * OM ** 2 + 1 - np.cos(TH), levels=[2.0], colors="tab:red", linewidths=2)
    axes[0].plot([0, 2 * np.pi, -2 * np.pi], [0, 0, 0], "o", c="black", label="stabile Fixpunkte")
    axes[0].plot([-np.pi, np.pi], [0, 0], "x", c="tab:red", ms=10, mew=2, label="Sattelpunkte (Separatrix rot)")
    axes[0].set_title("Ohne Dämpfung: Bahnen gleicher Energie")
    for th0 in [1.0, 2.5, 3.1]:
        sol = solve_ivp(pend(GAMMA), [0, 40], [th0, 0.0], max_step=0.02)
        axes[1].plot(sol.y[0], sol.y[1], lw=1.2, label=f"Start θ = {th0}")
        axes[2].semilogy(sol.t, V(sol.y), lw=1.2, label=f"Start θ = {th0}")
    axes[1].plot(0, 0, "o", c="black")
    axes[1].set_title(f"Mit Dämpfung γ = {GAMMA}: Spiralen in den Fixpunkt")
    for ax in axes[:2]:
        ax.set_xlabel("Winkel θ [rad]")
        ax.set_ylabel("Winkelgeschwindigkeit dθ/dt [rad/Zeiteinheit]")
        ax.legend(fontsize=8)
    axes[2].set_xlabel("Zeit (Einheiten von 1/ω₀)")
    axes[2].set_ylabel("V = ½(dθ/dt)² + 1 − cos θ")
    axes[2].set_title("Die Lyapunov-Funktion fällt monoton")
    axes[2].legend(fontsize=8)
    fig.tight_layout()
    plt.show()

    J0 = np.array([[0, 1], [-1, -GAMMA]]); Jpi = np.array([[0, 1], [1, -GAMMA]])
    print(f"Eigenwerte am Fixpunkt θ = 0: {np.round(np.linalg.eigvals(J0), 3)}  (komplex, Realteil < 0: stabile Spirale)")
    print(f"Eigenwerte am Fixpunkt θ = π: {np.round(np.linalg.eigvals(Jpi), 3)}  (reell, verschiedene Vorzeichen: Sattel)")
    sol = solve_ivp(pend(GAMMA), [0, 40], [2.5, 0.0], max_step=0.02)
    print(f"Größte Zunahme von V zwischen zwei Zeitpunkten: {np.max(np.diff(V(sol.y))):.1e} (≤ 0 bis auf Rundung)")


def logistic_map():
    """18. Die logistische Abbildung: Bifurkationen und Lyapunov-Exponent (Zellen 9 von chaos.ipynb)."""
    global R, _, attractor, axes, d, deltas, fig, i, lyap, n, rs, superstable
    global x
    rs = np.linspace(2.5, 4.0, 3000)
    x = np.full_like(rs, 0.3)
    for _ in range(1000):
        x = logistic(rs, x)
    attractor = []
    lyap = np.zeros_like(rs)
    for i in range(2000):
        x = logistic(rs, x)
        lyap += np.log(np.abs(rs * (1 - 2 * x)) + 1e-300)
        if i < 300:
            attractor.append(x.copy())
    lyap /= 2000
    attractor = np.array(attractor)

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    axes[0].plot(np.repeat(rs, 300), attractor.T.ravel(), ",", c="black", alpha=0.25)
    axes[0].set_ylabel("x auf dem Attraktor")
    axes[0].set_title("Bifurkationsdiagramm der logistischen Abbildung")
    axes[1].plot(rs, lyap, lw=0.6, c="black")
    axes[1].axhline(0, color="tab:red", lw=1)
    axes[1].axhline(np.log(2), color="tab:blue", ls=":", lw=1, label="ln 2")
    axes[1].set_ylim(-2.5, 1)
    axes[1].set_xlabel("Parameter r")
    axes[1].set_ylabel("Lyapunov-Exponent λ")
    axes[1].legend()
    fig.tight_layout()
    plt.show()

    def superstable(n, r_guess, width):
        """Parameter, bei dem x = 1/2 auf dem Zyklus der Periode 2^n liegt: F_r^(2^n)(1/2) = 1/2."""
        def g(r):
            x = 0.5
            for _ in range(2 ** n):
                x = r * x * (1 - x)
            return x - 0.5
        grid = np.linspace(r_guess - width, r_guess + width, 401)
        vals = [g(r) for r in grid]
        for a_, b_, va, vb in zip(grid[:-1], grid[1:], vals[:-1], vals[1:]):
            if va * vb < 0:
                return brentq(g, a_, b_, xtol=1e-14)

    R = [2.0, 1 + np.sqrt(5)]
    for n in range(2, 9):
        d = (R[-1] - R[-2]) / 4.669                           # Schätzung für den nächsten Abstand
        R.append(superstable(n, R[-1] + d, 0.3 * d))
    deltas = [(R[k] - R[k - 1]) / (R[k + 1] - R[k]) for k in range(1, len(R) - 1)]
    print("Superstabile Parameter R_n:", ", ".join(f"{v:.6f}" for v in R))
    print("Verhältnisse (R_n − R_(n−1)) / (R_(n+1) − R_n):", ", ".join(f"{v:.4f}" for v in deltas))
    print(f"Lyapunov-Exponent bei r = 4: {lyap[-1]:.4f}   (ln 2 = {np.log(2):.4f})")
    print(f"Erstes r mit λ > 0 (Beginn des Chaos, Gitterauflösung {rs[1] - rs[0]:.4f}): {rs[np.argmax((lyap > 0) & (rs > 3.5))]:.4f}")


def lorenz_system():
    """19. Der Schmetterlingseffekt im Lorenz-System (Zellen 12 von chaos.ipynb)."""
    global DT, _, a_, ax, ax2, b_, fig, fit, intercept, k, s, sep
    global slope, times, traj_a
    DT = 0.005
    s = np.array([1.0, 1.0, 1.0])
    for _ in range(int(20 / DT)):                         # einschwingen, bis die Bahn auf dem Attraktor ist
        s = rk4_step(lorenz, s, DT)
    a_, b_ = s.copy(), s + np.array([1e-9, 0, 0])
    traj_a, sep, times = [], [], []
    for k in range(int(40 / DT)):
        a_, b_ = rk4_step(lorenz, a_, DT), rk4_step(lorenz, b_, DT)
        traj_a.append(a_)
        sep.append(np.linalg.norm(a_ - b_))
        times.append((k + 1) * DT)
    traj_a, sep, times = np.array(traj_a), np.array(sep), np.array(times)
    fit = (sep > 1e-8) & (sep < 1e-1)
    slope, intercept = np.polyfit(times[fit], np.log(sep[fit]), 1)

    fig = plt.figure(figsize=(15, 5))
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    ax.plot(*traj_a.T, lw=0.4, c="tab:blue")
    ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z")
    ax.set_title("Lorenz-Attraktor (σ = 10, ρ = 28, β = 8/3)")
    ax2 = fig.add_subplot(1, 2, 2)
    ax2.semilogy(times, sep, c="black", lw=1, label="Abstand der beiden Trajektorien")
    ax2.semilogy(times[fit], np.exp(intercept + slope * times[fit]), c="tab:red", lw=2, label=f"Anpassung: λ ≈ {slope:.2f}")
    ax2.set_xlabel("Zeit t")
    ax2.set_ylabel("Abstand |δ(t)|")
    ax2.set_title("Startabstand 10⁻⁹")
    ax2.legend()
    fig.tight_layout()
    plt.show()
    print(f"Wachstumsrate aus der Anpassung: {slope:.3f};  Vorhersagehorizont von 10⁻⁹ bis 1: ln(10⁹)/λ ≈ {np.log(1e9) / slope:.0f} Zeiteinheiten")


def lyapunov_spectrum():
    """20. Das Spektrum der Lyapunov-Exponenten und die Dimension des Lorenz-Attraktors (Zellen 15 von chaos.ipynb)."""
    global D_KY, N_ORTHO, Q, Rm, T_TOTAL, ax, c, fig, history, i, j, k
    global lam, log_sums, lorenz_with_tangent, n_steps, signs, state, t_hist
    def lorenz_with_tangent(state):
        s, W = state[:3], state[3:].reshape(3, 3)
        return np.concatenate([lorenz(s), (lorenz_jacobian(s) @ W).ravel()])

    state = np.concatenate([traj_a[-1], np.eye(3).ravel()])
    T_TOTAL, N_ORTHO = 500.0, 10
    log_sums, history = np.zeros(3), []
    n_steps = int(T_TOTAL / DT)
    for k in range(1, n_steps + 1):
        state = rk4_step(lorenz_with_tangent, state, DT)
        if k % N_ORTHO == 0:
            Q, Rm = np.linalg.qr(state[3:].reshape(3, 3))
            signs = np.sign(np.diag(Rm))
            log_sums += np.log(np.abs(np.diag(Rm)))
            state[3:] = (Q * signs).ravel()
            history.append(log_sums / (k * DT))
    history = np.array(history)
    lam = history[-1]

    j = np.max(np.nonzero(np.cumsum(lam) >= 0)[0]) + 1
    D_KY = j + np.sum(lam[:j]) / abs(lam[j])

    fig, ax = plt.subplots(figsize=(10, 4.5))
    t_hist = np.arange(1, len(history) + 1) * N_ORTHO * DT
    for i, c in enumerate(["tab:red", "tab:green", "tab:blue"]):
        ax.plot(t_hist, history[:, i], c=c, label=f"λ{i + 1} → {lam[i]:.3f}")
    ax.set_xscale("log")
    ax.set_xlabel("Mittelungszeit T")
    ax.set_ylabel("laufender Mittelwert λᵢ(T)")
    ax.set_title("Konvergenz der Lyapunov-Exponenten (Lorenz)")
    ax.legend()
    fig.tight_layout()
    plt.show()
    print(f"Lyapunov-Spektrum: λ1 = {lam[0]:.3f}, λ2 = {lam[1]:.3f}, λ3 = {lam[2]:.3f}")
    print(f"Summe: {lam.sum():.3f}   (Divergenz −σ − 1 − β = {-SIGMA - 1 - BETA:.3f})")
    print(f"Kaplan-Yorke-Dimension: D = {j} + {np.sum(lam[:j]):.3f}/{abs(lam[j]):.3f} = {D_KY:.3f}")


def fractal_dimension():
    """21. Fraktale Dimension: Kochkurve und Hénon-Attraktor (Zellen 18 von chaos.ipynb)."""
    global A_H, B_H, D_KY_h, N_H, N_eps, Q, Rm, _, axes, c, densify, eps
    global eps_sets, fig, hen, i, koch, koch_pts, lam_h, log_sums, name, pts, ref, results
    global slope, v, x, y
    def koch(level):
        pts = np.array([[0.0, 0.0], [1.0, 0.0]])
        rot = np.array([[0.5, -np.sqrt(3) / 2], [np.sqrt(3) / 2, 0.5]])          # Drehung um 60°
        for _ in range(level):
            new = [pts[0]]
            for p, q in zip(pts[:-1], pts[1:]):
                d = (q - p) / 3
                new += [p + d, p + d + rot @ d, p + 2 * d, q]
            pts = np.array(new)
        return pts

    def densify(pts, n=20):
        """Zusätzliche Punkte auf jeder Strecke, damit kleine Kästchen die Kurve nicht verfehlen."""
        s = np.linspace(0, 1, n, endpoint=False)[:, None, None]
        return (pts[:-1] + s * (pts[1:] - pts[:-1])).reshape(-1, 2)

    koch_pts = densify(koch(7))

    A_H, B_H = 1.4, 0.3
    N_H = 400_000
    hen = np.empty((N_H, 2))
    x, y = 0.1, 0.1
    for _ in range(1000):
        x, y = 1 - A_H * x * x + y, B_H * x
    log_sums, v = np.zeros(2), np.eye(2)
    for i in range(N_H):
        x, y = 1 - A_H * x * x + y, B_H * x
        hen[i] = x, y
        Q, Rm = np.linalg.qr(np.array([[-2 * A_H * x, 1.0], [B_H, 0.0]]) @ v) if i < 100_000 else (None, None)
        if Q is not None:
            log_sums += np.log(np.abs(np.diag(Rm)))
            v = Q
    lam_h = log_sums / 100_000
    D_KY_h = 1 + lam_h[0] / abs(lam_h[1])

    eps_sets = {"Kochkurve": 3.0 ** -np.arange(2, 7), "Hénon": np.logspace(-3, -1, 10)}
    fig, axes = plt.subplots(1, 3, figsize=(17, 4.8))
    axes[0].plot(*koch(7).T, lw=0.5, c="black")                     # die Kurve selbst; koch_pts enthält sie 20-mal versetzt
    axes[0].set_aspect("equal")
    axes[0].set_title("Kochkurve, 7. Stufe")
    axes[0].set_xlabel("x"); axes[0].set_ylabel("y")
    axes[1].plot(*hen[:50_000].T, ",", c="black", alpha=0.5)
    axes[1].set_title(f"Hénon-Attraktor (a = {A_H}, b = {B_H})")
    axes[1].set_xlabel("x"); axes[1].set_ylabel("y")
    results = {}
    for name, pts, c, ref in [("Kochkurve", koch_pts, "tab:blue", np.log(4) / np.log(3)), ("Hénon", hen, "tab:red", D_KY_h)]:
        eps = eps_sets[name]
        N_eps = box_counting(pts, eps)
        slope = np.polyfit(np.log(1 / eps), np.log(N_eps), 1)[0]
        results[name] = slope
        print(f"{name}: N(ε) = {N_eps.tolist()}")
        axes[2].loglog(1 / eps, N_eps, "o-", c=c, label=f"{name}: Steigung {slope:.3f} (Vergleich {ref:.3f})")
    axes[2].set_xlabel("1/ε")
    axes[2].set_ylabel("Zahl der belegten Kästchen N(ε)")
    axes[2].set_title("Box-Counting")
    axes[2].legend(fontsize=8)
    fig.tight_layout()
    plt.show()

    print(f"Kochkurve: Box-Counting {results['Kochkurve']:.3f}, exakt ln4/ln3 = {np.log(4) / np.log(3):.4f}")
    print(f"Hénon: λ1 = {lam_h[0]:.3f}, λ2 = {lam_h[1]:.3f} (Summe {lam_h.sum():.3f}, ln 0.3 = {np.log(0.3):.3f}); "
          f"Kaplan-Yorke {D_KY_h:.3f}, Box-Counting {results['Hénon']:.3f}")
