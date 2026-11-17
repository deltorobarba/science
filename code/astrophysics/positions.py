"""Wo auf der Sonne Flares entstehen, für sun.ipynb: Röntgenflares aus den Ereignislisten der NOAA, ihre Regionen und
Positionen (mit differentieller Rotation auf die Flarezeit gedreht), aktive Breiten, δ-Regionen, das
Schmetterlingsdiagramm seit 2016 und der Vergleich mit Hα-Positionen und HEK.

Daten: tägliche Solar Event Reports und Solar Region Summaries (SRS) des Space Weather Prediction Center im Archiv der
NOAA (NGDC), Cache in data/sun/swpc/; HEK über sunpy, wenn erreichbar. Alle Schritte teilen sich ein Zustandsobjekt,
das `load` anlegt.
"""
import re
import socket
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from astropy.time import Time

import sundata                                         # vor sunpy: Downloads nach data/sun/sunpy
from sunpy.coordinates import sun

SWPC = sundata.DATA / "swpc"
BASE = "https://www.ngdc.noaa.gov/stp/space-weather/swpc-products/daily_reports"
A_ROT, B_ROT, C_ROT, EARTH = 14.713, -2.396, -1.787, 360 / 365.25     # differentielle Rotation [°/Tag], Erdumlauf
LOC = re.compile(r"([NS])(\d\d)([EW])(\d\d)")


def fetch(kind, day):
    """Eine Tagesdatei laden (kind = 'events' oder 'SRS'); fehlt sie im Archiv, None."""
    SWPC.mkdir(parents=True, exist_ok=True)
    sub = "solar_event_reports" if kind == "events" else "solar_region_summaries"
    path = SWPC / f"{day:%Y%m%d}{kind}.txt"
    if not path.exists():
        try:
            urllib.request.urlretrieve(f"{BASE}/{sub}/{day:%Y/%m}/{day:%Y%m%d}{kind}.txt", path)
        except Exception:
            return None
    return path


def fetch_many(kind, days):
    with ThreadPoolExecutor(8) as ex:                 # 8 Downloads gleichzeitig
        return list(ex.map(lambda d: fetch(kind, d), days))


def parse_loc(s):
    """'S15E06' -> (-15, -6); Norden und Westen positiv."""
    m = LOC.fullmatch(s)
    if not m:
        return np.nan, np.nan
    return int(m[2]) * (1 if m[1] == "N" else -1), int(m[4]) * (1 if m[3] == "W" else -1)


def parse_events(path, day):
    rows = []
    for line in path.read_text(errors="replace").splitlines():
        if not re.match(r"^\s*\d+\s", line):
            continue
        tok = line.split()
        if tok[1] == "+":                             # '+' markiert ein Ereignis mit mehreren Beobachtungen
            tok.pop(1)
        if len(tok) < 8:
            continue
        rest = tok[7:]
        reg = int(rest[-1]) if len(rest) >= 3 and re.fullmatch(r"\d{4,5}", rest[-1]) else np.nan
        rows.append(dict(tag=day, ev=int(tok[0]), beginn=tok[1], maximum=tok[2], ende=tok[3], obs=tok[4],
                         typ=tok[6], rest=rest, reg=reg))
    return rows


def parse_srs(path, day):
    rows, inside = [], False
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith("I.  Regions with Sunspots"):
            inside = True
            continue
        if line.startswith(("IA.", "II.")):
            break
        tok = line.split()
        if inside and len(tok) >= 8 and tok[0].isdigit():
            lat, lon = parse_loc(tok[1])
            rows.append(dict(tag=day, reg=int(tok[0]), lat=lat, lon=lon, carr=int(tok[2]), flaeche=int(tok[3]),
                             zurich=tok[4], n_flecken=int(tok[6]), mag=tok[7]))
    return rows


def flux(cls):
    try:
        return {"A": 1e-8, "B": 1e-7, "C": 1e-6, "M": 1e-5, "X": 1e-4}[cls[0]] * float(cls[1:])
    except (KeyError, ValueError, IndexError):
        return np.nan


