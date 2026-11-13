"""Emissionslinien der H-II-Regionen einer Galaxie aus SDSS-Spektren: Linienfits, Dichte und Staub, BPT-Diagramm, Metallizitätsgradient, Vergleich mit der SDSS-Pipeline.

Für galaxies.ipynb aus galaxies_hiiregions.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: sdss_spectra, line_fits, density_dust, bpt, metallicity_gradient, pipeline_check.
Downloads und Cache: data/galaxies/ (`galdata.py`).
"""
import galdata                                        # zuerst: Cache-Ordner für astropy
import os
import time
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from astropy import units as u
from astropy.coordinates import Angle
from astroquery.simbad import Simbad
from astroquery.sdss import SDSS
from astroquery.hips2fits import hips2fits


def sdss_spectra():
    """10. Die Galaxie und ihre SDSS-Spektren (Zellen 5, 7 von galaxies_hiiregions.ipynb)."""
    global ASTRODATA, C_KMS, GROUPS, LABEL, LINES, MAX_SPECTRA, SN_MIN, SPEC_GALAXY, axes, cls, col, dist
    global dx_all, dy_all, fig, first, g, g_a, g_dec, g_dist, g_pa, g_q, g_ra, half_g
    global img_opt, k, kpc_per_arcmin, lab, ln, m, query, r_deg, sdss_query, spec_list, spectra, v_sys
    global z0
    ASTRODATA = galdata.DATA


    SPEC_GALAXY = "M 101"    # auch gut: "M 33", "M 51"
    MAX_SPECTRA = 80         # höchstens so viele Spektren laden (je etwa 1 s)
    SN_MIN = 3.0             # Mindest-Signal-Rausch-Verhältnis jeder Linie, die in eine Diagnose eingeht
    C_KMS = 299792.458

    # Emissionslinien, Vakuumwellenlängen [Å]
    LINES = {"Hb": 4862.68, "OIII4959": 4960.30, "OIII5007": 5008.24, "NII6548": 6549.86, "Ha": 6564.61,
             "NII6584": 6585.27, "SII6717": 6718.29, "SII6731": 6732.67}
    LABEL = {"Hb": "Hβ", "OIII5007": "[O III]", "Ha": "Hα", "NII6584": "[N II]", "SII6717": "[S II]"}
    GROUPS = [["Hb"], ["OIII4959", "OIII5007"], ["NII6548", "Ha", "NII6584"], ["SII6717", "SII6731"]]
    pd.set_option("display.width", 160)

    def sdss_query(sql, tries=3):
        # SkyServer antwortet manchmal mit 503 (überlastet); dann nach einer Pause noch einmal
        for k in range(tries):
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")      # astropy meldet, dass specObjID nicht in eine 64-Bit-Ganzzahl passt
                    return SDSS.query_sql(sql, data_release=17)
            except Exception:
                if k == tries - 1:
                    raise
                time.sleep(20)

    g = Simbad.query_tap(f'''
SELECT b.ra, b.dec, b.rvz_radvel, b.galdim_majaxis, b.galdim_minaxis, b.galdim_angle, b.morph_type
FROM basic AS b JOIN ident AS i ON i.oidref = b.oid
WHERE i.id = '{SPEC_GALAXY}' ''').to_pandas().iloc[0]
    g_ra, g_dec, v_sys, g_a = g["ra"], g["dec"], g["rvz_radvel"], g["galdim_majaxis"]
    g_q = g["galdim_minaxis"] / g_a if pd.notna(g["galdim_minaxis"]) else 1.0
    g_pa = np.deg2rad(float(g["galdim_angle"]) if pd.notna(g["galdim_angle"]) else 0.0)
    dist = Simbad.query_tap(f'''SELECT m.dist, m.unit, m.method FROM mesDistance AS m JOIN ident AS i ON i.oidref = m.oidref
                            WHERE i.id = '{SPEC_GALAXY}' ''').to_pandas()
    dist["mpc"] = dist["dist"] * dist["unit"].str.strip().map({"Mpc": 1.0, "kpc": 1e-3, "pc": 1e-6})
    g_dist = dist.loc[dist["method"].str.strip() != "redshift", "mpc"].median()
    kpc_per_arcmin = g_dist * 1e3 * np.deg2rad(1 / 60)

    # Alle Spektren in einem Kasten um die Katalogellipse, Geschwindigkeit innerhalb von 600 km/s der Galaxie,
    # mit den Linienflüssen und Häufigkeiten aus dem MPA-JHU-Katalog, wo es sie gibt
    r_deg = g_a / 2 / 60
    query = f'''
SELECT s.specObjID, s.ra, s.dec, s.z, s.class, s.plate, s.mjd, s.fiberID, s.run2d, s.snMedian,
       l.h_alpha_flux AS mpa_Ha, l.h_beta_flux AS mpa_Hb, l.oiii_5007_flux AS mpa_OIII5007,
       l.nii_6584_flux AS mpa_NII6584, e.oh_p50 AS mpa_oh
FROM SpecObj AS s
LEFT JOIN galSpecLine AS l ON l.specObjID = s.specObjID
LEFT JOIN galSpecExtra AS e ON e.specObjID = s.specObjID
WHERE s.ra BETWEEN {g_ra - r_deg / np.cos(np.radians(g_dec))} AND {g_ra + r_deg / np.cos(np.radians(g_dec))}
  AND s.dec BETWEEN {g_dec - r_deg} AND {g_dec + r_deg}
  AND s.z BETWEEN {(v_sys - 600) / C_KMS} AND {(v_sys + 600) / C_KMS}
ORDER BY s.snMedian DESC'''
    spec_list = sdss_query(query)[:MAX_SPECTRA]
    spectra = SDSS.get_spectra(matches=spec_list, data_release=17)
    spec_list["specObjID"] = spec_list["specObjID"].astype(str)

    print(f"{SPEC_GALAXY}: Hubble-Typ {g['morph_type']}, v_sys = {v_sys:.0f} km/s, D = {g_dist:.2f} Mpc (1' = {kpc_per_arcmin:.2f} kpc), "
          f"Durchmesser {g_a:.1f}', q = {g_q:.2f}")
    print(f"{len(spec_list)} SDSS-Spektren geladen; Klassen der Pipeline: "
          f"{dict(zip(*np.unique(np.asarray(spec_list['class']), return_counts=True)))}")
    print(f"Mit Linienflüssen im MPA-JHU-Katalog: {np.isfinite(np.asarray(spec_list['mpa_Ha'], dtype=float)).sum()}")

    # Erster Blick: Lage der Fasern und das Spektrum mit dem höchsten Signal-Rausch-Verhältnis
    img_opt = hips2fits.query(hips="CDS/P/DSS2/color", width=500, height=500, ra=Angle(g_ra * u.deg), dec=Angle(g_dec * u.deg),
                              fov=Angle(1.2 * g_a * u.arcmin), projection="TAN", format="jpg")
    half_g = 0.6 * g_a
    dx_all = (np.asarray(spec_list["ra"]) - g_ra) * np.cos(np.radians(g_dec)) * 60     # Bogenminuten, Osten positiv
    dy_all = (np.asarray(spec_list["dec"]) - g_dec) * 60
    first = spectra[0][1].data
    fig, axes = plt.subplots(1, 2, figsize=(16, 5.5), gridspec_kw={"width_ratios": [1, 2.2]})
    axes[0].imshow(img_opt, extent=[half_g, -half_g, -half_g, half_g])
    for cls, col in [("GALAXY", "cyan"), ("STAR", "yellow")]:
        m = np.asarray(spec_list["class"]) == cls
        axes[0].scatter(dx_all[m], dy_all[m], s=30, facecolors="none", edgecolors=col, label=f"Pipeline-Klasse {cls} ({m.sum()})")
    axes[0].scatter(dx_all[0], dy_all[0], s=120, marker="s", facecolors="none", edgecolors="red", label="Spektrum rechts")
    axes[0].set_xlabel("ΔRA [']")
    axes[0].set_ylabel("ΔDec [']")
    axes[0].set_title(f"{SPEC_GALAXY}: SDSS-Fasern", fontsize=10)
    axes[0].legend(fontsize=7, loc="lower left")
    axes[1].plot(10 ** first["loglam"], first["flux"], c="black", lw=0.5)
    z0 = float(spec_list["z"][0])
    for k, (ln, lab) in enumerate(LABEL.items()):
        axes[1].axvline(LINES[ln] * (1 + z0), color="tab:red", lw=0.6, alpha=0.5)
        axes[1].text(LINES[ln] * (1 + z0) + 15, (0.95 - 0.07 * (k % 3)) * np.nanmax(first["flux"]), lab, fontsize=8, color="tab:red")
    axes[1].set_xlabel("Wellenlänge (Vakuum) [Å]")
    axes[1].set_ylabel("Fluss [10⁻¹⁷ erg s⁻¹ cm⁻² Å⁻¹]")
    axes[1].set_title(f"Rohes Spektrum, Faser mit dem höchsten S/N (z = {z0:.5f})", fontsize=10)
    fig.tight_layout()
    plt.show()


