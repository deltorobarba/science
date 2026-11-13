"""Baryonische akustische Oszillationen aus DESI DR2: Alcock-Paczynski, Ω_m und h·r_d, Schallhorizont, inverse Entfernungsleiter, w0 und wa mit MCMC.

Für cosmology.ipynb aus cosmology_bao.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, measurements, alcock_paczynski, bao_and_sne, omega_m_hrd, sound_horizon, inverse_ladder, galaxy_bump, bao_vs_cmb, three_omega_m, w0wa, w0wa_mcmc, w0wa_meaning, literature.
Downloads und Cache: data/cosmology/ (`cosmodata.py`).
"""
import cosmodata                                      # zuerst: Cache-Ordner für astropy
import os
import time
import urllib.request
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import ndimage, optimize, stats


def load():
    """57. Daten (Zellen 4, 6 von cosmology_bao.ipynb)."""
    global ASTRODATA, BBN, CMB_COV, CMB_MEAN, COV, COV_BAO, COV_SN, C_KMS, C_PLANCK, DESI_DIR, DESI_URL, E
    global ERR_BAO, H0_SH0ES, IC_BAO, IC_CMB, IC_SN, IC_SN_SUM, KIND, K_ZDRAG, K_ZSTAR, M_B_CEPHEID, M_SN, N
    global OMEGA_G, OMEGA_NU, PANTHEON, PANTHEON_URL, PARTS, PLANCK, SN, START, THETA, TRACERS, WM_PLANCK, W_PRIOR
    global X, Y_BAO, ZG, ZHEL_SN, Z_BAO, Z_SN, bao_model, chi2_bao, chi2_cmb, chi2_sn, cosmo, covariance
    global derived, derived_cov, distances, download, ellipse, fit, name, sigma, tab, total, unpack, use
    global z_drag, z_star
    ASTRODATA = cosmodata.DATA


    C_KMS, OMEGA_G, OMEGA_NU = 299792.458, 2.4728e-5, 0.00064   # c [km/s]; ω_γ für 2.7255 K; ω_ν eines Neutrinos mit 0.06 eV
    DESI_URL = "https://raw.githubusercontent.com/CobayaSampler/bao_data/master/desi_bao_dr2/"
    PANTHEON_URL = "https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/main/Pantheon%2B_Data/4_DISTANCES_AND_COVAR/"
    DESI_DIR, PANTHEON = ASTRODATA / "desi", ASTRODATA / "pantheon"
    TRACERS = {0.295: "BGS", 0.51: "LRG1", 0.706: "LRG2", 0.934: "LRG3+ELG1", 1.321: "ELG2", 1.484: "QSO", 2.33: "Lyα"}
    PLANCK = dict(h=0.6736, wb=0.02237, wc=0.1200, rd=147.09, zd=1059.94, zstar=1089.92, theta=1.04110, Om=0.3153, H0=(67.36, 0.54))
    CMB_MEAN = np.array([0.01041, 0.02223, 0.14208])                     # θ*, ω_b, ω_cb (DESI DR2, Gl. A1)
    CMB_COV = 1e-9 * np.array([[0.006621, 0.12444, -1.1929],
                               [0.12444, 21.344, -94.001],
                               [-1.1929, -94.001, 1488.4]])               # Gl. A2
    BBN = (0.02218, 0.00055)                                             # ω_b aus D/H (Schöneberg 2024; DESI Gl. 14)
    THETA = (1.04110, 0.00053)                                           # 100 θ* (DESI Gl. 16)
    H0_SH0ES = (73.04, 1.04)                                             # Riess et al. 2022
    M_B_CEPHEID = -19.249                                                # absolute Helligkeit aus Das Hubble-Diagramm
    W_PRIOR = dict(w0=(-3.0, 1.0), wa=(-3.0, 2.0))                       # flache Priors wie bei DESI, dazu w₀ + w_a < 0


    def download(url, path, check, timeout=300):
        path = Path(path)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            with urllib.request.urlopen(url, timeout=timeout) as r:
                data = r.read()
            if not check(data):
                raise OSError(f"{path.name}: unerwarteter Inhalt")
            path.write_bytes(data)
        return path


    name = "desi_gaussian_bao_ALL_GCcomb_"
    tab = np.loadtxt(download(DESI_URL + name + "mean.txt", DESI_DIR / (name + "mean.txt"), lambda d: d.startswith(b"# [z]")), dtype=str)
    Z_BAO, Y_BAO, KIND = tab[:, 0].astype(float), tab[:, 1].astype(float), tab[:, 2]
    COV_BAO = np.loadtxt(download(DESI_URL + name + "cov.txt", DESI_DIR / (name + "cov.txt"), lambda d: d[:1].isdigit()))
    IC_BAO = np.linalg.inv(COV_BAO)
    ERR_BAO = np.sqrt(np.diag(COV_BAO))

    SN = pd.read_csv(download(PANTHEON_URL + "Pantheon%2BSH0ES.dat", PANTHEON / "Pantheon+SH0ES.dat", lambda d: d.startswith(b"CID")), sep=r"\s+")
    N = len(SN)
    COV = np.loadtxt(download(PANTHEON_URL + "Pantheon%2BSH0ES_STAT%2BSYS.cov", PANTHEON / "Pantheon+SH0ES_STAT+SYS.cov",
                              lambda d: d.split(b"\n", 1)[0].strip() == b"1701"), skiprows=1).reshape(N, N)
    COV = (COV + COV.T) / 2                                              # die Textdatei ist auf 8 Stellen gerundet
    use = SN["zHD"].values > 0.01
    Z_SN, ZHEL_SN, M_SN = SN["zHD"].values[use], SN["zHEL"].values[use], SN["m_b_corr"].values[use]
    COV_SN = COV[np.ix_(use, use)]
    IC_SN = np.linalg.inv(COV_SN)
    IC_SN_SUM = IC_SN.sum()
    IC_CMB = np.linalg.inv(CMB_COV)

    print(f"DESI DR2: {len(Y_BAO)} Messwerte bei z = {Z_BAO.min()} bis {Z_BAO.max()}; Arten: "
          + ", ".join(f"{k} {np.sum(KIND == k)}" for k in ["DV_over_rs", "DM_over_rs", "DH_over_rs"]))
    print(f"Pantheon+: {use.sum()} Lichtkurven mit z > 0.01 (von {N}); CMB-Likelihood: 100 θ* = {100 * CMB_MEAN[0]:.3f} ± "
          f"{100 * np.sqrt(CMB_COV[0, 0]):.5f}, ω_b = {CMB_MEAN[1]} ± {np.sqrt(CMB_COV[1, 1]):.5f}, ω_cb = {CMB_MEAN[2]} ± {np.sqrt(CMB_COV[2, 2]):.4f}")

    X = np.linspace(0, np.log(1 + 1e8), 6001)                            # Gitter in ln(1+z)
    ZG = np.expm1(X)
    WM_PLANCK = PLANCK["wb"] + PLANCK["wc"] + OMEGA_NU


    def E(z, h, wm, w0=-1.0, wa=0.0):
        # H(z)/H₀ (flach): Photonen und zwei masselose Neutrinos als Strahlung, das massive Neutrino geht von Strahlung in Materie
        # über (Wurzel aus der Summe der Quadrate), Dunkle Energie mit w(a) = w₀ + w_a (1 − a)
        a = 1 / (1 + z)
        o_rad = OMEGA_G * (1 + 0.2271 * 3.046 * 2 / 3) / h**2
        o_nu1 = OMEGA_G * 0.2271 * 3.046 / 3 / h**2
        o_nu = np.sqrt((o_nu1 / a**4) ** 2 + (OMEGA_NU / h**2 / a**3) ** 2)
        o_m = (wm - OMEGA_NU) / h**2
        o_de = 1 - o_m - o_rad - np.sqrt(o_nu1**2 + (OMEGA_NU / h**2) ** 2)
        f_de = a ** (-3 * (1 + w0 + wa)) * np.exp(-3 * wa * (1 - a))
        return np.sqrt(o_rad / a**4 + o_nu + o_m / a**3 + o_de * f_de)


    def z_star(wb, wm):
        # Hu & Sugiyama (1996), Gl. E1
        g1 = 0.0783 * wb**-0.238 / (1 + 39.5 * wb**0.763)
        g2 = 0.560 / (1 + 21.1 * wb**1.81)
        return 1048 * (1 + 0.00124 * wb**-0.738) * (1 + g1 * wm**g2)


    def z_drag(wb, wm):
        # Eisenstein & Hu (1998), Gl. 4
        b1 = 0.313 * wm**-0.419 * (1 + 0.607 * wm**0.674)
        b2 = 0.238 * wm**0.223
        return 1291 * wm**0.251 / (1 + 0.659 * wm**0.828) * (1 + b1 * wb**b2)


    K_ZSTAR = PLANCK["zstar"] / z_star(PLANCK["wb"], WM_PLANCK)          # Eichung der Näherungen an Planck
    K_ZDRAG = PLANCK["zd"] / z_drag(PLANCK["wb"], WM_PLANCK)


    def cosmo(h, wb, wcb, w0=-1.0, wa=0.0):
        wm = wcb + OMEGA_NU
        f = (1 + ZG) / E(ZG, h, wm, w0, wa)                                # dz/E = (1+z)/E · d ln(1+z)
        dm = C_KMS / (100 * h) * np.concatenate([[0.0], np.cumsum((f[1:] + f[:-1]) / 2 * np.diff(X))])
        g = f / np.sqrt(3 * (1 + 3 * wb / (4 * OMEGA_G) / (1 + ZG)))       # c_s/c · dz/E
        seg = (g[1:] + g[:-1]) / 2 * np.diff(X)
        rs_above = C_KMS / (100 * h) * np.concatenate([np.cumsum(seg[::-1])[::-1], [0.0]])   # ∫_z^∞ c_s dz/H [Mpc]
        zs, zd = K_ZSTAR * z_star(wb, wm), K_ZDRAG * z_drag(wb, wm)
        at = lambda arr, z: np.interp(np.log1p(z), X, arr)
        return dict(h=h, wb=wb, wcb=wcb, wm=wm, w0=w0, wa=wa, dm=dm, rs_above=rs_above, zs=zs, zd=zd,
                    rd=at(rs_above, zd), rstar=at(rs_above, zs), theta=at(rs_above, zs) / at(dm, zs))


    def distances(c, z):
        DM = np.interp(np.log1p(z), X, c["dm"])
        DH = C_KMS / (100 * c["h"] * E(z, c["h"], c["wm"], c["w0"], c["wa"]))
        return DM, DH, (z * DM**2 * DH) ** (1 / 3)


    def bao_model(c):
        DM, DH, DV = distances(c, Z_BAO)
        return np.select([KIND == "DM_over_rs", KIND == "DH_over_rs"], [DM, DH], DV) / c["rd"]


    def chi2_bao(c):
        r = Y_BAO - bao_model(c)
        return r @ IC_BAO @ r


    def chi2_sn(c):
        # m_B − 5 log₁₀(D_L/Mpc) − 25 = M_B; über M_B analytisch minimiert
        r = M_SN - 5 * np.log10((1 + ZHEL_SN) * np.interp(np.log1p(Z_SN), X, c["dm"])) - 25
        a = IC_SN @ r
        return r @ a - a.sum() ** 2 / IC_SN_SUM


    def chi2_cmb(c):
        d = np.array([c["theta"], c["wb"], c["wcb"]]) - CMB_MEAN
        return d @ IC_CMB @ d


    PARTS = dict(BAO=chi2_bao, SN=chi2_sn, CMB=chi2_cmb,
                 BBN=lambda c: ((c["wb"] - BBN[0]) / BBN[1]) ** 2,
                 THETA=lambda c: ((100 * c["theta"] - THETA[0]) / THETA[1]) ** 2)


    def unpack(p, model):
        return (*p[:3], p[3], p[4]) if model == "w0wa" else (*p[:3], -1.0, 0.0)


    def total(p, data, model="lcdm"):
        h, wb, wcb, w0, wa = unpack(p, model)
        if not (0.4 < h < 1.0 and 0.005 < wb < 0.05 and 0.05 < wcb < 0.3 and W_PRIOR["w0"][0] <= w0 <= W_PRIOR["w0"][1]
                and W_PRIOR["wa"][0] <= wa <= W_PRIOR["wa"][1] and w0 + wa < 0):
            return 1e10
        c = cosmo(h, wb, wcb, w0, wa)
        return sum(PARTS[d](c) for d in data)


    START = dict(lcdm=[0.68, 0.0222, 0.142], w0wa=[0.68, 0.0222, 0.142, -0.8, -0.6])


    def fit(data, model="lcdm", start=None):
        # Nelder-Mead mit Neustarts (bleibt in schmalen Tälern sonst zu früh stehen)
        p, best = np.array(start if start is not None else START[model], float), None
        for _ in range(3):
            r = optimize.minimize(total, p, args=(data, model), method="Nelder-Mead",
                                  options=dict(xatol=1e-8, fatol=1e-7, maxiter=40000, maxfev=40000))
            p = r.x
            if best is None or r.fun < best.fun - 1e-7:
                best = r
        return best


    def covariance(p, data, model="lcdm", steps=(1e-4, 1e-5, 1e-4, 1e-3, 3e-3)):
        # Kovarianz = (½ Hesse-Matrix von χ²)⁻¹, mit zentralen Differenzen
        n = len(p)
        H = np.zeros((n, n))
        for i in range(n):
            for j in range(i, n):
                ei, ej = np.eye(n)[i] * steps[i], np.eye(n)[j] * steps[j]
                H[i, j] = H[j, i] = (total(p + ei + ej, data, model) - total(p + ei - ej, data, model)
                                     - total(p - ei + ej, data, model) + total(p - ei - ej, data, model)) / (4 * steps[i] * steps[j])
        return np.linalg.inv(H / 2)


    def derived(p, model="lcdm"):
        # H₀, Ω_m und h·r_d aus (h, ω_b, ω_cb, …)
        c = cosmo(*unpack(p, model))
        return np.array([100 * c["h"], c["wm"] / c["h"] ** 2, c["h"] * c["rd"]])


    def derived_cov(p, cov, model="lcdm"):
        J = np.array([(derived(p + np.eye(len(p))[i] * d, model) - derived(p - np.eye(len(p))[i] * d, model)) / (2 * d)
                      for i, d in enumerate([1e-5, 1e-6, 1e-5, 1e-4, 1e-4][:len(p)])]).T
        return J @ cov @ J.T


    def sigma(dchi2, dof=2):
        return stats.norm.isf(stats.chi2.sf(dchi2, dof) / 2)


    def ellipse(ax, mean, cov, color, label=None, levels=(2.30, 6.18), **kw):
        # 68- und 95-%-Ellipse einer zweidimensionalen Normalverteilung
        val, vec = np.linalg.eigh(cov)
        t = np.linspace(0, 2 * np.pi, 200)
        for n, lv in enumerate(levels):
            pts = mean[:, None] + vec @ (np.sqrt(val * lv)[:, None] * np.array([np.cos(t), np.sin(t)]))
            ax.plot(*pts, color=color, lw=1.8 if n == 0 else 1, label=label if n == 0 else None, **kw)


    C_PLANCK = cosmo(PLANCK["h"], PLANCK["wb"], PLANCK["wb"] + PLANCK["wc"])
    print(f"Eichfaktoren: z* × {K_ZSTAR:.5f}, z_d × {K_ZDRAG:.4f}")
    print(f"Planck-ΛCDM: r_d = {C_PLANCK['rd']:.2f} Mpc (Planck 147.09), r* = {C_PLANCK['rstar']:.2f} Mpc (144.43), "
          f"100 θ* = {100 * C_PLANCK['theta']:.5f} (1.04110)")


