"""Die Dunkelwolke ρ Ophiuchi: Bilder in sechs Bändern, Sternfarben, Extinktionskarte, Rötung gegen Entfernung, Staubtemperatur, Extinktionsgesetz, Masse und Entfernung der Wolke.

Für nebulae.ipynb aus nebulae_dust.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, bands, stars, colors, extinction_map, reddening_distance, dust_temperature, heating, distance_jump, extinction_law, obscuring_vs_emitting, mass, distance_check, sfd.
Downloads und Cache: data/nebulae/ (`nebdata.py`).
"""
import nebdata                                         # zuerst: Cache-Ordner für astropy
import io
import os
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import optimize, special, stats
from scipy.ndimage import map_coordinates
from astropy.io import fits
from astropy.wcs import WCS


def load():
    """Daten (Zellen 4, 6 von nebulae_dust.ipynb)."""
    global ASTRODATA, AV_CLOUD, AV_TAU_DIFFUSE, BANDS, BETA_FIX, BOX, BOX_WIDE, COLS_2MASS, CTRL, C_CGS, DE0, DE_MAP
    global DUST, EBV_CTRL, ESA_TAP, EXT_MAP, GAIA, GRID, HD147889, H_PLANCK, IMG, IRSA_TAP, K_B, K_CMB_TO_MJY
    global MIN_STARS, MU_H, M_H, M_SUN, NH_PER_AV, NPIX_IMG, NPIX_MAP, NU, PC, RA0, RA_MAP, R_JHK
    global SED, SED_ERR, SFD, SIZE, STARS, SURVEYS, TM, TM_CTRL, WMAP, XX, YY, at_map
    global download, fit_jump, fit_sed, fits_ok, irsa_dust, k, mbb, offsets, pixel_of, planck_mjy, rng, sfd_path
    global skyview, tap, to_map, url, xml_ctrl, xml_field
    ASTRODATA = nebdata.DATA


    RA0, DE0, SIZE = 247.0, -24.2, 3.0   # Mitte und Kantenlänge des Feldes [°]: L1688, L1689 und ρ Oph
    NPIX_MAP, NPIX_IMG = 60, 200         # Pixel des Rechengitters (3′) und der Bilder (0.9′)
    CTRL = (241.0, -29.0, 1.0)           # Kontrollfeld mit wenig Staub: Mitte und Radius [°] (Schritt 4)
    R_JHK = {"J": 0.282, "H": 0.175, "K": 0.112}   # A_λ / A_V im nahen Infrarot (Rieke & Lebofsky 1985)
    MIN_STARS = 3                        # mindestens so viele Sterne pro Pixel der Extinktionskarte (Schritt 5)
    BETA_FIX = 1.6                       # Spektralindex des Staubs, wenn er nicht frei ist (Schritt 7)
    K_CMB_TO_MJY = 287.45                # 353 GHz: MJy/sr pro K_CMB (Planck 2013 IX)
    AV_TAU_DIFFUSE = 3.1 * 1.49e4        # A_V / τ353 im diffusen Gas (Planck 2013 XI: E(B−V)/τ353 = 1.49·10⁴)
    NH_PER_AV = 1.87e21                  # Wasserstoffsäule pro A_V [cm⁻² mag⁻¹] (Bohlin et al. 1978, R_V = 3.1)
    MU_H = 1.37                          # Masse pro Wasserstoffatom in Einheiten von m_H (mit Helium)
    AV_CLOUD = 5.0                       # Sterne in Pixeln mit A_V über diesem Wert gelten als "auf der Wolke" (Schritt 6)
    HD147889 = (246.3513, -24.4658)      # B2-Stern am Rand von L1688 (Gaia DR3 6049140417677195136)
    STARS = {"ρ Oph": (246.3963, -23.4473), "HD 147889": HD147889, "22 Sco": (247.5520, -25.1153)}
    rng = np.random.default_rng(42)
    pd.set_option("display.width", 160)
    np.seterr(divide="ignore", invalid="ignore")
    H_PLANCK, K_B, C_CGS, M_H, PC, M_SUN = 6.62607e-27, 1.380649e-16, 2.99792458e10, 1.6726e-24, 3.0857e18, 1.989e33
    DUST = ASTRODATA / "dust"


    def download(urls, path, check=None, timeout=120, rounds=3, pause=10):
        # lädt eine Datei vom ersten Server, der antwortet, und liest sie danach aus dem Cache;
        # SkyView lehnt zu schnelle Anfragen mit einer HTML-Seite ab ("Too Many Processes"), deshalb Pausen
        path = Path(path)
        if path.exists():
            return path
        path.parent.mkdir(parents=True, exist_ok=True)
        for k in range(rounds):
            for url in urls:
                try:
                    with urllib.request.urlopen(url, timeout=timeout) as r:
                        data = r.read()
                except OSError:
                    continue
                if check is None or check(data):
                    path.write_bytes(data)
                    return path
            time.sleep(pause)
        raise OSError(f"Kein Server liefert {path.name}")


    fits_ok = lambda d: d[:6] == b"SIMPLE"


    def skyview(survey, npix):
        url = ("https://skyview.gsfc.nasa.gov/current/cgi/runquery.pl?" +
               urllib.parse.urlencode({"Position": f"{RA0},{DE0}", "Survey": survey, "Pixels": npix, "Size": SIZE,
                                       "Return": "FITS"}))
        h = fits.open(download([url], DUST / f"sv_{survey.replace(' ', '')}_{npix}.fits", fits_ok))[0]
        return h.data.astype(float), WCS(h.header)


    def tap(service, adql, path):
        # ein TAP-Ergebnis als Tabelle; die erste Zeile muss der Spaltenkopf sein, sonst ist es eine Fehlermeldung
        url = service + "?" + urllib.parse.urlencode({"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": adql})
        first = adql.split()[1].rstrip(",").encode()
        return pd.read_csv(download([url], path, check=lambda d: d.startswith(first), timeout=600))


    IRSA_TAP = "https://irsa.ipac.caltech.edu/TAP/sync"
    ESA_TAP = "https://gea.esac.esa.int/tap-server/tap/sync"
    COLS_2MASS = "ra, dec, j_m, j_msigcom, h_m, h_msigcom, k_m, k_msigcom, ph_qual, cc_flg"
    BOX = f"BOX('ICRS', {RA0}, {DE0}, {SIZE}, {SIZE})"

    # Bilder: fein für den Blick, grob (3′) für die Rechnungen
    SURVEYS = {"DSS2 Blue": "DSS2 blau (0.45 µm)", "DSS2 Red": "DSS2 rot (0.65 µm)", "WISE 12": "WISE 12 µm (warmer Staub)",
               "IRIS100": "IRIS 100 µm", "Planck 857 I": "Planck 857 GHz (350 µm)", "Planck 353 I": "Planck 353 GHz (850 µm)"}
    IMG = {s: skyview(s, NPIX_IMG) for s in SURVEYS}
    BANDS = {"IRIS100": 2.998e12, "Planck 857 I": 857e9, "Planck 545 I": 545e9, "Planck 353 I": 353e9}   # Frequenzen [Hz]
    GRID = {s: skyview(s, NPIX_MAP)[0] for s in BANDS}
    WMAP = skyview("Planck 857 I", NPIX_MAP)[1]                          # WCS des Rechengitters
    for k in ("Planck 353 I",):
        GRID[k] = GRID[k] * K_CMB_TO_MJY                                 # K_CMB -> MJy/sr

    # Sterne: 2MASS im Feld und im Kontrollfeld, Gaia mit Extinktion
    TM = tap(IRSA_TAP, f"SELECT {COLS_2MASS} FROM fp_psc WHERE CONTAINS(POINT('ICRS', ra, dec), {BOX}) = 1",
             DUST / "2mass_field.csv")
    TM_CTRL = tap(IRSA_TAP, f"SELECT {COLS_2MASS} FROM fp_psc WHERE CONTAINS(POINT('ICRS', ra, dec), "
                            f"CIRCLE('ICRS', {CTRL[0]}, {CTRL[1]}, {CTRL[2]})) = 1", DUST / "2mass_control.csv")
    BOX_WIDE = f"BOX('ICRS', {RA0}, {DE0}, {SIZE / np.cos(np.radians(DE0)) + 0.1:.3f}, {SIZE + 0.1})"   # bei ESA ohne cos δ
    GAIA = tap(ESA_TAP, "SELECT source_id, ra, dec, parallax, parallax_error, phot_g_mean_mag, bp_rp, ag_gspphot "
                        f"FROM gaiadr3.gaia_source WHERE 1 = CONTAINS(POINT('ICRS', ra, dec), {BOX_WIDE}) "
                        "AND parallax_over_error > 5 AND ag_gspphot IS NOT NULL", DUST / "gaia_field_wide.csv")

    # Staubdienst: Rötung des Kontrollfelds (Schlafly & Finkbeiner) und die Karte von Schlegel et al. als FITS
    def irsa_dust(ra, dec, size, name):
        url = f"https://irsa.ipac.caltech.edu/cgi-bin/DUST/nph-dust?locstr={ra}+{dec}+equ+j2000&regSize={size}"
        return download([url], DUST / name, check=lambda d: b"meanValueSandF" in d).read_text()


    xml_ctrl = irsa_dust(CTRL[0], CTRL[1], 2 * CTRL[2], "irsa_dust_control.xml")
    EBV_CTRL = float(re.search(r"<meanValueSandF>\s*([0-9.]+)", xml_ctrl).group(1))
    xml_field = irsa_dust(RA0, DE0, SIZE, "irsa_dust_field.xml")
    sfd_path = DUST / "sfd_field.fits"
    if not sfd_path.exists():
        url = re.search(r"(https://\S+?p150Dust\.fits)", xml_field).group(1)   # temporärer Link, gilt nur kurz
        download([url], sfd_path, fits_ok)
    SFD = fits.open(sfd_path)[0]

    print(f"2MASS: {len(TM)} Quellen im Feld, {len(TM_CTRL)} im Kontrollfeld (E(B−V) = {EBV_CTRL:.3f} nach Schlafly & Finkbeiner)")
    print(f"Gaia DR3 mit Parallaxe S/N > 5 und A_G: {len(GAIA)} Sterne")
    print("Bilder:", ", ".join(f"{s} {IMG[s][0].shape[0]}²" for s in IMG), f"| Rechengitter {NPIX_MAP}² zu {SIZE * 60 / NPIX_MAP:.0f}′")
    print("Medianwerte im Feld [MJy/sr]:", ", ".join(f"{s} {np.median(v):.1f}" for s, v in GRID.items()))

    YY, XX = np.mgrid[0:NPIX_MAP, 0:NPIX_MAP]
    RA_MAP, DE_MAP = WMAP.pixel_to_world_values(XX, YY)
    EXT_MAP = [SIZE / 2, -SIZE / 2, -SIZE / 2, SIZE / 2]                 # Achsen in Grad relativ zur Mitte, Osten links


    def offsets(ra, dec):
        # Abstand von der Feldmitte [°], Osten positiv
        return (np.asarray(ra) - RA0) * np.cos(np.radians(DE0)), np.asarray(dec) - DE0


    def pixel_of(ra, dec, wcs=WMAP, n=NPIX_MAP):
        x, y = wcs.world_to_pixel_values(np.asarray(ra), np.asarray(dec))
        xi, yi = np.floor(x + 0.5).astype(int), np.floor(y + 0.5).astype(int)
        inside = (xi >= 0) & (xi < n) & (yi >= 0) & (yi < n)
        return xi, yi, inside


    def to_map(ra, dec, values, min_n=MIN_STARS):
        # Median der Werte aller Sterne pro Pixel; Pixel mit weniger als min_n Sternen bleiben leer
        xi, yi, ok = pixel_of(ra, dec)
        df = pd.DataFrame({"x": xi[ok], "y": yi[ok], "v": np.asarray(values)[ok]})
        grp = df.groupby(["y", "x"])["v"]
        med, cnt = grp.median(), grp.size()
        out, n = np.full((NPIX_MAP, NPIX_MAP), np.nan), np.zeros((NPIX_MAP, NPIX_MAP), int)
        for (y, x), v in med.items():
            n[y, x] = cnt[(y, x)]
            if cnt[(y, x)] >= min_n:
                out[y, x] = v
        return out, n


    def at_map(m, ra, dec):
        # Wert einer Karte an Sternorten (NaN außerhalb)
        xi, yi, ok = pixel_of(ra, dec)
        v = np.full(len(xi), np.nan)
        v[ok] = m[yi[ok], xi[ok]]
        return v


    def planck_mjy(nu, T):
        return 2 * H_PLANCK * nu**3 / C_CGS**2 / np.expm1(H_PLANCK * nu / (K_B * T)) * 1e17   # [MJy/sr]


    def mbb(nu, tau353, T, beta):
        # modifizierter Schwarzkörper: I_ν = τ353 (ν/353 GHz)^β B_ν(T)
        return tau353 * (nu / 353e9) ** beta * planck_mjy(nu, T)


    NU = np.array(list(BANDS.values()))
    SED = np.stack([GRID[s] for s in BANDS])                            # 4 × 60 × 60 [MJy/sr]
    SED_ERR = 0.1                                                         # 10 % relativer Fehler je Band (Kalibrierung, Nullpunkt)


    def fit_sed(y, beta=None):
        # τ353, T und β (oder β fest) für eine Intensität y in vier Bändern
        if beta is None:
            f = lambda p: (mbb(NU, 10 ** p[0], p[1], p[2]) - y) / (SED_ERR * y)
            r = optimize.least_squares(f, [-4, 18, 1.6], bounds=([-8, 5, 0.5], [0, 80, 3.5]))
            return 10 ** r.x[0], r.x[1], r.x[2]
        f = lambda p: (mbb(NU, 10 ** p[0], p[1], beta) - y) / (SED_ERR * y)
        r = optimize.least_squares(f, [-4, 18], bounds=([-8, 5], [0, 80]))
        return 10 ** r.x[0], r.x[1], beta


    def fit_jump(A, plx, plx_err, d_grid=np.arange(80, 220, 0.5)):
        # Extinktion A vor und hinter einer dünnen Wolke in der Entfernung d_c:
        # vor der Wolke N(a0, s0), dahinter N(a1, s1), dazu ein gleichverteilter Fremdanteil f;
        # P(Stern vor der Wolke) folgt aus Parallaxe und Fehler
        def nll(th, dc):
            a0, s0, a1, s1, lf = th
            if s0 <= 0.1 or s1 <= 0.1:                                      # GSP-Phot streut mindestens 0.1 mag
                return 1e12
            f = special.expit(lf)
            p_front = stats.norm.cdf((plx - 1000 / dc) / plx_err)
            L = (1 - f) * (p_front * stats.norm.pdf(A, a0, s0) + (1 - p_front) * stats.norm.pdf(A, a1, s1)) + f / 10
            return -np.sum(np.log(L))
        th0, prof = np.array([0.4, 0.2, 3.0, 1.0, -3.0]), []
        for dc in d_grid:                                                  # Profil-Likelihood über d_c, jedes Mal vom selben Start
            r = optimize.minimize(nll, th0, args=(dc,), method="Nelder-Mead", options=dict(maxiter=3000, xatol=1e-4))
            prof.append(r.fun)
        prof = np.array(prof)
        best = d_grid[np.argmin(prof)]
        r = optimize.minimize(nll, th0, args=(best,), method="Nelder-Mead", options=dict(maxiter=5000, xatol=1e-5))
        return dict(d=best, grid=d_grid, prof=prof - prof.min(), a0=r.x[0], s0=r.x[1], a1=r.x[2], s1=r.x[3],
                    frac=special.expit(r.x[4]), n=len(A))


    print(f"Rechengitter: Mitte ({RA0}, {DE0}), {SIZE * 60 / NPIX_MAP:.1f}′ pro Pixel; "
          f"A_V/E(H−K) = {1 / (R_JHK['H'] - R_JHK['K']):.2f}, A_V/E(J−H) = {1 / (R_JHK['J'] - R_JHK['H']):.2f}, "
          f"E(J−H)/E(H−K) = {(R_JHK['J'] - R_JHK['H']) / (R_JHK['H'] - R_JHK['K']):.2f}")


