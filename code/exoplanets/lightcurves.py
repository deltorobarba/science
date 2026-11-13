"""Gemeinsame Werkzeuge für Lichtkurven in exoplanets.ipynb (Transitsuche und Vetting): lightkurve ohne Warnungen laden,
Arrays ohne Maske, Phase seit der nächsten Transitmitte, gleitender Median als Trend.

Die Kepler-Daten kommen über lightkurve aus dem Mikulski Archive for Space Telescopes (MAST); lightkurve speichert sie
in data/exoplanets/lightkurve/ neben dem Notebook.
"""
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

with warnings.catch_warnings():               # lightkurve meldet beim Import ein fehlendes Zusatzpaket (oktopus)
    warnings.simplefilter("ignore")
    import lightkurve as lk                    # noqa: F401  (für die anderen Module)

lk.conf.cache_dir = str(Path.cwd() / "data" / "exoplanets" / "lightkurve")


def unmask(q):
    """Einfaches float-Array aus einer astropy-Größe oder maskierten Spalte."""
    return np.asarray(getattr(q, "unmasked", q).value, dtype=float)


def fold_phase(t, P, t0):
    """Tage seit der nächsten Transitmitte."""
    return (t - t0 + 0.5 * P) % P - 0.5 * P


def running_median(t, f, window_d, use):
    """Trend = gleitender Median über die Punkte in `use` (Fenster in Tagen), auf alle Zeiten interpoliert."""
    s = pd.Series(f[use], index=pd.to_datetime(t[use], unit="D"))
    trend = s.rolling(pd.Timedelta(days=window_d), center=True, min_periods=5).median().to_numpy()
    return np.interp(t, t[use], trend)
