"""Ein X-Flare im Bild von SDO für sun.ipynb: die ganze Sonne in fünf Kanälen, Position des Flares, die aktive Region,
magnetischer Fluss und Polaritätsumkehrlinie, die Flare-Bänder und der Vergleich mit dem Heliophysics Event Knowledgebase
(HEK).

Daten: SDO/AIA (131, 171, 304, 1600 Å) und SDO/HMI (Magnetfeld entlang der Sichtlinie) über sunpy (Fido), Cache in
data/sun/sunpy/data/; HEK über sunpy, mit einer früheren Abfrage als Ersatz, wenn der Dienst nicht antwortet. Alle
Schritte teilen sich ein Zustandsobjekt, das `load` anlegt.
"""
import socket
from types import SimpleNamespace

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter, binary_dilation, label, distance_transform_edt
import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time
from astropy.visualization import ImageNormalize, AsinhStretch, LogStretch

import sundata                                         # vor sunpy: Downloads nach data/sun/sunpy
import sunpy.map
from sunpy.coordinates import frames
from sunpy.net import Fido, attrs as a, hek

CHANNELS = {
    131:  "AIA 131 Å: heißes Flare-Plasma, ~10 MK",
    171:  "AIA 171 Å: ruhige Korona, 0.6 MK",
    304:  "AIA 304 Å: Chromosphäre, ~50 000 K",
    1600: "AIA 1600 Å: Flare-Bänder, untere Chromosphäre",
    "HMI": "HMI: Magnetfeld entlang der Sichtlinie",
}


def to_stonyhurst(Tx, Ty, rsun, B0):
    """Bildkoordinaten → heliographische Breite und Länge: parallele Projektion und Drehung um B0."""
    x, y = (Tx / rsun).decompose().value, (Ty / rsun).decompose().value
    z = np.sqrt(1 - x ** 2 - y ** 2)
    lat = np.arcsin(y * np.cos(B0) + z * np.sin(B0))
    lon = np.arctan2(x, z * np.cos(B0) - y * np.sin(B0))
    return np.degrees(lat), np.degrees(lon), z


def label_ns(lat, lon):
    return f"{'N' if lat >= 0 else 'S'}{abs(lat):02.0f}{'W' if lon >= 0 else 'E'}{abs(lon):02.0f}"


def cached_files(PEAK):
    """Die fünf Dateien zur Zeit PEAK aus dem Cache, wenn alle schon da sind (sonst None)."""
    d = sundata.SUNPY_DIR / "data"
    found = [sorted(d.glob(f"aia.lev1.{wl}A_{PEAK.datetime:%Y_%m_%dT%H_%M}*.fits")) for wl in (131, 171, 304, 1600)]
    found.append(sorted(d.glob(f"hmi.m_45s.{PEAK.datetime:%Y.%m.%d_%H}_*.magnetogram.fits")))
    return [f[0] for f in found] if all(found) else None


