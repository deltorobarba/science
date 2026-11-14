"""Rotationskurven und Dunkle Materie aus SPARC: sichtbare Materie gegen Rotation, NFW- und Kern-Halos, radiale Beschleunigungsrelation, baryonische Tully-Fisher-Beziehung.

Für galaxies.ipynb aus galaxies_rotationcurves.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: sparc_data, quality_cuts, baryons_vs_rotation, halo_fits, radial_acceleration, tully_fisher, literature.
Downloads und Cache: data/galaxies/ (`galdata.py`).
"""
import galdata                                        # zuerst: Cache-Ordner für astropy
import io
import os
import zipfile
import urllib.request
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import odr
from astroquery.simbad import Simbad


def sparc_data():
    """21. Die SPARC-Datenbank (Zellen 5, 7 von galaxies_rotationcurves.ipynb)."""
    global ACC, ASTRODATA, GALAXY, G_KPC, H0_KPC, HUBBLE, REFRESH, SPARC_COLS, SPARC_GALAXY, SPARC_URL, UPS_BUL, UPS_DISK
    global ax, axes, d, fig, mrt, name, props, rc, rd, rotmod, sparc, sparc_file
    global sparc_name, zf
    ASTRODATA = galdata.DATA
    (ASTRODATA / "sparc").mkdir(parents=True, exist_ok=True)


    GALAXY = "NGC 2403"        # SPARC-Name oder SIMBAD-Name, z. B. "M 63" (= NGC 5055), "DDO 154", "UGC 128"
    REFRESH = False            # True: SPARC-Dateien neu laden
    SPARC_URL = "https://astroweb.case.edu/SPARC/"
    UPS_DISK, UPS_BUL = 0.5, 0.7   # Masse-Leuchtkraft-Verhältnisse bei 3.6 µm [M_sun/L_sun]
    H0_KPC = 73 / 1000             # H0 = 73 km/s/Mpc in km/s/kpc (Entfernungsskala von SPARC)
    G_KPC = 4.30091e-6             # Gravitationskonstante [kpc (km/s)² / M_sun]
    ACC = 1e6 / 3.0857e19          # (km/s)²/kpc -> m/s²
    pd.set_option("display.width", 160)

    def sparc_file(name):
        path = ASTRODATA / "sparc" / name
        if REFRESH or not path.exists():
            urllib.request.urlretrieve(SPARC_URL + name, path)
        return path

    # Galaxientabelle: der Datenblock folgt auf die letzte gestrichelte Linie, die Felder enthalten keine Leerzeichen
    mrt = sparc_file("SPARC_Lelli2016c.mrt").read_text()
    SPARC_COLS = ["Galaxy", "T", "D", "e_D", "f_D", "Inc", "e_Inc", "L36", "e_L36", "Reff", "SBeff",
                  "Rdisk", "SBdisk", "MHI", "RHI", "Vflat", "e_Vflat", "Q", "Ref"]
    sparc = pd.read_csv(io.StringIO(mrt.split("-" * 80)[-1].strip()), sep=r"\s+", names=SPARC_COLS)
    with zipfile.ZipFile(sparc_file("Rotmod_LTG.zip")) as zf:
        rotmod = {fn.replace("_rotmod.dat", ""): pd.DataFrame(np.loadtxt(zf.open(fn), comments="#"),
                                                              columns=["R", "Vobs", "errV", "Vgas", "Vdisk", "Vbul", "SBdisk", "SBbul"])
                  for fn in zf.namelist()}

    def sparc_name(name):
        # "NGC 2403" -> "NGC2403", "UGC 128" -> "UGC00128"; sonst die Aliasse aus SIMBAD durchsuchen ("M 63" -> "NGC5055")
        def norm(alias):
            cat, _, num = alias.partition(" ")
            num = num.strip()
            if not num.isdigit():
                return alias.replace(" ", "")
            width = {"NGC": 4, "IC": 4, "UGC": 5, "DDO": 3}.get(cat, 0)
            return f"{cat}{int(num):0{width}d}"
        if norm(name) in rotmod:
            return norm(name)
        ids = Simbad.query_tap(f'''SELECT i2.id FROM ident AS i1 JOIN ident AS i2 ON i1.oidref = i2.oidref
                              WHERE i1.id = '{name}' ''').to_pandas()["id"].str.replace(r"\s+", " ", regex=True)
        return next((norm(a) for a in ids if norm(a) in rotmod), None)

    SPARC_GALAXY = sparc_name(GALAXY)
    if SPARC_GALAXY is None:
        raise ValueError(f"{GALAXY} ist nicht in SPARC")
    props = sparc.loc[sparc["Galaxy"] == SPARC_GALAXY].iloc[0]
    rc = rotmod[SPARC_GALAXY]

    HUBBLE = ["S0", "Sa", "Sab", "Sb", "Sbc", "Sc", "Scd", "Sd", "Sdm", "Sm", "Im", "BCD"]
    print(f"SPARC: {len(sparc)} Galaxien, {sum(len(v) for v in rotmod.values()):,} Punkte auf den Rotationskurven")
    print(f"Hubble-Typen: {pd.Series(sparc['T']).map(dict(enumerate(HUBBLE))).value_counts().to_dict()}")
    print(f"V_flat von {sparc.loc[sparc['Vflat'] > 0, 'Vflat'].min():.0f} bis {sparc['Vflat'].max():.0f} km/s, "
          f"Entfernungen von {sparc['D'].min():.1f} bis {sparc['D'].max():.0f} Mpc")
    print(f"\n{GALAXY} = {SPARC_GALAXY}: Typ {HUBBLE[int(props['T'])]}, D = {props['D']:.2f} ± {props['e_D']:.2f} Mpc, "
          f"Neigung {props['Inc']:.0f}° ± {props['e_Inc']:.0f}°, L[3.6] = {props['L36']:.1f}·10⁹ L_sun, "
          f"M_HI = {props['MHI']:.2f}·10⁹ M_sun, Skalenlänge {props['Rdisk']:.2f} kpc, V_flat = {props['Vflat']:.0f} ± {props['e_Vflat']:.0f} km/s, "
          f"Qualität {props['Q']}")
    print(f"{len(rc)} Punkte von {rc['R'].min():.2f} bis {rc['R'].max():.1f} kpc (= {rc['R'].max() / props['Rdisk']:.1f} Skalenlängen)")

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    for name, d in rotmod.items():
        axes[0].plot(d["R"], d["Vobs"], c="0.75", lw=0.6)
        rd = sparc.loc[sparc["Galaxy"] == name, "Rdisk"].iloc[0]
        axes[1].plot(d["R"] / rd, d["Vobs"], c="0.75", lw=0.6)
    axes[0].errorbar(rc["R"], rc["Vobs"], rc["errV"], fmt="o-", c="tab:red", ms=3, lw=1, label=SPARC_GALAXY)
    axes[1].plot(rc["R"] / props["Rdisk"], rc["Vobs"], "o-", c="tab:red", ms=3, lw=1, label=SPARC_GALAXY)
    axes[0].set_xlim(0, 60)
    axes[0].set_xlabel("Radius [kpc]")
    axes[1].set_xlim(0, 15)
    axes[1].set_xlabel("Radius / Skalenlänge der Scheibe")
    for ax in axes:
        ax.set_ylabel("Rotationsgeschwindigkeit [km/s]")
        ax.legend(fontsize=8)
    axes[0].set_title(f"Alle {len(rotmod)} Rotationskurven", fontsize=10)
    axes[1].set_title("Radius in Skalenlängen der Scheibe", fontsize=10)
    fig.tight_layout()
    plt.show()


