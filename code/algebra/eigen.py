"""Eigenwerte und Eigenvektoren: Potenzen, lineare Differentialgleichungen, Schwingungen, Hauptkomponenten, Gershgorin, Störungstheorie, Jacobi, Potenzmethode, QR, Lanczos, Empfindlichkeit und Eigenwerte auf dem Quantencomputer (Hadamard-Test, QPE, HHL, VQE).

Für algebra.ipynb aus eigenvalues.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: see_eigenvectors, powers, linear_odes, vibrations, principal_components, trace_det, gershgorin, off_diagonal, jacobi_method, power_method, qr_algorithm, lanczos_method, sensitivity, quantum_measurement, hadamard_test, qpe, hhl_solver, vqe.
"""
import sys
import time
from itertools import permutations
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Circle, Ellipse, Polygon
from scipy.integrate import solve_ivp
from scipy.linalg import expm, hessenberg
from scipy.optimize import minimize
from scipy.signal import find_peaks
import scipy.sparse as sps
import scipy.sparse.linalg as spsl


def see_eigenvectors():
    """33. Eigenvektoren sehen (Zellen 4, 6 von eigenvalues.ipynb)."""
    global A, HADAMARD, M, PAULI_I, PAULI_X, PAULI_Y, PAULI_Z, ax, axes, bild, dreh, drehung
    global e, ev, ew, fig, k, kreis, lam, lanczos, load_digits, matrizen1, mit_spektrum, name
    global nebendiagonal_norm, np, operator_kette, p, phasenschaetzung, phasenschaetzung_rueckwaerts, plt, qpe_verteilung, r, richtung, ritz_werte, rng
    global schoen, scipy, sp, spalte, t_start, teile, th, theta, v, x0, zahl, zufalls_orthogonal
    global zufalls_unitaer
    # numpy, scipy, matplotlib, sympy und scikit-learn (nur für den Ziffern-Datensatz in Experiment 5) sind in Colab
    # vorinstalliert; installiert wird nichts.
    try:
        import numpy as np
        import scipy
        import sympy as sp
        import matplotlib.pyplot as plt
        from sklearn.datasets import load_digits
    except ImportError as e:
        raise ImportError(f"{e.name} fehlt; bitte lokal selbst installieren, am besten mit conda (conda-forge)") from None


    rng = np.random.default_rng(2026)
    t_start = time.time()

    PAULI_I = np.eye(2, dtype=complex)
    PAULI_X = np.array([[0, 1], [1, 0]], dtype=complex)
    PAULI_Y = np.array([[0, -1j], [1j, 0]])
    PAULI_Z = np.array([[1, 0], [0, -1]], dtype=complex)
    HADAMARD = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)


    def zufalls_orthogonal(n, rng):
        """Haar-verteilte orthogonale Matrix (QR einer Gauß-Matrix, Vorzeichen der Diagonale von R korrigiert)."""
        Q, R = np.linalg.qr(rng.standard_normal((n, n)))
        return Q * np.sign(np.diag(R))


    def zufalls_unitaer(n, rng):
        """Haar-verteilte unitäre Matrix."""
        Q, R = np.linalg.qr((rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))) / np.sqrt(2))
        return Q * (np.diag(R) / np.abs(np.diag(R)))


    def mit_spektrum(eigenwerte, rng):
        """Symmetrische Matrix Q diag(λ) Qᵀ mit vorgegebenen Eigenwerten und zufälligen Eigenvektoren."""
        Q = zufalls_orthogonal(len(eigenwerte), rng)
        return (Q * np.asarray(eigenwerte, dtype=float)) @ Q.T


    def nebendiagonal_norm(A):
        """off(A): Wurzel aus der Quadratsumme aller Einträge außerhalb der Diagonale."""
        return np.linalg.norm(A - np.diag(np.diag(A)))


    def zahl(z, stellen=3):
        """Komplexe Zahl kurz und lesbar: 0.45 + 0.78i, reelle ohne Imaginärteil."""
        z = complex(z)
        if abs(z.imag) < 1e-12:
            return f"{z.real:.{stellen}g}"
        return f"{z.real:.{stellen}g} {'+' if z.imag > 0 else '−'} {abs(z.imag):.{stellen}g}i"


    def operator_kette(ops, n, sparse=False):
        """Tensorprodukt über n Qubits; ops ist ein dict {Platz: 2×2-Matrix}, an den übrigen Plätzen steht die Eins."""
        out = sps.identity(1, dtype=complex, format="csr") if sparse else np.ones((1, 1), dtype=complex)
        for i in range(n):
            m = ops.get(i, PAULI_I)
            out = sps.kron(out, sps.csr_matrix(m), format="csr") if sparse else np.kron(out, m)
        return out


    def lanczos(matvec, v0, m):
        """m Schritte Lanczos mit vollständiger Reorthogonalisierung. Rückgabe: Diagonale α und Nebendiagonale β der
    Tridiagonalmatrix T_m; ihre Eigenwerte sind die Ritz-Werte."""
        V = np.zeros((m, len(v0)), dtype=v0.dtype)
        alpha, beta = np.zeros(m), np.zeros(m - 1)
        v = v0 / np.linalg.norm(v0)
        for j in range(m):
            V[j] = v
            w = matvec(v)
            alpha[j] = np.real(np.vdot(v, w))
            for _ in range(2):                                   # Gram–Schmidt gegen alle bisherigen Vektoren, zweimal
                w = w - V[:j + 1].T @ (V[:j + 1].conj() @ w)
            if j < m - 1:
                beta[j] = np.linalg.norm(w)
                v = w / beta[j]
        return alpha, beta


    def ritz_werte(alpha, beta):
        """Eigenwerte der Tridiagonalmatrix mit Diagonale α und Nebendiagonale β."""
        return np.linalg.eigvalsh(np.diag(alpha) + np.diag(beta, 1) + np.diag(beta, -1))


    def qpe_verteilung(phi, t):
        """Verteilung der Registerwerte j = 0 … 2^t − 1 der Phasenschätzung für einen Eigenzustand mit der Phase φ
    (U|u⟩ = e^(2πiφ)|u⟩): Amplitude (1/T) Σ_k e^(2πik(φ − j/T)), T = 2^t."""
        T = 2**t
        return np.abs(np.fft.fft(np.exp(2j * np.pi * phi * np.arange(T))) / T)**2


    def phasenschaetzung(U, psi, t):
        """Lehrbuch-Phasenschätzung als Zustandsvektor: Register aus t Qubits (T = 2^t Werte), System im Zustand ψ.
    Nach den Hadamard-Gattern und den kontrollierten U^(2^i) steht Σ_k |k⟩ U^k|ψ⟩/√T im Speicher, danach kommt die
    inverse QFT. Rückgabe: Feld der Form (T, d); Zeile j ist der (nicht normierte) Systemzustand zum Registerwert j,
    der die Phase j/T anzeigt."""
        T = 2**t
        zustand = np.empty((T, len(psi)), dtype=complex)
        v = np.asarray(psi, dtype=complex) / np.sqrt(T)
        for k in range(T):
            zustand[k] = v
            v = U @ v
        return np.fft.fft(zustand, axis=0) / np.sqrt(T)          # inverse QFT: |k⟩ → Σ_j e^(−2πi jk/T)|j⟩/√T


    def phasenschaetzung_rueckwaerts(zustand, U):
        """Die Umkehrung (QFT, kontrollierte U^(−k), Hadamard-Gatter). Rückgabe: der Systemzustand, der danach zum
    Register |0…0⟩ gehört."""
        T, d = zustand.shape
        z = np.fft.ifft(zustand, axis=0) * np.sqrt(T)
        v, W, Uinv = np.zeros(d, dtype=complex), np.eye(d, dtype=complex), U.conj().T
        for k in range(T):
            v += W @ z[k]
            W = Uinv @ W
        return v / np.sqrt(T)

    lam = sp.symbols("lambda")
    drehung = sp.Rational(9, 10) * sp.Matrix([[sp.cos(sp.pi / 3), -sp.sin(sp.pi / 3)], [sp.sin(sp.pi / 3), sp.cos(sp.pi / 3)]])
    matrizen1 = {
        "symmetrisch": sp.Matrix([[2, 1], [1, 2]]),
        "nicht symmetrisch": sp.Matrix([[1, sp.Rational(3, 2)], [0, 2]]),
        "Scherung": sp.Matrix([[1, 1], [0, 1]]),
        "Drehstreckung (60°, Faktor 0.9)": drehung,
    }
    for name, M in matrizen1.items():
        p = sp.expand((M - lam * sp.eye(2)).det())
        schoen = lambda e: str(e).replace("lambda", "λ").replace("**", "^").replace("*", "·").replace("I", "i")
        teile = [f"λ = {schoen(sp.nsimplify(w))} (algebraisch {a}, geometrisch {len(v)}, "
                 f"Eigenvektor ({', '.join(schoen(sp.simplify(c)) for c in v[0])}))" for w, a, v in M.eigenvects()]
        print(f"{name}: det(A − λI) = {schoen(p)}\n    " + "\n    ".join(teile))

    fig, axes = plt.subplots(2, 4, figsize=(18, 8.5), gridspec_kw={"height_ratios": [1.25, 1]})
    theta = np.linspace(0, 2 * np.pi, 721)
    kreis = np.array([np.cos(theta), np.sin(theta)])
    for spalte, (name, M) in enumerate(matrizen1.items()):
        A = np.array(M.evalf(), dtype=float)
        ax = axes[0, spalte]
        bild = A @ kreis
        ax.plot(*kreis, color="0.6", lw=1, label="Einheitskreis: x")
        ax.plot(*bild, color="tab:blue", lw=2, label="Bild: Ax")
        for th in np.linspace(0, 2 * np.pi, 16, endpoint=False):
            x0 = np.array([np.cos(th), np.sin(th)])
            ax.annotate("", A @ x0, x0, arrowprops=dict(arrowstyle="->", color="0.5", lw=0.7))
        ew, ev = np.linalg.eig(A)
        for k in range(2):
            if abs(ew[k].imag) < 1e-12:
                v = np.real(ev[:, k])
                ax.plot([-2.6 * v[0], 2.6 * v[0]], [-2.6 * v[1], 2.6 * v[1]], "--", color="tab:red", lw=1)
                ax.annotate("", ew[k].real * v, (0, 0), arrowprops=dict(arrowstyle="->", color="tab:red", lw=2.5))
        ax.set_xlim(-3, 3); ax.set_ylim(-3, 3); ax.set_aspect("equal")
        ax.set_title(f"{name}\nλ = " + ", ".join(zahl(w) for w in ew))
        ax.set_xlabel("x₁"); ax.set_ylabel("x₂")
        if spalte == 0:
            ax.plot([], [], "--", color="tab:red", label="Eigenrichtung, Pfeil = λv")
            ax.legend(loc="lower right", fontsize=8)
        ax = axes[1, spalte]
        dreh = (np.degrees(np.arctan2(bild[1], bild[0]) - theta) + 180) % 360 - 180
        ax.plot(np.degrees(theta), dreh, color="tab:blue")
        ax.axhline(0, color="k", lw=0.8)
        for k in range(2):
            if abs(ew[k].imag) < 1e-12:
                richtung = np.degrees(np.arctan2(ev[1, k].real, ev[0, k].real)) % 180
                for r in (richtung, richtung + 180):
                    ax.axvline(r, color="tab:red", ls="--", lw=1)
        ax.set_ylim(-185, 185); ax.set_yticks([-180, -90, 0, 90, 180])
        ax.set_xlabel("Richtung θ von x [Grad]"); ax.set_ylabel("Winkel von Ax gegen x [Grad]")
        ax.set_title("Nullstellen = Eigenrichtungen")
    plt.tight_layout()
    plt.show()


