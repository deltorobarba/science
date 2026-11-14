"""Überblick für galaxies.ipynb: die hellsten Galaxien und die Messier-Objekte am Himmel, M 51 in Farbbildern des nahen
und mittleren Infrarots und vom Röntgen- bis zum Radiobereich, die SDSS-Spektren in M 51 und ihr BPT-Diagramm.

Nutzt die Module von multiwavelength_astronomy.ipynb aus code/multiwavelength_astronomy/ (`catalog` für SIMBAD mit
Spiegel in Harvard, `surveys` für NASA SkyView, `plotting` für Karte und Bilder, `spectra` für SDSS und das BPT-Diagramm);
das Notebook legt diesen Ordner als zweiten auf sys.path. Die Funktionen teilen ihre Variablen über Modulvariablen und
laufen in dieser Reihenfolge: sky_map, ir_composites, wide_bands, m51_spectra, m51_bpt.
Downloads und Cache: data/galaxies/images/.
"""
import galdata                                        # zuerst: Cache-Ordner für astropy
import catalog
import plotting
import spectra
import surveys

CACHE = galdata.DATA / "images"
TARGET = "M 51"                    # wie photometry.SELECTED_GALAXY
PIXELS = 600                       # Pixel pro Seite der Bilder um M 51
VMAX, MIN_SIZE = 10.5, 3.0         # Galaxien heller als V = 10.5 und größer als 3 Bogenminuten (wie in Schritt 1)
WIDE_BANDS = ["RASS-Cnt Broad", "DSS2 Red", "H-Alpha Comp", "2MASS-K", "WISE 22",
              "IRIS100", "Planck 857 I", "Planck 030 I", "NVSS"]
DV = 600                           # Geschwindigkeitsfenster um die Geschwindigkeit laut SIMBAD [km/s]
SN_MIN = 3                         # alle vier BPT-Linien mit Signal-Rausch-Verhältnis über 3


def sky_map():
    """2. Die hellsten Galaxien und die Messier-Objekte am Himmel."""
    global bright, messier
    bright = catalog.bright_galaxies(CACHE, VMAX, MIN_SIZE)
    messier = catalog.messier(CACHE)
    catalog.show_messier(messier, kinds=["Galaxie"])
    plotting.sky_map(messier, galaxies=bright)


def ir_composites():
    """6. Farbbilder im nahen und mittleren Infrarot."""
    global target, fov, images
    target = catalog.lookup(TARGET, CACHE)
    fov = min(1.6 * target.size, surveys.MAX_FOV)            # wie die Bilder in Schritt 4: 1.6-mal die Größe
    composites = {"nahes Infrarot, durch den Staub":  ["2MASS-K", "2MASS-H", "2MASS-J"],
                  "mittleres Infrarot, warmer Staub": ["WISE 12", "WISE 4.6", "WISE 3.4"]}
    bands = sorted({b for channels in composites.values() for b in channels})
    images = surveys.images(target, bands, fov, PIXELS, CACHE)
    plotting.color_images(target, images, composites, fov)


def wide_bands():
    """7. M 51 vom Röntgen- bis zum Radiobereich."""
    global wide, wide_images
    wide = min(max(60, 3 * target.size), surveys.MAX_FOV)    # mindestens 1°: viele dieser Karten lösen nur Bogenminuten auf
    wide_images = surveys.images(target, WIDE_BANDS, wide, 360, CACHE)
    plotting.band_grid(target, wide_images, wide, lo=1, hi=99.9, soft=0.05)


def m51_spectra():
    """13. Spektren aus SDSS in M 51: drei Arten von Licht."""
    global spec_table, specs
    spec_table, folder = spectra.find(target, CACHE, dv=DV)
    specs = spectra.download(spec_table, folder)
    dss = surveys.images(target, ["DSS2 Red"], fov, PIXELS, CACHE).get("DSS2 Red")
    spectra.plot_spectra(target, spec_table, specs, dss, fov, n_show=5)


def m51_bpt():
    """14. Emissionslinien in M 51 und das BPT-Diagramm."""
    global lines, fits
    lines, fits = spectra.measure(spec_table, specs, sn_min=SN_MIN)
    spectra.plot_bpt(target, spec_table, specs, lines, fits, CACHE)
