"""Zufallsmatrizen: Wigner-Halbkreis, Abstoßung der Eigenwerte, Verhältnis-Statistik, Marchenko-Pastur und Quantenchaos gegen Lokalisierung.

Für stochastics.ipynb aus randommatrices.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, wigner_semicircle, level_repulsion, ratio_statistics, marchenko_pastur, quantum_chaos.
"""
import itertools
import numpy as np
import matplotlib.pyplot as plt


def load():
    """16. Daten (Zellen 4 von randommatrices.ipynb)."""
    global goe, gue, poisson, ratios, rng, semicircle, semicircle_cdf, unfolded_spacings, wigner_goe, wigner_gue
    # Alles hier (numpy, scipy, matplotlib) ist in Colab vorinstalliert

    rng = np.random.default_rng(1)

    def goe(N):
        A = rng.normal(size=(N, N))
        return (A + A.T) / np.sqrt(2)                     # Varianz 1 außerhalb, 2 auf der Diagonale

    def gue(N):
        A = (rng.normal(size=(N, N)) + 1j * rng.normal(size=(N, N))) / np.sqrt(2)
        return (A + A.conj().T) / np.sqrt(2)              # E|H_ij|² = 1 außerhalb der Diagonale

    semicircle = lambda x: np.sqrt(np.clip(4 - x ** 2, 0, None)) / (2 * np.pi)
    semicircle_cdf = lambda x: 0.5 + (x * np.sqrt(np.clip(4 - x ** 2, 0, None)) / (4 * np.pi)) + np.arcsin(np.clip(x / 2, -1, 1)) / np.pi

    def unfolded_spacings(ev, N, keep=0.5):
        """Entfalten mit dem Halbkreis, Abstände aus der mittleren Hälfte des Spektrums."""
        u = N * semicircle_cdf(np.sort(ev) / np.sqrt(N))
        s = np.diff(u)
        lo, hi = int(len(s) * (1 - keep) / 2), int(len(s) * (1 + keep) / 2)
        return s[lo:hi]

    def ratios(ev):
        s = np.diff(np.sort(ev))
        return np.minimum(s[:-1], s[1:]) / np.maximum(s[:-1], s[1:])

    wigner_goe = lambda s: np.pi / 2 * s * np.exp(-np.pi * s ** 2 / 4)
    wigner_gue = lambda s: 32 / np.pi ** 2 * s ** 2 * np.exp(-4 * s ** 2 / np.pi)
    poisson = lambda s: np.exp(-s)
    print("Funktionen bereit")


def wigner_semicircle():
    """17. Der Wigner-Halbkreis (Zellen 6 von randommatrices.ipynb)."""
    global B, N, ax, bins, c, ev, ev_goe, ev_gue, ev_pm, fig, m, name
    global xs
    N = 1500
    ev_goe = np.linalg.eigvalsh(goe(N))
    ev_gue = np.linalg.eigvalsh(gue(N))
    B = rng.choice([-1.0, 1.0], size=(N, N))
    ev_pm = np.linalg.eigvalsh(np.triu(B) + np.triu(B, 1).T)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    bins = np.linspace(-2.2, 2.2, 60)
    for ev, name, c in [(ev_goe, "GOE", "tab:blue"), (ev_gue, "GUE", "tab:red"), (ev_pm, "Einträge ±1", "tab:green")]:
        ax.hist(ev / np.sqrt(N), bins=bins, density=True, histtype="step", lw=1.5, color=c, label=name)
    xs = np.linspace(-2.2, 2.2, 400)
    ax.plot(xs, semicircle(xs), c="black", lw=2, ls="--", label="Halbkreis √(4 − x²)/2π")
    ax.set_xlabel("Eigenwert / √N")
    ax.set_ylabel("Dichte")
    ax.set_title(f"Eigenwertdichte, N = {N}")
    ax.legend()
    fig.tight_layout()
    plt.show()
    for ev, name in [(ev_goe, "GOE"), (ev_gue, "GUE"), (ev_pm, "±1")]:
        m = [np.mean((ev / np.sqrt(N)) ** k) for k in (2, 4, 6)]
        print(f"{name:4s}: Momente ⟨x²⟩, ⟨x⁴⟩, ⟨x⁶⟩ = {m[0]:.3f}, {m[1]:.3f}, {m[2]:.3f}   (Catalan-Zahlen: 1, 2, 5)")


