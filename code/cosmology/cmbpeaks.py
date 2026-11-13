"""Die akustischen Peaks der Hintergrundstrahlung aus Planck-Karten: eigenes Leistungsspektrum, Peaks, Schallhorizont, Baryonen und Materie, H0.

Für cosmology.ipynb aus cosmology_cmbpeaks.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, sky_patch, planck_spectrum, beam_noise, point_sources, cosmic_variance, own_spectrum, peaks, peak_spacing, sound_horizon, template, baryons_matter, h0_cmb, literature, what_if_73.
Downloads und Cache: data/cosmology/ (`cosmodata.py`).
"""
import cosmodata                                      # zuerst: Cache-Ordner für astropy
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.cosmology import FlatLambdaCDM
from astropy.io import fits
from scipy import integrate, ndimage, optimize


def load():
    """71. Daten (Zellen 4, 6 von cosmology_cmbpeaks.ipynb)."""
    global ARC_STRETCH, ASTRODATA, BINNED, CMB, C_KMS, DL, DT, EDGES, ERR, FIELDS, FULL, FWHM
    global H0_HD, H0_SH0ES, IRSA, L, LT, MAPS, NEFF_PLANCK, NPIX, OMEGA_G, OMEGA_NU, OM_SN, PEAKS
    global PIX, PIX_HEALPIX, PLANCK, PLANCK_TT, RAW, SIZE, SKYVIEW, THEORY, TROUGHS, WINDOW, _r, acoustic
    global d_theory, download, ell_grid, fill_gaps, fit_extremum, gauss_beam, h2_hu, h3_hu, h_from_theta, m, model, name
    global planck_txt, ref, remove_plane, simulate, skyview, spectrum, taper, transfer, z_star
    ASTRODATA = cosmodata.DATA


    CMB = ASTRODATA / "cmb"
    IRSA = "https://irsa.ipac.caltech.edu/data/Planck/release_3/ancillary-data/cosmoparams/"
    SKYVIEW = "https://skyview.gsfc.nasa.gov/current/cgi/runquery.pl?"
    C_KMS, OMEGA_G, OMEGA_NU = 299792.458, 2.4728e-5, 0.00064   # c [km/s]; ω_γ für 2.7255 K; ω_ν eines Neutrinos mit 0.06 eV
    FIELDS = {"Nordpol": (0, 90), "Südpol": (0, -90), "Nord, l = 150°": (150, 62), "Süd, l = 210°": (210, -62)}
    FWHM = {"100": 9.68, "143": 7.30}            # Strahlbreite der PR3-Karten [′]
    SIZE, NPIX = 20.0, 400                        # Feldgröße [°], Pixel pro Seite → 3′
    PIX = np.radians(SIZE / NPIX)                 # Pixel [rad]
    PIX_HEALPIX = 1.72                            # Pixel der HEALPix-Karten (Nside 2048) [′]
    EDGES = np.arange(40, 2001, 40)               # Grenzen der ℓ-Bins für die eigenen Spektren
    # Planck 2018 VI, Tabelle 2: TT,TE,EE+lowE+lensing und TT+lowE
    PLANCK = dict(wb=(0.02237, 0.00015), wc=(0.1200, 0.0012), wm=(0.1430, 0.0011), H0=(67.36, 0.54), theta=(1.04110, 0.00031),
                  zstar=(1089.92, 0.25), rstar=(144.43, 0.26), ns=(0.9649, 0.0042), Om=(0.3153, 0.0073))
    PLANCK_TT = dict(wb=(0.02212, 0.00022), wm=(0.1434, 0.0020), H0=(66.88, 0.92), theta=(1.04097, 0.00046))
    H0_SH0ES, H0_HD = (73.04, 1.04), (73.43, 1.05)        # Riess et al. 2022; Das Hubble-Diagramm
    OM_SN = (0.333, 0.018)                                 # Ω_m aus Pantheon+ (Das Hubble-Diagramm)
    NEFF_PLANCK = (2.99, 0.17)                             # Planck 2018 VI mit BAO


    def download(url, path, check, tries=6, pause=15, timeout=600):
        # lädt einmal und legt die Datei im Cache ab; SkyView lehnt schnelle Folgeanfragen mit einer HTML-Seite ab
        path = Path(path)
        if path.exists():
            return path
        path.parent.mkdir(parents=True, exist_ok=True)
        for _ in range(tries):
            try:
                with urllib.request.urlopen(url, timeout=timeout) as r:
                    data = r.read()
                if check(data):
                    path.write_bytes(data)
                    return path
            except OSError:
                pass
            time.sleep(pause)
        raise OSError(f"{path.name}: kein gültiger Download nach {tries} Versuchen")


    def planck_txt(name):
        return np.loadtxt(download(IRSA + name, CMB / name, lambda d: d.startswith(b"#")))


    def fill_gaps(x):
        # SkyView lässt an den galaktischen Polen einzelne Pixel leer (genau 0); sie bekommen das Mittel ihrer Nachbarn
        bad = x == 0
        if bad.any():
            num = ndimage.uniform_filter(np.where(bad, 0.0, x), 3)
            den = ndimage.uniform_filter((~bad).astype(float), 3)
            x = np.where(bad, num / np.maximum(den, 1e-9), x)
        return x, int(bad.sum())


    def skyview(freq, glon, glat):
        # ein Feld der Planck-Karte in μK_CMB, Lücken gefüllt
        q = urllib.parse.urlencode({"Position": f"{glon},{glat}", "Coordinates": "Galactic", "Projection": "Arc",
                                    "Survey": f"Planck {freq} I", "Pixels": NPIX, "Size": SIZE, "Return": "FITS"})
        path = download(SKYVIEW + q, CMB / f"planck{freq}_{glon}_{glat}_arc.fits", lambda d: d.startswith(b"SIMPLE"))
        return fill_gaps(fits.getdata(path).astype(float) * 1e6)


    FULL = planck_txt("COM_PowerSpect_CMB-TT-full_R3.01.txt")        # ℓ, D_ℓ, −σ, +σ
    BINNED = planck_txt("COM_PowerSpect_CMB-TT-binned_R3.01.txt")    # ℓ, D_ℓ, −σ, +σ, bestes Modell
    THEORY = planck_txt("COM_PowerSpect_CMB-base-plikHM-TTTEEE-lowl-lowE-lensing-minimum-theory_R3.01.txt")   # ℓ, TT, TE, …
    L, DL = FULL[:, 0], FULL[:, 1]
    ERR = (FULL[:, 2] + FULL[:, 3]) / 2
    LT, DT = THEORY[:, 0], THEORY[:, 1]
    RAW = {name: {f: skyview(f, *lb) for f in FWHM} for name, lb in FIELDS.items()}
    MAPS = {name: {f: v[0] for f, v in m.items()} for name, m in RAW.items()}

    print(f"Spektrum: ℓ = {L[0]:.0f} bis {L[-1]:.0f} ({len(L)} Werte), {len(BINNED)} Bins, bestes Modell bis ℓ = {LT[-1]:.0f}")
    for name, m in MAPS.items():
        print(f"{name:15s} (l, b) = {FIELDS[name]}: {m['143'].shape[0]}×{m['143'].shape[1]} Pixel, "
              f"Streuung 100 GHz {m['100'].std():5.1f} μK, 143 GHz {m['143'].std():5.1f} μK, gefüllte Lücken {RAW[name]['143'][1]}")

    def ell_grid(n=NPIX):
        k = np.fft.fftfreq(n, d=PIX) * 2 * np.pi
        lx, ly = np.meshgrid(k, k)
        return lx, ly, np.hypot(lx, ly)


    def gauss_beam(ell, fwhm):
        s = np.radians(fwhm / 60) / np.sqrt(8 * np.log(2))
        return np.exp(-ell**2 * s**2 / 2)


    def transfer(freq, lx, ly, ell):
        # Strahl × HEALPix-Pixel (als Gauß mit σ = Pixel/√12) × Rechteck des 3′-Pixels (SkyView mittelt nach Fläche)
        hp = gauss_beam(ell, PIX_HEALPIX * np.sqrt(8 * np.log(2) / 12))
        return gauss_beam(ell, FWHM[freq]) * hp * np.sinc(lx * PIX / (2 * np.pi)) * np.sinc(ly * PIX / (2 * np.pi))


    def taper(n=NPIX, frac=0.125):
        # Kosinus-Rand: die äußeren 12.5 % jeder Seite gehen weich auf null
        w = np.ones(n)
        m = int(n * frac)
        w[:m] = 0.5 * (1 - np.cos(np.pi * np.arange(m) / m))
        w[-m:] = w[:m][::-1]
        return np.outer(w, w)


    WINDOW = taper()
    # ARC dehnt quer zum Radius um θ/sin θ; Mittel über das Feld, gewichtet mit dem Fenster (wirkt wie ein um diesen Faktor kleineres ℓ)
    _r = np.hypot(*np.meshgrid((np.arange(NPIX) - NPIX / 2 + 0.5) * PIX, (np.arange(NPIX) - NPIX / 2 + 0.5) * PIX))
    ARC_STRETCH = np.sum(WINDOW**2 / np.sqrt(np.sinc(_r / np.pi))) / np.sum(WINDOW**2)


    def remove_plane(x):
        yy, xx = np.mgrid[:x.shape[0], :x.shape[1]]
        A = np.column_stack([np.ones(x.size), xx.ravel(), yy.ravel()])
        c, *_ = np.linalg.lstsq(A, x.ravel(), rcond=None)
        return x - (A @ c).reshape(x.shape)


    def spectrum(a, b, fa=None, fb=None, edges=EDGES, sky=True):
        # Kreuzspektrum D_ℓ [μK²] zweier Karten; mit fa, fb geteilt durch Strahl und Pixelfenster beider Karten;
        # sky=True rechnet die Dehnung der ARC-Projektion aus ℓ heraus (für Simulationen auf dem ebenen Gitter: False)
        lx, ly, ell = ell_grid(a.shape[0])
        Fa, Fb = np.fft.fft2(remove_plane(a) * WINDOW), np.fft.fft2(remove_plane(b) * WINDOW)
        P = (Fa * np.conj(Fb)).real * PIX**2 / a.size / np.mean(WINDOW**2)
        if fa:
            P = P / (transfer(fa, lx, ly, ell) * transfer(fb, lx, ly, ell))
        i = np.digitize(ell.ravel(), edges) - 1
        ok = (i >= 0) & (i < len(edges) - 1)
        n = np.bincount(i[ok], minlength=len(edges) - 1)
        lb = np.bincount(i[ok], ell.ravel()[ok], minlength=len(edges) - 1) / n
        cb = np.bincount(i[ok], P.ravel()[ok], minlength=len(edges) - 1) / n
        lb = lb * ARC_STRETCH if sky else lb
        return lb, lb * (lb + 1) * cb / (2 * np.pi)


    def simulate(rng, big=3 * NPIX):
        # Gaußsches Zufallsfeld mit dem Spektrum des besten Modells auf einem dreimal größeren Feld, gefaltet wie die Karten
        lx, ly, ell = ell_grid(big)
        cl = np.interp(ell, LT, DT * 2 * np.pi / (LT * (LT + 1)), left=0.0)
        g = np.fft.fft2(rng.normal(size=(big, big)))
        c = (big - NPIX) // 2
        return {f: np.fft.ifft2(g * np.sqrt(cl) / PIX * transfer(f, lx, ly, ell)).real[c:c + NPIX, c:c + NPIX] for f in FWHM}


    def d_theory(ell):
        return np.interp(ell, LT, DT)


    def z_star(wb, wm):
        # Rekombination nach Hu & Sugiyama (1996), Gl. E1
        g1 = 0.0783 * wb**-0.238 / (1 + 39.5 * wb**0.763)
        g2 = 0.560 / (1 + 21.1 * wb**1.81)
        return 1048 * (1 + 0.00124 * wb**-0.738) * (1 + g1 * wm**g2)


    def model(h, wb, wm, neff=3.046):
        # flaches ΛCDM; ω_m = ω_b + ω_c + ω_ν, ein Neutrino mit 0.06 eV wie bei Planck
        m_nu = ([0.06] + [0.0] * (int(neff) - 1)) * u.eV
        return FlatLambdaCDM(H0=100 * h, Om0=(wm - OMEGA_NU) / h**2, Ob0=wb / h**2, Tcmb0=2.7255, Neff=neff, m_nu=m_nu)


    def acoustic(h, wb, wm, neff=3.046, zs=None):
        # z*, Schallhorizont r_s = ∫ c_s/H dz, Entfernung D_M(z*) und 100 θ*
        cm = model(h, wb, wm, neff)
        zs = z_star(wb, wm) if zs is None else zs
        cs = lambda z: C_KMS / np.sqrt(3 * (1 + 3 * wb / (4 * OMEGA_G) / (1 + z)))
        rs = integrate.quad(lambda z: cs(z) / cm.H(z).value, zs, np.inf, limit=200)[0]
        dm = cm.comoving_transverse_distance(zs).value
        return dict(zs=zs, rs=rs, dm=dm, theta=100 * rs / dm)


    def h_from_theta(theta, wb, wm=None, Om=None, neff=3.046):
        # h mit 100 θ*(h) = theta, bei festem ω_m oder (mit Om) bei festem Ω_m
        f = lambda h: acoustic(h, wb, wm if Om is None else Om * h**2, neff)["theta"] - theta
        return optimize.brentq(f, 0.4, 1.0, xtol=1e-6)


    def fit_extremum(guess, half, y, err, sign=1):
        # gewichtetes kubisches Polynom in guess ± half; Lage und Höhe des Maximums (sign = 1) oder Minimums (sign = −1)
        m = (L > guess - half) & (L < guess + half)
        x = L[m] - guess
        A = np.vander(x, 4, increasing=True)
        w = 1 / err[m] ** 2
        c = np.linalg.solve(A.T @ (A * w[:, None]), A.T @ (w * y[m]))
        xs = np.linspace(-half, half, 2001)
        p = np.vander(xs, 4, increasing=True) @ c
        k = np.argmax(sign * p)
        return guess + xs[k], p[k], c


    PEAKS = [(220, 90), (537, 90), (813, 90), (1127, 100), (1420, 110)]   # Startwert und halbe Breite des Fensters
    TROUGHS = [(411, 80), (674, 80), (1022, 90), (1314, 100)]


    def h2_hu(wb, wm, ns):
        return 0.925 * wm**0.18 * 2.4 ** (ns - 1) / (1 + (wb / 0.0164) ** (12 * wm**0.52)) ** 0.2


    def h3_hu(wb, wm, ns):
        return 2.17 / (1 + (wb / 0.044) ** 2) * wm**0.59 * 3.6 ** (ns - 1) / (1 + 1.63 * (1 - wb / 0.071) * wm)


    ref = acoustic(PLANCK["H0"][0] / 100, PLANCK["wb"][0], PLANCK["wm"][0])
    print(f"Dehnung der ARC-Projektion im Mittel über das Feld: {100 * (ARC_STRETCH - 1):.2f} %")
    print(f"Mit den Planck-Werten: z* = {ref['zs']:.2f}, r_s = {ref['rs']:.2f} Mpc, D_M = {ref['dm']:.0f} Mpc, 100 θ* = {ref['theta']:.5f}")


