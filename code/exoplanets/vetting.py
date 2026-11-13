"""Vetting eines Transitsignals für exoplanets.ipynb: Ist es ein Planet auf dem Zielstern oder ein Fehlalarm?

Tests: verfeinerte Ephemeride, Differenzbild und Lichtschwerpunkt, Nachbarsterne aus Gaia DR3 in der Apertur, gerade
gegen ungerade Transits, sekundäre Bedeckung, nötige Bedeckungstiefe eines Nachbarn und Vergleich mit der Kepler Data
Validation (Tabelle cumulative des NASA Exoplanet Archive). Daten: Kepler über lightkurve aus MAST (alle Quartale in
Langzeitkadenz, ein Quartal Pixeldaten). Alle Schritte teilen sich ein Zustandsobjekt, das `load` anlegt.
"""
from types import SimpleNamespace

import numpy as np
import matplotlib.pyplot as plt
from astropy import units as u
from astropy.timeseries import BoxLeastSquares
from astropy.wcs.utils import proj_plane_pixel_scales
from astropy.coordinates import SkyCoord
from IPython.display import display

import archive
from lightcurves import lk, fold_phase, running_median, unmask

BKJD_OFFSET = 2454833.0          # Kepler-Zeit: BKJD = BJD - 2454833


def load(planet="Kepler-8 b", quarter=1):
    """Katalog-Ephemeride, Pixeldaten eines Quartals und alle Lichtkurven in Langzeitkadenz."""
    cat = archive.query("pscomppars", where=f"pl_name='{planet}'",
                        select="pl_name, hostname, pl_orbper, pl_tranmid, pl_trandur, pl_ratror, pl_ratdor, st_teff").iloc[0]
    P_cat = float(cat["pl_orbper"])
    T0_cat = float(cat["pl_tranmid"]) - BKJD_OFFSET      # Transitmitte in Kepler-Zeit
    T14 = float(cat["pl_trandur"]) / 24                   # Transitdauer [Tage]

    search_tpf = lk.search_targetpixelfile(planet, author="Kepler", exptime="long", quarter=quarter)
    tpf = search_tpf[0].download(quality_bitmask="default")

    search_lc = lk.search_lightcurve(planet, author="Kepler", exptime="long")
    search_lc = search_lc[np.argsort(np.asarray(search_lc.table["mission"]), kind="stable")]   # feste Reihenfolge
    print(f"Lade {len(search_lc)} Lichtkurven in Langzeitkadenz ...")
    stitched = search_lc.download_all(quality_bitmask="default").stitch()

    print(f"Planet:        {planet}")
    print(f"Ephemeride:    P = {P_cat:.6f} d,  T0 = {cat['pl_tranmid']:.5f} BJD = {T0_cat:.5f} BKJD")
    print(f"Transitdauer:  {T14 * 24:.2f} h")
    print(f"Pixeldaten:    {search_tpf.table['mission'][0]}, {tpf.shape[0]} Belichtungen, {tpf.shape[1]} x {tpf.shape[2]} Pixel")
    return SimpleNamespace(planet=planet, cat=cat, P_cat=P_cat, T0_cat=T0_cat, T14=T14, tpf=tpf, search_tpf=search_tpf,
                           search_lc=search_lc, stitched=stitched)


