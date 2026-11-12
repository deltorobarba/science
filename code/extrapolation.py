"""Approximation und Extrapolation für approximation.ipynb: ein Molekülpotential, gelernt nahe am Gleichgewicht.

Maschinell gelernte Potentiale (neuronale Netze, die Energien aus Quantenchemie-Rechnungen nachbilden) treiben heute
Molekulardynamik von Materialien und Proteinen. Hier ein Modell davon in einer Dimension: Die „Wahrheit“ ist das
Morse-Potential mit den Konstanten von H₂ (Dissoziationsenergie D_e = 4.747 eV, Gleichgewicht 0.7414 Å,
Schwingung 4401 cm⁻¹, NIST), gelernt aus 60 verrauschten Punkten zwischen 0.6 und 1.0 Å. Verglichen werden die
harmonische Näherung (Parabel, Taylor bis zur zweiten Ordnung), ein Polynom sechsten Grades, je fünf neuronale Netze mit
tanh und mit ReLU (scikit-learn, verschiedene Startwerte) und ein Modell mit der richtigen Form (drei Parameter).
"""
import warnings

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.neural_network import MLPRegressor

DE, RE, WE = 4.747, 0.7414, 4401.2                      # eV, Å, cm⁻¹ (H₂, Grundzustand)
MU = 1.00784 / 2 * 1.66054e-27                          # reduzierte Masse [kg]
A = np.sqrt(MU * (WE * 2.99792458e10 * 2 * np.pi) ** 2 / (2 * DE * 1.602177e-19)) * 1e-10   # [1/Å]


def morse(r, D=DE, a=A, r0=RE):
    return D * (1 - np.exp(-a * (r - r0))) ** 2


def train(lo=0.6, hi=1.0, n=60, noise=0.002, seeds=5, hidden=(32, 32), seed=0):
    """Trainingsdaten und alle Modelle; gibt (r_train, V_train, {Name: Funktion r → Vorhersagen}) zurück."""
    rng = np.random.default_rng(seed)
    r = np.sort(rng.uniform(lo, hi, n))
    y = morse(r) + rng.normal(0, noise, n)
    mr, sr, my, sy = r.mean(), r.std(), y.mean(), y.std()
    models = {}
    c2 = np.polyfit(r, y, 2)
    models["Parabel (harmonisch)"] = lambda x: np.polyval(c2, x)[None]
    c6 = np.polyfit((r - mr) / sr, y, 6)
    models["Polynom, Grad 6"] = lambda x: np.polyval(c6, (x - mr) / sr)[None]
    for act in ("tanh", "relu"):
        nets = []
        for s in range(seeds):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                net = MLPRegressor(hidden, activation=act, solver="lbfgs", max_iter=20000, tol=1e-10, random_state=s)
                net.fit(((r - mr) / sr)[:, None], (y - my) / sy)
            nets.append(net)
        models[f"{seeds} Netze mit {act}"] = lambda x, nets=nets: np.array(
            [nt.predict(((x - mr) / sr)[:, None]) * sy + my for nt in nets])
    p, _ = curve_fit(morse, r, y, p0=[3, 2, 0.75])
    models["Morse-Form (3 Parameter)"] = lambda x: morse(x, *p)[None]
    print(f"Training: {n} Punkte zwischen {lo} und {hi} Å (Energie {morse(lo):.2f} bis {morse(hi):.2f} eV über dem Minimum), "
          f"Rauschen {noise * 1000:.0f} meV; Morse-Form angepasst: D = {p[0]:.2f} eV, a = {p[1]:.2f}/Å, r₀ = {p[2]:.4f} Å "
          f"(wahr {DE}, {A:.2f}, {RE})")
    return r, y, models


def plot_extrapolation(r_train, y_train, models, lo=0.6, hi=1.0, r_max=4.0):
    """Links die Potentialkurven, rechts der Fehler gegen den Abstand; grau der Trainingsbereich."""
    x = np.linspace(0.4, r_max, 1000)
    truth = morse(x)
    inside = (x >= lo) & (x <= hi)
    k2, k4 = np.argmin(np.abs(x - 2)), len(x) - 1
    print(f"Wahr: V(0.4 Å) = {morse(0.4):.2f} eV, V(2 Å) = {morse(2):.2f} eV, V({r_max:g} Å) = {morse(r_max):.2f} eV")
    preds = {name: f(x) for name, f in models.items()}
    for name, P in preds.items():
        err_in = np.max(np.abs(P[:, inside] - truth[inside])) * 1000
        fmt = lambda v: (f"{v.min():.1f} bis {v.max():.1f}" if len(v) > 1 else f"{v[0]:.1f}") if np.all(np.abs(v) < 1e4) else \
            f"{v[0]:.0e}" if len(v) == 1 else f"{v.min():.0e} bis {v.max():.0e}"
        print(f"  {name:26s} Fehler im Training höchstens {err_in:5.1f} meV; V(0.4 Å) {fmt(P[:, 0])}, "
              f"V(2 Å) {fmt(P[:, k2])}, V({r_max:g} Å) {fmt(P[:, k4])} eV")

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    colors = dict(zip(models, ["tab:orange", "tab:purple", "tab:green", "tab:red", "tab:blue"]))
    for ax in axes:
        ax.axvspan(lo, hi, color="grey", alpha=0.2)
    ax = axes[0]
    ax.plot(x, truth, color="grey", lw=5, alpha=0.6, label="wahr: Morse-Potential von H₂")
    for name, P in preds.items():
        for i, row in enumerate(P):
            ax.plot(x, row, color=colors[name], lw=1.2, alpha=0.9, ls="--" if name.startswith("Morse") else "-",
                    label=name if i == 0 else None)
    ax.plot(r_train, y_train, ".", color="black", ms=4, label="Trainingspunkte (grau: Bereich)")
    ax.axhline(DE, color="black", ls=":", lw=1)
    ax.set_ylim(-1, 9)
    ax.set_xlabel("Abstand der Kerne r [Å]")
    ax.set_ylabel("Energie über dem Minimum [eV]")
    ax.set_title("Gelernt zwischen 0.6 und 1.0 Å, gefragt bis zur Dissoziation", fontsize=10)
    ax.legend(fontsize=8, loc="upper right")
    ax = axes[1]
    for name, P in preds.items():
        for i, row in enumerate(P):
            ax.semilogy(x, np.abs(row - truth) + 1e-6, color=colors[name], lw=1, alpha=0.8, label=name if i == 0 else None)
    ax.set_ylim(1e-5, 1e4)
    ax.set_xlabel("Abstand der Kerne r [Å]")
    ax.set_ylabel("|Modell − wahr| [eV]")
    ax.set_title("Innen klein für alle, außen entscheidet die Form der Familie", fontsize=10)
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    plt.show()
