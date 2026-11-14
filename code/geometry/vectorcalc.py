"""Vektoranalysis: Gradient, Divergenz, Rotation, Kurvenintegrale, die Sätze von Green, Gauß und Stokes, krummlinige Koordinaten, Helmholtz-Zerlegung, Laplace-Gleichung, Magnetfeld, Wahrscheinlichkeitsstrom und Berry-Krümmung.

Für geometry.ipynb aus vectorcalculus.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: gradient, div_curl, line_integrals, green, gauss, stokes, curvilinear, identities, helmholtz, laplace_equation, flux_volume, magnetic_field, probability_current, berry_curvature.
"""
import sys
from matplotlib.colors import LogNorm, TwoSlopeNorm, hsv_to_rgb
from scipy.integrate import solve_ivp
from scipy.optimize import fsolve
from scipy.special import i0
import scipy.sparse as sps
import scipy.sparse.linalg as spsl


def gradient():
    """1. Gradient: Höhenlinien, Richtungsableitung, kritische Punkte (Zellen 4, 6 von vectorcalculus.ipynb)."""
    global D_formel, D_quotient, G, H1n, QX, QY, X3, XX, YY, _, alpha, anstieg
    global art, arten, ax, axes, cf, div_num, div_s, e, ew, f1, f1n, fig
    global flaechenintegral, g0, g1n, gauss_legendre, grad_s, h, hoehe, info, kritisch, kurvenintegral, m, np
    global numerisch, ok, p, p0, parametrisierung, plt, richtungen, rng, rot2_num, rot_s, s1, schnuersenkel
    global scipy, sp, sq, u_, v_, x, x0, y, y0, z
    # numpy, scipy, matplotlib und sympy sind in Colab vorinstalliert; installiert wird nichts.
    try:
        import numpy as np
        import scipy
        import sympy as sp
        import matplotlib.pyplot as plt
    except ImportError as e:
        raise ImportError(f"{e.name} fehlt; bitte lokal selbst installieren, am besten mit conda (conda-forge)") from None


    rng = np.random.default_rng(2026)
    x, y, z = sp.symbols("x y z", real=True)
    X3 = (x, y, z)


    def grad_s(f, v=X3):
        """Gradient eines sympy-Skalarfelds."""
        return sp.Matrix([sp.diff(f, q) for q in v])


    def div_s(F, v=X3):
        """Divergenz eines sympy-Vektorfelds."""
        return sp.simplify(sum(sp.diff(F[i], v[i]) for i in range(len(v))))


    def rot_s(F, v=X3):
        """Rotation im ℝ³; in der Ebene (zwei Komponenten) der Skalar ∂x F_y − ∂y F_x."""
        if len(F) == 2:
            return sp.simplify(sp.diff(F[1], v[0]) - sp.diff(F[0], v[1]))
        return sp.Matrix([sp.diff(F[2], v[1]) - sp.diff(F[1], v[2]),
                          sp.diff(F[0], v[2]) - sp.diff(F[2], v[0]),
                          sp.diff(F[1], v[0]) - sp.diff(F[0], v[1])])


    def numerisch(ausdruck, v=X3):
        """sympy-Ausdruck (Skalar oder Vektor) → numpy-Funktion; konstante Komponenten werden auf die Form der
    Argumente gebracht, ein Vektorfeld hat die Form (Komponente, ...)."""
        if isinstance(ausdruck, sp.MatrixBase):
            komponenten = [numerisch(a, v) for a in ausdruck]
            return lambda *args: np.array([k(*args) for k in komponenten])
        f = sp.lambdify(v, ausdruck, "numpy")
        return lambda *args: np.broadcast_to(np.asarray(f(*args), dtype=float), np.broadcast(*args).shape).copy()


    def div_num(F, h):
        """Divergenz auf einem Gitter (indexing="ij", Achse i = Koordinate i) mit zentralen Differenzen."""
        return sum(np.gradient(F[i], h, axis=i) for i in range(len(F)))


    def rot2_num(F, h):
        """Rotation ∂x F_y − ∂y F_x eines ebenen Feldes auf einem Gitter."""
        return np.gradient(F[1], h, axis=0) - np.gradient(F[0], h, axis=1)


    def gauss_legendre(n, a, b):
        t, w = np.polynomial.legendre.leggauss(n)
        return 0.5 * (b - a) * t + 0.5 * (b + a), 0.5 * (b - a) * w


    def kurvenintegral(F, r, dr, a=0.0, b=2 * np.pi, n=400, geschlossen=True):
        """∫ F·dr entlang r(t), t ∈ [a, b]. Geschlossene Kurven mit der Trapezregel (für glatte periodische
    Integranden exponentiell genau), offene mit Gauß–Legendre."""
        if geschlossen:
            t = a + (b - a) * np.arange(n) / n
            w = np.full(n, (b - a) / n)
        else:
            t, w = gauss_legendre(n, a, b)
        return np.sum(np.sum(F(*r(t)) * dr(t), axis=0) * w)


    def flaechenintegral(G, r, ru, rv, ua, ub, va, vb, n=80, periodisch_v=False):
        """Fluss ∬ G·n dA = ∬ G(r(u, v))·(r_u × r_v) du dv über eine parametrisierte Fläche (Gauß–Legendre in u,
    in v auch Trapezregel, wenn die Fläche in v periodisch ist)."""
        u, wu = gauss_legendre(n, ua, ub)
        if periodisch_v:
            v = va + (vb - va) * np.arange(2 * n) / (2 * n)
            wv = np.full(2 * n, (vb - va) / (2 * n))
        else:
            v, wv = gauss_legendre(n, va, vb)
        U, V = np.meshgrid(u, v, indexing="ij")
        normale = np.cross(ru(U, V), rv(U, V), axis=0)
        return np.einsum("kij,kij,i,j->", G(*r(U, V)), normale, wu, wv)


    def parametrisierung(r_sym, u, v):
        """Aus einer symbolischen Parametrisierung r(u, v) die numpy-Funktionen r, r_u, r_v."""
        r_sym = sp.Matrix(r_sym)
        return [numerisch(a, (u, v)) for a in (r_sym, r_sym.diff(u), r_sym.diff(v))]


    def schnuersenkel(xs, ys):
        """Fläche eines Polygons (Gaußsche Trapezformel, „Shoelace“), positiv bei Umlauf gegen den Uhrzeigersinn."""
        return 0.5 * np.sum(xs * np.roll(ys, -1) - np.roll(xs, -1) * ys)

    u_, v_ = sp.symbols("u v", real=True)
    f1 = x * sp.exp(-x**2 - y**2) + (x**2 + y**2) / 20
    f1n = numerisch(f1, (x, y))
    g1n = numerisch(grad_s(f1, (x, y)), (x, y))
    H1n = sp.lambdify((x, y), sp.hessian(f1, (x, y)), "numpy")

    # Kritische Punkte: ∇f = 0 von vielen Startpunkten aus lösen, doppelte entfernen, mit der Hesse-Matrix einordnen
    kritisch = []
    for x0 in np.linspace(-3, 3, 13):
        for y0 in np.linspace(-3, 3, 13):
            p, info, ok, _ = fsolve(lambda q: g1n(*q), [x0, y0], full_output=True)
            if ok == 1 and np.linalg.norm(g1n(*p)) < 1e-10 and not any(np.allclose(p, q, atol=1e-6) for q in kritisch):
                kritisch.append(p)
    kritisch.sort(key=lambda p: p[0])
    arten = []
    for p in kritisch:
        ew = np.linalg.eigvalsh(np.array(H1n(*p), dtype=float))
        arten.append("Minimum" if ew.min() > 0 else "Maximum" if ew.max() < 0 else "Sattel")
        print(f"kritischer Punkt ({p[0]:+.4f}, {p[1]:+.4f}): f = {f1n(*p):+.4f}, "
              f"Eigenwerte der Hesse-Matrix ({ew[0]:+.4f}, {ew[1]:+.4f}) → {arten[-1]}")

    # Entlang (−f_y, f_x), also senkrecht zum Gradienten, bleibt f konstant; entlang ∇f steigt es am schnellsten
    p0 = np.array([0.5, 0.4])
    hoehe = solve_ivp(lambda s, q: np.array([-g1n(*q)[1], g1n(*q)[0]]) / np.linalg.norm(g1n(*q)), (0, 3.2), p0,
                      rtol=1e-11, atol=1e-12, max_step=0.01)
    anstieg = solve_ivp(lambda s, q: g1n(*q), (0, 40), p0, rtol=1e-10, atol=1e-12, max_step=0.05)
    print(f"Höhenlinie durch p0 = (0.5, 0.4), ein Umlauf: größte Abweichung |f − f(p0)| = "
          f"{np.max(np.abs(f1n(*hoehe.y) - f1n(*p0))):.1e}")
    print(f"Gradientenfluss ab p0 endet bei ({anstieg.y[0, -1]:.4f}, {anstieg.y[1, -1]:.4f}), dem Maximum")

    alpha = np.linspace(0, 2 * np.pi, 361)
    richtungen = np.array([np.cos(alpha), np.sin(alpha)])
    h = 1e-5
    D_quotient = (f1n(*(p0[:, None] + h * richtungen)) - f1n(*(p0[:, None] - h * richtungen))) / (2 * h)
    g0 = g1n(*p0)
    D_formel = g0 @ richtungen
    print(f"Richtungsableitung: Differenzenquotient gegen ∇f·u, größte Abweichung {np.max(np.abs(D_quotient - D_formel)):.1e};"
          f" Maximum {D_formel.max():.4f} bei α = {np.degrees(alpha[np.argmax(D_formel)]):.0f}°,"
          f" |∇f| = {np.linalg.norm(g0):.4f} bei arg ∇f = {np.degrees(np.arctan2(g0[1], g0[0])) % 360:.1f}°")

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    ax = axes[0]
    s1 = np.linspace(-3, 3, 301)
    XX, YY = np.meshgrid(s1, s1)
    cf = ax.contourf(XX, YY, f1n(XX, YY), levels=30, cmap="viridis")
    ax.contour(XX, YY, f1n(XX, YY), levels=30, colors="k", linewidths=0.3)
    fig.colorbar(cf, ax=ax, label="f(x, y)")
    sq = np.linspace(-2.8, 2.8, 15)
    QX, QY = np.meshgrid(sq, sq)
    G = g1n(QX, QY)
    ax.quiver(QX, QY, G[0] / np.hypot(*G), G[1] / np.hypot(*G), color="w", scale=30, width=0.003)
    ax.plot(*hoehe.y, color="tab:orange", lw=2.5, label="Höhenlinie durch p0 (senkrecht zu ∇f)")
    ax.plot(*anstieg.y, color="tab:red", lw=2.5, label="Gradientenfluss ab p0 (steilster Anstieg)")
    for p, art, m in zip(kritisch, arten, ["v", "s", "^"]):
        ax.plot(*p, m, color="w", mec="k", ms=10, label=art)
    ax.set_aspect("equal"); ax.set_xlabel("x"); ax.set_ylabel("y"); ax.legend(loc="lower left", fontsize=8)
    ax.set_title("Höhenlinien, Gradientenrichtungen (Pfeile) und kritische Punkte")
    ax = axes[1]
    ax.plot(np.degrees(alpha), D_formel, label="∇f·u (Formel)")
    ax.plot(np.degrees(alpha[::15]), D_quotient[::15], "o", ms=4, label="Differenzenquotient")
    ax.axhline(np.linalg.norm(g0), color="0.5", ls="--", label="±|∇f|")
    ax.axhline(-np.linalg.norm(g0), color="0.5", ls="--")
    ax.set_xlabel("Richtung α von u [Grad]"); ax.set_ylabel("Richtungsableitung D_u f(p0)")
    ax.set_title("Richtungsableitung bei p0 = (0.5, 0.4): ein Kosinus mit Amplitude |∇f|"); ax.legend()
    plt.tight_layout()
    plt.show()