def bands():
    """2. Die Wolke in sechs Bändern (Zellen 8 von nebulae_dust.ipynb)."""
    global ax, axes, dec, fig, hi, img, lo, name, ra, s, title, v
    global x, y
    fig, axes = plt.subplots(2, 3, figsize=(16, 10.5))
    for ax, (s, title) in zip(axes.flat, SURVEYS.items()):
        img = IMG[s][0]
        if s in ("WISE 12", "IRIS100", "Planck 857 I", "Planck 353 I"):
            img = np.log10(np.clip(img, np.nanpercentile(img, 0.5), None))
        lo, hi = np.nanpercentile(img, [1, 99.5])
        ax.imshow(np.clip((img - lo) / (hi - lo), 0, 1), origin="lower", cmap="gray" if "DSS" in s else "inferno",
                  extent=EXT_MAP)
        for name, (ra, dec) in STARS.items():
            x, y = offsets(ra, dec)
            ax.plot(x, y, "o", mfc="none", mec="cyan", ms=11, mew=1.2)
            ax.annotate(name, (x, y), xytext=(6, 6), textcoords="offset points", color="cyan", fontsize=9)
        ax.set_title(title, fontsize=11)
        ax.set_xlabel("Δα cos δ [°] (Osten links)")
        ax.set_ylabel("Δδ [°]")
    fig.suptitle("L1688 und L1689 in ρ Ophiuchi, 3° × 3°", fontsize=12)
    plt.tight_layout()
    plt.show()
    for s in SURVEYS:
        v = IMG[s][0]
        print(f"{s:14s}: Median {np.nanmedian(v):10.3f}, 99.5. Perzentil {np.nanpercentile(v, 99.5):10.3f}")


