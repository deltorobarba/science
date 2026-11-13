"""Transitsuche für exoplanets.ipynb: Kepler-Pixeldaten, Trend, Box Least Squares (BLS), gefaltete Lichtkurve,
physikalisches Transitmodell mit quadratischer Randverdunkelung und Vergleich mit dem NASA Exoplanet Archive.

Daten: Kepler über lightkurve aus MAST (ein Quartal Pixeldaten in Langzeitkadenz, sechs Lichtkurven in 1-Minuten-Kadenz),
Katalogwerte aus der Tabelle pscomppars des NASA Exoplanet Archive. Alle Schritte teilen sich ein Zustandsobjekt, das
`catalog` anlegt und die übrigen Funktionen ergänzen.
"""
from types import SimpleNamespace

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy.timeseries import BoxLeastSquares
from scipy.optimize import curve_fit

import archive
from lightcurves import lk, fold_phase, running_median, unmask

G_CGS = 6.674e-8                 # Gravitationskonstante [cm³ g⁻¹ s⁻²]


def catalog(planet="Kepler-8 b"):
    """Katalogwerte des Planeten; gibt das Zustandsobjekt zurück."""
    cat = archive.query("pscomppars", where=f"pl_name='{planet}'",
                        select="pl_name, hostname, pl_orbper, pl_rade, pl_ratror, pl_ratdor, pl_imppar, pl_orbincl, "
                               "pl_trandur, st_rad, st_mass, st_dens, st_teff").iloc[0]
    print(f"Planet:          {cat['pl_name']}  (Stern {cat['hostname']}, T_eff = {cat['st_teff']:.0f} K)")
    print(f"Katalog-Periode: {cat['pl_orbper']:.5f} d")
    print(f"Katalog-Radius:  {cat['pl_rade']:.2f} R_Erde  (Sternradius {cat['st_rad']:.2f} R_Sonne)")
    print(f"Transitdauer:    {cat['pl_trandur']:.2f} h")
    return SimpleNamespace(planet=planet, cat=cat)


def raw(s, quarter=1):
    """Pixelbild und Rohlichtkurve eines Quartals."""
    search = lk.search_targetpixelfile(s.planet, author="Kepler", exptime="long", quarter=quarter)
    if len(search) == 0:
        raise RuntimeError(f"Keine Kepler-Pixeldaten für {s.planet} in Quartal {quarter}.")
    tpf = search[0].download(quality_bitmask="default")
    lc_raw = tpf.to_lightcurve(aperture_mask=tpf.pipeline_mask)

    print(f"{search.table['mission'][0]}: {tpf.shape[0]} Belichtungen, {tpf.shape[1]} x {tpf.shape[2]} Pixel, "
          f"Dauer {np.ptp(tpf.time.value):.1f} Tage")

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.5), gridspec_kw={"width_ratios": [1, 2.2]})
    tpf.plot(ax=axes[0], aperture_mask=tpf.pipeline_mask, scale="log", title=f"{s.planet}: Pixelbild (log)")
    axes[1].plot(lc_raw.time.value, lc_raw.flux.value, ".", ms=2, c="black")
    axes[1].set_xlabel("Zeit [BKJD = BJD − 2454833, Tage]")
    axes[1].set_ylabel("Fluss in der Apertur [e⁻/s]")
    axes[1].set_title(f"Rohlichtkurve, {search.table['mission'][0]}")
    fig.tight_layout()
    plt.show()
    s.quarter, s.tpf, s.lc_raw = quarter, tpf, lc_raw


def detrend(s, window_length=101):
    """Normieren, Ausreißer über 5σ entfernen, langsamen Trend mit einem Savitzky-Golay-Filter teilen."""
    lc = s.lc_raw.remove_nans().remove_outliers(sigma=5).normalize()
    lc_flat = lc.flatten(window_length=window_length)

    fig, axes = plt.subplots(2, 1, figsize=(13, 6), sharex=True)
    axes[0].plot(lc.time.value, lc.flux.value, ".", ms=2, c="grey", label="normiert")
    axes[0].set_ylabel("Relativer Fluss")
    axes[0].set_title(f"{s.planet}: Lichtkurve vor und nach dem Entfernen des Trends")
    axes[0].legend()
    axes[1].plot(lc_flat.time.value, lc_flat.flux.value, ".", ms=2, c="tab:green", label="ohne Trend")
    axes[1].set_xlabel("Zeit [BKJD, Tage]")
    axes[1].set_ylabel("Relativer Fluss")
    axes[1].legend()
    fig.tight_layout()
    plt.show()
    s.lc, s.lc_flat = lc, lc_flat


