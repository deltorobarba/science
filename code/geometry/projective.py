"""Projektive Geometrie: Perspektive, homogene Koordinaten, Transformationen, Doppelverhältnis, klassische Sätze, Kegelschnitte, Cayley-Klein, Homographie, endliche Ebenen, Bloch-Kugel, Fubini-Study, Hopf-Faserung und Segre-Einbettung.

Für geometry.ipynb aus projectivegeometry.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: perspective, homogeneous, transformations, cross_ratio, classical_theorems, conics, cayley_klein, homography, finite_planes, projective_line, bloch_riemann, fubini_study, hopf, segre_veronese.
"""
import itertools
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon


def perspective():
    """23. Perspektive: Fluchtpunkte und Horizont (Zellen 4, 6 von projectivegeometry.ipynb)."""
    global K, P, R, anwenden, ax, bild, bloch, cx, cy, d, dlt, doppelverhaeltnis
    global f_px, farbe, fig, fluchtpunkt, fs_abstand, gerade_zeichnen, h, haar_zustand, hoehe, homographie_aus_4, horizont, kegelschnitt_zeichnen
    global ket, kollinear, kugel_aus_z, kugel_gitter, m, name, neigung, richtungen, riemann_z, rng, schnitt, seg
    global v, verbindung, x0, xs, z0
    # numpy, scipy und matplotlib sind in Colab vorinstalliert; es wird nichts nachinstalliert

    rng = np.random.default_rng(2026)


    def verbindung(p, q):
        """Gerade durch zwei Punkte (homogen): l = p × q."""
        return np.cross(p, q)


    def schnitt(l, m):
        """Schnittpunkt zweier Geraden: x = l × m."""
        return np.cross(l, m)


    def kollinear(p, q, r):
        """|det| der normierten Vektoren; null genau dann, wenn die drei Punkte (oder Geraden) inzident sind."""
        return abs(np.linalg.det(np.array([v / np.linalg.norm(v) for v in (p, q, r)])))


    def h(x, y):
        """Affiner Punkt -> homogene Koordinaten."""
        return np.array([x, y, 1.0])


    def anwenden(H, pts):
        """Homographie H auf affine Punkte der Form (N, 2) anwenden."""
        P = np.column_stack([pts, np.ones(len(pts))]) @ H.T
        return P[:, :2] / P[:, 2:3]


    def homographie_aus_4(src, dst):
        """Die Homographie, die vier Punkte src auf dst abbildet."""
        def rahmen(pts):
            P = np.column_stack([pts, np.ones(4)]).T                 # Spalten p1, ..., p4
            lam = np.linalg.solve(P[:, :3], P[:, 3])                 # p4 = λ1 p1 + λ2 p2 + λ3 p3
            return P[:, :3] * lam
        H = rahmen(np.asarray(dst, float)) @ np.linalg.inv(rahmen(np.asarray(src, float)))
        return H / H[2, 2]


    def dlt(src, dst, normieren=True, kondition=False):
        """Homographie aus N ≥ 4 Punktpaaren (Direct Linear Transform), wahlweise mit Hartley-Normierung.
    Mit kondition=True zusätzlich die Konditionszahl σ_max/σ_(n−1) des Gleichungssystems."""
        def T(pts):
            c = pts.mean(axis=0)
            s = np.sqrt(2) / np.mean(np.linalg.norm(pts - c, axis=1))
            return np.array([[s, 0, -s * c[0]], [0, s, -s * c[1]], [0, 0, 1]])
        T1, T2 = (T(src), T(dst)) if normieren else (np.eye(3), np.eye(3))
        a, b_ = anwenden(T1, src), anwenden(T2, dst)
        A = []
        for (x, y), (u, v) in zip(a, b_):                            # zwei Zeilen von x' × Hx = 0 pro Paar
            A.append([-x, -y, -1, 0, 0, 0, u * x, u * y, u])
            A.append([0, 0, 0, -x, -y, -1, v * x, v * y, v])
        _, sv, Vt = np.linalg.svd(np.array(A))
        H = Vt[-1].reshape(3, 3)                                     # kleinster Singulärvektor
        H = np.linalg.inv(T2) @ H @ T1
        return (H / H[2, 2], sv[0] / sv[-2]) if kondition else H / H[2, 2]


    def doppelverhaeltnis(a, b, c, d):
        """(A, B; C, D) für Koordinaten auf einer Geraden (reell oder komplex)."""
        return ((c - a) * (d - b)) / ((c - b) * (d - a))


    def kegelschnitt_zeichnen(ax, C, grenzen=(-3, 3, -3, 3), **kw):
        """Die Nullstellenmenge von (x, y, 1) C (x, y, 1)ᵀ in der affinen Karte als Höhenlinie zeichnen."""
        x = np.linspace(grenzen[0], grenzen[1], 600)
        y = np.linspace(grenzen[2], grenzen[3], 600)
        Xg, Yg = np.meshgrid(x, y)
        P = np.stack([Xg, Yg, np.ones_like(Xg)])
        Q = np.einsum("i...,ij,j...->...", P, C, P)
        ax.contour(Xg, Yg, Q, levels=[0], **kw)


    def gerade_zeichnen(ax, l, xlim, **kw):
        """Gerade l = (a, b, c) in der affinen Karte zeichnen."""
        a, b_, c = l
        if abs(b_) > 1e-12:
            x = np.array(xlim)
            ax.plot(x, -(a * x + c) / b_, **kw)
        else:
            ax.axvline(-c / a, **kw)


    # Quantenzustände als Strahlen
    def bloch(psi):
        """Bloch-Vektor eines (nicht unbedingt normierten) Qubit-Vektors."""
        a, b_ = psi / np.linalg.norm(psi)
        return np.array([2 * (np.conj(a) * b_).real, 2 * (np.conj(a) * b_).imag, abs(a) ** 2 - abs(b_) ** 2])


    def ket(r):
        """Ein Qubit-Vektor zum Bloch-Vektor r (Phase so gewählt, dass die erste Komponente reell ist)."""
        th, ph = np.arccos(np.clip(r[2], -1, 1)), np.arctan2(r[1], r[0])
        return np.array([np.cos(th / 2), np.exp(1j * ph) * np.sin(th / 2)])


    def riemann_z(psi):
        """Projektive Koordinate z = β/α ∈ ℂ ∪ {∞} des Strahls (α : β)."""
        return np.inf if abs(psi[0]) < 1e-14 else psi[1] / psi[0]


    def kugel_aus_z(z):
        """Inverse stereographische Projektion vom Südpol: z -> Punkt der Bloch-Kugel."""
        if np.isinf(z):
            return np.array([0, 0, -1.0])
        return np.array([2 * z.real, 2 * z.imag, 1 - abs(z) ** 2]) / (1 + abs(z) ** 2)


    def haar_zustand(N):
        g = rng.normal(size=N) + 1j * rng.normal(size=N)
        return g / np.linalg.norm(g)


    def fs_abstand(psi, phi):
        """Fubini-Study-Abstand arccos |<ψ|φ>| / (|ψ| |φ|)."""
        ov = abs(np.vdot(psi, phi)) / (np.linalg.norm(psi) * np.linalg.norm(phi))
        return np.arccos(np.clip(ov, 0, 1))


    def kugel_gitter(ax, alpha=0.15):
        u, v = np.mgrid[0:2 * np.pi:40j, 0:np.pi:20j]
        ax.plot_wireframe(np.cos(u) * np.sin(v), np.sin(u) * np.sin(v), np.cos(v), color="0.6", lw=0.4, alpha=alpha)
        ax.set_box_aspect((1, 1, 1))

    f_px, cx, cy = 800.0, 640.0, 360.0                               # Brennweite und Bildmitte [Pixel]
    K = np.array([[f_px, 0, cx], [0, f_px, cy], [0, 0, 1]])
    neigung = np.radians(8)                                          # Blick 8° nach unten (y zeigt nach unten)
    R = np.array([[1, 0, 0], [0, np.cos(neigung), -np.sin(neigung)], [0, np.sin(neigung), np.cos(neigung)]])
    P = K @ np.column_stack([R, np.zeros(3)])                        # Kamera im Ursprung: P = K [R | 0]
    hoehe = 1.6


    def bild(X):
        """Weltpunkte (N, 3) oder ein Punkt im Unendlichen (Richtung, w = 0) ins Bild projizieren."""
        X = np.atleast_2d(X)
        x = np.column_stack([X, np.ones(len(X))]) @ P.T
        return x[:, :2] / x[:, 2:3]


    def fluchtpunkt(d):
        v = P @ np.append(d, 0.0)                                    # Bild des Punktes im Unendlichen (d, 0)
        return v[:2] / v[2]


    horizont = np.linalg.inv(K).T @ R @ np.array([0, 1.0, 0])        # l = K^(−T) R n, n = Normale der Bodenebene
    richtungen = {"vorwärts (0, 0, 1)": np.array([0, 0, 1.0]), "diagonal (1, 0, 1)": np.array([1, 0, 1.0]),
                  "diagonal (−1, 0, 1)": np.array([-1, 0, 1.0])}

    fig, ax = plt.subplots(figsize=(11, 6.8))
    for x0 in np.arange(-4, 4.5, 1.0):                               # Linien in Blickrichtung
        seg = bild(np.array([[x0, hoehe, 2.0], [x0, hoehe, 400.0]]))
        ax.plot(seg[:, 0], seg[:, 1], color="tab:blue", lw=1)
    for z0 in [2, 3, 4, 6, 8, 12, 20, 40]:                           # Querlinien
        seg = bild(np.array([[-4, hoehe, z0], [4, hoehe, z0]]))
        ax.plot(seg[:, 0], seg[:, 1], color="tab:blue", lw=0.6, alpha=0.6)
    for x0 in np.arange(-12, 5, 2.0):                                # Diagonalen in Richtung (1, 0, 1) und (−1, 0, 1)
        seg = bild(np.array([[x0, hoehe, 2.0], [x0 + 300, hoehe, 302.0]]))
        ax.plot(seg[:, 0], seg[:, 1], color="tab:orange", lw=0.7, alpha=0.7)
        seg = bild(np.array([[-x0, hoehe, 2.0], [-x0 - 300, hoehe, 302.0]]))
        ax.plot(seg[:, 0], seg[:, 1], color="tab:green", lw=0.7, alpha=0.7)
    xs = np.array([-600, 1900])
    ax.plot(xs, -(horizont[0] * xs + horizont[2]) / horizont[1], "k--", lw=1, label="Horizont l = K^(−T) R n")
    for (name, d), m, farbe in zip(richtungen.items(), ["o", "s", "^"], ["tab:blue", "tab:orange", "tab:green"]):
        v = fluchtpunkt(d)
        ax.plot(*v, m, ms=10, color=farbe, mec="k", label=f"Fluchtpunkt {name}: ({v[0]:.0f}, {v[1]:.0f})")
        print(f"Fluchtpunkt {name:22s}: ({v[0]:8.1f}, {v[1]:6.1f}) px, liegt auf dem Horizont: "
              f"{abs(horizont @ np.append(v, 1)) / np.linalg.norm(horizont[:2]) < 1e-9}")
    ax.add_patch(plt.Rectangle((0, 0), 1280, 720, fill=False, ec="0.3", lw=1.5))
    ax.set_xlim(-600, 1900); ax.set_ylim(950, 150)                   # Bildkoordinaten: v nach unten
    ax.set_aspect("equal")
    ax.set_xlabel("Bildkoordinate u [Pixel]"); ax.set_ylabel("Bildkoordinate v [Pixel]")
    ax.set_title("Bodengitter durch eine Lochkamera (Rahmen: Bildsensor 1280 × 720)")
    ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2)
    plt.show()