def sky_patch():
    """72. Ein Stück Himmel bei 100 und 143 GHz (Zellen 8 von cosmology_cmbpeaks.ipynb)."""
    global a, ax, axs, b, ext, fig, im, img, m, name, r, title
    ext = [SIZE / 2, -SIZE / 2, -SIZE / 2, SIZE / 2]
    a, b = MAPS["Nordpol"]["143"], MAPS["Nordpol"]["100"]
    fig, axs = plt.subplots(1, 3, figsize=(17, 5.6), sharey=True)
    for ax, img, title in zip(axs, [a - a.mean(), b - b.mean(), (a - b) / 2],
                              ["143 GHz", "100 GHz", "halbe Differenz (143 − 100)/2"]):
        im = ax.imshow(img, origin="lower", extent=ext, cmap="RdBu_r", vmin=-300, vmax=300)
        ax.set_title(f"Galaktischer Nordpol, {title}", fontsize=10)
        ax.set_xlabel("Abstand vom Feldmittelpunkt [°]")
    axs[0].set_ylabel("Abstand vom Feldmittelpunkt [°]")
    axs[0].plot([-6, -5], [-8.5, -8.5], color="k", lw=3)
    axs[0].text(-5.5, -8, "1°", ha="center", fontsize=10)
    fig.colorbar(im, ax=axs, shrink=0.85, label="ΔT [μK_CMB]")
    plt.show()

    for name, m in MAPS.items():
        a, b = m["143"] - m["143"].mean(), m["100"] - m["100"].mean()
        r = np.corrcoef(a.ravel(), b.ravel())[0, 1]
        print(f"{name:15s}: Streuung 143 GHz {a.std():5.1f} μK, 100 GHz {b.std():5.1f} μK, "
              f"halbe Differenz {((a - b) / 2).std():4.1f} μK, Korrelation {r:.4f}")


