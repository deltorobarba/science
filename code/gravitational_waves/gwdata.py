"""Cache für gravitational_waves.ipynb: Ordner data/gravitational_waves/ neben dem Notebook.

Beim Import wird der Download-Cache von astropy dorthin gelegt (data/gravitational_waves/astropy/); gwpy speichert die
LIGO-Rohdaten mit cache=True dort. Deshalb dieses Modul vor gwpy importieren.
"""
from pathlib import Path
from astropy.config import paths

DATA = Path.cwd() / "data" / "gravitational_waves"
DATA.mkdir(parents=True, exist_ok=True)
paths.set_temp_cache(str(DATA), delete=False).__enter__()     # astropy-Cache jetzt data/gravitational_waves/astropy/
