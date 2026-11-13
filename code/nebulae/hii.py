"""Elektronentemperatur der H-II-Regionen von M 101 aus SDSS-Spektren: schwache Linien, Dichte, Temperatur, Häufigkeit, Metallizitätsgradient und Vergleich mit CHAOS.

Für nebulae.ipynb aus nebulae_temperature.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: regions, weak_lines, line_fits, saturation, density, thermometer, region_temperatures, tt_relations, stacking, abundances, gradient, fibers_vs_chaos, gradient_vs_chaos, strong_lines.
Downloads und Cache: data/nebulae/ (`nebdata.py`).
"""
import nebdata                                         # zuerst: Cache-Ordner für astropy
import io
import os
import time
import warnings
import urllib.request
from fractions import Fraction
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, brentq
from astropy.io import fits
from astropy.coordinates import SkyCoord
from astropy import units as u
from astroquery.sdss import SDSS


def regions():
    """27. Die H-II-Regionen von M 101 (Zellen 12, 13, 14, 16 von nebulae_temperature.ipynb)."""
    global AIR, ASTRODATA, Atom, CH, C_CGS, C_KMS, DEC0, D_MPC, FOV, GROUPS, HA_HB, HG_HB
    global H_PLANCK, INC_DEG, K, KPC_PER_R25, K_B, LINES, N2, N_E, N_MC, O2, O3, PA_DEG
    global PYNEB, R25_ARCSEC, RA0, S, S2, S3, SH95, SN_AUR, SN_STRONG, SPEC, VIZIER, V_SYS
    global _, air2vac, ax, axes, bins, ch_ab, ch_c, ch_lin, ch_pos, col, download, dx
    global dy, fig, fit_group, gas, half, hdus, idx, img, inst, inst_sigma, j_H, k_ccm
    global m, measure, n_te, numeric_rows, off, pa, pyneb_file, r_deg, r_over_r25, refine_z, rng, sdss_query
    global sep, spec_list, t, tol, vizier_table, xm, ym
    ASTRODATA = nebdata.DATA


    V_SYS = 241.0                                   # systemische Geschwindigkeit von M 101 [km/s]
    D_MPC = 7.4                                     # Entfernung wie bei CHAOS (Croxall et al. 2016)
    R25_ARCSEC, PA_DEG, INC_DEG = 864.0, 39.0, 18.0 # Scheibenradius, Lagewinkel und Neigung wie bei CHAOS
    N_E = 100.0                                     # Elektronendichte [cm⁻³] (Schritt 31)
    SN_STRONG = 3.0                                 # Mindest-S/N der starken Linien
    SN_AUR = 5.0                                    # Mindest-S/N der schwachen Temperaturlinien (Schritt 29)
    N_MC = 500                                      # Ziehungen für die Fehlerfortpflanzung
    C_KMS = 299792.458
    rng = np.random.default_rng(42)
    pd.set_option("display.width", 160)
    np.seterr(divide="ignore", invalid="ignore")                 # log von Nicht-Nachweisen und negativen Flüssen -> NaN

    VIZIER = ["https://vizier.cds.unistra.fr", "https://vizier.cfa.harvard.edu", "http://vizier.nao.ac.jp"]   # Spiegel
    PYNEB = "https://raw.githubusercontent.com/Morisset/PyNeb_devel/master/pyneb/"

    def download(urls, path, check=None):
        # lädt eine Datei vom ersten Server, der antwortet, und liest sie danach aus dem Cache
        path = Path(path)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            for url in urls:
                try:
                    with urllib.request.urlopen(url, timeout=30) as r:
                        data = r.read()
                except OSError:
                    continue
                if check is None or check(data):
                    path.write_bytes(data)
                    break
            else:
                raise OSError(f"Kein Server liefert {path.name}")
        return path

    def vizier_table(source):
        # eine VizieR-Tabelle als tabulatorgetrennter Text; CDS war im November 2026 zeitweise nicht erreichbar
        query = f"/viz-bin/asu-tsv?-source={source}&-out.max=unlimited&-out.all"
        p = download([m + query for m in VIZIER], ASTRODATA / "vizier" / (source.replace("/", "_") + ".tsv"),
                     check=lambda d: d.startswith(b"#"))
        lines = [l for l in p.read_text().splitlines(keepends=True) if l.strip() and not l.startswith("#")]
        df = pd.read_csv(io.StringIO("".join(lines)), sep="\t", skiprows=[1, 2], dtype=str)   # Zeilen 2, 3: Einheiten, Striche
        df.columns = [c.strip() for c in df.columns]
        return df.apply(lambda s: s.str.strip())

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

    # Atomphysik: Fünf-Niveau-Atome, Wasserstoff-Emissivitäten, Staubgesetz
    H_PLANCK, C_CGS, K_B = 6.62607e-27, 2.99792458e10, 1.380649e-16

    def air2vac(lam):
        # Luft- in Vakuumwellenlänge [Å] (Morton 2000); SDSS gibt Vakuumwellenlängen an
        s2 = (1e4 / lam) ** 2
        return lam * (1 + 8.34254e-5 + 2.406147e-2 / (130 - s2) + 1.5998e-4 / (38.9 - s2))

    AIR = {"OII3726": 3726.03, "OII3729": 3728.82, "Hg": 4340.47, "OIII4363": 4363.21, "Hb": 4861.33, "OIII4959": 4958.91,
           "OIII5007": 5006.84, "NII5755": 5754.59, "OI6300": 6300.30, "SIII6312": 6312.06, "NII6548": 6548.05, "Ha": 6562.80,
           "NII6584": 6583.45, "SII6717": 6716.44, "SII6731": 6730.82, "OII7320": 7320.0, "OII7330": 7330.2,
           "SIII9069": 9068.6, "SIII9532": 9530.6}
    LINES = {k: air2vac(v) for k, v in AIR.items()}           # Vakuumwellenlängen [Å]

    def numeric_rows(text):
        rows = []
        for line in text.splitlines():
            try:
                vals = [float(x) for x in line.split()]
            except ValueError:
                continue
            if vals:
                rows.append(vals)
        return rows

    def pyneb_file(name):
        return download([PYNEB + name], ASTRODATA / "pyneb" / Path(name).name)

    class Atom:
        """Fünf-Niveau-Atom im statistischen Gleichgewicht mit Atomdaten aus der PyNeb-Datenbank."""
        def __init__(self, ion, atom_src, coll_src, n=5):
            self.n = n
            self.A = np.array(numeric_rows(pyneb_file(f"atomic_data/{ion}_atom_{atom_src}.dat").read_text()))[:n, :n]
            text = pyneb_file(f"atomic_data/{ion}_coll_{coll_src}.dat").read_text()
            rows = numeric_rows(text)
            grid = np.array(rows[0][2:])
            unit = text.split("T_UNIT")[1].split()[0]                      # log(K), K/10000 oder K
            self.logT = {"log(K)": grid, "K/10000": np.log10(grid * 1e4), "K": np.log10(grid)}[unit]
            self.ups = {(int(r[0]) - 1, int(r[1]) - 1): np.array(r[2:]) for r in rows[1:]}   # Stoßstärken Υ(T)
            E, g = [], []
            for line in pyneb_file(f"atomic_data/levels/{ion}_levels.dat").read_text().splitlines():
                p = [s.strip() for s in line.split("|")]
                if len(p) >= 4 and p[2] and p[3]:
                    g.append(2 * float(Fraction(p[2])) + 1)                  # statistisches Gewicht 2J + 1
                    E.append(float(p[3]))                                   # Energie [cm⁻¹]
                if len(E) == n:
                    break
            self.E, self.g = np.array(E), np.array(g)

        def populations(self, T, ne):
            # Besetzung der Niveaus aus Stoßanregung, Stoßabregung und spontanem Zerfall
            n, E, g = self.n, self.E, self.g
            R = np.zeros((n, n))                                            # R[i, j]: Rate von i nach j pro Ion in i
            for i in range(n):
                for j in range(i + 1, n):
                    ups = np.interp(np.log10(T), self.logT, self.ups[(i, j)])
                    q_down = 8.629e-6 * ups / (g[j] * np.sqrt(T))
                    q_up = q_down * g[j] / g[i] * np.exp(-H_PLANCK * C_CGS * (E[j] - E[i]) / (K_B * T))
                    R[i, j] += ne * q_up
                    R[j, i] += ne * q_down + self.A[j, i]
            M = R.T - np.diag(R.sum(axis=1))                                # Zuflüsse minus Abflüsse = 0
            M[0] = 1.0                                                      # eine Gleichung durch die Normierung ersetzen
            b = np.zeros(n)
            b[0] = 1.0
            return np.linalg.solve(M, b)

        def wavelength(self, up, lo):
            return 1e8 / (self.E[up] - self.E[lo])                           # Vakuum [Å]

        def line(self, T, ne, lam, tol=1.0):
            # Emissivität 4πj/(n_ion n_e) [erg cm³ s⁻¹] aller Übergänge innerhalb von tol um lam
            N = self.populations(T, ne)
            tot = 0.0
            for up in range(self.n):
                for lo in range(up):
                    if self.A[up, lo] > 0 and abs(self.wavelength(up, lo) - lam) < tol:
                        tot += N[up] * self.A[up, lo] * H_PLANCK * C_CGS * (self.E[up] - self.E[lo]) / ne
            return tot

    O3 = Atom("o_iii", "FFT04-SZ00", "AK99")
    N2 = Atom("n_ii", "FFT04", "T11")
    S3 = Atom("s_iii", "FFTI06", "TG99")
    O2 = Atom("o_ii", "FFT04", "T07")
    S2 = Atom("s_ii", "TZ10-IFF05", "TZ10")
    def tol(name):
        return 2.0 if name in ("OII7320", "OII7330") else 1.0              # [O II] 7320 und 7330 sind je zwei Linien

    # Wasserstoff: Emissivitäten im Fall B (Storey & Hummer 1995) bei n_e = 100 cm⁻³
    SH95 = fits.open(pyneb_file("atomic_data_fits/h_i_rec_SH95.fits"))[1].data
    def j_H(T, trans="4_2"):                                                # "4_2" = Hβ, "3_2" = Hα, "5_2" = Hγ
        return np.interp(T, SH95["TEMP"][0], SH95[trans][0])
    HA_HB, HG_HB = j_H(1e4, "3_2") / j_H(1e4), j_H(1e4, "5_2") / j_H(1e4)

    def k_ccm(lam, Rv=3.1):
        # Staubgesetz von Cardelli, Clayton & Mathis (1989): k(λ) = A_λ / E(B−V), λ in Å
        x = 1e4 / np.asarray(lam, float)
        y = x - 1.82
        a = np.where(x < 1.1, 0.574 * x ** 1.61, 1 + 0.17699 * y - 0.50447 * y**2 - 0.02427 * y**3 + 0.72085 * y**4
                     + 0.01979 * y**5 - 0.77530 * y**6 + 0.32999 * y**7)
        b = np.where(x < 1.1, -0.527 * x ** 1.61, 1.41338 * y + 2.28305 * y**2 + 1.07233 * y**3 - 5.38434 * y**4
                     - 0.62251 * y**5 + 5.30260 * y**6 - 2.09002 * y**7)
        return Rv * a + b
    K = {k: float(k_ccm(v)) for k, v in LINES.items()}

    # Linienfits
    GROUPS = [(["NII6548", "Ha", "NII6584"], "frei"), (["Hb"], "frei"), (["OIII4959", "OIII5007"], "frei"),
              (["Hg", "OIII4363"], "frei"), (["NII5755"], "fest"), (["OI6300", "SIII6312"], "frei"),
              (["SII6717", "SII6731"], "frei"), (["OII7320", "OII7330"], "frei"), (["SIII9069"], "frei"),
              (["SIII9532"], "frei"), (["OII3726", "OII3729"], "frei")]

    def inst_sigma(sp, lam):
        # Breite σ [Å], die der Spektrograph einer unendlich schmalen Linie gibt (Spalte wdisp, in 10⁻⁴ dex)
        k = np.argmin(np.abs(sp["w"] - lam))
        return sp["wdisp"][k] * 1e-4 * np.log(10) * lam

    def fit_group(sp, names, z, sig=None, half=25):
        """Gaußlinien mit fester Lage auf einem linearen Kontinuum; Breite gemeinsam frei oder fest (sig).
    Linien mit maskierten Pixeln im Kern (gesättigt) fallen heraus. Namen dürfen auch Wellenlängen sein."""
        w, f, iv = sp["w"], sp["f"], sp["iv"]
        lam_all = np.array([LINES[n] if isinstance(n, str) else float(n) for n in names]) * (1 + z)
        if lam_all.min() - half < w.min() + 5 or lam_all.max() + half > w.max() - 5:
            return None
        bad = [(iv[np.abs(w - l) < 3] <= 0).any() for l in lam_all]
        keep = [n for n, b in zip(names, bad) if not b]
        if not keep:
            return None
        lam0 = np.array([l for l, b in zip(lam_all, bad) if not b])
        m = (w > lam_all.min() - half) & (w < lam_all.max() + half) & (iv > 0)
        for l, b in zip(lam_all, bad):
            if b:
                m &= np.abs(w - l) > 6
        W, F, E = w[m], f[m], 1 / np.sqrt(iv[m])
        def gauss(x, s, amps):
            return sum(a * np.exp(-0.5 * ((x - l) / s) ** 2) for a, l in zip(amps, lam0))
        if sig is None:
            model = lambda x, s, c0, c1, *a: c0 + c1 * (x - W.mean()) + gauss(x, s, a)
            p0 = [1.5, np.median(F), 0.0] + [max(F.max() - np.median(F), 1.0)] * len(keep)
            bounds = ([0.5, -np.inf, -np.inf] + [-np.inf] * len(keep), [5.0, np.inf, np.inf] + [np.inf] * len(keep))
            popt, pcov = curve_fit(model, W, F, p0=p0, sigma=E, absolute_sigma=True, bounds=bounds, maxfev=20000)
            s, ds, c0 = popt[0], np.sqrt(pcov[0, 0]), popt[1]
            amp, damp = popt[3:], np.sqrt(np.diag(pcov))[3:]
            curve = model(W, *popt)
        else:
            model = lambda x, c0, c1, *a: c0 + c1 * (x - W.mean()) + gauss(x, sig, a)
            popt, pcov = curve_fit(model, W, F, p0=[np.median(F), 0.0] + [0.0] * len(keep), sigma=E, absolute_sigma=True)
            s, ds, c0 = sig, 0.0, popt[0]
            amp, damp = popt[2:], np.sqrt(np.diag(pcov))[2:]
            curve = model(W, *popt)
        flux = amp * s * np.sqrt(2 * np.pi)
        err = np.sqrt((damp * s) ** 2 + (amp * ds) ** 2) * np.sqrt(2 * np.pi)
        return {"flux": dict(zip(keep, flux)), "err": dict(zip(keep, err)), "sigma": s, "cont": c0, "curve": (W, F, curve)}

    def refine_z(sp, z0):
        # Rotverschiebung aus der stärksten unmaskierten Linie
        w, f, iv = sp["w"], sp["f"], sp["iv"]
        for n in ["Hb", "OIII4959", "Ha", "NII6584"]:
            lam = LINES[n] * (1 + z0)
            if (iv[np.abs(w - lam) < 3] <= 0).any():
                continue
            m = np.abs(w - lam) < 6
            try:
                p, _ = curve_fit(lambda x, a, mu, s, c: c + a * np.exp(-0.5 * ((x - mu) / s) ** 2), w[m], f[m],
                                 p0=[f[m].max() - np.median(f[m]), lam, 1.5, np.median(f[m])])
                return p[1] / LINES[n] - 1
            except RuntimeError:
                continue
        return z0

    def measure(sp, z0):
        # alle Liniengruppen einer Faser; Lage aus der Rotverschiebung, Breite frei oder aus den starken Linien
        z = refine_z(sp, z0)
        rec, ratio = {"z": z}, []
        for names, mode in GROUPS:
            sig = None
            if mode == "fest":
                if not ratio:
                    continue
                sig = np.median(ratio) * inst_sigma(sp, LINES[names[0]] * (1 + z))
            try:
                r = fit_group(sp, names, z, sig)
            except (RuntimeError, ValueError):
                r = None
            if r is None:
                continue
            for n in r["flux"]:
                rec[n], rec[n + "_e"] = r["flux"][n], r["err"][n]
            if mode == "frei" and names[0] in ("NII6548", "Hb", "OIII4959"):
                si = inst_sigma(sp, LINES[names[-1]] * (1 + z))
                if si > 0:
                    ratio.append(r["sigma"] / si)
            if names == ["Hb"]:
                rec["cont_Hb"] = r["cont"]
        rec["width_ratio"] = np.median(ratio) if ratio else np.nan
        return rec

    # CHAOS (Croxall et al. 2016): Positionen, Linienflüsse relativ zu Hβ, Temperaturen und Häufigkeiten
    ch_pos = vizier_table("J/ApJ/830/4/table2")
    ch_lin = vizier_table("J/ApJ/830/4/table3")
    ch_ab = vizier_table("J/ApJ/830/4/table4").set_index("HIIid").apply(pd.to_numeric, errors="coerce")
    ch_pos["RgR25"] = pd.to_numeric(ch_pos["RgR25"])
    ch_lin["Flux"] = pd.to_numeric(ch_lin["Flux"], errors="coerce")
    ch_lin.loc[ch_lin["f_Flux"] == "<", "Flux"] = np.nan                     # obere Grenzen sind keine Messungen
    CH = ch_lin.assign(key=ch_lin["Species"] + ch_lin["lambda"]).pivot_table(index="HIIid", columns="key", values="Flux",
                                                                             aggfunc="first")
    ch_c = SkyCoord(ch_pos["RAJ2000"], ch_pos["DEJ2000"], unit=(u.hourangle, u.deg))

    # Das Zentrum steckt in den Namen: "NGC5457+7.2-3.8" liegt 7.2″ östlich und 3.8″ südlich davon
    off = ch_pos["HIIid"].str.extract(r"NGC5457([+-][\d.]+)([+-][\d.]+)").astype(float)
    RA0 = np.median(ch_c.ra.deg - off[0] / 3600 / np.cos(np.radians(ch_c.dec.deg)))
    DEC0 = np.median(ch_c.dec.deg - off[1] / 3600)

    def r_over_r25(ra, dec):
        # Abstand vom Zentrum in der Scheibe in Einheiten von R25 (Neigung und Lagewinkel wie bei CHAOS)
        x = (np.asarray(ra, float) - RA0) * np.cos(np.radians(DEC0)) * 3600
        y = (np.asarray(dec, float) - DEC0) * 3600
        pa, inc = np.radians(PA_DEG), np.radians(INC_DEG)
        return np.hypot(x * np.sin(pa) + y * np.cos(pa), (x * np.cos(pa) - y * np.sin(pa)) / np.cos(inc)) / R25_ARCSEC

    ch_pos["R_own"] = r_over_r25(ch_c.ra.deg, ch_c.dec.deg)
    KPC_PER_R25 = R25_ARCSEC / 206265 * D_MPC * 1e3

    # SDSS: alle Spektren in einem Kasten der halben Breite R25 um das Zentrum, innerhalb von 600 km/s der Galaxie
    r_deg = R25_ARCSEC / 3600
    spec_list = sdss_query(f'''
SELECT s.specObjID, s.ra, s.dec, s.z, s.class, s.plate, s.mjd, s.fiberID, s.run2d, s.instrument, s.snMedian
FROM SpecObj AS s
WHERE s.ra BETWEEN {RA0 - r_deg / np.cos(np.radians(DEC0))} AND {RA0 + r_deg / np.cos(np.radians(DEC0))}
  AND s.dec BETWEEN {DEC0 - r_deg} AND {DEC0 + r_deg}
  AND s.z BETWEEN {(V_SYS - 600) / C_KMS} AND {(V_SYS + 600) / C_KMS}
ORDER BY s.snMedian DESC''')
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        hdus = SDSS.get_spectra(matches=spec_list, data_release=17)
    SPEC = [dict(w=10 ** h[1].data["loglam"], f=h[1].data["flux"].astype(float), iv=h[1].data["ivar"].astype(float),
                 wdisp=h[1].data["wdisp"].astype(float)) for h in hdus]
    S = spec_list.to_pandas()
    S["specObjID"] = spec_list["specObjID"].astype(str)
    S["RR25"] = r_over_r25(S["ra"], S["dec"])
    idx, sep, _ = SkyCoord(S["ra"].values * u.deg, S["dec"].values * u.deg).match_to_catalog_sky(ch_c)
    S["chaos"] = np.where(sep.arcsec < 3, ch_pos["HIIid"].values[idx], None)
    gas = (S["class"] == "GALAXY").values

    # Farbbild aus SDSS
    FOV = 2.3 * R25_ARCSEC
    img = plt.imread(download([f"https://skyserver.sdss.org/dr17/SkyServerWS/ImgCutout/getjpeg?ra={RA0}&dec={DEC0}"
                               f"&scale={FOV / 1000:.4f}&width=1000&height=1000"], ASTRODATA / "sdss_m101.jpg"))

    n_te = ch_ab["Te([OIII])1"].notna() | ch_ab["Te([NII])1"].notna() | ch_ab["Te([SIII])1"].notna()
    print(f"Zentrum aus den CHAOS-Namen: RA {RA0:.5f}°, Dec {DEC0:.5f}°; R25 = {R25_ARCSEC / 60:.1f}′ = {KPC_PER_R25:.1f} kpc bei {D_MPC} Mpc")
    print(f"Kontrolle: eigene Abstände R/R25 minus CHAOS: höchstens {np.abs(ch_pos['R_own'] - ch_pos['RgR25']).max():.4f}")
    print(f"CHAOS: {len(ch_pos)} Regionen, {n_te.sum()} mit mindestens einer gemessenen Temperatur, {ch_ab['12+log(O/H)'].notna().sum()} mit O/H")
    print(f"SDSS: {len(S)} Spektren; Klassen {S['class'].value_counts().to_dict()}; "
          f"Spektrographen {S['instrument'].value_counts().to_dict()}")
    print(f"Fasern auf Gas: {gas.sum()} (SDSS {(gas & (S['instrument'] == 'SDSS')).sum()}, BOSS {(gas & (S['instrument'] == 'BOSS')).sum()}); "
          f"innerhalb von 3″ einer CHAOS-Region: {S.loc[gas, 'chaos'].notna().sum()}")

    half = FOV / 2 / 60
    dx = lambda ra: (np.asarray(ra, float) - RA0) * np.cos(np.radians(DEC0)) * 60
    dy = lambda dec: (np.asarray(dec, float) - DEC0) * 60
    fig, axes = plt.subplots(1, 2, figsize=(16, 6.8), gridspec_kw={"width_ratios": [1.15, 1]})
    ax = axes[0]
    ax.imshow(img, extent=[half, -half, -half, half])
    ax.scatter(dx(ch_c.ra.deg), dy(ch_c.dec.deg), marker="+", s=30, c="white", lw=0.9, label=f"CHAOS-Regionen ({len(ch_pos)})")
    for inst, col in [("SDSS", "cyan"), ("BOSS", "magenta")]:
        m = gas & (S["instrument"] == inst).values
        ax.scatter(dx(S.loc[m, "ra"]), dy(S.loc[m, "dec"]), s=45, facecolors="none", edgecolors=col, lw=1.2,
                   label=f"{inst}-Fasern auf Gas ({m.sum()})")
    ax.scatter(dx(S.loc[~gas, "ra"]), dy(S.loc[~gas, "dec"]), s=25, marker="x", c="yellow", lw=0.9, label=f"Klasse STAR ({(~gas).sum()})")
    t = np.linspace(0, 2 * np.pi, 300)
    pa, xm, ym = np.radians(PA_DEG), R25_ARCSEC / 60 * np.cos(t), R25_ARCSEC / 60 * np.cos(np.radians(INC_DEG)) * np.sin(t)
    ax.plot(xm * np.sin(pa) + ym * np.cos(pa), xm * np.cos(pa) - ym * np.sin(pa), c="orange", ls="--", lw=1, label="R25")
    ax.set_xlim(half, -half)
    ax.set_ylim(-half, half)
    ax.set_xlabel("ΔRA [′] (Osten links)")
    ax.set_ylabel("ΔDec [′]")
    ax.set_title("M 101: SDSS-Fasern und CHAOS-Spaltpositionen", fontsize=10)
    ax.legend(fontsize=8, loc="lower left")
    bins = np.arange(0, 1.25, 0.1)
    axes[1].hist(ch_pos["RgR25"], bins=bins, color="grey", alpha=0.6, label=f"CHAOS ({len(ch_pos)})")
    axes[1].hist(S.loc[gas, "RR25"], bins=bins, histtype="step", lw=2, color="tab:blue", label=f"SDSS-Fasern auf Gas ({gas.sum()})")
    axes[1].set_xlabel("Abstand vom Zentrum R / R25")
    axes[1].set_ylabel("Zahl der Regionen")
    axes[1].set_title("Verteilung über den Radius", fontsize=10)
    axes[1].legend(fontsize=9)
    fig.tight_layout()
    plt.show()


