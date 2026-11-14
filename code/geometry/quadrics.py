"""Quadriken und elliptische Kurven: Kegelschnitte und Quadrikflächen, quadratische Formen, rationale Punkte, die Gruppenaddition, elliptische Kurven über endlichen Körpern, ECDH und Shors Algorithmus für den diskreten Logarithmus.

Für geometry.ipynb aus quadrics_ellipticcurves.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, conic_invariants, cone_eccentricity, quadric_surfaces, quadratic_forms, rational_points_conics, group_law, heights, finite_field_curves, ecdh, shor_dlog.
"""
import random
import time
from fractions import Fraction
from math import gcd, isqrt, log, ceil
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from IPython.display import display


def load():
    """37. Daten (Zellen 4 von quadrics_ellipticcurves.ipynb)."""
    global O, SUBSCRIPT, classify_conic, conic_eccentricity, conic_matrices, conic_value, curve_str, ec_add, ec_count, ec_mul, ec_neg, ec_order
    global ec_points, field, principal_axes
    # Alles hier (numpy, scipy, sympy, matplotlib) ist in Colab vorinstalliert

    # ---------- Kegelschnitte  a x² + b xy + c y² + d x + e y + f = 0 ----------
    def conic_matrices(coef):
        a, b, c, d, e, f = coef
        A = np.array([[a, b / 2], [b / 2, c]], dtype=float)
        Ahat = np.array([[a, b / 2, d / 2], [b / 2, c, e / 2], [d / 2, e / 2, f]], dtype=float)
        return A, Ahat

    def conic_value(coef, x, y):
        a, b, c, d, e, f = coef
        return a * x * x + b * x * y + c * y * y + d * x + e * y + f

    def classify_conic(coef, tol=1e-9):
        """Typ aus den Invarianten δ = det A und Δ = det Â, skaleninvariant gemacht."""
        A, Ahat = conic_matrices(coef)
        s = np.max(np.abs(Ahat))
        delta, Delta = np.linalg.det(A / s), np.linalg.det(Ahat / s)
        if abs(Delta) < tol:
            return "Geradenpaar" if delta < -tol else ("Punkt" if delta > tol else "parallele Geraden")
        if delta > tol:
            return "Ellipse" if np.trace(A) * Delta < 0 else "leere Ellipse"
        return "Hyperbel" if delta < -tol else "Parabel"

    def principal_axes(coef, tol=1e-12):
        """Hauptachsentransformation: Eigenwerte, Drehung R, Zentrum oder Scheitel x0 und
    die Normalform als Funktion der Koordinaten w = Rᵀ(x − x0)."""
        a, b, c, d, e, f = coef
        A, Ahat = conic_matrices(coef)
        lam, R = np.linalg.eigh(A)
        bvec = np.array([d, e], dtype=float)
        if abs(np.linalg.det(A)) > tol:                         # Mittelpunktskegelschnitt
            x0 = -0.5 * np.linalg.solve(A, bvec)
            const = np.linalg.det(Ahat) / np.linalg.det(A)      # c' = Δ/δ
            return dict(lam=lam, R=R, x0=x0, const=const,
                        normal=lambda w: lam[0] * w[0] ** 2 + lam[1] * w[1] ** 2 + const)
        i, j = np.argsort(np.abs(lam))                          # λ_i = 0 (Achsenrichtung), λ_j ≠ 0
        bp = R.T @ bvec                                         # lineare Koeffizienten im gedrehten System
        u = np.zeros(2)
        u[j] = -bp[j] / (2 * lam[j])                            # quadratische Ergänzung in u_j
        u[i] = -(f - bp[j] ** 2 / (4 * lam[j])) / bp[i]
        return dict(lam=lam, R=R, x0=R @ u, const=0.0, lin=bp[i], i=i, j=j,
                    normal=lambda w: lam[j] * w[j] ** 2 + bp[i] * w[i])

    def conic_eccentricity(coef):
        """Exzentrizität aus der Normalform λ₁u² + λ₂v² = k mit k = −Δ/δ: e² = 1 − λ₁/λ₂, wobei λ₁ der
    betragskleinste Eigenwert mit dem Vorzeichen von k ist (große Halbachse bzw. reelle Achse)."""
        A, Ahat = conic_matrices(coef)
        lam = np.linalg.eigvalsh(A)
        k = -np.linalg.det(Ahat) / np.linalg.det(A)
        idx = [i for i in range(2) if np.sign(lam[i]) == np.sign(k)]
        i1 = min(idx, key=lambda i: abs(lam[i]))
        return np.sqrt(max(0.0, 1 - lam[i1] / lam[1 - i1]))

    # ---------- Elliptische Kurven  y² = x³ + a x + b ----------
    O = None                                                    # der Punkt im Unendlichen, das neutrale Element

    def ec_add(P, Q, a, p=None):
        """P + Q mit der Sekanten-Tangenten-Regel.
    p = None: über ℚ (Fraction) oder ℝ (float); sonst über dem Körper 𝔽ₚ."""
        if P is O:
            return Q
        if Q is O:
            return P
        (x1, y1), (x2, y2) = P, Q
        if p is None:
            if x1 == x2 and y1 == -y2:
                return O
            lam = (3 * x1 * x1 + a) / (2 * y1) if x1 == x2 else (y2 - y1) / (x2 - x1)
            x3 = lam * lam - x1 - x2
            return (x3, lam * (x1 - x3) - y1)
        if x1 == x2 and (y1 + y2) % p == 0:
            return O
        if x1 == x2:
            lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
        else:
            lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
        x3 = (lam * lam - x1 - x2) % p
        return (x3, (lam * (x1 - x3) - y1) % p)

    def ec_neg(P, p=None):
        if P is O:
            return O
        return (P[0], -P[1] % p) if p else (P[0], -P[1])

    def ec_mul(k, P, a, p=None):
        """k·P mit Double-and-Add: O(log k) Gruppenoperationen."""
        if k < 0:
            return ec_mul(-k, ec_neg(P, p), a, p)
        R = O
        while k:
            if k & 1:
                R = ec_add(R, P, a, p)
            P = ec_add(P, P, a, p)
            k >>= 1
        return R

    def ec_points(a, b, p):
        """Alle Punkte von y² = x³ + ax + b über 𝔽ₚ, beginnend mit O (für kleine p)."""
        roots = {}
        for y in range(p):
            roots.setdefault(y * y % p, []).append(y)
        return [O] + [(x, y) for x in range(p) for y in roots.get((x ** 3 + a * x + b) % p, [])]

    def ec_count(a, b, p):
        """#E(𝔽ₚ) = p + 1 + Σ_x χ(x³ + ax + b) mit dem Legendre-Symbol χ, vektorisiert."""
        x = np.arange(p, dtype=np.int64)
        rhs = (x * x % p * x + a * x + b) % p
        is_square = np.zeros(p, dtype=bool)
        is_square[x * x % p] = True
        return p + 1 + int(np.count_nonzero(is_square[rhs] & (rhs != 0))) - int(np.count_nonzero(~is_square[rhs]))

    SUBSCRIPT = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

    def field(p):
        return "𝔽" + str(p).translate(SUBSCRIPT)

    def curve_str(a, b):
        """Gleichung y² = x³ + ax + b als lesbarer Text."""
        s = "y² = x³"
        for coeff, term in [(a, "x"), (b, "")]:
            if coeff:
                mag = abs(coeff)
                s += (" − " if coeff < 0 else " + ") + ("" if mag == 1 and term else str(mag)) + term
        return s

    def ec_order(P, a, p):
        n, R = 1, P
        while R is not O:
            R, n = ec_add(R, P, a, p), n + 1
        return n

    print("Werkzeuge bereit")