def stars():
    """3. Sterne in Richtung der Wolke (Zellen 11 von nebulae_dust.ipynb)."""
    global CTRL2M, I857, N2M, NGA, STARS2M, _, ax, axes, bins, clean_2mass, col, ctrl_area
    global dens_ctrl, fig, hi857, idx, im, lab, m, title, xs, ys
    def clean_2mass(t):
        q, c = t["ph_qual"].astype(str), t["cc_flg"].astype(str)
        ok = q.str[1].isin(list("ABC")) & q.str[2].isin(list("ABC")) & (c.str[1:3] == "00")
        ok &= (t["h_msigcom"] < 0.1) & (t["k_msigcom"] < 0.1)
        t = t[ok].copy()
        t["has_j"] = t["ph_qual"].astype(str).str[0].isin(list("ABC")) & (t["j_msigcom"] < 0.1) & (t["cc_flg"].astype(str).str[0] == "0")
        t["jh"], t["hk"] = t["j_m"] - t["h_m"], t["h_m"] - t["k_m"]
        return t


    STARS2M, CTRL2M = clean_2mass(TM), clean_2mass(TM_CTRL)
    _, N2M = to_map(STARS2M["ra"], STARS2M["dec"], np.zeros(len(STARS2M)), min_n=0)
    _, NGA = to_map(GAIA["ra"], GAIA["dec"], np.zeros(len(GAIA)), min_n=0)
    ctrl_area = np.pi * CTRL[2] ** 2 * 3600 / 9                        # Pixel von 3′ × 3′ im Kontrollfeld
    dens_ctrl = len(CTRL2M) / ctrl_area

    fig, axes = plt.subplots(1, 3, figsize=(17, 5))
    for ax, (m, title) in zip(axes[:2], [(N2M, f"2MASS: {len(STARS2M)} Sterne"), (NGA, f"Gaia, Parallaxe S/N > 5: {len(GAIA)} Sterne")]):
        im = ax.imshow(m, origin="lower", cmap="viridis", extent=EXT_MAP)
        plt.colorbar(im, ax=ax, label="Sterne pro Pixel (3′ × 3′)")
        ax.contour(np.log10(GRID["Planck 857 I"]), levels=[2.2], colors="w", linewidths=0.8, extent=EXT_MAP)
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("Δα cos δ [°] (Osten links)")
        ax.set_ylabel("Δδ [°]")
    ax = axes[2]
    I857 = GRID["Planck 857 I"]
    for m, col, lab in [(N2M, "C0", "2MASS"), (NGA, "C1", "Gaia")]:
        bins = np.logspace(np.log10(I857.min()), np.log10(I857.max()), 15)
        idx = np.digitize(I857.ravel(), bins)
        xs = [np.median(I857.ravel()[idx == k]) for k in range(1, len(bins)) if (idx == k).sum() > 5]
        ys = [np.mean(m.ravel()[idx == k]) for k in range(1, len(bins)) if (idx == k).sum() > 5]
        ax.plot(xs, ys, "o-", color=col, label=lab)
    ax.axhline(dens_ctrl, color="C0", ls=":", label=f"2MASS im Kontrollfeld ({dens_ctrl:.0f})")
    ax.set_xscale("log")
    ax.set_xlabel("Planck 857 GHz [MJy/sr]")
    ax.set_ylabel("Sterne pro Pixel")
    ax.set_title("Wo der Staub strahlt, fehlen Sterne", fontsize=10)
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    print(f"2MASS nach Qualitätsschnitt: {len(STARS2M)} von {len(TM)} im Feld, {len(CTRL2M)} von {len(TM_CTRL)} im Kontrollfeld; "
          f"mit J: {STARS2M['has_j'].mean():.0%}")
    print(f"Sterne pro Pixel: 2MASS Median {np.median(N2M):.0f} (Kontrollfeld {dens_ctrl:.1f}), leere Pixel {np.sum(N2M == 0)}; "
          f"Gaia Median {np.median(NGA):.0f}, leere Pixel {np.sum(NGA == 0)}")
    hi857 = I857 > np.percentile(I857, 95)
    print(f"In den 5 % hellsten Planck-Pixeln: 2MASS {N2M[hi857].mean():.1f}, Gaia {NGA[hi857].mean():.1f} Sterne pro Pixel")


