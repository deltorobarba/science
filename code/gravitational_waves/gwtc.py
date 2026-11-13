"""Der Katalog der Gravitationswellen-Ereignisse (GWTC über GWOSC): bestätigte Ereignisse, die lautesten und extremsten, Massenlücken, Entfernung und Masse, ein Ereignis im Zeit-Frequenz-Bild, Reichweite der Detektoren, Auswahleffekt und Vergleich mit der Literatur.

Für gravitational_waves.ipynb aus gw_catalog.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, selection, extremes, masses, distances, event_spectrogram, snr_scaling, mass_distribution, literature.
Downloads und Cache: data/gravitational_waves/ (`gwdata.py`).
"""
import gwdata                                         # zuerst: Cache-Ordner für astropy (auch für gwpy)
import os, json, urllib.request
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy.time import Time
from gwosc.datasets import event_gps, event_detectors
from gwpy.timeseries import TimeSeries


def load():
    """Daten (Zellen 5 von gw_catalog.ipynb)."""
    global ASTRODATA, COLS, CONFIDENT, REFRESH, allev, path, raw
    plt.style.use("default")      # gwpy stellt beim Import den Plotstil um; der Katalog zeigt wie früher den Stil von matplotlib
    ASTRODATA = gwdata.DATA
    (ASTRODATA / "gwosc").mkdir(parents=True, exist_ok=True)


    REFRESH = False                                  # True: Katalog neu von GWOSC laden
    CONFIDENT = ["GWTC-5.0", "GWTC-4.1", "GWTC-4.0", "GWTC-3-confident", "GWTC-2.1-confident", "GWTC-1-confident",
                 "O4_Discovery_Papers", "O3_Discovery_Papers"]          # Reihenfolge: neuester Katalog zuerst

    path = ASTRODATA / "gwosc" / "allevents.json"
    if REFRESH or not path.exists():
        urllib.request.urlretrieve("https://gwosc.org/eventapi/json/allevents/", path)
    raw = json.loads(path.read_text())["events"]
    COLS = {"commonName": "name", "version": "version", "catalog.shortName": "katalog", "GPS": "gps",
            "mass_1_source": "m1", "mass_2_source": "m2", "chirp_mass_source": "mc", "total_mass_source": "m_ges",
            "final_mass_source": "m_end", "network_matched_filter_snr": "snr", "luminosity_distance": "dl",
            "redshift": "z", "chi_eff": "chi_eff", "far": "far", "p_astro": "p_astro"}
    allev = pd.DataFrame([{v: e.get(k) for k, v in COLS.items()} for e in raw.values()])
    print(f"{len(allev)} Einträge, {allev.name.nunique()} verschiedene Ereignisse")
    print(allev.katalog.value_counts().to_string())


def selection():
    """1. Den Katalog bereinigen (Zellen 8 von gw_catalog.ipynb)."""
    global cat, ev, nopar
    cat = allev[allev.katalog.isin(CONFIDENT)].copy()
    cat["prio"] = cat.katalog.map({k: i for i, k in enumerate(CONFIDENT)})
    cat = cat.sort_values(["prio", "version"], ascending=[True, False]).drop_duplicates("name").drop(columns="prio")
    cat["jahr"] = Time(cat.gps.values.astype(float), format="gps").decimalyear
    cat["kampagne"] = pd.cut(cat.jahr, [2015, 2016.5, 2018, 2021, 2030], labels=["O1", "O2", "O3", "O4"])
    cat["typ"] = np.select([cat.m1.isna(), cat.m1 < 3, cat.m2 < 3], ["ohne Parameter", "BNS", "NSBH"], "BBH")
    cat["mc_det"] = cat.mc * (1 + cat.z)
    cat = cat.sort_values("gps").reset_index(drop=True)

    print(f"Bestätigte Ereignisse: {len(cat)}, davon mit Parametern {cat.m1.notna().sum()}")
    print(pd.crosstab(cat.kampagne, cat.typ, margins=True, margins_name="Summe").to_string())
    print("\nNeuester Katalog je Ereignis:", cat.katalog.value_counts().to_dict())
    nopar = cat[cat.typ == "ohne Parameter"]
    print(f"Ohne Parameter: {len(nopar)} Kandidaten aus {sorted(nopar.katalog.unique())}, "
          f"Fehlalarmrate Median {nopar.far.median():.2g} pro Jahr (mit Parametern: {cat[cat.m1.notna()].far.median():.2g})")
    ev = cat[cat.m1.notna()].copy()                     # ab hier nur Ereignisse mit Parametern