def ephemeris(s):
    """BLS um die Katalog-Periode, Trend mit ausgeblendeten Transits, gefaltete Lichtkurve aller Quartale."""
    stitched, P_cat, T0_cat, T14 = s.stitched, s.P_cat, s.T0_cat, s.T14
    t_all, f_all, e_all = unmask(stitched.time), unmask(stitched.flux), unmask(stitched.flux_err)
    good = np.isfinite(t_all) & np.isfinite(f_all) & np.isfinite(e_all)
    order = np.argsort(t_all[good])
    t_all, f_all, e_all = t_all[good][order], f_all[good][order], e_all[good][order]

    # BLS auf engem Gitter um die Katalog-Periode
    f_rough = f_all / running_median(t_all, f_all, 1.0, np.ones(len(t_all), bool))
    bls = BoxLeastSquares(t_all, f_rough, e_all).power(np.linspace(0.9995 * P_cat, 1.0005 * P_cat, 2000),
                                                       T14 * np.array([0.6, 0.8, 1.0]), objective="snr")
    k = np.argmax(bls.power)
    P_d = bls.period[k]
    T0 = T0_cat + fold_phase(bls.transit_time[k], P_d, T0_cat)       # Epoche nahe der Katalog-Epoche

    # Trend mit ausgeblendeten Transits
    oot = np.abs(fold_phase(t_all, P_d, T0)) > 0.75 * T14
    f_det = f_all / running_median(t_all, f_all, max(3 * T14, 0.75), oot)
    ph = fold_phase(t_all, P_d, T0)

    fig, ax = plt.subplots(figsize=(10, 4))
    sel = np.abs(ph) < 3 * T14
    ax.plot(ph[sel] * 24, f_det[sel], ".", ms=1, c="lightgrey", label="Belichtungen")
    edges = np.linspace(-3 * T14, 3 * T14, 73)
    kb = np.digitize(ph[sel], edges) - 1
    ax.plot(0.5 * (edges[1:] + edges[:-1]) * 24, [np.mean(f_det[sel][kb == i]) for i in range(72)], "o-", ms=3,
            c="tab:red", label="gemittelt")
    ax.set_xlabel("Zeit seit Transitmitte [h]")
    ax.set_ylabel("Relativer Fluss")
    ax.set_title(f"{s.planet}: {len(s.search_lc)} Quartale gefaltet ({int(np.ptp(t_all) / P_d)} Umläufe)")
    ax.legend()
    fig.tight_layout()
    plt.show()

    print(f"{len(t_all)} Belichtungen über {np.ptp(t_all):.0f} Tage")
    print(f"Verfeinerte Ephemeride: P = {P_d:.6f} d (Katalog {P_cat:.6f} d),  T0 = {T0:.5f} BKJD "
          f"(Verschiebung {24 * 60 * (T0 - T0_cat):+.1f} min)")
    s.__dict__.update(t_all=t_all, f_det=f_det, ph=ph, P_d=P_d, T0=T0)


def centroid_test(s):
    """Differenzbild (außerhalb minus innerhalb des Transits) je Transit und Lichtschwerpunkt mit Bootstrap-Fehler."""
    tpf, P_d, T0, T14 = s.tpf, s.P_d, s.T0, s.T14
    cube = unmask(tpf.flux)                                      # (Belichtungen, Zeilen, Spalten) in e⁻/s
    t_tpf = unmask(tpf.time)
    ph_tpf = fold_phase(t_tpf, P_d, T0)
    live = np.isfinite(cube).mean(axis=0) > 0.9                  # Pixel, die fast immer Werte haben
    cube[:, ~live] = 0.0                                         # tote Pixel (ohne Daten) tragen nichts bei
    finite = np.isfinite(t_tpf) & np.isfinite(cube).all(axis=(1, 2))
    in_t = finite & (np.abs(ph_tpf) < 0.35 * T14)                                  # Transitkern
    out_t = finite & (np.abs(ph_tpf) > 0.75 * T14) & (np.abs(ph_tpf) < 2.0 * T14)   # lokale Grundlinie
    epoch_tpf = np.round((t_tpf - T0) / P_d).astype(int)
    diffs = []                                                    # ein Differenzbild pro Transit, mit eigener Grundlinie
    for n in np.unique(epoch_tpf[in_t]):
        i_n, o_n = in_t & (epoch_tpf == n), out_t & (epoch_tpf == n)
        if i_n.sum() >= 2 and o_n.sum() >= 4:
            diffs.append(cube[o_n].mean(axis=0) - cube[i_n].mean(axis=0))
    diffs = np.array(diffs)
    img_out = cube[out_t].mean(axis=0)
    diff = diffs.mean(axis=0)                                     # > 0, wo während des Transits Licht fehlt
    diff_err = diffs.std(axis=0, ddof=1) / np.sqrt(len(diffs))
    diff_snr = np.where(live, diff / np.where(diff_err > 0, diff_err, np.inf), 0.0)

    aperture = tpf.pipeline_mask

    def centroid(img):
        """Lichtschwerpunkt über die Aperturpixel (negative Werte zählen nicht)."""
        w = np.where(aperture, np.clip(img, 0, None), 0.0)
        yy, xx = np.indices(img.shape)
        return (w * xx).sum() / w.sum(), (w * yy).sum() / w.sum()

    cx_out, cy_out = centroid(img_out)
    cx_dif, cy_dif = centroid(diff)
    pix_arcsec = proj_plane_pixel_scales(tpf.wcs).mean() * 3600
    offset_pix = np.hypot(cx_dif - cx_out, cy_dif - cy_out)
    offset_arcsec = offset_pix * pix_arcsec

    # Bootstrap: Transits neu ziehen, Schwerpunkt des Differenzbilds neu rechnen
    rng = np.random.default_rng(1)
    boot = np.array([centroid(diffs[rng.integers(0, len(diffs), len(diffs))].mean(axis=0)) for _ in range(500)])
    offset_err_pix = np.hypot(*boot.std(axis=0))
    offset_err_arcsec = offset_err_pix * pix_arcsec

    print(f"{len(diffs)} Transits im Quartal: {in_t.sum()} Belichtungen im Transitkern, {out_t.sum()} in der Grundlinie; "
          f"{int((~live).sum())} Pixel ohne Daten")
    print(f"Schwerpunkt außerhalb des Transits: x = {cx_out:.3f}, y = {cy_out:.3f} Pixel")
    print(f"Schwerpunkt des Differenzbilds:     x = {cx_dif:.3f}, y = {cy_dif:.3f} Pixel")
    print(f"Abstand: {offset_pix:.3f} ± {offset_err_pix:.3f} Pixel = {offset_arcsec:.2f} ± {offset_err_arcsec:.2f}\"   "
          f"(Pixelgröße {pix_arcsec:.2f}\")")
    print(f"Größtes SNR im Differenzbild: {np.nanmax(diff_snr):.1f}")
    s.__dict__.update(img_out=img_out, diff=diff, diff_snr=diff_snr, aperture=aperture, cx_out=cx_out, cy_out=cy_out,
                      cx_dif=cx_dif, cy_dif=cy_dif, pix_arcsec=pix_arcsec, offset_pix=offset_pix,
                      offset_arcsec=offset_arcsec, offset_err_pix=offset_err_pix, offset_err_arcsec=offset_err_arcsec)