def hours(s):
    m = re.search(r"\d{4}", s)                        # Vorsilben U, A, B (unsicher, nach, vor) ignorieren
    return int(m[0][:2]) + int(m[0][2:]) / 60 if m else np.nan


def omega_syn(lat):
    """Synodische Rotationsgeschwindigkeit [°/Tag] bei der Breite lat."""
    s2 = np.sin(np.radians(lat)) ** 2
    return A_ROT + B_ROT * s2 + C_ROT * s2 ** 2 - EARTH


def label_ns(lat, lon):
    return f"{'N' if lat >= 0 else 'S'}{abs(lat):02.0f}{'W' if lon >= 0 else 'E'}{abs(lon):02.0f}"


def load(year=2024, butterfly_start="2016-01-01"):
    """Ereignislisten und SRS eines Jahres, dazu jede siebte SRS seit butterfly_start."""
    days = pd.date_range(f"{year}-01-01", f"{year}-12-31")
    ev_paths, srs_paths = fetch_many("events", days), fetch_many("SRS", days)
    events = pd.DataFrame([r for d, p in zip(days, ev_paths) if p for r in parse_events(p, d)])
    srs = pd.DataFrame([r for d, p in zip(days, srs_paths) if p for r in parse_srs(p, d)])
    wdays = pd.date_range(butterfly_start, pd.Timestamp.today() - pd.Timedelta(days=2), freq="7D")
    srs_w = pd.DataFrame([r for d, p in zip(wdays, fetch_many("SRS", wdays)) if p for r in parse_srs(p, d)])

    print(f"{year}: {sum(p is not None for p in ev_paths)} Ereignislisten, {sum(p is not None for p in srs_paths)} SRS "
          f"(von {len(days)} Tagen)")
    print(f"Ereignisse nach Typ: {events.typ.value_counts().head(6).to_dict()}")
    print(f"SRS {year}: {len(srs)} Regionstage, {srs.reg.nunique()} Regionen")
    print(f"Schmetterlingsdiagramm: {srs_w.tag.nunique()} SRS von {srs_w.tag.min():%Y-%m-%d} bis {srs_w.tag.max():%Y-%m-%d}, "
          f"{srs_w.reg.nunique()} Regionen")
    return SimpleNamespace(year=year, events=events, srs=srs, srs_w=srs_w)


def xray(s):
    """Röntgenflares (XRA) mit Klasse, Spitzenfluss, Zeit des Maximums und Region."""
    events = s.events
    fl = events[events.typ == "XRA"].copy()
    fl["klasse"] = fl.rest.str[1]
    fl["F"] = fl.klasse.map(flux)
    h = [hours(m) if "/" not in m else hours(b) for m, b in zip(fl.maximum, fl.beginn)]
    fl["t_max"] = (fl.tag + pd.to_timedelta(h, unit="h")).dt.round("min")
    fl["noaa"] = (fl.reg + 10000).astype("Int64")         # NOAA zählt seit 2002 über 10000, die Listen nur 4 Stellen
    fl = fl.dropna(subset=["F"]).reset_index(drop=True)
    counts = fl.klasse.str[0].value_counts()
    print(f"{len(fl)} Röntgenflares: " + ", ".join(f"{c} {counts.get(c, 0)}" for c in "BCMX"))
    print(f"Ohne Regionsangabe: {fl.reg.isna().mean():.1%} (Klasse M und X: {fl[fl.F >= 1e-5].reg.isna().mean():.1%})")
    print(f"Davon von GOES-16: {(fl.obs == 'G16').mean():.0%}, GOES-18: {(fl.obs == 'G18').mean():.0%}")
    print("\nDie zehn stärksten Flares:")
    print(fl.nlargest(10, "F")[["t_max", "klasse", "noaa"]].to_string(index=False))
    s.fl = fl


