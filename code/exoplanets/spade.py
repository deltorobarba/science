"""Superauflösung mit SPADE für exoplanets.ipynb: Hermite-Gauß-Moden, Fisher-Information von Kamera und Modenzählung,
Schätzung eines Abstands aus Photonen, Nachweis eines schwachen Planeten neben dem Stern (Huang und Lupo 2021) und wie
viele bekannte Planeten unter der Beugungsgrenze liegen.

Modell: eine Dimension, gaußsche Punktbildfunktion mit Breite σ = 1. Daten: große Halbachse und Entfernung aller
bestätigten Planeten aus der Tabelle pscomppars des NASA Exoplanet Archive.
"""
from math import factorial

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar

import archive

x = np.linspace(-12, 12, 20001)              # Ort auf dem Detektor [σ]
dx = x[1] - x[0]
gauss = lambda u: np.exp(-u ** 2 / 2) / np.sqrt(2 * np.pi)
p0 = gauss(x)                                # Stern allein, auf der Achse
I_Q = 0.25                                   # Quanten-Fisher-Information 1/(4σ²)


def hg_probs(x0, q_max=30):
    """Wahrscheinlichkeit, dass ein Photon einer Quelle bei x0 in Mode q landet: e^-Q Q^q / q!, Q = x0²/4."""
    Q = x0 ** 2 / 4
    q = np.arange(q_max)
    return np.exp(-Q) * Q ** q / np.array([factorial(k) for k in q], dtype=float)


def fisher_camera(theta):
    """Fisher-Information pro Photon der Kamera, zwei gleich helle Quellen bei ±theta/2 (numerisches Integral)."""
    p = 0.5 * (gauss(x - theta / 2) + gauss(x + theta / 2))
    dp = 0.25 * ((x - theta / 2) * gauss(x - theta / 2) - (x + theta / 2) * gauss(x + theta / 2))
    return np.sum(dp ** 2 / np.maximum(p, 1e-300)) * dx


def fisher_spade(theta, crosstalk=0.0, h=1e-5):
    """Fisher-Information pro Photon der Modenzählung; crosstalk = Anteil der Mode-0-Photonen, der in Mode 1 landet."""
    def probs(t):
        P = hg_probs(t / 2)                      # beide Quellen haben dieselbe Modenstatistik
        return np.r_[P[0] * (1 - crosstalk), P[1] + P[0] * crosstalk, P[2:]]
    lo = max(theta - h, 0)
    p, dp = probs(theta), (probs(theta + h) - probs(lo)) / (theta + h - lo)
    return np.sum(dp[p > 0] ** 2 / p[p > 0])


def D_camera(eps, theta):
    """Fehlerexponent pro Photon der Kamera: D(p0 || p1), p1 = (1 - eps) p0 + eps p_theta (numerisch)."""
    return -np.sum(p0 * np.log1p(eps * np.expm1((2 * x * theta - theta ** 2) / 2))) * dx


def D_spade(eps, theta, crosstalk=0.0):
    """SPADE auf den Lichtschwerpunkt ausgerichtet (Stern bei -eps·theta, Planet bei (1 - eps)·theta).
    Ergebnis 'Mode 0' gegen 'andere Mode'; crosstalk = Anteil der Mode-0-Photonen, der in andere Moden gelangt."""
    p1_mode0 = (1 - eps) * hg_probs(-eps * theta)[0] + eps * hg_probs((1 - eps) * theta)[0]
    a0, a1 = 1 - crosstalk, (1 - crosstalk) * p1_mode0          # Wahrscheinlichkeit für 'Mode 0' unter H0 und H1
    return a0 * np.log(a0 / a1) + ((1 - a0) * np.log((1 - a0) / (1 - a1)) if crosstalk > 0 else 0.0)


def plot_modes(theta_max=3.0):
    """Besetzung der ersten fünf Hermite-Gauß-Moden gegen den Abstand zweier Quellen."""
    thetas = np.linspace(0, theta_max, 200)
    P = np.array([hg_probs(t / 2, q_max=6) for t in thetas])
    fig, ax = plt.subplots(figsize=(9, 4.5))
    for q, c in zip(range(5), ["black", "tab:blue", "tab:orange", "tab:green", "tab:red"]):
        ax.plot(thetas, P[:, q], lw=2, c=c, label=f"Mode q = {q}")
    ax.plot(thetas, thetas ** 2 / 16, c="tab:blue", ls=":", label="θ²/16σ² (Näherung für Mode 1)")
    ax.set_xlabel("Abstand der Quellen θ / σ")
    ax.set_ylabel("Wahrscheinlichkeit P(q)")
    ax.set_ylim(0, 1.02)
    ax.set_title("Besetzung der Hermite-Gauß-Moden")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9)
    fig.tight_layout()
    plt.show()
    print(f"θ = 0.2σ: P(0) = {hg_probs(0.1)[0]:.5f}, P(1) = {hg_probs(0.1)[1]:.5f} (θ²/16σ² = {0.2 ** 2 / 16:.5f})")