def measurements():
    """58. Die Messungen von DESI DR2 (Zellen 8 von cosmology_bao.ipynb)."""
    global DHp, DMp, DVp, ax, ax2, col, curve, dz, fig, idx, k, lab
    global m, mk, name, pred, r, style, txt, z0, zz
    pred = bao_model(C_PLANCK)
    zz = np.linspace(0.02, 2.6, 300)
    DMp, DHp, DVp = distances(C_PLANCK, zz)
    style = {"DM_over_rs": ("C0", "o", r"$D_M/r_d$ (quer zur Sichtlinie)", DMp, -0.012),
             "DH_over_rs": ("C3", "s", r"$D_H/r_d$ (längs der Sichtlinie)", DHp, 0.012),
             "DV_over_rs": ("C2", "D", r"$D_V/r_d$ (Mittel, BGS)", DVp, 0.0)}
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(13, 9), sharex=True, gridspec_kw=dict(height_ratios=[3, 2]))
    for k, (col, mk, lab, curve, dz) in style.items():
        m = KIND == k
        ax.errorbar(Z_BAO[m], Y_BAO[m], yerr=ERR_BAO[m], fmt=mk, color=col, ms=7, capsize=3, label=lab)
        ax.plot(zz, curve / C_PLANCK["rd"], color=col, lw=1)
        ax2.errorbar(Z_BAO[m] + dz, Y_BAO[m] / pred[m], yerr=ERR_BAO[m] / pred[m], fmt=mk, color=col, ms=7, capsize=3)
    for z0, name in TRACERS.items():
        ax.text(z0, 44, name, ha="center", fontsize=9, color="0.3")
    ax.set_ylim(0, 46)
    ax.set_ylabel("Entfernung in Einheiten von $r_d$")
    ax.set_title("DESI DR2: Entfernungen in Einheiten des Schallhorizonts; Linien: Planck-ΛCDM", fontsize=10)
    ax.legend(fontsize=9, loc="center right")
    ax2.axhline(1, color="k", lw=1)
    ax2.set_xlabel("Rotverschiebung z")
    ax2.set_ylabel("DESI / Planck-ΛCDM")
    plt.tight_layout()
    plt.show()

    r = Y_BAO - pred
    print(f"χ² gegen Planck-ΛCDM: {r @ IC_BAO @ r:.1f} bei {len(Y_BAO)} Werten")
    for z0, name in TRACERS.items():
        idx = np.where(Z_BAO == z0)[0]
        txt = ", ".join(f"{KIND[i][:2]}/r_d = {Y_BAO[i]:.3f} ± {ERR_BAO[i]:.3f} ({Y_BAO[i] / pred[i]:.3f})" for i in idx)
        if len(idx) == 2:
            txt += f", Korrelation {COV_BAO[idx[0], idx[1]] / (ERR_BAO[idx[0]] * ERR_BAO[idx[1]]):+.2f}"
        print(f"{name:10s} z = {z0:5.3f}: {txt}")