def level_repulsion():
    """18. Abstoßung der Eigenwerte (Zellen 9 von randommatrices.ipynb)."""
    global N, REP, axes, beta, bins, c, cum, fig, name, s, s_goe, s_gue
    global s_poi, small, ss
    N, REP = 400, 40
    s_goe = np.concatenate([unfolded_spacings(np.linalg.eigvalsh(goe(N)), N) for _ in range(REP)])
    s_gue = np.concatenate([unfolded_spacings(np.linalg.eigvalsh(gue(N)), N) for _ in range(REP)])
    s_poi = np.diff(np.sort(rng.uniform(0, 20000, 20000)))

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    bins = np.linspace(0, 4, 41)
    ss = np.linspace(0, 4, 300)
    for s, name, c in [(s_poi, "unabhängige Zahlen", "tab:green"), (s_goe, "GOE", "tab:blue"), (s_gue, "GUE", "tab:red")]:
        axes[0].hist(s / s.mean(), bins=bins, density=True, alpha=0.35, color=c, label=name)
    axes[0].plot(ss, poisson(ss), c="tab:green", lw=2, label="Poisson e^(−s)")
    axes[0].plot(ss, wigner_goe(ss), c="tab:blue", lw=2, label="Wigner GOE (π/2) s e^(−πs²/4)")
    axes[0].plot(ss, wigner_gue(ss), c="tab:red", lw=2, label="Wigner GUE (32/π²) s² e^(−4s²/π)")
    axes[0].set_xlabel("Abstand s (mittlerer Abstand 1)")
    axes[0].set_ylabel("Dichte P(s)")
    axes[0].set_title("Abstandsverteilung")
    axes[0].legend(fontsize=8)
    small = np.logspace(-2, 0, 12)
    for s, name, c, beta in [(s_poi, "unabhängig", "tab:green", 0), (s_goe, "GOE", "tab:blue", 1), (s_gue, "GUE", "tab:red", 2)]:
        cum = [np.mean(s / s.mean() < x) for x in small]
        axes[1].loglog(small, cum, "o-", c=c, label=f"{name}: Anteil ~ s^{beta + 1}")
    axes[1].set_xlabel("Abstand s")
    axes[1].set_ylabel("Anteil der Abstände kleiner als s")
    axes[1].set_title("Kleine Abstände: P(s) ~ s^β")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()
    for s, name in [(s_poi, "unabhängig"), (s_goe, "GOE"), (s_gue, "GUE")]:
        print(f"{name:10s}: Anteil der Abstände < 0.1: {np.mean(s / s.mean() < 0.1):.4f}")


def ratio_statistics():
    """19. Die Verhältnis-Statistik (Zellen 12 von randommatrices.ipynb)."""
    global N_MAT, means, name, per_matrix, ref, samples
    N_MAT = 150
    samples = {"Poisson": [ratios(rng.uniform(0, 1, 200)) for _ in range(N_MAT)],
               "GOE": [ratios(np.linalg.eigvalsh(goe(400))[100:300]) for _ in range(N_MAT)],
               "GUE": [ratios(np.linalg.eigvalsh(gue(400))[100:300]) for _ in range(N_MAT)]}
    ref = {"Poisson": 2 * np.log(2) - 1, "GOE": 0.5307, "GUE": 0.5996}
    for name, per_matrix in samples.items():
        means = np.array([r.mean() for r in per_matrix])
        # Fehler aus der Streuung zwischen den Matrizen: benachbarte Verhältnisse derselben Matrix sind korreliert
        print(f"{name:8s}: ⟨r⟩ = {means.mean():.4f} ± {means.std() / np.sqrt(N_MAT):.4f}   (Theorie {ref[name]:.4f})")


