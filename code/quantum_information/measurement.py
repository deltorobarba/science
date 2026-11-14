"""Allgemeine Quantenmessung: POVM und Naimark, Zeigermodell, Zustandsunterscheidung, Unschärfe, schwache Messung, kontinuierliche Messung und Trajektorien, Zeno-Effekt, Feedback, Tomographie, Benchmarking und Classical Shadows.

Für quantum_information.ipynb aus quantummeasurement.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: povm, pointer_model, two_states, three_states, uncertainty, weak_value, continuous, trajectories, zeno, feedback, state_tomography, process_tomography, benchmarking, shadows.
"""
import cvxpy as cp
import sys
import functools
import itertools
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import expm, null_space
from scipy.optimize import curve_fit
from scipy.special import betainc
from scipy.stats import norm


def povm():
    """7. POVMs auf der Bloch-Kugel und Naimark-Dilatation (Zellen 4, 6 von quantummeasurement.ipynb)."""
    global E, E_sic, E_trine, I2, PAULI, U, X, Y, Z, a, amp, ax1
    global ax2, ax3, bloch, bloch_ket, c, dag, dm, ergebnis, fig, from_bloch, haeufig, is_povm
    global k, kreis, liouvillian, m, n_m, n_sic, n_trine, naimark_unitaer, name, p_naimark, p_povm, psd_sqrt
    global psi, r, rho, rng, shannon, sme_step, trace_distance, uu, v, vv
    rng = np.random.default_rng(2026)
    I2 = np.eye(2, dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Y = np.array([[0, -1j], [1j, 0]])
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    PAULI = {"I": I2, "X": X, "Y": Y, "Z": Z}
    def dm(psi):
        """Normierte Dichtematrix |ψ><ψ|."""
        psi = np.asarray(psi, dtype=complex)
        psi = psi / np.linalg.norm(psi)
        return np.outer(psi, psi.conj())
    def bloch_ket(theta, phi=0.0):
        """Reiner Qubit-Zustand mit den Bloch-Winkeln theta, phi."""
        return np.array([np.cos(theta / 2), np.exp(1j * phi) * np.sin(theta / 2)])
    def from_bloch(r):
        """Qubit-Dichtematrix (I + r·σ)/2."""
        return 0.5 * (I2 + r[0] * X + r[1] * Y + r[2] * Z)
    def bloch(rho):
        """Bloch-Vektor (Tr ρX, Tr ρY, Tr ρZ)."""
        return np.real([np.trace(rho @ P) for P in (X, Y, Z)])
    def psd_sqrt(A):
        """Wurzel einer positiv semidefiniten Matrix über die Eigenzerlegung."""
        w, V = np.linalg.eigh(A)
        return (V * np.sqrt(np.clip(w, 0, None))) @ V.conj().T
    def trace_distance(rho, sigma):
        """Spurabstand ½||ρ − σ||₁."""
        return 0.5 * np.abs(np.linalg.eigvalsh(rho - sigma)).sum()
    def is_povm(E, tol=1e-9):
        """Prüft E_m ≥ 0 und Σ E_m = I."""
        positiv = all(np.linalg.eigvalsh(Em).min() > -tol for Em in E)
        return positiv and np.allclose(sum(E), np.eye(E[0].shape[0]), atol=tol)
    def shannon(p):
        """Shannon-Entropie in Bit."""
        p = np.asarray(p, dtype=float)
        p = p[p > 1e-15]
        return -(p * np.log2(p)).sum()
    def liouvillian(H, Ls):
        """Lindblad-Gleichung als Matrix auf vec(ρ) (spaltenweise gestapelt): vec(AρB) = (Bᵀ ⊗ A) vec(ρ)."""
        d = H.shape[0]
        Id = np.eye(d)
        Lv = -1j * (np.kron(Id, H) - np.kron(H.T, Id))
        for L in Ls:
            LdL = L.conj().T @ L
            Lv = Lv + np.kron(L.conj(), L) - 0.5 * np.kron(Id, LdL) - 0.5 * np.kron(LdL.T, Id)
        return Lv
    def dag(A):
        return np.swapaxes(A.conj(), -1, -2)
    def sme_step(rho, H, L, dt):
        """Ein Zeitschritt der diffusiven stochastischen Mastergleichung für viele Trajektorien zugleich.
    Kraus-Form nach Rouchon und Ralph: ρ → MρM†/Tr mit M = I − (iH + ½L†L)dt + L dY; bleibt positiv.
    rho: (n, d, d); H: (d, d) oder (n, d, d); L: (d, d). Gibt den neuen Zustand und das Messsignal dY zurück."""
        n, d, _ = rho.shape
        Lr = L @ rho
        signal = np.real(np.trace(Lr + dag(Lr), axis1=1, axis2=2))           # Tr(Lρ + ρL†)
        dY = signal * dt + np.sqrt(dt) * rng.standard_normal(n)
        M = np.eye(d) - (1j * H + 0.5 * dag(L) @ L) * dt + L * dY[:, None, None]
        rho = M @ rho @ dag(M)
        return rho / np.real(np.trace(rho, axis1=1, axis2=2))[:, None, None], dY

    # Trine: drei Bloch-Richtungen im Abstand von 120° in der x-z-Ebene; SIC: die vier Ecken eines Tetraeders
    n_trine = [np.array([np.sin(a), 0, np.cos(a)]) for a in 2 * np.pi * np.arange(3) / 3]
    n_sic = [np.array([0, 0, 1.0])] + [np.array([np.sqrt(8) / 3 * np.cos(b), np.sqrt(8) / 3 * np.sin(b), -1 / 3])
                                       for b in 2 * np.pi * np.arange(3) / 3]
    E_trine = [2 / 3 * from_bloch(v) for v in n_trine]          # (I + n·σ)/3
    E_sic = [1 / 2 * from_bloch(v) for v in n_sic]              # (I + n·σ)/4
    print("Trine ist ein POVM:", is_povm(E_trine), "| SIC ist ein POVM:", is_povm(E_sic))
    print("Eigenwerte eines Trine-Elements:", np.round(np.linalg.eigvalsh(E_trine[0]), 3), "-> Rang 1, aber kein Projektor")
    print("SIC informationell vollständig (4 linear unabhängige Elemente):",
          np.linalg.matrix_rank(np.array([E.ravel() for E in E_sic])) == 4)


    def naimark_unitaer(M):
        """Unitäre U auf System ⊗ Ancilla mit U(|ψ>⊗|0>) = Σ_m M_m|ψ> ⊗ |m>."""
        n_m, d = len(M), M[0].shape[0]
        V = np.zeros((d * n_m, d), dtype=complex)
        for m, Mm in enumerate(M):
            V[m::n_m, :] = Mm                                    # Zeile i·n_m + m gehört zu |i>⊗|m>
        U = np.zeros((d * n_m, d * n_m), dtype=complex)
        U[:, ::n_m] = V                                          # Spalten zu |j>⊗|0>
        U[:, [k for k in range(d * n_m) if k % n_m]] = null_space(V.conj().T)   # orthonormal ergänzen
        return U


    psi = bloch_ket(1.1, 0.7)                                    # ein beliebiger Testzustand
    rho = dm(psi)
    ergebnis = {}
    for name, E in [("Trine", E_trine), ("SIC", E_sic)]:
        U = naimark_unitaer([psd_sqrt(Em) for Em in E])          # Lüders-Messoperatoren M_m = √E_m
        n_m = len(E)
        amp = (U @ np.kron(psi, np.eye(n_m)[0])).reshape(2, n_m) # Amplituden zu |i>⊗|m>
        p_naimark = (np.abs(amp) ** 2).sum(axis=0)               # projektive Messung der Ancilla
        p_povm = np.array([np.trace(Em @ rho).real for Em in E])
        ergebnis[name] = (p_povm, p_naimark)
        print(f"{name}: U ist {2 * n_m}x{2 * n_m} und unitär: {np.allclose(U.conj().T @ U, np.eye(2 * n_m))} | "
              f"Tr(E_m ρ) = {np.round(p_povm, 4)} | Naimark = {np.round(p_naimark, 4)}")

    p_povm, p_naimark = ergebnis["SIC"]
    haeufig = rng.multinomial(20_000, p_naimark) / 20_000        # 20 000 simulierte Messungen der Ancilla

    fig = plt.figure(figsize=(16, 4.8))
    ax1 = fig.add_subplot(1, 3, 1)
    kreis = np.linspace(0, 2 * np.pi, 200)
    ax1.plot(np.sin(kreis), np.cos(kreis), color="0.75")
    for k, v in enumerate(n_trine):
        ax1.annotate("", xy=(v[0], v[2]), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color="tab:blue", lw=2))
        ax1.text(1.18 * v[0], 1.18 * v[2], f"$E_{k}$", ha="center", va="center", fontsize=12)
    r = bloch(rho)
    ax1.plot(r[0], r[2], "o", color="tab:red", label="Testzustand (projiziert)")
    ax1.set_aspect("equal")
    ax1.set_xlim(-1.45, 1.45); ax1.set_ylim(-1.45, 1.45)
    ax1.set_xlabel("Bloch-Komponente x"); ax1.set_ylabel("Bloch-Komponente z")
    ax1.set_title("Trine-POVM in der x-z-Ebene")
    ax1.legend(loc="lower left")

    ax2 = fig.add_subplot(1, 3, 2, projection="3d")
    uu, vv = np.mgrid[0:2 * np.pi:30j, 0:np.pi:15j]
    ax2.plot_wireframe(np.cos(uu) * np.sin(vv), np.sin(uu) * np.sin(vv), np.cos(vv), color="0.85", lw=0.5)
    for a, c in itertools.combinations(n_sic, 2):
        ax2.plot(*zip(a, c), color="tab:green")
    for v in n_sic:
        ax2.quiver(0, 0, 0, *v, color="tab:green", arrow_length_ratio=0.1)
    ax2.set_xlabel("x"); ax2.set_ylabel("y"); ax2.set_zlabel("z")
    ax2.set_title("SIC-POVM: Tetraeder in der Bloch-Kugel")

    ax3 = fig.add_subplot(1, 3, 3)
    m = np.arange(4)
    ax3.bar(m - 0.2, p_povm, 0.4, label="Tr(E_m ρ)")
    ax3.bar(m + 0.2, haeufig, 0.4, label="Naimark: 20 000 Messungen der Ancilla")
    ax3.set_xticks(m)
    ax3.set_xlabel("Ergebnis m"); ax3.set_ylabel("Wahrscheinlichkeit")
    ax3.set_title("SIC-POVM: direkt gegen Naimark-Dilatation")
    ax3.legend(loc="upper right")
    plt.tight_layout()
    plt.show()


