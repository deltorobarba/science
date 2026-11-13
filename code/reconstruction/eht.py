"""Event Horizon Telescope für reconstruction.ipynb: echte (u,v)-Abdeckung von M 87* und Bilder aus wenigen Fourier-Punkten.

Daten: die öffentlichen, kalibrierten Visibilities der EHT-Kollaboration von 2017 (Datensatz 2019-D01-01 auf GitHub,
M 87* am 5., 6., 10. und 11. April, Bänder um 227 und 229 GHz, Stokes I, acht UVFITS-Dateien, zusammen etwa 4 MB).
Das Modul lädt sie mit Cache, passt ein Ringmodell an die Amplituden an, baut den Fourier-Operator der Abdeckung
(Bild → Visibilities und zurück) und rekonstruiert simulierte Bilder mit Dirty Image, Högbom-CLEAN und ℓ1 (FISTA aus
sensing.py). Die Simulation nimmt perfekte Phasen an; die echten Phasen verfälscht die Atmosphäre.
"""
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy.io import fits
from scipy.optimize import curve_fit
from scipy.special import j0

import sensing

URLS = ["https://raw.githubusercontent.com/eventhorizontelescope/2019-D01-01/master/uvfits/",
        "https://github.com/eventhorizontelescope/2019-D01-01/raw/master/uvfits/"]
DAYS = {"095": "5. April", "096": "6. April", "100": "10. April", "101": "11. April"}
FILES = [f"SR1_M87_2017_{day}_{band}_hops_netcal_StokesI.uvfits" for day in DAYS for band in ["lo", "hi"]]
STATIONS = {"AA": "ALMA", "AP": "APEX", "AZ": "SMT", "JC": "JCMT", "LM": "LMT", "PV": "IRAM 30 m", "SM": "SMA"}
SITES = {"Chile": ["AA", "AP"], "Arizona": ["AZ"], "Hawaii": ["JC", "SM"], "Mexiko": ["LM"], "Spanien": ["PV"]}
UAS = np.pi / 180 / 3600e6                       # eine Mikrobogensekunde in Radiant


def _zahl(n):
    """Ganze Zahl mit Leerzeichen als Tausendertrenner (51 119)."""
    return f"{n:,}".replace(",", " ")


def _download(fname, path, tries=3):
    for url in URLS:
        for i in range(tries):
            try:
                urllib.request.urlretrieve(url + fname, path)
                with open(path, "rb") as f:
                    if f.read(6) == b"SIMPLE":          # FITS-Datei, keine HTML-Fehlerseite
                        return True
            except Exception:
                pass
            time.sleep(2 * (i + 1))
    path.unlink(missing_ok=True)
    print(f"  {fname}: Download fehlgeschlagen")
    return False