def planck_spectrum():
    """73. Das Leistungsspektrum von Planck (Zellen 11 von cosmology_cmbpeaks.ipynb)."""
    global ax, ax2, chi2, db, dbm, eb, fig, i, lb
    lb, db, eb, dbm = BINNED[:, 0], BINNED[:, 1], (BINNED[:, 2] + BINNED[:, 3]) / 2, BINNED[:, 4]
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw=dict(height_ratios=[3, 1]))
    ax.errorbar(L, DL, yerr=[FULL[:, 2], FULL[:, 3]], fmt=".", ms=2, color="0.75", elinewidth=0.4, zorder=1,
                label="Planck PR3, einzelne ℓ")
    ax.errorbar(lb, db, yerr=eb, fmt="o", ms=3.5, color="k", zorder=3, label="Planck PR3, Bins")
    ax.plot(LT[LT <= 2508], DT[LT <= 2508], color="C3", lw=1.4, zorder=2, label="bestes ΛCDM-Modell")
    ax.set_ylim(-500, 7500)
    ax.set_ylabel(r"$D_\ell = \ell(\ell+1)C_\ell/2\pi$ [μK²]")
    ax.set_title("Das Temperatur-Leistungsspektrum der Hintergrundstrahlung (Planck 2018)", fontsize=10)
    ax.legend(fontsize=9)
    ax2.axhline(0, color="C3", lw=1)
    ax2.errorbar(lb, (db - dbm) / eb, yerr=1, fmt="o", ms=3.5, color="k")
    ax2.set_ylim(-4, 4)
    ax2.set_xlabel("Multipol ℓ")
    ax2.set_ylabel("(Daten − Modell)/σ")
    ax2.set_xlim(0, 2520)
    plt.tight_layout()
    plt.show()

    i = np.argmax(db)
    chi2 = np.sum(((db - dbm) / eb) ** 2)
    print(f"höchster Bin: ℓ = {lb[i]:.0f}, D = {db[i]:.0f} μK²; das entspricht Flecken von etwa {180 / lb[i]:.2f}°")
    print(f"Quadrupol ℓ = 2: gemessen {DL[0]:.0f} (−{FULL[0, 2]:.0f}/+{FULL[0, 3]:.0f}) μK², Modell {d_theory(2):.0f} μK²")
    print(f"Bins gegen bestes Modell: χ² = {chi2:.1f} bei {len(lb)} Bins (χ²/N = {chi2 / len(lb):.2f})")


def beam_noise():
    """74. Strahl, Pixel und Rauschen (Zellen 14 von cosmology_cmbpeaks.ipynb)."""
    global ax, ax2, c, d, ell, ells, f, fig, half, i, k, lb
    global lx, ly, m, n, ok, spec, st, t2, target
    m = MAPS["Nordpol"]
    lx, ly, ell = ell_grid()
    ells = np.arange(2, 2001)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.8))
    for f, c in [("100", "C0"), ("143", "C1")]:
        ax.plot(ells, gauss_beam(ells, FWHM[f]) ** 2, color=c, ls="--", label=f"{f} GHz: nur Strahl ({FWHM[f]}′)")
        i = np.digitize(ell.ravel(), EDGES) - 1
        ok = (i >= 0) & (i < len(EDGES) - 1)
        t2 = np.bincount(i[ok], transfer(f, lx, ly, ell).ravel()[ok] ** 2) / np.bincount(i[ok])
        lb = np.bincount(i[ok], ell.ravel()[ok]) / np.bincount(i[ok])
        ax.plot(lb, t2, "o-", ms=3, color=c, label=f"{f} GHz: Strahl und Pixel")
    ax.axhline(0.5, color="0.6", lw=0.8)
    ax.set_xlabel("Multipol ℓ")
    ax.set_ylabel(r"Dämpfung der Leistung $B_\ell^2$")
    ax.set_title("Wie stark dämpfen Strahl und Pixel die kleinen Skalen?", fontsize=10)
    ax.legend(fontsize=9)
    spec = {"143 GHz ohne Korrektur": spectrum(m["143"], m["143"]),
            "143 GHz korrigiert": spectrum(m["143"], m["143"], "143", "143"),
            "100 GHz korrigiert": spectrum(m["100"], m["100"], "100", "100"),
            "Kreuzspektrum 100 × 143": spectrum(m["100"], m["143"], "100", "143"),
            "halbe Differenz (Rauschen, Vordergründe)": spectrum((m["143"] - m["100"]) / 2, (m["143"] - m["100"]) / 2, "143", "143")}
    for (k, (lb, d)), st in zip(spec.items(), [":", "-", "-", "-", "--"]):
        ax2.plot(lb, np.abs(d), st, marker="o", ms=3, label=k)
    ax2.plot(ells, d_theory(ells), color="k", lw=1.2, label="bestes ΛCDM-Modell")
    ax2.set_yscale("log")
    ax2.set_ylim(5, 2e4)
    ax2.set_xlabel("Multipol ℓ")
    ax2.set_ylabel(r"$D_\ell$ [μK²]")
    ax2.set_title("Spektren des Feldes am Nordpol", fontsize=10)
    ax2.legend(fontsize=8.5, loc="lower left")
    plt.tight_layout()
    plt.show()

    half = {f: ells[np.argmin(np.abs(gauss_beam(ells, FWHM[f]) ** 2 - 0.5))] for f in FWHM}
    print(f"Strahl allein halbiert die Leistung bei ℓ = {half['100']} (100 GHz) und ℓ = {half['143']} (143 GHz)")
    lb = spec["143 GHz korrigiert"][0]
    for target in (500, 1000, 1500, 1900):
        k = np.argmin(np.abs(lb - target))
        n = spec["halbe Differenz (Rauschen, Vordergründe)"][1][k]
        print(f"ℓ ≈ {lb[k]:4.0f}: 143 korrigiert {spec['143 GHz korrigiert'][1][k]:6.0f}, Kreuz {spec['Kreuzspektrum 100 × 143'][1][k]:6.0f}, "
              f"halbe Differenz {n:6.0f}, Modell {d_theory(lb[k]):5.0f} μK²")


def point_sources():
    """75. Punktquellen (Zellen 17 von cosmology_cmbpeaks.ipynb)."""
    global CLEAN, SOURCES, _, ax, ax2, field_mean, fig, find_sources, im, inpaint, k, lb
    global m, name, pos, show, snr, target, x, x_clean, x_raw, y
    def find_sources(m, freq, nsig=5.0):
        # Hochpass (Karte minus Glättung auf 30′), dann Glättung mit dem Strahl; Maxima über nsig robusten σ
        hp = m - ndimage.gaussian_filter(m, 30 / 3 / 2.355)
        mf = ndimage.gaussian_filter(hp, FWHM[freq] / 3 / 2.355)
        snr = mf / (1.4826 * np.median(np.abs(mf - np.median(mf))))
        lab, n = ndimage.label(snr > nsig)
        return [tuple(p) for p in ndimage.maximum_position(snr, lab, range(1, n + 1))], snr


    def inpaint(m, pos, r=4, r2=7):
        # Kreis mit Radius r Pixel (12′) durch den Median des Rings r bis r2 ersetzen
        out = m.copy()
        yy, xx = np.mgrid[:m.shape[0], :m.shape[1]]
        for y, x in pos:
            d = np.hypot(yy - y, xx - x)
            out[d < r] = np.median(m[(d >= r) & (d < r2)])
        return out


    SOURCES, CLEAN = {}, {}
    for name, m in MAPS.items():
        pos = sorted(set(find_sources(m["100"], "100")[0]) | set(find_sources(m["143"], "143")[0]))
        SOURCES[name] = pos
        CLEAN[name] = {f: inpaint(m[f], pos) for f in FWHM}


    def field_mean(maps, fa, fb):
        lb = spectrum(maps["Nordpol"][fa], maps["Nordpol"][fb], fa, fb)[0]
        return lb, np.mean([spectrum(maps[n][fa], maps[n][fb], fa, fb)[1] for n in maps], axis=0)


    lb, x_raw = field_mean(MAPS, "100", "143")
    _, x_clean = field_mean(CLEAN, "100", "143")
    show = "Nord, l = 150°"
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    snr = find_sources(MAPS[show]["100"], "100")[1]
    im = ax.imshow(snr, origin="lower", extent=ext, cmap="RdBu_r", vmin=-6, vmax=6)
    for y, x in SOURCES[show]:
        ax.add_patch(plt.Circle((SIZE / 2 - (x + 0.5) * SIZE / NPIX, (y + 0.5) * SIZE / NPIX - SIZE / 2), 0.6, fill=False, color="k", lw=1.5))
    fig.colorbar(im, ax=ax, shrink=0.85, label="gefilterte Karte [robuste σ]")
    ax.set_xlabel("Abstand vom Feldmittelpunkt, Ost-West [°]")
    ax.set_ylabel("Abstand vom Feldmittelpunkt, Süd-Nord [°]")
    ax.set_title(f"Feld {show}, 100 GHz nach Hochpass und Strahlfilter; Kreise: Quellen über 5σ", fontsize=10)
    ax2.plot(lb, x_raw / d_theory(lb), "o-", ms=3.5, color="C3", label="Kreuzspektrum, alle Quellen")
    ax2.plot(lb, x_clean / d_theory(lb), "o-", ms=3.5, color="C0", label="nach dem Ersetzen der Quellen")
    ax2.axhline(1, color="0.5", lw=0.8)
    ax2.set_xlabel("Multipol ℓ")
    ax2.set_ylabel(r"$D_\ell$ / bestes Modell")
    ax2.set_title("Kreuzspektrum 100 × 143 der vier Felder, geteilt durch das Modell", fontsize=10)
    ax2.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    for name, pos in SOURCES.items():
        print(f"{name:15s}: {len(pos)} Quellen; Spitzen bei 100 / 143 GHz [μK]: " +
              ", ".join(f"{MAPS[name]['100'][p] - np.median(MAPS[name]['100']):.0f}/{MAPS[name]['143'][p] - np.median(MAPS[name]['143']):.0f}" for p in pos))
    for target in (500, 1000, 1500, 1900):
        k = np.argmin(np.abs(lb - target))
        print(f"ℓ ≈ {lb[k]:4.0f}: Kreuzspektrum / Modell {x_raw[k] / d_theory(lb[k]):.2f} mit Quellen, {x_clean[k] / d_theory(lb[k]):.2f} ohne")