def alcock_paczynski():
    """59. Alcock-Paczynski: die Form ohne Maßstab (Zellen 11 von cosmology_bao.ipynb)."""
    global F_AP, F_ERR, OM_AP, OM_AP_ERR, ax, ax2, chi_ap, col, e, f, f_ap, fig
    global inside, o, oms, pairs, z_ap, zi, zz
    pairs = [(i, j) for i in range(len(Z_BAO)) for j in range(len(Z_BAO))
             if Z_BAO[i] == Z_BAO[j] and KIND[i] == "DM_over_rs" and KIND[j] == "DH_over_rs"]
    z_ap = np.array([Z_BAO[i] for i, _ in pairs])
    F_AP = np.array([Y_BAO[i] / Y_BAO[j] for i, j in pairs])
    F_ERR = F_AP * np.array([np.sqrt(COV_BAO[i, i] / Y_BAO[i] ** 2 + COV_BAO[j, j] / Y_BAO[j] ** 2
                                     - 2 * COV_BAO[i, j] / (Y_BAO[i] * Y_BAO[j])) for i, j in pairs])


    def f_ap(Om, z):
        DM, DH, _ = distances(cosmo(0.7, 0.0224, Om * 0.49 - OMEGA_NU), z)
        return DM / DH


    oms = np.linspace(0.20, 0.42, 221)
    chi_ap = np.array([np.sum(((F_AP - f_ap(o, z_ap)) / F_ERR) ** 2) for o in oms])
    OM_AP = oms[np.argmin(chi_ap)]
    inside = oms[chi_ap - chi_ap.min() <= 1]
    OM_AP_ERR = (inside.max() - inside.min()) / 2

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.6))
    zz = np.linspace(0.05, 2.6, 200)
    for o, col in [(0.25, "C0"), (0.30, "C1"), (0.35, "C3")]:
        ax.plot(zz, f_ap(o, zz) / zz, color=col, lw=1.4, label=f"ΛCDM, Ω_m = {o}")
    ax.errorbar(z_ap, F_AP / z_ap, yerr=F_ERR / z_ap, fmt="ko", ms=7, capsize=3, label="DESI DR2")
    ax.set_xlabel("Rotverschiebung z")
    ax.set_ylabel(r"$F_\mathrm{AP}/z = D_M/(z\,D_H)$")
    ax.set_title("Das Verhältnis von Breite zu Tiefe hängt nur von Ω_m ab", fontsize=10)
    ax.legend(fontsize=9)
    ax2.plot(oms, chi_ap - chi_ap.min(), color="k", lw=1.6)
    ax2.axhline(1, color="0.5", ls=":")
    ax2.axvspan(PLANCK["Om"] - 0.0073, PLANCK["Om"] + 0.0073, color="C3", alpha=0.25, label="Planck 2018")
    ax2.set_ylim(0, 10)
    ax2.set_xlabel(r"$\Omega_m$")
    ax2.set_ylabel(r"$\Delta\chi^2$")
    ax2.set_title("Ω_m allein aus dem Alcock-Paczynski-Test", fontsize=10)
    ax2.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    for zi, f, e in zip(z_ap, F_AP, F_ERR):
        print(f"z = {zi:5.3f}: F_AP = {f:.4f} ± {e:.4f} ({100 * e / f:.1f} %)")
    print(f"Ω_m = {OM_AP:.3f} ± {OM_AP_ERR:.3f}, χ² = {chi_ap.min():.2f} bei {len(F_AP)} Werten und 1 Parameter")


