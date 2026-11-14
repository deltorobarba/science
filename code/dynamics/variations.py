"""Variationsrechnung: Laufzeiten verschiedener Bahnen (Brachistochrone), die direkte Methode, Noether am Zentralkraftproblem und Geodäten auf der Kugel.

Für dynamics.ipynb aus calculus_of_variations.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, travel_times, direct_method, noether, sphere_geodesics.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.optimize import brentq, minimize


def load():
    """1. Daten (Zellen 4 von calculus_of_variations.ipynb)."""
    global T_zykloide, a, g, laufzeit, theta1, x1, y1
    g = 9.81                       # Erdbeschleunigung in m/s²
    x1, y1 = 1.0, 0.5              # Endpunkt in m; y zeigt nach unten


    def laufzeit(x, y):
        """Laufzeit entlang des Polygonzugs (x, y), Start in Ruhe bei y = 0.

    Auf jedem geraden Stück ist die Beschleunigung konstant, also ist die Durchschnittsgeschwindigkeit
    der Mittelwert der Geschwindigkeiten an den Enden: dt = 2 ds / (v_a + v_b), exakt für den Polygonzug.
    """
        ds = np.hypot(np.diff(x), np.diff(y))
        v = np.sqrt(2 * g * np.clip(y, 0, None))
        m = ds > 0                                          # Stücke der Länge null überspringen
        return np.sum(2 * ds[m] / (v[1:][m] + v[:-1][m]))


    # Zykloide durch den Endpunkt: (theta - sin theta) / (1 - cos theta) = x1 / y1
    theta1 = brentq(lambda t: (t - np.sin(t)) / (1 - np.cos(t)) - x1 / y1, 1e-6, 2 * np.pi - 1e-6)
    a = y1 / (1 - np.cos(theta1))
    T_zykloide = np.sqrt(a / g) * theta1
    print(f"Zykloide: a = {a:.4f} m, theta1 = {theta1:.4f} (tiefster Punkt bei theta = pi), T = {T_zykloide:.4f} s")


def travel_times():
    """2. Laufzeiten verschiedener Bahnen (Zellen 6 von calculus_of_variations.ipynb)."""
    global T_gerade_exakt, ax1, ax2, bahnen, exponenten, fig, name, s, th, x, y, zeiten
    s = np.linspace(0, 1, 20001) ** 2                     # Stützstellen, dicht am Start
    th = theta1 * np.linspace(0, 1, 20001)                  # die Zykloide ist in theta schon dicht am Start
    bahnen = {
        "Zykloide": (a * (th - np.sin(th)), a * (1 - np.cos(th))),
        "Gerade": (x1 * s, y1 * s),
        "Potenzkurve p = 0.5": (x1 * s, y1 * s ** 0.5),
    }

    T_gerade_exakt = np.sqrt(2 * (x1**2 + y1**2) / (g * y1))
    print(f"Kontrolle: Gerade numerisch {laufzeit(*bahnen['Gerade']):.5f} s, exakt {T_gerade_exakt:.5f} s")
    print(f"Kontrolle: Zykloide numerisch {laufzeit(*bahnen['Zykloide']):.5f} s, exakt {T_zykloide:.5f} s")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.5))
    for name, (x, y) in bahnen.items():
        ax1.plot(x, y, label=f"{name}: {laufzeit(x, y):.4f} s")
    ax1.plot([0, x1], [0, y1], "ko")
    ax1.invert_yaxis()
    ax1.set_aspect("equal")
    ax1.set_xlabel("x [m]")
    ax1.set_ylabel("y [m], nach unten")
    ax1.set_title("Bahnen von (0, 0) nach (1, 0.5)")
    ax1.legend()

    exponenten = np.linspace(0.15, 1.0, 60)
    zeiten = [laufzeit(x1 * s, y1 * s ** p) for p in exponenten]
    ax2.plot(exponenten, zeiten, label="Potenzkurven")
    ax2.axhline(T_zykloide, color="k", ls="--", label="Zykloide")
    ax2.set_xlabel("Exponent p")
    ax2.set_ylabel("Laufzeit [s]")
    ax2.set_title("Laufzeit der Potenzkurven y = y1 (x/x1)^p")
    ax2.legend()
    plt.tight_layout()
    plt.show()


def direct_method():
    """3. Die direkte Methode (Zellen 9 von calculus_of_variations.ipynb)."""
    global ax, ergebnis, fig, n, start, th, x_gitter, y_opt, zeit_von
    n = 80
    x_gitter = x1 * np.linspace(0, 1, n + 2) ** 2           # dicht am Start, wo die Bahn steil ist


    def zeit_von(y_innen):
        y = np.concatenate([[0.0], y_innen, [y1]])
        return laufzeit(x_gitter, y)


    start = y1 * x_gitter[1:-1] / x1
    ergebnis = minimize(zeit_von, start, method="L-BFGS-B", bounds=[(1e-9, None)] * n, options={"maxiter": 5000})
    y_opt = np.concatenate([[0.0], ergebnis.x, [y1]])
    print(f"Minimierung: T = {ergebnis.fun:.5f} s nach {ergebnis.nit} Schritten, Zykloide exakt {T_zykloide:.5f} s")

    fig, ax = plt.subplots(figsize=(8, 4.5))
    th = np.linspace(0, theta1, 400)
    ax.plot(a * (th - np.sin(th)), a * (1 - np.cos(th)), "k-", lw=3, alpha=0.4, label="Zykloide")
    ax.plot(x_gitter, y_opt, "o-", ms=3, label="numerisch minimierter Polygonzug")
    ax.plot(x_gitter, y1 * x_gitter / x1, ":", label="Startwert (Gerade)")
    ax.invert_yaxis()
    ax.set_aspect("equal")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m], nach unten")
    ax.set_title("Direkte Methode gegen Euler–Lagrange")
    ax.legend()
    plt.show()


def noether():
    """4. Noether am Zentralkraftproblem (Zellen 12 von calculus_of_variations.ipynb)."""
    global ax, axes, bewegung, drehimpuls, energie, eps, farbe, fig, lsg, t, z0
    def bewegung(t, z, eps):
        x, y, vx, vy = z
        r3 = (x**2 + y**2) ** 1.5
        return [vx, vy, -x / r3 - eps * x, -y / r3 + eps * y]


    def energie(z, eps):
        x, y, vx, vy = z
        return 0.5 * (vx**2 + vy**2) - 1 / np.hypot(x, y) + 0.5 * eps * (x**2 - y**2)


    def drehimpuls(z):
        x, y, vx, vy = z
        return x * vy - y * vx


    z0 = [1.0, 0.0, 0.0, 0.8]
    t = np.linspace(0, 60, 3000)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for eps, farbe in [(0.0, "C0"), (0.01, "C1")]:
        lsg = solve_ivp(bewegung, (0, 60), z0, t_eval=t, args=(eps,), method="DOP853", rtol=1e-11, atol=1e-12)
        axes[0].plot(lsg.y[0], lsg.y[1], color=farbe, lw=0.7, label=f"ε = {eps}")
        axes[1].plot(t, energie(lsg.y, eps) - energie(z0, eps), color=farbe, label=f"ε = {eps}")
        axes[2].plot(t, drehimpuls(lsg.y), color=farbe, label=f"ε = {eps}")
    axes[0].set_aspect("equal")
    axes[0].set_title("Bahn")
    axes[0].set_xlabel("x")
    axes[0].set_ylabel("y")
    axes[1].set_title("Energie: Abweichung vom Startwert")
    axes[1].set_xlabel("Zeit")
    axes[2].set_title("Drehimpuls L_z")
    axes[2].set_xlabel("Zeit")
    for ax in axes:
        ax.legend()
    plt.tight_layout()
    plt.show()


def sphere_geodesics():
    """5. Geodäten auf der Kugel (Zellen 15 von calculus_of_variations.ipynb)."""
    global abstand, ax, ax2, c, dph, dth, fig, geodaete, lsg, normale, ph, punkte
    global r0, t, tempo, th, u, v0, w, z0
    def geodaete(t, z):
        th, ph, dth, dph = z
        return [dth, dph, np.sin(th) * np.cos(th) * dph**2, -2 / np.tan(th) * dth * dph]


    z0 = [1.0, 0.0, 0.3, 1.0]                                  # theta, phi, ihre Ableitungen
    tempo = np.sqrt(z0[2] ** 2 + np.sin(z0[0]) ** 2 * z0[3] ** 2)
    t = np.linspace(0, 2 * np.pi / tempo, 600)                 # eine volle Runde
    lsg = solve_ivp(geodaete, (0, t[-1]), z0, t_eval=t, method="DOP853", rtol=1e-11, atol=1e-12)
    th, ph, dth, dph = lsg.y
    punkte = np.array([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)])

    # Normale der Ebene aus Startpunkt und Startrichtung
    r0 = punkte[:, 0]
    v0 = np.array([np.cos(th[0]) * np.cos(ph[0]) * dth[0] - np.sin(th[0]) * np.sin(ph[0]) * dph[0],
                   np.cos(th[0]) * np.sin(ph[0]) * dth[0] + np.sin(th[0]) * np.cos(ph[0]) * dph[0],
                   -np.sin(th[0]) * dth[0]])
    normale = np.cross(r0, v0) / np.linalg.norm(np.cross(r0, v0))
    abstand = normale @ punkte
    c = np.sin(th) ** 2 * dph
    print(f"größter Abstand von der Ebene durch den Mittelpunkt: {np.abs(abstand).max():.1e}")
    print(f"Clairaut-Größe c: von {c.min():.10f} bis {c.max():.10f}")

    fig = plt.figure(figsize=(12, 5))
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    u, w = np.meshgrid(np.linspace(0, 2 * np.pi, 40), np.linspace(0, np.pi, 20))
    ax.plot_wireframe(np.cos(u) * np.sin(w), np.sin(u) * np.sin(w), np.cos(w), color="0.8", lw=0.5)
    ax.plot(*punkte, color="C3", lw=2, label="Geodäte")
    ax.set_box_aspect((1, 1, 1))
    ax.set_axis_off()
    ax.set_title("Geodäte auf der Einheitskugel")
    ax.legend()
    ax2 = fig.add_subplot(1, 2, 2)
    ax2.plot(t, abstand, label="Abstand von der Ebene")
    ax2.plot(t, c - c[0], label="c(t) − c(0)")
    ax2.set_xlabel("Parameter t")
    ax2.set_title("Ebene und Clairaut-Größe entlang der Bahn")
    ax2.legend()
    plt.tight_layout()
    plt.show()