def weak_lines():
    """28. Erster Blick auf die schwachen Linien (Zellen 19 von nebulae_temperature.ipynb)."""
    global I_SHOW, ax, c5471, core, cs, dist, fig, k, lab, lam, lo, m
    global masked, n, n5471, names, peak, sp, title, w0, weak, z_show, zooms
    # Die Faser auf NGC 5471, der hellen, metallarmen Riesen-H-II-Region am Ostrand von M 101
    n5471 = ch_pos[pd.to_numeric(ch_pos["NGC"], errors="coerce") == 5471]
    c5471 = SkyCoord(n5471["RAJ2000"], n5471["DEJ2000"], unit=(u.hourangle, u.deg))
    cs = SkyCoord(S["ra"].values * u.deg, S["dec"].values * u.deg)
    dist = np.min([cs.separation(c).arcsec for c in c5471], axis=0)
    I_SHOW = int(np.argmin(np.where(gas, dist, np.inf)))
    sp, z_show = SPEC[I_SHOW], S.loc[I_SHOW, "z"]
    masked = sp["iv"] <= 0
    print(f"Faser {S.loc[I_SHOW, 'specObjID']} ({S.loc[I_SHOW, 'instrument']}), {dist[I_SHOW]:.1f}″ von einer CHAOS-Position in NGC 5471, "
          f"R/R25 = {S.loc[I_SHOW, 'RR25']:.2f}")
    for n in ["Hb", "OIII5007", "Ha", "OIII4363"]:
        core = np.abs(sp["w"] - LINES[n] * (1 + z_show)) < 3
        print(f"  {n:9s}: {masked[core].sum()} maskierte Pixel im Linienkern")
    def peak(n):
        # Höhe des höchsten Pixels über dem Median der Umgebung
        lam = LINES[n] * (1 + z_show)
        near, core = np.abs(sp["w"] - lam) < 30, np.abs(sp["w"] - lam) < 2.5
        return np.nanmax(np.where(core & ~masked, sp["f"], np.nan)) - np.median(sp["f"][near])
    print("Spitzenhöhe über dem Kontinuum relativ zu Hγ: " + ", ".join(f"{n} {peak(n) / peak('Hg'):.3f}" for n in
          ["OIII4363", "NII5755", "SIII6312", "OII7320", "OII7330"]))

    fig = plt.figure(figsize=(16, 8))
    ax = fig.add_subplot(2, 1, 1)
    ax.semilogy(sp["w"], np.where(masked, np.nan, sp["f"]), lw=0.6, c="k")
    for k, w0 in enumerate(sp["w"][masked]):
        ax.axvspan(w0 - 1, w0 + 1, color="red", alpha=0.6, lw=0, label="maskierte Pixel (gesättigt)" if k == 0 else None)
    for n, lab in [("OIII4363", "[O III] 4363"), ("Hb", "Hβ"), ("OIII5007", "[O III] 5007"), ("NII5755", "[N II] 5755"),
                   ("SIII6312", "[S III] 6312"), ("Ha", "Hα"), ("OII7320", "[O II] 7320/30"), ("SIII9069", "[S III] 9069")]:
        weak = n in ("OIII4363", "NII5755", "SIII6312", "OII7320")
        ax.text(LINES[n] * (1 + z_show), 0.97, lab, rotation=90, fontsize=8, ha="center", va="top",
                color="tab:red" if weak else "tab:blue", transform=ax.get_xaxis_transform())
    ax.set_ylim(5, 3e5)
    ax.set_xlabel("Wellenlänge (Vakuum) [Å]")
    ax.set_ylabel("Fluss [10⁻¹⁷ erg s⁻¹ cm⁻² Å⁻¹]")
    ax.set_title("NGC 5471 im SDSS-Spektrum: starke Linien (blau) und schwache Temperaturlinien (rot)", fontsize=10)
    ax.legend(fontsize=8, loc="center right")
    zooms = [("Hγ und [O III] 4363", 4364.4, ["Hg", "OIII4363"]), ("[N II] 5755", 5756.2, ["NII5755"]),
             ("[O I] 6300 und [S III] 6312", 6308.0, ["OI6300", "SIII6312"]), ("[O II] 7320 und 7330", 7327.0, ["OII7320", "OII7330"])]
    for k, (title, lam, names) in enumerate(zooms):
        ax = fig.add_subplot(2, 4, 5 + k)
        lo = lam * (1 + z_show)
        m = np.abs(sp["w"] - lo) < 35
        ax.step(sp["w"][m], np.where(masked[m], np.nan, sp["f"][m]), where="mid", lw=0.9, c="k")
        for n in names:
            ax.axvline(LINES[n] * (1 + z_show), c="tab:red", ls=":", lw=1)
        ax.set_xlabel("Wellenlänge [Å]")
        if k == 0:
            ax.set_ylabel("Fluss [10⁻¹⁷ erg s⁻¹ cm⁻² Å⁻¹]")
        ax.set_title(title, fontsize=9)
    fig.tight_layout()
    plt.show()