def bao_and_sne():
    """60. BAO und Supernovae im selben Diagramm (Zellen 14 von cosmology_bao.ipynb)."""
    global ax, col, dm_sn, eb, edges, fig, i, k, kk, lab, m, mk
    global ratio_bao, ratio_sn, rb, sig_sn, w, zb
    dm_sn = 10 ** ((M_SN - M_B_CEPHEID - 25) / 5) / (1 + ZHEL_SN)
    ratio_sn = dm_sn / distances(C_PLANCK, Z_SN)[0]
    sig_sn = np.log(10) / 5 * np.sqrt(np.diag(COV_SN)) * ratio_sn
    edges = np.array([0.01, 0.02, 0.04, 0.07, 0.12, 0.2, 0.3, 0.4, 0.55, 0.75, 1.0, 1.5, 2.3])
    k = np.digitize(Z_SN, edges) - 1
    zb, rb, eb = [], [], []
    for i in range(len(edges) - 1):
        m = k == i
        if m.sum() >= 3:
            w = 1 / sig_sn[m] ** 2
            zb.append(np.average(Z_SN[m], weights=w))
            rb.append(np.average(ratio_sn[m], weights=w))
            eb.append(1 / np.sqrt(w.sum()))
    zb, rb, eb = map(np.array, (zb, rb, eb))
    ratio_bao = Y_BAO / pred

    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(Z_SN, ratio_sn, ".", ms=2, color="C1", alpha=0.25)
    ax.errorbar(zb, rb, yerr=eb, fmt="o", color="C1", ms=7, capsize=3, label=f"Supernovae mit $M_B$ = {M_B_CEPHEID} (Cepheiden), Bins")
    for kk, (col, mk, lab) in {"DM_over_rs": ("C0", "o", r"BAO $D_M$"), "DH_over_rs": ("C3", "s", r"BAO $D_H$"),
                               "DV_over_rs": ("C2", "D", r"BAO $D_V$")}.items():
        m = KIND == kk
        ax.errorbar(Z_BAO[m], ratio_bao[m], yerr=ERR_BAO[m] / pred[m], fmt=mk, color=col, ms=7, capsize=3,
                    label=lab + f" mit $r_d$ = {PLANCK['rd']} Mpc (Planck)")
    ax.axhline(1, color="k", lw=1, label="Planck-ΛCDM, H₀ = 67.36")
    ax.axhline(PLANCK["H0"][0] / H0_SH0ES[0], color="C1", ls="--", lw=1.2, label="Form von Planck, H₀ = 73.04")
    ax.set_xscale("log")
    ax.set_ylim(0.82, 1.08)
    ax.set_xlabel("Rotverschiebung z")
    ax.set_ylabel("Entfernung / Planck-ΛCDM")
    ax.set_title("Zwei Entfernungsleitern mit zwei Maßstäben", fontsize=10)
    ax.legend(fontsize=9, loc="lower left")
    plt.show()

    m = (zb > 0.1)
    print(f"Supernovae, z > 0.1: mittleres Verhältnis {np.average(rb[m], weights=1 / eb[m] ** 2):.4f}; "
          f"BAO: {np.average(ratio_bao, weights=(pred / ERR_BAO) ** 2):.4f}")
    print(f"Verhältnis der beiden Leitern: {np.average(ratio_bao, weights=(pred / ERR_BAO) ** 2) / np.average(rb[m], weights=1 / eb[m] ** 2):.4f}; "
          f"67.36/73.04 = {PLANCK['H0'][0] / H0_SH0ES[0]:.4f}")


def omega_m_hrd():
    """61. Ω_m und h·r_d nur aus den BAO (Zellen 17 von cosmology_bao.ipynb)."""
    global BAO2, Hq, ax, chi2_om_hrd, cs, e4, eps, fig, grid, hrd_g, om_g, r4
    global rho, x
    def chi2_om_hrd(Om, hrd):
        c = cosmo(0.7, 0.0224, Om * 0.49 - OMEGA_NU)
        return chi2_bao(dict(c, rd=hrd / 0.7))


    r4 = optimize.minimize(lambda q: chi2_om_hrd(*q), [0.30, 101.5], method="Nelder-Mead", options=dict(xatol=1e-8, fatol=1e-10))
    eps = np.array([1e-4, 1e-2])
    Hq = np.array([[(chi2_om_hrd(*(r4.x + np.eye(2)[i] * eps[i] + np.eye(2)[j] * eps[j]))
                     - chi2_om_hrd(*(r4.x + np.eye(2)[i] * eps[i] - np.eye(2)[j] * eps[j]))
                     - chi2_om_hrd(*(r4.x - np.eye(2)[i] * eps[i] + np.eye(2)[j] * eps[j]))
                     + chi2_om_hrd(*(r4.x - np.eye(2)[i] * eps[i] - np.eye(2)[j] * eps[j]))) / (4 * eps[i] * eps[j])
                    for j in range(2)] for i in range(2)])
    BAO2 = (r4.x, np.linalg.inv(Hq / 2))                     # (Ω_m, h r_d) und Kovarianz
    e4 = np.sqrt(np.diag(BAO2[1]))
    om_g, hrd_g = np.linspace(0.25, 0.35, 81), np.linspace(98, 105, 71)
    grid = np.array([[chi2_om_hrd(o, x) for o in om_g] for x in hrd_g])

    fig, ax = plt.subplots(figsize=(10, 7))
    cs = ax.contourf(om_g, hrd_g, grid - r4.fun, levels=[0, 2.30, 6.18], colors=["C0", "lightsteelblue"], alpha=0.8)
    ax.plot(*r4.x, "k+", ms=14, mew=2, label="eigenes Minimum")
    for x in (OM_AP - OM_AP_ERR, OM_AP + OM_AP_ERR):
        ax.axvline(x, color="C1", ls="--", lw=1.4)
    ax.plot([], [], color="C1", ls="--", label="Alcock-Paczynski allein, 1σ (Schritt 59)")
    ax.plot(PLANCK["Om"], PLANCK["h"] * PLANCK["rd"], "*", color="C3", ms=16, label="Planck 2018")
    ax.plot(0.2975, 101.54, "x", color="k", ms=10, mew=2, label="DESI DR2 (0.2975, 101.54)")
    ax.plot([], [], color="C0", lw=8, label="68 % (Δχ² < 2.30)")
    ax.plot([], [], color="lightsteelblue", lw=8, label="95 % (Δχ² < 6.18)")
    ax.set_xlabel(r"$\Omega_m$")
    ax.set_ylabel(r"$h\,r_d$ [Mpc]")
    ax.set_title("Was die BAO allein festlegen (flaches ΛCDM)", fontsize=10)
    ax.legend(fontsize=9)
    plt.show()

    rho = BAO2[1][0, 1] / (e4[0] * e4[1])
    print(f"Ω_m = {r4.x[0]:.4f} ± {e4[0]:.4f}, h r_d = {r4.x[1]:.2f} ± {e4[1]:.2f} Mpc, Korrelation {rho:.2f}, "
          f"χ² = {r4.fun:.2f} bei {len(Y_BAO)} − 2 Freiheitsgraden")
    print(f"DESI DR2: Ω_m = 0.2975 ± 0.0086, h r_d = 101.54 ± 0.73 Mpc, Korrelation −0.92; Planck: h r_d = {PLANCK['h'] * PLANCK['rd']:.2f} Mpc")


