"""Testfunktionen in beiden Bedeutungen: Bump-Funktionen, Mollifier, Distributionen und schwache Lösungen; Benchmark-Funktionen der Optimierung (Himmelblau, Rosenbrock, Rastrigin) und glatte Fenster und Zeitpläne in Quantenalgorithmen.

Für analysis.ipynb aus testfunctions.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: why_testfunctions, bump_function, building_blocks, mollifier, distributions, weak_solution, fourier_decay, gallery, gallery_contours, gallery_landscapes, himmelblau_minima, rosenbrock_valley, many_minima, fair_comparison, windowed_phase_estimation, adiabatic_schedules, grover_minimum, vqe_landscapes.
"""
import math
import time
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from matplotlib.colors import ListedColormap
from scipy.integrate import quad, solve_ivp, trapezoid
from scipy.optimize import brentq, minimize, differential_evolution, dual_annealing, basinhopping
from scipy.stats import special_ortho_group
from matplotlib.colors import LogNorm, Normalize


def why_testfunctions():
    """48. Wofür man Testfunktionen der Analysis braucht (Zellen 6 von testfunctions.ipynb)."""
    global GALERIE, PSI_INTEGRAL, Zaehler, ackley, beale, booth, bump, camel, easom, eggholder, f_exp, glaetten
    global glatter_uebergang, goldstein_price, himmelblau, phi_eps, rastrigin, rng, rosenbrock, schwefel, styblinski_tang
    # numpy, scipy, matplotlib und sympy sind in Colab vorinstalliert; installiert wird nichts.

    rng = np.random.default_rng(2026)


    def f_exp(x):
        """f(x) = e^(−1/x) für x > 0, sonst 0: glatt, alle Ableitungen bei 0 sind null."""
        x = np.asarray(x, dtype=float)
        pos = x > 0
        return np.where(pos, np.exp(-1 / np.where(pos, x, 1.0)), 0.0)


    def bump(x):
        """Standard-Bump-Funktion Ψ(x) = e^(−1/(1 − x²)) für |x| < 1, sonst 0."""
        return f_exp(1 - np.asarray(x, dtype=float) ** 2)


    def glatter_uebergang(x):
        """S(x) = f(x) / (f(x) + f(1 − x)): 0 für x ≤ 0, 1 für x ≥ 1, dazwischen glatt."""
        x = np.asarray(x, dtype=float)
        return f_exp(x) / (f_exp(x) + f_exp(1 - x))


    PSI_INTEGRAL = quad(lambda x: math.exp(-1 / (1 - x * x)), -1, 1, epsabs=1e-14)[0]     # ∫Ψ dx


    def phi_eps(x, eps):
        """Normierter Mollifier φ_ε(x) = Ψ(x/ε) / (ε ∫Ψ): Träger [−ε, ε], Integral 1."""
        return bump(np.asarray(x, dtype=float) / eps) / (eps * PSI_INTEGRAL)


    def glaetten(werte, x, eps):
        """Faltung u ∗ φ_ε auf dem gleichmäßigen Gitter x (außerhalb des Gitters gilt u = 0)."""
        dx = x[1] - x[0]
        n = int(np.ceil(eps / dx))
        kern = phi_eps(np.arange(-n, n + 1) * dx, eps)
        return np.convolve(werte, kern / kern.sum(), mode="same")


    # Benchmark-Funktionen: X hat die Form (d, ...), die erste Achse sind die Koordinaten.
    def booth(X):
        x, y = X
        return (x + 2 * y - 7) ** 2 + (2 * x + y - 5) ** 2

    def rosenbrock(X):
        x, y = X
        return (1 - x) ** 2 + 100 * (y - x ** 2) ** 2

    def beale(X):
        x, y = X
        return (1.5 - x + x * y) ** 2 + (2.25 - x + x * y ** 2) ** 2 + (2.625 - x + x * y ** 3) ** 2

    def himmelblau(X):
        x, y = X
        return (x ** 2 + y - 11) ** 2 + (x + y ** 2 - 7) ** 2

    def camel(X):
        x, y = X
        return (4 - 2.1 * x ** 2 + x ** 4 / 3) * x ** 2 + x * y + (4 * y ** 2 - 4) * y ** 2

    def goldstein_price(X):
        x, y = X
        a = 1 + (x + y + 1) ** 2 * (19 - 14 * x + 3 * x ** 2 - 14 * y + 6 * x * y + 3 * y ** 2)
        b = 30 + (2 * x - 3 * y) ** 2 * (18 - 32 * x + 12 * x ** 2 + 48 * y - 36 * x * y + 27 * y ** 2)
        return a * b

    def styblinski_tang(X):
        X = np.asarray(X)
        return 0.5 * np.sum(X ** 4 - 16 * X ** 2 + 5 * X, axis=0)

    def rastrigin(X):
        X = np.asarray(X)
        return 10 * X.shape[0] + np.sum(X ** 2 - 10 * np.cos(2 * np.pi * X), axis=0)

    def ackley(X):
        X = np.asarray(X)
        d = X.shape[0]
        return (-20 * np.exp(-0.2 * np.sqrt(np.sum(X ** 2, axis=0) / d))
                - np.exp(np.sum(np.cos(2 * np.pi * X), axis=0) / d) + 20 + np.e)

    def easom(X):
        x, y = X
        return -np.cos(x) * np.cos(y) * np.exp(-(x - np.pi) ** 2 - (y - np.pi) ** 2)

    def schwefel(X):
        X = np.asarray(X)
        return 418.9829 * X.shape[0] - np.sum(X * np.sin(np.sqrt(np.abs(X))), axis=0)

    def eggholder(X):
        x, y = X
        return -(y + 47) * np.sin(np.sqrt(np.abs(x / 2 + y + 47))) - x * np.sin(np.sqrt(np.abs(x - (y + 47))))


    # Name: (Funktion, Suchgebiet, Bildausschnitt, tabellierte Minimalstellen, tabellierter Minimalwert)
    GALERIE = {
        "Booth": (booth, [(-10, 10)] * 2, [(-10, 10)] * 2, [(1, 3)], 0.0),
        "Rosenbrock": (rosenbrock, [(-2, 2), (-1, 3)], [(-2, 2), (-1, 3)], [(1, 1)], 0.0),
        "Beale": (beale, [(-4.5, 4.5)] * 2, [(-4.5, 4.5)] * 2, [(3, 0.5)], 0.0),
        "Himmelblau": (himmelblau, [(-5, 5)] * 2, [(-5, 5)] * 2,
                       [(3, 2), (-2.805118, 3.131312), (-3.779310, -3.283186), (3.584428, -1.848126)], 0.0),
        "Six-Hump Camel": (camel, [(-3, 3), (-2, 2)], [(-2, 2), (-1.2, 1.2)], [(0.0898, -0.7126), (-0.0898, 0.7126)], -1.0316),
        "Goldstein–Price": (goldstein_price, [(-2, 2)] * 2, [(-2, 2)] * 2, [(0, -1)], 3.0),
        "Styblinski–Tang": (styblinski_tang, [(-5, 5)] * 2, [(-5, 5)] * 2, [(-2.903534, -2.903534)], -78.33234),
        "Rastrigin": (rastrigin, [(-5.12, 5.12)] * 2, [(-5.12, 5.12)] * 2, [(0, 0)], 0.0),
        "Ackley": (ackley, [(-32.768, 32.768)] * 2, [(-5, 5)] * 2, [(0, 0)], 0.0),
        "Easom": (easom, [(-100, 100)] * 2, [(-1, 7)] * 2, [(np.pi, np.pi)], -1.0),
        "Schwefel": (schwefel, [(-500, 500)] * 2, [(-500, 500)] * 2, [(420.9687, 420.9687)], 0.0),
        "Eggholder": (eggholder, [(-512, 512)] * 2, [(-512, 512)] * 2, [(512, 404.2319)], -959.6407),
    }


    class Zaehler:
        """Zählt Funktionsauswertungen; ein Aufruf mit d × S Punkten zählt S-mal."""

        def __init__(self, f):
            self.f, self.n = f, 0

        def __call__(self, x):
            x = np.asarray(x, dtype=float)
            self.n += 1 if x.ndim == 1 else x.shape[1]
            return self.f(x)


    print(f"∫Ψ dx = {PSI_INTEGRAL:.6f}")


def bump_function():
    """49. Die Bump-Funktion: glatt, aber nicht analytisch (Zellen 8 von testfunctions.ipynb)."""
    global C, abl, abl_wert, ableitungen, axes, fak, fig, m, maxima, n, n_, x_sym
    global xp, xs, xx
    x_sym = sp.symbols("x")
    ableitungen = [sp.exp(-1 / (1 - x_sym ** 2))]
    for n in range(12):
        ableitungen.append(sp.diff(ableitungen[-1], x_sym))
    abl = [sp.lambdify(x_sym, a, "numpy") for a in ableitungen]


    def abl_wert(n, x):
        """Ψ^(n)(x), außerhalb von (−1, 1) gleich 0."""
        x = np.atleast_1d(np.asarray(x, dtype=float))
        out = np.zeros_like(x)
        innen = np.abs(x) < 1
        with np.errstate(over="ignore", under="ignore"):
            out[innen] = abl[n](x[innen])
        return out


    xs = np.linspace(-0.9995, 0.9995, 40001)
    maxima = np.array([np.max(np.abs(abl_wert(n, xs))) for n in range(13)])
    fak = np.array([math.factorial(n) for n in range(13)], dtype=float)
    print("Ψ^(n)(1 − h) geht gegen 0, aber erst sehr nahe am Rand:")
    for n in [1, 2, 4, 8]:
        print(f"  n = {n}: " + "   ".join(f"h = {h}: {abl_wert(n, 1 - h)[0]:9.2e}" for h in [0.05, 0.01, 0.002]))
    print(f"Ψ(0.9) = {bump(0.9):.2e} > 0, obwohl jede Taylor-Näherung um x = 1 null ist")
    print("max|Ψ^(n)| / n!   für n = 0..12:", " ".join(f"{v:.1e}" for v in maxima / fak))
    print("max|Ψ^(n)| / (n!)² für n = 0..12:", " ".join(f"{v:.1e}" for v in maxima / fak ** 2))
    C = np.exp(np.polyfit(np.arange(4, 13), np.log(maxima[4:] / fak[4:] ** 2), 1)[0])
    print(f"max|Ψ^(n)| / (n!)² wächst geometrisch mit dem Faktor C ≈ {C:.2f} pro Ordnung (Gevrey-Klasse 2)")

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.6))
    xp = np.linspace(-1.3, 1.3, 2001)
    for n in [0, 1, 2, 4, 8]:
        axes[0].plot(xp, abl_wert(n, xp) / maxima[n], label="Ψ" if n == 0 else f"Ψ^({n})")
    axes[0].set_xlabel("x")
    axes[0].set_ylabel("Wert / Maximum des Betrags")
    axes[0].set_title("Bump-Funktion und Ableitungen, alle mit Träger [−1, 1]")
    axes[0].legend(fontsize=8)
    n_ = np.arange(13)
    axes[1].semilogy(n_, maxima / fak, "o-", label="max|Ψ^(n)| / n!")
    axes[1].semilogy(n_, maxima / fak ** 2, "s-", label="max|Ψ^(n)| / (n!)²")
    axes[1].semilogy(n_, maxima[4] / fak[4] ** 2 * C ** (n_ - 4.0), "k--", lw=1, label=f"geometrisch, Faktor {C:.1f}")
    axes[1].set_xlabel("Ordnung n")
    axes[1].set_ylabel("Quotient")
    axes[1].set_title("Wachstum der Ableitungen")
    axes[1].legend(fontsize=8)
    xx = np.logspace(-2, 0, 400)
    axes[2].loglog(xx, f_exp(xx), "k", lw=2.5, label="e^(−1/x)")
    for m in [5, 10, 20]:
        axes[2].loglog(xx, xx ** m, label=f"x^{m}")
    axes[2].set_ylim(1e-45, 2)
    axes[2].set_xlabel("x")
    axes[2].set_ylabel("Wert")
    axes[2].set_title("e^(−1/x) wird bei 0 flacher als jede Potenz")
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()