def div_curl():
    """2. Divergenz und Rotation sehen (Zellen 9 von vectorcalculus.ipynb)."""
    global F, Fn, Fs, XX, YY, abw, ax, axes, d_ex, d_num, felder, fig
    global h2, im, name, r_ex, r_num, s2, weg_vom_ursprung
    felder = {
        "Quelle (x, y)": (x, y),
        "Wirbel (−y, x)": (-y, x),
        "Scherung (y, 0)": (y, sp.Integer(0)),
        "Dehnung (x, −y)": (x, -y),
        "Potentialwirbel (−y, x)/r²": (-y / (x**2 + y**2), x / (x**2 + y**2)),
        "Zellen (sin y, sin x)": (sp.sin(y), sp.sin(x)),
    }
    s2 = np.linspace(-2, 2, 200)                                    # gerade Anzahl: kein Gitterpunkt im Ursprung
    h2 = s2[1] - s2[0]
    XX, YY = np.meshgrid(s2, s2, indexing="ij")
    weg_vom_ursprung = np.hypot(XX, YY) > 0.3

    fig, axes = plt.subplots(2, 3, figsize=(16, 10.5))
    for ax, (name, F) in zip(axes.flat, felder.items()):
        Fs = sp.Matrix(F)
        d_ex, r_ex = div_s(Fs, (x, y)), rot_s(Fs, (x, y))
        Fn = numerisch(Fs, (x, y))(XX, YY)
        d_num, r_num = div_num(Fn, h2), rot2_num(Fn, h2)
        abw = max(np.max(np.abs(d_num - numerisch(d_ex, (x, y))(XX, YY))[weg_vom_ursprung]),
                  np.max(np.abs(r_num - numerisch(r_ex, (x, y))(XX, YY))[weg_vom_ursprung]))
        print(f"{name:28s} div = {str(d_ex):12s} rot = {str(r_ex):16s} Gitter gegen exakt (r > 0.3): {abw:.1e}")
        im = ax.pcolormesh(s2, s2, np.clip(r_num, -3, 3).T, cmap="RdBu_r", norm=TwoSlopeNorm(0, -3, 3), shading="auto")
        ax.streamplot(s2, s2, Fn[0].T, Fn[1].T, color="k", density=1.1, linewidth=0.7, arrowsize=0.9)
        ax.set_xlim(-2, 2); ax.set_ylim(-2, 2)
        ax.set_aspect("equal"); ax.set_xlabel("x"); ax.set_ylabel("y")
        ax.set_title(f"{name}\ndiv = {d_ex},  rot = {r_ex}", fontsize=10)
    fig.colorbar(im, ax=axes, shrink=0.6, label="Rotation ∂x F_y − ∂y F_x")
    plt.show()


def line_integrals():
    """3. Kurvenintegrale: Arbeit, Wegunabhängigkeit und der Wirbel um ein Loch (Zellen 12 von vectorcalculus.ipynb)."""
    global F3, G3, V3, Vb, W_F, W_G, XX, YY, ax, axes, cs, dr
    global fig, name, phi3, r, s3, s3b, schleifen, tt, wege
    phi3 = x**2 * y + sp.sin(y)
    F3 = numerisch(grad_s(phi3, (x, y)), (x, y))
    G3 = lambda X, Y: np.array([-Y, X])
    V3 = lambda X, Y: np.array([-Y, X]) / (X**2 + Y**2)

    wege = {   # t ∈ [0, 1], alle von (0, 0) nach (1, 2)
        "Gerade": (lambda t: np.array([t, 2 * t]), lambda t: np.array([np.ones_like(t), 2 * np.ones_like(t)])),
        "Parabel": (lambda t: np.array([t, 2 * t**2]), lambda t: np.array([np.ones_like(t), 4 * t])),
        "Schleife": (lambda t: np.array([t + 0.7 * np.sin(2 * np.pi * t), 2 * t**2 + 0.9 * np.sin(np.pi * t)]),
                     lambda t: np.array([1 + 1.4 * np.pi * np.cos(2 * np.pi * t), 4 * t + 0.9 * np.pi * np.cos(np.pi * t)])),
    }
    print(f"φ(1, 2) − φ(0, 0) = 2 + sin 2 = {2 + np.sin(2):.10f}")
    for name, (r, dr) in wege.items():
        W_F = kurvenintegral(F3, r, dr, 0, 1, n=60, geschlossen=False)
        W_G = kurvenintegral(G3, r, dr, 0, 1, n=60, geschlossen=False)
        print(f"{name:9s} ∫∇φ·dr = {W_F:.10f}   ∫(−y, x)·dr = {W_G:+.6f}")

    schleifen = {   # t ∈ [0, 2π)
        "Kreis r = 1 um 0": (lambda t: np.array([np.cos(t), np.sin(t)]), lambda t: np.array([-np.sin(t), np.cos(t)])),
        "Ellipse um 0, verschoben": (lambda t: np.array([0.3 + 1.5 * np.cos(t), -0.2 + 0.8 * np.sin(t)]),
                                     lambda t: np.array([-1.5 * np.sin(t), 0.8 * np.cos(t)])),
        "Kreis um (2, 0), r = 0.7": (lambda t: np.array([2 + 0.7 * np.cos(t), 0.7 * np.sin(t)]),
                                     lambda t: np.array([-0.7 * np.sin(t), 0.7 * np.cos(t)])),
        "zweimal um 0": (lambda t: 1.3 * np.array([np.cos(2 * t), np.sin(2 * t)]),
                         lambda t: 2.6 * np.array([-np.sin(2 * t), np.cos(2 * t)])),
        "Kreis um 0 im Uhrzeigersinn": (lambda t: 0.6 * np.array([np.cos(t), -np.sin(t)]),
                                        lambda t: 0.6 * np.array([-np.sin(t), -np.cos(t)])),
    }
    for name, (r, dr) in schleifen.items():
        print(f"Potentialwirbel, {name:28s}: ∮ F·dr / 2π = {round(kurvenintegral(V3, r, dr, n=400) / (2 * np.pi), 12) + 0.0:+.12f}")

    fig, axes = plt.subplots(1, 2, figsize=(15, 6.3))
    ax = axes[0]
    s3 = np.linspace(-1, 2.6, 300)
    XX, YY = np.meshgrid(s3, s3)
    cs = ax.contourf(XX, YY, numerisch(phi3, (x, y))(XX, YY), levels=25, cmap="viridis")
    fig.colorbar(cs, ax=ax, label="Potential φ = x²y + sin y")
    tt = np.linspace(0, 1, 300)
    for name, (r, dr) in wege.items():
        ax.plot(*r(tt), lw=2.5, label=name)
    ax.plot([0, 1], [0, 2], "wo", mec="k")
    ax.set_aspect("equal"); ax.set_xlabel("x"); ax.set_ylabel("y"); ax.legend()
    ax.set_title("Drei Wege von (0, 0) nach (1, 2): ∫∇φ·dr ist immer φ(1, 2) − φ(0, 0)")
    ax = axes[1]
    s3b = np.linspace(-2.2, 3.0, 200)
    Vb = V3(*np.meshgrid(s3b, s3b))
    ax.streamplot(s3b, s3b, Vb[0], Vb[1], color="0.6", density=1.0, linewidth=0.6)
    tt = np.linspace(0, 2 * np.pi, 400)
    for name, (r, dr) in schleifen.items():
        ax.plot(*r(tt), lw=2, label=f"{name}: {int(np.rint(kurvenintegral(V3, r, dr) / (2 * np.pi))):+d}·2π")
    ax.plot(0, 0, "k*", ms=12)
    ax.set_aspect("equal"); ax.set_xlabel("x"); ax.set_ylabel("y"); ax.legend(fontsize=8, loc="upper right")
    ax.set_title("Potentialwirbel (−y, x)/r²: Zirkulation = 2π · Umlaufzahl um den Ursprung")
    plt.tight_layout()
    plt.show()


