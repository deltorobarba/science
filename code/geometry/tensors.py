"""Tensoranalysis auf Mannigfaltigkeiten: Christoffel-Symbole und Krümmung der Sphäre, Geodäten, Paralleltransport, Torus, Schwarzschild, Bianchi-Identitäten und Lichtablenkung an der Sonne.

Für geometry.ipynb aus tensoranalysis.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, sphere, geodesics, parallel_transport, torus, schwarzschild, bianchi, light_bending.
"""
import itertools
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp, trapezoid


def load():
    """15. Daten (Zellen 4 von tensoranalysis.ipynb)."""
    global christoffel, einstein, geodesic_rhs, ricci, ricci_scalar, riemann, show, simp
    # Alles hier Benutzte (numpy, sympy, scipy, matplotlib) ist in Colab vorinstalliert; installiert wird nichts.

    def simp(e):
        """Vereinfacht, auch mit trigonometrischen Identitäten wie sin(2θ)/(2 tan θ) − cos(2θ) = sin²θ."""
        return sp.trigsimp(sp.expand_trig(sp.simplify(e)))

    def christoffel(g, x):
        """Γ^a_bc = ½ g^ad (∂_b g_dc + ∂_c g_db − ∂_d g_bc)."""
        n = len(x)
        ginv = sp.simplify(g.inv())
        Gam = sp.MutableDenseNDimArray.zeros(n, n, n)
        for a in range(n):
            for b in range(n):
                for c in range(b, n):
                    val = simp(sum(ginv[a, d] * (sp.diff(g[d, c], x[b]) + sp.diff(g[d, b], x[c]) - sp.diff(g[b, c], x[d]))
                                          for d in range(n)) / 2)
                    Gam[a, b, c] = Gam[a, c, b] = val
        return sp.ImmutableDenseNDimArray(Gam)

    def riemann(Gam, x):
        """R^a_bcd = ∂_c Γ^a_db − ∂_d Γ^a_cb + Γ^a_ce Γ^e_db − Γ^a_de Γ^e_cb (antisymmetrisch in c, d)."""
        n = len(x)
        Riem = sp.MutableDenseNDimArray.zeros(n, n, n, n)
        for a, b, c, d in itertools.product(range(n), repeat=4):
            if c < d:
                val = simp(sp.diff(Gam[a, d, b], x[c]) - sp.diff(Gam[a, c, b], x[d])
                                  + sum(Gam[a, c, e] * Gam[e, d, b] - Gam[a, d, e] * Gam[e, c, b] for e in range(n)))
                Riem[a, b, c, d], Riem[a, b, d, c] = val, -val
        return sp.ImmutableDenseNDimArray(Riem)

    def ricci(Riem):
        """R_bd = R^a_bad."""
        n = Riem.shape[0]
        return sp.Matrix(n, n, lambda b, d: simp(sum(Riem[a, b, a, d] for a in range(n))))

    def ricci_scalar(Ric, g):
        return simp(sum(g.inv()[b, d] * Ric[b, d] for b in range(g.shape[0]) for d in range(g.shape[0])))

    def einstein(Ric, Rs, g):
        return (Ric - Rs * g / 2).applyfunc(simp)

    def show(name, T, labels):
        """Druckt die von null verschiedenen Komponenten, mit Koordinatennamen als Indizes."""
        for idx in itertools.product(range(T.shape[0]), repeat=len(T.shape)):
            if T[idx] != 0:
                print(f"  {name}[{','.join(labels[i] for i in idx)}] = {T[idx]}")

    def geodesic_rhs(Gam, x):
        """Numerische rechte Seite der Geodätengleichung für den Zustand (x, dx/dλ)."""
        n = len(x)
        f = sp.lambdify(x, Gam.tolist(), "numpy")
        def rhs(lam, y):
            pos, vel = y[:n], y[n:]
            G = np.array(f(*pos), dtype=float)
            return np.concatenate([vel, -np.einsum("abc,b,c->a", G, vel, vel)])
        return rhs

    print("Werkzeuge bereit")