def locate(s):
    """Position jedes Flares: Region aus der SRS, mit differentieller Rotation auf die Flarezeit gedreht; Bild auf der Scheibe."""
    fl, srs = s.fl, s.srs
    idx = srs.drop_duplicates(["tag", "reg"]).set_index(["tag", "reg"])
    pos = []
    for _, r in fl.iterrows():
        hit = None
        if not np.isnan(r.reg):
            for shift, source in ((0, "SRS desselben Tages"), (1, "SRS des Folgetags"), (-1, "SRS des Vortags")):
                key = (r.tag + pd.Timedelta(days=shift), int(r.reg))
                if key in idx.index:
                    sr = idx.loc[key]
                    dt = (r.t_max - key[0]).total_seconds() / 86400          # Tage seit 00:00 UT der SRS
                    hit = (sr.lat, sr.lon + omega_syn(sr.lat) * dt, sr.lon, sr.mag, sr.flaeche, source)
                    break
        pos.append(hit if hit else (np.nan, np.nan, np.nan, None, np.nan,
                                    "keine Region" if np.isnan(r.reg) else "Region nicht in der SRS"))
    fl[["lat", "lon", "lon_srs", "mag", "flaeche", "quelle"]] = pd.DataFrame(pos, index=fl.index)
    print(fl.quelle.value_counts().to_string())

    # Bildkoordinaten mit B0 und scheinbarem Sonnenradius zum Zeitpunkt jedes Flares
    ok = fl.lat.notna()
    tt = Time(list(fl.t_max[ok]))
    B0 = sun.B0(tt).to_value("rad")
    R_as = sun.angular_radius(tt).to_value("arcsec")
    phi, lam = np.radians(fl.lat[ok]), np.radians(fl.lon[ok])
    fl.loc[ok, "Tx"] = R_as * np.cos(phi) * np.sin(lam)
    fl.loc[ok, "Ty"] = R_as * (np.sin(phi) * np.cos(B0) - np.cos(phi) * np.cos(lam) * np.sin(B0))
    fl.loc[ok, "z"] = np.sin(phi) * np.sin(B0) + np.cos(phi) * np.cos(lam) * np.cos(B0)
    behind = fl.z < 0
    print(f"\nPosition bestimmt für {ok.mean():.1%} der Flares; davon hinter dem Rand (z < 0): {behind.sum()}, "
          f"davon {(behind & (fl.lon > 0)).sum()} am Westrand (Region schon hinter dem Rand, Flare noch sichtbar)")
    ex = fl.loc[fl.F.idxmax()]
    print(f"Stärkster Flare {ex.klasse} am {ex.t_max:%Y-%m-%d %H:%M} in NOAA {ex.noaa}: SRS {label_ns(ex.lat, ex.lon_srs)} um 00 UT "
          f"→ gedreht {label_ns(ex.lat, ex.lon)} ({ex.lon - ex.lon_srs:+.1f}°), Tx = {ex.Tx:.0f}″, Ty = {ex.Ty:.0f}″")

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.add_patch(plt.Circle((0, 0), 960, fill=False, color="0.4"))
    for lat0 in range(-60, 61, 15):                       # Breitenkreise für B0 = 0 zur Orientierung
        th = np.radians(np.linspace(-90, 90, 100))
        ax.plot(960 * np.cos(np.radians(lat0)) * np.sin(th), np.full_like(th, 960 * np.sin(np.radians(lat0))),
                c="0.85", lw=0.6, zorder=0)
    for lo, hi, col, name in ((1e-5, 1e-4, "tab:orange", "M"), (1e-4, 1, "tab:red", "X"), (1e-6, 1e-5, "tab:blue", "C")):
        sel = fl[(fl.F >= lo) & (fl.F < hi) & (fl.z > 0)]
        ax.scatter(sel.Tx, sel.Ty, s=5 + 2e5 * sel.F, c=col, alpha=0.5 if name == "C" else 0.8,
                   edgecolor="k" if name != "C" else "none", lw=0.3, label=f"{name} ({len(sel)})")
    ax.set_aspect("equal")
    ax.set_xlim(-1050, 1050)
    ax.set_ylim(-1050, 1050)
    ax.set_xlabel("Tx [″] (Westen rechts)")
    ax.set_ylabel("Ty [″] (Norden oben)")
    ax.set_title(f"Flares {s.year} auf der Sonnenscheibe (Größe ~ Spitzenfluss)")
    ax.legend(fontsize=8, loc="upper right")
    plt.show()
    s.ok = ok