def homogeneous():
    """24. Homogene Koordinaten: Verbindung, Schnitt, Punkte im Unendlichen (Zellen 9 von projectivegeometry.ipynb)."""
    global ax, ax2, d, farbe, fig, gx, gy, l, l1, l2, l3, name
    global p, p12, p13, p23, q, t, x, y
    fig = plt.figure(figsize=(15, 5.4))
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    # Ebene w = 1 (die affine Karte) und Strahlen durch den Ursprung
    gx, gy = np.meshgrid(np.linspace(-2, 2, 2), np.linspace(-2, 2, 2))
    ax.plot_surface(gx, gy, np.ones_like(gx), alpha=0.15, color="tab:blue")
    for (x, y), farbe in zip([(1.5, 0.5), (-1.0, 1.2), (0.3, -1.5)], ["tab:red", "tab:green", "tab:purple"]):
        t = np.linspace(-1.3, 1.3, 2)
        ax.plot(t * x, t * y, t * 1, color=farbe, lw=1.5)
        ax.scatter([x], [y], [1], color=farbe, s=30)
        ax.text(x, y, 1.15, f"({x:g}:{y:g}:1)", fontsize=8)
    d = np.array([1.0, 0.5, 0.0])                                    # Richtung in der Ebene w = 0: Punkt im Unendlichen
    t = np.linspace(-2, 2, 2)
    ax.plot(t * d[0], t * d[1], t * d[2], "k--", lw=1.5)
    ax.text(2 * d[0], 2 * d[1], 0.1, "(1:0.5:0) im Unendlichen", fontsize=8)
    ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("w")
    ax.set_title("ℝP²: jede Gerade durch 0 ist ein Punkt;\nwer die Ebene w = 1 nicht trifft, liegt im Unendlichen", fontsize=10)

    l1, l2, l3 = np.array([1, -2, 1.0]), np.array([1, -2, -2.0]), np.array([2, 1, -4.0])
    p12, p13, p23 = schnitt(l1, l2), schnitt(l1, l3), schnitt(l2, l3)
    print("l1 × l2 =", p12, "-> w = 0: Punkt im Unendlichen in Richtung", p12[:2] / np.linalg.norm(p12[:2]))
    print("liegt auf der Geraden im Unendlichen (0, 0, 1):", np.isclose(np.array([0, 0, 1.0]) @ p12, 0))
    print("l1 × l3 =", p13, "-> affin", p13[:2] / p13[2])
    print("Verbindungsgerade der beiden Schnittpunkte auf l3:", verbindung(p13, p23) / verbindung(p13, p23)[0] * l3[0],
          "= l3 bis auf einen Faktor:", np.allclose(np.cross(verbindung(p13, p23), l3), 0))
    q = h(1.0, 2.0)                                                  # ein dritter Punkt auf l3: 2·1 + 2 − 4 = 0
    print(f"Kollinearität |det| von zwei Schnittpunkten und (1, 2): {kollinear(p13, p23, q):.1e}")

    ax2 = fig.add_subplot(1, 2, 2)
    for l, name in [(l1, "l1: x − 2y + 1 = 0"), (l2, "l2: x − 2y − 2 = 0"), (l3, "l3: 2x + y − 4 = 0")]:
        gerade_zeichnen(ax2, l, (-4, 6), label=name)
    for p, name in [(p13, "l1 ∩ l3"), (p23, "l2 ∩ l3")]:
        ax2.plot(*(p[:2] / p[2]), "ko")
        ax2.annotate(name, p[:2] / p[2], xytext=(6, 6), textcoords="offset points")
    ax2.annotate("l1 ∩ l2 = (2 : 1 : 0)\nim Unendlichen", xy=(5.6, 2.8), xytext=(2.2, 3.6),
                 arrowprops=dict(arrowstyle="->"), fontsize=9)
    ax2.set_xlim(-4, 6); ax2.set_ylim(-3, 4); ax2.set_aspect("equal")
    ax2.set_xlabel("x"); ax2.set_ylabel("y"); ax2.set_title("Affine Karte w = 1")
    ax2.legend(loc="lower right")
    plt.tight_layout()
    plt.show()