def sphere():
    """16. Die 2-Sphäre: Christoffel-Symbole und Krümmung (Zellen 6 von tensoranalysis.ipynb)."""
    global Gam_s2, R_s2, Ric_s2, Riem_s2, X_s2, a, g_s2, ph, th
    a = sp.symbols("a", positive=True)
    th, ph = sp.symbols("theta phi")
    X_s2 = [th, ph]
    g_s2 = sp.diag(a ** 2, a ** 2 * sp.sin(th) ** 2)

    Gam_s2 = christoffel(g_s2, X_s2)
    Riem_s2 = riemann(Gam_s2, X_s2)
    Ric_s2 = ricci(Riem_s2)
    R_s2 = ricci_scalar(Ric_s2, g_s2)

    print("Christoffel-Symbole Γ^a_bc:")
    show("Γ", Gam_s2, ["θ", "φ"])
    print("Riemann-Tensor R^a_bcd:")
    show("R", Riem_s2, ["θ", "φ"])
    print(f"Ricci-Tensor: {Ric_s2.tolist()}")
    print(f"Ricci-Skalar R = {R_s2},  Gauß-Krümmung K = R/2 = {sp.simplify(R_s2 / 2)}")
    print(f"Unabhängige Komponenten des Riemann-Tensors in n Dimensionen, n²(n²−1)/12: " + ", ".join(f"n={n}: {n**2 * (n**2 - 1) // 12}" for n in (2, 3, 4)))


def geodesics():
    """17. Geodäten auf der Sphäre (Zellen 9 von tensoranalysis.ipynb)."""
    global L_phi, ax, ax2, dph, dth, fig, lam, normal, ph_n, rhs_s2, sol, speed2
    global th_n, u_, v_, xyz, y0
    rhs_s2 = geodesic_rhs(Gam_s2.subs(a, 1), X_s2)           # unit sphere
    y0 = [np.pi / 2, 0.0, -np.cos(np.radians(45)), np.sin(np.radians(45))]   # on the equator, heading north-east
    sol = solve_ivp(rhs_s2, [0, 2 * np.pi], y0, rtol=1e-11, atol=1e-12, dense_output=True)
    lam = np.linspace(0, 2 * np.pi, 400)
    th_n, ph_n, dth, dph = sol.sol(lam)
    xyz = np.array([np.sin(th_n) * np.cos(ph_n), np.sin(th_n) * np.sin(ph_n), np.cos(th_n)])

    normal = np.cross(xyz[:, 0], xyz[:, 40])
    normal /= np.linalg.norm(normal)
    speed2 = dth ** 2 + np.sin(th_n) ** 2 * dph ** 2               # g(v, v)
    L_phi = np.sin(th_n) ** 2 * dph                                 # conserved because the metric does not depend on φ

    fig = plt.figure(figsize=(12, 4.5))
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    u_, v_ = np.meshgrid(np.linspace(0, np.pi, 30), np.linspace(0, 2 * np.pi, 30))
    ax.plot_wireframe(np.sin(u_) * np.cos(v_), np.sin(u_) * np.sin(v_), np.cos(u_), color="lightgrey", lw=0.5)
    ax.plot(*xyz, c="tab:red", lw=2, label="numerische Geodäte")
    ax.view_init(elev=15, azim=20)
    ax.set_title("Geodäte auf der Einheitssphäre")
    ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z")
    ax.legend()
    ax2 = fig.add_subplot(1, 2, 2)
    ax2.plot(lam, normal @ xyz, label="Abstand von der Ebene der ersten Punkte")
    ax2.plot(lam, speed2 - speed2[0], label="g(v, v) − Anfangswert")
    ax2.plot(lam, L_phi - L_phi[0], label="sin²θ dφ/dλ − Anfangswert")
    ax2.set_xlabel("affiner Parameter λ (Bogenlänge auf der Einheitssphäre)")
    ax2.set_ylabel("Abweichung")
    ax2.set_title("Großkreis und Erhaltungsgrößen")
    ax2.legend(fontsize=8)
    fig.tight_layout()
    plt.show()
    print(f"größter Abstand von der Großkreisebene: {np.max(np.abs(normal @ xyz)):.1e}")
    print(f"größte Drift von g(v,v): {np.max(np.abs(speed2 - speed2[0])):.1e},  von sin²θ φ': {np.max(np.abs(L_phi - L_phi[0])):.1e}")


