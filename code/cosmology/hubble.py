"""Das Hubble-Diagramm aus Pantheon+: Kovarianz, Kalibratoren, Hubble-Fluss, H0, Ω_m, Beschleunigung und die Hubble-Spannung.

Für cosmology.ipynb aus cosmology_hubblediagram.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, catalog, hubble_diagram, redshifts, covariance, calibrators, hubble_flow, h0_joint, omega_m, acceleration, diag_vs_full, hubble_tension, vs_pantheon.
Downloads und Cache: data/cosmology/ (`cosmodata.py`).
"""
import cosmodata                                      # zuerst: Cache-Ordner für astropy
import os
import urllib.request
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import optimize, stats


def load():
    """1. Daten (Zellen 4, 6 von cosmology_hubblediagram.ipynb)."""
    global ASTRODATA, ASYM, BASE, CAL, COV, C_KMS, HF, LIT, N, OM_FIX, PANTHEON, SN
    global Z_HF, Z_MIN_COSMO, comoving, cov_path, download, gls, hessian, mu_model, offset_chi2, subcov
    ASTRODATA = cosmodata.DATA


    C_KMS = 299792.458                 # Lichtgeschwindigkeit [km/s]
    OM_FIX = 0.334                     # Ω_m, wenn es für H₀ festgehalten wird (Brout et al. 2022) (Schritt 8)
    Z_HF = (0.0233, 0.15)              # Hubble-Fluss wie bei SH0ES: weit genug für kleine Eigenbewegungen, nah genug für q₀ (Schritt 7)
    Z_MIN_COSMO = 0.01                 # untere Grenze für den Fit von Ω_m (Schritt 9)
    LIT = {"H0_SH0ES": (73.04, 1.04),  # Riess et al. 2022 (volle Entfernungsleiter)
           "H0_Brout": (73.5, 1.1),    # Brout et al. 2022 (Pantheon+ und SH0ES)
           "H0_Planck": (67.4, 0.5),   # Planck 2018 VI, ΛCDM aus der Hintergrundstrahlung
           "M_SH0ES": (-19.253, 0.027),
           "Om_Brout": (0.334, 0.018), "Om_Planck": (0.315, 0.007)}
    pd.set_option("display.width", 160)
    PANTHEON = ASTRODATA / "pantheon"
    BASE = "https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/main/Pantheon%2B_Data/4_DISTANCES_AND_COVAR/"


    def download(url, path, check=None, timeout=300):
        path = Path(path)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            with urllib.request.urlopen(url, timeout=timeout) as r:
                data = r.read()
            if check is not None and not check(data):
                raise OSError(f"{path.name}: unerwarteter Inhalt")
            path.write_bytes(data)
        return path


    SN = pd.read_csv(download(BASE + "Pantheon%2BSH0ES.dat", PANTHEON / "Pantheon+SH0ES.dat", lambda d: d.startswith(b"CID")),
                     sep=r"\s+")
    cov_path = download(BASE + "Pantheon%2BSH0ES_STAT%2BSYS.cov", PANTHEON / "Pantheon+SH0ES_STAT+SYS.cov",
                        lambda d: d.split(b"\n", 1)[0].strip() == b"1701")
    N = len(SN)
    COV = np.loadtxt(cov_path, skiprows=1).reshape(N, N)
    ASYM = np.abs(COV - COV.T).max()
    COV = (COV + COV.T) / 2                              # die Textdatei ist auf 8 Stellen gerundet
    CAL = SN["IS_CALIBRATOR"].values == 1
    HF = SN["USED_IN_SH0ES_HF"].values == 1
    print(f"{N} Lichtkurven von {SN['CID'].nunique()} Supernovae aus {SN['IDSURVEY'].nunique()} Durchmusterungen; "
          f"z von {SN['zHD'].min():.4f} bis {SN['zHD'].max():.2f}")
    print(f"Kalibratoren: {CAL.sum()} Lichtkurven von {SN.loc[CAL, 'CID'].nunique()} Supernovae; "
          f"Hubble-Fluss (SH0ES): {HF.sum()} Lichtkurven, z = {SN.loc[HF, 'zHD'].min():.4f} bis {SN.loc[HF, 'zHD'].max():.4f}")
    print(f"Kovarianz: {COV.shape}, größte Asymmetrie vor dem Symmetrisieren {ASYM:.0e} mag², kleinster Eigenwert {np.linalg.eigvalsh(COV).min():.2e}")

    def comoving(z, Om, Ol, n=6000):
        # mitbewegte Entfernung in Einheiten von c/H₀ für ein FLRW-Universum, Integral über 1/E(z)
        zz = np.linspace(0, max(np.max(z), 2.5), n)
        Ok = 1 - Om - Ol
        E = np.sqrt(np.clip(Om * (1 + zz) ** 3 + Ok * (1 + zz) ** 2 + Ol, 1e-12, None))
        I = np.concatenate([[0], np.cumsum((1 / E[1:] + 1 / E[:-1]) / 2 * np.diff(zz))])
        dc = np.interp(z, zz, I)
        if abs(Ok) < 1e-8:
            return dc
        s = np.sqrt(abs(Ok))
        return np.sinh(s * dc) / s if Ok > 0 else np.sin(s * dc) / s     # offene oder geschlossene Geometrie


    def mu_model(z, H0, Om, Ol=None, zhel=None):
        # Entfernungsmodul μ = 5 log₁₀(d_L / 10 pc); d_L = (1 + z_hel) · c/H₀ · D_M(z)
        Ol = 1 - Om if Ol is None else Ol
        zhel = z if zhel is None else zhel
        dl_mpc = (1 + zhel) * C_KMS / H0 * comoving(z, Om, Ol)
        return 5 * np.log10(dl_mpc) + 25


    def subcov(idx):
        return COV[np.ix_(idx, idx)]


    def gls(y, X, cov):
        # verallgemeinerte kleinste Quadrate: β = (Xᵀ C⁻¹ X)⁻¹ Xᵀ C⁻¹ y, Kovarianz (Xᵀ C⁻¹ X)⁻¹
        Ci = np.linalg.inv(cov)
        F = X.T @ Ci @ X
        beta = np.linalg.solve(F, X.T @ Ci @ y)
        r = y - X @ beta
        return beta, np.linalg.inv(F), r @ Ci @ r


    def offset_chi2(resid, Ci):
        # χ² minimiert über eine additive Konstante b: b = (1ᵀ C⁻¹ r) / (1ᵀ C⁻¹ 1)
        one = np.ones(len(resid))
        b = (one @ Ci @ resid) / (one @ Ci @ one)
        r = resid - b
        return r @ Ci @ r, b


    def hessian(f, x, h=1e-3):
        n = len(x)
        H = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                e1, e2 = np.eye(n)[i] * h, np.eye(n)[j] * h
                H[i, j] = (f(x + e1 + e2) - f(x + e1 - e2) - f(x - e1 + e2) + f(x - e1 - e2)) / (4 * h * h)
        return H


    print("Test: μ(z = 0.1, H₀ = 70, Ω_m = 0.3) =", round(float(mu_model(np.array([0.1]), 70, 0.3)[0]), 3),
          "| leeres Universum:", round(float(mu_model(np.array([0.1]), 70, 0.0, 0.0)[0]), 3))


