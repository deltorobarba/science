"""Der Krebsnebel: Fotoplatten aus 60 Jahren, Astrometrie gegen Gaia, Expansion der Filamente, Expansionszentrum und Konvergenzjahr, Entfernung, Bremsen des Pulsars und Energiebilanz.

Für nebulae.ipynb aus nebulae_crab.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, photos, filaments, gaia_frame, epoch_astrometry, common_grid, displacements, expansion_center, hubble_diagram, three_epochs, distance, pulsar, braking_index, literature, energy.
Downloads und Cache: data/nebulae/ (`nebdata.py`).
"""
import nebdata                                         # zuerst: Cache-Ordner für astropy
import calendar
import datetime
import os
import re
import urllib.parse
import urllib.request
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numpy.lib.stride_tricks import sliding_window_view
from scipy import ndimage, optimize, spatial
from astropy.io import fits
from astropy.time import Time
from astropy.wcs import WCS, FITSFixedWarning


def load():
    """Daten (Zellen 12 von nebulae_crab.ipynb)."""
    global ASTRODATA, CRAB, DE0, ESO, FWHM_COMMON, HALF, HP_SIGMA, I_NS, JB_FILES, M_FIL, M_SUN, PATCH
    global PEAK_MIN, PLATE_FILES, PS1, PSR, PSR_ID, RA0, SEARCH, STEP, STSCI, T_SN, V_R_MAX, YEAR
    global download, fits_ok, gaia, load_plate, plate_epoch, ps1_mosaic, ps1_part, rng, tap
    ASTRODATA = nebdata.DATA


    warnings.simplefilter("ignore", FITSFixedWarning)     # die DSS-Köpfe enthalten veraltete Schlüsselwörter
    RA0, DE0 = 83.63308, 22.01450      # Bezugspunkt aller Bilder: Crab-Pulsar (ICRS, gerundet)
    HALF = 360                         # halbe Kantenlänge des gemeinsamen Rasters [″], 1″ pro Pixel (Schritt 61)
    FWHM_COMMON = 4.4                  # gemeinsame Bildschärfe nach dem Angleichen [″] (Schritt 61)
    HP_SIGMA = 6.0                     # Breite des Hochpasses [″]: Strukturen größer als das werden entfernt
    PATCH, SEARCH, STEP = 10, 20, 8    # halbe Ausschnittgröße, Suchradius und Abstand der Ausschnitte [″] (Schritt 62)
    PEAK_MIN = 0.6                     # Mindestkorrelation, ab der eine Verschiebung zählt
    T_SN = 1054.5                      # Supernova: erstmals gesehen am 4. Juli 1054
    I_NS = 1e45                        # Trägheitsmoment des Neutronensterns [g cm²]
    V_R_MAX = 1500.0                   # größte Radialgeschwindigkeit der Filamente [km/s] (Martin et al. 2021)
    M_FIL = (4.6, 1.8)                 # Masse der Filamente und Fehler [Sonnenmassen] (Fesen et al. 1997)
    YEAR = 365.25 * 86400              # Sekunden pro Jahr
    M_SUN = 1.989e33                   # Sonnenmasse [g]
    CRAB = ASTRODATA / "crab"
    rng = np.random.default_rng(42)
    pd.set_option("display.width", 160)


    def download(urls, path, check=None):
        # lädt eine Datei vom ersten Server, der antwortet, und liest sie danach aus dem Cache
        path = Path(path)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            for url in urls:
                try:
                    with urllib.request.urlopen(url, timeout=120) as r:
                        data = r.read()
                except OSError:
                    continue
                if check is None or check(data):
                    path.write_bytes(data)
                    break
            else:
                raise OSError(f"Kein Server liefert {path.name}")
        return path


    fits_ok = lambda d: d[:6] == b"SIMPLE"


    def tap(adql, path):
        # Gaia DR3 über TAP: erst ESA, dann GAVO in Heidelberg (dort heißt die Tabelle gaia.dr3lite)
        services = [("https://gea.esac.esa.int/tap-server/tap/sync", "gaiadr3.gaia_source"),
                    ("https://dc.zah.uni-heidelberg.de/tap/sync", "gaia.dr3lite")]
        urls = [s + "?" + urllib.parse.urlencode({"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv",
                                                  "QUERY": adql.format(table=t)}) for s, t in services]
        return pd.read_csv(download(urls, path, check=lambda d: d.startswith(b"source_id")))


    def plate_epoch(h):
        # Datum der Belichtung als Dezimaljahr; die Server schreiben 1951-11-07, 1991/10/18 oder 08/11/51
        s = str(h["DATE-OBS"]).strip()
        m = re.match(r"(\d{4})[-/](\d{2})[-/](\d{2})", s)
        if m:
            y, mo, d = map(int, m.groups())
        else:
            d, mo, y = map(int, re.match(r"(\d{2})/(\d{2})/(\d{2})", s).groups())
            y += 1900
        day = (datetime.date(y, mo, d) - datetime.date(y, 1, 1)).days + 0.5
        return y + day / (366 if calendar.isleap(y) else 365)


    def load_plate(path):
        with fits.open(path) as h:
            h.verify("silentfix")                        # ESO schreibt eine Kopfzeile, die nicht dem Standard folgt
            return h[0].data.astype(float), h[0].header.copy()


    # Fotoplatten: POSS-I rot (1951) und POSS-II rot (1991), 12′ × 12′ um den Pulsar
    STSCI = "https://archive.stsci.edu/cgi-bin/dss_search?r={}&d={}&e=J2000&h=12&w=12&f=fits&c=none&v={}"
    ESO = "https://archive.eso.org/dss/dss/image?ra={}&dec={}&equinox=J2000&x=12&y=12&mime-type=application/x-fits&Sky-Survey={}"
    PLATE_FILES = {
        "POSS-I E": download([STSCI.format(RA0, DE0, "poss1_red"), ESO.format(RA0, DE0, "DSS1")], CRAB / "poss1_red.fits", fits_ok),
        "POSS-II F": download([ESO.format(RA0, DE0, "DSS2-red"), STSCI.format(RA0, DE0, "poss2ukstu_red")], CRAB / "poss2_red.fits", fits_ok),
    }

    # Pan-STARRS1: zwei Skycells pro Filter, 12′ × 12′, auf 0.5″ pro Pixel gemittelt
    PS1 = "https://ps1images.stsci.edu/cgi-bin/"


    def ps1_part(band, dec):
        # Skycell, die den Punkt (RA0, dec) enthält, ausgeschnitten um den Pulsar
        lst = download([f"{PS1}ps1filenames.py?ra={RA0}&dec={dec}&filters={band}"], CRAB / f"ps1_{band}_{dec:.3f}.txt")
        fn = pd.read_csv(lst, sep=r"\s+")["filename"].iloc[0]
        p = download([f"{PS1}fitscut.cgi?ra={RA0}&dec={DE0}&size=2880&output_size=1440&format=fits&red={fn}"],
                     CRAB / Path(fn).name, fits_ok)
        with fits.open(p) as h:
            hdr = h[0].header.copy()
            img = h[0].data.astype(float) / hdr["EXPTIME"]           # Zählrate: gleiche Skala in beiden Skycells
        mjd = np.array([50000 + int(hdr[k][1:5]) for k in hdr if k.startswith("INP_")])   # o5814g... = MJD 55814
        texp = np.array([hdr[k] for k in hdr if re.fullmatch(r"EXP_\d{4}", k)])
        return img, hdr, mjd, texp


    def ps1_mosaic(band):
        north, hdr, mjd, texp = ps1_part(band, DE0)
        south, _, mjd_s, texp_s = ps1_part(band, DE0 - 0.08)       # die Grenze liegt 160″ südlich des Pulsars
        both = np.isfinite(north) & np.isfinite(south)
        p = np.polyfit(south[both], north[both], 1)                # Untergrund und Skala im Überlapp angleichen
        img = np.where(np.isfinite(north), north, np.polyval(p, south))
        img[~np.isfinite(img)] = np.nanmedian(img)
        epoch = Time(np.average(mjd, weights=texp), format="mjd").decimalyear
        return img, hdr, epoch, dict(mjd=mjd, texp=texp, mjd_s=mjd_s, texp_s=texp_s, overlap=both.mean(), scale=p[0])


    # Gaia DR3: Feldsterne und Pulsar
    gaia = tap("SELECT source_id, ra, dec, pmra, pmdec, parallax, phot_g_mean_mag FROM {table} "
               "WHERE CONTAINS(POINT(ra, dec), CIRCLE(83.63308, 22.0145, 0.125)) = 1 AND phot_g_mean_mag < 20",
               CRAB / "gaia_field.csv")
    PSR_ID = 3403818172572314624                                  # Crab-Pulsar in Gaia DR3
    PSR = tap("SELECT source_id, ra, dec, parallax, parallax_error, pmra, pmra_error, pmdec, pmdec_error, "
              f"phot_g_mean_mag, ruwe FROM {{table}} WHERE source_id = {PSR_ID}", CRAB / "gaia_pulsar.csv").iloc[0]

    # Jodrell Bank: monatliche Ephemeriden des Pulsars (1982 bis heute)
    JB_FILES = [download([f"https://www.jb.man.ac.uk/pulsar/crab/{f}"], CRAB / f) for f in ("crab.txt", "crab2.txt")]
    print("Geladen:", ", ".join(p.name for p in sorted(CRAB.iterdir())))


