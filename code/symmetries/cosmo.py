"""Isotropie des Universums für symmetries.ipynb: kosmische Varianz im Planck-Spektrum und der Alcock-Paczynski-Test mit DESI.

Daten: das Temperatur-Leistungsspektrum der Hintergrundstrahlung von Planck 2018 (Release 3, je Multipol ℓ mit Fehlern)
und das Spektrum des besten Modells, beide über IRSA (NASA/IPAC); die BAO-Messungen von DESI DR2 (Mittelwerte und
Kovarianz) aus dem öffentlichen GitHub-Repository CobayaSampler/bao_data. Alles mit requests und Cache.
"""
import time
from pathlib import Path

import numpy as np
import requests
import matplotlib.pyplot as plt
from scipy.integrate import quad
from scipy.stats import chi2 as chi2_dist

PLANCK = "https://irsa.ipac.caltech.edu/data/Planck/release_3/ancillary-data/cosmoparams/"
PLANCK_FILES = {"data": "COM_PowerSpect_CMB-TT-full_R3.01.txt",
                "theory": "COM_PowerSpect_CMB-base-plikHM-TTTEEE-lowl-lowE-lensing-minimum-theory_R3.01.txt"}
DESI = "https://raw.githubusercontent.com/CobayaSampler/bao_data/master/desi_bao_dr2/"
DESI_FILES = {"mean": "desi_gaussian_bao_ALL_GCcomb_mean.txt", "cov": "desi_gaussian_bao_ALL_GCcomb_cov.txt"}


def _get(url, path):
    path = Path(path)
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    for i in range(3):
        try:
            r = requests.get(url, timeout=120)
            if r.ok and not r.text.lstrip().startswith("<"):
                path.write_bytes(r.content)
                return path
        except requests.RequestException:
            pass
        time.sleep(3 * (i + 1))
    raise OSError(f"{url} nicht erreichbar")


# ---- Schritt 6: Planck und die kosmische Varianz

def planck(cache):
    """Gemessenes Spektrum (ℓ, D_ℓ, −Fehler, +Fehler) und Modell (ℓ, D_ℓ), beide in µK²."""
    d = np.loadtxt(_get(PLANCK + PLANCK_FILES["data"], Path(cache) / PLANCK_FILES["data"]))
    t = np.loadtxt(_get(PLANCK + PLANCK_FILES["theory"], Path(cache) / PLANCK_FILES["theory"]))
    return d, t[:, :2]


def plot_cosmic_variance(d, theory, fsky=0.6):
    """Links das Spektrum mit dem Band der kosmischen Varianz, rechts der relative Fehler gegen √(2/(2ℓ+1)).

    fsky: Anteil des Himmels, den die Messung nutzt (Planck blendet die Milchstraße aus); weniger Himmel heißt weniger
    unabhängige Werte und √(1/fsky) größere Streuung.
    """
    ell, D, lo, hi = d[:, 0], d[:, 1], d[:, 2], d[:, 3]
    Dt = np.interp(ell, theory[:, 0], theory[:, 1])
    cv = np.sqrt(2 / (2 * ell + 1))
    rel = 0.5 * (lo + hi) / Dt
    for L in [30, 100, 500, 1000, 1500, 2000]:
        k = int(np.argmin(np.abs(ell - L)))
        print(f"  ℓ = {L:4d}: {2 * L + 1:4d} Werte a_ℓm; relativer Fehler von Planck {rel[k]:.3f}, kosmische Varianz "
              f"{cv[k]:.3f} am ganzen Himmel, {cv[k] / np.sqrt(fsky):.3f} bei {fsky:.0%} des Himmels")
    ratio = D[0] / Dt[0]
    p = chi2_dist.cdf(5 * ratio, 5)
    print(f"  Quadrupol ℓ = 2: gemessen {D[0]:.0f} µK², Modell {Dt[0]:.0f} µK² (Verhältnis {ratio:.2f}); aus nur 5 Werten "
          f"streut er wie χ² mit 5 Freiheitsgraden, so klein oder kleiner in {p:.1%} der Fälle")
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    axes[0].fill_between(ell, Dt * (1 - cv), Dt * (1 + cv), color="tab:orange", alpha=0.35, label="kosmische Varianz um das Modell")
    axes[0].errorbar(ell[:30], D[:30], yerr=[lo[:30], hi[:30]], fmt="o", ms=3, color="black", lw=0.8, label="Planck 2018, ℓ < 32")
    axes[0].plot(ell[30:], D[30:], ".", ms=1, color="grey", alpha=0.5, label="Planck 2018, ℓ ≥ 32")
    axes[0].plot(ell, Dt, color="tab:red", lw=1.2, label="bestes Modell (ΛCDM)")
    axes[0].set_xscale("log")
    axes[0].set_xlim(2, 2500)
    axes[0].set_xlabel("Multipol ℓ (Winkel etwa 180°/ℓ)")
    axes[0].set_ylabel("D_ℓ = ℓ(ℓ+1)C_ℓ/2π [µK²]")
    axes[0].set_title("Temperaturspektrum der Hintergrundstrahlung", fontsize=10)
    axes[0].legend(fontsize=8, loc="upper left")
    m = ell >= 30
    axes[1].loglog(ell[m], rel[m], color="black", lw=0.8, label="relativer Fehler von Planck")
    axes[1].loglog(ell[m], cv[m], color="tab:orange", lw=2, label="kosmische Varianz √(2/(2ℓ+1)), ganzer Himmel")
    axes[1].loglog(ell[m], cv[m] / np.sqrt(fsky), color="tab:orange", lw=1, ls="--", label=f"dasselbe bei {fsky:.0%} des Himmels")
    axes[1].set_xlabel("Multipol ℓ")
    axes[1].set_ylabel("Fehler / Modell")
    axes[1].set_title("Bis ℓ ≈ 1000 begrenzt die Zahl der Moden, nicht das Instrument", fontsize=10)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()