def line_fits():
    """29. Linienfits mit fester Lage und Breite (Zellen 22 von nebulae_temperature.ipynb)."""
    global EMPTY, F, L, W, _, ax, axes, examples, fig, h, i, j
    global lam, mad, model, n, noise, null, order, r, rec, res, rows, sn
    global sp, xx
    rows = []
    for i in np.where(gas)[0]:
        rec = measure(SPEC[i], S.loc[i, "z"])
        rec.update(i_spec=i, **S.loc[i, ["specObjID", "ra", "dec", "instrument", "RR25", "chaos"]].to_dict())
        rows.append(rec)
    L = pd.DataFrame(rows)
    def sn(name):
        return (L[name] / L[name + "_e"]).fillna(0)

    # Leermessung: dieselbe Messung an Stellen ohne Linie; das S/N sollte um 0 mit Streuung 1 liegen
    EMPTY = [4400, 4560, 5300, 5600, 5800, 6200, 6400, 7200, 7450, 8000]
    null = []
    for _, r in L.iterrows():
        for lam in EMPTY:
            sp = SPEC[r["i_spec"]]
            try:
                res = fit_group(sp, [lam], r["z"], sig=r["width_ratio"] * inst_sigma(sp, lam * (1 + r["z"])))
            except (RuntimeError, ValueError):
                continue
            if res:
                null.append(res["flux"][lam] / res["err"][lam])
    null = np.array(null)
    mad = 1.4826 * np.median(np.abs(null - np.median(null)))
    print(f"{len(L)} Fasern angepasst; Breite der Linien im Median {L['width_ratio'].median():.2f}-mal die Instrumentbreite")
    print(f"Leermessungen: {len(null)}, Mittel {null.mean():+.2f}, Streuung {null.std():.2f} (robust {mad:.2f}); "
          f"|S/N| > 3: {np.mean(np.abs(null) > 3):.1%} (Gauß: 0.3 %); S/N > {SN_AUR:.0f}: {(null > SN_AUR).sum()}")
    print(f"{'Linie':10s} {'gemessen':>9s} {'S/N > 3':>8s} {'S/N > 5':>8s}")
    for n in ["OIII4363", "NII5755", "SIII6312", "OII7320", "OII7330", "SIII9069", "SIII9532", "OII3726"]:
        print(f"{n:10s} {L[n].notna().sum():9d} {(sn(n) > 3).sum():8d} {(sn(n) > 5).sum():8d}")

    # drei Beispiele: starker, mittlerer und knapper Nachweis von [O III] 4363
    order = sn("OIII4363").sort_values(ascending=False)
    examples = [order.index[0], (order - 12).abs().idxmin(), (order - 5.5).abs().idxmin()]
    fig, axes = plt.subplots(1, 4, figsize=(17, 4))
    for ax, j in zip(axes[:3], examples):
        r = L.loc[j]
        res = fit_group(SPEC[r["i_spec"]], ["Hg", "OIII4363"], r["z"])
        W, F, model = res["curve"]
        ax.step(W, F, where="mid", c="k", lw=0.8, label="Daten")
        ax.plot(W, model, c="tab:red", lw=1.2, label="Fit")
        ax.axvline(LINES["OIII4363"] * (1 + r["z"]), c="tab:red", ls=":", lw=1)
        h = res["flux"].get("OIII4363", 0) / (res["sigma"] * np.sqrt(2 * np.pi))      # Höhe der 4363-Linie
        noise = 1.4826 * np.median(np.abs(F - model))
        ax.set_ylim(np.median(F) - 6 * noise, np.median(F) + max(2.5 * h, 10 * noise))
        ax.set_title(f"S/N(4363) = {sn('OIII4363')[j]:.1f}, R/R25 = {r['RR25']:.2f}", fontsize=9)
        ax.set_xlabel("Wellenlänge [Å]")
    axes[0].set_ylabel("Fluss [10⁻¹⁷ erg s⁻¹ cm⁻² Å⁻¹]")
    axes[0].legend(fontsize=8)
    xx = np.linspace(-6, 6, 200)
    axes[3].hist(null, bins=np.arange(-6, 6.5, 0.5), density=True, color="grey", alpha=0.6, label="Leermessungen")
    axes[3].plot(xx, np.exp(-xx ** 2 / 2) / np.sqrt(2 * np.pi), c="k", label="Gauß, Streuung 1")
    axes[3].hist(sn("OIII4363").clip(-6, 30), bins=np.arange(-6, 30.5, 1), density=True, histtype="step", lw=1.5,
                 color="tab:red", label="[O III] 4363 in den Fasern")
    axes[3].axvline(SN_AUR, c="tab:red", ls="--", lw=1, label=f"Schwelle S/N = {SN_AUR:.0f}")
    axes[3].set_xlabel("S/N")
    axes[3].set_ylabel("Dichte")
    axes[3].set_title("Wie oft erfindet das Rauschen eine Linie?", fontsize=9)
    axes[3].legend(fontsize=7)
    fig.suptitle("Hγ mit [O III] 4363: Lage aus der Rotverschiebung, Breite gemeinsam mit Hγ", fontsize=10)
    fig.tight_layout()
    plt.show()


