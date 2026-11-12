"""SDSS-Spektren für multiwavelength_astronomy.ipynb: das Licht einzelner Stellen einer Galaxie, Emissionslinien, BPT.

Daten: Sloan Digital Sky Survey, Data Release 17. Die Suche läuft als SQL über SkyServer
(skyserver.sdss.org/dr17/SkyServerWS/SearchTools/SqlSearch): alle Spektren in einem Kasten um das Objekt, deren
Geschwindigkeit innerhalb von 600 km/s der Geschwindigkeit laut SIMBAD liegt, mit den Linienflüssen des MPA-JHU-Katalogs
(galSpecLine) zum Vergleich. Die Spektren selbst (spec-lite, je etwa 0.2 MB) kommen von data.sdss.org. Alles über
requests, mit Cache. Die Linien passt das Modul selbst an (Gaußprofile auf einem linearen Kontinuum) und zeichnet das
BPT-Diagramm (Baldwin, Phillips, Terlevich 1981) vor 20 000 SDSS-Galaxien.
"""
import io
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt
from astropy.io import fits
from scipy.optimize import curve_fit

import catalog

SQL_URL = "https://skyserver.sdss.org/dr17/SkyServerWS/SearchTools/SqlSearch"
SAS = "https://data.sdss.org/sas/dr17"
C_KMS = 299792.458
# Ruhewellenlängen im Vakuum [Å] (SDSS misst im Vakuum)
LINES = {"OII3727": 3727.09, "OII3729": 3729.88, "Hb": 4862.68, "OIII4959": 4960.30, "OIII5007": 5008.24,
         "NII6548": 6549.86, "Ha": 6564.61, "NII6584": 6585.27, "SII6717": 6718.29, "SII6731": 6732.67}
LABELS = {"OII3727": "[O II]", "Hb": "Hβ", "OIII5007": "[O III]", "Ha": "Hα", "NII6584": "[N II]", "SII6717": "[S II]"}
ABSORPTION = {"Ca K": 3934.78, "Ca H": 3969.59, "Mg b": 5176.7, "Na D": 5895.6}
GROUPS = [["Hb", "OIII4959", "OIII5007"], ["NII6548", "Ha", "NII6584"], ["SII6717", "SII6731"]]


def sql(query, cache_file, tries=3):
    """SQL an SkyServer, Ergebnis als DataFrame (Cache als CSV)."""
    cache_file = Path(cache_file)
    if cache_file.exists():
        return pd.read_csv(cache_file)
    for i in range(tries):
        try:
            txt = requests.get(SQL_URL, params={"cmd": query, "format": "csv"}, timeout=180).text
            lines = txt.splitlines()
            head = next(k for k, l in enumerate(lines) if l and not l.startswith("#"))
            df = pd.read_csv(io.StringIO("\n".join(lines[head:])))
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(cache_file, index=False)
            return df
        except (requests.RequestException, StopIteration, pd.errors.ParserError):
            time.sleep(5 * (i + 1))
    raise OSError("SDSS SkyServer nicht erreichbar")


def radial_velocity(target):
    """Radialgeschwindigkeit laut SIMBAD [km/s]; NaN, wenn keine bekannt ist."""
    q = target.main_id.replace("'", "''")
    df = catalog.simbad(f"SELECT b.rvz_radvel FROM basic AS b WHERE b.main_id = '{q}'")
    return float(df["rvz_radvel"].iloc[0]) if len(df) and np.isfinite(df["rvz_radvel"].iloc[0]) else float("nan")


