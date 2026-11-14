"""Funktionentheorie: komplexe Zahlen, Phasenbilder, Holomorphie, Cauchy, Konvergenzradius, Singularitäten, Riemann-Flächen, Residuen, Argumentprinzip, Laplace-Transformation, Kramers-Kronig, Resolvente, Zerfall, analytische Fortsetzung und Lee-Yang.

Für analysis.ipynb aus complexanalysis.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: complex_numbers, phase_portraits, holomorphy, cauchy, convergence_radius, singularities, branch_points, residues, argument_principle, laplace, kramers_kronig, resolvent, decay_pole, continuation, lee_yang_zeros.
"""
import mpmath
import sys
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
from scipy.integrate import quad, solve_ivp, trapezoid
from scipy.special import erfc, gamma as gamma_fn
from scipy.linalg import expm


def complex_numbers():
    """1. Komplexe Zahlen: Drehstreckung, Einheitswurzeln, Interferenz (Zellen 4, 6 von complexanalysis.ipynb)."""
    global M, a, ax, axes, b_, fig, h, haus, k, kreisintegral, laurent, loes
    global phasenbild, phi, rng, t, talbot, umlaufzahl, w, wurzeln, z0
    rng = np.random.default_rng(2026)
    def phasenbild(ax, f, xlim, ylim, n=500, ringe=True):
        """Domain Coloring: Farbton = arg f (rot = positiv reell, dann gelb, grün, cyan, blau, magenta gegen den
    Uhrzeigersinn), Helligkeit mit Ringen bei |f| = e^k (Höhenlinien von log|f|)."""
        x = np.linspace(*xlim, n)
        y = np.linspace(*ylim, n)
        Z = x[None, :] + 1j * y[:, None]
        with np.errstate(all="ignore"):
            W = f(Z)
        farbton = (np.angle(W) / (2 * np.pi)) % 1
        if ringe:
            L = np.log(np.abs(W))
            hell = 0.7 + 0.3 * (L - np.floor(L))
        else:
            hell = np.ones_like(farbton)
        rgb = hsv_to_rgb(np.dstack([farbton, 0.85 * np.ones_like(farbton), hell]))
        rgb[~np.isfinite(W)] = 1.0
        ax.imshow(rgb, extent=[*xlim, *ylim], origin="lower", interpolation="bilinear")
        ax.set_xlabel("Re z"); ax.set_ylabel("Im z")
    def kreisintegral(f, a=0.0, r=1.0, N=256):
        """∮ f(z) dz über den Kreis |z − a| = r mit der Trapezregel (N Punkte)."""
        th = 2 * np.pi * np.arange(N) / N
        z = a + r * np.exp(1j * th)
        return np.sum(f(z) * 1j * (z - a)) * 2 * np.pi / N
    def laurent(f, a=0.0, r=1.0, N=256):
        """Laurent-Koeffizienten c_n (n = −N/2 .. N/2−1) aus Werten auf dem Kreis |z − a| = r: eine FFT."""
        th = 2 * np.pi * np.arange(N) / N
        werte = f(a + r * np.exp(1j * th))
        c = np.fft.fft(werte) / N                                   # c_n r^n
        n = np.fft.fftfreq(N, 1 / N).astype(int)
        return dict(zip(n, c / r ** n.astype(float)))
    def umlaufzahl(w):
        """Umlaufzahl einer geschlossenen Kurve w(θ) (Punkte, Anfang = Ende ausgenommen) um 0."""
        dphi = np.angle(np.roll(w, -1) / w)
        return np.sum(dphi) / (2 * np.pi)
    def talbot(F, t, M=24):
        """Inverse Laplace-Transformation f(t) über die feste Talbot-Kontur (Abate und Valkó 2004)."""
        r = 2 * M / (5 * t)
        th = np.arange(1, M) * np.pi / M
        s = r * th * (1 / np.tan(th) + 1j)
        sigma = th + (th / np.tan(th) - 1) / np.tan(th)
        return (r / M) * (0.5 * F(r) * np.exp(r * t) + np.sum((np.exp(t * s) * F(s) * (1 + 1j * sigma)).real))

    w = 1.15 * np.exp(1j * np.pi / 6)
    haus = np.array([0, 0.3, 0.3 + 0.2j, 0.15 + 0.35j, 0.2j, 0]) + 0.5
    M = np.array([[w.real, -w.imag], [w.imag, w.real]])               # dieselbe Zahl als reelle Matrix
    z0 = 0.7 - 0.4j
    print("Multiplikation als Matrix:", np.allclose(M @ [z0.real, z0.imag], [(w * z0).real, (w * z0).imag]),
          f"| e^(iπ) + 1 = {np.exp(1j * np.pi) + 1:.1e}")
    wurzeln = np.exp(2j * np.pi * np.arange(7) / 7)
    print("Summe der 7. Einheitswurzeln:", f"{abs(wurzeln.sum()):.1e}", "| Produkt:", np.round(np.prod(wurzeln), 12))

    fig, axes = plt.subplots(1, 3, figsize=(17, 5.2))
    ax = axes[0]
    for k in range(13):
        h = haus * w ** k
        ax.fill(h.real, h.imag, color=plt.get_cmap("viridis")(k / 12), alpha=0.8)
    ax.plot(0, 0, "k+")
    ax.set_aspect("equal"); ax.set_xlabel("Re"); ax.set_ylabel("Im")
    ax.set_title("Multiplikation mit w = 1.15·e^(iπ/6), 12-mal:\neine volle Drehung, gestreckt um 1.15¹²")
    ax = axes[1]
    t = np.linspace(0, 2 * np.pi, 300)
    ax.plot(np.cos(t), np.sin(t), color="0.7")
    ax.plot(wurzeln.real, wurzeln.imag, "o", ms=9, label="z⁷ = 1")
    loes = (1 + 1j) ** (1 / 5) * np.exp(2j * np.pi * np.arange(5) / 5)
    ax.plot(loes.real, loes.imag, "s", ms=8, label="z⁵ = 1 + i")
    ax.set_aspect("equal"); ax.legend(loc="lower left"); ax.set_xlabel("Re"); ax.set_ylabel("Im")
    ax.set_title("Einheitswurzeln und Wurzeln von 1 + i")
    ax = axes[2]
    phi = np.linspace(0, 4 * np.pi, 400)
    a, b_ = 1 / np.sqrt(2), np.exp(1j * phi) / np.sqrt(2)
    ax.plot(phi / np.pi, np.abs(a + b_) ** 2, label="|a + b|² (Amplituden addieren)")
    ax.plot(phi / np.pi, np.abs(a) ** 2 + np.abs(b_) ** 2, "--", label="|a|² + |b|² (Wahrscheinlichkeiten addieren)")
    ax.set_xlabel("Phasendifferenz φ [π]"); ax.set_ylabel("Wahrscheinlichkeit")
    ax.set_title("Zwei Wege mit |a|² = |b|² = ½: Interferenz"); ax.legend()
    plt.tight_layout()
    plt.show()