def photos():
    """57. Drei Fotos aus 60 Jahren (Zellen 13, 14, 16 von nebulae_crab.ipynb)."""
    global DESC, EPOCH, EXTENT, RAW, ZOOM, astrometry, axes, band, cut, d, de_c, design
    global epoch, fig, find_stars, first, fit_expansion, fit_poly, gaia_at, hdr, hi, im, img, info
    global j, k, last, lo, masked_ncc, measure, name, p, pair, prep, px, py
    global ra_c, resample, show, subpixel, tangent, to_grid, v, w, x0, x1, xc, y0
    global y1, yc
    # Werkzeuge 1: Sterne finden, Astrometrie gegen Gaia, Umrechnen auf ein gemeinsames Raster

    def tangent(ra, dec):
        # gnomonische Projektion um (RA0, DE0) in Bogensekunden: xi nach Osten, eta nach Norden
        a, d, a0, d0 = map(np.radians, (ra, dec, RA0, DE0))
        c = np.sin(d) * np.sin(d0) + np.cos(d) * np.cos(d0) * np.cos(a - a0)
        xi = np.cos(d) * np.sin(a - a0) / c
        eta = (np.sin(d) * np.cos(d0) - np.cos(d) * np.sin(d0) * np.cos(a - a0)) / c
        return np.degrees(xi) * 3600, np.degrees(eta) * 3600


    def gaia_at(epoch, gmax=20.0):
        # Gaia-Positionen (Epoche 2016.0) mit der Eigenbewegung auf eine andere Epoche geschoben
        g = gaia[gaia["phot_g_mean_mag"] < gmax]
        dt = epoch - 2016.0
        dec = g["dec"] + g["pmdec"].fillna(0) * dt / 3.6e6
        ra = g["ra"] + g["pmra"].fillna(0) * dt / 3.6e6 / np.cos(np.radians(g["dec"]))
        xi, eta = tangent(ra.values, dec.values)
        return ra.values, dec.values, xi, eta, g["phot_g_mean_mag"].values


    def find_stars(img, fwhm, nsig=6, edge=10):
        # lokale Maxima im geglätteten, hochpassgefilterten Bild; Lage mit gaußgewichtetem Schwerpunkt
        bg = ndimage.gaussian_filter(img, 4 * fwhm)
        hp = ndimage.gaussian_filter(img, fwhm / 2.355) - bg
        mad = 1.4826 * np.median(np.abs(hp - np.median(hp)))
        peak = (hp == ndimage.maximum_filter(hp, size=int(2 * fwhm) + 1)) & (hp > nsig * mad)
        y, x = np.nonzero(peak)
        keep = (x > edge) & (y > edge) & (x < img.shape[1] - edge) & (y < img.shape[0] - edge)
        x, y = x[keep].astype(float), y[keep].astype(float)
        s = fwhm / 2.355
        r = int(np.ceil(3 * s))
        yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
        for _ in range(10):
            nx, ny = x.copy(), y.copy()
            for i, (xi, yi) in enumerate(zip(x, y)):
                ix, iy = int(round(xi)), int(round(yi))
                cut = np.clip(img[iy - r:iy + r + 1, ix - r:ix + r + 1] - bg[iy - r:iy + r + 1, ix - r:ix + r + 1], 0, None)
                dx, dy = xx + ix - xi, yy + iy - yi
                w = np.exp(-(dx ** 2 + dy ** 2) / (2 * s * s)) * cut
                if w.sum() > 0:
                    nx[i] += 2 * (w * dx).sum() / w.sum()
                    ny[i] += 2 * (w * dy).sum() / w.sum()
            x, y = np.clip(nx, edge, img.shape[1] - edge - 1), np.clip(ny, edge, img.shape[0] - edge - 1)
        return x, y


    def design(u, v, order):
        # Spalten u^i v^j mit i + j <= order (Polynom zweiten Grades: 6 Spalten)
        return np.vstack([u ** i * v ** j for i in range(order + 1) for j in range(order + 1 - i)]).T


    def fit_poly(u, v, a, b, order=2, clip=3.0):
        # (a, b) als Polynom von (u, v) mit Kleinste-Quadrate und Sigma-Clipping
        keep = np.ones(len(u), bool)
        for _ in range(5):
            A = design(u[keep], v[keep], order)
            ca = np.linalg.lstsq(A, a[keep], rcond=None)[0]
            cb = np.linalg.lstsq(A, b[keep], rcond=None)[0]
            res = np.hypot(design(u, v, order) @ ca - a, design(u, v, order) @ cb - b)
            keep = res < clip * np.sqrt(np.mean(res[keep] ** 2))
        return ca, cb, res, keep


    def astrometry(img, wcs, epoch, fwhm, pix, gmin, gmax=19.0, rmin=250.0, order=2):
        # Sterne im Bild finden, mit Gaia zur Epoche des Bildes paaren, Pixel -> (xi, eta) als Polynom anpassen.
        # Nur Sterne außerhalb von rmin, damit der Nebel die Schwerpunkte nicht verfälscht.
        x, y = find_stars(img, fwhm)
        ra, dec, xi, eta, G = gaia_at(epoch)
        gx, gy = wcs.world_to_pixel_values(ra, dec)
        dist, j = spatial.cKDTree(np.c_[x, y]).query(np.c_[gx, gy], distance_upper_bound=3.0 / pix)
        sel = np.isfinite(dist) & (G > gmin) & (G < gmax) & (np.hypot(xi, eta) > rmin)
        xs, ys = x[j[sel]], y[j[sel]]
        ca, cb, res, keep = fit_poly(xs, ys, xi[sel], eta[sel], order)
        ia, ib, _, _ = fit_poly(xi[sel][keep], eta[sel][keep], xs[keep], ys[keep], order)   # Umkehrung für das Raster
        xi_h, eta_h = tangent(*wcs.pixel_to_world_values(xs, ys))   # was die Plattenlösung im Kopf aus den Sternen macht
        A = design(xs, ys, order)
        return dict(fwd=(ca, cb), inv=(ia, ib), order=order, res=res, keep=keep, G=G[sel], xi=xi[sel], eta=eta[sel],
                    hdr_vec=np.c_[xi_h - xi[sel], eta_h - eta[sel]], fit_vec=np.c_[A @ ca - xi[sel], A @ cb - eta[sel]],
                    rms=np.sqrt(np.mean(res[keep] ** 2)), n=keep.sum(), n_found=len(x))


    def resample(img, ast, presmooth=0.0):
        # Bild auf das gemeinsame Raster (1″ pro Pixel, Osten links, Norden oben) umrechnen
        t = np.arange(-HALF, HALF + 1.0)
        XI, ETA = np.meshgrid(-t, t)
        A = design(XI.ravel(), ETA.ravel(), ast["order"])
        x = (A @ ast["inv"][0]).reshape(XI.shape)
        y = (A @ ast["inv"][1]).reshape(XI.shape)
        src = ndimage.gaussian_filter(img, presmooth) if presmooth else img
        return ndimage.map_coordinates(src, [y, x], order=3, mode="nearest")


    def to_grid(xi, eta):
        # (xi, eta) in ″ -> (Spalte, Zeile) im gemeinsamen Raster
        return HALF - np.asarray(xi), HALF + np.asarray(eta)


    EXTENT = [HALF + 0.5, -HALF - 0.5, -HALF - 0.5, HALF + 0.5]      # für imshow: Osten links


    def show(ax, im, lo=5, hi=99.7, gamma=0.6, cmap="gray"):
        v0, v1 = np.percentile(im, [lo, hi])
        return ax.imshow(np.clip((im - v0) / (v1 - v0), 0, 1) ** gamma, origin="lower", cmap=cmap, extent=EXTENT)

    # Werkzeuge 2: Bilder angleichen, Verschiebungen messen, Expansion anpassen

    def prep(name, fwhm_target=FWHM_COMMON, hp_sigma=HP_SIGMA, star_scale=1.0):
        # gleiche Schärfe für alle Epochen, Hochpass, Sterne ausmaskieren (Maske True = Pixel nicht benutzen)
        im = GRID[name]
        s = np.sqrt(max(fwhm_target ** 2 - FWHM[name] ** 2, 0.0)) / 2.355
        im = ndimage.gaussian_filter(im, s) if s > 0 else im
        hp = im - ndimage.gaussian_filter(im, hp_sigma)
        _, _, xi, eta, G = gaia_at(EPOCH[name])
        col, row = to_grid(xi, eta)
        rad = star_scale * np.where(G > 17, 4.0, np.where(G > 14, 6.0, 9.0))
        yy, xx = np.mgrid[0:2 * HALF + 1, 0:2 * HALF + 1]
        mask = np.zeros(im.shape, bool)
        for c, r, q in zip(col, row, rad):
            i0, i1 = int(max(r - q, 0)), int(min(r + q + 1, 2 * HALF + 1))
            j0, j1 = int(max(c - q, 0)), int(min(c + q + 1, 2 * HALF + 1))
            if i0 < i1 and j0 < j1:
                mask[i0:i1, j0:j1] |= (xx[i0:i1, j0:j1] - c) ** 2 + (yy[i0:i1, j0:j1] - r) ** 2 <= q * q
        return hp, mask


    def masked_ncc(tpl, tpl_ok, region, region_ok, min_frac=0.6):
        # normierte Kreuzkorrelation für jede Verschiebung; es zählen nur Pixel, die in BEIDEN Bildern gültig sind
        W = sliding_window_view(region, tpl.shape)
        V = sliding_window_view(region_ok, tpl.shape) & tpl_ok
        n = V.sum((-1, -2)).astype(float)
        T = np.where(V, tpl, 0.0)
        R = np.where(V, W, 0.0)
        st, sr = T.sum((-1, -2)), R.sum((-1, -2))
        with np.errstate(divide="ignore", invalid="ignore"):
            cov = (T * R).sum((-1, -2)) - st * sr / n
            var = ((T * T).sum((-1, -2)) - st * st / n) * ((R * R).sum((-1, -2)) - sr * sr / n)
            ncc = cov / np.sqrt(np.clip(var, 1e-30, None))
        ncc[n < min_frac * tpl.size] = -1
        return ncc


    def subpixel(ncc, iy, ix):
        # Parabel durch das Maximum und seine Nachbarn, getrennt in beiden Richtungen
        def vertex(a, b, c):
            d = a - 2 * b + c
            return 0.5 * (a - c) / d if d < 0 else 0.0
        return iy + vertex(ncc[iy - 1, ix], ncc[iy, ix], ncc[iy + 1, ix]), ix + vertex(ncc[iy, ix - 1], ncc[iy, ix], ncc[iy, ix + 1])


    def measure(late, early, patch=PATCH, search=SEARCH, step=STEP, use_mask=True):
        # Ausschnitte des späten Bildes im frühen Bild suchen; Ergebnis: Verschiebung früh -> spät in ″ (Osten, Norden)
        (h2, m2), (h1, m1) = late, early
        rows = []
        centers = np.arange(search + patch, 2 * HALF + 1 - search - patch, step)
        for r in centers:
            for c in centers:
                if not NEB[r, c]:
                    continue
                ok2 = ~m2[r - patch:r + patch + 1, c - patch:c + patch + 1]
                if ok2.mean() < 0.7:
                    continue
                tpl = h2[r - patch:r + patch + 1, c - patch:c + patch + 1]
                win = (slice(r - patch - search, r + patch + search + 1), slice(c - patch - search, c + patch + search + 1))
                if use_mask:
                    ncc = masked_ncc(tpl, ok2, h1[win], ~m1[win])
                else:                                             # Variation: Sterne als Nullen statt ausgelassen
                    ncc = masked_ncc(np.where(ok2, tpl, 0.0), np.ones_like(ok2), np.where(m1[win], 0.0, h1[win]),
                                     np.ones_like(m1[win]))
                iy, ix = np.unravel_index(np.argmax(ncc), ncc.shape)
                if not (0 < iy < ncc.shape[0] - 1 and 0 < ix < ncc.shape[1] - 1):
                    continue                                      # Maximum am Rand des Suchbereichs: unsicher
                sy, sx = subpixel(ncc, iy, ix)
                rows.append(dict(xi=HALF - c, eta=r - HALF, peak=ncc[iy, ix], dxi=sx - search, deta=-(sy - search)))
        return pd.DataFrame(rows)


    def fit_expansion(df, clip=3.0):
        # Verschiebung = k * (Ort - Zentrum): linear in (k, k*cx, k*cy); Ausreißer werden iterativ verworfen
        keep = np.ones(len(df), bool)
        for _ in range(5):
            d = df[keep]
            n = len(d)
            A = np.zeros((2 * n, 3))
            A[:n, 0], A[:n, 1], A[n:, 0], A[n:, 2] = d["xi"], -1, d["eta"], -1
            k, ax, ay = np.linalg.lstsq(A, np.r_[d["dxi"], d["deta"]], rcond=None)[0]
            res = np.hypot(df["dxi"] - (k * df["xi"] - ax), df["deta"] - (k * df["eta"] - ay)).values
            keep = res < clip * 1.4826 * np.median(res[keep])
        return dict(k=k, cx=ax / k, cy=ay / k, keep=keep, res=res, n=keep.sum())


    def pair(early, late, n_boot=200, **kw):
        # Verschiebungen zwischen zwei Epochen, Expansion anpassen, Konvergenzjahr mit Bootstrap-Fehler
        H_ = kw.pop("H", H)
        peak_min = kw.pop("peak_min", PEAK_MIN)
        df = measure(H_[late], H_[early], **kw)
        df = df[df["peak"] > peak_min].reset_index(drop=True)
        dt = EPOCH[late] - EPOCH[early]
        f = fit_expansion(df)
        boot = []
        for _ in range(n_boot):
            b = fit_expansion(df.iloc[rng.integers(0, len(df), len(df))].reset_index(drop=True))
            boot.append((EPOCH[late] - dt / b["k"], b["cx"], b["cy"]))
        boot = np.array(boot).reshape(-1, 3)
        err = boot.std(axis=0) if n_boot else np.full(3, np.nan)
        return dict(df=df, dt=dt, t0=EPOCH[late] - dt / f["k"], t0_err=err[0], cx_err=err[1], cy_err=err[2], boot=boot, **f)

    DESC = {"POSS-I E": "103aE + rotes Plexiglas, 620–670 nm", "POSS-II F": "IIIaF + RG610, 610–690 nm",
            "PS1 r": "CCD, Filter r, 550–690 nm", "PS1 i": "CCD, Filter i, 690–820 nm"}
    RAW = {}
    for name, p in PLATE_FILES.items():
        img, hdr = load_plate(p)
        RAW[name] = dict(img=img, hdr=hdr, wcs=WCS(hdr), epoch=plate_epoch(hdr),
                         pix=hdr["XPIXELSZ"] * hdr["PLTSCALE"] / 1000, label=f"Platte {hdr['PLATEID'].strip()}, {hdr['EXPOSURE']:.0f} min")
    for band in ("r", "i"):
        img, hdr, epoch, info = ps1_mosaic(band)
        first, last = Time(info["mjd"].min(), format="mjd"), Time(info["mjd"].max(), format="mjd")
        RAW[f"PS1 {band}"] = dict(img=img, hdr=hdr, wcs=WCS(hdr), epoch=epoch, pix=abs(hdr["CDELT1"]) * 3600, info=info,
                                  label=f"{len(info['mjd'])} Belichtungen, {info['texp'].sum():.0f} s, {first.iso[:7]} bis {last.iso[:7]}")
    EPOCH = {k: v["epoch"] for k, v in RAW.items()}

    print(f"{'Bild':10s} {'Epoche':>8s}  {'Pixel':>6s}  {'Größe':>9s}  Band und Belichtung")
    for k, v in RAW.items():
        print(f"{k:10s} {v['epoch']:8.2f}  {v['pix']:5.2f}″  {v['img'].shape[1]:4d}×{v['img'].shape[0]:<4d}  {DESC[k]}; {v['label']}")
    info = RAW["PS1 r"]["info"]
    print(f"PS1-Mosaik: Skycells im Überlapp angeglichen (Skala {info['scale']:.3f}), Überlapp {info['overlap']:.0%} des Ausschnitts")
    print(f"Zeitbasis 1951 -> PS1 r: {EPOCH['PS1 r'] - EPOCH['POSS-I E']:.2f} Jahre")

    ZOOM = (15.0, -75.0, 40.0)           # Mitte (xi, eta) und halbe Breite des Zooms [″]: helles Filament südlich des Pulsars
    fig, axes = plt.subplots(2, 3, figsize=(15, 10), gridspec_kw={"height_ratios": [1, 1]})
    for j, name in enumerate(["POSS-I E", "POSS-II F", "PS1 r"]):
        v = RAW[name]
        im = v["img"]
        lo, hi = np.percentile(im, [5, 99.7])
        axes[0, j].imshow(np.clip((im - lo) / (hi - lo), 0, 1) ** 0.6, origin="lower", cmap="gray")
        axes[0, j].set_title(f"{name} ({v['epoch']:.1f}), {v['pix']:.2f}″ pro Pixel", fontsize=10)
        axes[0, j].set_xlabel("x [Pixel]")
        axes[0, j].set_ylabel("y [Pixel]")
        # Zoom: Ecken des Himmelsausschnitts über die Plattenlösung in Pixel umrechnen
        xc, yc, w = ZOOM
        d = w / 3600
        ra_c = RA0 + xc / 3600 / np.cos(np.radians(DE0))
        de_c = DE0 + yc / 3600
        px, py = v["wcs"].world_to_pixel_values([ra_c + d / np.cos(np.radians(DE0)), ra_c - d / np.cos(np.radians(DE0))],
                                                [de_c - d, de_c + d])
        x0, x1 = int(min(px)), int(max(px)) + 1
        y0, y1 = int(min(py)), int(max(py)) + 1
        cut = im[y0:y1, x0:x1]
        lo, hi = np.percentile(cut, [1, 99.8])
        axes[1, j].imshow(np.clip((cut - lo) / (hi - lo), 0, 1), origin="lower", cmap="gray", interpolation="nearest",
                          extent=[x0 - 0.5, x1 - 0.5, y0 - 0.5, y1 - 0.5])
        axes[1, j].set_title(f"Zoom 80″ × 80″ um ξ = {xc:.0f}″, η = {yc:.0f}″", fontsize=10)
        axes[1, j].set_xlabel("x [Pixel]")
        axes[1, j].set_ylabel("y [Pixel]")
        axes[0, j].add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec="orange", lw=1.2))
    fig.suptitle("Rohdaten: POSS-I (1951), POSS-II (1991), Pan-STARRS (2009–2014), jeweils 12′ × 12′ um den Pulsar", fontsize=11)
    fig.tight_layout()
    plt.show()