def catalog():
    """2. Der Katalog (Zellen 8 von cosmology_hubblediagram.ipynb)."""
    global ax, bins, col, dup, fig, g, grp, ra, sc
    grp = np.where(CAL, "Kalibratoren (Cepheiden)", np.where(HF, "Hubble-Fluss (SH0ES)", "übrige"))
    fig = plt.figure(figsize=(16, 5.5))
    ax = fig.add_subplot(1, 2, 1)
    bins = np.logspace(-3.2, 0.4, 50)
    for g, col in [("übrige", "0.6"), ("Hubble-Fluss (SH0ES)", "C0"), ("Kalibratoren (Cepheiden)", "C3")]:
        ax.hist(SN.loc[grp == g, "zHD"], bins=bins, color=col, alpha=0.8, label=f"{g} ({(grp == g).sum()})")
    ax.set_xscale("log")
    ax.set_xlabel("Rotverschiebung z")
    ax.set_ylabel("Zahl der Lichtkurven")
    ax.set_title(f"{N} Lichtkurven, {SN['CID'].nunique()} Supernovae", fontsize=10)
    ax.legend(fontsize=9)
    ax = fig.add_subplot(1, 2, 2, projection="mollweide")
    ra = np.radians(SN["RA"].values)
    ra = np.where(ra > np.pi, ra - 2 * np.pi, ra)
    sc = ax.scatter(-ra, np.radians(SN["DEC"]), c=np.log10(SN["zHD"]), s=4, cmap="viridis")
    plt.colorbar(sc, ax=ax, shrink=0.6, label="log₁₀ z")
    ax.grid(alpha=0.3)
    ax.set_xticklabels([f"{int(((-x) % 360) / 15)}h" for x in range(-150, 151, 30)], fontsize=8)
    ax.set_title("Lage am Himmel (äquatorial, Rektaszension nach links)", fontsize=10, pad=18)
    plt.tight_layout()
    plt.show()

    dup = SN["CID"].value_counts()
    print(f"Lichtkurven pro Supernova: 1 bei {np.sum(dup == 1)}, 2 bei {np.sum(dup == 2)}, 3 oder mehr bei {np.sum(dup >= 3)}")
    print(f"Median z: alle {SN['zHD'].median():.3f}, z < 0.1: {np.mean(SN['zHD'] < 0.1):.0%}, z > 1: {np.sum(SN['zHD'] > 1)} Lichtkurven")
    print("Kalibratoren:", ", ".join(sorted(SN.loc[CAL, "CID"].unique())[:12]), "...")


def hubble_diagram():
    """3. Das Hubble-Diagramm (Zellen 11 von cosmology_hubblediagram.ipynb)."""
    global H0, M0, Ol, Om, ax, axes, base, col, empty, err, fig, hi
    global idx, lab, m, mb, off, res, sel, z, zb, ze, zhel, zz
    z, zhel, mb = SN["zHD"].values, SN["zHEL"].values, SN["m_b_corr"].values
    err = SN["m_b_corr_err_DIAG"].values
    M0 = -19.25
    zz = np.logspace(-3, 0.4, 300)
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
    ax = axes[0]
    ax.errorbar(z[~CAL], mb[~CAL], yerr=err[~CAL], fmt=".", ms=2, color="0.5", alpha=0.4, elinewidth=0.5)
    ax.plot(z[CAL], mb[CAL], "o", color="C3", ms=4, label="Kalibratoren")
    for H0, col in [(67.4, "C1"), (73.0, "C0")]:
        ax.plot(zz, M0 + 5 * np.log10(C_KMS * zz / H0) + 25, color=col, label=f"d = cz/H₀, H₀ = {H0}")
    ax.set_xscale("log")
    ax.set_xlabel("Rotverschiebung z")
    ax.set_ylabel("m_b_corr [mag]")
    ax.set_title("Helligkeit gegen Rotverschiebung", fontsize=10)
    ax.legend(fontsize=9)
    ax = axes[1]
    empty = mu_model(z, 70, 0.0, 0.0, zhel)
    sel = z > Z_MIN_COSMO
    res = mb - empty
    off = np.median(res[sel & (z < 0.1)])
    zb = np.logspace(-2, 0.35, 15)
    idx = np.digitize(z, zb)
    ax.plot(z[sel], res[sel] - off, ".", ms=2, color="0.6", alpha=0.5)
    ax.errorbar([np.median(z[idx == k]) for k in range(1, len(zb)) if (idx == k).sum() > 4],
                [np.median(res[idx == k] - off) for k in range(1, len(zb)) if (idx == k).sum() > 4],
                fmt="ko", ms=5, label="Median in Intervallen")
    ze = np.logspace(-2, 0.35, 200)
    base = mu_model(ze, 70, 0.0, 0.0)
    for (Om, Ol), col, lab in [((1.0, 0.0), "C1", "nur Materie (Ω_m = 1)"), ((0.3, 0.7), "C0", "ΛCDM (Ω_m = 0.3, Ω_Λ = 0.7)")]:
        m = mu_model(ze, 70, Om, Ol)
        ax.plot(ze, m - base - np.interp(0.03, ze, m - base), color=col, label=lab)
    ax.axhline(0, color="k", lw=1, label="leeres Universum")
    ax.set_xscale("log")
    ax.set_ylim(-1.0, 0.6)
    ax.set_xlabel("Rotverschiebung z")
    ax.set_ylabel("Δμ gegen leeres Universum [mag]")
    ax.set_title("Weiter weg ist es heller als ohne Beschleunigung", fontsize=10)
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    hi = (z > 0.4) & (z < 0.8)
    print(f"Streuung um eine Gerade im Hubble-Fluss (0.023 < z < 0.15): {np.std(mb[HF] - (5 * np.log10(z[HF]))):.3f} mag; "
          f"typischer Fehler pro Lichtkurve {np.median(err):.3f} mag")
    print(f"Abweichung vom leeren Universum bei 0.4 < z < 0.8 (Median, auf z ≈ 0.03 normiert): {np.median(res[hi] - off):+.3f} mag")