def parallel_transport():
    """18. Paralleltransport um einen Breitenkreis (Zellen 12 von tensoranalysis.ipynb)."""
    global Gam_num, ax, err, fig, measured, predicted, thetas0, transport_angle
    Gam_num = sp.lambdify([th, ph], Gam_s2.subs(a, 1).tolist(), "numpy")

    def transport_angle(theta0):
        """Paralleltransport von e_θ einmal um θ = theta0 (Kurve x(λ) = (theta0, λ)); gibt den Drehwinkel zurück."""
        def rhs(lam, V):
            G = np.array(Gam_num(theta0, lam), dtype=float)
            return -np.einsum("abc,b,c->a", G, np.array([0.0, 1.0]), V)     # dx/dλ = (0, 1)
        V_end = solve_ivp(rhs, [0, 2 * np.pi], [1.0, 0.0], rtol=1e-11, atol=1e-12).y[:, -1]
        return np.arctan2(V_end[1] * np.sin(theta0), V_end[0]) % (2 * np.pi)   # angle in the orthonormal frame

    thetas0 = np.linspace(0.05, np.pi - 0.05, 40)
    measured = np.array([transport_angle(t) for t in thetas0])
    predicted = (2 * np.pi * (1 - np.cos(thetas0))) % (2 * np.pi)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(np.degrees(thetas0), np.degrees(measured), "o", ms=4, label="numerischer Paralleltransport")
    ax.plot(np.degrees(thetas0), np.degrees(predicted), c="black", lw=1, label="∫K dA über die Kappe = 2π(1 − cos θ₀), mod 360°")
    ax.set_xlabel("Polabstand θ₀ der Schleife [°]")
    ax.set_ylabel("Drehung des transportierten Vektors [°]")
    ax.set_title("Holonomie auf der Einheitssphäre")
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()
    err = np.minimum(np.abs(measured - predicted), 2 * np.pi - np.abs(measured - predicted))
    print(f"größte Abweichung von 2π(1 − cos θ₀) mod 2π: {np.degrees(err.max()):.2e} Grad")
    print(f"Beispiel θ₀ = 60°: Drehung {np.degrees(transport_angle(np.pi / 3)):.4f}°, Kappenfläche/a² = {np.degrees(2 * np.pi * (1 - 0.5)):.4f}°")


def torus():
    """19. Der Torus: Krümmung mit wechselndem Vorzeichen, und Gauß–Bonnet (Zellen 15 von tensoranalysis.ipynb)."""
    global Gam_t, K_num, K_t, Kc, P_, Rt, T_, Xt, Yt, Zt, ax, ax2
    global fig, g_t, norm, rt, sqrt_det, total_K_sphere, total_K_torus, tt, vals
    Rt, rt = sp.symbols("R r", positive=True)
    g_t = sp.diag(rt ** 2, (Rt + rt * sp.cos(th)) ** 2)
    Gam_t = christoffel(g_t, X_s2)
    K_t = sp.simplify(ricci_scalar(ricci(riemann(Gam_t, X_s2)), g_t) / 2)
    print(f"Gauß-Krümmung des Torus: K = {K_t}")

    vals = {Rt: 2.0, rt: 1.0}
    K_num = sp.lambdify(th, K_t.subs(vals), "numpy")
    sqrt_det = sp.lambdify(th, sp.sqrt(g_t.det()).subs(vals), "numpy")
    tt = np.linspace(0, 2 * np.pi, 2001)
    total_K_torus = trapezoid(K_num(tt) * sqrt_det(tt), tt) * 2 * np.pi        # ∫∫ K √g dθ dφ
    total_K_sphere = float(sp.integrate(sp.integrate((R_s2 / 2 * sp.sqrt(g_s2.det())).subs(a, 1), (th, 0, sp.pi)), (ph, 0, 2 * sp.pi)))

    fig = plt.figure(figsize=(12, 4.5))
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    T_, P_ = np.meshgrid(np.linspace(0, 2 * np.pi, 80), np.linspace(0, 2 * np.pi, 80))
    Xt, Yt, Zt = (2 + np.cos(T_)) * np.cos(P_), (2 + np.cos(T_)) * np.sin(P_), np.sin(T_)
    Kc = K_num(T_)
    norm = plt.matplotlib.colors.TwoSlopeNorm(vmin=Kc.min(), vcenter=0.0, vmax=Kc.max())
    ax.plot_surface(Xt, Yt, Zt, facecolors=plt.cm.RdBu_r(norm(Kc)), linewidth=0, antialiased=True, shade=False)
    ax.view_init(elev=35, azim=-60)
    ax.set_box_aspect((1, 1, 0.35))
    ax.set_title("Gauß-Krümmung auf dem Torus (rot > 0, blau < 0)")
    ax.set_axis_off()
    ax2 = fig.add_subplot(1, 2, 2)
    ax2.plot(np.degrees(tt), K_num(tt), c="black")
    ax2.axhline(0, color="grey", lw=0.8)
    ax2.set_xlabel("Winkel θ um die Röhre [°] (0° = äußerer Äquator)")
    ax2.set_ylabel("Gauß-Krümmung K [1/r²]")
    ax2.set_title("R = 2, r = 1")
    fig.tight_layout()
    plt.show()
    print(f"∫K dA, Torus:  {total_K_torus:.2e}   (Gauß–Bonnet: 2π·χ = 0)")
    print(f"∫K dA, Sphäre: {total_K_sphere:.6f}   (Gauß–Bonnet: 2π·2 = {4 * np.pi:.6f})")