def marchenko_pastur():
    """20. Rauschen in Kovarianzmatrizen: Marchenko–Pastur und ein verstecktes Signal (Zellen 15 von randommatrices.ipynb)."""
    global X, axes, ells, ev_noise, fig, gam, lam_m, lam_p, mp, n, p, theory
    global top_eigenvalue, tops, xs
    n, p = 2000, 500
    gam = p / n
    lam_m, lam_p = (1 - np.sqrt(gam)) ** 2, (1 + np.sqrt(gam)) ** 2
    mp = lambda x: np.sqrt(np.clip((lam_p - x) * (x - lam_m), 0, None)) / (2 * np.pi * gam * x)

    X = rng.normal(size=(n, p))
    ev_noise = np.linalg.eigvalsh(X.T @ X / n)

    def top_eigenvalue(ell):
        v = rng.normal(size=p); v /= np.linalg.norm(v)
        Y = rng.normal(size=(n, p)) + np.sqrt(ell) * rng.normal(size=(n, 1)) * v      # Kovarianz I + ℓ v vᵀ
        return np.linalg.eigvalsh(Y.T @ Y / n)[-1]

    ells = np.linspace(0.05, 2.0, 25)
    tops = np.array([np.mean([top_eigenvalue(l) for _ in range(3)]) for l in ells])
    theory = np.where(ells > np.sqrt(gam), (1 + ells) * (1 + gam / ells), lam_p)

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    axes[0].hist(ev_noise, bins=60, density=True, alpha=0.5, color="tab:blue", label=f"Eigenwerte, reines Rauschen (p = {p}, n = {n})")
    xs = np.linspace(lam_m, lam_p, 400)
    axes[0].plot(xs, mp(xs), c="black", lw=2, label="Marchenko-Pastur, γ = 0.25")
    axes[0].axvline(1, color="tab:red", ls=":", label="wahre Varianz: 1")
    axes[0].set_xlabel("Eigenwert der geschätzten Kovarianz")
    axes[0].set_ylabel("Dichte")
    axes[0].set_title("Rauschen allein streut die Eigenwerte von 0.25 bis 2.25")
    axes[0].legend(fontsize=8)
    axes[1].plot(ells, tops, "o", label="größter Eigenwert (Mittel aus 3 Ziehungen)")
    axes[1].plot(ells, theory, c="black", label="Theorie: Rand λ₊ oder (1 + ℓ)(1 + γ/ℓ)")
    axes[1].plot(ells, 1 + ells, c="grey", ls=":", label="wahre Varianz 1 + ℓ")
    axes[1].axvline(np.sqrt(gam), color="tab:red", ls="--", label="Schwelle ℓ = √γ")
    axes[1].set_xlabel("Stärke des Signals ℓ")
    axes[1].set_ylabel("größter Eigenwert")
    axes[1].set_title("BBP-Übergang")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()
    print(f"Rauschen: kleinster Eigenwert {ev_noise.min():.3f} (Theorie {lam_m:.3f}), größter {ev_noise.max():.3f} (Theorie {lam_p:.3f})")


def quantum_chaos():
    """21. Quantenchaos und Lokalisierung in einer Spinkette (Zellen 18 von randommatrices.ipynb)."""
    global D, L, W, Ws, ax, basis, fig, heisenberg_random_field, index, r, r_mean, rs_
    L = 12
    basis = [s for s in itertools.product([0, 1], repeat=L) if sum(s) == L // 2]     # 1 = Spin hoch
    index = {s: i for i, s in enumerate(basis)}
    D = len(basis)

    def heisenberg_random_field(W):
        h = rng.uniform(-W, W, L)
        H = np.zeros((D, D))
        for k, s in enumerate(basis):
            sz = np.array(s) - 0.5
            H[k, k] = np.sum(sz[:-1] * sz[1:]) + np.sum(h * sz)
            for i in range(L - 1):
                if s[i] != s[i + 1]:                                      # S⁺S⁻ + S⁻S⁺ tauscht antiparallele Nachbarn
                    t_ = list(s); t_[i], t_[i + 1] = t_[i + 1], t_[i]
                    H[index[tuple(t_)], k] = 0.5
        return H

    Ws = [0.25, 0.5, 1, 2, 3, 4, 6, 8, 12]
    r_mean = []
    for W in Ws:
        rs_ = [ratios(np.linalg.eigvalsh(heisenberg_random_field(W))[D // 4: 3 * D // 4]) for _ in range(15)]
        r_mean.append(np.mean(np.concatenate(rs_)))

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(Ws, r_mean, "o-", c="black", label=f"Heisenberg-Kette, L = {L}, Sektor Sᶻ = 0 ({D} Zustände)")
    ax.axhline(0.5307, color="tab:blue", ls="--", label="GOE 0.531")
    ax.axhline(2 * np.log(2) - 1, color="tab:green", ls="--", label="Poisson 0.386")
    ax.set_xscale("log")
    ax.set_xlabel("Stärke der Unordnung W")
    ax.set_ylabel("⟨r⟩ (mittlere Hälfte des Spektrums)")
    ax.set_title("Von Quantenchaos zu Lokalisierung")
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()
    for W, r in zip(Ws, r_mean):
        print(f"W = {W:5.2f}:  ⟨r⟩ = {r:.3f}")