def saturation():
    """30. Gesättigte Linien und Staub (Zellen 25 von nebulae_temperature.ipynb)."""
    global I, R59, axes, bright, d_ebv, ebv_a, ebv_g, fig, lim, ok59, r59, sat5007
    global use_a, use_g
    # [O III] 5007 aus 4959, wo 5007 gesättigt ist: beide Linien kommen vom selben Niveau
    R59 = O3.line(1e4, N_E, LINES["OIII5007"]) / O3.line(1e4, N_E, LINES["OIII4959"])
    sat5007 = L["OIII5007"].isna() & L["OIII4959"].notna()
    L["O5007"] = L["OIII5007"].where(~sat5007, R59 * L["OIII4959"])
    L["O5007_e"] = L["OIII5007_e"].where(~sat5007, R59 * L["OIII4959_e"])
    ok59 = (sn("OIII4959") > 20) & (sn("OIII5007") > 20)
    r59 = L.loc[ok59, "OIII5007"] / L.loc[ok59, "OIII4959"]

    # Staub: Hα/Hβ, wo Hα gesättigt ist Hγ/Hβ
    ebv_a = 2.5 / (K["Hb"] - K["Ha"]) * np.log10(L["Ha"] / L["Hb"] / HA_HB)
    ebv_g = 2.5 / (K["Hb"] - K["Hg"]) * np.log10(L["Hg"] / L["Hb"] / HG_HB)
    use_a = (sn("Ha") > SN_STRONG) & (sn("Hb") > SN_STRONG)
    use_g = ~use_a & (sn("Hg") > SN_STRONG) & (sn("Hb") > SN_STRONG)
    L["EBV_src"] = np.where(use_a, "Ha/Hb", np.where(use_g, "Hg/Hb", "-"))
    L["EBV"] = np.where(use_a, ebv_a, np.where(use_g, ebv_g, np.nan)).clip(0, None)
    L["EW_Hb"] = L["Hb"] / L["cont_Hb"]
    bright = use_a & (sn("Hg") > 30)
    d_ebv = (ebv_a - ebv_g)[bright]

    def I(name, col=None):
        # entrötete Intensität relativ zu Hβ
        return L[col or name] / L["Hb"] * 10 ** (0.4 * L["EBV"] * (K[name] - K["Hb"]))

    print(f"Theorie: 5007/4959 = {R59:.3f}; gemessen in {ok59.sum()} Fasern (S/N > 20): Median {r59.median():.3f}, Streuung {r59.std():.3f}")
    print(f"[O III] 5007 gesättigt und aus 4959 ersetzt: {sat5007.sum()} Fasern; Hα gesättigt: {(L['Ha'].isna() & L['Hb'].notna()).sum()}")
    print(f"Staub aus Hα/Hβ: {use_a.sum()} Fasern, aus Hγ/Hβ: {use_g.sum()}, ohne Staubwert: {(~use_a & ~use_g).sum()}")
    print(f"E(B−V): Median {L['EBV'].median():.2f} mag (16.–84. Perzentil {L['EBV'].quantile(0.16):.2f} bis {L['EBV'].quantile(0.84):.2f})")
    print(f"Hα/Hβ gegen Hγ/Hβ in {bright.sum()} hellen Fasern: Unterschied im Median {d_ebv.median():+.3f} mag, Streuung {d_ebv.std():.3f} mag")
    print(f"Lichtverlust durch Staub bei E(B−V) = {L['EBV'].median():.2f}: [O III] 4363 gegenüber 5007 um "
          f"{1 - 10 ** (-0.4 * L['EBV'].median() * (K['OIII4363'] - K['OIII5007'])):.0%} stärker geschwächt, "
          f"[S III] 6312 gegenüber 9069 um {1 - 10 ** (-0.4 * L['EBV'].median() * (K['SIII6312'] - K['SIII9069'])):.0%}")

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    axes[0].hist(r59, bins=np.arange(2.5, 3.5, 0.04), color="tab:blue", alpha=0.7, label=f"gemessen ({ok59.sum()} Fasern)")
    axes[0].axvline(R59, c="k", ls="--", label=f"Atomphysik: {R59:.2f}")
    axes[0].set_xlabel("[O III] 5007 / 4959")
    axes[0].set_ylabel("Zahl der Fasern")
    axes[0].set_title("Das feste Verhältnis der [O III]-Linien", fontsize=10)
    axes[0].legend(fontsize=8)
    lim = [-0.3, 1.0]
    axes[1].errorbar(ebv_g[bright], ebv_a[bright], fmt="o", ms=4, c="tab:orange")
    axes[1].plot(lim, lim, "k--", lw=1, label="1:1")
    axes[1].set_xlim(lim)
    axes[1].set_ylim(lim)
    axes[1].set_xlabel("E(B−V) aus Hγ/Hβ [mag]")
    axes[1].set_ylabel("E(B−V) aus Hα/Hβ [mag]")
    axes[1].set_title("Zwei Balmer-Dekremente, ein Staub", fontsize=10)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()


def density():
    """31. Die Dichte (Zellen 28 von nebulae_temperature.ipynb)."""
    global R_lim, R_meas, R_ref, R_s2, THERMO, T_true, T_wrong, atom, axes, col, fig, i1
    global i2, lo_pair, n, name, ne_grid, ne_of, ratio, up
    ne_grid = np.logspace(0, 5, 120)
    R_s2 = np.array([S2.line(1e4, n, LINES["SII6717"]) / S2.line(1e4, n, LINES["SII6731"]) for n in ne_grid])
    R_meas = (L["SII6717"] / L["SII6731"])[(sn("SII6717") > SN_STRONG) & (sn("SII6731") > SN_STRONG)]
    R_lim = R_s2[0]
    def ne_of(R):
        return np.interp(R, R_s2[::-1], ne_grid[::-1]) if R < R_lim else np.nan
    print(f"[S II] 6717/6731 in {len(R_meas)} Fasern: Median {R_meas.median():.3f} (16.–84. Perzentil {R_meas.quantile(0.16):.2f} "
          f"bis {R_meas.quantile(0.84):.2f}); Grenzwert für dünnes Gas {R_lim:.3f}")
    print(f"  -> n_e ≈ {ne_of(R_meas.median()):.0f} cm⁻³ aus dem Median, {ne_of(R_meas.quantile(0.84)):.0f} bis "
          f"{ne_of(R_meas.quantile(0.16)):.0f} cm⁻³ aus den Perzentilen; {np.mean(R_meas > R_lim):.0%} liegen über dem Grenzwert")

    # Wie stark hängen die Thermometer von der Dichte ab? Temperatur, die man bei falscher Dichte erhielte
    def ratio(atom, up, lo_pair, T, ne):
        return atom.line(T, ne, LINES[up]) / sum(atom.line(T, ne, LINES[l]) for l in lo_pair)
    THERMO = {"[O III]": (O3, "OIII4363", ["OIII4959", "OIII5007"], "tab:blue"), "[N II]": (N2, "NII5755", ["NII6548", "NII6584"], "tab:green"),
              "[S III]": (S3, "SIII6312", ["SIII9069", "SIII9532"], "tab:orange")}
    T_true = 1e4
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    axes[0].semilogx(ne_grid, R_s2, c="k", label="Fünf-Niveau-Atom, T = 10 000 K")
    axes[0].axhspan(R_meas.quantile(0.16), R_meas.quantile(0.84), color="tab:blue", alpha=0.2, label="gemessen, 16.–84. Perzentil")
    axes[0].axhline(R_meas.median(), c="tab:blue", ls="--", label=f"Median {R_meas.median():.2f}")
    axes[0].axvline(N_E, c="grey", ls=":", label=f"angenommen: {N_E:.0f} cm⁻³")
    axes[0].set_xlabel("Elektronendichte n_e [cm⁻³]")
    axes[0].set_ylabel("[S II] 6717 / 6731")
    axes[0].set_title("Die Dichte aus dem [S II]-Dublett", fontsize=10)
    axes[0].legend(fontsize=8)
    for name, (atom, up, lo_pair, col) in THERMO.items():
        R_ref = ratio(atom, up, lo_pair, T_true, N_E)
        T_wrong = []
        for n in ne_grid:
            try:
                T_wrong.append(brentq(lambda T: ratio(atom, up, lo_pair, T, n) - R_ref, 3000, 40000))
            except ValueError:                                  # bei sehr hoher Dichte keine Lösung im Bereich
                T_wrong.append(np.nan)
        axes[1].semilogx(ne_grid, np.array(T_wrong), c=col, label=name)
        i1, i2 = np.argmin(np.abs(ne_grid - 10)), np.argmin(np.abs(ne_grid - 1000))
        print(f"{name}: angenommene Dichte 10 statt 100 cm⁻³ -> T = {T_wrong[i1]:.0f} K, 1000 cm⁻³ -> {T_wrong[i2]:.0f} K (wahr 10 000 K)")
    axes[1].axvline(N_E, c="grey", ls=":")
    axes[1].set_xlabel("angenommene Elektronendichte [cm⁻³]")
    axes[1].set_ylabel("abgeleitete Temperatur [K]")
    axes[1].set_title(f"Fehler der Temperatur bei falscher Dichte (wahr: {N_E:.0f} cm⁻³, 10 000 K)", fontsize=10)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()