def load(peak="2024-10-03T12:18:00", box_arcsec=200):
    """Je ein Bild der vier AIA-Kanäle und ein HMI-Magnetogramm zum Maximum des Flares (aus dem Cache oder über Fido)."""
    PEAK = Time(peak)
    files = cached_files(PEAK)
    if files is None:                                   # Suche bei VSO und JSOC dauert oft über eine Minute
        window = a.Time(PEAK, PEAK + 45 * u.s)
        wl = a.Wavelength(131 * u.AA) | a.Wavelength(171 * u.AA) | a.Wavelength(304 * u.AA) | a.Wavelength(1600 * u.AA)
        search = Fido.search(window, (a.Instrument.aia & wl) | (a.Instrument.hmi & a.Physobs.los_magnetic_field))
        files = Fido.fetch(*[block[:1] for block in search], progress=False)

    maps = {}
    for f in files:
        m = sunpy.map.Map(f)
        if m.detector == "HMI":
            maps["HMI"] = m.rotate(order=1)                 # HMI ist um 180° gedreht gespeichert
        else:
            maps[int(m.wavelength.to_value(u.AA))] = m
    maps = {k: maps[k] for k in CHANNELS if k in maps}
    print(f"{'Kanal':<6}{'Zeit (UT)':<22}{'Belichtung':>12}{'Pixel':>9}{'Maximum':>10}{'gesättigt':>11}")
    for k, m in maps.items():
        expo = f"{m.exposure_time.to_value(u.s):.4f} s" if k != "HMI" else "45 s"
        sat = f"{np.sum(m.data >= 16000)}" if k != "HMI" else "-"
        print(f"{str(k):<6}{m.date.isot[:19]:<22}{expo:>12}{m.scale[0].to_value(u.arcsec / u.pix):>8.3f}″{np.nanmax(m.data):>10.0f}{sat:>11}")
    m0 = maps[131]
    print(f"\nAbstand SDO-Sonne {m0.dsun.to(u.AU):.4f}, Sonnenradius {m0.rsun_obs:.1f}, B0 = {m0.observer_coordinate.lat.to(u.deg):.2f}")
    return SimpleNamespace(PEAK=PEAK, BOX=box_arcsec * u.arcsec, maps=maps)


def overview(s):
    """Die ganze Sonne in allen Kanälen (4 × 4 Pixel gemittelt)."""
    maps, PEAK = s.maps, s.PEAK
    fig = plt.figure(figsize=(16, 10))
    for i, (k, m) in enumerate(maps.items()):
        small = m.superpixel([4, 4] * u.pix, func=np.mean)          # 4 × 4 Pixel mitteln: weniger Rauschen, kleineres Bild
        ax = fig.add_subplot(2, 3, i + 1, projection=small)
        if k == "HMI":
            small.plot(axes=ax, cmap="gray", norm=plt.Normalize(-1000, 1000))
        else:
            small = small / m.exposure_time                          # DN/s
            small.plot(axes=ax, norm=ImageNormalize(vmin=0, vmax=np.nanpercentile(small.data, 99.99),
                                                    stretch=LogStretch(1000)))
        ax.set_title(CHANNELS[k], fontsize=9)
        ax.coords[0].set_axislabel(" ")
        ax.coords[1].set_axislabel(" ")
    fig.suptitle(f"SDO am {PEAK.iso[:16]} UT", y=0.98)
    fig.tight_layout()
    plt.show()


def locate(s, smooth=4):
    """Hellster Punkt in AIA 131 Å (geglättet) und seine heliographische Position, eigene Formel gegen sunpy."""
    m131 = s.maps[131]
    img = gaussian_filter(np.nan_to_num(m131.data), smooth)
    iy, ix = np.unravel_index(np.argmax(img), img.shape)
    own = m131.pixel_to_world(ix * u.pix, iy * u.pix)
    B0 = m131.observer_coordinate.lat.to_value(u.rad)
    lat_own, lon_own, mu_own = to_stonyhurst(own.Tx, own.Ty, m131.rsun_obs, B0)
    hgs = own.transform_to(frames.HeliographicStonyhurst(obstime=m131.date))
    km_per_arcsec = (m131.dsun * np.pi / 648000).to_value(u.km)
    print(f"Hellster Punkt in AIA 131 Å: Tx = {own.Tx.to_value(u.arcsec):.1f}″, Ty = {own.Ty.to_value(u.arcsec):.1f}″")
    print(f"Eigene Formel:  Breite {lat_own:+.2f}°, Länge {lon_own:+.2f}°  → {label_ns(lat_own, lon_own)},  μ = {mu_own:.3f}")
    print(f"sunpy:          Breite {hgs.lat.to_value(u.deg):+.2f}°, Länge {hgs.lon.to_value(u.deg):+.2f}°")
    print(f"1″ = {km_per_arcsec:.1f} km auf der Sonne")
    s.__dict__.update(m131=m131, own=own, B0=B0, km_per_arcsec=km_per_arcsec)