def phase_portraits():
    """2. Phasenbilder: Nullstellen und Pole sehen (Zellen 9 von complexanalysis.ipynb)."""
    global ax, axes, beispiele, f, fig, name, p, pole, w_
    beispiele = {
        "f(z) = z": lambda z: z,
        "f(z) = z³": lambda z: z ** 3,
        "f(z) = 1/z": lambda z: 1 / z,
        "f(z) = (z² − 1)(z − 2 − i)² / (z² + 2 + 2i)": lambda z: (z ** 2 - 1) * (z - 2 - 1j) ** 2 / (z ** 2 + 2 + 2j),
        "f(z) = e^z": np.exp,
        "f(z) = sin z": np.sin,
    }
    fig, axes = plt.subplots(2, 3, figsize=(15, 9.5))
    for ax, (name, f) in zip(axes.flat, beispiele.items()):
        phasenbild(ax, f, (-3, 3), (-3, 3))
        ax.set_title(name, fontsize=10)
    plt.tight_layout()
    plt.show()

    f = beispiele["f(z) = (z² − 1)(z − 2 − i)² / (z² + 2 + 2i)"]
    pole = np.roots([1, 0, 2 + 2j])
    for name, p in [("Nullstelle 1", 1), ("Nullstelle −1", -1), ("Nullstelle 2+i", 2 + 1j), ("Pol", pole[0]), ("Pol", pole[1])]:
        w_ = f(p + 0.05 * np.exp(2j * np.pi * np.arange(400) / 400))
        print(f"{name:14s} bei {complex(p):.3f}: Umlaufzahl des Bildes eines kleinen Kreises {umlaufzahl(w_):+.0f}")


def holomorphy():
    """3. Holomorphie: Cauchy–Riemann, Winkeltreue und Strömungen (Zellen 12 von complexanalysis.ipynb)."""
    global A0, Gamma, Phi, R, U, alpha, ax, axes, bild, bildwinkel, c, cr_rest
    global dPhi, f, farbe, fig, linie, mu, name, profil, punkte, rr, s, t
    global tt, zeta, zz
    def cr_rest(f, z, h=1e-6):
        """|u_x − v_y| + |u_y + v_x| mit zentralen Differenzen."""
        fx = (f(z + h) - f(z - h)) / (2 * h)
        fy = (f(z + 1j * h) - f(z - 1j * h)) / (2 * h)
        return abs(fx.real - fy.imag) + abs(fy.real + fx.imag)


    punkte = rng.normal(size=20) + 1j * rng.normal(size=20)
    for name, f in [("z²", lambda z: z ** 2), ("e^z", np.exp), ("sin z", np.sin), ("1/z", lambda z: 1 / z),
                    ("z̄", np.conj), ("|z|²", lambda z: abs(z) ** 2 + 0j), ("Re z", lambda z: z.real + 0j)]:
        print(f"{name:6s}: größter Cauchy-Riemann-Rest an 20 Zufallspunkten {max(cr_rest(f, z) for z in punkte):.1e}")

    # Winkel zwischen den Bildern der Gitterlinien unter z ↦ z²
    def bildwinkel(z, h=1e-6):
        d1 = (z + h) ** 2 - z ** 2
        d2 = (z + 1j * h) ** 2 - z ** 2
        return np.degrees(abs(np.angle(d2 / d1)))
    print("Winkel der Bildkurven unter z²:", np.round([bildwinkel(z) for z in punkte[:5]], 4), "Grad;",
          f"bei z = 0: {np.degrees(abs(np.angle((1j * 1e-6) ** 2 / (1e-6) ** 2))):.0f} Grad (z² verdoppelt Winkel, f'(0) = 0)")

    fig, axes = plt.subplots(1, 2, figsize=(15, 6.2))
    ax = axes[0]
    s = np.linspace(-1.5, 1.5, 13)
    t = np.linspace(-1.5, 1.5, 300)
    for c in s:
        for linie, farbe in [(c + 1j * t, "tab:blue"), (t + 1j * c, "tab:orange")]:
            bild = linie ** 2
            ax.plot(bild.real, bild.imag, color=farbe, lw=0.7)
    ax.set_aspect("equal"); ax.set_xlim(-3, 3); ax.set_ylim(-3, 3)
    ax.set_xlabel("Re w"); ax.set_ylabel("Im w")
    ax.set_title("Bild des Quadratgitters unter w = z²: rechte Winkel bleiben\n(Parabeln schneiden sich senkrecht)")

    # Strömung um ein Joukowski-Profil
    mu = -0.08 + 0.08j                                              # Mittelpunkt des Kreises in der ζ-Ebene
    R = abs(1 - mu)                                                 # Kreis durch ζ = 1, das Bild ist die Hinterkante
    U, alpha = 1.0, np.radians(8)                                   # Anströmung und Anstellwinkel


    def dPhi(zeta, Gamma):
        return U * (np.exp(-1j * alpha) - R ** 2 * np.exp(1j * alpha) / (zeta - mu) ** 2) + 1j * Gamma / (2 * np.pi * (zeta - mu))


    A0 = dPhi(1.0, 0.0)
    Gamma = (-A0 / (dPhi(1.0, 1.0) - A0)).real                     # Kutta-Bedingung: Staupunkt an der Hinterkante
    print(f"Zirkulation nach der Kutta-Bedingung Γ = {Gamma:.4f}, Auftrieb pro Länge ρUΓ = {Gamma:.4f}·ρU² (Kutta–Joukowski)")
    rr, tt = np.meshgrid(np.linspace(R, 6 * R, 300), np.linspace(0, 2 * np.pi, 400))
    zeta = mu + rr * np.exp(1j * tt)
    Phi = U * ((zeta - mu) * np.exp(-1j * alpha) + R ** 2 * np.exp(1j * alpha) / (zeta - mu)) + 1j * Gamma / (2 * np.pi) * np.log(zeta - mu)
    zz = zeta + 1 / zeta                                            # Joukowski-Abbildung
    ax = axes[1]
    ax.contour(zz.real, zz.imag, Phi.imag, levels=np.linspace(-3, 3, 41), colors="tab:blue", linewidths=0.7)
    profil = mu + R * np.exp(1j * np.linspace(0, 2 * np.pi, 400))
    profil = profil + 1 / profil
    ax.fill(profil.real, profil.imag, color="0.3")
    ax.set_aspect("equal"); ax.set_xlim(-3, 3.5); ax.set_ylim(-2, 2)
    ax.set_xlabel("x"); ax.set_ylabel("y")
    ax.set_title("Stromlinien um ein Joukowski-Profil (8° Anstellwinkel, Kutta-Bedingung)")
    plt.tight_layout()
    plt.show()