def colors():
    """4. Farben ohne und mit Staub (Zellen 14 von nebulae_dust.ipynb)."""
    global HK0, JH0, SIG_HK, SIG_JH, av, av_ctrl, ax, axes, cj, df, fig, k_hk
    global k_jh, title
    k_hk, k_jh = 1 / (R_JHK["H"] - R_JHK["K"]), 1 / (R_JHK["J"] - R_JHK["H"])
    av_ctrl = 3.1 * EBV_CTRL
    cj = CTRL2M[CTRL2M["has_j"]]
    HK0 = CTRL2M["hk"].median() - av_ctrl / k_hk                         # Eigenfarben ohne Staub
    JH0 = cj["jh"].median() - av_ctrl / k_jh
    SIG_HK = 1.4826 * np.median(np.abs(CTRL2M["hk"] - CTRL2M["hk"].median()))
    SIG_JH = 1.4826 * np.median(np.abs(cj["jh"] - cj["jh"].median()))

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharex=True, sharey=True)
    for ax, (df, title) in zip(axes, [(cj, f"Kontrollfeld ({len(cj)} Sterne mit J)"), (STARS2M[STARS2M["has_j"]], "Feld der Wolke")]):
        ax.hist2d(df["hk"], df["jh"], bins=[np.arange(-0.3, 2.5, 0.025), np.arange(0, 4.0, 0.04)], cmap="Greys", cmin=1,
                  norm=plt.matplotlib.colors.LogNorm())
        ax.plot(HK0, JH0, "r*", ms=14, label=f"Eigenfarbe: H−K = {HK0:.3f}, J−H = {JH0:.3f}")
        for av in (5, 10, 20):
            ax.annotate("", xy=(HK0 + av / k_hk, JH0 + av / k_jh), xytext=(HK0, JH0),
                        arrowprops=dict(arrowstyle="->", color="C3", lw=1.5))
            ax.text(HK0 + av / k_hk + 0.02, JH0 + av / k_jh, f"A_V = {av}", color="C3", fontsize=9)
        ax.set_xlabel("H − K [mag]")
        ax.set_title(title, fontsize=10)
    axes[0].set_ylabel("J − H [mag]")
    axes[0].legend(fontsize=9, loc="lower right")
    plt.tight_layout()
    plt.show()

    print(f"Kontrollfeld: H−K Median {CTRL2M['hk'].median():.3f}, J−H Median {cj['jh'].median():.3f}; "
          f"abzüglich A_V = {av_ctrl:.2f}: H−K₀ = {HK0:.3f} ± {SIG_HK:.3f}, J−H₀ = {JH0:.3f} ± {SIG_JH:.3f} (Streuung)")
    print(f"Streuung in A_V pro Stern aus der Eigenfarbe: H−K {k_hk * SIG_HK:.2f} mag, J−H {k_jh * SIG_JH:.2f} mag")


def extinction_map():
    """5. Die Extinktionskarte (Zellen 17 von nebulae_dust.ipynb)."""
    global AV_MAP, N_MAP, av_star, ax, axes, dec, fig, good, im, logI, name, ra
    global rho, x, y
    def av_star(t):
        # Extinktion pro Stern aus H−K und J−H, gewichtet mit Messfehler und Streuung der Eigenfarben
        av_hk = k_hk * (t["hk"] - HK0)
        var_hk = k_hk**2 * (SIG_HK**2 + t["h_msigcom"] ** 2 + t["k_msigcom"] ** 2)
        av_jh = k_jh * (t["jh"] - JH0)
        var_jh = k_jh**2 * (SIG_JH**2 + t["j_msigcom"] ** 2 + t["h_msigcom"] ** 2)
        w_hk, w_jh = 1 / var_hk, np.where(t["has_j"], 1 / var_jh, 0.0)
        av = (w_hk * av_hk + w_jh * np.nan_to_num(av_jh)) / (w_hk + w_jh)
        return av, 1 / np.sqrt(w_hk + w_jh)


    STARS2M["AV"], STARS2M["AV_err"] = av_star(STARS2M)
    AV_MAP, N_MAP = to_map(STARS2M["ra"], STARS2M["dec"], STARS2M["AV"])
    good = np.isfinite(AV_MAP)
    logI = np.log10(GRID["Planck 857 I"])

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    ax = axes[0]
    im = ax.imshow(AV_MAP, origin="lower", cmap="magma", extent=EXT_MAP, vmin=0, vmax=np.nanpercentile(AV_MAP, 99.5))
    plt.colorbar(im, ax=ax, label="A_V [mag]")
    ax.imshow(np.where(good, np.nan, 1.0), origin="lower", cmap="Blues", vmin=0, vmax=1.5, extent=EXT_MAP, alpha=0.9)
    for name, (ra, dec) in STARS.items():
        x, y = offsets(ra, dec)
        ax.plot(x, y, "o", mfc="none", mec="cyan", ms=10)
    ax.set_title(f"Extinktion aus 2MASS (blau: weniger als {MIN_STARS} Sterne)", fontsize=10)
    ax.set_xlabel("Δα cos δ [°] (Osten links)")
    ax.set_ylabel("Δδ [°]")
    ax = axes[1]
    ax.scatter(GRID["Planck 857 I"][good], AV_MAP[good], s=4, alpha=0.5)
    ax.set_xscale("log")
    ax.set_xlabel("Planck 857 GHz [MJy/sr]")
    ax.set_ylabel("A_V aus 2MASS [mag]")
    ax.set_title("Staub, der verdeckt, gegen Staub, der strahlt", fontsize=10)
    plt.tight_layout()
    plt.show()

    rho = stats.spearmanr(GRID["Planck 857 I"][good], AV_MAP[good]).statistic
    print(f"{len(STARS2M)} Sterne, A_V pro Stern Median {STARS2M['AV'].median():.2f}, Fehler pro Stern Median {STARS2M['AV_err'].median():.2f} mag")
    print(f"Karte: {good.sum()} von {good.size} Pixeln mit ≥ {MIN_STARS} Sternen; A_V Median {np.nanmedian(AV_MAP):.2f}, "
          f"95. Perzentil {np.nanpercentile(AV_MAP, 95):.1f}, Maximum {np.nanmax(AV_MAP):.1f} mag; Rangkorrelation mit Planck 857 {rho:.2f}")
    print(f"Leere Pixel liegen bei Planck 857 im Median bei {np.median(GRID['Planck 857 I'][~good]):.0f} MJy/sr "
          f"(Feld {np.median(GRID['Planck 857 I']):.0f})")