def region(s):
    """Ausschnitt um die aktive Region in allen Kanälen, mit HMI-Konturen."""
    maps, own, BOX = s.maps, s.own, s.BOX
    bl = SkyCoord(own.Tx - BOX / 2, own.Ty - BOX / 2, frame=own.frame)
    tr = SkyCoord(own.Tx + BOX / 2, own.Ty + BOX / 2, frame=own.frame)
    subs = {k: m.submap(bl, top_right=tr) for k, m in maps.items()}
    hmi = subs["HMI"]
    hmi_s = sunpy.map.Map(gaussian_filter(np.nan_to_num(hmi.data), 2), hmi.meta)    # leicht geglättet für Konturen

    fig = plt.figure(figsize=(16, 10))
    for i, (k, sub) in enumerate(subs.items()):
        ax = fig.add_subplot(2, 3, i + 1, projection=sub)
        if k == "HMI":
            sub.plot(axes=ax, cmap="gray", norm=plt.Normalize(-1500, 1500))
        else:
            sub.plot(axes=ax, norm=ImageNormalize(sub.data, vmin=np.nanpercentile(sub.data, 1),
                                                  vmax=np.nanmax(sub.data), stretch=AsinhStretch(0.05)))
            hmi_s.draw_contours([-500, 500] * u.G, axes=ax, colors=["tab:blue", "tab:red"], linewidths=0.7)
        ax.plot_coord(own, "+", color="lime", ms=14, mew=2)
        ax.set_title(CHANNELS[k], fontsize=9)
        ax.coords[0].set_axislabel(" ")
        ax.coords[1].set_axislabel(" ")
    fig.suptitle(f"Ausschnitt {BOX.value:.0f}″ × {BOX.value:.0f}″ (grünes +: hellster Punkt in 131 Å; Konturen: HMI ±500 G, rot positiv, blau negativ)", y=0.98)
    fig.tight_layout()
    plt.show()
    for k in (171, 1600):
        print(f"AIA {k}: {np.sum(subs[k].data >= 16000)} gesättigte Pixel im Ausschnitt")
    s.subs, s.hmi = subs, hmi