# ---- Schritt 7: Alcock-Paczynski mit DESI

def desi(cache):
    """DESI DR2: Liste (z, Wert, Größe) und Kovarianz."""
    mean = np.loadtxt(_get(DESI + DESI_FILES["mean"], Path(cache) / DESI_FILES["mean"]), dtype=str)
    cov = np.loadtxt(_get(DESI + DESI_FILES["cov"], Path(cache) / DESI_FILES["cov"]))
    return mean, cov


def ap_data(mean, cov):
    """F_AP = D_M/D_H bei jeder Rotverschiebung mit beiden Größen; Kovarianz über die Ableitungen weitergegeben."""
    z = mean[:, 0].astype(float)
    val = mean[:, 1].astype(float)
    kind = mean[:, 2]
    zs = sorted(set(z[kind == "DM_over_rs"]) & set(z[kind == "DH_over_rs"]))
    J = np.zeros((len(zs), len(val)))
    F = np.zeros(len(zs))
    for k, zz in enumerate(zs):
        i = int(np.flatnonzero((z == zz) & (kind == "DM_over_rs"))[0])
        j = int(np.flatnonzero((z == zz) & (kind == "DH_over_rs"))[0])
        F[k] = val[i] / val[j]
        J[k, i] = 1 / val[j]
        J[k, j] = -val[i] / val[j] ** 2
    return np.array(zs), F, J @ cov @ J.T


def f_ap(z, om):
    """Flaches ΛCDM ohne Strahlung: F_AP = D_M/D_H = E(z) ∫₀^z dz'/E(z'); H₀ und das Lineal r_d fallen heraus."""
    E = lambda x: np.sqrt(om * (1 + x) ** 3 + 1 - om)
    return np.array([E(zz) * quad(lambda x: 1 / E(x), 0, zz)[0] for zz in np.atleast_1d(z)])


def plot_ap(zs, F, C, oms=np.linspace(0.15, 0.5, 351)):
    """Links F_AP/z gegen z mit Modellen, rechts χ² gegen Ω_m; das Minimum und das Intervall mit Δχ² = 1."""
    Ci = np.linalg.inv(C)
    chi2 = np.array([(F - f_ap(zs, om)) @ Ci @ (F - f_ap(zs, om)) for om in oms])
    k = int(np.argmin(chi2))
    inside = oms[chi2 <= chi2[k] + 1]
    om_best, lo, hi = oms[k], inside.min(), inside.max()
    print(f"DESI DR2: {len(zs)} Rotverschiebungen mit D_M und D_H, z = " + ", ".join(f"{x:.2f}" for x in zs))
    print(f"  Ω_m aus F_AP allein: {om_best:.3f} (−{om_best - lo:.3f}, +{hi - om_best:.3f}), χ² = {chi2[k]:.1f} bei "
          f"{len(zs) - 1} Freiheitsgraden; zum Vergleich Planck 2018: 0.315 ± 0.007")
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.6))
    zz = np.linspace(0.05, 2.6, 200)
    for om, c in [(0.2, "tab:green"), (om_best, "tab:red"), (0.4, "tab:purple")]:
        axes[0].plot(zz, f_ap(zz, om) / zz, color=c, lw=2 if om == om_best else 1, label=f"Ω_m = {om:.3f}")
    axes[0].errorbar(zs, F / zs, yerr=np.sqrt(np.diag(C)) / zs, fmt="o", color="black", ms=5, label="DESI DR2")
    axes[0].set_xlabel("Rotverschiebung z")
    axes[0].set_ylabel("F_AP / z = D_M / (z D_H)")
    axes[0].set_title("Alcock-Paczynski: Verhältnis quer zu längs der Sichtlinie", fontsize=10)
    axes[0].legend(fontsize=8)
    axes[1].plot(oms, chi2 - chi2[k], color="black")
    axes[1].axhline(1, color="grey", ls=":")
    axes[1].axvspan(lo, hi, color="tab:red", alpha=0.15, label=f"Ω_m = {om_best:.3f} (Δχ² < 1)")
    axes[1].set_ylim(0, 10)
    axes[1].set_xlabel("Materiedichte Ω_m")
    axes[1].set_ylabel("Δχ²")
    axes[1].set_title("Ω_m nur aus der Annahme, dass das Universum isotrop ist", fontsize=10)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()
    return om_best, lo, hi