def find(target, cache_dir, dv=600, max_n=60):
    """SDSS-Spektren im Kasten um die Größe des Objekts mit Geschwindigkeit v_sys ± dv, nach S/N sortiert."""
    folder = Path(cache_dir) / "".join(c if c.isalnum() else "_" for c in target.name.strip()) / "sdss"
    v = radial_velocity(target)
    v0 = 0.0 if not np.isfinite(v) else v
    r = target.size / 2 / 60
    dra = r / np.cos(np.radians(target.dec))
    df = sql(f"""
        SELECT TOP {max_n} s.specObjID, s.ra, s.dec, s.z, s.class, s.subClass, s.plate, s.mjd, s.fiberID, s.run2d,
               s.snMedian, l.h_alpha_flux AS mpa_ha, l.h_beta_flux AS mpa_hb, l.oiii_5007_flux AS mpa_oiii,
               l.nii_6584_flux AS mpa_nii
        FROM SpecObj AS s LEFT JOIN galSpecLine AS l ON l.specObjID = s.specObjID
        WHERE s.ra BETWEEN {target.ra - dra} AND {target.ra + dra} AND s.dec BETWEEN {target.dec - r} AND {target.dec + r}
          AND s.z BETWEEN {(v0 - dv) / C_KMS} AND {(v0 + dv) / C_KMS}
        ORDER BY s.snMedian DESC""", folder / "specobj.csv")
    df["subClass"] = df["subClass"].fillna("").astype(str)
    df["dx"] = (df["ra"] - target.ra) * np.cos(np.radians(target.dec)) * 60      # Bogenminuten, Osten positiv
    df["dy"] = (df["dec"] - target.dec) * 60
    vtext = f"{v:.0f} km/s laut SIMBAD" if np.isfinite(v) else "unbekannt, angenommen 0 km/s"
    print(f"{target.name}: Geschwindigkeit {vtext}; im Kasten von {target.size:.1f}′ mit ±{dv} km/s "
          f"{len(df)} SDSS-Spektren" + (f" ({', '.join(f'{n} {k}' for k, n in df['class'].value_counts().items())})" if len(df) else ""))
    return df.reset_index(drop=True), folder


def _get(args):
    row, folder = args
    plate, mjd, fiber, run2d = int(row.plate), int(row.mjd), int(row.fiberID), str(row.run2d).strip()
    name = f"spec-{plate:04d}-{mjd}-{fiber:04d}.fits"
    path = folder / name
    if path.exists():
        return path
    survey = "eboss" if run2d.startswith("v") else "sdss"
    url = f"{SAS}/{survey}/spectro/redux/{run2d}/spectra/lite/{plate:04d}/{name}"
    for i in range(3):
        try:
            d = requests.get(url, timeout=60).content
            if d[:6] == b"SIMPLE":
                path.write_bytes(d)
                return path
        except requests.RequestException:
            pass
        time.sleep(2 * (i + 1))
    return None


def download(df, folder, workers=8):
    """Spektren laden (Cache); gibt je Zeile (Wellenlänge, Fluss, Fehler) oder None zurück."""
    folder.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(workers) as ex:
        paths = list(ex.map(_get, [(r, folder) for r in df.itertuples()]))
    out = []
    for p in paths:
        if p is None:
            out.append(None)
            continue
        with fits.open(p) as h:
            d = h[1].data
            ivar = np.array(d["ivar"], dtype=float)
            err = np.where(ivar > 0, 1 / np.sqrt(np.where(ivar > 0, ivar, 1)), np.nan)
            out.append((10 ** np.array(d["loglam"], dtype=float), np.array(d["flux"], dtype=float), err))
    print(f"{sum(o is not None for o in out)} von {len(df)} Spektren geladen (Cache {folder.parent.name}/sdss/)")
    return out


def fit_group(wave, flux, err, names, z0):
    """Gaußlinien mit gemeinsamer Rotverschiebung und Breite auf einem linearen Kontinuum. Gibt Flüsse und Fehler."""
    lam0 = np.array([LINES[n] for n in names])
    m = (wave > lam0.min() * (1 + z0) - 30) & (wave < lam0.max() * (1 + z0) + 30) & np.isfinite(err)
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
    k = np.sqrt(2 * np.pi)
    fl = {n: popt[4 + i] * popt[1] * k for i, n in enumerate(names)}
    er = {n: np.hypot(perr[4 + i] * popt[1], popt[4 + i] * perr[1]) * k for i, n in enumerate(names)}
    return fl, er, popt[0], (w, model(w, *popt))