def magnetic(s, b_t=150, k_dil=3):
    """Magnetischer Fluss der Region (μ-korrigiert) und die Polaritätsumkehrlinie bei ±b_t Gauß."""
    hmi, own, km_per_arcsec = s.hmi, s.own, s.km_per_arcsec
    B = np.nan_to_num(hmi.data)
    ny, nx = B.shape
    xx_h, yy_h = np.meshgrid(np.arange(nx), np.arange(ny))
    c = hmi.pixel_to_world(xx_h * u.pix, yy_h * u.pix)
    rsun = hmi.rsun_obs.to_value(u.arcsec)
    mu = np.sqrt(np.clip(1 - (c.Tx.to_value(u.arcsec) ** 2 + c.Ty.to_value(u.arcsec) ** 2) / rsun ** 2, 0, 1))
    pix_mm = hmi.scale[0].to_value(u.arcsec / u.pix) * km_per_arcsec / 1e3          # Pixelgröße in Mm
    A_p = (pix_mm * 1e8) ** 2                                                       # projizierte Pixelfläche [cm²]
    noise = np.std(B[np.abs(B) < 50])
    print(f"μ im Ausschnitt {mu.min():.3f} bis {mu.max():.3f};  HMI-Pixel {pix_mm * 1e3:.0f} km;  Rauschen ≈ {noise:.0f} G")

    # Region: zusammenhängendes Gebiet, in dem das geglättete |B| über 100 G liegt
    region_lab, _ = label(gaussian_filter(np.abs(B), 8) > 100)
    sizes = np.bincount(region_lab.ravel())
    sizes[0] = 0
    region = region_lab == sizes.argmax()
    flux = B / mu ** 2 * A_p
    phi_p, phi_n = flux[region & (B > 0)].sum(), flux[region & (B < 0)].sum()
    print(f"Region: {region.sum() * pix_mm ** 2:,.0f} Mm²;  Φ+ = {phi_p:.2e} Mx,  Φ− = {phi_n:.2e} Mx,  "
          f"|Φ| = {phi_p - phi_n:.2e} Mx,  Ungleichgewicht (Φ+ + Φ−)/|Φ| = {(phi_p + phi_n) / (phi_p - phi_n):+.2f}")
    print(f"Ohne μ-Korrektur wäre |Φ| = {np.abs(B[region]).sum() * A_p:.2e} Mx")

    Bs = gaussian_filter(B, 2)
    for bt in (b_t, 300, 500):
        pil_t = binary_dilation(Bs > bt, iterations=k_dil) & binary_dilation(Bs < -bt, iterations=k_dil)
        print(f"Umkehrlinie bei ±{bt} G: {pil_t.sum()} Pixel, Länge ≈ {pil_t.sum() / (2 * k_dil + 1) * pix_mm:.0f} Mm")
    pil = binary_dilation(Bs > b_t, iterations=k_dil) & binary_dilation(Bs < -b_t, iterations=k_dil)
    dist_pil = distance_transform_edt(~pil) * pix_mm                                 # Abstand zur Umkehrlinie [Mm]
    near = region & (dist_pil < 10)
    print(f"Anteil des Flusses der Region innerhalb von 10 Mm um die Umkehrlinie: {np.abs(flux[near]).sum() / np.abs(flux[region]).sum():.0%}")
    p_own = hmi.world_to_pixel(own)
    j, i = int(round(p_own.y.value)), int(round(p_own.x.value))
    print(f"Hellster Punkt in 131 Å: B = {Bs[j, i]:+.0f} G, {dist_pil[j, i]:.1f} Mm von der Umkehrlinie")

    fig = plt.figure(figsize=(8, 7))
    ax = fig.add_subplot(projection=hmi)
    hmi.plot(axes=ax, cmap="gray", norm=plt.Normalize(-1500, 1500))
    ax.contour(region, levels=[0.5], colors="gold", linewidths=0.8)
    ax.contour(pil, levels=[0.5], colors="magenta", linewidths=1.2)
    ax.plot_coord(own, "+", color="lime", ms=14, mew=2)
    ax.set_title(f"HMI mit Region (gelb) und Umkehrlinie bei ±{b_t} G (magenta)", fontsize=10)
    plt.colorbar(ax.images[0], ax=ax, label="B entlang der Sichtlinie [G]", shrink=0.8)
    plt.show()
    s.__dict__.update(B=B, mu=mu, c=c, flux=flux, region=region, Bs=Bs, pil=pil, dist_pil=dist_pil)