def building_blocks():
    """50. Bausteine: glatter Übergang, Plateau, Zerlegung der Eins (Zellen 11 von testfunctions.ipynb)."""
    global S, a_pl, anzahl, axes, b_pl, chi, dS, ddS, fig, k, ks, nenner
    global plateau, psi, summe, xg, xs
    xs = np.linspace(-0.5, 1.5, 8001)
    S = glatter_uebergang(xs)
    dS = np.gradient(S, xs)
    ddS = np.gradient(dS, xs)
    print(f"S(0.5) = {glatter_uebergang(0.5):.3f}; größte Abweichung von S(x) + S(1 − x) = 1: "
          f"{np.max(np.abs(S + glatter_uebergang(1 - xs) - 1)):.1e}")
    print(f"S = 0 für alle x ≤ 0: {np.all(S[xs <= 0] == 0)};  S = 1 für alle x ≥ 1: {np.all(S[xs >= 1] == 1)}")

    xg = np.linspace(-3, 3, 12001)
    a_pl, b_pl = 1.0, 2.0
    plateau = glatter_uebergang((b_pl - np.abs(xg)) / (b_pl - a_pl))
    print(f"Plateau: genau 1 auf [−1, 1]: {np.all(plateau[np.abs(xg) <= a_pl] == 1)};  "
          f"genau 0 außerhalb von (−2, 2): {np.all(plateau[np.abs(xg) >= b_pl] == 0)}")

    psi = lambda t: bump(t / 0.75)                          # Träger [−0.75, 0.75], breiter als 1
    ks = range(-5, 6)
    nenner = sum(psi(xg - j) for j in ks)
    chi = {k: psi(xg - k) / nenner for k in ks}
    summe = sum(chi.values())
    anzahl = sum((c > 0).astype(int) for c in chi.values())
    print(f"Zerlegung der Eins auf [−3, 3]: größte Abweichung |Σχ_k − 1| = {np.max(np.abs(summe - 1)):.1e}; "
          f"an jeder Stelle {anzahl.min()} bis {anzahl.max()} Terme ungleich 0")

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.4))
    axes[0].plot(xs, S, "k", lw=2.5, label="S(x)")
    axes[0].plot(xs, dS / np.max(np.abs(dS)), label="S'(x) / max|S'|")
    axes[0].plot(xs, ddS / np.max(np.abs(ddS)), label="S''(x) / max|S''|")
    axes[0].set_xlabel("x")
    axes[0].set_ylabel("Wert")
    axes[0].set_title("Glatter Übergang von 0 nach 1")
    axes[0].legend(fontsize=8)
    axes[1].plot(xg, plateau, "k", lw=2.5, label="Plateau χ: 1 auf [−1, 1], 0 ab |x| = 2")
    axes[1].plot(xg, bump(xg / 2) / bump(0), "--", label="Ψ(x/2) / Ψ(0) zum Vergleich")
    axes[1].set_xlabel("x")
    axes[1].set_ylabel("Wert")
    axes[1].set_title("Glatte Abschneidefunktion")
    axes[1].legend(fontsize=8)
    for k in range(-3, 4):
        axes[2].plot(xg, chi[k], lw=1.5, label=f"χ_{k}" if abs(k) <= 1 else None)
    axes[2].plot(xg, summe, "k--", lw=2, label="Σ χ_k")
    axes[2].set_xlim(-3, 3)
    axes[2].set_xlabel("x")
    axes[2].set_ylabel("Wert")
    axes[2].set_title("Zerlegung der Eins")
    axes[2].legend(fontsize=8, loc="center right")
    plt.tight_layout()
    plt.show()


def mollifier():
    """51. Glätten mit einem Mollifier (Zellen 14 von testfunctions.ipynb)."""
    global axes, betrag, dx, e_, eps, epsilons, fehler_betrag, fehler_kasten, fig, gb, gk, innen
    global kasten, m1, ort, traeger, weier, x
    x = np.linspace(-3, 3, 30001)
    dx = x[1] - x[0]
    m1 = quad(lambda z: abs(z) * math.exp(-1 / (1 - z * z)), -1, 1, epsabs=1e-14)[0] / PSI_INTEGRAL
    print(f"m1 = ∫|z| φ(z) dz = {m1:.5f}")
    betrag = np.abs(x)
    kasten = np.where(np.abs(x) < 1, 1.0, 0.0) + 0.5 * np.isclose(np.abs(x), 1)      # Mittelwert am Sprung
    weier = sum(0.5 ** k * np.cos(3 ** k * np.pi * x) for k in range(7))
    innen = np.abs(x) < 2                                    # fern vom Gitterrand
    epsilons = [0.4, 0.2, 0.1, 0.05, 0.025, 0.0125]
    fehler_betrag, fehler_kasten = [], []
    for eps in epsilons:
        gb = glaetten(betrag, x, eps)
        gk = glaetten(kasten, x, eps)
        fehler_betrag.append(np.max(np.abs(gb - betrag)[innen]))
        fehler_kasten.append(np.sum(np.abs(gk - kasten)[innen]) * dx)
        ort = x[innen][np.argmax(np.abs(gb - betrag)[innen])]
        traeger = x[gk > 0]
        print(f"ε = {eps:6.4f}: max|u_ε − |x|| = {fehler_betrag[-1]:.5f} bei x = {ort:+.4f} (ε·m1 = {eps * m1:.5f});  "
              f"L1-Fehler Kasten {fehler_kasten[-1]:.5f} (2ε·m1 = {2 * eps * m1:.5f});  Träger [{traeger.min():.4f}, {traeger.max():.4f}]")
    print("(Der numerische Träger ist etwas kleiner als [−1 − ε, 1 + ε], weil e^(−1/(1−z²)) nahe |z| = 1 unter die kleinste "
          "darstellbare Zahl fällt.)")

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    for eps in [0.4, 0.1, 0.025]:
        axes[0, 0].plot(x, glaetten(betrag, x, eps), label=f"ε = {eps}")
        axes[0, 1].plot(x, glaetten(kasten, x, eps), label=f"ε = {eps}")
    axes[0, 0].plot(x, betrag, "k--", lw=1, label="|x|")
    axes[0, 0].set_xlim(-0.8, 0.8)
    axes[0, 0].set_ylim(-0.02, 0.8)
    axes[0, 0].set_xlabel("x")
    axes[0, 0].set_ylabel("Wert")
    axes[0, 0].set_title("Geglättetes |x|: nur in (−ε, ε) verändert")
    axes[0, 0].legend(fontsize=8)
    axes[0, 1].plot(x, kasten, "k--", lw=1, label="Kasten")
    axes[0, 1].set_xlim(-1.8, 1.8)
    axes[0, 1].set_xlabel("x")
    axes[0, 1].set_ylabel("Wert")
    axes[0, 1].set_title("Geglätteter Kasten: Träger [−1 − ε, 1 + ε]")
    axes[0, 1].legend(fontsize=8)
    axes[1, 0].plot(x, weier, color="0.7", lw=0.6, label="W(x)")
    for eps in [0.05, 0.01]:
        axes[1, 0].plot(x, glaetten(weier, x, eps), label=f"W ∗ φ_ε, ε = {eps}")
    axes[1, 0].set_xlim(-1, 1)
    axes[1, 0].set_xlabel("x")
    axes[1, 0].set_ylabel("Wert")
    axes[1, 0].set_title("Weierstraß-artige Funktion und ihre Glättungen")
    axes[1, 0].legend(fontsize=8)
    e_ = np.array(epsilons)
    axes[1, 1].loglog(e_, fehler_betrag, "o", label="max-Fehler für |x|")
    axes[1, 1].loglog(e_, fehler_kasten, "s", label="L1-Fehler für den Kasten")
    axes[1, 1].loglog(e_, m1 * e_, "k-", lw=1, label="ε·m1")
    axes[1, 1].loglog(e_, 2 * m1 * e_, "k--", lw=1, label="2ε·m1")
    axes[1, 1].set_xlabel("ε")
    axes[1, 1].set_ylabel("Fehler")
    axes[1, 1].set_title("Fehler proportional zu ε")
    axes[1, 1].legend(fontsize=8)
    plt.tight_layout()
    plt.show()