def pointer_model():
    """8. Das Zeigermodell: von stark zu schwach (Zellen 9 von quantummeasurement.ipynb)."""
    global a, axes, dq, farbe, fig, g, g_test, g_werte, gauss, info_sim, koh_num, p_plus
    global phi0, q, q_mess, sigma
    p_plus = 0.7                                               # Born-Wahrscheinlichkeit für σ_z = +1
    sigma = 1.0                                                # Breite des Zeigers
    q = np.linspace(-7, 7, 1401)
    dq = q[1] - q[0]
    gauss = lambda q, mu: np.exp(-(q - mu) ** 2 / (2 * sigma ** 2)) / np.sqrt(2 * np.pi * sigma ** 2)
    phi0 = lambda q: (2 * np.pi * sigma ** 2) ** -0.25 * np.exp(-q ** 2 / (4 * sigma ** 2))   # Zeiger-Wellenfunktion

    fig, axes = plt.subplots(1, 2, figsize=(15, 4.8))
    for g, farbe in [(3.0, "tab:blue"), (1.0, "tab:orange"), (0.2, "tab:green")]:
        a = np.where(rng.random(20_000) < p_plus, 1, -1)       # Eigenwert nach der Born-Regel
        q_mess = g * a + sigma * rng.standard_normal(20_000)   # Zeiger um g·a verschoben, dazu seine Breite
        axes[0].hist(q_mess, bins=100, range=(-7, 7), density=True, alpha=0.3, color=farbe)
        axes[0].plot(q, p_plus * gauss(q, g) + (1 - p_plus) * gauss(q, -g), color=farbe, label=f"g/σ = {g:g}")
    axes[0].set_xlabel("Zeigerposition q [σ]")
    axes[0].set_ylabel("Wahrscheinlichkeitsdichte [1/σ]")
    axes[0].set_title("Zeigerverteilung bei p(+1) = 0.7: Histogramm aus 20 000 Läufen und Formel")
    axes[0].legend()

    g_werte = np.logspace(-1.5, 0.8, 80)
    g_test = np.array([0.1, 0.3, 0.6, 1.0, 1.6, 2.5])
    # Information: Eigenzustand +1, geraten wird nach dem Vorzeichen des Zeigers
    info_sim = [np.mean(g + sigma * rng.standard_normal(20_000) > 0) for g in g_test]
    # Störung: Nichtdiagonalelement von |+x> nach der Messung ohne Ablesen, M(q) = diag(φ0(q−g), φ0(q+g))
    koh_num = [sum(phi0(q - g) * phi0(q + g)) * dq for g in g_test]

    axes[1].plot(g_werte, norm.cdf(g_werte / sigma), color="tab:purple", label="Information: P(richtig geraten) = Φ(g/σ)")
    axes[1].plot(g_test, info_sim, "o", color="tab:purple", label="simuliert (20 000 Läufe)")
    axes[1].plot(g_werte, np.exp(-g_werte ** 2 / (2 * sigma ** 2)), color="tab:red", label="verbleibende Kohärenz e^(−g²/2σ²)")
    axes[1].plot(g_test, koh_num, "s", color="tab:red", label="numerisch aus den Messoperatoren M(q)")
    axes[1].set_xscale("log")
    axes[1].set_xlabel("Kopplung g/σ")
    axes[1].set_ylabel("Wahrscheinlichkeit bzw. Faktor")
    axes[1].set_title("Information gegen Störung")
    axes[1].legend(fontsize=9)
    plt.tight_layout()
    plt.show()