def extremes():
    """2. Die lautesten und extremsten Ereignisse (Zellen 11 von gw_catalog.ipynb)."""
    global label, row, show
    show = ["name", "katalog", "snr", "m1", "m2", "dl", "z"]
    print("Die zehn lautesten Ereignisse (Netzwerk-SNR):")
    print(cat.nlargest(10, "snr")[show].to_string(index=False))
    print("\nExtreme:")
    for label, row in (("schwerstes (Gesamtmasse)", ev.loc[ev.m_ges.idxmax()]), ("leichtestes", ev.loc[ev.m_ges.idxmin()]),
                       ("nächstes", ev.loc[ev.dl.idxmin()]), ("fernstes", ev.loc[ev.dl.idxmax()])):
        print(f"  {label:<26}{row['name']:<18} m1 = {row.m1:6.1f}, m2 = {row.m2:6.1f} M☉, D_L = {row.dl:6.0f} Mpc, z = {row.z:.2f}")


def masses():
    """3. Die Massen (Zellen 14 von gw_catalog.ipynb)."""
    global axes, col, cols, fig, lower_gap, s, t, upper_gap
    lower_gap = ev[((ev.m1 > 3) & (ev.m1 < 5)) | ((ev.m2 > 3) & (ev.m2 < 5))]
    upper_gap = ev[(ev.m1 > 65) | (ev.m2 > 65)]
    print(f"Untere Lücke (eine Masse 3–5 M☉): {', '.join(f'{r.name} ({r.m1:.1f}+{r.m2:.1f})' for r in lower_gap.itertuples())}")
    print(f"Obere Lücke (eine Masse über 65 M☉): {len(upper_gap)} Ereignisse, davon mit m2 > 65: {(upper_gap.m2 > 65).sum()}")
    print(upper_gap.nlargest(5, "m1")[["name", "m1", "m2", "m_end", "chi_eff"]].to_string(index=False))
    print(f"\nVerhältnis m2/m1: Median {np.median(ev.m2 / ev.m1):.2f}; {np.mean(ev.m2 / ev.m1 > 0.5):.0%} der Paare über 0.5")

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    cols = {"BBH": "tab:blue", "NSBH": "tab:green", "BNS": "tab:red"}
    for t, col in cols.items():
        s = ev[ev.typ == t]
        axes[0].scatter(s.m1, s.m2, s=12, c=col, label=f"{t} ({len(s)})")
    axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    axes[0].axhspan(3, 5, color="0.85", zorder=0)
    axes[0].axvspan(3, 5, color="0.85", zorder=0)
    axes[0].axvspan(65, 130, color="tab:orange", alpha=0.12, zorder=0, label="obere Lücke (etwa)")
    axes[0].plot([1, 200], [1, 200], c="0.6", lw=0.8, ls="--")
    axes[0].set_xlabel("m1 [M☉]")
    axes[0].set_ylabel("m2 [M☉]")
    axes[0].set_title("Massen im Ruhesystem der Quelle (grau: untere Lücke)")
    axes[0].legend(fontsize=8)
    axes[1].hist(ev.m1, bins=np.logspace(0, np.log10(200), 40), color="0.4")
    axes[1].set_xscale("log")
    axes[1].set_xlabel("m1 [M☉]")
    axes[1].set_ylabel("Ereignisse")
    axes[1].set_title("Beobachtete Verteilung der größeren Masse")
    fig.tight_layout()
    plt.show()


def distances():
    """4. Entfernung und Masse (Zellen 17 von gw_catalog.ipynb)."""
    global ax, col, fig, k, k_o4, mm, ref, s
    print(ev.groupby("kampagne", observed=True).agg(n=("name", "size"), dl_median=("dl", "median"), dl_max=("dl", "max"),
                                                   z_max=("z", "max"), mc_det_median=("mc_det", "median")).round(2).to_string())
    fig, ax = plt.subplots(figsize=(9, 5))
    for k, col in zip(["O1", "O2", "O3", "O4"], ["tab:purple", "tab:green", "tab:blue", "tab:orange"]):
        s = ev[ev.kampagne == k]
        ax.scatter(s.mc_det, s.dl, s=12, c=col, label=f"{k} ({len(s)})")
    mm = np.logspace(0, 2.3, 50)
    ref = ev[ev.kampagne == "O4"]
    k_o4 = np.quantile(ref.dl * ref.snr / 8 / ref.mc_det ** (5 / 6), 0.9)
    ax.plot(mm, k_o4 * mm ** (5 / 6), c="black", ls="--", lw=1, label="∝ M^(5/6) (Reichweite O4, 90 %-Quantil)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Chirp-Masse im Detektor M_det [M☉]")
    ax.set_ylabel("Leuchtkraftentfernung D_L [Mpc]")
    ax.set_title("Schwere Systeme werden weiter gesehen")
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()


