"""Planetarische Nebel: Bilder, Kataloge, Gaia-Entfernungen, Rötung, Alter, Zanstra-Temperaturen, HR-Diagramm der Zentralsterne, [O III]-Leuchtkraftfunktion und Entfernung von M 31.

Für nebulae.ipynb aus nebulae_planetary.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, images, catalogs, distances, reddening, ages, zanstra_h, zanstra_he, hr_diagram, core_masses, brightest_oiii, m31_nebulae, luminosity_function, literature, m31_distance.
Downloads und Cache: data/nebulae/ (`nebdata.py`).
"""
import nebdata                                         # zuerst: Cache-Ordner für astropy
import io
import os
import re
import urllib.request
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.path as mpath
from scipy import integrate, optimize
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter1d
from astropy.io import fits


def load():
    """Daten (Zellen 4, 6, 8 von nebulae_planetary.ipynb)."""
    global ASTRODATA, A_B, A_EFF, BELOW, C89, CW, C_BULGE_MAX, C_CGS, EBV_M31, FNU_V0, HA_HB, H_PLANCK
    global K, KM, K_B, LAM, LAM_V, LINE, LOGT, L_SUN, L_plateau, M, M06, M5007_LIM
    global M_CORE, M_STAR_LIT, NU_H, NU_HE2, NU_V, PC, PLX_ZP, PS1, PYNEB, R0_PC, REL_MIN, RUWE_MAX
    global R_V, SH_H, SH_HE, SIGMA_SB, SIG_BULGE, SIG_C89, SIG_M06, SNR_PLX, TRACKS, T_NEB, V84, VIZIER
    global VW, WEID, YEAR, ZR, Z_TRACKS, alpha_B, deredden, df, download, fit_pnlf, fits_ok, g
    global j_rec, k_ccm, lightest, luminosity, name, nu_of, photon_flux, planck_nu, pnlf_pdf, ps1_color, rng, track_mass
    global vizier_ok, vizier_table, zanstra_T, zanstra_ratio
    ASTRODATA = nebdata.DATA


    SNR_PLX = 5.0          # Mindest-S/N der Parallaxe (Schritt 44)
    PLX_ZP = -0.017        # Nullpunkt der Gaia-Parallaxen [mas]: wahre = gemessene − PLX_ZP (Lindegren et al. 2021)
    RUWE_MAX = 1.4         # darüber ist die Astrometrie eines Einzelsterns unzuverlässig
    REL_MIN = 0.8          # Mindestzuverlässigkeit der Zuordnung Gaia-Stern = Zentralstern (Chornay & Walton 2021)
    R_V = 3.1              # Staubgesetz von Cardelli, Clayton & Mathis (1989) mit R_V = A_V / E(B−V) (Schritt 45)
    T_NEB = 1.0e4          # Elektronentemperatur der Nebel [K] für die Rekombinationskoeffizienten (Schritt 47)
    LAM_V = 5480.0         # effektive Wellenlänge des V-Filters [Å]
    FNU_V0 = 3.63e-20      # F_ν eines Sterns mit V = 0 [erg s⁻¹ cm⁻² Hz⁻¹] (Bessell et al. 1998)
    Z_TRACKS = 0.016       # Metallizität der Entwicklungswege (Vassiliadis & Wood 1994), etwa solar
    M_CORE = {1.0: 0.569, 1.5: 0.597, 2.0: 0.633, 2.5: 0.677, 3.5: 0.754, 5.0: 0.900}   # Anfangs- -> Kernmasse [M☉]
    R0_PC = 8178.0         # Entfernung zum Galaktischen Zentrum [pc] (GRAVITY Collaboration 2019) (Schritt 51)
    C_BULGE_MAX = 1.5      # nur Bulge-Nebel mit mäßiger Rötung, c(Hβ) < 1.5 (Schritt 51)
    SIG_BULGE = 0.3        # Streuung von M5007 im Bulge [mag]: Rötungsfehler und Tiefe des Bulge
    M_STAR_LIT = -4.53     # Abbruchhelligkeit der PNLF, an Cepheiden geeicht (Ciardullo 2012)
    EBV_M31 = 0.057        # Vordergrundrötung vor M 31 (Schlafly & Finkbeiner 2011, Mittel 2.5° bis 3.3° um M 31)
    SIG_C89, SIG_M06 = 0.07, 0.15   # Messfehler von m5007 bei Ciardullo et al. und Merrett et al. [mag] (Schritt 52)
    M5007_LIM = {"Ciardullo 1989": 22.0, "Merrett 2006": 22.5}   # Grenze der Vollständigkeit [mag] (Schritt 53)
    rng = np.random.default_rng(42)
    pd.set_option("display.width", 160)
    np.seterr(divide="ignore", invalid="ignore")      # log von fehlenden Werten -> NaN

    H_PLANCK, C_CGS, K_B, SIGMA_SB = 6.62607e-27, 2.99792458e10, 1.380649e-16, 5.6704e-5
    L_SUN, PC, YEAR, KM = 3.828e33, 3.0857e18, 3.156e7, 1e5
    NU_H = 13.598 * 1.602177e-12 / H_PLANCK          # Ionisationskante des Wasserstoffs (91.2 nm) [Hz]
    NU_HE2 = 4 * NU_H                                # Ionisationskante von He⁺ (54.4 eV, 22.8 nm) [Hz]

    VIZIER = ["https://vizier.cds.unistra.fr", "https://vizier.cfa.harvard.edu", "http://vizier.nao.ac.jp"]
    PYNEB = "https://raw.githubusercontent.com/Morisset/PyNeb_devel/master/pyneb/atomic_data_fits/"
    PS1 = "https://ps1images.stsci.edu/cgi-bin/"


    def download(urls, path, check=None, timeout=60, rounds=2):
        # lädt eine Datei vom ersten Server, der antwortet, und liest sie danach aus dem Cache;
        # die Spiegel fallen manchmal für Minuten aus, deshalb wird die Liste zweimal durchlaufen
        path = Path(path)
        if path.exists():
            return path
        path.parent.mkdir(parents=True, exist_ok=True)
        for url in urls * rounds:
            try:
                with urllib.request.urlopen(url, timeout=timeout) as r:
                    data = r.read()
            except OSError:
                continue
            if check is None or check(data):
                path.write_bytes(data)
                return path
        raise OSError(f"Kein Server liefert {path.name}")


    def vizier_ok(d):
        # eine Strichzeile unter dem Spaltenkopf und danach Daten; ein gestörter Spiegel liefert nur Fehlermeldungen
        lines = d.splitlines()
        dash = [i for i, line in enumerate(lines) if line.startswith(b"---")]
        return bool(dash) and any(line.strip() and not line.startswith(b"#") for line in lines[dash[0] + 1:])


    def vizier_table(source, numeric=()):
        # eine VizieR-Tabelle als Text; Zahlenspalten werden umgewandelt, leere Felder werden NaN
        query = f"/viz-bin/asu-tsv?-source={source}&-out.max=unlimited&-out.all"
        p = download([m + query for m in VIZIER], ASTRODATA / "vizier" / (source.replace("/", "_") + ".tsv"), vizier_ok,
                     timeout=30)
        lines = [l for l in p.read_text().splitlines(keepends=True) if l.strip() and not l.startswith("#")]
        df = pd.read_csv(io.StringIO("".join(lines)), sep="\t", skiprows=[1, 2], dtype=str)
        df.columns = [c.strip() for c in df.columns]
        df = df.apply(lambda s: s.str.strip())
        for c in numeric:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        return df


    def ps1_color(ra, dec, size_arcsec, path, stretch=""):
        # Farbbild aus i, r, g (rot, grün, blau), serverseitig auf höchstens 800 Pixel verkleinert
        lst = download([f"{PS1}ps1filenames.py?ra={ra}&dec={dec}&filters=gri"], path.with_suffix(".txt"))
        files = pd.read_csv(lst, sep=r"\s+").set_index("filter")["filename"]
        size = int(size_arcsec / 0.25)                                       # 0.25″ pro Pixel
        url = (f"{PS1}fitscut.cgi?ra={ra}&dec={dec}&size={size}&output_size={min(size, 800)}&format=jpg"
               f"&red={files['i']}&green={files['r']}&blue={files['g']}{stretch}")
        return mpimg.imread(download([url], path, check=lambda d: d[:3] == b"\xff\xd8\xff", timeout=300))


    # Zentralsterne in Gaia EDR3
    CW = vizier_table("J/A+A/656/A110/tablea1", ["RA_ICRS", "DE_ICRS", "Rel", "BP-RP", "Gmag", "plx", "e_plx", "RUWE",
                                                 "pnRad", "rcomb", "b_rcomb", "B_rcomb"])
    # Strasbourg-ESO-Katalog: Namen, Durchmesser, Hβ-Flüsse, Linien, Geschwindigkeiten, Zentralsterne
    V84 = {"main": vizier_table("V/84/main"),
           "diam": vizier_table("V/84/diam", ["oDiam"]),
           "hbeta": vizier_table("V/84/hbeta", ["log(Fbeta)"]),
           "intens": vizier_table("V/84/intens", ["I4686", "I5007", "I6563"]),
           "vel": vizier_table("V/84/vel", ["ExpVel"]),
           "cstar": vizier_table("V/84/cstar", ["Vmag"])}
    # Entwicklungswege, Literaturwerte der Zentralsterne, Nebel in M 31
    VW = vizier_table("J/ApJS/92/125/table3", ["M", "Z", "Time", "log(Teff)", "log(L)"])
    WEID = (vizier_table("J/A+A/640/A10/ph-para", ["logTeff", "logL"])
            .merge(vizier_table("J/A+A/640/A10/catalog")[["PNG", "SpType1"]].drop_duplicates("PNG"), on="PNG", how="left")
            .drop_duplicates("PNG"))
    C89 = vizier_table("J/ApJ/339/53/table2", ["PN", "m5007", "e_m5007"])
    M06 = vizier_table("J/MNRAS/369/120/table3", ["m5007", "HV", "C89"])
    # Rekombination im Fall B (Storey & Hummer 1995), Zeile 0 = Elektronendichte 100 cm⁻³
    fits_ok = lambda d: d[:6] == b"SIMPLE"
    SH_H = fits.open(download([PYNEB + "h_i_rec_SH95.fits"], ASTRODATA / "pyneb" / "h_i_rec_SH95.fits", fits_ok))[1].data
    SH_HE = fits.open(download([PYNEB + "he_ii_rec_SH95.fits"], ASTRODATA / "pyneb" / "he_ii_rec_SH95.fits", fits_ok))[1].data

    for name, df in [("Chornay & Walton 2021", CW), ("Strasbourg-ESO: Nebel", V84["main"]),
                     ("  mit Durchmesser", V84["diam"].dropna(subset=["oDiam"])), ("  mit Hβ-Fluss", V84["hbeta"]),
                     ("  mit Linienstärken", V84["intens"]), ("  mit Geschwindigkeiten", V84["vel"]),
                     ("  mit Zentralstern", V84["cstar"]), ("Vassiliadis & Wood 1994", VW), ("Weidmann et al. 2020", WEID),
                     ("Ciardullo et al. 1989", C89), ("Merrett et al. 2006", M06)]:
        print(f"{name:26s} {len(df):5d} Zeilen")

    def k_ccm(lam, Rv=R_V):
        # Staubgesetz von Cardelli, Clayton & Mathis (1989) im Optischen: k(λ) = A_λ / E(B−V), λ in Å
        x = 1e4 / np.asarray(lam, float)
        y = x - 1.82
        a = 1 + 0.17699 * y - 0.50447 * y**2 - 0.02427 * y**3 + 0.72085 * y**4 + 0.01979 * y**5 - 0.77530 * y**6 + 0.32999 * y**7
        b = 1.41338 * y + 2.28305 * y**2 + 1.07233 * y**3 - 5.38434 * y**4 - 0.62251 * y**5 + 5.30260 * y**6 - 2.09002 * y**7
        return Rv * a + b


    LAM = {"Hb": 4861.33, "Ha": 6562.80, "O3": 5006.84, "He2": 4685.68, "V": LAM_V}
    K = {k: float(k_ccm(v)) for k, v in LAM.items()}
    nu_of = lambda lam: C_CGS / (lam * 1e-8)


    def j_rec(tab, trans, T):
        # Emissivität 4πj / (n_e n_ion) [erg cm³ s⁻¹] bei n_e = 100 cm⁻³; "4_2" = Hβ, "3_2" = Hα, He II "4_3" = 4686
        return np.interp(T, tab["TEMP"][0], tab[trans][0])


    def alpha_B(T):
        # Rekombinationskoeffizient des Wasserstoffs im Fall B [cm³ s⁻¹] (Draine 2011, Gl. 14.6)
        t4 = T / 1e4
        return 2.54e-13 * t4 ** (-0.8163 - 0.0208 * np.log(t4))


    HA_HB = j_rec(SH_H, "3_2", T_NEB) / j_rec(SH_H, "4_2", T_NEB)                 # Balmer-Dekrement ohne Staub
    A_EFF = {"H": j_rec(SH_H, "4_2", T_NEB) / (H_PLANCK * nu_of(LAM["Hb"])),       # effektive Rekombination in Hβ
             "He": j_rec(SH_HE, "4_3", T_NEB) / (H_PLANCK * nu_of(LAM["He2"]))}    # ... und in He II 4686
    A_B = {"H": alpha_B(T_NEB), "He": 2 * alpha_B(T_NEB / 4)}                      # He⁺ ist wasserstoffähnlich mit Z = 2
    LINE = {"H": (nu_of(LAM["Hb"]), NU_H), "He": (nu_of(LAM["He2"]), NU_HE2)}       # Linienfrequenz, Ionisationskante
    NU_V = nu_of(LAM_V)


    def deredden(df):
        # Rötung aus Hα/Hβ und entrötete Flüsse [erg s⁻¹ cm⁻²]
        df = df.copy()
        df["EBV"] = (np.log10(df["I6563"] / 100 / HA_HB) / (0.4 * (K["Hb"] - K["Ha"]))).clip(lower=0)
        df["c"] = 0.4 * K["Hb"] * df["EBV"]                                        # c(Hβ) = log10 der Schwächung von Hβ
        df["F_Hb"] = 10 ** df["log(Fbeta)"] * 10 ** df["c"]
        df["F_O3"] = df["I5007"] / 100 * df["F_Hb"] * 10 ** (0.4 * df["EBV"] * (K["O3"] - K["Hb"]))
        df["F_He2"] = df["I4686"] / 100 * df["F_Hb"] * 10 ** (0.4 * df["EBV"] * (K["He2"] - K["Hb"]))
        df["m5007"] = -2.5 * np.log10(df["F_O3"]) - 13.74                           # [O III]-Helligkeit (Jacoby 1989)
        return df


    def planck_nu(nu, T):
        return 2 * H_PLANCK * nu**3 / C_CGS**2 / np.expm1(H_PLANCK * nu / (K_B * T))


    def photon_flux(T, nu0):
        # ∫ B_ν / ν dν von nu0 bis unendlich [erg s⁻¹ cm⁻² sr⁻¹]; geteilt durch h ist das die Zahl ionisierender Photonen
        x0 = H_PLANCK * nu0 / (K_B * T)
        I = integrate.quad(lambda x: x * x / np.expm1(x), x0, x0 + 60)[0]
        return 2 * H_PLANCK / C_CGS**2 * (K_B * T / H_PLANCK) ** 3 * I


    def zanstra_ratio(T, ion):
        # erwartetes F(Linie) / F_ν(V) [Hz] für einen Schwarzkörper der Temperatur T
        nu_line, nu0 = LINE[ion]
        return nu_line * A_EFF[ion] / A_B[ion] * photon_flux(T, nu0) / planck_nu(NU_V, T)


    LOGT = np.linspace(np.log10(1.2e4), np.log10(6e5), 500)
    ZR = {ion: np.log10([zanstra_ratio(10**t, ion) for t in LOGT]) for ion in ("H", "He")}   # steigt monoton mit T


    def zanstra_T(ratio, ion):
        # Umkehrung: die Temperatur, bei der das erwartete Verhältnis dem gemessenen gleicht
        return 10 ** np.interp(np.log10(np.asarray(ratio, float)), ZR[ion], LOGT, left=np.nan, right=np.nan)


    def luminosity(fnu_v, d_pc, T):
        # Leuchtkraft [L☉] eines Schwarzkörpers mit dem Fluss F_ν(V) in der Entfernung d
        return 4 * np.pi * (d_pc * PC) ** 2 * fnu_v * SIGMA_SB * T**4 / np.pi / planck_nu(NU_V, T) / L_SUN


    print(f"k(λ) = A_λ/E(B−V): Hβ {K['Hb']:.2f}, Hα {K['Ha']:.2f}, 5007 {K['O3']:.2f}, 4686 {K['He2']:.2f}, V {K['V']:.2f}")
    print(f"Hα/Hβ ohne Staub = {HA_HB:.3f};  α_eff(Hβ)/α_B = {A_EFF['H'] / A_B['H']:.3f};  "
          f"α_eff(4686)/α_B(He⁺) = {A_EFF['He'] / A_B['He']:.3f}")

    TRACKS = VW[VW["Z"] == Z_TRACKS].copy()
    TRACKS["Mc"] = TRACKS["M"].map(M_CORE)
    lightest = TRACKS[TRACKS["Mc"] == TRACKS["Mc"].min()].sort_values("Time")
    # Die Bucht innerhalb der leichtesten Spur (waagrechter Ast oben, Abkühlungsast links, zum Anfang geschlossen):
    # Sterne dort sind leichter als 0.569 M☉, oder ihre Leuchtkraft ist unterschätzt
    BELOW = mpath.Path(lightest[["log(Teff)", "log(L)"]].values)


    def track_mass(logT, logL):
        # Kernmasse und Alter seit log T = 4 durch lineare Interpolation zwischen den Spuren
        pts = TRACKS[["log(Teff)", "log(L)"]].values
        xy = np.column_stack([logT, logL])
        mc = griddata(pts, TRACKS["Mc"].values, xy)
        age = 10 ** griddata(pts, np.log10(TRACKS["Time"].clip(lower=10)).values, xy)
        under =np.array([BELOW.contains_point(p) for p in xy])
        mc[under], age[under] = np.nan, np.nan
        return mc, age, under


    def pnlf_pdf(m, m_star, sig, frac, lo, hi, dm=0.005):
        # Wahrscheinlichkeitsdichte der Helligkeiten in [lo, hi]: PNLF gefaltet mit dem Messfehler sig plus Fremdanteil frac
        g = np.arange(lo - 2, hi + 2, dm)
        p = np.where(g > m_star, np.exp(0.307 * g) * (1 - np.exp(3 * (m_star - g))), 0.0)
        if sig > 0:
            p = gaussian_filter1d(p, sig / dm, mode="constant")
        inside = (g >= lo) & (g <= hi)
        p = p / np.trapz(p[inside], g[inside])
        return (1 - frac) * np.interp(m, g, p) + frac / (hi - lo)


    def fit_pnlf(m, sig, lo, hi, start, free_frac=True):
        # Maximum Likelihood für m* (und den Fremdanteil); Fehler aus der Profil-Likelihood (Δ ln L = 0.5)
        m = m[(m >= lo) & (m <= hi)]
        if not free_frac:                       # ohne Fremdanteil muss die Kante unter dem hellsten Objekt liegen
            start = min(start, m.min() - 4 * sig - 0.05)
        to_frac = lambda t: 1 / (1 + np.exp(-t)) if free_frac else 0.0
        nll = lambda th: -np.sum(np.log(pnlf_pdf(m, th[0], sig, to_frac(th[1]), lo, hi)))
        best = optimize.minimize(nll, [start, -4.0], method="Nelder-Mead", options=dict(xatol=1e-4, fatol=1e-4))
        grid = np.arange(best.x[0] - 1.0, best.x[0] + 1.0, 0.01)
        prof = np.array([optimize.minimize_scalar(lambda t: nll([g, t]), bounds=(-12, 3), method="bounded").fun
                         if free_frac else nll([g, 0.0]) for g in grid])
        prof -= min(prof.min(), best.fun)
        inside = grid[prof < 0.5]
        return dict(m_star=best.x[0], frac=to_frac(best.x[1]), n=len(m), lo=inside.min(), hi=inside.max(),
                    grid=grid, prof=prof)


    print(f"Spuren bei Z = {Z_TRACKS}: Anfangsmassen {sorted(TRACKS['M'].unique())} M☉, "
          f"Kernmassen {sorted(TRACKS['Mc'].unique())} M☉, {len(TRACKS)} Punkte")
    for M, g in TRACKS.groupby("M"):
        L_plateau = 10 ** g["log(L)"].max()
        print(f"  M_i = {M:.1f}: Plateau log L = {np.log10(L_plateau):.2f}, Kernmasse aus L = 59250 (M_c − 0.495): "
              f"{0.495 + L_plateau / 59250:.3f} (Tabelle {M_CORE[M]:.3f})")