def two_states():
    """9. Zwei Zustände unterscheiden: Helstrom und eindeutige Unterscheidung (Zellen 12 von quantummeasurement.ipynb)."""
    global E0, E1, E_usd, N, P0, V, a, antwort, ax, c, c_werte, fehler_hel
    global fehler_usd, fig, frage_usd, i, j, p, p_null, psi0, psi1, r, rho0, rho1
    global senkrecht, sim, w
    def senkrecht(psi):
        """Der zu einem Qubit-Zustand orthogonale Zustand."""
        return np.array([-psi[1].conj(), psi[0].conj()])


    c_werte = np.linspace(0, 1, 201)
    sim = []
    for c in [0.2, 0.4, 0.6, 0.8, 0.95]:
        psi0, psi1 = bloch_ket(0), bloch_ket(2 * np.arccos(c))            # Überlapp |<ψ0|ψ1>| = c
        rho0, rho1 = dm(psi0), dm(psi1)
        N = 20_000
        i = rng.integers(0, 2, N)                                          # präparierter Zustand, gleiche Priors

        # Helstrom: Projektor auf den positiven Eigenraum von Γ = ½ρ0 − ½ρ1 heißt „0“
        w, V = np.linalg.eigh(0.5 * rho0 - 0.5 * rho1)
        P0 = V[:, w > 0] @ V[:, w > 0].conj().T
        p_null = np.where(i == 0, np.trace(P0 @ rho0).real, np.trace(P0 @ rho1).real)
        fehler_hel = np.mean((rng.random(N) < p_null) != (i == 0))

        # eindeutige Unterscheidung: E0 ∝ |ψ1⊥><ψ1⊥|, E1 ∝ |ψ0⊥><ψ0⊥|, der Rest heißt „?“
        a = 1 / (1 + c)
        E0, E1 = a * dm(senkrecht(psi1)), a * dm(senkrecht(psi0))
        E_usd = [E0, E1, I2 - E0 - E1]
        antwort = np.empty(N, dtype=int)
        for j, r in enumerate((rho0, rho1)):
            p = np.clip([np.trace(E @ r).real for E in E_usd], 0, None)
            antwort[i == j] = rng.choice(3, size=(i == j).sum(), p=p / p.sum())
        fehler_usd = np.mean((antwort < 2) & (antwort != i))
        frage_usd = np.mean(antwort == 2)
        sim.append((c, fehler_hel, frage_usd))
        print(f"c = {c:.2f}: Helstrom-Fehler {fehler_hel:.4f} (Formel {0.5 * (1 - np.sqrt(1 - c ** 2)):.4f}) | "
              f"eindeutig: Fehler {fehler_usd:.4f}, „?“ {frage_usd:.4f} (Formel {c:.2f}) | "
              f"E_? ≥ 0: {np.linalg.eigvalsh(E_usd[2]).min() > -1e-12}")
    sim = np.array(sim)

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(c_werte, 0.5 * (1 - np.sqrt(1 - c_werte ** 2)), color="tab:blue", label="Helstrom: Fehlerwahrscheinlichkeit")
    ax.plot(c_werte, c_werte ** 2 / 2, "--", color="tab:blue", label="naiv (Projektor auf ψ₀): Fehlerwahrscheinlichkeit")
    ax.plot(c_werte, c_werte, color="tab:orange", label="eindeutig: Wahrscheinlichkeit für „?“ (nie falsch)")
    ax.plot(sim[:, 0], sim[:, 1], "o", color="tab:blue", label="Simulation Helstrom")
    ax.plot(sim[:, 0], sim[:, 2], "s", color="tab:orange", label="Simulation eindeutig")
    ax.set_xlabel("Überlapp c = |⟨ψ₀|ψ₁⟩|")
    ax.set_ylabel("Wahrscheinlichkeit")
    ax.set_title("Zwei reine Zustände mit gleichen Priors unterscheiden")
    ax.legend()
    plt.show()


def three_states():
    """10. Drei Zustände: SDP gegen Pretty-Good-Measurement (Zellen 15 von quantummeasurement.ipynb)."""
    global P_pgm, P_sdp, ax, beta, bt, fig, k120, pgm, ps, rhos, sdp_unterscheidung
    def sdp_unterscheidung(rhos, ps):
        """Beste Erfolgswahrscheinlichkeit max Σ p_i Tr(E_i ρ_i) unter E_i ≥ 0, Σ E_i = I."""
        d = rhos[0].shape[0]
        E = [cp.Variable((d, d), hermitian=True) for _ in rhos]
        ziel = cp.Maximize(cp.real(sum(p * cp.trace(r @ Ei) for p, r, Ei in zip(ps, rhos, E))))
        problem = cp.Problem(ziel, [Ei >> 0 for Ei in E] + [sum(E) == np.eye(d)])
        problem.solve()
        return problem.value


    def pgm(rhos, ps):
        """Erfolgswahrscheinlichkeit der Pretty-Good-Measurement E_i = ρ^(−1/2) p_i ρ_i ρ^(−1/2)."""
        rho = sum(p * r for p, r in zip(ps, rhos))
        w, V = np.linalg.eigh(rho)
        inv_wurzel = (V * np.where(w > 1e-12, 1 / np.sqrt(np.abs(w) + 1e-300), 0)) @ V.conj().T
        E = [inv_wurzel @ (p * r) @ inv_wurzel for p, r in zip(ps, rhos)]
        E[0] = E[0] + np.eye(len(w)) - sum(E)          # Kern von ρ zu E_0 (ändert die Erfolgswahrscheinlichkeit nicht)
        assert is_povm(E)
        return sum(p * np.trace(r @ Ei).real for p, r, Ei in zip(ps, rhos, E))


    beta = np.radians(np.linspace(5, 180, 36))
    P_sdp, P_pgm = [], []
    for bt in beta:
        rhos = [from_bloch([np.sin(a), 0, np.cos(a)]) for a in (0, bt, -bt)]
        P_sdp.append(sdp_unterscheidung(rhos, [1 / 3] * 3))
        P_pgm.append(pgm(rhos, [1 / 3] * 3))
    P_sdp, P_pgm = np.array(P_sdp), np.array(P_pgm)
    k120 = np.argmin(abs(np.degrees(beta) - 120))
    print(f"Trine (β = 120°): SDP {P_sdp[k120]:.4f}, PGM {P_pgm[k120]:.4f}, erwartet 2/3")
    print("PGM ≥ SDP² überall:", np.all(P_pgm >= P_sdp ** 2 - 1e-6))

    # ein unsymmetrischer Fall: drei zufällige gemischte Zustände mit ungleichen Priors
    rhos = [from_bloch(v / np.linalg.norm(v) * rng.uniform(0.5, 1)) for v in rng.normal(size=(3, 3))]
    ps = [0.5, 0.3, 0.2]
    print(f"Zufällige gemischte Zustände, Priors {ps}: SDP {sdp_unterscheidung(rhos, ps):.4f}, PGM {pgm(rhos, ps):.4f}")

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(np.degrees(beta), P_sdp, "o-", ms=4, label="beste Messung (SDP)")
    ax.plot(np.degrees(beta), P_pgm, "s-", ms=4, label="Pretty-Good-Measurement")
    ax.plot(np.degrees(beta), P_sdp ** 2, ":", color="0.4", label="Barnum–Knill-Schranke P_opt²")
    ax.axhline(1 / 3, color="0.6", ls="--", label="Raten: 1/3")
    ax.axvline(120, color="0.8", lw=6, alpha=0.6, label="Trine")
    ax.set_xlabel("Winkel β zwischen den Bloch-Vektoren [Grad]")
    ax.set_ylabel("Erfolgswahrscheinlichkeit")
    ax.set_title("Drei reine Qubit-Zustände bei 0 und ±β unterscheiden")
    ax.legend()
    plt.show()


