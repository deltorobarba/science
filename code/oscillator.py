"""Der harmonische Oszillator und seine Abweichungen für heisenbergweyl.ipynb.

Schritt 1: Spektren nahe einem Minimum. Transmon-Qubit H = 4E_C (n − n_g)² − E_J cos φ in der Ladungsbasis (Koch und
andere 2007) und das Morse-Potential mit den Konstanten von H₂ (ω_e = 4401.21 cm⁻¹, D_e = 38 297 cm⁻¹, Huber und
Herzberg), beide gegen den Oszillator mit derselben Krümmung.
Schritt 3: Eine Viertelperiode des Oszillators ist die Fourier-Transformation; Q und P auf einem Gitter mit d Punkten
(Abstand √(2π/d), P = F†QF) und abgeschnitten nach N Fock-Zuständen: [Q, P] = i·1 kann nicht überall gelten (Spur null).
Schritt 5: Wellenpaket im harmonischen und im Morse-Potential von H₂ gegen die klassische Bahn (Ehrenfest).
Einheiten in Schritt 5: atomare Einheiten intern, ausgegeben in Å und fs.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.linalg import eigh

CM_TO_HARTREE = 1 / 219474.63
BOHR_A, AU_FS = 0.529177, 0.0241888
H2 = dict(we=4401.21, De=38297.0, mu=0.50391 * 1822.888)      # cm⁻¹, cm⁻¹, reduzierte Masse in Elektronenmassen


# ---- Schritt 1: Spektren

def transmon(EJ=12.5, EC=0.25, ng=0.0, ncut=40, levels=8):
    """Niveaus des Transmons in GHz (über dem Grundzustand) in der Ladungsbasis n = −ncut … ncut."""
    n = np.arange(-ncut, ncut + 1)
    H = np.diag(4 * EC * (n - ng) ** 2) - EJ / 2 * (np.eye(len(n), k=1) + np.eye(len(n), k=-1))
    E = np.linalg.eigvalsh(H)[:levels]
    return E - E[0]


def morse_levels(we=H2["we"], De=H2["De"]):
    """Gebundene Niveaus des Morse-Potentials in cm⁻¹ über dem Grundzustand: ω_e(v+½) − ω_e²/(4D_e)(v+½)²."""
    wexe = we ** 2 / (4 * De)
    v = np.arange(int(we / (2 * wexe) - 0.5) + 1)
    E = we * (v + 0.5) - wexe * (v + 0.5) ** 2
    return E - E[0]


def plot_spectra(EJ=12.5, EC=0.25, levels=6):
    """Links das Potential des Transmons mit seinen Niveaus und der Parabel, rechts die Abstände der Niveaus."""
    w_p = np.sqrt(8 * EJ * EC)                                    # Plasmafrequenz: Oszillator mit derselben Krümmung
    E = transmon(EJ, EC, levels=40)
    E = E[: min(levels, int(np.sum(E + w_p / 2 < 2 * EJ)))]       # nur Niveaus unter der Barriere 2E_J: dort ist es ein Oszillator                                    # Plasmafrequenz: Oszillator mit derselben Krümmung
    f = np.diff(E)
    print(f"Transmon mit E_J = {EJ:g} GHz, E_C = {EC:g} GHz (E_J/E_C = {EJ / EC:g}): Parabel gibt √(8 E_J E_C) = {w_p:.3f} GHz für jeden Übergang")
    print("  Übergänge n → n+1 [GHz]: " + ", ".join(f"{x:.3f}" for x in f[:5])
          + f"; Anharmonizität f12 − f01 = {1e3 * (f[1] - f[0]):.0f} MHz (Näherung −E_C = {-1e3 * EC:.0f} MHz)")
    M = morse_levels()
    wexe = H2["we"] ** 2 / (4 * H2["De"])
    print(f"H₂ als Morse-Oszillator: {len(M)} gebundene Niveaus; erster Übergang {M[1]:.0f} cm⁻¹ "
          f"(Parabel {H2['we']:.0f} cm⁻¹, gemessen 4161 cm⁻¹), der letzte nur noch {M[-1] - M[-2]:.0f} cm⁻¹; "
          f"Abstand sinkt je Niveau um 2ω_e x_e = {2 * wexe:.0f} cm⁻¹")
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    ax = axes[0]
    phi = np.linspace(-np.pi, np.pi, 400)
    V = EJ * (1 - np.cos(phi))
    ax.plot(phi, V, color="black", lw=2, label="Transmon: E_J (1 − cos φ)")
    ax.plot(phi, EJ * phi ** 2 / 2, "--", color="tab:blue", label="Parabel E_J φ²/2 (Grad 2)")
    E0 = w_p / 2 - EC / 4                                         # Nullpunkt über dem Minimum (Näherung)
    for k, e in enumerate(E):
        x = np.arccos(max(1 - (E0 + e) / EJ, -1))
        ax.plot([-x, x], [E0 + e] * 2, color="tab:red", lw=1.4, label="Niveaus des Transmons" if k == 0 else None)
        xh = np.sqrt(2 * (w_p * (k + 0.5)) / EJ)
        ax.plot([-xh, xh], [w_p * (k + 0.5)] * 2, ":", color="tab:blue", lw=1, label="Niveaus der Parabel" if k == 0 else None)
    ax.set_xlim(-np.pi, np.pi)
    ax.set_ylim(0, 2.6 * EJ)
    ax.set_xlabel("Phase φ über dem Kontakt [rad]")
    ax.set_ylabel("Energie / h [GHz]")
    ax.set_title("Transmon: nahe am Minimum fast eine Parabel", fontsize=10)
    ax.legend(fontsize=8, loc="upper center", ncol=2)
    ax = axes[1]
    nT = np.arange(len(f))
    ax.plot(nT, f / f[0], "o-", color="tab:red", label="Transmon, Übergang n → n+1")
    ax.plot(np.arange(len(M) - 1), np.diff(M) / M[1], "s-", color="tab:green", ms=4, label="H₂ (Morse), Schwingung v → v+1")
    ax.axhline(1, color="tab:blue", ls="--", label="Oszillator: alle Abstände gleich")
    ax.set_xlabel("unteres Niveau n bzw. v")
    ax.set_ylabel("Abstand / erster Abstand")
    ax.set_title("Ungleiche Abstände machen aus dem Oszillator ein Qubit", fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()
    return E, M


# ---- Schritt 3: Vierteldrehung und Kommutator auf endlichen Räumen

def hermite_functions(x, nmax):
    """Eigenfunktionen φ_n(x) des Oszillators H = (p² + x²)/2 (stabile Rekursion), Zeilen n = 0 … nmax−1."""
    phi = np.zeros((nmax, len(x)))
    phi[0] = np.pi ** -0.25 * np.exp(-x ** 2 / 2)
    if nmax > 1:
        phi[1] = np.sqrt(2) * x * phi[0]
    for n in range(2, nmax):
        phi[n] = np.sqrt(2 / n) * x * phi[n - 1] - np.sqrt((n - 1) / n) * phi[n - 2]
    return phi


def quarter_turn(psi0, x, nmax=120):
    """ψ(x, t = π/2) unter H = (p² + x²)/2 über die Fock-Zerlegung, und die Fourier-Transformierte ψ̃(p) von ψ0."""
    dx = x[1] - x[0]
    phi = hermite_functions(x, nmax)
    c = phi @ psi0 * dx
    psi_t = (c * np.exp(-1j * (np.arange(nmax) + 0.5) * np.pi / 2)) @ phi
    psi_p = np.exp(-1j * np.outer(x, x)) @ psi0 * dx / np.sqrt(2 * np.pi)   # ψ̃(p) auf denselben Stützstellen
    return psi_t, psi_p, 1 - np.sum(np.abs(c) ** 2)


def grid_qp(d):
    """Q und P auf einem Gitter mit d Punkten (d ungerade), Abstand √(2π/d); P = F† Q F mit zentrierter DFT."""
    k = np.arange(d) - (d - 1) // 2
    delta = np.sqrt(2 * np.pi / d)
    Fc = np.exp(-2j * np.pi * np.outer(k, k) / d) / np.sqrt(d)
    Q = np.diag(k * delta)
    return Q, Fc.conj().T @ Q @ Fc


def ccr_by_level(d):
    """⟨n|[Q, P]|n⟩/i in den Eigenzuständen von (Q² + P²)/2 auf dem Gitter; ihre Summe ist die Spur, also null."""
    Q, P = grid_qp(d)
    _, V = eigh((Q @ Q + P @ P) / 2)
    C = Q @ P - P @ Q
    return np.real(np.einsum("in,ij,jn->n", V.conj(), C, V) / 1j)


def plot_phase(x0=1.6, p0=0.0, ds=(25, 51, 101, 201), N_fock=12):
    """Links die Vierteldrehung, rechts ⟨n|[Q,P]|n⟩/i auf Gittern und nach N Fock-Zuständen."""
    x = np.linspace(-10, 10, 801)
    dx = x[1] - x[0]
    psi0 = np.exp(-(x - x0) ** 2 / 2 * 2.5 + 1j * p0 * x) + 0.7 * np.exp(-(x + 1.2) ** 2 / 2 * 0.6 + 1j * 1.5 * x)
    psi0 /= np.sqrt(np.sum(np.abs(psi0) ** 2) * dx)
    psi_t, psi_p, lost = quarter_turn(psi0, x)
    phase = np.vdot(psi_p, psi_t) / abs(np.vdot(psi_p, psi_t))
    err = np.max(np.abs(psi_t - phase * psi_p))
    print(f"Vierteldrehung t = π/2 (Periode 2π): größte Abweichung |ψ(t) − e^(iθ) ψ̃| = {err:.1e}, "
          f"globale Phase θ = {np.degrees(np.angle(phase)):.1f}° (Fock-Rest {lost:.0e})")
    a = np.diag(np.sqrt(np.arange(1, N_fock)), 1)
    Qf, Pf = (a + a.T) / np.sqrt(2), 1j * (a.T - a) / np.sqrt(2)
    diag = np.real(np.diag(Qf @ Pf - Pf @ Qf) / 1j)
    print(f"Abgeschnitten nach N = {N_fock} Fock-Zuständen: Diagonale von [Q, P]/i = "
          + ", ".join(f"{v:g}" for v in diag) + f"; Spur {diag.sum():g}")
    curves = {}
    for d in ds:
        c = ccr_by_level(d)
        good = np.argmax(np.abs(c - 1) > 0.01)
        curves[d] = c
        print(f"  Gitter mit d = {d}: ⟨n|[Q,P]|n⟩/i auf 1 % genau für die untersten {good} Zustände ({good / d:.0%}), "
              f"laufende Summe höchstens {np.cumsum(c).max():.1f}, am Ende {c.sum():.0e}")
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    ax = axes[0]
    ax.plot(x, np.abs(psi0) ** 2, color="black", lw=1.5, label="|ψ(x, 0)|²")
    ax.plot(x, np.abs(psi_t) ** 2, color="tab:red", lw=2.5, label="|ψ(x, T/4)|² nach einer Viertelperiode")
    ax.plot(x, np.abs(psi_p) ** 2, "--", color="tab:cyan", lw=1.5, label="|ψ̃(p)|² Fourier-Transformierte von ψ(x, 0)")
    ax.set_xlim(-6, 6)
    ax.set_xlabel("x bzw. p (Einheiten des Oszillators)")
    ax.set_ylabel("Wahrscheinlichkeitsdichte")
    ax.set_title("Eine Viertelperiode des Oszillators ist die Fourier-Transformation", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[1]
    for (d, c), col in zip(curves.items(), ["tab:orange", "tab:green", "tab:purple", "tab:brown"]):
        ax.plot((np.arange(d) + 1) / d, np.cumsum(c) / d, color=col, lw=1.6, label=f"Gitter mit d = {d} Punkten")
    ax.plot((np.arange(N_fock) + 1) / N_fock, np.cumsum(diag) / N_fock, "o--", color="black", ms=4,
            label=f"abgeschnittener Oszillator, N = {N_fock}")
    ax.plot([0, 1], [0, 1], ":", color="grey", label="Heisenberg [Q, P] = i: jedes Niveau trägt 1 bei")
    ax.set_xlabel("Anteil der Niveaus n / Zahl der Zustände")
    ax.set_ylabel("Σ ⟨m|[Q, P]|m⟩ / i bis n, geteilt durch die Zahl der Zustände")
    ax.set_title("Im Endlichen ist die Spur von [Q, P] null: oben wird zurückgezahlt", fontsize=10)
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    plt.show()
    return curves


# ---- Schritt 5: Ehrenfest

def _grid_hamiltonian(V, x, mu):
    """H = p²/2μ + V(x) auf einem Fourier-Gitter (spektral genau)."""
    n, dx = len(x), x[1] - x[0]
    k = 2 * np.pi * np.fft.fftfreq(n, dx)
    F = np.fft.fft(np.eye(n), axis=0)
    T = np.real(np.linalg.inv(F) @ np.diag(k ** 2 / (2 * mu)) @ F)
    return T + np.diag(V)


def ehrenfest(shift_A=0.25, t_max_fs=160, steps=1600, n=700):
    """⟨x⟩(t) eines verschobenen Grundzustands im harmonischen und im Morse-Potential von H₂, quantenmechanisch und klassisch."""
    we, De, mu = H2["we"] * CM_TO_HARTREE, H2["De"] * CM_TO_HARTREE, H2["mu"]
    a = we * np.sqrt(mu / (2 * De))
    x = np.linspace(-3.0, 4.0, n)                                  # Abstand vom Gleichgewicht in Bohr
    pots = {"harmonisch": lambda r: 0.5 * mu * we ** 2 * r ** 2, "Morse (H₂)": lambda r: De * (1 - np.exp(-a * r)) ** 2}
    force = {"harmonisch": lambda r: -mu * we ** 2 * r, "Morse (H₂)": lambda r: -2 * De * a * np.exp(-a * r) * (1 - np.exp(-a * r))}
    t = np.linspace(0, t_max_fs / AU_FS, steps)
    x0 = shift_A / BOHR_A
    sigma = 1 / np.sqrt(2 * mu * we)
    psi0 = np.exp(-(x - x0) ** 2 / (4 * sigma ** 2))
    psi0 /= np.linalg.norm(psi0)
    out = {}
    for name, V in pots.items():
        E, U = eigh(_grid_hamiltonian(V(x), x, mu))
        c = U.T @ psi0
        psi_t = U @ (c[:, None] * np.exp(-1j * np.outer(E, t)))
        xq = np.sum(np.abs(psi_t) ** 2 * x[:, None], axis=0)
        sol = solve_ivp(lambda _, y: [y[1] / mu, force[name](y[0])], (0, t[-1]), [x0, 0.0], t_eval=t, rtol=1e-12, atol=1e-14,
                        method="DOP853")
        out[name] = (xq * BOHR_A, sol.y[0] * BOHR_A)
    wexe = we ** 2 / (4 * De)
    t_rev = 2 * np.pi / (2 * wexe) * AU_FS
    return t * AU_FS, out, t_rev, 2 * np.pi / we * AU_FS


def plot_ehrenfest(shift_A=0.25, t_max_fs=160):
    """Links harmonisch, rechts Morse: Mittelwert des Wellenpakets gegen die klassische Bahn."""
    t, out, t_rev, period = ehrenfest(shift_A, t_max_fs)
    dh = np.max(np.abs(out["harmonisch"][0] - out["harmonisch"][1]))
    xq, xc = out["Morse (H₂)"]
    amp = lambda y, w: np.ptp(y[w])
    late = (t > t_rev - 2 * period) & (t < t_rev + 2 * period)
    mid = (t > t_rev / 2 - 2 * period) & (t < t_rev / 2 + 2 * period)
    print(f"H₂, Wellenpaket um {shift_A} Å gestreckt, Schwingungsperiode {period:.2f} fs:")
    print(f"  harmonisch: größte Abweichung zwischen ⟨x⟩ und klassischer Bahn {dh:.1e} Å (Ehrenfest exakt für Grad 2)")
    if late.sum() and t[-1] >= t_rev + 2 * period:
        print(f"  Morse: Schwingungsweite von ⟨x⟩ am Anfang {amp(xq, t < 2 * period):.3f} Å, um t = {t_rev / 2:.0f} fs "
              f"{amp(xq, mid):.3f} Å, um t = {t_rev:.0f} fs (Wiederkehr 2π/(2ω_e x_e)) {amp(xq, late):.3f} Å; "
              f"klassisch bleibt sie {amp(xc, late):.3f} Å")
    else:
        print(f"  Morse: Schwingungsweite von ⟨x⟩ am Anfang {amp(xq, t < 2 * period):.3f} Å, am Ende {amp(xq, t > t[-1] - 2 * period):.3f} Å; "
              f"die Wiederkehr bei {t_rev:.0f} fs liegt hinter dem Zeitfenster (t_max_fs größer wählen)")
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    for ax, (name, (q, c)) in zip(axes, out.items()):
        ax.plot(t, c, color="tab:blue", lw=1, label="klassische Bahn (Newton)")
        ax.plot(t, q, "--" if name == "harmonisch" else "-", color="tab:red", lw=1.2, label="⟨x⟩ des Wellenpakets")
        ax.set_xlabel("Zeit [fs]")
        ax.set_ylabel("Streckung der Bindung [Å]")
        ax.legend(fontsize=8, loc="lower right")
    if t_rev <= t[-1]:
        axes[1].axvline(t_rev, color="grey", ls=":", lw=1)
        axes[1].text(t_rev, axes[1].get_ylim()[1] * 0.92, " Wiederkehr", color="grey", fontsize=8)
    axes[0].set_title(f"Harmonisch (Grad 2): Quantenmittel = klassische Bahn (Abweichung {dh:.0e} Å)", fontsize=10)
    axes[1].set_title("Morse (Grad ≥ 3): das Paket zerfließt und kehrt wieder", fontsize=10)
    fig.tight_layout()
    plt.show()
    return t, out