def schwarzschild():
    """20. Schwarzschild: Vakuum, erste Bianchi-Identität und Gezeitenkräfte (Zellen 18 von tensoranalysis.ipynb)."""
    global G_SI, Gam_s, M, Ric_s, Riem_s, X_s, c_SI, cases, f_s, g_s, gd, gi
    global kretschmann, mass, name, r, radius, t, tidal_r, tidal_th, viol
    t, r, M = sp.symbols("t r M", positive=True)
    X_s = [t, r, th, ph]
    f_s = 1 - 2 * M / r
    g_s = sp.diag(-f_s, 1 / f_s, r ** 2, r ** 2 * sp.sin(th) ** 2)
    Gam_s = christoffel(g_s, X_s)
    Riem_s = riemann(Gam_s, X_s)
    Ric_s = ricci(Riem_s)
    print(f"Ricci-Tensor von Schwarzschild: {'null (Vakuum)' if Ric_s == sp.zeros(4, 4) else Ric_s}")

    # Erste Bianchi-Identität: R^a_bcd + R^a_cdb + R^a_dbc = 0
    viol = [sp.simplify(Riem_s[a_, b, c, d] + Riem_s[a_, c, d, b] + Riem_s[a_, d, b, c])
            for a_, b, c, d in itertools.product(range(4), repeat=4)]
    print(f"Erste Bianchi-Identität: {sum(v != 0 for v in viol)} verletzte Komponenten von {len(viol)}")

    # Kretschmann-Skalar für diese diagonale Metrik: Σ (R^a_bcd)² g_aa g^bb g^cc g^dd
    gd, gi = [g_s[i, i] for i in range(4)], [1 / g_s[i, i] for i in range(4)]
    kretschmann = sp.simplify(sum(Riem_s[a_, b, c, d] ** 2 * gd[a_] * gi[b] * gi[c] * gi[d]
                                  for a_, b, c, d in itertools.product(range(4), repeat=4)))
    print(f"Kretschmann-Skalar: {kretschmann}")

    # Gezeitentensor im ruhenden Orthonormalsystem: R^r̂_t̂r̂t̂ = R^r_trt / (1 − 2M/r), ebenso für θ
    tidal_r = sp.simplify(Riem_s[1, 0, 1, 0] / f_s)
    tidal_th = sp.simplify(Riem_s[2, 0, 2, 0] / f_s)
    print(f"R^r̂_t̂r̂t̂ = {tidal_r},   R^θ̂_t̂θ̂t̂ = {tidal_th}")

    # Größe der radialen Gezeitenbeschleunigung 2GM L / r³ über einen 2 m langen Körper, in SI-Einheiten
    G_SI, c_SI = 6.674e-11, 2.998e8
    cases = [("Erdoberfläche", 5.972e24, 6.371e6), ("Sonnenoberfläche", 1.989e30, 6.957e8),
             ("Horizont, 10 Sonnenmassen", 10 * 1.989e30, 2 * G_SI * 10 * 1.989e30 / c_SI ** 2),
             ("Horizont, Sgr A* (4,3e6 Sonnenmassen)", 4.3e6 * 1.989e30, 2 * G_SI * 4.3e6 * 1.989e30 / c_SI ** 2)]
    print("\nRadiale Gezeitenbeschleunigung zwischen Kopf und Füßen (2 m):")
    for name, mass, radius in cases:
        print(f"  {name:38s} r = {radius:9.3e} m:  Δa = {2 * G_SI * mass * 2.0 / radius ** 3:9.2e} m/s²")


