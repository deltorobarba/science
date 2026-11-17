"""Vorstufen ohne Ausgabe für astrophysics.ipynb.

Die Funktionen eines Moduls reichen ihre Zwischenergebnisse weiter. Einige Schritte brauchen deshalb Rechnungen aus
Schritten, die das Notebook nicht zeigt (z. B. die Linienfits vor der Dichte). `silent()` führt solche Vorstufen aus und
verwirft dabei Text und Bilder.
"""
import contextlib
import io

import matplotlib.pyplot as plt


@contextlib.contextmanager
def silent():
    """Block ohne Text- und Bildausgabe ausführen: print wird verworfen, jede Abbildung sofort geschlossen."""
    show = plt.show
    plt.show = lambda *args, **kwargs: plt.close("all")
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            yield
    finally:
        plt.show = show
        plt.close("all")