def cosmic_variance():
    """76. Kosmische Varianz und ein Test des Verfahrens (Zellen 20 von cosmology_cmbpeaks.ipynb)."""
    global N_SIM, ax, ax2, expect, fig, fsky_planck, hi, k, lb, lo, n_ring, ratio
    global rng, s, sims, w2, w4
    rng = np.random.default_rng(42)
    N_SIM = 24
    lb = spectrum(MAPS["Nordpol"]["100"], MAPS["Nordpol"]["143"], "100", "143", sky=False)[0]
    sims = np.array([spectrum(s["100"], s["143"], "100", "143", sky=False)[1] for s in (simulate(rng) for _ in range(N_SIM))])
    ratio = sims / d_theory(lb)
    w2, w4 = np.mean(WINDOW**2), np.mean(WINDOW**4)
    n_ring = lb * np.diff(EDGES) * np.radians(SIZE) ** 2 / (2 * np.pi) * w2**2 / w4   # unabhängige Wellen pro Ring
    expect = np.sqrt(2 / n_ring)

    fsky_planck = 2 / ((2 * L + 1) * (ERR / d_theory(L)) ** 2)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.6))
    ax.plot(L[L >= 30], fsky_planck[L >= 30], ".", ms=2, color="0.6", label="einzelne ℓ")
    k = np.convolve(fsky_planck[L >= 30], np.ones(51) / 51, mode="same")
    ax.plot(L[L >= 30][25:-25], k[25:-25], color="C3", lw=1.6, label="gleitender Mittelwert über 51 ℓ")
    ax.set_ylim(0, 1)
    ax.set_xlabel("Multipol ℓ")
    ax.set_ylabel(r"wirksamer Himmelsanteil $f_\mathrm{sky}$")
    ax.set_title("Wo begrenzt die kosmische Varianz Planck, wo das Rauschen?", fontsize=10)
    ax.legend(fontsize=9)
    ax2.errorbar(lb, ratio.mean(0), yerr=ratio.std(0) / np.sqrt(N_SIM), fmt="o", ms=3.5, color="C0",
                 label=f"Mittel der {N_SIM} Simulationen / Eingabe")
    ax2.plot(lb, ratio.std(0), "s", ms=3.5, color="C1", label="Streuung von Feld zu Feld")
    ax2.plot(lb, expect, color="C1", lw=1.4, label="erwartet aus der kosmischen Varianz eines 20°-Feldes")
    ax2.axhline(1, color="0.5", lw=0.8)
    ax2.set_xlabel("Multipol ℓ")
    ax2.set_ylabel(r"relativ zum Eingangsspektrum")
    ax2.set_title("Gibt das Verfahren das Eingangsspektrum zurück?", fontsize=10)
    ax2.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    for lo, hi in [(30, 800), (800, 1300), (1300, 1800), (1800, 2508)]:
        s = (L >= lo) & (L < hi)
        print(f"Planck ℓ = {lo:4d}–{hi:4d}: Fehler / kosmische Varianz {np.median(ERR[s] / d_theory(L[s]) * np.sqrt((2 * L[s] + 1) / 2)):5.2f}, "
              f"f_sky = {np.median(fsky_planck[s]):.2f}")
    for lo, hi in [(40, 400), (400, 1200), (1200, 2000)]:
        s = (lb >= lo) & (lb < hi)
        print(f"Simulationen ℓ = {lo:4d}–{hi:4d}: Mittel/Eingabe {ratio[:, s].mean():.3f} ± {ratio[:, s].mean(1).std() / np.sqrt(N_SIM):.3f}, "
              f"Streuung/erwartet {np.mean(ratio[:, s].std(0) / expect[s]):.2f}")
    print(f"wirksamer Himmelsanteil eines Feldes: {np.radians(SIZE) ** 2 * w2**2 / w4 / (4 * np.pi):.4f}")


def own_spectrum():
    """77. Das eigene Spektrum aus vier Feldern (Zellen 23 von cosmology_cmbpeaks.ipynb)."""
    global LMAX_OWN, _, auto100, auto143, ax, ax2, c2, chi2_own, cross, dof, dof_own, e
    global e_own, ells, fig, fit_own, free, lab, lb, lmax, n_ring, names, own_model, p
    global p_own, sig, theta_own, w2, w4
    names = list(MAPS)
    lb, cross = field_mean(CLEAN, "100", "143")
    _, auto100 = field_mean(CLEAN, "100", "100")
    _, auto143 = field_mean(CLEAN, "143", "143")
    w2, w4 = np.mean(WINDOW**2), np.mean(WINDOW**4)
    n_ring = lb / ARC_STRETCH * np.diff(EDGES) * np.radians(SIZE) ** 2 / (2 * np.pi) * w2**2 / w4
    sig = np.sqrt((auto100 * auto143 + cross**2) / (len(names) * n_ring))
    LMAX_OWN = 1200


    def own_model(p, ell=lb):
        A, P, alpha = p
        return A * d_theory(ell * alpha) + P * (ell / 1500) ** 2


    def fit_own(lmax, free=(True, True, True)):
        # least squares bis lmax; nicht freie Größen bleiben bei A = 1, P = 0, α = 1
        m = lb <= lmax
        idx = [i for i in range(3) if free[i]]

        def full(q):
            p = np.array([1.0, 0.0, 1.0])
            p[idx] = q
            return p

        r = optimize.least_squares(lambda q: ((cross - own_model(full(q))) / sig)[m], np.array([1.0, 100.0, 1.0])[idx])
        e = np.zeros(3)
        e[idx] = np.sqrt(np.diag(np.linalg.inv(r.jac.T @ r.jac)))
        return full(r.x), e, np.sum(r.fun**2), m.sum() - len(idx)


    p_own, e_own, chi2_own, dof_own = fit_own(LMAX_OWN)
    theta_own = PLANCK["theta"][0] * p_own[2], PLANCK["theta"][0] * e_own[2]
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw=dict(height_ratios=[3, 1]))
    ells = np.arange(30, 2001)
    ax.errorbar(BINNED[:, 0], BINNED[:, 1], yerr=BINNED[:, 2], fmt="s", ms=3, color="0.6", label="Planck PR3, Bins")
    ax.plot(ells, d_theory(ells), color="k", lw=1, label="bestes ΛCDM-Modell")
    ax.errorbar(lb, cross, yerr=sig, fmt="o", ms=4.5, color="C0", label="eigenes Kreuzspektrum, vier Felder")
    ax.plot(ells, own_model(p_own, ells), color="C3", lw=1.4, label=f"Fit bis ℓ = {LMAX_OWN}: A, P, α")
    ax.plot(ells, p_own[1] * (ells / 1500) ** 2, color="C3", ls="--", lw=1, label="davon Punktquellen P (ℓ/1500)²")
    ax.axvline(LMAX_OWN, color="0.7", ls=":")
    ax.set_ylim(0, 7000)
    ax.set_ylabel(r"$D_\ell$ [μK²]")
    ax.set_title("Das eigene Spektrum aus 4 × 400 Quadratgrad gegen Planck", fontsize=10)
    ax.legend(fontsize=9)
    ax2.errorbar(lb, (cross - own_model(p_own)) / sig, yerr=1, fmt="o", ms=4, color="C0")
    ax2.axhline(0, color="C3")
    ax2.set_ylim(-4, 4)
    ax2.set_xlabel("Multipol ℓ")
    ax2.set_ylabel("(eigen − Fit)/σ")
    plt.tight_layout()
    plt.show()

    print(f"Fit bis ℓ = {LMAX_OWN}: A = {p_own[0]:.3f} ± {e_own[0]:.3f}, P = {p_own[1]:.0f} ± {e_own[1]:.0f} μK², "
          f"α = {p_own[2]:.4f} ± {e_own[2]:.4f}; χ² = {chi2_own:.1f} bei {dof_own} Freiheitsgraden")
    print(f"eigenes 100 θ* = {theta_own[0]:.4f} ± {theta_own[1]:.4f} (Planck {PLANCK['theta'][0]:.5f})")
    for lmax, free, lab in [(LMAX_OWN, (True, True, False), "α = 1 fest"), (LMAX_OWN, (True, False, True), "ohne Punktquellen"),
                            (2000, (True, True, True), "bis ℓ = 2000")]:
        p, e, c2, dof = fit_own(lmax, free)
        print(f"  {lab:18s}: A = {p[0]:.3f}, P = {p[1]:4.0f}, α = {p[2]:.4f} ± {e[2]:.4f}, χ² = {c2:.1f} bei {dof}")