def green():
    """4. Satz von Green: die Fläche aus dem Rand (Zellen 15 von vectorcalculus.ipynb)."""
    global A_exakt, F4, Fb, Ns, P4, Q4, XX, YY, ax, axes, blume, dblume
    global div4, fehler_polygon, fehler_trapez, fig, flaeche_polar, flaechenfeld, im, normal_feld, rho4, rot4, s4, tt
    rho4 = lambda t: np.exp(0.5 * np.cos(3 * t))
    blume = lambda t: rho4(t) * np.array([np.cos(t), np.sin(t)])
    dblume = lambda t: rho4(t) * np.array([-1.5 * np.sin(3 * t) * np.cos(t) - np.sin(t),
                                           -1.5 * np.sin(3 * t) * np.sin(t) + np.cos(t)])
    A_exakt = np.pi * i0(1.0)
    flaechenfeld = lambda X, Y: 0.5 * np.array([-Y, X])            # ½ ∮ (x dy − y dx), Rotation 1
    Ns = np.arange(6, 121, 6)                                      # Vielfache von 6, wegen der dreizähligen Symmetrie
    fehler_trapez = [abs(kurvenintegral(flaechenfeld, blume, dblume, n=N) - A_exakt) for N in Ns]
    fehler_polygon = [abs(schnuersenkel(*blume(2 * np.pi * np.arange(N) / N)) - A_exakt) for N in Ns]
    print(f"Fläche der Blume: exakt π I₀(1) = {A_exakt:.12f}; Trapezregel N = 40: {kurvenintegral(flaechenfeld, blume, dblume, n=40):.12f};"
          f" Polygon N = 40: {schnuersenkel(*blume(2 * np.pi * np.arange(40) / 40)):.12f}")


    def flaeche_polar(g, rho, n_phi=400, n_r=40):
        """∬ g dA über das sternförmige Gebiet 0 ≤ r ≤ ρ(φ) (Trapezregel in φ, Gauß–Legendre in r)."""
        phi = 2 * np.pi * np.arange(n_phi) / n_phi
        t, w = np.polynomial.legendre.leggauss(n_r)
        R = rho(phi)[None, :] * 0.5 * (t[:, None] + 1)
        W = 0.5 * rho(phi)[None, :] * w[:, None]
        return np.sum(g(R * np.cos(phi), R * np.sin(phi)) * R * W) * 2 * np.pi / n_phi


    P4, Q4 = x * y - y**3, x**3 + x * sp.sin(y)
    F4 = numerisch(sp.Matrix([P4, Q4]), (x, y))
    rot4 = numerisch(rot_s(sp.Matrix([P4, Q4]), (x, y)), (x, y))
    div4 = numerisch(div_s(sp.Matrix([P4, Q4]), (x, y)), (x, y))
    normal_feld = lambda X, Y: np.array([-F4(X, Y)[1], F4(X, Y)[0]])  # F·n ds = P dy − Q dx
    print(f"rot F = {rot_s(sp.Matrix([P4, Q4]), (x, y))}:  ∮ F·dr = {kurvenintegral(F4, blume, dblume):.12f},"
          f"  ∬ rot F dA = {flaeche_polar(rot4, rho4):.12f}")
    print(f"div F = {div_s(sp.Matrix([P4, Q4]), (x, y))}:  ∮ F·n ds = {kurvenintegral(normal_feld, blume, dblume):.12f},"
          f"  ∬ div F dA = {flaeche_polar(div4, rho4):.12f}")

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    ax = axes[0]
    s4 = np.linspace(-2, 2, 300)
    XX, YY = np.meshgrid(s4, s4)
    im = ax.pcolormesh(s4, s4, rot4(XX, YY), cmap="RdBu_r", norm=TwoSlopeNorm(0), shading="auto")
    fig.colorbar(im, ax=ax, label="rot F = ∂x Q − ∂y P")
    Fb = F4(XX, YY)
    ax.streamplot(s4, s4, Fb[0], Fb[1], color="k", density=1.0, linewidth=0.6)
    tt = np.linspace(0, 2 * np.pi, 400)
    ax.plot(*blume(tt), color="tab:green", lw=3, label="Rand der Blume ρ = e^(0.5 cos 3t)")
    ax.plot(*blume(2 * np.pi * np.arange(12) / 12), "o--", color="tab:orange", label="eingeschriebenes Polygon, N = 12")
    ax.set_aspect("equal"); ax.set_xlabel("x"); ax.set_ylabel("y"); ax.legend(loc="lower left", fontsize=8)
    ax.set_title("F = (xy − y³, x³ + x sin y) und das Gebiet")
    ax = axes[1]
    ax.semilogy(Ns, np.maximum(fehler_trapez, 1e-17), "o-", ms=3, label="Trapezregel für ½∮(x dy − y dx)")
    ax.semilogy(Ns, fehler_polygon, "s-", ms=3, label="eingeschriebenes Polygon (Shoelace)")
    ax.semilogy(Ns, 20 / Ns.astype(float) ** 2, "k:", label="∝ N⁻²")
    ax.set_xlabel("Zahl der Punkte N auf dem Rand"); ax.set_ylabel("Fehler der Fläche")
    ax.set_title("Fläche aus dem Rand: exponentielle gegen quadratische Konvergenz"); ax.legend()
    plt.tight_layout()
    plt.show()


def gauss():
    """5. Gaußscher Integralsatz: der Fluss einer Punktladung (Zellen 18 von vectorcalculus.ipynb)."""
    global E_xz, F5, M, R, XX, ZZ, ax, axes, coulomb, d, dipol, farbe
    global fehler, fig, fluss_kugel, fluss_wuerfel, kugel, kugeln, minus, name, ns, ph_, plus, r0
    global s5, th_, tt, wert
    th_, ph_ = sp.symbols("theta phi", real=True)
    kugel = parametrisierung([sp.sin(th_) * sp.cos(ph_), sp.sin(th_) * sp.sin(ph_), sp.cos(th_)], th_, ph_)  # r_θ × r_φ nach außen


    def coulomb(r0, q=1.0):
        def E(X, Y, Z):
            d = np.array([X - r0[0], Y - r0[1], Z - r0[2]])
            return q * d / np.sum(d**2, axis=0) ** 1.5
        return E


    def fluss_kugel(G, M=(0, 0, 0), R=1.0, n=80):
        """Fluss durch die Kugel um M mit Radius R (nach außen orientiert)."""
        r, ru, rv = kugel
        verschoben = lambda U, V: np.array(M, dtype=float)[:, None, None] + R * r(U, V)
        return flaechenintegral(G, verschoben, lambda U, V: R * ru(U, V), lambda U, V: R * rv(U, V),
                                0, np.pi, 0, 2 * np.pi, n=n, periodisch_v=True)


    def fluss_wuerfel(G, n=40):
        """Fluss durch die Oberfläche des Würfels [−1, 1]³ (nach außen orientiert)."""
        t, w = gauss_legendre(n, -1, 1)
        U, V = np.meshgrid(t, t, indexing="ij")
        gesamt = 0.0
        for a in range(3):
            for s in (-1.0, 1.0):
                P = [None] * 3
                P[a], P[(a + 1) % 3], P[(a + 2) % 3] = np.full_like(U, s), U, V
                gesamt += s * np.sum(G(*P)[a] * np.outer(w, w))
        return gesamt


    for name, r0 in [("im Mittelpunkt", (0, 0, 0)), ("bei (0.3, 0.2, 0.1)", (0.3, 0.2, 0.1)),
                     ("bei (0, 0, 0.9), nahe am Rand", (0, 0, 0.9)), ("bei (0, 0, 1.5), außen", (0, 0, 1.5))]:
        print(f"Ladung {name:30s}: Fluss/4π durch die Einheitskugel {round(fluss_kugel(coulomb(r0), n=120) / (4 * np.pi), 10) + 0.0:+.10f},"
              f" durch den Würfel [−1, 1]³ {round(fluss_wuerfel(coulomb(r0), n=120) / (4 * np.pi), 10) + 0.0:+.10f}")

    # Der Satz selbst für ein glattes Feld: F = (x³, y³, z³), div F = 3(x² + y² + z²)
    F5 = lambda X, Y, Z: np.array([X**3, Y**3, Z**3])
    print(f"F = (x³, y³, z³): Fluss durch die Einheitskugel {fluss_kugel(F5, n=20):.12f}, ∫div F dV = 12π/5 = {12 * np.pi / 5:.12f};"
          f" durch den Würfel {fluss_wuerfel(F5, n=10):.12f}, ∫div F dV = 24")

    # Dipol: Kugeln um die positive, um die negative und um beide Ladungen
    plus, minus = (-0.6, 0, 0), (0.6, 0, 0)
    dipol = lambda X, Y, Z: coulomb(plus, 1)(X, Y, Z) + coulomb(minus, -1)(X, Y, Z)
    kugeln = {"um +": (plus, 0.4), "um −": (minus, 0.4), "um beide": ((0, 0, 0), 1.3)}
    for name, (M, R) in kugeln.items():
        print(f"Dipol, Kugel {name:9s}: Fluss/4π = {round(fluss_kugel(dipol, M, R, n=120) / (4 * np.pi), 10) + 0.0:+.10f}")

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    ax = axes[0]
    ns = np.arange(4, 161, 4)
    for d in [0.7, 0.3, 0.1, 0.03]:
        fehler = [abs(fluss_kugel(coulomb((0, 0, 1 - d)), n=n) - 4 * np.pi) / (4 * np.pi) for n in ns]
        ax.semilogy(ns, np.maximum(fehler, 1e-17), "o-", ms=3, label=f"Abstand zur Oberfläche {d}")
    ax.set_xlabel("Stützstellen n pro Richtung (θ: n, φ: 2n)"); ax.set_ylabel("relativer Fehler des Flusses")
    ax.set_title("Fluss durch die Einheitskugel: je näher die Ladung, desto mehr Stützstellen"); ax.legend()
    ax = axes[1]
    s5 = np.linspace(-2, 2, 300)
    XX, ZZ = np.meshgrid(s5, s5)
    E_xz = dipol(XX, np.zeros_like(XX), ZZ)
    ax.streamplot(s5, s5, E_xz[0], E_xz[2], color=np.log10(np.hypot(E_xz[0], E_xz[2])), cmap="viridis",
                  density=1.4, linewidth=0.8)
    tt = np.linspace(0, 2 * np.pi, 200)
    for (name, (M, R)), farbe in zip(kugeln.items(), ["tab:red", "tab:blue", "tab:green"]):
        wert = round(fluss_kugel(dipol, M, R, n=120) / (4 * np.pi), 6) + 0.0
        ax.plot(M[0] + R * np.cos(tt), M[2] + R * np.sin(tt), color=farbe, lw=2.5, label=f"Kugel {name}: Fluss = {wert:+.0f}·4π")
    ax.plot(plus[0], plus[2], "o", color="tab:red", ms=9); ax.plot(minus[0], minus[2], "o", color="tab:blue", ms=9)
    ax.set_aspect("equal"); ax.set_xlabel("x"); ax.set_ylabel("z"); ax.legend(loc="lower left", fontsize=8)
    ax.set_title("Dipol in der xz-Ebene (Farbe: log₁₀|E|) und drei Kugeln")
    plt.tight_layout()
    plt.show()