def redshifts():
    """4. Rotverschiebungen und Eigenbewegungen (Zellen 14 von cosmology_hubblediagram.ipynb)."""
    global ax, axes, dmu, dz_cmb, dz_pec, fig, hi, lo, m, v, zz
    dz_cmb = SN["zCMB"] - SN["zHEL"]
    dz_pec = SN["zHD"] - SN["zCMB"]
    dmu = 5 * np.log10(SN["zHD"] / SN["zCMB"])
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    ax = axes[0]
    ax.scatter(SN["zHD"], C_KMS * dz_cmb, s=3, label="zCMB − zHEL (Bewegung der Sonne)")
    ax.scatter(SN["zHD"], C_KMS * dz_pec, s=3, label="zHD − zCMB (Eigenbewegung der Galaxie)")
    ax.set_xscale("log")
    ax.set_xlabel("z")
    ax.set_ylabel("Unterschied × c [km/s]")
    ax.set_title("Korrekturen der Rotverschiebung", fontsize=10)
    ax.legend(fontsize=9, markerscale=3)
    ax = axes[1]
    ax.scatter(SN["zHD"], dmu, s=3, c="C1")
    zz = np.logspace(np.log10(0.0025), -0.5, 100)                   # erst ab cz > 300 km/s ist 1 − 300/cz positiv
    for v in (300, -300):
        ax.plot(zz, 5 * np.log10(1 + v / (C_KMS * zz)), "k:", lw=1)
    ax.axvline(Z_HF[0], color="C0", ls="--", label=f"untere Grenze des Hubble-Flusses (z = {Z_HF[0]})")
    ax.set_xscale("log")
    ax.set_ylim(-0.5, 0.5)
    ax.set_xlabel("z")
    ax.set_ylabel("Δμ = 5 log₁₀(zHD / zCMB) [mag]")
    ax.set_title("Was die Eigenbewegung im Entfernungsmodul ausmacht; punktiert: ±300 km/s", fontsize=10)
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    for lo, hi in [(0, 0.01), (0.01, 0.0233), (0.0233, 0.15), (0.15, 3)]:
        m = (SN["zHD"] >= lo) & (SN["zHD"] < hi)
        print(f"z {lo:6.4f} bis {hi:<6}: {m.sum():4d} Lichtkurven, |zHD − zCMB|·c Median {np.median(np.abs(C_KMS * dz_pec[m])):5.0f} km/s, "
              f"|Δμ| Median {np.median(np.abs(dmu[m])):.3f} mag")
    print(f"VPECERR: Median {SN['VPECERR'].median():.0f} km/s")