def images():
    """42. Vier Nebel im Bild (Zellen 10 von nebulae_planetary.ipynb)."""
    global SHOW, ax, axes, bar, cw_by_png, d, fig, h, img, name, png, r
    global rows, size, stretch
    SHOW = [("NGC 7662", "106.5-17.6", 60, "&asinh=True&autoscale=99.99"),   # Name, PNG, Bildgröße [″], Streckung
            ("M 57 (NGC 6720)", "063.1+13.9", 150, ""),
            ("M 27 (NGC 6853)", "060.8-03.6", 540, ""),
            ("Abell 39", "047.0+42.4", 240, "")]
    cw_by_png = CW.set_index("PNG")
    fig, axes = plt.subplots(1, 4, figsize=(18, 5))
    rows = []
    for ax, (name, png, size, stretch) in zip(axes, SHOW):
        r = cw_by_png.loc[png]
        img = ps1_color(r["RA_ICRS"], r["DE_ICRS"], size, ASTRODATA / "pn" / f"ps1_{png}.jpg", stretch)
        h = size / 2
        ax.imshow(img, extent=[h, -h, -h, h])                       # Norden oben, Osten links
        ax.plot(0, 0, "o", mfc="none", mec="yellow", ms=16, mew=1.3)
        ax.add_patch(plt.Circle((0, 0), r["pnRad"], fill=False, ls="--", color="white", lw=0.8))
        d = 1000 / (r["plx"] - PLX_ZP)
        bar = 0.1 * 206265 / d                                      # 0.1 pc in Bogensekunden
        ax.plot([0.9 * h, 0.9 * h - bar], [-0.85 * h] * 2, color="white", lw=2.5)
        ax.text(0.9 * h - bar / 2, -0.78 * h, "0.1 pc", color="white", ha="center", fontsize=9)
        ax.set_title(f"{name}\nd = {d:.0f} pc, Radius {r['pnRad']:.0f}″", fontsize=10)
        ax.set_xlabel("Δα cos δ [″] (Osten links)")
        ax.set_ylabel("Δδ [″]")
        rows.append(dict(Nebel=name, PNG=png, G=r["Gmag"], Parallaxe_mas=r["plx"], SN=r["plx"] / r["e_plx"], d_pc=d,
                         Radius_as=r["pnRad"], Radius_pc=r["pnRad"] / 206265 * d))
    fig.suptitle("Vier Planetarische Nebel in Pan-STARRS (i, r, g); gelber Kreis: Zentralstern nach Gaia, gestrichelt: Radius nach HASH",
                 fontsize=11)
    plt.tight_layout()
    plt.show()
    print(pd.DataFrame(rows).to_string(index=False, float_format=lambda x: f"{x:.2f}"))