def measure(df, specs, sn_min=3):
    """Linienflüsse aller Spektren; BPT-Verhältnisse für Spektren mit S/N > sn_min in allen vier Linien."""
    rows, curves = [], {}
    for i, (r, s) in enumerate(zip(df.itertuples(), specs)):
        rec = {"nr": i + 1, "class": df["class"].iloc[i].strip(), "subClass": r.subClass}
        if s is None:
            rows.append(rec)
            continue
        wave, flux, err = s
        try:
            for grp in GROUPS:
                fl, er, z, curve = fit_group(wave, flux, err, grp, r.z)
                for n in grp:
                    rec[n], rec[n + "_err"] = fl[n], er[n]
                curves.setdefault(i, []).append(curve)
                if "Ha" in grp:
                    rec["v"] = z * C_KMS
        except (RuntimeError, ValueError):
            pass
        rows.append(rec)
    L = pd.DataFrame(rows)
    for n in ["Hb", "OIII5007", "Ha", "NII6584"]:
        if n not in L:
            L[n], L[n + "_err"] = np.nan, np.nan
    ok = np.all([L[n] > sn_min * L[n + "_err"] for n in ["Hb", "OIII5007", "Ha", "NII6584"]], axis=0)
    L["x"] = np.where(ok, np.log10(L["NII6584"] / L["Ha"]), np.nan)       # log [N II]/Hα
    L["y"] = np.where(ok, np.log10(L["OIII5007"] / L["Hb"]), np.nan)      # log [O III]/Hβ
    mpa = df[["mpa_ha", "mpa_hb", "mpa_oiii", "mpa_nii"]].to_numpy(dtype=float)
    pos = np.all(mpa > 0, axis=1)                                         # MPA-JHU: alle vier Linien positiv
    safe = np.where(pos[:, None], mpa, 1.0)
    L["x_mpa"] = np.where(pos, np.log10(safe[:, 3] / safe[:, 0]), np.nan)
    L["y_mpa"] = np.where(pos, np.log10(safe[:, 2] / safe[:, 1]), np.nan)
    L["typ"] = [bpt_class(x, y) for x, y in zip(L["x"], L["y"])]
    L["typ_mpa"] = [bpt_class(x, y) for x, y in zip(L["x_mpa"], L["y_mpa"])]
    return L, curves


def kauffmann(x):
    """Obere Grenze der Sternentstehung (Kauffmann und andere 2003), für log [N II]/Hα < 0.05."""
    return 0.61 / (x - 0.05) + 1.3


def kewley(x):
    """Größtmögliche Sternentstehung im Modell (Kewley und andere 2001), für log [N II]/Hα < 0.47."""
    return 0.61 / (x - 0.47) + 1.19


def bpt_class(x, y):
    if not (np.isfinite(x) and np.isfinite(y)):
        return ""
    if x < 0.05 and y < kauffmann(x):
        return "Sternentstehung"
    if x < 0.47 and y < kewley(x):
        return "Übergang"
    return "AGN oder LINER"


def reference(cache_dir, n=20000):
    """BPT-Verhältnisse von n SDSS-Galaxien aus dem MPA-JHU-Katalog (alle vier Linien mit S/N > 3)."""
    df = sql(f"""SELECT TOP {n} l.h_alpha_flux AS ha, l.h_beta_flux AS hb, l.oiii_5007_flux AS oiii, l.nii_6584_flux AS nii
        FROM galSpecLine AS l WHERE l.h_alpha_flux > 3 * l.h_alpha_flux_err AND l.h_beta_flux > 3 * l.h_beta_flux_err
          AND l.oiii_5007_flux > 3 * l.oiii_5007_flux_err AND l.nii_6584_flux > 3 * l.nii_6584_flux_err""",
             Path(cache_dir) / "sdss_bpt_reference.csv")
    df = df[(df[["ha", "hb", "oiii", "nii"]] > 0).all(axis=1)]          # einige Einträge haben Fluss 0
    return np.log10(df["nii"] / df["ha"]), np.log10(df["oiii"] / df["hb"])


