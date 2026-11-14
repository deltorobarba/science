"""Photometrie einer Galaxie: die hellsten Galaxien aus SIMBAD, Bilder in sechs Bändern, Himmel und radiales Profil, Sérsic-Fit, Farbkarte, Bulge und Scheibe, Vergleich mit S4G.

Für galaxies.ipynb aus galaxies_photometry.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: brightest, target, band_images, composites, sky_profile, sersic_fit, color_map, bulge_and_disk, s4g.
Downloads und Cache: data/galaxies/ (`galdata.py`).
"""
import galdata                                        # zuerst: Cache-Ordner für astropy
import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from scipy.optimize import curve_fit
from scipy.special import gammaincinv, gamma as gamma_fn
from scipy.ndimage import gaussian_filter
from astropy import units as u
from astropy.coordinates import SkyCoord, Angle
from astroquery.simbad import Simbad
from astroquery.ipac.ned import Ned
from astroquery.skyview import SkyView
from astroquery.hips2fits import hips2fits
from astroquery.vizier import Vizier


def brightest():
    """1. Die hellsten Galaxien am Himmel (Zellen 5, 7 von galaxies_photometry.ipynb)."""
    global ASTRODATA, H0, MAX_VMAG, MIN_SIZE, SELECTED_GALAXY, cols, galaxies, query
    ASTRODATA = galdata.DATA


    SELECTED_GALAXY = "M 51"   # Name wie in der Tabelle unten, z. B. "M 81", "M 101", "M 104", "M 87"
    H0 = 70.0                  # Hubble-Konstante [km/s/Mpc]
    pd.set_option("display.width", 160)

    MAX_VMAG = 10.5   # nur Galaxien heller als V = 10.5
    MIN_SIZE = 3.0    # Durchmesser entlang der großen Achse mindestens 3 Bogenminuten

    query = f'''
SELECT b.main_id, d.label AS typ, b.morph_type, b.ra, b.dec,
       b.rvz_redshift, b.rvz_radvel, b.galdim_majaxis, b.galdim_minaxis, b.galdim_angle,
       f.B AS bmag, f.V AS vmag, f.K AS kmag
FROM basic AS b
JOIN allfluxes AS f ON f.oidref = b.oid
JOIN otypedef AS d ON d.otype = b.otype
WHERE d.path LIKE 'G%' AND b.otype NOT IN ('GrG', 'CGG', 'ClG', 'SCG', 'PCG')
  AND f.V < {MAX_VMAG} AND b.galdim_majaxis >= {MIN_SIZE}
ORDER BY vmag
'''
    galaxies = Simbad.query_tap(query).to_pandas()
    galaxies["main_id"] = galaxies["main_id"].str.replace(r"\s+", " ", regex=True)    # "M  51" -> "M 51"
    galaxies["b_v"] = galaxies["bmag"] - galaxies["vmag"]                             # Farbindex B - V
    galaxies = galaxies.drop_duplicates(subset="main_id").reset_index(drop=True)
    print(f"{len(galaxies)} Galaxien mit V < {MAX_VMAG} und Durchmesser >= {MIN_SIZE}' in SIMBAD")
    print("\nHäufigste Objekttypen:", galaxies["typ"].value_counts().head(6).to_dict())

    cols = {"main_id": "Name", "typ": "Typ", "morph_type": "Hubble-Typ", "vmag": "V", "b_v": "B-V",
            "galdim_majaxis": "Durchmesser [']", "rvz_radvel": "v [km/s]"}
    print("\nDie 15 hellsten:")
    print(galaxies.head(15)[list(cols)].rename(columns=cols).round(2).to_string(index=False))


