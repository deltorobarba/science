"""Überblick für astrophysics.ipynb (bis 2026-11-17 galaxies.ipynb): die hellsten Galaxien und die Messier-Objekte am Himmel, M 51 in Farbbildern des nahen
und mittleren Infrarots und vom Röntgen- bis zum Radiobereich, die SDSS-Spektren in M 51 und ihr BPT-Diagramm.

Nutzt die Module `catalog` (SIMBAD mit Spiegel in Harvard), `surveys` (NASA SkyView), `plotting` (Karte und Bilder) und
`spectra` (SDSS und BPT-Diagramm), die bis 2026-11-14 zu multiwavelength_astronomy.ipynb gehörten und jetzt hier in
code/galaxies/ liegen. Die Funktionen teilen ihre Variablen über Modulvariablen und laufen in dieser Reihenfolge:
sky_map, ir_composites, wide_bands, sdss_spectra, sdss_bpt. Die Galaxie wählt das Notebook (Name als Argument, wie bei
photometry.target).
Downloads und Cache: data/galaxies/images/.
"""
import galdata                                        # zuerst: Cache-Ordner für astropy
import catalog
import plotting
import spectra
import surveys

CACHE = galdata.DATA / "images"
PIXELS = 600                       # Pixel pro Seite der Bilder um die Galaxie
VMAX, MIN_SIZE = 10.5, 3.0         # Galaxien heller als V = 10.5 und größer als 3 Bogenminuten (wie in Schritt 1)
WIDE_BANDS = ["RASS-Cnt Broad", "DSS2 Red", "H-Alpha Comp", "2MASS-K", "WISE 22",
              "IRIS100", "Planck 857 I", "Planck 030 I", "NVSS"]
DV = 600                           # Geschwindigkeitsfenster um die Geschwindigkeit laut SIMBAD [km/s]
SN_MIN = 3                         # alle vier BPT-Linien mit Signal-Rausch-Verhältnis über 3


def _select(name):
    """Die Galaxie aus SIMBAD (Cache) und das Bildfeld: 1.6-mal die Größe, wie in photometry.band_images."""
    global target, fov
    target = catalog.lookup(name, CACHE)
    fov = min(1.6 * target.size, surveys.MAX_FOV)


def sky_map(vmax=VMAX, min_size=MIN_SIZE):
    """2. Die hellsten Galaxien und die Messier-Objekte am Himmel."""
    global bright, messier
    bright = catalog.bright_galaxies(CACHE, vmax, min_size)
    messier = catalog.messier(CACHE)
    catalog.show_messier(messier, kinds=["Galaxie"])
    plotting.sky_map(messier, galaxies=bright)


def ir_composites(name):
    """Farbbilder im nahen und mittleren Infrarot."""
    global images
    _select(name)
    composites = {"nahes Infrarot, durch den Staub":  ["2MASS-K", "2MASS-H", "2MASS-J"],
                  "mittleres Infrarot, warmer Staub": ["WISE 12", "WISE 4.6", "WISE 3.4"]}
    bands = sorted({b for channels in composites.values() for b in channels})
    images = surveys.images(target, bands, fov, PIXELS, CACHE)
    plotting.color_images(target, images, composites, fov)


def wide_bands(name):
    """6. Die Galaxie vom Röntgen- bis zum Radiobereich."""
    global wide, wide_images
    _select(name)
    wide = min(max(60, 3 * target.size), surveys.MAX_FOV)    # mindestens 1°: viele dieser Karten lösen nur Bogenminuten auf
    wide_images = surveys.images(target, WIDE_BANDS, wide, 360, CACHE)
    plotting.band_grid(target, wide_images, wide, lo=1, hi=99.9, soft=0.05)


def sdss_spectra(name):
    """8. Spektren aus SDSS: drei Arten von Licht."""
    global spec_table, specs
    _select(name)
    spec_table, folder = spectra.find(target, CACHE, dv=DV)
    specs = spectra.download(spec_table, folder)
    dss = surveys.images(target, ["DSS2 Red"], fov, PIXELS, CACHE).get("DSS2 Red")
    spectra.plot_spectra(target, spec_table, specs, dss, fov, n_show=5)


def sdss_bpt():
    """Emissionslinien der Spektren aus `sdss_spectra` und das BPT-Diagramm."""
    global lines, fits
    lines, fits = spectra.measure(spec_table, specs, sn_min=SN_MIN)
    spectra.plot_bpt(target, spec_table, specs, lines, fits, CACHE)