def periodogram(s, durations=np.linspace(0.04, 0.30, 12)):
    """BLS grob über 0.5 bis 20 Tage, dann fein um den stärksten Peak."""
    cat, lc_flat = s.cat, s.lc_flat
    pg_coarse = lc_flat.to_periodogram(method="bls", minimum_period=0.5, maximum_period=20.0,
                                       duration=durations, frequency_factor=1)
    p_coarse = pg_coarse.period_at_max_power.value
    pg = lc_flat.to_periodogram(method="bls", period=np.linspace(0.995 * p_coarse, 1.005 * p_coarse, 4000),
                                duration=durations)

    period = pg.period_at_max_power.value              # [d]
    t0 = pg.transit_time_at_max_power.value            # [BKJD]
    duration = pg.duration_at_max_power.value          # [d]
    depth = float(pg.depth_at_max_power.value)

    fig, ax = plt.subplots(figsize=(13, 4))
    ax.plot(pg_coarse.period.value, pg_coarse.power.value, c="black", lw=0.6)
    ax.axvline(period, color="tab:red", ls="--", alpha=0.7, label=f"Maximum: P = {period:.4f} d")
    for n in (2, 3):
        ax.axvline(period / n, color="grey", ls=":", lw=1, label="Aliase P/2, P/3" if n == 2 else None)
    ax.set_xscale("log")
    ax.set_xlabel("Periode [Tage]")
    ax.set_ylabel("BLS-Power")
    ax.set_title(f"BLS-Periodogramm, {s.planet}, Quartal {s.quarter} ({len(pg_coarse.period)} Perioden)")
    ax.legend()
    fig.tight_layout()
    plt.show()

    print(f"Periode:        {period:.5f} d   (Katalog {cat['pl_orbper']:.5f} d, Abweichung "
          f"{abs(period - cat['pl_orbper']) / cat['pl_orbper'] * 100:.3f} %)")
    print(f"Transitmitte:   T0 = {t0:.4f} BKJD")
    print(f"Kastendauer:    {duration * 24:.2f} h   (Katalog T14 = {cat['pl_trandur']:.2f} h)")
    print(f"Kastentiefe:    {depth * 1e6:.0f} ppm  ->  Rp/R* = {np.sqrt(depth):.4f}   (Katalog {cat['pl_ratror']:.4f})")
    s.period, s.t0, s.duration, s.depth = period, t0, duration, depth


def fold(s):
    """Alle Transits auf die gefundene Periode falten."""
    period, t0, duration, lc_flat = s.period, s.t0, s.duration, s.lc_flat
    folded = lc_flat.fold(period=period, epoch_time=t0)
    binned = folded.bin(time_bin_size=duration / 8)

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(folded.time.value * 24, folded.flux.value, ".", ms=2, c="lightgrey", label="Belichtungen")
    ax.plot(binned.time.value * 24, binned.flux.value, "o-", ms=3, c="tab:red", label="gemittelt")
    ax.set_xlim(-3 * duration * 24, 3 * duration * 24)
    ax.set_xlabel("Zeit seit Transitmitte [h]")
    ax.set_ylabel("Relativer Fluss")
    ax.set_title(f"{s.planet}: gefaltet mit P = {period:.4f} d ({int(np.ptp(lc_flat.time.value) / period)} Transits)")
    ax.legend()
    fig.tight_layout()
    plt.show()


def transit_flux(z, p, u1, u2, n_r=400):
    """Relativer Fluss eines quadratisch randverdunkelten Sterns, den ein Planet mit Radius p (in Sternradien)
    im projizierten Abstand z bedeckt. Numerische Integration über Ringe der Sternscheibe (Genauigkeit ~1e-6)."""
    r = (np.arange(n_r) + 0.5) / n_r                         # Ringradien auf der Sternscheibe
    mu = np.sqrt(1 - r ** 2)
    I = 1 - u1 * (1 - mu) - u2 * (1 - mu) ** 2               # Intensität mit Randverdunkelung
    z = np.atleast_1d(z)[:, None]
    # halber Winkel des Bogens von Ring r, der innerhalb der Planetenscheibe liegt
    cos_th = np.clip((r ** 2 + z ** 2 - p ** 2) / (2 * r * np.maximum(z, 1e-12)), -1, 1)
    theta = np.where(r + z <= p, np.pi, np.where(np.abs(r - z) >= p, 0.0, np.arccos(cos_th)))
    return 1 - (I * theta * r).sum(axis=1) / (np.pi * (I * r).sum())