def filaments():
    """58. Filamente und Synchrotronlicht (Zellen 19 von nebulae_crab.ipynb)."""
    global EBV, G_s, K_LINE, LAM_I, LAM_R, _, alpha, alpha_meas, ax, axes, cmap, de_s
    global ext, fig, frac, gmax, gx, gy, hi, i_img, im, inner, is_, k10
    global line, lo, nx, ny, pcx, pcy, r_img, ra_s, rad, redden, rs, sel
    global stars, title, w
    r_img, i_img = RAW["PS1 r"]["img"], RAW["PS1 i"]["img"]          # dasselbe Pixelgitter (0.5″), Zählrate
    rs, is_ = ndimage.gaussian_filter(r_img, 2), ndimage.gaussian_filter(i_img, 2)
    # Sterne ausmaskieren: rote Vordergrundsterne haben selbst ein kleines r/i
    ra_s, de_s, _, _, G_s = gaia_at(RAW["PS1 r"]["epoch"], 21)
    gx, gy = RAW["PS1 r"]["wcs"].world_to_pixel_values(ra_s, de_s)
    stars = np.zeros(r_img.shape, bool)
    stars[np.clip(np.round(gy).astype(int), 0, r_img.shape[0] - 1), np.clip(np.round(gx).astype(int), 0, r_img.shape[1] - 1)] = True
    for gmax, rad in [(21, 6), (17, 10), (14, 18)]:                  # Radius in Pixeln zu 0.5″, größer für helle Sterne
        sel = np.zeros(r_img.shape, bool)
        sel[np.clip(np.round(gy[G_s < gmax]).astype(int), 0, r_img.shape[0] - 1), np.clip(np.round(gx[G_s < gmax]).astype(int), 0, r_img.shape[1] - 1)] = True
        stars |= ndimage.binary_dilation(sel, iterations=rad)
    inner = (is_ > np.percentile(is_, 97)) & ~stars                     # helles Inneres des Nebels ohne Sterne
    K_LINE = np.percentile((rs / is_)[inner], 5)                         # wenig Linienlicht: kleinstes r/i
    line = r_img - K_LINE * i_img

    # Erwartung für Synchrotronlicht: F_nu ~ nu^-alpha, also r/i = (nu_r / nu_i)^-alpha = (lambda_r / lambda_i)^alpha, dazu die Rötung
    LAM_R, LAM_I, EBV = 617.0, 750.0, 0.52                              # Schwerpunkte der Filter [nm], Rötung des Krebsnebels
    redden = 10 ** (-0.4 * (2.27 - 1.68) * EBV)
    for alpha in (0.6, 0.8, 1.0):
        print(f"Synchrotron mit alpha = {alpha}: r/i = {(LAM_R / LAM_I) ** alpha:.3f} ohne Staub, {(LAM_R / LAM_I) ** alpha * redden:.3f} mit E(B-V) = {EBV}")
    alpha_meas = np.log(K_LINE / redden) / np.log(LAM_R / LAM_I)
    k10 = np.percentile((rs / is_)[inner], 10)
    print(f"gemessen: k = 5. Perzentil von r/i im Inneren (ohne Sterne) = {K_LINE:.3f} -> Spektralindex alpha = {alpha_meas:.2f} (mit Rötung); "
          f"mit dem 10. Perzentil {k10:.3f} -> alpha = {np.log(k10 / redden) / np.log(LAM_R / LAM_I):.2f}")
    frac = np.clip(line, 0, None).sum() / np.clip(r_img - np.median(r_img), 0, None).sum()
    print(f"Anteil des Linienlichts am r-Licht des Feldes: {frac:.0%}")

    w = RAW["PS1 r"]["wcs"]
    ny, nx = r_img.shape
    pcx, pcy = w.world_to_pixel_values(RA0, DE0)                    # Pixel des Bezugspunkts im PS1-Bild
    ext = [(pcx + 0.5) * 0.5, -(nx - pcx - 0.5) * 0.5, -(pcy + 0.5) * 0.5, (ny - pcy - 0.5) * 0.5]   # ″, Osten links
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.6))
    for ax, im, title, cmap in [(axes[0], i_img, "PS1 i: fast nur Synchrotronlicht", "gray"),
                                (axes[1], r_img, "PS1 r: Synchrotron + Linien", "gray"),
                                (axes[2], line, f"r − {K_LINE:.2f}·i: nur Linienlicht (Filamente)", "magma")]:
        lo, hi = np.percentile(im, [20, 99.8])
        ax.imshow(np.clip((im - lo) / (hi - lo), 0, 1) ** 0.6, origin="lower", cmap=cmap, extent=ext)
        ax.set_xlim(240, -240)
        ax.set_ylim(-200, 200)
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("ξ [″] (Osten links)")
        ax.set_ylabel("η [″]")
    fig.tight_layout()
    plt.show()


def gaia_frame():
    """59. Gaia-Sterne als Bezugssystem (Zellen 22 von nebulae_crab.ipynb)."""
    global G, PSR_1054, SCALE, ax, axes, bins, eta_g, fast, fig, hi, lo, pm
    global psr_eta, psr_xi, r_img, sc, shift60, xi_g
    G = gaia["phot_g_mean_mag"].values
    pm = np.hypot(gaia["pmra"], gaia["pmdec"]).values                   # mas/Jahr
    shift60 = pm * (EPOCH["PS1 r"] - EPOCH["POSS-I E"]) / 1000          # ″ in 60 Jahren
    xi_g, eta_g = tangent(gaia["ra"].values, gaia["dec"].values)
    psr_xi, psr_eta = tangent(PSR["ra"], PSR["dec"])
    PSR_1054 = (psr_xi + PSR["pmra"] * (T_SN - 2016.0) / 1000, psr_eta + PSR["pmdec"] * (T_SN - 2016.0) / 1000)   # Ort 1054
    print(f"Gaia DR3 im Kreis von 7.5′: {len(gaia)} Sterne mit G < 20, davon {np.sum((G < 19) & np.isfinite(pm))} mit G < 19 und Eigenbewegung")
    print(f"Eigenbewegung: Median {np.nanmedian(pm):.1f} mas/Jahr, also {np.nanmedian(shift60):.2f}″ in 60 Jahren; "
          f"{np.sum(shift60 > 0.5)} Sterne wandern mehr als 0.5″, der schnellste {np.nanmax(shift60):.1f}″")
    print(f"Pulsar (Gaia DR3 {PSR_ID}): G = {PSR['phot_g_mean_mag']:.2f}, Ort 2016.0 bei ξ = {psr_xi:.2f}″, η = {psr_eta:.2f}″, "
          f"μ = ({PSR['pmra']:.2f} ± {PSR['pmra_error']:.2f}, {PSR['pmdec']:.2f} ± {PSR['pmdec_error']:.2f}) mas/Jahr, "
          f"Parallaxe {PSR['parallax']:.3f} ± {PSR['parallax_error']:.3f} mas, RUWE {PSR['ruwe']:.2f}")
    print(f"Pulsar mit seiner Eigenbewegung zurückgerechnet auf 1054: ξ = {PSR_1054[0]:+.1f}″, η = {PSR_1054[1]:+.1f}″")

    fig, axes = plt.subplots(1, 2, figsize=(15, 6.5), gridspec_kw={"width_ratios": [1.1, 1]})
    ax = axes[0]
    r_img = RAW["PS1 r"]["img"]
    lo, hi = np.percentile(r_img, [5, 99.7])
    ax.imshow(np.clip((r_img - lo) / (hi - lo), 0, 1) ** 0.6, origin="lower", cmap="gray", extent=ext)
    sc = ax.scatter(xi_g, eta_g, c=G, s=14, cmap="viridis_r", vmin=12, vmax=20, lw=0)
    SCALE = 20                                                          # Pfeile: Bewegung in 60 Jahren, 20-fach
    fast = (shift60 > 0.3) & (shift60 < 5)                              # die wenigen schnelleren Sterne würden das Bild überdecken
    ax.quiver(xi_g[fast], eta_g[fast], -gaia["pmra"].values[fast] * 60e-3 * SCALE, gaia["pmdec"].values[fast] * 60e-3 * SCALE,
              angles="xy", scale_units="xy", scale=1, color="orange", width=0.003, label=f"Bewegung in 60 Jahren × {SCALE}")
    ax.plot(psr_xi, psr_eta, "c*", ms=12, label="Pulsar")
    ax.set_xlim(HALF, -HALF)
    ax.set_ylim(-HALF, HALF)
    ax.set_xlabel("ξ [″] (Osten links)")
    ax.set_ylabel("η [″]")
    ax.set_title("Gaia-DR3-Sterne auf dem Pan-STARRS-Bild (r)", fontsize=10)
    ax.legend(fontsize=8, loc="lower left")
    fig.colorbar(sc, ax=ax, label="G [mag]", fraction=0.04)
    ax = axes[1]
    bins = np.logspace(-3, 1.3, 40)
    ax.hist(shift60[np.isfinite(shift60)], bins=bins, color="grey", alpha=0.7, label="Feldsterne")
    ax.axvline(np.hypot(PSR["pmra"], PSR["pmdec"]) * 60e-3, color="c", lw=2, label="Pulsar")
    ax.axvspan(5, 15, color="tab:red", alpha=0.15, label="Filamente (erwartet)")
    ax.set_xscale("log")
    ax.set_xlabel("Bewegung zwischen 1951 und 2011 [″]")
    ax.set_ylabel("Zahl der Sterne")
    ax.set_title("Wie weit wandern die Bezugssterne in 60 Jahren?", fontsize=10)
    ax.legend(fontsize=9)
    fig.tight_layout()
    plt.show()