def catalogs():
    """43. Kataloge und Auswahl (Zellen 13 von nebulae_planetary.ipynb)."""
    global ALL, GAIA, S, _, ax, ax2, cstar, fig, funnel, g, i, in_v84
    global lb, lbg, lines, main, n, s_, saturated, sc, vel
    main = V84["main"][["PNG", "Name"]].copy()
    lb = main["PNG"].str.extract(r"^(\d{3}\.\d)([+-]\d{2}\.\d)$").astype(float)
    main["l"] = np.where(lb[0] > 180, lb[0] - 360, lb[0])
    main["b"] = lb[1]
    lines = V84["intens"][V84["intens"]["LineRef"] == "b"].copy()      # Linien relativ zu Hβ = 100
    saturated = lines["n_I5007"] == "*"
    lines.loc[saturated, "I5007"] *= 2.98                               # 5007 gesättigt: der Katalog gibt 4959 an
    cstar = V84["cstar"][V84["cstar"]["l_Vmag"] != ">"]                 # nur gemessene V, keine Grenzen
    vel = V84["vel"][V84["vel"]["l_ExpVel"] == ""]                      # nur gemessene Geschwindigkeiten
    ALL = (main.merge(V84["diam"][["PNG", "oDiam"]], on="PNG", how="left")
               .merge(V84["hbeta"][["PNG", "log(Fbeta)"]], on="PNG", how="left")
               .merge(lines[["PNG", "I4686", "I5007", "I6563"]], on="PNG", how="left")
               .merge(cstar[["PNG", "Vmag", "Quality"]], on="PNG", how="left")
               .merge(vel[["PNG", "ExpVel"]], on="PNG", how="left"))
    ALL = deredden(ALL)                                                  # Rötung und entrötete Flüsse (Schritt 45)

    GAIA = CW[["PNG", "Name", "RA_ICRS", "DE_ICRS", "Rel", "Gmag", "plx", "e_plx", "RUWE", "pnRad", "rcomb"]].copy()
    GAIA = GAIA.rename(columns={"Name": "Name_HASH"})
    GAIA["snr"] = GAIA["plx"] / GAIA["e_plx"]
    GAIA["sure"] = (GAIA["Rel"] > REL_MIN) & (GAIA["RUWE"] < RUWE_MAX)
    GAIA["good"] = GAIA["sure"] & (GAIA["snr"] > SNR_PLX)
    lbg = GAIA["PNG"].str.extract(r"^(\d{3}\.\d)([+-]\d{2}\.\d)$").astype(float)
    GAIA["l"] = np.where(lbg[0] > 180, lbg[0] - 360, lbg[0])
    GAIA["b"] = lbg[1]
    S = GAIA[GAIA["good"]].drop(columns=["l", "b"]).merge(ALL, on="PNG", how="left")
    S["Name"] = S["Name"].fillna(S["Name_HASH"])
    in_v84 = S["I6563"].notna() & S["log(Fbeta)"].notna()
    funnel = [("HASH-Nebel mit Gaia-Kandidat", len(CW)),
              (f"Zuordnung sicher (> {REL_MIN}), RUWE < {RUWE_MAX}", int(GAIA["sure"].sum())),
              (f"Parallaxe S/N > {SNR_PLX:.0f}", int(GAIA["good"].sum())),
              ("+ Hβ-Fluss und Hα/Hβ", int(in_v84.sum())),
              ("+ [O III] 5007", int((in_v84 & S["I5007"].notna()).sum())),
              ("+ V des Zentralsterns", int((in_v84 & S["Vmag"].notna()).sum())),
              ("+ He II 4686", int((in_v84 & S["Vmag"].notna() & S["I4686"].notna()).sum())),
              ("Radius und Expansionsgeschw.", int((S["pnRad"].notna() & S["ExpVel"].notna()).sum()))]

    fig = plt.figure(figsize=(15, 5.2))
    ax = fig.add_subplot(1, 2, 1, projection="aitoff")
    ax.scatter(-np.radians(GAIA["l"]), np.radians(GAIA["b"]), s=2, c="0.7", label=f"alle {len(GAIA)} HASH-Nebel mit Gaia-Kandidat")
    g = GAIA[GAIA["good"]]
    sc = ax.scatter(-np.radians(g["l"]), np.radians(g["b"]), s=10, c=np.log10(1000 / (g["plx"] - PLX_ZP)), cmap="viridis",
                    label=f"{len(g)} mit Parallaxe S/N > {SNR_PLX:.0f}")
    plt.colorbar(sc, ax=ax, shrink=0.6, label="log₁₀(Entfernung / pc)")
    ax.set_xticklabels([f"{t}°" for t in [150, 120, 90, 60, 30, 0, 330, 300, 270, 240, 210]], fontsize=7)
    ax.grid(alpha=0.3)
    ax.set_title("Galaktische Koordinaten (Zentrum in der Mitte, l wächst nach links)", fontsize=10, pad=22)
    ax.legend(loc="lower right", fontsize=8, bbox_to_anchor=(1.05, -0.2))
    ax2 = fig.add_subplot(1, 2, 2)
    ax2.barh(range(len(funnel))[::-1], [n for _, n in funnel], color=["0.6"] * 3 + ["C0"] * 4 + ["C1"])
    ax2.set_yticks(range(len(funnel))[::-1])
    ax2.set_yticklabels([s for s, _ in funnel], fontsize=9)
    for i, (_, n) in enumerate(funnel):
        ax2.text(n + 15, len(funnel) - 1 - i, str(n), va="center", fontsize=9)
    ax2.set_xlabel("Zahl der Nebel")
    ax2.set_title("Von allen Nebeln zur Arbeitsstichprobe", fontsize=10)
    plt.tight_layout()
    plt.show()
    for s_, n in funnel:
        print(f"{s_:38s} {n:5d}")
    print(f"Gesättigtes 5007 durch 2.98 × 4959 ersetzt: {saturated.sum()} Nebel im ganzen Katalog")
    print(f"Anteil mit |b| < 10°: alle {np.mean(np.abs(GAIA['b']) < 10):.0%}, Arbeitsstichprobe {np.mean(np.abs(g['b']) < 10):.0%}")