def plot_spectra(target, df, specs, image=None, fov=None, n_show=5):
    """Links die Fasern auf einem Bild (Nummern = Reihenfolge nach S/N), rechts die Spektren mit den wichtigsten Linien."""
    if not len(df):
        print("Keine SDSS-Spektren: Das Objekt liegt außerhalb der Felder von SDSS oder hat keine passende Geschwindigkeit.")
        return
    show = [i for i in range(len(df)) if specs[i] is not None][:n_show]
    fig, axes = plt.subplots(1, 2, figsize=(15, 6), gridspec_kw={"width_ratios": [1, 1.9]})
    ax = axes[0]
    if image is not None and fov is not None:
        h = fov / 2
        a, b = np.nanpercentile(image, [20, 99.7])
        ax.imshow(np.clip((image - a) / (b - a), 0, 1) ** 0.5, origin="lower", cmap="gray", extent=[h, -h, -h, h])
    colors = {"GALAXY": "cyan", "STAR": "yellow", "QSO": "magenta"}
    for cls, c in colors.items():
        m = df["class"].str.strip() == cls
        if m.any():
            ax.scatter(df.loc[m, "dx"], df.loc[m, "dy"], s=40, facecolors="none", edgecolors=c, label=f"{cls} ({m.sum()})")
    for i in show:
        ax.annotate(str(i + 1), (df["dx"][i], df["dy"][i]), xytext=(4, 4), textcoords="offset points", color="red", fontsize=10)
    ax.set_xlabel("ΔRA [′] (Osten links)")
    ax.set_ylabel("ΔDec [′]")
    ax.set_title(f"{target.name}: SDSS-Fasern (3″) auf DSS2 Red", fontsize=10)
    ax.legend(fontsize=8, loc="lower left")
    ax = axes[1]
    for k, i in enumerate(show):
        wave, flux, err = specs[i]
        rest = wave / (1 + df["z"][i])
        norm = np.nanpercentile(flux[(rest > 4000) & (rest < 9000)], 95)        # Höhe des Kontinuums
        y = np.clip(flux / norm, -0.2, 1.4) / 1.4                                 # starke Linien oben gekappt
        ax.plot(rest, y - 1.1 * k, lw=0.5, color=plt.cm.tab10(k))
        ax.text(9250, -1.1 * k + 0.88, f"{i + 1}: {df['class'][i].strip()} {df['subClass'][i]}".strip(), fontsize=8,
                ha="right", va="bottom", color=plt.cm.tab10(k))
    for n, lab in LABELS.items():
        ax.axvline(LINES[n], color="tab:red", lw=0.6, alpha=0.4)
        shift = {"Ha": -25, "NII6584": 25}.get(n, 0)                         # Hα und [N II] liegen 20 Å auseinander
        ax.text(LINES[n] + shift, 1.08, lab, color="tab:red", fontsize=8, ha="center", rotation=90, va="bottom")
    for lab, l in ABSORPTION.items():
        ax.axvline(l, color="tab:blue", lw=0.6, alpha=0.4, ls="--")
        ax.text(l, 1.08, lab, color="tab:blue", fontsize=8, ha="center", rotation=90, va="bottom")
    ax.set_xlim(3600, 9300)
    ax.set_ylim(-1.1 * (len(show) - 1) - 0.3, 1.45)
    ax.set_yticks([])
    ax.set_xlabel("Ruhewellenlänge [Å] (rot: Emission, blau gestrichelt: Absorption)")
    ax.set_title(f"Die {len(show)} Spektren mit dem höchsten Signal-Rausch-Verhältnis (auf das Kontinuum normiert, versetzt)",
                 fontsize=10)
    fig.tight_layout()
    plt.show()


