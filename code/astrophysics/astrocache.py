"""Gemeinsamer astropy-Cache für astrophysics.ipynb: data/astrophysics/astropy/.

astropy, astroquery und gwpy legen Downloads im astropy-Cache ab. Die Cache-Module der Teile (galdata, nebdata, gwdata,
cosmodata) setzten bis 2026-11-17 je einen eigenen Ordner; in einem Notebook gälte dann nur der zuletzt gesetzte, und die
anderen Teile fänden ihre Downloads nicht. Deshalb importieren sie dieses Modul, das den Cache einmal festlegt. Ihre
übrigen Dateien bleiben in data/galaxies/, data/nebulae/ usw.
"""
from pathlib import Path
from astropy.config import paths

DATA = Path.cwd() / "data" / "astrophysics"
DATA.mkdir(parents=True, exist_ok=True)
paths.set_temp_cache(str(DATA), delete=False).__enter__()     # astropy-Cache jetzt data/astrophysics/astropy/