def reddening_distance():
    """6. Rötung gegen Entfernung (Zellen 20 von nebulae_dust.ipynb)."""
    global EDGES, ax, axes, col, fig, g, lab, m, mid, off, ok, on
    global s, table, xi, yi
    GAIA["d"] = 1000 / (GAIA["parallax"] + 0.017)
    GAIA["plx"] = GAIA["parallax"] + 0.017
    GAIA["AV_map"] = at_map(AV_MAP, GAIA["ra"], GAIA["dec"])
    xi, yi, ok = pixel_of(GAIA["ra"], GAIA["dec"])
    GAIA["in_field"] = ok
    GAIA["empty"] = ok & np.isnan(GAIA["AV_map"])
    on = GAIA["in_field"] & ((GAIA["AV_map"] > AV_CLOUD) | GAIA["empty"])
    off = GAIA["in_field"] & (GAIA["AV_map"] < 2)
    EDGES = [0, 100, 120, 130, 135, 140, 150, 170, 200, 300, 500, 1000, 3000]

    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
    ax = axes[0]
    ax.scatter(GAIA.loc[off, "d"], GAIA.loc[off, "ag_gspphot"], s=2, c="0.6", alpha=0.4, label=f"neben der Wolke, A_V < 2 ({off.sum()})")
    ax.scatter(GAIA.loc[on, "d"], GAIA.loc[on, "ag_gspphot"], s=8, c="C3", label=f"auf der Wolke ({on.sum()})")
    ax.set_xscale("log")
    ax.set_xlim(60, 4000)
    ax.set_xlabel("Entfernung 1/ϖ [pc]")
    ax.set_ylabel("A_G (Gaia GSP-Phot) [mag]")
    ax.set_title("Extinktion jedes Sterns gegen seine Entfernung", fontsize=10)
    ax.legend(fontsize=9)
    ax = axes[1]
    for m, col, lab in [(off, "0.4", "neben der Wolke"), (on, "C3", "auf der Wolke")]:
        s = GAIA[m]
        g = s.groupby(pd.cut(s["d"], EDGES), observed=False)["ag_gspphot"]
        mid = [np.sqrt(max(a.left, 60) * a.right) for a in g.median().index]
        ax.plot(mid, g.median().values, "o-", color=col, label=lab)
    ax.set_xscale("log")
    ax.set_xlabel("Entfernung [pc]")
    ax.set_ylabel("Median A_G [mag]")
    ax.set_title("Median in Entfernungsintervallen", fontsize=10)
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    table = pd.DataFrame({lab: GAIA[m].groupby(pd.cut(GAIA.loc[m, "d"], EDGES), observed=False)["ag_gspphot"].agg(["count", "median"])
                          .apply(lambda r: f"{int(r['count'])}: {r['median']:.2f}" if r["count"] else "–", axis=1)
                          for m, lab in [(on, "auf der Wolke (Zahl: A_G)"), (off, "daneben (Zahl: A_G)")]})
    print(table.to_string())


def dust_temperature():
    """7. Wie warm ist der Staub? (Zellen 23 von nebulae_dust.ipynb)."""
    global BETA, EXAMPLES, TAU, TEMP, TEMP_FIX, ax, cmap, col, core, dec, dense, edge
    global fig, hi, hot, i, im, j, k, lab, lo, m, name, nu_plot
    global ox, oy, ra, title, x, y
    TAU, TEMP, BETA = (np.full((NPIX_MAP, NPIX_MAP), np.nan) for _ in range(3))
    TEMP_FIX = np.full((NPIX_MAP, NPIX_MAP), np.nan)
    for i in range(NPIX_MAP):
        for j in range(NPIX_MAP):
            TAU[i, j], TEMP[i, j], BETA[i, j] = fit_sed(SED[:, i, j])
            TEMP_FIX[i, j] = fit_sed(SED[:, i, j], beta=BETA_FIX)[1]
    core = np.unravel_index(np.argmax(TAU), TAU.shape)
    hot = np.unravel_index(np.argmax(TEMP), TEMP.shape)
    edge = (3, NPIX_MAP - 4)
    EXAMPLES = {"dichtester Pixel": core, "wärmster Pixel": hot, "Feldrand": edge}

    fig = plt.figure(figsize=(16, 10))
    ax = fig.add_subplot(2, 3, (1, 3))
    nu_plot = np.logspace(np.log10(200e9), np.log10(5e12), 200)
    for (lab, (i, j)), col in zip(EXAMPLES.items(), ["C0", "C3", "0.4"]):
        ax.errorbar(NU / 1e9, SED[:, i, j], yerr=SED_ERR * SED[:, i, j], fmt="o", color=col)
        ax.plot(nu_plot / 1e9, mbb(nu_plot, TAU[i, j], TEMP[i, j], BETA[i, j]), color=col,
                label=f"{lab}: T = {TEMP[i, j]:.1f} K, β = {BETA[i, j]:.2f}, τ353 = {TAU[i, j]:.1e}")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks([300, 500, 1000, 2000, 3000], labels=["300", "500", "1000", "2000", "3000"])
    ax.xaxis.set_minor_formatter(plt.NullFormatter())
    ax.set_xlabel("Frequenz [GHz]")
    ax.set_ylabel("Intensität [MJy/sr]")
    ax.set_title("Spektren dreier Pixel mit angepasstem modifiziertem Schwarzkörper", fontsize=10)
    ax.legend(fontsize=9)
    for k, (m, title, cmap, lab) in enumerate([(TEMP, "Temperatur", "coolwarm", "T [K]"),
                                               (np.log10(TAU), "optische Tiefe", "magma", "log₁₀ τ353"),
                                               (BETA, "Spektralindex", "viridis", "β")]):
        ax = fig.add_subplot(2, 3, 4 + k)
        lo, hi = np.percentile(m, [1, 99])
        im = ax.imshow(m, origin="lower", cmap=cmap, extent=EXT_MAP, vmin=lo, vmax=hi)
        plt.colorbar(im, ax=ax, label=lab)
        for name, (ra, dec) in STARS.items():
            x, y = offsets(ra, dec)
            ax.plot(x, y, "o", mfc="none", mec="k", ms=10)
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("Δα cos δ [°] (Osten links)")
    plt.tight_layout()
    plt.show()

    dense = TAU > np.percentile(TAU, 95)
    print(f"T: Median {np.median(TEMP):.1f} K (5 % bis 95 %: {np.percentile(TEMP, 5):.1f} bis {np.percentile(TEMP, 95):.1f}), "
          f"β: Median {np.median(BETA):.2f} ({np.percentile(BETA, 5):.2f} bis {np.percentile(BETA, 95):.2f}); "
          f"mit β = {BETA_FIX}: T Median {np.median(TEMP_FIX):.1f} K")
    print(f"In den 5 % dichtesten Pixeln: T {np.median(TEMP[dense]):.1f} K, sonst {np.median(TEMP[~dense]):.1f} K; "
          f"Rangkorrelation T–β {stats.spearmanr(TEMP.ravel(), BETA.ravel()).statistic:+.2f}")
    for lab, (i, j) in EXAMPLES.items():
        ox, oy = offsets(RA_MAP[i, j], DE_MAP[i, j])
        print(f"{lab:16s}: Δ = ({ox:+.2f}°, {oy:+.2f}°), "
              f"T = {TEMP[i, j]:.1f} K, β = {BETA[i, j]:.2f}, τ353 = {TAU[i, j]:.2e}")