def load(cache):
    """Alle acht Dateien laden (Cache in `cache`), Stokes I als gewichtetes Mittel von RR und LL; u, v in Wellenlängen."""
    cache = Path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    rows = []
    for fname in FILES:
        path = cache / fname
        if not path.exists() and not _download(fname, path):
            continue
        with fits.open(path) as hdul:
            grp = hdul[0]
            freq = grp.header["CRVAL4"]
            names = [n.strip() for n in hdul["AIPS AN"].data["ANNAME"]]
            d = grp.data.data[:, 0, 0, 0, 0, :2, :]           # RR und LL, je [Realteil, Imaginärteil, Gewicht]
            w = np.clip(d[..., 2], 0, None)
            wsum = w.sum(axis=1)
            ok = wsum > 0
            vis = ((d[..., 0] + 1j * d[..., 1]) * w).sum(axis=1)[ok] / wsum[ok]
            bl = grp.data.par("BASELINE").astype(int)[ok]
            rows.append(pd.DataFrame({"day": fname[13:16], "band": fname[17:19],
                                      "u": grp.data.par("UU---SIN")[ok] * freq, "v": grp.data.par("VV---SIN")[ok] * freq,
                                      "vis": vis, "sigma": 1 / np.sqrt(wsum[ok]), "time": grp.data.par("DATE")[ok],
                                      "st1": [names[a - 1] for a in bl // 256], "st2": [names[a - 1] for a in bl % 256]}))
    df = pd.concat(rows, ignore_index=True)
    df["rho"] = np.hypot(df["u"], df["v"])
    df["amp"] = np.abs(df["vis"])
    n_bl = df[["st1", "st2"]].drop_duplicates().shape[0]
    print(f"{_zahl(len(df))} Visibilities aus {len(rows)} Dateien, {n_bl} Basislinien zwischen "
          f"{len(set(df.st1) | set(df.st2))} Stationen")
    print(f"Längste Basislinie {df['rho'].max() / 1e9:.2f} Gλ, also Auflösung λ/B ≈ {1 / df['rho'].max() / UAS:.0f} µas")
    return df


def ring_amp(rho, F, d_uas, w_uas):
    """Amplitude eines dünnen Rings (Fluss F, Durchmesser d), mit einem Gauß der Breite w verschmiert."""
    return F * np.abs(j0(np.pi * d_uas * UAS * rho)) * np.exp(-(np.pi * w_uas * UAS * rho) ** 2 / (4 * np.log(2)))


def fit_ring(df, rho_min=1e9):
    """Ringmodell an die Amplituden auf Basislinien über rho_min (kürzere sehen auch den Jet); 5 % Eichfehler dazu."""
    sub = df[df["rho"] > rho_min]
    p, cov = curve_fit(ring_amp, sub["rho"], sub["amp"], p0=[0.6, 40, 10], sigma=sub["sigma"] + 0.05 * sub["amp"],
                       bounds=([0, 10, 0], [3, 100, 60]))
    fit = {"F": p[0], "d": p[1], "w": p[2], "d_err": np.sqrt(cov[1, 1]), "null": 2.405 / (np.pi * p[1] * UAS), "n": len(sub)}
    print(f"Ringmodell an {_zahl(fit['n'])} Amplituden: Durchmesser {fit['d']:.1f} µas, Breite {fit['w']:.1f} µas, "
          f"Fluss {fit['F']:.2f} Jy; erste Nullstelle bei {fit['null'] / 1e9:.2f} Gλ")
    return fit


def plot_data(df, fit):
    """Links die (u,v)-Abdeckung mit gespiegelten Punkten, rechts die Amplituden mit dem Ringmodell."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    for (s1, s2), g in df.groupby(["st1", "st2"]):
        pts = axes[0].plot(g["u"] / 1e9, g["v"] / 1e9, ".", ms=1.5, label=f"{s1}-{s2}")
        axes[0].plot(-g["u"] / 1e9, -g["v"] / 1e9, ".", ms=1.5, c=pts[0].get_color())
    axes[0].set_aspect("equal")
    axes[0].invert_xaxis()
    axes[0].set_xlabel("u [Gλ]")
    axes[0].set_ylabel("v [Gλ]")
    axes[0].set_title("Gemessene Punkte der Fourier-Ebene (EHT 2017, vier Nächte)", fontsize=10)
    axes[0].legend(fontsize=6, ncol=3, markerscale=5, loc="lower left")
    axes[1].scatter(df["rho"] / 1e9, df["amp"], s=1, c="grey", alpha=0.3, label="gemessene Amplituden")
    rr = np.linspace(0.01, 9e9, 500)
    axes[1].plot(rr / 1e9, ring_amp(rr, fit["F"], fit["d"], fit["w"]), c="tab:red", lw=2,
                 label=f"Ringmodell, Durchmesser {fit['d']:.1f} µas")
    axes[1].axvline(fit["null"] / 1e9, color="tab:red", ls="--", lw=1, label=f"erste Nullstelle {fit['null'] / 1e9:.2f} Gλ")
    axes[1].set_ylim(0, 0.8)
    axes[1].set_xlabel("Länge der Basislinie ρ [Gλ]")
    axes[1].set_ylabel("Amplitude |V| [Jy]")
    axes[1].set_title("M 87*: Amplitude gegen Länge der Basislinie", fontsize=10)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()


def _baseline(sub, a, b):
    """Visibilities einer Basislinie a-b als Zeitreihe (Sekunden); liegt sie als b-a vor, konjugiert."""
    s = sub[(sub["st1"] == a) & (sub["st2"] == b)].set_index("t")["vis"]
    if len(s) == 0:
        s = np.conj(sub[(sub["st1"] == b) & (sub["st2"] == a)].set_index("t")["vis"])
    return s[~s.index.duplicated()]


def circular(deg):
    """Mittelwert und Streuung von Winkeln über Einheitszeiger (359° und 1° liegen nah beieinander)."""
    z = np.mean(np.exp(1j * np.deg2rad(deg)))
    return float(np.rad2deg(np.angle(z))), float(np.rad2deg(np.sqrt(-2 * np.log(np.abs(z)))))


def plot_closure(df, triangle=("AA", "AZ", "LM"), band="lo"):
    """Phase einer Basislinie gegen die Closure-Phase eines Dreiecks, in allen Nächten.

    Closure-Phase = Phase(a-b) + Phase(b-c) − Phase(a-c): Der Phasenfehler jeder Station (Atmosphäre, Uhr) kommt
    einmal mit Plus und einmal mit Minus vor und fällt heraus; übrig bleibt eine Eigenschaft der Quelle.
    """
    a, b, c = triangle
    nights = {}
    for day in DAYS:
        sub = df[(df["day"] == day) & (df["band"] == band)].copy()
        sub["t"] = np.round((sub["time"] - sub["time"].min()) * 86400).astype(int)
        ab, bc, ac = _baseline(sub, a, b), _baseline(sub, b, c), _baseline(sub, a, c)
        common = ab.index.intersection(bc.index).intersection(ac.index)
        if len(common) == 0:
            continue
        nights[day] = dict(t=np.asarray(common) / 3600, phase=np.angle(ab[common], deg=True),
                           closure=np.angle(ab[common] * bc[common] * np.conj(ac[common]), deg=True))
    names = "–".join(STATIONS[s] for s in triangle)
    print(f"Dreieck {names}, Band {band}: Phase der Basislinie {STATIONS[a]}–{STATIONS[b]} gegen Closure-Phase")
    for day, d in nights.items():
        pm, ps = circular(d["phase"])
        cm, cs = circular(d["closure"])
        print(f"  {DAYS[day]:>10s} ({len(d['t'])} Zeitpunkte): Phase {pm:+6.1f}° ± {ps:5.1f}°,  Closure-Phase {cm:+5.1f}° ± {cs:4.1f}°")
    first = next(iter(nights))
    d = nights[first]
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(d["t"], d["phase"], ".", ms=3, color="tab:blue", label=f"Phase der Basislinie {STATIONS[a]}–{STATIONS[b]}")
    ax.plot(d["t"], d["closure"], ".", ms=3, color="tab:red", label=f"Closure-Phase {names}")
    ax.axhline(0, color="black", lw=0.6)
    ax.set_ylim(-180, 180)
    ax.set_yticks(range(-180, 181, 90))
    ax.set_xlabel(f"Zeit seit Beginn der Beobachtung am {DAYS[first]} [h]")
    ax.set_ylabel("Phase [°]")
    ax.set_title("Die Fehler der Stationen heben sich in der Closure-Phase heraus", fontsize=10)
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    plt.show()
    return nights


def coverage(df, minutes=10):
    """(u,v)-Punkte je Basislinie und Nacht über `minutes` gemittelt (ohne die gespiegelten), Form (K, 2)."""
    tbin = np.floor((df["time"] - df["time"].min()) * 24 * 60 / minutes)
    return df.assign(tbin=tbin).groupby(["day", "st1", "st2", "tbin"])[["u", "v"]].mean().to_numpy()


class Fourier:
    """Messoperator A der Abdeckung: Bild (n × n Pixel, Jy pro Pixel) → Visibilities an den K Punkten, und zurück."""

    def __init__(self, uv, n_pix=64, pix_uas=2.5):
        self.uv, self.n_pix, self.pix_uas = uv, n_pix, pix_uas
        self.lm = (np.arange(n_pix) - n_pix // 2) * pix_uas * UAS
        self.EX = np.exp(-2j * np.pi * np.outer(self.lm, uv[:, 0]))       # Spalten des Bildes: l (Osten)
        self.EY = np.exp(-2j * np.pi * np.outer(self.lm, uv[:, 1]))       # Zeilen: m (Norden)
        self.extent = [(-n_pix // 2 - 0.5) * pix_uas, (n_pix // 2 - 0.5) * pix_uas] * 2

    def forward(self, img):
        """V_k = Σ I(l, m) · exp(−2πi (u_k l + v_k m)), getrennt in l und m gerechnet."""
        return ((img @ self.EX) * self.EY).sum(axis=0)

    def adjoint(self, vis):
        """Transponierter Operator für reelle Bilder: Re Σ_k V_k · exp(+2πi (u_k l + v_k m))."""
        return ((np.conj(self.EY) * vis) @ np.conj(self.EX).T).real

    def dirty(self, vis):
        """Dirty Image: alle gemessenen Fourier-Punkte zurücktransformiert, fehlende als null; Punktquelle F hat Spitze F."""
        return self.adjoint(vis) / len(vis)

    def beam(self, size=None):
        """Dirty Beam (Bild einer Punktquelle in der Mitte) auf einem Raster mit `size` Pixeln Kantenlänge."""
        size = size or self.n_pix
        lm = (np.arange(size) - size // 2) * self.pix_uas * UAS
        return ((np.exp(2j * np.pi * np.outer(lm, self.uv[:, 1])) @ np.exp(2j * np.pi * np.outer(lm, self.uv[:, 0])).T).real
                / len(self.uv))


def crescent(n_pix=64, pix_uas=2.5, d_uas=42, width_uas=6, flux=0.6, contrast=0.6, pa_deg=180):
    """Ring mit Durchmesser d und Breite width, auf der Seite pa (vom Norden über Osten; 180° = Süden) heller.

    contrast: Helligkeit variiert wie 1 + contrast · cos(Winkel − pa). Gesamtfluss `flux` in Jy.
    """
    y, x = (np.mgrid[:n_pix, :n_pix] - n_pix // 2) * pix_uas            # x nach Osten, y nach Norden
    r, phi = np.hypot(x, y), np.arctan2(x, y)                              # Winkel vom Norden über Osten
    img = np.exp(-0.5 * ((r - d_uas / 2) / (width_uas / 2.355)) ** 2) * (1 + contrast * np.cos(phi - np.deg2rad(pa_deg)))
    return img * flux / img.sum()


def clean(F, vis, gain=0.1, n_iter=2000, threshold=0.02, restore_uas=20):
    """Högbom-CLEAN: immer wieder die hellste Stelle des Restbildes als Punktquelle nehmen und ihren Dirty Beam abziehen.

    Stoppt, wenn das Restbild unter `threshold` × Spitze des Dirty Image fällt. Ergebnis: die Punktquellen, mit einem
    Gauß von `restore_uas` Halbwertsbreite verschmiert (Jy pro Pixel), und die Zahl der Punktquellen.
    """
    n = F.n_pix
    beam2 = F.beam(2 * n)                                   # doppelt so groß, damit er an jedes Pixel verschoben werden kann
    res = F.dirty(vis)
    comps = np.zeros_like(res)
    stop = threshold * res.max()
    for _ in range(n_iter):
        i, j = np.unravel_index(np.argmax(res), res.shape)
        if res[i, j] < stop:
            break
        comps[i, j] += gain * res[i, j]
        res -= gain * res[i, j] * beam2[n - i:2 * n - i, n - j:2 * n - j]
    return blur(comps, F.pix_uas, restore_uas), int((comps > 0).sum())


def blur(img, pix_uas, fwhm_uas):
    """Bild mit einem Gauß der Halbwertsbreite fwhm verschmieren (Fluss bleibt gleich)."""
    n = img.shape[0]
    y, x = (np.mgrid[:n, :n] - n // 2) * pix_uas
    g = np.exp(-0.5 * (x ** 2 + y ** 2) / (fwhm_uas / 2.355) ** 2)
    g /= g.sum()
    return np.real(np.fft.ifft2(np.fft.fft2(img) * np.fft.fft2(np.fft.ifftshift(g))))


def nxcorr(a, b):
    """Normierte Kreuzkorrelation zweier Bilder (1 = gleich bis auf Helligkeit), Maß der EHT-Bildvergleiche."""
    a, b = a - a.mean(), b - b.mean()
    return float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum()))


def reconstruct(F, vis, lam_rel=0.01, n_iter=500):
    """ℓ1 mit Positivität (FISTA): λ relativ zum größten Wert von Aᵀy, damit es nicht von der Zahl der Punkte abhängt."""
    lam = lam_rel * np.abs(F.adjoint(vis)).max()
    img, _ = sensing.fista(F.forward, F.adjoint, vis, (F.n_pix, F.n_pix), lam=lam, n_iter=n_iter, positive=True)
    return img


def compare(df, truth, noise_jy=0.01, lam_rel=0.01, drop=("Chile", "Arizona", "Mexiko"), night="100", seed=0):
    """Ein Modellbild an der echten Abdeckung „messen“ (mit Rauschen) und auf mehrere Arten zurückrechnen.

    Erste Reihe: volle Abdeckung mit Dirty Image, CLEAN und ℓ1. Zweite Reihe: ℓ1 ohne je einen Standort aus `drop`
    und mit nur einer Nacht. Gibt die Bilder zurück und druckt je Bild die Kreuzkorrelation mit dem wahren Bild.
    """
    rng = np.random.default_rng(seed)

    def messen(sub):
        F = Fourier(coverage(sub))
        vis = F.forward(truth)
        return F, vis + noise_jy * (rng.normal(size=len(vis)) + 1j * rng.normal(size=len(vis))) / np.sqrt(2)

    F, vis = messen(df)
    oben = {"wahres Bild": truth, "Dirty Image": F.dirty(vis), "CLEAN (20 µas)": clean(F, vis)[0],
            "ℓ1 + Helligkeit ≥ 0": reconstruct(F, vis, lam_rel)}
    punkte = {"volle Abdeckung": len(vis)}
    unten = {}
    for site in drop:
        sub = df[~df["st1"].isin(SITES[site]) & ~df["st2"].isin(SITES[site])]
        Fs, vs = messen(sub)
        unten[f"ℓ1 ohne {site}"] = reconstruct(Fs, vs, lam_rel)
        punkte[f"ℓ1 ohne {site}"] = len(vs)
    Fn, vn = messen(df[df["day"] == night])
    unten[f"ℓ1, nur {DAYS[night]}"] = reconstruct(Fn, vn, lam_rel)
    punkte[f"ℓ1, nur {DAYS[night]}"] = len(vn)
    print(f"Bild {F.n_pix} × {F.n_pix} = {F.n_pix ** 2} Pixel zu {F.pix_uas} µas; Rauschen {noise_jy * 1000:.0f} mJy je Punkt")
    print("Kreuzkorrelation mit dem wahren Bild (1 = gleich):")
    for name, img in list(oben.items())[1:] + list(unten.items()):
        n = punkte.get(name, punkte["volle Abdeckung"])
        print(f"  {name:24s} {nxcorr(img, truth):.2f}   ({n} gemittelte Fourier-Punkte)")
    print(f"  zum Vergleich: wahres Bild mit 20 µas verschmiert {nxcorr(blur(truth, F.pix_uas, 20), truth):.2f}")
    return F, oben, unten


def plot_images(F, reihen, title):
    """Bilder als Raster (eine Reihe je dict), Osten links, Achsen in µas."""
    ncol = max(len(r) for r in reihen)
    fig, axes = plt.subplots(len(reihen), ncol, figsize=(3.6 * ncol, 4.0 * len(reihen)), squeeze=False)
    for zeile, bilder in zip(axes, reihen):
        for ax, (name, img) in zip(zeile, bilder.items()):
            ax.imshow(img, origin="lower", cmap="afmhot", extent=F.extent)
            ax.invert_xaxis()
            ax.set_title(name, fontsize=10)
            ax.set_xlabel("Δα [µas]")
        zeile[0].set_ylabel("Δδ [µas]")
    fig.suptitle(title, fontsize=11)
    fig.tight_layout(h_pad=2.0)
    plt.show()