def event_spectrogram():
    """5. Ein Ereignis aus dem Katalog ansehen (Zellen 20 von gw_catalog.ipynb)."""
    global DET, G_C3, PADDING, SELECTED_EVENT, ax, dets, gps, plot, q, row, strain, tau30
    global white, window
    SELECTED_EVENT = "GW250114_082203"               # Name aus der Tabelle, z. B. "GW150914", "GW190521" oder "GW170817"
    PADDING = 16                                     # Sekunden Rohdaten vor und nach dem Ereignis
    row = cat[cat.name == SELECTED_EVENT].iloc[0]
    gps = event_gps(SELECTED_EVENT)
    dets = sorted(event_detectors(SELECTED_EVENT))
    DET = "H1" if "H1" in dets else dets[0]          # L1 hatte bei GW170817 eine Störung (Glitch) kurz vor dem Signal
    print(f"{SELECTED_EVENT} ({row.katalog}): GPS {gps}, Detektoren {dets}, verwendet {DET}")
    print(f"m1 = {row.m1:.2f}, m2 = {row.m2:.2f} M☉, Chirp-Masse {row.mc:.3f} M☉ (im Detektor {row.mc_det:.3f}), "
          f"D_L = {row.dl:.0f} Mpc, SNR = {row.snr:.1f}")

    # Dauer im Band ab 30 Hz (Newtonsche Näherung, Integration von df/dt)
    G_C3 = 4.925e-6                                  # G M☉ / c³ in Sekunden
    tau30 = 5 / 256 * (np.pi * 30) ** (-8 / 3) * (G_C3 * row.mc_det) ** (-5 / 3)
    print(f"Zeit von 30 Hz bis zur Verschmelzung: {tau30:.2f} s")

    strain = TimeSeries.fetch_open_data(DET, gps - PADDING, gps + PADDING, sample_rate=4096, cache=True)
    white = strain.whiten()
    window = min(max(2 * tau30, 0.5), PADDING - 2)
    q = white.q_transform(qrange=(4, 64), frange=(20, 512), outseg=(gps - window, gps + 0.3))
    plot = q.plot(figsize=(12, 4.5))
    ax = plot.gca()
    ax.set_xscale("seconds", epoch=gps)
    ax.set_yscale("log")
    ax.set_ylim(20, 512)
    ax.set_ylabel("Frequenz [Hz]")
    ax.set_xlabel(f"Zeit relativ zum Ereignis [s]")
    ax.set_title(f"{SELECTED_EVENT}: Q-Transformation der weißgerechneten Daten ({DET})")
    ax.colorbar(label="normierte Energie", clim=(0, 25))
    plt.show()                                       # wie in gw150914; plot.show() von gwpy warnt bei Inline-Bildern
    plt.style.use("default")                         # gwpy stellt beim Import den Plotstil um; zurücksetzen