def neighbours(s):
    """Gaia-DR3-Sterne um das Ziel, ihr Licht in der Apertur und die drei Bilder (Pixel, Differenz, SNR)."""
    tpf, aperture, pix_arcsec = s.tpf, s.aperture, s.pix_arcsec
    img_out, diff, diff_snr = s.img_out, s.diff, s.diff_snr
    cx_out, cy_out, cx_dif, cy_dif = s.cx_out, s.cy_out, s.cx_dif, s.cy_dif
    radius = pix_arcsec * max(tpf.shape[1:]) * 0.8 * u.arcsec
    gaia = archive.gaia_region(tpf.ra, tpf.dec, radius.value)
    coords = SkyCoord(gaia["RA_ICRS"].values, gaia["DE_ICRS"].values, unit="deg")   # Epoche 2016; Eigenbewegung vernachlässigbar
    gaia["x"], gaia["y"] = tpf.wcs.world_to_pixel(coords)
    gaia["sep_arcsec"] = coords.separation(SkyCoord(tpf.ra, tpf.dec, unit="deg")).arcsec
    target = gaia.loc[gaia["sep_arcsec"].idxmin()]
    col_i, row_i = np.round(gaia["x"]).astype(int), np.round(gaia["y"]).astype(int)
    inside = (col_i >= 0) & (row_i >= 0) & (col_i < aperture.shape[1]) & (row_i < aperture.shape[0])
    gaia["in_aperture"] = False
    gaia.loc[inside, "in_aperture"] = aperture[row_i[inside], col_i[inside]]
    gaia["flux_rel"] = 10 ** (-0.4 * (gaia["Gmag"] - target["Gmag"]))
    contam = gaia.loc[gaia["in_aperture"] & (gaia["Source"] != target["Source"]), "flux_rel"].sum() / \
             gaia.loc[gaia["in_aperture"], "flux_rel"].sum()
    crowdsap = tpf.hdu[1].header.get("CROWDSAP", np.nan)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    panels = [(img_out, "Bild außerhalb des Transits [e⁻/s]", "viridis"),
              (diff, "Differenzbild: außerhalb − innerhalb [e⁻/s]", "RdBu_r"),
              (diff_snr, "Differenzbild: SNR pro Pixel", "RdBu_r")]
    for ax, (img, title, cmap) in zip(axes, panels):
        lim = np.nanmax(np.abs(img)) if cmap == "RdBu_r" else None
        im = ax.imshow(img, origin="lower", cmap=cmap, vmin=-lim if lim else None, vmax=lim)
        fig.colorbar(im, ax=ax, fraction=0.046)
        for yy_, xx_ in zip(*np.nonzero(aperture)):              # Apertur der Pipeline: jedes Pixel umrandet
            ax.add_patch(plt.Rectangle((xx_ - 0.5, yy_ - 0.5), 1, 1, fill=False, ec="orange", lw=1.5))
        sizes = 250 * gaia["flux_rel"]
        ax.scatter(gaia["x"], gaia["y"], s=np.clip(sizes, 15, 400), facecolors="none", edgecolors="magenta", lw=1.5,
                   label="Gaia DR3 (Größe ~ Fluss)")
        ax.scatter([target["x"]], [target["y"]], marker="*", s=200, c="red", label="Zielstern (Gaia)")
        ax.plot(cx_out, cy_out, "+", c="white", ms=12, mew=2, label="Schwerpunkt außerhalb des Transits")
        ax.plot(cx_dif, cy_dif, "x", c="black", ms=10, mew=2, label="Schwerpunkt Differenzbild")
        ax.set_xlim(-0.5, img.shape[1] - 0.5)
        ax.set_ylim(-0.5, img.shape[0] - 0.5)
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("Pixelspalte")
        ax.set_ylabel("Pixelzeile")
    axes[0].plot([], [], "s", mfc="none", mec="orange", label="Apertur der Pipeline")
    axes[0].legend(fontsize=7, loc="upper left")
    fig.suptitle(f"{s.planet}: Welcher Stern wird dunkler? ({s.search_tpf.table['mission'][0]}, {pix_arcsec:.2f}\"/Pixel)")
    fig.tight_layout()
    plt.show()

    print(f"Gaia DR3: {len(gaia)} Sterne im Umkreis von {radius:.0f}, davon {int(gaia['in_aperture'].sum())} in der Apertur")
    print(f"Fremdlicht in der Apertur, eigene Schätzung aus Gaia: {100 * contam:.2f} %")
    print(f"Fremdlicht in der Apertur, Pipeline (1 − CROWDSAP):   {100 * (1 - crowdsap):.2f} %")
    display(gaia[["Source", "Gmag", "sep_arcsec", "in_aperture"]].sort_values("sep_arcsec").round(2))
    s.gaia, s.target = gaia, target