def transformations():
    """25. Die Hierarchie der Transformationen (Zellen 12 von projectivegeometry.ipynb)."""
    global H, L, Rot, W, abbildungen, ax, axes, dv, fig, g, gitter, kreis
    global messen, name, par, punkte, quadrat, teil, w
    quadrat = np.array([[0, 0], [1, 0], [1, 1], [0, 1.0]])
    w = np.radians(30)
    Rot = np.array([[np.cos(w), -np.sin(w)], [np.sin(w), np.cos(w)]])
    abbildungen = {
        "euklidisch": np.block([[Rot, np.array([[0.4], [0.2]])], [np.zeros((1, 2)), np.ones((1, 1))]]),
        "Ähnlichkeit": np.block([[1.5 * Rot, np.array([[0.4], [0.2]])], [np.zeros((1, 2)), np.ones((1, 1))]]),
        "affin": np.array([[1.2, 0.6, 0.1], [0.1, 0.8, 0.2], [0, 0, 1.0]]),
        "projektiv": homographie_aus_4(quadrat, np.array([[0, 0], [1.6, 0.2], [1.1, 1.0], [0.2, 0.8]])),
    }
    print("projektive Matrix bildet die vier Ecken richtig ab:",
          np.allclose(anwenden(abbildungen["projektiv"], quadrat), [[0, 0], [1.6, 0.2], [1.1, 1.0], [0.2, 0.8]]))

    gitter = [np.column_stack([np.full(50, s), np.linspace(0, 1, 50)]) for s in np.linspace(0, 1, 6)] + \
             [np.column_stack([np.linspace(0, 1, 50), np.full(50, s)]) for s in np.linspace(0, 1, 6)]
    kreis = 0.5 + 0.3 * np.column_stack([np.cos(np.linspace(0, 2 * np.pi, 200)), np.sin(np.linspace(0, 2 * np.pi, 200))])
    punkte = np.array([[0, 0], [0.25, 0], [0.5, 0], [1, 0.0]])        # vier Punkte auf der unteren Kante


    def messen(H):
        A, B, D = anwenden(H, np.array([[0, 0], [1, 0], [0, 1.0]]))
        winkel = np.degrees(np.arccos((B - A) @ (D - A) / np.linalg.norm(B - A) / np.linalg.norm(D - A)))
        links, rechts = anwenden(H, np.array([[0, 0], [0, 1.0]])), anwenden(H, np.array([[1, 0], [1, 1.0]]))
        r1, r2 = links[1] - links[0], rechts[1] - rechts[0]
        parallel = abs(r1[0] * r2[1] - r1[1] * r2[0]) / np.linalg.norm(r1) / np.linalg.norm(r2) < 1e-9
        q = anwenden(H, punkte)
        s = np.linalg.norm(q - q[0], axis=1)                         # Koordinate längs der Bildgeraden
        teil = s[1] / s[2]                                           # Teilverhältnis AB/AC (im Original 0.5)
        return np.linalg.norm(B - A), winkel, parallel, teil, doppelverhaeltnis(*s)


    print(f"\n{'':12s} {'Länge':>7s} {'Winkel':>8s} {'parallel':>9s} {'Teilverh.':>10s} {'Doppelverh.':>12s}")
    print(f"{'Original':12s} {1:7.3f} {90:8.2f} {'ja':>9s} {0.5:10.3f} {doppelverhaeltnis(0, 0.25, 0.5, 1):12.4f}")
    fig, axes = plt.subplots(1, 4, figsize=(17, 4.4))
    for ax, (name, H) in zip(axes, abbildungen.items()):
        L, W, par, teil, dv = messen(H)
        print(f"{name:12s} {L:7.3f} {W:8.2f} {'ja' if par else 'nein':>9s} {teil:10.3f} {dv:12.4f}")
        for g in gitter:
            ax.plot(*anwenden(np.eye(3), g).T, color="0.8", lw=0.6)
            ax.plot(*anwenden(H, g).T, color="tab:blue", lw=0.8)
        ax.plot(*anwenden(H, kreis).T, color="tab:red")
        ax.plot(*anwenden(H, punkte).T, "ko", ms=4)
        ax.set_aspect("equal"); ax.set_title(name)
        ax.set_xlabel("x"); ax.set_ylabel("y")
    plt.suptitle("Quadratgitter mit Kreis (grau: Original); schwarz: vier Punkte für das Doppelverhältnis", y=1.02)
    plt.tight_layout()
    plt.show()


def cross_ratio():
    """26. Das Doppelverhältnis und die Möbius-Abbildungen (Zellen 15 von projectivegeometry.ipynb)."""
    global a, abb, ax, axes, b_, c, d, dv, farbe, fig, kreis, kreispunkte
    global lam, moebius, s, t, teil, titel, x, y, zline
    x = np.array([0.0, 1.0, 3.0, 4.0])
    teil, dv = [], []
    while len(dv) < 2000:
        a, b_, c, d = rng.normal(size=4)
        if np.all(np.sign(c * x + d) == np.sign(c * x[0] + d)):      # kein Pol zwischen den Punkten
            y = (a * x + b_) / (c * x + d)
            teil.append((y[2] - y[0]) / (y[2] - y[1]))
            dv.append(doppelverhaeltnis(*y))
    teil, dv = np.array(teil), np.array(dv)
    lam = doppelverhaeltnis(*x)
    print(f"Doppelverhältnis vorher {lam:.6f}, nachher {dv.min():.6f} bis {dv.max():.6f}")
    print(f"Teilverhältnis AC/BC vorher {(x[2] - x[0]) / (x[2] - x[1]):.3f}, nachher Median {np.median(teil):.3f}, "
          f"Bereich {np.percentile(teil, 5):.2f} bis {np.percentile(teil, 95):.2f} (5 %- bis 95 %-Perzentil)")
    print("Die sechs Werte unter den 24 Vertauschungen:", sorted({round(float(v), 4) for v in
          [doppelverhaeltnis(*x[list(pm)]) for pm in itertools.permutations(range(4))]}))
    print("λ, 1/λ, 1−λ, 1/(1−λ), λ/(λ−1), (λ−1)/λ:", np.round(sorted([lam, 1 / lam, 1 - lam, 1 / (1 - lam), lam / (lam - 1), (lam - 1) / lam]), 4))

    moebius = lambda z: (2 * z + 1j) / (z + 2.2 - 1j)
    kreispunkte = np.exp(1j * np.array([0.3, 1.4, 2.9, 4.6]))         # vier Punkte auf dem Einheitskreis
    print(f"\nDoppelverhältnis von vier Punkten eines Kreises: {doppelverhaeltnis(*kreispunkte):.4f} (reell), "
          f"nach der Möbius-Abbildung: {doppelverhaeltnis(*moebius(kreispunkte)):.4f}")

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.8))
    axes[0].hist(teil, bins=np.linspace(0, 12, 97), color="0.5", label="Teilverhältnis AC/BC")
    axes[0].axvline(lam, color="tab:red", lw=3, label=f"Doppelverhältnis: immer {lam:.3f}")
    axes[0].set_xlabel("Wert"); axes[0].set_ylabel("Anzahl Homographien")
    axes[0].set_title("2000 zufällige Homographien der Geraden"); axes[0].legend()
    t = np.linspace(-1, 1, 400)
    for s in np.linspace(-1, 1, 9):
        for zline, farbe in [(s + 1j * t, "tab:blue"), (t + 1j * s, "tab:orange")]:
            axes[1].plot(zline.real, zline.imag, color=farbe, lw=0.8)
            axes[2].plot(moebius(zline).real, moebius(zline).imag, color=farbe, lw=0.8)
    for ax, abb, titel in [(axes[1], lambda z: z, "Gitter in ℂ"), (axes[2], moebius, "Bild unter z ↦ (2z + i)/(z + 2.2 − i)")]:
        kreis = abb(np.exp(1j * np.linspace(0, 2 * np.pi, 300)))
        ax.plot(kreis.real, kreis.imag, "k", lw=1.5)
        ax.plot(abb(kreispunkte).real, abb(kreispunkte).imag, "ro")
        ax.set_aspect("equal"); ax.set_title(titel)
        ax.set_xlabel("Re z"); ax.set_ylabel("Im z")
    plt.tight_layout()
    plt.show()


