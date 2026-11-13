"""Abfragen für exoplanets.ipynb: NASA Exoplanet Archive (TAP über astroquery), Gaia DR3 (VizieR) und Spektren des
Archivs, jeweils mit Cache auf der Platte und Wiederholungen.

Der Cache liegt in data/exoplanets/archive/ neben dem Notebook. Am 2026-11-12 kam die TAP-Abfrage einmal als
Cloudflare-Seite zurück; deshalb wird bis zu dreimal mit Pause wiederholt, und ein vorhandener Cache wird immer genutzt.
VizieR in Straßburg antwortete am 2026-11-13 mit 404; dann wird der Spiegel in Harvard gefragt.
"""
import hashlib
import re
import time
import warnings
from pathlib import Path

import pandas as pd

CACHE = Path.cwd() / "data" / "exoplanets" / "archive"


def _cached(key, fetch, tries=3, pause=10):
    """Gibt den Cache zu `key` zurück oder ruft `fetch()` auf (mit Wiederholungen) und speichert das Ergebnis als CSV."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{hashlib.sha1(key.encode()).hexdigest()[:16]}.csv"
    if path.is_file():
        return pd.read_csv(path)
    for k in range(tries):
        try:
            df = fetch()
            if df is None or len(df.columns) == 0:
                raise ValueError("leere Antwort")
            df.to_csv(path, index=False)
            return df
        except Exception as err:              # Netz, Cloudflare-Seite, Zeitüberschreitung
            if k == tries - 1:
                raise RuntimeError(f"Abfrage fehlgeschlagen nach {tries} Versuchen ({err}); später erneut versuchen") from err
            time.sleep(pause)


def query(table, where=None, select=None):
    """NASA Exoplanet Archive, Tabelle `table` (z. B. pscomppars), als pandas-Tabelle."""
    from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive

    def fetch():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            kw = {k: v for k, v in (("where", where), ("select", select)) if v}
            return NasaExoplanetArchive.query_criteria(table=table, **kw).to_pandas()
    return _cached(f"nea|{table}|{where}|{select}", fetch)


def gaia_region(ra, dec, radius_arcsec):
    """Gaia DR3 (VizieR I/355/gaiadr3) im Kreis um (ra, dec): Source, RA_ICRS, DE_ICRS, Gmag."""
    from astropy import units as u
    from astropy.coordinates import SkyCoord
    from astroquery.vizier import Vizier

    def fetch():
        last = None
        for server in ("vizier.cds.unistra.fr", "vizier.cfa.harvard.edu"):     # Hauptserver, dann Spiegel
            try:
                v = Vizier(columns=["Source", "RA_ICRS", "DE_ICRS", "Gmag"], row_limit=-1)
                v.VIZIER_SERVER = server
                res = v.query_region(SkyCoord(ra, dec, unit="deg"), radius=radius_arcsec * u.arcsec, catalog="I/355/gaiadr3")
                return res[0].to_pandas()
            except Exception as err:
                last = err
        raise last
    return _cached(f"gaia|{ra:.6f}|{dec:.6f}|{radius_arcsec:.3f}", fetch)


def spectrum(spec_path):
    """Eine Spektrendatei des Archivs (über den Arbeitsbereich der Weboberfläche) als astropy-Tabelle."""
    import requests
    from astropy.io import ascii
    from astropy.table import Table

    def fetch():
        base = "https://exoplanetarchive.ipac.caltech.edu"
        page = requests.get(base + "/cgi-bin/atmospheres/nph-firefly?atmospheres", timeout=60).text
        workspace = re.search(r"/workspace/TMP_[A-Za-z0-9_]+", page).group(0)
        r = requests.get(f"{base}{workspace}/atmospheres/tab1/data/{spec_path}", timeout=60)
        r.raise_for_status()
        return ascii.read(r.text, format="ipac").to_pandas()
    return Table.from_pandas(_cached(f"spec|{spec_path}", fetch))