def peaks():
    """78. Lage und Höhe der Peaks (Zellen 26 von cosmology_cmbpeaks.ipynb)."""
    global H_MC, H_OBS, H_THEORY, N_MC, PK, PK_E, PK_T, TR, TR_E, TR_T, ax, c
    global col, extrema, fig, g, h, i, lst, mc, rng, s, sign, x
    global x0, xs, y, y0
    rng = np.random.default_rng(7)
    N_MC = 300


    def extrema(y):
        pk = np.array([fit_extremum(g, h, y, ERR, 1)[:2] for g, h in PEAKS])
        tr = np.array([fit_extremum(g, h, y, ERR, -1)[:2] for g, h in TROUGHS])
        return pk, tr


    PK, TR = extrema(DL)
    PK_T, TR_T = extrema(d_theory(L))
    mc = [extrema(DL + rng.normal(0, ERR)) for _ in range(N_MC)]
    PK_E = np.std([m[0] for m in mc], axis=0)
    TR_E = np.std([m[1] for m in mc], axis=0)
    H_OBS = np.array([PK[1, 1] / PK[0, 1], PK[2, 1] / PK[0, 1]])
    H_MC = np.array([[m[0][1, 1] / m[0][0, 1], m[0][2, 1] / m[0][0, 1]] for m in mc])
    H_THEORY = np.array([PK_T[1, 1] / PK_T[0, 1], PK_T[2, 1] / PK_T[0, 1]])

    fig, ax = plt.subplots(figsize=(14, 6))
    s = (L >= 100) & (L <= 1900)
    ax.plot(L[s], DL[s], ".", ms=2.5, color="0.7", label="Planck PR3, einzelne ℓ")
    ax.plot(L[s], d_theory(L[s]), color="k", lw=0.8, label="bestes ΛCDM-Modell")
    for lst, sign, col in [(PEAKS, 1, "C3"), (TROUGHS, -1, "C0")]:
        for g, h in lst:
            x0, y0, c = fit_extremum(g, h, DL, ERR, sign)
            xs = np.linspace(-h, h, 200)
            ax.plot(g + xs, np.vander(xs, 4, increasing=True) @ c, color=col, lw=2)
    ax.errorbar(PK[:, 0], PK[:, 1], xerr=PK_E[:, 0], yerr=PK_E[:, 1], fmt="o", color="C3", ms=6, capsize=3, label="Peaks (kubischer Fit)")
    ax.errorbar(TR[:, 0], TR[:, 1], xerr=TR_E[:, 0], yerr=TR_E[:, 1], fmt="s", color="C0", ms=6, capsize=3, label="Täler")
    for i, (x, y) in enumerate(PK):
        ax.annotate(f"{i + 1}", (x, y), xytext=(0, 10), textcoords="offset points", ha="center", fontsize=11, color="C3")
    ax.set_xlabel("Multipol ℓ")
    ax.set_ylabel(r"$D_\ell$ [μK²]")
    ax.set_title("Fünf Peaks und vier Täler im Spektrum von Planck", fontsize=10)
    ax.legend(fontsize=9)
    plt.show()

    print(" Nr.   ℓ (Planck)      ℓ (Modell)   D (Planck) [μK²]   D (Modell)")
    for i in range(len(PK)):
        print(f"Peak {i + 1}: {PK[i, 0]:7.1f} ± {PK_E[i, 0]:4.1f}   {PK_T[i, 0]:7.1f}     {PK[i, 1]:6.0f} ± {PK_E[i, 1]:3.0f}     {PK_T[i, 1]:6.0f}")
    for i in range(len(TR)):
        print(f"Tal  {i + 1}: {TR[i, 0]:7.1f} ± {TR_E[i, 0]:4.1f}   {TR_T[i, 0]:7.1f}     {TR[i, 1]:6.0f} ± {TR_E[i, 1]:3.0f}     {TR_T[i, 1]:6.0f}")
    print(f"H2 = {H_OBS[0]:.4f} ± {H_MC[:, 0].std():.4f} (Modell {H_THEORY[0]:.4f}),  H3 = {H_OBS[1]:.4f} ± {H_MC[:, 1].std():.4f} (Modell {H_THEORY[1]:.4f})")


def peak_spacing():
    """79. Der Abstand der Peaks (Zellen 29 von cosmology_cmbpeaks.ipynb)."""
    global G, LA, LA_T, PHI, PHI_T, THETA_PEAKS, THETA_RAW, ax, ax2, fig, la_mc, n
    global nn, phi_hu, r_hu, spacing
    n = np.arange(1, len(PK) + 1)
    G = np.column_stack([n, -np.ones(len(n))])                  # ℓ_n = ℓ_A n − ℓ_A φ


    def spacing(lp):
        c = np.linalg.lstsq(G, lp, rcond=None)[0]
        return c[0], c[1] / c[0]


    LA, PHI = spacing(PK[:, 0])
    LA_T, PHI_T = spacing(PK_T[:, 0])
    la_mc = np.array([spacing(m[0][:, 0])[0] for m in mc])
    THETA_RAW = 100 * np.pi / LA
    THETA_PEAKS = (PLANCK["theta"][0] * LA_T / LA, PLANCK["theta"][0] * LA_T * la_mc.std() / LA**2)
    r_hu = 0.042 / PLANCK["wm"][0] * PLANCK["zstar"][0] / 1000      # r* aus Hu et al. 2001, Gl. A5
    phi_hu = 0.267 * (r_hu / 0.3) ** 0.1                              # Gl. A7

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.6))
    ax.errorbar(n, PK[:, 0], yerr=PK_E[:, 0], fmt="o", color="C3", ms=7, label="Peaks von Planck")
    ax.errorbar(np.arange(len(TR)) + 1.5, TR[:, 0], yerr=TR_E[:, 0], fmt="s", color="C0", ms=6, label="Täler (bei n + ½)")
    nn = np.linspace(0.5, 5.5, 50)
    ax.plot(nn, LA * (nn - PHI), color="k", lw=1.2, label=f"ℓ_A (n − φ): ℓ_A = {LA:.1f}, φ = {PHI:.3f}")
    ax.set_xticks(n)
    ax.set_xlabel("Nummer n")
    ax.set_ylabel("Lage ℓ")
    ax.set_title("Liegen die Peaks in gleichen Abständen?", fontsize=10)
    ax.legend(fontsize=9)
    ax2.errorbar(n, PK[:, 0] - LA * (n - PHI), yerr=PK_E[:, 0], fmt="o-", color="C3", ms=7, label="Planck")
    ax2.plot(n, PK_T[:, 0] - LA_T * (n - PHI_T), "s--", color="k", ms=6, mfc="none", label="bestes Modell")
    ax2.axhline(0, color="0.6", lw=0.8)
    ax2.set_xticks(n)
    ax2.set_xlabel("Nummer n des Peaks")
    ax2.set_ylabel("Abweichung von der Geraden Δℓ")
    ax2.set_title("Ungerade und gerade Peaks weichen in entgegengesetzte Richtungen ab", fontsize=10)
    ax2.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    print(f"Planck: ℓ_A = {LA:.2f} ± {la_mc.std():.2f}, φ = {PHI:.3f};  bestes Modell: ℓ_A = {LA_T:.2f}, φ = {PHI_T:.3f};  "
          f"Hu et al.: φ ≈ {phi_hu:.3f}")
    print(f"100 θ* roh π/ℓ_A = {THETA_RAW:.4f} (das sind {np.degrees(np.pi / LA):.3f}°); "
          f"geeicht = {THETA_PEAKS[0]:.4f} ± {THETA_PEAKS[1]:.4f} (Planck {PLANCK['theta'][0]:.5f})")
    print(f"für das beste Modell gibt π/ℓ_A 100 θ* = {100 * np.pi / LA_T:.4f} statt 1.04110: Fehler der Geraden {100 * (np.pi / LA_T / 1.0411e-2 - 1):+.2f} %")