def target():
    """3. Die ausgewählte Galaxie und ihre Entfernung (Zellen 10 von galaxies_photometry.ipynb)."""
    global M_V, a_arcmin, attempt, ax, b_arcmin, coord, d, d_hubble, dist, dist_mpc, e, error
    global fig, info, j, kpc_per_arcmin, m, match, methods, ned, order, pa_deg, rng, size_kpc
    global to_mpc, v_rec
    match = galaxies.loc[galaxies["main_id"] == SELECTED_GALAXY]
    if len(match) == 0:
        raise ValueError(f"'{SELECTED_GALAXY}' nicht gefunden; Schreibweise prüfen (Leerzeichen in 'M 51').")
    info = match.iloc[0]
    coord = SkyCoord(info["ra"], info["dec"], unit="deg")
    a_arcmin = info["galdim_majaxis"]                                          # Durchmesser große Achse [']
    b_arcmin = info["galdim_minaxis"] if pd.notna(info["galdim_minaxis"]) else a_arcmin
    pa_deg = float(info["galdim_angle"]) if pd.notna(info["galdim_angle"]) else 0.0   # von Norden über Osten

    # Entfernungen, die nicht aus der Rotverschiebung stammen (Cepheiden, TRGB, PNLF, Tully-Fisher, ...)
    dist = Simbad.query_tap(f'''
SELECT m.dist, m.unit, m.method, m.bibcode
FROM mesDistance AS m JOIN ident AS i ON i.oidref = m.oidref
WHERE i.id = '{SELECTED_GALAXY}'
''').to_pandas()
    to_mpc = {"Mpc": 1.0, "kpc": 1e-3, "pc": 1e-6}
    dist["dist_mpc"] = dist["dist"] * dist["unit"].str.strip().map(to_mpc)
    dist = dist[dist["method"].str.strip() != "redshift"].dropna(subset=["dist_mpc"])
    dist_mpc = dist["dist_mpc"].median()

    # Fluchtgeschwindigkeit aus NED
    ned, v_rec = None, info["rvz_radvel"]
    for attempt in range(2):                                      # NED antwortet manchmal langsam
        try:
            ned = Ned.query_object(SELECTED_GALAXY).to_pandas().iloc[0]
            v_rec = float(ned["Velocity"])
            break
        except Exception as e:
            error = e
    if ned is None:
        print(f"NED-Abfrage fehlgeschlagen ({error}); nehme die Geschwindigkeit aus SIMBAD")

    kpc_per_arcmin = dist_mpc * 1e3 * np.deg2rad(1 / 60)
    size_kpc = a_arcmin * kpc_per_arcmin
    M_V = info["vmag"] - 5 * np.log10(dist_mpc * 1e6 / 10)
    d_hubble = v_rec / H0

    print(f"Galaxie:               {SELECTED_GALAXY}" + (f"   (NED: {ned['Object Name']}, Typ {ned['Type']})" if ned is not None else ""))
    print(f"Objekttyp:             {info['typ']}   |   Hubble-Typ: {info['morph_type']}")
    print(f"Koordinaten:           {coord.to_string('hmsdms', precision=1)}")
    print(f"Helligkeit:            V = {info['vmag']:.2f}   B-V = {info['b_v']:.2f}   K = {info['kmag']:.2f}")
    print(f"Scheinbare Größe:      {a_arcmin:.1f}' x {b_arcmin:.1f}'   (PA {pa_deg:.0f}°)")
    print(f"Fluchtgeschwindigkeit: {v_rec:.0f} km/s (NED; SIMBAD: {info['rvz_radvel']:.0f} km/s)")
    print(f"Entfernung:            {dist_mpc:.2f} Mpc = {dist_mpc * 3.26156:.1f} Millionen Lichtjahre "
          f"(Median aus {len(dist)} Messungen ohne Rotverschiebung)")
    print(f"Maßstab:               1' = {kpc_per_arcmin:.2f} kpc")
    print(f"Durchmesser:           {size_kpc:.1f} kpc = {size_kpc * 3261.56:,.0f} Lichtjahre")
    print(f"Absolute Helligkeit:   M_V = {M_V:.2f}")
    print(f"\nHubble-Gesetz: v/H0 = {d_hubble:.2f} Mpc gegen die Entfernungsleiter {dist_mpc:.2f} Mpc")
    print(f"Eigenbewegung: v - H0·D = {v_rec - H0 * dist_mpc:+.0f} km/s")

    if len(dist):
        rng = np.random.default_rng(0)
        methods = dist["method"].str.strip().str.upper().replace("", "ohne Angabe")
        order = methods.value_counts().index
        fig, ax = plt.subplots(figsize=(10, 0.45 * len(order) + 1.6))
        for j, m in enumerate(order):
            d = dist.loc[methods == m, "dist_mpc"]
            ax.scatter(d, j + rng.uniform(-0.15, 0.15, len(d)), s=18, alpha=0.7)
        ax.axvline(dist_mpc, color="black", ls="--", label=f"Median {dist_mpc:.2f} Mpc")
        if d_hubble > 0:
            ax.axvline(d_hubble, color="tab:red", ls=":", label=f"Hubble-Gesetz {d_hubble:.2f} Mpc")
        ax.set_yticks(range(len(order)), [f"{m} ({(methods == m).sum()})" for m in order])
        ax.set_xlabel("Entfernung [Mpc]")
        ax.set_title(f"{SELECTED_GALAXY}: veröffentlichte Entfernungen nach Methode (SIMBAD)")
        ax.legend(fontsize=8)
        fig.tight_layout()
        plt.show()