def quality_cuts():
    """22. Qualitätsschnitte (Zellen 10 von galaxies_rotationcurves.ipynb)."""
    global axes, fig, keep, label, m, pts, pts_ok, steps, v_bar_sq
    def v_bar_sq(d, ups_disk=UPS_DISK, ups_bul=UPS_BUL):
        # Gas mit Vorzeichen, Sterne mit Masse-Leuchtkraft-Verhältnis
        return np.abs(d["Vgas"]) * d["Vgas"] + ups_disk * d["Vdisk"] ** 2 + ups_bul * d["Vbul"] ** 2

    pts = pd.concat([d.assign(Galaxy=name) for name, d in rotmod.items()], ignore_index=True)
    pts = pts.merge(sparc[["Galaxy", "Q", "Inc"]], on="Galaxy")
    pts["vb2"] = v_bar_sq(pts)
    steps = [("alle", np.ones(len(pts), bool)),
             ("Qualität 1 oder 2", pts["Q"] < 3),
             ("Neigung >= 30°", pts["Inc"] >= 30),
             ("Fehler < 10 % von V_obs", pts["errV"] < 0.1 * pts["Vobs"]),
             ("V_obs > 0 und V_bar² > 0", (pts["Vobs"] > 0) & (pts["vb2"] > 0))]
    keep = np.ones(len(pts), bool)
    for label, m in steps:
        keep &= m
        print(f"{label:28s} {keep.sum():5d} Punkte aus {pts.loc[keep, 'Galaxy'].nunique():3d} Galaxien")
    pts_ok = pts[keep]

    fig, axes = plt.subplots(1, 2, figsize=(12, 3.8))
    axes[0].hist(sparc["Inc"], bins=np.arange(0, 95, 5), color="tab:blue", alpha=0.7)
    axes[0].axvline(30, color="black", ls="--", label="Schnitt bei 30°")
    axes[0].set_xlabel("Neigung [°]")
    axes[0].set_ylabel("Zahl der Galaxien")
    axes[0].set_title("Neigungen", fontsize=10)
    axes[0].legend(fontsize=8)
    axes[1].hist(np.clip(pts["errV"] / pts["Vobs"], 0, 0.5), bins=50, color="tab:orange", alpha=0.7)
    axes[1].axvline(0.1, color="black", ls="--", label="Schnitt bei 10 %")
    axes[1].set_xlabel("relativer Fehler der Rotationsgeschwindigkeit")
    axes[1].set_ylabel("Zahl der Punkte")
    axes[1].set_title("Messfehler", fontsize=10)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()


