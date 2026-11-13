"""Transmissionsspektroskopie für exoplanets.ipynb: JWST-Spektrum eines Planeten, Vergleich zweier Transits, Höhe der
Molekülbanden in Skalenhöhen, Test auf ein flaches Spektrum, Gleichgewichtstemperatur und Bond-Albedo.

Daten: Spektren und Planetenwerte aus dem NASA Exoplanet Archive (Tabellen spectra und pscomppars). Voreinstellung
HATS-6 b mit der Atmosphärentemperatur 514 K aus der Analyse von Guzmán Caloca et al. (2026). Alle Schritte teilen sich
ein Zustandsobjekt, das `load` anlegt.
"""
from types import SimpleNamespace

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import chi2 as chi2_dist
from IPython.display import display

import archive

MU = 2.3              # mittleres Molekulargewicht einer Wasserstoff-Helium-Atmosphäre [u]
G_CGS = 6.674e-8      # Gravitationskonstante [cm³ g⁻¹ s⁻²]
BANDS = {"H₂O": [1.4, 1.9, 2.7], "CH₄": [2.3, 3.3], "NH₃": [3.0], "CO₂": [4.3], "CO": [4.7]}
COLORS = {"H₂O": "tab:blue", "CH₄": "tab:green", "NH₃": "tab:purple", "CO₂": "tab:red", "CO": "tab:brown"}
to_ppm = lambda s, col: np.array(s[col], dtype=float) * 1e4              # Prozent -> ppm


def load(planet="HATS-6 b", t_retrieved=514):
    """Liste der Spektren im Archiv und die Werte von Planet und Stern."""
    spec_meta = archive.query("spectra", where=f"pl_name='{planet}'")
    spec_meta["authors"] = spec_meta["authors"].str.replace("&aacute;", "á")
    print(f"{len(spec_meta)} Spektren von {planet} im Archiv:")
    display(spec_meta[["spec_type", "instrument", "minwavelng", "maxwavelng", "num_datapoints", "authors", "bibcode", "note"]])

    pp = archive.query("pscomppars", where=f"pl_name='{planet}'",
                       select="pl_name, pl_orbper, pl_rade, pl_radj, pl_bmasse, pl_bmassj, pl_eqt, st_rad, st_teff, "
                              "st_spectype, pl_ratdor").iloc[0]
    print(f"Planet: R = {pp['pl_radj']:.2f} R_Jup, M = {pp['pl_bmassj']:.2f} M_Jup, P = {pp['pl_orbper']:.2f} d, "
          f"T_eq (Katalog) = {pp['pl_eqt']:.0f} K")
    print(f"Stern:  {pp['st_spectype']}, T = {pp['st_teff']:.0f} K, R = {pp['st_rad']:.2f} R_Sonne")
    return SimpleNamespace(planet=planet, T_RETRIEVED=t_retrieved, spec_meta=spec_meta, pp=pp)


def clean(s, name, nsig=5):
    """Wellenlänge, Tiefe, Fehler ohne Kanäle, die mehr als nsig·σ vom gleitenden Median abweichen."""
    w, d, e = np.array(s["CENTRALWAVELNG"], dtype=float), to_ppm(s, "PL_TRANDEP"), to_ppm(s, "PL_TRANDEPERR1")
    med = pd.Series(d).rolling(7, center=True, min_periods=3).median().to_numpy()
    bad = np.abs(d - med) > nsig * e
    for wi, di, mi, ei in zip(w[bad], d[bad], med[bad], e[bad]):
        print(f"  {name}: Kanal bei {wi:.3f} µm entfernt ({di:.0f} ppm statt etwa {mi:.0f} ppm, {abs(di - mi) / ei:.0f}σ)")
    return w[~bad], d[~bad], e[~bad]