def covariance():
    """5. Die Kovarianzmatrix (Zellen 17 von cosmology_hubblediagram.ipynb)."""
    global CORR, ax, axes, dups, fig, im, iu, lam, near300, off_diag, order, rho_dup
    global sd, w
    order = np.argsort(SN["zHD"].values)
    sd = np.sqrt(np.diag(COV))
    CORR = COV / np.outer(sd, sd)
    lam = np.linalg.eigvalsh(COV)[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    ax = axes[0]
    near300 = order[:300]
    im = ax.imshow(CORR[np.ix_(near300, near300)], cmap="RdBu_r", vmin=-1, vmax=1, interpolation="nearest")
    plt.colorbar(im, ax=ax, label="Korrelation")
    ax.set_xlabel("Lichtkurve (nach z sortiert)")
    ax.set_ylabel("Lichtkurve (nach z sortiert)")
    ax.set_title(f"Korrelation der 300 nächsten Lichtkurven (z < {SN['zHD'].values[near300].max():.3f})", fontsize=10)
    ax = axes[1]
    ax.semilogy(np.arange(1, N + 1), lam, "C0-")
    ax.semilogy(np.arange(1, N + 1), np.sort(np.diag(COV))[::-1], "C1--", label="Diagonale allein (sortiert)")
    ax.set_xscale("log")
    ax.set_xlabel("Nummer des Eigenwerts")
    ax.set_ylabel("Eigenwert [mag²]")
    ax.set_title("Eigenwerte der Kovarianz", fontsize=10)
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    off_diag = COV - np.diag(np.diag(COV))
    dups = [g.index.values for _, g in SN.groupby("CID") if len(g) > 1]
    rho_dup = [CORR[i, j] for g in dups for a, i in enumerate(g) for j in g[a + 1:]]
    iu = np.triu_indices(N, 1)
    print(f"Diagonale: Fehler pro Lichtkurve Median {np.median(sd):.3f} mag; Nebendiagonale: Median der Korrelation {np.median(CORR[iu]):.3f}, "
          f"Anteil > 0.1: {np.mean(CORR[iu] > 0.1):.1%}")
    print(f"Zwei Lichtkurven derselben Supernova ({len(rho_dup)} Paare): Korrelation Median {np.median(rho_dup):.2f}")
    print(f"Größter Eigenwert {lam[0]:.4f} mag² (σ = {np.sqrt(lam[0]):.3f}), die 10 größten zusammen {lam[:10].sum() / lam.sum():.1%} der Spur")
    w = np.ones(N) / N
    print(f"Fehler des Mittelwerts aller {N} Lichtkurven: nur Diagonale {np.sqrt(w @ np.diag(np.diag(COV)) @ w):.4f} mag, "
          f"volle Kovarianz {np.sqrt(w @ COV @ w):.4f} mag")


def calibrators():
    """6. Die Kalibratoren: wie hell ist eine Supernova? (Zellen 20 von cosmology_hubblediagram.ipynb)."""
    global M_CAL, M_CAL_ERR, M_diag, a, ax, axes, b, chi2_cal, col, covM, fig, ic
    global lab, m, names, o, p, r_cal
    ic = np.where(CAL)[0]
    r_cal = SN["m_b_corr"].values[ic] - SN["CEPH_DIST"].values[ic]
    (M_CAL,), covM, chi2_cal = gls(r_cal, np.ones((len(ic), 1)), subcov(ic))
    M_CAL_ERR = np.sqrt(covM[0, 0])
    M_diag = np.average(r_cal, weights=1 / np.diag(subcov(ic)))
    names = SN["CID"].values[ic]

    fig, axes = plt.subplots(1, 2, figsize=(15, 6), gridspec_kw={"width_ratios": [1.4, 1]})
    ax = axes[0]
    o = np.argsort(r_cal)
    ax.errorbar(r_cal[o], np.arange(len(ic)), xerr=np.sqrt(np.diag(subcov(ic)))[o], fmt="o", ms=3, color="C3")
    ax.axvline(M_CAL, color="k", label=f"Mittel mit Kovarianz: {M_CAL:.3f} ± {M_CAL_ERR:.3f}")
    ax.axvspan(*LIT["M_SH0ES"][0] + np.array([-1, 1]) * LIT["M_SH0ES"][1], color="C0", alpha=0.2, label="Riess et al. 2022")
    ax.set_yticks(np.arange(len(ic))[::3])
    ax.set_yticklabels(names[o][::3], fontsize=7)
    ax.set_xlabel("M_B = m_b_corr − μ(Cepheiden) [mag]")
    ax.set_title(f"{len(ic)} Kalibrator-Lichtkurven", fontsize=10)
    ax.legend(fontsize=9)
    ax = axes[1]
    for m, col, lab in [(CAL, "C3", "Kalibratoren"), (HF, "C0", "Hubble-Fluss")]:
        ax.hist(SN.loc[m, "c"], bins=np.arange(-0.3, 0.31, 0.03), histtype="step", lw=2, color=col, density=True, label=f"{lab}: Farbe c")
        ax.hist(SN.loc[m, "x1"] / 10, bins=np.arange(-0.3, 0.31, 0.03), histtype="step", lw=1, ls="--", color=col, density=True,
                label=f"{lab}: Breite x1 / 10")
    ax.set_xlabel("Lichtkurvenparameter")
    ax.set_ylabel("Dichte")
    ax.set_title("Sind Kalibratoren gewöhnliche Supernovae?", fontsize=10)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"M_B = {M_CAL:.4f} ± {M_CAL_ERR:.4f} (volle Kovarianz), diagonal gewichtet {M_diag:.4f}; Riess et al. 2022: "
          f"{LIT['M_SH0ES'][0]} ± {LIT['M_SH0ES'][1]}")
    print(f"χ² = {chi2_cal:.1f} bei {len(ic) - 1} Freiheitsgraden; Streuung der Einzelwerte {np.std(r_cal):.3f} mag")
    for p in ("c", "x1", "HOST_LOGMASS"):
        a, b = SN.loc[CAL, p], SN.loc[HF, p]
        a, b = a[a > -9], b[b > -9]
        print(f"{p:13s}: Kalibratoren Median {a.median():+.3f}, Hubble-Fluss {b.median():+.3f}; KS-Test p = {stats.ks_2samp(a, b).pvalue:.2f}")


def hubble_flow():
    """7. Der Hubble-Fluss (Zellen 23 von cosmology_hubblediagram.ipynb)."""
    global A_B, A_B_ERR, H0_SIMPLE, H0_SIMPLE_ERR, J0, M_for_planck, Mg, Q0, ax, axes, chi2_a, col
    global covA, cov_a, f_z, fig, ih, key, mh, y_a, zh
    Q0, J0 = -0.55, 1.0
    ih = np.where(HF)[0]
    zh = SN["zHD"].values[ih]
    mh = SN["m_b_corr"].values[ih]
    f_z = 1 + 0.5 * (1 - Q0) * zh - (1 - Q0 - 3 * Q0**2 + J0) * zh**2 / 6
    y_a = np.log10(C_KMS * zh * f_z) - 0.2 * mh                          # jede Lichtkurve gibt ein a_B
    cov_a = 0.04 * subcov(ih)                                            # 0.2² × Kovarianz der Helligkeiten
    (A_B,), covA, chi2_a = gls(y_a, np.ones((len(ih), 1)), cov_a)
    A_B_ERR = np.sqrt(covA[0, 0])
    H0_SIMPLE = 10 ** (0.2 * M_CAL + A_B + 5)
    H0_SIMPLE_ERR = H0_SIMPLE * np.log(10) * np.hypot(0.2 * M_CAL_ERR, A_B_ERR)

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    ax = axes[0]
    ax.errorbar(zh, y_a, yerr=0.2 * np.sqrt(np.diag(subcov(ih))), fmt=".", ms=3, alpha=0.6)
    ax.axhline(A_B, color="C3", label=f"a_B = {A_B:.4f} ± {A_B_ERR:.4f}")
    ax.set_xlabel("z")
    ax.set_ylabel("log₁₀(cz f(z)) − 0.2 m")
    ax.set_title(f"{len(ih)} Lichtkurven im Hubble-Fluss", fontsize=10)
    ax.legend(fontsize=9)
    ax = axes[1]
    Mg = np.linspace(-19.6, -18.9, 100)
    ax.plot(Mg, 10 ** (0.2 * Mg + A_B + 5), "k-", label="H₀ = 10^(0.2 M_B + a_B + 5)")
    ax.axvspan(M_CAL - M_CAL_ERR, M_CAL + M_CAL_ERR, color="C3", alpha=0.3, label="M_B aus den Cepheiden (Schritt 6)")
    for key, col in [("H0_Planck", "C1"), ("H0_SH0ES", "C0")]:
        ax.axhspan(LIT[key][0] - LIT[key][1], LIT[key][0] + LIT[key][1], color=col, alpha=0.25, label=key.replace("H0_", "H₀ "))
    ax.set_xlabel("M_B [mag]")
    ax.set_ylabel("H₀ [km/s/Mpc]")
    ax.set_title("Welche Helligkeit bräuchte welches H₀?", fontsize=10)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    M_for_planck = 5 * (np.log10(LIT["H0_Planck"][0]) - A_B - 5)
    print(f"a_B = {A_B:.5f} ± {A_B_ERR:.5f} (χ² = {chi2_a:.1f} bei {len(ih) - 1} Freiheitsgraden)")
    print(f"H₀ = 10^(0.2 · {M_CAL:.3f} + {A_B:.4f} + 5) = {H0_SIMPLE:.2f} ± {H0_SIMPLE_ERR:.2f} km/s/Mpc")
    print(f"Für H₀ = {LIT['H0_Planck'][0]} müsste M_B = {M_for_planck:.3f} sein, {M_for_planck - M_CAL:+.3f} mag "
          f"({(M_for_planck - M_CAL) / M_CAL_ERR:.1f} σ) neben dem Wert der Cepheiden")