def odd_even(s):
    """Tiefe gerader und ungerader Transits und sekundäre Bedeckung bei Phase 0.5."""
    t_all, f_det, ph, P_d, T0, T14 = s.t_all, s.f_det, s.ph, s.P_d, s.T0, s.T14
    epoch = np.round((t_all - T0) / P_d).astype(int)
    core = np.abs(ph) < 0.35 * T14
    ref = (np.abs(ph) > 0.75 * T14) & (np.abs(ph) < 2 * T14)

    def dip(sel_in, sel_ref):
        d = np.mean(f_det[sel_ref]) - np.mean(f_det[sel_in])
        return d, np.sqrt(np.var(f_det[sel_in]) / sel_in.sum() + np.var(f_det[sel_ref]) / sel_ref.sum())

    d_all, e_all_d = dip(core, ref)
    d_odd, e_odd = dip(core & (epoch % 2 == 1), ref & (epoch % 2 == 1))
    d_even, e_even = dip(core & (epoch % 2 == 0), ref & (epoch % 2 == 0))
    ph2 = fold_phase(t_all, P_d, T0 + P_d / 2)                     # Phase 0.5 bei Kreisbahn
    d_sec, e_sec = dip(np.abs(ph2) < 0.35 * T14, (np.abs(ph2) > 0.75 * T14) & (np.abs(ph2) < 2 * T14))
    sigma_oe = abs(d_odd - d_even) / np.hypot(e_odd, e_even)
    sec_limit = max(d_sec, 0) + 3 * e_sec                          # 3σ-Obergrenze

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.5))
    e = np.linspace(-2 * T14 * 24, 2 * T14 * 24, 41)
    for parity, c, name, d in [(1, "tab:blue", "ungerade", d_odd), (0, "tab:orange", "gerade", d_even)]:
        sel = (epoch % 2 == parity) & (np.abs(ph) < 2 * T14)
        kk = np.digitize(ph[sel] * 24, e) - 1
        axes[0].plot(0.5 * (e[1:] + e[:-1]), [np.mean(f_det[sel][kk == i]) for i in range(40)], "o-", c=c, ms=3,
                     label=f"{name} Transits: Tiefe {1e6 * d:.0f} ppm")
    axes[0].set_xlabel("Zeit seit Transitmitte [h]")
    axes[0].set_ylabel("Relativer Fluss")
    axes[0].set_title("Gerade gegen ungerade Transits (ein Doppelstern mit Periode 2P wäre verschieden)", fontsize=10)
    axes[0].legend(fontsize=8)
    sel = np.abs(ph2) < 2 * T14
    e2 = np.linspace(-2 * T14 * 24, 2 * T14 * 24, 31)
    kk = np.digitize(ph2[sel] * 24, e2) - 1
    axes[1].plot(0.5 * (e2[1:] + e2[:-1]), [1e6 * (np.mean(f_det[sel][kk == i]) - 1) for i in range(30)], "o-",
                 c="tab:red", ms=3, label="gemittelt")
    axes[1].axvspan(-0.35 * T14 * 24, 0.35 * T14 * 24, color="grey", alpha=0.2, label="erwartete Bedeckung (Kreisbahn)")
    axes[1].axhline(0, color="black", lw=0.8)
    axes[1].set_xlabel("Zeit seit Phase 0.5 [h]")
    axes[1].set_ylabel("Relativer Fluss − 1 [ppm]")
    axes[1].set_title(f"Sekundäre Bedeckung: {1e6 * d_sec:.0f} ± {1e6 * e_sec:.0f} ppm", fontsize=10)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()

    print(f"Transittiefe (Kern, alle {len(np.unique(epoch[core]))} Transits): {1e6 * d_all:.0f} ± {1e6 * e_all_d:.0f} ppm")
    print(f"Ungerade / gerade:  {1e6 * d_odd:.0f} ± {1e6 * e_odd:.0f} ppm  /  {1e6 * d_even:.0f} ± {1e6 * e_even:.0f} ppm"
          f"   ->  Unterschied {sigma_oe:.1f} σ")
    print(f"Sekundäre Bedeckung: {1e6 * d_sec:.0f} ± {1e6 * e_sec:.0f} ppm   (3σ-Obergrenze {1e6 * sec_limit:.0f} ppm)")
    s.__dict__.update(d_all=d_all, d_sec=d_sec, e_sec=e_sec, sigma_oe=sigma_oe, sec_limit=sec_limit)