def conic_invariants():
    """38. Kegelschnitte: Invarianten und Hauptachsen (Zellen 6 von quadrics_ellipticcurves.ipynb)."""
    global A, Ahat, Xg, Yg, ax, axes, axes_, coef, col, conics, dvec, err
    global fig, k_, l1, l2, li, lj, name, pa, pts, rng, s, w
    conics = {"Ellipse": (5, -4, 8, -6, 12, -12),
              "Hyperbel": (1, 4, 1, -2, 2, -4),
              "Parabel": (1, -2, 1, -4, -4, 4),
              "Geradenpaar": (2, -1, -1, 0, 3, -2)}            # = (x − y + 1)(2x + y − 2)
    rng = np.random.default_rng(1)
    Xg, Yg = np.meshgrid(np.linspace(-4, 4, 801), np.linspace(-4, 4, 801))
    fig, axes = plt.subplots(1, 4, figsize=(18, 4.8))
    for ax, (name, coef) in zip(axes, conics.items()):
        A, Ahat = conic_matrices(coef)
        pa = principal_axes(coef)
        ax.contour(Xg, Yg, conic_value(coef, Xg, Yg), levels=[0], colors="black", linewidths=1.5)
        for k_, col in zip(range(2), ["tab:red", "tab:blue"]):
            dvec = pa["R"][:, k_]
            ax.plot(*np.array([pa["x0"] - 8 * dvec, pa["x0"] + 8 * dvec]).T, c=col, lw=1, ls="--",
                    label=f"Eigenvektor zu λ = {pa['lam'][k_]:+.2f}")
        ax.plot(*pa["x0"], "o", c="black", ms=5)
        pts = rng.uniform(-4, 4, (1000, 2))
        w = (pts - pa["x0"]) @ pa["R"]                        # Zeilen: wᵀ = (x − x0)ᵀ R
        err = np.max(np.abs(conic_value(coef, pts[:, 0], pts[:, 1]) - pa["normal"](w.T)))
        ax.set_title(f"{name}: δ = {np.linalg.det(A):+.2f}, Δ = {np.linalg.det(Ahat):+.2f}\n"
                     f"aus den Invarianten: {classify_conic(coef)}; Probe der Normalform {err:.0e}", fontsize=9)
        ax.set_xlim(-4, 4); ax.set_ylim(-4, 4); ax.set_aspect("equal")
        ax.set_xlabel("x"); ax.set_ylabel("y")
        ax.legend(fontsize=7, loc="lower right")
    fig.tight_layout()
    plt.show()

    for name, coef in conics.items():
        pa = principal_axes(coef)
        l1, l2 = pa["lam"]
        if name == "Parabel":
            lj, li = pa["lam"][pa["j"]], pa["lin"]
            print(f"{name:12s}: Normalform {lj:+.3f} w₂² {li:+.3f} w₁ = 0, also w₂² = {-li / lj:+.3f} w₁;  "
                  f"Scheitel ({pa['x0'][0]:.3f}, {pa['x0'][1]:.3f})")
        elif name == "Geradenpaar":
            s = np.sqrt(-l1 / l2)
            print(f"{name:12s}: Normalform {l1:+.3f} u² {l2:+.3f} v² = 0 (Konstante {abs(pa['const']):.0e}), also v = ±{s:.3f} u;  "
                  f"Schnittpunkt ({pa['x0'][0]:.3f}, {pa['x0'][1]:.3f}), Winkel zwischen den Geraden {np.degrees(2 * np.arctan(s)):.2f}°")
        else:
            axes_ = [np.sqrt(abs(pa["const"] / l)) for l in (l1, l2)]
            print(f"{name:12s}: Normalform {l1:+.3f} u² {l2:+.3f} v² {pa['const']:+.3f} = 0;  Zentrum ({pa['x0'][0]:.3f}, {pa['x0'][1]:.3f}), "
                  f"Halbachsen {axes_[0]:.3f} und {axes_[1]:.3f}")


def cone_eccentricity():
    """39. Der Kegel, die Exzentrizität und die Keplerbahnen (Zellen 9 von quadrics_ellipticcurves.ipynb)."""
    global Avec, L, RR, T, TH, Xk, Yk, ax2, ax3, coef, col, cut_rows
    global drift, e_fit, e_lrl, e_t, e_target, fig, fit_conic, keep, kepler_rhs, kepler_rows, m, name
    global ok, phi, r, sol, sv, typ, v0, vx, vy, x, y
    def kepler_rhs(t, s):
        x, y, vx, vy = s
        r3 = (x * x + y * y) ** 1.5
        return [vx, vy, -x / r3, -y / r3]

    def fit_conic(x, y):
        D = np.column_stack([x * x, x * y, y * y, x, y, np.ones_like(x)])
        sv = np.linalg.svd(D, full_matrices=False)
        return sv[2][-1], sv[1][-1] / sv[1][0]                   # Koeffizienten, relativer kleinster Singulärwert

    fig = plt.figure(figsize=(16, 6.2))
    ax3 = fig.add_subplot(1, 2, 1, projection="3d")
    TH, RR = np.meshgrid(np.linspace(0, 2 * np.pi, 120), np.linspace(0, 3.0, 40))
    ax3.plot_surface(RR * np.cos(TH), RR * np.sin(TH), RR, color="lightgrey", alpha=0.18, linewidth=0)
    cut_rows = []
    for m, col, name in [(0.5, "tab:blue", "Ellipse"), (1.0, "tab:green", "Parabel"), (1.6, "tab:red", "Hyperbel")]:
        phi = np.linspace(-np.pi, np.pi, 6001)
        with np.errstate(divide="ignore"):
            r = 1 / (1 - m * np.cos(phi))                     # r(φ)
        r[(r <= 0) | (r > 3.0)] = np.nan
        ax3.plot(r * np.cos(phi), r * np.sin(phi), r, c=col, lw=2.5, label=f"Ebene z = 1 + {m} x: {name}")
        ax3.plot(r * np.cos(phi), r * np.sin(phi), 0 * r, c=col, lw=1, ls="--")
        ok = np.isfinite(r)
        coef, sv = fit_conic(r[ok] * np.cos(phi[ok]), r[ok] * np.sin(phi[ok]))
        cut_rows.append((m, conic_eccentricity(coef), classify_conic(coef)))
    ax3.set_xlabel("x"); ax3.set_ylabel("y"); ax3.set_zlabel("z")
    ax3.plot([], [], "k--", lw=1, label="Projektion auf z = 0 (Brennpunkt im Ursprung)")
    ax3.set_zlim(0, 3.0)
    ax3.set_box_aspect((1, 1, 0.5))
    ax3.view_init(elev=40, azim=-135)
    ax3.set_title("Schnitte des Kegels x² + y² = z² mit Ebenen z = 1 + m x")
    ax3.legend(fontsize=8, loc="upper left")

    ax2 = fig.add_subplot(1, 2, 2)
    Xk, Yk = np.meshgrid(np.linspace(-6, 3, 900), np.linspace(-5, 5, 1000))
    kepler_rows = []
    for e_target, col in [(0.0, "tab:purple"), (0.5, "tab:blue"), (1.0, "tab:green"), (1.6, "tab:red")]:
        v0 = np.sqrt(1 + e_target)
        T = 2 * np.pi * (1 / (1 - e_target)) ** 1.5 if e_target < 1 else 10.0      # ein Umlauf bzw. Flug nach außen
        sol = solve_ivp(kepler_rhs, [0, T], [1.0, 0.0, 0.0, v0], method="DOP853", rtol=1e-12, atol=1e-12,
                        t_eval=np.linspace(0, T, 3000))
        x, y, vx, vy = sol.y
        L = x * vy - y * vx
        r = np.hypot(x, y)
        Avec = np.array([vy * L - x / r, -vx * L - y / r])                        # Laplace-Runge-Lenz-Vektor
        if e_target >= 1:                                                          # Rückweg durch Zeitumkehr (Spiegelung an der x-Achse)
            x, y = np.r_[x[::-1], x], np.r_[-y[::-1], y]
        coef, sv = fit_conic(x, y)
        keep = (x > -6) & (np.abs(y) < 5)
        ax2.plot(x[keep], y[keep], c=col, lw=4, alpha=0.35, label=f"v₀ = {v0:.3f}: e = |v₀² − 1| = {e_target}")
        ax2.contour(Xk, Yk, conic_value(coef, Xk, Yk), levels=[0], colors="black", linewidths=0.8, linestyles="--")
        kepler_rows.append((v0, e_target, np.linalg.norm(Avec[:, 0]), np.max(np.linalg.norm(Avec - Avec[:, :1], axis=0)),
                            conic_eccentricity(coef), classify_conic(coef), sv))
    ax2.plot(0, 0, "*", c="orange", ms=14, label="Zentralkörper (Brennpunkt)")
    ax2.plot([], [], "k--", lw=0.8, label="angepasster Kegelschnitt")
    ax2.set_xlim(-6, 3); ax2.set_ylim(-5, 5); ax2.set_aspect("equal")
    ax2.set_xlabel("x"); ax2.set_ylabel("y")
    ax2.set_title("Keplerbahnen im Potential −1/r und angepasste Kegelschnitte")
    ax2.legend(fontsize=8, loc="lower left")
    fig.tight_layout()
    plt.show()

    for m, e_fit, typ in cut_rows:
        print(f"Kegelschnitt mit m = {m}: Exzentrizität aus der Anpassung {e_fit:.10f}, Typ {typ}")
    for v0, e_t, e_lrl, drift, e_fit, typ, sv in kepler_rows:
        print(f"Bahn v₀ = {v0:.4f}: e Theorie {e_t:.3f}, |A| = {e_lrl:.10f}, Drift von A {drift:.0e}, "
              f"e aus der Anpassung {e_fit:.8f} ({typ}), Residuum σ_min/σ_max = {sv:.0e}")