def h0_joint():
    """8. H₀ im gemeinsamen Fit (Zellen 26 von cosmology_hubblediagram.ipynb)."""
    global CJ, COV_J, D, H0_J, H0_J_ERR, Hg, M_J, M_J_ERR, Mg, ax, axes, ceph
    global chi2_joint, col, fig, fit, is_cal, isel, key, mj, model, rho, zhj, zj
    isel = np.where(CAL | HF)[0]
    CJ = np.linalg.inv(subcov(isel))
    zj, zhj = SN["zHD"].values[isel], SN["zHEL"].values[isel]
    mj, ceph, is_cal = SN["m_b_corr"].values[isel], SN["CEPH_DIST"].values[isel], CAL[isel]


    def chi2_joint(p, Om=OM_FIX, Ci=CJ):
        M, H0 = p
        model = np.where(is_cal, ceph, mu_model(zj, H0, Om, zhel=zhj))
        r = mj - M - model
        return r @ Ci @ r


    fit = optimize.minimize(chi2_joint, [-19.25, 73.0], method="Nelder-Mead", options=dict(xatol=1e-7, fatol=1e-7))
    M_J, H0_J = fit.x
    COV_J = np.linalg.inv(hessian(chi2_joint, fit.x) / 2)
    H0_J_ERR, M_J_ERR = np.sqrt(COV_J[1, 1]), np.sqrt(COV_J[0, 0])
    rho = COV_J[0, 1] / (H0_J_ERR * M_J_ERR)

    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
    ax = axes[0]
    Mg, Hg = np.linspace(M_J - 4 * M_J_ERR, M_J + 4 * M_J_ERR, 61), np.linspace(H0_J - 4 * H0_J_ERR, H0_J + 4 * H0_J_ERR, 61)
    D = np.array([[chi2_joint([a, b]) for a in Mg] for b in Hg]) - fit.fun
    ax.contour(Mg, Hg, D, levels=[2.30, 6.18], colors=["C0", "C0"], linestyles=["-", "--"])
    ax.plot(M_J, H0_J, "C0x", ms=10)
    for key, col in [("H0_Planck", "C1"), ("H0_SH0ES", "C3")]:
        ax.axhspan(LIT[key][0] - LIT[key][1], LIT[key][0] + LIT[key][1], color=col, alpha=0.2, label=key.replace("H0_", "H₀ "))
    ax.set_xlabel("M_B [mag]")
    ax.set_ylabel("H₀ [km/s/Mpc]")
    ax.set_title("68 % und 95 % (Δχ² = 2.30 und 6.18)", fontsize=10)
    ax.legend(fontsize=9)
    ax = axes[1]
    model = np.where(is_cal, ceph, mu_model(zj, H0_J, OM_FIX, zhel=zhj))
    ax.errorbar(zj, mj - M_J - model, yerr=np.sqrt(np.diag(subcov(isel))), fmt=".", ms=3, alpha=0.5)
    ax.axhline(0, color="k", lw=1)
    ax.set_xscale("log")
    ax.set_xlabel("z")
    ax.set_ylabel("Residuum [mag]")
    ax.set_title("Kalibratoren (links, z < 0.02) und Hubble-Fluss", fontsize=10)
    plt.tight_layout()
    plt.show()

    print(f"M_B = {M_J:.4f} ± {M_J_ERR:.4f}, H₀ = {H0_J:.2f} ± {H0_J_ERR:.2f} km/s/Mpc, Korrelation {rho:+.2f}; "
          f"χ² = {fit.fun:.1f} bei {len(isel) - 2} Freiheitsgraden")
    print(f"Schritt 7 (Achsenabschnitt): {H0_SIMPLE:.2f} ± {H0_SIMPLE_ERR:.2f}; δH₀/H₀ = 0.46 · δM_B: "
          f"0.03 mag in M_B sind {0.2 * np.log(10) * 0.03:.1%} in H₀")


