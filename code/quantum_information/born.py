"""Projektive Messung und Born-Regel: Spektralsatz, Häufigkeiten gegen Wahrscheinlichkeiten, Messrichtung auf der Bloch-Kugel, Lüders-Regel und entartete Eigenwerte.

Für quantum_information.ipynb aus bornrule.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: spectral_theorem, frequencies, frequency_distribution, bloch_direction, post_measurement, degenerate.
"""
import numpy as np
import matplotlib.pyplot as plt


def spectral_theorem():
    """1. Kontrolle des Spektralsatzes (Zellen 4, 6 von bornrule.ipynb)."""
    global A, I2, P, bloch_zustand, born, messen, rng, spektralzerlegung, sx, sy, sz, werte
    rng = np.random.default_rng(42)

    I2 = np.eye(2, dtype=complex)
    sx = np.array([[0, 1], [1, 0]], dtype=complex)
    sy = np.array([[0, -1j], [1j, 0]])
    sz = np.array([[1, 0], [0, -1]], dtype=complex)


    def spektralzerlegung(A, tol=1e-9):
        """Verschiedene Eigenwerte a_k von A und die Projektoren P_k auf ihre Eigenräume."""
        w, V = np.linalg.eigh(A)
        werte = []
        for a in w:                                   # entartete Eigenwerte nur einmal aufnehmen
            if not any(abs(a - b) < tol for b in werte):
                werte.append(a)
        projektoren = []
        for a in werte:
            Vk = V[:, np.abs(w - a) < tol]            # Eigenvektoren zum Eigenwert a
            projektoren.append(Vk @ Vk.conj().T)
        return np.array(werte), projektoren


    def born(rho, projektoren):
        """Born-Wahrscheinlichkeiten p(k) = Tr(rho P_k)."""
        return np.array([np.trace(rho @ P).real for P in projektoren])


    def messen(rho, A, N):
        """N unabhängige Messungen von A im Zustand rho; gibt die Messwerte zurück."""
        werte, P = spektralzerlegung(A)
        p = born(rho, P)
        return rng.choice(werte, size=N, p=p / p.sum())


    def bloch_zustand(theta, phi):
        """Reiner Qubit-Zustand mit den Bloch-Winkeln theta und phi als Dichtematrix."""
        psi = np.array([np.cos(theta / 2), np.exp(1j * phi) * np.sin(theta / 2)])
        return np.outer(psi, psi.conj())

    A = np.array([[2, 1, 0], [1, 2, 0], [0, 0, 3]], dtype=complex)
    werte, P = spektralzerlegung(A)
    print("Eigenwerte:        ", np.round(werte, 6))
    print("A = Σ a_k P_k:     ", np.allclose(A, sum(a * Pk for a, Pk in zip(werte, P))))
    print("Σ P_k = I:         ", np.allclose(sum(P), np.eye(3)))
    print("P_k P_l = 0 (k≠l): ", all(np.allclose(P[i] @ P[j], 0) for i in range(len(P)) for j in range(len(P)) if i != j))
    print("Rang der P_k:      ", [int(round(np.trace(Pk).real)) for Pk in P])


def frequencies():
    """2. Häufigkeit gegen Anzahl der Messungen (Zellen 9 von bornrule.ipynb)."""
    global N, N_max, ax, ergebnisse, f_plus, fig, p_plus, phi, rho, sigma, theta
    theta, phi = 2 * np.pi / 3, 0.4
    rho = bloch_zustand(theta, phi)
    p_plus = np.trace(rho @ (I2 + sz) / 2).real          # Born-Wahrscheinlichkeit für +1

    N_max = 10_000
    ergebnisse = messen(rho, sz, N_max)
    N = np.arange(1, N_max + 1)
    f_plus = np.cumsum(np.isclose(ergebnisse, 1)) / N     # laufende Häufigkeit von +1
    sigma = np.sqrt(p_plus * (1 - p_plus) / N)

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(N, f_plus, lw=1, label="gemessene Häufigkeit")
    ax.axhline(p_plus, color="k", ls="--", label=f"Born: p(+1) = {p_plus:.3f}")
    ax.fill_between(N, p_plus - sigma, p_plus + sigma, alpha=0.25, label="± eine Standardabweichung")
    ax.set_xscale("log")
    ax.set_ylim(0, 1)
    ax.set_xlabel("Anzahl der Messungen N")
    ax.set_ylabel("Häufigkeit von +1")
    ax.set_title("Messung von σ_z: Häufigkeit gegen Anzahl der Messungen")
    ax.legend()
    plt.show()
    print(f"p(+1) = {p_plus:.4f}; nach N = {N_max}: Häufigkeit {f_plus[-1]:.4f}, Abweichung {abs(f_plus[-1] - p_plus):.4f}, "
          f"eine Standardabweichung {sigma[-1]:.4f}")
    print(f"Anteil der N, bei denen die laufende Häufigkeit im Band ±σ liegt: {np.mean(np.abs(f_plus - p_plus) <= sigma):.2f}")