def stokes():
    """6. Satz von Stokes: ein Rand, viele Flächen (Zellen 21 von vectorcalculus.ipynb)."""
    global F6, F6n, P, U, V, a, ax, b, dkreis3, erster, fig, flaechen
    global k, kreis3, name, r, r_sym, rh_, rotF6, rotF6n, tt, werte, zirkulation
    F6 = sp.Matrix([y * z - y**3, x**3 + x * z**2, sp.exp(x * y)])
    rotF6 = rot_s(F6)
    print("rot F =", list(rotF6), "  div rot F =", div_s(rotF6))
    F6n, rotF6n = numerisch(F6), numerisch(rotF6)
    kreis3 = lambda t: np.array([np.cos(t), np.sin(t), np.zeros_like(t)])
    dkreis3 = lambda t: np.array([-np.sin(t), np.cos(t), np.zeros_like(t)])
    zirkulation = kurvenintegral(F6n, kreis3, dkreis3, n=200)
    print(f"Zirkulation entlang des Einheitskreises: {zirkulation:.12f}  (3π/2 = {1.5 * np.pi:.12f})")

    rh_ = sp.symbols("rho", positive=True)
    flaechen = {    # Parametrisierung, Bereich des ersten Parameters; der zweite ist der Winkel φ ∈ [0, 2π)
        "Kreisscheibe": ([rh_ * sp.cos(ph_), rh_ * sp.sin(ph_), 0], (0, 1)),
        "Halbkugel": ([sp.sin(th_) * sp.cos(ph_), sp.sin(th_) * sp.sin(ph_), sp.cos(th_)], (0, np.pi / 2)),
        "Paraboloid z = 2(1 − ρ²)": ([rh_ * sp.cos(ph_), rh_ * sp.sin(ph_), 2 * (1 - rh_**2)], (0, 1)),
        "Schale z = −1.5(1 − ρ²)": ([rh_ * sp.cos(ph_), rh_ * sp.sin(ph_), -1.5 * (1 - rh_**2)], (0, 1)),
        "verbeulte Kappe": ([rh_ * sp.cos(ph_), rh_ * sp.sin(ph_), (1 - rh_**2) * (0.6 + 3 * rh_**3 * sp.sin(3 * ph_))], (0, 1)),
    }
    werte = {}
    for name, (r_sym, (a, b)) in flaechen.items():
        erster = th_ if name == "Halbkugel" else rh_
        werte[name] = flaechenintegral(rotF6n, *parametrisierung(r_sym, erster, ph_), a, b, 0, 2 * np.pi, n=60, periodisch_v=True)
        print(f"{name:26s}: Fluss von rot F = {werte[name]:.12f}")
    print(f"geschlossene Einheitskugel  : Fluss von rot F = {fluss_kugel(rotF6n, n=60):+.1e}")

    fig = plt.figure(figsize=(17, 4.6))
    for k, (name, (r_sym, (a, b))) in enumerate(flaechen.items()):
        ax = fig.add_subplot(1, 5, k + 1, projection="3d")
        erster = th_ if name == "Halbkugel" else rh_
        r = parametrisierung(r_sym, erster, ph_)[0]
        U, V = np.meshgrid(np.linspace(a, b, 30), np.linspace(0, 2 * np.pi, 60), indexing="ij")
        P = r(U, V)
        ax.plot_surface(*P, color="tab:cyan", alpha=0.55, edgecolor="0.4", linewidth=0.1)
        tt = np.linspace(0, 2 * np.pi, 200)
        ax.plot(*kreis3(tt), color="tab:red", lw=2.5)
        ax.set_zlim(-1.5, 2); ax.set_zticks([-1, 0, 1, 2]); ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z")
        ax.set_title(f"{name}\nFluss von rot F = {werte[name]:.6f}", fontsize=9)
    fig.suptitle(f"Fünf Flächen mit demselben Rand (rot); Zirkulation entlang des Randes = {zirkulation:.6f}")
    plt.tight_layout()
    plt.show()


def curvilinear():
    """7. Krummlinige Koordinaten (Zellen 24 von vectorcalculus.ipynb)."""
    global Jac, R7, XX, X_kugel, Y21, YY, ZZ, abw7, ax, axes, div_k, div_z
    global f7, fig, grad_k, grad_z, h7, innen, lap7, lap_k, lap_kart, lap_z, n_, nach_kugel
    global operatoren, p_, pp, px, py, pz_, r_, rot_k, rot_z, rr, rz_, s7
    global strahl, t_, tt, u7, zz_
    r_, t_, p_ = sp.symbols("r theta phi", positive=True)
    rz_, pz_, zz_ = sp.symbols("rho phi z", real=True)


    def operatoren(q, h):
        """grad, div, rot, Δ in orthogonalen Koordinaten q mit Skalenfaktoren h (Komponenten in der Basis e_q)."""
        J = h[0] * h[1] * h[2]
        grad = lambda f: sp.Matrix([sp.diff(f, q[i]) / h[i] for i in range(3)])
        div = lambda F: sp.simplify(sum(sp.diff(J / h[i] * F[i], q[i]) for i in range(3)) / J)
        rot = lambda F: sp.Matrix([(sp.diff(h[2] * F[2], q[1]) - sp.diff(h[1] * F[1], q[2])) / (h[1] * h[2]),
                                   (sp.diff(h[0] * F[0], q[2]) - sp.diff(h[2] * F[2], q[0])) / (h[2] * h[0]),
                                   (sp.diff(h[1] * F[1], q[0]) - sp.diff(h[0] * F[0], q[1])) / (h[0] * h[1])]).applyfunc(sp.simplify)
        lap = lambda f: sp.simplify(div(grad(f)))
        return grad, div, rot, lap


    # Skalenfaktoren aus der Abbildung (r, θ, φ) → (x, y, z): Metrik g_ij = ∂_i X · ∂_j X
    X_kugel = sp.Matrix([r_ * sp.sin(t_) * sp.cos(p_), r_ * sp.sin(t_) * sp.sin(p_), r_ * sp.cos(t_)])
    Jac = X_kugel.jacobian([r_, t_, p_])
    print("Metrik in Kugelkoordinaten:", sp.simplify(Jac.T * Jac).tolist(), "  det der Jacobi-Matrix:", sp.simplify(Jac.det()))
    grad_k, div_k, rot_k, lap_k = operatoren((r_, t_, p_), (1, r_, r_ * sp.sin(t_)))
    grad_z, div_z, rot_z, lap_z = operatoren((rz_, pz_, zz_), (1, rz_, 1))

    nach_kugel = {x: X_kugel[0], y: X_kugel[1], z: X_kugel[2]}
    f7 = x**2 * y * z + z**3 + sp.exp(x) * y
    lap_kart = sum(sp.diff(f7, q, 2) for q in X3)
    print("Δf kartesisch gegen Kugelformel, f = x²yz + z³ + eˣy:  Differenz =",
          sp.simplify(lap_k(f7.subs(nach_kugel)) - lap_kart.subs(nach_kugel)))
    n_ = sp.symbols("n")
    print("Δ rⁿ =", sp.factor(lap_k(r_**n_)), "  Δ(1/r) =", lap_k(1 / r_), "  div(e_r/r²) =", div_k([1 / r_**2, 0, 0]))
    Y21 = sp.expand_func(sp.Ynm(2, 1, t_, p_))
    print("Δ(r² Y₂¹) =", lap_k(r_**2 * Y21), "  r² ΔY₂¹ / Y₂¹ =", sp.simplify(lap_k(Y21) * r_**2 / Y21), "= −l(l + 1) mit l = 2")
    print("Zylinder: rot(e_φ/ρ) =", list(rot_z([0, 1 / rz_, 0])), " div(e_ρ/ρ) =", div_z([1 / rz_, 0, 0]),
          " Δ ln ρ =", lap_z(sp.log(rz_)), " rot(starre Drehung ωρ e_φ) =", list(rot_z([0, sp.Symbol("omega") * rz_, 0])))

    # Numerisch: Δ e^(−r²) auf einem kartesischen Gitter (7-Punkte-Stern) gegen (4r² − 6) e^(−r²)
    s7 = np.linspace(-3, 3, 121)
    h7 = s7[1] - s7[0]
    XX, YY, ZZ = np.meshgrid(s7, s7, s7, indexing="ij")
    u7 = np.exp(-(XX**2 + YY**2 + ZZ**2))
    lap7 = sum(np.roll(u7, -1, a) - 2 * u7 + np.roll(u7, 1, a) for a in range(3)) / h7**2
    R7 = np.sqrt(XX**2 + YY**2 + ZZ**2)
    innen = (np.abs(XX) < 2.9) & (np.abs(YY) < 2.9) & (np.abs(ZZ) < 2.9)
    abw7 = np.max(np.abs(lap7 - (4 * R7**2 - 6) * u7)[innen])
    print(f"Δ e^(−r²): 7-Punkte-Stern (h = {h7:.3f}) gegen Kugelformel, größte Abweichung {abw7:.1e}")

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    ax = axes[0]
    for rr in [0.5, 1.0, 1.5, 2.0]:
        tt = np.linspace(0, 2 * np.pi, 200)
        ax.plot(rr * np.cos(tt), rr * np.sin(tt), color="0.75", lw=0.8)
    for pp in np.linspace(0, 2 * np.pi, 12, endpoint=False):
        ax.plot([0, 2.2 * np.cos(pp)], [0, 2.2 * np.sin(pp)], color="0.75", lw=0.8)
    for rr in [0.5, 1.0, 1.5, 2.0]:
        for pp in np.linspace(0, 2 * np.pi, 8, endpoint=False):
            px, py = rr * np.cos(pp), rr * np.sin(pp)
            ax.arrow(px, py, 0.25 * np.cos(pp), 0.25 * np.sin(pp), head_width=0.05, color="tab:red")
            ax.arrow(px, py, -0.25 * np.sin(pp), 0.25 * np.cos(pp), head_width=0.05, color="tab:blue")
    ax.plot([], [], color="tab:red", label="e_r (radial)"); ax.plot([], [], color="tab:blue", label="e_φ (tangential)")
    ax.set_aspect("equal"); ax.set_xlabel("x"); ax.set_ylabel("y"); ax.legend(loc="upper right")
    ax.set_title("Polarkoordinaten: die Basisvektoren drehen sich mit dem Ort")
    ax = axes[1]
    strahl = (np.abs(YY) < 1e-9) & (np.abs(ZZ) < 1e-9) & (XX >= 0)
    rr = np.linspace(0, 3, 300)
    ax.plot(rr, (4 * rr**2 - 6) * np.exp(-rr**2), label="f'' + (2/r) f' = (4r² − 6) e^(−r²)")
    ax.plot(XX[strahl], lap7[strahl], "o", ms=4, label=f"7-Punkte-Stern auf dem Gitter, h = {h7:.2f}")
    ax.set_xlabel("r"); ax.set_ylabel("Δ e^(−r²)"); ax.legend()
    ax.set_title("Laplace-Operator einer radialen Funktion: Kugelformel gegen Gitter")
    plt.tight_layout()
    plt.show()


