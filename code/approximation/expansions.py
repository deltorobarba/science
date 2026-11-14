"""Reihen und ihre Grenzen für approximation.ipynb: Konvergenzradius, Runge und Tschebyschow, asymptotische Reihen.

Schritt 1: Die Taylor-Reihe von 1/(1+x²) bricht bei |x| = 1 ab, obwohl die Funktion auf der reellen Achse glatt ist;
schuld sind die Pole bei ±i. Interpolation mit gleichabständigen Stützstellen divergiert (Runge), mit
Tschebyschow-Knoten konvergiert sie mit der Rate, die der Abstand der Pole vorgibt; ein Knick (|x|) bremst sie.
Schritt 2: Mikroskop, Weitwinkel und Mosaik. softplus(x) = ln(1 + eˣ) auf [−5, 5], mit gleich vielen Parametern
genähert durch Taylor um 0 und Padé (lokal, aus den Ableitungen bei 0), Tschebyschow-Interpolation und Minimax-Polynom
(global, Fehler über das Intervall bewertet; Minimax mit dem Remez-Algorithmus) und kubischen Spline (stückweise).
Schritt 3: Die Stirling-Reihe für ln n! divergiert für jedes n und ist trotzdem die beste Näherung, wenn man beim
kleinsten Term abschneidet; ihr erster Term macht aus dem Zählen von Bitfolgen die Entropie. Alles ohne Daten.
"""
import numpy as np
import matplotlib.pyplot as plt
import mpmath
from numpy.polynomial import chebyshev as cheb, polynomial as poly
from scipy.interpolate import BarycentricInterpolator, CubicSpline
from scipy.special import gammaln


def _f(x):
    return 1 / (1 + x ** 2)


def _interp(nodes, g, x):
    return BarycentricInterpolator(nodes, g(nodes))(x)


def _cheb_nodes(n, L):
    k = np.arange(n + 1)
    return L * np.cos((2 * k + 1) * np.pi / (2 * (n + 1)))


# ---- Schritt 1: Konvergenzradius, Runge und Tschebyschow

