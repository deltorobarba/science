"""Der Schatten von M 87* aus den öffentlichen EHT-Daten: Visibilities, Closure-Phasen, Ringdurchmesser, Dirty Image, CLEAN und die Masse des schwarzen Lochs.

Für galaxies.ipynb aus galaxies_m87.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: visibilities, closure_phases, ring_diameter, dirty_map, clean, point_sources, mass.
Downloads und Cache: data/galaxies/ (`galdata.py`).
"""
import galdata                                        # zuerst: Cache-Ordner für astropy
import urllib.request
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.special import j0
from astropy.io import fits


def visibilities():
    """31. Die Visibilities (Zellen 4, 6 von galaxies_m87.ipynb)."""
    global ASTRODATA, C, DAYS, EHT_FILES, EHT_URL, G, MPC, MSUN, REFRESH, STATIONS, UAS, axes
    global bl, d, eht, fig, fname, freq, g, grp, hdul, n_bl, names, ok
    global path, pts, rows, s1, s2, short, vis, w, wsum
    ASTRODATA = galdata.DATA
    (ASTRODATA / "eht").mkdir(parents=True, exist_ok=True)
    REFRESH = False                      # True: Dateien neu laden
    EHT_URL = "https://raw.githubusercontent.com/eventhorizontelescope/2019-D01-01/master/uvfits/"
    DAYS = {"095": "5. April", "096": "6. April", "100": "10. April", "101": "11. April"}
    EHT_FILES = [f"SR1_M87_2017_{day}_{band}_hops_netcal_StokesI.uvfits" for day in DAYS for band in ["lo", "hi"]]
    STATIONS = {"AA": "ALMA (Chile)", "AP": "APEX (Chile)", "AZ": "SMT (Arizona)", "JC": "JCMT (Hawaii)",
                "LM": "LMT (Mexiko)", "PV": "IRAM 30 m (Spanien)", "SM": "SMA (Hawaii)"}
    UAS = np.pi / 180 / 3600e6           # 1 Mikrobogensekunde in Radiant
    G, C, MSUN, MPC = 6.674e-11, 2.998e8, 1.989e30, 3.0857e22
    pd.set_option("display.width", 160)

    rows = []
    for fname in EHT_FILES:
        path = ASTRODATA / "eht" / fname
        if REFRESH or not path.exists():
            urllib.request.urlretrieve(EHT_URL + fname, path)
        with fits.open(path) as hdul:
            grp = hdul[0]
            freq = grp.header["CRVAL4"]
            names = [n.strip() for n in hdul["AIPS AN"].data["ANNAME"]]
            d = grp.data.data[:, 0, 0, 0, 0, :2, :]                  # RR und LL, je [Realteil, Imaginärteil, Gewicht]
            w = np.clip(d[..., 2], 0, None)
            wsum = w.sum(axis=1)
            ok = wsum > 0
            vis = ((d[..., 0] + 1j * d[..., 1]) * w).sum(axis=1)[ok] / wsum[ok]   # gewichtetes Mittel = Stokes I
            bl = grp.data.par("BASELINE").astype(int)[ok]
            rows.append(pd.DataFrame({"day": fname[13:16], "band": fname[17:19],
                                      "u": grp.data.par("UU---SIN")[ok] * freq, "v": grp.data.par("VV---SIN")[ok] * freq,
                                      "vis": vis, "sigma": 1 / np.sqrt(wsum[ok]), "time": grp.data.par("DATE")[ok],
                                      "st1": [names[a - 1] for a in bl // 256], "st2": [names[a - 1] for a in bl % 256]}))
    eht = pd.concat(rows, ignore_index=True)
    eht["rho"] = np.hypot(eht["u"], eht["v"])
    eht["amp"] = np.abs(eht["vis"])
    n_bl = eht[["st1", "st2"]].drop_duplicates().shape[0]
    print(f"{len(eht):,} Visibilities, {n_bl} Basislinien zwischen {len(set(eht.st1) | set(eht.st2))} Stationen")
    print("Pro Nacht:", {DAYS[k]: v for k, v in eht.groupby("day").size().items()})
    print(f"Längste Basislinie {eht['rho'].max() / 1e9:.2f} Gλ -> Auflösung λ/B ≈ {1 / eht['rho'].max() / UAS:.0f} µas")
    short = eht.groupby(["st1", "st2"])["rho"].max().sort_values()
    print("Kürzeste Basislinien:", ", ".join(f"{a}-{b} {r / 1e6:.1f} Mλ" for (a, b), r in short.head(2).items()),
          "(innerhalb eines Standorts)")
    print(f"Amplituden: auf kurzen Basislinien (< 0.1 Gλ) im Median {eht.loc[eht['rho'] < 1e8, 'amp'].median():.2f} Jy, "
          f"auf langen (> 1 Gλ) {eht.loc[eht['rho'] > 1e9, 'amp'].median():.2f} Jy")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    for (s1, s2), g in eht.groupby(["st1", "st2"]):
        pts = axes[0].plot(g["u"] / 1e9, g["v"] / 1e9, ".", ms=1.5, label=f"{s1}-{s2}")
        axes[0].plot(-g["u"] / 1e9, -g["v"] / 1e9, ".", ms=1.5, c=pts[0].get_color())
    axes[0].set_aspect("equal")
    axes[0].invert_xaxis()
    axes[0].set_xlabel("u [Gλ]")
    axes[0].set_ylabel("v [Gλ]")
    axes[0].set_title("(u,v)-Abdeckung des EHT 2017 (mit gespiegelten Punkten)", fontsize=10)
    axes[0].legend(fontsize=6, ncol=3, markerscale=5, loc="lower left")
    axes[1].scatter(eht["rho"] / 1e9, eht["amp"], s=1, c="grey", alpha=0.3)
    axes[1].set_ylim(0, 1.4)
    axes[1].set_xlabel("Länge der Basislinie ρ [Gλ]")
    axes[1].set_ylabel("|V| [Jy]")
    axes[1].set_title("M 87*: Amplitude gegen Länge der Basislinie", fontsize=10)
    fig.tight_layout()
    plt.show()


def closure_phases():
    """32. Phasen und Closure-Phasen (Zellen 9 von galaxies_m87.ipynb)."""
    global BAND, DAY, TRI, a, ax, b, c, circ_stats, cl_all, closure, cm, common
    global day, fig, hours, label, mean, ph, phase_ab, series, std, sub, v_ab, v_ac
    global v_bc, x, y, z
    DAY, BAND, TRI = "095", "lo", ("AA", "AZ", "LM")      # ALMA, SMT, LMT

    def circ_stats(phase_deg):
        # Mittelwert und Streuung für Winkel: über Einheitszeiger mitteln
        z = np.mean(np.exp(1j * np.deg2rad(phase_deg)))
        return np.rad2deg(np.angle(z)), np.rad2deg(np.sqrt(-2 * np.log(np.abs(z))))

    sub = eht[(eht["day"] == DAY) & (eht["band"] == BAND)].copy()
    sub["t"] = np.round((sub["time"] - sub["time"].min()) * 86400).astype(int)       # Sekunden seit Beginn
    def series(a, b):
        s = sub[(sub["st1"] == a) & (sub["st2"] == b)].set_index("t")["vis"]
        return s[~s.index.duplicated()]
    a, b, c = TRI
    v_ab, v_bc, v_ac = series(a, b), series(b, c), series(a, c)
    common = v_ab.index.intersection(v_bc.index).intersection(v_ac.index)
    closure = np.angle(v_ab[common] * v_bc[common] * np.conj(v_ac[common]), deg=True)   # φ_ab + φ_bc + φ_ca
    phase_ab = np.angle(v_ab[common], deg=True)

    print(f"Dreieck {'-'.join(TRI)} am {DAYS[DAY]}, Band {BAND}: {len(common)} gemeinsame Zeitpunkte")
    for label, ph in [(f"Phase {a}-{b}", phase_ab), (f"Phase {b}-{c}", np.angle(v_bc[common], deg=True)),
                      (f"Phase {a}-{c}", np.angle(v_ac[common], deg=True)), ("Closure-Phase", closure)]:
        mean, std = circ_stats(ph)
        print(f"  {label:16s} Mittel {mean:+7.1f}°, zirkuläre Streuung {std:6.1f}°")
    cl_all = {}
    for day in DAYS:
        sub = eht[(eht["day"] == day) & (eht["band"] == BAND)].copy()
        sub["t"] = np.round((sub["time"] - sub["time"].min()) * 86400).astype(int)
        x, y, z = series(a, b), series(b, c), series(a, c)
        cm = x.index.intersection(y.index).intersection(z.index)
        cl_all[day] = circ_stats(np.angle(x[cm] * y[cm] * np.conj(z[cm]), deg=True)) + (len(cm),)
    print("Closure-Phase in allen Nächten:", ", ".join(f"{DAYS[k]}: {m:+.0f}° ± {s:.0f}° ({n})" for k, (m, s, n) in cl_all.items()))

    hours = np.asarray(common) / 3600
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(hours, phase_ab, ".", ms=3, c="tab:blue", label=f"Phase der Basislinie {a}-{b}")
    ax.plot(hours, closure, ".", ms=3, c="tab:red", label=f"Closure-Phase {'-'.join(TRI)}")
    ax.axhline(0, color="black", lw=0.6)
    ax.set_ylim(-180, 180)
    ax.set_yticks(range(-180, 181, 90))
    ax.set_xlabel(f"Zeit seit Beginn der Beobachtung am {DAYS[DAY]} [h]")
    ax.set_ylabel("Phase [°]")
    ax.set_title("Die Stationsfehler heben sich in der Closure-Phase heraus", fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()


def ring_diameter():
    """33. Der Ringdurchmesser aus den Amplituden (Zellen 12 von galaxies_m87.ipynb)."""
    global F_ring, ax, c_ring, d_days, d_ring, day, fig, fit_ring, long_bl, p, p_ring, per_day
    global rho_null, ring_amp, rr, w_ring
    def ring_amp(rho, F, d_uas, w_uas):
        return F * np.abs(j0(np.pi * d_uas * UAS * rho)) * np.exp(-(np.pi * w_uas * UAS * rho) ** 2 / (4 * np.log(2)))

    def fit_ring(df):
        sig = df["sigma"] + 0.05 * df["amp"]               # 5 % systematischer Fehler der Amplitudeneichung
        p, cov = curve_fit(ring_amp, df["rho"], df["amp"], p0=[0.6, 40, 10], sigma=sig, bounds=([0, 10, 0], [3, 100, 60]))
        return p, cov

    long_bl = eht["rho"] > 1e9
    p_ring, c_ring = fit_ring(eht[long_bl])
    F_ring, d_ring, w_ring = p_ring
    rho_null = 2.405 / (np.pi * d_ring * UAS)                # erste Nullstelle von J0
    per_day = {day: fit_ring(eht[long_bl & (eht["day"] == day)])[0] for day in DAYS}
    d_days = np.array([p[1] for p in per_day.values()])

    print(f"Ringfit an {long_bl.sum():,} Amplituden auf Basislinien über 1 Gλ")
    print(f"  Durchmesser d = {d_ring:.1f} µas (formaler Fehler ± {np.sqrt(c_ring[1, 1]):.2f}), Breite w = {w_ring:.1f} µas, "
          f"kompakter Fluss F = {F_ring:.2f} Jy")
    print(f"  Erste Nullstelle der Amplitude bei {rho_null / 1e9:.2f} Gλ")
    for day, p in per_day.items():
        print(f"  {DAYS[day]:>10s}: d = {p[1]:.1f} µas, w = {p[2]:.1f} µas, F = {p[0]:.2f} Jy")
    print(f"  Streuung zwischen den Nächten: ± {d_days.std(ddof=1):.1f} µas")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.scatter(eht["rho"] / 1e9, eht["amp"], s=1, c="grey", alpha=0.3, label="Amplituden")
    rr = np.linspace(0.01, 9e9, 500)
    ax.plot(rr / 1e9, ring_amp(rr, *p_ring), c="tab:red", lw=2, label=f"Ringmodell: d = {d_ring:.1f} µas, w = {w_ring:.1f} µas")
    ax.axvline(rho_null / 1e9, color="tab:red", ls="--", lw=1, label=f"erste Nullstelle {rho_null / 1e9:.2f} Gλ")
    ax.axvline(1, color="black", lw=0.6, ls=":")
    ax.set_ylim(0, 0.8)
    ax.set_xlabel("Länge der Basislinie ρ [Gλ]")
    ax.set_ylabel("|V| [Jy]")
    ax.set_title("M 87*: Ringmodell an die Amplituden", fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()


def dirty_map():
    """34. Dirty Beam und Dirty Image (Zellen 15 von galaxies_m87.ipynb)."""
    global BEAM2, EX, EY, FOV_UAS, N_PIX, PIX_UAS, axes, dirty_beam, dirty_image, ext, fig, lm
    global lm2, ring_dirty, ring_src, show, side, sky_visibilities, uv
    eht["tbin"] = np.floor((eht["time"] - eht["time"].min()) * 24 * 6)        # 10-Minuten-Intervalle
    uv = eht.groupby(["day", "st1", "st2", "tbin"])[["u", "v"]].mean().to_numpy()
    uv = np.vstack([uv, -uv])
    N_PIX, FOV_UAS = 64, 160
    PIX_UAS = FOV_UAS / N_PIX
    lm = (np.arange(N_PIX) - N_PIX // 2) * PIX_UAS * UAS
    EX = np.exp(2j * np.pi * np.outer(lm, uv[:, 0]))                          # Spalten: l (Osten)
    EY = np.exp(2j * np.pi * np.outer(lm, uv[:, 1]))                          # Zeilen: m (Norden)

    def sky_visibilities(sources):
        # Visibilities von Punktquellen [(Fluss, l_µas, m_µas), ...] an den EHT-Punkten
        return sum(F * np.exp(-2j * np.pi * (uv[:, 0] * l + uv[:, 1] * m) * UAS) for F, l, m in sources)

    def dirty_image(vis):
        return ((EY * vis) @ EX.T).real / len(vis)                            # Rücktransformation an den gemessenen Punkten

    # Dirty Beam auf einem doppelt so großen Raster, damit er beim CLEAN an jedes Pixel verschoben werden kann
    lm2 = (np.arange(2 * N_PIX) - N_PIX) * PIX_UAS * UAS
    BEAM2 = (np.exp(2j * np.pi * np.outer(lm2, uv[:, 1])) @ np.exp(2j * np.pi * np.outer(lm2, uv[:, 0])).T).real / len(uv)
    dirty_beam = BEAM2[N_PIX // 2:3 * N_PIX // 2, N_PIX // 2:3 * N_PIX // 2]
    side = np.abs(dirty_beam[np.hypot(*np.mgrid[-N_PIX // 2:N_PIX // 2, -N_PIX // 2:N_PIX // 2]) * PIX_UAS > 25]).max()

    ring_src = [(F_ring / 72, d_ring / 2 * np.cos(t), d_ring / 2 * np.sin(t)) for t in np.linspace(0, 2 * np.pi, 72, endpoint=False)]
    ring_dirty = dirty_image(sky_visibilities(ring_src))
    print(f"{len(uv) // 2} gemittelte (u,v)-Punkte (dazu die gespiegelten), Bild {N_PIX} x {N_PIX} Pixel zu {PIX_UAS:.1f} µas")
    print(f"Höchste Nebenkeule des Dirty Beam außerhalb von 25 µas: {side:.0%} der Hauptkeule")

    ext = [(-N_PIX // 2 - 0.5) * PIX_UAS, (N_PIX // 2 - 0.5) * PIX_UAS] * 2           # Pixelmitten auf den Koordinaten lm
    def show(ax, img, title, cmap="afmhot"):
        ax.imshow(img, origin="lower", cmap=cmap, extent=ext)
        ax.invert_xaxis()                                                     # Osten links
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("Δα [µas]")
        ax.set_ylabel("Δδ [µas]")

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    show(axes[0], dirty_beam, "Dirty Beam (EHT-Abdeckung 2017)", "viridis")
    show(axes[1], ring_dirty, f"Dirty Image eines Rings von {d_ring:.0f} µas")
    axes[1].add_patch(plt.Circle((0, 0), d_ring / 2, fill=False, ec="cyan", ls="--", lw=0.8))
    fig.tight_layout()
    plt.show()


def clean():
    """35. CLEAN (Zellen 18 von galaxies_m87.ipynb)."""
    global K_EX, NOISE, _, ax, axes, centre_ratio, fig, hogbom_clean, img, noisy, pix_to_uas, pk
    global r_pix, random_sky, ring_comps, ring_restored, rng, sp_comps, sp_dirty, sp_res, sp_restored, sparse_sky, title, top_k_peaks
    global xx_, yy_
    def hogbom_clean(dirty, gain=0.1, n_iter=1000, threshold=0.02):
        # hellstes Restpixel suchen, Komponente speichern, verschobenen Dirty Beam abziehen
        res, comps = dirty.copy(), np.zeros_like(dirty)
        for _ in range(n_iter):
            iy, ix = np.unravel_index(np.argmax(res), res.shape)
            if res[iy, ix] < threshold * dirty.max():
                break
            comps[iy, ix] += gain * res[iy, ix]
            res -= gain * res[iy, ix] * BEAM2[N_PIX - iy:2 * N_PIX - iy, N_PIX - ix:2 * N_PIX - ix]
        fwhm_pix = 1 / eht["rho"].max() / UAS / PIX_UAS                     # Restaurierungsstrahl ≈ λ/B_max
        yy_, xx_ = np.mgrid[:N_PIX, :N_PIX] - N_PIX // 2
        clean_beam = np.exp(-4 * np.log(2) * (xx_ ** 2 + yy_ ** 2) / fwhm_pix ** 2)
        restored = np.real(np.fft.ifft2(np.fft.fft2(comps) * np.fft.fft2(np.fft.ifftshift(clean_beam)))) + res
        return comps, res, restored

    def top_k_peaks(img, k, min_sep_pix=4):
        # Orte der k hellsten lokalen Maxima (gierig, mit Mindestabstand)
        work, peaks = img.copy(), []
        for _ in range(k):
            iy, ix = np.unravel_index(np.argmax(work), work.shape)
            peaks.append((ix, iy))
            work[max(iy - min_sep_pix, 0):iy + min_sep_pix + 1, max(ix - min_sep_pix, 0):ix + min_sep_pix + 1] = -np.inf
        return np.array(peaks)

    def pix_to_uas(p):
        return (p - N_PIX // 2) * PIX_UAS

    rng = np.random.default_rng(11)
    K_EX, NOISE = 5, 0.02
    def random_sky(k):
        return [(rng.uniform(0.5, 1.0), rng.uniform(-60, 60), rng.uniform(-60, 60)) for _ in range(k)]
    def noisy(vis):
        n = NOISE * (rng.normal(size=len(vis) // 2) + 1j * rng.normal(size=len(vis) // 2))
        return vis + np.r_[n, np.conj(n)]                                      # Rauschen hermitesch, damit das Bild reell bleibt

    ring_comps, _, ring_restored = hogbom_clean(ring_dirty)
    sparse_sky = random_sky(K_EX)
    sp_dirty = dirty_image(noisy(sky_visibilities(sparse_sky)))
    sp_comps, sp_res, sp_restored = hogbom_clean(sp_dirty)
    yy_, xx_ = np.mgrid[:N_PIX, :N_PIX] - N_PIX // 2
    r_pix = np.hypot(xx_, yy_) * PIX_UAS
    centre_ratio = ring_restored[r_pix < 5].mean() / ring_restored[np.abs(r_pix - d_ring / 2) < 3].mean()
    print(f"Ring: {np.count_nonzero(ring_comps)} CLEAN-Komponenten; Helligkeit in der Mitte / auf dem Ring = {centre_ratio:.2f}")
    print(f"Punktquellen: {np.count_nonzero(sp_comps)} Komponenten, Rest im Restbild {np.abs(sp_res).max() / sp_dirty.max():.1%} des Dirty-Maximums")

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    show(axes[0], ring_restored, "Ring nach CLEAN")
    axes[0].add_patch(plt.Circle((0, 0), d_ring / 2, fill=False, ec="cyan", ls="--", lw=0.8))
    for ax, img, title in [(axes[1], sp_dirty, f"Dirty Image: {K_EX} Punktquellen mit Rauschen"),
                           (axes[2], sp_restored, "nach CLEAN")]:
        show(ax, img, title)
        ax.scatter([l for _, l, _ in sparse_sky], [m for _, _, m in sparse_sky], marker="+", s=120, c="cyan", label="wahre Quellen")
        pk = top_k_peaks(img, K_EX)
        ax.scatter(pix_to_uas(pk[:, 0]), pix_to_uas(pk[:, 1]), marker="o", s=80, facecolors="none", edgecolors="lime",
                   label=f"die {K_EX} hellsten Maxima")
        ax.legend(fontsize=7, loc="lower left")
    fig.tight_layout()
    plt.show()


def point_sources():
    """36. Wie viele Punktquellen findet man wieder? (Zellen 21 von galaxies_m87.ipynb)."""
    global K_LIST, N_TRIALS, _, ax, dimg, e_, ec, ed, fig, k, key, label
    global m_, mk, r_c, r_d, rc, rd, rec, recall, s
    def recall(sources, img, tol_uas=8):
        # Anteil der wahren Quellen, neben denen eines der k hellsten Maxima liegt
        truth = np.array([(l, m) for _, l, m in sources])
        found = pix_to_uas(top_k_peaks(img, len(sources)))
        d = np.hypot(truth[:, None, 0] - found[None, :, 0], truth[:, None, 1] - found[None, :, 1])
        return np.mean(d.min(axis=1) < tol_uas)

    K_LIST, N_TRIALS = [1, 2, 3, 5, 8, 12], 30
    rec = {"dirty": [], "clean": []}
    for k in K_LIST:
        r_d, r_c = [], []
        for _ in range(N_TRIALS):
            s = random_sky(k)
            dimg = dirty_image(noisy(sky_visibilities(s)))
            r_d.append(recall(s, dimg))
            r_c.append(recall(s, hogbom_clean(dimg)[2]))
        rec["dirty"].append((np.mean(r_d), np.std(r_d) / np.sqrt(N_TRIALS)))
        rec["clean"].append((np.mean(r_c), np.std(r_c) / np.sqrt(N_TRIALS)))
    print(f"Trefferquote (Abstand unter 8 µas), {N_TRIALS} zufällige Himmel pro k, Rauschen {NOISE} Jy pro Visibility")
    for k, (rd, ed), (rc, ec) in zip(K_LIST, rec["dirty"], rec["clean"]):
        print(f"  k = {k:2d}:  Dirty Image {rd:.2f} ± {ed:.2f}   |   nach CLEAN {rc:.2f} ± {ec:.2f}")

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for key, mk, label in [("dirty", "o--", "k hellste Maxima des Dirty Image"), ("clean", "s-", "k hellste Maxima nach CLEAN")]:
        m_, e_ = np.array(rec[key]).T
        ax.errorbar(K_LIST, m_, e_, fmt=mk, capsize=3, label=label)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Zahl der Punktquellen k")
    ax.set_ylabel("Trefferquote")
    ax.set_title(f"Wiederfinden von Punktquellen mit der EHT-Abdeckung ({N_TRIALS} Himmel pro k)", fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()


def mass():
    """37. Durchmesser und Masse im Vergleich (Zellen 24 von galaxies_m87.ipynb)."""
    global D_M87, _, alpha_eht, ax, d_err, fig, j, label, m, m_err, m_own, m_shadow
    global masses, quote, theta_g
    D_M87 = 16.8                                     # Mpc, wie in EHT Collaboration (2019)
    def theta_g(m_sun, d_mpc=D_M87):
        return G * m_sun * MSUN / C ** 2 / (d_mpc * MPC) / UAS          # µas

    alpha_eht = 42 / theta_g(6.5e9)                  # Verhältnis Ring / θ_g im veröffentlichten Ergebnis
    d_err = d_days.std(ddof=1)
    m_own = d_ring / alpha_eht / theta_g(1.0)
    m_err = m_own * d_err / d_ring
    m_shadow = d_ring / (2 * np.sqrt(27)) / theta_g(1.0)               # falls der Ring genau der Schatten wäre

    masses = [("EHT Collaboration (2019), Ring", 6.5e9, "6.5 ± 0.7"),
              ("Sterne (Gebhardt et al. 2011)", 6.6e9 * D_M87 / 17.9, "6.6 ± 0.4 bei 17.9 Mpc"),
              ("Gas (Walsh et al. 2013)", 3.5e9 * D_M87 / 17.9, "3.5 (+0.9/−0.3) bei 17.9 Mpc")]
    print(f"Ringdurchmesser: eigen {d_ring:.1f} ± {d_err:.1f} µas (Streuung der Nächte), EHT Collaboration (2019): 42 ± 3 µas")
    print(f"θ_g für 6.5·10⁹ M_sun bei {D_M87} Mpc: {theta_g(6.5e9):.2f} µas; veröffentlichtes Verhältnis d / θ_g = {alpha_eht:.1f}, "
          f"Schatten allein 2√27 = {2 * np.sqrt(27):.1f}")
    print(f"Eigene Masse mit d / θ_g = {alpha_eht:.1f}: ({m_own / 1e9:.2f} ± {m_err / 1e9:.2f})·10⁹ M_sun (nur Streuung der Nächte); "
          f"wäre der Ring der Schatten selbst: {m_shadow / 1e9:.1f}·10⁹ M_sun")
    print("\nVorhergesagter Ringdurchmesser für die veröffentlichten Massen (umgerechnet auf 16.8 Mpc):")
    for label, m, quote in masses:
        print(f"  {label:32s} M = {m / 1e9:.1f}·10⁹ M_sun ({quote})  ->  d = {alpha_eht * theta_g(m):.0f} µas")

    fig, ax = plt.subplots(figsize=(10, 3.2))
    for j, (label, m, _) in enumerate(masses):
        ax.plot(alpha_eht * theta_g(m), j, "s", ms=8, c="black")
    ax.errorbar(42, 0, xerr=3, fmt="none", c="black", capsize=4)
    ax.axvline(d_ring, color="tab:red", label=f"eigene Messung {d_ring:.1f} µas")
    ax.set_yticks(range(len(masses)), [f"{label}: {m / 1e9:.1f}·10⁹ M_sun" for label, m, _ in masses], fontsize=8)
    ax.set_ylim(-0.6, len(masses) - 0.4)
    ax.set_xlabel("erwarteter Ringdurchmesser d = 11.0 θ_g [µas]")
    ax.set_title("Erwarteter Ring für die veröffentlichten Massen gegen den gemessenen Ring", fontsize=10)
    ax.legend(fontsize=8, loc="center left")
    fig.tight_layout()
    plt.show()