def quadric_surfaces():
    """40. Quadrikflächen: Signatur und Geraden auf dem Hyperboloid (Zellen 12 von quadrics_ellipticcurves.ipynb)."""
    global Ahat, Rr, S, U, V, Xs, Ys, ax, axs, col, fig, kind
    global lx, ly, lz, name, ph, quadrics, res_hyp, res_sad, sA, sAh, s_, sgn
    global signature, surf, t, tt, u
    def signature(M, tol=1e-12):
        ev = np.linalg.eigvalsh(M)
        return int(np.sum(ev > tol)), int(np.sum(ev < -tol))

    # Â für F(x, y, z) = (x, y, z, 1) Â (x, y, z, 1)ᵀ
    quadrics = {
        "Ellipsoid x²/4 + y² + z²/2.25 = 1": np.diag([1 / 4, 1, 1 / 2.25, -1]),
        "einschaliges Hyperboloid x² + y² − z² = 1": np.diag([1, 1, -1, -1.0]),
        "zweischaliges Hyperboloid x² + y² − z² = −1": np.diag([1, 1, -1, 1.0]),
        "elliptisches Paraboloid z = x² + y²": np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, -0.5], [0, 0, -0.5, 0]]),
        "hyperbolisches Paraboloid z = x² − y²": np.array([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 0, -0.5], [0, 0, -0.5, 0]]),
        "Kegel x² + y² = z²": np.diag([1, 1, -1, 0.0]),
    }
    u = np.linspace(0, 2 * np.pi, 70)
    fig = plt.figure(figsize=(18, 11))
    axs = [fig.add_subplot(2, 3, i + 1, projection="3d") for i in range(6)]
    surf = dict(color="tab:blue", alpha=0.30, linewidth=0, shade=True)

    U, V = np.meshgrid(u, np.linspace(0, np.pi, 40))
    axs[0].plot_surface(2 * np.cos(U) * np.sin(V), np.sin(U) * np.sin(V), 1.5 * np.cos(V), **surf)

    U, S = np.meshgrid(u, np.linspace(-1.4, 1.4, 40))
    axs[1].plot_surface(np.cosh(S) * np.cos(U), np.cosh(S) * np.sin(U), np.sinh(S), **surf)
    t = np.linspace(-np.sinh(1.4), np.sinh(1.4), 200)
    res_hyp = 0.0
    for sgn, col in [(1, "tab:red"), (-1, "tab:orange")]:
        for ph in np.linspace(0, 2 * np.pi, 16, endpoint=False):
            lx, ly, lz = np.cos(ph) - t * np.sin(ph), np.sin(ph) + t * np.cos(ph), sgn * t
            axs[1].plot(lx, ly, lz, c=col, lw=1)
            res_hyp = max(res_hyp, np.max(np.abs(lx ** 2 + ly ** 2 - lz ** 2 - 1)))

    U, S = np.meshgrid(u, np.linspace(0, 1.6, 30))
    for sgn in (1, -1):
        axs[2].plot_surface(np.sinh(S) * np.cos(U), np.sinh(S) * np.sin(U), sgn * np.cosh(S), **surf)

    U, Rr = np.meshgrid(u, np.linspace(0, 1.5, 30))
    axs[3].plot_surface(Rr * np.cos(U), Rr * np.sin(U), Rr ** 2, **surf)

    Xs, Ys = np.meshgrid(np.linspace(-1.5, 1.5, 40), np.linspace(-1.5, 1.5, 40))
    axs[4].plot_surface(Xs, Ys, Xs ** 2 - Ys ** 2, **surf)
    res_sad = 0.0
    tt = np.linspace(-1.5, 1.5, 200)
    for s_ in np.linspace(-1.5, 1.5, 11):
        for lx, ly, col in [((s_ + tt) / 2, (tt - s_) / 2, "tab:red"),      # x − y = s
                            ((tt + s_) / 2, (s_ - tt) / 2, "tab:orange")]:  # x + y = s
            lz = (lx - ly) * (lx + ly)
            axs[4].plot(lx, ly, lz, c=col, lw=1)
        lx, ly = (s_ + tt) / 2, (tt - s_) / 2
        res_sad = max(res_sad, np.max(np.abs(lx ** 2 - ly ** 2 - s_ * tt)))   # z = s·t entlang der Geraden

    U, Rr = np.meshgrid(u, np.linspace(0, 1.5, 30))
    for sgn in (1, -1):
        axs[5].plot_surface(Rr * np.cos(U), Rr * np.sin(U), sgn * Rr, **surf)

    for ax, (name, Ahat) in zip(axs, quadrics.items()):
        ax.set_box_aspect([np.ptp(lim) for lim in (ax.get_xlim3d(), ax.get_ylim3d(), ax.get_zlim3d())])   # gleiche Maßstäbe
        sA, sAh = signature(Ahat[:3, :3]), signature(Ahat)
        ax.set_title(f"{name}\nSignatur A: {sA}, Signatur Â: {sAh}", fontsize=9)
        ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z")
        ax.locator_params(nbins=5)
    fig.tight_layout()
    plt.show()

    for name, Ahat in quadrics.items():
        sAh = signature(Ahat)
        kind = "Rang 3, Kegel (entartet)" if sum(sAh) < 4 else ("doppelt geregelt" if sAh == (2, 2) else "nicht geregelt, projektiv eine Kugel")
        print(f"{name:46s} Signatur Â = {sAh}: {kind}")
    print(f"Probe der Geraden: größte |F| auf dem Hyperboloid {res_hyp:.1e}, auf dem Sattel {res_sad:.1e}")