def visits(s):
    """JWST-Transmissionsspektren laden; die beiden einzelnen Transits Kanal für Kanal vergleichen."""
    spec_meta = s.spec_meta
    jwst = spec_meta[spec_meta["facility"].str.contains("JWST", na=False) & (spec_meta["spec_type"] == "Transmission")].copy()
    jwst["coadded"] = jwst["note"].str.contains("Co-added", case=False, na=False)
    main = jwst.sort_values(["coadded", "num_datapoints"], ascending=False).iloc[0]
    spectra = {r["note"]: archive.spectrum(r["spec_path"]) for _, r in jwst[jwst["bibcode"] == main["bibcode"]].iterrows()}

    spec = spectra[main["note"]]
    wl, dep, err = np.array(spec["CENTRALWAVELNG"], dtype=float), to_ppm(spec, "PL_TRANDEP"), to_ppm(spec, "PL_TRANDEPERR1")

    vis = [n for n in spectra if n != main["note"]]
    if len(vis) >= 2:
        wa, da, ea = clean(spectra[vis[0]], vis[0].split(";")[0])
        wb, db_, eb_ = clean(spectra[vis[1]], vis[1].split(";")[0])
        inside = (wa >= wb.min()) & (wa <= wb.max())
        wa, da, ea = wa[inside], da[inside], ea[inside]
        db, eb = np.interp(wa, wb, db_), np.interp(wa, wb, eb_)
        z = (da - db) / np.hypot(ea, eb)

        fig, axes = plt.subplots(1, 2, figsize=(15, 4.5), gridspec_kw={"width_ratios": [2.2, 1]})
        axes[0].plot(wa, z, ".", ms=3, c="black")
        axes[0].axhspan(-1, 1, color="grey", alpha=0.2, label="±1σ")
        axes[0].set_xlabel("Wellenlänge [µm]")
        axes[0].set_ylabel("(Transit 1 − Transit 2) / σ")
        axes[0].set_title("Unterschied der beiden Transits in Einheiten ihres Fehlers")
        axes[0].legend()
        xs = np.linspace(-5, 5, 200)
        axes[1].hist(z, bins=np.linspace(-5, 5, 41), density=True, color="tab:blue", alpha=0.6, label="gemessen")
        axes[1].plot(xs, np.exp(-xs ** 2 / 2) / np.sqrt(2 * np.pi), c="black", label="Normalverteilung, Breite 1")
        axes[1].set_xlabel("(Transit 1 − Transit 2) / σ")
        axes[1].set_ylabel("Dichte")
        axes[1].set_title("Verteilung")
        axes[1].legend(fontsize=8)
        fig.tight_layout()
        plt.show()
        print(f"{len(z)} Wellenlängen: χ²/Freiheitsgrad = {np.mean(z ** 2):.2f}, mittlerer Versatz {np.median(da - db):+.0f} ppm, "
              f"Anteil |Unterschied| > 3σ: {np.mean(np.abs(z) > 3):.1%}")
    print(f"Hauptspektrum: {main['note']} ({len(wl)} Punkte, {wl.min():.2f}–{wl.max():.2f} µm, mittlerer Fehler {np.median(err):.0f} ppm)")
    s.__dict__.update(main=main, spectra=spectra, wl=wl, dep=dep, err=err, visits=vis)