def baryons_vs_rotation():
    """23. Sichtbare Materie gegen beobachtete Rotation (Zellen 13 von galaxies_rotationcurves.ipynb)."""
    global ax, axes, below, f_dm, fig, m_bar, m_dyn, r22, r_half, r_kep, r_kpc, v_bar
    global v_obs
    r_kpc = rc["R"].to_numpy()
    v_obs = rc["Vobs"].to_numpy()
    v_bar = np.sqrt(np.clip(v_bar_sq(rc), 0, None)).to_numpy()
    f_dm = 1 - v_bar ** 2 / v_obs ** 2
    r22 = 2.2 * props["Rdisk"]                                            # dort hat eine exponentielle Scheibe ihr Maximum
    print(f"Bei 2.2 Skalenlängen ({r22:.1f} kpc): V_bar = {np.interp(r22, r_kpc, v_bar):.0f} km/s, V_obs = {np.interp(r22, r_kpc, v_obs):.0f} km/s, "
          f"Anteil Dunkle Materie {np.interp(r22, r_kpc, f_dm):.0%}")
    print(f"Am letzten Punkt ({r_kpc[-1]:.1f} kpc): V_bar = {v_bar[-1]:.0f} km/s, V_obs = {v_obs[-1]:.0f} km/s, Anteil Dunkle Materie {f_dm[-1]:.0%}")
    below = np.flatnonzero(f_dm <= 0.5)
    r_half = r_kpc[below[-1] + 1] if len(below) and below[-1] + 1 < len(r_kpc) else (r_kpc[0] if not len(below) else np.nan)
    print(f"Ab {r_half:.1f} kpc (= {r_half / props['Rdisk']:.1f} Skalenlängen) bleibt der Anteil der Dunklen Materie über 50 %")
    m_dyn = v_obs[-1] ** 2 * r_kpc[-1] / G_KPC
    m_bar = v_bar[-1] ** 2 * r_kpc[-1] / G_KPC
    print(f"Masse innerhalb {r_kpc[-1]:.0f} kpc (kugelsymmetrisch genähert): gesamt {m_dyn:.2e} M_sun, sichtbar {m_bar:.2e} M_sun")

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    ax = axes[0]
    ax.errorbar(r_kpc, v_obs, rc["errV"], fmt="o", c="black", ms=4, label="beobachtet (HI, Hα)")
    ax.plot(r_kpc, rc["Vgas"], c="tab:green", ls="--", label="Gas")
    ax.plot(r_kpc, np.sqrt(UPS_DISK) * rc["Vdisk"], c="tab:blue", ls="--", label=f"Sternscheibe (Υ = {UPS_DISK})")
    if rc["Vbul"].max() > 0:
        ax.plot(r_kpc, np.sqrt(UPS_BUL) * rc["Vbul"], c="tab:purple", ls="--", label=f"Bulge (Υ = {UPS_BUL})")
    ax.plot(r_kpc, v_bar, c="tab:orange", lw=2, label="sichtbare Materie zusammen")
    r_kep = np.linspace(r_kpc[np.argmax(v_bar)], r_kpc[-1], 50)
    ax.plot(r_kep, v_bar.max() * np.sqrt(r_kpc[np.argmax(v_bar)] / r_kep), c="tab:orange", ls=":", lw=1, label="Kepler-Abfall ab dem Maximum")
    ax.set_xlabel("Radius [kpc]")
    ax.set_ylabel("Rotationsgeschwindigkeit [km/s]")
    ax.set_title(f"{SPARC_GALAXY}: Beiträge zur Rotation", fontsize=10)
    ax.legend(fontsize=7, loc="lower right")
    axes[1].plot(r_kpc, f_dm, "o-", c="black", ms=3)
    axes[1].axhline(0.5, color="grey", ls=":", lw=1)
    axes[1].axvline(r22, color="tab:blue", ls="--", lw=1, label="2.2 Skalenlängen")
    axes[1].set_ylim(-0.1, 1)
    axes[1].set_xlabel("Radius [kpc]")
    axes[1].set_ylabel("Anteil Dunkler Materie innerhalb r")
    axes[1].set_title("1 − V_bar² / V_obs²", fontsize=10)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()


