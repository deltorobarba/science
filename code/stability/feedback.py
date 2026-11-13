"""Rückkopplung für stability.ipynb: adaptive Optik im Teleskop und die Lernrate beim Gradientenabstieg.

Teil 1: ein Regelkreis der adaptiven Optik, auf eine Mode reduziert. Die Atmosphäre verschiebt die Phase φ_k (langsamer
Zufallsprozess mit einem Spektrum ∝ f^(−8/3) oberhalb von 10 Hz wie bei Kolmogorov-Turbulenz, Bildfrequenz 1 kHz), der Sensor misst den Rest
mit Rauschen (Streuung 0.2) und zwei Bildern Verzögerung, ein Integrator stellt den Spiegel nach: c_{k+1} = c_k + g·Messung_{k−1}.
Der Kreis ist stabil, solange alle Nullstellen von z² − z + g innerhalb des Einheitskreises liegen (g < 1).
Teil 2: Gradientenabstieg für die kleinsten Quadrate auf dem Diabetes-Datensatz (442 Patienten, 10 Merkmale, in
scikit-learn enthalten). Er konvergiert genau dann, wenn die Lernrate kleiner ist als 2/λ_max, mit λ_max dem größten
Eigenwert der Hesse-Matrix XᵀX/n.
"""
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_diabetes


def turbulence(n, seed=0, slope=-8 / 3, f0=10.0, fs=1000.0):
    """Phasenverlauf mit Leistungsspektrum ∝ f^slope oberhalb von f0 [Hz] (darunter flach), Streuung 1."""
    rng = np.random.default_rng(seed)
    f = np.fft.rfftfreq(n, 1 / fs)
    amp = np.where(f > 0, (np.maximum(f, f0)) ** (slope / 2), 0)
    x = np.fft.irfft(amp * np.exp(2j * np.pi * rng.uniform(size=len(f))), n)
    return x / x.std()


def ao_loop(phi, gain, delay=2, noise=0.2, seed=1):
    """Rest φ − c im geschlossenen Kreis: c_{k+1} = c_k + g·Messung_{k−d+1} (Integrator, d Bilder Verzögerung)."""
    rng = np.random.default_rng(seed)
    c = np.zeros(len(phi) + 1)
    meas = np.zeros(len(phi))
    for k in range(len(phi)):
        meas[k] = phi[k] - c[k] + noise * rng.normal()
        c[k + 1] = c[k] + gain * (meas[k - delay + 1] if k - delay + 1 >= 0 else 0.0)
        if abs(c[k + 1]) > 1e6:
            return np.full(len(phi), np.inf)
    return phi - c[:-1]


def stability_limit(delay=2):
    """Größte Verstärkung, bei der alle Nullstellen von z^d − z^(d−1) + g im Einheitskreis liegen."""
    gs = np.linspace(0.001, 2.5, 5000)

    def stable(g):
        poly = np.zeros(delay + 1)
        poly[0], poly[1] = 1, -1
        poly[delay] += g
        return np.max(np.abs(np.roots(poly))) < 1

    return gs[np.argmin([stable(g) for g in gs])]


def gradient_descent(X, y, eta, steps=200):
    w = np.zeros(X.shape[1])
    loss = []
    for _ in range(steps):
        r = X @ w - y
        loss.append(0.5 * np.mean(r ** 2))
        w -= eta * X.T @ r / len(y)
    return np.array(loss)


def plot_feedback(gains=np.linspace(0.02, 1.1, 55), delay=2, factors=(0.5, 0.95, 1.05), n=20000):
    """Links der Rest der adaptiven Optik gegen die Verstärkung, rechts der Verlust beim Gradientenabstieg."""
    gains = np.asarray(gains, float)
    phi = turbulence(n)
    g_max = stability_limit(delay)
    rms = []
    for g in gains:
        res = ao_loop(phi, g, delay)
        rms.append(np.sqrt(np.mean(res[n // 4:] ** 2)) if np.all(np.isfinite(res)) else np.inf)
    rms = np.array(rms)
    k = int(np.argmin(rms))
    poly = "z² − z + g" if delay == 2 else f"z^{delay} − z^{delay - 1} + g"
    print(f"Adaptive Optik, {delay} Bilder Verzögerung: stabil bis g = {g_max:.3f} (Nullstellen von {poly}); "
          f"Rest (ohne Regelung 1) bei g = {gains[0]:.2f}: {rms[0]:.2f}, am besten {rms[k]:.2f} bei g = {gains[k]:.2f}, "
          f"bei g = {gains[gains < g_max][-1]:.2f}: {rms[gains < g_max][-1]:.2f}; darüber wächst er ohne Grenze "
          f"({np.sum(~np.isfinite(rms))} von {len(gains)} Verstärkungen)")
    data = load_diabetes()
    X = (data.data - data.data.mean(0)) / data.data.std(0)
    X = np.hstack([X, np.ones((len(X), 1))])
    y = (data.target - data.target.mean()) / data.target.std()
    lam = np.linalg.eigvalsh(X.T @ X / len(y))
    eta_max = 2 / lam[-1]
    print(f"Diabetes-Daten ({X.shape[0]} Patienten, {X.shape[1] - 1} Merkmale): Eigenwerte der Hesse-Matrix von "
          f"{lam[0]:.3f} bis {lam[-1]:.2f}; Grenze der Lernrate 2/λ_max = {eta_max:.3f}")
    losses = {}
    for f in factors:
        losses[f] = gradient_descent(X, y, f * eta_max)
        print(f"  Lernrate {f:.2f}·2/λ_max: Verlust nach 200 Schritten {losses[f][-1]:.3g}")
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    ax = axes[0]
    ax.plot(gains[np.isfinite(rms)], rms[np.isfinite(rms)], "o-", color="black", ms=4, label="Rest nach der Regelung (Streuung)")
    ax.axhline(1, color="grey", ls=":", label="ohne Regelung")
    ax.axvline(g_max, color="tab:red", ls="--", label=f"Stabilitätsgrenze g = {g_max:.3f}")
    ax.axvspan(g_max, gains[-1] + 0.02, color="tab:red", alpha=0.12, label="instabil: der Rest wächst ohne Grenze")
    ax.plot(gains[k], rms[k], "*", color="tab:green", ms=14, label=f"beste Verstärkung g = {gains[k]:.2f}")
    ax.set_ylim(0, 2)
    ax.set_xlabel("Verstärkung g des Regelkreises")
    ax.set_ylabel("verbleibende Phase (Streuung der Turbulenz = 1)")
    ax.set_title("Adaptive Optik: zu wenig Rückkopplung bleibt hinterher, zu viel schwingt", fontsize=10)
    ax.legend(fontsize=8, loc="upper left")
    ax = axes[1]
    for f, c in zip(factors, ["tab:blue", "tab:orange", "tab:red"]):
        ax.semilogy(losses[f], color=c, label=f"Lernrate {f:.2f} · 2/λ_max")
    ax.set_ylim(None, 1e3)
    ax.set_xlabel("Schritt")
    ax.set_ylabel("Verlust (mittlerer quadratischer Fehler / 2)")
    ax.set_title("Gradientenabstieg: dieselbe Grenze, 2/λ_max der Hesse-Matrix", fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()
    return g_max, eta_max