def sound_horizon():
    """62. Der Schallhorizont r_d (Zellen 20 von cosmology_bao.ipynb)."""
    global aubourg, ax, ax2, c5, col, d, fig, lab, rd_raw, rv, s_b, s_cb
    global wb_, wcbP, wcbs, zd_raw, zv, zz
    def aubourg(wb, wcb, wnu=OMEGA_NU):
        return 55.154 * np.exp(-72.3 * (wnu + 0.0006) ** 2) / (wcb**0.25351 * wb**0.12807)


    c5 = C_PLANCK
    zd_raw = z_drag(PLANCK["wb"], WM_PLANCK)
    rd_raw = np.interp(np.log1p(zd_raw), X, c5["rs_above"])
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.6))
    zz = np.linspace(900, 1300, 400)
    ax.plot(zz, np.interp(np.log1p(zz), X, c5["rs_above"]), color="k", lw=1.6)
    for zv, rv, lab, col in [(c5["zs"], c5["rstar"], "r*", "C0"), (c5["zd"], c5["rd"], "r_d", "C3"), (zd_raw, rd_raw, "r_d (ungeeicht)", "0.5")]:
        ax.plot(zv, rv, "o", color=col, ms=8)
        ax.annotate(f"{lab} = {rv:.2f} Mpc bei z = {zv:.1f}", (zv, rv), xytext=(12, 4), textcoords="offset points", fontsize=9, color=col)
    ax.invert_xaxis()
    ax.set_xlabel("Rotverschiebung z (die Zeit läuft nach rechts)")
    ax.set_ylabel(r"$\int_z^\infty c_s\,dz/H$ [Mpc]")
    ax.set_title("Der Schallhorizont wächst bis zur Drag-Epoche weiter", fontsize=10)
    wcbs = np.linspace(0.12, 0.165, 46)
    for wb_, col in [(0.0210, "C0"), (PLANCK["wb"], "C3"), (0.0240, "C2")]:
        ax2.plot(wcbs, [cosmo(PLANCK["h"], wb_, x)["rd"] for x in wcbs], color=col, lw=1.6, label=f"Integral, ω_b = {wb_}")
        ax2.plot(wcbs, aubourg(wb_, wcbs), color=col, ls=":", lw=1.4)
    ax2.plot([], [], color="k", ls=":", label="Formel von Aubourg et al.")
    ax2.plot(PLANCK["wb"] + PLANCK["wc"], PLANCK["rd"], "*", color="C3", ms=14, label="Planck 2018")
    ax2.set_xlabel(r"$\omega_{cb} = (\Omega_b + \Omega_c)\,h^2$")
    ax2.set_ylabel(r"$r_d$ [Mpc]")
    ax2.set_title("Mehr Materie oder mehr Baryonen machen das Lineal kürzer", fontsize=10)
    ax2.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    wcbP = PLANCK["wb"] + PLANCK["wc"]
    d = 1e-3
    s_cb = (np.log(cosmo(PLANCK["h"], PLANCK["wb"], wcbP * (1 + d))["rd"]) - np.log(cosmo(PLANCK["h"], PLANCK["wb"], wcbP * (1 - d))["rd"])) / (2 * d)
    s_b = (np.log(cosmo(PLANCK["h"], PLANCK["wb"] * (1 + d), wcbP)["rd"]) - np.log(cosmo(PLANCK["h"], PLANCK["wb"] * (1 - d), wcbP)["rd"])) / (2 * d)
    print(f"z* = {c5['zs']:.2f}, z_d = {c5['zd']:.2f} (Näherung ungeeicht {zd_raw:.1f}); r* = {c5['rstar']:.2f} Mpc, r_d = {c5['rd']:.2f} Mpc "
          f"(+{100 * (c5['rd'] / c5['rstar'] - 1):.1f} %)")
    print(f"r_d ungeeicht {rd_raw:.2f} Mpc ({100 * (rd_raw / c5['rd'] - 1):+.1f} %), Aubourg {aubourg(PLANCK['wb'], wcbP):.2f} Mpc, Planck {PLANCK['rd']}")
    print(f"Empfindlichkeit: d ln r_d / d ln ω_cb = {s_cb:.3f}, d ln r_d / d ln ω_b = {s_b:.3f} (Aubourg: −0.254, −0.128)")


def inverse_ladder():
    """63. Die inverse Entfernungsleiter (Zellen 23 von cosmology_bao.ipynb)."""
    global FITS, ax, col, cov, data, dcov, dv, e, fig, key, r
    FITS = {}
    for key, data in [("BAO+BBN", ("BAO", "BBN")), ("BAO+BBN+θ*", ("BAO", "BBN", "THETA"))]:
        r = fit(data)
        cov = covariance(r.x, data)
        FITS[key] = (r, cov, derived(r.x), derived_cov(r.x, cov))
    fig, ax = plt.subplots(figsize=(10, 7))
    for (key, (r, cov, dv, dcov)), col in zip(FITS.items(), ["C0", "C3"]):
        ellipse(ax, dv[[1, 0]], dcov[np.ix_([1, 0], [1, 0])], col, label=f"DESI + {key[4:]}")
    ax.axhspan(H0_SH0ES[0] - H0_SH0ES[1], H0_SH0ES[0] + H0_SH0ES[1], color="C2", alpha=0.25, label="SH0ES")
    ax.errorbar(PLANCK["Om"], PLANCK["H0"][0], xerr=0.0073, yerr=PLANCK["H0"][1], fmt="s", color="k", label="Planck 2018")
    ax.set_xlabel(r"$\Omega_m$")
    ax.set_ylabel("H₀ [km/s/Mpc]")
    ax.set_xlim(0.26, 0.34)
    ax.set_ylim(65, 75)
    ax.set_title("H₀ ohne Cepheiden: BAO mit einem Lineal aus dem frühen Universum (68 und 95 %)", fontsize=10)
    ax.legend(fontsize=9)
    plt.show()

    for key, (r, cov, dv, dcov) in FITS.items():
        e = np.sqrt(np.diag(dcov))
        print(f"{key:11s}: H₀ = {dv[0]:.2f} ± {e[0]:.2f}, Ω_m = {dv[1]:.4f} ± {e[1]:.4f}, ω_b = {r.x[1]:.5f}, "
              f"r_d = {dv[2] / r.x[0]:.2f} Mpc, χ² = {r.fun:.2f}; gegen SH0ES {(H0_SH0ES[0] - dv[0]) / np.hypot(e[0], H0_SH0ES[1]):.1f} σ")
    print("DESI DR2: BAO+BBN 68.51 ± 0.58 (Ω_m 0.2977 ± 0.0086); BAO+BBN+θ* 68.45 ± 0.47 (Ω_m 0.2967 ± 0.0045)")


def galaxy_bump():
    """64. Der Buckel in der Verteilung der Galaxien (Zellen 26 von cosmology_bao.ipynb)."""
    global EH, P, T, ax, ax2, col, damp, eh98, fig, k, m, peak
    global r, s, smooth, w, wb_, xi
    def eh98(k, wb, wm, tcmb=2.7255):
        # Transferfunktion mit Baryonen, Eisenstein & Hu (1998), Gl. 2 bis 24; k in 1/Mpc
        th = tcmb / 2.7
        fb, fc = wb / wm, 1 - wb / wm
        zeq, keq = 2.50e4 * wm * th**-4, 7.46e-2 * wm * th**-2
        zd = z_drag(wb, wm)
        R = lambda z: 31.5 * wb * th**-4 * (z / 1e3) ** -1
        Req, Rd = R(zeq), R(zd)
        s = 2 / (3 * keq) * np.sqrt(6 / Req) * np.log((np.sqrt(1 + Rd) + np.sqrt(Rd + Req)) / (1 + np.sqrt(Req)))
        ksilk = 1.6 * wb**0.52 * wm**0.73 * (1 + (10.4 * wm) ** -0.95)
        q = k / (13.41 * keq)
        a1 = (46.9 * wm) ** 0.670 * (1 + (32.1 * wm) ** -0.532)
        a2 = (12.0 * wm) ** 0.424 * (1 + (45.0 * wm) ** -0.582)
        alpha_c = a1 ** (-fb) * a2 ** (-fb**3)
        bb1, bb2 = 0.944 / (1 + (458 * wm) ** -0.708), (0.395 * wm) ** -0.0266
        beta_c = 1 / (1 + bb1 * (fc**bb2 - 1))

        def T0(a, b):
            L = np.log(np.e + 1.8 * b * q)
            return L / (L + (14.2 / a + 386 / (1 + 69.9 * q**1.08)) * q**2)

        f = 1 / (1 + (k * s / 5.4) ** 4)
        Tc = f * T0(1, beta_c) + (1 - f) * T0(alpha_c, beta_c)
        y = (1 + zeq) / (1 + zd)
        G = y * (-6 * np.sqrt(1 + y) + (2 + 3 * y) * np.log((np.sqrt(1 + y) + 1) / (np.sqrt(1 + y) - 1)))
        alpha_b = 2.07 * keq * s * (1 + Rd) ** -0.75 * G
        beta_b = 0.5 + fb + (3 - 2 * fb) * np.sqrt((17.2 * wm) ** 2 + 1)
        s_t = s / (1 + (8.41 * wm**0.435 / (k * s)) ** 3) ** (1 / 3)
        Tb = (T0(1, 1) / (1 + (k * s / 5.2) ** 2) + alpha_b / (1 + (beta_b / (k * s)) ** 3) * np.exp(-((k / ksilk) ** 1.4))) * np.sinc(k * s_t / np.pi)
        return fb * Tb + fc * Tc, s


    k = np.logspace(-4, 1, 20000)
    r = np.linspace(20, 200, 181)
    damp = np.exp(-(k * 6.0) ** 2)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.6))
    EH = {}
    for wb_, col in [(0.005, "0.5"), (PLANCK["wb"], "C3"), (0.035, "C0")]:
        T, s = eh98(k, wb_, WM_PLANCK)
        P = k ** 0.9649 * T**2
        smooth = np.exp(ndimage.gaussian_filter1d(np.log(P), 600))
        xi = np.array([np.trapz(k**2 * P * damp * np.sinc(k * rr / np.pi), k) for rr in r]) / (2 * np.pi**2)
        peak = r[r > 120][np.argmax((r**2 * xi)[r > 120])]
        EH[wb_] = (s, peak, r**2 * xi)
        m = (k > 0.01) & (k < 0.4)
        ax.plot(k[m], P[m] / smooth[m], color=col, lw=1.4, label=f"ω_b = {wb_}")
        ax2.plot(r, r**2 * xi / np.max(np.abs(r**2 * xi)[r > 60]), color=col, lw=1.6, label=f"ω_b = {wb_}: Schallhorizont {s:.0f} Mpc")
    ax.set_xscale("log")
    ax.set_xlabel("Wellenzahl k [1/Mpc]")
    ax.set_ylabel("P(k) / geglättetes P(k)")
    ax.set_title("Baryonen prägen dem Spektrum Wellen auf", fontsize=10)
    ax.legend(fontsize=9)
    ax2.axvline(PLANCK["rd"], color="C3", ls=":", lw=1)
    ax2.set_xlabel("Abstand r [Mpc, mitbewegt]")
    ax2.set_ylabel(r"$r^2\xi(r)$, normiert")
    ax2.set_title("… und in der Korrelationsfunktion einen Buckel beim Schallhorizont", fontsize=10)
    ax2.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    for wb_, (s, peak, w) in EH.items():
        print(f"ω_b = {wb_}: Schallhorizont nach Eisenstein & Hu {s:.1f} Mpc, Buckel von r²ξ bei {peak:.0f} Mpc")
    print(f"zum Vergleich r_d aus Schritt 62: {C_PLANCK['rd']:.2f} Mpc")