def epoch_astrometry():
    """60. Astrometrie jeder Epoche (Zellen 25 von nebulae_crab.ipynb)."""
    global AST, S, a, ax, axes, bins, col, fig, fwhm, gmin, h, idx
    global k, name, order, r, rms, title, v, vec
    AST = {}
    for name, fwhm, gmin in [("POSS-I E", 2.0, 13.0), ("POSS-II F", 3.0, 13.0), ("PS1 r", 2.5, 14.5), ("PS1 i", 2.5, 14.5)]:
        v = RAW[name]
        AST[name] = a = astrometry(v["img"], v["wcs"], v["epoch"], fwhm, v["pix"], gmin)
        h = a["hdr_vec"][a["keep"]]
        print(f"{name:10s}: {a['n_found']:4d} Sterne gefunden, {a['n']:3d} mit Gaia gepaart und benutzt; "
              f"Kopf-Plattenlösung: Versatz ({np.median(h[:, 0]):+.2f}, {np.median(h[:, 1]):+.2f})″, "
              f"Streuung {np.sqrt(np.mean(np.sum((h - np.median(h, 0)) ** 2, 1))):.2f}″ -> eigene Lösung: Rest {a['rms']:.3f}″")
    for order in (1, 3):
        a = astrometry(RAW["POSS-I E"]["img"], RAW["POSS-I E"]["wcs"], EPOCH["POSS-I E"], 2.0, RAW["POSS-I E"]["pix"], 13.0, order=order)
        print(f"Kontrolle POSS-I E mit Polynom vom Grad {order}: Rest {a['rms']:.3f}″ ({a['n']} Sterne)")

    fig, axes = plt.subplots(1, 3, figsize=(17, 5.6))
    a = AST["POSS-I E"]
    k = a["keep"]
    S = 150                                                              # Pfeile 150-fach vergrößert
    h = a["hdr_vec"][k] - np.median(a["hdr_vec"][k], axis=0)
    for ax, vec, title in [(axes[0], h, "POSS-I E: Kopf-Plattenlösung minus Gaia\n(ohne den mittleren Versatz)"),
                           (axes[1], a["fit_vec"][k], "POSS-I E: eigene Lösung (Grad 2) minus Gaia")]:
        ax.quiver(a["xi"][k], a["eta"][k], vec[:, 0] * S, vec[:, 1] * S, angles="xy", scale_units="xy", scale=1,
                  color="tab:blue", width=0.003)
        ax.quiver([-330], [-330], [1.0 * S], [0], angles="xy", scale_units="xy", scale=1, color="k", width=0.004)
        ax.text(-330 + S / 2, -315, "1″", ha="center", fontsize=9)
        ax.add_patch(plt.Circle((0, 0), 250, fill=False, ls="--", color="grey"))
        ax.set_xlim(HALF + 20, -HALF - 20)
        ax.set_ylim(-HALF - 20, HALF + 20)
        ax.set_aspect("equal")
        ax.set_xlabel("ξ [″] (Osten links)")
        ax.set_ylabel("η [″]")
        ax.set_title(title + f": Streuung {np.sqrt(np.mean(np.sum(vec ** 2, 1))):.2f}″", fontsize=10)
    ax = axes[2]
    bins = np.arange(13, 19.5, 1.0)
    for name, col in zip(AST, ["tab:red", "tab:orange", "tab:blue", "tab:cyan"]):
        a = AST[name]
        r = np.hypot(*a["fit_vec"].T)
        idx = np.digitize(a["G"], bins)
        rms = [np.sqrt(np.mean(r[(idx == i) & a["keep"]] ** 2)) if np.sum((idx == i) & a["keep"]) > 4 else np.nan
               for i in range(1, len(bins))]
        ax.plot(bins[:-1] + 0.5, rms, "o-", color=col, label=f"{name} ({EPOCH[name]:.1f}): {a['rms']:.3f}″")
    ax.set_yscale("log")
    ax.set_xlabel("Gaia G [mag]")
    ax.set_ylabel("Restfehler pro Stern (rms) [″]")
    ax.set_title("Restfehler der eigenen Lösung nach Helligkeit", fontsize=10)
    ax.legend(fontsize=9)
    fig.tight_layout()
    plt.show()


def common_grid():
    """61. Gemeinsames Raster und die Expansion auf einen Blick (Zellen 28 von nebulae_crab.ipynb)."""
    global EPOCHS3, ETA_G, FWHM, GRID, H, NEB, NEB_LEVEL, S_GRID, S_MAX, XI_G, _, a
    global a2, ax, axes, corr, enlarge, fig, fwhm_on_grid, h1, h2, hi, i, lab
    global lo, m1, m2, n, name, norm, ok, p, s, s_1054, sm, smooth
    global t0_glob, title, xx_g, yy_g
    GRID = {}
    for name in AST:
        GRID[name] = resample(RAW[name]["img"], AST[name], presmooth=1.0 if name.startswith("PS1") else 0.0)


    def fwhm_on_grid(im, epoch):
        # Halbwertsbreite der Sterne im Raster: 2D-Gauß an Gaia-Sterne mit 14 < G < 18 außerhalb des Nebels
        _, _, xi, eta, G = gaia_at(epoch, 18)
        col, row = to_grid(xi, eta)
        ok = (G > 14) & (np.abs(xi) < HALF - 30) & (np.abs(eta) < HALF - 30) & (np.hypot(xi, eta) > 250)
        yy, xx = np.mgrid[-7:8, -7:8]
        out = []
        for c, r in zip(col[ok], row[ok]):
            cut = im[int(round(r)) - 7:int(round(r)) + 8, int(round(c)) - 7:int(round(c)) + 8]
            f = lambda p: (p[0] * np.exp(-((xx - p[1]) ** 2 + (yy - p[2]) ** 2) / (2 * p[3] ** 2)) + p[4] - cut).ravel()
            p = optimize.least_squares(f, [cut.max() - np.median(cut), 0, 0, 1.5, np.median(cut)]).x
            if p[0] > 0 and 0.3 < abs(p[3]) < 5:
                out.append(2.355 * abs(p[3]))
        return np.median(out), len(out)


    FWHM = {}
    for name in GRID:
        FWHM[name], n = fwhm_on_grid(GRID[name], EPOCH[name])
        print(f"{name:10s}: Sterne im Raster mit FWHM {FWHM[name]:.2f}″ (Median aus {n} Sternen) -> Glättungskern "
              f"{np.sqrt(max(FWHM_COMMON ** 2 - FWHM[name] ** 2, 0)):.2f}″")

    EPOCHS3 = ["POSS-I E", "POSS-II F", "PS1 r"]
    H = {name: prep(name) for name in EPOCHS3}
    smooth = {n: ndimage.gaussian_filter(GRID[n], np.sqrt(max(FWHM_COMMON ** 2 - FWHM[n] ** 2, 0)) / 2.355) for n in EPOCHS3}

    # Nebelmaske: geglättetes PS1-r-Bild über 3 % des Helligkeitsumfangs, größte zusammenhängende Fläche, Löcher gefüllt
    NEB_LEVEL = 0.03
    sm = ndimage.gaussian_filter(GRID["PS1 r"], 8)
    lo, hi = np.percentile(sm, [50, 99.5])
    lab, _ = ndimage.label(sm > lo + NEB_LEVEL * (hi - lo))
    NEB = ndimage.binary_fill_holes(lab == np.bincount(lab.ravel())[1:].argmax() + 1)
    print(f"Nebelmaske: {NEB.sum()} Quadratbogensekunden, so groß wie ein Kreis mit {np.sqrt(NEB.sum() / np.pi):.0f}″ Radius; "
          f"Sterne maskiert: {H['PS1 r'][1].mean():.0%} des Rasters")

    # Grobe Probe: 1951 um den Geburtsort des Pulsars vergrößern und mit 2011 korrelieren
    yy_g, xx_g = np.mgrid[0:2 * HALF + 1, 0:2 * HALF + 1]
    XI_G, ETA_G = HALF - xx_g, yy_g - HALF


    def enlarge(img, s, c=PSR_1054):
        # Wert bei p kommt von c + (p - c)/s: das Bild wird um c um den Faktor s größer
        col, row = to_grid(c[0] + (XI_G - c[0]) / s, c[1] + (ETA_G - c[1]) / s)
        return ndimage.map_coordinates(img, [row, col], order=1, mode="nearest")


    (h1, m1), (h2, m2) = H["POSS-I E"], H["PS1 r"]
    S_GRID = np.arange(1.0, 1.1201, 0.0025)
    corr = []
    for s in S_GRID:
        ok = NEB & ~m2 & ~(enlarge(m1.astype(float), s) > 0.5)
        corr.append(np.corrcoef(enlarge(h1, s)[ok], h2[ok])[0, 1])
    corr = np.array(corr)
    i = np.argmax(corr)
    p = np.polyfit(S_GRID[i - 3:i + 4], corr[i - 3:i + 4], 2)
    S_MAX = -p[1] / (2 * p[0])
    s_1054 = (EPOCH["PS1 r"] - T_SN) / (EPOCH["POSS-I E"] - T_SN)
    t0_glob = EPOCH["PS1 r"] - (EPOCH["PS1 r"] - EPOCH["POSS-I E"]) / (1 - 1 / S_MAX)
    print(f"Korrelation 1951 gegen 2011: {corr[0]:.2f} ohne Vergrößerung, {corr.max():.2f} bei s = {S_MAX:.4f} "
          f"(der Nebel ist um {100 * (S_MAX - 1):.1f} % gewachsen) -> grobes Konvergenzjahr {t0_glob:.0f}")
    print(f"Erwartung bei konstanter Geschwindigkeit seit 1054: s = {s_1054:.4f} ({100 * (s_1054 - 1):.1f} %)")


    def norm(im):
        v = np.percentile(im[NEB], [1, 99.5])
        return np.clip((im - v[0]) / (v[1] - v[0]), 0, 1)


    a2 = norm(h2)
    fig, axes = plt.subplots(1, 3, figsize=(18, 6.2), gridspec_kw={"width_ratios": [1, 1, 0.9]})
    for ax, a, title in [(axes[0], norm(h1), "rot = 1951, türkis = 2011 (Hochpass)"),
                         (axes[1], norm(enlarge(h1, S_MAX)), f"1951 um {100 * (S_MAX - 1):.1f} % vergrößert: Filamente decken sich"),
                         ]:
        ax.imshow(np.dstack([a, a2, a2]), origin="lower", extent=EXTENT)
        ax.contour(NEB, levels=[0.5], colors="yellow", linewidths=0.6, extent=EXTENT, origin="lower")
        ax.set_xlim(230, -230)
        ax.set_ylim(-200, 200)
        ax.set_xlabel("ξ [″] (Osten links)")
        ax.set_ylabel("η [″]")
        ax.set_title(title, fontsize=10)
    ax = axes[2]
    ax.plot(S_GRID, corr, "k-", lw=2)
    ax.axvline(S_MAX, color="tab:red", label=f"Maximum s = {S_MAX:.4f}")
    ax.axvline(s_1054, color="grey", ls=":", lw=2, label=f"konstant seit 1054: s = {s_1054:.4f}")
    ax.set_xlabel("Vergrößerung s des Bildes von 1951")
    ax.set_ylabel("Korrelation mit 2011 (Nebel ohne Sterne)")
    ax.set_title("Wie stark ist der Nebel in 60 Jahren gewachsen?", fontsize=10)
    ax.legend(fontsize=9)
    fig.tight_layout()
    plt.show()


