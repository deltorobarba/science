"""Der Orionnebel vom Röntgen- bis zum Radiobereich: Bilder aus SkyView, Entfernung aus Gaia, Photometrie, frei-frei-Strahlung, Extinktion, Strömgren-Kugel, Spektrum, Staubtemperatur, junge Sterne.

Für nebulae.ipynb aus nebulae_orion.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, multiwavelength, color_images, distance, region_photometry, free_free, extinction, density, spectrum, dust_temperature, young_stars, literature.
Downloads und Cache: data/nebulae/ (`nebdata.py`).
"""
import nebdata                                         # zuerst: Cache-Ordner für astropy
import io
import os
import time
import warnings
import urllib.parse
import urllib.request
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy.io import fits
from scipy import ndimage, optimize


def load():
    """Daten (Zellen 4, 6 von nebulae_orion.ipynb)."""
    global ALPHA_B, ALPHA_HA, APER, ASTRODATA, BANDS, BG, CLOSE, CLOSEMAP, COLOR, COLS, C_SI, DE0
    global DISK_HILLENBRAND, DIST_REF, D_FROM_GAIA, GAIA, H_PL, IRSA_TAP, K_B, LSUN, MARTINS_V, MSUN, M_H, N_CLOSE
    global N_WIDE, ORION, PC_CM, PIX_WIDE, RA0, R_ARCMIN, SKYVIEW, TM_CTRL, TM_ONC, T_E, WIDE, WIDEMAP
    global dB_dT_cmb, fetch, mbb, photometry, planck, rgb, skyview, stretch, tap, to_jy_sr, xx, yy
    ASTRODATA = nebdata.DATA


    warnings.filterwarnings("ignore", message="Invalid 'BLANK' keyword")   # SkyView schreibt BLANK auch in Gleitkomma-Bilder

    RA0, DE0 = 83.8186, -5.3897                                   # θ¹ Ori C (SIMBAD)
    ORION = ASTRODATA / "orion"
    SKYVIEW = "https://skyview.gsfc.nasa.gov/current/cgi/runquery.pl?"
    IRSA_TAP = "https://irsa.ipac.caltech.edu/TAP/sync"
    H_PL, K_B, C_SI = 6.62607e-34, 1.380649e-23, 2.99792458e8
    PC_CM, LSUN, MSUN, M_H = 3.0857e18, 3.828e33, 1.989e33, 1.6726e-24
    ALPHA_B, ALPHA_HA = 2.59e-13, 1.17e-13                         # cm³/s bei 10⁴ K, Fall B
    T_E = 1.0e4
    WIDE, N_WIDE = 3.0, 360                                        # Übersicht: 3° mit 360 Pixeln (30″)
    CLOSE, N_CLOSE = 1.0, 800                                      # Farbbilder: 1° mit 800 Pixeln (4.5″)
    APER, BG = 40.0, (60.0, 85.0)                                  # Öffnung und Hintergrundring [′]
    # Band: (SkyView-Name, Frequenz [Hz], Einheit, Beschriftung)
    BANDS = {"ROSAT": ("RASS-Cnt Broad", None, "Zählrate", "ROSAT 0.1–2.4 keV"),
             "DSS2 R": ("DSS2 Red", None, "Zählwert", "DSS2 rot (0.65 µm)"),
             "Hα": ("SHASSA H", None, "dR", "SHASSA Hα (656 nm)"),
             "2MASS K": ("2MASS-K", None, "Zählwert", "2MASS K (2.2 µm)"),
             "WISE 3.4": ("WISE 3.4", None, "Zählwert", "WISE 3.4 µm"),
             "WISE 22": ("WISE 22", None, "Zählwert", "WISE 22 µm"),
             "IRIS 12": ("IRIS12", 25e12, "MJy/sr", "IRIS 12 µm"),
             "IRIS 25": ("IRIS25", 12e12, "MJy/sr", "IRIS 25 µm"),
             "IRIS 60": ("IRIS60", 5e12, "MJy/sr", "IRIS 60 µm"),
             "IRIS 100": ("IRIS100", 3e12, "MJy/sr", "IRIS 100 µm"),
             "Planck 857": ("Planck 857 I", 857e9, "MJy/sr", "Planck 857 GHz (350 µm)"),
             "Planck 545": ("Planck 545 I", 545e9, "MJy/sr", "Planck 545 GHz (550 µm)"),
             "Planck 353": ("Planck 353 I", 353e9, "K_CMB", "Planck 353 GHz (850 µm)"),
             "Planck 217": ("Planck 217 I", 217e9, "K_CMB", "Planck 217 GHz (1.4 mm)"),
             "Planck 70": ("Planck 070 I", 70.4e9, "K_CMB", "Planck 70 GHz (4.3 mm)"),
             "Planck 44": ("Planck 044 I", 44.1e9, "K_CMB", "Planck 44 GHz (6.8 mm)"),
             "Planck 28": ("Planck 030 I", 28.4e9, "K_CMB", "Planck 28 GHz (1 cm)"),
             "Bonn 1.4": ("1420MHz (Bonn)", 1.42e9, "mK", "Bonn 1.4 GHz (21 cm)"),
             "NVSS": ("NVSS", None, "Jy/beam", "NVSS 1.4 GHz (21 cm)")}
    COLOR = {"DSS2": ["DSS2 Red", "DSS2 Mitte", "DSS2 Blue"], "2MASS": ["2MASS-K", "2MASS-H", "2MASS-J"], "WISE": ["WISE 12", "WISE 4.6", "WISE 3.4"]}
    DIST_REF = {"Menten et al. 2007 (VLBA)": (414.0, 7.0), "Kounkel et al. 2017 (VLBA)": (388.0, 5.0)}
    # Martins et al. 2005, Tabelle 4 (Zwergsterne, beobachtete Temperaturskala): Typ, T_eff, log L/L☉, log Q₀
    MARTINS_V = pd.DataFrame([("O3", 44852, 5.84, 49.64), ("O4", 42857, 5.67, 49.44), ("O5", 40862, 5.49, 49.22), ("O5.5", 39865, 5.41, 49.10),
                              ("O6", 38867, 5.32, 48.99), ("O6.5", 37870, 5.23, 48.88), ("O7", 36872, 5.14, 48.75), ("O7.5", 35874, 5.05, 48.61),
                              ("O8", 34877, 4.96, 48.44), ("O8.5", 33879, 4.86, 48.27), ("O9", 32882, 4.77, 48.06), ("O9.5", 31884, 4.68, 47.88)],
                             columns=["typ", "teff", "logL", "logQ"])
    DISK_HILLENBRAND = (0.55, 0.90)                               # Anteil mit inneren Scheiben (I−K-Überschuss)


    def fetch(url, path, check, tries=5, pause=15, timeout=600):
        path = Path(path)
        if path.exists():
            return path
        path.parent.mkdir(parents=True, exist_ok=True)
        for _ in range(tries):
            try:
                with urllib.request.urlopen(url, timeout=timeout) as r:
                    data = r.read()
                if check(data):
                    path.write_bytes(data)
                    return path
            except OSError:
                pass
            time.sleep(pause)                                     # SkyView lehnt schnelle Folgeanfragen ab („Too Many Processes“)
        raise OSError(f"{path.name}: kein gültiger Download nach {tries} Versuchen")


    def skyview(survey, size, npix):
        q = urllib.parse.urlencode({"Position": f"{RA0},{DE0}", "Survey": survey, "Pixels": npix, "Size": size, "Return": "FITS"})
        name = survey.replace(" ", "_").replace("(", "").replace(")", "") + f"_{size:g}_{npix}.fits"
        with fits.open(fetch(SKYVIEW + q, ORION / name, lambda d: d.startswith(b"SIMPLE"))) as h:
            return h[0].data.astype(float)


    def tap(adql, path):
        url = IRSA_TAP + "?" + urllib.parse.urlencode({"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": adql})
        first = adql.split()[1].rstrip(",").encode()
        return pd.read_csv(fetch(url, path, lambda d: d.startswith(first)))


    WIDEMAP = {k: skyview(v[0], WIDE, N_WIDE) for k, v in BANDS.items()}
    CLOSEMAP = {s: skyview(s, CLOSE, N_CLOSE) for s in sorted({x for v in COLOR.values() for x in v} - {"DSS2 Mitte"})}
    CLOSEMAP["DSS2 Mitte"] = (CLOSEMAP["DSS2 Red"] + CLOSEMAP["DSS2 Blue"]) / 2   # künstlicher Grünkanal aus Rot und Blau
    GAIA = tap("SELECT source_id, ra, dec, parallax, parallax_error, ruwe, phot_g_mean_mag FROM gaia_dr3_source "
               f"WHERE CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {RA0}, {DE0}, 0.25)) = 1 AND parallax_over_error > 10 AND ruwe < 1.4",
               ORION / "gaia_onc.csv")
    COLS = "ra, dec, j_m, h_m, k_m, j_msigcom, h_msigcom, k_msigcom, ph_qual"
    TM_ONC = tap(f"SELECT {COLS} FROM fp_psc WHERE CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {RA0}, {DE0}, 0.17)) = 1", ORION / "2mass_onc.csv")
    TM_CTRL = tap(f"SELECT {COLS} FROM fp_psc WHERE CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {RA0 + 6}, {DE0}, 0.17)) = 1", ORION / "2mass_ctrl.csv")
    print(f"{len(WIDEMAP)} Übersichtskarten (3°), {len(CLOSEMAP)} Karten für Farbbilder (1°); Gaia: {len(GAIA)} Sterne bis 15′; "
          f"2MASS: {len(TM_ONC)} Quellen bis 10′ um das Trapez, {len(TM_CTRL)} im Vergleichsfeld")

    PIX_WIDE = np.radians(WIDE / N_WIDE)                            # Pixel in rad
    yy, xx = np.mgrid[:N_WIDE, :N_WIDE]
    R_ARCMIN = np.hypot(xx - N_WIDE / 2 + 0.5, yy - N_WIDE / 2 + 0.5) * WIDE / N_WIDE * 60


    def planck(nu, T):
        return 2 * H_PL * nu**3 / C_SI**2 / np.expm1(H_PL * nu / (K_B * T))      # W/m²/Hz/sr


    def dB_dT_cmb(nu, T=2.7255):
        x = H_PL * nu / (K_B * T)
        return 2 * K_B * nu**2 / C_SI**2 * x**2 * np.exp(x) / np.expm1(x) ** 2 * 1e26   # Jy/sr pro K


    def to_jy_sr(key):
        survey, nu, unit, _ = BANDS[key]
        x = WIDEMAP[key]
        if unit == "MJy/sr":
            return x * 1e6
        if unit == "K_CMB":
            return x * dB_dT_cmb(nu)
        if unit == "mK":
            return x * 1e-3 * 2 * K_B * nu**2 / C_SI**2 * 1e26                       # Rayleigh-Jeans
        raise ValueError(f"{key}: nicht geeicht")


    def photometry(img, radius=APER, ring=BG):
        # Fluss in der Öffnung minus Median des Rings; Fehler aus der Streuung des Hintergrunds zwischen 8 Sektoren des Rings
        ring_pix = (R_ARCMIN > ring[0]) & (R_ARCMIN < ring[1])
        inside = R_ARCMIN < radius
        flux = np.sum(img[inside] - np.median(img[ring_pix])) * PIX_WIDE**2
        sector = (np.degrees(np.arctan2(yy - N_WIDE / 2 + 0.5, xx - N_WIDE / 2 + 0.5)) % 360 // 45).astype(int)
        levels = [np.median(img[ring_pix & (sector == s)]) for s in range(8)]
        return flux, np.std(levels) * inside.sum() * PIX_WIDE**2


    def stretch(x, lo=1, hi=99.7, soft=0.1, gamma=1.0):
        a, b = np.nanpercentile(x, [lo, hi])
        y = np.clip((x - a) / (b - a), 0, 1)
        return (np.arcsinh(y / soft) / np.arcsinh(1 / soft)) ** gamma


    def rgb(keys, **kw):
        # übersättigte Pixel (NaN) als hellster Wert
        return np.dstack([np.nan_to_num(stretch(CLOSEMAP[k], **kw), nan=1.0) for k in keys])


    def mbb(nu, lnA, T, beta):
        return np.exp(lnA) * (nu / 1e12) ** beta * planck(nu, T) * 1e26                # Jy


    D_FROM_GAIA = None                                               # wird in Schritt 19 gesetzt
    print(f"Pixel der Übersicht {np.degrees(PIX_WIDE) * 3600:.0f}″, Öffnung {APER:.0f}′, Hintergrund {BG[0]:.0f}–{BG[1]:.0f}′")


def multiwavelength():
    """17. Der Orionnebel vom Röntgen- bis zum Radiobereich (Zellen 8 von nebulae_orion.ipynb)."""
    global ax, axs, dx, dy, ext, fig, i, img, j, key, show
    show = ["ROSAT", "DSS2 R", "Hα", "2MASS K", "WISE 3.4", "WISE 22", "IRIS 60", "IRIS 100", "Planck 857", "Planck 353", "Planck 28", "NVSS"]
    ext = [WIDE / 2 * 60, -WIDE / 2 * 60, -WIDE / 2 * 60, WIDE / 2 * 60]
    fig, axs = plt.subplots(3, 4, figsize=(17, 13))
    for ax, key in zip(axs.ravel(), show):
        img = WIDEMAP[key]
        ax.imshow(stretch(img, lo=1, hi=99.9, soft=0.05), origin="lower", extent=ext, cmap="inferno")
        ax.add_patch(plt.Circle((0, 0), APER, fill=False, color="w", lw=1, ls="--"))
        ax.plot(0, 0, "+", color="cyan", ms=10, mew=1.5)
        ax.set_title(BANDS[key][3], fontsize=10)
        ax.set_xticks([-60, 0, 60])
        ax.set_yticks([-60, 0, 60])
    for ax in axs[-1]:
        ax.set_xlabel("Rektaszension relativ [′]")
    for ax in axs[:, 0]:
        ax.set_ylabel("Deklination relativ [′]")
    plt.suptitle("Der Orionnebel in 12 Bändern (3° × 3°, Kreis: Öffnung von 40′, Kreuz: θ¹ Ori C)", fontsize=12)
    plt.tight_layout()
    plt.show()

    for key in show:
        img = WIDEMAP[key]
        j, i = np.unravel_index(np.nanargmax(np.where(R_ARCMIN < 30, img, -np.inf)), img.shape)
        dx, dy = -(i - N_WIDE / 2 + 0.5) * WIDE / N_WIDE * 60, (j - N_WIDE / 2 + 0.5) * WIDE / N_WIDE * 60
        print(f"{BANDS[key][3]:26s}: hellstes Pixel {np.hypot(dx, dy):5.1f}′ vom Trapez (Ost {dx:+5.1f}′, Nord {dy:+5.1f}′)")


def color_images():
    """18. Farbbilder in drei Wellenlängenbereichen (Zellen 11 von nebulae_orion.ipynb)."""
    global ax, axs, e1, fig, hp, img, key, keys, lab, name, peaks, rc
    global s, xc, yc
    fig, axs = plt.subplots(1, 3, figsize=(18, 6.4))
    e1 = [CLOSE / 2 * 60, -CLOSE / 2 * 60, -CLOSE / 2 * 60, CLOSE / 2 * 60]
    for ax, (name, keys), lab in zip(axs, COLOR.items(), ["optisch: DSS2 rot / Mittel / blau", "nahes Infrarot: 2MASS K / H / J", "mittleres Infrarot: WISE 12 / 4.6 / 3.4 µm"]):
        ax.imshow(rgb(keys, lo=5, hi=99.99, soft=1.0, gamma=1.6) if name == "DSS2" else rgb(keys, lo=2, hi=99.8, soft=0.08), origin="lower", extent=e1)
        ax.set_title(lab, fontsize=11)
        ax.set_xlabel("Rektaszension relativ [′]")
    axs[0].set_ylabel("Deklination relativ [′]")
    plt.tight_layout()
    plt.show()

    yc, xc = np.mgrid[:N_CLOSE, :N_CLOSE]
    rc = np.hypot(xc - N_CLOSE / 2 + 0.5, yc - N_CLOSE / 2 + 0.5) * CLOSE / N_CLOSE * 60
    for key in ["2MASS-J", "2MASS-K"]:
        img = CLOSEMAP[key]
        hp = img - ndimage.median_filter(img, size=9)
        s = 1.4826 * np.median(np.abs(hp - np.median(hp)))
        peaks = (hp == ndimage.maximum_filter(hp, size=5)) & (hp > 8 * s) & (rc < 10)
        print(f"{key:9s}: {peaks.sum():4d} Punktquellen über 8σ bis 10′ um das Trapez")


def distance():
    """19. Die Entfernung aus Gaia (Zellen 14 von nebulae_orion.ipynb)."""
    global D_ERR, D_FROM_GAIA, PLX, PLX_SYS, ax, col, d, e, fig, lab, mem, plx
    global w
    mem = (GAIA.parallax > 2.0) & (GAIA.parallax < 3.5)
    plx = GAIA.parallax[mem] + 0.017
    w = 1 / GAIA.parallax_error[mem] ** 2
    PLX = (np.average(plx, weights=w), 1 / np.sqrt(w.sum()))
    PLX_SYS = 0.010                                                # angenommene Unsicherheit des Nullpunkts [mas]
    D_FROM_GAIA = 1000 / PLX[0]
    D_ERR = D_FROM_GAIA * np.hypot(PLX[1], PLX_SYS) / PLX[0]
    fig, ax = plt.subplots(figsize=(11, 5.6))
    ax.hist(GAIA.parallax + 0.017, bins=np.linspace(0, 6, 121), color="0.7", label="alle Sterne (15′, Parallaxe auf 10 %)")
    ax.hist(plx, bins=np.linspace(0, 6, 121), color="C0", label=f"Mitglieder (2.0–3.5 mas): {mem.sum()}")
    ax.axvline(PLX[0], color="k", lw=1.5, label=f"gewichtetes Mittel: {PLX[0]:.3f} mas = {D_FROM_GAIA:.1f} pc")
    for (lab, (d, e)), col in zip(DIST_REF.items(), ["C3", "C2"]):
        ax.axvspan(1000 / (d + e), 1000 / (d - e), color=col, alpha=0.4, label=f"{lab}: {d:.0f} ± {e:.0f} pc")
    ax.set_xlabel("Parallaxe [mas] (mit Nullpunkt +0.017)")
    ax.set_ylabel("Zahl der Sterne")
    ax.set_title("Die Parallaxen der Sterne im Orionnebel", fontsize=10)
    ax.legend(fontsize=9)
    plt.show()

    print(f"Mitglieder {mem.sum()} von {len(GAIA)}; Parallaxe {PLX[0]:.4f} ± {PLX[1]:.4f} mas (Streuung der Sterne {plx.std():.3f} mas)")
    print(f"Entfernung {D_FROM_GAIA:.1f} ± {D_ERR:.1f} pc (statistisch ± {D_FROM_GAIA * PLX[1] / PLX[0]:.1f}, Nullpunkt ± {D_FROM_GAIA * PLX_SYS / PLX[0]:.1f}; Median der Sterne {1000 / np.median(plx):.1f} pc; ohne Nullpunkt {1000 / np.average(plx - 0.017, weights=w):.1f} pc)")
    for lab, (d, e) in DIST_REF.items():
        print(f"  gegen {lab}: {(D_FROM_GAIA - d) / np.hypot(D_ERR, e):+.1f} σ")


def region_photometry():
    """20. Photometrie der ganzen Region (Zellen 17 von nebulae_orion.ipynb)."""
    global CAL, FLUX, ax, e, f, fig, grow, img, key, radii
    CAL = [k for k, v in BANDS.items() if v[1] is not None]
    radii = np.arange(5, 56, 2.5)
    FLUX = {}
    fig, ax = plt.subplots(figsize=(11, 5.8))
    for key in CAL:
        img = to_jy_sr(key)
        grow = np.array([photometry(img, r)[0] for r in radii])
        FLUX[key] = photometry(img)
        if key in ["IRIS 12", "IRIS 100", "Planck 857", "Planck 353", "Planck 28", "Bonn 1.4"]:
            ax.plot(radii, grow / FLUX[key][0], "o-", ms=4, label=BANDS[key][3])
    ax.axvline(APER, color="0.5", ls=":")
    ax.axhline(1, color="0.5", lw=0.8)
    ax.set_xlabel("Radius der Öffnung [′]")
    ax.set_ylabel("Fluss / Fluss bei 40′")
    ax.set_title("Wachstumskurven: Wann ist die ganze Strahlung erfasst?", fontsize=10)
    ax.legend(fontsize=9)
    plt.show()

    for key in CAL:
        f, e = FLUX[key]
        print(f"{BANDS[key][3]:26s} ν = {BANDS[key][1] / 1e9:8.1f} GHz: S = {f:10.1f} ± {e:7.1f} Jy")


def free_free():
    """21. Frei-frei-Strahlung und der Stern, der den Nebel ionisiert (Zellen 20 von nebulae_orion.ipynb)."""
    global ALPHA_FF, E_ff, L28, Q_ERR, Q_ION, S_ff, ax, ax2, d_cm, ff_keys, fig, lnS0
    global nn, nu_ff, typ
    ff_keys = ["Planck 28", "Planck 44", "Planck 70"]
    nu_ff = np.array([BANDS[k][1] for k in ff_keys])
    S_ff = np.array([FLUX[k][0] for k in ff_keys])
    E_ff = np.array([FLUX[k][1] for k in ff_keys])
    ALPHA_FF, lnS0 = np.polyfit(np.log(nu_ff / 28.4e9), np.log(S_ff), 1, w=S_ff / E_ff)
    d_cm = D_FROM_GAIA * PC_CM
    L28 = 4 * np.pi * d_cm**2 * S_ff[0] * 1e-23
    Q_ION = 6.3e52 * (T_E / 1e4) ** -0.45 * (28.4) ** 0.1 * L28 / 1e27
    Q_ERR = Q_ION * np.hypot(E_ff[0] / S_ff[0], 2 * D_ERR / D_FROM_GAIA)

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.6))
    nn = np.logspace(9, 11.2, 50)
    ax.errorbar(nu_ff / 1e9, S_ff, yerr=E_ff, fmt="o", color="C0", ms=8, capsize=4, label="Planck (Öffnung 40′)")
    ax.plot(nn / 1e9, np.exp(lnS0) * (nn / 28.4e9) ** ALPHA_FF, color="C0", lw=1.2, label=f"Potenzgesetz, α = {ALPHA_FF:+.2f}")
    ax.plot(nn / 1e9, S_ff[0] * (nn / 28.4e9) ** -0.1, color="0.5", ls=":", label="dünne Frei-frei-Strahlung, α = −0.1")
    ax.errorbar(1.42, FLUX["Bonn 1.4"][0], yerr=FLUX["Bonn 1.4"][1], fmt="s", color="C3", ms=8, capsize=4, label="Bonn 1.4 GHz (nicht im Fit)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(50, 1000)
    ax.set_xlabel("Frequenz [GHz]")
    ax.set_ylabel("Flussdichte [Jy]")
    ax.set_title("Das Radiospektrum des Orionnebels", fontsize=10)
    ax.legend(fontsize=9)
    ax2.plot(MARTINS_V.logQ, range(len(MARTINS_V)), "o-", color="0.4", label="O-Zwergsterne (Martins et al. 2005)")
    ax2.set_yticks(range(len(MARTINS_V)))
    ax2.set_yticklabels(MARTINS_V.typ + " V")
    ax2.axvspan(np.log10(Q_ION - Q_ERR), np.log10(Q_ION + Q_ERR), color="C0", alpha=0.3, label=f"Orionnebel: log Q = {np.log10(Q_ION):.2f}")
    ax2.set_xlabel(r"log $Q$ [Photonen/s]")
    ax2.set_title("Welcher Stern liefert so viele ionisierende Photonen?", fontsize=10)
    ax2.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    typ = MARTINS_V.typ[np.argmin(np.abs(MARTINS_V.logQ - np.log10(Q_ION)))]
    print(f"Spektralindex 28–70 GHz: α = {ALPHA_FF:+.3f}; S(28 GHz) = {S_ff[0]:.1f} ± {E_ff[0]:.1f} Jy, Bonn 1.4 GHz {FLUX['Bonn 1.4'][0]:.1f} Jy "
          f"(erwartet mit α = −0.1: {S_ff[0] * (1.42 / 28.4) ** -0.1:.0f} Jy)")
    print(f"L_ν(28 GHz) = {L28:.2e} erg/s/Hz, Q = {Q_ION:.2e} ± {Q_ERR:.1e} s⁻¹ (log Q = {np.log10(Q_ION):.2f}); passt zu {typ} V "
          f"(log Q = {MARTINS_V.logQ[MARTINS_V.typ == typ].values[0]})")


def extinction():
    """22. Wie viel Staub vor den Sternen liegt (Zellen 23 von nebulae_orion.ipynb)."""
    global AV_CTL, AV_ONC, JH0, ax, ax2, bins, colors, ctl, ex_c, ex_o, fig, hk_c
    global hk_o, jh_c, jh_o, onc, sat_area, sc
    def colors(df):
        df = df[df.ph_qual.astype(str).str[:3] == "AAA"]
        jh, hk = df.j_m - df.h_m, df.h_m - df.k_m
        dist = (1.70 * (hk - 0.30) - (jh - 0.61)) / np.hypot(1.70, 1)
        sig = np.hypot(1.70 * np.hypot(df.h_msigcom, df.k_msigcom), np.hypot(df.j_msigcom, df.h_msigcom)) / np.hypot(1.70, 1)
        return df, jh, hk, dist > np.maximum(sig, 0.03)


    onc, jh_o, hk_o, ex_o = colors(TM_ONC)
    ctl, jh_c, hk_c, ex_c = colors(TM_CTRL)
    JH0 = np.median(jh_c[~ex_c])
    AV_ONC = 9.35 * (jh_o[~ex_o] - JH0)
    AV_CTL = 9.35 * (jh_c[~ex_c] - JH0)
    sat_area = np.sum(WIDEMAP["Hα"] > 9.0e4) * (WIDE / N_WIDE * 60) ** 2
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    sc = ax.scatter(-(onc.ra[~ex_o] - RA0) * np.cos(np.radians(DE0)) * 60, (onc.dec[~ex_o] - DE0) * 60, c=AV_ONC, s=10, cmap="viridis", vmin=0, vmax=10)
    plt.colorbar(sc, ax=ax, label=r"$A_V$ [mag]")
    ax.invert_xaxis()
    ax.set_aspect("equal")
    ax.set_xlabel("Rektaszension relativ [′] (Osten links)")
    ax.set_ylabel("Deklination relativ [′]")
    ax.set_title("Extinktion der Haufensterne ohne Überschuss (2MASS J − H)", fontsize=10)
    bins = np.linspace(-3, 20, 47)
    ax2.hist(AV_CTL, bins=bins, density=True, histtype="step", lw=2, color="0.5", label=f"Vergleichsfeld ({len(AV_CTL)})")
    ax2.hist(AV_ONC, bins=bins, density=True, histtype="step", lw=2, color="C3", label=f"Orionnebel-Haufen ({len(AV_ONC)})")
    ax2.set_xlabel(r"$A_V$ [mag]")
    ax2.set_ylabel("Anteil pro mag")
    ax2.set_title("Wie viel Staub vor den Sternen liegt", fontsize=10)
    ax2.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    print(f"SHASSA übersättigt (über 9·10⁴ dR) auf {sat_area:.0f} Quadratbogenminuten")
    print(f"Eigenfarbe (J − H)₀ = {JH0:.3f} (Median im Vergleichsfeld)")
    print(f"A_V Haufen: Median {np.median(AV_ONC):.2f} mag, 16. bis 84. Perzentil {np.percentile(AV_ONC, 16):.2f} bis {np.percentile(AV_ONC, 84):.2f}, "
          f"Anteil über 5 mag {np.mean(AV_ONC > 5):.2f}; Vergleichsfeld: Median {np.median(AV_CTL):.2f}, Streuung {np.std(AV_CTL):.2f} mag")
    print(f"Sterne mit A_V über 5 mag liegen im Median {np.median(np.hypot((onc.ra[~ex_o][AV_ONC > 5] - RA0) * np.cos(np.radians(DE0)), onc.dec[~ex_o][AV_ONC > 5] - DE0)) * 60:.1f}′ "
          f"vom Trapez, die übrigen {np.median(np.hypot((onc.ra[~ex_o][AV_ONC <= 5] - RA0) * np.cos(np.radians(DE0)), onc.dec[~ex_o][AV_ONC <= 5] - DE0)) * 60:.1f}′")


def density():
    """23. Dichte, Größe und die Strömgren-Kugel (Zellen 26 von nebulae_orion.ipynb)."""
    global EM_CORE, EPS, M_HII, N_CORE, N_RMS, R_ION, R_cm, SRC, TAU_14, T_B, ax, ax2
    global c0, c1, fig, fit70, fwhm, gauss2d, im, nn, nv, om_nvss, z70, zoom
    nv = WIDEMAP["NVSS"]
    om_nvss = 1.1331 * np.radians(45 / 3600) ** 2
    T_B = nv[R_ARCMIN < 5].max() * 1e-26 * C_SI**2 / (2 * K_B * 1.4e9**2 * om_nvss)
    TAU_14 = -np.log(1 - T_B / T_E)
    EM_CORE = TAU_14 / (3.28e-7 * (T_E / 1e4) ** -1.35 * 1.4 ** -2.1)
    N_CORE = np.sqrt(EM_CORE / 0.1)
    z70 = WIDEMAP["Planck 70"] - np.median(WIDEMAP["Planck 70"][(R_ARCMIN > BG[0]) & (R_ARCMIN < BG[1])])


    def gauss2d(p):
        A, x0, y0, s1, s2, th = p
        xr = (xx - x0) * np.cos(th) + (yy - y0) * np.sin(th)
        yr = -(xx - x0) * np.sin(th) + (yy - y0) * np.cos(th)
        return A * np.exp(-0.5 * (xr**2 / s1**2 + yr**2 / s2**2))


    fit70 = optimize.least_squares(lambda p: (gauss2d(p) - z70)[R_ARCMIN < 30], [z70.max(), N_WIDE / 2, N_WIDE / 2, 15, 15, 0])
    fwhm = 2.355 * np.abs(fit70.x[3:5]) * WIDE / N_WIDE * 60
    SRC = np.sqrt(np.clip(fwhm**2 - 13.3**2, 0, None))
    R_ION = 0.5 * np.sqrt(SRC[0] * SRC[1]) * D_FROM_GAIA * np.radians(1 / 60)    # pc, Halbwertsradius
    R_cm = R_ION * PC_CM
    N_RMS = np.sqrt(3 * Q_ION / (4 * np.pi * R_cm**3 * ALPHA_B))
    M_HII = 4 / 3 * np.pi * R_cm**3 * N_RMS * 1.4 * M_H / MSUN
    EPS = (N_RMS / N_CORE) ** 2
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    zoom = R_ARCMIN < 20
    c0, c1 = N_WIDE // 2 - 40, N_WIDE // 2 + 40
    im = ax.imshow(nv[c0:c1, c0:c1], origin="lower", extent=[20, -20, -20, 20], cmap="magma", vmin=0, vmax=np.percentile(nv[c0:c1, c0:c1], 99.8))
    plt.colorbar(im, ax=ax, label="NVSS 1.4 GHz [Jy/Strahl]")
    ax.contour(np.linspace(20, -20, 80), np.linspace(-20, 20, 80), z70[c0:c1, c0:c1], levels=[0.5 * z70.max()], colors="cyan", linewidths=1.5)
    ax.set_xlabel("Rektaszension relativ [′]")
    ax.set_ylabel("Deklination relativ [′]")
    ax.set_title("Der Kern bei 1.4 GHz (NVSS); cyan: halbe Höhe bei 70 GHz", fontsize=10)
    nn = np.logspace(1, 5, 100)
    ax2.loglog(nn, (3 * Q_ION / (4 * np.pi * nn**2 * ALPHA_B)) ** (1 / 3) / PC_CM, color="C0", lw=1.8, label=f"Strömgren-Radius, Q = {Q_ION:.1e} s⁻¹")
    ax2.plot(N_RMS, R_ION, "o", color="C3", ms=9, label=f"ganzes Gebiet (70 GHz): R = {R_ION:.2f} pc, n_rms = {N_RMS:.0f}")
    ax2.axvline(N_CORE, color="C2", ls="--", label=f"Kern aus NVSS: n ≈ {N_CORE:.0f} cm⁻³")
    ax2.set_xlabel(r"Elektronendichte $n_e$ [cm$^{-3}$]")
    ax2.set_ylabel("Radius [pc]")
    ax2.set_title("Wie groß kann das ionisierte Gebiet sein?", fontsize=10)
    ax2.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    print(f"NVSS: Spitze {nv[R_ARCMIN < 5].max():.1f} Jy/Strahl → T_b = {T_B:.0f} K, τ(1.4 GHz) = {TAU_14:.2f}, EM = {EM_CORE:.2e} pc cm⁻⁶, "
          f"n ≈ {N_CORE:.0f} cm⁻³ (0.1 pc); τ(28 GHz) = {TAU_14 * (28.4 / 1.4) ** -2.1:.4f}")
    print(f"70 GHz: FWHM {fwhm[0]:.1f}′ × {fwhm[1]:.1f}′, ohne Strahl {SRC[0]:.1f}′ × {SRC[1]:.1f}′ → R = {R_ION:.2f} pc; n_rms = {N_RMS:.0f} cm⁻³, "
          f"Masse {M_HII:.1f} M☉; Füllfaktor (n_rms/n_Kern)² = {EPS:.2f}")
    print(f"Strömgren-Radius: n = 10³ → {(3 * Q_ION / (4 * np.pi * 1e6 * ALPHA_B)) ** (1 / 3) / PC_CM:.2f} pc, n = {N_CORE:.0f} → "
          f"{(3 * Q_ION / (4 * np.pi * N_CORE**2 * ALPHA_B)) ** (1 / 3) / PC_CM:.2f} pc")


def spectrum():
    """24. Das Spektrum der ganzen Region (Zellen 29 von nebulae_orion.ipynb)."""
    global BETA, E_BETA, E_T, E_all, J, LNA, L_DATA, L_MBB, L_O7, M_GAS, S_all, T_DUST
    global ax, cov, d_m, dust, ff_all, fig, fitm, kappa353, keys, nf, nn, nu_all
    global o, res, top
    keys = [k for k in CAL if k != "Bonn 1.4"]
    nu_all = np.array([BANDS[k][1] for k in keys])
    S_all = np.array([FLUX[k][0] for k in keys])
    E_all = np.array([FLUX[k][1] for k in keys])
    ff_all = S_ff[0] * (nu_all / 28.4e9) ** -0.1
    dust = S_all - ff_all
    fitm = (nu_all <= 5e12) & (nu_all >= 217e9)
    res = optimize.least_squares(lambda p: np.log(mbb(nu_all[fitm], *p)) - np.log(dust[fitm]), [np.log(1e-3), 40.0, 1.7])
    LNA, T_DUST, BETA = res.x
    J = res.jac
    cov = np.linalg.inv(J.T @ J) * np.sum(res.fun**2) / max(fitm.sum() - 3, 1)
    E_T, E_BETA = np.sqrt(np.diag(cov))[1:]
    d_m = D_FROM_GAIA * PC_CM / 100
    nn = np.logspace(np.log10(100e9), 14, 3000)
    L_MBB = 4 * np.pi * d_m**2 * np.trapz(mbb(nn, *res.x) * 1e-26, nn) / (LSUN / 1e7)
    o = np.argsort(nu_all)
    L_DATA = 4 * np.pi * d_m**2 * np.trapz(dust[o] * 1e-26, nu_all[o]) / (LSUN / 1e7)
    kappa353 = 0.1 * (353e9 / 1e12) ** BETA * 0.1                  # m²/kg Gas
    M_GAS = dust[keys.index("Planck 353")] * 1e-26 * d_m**2 / (kappa353 * planck(353e9, T_DUST)) / (MSUN / 1e3)
    L_O7 = 10 ** MARTINS_V.logL[MARTINS_V.typ == "O7"].values[0]

    fig, ax = plt.subplots(figsize=(12, 6.5))
    ax.errorbar(nu_all / 1e9, nu_all * S_all * 1e-26, yerr=nu_all * E_all * 1e-26, fmt="o", color="k", ms=7, capsize=3, label="gemessen (Öffnung 40′)")
    ax.plot(nn / 1e9, nn * mbb(nn, *res.x) * 1e-26, color="C3", lw=1.6, label=f"Staub: T = {T_DUST:.1f} K, β = {BETA:.2f}")
    nf = np.logspace(9.4, 13.5, 200)
    ax.plot(nf / 1e9, nf * S_ff[0] * (nf / 28.4e9) ** -0.1 * 1e-26, color="C0", lw=1.4, label="Frei-frei-Strahlung (α = −0.1)")
    ax.plot(nf / 1e9, nf * (mbb(nf, *res.x) + S_ff[0] * (nf / 28.4e9) ** -0.1) * 1e-26, color="0.4", ls="--", lw=1, label="Summe")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(1e-14, 3e-8)
    ax.set_xlabel("Frequenz [GHz]")
    ax.set_ylabel(r"$\nu S_\nu$ [W/m²]")
    ax.set_title("Das Spektrum des Orionnebels von 1 cm bis 12 µm", fontsize=10)
    top = ax.secondary_xaxis("top", functions=(lambda f: 2.998e5 / np.maximum(f, 1e-9), lambda w: 2.998e5 / np.maximum(w, 1e-9)))
    top.set_xlabel("Wellenlänge [µm]")
    ax.legend(fontsize=9)
    plt.show()

    print(f"Staub: T = {T_DUST:.1f} ± {E_T:.1f} K, β = {BETA:.2f} ± {E_BETA:.2f}; Maximum von νS_ν bei {2.998e14 / nu_all[np.argmax(nu_all * S_all)]:.0f} µm")
    print(f"Infrarot-Leuchtkraft: Modell {L_MBB:.2e} L☉, Messpunkte {L_DATA:.2e} L☉; O7 V nach Martins: {L_O7:.2e} L☉ "
          f"(Verhältnis Messpunkte/O7 V = {L_DATA / L_O7:.1f})")
    print(f"Masse von Gas und Staub aus 353 GHz: {M_GAS:.0f} M☉; ionisiertes Gas (Schritt 23): {M_HII:.0f} M☉")


def dust_temperature():
    """25. Eine Karte der Staubtemperatur (Zellen 32 von nebulae_orion.ipynb)."""
    global SLOPE, TMAP, Tg, ax, ax2, bg100, bg60, fig, i100, i60, im, lnT0
    global ok, ratio, rg, rr, tprof
    i60, i100 = to_jy_sr("IRIS 60"), to_jy_sr("IRIS 100")
    bg60 = np.median(i60[(R_ARCMIN > BG[0]) & (R_ARCMIN < BG[1])])
    bg100 = np.median(i100[(R_ARCMIN > BG[0]) & (R_ARCMIN < BG[1])])
    ratio = (i60 - 0.5 * bg60) / (i100 - 0.5 * bg100)               # halber Hintergrund abgezogen: Wolke vor und hinter dem Nebel
    Tg = np.linspace(10, 150, 1401)
    rg = (5e12 / 3e12) ** 1.5 * planck(5e12, Tg) / planck(3e12, Tg)
    TMAP = np.interp(ratio, rg, Tg, left=np.nan, right=np.nan)
    TMAP[(i100 - 0.5 * bg100) < 3 * np.std(i100[(R_ARCMIN > BG[0]) & (R_ARCMIN < BG[1])])] = np.nan
    rr = np.arange(1, 50, 1.0)
    tprof = np.array([np.nanmedian(TMAP[(R_ARCMIN >= r - 0.5) & (R_ARCMIN < r + 0.5)]) for r in rr])
    ok = (rr >= 3) & (rr <= 30) & np.isfinite(tprof)
    SLOPE, lnT0 = np.polyfit(np.log(rr[ok]), np.log(tprof[ok]), 1)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    im = ax.imshow(TMAP, origin="lower", extent=ext, cmap="coolwarm", vmin=20, vmax=70)
    ax.plot(0, 0, "+", color="k", ms=12, mew=1.5)
    plt.colorbar(im, ax=ax, label="Farbtemperatur 60/100 µm [K]")
    ax.set_xlabel("Rektaszension relativ [′]")
    ax.set_ylabel("Deklination relativ [′]")
    ax.set_title("Staubtemperatur aus IRIS 60 und 100 µm (β = 1.5)", fontsize=10)
    ax2.loglog(rr, tprof, "o", color="C3", ms=5, label="Median im Ring")
    ax2.loglog(rr[ok], np.exp(lnT0) * rr[ok] ** SLOPE, color="k", lw=1.4, label=f"Fit 3–30′: T ∝ r^{SLOPE:.2f}")
    ax2.loglog(rr[ok], np.exp(lnT0) * rr[ok][0] ** SLOPE * (rr[ok] / rr[ok][0]) ** (-2 / 5.5), color="C0", ls="--", lw=1.2, label="ein Stern: T ∝ r^−0.36")
    ax2.set_xlabel("Abstand vom Trapez [′]")
    ax2.set_ylabel("Farbtemperatur [K]")
    ax2.set_title("Wie die Staubtemperatur nach außen fällt", fontsize=10)
    ax2.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    print(f"Farbtemperatur: Maximum {np.nanmax(TMAP):.1f} K, bei 5′ {np.interp(5, rr, tprof):.1f} K, bei 20′ {np.interp(20, rr, tprof):.1f} K, "
          f"bei 40′ {np.interp(40, rr, tprof):.1f} K; Steigung {SLOPE:.2f} (ein Stern: −0.36)")


def young_stars():
    """26. Junge Sterne mit Infrarot-Überschuss (Zellen 35 von nebulae_orion.ipynb)."""
    global F_CORR, F_CTRL, F_ONC, ax, axs, ex, fig, hk, hk_line, jh, lab
    # jh_o, hk_o, ex_o und jh_c, hk_c, ex_c aus Schritt 22 (Funktion colors)
    F_ONC, F_CTRL = ex_o.mean(), ex_c.mean()
    F_CORR = (F_ONC - F_CTRL) / (1 - F_CTRL)
    fig, axs = plt.subplots(1, 2, figsize=(16, 6.5), sharex=True, sharey=True)
    hk_line = np.linspace(-0.3, 2.5, 10)
    for ax, (jh, hk, ex, lab) in zip(axs, [(jh_o, hk_o, ex_o, "Orionnebel-Haufen (10′)"), (jh_c, hk_c, ex_c, "Vergleichsfeld 6° östlich (10′)")]):
        ax.scatter(hk[~ex], jh[~ex], s=6, color="0.5", label="ohne Überschuss")
        ax.scatter(hk[ex], jh[ex], s=8, color="C3", label=f"mit Überschuss: {ex.sum()} von {len(ex)} ({100 * ex.mean():.1f} %)")
        ax.plot(hk_line, 0.61 + 1.70 * (hk_line - 0.30), color="k", lw=1.2, label="Rötungsgerade durch das rote Ende der Zwerge")
        ax.plot(hk_line, 0.52 + 0.58 * hk_line, color="C0", ls="--", lw=1.2, label="T-Tauri-Streifen (Meyer et al. 1997)")
        ax.set_xlim(-0.3, 2.2)
        ax.set_ylim(-0.2, 3.5)
        ax.set_xlabel("H − K [mag]")
        ax.set_title(lab, fontsize=10)
        ax.legend(fontsize=8.5, loc="upper left")
    axs[0].set_ylabel("J − H [mag]")
    plt.tight_layout()
    plt.show()

    print(f"Orionnebel-Haufen: {ex_o.sum()} von {len(ex_o)} mit Überschuss ({100 * F_ONC:.1f} %); Vergleichsfeld {ex_c.sum()} von {len(ex_c)} "
          f"({100 * F_CTRL:.1f} %); um Fehlalarme korrigiert {100 * F_CORR:.1f} %")
    print(f"Hillenbrand et al. 1998 (aus I − K): mindestens {100 * DISK_HILLENBRAND[0]:.0f} %, höchstens {100 * DISK_HILLENBRAND[1]:.0f} %")


def literature():
    """27. Gegen die Literatur (Zellen 38 von nebulae_orion.ipynb)."""
    global ax, col, e, fig, i, lab, rows, v
    rows = [("Entfernung / Kounkel et al. 2017", D_FROM_GAIA / DIST_REF["Kounkel et al. 2017 (VLBA)"][0],
             np.hypot(D_ERR / D_FROM_GAIA, 5 / 388), "C0"),
            ("Entfernung / Menten et al. 2007", D_FROM_GAIA / DIST_REF["Menten et al. 2007 (VLBA)"][0],
             np.hypot(D_ERR / D_FROM_GAIA, 7 / 414), "C0"),
            ("Q / Q(O7 V)", Q_ION / 10 ** 48.75, Q_ERR / 10 ** 48.75, "C3"),
            ("L_IR (Messpunkte) / L(O7 V)", L_DATA / L_O7, 0.1 * L_DATA / L_O7, "C1"),
            ("Scheibenanteil (JHK) / 55 % (Hillenbrand)", F_CORR / DISK_HILLENBRAND[0], 0.02 / DISK_HILLENBRAND[0], "C2")]
    fig, ax = plt.subplots(figsize=(11, 4.8))
    for i, (lab, v, e, col) in enumerate(rows):
        ax.errorbar(v, -i, xerr=e, fmt="o", color=col, ms=8, capsize=4)
    ax.axvline(1, color="k", lw=1)
    ax.set_yticks(-np.arange(len(rows)))
    ax.set_yticklabels([r[0] for r in rows], fontsize=10)
    ax.set_xscale("log")
    ax.set_xlabel("eigener Wert / Vergleichswert")
    ax.set_title("Wie die eigenen Zahlen zu den veröffentlichten passen", fontsize=10)
    plt.tight_layout()
    plt.show()

    print(f"Entfernung {D_FROM_GAIA:.1f} ± {D_ERR:.1f} pc; Kounkel 388 ± 5, Menten 414 ± 7")
    print(f"log Q = {np.log10(Q_ION):.2f}; O7 V: 48.75, O6 V: 48.99, O7.5 V: 48.61")
    print(f"L_IR = {L_DATA:.2e} L☉ (Modell {L_MBB:.2e}); O7 V: {L_O7:.2e} L☉")
    print(f"Scheiben: {100 * F_CORR:.1f} % (J, H, K); Hillenbrand et al. 1998: 55 bis 90 % (I − K)")
    print(f"A_V der Haufensterne: Median {np.median(AV_ONC):.2f} mag (16. bis 84. Perzentil {np.percentile(AV_ONC, 16):.2f} bis {np.percentile(AV_ONC, 84):.2f})")
