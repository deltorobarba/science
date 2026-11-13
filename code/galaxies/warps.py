"""Warps in Galaxien in Kantenlage aus DECaLS-Bildern: Lage der Scheibe, Spine-Fit, Warp-Profil, Staub oder Geometrie, Stichprobe gegen den Katalog von Sánchez-Saavedra et al.

Für galaxies.ipynb aus galaxies_warps.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, image, orientation, spine_fit, warp_shape, dust_or_geometry, sample, sample_profiles.
Downloads und Cache: data/galaxies/ (`galdata.py`).
"""
import galdata                                        # zuerst: Cache-Ordner für astropy
import os
import socket
import urllib.request
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS
from astropy.wcs.utils import proj_plane_pixel_scales
from astropy.stats import sigma_clipped_stats
from astroquery.simbad import Simbad
from scipy import ndimage
from scipy.optimize import curve_fit
from functools import lru_cache
from IPython.display import display


def load():
    """23. Daten (Zellen 5, 7 von galaxies_warps.ipynb)."""
    global ASTRODATA, BIN, C_KMS, DEMO, EBENEN, GALAXY, H0, NPIX_MAX, PIXSCALE, REFRESH, R_INNER, SNR_MIN
    global ax, axes, ebene, fig, fn, half, maj, pix, r, s, size_arcsec, titel
    global url
    ASTRODATA = galdata.DATA
    (ASTRODATA / "decals").mkdir(parents=True, exist_ok=True)
    (ASTRODATA / "vizier").mkdir(parents=True, exist_ok=True)
    socket.setdefaulttimeout(60)                        # ein hängender Server soll das Notebook nicht anhalten


    GALAXY   = "ESO 240-011"
    DEMO     = False      # True: synthetische Galaxien statt Download
    REFRESH  = False      # True: FITS-Dateien und Katalog neu laden
    PIXSCALE = 0.262      # natives Pixelmaß von DECam ["/px]
    NPIX_MAX = 800        # größere Galaxien werden gröber abgetastet
    H0, C_KMS = 70.0, 299792.458   # nur, wenn SIMBAD keine Entfernung ohne Rotverschiebung kennt
    SNR_MIN  = 5.0        # Mindest-SNR pro Spalte
    BIN      = 3          # Spalten zusammenfassen [px]
    R_INNER  = 0.3        # Referenzbereich: |R| < R_INNER * R_max
    pd.set_option("display.width", 160)

    # Farbbilder (JPEG) aus dem Legacy-Survey-Viewer, nur zur Ansicht; Ebene: (Titel, Pixelmaß ["/px])
    EBENEN = {
        "galex":       ("UV (GALEX FUV, NUV): junge Sterne", 1.5),
        "ls-dr10":     ("optisch (DECam g, r, z): Sternlicht, Staub", None),
        "unwise-neo7": ("3.4 und 4.6 µm (unWISE): alte Sterne", 2.75),
        "wssa":        ("12 µm (WISE): warmer Staub", 5.0),
    }

    if DEMO:
        print("Im Demo-Modus gibt es keine Himmelsbilder.")
    else:
        s = Simbad()
        s.add_votable_fields("galdim_majaxis")
        r = s.query_object(GALAXY)
        maj = np.nan if np.ma.is_masked(r["galdim_majaxis"][0]) else float(r["galdim_majaxis"][0])
        size_arcsec = 1.6 * 60 * (maj if np.isfinite(maj) else 3)       # Feld wie bei den FITS-Ausschnitten
        half = size_arcsec / 120                                         # halbe Feldbreite [']
        fig, axes = plt.subplots(1, len(EBENEN), figsize=(16, 4.4))
        for ax, (ebene, (titel, pix)) in zip(axes, EBENEN.items()):
            pix = pix or max(PIXSCALE, round(size_arcsec / NPIX_MAX, 3))
            fn = ASTRODATA / "decals" / f"{GALAXY.replace(' ', '_')}_{ebene}.jpg"
            if REFRESH or not fn.exists():
                url = (f"https://www.legacysurvey.org/viewer/jpeg-cutout?ra={float(r['ra'][0]):.6f}&dec={float(r['dec'][0]):.6f}"
                       f"&layer={ebene}&pixscale={pix}&size={int(size_arcsec / pix)}")
                try:
                    urllib.request.urlretrieve(url, fn)
                except OSError:
                    fn.unlink(missing_ok=True)
                    ax.set_title(f"{titel}\n(nicht verfügbar)", fontsize=9)
                    ax.axis("off")
                    continue
            ax.imshow(plt.imread(fn), extent=[half, -half, -half, half])   # Zeilen des JPG laufen von Norden nach Süden
            ax.set_title(titel, fontsize=9)
            ax.set_xlabel("ΔRA [']")
        axes[0].set_ylabel("ΔDec [']")
        fig.suptitle(f"{GALAXY} in vier Wellenlängenbereichen", y=1.0)
        fig.tight_layout()
        plt.show()