def distances():
    """44. Entfernungen aus Gaia (Zellen 16 von nebulae_planetary.ipynb)."""
    global ax, axes, col, df, e, fig, hi_q, k, lab, ls, mid_q, ok
    global q, sure, v, x
    S["d"] = 1000 / (S["plx"] - PLX_ZP)
    sure = GAIA[GAIA["sure"]].copy()
    sure["d_inv"] = 1000 / (sure["plx"] - PLX_ZP)
    hi_q = sure[sure["snr"] > SNR_PLX]
    mid_q = sure[(sure["snr"] > 2) & (sure["snr"] <= SNR_PLX)]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.2))
    ax = axes[0]
    ok = sure["plx"] > 0
    ax.scatter(sure.loc[ok, "e_plx"], sure.loc[ok, "plx"], s=4, c=np.where(sure.loc[ok, "snr"] > SNR_PLX, "C0", "0.6"))
    e = np.logspace(-2, 0.5, 50)
    for k, ls in [(SNR_PLX, "-"), (2, "--"), (1, ":")]:
        ax.plot(e, k * e, "k", ls=ls, lw=1, label=f"S/N = {k:.0f}")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Fehler der Parallaxe [mas]")
    ax.set_ylabel("Parallaxe [mas]")
    ax.set_title(f"{len(sure)} sicher zugeordnete Zentralsterne ({ok.sum()} mit ϖ > 0); blau: S/N > {SNR_PLX:.0f}", fontsize=10)
    ax.legend(fontsize=9)
    ax = axes[1]
    for df, col, lab in [(mid_q, "C1", "2 < S/N ≤ 5"), (hi_q, "C0", f"S/N > {SNR_PLX:.0f}")]:
        v = df.dropna(subset=["rcomb"])
        ax.scatter(v["rcomb"], v["d_inv"], s=8, c=col, label=f"{lab} ({len(v)})")
    x = np.logspace(1.8, 4.3, 10)
    ax.plot(x, x, "k-", lw=1, label="gleich")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Entfernung aus Parallaxe und Flächenhelligkeit (Chornay & Walton) [pc]")
    ax.set_ylabel("1000 / (ϖ − ϖ₀) [pc]")
    ax.set_title("Wann genügt 1/Parallaxe?", fontsize=10)
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    for lab, df in [(f"S/N > {SNR_PLX:.0f}", hi_q), ("2 < S/N ≤ 5", mid_q)]:
        v = df.dropna(subset=["rcomb"])
        q = np.log10(v["d_inv"] / v["rcomb"])
        print(f"{lab:10s}: {len(df):4d} Sterne, log10(1/ϖ ÷ kombiniert) Median {q.median():+.3f}, "
              f"Anteil 1/ϖ größer: {np.mean(q > 0):.0%}, typischer Fehler der Entfernung {np.median(1 / df['snr']):.0%}")
    print(f"Arbeitsstichprobe: {len(S)} Nebel, Entfernung Median {S['d'].median():.0f} pc "
          f"(10 % bis 90 %: {S['d'].quantile(0.1):.0f} bis {S['d'].quantile(0.9):.0f} pc)")
    print("Die nächsten fünf:", ", ".join(f"{n} {d:.0f} pc" for n, d in S.nsmallest(5, "d")[["Name", "d"]].values))


def reddening():
    """45. Rötung aus dem Balmer-Dekrement (Zellen 19 von nebulae_planetary.ipynb)."""
    global _, ax, axes, far, fig, near, r, ratio, row, sc
    r = S.dropna(subset=["EBV"])
    ratio = r["I6563"] / 100
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    ax = axes[0]
    ax.hist(ratio, bins=np.arange(1.5, 12.5, 0.25), color="C0", alpha=0.8)
    ax.axvline(HA_HB, color="k", ls="--", label=f"ohne Staub: {HA_HB:.2f}")
    ax.set_xlabel("beobachtetes Hα / Hβ")
    ax.set_ylabel("Zahl der Nebel")
    ax.set_title(f"Balmer-Dekrement von {len(r)} Nebeln der Arbeitsstichprobe", fontsize=10)
    ax.legend()
    ax = axes[1]
    sc = ax.scatter(r["d"], r["EBV"], c=np.abs(r["b"]), cmap="plasma_r", s=14, vmax=30)
    plt.colorbar(sc, ax=ax, label="|galaktische Breite b| [°]")
    ax.set_xscale("log")
    ax.set_xlabel("Entfernung [pc]")
    ax.set_ylabel("E(B−V) [mag]")
    ax.set_title("Rötung gegen Entfernung", fontsize=10)
    for _, row in r.nlargest(4, "EBV").iterrows():
        ax.annotate(row["Name"], (row["d"], row["EBV"]), fontsize=8, xytext=(4, 2), textcoords="offset points")
    plt.tight_layout()
    plt.show()

    print(f"{len(r)} Nebel: E(B−V) Median {r['EBV'].median():.2f} mag, c(Hβ) Median {r['c'].median():.2f}; "
          f"{np.mean(ratio < HA_HB):.0%} haben Hα/Hβ < {HA_HB:.2f} (E = 0 gesetzt)")
    near, far = r[r["d"] < 1500], r[r["d"] >= 1500]
    print(f"E(B−V) Median: näher als 1.5 kpc {near['EBV'].median():.2f} ({len(near)}), weiter {far['EBV'].median():.2f} ({len(far)}); "
          f"|b| < 5°: {r.loc[np.abs(r['b']) < 5, 'EBV'].median():.2f}, |b| > 15°: {r.loc[np.abs(r['b']) > 15, 'EBV'].median():.2f}")
    print(f"Schwächung bei E(B−V) = 1: Hβ {K['Hb']:.2f} mag, [O III] 5007 {K['O3']:.2f} mag, V {K['V']:.2f} mag")