def sound_horizon():
    """80. Der Schallhorizont (Zellen 32 von cosmology_cmbpeaks.ipynb)."""
    global R, REF, ax, ax2, axr, before, cm0, cm_nob, cs, dr, fig, h0
    global k, lab, ref_pz, rs_above, rs_nob, wb0, wm0, z, z_eq, zz
    h0, wb0, wm0 = PLANCK["H0"][0] / 100, PLANCK["wb"][0], PLANCK["wm"][0]
    cm0 = model(h0, wb0, wm0)
    z = np.logspace(1, 8, 4000)
    R = 3 * wb0 / (4 * OMEGA_G) / (1 + z)
    cs = 1 / np.sqrt(3 * (1 + R))
    dr = C_KMS * cs / cm0.H(z).value                                  # dr_s/dz [Mpc]
    rs_above = np.concatenate([np.cumsum(((dr[1:] + dr[:-1]) / 2 * np.diff(z))[::-1])[::-1], [0.0]])   # ∫_z^∞
    REF = acoustic(h0, wb0, wm0)
    ref_pz = acoustic(h0, wb0, wm0, zs=PLANCK["zstar"][0])
    cm_nob = lambda zz: C_KMS / np.sqrt(3) / cm0.H(zz).value
    rs_nob = integrate.quad(cm_nob, REF["zs"], np.inf, limit=200)[0]
    z_eq = wm0 / (OMEGA_G * (1 + 0.2271 * 3.046)) - 1                   # Strahlung: Photonen und 3.046 Neutrinoarten

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.6))
    ax.plot(z, cs, color="C0", lw=1.6, label=r"$c_s/c$")
    ax.axhline(1 / np.sqrt(3), color="C0", ls=":", lw=1, label=r"$1/\sqrt{3}$ (ohne Baryonen)")
    ax.set_xscale("log")
    ax.set_xlim(z[-1], 3e2)
    ax.axvspan(3e2, REF["zs"], color="0.9", zorder=0)
    ax.text(560, 0.33, "nach der Rekombination", rotation=90, fontsize=9, ha="center", va="center")
    ax.set_xlabel("Rotverschiebung z (die Zeit läuft nach rechts)")
    ax.set_ylabel(r"Schallgeschwindigkeit $c_s/c$", color="C0")
    axr = ax.twinx()
    axr.plot(z, R, color="C1", lw=1.6, label=r"$R = 3\rho_b/4\rho_\gamma$")
    axr.set_yscale("log")
    axr.set_ylabel("R", color="C1")
    for zz, lab in [(REF["zs"], "z*"), (z_eq, r"$z_\mathrm{eq}$")]:
        ax.axvline(zz, color="0.5", ls="--", lw=1)
        ax.text(zz * 1.15, 0.585, lab, fontsize=10)
    ax.set_title("Baryonen bremsen den Schall", fontsize=10)
    ax.legend(loc="lower left", fontsize=9)
    axr.legend(loc="lower right", fontsize=9)
    before = z >= REF["zs"]
    ax2.plot(z[before], rs_above[before], color="C3", lw=1.6)
    ax2.axvline(REF["zs"], color="0.5", ls="--", lw=1)
    ax2.axvline(z_eq, color="0.5", ls="--", lw=1)
    ax2.plot(REF["zs"], REF["rs"], "o", color="C3", ms=8)
    ax2.annotate(f"r_s = {REF['rs']:.1f} Mpc bei z* = {REF['zs']:.0f}", (REF["zs"], REF["rs"]), xytext=(-230, 0),
                 textcoords="offset points", fontsize=10, arrowprops=dict(arrowstyle="->", color="0.4"))
    ax2.text(z_eq * 1.15, 5, r"$z_\mathrm{eq}$", fontsize=10)
    ax2.set_xscale("log")
    ax2.set_xlim(z[-1], 3e2)
    ax2.set_ylim(0, 160)
    ax2.set_xlabel("Rotverschiebung z (die Zeit läuft nach rechts)")
    ax2.set_ylabel(r"$\int_z^\infty c_s\,dz/H$ [Mpc, mitbewegt]")
    ax2.set_title("Wie der Schallhorizont bis zur Rekombination wächst", fontsize=10)
    plt.tight_layout()
    plt.show()

    k = np.argmin(np.abs(z - REF["zs"]))
    print(f"z* = {REF['zs']:.2f} (Näherung) gegen {PLANCK['zstar'][0]} (Planck); z_eq = {z_eq:.0f}; "
          f"bei z*: R = {R[k]:.3f}, c_s = {cs[k]:.3f} c")
    print(f"r_s = {REF['rs']:.2f} Mpc (Planck {PLANCK['rstar'][0]} ± {PLANCK['rstar'][1]}), D_M = {REF['dm']:.0f} Mpc, "
          f"100 θ* = {REF['theta']:.5f} (Planck {PLANCK['theta'][0]})")
    print(f"mit z* von Planck: r_s = {ref_pz['rs']:.2f} Mpc, 100 θ* = {ref_pz['theta']:.5f}")
    print(f"ohne Baryonen in c_s: r_s = {rs_nob:.1f} Mpc ({100 * (rs_nob / REF['rs'] - 1):+.0f} %); "
          f"vor z_eq entstanden {100 * np.interp(z_eq, z, rs_above) / REF['rs']:.0f} % von r_s")


def template():
    """81. Die Schablone: $\\theta_\\star$ aus dem ganzen Spektrum (Zellen 35 von cosmology_cmbpeaks.ipynb)."""
    global A, STRETCH, THETA_FIT, a, a_best, alphas, ax, c, c2, chi2_stretch, col, e
    global fig, k, lmax, nn, prof, use
    use = L >= 30


    def chi2_stretch(alpha, lmax):
        s = use & (L <= lmax)
        t = d_theory(L[s] * alpha)
        A = np.sum(DL[s] * t / ERR[s] ** 2) / np.sum(t**2 / ERR[s] ** 2)
        return np.sum(((DL[s] - A * t) / ERR[s]) ** 2), A


    alphas = np.linspace(0.994, 1.006, 241)
    STRETCH = {}
    fig, ax = plt.subplots(figsize=(11, 5.6))
    for lmax, col in [(800, "C0"), (1500, "C1"), (2508, "C3")]:
        prof = np.array([chi2_stretch(a, lmax)[0] for a in alphas])
        k = np.argmin(prof)
        c = np.polyfit(alphas[max(k - 15, 0):k + 16] - alphas[k], prof[max(k - 15, 0):k + 16], 2)
        a_best = alphas[k] - c[1] / (2 * c[0])
        STRETCH[lmax] = (a_best, 1 / np.sqrt(c[0]), prof.min(), chi2_stretch(a_best, lmax)[1], np.sum(use & (L <= lmax)))
        ax.plot(PLANCK["theta"][0] * alphas, prof - prof.min(), color=col, lw=1.6, label=f"ℓ = 30 bis {lmax}")
    ax.axhline(1, color="0.5", ls=":", lw=1)
    ax.axvspan(PLANCK_TT["theta"][0] - PLANCK_TT["theta"][1], PLANCK_TT["theta"][0] + PLANCK_TT["theta"][1], color="0.85",
               label="Planck TT+lowE (alle Parameter frei)")
    ax.set_ylim(0, 25)
    ax.set_xlabel(r"$100\,\theta_* = 100\,\alpha\,\theta_*^\mathrm{Modell}$")
    ax.set_ylabel(r"$\Delta\chi^2$")
    ax.set_title("Wie stark legt die Form des Spektrums den Winkel des Schallhorizonts fest?", fontsize=10)
    ax.legend(fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=4)
    plt.show()

    for lmax, (a, e, c2, A, nn) in STRETCH.items():
        print(f"ℓ bis {lmax:4d}: α = {a:.5f} ± {e:.5f}, 100 θ* = {PLANCK['theta'][0] * a:.5f} ± {PLANCK['theta'][0] * e:.5f}, "
              f"A = {A:.4f}, χ² = {c2:.0f} bei {nn} Werten")
    THETA_FIT = (PLANCK["theta"][0] * STRETCH[2508][0], PLANCK["theta"][0] * STRETCH[2508][1])
    print(f"Planck TT+lowE: 100 θ* = {PLANCK_TT['theta'][0]} ± {PLANCK_TT['theta'][1]}; "
          f"Abstand {(THETA_FIT[0] - PLANCK_TT['theta'][0]) / np.hypot(THETA_FIT[1], PLANCK_TT['theta'][1]):+.1f} σ")