def classical_theorems():
    """27. Desargues, Pappus, Pascal, Brianchon (Zellen 18 von projectivegeometry.ipynb)."""
    global A, B, C, D, ELLIPSE, M, Pp, S, V, X, X2, Y
    global _, a, aff, auf_ellipse, ax, axes, b_, brianchon, c, desargues, farbe, fig
    global i, k, kompakt, name, p, pappus, pascal, q, saetze, satz, werte
    def desargues(r):
        O = h(*r.normal(size=2))
        A, B, C = (h(*r.normal(size=2)) for _ in range(3))
        A2, B2, C2 = (O + r.uniform(0.5, 2.5) * (X - O) for X in (A, B, C))   # perspektiv zu O
        S = [schnitt(verbindung(A, B), verbindung(A2, B2)), schnitt(verbindung(B, C), verbindung(B2, C2)),
             schnitt(verbindung(C, A), verbindung(C2, A2))]
        return kollinear(*S), dict(O=O, Dreieck1=(A, B, C), Dreieck2=(A2, B2, C2), S=S)


    def pappus(r):
        g1, g2 = [h(*r.normal(size=2)), h(*r.normal(size=2))], [h(*r.normal(size=2)), h(*r.normal(size=2))]
        A, B, C = (g1[0] + t * (g1[1] - g1[0]) for t in r.uniform(-1, 2, 3))
        a, b_, c = (g2[0] + t * (g2[1] - g2[0]) for t in r.uniform(-1, 2, 3))
        S = [schnitt(verbindung(A, b_), verbindung(a, B)), schnitt(verbindung(A, c), verbindung(a, C)),
             schnitt(verbindung(B, c), verbindung(b_, C))]
        return kollinear(*S), dict(Punkte=(A, B, C, a, b_, c), S=S)


    ELLIPSE = np.diag([1 / 2.0 ** 2, 1 / 1.2 ** 2, -1.0])            # x²/4 + y²/1.44 = 1


    def auf_ellipse(phi):
        return np.array([2.0 * np.cos(phi), 1.2 * np.sin(phi), 1.0])


    def pascal(r):
        P = [auf_ellipse(t) for t in np.sort(r.uniform(0, 2 * np.pi, 6))]
        S = [schnitt(verbindung(P[i], P[i + 1]), verbindung(P[i + 3], P[(i + 4) % 6])) for i in range(3)]
        return kollinear(*S), dict(P=P, S=S)


    def brianchon(r):
        P = [auf_ellipse(t) for t in np.sort(r.uniform(0, 2 * np.pi, 6))]
        T = [ELLIPSE @ p for p in P]                                 # Tangenten
        V = [schnitt(T[i], T[(i + 1) % 6]) for i in range(6)]        # Ecken des umbeschriebenen Sechsecks
        D = [verbindung(V[i], V[i + 3]) for i in range(3)]           # Hauptdiagonalen
        return kollinear(*D), dict(P=P, V=V, D=D)


    saetze = {"Desargues": desargues, "Pappus": pappus, "Pascal": pascal, "Brianchon": brianchon}
    for name, satz in saetze.items():
        werte = [satz(rng)[0] for _ in range(2000)]
        print(f"{name:10s}: |det| über 2000 zufällige Konfigurationen höchstens {max(werte):.1e}")

    aff = lambda X: X[:2] / X[2]


    def kompakt(satz, schluessel, grenze):
        """Erste Konfiguration (Startwert 0, 1, ...), deren Schnittpunkte im Bildausschnitt liegen."""
        for start in range(500):
            _, k = satz(np.random.default_rng(start))
            if all(np.all(np.abs(aff(X)) < grenze) for X in k[schluessel]):
                return k


    fig, axes = plt.subplots(2, 2, figsize=(13, 11))
    # Desargues
    k = kompakt(desargues, "S", 4)
    ax = axes[0, 0]
    for D, farbe in [(k["Dreieck1"], "tab:blue"), (k["Dreieck2"], "tab:orange")]:
        ax.add_patch(Polygon([aff(X) for X in D], fill=False, ec=farbe, lw=1.5))
    for X, X2 in zip(k["Dreieck1"], k["Dreieck2"]):
        ax.plot(*np.array([aff(k["O"]), aff(X2)]).T, color="0.6", lw=0.8)
    ax.plot(*aff(k["O"]), "ko"); ax.annotate("O", aff(k["O"]), xytext=(4, 4), textcoords="offset points")
    S = np.array([aff(s) for s in k["S"]])
    ax.plot(*S.T, "rs-", label="Schnittpunkte entsprechender Seiten")
    ax.set_title("Desargues"); ax.legend(fontsize=8)
    # Pappus
    k = kompakt(pappus, "S", 3)
    ax = axes[0, 1]
    A, B, C, a, b_, c = [aff(X) for X in k["Punkte"]]
    ax.plot(*np.array([A, B, C]).T, "o-", color="tab:blue"); ax.plot(*np.array([a, b_, c]).T, "o-", color="tab:orange")
    for X, Y in [(A, b_), (a, B), (A, c), (a, C), (B, c), (b_, C)]:
        ax.plot(*np.array([X, Y]).T, color="0.6", lw=0.8)
    S = np.array([aff(s) for s in k["S"]])
    ax.plot(*S.T, "rs-", label="Pappus-Gerade"); ax.set_title("Pappus"); ax.legend(fontsize=8)
    # Pascal
    k = kompakt(pascal, "S", 5)
    ax = axes[1, 0]
    kegelschnitt_zeichnen(ax, ELLIPSE, (-6, 6, -6, 6), colors="k")
    Pp = np.array([aff(p) for p in k["P"]])
    for i in range(6):
        p, q = k["P"][i], k["P"][(i + 1) % 6]
        ax.plot(*np.array([aff(p), aff(q)]).T, color="tab:blue")
    S = np.array([aff(s) for s in k["S"]])
    for i in range(3):                                               # Seiten bis zu den Schnittpunkten verlängern
        for p in (k["P"][i], k["P"][i + 1], k["P"][i + 3], k["P"][(i + 4) % 6]):
            ax.plot(*np.array([aff(p), S[i]]).T, color="0.75", lw=0.6, ls=":")
    ax.plot(*Pp.T, "ko"); ax.plot(*S.T, "rs-", label="Pascal-Gerade")
    ax.set_xlim(-6, 6); ax.set_ylim(-6, 6); ax.set_aspect("equal"); ax.set_title("Pascal"); ax.legend(fontsize=8)
    # Brianchon
    _, k = brianchon(np.random.default_rng(4))
    ax = axes[1, 1]
    kegelschnitt_zeichnen(ax, ELLIPSE, (-6, 6, -6, 6), colors="k")
    V = np.array([aff(v) for v in k["V"]])
    ax.add_patch(Polygon(V, fill=False, ec="tab:blue"))
    for i in range(3):
        ax.plot(*np.array([V[i], V[i + 3]]).T, color="tab:orange")
    M = schnitt(k["D"][0], k["D"][1])
    ax.plot(*aff(M), "rs", ms=8, label="gemeinsamer Punkt der Diagonalen")
    ax.plot(*np.array([aff(p) for p in k["P"]]).T, "ko", ms=4)
    ax.set_xlim(-6, 6); ax.set_ylim(-6, 6); ax.set_aspect("equal"); ax.set_title("Brianchon"); ax.legend(fontsize=8)
    for ax in axes.flat:
        ax.set_xlabel("x"); ax.set_ylabel("y")
    plt.tight_layout()
    plt.show()


def conics():
    """28. Kegelschnitte: eine Kurve, drei Gesichter (Zellen 21 von projectivegeometry.ipynb)."""
    global C, C2, H, I, KREIS, Pp, T, _, a, a_, ax, axes
    global b_, c_, faelle, farbe, fig, fuss, m, name, polare, rad, richt, s
    global typ
    KREIS = np.diag([1.0, 1.0, -1.0])
    faelle = {"Ellipse": 0.5, "Parabel": 1.0, "Hyperbel": 2.0}        # H schickt die Gerade x = −1/a ins Unendliche


    def typ(C):
        """Affiner Typ aus dem oberen 2×2-Block (Schnitt mit der Geraden im Unendlichen)."""
        d = np.linalg.det(C[:2, :2])
        return "Ellipse" if d > 1e-9 else ("Hyperbel" if d < -1e-9 else "Parabel")


    fig, axes = plt.subplots(1, 4, figsize=(18, 4.6))
    ax = axes[0]
    kegelschnitt_zeichnen(ax, KREIS, (-3, 3, -3, 3), colors="k")
    for (name, a), farbe in zip(faelle.items(), ["tab:green", "tab:orange", "tab:red"]):
        ax.axvline(-1 / a, color=farbe, ls="--", label=f"{name}: x = {-1 / a:g} wird zur Geraden im Unendlichen")
    Pp = h(2.0, 0.8)
    polare = KREIS @ Pp
    gerade_zeichnen(ax, polare, (-3, 3), color="tab:purple", label="Polare von P")
    # Berührpunkte: Schnitt der Polaren mit dem Kreis
    a_, b_, c_ = polare
    richt = np.array([-b_, a_]) / np.hypot(a_, b_)
    fuss = -c_ * np.array([a_, b_]) / (a_ ** 2 + b_ ** 2)
    s = np.sqrt(1 - fuss @ fuss)
    for T in (fuss + s * richt, fuss - s * richt):
        ax.plot(*np.array([Pp[:2], T]).T, color="tab:purple", lw=0.8)
        ax.plot(*T, "o", color="tab:purple")
    ax.plot(*Pp[:2], "ko"); ax.annotate("P", Pp[:2], xytext=(5, 5), textcoords="offset points")
    ax.set_xlim(-3, 3); ax.set_ylim(-3, 3); ax.set_aspect("equal")
    ax.set_title("Kreis, Pol und Polare"); ax.legend(fontsize=7, loc="lower left")
    for ax, ((name, a), farbe) in zip(axes[1:], zip(faelle.items(), ["tab:green", "tab:orange", "tab:red"])):
        H = np.array([[1, 0, 0], [0, 1, 0], [a, 0, 1.0]])
        C2 = np.linalg.inv(H).T @ KREIS @ np.linalg.inv(H)
        kegelschnitt_zeichnen(ax, C2, (-6, 6, -6, 6), colors=farbe)
        ax.set_xlim(-6, 6); ax.set_ylim(-6, 6); ax.set_aspect("equal")
        ax.set_title(f"Bild unter H mit a = {a:g}: {typ(C2)}")
        print(f"a = {a:g}: Typ {typ(C2):8s}, Determinante des 2×2-Blocks {np.linalg.det(C2[:2, :2]):+.3f}")
    for ax in axes:
        ax.set_xlabel("x"); ax.set_ylabel("y")
    plt.tight_layout()
    plt.show()

    I = np.array([1, 1j, 0])
    for _ in range(3):
        m, rad = rng.normal(size=2), rng.uniform(0.5, 2)
        C = np.array([[1, 0, -m[0]], [0, 1, -m[1]], [-m[0], -m[1], m @ m - rad ** 2]])   # (x−m)² − r² = 0
        print(f"Kreis um ({m[0]:+.2f}, {m[1]:+.2f}), Radius {rad:.2f}: Iᵀ C I = {I @ C @ I:.1e}")
    print(f"Ellipse x²/4 + y² = 1: Iᵀ C I = {I @ np.diag([0.25, 1, -1]) @ I:.2f} (kein Kreis)")