def cauchy():
    """4. Cauchy-Satz, Integralformel und die Trapezregel (Zellen 15 von complexanalysis.ipynb)."""
    global N_werte, a, ax, c, erwartet, exakt_glatt, f, fehler_analytisch, fehler_glatt, fig, kf, name
    global r
    c, r = 0.3 + 0.2j, 0.5
    for name, f, a, erwartet in [("e^z, Kreis um 0.3+0.2i", np.exp, c, 0), ("z², Kreis um 0.3+0.2i", lambda z: z ** 2, c, 0),
                                  ("1/z, 0 innen", lambda z: 1 / z, c, 2j * np.pi), ("1/z², 0 innen", lambda z: z ** -2.0, c, 0),
                                  ("z̄ (nicht holomorph)", np.conj, c, 2j * np.pi * r ** 2)]:
        print(f"∮ {name:24s} = {kreisintegral(f, a, r):.6f}   (erwartet {erwartet:.6f})")

    kf = laurent(np.exp, 0, 10.0, 128)                              # Kreis vom Radius 10: alle c_n·rⁿ sind gut aufgelöst
    print("Taylor-Koeffizienten von e^z aus der Cauchy-Formel (FFT, 128 Punkte), n!·c_n für n = 0..7:",
          np.round([math.factorial(n) * kf[n].real for n in range(8)], 12))
    print(f"größter relativer Fehler |n!·c_n − 1| für n ≤ 30: {max(abs(math.factorial(n) * kf[n] - 1) for n in range(31)):.1e}")

    N_werte = np.arange(4, 81, 2)
    fehler_analytisch = [abs(kreisintegral(lambda z: np.exp(z) / z, 0, 1, N) - 2j * np.pi) for N in N_werte]
    exakt_glatt = 8 / 3                                           # ∫ |sin θ|³ dθ über [0, 2π]
    fehler_glatt = [abs(np.sum(np.abs(np.sin(2 * np.pi * np.arange(N) / N)) ** 3) * 2 * np.pi / N - exakt_glatt) for N in N_werte]

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.semilogy(N_werte, np.maximum(fehler_analytisch, 1e-17), "o-", label="∮ e^z/z dz (analytisch)")
    ax.semilogy(N_werte, fehler_glatt, "s-", label="∫ |sin θ|³ dθ (zweimal stetig differenzierbar)")
    ax.semilogy(N_werte, 30.0 * N_werte ** -4.0, "k--", lw=1, label="∝ N⁻⁴")
    ax.set_xlabel("Anzahl N der Stützstellen"); ax.set_ylabel("Fehler der Trapezregel")
    ax.set_title("Trapezregel auf dem Kreis: exponentiell gegen algebraisch"); ax.legend()
    plt.show()