def planck_ratio(T1, T2, lam_um=0.65):
    """B_λ(T1) / B_λ(T2) bei der Wellenlänge lam_um (Kepler-Band etwa 0.65 µm)."""
    x = 14387.77 / lam_um                                     # hc/(λk) in K
    return np.expm1(x / T2) / np.expm1(x / T1)


def verdict(s):
    """Nötige Bedeckungstiefe der Nachbarn, erwartete sekundäre Bedeckung eines Planeten, Zusammenfassung der Tests."""
    gaia, target, cat, d_all, d_sec, e_sec, sec_limit = s.gaia, s.target, s.cat, s.d_all, s.d_sec, s.e_sec, s.sec_limit
    # (a) Welche Bedeckungstiefe bräuchte jeder Stern in der Apertur?
    in_ap = gaia[gaia["in_aperture"]].copy()
    in_ap["c"] = in_ap["flux_rel"] / in_ap["flux_rel"].sum()
    in_ap["nötige Tiefe [%]"] = 100 * d_all / in_ap["c"]
    print("Sterne in der Apertur und die Bedeckungstiefe, die sie selbst für den beobachteten Einbruch bräuchten:")
    display(in_ap[["Source", "Gmag", "sep_arcsec", "c", "nötige Tiefe [%]"]].round(4))

    # (b) Erwartete sekundäre Bedeckung eines Planeten
    k_rr, a_rs, T_star = cat["pl_ratror"], cat["pl_ratdor"], cat["st_teff"]
    print(f"\nErwartete sekundäre Bedeckung eines Planeten (Rp/R* = {k_rr:.4f}, a/R* = {a_rs:.2f}, T* = {T_star:.0f} K):")
    planet_max = 0.0
    for f_red, label in [(1 / 4, "volle Wärmeverteilung"), (2 / 3, "keine Wärmeverteilung")]:
        T_day = T_star * np.sqrt(1 / a_rs) * f_red ** 0.25         # Bond-Albedo 0
        thermal = k_rr ** 2 * planck_ratio(T_day, T_star)
        for A_g in [0.0, 0.1, 0.3]:
            refl = A_g * (k_rr / a_rs) ** 2
            planet_max = max(planet_max, thermal + refl)
            print(f"  {label:23s} T_Tag = {T_day:4.0f} K,  A_g = {A_g:.1f}:  thermisch {1e6 * thermal:4.1f} ppm "
                  f"+ reflektiert {1e6 * refl:4.1f} ppm = {1e6 * (thermal + refl):4.1f} ppm")
    print(f"Gemessen: {1e6 * d_sec:.0f} ± {1e6 * e_sec:.0f} ppm, 3σ-Obergrenze {1e6 * sec_limit:.0f} ppm")

    # (c) Zusammenfassung der Tests
    tests = [
        ("Differenzbild-Schwerpunkt auf dem Zielstern (< 3σ)", s.offset_pix < 3 * s.offset_err_pix,
         f"{s.offset_arcsec:.2f} ± {s.offset_err_arcsec:.2f}\" ({s.offset_pix / s.offset_err_pix:.1f} σ)"),
        ("Kein Nachbarstern in der Apertur kann den Einbruch erzeugen",
         bool((in_ap.loc[in_ap["Source"] != target["Source"], "nötige Tiefe [%]"] > 100).all()),
         f"kleinste nötige Tiefe {in_ap.loc[in_ap['Source'] != target['Source'], 'nötige Tiefe [%]'].min():.0f} %"
         if (in_ap["Source"] != target["Source"]).any() else "kein Nachbar in der Apertur"),
        ("Gerade und ungerade Transits gleich tief (< 3σ)", s.sigma_oe < 3, f"{s.sigma_oe:.1f} σ"),
        ("Sekundäre Bedeckung nicht tiefer als bei einem Planeten möglich", sec_limit <= planet_max,
         f"3σ-Obergrenze {1e6 * sec_limit:.0f} ppm, Planet bis {1e6 * planet_max:.0f} ppm"),
    ]
    print()
    print(f"{'Test':<64}{'Ergebnis':<18}{'Messwert'}")
    print("-" * 120)
    for name, passed, value in tests:
        print(f"{name:<64}{'bestanden' if passed else 'NICHT bestanden':<18}{value}")
    print(f"\nGesamt: {'alle Tests passen zu einem Planeten auf dem Zielstern' if all(t[1] for t in tests) else 'mindestens ein Test spricht dagegen, genauer prüfen'}")


