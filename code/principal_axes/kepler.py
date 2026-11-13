"""Kepler-Lichtkurven für principal_axes.ipynb: gemeinsame Systematik vieler Sterne als Hauptachsen finden und entfernen.

Daten: Lichtkurven des Kepler-Weltraumteleskops (long cadence, 30 Minuten) aus dem MAST-Archiv des STScI. Die Suche
(archive.stsci.edu, Kepler data search) liefert alle Sterne auf demselben CCD-Kanal und im selben Quartal wie ein
Zielstern; die Dateien kommen über den Download-Dienst von mast.stsci.edu (je etwa 190 KB für Quartal 1), parallel und mit
Cache. Beides über requests (urllib scheitert lokal am Zertifikat von archive.stsci.edu). Verwendet wird der rohe
Aperturfluss SAP_FLUX; die Pipeline-Kurve PDCSAP_FLUX (schon um gemeinsame Achsen korrigiert) dient zum Vergleich.
"""
import csv
import io
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import requests
import matplotlib.pyplot as plt
from astropy.io import fits

SEARCH = "https://archive.stsci.edu/kepler/data_search/search.php"
DOWNLOAD = ["https://mast.stsci.edu/api/v0.1/Download/file?uri=mast:KEPLER/url/missions/kepler/lightcurves/",
            "https://archive.stsci.edu/missions/kepler/lightcurves/"]


def _search(cache_file, **params):
    """Kepler data search als CSV (Zeilen ohne die zwei Kopfzeilen); Ergebnis im Cache."""
    if cache_file.exists():
        return list(csv.reader(io.StringIO(cache_file.read_text())))
    params = {"action": "Search", "outputformat": "CSV", "ktc_target_type": "LC", "max_records": 5000, **params}
    for i in range(3):
        try:
            txt = requests.get(SEARCH, params=params, timeout=90).text
            if txt.startswith("Kepler ID"):
                rows = list(csv.reader(io.StringIO(txt)))[2:]
                cache_file.write_text("\n".join(",".join(r) for r in rows))
                return rows
        except requests.RequestException:
            pass
        time.sleep(3 * (i + 1))
    raise RuntimeError("Kepler-Suche bei MAST nicht erreichbar")


def channel_stars(kic, quarter, cache, kepmag=(10, 13.5), n=150):
    """Kanal des Zielsterns im Quartal und die n hellsten Sterne mit Kepler-Helligkeit in `kepmag` auf diesem Kanal."""
    cache = Path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    ziel = _search(cache / f"ziel_{kic}_q{quarter}.csv", ktc_kepler_id=kic, sci_data_quarter=quarter,
                   selectedColumnsCsv="ktc_kepler_id,sci_channel,sci_data_set_name")[0]
    channel = int(ziel[1])
    rows = _search(cache / f"kanal{channel}_q{quarter}.csv", sci_channel=channel, sci_data_quarter=quarter,
                   kic_kepmag=f"{kepmag[0]}..{kepmag[1]}", selectedColumnsCsv="ktc_kepler_id,kic_kepmag,sci_data_set_name")
    rows = sorted(rows, key=lambda r: float(r[1]))
    stars = [(int(r[0]), r[2].lower()) for r in rows if int(r[0]) != kic][:n]
    print(f"KIC {kic} liegt in Quartal {quarter} auf CCD-Kanal {channel}; dort {len(rows)} Sterne mit "
          f"Kepler-Helligkeit {kepmag[0]} bis {kepmag[1]}, genommen die {len(stars)} hellsten")
    return (kic, ziel[2].lower()), stars


def _get(args):
    (kic, ds), cache = args
    path = cache / f"{ds}_llc.fits"
    if path.exists():
        return path
    k9 = f"{kic:09d}"
    for url in DOWNLOAD:
        for i in range(2):
            try:
                d = requests.get(f"{url}{k9[:4]}/{k9}/{ds}_llc.fits", timeout=60).content
                if d[:6] == b"SIMPLE":                         # FITS-Datei, keine Fehlerseite
                    path.write_bytes(d)
                    return path
            except requests.RequestException:
                pass
            time.sleep(1 + i)
    return None


def download(stars, cache, workers=8):
    """Lichtkurven parallel laden (Cache). Gibt die Pfade der vorhandenen Dateien zurück."""
    cache = Path(cache)
    t = time.time()
    with ThreadPoolExecutor(workers) as ex:
        paths = list(ex.map(_get, [(s, cache) for s in stars]))
    ok = [p for p in paths if p is not None]
    print(f"{len(ok)} von {len(stars)} Lichtkurven vorhanden ({time.time() - t:.0f} s; Cache {cache.name}/)")
    return ok


