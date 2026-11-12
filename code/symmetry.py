"""Symmetrien in Matrizen und Zustandsräumen für symmetries.ipynb: Fourier aus Translationssymmetrie, Erhaltungsgrößen in
einer Spinkette, Berry-Phase auf der Bloch-Kugel.

Alles simuliert, keine Downloads. Ring: eine symmetrische Kopplungsmatrix, die nur vom Abstand abhängt (zirkulant), wird
von der Fourier-Transformation diagonalisiert, gleich welche Kopplungen. Spinkette: XXZ-Kette mit zufälligen Feldern in z;
die Gesamtmagnetisierung bleibt erhalten und zerlegt den Hilbertraum in Blöcke. Berry-Phase: ein Spin-1/2 in einem Feld,
das langsam einen Kegel abfährt; die geometrische Phase ist der halbe Raumwinkel.
"""
import time

import numpy as np
import matplotlib.pyplot as plt


# ---- Schritt 1: Translationssymmetrie

def ring(N, couplings):
    """Symmetrische N × N-Matrix eines Rings: Diagonale 2·Σc, Kopplung −c_d zu den Nachbarn im Abstand d (Federn)."""
    H = np.zeros((N, N))
    for d, c in enumerate(couplings, start=1):
        for i in range(N):
            H[i, (i + d) % N] -= c
            H[(i + d) % N, i] -= c
    H[np.diag_indices(N)] = 2 * np.sum(couplings)
    return H


def plot_ring(N=200, couplings=(1.0, 0.45, -0.2, 0.07), N_time=2000):
    """Eigenvektoren des Rings sind Sinuswellen, die Eigenwerte die Fourier-Transformierte der ersten Zeile."""
    H = ring(N, couplings)
    w, V = np.linalg.eigh(H)
    w_fft = np.sort(np.real(np.fft.fft(H[0])))
    print(f"Ring aus {N} Gliedern, Kopplungen {couplings} zu den Nachbarn im Abstand 1 bis {len(couplings)}")
    print(f"  Eigenwerte aus der vollen Zerlegung und aus der Fourier-Transformation der ersten Zeile: "
          f"größte Abweichung {np.max(np.abs(w - w_fft)):.1e}")
    Hb = ring(N_time, couplings)
    t0 = time.perf_counter(); np.linalg.eigvalsh(Hb); t_full = time.perf_counter() - t0
    t0 = time.perf_counter(); np.fft.fft(Hb[0]); t_fft = time.perf_counter() - t0
    print(f"  Rechenzeit für {N_time} Glieder: volle Zerlegung {t_full:.2f} s, Fourier {t_fft * 1e3:.2f} ms "
          f"(etwa {t_full / t_fft:.0f}-mal schneller)")
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.5))
    for k, c in zip([0, 1, 3, 9], ["black", "tab:blue", "tab:orange", "tab:green"]):
        v = V[:, k] / np.max(np.abs(V[:, k]))
        axes[0].plot(np.arange(N), v - 2.3 * [0, 1, 3, 9].index(k), color=c, lw=1.2, label=f"Eigenvektor {k + 1}")
    axes[0].set_xlabel("Glied des Rings")
    axes[0].set_yticks([])
    axes[0].set_title("Die Eigenvektoren sind Sinuswellen (versetzt gezeichnet)", fontsize=10)
    axes[0].legend(fontsize=8, loc="upper right")
    idx = np.arange(N)
    axes[1].plot(idx, w_fft, color="tab:red", lw=2, label="Fourier-Transformierte der ersten Zeile (sortiert)")
    axes[1].plot(idx[::4], w[::4], "o", ms=5, mfc="none", color="black", label="Eigenwerte der vollen Zerlegung (jeder vierte)")
    axes[1].set_xlabel("Nummer des Eigenwerts (aufsteigend)")
    axes[1].set_ylabel("Eigenwert")
    axes[1].set_title("Eigenwerte = Fourier-Transformierte der Kopplungen", fontsize=10)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()


# ---- Schritt 2: Erhaltungsgrößen in einer Spinkette