def displacements():
    """62. Wie weit sind die Filamente gewandert? (Zellen 31 von nebulae_crab.ipynb)."""
    global P60, SC, ax, c, cand, clean, cm, df, dt60, ex, ext_win, fig
    global gs, h1, h2, hp_, im, k, m1, m2, m_, n, n_all, ncc_ex
    global qv, r, rad, rr_, tan_, title, v, win
    P60 = pair("POSS-I E", "PS1 r")
    df = P60["df"]
    dt60 = P60["dt"]
    rr_ = np.hypot(df["xi"], df["eta"])
    rad = (df["dxi"] * df["xi"] + df["deta"] * df["eta"]) / rr_
    tan_ = (df["deta"] * df["xi"] - df["dxi"] * df["eta"]) / rr_
    n_all = len(measure(H["PS1 r"], H["POSS-I E"]))
    print(f"Ausschnitte in der Nebelmaske mit Maximum im Suchbereich: {n_all}; mit Korrelation > {PEAK_MIN}: {len(df)}")
    print(f"Verschiebung 1951 -> 2011 ({dt60:.2f} Jahre): Median {np.median(np.hypot(df['dxi'], df['deta'])):.2f}″, "
          f"größte {np.hypot(df['dxi'], df['deta']).max():.1f}″; radial im Median {np.median(rad):+.2f}″, tangential {np.median(tan_):+.2f}″")
    print(f"Anteil der Verschiebungen, die vom Pulsar weg zeigen: {np.mean(rad > 0):.0%}")

    # Beispiel: ein Ausschnitt ohne maskierte Sterne, hohe Korrelation, große Verschiebung
    (h2, m2), (h1, m1) = H["PS1 r"], H["POSS-I E"]
    clean = np.array([not m2[int(HALF + e) - PATCH:int(HALF + e) + PATCH + 1, int(HALF - x) - PATCH:int(HALF - x) + PATCH + 1].any()
                      for x, e in zip(df["xi"], df["eta"])])
    cand = df[clean & (df["peak"] > 0.85)]
    ex = cand.loc[np.hypot(cand["dxi"], cand["deta"]).idxmax()].copy()
    ex["r"] = np.hypot(ex["xi"], ex["eta"])
    c, r = int(HALF - ex["xi"]), int(HALF + ex["eta"])
    win = (slice(r - PATCH - SEARCH, r + PATCH + SEARCH + 1), slice(c - PATCH - SEARCH, c + PATCH + SEARCH + 1))
    ncc_ex = masked_ncc(h2[r - PATCH:r + PATCH + 1, c - PATCH:c + PATCH + 1], ~m2[r - PATCH:r + PATCH + 1, c - PATCH:c + PATCH + 1],
                        h1[win], ~m1[win])
    print(f"Beispiel bei ξ = {ex['xi']:.0f}″, η = {ex['eta']:.0f}″ (Abstand {ex['r']:.0f}″): Verschiebung ({ex['dxi']:+.2f}, {ex['deta']:+.2f})″, "
          f"Korrelation {ex['peak']:.2f}")

    fig = plt.figure(figsize=(16, 11))
    gs = fig.add_gridspec(3, 3)
    ext_win = [ex["xi"] + PATCH + SEARCH + 0.5, ex["xi"] - PATCH - SEARCH - 0.5, ex["eta"] - PATCH - SEARCH - 0.5, ex["eta"] + PATCH + SEARCH + 0.5]
    for k, (n, title) in enumerate([("PS1 r", "2011: Ausschnitt (Rahmen) im Hochpassbild"), ("POSS-I E", "1951: gleiche Stelle (gestrichelt) und Treffer")]):
        ax = fig.add_subplot(gs[k, 0])
        hp_, m_ = H[n]
        v = np.where(m_, np.nan, hp_)[win]
        cm = plt.get_cmap("gray").copy()
        cm.set_bad("tab:red", 0.35)                                       # maskierte Sterne rötlich
        ax.imshow(v, origin="lower", cmap=cm, extent=ext_win, vmin=np.nanpercentile(v, 2), vmax=np.nanpercentile(v, 99.5))
        ax.add_patch(plt.Rectangle((ex["xi"] - PATCH, ex["eta"] - PATCH), 2 * PATCH, 2 * PATCH, fill=False, ec="c", lw=1.5,
                                   ls="--" if k else "-"))
        if k:
            ax.add_patch(plt.Rectangle((ex["xi"] - ex["dxi"] - PATCH, ex["eta"] - ex["deta"] - PATCH), 2 * PATCH, 2 * PATCH,
                                       fill=False, ec="orange", lw=1.5))
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("ξ [″]")
        ax.set_ylabel("η [″]")
    ax = fig.add_subplot(gs[2, 0])
    im = ax.imshow(np.where(ncc_ex > -1, ncc_ex, np.nan), origin="lower", cmap="viridis",
                   extent=[SEARCH + 0.5, -SEARCH - 0.5, -SEARCH - 0.5, SEARCH + 0.5])
    ax.plot(-ex["dxi"], -ex["deta"], "r+", ms=14, mew=2)
    ax.set_xlabel("Versatz des Ausschnitts in ξ [″]")
    ax.set_ylabel("Versatz in η [″]")
    ax.set_title("Korrelation für jeden Versatz (Kreuz: Maximum)", fontsize=10)
    fig.colorbar(im, ax=ax, fraction=0.05, label="NCC")
    ax = fig.add_subplot(gs[:, 1:])
    show(ax, smooth["PS1 r"], lo=20, hi=99.8, gamma=0.7)
    SC = 5
    qv = ax.quiver(df["xi"], df["eta"], df["dxi"] * SC, df["deta"] * SC, df["peak"], angles="xy", scale_units="xy", scale=1,
                   cmap="autumn", width=0.0025)
    ax.quiver([200], [-190], [5 * SC], [0], angles="xy", scale_units="xy", scale=1, color="w", width=0.003)
    ax.text(200 - 2.5 * SC, -180, "5″", color="w", ha="center", fontsize=10)
    ax.plot(psr_xi, psr_eta, "c*", ms=12)
    ax.set_xlim(240, -240)
    ax.set_ylim(-210, 210)
    ax.set_xlabel("ξ [″] (Osten links)")
    ax.set_ylabel("η [″]")
    ax.set_title(f"{len(df)} Verschiebungen 1951 → 2011, Pfeile {SC}-fach (Farbe: Korrelation)", fontsize=10)
    fig.colorbar(qv, ax=ax, fraction=0.035, label="Korrelation")
    fig.tight_layout()
    plt.show()


def expansion_center():
    """63. Das Expansionszentrum und der Geburtsort des Pulsars (Zellen 34 von nebulae_crab.ipynb)."""
    global _, ax, axes, cx, cy, d, ex_, ey_, f, fig, m_eta, m_xi
    global psr_1054, psr_t, row_
    f = P60
    cx, cy = f["cx"], f["cy"]
    ex_, ey_ = f["cx_err"], f["cy_err"]
    # Pulsar: heute (2016.0) und zurückgerechnet auf 1054 (Schritt 59)
    psr_1054 = PSR_1054
    psr_t = np.linspace(T_SN, 2016.0, 50) - 2016.0
    # Martin et al. (2025): Zentrum bei 5h34m32.67s +22°00'46.7" (J2000), Fehler 1.2"
    m_xi, m_eta = tangent(15 * (5 + 34 / 60 + 32.67 / 3600), 22 + 0 / 60 + 46.7 / 3600)
    print(f"Expansionszentrum (eigene Messung): ξ = {cx:+.1f} ± {ex_:.1f}″, η = {cy:+.1f} ± {ey_:.1f}″ ({f['n']} von {len(f['df'])} Ausschnitten)")
    print(f"Pulsar 2016.0: ξ = {psr_xi:+.2f}″, η = {psr_eta:+.2f}″; zurückgerechnet auf 1054: ξ = {psr_1054[0]:+.1f}″, η = {psr_1054[1]:+.1f}″")
    print(f"Abstand Zentrum - Pulsar 1054: {np.hypot(cx - psr_1054[0], cy - psr_1054[1]):.1f}″ "
          f"(Δξ = {cx - psr_1054[0]:+.1f}″, Δη = {cy - psr_1054[1]:+.1f}″); Zentrum - Pulsar heute: {np.hypot(cx - psr_xi, cy - psr_eta):.1f}″")
    print(f"Martin et al. (2025): ξ = {m_xi:+.1f}″, η = {m_eta:+.1f}″ ± 1.2″; Unterschied zur eigenen Messung "
          f"Δξ = {cx - m_xi:+.1f}″, Δη = {cy - m_eta:+.1f}″")
    print(f"Restabweichung pro Ausschnitt nach der Anpassung: {np.sqrt(np.mean(f['res'][f['keep']] ** 2) / 2):.2f}″ pro Achse")

    fig, axes = plt.subplots(1, 2, figsize=(15, 6.8))
    ax = axes[0]
    show(ax, smooth["PS1 r"], lo=20, hi=99.8, gamma=0.7)
    d = f["df"][f["keep"]]
    for _, row_ in d.sample(150, random_state=1).iterrows():                  # Verschiebungen nach innen verlängert
        ax.plot([row_["xi"], row_["xi"] - row_["dxi"] / f["k"]], [row_["eta"], row_["eta"] - row_["deta"] / f["k"]],
                color="orange", lw=0.4, alpha=0.6)
    ax.plot(cx, cy, "w+", ms=16, mew=2.5)
    ax.set_xlim(240, -240)
    ax.set_ylim(-210, 210)
    ax.set_xlabel("ξ [″] (Osten links)")
    ax.set_ylabel("η [″]")
    ax.set_title("150 Verschiebungen, bis zum Ursprung zurückverlängert", fontsize=10)
    ax = axes[1]
    show(ax, GRID["PS1 r"], lo=20, hi=99.95, gamma=0.5)
    ax.scatter(f["boot"][:, 1], f["boot"][:, 2], s=4, c="orange", alpha=0.5, label="Zentrum, Bootstrap")
    ax.errorbar(cx, cy, xerr=ex_, yerr=ey_, fmt="o", color="orange", mec="k", ms=8, capsize=3, label="Zentrum (eigene Messung)")
    ax.errorbar(m_xi, m_eta, xerr=1.2, yerr=1.2, fmt="s", color="lime", mec="k", ms=7, capsize=3, label="Zentrum Martin et al. (2025)")
    ax.plot(psr_xi + PSR["pmra"] * psr_t / 1000, psr_eta + PSR["pmdec"] * psr_t / 1000, "c-", lw=2, label="Weg des Pulsars seit 1054 (Gaia)")
    ax.plot(*psr_1054, "co", ms=8, mec="k", label="Pulsar 1054")
    ax.plot(psr_xi, psr_eta, "c*", ms=16, mec="k", label="Pulsar heute")
    ax.set_xlim(25, -10)
    ax.set_ylim(-17, 12)
    ax.set_xlabel("ξ [″] (Osten links)")
    ax.set_ylabel("η [″]")
    ax.set_title("Zentrum der Expansion und Weg des Pulsars", fontsize=10)
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    plt.show()


