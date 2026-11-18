"""Die Messier-Objekte am Himmel für astrophysics.ipynb (bis 2026-11-17 nebulae.ipynb): der Katalog aus SIMBAD, die zwölf Nebel und eine Himmelskarte in
galaktischen Koordinaten; dann ein Nebel nach Wahl (`target`, Standard M 42) vom Röntgen- bis zum Radiobereich und in
Farbbildern (seit 2026-11-18, ersetzt die Bilder aus orion.py).

Nutzt die Module `catalog` (SIMBAD mit Spiegel in Harvard) und `plotting` (das `surveys` importiert) aus
code/galaxies/; das Notebook legt diesen Ordner als zweiten auf sys.path.
Downloads und Cache: data/nebulae/images/.
"""
import nebdata                                        # zuerst: Cache-Ordner für astropy
import catalog
import plotting
import surveys

CACHE = nebdata.DATA / "images"
PIXELS = 800                       # Pixel pro Seite der Farbbilder
COLOR_MAX_FOV = 60.0               # Farbbilder höchstens 1°: 2MASS und WISE lösen 2″ bis 12″ auf (wie früher orion.py)
WIDE_BANDS = ["RASS-Cnt Broad", "DSS2 Red", "H-Alpha Comp", "2MASS-K", "WISE 22",
              "IRIS100", "Planck 857 I", "Planck 030 I", "NVSS"]           # wie bei den Galaxien (overview.py)
COMPOSITES = {"optisch, wie mit dem Auge": ["DSS2 Red", "DSS2 Mitte", "DSS2 Blue"],
              "nahes Infrarot, durch den Staub": ["2MASS-K", "2MASS-H", "2MASS-J"],
              "mittleres Infrarot, warmer Staub": ["WISE 12", "WISE 4.6", "WISE 3.4"]}
STRETCHES = {"optisch, wie mit dem Auge": dict(lo=5, hi=99.99, soft=1.0, gamma=1.6),   # helle Nebel: sonst ist der Kern weiß
             "nahes Infrarot, durch den Staub": dict(lo=2, hi=99.8, soft=0.08),       # (Werte aus dem früheren orion.py)
             "mittleres Infrarot, warmer Staub": dict(lo=2, hi=99.8, soft=0.08)}


def sky():
    """12. Die Nebel des Messier-Katalogs am Himmel."""
    global messier_objects
    messier_objects = catalog.messier(CACHE)
    catalog.show_messier(messier_objects, kinds=["Nebel"])
    plotting.sky_map(messier_objects)


def target(name="M 42"):
    """13. Einen Nebel wählen: Steckbrief aus SIMBAD und das Bildfeld der Farbbilder (1.6-mal die Größe, höchstens 1°).
    name: jeder Name, den SIMBAD kennt, z. B. "M 1", "M 57", "Helix Nebula"."""
    global nebula, fov
    nebula = catalog.lookup(name, CACHE)
    fov = min(1.6 * nebula.size, COLOR_MAX_FOV)
    catalog.describe(nebula, fov, PIXELS)


def wide_bands():
    """14. Der Nebel vom Röntgen- bis zum Radiobereich: neun Durchmusterungen, Feld dreimal so groß wie der Nebel."""
    global wide, wide_images
    wide = min(max(60, 3 * nebula.size), surveys.MAX_FOV)    # mindestens 1°: viele dieser Karten lösen nur Bogenminuten auf
    wide_images = surveys.images(nebula, WIDE_BANDS, wide, 360, CACHE)
    plotting.band_grid(nebula, wide_images, wide, lo=1, hi=99.9, soft=0.05)


def color_images():
    """Farbbilder in drei Wellenlängenbereichen: optisch (DSS2), nahes Infrarot (2MASS), mittleres Infrarot (WISE)."""
    global images
    bands = sorted({b for channels in COMPOSITES.values() for b in channels})
    images = surveys.images(nebula, bands, fov, PIXELS, CACHE)
    plotting.color_images(nebula, images, COMPOSITES, fov, STRETCHES)