def quadratic_forms():
    """41. Quadratische Formen in Optimierung und Statistik (Zellen 15 von quadrics_ellipticcurves.ipynb)."""
    global H, Hk, R30, Sigma, V_s, Xg, Yg, alpha, axes, col, d2, ell
    global err, fig, fractions, fval, gradient_descent, k_, kappa, lab, lam_s, meas, path, r_
    global rates, rho, rng, rotation, samples, theo, tt, x_newton, x_start
    def rotation(deg):
        c, s = np.cos(np.radians(deg)), np.sin(np.radians(deg))
        return np.array([[c, -s], [s, c]])

    def gradient_descent(H, x0, alpha, steps):
        xs = [x0]
        for _ in range(steps):
            xs.append(xs[-1] - alpha * H @ xs[-1])
        return np.array(xs)

    rng = np.random.default_rng(4)
    R30 = rotation(30)
    H = R30 @ np.diag([1.0, 10.0]) @ R30.T
    x_start = np.array([-2.5, 1.6])
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.2))
    Xg, Yg = np.meshgrid(np.linspace(-3, 3, 300), np.linspace(-2.2, 2.2, 300))
    fval = 0.5 * (H[0, 0] * Xg ** 2 + 2 * H[0, 1] * Xg * Yg + H[1, 1] * Yg ** 2)
    axes[0].contour(Xg, Yg, fval, levels=np.geomspace(0.02, 30, 14), colors="lightgrey", linewidths=0.8)
    for alpha, lab, col in [(1 / 10, "Gradient, α = 1/λ_max", "tab:blue"), (2 / 11, "Gradient, α = 2/(λ_min + λ_max)", "tab:red")]:
        path = gradient_descent(H, x_start, alpha, 25)
        axes[0].plot(*path.T, "o-", ms=3, lw=1, c=col, label=f"{lab}: |x₂₅| = {np.linalg.norm(path[-1]):.1e}")
    x_newton = x_start - np.linalg.solve(H, H @ x_start)
    axes[0].plot(*np.array([x_start, x_newton]).T, "s-", c="tab:green", ms=5, label=f"Newton: |x₁| = {np.linalg.norm(x_newton):.0e}")
    for k_, col in zip(range(2), ["black", "black"]):
        axes[0].annotate("", xy=R30[:, k_] * (1.5 if k_ == 0 else 0.6), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=col))
    axes[0].set_aspect("equal")
    axes[0].set_xlabel("x₁"); axes[0].set_ylabel("x₂")
    axes[0].set_title("Niveaulinien von ½ xᵀHx, Pfeile: Eigenvektoren (λ = 1, 10)")
    axes[0].legend(fontsize=8, loc="lower right")

    rates = {}
    for kappa, col in [(2, "tab:green"), (10, "tab:blue"), (50, "tab:red")]:
        Hk = np.diag([1.0, kappa])
        path = gradient_descent(Hk, np.array([1.0, 1.0]) / np.sqrt(2), 2 / (1 + kappa), 60)
        err = np.linalg.norm(path, axis=1)
        rho = (kappa - 1) / (kappa + 1)
        rates[kappa] = (np.exp(np.polyfit(np.arange(61), np.log(err), 1)[0]), rho)
        axes[1].semilogy(err, c=col, lw=2, label=f"κ = {kappa}: gemessen {rates[kappa][0]:.4f} pro Schritt")
        axes[1].semilogy(rho ** np.arange(61), "--", c="black", lw=0.8)
    axes[1].plot([], [], "k--", lw=0.8, label="Vorhersage ((κ − 1)/(κ + 1))^k")
    axes[1].set_xlabel("Iteration k")
    axes[1].set_ylabel("Fehler |x_k − x*|")
    axes[1].set_title("Gradientenverfahren mit α = 2/(λ_min + λ_max)")
    axes[1].legend(fontsize=8)

    Sigma = np.array([[2.0, 1.2], [1.2, 1.0]])
    samples = rng.standard_normal((20000, 2)) @ np.linalg.cholesky(Sigma).T
    d2 = np.einsum("ij,jk,ik->i", samples, np.linalg.inv(Sigma), samples)
    axes[2].plot(*samples.T, ".", ms=1, c="tab:blue", alpha=0.3)
    lam_s, V_s = np.linalg.eigh(Sigma)
    tt = np.linspace(0, 2 * np.pi, 400)
    fractions = {}
    for r_, col in [(1, "tab:green"), (2, "tab:orange"), (3, "tab:red")]:
        ell = r_ * (V_s @ np.diag(np.sqrt(lam_s)) @ np.array([np.cos(tt), np.sin(tt)]))
        fractions[r_] = (np.mean(d2 <= r_ ** 2), 1 - np.exp(-r_ ** 2 / 2))
        axes[2].plot(*ell, c=col, lw=2, label=f"d = {r_}: innen {fractions[r_][0]:.4f}, Theorie {fractions[r_][1]:.4f}")
    axes[2].set_aspect("equal")
    axes[2].set_xlim(-5, 5); axes[2].set_ylim(-4, 4)
    axes[2].set_xlabel("x₁"); axes[2].set_ylabel("x₂")
    axes[2].set_title("Normalverteilung, Σ = [[2, 1.2], [1.2, 1]]")
    axes[2].legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    plt.show()

    for kappa, (meas, theo) in rates.items():
        print(f"κ = {kappa:2d}: Kontraktion pro Schritt gemessen {meas:.6f}, Theorie (κ − 1)/(κ + 1) = {theo:.6f}; "
              f"Schritte für Faktor 10⁻⁶: {np.log(1e-6) / np.log(theo):.0f}")
    for r_, (meas, theo) in fractions.items():
        print(f"Anteil in der Ellipse d ≤ {r_}: {meas:.4f} (Theorie 1 − e^(−r²/2) = {theo:.4f})")


def rational_points_conics():
    """42. Rationale Punkte auf Kegelschnitten: pythagoreische Tripel (Zellen 18 von quadrics_ellipticcurves.ipynb)."""
    global C, a, ax, axes, b, big, brute, c, col, fig, first_rational_point, found
    global nn, param, pred, primitive_triples, small, sx, sy, tq, triples_brute, tt, xq, yq
    def primitive_triples(C):
        """Alle primitiven Tripel (a < b < c ≤ C) aus der Parametrisierung (n² − m², 2mn, n² + m²)."""
        n = np.arange(2, isqrt(C) + 1)[:, None]
        m = np.arange(1, isqrt(C) + 1)[None, :]
        ok = (m < n) & ((n - m) % 2 == 1) & (np.gcd(m, n) == 1) & (n * n + m * m <= C)
        nn, mm = np.broadcast_to(n, ok.shape)[ok], np.broadcast_to(m, ok.shape)[ok]
        a, b, c = nn * nn - mm * mm, 2 * mm * nn, nn * nn + mm * mm
        return np.column_stack([np.minimum(a, b), np.maximum(a, b), c])

    def triples_brute(C):
        out = set()
        for c in range(1, C + 1):
            a = np.arange(1, c, dtype=np.int64)
            b2 = c * c - a * a
            b = np.round(np.sqrt(b2)).astype(np.int64)
            for ai, bi in zip(a[(b * b == b2) & (a < b)], b[(b * b == b2) & (a < b)]):
                if gcd(gcd(int(ai), int(bi)), c) == 1:
                    out.add((int(ai), int(bi), c))
        return out

    def first_rational_point(nn, Zmax=300):
        """Kleinste Lösung von X² + Y² = n Z² ohne gemeinsamen Teiler mit Z ≤ Zmax, sonst None."""
        for Z in range(1, Zmax + 1):
            X = np.arange(0, isqrt(nn * Z * Z) + 1, dtype=np.int64)
            Y2 = nn * Z * Z - X * X
            Y = np.round(np.sqrt(Y2)).astype(np.int64)
            for x_, y_ in zip(X[Y * Y == Y2], Y[Y * Y == Y2]):
                if gcd(gcd(int(x_), int(y_)), Z) == 1:
                    return int(x_), int(y_), Z
        return None

    fig, axes = plt.subplots(1, 2, figsize=(15, 6.6))
    ax = axes[0]
    small = primitive_triples(300)
    for a, b, c in small:
        for sx in (1, -1):
            for sy in (1, -1):
                ax.plot([sx * a / c, sx * b / c], [sy * b / c, sy * a / c], ".", c="black", ms=2.5, zorder=3)
    tt = np.linspace(0, 2 * np.pi, 400)
    ax.plot(np.cos(tt), np.sin(tt), c="lightgrey", lw=3, zorder=1)
    for tq, col in zip([Fraction(1, 5), Fraction(1, 3), Fraction(1, 2), Fraction(2, 3), Fraction(1, 1), Fraction(3, 2), Fraction(4, 1)],
                       plt.cm.viridis(np.linspace(0, 0.9, 7))):
        xq, yq = (1 - tq ** 2) / (1 + tq ** 2), 2 * tq / (1 + tq ** 2)
        ax.plot([-1, float(xq)], [0, float(yq)], c=col, lw=1)
        ax.plot(float(xq), float(yq), "o", c=col, ms=6, zorder=4)
        ax.annotate(f"t = {tq}: ({xq}, {yq})", (float(xq), float(yq)), xytext=(6, 2), textcoords="offset points", fontsize=8)
    ax.plot(-1, 0, "o", c="tab:red", ms=7, zorder=4)
    ax.set_xlim(-1.2, 1.75); ax.set_ylim(-1.2, 1.2); ax.set_aspect("equal")
    ax.set_xlabel("x"); ax.set_ylabel("y")
    ax.set_title("Geraden durch (−1, 0) mit rationaler Steigung t; schwarz: alle Punkte mit Nenner ≤ 300")

    big = primitive_triples(20000)
    axes[1].plot(big[:, 0], big[:, 1], ".", ms=1.2, c="tab:blue")
    axes[1].plot(big[:, 1], big[:, 0], ".", ms=1.2, c="tab:blue")
    axes[1].set_xlim(0, 20000); axes[1].set_ylim(0, 20000); axes[1].set_aspect("equal")
    axes[1].set_xlabel("Kathete a"); axes[1].set_ylabel("Kathete b")
    axes[1].set_title(f"{len(big)} primitive Tripel mit c ≤ 20 000")
    fig.tight_layout()
    plt.show()

    param = {tuple(int(v) for v in row) for row in primitive_triples(2000)}
    brute = triples_brute(2000)
    print(f"c ≤ 2000: Parametrisierung {len(param)} Tripel, Durchprobieren {len(brute)}, identisch: {param == brute}")
    for C in [10 ** 3, 10 ** 4, 10 ** 5, 10 ** 6]:
        print(f"Primitive Tripel mit c ≤ {C:>9,}: {len(primitive_triples(C)):7d};  C/(2π) = {C / (2 * np.pi):9.1f}")
    print("\nx² + y² = n: rationaler Punkt?")
    for nn in range(1, 16):
        pred = all(e % 2 == 0 for q, e in sp.factorint(nn).items() if q % 4 == 3)
        found = first_rational_point(nn)
        print(f"  n = {nn:2d}: Vorhersage {'ja  ' if pred else 'nein'} | gefunden: "
              f"{f'({found[0]}/{found[2]})² + ({found[1]}/{found[2]})²' if found else 'keine Lösung mit Nenner ≤ 300'}")