def ages():
    """46. Größe und kinematisches Alter (Zellen 22 von nebulae_planetary.ipynb)."""
    global ax, axes, fig, kin, lab, m, name, off, rho, sc, t, v
    S["R_pc"] = S["pnRad"] / 206265 * S["d"]
    S["t_kin"] = S["R_pc"] * PC / (S["ExpVel"] * KM) / YEAR
    kin = S.dropna(subset=["t_kin"])

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    ax = axes[0]
    sc = ax.scatter(kin["ExpVel"], kin["R_pc"], c=np.log10(kin["d"]), cmap="viridis", s=18)
    plt.colorbar(sc, ax=ax, label="log₁₀(Entfernung / pc)")
    v = np.logspace(0.4, 2.0, 50)
    for t, lab in [(1e3, "1000 J"), (3e3, "3000 J"), (1e4, "10 000 J"), (3e4, "30 000 J"), (1e5, "100 000 J")]:
        ax.plot(v, v * KM * t * YEAR / PC, "k:", lw=0.8)
        ax.text(v[-1] * 1.03, v[-1] * KM * t * YEAR / PC, lab, fontsize=8, va="center")
    for name, off in [("NGC 7662", (5, -3)), ("NGC 6720", (5, 2)), ("NGC 6853", (5, -10)), ("NGC 7293", (-48, 4))]:
        m = kin["Name"] == name
        if m.any():
            ax.annotate(name, (kin.loc[m, "ExpVel"].iloc[0], kin.loc[m, "R_pc"].iloc[0]), fontsize=8,
                        xytext=off, textcoords="offset points")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(2.5, 190)
    ax.set_xlabel("Expansionsgeschwindigkeit aus [O III] [km/s]")
    ax.set_ylabel("Radius [pc]")
    ax.set_title(f"{len(kin)} Nebel; punktiert: gleiches kinematisches Alter in Jahren", fontsize=10)
    ax = axes[1]
    ax.hist(np.log10(kin["t_kin"]), bins=np.arange(2.6, 5.4, 0.1), color="C0", alpha=0.8)
    ax.axvline(np.log10(kin["t_kin"].median()), color="k", ls="--", label=f"Median {kin['t_kin'].median():.0f} Jahre")
    ax.set_xlabel("log₁₀(kinematisches Alter / Jahre)")
    ax.set_ylabel("Zahl der Nebel")
    ax.set_title("Wie lange wachsen die Hüllen schon?", fontsize=10)
    ax.legend()
    plt.tight_layout()
    plt.show()

    print(f"{len(kin)} Nebel: Radius Median {kin['R_pc'].median():.3f} pc ({kin['R_pc'].quantile(0.1):.3f} bis "
          f"{kin['R_pc'].quantile(0.9):.3f}), Geschwindigkeit Median {kin['ExpVel'].median():.1f} km/s, "
          f"Alter Median {kin['t_kin'].median():.0f} Jahre (10 % bis 90 %: {kin['t_kin'].quantile(0.1):.0f} bis {kin['t_kin'].quantile(0.9):.0f})")
    rho = kin[["R_pc", "ExpVel"]].corr(method="spearman").iloc[0, 1]
    print(f"Rangkorrelation Radius–Geschwindigkeit: {rho:+.2f}")
    print(kin.set_index("Name").loc[[n for n in ["NGC 7662", "NGC 6720", "NGC 6853", "NGC 7293"] if n in set(kin["Name"])],
                                    ["d", "pnRad", "R_pc", "ExpVel", "t_kin"]].round(3).to_string())


def zanstra_h():
    """47. Die Zanstra-Temperatur aus Wasserstoff (Zellen 25 von nebulae_planetary.ipynb)."""
    global EXAMPLES, S, T, WEID_COLS, ax, axes, fig, i, name, q, row, th
    global usable
    WEID_COLS = ["PNG", "SpType1", "TpTeff", "logTeff", "logL"]
    S = S.drop(columns=[c for c in WEID_COLS[1:] if c in S.columns]).merge(WEID[WEID_COLS], on="PNG", how="left")
    S["cool"] = S["SpType1"].fillna("").str.match(r"^\s*([AFGKM]|B[5-9])")
    S["V0"] = S["Vmag"] - K["V"] * S["EBV"]                           # entrötete V-Helligkeit
    S["FnuV"] = FNU_V0 * 10 ** (-0.4 * S["V0"])                        # F_ν bei 548 nm [erg s⁻¹ cm⁻² Hz⁻¹]
    usable = S["Vmag"].notna() & S["F_Hb"].notna() & ~S["Quality"].isin(["C", "D"]) & ~S["cool"]
    S["T_H"] = np.where(usable, zanstra_T(S["F_Hb"] / S["FnuV"], "H"), np.nan)

    EXAMPLES = ["NGC 6853", "NGC 7293", "NGC 3242", "NGC 6543"]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    ax = axes[0]
    ax.plot(10 ** LOGT / 1e3, 10 ** ZR["H"], "C0-", label="Hβ: Photonen über 13.6 eV")
    ax.plot(10 ** LOGT / 1e3, 10 ** ZR["He"], "C3-", label="He II 4686: Photonen über 54.4 eV")
    for i, name in enumerate(EXAMPLES):
        row = S[S["Name"] == name]
        if len(row) and np.isfinite(row["T_H"].iloc[0]):
            q, T = (row["F_Hb"] / row["FnuV"]).iloc[0], row["T_H"].iloc[0]
            ax.axhline(q, color=f"C{i + 4}", lw=0.8, ls=":")
            ax.plot(T / 1e3, q, "o", color=f"C{i + 4}", label=f"{name}: {T / 1e3:.0f} kK")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(12, 600)
    ax.set_xticks([20, 50, 100, 200, 500], labels=["20", "50", "100", "200", "500"])
    ax.xaxis.set_minor_formatter(plt.NullFormatter())
    ax.set_ylim(1e10, 1e17)
    ax.set_xlabel("Temperatur des Sterns [1000 K]")
    ax.set_ylabel("F(Linie) / F_ν(V) [Hz]")
    ax.set_title("Zanstra-Beziehung für einen Schwarzkörper", fontsize=10)
    ax.legend(fontsize=8, loc="lower right")
    ax = axes[1]
    th = S["T_H"].dropna()
    ax.hist(th / 1e3, bins=np.arange(10, 160, 5), color="C0", alpha=0.8)
    ax.axvline(th.median() / 1e3, color="k", ls="--", label=f"Median {th.median() / 1e3:.0f} kK")
    ax.set_xlabel("Zanstra-Temperatur aus Wasserstoff [1000 K]")
    ax.set_ylabel("Zahl der Zentralsterne")
    ax.set_title(f"{len(th)} Zentralsterne", fontsize=10)
    ax.legend()
    plt.tight_layout()
    plt.show()

    print(f"Zanstra-Temperatur (H) für {len(th)} Sterne: Median {th.median():.0f} K, 10 % bis 90 %: "
          f"{th.quantile(0.1):.0f} bis {th.quantile(0.9):.0f} K")
    print("Ausgelassen wegen kühlem Begleiter:", ", ".join(f"{n} ({s})" for n, s in
                                                         S.loc[S["cool"] & S["Vmag"].notna(), ["Name", "SpType1"]].values))
    print(S.set_index("Name").loc[[n for n in EXAMPLES if n in set(S["Name"])], ["Vmag", "EBV", "V0", "F_Hb", "T_H"]]
          .to_string(float_format=lambda x: f"{x:.3g}"))


def zanstra_he():
    """48. Ein zweites Thermometer: He II (Zellen 28 von nebulae_planetary.ipynb)."""
    global _, ax, axes, both, both_r, fig, large, q, rho, row, sc, setter
    global small
    S["T_He"] = np.where(usable, zanstra_T(S["F_He2"] / S["FnuV"], "He"), np.nan)
    S["T"] = np.where(S["T_He"].notna(), np.fmax(S["T_He"], S["T_H"]), S["T_H"])
    S["T_limit"] = S["T_He"].isna() & S["T_H"].notna()                  # nur Wasserstoff: untere Grenze
    both = S.dropna(subset=["T_H", "T_He"])
    both_r = both.dropna(subset=["R_pc"])

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    ax = axes[0]
    sc = ax.scatter(both["T_H"] / 1e3, both["T_He"] / 1e3, c=np.log10(both["R_pc"]), cmap="viridis", s=22)
    plt.colorbar(sc, ax=ax, label="log₁₀(Radius / pc)")
    ax.plot([15, 250], [15, 250], "k-", lw=1, label="gleich")
    ax.set_xscale("log")
    ax.set_yscale("log")
    for setter in (ax.set_xticks, ax.set_yticks):
        setter([20, 30, 50, 100, 200], labels=["20", "30", "50", "100", "200"])
    ax.xaxis.set_minor_formatter(plt.NullFormatter())
    ax.yaxis.set_minor_formatter(plt.NullFormatter())
    ax.set_xlabel("T aus Wasserstoff [1000 K]")
    ax.set_ylabel("T aus He II [1000 K]")
    ax.set_title(f"{len(both)} Zentralsterne mit beiden Temperaturen", fontsize=10)
    ax.legend()
    ax = axes[1]
    q = both_r["T_He"] / both_r["T_H"]
    ax.scatter(both_r["R_pc"], q, s=22, c="C0")
    for _, row in both_r.assign(q=q).nlargest(3, "q").iterrows():
        ax.annotate(row["Name"], (row["R_pc"], row["q"]), fontsize=8, xytext=(4, 2), textcoords="offset points")
    ax.axhline(1, color="k", lw=1)
    ax.set_xscale("log")
    ax.set_xlabel("Radius des Nebels [pc]")
    ax.set_ylabel("T(He II) / T(H)")
    ax.set_title("Große Nebel lassen Wasserstoff-Photonen entweichen", fontsize=10)
    plt.tight_layout()
    plt.show()

    rho = both_r[["R_pc"]].assign(q=q).corr(method="spearman").iloc[0, 1]
    small, large = both_r[both_r["R_pc"] < 0.1], both_r[both_r["R_pc"] >= 0.1]
    print(f"{len(both)} Sterne mit beiden Temperaturen: T(He II)/T(H) Median {np.median(both['T_He'] / both['T_H']):.2f}; "
          f"Radius < 0.1 pc: {np.median(small['T_He'] / small['T_H']):.2f} ({len(small)}), "
          f"≥ 0.1 pc: {np.median(large['T_He'] / large['T_H']):.2f} ({len(large)}); Rangkorrelation mit dem Radius {rho:+.2f}")
    print(f"Temperatur für die folgenden Schritte: {S['T'].notna().sum()} Sterne, davon {int(S['T_limit'].sum())} nur aus "
          f"Wasserstoff (untere Grenze); Median mit He II {S.loc[~S['T_limit'] & S['T'].notna(), 'T'].median():.0f} K")