def plot_fisher(crosstalk=1e-3):
    """Fisher-Information pro Photon: Kamera gegen SPADE, mit und ohne Übersprechen."""
    theta_grid = np.logspace(-2, np.log10(5), 60)
    F_cam = np.array([fisher_camera(t) for t in theta_grid])
    F_sp = np.array([fisher_spade(t) for t in theta_grid])
    F_ct = np.array([fisher_spade(t, crosstalk) for t in theta_grid])

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.loglog(theta_grid, F_sp / I_Q, c="tab:green", lw=2.5, label="SPADE (Hermite-Gauß-Moden)")
    ax.loglog(theta_grid, F_ct / I_Q, c="tab:green", ls="-.", label=f"SPADE mit Übersprechen {crosstalk:g}")
    ax.loglog(theta_grid, F_cam / I_Q, c="tab:red", ls="--", lw=2, label="Kamera")
    ax.loglog(theta_grid, theta_grid ** 2 / 8 / I_Q, c="tab:red", ls=":", lw=1, label="θ²/8σ⁴ (Näherung für kleine θ)")
    ax.axhline(1, color="black", ls=":", label="Quanten-Fisher-Information 1/(4σ²)")
    ax.set_ylim(1e-5, 2)
    ax.set_xlabel("Abstand θ / σ")
    ax.set_ylabel("Fisher-Information pro Photon / (1/4σ²)")
    ax.set_title("Rayleighs Fluch: Kamera gegen SPADE")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    plt.show()

    for t in [0.05, 0.2, 1.0]:
        print(f"θ = {t:4.2f}σ:  Kamera {fisher_camera(t) / I_Q:.2e}  (Formel θ²/8: {t ** 2 / 8 / I_Q:.2e}),  "
              f"SPADE {fisher_spade(t) / I_Q:.3f},  SPADE mit Übersprechen {fisher_spade(t, crosstalk) / I_Q:.3f}   [in Einheiten von 1/4σ²]")


def estimate(n_phot=10_000, theta_true=0.2, n_rep=200, seed=3):
    """Maximum-Likelihood-Schätzung des Abstands aus n_phot Photonen, n_rep-mal wiederholt, Kamera gegen SPADE."""
    rng = np.random.default_rng(seed)
    est_cam, est_sp = [], []
    for _ in range(n_rep):
        pos = rng.normal(0, 1, n_phot) + rng.choice([-theta_true / 2, theta_true / 2], n_phot)
        nll = lambda t: -np.sum(np.log(0.5 * (np.exp(-(pos - t / 2) ** 2 / 2) + np.exp(-(pos + t / 2) ** 2 / 2))))
        est_cam.append(minimize_scalar(nll, bounds=(0, 2), method="bounded").x)
        q = rng.poisson(theta_true ** 2 / 16, n_phot)
        est_sp.append(4 * np.sqrt(q.mean()))
    est_cam, est_sp = np.array(est_cam), np.array(est_sp)
    rmse = lambda e: np.sqrt(np.mean((e - theta_true) ** 2))
    crb_cam = 1 / np.sqrt(n_phot * fisher_camera(theta_true))
    crb_sp = 1 / np.sqrt(n_phot * fisher_spade(theta_true))

    fig, ax = plt.subplots(figsize=(9, 4.5))
    bins = np.linspace(0, 0.6, 61)
    ax.hist(est_cam, bins=bins, alpha=0.6, color="tab:red", label=f"Kamera: RMSE {rmse(est_cam):.3f}σ")
    ax.hist(est_sp, bins=bins, alpha=0.6, color="tab:green", label=f"SPADE: RMSE {rmse(est_sp):.3f}σ")
    ax.axvline(theta_true, color="black", lw=1, label=f"wahrer Abstand {theta_true}σ")
    ax.set_xlabel("geschätzter Abstand θ̂ / σ")
    ax.set_ylabel(f"Anzahl ({n_rep} Wiederholungen)")
    ax.set_title(f"Maximum-Likelihood-Schätzung aus je {n_phot:,} Photonen")
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()

    print(f"Kamera: RMSE {rmse(est_cam):.3f}σ, Cramér-Rao-Schranke {crb_cam:.3f}σ; "
          f"{np.mean(est_cam < 1e-3):.0%} der Schätzungen bleiben bei θ̂ = 0 hängen")
    print(f"SPADE:  RMSE {rmse(est_sp):.3f}σ, Cramér-Rao-Schranke {crb_sp:.3f}σ, Quantengrenze {1 / np.sqrt(n_phot * I_Q):.3f}σ")