def cayley_klein():
    """29. Cayley–Klein: hyperbolische Geometrie im Kreis (Zellen 24 von projectivegeometry.ipynb)."""
    global B, P_, _, a, a2, ax, axes, boost, c, c2, e, farbe
    global fig, g, hyperbolischer_kreis, i, klein_abstand, kreis, p, phi, q, r_, schritte, t
    global x0
    def klein_abstand(p, q):
        """Hyperbolischer Abstand im Klein-Modell: ½ ln (a, b; p, q) mit den Randpunkten a, b der Sehne durch p, q."""
        d = q - p
        A, B, C = d @ d, 2 * p @ d, p @ p - 1                      # |p + t d|² = 1
        t1, t2 = np.sort(np.roots([A, B, C]).real)                   # t1 < 0 < 1 < t2: Randpunkte a, b
        return 0.5 * np.log(((1 - t1) * t2) / ((0 - t1) * (t2 - 1)))


    def boost(u):
        """Homographie, die den Einheitskreis festhält: Lorentz-Boost in x-Richtung (Form x² + y² − w²)."""
        return np.array([[np.cosh(u), 0, np.sinh(u)], [0, 1, 0], [np.sinh(u), 0, np.cosh(u)]])


    p, q, r_ = np.array([-0.3, 0.1]), np.array([0.2, 0.25]), np.array([0.7, 0.4])
    r_ = p + 1.6 * (q - p)                                           # dritter Punkt auf derselben Sehne
    print(f"Additivität: d(p,q) + d(q,r) = {klein_abstand(p, q) + klein_abstand(q, r_):.6f}, d(p,r) = {klein_abstand(p, r_):.6f}")
    print(f"d(0, ρ) gegen artanh ρ: {klein_abstand(np.zeros(2), np.array([0.9, 0])):.6f} gegen {np.arctanh(0.9):.6f}")
    B = boost(0.8)
    for _ in range(3):
        a, c = (rng.uniform(-0.6, 0.6, 2) for _ in range(2))
        a2, c2 = anwenden(B, np.array([a, c]))
        print(f"Boost: hyperbolisch {klein_abstand(a, c):.5f} -> {klein_abstand(a2, c2):.5f}, "
              f"euklidisch {np.linalg.norm(a - c):.4f} -> {np.linalg.norm(a2 - c2):.4f}")


    def hyperbolischer_kreis(m, rad, n=200):
        """Punkte mit hyperbolischem Abstand rad von m (Bisektion längs Strahlen)."""
        pts = []
        for phi in np.linspace(0, 2 * np.pi, n):
            e = np.array([np.cos(phi), np.sin(phi)])
            lo, hi = 0.0, (-(m @ e) + np.sqrt((m @ e) ** 2 - m @ m + 1)) * (1 - 1e-12)
            for _ in range(60):
                mid = (lo + hi) / 2
                lo, hi = (mid, hi) if klein_abstand(m, m + mid * e) < rad else (lo, mid)
            pts.append(m + lo * e)
        return np.array(pts)


    fig, axes = plt.subplots(1, 2, figsize=(13, 6.2))
    ax = axes[0]
    ax.add_patch(plt.Circle((0, 0), 1, fill=False, color="k"))
    for x0, farbe in zip([0, 0.5, 0.8, 0.95], ["tab:blue", "tab:orange", "tab:green", "tab:red"]):
        kreis = hyperbolischer_kreis(np.array([x0, 0.0]), 0.5)
        ax.plot(*kreis.T, color=farbe, label=f"Mittelpunkt x = {x0}")
        ax.plot(x0, 0, ".", color=farbe)
    schritte = np.tanh(0.5 * np.arange(0, 7))                        # hyperbolisch gleich weit: Abstand 0.5
    ax.plot(schritte, -0.6 * np.ones_like(schritte), "k|", ms=12)
    ax.plot(-schritte, -0.6 * np.ones_like(schritte), "k|", ms=12)
    ax.text(-0.95, -0.72, "Marken im hyperbolischen Abstand 0.5 (auf y = −0.6 verschoben)", fontsize=8)
    ax.set_aspect("equal"); ax.set_xlim(-1.05, 1.05); ax.set_ylim(-1.05, 1.05)
    ax.set_title("Kreise mit hyperbolischem Radius 0.5"); ax.legend(fontsize=8, loc="upper left")
    ax = axes[1]
    ax.add_patch(plt.Circle((0, 0), 1, fill=False, color="k"))
    g = [np.array([-0.6, -0.8]), np.array([0.6, -0.8])]              # eine Gerade (Sehne)
    ax.plot(*np.array(g).T, color="tab:blue", lw=2, label="Gerade g")
    P_ = np.array([0.0, 0.3])
    ax.plot(*P_, "ko"); ax.annotate("P", P_, xytext=(5, 5), textcoords="offset points")
    for i, phi in enumerate(np.linspace(-0.55, 0.55, 9)):          # Sehnen durch P, die g im Inneren nicht treffen
        e = np.array([np.cos(phi), np.sin(phi)])
        t = np.roots([1, 2 * P_ @ e, P_ @ P_ - 1]).real
        ax.plot(*np.array([P_ + t[0] * e, P_ + t[1] * e]).T, color="tab:orange", lw=0.8,
                label="Geraden durch P, die g nicht schneiden" if i == 0 else None)
    ax.set_aspect("equal"); ax.set_xlim(-1.05, 1.05); ax.set_ylim(-1.05, 1.05)
    ax.set_title("Unendlich viele Parallelen durch P"); ax.legend(fontsize=8, loc="upper left")
    for ax in axes:
        ax.set_xlabel("x"); ax.set_ylabel("y")
    plt.tight_layout()
    plt.show()


def homography():
    """30. Computer Vision: Homographie schätzen und entzerren (Zellen 27 von projectivegeometry.ipynb)."""
    global H_est, H_rekt, H_wahr, Kc, Rc, _, aussen, axes, bild_ecken, drehung, e, ecken
    global farbe, fehler, feld, fig, gemessen, i, idx, j, kante, kond, n_feld, name
    global norm_, s, sigmas, tc
    Kc = np.array([[1000, 0, 640], [0, 1000, 480], [0, 0, 1.0]])
    def drehung(ax_, w):
        c, s = np.cos(w), np.sin(w)
        return {"x": np.array([[1, 0, 0], [0, c, -s], [0, s, c]]), "y": np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])}[ax_]
    Rc = drehung("y", np.radians(20)) @ drehung("x", np.radians(-50))
    tc = np.array([-0.4, -0.3, 1.6])
    H_wahr = Kc @ np.column_stack([Rc[:, 0], Rc[:, 1], tc])          # Ebene Z = 0 -> Bild: H = K [r1 r2 t]
    H_wahr /= H_wahr[2, 2]

    n_feld, kante = 8, 0.1                                           # 8 × 8 Felder zu 10 cm
    ecken = np.array([[i * kante, j * kante] for j in range(n_feld + 1) for i in range(n_feld + 1)])
    bild_ecken = anwenden(H_wahr, ecken)

    aussen = np.array([[0, 0], [0.8, 0], [0.8, 0.8], [0, 0.8]])
    H_rekt = homographie_aus_4(anwenden(H_wahr, aussen), aussen * 1000)   # Bild -> entzerrtes Quadrat (800 px)

    fig, axes = plt.subplots(1, 3, figsize=(18, 5.4))
    for i, j in itertools.product(range(n_feld), repeat=2):
        feld = np.array([[i, j], [i + 1, j], [i + 1, j + 1], [i, j + 1]]) * kante
        farbe = "0.15" if (i + j) % 2 else "0.9"
        axes[0].add_patch(Polygon(anwenden(H_wahr, feld), fc=farbe, ec="0.5", lw=0.3))
        axes[1].add_patch(Polygon(anwenden(H_rekt @ H_wahr, feld), fc=farbe, ec="0.5", lw=0.3))
    axes[0].plot(*anwenden(H_wahr, aussen).T, "ro", ms=6, label="die vier Ecken für die Entzerrung")
    axes[0].set_xlim(0, 1280); axes[0].set_ylim(960, 0); axes[0].set_aspect("equal")
    axes[0].set_xlabel("u [Pixel]"); axes[0].set_ylabel("v [Pixel]"); axes[0].set_title("Kamerabild"); axes[0].legend(fontsize=8)
    axes[1].set_xlim(-50, 850); axes[1].set_ylim(850, -50); axes[1].set_aspect("equal")
    axes[1].set_xlabel("x [mm]"); axes[1].set_ylabel("y [mm]"); axes[1].set_title("Entzerrt mit der Homographie aus 4 Ecken")

    sigmas = np.array([0.1, 0.3, 1, 3, 10])
    fehler = {True: [], False: []}
    for s in sigmas:
        for norm_ in (True, False):
            e = []
            for _ in range(100):
                idx = rng.choice(len(ecken), 30, replace=False)
                gemessen = bild_ecken[idx] + s * rng.normal(size=(30, 2))
                H_est = dlt(ecken[idx], gemessen, normieren=norm_)
                e.append(np.sqrt(np.mean(np.sum((anwenden(H_est, ecken) - bild_ecken) ** 2, axis=1))))
            fehler[norm_].append(np.mean(e))
    idx = rng.choice(len(ecken), 30, replace=False)
    for norm_, name in [(True, "mit Normierung"), (False, "ohne Normierung")]:
        axes[2].loglog(sigmas, fehler[norm_], "o-", label=f"DLT {name}")
        _, kond = dlt(ecken[idx], bild_ecken[idx] + rng.normal(size=(30, 2)), normieren=norm_, kondition=True)
        print(f"DLT {name:16s}: Konditionszahl {kond:9.2e}, mittlerer Übertragungsfehler {np.round(fehler[norm_], 3)} px "
              f"für σ = {sigmas}")
    axes[2].loglog(sigmas, sigmas * fehler[True][0] / sigmas[0], "k--", lw=1, label="∝ σ")
    axes[2].set_xlabel("Pixelrauschen σ [Pixel]"); axes[2].set_ylabel("RMS-Fehler über alle 81 Ecken [Pixel]")
    axes[2].set_title("Schätzung aus 30 verrauschten Punktpaaren"); axes[2].legend()
    plt.tight_layout()
    plt.show()