def band_images():
    """4. Bilder in sechs Wellenlängenbereichen (Zellen 13 von galaxies_photometry.ipynb)."""
    global FOV_FACTOR, PIXELS, SURVEYS, ax, axes, catalog_ellipse, data, extent, fig, fov, half, hdul
    global hdus, images, img, name, ncol, nrow, pix_arcmin, stretch
    SURVEYS = {
        "GALEX Near UV": "UV 0.23 µm: junge, massereiche Sterne",
        "DSS2 Blue":     "optisch 0.47 µm: blaue Sterne, Staubbänder",
        "DSS2 Red":      "optisch 0.65 µm: Sternlicht",
        "2MASS-K":       "nahes IR 2.2 µm: alte Sterne",
        "WISE 3.4":      "IR 3.4 µm: Sternmasse",
        "WISE 12":       "IR 12 µm: warmer Staub, Sternentstehung",
    }
    FOV_FACTOR = 1.6    # Bildfeld = 1.6 x Durchmesser
    PIXELS = 400

    fov = FOV_FACTOR * a_arcmin * u.arcmin
    print(f"Lade {len(SURVEYS)} Bilder, {PIXELS}x{PIXELS} Pixel, Feld {fov:.1f} ...")
    hdus = SkyView.get_images(position=coord, survey=list(SURVEYS), pixels=PIXELS, width=fov, height=fov)
    images = {}
    for name, hdul in zip(SURVEYS, hdus):
        data = hdul[0].data.astype(float)
        if np.nanmax(data) == np.nanmin(data):
            print(f"   {name:14s} keine Abdeckung")
            continue
        images[name] = data
        print(f"   {name:14s} {data.shape}")

    pix_arcmin = abs(hdus[0][0].header["CDELT1"]) * 60                  # Bogenminuten pro Pixel
    half = PIXELS / 2 * pix_arcmin
    extent = [half, -half, -half, half]                                  # Osten links, Norden oben
    print(f"Pixelgröße {pix_arcmin * 60:.2f}\"")

    def stretch(img, lo=1, hi=99.8):
        # Asinh-Streckung zwischen zwei Perzentilen (wie in ds9 oder Aladin)
        vmin, vmax = np.nanpercentile(img, [lo, hi])
        x = np.clip((img - vmin) / (vmax - vmin), 0, 1)
        return np.arcsinh(10 * x) / np.arcsinh(10)

    def catalog_ellipse(color="white"):
        return Ellipse((0, 0), width=b_arcmin, height=a_arcmin, angle=-pa_deg, fill=False, ec=color, ls="--", lw=0.8)

    ncol = 3
    nrow = int(np.ceil(len(images) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(13, 4.4 * nrow))
    for ax, (name, img) in zip(axes.flat, images.items()):
        ax.imshow(stretch(img), origin="lower", cmap="inferno", extent=extent)
        ax.add_patch(catalog_ellipse())
        ax.set_title(f"{name}\n{SURVEYS[name]}", fontsize=9)
        ax.set_xlabel("ΔRA [']")
        ax.set_ylabel("ΔDec [']")
    for ax in list(axes.flat)[len(images):]:
        ax.axis("off")
    fig.suptitle(f"{SELECTED_GALAXY} in sechs Bändern (gestrichelt: Größe laut SIMBAD)", y=1.0)
    fig.tight_layout()
    plt.show()


def composites():
    """5. Bilder in sechs Wellenlängenbereichen (Zellen 16 von galaxies_photometry.ipynb)."""
    global CHANNELS, HIPS, available, ax, axes, fig, optical, rgb
    HIPS = "CDS/P/DSS2/color"   # Alternativen: "CDS/P/PanSTARRS/DR1/color-z-zg-g" (Dec > -30°), "CDS/P/SDSS9/color"
    optical = hips2fits.query(hips=HIPS, width=PIXELS, height=PIXELS, ra=Angle(info["ra"] * u.deg),
                              dec=Angle(info["dec"] * u.deg), fov=Angle(fov), projection="TAN", format="jpg")

    CHANNELS = ["WISE 12", "WISE 3.4", "GALEX Near UV"]
    available = [c for c in CHANNELS if c in images]
    if len(available) < 3:                       # ohne GALEX: DSS2 Blue als blauer Kanal
        available = [c for c in ["WISE 12", "WISE 3.4", "DSS2 Blue"] if c in images]
    rgb = np.dstack([stretch(images[c], lo=50, hi=99.8) for c in available])   # lo=50: Himmel wird schwarz

    fig, axes = plt.subplots(1, 2, figsize=(13, 6.5))
    axes[0].imshow(optical, extent=extent)       # die Zeilen des JPG laufen von Norden nach Süden
    axes[0].set_title(f"{SELECTED_GALAXY}: Farbbild ({HIPS.split('/')[2]})")
    axes[1].imshow(rgb, origin="lower", extent=extent)
    axes[1].set_title(f"Falschfarben  R: {available[0]}  G: {available[1]}  B: {available[2]}", fontsize=10)
    for ax in axes:
        ax.add_patch(catalog_ellipse())
        ax.set_xlabel("ΔRA [']")
        ax.set_ylabel("ΔDec [']")
    fig.tight_layout()
    plt.show()


def sky_profile():
    """8. Himmelshintergrund und radiales Profil (Zellen 19 von galaxies_photometry.ipynb)."""
    global BAND, N_BINS, a_cat, axes, col, dx, dy, edges, f, fig, img, nx
    global ny, pa, prof, q, r_ell, r_mid, raw, ring_median, robust_std, sky, sky_noise, sky_region
    global x_a, x_b, xx, yy
    BAND = "WISE 3.4"
    N_BINS = 40

    img = images[BAND]
    ny, nx = img.shape
    yy, xx = np.mgrid[:ny, :nx]
    dx = -(xx - (nx - 1) / 2) * pix_arcmin            # Bogenminuten, Osten positiv
    dy = (yy - (ny - 1) / 2) * pix_arcmin             # Bogenminuten, Norden positiv

    # Elliptischer Radius
    pa = np.deg2rad(pa_deg)
    q = b_arcmin / a_arcmin
    x_a = dx * np.sin(pa) + dy * np.cos(pa)
    x_b = dx * np.cos(pa) - dy * np.sin(pa)
    r_ell = np.hypot(x_a, x_b / q)                    # Radius entlang der großen Halbachse [']

    a_cat = a_arcmin / 2                               # große Halbachse laut Katalog
    def robust_std(x):
        # Streuung aus der mittleren absoluten Abweichung; Sterne im Feld blähen die Standardabweichung auf
        x = x[np.isfinite(x)]
        return 1.4826 * np.median(np.abs(x - np.median(x)))

    sky_region = r_ell > 1.1 * a_cat
    sky = np.nanmedian(img[sky_region])
    sky_noise = robust_std(img[sky_region])

    def ring_median(image, r, edges):
        # Median in elliptischen Ringen; NaN, wo ein Ring keine gültigen Pixel hat
        out = np.full(len(edges) - 1, np.nan)
        for k, (lo, hi) in enumerate(zip(edges[:-1], edges[1:])):
            v = image[(r >= lo) & (r < hi)]
            v = v[np.isfinite(v)]
            if v.size:
                out[k] = np.median(v)
        return out

    edges = np.linspace(0, 1.3 * a_cat, N_BINS + 1)
    r_mid = 0.5 * (edges[1:] + edges[:-1])
    raw = ring_median(img, r_ell, edges)
    prof = raw - sky

    print(f"Himmel (Median außerhalb 1.1 a): {sky:.3f}, robuste Streuung {sky_noise:.3f}  [{BAND}-Einheiten]")
    print(f"Profil: {N_BINS} Ringe bis {edges[-1]:.2f}'; Achsenverhältnis q = {q:.2f}, PA = {pa_deg:.0f}°")
    print(f"Zentrum {raw[0]:.1f}, bei a: {np.interp(a_cat, r_mid, raw):.2f}; Profil fällt unter 3 σ des Himmels bei "
          f"{r_mid[np.argmax(prof < 3 * sky_noise)]:.2f}'")

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    axes[0].imshow(stretch(img), origin="lower", cmap="inferno", extent=extent)
    for f, col in [(0.05, "cyan"), (0.5, "cyan"), (0.9, "cyan"), (1.1, "white")]:
        axes[0].add_patch(Ellipse((0, 0), 2 * f * a_cat * q, 2 * f * a_cat, angle=-pa_deg, fill=False, ec=col, lw=0.8))
    axes[0].set_title(f"{BAND}: Ellipsen bei 0.05, 0.5, 0.9 a (weiß: Beginn des Himmels)", fontsize=10)
    axes[0].set_xlabel("ΔRA [']")
    axes[0].set_ylabel("ΔDec [']")
    axes[1].semilogy(r_mid, raw, "o", c="black", ms=4, label="Median im Ring (roh)")
    axes[1].axhline(sky, color="tab:blue", ls="--", label=f"Himmel {sky:.2f}")
    axes[1].axhspan(sky - sky_noise, sky + sky_noise, color="tab:blue", alpha=0.15, label="Himmel ± 1 σ")
    axes[1].axvline(a_cat, color="grey", ls=":", label="große Halbachse laut SIMBAD")
    axes[1].set_xlabel("Radius entlang der großen Halbachse [']")
    axes[1].set_ylabel(f"Flächenhelligkeit [{BAND}-Einheiten]")
    axes[1].set_title("Rohes Profil und Himmelshintergrund", fontsize=10)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()


def sersic_fit():
    """9. Das Sérsic-Profil (Zellen 22 von galaxies_photometry.ipynb)."""
    global I_e, R_FIT, axes, fig, h_single, kind, n, n_err, p0, pcov, popt, r_e
    global r_plot, re_err, resid_single, sel, sersic
    R_FIT = (0.05, 0.9)   # Fitbereich in Einheiten der großen Halbachse

    def sersic(r, I_e, r_e, n):
        b_n = gammaincinv(2 * n, 0.5)
        return I_e * np.exp(-b_n * ((r / r_e) ** (1 / n) - 1))

    sel = (r_mid > R_FIT[0] * a_cat) & (r_mid < R_FIT[1] * a_cat) & (prof > 0)
    p0 = [np.log(max(np.interp(a_cat / 3, r_mid, prof), 1e-6)), a_cat / 3, 2.0]
    popt, pcov = curve_fit(lambda r, lnI, r_e, n: np.log(sersic(r, np.exp(lnI), r_e, n)),
                           r_mid[sel], np.log(prof[sel]), p0=p0, bounds=([-np.inf, 0.01, 0.3], [np.inf, 5 * a_cat, 10]))
    I_e, r_e, n = np.exp(popt[0]), popt[1], popt[2]
    n_err, re_err = np.sqrt(pcov[2, 2]), np.sqrt(pcov[1, 1])
    resid_single = np.log(prof[sel]) - np.log(sersic(r_mid[sel], I_e, r_e, n))

    kind = ("scheibendominiert (Spirale, S0)" if n < 2 else
            "Übergang (Bulge und Scheibe)" if n < 2.5 else "sphäroiddominiert (elliptisch, klassischer Bulge)")
    print(f"Sérsic-Fit in {BAND} an {sel.sum()} Ringe")
    print(f"  Sérsic-Index:     n = {n:.2f} ± {n_err:.2f}   ->  {kind}")
    print(f"  Hubble-Typ:       {info['morph_type']}  (SIMBAD)")
    print(f"  Effektivradius:   r_e = {r_e:.2f}' ± {re_err:.2f}' = {r_e * kpc_per_arcmin:.2f} kpc")
    if n < 2:
        h_single = r_e / gammaincinv(2, 0.5)          # für n = 1 ist r_e = 1.678 h
        print(f"  Skalenlänge:      h ≈ r_e/1.678 = {h_single:.2f}' = {h_single * kpc_per_arcmin:.2f} kpc  (Milchstraße etwa 2.6 kpc)")
    print(f"  Neigung:          q = {q:.2f}  ->  i = arccos q = {np.rad2deg(np.arccos(np.clip(q, 0, 1))):.0f}° (dünne Scheibe)")
    print(f"  Residuen:         rms in ln I = {np.sqrt(np.mean(resid_single ** 2)):.3f}")

    fig, axes = plt.subplots(2, 1, figsize=(9, 6.5), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    axes[0].semilogy(r_mid, np.where(prof > 0, prof, np.nan), "o", c="grey", ms=4, label="Profil minus Himmel")
    axes[0].semilogy(r_mid[sel], prof[sel], "o", c="tab:green", ms=4, label="Fitbereich")
    r_plot = np.linspace(r_mid[0], r_mid[-1], 300)
    axes[0].semilogy(r_plot, sersic(r_plot, I_e, r_e, n), c="tab:red", lw=2, label=f"Sérsic, n = {n:.2f}")
    axes[0].axvline(r_e, color="tab:red", ls="--", lw=1, label=f"r_e = {r_e:.2f}'")
    axes[0].set_ylabel(f"Flächenhelligkeit [{BAND}-Einheiten]")
    axes[0].set_title(f"{SELECTED_GALAXY}: radiales Profil und Sérsic-Fit")
    axes[0].legend(fontsize=8)
    axes[1].plot(r_mid[sel], resid_single, "o-", c="tab:green", ms=3)
    axes[1].axhline(0, color="black", lw=0.8)
    axes[1].set_xlabel("Radius entlang der großen Halbachse [']")
    axes[1].set_ylabel("ln(Daten/Modell)")
    fig.tight_layout()
    plt.show()


def color_map():
    """10. Die Farbkarte (Zellen 25 von galaxies_photometry.ipynb)."""
    global axes, c_prof, colour, colour_ok, covered, det, fig, im, in_ring, inner, nuv, nuv_n
    global nuv_sky, outer, w1, w1_n, w1_sky
    colour_ok = "GALEX Near UV" in images and "WISE 3.4" in images
    if not colour_ok:
        print("Kein GALEX-Bild für diese Galaxie; die Farbkarte entfällt.")
    else:
        nuv = gaussian_filter(images["GALEX Near UV"], 2)       # auf ähnliche Auflösung glätten
        w1 = gaussian_filter(images["WISE 3.4"], 2)
        nuv_sky, w1_sky = np.nanmedian(nuv[sky_region]), np.nanmedian(w1[sky_region])
        nuv_n, w1_n = robust_std(nuv[sky_region]), robust_std(w1[sky_region])
        det = ((nuv - nuv_sky) > 3 * nuv_n) & ((w1 - w1_sky) > 3 * w1_n) & (r_ell < a_cat)
        colour = np.full(img.shape, np.nan)
        colour[det] = -2.5 * np.log10((nuv - nuv_sky)[det] / (w1 - w1_sky)[det])
        colour -= np.nanmedian(colour)                                              # nur relativ
        c_prof = ring_median(colour, r_ell, edges)
        in_ring = np.digitize(r_ell, edges) - 1
        covered = np.array([det[in_ring == k].mean() if (in_ring == k).any() else 0 for k in range(len(r_mid))])
        c_prof[covered < 0.5] = np.nan                                              # Ringe, die nur zum Teil gemessen sind
        inner = np.nanmedian(c_prof[r_mid < 0.1 * a_cat])                          # Zentrum (Bulge)
        outer = np.nanmedian(c_prof[(r_mid > 0.3 * a_cat) & (r_mid < 0.7 * a_cat)])  # Scheibe, ohne den Rand
        print(f"Pixel mit beiden Bändern über 3 σ: {det.sum()}")
        print(f"NUV - W1 im Zentrum (r < 0.1 a): {inner:+.2f} mag, in der Scheibe (0.3-0.7 a): {outer:+.2f} mag")
        print(f"Die Scheibe ist um {inner - outer:.2f} mag blauer als das Zentrum")

        fig, axes = plt.subplots(1, 2, figsize=(13, 5))
        im = axes[0].imshow(colour, origin="lower", cmap="RdYlBu_r", extent=extent, vmin=-1.5, vmax=1.5)
        axes[0].add_patch(catalog_ellipse("black"))
        fig.colorbar(im, ax=axes[0], label="relatives NUV − W1 [mag] (blau = junge Sterne)")
        axes[0].set_title(f"{SELECTED_GALAXY}: Farbkarte", fontsize=10)
        axes[0].set_xlabel("ΔRA [']")
        axes[0].set_ylabel("ΔDec [']")
        axes[1].plot(r_mid * kpc_per_arcmin, c_prof, "o-", c="tab:purple")
        axes[1].invert_yaxis()
        axes[1].set_xlabel("Radius [kpc]")
        axes[1].set_ylabel("relatives NUV − W1 [mag] (oben = blauer)")
        axes[1].set_title("Farbprofil: Sternentstehung gegen Radius", fontsize=10)
        fig.tight_layout()
        plt.show()


def bulge_and_disk():
    """11. Bulge und Scheibe (Zellen 28 von galaxies_photometry.ipynb)."""
    global BT, L_bulge, L_disk, PSF_ARCMIN, _, at_bound, ax, b_nb, bd_bounds, bulge_disk, fig, h_d
    global lnI0_d, lnIe_b, n_b, p0_bd, p_bd, re_b, rms_double, rms_single, rp, sel2
    PSF_ARCMIN = 0.2      # WISE 3.4 µm löst etwa 6" auf, die SkyView-Pixel sind etwa 2"

    def bulge_disk(r, lnIe, r_e_b, n_b, lnI0, h):
        return sersic(r, np.exp(lnIe), r_e_b, n_b) + np.exp(lnI0) * np.exp(-r / h)

    sel2 = (r_mid > PSF_ARCMIN) & (r_mid < R_FIT[1] * a_cat) & (prof > 0)
    p0_bd = [np.log(prof[sel2][0]), 0.1 * a_cat, 2.0, np.log(prof[sel2][len(prof[sel2]) // 3]), 0.3 * a_cat]
    bd_bounds = ([-np.inf, 0.01, 0.5, -np.inf, 0.02], [np.inf, 0.5 * a_cat, 8.0, np.inf, 2 * a_cat])
    p_bd, _ = curve_fit(lambda r, *p: np.log(bulge_disk(r, *p)), r_mid[sel2], np.log(prof[sel2]),
                        p0=p0_bd, bounds=bd_bounds, maxfev=20000)
    lnIe_b, re_b, n_b, lnI0_d, h_d = p_bd

    # Gesamtlicht der Komponenten
    b_nb = gammaincinv(2 * n_b, 0.5)
    L_bulge = 2 * np.pi * q * n_b * np.exp(lnIe_b) * re_b ** 2 * np.exp(b_nb) * gamma_fn(2 * n_b) / b_nb ** (2 * n_b)
    L_disk = 2 * np.pi * q * np.exp(lnI0_d) * h_d ** 2
    BT = L_bulge / (L_bulge + L_disk)
    rms_single = np.sqrt(np.mean((np.log(prof[sel2]) - np.log(sersic(r_mid[sel2], I_e, r_e, n))) ** 2))
    rms_double = np.sqrt(np.mean((np.log(prof[sel2]) - np.log(bulge_disk(r_mid[sel2], *p_bd))) ** 2))

    at_bound = n_b < 0.55 or n_b > 7.9
    print(f"Bulge und Scheibe in {BAND} (Radien {PSF_ARCMIN}' bis {R_FIT[1] * a_cat:.1f}')")
    print(f"  Bulge:   n = {n_b:.2f}, r_e = {re_b:.2f}' = {re_b * kpc_per_arcmin:.2f} kpc"
          + ("   (n an der Grenze des Fits: Bulge kaum aufgelöst)" if at_bound else ""))
    print(f"  Scheibe: h = {h_d:.2f}' = {h_d * kpc_per_arcmin:.2f} kpc")
    print(f"  B/T = {BT:.2f}   (Hubble-Typ {info['morph_type']})")
    print(f"  Residuen (rms in ln I): ein Sérsic-Profil {rms_single:.3f}  ->  Bulge und Scheibe {rms_double:.3f}")

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.semilogy(r_mid, np.where(prof > 0, prof, np.nan), "o", c="grey", ms=4, label="Profil minus Himmel")
    ax.semilogy(r_mid[sel2], prof[sel2], "o", c="tab:green", ms=4, label="Fitbereich")
    rp = np.linspace(0.01, r_mid[-1], 300)
    ax.semilogy(rp, sersic(rp, np.exp(lnIe_b), re_b, n_b), c="tab:red", ls="--",
                label=f"Bulge: n = {n_b:.1f}, r_e = {re_b * kpc_per_arcmin:.2f} kpc")
    ax.semilogy(rp, np.exp(lnI0_d) * np.exp(-rp / h_d), c="tab:blue", ls="--", label=f"Scheibe: h = {h_d * kpc_per_arcmin:.2f} kpc")
    ax.semilogy(rp, bulge_disk(rp, *p_bd), c="black", lw=2, label=f"Bulge + Scheibe, B/T = {BT:.2f}")
    ax.semilogy(rp, sersic(rp, I_e, r_e, n), c="orange", lw=1, ls=":", label=f"ein Sérsic-Profil, n = {n:.2f}")
    ax.axvspan(0, PSF_ARCMIN, color="grey", alpha=0.15, label="nicht aufgelöst")
    ax.set_ylim(np.nanmin(prof[prof > 0]) * 0.5, np.nanmax(prof) * 2)
    ax.set_xlabel("Radius entlang der großen Halbachse [']")
    ax.set_ylabel(f"Flächenhelligkeit [{BAND}-Einheiten]")
    ax.set_title(f"{SELECTED_GALAXY}: Zerlegung in Bulge und Scheibe")
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()


def s4g():
    """12. Vergleich mit der S4G-Zerlegung (Zellen 31 von galaxies_photometry.ipynb)."""
    global _, bul, comps, disk, h_s4, hit, p_all, rows, s4, sel_all, table, viz
    viz = Vizier(columns=["**"], row_limit=-1)
    hit = viz.query_region(coord, radius=1 * u.arcmin, catalog="J/ApJS/219/4/galaxies")
    if len(hit) == 0:
        print(f"{SELECTED_GALAXY} ist nicht in S4G (nur Galaxien näher als 40 Mpc mit HI-Geschwindigkeit, "
              "elliptische Galaxien fehlen meist)")
    else:
        s4 = hit[0].to_pandas()
        s4 = s4.iloc[[np.argmin(coord.separation(SkyCoord(s4["_RA"], s4["_DE"], unit="deg")).arcsec)]].iloc[0]
        comps = viz.query_constraints(catalog="J/ApJS/219/4/table7", Name=s4["Name"])[0].to_pandas()
        bul = comps[(comps["C"].str.strip() == "B") & (comps["Fn"].str.strip() == "sersic")]
        disk = comps[comps["Fn"].str.strip().isin(["expdisk", "edgedisk"])]
        h_s4 = (disk["hr3"].fillna(disk["hr2"]).iloc[0] / 60) if len(disk) else np.nan
        print(f"S4G: {s4['Name']}, Modell '{comps['Mod'].iloc[0].strip()}' mit den Komponenten "
              f"{', '.join(comps['C'].str.strip() + ' (' + comps['Fn'].str.strip() + ')')}, Qualität {comps['Q'].iloc[0]}")

        # Ein Sérsic-Profil über den ganzen Radius, wie bei S4G ohne inneren Schnitt
        sel_all = (r_mid < R_FIT[1] * a_cat) & (prof > 0)
        p_all, _ = curve_fit(lambda r, lnI, r_e, n: np.log(sersic(r, np.exp(lnI), r_e, n)), r_mid[sel_all],
                             np.log(prof[sel_all]), p0=p0, bounds=([-np.inf, 0.01, 0.3], [np.inf, 5 * a_cat, 10]))

        rows = [("ein Sérsic-Profil: n", f"{n:.2f}", f"{p_all[2]:.2f}", f"{s4['n']:.2f}"),
                ("ein Sérsic-Profil: r_e [']", f"{r_e:.2f}", f"{p_all[1]:.2f}", f"{s4['Re'] / 60:.2f}"),
                ("Achsenverhältnis q", f"{q:.2f} (SIMBAD)", "", f"{s4['q']:.2f}"),
                ("B/T", f"{BT:.2f}", "", f"{bul['f1'].iloc[0]:.2f}" if len(bul) else "0 (kein Bulge)"),
                ("Bulge: n", f"{n_b:.2f}", "", f"{bul['n'].iloc[0]:.2f}" if len(bul) else "-"),
                ("Bulge: r_e [']", f"{re_b:.2f}", "", f"{bul['Re'].iloc[0] / 60:.2f}" if len(bul) else "-"),
                ("Scheibe: h [']", f"{h_d:.2f}", "", f"{h_s4:.2f}"),
                ("Scheibe: h [kpc]", f"{h_d * kpc_per_arcmin:.2f}", "", f"{h_s4 * kpc_per_arcmin:.2f}")]
        table = pd.DataFrame(rows, columns=["Größe", "eigen (0.05-0.9 a)", "eigen (0-0.9 a)", "S4G"])
        print(f"\nEntfernung für beide: {dist_mpc:.2f} Mpc\n")
        print(table.to_string(index=False))