def line_fits():
    """11. Linienfits (Zellen 10 von galaxies_hiiregions.ipynb)."""
    global L, ax, axes, best, col, curve, curves, d, dv, er, err, f
    global fig, fit_group, fl, flux, gas, good, grp, ha_pipe, hdul, ivar, k, keys
    global ln, mcurve, n_masked, rec, rows, sp, stars, title, w, wave, z_fit, zl
    def fit_group(wave, flux, err, names, z0):
        # Gaußlinien mit gemeinsamer Rotverschiebung und Breite auf einem linearen Kontinuum
        lam0 = np.array([LINES[ln] for ln in names])
        m = (wave > lam0.min() * (1 + z0) - 25) & (wave < lam0.max() * (1 + z0) + 25) & np.isfinite(err)
        w, f, e = wave[m], flux[m], err[m]
        def model(w, z, sig, c0, c1, *amps):
            out = c0 + c1 * (w - w.mean())
            for a, l in zip(amps, lam0):
                out = out + a * np.exp(-0.5 * ((w - l * (1 + z)) / sig) ** 2)
            return out
        p0 = [z0, 2.0, np.median(f), 0.0] + [max(f.max() - np.median(f), 1.0)] * len(names)
        lo = [z0 - 0.002, 0.5, -np.inf, -np.inf] + [0.0] * len(names)
        hi = [z0 + 0.002, 8.0, np.inf, np.inf] + [np.inf] * len(names)
        popt, pcov = curve_fit(model, w, f, p0=p0, sigma=e, absolute_sigma=True, bounds=(lo, hi), maxfev=20000)
        perr = np.sqrt(np.diag(pcov))
        sig, dsig = popt[1], perr[1]
        fluxes = {ln: popt[4 + i] * sig * np.sqrt(2 * np.pi) for i, ln in enumerate(names)}
        errs = {ln: np.sqrt((perr[4 + i] * sig) ** 2 + (popt[4 + i] * dsig) ** 2) * np.sqrt(2 * np.pi) for i, ln in enumerate(names)}
        # Liegen im Kern einer Linie (± 2 σ) Pixel ohne Daten (ivar = 0, z. B. gesättigt), schätzt der Fit
        # die Höhe nur aus den Flanken; solche Linien werden verworfen
        for l, ln in zip(lam0, names):
            core = np.abs(wave - l * (1 + popt[0])) < 2 * sig
            if (~np.isfinite(err[core])).any():
                fluxes[ln], errs[ln] = np.nan, np.nan
        return fluxes, errs, popt[0], (w, f, model(w, *popt))

    rows, curves = [], {}
    for sp, hdul in zip(spec_list, spectra):
        d = hdul[1].data
        wave, flux, ivar = 10 ** d["loglam"], d["flux"], d["ivar"]
        err = np.where(ivar > 0, 1 / np.sqrt(np.where(ivar > 0, ivar, 1)), np.nan)
        rec = {"specObjID": sp["specObjID"], "ra": sp["ra"], "dec": sp["dec"], "z_sdss": sp["z"], "class": sp["class"]}
        try:
            for grp in GROUPS:
                fl, er, z_fit, curve = fit_group(wave, flux, err, grp, sp["z"])
                for ln in grp:
                    rec[ln], rec[ln + "_err"] = fl[ln], er[ln]
                if "Ha" in grp:
                    rec["z_own"] = z_fit
                curves.setdefault(sp["specObjID"], {})[grp[-1]] = curve
        except (RuntimeError, ValueError):
            continue
        zl = hdul[3].data                                   # Linienfits der SDSS-Pipeline (SPZLINE)
        ha_pipe = zl[zl["LINENAME"] == "H_alpha"]
        rec["Ha_pipeline"] = float(ha_pipe["LINEAREA"][0]) if len(ha_pipe) else np.nan
        for col in ["mpa_Ha", "mpa_Hb", "mpa_OIII5007", "mpa_NII6584", "mpa_oh"]:
            rec[col] = float(sp[col]) if not np.ma.is_masked(sp[col]) else np.nan
        rows.append(rec)
    L = pd.DataFrame(rows)

    def good(*names):
        # alle genannten Linien mit S/N über SN_MIN
        return np.all([L[ln] > SN_MIN * L[ln + "_err"] for ln in names], axis=0)

    L["v_own"] = L["z_own"] * C_KMS
    n_masked = sum(L[ln].isna().sum() for ln in LINES)
    print(f"{len(L)} von {len(spec_list)} Spektren angepasst; {n_masked} Linien verworfen, weil ihr Kern maskierte Pixel enthält")
    for ln in LINES:
        if L[ln].isna().any():
            print(f"  {ln}: in {L[ln].isna().sum()} Spektren")
    for ln in ["Ha", "Hb", "OIII5007", "NII6584", "SII6717", "SII6731"]:
        print(f"  {ln:9s} mit S/N > {SN_MIN:.0f}: {good(ln).sum():3d}")
    gas = good("Ha", "NII6584")                          # Gas mit Metalllinien, also H-II-Regionen in der Galaxie
    dv = (L.loc[gas, "z_own"] - L.loc[gas, "z_sdss"]) * C_KMS
    print(f"Eigene Geschwindigkeit aus Hα minus SDSS-Rotverschiebung: Median {dv.median():+.1f} km/s, Streuung {dv.std():.1f} km/s")
    print(f"Geschwindigkeiten der {gas.sum()} Regionen mit Hα und [N II]: {L.loc[gas, 'v_own'].min():.0f} bis {L.loc[gas, 'v_own'].max():.0f} km/s "
          f"(v_sys laut SIMBAD {v_sys:.0f} km/s)")
    stars = L["class"] == "STAR"
    print(f"Spektren der Klasse STAR: {stars.sum()}, davon mit [N II]: {(stars & gas).sum()}; Geschwindigkeiten "
          f"{', '.join(f'{v:.0f}' for v in np.sort(L.loc[stars, 'v_own']))} km/s")

    best = L.loc[L["Ha"].idxmax()]
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.2))
    for ax, keys, title in [(axes[0], ["Hb", "OIII5007"], "Hβ und [O III]"), (axes[1], ["NII6584"], "[N II] und Hα"),
                            (axes[2], ["SII6731"], "[S II] 6717, 6731")]:
        for k in keys:
            w, f, mcurve = curves[best["specObjID"]][k]
            ax.plot(w, f, c="black", lw=0.8, label="Daten" if k == keys[0] else None)
            ax.plot(w, mcurve, c="tab:red", lw=1.2, label="Fit" if k == keys[0] else None)
        ax.set_xlabel("Wellenlänge (Vakuum) [Å]")
        ax.set_title(title, fontsize=10)
        ax.legend(fontsize=8)
    axes[0].set_ylabel("Fluss [10⁻¹⁷ erg s⁻¹ cm⁻² Å⁻¹]")
    fig.suptitle(f"Gaußfits an die hellste H-II-Region (Hα = {best['Ha']:.0f} · 10⁻¹⁷ erg s⁻¹ cm⁻²)", y=1.02)
    fig.tight_layout()
    plt.show()