def ribbons(s, factor=30, min_pix=50):
    """Flare-Bänder in AIA 1600 Å (heller als factor × Median) und ihre Polarität im HMI-Bild."""
    subs, hmi, maps, B, mu, pil, dist_pil, km_per_arcsec = s.subs, s.hmi, s.maps, s.B, s.mu, s.pil, s.dist_pil, s.km_per_arcsec
    ny, nx = B.shape
    s1600 = subs[1600]
    thr = factor * np.median(s1600.data)
    rib_lab, n_rib = label(s1600.data > thr)
    A_1600 = (s1600.scale[0].to_value(u.arcsec / u.pix) * km_per_arcsec * 1e5) ** 2       # cm²
    print(f"Schwelle {thr:.0f} DN ({thr / maps[1600].exposure_time.to_value(u.s):.0f} DN/s), {n_rib} zusammenhängende Gebiete")

    rows = []
    for k in range(1, n_rib + 1):
        yy, xx = np.nonzero(rib_lab == k)
        if len(yy) < min_pix:
            continue
        w = s1600.pixel_to_world(xx * u.pix, yy * u.pix)
        p = hmi.world_to_pixel(w)                          # dieselben Orte im HMI-Bild
        hi = np.clip(np.round(p.y.value).astype(int), 0, ny - 1)
        hx = np.clip(np.round(p.x.value).astype(int), 0, nx - 1)
        b, m_ = B[hi, hx], mu[hi, hx]
        rows.append(dict(band=k, pixel=len(yy), flaeche_Mm2=len(yy) * A_1600 / 1e16 / m_.mean(),
                         B_mittel=b.mean(), anteil_pos=np.mean(b > 100), anteil_neg=np.mean(b < -100),
                         fluss=np.sum(b / m_ ** 2) * A_1600, abstand_PIL_Mm=np.median(dist_pil[hi, hx]),
                         Tx=w.Tx.to_value(u.arcsec).mean(), Ty=w.Ty.to_value(u.arcsec).mean()))
    rib = pd.DataFrame(rows)
    # Polarität eines Bandes: mehr als die Hälfte seiner Pixel über +100 G bzw. unter -100 G
    rib["polaritaet"] = np.select([rib.anteil_pos > 0.5, rib.anteil_neg > 0.5], ["positiv", "negativ"], "schwaches Feld")
    pd.set_option("display.width", 170)
    print(rib.round(2).to_string(index=False))
    pos, neg = rib[rib.polaritaet == "positiv"], rib[rib.polaritaet == "negativ"]
    print(f"\nBänder in positiver Polarität: {len(pos)}, {pos.flaeche_Mm2.sum():.0f} Mm², Fluss {pos.fluss.sum():+.2e} Mx")
    print(f"Bänder in negativer Polarität: {len(neg)}, {neg.flaeche_Mm2.sum():.0f} Mm², Fluss {neg.fluss.sum():+.2e} Mx")
    print(f"Verhältnis der Beträge: {pos.fluss.sum() / -neg.fluss.sum():.2f}")

    fig = plt.figure(figsize=(14, 6.5))
    ax = fig.add_subplot(1, 2, 1, projection=s1600)
    s1600.plot(axes=ax, norm=ImageNormalize(s1600.data, vmin=np.percentile(s1600.data, 1), vmax=np.nanmax(s1600.data),
                                             stretch=AsinhStretch(0.05)))
    ax.contour(rib_lab > 0, levels=[0.5], colors="white", linewidths=0.6)
    ax.set_title(f"AIA 1600 Å mit Bandpixeln (> {factor} × Median)", fontsize=10)
    ax2 = fig.add_subplot(1, 2, 2, projection=hmi)
    hmi.plot(axes=ax2, cmap="gray", norm=plt.Normalize(-1500, 1500))
    ax2.contour(pil, levels=[0.5], colors="magenta", linewidths=1)
    for _, r in rib.iterrows():
        yy, xx = np.nonzero(rib_lab == r.band)
        w = s1600.pixel_to_world(xx * u.pix, yy * u.pix)
        col = {"positiv": "tab:red", "negativ": "tab:blue"}.get(r.polaritaet, "gold")
        ax2.plot_coord(w, ".", ms=1, color=col, alpha=0.5)
    ax2.set_title("Bänder auf dem Magnetogramm (rot: positive, blau: negative Polarität; magenta: Umkehrlinie)", fontsize=10)
    fig.tight_layout()
    plt.show()
    s.rib = rib