def powers():
    """34. Potenzen: wer auf lange Sicht gewinnt (Zellen 9 von eigenvalues.ipynb)."""
    global P, P_google, P_langsam, P_schnell, abstand, axes, besuche, daempfung, ew, ew_l, farbe, fib
    global fig, goldener_schnitt, gueltig, k, k_anker, ketten, kumuliert, l2, links, links_l, n2, name
    global ordnung, p, pi, pi_l, rate, u, zufall, zustand
    fib = sp.Matrix([[1, 1], [1, 0]])
    goldener_schnitt = (1 + sp.sqrt(5)) / 2
    print("Fibonacci: [[1, 1], [1, 0]]^30 =", (fib**30).tolist(), " Eigenwerte", list(fib.eigenvals()))
    print(f"  F_30 = {(fib**30)[0, 1]},  φ^30/√5 = {float(goldener_schnitt**30 / sp.sqrt(5)):.6f}")

    n2 = 6
    P_schnell = rng.random((n2, n2))
    P_schnell /= P_schnell.sum(axis=1, keepdims=True)
    P_langsam = np.zeros((n2, n2))
    P_langsam[:3, :3] = rng.random((3, 3)) + 0.5
    P_langsam[3:, 3:] = rng.random((3, 3)) + 0.5
    P_langsam[0, 4] = P_langsam[2, 3] = P_langsam[3, 1] = P_langsam[5, 2] = 0.04   # schwache Brücken zwischen den Gruppen
    P_langsam /= P_langsam.sum(axis=1, keepdims=True)
    daempfung = 0.85
    P_google = daempfung * P_langsam + (1 - daempfung) / n2                    # PageRank: mit 15 % zufällig springen
    ketten = {"gut gemischt": P_schnell, "zwei Gruppen": P_langsam, "zwei Gruppen + Dämpfung 0.85": P_google}

    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
    for (name, P), farbe in zip(ketten.items(), ["tab:green", "tab:red", "tab:purple"]):
        ew, links = np.linalg.eig(P.T)                                           # linke Eigenvektoren: π P = π
        ordnung = np.argsort(-np.abs(ew))
        ew, links = ew[ordnung], links[:, ordnung]
        pi = np.real(links[:, 0]) / np.real(links[:, 0]).sum()
        p, abstand = np.eye(n2)[0], []
        for k in range(80):
            abstand.append(np.abs(p - pi).sum())
            p = p @ P
        abstand = np.array(abstand)
        l2 = np.abs(ew[1])
        gueltig = np.arange(3, 80)[abstand[3:] > 1e-12]                         # oberhalb der Rundungsgrenze
        rate = np.exp(np.polyfit(gueltig, np.log(abstand[gueltig]), 1)[0])
        print(f"{name}: Eigenwerte " + ", ".join(zahl(w) for w in ew)
              + f"\n    π = {np.round(pi, 4)}, |λ₂| = {l2:.4f}, gemessene Rate von ‖p_k − π‖₁: {rate:.4f};"
              f" Abstand nach 20 Schritten {abstand[20]:.1e}, nach 79 Schritten {abstand[79]:.1e}")
        axes[0].semilogy(abstand, "o", ms=3, color=farbe, label=f"{name}: ‖p_k − π‖₁")
        k_anker = gueltig[len(gueltig) // 2]
        axes[0].semilogy(np.arange(80), abstand[k_anker] * l2**(np.arange(80) - k_anker), "--", color=farbe, lw=1,
                         label=f"∝ |λ₂|^k, |λ₂| = {l2:.3f}")
        axes[1].plot(ew.real, ew.imag, "o", ms=8, color=farbe, label=name)

    # Ergodensatz: die Häufigkeiten einer langen Irrfahrt gegen π
    zustand, besuche = 0, np.zeros(n2)
    kumuliert = np.cumsum(P_langsam, axis=1)
    zufall = rng.random(200_000)
    for u in zufall:
        zustand = min(int(np.searchsorted(kumuliert[zustand], u)), n2 - 1)
        besuche[zustand] += 1
    ew_l, links_l = np.linalg.eig(P_langsam.T)
    pi_l = np.real(links_l[:, np.argmax(np.real(ew_l))]); pi_l /= pi_l.sum()
    print(f"Irrfahrt mit 200 000 Schritten (zwei Gruppen): Häufigkeiten {np.round(besuche / besuche.sum(), 4)}, π = {np.round(pi_l, 4)}")

    axes[0].set_ylim(1e-16, 3); axes[0].set_xlabel("Schritt k"); axes[0].set_ylabel("Abstand zur stationären Verteilung")
    axes[0].set_title("Konvergenz von p_k = p_0 P^k: die Rate ist |λ₂|"); axes[0].legend(fontsize=8)
    axes[1].add_patch(Circle((0, 0), 1, fill=False, color="k", lw=1))
    axes[1].add_patch(Circle((0, 0), daempfung, fill=False, color="tab:purple", ls=":", lw=1))
    axes[1].set_aspect("equal"); axes[1].set_xlim(-1.1, 1.1); axes[1].set_ylim(-1.1, 1.1)
    axes[1].set_xlabel("Re λ"); axes[1].set_ylabel("Im λ"); axes[1].legend(fontsize=8, loc="lower left")
    axes[1].set_title("Eigenwerte der Übergangsmatrizen (Einheitskreis, Kreis 0.85 gepunktet)")
    plt.tight_layout()
    plt.show()


def linear_odes():
    """35. Lineare Differentialgleichungen: Spur und Determinante entscheiden (Zellen 12 von eigenvalues.ipynb)."""
    global A, V, XX, YY, ax, ax0, beispiele3, det, ew, fig, formel, gs
    global j, k, name, s3, tau, text, tr, w, xy
    beispiele3 = {
        "1 stabiler Knoten (Senke)": np.array([[-2.0, 1.0], [0.0, -1.0]]),
        "2 instabiler Knoten (Quelle)": np.array([[2.0, 1.0], [0.0, 1.0]]),
        "3 Sattel": np.array([[1.0, 1.0], [1.0, -1.0]]),
        "4 stabiler Strudel": np.array([[-0.5, -2.0], [2.0, -0.5]]),
        "5 instabiler Strudel": np.array([[0.3, -2.0], [2.0, 0.3]]),
        "6 Zentrum": np.array([[0.0, -2.0], [1.0, 0.0]]),
    }
    fig = plt.figure(figsize=(19, 8.5))
    gs = GridSpec(2, 5, figure=fig, width_ratios=[1.3, 1.3, 1, 1, 1], hspace=0.35)
    ax0 = fig.add_subplot(gs[:, :2])
    tau = np.linspace(-4, 4, 400)
    ax0.plot(tau, tau**2 / 4, color="k", lw=1.5, label="Δ = τ²/4 (doppelter Eigenwert)")
    ax0.axhline(0, color="k", lw=0.8); ax0.axvline(0, color="k", lw=0.8)
    ax0.fill_between(tau, -3, 0, color="tab:orange", alpha=0.12)
    ax0.fill_between(tau, tau**2 / 4, 6, color="tab:blue", alpha=0.08)
    for text, xy in [("Sattel: λ reell, Vorzeichen verschieden", (-3.6, -2.2)), ("stabile Knoten", (-3.6, 1.0)),
                     ("instabile Knoten", (2.2, 1.0)), ("stabile Strudel", (-2.4, 4.8)), ("instabile Strudel", (0.9, 4.8)),
                     ("Zentren auf τ = 0", (0.08, 3.3))]:
        ax0.text(*xy, text, fontsize=9)
    for k, (name, A) in enumerate(beispiele3.items()):
        tr, det = np.trace(A), np.linalg.det(A)
        ew = np.linalg.eigvals(A)
        formel = (tr + np.array([1, -1]) * np.sqrt(complex(tr**2 - 4 * det))) / 2
        print(f"{name}: τ = {tr:+.2f}, Δ = {det:+.2f}, τ² − 4Δ = {tr**2 - 4 * det:+.2f} → λ = " + ", ".join(zahl(z) for z in ew)
              + "; aus τ und Δ: " + ", ".join(zahl(z) for z in formel))
        ax0.plot(tr, det, "o", ms=9, color="tab:red")
        ax0.annotate(name.split()[0], (tr, det), xytext=(6, 4), textcoords="offset points", fontsize=11, color="tab:red")
        ax = fig.add_subplot(gs[k // 3, 2 + k % 3])
        s3 = np.linspace(-2, 2, 41)
        XX, YY = np.meshgrid(s3, s3)
        ax.streamplot(XX, YY, A[0, 0] * XX + A[0, 1] * YY, A[1, 0] * XX + A[1, 1] * YY, density=0.9, color="0.4",
                      linewidth=0.8, arrowsize=0.8)
        w, V = np.linalg.eig(A)
        for j in range(2):
            if abs(w[j].imag) < 1e-12:
                ax.plot([-3 * V[0, j], 3 * V[0, j]], [-3 * V[1, j], 3 * V[1, j]], color="tab:red", lw=2)
        ax.set_xlim(-2, 2); ax.set_ylim(-2, 2); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(f"{name}\nλ = " + ", ".join(zahl(z) for z in w), fontsize=10)
    ax0.set_xlim(-4, 4); ax0.set_ylim(-3, 6)
    ax0.set_xlabel("Spur τ = λ₁ + λ₂"); ax0.set_ylabel("Determinante Δ = λ₁ · λ₂")
    ax0.set_title("Spur-Determinanten-Ebene von ẋ = Ax"); ax0.legend(loc="lower right")
    plt.subplots_adjust(left=0.05, right=0.98, top=0.93, bottom=0.08, wspace=0.25)
    plt.show()


def vibrations():
    """36. Schwingungen: Eigenfrequenzen messen (Zellen 15 von eigenvalues.ipynb)."""
    global K4, N4, T4, _, a, ax, axes, b, c, dt4, fenster, fig
    global gemessen, i, k, loes, moden, nfft, omega_achse, omega_exakt, omega_formel, signal4, spektrum, spitzen
    global t4, w, w2, x0_4
    N4 = 8
    K4 = 2 * np.eye(N4) - np.eye(N4, k=1) - np.eye(N4, k=-1)               # Federkette mit festen Enden, k/m = 1
    w2, moden = np.linalg.eigh(K4)
    omega_exakt = np.sqrt(w2)
    omega_formel = 2 * np.sin(np.arange(1, N4 + 1) * np.pi / (2 * (N4 + 1)))
    print("Eigenfrequenzen ω_k = √λ_k:", np.round(omega_exakt, 5))
    print(f"Formel 2 sin(kπ/18), größte Abweichung {np.max(np.abs(omega_exakt - omega_formel)):.1e}")

    # Die Bewegung wird numerisch integriert, ohne Eigenwerte; die Frequenzen liest man danach aus dem Spektrum ab.
    x0_4 = rng.standard_normal(N4)
    dt4, T4 = 0.1, 600.0
    t4 = np.arange(0, T4, dt4)
    loes = solve_ivp(lambda t, q: np.concatenate([q[N4:], -K4 @ q[:N4]]), (0, T4), np.concatenate([x0_4, np.zeros(N4)]),
                     t_eval=t4, method="DOP853", rtol=1e-10, atol=1e-12)
    signal4 = loes.y[0]                                                       # Auslenkung der ersten Masse
    fenster = np.hanning(len(signal4))
    nfft = 2**18
    spektrum = np.abs(np.fft.rfft(signal4 * fenster, nfft))
    omega_achse = 2 * np.pi * np.fft.rfftfreq(nfft, dt4)
    spitzen, _ = find_peaks(spektrum, height=spektrum.max() * 1e-4, distance=200)
    spitzen = np.sort(spitzen[np.argsort(-spektrum[spitzen])][:N4])
    gemessen = []
    for i in spitzen:                                                         # Parabel durch die drei höchsten Punkte
        a, b, c = np.log(spektrum[i - 1:i + 2])
        gemessen.append(omega_achse[i] + 0.5 * (a - c) / (a - 2 * b + c) * (omega_achse[1] - omega_achse[0]))
    gemessen = np.array(gemessen)
    print("aus dem Spektrum gemessen:      ", np.round(gemessen, 5))
    print(f"größte Abweichung {np.max(np.abs(gemessen - omega_exakt)):.1e}, Auflösung 2π/T = {2 * np.pi / T4:.4f}")
    print("Höhen der Spitzen (relativ zur höchsten):", np.round(spektrum[spitzen] / spektrum.max(), 3))

    fig, axes = plt.subplots(1, 3, figsize=(19, 5.5), gridspec_kw={"width_ratios": [1, 1.3, 1.3]})
    ax = axes[0]
    for k in range(N4):
        ax.plot(np.arange(N4 + 2), np.concatenate([[0], moden[:, k], [0]]) + 1.2 * k, "o-", ms=4)
        ax.text(N4 + 1.3, 1.2 * k, f"ω = {omega_exakt[k]:.3f}", va="center", fontsize=8)
    ax.set_xlim(-0.5, N4 + 3.3); ax.set_xlabel("Masse j (0 und 9 sind die festen Enden)")
    ax.set_ylabel("Eigenvektor v_k (versetzt um 1.2 k)"); ax.set_title("Normalmoden = Eigenvektoren von K")
    ax = axes[1]
    ax.plot(t4[t4 < 120], signal4[t4 < 120], lw=1)
    ax.set_xlabel("Zeit t [√(m/k)]"); ax.set_ylabel("Auslenkung x₁ [Länge]")
    ax.set_title("Bewegung der ersten Masse nach einem zufälligen Anfangsstoß")
    ax = axes[2]
    ax.semilogy(omega_achse, spektrum / spektrum.max(), lw=1, label="|FFT| von x₁(t) mit Hann-Fenster")
    for k, w in enumerate(omega_exakt):
        ax.axvline(w, color="tab:red", ls="--", lw=0.8, label="ω_k = √λ_k(K)" if k == 0 else None)
    ax.set_xlim(0, 2.2); ax.set_ylim(1e-7, 2)
    ax.set_xlabel("Kreisfrequenz ω [√(k/m)]"); ax.set_ylabel("Amplitude (normiert)")
    ax.set_title("Spektrum: die Spitzen liegen bei den Eigenfrequenzen"); ax.legend(loc="lower left", fontsize=8)
    plt.tight_layout()
    plt.show()


def principal_components():
    """37. Daten: Hauptkomponenten sind Eigenvektoren (Zellen 18 von eigenvalues.ipynb)."""
    global C5, Cz, R5, V5, Vz, Xz, anteil, ax, ax2, axes, farbe, fehler
    global fig, h1, h2, i, j, k, kachel, kacheln, l1, l2_, l5, lz
    global montage, rekon, text, v, winkel5, wolke, ziffern
    winkel5 = np.radians(30)
    R5 = np.array([[np.cos(winkel5), -np.sin(winkel5)], [np.sin(winkel5), np.cos(winkel5)]])
    wolke = rng.multivariate_normal([0, 0], R5 @ np.diag([9.0, 1.0]) @ R5.T, size=500)
    C5 = np.cov(wolke.T)
    l5, V5 = np.linalg.eigh(C5)
    print(f"Punktwolke: Kovarianz-Eigenwerte {np.round(l5[::-1], 3)} (wahr 9 und 1), "
          f"Hauptachse bei {np.degrees(np.arctan2(V5[1, 1], V5[0, 1])) % 180:.1f}° (wahr 30°)")

    ziffern = load_digits().data                                              # 1797 Bilder, 8×8 = 64 Pixel, Werte 0…16
    Xz = ziffern - ziffern.mean(axis=0)
    Cz = Xz.T @ Xz / (len(Xz) - 1)
    lz, Vz = np.linalg.eigh(Cz)
    lz, Vz = lz[::-1], Vz[:, ::-1]
    anteil = np.cumsum(lz) / lz.sum()
    print(f"Ziffern: {Xz.shape[0]} Bilder mit {Xz.shape[1]} Pixeln; Spur der Kovarianz = Gesamtvarianz {lz.sum():.1f}")
    for k in [2, 5, 10, 20, 30]:
        rekon = Xz @ Vz[:, :k] @ Vz[:, :k].T
        fehler = np.sum((Xz - rekon)**2) / (len(Xz) - 1)
        print(f"  k = {k:2d}: erklärter Anteil {anteil[k - 1]:.3f}, Rekonstruktionsfehler {fehler:9.4f}, "
              f"Summe der übrigen Eigenwerte {lz[k:].sum():9.4f}")
    print(f"  Pixel, die in allen Bildern gleich sind (Varianz 0): {np.sum(Xz.std(axis=0) == 0)}")
    print(f"  für 90 % der Varianz braucht man {np.searchsorted(anteil, 0.9) + 1} von 64 Komponenten")

    fig, axes = plt.subplots(1, 3, figsize=(19, 5.5), gridspec_kw={"width_ratios": [1, 1.2, 1.4]})
    ax = axes[0]
    ax.plot(*wolke.T, ".", ms=3, color="0.5", alpha=0.6, label="500 Punkte")
    for j, farbe in zip([1, 0], ["tab:red", "tab:blue"]):
        v = V5[:, j] * 2 * np.sqrt(l5[j])
        ax.annotate("", v, (0, 0), arrowprops=dict(arrowstyle="->", color=farbe, lw=2.5))
        ax.plot([], [], color=farbe, lw=2.5, label=f"Eigenvektor, Länge 2√λ, λ = {l5[j]:.2f}")
    ax.add_patch(Ellipse((0, 0), 4 * np.sqrt(l5[1]), 4 * np.sqrt(l5[0]), angle=np.degrees(np.arctan2(V5[1, 1], V5[0, 1])),
                         fill=False, color="k", ls="--", label="2σ-Ellipse"))
    ax.set_aspect("equal"); ax.set_xlim(-9, 9); ax.set_ylim(-7, 7); ax.legend(fontsize=8, loc="lower right")
    ax.set_xlabel("Merkmal 1"); ax.set_ylabel("Merkmal 2"); ax.set_title("Hauptachsen = Eigenvektoren der Kovarianz")
    ax = axes[1]
    ax.semilogy(np.arange(1, 65), lz, "o-", ms=3, label="Eigenwert λ_k (Varianz entlang v_k)")
    ax.set_ylim(1e-2, 300); ax.set_xlabel("Komponente k"); ax.set_ylabel("λ_k [Pixelwert²]")
    ax2 = ax.twinx()
    ax2.plot(np.arange(1, 65), anteil, color="tab:orange", label="kumulierter Anteil Σλ/Spur (rechte Achse)")
    ax2.axhline(0.9, color="tab:orange", ls=":", lw=1)
    ax2.set_ylabel("erklärter Anteil der Varianz"); ax2.set_ylim(0, 1.02)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2_ = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2_, loc="lower left", fontsize=8)
    ax.set_title("Spektrum der Kovarianz der 8×8-Ziffern")
    ax = axes[2]
    kacheln = [ziffern.mean(axis=0).reshape(8, 8) / 8 - 1] + [Vz[:, k].reshape(8, 8) / np.abs(Vz[:, k]).max() for k in range(7)]
    montage = np.full((17, 35), np.nan)
    for i, kachel in enumerate(kacheln):
        montage[9 * (i // 4):9 * (i // 4) + 8, 9 * (i % 4):9 * (i % 4) + 8] = kachel
    ax.imshow(montage, cmap="RdBu_r", vmin=-1, vmax=1)
    for i, text in enumerate(["Mittelwert"] + [f"v_{k + 1}, λ = {lz[k]:.0f}" for k in range(7)]):
        ax.text(9 * (i % 4) + 3.5, 9 * (i // 4) - 0.8, text, ha="center", fontsize=9)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_ylim(16.6, -2)
    ax.set_title("Mittelwert und die ersten sieben Eigenvektoren als Bilder („Eigenziffern“)\nrot positiv, blau negativ")
    plt.tight_layout()
    plt.show()


def trace_det():
    """38. Spur und Determinante: was nicht vom Koordinatensystem abhängt (Zellen 21 von eigenvalues.ipynb)."""
    global A6, A_goe, Ak, B, G6, S, _, ax, axes, catalan, diagonalen, e_k
    global ew6, ew_abw, ew_goe, farbe, fig, i, k, kk, koeff_newton, m, momente_ew, momente_spur
    global n6, p_k, spuren
    A6 = rng.standard_normal((4, 4))
    ew6 = np.linalg.eigvals(A6)
    print("A: Eigenwerte " + ", ".join(zahl(w, 4) for w in ew6) + f"\n   Spur {np.trace(A6):+.6f} = Σλ {np.sum(ew6).real:+.6f}, "
          f"det {np.linalg.det(A6):+.6f} = Πλ {np.prod(ew6).real:+.6f}")
    diagonalen, spuren, ew_abw = [], [], 0.0
    for _ in range(300):
        S = zufalls_orthogonal(4, rng) @ np.diag(np.exp(0.6 * rng.standard_normal(4))) @ zufalls_orthogonal(4, rng)
        B = S @ A6 @ np.linalg.inv(S)                                          # ähnliche Matrix: anderes Koordinatensystem
        diagonalen.append(np.diag(B)); spuren.append(np.trace(B))
        ew_abw = max(ew_abw, np.max(np.abs(np.sort_complex(np.linalg.eigvals(B)) - np.sort_complex(ew6))))
    diagonalen = np.array(diagonalen)
    print(f"300 Ähnlichkeitstransformationen S A S⁻¹: Diagonaleinträge zwischen {diagonalen.min():+.2f} und {diagonalen.max():+.2f},"
          f" Spur schwankt um {np.ptp(spuren):.1e}, Eigenwerte um höchstens {ew_abw:.1e}")

    # Newton-Identitäten: die Koeffizienten des charakteristischen Polynoms aus den Spuren der Potenzen
    p_k = [np.trace(np.linalg.matrix_power(A6, k)) for k in range(1, 5)]
    e_k = [1.0]
    for k in range(1, 5):
        e_k.append(sum((-1)**(i - 1) * e_k[k - i] * p_k[i - 1] for i in range(1, k + 1)) / k)
    koeff_newton = [(-1)**k * e for k, e in enumerate(e_k)]
    print("char. Polynom aus den Spuren tr(A^k):", np.round(koeff_newton, 6))
    print("char. Polynom direkt (np.poly):       ", np.round(np.poly(A6), 6))

    n6 = 400
    G6 = rng.standard_normal((n6, n6))
    A_goe = (G6 + G6.T) / np.sqrt(2 * n6)
    momente_spur, momente_ew = [], []
    ew_goe = np.linalg.eigvalsh(A_goe)
    Ak = np.eye(n6)
    for k in range(1, 11):
        Ak = Ak @ A_goe
        momente_spur.append(np.trace(Ak) / n6)
        momente_ew.append(np.mean(ew_goe**k))
    catalan = [0 if k % 2 else sp.catalan(k // 2) for k in range(1, 11)]
    print("Momente tr(A^k)/n für k = 2, 4, 6, 8, 10:", np.round(momente_spur[1::2], 3), " Catalan-Zahlen:", catalan[1::2])
    print("ungerade Momente k = 1, 3, 5, 7, 9:      ", np.round(momente_spur[0::2], 3))
    print(f"  Abweichung tr(A^k)/n gegen Mittel von λ^k: höchstens {np.max(np.abs(np.array(momente_spur) - momente_ew)):.1e}")

    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
    ax = axes[0]
    for i, farbe in enumerate(["tab:blue", "tab:orange", "tab:green", "tab:purple"]):
        ax.plot(diagonalen[:, i], ".", ms=4, color=farbe, label=f"Diagonaleintrag b_{i + 1}{i + 1}")
    ax.plot(diagonalen.sum(axis=1), "k-", lw=2, label="Summe = Spur")
    ax.axhline(np.sum(ew6).real, color="tab:red", ls="--", label="Σλ")
    ax.set_xlabel("Nummer der Transformation S"); ax.set_ylabel("Wert"); ax.legend(fontsize=8, ncol=2)
    ax.set_title("Die Diagonale hängt vom Koordinatensystem ab, ihre Summe nicht")
    ax = axes[1]
    kk = np.arange(2, 11, 2)
    ax.bar(kk - 0.3, momente_spur[1::2], width=0.6, label="tr(A^k)/n (ohne Eigenwerte gerechnet)")
    ax.bar(kk + 0.3, [float(c) for c in catalan[1::2]], width=0.6, label="Catalan-Zahl C_(k/2) (Halbkreisgesetz)")
    for k, m in zip(kk, momente_spur[1::2]):
        ax.text(k - 0.3, m * 1.15, f"{m:.2f}", ha="center", fontsize=8)
    ax.set_yscale("log"); ax.set_ylim(0.5, 100); ax.set_xticks(kk)
    ax.set_xlabel("Potenz k"); ax.set_ylabel("Spektralmoment"); ax.legend(fontsize=8)
    ax.set_title("Spektralmomente einer GOE-Matrix (n = 400) aus Spuren")
    plt.tight_layout()
    plt.show()


def gershgorin():
    """39. Was die Diagonale über die Eigenwerte verrät: Gershgorin und Schur–Horn (Zellen 24 von eigenvalues.ipynb)."""
    global A7, E7, ax, axes, diag7, drin, e, ebene, ecken, ew7, ew_sh, fig
    global i, innen, mitte, pfade, punkte, radien, schluss
    diag7 = np.array([-6.0, -2.0, 1.0, 4.0, 8.0])
    E7 = np.array([[0.0, 0.5, 0.3, 0.0, 0.2],
                   [0.8, 0.0, 0.6, 0.2, 0.0],
                   [0.2, -0.4, 0.0, 2.0, 0.3],
                   [0.0, 0.3, -2.0, 0.0, 0.5],
                   [0.1, 0.0, 0.4, -0.3, 0.0]])                                # Nebendiagonale; a_34 = −a_43 koppelt 3 und 4 stark
    A7 = np.diag(diag7) + E7
    radien = np.sum(np.abs(E7), axis=1)
    ew7 = np.linalg.eigvals(A7)
    print("Diagonale:", diag7, " Gershgorin-Radien:", np.round(radien, 3))
    print("Eigenwerte:", ", ".join(zahl(w) for w in np.sort_complex(ew7)))
    for i in range(5):
        drin = np.abs(ew7 - diag7[i]) <= radien[i] + 1e-12
        print(f"  Kreis {i + 1} (Mitte {diag7[i]:+.0f}, Radius {radien[i]:.2f}) enthält {drin.sum()} Eigenwert(e)")
    pfade = np.array([np.linalg.eigvals(np.diag(diag7) + s * E7) for s in np.linspace(0, 1, 201)])

    ew_sh = np.array([1.0, 2.0, 4.0])
    punkte = np.array([np.real(np.diag(U @ np.diag(ew_sh) @ U.conj().T)) for U in (zufalls_unitaer(3, rng) for _ in range(6000))])
    schluss = np.sort(punkte, axis=1)[:, ::-1]
    print(f"Schur–Horn: 6000 Diagonalen von UΛU† mit Λ = diag(1, 2, 4): Summe {punkte.sum(1).min():.12f} … {punkte.sum(1).max():.12f};"
          f" größter Eintrag ≤ 4: {np.all(schluss[:, 0] <= 4 + 1e-12)}, Summe der zwei größten ≤ 6: {np.all(schluss[:, :2].sum(1) <= 6 + 1e-12)}")
    ebene = lambda P: np.array([(P[..., 0] - P[..., 1]) / np.sqrt(2), (P[..., 0] + P[..., 1] - 2 * P[..., 2]) / np.sqrt(6)])
    # Dichte: Anteil der Punkte im um die Mitte auf halbe Größe verkleinerten Sechseck (ein Viertel der Fläche)
    mitte = np.array([7 / 3] * 3)
    innen = np.all(np.sort(mitte + 2 * (punkte - mitte), axis=1)[:, ::-1].cumsum(axis=1)[:, :2] <= np.array([4, 6]) + 1e-12, axis=1)
    print(f"  Anteil der Punkte im inneren Sechseck halber Größe (ein Viertel der Fläche): {innen.mean():.3f}")
    ecken = np.array(list(permutations(ew_sh)))
    ecken = ecken[np.argsort(np.arctan2(*ebene(ecken)[::-1]))]

    fig, axes = plt.subplots(1, 2, figsize=(16, 6.5))
    ax = axes[0]
    for i in range(5):
        ax.add_patch(Circle((diag7[i], 0), radien[i], color=f"C{i}", alpha=0.18))
        ax.add_patch(Circle((diag7[i], 0), radien[i], color=f"C{i}", fill=False, lw=1.5))
        ax.plot(diag7[i], 0, "x", color=f"C{i}", ms=10, mew=2)
    ax.plot(pfade.real.ravel(), pfade.imag.ravel(), ".", ms=1, color="0.4")
    ax.plot(ew7.real, ew7.imag, "o", color="k", ms=8, label="Eigenwerte von A")
    ax.plot([], [], "x", color="0.3", ms=8, mew=2, label="Diagonaleinträge a_ii (Kreismitten)")
    ax.plot([], [], ".", color="0.4", label="Wege der Eigenwerte für D + sE, s = 0 … 1")
    ax.set_aspect("equal"); ax.set_xlim(-8, 10); ax.set_ylim(-4, 4); ax.legend(fontsize=8, loc="lower left")
    ax.set_xlabel("Re λ"); ax.set_ylabel("Im λ"); ax.set_title("Gershgorin-Kreise: Mitte a_ii, Radius Σ_{j≠i}|a_ij|")
    ax = axes[1]
    ax.plot(*ebene(punkte), ".", ms=1.5, alpha=0.4, color="tab:blue", label="diag(UΛU†) für 6000 zufällige U")
    ax.add_patch(Polygon(ebene(ecken).T, closed=True, fill=False, color="tab:red", lw=2, label="konvexe Hülle der Permutationen von (1, 2, 4)"))
    for e in ecken:
        ax.annotate(str(tuple(int(v) for v in e)), ebene(e), xytext=(5, 5), textcoords="offset points", fontsize=9)
    ax.plot(*ebene(np.array([7 / 3] * 3)), "k+", ms=12, label="(7/3, 7/3, 7/3): alle Diagonaleinträge gleich")
    ax.set_aspect("equal"); ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    ax.set_xlabel("(d₁ − d₂)/√2"); ax.set_ylabel("(d₁ + d₂ − 2d₃)/√6")
    ax.set_title("Schur–Horn: mögliche Diagonalen bei festen Eigenwerten (Ebene d₁ + d₂ + d₃ = 7)")
    plt.tight_layout()
    plt.show()


def off_diagonal():
    """40. Was die Nebendiagonale bewirkt: Kopplung, vermiedene Kreuzung, Störungstheorie (Zellen 27 von eigenvalues.ipynb)."""
    global D8, W8, _, axes, e, e0, eps8, exakt, f0, f2, farbe, fig
    global g, g0, g_werte, gewicht, gs8, h8, st0, st2, v, v8, w, w_m
    global w_p, werte, zweite
    eps8 = np.linspace(-2, 2, 401)
    gs8 = [0.0, 0.1, 0.3, 0.6]
    fig, axes = plt.subplots(1, 3, figsize=(19, 5.5))
    for g, farbe in zip(gs8, ["k", "tab:blue", "tab:orange", "tab:green"]):
        werte, gewicht = [], []
        for e in eps8:
            w, v = np.linalg.eigh(np.array([[e, g], [g, -e]]))
            werte.append(w); gewicht.append(v[0, 0]**2)
        werte = np.array(werte)
        axes[0].plot(eps8, werte[:, 0], color=farbe, label=f"g = {g}")
        axes[0].plot(eps8, werte[:, 1], color=farbe)
        axes[1].plot(eps8, gewicht, color=farbe, label=f"g = {g}")
        if g > 0:
            print(f"g = {g}: kleinster Abstand der beiden Niveaus {np.min(werte[:, 1] - werte[:, 0]):.4f} (= 2g)")
    # Hellmann–Feynman: dλ/dε = ⟨v|∂H/∂ε|v⟩ = ⟨v|σ_z|v⟩
    e0, g0, h8 = 0.4, 0.3, 1e-6
    w_p = np.linalg.eigvalsh(np.array([[e0 + h8, g0], [g0, -e0 - h8]]))[0]
    w_m = np.linalg.eigvalsh(np.array([[e0 - h8, g0], [g0, -e0 + h8]]))[0]
    _, v8 = np.linalg.eigh(np.array([[e0, g0], [g0, -e0]]))
    print(f"Hellmann–Feynman bei ε = 0.4, g = 0.3: dλ₋/dε = {(w_p - w_m) / (2 * h8):+.8f}, ⟨v₋|σ_z|v₋⟩ = {v8[:, 0] @ np.diag([1, -1]) @ v8[:, 0]:+.8f},"
          f" exakt −ε/√(ε² + g²) = {-e0 / np.hypot(e0, g0):+.8f}")

    # Störungstheorie für eine 6×6-Matrix: Diagonale D plus Kopplung g·W
    D8 = np.array([0.0, 1.0, 2.5, 3.2, 4.5, 6.0])
    W8 = rng.standard_normal((6, 6)); W8 = (W8 + W8.T) / 2; np.fill_diagonal(W8, 0)
    g_werte = np.logspace(-3, -0.5, 26)
    f0, f2 = [], []
    for g in g_werte:
        exakt = np.linalg.eigvalsh(np.diag(D8) + g * W8)
        zweite = D8 + np.array([sum((g * W8[i, j])**2 / (D8[i] - D8[j]) for j in range(6) if j != i) for i in range(6)])
        f0.append(np.max(np.abs(exakt - D8))); f2.append(np.max(np.abs(exakt - np.sort(zweite))))
    st0 = np.polyfit(np.log(g_werte[:15]), np.log(f0[:15]), 1)[0]
    st2 = np.polyfit(np.log(g_werte[:15]), np.log(f2[:15]), 1)[0]
    print(f"6×6: Fehler der Diagonale allein ∝ g^{st0:.2f}, mit zweiter Ordnung Σ|g W_ij|²/(d_i − d_j) ∝ g^{st2:.2f}")
    axes[2].loglog(g_werte, f0, "o-", ms=4, label=f"nur Diagonale: Fehler ∝ g^{st0:.2f}")
    axes[2].loglog(g_werte, f2, "s-", ms=4, label=f"Diagonale + 2. Ordnung: Fehler ∝ g^{st2:.2f}")
    axes[0].set_xlabel("Verstimmung ε (Diagonale ±ε)"); axes[0].set_ylabel("Eigenwerte ±√(ε² + g²)")
    axes[0].set_title("Kopplung g auf der Nebendiagonale: vermiedene Kreuzung"); axes[0].legend()
    axes[1].set_xlabel("Verstimmung ε"); axes[1].set_ylabel("Gewicht von |0⟩ im unteren Eigenvektor")
    axes[1].set_title("Mischung der Eigenvektoren: Breite ≈ g"); axes[1].legend()
    axes[2].set_xlabel("Kopplungsstärke g"); axes[2].set_ylabel("größter Fehler der Eigenwerte")
    axes[2].set_title("Störungstheorie: Diagonale als nullte Näherung"); axes[2].legend()
    plt.tight_layout()
    plt.show()


def jacobi_method():
    """41. Jacobi-Verfahren: die Nebendiagonale wegdrehen (Zellen 30 von eigenvalues.ipynb)."""
    global A9, B9, J, V9, ax, fig, frob, gs9, i, im, jacobi_rotation, n9
    global neben3, p, q, schnapp, sw, sweep, verlauf
    def jacobi_rotation(A, p, q):
        """Eine Jacobi-Drehung in der (p, q)-Ebene, die a_pq zu null macht. Rückgabe: Jᵀ A J und J."""
        if A[p, q] == 0:
            return A, np.eye(len(A))
        tau = (A[q, q] - A[p, p]) / (2 * A[p, q])
        t = np.sign(tau) / (abs(tau) + np.sqrt(1 + tau**2)) if tau != 0 else 1.0
        c = 1 / np.sqrt(1 + t**2); s = t * c
        J = np.eye(len(A)); J[p, p] = J[q, q] = c; J[p, q] = s; J[q, p] = -s
        return J.T @ A @ J, J


    n9 = 8
    A9 = rng.standard_normal((n9, n9)); A9 = (A9 + A9.T) / 2
    B9, V9 = A9.copy(), np.eye(n9)
    verlauf, frob, schnapp = [nebendiagonal_norm(B9)], [np.sum(B9**2)], {0: B9.copy()}
    for sweep in range(1, 7):
        for p in range(n9 - 1):
            for q in range(p + 1, n9):
                B9, J = jacobi_rotation(B9, p, q)
                V9 = V9 @ J
                verlauf.append(nebendiagonal_norm(B9)); frob.append(np.sum(B9**2))
        schnapp[sweep] = B9.copy()
        print(f"nach Sweep {sweep}: off(A) = {verlauf[-1]:.2e}")
    neben3 = np.abs(schnapp[3][~np.eye(n9, dtype=bool)])
    print(f"nach 3 Sweeps liegen die Nebendiagonaleinträge zwischen {neben3.min():.0e} und {neben3.max():.0e}")
    print(f"Frobenius-Norm² bleibt {frob[0]:.6f} (Schwankung {np.ptp(frob):.1e}); am Ende Σ a_ii² = {np.sum(np.diag(B9)**2):.6f}")
    print("Diagonale nach Jacobi (sortiert):", np.round(np.sort(np.diag(B9)), 10))
    print("np.linalg.eigvalsh:              ", np.round(np.linalg.eigvalsh(A9), 10))
    print(f"‖A V − V diag‖ = {np.linalg.norm(A9 @ V9 - V9 @ np.diag(np.diag(B9))):.1e}: die Spalten der aufmultiplizierten Drehungen sind die Eigenvektoren")

    fig = plt.figure(figsize=(19, 5))
    gs9 = GridSpec(1, 4, figure=fig, width_ratios=[1, 1, 1, 1.6])
    for i, sw in enumerate([0, 1, 3]):
        ax = fig.add_subplot(gs9[0, i])
        im = ax.imshow(np.log10(np.abs(schnapp[sw]) + 1e-17), cmap="magma", vmin=-16, vmax=0.5)
        ax.set_title({0: "log₁₀|a_ij| am Anfang", 1: "log₁₀|a_ij| nach 1 Sweep"}.get(sw, f"log₁₀|a_ij| nach {sw} Sweeps"))
        ax.set_xticks([]); ax.set_yticks([])
    fig.colorbar(im, ax=ax, fraction=0.046)
    ax = fig.add_subplot(gs9[0, 3])
    ax.semilogy(verlauf, lw=1.5, label="off(A) nach jeder Drehung")
    for sw in range(1, 7):
        ax.axvline(sw * n9 * (n9 - 1) // 2, color="0.7", lw=0.8, ls=":")
    ax.set_xlabel("Zahl der Jacobi-Drehungen (gepunktet: Ende eines Sweeps mit 28 Drehungen)")
    ax.set_ylabel("off(A) = (Σ_{i≠j} a_ij²)^½"); ax.set_title("Jacobi-Verfahren: die Nebendiagonale verschwindet"); ax.legend()
    plt.tight_layout()
    plt.show()


def power_method():
    """42. Potenzmethode, Rayleigh-Quotient und Rayleigh-Quotienten-Iteration (Zellen 33 von eigenvalues.ipynb)."""
    global A10, A_inv, Q10, art, axes, erst, f_ray, f_vek, farbe, fehler, fig, k
    global n10, name, r, rho, sigma, spektrum10, v1, v1_inv, x, x_start
    n10 = 50
    fig, axes = plt.subplots(1, 2, figsize=(16, 5.5))
    for r, farbe in zip([0.5, 0.9, 0.99], ["tab:green", "tab:blue", "tab:red"]):
        spektrum10 = np.concatenate([[1.0, r], rng.uniform(-0.8 * r, 0.8 * r, n10 - 2)])
        Q10 = zufalls_orthogonal(n10, rng)
        A10 = (Q10 * spektrum10) @ Q10.T
        v1 = Q10[:, 0]
        x = rng.standard_normal(n10)
        f_vek, f_ray = [], []
        for k in range(200):
            x = A10 @ x; x /= np.linalg.norm(x)
            f_vek.append(np.linalg.norm(x - (x @ v1) * v1)); f_ray.append(abs(x @ A10 @ x - 1.0))   # Sinus des Winkels
        f_vek, f_ray = np.maximum(f_vek, 1e-17), np.maximum(f_ray, 1e-17)
        axes[0].semilogy(f_vek, color=farbe, label=f"λ₂/λ₁ = {r}: Winkelfehler sin∠(x_k, v₁)")
        axes[0].semilogy(f_ray, color=farbe, ls="--", label=f"λ₂/λ₁ = {r}: Fehler des Rayleigh-Quotienten")
        erst = lambda f: next((k + 1 for k, w in enumerate(f) if w < 1e-14), None)
        print(f"λ₂/λ₁ = {r}: nach 200 Schritten Winkelfehler {f_vek[-1]:.1e} (r^200 = {r**200:.1e}), "
              f"Rayleigh-Fehler {f_ray[-1]:.1e} (r^400 = {r**400:.1e}); unter 1e-14 nach {erst(f_vek)} bzw. {erst(f_ray)} Schritten")
        if r == 0.9:
            A_inv, v1_inv = A10, v1
    axes[0].set_ylim(1e-17, 3); axes[0].set_xlabel("Iteration k"); axes[0].set_ylabel("Fehler")
    axes[0].set_title("Potenzmethode: Rate λ₂/λ₁, Rayleigh-Quotient doppelt so schnell"); axes[0].legend(fontsize=8)

    x_start = v1_inv + 0.4 * rng.standard_normal(n10) / np.sqrt(n10)
    x_start /= np.linalg.norm(x_start)
    for name, art, farbe in [("inverse Iteration, Shift σ = 1.05", "invers", "tab:purple"), ("Rayleigh-Quotienten-Iteration", "rqi", "tab:orange")]:
        x, fehler = x_start.copy(), []
        for k in range(12):
            rho = x @ A_inv @ x
            fehler.append(abs(rho - 1.0))
            sigma = 1.05 if art == "invers" else rho
            try:
                x = np.linalg.solve(A_inv - sigma * np.eye(n10), x)
            except np.linalg.LinAlgError:
                break
            x /= np.linalg.norm(x)
        fehler = np.maximum(fehler, 1e-17)
        axes[1].semilogy(fehler, "o-", color=farbe, label=name)
        print(f"{name}: |ρ_k − λ₁| = " + ", ".join(f"{f:.0e}" for f in fehler[:7]))
    axes[1].set_ylim(1e-17, 1); axes[1].set_xlabel("Iteration k"); axes[1].set_ylabel("|ρ_k − λ₁|")
    axes[1].set_title("Mit Shift: inverse Iteration (linear) und RQI (kubisch)"); axes[1].legend()
    plt.tight_layout()
    plt.show()


def qr_algorithm():
    """43. QR-Algorithmus: das Standardverfahren (Zellen 36 von eigenvalues.ipynb)."""
    global A11, Ak, Q, R, ax, ew11, fig, g, grenzen, gs11, i, im
    global k, kk, prot11, qr_mit_shift, quot, rate, schnapp11, schritte11, unten, werte11
    ew11 = np.array([8.0, 6.0, 3.0, 2.5, 1.0, 0.5])
    A11 = hessenberg(mit_spektrum(ew11, rng))                                # symmetrisch → tridiagonal
    A11 = np.triu(np.tril(A11, 1), -1)                                        # Rundungsreste außerhalb des Bandes löschen
    Ak, unten, schnapp11 = A11.copy(), [], {0: A11.copy()}
    for k in range(1, 61):
        Q, R = np.linalg.qr(Ak)
        Ak = R @ Q                                                            # A_k = Qᵀ A_(k−1) Q: ähnlich, gleiche Eigenwerte
        unten.append(np.abs(np.diag(Ak, -1)))
        if k in (5, 40):
            schnapp11[k] = Ak.copy()
    unten = np.array(unten)
    quot = ew11[1:] / ew11[:-1]
    for i in range(5):
        rate = np.exp(np.polyfit(np.arange(10, 40), np.log(unten[9:39, i]), 1)[0])
        print(f"|a_({i + 2},{i + 1})|: Rate pro Iteration {rate:.4f}, erwartet λ_{i + 2}/λ_{i + 1} = {quot[i]:.4f}")
    print("Diagonale nach 60 Iterationen:", np.round(np.diag(Ak), 8))


    def qr_mit_shift(A, tol=1e-14):
        """QR-Verfahren mit Wilkinson-Shift und Deflation für symmetrische Tridiagonalmatrizen; zählt die Iterationen
    pro Eigenwert und protokolliert |a_(m,m−1)|."""
        A = A.copy(); n = len(A); werte, schritte, protokoll = [], [], []
        while n > 1:
            it = 0
            while abs(A[n - 1, n - 2]) > tol * (abs(A[n - 1, n - 1]) + abs(A[n - 2, n - 2])):
                a, b, c = A[n - 2, n - 2], A[n - 1, n - 2], A[n - 1, n - 1]
                d = (a - c) / 2
                mu = c - np.sign(d if d != 0 else 1.0) * b**2 / (abs(d) + np.hypot(d, b))
                Q, R = np.linalg.qr(A[:n, :n] - mu * np.eye(n))
                A[:n, :n] = R @ Q + mu * np.eye(n)
                it += 1; protokoll.append(abs(A[n - 1, n - 2]))
            werte.append(A[n - 1, n - 1]); schritte.append(it); n -= 1
        werte.append(A[0, 0])
        return np.array(werte), schritte, protokoll


    werte11, schritte11, prot11 = qr_mit_shift(A11)
    print("|a_(m,m−1)| nach jedem Schritt mit Shift:", ", ".join(f"{w:.0e}" for w in prot11))
    print(f"mit Wilkinson-Shift: Eigenwerte {np.round(np.sort(werte11)[::-1], 12)}, Iterationen pro Eigenwert {schritte11}"
          f" (zusammen {sum(schritte11)})")

    fig = plt.figure(figsize=(19, 5.2))
    gs11 = GridSpec(1, 4, figure=fig, width_ratios=[1, 1, 1.6, 1.3])
    for i, k in enumerate([0, 40]):
        ax = fig.add_subplot(gs11[0, i])
        im = ax.imshow(np.log10(np.abs(schnapp11[k]) + 1e-17), cmap="magma", vmin=-16, vmax=1)
        ax.set_title(f"log₁₀|a_ij| nach {k} QR-Schritten" if k else "log₁₀|a_ij|: tridiagonal (Hessenberg)")
        ax.set_xticks([]); ax.set_yticks([])
    fig.colorbar(im, ax=ax, fraction=0.046)
    ax = fig.add_subplot(gs11[0, 2])
    kk = np.arange(1, 61)
    for i in range(5):
        ax.semilogy(kk, unten[:, i], color=f"C{i}", label=f"|a_({i + 2},{i + 1})|, λ_{i + 2}/λ_{i + 1} = {quot[i]:.3f}")
        ax.semilogy(kk, unten[19, i] * quot[i]**(kk - 20), color=f"C{i}", ls=":", lw=1)
    ax.set_ylim(1e-17, 10); ax.set_xlabel("QR-Iteration k (ohne Shift)"); ax.set_ylabel("Betrag des Nebendiagonaleintrags")
    ax.set_title("Ohne Shift: jeder Eintrag fällt mit (λ_{i+1}/λ_i)^k (gepunktet)"); ax.legend(fontsize=8)
    ax = fig.add_subplot(gs11[0, 3])
    ax.semilogy(np.arange(1, len(prot11) + 1), np.maximum(prot11, 1e-18), "o-", color="tab:red")
    grenzen = np.cumsum(schritte11)
    for g in grenzen[:-1]:
        ax.axvline(g + 0.5, color="0.6", ls=":")
    ax.set_xlabel("QR-Iteration mit Wilkinson-Shift"); ax.set_ylabel("|a_(m,m−1)| der aktiven Zeile")
    ax.set_title("Mit Wilkinson-Shift (gepunktet: Deflation)")
    plt.tight_layout()
    plt.show()


def lanczos_method():
    """44. Lanczos: Eigenwerte riesiger dünnbesetzter Matrizen (Zellen 39 von eigenvalues.ipynb)."""
    global H12, N12, alpha12, ax, axes, beta12, e, f, f_e0, farbe, fig, gesamt
    global j, m, m12, paare, r, ref, ritz, t0_12, verschieden
    N12 = 14
    paare = [(i, (i + 1) % N12) for i in range(N12)]
    H12 = sum(operator_kette({i: P, j: P}, N12, sparse=True) for i, j in paare for P in (PAULI_X, PAULI_Y, PAULI_Z)) / 4
    H12 = sps.csr_matrix(H12.real)                                            # S_i·S_j mit S = σ/2; alle Einträge reell
    print(f"Heisenberg-Ring mit {N12} Spins: Dimension {H12.shape[0]}, {H12.nnz} Einträge ungleich null "
          f"({H12.nnz / H12.shape[0]**2:.1e} der Matrix; dicht wären es {H12.shape[0]**2 * 8 / 1e9:.1f} GB)")
    t0_12 = time.time()
    ref = np.sort(spsl.eigsh(H12, k=8, which="SA", return_eigenvectors=False))
    print(f"scipy eigsh (ARPACK, implizit neugestartetes Lanczos): 8 kleinste Eigenwerte {np.round(ref, 6)} in {time.time() - t0_12:.1f} s")
    print(f"  E₀/N = {ref[0] / N12:.6f}; unendlich lange Kette (Bethe-Ansatz): 1/4 − ln 2 = {0.25 - np.log(2):.6f}")
    m12 = 120
    alpha12, beta12 = lanczos(lambda v: H12 @ v, rng.standard_normal(H12.shape[0]), m12)
    ritz = [ritz_werte(alpha12[:m], beta12[:m - 1]) for m in range(2, m12 + 1)]
    f_e0 = np.array([abs(r[0] - ref[0]) for r in ritz])
    verschieden = ref[np.concatenate([[True], np.diff(ref) > 1e-6])]
    print(f"Lanczos: |Ritz₀ − E₀| = {f_e0[18]:.1e} nach 20, {f_e0[38]:.1e} nach 40, {f_e0[58]:.1e} nach 60 Schritten")
    print(f"  verschiedene Eigenwerte unter den 8 kleinsten: {np.round(verschieden, 6)}")
    for m in (60, m12):
        r = ritz[m - 2]
        print(f"  Ritz-Werte nach {m} Schritten bis {ref[-1]:.4f}: {np.round(r[r < ref[-1] + 1e-6], 6)}")
    gesamt = np.array(spsl.eigsh(H12, k=1, which="LA", return_eigenvectors=False))
    print(f"  größter Eigenwert {gesamt[0]:.6f} (= N/4, alle Spins parallel); Ritz_max nach {m12} Schritten {ritz[-1][-1]:.6f}")

    fig, axes = plt.subplots(1, 2, figsize=(16, 5.5))
    ax = axes[0]
    for m, r in zip(range(2, m12 + 1), ritz):
        ax.plot(np.full(len(r), m), r, "_", color="tab:blue", ms=5)
    for e in verschieden:
        ax.axhline(e, color="tab:red", lw=0.6, ls="--")
    ax.axhline(gesamt[0], color="tab:red", lw=0.6, ls="--")
    ax.set_xlabel("Lanczos-Schritte m (Dimension des Krylov-Raums)"); ax.set_ylabel("Ritz-Werte (Eigenwerte von T_m) [J]")
    ax.set_title("Ritz-Werte: die Ränder des Spektrums konvergieren zuerst (rot: exakt)")
    ax = axes[1]
    for j, farbe in enumerate(["tab:blue", "tab:orange", "tab:green"]):
        e = verschieden[j]
        f = [np.min(np.abs(r - e)) for r in ritz]
        ax.semilogy(range(2, m12 + 1), np.maximum(f, 1e-16), color=farbe, label=f"nächster Ritz-Wert an E = {e:.4f}")
    ax.set_xlabel("Lanczos-Schritte m"); ax.set_ylabel("Abstand zum exakten Eigenwert [J]"); ax.legend(fontsize=8)
    ax.set_title(f"Konvergenz für den Heisenberg-Ring, N = {N12}, Dimension {2**N12}")
    plt.tight_layout()
    plt.show()


def sensitivity():
    """45. Wie empfindlich sind Eigenwerte? (Zellen 42 von eigenvalues.ipynb)."""
    global D13, E, J13, S13, V13, _, a, ax, axes, b, e, eps13
    global eps_werte, f_jor, f_sym, fig, n13, st_j, st_s, verschiebung, wolke_j, wolke_s
    n13 = 8
    S13 = rng.standard_normal((n13, n13)); S13 = (S13 + S13.T) / 2
    J13 = np.eye(n13, k=1)                                                    # Jordan-Block zum Eigenwert 0
    eps13 = 1e-8
    wolke_s, wolke_j = [], []
    for _ in range(300):
        E = rng.standard_normal((n13, n13)); E *= eps13 / np.linalg.norm(E, 2)
        wolke_s.append(np.linalg.eigvalsh(S13 + (E + E.T) / 2) - np.linalg.eigvalsh(S13))
        wolke_j.append(np.linalg.eigvals(J13 + E))
    wolke_s, wolke_j = np.concatenate(wolke_s), np.concatenate(wolke_j)
    print(f"symmetrisch, ‖E‖ = 1e-8: größte Verschiebung eines Eigenwerts {np.max(np.abs(wolke_s)):.1e} (Weyl: ≤ ‖E‖)")
    print(f"Jordan-Block 8×8, ‖E‖ = 1e-8: größte Verschiebung {np.max(np.abs(wolke_j)):.3f}, (1e-8)^(1/8) = {eps13**(1 / 8):.3f}")
    eps_werte = np.logspace(-14, -2, 13)
    f_sym, f_jor = [], []
    for e in eps_werte:
        a, b = [], []
        for _ in range(30):
            E = rng.standard_normal((n13, n13)); E *= e / np.linalg.norm(E, 2)
            a.append(np.max(np.abs(np.linalg.eigvalsh(S13 + (E + E.T) / 2) - np.linalg.eigvalsh(S13))))
            b.append(np.max(np.abs(np.linalg.eigvals(J13 + E))))
        f_sym.append(np.median(a)); f_jor.append(np.median(b))
    st_s = np.polyfit(np.log(eps_werte[2:]), np.log(f_sym[2:]), 1)[0]
    st_j = np.polyfit(np.log(eps_werte), np.log(f_jor), 1)[0]
    print(f"Steigungen: symmetrisch {st_s:.2f}, Jordan-Block {st_j:.3f} (erwartet 1 und 1/8 = 0.125)")
    # Bauer–Fike: |δλ| ≤ κ(V)‖E‖ für diagonalisierbare A = VΛV⁻¹; κ(V) misst, wie schief die Eigenvektoren stehen
    D13 = np.diag(np.arange(1, n13 + 1, dtype=float)) + 3 * np.triu(rng.standard_normal((n13, n13)), 1)
    _, V13 = np.linalg.eig(D13)
    verschiebung = []
    for _ in range(100):
        E = rng.standard_normal((n13, n13)); E *= eps13 / np.linalg.norm(E, 2)
        verschiebung.append(np.max(np.abs(np.sort(np.linalg.eigvals(D13 + E).real) - np.arange(1, n13 + 1))))
    print(f"obere Dreiecksmatrix mit Diagonale 1 … 8: κ(V) = {np.linalg.cond(V13):.1e}; größte Verschiebung bei ‖E‖ = 1e-8: "
          f"{max(verschiebung):.1e}, Schranke κ(V)·‖E‖ = {np.linalg.cond(V13) * eps13:.1e} (symmetrisch: κ(V) = 1)")

    fig, axes = plt.subplots(1, 3, figsize=(19, 5.5))
    ax = axes[0]
    ax.hist(wolke_s / eps13, bins=60, color="tab:blue")
    ax.axvline(-1, color="k", ls="--", label="Weyl-Schranke ±‖E‖"); ax.axvline(1, color="k", ls="--")
    ax.set_xlabel("Verschiebung δλ / ‖E‖"); ax.set_ylabel("Anzahl (300 Störungen × 8 Eigenwerte)")
    ax.set_title("symmetrisch, ‖E‖ = 1e-8: δλ reell und ≤ ‖E‖"); ax.legend(fontsize=8)
    ax = axes[1]
    ax.plot(wolke_j.real, wolke_j.imag, ".", ms=2, color="tab:red")
    ax.add_patch(Circle((0, 0), eps13**(1 / 8), fill=False, color="k", ls="--", label="Radius ε^(1/8) = 0.1"))
    ax.set_aspect("equal"); ax.set_xlim(-0.2, 0.2); ax.set_ylim(-0.2, 0.2); ax.legend(loc="lower right", fontsize=8)
    ax.set_xlabel("Re λ"); ax.set_ylabel("Im λ"); ax.set_title("Jordan-Block 8×8: alle Eigenwerte 0, nach Störung 1e-8")
    ax = axes[2]
    ax.loglog(eps_werte, f_sym, "o-", label=f"symmetrisch: ∝ ε^{st_s:.2f}")
    ax.loglog(eps_werte, f_jor, "s-", label=f"Jordan-Block: ∝ ε^{st_j:.3f}")
    ax.loglog(eps_werte, eps_werte, "k:", lw=1, label="ε")
    ax.set_xlabel("Größe der Störung ε = ‖E‖₂"); ax.set_ylabel("größte Verschiebung (Median über 30 Störungen)")
    ax.set_title("Empfindlichkeit: normal gegen nicht normal"); ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()


def quantum_measurement():
    """46. Quanten: Eigenwerte sind Messwerte (Zellen 45 von eigenvalues.ipynb)."""
    global N14, SX, SZ, V14, a14, ax, daempf, erw_sx, erw_sz, fig, g, gammas
    global gs14, i, im, k, l, p_born, psi14, r, reinheit, rho14, rho_eig, s2
    global schuesse, titel, w, werte14, zaehl
    s2 = 1 / np.sqrt(2)
    SX = np.array([[0, s2, 0], [s2, 0, s2], [0, s2, 0]], dtype=complex)        # Spin 1, ħ = 1
    SZ = np.diag([1.0, 0.0, -1.0]).astype(complex)
    a14, V14 = np.linalg.eigh(SX)                                              # Eigenwerte −1, 0, 1
    psi14 = np.array([0.7, 0.6, 0.2 + 0.3j]); psi14 /= np.linalg.norm(psi14)
    rho14 = np.outer(psi14, psi14.conj())
    rho_eig = V14.conj().T @ rho14 @ V14                                       # ρ in der Eigenbasis von S_x
    p_born = np.real(np.diag(rho_eig))
    a14 = np.round(a14, 12) + 0.0                                              # −0 vermeiden
    print(f"Eigenwerte von S_x: {a14}; Born-Wahrscheinlichkeiten = Diagonale von ρ in der Eigenbasis: {np.round(p_born, 4)}")
    print(f"⟨S_x⟩ = tr(ρ S_x) = {np.real(np.trace(rho14 @ SX)):+.4f} = Σ a_k p_k = {a14 @ p_born:+.4f}")
    N14 = 2000
    schuesse = rng.choice(a14, size=N14, p=p_born)
    werte14, zaehl = np.unique(np.round(schuesse, 9), return_counts=True)
    print(f"{N14} Messungen: nur die Werte {werte14} kommen vor, Häufigkeiten {np.round(zaehl / N14, 4)}; "
          f"Mittelwert {schuesse.mean():+.4f} ± {schuesse.std(ddof=1) / np.sqrt(N14):.4f}")
    gammas = np.linspace(0, 4, 41)
    erw_sx, erw_sz, reinheit = [], [], []
    for g in gammas:
        daempf = np.full((3, 3), np.exp(-g)); np.fill_diagonal(daempf, 1.0)
        r = V14 @ (rho_eig * daempf) @ V14.conj().T                            # Dephasierung in der Eigenbasis von S_x
        erw_sx.append(np.real(np.trace(r @ SX))); erw_sz.append(np.real(np.trace(r @ SZ))); reinheit.append(np.real(np.trace(r @ r)))
    print(f"Dephasierung: ⟨S_x⟩ bleibt {erw_sx[0]:+.4f} … {erw_sx[-1]:+.4f}, ⟨S_z⟩ fällt von {erw_sz[0]:+.4f} auf {erw_sz[-1]:+.4f},"
          f" Reinheit tr ρ² von {reinheit[0]:.4f} auf {reinheit[-1]:.4f} (Σp_k² = {np.sum(p_born**2):.4f})")
    print(f"⟨a_k|S_z|a_k⟩ für die drei Eigenvektoren von S_x: {np.round(np.real(np.diag(V14.conj().T @ SZ @ V14)), 12)}")

    fig = plt.figure(figsize=(19, 5.2))
    gs14 = GridSpec(1, 4, figure=fig, width_ratios=[1, 1, 1.2, 1.4])
    daempf = np.full((3, 3), np.exp(-4.0)); np.fill_diagonal(daempf, 1.0)
    for i, (titel, r) in enumerate([("|ρ_kl| in der Eigenbasis von S_x", rho_eig), ("nach Dephasierung γt = 4", rho_eig * daempf)]):
        ax = fig.add_subplot(gs14[0, i])
        im = ax.imshow(np.abs(r), cmap="viridis", vmin=0, vmax=1)
        for (k, l), w in np.ndenumerate(np.abs(r)):
            ax.text(l, k, f"{w:.3f}", ha="center", va="center", color="w" if w < 0.6 else "k", fontsize=10)
        ax.set_xticks(range(3), [f"a = {int(round(a)):+d}" for a in a14]); ax.set_yticks(range(3), [f"a = {int(round(a)):+d}" for a in a14])
        ax.set_title(titel)
    fig.colorbar(im, ax=ax, fraction=0.046)
    ax = fig.add_subplot(gs14[0, 2])
    ax.bar(werte14 - 0.15, zaehl / N14, width=0.3, label=f"Häufigkeit in {N14} Messungen")
    ax.bar(a14 + 0.15, p_born, width=0.3, label="Born: p_k = ⟨a_k|ρ|a_k⟩")
    ax.set_xticks(a14); ax.set_xlabel("Messwert = Eigenwert von S_x [ħ]"); ax.set_ylabel("Wahrscheinlichkeit")
    ax.set_title("Messung von S_x liefert nur Eigenwerte"); ax.legend(fontsize=8)
    ax = fig.add_subplot(gs14[0, 3])
    ax.plot(gammas, erw_sx, label="⟨S_x⟩ (hängt nur von der Diagonale ab)")
    ax.plot(gammas, erw_sz, label="⟨S_z⟩ (braucht die Nebendiagonale)")
    ax.plot(gammas, reinheit, label="Reinheit tr ρ²")
    ax.set_xlabel("Dephasierung γt"); ax.set_ylabel("Wert [ħ bzw. dimensionslos]")
    ax.set_title("Kohärenzen verschwinden: S_x merkt nichts, S_z schon"); ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()


def hadamard_test():
    """47. Spektroskopie auf dem Quantencomputer: Hadamard-Test und Fourier-Transformation (Zellen 48 von eigenvalues.ipynb)."""
    global CU, E15, H15, K15, S_gate, U_test, V15, _, ax, axes, c15, dim15
    global dt15, fenster15, fig, g_exakt, g_mess, gefunden, im_mess, n15, name, nfft15, omega15, p0
    global psi15, re_mess, schuesse15, sichtbar, spek_exakt, spek_mess, spitzen15, t15, t_test, wert, z
    n15 = 3
    H15 = (-sum(operator_kette({i: PAULI_Z, i + 1: PAULI_Z}, n15) for i in range(n15 - 1))
           - 0.8 * sum(operator_kette({i: PAULI_X}, n15) for i in range(n15)) - 0.3 * operator_kette({0: PAULI_Z}, n15))
    E15, V15 = np.linalg.eigh(H15)
    psi15 = np.zeros(2**n15, dtype=complex); psi15[0] = 1.0                   # |000⟩
    c15 = np.abs(V15.conj().T @ psi15)**2
    print("Eigenwerte von H:", np.round(E15, 4))
    print("Gewichte |⟨E_j|000⟩|²:", np.round(c15, 4))

    # Hadamard-Test, einmal als echte Schaltung: Hilfsqubit |+⟩, kontrolliertes U, H, messen. P(0) = (1 + Re⟨ψ|U|ψ⟩)/2.
    t_test = 0.7
    U_test = expm(-1j * H15 * t_test)
    dim15 = 2**n15
    CU = np.block([[np.eye(dim15), np.zeros((dim15, dim15))], [np.zeros((dim15, dim15)), U_test]])
    for name, S_gate in [("Re", np.eye(2)), ("Im", np.diag([1, -1j]))]:
        z = np.kron(HADAMARD @ np.array([1, 0]), psi15)
        z = CU @ z
        z = np.kron(HADAMARD @ S_gate, np.eye(dim15)) @ z
        p0 = np.sum(np.abs(z[:dim15])**2)
        wert = np.vdot(psi15, U_test @ psi15)
        print(f"Hadamard-Test ({name}) bei t = {t_test}: 2 P(0) − 1 = {2 * p0 - 1:+.6f}, "
              f"{name}⟨ψ|U|ψ⟩ = {(wert.real if name == 'Re' else wert.imag):+.6f}")

    dt15, K15, schuesse15 = 0.25, 256, 400
    t15 = dt15 * np.arange(K15)
    g_exakt = np.array([np.vdot(psi15, V15 @ (np.exp(-1j * E15 * t) * (V15.conj().T @ psi15))) for t in t15])
    re_mess = 2 * rng.binomial(schuesse15, np.clip((1 + g_exakt.real) / 2, 0, 1)) / schuesse15 - 1   # P(0) beim Hadamard-Test
    im_mess = 2 * rng.binomial(schuesse15, np.clip((1 + g_exakt.imag) / 2, 0, 1)) / schuesse15 - 1
    g_mess = re_mess + 1j * im_mess
    print(f"{K15} Zeitpunkte, Δt = {dt15}, je {schuesse15} Schüsse für Re und Im; Messrauschen pro Punkt {np.std(g_mess - g_exakt):.3f}")
    nfft15 = 2**14
    fenster15 = np.hanning(K15)
    omega15 = -2 * np.pi * np.fft.fftshift(np.fft.fftfreq(nfft15, dt15))     # Vorzeichen: g(t) = Σ|c|² e^(−iEt)
    spek_exakt = np.abs(np.fft.fftshift(np.fft.fft(g_exakt * fenster15, nfft15)))
    spek_mess = np.abs(np.fft.fftshift(np.fft.fft(g_mess * fenster15, nfft15)))
    spitzen15, _ = find_peaks(spek_mess, height=0.15 * spek_mess.max())
    gefunden = np.sort(omega15[spitzen15])
    print(f"Auflösung 2π/(K Δt) = {2 * np.pi / (K15 * dt15):.3f}, Nyquist-Grenze ±π/Δt = ±{np.pi / dt15:.2f}")
    print("Spitzen des gemessenen Spektrums bei ω =", np.round(gefunden, 3))
    sichtbar = E15[c15 > 0.05]
    print("Eigenwerte mit Gewicht über 5 %:       ", np.round(np.sort(sichtbar), 3))

    fig, axes = plt.subplots(1, 2, figsize=(17, 5.5))
    ax = axes[0]
    ax.plot(t15, g_exakt.real, color="tab:blue", lw=1.2, label="Re g(t) exakt")
    ax.plot(t15, re_mess, ".", ms=3, color="tab:blue", alpha=0.6, label=f"Re g(t) aus dem Hadamard-Test ({schuesse15} Schüsse)")
    ax.plot(t15, g_exakt.imag, color="tab:orange", lw=1.2, label="Im g(t) exakt")
    ax.set_xlim(0, 30); ax.set_xlabel("Zeit t [ħ/J]"); ax.set_ylabel("g(t) = ⟨ψ|e^(−iHt)|ψ⟩")
    ax.set_title("Autokorrelation des Zustands |000⟩ in der Ising-Kette (3 Qubits)"); ax.legend(fontsize=8, loc="lower right")
    ax = axes[1]
    ax.plot(omega15, spek_mess / spek_mess.max(), color="tab:blue", label="Spektrum aus den gemessenen Daten")
    ax.plot(omega15, spek_exakt / spek_exakt.max(), color="0.5", ls="--", lw=1, label="Spektrum aus exaktem g(t)")
    ax.vlines(E15, 0, c15 / c15.max(), color="tab:red", lw=2.5, label="Eigenwerte E_j, Höhe ∝ |⟨E_j|ψ⟩|²")
    ax.set_xlim(-6, 6); ax.set_xlabel("Energie ω [J]"); ax.set_ylabel("|Fourier-Transformierte| (normiert)")
    ax.set_title("Die Frequenzen von g(t) sind die Eigenwerte"); ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()


def qpe():
    """48. Quantenphasenschätzung (QPE) (Zellen 51 von eigenvalues.ipynb)."""
    global M, Q16, T16, U16, ax, axes, d, f, farbe, fehler_h, fehler_q, fig
    global im, j, j0, k, kosten_h, kosten_q, masse, nach, naechst, p, p16, phasen16
    global phi, phis, psi16, re, st_h, st_q, t, t16, zustand16
    t16 = 5
    T16 = 2**t16
    fig, axes = plt.subplots(1, 3, figsize=(19, 5.5))
    ax = axes[0]
    for phi, farbe in [(10 / T16, "tab:blue"), (10.4 / T16, "tab:orange"), (10.5 / T16, "tab:red")]:
        p = qpe_verteilung(phi, t16)
        ax.plot(np.arange(T16) / T16, p, "o-", ms=4, color=farbe, label=f"φ = {phi * T16:.1f}/32")
        naechst = int(np.round(phi * T16)) % T16
        print(f"φ = {phi * T16:.1f}/32: P(nächster Gitterwert) = {p[naechst]:.4f}, P(einer der zwei nächsten) = "
              f"{np.sort(p)[-2:].sum():.4f}")
    print(f"untere Schranke 4/π² = {4 / np.pi**2:.4f} für den nächsten, 8/π² = {8 / np.pi**2:.4f} für die zwei nächsten")
    ax.set_xlim(0.15, 0.5); ax.set_xlabel("angezeigte Phase j/2^t"); ax.set_ylabel("Wahrscheinlichkeit")
    ax.set_title(f"QPE mit t = {t16} Qubits, Eigenzustand als Eingabe"); ax.legend()

    # Überlagerung zweier Eigenzustände: die Messung des Registers wählt einen aus
    phasen16 = np.array([0.2, 0.65, 0.41, 0.87])
    Q16 = zufalls_unitaer(4, rng)
    U16 = (Q16 * np.exp(2j * np.pi * phasen16)) @ Q16.conj().T
    psi16 = np.sqrt(0.7) * Q16[:, 0] + np.sqrt(0.3) * Q16[:, 1]
    zustand16 = phasenschaetzung(U16, psi16, 7)
    p16 = np.sum(np.abs(zustand16)**2, axis=1)
    ax = axes[1]
    ax.bar(np.arange(128) / 128, p16, width=1 / 128, color="tab:blue")
    for j0, k in [(int(np.argmax(p16[:64])), 0), (64 + int(np.argmax(p16[64:])), 1)]:
        nach = zustand16[j0] / np.linalg.norm(zustand16[j0])
        masse = p16[max(j0 - 3, 0):j0 + 4].sum()
        print(f"Register zeigt {j0}/128 = {j0 / 128:.4f} (Phase {phasen16[k]}): Wahrscheinlichkeit um die Spitze {masse:.3f}"
              f" (|c|² = {[0.7, 0.3][k]}), Überlapp des Systems danach mit dem Eigenvektor {abs(np.vdot(Q16[:, k], nach))**2:.6f}")
    ax.set_xlabel("angezeigte Phase j/2^t"); ax.set_ylabel("Wahrscheinlichkeit")
    ax.set_title("t = 7, Eingabe √0.7|u₁⟩ + √0.3|u₂⟩ (φ₁ = 0.2, φ₂ = 0.65)")

    # Kosten gegen Genauigkeit: Hadamard-Test mit U allein gegen QPE mit U^(2^i)
    ax = axes[2]
    phis = rng.random(300)
    kosten_h, fehler_h, kosten_q, fehler_q = [], [], [], []
    for M in [16, 64, 256, 1024, 4096, 16384, 65536]:
        f = []
        for phi in phis[:100]:
            re = 2 * rng.binomial(M // 2, (1 + np.cos(2 * np.pi * phi)) / 2) / (M // 2) - 1
            im = 2 * rng.binomial(M // 2, (1 + np.sin(2 * np.pi * phi)) / 2) / (M // 2) - 1
            d = (np.arctan2(im, re) / (2 * np.pi) - phi + 0.5) % 1 - 0.5
            f.append(abs(d))
        kosten_h.append(M); fehler_h.append(np.median(f))
    for t in range(3, 15):
        f = []
        for phi in phis:
            j = rng.choice(2**t, p=qpe_verteilung(phi, t))
            f.append(abs((j / 2**t - phi + 0.5) % 1 - 0.5))
        kosten_q.append(2**t - 1); fehler_q.append(np.median(f))
    st_h = np.polyfit(np.log(kosten_h), np.log(fehler_h), 1)[0]
    st_q = np.polyfit(np.log(kosten_q), np.log(fehler_q), 1)[0]
    print(f"Fehler gegen Zahl der Anwendungen von U: Hadamard-Test ∝ M^{st_h:.2f}, QPE ∝ M^{st_q:.2f}")
    print(f"  bei etwa 16 000 Anwendungen: Hadamard-Test {fehler_h[5]:.1e}, QPE (t = 14) {fehler_q[-1]:.1e}")
    ax.loglog(kosten_h, fehler_h, "o-", label=f"Hadamard-Test, M Schüsse: ∝ M^{st_h:.2f}")
    ax.loglog(kosten_q, fehler_q, "s-", label=f"QPE, t Qubits, M = 2^t − 1: ∝ M^{st_q:.2f}")
    ax.set_xlabel("Anwendungen von U (Gesamtzeit)"); ax.set_ylabel("Median des Phasenfehlers |φ̂ − φ|")
    ax.set_title("Standardquantengrenze 1/√M gegen Heisenberg-Grenze 1/M"); ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()


def hhl_solver():
    """49. HHL: lineare Gleichungssysteme über die Eigenwerte (Zellen 54 von eigenvalues.ipynb)."""
    global A, A_dyad, A_pois, A_zuf, C, _, ax, axes, b, b4, b_pois, beta2
    global ergebnis17, ew_pois, faelle, farbe, fig, hhl, m, n_p, name, p, reg, t
    global t0, treue, w, werte, x_exakt, x_klass, xq
    def hhl(A, b, t, t0, C):
        """HHL als Zustandsvektor: QPE mit U = e^(iAt0), Drehung des Hilfsqubits um C/λ̃, QPE rückwärts, Hilfsqubit = 1
    und Register = 0 nachweisen. Rückgabe: normierter Lösungszustand, Erfolgswahrscheinlichkeit, Registerverteilung."""
        T = 2**t
        U = expm(1j * A * t0)
        b = b / np.linalg.norm(b)
        z = phasenschaetzung(U, b, t)
        lam_schaetz = 2 * np.pi * np.arange(T) / (T * t0)                      # Registerwert j → λ̃ = 2πj/(T t0)
        amplitude = np.zeros(T)
        amplitude[1:] = np.minimum(1.0, C / lam_schaetz[1:])                    # Hilfsqubit: |0⟩ → √(1 − (C/λ̃)²)|0⟩ + C/λ̃ |1⟩
        x = phasenschaetzung_rueckwaerts(z * amplitude[:, None], U)
        p_erfolg = np.linalg.norm(x)**2
        return x / np.linalg.norm(x), p_erfolg, np.sum(np.abs(z)**2, axis=1)


    def treue(x_quanten, A, b):
        x = np.linalg.solve(A, b)
        return abs(np.vdot(x / np.linalg.norm(x), x_quanten))**2


    A_dyad = mit_spektrum([1.0, 2.0, 3.0, 4.0], rng)                            # exakt darstellbare Eigenwerte
    A_zuf = mit_spektrum(rng.uniform(1.0, 4.0, 4), rng)
    n_p = 8
    A_pois = 2 * np.eye(n_p) - np.eye(n_p, k=1) - np.eye(n_p, k=-1)           # −u'' auf 8 inneren Punkten (·h²)
    b4 = rng.standard_normal(4)
    b_pois = np.ones(n_p)                                                       # konstante Quelle f = 1
    ew_pois = np.linalg.eigvalsh(A_pois)
    print(f"Poisson: Eigenwerte {np.round(ew_pois, 4)}, Kondition κ = {ew_pois[-1] / ew_pois[0]:.1f}")
    print(f"A (zufällig): Eigenwerte {np.round(np.linalg.eigvalsh(A_zuf), 4)}")
    faelle = {"A mit Eigenwerten 1, 2, 3, 4": (A_dyad, b4, 2 * np.pi / 8, 1.0),
              "A mit zufälligen Eigenwerten in [1, 4]": (A_zuf, b4, 2 * np.pi / 8, 1.0),
              "Poisson-Matrix 8×8 (3 Qubits)": (A_pois, b_pois, np.pi / 4, 0.9 * ew_pois[0])}
    ergebnis17 = {}
    for name, (A, b, t0, C) in faelle.items():
        werte = []
        for t in range(3, 11):
            xq, p, _ = hhl(A, b, t, t0, C)
            werte.append((t, 1 - treue(xq, A, b), p))
        ergebnis17[name] = np.array(werte)
        print(f"{name}: 1 − Treue für t = 3 … 10: " + ", ".join(f"{w[1]:.0e}" for w in werte)
              + f"; Erfolgswahrscheinlichkeit bei t = 10: {werte[-1][2]:.4f}")
        x_klass = np.linalg.solve(A, b / np.linalg.norm(b))
        print(f"    erwartet für ideales HHL: Σ|β_j|²(C/λ_j)² = ‖C A⁻¹ b‖² = {np.linalg.norm(C * x_klass)**2:.4f}")

    fig, axes = plt.subplots(1, 3, figsize=(19, 5.5))
    ax = axes[0]
    _, _, reg = hhl(A_dyad, b4, 5, 2 * np.pi / 8, 1.0)
    beta2 = np.abs(np.linalg.eigh(A_dyad)[1].T @ (b4 / np.linalg.norm(b4)))**2
    ax.bar(2 * np.pi * np.arange(32) / (32 * 2 * np.pi / 8), reg, width=0.2, label="Register nach der QPE (t = 5)")
    ax.plot(np.linalg.eigvalsh(A_dyad), beta2, "rv", ms=9, label="|β_j|² = |⟨u_j|b⟩|² bei λ_j")
    ax.set_xlabel("angezeigter Eigenwert λ̃ = 2πj/(2^t t₀)"); ax.set_ylabel("Wahrscheinlichkeit")
    ax.set_title("Schritt 33 von HHL: QPE schreibt λ_j ins Register"); ax.legend(fontsize=8); ax.set_xlim(-0.2, 8)
    ax = axes[1]
    x_exakt = np.linalg.solve(A_pois, b_pois); x_exakt /= np.linalg.norm(x_exakt)
    for t, m, farbe in [(4, "s", "tab:orange"), (6, "^", "tab:green"), (9, "o", "tab:blue")]:
        xq, p, _ = hhl(A_pois, b_pois, t, np.pi / 4, 0.9 * ew_pois[0])
        xq = xq * np.exp(-1j * np.angle(np.vdot(x_exakt, xq)))
        ax.plot(np.arange(1, n_p + 1), xq.real, m + "--", color=farbe, ms=7, label=f"HHL, t = {t}: Treue {treue(xq, A_pois, b_pois):.4f}")
    ax.plot(np.arange(1, n_p + 1), x_exakt, "k-", lw=2, label="exakt: u(x) ∝ x(1 − x)")
    ax.set_xlabel("Gitterpunkt i"); ax.set_ylabel("Amplitude ⟨i|x⟩"); ax.legend(fontsize=8)
    ax.set_title("Lösung von −u'' = 1 als Quantenzustand")
    ax = axes[2]
    for (name, w), m in zip(ergebnis17.items(), ["o", "s", "^"]):
        ax.semilogy(w[:, 0], np.maximum(w[:, 1], 1e-16), m + "-", label=name)
    ax.set_xlabel("Zahl t der Register-Qubits"); ax.set_ylabel("1 − Treue |⟨x|x̃⟩|²")
    ax.set_title("Genauigkeit von HHL hängt an der Auflösung der QPE"); ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()


def vqe():
    """50. Variational Quantum Eigensolver (VQE) (Zellen 57 von eigenvalues.ipynb)."""
    global E18, H18, H_alle, X_diag, ZZ_diag, a_k, ansatz, ax, axes, c, c_k, delta
    global e_minus, e_plus, energie_exakt, energie_schuesse, farbe, fig, grund, h18, k, lagen18, n18, n_liste
    global name, psi_opt, res, schuss_n, spsa_mess, spsa_wahr, streuung, theta, theta0, u, unter_e1, var_formel
    global verlauf_exakt, werte, xx1, zz1
    n18, h18 = 4, 1.0
    H18 = (-sum(operator_kette({i: PAULI_Z, i + 1: PAULI_Z}, n18) for i in range(n18 - 1))
           - h18 * sum(operator_kette({i: PAULI_X}, n18) for i in range(n18))).real
    E18 = np.linalg.eigvalsh(H18)
    print(f"Ising-Kette mit 4 Spins, h = {h18}: E₀ = {E18[0]:.6f}, E₁ = {E18[1]:.6f}")
    ZZ_diag = np.real(sum(np.diag(operator_kette({i: PAULI_Z, i + 1: PAULI_Z}, n18)) for i in range(n18 - 1)))  # Werte −3, −1, 1, 3
    X_diag = np.real(sum(np.diag(operator_kette({i: PAULI_Z}, n18)) for i in range(n18)))                     # Σ Z nach Basiswechsel H
    H_alle = operator_kette({i: HADAMARD for i in range(n18)}, n18).real
    lagen18 = 3


    def ansatz(theta):
        """RY-Drehungen auf allen Qubits, dann eine CNOT-Leiter, das Ganze 'lagen18'-mal, zum Schluss noch eine RY-Lage."""
        psi = np.zeros(2**n18); psi[0] = 1.0
        theta = theta.reshape(lagen18 + 1, n18)
        for lage in range(lagen18 + 1):
            psi = psi.reshape([2] * n18)
            for q in range(n18):
                c, s = np.cos(theta[lage, q] / 2), np.sin(theta[lage, q] / 2)
                psi = np.moveaxis(np.tensordot(np.array([[c, -s], [s, c]]), np.moveaxis(psi, q, 0), axes=1), 0, q)
            if lage < lagen18:
                for q in range(n18 - 1):                                      # CNOT q → q+1
                    psi = psi.copy()
                    idx = [slice(None)] * n18; idx[q] = 1
                    psi[tuple(idx)] = np.flip(psi[tuple(idx)], axis=q)              # Ziel q+1 ist im Teilfeld Achse q
            psi = psi.reshape(-1)
        return psi


    def energie_exakt(theta):
        psi = ansatz(theta)
        return psi @ H18 @ psi


    def energie_schuesse(theta, n, rng, einzeln=False):
        """⟨H⟩ aus Messungen: n Schüsse in der Z-Basis für Σ Z_i Z_(i+1), n Schüsse nach H^⊗4 für Σ X_i. Jeder Schuss
    liefert einen Eigenwert der gemessenen Pauli-Summe."""
        psi = ansatz(theta)
        zz = ZZ_diag[rng.choice(2**n18, size=n, p=psi**2)]
        xx = X_diag[rng.choice(2**n18, size=n, p=(H_alle @ psi)**2)]
        if einzeln:
            return zz, xx
        return -zz.mean() - h18 * xx.mean()


    theta0 = rng.uniform(-0.1, 0.1, (lagen18 + 1) * n18)
    verlauf_exakt = []
    res = minimize(lambda th: verlauf_exakt.append(energie_exakt(th)) or verlauf_exakt[-1], theta0, method="COBYLA",
                   options={"maxiter": 3000, "rhobeg": 0.5, "tol": 1e-10})
    psi_opt = ansatz(res.x)
    grund = np.linalg.eigh(H18)[1][:, 0]
    print(f"VQE exakt (COBYLA): E = {res.fun:.6f}, Fehler {res.fun - E18[0]:.1e}, Überlapp mit dem Grundzustand "
          f"{abs(grund @ psi_opt)**2:.6f}, {len(verlauf_exakt)} Auswertungen")

    # SPSA mit Messrauschen: pro Schritt zwei Energieschätzungen mit je 1000 Schüssen pro Basis
    theta, schuss_n = theta0.copy(), 1000
    spsa_mess, spsa_wahr = [], []
    for k in range(600):
        a_k, c_k = 0.3 / (k + 1 + 30)**0.602, 0.15 / (k + 1)**0.101
        delta = rng.choice([-1, 1], size=theta.size)
        e_plus = energie_schuesse(theta + c_k * delta, schuss_n, rng)
        e_minus = energie_schuesse(theta - c_k * delta, schuss_n, rng)
        theta = theta - a_k * (e_plus - e_minus) / (2 * c_k) * delta
        spsa_mess.append((e_plus + e_minus) / 2); spsa_wahr.append(energie_exakt(theta))
    print(f"VQE mit SPSA und Schüssen: wahre Energie am Ende {spsa_wahr[-1]:.4f} (Fehler {spsa_wahr[-1] - E18[0]:.3f}), "
          f"Schüsse insgesamt {600 * 2 * 2 * schuss_n:,}".replace(",", " "))
    unter_e1 = lambda f: next((k + 1 for k, w in enumerate(f) if w < E18[1]), None)
    print(f"unter E₁ nach {unter_e1(verlauf_exakt)} Auswertungen (COBYLA) bzw. {2 * unter_e1(spsa_wahr)} Auswertungen (SPSA)")
    print(f"gemessene SPSA-Schätzungen unter E₀: {np.sum(np.array(spsa_mess) < E18[0])} von {len(spsa_mess)}; "
          f"Streuung der Schätzungen in den letzten 100 Schritten {np.std(np.array(spsa_mess[-100:]) - np.array(spsa_wahr[-100:])):.3f}")
    print(f"Variationsprinzip: kleinste wahre Energie aller Auswertungen {min(min(verlauf_exakt), min(spsa_wahr)):.6f} ≥ E₀ = {E18[0]:.6f}")
    zz1, xx1 = energie_schuesse(res.x, 20000, rng, einzeln=True)
    print(f"Einzelschüsse am Optimum: Σ Z_iZ_(i+1) ∈ {sorted(set(zz1.astype(int)))}, Σ X_i ∈ {sorted(set(xx1.astype(int)))}")
    n_liste = np.array([10, 30, 100, 300, 1000, 3000, 10000])
    streuung = [np.std([energie_schuesse(res.x, n, rng) for _ in range(200)]) for n in n_liste]
    var_formel = np.var(zz1) + h18**2 * np.var(xx1)
    print(f"Streuung der Energieschätzung: {np.round(streuung, 4)}; Formel √((Var ZZ + Var X)/n) bei n = 1000: "
          f"{np.sqrt(var_formel / 1000):.4f}")

    fig, axes = plt.subplots(1, 3, figsize=(19, 5.5))
    ax = axes[0]
    ax.plot(np.arange(1, len(verlauf_exakt) + 1), verlauf_exakt, color="tab:blue", lw=1, label="COBYLA, exakte Erwartungswerte")
    ax.plot(np.arange(1, 1201, 2), spsa_mess, ".", ms=2, color="tab:orange", alpha=0.5, label="SPSA: gemessene Schätzungen")
    ax.plot(np.arange(1, 1201, 2), spsa_wahr, color="tab:red", lw=1.5, label="SPSA: wahre Energie der Parameter")
    ax.axhline(E18[0], color="k", ls="--", label=f"E₀ = {E18[0]:.4f}")
    ax.axhline(E18[1], color="0.5", ls=":", label=f"E₁ = {E18[1]:.4f}")
    ax.set_xlim(0, 1200); ax.set_ylim(E18[0] - 0.3, -2.0)
    ax.set_xlabel("Energieauswertungen"); ax.set_ylabel("⟨ψ(θ)|H|ψ(θ)⟩ [J]"); ax.legend(fontsize=8)
    ax.set_title("VQE: der Erwartungswert sinkt bis knapp über E₀")
    ax = axes[1]
    for werte, farbe, name in [(zz1, "tab:blue", "Σ Z_iZ_{i+1} (Z-Basis)"), (xx1, "tab:green", "Σ X_i (X-Basis)")]:
        u, c = np.unique(werte, return_counts=True)
        ax.bar(u + (0.15 if farbe == "tab:green" else -0.15), c / len(werte), width=0.3, color=farbe, label=name)
    ax.set_xlabel("Wert eines einzelnen Schusses = Eigenwert der Pauli-Summe"); ax.set_ylabel("Häufigkeit")
    ax.set_title("20 000 Schüsse am Optimum: nur ganze Zahlen"); ax.legend(fontsize=8)
    ax = axes[2]
    ax.loglog(n_liste, streuung, "o-", label="Streuung der Energieschätzung (200 Wiederholungen)")
    ax.loglog(n_liste, np.sqrt(var_formel / n_liste), "k:", label="√(Varianz/n)")
    ax.set_xlabel("Schüsse n pro Basis"); ax.set_ylabel("Standardabweichung [J]"); ax.legend(fontsize=8)
    ax.set_title("Messrauschen fällt wie 1/√n")
    plt.tight_layout()
    plt.show()
    print(f"Laufzeit des ganzen Notebooks bis hier: {time.time() - t_start:.0f} s")