def group_law():
    """43. Die Gruppenaddition auf einer elliptischen Kurve (Zellen 21 von quadrics_ellipticcurves.ipynb)."""
    global P, PQ, Q, R, a_, axes, b_, cubic, digits, draw_case, fails, fig
    global lam_, lhs, nu_, on17, on_curve_point, pts17, rhs, xs_, xx, ys_, yy
    xs_, ys_, lam_, nu_, a_, b_ = sp.symbols("x y lambda nu a b")
    cubic = sp.Poly(xs_ ** 3 + a_ * xs_ + b_ - (lam_ * xs_ + nu_) ** 2, xs_)
    print("x³ + ax + b − (λx + ν)² hat die Koeffizienten (x³, x², x, 1):")
    display(cubic.all_coeffs())
    print("Steigung der Tangente an y² = x³ + ax + b:")
    display(sp.Eq(sp.Symbol("dy/dx"), sp.idiff(ys_ ** 2 - xs_ ** 3 - a_ * xs_ - b_, ys_, xs_)))

    def on_curve_point(x, a, b, sign=1):
        return (x, sign * np.sqrt(x ** 3 + a * x + b))

    def draw_case(ax, a, b, P, Q, title):
        Xg, Yg = np.meshgrid(np.linspace(-2, 3.2, 700), np.linspace(-4.6, 4.6, 700))
        ax.contour(Xg, Yg, Yg ** 2 - Xg ** 3 - a * Xg - b, levels=[0], colors="black", linewidths=1.5)
        S = ec_add(P, Q, a)
        Rp = ec_neg(S)                                            # dritter Schnittpunkt der Geraden
        lam = (Rp[1] - P[1]) / (Rp[0] - P[0])
        xl = np.linspace(-2, 3.2, 10)
        ax.plot(xl, P[1] + lam * (xl - P[0]), c="tab:blue", lw=1, label="Gerade durch P und Q" if P != Q else "Tangente in P")
        ax.plot([Rp[0], S[0]], [Rp[1], S[1]], c="grey", ls=":", lw=1)
        for pt, name, col in [(P, "P", "tab:blue"), (Q, "Q", "tab:blue"), (Rp, "−(P + Q)" if P != Q else "−2P", "tab:orange"),
                              (S, "P + Q" if P != Q else "2P", "tab:red")]:
            if name == "Q" and P == Q:
                continue
            ax.plot(*pt, "o", c=col, ms=7)
            ax.annotate(name, pt, xytext=(6, 6), textcoords="offset points", fontsize=10)
        ax.set_xlim(-2, 3.2); ax.set_ylim(-4.6, 4.6)
        ax.set_xlabel("x"); ax.set_ylabel("y")
        ax.set_title(title + f"\nErgebnis ({S[0]:.4f}, {S[1]:.4f}), Probe y² − x³ − ax − b = {S[1] ** 2 - S[0] ** 3 - a * S[0] - b:.0e}", fontsize=9)
        ax.legend(fontsize=8, loc="lower right")

    fig, axes = plt.subplots(1, 3, figsize=(18, 5.6))
    draw_case(axes[0], -1, 1, on_curve_point(-1.2, -1, 1, -1), on_curve_point(0.2, -1, 1), "P + Q auf y² = x³ − x + 1")
    draw_case(axes[1], -1, 1, (1.0, 1.0), (1.0, 1.0), "Verdopplung 2P auf y² = x³ − x + 1")
    draw_case(axes[2], -1, 0, on_curve_point(-0.9, -1, 0), on_curve_point(-0.2, -1, 0, -1), "Zwei Punkte auf dem Ei von y² = x³ − x")
    fig.tight_layout()
    plt.show()

    pts17 = []
    for xx in [-2, -1, 2, 4, 8, 43, 52, 5234]:
        yy = isqrt(xx ** 3 + 17)
        assert yy * yy == xx ** 3 + 17
        pts17 += [(Fraction(xx), Fraction(yy)), (Fraction(xx), Fraction(-yy))]
    on17 = lambda P: P is O or P[1] ** 2 == P[0] ** 3 + 17
    fails, digits = 0, 0
    for P in pts17:
        for Q in pts17:
            PQ = ec_add(P, Q, 0)
            for R in pts17:
                lhs, rhs = ec_add(PQ, R, 0), ec_add(P, ec_add(Q, R, 0), 0)
                fails += (lhs != rhs) or not on17(lhs)
                if lhs is not O:
                    digits = max(digits, len(str(lhs[0].denominator)))
    print(f"y² = x³ + 17: {len(pts17)} ganzzahlige Punkte, {len(pts17) ** 3} Tripel (P + Q) + R = P + (Q + R) exakt geprüft, "
          f"Abweichungen oder Punkte neben der Kurve: {fails}; größter Nenner von x: {digits} Stellen")


def heights():
    """44. Rationale Punkte und Höhe: Grad 2, 3 und 4 (Zellen 24 von quadrics_ellipticcurves.ipynb)."""
    global A, A_, B, B_, Cs, D, H_, H_mult, N_circle, N_ell, P, a
    global a_, axes, b, b4, b_, c, fig, found, h_, height, hs, hyp
    global icpt, mult, n, nP, ns, ok, quartic, rhs, slope
    def height(q):
        return max(abs(q.numerator), q.denominator)

    # Grad 3: Vielfache von P = (3, 5) auf y² = x³ − 2
    P = (Fraction(3), Fraction(5))
    mult, nP = [], O
    for n in range(1, 31):
        nP = ec_add(nP, P, 0)
        assert nP[1] ** 2 == nP[0] ** 3 - 2
        mult.append((n, height(nP[0]), log(height(nP[0]))))
    ns = np.array([m_[0] for m_ in mult])
    hs = np.array([m_[2] for m_ in mult])
    slope, icpt = np.polyfit(ns[5:] ** 2, hs[5:], 1)

    # unabhängige Suche: x = A/D², A³ − 2D⁶ = B²
    found = []
    for D in range(1, isqrt(20000) + 1):
        A = np.arange(-20000, 20001, dtype=np.int64)
        rhs = A ** 3 - 2 * D ** 6
        ok = rhs >= 0
        B = np.round(np.sqrt(rhs[ok].astype(float))).astype(np.int64)
        for A_, B_ in zip(A[ok][B * B == rhs[ok]], B[B * B == rhs[ok]]):
            if gcd(int(A_), D) == 1:
                found.append((Fraction(int(A_), D * D), Fraction(int(B_), D ** 3)))
    print("Alle Punkte mit H(x) ≤ 20 000 auf y² = x³ − 2 (nur y ≥ 0):", [f"({q[0]}, {q[1]})" for q in found])
    print("Zum Vergleich: x(P) = 3, x(2P) =", ec_add(P, P, 0)[0], ", H(x(3P)) =", mult[2][1])

    # Grad 2: Kreis, acht Punkte pro primitivem Tripel plus (±1, 0), (0, ±1)
    hyp = np.sort(primitive_triples(10 ** 6)[:, 2])
    Cs = np.unique(np.geomspace(1, 10 ** 6, 400).astype(int))
    N_circle = 4 + 8 * np.searchsorted(hyp, Cs, side="right")
    # Grad 3: ±nP mit H(x(nP)) ≤ C
    H_mult = np.array([m_[1] for m_ in mult], dtype=object)
    N_ell = np.array([2 * sum(1 for h_ in H_mult if h_ <= C) for C in Cs])
    # Grad 4: a⁴ + b⁴ = c⁴ mit 0 ≤ a ≤ c ≤ 2000
    quartic = []
    for c in range(1, 2001):
        a = np.arange(0, c + 1, dtype=np.int64)
        b4 = c ** 4 - a ** 4
        b = np.round(b4.astype(float) ** 0.25).astype(np.int64)
        for a_, b_ in zip(a[b ** 4 == b4], b[b ** 4 == b4]):
            if gcd(gcd(int(a_), int(b_)), c) == 1:
                quartic.append((int(a_), int(b_), c))

    fig, axes = plt.subplots(1, 2, figsize=(15, 5.2))
    axes[0].loglog(Cs, N_circle, c="tab:blue", lw=2, label="Kreis x² + y² = 1 (g = 0)")
    axes[0].loglog(Cs, 4 * Cs / np.pi, "--", c="black", lw=0.8, label="4C/π")
    axes[0].loglog(Cs, N_ell, c="tab:orange", lw=2, drawstyle="steps-post", label="y² = x³ − 2 (g = 1, Rang 1)")
    axes[0].loglog(Cs[Cs <= 2000], np.full(np.sum(Cs <= 2000), 4), c="tab:red", lw=2, label="x⁴ + y⁴ = 1 (g = 3), gesucht bis 2000")
    axes[0].set_xlabel("Höhe C")
    axes[0].set_ylabel("Anzahl rationaler Punkte mit Höhe ≤ C")
    axes[0].set_title("Rationale Punkte nach Geschlecht")
    axes[0].legend(fontsize=8)
    axes[1].plot(ns ** 2, hs, "o", c="tab:orange", label="h(x(nP)) = log H(x(nP))")
    axes[1].plot(ns ** 2, slope * ns ** 2 + icpt, c="black", lw=0.8, label=f"Gerade mit Steigung ĥ_x = {slope:.6f}")
    axes[1].set_xlabel("n²")
    axes[1].set_ylabel("logarithmische Höhe")
    axes[1].set_title("Höhe der Vielfachen von P = (3, 5) auf y² = x³ − 2")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()

    for n, H_, h_ in mult[:4] + mult[9:10] + mult[-1:]:
        print(f"n = {n:2d}: H(x(nP)) hat {len(str(H_)):4d} Stellen, h/n² = {h_ / n ** 2:.6f}")
    print(f"Kanonische Höhe aus der Anpassung: ĥ_x(P) = {slope:.6f} (Silverman-Normierung ĥ = {slope / 2:.6f}); "
          f"Abweichung h − ĥ_x n² für n ≥ 6 höchstens {np.max(np.abs(hs[5:] - slope * ns[5:] ** 2)):.3f}")
    print(f"Kreis: N(10⁶) = {N_circle[-1]}, 4C/π = {4e6 / np.pi:.0f};  elliptische Kurve: N(10⁶) = {N_ell[-1]};  "
          f"Quartik: primitive Lösungen von a⁴ + b⁴ = c⁴ mit c ≤ 2000: {quartic}")