def compare(s, timeout=30):
    """Positionen aus AIA, den Bändern und dem HMI-Fluss gegen den Katalogeintrag in HEK."""
    PEAK, m131, own, rib, flux, region, c, B0 = s.PEAK, s.m131, s.own, s.rib, s.flux, s.region, s.c, s.B0
    hmi, subs, Bs, dist_pil, km_per_arcsec = s.hmi, s.subs, s.Bs, s.dist_pil, s.km_per_arcsec
    HEK_FALLBACK = dict(hpc_x=48.66, hpc_y=-353.99, ar_noaanum=13842, fl_goescls="X9.0",
                        quelle="frühere HEK-Abfrage (SSW Latest Events), weil HEK nicht antwortete")
    socket.setdefaulttimeout(timeout)               # HEK hängt sonst minutenlang, wenn der Dienst gestört ist
    try:
        res = hek.HEKClient().search(a.Time(PEAK - 20 * u.min, PEAK + 20 * u.min), a.hek.EventType("FL"),
                                     a.hek.FL.GOESCls >= "X1.0")
        # Einträge von SWPC haben keine echte Position (hpc_x = 0); SSW Latest Events bestimmt sie aus Bildern
        res = [r for r in res if str(r["frm_name"]) == "SSW Latest Events"]
        if len(res) == 0:
            raise RuntimeError("kein Eintrag von SSW Latest Events")
        r0 = res[0]
        ar = int(r0["ar_noaanum"])
        cat = dict(hpc_x=float(r0["hpc_x"]), hpc_y=float(r0["hpc_y"]),
                   ar_noaanum=ar + 10000 if ar < 10000 else ar,      # SSW nennt die Region vierstellig (3842 = 13842)
                   fl_goescls=str(r0["fl_goescls"]), quelle=f"HEK, {r0['frm_name']}")
    except Exception as e:
        print(f"HEK nicht verfügbar ({type(e).__name__}: {str(e)[:80]})")
        cat = HEK_FALLBACK
    finally:
        socket.setdefaulttimeout(None)

    cat_c = SkyCoord(cat["hpc_x"] * u.arcsec, cat["hpc_y"] * u.arcsec, frame=m131.coordinate_frame)
    mid = SkyCoord(np.average(rib.Tx, weights=rib.pixel) * u.arcsec, np.average(rib.Ty, weights=rib.pixel) * u.arcsec,
                   frame=m131.coordinate_frame)
    w_reg = np.abs(flux) * region
    cen = SkyCoord(np.sum(c.Tx.to_value(u.arcsec) * w_reg) / w_reg.sum() * u.arcsec,
                   np.sum(c.Ty.to_value(u.arcsec) * w_reg) / w_reg.sum() * u.arcsec,
                   frame=m131.coordinate_frame)          # 43 s Zeitunterschied zu HMI: vernachlässigbar

    print(f"Katalog: {cat['fl_goescls']} in NOAA {cat['ar_noaanum']}  ({cat['quelle']})\n")
    print(f"{'Position':<38}{'Tx':>8}{'Ty':>9}{'':>3}{'heliogr.':<10}{'Abstand zu HEK':>16}")
    for name, pt in (("HEK", cat_c), ("hellster Punkt AIA 131 Å", own), ("Mitte der Bänder AIA 1600 Å", mid),
                     ("Flussschwerpunkt der Region (HMI)", cen)):
        la, lo, _ = to_stonyhurst(pt.Tx, pt.Ty, m131.rsun_obs, B0)
        d = pt.separation(cat_c).to_value(u.arcsec)
        print(f"{name:<38}{pt.Tx.to_value(u.arcsec):>7.1f}″{pt.Ty.to_value(u.arcsec):>8.1f}″   {label_ns(la, lo):<10}"
              f"{d:>7.1f}″ = {d * km_per_arcsec / 1e3:>4.0f} Mm")
    p_hek = hmi.world_to_pixel(cat_c)
    jh, ih = int(round(p_hek.y.value)), int(round(p_hek.x.value))
    p131 = subs[131].world_to_pixel(cat_c)
    v131 = subs[131].data[int(round(p131.y.value)), int(round(p131.x.value))]
    print(f"\nAn der HEK-Position: B = {Bs[jh, ih]:+.0f} G, {dist_pil[jh, ih]:.1f} Mm von der Umkehrlinie, "
          f"AIA 131 Å {v131:.0f} DN (Maximum im Ausschnitt {subs[131].data.max():.0f} DN)")