def spectrum(s):
    """Das Transmissionsspektrum mit den Banden der Moleküle und einer Achse in Skalenhöhen."""
    pp, wl, dep, err, main, T_RETRIEVED = s.pp, s.wl, s.dep, s.err, s.main, s.T_RETRIEVED
    R_p, M_p, R_s = pp["pl_rade"] * 6.371e8, pp["pl_bmasse"] * 5.972e27, pp["st_rad"] * 6.957e10      # cgs
    g = G_CGS * M_p / R_p ** 2
    scale_height = lambda T: 1.381e-16 * T / (MU * 1.6735e-24 * g)              # H = kT / (μ m_H g)  [cm]
    ppm_per_H = lambda T: 2 * R_p * scale_height(T) / R_s ** 2 * 1e6            # Änderung der Tiefe pro H  [ppm]
    T_axis = T_RETRIEVED or pp["pl_eqt"]
    base = np.median(dep)

    fig, ax = plt.subplots(figsize=(14, 5.5))
    for note in s.visits:
        sp = s.spectra[note]
        ax.plot(np.array(sp["CENTRALWAVELNG"], dtype=float), to_ppm(sp, "PL_TRANDEP"), ".", c="lightgrey", ms=3, zorder=1)
    ax.plot([], [], ".", c="lightgrey", label="einzelne Transits")
    ax.errorbar(wl, dep, err, fmt="o", c="black", ms=3, lw=0.8, label=main["note"].split(";")[0], zorder=3)
    for mol, centres in BANDS.items():
        for i, c in enumerate(centres):
            if wl.min() < c < wl.max():
                ax.axvspan(c - 0.06, c + 0.06, color=COLORS[mol], alpha=0.15, label=mol if i == 0 else None)
    ax.axhline(base, color="grey", ls=":", lw=1, label=f"Median ({base:.0f} ppm)")
    pad = 0.3 * np.ptp(dep)
    ax.set_ylim((dep - err).min() - pad, (dep + err).max() + pad)                # einzelne Transits streuen an den Rändern
    ax.set_xlim(wl.min() - 0.1, wl.max() + 0.1)
    ax.set_xlabel("Wellenlänge [µm]")
    ax.set_ylabel("Transittiefe [ppm]")
    ax.set_title(f"{s.planet}: JWST-Transmissionsspektrum, {main['instrument']} ({main['authors']})", fontsize=10)
    ax.legend(fontsize=8, ncol=4, loc="upper left")
    ax_h = ax.twinx()
    ax_h.set_ylim((np.array(ax.get_ylim()) - base) / ppm_per_H(T_axis))
    ax_h.set_ylabel(f"Skalenhöhen über dem Median (T = {T_axis:.0f} K)")
    fig.tight_layout()
    plt.show()

    print(f"g = {g / 100:.1f} m/s²")
    for T in [pp["pl_eqt"], T_RETRIEVED]:
        if T:
            print(f"T = {T:.0f} K:  H = {scale_height(T) / 1e5:.0f} km  ->  {ppm_per_H(T):.0f} ppm pro Skalenhöhe")
    s.__dict__.update(ppm_per_H=ppm_per_H, T_axis=T_axis, base=base)


def bands(s):
    """Überschuss jeder Bande über dem Median, in ppm und in Skalenhöhen."""
    pp, wl, dep, err, base, ppm_per_H, T_axis = s.pp, s.wl, s.dep, s.err, s.base, s.ppm_per_H, s.T_axis
    rows = []
    for mol, cs in BANDS.items():
        best = None
        for c in cs:
            sel = np.abs(wl - c) < 0.1
            if wl.min() < c < wl.max() and sel.any():
                ex, ex_err = dep[sel].mean() - base, np.sqrt(np.sum(err[sel] ** 2)) / sel.sum()
                if best is None or ex > best[1]:
                    best = (c, ex, ex_err)
        if best:
            c, ex, ex_err = best
            rows.append((mol, c, ex, ex_err, ex / ppm_per_H(pp["pl_eqt"]), ex / ppm_per_H(T_axis)))
    bands = pd.DataFrame(rows, columns=["Molekül", "Bande [µm]", "Überschuss [ppm]", "Fehler [ppm]",
                                        f"H bei {pp['pl_eqt']:.0f} K", f"H bei {T_axis:.0f} K"])
    bands["Signifikanz [σ]"] = bands["Überschuss [ppm]"] / bands["Fehler [ppm]"]
    display(bands.round(1))
    s.bands = bands