def omega_m():
    """9. Ω_m aus dem ganzen Diagramm (Zellen 29 von cosmology_hubblediagram.ipynb)."""
    global C2i, OM_ERR, OM_FIT, OM_GRID, Ol, Om, _, ax, axes, chi_om, col, fig
    global fo, good, ic2, inside, k, lab, m2, mm, off_best, ref, res, z2
    global zb, ze, zh2
    ic2 = np.where((SN["zHD"].values > Z_MIN_COSMO) & ~CAL)[0]
    C2i = np.linalg.inv(subcov(ic2))
    z2, zh2, m2 = SN["zHD"].values[ic2], SN["zHEL"].values[ic2], SN["m_b_corr"].values[ic2]
    OM_GRID = np.linspace(0.15, 0.55, 161)
    chi_om = np.array([offset_chi2(m2 - mu_model(z2, 70, om, zhel=zh2), C2i)[0] for om in OM_GRID])
    fo = optimize.minimize_scalar(lambda om: offset_chi2(m2 - mu_model(z2, 70, om, zhel=zh2), C2i)[0], bounds=(0.1, 0.6), method="bounded")
    OM_FIT = fo.x
    inside = OM_GRID[chi_om - fo.fun < 1]
    OM_ERR = (inside.max() - inside.min()) / 2
    _, off_best = offset_chi2(m2 - mu_model(z2, 70, OM_FIT, zhel=zh2), C2i)

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    ax = axes[0]
    ax.plot(OM_GRID, chi_om - fo.fun)
    ax.axhline(1, color="k", ls=":")
    ax.axvline(LIT["Om_Planck"][0], color="C1", ls="--", label="Planck 2018")
    ax.set_ylim(0, 25)
    ax.set_xlabel("Ω_m (flach)")
    ax.set_ylabel("Δχ²")
    ax.set_title(f"Ω_m = {OM_FIT:.3f} ± {OM_ERR:.3f} aus {len(ic2)} Lichtkurven", fontsize=10)
    ax.legend(fontsize=9)
    ax = axes[1]
    res = m2 - off_best - mu_model(z2, 70, OM_FIT, zhel=zh2)
    zb = np.logspace(-2, 0.35, 16)
    k = np.digitize(z2, zb)
    ax.plot(z2, res, ".", ms=2, color="0.6", alpha=0.5)
    good = [j for j in range(1, len(zb)) if (k == j).sum() > 4]
    ax.plot([np.median(z2[k == j]) for j in good], [np.median(res[k == j]) for j in good], "ko", label="Median in Intervallen")
    ze = np.logspace(-2, 0.35, 200)
    ref = mu_model(ze, 70, OM_FIT)
    for (Om, Ol), col, lab in [((1.0, 0.0), "C1", "nur Materie"), ((0.0, 0.0), "C2", "leer"), ((OM_FIT, 1 - OM_FIT), "C0", "bester Fit")]:
        mm = mu_model(ze, 70, Om, Ol)
        ax.plot(ze, mm - ref - np.interp(0.05, ze, mm - ref), color=col, label=lab)
    ax.set_xscale("log")
    ax.set_ylim(-0.8, 0.6)
    ax.set_xlabel("z")
    ax.set_ylabel("Residuum gegen den besten Fit [mag]")
    ax.set_title("Residuen und andere Universen (bei z = 0.05 angeglichen)", fontsize=10)
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    print(f"Ω_m = {OM_FIT:.4f} ± {OM_ERR:.4f} (Δχ² = 1), χ²_min = {fo.fun:.1f} bei {len(ic2) - 2} Freiheitsgraden; "
          f"Ω_Λ = {1 - OM_FIT:.3f}, q₀ = {OM_FIT / 2 - (1 - OM_FIT):.3f}")
    print(f"Δχ² für Ω_m = 1 (nur Materie): {offset_chi2(m2 - mu_model(z2, 70, 1.0, zhel=zh2), C2i)[0] - fo.fun:.0f}")


def acceleration():
    """10. Beschleunigt die Expansion? (Zellen 32 von cosmology_hubblediagram.ipynb)."""
    global CHI, CHI_PLOT, OL_NF, OLg, OM_NF, OMg, VALID, a, acc, ax, b, c2
    global cs, fig, i, j, ol, ol0, om, physical, z_chk
    OMg = np.linspace(0.0, 1.0, 51)
    OLg = np.linspace(0.0, 1.4, 57)
    z_chk = np.linspace(0, z2.max(), 400)


    def physical(om, ol):
        # ein Urknall (E² > 0 bis zur fernsten Supernova) und positive Entfernungen; sonst ist das Modell ausgeschlossen
        ok = 1 - om - ol
        e2 = om * (1 + z_chk) ** 3 + ok * (1 + z_chk) ** 2 + ol
        return e2.min() > 0 and comoving(z2.max(), om, ol) > 0


    VALID = np.array([[physical(om, ol) for om in OMg] for ol in OLg])
    CHI = np.full(VALID.shape, np.inf)
    with np.errstate(invalid="ignore", divide="ignore"):                  # in geschlossenen Modellen kann D_M zwischendurch negativ werden
        for a, ol in enumerate(OLg):
            for b, om in enumerate(OMg):
                if VALID[a, b]:
                    c2 = offset_chi2(m2 - mu_model(z2, 70, om, ol, zhel=zh2), C2i)[0]
                    if np.isfinite(c2):
                        CHI[a, b] = c2
                    else:
                        VALID[a, b] = False
    CHI -= CHI.min()
    j, i = np.unravel_index(np.argmin(CHI), CHI.shape)
    OM_NF, OL_NF = OMg[i], OLg[j]
    fig, ax = plt.subplots(figsize=(8, 7))
    CHI_PLOT = np.where(VALID, CHI, 1e4)
    cs = ax.contourf(OMg, OLg, CHI_PLOT, levels=[0, 2.30, 6.18, 11.8], colors=["C0", "#7fb3d5", "#d4e6f1"])
    ax.contour(OMg, OLg, CHI_PLOT, levels=[2.30, 6.18, 11.8], colors="C0", linewidths=0.8)
    ax.contourf(OMg, OLg, (~VALID).astype(float), levels=[0.5, 1.5], colors="none", hatches=["///"])
    ax.text(0.01, 1.32, "kein Urknall", fontsize=9, backgroundcolor="w")
    ax.plot(OMg, 1 - OMg, "k-", label="flach (Ω_k = 0)")
    ax.plot(OMg, OMg / 2, "k--", label="q₀ = 0: darüber beschleunigt")
    ax.axhline(0, color="C3", lw=1.5, label="keine kosmologische Konstante")
    ax.plot(OM_NF, OL_NF, "wx", ms=10, mew=2, label=f"bester Fit ({OM_NF:.2f}, {OL_NF:.2f})")
    ax.plot(LIT["Om_Planck"][0], 1 - LIT["Om_Planck"][0], "C1*", ms=14, label="Planck 2018")
    ax.set_xlabel("Ω_m")
    ax.set_ylabel("Ω_Λ")
    ax.set_title("Erlaubte Bereiche: 68, 95 und 99.7 % (Δχ² = 2.30, 6.18, 11.8)", fontsize=10)
    ax.set_ylim(-0.03, 1.4)
    ax.legend(fontsize=9, loc="lower right")
    plt.tight_layout()
    plt.show()

    ol0 = CHI[0, VALID[0]].min()
    acc = np.array([[ol > om / 2 for om in OMg] for ol in OLg])
    print(f"Bester Fit mit Krümmung: Ω_m = {OM_NF:.2f}, Ω_Λ = {OL_NF:.2f}, Ω_k = {1 - OM_NF - OL_NF:+.2f}")
    print(f"Kleinstes Δχ² ohne kosmologische Konstante (Ω_Λ = 0): {ol0:.0f}, entspricht {np.sqrt(ol0):.0f} σ bei einem Parameter")
    print(f"Kleinstes Δχ² im gebremsten Bereich (q₀ > 0): {CHI[~acc & VALID].min():.0f}; ausgeschlossene Gitterpunkte (kein Urknall): {(~VALID).sum()}")