def thermometer():
    """32. Das Atom als Thermometer (Zellen 31 von nebulae_temperature.ipynb)."""
    global CHT, RATIO, TG, T_from, axes, c, ch_T, col, d, fig, i10, kind
    global lab, obs95, of, r95, table
    # Thermometer als Tabellen: Linienverhältnis gegen Temperatur bei N_E
    TG = np.arange(5000.0, 25001.0, 25.0)
    def table(atom, up, lo_list):
        return np.array([atom.line(T, N_E, LINES[up], tol(up)) / sum(atom.line(T, N_E, LINES[l], tol(l)) for l in lo_list) for T in TG])
    RATIO = {"O3": table(O3, "OIII4363", ["OIII4959", "OIII5007"]), "N2": table(N2, "NII5755", ["NII6548", "NII6584"]),
             "S3": table(S3, "SIII6312", ["SIII9069", "SIII9532"])}
    def T_from(kind, R):
        return np.interp(R, RATIO[kind], TG, left=np.nan, right=np.nan)  # das Verhältnis steigt mit T

    # Vereinfachte Formel aus dem Drei-Niveau-Bild (Osterbrock & Ferland 2006, Gl. 5.4)
    of = 1 / (7.90 * np.exp(3.29e4 / TG))
    i10 = np.argmin(np.abs(TG - 1e4))
    print(f"[O III] (4959+5007)/4363 bei 10 000 K: Fünf-Niveau-Atom {1 / RATIO['O3'][i10]:.0f}, "
          f"Osterbrock & Ferland {1 / of[i10]:.0f}; bei 8000 K {1 / RATIO['O3'][np.argmin(np.abs(TG - 8000))]:.0f}, "
          f"bei 13 000 K {1 / RATIO['O3'][np.argmin(np.abs(TG - 13000))]:.0f}")

    # Prüfung: aus den CHAOS-Linienverhältnissen die Temperatur rechnen und mit der von CHAOS vergleichen
    ch_T = pd.DataFrame(index=CH.index)
    ch_T["O3"] = T_from("O3", CH["[OIII]4363"] / (CH["[OIII]4959"] + CH["[OIII]5007"]))
    ch_T["N2"] = T_from("N2", CH["[NII]5755"] / (CH["[NII]6548"] + CH["[NII]6583"]))
    ch_T["S3"] = T_from("S3", CH["[SIII]6312"] / (CH["[SIII]9069"] + CH["[SIII]9531"]))
    CHT = {"O3": "Te([OIII])1", "N2": "Te([NII])1", "S3": "Te([SIII])1"}
    r95 = S3.line(1e4, N_E, LINES["SIII9532"]) / S3.line(1e4, N_E, LINES["SIII9069"])
    ch_T["S3_9069"] = T_from("S3", CH["[SIII]6312"] / (CH["[SIII]9069"] * (1 + r95)))
    for kind, col in CHT.items():
        d = (ch_T[kind] - ch_ab[col].reindex(ch_T.index)).dropna()
        print(f"T{kind} eigen minus CHAOS: {len(d)} Regionen, Median {d.median():+.0f} K, Streuung {d.std():.0f} K")
    d = (ch_T["S3_9069"] - ch_ab["Te([SIII])1"].reindex(ch_T.index)).dropna()
    obs95 = (CH["[SIII]9531"] / CH["[SIII]9069"]).dropna()
    print(f"T[S III] nur aus 9069 (9532 aus der Theorie, {r95:.2f} × 9069): Median {d.median():+.0f} K, Streuung {d.std():.0f} K; "
          f"gemessen 9532/9069 bei CHAOS: Median {obs95.median():.2f}, 16.–84. Perzentil {obs95.quantile(0.16):.2f} bis {obs95.quantile(0.84):.2f}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for kind, lab, c in [("O3", "[O III] 4363 / (4959+5007)", "tab:blue"), ("N2", "[N II] 5755 / (6548+6584)", "tab:green"),
                         ("S3", "[S III] 6312 / (9069+9532)", "tab:orange")]:
        axes[0].semilogy(TG, RATIO[kind], c=c, label=lab)
    axes[0].semilogy(TG, of, "k:", label="[O III] Drei-Niveau-Formel (Osterbrock & Ferland)")
    axes[0].set_xlabel("Elektronentemperatur T [K]")
    axes[0].set_ylabel("Linienverhältnis")
    axes[0].set_title(f"Drei Thermometer (n_e = {N_E:.0f} cm⁻³)", fontsize=10)
    axes[0].legend(fontsize=8)
    for kind, c in [("O3", "tab:blue"), ("N2", "tab:green"), ("S3", "tab:orange")]:
        axes[1].scatter(ch_ab[CHT[kind]].reindex(ch_T.index), ch_T[kind], s=18, c=c, label=f"T{kind}".replace("TO3", "T[O III]")
                        .replace("TN2", "T[N II]").replace("TS3", "T[S III]"))
    axes[1].plot([5000, 17000], [5000, 17000], "k--", lw=1, label="1:1")
    axes[1].set_xlabel("Temperatur bei CHAOS [K]")
    axes[1].set_ylabel("eigene Temperatur aus den CHAOS-Linien [K]")
    axes[1].set_title("Prüfung des eigenen Atoms an den CHAOS-Messungen", fontsize=10)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()


def region_temperatures():
    """33. Die Temperaturen der Regionen (Zellen 34 von nebulae_temperature.ipynb)."""
    global AURORAL, DRAWS, STRONG, ax, axes, c, ch_m, col, dic, draw, dsl, e
    global fig, fit_gradient, hi, ic, j, kind, lab, lo, m, med, mm, r
    global r_n2, s, s_int, sl, t, temperatures
    AURORAL = ["OIII4363", "NII5755", "SIII6312", "OII7320", "OII7330"]
    STRONG = ["Ha", "Hb", "Hg", "O5007", "NII6584", "SIII9069", "OII3726", "OII3729"]
    r_n2 = N2.line(1e4, N_E, LINES["NII6584"]) / N2.line(1e4, N_E, LINES["NII6548"])     # festes Verhältnis 6584/6548

    def draw(row, n=N_MC):
        # Linienflüsse einer Faser n-mal aus ihren Fehlern ziehen; nur Nachweise über der Schwelle
        s = {}
        for k in STRONG + AURORAL:
            if np.isfinite(row.get(k, np.nan)) and row[k] / row[k + "_e"] > (SN_AUR if k in AURORAL else SN_STRONG):
                s[k] = row[k] + row[k + "_e"] * rng.standard_normal(n)
        if not ("OII7320" in s and "OII7330" in s):
            s.pop("OII7320", None)
            s.pop("OII7330", None)
        return s

    def temperatures(s, src):
        # Staub und Temperaturen aus einer Ziehung
        if src == "Ha/Hb" and "Ha" in s:
            ebv = 2.5 / (K["Hb"] - K["Ha"]) * np.log10(s["Ha"] / s["Hb"] / HA_HB)
        elif "Hg" in s:
            ebv = 2.5 / (K["Hb"] - K["Hg"]) * np.log10(s["Hg"] / s["Hb"] / HG_HB)
        else:
            return None
        ebv = np.clip(ebv, 0, None)
        Ii = lambda name, f: f / s["Hb"] * 10 ** (0.4 * ebv * (K[name] - K["Hb"]))
        out = {"EBV": ebv, "I5007": Ii("OIII5007", s["O5007"])}
        if "OIII4363" in s:
            out["T_O3"] = T_from("O3", Ii("OIII4363", s["OIII4363"]) / (out["I5007"] * (1 + 1 / R59)))
        if "NII5755" in s and "NII6584" in s:
            out["T_N2"] = T_from("N2", Ii("NII5755", s["NII5755"]) / (Ii("NII6584", s["NII6584"]) * (1 + 1 / r_n2)))
        if "SIII6312" in s and "SIII9069" in s:
            out["T_S3"] = T_from("S3", Ii("SIII6312", s["SIII6312"]) / (Ii("SIII9069", s["SIII9069"]) * (1 + r95)))
        if "OII7320" in s:
            out["I7325"] = Ii("OII7320", s["OII7320"] + s["OII7330"])
        if "OII3726" in s and "OII3729" in s:
            out["I3727"] = Ii("OII3726", s["OII3726"] + s["OII3729"])
        return out

    def fit_gradient(R, y, e):
        # Gerade mit zusätzlicher innerer Streuung σ_int, so dass χ² pro Freiheitsgrad 1 ist
        R, y, e = map(np.asarray, (R, y, e))
        def chi2_red(s_int):
            w = 1 / (e ** 2 + s_int ** 2)
            p = np.polyfit(R, y, 1, w=np.sqrt(w))
            return np.sum(w * (y - np.polyval(p, R)) ** 2) / (len(y) - 2) - 1
        s_int = brentq(chi2_red, 0, 5 * np.std(y)) if chi2_red(0) > 0 else 0.0
        w = 1 / (e ** 2 + s_int ** 2)
        p, cov = np.polyfit(R, y, 1, w=np.sqrt(w), cov="unscaled")
        return p, np.sqrt(np.diag(cov)), s_int

    DRAWS = {}
    for j, r in L.iterrows():
        if r["EBV_src"] == "-" or not np.isfinite(r.get("O5007", np.nan)):
            continue
        s = draw(r)
        if "Hb" not in s or "O5007" not in s:
            continue
        t = temperatures(s, r["EBV_src"])
        if t:
            DRAWS[j] = t
    for kind in ["T_O3", "T_N2", "T_S3"]:
        med, lo, hi = np.full(len(L), np.nan), np.full(len(L), np.nan), np.full(len(L), np.nan)
        for j, t in DRAWS.items():
            if kind in t and np.isfinite(t[kind]).mean() > 0.9:
                med[j], lo[j], hi[j] = np.nanpercentile(t[kind], [50, 16, 84])
        L[kind], L[kind + "_lo"], L[kind + "_hi"] = med, lo, hi
        e = (L[kind + "_hi"] - L[kind + "_lo"]) / 2
        print(f"{kind}: {L[kind].notna().sum():2d} Fasern, {L[kind].min():.0f} bis {L[kind].max():.0f} K, Median {L[kind].median():.0f} K, "
              f"Fehler im Median ±{e.median():.0f} K")
    m = L["T_O3"].notna()
    (sl, ic), (dsl, dic), s_int = fit_gradient(L.loc[m, "RR25"], L.loc[m, "T_O3"], (L.loc[m, "T_O3_hi"] - L.loc[m, "T_O3_lo"]) / 2)
    print(f"Gerade durch T[O III]: {ic:.0f} ± {dic:.0f} K im Zentrum, {sl:+.0f} ± {dsl:.0f} K pro R25, innere Streuung {s_int:.0f} K")
    ch_m = ch_ab.reindex(ch_pos["HIIid"].values)
    ch_m.index = ch_pos.index
    for kind, col in CHT.items():
        mm = ch_m[col].notna()
        print(f"  CHAOS {col}: {mm.sum()} Regionen, {ch_m.loc[mm, col].min():.0f} bis {ch_m.loc[mm, col].max():.0f} K")

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.6), sharey=True)
    for ax, (kind, lab, c) in zip(axes, [("T_O3", "T[O III] aus 4363/5007", "tab:blue"), ("T_N2", "T[N II] aus 5755/6584", "tab:green"),
                                         ("T_S3", "T[S III] aus 6312/9069", "tab:orange")]):
        mm = L[kind].notna()
        ax.scatter(ch_pos["RgR25"], ch_m[CHT[kind[2:]]], s=12, c="grey", alpha=0.5, label="CHAOS")
        ax.errorbar(L.loc[mm, "RR25"], L.loc[mm, kind], yerr=[L.loc[mm, kind] - L.loc[mm, kind + "_lo"], L.loc[mm, kind + "_hi"] - L.loc[mm, kind]],
                    fmt="o", ms=5, c=c, label=f"SDSS ({mm.sum()} Fasern)")
        ax.set_xlabel("R / R25")
        ax.set_title(lab, fontsize=10)
        ax.legend(fontsize=8)
    axes[0].plot(np.linspace(0, 1.1, 10), ic + sl * np.linspace(0, 1.1, 10), "b--", lw=1)
    axes[0].set_ylabel("Elektronentemperatur [K]")
    axes[0].set_ylim(5000, 20000)
    fig.tight_layout()
    plt.show()