def matrix(target_path, paths, min_good=0.8):
    """Relativer Fluss (SAP / Median − 1) aller Sterne auf gemeinsamen guten Zeitpunkten.

    Ein Zeitpunkt zählt, wenn alle Sterne einen Wert haben und mindestens `min_good` der Sterne kein Qualitäts-Flag
    (die Flags unterscheiden sich von Stern zu Stern; ihre Schnittmenge wäre leer).
    """
    def read(p):
        with fits.open(p) as h:
            d = h[1].data
            return np.array(d["TIME"]), np.array(d["SAP_FLUX"]), np.array(d["PDCSAP_FLUX"]), np.array(d["SAP_QUALITY"])
    tgt = read(target_path)
    others = [read(p) for p in paths]
    others = [o for o in others if len(o[0]) == len(tgt[0])]
    alle = others + [tgt]
    good = np.all([np.isfinite(o[0]) & np.isfinite(o[1]) for o in alle], axis=0)
    good &= np.mean([o[3] == 0 for o in alle], axis=0) >= min_good
    X = np.array([o[1][good] / np.median(o[1][good]) - 1 for o in others])
    y = tgt[1][good] / np.median(tgt[1][good]) - 1
    pdc = tgt[2][good] / np.nanmedian(tgt[2][good]) - 1
    streuung = f"{np.median(X.std(axis=1)) * 1e6:,.0f}".replace(",", " ")       # nur die Zahl, nicht den Satz
    print(f"{len(X)} Sterne × {good.sum()} gemeinsame Zeitpunkte (von {len(good)}); "
          f"Streuung je Stern im Median {streuung} ppm")
    return tgt[0][good], X, y, pdc


def axes(X):
    """Hauptachsen der Korrelationsmatrix (jeder Stern auf Mittel 0 und Streuung 1).

    Gibt Eigenwerte (Summe = Zahl der Sterne), Gewichte der Sterne U, Zeitachsen Vt, die Participation Ratio jeder
    Achse (wie viele Sterne sie tragen) und die Marchenko-Pastur-Kante (1 + √γ)² zurück.
    """
    p, T = X.shape
    Z = (X - X.mean(axis=1, keepdims=True)) / X.std(axis=1, keepdims=True)
    U, s, Vt = np.linalg.svd(Z, full_matrices=False)
    ev = s ** 2 / T
    pr = 1 / np.sum(U ** 4, axis=0)
    return ev, U, Vt, pr, (1 + np.sqrt(p / T)) ** 2


def correct(y, Vt, k):
    """Die obersten k Zeitachsen (und eine Konstante) per kleinster Quadrate an y anpassen und abziehen."""
    B = np.vstack([np.ones(len(y)), Vt[:k]]).T
    return y - B @ np.linalg.lstsq(B, y, rcond=None)[0]


def transit(y, t, period, half_width_h=1.0):
    """Tiefe des Transits (Median außerhalb minus Median innerhalb ±half_width_h um die Mitte) und Streuung in 6.5-h-Mitteln.

    Die Mitte ist das Minimum des gefalteten, in 200 Phasen gemittelten Verlaufs. Gibt Tiefe, Streuung (ppm) und den
    Abstand jedes Punktes zur Transitmitte in Stunden zurück.
    """
    ph = (t % period) / period
    idx = np.minimum((ph * 200).astype(int), 199)
    prof = np.array([np.median(y[idx == b]) if np.any(idx == b) else np.nan for b in range(200)])
    c = (np.nanargmin(prof) + 0.5) / 200
    dh = (((ph - c + 0.5) % 1) - 0.5) * period * 24
    depth = np.median(y[(np.abs(dh) > 3) & (np.abs(dh) < 10)]) - np.median(y[np.abs(dh) < half_width_h])
    out = np.abs(dh) > 3
    tb = np.floor(t[out] / (6.5 / 24))
    means = [y[out][tb == b].mean() for b in np.unique(tb) if (tb == b).sum() > 8]
    return depth, np.std(means) * 1e6, dh


