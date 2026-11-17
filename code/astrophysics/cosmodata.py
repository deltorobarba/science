"""Cache für astrophysics.ipynb (bis 2026-11-17 cosmology.ipynb): Ordner data/cosmology/ neben dem Notebook.

Beim Import wird der Download-Cache von astropy (auch der von astroquery) nach data/astrophysics/astropy/ (über astrocache, bis 2026-11-17 data/cosmology/astropy/) gelegt. Deshalb
dieses Modul vor astropy und astroquery importieren.
"""
from pathlib import Path
from astropy.config import paths

DATA = Path.cwd() / "data" / "cosmology"
DATA.mkdir(parents=True, exist_ok=True)
import astrocache                                             # gemeinsamer astropy-Cache data/astrophysics/astropy/ (bis 2026-11-17 data/cosmology/astropy/)