def hubble_diagram():
    """64. Ein Hubble-Diagramm des Nebels und das Konvergenzjahr (Zellen 37 von nebulae_crab.ipynb)."""
    global T0, YEARS, _, ax, axes, bins, closest_approach, d, e_rate, fig, idx, med
    global nx_, ny_, px, py, r_c, rg, sc_data, sc_true, sig, t2, t_ca, t_sim
    global v_rad, vx, vx_true, vy, vy_true
    t2 = EPOCH["PS1 r"]
    d = P60["df"][P60["keep"]].reset_index(drop=True)
    px, py = d["xi"] - cx, d["eta"] - cy
    r_c = np.hypot(px, py)
    v_rad = (d["dxi"] * px + d["deta"] * py) / r_c / dt60                    # ″ pro Jahr vom Zentrum weg
    e_rate = P60["k"] / dt60                                                  # Expansionsrate [1/Jahr]
    T0 = P60["t0"]
    print(f"Steigung im Hubble-Diagramm: e = {e_rate * 100:.4f} % pro Jahr -> scheinbares Alter 1/e = {1 / e_rate:.0f} Jahre "
          f"vor {t2:.1f}, Konvergenzjahr {T0:.1f} ± {P60['t0_err']:.1f}")
    print(f"Größte Geschwindigkeit am Himmel: {v_rad.max():.3f}″/Jahr in {r_c[v_rad.idxmax()]:.0f}″ Abstand")

    def closest_approach(xi, eta, vx, vy, years):
        # Radius (rms) der zurückgerechneten Punktwolke für jedes Jahr
        return np.array([np.sqrt(np.var(xi - vx * (t2 - t)) + np.var(eta - vy * (t2 - t))) for t in years])

    YEARS = np.arange(950, 1301, 1.0)
    vx, vy = d["dxi"] / dt60, d["deta"] / dt60
    sc_data = closest_approach(d["xi"], d["eta"], vx, vy, YEARS)
    t_ca = YEARS[np.argmin(sc_data)]
    # Simulation: dieselben Orte, perfekte Expansion aus T0, dazu Rauschen in der Größe der gemessenen Restabweichung
    sig = np.sqrt(np.mean(P60["res"][P60["keep"]] ** 2) / 2)
    vx_true, vy_true = P60["k"] * px / dt60, P60["k"] * py / dt60
    sc_true = closest_approach(d["xi"], d["eta"], vx_true, vy_true, YEARS)
    t_sim = []
    for _ in range(50):
        nx_, ny_ = rng.normal(0, sig, len(d)) / dt60, rng.normal(0, sig, len(d)) / dt60
        t_sim.append(YEARS[np.argmin(closest_approach(d["xi"], d["eta"], vx_true + nx_, vy_true + ny_, YEARS))])
    print(f"Methode der kleinsten Streuung: Minimum {t_ca:.0f} (Radius dort {sc_data.min():.1f}″)")
    print(f"Simulation ohne Rauschen: Minimum {YEARS[np.argmin(sc_true)]:.0f}; mit {sig:.2f}″ Rauschen pro Achse: "
          f"{np.mean(t_sim):.0f} ± {np.std(t_sim):.0f} (50 Ziehungen) -> Verschiebung um {np.mean(t_sim) - T0:+.0f} Jahre")

    fig, axes = plt.subplots(1, 2, figsize=(15, 5.8))
    ax = axes[0]
    ax.scatter(r_c, v_rad * 1000, s=6, alpha=0.4, color="tab:blue", label=f"Ausschnitte ({len(d)})")
    bins = np.arange(0, 241, 20)
    idx = np.digitize(r_c, bins)
    med = [np.median(v_rad[idx == i]) * 1000 if np.sum(idx == i) > 5 else np.nan for i in range(1, len(bins))]
    ax.plot(bins[:-1] + 10, med, "ko", ms=7, label="Median je 20″")
    rg = np.linspace(0, 240, 2)
    ax.plot(rg, e_rate * rg * 1000, "r-", lw=2, label=f"Gerade: 1/e = {1 / e_rate:.0f} Jahre (Konvergenz {T0:.0f})")
    ax.plot(rg, rg / (t2 - T_SN) * 1000, "k--", lw=1.5, label=f"konstante Geschwindigkeit seit {T_SN:.0f}")
    ax.set_xlabel("Abstand vom Expansionszentrum [″]")
    ax.set_ylabel("Geschwindigkeit vom Zentrum weg [mas/Jahr]")
    ax.set_title("Hubble-Diagramm des Krebsnebels (1951 → 2011)", fontsize=10)
    ax.set_xlim(0, 240)
    ax.legend(fontsize=9)
    ax = axes[1]
    ax.plot(YEARS, sc_data, "b-", lw=2, label=f"gemessene Geschwindigkeiten: Minimum {t_ca:.0f}")
    ax.plot(YEARS, sc_true, "k--", lw=1.5, label=f"Simulation ohne Rauschen: Minimum {YEARS[np.argmin(sc_true)]:.0f}")
    ax.axvline(T0, color="r", lw=1.5, label=f"Fit-Methode {T0:.0f}")
    ax.axvline(T_SN, color="grey", ls=":", lw=2, label="Supernova 1054")
    ax.axvspan(np.mean(t_sim) - np.std(t_sim), np.mean(t_sim) + np.std(t_sim), color="b", alpha=0.15,
               label=f"Simulation mit Rauschen: {np.mean(t_sim):.0f} ± {np.std(t_sim):.0f}")
    ax.set_xlabel("Jahr")
    ax.set_ylabel("Radius der zurückgerechneten Punktwolke (rms) [″]")
    ax.set_title("Methode der kleinsten Streuung", fontsize=10)
    ax.set_ylim(0, None)
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()


def three_epochs():
    """65. Drei Epochen, drei Paare: Wie sicher ist das Jahr? (Zellen 40 von nebulae_crab.ipynb)."""
    global Hv, PAIRS, RES, T0_SYS, VAR, a_, ax, axes, b_, col, delta, dts
    global fig, i, k_chain, kw, lab, labs, ls, t0_var, v
    PAIRS = {"1951 → 2011": ("POSS-I E", "PS1 r"), "1951 → 1991": ("POSS-I E", "POSS-II F"), "1991 → 2011": ("POSS-II F", "PS1 r")}
    RES = {"1951 → 2011": P60}
    for lab, (a_, b_) in list(PAIRS.items())[1:]:
        RES[lab] = pair(a_, b_)
    for lab, v in RES.items():
        print(f"{lab}: Δt = {v['dt']:5.2f} Jahre, {v['n']:4d} Ausschnitte, k = {v['k']:.5f}, Konvergenzjahr {v['t0']:7.1f} ± {v['t0_err']:4.1f}, "
              f"Zentrum ({v['cx']:+.1f}, {v['cy']:+.1f})″")
    k_chain = 1 - (1 - RES["1951 → 1991"]["k"]) * (1 - RES["1991 → 2011"]["k"])
    print(f"Verkettet: k = {k_chain:.5f} gegen direkt {P60['k']:.5f} (Unterschied {100 * (k_chain / P60['k'] - 1):+.1f} %)")

    VAR = {"Grundeinstellung": P60}
    VAR["Ausschnitte 29″ statt 21″"] = pair("POSS-I E", "PS1 r", patch=14, n_boot=0)
    for lab, kw in [("Hochpass 4″ statt 6″", dict(hp_sigma=4.0)), ("Hochpass 10″", dict(hp_sigma=10.0)),
                    ("Schärfe 5.5″ statt 4.4″", dict(fwhm_target=5.5)), ("Sternmasken × 1.5", dict(star_scale=1.5))]:
        Hv = {n: prep(n, **kw) for n in ("POSS-I E", "PS1 r")}
        VAR[lab] = pair("POSS-I E", "PS1 r", H=Hv, n_boot=0)
    VAR["Korrelation > 0.75"] = pair("POSS-I E", "PS1 r", peak_min=0.75, n_boot=0)
    VAR["Korrelation > 0.45"] = pair("POSS-I E", "PS1 r", peak_min=0.45, n_boot=0)
    t0_var = np.array([v["t0"] for v in VAR.values()])
    T0_SYS = t0_var.std()
    for lab, v in VAR.items():
        print(f"  {lab:27s}: {v['n']:4d} Ausschnitte, Konvergenzjahr {v['t0']:7.1f}")
    print(f"Streuung über die Einstellungen (systematisch): ± {T0_SYS:.1f} Jahre; Spanne {t0_var.min():.0f} bis {t0_var.max():.0f}")
    print(f"Ergebnis: Konvergenzjahr {T0:.0f} ± {P60['t0_err']:.0f} (statistisch) ± {T0_SYS:.0f} (systematisch)")

    fig, axes = plt.subplots(1, 3, figsize=(19, 5.8), gridspec_kw={"width_ratios": [1, 1.1, 1], "wspace": 0.55})
    ax = axes[0]
    for i, (lab, v) in enumerate(RES.items()):
        ax.errorbar(i, v["t0"], yerr=v["t0_err"], fmt="o", ms=8, capsize=4, color=["tab:red", "tab:orange", "tab:green"][i])
    ax.axhline(T_SN, color="grey", ls=":", lw=2, label="Supernova 1054")
    ax.axhspan(T0 - T0_SYS, T0 + T0_SYS, color="tab:red", alpha=0.12, label="1951 → 2011 ± systematisch")
    ax.set_xticks(range(3), [f"{lab}\n(Δt = {v['dt']:.0f} J.)" for lab, v in RES.items()])
    ax.set_ylabel("Konvergenzjahr")
    ax.set_title("Drei Paare von Epochen (Fehler: Bootstrap)", fontsize=10)
    ax.legend(fontsize=8, loc="lower right")
    ax = axes[1]
    labs = list(VAR)
    ax.barh(range(len(labs)), [v["t0"] - T0 for v in VAR.values()], color=["tab:red"] + ["grey"] * (len(labs) - 1))
    ax.set_yticks(range(len(labs)), [f"{l_} ({VAR[l_]['n']})" for l_ in labs], fontsize=9)
    ax.invert_yaxis()
    ax.axvline(0, color="k", lw=0.8)
    ax.set_xlabel(f"Konvergenzjahr minus Grundeinstellung ({T0:.0f}) [Jahre]")
    ax.set_title("1951 → 2011 mit geänderten Einstellungen (Zahl der Ausschnitte)", fontsize=10)
    ax = axes[2]
    dts = np.linspace(5, 80, 200)
    for delta, ls in [(0.05, "--"), (0.1, "-")]:
        ax.plot(dts, (t2 - T0) ** 2 / dts * delta / 120, "k", ls=ls, label=f"Fehler {delta}″ in 120″ Abstand")
    for (lab, v), col in zip(RES.items(), ["tab:red", "tab:orange", "tab:green"]):
        ax.plot(v["dt"], (t2 - T0) ** 2 / v["dt"] * 0.1 / 120, "o", color=col, ms=9, label=lab)
    ax.set_xlabel("Zeitbasis Δt [Jahre]")
    ax.set_ylabel("Verschiebung des Konvergenzjahres [Jahre]")
    ax.set_title("Empfindlichkeit gegen systematische Fehler", fontsize=10)
    ax.set_ylim(0, 60)
    ax.legend(fontsize=8)
    plt.show()


