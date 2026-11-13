"""Demographie der Exoplaneten für exoplanets.ipynb: Perioden-Radius-Ebene, Radiuslücke, Masse-Radius-Diagramm mit
Kurven konstanter Dichte und der Gesteinsrelation, Vergleich mit Fulton et al. (2017).

Daten: alle bestätigten Planeten aus der Tabelle pscomppars des NASA Exoplanet Archive. Alle Schritte teilen sich ein
Zustandsobjekt, das `load` anlegt.
"""
from types import SimpleNamespace

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

import archive

COLUMNS = ("pl_name, discoverymethod, pl_orbper, pl_rade, pl_radeerr1, pl_radeerr2, "
           "pl_bmasse, pl_bmasseerr1, pl_bmasseerr2, pl_bmassprov, pl_insol, st_mass")
SOLAR_SYSTEM = [("Erde", 1.0, 1.0), ("Neptun", 17.15, 3.88), ("Saturn", 95.16, 9.45), ("Jupiter", 317.8, 11.21)]
r_rock = lambda m: m ** (1 / 3.7)                              # Zeng et al. (2016), erdähnlich, R und M in Erdeinheiten


def load(highlight="Kepler-8 b"):
    """Alle bestätigten Planeten; `highlight` wird in den Bildern markiert."""
    pop = archive.query("pscomppars", select=COLUMNS)
    hl = pop.loc[pop["pl_name"] == highlight].iloc[0]
    print(f"{len(pop)} bestätigte Exoplaneten")
    print(f"  mit Radius:                  {pop['pl_rade'].notna().sum()}")
    print(f"  mit gemessenem Radiusfehler: {pop['pl_radeerr1'].notna().sum()}  (die übrigen Radien sind aus einer Masse-Radius-Beziehung geschätzt)")
    print(f"  mit gemessener Masse:        {(pop['pl_bmassprov'] == 'Mass').sum()}  (die übrigen: M sin i oder geschätzt)")
    return SimpleNamespace(pop=pop, hl=hl, highlight=highlight)


def quality(s):
    """Zwei Stichproben: kleine Planeten mit genauem Radius, Planeten mit gemessener Masse und gutem Radius."""
    pop = s.pop
    pop["rad_relerr"] = (pop["pl_radeerr1"] - pop["pl_radeerr2"]) / 2 / pop["pl_rade"]      # mittlerer relativer Fehler
    pop["mass_relerr"] = (pop["pl_bmasseerr1"] - pop["pl_bmasseerr2"]) / 2 / pop["pl_bmasse"]
    small = pop[(pop["pl_orbper"] < 100) & (pop["rad_relerr"] < 0.10) & pop["pl_rade"].between(1.0, 4.0)].copy()
    mr = pop[(pop["pl_bmassprov"] == "Mass") & (pop["mass_relerr"] < 0.30) & (pop["rad_relerr"] < 0.30)].copy()
    print(f"Stichprobe Radiuslücke:  {len(small)} Planeten (P < 100 d, 1–4 R_Erde, Radiusfehler < 10 %)")
    print(f"Stichprobe Masse-Radius: {len(mr)} Planeten (gemessene Masse, Fehler von Masse und Radius < 30 %)")
    s.small, s.mr = small, mr


def period_radius(s):
    """Alle Planeten mit gemessenem Radius in der Ebene aus Umlaufzeit und Radius."""
    pop, hl = s.pop, s.hl
    fig, ax = plt.subplots(figsize=(10, 5.5))
    has_r = pop["pl_rade"].notna() & pop["pl_orbper"].notna() & pop["pl_radeerr1"].notna()
    for method, c, label in [("Transit", "tab:blue", "Transit"), ("Radial Velocity", "tab:green", "Radialgeschwindigkeit")]:
        m = has_r & (pop["discoverymethod"] == method)
        ax.scatter(pop.loc[m, "pl_orbper"], pop.loc[m, "pl_rade"], s=4, alpha=0.45, c=c, label=label)
    m = has_r & ~pop["discoverymethod"].isin(["Transit", "Radial Velocity"])
    ax.scatter(pop.loc[m, "pl_orbper"], pop.loc[m, "pl_rade"], s=4, alpha=0.3, c="grey", label="andere Methoden")
    ax.axhspan(1.5, 2.0, color="orange", alpha=0.2, label="Radiuslücke (1.5–2.0 R⊕)")
    ax.text(0.8, 4.5, "Neptun-\nWüste", fontsize=10, color="darkred", weight="bold")
    ax.scatter([hl["pl_orbper"]], [hl["pl_rade"]], marker="*", s=250, c="red", edgecolor="black", zorder=5)
    ax.annotate(s.highlight, (hl["pl_orbper"], hl["pl_rade"]), xytext=(10, 6), textcoords="offset points", fontsize=9)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.2, 3e4)
    ax.set_ylim(0.3, 30)
    ax.set_xlabel("Umlaufzeit P [Tage]")
    ax.set_ylabel("Radius [R⊕]")
    ax.set_title(f"Perioden-Radius-Ebene ({has_r.sum()} Planeten mit gemessenem Radius)")
    ax.legend(loc="lower right", fontsize=8, markerscale=2)
    fig.tight_layout()
    plt.show()


