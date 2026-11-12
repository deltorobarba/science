"""SIMBAD-Abfragen für multiwavelength_astronomy.ipynb: der Messier-Katalog, ein Objekt nach Namen, seine Entfernung.

SIMBAD läuft in Straßburg (CDS) und als Spiegel an der CfA in Harvard. Fällt einer aus (CDS antwortete am 2026-11-12
mit 404), fragt der Code den nächsten. Jede Antwort wird in `cache_dir` gespeichert, ein zweiter Lauf braucht SIMBAD
dann nicht mehr.
"""
import io
import json
import re
import textwrap
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord

SIMBAD_TAP = ["https://simbad.cds.unistra.fr/simbad/sim-tap/sync",
              "https://simbad.cfa.harvard.edu/simbad/sim-tap/sync"]

# Vier große Nebel führt SIMBAD unter dem Sternhaufen in ihrer Mitte (Typ OpC, Größe des Haufens).
# Hier die ungefähre Größe des Nebels in Bogenminuten, damit das Bildfeld passt.
NEBULAE_FILED_AS_CLUSTERS = {"M 8": 90.0, "M 16": 35.0, "M 17": 11.0, "M 20": 28.0}
NEBULA_TYPES = {"HII", "PN", "SNR", "RNe", "DNe", "GNe", "ISM", "Cld", "MoC", "bub", "EmO", "SFR"}
DEFAULT_SIZE = 15.0        # Bogenminuten, wenn SIMBAD keine Größe kennt
PC_TO_LY = 3.26156


def simbad(adql, timeout=60):
    """ADQL-Abfrage an SIMBAD als DataFrame; probiert die Server der Reihe nach."""
    query = urllib.parse.urlencode({"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": adql})
    errors = []
    for server in SIMBAD_TAP:
        try:
            with urllib.request.urlopen(f"{server}?{query}", timeout=timeout) as r:
                data = r.read()
            if data.lstrip()[:1] == b"<":                 # HTML-Fehlerseite statt CSV
                raise OSError("HTML statt CSV")
            return pd.read_csv(io.BytesIO(data))
        except Exception as e:
            errors.append(f"{urllib.parse.urlparse(server).netloc}: {e}")
    raise OSError("SIMBAD nicht erreichbar: " + "; ".join(errors))


def kind_of(otype, path, name=""):
    """Grobe Klasse für die Auswahl: Galaxie, Nebel, Sternhaufen oder sonstiges."""
    if name in NEBULAE_FILED_AS_CLUSTERS:
        return "Nebel"
    if str(path).startswith("G"):
        return "Galaxie"
    if otype in NEBULA_TYPES or str(path).startswith("ISM"):
        return "Nebel"
    if str(path).startswith("Cl*") or otype == "As*":
        return "Sternhaufen"
    return "sonstiges"


