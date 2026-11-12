"""Chaos für stability.ipynb: Lyapunov-Exponenten in der logistischen Abbildung, bei Lorenz und bei Sternbahnen in einer Galaxie.

Schritt 1: die logistische Abbildung x → r·x·(1 − x) (Feigenbaum-Szenario) und das Lorenz-System (σ = 10, ρ = 28, β = 8/3),
Lyapunov-Exponent nach Benettin (Bahn und linearisierte Störung, die Störung immer wieder auf Länge 1 gesetzt).
Schritt 2: Sternbahnen im Potential von Hénon und Heiles (1964, ein Modell für die Bewegung von Sternen in einer Galaxie),
viele Bahnen auf einmal mit dem symplektischen Störmer-Verlet-Verfahren; dazu die Kirkwood-Lücken im Asteroidengürtel aus
der Small-Body Database des JPL (ssd-api.jpl.nasa.gov, große Halbachsen der nummerierten Asteroiden, mit requests und Cache).
"""
import time
from pathlib import Path

import numpy as np
import requests
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp


# ---- Schritt 1: logistische Abbildung und Lorenz

def logistic(rs, n_skip=1000, n_keep=300, x0=0.3):
    """Für jedes r: die letzten n_keep Werte (Attraktor) und den Lyapunov-Exponenten ⟨ln|r(1 − 2x)|⟩."""
    x = np.full(len(rs), x0)
    for _ in range(n_skip):
        x = rs * x * (1 - x)
    keep = np.empty((n_keep, len(rs)))
    lyap = np.zeros(len(rs))
    for k in range(n_keep * 10):
        lyap += np.log(np.abs(rs * (1 - 2 * x)) + 1e-300)
        x = rs * x * (1 - x)
        if k < n_keep:
            keep[k] = x
    return keep, lyap / (n_keep * 10)


def _lorenz(t, u, s=10.0, r=28.0, b=8 / 3):
    x, y, z = u
    return [s * (y - x), x * (r - z) - y, x * y - b * z]


def _lorenz_tangent(t, w, s=10.0, r=28.0, b=8 / 3):
    x, y, z, dx, dy, dz = w
    return [s * (y - x), x * (r - z) - y, x * y - b * z,
            s * (dy - dx), (r - z) * dx - dy - x * dz, y * dx + x * dy - b * dz]


def lorenz_lyapunov(T=1000.0, segment=2.0):
    """Größter Lyapunov-Exponent: Bahn und linearisierte Störung zusammen integrieren, die Störung nach jedem Abschnitt
    auf Länge 1 zurücksetzen und die Logarithmen der Streckungen mitteln (Benettin und andere 1980)."""
    u = solve_ivp(_lorenz, (0, 20), [1.0, 1.0, 1.0], rtol=1e-10, atol=1e-12).y[:, -1]
    w = np.concatenate([u, [1.0, 0.0, 0.0]])
    total = 0.0
    for _ in range(int(T / segment)):
        w = solve_ivp(_lorenz_tangent, (0, segment), w, rtol=1e-10, atol=1e-12).y[:, -1]
        d = np.linalg.norm(w[3:])
        total += np.log(d)
        w[3:] /= d
    return total / T, u