def density_dust():
    """12. Dichte und Staub (Zellen 13 von galaxies_hiiregions.ipynb)."""
    global A_SII, B_SII, C_SII, R_hi, R_lo, R_med, R_of_ne, above, axes, ebv_med, fig, n_med
    global ne, ne_of_R, ok_b, ok_s
    np.seterr(divide="ignore", invalid="ignore")                          # log von Nicht-Nachweisen -> NaN
    A_SII, B_SII, C_SII = 0.4315, 2107.0, 627.1                           # Sanders et al. (2016), T = 10^4 K
    def R_of_ne(ne):
        return A_SII * (B_SII + ne) / (C_SII + ne)
    def ne_of_R(R):
        return (C_SII * R - A_SII * B_SII) / (A_SII - R)

    L["R_SII"] = L["SII6717"] / L["SII6731"]
    L["balmer"] = L["Ha"] / L["Hb"]
    L["EBV"] = 2.5 / (3.61 - 2.53) * np.log10(L["balmer"] / 2.86)
    ok_s = good("SII6717", "SII6731", "Ha")
    ok_b = good("Ha", "Hb")
    R_med = L.loc[ok_s, "R_SII"].median()
    R_lo, R_hi = L.loc[ok_s, "R_SII"].quantile([0.16, 0.84])
    n_med = ne_of_R(R_med) if R_med < A_SII * B_SII / C_SII else 0.0
    above = (L.loc[ok_s, "R_SII"] > A_SII * B_SII / C_SII).mean()
    ebv_med = L.loc[ok_b, "EBV"].median()

    print(f"[S II] 6717/6731 in {ok_s.sum()} Regionen: Median {R_med:.3f} (16.-84. Perzentil {R_lo:.2f} bis {R_hi:.2f})")
    print(f"  -> n_e ≈ {n_med:.0f} cm⁻³ aus dem Median; {above:.0%} der Regionen liegen über dem Grenzwert 1.45 für n_e -> 0")
    print(f"Hα/Hβ in {ok_b.sum()} Regionen: Median {L.loc[ok_b, 'balmer'].median():.2f} (ohne Staub 2.86)")
    print(f"  -> E(B-V) ≈ {ebv_med:.2f} mag, A_V ≈ {3.1 * ebv_med:.2f} mag, also {1 - 10 ** (-0.4 * 2.53 * ebv_med):.0%} des Hα-Lichts "
          f"und {1 - 10 ** (-0.4 * 3.61 * ebv_med):.0%} des Hβ-Lichts vom Staub geschluckt")
    print(f"  Regionen mit Hα/Hβ < 2.86 (unphysikalisch, Rauschen oder Absorption der Sterne unter Hβ): {(L.loc[ok_b, 'balmer'] < 2.86).sum()}")

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    ne = np.logspace(0, 5, 300)
    axes[0].semilogx(ne, R_of_ne(ne), c="black", label="R(n_e), Sanders et al. (2016)")
    axes[0].axhspan(R_lo, R_hi, color="tab:blue", alpha=0.2, label="gemessen, 16.-84. Perzentil")
    axes[0].axhline(R_med, color="tab:blue", ls="--", label=f"Median {R_med:.2f}")
    axes[0].axhline(A_SII * B_SII / C_SII, color="grey", ls=":", lw=1, label="Grenzwert n_e → 0")
    axes[0].set_xlabel("Elektronendichte n_e [cm⁻³]")
    axes[0].set_ylabel("[S II] 6717 / 6731")
    axes[0].set_title("Elektronendichte aus dem [S II]-Dublett", fontsize=10)
    axes[0].legend(fontsize=8)
    axes[1].hist(L.loc[ok_b, "balmer"], bins=np.arange(2.0, 7.0, 0.2), color="tab:orange", alpha=0.7, label="H-II-Regionen")
    axes[1].axvline(2.86, color="black", ls=":", label="ohne Staub (Fall B): 2.86")
    axes[1].axvline(L.loc[ok_b, "balmer"].median(), color="tab:red", ls="--", label=f"Median {L.loc[ok_b, 'balmer'].median():.2f}")
    axes[1].set_xlabel("Hα / Hβ")
    axes[1].set_ylabel("Zahl der Regionen")
    axes[1].set_title("Balmer-Dekrement", fontsize=10)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()