def heating():
    """8. Ein Stern heizt den Staub (Zellen 26 von nebulae_dust.ipynb)."""
    global R_ARC, T_B, ax, axes, cov, dx, dy, excess, fig, fit_r, heat_model, med
    global n_b, near, p, pc_per_arcmin, perr, pos, r_ring, rr, slope, sx, sy
    dx, dy = offsets(RA_MAP, DE_MAP)
    sx, sy = offsets(*HD147889)
    R_ARC = np.hypot(dx - sx, dy - sy) * 60                              # projizierter Abstand [′]
    n_b = 4 + BETA_FIX
    T_B = np.median(TEMP_FIX[(R_ARC >= 30) & (R_ARC < 40)])             # Hintergrund aus dem Ring 30′ bis 40′
    fit_r = (R_ARC > 5) & (R_ARC < 30)                                   # innerhalb von 5′ verschmiert der Planck-Strahl


    def heat_model(r, r0, n):
        return (T_B**n_b * (1 + (r0 / r) ** n)) ** (1 / n_b)


    p, cov = optimize.curve_fit(heat_model, R_ARC[fit_r], TEMP_FIX[fit_r], p0=[8, 2])
    perr = np.sqrt(np.diag(cov))
    r_ring = np.arange(0, 45, 3)
    med = [np.median(TEMP_FIX[(R_ARC >= a) & (R_ARC < a + 3)]) for a in r_ring]
    near = R_ARC < 45
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
    ax = axes[0]
    ax.scatter(R_ARC[near], TEMP_FIX[near], s=5, alpha=0.3, label="Pixel")
    ax.plot(r_ring + 1.5, med, "ko-", label="Median im Ring")
    rr = np.linspace(1, 45, 200)
    ax.plot(rr, heat_model(rr, *p), "C3-", lw=2, label=f"Modell: r₀ = {p[0]:.1f}′, n = {p[1]:.2f}")
    ax.axhline(T_B, color="0.4", ls=":", label=f"Hintergrund T_b = {T_B:.1f} K")
    ax.axvspan(0, 5, color="0.9", label="verschmiert (Strahl 5′)")
    ax.set_ylim(15, 40)
    ax.set_xlabel("Abstand von HD 147889 [′]")
    ax.set_ylabel("Staubtemperatur (β = 1.6) [K]")
    ax.set_title("Temperatur gegen Abstand", fontsize=10)
    ax.legend(fontsize=9)
    ax = axes[1]
    excess = TEMP_FIX**n_b - T_B**n_b
    pos = fit_r & (excess > 0)
    ax.loglog(R_ARC[pos], excess[pos], ".", ms=4, alpha=0.5)
    ax.loglog(rr[rr > 5], T_B**n_b * (p[0] / rr[rr > 5]) ** p[1], "C3-", label=f"∝ r^−{p[1]:.2f} (Fit)")
    ax.loglog(rr[rr > 5], T_B**n_b * (p[0] / rr[rr > 5]) ** 2, "k:", label="∝ r^−2 (Erwartung)")
    ax.set_xlabel("Abstand [′]")
    ax.set_ylabel("T^(4+β) − T_b^(4+β) [K^5.6]")
    ax.set_title("Der Beitrag des Sterns allein, 5′ bis 30′", fontsize=10)
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    pc_per_arcmin = 136 * np.pi / (180 * 60)
    slope = np.polyfit(np.log10(R_ARC[pos]), np.log10(excess[pos]), 1)[0]
    print(f"T_b = {T_B:.2f} K (Ring 30′ bis 40′); Fit 5′ bis 30′: r₀ = {p[0]:.1f} ± {perr[0]:.1f}′ ({p[0] * pc_per_arcmin:.2f} pc), "
          f"n = {p[1]:.2f} ± {perr[1]:.2f} (erwartet 2); Gerade im log-log-Bild: Steigung {slope:.2f}")
    print(f"Ringmediane: 0–3′ {med[0]:.1f} K, 9–12′ {med[3]:.1f} K, 18–21′ {med[6]:.1f} K, 30–33′ {med[10]:.1f} K; "
          f"wärmster Pixel {np.nanmax(TEMP_FIX):.1f} K in {R_ARC.ravel()[np.nanargmax(TEMP_FIX)]:.1f}′ Abstand")


def distance_jump():
    """9. Die Entfernung aus dem Sprung (Zellen 29 von nebulae_dust.ipynb)."""
    global D_JUMP, D_JUMP_ERR, JUMP, ax, axes, b, boot, cloud, dd, fig, inside, n_front
    global s
    cloud = GAIA[on & (GAIA["d"] < 3000)]
    JUMP = fit_jump(cloud["ag_gspphot"].values, cloud["plx"].values, cloud["parallax_error"].values)
    boot = []
    for b in range(30):
        s = cloud.sample(len(cloud), replace=True, random_state=b)
        boot.append(fit_jump(s["ag_gspphot"].values, s["plx"].values, s["parallax_error"].values,
                             d_grid=np.arange(JUMP["d"] - 15, JUMP["d"] + 15, 0.5))["d"])
    boot = np.array(boot)
    D_JUMP, D_JUMP_ERR = JUMP["d"], np.std(boot)
    inside = JUMP["grid"][JUMP["prof"] < 0.5]

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    ax = axes[0]
    ax.plot(JUMP["grid"], JUMP["prof"], "C0-")
    ax.axhline(0.5, color="k", ls=":")
    ax.axvline(137.3, color="C3", ls="--", label="VLBI, L1688: 137.3 pc")
    ax.set_ylim(0, 40)
    ax.set_xlim(115, 155)
    ax.set_xlabel("Entfernung der Staubschicht d_c [pc]")
    ax.set_ylabel("Δ ln L")
    ax.set_title(f"Profil-Likelihood: d_c = {D_JUMP:.2f} pc", fontsize=10)
    ax.legend(fontsize=9)
    ax = axes[1]
    ax.scatter(cloud["d"], cloud["ag_gspphot"], s=8, c="C3", alpha=0.6, label=f"Sterne auf der Wolke ({len(cloud)})")
    dd = np.linspace(60, 3000, 400)
    ax.plot(dd, np.where(dd < D_JUMP, JUMP["a0"], JUMP["a1"]), "k-", lw=2, label="Modell (Mittelwerte)")
    ax.fill_between(dd, np.where(dd < D_JUMP, JUMP["a0"] - JUMP["s0"], JUMP["a1"] - JUMP["s1"]),
                    np.where(dd < D_JUMP, JUMP["a0"] + JUMP["s0"], JUMP["a1"] + JUMP["s1"]), color="k", alpha=0.15)
    ax.set_xscale("log")
    ax.set_xlim(60, 3000)
    ax.set_xlabel("Entfernung 1/ϖ [pc]")
    ax.set_ylabel("A_G [mag]")
    ax.set_title("Sterne und angepasstes Stufenmodell", fontsize=10)
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    print(f"{JUMP['n']} Sterne: d_c = {D_JUMP:.2f} pc (Profil 1σ: {inside.min():.2f} bis {inside.max():.2f}, Bootstrap ± {D_JUMP_ERR:.2f} pc)")
    print(f"davor A_G = {JUMP['a0']:.2f} ± {JUMP['s0']:.2f}, dahinter {JUMP['a1']:.2f} ± {JUMP['s1']:.2f} mag, Fremdanteil {JUMP['frac']:.1%}")
    n_front = int(np.sum(cloud["d"] < D_JUMP))
    print(f"Sterne vor der Schicht: {n_front}; nächster geröteter Stern (A_G > 2): {cloud.loc[cloud['ag_gspphot'] > 2, 'd'].min():.1f} pc")