def halo_fits():
    """24. NFW-Halo gegen Halo mit Kern (Zellen 16 von galaxies_rotationcurves.ipynb)."""
    global axes, c_iso, c_nfw, chi2_iso, chi2_nfw, dof, err, fig, m200, p_iso, p_nfw, r200
    global v_iso, v_nfw, v_tot_iso, v_tot_nfw
    def v_nfw(r, v200, c):
        # NFW
        x = r / (v200 / (10 * H0_KPC))
        return v200 * np.sqrt((np.log(1 + c * x) - c * x / (1 + c * x)) / (x * (np.log(1 + c) - c / (1 + c))))

    def v_iso(r, v_inf, r_c):
        # pseudo-isotherm
        return v_inf * np.sqrt(1 - r_c / r * np.arctan(r / r_c))

    err = np.maximum(rc["errV"].to_numpy(), 1.0)
    p_nfw, c_nfw = curve_fit(lambda r, v200, c: np.sqrt(v_bar ** 2 + v_nfw(r, v200, c) ** 2), r_kpc, v_obs,
                             p0=[150, 10], sigma=err, absolute_sigma=True, bounds=([10, 1], [500, 40]))
    p_iso, c_iso = curve_fit(lambda r, vi, rcore: np.sqrt(v_bar ** 2 + v_iso(r, vi, rcore) ** 2), r_kpc, v_obs,
                             p0=[150, 2], sigma=err, absolute_sigma=True, bounds=([5, 0.05], [500, 50]))
    v_tot_nfw = np.sqrt(v_bar ** 2 + v_nfw(r_kpc, *p_nfw) ** 2)
    v_tot_iso = np.sqrt(v_bar ** 2 + v_iso(r_kpc, *p_iso) ** 2)
    dof = len(r_kpc) - 2
    chi2_nfw = np.sum(((v_obs - v_tot_nfw) / err) ** 2) / dof
    chi2_iso = np.sum(((v_obs - v_tot_iso) / err) ** 2) / dof
    r200 = p_nfw[0] / (10 * H0_KPC)
    m200 = p_nfw[0] ** 2 * r200 / G_KPC
    print(f"NFW:       V200 = {p_nfw[0]:.0f} ± {np.sqrt(c_nfw[0, 0]):.0f} km/s, c = {p_nfw[1]:.1f} ± {np.sqrt(c_nfw[1, 1]):.1f}, "
          f"R200 = {r200:.0f} kpc, M200 = {m200:.1e} M_sun, r_s = {r200 / p_nfw[1]:.1f} kpc;  χ²_red = {chi2_nfw:.2f}")
    print(f"Mit Kern:  V_inf = {p_iso[0]:.0f} ± {np.sqrt(c_iso[0, 0]):.0f} km/s, r_c = {p_iso[1]:.2f} ± {np.sqrt(c_iso[1, 1]):.2f} kpc;  "
          f"χ²_red = {chi2_iso:.2f}")
    print(f"Besser passt {'NFW' if chi2_nfw < chi2_iso else 'der Halo mit Kern'} (χ²_red {min(chi2_nfw, chi2_iso):.2f} gegen {max(chi2_nfw, chi2_iso):.2f})")
    print(f"Sichtbare Masse gegen Halo: M_bar(gesamt) = {(UPS_DISK * props['L36'] + 1.33 * props['MHI']) * 1e9:.1e} M_sun, "
          f"M200 / M_bar = {m200 / ((UPS_DISK * props['L36'] + 1.33 * props['MHI']) * 1e9):.0f}")

    fig, axes = plt.subplots(2, 1, figsize=(9, 7), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    axes[0].errorbar(r_kpc, v_obs, rc["errV"], fmt="o", c="black", ms=4, label="beobachtet")
    axes[0].plot(r_kpc, v_bar, c="tab:orange", lw=1.5, label="sichtbare Materie")
    axes[0].plot(r_kpc, v_nfw(r_kpc, *p_nfw), c="tab:red", ls="--", lw=1, label="NFW-Halo allein")
    axes[0].plot(r_kpc, v_tot_nfw, c="tab:red", lw=2, label=f"sichtbar + NFW (χ²_red = {chi2_nfw:.1f})")
    axes[0].plot(r_kpc, v_iso(r_kpc, *p_iso), c="tab:blue", ls="--", lw=1, label="Halo mit Kern allein")
    axes[0].plot(r_kpc, v_tot_iso, c="tab:blue", lw=2, label=f"sichtbar + Kern (χ²_red = {chi2_iso:.1f})")
    axes[0].set_ylabel("Rotationsgeschwindigkeit [km/s]")
    axes[0].set_title(f"{SPARC_GALAXY}: Massenmodelle (D = {props['D']:.2f} Mpc)", fontsize=10)
    axes[0].legend(fontsize=8, loc="lower right")
    axes[1].plot(r_kpc, (v_obs - v_tot_nfw) / err, "o-", c="tab:red", ms=3, label="NFW")
    axes[1].plot(r_kpc, (v_obs - v_tot_iso) / err, "s-", c="tab:blue", ms=3, label="Kern")
    axes[1].axhline(0, color="black", lw=0.8)
    axes[1].set_xlabel("Radius [kpc]")
    axes[1].set_ylabel("Residuum / Fehler")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()


def radial_acceleration():
    """25. Die radiale Beschleunigungsrelation (Zellen 19 von galaxies_rotationcurves.ipynb)."""
    global ax, fig, g_bar, g_obs, gb, gdag, gdag_err, hb, hi, lg_cov, lg_dag, lo
    global m, own, rar, resid
    g_obs = pts_ok["Vobs"] ** 2 / pts_ok["R"] * ACC
    g_bar = pts_ok["vb2"] / pts_ok["R"] * ACC
    def rar(gb, gdag):
        return gb / (1 - np.exp(-np.sqrt(gb / gdag)))
    lg_dag, lg_cov = curve_fit(lambda lg, lgd: np.log10(rar(10 ** lg, 10 ** lgd)), np.log10(g_bar), np.log10(g_obs), p0=[-10.0])
    gdag = 10 ** lg_dag[0]
    gdag_err = gdag * np.log(10) * np.sqrt(lg_cov[0, 0])
    resid = np.log10(g_obs) - np.log10(rar(g_bar, gdag))
    print(f"{len(pts_ok):,} Punkte aus {pts_ok['Galaxy'].nunique()} Galaxien")
    print(f"g† = ({gdag * 1e10:.3f} ± {gdag_err * 1e10:.3f})·10⁻¹⁰ m/s² (nur statistischer Fehler)")
    print(f"Streuung um die Kurve: {resid.std():.3f} dex; ohne Dunkle Materie (g_obs = g_bar): {np.std(np.log10(g_obs / g_bar)):.3f} dex "
          f"um einen Mittelwert von {np.mean(np.log10(g_obs / g_bar)):+.2f} dex")
    for lo, hi in [(-12.5, -11.5), (-11.5, -10.5), (-10.5, -9.5), (-9.5, -8.5)]:
        m = (np.log10(g_bar) >= lo) & (np.log10(g_bar) < hi)
        if m.sum():
            print(f"  log g_bar in [{lo}, {hi}): {m.sum():4d} Punkte, g_obs/g_bar im Median {np.median(g_obs[m] / g_bar[m]):5.1f}")

    fig, ax = plt.subplots(figsize=(8, 6.5))
    hb = ax.hexbin(np.log10(g_bar), np.log10(g_obs), gridsize=60, bins="log", cmap="Greys", mincnt=1)
    gb = np.logspace(-12.5, -8.5, 200)
    ax.plot(np.log10(gb), np.log10(gb), "k--", lw=1, label="ohne Dunkle Materie (g_obs = g_bar)")
    ax.plot(np.log10(gb), np.log10(rar(gb, gdag)), "r-", lw=2, label=f"Fit: g† = {gdag:.2e} m/s²")
    ax.plot(np.log10(gb), 0.5 * np.log10(gb * gdag), c="tab:red", ls=":", lw=1, label="Grenzfall √(g_bar g†)")
    own = (v_bar > 0) & (v_obs > 0)
    ax.scatter(np.log10((v_bar ** 2 / r_kpc * ACC)[own]), np.log10((v_obs ** 2 / r_kpc * ACC)[own]), c="tab:orange", s=15,
               edgecolor="k", lw=0.3, zorder=3, label=SPARC_GALAXY)
    ax.axvline(np.log10(gdag), color="tab:red", lw=0.6, alpha=0.5)
    fig.colorbar(hb, ax=ax, label="Punkte pro Feld")
    ax.set_xlabel("log g_bar [m/s²] (aus Sternen und Gas)")
    ax.set_ylabel("log g_obs [m/s²] (aus der Rotationskurve)")
    ax.set_title(f"Radiale Beschleunigungsrelation ({len(pts_ok):,} Punkte)", fontsize=10)
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    plt.show()


def tully_fisher():
    """26. Die baryonische Tully-Fisher-Beziehung (Zellen 22 von galaxies_rotationcurves.ipynb)."""
    global G_SI, MSUN, ax, btf, fig, fit, icpt, icpt_err, icpt_ols, icpt_pred, m_pred, scatter
    global slope, slope_err, slope_ols, sx, sy, vv, x_btf, y_btf
    btf = sparc[(sparc["Vflat"] > 0) & (sparc["Q"] < 3)].copy()
    btf["Mbar"] = (UPS_DISK * btf["L36"] + 1.33 * btf["MHI"]) * 1e9
    x_btf, y_btf = np.log10(btf["Vflat"]), np.log10(btf["Mbar"])
    sx = btf["e_Vflat"] / btf["Vflat"] / np.log(10)                            # Fehler von log V
    sy = np.full(len(btf), 0.1)                                                # 0.1 dex für Masse-Leuchtkraft und Entfernung
    fit = odr.ODR(odr.RealData(x_btf, y_btf, sx=sx, sy=sy), odr.unilinear, beta0=[4.0, 2.0]).run()
    slope, icpt = fit.beta
    slope_err, icpt_err = fit.sd_beta
    slope_ols, icpt_ols = np.polyfit(x_btf, y_btf, 1)
    scatter = np.std(y_btf - (icpt + slope * x_btf))

    # Vorhersage aus der Beschleunigungsrelation: M = V^4 / (G g†)
    G_SI, MSUN = 6.674e-11, 1.989e30
    def m_pred(v_kms):
        return (v_kms * 1e3) ** 4 / (G_SI * gdag) / MSUN
    icpt_pred = np.log10(m_pred(1.0))
    print(f"{len(btf)} Galaxien mit V_flat und Qualität 1 oder 2")
    print(f"Orthogonale Regression: log M_bar = ({slope:.2f} ± {slope_err:.2f}) log V_flat + ({icpt:.2f} ± {icpt_err:.2f}), "
          f"Streuung {scatter:.2f} dex")
    print(f"Gewöhnliche Regression: Steigung {slope_ols:.2f} (zu flach)")
    print(f"Aus g†: Steigung 4, log M_bar = 4 log V_flat + {icpt_pred:.2f};  bei V_flat = 100 km/s: "
          f"Fit {10 ** (icpt + 2 * slope):.2e}, Vorhersage {m_pred(100):.2e} M_sun")
    print(f"Gasanteil: von {(1.33 * btf['MHI'] * 1e9 / btf['Mbar']).min():.0%} bis {(1.33 * btf['MHI'] * 1e9 / btf['Mbar']).max():.0%}; "
          f"Median unter 50 km/s {(1.33 * btf['MHI'] * 1e9 / btf['Mbar'])[btf['Vflat'] < 50].median():.0%}, "
          f"über 200 km/s {(1.33 * btf['MHI'] * 1e9 / btf['Mbar'])[btf['Vflat'] > 200].median():.0%}")

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.errorbar(btf["Vflat"], btf["Mbar"], xerr=btf["e_Vflat"], fmt="o", ms=3, c="grey", alpha=0.6, lw=0.5,
                label=f"{len(btf)} SPARC-Galaxien")
    vv = np.logspace(1.3, 2.6, 50)
    ax.plot(vv, 10 ** icpt * vv ** slope, "r-", label=f"orthogonale Regression: M ∝ V^{slope:.2f}")
    ax.plot(vv, 10 ** icpt_ols * vv ** slope_ols, c="tab:red", ls=":", lw=1, label=f"gewöhnliche Regression: M ∝ V^{slope_ols:.2f}")
    ax.plot(vv, m_pred(vv), "b--", lw=1, label="M = V⁴ / (G g†) aus Schritt 25")
    if props["Vflat"] > 0:
        ax.scatter([props["Vflat"]], [(UPS_DISK * props["L36"] + 1.33 * props["MHI"]) * 1e9], marker="*", s=250,
                   c="tab:orange", edgecolor="k", zorder=5, label=SPARC_GALAXY)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Flache Rotationsgeschwindigkeit V_flat [km/s]")
    ax.set_ylabel("Sichtbare Masse M_bar [M_sun]")
    ax.set_title("Baryonische Tully-Fisher-Beziehung", fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()


def literature():
    """27. Vergleich mit den SPARC-Veröffentlichungen (Zellen 25 von galaxies_rotationcurves.ipynb)."""
    global rows
    rows = [("g† [10⁻¹⁰ m/s²]", f"{gdag * 1e10:.2f} ± {gdag_err * 1e10:.2f}", "1.20 ± 0.02 (stat.) ± 0.24 (syst.)", "McGaugh, Lelli & Schombert (2016)"),
            ("Streuung der Beschleunigungsrelation [dex]", f"{resid.std():.2f}", "0.13", "McGaugh, Lelli & Schombert (2016)"),
            ("Zahl der Punkte", f"{len(pts_ok):,}", "2,693", "McGaugh, Lelli & Schombert (2016)"),
            ("Steigung der Tully-Fisher-Beziehung", f"{slope:.2f} ± {slope_err:.2f}", "etwa 3.5 bis 4, je nach Methode", "Lelli et al. (2016, 2019)"),
            (f"V_flat von {SPARC_GALAXY} [km/s]", f"{np.mean(v_obs[-3:]):.0f} (Mittel der letzten 3 Punkte)",
             f"{props['Vflat']:.0f} ± {props['e_Vflat']:.0f}", "SPARC-Tabelle")]
    print(pd.DataFrame(rows, columns=["Größe", "eigen", "veröffentlicht", "Quelle"]).to_string(index=False))
