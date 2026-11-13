"""Pantheon+ für principal_axes.ipynb: die volle Kovarianz von Supernovae und warum sie den Fehler von H₀ bestimmt.

Daten: Pantheon+SH0ES (Scolnic und andere 2022, Brout und andere 2022, Riess und andere 2022) aus dem öffentlichen
GitHub-Repository PantheonPlusSH0ES/DataRelease: die Tabelle der 1701 Lichtkurven (`Pantheon+SH0ES.dat`, 0.6 MB) und die
volle Kovarianz aus Statistik und Systematik (`Pantheon+SH0ES_STAT+SYS.cov`, 33 MB), mit requests und Cache. Angepasst
werden die absolute Helligkeit M_B und H₀ aus 77 Kalibratoren (Entfernung aus Cepheiden) und 277 Supernovae im
Hubble-Fluss, mit verallgemeinerten kleinsten Quadraten, einmal mit voller Kovarianz und einmal nur mit ihrer Diagonale.
"""
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt

BASE = "https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/main/Pantheon%2B_Data/4_DISTANCES_AND_COVAR/"
FILES = {"Pantheon+SH0ES.dat": "Pantheon%2BSH0ES.dat", "Pantheon+SH0ES_STAT+SYS.cov": "Pantheon%2BSH0ES_STAT%2BSYS.cov"}
C_KMS = 299792.458
Q0, J0 = -0.55, 1.0                  # Abbremsung und Ruck für die Entfernung bei kleinem z (wie SH0ES)
PLANCK_H0, PLANCK_ERR = 67.4, 0.5    # Planck 2018, aus der Hintergrundstrahlung
SH0ES_H0, SH0ES_ERR = 73.04, 1.04    # Riess und andere 2022


def load(cache):
    """Tabelle und Kovarianz laden (Cache in `cache`); die Kovarianz wird symmetrisiert (Text auf 8 Stellen gerundet)."""
    cache = Path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    for name, url in FILES.items():
        path = cache / name
        for i in range(3):
            if path.exists():
                break
            try:
                r = requests.get(BASE + url, timeout=300)
                if r.ok and r.content[:1] in (b"C", b"1"):            # Tabelle beginnt mit "CID", Kovarianz mit "1701"
                    path.write_bytes(r.content)
            except requests.RequestException:
                time.sleep(3 * (i + 1))
    sn = pd.read_csv(cache / "Pantheon+SH0ES.dat", sep=r"\s+")
    n = len(sn)
    cov = np.loadtxt(cache / "Pantheon+SH0ES_STAT+SYS.cov", skiprows=1).reshape(n, n)
    print(f"Pantheon+SH0ES: {n} Lichtkurven, Kovarianz {n} × {n}")
    return sn, (cov + cov.T) / 2


def design(sn):
    """Auswahl (Kalibratoren und Hubble-Fluss), Messwerte y und Matrix X für die Parameter M_B und a = 5 log10 H₀.

    Kalibratoren: m = M_B + μ(Cepheiden). Hubble-Fluss: m = M_B + 5 log10(c z f(z) / H₀) + 25, f aus Q0 und J0.
    """
    cal = sn["IS_CALIBRATOR"].values == 1
    idx = np.flatnonzero(cal | (sn["USED_IN_SH0ES_HF"].values == 1))
    z, zh = sn["zHD"].values, sn["zHEL"].values
    f = (1 + 0.5 * (1 - Q0) * z - (1 - Q0 - 3 * Q0 ** 2 + J0) * z ** 2 / 6) * (1 + zh) / (1 + z)
    y = sn["m_b_corr"].values[idx].copy()
    X = np.zeros((len(idx), 2))
    X[:, 0] = 1
    for k, i in enumerate(idx):
        if cal[i]:
            y[k] -= sn["CEPH_DIST"].values[i]
        else:
            y[k] -= 5 * np.log10(C_KMS * z[i] * f[i]) + 25
            X[k, 1] = -1
    return idx, cal[idx], y, X


def gls(y, X, C):
    """Verallgemeinerte kleinste Quadrate: θ = (Xᵀ C⁻¹ X)⁻¹ Xᵀ C⁻¹ y. Gibt M_B, σ(M_B), H₀, σ(H₀)."""
    Ci = np.linalg.inv(C)
    F = X.T @ Ci @ X
    th = np.linalg.solve(F, X.T @ Ci @ y)
    cov = np.linalg.inv(F)
    h0 = 10 ** (th[1] / 5)
    return th[0], np.sqrt(cov[0, 0]), h0, h0 * np.log(10) / 5 * np.sqrt(cov[1, 1])