def bianchi():
    """21. Die kontrahierte Bianchi-Identität in einem expandierenden Universum (Zellen 21 von tensoranalysis.ipynb)."""
    global G_f, G_up, Gam_f, Ric_f, Rs_f, X_f, af, div, g_f, xx, yy, zz
    xx, yy, zz = sp.symbols("x y z")
    af = sp.Function("a")(t)
    X_f = [t, xx, yy, zz]
    g_f = sp.diag(-1, af ** 2, af ** 2, af ** 2)
    Gam_f = christoffel(g_f, X_f)
    Ric_f = ricci(riemann(Gam_f, X_f))
    Rs_f = ricci_scalar(Ric_f, g_f)
    G_f = einstein(Ric_f, Rs_f, g_f)
    G_up = sp.simplify(g_f.inv() * G_f * g_f.inv())
    print(f"Ricci-Skalar: R = {Rs_f}")
    print(f"G_tt = {sp.simplify(G_f[0, 0])},   G_xx = {sp.simplify(G_f[1, 1])}")

    div = [sp.simplify(sum(sp.diff(G_up[m, n_], X_f[m]) for m in range(4))
                       + sum(Gam_f[m, m, l] * G_up[l, n_] for m in range(4) for l in range(4))
                       + sum(Gam_f[n_, m, l] * G_up[m, l] for m in range(4) for l in range(4))) for n_ in range(4)]
    print(f"∇_μ G^μν for ν = t, x, y, z: {div}")


def light_bending():
    """22. Geodäten um die Sonne: Lichtablenkung und Perihel des Merkur (Zellen 24 von tensoranalysis.ipynb)."""
    global A_MERC, E_MERC, M_SUN, P_MERC, RAD_TO_ARCSEC, R_SUN, axes, d_sun, defl, deflection, eps_grid, eps_merc
    global fig, per_century, perihelion_shift, prec, shift
    M_SUN = 1476.6                        # GM/c² of the Sun [m]
    R_SUN = 6.957e8                       # radius of the Sun [m]
    A_MERC, E_MERC, P_MERC = 5.7909e10, 0.2056, 87.969   # semi-major axis [m], eccentricity, period [days]
    RAD_TO_ARCSEC = 180 / np.pi * 3600

    def deflection(eps):
        leave = lambda phi, w: w[0]
        leave.terminal, leave.direction = True, -1
        sol = solve_ivp(lambda phi, w: [w[1], -w[0] + 3 * eps * w[0] ** 2], [0, 4], [0.0, 1.0],
                        method="DOP853", rtol=1e-13, atol=1e-16, events=leave)
        return sol.t_events[0][0] - np.pi

    def perihelion_shift(eps, e):
        peri = lambda phi, w: w[1]
        peri.direction = -1                       # w' changes from + to −: maximum of w = perihelion
        sol = solve_ivp(lambda phi, w: [w[1], -w[0] + 1 + 3 * eps * w[0] ** 2], [0, 2 * np.pi + 1], [1 + e, 0.0],
                        method="DOP853", rtol=1e-13, atol=1e-16, events=peri)
        return [p for p in sol.t_events[0] if p > 1][0] - 2 * np.pi

    eps_grid = np.logspace(-6, -2, 9)
    defl = np.array([deflection(e_) for e_ in eps_grid])
    prec = np.array([perihelion_shift(e_, E_MERC) for e_ in eps_grid])

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    axes[0].loglog(eps_grid, defl, "o", label="numerische Nullgeodäte")
    axes[0].loglog(eps_grid, 4 * eps_grid, c="black", lw=1, label="4M/b")
    axes[0].set_xlabel("M/b")
    axes[0].set_ylabel("Ablenkwinkel [rad]")
    axes[0].set_title("Lichtablenkung")
    axes[0].legend()
    axes[1].loglog(eps_grid, prec, "o", label="numerische zeitartige Geodäte")
    axes[1].loglog(eps_grid, 6 * np.pi * eps_grid, c="black", lw=1, label="6πM/p")
    axes[1].set_xlabel("M/p")
    axes[1].set_ylabel("Periheldrehung pro Umlauf [rad]")
    axes[1].set_title(f"Periheldrehung (e = {E_MERC})")
    axes[1].legend()
    fig.tight_layout()
    plt.show()

    d_sun = deflection(M_SUN / R_SUN)
    eps_merc = M_SUN / (A_MERC * (1 - E_MERC ** 2))
    shift = perihelion_shift(eps_merc, E_MERC)
    per_century = shift * 36525 / P_MERC
    print(f"Licht am Sonnenrand: {d_sun * RAD_TO_ARCSEC:.4f}″   (4GM/(c²R) = {4 * M_SUN / R_SUN * RAD_TO_ARCSEC:.4f}″)")
    print(f"Merkur: {shift:.4e} rad pro Umlauf = {per_century * RAD_TO_ARCSEC:.2f}″ pro Jahrhundert   "
          f"(6πGM/(c²a(1−e²)) = {6 * np.pi * eps_merc * 36525 / P_MERC * RAD_TO_ARCSEC:.2f}″)")