def diag_vs_full():
    """11. Diagonale gegen volle Kovarianz (Zellen 35 von cosmology_hubblediagram.ipynb)."""
    global TAB, ax, axes, col, diag, ecol, fig, h, h0_fit, he, ih0, iom
    global lab, o, oe, om_fit, once, rows
    def h0_fit(idx, diagonal):
        # M_B und H₀ wie in Schritt 8 für die Lichtkurven idx, mit voller Kovarianz oder nur ihrer Diagonale
        C_ = subcov(idx)
        Ci = np.linalg.inv(np.diag(np.diag(C_)) if diagonal else C_)
        zz_, zh_, mm_, ce_, ca_ = SN["zHD"].values[idx], SN["zHEL"].values[idx], SN["m_b_corr"].values[idx], SN["CEPH_DIST"].values[idx], CAL[idx]
        g = lambda p: (lambda r: r @ Ci @ r)(mm_ - p[0] - np.where(ca_, ce_, mu_model(zz_, p[1], OM_FIX, zhel=zh_)))
        f = optimize.minimize(g, [-19.25, 73.0], method="Nelder-Mead", options=dict(xatol=1e-7, fatol=1e-7))
        return f.x[1], np.sqrt(np.linalg.inv(hessian(g, f.x) / 2)[1, 1])


    def om_fit(idx, diagonal):
        # Ω_m wie in Schritt 9 für die Lichtkurven idx
        C_ = subcov(idx)
        Ci = np.linalg.inv(np.diag(np.diag(C_)) if diagonal else C_)
        zz_, zh_, mm_ = SN["zHD"].values[idx], SN["zHEL"].values[idx], SN["m_b_corr"].values[idx]
        g = lambda om: offset_chi2(mm_ - mu_model(zz_, 70, om, zhel=zh_), Ci)[0]
        best = optimize.minimize_scalar(g, bounds=(0.1, 0.6), method="bounded")
        grid = np.linspace(best.x - 0.08, best.x + 0.08, 81)
        inside = grid[np.array([g(o) for o in grid]) - best.fun < 1]
        return best.x, (inside.max() - inside.min()) / 2


    def once(idx):
        # von mehrfach beobachteten Supernovae nur die Lichtkurve mit dem kleinsten Fehler
        keep = SN.iloc[idx].sort_values("m_b_corr_err_DIAG").drop_duplicates("CID").index
        return np.sort(keep.values)


    rows = []
    for lab, ih0, iom, diag in [("volle Kovarianz", isel, ic2, False), ("nur Diagonale", isel, ic2, True),
                                ("Diagonale, jede Supernova einmal", once(isel), once(ic2), True)]:
        h, he = h0_fit(ih0, diag)
        o, oe = om_fit(iom, diag)
        rows.append(dict(Matrix=lab, Lichtkurven_H0=len(ih0), H0=h, H0_Fehler=he, Lichtkurven_Om=len(iom), Om=o, Om_Fehler=oe))
    TAB = pd.DataFrame(rows)

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.5))
    for ax, (col, ecol, lab) in zip(axes, [("H0", "H0_Fehler", "H₀ [km/s/Mpc]"), ("Om", "Om_Fehler", "Ω_m")]):
        ax.errorbar(TAB[col], np.arange(len(TAB))[::-1], xerr=TAB[ecol], fmt="o", capsize=4)
        ax.set_yticks(np.arange(len(TAB))[::-1])
        ax.set_yticklabels(TAB["Matrix"], fontsize=9)
        ax.set_xlabel(lab)
    axes[0].set_title("H₀ aus Kalibratoren und Hubble-Fluss", fontsize=10)
    axes[1].set_title("Ω_m aus dem ganzen Diagramm", fontsize=10)
    plt.tight_layout()
    plt.show()
    print(TAB.to_string(index=False, float_format=lambda x: f"{x:.4f}"))


