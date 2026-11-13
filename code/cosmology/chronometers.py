"""Kosmische Chronometer: H(z) aus dem Alter passiv alternder Galaxien, Fehlerhaushalt, ΛCDM-Fit, Gauß-Prozess, Beginn der Beschleunigung und Eichung von BAO und Supernovae.

Für cosmology.ipynb aus cosmology_chronometers.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, measurements, error_budget, clock_precision, lcdm_fit, gaussian_process, acceleration_onset, calibrate_ruler, with_bao, calibrate_candles, literature.
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
    """46. Daten (Zellen 4, 6 von cosmology_chronometers.ipynb)."""
    global ASTRODATA, CC_DIR, CC_URL, COV, COV_BAO, COV_CC, COV_PARTS, C_KMS, DESI_DIR, DESI_URL, E, ETA
    global E_CC, H0_SH0ES, HRD_BAO, H_CC, IC_BAO, IC_CC, IC_CC_DIAG, IC_SN, IC_SN_SUM, KIND, M_B_CEPHEID, M_SN
    global N, OMEGA_R, PANTHEON, PANTHEON_URL, PLANCK, RD_HJV, REF_CC, SN, Y_BAO, ZG, ZHEL_SN, Z_BAO
    global Z_CC, Z_SN, cc, chi2_bao, chi2_cc, chi2_sn, comoving, download, eta, fit, gp_fit, gp_predict
    global interval, kern, name, profile, tab, total, use
    ASTRODATA = cosmodata.DATA


    C_KMS, OMEGA_R = 299792.458, 4.18e-5                     # c [km/s]; ω_r von Photonen und Neutrinos
    CC_URL = "https://gitlab.com/mmoresco/CCcovariance/-/raw/master/data/"
    DESI_URL = "https://raw.githubusercontent.com/CobayaSampler/bao_data/master/desi_bao_dr2/"
    PANTHEON_URL = "https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/main/Pantheon%2B_Data/4_DISTANCES_AND_COVAR/"
    CC_DIR, DESI_DIR, PANTHEON = ASTRODATA / "chronometers", ASTRODATA / "desi", ASTRODATA / "pantheon"
    PLANCK = dict(H0=(67.36, 0.54), Om=(0.3153, 0.0073), rd=(147.09, 0.26))
    H0_SH0ES = (73.04, 1.04)
    M_B_CEPHEID = (-19.249, 0.030)                            # Das Hubble-Diagramm (Cepheiden, SH0ES)
    HRD_BAO = (101.55, 0.74)                                  # h·r_d aus den BAO allein (Baryonische akustische Oszillationen)
    RD_HJV = (142.8, 3.7)                                     # Heavens, Jimenez & Verde 2014 (Uhren und BAO)


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


    cc = np.genfromtxt(download(CC_URL + "HzTable_MM_BC03.dat", CC_DIR / "HzTable_MM_BC03.dat", lambda d: d.startswith(b"# z")),
                       delimiter=",", comments="#", dtype=None, encoding="utf-8")
    Z_CC = np.array([r[0] for r in cc]); H_CC = np.array([r[1] for r in cc]); E_CC = np.array([r[2] for r in cc])
    REF_CC = np.array([r[5] for r in cc])
    eta = np.genfromtxt(download(CC_URL + "data_MM20.dat", CC_DIR / "data_MM20.dat", lambda d: d.startswith(b"# z")), comments="#")
    ETA = {name: np.interp(Z_CC, eta[:, 0], eta[:, col]) / 100 for name, col in [("IMF", 1), ("Sternbibliothek", 2), ("SPS", 3), ("SPS ohne Ausreißer", 4)]}
    COV_PARTS = {"statistisch + Metallizität": np.diag(E_CC**2),
                 "IMF": np.outer(H_CC * ETA["IMF"], H_CC * ETA["IMF"]),
                 "Modell (SPS)": np.outer(H_CC * ETA["SPS ohne Ausreißer"], H_CC * ETA["SPS ohne Ausreißer"])}
    COV_CC = sum(COV_PARTS.values())                          # wie Moresco et al. 2020 (CC_covariance.ipynb)
    IC_CC, IC_CC_DIAG = np.linalg.inv(COV_CC), np.diag(1 / E_CC**2)

    name = "desi_gaussian_bao_ALL_GCcomb_"
    tab = np.loadtxt(download(DESI_URL + name + "mean.txt", DESI_DIR / (name + "mean.txt"), lambda d: d.startswith(b"# [z]")), dtype=str)
    Z_BAO, Y_BAO, KIND = tab[:, 0].astype(float), tab[:, 1].astype(float), tab[:, 2]
    COV_BAO = np.loadtxt(download(DESI_URL + name + "cov.txt", DESI_DIR / (name + "cov.txt"), lambda d: d[:1].isdigit()))
    IC_BAO = np.linalg.inv(COV_BAO)

    SN = pd.read_csv(download(PANTHEON_URL + "Pantheon%2BSH0ES.dat", PANTHEON / "Pantheon+SH0ES.dat", lambda d: d.startswith(b"CID")), sep=r"\s+")
    N = len(SN)
    COV = np.loadtxt(download(PANTHEON_URL + "Pantheon%2BSH0ES_STAT%2BSYS.cov", PANTHEON / "Pantheon+SH0ES_STAT+SYS.cov",
                              lambda d: d.split(b"\n", 1)[0].strip() == b"1701"), skiprows=1).reshape(N, N)
    COV = (COV + COV.T) / 2
    use = SN["zHD"].values > 0.01
    Z_SN, ZHEL_SN, M_SN = SN["zHD"].values[use], SN["zHEL"].values[use], SN["m_b_corr"].values[use]
    IC_SN = np.linalg.inv(COV[np.ix_(use, use)])
    IC_SN_SUM = IC_SN.sum()

    print(f"Chronometer: {len(Z_CC)} Messungen bei z = {Z_CC.min()} bis {Z_CC.max()}, Fehler {100 * (E_CC / H_CC).min():.0f} bis {100 * (E_CC / H_CC).max():.0f} %")
    print(f"DESI: {len(Y_BAO)} BAO-Werte; Pantheon+: {use.sum()} Supernovae mit z > 0.01")

    ZG = np.linspace(0, 2.5, 2501)


    def E(z, H0, Om):
        o_r = OMEGA_R / (H0 / 100) ** 2
        return np.sqrt(Om * (1 + z) ** 3 + o_r * (1 + z) ** 4 + 1 - Om - o_r)


    def comoving(H0, Om):
        f = 1 / E(ZG, H0, Om)
        return C_KMS / H0 * np.concatenate([[0.0], np.cumsum((f[1:] + f[:-1]) / 2 * np.diff(ZG))])


    def chi2_cc(H0, Om, ic=None):
        r = H_CC - H0 * E(Z_CC, H0, Om)
        return r @ (IC_CC if ic is None else ic) @ r


    def chi2_bao(H0, Om, rd):
        DM = np.interp(Z_BAO, ZG, comoving(H0, Om))
        DH = C_KMS / (H0 * E(Z_BAO, H0, Om))
        DV = (Z_BAO * DM**2 * DH) ** (1 / 3)
        r = Y_BAO - np.select([KIND == "DM_over_rs", KIND == "DH_over_rs"], [DM, DH], DV) / rd
        return r @ IC_BAO @ r


    def chi2_sn(H0, Om, return_M=False):
        r = M_SN - 5 * np.log10((1 + ZHEL_SN) * np.interp(Z_SN, ZG, comoving(H0, Om))) - 25
        a = IC_SN @ r
        chi = r @ a - a.sum() ** 2 / IC_SN_SUM
        return (chi, a.sum() / IC_SN_SUM) if return_M else chi


    def total(p, data):
        H0, Om, rd = p
        if not (20 < H0 < 150 and 0.01 < Om < 1.0 and 50 < rd < 300):
            return 1e10
        return (chi2_cc(H0, Om) if "CC" in data else 0) + (chi2_bao(H0, Om, rd) if "BAO" in data else 0) \
            + (chi2_sn(H0, Om) if "SN" in data else 0)


    def fit(data, start=(68.0, 0.3, 147.0)):
        best = None
        p = np.array(start)
        for _ in range(3):
            r = optimize.minimize(total, p, args=(data,), method="Nelder-Mead", options=dict(xatol=1e-7, fatol=1e-8, maxiter=20000))
            p = r.x
            if best is None or r.fun < best.fun - 1e-8:
                best = r
        return best


    def profile(data, index, values, best):
        # χ² minimiert über die übrigen Parameter, für jeden Wert des Parameters index, relativ zum Minimum
        free = [i for i in range(3) if i != index]
        out = []
        for v in values:
            def f(q):
                p = np.empty(3)
                p[index], p[free] = v, q
                return total(p, data)
            out.append(optimize.minimize(f, best.x[free], method="Nelder-Mead", options=dict(xatol=1e-6, fatol=1e-7)).fun)
        return np.array(out) - best.fun


    def interval(values, dchi2, level=1.0):
        ok = values[dchi2 <= level]
        return ok.min(), ok.max()


    def kern(a, b, sf, l):
        return sf**2 * np.exp(-((a[:, None] - b[None, :]) ** 2) / (2 * l**2))


    def gp_fit(cov):
        # σ_f und ℓ mit der größten Randwahrscheinlichkeit (Mittelwert null)
        def nlml(th):
            sf, l = np.exp(th)
            L = np.linalg.cholesky(kern(Z_CC, Z_CC, sf, l) + cov)
            alpha = np.linalg.solve(L.T, np.linalg.solve(L, H_CC))
            return 0.5 * H_CC @ alpha + np.log(np.diag(L)).sum()
        r = optimize.minimize(nlml, np.log([150.0, 2.0]), method="Nelder-Mead")
        return np.exp(r.x)


    def gp_predict(zs, cov, sf, l):
        # gemeinsames Mittel und Kovarianz von (H(zs), H'(zs)) unter dem Gauß-Prozess
        Ki = np.linalg.inv(kern(Z_CC, Z_CC, sf, l) + cov)
        d = zs[:, None] - Z_CC[None, :]
        k0 = kern(zs, Z_CC, sf, l)
        k1 = -d / l**2 * k0                                    # Kovarianz von H'(z*) und H(z_i)
        dd = zs[:, None] - zs[None, :]
        kss = kern(zs, zs, sf, l)
        K11 = kss * (1 - dd**2 / l**2) / l**2                  # Kovarianz von H'(z*) und H'(z*')
        K01 = dd / l**2 * kss                                  # Kovarianz von H(z*) und H'(z*')
        A = np.vstack([k0, k1])
        mean = A @ Ki @ H_CC
        prior = np.block([[kss, K01], [K01.T, K11]])
        return mean, prior - A @ Ki @ A.T


    print(f"Kovarianz: Determinante {np.linalg.det(COV_CC):.3e}, Bedingungszahl {np.linalg.cond(COV_CC):.0f}")


def measurements():
    """47. Die Messungen (Zellen 8 von cosmology_chronometers.ipynb)."""
    global H0, a_, ax, ax2, col, e, fig, h, lab, m, r, ref
    global y, zi, zz
    zz = np.linspace(0, 2.1, 300)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    for ref, col in zip(dict.fromkeys(REF_CC), ["C0", "C1", "C2"]):
        m = REF_CC == ref
        for a_, y in [(ax, H_CC), (ax2, H_CC / (1 + Z_CC))]:
            a_.errorbar(Z_CC[m], y[m], yerr=E_CC[m] / (1 if a_ is ax else 1 + Z_CC[m]), fmt="o", color=col, ms=7, capsize=3, label=ref)
    for H0, col, lab in [(PLANCK["H0"][0], "k", "Planck-ΛCDM (H₀ = 67.36)"), (H0_SH0ES[0], "C3", "gleiche Form, H₀ = 73.04")]:
        ax.plot(zz, H0 * E(zz, H0, PLANCK["Om"][0]), color=col, lw=1.4, label=lab)
        ax2.plot(zz, H0 * E(zz, H0, PLANCK["Om"][0]) / (1 + zz), color=col, lw=1.4, label=lab)
    ax.set_xlabel("Rotverschiebung z")
    ax.set_ylabel("H(z) [km/s/Mpc]")
    ax.set_title("Expansionsrate aus dem Alter passiver Galaxien", fontsize=10)
    ax.legend(fontsize=9)
    ax2.set_xlabel("Rotverschiebung z")
    ax2.set_ylabel(r"$H(z)/(1+z) = \dot a/a_0$ [km/s/Mpc]")
    ax2.set_title("Wächst der Skalenfaktor heute schneller als früher?", fontsize=10)
    ax2.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    for H0, lab in [(PLANCK["H0"][0], "Planck"), (H0_SH0ES[0], "H₀ = 73.04")]:
        r = (H_CC - H0 * E(Z_CC, H0, PLANCK["Om"][0])) / E_CC
        print(f"gegen {lab:10s}: χ² (nur Diagonale) = {np.sum(r**2):.1f} bei {len(r)} Werten, mittlere Abweichung {r.mean():+.2f} σ")
    for zi, h, e, ref in zip(Z_CC, H_CC, E_CC, REF_CC):
        print(f"z = {zi:.4f}: H = {h:6.1f} ± {e:4.1f} ({100 * e / h:4.1f} %)  {ref}")


def error_budget():
    """48. Der Fehlerhaushalt und die Kovarianz (Zellen 11 von cosmology_chronometers.ipynb)."""
    global ax, ax2, ci, corr, cv, cy, fig, im, k, lab, off, one
    global rel, st, v, y
    rel = {"Tabelle (Statistik + Metallizität)": E_CC / H_CC, "IMF": ETA["IMF"], "Modell (SPS, ohne Ausreißer)": ETA["SPS ohne Ausreißer"],
           "Modell (SPS, alle Modelle)": ETA["SPS"], "Sternbibliothek (nicht verwendet)": ETA["Sternbibliothek"]}
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    for (k, v), st in zip(rel.items(), ["o-", "s-", "D-", "D--", "^:"]):
        ax.plot(Z_CC, 100 * v, st, ms=5, label=k)
    ax.set_xlabel("Rotverschiebung z")
    ax.set_ylabel("relativer Fehler von H(z) [%]")
    ax.set_title("Woher die Fehler kommen", fontsize=10)
    ax.legend(fontsize=9)
    corr = COV_CC / np.sqrt(np.outer(np.diag(COV_CC), np.diag(COV_CC)))
    im = ax2.imshow(corr, cmap="viridis", vmin=0, vmax=1)
    ax2.set_xticks(range(len(Z_CC)))
    ax2.set_xticklabels([f"{x:.2f}" for x in Z_CC], rotation=90, fontsize=8)
    ax2.set_yticks(range(len(Z_CC)))
    ax2.set_yticklabels([f"{x:.2f}" for x in Z_CC], fontsize=8)
    ax2.set_xlabel("z")
    ax2.set_ylabel("z")
    ax2.set_title("Korrelation der Fehler (volle Kovarianz)", fontsize=10)
    plt.colorbar(im, ax=ax2, shrink=0.85, label="Korrelationskoeffizient")
    plt.tight_layout()
    plt.show()

    y = H_CC / (PLANCK["H0"][0] * E(Z_CC, PLANCK["H0"][0], PLANCK["Om"][0]))
    for lab, cv in [("nur Diagonale", np.diag(E_CC**2)), ("volle Kovarianz", COV_CC)]:
        cy = cv / np.outer(H_CC / y, H_CC / y)
        ci = np.linalg.inv(cy)
        one = np.ones(len(y))
        print(f"H/H_Planck gemittelt, {lab:16s}: {(one @ ci @ y) / (one @ ci @ one):.3f} ± {1 / np.sqrt(one @ ci @ one):.3f}")
    off = corr[~np.eye(len(Z_CC), dtype=bool)]
    print(f"Korrelationen außerhalb der Diagonale: {off.min():.2f} bis {off.max():.2f}, Median {np.median(off):.2f}")
    print(f"mittlere relative Fehler: Tabelle {100 * np.mean(E_CC / H_CC):.1f} %, IMF {100 * np.mean(ETA['IMF']):.2f} %, "
          f"SPS {100 * np.mean(ETA['SPS ohne Ausreißer']):.1f} % (mit allen Modellen {100 * np.mean(ETA['SPS']):.1f} %)")


def clock_precision():
    """49. Wie genau muss die Uhr gehen? (Zellen 14 von cosmology_chronometers.ipynb)."""
    global DT, GYR, H0, a1, a2, a_, age, ax, ax2, col, dt, fig
    global k, t, z0, zt
    GYR = 977.8                                                # 1/(km/s/Mpc) in Gyr
    zt = np.linspace(0, 3, 601)


    def age(z, H0, Om, zmax=1e4):
        zz_ = np.concatenate([np.linspace(z, 20, 4000), np.logspace(np.log10(20.01), np.log10(zmax), 2000)])
        f = 1 / ((1 + zz_) * H0 * E(zz_, H0, Om))
        return GYR * np.sum((f[1:] + f[:-1]) / 2 * np.diff(zz_))


    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.6))
    DT = {}
    for H0, col in [(PLANCK["H0"][0], "k"), (H0_SH0ES[0], "C3")]:
        t = np.array([age(x, H0, PLANCK["Om"][0]) for x in zt])
        dt = np.array([age(x - 0.05, H0, PLANCK["Om"][0]) - age(x + 0.05, H0, PLANCK["Om"][0]) for x in zt[(zt >= 0.05)]])
        DT[H0] = (zt[zt >= 0.05], dt)
        ax.plot(zt, t, color=col, lw=1.6, label=f"H₀ = {H0}")
        ax2.plot(zt[zt >= 0.05], 1e3 * dt, color=col, lw=1.6, label=f"H₀ = {H0}")
    ax2.plot(DT[PLANCK["H0"][0]][0], 1e3 * (DT[PLANCK["H0"][0]][1] - DT[H0_SH0ES[0]][1]), color="C0", ls="--", lw=1.4, label="Unterschied")
    for a_ in (ax, ax2):
        a_.set_xlabel("Rotverschiebung z")
        a_.legend(fontsize=9)
    ax.set_ylabel("Alter des Universums [Gyr]")
    ax.set_title("Wie alt war das Universum bei z?", fontsize=10)
    ax2.set_ylabel("Zeit zwischen z − 0.05 und z + 0.05 [Myr]")
    ax2.set_title("Welche Altersunterschiede die Uhr auflösen muss", fontsize=10)
    plt.tight_layout()
    plt.show()

    for H0 in (PLANCK["H0"][0], H0_SH0ES[0]):
        print(f"H₀ = {H0}: Alter heute {age(0, H0, PLANCK['Om'][0]):.2f} Gyr, bei z = 0.5 {age(0.5, H0, PLANCK['Om'][0]):.2f} Gyr, "
              f"bei z = 1.97 {age(1.965, H0, PLANCK['Om'][0]):.2f} Gyr")
    for z0 in (0.2, 0.5, 1.0, 1.5):
        k = np.argmin(np.abs(DT[PLANCK["H0"][0]][0] - z0))
        a1, a2 = DT[PLANCK["H0"][0]][1][k], DT[H0_SH0ES[0]][1][k]
        print(f"z = {z0}: Δt = {1e3 * a1:.0f} Myr (Planck), {1e3 * a2:.0f} Myr (73.04), Unterschied {1e3 * (a1 - a2):.0f} Myr; "
              f"5 % von Δt sind {50 * a1:.0f} Myr")


def lcdm_fit():
    """50. H₀ und Ω_m aus den Uhren in ΛCDM (Zellen 17 von cosmology_chronometers.ipynb)."""
    global FIT4, ax, chi, col, fig, grid, h_g, hi, ic, lab, lo, om_g
    global prof, r, x
    FIT4 = {}
    om_g, h_g = np.linspace(0.05, 0.75, 141), np.linspace(50, 85, 141)
    fig, ax = plt.subplots(figsize=(10, 7))
    for lab, ic, col in [("volle Kovarianz", IC_CC, "C0"), ("nur Diagonale", IC_CC_DIAG, "C1")]:
        r = optimize.minimize(lambda q: chi2_cc(*q, ic=ic), [68, 0.3], method="Nelder-Mead", options=dict(xatol=1e-8, fatol=1e-10))
        grid = np.array([[chi2_cc(h, o, ic=ic) for o in om_g] for h in h_g]) - r.fun
        prof = grid.min(axis=1)
        lo, hi = interval(h_g, prof)
        FIT4[lab] = (r.x, r.fun, lo, hi)
        ax.contour(om_g, h_g, grid, levels=[2.30, 6.18], colors=[col], linewidths=[1.8, 1])
        ax.plot(*r.x[::-1], "+", color=col, ms=14, mew=2)
        ax.plot([], [], color=col, lw=2, label=f"Chronometer, {lab}")
    ax.errorbar(PLANCK["Om"][0], PLANCK["H0"][0], xerr=PLANCK["Om"][1], yerr=PLANCK["H0"][1], fmt="s", color="k", label="Planck 2018")
    ax.axhspan(H0_SH0ES[0] - H0_SH0ES[1], H0_SH0ES[0] + H0_SH0ES[1], color="C2", alpha=0.25, label="SH0ES")
    ax.set_xlabel(r"$\Omega_m$")
    ax.set_ylabel("H₀ [km/s/Mpc]")
    ax.set_title("Was die Uhren in flachem ΛCDM festlegen (68 und 95 %)", fontsize=10)
    ax.legend(fontsize=9)
    plt.show()

    for lab, (x, chi, lo, hi) in FIT4.items():
        print(f"{lab:16s}: H₀ = {x[0]:.2f} (68 %: {lo:.1f} bis {hi:.1f}, also ± {(hi - lo) / 2:.1f}), Ω_m = {x[1]:.3f}, χ² = {chi:.2f} bei {len(Z_CC) - 2} Freiheitsgraden")
    x = FIT4["volle Kovarianz"]
    print(f"Abstand zu SH0ES: {(H0_SH0ES[0] - x[0][0]) / np.hypot((x[3] - x[2]) / 2, H0_SH0ES[1]):.1f} σ, zu Planck: {(x[0][0] - PLANCK['H0'][0]) / np.hypot((x[3] - x[2]) / 2, PLANCK['H0'][1]):+.1f} σ")


def gaussian_process():
    """51. H₀ ohne Modell: ein Gauß-Prozess (Zellen 20 von cosmology_chronometers.ipynb)."""
    global GP, H0_GP, _, ax, cov, cv, fig, l, lab, mean, n, sd
    global sf, x, zs
    zs = np.linspace(0, 2.1, 211)
    GP = {}
    for lab, cov in [("volle Kovarianz", COV_CC), ("nur Diagonale", np.diag(E_CC**2))]:
        sf, l = gp_fit(cov)
        mean, cv = gp_predict(zs, cov, sf, l)
        GP[lab] = (sf, l, mean, cv, cov)
    fig, ax = plt.subplots(figsize=(12, 6.5))
    sf, l, mean, cv, _ = GP["volle Kovarianz"]
    n = len(zs)
    sd = np.sqrt(np.diag(cv)[:n])
    ax.fill_between(zs, mean[:n] - sd, mean[:n] + sd, color="C0", alpha=0.3, label="Gauß-Prozess, 68 % (volle Kovarianz)")
    ax.plot(zs, mean[:n], color="C0", lw=1.6)
    x = FIT4["volle Kovarianz"][0]
    ax.plot(zs, x[0] * E(zs, *x), color="k", ls="--", lw=1.2, label=f"ΛCDM-Fit (Schritt 50): H₀ = {x[0]:.1f}")
    ax.errorbar(Z_CC, H_CC, yerr=E_CC, fmt="ko", ms=6, capsize=3, label="Chronometer")
    ax.errorbar(0, H0_SH0ES[0], yerr=H0_SH0ES[1], fmt="D", color="C2", ms=8, capsize=4, label="SH0ES")
    ax.errorbar(0.02, PLANCK["H0"][0], yerr=PLANCK["H0"][1], fmt="s", color="C3", ms=8, capsize=4, label="Planck")
    ax.set_xlabel("Rotverschiebung z")
    ax.set_ylabel("H(z) [km/s/Mpc]")
    ax.set_title("H(z) ohne kosmologisches Modell", fontsize=10)
    ax.legend(fontsize=9, loc="upper left")
    plt.show()

    for lab, (sf, l, mean, cv, _) in GP.items():
        print(f"{lab:16s}: σ_f = {sf:.0f} km/s/Mpc, ℓ = {l:.2f}; H₀ = {mean[0]:.2f} ± {np.sqrt(cv[0, 0]):.2f}, "
              f"H(1) = {mean[100]:.1f} ± {np.sqrt(cv[100, 100]):.1f}")
    H0_GP = (GP["volle Kovarianz"][2][0], np.sqrt(GP["volle Kovarianz"][3][0, 0]))


def acceleration_onset():
    """52. Wann die Beschleunigung begann (Zellen 23 von cosmology_chronometers.ipynb)."""
    global Hd, _, ax, crossing, cv, dHd, draws, fig, hi, l, lo, mean
    global med, ok, om_hi, om_lo, om_p, prof_om, q, q_l, sf, x, zt_of, zt_s
    sf, l, mean, cv, _ = GP["volle Kovarianz"]
    draws = np.random.default_rng(5).multivariate_normal(mean, cv + 1e-9 * np.eye(len(mean)), size=4000)
    Hd, dHd = draws[:, :n], draws[:, n:]
    q = (1 + zs) * dHd / Hd - 1


    def crossing(row):
        # erste Stelle von z = 0 aus, an der q von negativ zu positiv wechselt, linear interpoliert
        k = np.where((row[:-1] < 0) & (row[1:] >= 0))[0]
        if len(k) == 0:
            return np.nan
        k = k[0]
        return zs[k] - row[k] * (zs[k + 1] - zs[k]) / (row[k + 1] - row[k])


    zt_s = np.array([crossing(row) for row in q])
    x = FIT4["volle Kovarianz"][0]
    q_l = (1 + zs) * np.gradient(E(zs, *x), zs) / E(zs, *x) - 1
    om_p = np.linspace(0.05, 0.9, 341)
    prof_om = np.array([optimize.minimize_scalar(lambda h: chi2_cc(h, o), bounds=(30, 120), method="bounded").fun for o in om_p])
    prof_om -= prof_om.min()
    zt_of = lambda Om: (2 * (1 - Om) / Om) ** (1 / 3) - 1
    om_lo, om_hi = interval(om_p, prof_om)

    fig, ax = plt.subplots(figsize=(12, 6))
    lo, med, hi = np.percentile(q, [16, 50, 84], axis=0)
    ax.fill_between(zs, lo, hi, color="C0", alpha=0.3, label="Gauß-Prozess, 68 %")
    ax.plot(zs, med, color="C0", lw=1.6, label="Gauß-Prozess, Median")
    ax.plot(zs, q_l, color="k", ls="--", lw=1.4, label=f"ΛCDM-Fit, Ω_m = {x[1]:.2f}")
    ax.plot(zs, 1.5 * PLANCK["Om"][0] * (1 + zs) ** 3 / (PLANCK["Om"][0] * (1 + zs) ** 3 + 1 - PLANCK["Om"][0]) - 1, color="C3", lw=1.2, label="Planck-ΛCDM")
    ax.axhline(0, color="0.5", lw=0.8)
    ax.set_ylim(-1.5, 1.5)
    ax.set_xlabel("Rotverschiebung z")
    ax.set_ylabel("Verzögerungsparameter q(z)")
    ax.set_title("Gebremste Expansion (q > 0) und Beschleunigung (q < 0)", fontsize=10)
    ax.legend(fontsize=9)
    plt.show()

    ok = np.isfinite(zt_s)
    print(f"Gauß-Prozess: q₀ = {np.median(q[:, 0]):.2f} ({np.percentile(q[:, 0], 16):.2f} bis {np.percentile(q[:, 0], 84):.2f}); "
          f"Vorzeichenwechsel in {100 * ok.mean():.0f} % der Stichproben, z_t = {np.median(zt_s[ok]):.2f} "
          f"({np.percentile(zt_s[ok], 16):.2f} bis {np.percentile(zt_s[ok], 84):.2f})")
    print(f"ΛCDM-Fit: Ω_m = {x[1]:.3f} ({om_lo:.3f} bis {om_hi:.3f}), z_t = {zt_of(x[1]):.2f} ({zt_of(om_hi):.2f} bis {zt_of(om_lo):.2f}), q₀ = {1.5 * x[1] - 1:.2f}")
    print(f"Planck-ΛCDM: z_t = {zt_of(PLANCK['Om'][0]):.2f}, q₀ = {1.5 * PLANCK['Om'][0] - 1:.2f}")


def calibrate_ruler():
    """53. Die Uhr eicht das Lineal, Punkt für Punkt (Zellen 26 von cosmology_chronometers.ipynb)."""
    global CH, C_rd, H_dh, J, RD_POINT, _, ax, ci, cov, cv_dh, dh, e
    global e_dh, fig, h, inside, l, mean_dh, mh, one, r, rd73, rd_z, sf
    global z_dh, zi
    mh = KIND == "DH_over_rs"
    z_dh, dh, e_dh = Z_BAO[mh], Y_BAO[mh], np.sqrt(np.diag(COV_BAO))[mh]
    inside = z_dh < Z_CC.max()                                # Lyman-α bei z = 2.33 liegt jenseits der Uhren
    z_dh, dh, e_dh = z_dh[inside], dh[inside], e_dh[inside]
    sf, l, _, _, cov = GP["volle Kovarianz"]
    mean_dh, cv_dh = gp_predict(z_dh, cov, sf, l)
    H_dh, CH = mean_dh[:len(z_dh)], cv_dh[:len(z_dh), :len(z_dh)]
    rd_z = C_KMS / (H_dh * dh)
    J = np.diag(rd_z / H_dh)                                  # ∂r_d/∂H
    C_rd = J @ CH @ J + np.diag((rd_z * e_dh / dh) ** 2)
    ci = np.linalg.inv(C_rd)
    one = np.ones(len(rd_z))
    RD_POINT = ((one @ ci @ rd_z) / (one @ ci @ one), 1 / np.sqrt(one @ ci @ one))

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.errorbar(z_dh, rd_z, yerr=np.sqrt(np.diag(C_rd)), fmt="o", color="C0", ms=8, capsize=4, label="Chronometer (Gauß-Prozess) + DESI D_H/r_d")
    ax.axhspan(RD_POINT[0] - RD_POINT[1], RD_POINT[0] + RD_POINT[1], color="C0", alpha=0.2, label=f"gewichtetes Mittel {RD_POINT[0]:.1f} ± {RD_POINT[1]:.1f} Mpc")
    ax.axhline(PLANCK["rd"][0], color="k", lw=1.4, label="Planck (frühes Universum)")
    rd73 = HRD_BAO[0] / (H0_SH0ES[0] / 100)
    ax.axhline(rd73, color="C2", ls="--", lw=1.4, label=f"h·r_d der BAO mit H₀ = 73.04: {rd73:.1f} Mpc")
    ax.set_xlabel("Rotverschiebung z")
    ax.set_ylabel(r"$r_d$ [Mpc]")
    ax.set_title("Das Lineal der BAO, gemessen mit der Uhr der Chronometer", fontsize=10)
    ax.legend(fontsize=9)
    plt.show()

    for zi, r, e, h in zip(z_dh, rd_z, np.sqrt(np.diag(C_rd)), H_dh):
        print(f"z = {zi:5.3f}: H = {h:6.1f} km/s/Mpc, r_d = {r:6.1f} ± {e:4.1f} Mpc")
    print(f"Mittel: r_d = {RD_POINT[0]:.1f} ± {RD_POINT[1]:.1f} Mpc; Planck {PLANCK['rd'][0]} ({(RD_POINT[0] - PLANCK['rd'][0]) / RD_POINT[1]:+.1f} σ), "
          f"mit H₀ = 73.04 nötig {rd73:.1f} ({(RD_POINT[0] - rd73) / RD_POINT[1]:+.1f} σ)")


def with_bao():
    """54. Uhren und BAO zusammen in ΛCDM (Zellen 29 von cosmology_chronometers.ipynb)."""
    global FIT8, PROF8, RD8, _, a_, ax, ax2, col, data, e, fig, hh
    global hl, hs, key, lab, ph, pr, r, rds, rh, rl, x
    FIT8, PROF8 = {}, {}
    rds, hs = np.linspace(125, 175, 101), np.linspace(55, 85, 121)
    for key, data in [("Uhren + BAO", ("CC", "BAO")), ("Uhren + BAO + Pantheon+", ("CC", "BAO", "SN"))]:
        r = fit(data)
        FIT8[key] = r
        PROF8[key] = (profile(data, 2, rds, r), profile(data, 0, hs, r))
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.6))
    for (key, (pr, ph)), col in zip(PROF8.items(), ["C0", "C3"]):
        ax.plot(rds, pr, color=col, lw=1.6, label=key)
        ax2.plot(hs, ph, color=col, lw=1.6, label=key)
    ax.axvline(PLANCK["rd"][0], color="k", lw=1.2, label="Planck")
    ax.axvline(HRD_BAO[0] / (H0_SH0ES[0] / 100), color="C2", ls="--", lw=1.2, label="nötig für H₀ = 73.04")
    ax2.axvspan(H0_SH0ES[0] - H0_SH0ES[1], H0_SH0ES[0] + H0_SH0ES[1], color="C2", alpha=0.25, label="SH0ES")
    ax2.axvspan(PLANCK["H0"][0] - PLANCK["H0"][1], PLANCK["H0"][0] + PLANCK["H0"][1], color="0.6", alpha=0.4, label="Planck")
    for a_, lab in [(ax, r"$r_d$ [Mpc]"), (ax2, "H₀ [km/s/Mpc]")]:
        a_.axhline(1, color="0.5", ls=":")
        a_.set_ylim(0, 9)
        a_.set_xlabel(lab)
        a_.set_ylabel(r"$\Delta\chi^2$ (Profil)")
        a_.legend(fontsize=9)
    ax.set_title("Länge des Lineals ohne frühes Universum", fontsize=10)
    ax2.set_title("H₀ ohne Cepheiden und ohne frühes Universum", fontsize=10)
    plt.tight_layout()
    plt.show()

    RD8 = {}
    for key, r in FIT8.items():
        pr, ph = PROF8[key]
        (rl, rh), (hl, hh) = interval(rds, pr), interval(hs, ph)
        RD8[key] = (r.x, (rh - rl) / 2, (hh - hl) / 2)
        print(f"{key:24s}: r_d = {r.x[2]:.1f} ({rl:.1f} bis {rh:.1f}), H₀ = {r.x[0]:.2f} ({hl:.1f} bis {hh:.1f}), Ω_m = {r.x[1]:.3f}, "
              f"h r_d = {r.x[0] / 100 * r.x[2]:.2f}, χ² = {r.fun:.1f}")
    x, e, _ = RD8["Uhren + BAO"]
    print(f"Uhren + BAO: r_d gegen Planck {(x[2] - PLANCK['rd'][0]) / e:+.1f} σ, gegen das für H₀ = 73 nötige {(x[2] - HRD_BAO[0] / 0.7304) / e:+.1f} σ")


def calibrate_candles():
    """55. Die Uhr eicht die Kerzen (Zellen 32 von cosmology_chronometers.ipynb)."""
    global M9, M_of_H0, ax, eM, fig, hi9, hs9, lo9, prof9, r9, top
    r9 = fit(("CC", "SN"))
    hs9 = np.linspace(55, 85, 121)
    prof9 = profile(("CC", "SN"), 0, hs9, r9)
    lo9, hi9 = interval(hs9, prof9)
    M9 = chi2_sn(r9.x[0], r9.x[1], return_M=True)[1]
    M_of_H0 = lambda H0: M9 + 5 * np.log10(H0 / r9.x[0])     # bei fester Form
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(hs9, prof9, color="C0", lw=1.8, label="Uhren + Pantheon+ (Profil)")
    ax.axhline(1, color="0.5", ls=":")
    ax.axvspan(H0_SH0ES[0] - H0_SH0ES[1], H0_SH0ES[0] + H0_SH0ES[1], color="C2", alpha=0.25, label="SH0ES (M_B aus Cepheiden)")
    ax.axvspan(PLANCK["H0"][0] - PLANCK["H0"][1], PLANCK["H0"][0] + PLANCK["H0"][1], color="0.6", alpha=0.4, label="Planck")
    ax.set_ylim(0, 9)
    ax.set_xlabel("H₀ [km/s/Mpc]")
    ax.set_ylabel(r"$\Delta\chi^2$ (Profil)")
    ax.set_title("Supernovae mit der Uhr geeicht", fontsize=10, pad=42)
    top = ax.secondary_xaxis("top", functions=(M_of_H0, lambda M: r9.x[0] * 10 ** ((M - M9) / 5)))
    top.set_xlabel(r"absolute Helligkeit $M_B$ der Supernovae [mag]")
    ax.legend(fontsize=9)
    plt.show()

    eM = 5 / np.log(10) * (hi9 - lo9) / 2 / r9.x[0]
    print(f"Uhren + Pantheon+: H₀ = {r9.x[0]:.2f} ({lo9:.1f} bis {hi9:.1f}), Ω_m = {r9.x[1]:.3f}, χ² = {r9.fun:.1f}")
    print(f"M_B = {M9:.3f} ± {eM:.3f} mag; Cepheiden {M_B_CEPHEID[0]} ± {M_B_CEPHEID[1]} → Unterschied {M9 - M_B_CEPHEID[0]:+.3f} mag "
          f"({(M9 - M_B_CEPHEID[0]) / np.hypot(eM, M_B_CEPHEID[1]):+.1f} σ)")


def literature():
    """56. Gegen Planck, SH0ES und die anderen Wege (Zellen 35 von cosmology_chronometers.ipynb)."""
    global _, a_, ax, ax2, col, e, eh8, eh8s, erd73, erd8, erd8s, fig
    global h_rows, i, lab, name, rd73, rd_rows, rows, v, x8, x8s
    x8, erd8, eh8 = RD8["Uhren + BAO"]
    x8s, erd8s, eh8s = RD8["Uhren + BAO + Pantheon+"]
    h_rows = [("Uhren, ΛCDM (Schritt 50)", FIT4["volle Kovarianz"][0][0], (FIT4["volle Kovarianz"][3] - FIT4["volle Kovarianz"][2]) / 2, "C0"),
              ("Uhren, Gauß-Prozess (Schritt 51)", *H0_GP, "C0"),
              ("Uhren + BAO (Schritt 54)", x8[0], eh8, "C0"),
              ("Uhren + Pantheon+ (Schritt 55)", r9.x[0], (hi9 - lo9) / 2, "C0"),
              ("Planck 2018", *PLANCK["H0"], "k"),
              ("DESI DR2: BAO + BBN", 68.51, 0.58, "k"),
              ("SH0ES (Riess et al. 2022)", *H0_SH0ES, "C2")]
    rd_rows = [("Uhren + BAO, Punkt für Punkt (Schritt 53)", *RD_POINT, "C0"),
               ("Uhren + BAO, ΛCDM (Schritt 54)", x8[2], erd8, "C0"),
               ("Uhren + BAO + Pantheon+ (Schritt 54)", x8s[2], erd8s, "C0"),
               ("Heavens, Jimenez & Verde 2014", *RD_HJV, "k"),
               ("Planck 2018", *PLANCK["rd"], "k"),
               ("BAO h·r_d mit H₀ von SH0ES", HRD_BAO[0] / (H0_SH0ES[0] / 100), HRD_BAO[0] / (H0_SH0ES[0] / 100) * np.hypot(HRD_BAO[1] / HRD_BAO[0], H0_SH0ES[1] / H0_SH0ES[0]), "C2")]
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(17, 5.6))
    for a_, rows, lab in [(ax, h_rows, "H₀ [km/s/Mpc]"), (ax2, rd_rows, r"$r_d$ [Mpc]")]:
        for i, (name, v, e, col) in enumerate(rows):
            a_.errorbar(v, -i, xerr=e, fmt="o", color=col, ms=7, capsize=4)
        a_.set_yticks(-np.arange(len(rows)))
        a_.set_yticklabels([r[0] for r in rows], fontsize=9.5)
        a_.set_xlabel(lab)
    ax.set_title("Hubble-Konstante", fontsize=10)
    ax2.set_title("Länge des Lineals", fontsize=10)
    plt.tight_layout()
    plt.show()

    for name, v, e, _ in h_rows[:4]:
        print(f"{name:34s}: H₀ = {v:.2f} ± {e:.2f}; gegen Planck {(v - PLANCK['H0'][0]) / np.hypot(e, PLANCK['H0'][1]):+.1f} σ, "
              f"gegen SH0ES {(v - H0_SH0ES[0]) / np.hypot(e, H0_SH0ES[1]):+.1f} σ")
    rd73, erd73 = rd_rows[-1][1], rd_rows[-1][2]
    for name, v, e, _ in rd_rows[:3]:
        print(f"{name:42s}: r_d = {v:.1f} ± {e:.1f} Mpc; gegen Planck {(v - PLANCK['rd'][0]) / e:+.1f} σ, gegen {rd73:.1f} Mpc {(v - rd73) / np.hypot(e, erd73):+.1f} σ; "
              f"Abstand der Hypothesen in eigenen Fehlern: {(PLANCK['rd'][0] - rd73) / e:.1f}")