def latitudes(s):
    """Breiten der Flares und Regionen, Nord-Süd-Asymmetrie."""
    fl, srs, ok = s.fl, s.srs, s.ok
    p = fl[ok]
    for lo, name in ((1e-6, "C und stärker"), (1e-5, "M und stärker"), (1e-4, "X")):
        sel = p[p.F >= lo]
        n_n, n_s = (sel.lat > 0).sum(), (sel.lat < 0).sum()
        asym = (n_n - n_s) / (n_n + n_s)
        print(f"{name:<14} n = {len(sel):>4}: |Breite| Median {sel.lat.abs().median():4.1f}°, mittlere 50 % "
              f"{sel.lat.abs().quantile(.25):.0f}°–{sel.lat.abs().quantile(.75):.0f}°;  Nord {n_n}, Süd {n_s}, "
              f"Asymmetrie {asym:+.2f} ± {2 * np.sqrt(n_n * n_s / (n_n + n_s) ** 3):.2f}")
    regions = srs.drop_duplicates("reg")
    print(f"Regionen {s.year} (erste Sichtung): |Breite| Median {regions.lat.abs().median():.1f}°, "
          f"Nord {(regions.lat > 0).sum()}, Süd {(regions.lat < 0).sum()}")

    fig, ax = plt.subplots(figsize=(10, 3.8))
    bins = np.arange(-45, 46, 2.5)
    ax.hist(regions.lat, bins=bins, color="0.8", label=f"Regionen ({len(regions)})")
    ax.hist(p[p.F >= 1e-6].lat, bins=bins, histtype="step", color="tab:blue", lw=1.5, label="Flares ≥ C1")
    ax.hist(p[p.F >= 1e-5].lat, bins=bins, color="tab:orange", alpha=0.8, label="Flares ≥ M1")
    ax.set_xlabel("heliographische Breite [°] (Süden negativ)")
    ax.set_ylabel("Anzahl")
    ax.set_title(f"Aktive Breiten {s.year}")
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()


def delta(s):
    """Wie viele Flares aus Regionen mit δ-Konfiguration kommen, und die produktivsten Regionen."""
    fl, srs = s.fl, s.srs
    p_delta = srs.mag.str.contains("Delta").mean()
    print(f"Anteil der Regionstage mit δ-Klasse: {p_delta:.1%}  ({len(srs)} Regionstage)\n")
    known = fl[fl.mag.notna()]
    print(f"{'Klasse':<8}{'Flares':>8}{'aus δ-Regionen':>18}{'Anreicherung':>15}")
    for lo, name in ((1e-6, "C"), (1e-5, "M"), (1e-4, "X")):
        sel = known[(known.F >= lo) & (known.F < lo * 10)]
        q = sel.mag.str.contains("Delta").mean()
        err = np.sqrt(q * (1 - q) / len(sel))
        print(f"{name:<8}{len(sel):>8}{q:>12.0%} ± {err:.0%}{q / p_delta:>13.1f}×")

    top = (fl[fl.F >= 1e-5].groupby("noaa")
           .agg(M_und_X=("F", "size"), X=("F", lambda f: (f >= 1e-4).sum()), staerkster=("klasse", lambda c: c.iloc[np.argmax(c.map(flux))]),
                erster=("t_max", "min"), lat=("lat", "median")))
    mag = srs.assign(noaa=srs.reg + 10000).groupby("noaa").agg(
        max_flaeche=("flaeche", "max"), delta_tage=("mag", lambda m: m.str.contains("Delta").sum()), tage=("mag", "size"))
    top = top.join(mag).sort_values("M_und_X", ascending=False)
    print(f"\nDie produktivsten Regionen (Fläche in Millionstel der Halbkugel):")
    print(top.head(8).to_string(formatters={"erster": lambda t: f"{t:%Y-%m-%d}", "lat": "{:+.0f}".format}))
    share = top.head(10).M_und_X.sum() / top.M_und_X.sum()
    print(f"\nDie zehn produktivsten von {len(top)} Regionen mit M- oder X-Flares erzeugten {share:.0%} dieser Flares.")