def hr_diagram():
    """49. Das HR-Diagramm der Zentralsterne (Zellen 31 von nebulae_planetary.ipynb)."""
    global M, ax, axes, cmap, col, df, fig, g, hr, hr_h, hr_he, hv
    global i, j, kw, mk, rho, t, v
    S["L"] = luminosity(S["FnuV"], S["d"], S["T"])
    hr = S.dropna(subset=["T", "L"])
    hr_he, hr_h = hr[~hr["T_limit"]], hr[hr["T_limit"]]

    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))
    ax = axes[0]
    cmap = plt.get_cmap("copper_r")
    for i, (M, g) in enumerate(TRACKS.groupby("M")):
        col = cmap(0.2 + 0.8 * i / 5)
        ax.plot(g["log(Teff)"], g["log(L)"], "-", color=col, lw=1.2, label=f"{M_CORE[M]:.3f} M☉")
        for t, mk in [(1e3, "o"), (1e4, "s"), (1e5, "^")]:
            j = np.argmin(np.abs(np.log10(g["Time"].clip(lower=1)) - np.log10(t)))
            ax.plot(g["log(Teff)"].iloc[j], g["log(L)"].iloc[j], mk, color=col, ms=4)
    ax.scatter(np.log10(hr_he["T"]), np.log10(hr_he["L"]), s=24, c="C3", zorder=3, label=f"T aus He II ({len(hr_he)})")
    ax.scatter(np.log10(hr_h["T"]), np.log10(hr_h["L"]), s=24, facecolors="none", edgecolors="C0", zorder=3,
               label=f"T nur aus H, untere Grenze ({len(hr_h)})")
    ax.invert_xaxis()
    ax.set_xlim(5.45, 4.2)
    ax.set_ylim(0.3, 4.8)
    ax.set_xlabel("log₁₀(T / K)")
    ax.set_ylabel("log₁₀(L / L☉)")
    ax.set_title("Kreis, Quadrat, Dreieck: 10³, 10⁴, 10⁵ Jahre seit T = 10 000 K", fontsize=10)
    ax.legend(fontsize=7, loc="lower left", ncol=2)
    ax = axes[1]
    for df, kw in [(hr_he, dict(c="C3", s=24)), (hr_h, dict(facecolors="none", edgecolors="C0", s=24))]:
        v = df.dropna(subset=["R_pc"])
        ax.scatter(v["R_pc"], v["L"], **kw)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Radius des Nebels [pc]")
    ax.set_ylabel("Leuchtkraft des Zentralsterns [L☉]")
    ax.set_title("Mit wachsendem Nebel wird der Stern schwächer", fontsize=10)
    plt.tight_layout()
    plt.show()

    hv = hr.dropna(subset=["R_pc"])
    rho = hv[["R_pc", "L"]].corr(method="spearman").iloc[0, 1]
    print(f"{len(hr)} Sterne im HR-Diagramm; log L Median {np.log10(hr_he['L']).median():.2f} (mit He II), "
          f"{np.log10(hr_h['L']).median():.2f} (nur H); Rangkorrelation Radius–Leuchtkraft {rho:+.2f}")
    print(f"Radius < 0.1 pc: L Median {hv.loc[hv['R_pc'] < 0.1, 'L'].median():.0f} L☉, "
          f"> 0.3 pc: {hv.loc[hv['R_pc'] > 0.3, 'L'].median():.0f} L☉")


def core_masses():
    """50. Kernmassen und zwei Uhren (Zellen 34 von nebulae_planetary.ipynb)."""
    global OFFSETS, _, age, ax, axes, clocks, fig, he, masses, mc, q, row
    global sc, under, x
    he = ~S["T_limit"] & S["T"].notna() & S["L"].notna()
    mc, age, under = track_mass(np.log10(S.loc[he, "T"]), np.log10(S.loc[he, "L"]))
    S.loc[he, "Mc"], S.loc[he, "t_track"], S.loc[he, "under"] = mc, age, under
    clocks = S[he & S["t_track"].notna() & S["t_kin"].notna()]
    masses = S.loc[he, "Mc"].dropna()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    ax = axes[0]
    ax.hist(masses, bins=np.arange(0.56, 0.92, 0.02), color="C3", alpha=0.8, label=f"im Gitter ({len(masses)})")
    ax.bar(0.55, int(under.sum()), width=0.018, color="0.5", label=f"unter der 0.569-Spur ({int(under.sum())})")
    ax.axvline(0.6, color="k", ls=":", label="typischer Weißer Zwerg (0.6 M☉)")
    ax.set_xlabel("Kernmasse [M☉]")
    ax.set_ylabel("Zahl der Zentralsterne")
    ax.set_title(f"{int(he.sum())} Zentralsterne mit He-II-Temperatur", fontsize=10)
    ax.legend(fontsize=9)
    ax = axes[1]
    sc = ax.scatter(clocks["t_kin"], clocks["t_track"], c=clocks["Mc"], cmap="copper_r", s=30, vmin=0.56, vmax=0.8)
    plt.colorbar(sc, ax=ax, label="Kernmasse [M☉]")
    x = np.logspace(2.5, 5.5, 10)
    ax.plot(x, x, "k-", lw=1, label="gleich")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("kinematisches Alter R/v [Jahre]")
    ax.set_ylabel("Alter auf dem Entwicklungsweg [Jahre]")
    ax.set_title(f"Zwei Uhren für {len(clocks)} Nebel", fontsize=10)
    OFFSETS = {"NGC 6853": (5, 2), "NGC 3242": (5, -10), "NGC 6543": (5, 4), "NGC 6826": (5, -3), "He 2-108": (5, -3)}
    for _, row in clocks.iterrows():
        if row["Name"] in OFFSETS:
            ax.annotate(row["Name"], (row["t_kin"], row["t_track"]), fontsize=8, xytext=OFFSETS[row["Name"]],
                        textcoords="offset points")
    ax.legend()
    plt.tight_layout()
    plt.show()

    print(f"Kernmassen: {len(masses)} im Gitter, Median {masses.median():.3f} M☉ (16 % bis 84 %: {masses.quantile(0.16):.3f} "
          f"bis {masses.quantile(0.84):.3f}); {int(under.sum())} von {int(he.sum())} unter der leichtesten Spur, "
          f"{int(he.sum()) - len(masses) - int(under.sum())} außerhalb des Gitters")
    q = np.log10(clocks["t_track"] / clocks["t_kin"])
    print(f"Alter auf dem Weg ÷ kinematisch: Median {10 ** q.median():.2f}, Streuung {q.std():.2f} dex; "
          f"leichter als 0.6 M☉: {10 ** q[clocks['Mc'] < 0.6].median():.2f} ({(clocks['Mc'] < 0.6).sum()}), "
          f"schwerer: {10 ** q[clocks['Mc'] >= 0.6].median():.2f} ({(clocks['Mc'] >= 0.6).sum()})")