def distributions():
    """52. Distributionen: schwache Ableitungen, $\\delta$ als Grenzwert, Sokhotski–Plemelj (Zellen 17 von testfunctions.ipynb)."""
    global _, a, av, axes, b, bv, c, cv, d, delta_fehler, dphi, dphi_np
    global e, eps_liste, eps_sp, fig, g, hauptwert, hi, im_sp, lo, m2, norm_phi, opt
    global phi, phi_np, phi_sym, r, re_sp, rv, testfunktion, tests, w1, w2, w3, w4
    global xp, xv
    xv, cv, rv, av, bv = sp.symbols("x c r a b", real=True)
    phi_sym = sp.exp(-1 / (1 - ((xv - cv) / rv) ** 2)) * (1 + av * xv + bv * xv ** 2)
    phi_np = sp.lambdify((xv, cv, rv, av, bv), phi_sym, "math")
    dphi_np = sp.lambdify((xv, cv, rv, av, bv), sp.diff(phi_sym, xv), "math")


    def testfunktion(c, r, a, b):
        """Ψ((x − c)/r)·(1 + a x + b x²) und ihre Ableitung, außerhalb des Trägers 0 (skalare Funktionen für quad)."""
        phi = lambda x: phi_np(x, c, r, a, b) if abs(x - c) < r else 0.0
        dphi = lambda x: dphi_np(x, c, r, a, b) if abs(x - c) < r else 0.0
        return phi, dphi


    opt = dict(points=[0.0], limit=200, epsabs=1e-13, epsrel=1e-12)
    print("                      −∫Hφ'        φ(0)      −∫|x|φ'    ∫sign·φ    −∫sign·φ'     2φ(0)")
    tests = []
    for _ in range(4):
        c, r, a, b = rng.uniform(-0.5, 0.5), rng.uniform(0.8, 2.0), rng.uniform(-1, 1), rng.uniform(-1, 1)
        phi, dphi = testfunktion(c, r, a, b)
        tests.append((c, r, phi))
        lo, hi = c - r, c + r
        w1 = -quad(lambda x: (x > 0) * dphi(x), lo, hi, **opt)[0]
        w2 = -quad(lambda x: abs(x) * dphi(x), lo, hi, **opt)[0]
        w3 = quad(lambda x: np.sign(x) * phi(x), lo, hi, **opt)[0]
        w4 = -quad(lambda x: np.sign(x) * dphi(x), lo, hi, **opt)[0]
        print(f"c = {c:+.2f}, r = {r:.2f}:  {w1:10.7f} {phi(0.0):10.7f}   {w2:10.7f} {w3:10.7f}   {w4:10.7f} {2 * phi(0.0):10.7f}")

    m2 = quad(lambda z: z * z * math.exp(-1 / (1 - z * z)), -1, 1, epsabs=1e-14)[0] / PSI_INTEGRAL
    norm_phi = math.sqrt(quad(lambda z: (math.exp(-1 / (1 - z * z)) / PSI_INTEGRAL) ** 2, -1, 1)[0])
    g = lambda x: math.cos(x) + x ** 3                      # g(0) = 1, g''(0) = −1
    eps_liste = np.array([0.5, 0.2, 0.1, 0.05, 0.02, 0.01])
    delta_fehler = np.array([quad(lambda x: float(phi_eps(x, e)) * g(x), -e, e, epsabs=1e-15, epsrel=1e-13)[0] - 1
                             for e in eps_liste])
    print(f"\n⟨φ_ε, g⟩ − g(0) mit g = cos x + x³ (Vorhersage −ε²m2/2, m2 = {m2:.5f}):")
    for e, d in zip(eps_liste, delta_fehler):
        print(f"  ε = {e:5.2f}: {d:+.3e}   Vorhersage {-e * e * m2 / 2:+.3e}   Norm ‖φ_ε‖₂ = {norm_phi / math.sqrt(e):7.3f}")

    c, r, phi = tests[0]
    hauptwert = quad(phi, c - r, c + r, weight="cauchy", wvar=0.0)[0]
    eps_sp = np.logspace(0, -4, 13)
    re_sp = np.array([quad(lambda x: phi(x) * x / (x * x + e * e), c - r, c + r, points=[0.0], limit=400)[0] for e in eps_sp])
    im_sp = np.array([-quad(lambda x: phi(x) * e / (x * x + e * e), c - r, c + r, points=[0.0], limit=400)[0] for e in eps_sp])
    print(f"\nSokhotski–Plemelj für die erste Testfunktion: Re → P∫φ/x = {hauptwert:.6f}, Im → −πφ(0) = {-np.pi * phi(0.0):.6f}")
    print(f"  bei ε = 1e−4: Re = {re_sp[-1]:.6f}, Im = {im_sp[-1]:.6f}")

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.5))
    xp = np.linspace(-0.6, 0.6, 2001)
    for e in [0.5, 0.2, 0.1, 0.05]:
        axes[0].plot(xp, phi_eps(xp, e), label=f"φ_ε, ε = {e}")
    axes[0].set_xlabel("x")
    axes[0].set_ylabel("φ_ε(x)")
    axes[0].set_title("Eine Folge von Testfunktionen mit Grenzwert δ")
    axes[0].legend(fontsize=8)
    axes[1].loglog(eps_liste, np.abs(delta_fehler), "o", label="|⟨φ_ε, g⟩ − g(0)|")
    axes[1].loglog(eps_liste, eps_liste ** 2 * m2 / 2, "k-", lw=1, label="ε²·m2/2")
    axes[1].set_xlabel("ε")
    axes[1].set_ylabel("Abweichung")
    axes[1].set_title("Konvergenz gegen δ: Fehler ∝ ε²")
    axes[1].legend(fontsize=8)
    axes[2].semilogx(eps_sp, re_sp, "o-", label="Re ∫φ/(x + iε)")
    axes[2].semilogx(eps_sp, im_sp, "s-", label="Im ∫φ/(x + iε)")
    axes[2].axhline(hauptwert, color="C0", ls="--", lw=1, label="P∫φ/x")
    axes[2].axhline(-np.pi * phi(0.0), color="C1", ls="--", lw=1, label="−πφ(0)")
    axes[2].set_xlabel("ε")
    axes[2].set_ylabel("Wert")
    axes[2].set_title("Sokhotski–Plemelj: 1/(x + i0) = P(1/x) − iπδ")
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()


def weak_solution():
    """53. Eine schwache Lösung der Wellengleichung (Zellen 20 von testfunctions.ipynb)."""
    global F_dreieck, T, Tb, X, Xb, _, axes, bild, box_phi, bump2, c, ergebnisse
    global fig, grenze, gt, gx, integrand, ist, kreis, lim, marker, phi2, r, r_
    global schwacher_test, skala, t0, t0_, tt_, vor, vorhersage, wert, x0, x0_, xx_
    xx_, tt_, x0_, t0_, r_ = sp.symbols("x t x0 t0 r", real=True)
    phi2 = sp.exp(-1 / (1 - ((xx_ - x0_) ** 2 + (tt_ - t0_) ** 2) / r_ ** 2))        # Bump-Funktion in (x, t)
    box_phi = sp.lambdify((xx_, tt_, x0_, t0_, r_), sp.diff(phi2, tt_, 2) - sp.diff(phi2, xx_, 2), "numpy")
    F_dreieck = lambda xi: np.maximum(0.0, 1 - np.abs(xi))


    def bump2(X, T, x0, t0, r):
        rho2 = ((X - x0) ** 2 + (T - t0) ** 2) / r ** 2
        return np.where(rho2 < 1, np.exp(-1 / np.where(rho2 < 1, 1 - rho2, 1.0)), 0.0)


    def schwacher_test(c, x0, t0, r, n=1601):
        """⟨u, □φ⟩ für u = F(x − ct) und die Bump-Funktion um (x0, t0) mit Radius r, dazu der theoretische Wert."""
        gx, gt = np.linspace(x0 - r, x0 + r, n), np.linspace(t0 - r, t0 + r, n)
        X, T = np.meshgrid(gx, gt, indexing="ij")
        B = np.zeros_like(X)
        m = ((X - x0) ** 2 + (T - t0) ** 2) < r ** 2 * (1 - 1e-3)
        with np.errstate(all="ignore"):
            B[m] = box_phi(X[m], T[m], x0, t0, r)
        integrand = F_dreieck(X - c * T) * B
        h = (gx[1] - gx[0]) * (gt[1] - gt[0])
        ts = np.linspace(t0 - r, t0 + r, 20001)
        linien = bump2(c * ts - 1, ts, x0, t0, r) - 2 * bump2(c * ts, ts, x0, t0, r) + bump2(c * ts + 1, ts, x0, t0, r)
        return np.sum(integrand) * h, (c ** 2 - 1) * trapezoid(linien, ts), np.sum(np.abs(integrand)) * h, (X, T, integrand)


    ergebnisse = {1.0: [], 2.0: []}
    for c in [1.0, 2.0]:
        for _ in range(5):
            t0, r = rng.uniform(0.5, 1.5), rng.uniform(0.8, 1.5)
            x0 = c * t0 + rng.uniform(-0.6, 0.6)
            wert, vorhersage, skala, bild = schwacher_test(c, x0, t0, r)
            vorhersage += 0.0                                   # −0.0 als +0.0 anzeigen
            ergebnisse[c].append((x0, t0, r, wert, vorhersage, skala, bild))
            print(f"c = {c:.0f}: φ um ({x0:+.2f}, {t0:.2f}), r = {r:.2f}:  ⟨u, □φ⟩ = {wert:+.3e}   Vorhersage {vorhersage:+.3e}   "
                  f"(Größe ∫|u □φ| = {skala:.3f})")

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.8))
    gx, gt = np.linspace(-1.5, 4.0, 550), np.linspace(-0.7, 2.8, 350)
    X, T = np.meshgrid(gx, gt)
    axes[0].imshow(F_dreieck(X - T), extent=[gx[0], gx[-1], gt[0], gt[-1]], origin="lower", aspect="equal", cmap="Blues")
    kreis = np.linspace(0, 2 * np.pi, 200)
    for x0, t0, r, *_ in ergebnisse[1.0]:
        axes[0].plot(x0 + r * np.cos(kreis), t0 + r * np.sin(kreis), "r", lw=1)
    axes[0].set_xlabel("Ort x")
    axes[0].set_ylabel("Zeit t")
    axes[0].set_title("u = F(x − t) und die Träger der Testfunktionen")
    Xb, Tb, integrand = ergebnisse[1.0][0][6]
    grenze = np.max(np.abs(integrand))
    bild = axes[1].imshow(integrand.T, extent=[Xb.min(), Xb.max(), Tb.min(), Tb.max()], origin="lower", aspect="auto",
                          cmap="RdBu_r", vmin=-grenze, vmax=grenze)
    axes[1].set_aspect("equal")
    plt.colorbar(bild, ax=axes[1], label="u · □φ")
    axes[1].set_xlabel("Ort x")
    axes[1].set_ylabel("Zeit t")
    axes[1].set_title("Integrand u·□φ: positive und negative Teile heben sich auf")
    for c, marker in [(1.0, "o"), (2.0, "s")]:
        vor = [e[4] for e in ergebnisse[c]]
        ist = [e[3] for e in ergebnisse[c]]
        axes[2].plot(vor, ist, marker, ms=8, label=f"c = {c:.0f}")
    lim = 1.1 * max(abs(e[4]) for e in ergebnisse[2.0])
    axes[2].plot([-lim, lim], [-lim, lim], "k--", lw=1, label="Gerade ist = Vorhersage")
    axes[2].set_xlabel("Vorhersage (c² − 1)·∫[φ(ct−1, t) − 2φ(ct, t) + φ(ct+1, t)] dt")
    axes[2].set_ylabel("numerisch ⟨u, □φ⟩")
    axes[2].set_title("Schwache Lösung nur für c = 1")
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()