def uncertainty():
    """11. Unschärfe und gemeinsame Messbarkeit (Zellen 18 von quantummeasurement.ipynb)."""
    global HX, HZ, ax, axes, bild, eta, farbe, fig, gemischt, lam_min, links, name
    global produkt, punkte, px, pz, r, rein, robertson, t, theta, v, x, y
    global z
    fig, axes = plt.subplots(1, 3, figsize=(17, 4.8))

    # (a) reine Zustände auf dem Großkreis in der x-z-Ebene
    theta = np.linspace(0, 2 * np.pi, 400)
    HX, HZ, produkt, robertson = [], [], [], []
    for t in theta:
        r = from_bloch([np.sin(t), 0, np.cos(t)])
        px, pz = np.trace(r @ (I2 + X) / 2).real, np.trace(r @ (I2 + Z) / 2).real
        HX.append(shannon([px, 1 - px])); HZ.append(shannon([pz, 1 - pz]))
        x, y, z = bloch(r)
        produkt.append(np.sqrt((1 - x ** 2) * (1 - z ** 2))); robertson.append(abs(y))
    ax = axes[0]
    ax.plot(np.degrees(theta), np.array(HX) + np.array(HZ), label="H(X) + H(Z) [Bit]")
    ax.axhline(1, color="tab:blue", ls="--", label="Maassen–Uffink: 1 Bit")
    ax.plot(np.degrees(theta), produkt, color="tab:green", label="ΔX·ΔZ")
    ax.plot(np.degrees(theta), robertson, color="tab:green", ls="--", label="Robertson: |⟨Y⟩| = 0")
    ax.set_xlabel("Bloch-Winkel θ in der x-z-Ebene [Grad]")
    ax.set_ylabel("Wert")
    ax.set_title("Reine Zustände in der x-z-Ebene")
    ax.legend(fontsize=9, loc="center right")

    # (b) zufällige Zustände: linke Seite gegen rechte Seite der Relationen
    v = rng.normal(size=(1500, 3)); v /= np.linalg.norm(v, axis=1, keepdims=True)
    rein = v                                                     # auf der Kugel
    gemischt = v * rng.uniform(0, 1, (1500, 1)) ** (1 / 3)      # gleichverteilt in der Kugel
    ax = axes[1]
    for punkte, name, farbe in [(gemischt, "gemischt", "tab:orange"), (rein, "rein", "tab:blue")]:
        x, y, z = punkte.T
        links = (1 - x ** 2) * (1 - z ** 2)                      # (ΔX)²(ΔZ)²
        ax.plot(x ** 2 * z ** 2 + y ** 2, links, ".", ms=2, color=farbe, label=f"Schrödinger, {name}")
    x, y, z = gemischt.T
    ax.plot(y ** 2, (1 - x ** 2) * (1 - z ** 2), ".", ms=2, color="0.6", label="Robertson, gemischt")
    ax.plot([0, 1], [0, 1], "k--", lw=1, label="Gleichheit")
    ax.set_xlabel("rechte Seite (Schranke)")
    ax.set_ylabel("(ΔX)²·(ΔZ)²")
    ax.set_title("Robertson und Schrödinger für σ_x und σ_z")
    ax.legend(fontsize=9, markerscale=4)

    # (c) gemeinsame Messbarkeit: kleinster Eigenwert von G_ab = (I + a η_x σ_x + b η_z σ_z)/4
    eta = np.linspace(0, 1, 201)
    lam_min = np.array([[min(np.linalg.eigvalsh((I2 + a * ex * X + bb * ez * Z) / 4).min()
                             for a in (1, -1) for bb in (1, -1)) for ex in eta] for ez in eta])
    ax = axes[2]
    bild = ax.pcolormesh(eta, eta, lam_min, cmap="RdBu", vmin=-0.11, vmax=0.11, shading="auto")
    ax.contour(eta, eta, lam_min, levels=[0], colors="k")
    ax.plot(np.cos(np.linspace(0, np.pi / 2, 100)), np.sin(np.linspace(0, np.pi / 2, 100)), "y--", label="η_x² + η_z² = 1")
    plt.colorbar(bild, ax=ax, label="kleinster Eigenwert von G_ab")
    ax.set_aspect("equal")
    ax.set_xlabel("Schärfe η_x"); ax.set_ylabel("Schärfe η_z")
    ax.set_title("Gemeinsame Messbarkeit (blau: G ist ein POVM)")
    ax.legend(loc="lower left")
    plt.tight_layout()
    plt.show()
    print(f"Minimum von H(X) + H(Z) auf dem Kreis: {min(np.array(HX) + np.array(HZ)):.4f} Bit")


def weak_value():
    """12. Schwache Messung und Weak Value (Zellen 21 von quantummeasurement.ipynb)."""
    global A_w, _, ax, axes, dichte, dq, eps, farbe, fig, g, g_werte, n_post
    global p_post, phi0, psi_f, psi_i, q, sigma, verschiebung, zeiger_nach_postselektion
    eps = 0.1
    psi_i = np.array([1, 1]) / np.sqrt(2)                                   # |+x>
    psi_f = np.array([np.cos(np.pi / 4 - eps), -np.sin(np.pi / 4 - eps)])   # fast orthogonal zu |+x>
    A_w = (psi_f.conj() @ Z @ psi_i) / (psi_f.conj() @ psi_i)
    print(f"Weak Value A_w = {A_w.real:.3f} (cot ε = {1 / np.tan(eps):.3f}), "
          f"Wahrscheinlichkeit der Postselektion {abs(psi_f.conj() @ psi_i) ** 2:.4f}")

    sigma = 1.0
    q = np.linspace(-40, 40, 16001)
    dq = q[1] - q[0]
    phi0 = lambda x: (2 * np.pi * sigma ** 2) ** -0.25 * np.exp(-x ** 2 / (4 * sigma ** 2))


    def zeiger_nach_postselektion(g):
        """Exakte Zeigerverteilung nach U = exp(−i g σ_z ⊗ p) und Postselektion auf psi_f (nicht nur erste Ordnung)."""
        amp = psi_f.conj()[0] * psi_i[0] * phi0(q - g) + psi_f.conj()[1] * psi_i[1] * phi0(q + g)
        dichte = np.abs(amp) ** 2
        p_post = dichte.sum() * dq
        return dichte / p_post, p_post


    fig, axes = plt.subplots(1, 2, figsize=(15, 4.8))
    ax = axes[0]
    ax.plot(q, phi0(q) ** 2, "k--", label="Zeiger vorher")
    for g, farbe in [(0.05, "tab:blue"), (3.0, "tab:red")]:
        dichte, p_post = zeiger_nach_postselektion(g)
        ax.plot(q, dichte, color=farbe, label=f"g/σ = {g:g}, postselektiert (Mittel {np.sum(q * dichte) * dq:.2f}σ)")
    ax.set_xlim(-6, 6)
    ax.set_xlabel("Zeigerposition q [σ]"); ax.set_ylabel("Wahrscheinlichkeitsdichte [1/σ]")
    ax.set_title("Zeigerverteilung nach Postselektion")
    ax.legend(fontsize=9)

    g_werte = np.logspace(-2.5, 1, 60)
    verschiebung = []
    for g in g_werte:
        dichte, _ = zeiger_nach_postselektion(g)
        verschiebung.append(np.sum(q * dichte) * dq / g)                    # mittlere Verschiebung in Einheiten von g
    ax = axes[1]
    ax.plot(g_werte, verschiebung, label="exakte mittlere Verschiebung / g")
    ax.axhline(A_w.real, color="tab:green", ls="--", label=f"Re A_w = {A_w.real:.2f}")
    ax.axhspan(-1, 1, color="0.85", label="Spektrum von σ_z: [−1, 1]")
    ax.set_xscale("log")
    ax.set_xlabel("Kopplung g/σ"); ax.set_ylabel("⟨q⟩ / g")
    ax.set_title("Vom Weak Value (schwach) zu den Eigenwerten (stark)")
    ax.legend()
    plt.tight_layout()
    plt.show()

    # Wie viele Läufe braucht man, um die Verschiebung 0.5σ bei g = 0.05 mit 5 Standardabweichungen zu sehen?
    n_post = (5 * sigma / (0.05 * A_w.real)) ** 2
    print(f"nötig: etwa {n_post:.0f} postselektierte Läufe, also etwa {n_post / abs(psi_f.conj() @ psi_i) ** 2:.0f} Läufe insgesamt")