def identities():
    """8. Die Identitäten $\\nabla\\times\\nabla f = 0$ und $\\nabla\\cdot(\\nabla\\times\\mathbf A) = 0$, auch auf dem Gitter (Zellen 27 von vectorcalculus.ipynb)."""
    global A8, A_g, D, D2, XX, YY, ZZ, ax, divA, f8, f_g, fig
    global gdivA, grad_f, h8, hs, identitaeten, lap_vec, m, n, name, ns8, rest, reste
    global rot_D, rrA, s8, werte8
    f8 = sp.Function("f")(x, y, z)
    A8 = sp.Matrix([sp.Function(f"A_{i}")(x, y, z) for i in "xyz"])
    lap_vec = lambda A: sp.Matrix([sum(sp.diff(a, q, 2) for q in X3) for a in A])
    identitaeten = {
        "rot grad f": rot_s(grad_s(f8)),
        "div rot A": div_s(rot_s(A8)),
        "rot rot A − (grad div A − ΔA)": rot_s(rot_s(A8)) - (grad_s(div_s(A8)) - lap_vec(A8)),
        "div(fA) − (∇f·A + f div A)": div_s(f8 * A8) - (grad_s(f8).dot(A8) + f8 * div_s(A8)),
        "rot(fA) − (∇f × A + f rot A)": rot_s(f8 * A8) - (grad_s(f8).cross(A8) + f8 * rot_s(A8)),
    }
    for name, rest in identitaeten.items():
        rest = sp.simplify(rest)
        print(f"{name:32s} = {list(rest) if isinstance(rest, sp.MatrixBase) else rest}")


    def D(u, a, h):    # zentrale Differenz entlang Achse a, periodisch
        return (np.roll(u, -1, a) - np.roll(u, 1, a)) / (2 * h)


    def D2(u, a, h):   # 3-Punkte-Stern für die zweite Ableitung
        return (np.roll(u, -1, a) - 2 * u + np.roll(u, 1, a)) / h**2


    def rot_D(A, h):
        return np.array([D(A[2], 1, h) - D(A[1], 2, h), D(A[0], 2, h) - D(A[2], 0, h), D(A[1], 0, h) - D(A[0], 1, h)])


    reste = {k: [] for k in ["rot grad f", "div rot A", "rot rot A − (grad div A − Σ DᵢDᵢ A)", "rot rot A − (grad div A − Δ₃ A)"]}
    ns8 = [12, 24, 48, 96]
    for n in ns8:
        s8 = 2 * np.pi * np.arange(n) / n
        h8 = s8[1]
        XX, YY, ZZ = np.meshgrid(s8, s8, s8, indexing="ij")
        f_g = np.cos(XX) * np.sin(2 * YY) + np.sin(ZZ) * np.cos(XX)
        A_g = np.array([np.sin(YY + ZZ) + np.sin(XX) * np.cos(YY), np.cos(ZZ) * np.sin(2 * XX) + np.sin(YY) ** 2,
                        np.sin(XX) * np.cos(YY) + np.cos(ZZ) * np.sin(XX)])
        grad_f = np.array([D(f_g, a, h8) for a in range(3)])
        divA = sum(D(A_g[a], a, h8) for a in range(3))
        gdivA = np.array([D(divA, a, h8) for a in range(3)])
        rrA = rot_D(rot_D(A_g, h8), h8)
        reste["rot grad f"].append(np.max(np.abs(rot_D(grad_f, h8))))
        reste["div rot A"].append(np.max(np.abs(sum(D(rot_D(A_g, h8)[a], a, h8) for a in range(3)))))
        reste["rot rot A − (grad div A − Σ DᵢDᵢ A)"].append(
            np.max(np.abs(rrA - gdivA + np.array([sum(D(D(A_g[c], a, h8), a, h8) for a in range(3)) for c in range(3)]))))
        reste["rot rot A − (grad div A − Δ₃ A)"].append(
            np.max(np.abs(rrA - gdivA + np.array([sum(D2(A_g[c], a, h8) for a in range(3)) for c in range(3)]))))
    for name, werte8 in reste.items():
        print(f"Gitter: {name:40s}", "  ".join(f"n={n}: {w:.1e}" for n, w in zip(ns8, werte8)))

    fig, ax = plt.subplots(figsize=(8, 5.5))
    hs = 2 * np.pi / np.array(ns8)
    for (name, werte8), m in zip(reste.items(), "osD^"):
        ax.loglog(hs, np.maximum(werte8, 1e-17), m + "-", label=name)
    ax.loglog(hs, 3 * hs**2, "k:", label="∝ h²")
    ax.set_xlabel("Gitterweite h"); ax.set_ylabel("größter Rest auf dem Gitter")
    ax.set_title("Identitäten auf dem Gitter: was nur auf vertauschbaren Ableitungen beruht, bleibt exakt")
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()


def helmholtz():
    """9. Helmholtz-Zerlegung mit der FFT (Zellen 30 von vectorcalculus.ipynb)."""
    global F, K2, KX, KY, XX, YY, ax, axes, c9, c_rek, fig, g9
    global g_rek, gh, hinter, im, k9, kv, mittel, n9, name, phi9, phi_rek, psi9
    global psi_rek, s9, spektral_div, spektral_rot, titel, v9, vh, w9, w_rek, wh
    n9 = 128
    s9 = 2 * np.pi * np.arange(n9) / n9
    XX, YY = np.meshgrid(s9, s9, indexing="ij")
    phi9 = np.sin(XX) * np.cos(2 * YY) + 0.5 * np.cos(3 * XX + YY)
    psi9 = np.cos(XX) * np.sin(YY) + 0.3 * np.sin(2 * XX - 3 * YY)
    g9 = np.array([np.cos(XX) * np.cos(2 * YY) - 1.5 * np.sin(3 * XX + YY),            # ∇φ
                   -2 * np.sin(XX) * np.sin(2 * YY) - 0.5 * np.sin(3 * XX + YY)])
    w9 = np.array([np.cos(XX) * np.cos(YY) - 0.9 * np.cos(2 * XX - 3 * YY),            # (∂yψ, −∂xψ)
                   np.sin(XX) * np.sin(YY) - 0.6 * np.cos(2 * XX - 3 * YY)])
    c9 = np.array([0.2, -0.1])
    v9 = g9 + w9 + c9[:, None, None]

    k9 = np.fft.fftfreq(n9, 1 / n9)                                  # ganzzahlige Wellenzahlen
    KX, KY = np.meshgrid(k9, k9, indexing="ij")
    K2 = KX**2 + KY**2
    K2[0, 0] = 1.0
    vh = np.fft.fft2(v9, axes=(1, 2))
    kv = (KX * vh[0] + KY * vh[1]) / K2                              # (k·v̂)/k²
    gh = np.array([KX * kv, KY * kv]); gh[:, 0, 0] = 0
    wh = vh - gh; wh[:, 0, 0] = 0
    g_rek, w_rek = np.fft.ifft2(gh, axes=(1, 2)).real, np.fft.ifft2(wh, axes=(1, 2)).real
    c_rek = vh[:, 0, 0].real / n9**2
    phi_rek = np.fft.ifft2(-1j * kv).real                            # φ̂ = (k·v̂)/(i k²)
    psi_rek = np.fft.ifft2((KY * wh[0] - KX * wh[1]) / (1j * K2)).real

    spektral_div = lambda F: np.fft.ifft2(1j * KX * np.fft.fft2(F[0]) + 1j * KY * np.fft.fft2(F[1])).real
    spektral_rot = lambda F: np.fft.ifft2(1j * KX * np.fft.fft2(F[1]) - 1j * KY * np.fft.fft2(F[0])).real
    print(f"Gradiententeil: Abweichung vom Bauteil {np.max(np.abs(g_rek - g9)):.1e}, rot = {np.max(np.abs(spektral_rot(g_rek))):.1e}")
    print(f"quellenfreier Teil: Abweichung {np.max(np.abs(w_rek - w9)):.1e}, div = {np.max(np.abs(spektral_div(w_rek))):.1e}")
    print(f"Mittelwert {c_rek.round(12)}; φ und ψ bis auf Konstanten: {np.max(np.abs(phi_rek - phi9 + phi9.mean())):.1e},"
          f" {np.max(np.abs(psi_rek - psi9 + psi9.mean())):.1e}")
    mittel = lambda F, G: np.mean(np.sum(F * G, axis=0))
    print(f"⟨∇φ, ∇⊥ψ⟩ = {mittel(g_rek, w_rek):+.1e};  Mittelwert von |v|² = {mittel(v9, v9):.6f}"
          f" = {mittel(g_rek, g_rek):.6f} (Gradient) + {mittel(w_rek, w_rek):.6f} (quellenfrei) + {c_rek @ c_rek:.6f} (konstant)")

    fig, axes = plt.subplots(1, 3, figsize=(17, 5.6))
    for ax, (titel, F, hinter, name) in zip(axes, [
            ("Feld v = ∇φ + ∇⊥ψ + c", v9, np.hypot(*v9), "|v|"),
            ("wirbelfreier Teil ∇φ (Hintergrund φ)", g_rek, phi_rek, "φ"),
            ("quellenfreier Teil ∇⊥ψ (Hintergrund ψ)", w_rek, psi_rek, "ψ")]):
        im = ax.pcolormesh(s9, s9, hinter.T, cmap="viridis" if name == "|v|" else "RdBu_r", shading="auto")
        fig.colorbar(im, ax=ax, label=name, shrink=0.85)
        ax.streamplot(s9, s9, F[0].T, F[1].T, color="k", density=1.0, linewidth=0.6)
        ax.set_aspect("equal"); ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_title(titel)
    plt.tight_layout()
    plt.show()