def convergence_radius():
    """5. Der Konvergenzradius: die Singularität, die man auf der reellen Achse nicht sieht (Zellen 18 von complexanalysis.ipynb)."""
    global N, R_wahr, ax, axes, f, fenster, fig, funktionen, k, linie, m, n
    global name, schaetz, t, teil, x
    fig, axes = plt.subplots(1, 3, figsize=(17, 4.8))
    x = np.linspace(-1.6, 1.6, 400)
    ax = axes[0]
    ax.plot(x, 1 / (1 + x ** 2), "k", lw=2.5, label="1/(1 + x²)")
    for N in [6, 12, 24]:
        teil = sum((-1) ** k * x ** (2 * k) for k in range(N // 2 + 1))
        ax.plot(x, teil, label=f"Taylor bis x^{N}")
    ax.axvspan(-1.6, -1, color="0.9"); ax.axvspan(1, 1.6, color="0.9")
    ax.set_ylim(-1, 2); ax.set_xlabel("x"); ax.set_ylabel("Wert")
    ax.set_title("Reelle Teilsummen divergieren für |x| > 1"); ax.legend(fontsize=8)
    phasenbild(axes[1], lambda z: 1 / (1 + z ** 2), (-2, 2), (-2, 2))
    t = np.linspace(0, 2 * np.pi, 300)
    axes[1].plot(np.cos(t), np.sin(t), "w--", lw=1.5)
    axes[1].set_title("Phasenbild: Pole bei ±i begrenzen den Kreis |z| < 1")

    funktionen = {"1/(1+z²)": (lambda z: 1 / (1 + z ** 2), 1.0), "1/(4+z²)": (lambda z: 1 / (4 + z ** 2), 2.0),
                  "log(1+z)": (lambda z: np.log(1 + z), 1.0), "tan z": (np.tan, np.pi / 2),
                  "1/(1−z+z²)": (lambda z: 1 / (1 - z + z ** 2), 1.0)}
    ax = axes[2]
    n = np.arange(5, 61)
    for name, (f, R_wahr) in funktionen.items():
        k = laurent(f, 0, 0.9 * R_wahr, 256)                         # Koeffizienten aus einem Kreis innerhalb des Radius
        schaetz = []
        for m in n:
            fenster = [abs(k[j]) for j in range(m - 3, m + 1) if abs(k[j]) > 1e-300]   # 4 Koeffizienten: Lücken (z. B. tan) überbrücken
            schaetz.append(max(fenster) ** (-1 / m) if fenster else np.nan)
        linie, = ax.plot(n, schaetz, label=f"{name}: Abstand zur Singularität {R_wahr:.3f}")
        ax.axhline(R_wahr, color=linie.get_color(), ls=":", lw=1)
        print(f"{name:11s}: Schätzung bei n = 60: {schaetz[-1]:.3f}, Abstand zur nächsten Singularität {R_wahr:.3f}")
    ax.set_xlabel("n"); ax.set_ylabel("|c_n|^(−1/n)"); ax.set_ylim(0, 2.5)
    ax.set_title("Konvergenzradius aus den Koeffizienten (Wurzelkriterium)"); ax.legend(fontsize=7)
    plt.tight_layout()
    plt.show()


def singularities():
    """6. Isolierte Singularitäten: hebbar, Pol, wesentlich (Zellen 21 von complexanalysis.ipynb)."""
    global art, ax, axes, betrag, f, farbe, fig, k, loes, name, radien, singulaer
    global th, ziel
    singulaer = {"hebbar: sin z / z": lambda z: np.sin(z) / z, "Pol der Ordnung 3: 1/z³": lambda z: z ** -3.0,
                 "wesentlich: e^(1/z)": lambda z: np.exp(1 / z)}
    fig, axes = plt.subplots(1, 4, figsize=(19, 4.8))
    for ax, (name, f) in zip(axes[:3], singulaer.items()):
        phasenbild(ax, f, (-0.6, 0.6), (-0.6, 0.6), n=700)
        ax.set_title(name, fontsize=10)
        k = laurent(f, 0, 0.3, 128)
        print(f"{name:25s}: |c_n| für n = −6..2: {[round(float(abs(k[j])), 4) for j in range(-6, 3)]}")
    print("zum Vergleich 1/n! für n = 6..0:", [round(1 / math.factorial(j), 4) for j in range(6, -1, -1)])

    ax = axes[3]
    radien = np.logspace(-2, 0, 40)
    th = np.linspace(0, 2 * np.pi, 2000, endpoint=False)
    for (name, f), farbe in zip(singulaer.items(), ["tab:green", "tab:blue", "tab:red"]):
        betrag = np.array([np.abs(f(r_ * np.exp(1j * th))) for r_ in radien])
        art = name.split(":")[0]
        ax.loglog(radien, betrag.max(axis=1), color=farbe, label=f"max |f|, {art}")
        ax.loglog(radien, np.maximum(betrag.min(axis=1), 1e-300), color=farbe, ls="--", label=f"min |f|, {art}")
    ax.set_ylim(1e-12, 1e12); ax.set_xlabel("Radius r des Kreises"); ax.set_ylabel("|f| auf dem Kreis")
    ax.set_title("Wachstum nahe 0"); ax.legend(fontsize=7, ncol=2)
    plt.tight_layout()
    plt.show()

    ziel = 2 - 3j
    loes = 1 / (np.log(ziel) + 2j * np.pi * np.arange(1, 6))
    print(f"Lösungen von e^(1/z) = {ziel}: |z_k| = {np.round(np.abs(loes), 4)}, Probe |e^(1/z_k) − w| = "
          f"{np.max(np.abs(np.exp(1 / loes) - ziel)):.1e}")


def branch_points():
    """7. Verzweigungspunkte und Riemann-Flächen (Zellen 24 von complexanalysis.ipynb)."""
    global W, Z, ax, fig, fortsetzen, idx, k, r_, t_, umlauf, w_log, w_sqrt
    def fortsetzen(wurzel_von, z_weg, start):
        """Stetige Fortsetzung: in jedem Schritt den Zweig wählen, der dem vorigen Wert am nächsten liegt."""
        werte = [start]
        for z in z_weg[1:]:
            kandidaten = wurzel_von(z)
            werte.append(kandidaten[np.argmin(np.abs(kandidaten - werte[-1]))])
        return np.array(werte)


    umlauf = 2 * np.exp(1j * np.linspace(0, 4 * np.pi, 2001))      # zwei Umläufe um 0
    w_sqrt = fortsetzen(lambda z: np.array([np.sqrt(z), -np.sqrt(z)]), umlauf, np.sqrt(2 + 0j))
    w_log = fortsetzen(lambda z: np.log(z) + 2j * np.pi * np.arange(-3, 4), umlauf, np.log(2 + 0j))
    for k, idx in [(1, 1000), (2, 2000)]:
        print(f"nach {k} Umlauf/Umläufen: √z = {w_sqrt[idx]:.4f} (Start {w_sqrt[0]:.4f}), log z = {w_log[idx]:.4f} (Start {w_log[0]:.4f})")

    fig = plt.figure(figsize=(18, 5.2))
    ax = fig.add_subplot(1, 3, 1)
    phasenbild(ax, np.sqrt, (-2, 2), (-2, 2))
    ax.plot([-2, 0], [0, 0], "k", lw=3, label="Verzweigungsschnitt des Hauptzweigs")
    ax.legend(loc="upper left", fontsize=8); ax.set_title("√z (Hauptzweig): Sprung der Farbe auf der negativen Achse")
    ax = fig.add_subplot(1, 3, 2, projection="3d")
    r_, t_ = np.meshgrid(np.linspace(0, 1.5, 30), np.linspace(0, 4 * np.pi, 160))
    Z = r_ * np.exp(1j * t_)
    W = np.sqrt(r_) * np.exp(1j * t_ / 2)                           # stetig über zwei Umläufe: beide Blätter
    ax.plot_surface(Z.real, Z.imag, W.real, facecolors=plt.get_cmap("twilight")((W.imag / 1.3 + 1) / 2), lw=0, alpha=0.9)
    ax.set_xlabel("Re z"); ax.set_ylabel("Im z"); ax.set_zlabel("Re √z")
    ax.set_title("Riemann-Fläche von √z: zwei Blätter\n(Farbe: Im √z)", fontsize=10)
    ax = fig.add_subplot(1, 3, 3, projection="3d")
    r_, t_ = np.meshgrid(np.linspace(0.05, 1.5, 20), np.linspace(-2 * np.pi, 2 * np.pi, 200))
    ax.plot_surface(r_ * np.cos(t_), r_ * np.sin(t_), t_, cmap="viridis", lw=0, alpha=0.9)
    ax.set_xlabel("Re z"); ax.set_ylabel("Im z"); ax.set_zlabel("Im log z")
    ax.set_title("Riemann-Fläche von log z: eine Wendelfläche\nmit unendlich vielen Blättern", fontsize=10)
    plt.tight_layout()
    plt.show()


def residues():
    """8. Der Residuensatz für reelle Integrale (Zellen 27 von complexanalysis.ipynb)."""
    global R_, a_, ax, axes, bogen, f, fig, formel, gerade, integrale, name, numerisch
    global radien, th, weg, z
    a_ = 0.3
    integrale = [
        ("∫ dx/(1+x²) über ℝ", quad(lambda x: 1 / (1 + x ** 2), -np.inf, np.inf)[0], np.pi, "Halbkreis, Pol i: 2πi·1/(2i)"),
        ("∫ dx/(1+x⁴) über ℝ", quad(lambda x: 1 / (1 + x ** 4), -np.inf, np.inf)[0], np.pi / np.sqrt(2), "Halbkreis, Pole e^(iπ/4), e^(3iπ/4)"),
        ("∫ cos(2x)/(1+x²) über ℝ", 2 * quad(lambda x: 1 / (1 + x ** 2), 0, np.inf, weight="cos", wvar=2)[0], np.pi * np.exp(-2),
         "Halbkreis mit e^(2iz), Jordan"),
        ("∫ sin x / x über [0, ∞)", quad(lambda x: np.sinc(x / np.pi), 0, 1)[0] + quad(lambda x: 1 / x, 1, np.inf, weight="sin", wvar=1)[0],
         np.pi / 2, "Halbkreis mit Einbuchtung um 0"),
        ("∫ x^(a−1)/(1+x) über [0, ∞), a = 0.3", quad(lambda x: x ** (a_ - 1) / (1 + x), 0, 1)[0] + quad(lambda x: x ** (a_ - 1) / (1 + x), 1, np.inf)[0],
         np.pi / np.sin(np.pi * a_), "Schlüsselloch um den Schnitt"),
        ("∫ dθ/(2 + cos θ) über [0, 2π]", quad(lambda t: 1 / (2 + np.cos(t)), 0, 2 * np.pi)[0], 2 * np.pi / np.sqrt(3), "Einheitskreis z = e^(iθ)"),
    ]
    for name, numerisch, formel, weg in integrale:
        print(f"{name:38s} numerisch {numerisch:.10f}, Residuen {formel:.10f}, Differenz {abs(numerisch - formel):.1e}  ({weg})")

    print(f"Residuum von e^(2iz)/(1+z²) bei i, numerisch über einen kleinen Kreis: {kreisintegral(lambda z: np.exp(2j * z) / (1 + z ** 2), 1j, 0.3) / (2j * np.pi):.8f}, "
          f"Formel e^(−2)/(2i) = {np.exp(-2) / 2j:.8f}")

    f = lambda z: np.exp(2j * z) / (1 + z ** 2)
    radien = np.linspace(1.5, 30, 60)
    gerade, bogen = [], []
    for R_ in radien:
        gerade.append(quad(lambda x: f(x).real, -R_, R_, limit=200)[0])
        th = np.linspace(0, np.pi, 4001)
        z = R_ * np.exp(1j * th)
        bogen.append(trapezoid(f(z) * 1j * z, th))
    gerade, bogen = np.array(gerade), np.array(bogen)
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    ax = axes[0]
    th = np.linspace(0, np.pi, 200)
    ax.plot(np.concatenate([[-3, 3], 3 * np.exp(1j * th).real]), np.concatenate([[0, 0], 3 * np.exp(1j * th).imag]), "k")
    ax.plot([0, 0], [1, -1], "rx", ms=10); ax.annotate("Pol i (innen)", (0, 1), xytext=(8, 4), textcoords="offset points")
    ax.annotate("Pol −i (außen)", (0, -1), xytext=(8, 4), textcoords="offset points")
    ax.set_aspect("equal"); ax.set_xlabel("Re z"); ax.set_ylabel("Im z"); ax.set_title("Halbkreiskontur vom Radius R")
    ax = axes[1]
    ax.plot(radien, gerade, label="Beitrag der reellen Strecke")
    ax.plot(radien, bogen.real, label="Re Beitrag des Halbkreises")
    ax.plot(radien, gerade + bogen.real, lw=4, alpha=0.5, label="Summe")
    ax.axhline(np.pi * np.exp(-2), color="k", ls="--", label="2πi · Res = π e^(−2)")
    ax.set_xlabel("Radius R"); ax.set_ylabel("Integralwert")
    ax.set_title("∮ e^(2iz)/(1+z²) dz: der Halbkreis verschwindet"); ax.legend()
    plt.tight_layout()
    plt.show()


def argument_principle():
    """9. Argumentprinzip, Rouché und das Nyquist-Kriterium (Zellen 30 von complexanalysis.ipynb)."""
    global K, L, R_, ax, axes, farbe, fig, omega, p, pole_geschlossen, th, w_
    global wurzeln
    p = np.poly1d([1, 0, -3, 0, 1, -0.5])
    wurzeln = p.roots
    th = 2 * np.pi * np.arange(4000) / 4000
    for R_ in [0.3, 0.6, 1.0, 1.5, 2.0]:
        print(f"|z| < {R_}: Umlaufzahl {umlaufzahl(p(R_ * np.exp(1j * th))):+.0f}, Nullstellen laut np.roots: {np.sum(np.abs(wurzeln) < R_)}")

    fig, axes = plt.subplots(1, 3, figsize=(18, 5.2))
    ax = axes[0]
    for R_, farbe in [(0.6, "tab:blue"), (1.5, "tab:orange")]:
        w_ = p(R_ * np.exp(1j * th))
        ax.plot(w_.real, w_.imag, color=farbe, label=f"Bild des Kreises |z| = {R_}: Umlaufzahl {umlaufzahl(w_):.0f}")
    ax.plot(0, 0, "k+", ms=12)
    ax.set_aspect("equal"); ax.set_xlim(-6, 6); ax.set_ylim(-6, 6)
    ax.set_xlabel("Re p"); ax.set_ylabel("Im p"); ax.set_title("Argumentprinzip: p(Kreis)"); ax.legend(fontsize=8)
    phasenbild(axes[1], p, (-2.2, 2.2), (-2.2, 2.2))
    for R_ in [0.6, 1.5]:
        axes[1].plot(R_ * np.cos(th), R_ * np.sin(th), "w--", lw=1)
    axes[1].set_title("Phasenbild von p mit den beiden Kreisen")

    ax = axes[2]
    omega = np.concatenate([-np.logspace(3, -3, 2000), np.logspace(-3, 3, 2000)])
    for K, farbe in [(4, "tab:green"), (8, "tab:orange"), (12, "tab:red")]:
        L = K / (1j * omega + 1) ** 3
        pole_geschlossen = np.roots([1, 3, 3, 1 + K])
        ax.plot(L.real, L.imag, color=farbe,
                label=f"K = {K}: Umlaufzahl um −1: {umlaufzahl(L + 1):+.2f}; max Re(Pol) = {pole_geschlossen.real.max():+.3f}")
    ax.plot(-1, 0, "kx", ms=12, mew=2)
    ax.set_xlim(-3, 13); ax.set_ylim(-8, 8); ax.set_aspect("equal")
    ax.set_xlabel("Re L(iω)"); ax.set_ylabel("Im L(iω)"); ax.set_title("Nyquist-Kurven von L(s) = K/(s+1)³"); ax.legend(fontsize=7)
    plt.tight_layout()
    plt.show()
    print("kritisch: L(iω) reell negativ bei 3·arctan ω = π, also ω = √3 und |L| = K/8: K_krit = 8")


def laplace():
    """10. Laplace-Transformation: Pole, Residuen und die Talbot-Kontur (Zellen 33 von complexanalysis.ipynb)."""
    global F, a_w, axes, f_talbot, faelle, farbe, fig, gam, name, ode, omega0, pole
    global t, tt, x_res, x_residuen
    omega0 = 1.0
    t = np.linspace(0, 20, 400)
    faelle = {"schwach gedämpft, γ = 0.2": 0.2, "kritisch, γ = 1": 1.0, "überdämpft, γ = 2": 2.0}


    def x_residuen(t, gam, r_kreis=0.05):
        """Summe der Residuen von X(s) e^(st), jedes numerisch als kleines Kreisintegral (funktioniert auch bei Doppelpolen)."""
        pole = np.unique(np.round(np.concatenate([[0.0], np.roots([1, 2 * gam, omega0 ** 2])]), 4))   # Doppelpol nur einmal
        X = lambda s: 1 / (s * (s ** 2 + 2 * gam * s + omega0 ** 2))
        return np.array([sum(kreisintegral(lambda s: X(s) * np.exp(s * tt), p_, r_kreis) / (2j * np.pi) for p_ in pole).real for tt in t]), pole


    fig, axes = plt.subplots(1, 3, figsize=(18, 4.8))
    for (name, gam), farbe in zip(faelle.items(), ["tab:blue", "tab:orange", "tab:green"]):
        x_res, pole = x_residuen(t, gam)
        ode = solve_ivp(lambda tt, y: [y[1], 1 - 2 * gam * y[1] - omega0 ** 2 * y[0]], (0, 20), [0, 0], t_eval=t, rtol=1e-10, atol=1e-12)
        axes[1].plot(t, x_res, color=farbe, label=name)
        axes[1].plot(t[::12], ode.y[0][::12], "o", ms=3, color=farbe)
        axes[0].plot(pole.real, pole.imag, "x", ms=10, mew=2, color=farbe, label=name)
        print(f"{name:26s}: Pole {np.round(pole, 3)}, größte Abweichung Residuen − ODE {np.max(np.abs(x_res - ode.y[0])):.1e}")
    axes[0].axvline(0, color="0.6", lw=1); axes[0].axhline(0, color="0.6", lw=1)
    axes[0].set_xlabel("Re s"); axes[0].set_ylabel("Im s"); axes[0].set_title("Pole von X(s) in der s-Ebene")
    axes[0].legend(fontsize=8); axes[0].set_xlim(-4, 0.5); axes[0].set_ylim(-1.5, 1.5)
    axes[1].set_xlabel("Zeit t [1/ω₀]"); axes[1].set_ylabel("x(t)")
    axes[1].set_title("Sprungantwort: Residuensumme (Linie) und ODE (Punkte)"); axes[1].legend(fontsize=8)

    a_w = 1.0
    F = lambda s: np.exp(-a_w * np.sqrt(s)) / s
    tt = np.linspace(0.02, 10, 200)
    f_talbot = np.array([talbot(F, x_) for x_ in tt])
    axes[2].plot(tt, erfc(a_w / (2 * np.sqrt(tt))), "k", lw=3, label="exakt: erfc(a / 2√t)")
    axes[2].plot(tt[::6], f_talbot[::6], "o", ms=4, color="tab:red", label="Talbot-Kontur, 23 Stützstellen")
    axes[2].set_xlabel("Zeit t"); axes[2].set_ylabel("f(t)"); axes[2].set_title("F(s) = e^(−√s)/s: Verzweigungsschnitt bei s ≤ 0")
    axes[2].legend()
    plt.tight_layout()
    plt.show()
    print(f"Talbot gegen erfc: größte Abweichung {np.max(np.abs(f_talbot - erfc(a_w / (2 * np.sqrt(tt))))):.1e}")


def kramers_kronig():
    """11. Kramers–Kronig: Kausalität bestimmt den Realteil aus dem Imaginärteil (Zellen 36 von complexanalysis.ipynb)."""
    global axes, chi, chi_t, chi_t_exakt, dw, fig, gam, kk_real, omega, re_kk, t, w0
    global wd, wgit
    w0, gam = 1.0, 0.3
    chi = lambda w: 1 / (w0 ** 2 - w ** 2 - 1j * gam * w)
    print("Pole von χ:", np.round(np.roots([-1, -1j * gam, w0 ** 2]), 4), "(beide mit Im < 0)")

    def kk_real(w):
        """Re χ(ω) = (1/π) P∫ Im χ(ω')/(ω' − ω) dω' (Hauptwert mit QUADPACK, Gewicht 'cauchy')."""
        L = 200.0
        return quad(lambda x: chi(x).imag, -L, L, weight="cauchy", wvar=w, limit=400)[0] / np.pi

    omega = np.linspace(-3, 3, 121)
    re_kk = np.array([kk_real(w) for w in omega])
    print(f"größte Abweichung Re χ (Kramers–Kronig) − Re χ (exakt): {np.max(np.abs(re_kk - chi(omega).real)):.1e} "
          "(Rest vom endlichen Integrationsbereich)")

    t = np.linspace(-10, 40, 2000)
    wgit = np.linspace(-400, 400, 2 ** 18)
    dw = wgit[1] - wgit[0]
    chi_t = np.array([np.sum(chi(wgit) * np.exp(-1j * wgit * tt)).real * dw / (2 * np.pi) for tt in t[::10]])
    wd = np.sqrt(w0 ** 2 - gam ** 2 / 4)
    chi_t_exakt = np.where(t > 0, np.exp(-gam * t / 2) * np.sin(wd * t) / wd, 0.0)

    fig, axes = plt.subplots(1, 2, figsize=(15, 4.8))
    axes[0].plot(omega, chi(omega).imag, label="Im χ (Absorption)")
    axes[0].plot(omega, chi(omega).real, "k", lw=3, alpha=0.4, label="Re χ (exakt)")
    axes[0].plot(omega[::3], re_kk[::3], "o", ms=4, label="Re χ aus Im χ (Kramers–Kronig)")
    axes[0].set_xlabel("Frequenz ω [ω₀]"); axes[0].set_ylabel("χ(ω)"); axes[0].set_title("Lorentz-Oszillator, γ = 0.3 ω₀")
    axes[0].legend()
    axes[1].plot(t, chi_t_exakt, "k", lw=3, alpha=0.4, label="exakt: e^(−γt/2) sin(ω_d t)/ω_d für t > 0")
    axes[1].plot(t[::10], chi_t, ".", ms=4, label="numerische Fourier-Rücktransformation")
    axes[1].axvline(0, color="0.6", lw=1)
    axes[1].set_xlabel("Zeit t [1/ω₀]"); axes[1].set_ylabel("χ(t)"); axes[1].set_title("Antwort im Zeitbereich: null vor dem Stoß")
    axes[1].legend(fontsize=9)
    plt.tight_layout()
    plt.show()
    print(f"größter Betrag von χ(t) für t < 0 (numerisch): {np.max(np.abs(chi_t[t[::10] < -0.5])):.1e}")


def resolvent():
    """12. Die Resolvente: Projektoren, Zeitentwicklung und Zustandsdichte als Kurvenintegrale (Zellen 39 von complexanalysis.ipynb)."""
    global A, E, Eg, G, H, N, P, U, V, abstand, axes, e
    global eta, fig, j, matrix_kreisintegral, mitte, radius, rho, t0
    N = 6
    A = rng.normal(size=(N, N)) + 1j * rng.normal(size=(N, N))
    H = (A + A.conj().T) / 2
    E, V = np.linalg.eigh(H)
    G = lambda z: np.linalg.inv(z * np.eye(N) - H)


    def matrix_kreisintegral(f, a, r, n=128):
        th = 2 * np.pi * np.arange(n) / n
        z = a + r * np.exp(1j * th)
        return sum(f(zz) * G(zz) * 1j * (zz - a) for zz in z) * 2 * np.pi / n / (2j * np.pi)


    abstand = np.min(np.diff(E))
    j = 2
    P = matrix_kreisintegral(lambda z: 1.0, E[j], abstand / 2)
    print(f"Riesz-Projektor um E_{j} = {E[j]:.3f}: Abweichung von |v><v| {np.max(np.abs(P - np.outer(V[:, j], V[:, j].conj()))):.1e}, "
          f"P² = P: {np.allclose(P @ P, P)}")
    t0 = 1.7
    mitte, radius = (E[0] + E[-1]) / 2, (E[-1] - E[0]) / 2 + 1.0
    U = matrix_kreisintegral(lambda z: np.exp(-1j * z * t0), mitte, radius, n=256)
    print(f"e^(−iHt) für t = {t0} als Kurvenintegral: Abweichung von expm {np.max(np.abs(U - expm(-1j * H * t0))):.1e}")

    Eg = np.linspace(E[0] - 2, E[-1] + 2, 2000)
    fig, axes = plt.subplots(1, 2, figsize=(15, 4.8))
    for eta in [0.3, 0.05]:
        rho = np.array([-np.trace(G(x + 1j * eta)).imag / np.pi for x in Eg])
        axes[0].plot(Eg, rho, label=f"η = {eta}: Fläche im Fenster {np.sum(rho) * (Eg[1] - Eg[0]):.3f} (Rest in den Lorentz-Ausläufern)")
    for e in E:
        axes[0].axvline(e, color="0.7", lw=0.8)
    axes[0].set_xlabel("Energie E"); axes[0].set_ylabel("−(1/π) Im Tr G(E + iη)")
    axes[0].set_title("Zustandsdichte (graue Linien: Eigenwerte)"); axes[0].legend()
    phasenbild(axes[1], np.vectorize(lambda z: np.trace(G(z))), (E[0] - 1.5, E[-1] + 1.5), (-1.5, 1.5), n=360)
    axes[1].plot(E, 0 * E, "wx", ms=8)
    axes[1].set_title("Phasenbild von Tr G(z): Pole (×) bei den Eigenwerten,\ndazwischen je eine Nullstelle", fontsize=10)
    plt.tight_layout()
    plt.show()


def decay_pole():
    """13. Zerfall: ein Pol auf dem zweiten Blatt (Zellen 42 von complexanalysis.ipynb)."""
    global Eb, F_, Gamma_fit, Gamma_gr, Gamma_pol, H, N_b, P_lang, P_ueber, Sigma_II, V, W
    global _, amp, axes, bins, dF, delta, fig, g, gewicht, lam, m, t
    global t_lang, xx, z
    W, N_b, g = 10.0, 1600, 0.05
    Eb = np.linspace(-W, W, N_b)
    delta = Eb[1] - Eb[0]
    H = np.zeros((N_b + 1, N_b + 1))
    H[1:, 1:] = np.diag(Eb)
    H[0, 1:] = H[1:, 0] = g
    lam, V = np.linalg.eigh(H)
    gewicht = np.abs(V[0]) ** 2                                       # |<0|n>|²: lokale Zustandsdichte

    Gamma_gr = 2 * np.pi * g ** 2 / delta                            # Fermis goldene Regel
    Sigma_II = lambda z: g ** 2 / delta * np.log((z + W) / (z - W)) - 2j * np.pi * g ** 2 / delta   # zweites Blatt (Im z < 0)
    z = -0.5j * Gamma_gr
    for _ in range(50):                                              # Newton für z − Σ_II(z) = 0
        F_ = z - Sigma_II(z)
        dF = 1 - g ** 2 / delta * (1 / (z + W) - 1 / (z - W))
        z = z - F_ / dF
    Gamma_pol = -2 * z.imag
    print(f"goldene Regel Γ = {Gamma_gr:.4f}; Pol auf dem zweiten Blatt z* = {z:.5f}, also Γ_Pol = {Gamma_pol:.4f} "
          f"(Näherung Γ/(1 − Γ/(πW)) = {Gamma_gr / (1 - Gamma_gr / (np.pi * W)):.4f})")
    print(f"Probe: auf dem ersten Blatt hat 1/(z − Σ(z)) in der unteren Halbebene dort keinen Pol: "
          f"|z* − Σ_I(z*)| = {abs(z - (Sigma_II(z) + 2j * np.pi * g ** 2 / delta)):.3f}")

    t = np.linspace(0, 10, 600)
    amp = (gewicht[None, :] * np.exp(-1j * np.outer(t, lam))).sum(axis=1)
    P_ueber = np.abs(amp) ** 2
    m = (t > 1) & (t < 6)
    Gamma_fit = -np.polyfit(t[m], np.log(P_ueber[m]), 1)[0]
    print(f"Fit der Überlebenswahrscheinlichkeit für 1 < t < 6: Γ = {Gamma_fit:.4f}; Rückkehrzeit 2π/δ = {2 * np.pi / delta:.0f}")
    t_lang = np.linspace(495, 512, 400)
    P_lang = np.abs((gewicht[None, :] * np.exp(-1j * np.outer(t_lang, lam))).sum(axis=1)) ** 2

    fig, axes = plt.subplots(1, 3, figsize=(18, 4.8))
    axes[0].semilogy(t, P_ueber, label="exakt (Diagonalisierung)")
    axes[0].semilogy(t, np.exp(-Gamma_pol * t), "--", label=f"e^(−Γ_Pol t), Γ_Pol = {Gamma_pol:.3f}")
    axes[0].semilogy(t, np.exp(-Gamma_gr * t), ":", label=f"e^(−Γ t), goldene Regel {Gamma_gr:.3f}")
    axes[0].set_xlabel("Zeit t"); axes[0].set_ylabel("|<0|e^(−iHt)|0>|²"); axes[0].set_title("Überlebenswahrscheinlichkeit")
    axes[0].legend(fontsize=8)
    axes[1].plot(t_lang, P_lang)
    axes[1].set_xlabel("Zeit t"); axes[1].set_ylabel("Überlebenswahrscheinlichkeit")
    axes[1].set_title(f"Rückkehr bei t ≈ 2π/δ = {2 * np.pi / delta:.0f} (diskretes Spektrum)")
    bins = np.linspace(-4, 4, 161)
    axes[2].hist(lam, bins=bins, weights=gewicht / (bins[1] - bins[0]), color="0.6", label="|<0|n>|² der Eigenzustände")
    xx = np.linspace(-4, 4, 400)
    axes[2].plot(xx, (Gamma_pol / (2 * np.pi)) / (xx ** 2 + Gamma_pol ** 2 / 4), "k", label="Lorentz-Linie der Breite Γ_Pol")
    axes[2].set_xlabel("Energie E"); axes[2].set_ylabel("lokale Zustandsdichte"); axes[2].set_title("Spektrallinie des zerfallenden Zustands")
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()


def continuation():
    """14. Analytische Fortsetzung: Gamma, Zeta und $-\\tfrac1{12}$ (Zellen 45 von complexanalysis.ipynb)."""
    global Zt, axes, eps, fig, n, nullst, res, sig, tk, z_m1, zeta_reell
    for n in range(4):
        res = kreisintegral(lambda s: gamma_fn(s), -n, 0.1) / (2j * np.pi)
        print(f"Res Γ bei s = −{n}: {res.real:+.6f} (Formel (−1)^n/n! = {(-1) ** n / math.factorial(n):+.6f})")
    print(f"Γ(1/2)² = {gamma_fn(0.5) ** 2:.10f} = π; Spiegelung Γ(s)Γ(1−s) sin(πs)/π bei s = 0.3+0.4i: "
          f"{gamma_fn(0.3 + 0.4j) * gamma_fn(0.7 - 0.4j) * np.sin(np.pi * (0.3 + 0.4j)) / np.pi:.10f}")
    z_m1 = 2 ** -1 * np.pi ** -2 * np.sin(-np.pi / 2) * gamma_fn(2) * (np.pi ** 2 / 6)
    print(f"ζ(−1) aus der Funktionalgleichung: {z_m1:.10f}; mpmath: {float(mpmath.zeta(-1)):.10f}; ζ(0) = {float(mpmath.zeta(0)):.4f}")
    for eps in [0.1, 0.01, 0.001]:
        n = np.arange(1, int(60 / eps))
        print(f"ε = {eps}: Σ n e^(−εn) − 1/ε² = {np.sum(n * np.exp(-eps * n)) - 1 / eps ** 2:+.8f}  (−1/12 = {-1 / 12:+.8f})")

    fig, axes = plt.subplots(1, 3, figsize=(18, 4.8))
    phasenbild(axes[0], gamma_fn, (-4.5, 4.5), (-3, 3), n=600)
    axes[0].set_xlabel("Re s"); axes[0].set_ylabel("Im s")
    axes[0].set_title("Phasenbild von Γ(s): Pole bei 0, −1, −2, ...")
    sig = np.linspace(-9, 4, 1200)
    zeta_reell = np.array([float(mpmath.zeta(s_)) if abs(s_ - 1) > 1e-3 else np.nan for s_ in sig])
    axes[1].plot(sig, zeta_reell)
    axes[1].plot([-2, -4, -6, -8], [0, 0, 0, 0], "ro", label="triviale Nullstellen")
    axes[1].plot(-1, -1 / 12, "ks", label="ζ(−1) = −1/12")
    axes[1].axhline(0, color="0.6", lw=1); axes[1].axvline(1, color="0.8", ls="--", lw=1)
    axes[1].set_ylim(-1.5, 3); axes[1].set_xlabel("s (reell)"); axes[1].set_ylabel("ζ(s)")
    axes[1].set_title("ζ auf der reellen Achse (Pol bei s = 1)"); axes[1].legend(fontsize=8)
    tk = np.linspace(0, 50, 2000)
    Zt = np.array([float(mpmath.siegelz(x_)) for x_ in tk])           # Hardy-Funktion: reell, |Z(t)| = |ζ(1/2 + it)|
    nullst = [float(mpmath.zetazero(k).imag) for k in range(1, 11)]
    axes[2].plot(tk, Zt, label="Z(t), |Z(t)| = |ζ(½ + it)|")
    axes[2].plot(nullst, np.zeros(10), "ro", ms=5, label="Nullstellen 14.13, 21.02, 25.01, ...")
    axes[2].axhline(0, color="0.6", lw=1)
    axes[2].set_xlabel("t"); axes[2].set_ylabel("Z(t)"); axes[2].set_title("ζ auf der kritischen Geraden Re s = ½")
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()
    print("erste Nullstellen auf der kritischen Geraden:", np.round(nullst[:5], 4))


def lee_yang_zeros():
    """15. Lee–Yang: Nullstellen der Zustandssumme (Zellen 48 von complexanalysis.ipynb)."""
    global N, ax, axes, bJ, farbe, fig, kreis, lee_yang, nz, titel, winkel
    mpmath.mp.dps = 80


    def lee_yang(N, bJ):
        """Nullstellen von Z(z) = Σ_n C(N, n) exp(βJ/(2N)·((N−2n)² − N)) z^n, mit 80 Stellen gerechnet."""
        koef = [mpmath.binomial(N, n) * mpmath.exp(mpmath.mpf(bJ) / (2 * N) * ((N - 2 * n) ** 2 - N)) for n in range(N + 1)]
        return np.array([complex(r_) for r_ in mpmath.polyroots(koef[::-1], maxsteps=500, extraprec=400)])


    fig, axes = plt.subplots(1, 3, figsize=(18, 5.4))
    kreis = np.exp(1j * np.linspace(0, 2 * np.pi, 400))
    for ax, (bJ, titel) in zip(axes[:2], [(0.6, "βJ = 0.6 (ungeordnet)"), (1.6, "βJ = 1.6 (geordnet)")]):
        ax.plot(kreis.real, kreis.imag, color="0.75")
        for N, farbe in [(20, "tab:blue"), (60, "tab:orange")]:
            nz = lee_yang(N, bJ)
            ax.plot(nz.real, nz.imag, ".", color=farbe, ms=6,
                    label=f"N = {N}: |z| ∈ [{np.abs(nz).min():.6f}, {np.abs(nz).max():.6f}], kleinster Winkel {np.min(np.abs(np.angle(nz))):.3f}")
        ax.plot(1, 0, "k*", ms=12)
        ax.set_aspect("equal"); ax.set_xlabel("Re z"); ax.set_ylabel("Im z"); ax.set_title(f"Ferromagnet, {titel}")
        ax.legend(fontsize=7, loc="lower left")
    nz = lee_yang(40, -1.0)
    axes[2].axvline(0, color="0.75", lw=3, label="Einheitskreis |z| = 1")
    axes[2].plot(np.log10(np.abs(nz)), np.angle(nz), "r.", ms=7, label="Nullstellen")
    axes[2].set_ylim(-np.pi - 0.2, np.pi + 0.2)
    axes[2].set_xlabel("log₁₀ |z|"); axes[2].set_ylabel("arg z [rad]")
    axes[2].set_title("Antiferromagnet βJ = −1, N = 40: Nullstellen auf der\nnegativen reellen Achse (arg z = π), nicht auf dem Kreis", fontsize=10)
    axes[2].legend(fontsize=8)
    print(f"Antiferromagnet: |z| reicht von {np.abs(nz).min():.3g} bis {np.abs(nz).max():.3g}")
    plt.tight_layout()
    plt.show()

    for bJ in [0.6, 1.0, 1.6]:
        winkel = [np.min(np.abs(np.angle(lee_yang(N, bJ)))) for N in [20, 40, 80]]
        print(f"βJ = {bJ}: kleinster Winkel der Nullstellen zur reellen Achse für N = 20, 40, 80: {np.round(winkel, 4)}")