def tt_relations():
    """34. Temperatur gegen Temperatur (Zellen 37 von nebulae_temperature.ipynb)."""
    global TT, a, ax, axes, b, col, d, dc, fig, kind, lab, m
    global tt
    # Temperatur-Temperatur-Beziehungen von CHAOS (Croxall et al. 2016, Gl. 5 und 7; T in 10⁴ K)
    TT = {"T_N2": (0.714, 0.257), "T_S3": (1.265, -0.232)}
    tt = np.linspace(0.5, 1.8, 50)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, (kind, (a, b)), col, lab in zip(axes, TT.items(), ["Te([NII])1", "Te([SIII])1"], ["T[N II]", "T[S III]"]):
        ax.scatter(ch_ab["Te([OIII])1"], ch_ab[col], s=14, c="grey", alpha=0.6, label="CHAOS")
        m = L["T_O3"].notna() & L[kind].notna()
        ax.errorbar(L.loc[m, "T_O3"], L.loc[m, kind],
                    xerr=[L.loc[m, "T_O3"] - L.loc[m, "T_O3_lo"], L.loc[m, "T_O3_hi"] - L.loc[m, "T_O3"]],
                    yerr=[L.loc[m, kind] - L.loc[m, kind + "_lo"], L.loc[m, kind + "_hi"] - L.loc[m, kind]], fmt="o", ms=5, c="tab:red",
                    label=f"SDSS ({m.sum()} Fasern)")
        ax.plot(tt * 1e4, (a * tt + b) * 1e4, "k-", lw=1, label=f"CHAOS-Beziehung (in 10⁴ K): {lab} = {a} T[O III] {b:+.3f}")
        ax.plot(tt * 1e4, tt * 1e4, "k:", lw=1, label="gleiche Temperatur")
        d = L.loc[m, kind] - (a * L.loc[m, "T_O3"] / 1e4 + b) * 1e4
        dc = ch_ab[col] - (a * ch_ab["Te([OIII])1"] / 1e4 + b) * 1e4
        print(f"{lab} gegen T[O III]: {m.sum()} Fasern, Abweichung von der CHAOS-Beziehung Median {d.median():+.0f} K, Streuung {d.std():.0f} K; "
              f"CHAOS selbst: Streuung {dc.std():.0f} K ({dc.notna().sum()} Regionen)")
        ax.set_xlim(6000, 17500)
        ax.set_ylim(5000, 17500)
        ax.set_xlabel("T[O III] [K] (Zone von O²⁺)")
        ax.set_ylabel(f"{lab} [K]")
        ax.set_title(f"{lab} gegen T[O III]", fontsize=10)
        ax.legend(fontsize=7, loc="upper left")
    fig.tight_layout()
    plt.show()


def stacking():
    """35. Stapeln (Zellen 40 von nebulae_temperature.ipynb)."""
    global EW_MIN, F, R_STACK, STACK, T_st, W, _, acc, ax, axes, c, cand
    global dered, e, f, fig, good, grid, hi, k, kind, lam, lo, med
    global mm, mode, model, n, names, r, sd, sig, sp, st, title, v
    global var, w0, w_rest, weights, wsum
    # Innere Fasern ohne sicheren Einzelnachweis von [O III] 4363 im Ruhesystem mitteln
    R_STACK, EW_MIN = 0.45, 30.0          # innen; Gas muss das Sternlicht überstrahlen (Äquivalentbreite von Hβ in Å)
    cand = L[(L["RR25"] < R_STACK) & (sn("OIII4363") < SN_AUR) & (sn("Hb") > 10) & L["EBV"].notna() & (L["instrument"] == "SDSS")
             & (L["EW_Hb"] > EW_MIN)]
    weights = []
    grid = np.arange(3800.0, 9180.0, 0.5)
    acc, wsum, var = np.zeros_like(grid), np.zeros_like(grid), np.zeros_like(grid)
    for _, r in cand.iterrows():
        sp = SPEC[r["i_spec"]]
        w_rest = sp["w"] / (1 + r["z"])
        dered = 10 ** (0.4 * r["EBV"] * (k_ccm(w_rest) - K["Hb"])) / r["Hb"]       # entrötet und relativ zu Hβ
        f = np.interp(grid, w_rest, sp["f"] * dered)
        e = np.interp(grid, w_rest, np.where(sp["iv"] > 0, 1 / np.sqrt(np.where(sp["iv"] > 0, sp["iv"], 1)), np.inf) * dered)
        good = np.isfinite(e)
        for lam in LINES.values():                                  # gesättigte Linie: Spektrum um die ganze Linie herum weglassen
            if (sp["iv"][np.abs(w_rest - lam) < 3] <= 0).any():
                good &= np.abs(grid - lam) > 30
        w0 = 1 / np.median(e[good & (grid > 5100) & (grid < 5600)]) ** 2             # ein festes Gewicht pro Spektrum
        weights.append(w0)
        acc += np.where(good, w0 * f, 0)
        wsum += np.where(good, w0, 0)
        var += np.where(good, w0 ** 2 * e ** 2, 0)
    STACK = {"w": grid, "f": 1e3 * acc / wsum, "iv": (wsum / 1e3) ** 2 / var,
             "wdisp": np.interp(grid, SPEC[cand["i_spec"].iloc[0]]["w"] / (1 + cand["z"].iloc[0]), SPEC[cand["i_spec"].iloc[0]]["wdisp"])}
    st = {}
    for names, mode in GROUPS:
        sig = None
        if mode == "fest":
            sig = cand["width_ratio"].median() * inst_sigma(STACK, LINES[names[0]])
        r = fit_group(STACK, names, 0.0, sig)
        if r:
            for n in r["flux"]:
                st[n], st[n + "_e"] = r["flux"][n] / 1e3, r["err"][n] / 1e3
    weights = np.array(weights)
    print(f"Stapel aus {len(cand)} Fasern mit R/R25 < {R_STACK} und EW(Hβ) > {EW_MIN:.0f} Å (Median R/R25 = {cand['RR25'].median():.2f}), "
          f"einzeln S/N(4363) zwischen {sn('OIII4363')[cand.index].min():.1f} und {sn('OIII4363')[cand.index].max():.1f}")
    print(f"  effektive Zahl der Fasern (Σw)²/Σw² = {weights.sum() ** 2 / (weights ** 2).sum():.1f}; größter Anteil einer Faser "
          f"{weights.max() / weights.sum():.0%}")
    for n in ["Hg", "OIII4363", "OIII5007", "NII5755", "NII6584", "SIII6312", "SIII9069", "OII7320", "OII7330", "Ha"]:
        print(f"  {n:9s} I/Hβ = {st[n]:.4f} ± {st[n + '_e']:.4f}  (S/N {st[n] / st[n + '_e']:.1f})")
    print(f"  Kontrollen: 5007/4959 = {st['OIII5007'] / st['OIII4959']:.2f} (Theorie {R59:.2f}), Hα/Hβ = {st['Ha']:.2f} (Theorie {HA_HB:.2f})")
    sd = {k: st[k] + st[k + "_e"] * rng.standard_normal(4000) for k in ["OIII4363", "OIII5007", "NII5755", "NII6584", "SIII6312", "SIII9069"]}
    T_st = {"T_O3": T_from("O3", sd["OIII4363"] / (sd["OIII5007"] * (1 + 1 / R59))),
            "T_N2": T_from("N2", sd["NII5755"] / (sd["NII6584"] * (1 + 1 / r_n2))),
            "T_S3": T_from("S3", sd["SIII6312"] / (sd["SIII9069"] * (1 + r95)))}
    for k, v in T_st.items():
        lo, med, hi = np.nanpercentile(v, [16, 50, 84])
        print(f"  {k}: {med:.0f} (+{hi - med:.0f} / −{med - lo:.0f}) K")

    fig, axes = plt.subplots(1, 4, figsize=(18, 4))
    for ax, (title, names) in zip(axes[:3], [("Hγ und [O III] 4363", ["Hg", "OIII4363"]), ("[N II] 5755", ["NII5755"]),
                                              ("[O I] 6300 und [S III] 6312", ["OI6300", "SIII6312"])]):
        sig = cand["width_ratio"].median() * inst_sigma(STACK, LINES[names[0]]) if names == ["NII5755"] else None
        r = fit_group(STACK, names, 0.0, sig)
        W, F, model = r["curve"]
        ax.step(W, F / 1e3, where="mid", c="k", lw=0.8, label="Stapel")
        ax.plot(W, model / 1e3, c="tab:red", label="Fit")
        for n in names:
            ax.axvline(LINES[n], c="tab:red", ls=":", lw=1)
        if names[0] == "Hg":
            ax.set_ylim(None, np.median(F / 1e3) + 4 * (st["OIII4363"] / (np.sqrt(2 * np.pi) * 1.3)))
        ax.set_xlabel("Wellenlänge im Ruhesystem [Å]")
        ax.set_title(title, fontsize=9)
    axes[0].set_ylabel("Fluss relativ zu Hβ [Å⁻¹]")
    axes[0].legend(fontsize=8)
    for kind, c in [("T_O3", "tab:blue"), ("T_N2", "tab:green"), ("T_S3", "tab:orange")]:
        mm = L[kind].notna()
        axes[3].scatter(L.loc[mm, "RR25"], L.loc[mm, kind], s=14, c=c, alpha=0.5)
        lo, med, hi = np.nanpercentile(T_st[kind], [16, 50, 84])
        axes[3].errorbar(cand["RR25"].median(), med, yerr=[[med - lo], [hi - med]], fmt="*", ms=14, c=c, mec="k",
                         label=f"Stapel {kind.replace('T_O3', 'T[O III]').replace('T_N2', 'T[N II]').replace('T_S3', 'T[S III]')}")
    axes[3].set_xlabel("R / R25")
    axes[3].set_ylabel("Elektronentemperatur [K]")
    axes[3].set_ylim(5000, 16000)
    axes[3].set_title("Stapel (Sterne) und Einzelfasern (Punkte)", fontsize=9)
    axes[3].legend(fontsize=7)
    fig.tight_layout()
    plt.show()