def distance():
    """66. Wie weit ist der Krebsnebel entfernt? (Zellen 43 von nebulae_crab.ipynb)."""
    global A_AX, B_AX, D_EXP, D_GAIA, L, PA_AX, ang, ax, axes, col, cov, dd
    global eplx, ex_eta, ex_xi, fig, lab, lam, mu_b, p, pa, pdf, plx, rel
    global s, tt, vec, xm, xx_, y, ym, yy_
    yy_, xx_ = np.nonzero(NEB)
    cov = np.cov(np.vstack([HALF - xx_, yy_ - HALF]).astype(float))
    lam, vec = np.linalg.eigh(cov)
    A_AX, B_AX = 2 * np.sqrt(lam[1]), 2 * np.sqrt(lam[0])                   # gleichmäßig gefüllte Ellipse: Varianz = a²/4
    PA_AX = np.degrees(np.arctan2(vec[0, 1], vec[1, 1])) % 180            # Lagewinkel der großen Achse, Nord über Ost
    mu_b = e_rate * B_AX                                                   # ″ pro Jahr am Rand der kurzen Achse
    D_EXP = V_R_MAX / (4.74 * mu_b)
    rel = np.sqrt(0.10 ** 2 + 0.10 ** 2 + (P60["t0_err"] / (t2 - T0)) ** 2)  # 10 % für v_r,max, 10 % für b, dazu e
    plx, eplx = PSR["parallax"], PSR["parallax_error"]
    D_GAIA = 1000 / plx
    print(f"Nebelmaske als Ellipse: halbe Achsen a = {A_AX:.0f}″, b = {B_AX:.0f}″, Lagewinkel {PA_AX:.0f}°")
    print(f"Expansionsrate e = {e_rate:.3e} pro Jahr -> Rand der kurzen Achse bewegt sich mit {mu_b * 1000:.0f} mas/Jahr")
    print(f"Expansionsparallaxe: d = {V_R_MAX:.0f} km/s / (4.74 × {mu_b:.4f}″/Jahr) = {D_EXP:.0f} ± {rel * D_EXP:.0f} pc")
    print(f"Gaia DR3: Parallaxe {plx:.3f} ± {eplx:.3f} mas -> d = 1/ϖ = {D_GAIA:.0f} pc "
          f"(68 %: {1000 / (plx + eplx):.0f} bis {1000 / (plx - eplx):.0f} pc)")
    print(f"VLBI (Lin et al. 2023): 0.53 ± 0.06 mas -> {1000 / 0.53:.0f} pc")
    print(f"Mit d = {D_GAIA:.0f} pc: Rand der langen Achse {4.74 * e_rate * A_AX * D_GAIA:.0f} km/s, der kurzen {4.74 * e_rate * B_AX * D_GAIA:.0f} km/s; "
          f"Größe des Nebels {2 * A_AX * D_GAIA / 206265:.1f} × {2 * B_AX * D_GAIA / 206265:.1f} pc")

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    ax = axes[0]
    show(ax, smooth["PS1 r"], lo=20, hi=99.8, gamma=0.7)
    ax.contour(NEB, levels=[0.5], colors="yellow", linewidths=1, extent=EXTENT, origin="lower")
    xm, ym = (HALF - xx_).mean(), (yy_ - HALF).mean()
    tt = np.linspace(0, 2 * np.pi, 300)
    pa = np.radians(PA_AX)
    ex_xi = xm + A_AX * np.cos(tt) * np.sin(pa) + B_AX * np.sin(tt) * np.cos(pa)
    ex_eta = ym + A_AX * np.cos(tt) * np.cos(pa) - B_AX * np.sin(tt) * np.sin(pa)
    ax.plot(ex_xi, ex_eta, "c--", lw=1.5, label=f"Ellipse: a = {A_AX:.0f}″, b = {B_AX:.0f}″")
    for L, ang, col in [(A_AX, pa, "c"), (B_AX, pa + np.pi / 2, "m")]:
        ax.plot([xm - L * np.sin(ang), xm + L * np.sin(ang)], [ym - L * np.cos(ang), ym + L * np.cos(ang)], color=col, lw=1.5)
    ax.set_xlim(260, -260)
    ax.set_ylim(-220, 220)
    ax.set_xlabel("ξ [″] (Osten links)")
    ax.set_ylabel("η [″]")
    ax.set_title("Nebelmaske (gelb) und Ellipse gleicher Momente", fontsize=10)
    ax.legend(fontsize=9, loc="lower left")
    ax = axes[1]
    dd = np.linspace(800, 4000, 600)
    pdf = lambda p, s: np.exp(-0.5 * ((1000 / dd - p) / s) ** 2) * 1000 / dd ** 2      # Gauß in der Parallaxe -> Dichte in d
    for (p, s), lab, col in [((plx, eplx), "Gaia DR3 (Pulsar)", "tab:blue"), ((0.53, 0.06), "VLBI, Lin et al. (2023)", "tab:green")]:
        y = pdf(p, s)
        ax.plot(dd, y / y.max(), color=col, lw=2, label=f"{lab}: {1000 / p:.0f} pc")
    y = np.exp(-0.5 * ((dd - D_EXP) / (rel * D_EXP)) ** 2)
    ax.plot(dd, y, color="tab:red", lw=2, label=f"Expansionsparallaxe (eigene Messung): {D_EXP:.0f} pc")
    ax.axvline(2000, color="grey", ls=":", label="üblicher Wert 2 kpc (Trimble 1973)")
    ax.set_xlabel("Entfernung d [pc]")
    ax.set_ylabel("Wahrscheinlichkeitsdichte (Maximum = 1)")
    ax.set_title("Entfernung des Krebsnebels", fontsize=10)
    ax.legend(fontsize=9)
    fig.tight_layout()
    plt.show()


def pulsar():
    """67. Der Pulsar bremst (Zellen 46 von nebulae_crab.ipynb)."""
    global B_EQ, EDOT, GLITCH, JB, P, Pdot, TAU_C, ax, axes, big, dsec, fig
    global g, j, jumps, k, line, m, ndig, now, nu, nud, p, pred
    global rows, t
    rows = []
    for p in JB_FILES:
        for line in p.read_text(encoding="latin-1").splitlines():
            t = line.split()
            if len(t) < 8 or not re.fullmatch(r"\d{2}", t[0]) or not re.fullmatch(r"\d{5}", t[3]):
                continue
            k = next((i for i, s in enumerate(t) if re.fullmatch(r"\d{2}\.\d{9,11}", s)), None)   # die Frequenz, z. B. 29.5340803404
            if k is None:
                continue
            ndig = len(t[k].split(".")[1])
            rows.append(dict(mjd=int(t[3]), nu=float(t[k]), s_nu=float(t[k + 1]) * 10.0 ** -ndig,
                             nudot=float(t[k + 2]) * 1e-15, s_nudot=float(t[k + 3]) * 1e-15))
    JB = pd.DataFrame(rows).drop_duplicates("mjd").sort_values("mjd").reset_index(drop=True)
    JB["year"] = Time(JB["mjd"].values, format="mjd").decimalyear

    # Glitches: Frequenz liegt mehr als 1e-7 Hz über der Vorhersage aus dem Vormonat; ein Ereignis pro 60 Tage
    dsec = JB["mjd"].diff().values * 86400
    pred = JB["nu"].shift(1) + 0.5 * (JB["nudot"].shift(1) + JB["nudot"]) * dsec
    JB["jump"] = JB["nu"] - pred
    GLITCH = []
    for m, j in zip(JB["mjd"], JB["jump"]):
        if j > 1e-7 and (not GLITCH or m - GLITCH[-1] > 60):
            GLITCH.append(m)
    GLITCH = np.array(GLITCH)

    now = JB.iloc[-1]
    nu, nud = now["nu"], now["nudot"]
    P, Pdot = 1 / nu, -nud / nu ** 2
    EDOT = 4 * np.pi ** 2 * I_NS * nu * -nud
    TAU_C = nu / (-2 * nud) / YEAR
    B_EQ = 3.2e19 * np.sqrt(P * Pdot)
    print(f"{len(JB)} Monatswerte von {Time(JB['mjd'].min(), format='mjd').iso[:10]} bis {Time(JB['mjd'].max(), format='mjd').iso[:10]}; "
          f"Fehler typisch {JB['s_nu'].median():.0e} Hz in ν und {JB['s_nudot'].median():.0e} Hz/s in ν̇")
    print(f"ν: {JB['nu'].iloc[0]:.6f} Hz -> {nu:.6f} Hz (Verlust {JB['nu'].iloc[0] - nu:.4f} Hz in {now['year'] - JB['year'].iloc[0]:.1f} Jahren)")
    print(f"Heute: P = {P * 1e3:.4f} ms, Ṗ = {Pdot:.3e} s/s, die Periode wächst also um {Pdot * 86400 * 1e9:.0f} Nanosekunden pro Tag")
    print(f"Ė = 4π² I ν |ν̇| = {EDOT:.2e} erg/s = {EDOT / 3.828e33:.1e} Sonnenleuchtkräfte (I = {I_NS:.0e} g cm²)")
    print(f"charakteristisches Alter τ_c = ν / (2|ν̇|) = {TAU_C:.0f} Jahre (wahres Alter {now['year'] - T_SN:.0f} Jahre); B = {B_EQ:.2e} G")
    print(f"Glitches (Sprung > 1e-7 Hz): {len(GLITCH)}, in den Jahren {', '.join(f'{y:.1f}' for y in Time(GLITCH, format='mjd').decimalyear)}")
    big = JB.loc[JB["jump"].idxmax()]
    print(f"größter Sprung: {big['jump'] * 1e6:.1f} µHz (Δν/ν = {big['jump'] / big['nu']:.1e}) im Jahr {big['year']:.1f}")

    fig, axes = plt.subplots(1, 2, figsize=(16, 5.6))
    ax = axes[0]
    ax.plot(JB["year"], JB["nudot"] * 1e10, "k.", ms=3)
    for g in Time(GLITCH, format="mjd").decimalyear:
        ax.axvline(g, color="tab:red", lw=0.8, alpha=0.6)
    ax.set_xlabel("Jahr")
    ax.set_ylabel("ν̇ [10⁻¹⁰ Hz/s]")
    ax.set_title("Abbremsung ν̇ (rote Linien: Glitches)", fontsize=10)
    ax = axes[1]
    jumps = JB.set_index("mjd").loc[GLITCH, "jump"]
    ax.stem(Time(GLITCH, format="mjd").decimalyear, jumps.values / JB["nu"].mean(), linefmt="tab:red", markerfmt="o", basefmt=" ")
    ax.set_yscale("log")
    ax.set_xlim(JB["year"].min(), JB["year"].max() + 0.5)
    ax.set_xlabel("Jahr")
    ax.set_ylabel("Δν/ν (Sprung gegen die Vorhersage aus dem Vormonat)")
    ax.set_title("Größe der gefundenen Glitches", fontsize=10)
    fig.tight_layout()
    plt.show()


