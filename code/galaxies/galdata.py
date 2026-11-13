"""Cache für galaxies.ipynb: Ordner data/galaxies/ neben dem Notebook.

Beim Import wird der Download-Cache von astropy (auch der von astroquery) nach data/galaxies/astropy/ gelegt. Deshalb
dieses Modul vor astropy und astroquery importieren.
"""
from pathlib import Path
from astropy.config import paths

DATA = Path.cwd() / "data" / "galaxies"
DATA.mkdir(parents=True, exist_ok=True)
paths.set_temp_cache(str(DATA), delete=False).__enter__()     # astropy-Cache jetzt data/galaxies/astropy/

# Ausweichwege, wenn die Dienste des CDS in Straßburg nicht antworten (am 2026-11-13 gaben SIMBAD, VizieR und
# hips2fits 404): SIMBAD über den Spiegel in Harvard, Farbbilder (DSS2 color) aus den SkyView-Bildern DSS2 Rot und Blau.
import urllib.request


def _erreichbar(url, timeout=15):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status == 200
    except Exception:
        return False


if not _erreichbar("https://simbad.cds.unistra.fr/simbad/sim-tap/capabilities"):
    from astroquery.simbad import Simbad, conf as _simbad_conf
    _simbad_conf.server = "simbad.harvard.edu"
    Simbad.server = "simbad.harvard.edu"
    print("SIMBAD in Straßburg nicht erreichbar: Spiegel simbad.harvard.edu")


def _dss2_color(width, height, ra, dec, fov, **kw):
    """Farbbild wie hips2fits mit CDS/P/DSS2/color (jpg, Norden oben, Osten links) aus SkyView DSS2 Rot und Blau."""
    import numpy as np
    from astropy.coordinates import SkyCoord
    from astroquery.skyview import SkyView
    pos = SkyCoord(ra, dec)
    red, blue = (SkyView.get_images(position=pos, survey=s, pixels=f"{width},{height}", width=fov,
                                    height=fov * height / width)[0][0].data for s in ("DSS2 Red", "DSS2 Blue"))

    def scale(x):
        lo, hi = np.nanpercentile(x, [1, 99.7])
        return np.clip((x - lo) / (hi - lo), 0, 1)
    r, b = scale(red), scale(blue)
    return (255 * np.dstack([r, (r + b) / 2, b])[::-1]).astype(np.uint8)    # FITS: erste Zeile Süden, JPEG: Norden


def _hips2fits_mit_ersatz():
    from astroquery.hips2fits import hips2fits
    original = hips2fits.query

    def query(*args, **kw):
        try:
            return original(*args, **kw)
        except Exception:
            if kw.get("format") != "jpg" or "DSS2/color" not in str(kw.get("hips", "")):
                raise
            print("hips2fits (CDS) nicht erreichbar: Farbbild aus SkyView DSS2 Rot und Blau")
            return _dss2_color(**kw)
    hips2fits.query = query


_hips2fits_mit_ersatz()