def extinction_law():
    """10. Das Extinktionsgesetz im Infraroten (Zellen 32 von nebulae_dust.ipynb)."""
    global DELTA, SLOPE, SLOPE_ERR, SLOPE_PA, ax, boot, deming_slope, fig, keep, principal_slope, red, resid
    global s1, sel, slope_rl, x
    red = STARS2M[STARS2M["has_j"] & STARS2M["AV"].between(3, 25)]


    def principal_slope(x, y):
        c = np.cov(x, y)
        w, v = np.linalg.eigh(c)
        return v[1, 1] / v[0, 1]


    def deming_slope(x, y, delta):
        # Gerade mit Fehlern in x und y, delta = Varianz(y-Fehler) / Varianz(x-Fehler)
        sxx, syy, sxy = np.var(x), np.var(y), np.cov(x, y, bias=True)[0, 1]
        return (syy - delta * sxx + np.sqrt((syy - delta * sxx) ** 2 + 4 * delta * sxy**2)) / (2 * sxy)


    DELTA = (SIG_JH**2 + np.median(red["j_msigcom"] ** 2 + red["h_msigcom"] ** 2)) / \
            (SIG_HK**2 + np.median(red["h_msigcom"] ** 2 + red["k_msigcom"] ** 2))
    s1 = deming_slope(red["hk"], red["jh"], DELTA)
    resid = (red["jh"] - JH0) - s1 * (red["hk"] - HK0)
    keep = np.abs(resid - resid.median()) < 3 * 1.4826 * np.median(np.abs(resid - resid.median()))
    sel = red[keep]
    SLOPE = deming_slope(sel["hk"], sel["jh"], DELTA)
    SLOPE_PA = principal_slope(sel["hk"], sel["jh"])                    # Hauptachse ohne Fehlergewichtung, zum Vergleich
    boot = [deming_slope(*sel.sample(len(sel), replace=True, random_state=b)[["hk", "jh"]].values.T, DELTA) for b in range(200)]
    SLOPE_ERR = np.std(boot)
    slope_rl = (R_JHK["J"] - R_JHK["H"]) / (R_JHK["H"] - R_JHK["K"])

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(red["hk"], red["jh"], s=3, c="0.6", label=f"3 < A_V < 25 ({len(red)})")
    ax.scatter(sel["hk"], sel["jh"], s=3, c="C0", label=f"nach 3σ-Schnitt ({len(sel)})")
    x = np.linspace(HK0, red["hk"].max(), 50)
    ax.plot(x, JH0 + SLOPE * (x - HK0), "C3-", lw=2, label=f"Deming: Steigung {SLOPE:.3f} ± {SLOPE_ERR:.3f}")
    ax.plot(x, JH0 + slope_rl * (x - HK0), "k--", label=f"Rieke & Lebofsky 1985: {slope_rl:.2f}")
    ax.plot(x, JH0 + SLOPE_PA * (x - HK0), "C2:", label=f"Hauptachse ohne Gewichtung: {SLOPE_PA:.2f}")
    ax.set_xlabel("H − K [mag]")
    ax.set_ylabel("J − H [mag]")
    ax.set_title("Rötungsvektor in L1688", fontsize=10)
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    print(f"Varianzverhältnis der Fehler δ = {DELTA:.2f}; erster Fit {s1:.3f}, nach Schnitt ({len(sel)} von {len(red)}) "
          f"{SLOPE:.3f} ± {SLOPE_ERR:.3f}; Hauptachse ohne Gewichtung {SLOPE_PA:.3f}; Rieke & Lebofsky {slope_rl:.3f}")
    print(f"Entfernt (vor allem Infrarotexzess): {len(red) - len(sel)} Sterne, davon unter der Geraden {np.sum(~keep & (resid < 0))}")


def obscuring_vs_emitting():
    """11. Staub, der verdeckt, gegen Staub, der leuchtet (Zellen 35 von nebulae_dust.ipynb)."""
    global AV_PER_TAU, AV_TAU_MAP, ax, axes, fig, hi, lo, m, ratio, sc, t, use
    use = (N_MAP >= 5) & np.isfinite(AV_MAP) & (AV_MAP > 0.5)
    ratio = AV_MAP[use] / TAU[use]
    AV_PER_TAU = np.median(ratio)
    AV_TAU_MAP = AV_PER_TAU * TAU                                       # Extinktion aus τ353, ohne Lücken
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
    ax = axes[0]
    ax.scatter(TAU[use], AV_MAP[use], s=4, alpha=0.4)
    t = np.logspace(np.log10(TAU[use].min()), np.log10(TAU[use].max()), 50)
    ax.plot(t, AV_TAU_DIFFUSE * t, "k--", label=f"diffuses Gas (Planck): {AV_TAU_DIFFUSE:.2e}")
    ax.plot(t, AV_PER_TAU * t, "C3-", label=f"Median hier: {AV_PER_TAU:.2e}")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("τ353")
    ax.set_ylabel("A_V aus 2MASS [mag]")
    ax.set_title(f"{use.sum()} Pixel mit ≥ 5 Sternen", fontsize=10)
    ax.legend(fontsize=9)
    ax = axes[1]
    sc = ax.scatter(TEMP[use], ratio, c=AV_MAP[use], s=5, cmap="magma", vmax=12)
    plt.colorbar(sc, ax=ax, label="A_V [mag]")
    ax.axhline(AV_TAU_DIFFUSE, color="k", ls="--")
    ax.set_yscale("log")
    ax.set_xlabel("Staubtemperatur [K]")
    ax.set_ylabel("A_V / τ353")
    ax.set_title("Verhältnis gegen Temperatur", fontsize=10)
    plt.tight_layout()
    plt.show()

    print(f"A_V/τ353: Median {AV_PER_TAU:.3g} (16 % bis 84 %: {np.percentile(ratio, 16):.3g} bis {np.percentile(ratio, 84):.3g}), "
          f"diffus {AV_TAU_DIFFUSE:.3g}: {AV_PER_TAU / AV_TAU_DIFFUSE - 1:+.0%}")
    for lo, hi in [(0.5, 3), (3, 6), (6, 10), (10, 40)]:
        m = use & (AV_MAP >= lo) & (AV_MAP < hi)
        if m.any():
            print(f"A_V {lo:4.1f} bis {hi:2d}: {m.sum():4d} Pixel, A_V/τ353 {np.median(AV_MAP[m] / TAU[m]):.3g}, T {np.median(TEMP[m]):.1f} K")
    print(f"Rangkorrelation Verhältnis–Temperatur {stats.spearmanr(TEMP[use], ratio).statistic:+.2f}; "
          f"A_V aus τ353: Maximum {AV_TAU_MAP.max():.0f} mag (2MASS: {np.nanmax(AV_MAP):.0f})")


def mass():
    """12. Die Masse der Wolke (Zellen 38 von nebulae_dust.ipynb)."""
    global AV_BEST, A_2M, D_CLOUD, M_2M, M_TAU, ax, axes, fig, k, mass_per_mag, pix_cm, t
    global thresholds
    D_CLOUD = D_JUMP                                                    # Entfernung aus Schritt 9 [pc]
    pix_cm = np.radians(SIZE / NPIX_MAP) * D_CLOUD * PC
    mass_per_mag = MU_H * M_H * NH_PER_AV * pix_cm**2 / M_SUN           # Sonnenmassen pro Pixel und Magnitude A_V
    AV_BEST = np.where(np.isfinite(AV_MAP), AV_MAP, AV_TAU_MAP)
    thresholds = np.arange(1, 21)
    M_2M = np.array([np.sum(AV_BEST[AV_BEST > t]) * mass_per_mag for t in thresholds])
    M_TAU = np.array([np.sum(AV_TAU_MAP[AV_TAU_MAP > t]) * mass_per_mag for t in thresholds])
    A_2M = np.array([np.sum(AV_BEST > t) for t in thresholds]) * (pix_cm / PC) ** 2

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    ax = axes[0]
    ax.semilogy(thresholds, M_2M, "o-", label="2MASS (Lücken aus τ353)")
    ax.semilogy(thresholds, M_TAU, "s--", label="nur τ353")
    ax.axvline(7, color="k", ls=":")
    ax.set_xlabel("Schwelle A_V [mag]")
    ax.set_ylabel("Masse über der Schwelle [M☉]")
    ax.set_title(f"Masse in {D_CLOUD:.0f} pc Entfernung", fontsize=10)
    ax.legend(fontsize=9)
    ax = axes[1]
    ax.semilogy(thresholds, A_2M, "o-")
    ax.axvline(7, color="k", ls=":")
    ax.set_xlabel("Schwelle A_V [mag]")
    ax.set_ylabel("Fläche über der Schwelle [pc²]")
    ax.set_title("Fläche", fontsize=10)
    plt.tight_layout()
    plt.show()

    print(f"Ein Pixel: {pix_cm / PC:.3f} pc Kantenlänge, {mass_per_mag:.3f} M☉ pro Magnitude A_V")
    for t in (1, 3, 7, 15):
        k = t - 1
        print(f"A_V > {t:2d}: 2MASS {M_2M[k]:7.0f} M☉ auf {A_2M[k]:5.1f} pc², nur τ {M_TAU[k]:7.0f} M☉")
    print(f"Anteil der Masse über A_V = 7 an der über A_V = 1: {M_2M[6] / M_2M[0]:.0%}; ganzes Feld {np.sum(AV_BEST) * mass_per_mag:.0f} M☉")