def study(sn, cov, n_axes=40):
    """Korrelationen, Hauptachsen der Korrelationsmatrix, H₀ mit voller Kovarianz und nur mit der Diagonale."""
    idx, iscal, y, X = design(sn)
    C = cov[np.ix_(idx, idx)]
    sd = np.sqrt(np.diag(C))
    R = C / np.outer(sd, sd)
    survey = sn["IDSURVEY"].values[idx]
    off = ~np.eye(len(idx), dtype=bool)
    same = (survey[:, None] == survey[None, :]) & off
    cc = R[np.ix_(iscal, iscal)][~np.eye(iscal.sum(), dtype=bool)]
    print(f"{iscal.sum()} Kalibratoren und {(~iscal).sum()} Supernovae im Hubble-Fluss, Kovarianz {len(idx)} × {len(idx)}")
    print(f"Mittlere Korrelation zweier Supernovae: alle {R[off].mean():.3f}, gleiche Durchmusterung {R[same].mean():.3f} "
          f"({same.sum() // 2} Paare), Kalibratoren untereinander {cc.mean():.3f}")
    for name, m in [("Kalibratoren", iscal), ("Hubble-Fluss", ~iscal)]:
        w = np.ones(m.sum()) / m.sum()
        full = np.sqrt(w @ C[np.ix_(m, m)] @ w)
        diag = np.sqrt(w @ np.diag(np.diag(C[np.ix_(m, m)])) @ w)
        print(f"  Mittelwert der {m.sum()} {name}: σ = {full:.4f} mag mit Korrelationen, {diag:.4f} ohne "
              f"(Faktor {full / diag:.2f})")
    ev, V = np.linalg.eigh(R)
    ev, V = ev[::-1], V[:, ::-1]
    pr = 1 / np.sum(V ** 4, axis=0)
    print("Oberste Eigenwerte der Korrelationsmatrix (ohne Korrelation alle 1): "
          + ", ".join(f"{e:.1f}" for e in ev[:4]) + "; getragen von " + ", ".join(f"{p:.0f}" for p in pr[:4]) + " Supernovae")
    res = {}
    for name, Cm in [("volle Kovarianz", C), ("nur Diagonale", np.diag(np.diag(C)))]:
        M, dM, h0, dh0 = gls(y, X, Cm)
        sigma = (h0 - PLANCK_H0) / np.hypot(dh0, PLANCK_ERR)
        res[name] = (h0, dh0)
        print(f"  {name:16s} M_B = {M:.3f} ± {dM:.3f},  H₀ = {h0:.2f} ± {dh0:.2f} km/s/Mpc,  Abstand zu Planck {sigma:.1f}σ")
    order = np.lexsort((survey, ~iscal))                                    # erst Kalibratoren, dann nach Durchmusterung
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8), gridspec_kw={"width_ratios": [1.05, 1, 0.8]})
    im = axes[0].imshow(R[np.ix_(order, order)], cmap="RdBu_r", vmin=-0.15, vmax=0.15, interpolation="nearest")
    k = iscal.sum()
    for a in (axes[0].axhline, axes[0].axvline):
        a(k - 0.5, color="black", lw=0.8)
    axes[0].set_title("Korrelationsmatrix (Kalibratoren oben links,\nHubble-Fluss nach Durchmusterung sortiert)", fontsize=10)
    axes[0].set_xlabel("Supernova")
    axes[0].set_ylabel("Supernova")
    fig.colorbar(im, ax=axes[0], fraction=0.046)
    r = np.arange(1, n_axes + 1)
    axes[1].semilogy(r, ev[:n_axes], "o-", ms=4, color="black")
    axes[1].axhline(1, color="tab:blue", ls="--", label="ohne Korrelationen: alle Eigenwerte 1")
    for i in range(2):
        axes[1].annotate(f"{pr[i]:.0f} Supernovae", (r[i], ev[i]), xytext=(8, -4), textcoords="offset points", fontsize=8)
    axes[1].set_xlabel("Rang der Achse")
    axes[1].set_ylabel("Eigenwert der Korrelationsmatrix")
    axes[1].set_title("Gemeinsame Achsen: die Eichung der Durchmusterungen", fontsize=10)
    axes[1].legend(fontsize=8)
    labels = list(res) + ["SH0ES 2022", "Planck 2018"]
    vals = list(res.values()) + [(SH0ES_H0, SH0ES_ERR), (PLANCK_H0, PLANCK_ERR)]
    colors = ["tab:red", "tab:orange", "grey", "tab:blue"]
    for j, ((h, e), c) in enumerate(zip(vals, colors)):
        axes[2].errorbar(h, j, xerr=e, fmt="o", color=c, capsize=4)
    axes[2].set_yticks(range(len(labels)), labels)
    axes[2].invert_yaxis()
    axes[2].set_xlabel("H₀ [km/s/Mpc]")
    axes[2].set_title("H₀: gleicher Wert, verschiedener Fehler", fontsize=10)
    fig.tight_layout()
    plt.show()
    return res