def fourier_decay():
    """54. Fourier-Abfall: von $1/k$ bis $e^{-\\sqrt k}$ (Zellen 23 von testfunctions.ipynb)."""
    global F, Psi_hat, _, abw, axes, fig, formeln, gauss_num, gut, huelle, j, k
    global k_fft, kk, m, name, p, profil, psi_hat_fft, psi_hat_sattel, s
    def psi_hat_fft(dx=1e-3, M=2 ** 21):
        """Ψ̂(k) = ∫Ψ(x) e^(−ikx) dx auf dem Gitter k_j = 2πj/(M dx) mit einer FFT; die Trapezregel ist für glatte
    Funktionen mit kompaktem Träger bis auf Rundungsfehler exakt."""
        xs = np.arange(-1, 1 + dx / 2, dx)
        a = np.zeros(M)
        a[:xs.size] = bump(xs)
        k = 2 * np.pi * np.arange(M) / (M * dx)
        return k, (dx * np.exp(1j * k) * np.fft.fft(a)).real       # Phasenfaktor, weil das Gitter bei x = −1 beginnt


    def psi_hat_sattel(k):
        k = np.asarray(k, dtype=float)
        return 2 * np.sqrt(2 * np.pi) * np.exp(-0.25) * (2 * k) ** -0.75 * np.exp(-np.sqrt(k)) * np.cos(k - np.sqrt(k) - 3 * np.pi / 8)


    formeln = {
        "Rechteck (Sprung)": (lambda k: 2 * np.sin(k) / k, lambda x: 1.0),
        "Dreieck (Knick)": (lambda k: 4 * np.sin(k / 2) ** 2 / k ** 2, lambda x: 1 - abs(x)),
        "Hann cos²(πx/2)": (lambda k: np.pi ** 2 * np.sin(k) / (k * (np.pi ** 2 - k ** 2)), lambda x: math.cos(math.pi * x / 2) ** 2),
    }
    for name, (F, profil) in formeln.items():
        abw = max(abs(quad(profil, -1, 1, weight="cos", wvar=kk)[0] - F(kk)) for kk in [0.7, 3.7, 25.0, 140.0])
        print(f"{name:18s}: geschlossene Formel gegen numerisches Integral, größte Abweichung {abw:.1e}")
    gauss_num = 2 * quad(lambda x: math.exp(-x * x), 0, np.inf, weight="cos", wvar=3.0)[0]
    print(f"Gauß e^(−x²)       : bei k = 3 numerisch {gauss_num:.10f}, Formel {np.sqrt(np.pi) * np.exp(-9 / 4):.10f}")

    k_fft, Psi_hat = psi_hat_fft()
    print(f"Kontrolle: Ψ̂(0) = {Psi_hat[0]:.8f} = ∫Ψ = {PSI_INTEGRAL:.8f}")
    print("\n   k    Ψ̂(k) numerisch   Sattelpunkt     Verhältnis   Rechteck-Hülle 2/k")
    for kk in [25, 50, 100, 200, 400, 700]:
        j = np.argmin(np.abs(k_fft - kk))
        print(f"{k_fft[j]:6.1f}  {Psi_hat[j]:+.4e}   {psi_hat_sattel(k_fft[j]):+.4e}   {Psi_hat[j] / psi_hat_sattel(k_fft[j]):8.4f}     {2 / k_fft[j]:.1e}")

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.8))
    k = np.logspace(0, 3, 4000)
    for name, (F, _) in formeln.items():
        axes[0].loglog(k, np.abs(F(k)), lw=0.8, label=name)
    axes[0].loglog(k, np.sqrt(np.pi) * np.exp(-k ** 2 / 4), lw=1.5, label="Gauß e^(−x²)")
    m = (k_fft > 1) & (k_fft < 1000)
    axes[0].loglog(k_fft[m][::5], np.abs(Psi_hat[m][::5]), "k", lw=0.8, label="Bump Ψ")
    for p, s in [(1, 2), (2, 4), (3, np.pi ** 2)]:
        axes[0].loglog(k, s / k ** p, "k:", lw=0.8)
    axes[0].set_ylim(1e-16, 3)
    axes[0].set_xlabel("Wellenzahl k")
    axes[0].set_ylabel("|φ̂(k)|")
    axes[0].set_title("Fourier-Abfall; gepunktet: 2/k, 4/k², π²/k³")
    axes[0].legend(fontsize=7, loc="lower left")
    m = (k_fft > 5) & (k_fft < 700)
    axes[1].semilogy(k_fft[m], np.abs(Psi_hat[m]), "k", lw=0.8, label="|Ψ̂(k)| numerisch (FFT)")
    axes[1].semilogy(k_fft[m], np.abs(psi_hat_sattel(k_fft[m])), "C3--", lw=0.8, label="Sattelpunkt-Formel")
    axes[1].semilogy(k_fft[m], 2 * np.sqrt(2 * np.pi) * np.exp(-0.25) * (2 * k_fft[m]) ** -0.75 * np.exp(-np.sqrt(k_fft[m])),
                     "C0", lw=1.5, label="Hülle 2√(2π) e^(−1/4) (2k)^(−3/4) e^(−√k)")
    axes[1].set_xlabel("Wellenzahl k")
    axes[1].set_ylabel("|Ψ̂(k)|")
    axes[1].set_title("Bump-Funktion: Abfall wie e^(−√k)")
    axes[1].legend(fontsize=8)
    huelle = 2 * np.sqrt(2 * np.pi) * np.exp(-0.25) * (2 * k_fft[m]) ** -0.75 * np.exp(-np.sqrt(k_fft[m]))
    gut = np.abs(np.cos(k_fft[m] - np.sqrt(k_fft[m]) - 3 * np.pi / 8)) > 0.5
    axes[2].plot(np.sqrt(k_fft[m][gut]), Psi_hat[m][gut] / psi_hat_sattel(k_fft[m][gut]), ".", ms=2)
    axes[2].axhline(1, color="k", lw=1)
    axes[2].set_ylim(0.8, 1.2)
    axes[2].set_xlabel("√k")
    axes[2].set_ylabel("numerisch / Sattelpunkt")
    axes[2].set_title("Verhältnis geht gegen 1 (wo |cos| > 0.5)")
    plt.tight_layout()
    plt.show()


def gallery():
    """55. Galerie: zwölf klassische Benchmark-Funktionen (Zellen 26 von testfunctions.ipynb)."""
    global X, Y, Z, _, ax, axes, beste, bester, bild, bildausschnitt, f, farbe
    global fig, fmin, g_schw, gebiet, grad, gradient_num, gx, gy, kandidaten, lokal, minima, name
    global p, reihe, skala, t, v, werte
    def gradient_num(f, p, h):
        p = np.asarray(p, dtype=float)
        return np.array([(f(p + h * e) - f(p - h * e)) / (2 * h) for e in np.eye(2)])


    print(f"{'Funktion':16s} {'Tabelle f*':>12s} {'f(x*)':>12s} {'|∇f(x*)|':>10s} {'beste Suche':>12s}   gefunden bei")
    for name, (f, gebiet, _, minima, fmin) in GALERIE.items():
        skala = gebiet[0][1] - gebiet[0][0]
        werte = [f(np.array(p, dtype=float)) for p in minima]
        grad = max(np.linalg.norm(gradient_num(f, p, 1e-6 * skala)) for p in minima)
        gx = np.linspace(*gebiet[0], 801)
        gy = np.linspace(*gebiet[1], 801)
        X, Y = np.meshgrid(gx, gy)
        Z = f(np.array([X, Y]))
        beste = np.argsort(Z.ravel())[:20]
        kandidaten = [minimize(f, [X.ravel()[i], Y.ravel()[i]], method="L-BFGS-B", bounds=gebiet,
                               options=dict(ftol=1e-15, gtol=1e-12)) for i in beste]
        bester = min(kandidaten, key=lambda r: r.fun)
        print(f"{name:16s} {fmin:12.5f} {min(werte):12.5f} {grad:10.1e} {bester.fun:12.5f}   ({bester.x[0]:.4f}, {bester.x[1]:.4f})")

    g_schw = lambda t: -t * np.sin(np.sqrt(np.abs(t)))         # Schwefel in einer Koordinate (ohne Konstante)
    t = np.linspace(-500, 500, 2000001)
    v = g_schw(t)
    lokal = np.where((v[1:-1] < v[:-2]) & (v[1:-1] < v[2:]))[0] + 1
    reihe = lokal[np.argsort(v[lokal])][:3]
    print("\nSchwefel, eine Koordinate: die drei tiefsten lokalen Minima bei x =",
          ", ".join(f"{t[i]:.2f} (Wert {v[i]:.2f})" for i in reihe))

    fig, axes = plt.subplots(3, 4, figsize=(18, 13))
    for ax, (name, (f, gebiet, bildausschnitt, minima, fmin)) in zip(axes.flat, GALERIE.items()):
        gx = np.linspace(*bildausschnitt[0], 400)
        gy = np.linspace(*bildausschnitt[1], 400)
        X, Y = np.meshgrid(gx, gy)
        Z = f(np.array([X, Y]))
        farbe = np.log10(1 + Z - Z.min())
        bild = ax.imshow(farbe, extent=[gx[0], gx[-1], gy[0], gy[-1]], origin="lower", aspect="auto", cmap="viridis")
        ax.contour(X, Y, farbe, levels=12, colors="white", linewidths=0.4)
        for p in minima:
            if bildausschnitt[0][0] <= p[0] <= bildausschnitt[0][1] and bildausschnitt[1][0] <= p[1] <= bildausschnitt[1][1]:
                ax.plot(*p, "r*", ms=13, mec="white")
        ax.set_title(f"{name}: f* = {fmin:g}", fontsize=10)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        plt.colorbar(bild, ax=ax, label="log10(1 + f − min)")
    plt.tight_layout()
    plt.show()


def gallery_contours():
    """56. Galerie: zwölf klassische Benchmark-Funktionen (Zellen 29 von testfunctions.ipynb)."""
    global Z, _, ausschnitt, ax, blick, f, f_stern, f_tal, fig, flaeche_3d, k, minima
    global name
    def flaeche_3d(ax, f, ausschnitt, f_stern, n=200, blick=(50, -30), farbbalken=True, schrift=10, log=True):
        """f(x, y) als Fläche über dem Ausschnitt; Farbe nach f − f* (blau = nahe am Minimum), logarithmisch ab
    10⁻⁴ der Spannweite, damit flache Mulden als Flecken sichtbar sind, oder linear (log=False)."""
        gx = np.linspace(*ausschnitt[0], n)
        gy = np.linspace(*ausschnitt[1], n)
        X, Y = np.meshgrid(gx, gy)
        Z = f(np.array([X, Y]))
        abstand = Z - min(f_stern, Z.min())
        norm = LogNorm(vmin=1e-4 * abstand.max(), vmax=abstand.max(), clip=True) if log else Normalize(0, abstand.max())
        ax.plot_surface(X, Y, Z, facecolors=plt.cm.jet(norm(abstand)), rstride=1, cstride=1, linewidth=0,
                        antialiased=False, shade=False)
        ax.view_init(elev=blick[0], azim=blick[1])
        ax.set_xlabel("x", fontsize=schrift)
        ax.set_ylabel("y", fontsize=schrift)
        ax.set_zlabel("f(x, y)", fontsize=schrift)
        if farbbalken:
            skala = plt.cm.ScalarMappable(norm=norm, cmap="jet")
            plt.colorbar(skala, ax=ax, shrink=0.55, pad=0.1, label="f − f*" + (" (logarithmisch)" if log else ""))
        return Z


    fig = plt.figure(figsize=(18, 8))
    for k, (name, blick) in enumerate([("Himmelblau", (50, -30)), ("Rosenbrock", (35, -120))]):
        f, _, ausschnitt, minima, f_stern = GALERIE[name]
        ax = fig.add_subplot(1, 2, k + 1, projection="3d")
        Z = flaeche_3d(ax, f, ausschnitt, f_stern, n=250, blick=blick)
        ax.set_title(f"{name}: f zwischen {Z.min():.2g} und {Z.max():.0f}, Minimum f* = {f_stern:g}")
    plt.tight_layout()
    plt.show()

    f_tal = lambda x: rosenbrock(np.array([x, x ** 2]))
    print("Rosenbrock entlang der Talsohle y = x²: f(−1, 1) = {:.0f}, f(0, 0) = {:.0f}, f(0.5, 0.25) = {:.2f}, f(1, 1) = {:.0f}"
          .format(f_tal(-1.0), f_tal(0.0), f_tal(0.5), f_tal(1.0)))
    print("Rosenbrock quer zum Tal, 0.5 neben der Sohle: f(0.5, 0.75) = {:.1f}".format(rosenbrock(np.array([0.5, 0.75]))))


def gallery_landscapes():
    """57. Galerie: zwölf klassische Benchmark-Funktionen (Zellen 32 von testfunctions.ipynb)."""
    global _, ausschnitt, ax, blicke, f, f_stern, fig, k, linear, minima, name
    linear = {"Rastrigin", "Ackley", "Easom", "Schwefel", "Eggholder"}
    blicke = {"Rosenbrock": (35, -120), "Beale": (40, -50), "Goldstein–Price": (35, -50), "Easom": (70, -30), "Eggholder": (40, -120)}
    fig = plt.figure(figsize=(20, 15))
    for k, (name, (f, _, ausschnitt, minima, f_stern)) in enumerate(GALERIE.items()):
        ax = fig.add_subplot(3, 4, k + 1, projection="3d")
        flaeche_3d(ax, f, ausschnitt, f_stern, n=120, blick=blicke.get(name, (50, -30)), farbbalken=False, schrift=8,
                   log=name not in linear)
        ax.set_title(f"{name}: f* = {f_stern:g}" + (" (Farbe linear)" if name in linear else ""), fontsize=11)
        ax.tick_params(labelsize=7)
    fig.suptitle("Die zwölf Benchmark-Funktionen als Flächen; Farbe nach f − f* (blau = nahe am Minimum, rot = weit darüber)", fontsize=13)
    plt.tight_layout(rect=(0, 0, 1, 0.96))
    plt.show()