def plot_radius(L=5.0, degree=16, degrees=(2, 4, 8, 12, 16, 24, 32, 48, 64)):
    """Links Taylor-Reihen von 1/(1+x²), Mitte Interpolation auf [−L, L], rechts der größte Fehler gegen den Grad."""
    x = np.linspace(-L, L, 4001)
    rho = (1 + np.sqrt(1 + L ** 2)) / L                 # Bernstein-Ellipse durch die Pole ±i, auf [−1, 1] skaliert
    print(f"Taylor-Reihe um 0: 1 − x² + x⁴ − …, Konvergenzradius 1 (Abstand der Pole ±i vom Entwicklungspunkt)")
    for n in (4, 16, 32):
        t = lambda xx: sum((-1) ** k * xx ** (2 * k) for k in range(n // 2 + 1))
        print(f"  Grad {n:2d}: Fehler bei x = 0.5 {abs(t(0.5) - _f(0.5)):.1e}, bei x = 0.9 {abs(t(0.9) - _f(0.9)):.1e}, "
              f"bei x = 1.1 {abs(t(1.1) - _f(1.1)):.1e}")
    rows = []
    for n in degrees:
        e_eq = np.max(np.abs(_interp(np.linspace(-L, L, n + 1), _f, x) - _f(x))) if n <= 48 else np.nan
        e_ch = np.max(np.abs(_interp(_cheb_nodes(n, L), _f, x) - _f(x)))
        e_abs = np.max(np.abs(_interp(_cheb_nodes(n, L), np.abs, x) - np.abs(x)))
        rows.append((n, e_eq, e_ch, rho ** -n, e_abs))
    rows = np.array(rows)
    print(f"Interpolation auf [−{L:g}, {L:g}], größter Fehler (gleichabständig | Tschebyschow | Vorhersage ρ^−n mit "
          f"ρ = {rho:.3f} | Tschebyschow für |x|):")
    for n, a, b, c, d in rows:
        print(f"  Grad {int(n):2d}: " + ("        –" if np.isnan(a) else f"{a:9.1e}") + f" | {b:.1e} | {c:.1e} | {d:.1e}")

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.6))
    ax = axes[0]
    xs = np.linspace(-1.6, 1.6, 801)
    ax.plot(xs, _f(xs), color="black", lw=2.5, label="1/(1+x²)")
    for n, c in [(2, "tab:orange"), (8, "tab:green"), (32, "tab:red")]:
        t = sum((-1) ** k * xs ** (2 * k) for k in range(n // 2 + 1))
        ax.plot(xs, t, color=c, lw=1.2, label=f"Taylor bis Grad {n}")
    ax.axvspan(-1, 1, color="grey", alpha=0.12, label="Konvergenzradius |x| < 1")
    ax.set_ylim(-0.5, 1.6)
    ax.set_xlabel("x")
    ax.set_ylabel("Wert")
    ax.set_title("Taylor um 0: mehr Terme helfen nur innerhalb |x| < 1", fontsize=10)
    ax.legend(fontsize=8, loc="lower center")
    ax = axes[1]
    ax.plot(x, _f(x), color="black", lw=2.5, label="1/(1+x²)")
    ax.plot(x, _interp(np.linspace(-L, L, degree + 1), _f, x), color="tab:red", lw=1.2,
            label=f"gleichabständige Knoten, Grad {degree}")
    ax.plot(x, _interp(_cheb_nodes(degree, L), _f, x), color="tab:blue", lw=1.2,
            label=f"Tschebyschow-Knoten, Grad {degree}")
    ax.plot(_cheb_nodes(degree, L), _f(_cheb_nodes(degree, L)), "o", color="tab:blue", ms=3)
    ax.set_ylim(-1, 2.5)
    ax.set_xlabel("x")
    ax.set_title(f"Interpolation auf [−{L:g}, {L:g}]: Runge gegen Tschebyschow", fontsize=10)
    ax.legend(fontsize=8, loc="upper center")
    ax = axes[2]
    ok = ~np.isnan(rows[:, 1])
    ax.semilogy(rows[ok, 0], rows[ok, 1], "s-", color="tab:red", label="1/(1+x²), gleichabständig")
    ax.semilogy(rows[:, 0], rows[:, 2], "o-", color="tab:blue", label="1/(1+x²), Tschebyschow")
    ax.semilogy(rows[:, 0], rows[:, 3], "--", color="tab:blue", lw=1, label=f"Vorhersage aus den Polen: {rho:.2f}^−n")
    ax.semilogy(rows[:, 0], rows[:, 4], "^-", color="tab:purple", label="|x| (Knick), Tschebyschow: etwa 1/n")
    ax.set_xlabel("Grad n")
    ax.set_ylabel("größter Fehler auf dem Intervall")
    ax.set_title("Wie schnell es konvergiert, sagen die Singularitäten", fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()


# ---- Schritt 2: Mikroskop, Weitwinkel und Mosaik

def _softplus(x):
    return np.logaddexp(0, x)                                       # ln(1 + eˣ) ohne Überlauf


def _softplus_mp(z):
    return mpmath.log(1 + mpmath.exp(z))


def _remez(f, n, L, grid_size=20001, iters=80):
    """Minimax-Polynom vom Grad n auf [−L, L] (Remez-Austausch): Fehler pendelt mit gleicher Höhe ±E an n + 2 Stellen."""
    k = np.arange(n + 2)
    xs = -L * np.cos(np.pi * k / (n + 1))                           # Start: Extrema des Tschebyschow-Polynoms
    grid = np.linspace(-L, L, grid_size)
    for _ in range(iters):
        A = np.hstack([np.vander(xs, n + 1, increasing=True), ((-1.0) ** k)[:, None]])
        sol = np.linalg.solve(A, f(xs))
        c, E = sol[:-1], sol[-1]
        err = f(grid) - poly.polyval(grid, c)
        cuts = np.flatnonzero(np.diff(np.sign(err)) != 0) + 1          # Abschnitte mit gleichem Vorzeichen
        ext = [seg[np.argmax(np.abs(err[seg]))] for seg in np.split(np.arange(grid.size), cuts)]
        while len(ext) > n + 2:                                      # zu viele Abschnitte: die kleinsten Ausschläge weg
            ext.pop(min(range(len(ext)), key=lambda j: abs(err[ext[j]])))
        if len(ext) < n + 2:
            break
        new = grid[ext]
        if np.allclose(new, xs, atol=1e-10):
            break
        xs = new
    return c, abs(E)


def _lenses(n, L, x):
    """Die fünf Näherungen mit je n + 1 Parametern (Polynome vom Grad n, Padé [n − n//2 / n//2], Spline durch n + 1 Punkte)."""
    mpmath.mp.dps = 50
    t = mpmath.taylor(_softplus_mp, 0, n)
    p, q = mpmath.pade(t, n - n // 2, n // 2)
    c_minimax, E = _remez(_softplus, n, L)
    knots = np.linspace(-L, L, n + 1)
    approx = {
        "Taylor um 0": poly.polyval(x, [float(a) for a in t]),
        f"Padé [{n - n // 2}/{n // 2}]": poly.polyval(x, [float(a) for a in p]) / poly.polyval(x, [float(a) for a in q]),
        "Tschebyschow-Interpolation": cheb.Chebyshev.interpolate(_softplus, n, domain=[-L, L])(x),
        "Minimax (Remez)": poly.polyval(x, c_minimax),
        "kubischer Spline": CubicSpline(knots, _softplus(knots))(x),
    }
    return approx, E, knots


def plot_lenses(L=5.0, n_param=10, n_params=range(4, 27, 2), points=(0.1, 1.0, 3.0, 5.0)):
    """softplus auf [−L, L]: links die Näherungen, Mitte der Fehler über x, rechts der größte Fehler gegen die Parameter."""
    x = np.linspace(-L, L, 20001)
    f = _softplus(x)
    n = n_param - 1
    approx, E, knots = _lenses(n, L, x)
    colors = dict(zip(approx, ["tab:red", "tab:orange", "tab:blue", "tab:purple", "tab:green"]))
    print(f"softplus(x) = ln(1 + eˣ) auf [−{L:g}, {L:g}]; Singularitäten bei ±iπ, Taylor-Reihe um 0 konvergiert für |x| < π")
    print(f"Je {n_param} Parameter (Polynome vom Grad {n}, Spline durch {n_param} Punkte). Fehler bei x = "
          + ", ".join(f"{p:g}" for p in points) + " und größter Fehler auf dem Intervall:")
    for name, y in approx.items():
        err = np.abs(y - f)
        at = [err[np.argmin(np.abs(x - p))] for p in points]
        print(f"  {name:27s} " + "  ".join(f"{e:8.1e}" for e in at) + f"   | größter {err.max():.1e}")
    print(f"Minimax: Der Fehler pendelt zwischen +{E:.2e} und −{E:.2e} an {n + 2} Stellen (Satz von Tschebyschow)")
    rows = []
    for m in n_params:
        a, _, _ = _lenses(m - 1, L, x)
        rows.append([np.max(np.abs(y - f)) for y in a.values()])
    rows = np.array(rows)
    print("Größter Fehler gegen die Zahl der Parameter (Taylor | Padé | Tschebyschow | Minimax | Spline):")
    for m, r in zip(n_params, rows):
        print(f"  {m:2d}: " + " | ".join(f"{v:.1e}" for v in r))

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.6))
    ax = axes[0]
    ax.plot(x, f, color="black", lw=3, label="softplus(x) = ln(1 + eˣ)")
    for name, y in approx.items():
        ax.plot(x, y, color=colors[name], lw=1.2, label=name)
    ax.set_ylim(-1, 6)
    ax.set_xlabel("x")
    ax.set_ylabel("Wert")
    ax.set_title(f"{n_param} Parameter je Verfahren: nur Taylor fällt sichtbar heraus", fontsize=10)
    ax.legend(fontsize=8, loc="upper left")
    ax = axes[1]
    for name, y in approx.items():
        ax.semilogy(x, np.maximum(np.abs(y - f), 1e-17), color=colors[name], lw=1, label=name)
    ax.axhline(E, color="tab:purple", ls="--", lw=0.8)
    ax.text(-L, E * 2, f" Minimax: ±{E:.1e}", fontsize=8, color="tab:purple")
    ax.plot(knots, np.full(knots.size, 3e-17), "|", color="tab:green", ms=8)
    for s in (-np.pi, np.pi):
        ax.axvline(s, color="grey", ls=":", lw=1)
    ax.text(np.pi, 1e1, " |x| = π", fontsize=8, color="grey")
    ax.set_ylim(1e-17, 1e2)
    ax.set_xlabel("x")
    ax.set_ylabel("Fehler |Näherung − softplus|")
    ax.set_title("Mikroskop gegen Weitwinkel: wo der Fehler sitzt", fontsize=10)
    ax.legend(fontsize=7, loc="lower left")
    ax = axes[2]
    for j, name in enumerate(approx):
        ax.semilogy(list(n_params), rows[:, j], "o-", ms=4, color=colors[name], label=name.split(" [")[0])
    ax.set_xlabel("Zahl der Parameter")
    ax.set_ylabel(f"größter Fehler auf [−{L:g}, {L:g}]")
    ax.set_title("Mehr Parameter: Taylor divergiert, der Spline wird nur langsam besser", fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()


# ---- Schritt 3: asymptotische Reihen

def stirling_error(n, K):
    """|Stirling mit K Korrekturtermen − ln n!|, mit 50 Stellen gerechnet (mpmath)."""
    import mpmath as mp
    mp.mp.dps = 50
    s = n * mp.log(n) - n + mp.log(2 * mp.pi * n) / 2
    out = [abs(s - mp.loggamma(n + 1))]
    for k in range(1, K + 1):
        s += mp.bernoulli(2 * k) / (2 * k * (2 * k - 1) * mp.mpf(n) ** (2 * k - 1))
        out.append(abs(s - mp.loggamma(n + 1)))
    return np.array([float(v) for v in out])


def plot_stirling(ns=(1, 2, 3, 5), K=30, Ns=(10, 100, 1000)):
    """Links der Fehler der Stirling-Reihe gegen die Zahl der Korrekturterme, rechts log₂(N über k)/N gegen die Entropie."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.6))
    ax = axes[0]
    print("Stirling: ln n! ≈ n ln n − n + ½ ln(2πn) + 1/(12n) − 1/(360n³) + …")
    for n, c in zip(ns, ["tab:red", "tab:orange", "tab:green", "tab:blue"]):
        e = stirling_error(n, K)
        k = int(np.argmin(e))
        print(f"  n = {n}: ohne Korrektur Fehler {e[0]:.1e}; am besten nach {k} Termen (π·n = {np.pi * n:.1f}) mit "
              f"{e[k]:.1e}; nach {K} Termen {e[-1]:.1e}")
        ax.semilogy(np.arange(K + 1), e, "o-", ms=3, color=c, label=f"n = {n}")
        ax.semilogy(k, e[k], "*", ms=12, color=c)
    ax.set_ylim(1e-17, 1e3)
    ax.set_xlabel("Zahl der Korrekturterme K")
    ax.set_ylabel("|Stirling − ln n!|")
    ax.set_title("Divergent, aber nützlich: beim kleinsten Term abschneiden (★)", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[1]
    p = np.linspace(0, 1, 401)
    H = -np.where(p > 0, p * np.log2(np.where(p > 0, p, 1)), 0) - np.where(p < 1, (1 - p) * np.log2(np.where(p < 1, 1 - p, 1)), 0)
    ax.plot(p, H, color="black", lw=2.5, label="Entropie H(p) in Bit")
    print("Anzahl der Bitfolgen der Länge N mit k Einsen: (N über k) ≈ 2^(N·H(k/N))")
    for N, c in zip(Ns, ["tab:orange", "tab:green", "tab:blue"]):
        k = np.arange(N + 1)
        lc = (gammaln(N + 1) - gammaln(k + 1) - gammaln(N - k + 1)) / np.log(2) / N
        Hk = np.interp(k / N, p, H)
        print(f"  N = {N:4d}: größte Abweichung von H {np.max(np.abs(lc - Hk)):.4f} Bit je Zeichen "
              f"(Stirling: log₂(2πN/4)/(2N) = {np.log2(2 * np.pi * N / 4) / (2 * N):.4f} bei k = N/2)")
        ax.plot(k / N, lc, ".-" if N <= 10 else "-", color=c, lw=1, ms=5, label=f"log₂(N über k)/N, N = {N}")
    ax.set_xlabel("Anteil der Einsen p = k/N")
    ax.set_ylabel("Bit je Zeichen")
    ax.set_title("Stirling macht aus dem Zählen die Entropie", fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()