def finite_planes():
    """31. Endliche projektive Ebenen: Fano-Ebene und PG(2, q) (Zellen 30 von projectivegeometry.ipynb)."""
    global C, N, N7, P5, Pq, ax, axes, codewoerter, dmin, fano, fig, im
    global lage, linear, mitte, ok, p, pg2, pkt, q, reihenfolge, spalte, xy
    def pg2(q):
        """Punkte von PG(2, q) für eine Primzahl q: Vektoren in F_q³, deren erste Koordinate ≠ 0 gleich 1 ist."""
        pts = [v for v in itertools.product(range(q), repeat=3) if any(v) and v[next(i for i in range(3) if v[i])] == 1]
        return np.array(pts)


    for q in [2, 3, 5, 7]:
        Pq = pg2(q)                                                  # Geraden: dieselben Vektoren (Dualität)
        N = (Pq @ Pq.T % q == 0).astype(int)                         # Inzidenz: Punkt x liegt auf Gerade l, wenn l·x ≡ 0
        ok = np.array_equal(N @ N.T, q * np.eye(len(Pq), dtype=int) + 1)
        print(f"q = {q}: {len(Pq):3d} Punkte (q²+q+1 = {q * q + q + 1}), Punkte pro Gerade {sorted({int(v) for v in N.sum(axis=0)})}, "
              f"N Nᵀ = qI + J: {ok}")

    fano = pg2(2)
    N7 = (fano @ fano.T % 2 == 0).astype(int)
    codewoerter = {tuple(c) for c in N7.T} | {tuple(1 - c) for c in N7.T} | {(0,) * 7, (1,) * 7}
    C = np.array(sorted(codewoerter))
    linear = all(tuple((a + b_) % 2) in codewoerter for a in C for b_ in C)
    dmin = min(np.sum(a != b_) for a, b_ in itertools.combinations(C, 2))
    print(f"\nFano-Code: {len(C)} Codewörter, linear: {linear}, Mindestabstand {dmin} -> der [7, 4, 3]-Hamming-Code")

    lage = {(1, 0, 0): (0, 0), (0, 1, 0): (2, 0), (0, 0, 1): (1, np.sqrt(3)), (1, 1, 0): (1, 0),
            (0, 1, 1): (1.5, np.sqrt(3) / 2), (1, 0, 1): (0.5, np.sqrt(3) / 2), (1, 1, 1): (1, np.sqrt(3) / 3)}
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.2))
    ax = axes[0]
    mitte = np.array(lage[(1, 1, 1)])
    for spalte in N7.T:
        pkt = [tuple(fano[i]) for i in np.nonzero(spalte)[0]]
        xy = np.array([lage[p] for p in pkt])
        if all(sum(p) == 2 for p in pkt):                            # die Gerade aus den drei Seitenmitten: der Inkreis
            ax.add_patch(plt.Circle(mitte, np.linalg.norm(xy[0] - mitte), fill=False, color="tab:red", lw=1.5))
        else:
            reihenfolge = np.argsort(xy[:, 0] + 1e-3 * xy[:, 1])
            ax.plot(*xy[reihenfolge].T, color="tab:blue", lw=1.5)
    for p, xy in lage.items():
        ax.plot(*xy, "ko", ms=10)
        ax.annotate("".join(map(str, p)), xy, xytext=(8, -14), textcoords="offset points", fontsize=10)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("Fano-Ebene PG(2, 2): 7 Punkte, 7 Geraden (eine davon als Kreis)")
    P5 = pg2(5)
    im = axes[1].imshow((P5 @ P5.T % 5 == 0).astype(int), cmap="Greys")
    axes[1].set_xlabel("Gerade (Index)"); axes[1].set_ylabel("Punkt (Index)")
    axes[1].set_title("Inzidenzmatrix von PG(2, 5): 31 × 31, je 6 Einsen pro Zeile und Spalte")
    plt.tight_layout()
    plt.show()