def brightest_oiii():
    """51. Die hellsten Nebel der Milchstraße in [O III] (Zellen 37 von nebulae_planetary.ipynb)."""
    global BULGE_LIM, FIT_BULGE, FIT_BULGE_ALL, M_STAR_OWN, M_STAR_OWN_ERR, ax, axes, bins, bulge, calib, col, f
    global fig, g, lab, local, nfit
    S["M5007"] = S["m5007"] - 5 * np.log10(S["d"] / 10)
    BULGE_LIM = -2.5                                                   # nur die hellsten 2 mag gehen in den Fit
    bulge = ALL[(ALL["l"].abs() < 10) & ALL["b"].abs().between(2, 10) & (ALL["oDiam"] < 20)].dropna(subset=["m5007"]).copy()
    bulge["M5007"] = bulge["m5007"] - 5 * np.log10(R0_PC / 10)
    calib = bulge[bulge["c"] < C_BULGE_MAX]
    FIT_BULGE = fit_pnlf(calib["M5007"].values, SIG_BULGE, -8.0, BULGE_LIM, -4.6)
    FIT_BULGE_ALL = fit_pnlf(bulge["M5007"].values, SIG_BULGE, -8.0, BULGE_LIM, -4.6)
    M_STAR_OWN = FIT_BULGE["m_star"]
    M_STAR_OWN_ERR = (FIT_BULGE["hi"] - FIT_BULGE["lo"]) / 2
    local = S.dropna(subset=["M5007"])

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    ax = axes[0]
    bins = np.arange(-8, 2.01, 0.25)
    ax.hist(bulge["M5007"], bins=bins, color="0.75", label=f"Bulge, alle ({len(bulge)})")
    ax.hist(calib["M5007"], bins=bins, color="C0", alpha=0.8, label=f"Bulge, c(Hβ) < {C_BULGE_MAX} ({len(calib)})")
    ax.hist(local["M5007"], bins=bins, histtype="step", color="C3", lw=2, label=f"Gaia-Stichprobe ({len(local)})")
    g = np.linspace(-7, BULGE_LIM, 300)
    nfit = FIT_BULGE["n"] * (1 - FIT_BULGE["frac"])
    ax.plot(g, nfit * 0.25 * pnlf_pdf(g, M_STAR_OWN, SIG_BULGE, 0, -8.0, BULGE_LIM), "k-", lw=1.5, label="angepasste PNLF")
    ax.axvline(M_STAR_OWN, color="C0", ls="--", label=f"M* Bulge = {M_STAR_OWN:.2f}")
    ax.axvline(M_STAR_LIT, color="k", ls=":", label=f"M* Ciardullo 2012 = {M_STAR_LIT}")
    ax.set_xlabel("M5007 [mag]")
    ax.set_ylabel("Zahl der Nebel pro 0.25 mag")
    ax.set_title("Absolute [O III]-Helligkeiten", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[1]
    for f, col, lab in [(FIT_BULGE, "C0", f"c(Hβ) < {C_BULGE_MAX}"), (FIT_BULGE_ALL, "0.5", "alle Bulge-Nebel")]:
        ax.plot(f["grid"], f["prof"], color=col, label=f"{lab}: M* = {f['m_star']:.2f}, Fremdanteil {f['frac']:.0%}")
    ax.axhline(0.5, color="k", ls=":", lw=1)
    ax.axvline(M_STAR_LIT, color="k", ls=":")
    ax.set_ylim(0, 6)
    ax.set_xlim(-6.6, -4.0)
    ax.set_xlabel("M* [mag]")
    ax.set_ylabel("Δ ln L")
    ax.set_title("Profil-Likelihood der Abbruchhelligkeit", fontsize=10)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print("Hellste Nebel mit Gaia-Entfernung:", ", ".join(f"{n} {m:.2f}" for n, m in local.nsmallest(5, "M5007")[["Name", "M5007"]].values))
    print(f"Bulge: {len(bulge)} Nebel, c(Hβ) Median {bulge['c'].median():.2f}; mit c < {C_BULGE_MAX}: {len(calib)}")
    print("Hellste Bulge-Nebel (alle):", ", ".join(f"{n} {m:.2f} (c = {c:.1f})" for n, m, c in
                                                 bulge.nsmallest(5, "M5007")[["Name", "M5007", "c"]].values))
    for lab, f in [(f"c < {C_BULGE_MAX}", FIT_BULGE), ("alle", FIT_BULGE_ALL)]:
        print(f"Fit Bulge {lab:8s}: M* = {f['m_star']:.2f} (1σ: {f['lo']:.2f} bis {f['hi']:.2f}), Fremdanteil {f['frac']:.1%}, "
              f"{f['n']} Nebel heller als {BULGE_LIM}")


def m31_nebulae():
    """52. Planetarische Nebel in M 31 (Zellen 40 von nebulae_planetary.ipynb)."""
    global DE_M31, RA_M31, SIG_DIFF, V_M31, ax, axes, bins, c89, col, de, diff, fig
    global k, m31, match, ra, sc, sgn
    m31 = M06[(M06["Host"] == "") & M06["m5007"].notna()].copy()
    ra = m31["RAJ2000"].str.split(expand=True).astype(float)
    de = m31["DEJ2000"].str.split(expand=True).astype(float)
    m31["ra"] = 15 * (ra[0] + ra[1] / 60 + ra[2] / 3600)
    sgn = np.where(m31["DEJ2000"].str.startswith("-"), -1, 1)
    m31["dec"] = sgn * (de[0].abs() + de[1] / 60 + de[2] / 3600)
    RA_M31, DE_M31, V_M31 = 10.6847, 41.2690, -300.0                  # Zentrum und Systemgeschwindigkeit [km/s]
    m31["x"] = (m31["ra"] - RA_M31) * np.cos(np.radians(DE_M31))
    m31["y"] = m31["dec"] - DE_M31
    c89 = C89[C89["Sample"].str.contains("A|B", na=False) & C89["m5007"].notna()]
    match = M06.dropna(subset=["C89", "m5007"]).merge(C89.dropna(subset=["m5007"]), left_on="C89", right_on="PN",
                                                      suffixes=("_M06", "_C89"))
    diff = match["m5007_M06"] - match["m5007_C89"]
    SIG_DIFF = 1.4826 * np.median(np.abs(diff - diff.median()))

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    ax = axes[0]
    sc = ax.scatter(m31["x"], m31["y"], c=m31["HV"] - V_M31, cmap="coolwarm", s=3, vmin=-300, vmax=300)
    plt.colorbar(sc, ax=ax, label="Geschwindigkeit relativ zu M 31 [km/s]")
    ax.set_xlim(2.2, -2.2)
    ax.set_aspect("equal")
    ax.set_xlabel("Δα cos δ [°] (Osten links)")
    ax.set_ylabel("Δδ [°]")
    ax.set_title(f"{len(m31)} Nebel in M 31 (Merrett et al. 2006)", fontsize=10)
    ax = axes[1]
    bins = np.arange(19.0, 27.01, 0.2)
    ax.hist(m31["m5007"], bins=bins, histtype="step", lw=1.8, color="C0", label=f"Merrett et al. 2006 ({len(m31)})")
    ax.hist(c89["m5007"], bins=bins, color="C1", alpha=0.7, label=f"Ciardullo et al. 1989, Stichproben A, B ({len(c89)})")
    for k, col in [("Ciardullo 1989", "C1"), ("Merrett 2006", "C0")]:
        ax.axvline(M5007_LIM[k], color=col, ls=":", lw=1)
    ax.set_yscale("log")
    ax.set_xlabel("m5007 [mag]")
    ax.set_ylabel("Zahl pro 0.2 mag")
    ax.set_title("Helligkeitsverteilung; punktiert: Grenze für den Fit", fontsize=10)
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    print(f"Merrett et al.: {len(M06)} Objekte, davon {len(m31)} in M 31; Begleiter und andere: "
          + ", ".join(f"{k} {v}" for k, v in M06.loc[M06['Host'] != '', 'Host'].value_counts().head(5).items()))
    print("Hellste fünf in M 31 (Merrett):", np.sort(m31["m5007"].values)[:5], "; Ciardullo A/B:", np.sort(c89["m5007"].values)[:5])
    print(f"Gemeinsame Nebel: {len(match)}; Merrett − Ciardullo: Median {diff.median():+.3f} mag, robuste Streuung {SIG_DIFF:.3f} mag")
    print(f"Geschwindigkeit: Nordosten (x > 0.5°) Median {np.median(m31.loc[m31['x'] > 0.5, 'HV']):.0f} km/s, "
          f"Südwesten (x < −0.5°) {np.median(m31.loc[m31['x'] < -0.5, 'HV']):.0f} km/s")


def luminosity_function():
    """53. Die Leuchtkraftfunktion von M 31 (Zellen 43 von nebulae_planetary.ipynb)."""
    global A5007_M31, FIT, SAMPLES, ax, axes, col, e, f, fig, g, h, hi
    global k, lo, m, mu, sel, sig
    A5007_M31 = K["O3"] * EBV_M31
    FIT = {"Ciardullo 1989": fit_pnlf(c89["m5007"].values, SIG_C89, 18.5, M5007_LIM["Ciardullo 1989"], 20.2),
           "Merrett 2006": fit_pnlf(m31["m5007"].values, SIG_M06, 17.0, M5007_LIM["Merrett 2006"], 20.2)}
    SAMPLES = {"Ciardullo 1989": (c89["m5007"].values, SIG_C89, 18.5), "Merrett 2006": (m31["m5007"].values, SIG_M06, 17.0)}

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    ax = axes[0]
    for (k, f), col in zip(FIT.items(), ["C1", "C0"]):
        m, sig, lo = SAMPLES[k]
        hi = M5007_LIM[k]
        sel = m[(m >= 19.0) & (m <= hi)]
        h, e = np.histogram(sel, bins=np.arange(19.0, hi + 0.01, 0.1))
        ax.errorbar(0.5 * (e[1:] + e[:-1]), h, yerr=np.sqrt(h), fmt="o", ms=3, color=col, label=f"{k} ({f['n']} Nebel)")
        g = np.linspace(19.0, hi, 400)
        ax.plot(g, f["n"] * 0.1 * pnlf_pdf(g, f["m_star"], sig, f["frac"], lo, hi), color=col, lw=1.5,
                label=f"m* = {f['m_star']:.2f}, Fremdanteil {f['frac']:.1%}")
    ax.set_yscale("log")
    ax.set_ylim(0.5, 300)
    ax.set_xlabel("m5007 [mag]")
    ax.set_ylabel("Zahl pro 0.1 mag")
    ax.set_title("Helle Enden der Leuchtkraftfunktion", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[1]
    for (k, f), col in zip(FIT.items(), ["C1", "C0"]):
        ax.plot(f["grid"], f["prof"], color=col, label=f"{k}: {f['lo']:.2f} bis {f['hi']:.2f}")
    ax.axhline(0.5, color="k", ls=":", lw=1)
    ax.set_xlim(19.7, 20.7)
    ax.set_ylim(0, 6)
    ax.set_xlabel("m* [mag]")
    ax.set_ylabel("Δ ln L")
    ax.set_title("Profil-Likelihood; punktiert: 1σ", fontsize=10)
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    print(f"Vordergrund vor M 31: E(B−V) = {EBV_M31}, A5007 = {A5007_M31:.3f} mag")
    for k, f in FIT.items():
        mu = f["m_star"] - A5007_M31 - M_STAR_LIT
        print(f"{k:15s}: m* = {f['m_star']:.3f} (+{f['hi'] - f['m_star']:.3f} / −{f['m_star'] - f['lo']:.3f}), "
              f"Fremdanteil {f['frac']:.1%} von {f['n']}; μ = {mu:.2f} mit M* = {M_STAR_LIT}, d = {10 ** (mu / 5 + 1) / 1e3:.0f} kpc")


def literature():
    """54. Temperaturen und Leuchtkräfte gegen die Literatur (Zellen 46 von nebulae_planetary.ipynb)."""
    global _, ax, axes, cmp, col, eff, fig, groups, lab, m, v
    cmp = S[S["T"].notna() & S["logTeff"].notna()].copy()
    cmp["dT"] = np.log10(cmp["T"]) - cmp["logTeff"]
    cmp["dL"] = np.log10(cmp["L"]) - cmp["logL"]
    groups = [(~cmp["T_limit"], "C3", "T aus He II"), (cmp["T_limit"], "C0", "T nur aus H")]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.2))
    ax = axes[0]
    for m, col, lab in groups:
        ax.scatter(cmp.loc[m, "logTeff"], np.log10(cmp.loc[m, "T"]), s=22, c=col, label=f"{lab} ({m.sum()})")
    ax.plot([4.2, 5.4], [4.2, 5.4], "k-", lw=1)
    ax.set_xlabel("log₁₀ T, Weidmann et al. 2020")
    ax.set_ylabel("log₁₀ T, Zanstra (dieses Notebook)")
    ax.set_title("Temperaturen", fontsize=10)
    ax.legend()
    ax = axes[1]
    for m, col, lab in groups:
        v = cmp[m].dropna(subset=["dL"])
        ax.scatter(v["logL"], np.log10(v["L"]), s=22, c=col, label=f"{lab} ({len(v)})")
    ax.plot([0.5, 4.6], [0.5, 4.6], "k-", lw=1)
    ax.set_xlabel("log₁₀ L / L☉, Weidmann et al. 2020")
    ax.set_ylabel("log₁₀ L / L☉ (dieses Notebook)")
    ax.set_title("Leuchtkräfte", fontsize=10)
    ax.legend()
    plt.tight_layout()
    plt.show()

    for m, _, lab in groups:
        v = cmp[m]
        print(f"{lab:12s}: {len(v):3d} Sterne, Δ log T Median {v['dT'].median():+.3f}, Streuung (robust) "
              f"{1.4826 * np.median(np.abs(v['dT'] - v['dT'].median())):.3f}; Δ log L Median {v['dL'].median():+.2f}, "
              f"Streuung {1.4826 * np.median(np.abs(v['dL'].dropna() - v['dL'].median())):.2f}")
    eff = cmp[~cmp["T_limit"] & (cmp["TpTeff"] == "eff")]
    print(f"Nur gegen Spektralanalysen („eff“) mit He-II-Temperatur: {len(eff)} Sterne, Δ log T Median {eff['dT'].median():+.3f}")
    print("Größte Abweichungen:", ", ".join(f"{n} {d:+.2f}" for n, d in cmp.reindex(cmp["dT"].abs().sort_values(ascending=False).index)
                                             [["Name", "dT"]].head(4).values))