def messier(cache_dir):
    """Alle 110 Messier-Objekte mit Typ, Lage, Größe und Helligkeit (Cache: messier.csv)."""
    path = Path(cache_dir) / "messier.csv"
    if path.exists():
        return pd.read_csv(path)
    df = simbad("""
        SELECT i.id, b.main_id, b.otype, d.description, d.path, b.ra, b.dec,
               b.galdim_majaxis, f.V AS vmag
        FROM ident AS i JOIN basic AS b ON b.oid = i.oidref
        JOIN otypedef AS d ON d.otype = b.otype
        LEFT JOIN allfluxes AS f ON f.oidref = b.oid
        WHERE i.id LIKE 'M %'""")                    # SIZE ist in ADQL reserviert, deshalb kein Alias "size"
    df["size"] = df["galdim_majaxis"]
    df["name"] = df["id"].str.replace(r"\s+", " ", regex=True).str.strip()
    df = df[df["name"].str.fullmatch(r"M \d+")].copy()        # ohne Minkowski-Nebel wie "M 1-92"
    df["number"] = df["name"].str[2:].astype(int)
    df["kind"] = [kind_of(o, p, n) for o, p, n in zip(df["otype"], df["path"], df["name"])]
    for name, size in NEBULAE_FILED_AS_CLUSTERS.items():
        df.loc[df["name"] == name, "size"] = size
    df = df.sort_values("number").drop_duplicates("name")
    df = df[["name", "kind", "otype", "description", "ra", "dec", "size", "vmag"]].reset_index(drop=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return df


def show_messier(df):
    """Galaxien und Nebel als kurze Liste: Name, SIMBAD-Typ, Größe in Bogenminuten."""
    plural = {"Galaxie": "Galaxien", "Nebel": "Nebel", "Sternhaufen": "Sternhaufen", "sonstiges": "sonstige"}
    counts = df["kind"].value_counts()
    print(f"{len(df)} Messier-Objekte: " + ", ".join(f"{n} {plural[k]}" for k, n in counts.items()))
    print("In Klammern der SIMBAD-Typ und die Größe (große Achse in Bogenminuten).")
    for kind in ["Galaxie", "Nebel"]:
        sub = df[df["kind"] == kind]
        items = [f"{r.name} ({r.otype}, {r.size:.0f}′)" if np.isfinite(r.size) else f"{r.name} ({r.otype})"
                 for r in sub.itertuples()]
        print(f"\n{plural[kind]} ({len(sub)}):")
        print(textwrap.fill(", ".join(items), width=110, initial_indent="  ", subsequent_indent="  "))


@dataclass
class Target:
    name: str
    main_id: str
    otype: str
    description: str
    kind: str
    ra: float
    dec: float
    size: float              # große Achse [′]
    minor: float             # kleine Achse [′]
    pa: float                # Positionswinkel der großen Achse, von Norden über Osten [°]
    size_from_simbad: bool
    vmag: float
    dist_pc: float           # Median der Entfernungen ohne Rotverschiebung, NaN wenn keine
    n_dist: int

    @property
    def coord(self):
        return SkyCoord(self.ra, self.dec, unit="deg")

    @property
    def ly_per_arcmin(self):
        return self.dist_pc * PC_TO_LY * np.radians(1 / 60)


def lookup(name, cache_dir):
    """Ein Objekt nach Namen (alles, was SIMBAD kennt), mit Größe und Entfernung (Cache: <Name>/simbad.json)."""
    safe = "".join(c if c.isalnum() else "_" for c in name.strip())
    path = Path(cache_dir) / safe / "simbad.json"
    if path.exists():
        return Target(**json.loads(path.read_text()))
    q = name.replace("'", "''")
    b = simbad(f"""
        SELECT b.main_id, b.otype, d.description, d.path, b.ra, b.dec,
               b.galdim_majaxis, b.galdim_minaxis, b.galdim_angle, f.V AS vmag
        FROM ident AS i JOIN basic AS b ON b.oid = i.oidref
        JOIN otypedef AS d ON d.otype = b.otype
        LEFT JOIN allfluxes AS f ON f.oidref = b.oid
        WHERE i.id = '{q}'""")
    if len(b) == 0:
        raise ValueError(f"SIMBAD kennt '{name}' nicht; Schreibweise prüfen (z. B. 'M 51', 'NGC 891', 'Orion Nebula')")
    b = b.iloc[0]
    main = " ".join(str(b["main_id"]).split())
    messier_name = re.sub(r"^M\s*(\d+)$", r"M \1", name.strip(), flags=re.IGNORECASE)   # "m17" -> "M 17"
    listed = next((k for k in (main, messier_name) if k in NEBULAE_FILED_AS_CLUSTERS), None)
    size, from_simbad = b["galdim_majaxis"], True
    if listed:
        size, from_simbad = NEBULAE_FILED_AS_CLUSTERS[listed], False
    if not np.isfinite(size):
        size, from_simbad = DEFAULT_SIZE, False
    minor = b["galdim_minaxis"] if from_simbad and np.isfinite(b["galdim_minaxis"]) else size
    pa = float(b["galdim_angle"]) if from_simbad and np.isfinite(b["galdim_angle"]) else 0.0

    d = simbad(f"""
        SELECT m.dist, m.unit, m.method
        FROM mesDistance AS m JOIN ident AS i ON i.oidref = m.oidref
        WHERE i.id = '{q}'""")
    to_pc = {"pc": 1.0, "kpc": 1e3, "Mpc": 1e6}
    d["pc"] = d["dist"] * d["unit"].astype(str).str.strip().map(to_pc)
    d = d[d["method"].astype(str).str.strip() != "redshift"].dropna(subset=["pc"])

    t = Target(name=name, main_id=main, otype=b["otype"], description=b["description"],
               kind=kind_of(b["otype"], b["path"], listed or main), ra=float(b["ra"]), dec=float(b["dec"]),
               size=float(size), minor=float(minor), pa=pa, size_from_simbad=bool(from_simbad),
               vmag=float(b["vmag"]) if np.isfinite(b["vmag"]) else float("nan"),
               dist_pc=float(d["pc"].median()) if len(d) else float("nan"), n_dist=int(len(d)))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(t), indent=1))
    return t


def distance_text(pc):
    if pc >= 1e6:
        return f"{pc / 1e6:.1f} Mpc = {pc * PC_TO_LY / 1e6:.0f} Millionen Lichtjahre"
    return f"{pc:,.0f} pc = {pc * PC_TO_LY:,.0f} Lichtjahre".replace(",", " ")


def describe(t, fov, npix):
    """Steckbrief des Objekts und des Bildfelds."""
    size_note = "laut SIMBAD" if t.size_from_simbad else "angenommen, SIMBAD kennt keine Größe des Nebels"
    print(t.name + (f"  (in SIMBAD: {t.main_id})" if t.main_id != " ".join(t.name.split()) else ""))
    print(f"Typ:          {t.kind}, {t.description} ({t.otype})")
    print(f"Koordinaten:  {t.coord.to_string('hmsdms', precision=0)}  (RA {t.ra:.4f}°, Dec {t.dec:+.4f}°)")
    print(f"Größe:        {t.size:.1f}′ × {t.minor:.1f}′, PA {t.pa:.0f}°  ({size_note})")
    if np.isfinite(t.vmag):
        print(f"Helligkeit:   V = {t.vmag:.2f}")
    if np.isfinite(t.dist_pc):
        print(f"Entfernung:   {distance_text(t.dist_pc)}  (Median aus {t.n_dist} Messungen ohne Rotverschiebung)")
        per = f"{t.ly_per_arcmin:,.0f}" if t.ly_per_arcmin >= 100 else f"{t.ly_per_arcmin:.1f}"
        size = f"{t.size * t.ly_per_arcmin:,.0f}"
        print(f"Maßstab:      1′ = {per} Lichtjahre; große Achse {size} Lichtjahre".replace(",", " "))
    else:
        print("Entfernung:   keine Messung in SIMBAD; die Bilder haben keinen Maßstab in Lichtjahren")
    print(f"Bildfeld:     {fov:.1f}′ × {fov:.1f}′ mit {npix} × {npix} Pixeln ({fov * 60 / npix:.1f}″ pro Pixel)")