def bao_vs_cmb():
    """65. BAO gegen Hintergrundstrahlung in ΛCDM (Zellen 29 von cosmology_bao.ipynb)."""
    global CMB2, T_CHI2, ax, cov_bc, cov_cmb, d, dcov_bc, dcov_cmb, dv_bc, dv_cmb, e_bc, e_cmb
    global fig, r_bc, r_cmb
    r_cmb = fit(("CMB",))
    cov_cmb = covariance(r_cmb.x, ("CMB",))
    dv_cmb, dcov_cmb = derived(r_cmb.x), derived_cov(r_cmb.x, cov_cmb)
    CMB2 = (dv_cmb[1:], dcov_cmb[1:, 1:])                     # (Ω_m, h r_d)
    d = BAO2[0] - CMB2[0]
    T_CHI2 = d @ np.linalg.inv(BAO2[1] + CMB2[1]) @ d
    r_bc = fit(("BAO", "CMB"))
    cov_bc = covariance(r_bc.x, ("BAO", "CMB"))
    dv_bc, dcov_bc = derived(r_bc.x), derived_cov(r_bc.x, cov_bc)

    fig, ax = plt.subplots(figsize=(10, 7))
    ellipse(ax, BAO2[0], BAO2[1], "C0", label="DESI BAO")
    ellipse(ax, CMB2[0], CMB2[1], "C3", label="CMB (θ*, ω_b, ω_cb), ΛCDM")
    ellipse(ax, dv_bc[1:], dcov_bc[1:, 1:], "k", label="beide zusammen")
    ax.set_xlabel(r"$\Omega_m$")
    ax.set_ylabel(r"$h\,r_d$ [Mpc]")
    ax.set_title("Zwei Wege zu Ω_m und h·r_d in ΛCDM (68 und 95 %)", fontsize=10)
    ax.legend(fontsize=9)
    plt.show()

    e_cmb, e_bc = np.sqrt(np.diag(dcov_cmb)), np.sqrt(np.diag(dcov_bc))
    print(f"CMB allein: H₀ = {dv_cmb[0]:.2f} ± {e_cmb[0]:.2f}, Ω_m = {dv_cmb[1]:.4f} ± {e_cmb[1]:.4f}, h r_d = {dv_cmb[2]:.2f} ± {e_cmb[2]:.2f}")
    print(f"Abstand BAO – CMB: Δχ² = {T_CHI2:.2f} bei 2 Freiheitsgraden → {sigma(T_CHI2):.1f} σ (DESI mit voller CMB: 2.3 σ)")
    print(f"DESI + CMB: H₀ = {dv_bc[0]:.2f} ± {e_bc[0]:.2f}, Ω_m = {dv_bc[1]:.4f} ± {e_bc[1]:.4f}, χ² = {r_bc.fun:.2f} "
          f"(DESI mit voller CMB: 68.17 ± 0.28, 0.3027 ± 0.0036)")


def three_omega_m():
    """66. Drei Messungen von Ω_m (Zellen 32 von cosmology_bao.ipynb)."""
    global OMEGAS, OM_SN, _, ax, c_sn, chi_sn, col, e, e1, e2, fig, i
    global inside, j, lab, names, oms, r_sn, v, v1, v2
    c_sn = lambda Om: cosmo(0.7, 0.0224, Om * 0.49 - OMEGA_NU)
    oms = np.linspace(0.25, 0.42, 171)
    chi_sn = np.array([chi2_sn(c_sn(o)) for o in oms])
    r_sn = optimize.minimize_scalar(lambda o: chi2_sn(c_sn(o)), bounds=(0.2, 0.5), method="bounded")
    inside = oms[chi_sn - r_sn.fun <= 1]
    OM_SN = (r_sn.x, (inside.max() - inside.min()) / 2)
    OMEGAS = {"Alcock-Paczynski (DESI)": (OM_AP, OM_AP_ERR, "C1"),
              "BAO allein (DESI)": (BAO2[0][0], np.sqrt(BAO2[1][0, 0]), "C0"),
              "CMB (θ*, ω_b, ω_cb)": (dv_cmb[1], e_cmb[1], "C3"),
              "Supernovae (Pantheon+)": (OM_SN[0], OM_SN[1], "C2"),
              "BAO + CMB": (dv_bc[1], e_bc[1], "k")}
    fig, ax = plt.subplots(figsize=(11, 4.8))
    for i, (lab, (v, e, col)) in enumerate(OMEGAS.items()):
        ax.errorbar(v, -i, xerr=e, fmt="o", color=col, ms=8, capsize=4)
    ax.set_yticks(-np.arange(len(OMEGAS)))
    ax.set_yticklabels(list(OMEGAS), fontsize=10)
    ax.set_xlabel(r"$\Omega_m$ (flaches ΛCDM)")
    ax.set_title("Wie viel Materie verlangt jede Messung für sich?", fontsize=10)
    plt.tight_layout()
    plt.show()

    for lab, (v, e, _) in OMEGAS.items():
        print(f"{lab:26s}: Ω_m = {v:.4f} ± {e:.4f}")
    names = ["BAO allein (DESI)", "CMB (θ*, ω_b, ω_cb)", "Supernovae (Pantheon+)"]
    for i in range(3):
        for j in range(i + 1, 3):
            (v1, e1, _), (v2, e2, _) = OMEGAS[names[i]], OMEGAS[names[j]]
            print(f"{names[i]} gegen {names[j]}: {abs(v1 - v2) / np.hypot(e1, e2):.1f} σ")
    print(f"Supernovae: χ² = {r_sn.fun:.1f} bei {len(Z_SN)} Lichtkurven; DESI Tabelle V: DESI 0.2975, CMB 0.3169; Pantheon+ (Brout et al. 2022): 0.334 ± 0.018")


