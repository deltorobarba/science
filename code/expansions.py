"""Reihen und ihre Grenzen für approximation.ipynb: Konvergenzradius, Runge und Tschebyschow, asymptotische Reihen.

Schritt 1: Die Taylor-Reihe von 1/(1+x²) bricht bei |x| = 1 ab, obwohl die Funktion auf der reellen Achse glatt ist;
schuld sind die Pole bei ±i. Interpolation mit gleichabständigen Stützstellen divergiert (Runge), mit
Tschebyschow-Knoten konvergiert sie mit der Rate, die der Abstand der Pole vorgibt; ein Knick (|x|) bremst sie.
Schritt 2: Die Stirling-Reihe für ln n! divergiert für jedes n und ist trotzdem die beste Näherung, wenn man beim
kleinsten Term abschneidet; ihr erster Term macht aus dem Zählen von Bitfolgen die Entropie. Alles ohne Daten.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import BarycentricInterpolator
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


# ---- Schritt 2: asymptotische Reihen

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