def finite_field_curves():
    """45. Elliptische Kurven über endlichen Körpern: Hasse und Sato-Tate (Zellen 27 von quadrics_ellipticcurves.ipynb)."""
    global E61, a, a1, a_p, ap, ax, axes, b, bad, cnt, curves, fig
    global m2, m4, moments, mx, name, orders, p, primes, ps, ps_, pts, xi
    global xn, xx, z, z3
    primes = np.array(list(sp.primerange(5, 30000)))
    curves = {"y² = x³ + x + 1 (ohne CM)": (1, 1), "y² = x³ − x (mit CM)": (-1, 0)}
    ap = {}
    for name, (a, b) in curves.items():
        ps = [p for p in primes if (4 * a ** 3 + 27 * b ** 2) % p != 0]
        ap[name] = (np.array(ps), np.array([p + 1 - ec_count(a, b, p) for p in ps]))

    fig, axes = plt.subplots(1, 4, figsize=(20, 4.8))
    pts = ec_points(2, 3, 97)
    axes[0].plot([q[0] for q in pts[1:]], [q[1] for q in pts[1:]], "o", ms=3.5, c="tab:blue")
    axes[0].axhline(97 / 2, c="grey", lw=0.8, ls=":", label="Symmetrie y ↔ p − y")
    axes[0].set_xlabel("x"); axes[0].set_ylabel("y")
    axes[0].set_title(f"{curve_str(2, 3)} über {field(97)}: {len(pts)} Punkte (mit O)")
    axes[0].legend(fontsize=8, loc="upper right")

    ps, a1 = ap["y² = x³ + x + 1 (ohne CM)"]
    axes[1].plot(ps, a1, ".", ms=1.5, c="tab:blue", label="a_p")
    axes[1].plot(ps, 2 * np.sqrt(ps), c="tab:red", lw=1, label="±2√p")
    axes[1].plot(ps, -2 * np.sqrt(ps), c="tab:red", lw=1)
    axes[1].set_xlabel("Primzahl p"); axes[1].set_ylabel("a_p = p + 1 − #E(𝔽ₚ)")
    axes[1].set_title("Hasse-Schranke, y² = x³ + x + 1")
    axes[1].legend(fontsize=8, loc="lower left")

    xx = np.linspace(-1, 1, 400)
    moments = {}
    for ax, (name, (ps_, a_p)) in zip(axes[2:], ap.items()):
        xn = a_p / (2 * np.sqrt(ps_))
        moments[name] = (np.mean(xn ** 2), np.mean(xn ** 4), np.max(np.abs(xn)), np.mean(a_p == 0),
                         np.mean(a_p[ps_ % 4 == 3] == 0), len(ps_))
        ax.hist(xn, bins=40, range=(-1, 1), density=True, color="tab:blue", alpha=0.7, label="a_p/(2√p)")
        ax.plot(xx, 2 / np.pi * np.sqrt(1 - xx ** 2), c="tab:red", lw=2, label="Sato-Tate: (2/π)√(1 − x²)")
        ax.set_xlabel("x = a_p/(2√p)"); ax.set_ylabel("Dichte")
        ax.set_title(f"{name}, {len(ps_)} Primzahlen")
    xi = np.linspace(-0.995, 0.995, 400)
    axes[3].plot(xi, 0.5 / (np.pi * np.sqrt(1 - xi ** 2)), c="tab:orange", lw=2, label="p ≡ 1 mod 4: ½ · 1/(π√(1 − x²))")
    axes[3].annotate("p ≡ 3 mod 4: a_p = 0\n(halbe Masse, Balken bis Dichte 10)", (0.0, 2.9), xytext=(0.15, 1.9), fontsize=8,
                     arrowprops=dict(arrowstyle="->", color="black"))
    axes[3].set_ylim(0, 3)
    for ax in axes[2:]:
        ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    plt.show()

    for name, (m2, m4, mx, z, z3, cnt) in moments.items():
        print(f"{name:26s}: max |a_p|/(2√p) = {mx:.4f};  ⟨x²⟩ = {m2:.4f} (Sato-Tate 0.25), ⟨x⁴⟩ = {m4:.4f} (0.125);  "
              f"Anteil a_p = 0: {z:.3f}, davon bei p ≡ 3 mod 4: {z3:.3f}")

    a, b, p = 2, 3, 61
    E61 = ec_points(a, b, p)
    bad = sum(ec_add(ec_add(P, Q, a, p), R, a, p) != ec_add(P, ec_add(Q, R, a, p), a, p)
              for P in E61 for Q in E61 for R in E61)
    orders = [ec_order(P, a, p) for P in E61[1:]]
    print(f"{curve_str(a, b)} über {field(p)}: {len(E61)} Punkte, Assoziativität auf allen {len(E61) ** 3} Tripeln, Verstöße: {bad}; "
          f"größte Punktordnung {max(orders)}, die Gruppe ist {'zyklisch' if max(orders) == len(E61) else 'nicht zyklisch'} "
          f"({sp.factorint(len(E61))})")


