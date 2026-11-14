"""Die Messier-Objekte am Himmel für nebulae.ipynb: der Katalog aus SIMBAD, die zwölf Nebel und eine Himmelskarte in
galaktischen Koordinaten.

Nutzt die Module `catalog` (SIMBAD mit Spiegel in Harvard) und `plotting` (das `surveys` importiert) aus
code/galaxies/; das Notebook legt diesen Ordner als zweiten auf sys.path.
Downloads und Cache: data/nebulae/images/.
"""
import nebdata                                        # zuerst: Cache-Ordner für astropy
import catalog
import plotting

CACHE = nebdata.DATA / "images"


def sky():
    """1. Die Nebel des Messier-Katalogs am Himmel."""
    global messier_objects
    messier_objects = catalog.messier(CACHE)
    catalog.show_messier(messier_objects, kinds=["Nebel"])
    plotting.sky_map(messier_objects)