def laplace_equation():
    """10. Die Laplace-Gleichung: Mittelwert, Maximumprinzip und Irrfahrten (Zellen 33 von vectorcalculus.ipynb)."""
    global W_rw, XX, YY, aktiv, ax, axes, fehler10, fig, g, hs10, idx, im
    global k, kreis, laplace_dirichlet, n, n_rw, name, ns10, pfad, pfade, pos, s, s_rw
    global schritte, tt, u, u_ex, u_rw, werte_rw
    def laplace_dirichlet(n, rand_oben):
        """Δu = 0 im Einheitsquadrat, u = rand_oben(x) auf y = 1, sonst 0; n innere Punkte pro Richtung,
    5-Punkte-Stern, Index (i, j) ↔ (x_i, y_j)."""
        h = 1 / (n + 1)
        s = np.linspace(h, 1 - h, n)
        T = sps.diags([1.0, -2.0, 1.0], [-1, 0, 1], shape=(n, n))
        L = (sps.kron(T, sps.identity(n)) + sps.kron(sps.identity(n), T)) / h**2
        b = np.zeros((n, n))
        b[:, -1] -= rand_oben(s) / h**2
        return s, spsl.spsolve(L.tocsc(), b.ravel()).reshape(n, n)


    u_ex = lambda X, Y: np.sin(np.pi * X) * np.sinh(np.pi * Y) / np.sinh(np.pi)
    ns10, fehler10 = [7, 15, 31, 63, 127], []
    for n in ns10:
        s, u = laplace_dirichlet(n, lambda t: np.sin(np.pi * t))
        XX, YY = np.meshgrid(s, s, indexing="ij")
        fehler10.append(np.max(np.abs(u - u_ex(XX, YY))))
        print(f"n = {n:3d}, h = {1 / (n + 1):.4f}: größter Fehler {fehler10[-1]:.2e}, max u innen = {u.max():.4f} (Rand: max 1), min u = {u.min():.1e}")

    tt = 2 * np.pi * np.arange(64) / 64
    for name, g in [("u (harmonisch)", u_ex), ("x² + y² (Δ = 4)", lambda X, Y: X**2 + Y**2)]:
        kreis = g(0.5 + 0.3 * np.cos(tt), 0.5 + 0.3 * np.sin(tt)).mean()
        print(f"{name:16s}: Mittel auf dem Kreis r = 0.3 um (0.5, 0.5) = {kreis:.12f}, Wert im Mittelpunkt = {g(0.5, 0.5):.12f}")

    # Irrfahrten auf dem Gitter n = 31 (h = 1/32) ab (0.5, 0.5); der Wert am Austrittspunkt wird gemittelt
    n_rw, W_rw = 31, 20000
    s_rw, u_rw = laplace_dirichlet(n_rw, lambda t: np.sin(np.pi * t))
    pos = np.full((W_rw, 2), n_rw // 2)
    aktiv = np.ones(W_rw, bool)
    schritte = np.array([[1, 0], [-1, 0], [0, 1], [0, -1]])
    pfade = [[pos[k].copy()] for k in range(3)]
    while aktiv.any():
        idx = np.flatnonzero(aktiv)
        pos[idx] += schritte[rng.integers(0, 4, idx.size)]
        for k in range(3):
            if aktiv[k]:
                pfade[k].append(pos[k].copy())
        aktiv[idx] = np.all((pos[idx] >= 0) & (pos[idx] < n_rw), axis=1)
    werte_rw = np.where(pos[:, 1] == n_rw, np.sin(np.pi * (pos[:, 0] + 1) / (n_rw + 1)), 0.0)
    print(f"Irrfahrten ({W_rw}): u(0.5, 0.5) ≈ {werte_rw.mean():.4f} ± {werte_rw.std() / np.sqrt(W_rw):.4f};"
          f" Gitterlösung {u_rw[n_rw // 2, n_rw // 2]:.4f}; exakt {u_ex(0.5, 0.5):.4f}")

    fig, axes = plt.subplots(1, 2, figsize=(15, 6.2))
    ax = axes[0]
    im = ax.pcolormesh(s_rw, s_rw, u_rw.T, cmap="viridis", shading="auto")
    fig.colorbar(im, ax=ax, label="u(x, y)")
    for k, pfad in enumerate(pfade):
        pfad = (np.array(pfad) + 1) / (n_rw + 1)
        ax.plot(pfad[:, 0], pfad[:, 1], lw=1, color=["w", "tab:orange", "tab:red"][k], label=f"Irrfahrt {k + 1}")
    ax.plot(0.5 + 0.3 * np.cos(tt), 0.5 + 0.3 * np.sin(tt), "w--", lw=1, label="Kreis r = 0.3")
    ax.set_aspect("equal"); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_xlabel("x"); ax.set_ylabel("y")
    ax.legend(loc="lower right", fontsize=8); ax.set_title("Lösung auf dem Gitter (n = 31) und drei Irrfahrten ab (0.5, 0.5)")
    ax = axes[1]
    hs10 = 1 / (np.array(ns10) + 1)
    ax.loglog(hs10, fehler10, "o-", label="größter Fehler, 5-Punkte-Stern")
    ax.loglog(hs10, fehler10[0] * (hs10 / hs10[0]) ** 2, "k:", label="∝ h²")
    ax.set_xlabel("Gitterweite h"); ax.set_ylabel("größter Fehler"); ax.legend()
    ax.set_title("Dirichlet-Problem: der Fehler fällt wie h²")
    plt.tight_layout()
    plt.show()


def flux_volume():
    """11. Fluss, Volumen und die Divergenz in hohen Dimensionen (Zellen 36 von vectorcalculus.ipynb)."""
    global A, E, Jnn, Js, P, W, art, ax, axes, b, d, div_exakt
    global eps, farbe, fig, gam, jvp, k, ks, ln_detJ, los, ls, m, mu
    global pendel, rand0, rmse, schaetzung, t11, tropfen, tv, v_nn, var_theo, vdp_mit_jacobi, x0
    pendel = lambda Q, gam=0.0: np.array([Q[1], -np.sin(Q[0]) - gam * Q[1]])
    t11 = np.linspace(0, 8, 9)
    rand0 = np.array([1.5, 0.0])[:, None] + 0.4 * np.array([np.cos(2 * np.pi * np.arange(4000) / 4000),
                                                             np.sin(2 * np.pi * np.arange(4000) / 4000)])
    tropfen = {}
    for gam in [0.0, 0.25]:
        los = solve_ivp(lambda t, Y: pendel(Y.reshape(2, -1), gam).ravel(), (0, 8), rand0.ravel(), t_eval=t11,
                        rtol=1e-10, atol=1e-12)
        tropfen[gam] = los.y.reshape(2, -1, len(t11))
        A = np.array([schnuersenkel(*tropfen[gam][:, :, k]) for k in range(len(t11))])
        print(f"Pendel, γ = {gam}: Fläche/Anfangsfläche bei t = 8: {A[-1] / A[0]:.8f}, e^(−γt) = {np.exp(-gam * 8):.8f};"
              f" größte Abweichung über t = 0, 1, …, 8: {np.max(np.abs(A / A[0] - np.exp(-gam * t11))):.1e}")

    # Van der Pol: Zustand, Jacobi-Matrix (Variationsgleichung) und ∫div v dt gemeinsam integrieren
    mu = 1.0
    def vdp_mit_jacobi(t, Y):
        q, p, J = Y[0], Y[1], Y[2:6].reshape(2, 2)
        Dv = np.array([[0, 1], [-1 - 2 * mu * q * p, mu * (1 - q**2)]])
        return np.concatenate([[p, mu * (1 - q**2) * p - q], (Dv @ J).ravel(), [mu * (1 - q**2)]])
    tv = np.linspace(0, 15, 600)
    los = solve_ivp(vdp_mit_jacobi, (0, 15), [0.5, 0, 1, 0, 0, 1, 0], t_eval=tv, rtol=1e-11, atol=1e-12)
    ln_detJ = np.log(np.abs([np.linalg.det(los.y[2:6, k].reshape(2, 2)) for k in range(len(tv))]))
    print(f"Van der Pol (μ = 1): größte Abweichung |ln det J − ∫div v dt| bis t = 15: {np.max(np.abs(ln_detJ - los.y[6])):.1e}")

    # Hutchinson: div v = tr J = E[εᵀJε] für E[εεᵀ] = 1, v(x) = tanh(Wx + b) in d = 100, W mit großer Diagonale
    d = 100
    W = np.diag(rng.uniform(0.5, 2.0, d)) + 0.3 * rng.normal(size=(d, d)) / np.sqrt(d)
    b = rng.normal(size=d)
    v_nn = lambda X: np.tanh(W @ X + b)
    x0 = rng.normal(size=d)
    Jnn = (1 - v_nn(x0) ** 2)[:, None] * W
    div_exakt = np.trace(Jnn)
    eps = rng.choice([-1.0, 1.0], size=d)
    jvp = (v_nn(x0 + 1e-5 * eps) - v_nn(x0 - 1e-5 * eps)) / 2e-5        # Jε aus zwei Auswertungen von v
    print(f"div v exakt (Spur der Jacobi-Matrix) = {div_exakt:.6f}; εᵀJε aus zwei Auswertungen von v: {eps @ jvp:.6f},"
          f" mit der Matrix: {eps @ Jnn @ eps:.6f}")
    Js = (Jnn + Jnn.T) / 2
    var_theo = {"Gauß": 2 * np.sum(Js**2), "Rademacher": 2 * (np.sum(Js**2) - np.sum(np.diag(Js) ** 2))}
    ks = 2 ** np.arange(0, 9)
    rmse = {"Gauß": [], "Rademacher": []}
    for k in ks:
        for art in rmse:
            E = rng.normal(size=(2000, k, d)) if art == "Gauß" else rng.choice([-1.0, 1.0], size=(2000, k, d))
            schaetzung = np.einsum("rki,ij,rkj->r", E, Jnn, E) / k
            rmse[art].append(np.sqrt(np.mean((schaetzung - div_exakt) ** 2)))
    for art in rmse:
        print(f"{art:10s}: Standardabweichung einer Probe gemessen {rmse[art][0]:.3f}, Theorie √Var = {np.sqrt(var_theo[art]):.3f};"
              f" relativer Fehler mit k = 16 Proben {rmse[art][4] / abs(div_exakt):.1%}")

    fig, axes = plt.subplots(2, 2, figsize=(15, 11))
    ax = axes[0, 0]
    for k in [0, 4, 8]:
        P = tropfen[0.0][:, :, k]
        ax.fill(P[0], P[1], color="tab:blue", alpha=0.2 + 0.25 * k / 8, label=f"γ = 0, t = {t11[k]:.0f}")
    for k, ls in [(4, "-"), (8, "--")]:
        P = tropfen[0.25][:, :, k]
        ax.plot(P[0], P[1], color="tab:red", lw=1.8, ls=ls, label=f"γ = 0.25, t = {t11[k]:.0f} (Umriss)")
    ax.set_xlabel("Winkel q [rad]"); ax.set_ylabel("Impuls p"); ax.legend(fontsize=8)
    ax.set_title("Ein Tropfen im Phasenraum des Pendels (t = 0, 4, 8)")
    ax = axes[0, 1]
    for gam, farbe in [(0.0, "tab:blue"), (0.25, "tab:red")]:
        A = np.array([schnuersenkel(*tropfen[gam][:, :, k]) for k in range(len(t11))])
        ax.plot(t11, A / A[0], "o", color=farbe, label=f"Fläche/Anfangsfläche, γ = {gam}")
        ax.plot(t11, np.exp(-gam * t11), "-", color=farbe, alpha=0.6, label=f"e^(−γt), γ = {gam}")
    ax.set_xlabel("Zeit t"); ax.set_ylabel("relative Fläche"); ax.legend(fontsize=8)
    ax.set_title("Fläche des Tropfens: erhalten ohne Reibung, e^(−γt) mit Reibung")
    ax = axes[1, 0]
    ax.plot(tv, ln_detJ, label="ln det J (Variationsgleichung)")
    ax.plot(tv[::12], los.y[6, ::12], "o", ms=4, label="∫₀ᵗ div v dt = ∫ μ(1 − x²) dt")
    ax.set_xlabel("Zeit t"); ax.set_ylabel("ln J"); ax.legend()
    ax.set_title("Van der Pol: die Divergenz entlang der Bahn bestimmt ln J")
    ax = axes[1, 1]
    for art, m in [("Gauß", "o-"), ("Rademacher", "s-")]:
        ax.loglog(ks, rmse[art], m, label=f"{art}, gemessen")
        ax.loglog(ks, np.sqrt(var_theo[art] / ks), "k:", lw=1)
    ax.plot([], [], "k:", label="√(Var/k), Theorie")
    ax.set_xlabel("Zahl der Zufallsvektoren k"); ax.set_ylabel("mittlerer Fehler der Schätzung von div v")
    ax.set_title(f"Hutchinson in d = {d}: Fehler ∝ 1/√k (div v = {div_exakt:.2f})"); ax.legend()
    plt.tight_layout()
    plt.show()


def magnetic_field():
    """12. Magnetfeld einer Leiterschleife: Biot–Savart, $\\nabla\\cdot\\mathbf B = 0$ und Ampère (Zellen 39 von vectorcalculus.ipynb)."""
    global B_achse, Bxz, Bz, R, XX, ZZ, abstand_draht, ampere, ax, axes, biot_savart, dBz
    global divB, dr, farbe, fig, hb, mx, name, punkte, r, s12, tt, wege12
    global zs, zz
    def biot_savart(P, n=400, block=2000):
        """B(P) für die Schleife r'(t) = (cos t, sin t, 0) mit μ0 I = 1: B = (1/4π) ∮ dl × (P − r')/|P − r'|³.
    P hat die Form (3, ...); Trapezregel mit n Punkten auf der Schleife."""
        t = 2 * np.pi * np.arange(n) / n
        rq = np.array([np.cos(t), np.sin(t), np.zeros(n)])
        dl = np.array([-np.sin(t), np.cos(t), np.zeros(n)]) * 2 * np.pi / n
        form = P.shape[1:]
        P = P.reshape(3, -1)
        B = np.empty_like(P, dtype=float)
        for a in range(0, P.shape[1], block):
            d = P[:, a:a + block, None] - rq[:, None, :]
            B[:, a:a + block] = np.sum(np.cross(dl[:, None, :], d, axis=0) / np.sum(d**2, axis=0) ** 1.5, axis=2) / (4 * np.pi)
        return B.reshape(3, *form)


    zs = np.linspace(-3, 3, 13)
    B_achse = biot_savart(np.array([np.zeros_like(zs), np.zeros_like(zs), zs]))
    print(f"Achse: größte Abweichung von 1/(2(1 + z²)^(3/2)): {np.max(np.abs(B_achse[2] - 0.5 / (1 + zs**2) ** 1.5)):.1e},"
          f" größte Querkomponente {np.max(np.abs(B_achse[:2])):.1e}")

    # div B mit zentralen Differenzen an zufälligen Punkten mit Abstand ≥ 0.3 vom Draht
    punkte = rng.uniform(-2, 2, size=(3, 400))
    abstand_draht = np.hypot(np.hypot(punkte[0], punkte[1]) - 1, punkte[2])
    punkte = punkte[:, abstand_draht > 0.3][:, :100]
    hb = 1e-4
    divB = sum((biot_savart(punkte + hb * np.eye(3)[a][:, None])[a] - biot_savart(punkte - hb * np.eye(3)[a][:, None])[a]) / (2 * hb)
               for a in range(3))
    dBz = (biot_savart(punkte + hb * np.eye(3)[2][:, None])[2] - biot_savart(punkte - hb * np.eye(3)[2][:, None])[2]) / (2 * hb)
    print(f"div B an 100 Punkten: größter Betrag {np.max(np.abs(divB)):.1e}, typische Größe einer einzelnen Ableitung ∂B_z/∂z: {np.median(np.abs(dBz)):.1e}")

    wege12 = {   # geschlossene Wege in der xz-Ebene; der Draht durchstößt sie bei x = +1 (Strom in +y) und x = −1 (Strom in −y)
        "Kreis r = 0.3 um (1, 0, 0)": ((1, 0.3)),
        "Kreis r = 0.8 um (1, 0, 0)": ((1, 0.8)),
        "Kreis r = 0.3 um (2, 0, 0)": ((2, 0.3)),
        "Kreis r = 1.5 um (0, 0, 0)": ((0, 1.5)),
    }
    ampere = {}
    for name, (mx, R) in wege12.items():
        r = lambda t: np.array([mx + R * np.cos(t), np.zeros_like(t), -R * np.sin(t)])
        dr = lambda t: np.array([-R * np.sin(t), np.zeros_like(t), -R * np.cos(t)])
        ampere[name] = kurvenintegral(lambda X, Y, Z: biot_savart(np.array([X, Y, Z])), r, dr, n=400)
        print(f"Ampère, {name}: ∮ B·dl = {round(ampere[name], 9) + 0.0:+.9f}  (in Einheiten von μ0 I)")

    fig, axes = plt.subplots(1, 2, figsize=(15, 6.3))
    ax = axes[0]
    s12 = np.linspace(-2.5, 2.5, 120)                              # gerade Anzahl: kein Gitterpunkt auf dem Draht
    XX, ZZ = np.meshgrid(s12, s12)
    Bxz = biot_savart(np.array([XX, np.zeros_like(XX), ZZ]))
    ax.streamplot(s12, s12, Bxz[0], Bxz[2], color=np.log10(np.hypot(Bxz[0], Bxz[2])), cmap="viridis", density=1.5, linewidth=0.8)
    # y zeigt in die Bildebene hinein: bei x = +1 fließt der Strom hinein (⊗), bei x = −1 heraus (⊙)
    ax.plot([1], [0], "o", ms=10, mfc="w", mec="k"); ax.plot([1], [0], "kx", ms=7)
    ax.plot([-1], [0], "o", ms=10, mfc="w", mec="k"); ax.plot([-1], [0], "k.", ms=4)
    tt = np.linspace(0, 2 * np.pi, 200)
    for (name, (mx, R)), farbe in zip(wege12.items(), ["tab:red", "tab:orange", "tab:blue", "tab:green"]):
        ax.plot(mx + R * np.cos(tt), R * np.sin(tt), color=farbe, lw=2, label=f"{name}: {round(ampere[name], 6) + 0.0:+.0f}")
    ax.set_aspect("equal"); ax.set_xlabel("x"); ax.set_ylabel("z"); ax.legend(loc="lower left", fontsize=8)
    ax.set_title("Feldlinien der Schleife in der xz-Ebene (Farbe: log₁₀|B|)\nund ∮B·dl in Einheiten von μ0 I")
    ax = axes[1]
    zz = np.logspace(-1.5, 1.3, 40)
    Bz = biot_savart(np.array([np.zeros_like(zz), np.zeros_like(zz), zz]))[2]
    ax.loglog(zz, 0.5 / (1 + zz**2) ** 1.5, label="1/(2(1 + z²)^(3/2))")
    ax.loglog(zz, Bz, "o", ms=4, label="Biot–Savart, 400 Punkte auf der Schleife")
    ax.loglog(zz[zz > 2], 0.5 / zz[zz > 2] ** 3, "k--", label="Dipol 1/(2z³)")
    ax.set_xlabel("Abstand z auf der Achse [Schleifenradien]"); ax.set_ylabel("B_z [μ0 I / R]")
    ax.set_title("Feld auf der Achse: Nahfeld und Dipolabfall ∝ z⁻³"); ax.legend()
    plt.tight_layout()
    plt.show()


def probability_current():
    """13. Wahrscheinlichkeitsstrom und quantisierte Wirbel (Zellen 42 von vectorcalculus.ipynb)."""
    global J, J0, M, P, P0, R, XB, XX, YB, YY, a13, ax
    global axes, b13, div_j, dr, drho_dt, dt, fig, h13, hell, knoten, lab, name
    global psi13, psi_w, r, s13, s13b, strom, t0, tb, v_w, z1, z2, z3
    global zk
    # Zeitabhängiger Zustand: ψ = e^(−r²/2) [a e^(−it) + b (x + iy) e^(−2it)], eine Überlagerung von E = 1 und E = 2
    a13, b13 = 0.6, 0.8
    psi13 = lambda X, Y, t: np.exp(-(X**2 + Y**2) / 2) * (a13 * np.exp(-1j * t) + b13 * (X + 1j * Y) * np.exp(-2j * t))
    s13 = np.linspace(-4, 4, 401)
    h13 = s13[1] - s13[0]
    XX, YY = np.meshgrid(s13, s13, indexing="ij")


    def strom(psi, h):
        """j = Im(ψ* ∇ψ) mit zentralen Differenzen."""
        return np.array([np.imag(np.conj(psi) * np.gradient(psi, h, axis=a)) for a in range(2)])


    t0, dt = 0.7, 1e-4
    drho_dt = (np.abs(psi13(XX, YY, t0 + dt)) ** 2 - np.abs(psi13(XX, YY, t0 - dt)) ** 2) / (2 * dt)
    div_j = div_num(strom(psi13(XX, YY, t0), h13), h13)
    print(f"Kontinuitätsgleichung bei t = {t0}: max|∂ρ/∂t + div j| = {np.max(np.abs(drho_dt + div_j)):.1e}"
          f" bei max|∂ρ/∂t| = {np.max(np.abs(drho_dt)):.2f} (Gitter h = {h13:.2f})")
    print(f"Nullstelle von ψ bei x + iy = −(a/b) e^(it): Radius a/b = {a13 / b13:.2f}, Umlaufzeit 2π")

    # Momentaufnahme mit drei Wirbeln: ψ = (z − z1)(z − z2)(z̄ − z̄3) e^(−|z|²/2)
    z1, z2, z3 = 0.8 + 0.3j, -0.6 + 0.8j, -0.3 - 0.9j
    psi_w = lambda X, Y: ((X + 1j * Y - z1) * (X + 1j * Y - z2) * np.conj(X + 1j * Y - z3)) * np.exp(-(X**2 + Y**2) / 2)
    def v_w(X, Y):
        """v = Im(∇ψ/ψ) = ∇ arg ψ, exakt aus ln ψ = ln(z − z1) + ln(z − z2) + ln(z̄ − z̄3) − |z|²/2."""
        Z = X + 1j * Y
        dx = 1 / (Z - z1) + 1 / (Z - z2) + 1 / np.conj(Z - z3) - X
        dy = 1j / (Z - z1) + 1j / (Z - z2) - 1j / np.conj(Z - z3) - Y
        return np.array([dx.imag, dy.imag])
    for name, (M, R) in {"um z1": (z1, 0.2), "um z2": (z2, 0.2), "um z3 (z̄ − z̄3)": (z3, 0.2), "Kreis r = 2.5 um 0": (0, 2.5),
                         "um z1 und z3": ((z1 + z3) / 2, 0.75)}.items():
        r = lambda t: np.array([M.real + R * np.cos(t), M.imag + R * np.sin(t)]) if isinstance(M, complex) else R * np.array([np.cos(t), np.sin(t)])
        dr = lambda t: R * np.array([-np.sin(t), np.cos(t)])
        print(f"Zirkulation {name:17s}: ∮ v·dl / 2π = {round(kurvenintegral(v_w, r, dr, n=800) / (2 * np.pi), 9) + 0.0:+.9f}")

    fig, axes = plt.subplots(1, 2, figsize=(15, 6.5))
    ax = axes[0]
    s13b = np.linspace(-2.5, 2.5, 400)
    XB, YB = np.meshgrid(s13b, s13b)
    P = psi_w(XB, YB)
    hell = np.clip(np.abs(P) / np.abs(P).max(), 0, 1) ** 0.5
    ax.imshow(hsv_to_rgb(np.dstack([(np.angle(P) / (2 * np.pi)) % 1, 0.8 * np.ones_like(hell), 0.35 + 0.65 * hell])),
              extent=[-2.5, 2.5, -2.5, 2.5], origin="lower")
    J = np.abs(P) ** 2 * v_w(XB, YB)
    ax.streamplot(s13b, s13b, J[0], J[1], color="k", density=1.2, linewidth=0.6)
    for zk, lab in [(z1, "+1"), (z2, "+1"), (z3, "−1")]:
        ax.annotate(lab, (zk.real, zk.imag), xytext=(6, 6), textcoords="offset points", color="w", fontsize=12, weight="bold")
    ax.set_xlabel("x"); ax.set_ylabel("y")
    ax.set_title("Phase von ψ (Farbe), |ψ| (Helligkeit) und Stromlinien von j;\nZirkulation um die Nullstellen in Einheiten von 2π")
    ax = axes[1]
    P0 = psi13(XX, YY, 0.0)
    ax.pcolormesh(s13, s13, (np.abs(P0) ** 2).T, cmap="magma", shading="auto")
    J0 = strom(P0, h13)
    ax.streamplot(s13, s13, J0[0].T, J0[1].T, color="w", density=1.0, linewidth=0.6)
    tb = np.linspace(0, 2 * np.pi, 9)[:-1]
    knoten = -(a13 / b13) * np.exp(1j * tb)
    ax.plot(knoten.real, knoten.imag, "o", color="tab:cyan", ms=7, label="Nullstelle bei t = 0, π/4, …, 7π/4")
    ax.plot(knoten[0].real, knoten[0].imag, "o", color="tab:cyan", mec="w", ms=11)
    ax.set_xlim(-2.5, 2.5); ax.set_ylim(-2.5, 2.5); ax.set_aspect("equal"); ax.set_xlabel("x"); ax.set_ylabel("y")
    ax.legend(loc="lower left", fontsize=8)
    ax.set_title("Oszillator, a e^(−it) φ₀ + b (x + iy) e^(−2it) φ₀: Dichte und j bei t = 0;\nder Wirbel läuft mit ω = 1 im Kreis")
    plt.tight_layout()
    plt.show()


def berry_curvature():
    """14. Berry-Krümmung: ein Monopol im Parameterraum (Zellen 45 von vectorcalculus.ipynb)."""
    global F, Fq, H_kugel, H_qwz, KXq, KYq, PAULI, PP, S, SPIN1, TT, V
    global ax, axes, berry, chern_qwz, cherns, fig, halber_raumwinkel, im, ms, name, nk, np_
    global nt, phis, plaketten_fluss, raumwinkel, s_, th, thetas, zustaende
    PAULI = [np.array([[0, 1], [1, 0]], complex), np.array([[0, -1j], [1j, 0]]), np.array([[1, 0], [0, -1]], complex)]
    s_ = 1 / np.sqrt(2)
    SPIN1 = [np.array([[0, s_, 0], [s_, 0, s_], [0, s_, 0]], complex), np.array([[0, -1j * s_, 0], [1j * s_, 0, -1j * s_], [0, 1j * s_, 0]]),
             np.diag([1.0, 0.0, -1.0]).astype(complex)]


    def zustaende(H_von, gitter):
        """Eigenvektoren (nach Energie sortiert) auf einem Gitter von Parametern; Form (..., dim, dim)."""
        return np.linalg.eigh(H_von(*gitter))[1]


    def plaketten_fluss(U, periodisch_erste=False):
        """Berry-Fluss durch jede Plakette (Fukui–Hatsugai–Suzuki): −arg des Produkts der vier Überlappungen.
    U[i, j] = Zustandsvektor; zweite Gitterrichtung periodisch."""
        U1 = np.roll(U, -1, axis=0) if periodisch_erste else U[1:]
        U0 = U if periodisch_erste else U[:-1]
        U2, U3 = np.roll(U1, -1, axis=1), np.roll(U0, -1, axis=1)
        ue = lambda A, B: np.sum(np.conj(A) * B, axis=-1)
        return -np.angle(ue(U0, U1) * ue(U1, U2) * ue(U2, U3) * ue(U3, U0))


    H_kugel = lambda S: (lambda T, P: np.einsum("...,ab->...ab", np.sin(T) * np.cos(P), S[0])
                         + np.einsum("...,ab->...ab", np.sin(T) * np.sin(P), S[1]) + np.einsum("...,ab->...ab", np.cos(T), S[2]))
    nt, np_ = 60, 120
    TT, PP = np.meshgrid(np.linspace(0, np.pi, nt + 1), 2 * np.pi * np.arange(np_) / np_, indexing="ij")
    for name, S in [("Spin ½", PAULI), ("Spin 1", SPIN1)]:
        V = zustaende(H_kugel(S), (TT, PP))
        cherns = [np.sum(plaketten_fluss(V[..., :, m])) / (2 * np.pi) for m in range(V.shape[-1])]
        print(f"{name}: Chern-Zahlen der Zustände (nach Energie aufsteigend): {np.round(cherns, 9) + 0.0}")
        if name == "Spin ½":
            F = plaketten_fluss(V[..., :, 0])
            raumwinkel = (np.cos(TT[:-1]) - np.cos(TT[1:])) * 2 * np.pi / np_   # Raumwinkel jeder Plakette
            print(f"  unterer Zustand: Berry-Fluss / Raumwinkel pro Plakette = {np.mean(F / raumwinkel):.6f} ± {np.std(F / raumwinkel):.1e}"
                  f" → Krümmung R̂/(2R²), ein Monopol der Stärke ½")

    # Berry-Phase eines Breitenkreises bei θ (unterer Zustand von Spin ½) gegen den halben Raumwinkel
    thetas = np.linspace(0.05, np.pi - 0.05, 40)
    phis = 2 * np.pi * np.arange(400) / 400
    berry = []
    for th in thetas:
        V = zustaende(H_kugel(PAULI), (np.full_like(phis, th), phis))[..., :, 0]
        berry.append(-np.angle(np.prod(np.sum(np.conj(V) * np.roll(V, -1, axis=0), axis=1))))
    halber_raumwinkel = np.angle(np.exp(1j * np.pi * (1 - np.cos(thetas))))          # Ω/2 = π(1 − cos θ), nach (−π, π]
    print(f"Berry-Phase gegen Ω/2 (mod 2π): größte Abweichung {np.max(np.abs(np.angle(np.exp(1j * (np.array(berry) - halber_raumwinkel))))):.1e}")

    # Qi–Wu–Zhang: H(k) = sin kx σx + sin ky σy + (m + cos kx + cos ky) σz auf der Brillouin-Zone
    nk = 60
    KXq, KYq = np.meshgrid(2 * np.pi * np.arange(nk) / nk, 2 * np.pi * np.arange(nk) / nk, indexing="ij")
    H_qwz = lambda m: (lambda KX, KY: np.einsum("...,ab->...ab", np.sin(KX), PAULI[0]) + np.einsum("...,ab->...ab", np.sin(KY), PAULI[1])
                       + np.einsum("...,ab->...ab", m + np.cos(KX) + np.cos(KY), PAULI[2]))
    ms = np.linspace(-3, 3, 60)
    chern_qwz = [np.sum(plaketten_fluss(zustaende(H_qwz(m), (KXq, KYq))[..., :, 0], periodisch_erste=True)) / (2 * np.pi) for m in ms]
    print("QWZ, unteres Band: Chern-Zahl für m = −2.5, −1, 1, 2.5:",
          [round(np.sum(plaketten_fluss(zustaende(H_qwz(m), (KXq, KYq))[..., :, 0], periodisch_erste=True)) / (2 * np.pi), 9) + 0.0
           for m in (-2.5, -1, 1, 2.5)])

    fig, axes = plt.subplots(1, 3, figsize=(17, 5.2))
    ax = axes[0]
    ax.plot(thetas, halber_raumwinkel, label="Ω/2 = π(1 − cos θ), nach (−π, π]")
    ax.plot(thetas, berry, "o", ms=4, label="Berry-Phase aus 400 Eigenvektoren")
    ax.set_xlabel("Polarwinkel θ des Breitenkreises [rad]"); ax.set_ylabel("Phase [rad]"); ax.legend(fontsize=8)
    ax.set_title("Spin ½, unterer Zustand: Berry-Phase = halber Raumwinkel")
    ax = axes[1]
    ax.plot(ms, chern_qwz, "o-", ms=4)
    ax.set_xlabel("Massenparameter m"); ax.set_ylabel("Chern-Zahl des unteren Bandes")
    ax.set_title("Qi–Wu–Zhang: Sprünge bei m = −2, 0, 2 (Bandlücke schließt)")
    ax = axes[2]
    Fq = plaketten_fluss(zustaende(H_qwz(1.0), (KXq, KYq))[..., :, 0], periodisch_erste=True) / (2 * np.pi / nk) ** 2
    im = ax.pcolormesh(KXq[:, 0], KYq[0], Fq.T, cmap="RdBu_r", norm=TwoSlopeNorm(0), shading="auto")
    fig.colorbar(im, ax=ax, label="Berry-Krümmung F(k)")
    ax.set_aspect("equal"); ax.set_xlabel("k_x [1/Gitterkonstante]"); ax.set_ylabel("k_y [1/Gitterkonstante]")
    ax.set_title(f"QWZ, m = 1: Berry-Krümmung über der Brillouin-Zone\nΣ F ΔkxΔky / 2π = {np.sum(Fq) * (2 * np.pi / nk) ** 2 / (2 * np.pi):+.6f}")
    plt.tight_layout()
    plt.show()