def xxz(N, delta=1.0, W=1.0, seed=0):
    """Hamilton-Operator der periodischen XXZ-Kette mit Feldern h_i aus [−W, W] in z, als dichte Matrix (Basis: Bitmuster).

    H = Σ (S^x_i S^x_{i+1} + S^y_i S^y_{i+1} + Δ S^z_i S^z_{i+1}) + Σ h_i S^z_i. Die Felder brechen Translation und
    Spiegelung; erhalten bleibt nur die Gesamtmagnetisierung Σ S^z_i.
    """
    rng = np.random.default_rng(seed)
    h = rng.uniform(-W, W, N)
    d = 2 ** N
    H = np.zeros((d, d))
    states = np.arange(d)
    bits = (states[:, None] >> np.arange(N)) & 1                 # bits[s, i] = Spin i (1 = oben)
    sz = bits - 0.5
    H[states, states] = delta * np.sum(sz * np.roll(sz, -1, axis=1), axis=1) + sz @ h
    for i in range(N):
        j = (i + 1) % N
        flip = bits[:, i] != bits[:, j]                          # nur antiparallele Nachbarn tauschen
        s = states[flip]
        H[s, s ^ (1 << i) ^ (1 << j)] += 0.5
    return H, bits.sum(axis=1)


def spacing_ratios(E):
    """Verhältnisse benachbarter Abstände r = min(s_n, s_n+1)/max(…) in der mittleren Hälfte des Spektrums."""
    E = np.sort(E)
    E = E[len(E) // 4: 3 * len(E) // 4]
    s = np.diff(E)
    s1, s2 = s[:-1], s[1:]
    keep = np.maximum(s1, s2) > 1e-12
    return np.minimum(s1, s2)[keep] / np.maximum(s1, s2)[keep]


def plot_sectors(N=12, delta=1.0, W=1.0, seed=0, N_show=8):
    """Blockstruktur nach der Magnetisierung, Rechenzeit, und Abstandsstatistik ganz gegen in einem Block."""
    H, up = xxz(N, delta, W, seed)
    sizes = np.bincount(up, minlength=N + 1)
    t0 = time.perf_counter(); E_all = np.linalg.eigvalsh(H); t_full = time.perf_counter() - t0
    t0 = time.perf_counter()
    blocks = {k: np.linalg.eigvalsh(H[np.ix_(up == k, up == k)]) for k in range(N + 1)}
    t_blocks = time.perf_counter() - t0
    same = np.allclose(np.sort(np.concatenate(list(blocks.values()))), E_all)
    r_all, r_one = spacing_ratios(E_all), spacing_ratios(blocks[N // 2])
    print(f"XXZ-Kette mit {N} Spins: {2 ** N} Zustände; Blöcke nach der Zahl der Spins oben: "
          + ", ".join(str(s) for s in sizes) + f" (größter {sizes.max()})")
    print(f"  Eigenwerte ganz {t_full:.2f} s, in Blöcken {t_blocks:.2f} s; dieselben Eigenwerte: {same}")
    print(f"  mittleres r: alle Blöcke gemischt {r_all.mean():.3f}, nur der Block mit {N // 2} Spins oben {r_one.mean():.3f} "
          "(Poisson, unabhängige Niveaus: 0.386; Zufallsmatrizen GOE, Niveauabstoßung: 0.531)")
    Hs, ups = xxz(N_show, delta, W, seed)
    order = np.argsort(ups, kind="stable")
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.6), gridspec_kw={"width_ratios": [1, 1, 1.3]})
    axes[0].imshow(np.abs(Hs) > 1e-12, cmap="Greys", interpolation="nearest")
    axes[0].set_title(f"H für {N_show} Spins, Basis wie gezählt", fontsize=10)
    axes[1].imshow(np.abs(Hs[np.ix_(order, order)]) > 1e-12, cmap="Greys", interpolation="nearest")
    axes[1].set_title("dieselbe Matrix, nach Magnetisierung sortiert", fontsize=10)
    for ax in axes[:2]:
        ax.set_xticks([])
        ax.set_yticks([])
    r = np.linspace(0, 1, 200)
    axes[2].hist(r_all, bins=30, density=True, alpha=0.5, color="tab:blue", label=f"alle Blöcke gemischt, ⟨r⟩ = {r_all.mean():.3f}")
    axes[2].hist(r_one, bins=30, density=True, alpha=0.5, color="tab:red", label=f"ein Block, ⟨r⟩ = {r_one.mean():.3f}")
    axes[2].plot(r, 2 / (1 + r) ** 2, color="tab:blue", lw=1.5, label="Poisson: 2/(1 + r)²")
    axes[2].plot(r, 27 / 4 * (r + r ** 2) / (1 + r + r ** 2) ** 2.5, color="tab:red", lw=1.5, label="GOE (Atas und andere 2013)")
    axes[2].set_xlabel("Verhältnis benachbarter Abstände r")
    axes[2].set_ylabel("Dichte")
    axes[2].set_title(f"Niveaustatistik, {N} Spins", fontsize=10)
    axes[2].legend(fontsize=8)
    fig.tight_layout()
    plt.show()


# ---- Schritt 4: Berry-Phase

SX = np.array([[0, 1], [1, 0]], dtype=complex)
SY = np.array([[0, -1j], [1j, 0]])
SZ = np.array([[1, 0], [0, -1]], dtype=complex)


def berry_phase(theta, T, steps=4000):
    """Feld der Stärke 1 läuft in der Zeit T einmal auf einem Kegel mit Öffnungswinkel theta um z (ħ = 1).

    Start im Grundzustand (Spin parallel zum Feld). Gibt die geometrische Phase zurück: Gesamtphase minus dynamische
    Phase, auf (−π, π] gebracht. Jeder Zeitschritt ist exakt (Exponential einer 2 × 2-Matrix).
    """
    def H(t):
        n = np.array([np.sin(theta) * np.cos(2 * np.pi * t / T), np.sin(theta) * np.sin(2 * np.pi * t / T), np.cos(theta)])
        return -0.5 * (n[0] * SX + n[1] * SY + n[2] * SZ)
    w, V = np.linalg.eigh(H(0))
    psi0 = V[:, 0]
    psi = psi0.copy()
    dt = T / steps
    for k in range(steps):
        w, V = np.linalg.eigh(H((k + 0.5) * dt))
        psi = V @ (np.exp(-1j * w * dt) * (V.conj().T @ psi))
    total = np.angle(np.vdot(psi0, psi))
    dyn = 0.5 * T                                            # Energie −1/2 über die Zeit T: Phase +T/2
    return float(np.angle(np.exp(1j * (total - dyn)))), float(abs(np.vdot(psi0, psi)))


def plot_berry(thetas_deg=np.arange(0, 181, 15), times=(20, 100, 500)):
    """Geometrische Phase gegen den Öffnungswinkel, für drei Umlaufzeiten, gegen −Ω/2 = −π(1 − cos θ)."""
    th = np.deg2rad(thetas_deg)
    theory = np.angle(np.exp(-1j * np.pi * (1 - np.cos(th))))
    fig, ax = plt.subplots(figsize=(10, 4.6))
    tt = np.linspace(0, np.pi, 300)
    ax.plot(np.rad2deg(tt), np.angle(np.exp(-1j * np.pi * (1 - np.cos(tt)))), color="black", lw=1.5,
            label="halber Raumwinkel: −π(1 − cos θ), auf (−π, π]")
    for T, c in zip(times, ["tab:orange", "tab:blue", "tab:red"]):
        res = [berry_phase(t, T) for t in th]
        g = np.array([r[0] for r in res])
        err = np.max(np.abs(np.angle(np.exp(1j * (g - theory)))))
        print(f"Umlaufzeit T = {T:4d} (in 1/Feld): größte Abweichung von −Ω/2 {err:.4f} rad, "
              f"Überlapp mit dem Startzustand mindestens {min(r[1] for r in res):.4f}")
        ax.plot(thetas_deg, g, "o", ms=6 if T == times[-1] else 4, mfc="none" if T != times[-1] else c, color=c,
                label=f"numerisch, Umlaufzeit T = {T}")
    ax.set_xlabel("Öffnungswinkel des Kegels θ [°]")
    ax.set_ylabel("geometrische Phase [rad]")
    ax.set_title("Berry-Phase: Sie hängt nur vom Raumwinkel ab, nicht von der Zeit", fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()
