"""Quantenchaos für stability.ipynb: Scrambling (OTOC) in der Ising-Kette und Thermalisierung gegen Vielteilchen-Lokalisierung.

Schritt 3: der Kommutator C(r, t) = ½·Tr(|[W(t), V_r]|²)/2ⁿ zwischen einem lokalen Operator W am Rand und V_r im Abstand r
(out-of-time-ordered correlator, OTOC, bei unendlicher Temperatur), für die Ising-Kette mit Querfeld h_x und Längsfeld h_z
(chaotisch bei h_z = 0.5 nach Bañuls, Cirac und Hastings 2011, integrabel bei h_z = 0). Gemessen werden X-Operatoren
(in Richtung des Querfelds); gerechnet wird in der Basis, in der sie diagonal sind. Exakt mit dichten Matrizen.
Schritt 4: die XXZ-Kette (Δ = 1) mit Zufallsfeldern aus [−W, W] im Block mit Magnetisierung null, Start im Néel-Zustand;
gemessen werden die Imbalance (merkt sich die Kette, welche Plätze am Anfang besetzt waren?) und die Abstandsstatistik der
Energien (Pal und Huse 2010: Übergang bei W ≈ 3.5).
"""
from itertools import combinations

import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import eigh


# ---- Schritt 3: OTOC

def ising_rotated(n, hx, hz):
    """H = Σ X_i X_i+1 + h_x Σ Z_i + h_z Σ X_i in der Basis, in der die gemessenen Operatoren (hier Z) diagonal sind.

    Das ist die gewohnte Kette Σ Z_i Z_i+1 + h_x Σ X_i + h_z Σ Z_i nach einem Hadamard auf jedem Qubit; die gemessenen
    Operatoren sind dort die X_i. Offener Rand. Gibt H und die Diagonalen z[:, i] = ±1 zurück.
    """
    idx = np.arange(2 ** n)
    z = 1 - 2 * ((idx[:, None] >> np.arange(n)[::-1]) & 1)
    H = np.diag(hx * z.sum(axis=1).astype(float))
    for i in range(n):
        flip_i = idx ^ (1 << (n - 1 - i))
        H[flip_i, idx] += hz                                     # h_z X_i
        if i < n - 1:
            H[flip_i ^ (1 << (n - 2 - i)), idx] += 1.0           # X_i X_i+1
    return H, z


def otoc(n, hx, hz, times):
    """C(r, t) für W = X am Rand (Platz 0) und V = X auf Platz r; Zeilen: Zeiten, Spalten: r = 0 … n−1."""
    H, z = ising_rotated(n, hx, hz)
    E, U = eigh(H)
    w_e = U.T @ (z[:, 0][:, None] * U)                          # W in der Eigenbasis
    C = np.empty((len(times), n))
    for k, t in enumerate(times):
        ph = np.exp(1j * E * t)
        Wt = U @ (ph[:, None] * w_e * ph.conj()[None, :]) @ U.T   # W(t) = e^{iHt} W e^{−iHt}
        M = np.real(Wt * Wt.T)                                   # Tr(W V W V) = Σ_ab W_ab v_b W_ba v_a für diagonales V
        F = np.einsum("ar,ab,br->r", z, M, z) / 2 ** n
        C[k] = 1 - F
    return C


