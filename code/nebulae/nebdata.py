"""Gemeinsamer Datenordner für nebulae.ipynb: data/nebulae/ neben dem Notebook.

Die Module laden ihre Bilder und Kataloge selbst nach data/nebulae/<thema>/. Downloads über astropy und astroquery (SDSS)
landen im Cache data/nebulae/astropy/; dafür setzt dieses Modul beim Import einen eigenen Cache-Ordner für astropy.
Die alten Notebooks setzten dafür XDG_CACHE_HOME; das ignoriert astropy mit einer Warnung, wenn ~/.astropy/cache schon
existiert.
"""
from pathlib import Path

from astropy.config import paths

DATA = Path.cwd() / "data" / "nebulae"
DATA.mkdir(parents=True, exist_ok=True)
paths.set_temp_cache(str(DATA), delete=False).__enter__()     # astropy-Cache jetzt data/nebulae/astropy/