def plot_bpt(target, df, specs, L, curves, cache_dir, n_left=4, n_print=8):
    """Links Hα und [N II] einzelner Fasern (mit Fit, wo er gelingt), rechts das BPT-Diagramm vor den SDSS-Galaxien.

    Gefüllte Punkte: eigener Fit (lineares Kontinuum). Offene Punkte: MPA-JHU-Katalog, der vorher ein Modell des
    Sternlichts abzieht; bei Fasern mit starker Absorption (Kern alter Galaxien) gibt es nur diese Werte.
    """
    own = L.dropna(subset=["x", "y"])
    mpa_only = L[L["x"].isna() & L["x_mpa"].notna()]
    if not len(own) and not len(mpa_only):
        print("Kein Spektrum hat Hβ, [O III], Hα und [N II] mit S/N > 3; kein BPT-Diagramm.")
        return
    counts = own["typ"].value_counts()
    print(f"BPT aus dem eigenen Fit: {len(own)} Fasern (" + ", ".join(f"{k} {v}" for k, v in counts.items()) + ")"
          + (f"; nur aus MPA-JHU: {len(mpa_only)}" if len(mpa_only) else ""))
    for r in list(own.itertuples())[:n_print]:
        m = f"; MPA-JHU ({r.x_mpa:+.2f}, {r.y_mpa:+.2f})" if np.isfinite(r.x_mpa) else ""
        print(f"  {r.nr:2d} {r.subClass:12s} v = {r.v:4.0f} km/s, log [N II]/Hα = {r.x:+.2f}, log [O III]/Hβ = {r.y:+.2f}"
              f" → {r.typ}{m}")
    if len(own) > n_print:
        print(f"  … und {len(own) - n_print} weitere")
    for r in mpa_only.itertuples():
        print(f"  {r.nr:2d} {r.subClass:12s} eigener Fit: eine der vier Linien unter S/N 3; "
              f"MPA-JHU: log [N II]/Hα = {r.x_mpa:+.2f}, log [O III]/Hβ = {r.y_mpa:+.2f} → {r.typ_mpa}")
    xr, yr = reference(cache_dir)
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5), gridspec_kw={"width_ratios": [1.3, 1]})
    ax = axes[0]
    left = list(mpa_only.itertuples())[:1] + list(own.itertuples())[:n_left - min(1, len(mpa_only))]
    for k, r in enumerate(left):
        i = r.nr - 1
        wave, flux, err = specs[i]
        z = df["z"][i]
        m = (wave / (1 + z) > 6530) & (wave / (1 + z) < 6600)
        lo, top = np.nanmin(flux[m]), np.nanmax(flux[m])
        typ = r.typ if isinstance(r.typ, str) and r.typ else f"{r.typ_mpa} (MPA-JHU)"
        ax.plot(wave[m] / (1 + z), (flux[m] - lo) / (top - lo) - 1.2 * k, lw=0.8, color=plt.cm.tab10(r.nr % 10),
                label=f"{r.nr}: {typ}")
        if np.isfinite(r.x) and i in curves:
            w, model = curves[i][1]
            mm = (w / (1 + z) > 6530) & (w / (1 + z) < 6600)
            ax.plot(w[mm] / (1 + z), (model[mm] - lo) / (top - lo) - 1.2 * k, lw=1, color="black", ls="--")
    for n in ["NII6548", "Ha", "NII6584"]:
        ax.axvline(LINES[n], color="grey", lw=0.5)
    ax.set_xlabel("Ruhewellenlänge [Å] ([N II] 6550, Hα 6565, [N II] 6585)")
    ax.set_yticks([])
    ax.set_title("Hα und [N II] einzelner Fasern, Gauß-Fit gestrichelt", fontsize=10)
    ax.legend(fontsize=8, loc="lower left")
    ax = axes[1]
    ax.hexbin(xr, yr, gridsize=80, extent=(-1.6, 0.6, -1.2, 1.4), bins="log", cmap="Greys", mincnt=1)
    xx = np.linspace(-1.6, 0.0, 200)
    ax.plot(xx, kauffmann(xx), color="tab:blue", label="Kauffmann 2003: darunter Sternentstehung")
    xx = np.linspace(-1.6, 0.4, 200)
    ax.plot(xx, kewley(xx), color="tab:red", ls="--", label="Kewley 2001: darüber AGN oder LINER")
    ax.scatter(own["x"], own["y"], s=45, c=[plt.cm.tab10(n % 10) for n in own["nr"]], edgecolor="black", zorder=3,
               label="eigener Fit")
    allm = L.dropna(subset=["x_mpa", "y_mpa"])
    ax.scatter(allm["x_mpa"], allm["y_mpa"], s=60, facecolors="none", edgecolors=[plt.cm.tab10(n % 10) for n in allm["nr"]],
               zorder=3, label="MPA-JHU")
    for r in list(own.itertuples())[:n_print] + list(mpa_only.itertuples()):
        x, y = (r.x, r.y) if np.isfinite(r.x) else (r.x_mpa, r.y_mpa)
        ax.annotate(str(r.nr), (x, y), xytext=(5, 4), textcoords="offset points", fontsize=9)
    ax.text(-1.5, 1.2, "Sternentstehung", fontsize=9, color="tab:blue")
    ax.text(0.05, 1.2, "AGN, LINER", fontsize=9, color="tab:red")
    ax.set_xlim(-1.6, 0.6)
    ax.set_ylim(-1.2, 1.4)
    ax.set_xlabel("log [N II] 6585 / Hα")
    ax.set_ylabel("log [O III] 5008 / Hβ")
    n_ref = f"{len(xr):,}".replace(",", " ")
    ax.set_title(f"BPT-Diagramm: {target.name} vor {n_ref} SDSS-Galaxien (grau)", fontsize=10)
    ax.legend(fontsize=8, loc="lower left")
    fig.tight_layout()
    plt.show()
