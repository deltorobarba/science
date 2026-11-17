"""Cache für astrophysics.ipynb (bis 2026-11-17 gravitational_waves.ipynb): Ordner data/gravitational_waves/ neben dem Notebook.

Beim Import legt astrocache den Download-Cache von astropy nach data/astrophysics/astropy/ (bis 2026-11-17
data/gravitational_waves/astropy/); gwpy speichert die
LIGO-Rohdaten mit cache=True dort. Deshalb dieses Modul vor gwpy importieren.
"""
from pathlib import Path
from astropy.config import paths

DATA = Path.cwd() / "data" / "gravitational_waves"
DATA.mkdir(parents=True, exist_ok=True)
import matplotlib
import astrocache                                             # gemeinsamer astropy-Cache data/astrophysics/astropy/ (bis 2026-11-17 data/gravitational_waves/astropy/)

RC_VORHER = dict(matplotlib.rcParams)                        # Plotstil vor gwpy; gw150914 stellt ihn nach dem Import zurück