def baryons_matter():
    """82. Baryonen und Materie aus den Peakhöhen (Zellen 38 von cosmology_cmbpeaks.ipynb)."""
    global NS, WB_OWN, WM_OWN, W_MC, W_SYS, ax, col, e, f, fig, formula_err, gb
    global gm, h, invert, lab, ns, v, wb_cal, wm_cal
    NS = PLANCK["ns"][0]


    def invert(h2, h3, ns=NS):
        return optimize.fsolve(lambda p: [h2_hu(*p, ns) - h2, h3_hu(*p, ns) - h3], [0.022, 0.14])


    WB_OWN, WM_OWN = invert(*H_OBS)
    W_MC = np.array([invert(*h) for h in H_MC])
    formula_err = np.array([h2_hu(wb0, wm0, NS), h3_hu(wb0, wm0, NS)]) / H_THEORY - 1        # Fehler der Formeln am Modell
    wb_cal, wm_cal = invert(*(H_OBS * (1 + formula_err)))
    W_SYS = np.abs([WB_OWN - wb_cal, WM_OWN - wm_cal])

    gb, gm = np.meshgrid(np.linspace(0.019, 0.026, 300), np.linspace(0.115, 0.170, 300))
    fig, ax = plt.subplots(figsize=(10, 7))
    for f, h, e, col, lab in [(h2_hu, H_OBS[0], H_MC[:, 0].std(), "C0", "H₂"), (h3_hu, H_OBS[1], H_MC[:, 1].std(), "C1", "H₃")]:
        v = f(gb, gm, NS)
        ax.contourf(gb, gm, np.abs(v - h), levels=[0, e], colors=[col], alpha=0.35)
        ax.contour(gb, gm, v, levels=[h], colors=[col], linewidths=1.5)
        ax.plot([], [], color=col, lw=6, alpha=0.5, label=f"{lab} = {h:.3f} ± {e:.3f}")
    ax.plot(W_MC[:, 0], W_MC[:, 1], ".", ms=2, color="0.3", alpha=0.5, label="Monte-Carlo-Wiederholungen")
    ax.plot(WB_OWN, WM_OWN, "*", ms=16, color="C3", label="eigene Lösung")
    ax.errorbar(PLANCK["wb"][0], PLANCK["wm"][0], xerr=PLANCK["wb"][1], yerr=PLANCK["wm"][1], fmt="s", color="k", ms=7,
                label="Planck TT,TE,EE+lowE+lensing")
    ax.errorbar(PLANCK_TT["wb"][0], PLANCK_TT["wm"][0], xerr=PLANCK_TT["wb"][1], yerr=PLANCK_TT["wm"][1], fmt="D", color="0.5",
                ms=6, label="Planck TT+lowE")
    ax.set_xlabel(r"Baryonen $\omega_b = \Omega_b h^2$")
    ax.set_ylabel(r"Materie $\omega_m = \Omega_m h^2$")
    ax.set_title("Wo sich die Streifen gleicher Peakhöhe kreuzen", fontsize=10)
    ax.legend(fontsize=9, loc="upper left")
    plt.show()

    print(f"Formeln am besten Modell: H₂ um {100 * formula_err[0]:+.1f} %, H₃ um {100 * formula_err[1]:+.1f} % daneben")
    print(f"ω_b = {WB_OWN:.5f} ± {W_MC[:, 0].std():.5f} (stat.) ± {W_SYS[0]:.5f} (Formel), Planck {PLANCK['wb'][0]}")
    print(f"ω_m = {WM_OWN:.4f} ± {W_MC[:, 1].std():.4f} (stat.) ± {W_SYS[1]:.4f} (Formel), Planck {PLANCK['wm'][0]}")
    for ns in (0.955, 0.975):
        print(f"mit n_s = {ns}: ω_b = {invert(*H_OBS, ns)[0]:.5f}, ω_m = {invert(*H_OBS, ns)[1]:.4f}")


def h0_cmb():
    """83. H₀ aus dem Winkel des Schallhorizonts (Zellen 41 von cosmology_cmbpeaks.ipynb)."""
    global H_A, H_B, H_B_ERR, H_C, H_C_ERR, ax, ax2, b, col, fig, hb_mc, hb_sys
    global hc_pm, hh, lab, line, m, oms, th_mc, wb_mc, wm_mc
    wb_mc, wm_mc = W_MC[:100, 0], W_MC[:100, 1]
    th_mc = THETA_FIT[0] + rng.normal(0, THETA_FIT[1], 100)
    H_A = 100 * h_from_theta(THETA_FIT[0], wb0, wm0)
    H_B = 100 * h_from_theta(THETA_FIT[0], WB_OWN, WM_OWN)
    hb_mc = np.array([100 * h_from_theta(t, b, m) for t, b, m in zip(th_mc, wb_mc, wm_mc)])
    hb_sys = abs(100 * h_from_theta(THETA_FIT[0], wb_cal, wm_cal) - H_B)
    H_B_ERR = np.hypot(hb_mc.std(), hb_sys)
    H_C = 100 * h_from_theta(THETA_FIT[0], WB_OWN, Om=OM_SN[0])
    hc_pm = [100 * h_from_theta(THETA_FIT[0], WB_OWN, Om=OM_SN[0] + d * OM_SN[1]) for d in (-1, 1)]
    H_C_ERR = abs(hc_pm[0] - hc_pm[1]) / 2

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    hh = np.linspace(0.60, 0.78, 37)
    for (b, m, lab, col) in [(wb0, wm0, "Dichten von Planck (A)", "k"), (WB_OWN, WM_OWN, "Dichten aus den Peakhöhen (B)", "C3")]:
        ax.plot(100 * hh, [acoustic(x, b, m)["theta"] for x in hh], color=col, lw=1.6, label=lab)
    ax.axhspan(THETA_FIT[0] - THETA_FIT[1], THETA_FIT[0] + THETA_FIT[1], color="C0", alpha=0.3, label="100 θ* aus Schritt 81")
    ax.axvline(H_A, color="k", ls=":", lw=1)
    ax.axvline(H_B, color="C3", ls=":", lw=1)
    ax.axvspan(H0_SH0ES[0] - H0_SH0ES[1], H0_SH0ES[0] + H0_SH0ES[1], color="C2", alpha=0.2, label="SH0ES")
    ax.set_xlabel("H₀ [km/s/Mpc]")
    ax.set_ylabel(r"$100\,\theta_*$")
    ax.set_title("Bei festen Dichten legt θ* die Hubble-Konstante fest", fontsize=10)
    ax.legend(fontsize=9)
    oms = np.linspace(0.24, 0.40, 17)
    line = np.array([100 * h_from_theta(THETA_FIT[0], WB_OWN, Om=o) for o in oms])
    ax2.plot(oms, line, color="C0", lw=2, label="θ* aus Schritt 81, ω_b aus den Peakhöhen")
    ax2.axvspan(OM_SN[0] - OM_SN[1], OM_SN[0] + OM_SN[1], color="C1", alpha=0.25, label="Ω_m aus Pantheon+")
    ax2.axhspan(H0_SH0ES[0] - H0_SH0ES[1], H0_SH0ES[0] + H0_SH0ES[1], color="C2", alpha=0.25, label="H₀ von SH0ES")
    ax2.errorbar(PLANCK["Om"][0], PLANCK["H0"][0], xerr=PLANCK["Om"][1], yerr=PLANCK["H0"][1], fmt="s", color="k", label="Planck 2018")
    ax2.errorbar(OM_SN[0], H_C, xerr=OM_SN[1], yerr=H_C_ERR, fmt="o", color="C3", ms=7, label="C: Schnittpunkt")
    ax2.set_xlabel(r"$\Omega_m$")
    ax2.set_ylabel("H₀ [km/s/Mpc]")
    ax2.set_title("θ* legt eine Linie in der Ebene von Ω_m und H₀ fest", fontsize=10)
    ax2.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    print(f"A (Dichten von Planck):       H₀ = {H_A:.2f} km/s/Mpc  (Planck selbst {PLANCK['H0'][0]} ± {PLANCK['H0'][1]})")
    print(f"B (Dichten aus Peakhöhen):    H₀ = {H_B:.2f} ± {hb_mc.std():.2f} (stat.) ± {hb_sys:.2f} (Formel)")
    print(f"C (ω_b, Ω_m aus Pantheon+):   H₀ = {H_C:.2f} ± {H_C_ERR:.2f}")
    print(f"Ω_m h³ entlang der Linie: {np.min(oms * (line / 100) ** 3):.4f} bis {np.max(oms * (line / 100) ** 3):.4f} (Planck 0.0963)")
    print(f"mit dem z* von Planck statt der Näherung, Dichten von Planck: H₀ = "
          f"{100 * optimize.brentq(lambda h: acoustic(h, wb0, wm0, zs=PLANCK['zstar'][0])['theta'] - THETA_FIT[0], 0.5, 0.9):.2f}")