def m31_distance():
    """55. Die Entfernung von M 31 (Zellen 49 von nebulae_planetary.ipynb)."""
    global EBV_ERR, LIT_MU, MU, M_STARS, M_STAR_LIT_ERR, ax, axes, ceph, col, err, err_m, f
    global fig, i, items, k, lab, ms, ms_err, mu, sec
    LIT_MU = {"Cepheiden (Li et al. 2021)": (24.407, 0.032),
              "TRGB (McConnachie et al. 2005)": (24.47, 0.07),
              "Bedeckungsveränderliche (Vilardell et al. 2010)": (24.36, 0.08)}
    M_STAR_LIT_ERR, EBV_ERR = 0.06, 0.011
    M_STARS = {"Ciardullo 2012 (Cepheiden)": (M_STAR_LIT, M_STAR_LIT_ERR),
               f"Bulge, c < {C_BULGE_MAX} (Schritt 51)": (M_STAR_OWN, M_STAR_OWN_ERR),
               "Bulge, alle Nebel (Schritt 51)": (FIT_BULGE_ALL["m_star"], (FIT_BULGE_ALL["hi"] - FIT_BULGE_ALL["lo"]) / 2),
               "Kovacevic et al. 2011, auf 8.18 kpc": (-4.38 - 5 * np.log10(R0_PC / 7520), 0.13)}
    MU = {}
    for k, f in FIT.items():
        err_m = (f["hi"] - f["lo"]) / 2
        for lab, (ms, ms_err) in [("M* = −4.53", (M_STAR_LIT, M_STAR_LIT_ERR)), ("M* aus dem Bulge", (M_STAR_OWN, M_STAR_OWN_ERR))]:
            MU[f"PNLF, {k}, {lab}"] = (f["m_star"] - A5007_M31 - ms, np.sqrt(err_m**2 + ms_err**2 + (K["O3"] * EBV_ERR) ** 2))

    fig, axes = plt.subplots(1, 2, figsize=(15, 5), gridspec_kw={"width_ratios": [1.3, 1]})
    ax = axes[0]
    items = list(MU.items()) + list(LIT_MU.items())
    for i, (lab, (mu, err)) in enumerate(items):
        col = "C3" if lab.startswith("PNLF") else "k"
        ax.errorbar(mu, -i, xerr=err, fmt="o", color=col, capsize=3)
    ax.set_yticks([-i for i in range(len(items))])
    ax.set_yticklabels([lab for lab, _ in items], fontsize=9)
    ax.axvspan(LIT_MU["Cepheiden (Li et al. 2021)"][0] - 0.032, LIT_MU["Cepheiden (Li et al. 2021)"][0] + 0.032, color="0.85")
    sec = ax.secondary_xaxis("top", functions=(lambda mu: 10 ** (mu / 5 + 1) / 1e3, lambda d: 5 * np.log10(d * 1e3) - 5))
    sec.set_xlabel("Entfernung [kpc]")
    ax.set_xlabel("Entfernungsmodul μ [mag]")
    ax.set_title("M 31: Planetarische Nebel (rot) gegen andere Methoden", fontsize=10, pad=12)
    ax = axes[1]
    for i, (lab, (ms, err)) in enumerate(M_STARS.items()):
        ax.errorbar(ms, -i, xerr=err, fmt="s", color="C0" if "Bulge," in lab else "k", capsize=3)
    ax.set_yticks([-i for i in range(len(M_STARS))])
    ax.set_yticklabels(list(M_STARS), fontsize=9)
    ax.set_xlabel("M* [mag]")
    ax.set_title("Eichungen der Abbruchhelligkeit", fontsize=10)
    plt.tight_layout()
    plt.show()

    for lab, (mu, err) in items:
        print(f"{lab:48s} μ = {mu:.2f} ± {err:.2f}  d = {10 ** (mu / 5 + 1) / 1e3:4.0f} kpc")
    ceph = LIT_MU["Cepheiden (Li et al. 2021)"][0]
    print(f"Abstand zu den Cepheiden: " + ", ".join(f"{k.split(', ', 1)[1]} {mu - ceph:+.2f} ({(mu - ceph) / err:+.1f}σ)"
                                                      for k, (mu, err) in MU.items()))
    print(f"M* aus dem Bulge {M_STAR_OWN:.2f} ± {M_STAR_OWN_ERR:.2f} gegen Ciardullo {M_STAR_LIT} und Kovacevic "
          f"{M_STARS['Kovacevic et al. 2011, auf 8.18 kpc'][0]:.2f}")