def w0wa():
    """67. Dunkle Energie mit w₀ und w_a (Zellen 35 von cosmology_bao.ipynb)."""
    global COMBOS, DESI_TAB6, W_FITS, ax, base, c_l, c_w, col, d, data, fig, j
    global key, kk, lab, m, mk, rl, rw, zz
    COMBOS = {"DESI": ("BAO",), "DESI+CMB": ("BAO", "CMB"), "DESI+Pantheon+": ("BAO", "SN"), "DESI+CMB+Pantheon+": ("BAO", "CMB", "SN")}
    DESI_TAB6 = {"DESI": (-4.7, 1.7), "DESI+CMB": (-8.0, 2.4), "DESI+Pantheon+": (-4.9, 1.7), "DESI+CMB+Pantheon+": (-10.7, 2.8)}
    W_FITS = {}
    for key, data in COMBOS.items():
        rl = fit(data)
        rw = fit(data, "w0wa", start=list(rl.x) + [-0.8, -0.6])
        W_FITS[key] = (rl, rw)

    c_l = cosmo(*unpack(W_FITS["DESI+CMB"][0].x, "lcdm"))
    c_w = cosmo(*unpack(W_FITS["DESI+CMB"][1].x, "w0wa"))
    base = bao_model(c_l)
    zz = np.linspace(0.05, 2.6, 300)
    fig, ax = plt.subplots(figsize=(13, 6))
    for kk, (col, mk, lab, j) in {"DM_over_rs": ("C0", "o", r"$D_M/r_d$", 0), "DH_over_rs": ("C3", "s", r"$D_H/r_d$", 1),
                                  "DV_over_rs": ("C2", "D", r"$D_V/r_d$", 2)}.items():
        m = KIND == kk
        ax.errorbar(Z_BAO[m], Y_BAO[m] / base[m], yerr=ERR_BAO[m] / base[m], fmt=mk, color=col, ms=7, capsize=3, label="DESI " + lab)
        ax.plot(zz, (distances(c_w, zz)[j] / c_w["rd"]) / (distances(c_l, zz)[j] / c_l["rd"]), color=col, lw=1.4)
    ax.axhline(1, color="k", lw=1)
    ax.plot([], [], color="0.4", lw=1.4, label="bestes w₀w_a-Modell")
    ax.set_xlabel("Rotverschiebung z")
    ax.set_ylabel("relativ zum besten ΛCDM-Modell (DESI + CMB)")
    ax.set_title("Wo w₀w_aCDM die Daten besser trifft (DESI + CMB)", fontsize=10)
    ax.legend(fontsize=9, ncol=2)
    plt.show()

    print("Kombination           χ²(ΛCDM)  χ²(w₀w_a)    Δχ²     σ     w₀      w_a     DESI Tab. VI")
    for key, (rl, rw) in W_FITS.items():
        d = rw.fun - rl.fun
        print(f"{key:20s} {rl.fun:9.2f} {rw.fun:10.2f} {d:7.2f} {sigma(-d):5.1f} {rw.x[3]:7.3f} {rw.x[4]:7.3f}     "
              f"{DESI_TAB6[key][0]} ({DESI_TAB6[key][1]} σ)")
    print("DESI Tab. VI mit voller CMB: DESI+CMB −12.5 (3.1 σ), DESI+CMB+Pantheon+ −10.7 (2.8 σ); "
          "DESI+(θ*, ω_b, ω_cb)CMB −8.0 (2.4 σ). Der Wert für DESI+CMB+Pantheon+ stammt aus der vollen CMB.")