def bpt():
    """13. Das BPT-Diagramm (Zellen 16 von galaxies_hiiregions.ipynb)."""
    global ax, below_kauff, below_kewley, bpt_ok, dxs, dys, fig, kauff, kewley, rN2, rO3, ref
    global ref_class, sc, xx, xx2
    L["logN2"] = np.log10(L["NII6584"] / L["Ha"])
    L["logO3"] = np.log10(L["OIII5007"] / L["Hb"])
    def kauff(x):
        return 0.61 / (x - 0.05) + 1.30
    def kewley(x):
        return 0.61 / (x - 0.47) + 1.19
    bpt_ok = good("Ha", "Hb", "OIII5007", "NII6584")
    below_kauff = (L["logN2"] < 0.0) & (L["logO3"] < kauff(L["logN2"]))
    below_kewley = (L["logN2"] < 0.4) & (L["logO3"] < kewley(L["logN2"]))
    L["bpt"] = np.where(~bpt_ok, "zu schwach", np.where(below_kauff, "Sternentstehung", np.where(below_kewley, "Mischform", "AGN")))
    L["star_forming"] = L["bpt"] == "Sternentstehung"

    ref = sdss_query('''SELECT TOP 20000 l.h_alpha_flux AS ha, l.h_beta_flux AS hb, l.oiii_5007_flux AS oiii, l.nii_6584_flux AS nii
FROM galSpecLine AS l WHERE l.h_alpha_flux > 5 * l.h_alpha_flux_err AND l.h_beta_flux > 5 * l.h_beta_flux_err
  AND l.oiii_5007_flux > 5 * l.oiii_5007_flux_err AND l.nii_6584_flux > 5 * l.nii_6584_flux_err
  AND l.h_alpha_flux_err > 0 AND l.h_beta_flux_err > 0''').to_pandas()
    rN2, rO3 = np.log10(ref["nii"] / ref["ha"]), np.log10(ref["oiii"] / ref["hb"])
    ref_class = np.where((rN2 < 0) & (rO3 < kauff(rN2)), "Sternentstehung",
                         np.where((rN2 < 0.4) & (rO3 < kewley(rN2)), "Mischform", "AGN"))

    print(f"{SPEC_GALAXY}: {bpt_ok.sum()} Regionen mit allen vier Linien über S/N {SN_MIN:.0f}:",
          L.loc[bpt_ok, "bpt"].value_counts().to_dict())
    print(f"Vergleichsgalaxien ({len(ref):,}):", {k: f"{v:.0%}" for k, v in pd.Series(ref_class).value_counts(normalize=True).items()})
    print(f"Bereich der H-II-Regionen: log [N II]/Hα von {L.loc[bpt_ok, 'logN2'].min():.2f} bis {L.loc[bpt_ok, 'logN2'].max():.2f}, "
          f"log [O III]/Hβ von {L.loc[bpt_ok, 'logO3'].min():.2f} bis {L.loc[bpt_ok, 'logO3'].max():.2f}")

    # Abstand vom Zentrum in der Scheibe, hier schon für die Farben gebraucht
    dxs = (L["ra"] - g_ra) * np.cos(np.radians(g_dec)) * 60
    dys = (L["dec"] - g_dec) * 60
    L["R_arcmin"] = np.hypot(dxs * np.sin(g_pa) + dys * np.cos(g_pa), (dxs * np.cos(g_pa) - dys * np.sin(g_pa)) / g_q)
    L["R_kpc"] = L["R_arcmin"] * kpc_per_arcmin

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hexbin(rN2, rO3, gridsize=80, extent=(-2, 0.7, -1.3, 1.5), bins="log", cmap="Greys", mincnt=1)
    xx = np.linspace(-2, 0.0, 200)
    ax.plot(xx, kauff(xx), "b--", lw=1, label="Kauffmann et al. (2003)")
    xx2 = np.linspace(-2, 0.4, 200)
    ax.plot(xx2, kewley(xx2), "r-", lw=1, label="Kewley et al. (2001)")
    sc = ax.scatter(L.loc[bpt_ok, "logN2"], L.loc[bpt_ok, "logO3"], c=L.loc[bpt_ok, "R_kpc"], cmap="viridis", s=30, edgecolor="k", zorder=3)
    fig.colorbar(sc, ax=ax, label="Abstand vom Zentrum [kpc]")
    ax.text(-1.6, -0.9, "Sternentstehung", fontsize=9)
    ax.text(0.05, 1.1, "AGN\n(Seyfert)", fontsize=9)
    ax.text(0.1, -0.6, "LINER,\nMischformen", fontsize=8)
    ax.set_xlim(-2, 0.7)
    ax.set_ylim(-1.3, 1.5)
    ax.set_xlabel("log [N II] 6584 / Hα")
    ax.set_ylabel("log [O III] 5007 / Hβ")
    ax.set_title(f"BPT-Diagramm: H-II-Regionen von {SPEC_GALAXY} vor {len(ref):,} SDSS-Galaxien", fontsize=10)
    ax.legend(fontsize=8, loc="lower left")
    fig.tight_layout()
    plt.show()