def plot_logistic_lorenz(r_min=2.8, r_max=4.0, n_r=1500, deltas=(1e-10, 1e-7, 1e-4)):
    """Links das Bifurkationsdiagramm mit dem Lyapunov-Exponenten darunter, rechts zwei Lorenz-Bahnen, die sich trennen."""
    rs = np.linspace(r_min, r_max, n_r)
    keep, lyap = logistic(rs)
    chaos_start = rs[np.argmax((lyap > 0.01) & (rs > 3.5))]
    print(f"Logistische Abbildung: λ < 0 bis r ≈ {chaos_start:.3f} (Feigenbaum: Chaos ab r = 3.5699); "
          f"bei r = 4 ist λ = {lyap[-1]:.3f} (exakt ln 2 = {np.log(2):.3f}); bei r = 3.83 (Fenster mit Periode 3) "
          f"λ = {lyap[np.argmin(np.abs(rs - 3.83))]:.3f}")
    lam, u0 = lorenz_lyapunov()
    print(f"Lorenz: größter Lyapunov-Exponent {lam:.3f} pro Zeiteinheit (Literatur 0.906); ein Fehler wächst je Zeiteinheit "
          f"um den Faktor {np.exp(lam):.2f}")
    t = np.linspace(0, 40, 4001)
    fig = plt.figure(figsize=(16, 5.6))
    gs = fig.add_gridspec(2, 2, height_ratios=[2, 1], width_ratios=[1.15, 1])
    ax = fig.add_subplot(gs[0, 0])
    ax.plot(np.repeat(rs[None], keep.shape[0], 0).ravel(), keep.ravel(), ",", color="black", alpha=0.3)
    ax.set_ylabel("x nach dem Einschwingen")
    ax.set_title("Logistische Abbildung x → r·x·(1 − x): Verdopplungen, dann Chaos", fontsize=10)
    ax.set_xlim(r_min, r_max)
    ax.tick_params(labelbottom=False)
    ax2 = fig.add_subplot(gs[1, 0], sharex=ax)
    ax2.plot(rs, lyap, color="tab:blue", lw=0.8)
    ax2.axhline(0, color="black", lw=0.8)
    ax2.fill_between(rs, 0, lyap, where=lyap > 0, color="tab:red", alpha=0.4, label="λ > 0: Chaos")
    ax2.set_ylim(-1.5, 1)
    ax2.set_xlabel("Parameter r")
    ax2.set_ylabel("Lyapunov-Exponent λ")
    ax2.legend(fontsize=8, loc="lower left")
    ax3 = fig.add_subplot(gs[:, 1])
    ref = solve_ivp(_lorenz, (0, t[-1]), u0, t_eval=t, rtol=1e-11, atol=1e-13).y
    print("Vorhersagbarkeit: Wann ist der Abstand zweier Bahnen auf 1 gewachsen (Attraktor etwa 40 breit)?")
    for d0, c in zip(deltas, ["tab:purple", "tab:green", "tab:orange"]):
        other = solve_ivp(_lorenz, (0, t[-1]), u0 + np.array([d0, 0, 0]), t_eval=t, rtol=1e-11, atol=1e-13).y
        dist = np.linalg.norm(other - ref, axis=0)
        t1 = t[np.argmax(dist > 1)]
        print(f"  Anfangsfehler {d0:.0e}: nach t = {t1:.1f} (Schätzung ln(1/δ)/λ = {np.log(1 / d0) / lam:.1f})")
        ax3.semilogy(t, dist, color=c, lw=1, label=f"Anfangsfehler {d0:.0e}")
    ax3.semilogy(t, deltas[0] * np.exp(lam * t), "k--", lw=1, label=f"e^(λt) mit λ = {lam:.2f}")
    ax3.set_ylim(min(deltas) / 10, 100)
    ax3.set_xlabel("Zeit")
    ax3.set_ylabel("Abstand zweier Lorenz-Bahnen")
    ax3.set_title("Lorenz: Jeder Anfangsfehler wächst exponentiell, bis er so groß ist wie der Attraktor", fontsize=10)
    ax3.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    plt.show()
    return lam


# ---- Schritt 2: Hénon-Heiles und Kirkwood-Lücken

def _force(x, y):
    return -x - 2 * x * y, -y - x ** 2 + y ** 2


def _potential(x, y):
    return 0.5 * (x ** 2 + y ** 2) + x ** 2 * y - y ** 3 / 3


def henon_heiles(E, n_orbits=60, T=1000.0, dt=0.01, d0=1e-8, renorm=50, seed=0):
    """Viele Bahnen gleicher Energie E auf einmal; Start auf dem Schnitt x = 0 mit px > 0.

    Gibt die Punkte des Poincaré-Schnitts (y, py, Nummer der Bahn) und den Lyapunov-Exponenten jeder Bahn zurück.
    """
    rng = np.random.default_rng(seed)
    y, py = [], []
    while len(y) < n_orbits:                                    # zufällige Punkte im erlaubten Bereich des Schnitts
        yy, pp = rng.uniform(-0.6, 1.0), rng.uniform(-0.7, 0.7)
        if E - _potential(0, yy) - 0.5 * pp ** 2 > 0:
            y.append(yy)
            py.append(pp)
    y, py = np.array(y), np.array(py)
    x = np.zeros(n_orbits)
    px = np.sqrt(2 * (E - _potential(0, y)) - py ** 2)
    S = np.array([x, y, px, py])
    D = S + d0 * rng.normal(size=S.shape) / 2
    total = np.zeros(n_orbits)
    pts = []
    steps = int(T / dt)
    for k in range(steps):
        for Z in (S, D):                                        # Störmer-Verlet (symplektisch, Energie bleibt erhalten)
            fx, fy = _force(Z[0], Z[1])
            Z[2] += 0.5 * dt * fx
            Z[3] += 0.5 * dt * fy
            xo = Z[0].copy() if Z is S else None
            Z[0] += dt * Z[2]
            Z[1] += dt * Z[3]
            fx, fy = _force(Z[0], Z[1])
            Z[2] += 0.5 * dt * fx
            Z[3] += 0.5 * dt * fy
            if Z is S:
                cross = (xo < 0) & (Z[0] >= 0) & (Z[2] > 0)
                if cross.any():
                    w = -xo[cross] / (Z[0][cross] - xo[cross])
                    pts.append(np.array([Z[1][cross] - (1 - w) * dt * Z[3][cross], Z[3][cross], np.flatnonzero(cross)]))
        if (k + 1) % renorm == 0:
            d = np.linalg.norm(D - S, axis=0)
            total += np.log(d / d0)
            D = S + (D - S) * (d0 / d)
    pts = np.concatenate(pts, axis=1) if pts else np.zeros((3, 0))
    return pts, total / T