def himmelblau_minima():
    """58. Himmelblau: vier Minima, neun kritische Punkte, zwei Arten von Einzugsgebieten (Zellen 35 von testfunctions.ipynb)."""
    global X0, Y0, Z, _, abstand, anz, ax, axes, becken_gd, cmap_gd, det, ev
    global f_sym, farben_alle, farben_min, fig, fx, fy, g, grad_h, gx_, gy_, hesse, hxx
    global hxy, hyy, idx, kritisch, minima_h, n, pp, punkte, resultante, symbol, t, typ
    global typen, w, wurzeln, x, x0, xs_, y, y0, ys_, ziel_nt
    xs_, ys_ = sp.symbols("x y", real=True)
    f_sym = (xs_ ** 2 + ys_ - 11) ** 2 + (xs_ + ys_ ** 2 - 7) ** 2
    fx, fy = sp.diff(f_sym, xs_), sp.diff(f_sym, ys_)
    print("Faktorisierung:", sp.factor(sp.expand(xs_ + (11 - xs_ ** 2) ** 2 - 7)))
    resultante = sp.Poly(sp.resultant(fx, fy, ys_), xs_)
    wurzeln = [complex(w) for w in resultante.nroots(n=30)]
    print(f"Resultante von f_x und f_y bezüglich y: Grad {resultante.degree()}, reelle Nullstellen: "
          f"{sum(abs(w.imag) < 1e-12 for w in wurzeln)}")

    hesse = sp.lambdify((xs_, ys_), sp.hessian(f_sym, (xs_, ys_)), "numpy")
    kritisch = []
    for w in wurzeln:
        x0 = w.real
        for y0 in sp.Poly(fx.subs(xs_, x0), ys_).nroots(n=30):
            y0 = complex(y0)
            if abs(y0.imag) < 1e-10 and abs(float(fy.subs({xs_: x0, ys_: y0.real}))) < 1e-6:
                ev = np.linalg.eigvalsh(np.array(hesse(x0, y0.real), dtype=float))
                typ = "Minimum" if ev.min() > 0 else ("Maximum" if ev.max() < 0 else "Sattel")
                kritisch.append((x0, y0.real, typ))
    kritisch.sort(key=lambda k: ("Minimum", "Sattel", "Maximum").index(k[2]))
    print(f"\n{'x':>10s} {'y':>10s} {'f':>11s}   Typ")
    for x0, y0, typ in kritisch:
        print(f"{x0:10.6f} {y0:10.6f} {himmelblau((x0, y0)):11.6f}   {typ}")
    anz = {t: sum(k[2] == t for k in kritisch) for t in ("Minimum", "Sattel", "Maximum")}
    print(f"Poincaré–Hopf: #Min − #Sattel + #Max = {anz['Minimum']} − {anz['Sattel']} + {anz['Maximum']} = "
          f"{anz['Minimum'] - anz['Sattel'] + anz['Maximum']}")


    def grad_h(x, y):
        a, b = x ** 2 + y - 11, x + y ** 2 - 7
        return 4 * x * a + 2 * b, 2 * a + 4 * y * b


    n = 300
    g = np.linspace(-5, 5, n)
    X0, Y0 = np.meshgrid(g, g)
    punkte = np.array([[k[0], k[1]] for k in kritisch])
    minima_h = punkte[:4]

    # Gradientenabstieg mit kleinem Schritt (≈ Gradientenfluss)
    x, y = X0.copy(), Y0.copy()
    for _ in range(3000):
        gx_, gy_ = grad_h(x, y)
        x, y = x - 0.004 * gx_, y - 0.004 * gy_
    abstand = np.hypot(x[..., None] - minima_h[:, 0], y[..., None] - minima_h[:, 1])
    becken_gd = np.where(abstand.min(axis=-1) < 1e-3, abstand.argmin(axis=-1), -1)

    # Newton für ∇f = 0
    x, y = X0.copy(), Y0.copy()
    with np.errstate(all="ignore"):
        for _ in range(60):
            gx_, gy_ = grad_h(x, y)
            hxx, hyy, hxy = 12 * x ** 2 + 4 * y - 42, 12 * y ** 2 + 4 * x - 26, 4 * x + 4 * y
            det = hxx * hyy - hxy ** 2
            x, y = x - (hyy * gx_ - hxy * gy_) / det, y - (hxx * gy_ - hxy * gx_) / det
        abstand = np.hypot(x[..., None] - punkte[:, 0], y[..., None] - punkte[:, 1])
        ziel_nt = np.where(np.nan_to_num(abstand.min(axis=-1), nan=1e9) < 1e-6, abstand.argmin(axis=-1), -1)
    print("\nGradientenabstieg: Anteile der vier Minima:", ", ".join(f"{np.mean(becken_gd == i):.3f}" for i in range(4)),
          f"| nicht entschieden: {np.mean(becken_gd == -1):.4f}")
    typen = np.array([k[2] for k in kritisch])
    for t in ("Minimum", "Sattel", "Maximum"):
        idx = np.where(typen == t)[0]
        print(f"Newton endet in einem {t:8s}: {np.mean(np.isin(ziel_nt, idx)):.3f}")
    print(f"Newton ohne Konvergenz in 60 Schritten: {np.mean(ziel_nt == -1):.4f}")

    farben_min = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.6))
    Z = himmelblau(np.array([X0, Y0]))
    axes[0].contourf(X0, Y0, np.log10(1 + Z), levels=30, cmap="viridis")
    symbol = {"Minimum": "o", "Sattel": "X", "Maximum": "^"}
    for t in ("Minimum", "Sattel", "Maximum"):
        pp = punkte[typen == t]
        axes[0].plot(pp[:, 0], pp[:, 1], symbol[t], color="w", mec="k", ms=10, ls="none", label=f"{t} ({len(pp)})")
    axes[0].set_title("Himmelblau: log10(1 + f) und kritische Punkte")
    axes[0].legend(fontsize=8, loc="lower left")
    cmap_gd = ListedColormap(["0.85"] + farben_min)
    axes[1].imshow(becken_gd + 1, extent=[-5, 5, -5, 5], origin="lower", cmap=cmap_gd, vmin=0, vmax=4)
    axes[1].plot(punkte[typen == "Sattel"][:, 0], punkte[typen == "Sattel"][:, 1], "kX", ms=9, label="Sattel")
    axes[1].plot(minima_h[:, 0], minima_h[:, 1], "wo", mec="k", ms=9, label="Minimum")
    axes[1].set_title("Einzugsgebiete des Gradientenabstiegs")
    axes[1].legend(fontsize=8, loc="lower left")
    farben_alle = ["0.15"] + farben_min + ["#bbbbbb", "#999999", "#777777", "#555555", "#ffffff"]
    axes[2].imshow(ziel_nt + 1, extent=[-5, 5, -5, 5], origin="lower", cmap=ListedColormap(farben_alle), vmin=0, vmax=9,
                   interpolation="nearest")
    axes[2].plot(punkte[:, 0], punkte[:, 1], "k.", ms=6)
    axes[2].set_title("Newton für ∇f = 0: farbig Minima, grau Sattel, weiß Maximum")
    for ax in axes:
        ax.set_xlabel("x")
        ax.set_ylabel("y")
    plt.tight_layout()
    plt.show()


def rosenbrock_valley():
    """59. Rosenbrock: das gekrümmte Tal (Zellen 38 von testfunctions.ipynb)."""
    global X, Y, abst, adam, axes, eigene, ev, f_rb, farbe9, fig, g_rb, gd
    global gx, gy, h_rb, heavy_ball, kw, laeufe, methode, name, newton, r, schritt, schritte
    global status, tol, weg, x_start, x_stern, zaehler
    def f_rb(z):
        return rosenbrock(z)

    def g_rb(z):
        x, y = z
        return np.array([-2 * (1 - x) - 400 * x * (y - x ** 2), 200 * (y - x ** 2)])

    def h_rb(z):
        x, y = z
        return np.array([[2 - 400 * (y - x ** 2) + 800 * x ** 2, -400 * x], [-400 * x, 200]])


    ev = np.linalg.eigvalsh(h_rb([1, 1]))
    print(f"Hesse-Matrix bei (1, 1): Eigenwerte {ev[1]:.2f} und {ev[0]:.4f}, Kondition {ev[1] / ev[0]:.0f}, "
          f"Stabilitätsgrenze 2/λmax = {2 / ev[1]:.6f}")
    x_start, x_stern, tol = np.array([-1.2, 1.0]), np.array([1.0, 1.0]), 1e-6


    def eigene(schritt, max_schritte=200000):
        """Führt ein Verfahren aus; schritt(x, zustand, i) gibt (x_neu, zustand) zurück. Ergebnis: Weg und Zahl der Schritte."""
        x, zustand, weg = x_start.copy(), None, [x_start.copy()]
        for i in range(1, max_schritte + 1):
            x, zustand = schritt(x, zustand, i)
            weg.append(x.copy())
            if not np.all(np.isfinite(x)) or np.linalg.norm(x - x_stern) > 1e6:
                return np.array(weg), i, "divergiert"
            if np.linalg.norm(x - x_stern) < tol:
                return np.array(weg), i, "konvergiert"
        return np.array(weg), max_schritte, "nicht konvergiert"


    def gd(eta):
        return lambda x, z, i: (x - eta * g_rb(x), None)

    def heavy_ball(eta, beta):
        def schritt(x, v, i):
            v = beta * (np.zeros(2) if v is None else v) - eta * g_rb(x)
            return x + v, v
        return schritt

    def adam(lr, b1=0.9, b2=0.999, e=1e-8):
        def schritt(x, z, i):
            m, v = (np.zeros(2), np.zeros(2)) if z is None else z
            gr = g_rb(x)
            m, v = b1 * m + (1 - b1) * gr, b2 * v + (1 - b2) * gr ** 2
            return x - lr * (m / (1 - b1 ** i)) / (np.sqrt(v / (1 - b2 ** i)) + e), (m, v)
        return schritt

    def newton(x, z, i):
        return x - np.linalg.solve(h_rb(x), g_rb(x)), None


    laeufe = {}
    farbe9 = {"Gradient η = 0.001": "C0", "Gradient η = 0.002": "C7", "Momentum η = 0.001, β = 0.9": "C1",
              "Adam lr = 0.01": "C2", "Newton": "C3", "Nelder-Mead": "C4", "BFGS": "C5"}
    for name, schritt in [("Gradient η = 0.001", gd(0.001)), ("Gradient η = 0.002", gd(0.002)),
                          ("Momentum η = 0.001, β = 0.9", heavy_ball(0.001, 0.9)), ("Adam lr = 0.01", adam(0.01)),
                          ("Newton", newton)]:
        weg, schritte, status = eigene(schritt)
        laeufe[name] = weg
        print(f"{name:28s}: {schritte:7d} Schritte, {status}, Abstand am Ende {np.linalg.norm(weg[-1] - x_stern):.1e}")
    print(f"Vorhersage für den Gradientenabstieg mit η = 0.001: ln(1e6)/(η λmin) = {np.log(1e6) / (0.001 * ev[0]):.0f} Schritte")

    for methode, kw in [("Nelder-Mead", dict(options=dict(xatol=1e-10, fatol=1e-20, maxiter=20000))),
                        ("BFGS", dict(jac=g_rb, options=dict(gtol=1e-10)))]:
        weg = [x_start.copy()]
        zaehler = Zaehler(f_rb)
        r = minimize(zaehler, x_start, method=methode, callback=lambda xk, *a: weg.append(np.array(xk)), **kw)
        laeufe[methode] = np.array(weg)
        print(f"{methode:28s}: {r.nit:7d} Iterationen, {zaehler.n} Funktionsauswertungen"
              + (f" und {r.njev} Gradienten" if methode == "BFGS" else "") + f", Abstand am Ende {np.linalg.norm(r.x - x_stern):.1e}")

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    gx, gy = np.linspace(-1.6, 1.6, 400), np.linspace(-0.6, 1.8, 400)
    X, Y = np.meshgrid(gx, gy)
    axes[0].contourf(X, Y, np.log10(rosenbrock(np.array([X, Y])) + 1e-3), levels=30, cmap="Greys")
    for name, weg in laeufe.items():
        if name == "Gradient η = 0.002":
            continue
        axes[0].plot(weg[:, 0], weg[:, 1], "-", lw=1.2, color=farbe9[name], label=name)
    axes[0].plot(*x_start, "ko", ms=8)
    axes[0].plot(1, 1, "r*", ms=15)
    axes[0].set_xlim(-1.6, 1.6)
    axes[0].set_ylim(-0.6, 1.8)
    axes[0].set_xlabel("x")
    axes[0].set_ylabel("y")
    axes[0].set_title("Wege im Tal y ≈ x² (Newton springt erst weit weg)")
    axes[0].legend(fontsize=8, loc="lower right")
    for name, weg in laeufe.items():
        abst = np.linalg.norm(weg - x_stern, axis=1)
        axes[1].loglog(np.arange(1, len(abst) + 1), abst, lw=1.2, color=farbe9[name], label=name)
    axes[1].axhline(tol, color="k", ls=":", lw=1)
    axes[1].set_ylim(1e-12, 1e2)
    axes[1].set_xlabel("Schritt bzw. Iteration")
    axes[1].set_ylabel("Abstand ‖x − (1, 1)‖")
    axes[1].set_title("Konvergenz")
    axes[1].legend(fontsize=8, loc="lower left")
    plt.tight_layout()
    plt.show()