def ecdh():
    """46. ECDH und das diskrete Logarithmusproblem (Zellen 30 von quadrics_ellipticcurves.ipynb)."""
    global A_pub, B_pub, G, G256, Gs_, N, N256, Nn, Nref, Ns_, Nu, Q
    global _, a, as_, axes, b, bits, bs_, col, dlog_brute, dlog_bsgs, dlog_rho, fig
    global k, k0, k1, k2, means, multiples, name, ops, ops_rho, p, p256, ps_
    global random_prime_order_curve, ref_labels, refs, results, rng9, rows, sa, sb, sc, slopes, t0, t_mul
    rng9 = random.Random(9)

    def random_prime_order_curve(bits, rng):
        """Zufällige Kurve y² = x³ + ax + b über 𝔽ₚ (p mit etwa `bits` Bit) mit Primzahlordnung N ≠ p, und ein Erzeuger G."""
        while True:
            p = int(sp.nextprime(rng.randrange(2 ** (bits - 1), 2 ** bits)))
            a, b = rng.randrange(p), rng.randrange(p)
            if (4 * a ** 3 + 27 * b ** 2) % p == 0:
                continue
            N = ec_count(a, b, p)
            if N == p or not sp.isprime(N):
                continue
            while True:                                           # jeder Punkt ≠ O erzeugt die Gruppe
                x = rng.randrange(p)
                r = (x ** 3 + a * x + b) % p
                if r and pow(r, (p - 1) // 2, p) == 1:
                    return p, a, b, N, (x, int(sp.sqrt_mod(r, p)))

    def dlog_brute(G, Q, a, p):
        R, k = G, 1
        while R != Q:
            R, k = ec_add(R, G, a, p), k + 1
        return k, k - 1

    def dlog_bsgs(G, Q, N, a, p):
        m = isqrt(N - 1) + 1
        table, R = {}, O
        for j in range(m):                                        # Baby Steps jG
            table.setdefault(R, j)
            R = ec_add(R, G, a, p)
        giant, gamma, ops = ec_neg(R, p), Q, m                    # R = mG
        for i in range(m + 1):                                    # Giant Steps Q − imG
            if gamma in table:
                return (i * m + table[gamma]) % N, ops
            gamma, ops = ec_add(gamma, giant, a, p), ops + 1

    def dlog_rho(G, Q, N, a, p, rng, r=20):
        while True:
            cs, ds = [rng.randrange(N) for _ in range(r)], [rng.randrange(N) for _ in range(r)]
            M = [ec_add(ec_mul(c, G, a, p), ec_mul(d, Q, a, p), a, p) for c, d in zip(cs, ds)]
            def step(X, al, be):
                j = 0 if X is O else X[0] % r
                return ec_add(X, M[j], a, p), (al + cs[j]) % N, (be + ds[j]) % N
            al0, be0 = rng.randrange(N), rng.randrange(N)
            X0 = ec_add(ec_mul(al0, G, a, p), ec_mul(be0, Q, a, p), a, p)
            T, H_, ops = (X0, al0, be0), (X0, al0, be0), 0
            while True:                                           # Floyd: Schildkröte ein Schritt, Hase zwei
                T, H_, ops = step(*T), step(*step(*H_)), ops + 3
                if T[0] == H_[0]:
                    break
            if (T[2] - H_[2]) % N:
                return (H_[1] - T[1]) * pow(T[2] - H_[2], -1, N) % N, ops

    # Spielzeug-ECDH
    p, a, b, N, G = random_prime_order_curve(16, rng9)
    sa, sb = rng9.randrange(1, N), rng9.randrange(1, N)
    A_pub, B_pub = ec_mul(sa, G, a, p), ec_mul(sb, G, a, p)
    print(f"Kurve {curve_str(a, b)} über {field(p)}, Ordnung N = {N} (prim), Erzeuger G = {G}")
    print(f"Alice: geheim a = {sa}, öffentlich A = aG = {A_pub}")
    print(f"Bob:   geheim b = {sb}, öffentlich B = bG = {B_pub}")
    print(f"aB = {ec_mul(sa, B_pub, a, p)}, bA = {ec_mul(sb, A_pub, a, p)}, abG = {ec_mul(sa * sb % N, G, a, p)}")

    # Skalierung der Angriffe
    results = {"Durchprobieren": [], "Baby-Step-Giant-Step": [], "Pollard-Rho": []}
    for bits in range(10, 23, 2):
        p, a, b, N, G = random_prime_order_curve(bits, rng9)
        for _ in range(6):
            k = rng9.randrange(1, N)
            Q = ec_mul(k, G, a, p)
            if bits <= 18:
                k0, ops = dlog_brute(G, Q, a, p); assert k0 == k
                results["Durchprobieren"].append((N, ops))
            k1, ops = dlog_bsgs(G, Q, N, a, p); assert k1 == k
            results["Baby-Step-Giant-Step"].append((N, ops))
            k2, ops = dlog_rho(G, Q, N, a, p, rng9); assert k2 == k
            results["Pollard-Rho"].append((N, ops))

    ps_, as_, bs_, Ns_, Gs_ = random_prime_order_curve(7, random.Random(3))
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.6))
    multiples = [ec_mul(k, Gs_, as_, ps_) for k in range(1, Ns_)]
    axes[0].plot([q[0] for q in multiples], [q[1] for q in multiples], c="lightgrey", lw=0.6, zorder=1)
    sc = axes[0].scatter([q[0] for q in multiples], [q[1] for q in multiples], c=np.arange(1, Ns_), cmap="viridis", s=22, zorder=2)
    fig.colorbar(sc, ax=axes[0], label="k")
    axes[0].set_xlabel("x"); axes[0].set_ylabel("y")
    axes[0].set_title(f"Vielfache kG auf {curve_str(as_, bs_)} über {field(ps_)} (N = {Ns_}), in der Reihenfolge von k verbunden", fontsize=9)
    slopes, refs = {}, {"Durchprobieren": lambda N_: N_ / 2, "Baby-Step-Giant-Step": lambda N_: 1.5 * np.sqrt(N_),
                        "Pollard-Rho": lambda N_: 3 * np.sqrt(np.pi * N_ / 2)}
    ref_labels = {"Durchprobieren": "N/2", "Baby-Step-Giant-Step": "1.5 √N (m Baby Steps + im Mittel m/2 Giant Steps)",
                  "Pollard-Rho": "3 √(πN/2) (Floyd: 3 Operationen pro Iteration)"}
    Nref = np.geomspace(500, 5e6, 50)
    for (name, rows), col in zip(results.items(), ["tab:red", "tab:green", "tab:blue"]):
        Nn, ops = np.array(rows, dtype=float).T
        Nu = np.unique(Nn)
        means = np.array([ops[Nn == v].mean() for v in Nu])
        slopes[name] = np.polyfit(np.log(Nu), np.log(means), 1)[0]
        axes[1].loglog(Nn, ops, "o", c=col, ms=3, alpha=0.4)
        axes[1].loglog(Nu, means, "o-", c=col, ms=6, lw=1.5, label=f"{name}: Mittelwerte, Steigung {slopes[name]:.2f}")
        axes[1].loglog(Nref, refs[name](Nref), ":", c=col, lw=1, label=ref_labels[name])
    axes[1].set_xlabel("Gruppenordnung N")
    axes[1].set_ylabel("Gruppenoperationen")
    axes[1].set_title("Aufwand für einen diskreten Logarithmus")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()
    for name, rows in results.items():
        Nn, ops = np.array(rows, dtype=float).T
        print(f"{name:21s}: Steigung der Mittelwerte {slopes[name]:.3f};  gemessen / Vorhersage ({ref_labels[name].split(' (')[0]}) "
              f"im Mittel {np.mean(ops / refs[name](Nn)):.2f} über {len(ops)} Logarithmen")

    # secp256k1 (Bitcoin): y² = x³ + 7 über 𝔽ₚ mit p = 2²⁵⁶ − 2³² − 977
    p256 = 2 ** 256 - 2 ** 32 - 977
    G256 = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
            0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
    N256 = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    print(f"\nsecp256k1: G auf der Kurve: {(G256[1] ** 2 - G256[0] ** 3 - 7) % p256 == 0};  N prim: {sp.isprime(N256)};  "
          f"N·G = O: {ec_mul(N256, G256, 0, p256) is O}")
    sa, sb = rng9.randrange(1, N256), rng9.randrange(1, N256)
    t0 = time.perf_counter()
    A_pub = ec_mul(sa, G256, 0, p256)
    t_mul = time.perf_counter() - t0
    B_pub = ec_mul(sb, G256, 0, p256)
    print(f"Ein Skalarprodukt mit {sa.bit_length()}-Bit-Schlüssel: {sa.bit_length()} Verdopplungen und {bin(sa).count('1')} Additionen, "
          f"{1e3 * t_mul:.1f} ms in reinem Python")
    print(f"Gemeinsames Geheimnis gleich: {ec_mul(sa, B_pub, 0, p256) == ec_mul(sb, A_pub, 0, p256)}")
    ops_rho = np.sqrt(np.pi * N256 / 2)
    print(f"Pollard-Rho bräuchte √(πN/2) = {ops_rho:.2e} Operationen, bei 10¹² Operationen pro Sekunde {ops_rho / 1e12 / 3.156e7:.1e} Jahre")