def braking_index():
    """68. Bremsindex und Anfangsperiode (Zellen 49 von nebulae_crab.ipynb)."""
    global AGE, E_ROT, N_ALL, N_BRAKE, P0, P0_BEST, Pt, SEG, ax, axes, braking_segments, col
    global fig, g, n, p0_from, pw, tw, yrs
    def braking_segments(skip=150, min_span=500):
        # in jedem Abschnitt zwischen zwei Glitches: Gerade an nu-dot(t) -> nu-ddot, daraus n = nu nu-ddot / nu-dot²
        edges = np.r_[JB["mjd"].min() - 1, GLITCH, JB["mjd"].max() + 1]
        out = []
        for a_, b_ in zip(edges[:-1], edges[1:]):
            s = JB[(JB["mjd"] >= a_ + (skip if a_ in GLITCH else 0)) & (JB["mjd"] < b_ - 1)]
            if len(s) < 8 or s["mjd"].max() - s["mjd"].min() < min_span:
                continue
            t = (s["mjd"] - s["mjd"].mean()).values * 86400
            p = np.polyfit(t, s["nudot"], 1)
            res = s["nudot"] - np.polyval(p, t)
            err = np.sqrt(np.sum(res ** 2) / (len(s) - 2) / np.sum((t - t.mean()) ** 2))
            nu_m = s["nu"].mean()
            out.append(dict(start=s["year"].min(), end=s["year"].max(), n_pts=len(s), nuddot=p[0],
                            n=nu_m * p[0] / p[1] ** 2, n_err=nu_m * err / p[1] ** 2))
        return pd.DataFrame(out)


    SEG = braking_segments()
    N_BRAKE = SEG["n"].median()
    tw = (JB["mjd"] - JB["mjd"].mean()).values * 86400
    pw = np.polyfit(tw, JB["nudot"], 1)
    N_ALL = JB["nu"].mean() * pw[0] / pw[1] ** 2
    print(SEG.round({"start": 1, "end": 1, "n": 3, "n_err": 3}).to_string(index=False, formatters={"nuddot": "{:.3e}".format}))
    print(f"Bremsindex zwischen Glitches: Median {N_BRAKE:.2f} (Abschnitte {SEG['n'].min():.2f} bis {SEG['n'].max():.2f}); "
          f"über alle {now['year'] - JB['year'].iloc[0]:.0f} Jahre mit Glitches: {N_ALL:.2f}")

    AGE = now["year"] - T_SN
    def p0_from(n):
        # P0 aus P, Ṗ, n und dem bekannten Alter: Alter = P / ((n - 1) Ṗ) · [1 - (P0 / P)^(n - 1)]
        return P * (1 - AGE * YEAR * (n - 1) * Pdot / P) ** (1 / (n - 1))
    E_ROT = {}
    for n in (N_BRAKE, N_ALL, 3.0):
        P0 = p0_from(n)
        E_ROT[n] = 2 * np.pi ** 2 * I_NS * (1 / P0 ** 2 - 1 / P ** 2)
        print(f"n = {n:.2f}: Anfangsperiode P0 = {P0 * 1e3:.1f} ms ({1 / P0:.0f} Umdrehungen pro Sekunde), "
              f"seit 1054 abgegebene Rotationsenergie {E_ROT[n]:.2e} erg")
    P0_BEST = p0_from(N_BRAKE)

    fig, axes = plt.subplots(1, 2, figsize=(16, 5.6))
    ax = axes[0]
    ax.errorbar((SEG["start"] + SEG["end"]) / 2, SEG["n"], xerr=(SEG["end"] - SEG["start"]) / 2, yerr=SEG["n_err"],
                fmt="o", color="k", capsize=3, label="Abschnitt zwischen zwei Glitches")
    ax.axhline(3, color="tab:blue", ls="--", label="Dipol im Vakuum: n = 3")
    ax.axhline(2.50, color="tab:green", ls=":", lw=2, label="Lyne et al. (2015): n = 2.50 zwischen Glitches")
    ax.axhline(N_ALL, color="tab:red", ls="-.", label=f"eine Gerade über alles: n = {N_ALL:.2f}")
    for g in Time(GLITCH, format="mjd").decimalyear:
        ax.axvline(g, color="tab:red", lw=0.6, alpha=0.4)
    ax.set_xlabel("Jahr")
    ax.set_ylabel("Bremsindex n = ν ν̈ / ν̇²")
    ax.set_ylim(2.0, 3.1)
    ax.set_title("Bremsindex aus 44 Jahren Jodrell Bank", fontsize=10)
    ax.legend(fontsize=8, loc="upper left")
    ax = axes[1]
    yrs = np.linspace(T_SN, now["year"], 300)
    for n, col in [(N_BRAKE, "k"), (N_ALL, "tab:red"), (3.0, "tab:blue")]:
        P0 = p0_from(n)
        # P(t) aus dem Bremsgesetz: P^(n-1) wächst linear mit der Zeit
        Pt = (P0 ** (n - 1) + (P ** (n - 1) - P0 ** (n - 1)) * (yrs - T_SN) / AGE) ** (1 / (n - 1))
        ax.plot(yrs, Pt * 1e3, color=col, lw=2, label=f"n = {n:.2f}: P0 = {P0 * 1e3:.1f} ms")
    ax.plot(JB["year"], 1e3 / JB["nu"], "o", color="orange", ms=2, label="Jodrell Bank 1982–2026")
    ax.set_xlabel("Jahr")
    ax.set_ylabel("Periode P [ms]")
    ax.set_title("Wie schnell drehte sich der Pulsar seit 1054?", fontsize=10)
    ax.legend(fontsize=9)
    fig.tight_layout()
    plt.show()


def literature():
    """69. Das Konvergenzjahr gegen die Literatur (Zellen 52 von nebulae_crab.ipynb)."""
    global BETA, LIT, ax, axes, bb, cols, dbeta, fig, fmt_err, fmt_year, i, own
    global row_, t1, tc_of, v_hom
    LIT = pd.DataFrame([
        ("Duncan (1939)", 1172, np.nan, "kleinste Streuung"),
        ("Trimble (1968)", 1140, 15, "kleinste Streuung"),
        ("Wyckoff & Murray (1977)", 1120, 7, "Fit an Trimbles Daten"),
        ("Nugent (1998)", 1130, 16, "kleinste Streuung"),
        ("Rudie et al. (2008), nur Jet", 1055, 24, "Fit"),
        ("Bietenholz & Nugent (2015)", 1091, 34, "Bayes, Daten von Nugent"),
        ("Martin et al. (2025)", 1140.5, 1.4, "kleinste Streuung"),
        ("Martin et al. (2025)", 1105.5, 0.5, "Fit"),
        ("eigene Messung", round(t_ca), np.nan, "kleinste Streuung"),
        ("eigene Messung", round(T0), np.hypot(P60["t0_err"], T0_SYS), "Fit"),
    ], columns=["Quelle", "Jahr", "Fehler", "Methode"])
    fmt_year = lambda x: f"{x:.1f}" if x % 1 else f"{x:.0f}"
    fmt_err = lambda x: "–" if not np.isfinite(x) else (f"{x:.1f}" if x < 2 else f"{x:.0f}")
    print(LIT.to_string(index=False, na_rep="–", formatters={"Jahr": fmt_year, "Fehler": fmt_err}))

    t1 = EPOCH["POSS-I E"]
    BETA = np.log(1 - P60["k"]) / np.log((t1 - T_SN) / (t2 - T_SN))
    dbeta = np.std([np.log(1 - P60["dt"] / (t2 - t)) / np.log((t1 - T_SN) / (t2 - T_SN)) for t in rng.normal(T0, np.hypot(P60["t0_err"], T0_SYS), 2000)])
    v_hom = 1 / (t2 - T_SN)
    print(f"Beschleunigung: β = {BETA:.3f} ± {dbeta:.3f}; die Filamente sind heute {100 * (BETA - 1):.1f} % schneller als im Mittel seit 1054")
    print(f"Zum Vergleich: Bietenholz & Nugent (2015) β = 1.040 ± 0.039; Martin et al. (2025) v/v_h = 1.06 "
          f"(eigene Messung im selben Maß: {(t2 - T_SN) / (t2 - T0):.3f})")

    fig, axes = plt.subplots(1, 2, figsize=(16, 5.8), gridspec_kw={"width_ratios": [1.4, 1]})
    ax = axes[0]
    cols = {"kleinste Streuung": "tab:blue", "Fit": "tab:red", "Fit an Trimbles Daten": "tab:red", "Bayes, Daten von Nugent": "tab:purple"}
    for i, row_ in LIT.iterrows():
        own = row_["Quelle"] == "eigene Messung"
        ax.errorbar(row_["Jahr"], i, xerr=row_["Fehler"] if np.isfinite(row_["Fehler"]) else None, fmt="*" if own else "o",
                    ms=14 if own else 7, color=cols[row_["Methode"]], capsize=3)
    ax.set_yticks(range(len(LIT)), [f"{q} – {m}" for q, m in zip(LIT["Quelle"], LIT["Methode"])], fontsize=9)
    ax.invert_yaxis()
    ax.axvline(T_SN, color="grey", ls=":", lw=2)
    ax.text(T_SN + 2, len(LIT) - 0.6, "SN 1054", color="grey", fontsize=9)
    ax.set_xlabel("Konvergenzjahr")
    ax.set_title("Konvergenzjahre der Filamente (blau: kleinste Streuung, rot: Fit)", fontsize=10)
    ax = axes[1]
    tc_of = lambda b: t2 - P60["dt"] / (1 - ((t1 - T_SN) / (t2 - T_SN)) ** b)  # Konvergenzjahr, das unsere Epochen bei gegebenem β messen
    bb = np.linspace(1.0, 1.10, 200)
    ax.plot(bb, tc_of(bb), "k-", lw=2, label="Konvergenzjahr bei r ∝ (t − 1054)^β")
    ax.errorbar(BETA, T0, xerr=dbeta, yerr=np.hypot(P60["t0_err"], T0_SYS), fmt="*", ms=14, color="tab:red", capsize=3,
                label=f"eigene Messung: β = {BETA:.3f}")
    ax.errorbar(1.040, tc_of(1.040), xerr=0.039, fmt="s", color="tab:purple", capsize=3, label="Bietenholz & Nugent (2015): β = 1.040")
    ax.plot(1.06, 1105.5, "o", color="tab:green", ms=8, label="Martin et al. (2025): v/v_h = 1.06, Fit 1105.5")
    ax.axhline(T_SN, color="grey", ls=":", lw=2)
    ax.set_xlabel("Exponent β (heutige Geschwindigkeit / mittlere seit 1054)")
    ax.set_ylabel("Konvergenzjahr")
    ax.set_title("Wie viel Beschleunigung steckt im Konvergenzjahr?", fontsize=10)
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    plt.show()


def energy():
    """70. Energiebilanz: Kann der Pulsar die Filamente beschleunigen? (Zellen 55 von nebulae_crab.ipynb)."""
    global DE_ACC, DE_ERR, E_KIN, E_KIN_ERR, E_R, L_SYN, ax, col, d, err, fig, i
    global items, lab, v2, v_perp, val
    d = P60["df"][P60["keep"]]
    v_perp = np.hypot(d["dxi"], d["deta"]) / dt60 * 4.74 * D_GAIA                 # km/s quer zur Sichtlinie
    v2 = 1.5 * np.mean(v_perp ** 2) * 1e10                                        # (cm/s)², räumlich
    E_KIN = 0.5 * M_FIL[0] * M_SUN * v2
    E_KIN_ERR = E_KIN * np.hypot(M_FIL[1] / M_FIL[0], 0.2)
    DE_ACC = E_KIN * (1 - 1 / BETA ** 2)
    DE_ERR = np.hypot(DE_ACC * E_KIN_ERR / E_KIN, E_KIN * 2 * dbeta / BETA ** 3)
    L_SYN = 1.3e38
    E_R = E_ROT[N_BRAKE]
    print(f"Geschwindigkeit quer zur Sichtlinie (d = {D_GAIA:.0f} pc): Median {np.median(v_perp):.0f} km/s, höchste {v_perp.max():.0f} km/s; "
          f"räumlich rms {np.sqrt(v2) / 1e5:.0f} km/s")
    print(f"Bewegungsenergie der Filamente: {E_KIN:.1e} ± {E_KIN_ERR:.1e} erg")
    print(f"davon durch Beschleunigung (β = {BETA:.3f}): {DE_ACC:.1e} ± {DE_ERR:.1e} erg")
    print(f"Rotationsenergie, die der Pulsar seit 1054 verloren hat (n = {N_BRAKE:.2f}): {E_R:.1e} erg "
          f"-> Anteil der Beschleunigung {DE_ACC / E_R:.0%}")
    print(f"Synchrotronleistung heute {L_SYN:.1e} erg/s = {L_SYN / EDOT:.0%} von Ė; über {AGE:.0f} Jahre bei heutiger Leistung "
          f"{L_SYN * AGE * YEAR:.1e} erg")

    items = [("Rotationsenergie, seit 1054\nverloren (Pulsar)", E_R, 0.5 * E_R, "tab:blue"),
             ("Bewegungsenergie der\nFilamente heute", E_KIN, E_KIN_ERR, "tab:orange"),
             ("davon durch Beschleunigung\nseit 1054", DE_ACC, DE_ERR, "tab:red"),
             ("Synchrotronstrahlung,\nheutige Leistung × Alter", L_SYN * AGE * YEAR, 0.5 * L_SYN * AGE * YEAR, "tab:purple"),
             ("Ė heute × 1 Jahr", EDOT * YEAR, 0, "grey")]
    fig, ax = plt.subplots(figsize=(12, 5.2))
    for i, (lab, val, err, col) in enumerate(items):
        ax.barh(i, val, color=col, alpha=0.8)
        if err:
            ax.errorbar(val, i, xerr=[[min(err, 0.9 * val)], [err]], color="k", capsize=4)
        ax.text(val * 1.15 + (err or 0), i, f"{val:.1e} erg", va="center", fontsize=9)
    ax.set_xscale("log")
    ax.set_xlim(1e45, 1e51)
    ax.set_yticks(range(len(items)), [it[0] for it in items], fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Energie [erg]")
    ax.set_title("Energiebilanz des Krebsnebels (Fehlerbalken: Masse, Trägheitsmoment, β)", fontsize=10)
    fig.tight_layout()
    plt.show()