def snr_scaling():
    """6. Signalstärke, Chirp-Masse und die Reichweite der Detektoren (Zellen 23 von gw_catalog.ipynb)."""
    global RUNS, ax, coef, col, d, err, fig, fit_scaling, g, lim, r, reach
    global s, sd, xx
    RUNS = ["O1", "O2", "O3", "O4"]
    def fit_scaling(d):
        X = np.column_stack([np.log10(d.mc_det)] + [(d.kampagne == r).astype(float) for r in RUNS])
        y = np.log10(d.snr * d.dl)
        coef, res, *_ = np.linalg.lstsq(X, y, rcond=None)
        resid = y - X @ coef
        cov = np.linalg.inv(X.T @ X) * resid.var(ddof=X.shape[1])
        return coef, np.sqrt(np.diag(cov)), resid.std()

    g = ev.dropna(subset=["mc_det", "dl", "snr"])
    for lim in (10, 20, 1000):
        d = g[g.mc_det < lim]
        coef, err, sd = fit_scaling(d)
        print(f"M_det < {lim:>4} M☉ (n = {len(d):>3}): Steigung s = {coef[0]:.2f} ± {err[0]:.2f}  (erwartet 5/6 = 0.83), "
              f"Streuung ±{sd:.2f} dex")
    coef, err, sd = fit_scaling(g[g.mc_det < 20])
    reach = {r: 10 ** (coef[i + 1] - coef[3]) for i, r in enumerate(RUNS)}
    print("\nReichweite relativ zu O3 (aus den Ereignissen mit M_det < 20 M☉): "
          + ", ".join(f"{r} {v:.2f}" for r, v in reach.items()))

    fig, ax = plt.subplots(figsize=(9, 5))
    for r, col in zip(RUNS, ["tab:purple", "tab:green", "tab:blue", "tab:orange"]):
        s = g[g.kampagne == r]
        ax.scatter(s.mc_det, s.snr * s.dl, s=12, c=col, label=r)
        xx = np.logspace(0, 2.3, 20)
        ax.plot(xx, 10 ** (coef[0] * np.log10(xx) + coef[RUNS.index(r) + 1]), c=col, lw=1)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Chirp-Masse im Detektor M_det [M☉]")
    ax.set_ylabel("ρ · D_L [Mpc]")
    ax.set_title(f"ρ·D_L ∝ M^s mit s = {coef[0]:.2f} (Fit für M_det < 20 M☉, verlängert)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()


def mass_distribution():
    """7. Der Auswahleffekt (Zellen 26 von gw_catalog.ipynb)."""
    global _, ax, bbh, bins, centers, fig, obs, tab, wgt, width
    bbh = ev[ev.typ == "BBH"].dropna(subset=["dl", "snr"]).copy()
    bbh["d_max"] = bbh.dl * bbh.snr / 8
    bbh["w"] = 1 / bbh.d_max ** 3
    bins = np.array([5, 7, 9, 12, 15, 20, 25, 30, 35, 40, 50, 65, 80, 150])
    obs, _ = np.histogram(bbh.m1, bins)
    wgt, _ = np.histogram(bbh.m1, bins, weights=bbh.w)
    width = np.diff(bins)
    tab = pd.DataFrame({"m1": [f"{a}-{b}" for a, b in zip(bins[:-1], bins[1:])], "beobachtet": obs,
                        "Anteil beobachtet": obs / obs.sum(), "Anteil gewichtet": wgt / wgt.sum(),
                        "gewichtet pro M☉": wgt / wgt.sum() / width})
    print(tab.round(4).to_string(index=False))
    print(f"\nAnteil m1 < 15 M☉: beobachtet {np.mean(bbh.m1 < 15):.0%}, gewichtet {bbh.w[bbh.m1 < 15].sum() / bbh.w.sum():.0%}")
    print(f"Reichweite D_max: Median {bbh.d_max.median():.0f} Mpc; für m1 < 15 M☉ {bbh.d_max[bbh.m1 < 15].median():.0f} Mpc, "
          f"für m1 > 30 M☉ {bbh.d_max[bbh.m1 > 30].median():.0f} Mpc")

    fig, ax = plt.subplots(figsize=(9, 4.2))
    centers = np.sqrt(bins[:-1] * bins[1:])
    ax.step(bins, np.r_[obs / obs.sum() / width, 0], where="post", c="0.5", label="beobachtet")
    ax.step(bins, np.r_[wgt / wgt.sum() / width, 0], where="post", c="tab:red", label="mit 1/V_max gewichtet")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("m1 [M☉]")
    ax.set_ylabel("Anteil pro M☉")
    ax.set_title("Massenverteilung der Schwarzen Löcher: beobachtet und um den Auswahleffekt korrigiert")
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()


def literature():
    """8. Vergleich mit den Katalogwerten und der Literatur (Zellen 29 von gw_catalog.ipynb)."""
    global lit, mc_own, r, ratio, worst
    mc_own = (ev.m1 * ev.m2) ** 0.6 / (ev.m1 + ev.m2) ** 0.2
    ratio = mc_own / ev.mc
    print(f"Chirp-Masse aus den Medianen von m1, m2 geteilt durch den Katalogwert: Median {ratio.median():.3f}, "
          f"5–95 % {ratio.quantile(0.05):.3f} bis {ratio.quantile(0.95):.3f}")
    worst = ev.loc[(ratio - 1).abs().idxmax()]
    print(f"  größte Abweichung: {worst['name']} ({ratio.max():.3f}); m1 = {worst.m1}, m2 = {worst.m2}, Katalog-Mc = {worst.mc}")

    print("\nReichweite relativ zu O3:")
    print(f"  {'':<8}{'eigene Messung':>16}{'BNS-Reichweite LIGO (etwa)':>30}")
    lit = {"O1": "70–80 Mpc", "O2": "60–100 Mpc", "O3": "110–130 Mpc", "O4": "150–160 Mpc"}
    for r in RUNS:
        print(f"  {r:<8}{reach[r]:>16.2f}{lit[r]:>30}")
    print("\nGewichtete Verteilung von m1: lokale Maxima bei",
          ", ".join(tab.m1[i] + " M☉" for i in range(1, len(tab) - 1)
                    if tab["gewichtet pro M☉"][i] > tab["gewichtet pro M☉"][i - 1] and tab["gewichtet pro M☉"][i] > tab["gewichtet pro M☉"][i + 1]),
          "\nLVK (GWTC-3, Populationsanalyse): Häufungen bei etwa 10 und 35 M☉")
