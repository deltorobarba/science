"""Bilder zeichnen für galaxies.ipynb (über overview.py) und nebulae.ipynb (über messier.py): Helligkeit strecken,
Farbbilder mischen, Tafeln, Himmelskarte. Bis 2026-11-14 Teil von multiwavelength_astronomy.ipynb.

Alle Bilder haben Norden oben und Osten links (wie am Himmel von der Erde aus gesehen); die Achsen zählen
Bogenminuten vom Objekt aus.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from astropy.coordinates import SkyCoord

from surveys import INFO, MEAN_BANDS

KIND_COLORS = {"Galaxie": "tab:blue", "Nebel": "tab:red", "Sternhaufen": "0.6", "sonstiges": "0.6"}


def stretch(img, lo=1.0, hi=99.8, soft=0.1, gamma=1.0):
    """Asinh-Streckung zwischen zwei Perzentilen: schwache Teile sichtbar, helle nicht übersättigt."""
    a, b = np.nanpercentile(img, [lo, hi])
    x = np.clip((img - a) / (b - a), 0, 1)
    y = (np.arcsinh(x / soft) / np.arcsinh(1 / soft)) ** gamma
    return np.nan_to_num(y, nan=1.0)                  # übersättigte Pixel (NaN) als hellster Wert


def rgb(images, channels, **kw):
    """Drei Bilder als Rot, Grün, Blau, jedes für sich gestreckt."""
    return np.dstack([stretch(images[c], **kw) for c in channels])


def extent(fov):
    h = fov / 2
    return [h, -h, -h, h]                            # Osten links, Norden oben


def nice_length(x):
    """Runde Länge (1, 2 oder 5 mal Zehnerpotenz) knapp unter x."""
    p = 10 ** np.floor(np.log10(x))
    return max(m for m in (1, 2, 5) if m * p <= x) * p


def decorate(ax, target, fov, color="white", ellipse=True):
    """Größe laut SIMBAD (gestrichelt) und Maßstab in Lichtjahren (unten rechts)."""
    if ellipse and target.size_from_simbad and target.size < 0.9 * fov:
        ax.add_patch(Ellipse((0, 0), width=target.minor, height=target.size, angle=-target.pa,
                             fill=False, ec=color, ls="--", lw=0.8))
    if np.isfinite(target.dist_pc):
        ly = nice_length(0.3 * fov * target.ly_per_arcmin)
        length = ly / target.ly_per_arcmin            # Bogenminuten
        h = fov / 2
        x1 = -0.9 * h
        ax.plot([x1 + length, x1], [-0.88 * h] * 2, color=color, lw=2.5)
        label = f"{ly:,.0f} Lichtjahre".replace(",", " ")
        ax.text(x1 + length / 2, -0.83 * h, label, color=color, ha="center", va="bottom", fontsize=9)


def _galactic(ra, dec):
    g = SkyCoord(np.asarray(ra), np.asarray(dec), unit="deg").galactic
    return -np.radians(((g.l.deg + 180) % 360) - 180), np.radians(g.b.deg)   # l wächst nach links, wie am Himmel


def sky_map(df, galaxies=None, label_n=15):
    """Himmelskarte in galaktischen Koordinaten (Mollweide), Mitte der Milchstraße in der Mitte.

    Ohne `galaxies`: alle Messier-Objekte. Mit `galaxies` (Tabelle aus catalog.bright_galaxies): diese Galaxien, Punkte
    nach Größe, die `label_n` hellsten mit Namen, dazu Nebel und Sternhaufen aus dem Messier-Katalog `df`.
    """
    lon, lat = _galactic(df["ra"], df["dec"])
    fig = plt.figure(figsize=(12, 6.2))
    ax = fig.add_subplot(111, projection="mollweide")
    kind = df["kind"].values
    groups = [("Messier: Sternhaufen und sonstiges", ~np.isin(kind, ["Galaxie", "Nebel"]), "0.6", 12),
              ("Messier: Galaxien", kind == "Galaxie", KIND_COLORS["Galaxie"], 40),
              ("Messier: Nebel", kind == "Nebel", KIND_COLORS["Nebel"], 40)]
    if galaxies is not None:
        groups = [g for g in groups if "Galaxien" not in g[0]]
        gl, gb = _galactic(galaxies["ra"], galaxies["dec"])
        size = 8 + 25 * np.log10(np.clip(galaxies["galdim_majaxis"].values, 3, None) / 3 + 1) ** 2
        ax.scatter(gl, gb, s=size, c=KIND_COLORS["Galaxie"], alpha=0.8, zorder=2,
                   label=f"Galaxien heller als V = {galaxies['vmag'].max():.1f} ({len(galaxies)})")
        for x, y, name in list(zip(gl, gb, galaxies["name"]))[:label_n]:
            ax.annotate(name, (x, y), xytext=(3, 3), textcoords="offset points", fontsize=7, color="tab:blue")
    for label, m, color, size in groups:
        ax.scatter(lon[m], lat[m], s=size, c=color, alpha=0.9 if size > 12 else 0.6,
                   label=f"{label} ({m.sum()})", zorder=3 if size > 12 else 1)
        if size > 12:                                 # Messier-Nummer neben Galaxien und Nebel
            for x, y, name in zip(lon[m], lat[m], df["name"].values[m]):
                ax.annotate(name[2:], (x, y), xytext=(3, 3), textcoords="offset points", fontsize=7)
    ax.axhline(0, color="0.7", lw=0.8)
    ticks = np.radians(np.arange(-150, 181, 30))
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{(-t) % 360:.0f}°" for t in np.degrees(ticks)], fontsize=8)
    ax.grid(alpha=0.3)
    ax.set_xlabel("galaktische Länge l")
    ax.set_ylabel("galaktische Breite b")
    title = ("Die hellsten Galaxien und die Messier-Objekte am Himmel" if galaxies is not None
             else "Die Messier-Objekte am Himmel")
    ax.set_title(title + " (Linie: Ebene der Milchstraße, Zahlen: Messier-Nummer)", fontsize=11)
    ax.legend(loc="lower right", fontsize=9, bbox_to_anchor=(1.08, -0.08))
    plt.show()


def color_images(target, images, composites, fov, stretches=None):
    """Mehrere Farbbilder nebeneinander; composites = {Titel: [Rot, Grün, Blau]}.

    stretches = {Titel: dict(lo=…, hi=…, soft=…, gamma=…)} ändert die Streckung einzelner Bilder; ohne Angabe
    beginnt die Skala beim 20. Perzentil, damit der verrauschte Himmel dunkel bleibt.
    """
    stretches = stretches or {}
    shown = {t: c for t, c in composites.items() if all(b in images for b in c)}
    for t in composites:
        if t not in shown:
            print(f"{t}: fehlt, weil ein Band keine Abdeckung hat")
    n = len(shown)
    ncol = 2 if n == 4 else min(n, 3)
    nrow = int(np.ceil(n / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(6.6 * ncol, 6.4 * nrow), squeeze=False)
    for ax, (title, chans) in zip(axes.flat, shown.items()):
        ax.imshow(rgb(images, chans, **stretches.get(title, dict(lo=20))), origin="lower", extent=extent(fov))
        decorate(ax, target, fov)
        ax.set_title(f"{title}\nR: {chans[0]}   G: {chans[1]}   B: {chans[2]}", fontsize=10)
        ax.set_xlabel("ΔRA [′] (Osten links)")
        ax.set_ylabel("ΔDec [′]")
    for ax in list(axes.flat)[n:]:
        ax.axis("off")
    fig.suptitle(f"{target.name}: Farbbilder ({fov:.0f}′ × {fov:.0f}′, gestrichelt: Größe laut SIMBAD)", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    plt.show()


def band_grid(target, images, fov, ncol=3, cmap="inferno", **kw):
    """Jedes Band als eigenes Bild, in der Reihenfolge der Wellenlänge, wie sie übergeben wurde."""
    keys = [k for k in images if k not in MEAN_BANDS]
    nrow = int(np.ceil(len(keys) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(4.6 * ncol, 4.7 * nrow), squeeze=False)
    for ax, key in zip(axes.flat, keys):
        ax.imshow(stretch(images[key], **kw), origin="lower", cmap=cmap, extent=extent(fov))
        decorate(ax, target, fov)
        wave, what, res = INFO.get(key, ("", "", ""))
        ax.set_title(f"{key}: {wave}\n{what} (Auflösung {res})" if wave else key, fontsize=9)
        ax.tick_params(labelsize=8)
    for ax in list(axes.flat)[len(keys):]:
        ax.axis("off")
    for ax in axes[-1]:
        ax.set_xlabel("ΔRA [′] (Osten links)")
    for ax in axes[:, 0]:
        ax.set_ylabel("ΔDec [′]")
    fig.suptitle(f"{target.name} in {len(keys)} Bändern ({fov:.0f}′ × {fov:.0f}′)", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    plt.show()