def compare_dv(s):
    """Eigene Tests gegen die Kepler Data Validation (KOI-Tabelle cumulative)."""
    koi = archive.query("cumulative", where=f"kepler_name='{s.planet}'",
                        select="kepoi_name, kepler_name, koi_disposition, koi_score, koi_fpflag_nt, koi_fpflag_ss, "
                               "koi_fpflag_co, koi_fpflag_ec, koi_dicco_msky, koi_dicco_msky_err, koi_depth, koi_period")
    if len(koi) == 0:
        print(f"{s.planet} steht nicht in der KOI-Tabelle (kein Kepler-Kandidat).")
        return
    r = koi.iloc[0]
    print(f"{r['kepoi_name']} = {r['kepler_name']}: Einstufung {r['koi_disposition']}, koi_score = {r['koi_score']:.3f}")
    print("Warnflaggen der Pipeline (1 = Hinweis auf einen Fehlalarm):")
    for col, meaning in [("koi_fpflag_nt", "kein transitähnliches Signal"),
                         ("koi_fpflag_ss", "Doppelstern: sekundäre Bedeckung oder ungleiche Tiefen"),
                         ("koi_fpflag_co", "Quelle neben dem Zielstern (Schwerpunkt)"),
                         ("koi_fpflag_ec", "Signal kopiert von einem anderen Stern (Ephemeriden-Abgleich)")]:
        print(f"  {col:15s} = {int(r[col])}   {meaning}")
    print()
    print(f"{'Größe':<44}{'eigene Messung':<22}{'Kepler DV'}")
    print("-" * 84)
    rows = [("Differenzbild-Schwerpunkt, Abstand", f'{s.offset_arcsec:.2f} ± {s.offset_err_arcsec:.2f}"',
             f'{r["koi_dicco_msky"]:.2f} ± {r["koi_dicco_msky_err"]:.2f}"'),
            ("Transittiefe [ppm]", f"{1e6 * s.d_all:.0f}", f"{r['koi_depth']:.0f}"),
            ("Periode [d]", f"{s.P_d:.6f}", f"{r['koi_period']:.6f}")]
    for name, own, ref in rows:
        print(f"{name:<44}{own:<22}{ref}")