def w0wa_mcmc():
    """68. Welche Werte von w₀ und w_a erlaubt sind (MCMC) (Zellen 38 von cosmology_bao.ipynb)."""
    global CHAINS, H, acc, ax, ch, col, dv, fig, key, lam, levels, metropolis
    global t0, xc, xe, yc, ye
    def metropolis(data, start, n=20000, seed=11):
        rng = np.random.default_rng(seed)
        p = np.array(start, float)
        f = total(p, data, "w0wa")
        try:
            cov0 = covariance(p, data, "w0wa")
            L = np.linalg.cholesky(cov0 * 2.38**2 / len(p))
        except np.linalg.LinAlgError:
            L = np.diag([5e-3, 1e-4, 5e-4, 0.05, 0.2]) * 2.38 / np.sqrt(len(p))
        chain, acc = np.empty((n, len(p))), 0
        for i in range(n):
            q = p + L @ rng.normal(size=len(p))
            g = total(q, data, "w0wa")
            if g < f or rng.random() < np.exp((f - g) / 2):
                p, f, acc = q, g, acc + 1
            chain[i] = p
            if i == n // 4:                                  # Vorschläge einmal an die bisherige Kette anpassen
                L = np.linalg.cholesky(np.cov(chain[n // 8:i].T) * 2.38**2 / len(p) + 1e-12 * np.eye(len(p)))
        return chain[n // 4:], acc / n


    def levels(H, fracs=(0.68, 0.95)):
        v = np.sort(H.ravel())[::-1]
        c = np.cumsum(v) / v.sum()
        return sorted(v[np.searchsorted(c, f)] for f in fracs)


    t0 = time.time()
    CHAINS = {key: metropolis(COMBOS[key], W_FITS[key][1].x) for key in ["DESI+CMB", "DESI+CMB+Pantheon+"]}
    fig, ax = plt.subplots(figsize=(10, 7.5))
    for (key, (ch, acc)), col in zip(CHAINS.items(), ["C0", "C3"]):
        H, xe, ye = np.histogram2d(ch[:, 3], ch[:, 4], bins=60, range=[[-1.6, 0.4], [-3.0, 1.0]])
        H = ndimage.gaussian_filter(H, 1.5)
        xc, yc = (xe[1:] + xe[:-1]) / 2, (ye[1:] + ye[:-1]) / 2
        ax.contourf(xc, yc, H.T, levels=levels(H) + [H.max()], colors=[col, col], alpha=0.25)
        ax.contour(xc, yc, H.T, levels=levels(H), colors=[col], linewidths=[1, 1.8])
        ax.plot([], [], color=col, lw=6, alpha=0.5, label=key)
    ax.plot(-1, 0, "k*", ms=16, label="ΛCDM")
    ax.errorbar(-0.43, -1.72, xerr=0.22, yerr=0.64, fmt="s", color="C0", mfc="none", ms=8, label="DESI: DESI+(θ*, ω_b, ω_cb)CMB")
    ax.errorbar(-0.838, -0.62, xerr=0.055, yerr=0.2, fmt="s", color="C3", mfc="none", ms=8, label="DESI: DESI+CMB+Pantheon+")
    ax.axhline(0, color="0.6", lw=0.8, ls=":")
    ax.axvline(-1, color="0.6", lw=0.8, ls=":")
    ax.plot([-1.6, 0.4], [1.6, -0.4], color="0.6", lw=0.8, ls="--")
    ax.text(0.15, -0.35, "w₀ + w_a = 0", fontsize=8, color="0.4", rotation=-40)
    ax.set_xlim(-1.6, 0.4)
    ax.set_ylim(-3.0, 1.0)
    ax.set_xlabel(r"$w_0$")
    ax.set_ylabel(r"$w_a$")
    ax.set_title("Posterior von w₀ und w_a (eigener MCMC, 68 und 95 %)", fontsize=10)
    ax.legend(fontsize=9, loc="lower left")
    plt.show()

    for key, (ch, acc) in CHAINS.items():
        dv = np.array([derived(p, "w0wa") for p in ch[::20]])
        lam = np.mean((ch[:, 3] > -1) & (ch[:, 4] < 0))
        print(f"{key}: Akzeptanz {100 * acc:.0f} %, w₀ = {ch[:, 3].mean():.3f} ± {ch[:, 3].std():.3f}, w_a = {ch[:, 4].mean():.2f} ± {ch[:, 4].std():.2f}, "
              f"H₀ = {dv[:, 0].mean():.2f} ± {dv[:, 0].std():.2f}, Ω_m = {dv[:, 1].mean():.4f} ± {dv[:, 1].std():.4f}; "
              f"Anteil mit w₀ > −1 und w_a < 0: {100 * lam:.0f} %")
    print("DESI Tabelle V: DESI+(θ*, ω_b, ω_cb)CMB w₀ = −0.43 ± 0.22, w_a = −1.72 ± 0.64, Ω_m = 0.353 ± 0.022, H₀ = 63.7 +1.7/−2.2; "
          "DESI+CMB+Pantheon+ w₀ = −0.838 ± 0.055, w_a = −0.62 +0.22/−0.19, Ω_m = 0.3114 ± 0.0057, H₀ = 67.51 ± 0.59")
    print(f"Rechenzeit der Ketten: {time.time() - t0:.0f} s")


def w0wa_meaning():
    """69. Was w₀ und w_a für die Dunkle Energie bedeuten (Zellen 41 von cosmology_bao.ipynb)."""
    global a, ax, ax2, axx, best, ch, cross, draw, fig, hi, lab, lo
    global med, rho, rho_b, w, w0b, wab, y, z_cross, zz
    ch = CHAINS["DESI+CMB+Pantheon+"][0]
    draw = ch[np.random.default_rng(3).choice(len(ch), 2000, replace=False)]
    zz = np.linspace(0, 2.5, 251)
    a = 1 / (1 + zz)
    w = draw[:, 3:4] + draw[:, 4:5] * (1 - a)
    rho = a ** (-3 * (1 + draw[:, 3:4] + draw[:, 4:5])) * np.exp(-3 * draw[:, 4:5] * (1 - a))
    best = W_FITS["DESI+CMB+Pantheon+"][1].x
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.6))
    for axx, y, lab in [(ax, w, r"$w(z)$"), (ax2, rho, r"$\rho_\mathrm{DE}(z)/\rho_\mathrm{DE,0}$")]:
        lo, med, hi = np.percentile(y, [16, 50, 84], axis=0)
        axx.fill_between(zz, lo, hi, color="C3", alpha=0.3, label="68 % der Posterior (DESI + CMB + Pantheon+)")
        axx.plot(zz, med, color="C3", lw=1.6, label="Median")
        axx.axhline(-1 if axx is ax else 1, color="k", lw=1.2, label="ΛCDM")
        axx.set_xlabel("Rotverschiebung z")
        axx.set_ylabel(lab)
        axx.legend(fontsize=9)
    ax.set_title("Zustandsgleichung der Dunklen Energie", fontsize=10)
    ax2.set_title("Dichte der Dunklen Energie relativ zu heute", fontsize=10)
    plt.tight_layout()
    plt.show()

    w0b, wab = best[3], best[4]
    z_cross = 1 / (1 + (1 + w0b) / wab) - 1
    rho_b = a ** (-3 * (1 + w0b + wab)) * np.exp(-3 * wab * (1 - a))
    cross = 1 / (1 + (1 + draw[:, 3]) / draw[:, 4]) - 1
    print(f"bestes Modell: w₀ = {w0b:.3f}, w_a = {wab:.3f}; w = −1 bei z = {z_cross:.2f}; Maximum der Dichte bei z = {zz[np.argmax(rho_b)]:.2f} "
          f"({rho_b.max():.3f} × heute); früh (z = 2.5) w = {w0b + wab * (1 - a[-1]):.2f}")
    print(f"Kreuzung in den Stichproben: Median z = {np.median(cross[(cross > 0) & (cross < 10)]):.2f}, "
          f"68 % zwischen {np.percentile(cross[(cross > 0) & (cross < 10)], 16):.2f} und {np.percentile(cross[(cross > 0) & (cross < 10)], 84):.2f}")
    print(f"Dichte bei z = 0.5: {np.median(rho[:, 50]):.3f} × heute ({np.percentile(rho[:, 50], 16):.3f} bis {np.percentile(rho[:, 50], 84):.3f})")


def literature():
    """70. Gegen DESI DR2 und die Entfernungsleiter (Zellen 44 von cosmology_bao.ipynb)."""
    global acc, ax, ch, col, desi, dvw, e, e4, fig, i, key, lab
    global own, rows, v
    own = {"BAO+BBN": (FITS["BAO+BBN"][2][0], np.sqrt(FITS["BAO+BBN"][3][0, 0])),
           "BAO+BBN+θ*": (FITS["BAO+BBN+θ*"][2][0], np.sqrt(FITS["BAO+BBN+θ*"][3][0, 0])),
           "BAO+CMB (ΛCDM)": (dv_bc[0], e_bc[0])}
    dvw = np.array([derived(p, "w0wa") for p in CHAINS["DESI+CMB+Pantheon+"][0][::20]])
    own["BAO+CMB+Pantheon+ (w₀w_a)"] = (dvw[:, 0].mean(), dvw[:, 0].std())
    desi = {"BAO+BBN": (68.51, 0.58), "BAO+BBN+θ*": (68.45, 0.47), "BAO+CMB (ΛCDM)": (68.17, 0.28), "BAO+CMB+Pantheon+ (w₀w_a)": (67.51, 0.59)}
    rows = []
    for key in own:
        rows += [(f"eigen: {key}", *own[key], "C0"), (f"DESI DR2: {key}", *desi[key], "C3")]
    rows += [("Planck 2018 (TT,TE,EE+lowE+lensing)", *PLANCK["H0"], "k"), ("Die akustischen Peaks: θ* + Ω_m aus Pantheon+", 66.71, 1.08, "k"),
             ("SH0ES (Riess et al. 2022)", *H0_SH0ES, "C2")]
    fig, ax = plt.subplots(figsize=(12, 6.5))
    for i, (lab, v, e, col) in enumerate(rows):
        ax.errorbar(v, -i, xerr=e, fmt="o", color=col, ms=7, capsize=4)
    ax.set_yticks(-np.arange(len(rows)))
    ax.set_yticklabels([r[0] for r in rows], fontsize=9.5)
    ax.axvspan(H0_SH0ES[0] - H0_SH0ES[1], H0_SH0ES[0] + H0_SH0ES[1], color="C2", alpha=0.15)
    ax.set_xlabel("H₀ [km/s/Mpc]")
    ax.set_title("H₀ aus der inversen Entfernungsleiter gegen die Cepheiden", fontsize=10)
    plt.tight_layout()
    plt.show()

    e4 = np.sqrt(np.diag(BAO2[1]))
    print(f"BAO allein:  Ω_m {BAO2[0][0]:.4f} ± {e4[0]:.4f} (DESI 0.2975 ± 0.0086), h r_d {BAO2[0][1]:.2f} ± {e4[1]:.2f} (101.54 ± 0.73)")
    for key in own:
        v, e = own[key]
        print(f"{key:28s}: H₀ = {v:.2f} ± {e:.2f} (DESI {desi[key][0]} ± {desi[key][1]}), gegen SH0ES {(H0_SH0ES[0] - v) / np.hypot(e, H0_SH0ES[1]):.1f} σ")
    for key, (ch, acc) in CHAINS.items():
        print(f"{key:28s}: w₀ = {ch[:, 3].mean():.3f} ± {ch[:, 3].std():.3f}, w_a = {ch[:, 4].mean():.2f} ± {ch[:, 4].std():.2f}")
