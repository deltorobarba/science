"""Gemeinsame Daten für sun.ipynb: der Ordner data/sun/ neben dem Notebook, die Sonnenfleckenzahl von SILSO und die
Einstellung von sunpy.

SILSO (Royal Observatory of Belgium) liefert Monatsmittel und die offizielle 13-Monats-Glättung als CSV; beide werden
in data/sun/silso/ gespeichert und nur mit refresh=True neu geladen. sunpy speichert Downloads (SDO, GOES) unter
data/sun/sunpy/data/; dafür setzt dieses Modul beim Import SUNPY_CONFIGDIR, bevor sunpy selbst importiert wird.
"""
import os
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path.cwd() / "data" / "sun"
SUNPY_DIR = DATA / "sunpy"
SUNPY_DIR.mkdir(parents=True, exist_ok=True)
(SUNPY_DIR / "sunpyrc").write_text(f"[general]\nworking_dir = {SUNPY_DIR}\n")
os.environ["SUNPY_CONFIGDIR"] = str(SUNPY_DIR)


def silso(name, refresh=False):
    """Eine SILSO-Reihe lesen (snmtotcsv: Monatsmittel, snmstotcsv: geglättet); fehlende Werte (-1) werden zu NaN."""
    path = DATA / "silso" / f"{name}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    if refresh or not path.exists():
        urllib.request.urlretrieve(f"https://www.sidc.be/SILSO/INFO/{name}.php", path)
    df = pd.read_csv(path, sep=";", names=["jahr", "monat", "t", "sn", "sd", "n_beob", "definitiv"])
    df.loc[df.sn < 0, "sn"] = np.nan
    return df