def radius_valley(s):
    """Verteilung der Radien kleiner Planeten, Kerndichteschätzung in log R, Tal und die beiden Maxima."""
    small = s.small
    logr = np.log10(small["pl_rade"])
    kde = gaussian_kde(logr, bw_method=0.15)
    grid = np.linspace(0, np.log10(4), 400)
    dens = kde(grid)
    search_range = (grid > np.log10(1.3)) & (grid < np.log10(2.5))
    r_valley = 10 ** grid[search_range][np.argmin(dens[search_range])]
    left, right = grid < np.log10(r_valley), grid > np.log10(r_valley)
    r_peak1 = 10 ** grid[left][np.argmax(dens[left])]
    r_peak2 = 10 ** grid[right][np.argmax(dens[right])]

    fig, ax1 = plt.subplots(figsize=(9, 4.5))
    ax1.hist(small["pl_rade"], bins=np.logspace(0, np.log10(4), 30), color="tab:blue", alpha=0.4,
             label=f"{len(small)} Planeten, P < 100 d, Radiusfehler < 10 %")
    ax1.set_xscale("log")
    ax1.set_xticks([1.0, 1.5, 2.0, 3.0, 4.0], ["1.0", "1.5", "2.0", "3.0", "4.0"])
    ax1.set_xlabel("Radius [R⊕]")
    ax1.set_ylabel("Anzahl Planeten")
    ax2 = ax1.twinx()
    ax2.plot(10 ** grid, dens, c="black", lw=2, label="Kerndichteschätzung in log R")
    ax2.set_yticks([])
    ax1.axvline(r_valley, color="tab:red", ls="--", lw=2, label=f"eigenes Tal: {r_valley:.2f} R⊕")
    ax1.axvspan(1.5, 2.0, color="orange", alpha=0.15, label="Fulton et al. (2017): 1.5–2.0 R⊕")
    ax1.set_title("Radiuslücke zwischen Supererden und Sub-Neptunen")
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=8)
    fig.tight_layout()
    plt.show()

    print(f"Tal (Minimum der KDE):          {r_valley:.2f} R_Erde")
    print(f"Maximum der Supererden:         {r_peak1:.2f} R_Erde")
    print(f"Maximum der Sub-Neptune:        {r_peak2:.2f} R_Erde")
    print(f"Tiefe des Tals: KDE im Tal / KDE im kleineren Maximum = "
          f"{kde(np.log10(r_valley))[0] / min(kde(np.log10(r_peak1))[0], kde(np.log10(r_peak2))[0]):.2f}")
    s.r_valley, s.r_peak1, s.r_peak2 = r_valley, r_peak1, r_peak2


def mass_radius(s):
    """Masse und Radius, gefärbt nach der Einstrahlung, mit den Planeten des Sonnensystems."""
    mr, hl = s.mr, s.hl
    fig, ax = plt.subplots(figsize=(10, 6))
    sc = ax.scatter(mr["pl_bmasse"], mr["pl_rade"], c=np.log10(mr["pl_insol"].where(mr["pl_insol"] > 0)),
                    cmap="plasma", s=9, alpha=0.7)
    fig.colorbar(sc, ax=ax).set_label("Einstrahlung log₁₀(S / S⊕)")
    for name, m_e, r_e in SOLAR_SYSTEM:
        ax.scatter([m_e], [r_e], marker="o", s=70, facecolors="none", edgecolors="black", lw=1.5)
        ax.text(m_e * 1.15, r_e * 0.9, name, fontsize=8, weight="bold")
    ax.scatter([hl["pl_bmasse"]], [hl["pl_rade"]], marker="*", s=250, c="red", edgecolor="black", zorder=5)
    ax.annotate(s.highlight, (hl["pl_bmasse"], hl["pl_rade"]), xytext=(10, -14), textcoords="offset points", fontsize=9)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.1, 1e4)
    ax.set_ylim(0.3, 30)
    ax.set_xlabel("Masse [M⊕]")
    ax.set_ylabel("Radius [R⊕]")
    ax.set_title(f"Masse und Radius von {len(mr)} Planeten (Fehler < 30 %)")
    fig.tight_layout()
    plt.show()

    rho_hl = hl["pl_bmasse"] * 5.972e27 / (4 / 3 * np.pi * (hl["pl_rade"] * 6.371e8) ** 3)
    print(f"{s.highlight}: M = {hl['pl_bmasse']:.0f} M⊕, R = {hl['pl_rade']:.1f} R⊕, mittlere Dichte {rho_hl:.2f} g/cm³ "
          f"(Saturn 0.69, Jupiter 1.33)")