def image():
    """24. Bild und Katalogdaten laden (Zellen 10 von galaxies_warps.ipynb)."""
    global DEMO_CASES, GALAXY, d_hubble, demo_galaxy, ext, hi, img, info, legacy_cutout, lo, load_galaxy, pix
    global simbad_info, wcs
    @lru_cache
    def simbad_info(name):
        s = Simbad()
        s.add_votable_fields("rvz_redshift", "galdim_majaxis", "galdim_angle")
        r = s.query_object(name)
        g = lambda k: np.nan if np.ma.is_masked(r[k][0]) else float(r[k][0])
        info = dict(ra=g("ra"), dec=g("dec"), z=g("rvz_redshift"), maj_arcmin=g("galdim_majaxis"), pa_cat=g("galdim_angle"))
        # Entfernungen, die nicht aus der Rotverschiebung stammen (meist Tully-Fisher)
        d = Simbad.query_tap(f"""SELECT m.dist, m.unit, m.method FROM mesDistance AS m
                             JOIN basic AS b ON b.oid = m.oidref WHERE b.main_id = '{r["main_id"][0]}'""").to_pandas()
        d = d[d["method"].str.strip() != "redshift"]
        d_mpc = (d["dist"] * d["unit"].str.strip().map({"Mpc": 1.0, "kpc": 1e-3, "pc": 1e-6})).dropna()
        if len(d_mpc):
            info["D_Mpc"], info["D_quelle"] = d_mpc.median(), f"Median aus {len(d_mpc)} Messungen ohne Rotverschiebung"
        else:
            info["D_Mpc"], info["D_quelle"] = C_KMS * info["z"] / H0, "cz/H0"
        return info

    def legacy_cutout(name, info, band="r"):
        size_arcsec = 1.6 * 60 * (info["maj_arcmin"] if np.isfinite(info["maj_arcmin"]) else 3)
        pix = max(PIXSCALE, round(size_arcsec / NPIX_MAX, 3))
        npix = int(size_arcsec / pix)
        fn = ASTRODATA / "decals" / f"{name.replace(' ', '_')}_{band}.fits"
        if REFRESH or not fn.exists():
            for layer in ("ls-dr10", "ls-dr9"):
                url = (f"https://www.legacysurvey.org/viewer/fits-cutout?ra={info['ra']:.6f}&dec={info['dec']:.6f}"
                       f"&layer={layer}&pixscale={pix}&size={npix}&bands={band}")
                try:
                    urllib.request.urlretrieve(url, fn)
                except OSError:                         # außerhalb der Abdeckung antwortet der Server mit Fehler 500
                    continue
                if np.nanmax(fits.getdata(fn)) > 0:     # nur Nullen: keine Abdeckung in dieser Ebene
                    break
            else:
                fn.unlink(missing_ok=True)
                raise RuntimeError(f"keine Legacy-Survey-Daten im {band}-Band")
        hdu = fits.open(fn)[0]
        return np.nan_to_num(hdu.data.astype(float)), WCS(hdu.header)

    def demo_galaxy(amp_O=6.0, amp_W=-6.0, pa=40.0, seed=1):
        # Exponentielle Scheibe mit sech²-Profil, Warp quadratisch ab R = 60 px (Amplituden in px)
        rng = np.random.default_rng(seed); n = 500; h, z0, Rw, Rm = 40.0, 4.0, 60.0, 160.0
        y, x = np.mgrid[:n, :n] - n / 2
        t = np.radians(pa - 90)                       # Bild: Norden oben, Osten links; R < 0 ist die Ostseite
        R = x * np.cos(t) + y * np.sin(t); Z = -x * np.sin(t) + y * np.cos(t)
        w = np.clip((np.abs(R) - Rw) / (Rm - Rw), 0, None) ** 2
        zc = np.where(R < 0, amp_O, amp_W) * w
        img = 200 * np.exp(-np.abs(R) / h) / np.cosh((Z - zc) / z0) ** 2
        for _ in range(25):                           # ein paar Sterne
            sx, sy = rng.uniform(-n/2, n/2, 2); img += rng.uniform(5, 200) * np.exp(-((x-sx)**2 + (y-sy)**2) / 4)
        img += rng.normal(0, 1.5, img.shape)
        w_ = WCS(naxis=2); w_.wcs.ctype = ["RA---TAN", "DEC--TAN"]; w_.wcs.crpix = [n/2+1, n/2+1]
        w_.wcs.crval = [150.0, -45.0]; w_.wcs.cdelt = [-PIXSCALE/3600, PIXSCALE/3600]
        info = dict(ra=150.0, dec=-45.0, z=0.01, maj_arcmin=n*PIXSCALE/60*0.8, pa_cat=pa,
                    D_Mpc=C_KMS * 0.01 / H0, D_quelle="cz/H0")
        return img, w_, info

    def load_galaxy(name, band="r"):
        if DEMO:
            img, wcs, info = demo_galaxy(**DEMO_CASES[name])
        else:
            info = dict(simbad_info(name))
            img, wcs = legacy_cutout(name, info, band)
        pix = proj_plane_pixel_scales(wcs)[0] * 3600                       # ["/px]
        info["kpc_per_px"] = info["D_Mpc"] * 1e3 * np.radians(pix / 3600)
        return img, wcs, pix, info

    DEMO_CASES = {"demo_S": dict(amp_O=6, amp_W=-6), "demo_U": dict(amp_O=6, amp_W=6, pa=120),
                  "demo_L": dict(amp_O=0, amp_W=7, pa=75), "demo_flach": dict(amp_O=0, amp_W=0, pa=10)}
    if DEMO: GALAXY = "demo_S"

    img, wcs, pix, info = load_galaxy(GALAXY)
    print(f"{GALAXY}: RA {info['ra']:.4f}, Dec {info['dec']:+.4f}, z = {info['z']:.5f}, große Achse {info['maj_arcmin']:.1f}'")
    d_hubble = "" if info["D_quelle"] == "cz/H0" else f"; cz/H0 = {C_KMS * info['z'] / H0:.1f} Mpc"
    print(f"D = {info['D_Mpc']:.1f} Mpc ({info['D_quelle']}{d_hubble})")
    print(f"1 px = {pix:.3f}\" = {info['kpc_per_px']*1e3:.0f} pc, Bild {img.shape[1]} x {img.shape[0]} px")

    lo, hi = np.percentile(img, [5, 99.7])
    ext = np.array([-1, 1, -1, 1]) * img.shape[0] * pix / 120         # Bogenminuten vom Bildzentrum
    plt.figure(figsize=(5, 5))
    plt.imshow(np.arcsinh((img - lo) / (hi - lo) * 10), origin="lower", cmap="gray_r", extent=ext)
    plt.xlabel("Δx [′] (Osten links)"); plt.ylabel("Δy [′] (Norden oben)")
    plt.title(f"{GALAXY}, r-Band (arcsinh-Streckung)", fontsize=10); plt.show()