def projective_line():
    """32. Die projektive Gerade über $\\mathbb F_p$ und gegenseitig unverzerrte Basen (Zellen 33 von projectivegeometry.ipynb)."""
    global O, U2, V, Xop, Zop, _, a, alle, ax, b_, basen, block
    global fig, g, geraden, im, omega, p, pt, punkte_pg1, ticks
    p = 5
    omega = np.exp(2j * np.pi / p)
    Xop = np.roll(np.eye(p), 1, axis=0)                              # X|j> = |j+1>
    Zop = np.diag(omega ** np.arange(p))                             # Z|j> = ω^j |j>
    punkte_pg1 = [(0, 1)] + [(1, k) for k in range(p)]
    geraden = {pt: sorted({((t * pt[0]) % p, (t * pt[1]) % p) for t in range(p)}) for pt in punkte_pg1}
    print("Punkte von PG(1, 5) = Geraden durch 0 in F_5²:")
    for pt, g in geraden.items():
        print(f"  ({pt[0]} : {pt[1]}): {g}")
    alle = {v for g in geraden.values() for v in g}
    print(f"jeder der {p * p - 1} Vektoren ≠ 0 liegt auf genau einer Geraden: {len(alle) == p * p and sum(len(g) - 1 for g in geraden.values()) == p * p - 1}")

    basen = []
    for a, b_ in punkte_pg1:
        O = np.linalg.matrix_power(Xop, a) @ np.linalg.matrix_power(Zop, b_)
        _, V = np.linalg.eig(O)
        basen.append(V / np.linalg.norm(V, axis=0))
    V = np.hstack(basen)
    U2 = np.abs(V.conj().T @ V) ** 2
    block = np.kron(np.eye(p + 1), np.ones((p, p))).astype(bool)
    print(f"innerhalb einer Basis: größte Abweichung von δ {np.abs(U2[block] - np.eye(p * (p + 1))[block]).max():.1e}; "
          f"zwischen Basen: größte Abweichung von 1/p {np.abs(U2[~block] - 1 / p).max():.1e}")

    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(U2, cmap="viridis")
    plt.colorbar(im, ax=ax, label="|⟨u|v⟩|²")
    ticks = np.arange(p // 2, p * (p + 1), p)
    ax.set_xticks(ticks, [f"({a}:{b_})" for a, b_ in punkte_pg1]); ax.set_yticks(ticks, [f"({a}:{b_})" for a, b_ in punkte_pg1])
    ax.set_xlabel("Basis zum Punkt von PG(1, 5)"); ax.set_ylabel("Basis zum Punkt von PG(1, 5)")
    ax.set_title("Überlappe der 6 Eigenbasen von X^a Z^b (je 5 Vektoren)")
    plt.show()


def bloch_riemann():
    """33. $\\mathbb CP^1$ als Bloch- und Riemann-Kugel (Zellen 36 von projectivegeometry.ipynb)."""
    global G, Pauli, Rmat, Ry, U, _, a, abw, ax, ax2, b_, c
    global d, ebene, ex, ey, fig, name, ph, phi, phis, psi, r, t
    global th, v, z, z_neu, zr, zs, zustaende
    psi = np.array([0.6, 0.8 * np.exp(0.7j)])
    print("globale Phase ändert z nicht:", np.isclose(riemann_z(psi), riemann_z(np.exp(1.3j) * psi)),
          "| Bloch-Vektor über z und direkt gleich:", np.allclose(kugel_aus_z(riemann_z(psi)), bloch(psi)))

    abw = []
    for _ in range(200):
        G = rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2))
        U, _ = np.linalg.qr(G)
        phi = rng.normal(size=2) + 1j * rng.normal(size=2)
        (a, b_), (c, d) = U
        z = riemann_z(phi)
        z_neu = (c + d * z) / (a + b_ * z)                           # Möbius-Abbildung
        Pauli = [np.array([[0, 1], [1, 0]]), np.array([[0, -1j], [1j, 0]]), np.diag([1, -1])]
        Rmat = np.array([[0.5 * np.trace(si @ U @ sj @ U.conj().T).real for sj in Pauli] for si in Pauli])
        abw.append(np.linalg.norm(kugel_aus_z(z_neu) - Rmat @ bloch(phi)))
        abw.append(abs(np.linalg.det(Rmat) - 1) + np.linalg.norm(Rmat.T @ Rmat - np.eye(3)))
    print(f"200 zufällige Unitäre: Möbius-Abbildung von z = Drehung R ∈ SO(3) des Bloch-Vektors, größte Abweichung {max(abw):.1e}")

    fig = plt.figure(figsize=(15, 6))
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    kugel_gitter(ax)
    ebene = np.linspace(-2.2, 2.2, 2)
    ex, ey = np.meshgrid(ebene, ebene)
    ax.plot_surface(ex, ey, 0 * ex, alpha=0.08, color="tab:blue")
    zustaende = {"|0⟩": np.array([1, 0]), "|+⟩": np.array([1, 1]), "|+i⟩": np.array([1, 1j]),
                 "ψ": psi, "(|0⟩ + 2|1⟩)/√5": np.array([1, 2])}
    for name, v in zustaende.items():
        r = bloch(v); z = riemann_z(v)
        ax.plot(*np.array([[0, 0, -1], [z.real, z.imag, 0]]).T, color="0.4", lw=0.8)   # Gerade vom Südpol
        ax.scatter(*r, s=40); ax.scatter(z.real, z.imag, 0, s=20, marker="x", color="k")
        ax.text(*(r * 1.12), name, fontsize=8)
    ax.scatter(0, 0, -1, color="k", s=40); ax.text(0, 0, -1.25, "Südpol |1⟩ ↦ z = ∞", fontsize=8)
    ax.set_xlim(-2.2, 2.2); ax.set_ylim(-2.2, 2.2); ax.set_zlim(-2.2, 2.2); ax.set_box_aspect((1, 1, 1))
    ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z")
    ax.set_title("Stereographische Projektion vom Südpol: Bloch-Vektor ↔ z = β/α", fontsize=10)

    ax2 = fig.add_subplot(1, 2, 2)
    Ry = np.array([[np.cos(0.5), -np.sin(0.5)], [np.sin(0.5), np.cos(0.5)]])   # Drehung um die y-Achse um 1 rad
    (a, b_), (c, d) = Ry
    for th in np.radians([30, 60, 90, 120, 150]):                    # Breitenkreise: Kreise |z| = tan(θ/2)
        phis = np.linspace(0, 2 * np.pi, 300)
        zs = np.tan(th / 2) * np.exp(1j * phis)
        ax2.plot(zs.real, zs.imag, color="tab:blue", lw=0.8)
        zr = (c + d * zs) / (a + b_ * zs)
        ax2.plot(zr.real, zr.imag, color="tab:red", lw=0.8)
    for ph in np.radians(np.arange(0, 180, 30)):                     # Längenkreise: Geraden durch 0
        t = np.linspace(-6, 6, 2)
        ax2.plot(t * np.cos(ph), t * np.sin(ph), color="tab:blue", lw=0.5, alpha=0.6)
    ax2.plot([], [], color="tab:blue", label="Breiten- und Längenkreise")
    ax2.plot([], [], color="tab:red", label="Breitenkreise nach Drehung um 1 rad (Möbius)")
    ax2.set_xlim(-4, 4); ax2.set_ylim(-4, 4); ax2.set_aspect("equal")
    ax2.set_xlabel("Re z"); ax2.set_ylabel("Im z"); ax2.set_title("Die z-Ebene: Kreise bleiben Kreise"); ax2.legend(fontsize=8)
    plt.tight_layout()
    plt.show()


