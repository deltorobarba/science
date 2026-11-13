"""Cache für cosmology.ipynb: Ordner data/cosmology/ neben dem Notebook.

Beim Import wird der Download-Cache von astropy (auch der von astroquery) nach data/cosmology/astropy/ gelegt. Deshalb
dieses Modul vor astropy und astroquery importieren.
"""
from pathlib import Path
from astropy.config import paths

DATA = Path.cwd() / "data" / "cosmology"
DATA.mkdir(parents=True, exist_ok=True)
paths.set_temp_cache(str(DATA), delete=False).__enter__()     # astropy-Cache jetzt data/cosmology/astropy/