def study(t, X, y, pdc, period, ks=(0, 1, 2, 4, 8, 20, 40), name="Kepler-8"):
    """Spektrum der Korrelationsmatrix, oberste Zeitachsen, Korrektur des Zielsterns mit k Achsen, gefalteter Transit."""
    ev, U, Vt, pr, edge = axes(X)
    k_mp = int(np.sum(ev > edge))
    print(f"Korrelationsmatrix {len(X)} × {len(X)}: oberste Eigenwerte " + ", ".join(f"{e:.2f}" for e in ev[:6])
          + f"; Marchenko-Pastur-Kante {edge:.2f}, darüber {k_mp} Achsen")
    print("  getragen von etwa " + ", ".join(f"{p:.0f}" for p in pr[:k_mp]) + " Sternen (Participation Ratio)")
    print(f"{name}: Transit-Tiefe und Streuung (6.5-h-Mittel) nach Abzug von k Achsen")
    for k in sorted(set(ks) | {k_mp}):
        d, s, _ = transit(correct(y, Vt, k), t, period)
        print(f"  k = {k:2d}: Tiefe {d:.3%}, Streuung {s:5.0f} ppm" + ("   ← Marchenko-Pastur" if k == k_mp else ""))
    d, s, _ = transit(pdc, t, period)
    print(f"  Pipeline (PDCSAP): Tiefe {d:.3%}, Streuung {s:5.0f} ppm")
    yk = correct(y, Vt, k_mp)
    fig, ax = plt.subplots(2, 2, figsize=(14, 8.5))
    n = 30
    ax[0, 0].semilogy(np.arange(1, n + 1), ev[:n], "o-", ms=4, color="black")
    ax[0, 0].semilogy(np.arange(1, k_mp + 1), ev[:k_mp], "o", ms=7, color="tab:red", label=f"{k_mp} Achsen über der Kante")
    ax[0, 0].axhline(edge, color="tab:blue", ls="--", label=f"Marchenko-Pastur-Kante {edge:.2f}")
    ax[0, 0].set_xlabel("Rang der Achse")
    ax[0, 0].set_ylabel("Eigenwert (Summe = Zahl der Sterne)")
    ax[0, 0].set_title(f"Spektrum der Korrelationsmatrix von {len(X)} Sternen", fontsize=10)
    ax[0, 0].legend(fontsize=8)
    for i in range(min(k_mp, 4)):
        ax[0, 1].plot(t, Vt[i] * np.sqrt(len(t)) - 4 * i, lw=0.8, label=f"Achse {i + 1} ({pr[i]:.0f} Sterne)")
    ax[0, 1].set_xlabel("Zeit [BKJD = BJD − 2 454 833]")
    ax[0, 1].set_yticks([])
    ax[0, 1].set_title("Die obersten Zeitachsen: gemeinsame Systematik des Kanals", fontsize=10)
    ax[0, 1].legend(fontsize=8, loc="lower left")
    ax[1, 0].plot(t, y * 1e2, ".", ms=1.5, color="grey", label="roh (SAP)")
    ax[1, 0].plot(t, yk * 1e2 - 1.5, ".", ms=1.5, color="tab:red", label=f"ohne {k_mp} Achsen (−1.5 % versetzt)")
    ax[1, 0].plot(t, pdc * 1e2 - 3, ".", ms=1.5, color="tab:blue", label="Pipeline PDCSAP (−3 % versetzt)")
    ax[1, 0].set_xlabel("Zeit [BKJD]")
    ax[1, 0].set_ylabel("relativer Fluss [%]")
    ax[1, 0].set_title(f"{name}: Lichtkurve vor und nach der Korrektur", fontsize=10)
    ax[1, 0].legend(fontsize=8, loc="lower left", markerscale=6)
    for lab, z, c in [("roh", y, "grey"), (f"ohne {k_mp} Achsen", yk, "tab:red"), ("PDCSAP", pdc, "tab:blue")]:
        d, s, dh = transit(z, t, period)
        m = np.abs(dh) < 6
        bins = np.arange(-6, 6.01, 0.5)
        mid = (bins[1:] + bins[:-1]) / 2
        prof = [np.median(z[m][(dh[m] >= a) & (dh[m] < b)]) for a, b in zip(bins[:-1], bins[1:])]
        ax[1, 1].plot(mid, (np.array(prof) - np.median(z[m & (np.abs(dh) > 3)])) * 1e2, "o-", ms=3, color=c,
                      label=f"{lab}: Tiefe {d:.2%}")
    ax[1, 1].set_xlabel(f"Zeit zur Transitmitte [h] (gefaltet mit P = {period} d)")
    ax[1, 1].set_ylabel("relativer Fluss [%]")
    ax[1, 1].set_title("Gefalteter Transit, Mittel in halben Stunden", fontsize=10)
    ax[1, 1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()
    return ev, Vt, k_mp