def shor_dlog():
    """47. Shors Algorithmus für den diskreten Logarithmus auf einer winzigen Kurve (Zellen 33 von quadrics_ellipticcurves.ipynb)."""
    global DFT, F, N, Pg, QFT, Qg, _, aP, as10, ax, axes, bQ
    global bs10, c_meas, extra, fig, group, idx, im, jj, k_secret, label, n0, n_bits
    global on_line, p_c, prob_all, prob_q, prob_uv, ps10, psi, psi_ab, qft_circuit, recovered, rng10, shor_qubit_registers
    global shots, succ, succ_q, tot, total_q, xg, xl, yl
    rng10 = np.random.default_rng(10)

    # kleinste Kurve über 𝔽ₚ (p > 40) mit Primzahlordnung N zwischen 40 und 60
    ps10, as10, bs10, N = next((p, a, b, ec_count(a, b, p)) for p in sp.primerange(41, 200) for a in range(1, p) for b in range(1, p)
                               if (4 * a ** 3 + 27 * b ** 2) % p and 40 <= ec_count(a, b, p) <= 60
                               and sp.isprime(ec_count(a, b, p)) and ec_count(a, b, p) != p)
    group = ec_points(as10, bs10, ps10)
    label = {pt: i for i, pt in enumerate(group)}                 # Index des Punkts im dritten Register
    Pg = group[1]
    k_secret = 29 % N
    Qg = ec_mul(k_secret, Pg, as10, ps10)

    # Schritt 38: Orakel |a⟩|b⟩|0⟩ → |a⟩|b⟩|aP + bQ⟩, Tabelle mit echter Punktaddition
    aP = [ec_mul(i, Pg, as10, ps10) for i in range(N)]
    bQ = [ec_mul(i, Qg, as10, ps10) for i in range(N)]
    F = np.array([[label[ec_add(aP[i], bQ[j], as10, ps10)] for j in range(N)] for i in range(N)])
    psi = np.zeros((N, N, N), dtype=complex)
    psi[np.arange(N)[:, None], np.arange(N)[None, :], F] = 1 / N
    # Schritt 39: drittes Register messen
    p_c = np.sum(np.abs(psi) ** 2, axis=(0, 1))
    c_meas = rng10.choice(N, p=p_c)
    psi_ab = psi[:, :, c_meas] / np.sqrt(p_c[c_meas])
    # Schritt 40: QFT auf beiden Registern, |x⟩ → (1/√N) Σ_y ω^{xy} |y⟩
    idx = np.arange(N)
    QFT = np.exp(2j * np.pi * np.outer(idx, idx) / N) / np.sqrt(N)
    prob_uv = np.abs(QFT @ psi_ab @ QFT.T) ** 2
    prob_all = sum(np.abs(QFT @ psi[:, :, c] @ QFT.T) ** 2 for c in range(N))   # ohne Messung (Spur über das 3. Register)
    # Schritt 41: klassische Nachbearbeitung
    shots = rng10.choice(N * N, size=12, p=prob_uv.ravel() / prob_uv.sum())
    recovered = [(int(s // N), int(s % N), int(s % N) * pow(int(s // N), -1, N) % N if s // N else None) for s in shots]
    on_line = prob_uv[idx, (k_secret * idx) % N].sum()

    # Register aus n Qubits: Q = 2ⁿ Zustände statt N
    def shor_qubit_registers(n_qubits):
        Qr = 2 ** n_qubits
        L = F[np.ix_(np.arange(Qr) % N, np.arange(Qr) % N)]
        prob = np.zeros((Qr, Qr))
        for c in range(N):
            prob += np.abs(np.fft.ifft2(L == c)) ** 2          # Amplitude (1/Q²) Σ ω_Q^{au + bv} über die Klasse c
        uu, vv = np.meshgrid(np.arange(Qr), np.arange(Qr), indexing="ij")
        ut, vt = np.rint(uu * N / Qr).astype(int) % N, np.rint(vv * N / Qr).astype(int) % N
        good = (ut != 0) & ((vt - k_secret * ut) % N == 0)    # Rundung liefert ein Element (u, ku) von H^⊥
        return prob, prob[good].sum(), prob.sum()

    n0 = ceil(np.log2(N))
    prob_q, succ_q, total_q = shor_qubit_registers(n0)

    fig, axes = plt.subplots(1, 4, figsize=(20, 5.0))
    axes[0].imshow(F.T, origin="lower", cmap="viridis", interpolation="nearest")
    axes[0].set_title(f"1. f(a, b) = aP + bQ (Farbe: Index des Punkts)\nKurve {curve_str(as10, bs10)} über {field(ps10)}, N = {N}", fontsize=9)
    axes[1].imshow(np.abs(psi_ab.T) ** 2, origin="lower", cmap="Blues", interpolation="nearest")
    axes[1].set_title(f"2. |ψ(a, b)|² nach der Messung von {group[c_meas]}\neine Nebenklasse von H = ⟨(−k, 1)⟩", fontsize=9)
    axes[2].imshow(prob_uv.T, origin="lower", cmap="Reds", interpolation="nearest")
    axes[2].set_title("3. |ψ̃(u, v)|² nach der QFT auf beiden Registern\nalles Gewicht auf H^⊥ = {(u, k·u mod N)}", fontsize=9)
    im = axes[3].imshow(np.log10(prob_q.T + 1e-12), origin="lower", cmap="magma", vmin=-8, interpolation="nearest")
    jj = np.arange(N)
    axes[3].plot(jj * 2 ** n0 / N, (k_secret * jj % N) * 2 ** n0 / N, "o", mfc="none", mec="cyan", ms=5, mew=0.8)
    fig.colorbar(im, ax=axes[3], label="log₁₀ Wahrscheinlichkeit")
    axes[3].set_title(f"4. Dasselbe mit {n0} Qubits pro Register ({2 ** n0} statt {N} Zustände)\nKreise: ideale Spitzen (jQ/N, (jk mod N)Q/N)", fontsize=9)
    for ax, (xl, yl) in zip(axes, [("a", "b"), ("a", "b"), ("u", "v"), ("u", "v")]):
        ax.set_xlabel(xl); ax.set_ylabel(yl)
    fig.tight_layout()
    plt.show()

    print(f"Kurve {curve_str(as10, bs10)} über {field(ps10)}: N = {N} (prim); P = {Pg}, Q = {Qg}; geheim k = {k_secret}")
    print(f"Gemessen im dritten Register: {group[c_meas]}; Wahrscheinlichkeit auf der Geraden v ≡ k·u: {on_line:.15f}")
    print(f"Verteilung mit und ohne Messung des dritten Registers, größte Differenz: {np.max(np.abs(prob_uv - prob_all)):.1e}")
    print("12 Messungen (u, v) → k = v·u⁻¹ mod N:", ", ".join(f"({u_},{v_})→{kk if kk is not None else '–'}" for u_, v_, kk in recovered))
    print(f"Erfolgswahrscheinlichkeit pro Durchlauf: ideal {1 - prob_uv[0].sum():.4f} (Theorie 1 − 1/N = {1 - 1 / N:.4f})")
    for extra in range(4):
        _, succ, tot = shor_qubit_registers(n0 + extra)
        print(f"  mit {n0 + extra} Qubits pro Register: Erfolg nach Rundung {succ:.4f}  (Gesamtwahrscheinlichkeit {tot:.12f})")

    def qft_circuit(n):
        """Unitärmatrix der QFT-Schaltung: H auf Qubit q, dann R_k von den folgenden Qubits, am Ende Umkehrung (SWAPs)."""
        Hm = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
        U = np.zeros((2 ** n, 2 ** n), dtype=complex)
        for col in range(2 ** n):
            st = np.zeros(2 ** n, dtype=complex)
            st[col] = 1
            st = st.reshape((2,) * n)                              # Achse 0 = höchstwertiges Qubit
            for q in range(n):
                st = np.moveaxis(np.tensordot(Hm, st, axes=([1], [q])), 0, q)
                for m_ in range(q + 1, n):
                    sl = [slice(None)] * n
                    sl[q], sl[m_] = 1, 1
                    st[tuple(sl)] *= np.exp(2j * np.pi / 2 ** (m_ - q + 1))   # kontrolliertes R_k, k = m − q + 1
            U[:, col] = np.transpose(st, list(range(n))[::-1]).reshape(-1)
        return U

    xg = np.arange(2 ** n0)
    DFT = np.exp(2j * np.pi * np.outer(xg, xg) / 2 ** n0) / np.sqrt(2 ** n0)
    print(f"\nQFT-Schaltung mit {n0} Qubits: {n0} Hadamard, {n0 * (n0 - 1) // 2} kontrollierte Phasen, {n0 // 2} SWAPs; "
          f"größte Abweichung von der DFT-Matrix {np.max(np.abs(qft_circuit(n0) - DFT)):.1e}")
    n_bits = 256
    print(f"Für eine 256-Bit-Kurve (Roetteler et al. 2017): {9 * n_bits + 2 * ceil(np.log2(n_bits)) + 10} logische Qubits, "
          f"Toffoli-Gatter höchstens (448 log₂n + 4090) n³ = {(448 * np.log2(n_bits) + 4090) * n_bits ** 3:.2e}; "
          f"die QFT auf {n_bits + 1} Qubits hat dagegen nur {(n_bits + 1) * n_bits // 2:,} kontrollierte Phasen")