def continuous():
    """13. Kontinuierliche Messung: der Kollaps als Zufallsweg (Zellen 24 von quantummeasurement.ipynb)."""
    global L, T, _, axes, dt, fig, j, k, kappa, n_traj, oben, rho
    global t, x, z, z0
    kappa, dt, T, n_traj = 1.0, 0.002, 4.0, 1000
    z0 = 0.4
    rho = np.repeat(dm([np.sqrt((1 + z0) / 2), np.sqrt((1 - z0) / 2)])[None], n_traj, axis=0)
    L = np.sqrt(kappa) * Z
    t = np.arange(int(T / dt) + 1) * dt
    z = np.empty((len(t), n_traj)); x = np.empty_like(z)
    z[0], x[0] = z0, np.sqrt(1 - z0 ** 2)
    for k in range(1, len(t)):
        rho, _ = sme_step(rho, 0 * I2, L, dt)
        z[k] = np.real(rho[:, 0, 0] - rho[:, 1, 1])
        x[k] = 2 * np.real(rho[:, 0, 1])

    oben = z[-1] > 0
    print(f"Anteil der Läufe bei z = +1: {oben.mean():.3f} (Born: {(1 + z0) / 2:.2f}); "
          f"|z| > 0.99 am Ende: {np.mean(abs(z[-1]) > 0.99):.3f}")

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.6))
    for j in range(14):
        axes[0].plot(t, z[:, j], lw=0.9, color="tab:blue" if oben[j] else "tab:red")
    axes[0].set_xlabel("Zeit t [1/κ]"); axes[0].set_ylabel("z = ⟨σ_z⟩")
    axes[0].set_title("14 Trajektorien (blau: enden bei +1)")

    axes[1].hist(z[-1], bins=40, range=(-1, 1), color="0.5")
    axes[1].set_xlabel("z am Ende (t = 4/κ)"); axes[1].set_ylabel("Anzahl Läufe")
    axes[1].set_title(f"Endwerte von {n_traj} Läufen: {oben.mean():.1%} bei +1")

    axes[2].plot(t, z.mean(axis=1), label="Mittel von z")
    axes[2].axhline(z0, color="tab:blue", ls="--", label="z₀ (Martingal)")
    axes[2].plot(t, x.mean(axis=1), label="Mittel von x")
    axes[2].plot(t, x[0, 0] * np.exp(-2 * kappa * t), "--", color="tab:orange", label="x₀·e^(−2κt) (Lindblad)")
    axes[2].set_xlabel("Zeit t [1/κ]"); axes[2].set_ylabel("Mittelwert über alle Läufe")
    axes[2].set_title("Ensemblemittel: Dephasierung, z bleibt erhalten")
    axes[2].legend()
    plt.tight_layout()
    plt.show()


def trajectories():
    """14. Eine Mastergleichung, zwei Arten von Trajektorien (Zellen 27 von quantummeasurement.ipynb)."""
    global Pe_homodyn, Pe_sprung, T, _, ax, axes, dt, fig, gamma, j, k, klick
    global n_traj, psi, psi_start, rho, sm, t
    gamma, dt, T, n_traj = 1.0, 0.002, 5.0, 2000
    sm = np.array([[0, 1], [0, 0]], dtype=complex)            # σ₋ = |0><1|: |1> (angeregt) → |0> (Grundzustand)
    t = np.arange(int(T / dt) + 1) * dt
    psi_start = np.array([1, 1]) / np.sqrt(2)

    # Photodetektion (Monte-Carlo-Wellenfunktion): Klick mit Wahrscheinlichkeit γ·dt·P_e, dann ψ → |0>;
    # ohne Klick ψ → (I − ½γ dt σ₊σ₋)ψ, normiert: Das Ausbleiben des Klicks verschiebt den Zustand Richtung |0>
    psi = np.repeat(psi_start[None], n_traj, axis=0).astype(complex)
    Pe_sprung = np.empty((len(t), n_traj)); Pe_sprung[0] = 0.5
    for k in range(1, len(t)):
        klick = rng.random(n_traj) < gamma * dt * np.abs(psi[:, 1]) ** 2
        psi[:, 1] *= 1 - 0.5 * gamma * dt
        psi[klick] = [1, 0]
        psi /= np.linalg.norm(psi, axis=1, keepdims=True)
        Pe_sprung[k] = np.abs(psi[:, 1]) ** 2

    # Homodyn-Detektion: diffusive stochastische Mastergleichung mit L = √γ σ₋
    rho = np.repeat(dm(psi_start)[None], n_traj, axis=0)
    Pe_homodyn = np.empty((len(t), n_traj)); Pe_homodyn[0] = 0.5
    for k in range(1, len(t)):
        rho, _ = sme_step(rho, 0 * I2, np.sqrt(gamma) * sm, dt)
        Pe_homodyn[k] = rho[:, 1, 1].real

    print(f"Anteil der Läufe mit Klick bis t = {T:g}/γ: {np.mean(Pe_sprung[-1] < 1e-9):.3f} "
          f"(erwartet ½(1 − e^(−γT)) = {0.5 * (1 - np.exp(-gamma * T)):.3f})")

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.6))
    for j in range(10):
        axes[0].plot(t, Pe_sprung[:, j], lw=1)
        axes[1].plot(t, Pe_homodyn[:, j], lw=0.8)
    axes[0].set_title("Photodetektion: Sprünge nach einem Klick")
    axes[1].set_title("Homodyn-Detektion: Diffusion")
    for ax in axes[:2]:
        ax.set_xlabel("Zeit t [1/γ]"); ax.set_ylabel("angeregte Besetzung P_e")
    axes[2].plot(t, Pe_sprung.mean(axis=1), label="Mittel Photodetektion")
    axes[2].plot(t, Pe_homodyn.mean(axis=1), label="Mittel Homodyn")
    axes[2].plot(t, 0.5 * np.exp(-gamma * t), "k--", label="Lindblad: ½·e^(−γt)")
    axes[2].plot(t, np.exp(-gamma * t) / (1 + np.exp(-gamma * t)), ":", color="tab:blue", label="ohne Klick: e^(−γt)/(1+e^(−γt))")
    axes[2].set_xlabel("Zeit t [1/γ]"); axes[2].set_ylabel("P_e")
    axes[2].set_title("Beide Entfaltungen ergeben dieselbe Mastergleichung")
    axes[2].legend()
    plt.tight_layout()
    plt.show()