def metallicity_gradient():
    """14. Der Metallizitätsgradient (Zellen 19 von galaxies_hiiregions.ipynb)."""
    global R_disk, _, axes, c, col, ds, dz0, fig, fits, gradient, ls, mk
    global rr, s, sc, use, z0
    L["O3N2"] = L["logO3"] - L["logN2"]
    L["Z_N2"] = 8.90 + 0.57 * L["logN2"]                 # Pettini & Pagel (2004)
    L["Z_O3N2"] = 8.73 - 0.32 * L["O3N2"]                # Pettini & Pagel (2004)
    use = L["star_forming"] & L["O3N2"].between(-1, 1.9)

    def gradient(col):
        (slope, icpt), cov = np.polyfit(L.loc[use, "R_kpc"], L.loc[use, col], 1, cov=True)
        scatter = np.std(L.loc[use, col] - (icpt + slope * L.loc[use, "R_kpc"]), ddof=2)
        return slope, np.sqrt(cov[0, 0]), icpt, np.sqrt(cov[1, 1]), scatter

    fits = {col: gradient(col) for col in ["Z_O3N2", "Z_N2"]}
    R_disk = g_a / 2 * kpc_per_arcmin
    print(f"{use.sum()} Regionen mit Sternentstehung, Abstände {L.loc[use, 'R_kpc'].min():.1f} bis {L.loc[use, 'R_kpc'].max():.1f} kpc "
          f"(Katalogradius {R_disk:.1f} kpc)")
    for col, (s, ds, z0, dz0, sc) in fits.items():
        print(f"  {col[2:]:5s}: 12 + log(O/H) = {z0:.2f} ± {dz0:.2f} {s:+.4f} ± {ds:.4f} × R[kpc], Streuung um die Gerade {sc:.3f} dex, "
              f"über den Katalogradius {s * R_disk:+.2f} dex")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    axes[0].imshow(img_opt, extent=[half_g, -half_g, -half_g, half_g])
    sc = axes[0].scatter(dxs[use], dys[use], c=L.loc[use, "Z_O3N2"], cmap="coolwarm", s=45, edgecolor="white")
    fig.colorbar(sc, ax=axes[0], label="12 + log(O/H) (O3N2)")
    axes[0].set_xlabel("ΔRA [']")
    axes[0].set_ylabel("ΔDec [']")
    axes[0].set_title(f"{SPEC_GALAXY}: Sauerstoffhäufigkeit der H-II-Regionen", fontsize=10)
    rr = np.linspace(0, L.loc[use, "R_kpc"].max() * 1.05, 50)
    for col, c, mk, ls in [("Z_O3N2", "tab:red", "o", "-"), ("Z_N2", "tab:blue", "s", "--")]:
        s, ds, z0, dz0, _ = fits[col]
        axes[1].scatter(L.loc[use, "R_kpc"], L.loc[use, col], c=c, s=20, marker=mk, label=col[2:])
        axes[1].plot(rr, z0 + s * rr, c=c, ls=ls, label=f"{col[2:]}: {s:+.3f} ± {ds:.3f} dex/kpc")
    axes[1].axhline(8.69, color="grey", ls=":", label="Sonne: 8.69")
    axes[1].set_xlabel("Abstand vom Zentrum in der Scheibe [kpc]")
    axes[1].set_ylabel("12 + log(O/H)")
    axes[1].set_title("Radialer Gradient der Sauerstoffhäufigkeit", fontsize=10)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()