def many_minima():
    """60. Viele lokale Minima: Rastrigin und Ackley (Zellen 41 von testfunctions.ipynb)."""
    global S_starts, X, _, ausw, auswertungen, axes, b_rast, d, dd, erfolg, f, farbe
    global fig, g1, grenzen, multistart, p1, pname, probleme, r, seed, tabelle, verf, verfahren
    global verschieden, vname, werte, zaehler
    g1 = lambda t: 2 * t + 20 * np.pi * np.sin(2 * np.pi * t)       # Ableitung von g(t) = t² − 10 cos 2πt + 10
    b_rast = brentq(g1, 0.4, 0.6)
    p1 = 2 * b_rast / 10.24
    print(f"Rand des Einzugsgebiets von 0: b = {b_rast:.5f}, p1 = 2b/10.24 = {p1:.5f}")
    S_starts = 100000
    erfolg = {}
    for d in range(1, 6):
        X = rng.uniform(-5.12, 5.12, (S_starts, d))
        for _ in range(300):
            X -= 0.002 * g1(X)                                  # Gradientenabstieg, kleiner Schritt
        erfolg[d] = np.mean(np.all(np.abs(X) < 1e-6, axis=1))
        verschieden = np.unique(np.round(X, 4), axis=0).shape[0] if d <= 3 else None
        print(f"d = {d}: Erfolg {erfolg[d]:.2e} (Vorhersage p1^d = {p1 ** d:.2e}, {S_starts} Starts)"
              + (f"; verschiedene lokale Minima gefunden: {verschieden} (11^d = {11 ** d})" if verschieden else ""))


    def multistart(f, grenzen, seed, starts=100):
        r_ = np.random.default_rng(seed)
        lo, hi = np.array(grenzen).T
        return min((minimize(f, r_.uniform(lo, hi), method="L-BFGS-B", bounds=grenzen) for _ in range(starts)), key=lambda r: r.fun)


    verfahren = {
        "Multistart (100 × L-BFGS-B)": multistart,
        "Basin-Hopping (100 Sprünge)": lambda f, gr, s: basinhopping(
            f, np.random.default_rng(s).uniform(*np.array(gr).T), niter=100, seed=s,
            minimizer_kwargs=dict(method="L-BFGS-B", bounds=gr)),
        "Dual Annealing": lambda f, gr, s: dual_annealing(f, gr, seed=s),
        "Differential Evolution": lambda f, gr, s: differential_evolution(f, gr, seed=s, tol=1e-10, vectorized=True,
                                                                           updating="deferred"),
    }
    d = 10
    probleme = {"Rastrigin": (rastrigin, [(-5.12, 5.12)] * d), "Ackley": (ackley, [(-32.768, 32.768)] * d)}
    tabelle = {}
    print(f"\nd = {d}, je drei Läufe:")
    for pname, (f, grenzen) in probleme.items():
        for vname, verf in verfahren.items():
            werte, auswertungen = [], []
            for seed in range(3):
                zaehler = Zaehler(f)
                r = verf(zaehler, grenzen, seed)
                werte.append(float(r.fun))
                auswertungen.append(zaehler.n)
            tabelle[(pname, vname)] = (werte, auswertungen)
            print(f"  {pname:9s} {vname:28s}: beste Werte {', '.join(f'{w:8.4f}' for w in werte)};  "
                  f"Erfolge {sum(w < 1e-6 for w in werte)}/3;  Auswertungen im Mittel {np.mean(auswertungen):9.0f}")

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    dd = np.arange(1, 6)
    axes[0].semilogy(dd, [erfolg[i] if erfolg[i] > 0 else np.nan for i in dd], "o", ms=8, label="Gradientenabstieg, gemessen")
    axes[0].semilogy(dd, p1 ** dd, "k-", label="Vorhersage p1^d")
    axes[0].semilogy(dd, 1.0 / S_starts * np.ones_like(dd, dtype=float), "k:", label="Auflösung 1/Zahl der Starts")
    axes[0].set_xlabel("Dimension d")
    axes[0].set_ylabel("Erfolgswahrscheinlichkeit")
    axes[0].set_title("Rastrigin: lokale Suche aus zufälligen Starts")
    axes[0].legend(fontsize=8)
    for (pname, vname), (werte, ausw) in tabelle.items():
        farbe = f"C{list(verfahren).index(vname)}"
        axes[1].loglog(ausw, np.maximum(werte, 1e-12), "o" if pname == "Rastrigin" else "s", color=farbe, ms=8,
                       label=vname if pname == "Rastrigin" else None)
    axes[1].plot([], [], "ko", label="Rastrigin")
    axes[1].plot([], [], "ks", label="Ackley")
    axes[1].set_xlabel("Funktionsauswertungen")
    axes[1].set_ylabel("bester Wert (Untergrenze 1e−12)")
    axes[1].set_title("d = 10: globale Verfahren, je drei Läufe")
    axes[1].legend(fontsize=7)
    plt.tight_layout()
    plt.show()


def fair_comparison():
    """61. Fair vergleichen: Verschieben und Drehen (Zellen 44 von testfunctions.ipynb)."""
    global B, P, R, R2, X, Y, Z, ax, axes, breite, d, ergebnis11
    global f, fig, g2, grenzen, j, koordinatensuche, m, median, methoden, spalte, titel, varianten
    global vname, werte, z, z2
    d, B = 10, 5.12
    R = special_ortho_group.rvs(d, random_state=11)
    z = np.random.default_rng(7).uniform(-3, 3, d)
    spalte = lambda v, X: v.reshape((-1,) + (1,) * (np.ndim(X) - 1))      # Verschiebung passend zu (d,) oder (d, S)
    varianten = {
        "Standard": lambda X: rastrigin(X),
        "verschoben": lambda X: rastrigin(np.asarray(X) - spalte(z, X)),
        "gedreht": lambda X: rastrigin(np.tensordot(R, np.asarray(X), axes=1)),
        "verschoben + gedreht": lambda X: rastrigin(np.tensordot(R, np.asarray(X) - spalte(z, X), axes=1)),
    }
    grenzen = [(-B, B)] * d


    def koordinatensuche(f, durchgaenge=3, n=1025):
        x, gitter, auswertungen = np.zeros(d), np.linspace(-B, B, n), 0
        for _ in range(durchgaenge):
            for i in range(d):
                Xk = np.repeat(x[:, None], n, axis=1)
                Xk[i] = gitter
                x[i] = gitter[np.argmin(f(Xk))]
                auswertungen += n
        r = minimize(f, x, method="L-BFGS-B", bounds=grenzen)
        return r.fun, auswertungen + r.nfev


    ergebnis11 = {}
    for vname, f in varianten.items():
        werte = {"Koordinatensuche": [koordinatensuche(f)[0]],
                 "L-BFGS-B aus der Mitte": [minimize(f, np.zeros(d), method="L-BFGS-B", bounds=grenzen).fun]}
        werte["Differential Evolution"] = [differential_evolution(f, grenzen, seed=s, tol=1e-10, vectorized=True,
                                                                  updating="deferred").fun for s in range(3)]
        werte["Dual Annealing"] = [dual_annealing(f, grenzen, seed=s).fun for s in range(3)]
        ergebnis11[vname] = werte
        print(f"{vname:21s}: " + ";  ".join(f"{m} {', '.join(f'{w:.3g}' for w in ws)}" for m, ws in werte.items()))

    fig, axes = plt.subplots(1, 3, figsize=(18, 5), gridspec_kw=dict(width_ratios=[1, 1, 1.6]))
    R2 = special_ortho_group.rvs(2, random_state=3)
    z2 = np.array([1.7, -2.3])
    g2 = np.linspace(-5.12, 5.12, 400)
    X, Y = np.meshgrid(g2, g2)
    P = np.array([X, Y])
    for ax, (titel, Z) in zip(axes[:2], [("Rastrigin in 2D", rastrigin(P)),
                                         ("verschoben + gedreht", rastrigin(np.tensordot(R2, P - z2[:, None, None], axes=1)))]):
        ax.imshow(Z, extent=[-5.12, 5.12, -5.12, 5.12], origin="lower", cmap="viridis")
        ax.set_title(titel)
        ax.set_xlabel("x₁")
        ax.set_ylabel("x₂")
    axes[1].plot(*z2, "r*", ms=14)
    axes[0].plot(0, 0, "r*", ms=14)
    methoden = list(ergebnis11["Standard"])
    breite = 0.2
    for j, m in enumerate(methoden):
        median = [np.median(ergebnis11[v][m]) + 1e-3 for v in varianten]
        axes[2].bar(np.arange(len(varianten)) + (j - 1.5) * breite, median, breite, label=m)
    axes[2].set_yscale("log")
    axes[2].set_xticks(np.arange(len(varianten)))
    axes[2].set_xticklabels(list(varianten))
    axes[2].set_ylabel("bester Wert f (Median) + 0.001")
    axes[2].set_title("d = 10: Ergebnis je Variante (globales Minimum f = 0)")
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()