def asteroids(cache, limit=200000):
    """Große Halbachsen [AU] der ersten `limit` nummerierten Asteroiden (JPL Small-Body Database)."""
    path = Path(cache) / f"asteroids_a_{limit}.npy"
    if path.exists():
        return np.load(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    for i in range(3):
        try:
            r = requests.get("https://ssd-api.jpl.nasa.gov/sbdb_query.api",
                             params={"fields": "a", "sb-kind": "a", "sb-ns": "n", "limit": limit}, timeout=180)
            if r.ok:
                a = np.array([float(row[0]) for row in r.json()["data"] if row[0] is not None])
                np.save(path, a)
                return a
        except (requests.RequestException, ValueError):
            pass
        time.sleep(5 * (i + 1))
    raise OSError("JPL Small-Body Database nicht erreichbar")


def plot_galaxy_asteroids(a, energies=(1 / 12, 1 / 8, 1 / 6), threshold=0.02):
    """Poincaré-Schnitte für zwei Energien (Farbe: Lyapunov-Exponent der Bahn) und die Kirkwood-Lücken."""
    res = {}
    for E in energies:
        pts, lam = henon_heiles(E)
        res[E] = (pts, lam)
        print(f"Hénon-Heiles, Energie {E:.4f}: {np.mean(lam > threshold):.0%} der {len(lam)} Bahnen chaotisch "
              f"(λ > {threshold}); größtes λ = {lam.max():.3f}, kleinstes {lam.min():.4f}")
    AJ = 5.2029
    reson = {"3:1": 3, "5:2": 2.5, "7:3": 7 / 3, "2:1": 2}
    fig, axes = plt.subplots(1, len(energies) + 1, figsize=(20, 4.8),
                             gridspec_kw={"width_ratios": [1] * len(energies) + [1.6]})
    for ax, E in zip(axes, energies):
        pts, lam = res[E]
        chaotic = lam[pts[2].astype(int)] > threshold
        ax.plot(pts[0][~chaotic], pts[1][~chaotic], ",", color="tab:blue")
        ax.plot(pts[0][chaotic], pts[1][chaotic], ",", color="tab:red")
        ax.plot([], [], "s", color="tab:blue", label="regelmäßige Bahnen (λ ≈ 0)")
        ax.plot([], [], "s", color="tab:red", label="chaotische Bahnen (λ > 0)")
        ax.set_xlabel("y")
        ax.set_ylabel("p_y")
        ax.set_title(f"Energie 1/{1 / E:.0f}: {np.mean(lam > threshold):.0%} der Bahnen chaotisch", fontsize=10)
        if E == energies[0]:
            ax.legend(fontsize=8, loc="lower left")
        ax.set_aspect("equal")
    ax = axes[-1]
    ax.hist(a, bins=np.linspace(2.0, 3.5, 301), color="grey")
    for name, ratio in reson.items():
        ar = AJ * ratio ** (-2 / 3)
        ax.axvline(ar, color="tab:red", lw=1, ls="--")
        ax.text(ar + 0.01, ax.get_ylim()[1] * 0.92, name, color="tab:red", fontsize=9)
        n_in = np.sum(np.abs(a - ar) < 0.01)
        n_out = (np.sum(np.abs(a - ar - 0.05) < 0.01) + np.sum(np.abs(a - ar + 0.05) < 0.01)) / 2
        print(f"  Resonanz {name} mit Jupiter bei a = {ar:.3f} AU: {n_in} Asteroiden in ±0.01 AU, daneben im Mittel {n_out:.0f}")
    ax.set_xlabel("große Halbachse a [AU]")
    ax.set_ylabel("Zahl der Asteroiden je 0.005 AU")
    ax.set_title(f"{len(a):,} nummerierte Asteroiden (JPL): Lücken bei den Resonanzen mit Jupiter".replace(",", " "),
                 fontsize=10)
    fig.tight_layout()
    plt.show()
    return res