def butterfly(s, t_min=2019.96):
    """Schmetterlingsdiagramm aus jeder siebten SRS und das exponentielle Wandern der Zonen in Zyklus 25.

    t_min: Minimum zwischen Zyklus 24 und 25 (Teil Sonnenflecken)."""
    srs_w = s.srs_w
    first = srs_w.sort_values("tag").groupby("reg").agg(tag=("tag", "first"), lat=("lat", "first"),
                                                         flaeche=("flaeche", "max"))
    first["jahr"] = first.tag.dt.year + (first.tag.dt.dayofyear - 0.5) / 365.25
    first = first.dropna(subset=["lat"])

    # Zyklus 25: Regionen ab Mitte 2020, als die letzten Regionen von Zyklus 24 verschwunden waren
    c25 = first[first.jahr >= 2020.5]
    law = lambda t, phi0, tau: phi0 * np.exp(-(t - t_min) / tau)
    fits = {}
    for name, sel in (("beide", c25), ("Nord", c25[c25.lat > 0]), ("Süd", c25[c25.lat < 0])):
        pr, cv = curve_fit(law, sel.jahr, sel.lat.abs(), p0=[25, 10])
        fits[name] = pr
        print(f"{name:<6} n = {len(sel):>4}: φ0 = {pr[0]:.1f} ± {np.sqrt(cv[0, 0]):.1f}°,  τ = {pr[1]:.1f} ± {np.sqrt(cv[1, 1]):.1f} Jahre")
    print("\nMittlere |Breite| neuer Regionen pro Jahr:")
    yearly = first.groupby(first.tag.dt.year).agg(n=("lat", "size"), mittel=("lat", lambda l: l.abs().mean()),
                                                  unter_10=("lat", lambda l: (l.abs() < 10).mean()))
    print(yearly.round(2).T.to_string())

    fig, ax = plt.subplots(figsize=(13, 4.8))
    # Zuordnung für die Farbe: bis Mitte 2018 alles Zyklus 24, bis Mitte 2020 nur Regionen unter 15° Breite
    cyc24 = (first.jahr < 2018.5) | ((first.jahr < 2020.5) & (first.lat.abs() < 15))
    for sel, col, name in ((cyc24, "0.5", "Zyklus 24"), (~cyc24, "tab:red", "Zyklus 25")):
        ax.scatter(first.jahr[sel], first.lat[sel], s=3 + first.flaeche[sel] / 15, c=col, alpha=0.5, lw=0, label=name)
    ax.legend(fontsize=8, loc="lower left")
    tt_fit = np.linspace(2020.5, first.jahr.max(), 100)
    for sign in (1, -1):
        ax.plot(tt_fit, sign * law(tt_fit, *fits["beide"]), c="black", lw=1.5)
    ax.axvline(t_min, c="tab:blue", ls=":", lw=1)
    ax.text(t_min, 42, " Minimum Dez. 2019", fontsize=8, color="tab:blue")
    ax.axhline(0, c="0.7", lw=0.5)
    ax.set_ylim(-48, 48)
    ax.set_xlabel("Jahr (erste Sichtung der Region)")
    ax.set_ylabel("heliographische Breite [°]")
    ax.set_title("Schmetterlingsdiagramm aus der Solar Region Summary (Punktgröße ~ Fläche; schwarz: exponentielles Gesetz)")
    fig.tight_layout()
    plt.show()