def flat_test(s):
    """χ² eines flachen Spektrums; Gleichgewichtstemperatur und die Bond-Albedo, die zur gemessenen Temperatur passt."""
    pp, dep, err, T_RETRIEVED = s.pp, s.dep, s.err, s.T_RETRIEVED
    w = 1 / err ** 2
    flat = np.sum(w * dep) / np.sum(w)
    chi2_flat = np.sum(((dep - flat) / err) ** 2)
    dof = len(dep) - 1
    print(f"Flaches Spektrum: mittlere Tiefe {flat:.0f} ppm, χ² = {chi2_flat:.0f} bei {dof} Freiheitsgraden "
          f"(χ²/Freiheitsgrad = {chi2_flat / dof:.1f}), Wahrscheinlichkeit p = {chi2_dist.sf(chi2_flat, dof):.1e}")

    T_eq0 = pp["st_teff"] * np.sqrt(1 / (2 * pp["pl_ratdor"]))                    # A_B = 0, volle Wärmeverteilung
    print(f"\nGleichgewichtstemperatur T_eq = T* √(R*/2a) = {pp['st_teff']:.0f} K · √(1/(2 · {pp['pl_ratdor']:.2f})) "
          f"= {T_eq0:.0f} K   (Katalog {pp['pl_eqt']:.0f} K)")
    A_B = None
    if T_RETRIEVED:
        A_B = 1 - (T_RETRIEVED / T_eq0) ** 4
        print(f"Temperatur aus dem Spektrum (Guzmán Caloca et al. 2026): {T_RETRIEVED} K, {T_eq0 - T_RETRIEVED:.0f} K kühler")
        print(f"Nötige Bond-Albedo A_B = 1 − (T/T_eq)⁴ = {A_B:.2f}")

    T = np.linspace(300, 800, 200)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(T, 1 - (T / T_eq0) ** 4, c="black", label="A_B = 1 − (T/T_eq,0)⁴")
    if T_RETRIEVED:
        ax.plot([T_RETRIEVED], [A_B], "o", c="tab:red", ms=8, label=f"T = {T_RETRIEVED} K  ->  A_B = {A_B:.2f}")
    ax.axvline(T_eq0, color="grey", ls=":", label=f"T_eq,0 = {T_eq0:.0f} K (A_B = 0)")
    ax.set_xlabel("Temperatur der Atmosphäre [K]")
    ax.set_ylabel("Nötige Bond-Albedo A_B")
    ax.set_title(f"{s.planet}: Albedo und Temperatur")
    ax.set_ylim(0, 1)
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()
    s.__dict__.update(chi2_flat=chi2_flat, dof=dof, T_eq0=T_eq0, A_B=A_B)


def compare(s):
    """Eigene Rechnung gegen Katalog und Veröffentlichung."""
    pp, bands, T_RETRIEVED = s.pp, s.bands, s.T_RETRIEVED
    strongest = bands.sort_values("Überschuss [ppm]", ascending=False)["Molekül"].tolist()
    print(f"{'Größe':<38}{'eigene Rechnung':<28}{'Katalog / Veröffentlichung'}")
    print("-" * 98)
    print(f"{'Gleichgewichtstemperatur (A_B = 0)':<38}{f'{s.T_eq0:.0f} K':<28}{pp['pl_eqt']:.0f} K (Katalog)")
    if T_RETRIEVED:
        print(f"{f'Bond-Albedo für {T_RETRIEVED} K':<38}{f'{s.A_B:.2f}':<28}≈ 0.71 (Veröffentlichung)")
    print(f"{'Spektrum flach?':<38}{f'nein, χ²/Fg = {s.chi2_flat / s.dof:.1f}':<28}nein: Moleküle nachgewiesen")
    print(f"{'Banden nach Höhe':<38}{', '.join(strongest):<28}H₂O, CH₄, CO₂, NH₃ (Retrieval)")
    print(f"\nQuelle: {s.main['authors']}, {s.main['bibcode']}")