def transit_model(t, dt0, p, a_rs, b, q1, q2, period_d, exptime_d, n_sub):
    """Kreisbahn; t in Tagen seit Transitmitte; Randverdunkelung nach Kipping (2013) mit q1, q2 in [0, 1].
    Jede Belichtung wird über ihre Dauer gemittelt (n_sub Stützpunkte)."""
    u1, u2 = 2 * np.sqrt(q1) * q2, np.sqrt(q1) * (1 - 2 * q2)
    inc = np.arccos(np.clip(b / a_rs, 0, 1))
    offsets = (np.arange(n_sub) - (n_sub - 1) / 2) / n_sub * exptime_d
    phase = 2 * np.pi * (np.asarray(t)[:, None] + offsets - dt0).ravel() / period_d
    z = a_rs * np.sqrt(np.sin(phase) ** 2 + (np.cos(inc) * np.cos(phase)) ** 2)
    z = np.where(np.cos(phase) > 0, z, 10.0)                  # Planet hinter dem Stern: kein Transit
    return transit_flux(z, p, u1, u2).reshape(len(t), n_sub).mean(axis=1)


def fit(s, n_files=6, short_cadence=True):
    """Transitmodell an n_files Lichtkurven (1-Minuten-Kadenz, wenn vorhanden) anpassen."""
    cat, period, duration = s.cat, s.period, s.duration
    # Daten: Pipeline-Lichtkurven, feste Reihenfolge (Q00, Q01, ...), damit jeder Lauf dieselben Dateien nimmt
    lc_search = lk.search_lightcurve(s.planet, author="Kepler")
    exptimes = np.asarray(lc_search.table["exptime"], dtype=float)
    FIT_EXPTIME = exptimes.min() if short_cadence and exptimes.min() <= 120 else 1800.0
    lc_search = lc_search[exptimes == FIT_EXPTIME]
    lc_search = lc_search[np.argsort(np.asarray(lc_search.table["mission"]), kind="stable")]
    n_files = min(n_files, len(lc_search))
    print(f"Lade {n_files} von {len(lc_search)} Lichtkurven ({FIT_EXPTIME:.0f} s Kadenz) ...")
    stitched = lc_search[:n_files].download_all(quality_bitmask="default").stitch()    # jede Datei auf 1 normiert
    t_all, f_all, e_all = unmask(stitched.time), unmask(stitched.flux), unmask(stitched.flux_err)
    good = np.isfinite(t_all) & np.isfinite(f_all) & np.isfinite(e_all)
    order = np.argsort(t_all[good])
    t_all, f_all, e_all = t_all[good][order], f_all[good][order], e_all[good][order]
    print(f"{len(t_all)} Belichtungen über {np.ptp(t_all):.0f} Tage")

    # Ephemeride: BLS auf engem Gitter um die Periode aus dem Periodogramm
    T14_guess = cat["pl_trandur"] / 24 if np.isfinite(cat["pl_trandur"]) else duration
    f_rough = f_all / running_median(t_all, f_all, 1.0, np.ones(len(t_all), bool))
    bls = BoxLeastSquares(t_all, f_rough, e_all).power(np.linspace(0.998 * period, 1.002 * period, 3000),
                                                       T14_guess * np.array([0.6, 0.8, 1.0, 1.2]), objective="snr")
    k = np.argmax(bls.power)
    P_d, t0_d, T14, depth_bls = bls.period[k], bls.transit_time[k], bls.duration[k], bls.depth[k]

    # Trend mit ausgeblendeten Transits, dann falten
    out_of_transit = np.abs(fold_phase(t_all, P_d, t0_d)) > 0.75 * T14
    f_det = f_all / running_median(t_all, f_all, max(3 * T14, 0.75), out_of_transit)
    ph = fold_phase(t_all, P_d, t0_d)
    win = np.abs(ph) < 2.5 * T14
    t_fit, f_fit = ph[win], f_det[win]

    # Mittelwerte in 2-Minuten-Intervallen der Phase: einige hundert statt zehntausende Punkte
    BIN_D = 2 / 1440
    edges_fit = np.arange(-2.5 * T14, 2.5 * T14 + BIN_D, BIN_D)
    ib = np.digitize(t_fit, edges_fit) - 1
    nbins = len(edges_fit) - 1
    n_in = np.bincount(ib, minlength=nbins)[:nbins]
    s1 = np.bincount(ib, weights=f_fit, minlength=nbins)[:nbins]
    s2 = np.bincount(ib, weights=f_fit ** 2, minlength=nbins)[:nbins]
    ok = n_in >= 3
    tb = (0.5 * (edges_fit[1:] + edges_fit[:-1]))[ok]
    fb = s1[ok] / n_in[ok]
    eb = np.sqrt(np.maximum(s2[ok] / n_in[ok] - fb ** 2, 1e-12) / (n_in[ok] - 1))    # Standardfehler des Mittelwerts
    EXPTIME_D = FIT_EXPTIME / 86400
    N_SUB = 1 if FIT_EXPTIME <= 120 else 7                    # Mittelung über die Belichtung nur bei Langzeitkadenz nötig

    model = lambda t, dt0, p, a_rs, b, q1, q2: transit_model(t, dt0, p, a_rs, b, q1, q2, P_d, EXPTIME_D, N_SUB)
    bounds = ([-0.02, 0.01, 1.5, 0.0, 0.0, 0.0], [0.02, 0.5, 50.0, 1.2, 1.0, 1.0])
    # Mehrere Starts in b; a/R* passend zur Dauer, T14 ≈ P/π · sqrt((1+p)² − b²) / (a/R*)
    p_start = np.sqrt(max(depth_bls, 1e-5))
    best = None
    for b_start in [0.1, 0.4, 0.6, 0.8]:
        a_start = np.clip(P_d / (np.pi * T14_guess) * np.sqrt((1 + p_start) ** 2 - b_start ** 2), 2, 40)
        try:
            popt_i, pcov_i = curve_fit(model, tb, fb, p0=[0.0, p_start, a_start, b_start, 0.36, 0.3], sigma=eb,
                                       absolute_sigma=True, bounds=bounds, maxfev=20000)
        except RuntimeError:
            continue
        chi2_i = np.sum(((fb - model(tb, *popt_i)) / eb) ** 2)
        print(f"  Start b = {b_start:.1f}:  χ² = {chi2_i:8.1f},  b = {popt_i[3]:.3f},  Rp/R* = {popt_i[1]:.4f}")
        if best is None or chi2_i < best[0]:
            best = (chi2_i, popt_i, pcov_i)
    _, popt, pcov = best
    perr = np.sqrt(np.diag(pcov))
    dt0_fit, p_fit, a_fit, b_fit, q1_fit, q2_fit = popt
    inc_fit = np.degrees(np.arccos(b_fit / a_fit))
    chi2_red = np.sum(((fb - model(tb, *popt)) / eb) ** 2) / (len(tb) - len(popt))
    T14_fit = P_d / np.pi * np.arcsin(np.sqrt((1 + p_fit) ** 2 - b_fit ** 2) / (a_fit * np.sin(np.radians(inc_fit))))
    rho_fit = 3 * np.pi * a_fit ** 3 / (G_CGS * (P_d * 86400) ** 2)      # Sterndichte aus Keplers drittem Gesetz
    rho_err = rho_fit * 3 * perr[2] / a_fit

    # Darstellung: alle Belichtungen, 60 Mittelwerte, Modell und BLS-Kasten
    tt = np.linspace(-2.5 * T14, 2.5 * T14, 800)
    edges = np.linspace(-2.5 * T14, 2.5 * T14, 61)
    idx = np.digitize(t_fit, edges) - 1
    t_bin = 0.5 * (edges[1:] + edges[:-1])
    f_bin = np.array([np.mean(f_fit[idx == i]) if np.any(idx == i) else np.nan for i in range(60)])
    e_bin = np.array([np.std(f_fit[idx == i]) / np.sqrt(max((idx == i).sum(), 1)) for i in range(60)])

    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    sub = np.random.default_rng(0).choice(len(t_fit), min(len(t_fit), 20000), replace=False)
    axes[0].plot(t_fit[sub] * 24, f_fit[sub], ".", ms=1, c="lightgrey",
                 label=f"Belichtungen ({n_files} Dateien, {int(np.ptp(t_all) / P_d)} Umläufe)")
    axes[0].errorbar(t_bin * 24, f_bin, e_bin, fmt="o", c="black", ms=3, label="gemittelt")
    axes[0].plot(tt * 24, model(tt, *popt), c="tab:red", lw=2, label=f"Transitmodell: Rp/R* = {p_fit:.4f}, b = {b_fit:.2f}")
    axes[0].plot(tt * 24, 1 - depth_bls * (np.abs(tt) < T14 / 2), c="tab:blue", lw=1, ls="--", label="BLS-Kasten")
    axes[0].set_ylabel("Relativer Fluss")
    axes[0].set_title(f"{s.planet}: Transitmodell ({FIT_EXPTIME:.0f} s Kadenz)")
    axes[0].legend(fontsize=8)
    axes[1].errorbar(tb * 24, (fb - model(tb, *popt)) * 1e6, eb * 1e6, fmt=".", c="grey", ms=2, label="2-min-Mittel")
    axes[1].axhline(0, color="tab:red", lw=1)
    axes[1].set_xlabel("Zeit seit Transitmitte [h]")
    axes[1].set_ylabel("Residuum [ppm]")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()

    u1_fit, u2_fit = 2 * np.sqrt(q1_fit) * q2_fit, np.sqrt(q1_fit) * (1 - 2 * q2_fit)
    print(f"Ephemeride:  P = {P_d:.5f} d,  T0 = {t0_d + dt0_fit:.4f} BKJD")
    print(f"Fit: reduziertes χ² = {chi2_red:.2f};  Randverdunkelung u1 = {u1_fit:.2f}, u2 = {u2_fit:.2f}")
    s.__dict__.update(P_d=P_d, p_fit=p_fit, perr=perr, depth_bls=depth_bls, a_fit=a_fit, b_fit=b_fit, inc_fit=inc_fit,
                      T14_fit=T14_fit, rho_fit=rho_fit, rho_err=rho_err)