def abundances():
    """36. Von der Temperatur zur Häufigkeit (Zellen 43 von nebulae_temperature.ipynb)."""
    global D, EMIS, T0, Tl, axes, c, col, d, dop, e, fig, high
    global ionic, j, key, lab, low, oh, op, opp, osrc, sc, src, t
    global zones
    # Emissivitäten relativ zu Hβ als Tabellen
    EMIS = {"O3": np.array([O3.line(T, N_E, LINES["OIII4959"]) + O3.line(T, N_E, LINES["OIII5007"]) for T in TG]),
            "O2b": np.array([O2.line(T, N_E, LINES["OII3726"]) + O2.line(T, N_E, LINES["OII3729"]) for T in TG]),
            "O2r": np.array([O2.line(T, N_E, LINES["OII7320"], 2) + O2.line(T, N_E, LINES["OII7330"], 2) for T in TG]),
            "Hb": j_H(TG)}
    def ionic(I_rel, key, T):
        # n(Ion)/n(H⁺) = I(λ)/I(Hβ) · j(Hβ)/j(λ)
        return I_rel * np.interp(T, TG, EMIS["Hb"] / EMIS[key], left=np.nan, right=np.nan)

    def zones(t):
        # Temperaturen der Zonen von O²⁺ (hoch) und O⁺ (niedrig); fehlende über die CHAOS-Beziehungen
        nan = np.full(len(t["EBV"]), np.nan)
        TO3, TN2, TS3 = t.get("T_O3", nan), t.get("T_N2", nan), t.get("T_S3", nan)
        high = np.where(np.isfinite(TO3), TO3, np.where(np.isfinite(TN2), (TN2 / 1e4 - 0.257) / 0.714 * 1e4,
                                                        (TS3 / 1e4 + 0.232) / 1.265 * 1e4))
        low = np.where(np.isfinite(TN2), TN2, np.where(np.isfinite(TO3), (0.714 * TO3 / 1e4 + 0.257) * 1e4,
                                                       ((TS3 / 1e4 + 0.232) / 1.265 * 0.714 + 0.257) * 1e4))
        src = next((k for k, v in [("[O III]", TO3), ("[N II]", TN2), ("[S III]", TS3)] if np.isfinite(v).mean() > 0.9), "-")
        return high, low, src

    for col in ["OH", "OH_lo", "OH_hi", "Opp_frac", "T_high", "T_low"]:
        L[col] = np.nan
    L["T_src"], L["O_src"] = "-", "-"
    for j, t in DRAWS.items():
        high, low, src = zones(t)
        if src == "-":
            continue
        opp = ionic(t["I5007"] * (1 + 1 / R59), "O3", high)
        if "I3727" in t:
            op, osrc = ionic(t["I3727"], "O2b", low), "3727"
        elif "I7325" in t:
            op, osrc = ionic(t["I7325"], "O2r", low), "7320/7330"
        else:
            continue
        oh = 12 + np.log10(op + opp)
        if np.isfinite(oh).mean() < 0.9:
            continue
        L.loc[j, ["OH_lo", "OH", "OH_hi"]] = np.nanpercentile(oh, [16, 50, 84])
        L.loc[j, ["Opp_frac", "T_high", "T_low"]] = np.nanmedian(opp / (op + opp)), np.nanmedian(high), np.nanmedian(low)
        L.loc[j, ["T_src", "O_src"]] = src, osrc
    D = L[L["OH"].notna()].copy()
    D["OH_e"] = (D["OH_hi"] - D["OH_lo"]) / 2
    print(f"Direkte Sauerstoffhäufigkeit in {len(D)} Fasern; Temperatur aus {D['T_src'].value_counts().to_dict()}, "
          f"O⁺ aus {D['O_src'].value_counts().to_dict()}")
    print(f"12 + log(O/H) von {D['OH'].min():.2f} bis {D['OH'].max():.2f}, Fehler im Median ±{D['OH_e'].median():.3f} dex; "
          f"O²⁺-Anteil von {D['Opp_frac'].min():.0%} bis {D['Opp_frac'].max():.0%}")

    # Wie stark hängt die Häufigkeit an der Temperatur? +500 K bei 8000 und 12 000 K
    for T0 in (8000, 12000):
        for key, lab in [("O3", "O²⁺ aus 5007"), ("O2b", "O⁺ aus 3727"), ("O2r", "O⁺ aus 7320/7330")]:
            d = np.log10(ionic(1.0, key, T0 + 500) / ionic(1.0, key, T0))
            print(f"  T = {T0} K, +500 K: {lab:18s} {d:+.3f} dex")
    # Prüfung an CHAOS: O⁺ aus 7320/7330 statt aus 3727, mit der CHAOS-Temperatur der Zone niedriger Ionisation
    Tl = ch_ab["Te([NII])2"].reindex(CH.index)
    dop = np.log10(ionic(CH["[OII]7320"] + CH["[OII]7330"], "O2r", Tl) / ionic(CH["[OII]3726"] + CH["[OII]3729"], "O2b", Tl)).dropna()
    print(f"CHAOS-Regionen: log O⁺(7320/7330) − log O⁺(3727) = {dop.median():+.3f} im Median, Streuung {dop.std():.3f} ({len(dop)} Regionen)")

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
    for key, lab, c in [("O3", "[O III] 4959+5007 (O²⁺)", "tab:blue"), ("O2b", "[O II] 3726+3729 (O⁺)", "tab:purple"),
                        ("O2r", "[O II] 7320+7330 (O⁺)", "tab:pink")]:
        e = EMIS[key] / EMIS["Hb"]
        axes[0].semilogy(TG, e / e[i10], c=c, label=lab)
    axes[0].axhline(1, c="grey", lw=0.8)
    axes[0].set_xlabel("Elektronentemperatur T [K]")
    axes[0].set_ylabel("j(λ)/j(Hβ), relativ zu 10 000 K")
    axes[0].set_title("Wie hell eine Linie pro Ion ist, hängt steil an T", fontsize=10)
    axes[0].legend(fontsize=8)
    sc = axes[1].scatter(D["RR25"], D["Opp_frac"], c=D["T_high"], cmap="plasma", s=40, edgecolor="k")
    fig.colorbar(sc, ax=axes[1], label="Temperatur der O²⁺-Zone [K]")
    axes[1].set_xlabel("R / R25")
    axes[1].set_ylabel("O²⁺ / (O⁺ + O²⁺)")
    axes[1].set_title("Ionisationsgrad des Sauerstoffs", fontsize=10)
    fig.tight_layout()
    plt.show()


def gradient():
    """37. Der direkte Metallizitätsgradient (Zellen 46 von nebulae_temperature.ipynb)."""
    global axes, dp_own, fig, m, mk, p_own, res, rr, sec, sint_own, src
    p_own, dp_own, sint_own = fit_gradient(D["RR25"], D["OH"], D["OH_e"])
    res = D["OH"] - np.polyval(p_own, D["RR25"])
    print(f"12 + log(O/H) = {p_own[1]:.3f} ± {dp_own[1]:.3f} {p_own[0]:+.3f} ± {dp_own[0]:.3f} · R/R25   ({len(D)} Fasern)")
    print(f"  pro kpc: {p_own[0] / KPC_PER_R25:+.4f} ± {dp_own[0] / KPC_PER_R25:.4f} dex/kpc (R25 = {KPC_PER_R25:.1f} kpc); "
          f"bei R25: {np.polyval(p_own, 1.0):.2f}")
    print(f"  Streuung um die Gerade {res.std():.3f} dex, innere Streuung {sint_own:.3f} dex, Messfehler im Median {D['OH_e'].median():.3f} dex")
    print(f"  zum Vergleich die Sonne: 8.69 (Asplund et al. 2009); Abfall von der Mitte bis R25: {-p_own[0]:.2f} dex = Faktor {10 ** -p_own[0]:.1f}")

    rr = np.linspace(0, 1.1, 50)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), gridspec_kw={"width_ratios": [2, 1]})
    for src, mk in [("[O III]", "o"), ("[N II]", "s"), ("[S III]", "^")]:
        m = D["T_src"] == src
        if m.any():
            axes[0].errorbar(D.loc[m, "RR25"], D.loc[m, "OH"], yerr=[D.loc[m, "OH"] - D.loc[m, "OH_lo"], D.loc[m, "OH_hi"] - D.loc[m, "OH"]],
                             fmt=mk, ms=6, c="tab:red", mec="k", label=f"Temperatur aus {src} ({m.sum()})")
    axes[0].plot(rr, np.polyval(p_own, rr), "k-", label=f"Fit: {p_own[1]:.2f} {p_own[0]:+.2f} R/R25")
    axes[0].fill_between(rr, np.polyval(p_own, rr) - sint_own, np.polyval(p_own, rr) + sint_own, color="grey", alpha=0.2,
                         label=f"innere Streuung ±{sint_own:.2f} dex")
    axes[0].axhline(8.69, c="orange", ls=":", label="Sonne: 8.69")
    axes[0].set_xlabel("R / R25")
    axes[0].set_ylabel("12 + log(O/H), direkte Methode")
    axes[0].set_title("Der direkte Metallizitätsgradient von M 101 aus SDSS-Fasern", fontsize=10)
    axes[0].legend(fontsize=8)
    sec = axes[0].secondary_xaxis("top", functions=(lambda x: x * KPC_PER_R25, lambda x: x / KPC_PER_R25))
    sec.set_xlabel("R [kpc]")
    axes[1].hist(res / np.sqrt(D["OH_e"] ** 2 + sint_own ** 2), bins=np.arange(-3, 3.25, 0.5), color="tab:red", alpha=0.6)
    axes[1].set_xlabel("Abweichung von der Geraden / Gesamtfehler")
    axes[1].set_ylabel("Zahl der Fasern")
    axes[1].set_title("Residuen", fontsize=10)
    fig.tight_layout()
    plt.show()