def detect(eps_list=(1e-2, 1e-4), crosstalk=1e-3, theta_show=0.3):
    """Fehlerexponent für den Nachweis eines Planeten mit Helligkeitsanteil eps neben dem Stern."""
    th = np.logspace(-2, 0.7, 60)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for eps, c in zip(eps_list, ["tab:blue", "tab:red", "tab:green", "tab:purple"]):
        ax.loglog(th, [D_camera(eps, t) for t in th], c=c, ls="--", label=f"Kamera, ε = {eps:g}")
        ax.loglog(th, [D_spade(eps, t) for t in th], c=c, lw=2, label=f"SPADE, ε = {eps:g}")
        ax.loglog(th, [D_spade(eps, t, crosstalk) for t in th], c=c, lw=1, ls="-.", label=f"SPADE mit Übersprechen {crosstalk:g}, ε = {eps:g}")
        ax.loglog(th, eps * (1 - np.exp(-th ** 2 / 4)), c="black", lw=0.8, ls=":",
                  label="Quantengrenze ε(1 − e^(−θ²/4σ²)), führende Ordnung" if eps == eps_list[0] else None)
    ax.set_xlabel("Abstand Stern–Planet θ / σ")
    ax.set_ylabel("Fehlerexponent pro Photon D(p0‖p1)")
    ax.set_ylim(1e-14, 1e-1)
    ax.set_title("Nachweis eines schwachen Planeten (Huang & Lupo 2021)")
    ax.legend(fontsize=7, loc="lower right")
    fig.tight_layout()
    plt.show()

    print(f"Bei θ = {theta_show}σ (Photonen für 99.9 % Nachweissicherheit ≈ ln(1000)/D):")
    for eps in eps_list:
        d_c, d_s, d_x = D_camera(eps, theta_show), D_spade(eps, theta_show), D_spade(eps, theta_show, crosstalk)
        print(f"  ε = {eps:g}:  Kamera {np.log(1e3) / d_c:.1e},  SPADE {np.log(1e3) / d_s:.1e},  "
              f"SPADE mit Übersprechen {np.log(1e3) / d_x:.1e} Photonen;  Gewinn von SPADE {d_s / d_c:.0f}-fach "
              f"(Näherung 1/(2ε) = {1 / (2 * eps):.0f})")


def known_planets(lambda_um=1.6, telescopes={"8 m (VLT)": 8.0, "39 m (ELT)": 39.0}):
    """Größter Winkelabstand a/d aller bekannten Planeten in Einheiten der Beugungsgrenze λ/D."""
    ang = archive.query("pscomppars", select="pl_name, pl_orbsmax, sy_dist")
    ang = ang.dropna(subset=["pl_orbsmax", "sy_dist"])
    ang["sep_mas"] = ang["pl_orbsmax"] / ang["sy_dist"] * 1000

    fig, ax = plt.subplots(figsize=(10, 5))
    for (name, D_m), c in zip(telescopes.items(), ["tab:blue", "tab:purple", "tab:green"]):
        lod_mas = lambda_um * 1e-6 / D_m * 206265e3
        ax.hist(ang["sep_mas"] / lod_mas, bins=np.logspace(-4, 4, 70), histtype="step", lw=1.5, color=c,
                label=f"{name}: λ/D = {lod_mas:.1f} mas")
    ax.axvspan(1e-4, 1, color="red", alpha=0.1, label="unter λ/D")
    ax.axvline(3, color="grey", ls=":", label="typischer innerer Arbeitswinkel eines Koronographen (~3 λ/D)")
    ax.set_xscale("log")
    ax.set_xlabel(f"größter Abstand Stern–Planet a/d [λ/D bei {lambda_um} µm]")
    ax.set_ylabel("Anzahl bekannter Planeten")
    ax.set_title(f"Bekannte Planeten relativ zur Beugungsgrenze ({len(ang)} mit a und d)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()

    for name, D_m in telescopes.items():
        lod_mas = lambda_um * 1e-6 / D_m * 206265e3
        r = ang["sep_mas"] / lod_mas
        print(f"{name:11s} λ/D = {lod_mas:4.1f} mas:  {(r < 1).sum()} Planeten unter λ/D ({(r < 1).mean():.0%}), "
              f"{(r < 3).sum()} unter 3 λ/D ({(r < 3).mean():.0%})")