def zeno():
    """15. Quanten-Zeno-Effekt (Zellen 30 von quantummeasurement.ipynb)."""
    global Lv, N, N_werte, Omega, T, U_rabi, _, axes, dt, fig, k, kappa
    global kurve, kurven, linie, p0, p_formel, p_sim, rho, rho0, seite, spruenge, t, t_traj
    global z_traj, zz
    Omega = 1.0
    U_rabi = lambda tau: expm(-1j * Omega * tau / 2 * X)

    # (a) N projektive Messungen von σ_z während der Zeit T = π/Ω (ohne Messung: vollständige Umkehr nach |1>)
    T = np.pi / Omega
    N_werte = np.arange(1, 41)
    p_sim = []
    for N in N_werte:
        p0 = abs((U_rabi(T / N) @ [1, 0])[0]) ** 2          # pro Intervall: Wahrscheinlichkeit, in |0> zu bleiben
        p_sim.append(np.mean(np.all(rng.random((4000, N)) < p0, axis=1)))   # alle N Messungen ergeben |0>
    p_formel = np.cos(np.pi / (2 * N_werte)) ** (2 * N_werte)

    # (b) kontinuierliche Messung: Lindblad-Gleichung mit H = (Ω/2)σ_x und L = √κ σ_z
    t = np.linspace(0, 40, 400)
    kurven = {}
    for kappa in [0.0, 1.0, 4.0, 16.0]:
        Lv = liouvillian(Omega / 2 * X, [np.sqrt(kappa) * Z])
        rho0 = dm([1, 0]).flatten(order="F")
        kurven[kappa] = [np.real((expm(Lv * tt) @ rho0).reshape(2, 2, order="F")[0, 0]) for tt in t]

    # (c) eine Trajektorie bei starker Messung, κ = 16Ω
    kappa, dt = 16.0, 0.001
    t_traj = np.arange(int(300 / dt) + 1) * dt
    rho = dm([1, 0])[None]
    z_traj = np.empty(len(t_traj)); z_traj[0] = 1
    for k in range(1, len(t_traj)):
        rho, _ = sme_step(rho, Omega / 2 * X, np.sqrt(kappa) * Z, dt)
        z_traj[k] = np.real(rho[0, 0, 0] - rho[0, 1, 1])
    # Sprünge mit Hysterese zählen: von z > 0.9 nach z < −0.9 oder umgekehrt (kurze Ausreißer zählen nicht)
    spruenge, seite = 0, 1
    for zz in z_traj:
        if seite * zz < -0.9:
            spruenge, seite = spruenge + 1, -seite

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.6))
    axes[0].plot(N_werte, p_formel, "k-", label="cos^(2N)(π/2N)")
    axes[0].plot(N_werte, p_sim, "o", ms=4, label="Simulation, 4000 Läufe")
    axes[0].plot(N_werte, np.exp(-np.pi ** 2 / (4 * N_werte)), "--", label="Näherung exp(−π²/4N)")
    axes[0].set_xlabel("Anzahl N der Messungen in der Zeit π/Ω"); axes[0].set_ylabel("P(immer |0>)")
    axes[0].set_title("Diskrete Messungen"); axes[0].legend()
    for kappa, kurve in kurven.items():
        linie, = axes[1].plot(t, kurve, label=f"κ = {kappa:g} Ω")
        if kappa >= 4:
            axes[1].plot(t, 0.5 * (1 + np.exp(-Omega ** 2 * t / (2 * kappa))), "--", color=linie.get_color())
    axes[1].set_xlabel("Zeit t [1/Ω]"); axes[1].set_ylabel("P(|0>), Mittel über Läufe")
    axes[1].set_title("Kontinuierliche Messung (gestrichelt: Rate Ω²/2κ)"); axes[1].legend()
    axes[2].plot(t_traj, z_traj, lw=0.6)
    axes[2].set_xlabel("Zeit t [1/Ω]"); axes[2].set_ylabel("z = ⟨σ_z⟩")
    axes[2].set_title(f"Eine Trajektorie bei κ = 16Ω: {spruenge} Sprünge")
    plt.tight_layout()
    plt.show()
    print(f"Sprünge in t = 300/Ω: {spruenge}; erwartet im Mittel 300·Ω²/(4κ) = {300 * Omega ** 2 / (4 * 16):.1f} "
          "(Sprungrate in jede Richtung Ω²/4κ, Anzahl Poisson-verteilt)")


def feedback():
    """16. Feedback: den Zufall des Kollapses beseitigen (Zellen 33 von quantummeasurement.ipynb)."""
    global H, L, T, _, a, anteil, axes, dt, fig, j, k, kappa
    global l, lam, lambdas, n_traj, p, rho, schritte, t, theorie, x, z_spur
    kappa, dt, T, n_traj = 1.0, 0.002, 12.0, 400
    lambdas = np.array([0, 0.5, 1, 2, 3, 4, 6, 8])                 # in Einheiten von κ
    lam = np.repeat(lambdas, n_traj)                               # alle Werte in einem Durchlauf
    rho = np.repeat(dm([1, 1])[None], len(lam), axis=0)
    L = np.sqrt(kappa) * Z
    schritte = int(T / dt)
    z_spur = np.empty((schritte + 1, len(lam))); z_spur[0] = 0
    for k in range(1, schritte + 1):
        x = 2 * np.real(rho[:, 0, 1])                              # Schätzung ⟨σ_x⟩ aus dem Quantenfilter
        H = 0.5 * (-lam * x)[:, None, None] * Y                    # H_fb = (u/2) σ_y mit u = −λ⟨σ_x⟩
        rho, _ = sme_step(rho, H, L, dt)
        z_spur[k] = np.real(rho[:, 0, 0] - rho[:, 1, 1])
    anteil = (z_spur[-1] > 0).reshape(len(lambdas), n_traj).mean(axis=1)

    a = np.linspace(0, 0.999, 300)
    theorie = 1 - betainc(1 + a, 1 - a, 0.5)                       # Skalenfunktion (Experiment 10, Fachbegriffe)
    for l, p in zip(lambdas, anteil):
        print(f"λ = {l:g}κ: Anteil bei +1 = {p:.3f}")

    t = np.arange(schritte + 1) * dt
    fig, axes = plt.subplots(1, 2, figsize=(15, 4.6))
    for j in range(12):
        axes[0].plot(t, z_spur[:, j], color="tab:red", lw=0.8, label="ohne Rückkopplung" if j == 0 else None)
        axes[0].plot(t, z_spur[:, 6 * n_traj + j], color="tab:blue", lw=0.8, label="λ = 6κ" if j == 0 else None)
    axes[0].set_xlim(0, 3)
    axes[0].set_xlabel("Zeit t [1/κ]"); axes[0].set_ylabel("z = ⟨σ_z⟩")
    axes[0].set_title("Trajektorien mit und ohne Rückkopplung"); axes[0].legend()
    axes[1].plot(lambdas, anteil, "o", label=f"Simulation ({n_traj} Läufe, t = {T:g}/κ)")
    axes[1].plot(4 * a, theorie, "k-", label="Theorie (Skalenfunktion)")
    axes[1].plot([4, 8], [1, 1], "k-")
    axes[1].axvline(4, color="0.6", ls="--", label="Schwelle λ = 4κ")
    axes[1].set_xlabel("Rückkopplungsstärke λ [κ]"); axes[1].set_ylabel("Anteil der Läufe bei z = +1")
    axes[1].set_title("Deterministischer Kollaps durch Feedback"); axes[1].legend()
    plt.tight_layout()
    plt.show()