def orientation():
    """25. Himmel abziehen, Lage der Scheibe bestimmen, Bild drehen (Zellen 13 von galaxies_warps.ipynb)."""
    global bg_std, pa_own, r_max, reduce_image, rot
    def reduce_image(img, wcs):
        _, med, std = sigma_clipped_stats(img, sigma=3)
        im = img - med
        # Zusammenhängende Quelle, die die Bildmitte enthält (= Galaxie, keine Sterne)
        sm = ndimage.gaussian_filter(im, 2)            # geglättet -> tiefere Isophote
        lab, _ = ndimage.label(ndimage.binary_opening(sm > 3 * sigma_clipped_stats(sm, sigma=3)[2], iterations=2))
        cy, cx = np.array(im.shape) // 2
        center = lab[cy-5:cy+6, cx-5:cx+6].ravel()
        m = lab == np.bincount(center[center > 0]).argmax()
        # Schwerpunkt und zweite Momente der Helligkeit
        y, x = np.nonzero(m); f = im[m]
        xc, yc = np.average(x, weights=f), np.average(y, weights=f)
        mxx, myy = np.average((x-xc)**2, weights=f), np.average((y-yc)**2, weights=f)
        mxy = np.average((x-xc)*(y-yc), weights=f)
        theta = 0.5 * np.degrees(np.arctan2(2 * mxy, mxx - myy))   # Winkel der großen Achse gegen x
        # Positionswinkel am Himmel (Nord über Ost) über das WCS
        t = np.radians(theta)
        p1, p2 = wcs.pixel_to_world([xc, xc + 50*np.cos(t)], [yc, yc + 50*np.sin(t)])
        pa_t = p1.position_angle(p2).deg               # Himmelsrichtung, in die theta zeigt
        # ndimage.rotate legt die Richtung "angle" auf +x; das Ostende soll links liegen wie am Himmel
        angle = theta + 180 if pa_t < 180 else theta
        shift = (im.shape[0]/2 - yc, im.shape[1]/2 - xc)
        rot = ndimage.rotate(ndimage.shift(im, shift, order=1), angle, reshape=False, order=1)
        m_rot = ndimage.rotate(ndimage.shift(m.astype(float), shift, order=0), angle, reshape=False, order=0) > 0.5
        r_max = np.percentile(np.abs(np.nonzero(m_rot)[1] - im.shape[1]/2), 99)   # Ausdehnung der Isophote
        return rot, std, pa_t % 180, r_max

    rot, bg_std, pa_own, r_max = reduce_image(img, wcs)
    print(f"Himmelsrauschen: {bg_std:.3g} (Bildeinheiten)")
    print(f"PA = {pa_own:.1f} Grad (Katalog: {info['pa_cat']:.0f} Grad)")
    print(f"R_max (3-sigma-Isophote, geglättet) = {r_max:.0f} px = {r_max*info['kpc_per_px']:.1f} kpc")