def distance_check():
    """13. Die Entfernung gegen VLBI und Hipparcos (Zellen 41 von nebulae_dust.ipynb)."""
    global CHECKS, D_SYS, LIT, ax, d, e, fig, i, items, k, lab, m
    global s, v
    LIT = {"VLBI, L1688 (Ortiz-León et al. 2017)": (137.3, 1.2), "VLBI, L1689 (Ortiz-León et al. 2017)": (147.3, 3.4),
           "Hipparcos, Sprung (Lombardi et al. 2008)": (119.0, 6.0)}
    CHECKS = {}
    for lab, m in [("A_V > 3 statt 5", GAIA["in_field"] & ((GAIA["AV_map"] > 3) | GAIA["empty"])),
                   ("A_V > 8 statt 5", GAIA["in_field"] & ((GAIA["AV_map"] > 8) | GAIA["empty"])),
                   ("Westhälfte (Δα < 0, mit L1688)", on & (offsets(GAIA["ra"], GAIA["dec"])[0] < 0)),
                   ("Osthälfte (Δα > 0, mit L1689)", on & (offsets(GAIA["ra"], GAIA["dec"])[0] > 0))]:
        s = GAIA[m & (GAIA["d"] < 3000)]
        CHECKS[lab] = fit_jump(s["ag_gspphot"].values, s["plx"].values, s["parallax_error"].values,
                               d_grid=np.arange(100, 180, 0.5))["d"]
    s = cloud
    CHECKS["ohne Nullpunkt"] = fit_jump(s["ag_gspphot"].values, s["parallax"].values, s["parallax_error"].values,
                                        d_grid=np.arange(100, 180, 0.5))["d"]
    D_SYS = np.std([v for k, v in CHECKS.items() if "Osten" not in k and "Westen" not in k] + [D_JUMP])

    fig, ax = plt.subplots(figsize=(10, 5))
    items = [("Gaia-Sprung (dieses Notebook)", (D_JUMP, np.hypot(D_JUMP_ERR, D_SYS)))] + list(LIT.items()) + \
            [(f"  Prüfung: {k}", (v, 0)) for k, v in CHECKS.items()]
    for i, (lab, (d, e)) in enumerate(items):
        ax.errorbar(d, -i, xerr=e, fmt="o" if "Prüfung" not in lab else "x", color="C3" if i == 0 else ("k" if "Prüfung" not in lab else "0.5"),
                    capsize=3)
    ax.set_yticks([-i for i in range(len(items))])
    ax.set_yticklabels([lab for lab, _ in items], fontsize=9)
    ax.set_xlabel("Entfernung [pc]")
    ax.set_title("Entfernung von ρ Ophiuchi", fontsize=10)
    plt.tight_layout()
    plt.show()

    print(f"Gaia-Sprung: {D_JUMP:.1f} ± {D_JUMP_ERR:.1f} (Bootstrap) ± {D_SYS:.1f} (Schnitte, Nullpunkt) pc")
    for k, v in CHECKS.items():
        print(f"  {k:24s}: {v:6.1f} pc")
    for k, (d, e) in LIT.items():
        print(f"{k:42s}: {d:6.1f} ± {e:.1f} pc, Unterschied {D_JUMP - d:+.1f} pc")


def sfd():
    """14. Die Extinktion gegen die Staubkarte von Schlegel, Finkbeiner & Davis (Zellen 44 von nebulae_dust.ipynb)."""
    global SFD_AV, ax, axes, dec, fig, hi, i, im, j, lo, m, name
    global px, py, q, ra, use, wsfd, x, y
    wsfd = WCS(SFD.header)
    px, py = wsfd.world_to_pixel_values(RA_MAP, DE_MAP)
    SFD_AV = 3.1 * map_coordinates(SFD.data.astype(float), [py, px], order=1, cval=np.nan)
    use = (N_MAP >= 5) & np.isfinite(AV_MAP) & (AV_MAP > 0.5) & np.isfinite(SFD_AV)
    q = SFD_AV[use] / AV_MAP[use]

    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
    ax = axes[0]
    im = ax.imshow(np.log10(SFD_AV / AV_BEST), origin="lower", cmap="RdBu_r", vmin=-1, vmax=1, extent=EXT_MAP)
    plt.colorbar(im, ax=ax, label="log₁₀(A_V SFD / A_V dieses Notebooks)")
    for name, (ra, dec) in STARS.items():
        x, y = offsets(ra, dec)
        ax.plot(x, y, "o", mfc="none", mec="k", ms=10)
        ax.annotate(name, (x, y), xytext=(6, 6), textcoords="offset points", fontsize=9)
    ax.set_title("Wo SFD zu viel (rot) und zu wenig (blau) Staub annimmt", fontsize=10)
    ax.set_xlabel("Δα cos δ [°] (Osten links)")
    ax.set_ylabel("Δδ [°]")
    ax = axes[1]
    ax.scatter(TEMP[use], q, s=5, alpha=0.5)
    ax.axhline(1, color="k", lw=1)
    ax.axhline(1 / 0.86, color="k", ls=":", label="Nacheichung 0.86 (Schlafly & Finkbeiner)")
    ax.set_yscale("log")
    ax.set_xlabel("Staubtemperatur aus Schritt 7 [K]")
    ax.set_ylabel("A_V (SFD) / A_V (2MASS)")
    ax.set_title("Verhältnis gegen Temperatur", fontsize=10)
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    print(f"{use.sum()} Pixel: SFD/2MASS Median {np.median(q):.2f} (16 % bis 84 %: {np.percentile(q, 16):.2f} bis {np.percentile(q, 84):.2f}); "
          f"Rangkorrelation mit T {stats.spearmanr(TEMP[use], q).statistic:+.2f}")
    for lo, hi in [(15, 19), (19, 21), (21, 23), (23, 40)]:
        m = (TEMP[use] >= lo) & (TEMP[use] < hi)
        if m.any():
            print(f"T {lo} bis {hi} K: {m.sum():4d} Pixel, SFD/2MASS {np.median(q[m]):.2f}")
    print(f"Pixel ohne SFD-Wert (Rand des Ausschnitts): {np.sum(~np.isfinite(SFD_AV))}")
    i, j = np.unravel_index(np.nanargmax(SFD_AV), SFD_AV.shape)
    print(f"Größtes A_V in SFD: {SFD_AV[i, j]:.0f} mag bei T = {TEMP[i, j]:.1f} K, {R_ARC[i, j]:.1f}′ von HD 147889; "
          f"2MASS/τ dort {AV_BEST[i, j]:.1f} mag")