def state_tomography():
    """17. Zustandstomographie: lineare Inversion gegen Maximum-Likelihood (Zellen 36 von quantummeasurement.ipynb)."""
    global N, N_werte, _, axes, basen, bell, ergebnisse, f, fehler_li, fehler_mle, fig, fl
    global fm, lineare_inversion, messdaten, mle, neg, proj, r_li, rho_wahr, unphysikalisch, wdh
    bell = np.array([1, 0, 0, 1]) / np.sqrt(2)
    rho_wahr = 0.95 * dm(bell) + 0.05 * np.eye(4) / 4

    basen = list(itertools.product("XYZ", repeat=2))              # 9 Einstellungen
    ergebnisse = list(itertools.product([1, -1], repeat=2))        # 4 Ergebnisse je Einstellung
    proj = np.array([[np.kron((I2 + s1 * PAULI[a]) / 2, (I2 + s2 * PAULI[c]) / 2) for s1, s2 in ergebnisse]
                     for a, c in basen])                           # Form (9, 4, 4, 4)


    def messdaten(rho, N):
        """N Messungen pro Einstellung; Häufigkeiten f[Einstellung, Ergebnis]."""
        p = np.clip(np.real(np.einsum("soij,ji->so", proj, rho)), 0, None)
        return np.array([rng.multinomial(N, ps / ps.sum()) for ps in p]) / N


    def lineare_inversion(f):
        """ρ = ¼ Σ_P <P> P; jeder Erwartungswert aus allen Einstellungen, die zu P passen (I passt zu jeder Basis)."""
        rho = np.zeros((4, 4), dtype=complex)
        for P1, P2 in itertools.product("IXYZ", repeat=2):
            werte = []
            for s, (a, c) in enumerate(basen):
                if P1 in ("I", a) and P2 in ("I", c):
                    vorzeichen = [(s1 if P1 != "I" else 1) * (s2 if P2 != "I" else 1) for s1, s2 in ergebnisse]
                    werte.append(f[s] @ vorzeichen)
            rho += np.mean(werte) * np.kron(PAULI[P1], PAULI[P2]) / 4
        return rho


    def mle(f, schritte=400):
        """Maximum-Likelihood mit der RρR-Iteration von Hradil."""
        rho = np.eye(4, dtype=complex) / 4
        for _ in range(schritte):
            p = np.real(np.einsum("soij,ji->so", proj, rho))
            R = np.einsum("so,soij->ij", f / np.maximum(p, 1e-12), proj)
            rho = R @ rho @ R
            rho /= np.trace(rho).real
        return rho


    N_werte = [10, 30, 100, 300, 1000, 3000, 10000]
    wdh = 20
    fehler_li, fehler_mle, unphysikalisch = [], [], []
    for N in N_werte:
        fl, fm, neg = [], [], 0
        for _ in range(wdh):
            f = messdaten(rho_wahr, N)
            r_li = lineare_inversion(f)
            fl.append(trace_distance(r_li, rho_wahr))
            fm.append(trace_distance(mle(f), rho_wahr))
            neg += np.linalg.eigvalsh(r_li).min() < 0
        fehler_li.append(np.mean(fl)); fehler_mle.append(np.mean(fm)); unphysikalisch.append(neg / wdh)
        print(f"N = {N:5d}: Spurabstand LI {np.mean(fl):.4f}, MLE {np.mean(fm):.4f}, LI unphysikalisch in {neg}/{wdh} Fällen")

    fig, axes = plt.subplots(1, 2, figsize=(15, 4.6))
    axes[0].loglog(N_werte, fehler_li, "o-", label="lineare Inversion")
    axes[0].loglog(N_werte, fehler_mle, "s-", label="Maximum-Likelihood")
    axes[0].loglog(N_werte, fehler_li[0] * np.sqrt(N_werte[0] / np.array(N_werte)), "k--", label="∝ 1/√N")
    axes[0].set_xlabel("Messungen pro Pauli-Basis N"); axes[0].set_ylabel("mittlerer Spurabstand zum wahren Zustand")
    axes[0].set_title(f"Fehler der Tomographie (Mittel über {wdh} Wiederholungen)"); axes[0].legend()
    axes[1].semilogx(N_werte, unphysikalisch, "o-", color="tab:red")
    axes[1].set_xlabel("Messungen pro Pauli-Basis N"); axes[1].set_ylabel("Anteil mit negativem Eigenwert")
    axes[1].set_title("Lineare Inversion: unphysikalische Schätzungen")
    plt.tight_layout()
    plt.show()


def process_tomography():
    """18. Prozesstomographie der Amplitudendämpfung (Zellen 39 von quantummeasurement.ipynb)."""
    global E_ad, K_ad, R, R_est, R_spam, R_wahr, ax, axes, bild, fig, gamma, i_
    global j_, kanal, paulis, prozesstomographie, ptm, qubit_tomographie, titel
    gamma = 0.3
    K_ad = [np.array([[1, 0], [0, np.sqrt(1 - gamma)]], dtype=complex), np.array([[0, np.sqrt(gamma)], [0, 0]], dtype=complex)]
    kanal = lambda rho, K: sum(k @ rho @ k.conj().T for k in K)
    paulis = [I2, X, Y, Z]


    def ptm(E):
        """Pauli-Transfermatrix R_ij = ½ Tr(P_i E(P_j)) eines linearen Qubit-Kanals E."""
        return np.array([[0.5 * np.trace(Pi @ E(Pj)).real for Pj in paulis] for Pi in paulis])


    def qubit_tomographie(rho, N, flip=0.0):
        """Bloch-Vektor aus je N Messungen in X, Y, Z; flip = Wahrscheinlichkeit, ein Ergebnis falsch auszulesen."""
        r = []
        for P in (X, Y, Z):
            p_plus = np.clip(np.trace(rho @ (I2 + P) / 2).real, 0, 1)
            p_plus = (1 - flip) * p_plus + flip * (1 - p_plus)
            r.append(2 * rng.binomial(N, p_plus) / N - 1)
        return from_bloch(r)


    def prozesstomographie(E, N, prep_fehler=0.0, flip=0.0):
        """Eingänge |0>, |1>, |+>, |+i> (bei Präparationsfehler zum Teil depolarisiert); Linearität ergibt E(P_j)."""
        eingang = {k: (1 - prep_fehler) * dm(v) + prep_fehler * I2 / 2
                   for k, v in {"0": [1, 0], "1": [0, 1], "+": [1, 1], "+i": [1, 1j]}.items()}
        aus = {k: qubit_tomographie(E(r), N, flip) for k, r in eingang.items()}
        bild = {"I": aus["0"] + aus["1"], "Z": aus["0"] - aus["1"]}
        bild["X"] = 2 * aus["+"] - bild["I"]
        bild["Y"] = 2 * aus["+i"] - bild["I"]
        return np.array([[0.5 * np.trace(Pi @ bild[j]).real for j in "IXYZ"] for Pi in paulis])


    E_ad = lambda rho: kanal(rho, K_ad)
    R_wahr = ptm(E_ad)
    R_est = prozesstomographie(E_ad, 10_000)
    R_spam = prozesstomographie(E_ad, 10_000, prep_fehler=0.04, flip=0.03)
    print("wahre PTM:\n", np.round(R_wahr, 3))
    print(f"größte Abweichung: ohne SPAM {np.abs(R_est - R_wahr).max():.3f}, mit SPAM-Fehlern {np.abs(R_spam - R_wahr).max():.3f}")

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.8))
    for ax, R, titel in [(axes[0], R_wahr, "wahr: Amplitudendämpfung γ = 0.3"),
                         (axes[1], R_est, "rekonstruiert, 10⁴ Messungen pro Basis"),
                         (axes[2], R_spam, "rekonstruiert, mit 4 % Präparations- und 3 % Auslesefehler")]:
        bild = ax.imshow(R, cmap="RdBu", vmin=-1, vmax=1)
        for i_ in range(4):
            for j_ in range(4):
                ax.text(j_, i_, f"{R[i_, j_]:.2f}", ha="center", va="center", fontsize=10)
        ax.set_xticks(range(4)); ax.set_xticklabels(list("IXYZ")); ax.set_yticks(range(4)); ax.set_yticklabels(list("IXYZ"))
        ax.set_xlabel("Eingang P_j"); ax.set_ylabel("Ausgang P_i")
        ax.set_title(titel, fontsize=10)
    plt.colorbar(bild, ax=axes, shrink=0.8, label="R_ij")
    plt.show()