def spine_fit():
    """26. Spine-Fit: Wo ist die Scheibe in jeder Spalte am hellsten? (Zellen 16 von galaxies_warps.ipynb)."""
    global ax, cx, cy, fig, fit_spine, gauss, hi, lo, ok, sc, spine, w
    def gauss(z, A, z0, s, c): return A * np.exp(-0.5 * ((z - z0) / s) ** 2) + c

    def fit_spine(rot, bg_std, r_max, zwin=None):
        ny, nx = rot.shape; cy, cx = ny // 2, nx // 2
        zwin = zwin or int(max(15, 0.25 * r_max))
        zz = np.arange(-zwin, zwin + 1)
        noise = bg_std / np.sqrt(BIN)                  # Rauschen nach Mittelung über BIN Spalten
        rows = []
        for x0 in range(cx - int(r_max), cx + int(r_max) - BIN + 1, BIN):
            prof = rot[cy - zwin:cy + zwin + 1, x0:x0 + BIN].mean(axis=1)
            try:
                p, _ = curve_fit(gauss, zz, prof, p0=[prof.max(), zz[prof.argmax()], 3, 0], maxfev=2000)
            except RuntimeError:
                continue
            rows.append(dict(R=x0 + BIN/2 - cx, z=p[1], sig=abs(p[2]), snr=p[0] / noise))
        sp = pd.DataFrame(rows)
        ok = (sp.snr > SNR_MIN) & (sp.z.abs() < 0.8 * zwin) & sp.sig.between(0.5, zwin / 2)
        # Sterne sind schmaler als die Scheibe: Breite mit der inneren Scheibe vergleichen
        sig_disk = sp.sig[ok & (sp.R.abs() < R_INNER * r_max)].median()
        ok &= sp.sig > 0.6 * sig_disk
        # restliche Ausreißer gegen den gleitenden Median der behaltenen Punkte entfernen
        z_ok = sp.z[ok]
        d = z_ok - z_ok.rolling(7, center=True, min_periods=3).median()
        ok[d.index[d.abs() > 4 * 1.4826 * np.median(np.abs(d)) + 0.5]] = False
        return sp, ok

    spine, ok = fit_spine(rot, bg_std, r_max)
    print(f"{len(spine)} Spalten gefittet, {ok.sum()} behalten (SNR > {SNR_MIN}, Ausreißer entfernt)")

    fig, ax = plt.subplots(1, 2, figsize=(11, 3.6))
    lo, hi = np.percentile(rot, [5, 99.7]); cy, cx = np.array(rot.shape) // 2; w = int(1.15 * r_max)
    ax[0].imshow(np.arcsinh((rot - lo) / (hi - lo) * 10)[cy - w//5:cy + w//5, cx - w:cx + w], origin="lower",
                 cmap="gray_r", extent=[-w, w, -w//5, w//5], aspect="auto")
    ax[0].plot(spine.R[ok], spine.z[ok], ".", ms=3, c="tab:red", label="Spine")
    ax[0].set_title("Gedrehtes Bild mit Spine", fontsize=10)
    ax[0].set_xlabel("R [px] (Osten links)"); ax[0].set_ylabel("z [px]"); ax[0].legend(fontsize=8)
    sc = ax[1].scatter(spine.R[ok], spine.z[ok], c=np.log10(spine.snr[ok]), s=8, cmap="viridis")
    ax[1].plot(spine.R[~ok], spine.z[~ok].clip(-20, 20), "x", c="0.7", ms=3, label="verworfen")
    plt.colorbar(sc, ax=ax[1], label="log₁₀ SNR"); ax[1].legend(fontsize=8)
    ax[1].set_title("Rohes z(R) aller Spalten", fontsize=10); ax[1].set_xlabel("R [px] (Osten links)"); ax[1].set_ylabel("z [px]")
    plt.tight_layout(); plt.show()


def warp_shape():
    """27. Referenzebene, Warp-Profil und Form (Zellen 19 von galaxies_warps.ipynb)."""
    global Rk, c, classify, label, r_in, res, sel, side, warp_profile, zw
    def warp_profile(spine, ok, r_max, kpc_per_px):
        s = spine[ok]
        inner = s.R.abs() < R_INNER * r_max
        a, b = np.polyfit(s.R[inner], s.z[inner], 1)
        zw = (s.z - (a * s.R + b)) / np.sqrt(1 + a**2) * kpc_per_px
        Rk = s.R * kpc_per_px
        scat = 1.4826 * np.median(np.abs(zw[inner] - np.median(zw[inner])))
        scat = max(scat, 0.25 * kpc_per_px)            # Untergrenze: 1/4 Pixel (Systematik)
        res = dict(a=a, b=b, scatter_kpc=scat)
        for side, sel in (("O", s.R < 0), ("W", s.R > 0)):               # Osten links, Westen rechts
            outer = sel & (s.R.abs() > 0.75 * s.R[sel].abs().max())      # äußerstes Viertel dieser Seite
            enough = outer.sum() >= 3
            res[f"amp_{side}"] = np.median(zw[outer]) if enough else np.nan
            res[f"R_{side}"] = np.median(Rk[outer].abs()) if enough else np.nan
            res[f"sig_{side}"] = abs(res[f"amp_{side}"]) / scat
            res[f"psi_{side}"] = np.degrees(np.arctan2(res[f"amp_{side}"], res[f"R_{side}"]))
        res["S"] = (res["amp_W"] - res["amp_O"]) / 2   # punktsymmetrischer Anteil
        res["U"] = (res["amp_W"] + res["amp_O"]) / 2   # spiegelsymmetrischer Anteil
        return Rk, zw, res

    def classify(res):
        sO, sW = res["sig_O"] > 2, res["sig_W"] > 2
        if sO and sW:
            kind = "S-Warp" if np.sign(res["amp_O"]) != np.sign(res["amp_W"]) else "U-Warp"
        elif sO or sW:
            kind = "L-Warp (einseitig)"
        else:
            return "kein Warp"
        return kind + (", klar" if max(res["sig_O"], res["sig_W"]) > 4 else ", schwach")

    Rk, zw, res = warp_profile(spine, ok, r_max, info["kpc_per_px"])
    res["klasse"] = classify(res)
    print(f"Innere Gerade: a = {res['a']:+.4f} (Restdrehung {np.degrees(np.arctan(res['a'])):+.2f} Grad), b = {res['b']:+.2f} px")
    print(f"Streuung innen s = {res['scatter_kpc']*1e3:.0f} pc")
    for side, label in (("O", "Ostseite"), ("W", "Westseite")):
        print(f"{label}: z_warp = {res['amp_' + side]*1e3:+.0f} pc ({res['sig_' + side]:.1f} s) bei R = {res['R_' + side]:.1f} kpc, "
              f"Warp-Winkel {res['psi_' + side]:+.1f} Grad")
    print(f"S-Anteil {abs(res['S'])*1e3:.0f} pc, U-Anteil {abs(res['U'])*1e3:.0f} pc  ->  {res['klasse']}")

    plt.figure(figsize=(6.5, 3.6))
    for label, sel, c in (("Ostseite", Rk < 0, "tab:blue"), ("Westseite", Rk > 0, "tab:orange")):
        plt.plot(Rk[sel], zw[sel], ".", c=c, ms=4, label=label)
    plt.axhline(0, c="k", lw=0.8)
    plt.axhspan(-2 * res["scatter_kpc"], 2 * res["scatter_kpc"], color="0.85", label="±2 s (innen)")
    r_in = R_INNER * r_max * info["kpc_per_px"]
    plt.axvspan(-r_in, r_in, color="tab:green", alpha=0.08, label="Referenzbereich")
    plt.xlabel("R [kpc] (Osten links)"); plt.ylabel(r"$z_\mathrm{warp}$ [kpc]")
    plt.title(rf"{GALAXY}: $z_\mathrm{{warp}} = [z-(aR+b)]/\sqrt{{1+a^2}}$  ->  {res['klasse']}", fontsize=10)
    plt.legend(fontsize=8); plt.tight_layout(); plt.show()


def dust_or_geometry():
    """28. Staub oder Geometrie? (Zellen 22 von galaxies_warps.ipynb)."""
    global Rk_b, band, c, res_b, warp_in_band, zw_b
    def warp_in_band(name, band):
        img_b, wcs_b, _, info_b = load_galaxy(name, band)
        rot_b, bg_b, _, rmax_b = reduce_image(img_b, wcs_b)
        sp_b, ok_b = fit_spine(rot_b, bg_b, rmax_b)
        return warp_profile(sp_b, ok_b, rmax_b, info_b["kpc_per_px"])

    if DEMO:
        print("Die Demo-Galaxien haben nur ein Band; dieser Schritt braucht echte Daten.")
    else:
        plt.figure(figsize=(6.5, 3.6))
        for band, c in (("g", "tab:blue"), ("r", "tab:green"), ("z", "tab:red")):
            Rk_b, zw_b, res_b = warp_in_band(GALAXY, band)
            plt.plot(Rk_b, zw_b, ".", c=c, ms=3, label=f"{band}-Band")
            print(f"{band}: Ost {res_b['amp_O']*1e3:+5.0f} pc, West {res_b['amp_W']*1e3:+5.0f} pc, "
                  f"s = {res_b['scatter_kpc']*1e3:3.0f} pc  ->  {classify(res_b)}")
        plt.axhline(0, c="k", lw=0.8)
        plt.xlabel("R [kpc] (Osten links)"); plt.ylabel(r"$z_\mathrm{warp}$ [kpc]")
        plt.title(f"{GALAXY}: Warp-Profil in drei Bändern", fontsize=10)
        plt.legend(fontsize=8); plt.tight_layout(); plt.show()


def sample():
    """29. Stichprobe und Warp-Katalog (Zellen 25 von galaxies_warps.ipynb)."""
    global SAMPLE, SS03, SS03_TYP, SS03_URL, analyse, e, name, profiles, row, rows, ss03_catalog, ss03_entry
    global tab
    SS03_URL = "https://cdsarc.cds.unistra.fr/ftp/J/A+A/399/457/"
    SS03_TYP = {"N": "S", "S": "S", "LN": "L", "LS": "L", "U": "U", "-": "kein", "?": "unklar"}   # N, S: Drehsinn des S

    def ss03_catalog():
        # Sánchez-Saavedra et al. (2003): Galaxien in Kantenlage südlich des Äquators, Warp-Winkel aus DSS-Bildern
        parts = []
        for t in ("table1.dat", "table2.dat"):                      # Spiralen, linsenförmige Galaxien
            fn = ASTRODATA / "vizier" / f"sanchez-saavedra2003_{t}"
            if REFRESH or not fn.exists():
                urllib.request.urlretrieve(SS03_URL + t, fn)
            parts.append(pd.read_fwf(fn, colspecs=[(6, 21), (22, 30), (31, 40), (56, 58), (59, 61), (63, 65)],
                                     names=["name", "ra_h", "dec", "typ", "psi_O", "psi_W"]))
        cat = pd.concat(parts, ignore_index=True)
        cat[["psi_O", "psi_W"]] = cat[["psi_O", "psi_W"]].apply(pd.to_numeric, errors="coerce")
        return cat

    def ss03_entry(cat, ra, dec):
        sep = np.hypot((cat.ra_h * 15 - ra) * np.cos(np.radians(dec)), cat.dec - dec) * 60      # Bogenminuten
        if sep.min() > 1:
            return "–"
        e = cat.loc[sep.idxmin()]
        angles = "" if np.isnan(e.psi_O) else f", {e.psi_O:.0f}° / {e.psi_W:.0f}°"
        return SS03_TYP.get(str(e.typ).strip(), str(e.typ)) + angles

    def analyse(name):
        img, wcs, pix, info = load_galaxy(name)
        rot, bg, pa, r_max = reduce_image(img, wcs)
        sp, ok = fit_spine(rot, bg, r_max)
        Rk, zw, res = warp_profile(sp, ok, r_max, info["kpc_per_px"])
        row = {"Galaxie": name, "D [Mpc]": round(info["D_Mpc"], 1),
               "PA eigen": round(pa, 1), "PA Katalog": info["pa_cat"], "R_max [kpc]": round(r_max * info["kpc_per_px"], 1),
               "Ost [pc]": round(res["amp_O"] * 1e3), "West [pc]": round(res["amp_W"] * 1e3),
               "s [pc]": round(res["scatter_kpc"] * 1e3),
               "ψ Ost/West [°]": f"{abs(res['psi_O']):.1f} / {abs(res['psi_W']):.1f}", "Klasse (r)": classify(res)}
        if not DEMO:
            try:
                row["Klasse (z)"] = classify(warp_in_band(name, "z")[2])
            except RuntimeError:                       # Lücken in der Abdeckung, z. B. IC 2531 ohne z-Band
                row["Klasse (z)"] = "kein z-Bild"
            row["SS03"] = ss03_entry(SS03, info["ra"], info["dec"])
        return row, (Rk, zw, res)

    if DEMO:
        SAMPLE = list(DEMO_CASES)
    else:
        SS03 = ss03_catalog()
        SAMPLE = ["ESO 240-011", "IC 2531", "IC 5176", "IC 4351", "IC 2000", "NGC 4013", "NGC 5907"]
    rows, profiles = [], {}
    for name in SAMPLE:
        try:
            row, profiles[name] = analyse(name)
            rows.append(row)
        except Exception as e:
            print(f"{name}: übersprungen ({e})")
    tab = pd.DataFrame(rows).set_index("Galaxie")
    if DEMO:
        tab.insert(0, "eingebaut", [f"O {DEMO_CASES[n].get('amp_O', 6):+g} / W {DEMO_CASES[n].get('amp_W', -6):+g} px" for n in tab.index])
    display(tab)


def sample_profiles():
    """30. Stichprobe und Warp-Katalog (Zellen 28 von galaxies_warps.ipynb)."""
    global Rk_g, ax, axs, fig, name, ncol, nrow, res_g, zw_g
    ncol = 2; nrow = int(np.ceil(len(profiles) / ncol))
    fig, axs = plt.subplots(nrow, ncol, figsize=(11, 2.7 * nrow), squeeze=False)
    for ax, (name, (Rk_g, zw_g, res_g)) in zip(axs.flat, profiles.items()):
        ax.plot(Rk_g[Rk_g < 0], zw_g[Rk_g < 0], ".", ms=3, c="tab:blue", label="Ostseite")
        ax.plot(Rk_g[Rk_g > 0], zw_g[Rk_g > 0], ".", ms=3, c="tab:orange", label="Westseite")
        ax.axhline(0, c="k", lw=0.8)
        ax.axhspan(-2 * res_g["scatter_kpc"], 2 * res_g["scatter_kpc"], color="0.88", label="±2 s (innen)")
        ax.set_title(f"{name}: {classify(res_g)}", fontsize=9)
        ax.set_xlabel("R [kpc] (Osten links)", fontsize=8); ax.set_ylabel(r"$z_\mathrm{warp}$ [kpc]", fontsize=8)
    for ax in axs.flat[len(profiles):]:
        ax.axis("off")
    axs[0, 0].legend(fontsize=7)
    fig.suptitle("Warp-Profile der Stichprobe im r-Band", fontsize=11)
    plt.tight_layout(); plt.show()
