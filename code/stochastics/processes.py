"""Stochastische Prozesse: Bernoulli, Random Walk, Markov-Ketten, Martingale, Poisson, weißes Rauschen, Brownsche Bewegung und Brücke, geometrische und gebrochene Brownsche Bewegung, Ornstein-Uhlenbeck, Lévy, Gauß-Prozesse und Verzweigungsprozesse.

Für stochastics.ipynb aus stochasticprocesses.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, bernoulli, random_walk, markov_chain, martingales, poisson_process, white_noise, brownian_motion, brownian_bridge, geometric_bm, ou_process, fractional_bm, levy, gaussian_processes, branching.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats, signal


def load():
    """1. Daten (Zellen 4 von stochasticprocesses.ipynb)."""
    global autocorrelation, brownian, fbm, ornstein_uhlenbeck
    # Alles hier (numpy, scipy, matplotlib) ist in Colab vorinstalliert

    def brownian(n_paths, n_steps, T=1.0, rng=None):
        """Brownsche Bewegung auf [0, T]: Summen unabhängiger Zuwächse N(0, dt). Gibt Zeiten und Pfade (n_paths × (n_steps+1)) zurück."""
        dt = T / n_steps
        dW = rng.normal(0, np.sqrt(dt), size=(n_paths, n_steps))
        return np.linspace(0, T, n_steps + 1), np.concatenate([np.zeros((n_paths, 1)), np.cumsum(dW, axis=1)], axis=1)

    def ornstein_uhlenbeck(x0, theta, sigma, n_steps, dt, rng):
        """Ornstein-Uhlenbeck-Prozess dX = -θ X dt + σ dW, exakt diskretisiert (kein Fehler durch den Zeitschritt)."""
        x0 = np.atleast_1d(np.asarray(x0, dtype=float))
        a, s = np.exp(-theta * dt), sigma * np.sqrt((1 - np.exp(-2 * theta * dt)) / (2 * theta))
        X = np.empty((len(x0), n_steps + 1))
        X[:, 0] = x0
        for k in range(n_steps):
            X[:, k + 1] = a * X[:, k] + s * rng.normal(size=len(x0))
        return X

    def fbm(H, n_steps, T=1.0, n_paths=1, rng=None):
        """Gebrochene Brownsche Bewegung mit Hurst-Exponent H über die Cholesky-Zerlegung ihrer Kovarianz (Schritt 12)."""
        t = np.linspace(T / n_steps, T, n_steps)
        cov = 0.5 * (t[:, None] ** (2 * H) + t[None, :] ** (2 * H) - np.abs(t[:, None] - t[None, :]) ** (2 * H))
        L = np.linalg.cholesky(cov + 1e-12 * np.eye(n_steps))
        paths = rng.normal(size=(n_paths, n_steps)) @ L.T
        return np.r_[0, t], np.concatenate([np.zeros((n_paths, 1)), paths], axis=1)

    def autocorrelation(x, max_lag):
        """Empirische Autokorrelation einer Zeitreihe für die Verschiebungen 0 ... max_lag."""
        x = x - x.mean()
        return np.array([np.dot(x[:len(x) - k], x[k:]) / np.dot(x, x) for k in range(max_lag + 1)])

    print("Werkzeuge bereit: Brownsche Bewegung, Ornstein-Uhlenbeck, gebrochene Brownsche Bewegung, Autokorrelation")


def bernoulli():
    """2. Der Bernoulli-Prozess (Zellen 6 von stochasticprocesses.ipynb)."""
    global S, X, axes, fig, k, long, n, p, r, rng, w, waits
    rng = np.random.default_rng(1)
    p, n = 0.3, 300
    X = rng.random((2000, n)) < p                                   # 2000 Folgen von je 300 Münzwürfen mit P(1) = p
    S = np.cumsum(X, axis=1)                                         # Zahl der Erfolge bis zum Schritt k
    waits = np.concatenate([np.diff(np.r_[-1, np.flatnonzero(row)]) for row in X[:200]])   # Wartezeiten bis zum nächsten Erfolg

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    for r in range(5):
        axes[0].vlines(np.flatnonzero(X[r, :100]), r + 0.1, r + 0.9, lw=1.5)
    axes[0].set_yticks(np.arange(5) + 0.5, [f"Folge {r + 1}" for r in range(5)])
    axes[0].set_xlabel("Schritt k")
    axes[0].set_title(f"Fünf Folgen, Strich = Erfolg (p = {p})", fontsize=10)
    k = np.arange(1, n + 1)
    for r in range(20):
        axes[1].plot(k, S[r], lw=0.6, c="tab:blue", alpha=0.6)
    axes[1].plot(k, p * k, "k-", lw=1.5, label="Erwartung p·k")
    axes[1].fill_between(k, p * k - 2 * np.sqrt(k * p * (1 - p)), p * k + 2 * np.sqrt(k * p * (1 - p)), color="grey", alpha=0.3, label="± 2 Standardabweichungen")
    axes[1].set_xlabel("Schritt k")
    axes[1].set_ylabel("Zahl der Erfolge S_k")
    axes[1].set_title("Zählen der Erfolge: binomialverteilt", fontsize=10)
    axes[1].legend(fontsize=8)
    w = np.arange(1, 21)
    axes[2].hist(waits, bins=np.arange(0.5, 21.5), density=True, alpha=0.6, label="gemessen")
    axes[2].plot(w, p * (1 - p) ** (w - 1), "ko-", ms=3, label="geometrisch: p(1 − p)^(w−1)")
    axes[2].set_xlabel("Wartezeit w bis zum nächsten Erfolg")
    axes[2].set_ylabel("Wahrscheinlichkeit")
    axes[2].set_title("Wartezeiten: geometrisch verteilt, ohne Gedächtnis", fontsize=10)
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"S_{n}: Mittel {S[:, -1].mean():.2f} (Theorie n·p = {n * p:.0f}), Varianz {S[:, -1].var():.2f} (Theorie n·p·(1−p) = {n * p * (1 - p):.0f})")
    print(f"Wartezeit: Mittel {waits.mean():.3f} (Theorie 1/p = {1 / p:.3f}), P(W > 5) = {np.mean(waits > 5):.3f} (Theorie (1−p)^5 = {(1 - p) ** 5:.3f})")
    long = waits[waits > 3]
    print(f"Kein Gedächtnis: P(W > 3 + 2 | W > 3) = {np.mean(long > 5):.3f}, P(W > 2) = {np.mean(waits > 2):.3f} (Theorie beide (1−p)^2 = {(1 - p) ** 2:.3f})")


def random_walk():
    """3. Der Random Walk (Zellen 9 von stochasticprocesses.ipynb)."""
    global axes, edge, fig, frac_positive, k, n, paths, r, returns, rng, steps, u
    global walk, x
    rng = np.random.default_rng(2)
    n, paths = 1000, 5000
    steps = rng.choice([-1, 1], size=(paths, n))
    walk = np.concatenate([np.zeros((paths, 1), dtype=int), np.cumsum(steps, axis=1)], axis=1)
    frac_positive = np.mean(walk[:, 1:] > 0, axis=1)                 # Anteil der Zeit, den der Pfad über null verbringt
    returns = np.sum(walk[:, 1:] == 0, axis=1)                       # Zahl der Rückkehren zum Start

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    k = np.arange(n + 1)
    for r in range(6):
        axes[0].plot(k, walk[r], lw=0.8)
    axes[0].plot(k, np.sqrt(k), "k--", lw=1, label="± √k")
    axes[0].plot(k, -np.sqrt(k), "k--", lw=1)
    axes[0].set_xlabel("Schritt k")
    axes[0].set_ylabel("Position")
    axes[0].set_title("Sechs Random Walks mit Schritten ±1", fontsize=10)
    axes[0].legend(fontsize=8)
    x = np.linspace(-120, 120, 300)
    axes[1].hist(walk[:, -1], bins=np.arange(-121, 122, 6), density=True, alpha=0.6, label=f"Endpunkt nach {n} Schritten")
    axes[1].plot(x, stats.norm.pdf(x, 0, np.sqrt(n)), "k-", label=f"Normalverteilung, σ = √{n}")
    axes[1].set_xlabel("Position nach n Schritten")
    axes[1].set_ylabel("Dichte")
    axes[1].set_title("Zentraler Grenzwertsatz: Endpunkte werden normalverteilt", fontsize=10)
    axes[1].legend(fontsize=8)
    u = np.linspace(0.005, 0.995, 200)
    axes[2].hist(frac_positive, bins=40, density=True, alpha=0.6, label="gemessen")
    axes[2].plot(u, 1 / (np.pi * np.sqrt(u * (1 - u))), "k-", label="Arkussinus-Dichte 1/(π√(u(1−u)))")
    axes[2].set_xlabel("Anteil der Zeit über null")
    axes[2].set_ylabel("Dichte")
    axes[2].set_title("Arkussinus-Gesetz: meist überwiegt eine Seite", fontsize=10)
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"Endpunkt nach {n} Schritten: Mittel {walk[:, -1].mean():.2f}, Standardabweichung {walk[:, -1].std():.1f} (Theorie √n = {np.sqrt(n):.1f})")
    edge = np.mean((frac_positive < 0.1) | (frac_positive > 0.9))
    print(f"Pfade, die mehr als 90 % der Zeit auf einer Seite sind: {edge:.1%} (Arkussinus: {4 / np.pi * np.arcsin(np.sqrt(0.1)):.1%}); "
          f"zwischen 45 % und 55 %: {np.mean(np.abs(frac_positive - 0.5) < 0.05):.1%} (Arkussinus: {2 / np.pi * (np.arcsin(np.sqrt(0.55)) - np.arcsin(np.sqrt(0.45))):.1%})")
    print(f"Rückkehren zum Start in {n} Schritten: im Mittel {returns.mean():.1f} (Theorie ≈ √(2n/π) = {np.sqrt(2 * n / np.pi):.1f})")


def markov_chain():
    """4. Die Markov-Kette (Zellen 12 von stochasticprocesses.ipynb)."""
    global P, T, _, axes, c, cum, evals, evecs, fig, freq, lam2, mu
    global names, ns, order, path, pi, rain, rng, run_lengths, start, t, tv, u
    global xb
    rng = np.random.default_rng(3)
    names = ["Sonne", "Wolken", "Regen"]
    P = np.array([[0.7, 0.2, 0.1],
                  [0.3, 0.4, 0.3],
                  [0.2, 0.4, 0.4]])                                  # P[i, j] = Wahrscheinlichkeit für j morgen, wenn heute i
    evals, evecs = np.linalg.eig(P.T)
    order = np.argsort(-np.abs(evals))
    pi = np.real(evecs[:, order[0]]); pi /= pi.sum()                 # stationäre Verteilung: linker Eigenvektor zum Eigenwert 1
    lam2 = np.abs(evals[order[1]])

    T = 100_000
    path = np.empty(T, dtype=int); path[0] = 2
    cum = np.cumsum(P, axis=1)
    u = rng.random(T)
    for t in range(1, T):
        path[t] = np.searchsorted(cum[path[t - 1]], u[t])
    freq = np.bincount(path, minlength=3) / T

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    axes[0].step(np.arange(60), path[:60], where="mid", c="tab:blue")
    axes[0].set_yticks([0, 1, 2], names)
    axes[0].set_xlabel("Tag")
    axes[0].set_title("Ein Pfad der Wetterkette (60 Tage)", fontsize=10)
    ns = np.arange(16)
    for start, c in zip(range(3), ["tab:orange", "tab:grey", "tab:blue"]):
        mu = np.eye(3)[start]
        tv = []
        for _ in ns:
            tv.append(0.5 * np.abs(mu - pi).sum())
            mu = mu @ P
        axes[1].semilogy(ns, tv, "o-", ms=3, c=c, label=f"Start: {names[start]}")
    axes[1].semilogy(ns, 0.5 * lam2 ** ns, "k--", lw=1, label=f"∝ |λ₂|ⁿ, |λ₂| = {lam2:.3f}")
    axes[1].set_xlabel("Tage n")
    axes[1].set_ylabel("Abstand zur stationären Verteilung")
    axes[1].set_title("Vergessen des Anfangs: Konvergenz gegen π", fontsize=10)
    axes[1].legend(fontsize=8)
    xb = np.arange(3)
    axes[2].bar(xb - 0.2, pi, 0.4, label="stationäre Verteilung π (Eigenvektor)")
    axes[2].bar(xb + 0.2, freq, 0.4, label=f"Häufigkeit in {T:,} Tagen")
    axes[2].set_xticks(xb, names)
    axes[2].set_ylabel("Anteil der Tage")
    axes[2].set_title("Ergodizität: Zeitmittel = stationäre Verteilung", fontsize=10)
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print("Übergangsmatrix P (Zeilen: heute, Spalten: morgen):")
    print(P)
    print(f"Eigenwerte von P: {np.round(evals[order], 4)}")
    print(f"Stationäre Verteilung π = {np.round(pi, 4)}  (Sonne, Wolken, Regen)")
    print(f"Häufigkeiten im Pfad     = {np.round(freq, 4)}")
    rain = np.r_[0, (path == 2).astype(int), 0]
    run_lengths = np.flatnonzero(np.diff(rain) == -1) - np.flatnonzero(np.diff(rain) == 1)
    print(f"Mittlere Dauer einer Regenphase: gemessen {run_lengths.mean():.2f} Tage, Theorie 1/(1 − P_RR) = {1 / (1 - P[2, 2]):.2f}")


def martingales():
    """5. Martingale: faire Spiele und Stoppzeiten (Zellen 15 von stochasticprocesses.ipynb)."""
    global _, a, axes, b, cases, counts, doubling, dur, fig, gain, measured, pos
    global r, results, rng, rng_demo, ruin, theory, vals, w, x, y
    rng = np.random.default_rng(4)

    def ruin(a, b, n_games, rng, max_steps=20_000):
        """Symmetrischer Random Walk ab 0, gestoppt bei +a oder -b. Gibt Endpunkte und Spieldauern zurück."""
        pos = np.zeros(n_games, dtype=int); dur = np.zeros(n_games, dtype=int); alive = np.ones(n_games, dtype=bool)
        for t in range(1, max_steps + 1):
            pos[alive] += rng.choice([-1, 1], size=alive.sum())
            dur[alive] = t
            alive &= (pos < a) & (pos > -b)
            if not alive.any():
                break
        return pos, dur

    cases = [(5, 5), (5, 10), (10, 5), (3, 12), (12, 3), (8, 16)]
    results = [(a, b) + tuple(ruin(a, b, 4000, rng)) for a, b in cases]

    def doubling(n_players, bankroll, max_rounds, rng):
        """Verdopplungsstrategie: Einsatz 1, nach jedem Verlust verdoppeln, nach einem Gewinn aufhören (fairer Münzwurf)."""
        final = np.empty(n_players)
        for i in range(n_players):
            money, stake = bankroll, 1
            for _ in range(max_rounds):
                if stake > money:                                    # Einsatz nicht mehr bezahlbar: Spieler ist pleite
                    break
                if rng.random() < 0.5:
                    money += stake
                    break
                money -= stake
                stake *= 2
            final[i] = money - bankroll
        return final

    gain = doubling(100_000, bankroll=1023, max_rounds=50, rng=rng)

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    rng_demo = np.random.default_rng(40)
    for r in range(8):
        w = [0]
        while -10 < w[-1] < 5:
            w.append(w[-1] + rng_demo.choice([-1, 1]))
        axes[0].plot(w, lw=1, c="tab:green" if w[-1] == 5 else "tab:red")
    axes[0].axhline(5, color="tab:green", ls="--", lw=1, label="Ziel +a = +5")
    axes[0].axhline(-10, color="tab:red", ls="--", lw=1, label="Ruin −b = −10")
    axes[0].set_xlabel("Runde")
    axes[0].set_ylabel("Gewinn")
    axes[0].set_title("Gestoppter Random Walk (Ruin des Spielers)", fontsize=10)
    axes[0].legend(fontsize=8)
    theory = [b / (a + b) for a, b, *_ in results]
    measured = [np.mean(pos == a) for a, b, pos, dur in results]
    axes[1].plot([0, 1], [0, 1], "k-", lw=1, label="Gerade: gemessen = b/(a+b)")
    axes[1].plot(theory, measured, "o", ms=7, label="sechs Paare (a, b)")
    for (a, b, *_), x, y in zip(results, theory, measured):
        axes[1].annotate(f"({a},{b})", (x, y), textcoords="offset points", xytext=(5, -10), fontsize=7)
    axes[1].set_xlabel("Vorhersage aus dem Stoppsatz: b/(a + b)")
    axes[1].set_ylabel("gemessene Wahrscheinlichkeit, +a zu erreichen")
    axes[1].set_title("Optionaler Stoppsatz: E[Gewinn beim Stopp] = 0", fontsize=10)
    axes[1].legend(fontsize=8)
    vals, counts = np.unique(gain, return_counts=True)
    axes[2].bar(range(len(vals)), counts / len(gain), color=["tab:red" if v < 0 else "tab:green" for v in vals])
    axes[2].set_xticks(range(len(vals)), [f"{v:+.0f}" for v in vals])
    axes[2].set_yscale("log")
    axes[2].set_xlabel("Gewinn am Ende")
    axes[2].set_ylabel("Anteil der Spieler")
    axes[2].set_title("Verdopplungsstrategie mit Kapital 1023", fontsize=10)
    plt.tight_layout()
    plt.show()

    for a, b, pos, dur in results:
        print(f"a = {a:2d}, b = {b:2d}:  P(+a) = {np.mean(pos == a):.3f} (b/(a+b) = {b / (a + b):.3f}),  "
              f"mittlerer Gewinn {pos.mean():+.3f} (0),  mittlere Dauer {dur.mean():6.1f} (a·b = {a * b})")
    print(f"Verdopplungsstrategie: Anteil mit Gewinn +1: {np.mean(gain == 1):.4f} (Theorie 1 − 2^−10 = {1 - 2 ** -10:.4f}), "
          f"Anteil pleite (−1023): {np.mean(gain == -1023):.4f}, mittlerer Gewinn {gain.mean():+.3f} (Theorie 0)")


def poisson_process():
    """6. Der Poisson-Prozess (Zellen 18 von stochasticprocesses.ipynb)."""
    global T, axes, cond, counts, ev, fig, gaps, kk, lam, r, rng, times
    global x
    rng = np.random.default_rng(5)
    lam, T = 2.0, 10.0
    gaps = rng.exponential(1 / lam, size=(20_000, 60))                # Wartezeiten zwischen den Ereignissen
    times = np.cumsum(gaps, axis=1)
    counts = (times <= T).sum(axis=1)                                # Zahl der Ereignisse bis T

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    for r in range(6):
        ev = times[r][times[r] <= T]
        axes[0].step(np.r_[0, ev, T], np.r_[0, np.arange(1, len(ev) + 1), len(ev)], where="post", lw=1)
    axes[0].plot([0, T], [0, lam * T], "k--", lw=1, label="Erwartung λt")
    axes[0].set_xlabel("Zeit t")
    axes[0].set_ylabel("Zahl der Ereignisse N(t)")
    axes[0].set_title(f"Sechs Zählpfade, Rate λ = {lam}", fontsize=10)
    axes[0].legend(fontsize=8)
    x = np.linspace(0, 4, 200)
    axes[1].hist(gaps[:, 0], bins=60, range=(0, 4), density=True, alpha=0.6, label="gemessen")
    axes[1].plot(x, lam * np.exp(-lam * x), "k-", label="Exponentialverteilung λe^(−λt)")
    axes[1].set_xlabel("Zeit zwischen zwei Ereignissen")
    axes[1].set_ylabel("Dichte")
    axes[1].set_title("Wartezeiten: exponentiell, ohne Gedächtnis", fontsize=10)
    axes[1].legend(fontsize=8)
    kk = np.arange(0, 41)
    axes[2].bar(kk, np.bincount(counts, minlength=41)[:41] / len(counts), alpha=0.6, label="gemessen")
    axes[2].plot(kk, stats.poisson.pmf(kk, lam * T), "ko", ms=3, label=f"Poisson-Verteilung, Mittel λT = {lam * T:.0f}")
    axes[2].set_xlabel(f"Zahl der Ereignisse bis T = {T:.0f}")
    axes[2].set_ylabel("Wahrscheinlichkeit")
    axes[2].set_title("Zählungen: Poisson-verteilt, Varianz = Mittel", fontsize=10)
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"N(T): Mittel {counts.mean():.3f}, Varianz {counts.var():.3f} (Theorie beide λT = {lam * T:.0f}); Fano-Faktor {counts.var() / counts.mean():.3f}")
    print(f"Wartezeit: Mittel {gaps.mean():.4f} (Theorie 1/λ = {1 / lam})")
    cond = gaps[:, 0][gaps[:, 0] > 0.5] - 0.5
    print(f"Kein Gedächtnis: mittlere Restwartezeit nach 0.5 Wartezeit {cond.mean():.4f} (wieder 1/λ = {1 / lam})")


def white_noise():
    """7. Weißes Rauschen (Zellen 21 von stochasticprocesses.ipynb)."""
    global ac, axes, colored, f_c, f_w, fig, fs, lags, n, psd_c, psd_w, rng
    global white
    rng = np.random.default_rng(6)
    n, fs = 2 ** 16, 1.0
    white = rng.normal(0, 1, n)
    colored = ornstein_uhlenbeck(0.0, 0.05, np.sqrt(2 * 0.05), n - 1, 1.0, rng)[0]   # zum Vergleich: korreliertes Rauschen, Varianz 1
    f_w, psd_w = signal.welch(white, fs=fs, nperseg=4096)
    f_c, psd_c = signal.welch(colored, fs=fs, nperseg=4096)

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    axes[0].plot(white[:300], lw=0.8, label="weißes Rauschen")
    axes[0].plot(colored[:300], lw=1.2, label="farbiges Rauschen (Ornstein-Uhlenbeck)")
    axes[0].set_xlabel("Zeitschritt")
    axes[0].set_ylabel("Wert")
    axes[0].set_title("Zwei Rauschsignale mit gleicher Varianz 1", fontsize=10)
    axes[0].legend(fontsize=8, loc="lower right")
    lags = np.arange(41)
    axes[1].plot(lags, autocorrelation(white, 40), "o-", ms=3, label="weiß")
    axes[1].plot(lags, autocorrelation(colored, 40), "s-", ms=3, label="farbig")
    axes[1].plot(lags, np.exp(-0.05 * lags), "k--", lw=1, label="e^(−0.05 τ)")
    axes[1].set_xlabel("Verschiebung τ")
    axes[1].set_ylabel("Autokorrelation")
    axes[1].set_title("Autokorrelation: weiß nur bei τ = 0", fontsize=10)
    axes[1].legend(fontsize=8)
    axes[2].loglog(f_w[1:], psd_w[1:], label="weiß")
    axes[2].loglog(f_c[1:], psd_c[1:], label="farbig")
    axes[2].axhline(2.0, color="k", ls="--", lw=1, label="flach: 2σ² / f_s")
    axes[2].set_xlabel("Frequenz f [1/Zeitschritt]")
    axes[2].set_ylabel("Leistungsdichte")
    axes[2].set_title("Spektrum: weiß ist flach (alle Frequenzen gleich stark)", fontsize=10)
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    ac = autocorrelation(white, 5)
    print(f"Weiß: Autokorrelation bei τ = 1 ... 5: {np.round(ac[1:], 4)}  (Theorie 0, Schwankung ±1/√n = ±{1 / np.sqrt(n):.4f})")
    print(f"Weiß: Leistungsdichte im Mittel {psd_w.mean():.3f} (Theorie 2σ²/f_s = 2), unter f = 0.01: {psd_w[(f_w > 0) & (f_w < 0.01)].mean():.3f}, über f = 0.25: {psd_w[f_w > 0.25].mean():.3f}")
    print(f"Farbig: Leistungsdichte bei f = 0.002 und f = 0.4: {np.interp(0.002, f_c, psd_c):.1f} und {np.interp(0.4, f_c, psd_c):.4f}")


def brownian_motion():
    """8. Die Brownsche Bewegung (Zellen 24 von stochasticprocesses.ipynb)."""
    global L, W, Wz, axes, c, cov, fig, levels, mask, qv, r, rng
    global t, tv, tz, w
    rng = np.random.default_rng(7)
    t, W = brownian(2000, 1024, T=1.0, rng=rng)                      # Ensemble für Varianz und Kovarianz
    tz, Wz = brownian(1, 2 ** 16, T=1.0, rng=rng)                    # ein fein aufgelöster Pfad

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    for r in range(6):
        axes[0].plot(t, W[r], lw=0.7)
    axes[0].plot(t, np.sqrt(t), "k--", lw=1, label="± √t")
    axes[0].plot(t, -np.sqrt(t), "k--", lw=1)
    axes[0].set_xlabel("Zeit t")
    axes[0].set_ylabel("W(t)")
    axes[0].set_title("Sechs Pfade der Brownschen Bewegung", fontsize=10)
    axes[0].legend(fontsize=8)
    levels = np.arange(4, 17)
    qv, tv = [], []
    for L in levels:
        w = Wz[0, :: 2 ** (16 - L)]                                   # derselbe Pfad, mit 2^L Schritten abgetastet
        qv.append(np.sum(np.diff(w) ** 2)); tv.append(np.sum(np.abs(np.diff(w))))
    axes[1].loglog(2 ** levels, qv, "o-", label="quadratische Variation Σ(ΔW)²")
    axes[1].loglog(2 ** levels, tv, "s-", label="Länge Σ|ΔW|")
    axes[1].loglog(2 ** levels, np.sqrt(2 * 2 ** levels / np.pi), "k--", lw=1, label="√(2n/π) (Länge wächst ohne Grenze)")
    axes[1].axhline(1, color="grey", ls=":", lw=1)
    axes[1].set_xlabel("Zahl der Teilintervalle n")
    axes[1].set_title("Ein Pfad: quadratische Variation → t = 1, Länge → ∞", fontsize=10)
    axes[1].legend(fontsize=8)
    c = 0.01
    mask = tz <= c
    axes[2].plot(tz, Wz[0], lw=0.6, label="Pfad auf [0, 1]")
    axes[2].plot(tz[mask] / c, Wz[0, mask] / np.sqrt(c), lw=0.6, label="Ausschnitt [0, 0.01], gestreckt: t/c, W/√c")
    axes[2].set_xlabel("Zeit (gestreckt)")
    axes[2].set_title("Selbstähnlichkeit: gestreckt sieht der Ausschnitt gleich aus", fontsize=10)
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"Varianz von W(t) bei t = 0.25, 0.5, 1: " + ", ".join(f"{W[:, np.searchsorted(t, s)].var():.3f}" for s in (0.25, 0.5, 1.0)) + "  (Theorie = t)")
    cov = np.mean(W[:, np.searchsorted(t, 0.3)] * W[:, np.searchsorted(t, 0.8)])
    print(f"Kovarianz E[W(0.3) W(0.8)] = {cov:.3f}  (Theorie min(s, t) = 0.3)")
    print(f"Quadratische Variation bei n = 16, 256, 4096, 65536: {qv[0]:.3f}, {qv[4]:.3f}, {qv[8]:.3f}, {qv[12]:.3f}  (Theorie → 1)")
    print(f"Länge des Pfads bei n = 16, 256, 4096, 65536: {tv[0]:.1f}, {tv[4]:.1f}, {tv[8]:.1f}, {tv[12]:.1f}  (wächst wie √(2n/π))")


def brownian_bridge():
    """9. Die Brownsche Brücke (Zellen 27 von stochasticprocesses.ipynb)."""
    global B, D, KS, U, W, axes, fig, i, n_samples, r, reps, rng
    global t, x
    rng = np.random.default_rng(8)
    t, W = brownian(4000, 1000, T=1.0, rng=rng)
    B = W - t * W[:, -1:]                                            # Brownsche Brücke: B(t) = W(t) − t·W(1)

    n_samples, reps = 200, 5000
    U = np.sort(rng.random((reps, n_samples)), axis=1)               # gleichverteilte Stichproben, sortiert
    i = np.arange(1, n_samples + 1)
    D = np.maximum(i / n_samples - U, U - (i - 1) / n_samples).max(axis=1)   # Kolmogorov-Smirnov-Abstand sup|F_n − F|
    KS = np.sqrt(n_samples) * D

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    for r in range(6):
        axes[0].plot(t, B[r], lw=0.7)
    axes[0].plot(t, np.sqrt(t * (1 - t)), "k--", lw=1, label="± √(t(1−t))")
    axes[0].plot(t, -np.sqrt(t * (1 - t)), "k--", lw=1)
    axes[0].set_xlabel("Zeit t")
    axes[0].set_ylabel("B(t)")
    axes[0].set_title("Sechs Brownsche Brücken: Start und Ende bei 0", fontsize=10)
    axes[0].legend(fontsize=8)
    axes[1].plot(t, B.var(axis=0), label="gemessene Varianz")
    axes[1].plot(t, t * (1 - t), "k--", label="t(1 − t)")
    axes[1].set_xlabel("Zeit t")
    axes[1].set_ylabel("Varianz")
    axes[1].set_title("Unsicherheit am größten in der Mitte", fontsize=10)
    axes[1].legend(fontsize=8)
    x = np.linspace(0.2, 2.5, 300)
    axes[2].hist(KS, bins=50, density=True, alpha=0.6, label=f"√n·sup|F_n − F|, n = {n_samples}")
    axes[2].plot(x, stats.kstwobign.pdf(x), "k-", label="Kolmogorov-Verteilung (Maximum |B|)")
    axes[2].axvline(stats.kstwobign.ppf(0.95), color="tab:red", ls="--", label=f"95 %-Grenze {stats.kstwobign.ppf(0.95):.3f}")
    axes[2].set_xlabel("Kolmogorov-Smirnov-Statistik")
    axes[2].set_ylabel("Dichte")
    axes[2].set_title("Kolmogorov-Smirnov-Test: Maximum einer Brücke", fontsize=10)
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"Varianz bei t = 0.5: {B[:, 500].var():.4f} (Theorie 0.25); bei t = 0.1: {B[:, 100].var():.4f} (Theorie 0.09)")
    print(f"Maximum |B| der Brücken im Mittel {np.abs(B).max(axis=1).mean():.3f} (Kolmogorov-Verteilung: {stats.kstwobign.mean():.3f}; "
          f"auf dem Gitter etwas kleiner)")
    print(f"KS-Statistik: Mittel {KS.mean():.3f}, Anteil über 1.358: {np.mean(KS > stats.kstwobign.ppf(0.95)):.3f} (soll 0.05)")


def geometric_bm():
    """10. Die geometrische Brownsche Bewegung (Zellen 30 von stochasticprocesses.ipynb)."""
    global S, S0, W, axes, below, end, fig, logS, mean_t, median_t, mu, r
    global rng, sigma, t, xs, years
    rng = np.random.default_rng(9)
    S0, mu, sigma, years = 100.0, 0.07, 0.30, 30
    t, W = brownian(10_000, years * 12, T=years, rng=rng)            # monatliche Schritte
    S = S0 * np.exp((mu - 0.5 * sigma ** 2) * t + sigma * W)         # Lösung von dS = μ S dt + σ S dW (Itô)
    mean_t, median_t = S0 * np.exp(mu * t), S0 * np.exp((mu - 0.5 * sigma ** 2) * t)

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    for r in range(30):
        axes[0].plot(t, S[r], lw=0.5, alpha=0.7)
    axes[0].plot(t, mean_t, "k-", lw=2, label="Mittelwert S₀e^(μt)")
    axes[0].plot(t, median_t, "k--", lw=2, label="Median S₀e^((μ−σ²/2)t)")
    axes[0].set_yscale("log")
    axes[0].set_xlabel("Zeit [Jahre]")
    axes[0].set_ylabel("Kurs S(t)")
    axes[0].set_title(f"30 Kurspfade, μ = {mu}, σ = {sigma}", fontsize=10)
    axes[0].legend(fontsize=8)
    end = S[:, -1]
    logS = np.log10(end)                                             # log10 des Endkurses ist normalverteilt
    axes[1].hist(logS, bins=60, density=True, alpha=0.6, label=f"S nach {years} Jahren")
    xs = np.linspace(logS.min(), logS.max(), 300)
    axes[1].plot(xs, stats.norm.pdf(xs, np.log10(median_t[-1]), sigma * np.sqrt(years) / np.log(10)), "k-", label="Log-Normalverteilung")
    axes[1].axvline(np.log10(mean_t[-1]), color="tab:red", ls="-", label=f"Mittelwert {mean_t[-1]:.0f}")
    axes[1].axvline(np.log10(median_t[-1]), color="tab:red", ls="--", label=f"Median {median_t[-1]:.0f}")
    axes[1].set_xticks(range(0, 6), ["1", "10", "100", "1000", "10⁴", "10⁵"])
    axes[1].set_xlabel("Endkurs (logarithmische Achse)")
    axes[1].set_ylabel("Dichte pro Zehnerpotenz")
    axes[1].set_title("Log-normal: wenige große Gewinner ziehen den Mittelwert hoch", fontsize=10)
    axes[1].legend(fontsize=7)
    below = (S < mean_t).mean(axis=0)
    axes[2].plot(t, below, label="Anteil der Pfade unter dem Mittelwert")
    axes[2].plot(t, stats.norm.cdf(0.5 * sigma * np.sqrt(t)), "k--", label="Theorie Φ(σ√t / 2)")
    axes[2].set_xlabel("Zeit [Jahre]")
    axes[2].set_ylabel("Anteil")
    axes[2].set_title("Die meisten Pfade bleiben unter dem Mittelwert", fontsize=10)
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"Nach {years} Jahren: Mittel {end.mean():.0f} (Theorie {mean_t[-1]:.0f}), Median {np.median(end):.0f} (Theorie {median_t[-1]:.0f})")
    print(f"Anteil der Pfade unter dem Mittelwert: {np.mean(end < mean_t[-1]):.3f} (Theorie {stats.norm.cdf(0.5 * sigma * np.sqrt(years)):.3f}); "
          f"unter dem Startwert {S0:.0f}: {np.mean(end < S0):.3f} (Theorie {stats.norm.cdf(-(mu - 0.5 * sigma ** 2) * np.sqrt(years) / sigma):.3f})")
    print(f"Typische Wachstumsrate (Median): μ − σ²/2 = {mu - 0.5 * sigma ** 2:.3f} pro Jahr statt μ = {mu}")


def ou_process():
    """11. Der Ornstein-Uhlenbeck-Prozess (Zellen 33 von stochasticprocesses.ipynb)."""
    global X, ac, axes, check, dt, f, fig, lag_steps, long, omega, psd, r
    global rng, sd, sigma, starts, theta, tt, x0
    rng = np.random.default_rng(10)
    theta, sigma, dt = 1.0, 1.0, 0.01
    starts = np.repeat([-3.0, 0.0, 3.0], 3)
    X = ornstein_uhlenbeck(starts, theta, sigma, 800, dt, rng)
    long = ornstein_uhlenbeck(0.0, theta, sigma, 2 ** 19, dt, rng)[0]
    lag_steps = np.arange(0, 401, 10)
    ac = autocorrelation(long, 400)[lag_steps]
    f, psd = signal.welch(long, fs=1 / dt, nperseg=2 ** 14)
    omega = 2 * np.pi * f

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    tt = np.arange(801) * dt
    for r, x0 in enumerate(starts):
        axes[0].plot(tt, X[r], lw=0.7, c={-3.0: "tab:blue", 0.0: "tab:grey", 3.0: "tab:red"}[x0])
    axes[0].plot(tt, 3 * np.exp(-theta * tt), "k--", lw=1, label="Mittelwert 3e^(−θt)")
    axes[0].plot(tt, -3 * np.exp(-theta * tt), "k--", lw=1)
    sd = sigma / np.sqrt(2 * theta)
    axes[0].axhspan(-2 * sd, 2 * sd, color="grey", alpha=0.15, label="± 2 stationäre Standardabweichungen")
    axes[0].set_xlabel("Zeit t")
    axes[0].set_ylabel("X(t)")
    axes[0].set_title(f"Rückkehr zum Mittelwert, θ = {theta}, σ = {sigma}", fontsize=10)
    axes[0].legend(fontsize=8)
    axes[1].plot(lag_steps * dt, ac, "o", ms=3, label="gemessen")
    axes[1].plot(lag_steps * dt, np.exp(-theta * lag_steps * dt), "k-", label="e^(−θτ)")
    axes[1].set_xlabel("Verschiebung τ")
    axes[1].set_ylabel("Autokorrelation")
    axes[1].set_title("Gedächtnis zerfällt exponentiell", fontsize=10)
    axes[1].legend(fontsize=8)
    axes[2].loglog(f[1:], psd[1:], label="gemessen")
    axes[2].loglog(f[1:], 2 * sigma ** 2 / (theta ** 2 + omega[1:] ** 2), "k--", label="Lorentz: 2σ²/(θ² + ω²)")
    axes[2].set_xlabel("Frequenz f")
    axes[2].set_ylabel("Leistungsdichte")
    axes[2].set_title("Spektrum: flach unter θ/2π, darüber ∝ 1/f²", fontsize=10)
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"Stationäre Varianz: gemessen {long.var():.4f}, Theorie σ²/(2θ) = {sigma ** 2 / (2 * theta):.4f}")
    print(f"Autokorrelation bei τ = 1: {autocorrelation(long, 100)[100]:.3f} (Theorie e^−1 = {np.exp(-1):.3f}); Korrelationszeit 1/θ = {1 / theta}")
    check = ornstein_uhlenbeck(np.full(4000, 3.0), theta, sigma, 100, dt, rng)[:, -1]   # 4000 Pfade ab x₀ = 3 bis t = 1
    print(f"4000 Pfade ab x₀ = 3, bei t = 1: Mittel {check.mean():.3f} (Theorie 3e^−θt = {3 * np.exp(-1):.3f}), Varianz {check.var():.3f} (Theorie σ²(1 − e^−2θt)/(2θ) = {(1 - np.exp(-2)) / 2:.3f})")


def fractional_bm():
    """12. Die gebrochene Brownsche Bewegung (Zellen 36 von stochasticprocesses.ipynb)."""
    global Bh, H, Hs, axes, c, estimates, fig, hh, inc, lags, rho1, rng
    global slope, t, var
    rng = np.random.default_rng(11)
    Hs = [0.25, 0.5, 0.75]
    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    estimates, rho1 = {}, {}
    lags = np.array([1, 2, 4, 8, 16, 32, 64])
    for H, c in zip(Hs, ["tab:red", "tab:grey", "tab:blue"]):
        t, Bh = fbm(H, 1024, T=1.0, n_paths=200, rng=rng)
        axes[0].plot(t, Bh[0], lw=0.8, c=c, label=f"H = {H}")
        var = [np.mean((Bh[:, L:] - Bh[:, :-L]) ** 2) for L in lags]
        slope = np.polyfit(np.log(lags), np.log(var), 1)[0]
        estimates[H] = slope / 2
        axes[1].loglog(lags / 1024, var, "o-", c=c, ms=4, label=f"H = {H}: Steigung {slope:.2f} (2H = {2 * H})")
        inc = np.diff(Bh, axis=1)
        rho1[H] = np.mean(inc[:, :-1] * inc[:, 1:]) / np.mean(inc ** 2)
    axes[0].set_xlabel("Zeit t")
    axes[0].set_ylabel("B_H(t)")
    axes[0].set_title("Rau (H < ½), Brownsch (H = ½), glatt und anhaltend (H > ½)", fontsize=10)
    axes[0].legend(fontsize=8)
    axes[1].set_xlabel("Zeitabstand Δt")
    axes[1].set_ylabel("mittleres Quadrat des Zuwachses")
    axes[1].set_title("Variogramm: Zuwachs² ∝ Δt^(2H)", fontsize=10)
    axes[1].legend(fontsize=8)
    hh = np.linspace(0.05, 0.95, 100)
    axes[2].plot(hh, 2 ** (2 * hh - 1) - 1, "k-", label="Theorie ρ(1) = 2^(2H−1) − 1")
    axes[2].plot(Hs, [rho1[H] for H in Hs], "o", ms=8, c="tab:orange", label="gemessen")
    axes[2].axhline(0, color="grey", lw=0.5)
    axes[2].set_xlabel("Hurst-Exponent H")
    axes[2].set_ylabel("Korrelation benachbarter Zuwächse")
    axes[2].set_title("H < ½: Umkehr wahrscheinlicher, H > ½: Fortsetzung", fontsize=10)
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    for H in Hs:
        print(f"H = {H}: geschätzt aus dem Variogramm {estimates[H]:.3f};  Korrelation benachbarter Zuwächse {rho1[H]:+.3f} (Theorie {2 ** (2 * H - 1) - 1:+.3f})")


def levy():
    """13. Lévy-Prozesse: Sprünge und schwere Ränder (Zellen 39 von stochasticprocesses.ipynb)."""
    global alpha, angles, axes, big_c, big_g, brown2d, bw, cauchy_inc, cpp_inc, dt, fig, gauss_inc
    global inc, jumps, lengths, levy_flight, lf, n, name, rng, steps2d, tt, x
    rng = np.random.default_rng(12)
    n = 5000
    dt = 1.0 / n
    gauss_inc = rng.normal(0, np.sqrt(dt), n)
    cauchy_inc = stats.cauchy.rvs(scale=dt, size=n, random_state=rng)          # α = 1: Skala wächst wie dt^(1/α) = dt
    jumps = rng.random(n) < 20 * dt                                           # zusammengesetzter Poisson-Prozess: Rate 20
    cpp_inc = jumps * rng.normal(0, 0.3, n)                                  # Sprunghöhen normalverteilt

    alpha = 1.5
    steps2d = stats.levy_stable.rvs(alpha, 0, size=(3000, 2), random_state=rng)
    angles = rng.uniform(0, 2 * np.pi, 3000)
    lengths = np.abs(stats.levy_stable.rvs(alpha, 0, size=3000, random_state=rng))
    levy_flight = np.cumsum(np.c_[lengths * np.cos(angles), lengths * np.sin(angles)], axis=0)
    brown2d = np.cumsum(rng.normal(size=(3000, 2)), axis=0)

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    tt = np.arange(1, n + 1) * dt
    axes[0].plot(tt, np.cumsum(gauss_inc), lw=0.8, label="Brownsche Bewegung")
    axes[0].plot(tt, np.cumsum(cpp_inc), lw=0.8, label="zusammengesetzter Poisson (Rate 20)")
    axes[0].plot(tt, np.cumsum(cauchy_inc), lw=0.8, label="Cauchy-Prozess (α = 1)")
    axes[0].set_yscale("symlog", linthresh=1)                        # linear zwischen −1 und 1, außerhalb logarithmisch
    axes[0].set_xlabel("Zeit t")
    axes[0].set_ylabel("X(t)")
    axes[0].set_title("Drei Lévy-Prozesse: stetig, nur Sprünge, Sprünge aller Größen", fontsize=10)
    axes[0].legend(fontsize=8)
    axes[1].plot(brown2d[:, 0], brown2d[:, 1], lw=0.5, label="Gaußscher Random Walk")
    axes[1].plot(levy_flight[:, 0], levy_flight[:, 1], lw=0.5, label=f"Lévy-Flug (α = {alpha})")
    axes[1].set_aspect("equal", adjustable="datalim")
    axes[1].set_title("3000 Schritte in der Ebene: Haufen und lange Sprünge", fontsize=10)
    axes[1].legend(fontsize=8)
    x = np.geomspace(0.1, 1e4, 200)
    big_g = np.abs(rng.normal(size=10 ** 6)); big_c = np.abs(stats.cauchy.rvs(size=10 ** 6, random_state=rng))
    axes[2].loglog(x, [np.mean(big_g > v) for v in x], label="Normalverteilung")
    axes[2].loglog(x, [np.mean(big_c > v) for v in x], label="Cauchy")
    axes[2].loglog(x, 2 / (np.pi * x), "k--", lw=1, label="2/(πx): Potenzgesetz")
    axes[2].set_ylim(1e-6, 1.5)
    axes[2].set_xlabel("Größe x eines Schritts")
    axes[2].set_ylabel("P(|Schritt| > x)")
    axes[2].set_title("Schwere Ränder: große Schritte sind nicht selten", fontsize=10)
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    for name, inc in [("Brownsch", gauss_inc), ("Cauchy", cauchy_inc)]:
        print(f"{name:8s}: größter Einzelschritt / Summe der Beträge aller Schritte = {np.abs(inc).max() / np.abs(inc).sum():.4f}")
    lf = np.hypot(*np.diff(levy_flight, axis=0).T); bw = np.hypot(*np.diff(brown2d, axis=0).T)
    print(f"Lévy-Flug: die 1 % längsten Schritte tragen {np.sort(lf)[-30:].sum() / lf.sum():.0%} des Weges; beim Gaußschen Random Walk {np.sort(bw)[-30:].sum() / bw.sum():.0%}")
    print(f"Cauchy: Mittelwert von 10^2, 10^4, 10^6 Werten: " + ", ".join(f"{stats.cauchy.rvs(size=m, random_state=rng).mean():+.2f}" for m in (10 ** 2, 10 ** 4, 10 ** 6))
          + "  (kein Gesetz der großen Zahl: der Mittelwert ist wieder Cauchy-verteilt)")


def gaussian_processes():
    """14. Gauß-Prozesse: ein Kern bestimmt den Prozess (Zellen 42 von stochasticprocesses.ipynb)."""
    global L, ax, axes, c, fig, gap, gp_posterior, inside, k, kernels, m, name
    global rng, s, truth, x, xs, ys
    rng = np.random.default_rng(13)
    x = np.linspace(0, 10, 300)
    kernels = {
        "RBF (glatt), ℓ = 1": lambda a, b: np.exp(-0.5 * (a[:, None] - b[None, :]) ** 2),
        "Exponentiell = Ornstein-Uhlenbeck": lambda a, b: np.exp(-np.abs(a[:, None] - b[None, :])),
        "periodisch, Periode 3": lambda a, b: np.exp(-2 * np.sin(np.pi * np.abs(a[:, None] - b[None, :]) / 3) ** 2),
    }

    def gp_posterior(xs, ys, xq, k, noise=0.05):
        """GP-Regression: Mittelwert und Standardabweichung an den Punkten xq nach den Beobachtungen (xs, ys)."""
        K = k(xs, xs) + noise ** 2 * np.eye(len(xs))
        Ks, Kss = k(xq, xs), k(xq, xq)
        Lc = np.linalg.cholesky(K)
        alpha = np.linalg.solve(Lc.T, np.linalg.solve(Lc, ys))
        v = np.linalg.solve(Lc, Ks.T)
        return Ks @ alpha, np.sqrt(np.clip(np.diag(Kss) - np.sum(v ** 2, axis=0), 0, None))

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    for (name, k), c in zip(kernels.items(), ["tab:blue", "tab:orange", "tab:green"]):
        L = np.linalg.cholesky(k(x, x) + 1e-8 * np.eye(len(x)))
        axes[0].plot(x, L @ rng.normal(size=len(x)), c=c, lw=1, label=name)
    axes[0].set_xlabel("x")
    axes[0].set_ylabel("f(x)")
    axes[0].set_title("Je eine Zufallsfunktion aus drei Kernen", fontsize=10)
    axes[0].legend(fontsize=7)
    truth = lambda z: np.sin(z) + 0.3 * z * np.cos(1.5 * z) / 3
    xs = np.array([0.5, 1.8, 3.0, 5.5, 6.2, 8.8])
    ys = truth(xs) + rng.normal(0, 0.05, len(xs))
    for ax, (name, k) in zip(axes[1:], list(kernels.items())[:2]):
        m, s = gp_posterior(xs, ys, x, k)
        ax.plot(x, truth(x), "k:", lw=1, label="wahre Funktion")
        ax.plot(x, m, c="tab:blue", label="Mittelwert der Vorhersage")
        ax.fill_between(x, m - 2 * s, m + 2 * s, color="tab:blue", alpha=0.2, label="± 2 Standardabweichungen")
        ax.plot(xs, ys, "ro", ms=5, label="6 Messpunkte")
        ax.set_xlabel("x")
        ax.set_title(f"GP-Regression mit Kern {name.split(',')[0].split(' (')[0]}", fontsize=10)
        ax.legend(fontsize=7, loc="lower left")
    plt.tight_layout()
    plt.show()

    for name, k in list(kernels.items())[:2]:
        m, s = gp_posterior(xs, ys, x, k)
        gap = (x > 3.5) & (x < 5.0)
        inside = (x >= xs.min()) & (x <= xs.max())
        print(f"{name:34s}: Unsicherheit an den Messpunkten {gp_posterior(xs, ys, xs, k)[1].mean():.3f}, in der Lücke 3.5 < x < 5 im Mittel {s[gap].mean():.3f}; "
              f"Fehler im Bereich der Messpunkte höchstens {np.abs(m - truth(x))[inside].max():.2f}, jenseits von x = {xs.max()} bis {np.abs(m - truth(x))[~inside].max():.2f}")


def branching():
    """15. Verzweigungsprozesse: Aussterben oder Explosion (Zellen 45 von stochasticprocesses.ipynb)."""
    global Z15, alive, axes, c, colors, extinction_probability, fig, g, galton_watson, gens, line, m
    global ms, n30, rng, runs, surv, surv1, z
    rng = np.random.default_rng(14)

    def galton_watson(m, generations, n_runs, rng, cap=10 ** 6):
        """Galton-Watson-Prozess: jedes Individuum hat Poisson(m) Nachkommen. Gibt die Größen Z_0 ... Z_g zurück."""
        Z = np.zeros((n_runs, generations + 1), dtype=np.int64); Z[:, 0] = 1
        for g in range(generations):
            z = np.minimum(Z[:, g], cap)
            Z[:, g + 1] = rng.poisson(m * z)                         # Summe von z unabhängigen Poisson(m) ist Poisson(m·z)
        return Z

    def extinction_probability(m):
        """Kleinste Lösung von q = exp(m(q − 1)), der erzeugenden Funktion der Poisson-Verteilung."""
        q = 0.0
        for _ in range(10_000):
            q = np.exp(m * (q - 1))
        return q

    ms = [0.8, 1.0, 1.2, 1.5, 2.0]
    colors = ["tab:blue", "tab:grey", "tab:green", "tab:orange", "tab:red"]
    runs = {m: galton_watson(m, 60, 20_000, rng) for m in ms}         # je 20 000 Stammbäume über 60 Generationen

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    n30 = np.arange(31)
    for z in galton_watson(1.0, 30, 20, rng):
        axes[0].plot(n30, z, lw=0.8)
    axes[0].axhline(1, color="k", ls="--", lw=1.5, label="Mittelwert mⁿ = 1")
    axes[0].set_xlabel("Generation n")
    axes[0].set_ylabel("Größe Z_n")
    axes[0].set_title("m = 1 (kritisch): fast alle sterben früh aus, einzelne wachsen eine Weile", fontsize=10)
    axes[0].legend(fontsize=8)
    Z15 = galton_watson(1.5, 30, 20, rng)
    for z in Z15:
        alive = z > 0
        line, = axes[1].semilogy(n30, np.where(alive, z, np.nan), lw=0.8)
        if not alive[-1]:
            g = np.argmax(~alive)                                    # erste Generation ohne Individuen
            axes[1].plot(g - 1, z[g - 1], "x", c=line.get_color(), ms=7)
    axes[1].semilogy(n30, 1.5 ** n30, "k--", lw=1.5, label="Mittelwert mⁿ = 1.5ⁿ")
    axes[1].set_xlabel("Generation n")
    axes[1].set_ylabel("Größe Z_n")
    axes[1].set_title(f"m = 1.5 (überkritisch): {np.sum(Z15[:, -1] == 0)} von 20 sterben früh aus (×)", fontsize=10)
    axes[1].legend(fontsize=8)
    gens = np.arange(61)
    for m, c in zip(ms, colors):
        surv = (runs[m] > 0).mean(axis=0)
        axes[2].semilogy(gens, np.where(surv > 0, surv, np.nan), c=c, label=f"m = {m}")
        if m > 1:
            axes[2].axhline(1 - extinction_probability(m), color=c, ls="--", lw=1)
    axes[2].semilogy(gens, 0.8 ** gens, c="tab:blue", ls="--", lw=1, label="0.8ⁿ (obere Schranke)")
    axes[2].semilogy(gens[1:], 2 / gens[1:], "k:", lw=1.5, label="2/n (kritisch)")
    axes[2].set_ylim(1e-4, 1.2)
    axes[2].set_xlabel("Generation n")
    axes[2].set_ylabel("Anteil noch lebender Stammbäume")
    axes[2].set_title("Überleben: gestrichelt 1 − q für m > 1", fontsize=10)
    axes[2].legend(fontsize=8, ncol=2)
    plt.tight_layout()
    plt.show()

    for m in ms:
        print(f"m = {m}: ausgestorben nach 60 Generationen {np.mean(runs[m][:, -1] == 0):.3f}, Theorie q = {extinction_probability(m):.3f}")
    surv1 = (runs[1.0] > 0).mean(axis=0)
    print("Kritisch (m = 1), Anteil lebender Stammbäume bei n = 10, 30, 60: " + ", ".join(f"{surv1[n]:.3f} (2/n = {2 / n:.3f})" for n in (10, 30, 60)))