def pipeline_check():
    """15. Vergleich mit der SDSS-Pipeline und dem MPA-JHU-Katalog (Zellen 22 von galaxies_hiiregions.ipynb)."""
    global _, axes, bd_mpa, c, col, cov_t, dev, ds, dz0, fac, fig, i_t
    global lim, ln, ls, m, m_oh, m_ratio, mpa_N2, mpa_O3, ok_pipe, ratio_pipe, rr, rt
    global s, s_t, z0
    ok_pipe = good("Ha") & (L["Ha_pipeline"] > 0)
    ratio_pipe = L.loc[ok_pipe, "Ha"] / L.loc[ok_pipe, "Ha_pipeline"]
    print(f"Hα eigen / SDSS-Pipeline ({ok_pipe.sum()} Fasern): Median {ratio_pipe.median():.3f}, Streuung {ratio_pipe.std():.3f}")
    for ln in ["Ha", "Hb", "OIII5007", "NII6584"]:
        m = good(ln) & (L["mpa_" + ln] > 0)
        rt = L.loc[m, ln] / L.loc[m, "mpa_" + ln]
        print(f"{ln:9s} eigen / MPA-JHU ({m.sum()} Fasern): Median {rt.median():.3f}, Streuung {rt.std():.3f}")
    m_ratio = bpt_ok & (L[["mpa_Ha", "mpa_Hb", "mpa_OIII5007", "mpa_NII6584"]] > 0).all(axis=1)
    mpa_N2 = np.log10(L["mpa_NII6584"] / L["mpa_Ha"])
    mpa_O3 = np.log10(L["mpa_OIII5007"] / L["mpa_Hb"])
    print(f"Linienverhältnisse ({m_ratio.sum()} Fasern): log [N II]/Hα eigen minus MPA-JHU {np.median((L['logN2'] - mpa_N2)[m_ratio]):+.3f}, "
          f"log [O III]/Hβ {np.median((L['logO3'] - mpa_O3)[m_ratio]):+.3f}")
    # Ist der Unterschied ein Faktor pro Faser (Flusseichung) oder pro Linie (Linienfit)?
    fac = pd.DataFrame({ln: L[ln] / L["mpa_" + ln] for ln in ["Ha", "Hb", "OIII5007", "NII6584"]})[m_ratio]
    dev = {ln: f"{(fac[ln] / fac['Ha'] - 1).abs().median():.1%}" for ln in ["Hb", "OIII5007", "NII6584"]}
    print(f"Faktor eigen/MPA-JHU für Hα pro Faser: {fac['Ha'].quantile(0.1):.2f} bis {fac['Ha'].quantile(0.9):.2f} (10.-90. Perzentil); "
          f"die Faktoren der anderen Linien derselben Faser weichen im Median ab um {dev}")
    bd_mpa = (L["mpa_Ha"] / L["mpa_Hb"])[m_ratio]
    print(f"Balmer-Dekrement pro Faser eigen / MPA-JHU: Median {(L.loc[m_ratio, 'balmer'] / bd_mpa).median():.3f}; "
          f"E(B-V) eigen minus MPA-JHU: Median {np.median(2.31 * np.log10(L.loc[m_ratio, 'balmer'] / bd_mpa)):+.3f} mag")

    m_oh = use & (L["mpa_oh"] > 0)
    (s_t, i_t), cov_t = np.polyfit(L.loc[m_oh, "R_kpc"], L.loc[m_oh, "mpa_oh"], 1, cov=True)
    print(f"\nGradient aus MPA-JHU (oh_p50, Tremonti et al. 2004; {m_oh.sum()} Regionen): "
          f"12 + log(O/H) = {i_t:.2f} {s_t:+.4f} ± {np.sqrt(cov_t[0, 0]):.4f} × R[kpc]")
    print(f"Nullpunkte im Zentrum: O3N2 {fits['Z_O3N2'][2]:.2f}, N2 {fits['Z_N2'][2]:.2f}, MPA-JHU {i_t:.2f}; Sonne 8.69")

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.8))
    lim = [L.loc[ok_pipe, "Ha"].min() * 0.5, L.loc[ok_pipe, "Ha"].max() * 2]
    axes[0].loglog(L.loc[ok_pipe, "Ha_pipeline"], L.loc[ok_pipe, "Ha"], "o", ms=4, c="tab:green", label="SDSS-Pipeline")
    m = good("Ha") & (L["mpa_Ha"] > 0)
    axes[0].loglog(L.loc[m, "mpa_Ha"], L.loc[m, "Ha"], "s", ms=4, mfc="none", c="tab:purple", label="MPA-JHU")
    axes[0].plot(lim, lim, "k--", lw=1, label="1:1")
    axes[0].set_xlabel("Hα-Fluss im Katalog [10⁻¹⁷ erg s⁻¹ cm⁻²]")
    axes[0].set_ylabel("Hα-Fluss eigen [10⁻¹⁷ erg s⁻¹ cm⁻²]")
    axes[0].set_title("Hα: eigener Fit gegen Kataloge", fontsize=10)
    axes[0].legend(fontsize=8)
    axes[1].scatter(mpa_N2[m_ratio], L.loc[m_ratio, "logN2"], s=20, c="tab:blue", label="log [N II]/Hα")
    axes[1].scatter(mpa_O3[m_ratio], L.loc[m_ratio, "logO3"], s=20, c="tab:red", marker="s", label="log [O III]/Hβ")
    axes[1].plot([-1.5, 1], [-1.5, 1], "k--", lw=1, label="1:1")
    axes[1].set_xlabel("MPA-JHU")
    axes[1].set_ylabel("eigen")
    axes[1].set_title("Linienverhältnisse", fontsize=10)
    axes[1].legend(fontsize=8)
    rr = np.linspace(0, L.loc[use, "R_kpc"].max() * 1.05, 50)
    axes[2].scatter(L.loc[m_oh, "R_kpc"], L.loc[m_oh, "mpa_oh"], s=20, c="tab:purple", marker="^", label="MPA-JHU (Tremonti et al. 2004)")
    axes[2].plot(rr, i_t + s_t * rr, c="tab:purple", label=f"MPA-JHU: {s_t:+.3f} dex/kpc")
    for col, c, ls in [("Z_O3N2", "tab:red", "-"), ("Z_N2", "tab:blue", "--")]:
        s, ds, z0, dz0, _ = fits[col]
        axes[2].plot(rr, z0 + s * rr, c=c, ls=ls, label=f"{col[2:]} (Pettini & Pagel 2004): {s:+.3f} dex/kpc")
    axes[2].axhline(8.69, color="grey", ls=":", label="Sonne: 8.69")
    axes[2].set_xlabel("Abstand vom Zentrum in der Scheibe [kpc]")
    axes[2].set_ylabel("12 + log(O/H)")
    axes[2].set_title("Gradient in drei Eichungen", fontsize=10)
    axes[2].legend(fontsize=7)
    fig.tight_layout()
    plt.show()