def plot_otoc(n=10, hx=1.05, hz_chaos=0.5, t_max=8.0, steps=81, threshold=0.5):
    """Links C(r, t) als Bild für die chaotische Kette, rechts C(t) weit hinten in beiden Ketten."""
    times = np.linspace(0, t_max, steps)
    Cc = otoc(n, hx, hz_chaos, times)
    Ci = otoc(n, hx, 0.0, times)
    arrive = np.array([times[np.argmax(Cc[:, r] > threshold)] if (Cc[:, r] > threshold).any() else np.nan for r in range(n)])
    ok = ~np.isnan(arrive) & (np.arange(n) >= 1)
    v_b = np.polyfit(arrive[ok], np.arange(n)[ok], 1)[0]
    print(f"Ising-Kette mit {n} Spins, h_x = {hx}: Die Störung erreicht Platz r (C > {threshold}) nach t = "
          + ", ".join(f"{arrive[r]:.1f}" for r in range(n) if ok[r]) + f"; Schmetterlingsgeschwindigkeit v_B ≈ {v_b:.2f} Plätze je Zeiteinheit")
    late = times > t_max * 0.6
    for name, C in (("chaotisch (h_z = %.1f)" % hz_chaos, Cc), ("integrabel (h_z = 0)", Ci)):
        print(f"  {name}: C am Platz r = {n // 2} nach t > {0.6 * t_max:.1f} im Mittel {C[late, n // 2].mean():.2f}, "
              f"am letzten Platz {C[late, -1].mean():.2f} (vollständig verwürfelt: 1)")
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    ax = axes[0]
    im = ax.pcolormesh(np.arange(n), times, Cc, shading="nearest", cmap="magma", vmin=0, vmax=1.2)
    ax.plot(np.arange(n)[ok], arrive[ok], "o", color="cyan", ms=4, label=f"Ankunft (C > {threshold}), v_B ≈ {v_b:.2f}")
    ax.set_xlabel("Abstand r vom Rand [Plätze]")
    ax.set_ylabel("Zeit t")
    ax.set_title(f"Chaotische Kette: Eine Störung am Rand breitet sich im Lichtkegel aus", fontsize=10)
    ax.legend(fontsize=8, loc="upper left")
    fig.colorbar(im, ax=ax, label="C(r, t)")
    ax = axes[1]
    for r, ls in ((n // 2, "-"), (n - 1, "--")):
        ax.plot(times, Cc[:, r], ls, color="tab:red", label=f"chaotisch, Platz {r}")
        ax.plot(times, Ci[:, r], ls, color="tab:blue", label=f"integrabel, Platz {r}")
    ax.axhline(1, color="black", lw=0.8, ls=":")
    ax.set_xlabel("Zeit t")
    ax.set_ylabel("C(r, t)")
    ax.set_title("Chaotisch bleibt die Information verwürfelt, integrabel kehrt sie zurück", fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()
    return Cc, Ci


# ---- Schritt 4: Thermalisierung und Vielteilchen-Lokalisierung

def sector(L):
    """Alle Bitmuster mit L/2 Einsen (Magnetisierung null) und ihre Nummer."""
    states = np.array([sum(1 << i for i in c) for c in combinations(range(L), L // 2)])
    return states, {s: k for k, s in enumerate(states)}


def xxz_sector(L, h, states, index):
    """H = Σ (S^x S^x + S^y S^y + S^z S^z)_i,i+1 + Σ h_i S^z_i auf dem Ring, im Block mit Magnetisierung null."""
    bits = (states[:, None] >> np.arange(L)) & 1
    sz = bits - 0.5
    H = np.diag(np.sum(sz * np.roll(sz, -1, axis=1), axis=1) + sz @ h)
    for i in range(L):
        j = (i + 1) % L
        for k in np.flatnonzero(bits[:, i] != bits[:, j]):
            H[index[states[k] ^ (1 << i) ^ (1 << j)], k] += 0.5
    return H, sz


def mbl(L=12, Ws=(0.5, 1, 2, 3, 4, 5, 6, 8, 10), realizations=15, times=np.geomspace(0.1, 1000, 60), seed=0):
    """Imbalance I(t) (Mittel über Zufallsfelder) und ⟨r⟩ der Energieabstände für jedes W."""
    states, index = sector(L)
    neel = index[sum(1 << i for i in range(0, L, 2))]
    sign = np.array([1 if i % 2 == 0 else -1 for i in range(L)])
    rng = np.random.default_rng(seed)
    out = {}
    for W in Ws:
        I, r = np.zeros(len(times)), []
        for _ in range(realizations):
            H, sz = xxz_sector(L, rng.uniform(-W, W, L), states, index)
            E, U = eigh(H)
            c = U[neel]                                          # Néel-Zustand in der Eigenbasis
            psi = U @ (c[:, None] * np.exp(-1j * np.outer(E, times)))
            I += (np.abs(psi) ** 2).T @ (2 * sz @ sign) / L
            Em = np.sort(E)[len(E) // 4: 3 * len(E) // 4]
            s = np.diff(Em)
            r.append(np.mean(np.minimum(s[:-1], s[1:]) / np.maximum(s[:-1], s[1:])))
        out[W] = (I / realizations, np.mean(r))
    return times, out


def plot_mbl(times, out, show=(0.5, 2, 5, 10)):
    """Links I(t) für einige Stärken der Unordnung, rechts die späte Imbalance und ⟨r⟩ gegen W."""
    Ws = np.array(list(out))
    late = np.array([out[W][0][times > 100].mean() for W in Ws])
    rbar = np.array([out[W][1] for W in Ws])
    print("Stärke W: Imbalance nach t > 100 | ⟨r⟩ (Poisson 0.386, Zufallsmatrix 0.531)")
    for W, a, b in zip(Ws, late, rbar):
        print(f"  W = {W:4.1f}: {a:5.2f} | {b:.3f}")
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    ax = axes[0]
    for W, c in zip(show, ["tab:red", "tab:orange", "tab:green", "tab:blue"]):
        ax.semilogx(times, out[W][0], color=c, lw=1.8, label=f"W = {W:g}")
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xlabel("Zeit t [ħ/J]")
    ax.set_ylabel("Imbalance I(t)")
    ax.set_title("Néel-Zustand: Merkt sich die Kette ihren Anfang?", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[1]
    ax.plot(Ws, late, "o-", color="black", label="Imbalance nach t > 100")
    ax.set_xlabel("Stärke der Unordnung W")
    ax.set_ylabel("Imbalance (Gedächtnis)")
    tw = ax.twinx()
    tw.plot(Ws, rbar, "s--", color="tab:purple", label="⟨r⟩ der Energieabstände")
    tw.axhline(0.531, color="tab:purple", lw=0.8, ls=":")
    tw.axhline(0.386, color="tab:purple", lw=0.8, ls=":")
    tw.set_ylim(0.37, 0.55)
    tw.text(Ws[-1], 0.527, "Zufallsmatrix 0.531", color="tab:purple", fontsize=8, ha="right", va="top")
    tw.text(Ws[0], 0.39, "Poisson 0.386", color="tab:purple", fontsize=8, ha="left", va="bottom")
    tw.set_ylabel("⟨r⟩", color="tab:purple")
    ax.set_title("Thermalisierung (vergessen) gegen Lokalisierung (erinnern)", fontsize=10)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = tw.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=8, loc="center right")
    fig.tight_layout()
    plt.show()