def hubble_tension():
    """12. H₀ gegen SH0ES und Planck: die Hubble-Spannung (Zellen 38 von cosmology_hubblediagram.ipynb)."""
    global Ca, OWN, ax, axes, ca, checks, col, e, fig, g, hf_alt, i
    global ia, isc, k_, kw, lab, ma, tension, v, vals, za, zcol, zha
    global zlo
    def tension(a, b):
        return (a[0] - b[0]) / np.hypot(a[1], b[1])


    OWN = (H0_J, H0_J_ERR)
    checks = {}
    for lab, kw in [("Ω_m = 0.315 (Planck)", dict(Om=0.315)), ("Ω_m = 0.25", dict(Om=0.25)), ("Ω_m = 0.40", dict(Om=0.40))]:
        checks[lab] = optimize.minimize(lambda p: chi2_joint(p, **kw), fit.x, method="Nelder-Mead", options=dict(xatol=1e-7)).x[1]
    for lab, zlo, zcol in [("Hubble-Fluss ab z = 0.01", 0.01, "zHD"), ("Hubble-Fluss ab z = 0.05", 0.05, "zHD"), ("zCMB statt zHD", Z_HF[0], "zCMB")]:
        hf_alt = (~CAL) & (SN[zcol].values > zlo) & (SN[zcol].values < Z_HF[1])
        ia = np.where(CAL | hf_alt)[0]
        Ca = np.linalg.inv(subcov(ia))
        za, zha, ma, ca, isc = SN[zcol].values[ia], SN["zHEL"].values[ia], SN["m_b_corr"].values[ia], SN["CEPH_DIST"].values[ia], CAL[ia]
        g = lambda p: (lambda r: r @ Ca @ r)(ma - p[0] - np.where(isc, ca, mu_model(za, p[1], OM_FIX, zhel=zha)))
        checks[lab] = optimize.minimize(g, fit.x, method="Nelder-Mead", options=dict(xatol=1e-7)).x[1]

    fig, axes = plt.subplots(1, 2, figsize=(15, 4.8), gridspec_kw={"width_ratios": [1, 1.1]})
    ax = axes[0]
    vals = [("dieses Notebook", OWN, "C3"), ("Brout et al. 2022", LIT["H0_Brout"], "k"), ("Riess et al. 2022 (SH0ES)", LIT["H0_SH0ES"], "k"),
            ("Planck 2018 (ΛCDM)", LIT["H0_Planck"], "C1")]
    for i, (lab, (v, e), col) in enumerate(vals):
        ax.errorbar(v, -i, xerr=e, fmt="o", color=col, capsize=4)
    ax.set_yticks([-i for i in range(len(vals))])
    ax.set_yticklabels([v[0] for v in vals], fontsize=9)
    ax.set_xlabel("H₀ [km/s/Mpc]")
    ax.set_title("Zwei Arten, H₀ zu messen", fontsize=10)
    ax = axes[1]
    ax.barh(range(len(checks))[::-1], [v - H0_J for v in checks.values()], color="C0")
    ax.set_yticks(range(len(checks))[::-1])
    ax.set_yticklabels(list(checks), fontsize=9)
    ax.axvline(0, color="k", lw=1)
    ax.axvspan(-H0_J_ERR, H0_J_ERR, color="C3", alpha=0.15, label="1σ statistisch")
    ax.set_xlabel("Änderung von H₀ [km/s/Mpc]")
    ax.set_title("Wie empfindlich ist H₀ gegen die Annahmen?", fontsize=10)
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    print(f"Eigenes H₀ = {H0_J:.2f} ± {H0_J_ERR:.2f}: gegen Brout {tension(OWN, LIT['H0_Brout']):+.1f} σ, "
          f"gegen SH0ES {tension(OWN, LIT['H0_SH0ES']):+.1f} σ, gegen Planck {tension(OWN, LIT['H0_Planck']):+.1f} σ")
    print(f"SH0ES gegen Planck: {tension(LIT['H0_SH0ES'], LIT['H0_Planck']):.1f} σ")
    for k_, v in checks.items():
        print(f"  {k_:28s}: H₀ = {v:.2f} ({v - H0_J:+.2f})")


def vs_pantheon():
    """13. Ω_m gegen Pantheon+ und Planck (Zellen 41 von cosmology_hubblediagram.ipynb)."""
    global Ci_, ax, axes, col, e, fig, i, ia, lab, ma, n_, om_checks
    global own, v, vals, za, zha, zlo
    om_checks = {}
    for zlo in (0.005, 0.01, 0.023, 0.05, 0.1):
        ia = np.where((SN["zHD"].values > zlo) & ~CAL)[0]
        Ci_ = np.linalg.inv(subcov(ia))
        za, zha, ma = SN["zHD"].values[ia], SN["zHEL"].values[ia], SN["m_b_corr"].values[ia]
        om_checks[zlo] = (optimize.minimize_scalar(lambda om: offset_chi2(ma - mu_model(za, 70, om, zhel=zha), Ci_)[0],
                                                   bounds=(0.1, 0.6), method="bounded").x, len(ia))
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.5))
    ax = axes[0]
    vals = [("dieses Notebook", (OM_FIT, OM_ERR), "C3"), ("Brout et al. 2022", LIT["Om_Brout"], "k"), ("Planck 2018", LIT["Om_Planck"], "C1")]
    for i, (lab, (v, e), col) in enumerate(vals):
        ax.errorbar(v, -i, xerr=e, fmt="o", color=col, capsize=4)
    ax.set_yticks([-i for i in range(len(vals))])
    ax.set_yticklabels([v[0] for v in vals], fontsize=9)
    ax.set_xlabel("Ω_m")
    ax.set_title("Materieanteil", fontsize=10)
    ax = axes[1]
    ax.plot(list(om_checks), [v[0] for v in om_checks.values()], "o-")
    ax.axhspan(OM_FIT - OM_ERR, OM_FIT + OM_ERR, color="C3", alpha=0.15)
    ax.set_xscale("log")
    ax.set_xlabel("untere Grenze in z")
    ax.set_ylabel("Ω_m")
    ax.set_title("Ω_m gegen die untere Grenze der Stichprobe", fontsize=10)
    plt.tight_layout()
    plt.show()

    own = (OM_FIT, OM_ERR)
    print(f"Ω_m = {OM_FIT:.4f} ± {OM_ERR:.4f}: gegen Brout {tension(own, LIT['Om_Brout']):+.2f} σ, gegen Planck {tension(own, LIT['Om_Planck']):+.2f} σ")
    for zlo, (v, n_) in om_checks.items():
        print(f"  z > {zlo:<6}: Ω_m = {v:.4f} ({n_} Lichtkurven)")