def windowed_phase_estimation():
    """62. Phasenschätzung mit Fenster (Zellen 47 von testfunctions.ipynb)."""
    global N, P, axes, fehler, fenster, fig, ks, m_q, name, qpe_verteilung, reihenfolge, rms
    global schwaenze, theta, vorhersage, w, xq
    def qpe_verteilung(w, theta):
        """P(y) = |(1/√N) Σ_x w_x e^(2πix(θ − y/N))|² für ein normiertes Fenster w (ein FFT-Aufruf)."""
        w = np.asarray(w, dtype=float) / np.linalg.norm(w)
        N = w.size
        A = np.fft.fft(w * np.exp(2j * np.pi * np.arange(N) * theta)) / np.sqrt(N)
        return np.abs(A) ** 2


    m_q, theta = 10, 0.2718281828
    N = 2 ** m_q
    xq = np.arange(N)
    fenster = {
        "Rechteck (Standard)": np.ones(N),
        "Sinus": np.sin(np.pi * (xq + 1) / (N + 1)),
        "Hann": np.sin(np.pi * (xq + 0.5) / N) ** 2,
        "Kaiser β = 10": np.kaiser(N, 10),
        "Bump": bump(2 * (xq + 0.5) / N - 1),
    }
    fehler = ((theta - xq / N + 0.5) % 1 - 0.5) * N          # Abstand y ↔ Nθ in Gitterpunkten, zyklisch
    ks = np.arange(1, 201)
    schwaenze = {}
    print(f"{'Fenster':20s} {'Σ P':>8s} {'RMS·N':>7s} " + " ".join(f"{'P(|Fehler|>' + str(k) + ')':>14s}" for k in [1, 5, 20, 100]))
    for name, w in fenster.items():
        P = qpe_verteilung(w, theta)
        schwaenze[name] = np.array([P[np.abs(fehler) > k].sum() for k in ks])
        rms = np.sqrt(np.sum(P * fehler ** 2))
        print(f"{name:20s} {P.sum():8.6f} {rms:7.3f} " + " ".join(f"{schwaenze[name][k - 1]:14.2e}" for k in [1, 5, 20, 100]))
    vorhersage = 2 * np.sin(np.pi * N * theta) ** 2 / (np.pi ** 2 * ks)
    print(f"Rechteck bei k = 20 und 100: gemessen {schwaenze['Rechteck (Standard)'][19]:.3e}, {schwaenze['Rechteck (Standard)'][99]:.3e};"
          f" Vorhersage 2 sin²(πNθ)/(π²k) = {vorhersage[19]:.3e}, {vorhersage[99]:.3e}")
    print(f"Kaiser-Fenster am Rand: {fenster['Kaiser β = 10'][0]:.1e} (relativ zur Mitte, nicht exakt 0)")

    fig, axes = plt.subplots(1, 3, figsize=(18, 4.8))
    for name, w in fenster.items():
        axes[0].plot(xq / N, w / np.max(w), label=name)
        P = qpe_verteilung(w, theta)
        reihenfolge = np.argsort(fehler)
        axes[1].semilogy(fehler[reihenfolge], np.maximum(P[reihenfolge], 1e-30), ".-", ms=3, lw=0.6, label=name)
        axes[2].loglog(ks, np.maximum(schwaenze[name], 1e-30), label=name)
    axes[2].loglog(ks, vorhersage, "k--", lw=1, label="2 sin²(πNθ)/(π²k)")
    axes[0].set_xlabel("x / N")
    axes[0].set_ylabel("w_x / max w")
    axes[0].set_title("Fenster im Register")
    axes[0].legend(fontsize=8)
    axes[1].set_xlim(-60, 60)
    axes[1].set_ylim(1e-25, 1)
    axes[1].set_xlabel("y − Nθ (Gitterpunkte)")
    axes[1].set_ylabel("P(y)")
    axes[1].set_title(f"Verteilung des Messergebnisses, N = {N}")
    axes[2].set_ylim(1e-25, 1)
    axes[2].set_xlabel("k (Gitterpunkte)")
    axes[2].set_ylabel("P(|y − Nθ| > k)")
    axes[2].set_title("Schwanzwahrscheinlichkeit")
    axes[2].legend(fontsize=8, loc="lower left")
    plt.tight_layout()
    plt.show()


def adiabatic_schedules():
    """63. Adiabatische Zeitpläne (Zellen 50 von testfunctions.ipynb)."""
    global P, PX, PZ, P_ad, Phi, TT, T_werte, a_gl, axes, b_gl, f_vor, fehler_adiabatisch
    global fig, glatt, gross, huelle, i, k_, linie, luecke, m_gl, name, s, sicher
    global steigung, t0_, tau, verhaeltnis, vorher, zeitplaene
    PX = np.array([[0, 1], [1, 0]], dtype=complex)
    PZ = np.diag([1.0, -1.0]).astype(complex)
    zeitplaene = {
        "linear": lambda t: t,
        "kubisch": lambda t: 3 * t ** 2 - 2 * t ** 3,
        "quintisch": lambda t: 6 * t ** 5 - 15 * t ** 4 + 10 * t ** 3,
        "glatt S(τ)": glatter_uebergang,
    }
    luecke = lambda s: 2 * np.sqrt(s ** 2 + (1 - s) ** 2)


    def fehler_adiabatisch(s, T):
        """Wahrscheinlichkeit, am Ende im angeregten Zustand |↓⟩ von −Z zu sein; gemessen wird |ψ↓|²/‖ψ‖², damit die
    Normdrift des Integrators nicht in das Ergebnis eingeht."""
        rhs = lambda t, y: -1j * ((-(1 - s(t / T)) * PX - s(t / T) * PZ) @ y)
        y = solve_ivp(rhs, (0, T), np.array([1, 1], dtype=complex) / np.sqrt(2), method="DOP853", rtol=1e-13, atol=1e-15).y[:, -1]
        return abs(y[1]) ** 2 / np.sum(np.abs(y) ** 2)


    T_werte = np.logspace(np.log10(2), np.log10(250), 44)
    t0_ = time.time()
    P_ad = {name: np.array([fehler_adiabatisch(s, T) for T in T_werte]) for name, s in zeitplaene.items()}
    print(f"Rechenzeit {time.time() - t0_:.1f} s")
    Phi = {name: quad(lambda t: luecke(float(s(t))), 0, 1, epsabs=1e-14)[0] for name, s in zeitplaene.items()}
    vorher = {
        "linear": lambda T: np.sin(T * Phi["linear"] / 2) ** 2 / (4 * T ** 2),
        "kubisch": lambda T: 2.25 * np.cos(T * Phi["kubisch"] / 2) ** 2 / T ** 4,
        "quintisch": lambda T: 56.25 * np.sin(T * Phi["quintisch"] / 2) ** 2 / T ** 6,
    }
    gross = T_werte > 50
    for name, f_vor in vorher.items():
        verhaeltnis = P_ad[name][gross] / f_vor(T_werte[gross])
        print(f"{name:10s}: Φ = {Phi[name]:.4f};  P/Vorhersage für T > 50: Median {np.median(verhaeltnis):.3f} "
              f"(Quartile {np.percentile(verhaeltnis, 25):.3f} bis {np.percentile(verhaeltnis, 75):.3f})")
    for name, k_ in [("linear", 1), ("kubisch", 2), ("quintisch", 3)]:
        huelle = P_ad[name] / (np.sin(T_werte * Phi[name] / 2) ** 2 if k_ != 2 else np.cos(T_werte * Phi[name] / 2) ** 2)
        sicher = gross & (np.abs(np.sin(T_werte * Phi[name] / 2) if k_ != 2 else np.cos(T_werte * Phi[name] / 2)) > 0.5)
        steigung = np.polyfit(np.log(T_werte[sicher]), np.log(huelle[sicher]), 1)[0]
        print(f"{name:10s}: Steigung der Hülle P/sin² bzw. P/cos² gegen T (T > 50): {steigung:.2f}  (Vorhersage {-2 * k_})")
    glatt = P_ad["glatt S(τ)"]
    m_gl = (T_werte > 30) & (glatt > 1e-23)      # darunter begrenzt die Genauigkeit des Integrators
    a_gl, b_gl = np.polyfit(np.sqrt(T_werte[m_gl]), np.log(glatt[m_gl]), 1)
    print(f"glatt     : ln P ≈ {b_gl:.2f} {a_gl:+.2f}·√T für T > 30 (Vorhersage für die Steigung: −4);  "
          f"P(T = {T_werte[-1]:.0f}) = {glatt[-1]:.1e}")

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    tau = np.linspace(0, 1, 501)
    for name, s in zeitplaene.items():
        linie, = axes[0].plot(tau, s(tau), label=f"s(τ) {name}")
        axes[0].plot(tau, np.gradient(s(tau), tau) / 3, "--", color=linie.get_color(), lw=1)
    axes[0].set_xlabel("τ = t/T")
    axes[0].set_ylabel("s(τ); gestrichelt s'(τ)/3")
    axes[0].set_title("Zeitpläne und ihre Ableitungen")
    axes[0].legend(fontsize=8)
    TT = np.logspace(np.log10(2), np.log10(250), 3000)
    for i, (name, P) in enumerate(P_ad.items()):
        axes[1].loglog(T_werte, P, "o", ms=4, color=f"C{i}", label=name)
        if name in vorher:
            axes[1].loglog(TT, vorher[name](TT), "-", lw=0.7, color=f"C{i}")
    axes[1].set_ylim(1e-26, 1)
    axes[1].set_xlabel("Laufzeit T (ħ = 1)")
    axes[1].set_ylabel("Fehlerwahrscheinlichkeit P")
    axes[1].set_title("Punkte: Simulation; Linien: Vorhersage aus den Randtermen")
    axes[1].legend(fontsize=8, loc="lower left")
    axes[2].semilogy(np.sqrt(T_werte), glatt, "o", ms=4, color="C3", label="glatt S(τ)")
    axes[2].semilogy(np.sqrt(T_werte[m_gl]), np.exp(b_gl + a_gl * np.sqrt(T_werte[m_gl])), "k--", lw=1,
                     label=f"exp({b_gl:.1f} {a_gl:+.2f}·√T)")
    axes[2].set_xlabel("√T")
    axes[2].set_ylabel("Fehlerwahrscheinlichkeit P")
    axes[2].set_title("Glatter Zeitplan: schneller als jede Potenz von 1/T")
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()