def fibers_vs_chaos():
    """38. Faser für Faser gegen CHAOS (Zellen 49 von nebulae_temperature.ipynb)."""
    global P, a, axes, b, c, chP, chcol, cmp_rows, cols, d, fig, kind
    global lab, n, ok, own_I, pairs, x, y
    P = L[L["chaos"].notna()].copy()
    pairs = {"Hα": ("Ha", "Halpha6563"), "[O III] 5007": ("OIII5007", "[OIII]5007"), "[N II] 6584": ("NII6584", "[NII]6583"),
             "[S II] 6717": ("SII6717", "[SII]6716"), "[S III] 9069": ("SIII9069", "[SIII]9069"), "[O II] 7320": ("OII7320", "[OII]7320"),
             "[S III] 6312": ("SIII6312", "[SIII]6312"), "[O III] 4363": ("OIII4363", "[OIII]4363"), "[N II] 5755": ("NII5755", "[NII]5755")}
    own_I = lambda n, col: (P[col] / P["Hb"] * 10 ** (0.4 * P["EBV"] * (K[n] - K["Hb"]))).where(sn(col)[P.index] > SN_STRONG)
    print(f"{len(P)} SDSS-Fasern liegen innerhalb von 3″ einer CHAOS-Region; Abstand Faser–Spalt im Median "
          f"{np.median(SkyCoord(P['ra'].values * u.deg, P['dec'].values * u.deg).separation(ch_c[[ch_pos.index[ch_pos['HIIid'] == c][0] for c in P['chaos']]]).arcsec):.1f}″")
    print(f"{'Linie':14s} {'Paare':>5s} {'log(eigen/CHAOS)':>17s} {'Streuung':>9s}")
    cmp_rows = []
    for lab, (n, chcol) in pairs.items():
        a, b = own_I(n, n), CH.loc[P["chaos"], chcol].values
        d = np.log10(a.values / b)
        ok = np.isfinite(d)
        cmp_rows.append((lab, a.values[ok], b[ok]))
        print(f"{lab:14s} {ok.sum():5d} {np.median(d[ok]):+17.3f} {np.std(d[ok]):9.3f}")
    chP = ch_ab.reindex(P["chaos"].values)
    fig, axes = plt.subplots(1, 3, figsize=(17, 5))
    cols = plt.cm.tab10(np.arange(len(cmp_rows)))
    for (lab, a, b), c in zip(cmp_rows, cols):
        axes[0].loglog(b, a, "o", ms=5, c=c, label=lab)
    axes[0].plot([3e-3, 5], [3e-3, 5], "k--", lw=1)
    axes[0].set_xlabel("CHAOS: I(λ)/I(Hβ)")
    axes[0].set_ylabel("SDSS eigen: I(λ)/I(Hβ)")
    axes[0].set_title("Entrötete Linienstärken Faser für Faser", fontsize=10)
    axes[0].legend(fontsize=7, ncol=2)
    for kind, c, lab in [("T_O3", "tab:blue", "T[O III]"), ("T_N2", "tab:green", "T[N II]"), ("T_S3", "tab:orange", "T[S III]")]:
        x, y = chP[CHT[kind[2:]]].values, P[kind].values
        ok = np.isfinite(x) & np.isfinite(y)
        axes[1].errorbar(x[ok], y[ok], yerr=[(P[kind] - P[kind + "_lo"]).values[ok], (P[kind + "_hi"] - P[kind]).values[ok]],
                         fmt="o", ms=5, c=c, label=f"{lab} ({ok.sum()})")
        if ok.any():
            print(f"{lab}: {ok.sum()} Paare, eigen minus CHAOS: " + ", ".join(f"{v:+.0f}" for v in (y - x)[ok]) + " K")
    axes[1].plot([6000, 15000], [6000, 15000], "k--", lw=1)
    axes[1].set_xlabel("CHAOS [K]")
    axes[1].set_ylabel("SDSS eigen [K]")
    axes[1].set_title("Temperaturen", fontsize=10)
    axes[1].legend(fontsize=8)
    x, y = chP["12+log(O/H)"].values, P["OH"].values
    ok = np.isfinite(x) & np.isfinite(y)
    axes[2].errorbar(x[ok], y[ok], xerr=chP["e_12+log(O/H)"].values[ok],
                     yerr=[(P["OH"] - P["OH_lo"]).values[ok], (P["OH_hi"] - P["OH"]).values[ok]], fmt="o", ms=6, c="tab:red")
    axes[2].plot([7.8, 8.9], [7.8, 8.9], "k--", lw=1, label="1:1")
    axes[2].set_xlabel("12 + log(O/H) bei CHAOS")
    axes[2].set_ylabel("12 + log(O/H) eigen (SDSS)")
    axes[2].set_title(f"Sauerstoffhäufigkeit ({ok.sum()} Paare)", fontsize=10)
    axes[2].legend(fontsize=8)
    print(f"O/H: {ok.sum()} Paare, eigen minus CHAOS: " + ", ".join(f"{v:+.2f}" for v in (y - x)[ok]) +
          f"; Median {np.median((y - x)[ok]):+.3f}, Streuung {np.std((y - x)[ok]):.3f} dex")
    fig.tight_layout()
    plt.show()


def gradient_vs_chaos():
    """39. Der Gradient gegen CHAOS (Zellen 52 von nebulae_temperature.ipynb)."""
    global PAPER, R0, ax, chg, dp_ch, dv, fig, name, p_ch, pdv, pv, rr
    global sint_ch, v
    chg = pd.DataFrame({"R": ch_pos.set_index("HIIid")["RgR25"], "OH": ch_ab["12+log(O/H)"], "e": ch_ab["e_12+log(O/H)"]}).dropna()
    p_ch, dp_ch, sint_ch = fit_gradient(chg["R"], chg["OH"], chg["e"])
    PAPER = (8.716, 0.023, -0.832, 0.044)                    # Croxall et al. (2016), Gl. 10
    print(f"CHAOS, eigener Fit an die Tabelle ({len(chg)} Regionen): {p_ch[1]:.3f} ± {dp_ch[1]:.3f} {p_ch[0]:+.3f} ± {dp_ch[0]:.3f} R/R25, "
          f"innere Streuung {sint_ch:.3f} dex")
    print(f"CHAOS im Paper: {PAPER[0]} ± {PAPER[1]} {PAPER[2]:+.3f} ± {PAPER[3]} R/R25, innere Streuung 0.074 dex")
    print(f"SDSS eigen ({len(D)} Fasern): {p_own[1]:.3f} ± {dp_own[1]:.3f} {p_own[0]:+.3f} ± {dp_own[0]:.3f} R/R25, innere Streuung {sint_own:.3f} dex")
    for name, (v, dv, pv, pdv) in {"Achsenabschnitt": (p_own[1], dp_own[1], PAPER[0], PAPER[1]),
                                   "Steigung": (p_own[0], dp_own[0], PAPER[2], PAPER[3])}.items():
        print(f"  {name}: Unterschied {v - pv:+.3f} = {(v - pv) / np.hypot(dv, pdv):+.1f} σ")
    for R0 in (0.2, 0.5, 0.8):
        print(f"  bei R/R25 = {R0}: SDSS {np.polyval(p_own, R0):.2f}, CHAOS {PAPER[0] + PAPER[2] * R0:.2f}")

    rr = np.linspace(0, 1.15, 50)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.errorbar(chg["R"], chg["OH"], yerr=chg["e"], fmt="o", ms=4, c="grey", alpha=0.6, label=f"CHAOS, Spaltspektren ({len(chg)})")
    ax.errorbar(D["RR25"], D["OH"], yerr=[D["OH"] - D["OH_lo"], D["OH_hi"] - D["OH"]], fmt="o", ms=6, c="tab:red", mec="k",
                label=f"SDSS-Fasern, eigene Messung ({len(D)})")
    ax.plot(rr, PAPER[0] + PAPER[2] * rr, c="k", lw=1.5, label=f"CHAOS: {PAPER[0]} {PAPER[2]:+.3f} R/R25")
    ax.plot(rr, np.polyval(p_own, rr), c="tab:red", ls="--", lw=1.5, label=f"eigen: {p_own[1]:.3f} {p_own[0]:+.3f} R/R25")
    ax.set_xlabel("R / R25")
    ax.set_ylabel("12 + log(O/H)")
    ax.set_title("Der direkte Gradient von M 101: SDSS-Fasern gegen CHAOS", fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()


def strong_lines():
    """40. Starke Linien gegen die direkte Methode (Zellen 55 von nebulae_temperature.ipynb)."""
    global CAL, L, axes, c, cols, d, fig, ids, m, mpa, name, p_cal
    global rr, sf, val
    # Häufigkeiten aus starken Linien für alle Fasern mit Sternentstehung
    ids = ",".join(L["specObjID"])
    mpa = sdss_query(f"SELECT e.specObjID, e.oh_p50 FROM galSpecExtra AS e WHERE e.specObjID IN ({ids})").to_pandas()
    mpa["specObjID"] = mpa["specObjID"].astype(str)
    L = L.drop(columns=[c for c in ["oh_p50"] if c in L]).merge(mpa, on="specObjID", how="left")
    L["oh_p50"] = L["oh_p50"].where(L["oh_p50"] > 0)
    L["logN2"] = np.log10(L["NII6584"] / L["Ha"])
    L["logO3"] = np.log10(L["O5007"] / L["Hb"])
    L["O3N2"] = L["logO3"] - L["logN2"]
    sf = ((sn("Ha") > SN_STRONG) & (sn("Hb") > SN_STRONG) & (sn("NII6584") > SN_STRONG) & (L["O5007"] / L["O5007_e"] > SN_STRONG)
          & (L["logN2"] < 0) & (L["logO3"] < 0.61 / (L["logN2"] - 0.05) + 1.30))      # unter der Kauffmann-Linie im BPT-Diagramm
    CAL = {"N2, Pettini & Pagel (2004)": 8.90 + 0.57 * L["logN2"], "O3N2, Pettini & Pagel (2004)": 8.73 - 0.32 * L["O3N2"],
           "N2, Marino et al. (2013)": 8.743 + 0.462 * L["logN2"], "O3N2, Marino et al. (2013)": 8.533 - 0.214 * L["O3N2"],
           "MPA-JHU, Tremonti et al. (2004)": L["oh_p50"]}
    print(f"{sf.sum()} Fasern mit Sternentstehung und allen vier starken Linien; {L.loc[sf, 'oh_p50'].notna().sum()} davon mit MPA-JHU-Wert")
    print(f"{'Eichung':34s} {'Paare':>5s} {'minus direkt':>13s} {'Streuung':>9s} {'Gradient [dex/R25]':>19s}")
    p_cal = {}
    for name, val in CAL.items():
        d = (val - L["OH"])[L["OH"].notna() & sf]
        m = sf & val.notna()
        p_cal[name] = np.polyfit(L.loc[m, "RR25"], val[m], 1)
        print(f"{name:34s} {d.notna().sum():5d} {d.median():+13.3f} {d.std():9.3f} {p_cal[name][0]:+19.3f}")
    print(f"{'direkt (Schritt 37)':34s} {'':5s} {'':>13s} {'':>9s} {p_own[0]:+19.3f}")

    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
    cols = ["tab:blue", "tab:cyan", "tab:green", "lime", "tab:purple"]
    for (name, val), c in zip(CAL.items(), cols):
        m = L["OH"].notna() & sf & val.notna()
        axes[0].scatter(L.loc[m, "OH"], val[m], s=30, c=c, edgecolor="k", lw=0.5, label=name)
    axes[0].plot([7.6, 9.4], [7.6, 9.4], "k--", lw=1, label="1:1")
    axes[0].set_xlabel("12 + log(O/H), direkte Methode")
    axes[0].set_ylabel("12 + log(O/H) aus starken Linien")
    axes[0].set_title("Starke Linien gegen die direkte Methode, Faser für Faser", fontsize=10)
    axes[0].legend(fontsize=7)
    rr = np.linspace(0, 1.1, 50)
    for (name, val), c in zip(CAL.items(), cols):
        axes[1].plot(rr, np.polyval(p_cal[name], rr), c=c, lw=1.5, label=name)
    axes[1].errorbar(D["RR25"], D["OH"], yerr=D["OH_e"], fmt="o", ms=5, c="tab:red", mec="k", label="direkt (SDSS)")
    axes[1].plot(rr, np.polyval(p_own, rr), c="tab:red", lw=2, ls="--", label="direkt, Fit")
    axes[1].plot(rr, PAPER[0] + PAPER[2] * rr, c="k", lw=1, label="direkt, CHAOS")
    axes[1].set_xlabel("R / R25")
    axes[1].set_ylabel("12 + log(O/H)")
    axes[1].set_title(f"Gradienten aus {sf.sum()} Fasern in fünf Eichungen", fontsize=10)
    axes[1].legend(fontsize=7)
    fig.tight_layout()
    plt.show()