def literature():
    """84. Gegen Planck 2018 und SH0ES (Zellen 44 von cosmology_cmbpeaks.ipynb)."""
    global H_A_ERR, H_D, H_D_ERR, _, ax, col, dH_dth, dth, e, fig, i, lab
    global rows, v
    dth = 1e-3
    dH_dth = 100 * (h_from_theta(theta_own[0] + dth, WB_OWN, WM_OWN) - h_from_theta(theta_own[0] - dth, WB_OWN, WM_OWN)) / (2 * dth)
    H_D = 100 * h_from_theta(theta_own[0], WB_OWN, WM_OWN)
    H_A_ERR = abs(100 * h_from_theta(THETA_FIT[0] + THETA_FIT[1], wb0, wm0) - 100 * h_from_theta(THETA_FIT[0] - THETA_FIT[1], wb0, wm0)) / 2
    H_D_ERR = np.sqrt((dH_dth * theta_own[1]) ** 2 + H_B_ERR**2 - (dH_dth * THETA_FIT[1]) ** 2)
    rows = [("D: θ* aus den eigenen Karten, Dichten aus den Peakhöhen", H_D, H_D_ERR, "C3"),
            ("B: θ* aus dem Spektrum, Dichten aus den Peakhöhen", H_B, H_B_ERR, "C3"),
            ("C: θ* und ω_b aus dem Spektrum, Ω_m aus Pantheon+", H_C, H_C_ERR, "C3"),
            ("A: θ* aus dem Spektrum, Dichten von Planck (nur Fehler von θ*)", H_A, H_A_ERR, "C3"),
            ("Planck 2018, TT+lowE", *PLANCK_TT["H0"], "k"),
            ("Planck 2018, TT,TE,EE+lowE+lensing", *PLANCK["H0"], "k"),
            ("SH0ES (Riess et al. 2022)", *H0_SH0ES, "C2"),
            ("Das Hubble-Diagramm (Pantheon+ und SH0ES)", *H0_HD, "C2")]
    fig, ax = plt.subplots(figsize=(12, 5.8))
    for i, (lab, v, e, col) in enumerate(rows):
        ax.errorbar(v, -i, xerr=e, fmt="o", color=col, ms=7, capsize=4)
    ax.set_yticks(-np.arange(len(rows)))
    ax.set_yticklabels([r[0] for r in rows], fontsize=9.5)
    ax.axvspan(H0_SH0ES[0] - H0_SH0ES[1], H0_SH0ES[0] + H0_SH0ES[1], color="C2", alpha=0.15)
    ax.axvspan(PLANCK["H0"][0] - PLANCK["H0"][1], PLANCK["H0"][0] + PLANCK["H0"][1], color="0.5", alpha=0.15)
    ax.set_xlabel("H₀ [km/s/Mpc]")
    ax.set_title("Die Hubble-Konstante von der frühen und von der späten Seite", fontsize=10)
    plt.tight_layout()
    plt.show()

    print("Größe         eigen                          Planck 2018 (TT,TE,EE+lowE+lensing)")
    print(f"100 θ*        {THETA_FIT[0]:.5f} ± {THETA_FIT[1]:.5f} (Schablone)     {PLANCK['theta'][0]} ± {PLANCK['theta'][1]}  (TT+lowE {PLANCK_TT['theta'][0]} ± {PLANCK_TT['theta'][1]})")
    print(f"              {theta_own[0]:.4f} ± {theta_own[1]:.4f} (eigene Karten)")
    print(f"              {THETA_PEAKS[0]:.4f} ± {THETA_PEAKS[1]:.4f} (Abstand der Peaks)")
    print(f"z*            {REF['zs']:.1f} (Näherung)                   {PLANCK['zstar'][0]} ± {PLANCK['zstar'][1]}")
    print(f"r_s [Mpc]     {REF['rs']:.2f} (mit Planck-Dichten)        {PLANCK['rstar'][0]} ± {PLANCK['rstar'][1]}")
    print(f"ω_b           {WB_OWN:.5f} ± {np.hypot(W_MC[:, 0].std(), W_SYS[0]):.5f}                {PLANCK['wb'][0]} ± {PLANCK['wb'][1]}")
    print(f"ω_m           {WM_OWN:.4f} ± {np.hypot(W_MC[:, 1].std(), W_SYS[1]):.4f}                  {PLANCK['wm'][0]} ± {PLANCK['wm'][1]}")
    for lab, v, e, _ in rows[:3]:
        print(f"{lab[:2]} H₀ = {v:.2f} ± {e:.2f}: gegen SH0ES {(H0_SH0ES[0] - v) / np.hypot(e, H0_SH0ES[1]):.1f} σ, "
              f"gegen Planck {(v - PLANCK['H0'][0]) / np.hypot(e, PLANCK['H0'][1]):+.1f} σ")


def what_if_73():
    """85. Was müsste sich ändern, damit 73 herauskommt? (Zellen 47 von cosmology_cmbpeaks.ipynb)."""
    global a, ax, ax2, fig, h73, h_neff, lcdm_sn, lcdm_wm, need_sn, need_wm, neff_73, neffs
    global o, om_cross, om_wm, oms, rs_lcdm, rs_need
    h73 = H0_SH0ES[0] / 100
    oms = np.linspace(0.22, 0.38, 33)
    rs_need, rs_lcdm = [], []
    for o in oms:
        a = acoustic(h73, wb0, o * h73**2)
        rs_lcdm.append(a["rs"])
        rs_need.append(THETA_FIT[0] / 100 * a["dm"])
    rs_need, rs_lcdm = np.array(rs_need), np.array(rs_lcdm)
    om_cross = np.interp(0, rs_lcdm - rs_need, oms)
    need_sn = np.interp(OM_SN[0], oms, rs_need)
    lcdm_sn = np.interp(OM_SN[0], oms, rs_lcdm)
    om_wm = wm0 / h73**2
    need_wm, lcdm_wm = np.interp(om_wm, oms, rs_need), np.interp(om_wm, oms, rs_lcdm)
    neffs = np.linspace(2.6, 4.2, 17)
    h_neff = np.array([100 * h_from_theta(THETA_FIT[0], wb0, wm0, neff=x) for x in neffs])
    neff_73 = np.interp(H0_SH0ES[0], h_neff, neffs)

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.8))
    ax.plot(oms, rs_need, color="C2", lw=2, label="nötig für H₀ = 73 bei gemessenem θ*")
    ax.plot(oms, rs_lcdm, color="k", lw=2, label="ΛCDM für ω_m = Ω_m · 0.73², ω_b von Planck")
    ax.axvspan(OM_SN[0] - OM_SN[1], OM_SN[0] + OM_SN[1], color="C1", alpha=0.25, label="Ω_m aus Pantheon+")
    ax.axvline(om_cross, color="0.5", ls=":", lw=1)
    ax.axvline(om_wm, color="0.5", lw=1.5, label="Ω_m = ω_m(Planck)/0.73²")
    ax.set_xlabel(r"$\Omega_m$")
    ax.set_ylabel(r"Schallhorizont $r_s$ [Mpc]")
    ax.set_title("Wie klein müsste der Schallhorizont für H₀ = 73 sein?", fontsize=10)
    ax.legend(fontsize=9)
    ax2.plot(neffs, h_neff, "o-", color="C3", ms=4, label="H₀ aus θ* (ω_b, ω_c von Planck fest)")
    ax2.axhspan(H0_SH0ES[0] - H0_SH0ES[1], H0_SH0ES[0] + H0_SH0ES[1], color="C2", alpha=0.25, label="SH0ES")
    ax2.axvspan(NEFF_PLANCK[0] - NEFF_PLANCK[1], NEFF_PLANCK[0] + NEFF_PLANCK[1], color="0.5", alpha=0.25,
                label="N_eff von Planck (mit BAO)")
    ax2.axvline(3.046, color="k", ls=":", lw=1)
    ax2.set_xlabel(r"$N_\mathrm{eff}$")
    ax2.set_ylabel("H₀ [km/s/Mpc]")
    ax2.set_title("Mehr Strahlung vor der Rekombination", fontsize=10)
    ax2.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    print(f"H₀ = 73 passt in ΛCDM zu θ* bei Ω_m = {om_cross:.3f} (ω_m = {om_cross * h73**2:.4f}; Planck {PLANCK['wm'][0]})")
    print(f"bei Ω_m = {OM_SN[0]} aus Pantheon+: r_s nötig {need_sn:.1f} Mpc, ΛCDM gibt {lcdm_sn:.1f} Mpc ({100 * (need_sn / lcdm_sn - 1):+.1f} %)")
    print(f"Ω_m = {om_cross:.3f} liegt {(OM_SN[0] - om_cross) / OM_SN[1]:.1f} σ unter Pantheon+")
    print(f"mit ω_m von Planck: Ω_m = {om_wm:.3f} ({(OM_SN[0] - om_wm) / OM_SN[1]:.1f} σ unter Pantheon+), r_s nötig {need_wm:.1f} statt {lcdm_wm:.1f} Mpc ({100 * (need_wm / lcdm_wm - 1):+.1f} %)")
    print(f"Ω_m = {OM_SN[0]} und H₀ = 73 verlangen ω_m = {OM_SN[0] * h73**2:.4f}, {100 * (OM_SN[0] * h73**2 / wm0 - 1):.0f} % mehr als Planck aus den Peakhöhen")
    print(f"N_eff für H₀ = 73: {neff_73:.2f}, also {(neff_73 - NEFF_PLANCK[0]) / NEFF_PLANCK[1]:.1f} σ über dem Wert von Planck; "
          f"r_s dann {acoustic(h73, wb0, wm0, neff=neff_73)['rs']:.1f} Mpc")