def benchmarking():
    """19. Randomized Benchmarking (Zellen 42 von quantummeasurement.ipynb)."""
    global A, B, E_auslese, F, F_pro, F_schuss, G, H_gate, K_amp, K_dep, K_rausch, S_gate
    global U, V, ax, cliffords, fig, folgen, g_ad, kov, m_werte, mm, modell, neu
    global ohne_phase, p_dep, p_fit, r_rb, r_unsicher, r_wahr, rand, rho_prep, ueberleben
    # Die 24 Clifford-Gatter eines Qubits: alle Produkte aus H und S, bis auf eine globale Phase
    H_gate = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
    S_gate = np.diag([1, 1j])


    def ohne_phase(U):
        k = np.argmax(np.abs(U.ravel()) > 1e-9)                    # erstes Element ≠ 0 reell positiv machen
        return U * np.exp(-1j * np.angle(U.ravel()[k]))


    cliffords, rand = [I2], [I2]
    while rand:
        neu = []
        for U in rand:
            for G in (H_gate, S_gate):
                V = ohne_phase(G @ U)
                if not any(np.allclose(V, W) for W in cliffords):
                    cliffords.append(V); neu.append(V)
        rand = neu
    print("Anzahl Clifford-Gatter:", len(cliffords))

    # Rauschen nach jedem Gatter: Depolarisation, dann Amplitudendämpfung (Kraus-Operatoren der Verkettung)
    p_dep, g_ad = 0.004, 0.006
    K_dep = [np.sqrt(1 - 3 * p_dep / 4) * I2] + [np.sqrt(p_dep / 4) * P for P in (X, Y, Z)]
    K_amp = [np.array([[1, 0], [0, np.sqrt(1 - g_ad)]], dtype=complex), np.array([[0, np.sqrt(g_ad)], [0, 0]], dtype=complex)]
    K_rausch = [a @ c for a in K_amp for c in K_dep]
    F_pro = sum(abs(np.trace(K)) ** 2 for K in K_rausch) / 4      # Prozess-Fidelity
    r_wahr = 1 - (2 * F_pro + 1) / 3                              # 1 − mittlere Fidelity

    rho_prep = 0.97 * dm([1, 0]) + 0.03 * dm([0, 1])             # Präparationsfehler
    E_auslese = np.diag([0.98, 0.05])                            # P(„0“ | |0>) = 0.98, P(„0“ | |1>) = 0.05


    def ueberleben(m):
        """Überlebenswahrscheinlichkeit einer zufälligen Folge aus m Cliffords plus Inversem."""
        rho, U_ges = rho_prep, I2
        for C in [cliffords[k] for k in rng.integers(0, 24, m)] + [None]:
            G = U_ges.conj().T if C is None else C                 # zum Schluss das Inverse der ganzen Folge
            rho = kanal(G @ rho @ G.conj().T, K_rausch)
            U_ges = G @ U_ges
        return np.trace(E_auslese @ rho).real


    m_werte = np.array([1, 5, 10, 20, 40, 70, 100, 150, 200, 300, 400])
    folgen = 50
    F = np.array([[ueberleben(m) for _ in range(folgen)] for m in m_werte])
    F_schuss = rng.binomial(2000, F) / 2000                        # 2000 Wiederholungen je Folge
    modell = lambda m, A, p, B: A * p ** m + B
    (A, p_fit, B), kov = curve_fit(modell, np.repeat(m_werte, folgen), F_schuss.ravel(), p0=(0.5, 0.99, 0.5))
    r_rb, r_unsicher = (1 - p_fit) / 2, np.sqrt(kov[1, 1]) / 2
    print(f"Fit: A = {A:.3f}, p = {p_fit:.5f}, B = {B:.3f}")
    print(f"Fehlerrate pro Gatter: RB {r_rb:.5f} ± {r_unsicher:.5f} (Fit-Unsicherheit), wahr {r_wahr:.5f}")

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(np.repeat(m_werte, folgen), F_schuss.ravel(), ".", color="0.75", ms=3, label="einzelne Folgen (2000 Schüsse)")
    ax.errorbar(m_werte, F_schuss.mean(axis=1), F_schuss.std(axis=1), fmt="o", capsize=3, label="Mittel ± Streuung")
    mm = np.linspace(0, 400, 200)
    ax.plot(mm, modell(mm, A, p_fit, B), "k-", label=f"Fit A·p^m + B, r = {r_rb:.4f} (wahr {r_wahr:.4f})")
    ax.set_xlabel("Länge m der Clifford-Folge"); ax.set_ylabel("Überlebenswahrscheinlichkeit")
    ax.set_title("Randomized Benchmarking eines Qubits"); ax.legend()
    plt.show()


def shadows():
    """20. Classical Shadows (Zellen 45 von quantummeasurement.ipynb)."""
    global N_werte, U_basis, _, abw, ax, basen, beobachtungen, bits, einstellungen, exakt, fehler, fig
    global ghz, k, linie, n, name, p_einst, pauli, pauli_name, s, schaetzwerte, schnappschuesse, w
    global wdh
    n = 6
    ghz = np.zeros(2 ** n, dtype=complex); ghz[[0, -1]] = 1 / np.sqrt(2)
    U_basis = {0: H_gate, 1: H_gate @ S_gate.conj().T, 2: I2}      # Drehung, nach der in Z gemessen wird: X, Y, Z
    pauli_name = {0: "X", 1: "Y", 2: "Z"}

    # Wahrscheinlichkeiten der Ergebnisse für alle 3^6 = 729 Basiseinstellungen, einmal vorberechnet
    einstellungen = list(itertools.product(range(3), repeat=n))
    p_einst = np.array([np.abs(functools.reduce(np.kron, [U_basis[k] for k in e]) @ ghz) ** 2 for e in einstellungen])
    bits = (np.arange(2 ** n)[:, None] >> np.arange(n - 1, -1, -1)) & 1     # Bit von Qubit 0 zuerst


    def schnappschuesse(N):
        """N Schnappschüsse: zufällige Basis pro Qubit (0 = X, 1 = Y, 2 = Z) und Ergebnis ±1."""
        code_ = rng.integers(0, 3 ** n, N)
        basen = np.array(einstellungen)[code_]
        ergebnis = np.empty(N, dtype=int)
        for c in np.unique(code_):
            idx = np.where(code_ == c)[0]
            ergebnis[idx] = rng.choice(2 ** n, size=len(idx), p=p_einst[c] / p_einst[c].sum())
        return basen, 1 - 2 * bits[ergebnis]


    def schaetzwerte(basen, s, pauli):
        """Schätzwert pro Schnappschuss: 3^k Π s_i, falls alle Basen zu pauli passen, sonst 0."""
        w = np.ones(len(basen))
        for qb, b in pauli.items():
            w = w * 3 * (basen[:, qb] == b) * s[:, qb]
        return w


    def exakt(pauli):
        P = functools.reduce(np.kron, [PAULI[pauli_name[pauli[qb]]] if qb in pauli else I2 for qb in range(n)])
        return np.real(ghz.conj() @ P @ ghz)


    beobachtungen = {"Z₀ (k = 1)": {0: 2}, "Z₀Z₁ (k = 2)": {0: 2, 1: 2},
                     "Z₀Z₁Z₂Z₃ (k = 4)": {q_: 2 for q_ in range(4)}, "X^⊗6 (k = 6)": {q_: 0 for q_ in range(6)}}
    N_werte = np.array([100, 300, 1000, 3000, 10000, 30000])
    wdh = 40
    fehler = {name: np.zeros(len(N_werte)) for name in beobachtungen}
    for _ in range(wdh):
        basen, s = schnappschuesse(N_werte[-1])
        for name, pauli in beobachtungen.items():
            w = schaetzwerte(basen, s, pauli)
            fehler[name] += (np.array([w[:N].mean() for N in N_werte]) - exakt(pauli)) ** 2 / wdh

    fig, ax = plt.subplots(figsize=(9, 4.8))
    for name, pauli in beobachtungen.items():
        k = len(pauli)
        linie, = ax.loglog(N_werte, np.sqrt(fehler[name]), "o", label=f"{name}, exakt {exakt(pauli):+.0f}")
        ax.loglog(N_werte, np.sqrt((3 ** k - exakt(pauli) ** 2) / N_werte), "--", color=linie.get_color())
    ax.set_xlabel("Anzahl N der Schnappschüsse"); ax.set_ylabel(f"RMS-Fehler ({wdh} Wiederholungen)")
    ax.set_title(f"Classical Shadows, GHZ mit 6 Qubits (gestrichelt: √((3^k − ⟨P⟩²)/N))")
    ax.legend()
    plt.show()

    # Ein einziger Datensatz für alle 135 zwei-lokalen Pauli-Observablen zugleich
    basen, s = schnappschuesse(30000)
    abw = [abs(schaetzwerte(basen, s, {q1: b1, q2: b2}).mean() - exakt({q1: b1, q2: b2}))
           for q1, q2 in itertools.combinations(range(n), 2) for b1 in range(3) for b2 in range(3)]
    print(f"Aus 30 000 Schnappschüssen: größter Fehler über alle {len(abw)} zwei-lokalen Pauli-Strings {max(abw):.3f}, "
          f"mittlerer {np.mean(abw):.3f}")