def grover_minimum():
    """64. Grover-Minimumsuche auf einer diskretisierten Benchmark-Funktion (Zellen 53 von testfunctions.ipynb)."""
    global HN, N, axes, bbht, duerr_hoyer, exponent, fig, g, groessen, laeufe_dh, mittel, mittel_schw
    global n, ordnung, r_dh, s_, werte, x_min
    def bbht(M, N, r_, lam=6 / 5):
        """Grover-Suche mit unbekannter Zahl M markierter Elemente (Boyer, Brassard, Høyer, Tapp). Gibt die Zahl der
    Abfragen bis zum Fund zurück; exakt simuliert über die Erfolgswahrscheinlichkeit sin²((2j+1)ϑ)."""
        ziel = np.arcsin(np.sqrt(M / N))
        m, abfragen = 1.0, 0
        while True:
            j = r_.integers(0, int(np.ceil(m)))
            abfragen += j + 1                                # j Iterationen + 1 Abfrage zum Prüfen des Messergebnisses
            if r_.random() < np.sin((2 * j + 1) * ziel) ** 2:
                return abfragen
            m = min(lam * m, np.sqrt(N))


    def duerr_hoyer(ordnung, r_):
        """ordnung: Indizes nach aufsteigendem Wert. Rang r = Position in ordnung (0 = Minimum)."""
        N = ordnung.size
        rang = r_.integers(N)                              # zufällige Startschwelle
        abfragen, schwellen = 0, 1
        while rang > 0:
            abfragen += bbht(rang, N, r_)                     # markiert: die rang Elemente unter der Schwelle
            rang = r_.integers(rang)                           # gemessen wird eines davon, gleichverteilt
            schwellen += 1
        return abfragen, schwellen


    r_dh = np.random.default_rng(5)
    groessen, mittel, mittel_schw = [], [], []
    for n in range(6, 21, 2):
        s_ = 2 ** (n // 2)
        g = np.linspace(-5, 5, s_)
        werte = himmelblau(np.array(np.meshgrid(g, g))).ravel()
        ordnung = np.argsort(werte, kind="stable")
        N = werte.size
        laeufe_dh = np.array([duerr_hoyer(ordnung, r_dh) for _ in range(400)])
        groessen.append(N)
        mittel.append(laeufe_dh[:, 0].mean())
        mittel_schw.append(laeufe_dh[:, 1].mean())
        x_min = np.unravel_index(ordnung[0], (s_, s_))
        print(f"N = 2^{n:2d} = {N:8d}: Abfragen im Mittel {mittel[-1]:8.1f} = {mittel[-1] / np.sqrt(N):.2f}·√N "
              f"(90 % unter {np.percentile(laeufe_dh[:, 0], 90) / np.sqrt(N):.2f}·√N);  Schwellen {mittel_schw[-1]:.2f} "
              f"(H_N = {np.sum(1 / np.arange(1, N + 1)):.2f});  Gitterminimum f = {werte[ordnung[0]]:.4f} bei "
              f"({g[x_min[1]]:+.3f}, {g[x_min[0]]:+.3f})")
    groessen, mittel = np.array(groessen, dtype=float), np.array(mittel)
    exponent = np.polyfit(np.log(groessen), np.log(mittel), 1)[0]
    print(f"Angepasster Exponent: Abfragen ∝ N^{exponent:.3f}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].loglog(groessen, mittel, "o", ms=8, label="Dürr–Høyer, Mittel aus 400 Läufen")
    axes[0].loglog(groessen, groessen, "k-", lw=1, label="klassisch: alle N Werte ansehen")
    axes[0].loglog(groessen, 22.5 * np.sqrt(groessen), "k--", lw=1, label="Abbruchschranke 22.5·√N")
    axes[0].loglog(groessen, mittel[-1] / np.sqrt(groessen[-1]) * np.sqrt(groessen), "C0:", label="∝ √N")
    axes[0].set_xlabel("Zahl der Gitterpunkte N")
    axes[0].set_ylabel("Orakel-Abfragen")
    axes[0].set_title("Minimum von Himmelblau auf dem Gitter")
    axes[0].legend(fontsize=8)
    HN = [np.sum(1 / np.arange(1, int(N) + 1)) for N in groessen]
    axes[1].plot(np.log(groessen), mittel_schw, "o", ms=8, label="Schwellen im Mittel")
    axes[1].plot(np.log(groessen), HN, "k-", lw=1, label="H_N = 1 + 1/2 + … + 1/N")
    axes[1].set_xlabel("ln N")
    axes[1].set_ylabel("Zahl der Schwellen")
    axes[1].set_title("Jeder Rang r wird mit Wahrscheinlichkeit 1/r Schwelle")
    axes[1].legend(fontsize=8)
    plt.tight_layout()
    plt.show()


def vqe_landscapes():
    """65. VQE-Landschaften: ein Sinus pro Parameter und Barren Plateaus (Zellen 56 von testfunctions.ipynb)."""
    global E_s, E_tt, E_von, G_s, L, PAULI, Z, _, a1, a2, a_s, achsen
    global art, ax, axes, b_s, bild, c_s, cz, diagonalen, drehung, e0, em, energie
    global ep, fig, gatter1, gitter, i, j, n, n_werte, nn, pos, r_vqe, schnitte
    global shift, steig, t0_, t_test, th, th_, tm, tp, tt, var, zentral, zz
    PAULI = {"X": np.array([[0, 1], [1, 0]], dtype=complex), "Y": np.array([[0, -1j], [1j, 0]]),
             "Z": np.diag([1.0, -1.0]).astype(complex)}


    def drehung(achse, th):
        return np.cos(th / 2) * np.eye(2) - 1j * np.sin(th / 2) * PAULI[achse]


    def gatter1(psi, U, q, n):
        """Ein-Qubit-Gatter U auf Qubit q (q = 0 ist das höchstwertige Bit)."""
        v = psi.reshape(2 ** q, 2, 2 ** (n - q - 1))
        a, b = v[:, 0, :], v[:, 1, :]
        return np.stack([U[0, 0] * a + U[0, 1] * b, U[1, 0] * a + U[1, 1] * b], axis=1).reshape(-1)


    def diagonalen(n):
        bits = (np.arange(2 ** n)[:, None] >> np.arange(n - 1, -1, -1)) & 1
        cz = np.prod(np.where(bits[:, :-1] & bits[:, 1:], -1.0, 1.0), axis=1)        # CZ-Kette (0,1), (1,2), …
        zz = np.where(bits[:, 0] ^ bits[:, 1], -1.0, 1.0)                              # Z₁Z₂
        return cz, zz


    def energie(theta, achsen, cz, zz):
        L, n = theta.shape
        psi = np.zeros(2 ** n, dtype=complex)
        psi[0] = 1
        ry = drehung("Y", np.pi / 4)
        for q in range(n):
            psi = gatter1(psi, ry, q, n)
        for l in range(L):
            for q in range(n):
                psi = gatter1(psi, drehung(achsen[l, q], theta[l, q]), q, n)
            psi = cz * psi
        return float(np.real(np.vdot(psi, zz * psi)))


    r_vqe = np.random.default_rng(15)
    n, L = 4, 8
    cz, zz = diagonalen(n)
    th = r_vqe.uniform(0, 2 * np.pi, (L, n))
    achsen = r_vqe.choice(list("XYZ"), size=(L, n))
    pos = (3, 2)


    def E_von(t):
        th_ = th.copy()
        th_[pos] = t
        return energie(th_, achsen, cz, zz)


    e0, ep, em = E_von(0.0), E_von(np.pi / 2), E_von(-np.pi / 2)
    a_s, c_s = (ep + em) / 2, (ep - em) / 2
    b_s = e0 - a_s
    tt = np.linspace(-np.pi, np.pi, 61)
    E_tt = np.array([E_von(t) for t in tt])
    print(f"E(θ) aus drei Werten als a + b cos θ + c sin θ: größte Abweichung an 61 Stellen {np.max(np.abs(E_tt - (a_s + b_s * np.cos(tt) + c_s * np.sin(tt)))):.1e}")
    t_test = th[pos]
    shift = (E_von(t_test + np.pi / 2) - E_von(t_test - np.pi / 2)) / 2
    zentral = (E_von(t_test + 1e-5) - E_von(t_test - 1e-5)) / 2e-5
    print(f"Gradient: Parameter-Shift {shift:+.12f}, zentrale Differenz (h = 1e−5) {zentral:+.12f}")

    t0_ = time.time()
    n_werte = [2, 4, 6, 8, 10]
    var = {"tief": ([], []), "flach": ([], [])}
    for n in n_werte:
        cz, zz = diagonalen(n)
        for art, L in [("tief", 10 * n), ("flach", 2)]:
            E_s, G_s = [], []
            for _ in range(100):
                th = r_vqe.uniform(0, 2 * np.pi, (L, n))
                achsen = r_vqe.choice(list("XYZ"), size=(L, n))
                tp, tm = th.copy(), th.copy()
                tp[0, 0] += np.pi / 2
                tm[0, 0] -= np.pi / 2
                E_s.append(energie(th, achsen, cz, zz))
                G_s.append((energie(tp, achsen, cz, zz) - energie(tm, achsen, cz, zz)) / 2)
            var[art][0].append(np.var(E_s))
            var[art][1].append(np.var(G_s))
        print(f"n = {n:2d}: Var E tief {var['tief'][0][-1]:.2e} (Haar 1/(2^n+1) = {1 / (2 ** n + 1):.2e}), "
              f"Var ∂E tief {var['tief'][1][-1]:.2e};  flach: Var E {var['flach'][0][-1]:.2e}, Var ∂E {var['flach'][1][-1]:.2e}")
    steig = np.polyfit(n_werte[1:], np.log2(var["tief"][1][1:]), 1)[0]
    print(f"Var ∂E (tief) ∝ 2^({steig:.2f}·n);  Rechenzeit {time.time() - t0_:.1f} s")

    schnitte = {}
    for n in [2, 8]:
        cz, zz = diagonalen(n)
        L = 10 * n
        th = r_vqe.uniform(0, 2 * np.pi, (L, n))
        achsen = r_vqe.choice(list("XYZ"), size=(L, n))
        gitter = np.linspace(0, 2 * np.pi, 21)
        Z = np.zeros((21, 21))
        for i, a1 in enumerate(gitter):
            for j, a2 in enumerate(gitter):
                th_ = th.copy()
                th_[0, 0], th_[L // 2, n - 1] = a1, a2
                Z[j, i] = energie(th_, achsen, cz, zz)
        schnitte[n] = Z
        print(f"Schnitt durch die Landschaft, n = {n}: E zwischen {Z.min():+.3f} und {Z.max():+.3f}")

    fig, axes = plt.subplots(1, 4, figsize=(21, 4.6))
    axes[0].plot(tt, E_tt, "o", ms=4, label="E(θ) simuliert")
    axes[0].plot(tt, a_s + b_s * np.cos(tt) + c_s * np.sin(tt), "k-", lw=1, label="Sinus aus drei Werten")
    axes[0].set_xlabel("θ (rad)")
    axes[0].set_ylabel("E = ⟨Z₁Z₂⟩")
    axes[0].set_title("Ein Parameter: exakt ein Sinus")
    axes[0].legend(fontsize=8)
    nn = np.array(n_werte)
    axes[1].semilogy(nn, var["tief"][0], "o-", label="Var E, tief (L = 10n)")
    axes[1].semilogy(nn, var["tief"][1], "s-", label="Var ∂E, tief")
    axes[1].semilogy(nn, var["flach"][0], "o--", label="Var E, flach (L = 2)")
    axes[1].semilogy(nn, var["flach"][1], "s--", label="Var ∂E, flach")
    axes[1].semilogy(nn, 1 / (2.0 ** nn + 1), "k-", lw=1, label="Haar: 1/(2^n + 1)")
    axes[1].set_xlabel("Zahl der Qubits n")
    axes[1].set_ylabel("Varianz über zufällige Parameter")
    axes[1].set_title("Barren Plateaus")
    axes[1].legend(fontsize=7)
    for ax, n in zip(axes[2:], [2, 8]):
        bild = ax.imshow(schnitte[n], extent=[0, 2 * np.pi, 0, 2 * np.pi], origin="lower", cmap="RdBu_r", vmin=-1, vmax=1)
        ax.set_xlabel("θ in Schicht 1 (rad)")
        ax.set_ylabel("θ in der mittleren Schicht (rad)")
        ax.set_title(f"Schnitt durch E, n = {n}, L = {10 * n}")
        plt.colorbar(bild, ax=ax, label="E")
    plt.tight_layout()
    plt.show()