def density_curves(s):
    """Kurven konstanter Dichte und die Gesteinsrelation; wie viel größer als Gestein sind Planeten unter und über dem Tal?"""
    mr, r_valley = s.mr, s.r_valley
    M_grid = np.logspace(-1, 4, 300)
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    ax = axes[0]
    ax.scatter(mr["pl_bmasse"], mr["pl_rade"], s=6, c="lightgrey", alpha=0.6, label="Planeten")
    for rho, ls, label in [(1.0, ":", "ρ = 1 g/cm³ (Wasser)"), (5.51, "--", "ρ = 5.51 g/cm³ (mittlere Dichte der Erde)"),
                           (10.0, "-.", "ρ = 10 g/cm³ (eisenreich)")]:
        ax.plot(M_grid, (M_grid * 5.972e27 / (4 / 3 * np.pi * rho)) ** (1 / 3) / 6.371e8, c="tab:gray", ls=ls, lw=1.2, label=label)
    M_rock = np.logspace(-1, np.log10(20), 100)
    ax.plot(M_rock, r_rock(M_rock), c="saddlebrown", lw=2.2, label="erdähnliches Gestein (Zeng et al. 2016)")
    for name, m_e, r_e in SOLAR_SYSTEM:
        ax.scatter([m_e], [r_e], marker="o", s=60, facecolors="none", edgecolors="black", lw=1.5)
        ax.text(m_e * 1.15, r_e * 0.9, name, fontsize=8)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.1, 1e4)
    ax.set_ylim(0.3, 30)
    ax.set_xlabel("Masse [M⊕]")
    ax.set_ylabel("Radius [R⊕]")
    ax.set_title("Masse-Radius-Diagramm mit Modellkurven")
    ax.legend(loc="upper left", fontsize=8)

    sm = mr[mr["pl_rade"] < 4].copy()
    sm["ratio"] = sm["pl_rade"] / r_rock(sm["pl_bmasse"])
    below, above = sm[sm["pl_rade"] < r_valley], sm[sm["pl_rade"] >= r_valley]
    bins = np.linspace(0.5, 3.0, 26)
    axes[1].hist(below["ratio"], bins=bins, alpha=0.6, color="saddlebrown", label=f"unter dem Tal (R < {r_valley:.2f} R⊕), {len(below)} Planeten")
    axes[1].hist(above["ratio"], bins=bins, alpha=0.6, color="tab:blue", label=f"über dem Tal (R ≥ {r_valley:.2f} R⊕), {len(above)} Planeten")
    axes[1].axvline(1.0, color="black", lw=1)
    axes[1].axvline(1.15, color="black", ls=":", lw=1, label="Grenze der Auswertung: 1.15")
    axes[1].set_xlabel("R / R_Gestein(M)")
    axes[1].set_ylabel("Anzahl Planeten")
    axes[1].set_title("Wie viel größer als ein Gesteinsplanet gleicher Masse?")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()

    for name, grp in [("unter dem Tal", below), ("über dem Tal", above)]:
        print(f"{name:14s}: Median R/R_Gestein = {grp['ratio'].median():.2f}, "
              f"mit Gestein verträglich (Verhältnis < 1.15): {(grp['ratio'] < 1.15).mean():.0%}")


def compare_fulton(s):
    """Eigene Werte gegen die Aussagen von Fulton et al. (2017)."""
    r_valley, r_peak1, r_peak2 = s.r_valley, s.r_peak1, s.r_peak2
    checks = [
        ("Tal im Bereich 1.5–2.0 R⊕",               f"{r_valley:.2f} R⊕", 1.5 <= r_valley <= 2.0),
        ("Maximum der Supererden unter 1.5 R⊕",     f"{r_peak1:.2f} R⊕", r_peak1 < 1.5),
        ("Maximum der Sub-Neptune bei 2.0–3.0 R⊕",  f"{r_peak2:.2f} R⊕", 2.0 <= r_peak2 <= 3.0),
    ]
    print(f"{'Aussage von Fulton et al. (2017)':<44}{'eigene Messung':<18}{'stimmt'}")
    print("-" * 70)
    for name, val, ok in checks:
        print(f"{name:<44}{val:<18}{'ja' if ok else 'nein'}")
