"""Gemeinsamer Datenordner für astrophysics.ipynb (bis 2026-11-17 nebulae.ipynb): data/nebulae/ neben dem Notebook.

Die Module laden ihre Bilder und Kataloge selbst nach data/nebulae/<thema>/. Downloads über astropy und astroquery (SDSS)
landen im Cache data/astrophysics/astropy/ (über astrocache, bis 2026-11-17 data/nebulae/astropy/); den Ordner legt astrocache beim Import fest.
Die alten Notebooks setzten dafür XDG_CACHE_HOME; das ignoriert astropy mit einer Warnung, wenn ~/.astropy/cache schon
existiert.
"""
from pathlib import Path

from astropy.config import paths

DATA = Path.cwd() / "data" / "nebulae"
DATA.mkdir(parents=True, exist_ok=True)
import astrocache                                             # gemeinsamer astropy-Cache data/astrophysics/astropy/ (bis 2026-11-17 data/nebulae/astropy/)