def frequency_distribution():
    """3. Verteilung der Häufigkeit bei festem N (Zellen 12 von bornrule.ipynb)."""
    global N_fest, ax, f, fig, s, wiederholungen, x
    N_fest, wiederholungen = 100, 5000
    f = np.array([np.mean(np.isclose(messen(rho, sz, N_fest), 1)) for _ in range(wiederholungen)])

    s = np.sqrt(p_plus * (1 - p_plus) / N_fest)
    x = np.linspace(p_plus - 4 * s, p_plus + 4 * s, 300)

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.hist(f, bins=np.arange(-0.005, 1.005, 0.01), density=True, alpha=0.6, label=f"{wiederholungen} Serien zu je {N_fest} Messungen")
    ax.plot(x, np.exp(-(x - p_plus) ** 2 / (2 * s**2)) / (s * np.sqrt(2 * np.pi)), "k", label="Normalverteilung mit √(p(1−p)/N)")
    ax.set_xlim(p_plus - 5 * s, p_plus + 5 * s)
    ax.set_xlabel("Häufigkeit von +1")
    ax.set_ylabel("Dichte")
    ax.set_title(f"Streuung der Häufigkeit bei N = {N_fest}")
    ax.legend()
    plt.show()
    print(f"gemessene Standardabweichung {f.std():.4f}, vorhergesagt {s:.4f}")


def bloch_direction():
    """4. Messrichtung auf der Bloch-Kugel (Zellen 15 von bornrule.ipynb)."""
    global A, a, abw, ax, fig, n, p_gemessen, p_theorie, r, sig, winkel, z
    r = np.array([np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)])   # Bloch-Vektor von rho

    winkel = np.linspace(0, np.pi, 13)                      # Messrichtung in der x-z-Ebene
    p_theorie, p_gemessen = [], []
    for a in winkel:
        n = np.array([np.sin(a), 0, np.cos(a)])
        A = n[0] * sx + n[1] * sy + n[2] * sz
        p_gemessen.append(np.mean(np.isclose(messen(rho, A, 2000), 1)))
        p_theorie.append((1 + n @ r) / 2)

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(np.degrees(winkel), p_theorie, "k-", label="Born-Regel")
    ax.plot(np.degrees(winkel), p_gemessen, "o", label="2000 Messungen pro Richtung")
    ax.set_xlabel("Winkel der Messrichtung zur z-Achse [Grad]")
    ax.set_ylabel("p(+1)")
    ax.set_title("Messung von n·σ für Richtungen in der x-z-Ebene")
    ax.legend()
    plt.show()
    abw = np.abs(np.array(p_gemessen) - np.array(p_theorie))
    print(f"Bloch-Vektor r = {np.round(r, 3)}; p(+1) von {min(p_theorie):.3f} bis {max(p_theorie):.3f}")
    sig = np.sqrt(np.array(p_theorie) * (1 - np.array(p_theorie)) / 2000)   # Standardabweichung je Richtung
    z = abw / sig
    print(f"größte Abweichung Messung gegen Born-Regel: {abw.max():.3f} bei {np.degrees(winkel[abw.argmax()]):.0f}°")
    print(f"in Standardabweichungen: größter Wert {z.max():.1f} bei {np.degrees(winkel[z.argmax()]):.0f}°, Mittelwert {z.mean():.2f}")


def post_measurement():
    """5. Zustand nach der Messung (Zellen 18 von bornrule.ipynb)."""
    global _, a1, a2, b1, b3, gleich_a, gleich_b, messen_mit_kollaps, rho1, rho2
    def messen_mit_kollaps(rho, A):
        """Eine Messung: Ergebnis a_k und Zustand P_k rho P_k / p(k) danach."""
        werte, P = spektralzerlegung(A)
        p = born(rho, P)
        k = rng.choice(len(werte), p=p / p.sum())
        return werte[k], P[k] @ rho @ P[k] / p[k]


    gleich_a = gleich_b = 0
    for _ in range(1000):
        a1, rho1 = messen_mit_kollaps(rho, sz)
        a2, _ = messen_mit_kollaps(rho1, sz)
        gleich_a += np.isclose(a1, a2)

        b1, rho1 = messen_mit_kollaps(rho, sz)
        _, rho2 = messen_mit_kollaps(rho1, sx)
        b3, _ = messen_mit_kollaps(rho2, sz)
        gleich_b += np.isclose(b1, b3)

    print("(a) σ_z, dann σ_z:          gleiches Ergebnis in", gleich_a, "von 1000 Fällen")
    print("(b) σ_z, dann σ_x, dann σ_z: gleiches Ergebnis in", gleich_b, "von 1000 Fällen")


def degenerate():
    """6. Entartete Eigenwerte (Zellen 21 von bornrule.ipynb)."""
    global P, name, obs, psi, rho3, rho_nach, werte
    psi = np.ones(3) / np.sqrt(3)
    rho3 = np.outer(psi, psi.conj())

    for name, obs in [("A = diag(1, 1, -1), entartet  ", np.diag([1, 1, -1]).astype(complex)),
                      ("B = diag(1, 2, -1), verfeinert", np.diag([1, 2, -1]).astype(complex))]:
        werte, P = spektralzerlegung(obs)
        rho_nach = sum(Pk @ rho3 @ Pk for Pk in P)          # Zustand nach der Messung, Ergebnis nicht gelesen
        print(f"{name}: Element <0|rho|1> vorher {rho3[0, 1].real:.3f}, nachher {rho_nach[0, 1].real:.3f}")
