"""Bilder aus NASA SkyView für galaxies.ipynb (über overview.py): Bänder, Download mit Cache und Wiederholungen.
Bis 2026-11-14 Teil von multiwavelength_astronomy.ipynb.

SkyView schneidet aus über 100 Himmelsdurchmusterungen ein Bild um eine Position aus und rechnet es auf ein
gemeinsames Pixelgitter (Norden oben, Osten links). Jedes Bild wird als FITS in `cache_dir/<Objekt>/` gespeichert.
"""
import time
import urllib.parse
import urllib.request
import warnings
from pathlib import Path

import numpy as np
from astropy.io import fits

SKYVIEW = "https://skyview.gsfc.nasa.gov/current/cgi/runquery.pl?"
MAX_FOV = 180.0     # Bogenminuten; bei 198′ lieferte SkyView am 2026-11-12 für WISE 22 µm nur ein leeres Bild

# SkyView-Name: (Wellenlänge, was man vor allem sieht, Auflösung)
INFO = {
    "RASS-Cnt Broad": ("Röntgen 0.1–2.4 keV", "heißes Gas, aktive Kerne", "≈ 2′"),
    "GALEX Near UV":  ("UV 0.23 µm", "junge, massereiche Sterne", "5″"),
    "DSS2 Blue":      ("optisch 0.47 µm", "blaue Sterne, gestreutes Licht", "≈ 2″"),
    "DSS2 Red":       ("optisch 0.65 µm", "Sternlicht und Hα", "≈ 2″"),
    "DSS2 IR":        ("optisch 0.85 µm", "kühle Sterne", "≈ 2″"),
    "H-Alpha Comp":   ("Hα 656 nm", "ionisierter Wasserstoff", "6′"),
    "2MASS-J":        ("nahes IR 1.2 µm", "Sterne, wenig Staub", "2″"),
    "2MASS-H":        ("nahes IR 1.6 µm", "Sterne", "2″"),
    "2MASS-K":        ("nahes IR 2.2 µm", "alte Sterne, durch Staub hindurch", "2″"),
    "WISE 3.4":       ("IR 3.4 µm", "Sternmasse", "6″"),
    "WISE 4.6":       ("IR 4.6 µm", "Sterne und heißer Staub", "6″"),
    "WISE 12":        ("IR 12 µm", "warmer Staub, PAH, Sternentstehung", "6.5″"),
    "WISE 22":        ("IR 22 µm", "warmer Staub um junge Sterne", "12″"),
    "IRIS100":        ("IR 100 µm", "kühler Staub (≈ 20–30 K)", "4′"),
    "Planck 857 I":   ("submm 350 µm", "kalter Staub", "5′"),
    "Planck 030 I":   ("Mikrowellen 1 cm", "Frei-frei- und Synchrotronstrahlung", "32′"),
    "NVSS":           ("Radio 21 cm", "Synchrotron, ionisiertes Gas", "45″"),
}
MEAN_BANDS = {"DSS2 Mitte": ("DSS2 Red", "DSS2 Blue")}   # künstlicher Grünkanal für optische Farbbilder


def fetch(url, path, check, tries=5, pause=10, timeout=300):
    """Datei laden und speichern; SkyView lehnt schnelle Folgeanfragen ab, deshalb Pausen und Wiederholungen."""
    path = Path(path)
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                data = r.read()
            if check(data):
                path.write_bytes(data)
                return path
        except OSError:
            pass
        time.sleep(pause)
    raise OSError(f"{path.name}: kein gültiger Download nach {tries} Versuchen")


def skyview(survey, ra, dec, fov_arcmin, npix, folder):
    """Ein Bild als Array (Zeile 0 = Süden, Spalte 0 = Osten), None ohne Abdeckung."""
    size = fov_arcmin / 60
    q = urllib.parse.urlencode({"Position": f"{ra:.5f},{dec:.5f}", "Survey": survey, "Pixels": npix,
                                "Size": f"{size:.5f}", "Return": "FITS"})
    name = "".join(c if c.isalnum() else "_" for c in survey) + f"_{fov_arcmin:.1f}_{npix}.fits"
    path = fetch(SKYVIEW + q, Path(folder) / name, lambda d: d.startswith(b"SIMPLE"))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")              # SkyView schreibt BLANK auch in Gleitkomma-Bilder
        with fits.open(path) as h:
            data = h[0].data.astype(float)
    good = np.isfinite(data)
    if good.mean() < 0.05 or np.nanmax(data) == np.nanmin(data):
        return None
    return data


def images(target, bands, fov_arcmin, npix, cache_dir):
    """Bilder eines Objekts in mehreren Bändern als dict; Bänder ohne Abdeckung fehlen."""
    folder = Path(cache_dir) / "".join(c if c.isalnum() else "_" for c in target.name.strip())
    out, missing = {}, []
    for band in bands:
        if band in MEAN_BANDS:
            continue
        img = skyview(band, target.ra, target.dec, fov_arcmin, npix, folder)
        if img is None:
            missing.append(band)
        else:
            out[band] = img
    for band, (a, b) in MEAN_BANDS.items():
        if band in bands and a in out and b in out:
            out[band] = (out[a] + out[b]) / 2
    print(f"{len(out)} Bilder, {fov_arcmin:.1f}′ mit {npix} Pixeln"
          + (f"; keine Daten (keine Abdeckung oder Feld zu groß): {', '.join(missing)}" if missing else ""))
    return out