def compare(s):
    """Eigene Messung gegen das NASA Exoplanet Archive."""
    cat, perr = s.cat, s.perr
    rho_mr = cat["st_mass"] * 1.989e33 / (4 / 3 * np.pi * (cat["st_rad"] * 6.957e10) ** 3)   # aus Katalog-M*, -R*
    rows = [
        ("Periode P [d]",               f"{s.P_d:.5f}",                               f"{cat['pl_orbper']:.5f}"),
        ("Radiusverhältnis Rp/R*",      f"{s.p_fit:.4f} ± {perr[1]:.4f}",             f"{cat['pl_ratror']:.4f}"),
        ("  (BLS-Kasten)",              f"{np.sqrt(s.depth_bls):.4f}",                ""),
        ("Skalierte Halbachse a/R*",    f"{s.a_fit:.2f} ± {perr[2]:.2f}",             f"{cat['pl_ratdor']:.2f}"),
        ("Stoßparameter b",             f"{s.b_fit:.3f} ± {perr[3]:.3f}",             f"{cat['pl_imppar']:.3f}"),
        ("Bahnneigung i [°]",           f"{s.inc_fit:.2f}",                           f"{cat['pl_orbincl']:.2f}"),
        ("Transitdauer T14 [h]",        f"{s.T14_fit * 24:.2f}",                      f"{cat['pl_trandur']:.2f}"),
        ("Planetenradius [R_Erde]",     f"{s.p_fit * cat['st_rad'] * 109.08:.2f}",   f"{cat['pl_rade']:.2f}"),
        ("Sterndichte ρ* [g/cm³]",      f"{s.rho_fit:.3f} ± {s.rho_err:.3f}",         f"{cat['st_dens']:.3f} (st_dens)"),
        ("  aus Katalog-M*, -R*",       "",                                           f"{rho_mr:.3f}"),
    ]
    print(f"{'Größe':<28}{'eigene Messung':<22}{'Katalog'}")
    print("-" * 68)
    for name, own, ref in rows:
        print(f"{name:<28}{own:<22}{ref}")
    print("\nFehler: nur statistisch, aus der Kovarianzmatrix des Fits. Der Planetenradius nutzt den Katalog-Sternradius "
          f"{cat['st_rad']:.2f} R_Sonne. Sonne zum Vergleich: ρ = 1.41 g/cm³.")