def fubini_study():
    """34. Fubini–Study-Metrik und Haar-Zustände (Zellen 39 von projectivegeometry.ipynb)."""
    global G, N, V, _, a, axes, c, d_fs, delta, farbe, fig, halbwinkel
    global psi, psi_d, ueb, var, w, xs
    d_fs, halbwinkel = [], []
    for _ in range(500):
        a, c = haar_zustand(2), haar_zustand(2)
        d_fs.append(fs_abstand(a, c))
        halbwinkel.append(0.5 * np.arccos(np.clip(bloch(a) @ bloch(c), -1, 1)))
    print(f"Qubits: größte Abweichung d_FS − (Winkel/2) = {np.max(np.abs(np.array(d_fs) - halbwinkel)):.1e}")

    N, delta = 6, 1e-4
    psi = haar_zustand(N)
    G = rng.normal(size=(N, N)) + 1j * rng.normal(size=(N, N)); G = (G + G.conj().T) / 2
    w, V = np.linalg.eigh(G)
    psi_d = V @ (np.exp(-1j * delta * w) * (V.conj().T @ psi))      # e^(−iδG) ψ
    var = np.real(np.vdot(psi, G @ G @ psi) - np.vdot(psi, G @ psi) ** 2)
    print(f"N = {N}: 4 Var(G) = {4 * var:.6f}, 4 (d_FS/δ)² = {4 * (fs_abstand(psi, psi_d) / delta) ** 2:.6f}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    axes[0].plot(halbwinkel, d_fs, ".", ms=3, label="500 zufällige Paare")
    axes[0].plot([0, np.pi / 2], [0, np.pi / 2], "k--", lw=1, label="d_FS = γ/2")
    axes[0].set_xlabel("halber Winkel γ/2 zwischen den Bloch-Vektoren [rad]"); axes[0].set_ylabel("d_FS [rad]")
    axes[0].set_title("Qubits: Fubini–Study = halber Bloch-Winkel"); axes[0].legend()
    xs = np.linspace(0, 1, 300)
    for N, farbe in zip([2, 3, 6, 11], ["tab:blue", "tab:orange", "tab:green", "tab:red"]):
        ueb = np.array([abs(haar_zustand(N)[0]) ** 2 for _ in range(20000)])
        axes[1].hist(ueb, bins=50, range=(0, 1), density=True, histtype="step", color=farbe)
        axes[1].plot(xs, (N - 1) * (1 - xs) ** (N - 2), color=farbe, lw=1.5, label=f"N = {N}: (N−1)(1−x)^(N−2)")
    axes[1].set_xlabel("x = |⟨0|ψ⟩|²"); axes[1].set_ylabel("Dichte")
    axes[1].set_title("Haar-zufällige Zustände in ℂP^(N−1) (Histogramme: 20 000 Zustände)"); axes[1].legend()
    axes[1].set_ylim(0, 5)
    plt.tight_layout()
    plt.show()


def hopf():
    """35. Geometrische Phase und Hopf-Faserung (Zellen 42 von projectivegeometry.ipynb)."""
    global B, _, a_, ax, ax_b, ax_h, breiten, chi, cmap, farbe, farben, faser
    global fig, halber, k, lim, ph, phase, r, r1, r2, raumwinkel, th, v
    global verschlingung, x4, xyz
    def raumwinkel(r1, r2, r3):
        """Orientierter Raumwinkel des geodätischen Dreiecks (Formel von Van Oosterom und Strackee)."""
        return 2 * np.arctan2(r1 @ np.cross(r2, r3), 1 + r1 @ r2 + r2 @ r3 + r3 @ r1)


    phase, halber = [], []
    for _ in range(1000):
        r = rng.normal(size=(3, 3)); r /= np.linalg.norm(r, axis=1, keepdims=True)
        k = [ket(x) * np.exp(1j * rng.uniform(0, 2 * np.pi)) for x in r]    # beliebige Phasen
        B = np.vdot(k[0], k[1]) * np.vdot(k[1], k[2]) * np.vdot(k[2], k[0])
        phase.append(np.angle(B)); halber.append(raumwinkel(*r) / 2)
    phase, halber = np.array(phase), np.array(halber)
    print(f"arg(Bargmann) − Ω/2: größte Abweichung {np.max(np.abs(np.angle(np.exp(1j * (phase - halber))))):.1e} "
          "(geometrische Phase des Umlaufs 1→2→3→1: γ = −Ω/2)")

    fig = plt.figure(figsize=(16, 5.6))
    ax = fig.add_subplot(1, 3, 1)
    ax.plot(halber, phase, ".", ms=3)
    ax.plot([-np.pi, np.pi], [-np.pi, np.pi], "k--", lw=1)
    ax.set_xlabel("Ω/2: halber orientierter Raumwinkel [rad]"); ax.set_ylabel("arg⟨1|2⟩⟨2|3⟩⟨3|1⟩ [rad]")
    ax.set_title("Bargmann-Invariante zufälliger Dreiecke\n(Phasen der Vektoren zufällig)")

    breiten = {np.radians(45): "Blues", np.radians(90): "Reds"}
    ax_b = fig.add_subplot(1, 3, 2, projection="3d")
    ax_h = fig.add_subplot(1, 3, 3, projection="3d")
    kugel_gitter(ax_b)
    chi = np.linspace(0, 2 * np.pi, 200)
    for th, cmap in breiten.items():
        farben = plt.get_cmap(cmap)(np.linspace(0.45, 0.95, 12))
        for ph, farbe in zip(np.linspace(0, 2 * np.pi, 12, endpoint=False), farben):
            v = ket(np.array([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)]))
            ax_b.scatter(*bloch(v), color=farbe, s=25)
            faser = np.exp(1j * chi)[:, None] * v[None, :]           # alle Vektoren e^(iχ) ψ: ein Kreis in S³
            x4 = np.column_stack([faser[:, 0].real, faser[:, 0].imag, faser[:, 1].real, faser[:, 1].imag])
            xyz = x4[:, :3] / (1 - x4[:, 3:4])                        # stereographische Projektion S³ -> ℝ³
            ax_h.plot(*xyz.T, color=farbe, lw=0.9)
    # Fasern über den Polen: über |0⟩ der Einheitskreis in der x-y-Ebene, über |1⟩ die z-Achse (durch den Projektionspunkt)
    ax_b.scatter([0, 0], [0, 0], [1, -1], color="k", s=40)
    ax_h.plot(np.cos(chi), np.sin(chi), 0 * chi, color="k", lw=2, label="Faser über |0⟩ (Nordpol)")
    ax_h.plot([0, 0], [0, 0], [-3, 3], color="k", lw=2, ls="--", label="Faser über |1⟩ (Südpol)")
    ax_h.legend(fontsize=8, loc="upper left")
    ax_b.set_title("Basispunkte auf zwei Breitenkreisen und die Pole", fontsize=10)
    ax_h.set_title("Ihre Fasern (globale Phasen) in S³, stereographisch in den ℝ³\nprojiziert: jeder Breitenkreis gibt einen Torus", fontsize=10)
    for a_ in (ax_b, ax_h):
        a_.set_xlabel("x"); a_.set_ylabel("y"); a_.set_zlabel("z")
    lim = 3.0
    ax_h.set_xlim(-lim, lim); ax_h.set_ylim(-lim, lim); ax_h.set_zlim(-lim, lim); ax_h.set_box_aspect((1, 1, 1))
    ax_h.view_init(elev=28, azim=40)
    plt.tight_layout()
    plt.show()

    # Verschlingung: zwei Fasern haben die Verschlingungszahl ±1 (Gauß-Integral, numerisch)
    def faser(r, n=400):
        v = ket(r)
        f_ = np.exp(1j * np.linspace(0, 2 * np.pi, n, endpoint=False))[:, None] * v[None, :]
        x4 = np.column_stack([f_[:, 0].real, f_[:, 0].imag, f_[:, 1].real, f_[:, 1].imag])
        return x4[:, :3] / (1 - x4[:, 3:4])


    def verschlingung(c1, c2):
        d1, d2 = np.roll(c1, -1, axis=0) - c1, np.roll(c2, -1, axis=0) - c2
        m1, m2 = c1 + d1 / 2, c2 + d2 / 2
        diff = m1[:, None, :] - m2[None, :, :]
        return np.sum(np.einsum("ijk,ijk->ij", diff, np.cross(d1[:, None, :], d2[None, :, :]))
                      / np.linalg.norm(diff, axis=2) ** 3) / (4 * np.pi)


    r1, r2 = np.array([1.0, 0, 0]), np.array([0, 0.6, 0.8])
    print(f"Gauß-Verschlingungszahl zweier Fasern: {verschlingung(faser(r1), faser(r2)):+.3f}")


def segre_veronese():
    """36. Segre und Veronese: Verschränkung und Majorana-Sterne (Zellen 45 von projectivegeometry.ipynb)."""
    global Cs, _, a, a_, abstand, ax, ax3, b2, beispiele, c, conc, fig
    global i, majorana_sterne, name, s, u
    conc, abstand = [], []
    for _ in range(2000):
        c = haar_zustand(4).reshape(2, 2)
        conc.append(2 * abs(np.linalg.det(c)))
        abstand.append(np.arccos(np.clip(np.linalg.svd(c, compute_uv=False)[0], 0, 1)))   # Überlapp mit dem nächsten Produkt
    a_, b2 = haar_zustand(2), haar_zustand(2)
    print(f"Produktzustand: c00 c11 − c01 c10 = {abs(np.linalg.det(np.outer(a_, b2))):.1e}")
    Cs = np.linspace(0, 1, 200)
    print(f"größte Abweichung von arccos √((1 + √(1−C²))/2): "
          f"{np.max(np.abs(np.array(abstand) - np.arccos(np.sqrt((1 + np.sqrt(1 - np.array(conc) ** 2)) / 2)))):.1e}")


    def majorana_sterne(a):
        """Majorana-Sterne eines symmetrischen Zustands mit Koeffizienten a_k vor |D_k> (k Einsen)."""
        n = len(a) - 1
        koef = np.array([a[k] * np.sqrt(math.comb(n, k)) for k in range(n + 1)], dtype=complex)
        koef[np.abs(koef) < 1e-12] = 0
        hoch = koef[::-1]                                            # Polynom in r = y/x, höchster Grad zuerst
        fuehrend = int(np.argmax(np.abs(hoch) > 0))                  # fehlende Grade: Nullstellen bei r = ∞, also z = 0
        wurzeln = np.roots(hoch[fuehrend:])
        zs = [0j] * fuehrend + [np.inf if abs(r) < 1e-12 else -1 / r for r in wurzeln]
        return np.array([kugel_aus_z(z) for z in zs])


    u = ket(np.array([np.sin(1.0) * np.cos(0.5), np.sin(1.0) * np.sin(0.5), np.cos(1.0)]))
    beispiele = {
        "kohärent, n = 4": np.array([np.sqrt(math.comb(4, k)) * u[0] ** (4 - k) * u[1] ** k for k in range(5)]),
        "GHZ, n = 5": np.array([1, 0, 0, 0, 0, 1]) / np.sqrt(2),
        "Dicke |D_2⟩, n = 4": np.array([0, 0, 1, 0, 0.0]),
        "zufällig symmetrisch, n = 6": haar_zustand(7),
    }
    fig = plt.figure(figsize=(18, 5))
    ax = fig.add_subplot(1, 5, 1)
    ax.plot(conc, abstand, ".", ms=2, label="2000 Haar-zufällige Zustände")
    ax.plot(Cs, np.arccos(np.sqrt((1 + np.sqrt(1 - Cs ** 2)) / 2)), "k-", lw=1, label="arccos √((1+√(1−C²))/2)")
    ax.set_xlabel("Concurrence C"); ax.set_ylabel("d_FS zur Segre-Quadrik [rad]")
    ax.set_title("Abstand zu den Produktzuständen", fontsize=10); ax.legend(fontsize=7)
    for i, (name, a) in enumerate(beispiele.items()):
        s = majorana_sterne(a)
        ax3 = fig.add_subplot(1, 5, i + 2, projection="3d")
        kugel_gitter(ax3, alpha=0.1)
        ax3.scatter(*s.T, s=60, color="tab:red", depthshade=False)
        ax3.set_title(name, fontsize=10)
        ax3.set_xticks([]); ax3.set_yticks([]); ax3.set_zticks([])
        print(f"{name:28s}: Sterne (x, y, z) = {np.round(s, 2).tolist()}")
    print("Bloch-Vektor des kohärenten Zustands:", np.round(bloch(u), 2).tolist())
    plt.tight_layout()
    plt.show()