def compare(s):
    """Eigene Positionen gegen Hα-Positionen derselben Ereignisse, den X-Flare in drei Quellen und HEK."""
    fl, events, YEAR = s.fl, s.events, s.year
    # a) Hα-Positionen (FLA) desselben Ereignisses
    fla = events[events.typ == "FLA"].copy()
    fla[["h_lat", "h_lon"]] = pd.DataFrame([parse_loc(r[0]) for r in fla.rest], index=fla.index)
    m = fl.merge(fla.drop_duplicates(["tag", "ev"])[["tag", "ev", "h_lat", "h_lon"]], on=["tag", "ev"]).dropna(subset=["lat", "h_lat"])
    d_lat, d_lon = m.lat - m.h_lat, m.lon - m.h_lon
    d = np.hypot(d_lat, d_lon * np.cos(np.radians(m.h_lat)))
    print(f"a) {len(m)} Flares haben auch eine Hα-Position ({(m.F >= 1e-5).sum()} davon M oder X).")
    print(f"   Abstand eigene Position - Hα: Median {np.median(d):.1f}°, 90 % unter {np.quantile(d, 0.9):.1f}°;  "
          f"Breite {d_lat.median():+.1f}°, Länge {d_lon.median():+.1f}° im Median")
    d0 = np.hypot(d_lat, (m.lon_srs - m.h_lon) * np.cos(np.radians(m.h_lat)))     # Position von 00 UT, ungedreht
    print(f"   ohne Drehung auf die Flarezeit: Median {np.median(d0):.1f}°")

    # b) der X-Flare vom 3. Oktober 2024 in drei Quellen
    if YEAR == 2024:
        x9 = fl[(fl.tag == "2024-10-03") & (fl.F >= 1e-4)].iloc[0]
        print(f"\nb) {x9.klasse} am 2024-10-03 {x9.t_max:%H:%M} UT in NOAA {x9.noaa}:")
        print(f"   eigene Position (SRS + Rotation)     {label_ns(x9.lat, x9.lon)}  ({x9.lat:+.0f}°, {x9.lon:+.1f}°)")
        print(f"   SDO, hellster Punkt in AIA 131 Å     S16W05  (-16.4°, +5.2°; Teil SDO unten)")
        print(f"   HEK (SSW Latest Events)              S15W03  (frühere Abfrage)")

    # c) HEK direkt, falls erreichbar
    print(f"\nc) HEK: Flares ab M5 im Jahr {YEAR}")
    big = fl[fl.F >= 5e-5]
    print(f"   eigene Liste: {len(big)} Flares ab M5, {big.lat.notna().sum()} mit Position"
          + ("; frühere HEK-Abfrage (SSW Latest Events) für 2024: 143" if YEAR == 2024 else ""))
    socket.setdefaulttimeout(60)
    try:
        from sunpy.net import attrs as a, hek
        res = hek.HEKClient().search(a.Time(f"{YEAR}-01-01", f"{YEAR}-12-31 23:59"), a.hek.EventType("FL"),
                                     a.hek.FL.GOESCls >= "M5.0", a.hek.FRM.Name == "SSW Latest Events")
        if len(res) == 0:
            raise RuntimeError("keine Einträge")
        hk = res["event_peaktime", "fl_goescls", "hgs_x", "hgs_y"].to_pandas()
        hk["t"] = pd.to_datetime(hk.event_peaktime)
        mm = pd.merge_asof(big.dropna(subset=["lat"]).sort_values("t_max"), hk.sort_values("t"), left_on="t_max",
                           right_on="t", direction="nearest", tolerance=pd.Timedelta("10min")).dropna(subset=["hgs_y"])
        dd = np.hypot(mm.lat - mm.hgs_y, (mm.lon - mm.hgs_x) * np.cos(np.radians(mm.lat)))
        print(f"   HEK: {len(hk)} Flares; {len(mm)} zugeordnet, Abstand Median {np.median(dd):.1f}°, 90 % unter {np.quantile(dd, 0.9):.1f}°")
    except Exception as e:
        print(f"   HEK nicht erreichbar ({type(e).__name__}); später erneut ausführen")
    finally:
        socket.setdefaulttimeout(None)

    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.hist(d, bins=np.arange(0, 20.5, 0.5), color="0.4", label="mit Drehung")
    ax.hist(d0, bins=np.arange(0, 20.5, 0.5), histtype="step", color="tab:red", label="ohne Drehung")
    ax.set_xlabel("Abstand zur Hα-Position [°]")
    ax.set_ylabel("Flares")
    ax.set_title("Eigene Position gegen Hα")
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()
