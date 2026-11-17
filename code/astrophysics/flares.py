"""Sonneneruptionen im Röntgenlicht für sun.ipynb: GOES-Flare-Listen, Flare-Klassen, Rate gegen Sonnenfleckenzahl,
Potenzgesetz der Spitzenflüsse, Anstieg und Abfall, die Lichtkurve des X-Flares vom 3. Oktober 2024 und GOES-16 gegen
GOES-18.

Daten: Flare-Listen (flsum) und 1-Minuten-Mittel (avg1m) der Röntgensensoren XRS von GOES-16 und GOES-18 aus dem Archiv
der NOAA (NetCDF, gelesen mit xarray), Cache in data/sun/goes/; Sonnenfleckenzahl von SILSO (`sundata.silso`).
Alle Schritte teilen sich ein Zustandsobjekt, das `load` anlegt.
"""
import re
import urllib.request
from types import SimpleNamespace

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, minimize
from scipy.stats import spearmanr

import sundata

DATA = sundata.DATA / "goes"
GOES = "https://data.ngdc.noaa.gov/platforms/solar-space-observing-satellites/goes"


def flsum_path(sat, refresh=False):
    """Neueste Flare-Liste eines Satelliten; der Dateiname enthält Start- und Enddatum."""
    DATA.mkdir(parents=True, exist_ok=True)
    cached = sorted(DATA.glob(f"sci_xrsf-l2-flsum_g{sat}_*.nc"))
    if cached and not refresh:
        return cached[-1]
    url = f"{GOES}/goes{sat}/l2/data/xrsf-l2-flsum_science/"
    html = urllib.request.urlopen(url).read().decode()
    name = sorted(set(re.findall(rf"sci_xrsf-l2-flsum_g{sat}_s\d+_e\d+_v[\d-]+\.nc", html)))[-1]
    urllib.request.urlretrieve(url + name, DATA / name)
    return DATA / name


def avg1m(sat, day):
    """1-Minuten-Mittel beider Kanäle für einen Tag (YYYY-MM-DD) als DataFrame.

    Eine gespeicherte Datei wird in jeder Version genommen; sonst die neueste im Verzeichnis des Monats (NOAA hat GOES-18
    2026 von v2-2-1 auf v2-2-2 neu prozessiert)."""
    DATA.mkdir(parents=True, exist_ok=True)
    d = day.replace("-", "")
    cached = sorted(DATA.glob(f"sci_xrsf-l2-avg1m_g{sat}_d{d}_v*.nc"))
    if cached:
        path = cached[-1]
    else:
        url = f"{GOES}/goes{sat}/l2/data/xrsf-l2-avg1m_science/{d[:4]}/{d[4:6]}/"
        html = urllib.request.urlopen(url).read().decode()
        names = sorted(set(re.findall(rf"sci_xrsf-l2-avg1m_g{sat}_d{d}_v[\d-]+\.nc", html)))
        if not names:
            raise FileNotFoundError(f"Keine 1-Minuten-Datei von GOES-{sat} für {day} in {url}")
        path = DATA / names[-1]
        urllib.request.urlretrieve(url + names[-1], path)
    ds = xr.open_dataset(path)
    return ds[["xrsa_flux", "xrsb_flux", "xrsa_flag", "xrsb_flag"]].to_dataframe()


def read_flares(sat, refresh=False):
    """Aus den Ereigniszeilen einen Flare pro Maximum machen: Start davor, Ende danach."""
    df = xr.open_dataset(flsum_path(sat, refresh)).to_dataframe().reset_index()
    df["status"] = df.status.astype(str)
    df = df.sort_values("time", kind="stable")
    st = df[df.status == "EVENT_START"][["time", "background_flux"]].rename(columns={"time": "t_start", "background_flux": "bg"})
    pk = df[df.status == "EVENT_PEAK"][["time", "xrsb_flux", "flare_class"]].rename(
        columns={"time": "t_peak", "xrsb_flux": "F", "flare_class": "klasse"})
    en = df[df.status == "EVENT_END"][["time", "integrated_flux"]].rename(columns={"time": "t_end", "integrated_flux": "fluenz"})
    f = pd.merge_asof(pk, st, left_on="t_peak", right_on="t_start", direction="backward")
    f = pd.merge_asof(f, en, left_on="t_peak", right_on="t_end", direction="forward")
    late = f.t_end > f.t_peak.shift(-1)          # ein Ende nach dem nächsten Maximum gehört nicht mehr dazu
    f.loc[late, ["t_end", "fluenz"]] = [pd.NaT, np.nan]
    f["F"] = f.F.astype(float)
    f["dF"] = f.F - f.bg                         # Spitzenfluss ohne Hintergrund
    f["anstieg"] = (f.t_peak - f.t_start).dt.total_seconds() / 60
    f["abfall"] = (f.t_end - f.t_peak).dt.total_seconds() / 60
    f["sat"] = sat
    return f


def goes_class(F, rounding=False):
    """Klasse aus dem Spitzenfluss; NOAA schneidet die Mantisse nach einer Nachkommastelle ab."""
    e = np.clip(np.floor(np.log10(F)).astype(int), -8, -4)
    mant = F / 10.0 ** e
    mant = np.round(mant, 1) if rounding else np.floor(mant * 10 + 1e-9) / 10
    return np.array([f"{'ABCMX'[k + 8]}{m:.1f}" for k, m in zip(e, mant)])


def load(event_day="2024-10-03", refresh=False):
    """Flare-Listen beider Satelliten und die monatliche Sonnenfleckenzahl."""
    fl = {sat: read_flares(sat, refresh) for sat in (16, 18)}
    for sat, f in fl.items():
        counts = f.klasse.str[0].value_counts()
        print(f"GOES-{sat}: {f.t_peak.min():%Y-%m-%d} bis {f.t_peak.max():%Y-%m-%d}, {len(f)} Flares  "
              + "  ".join(f"{c}: {counts.get(c, 0)}" for c in "ABCMX") + f"   (Datei {flsum_path(sat).name})")
    ssn = sundata.silso("snmtotcsv", refresh)              # dieselbe Reihe wie im Teil zum Zyklus
    ssn.index = pd.PeriodIndex.from_fields(year=ssn.jahr, month=ssn.monat, freq="M")
    return SimpleNamespace(fl=fl, ssn=ssn, event_day=event_day)


def classes(s):
    """Eigene Klassen gegen die Liste; eine gemeinsame Reihe aus GOES-16 und GOES-18."""
    fl = s.fl
    for sat, f in fl.items():
        trunc = np.mean(goes_class(f.F.values) == f.klasse.values)
        rnd = np.mean(goes_class(f.F.values, rounding=True) == f.klasse.values)
        print(f"GOES-{sat}: eigene Klasse = Listenklasse bei {trunc:.1%} (abgeschnitten) bzw. {rnd:.1%} (gerundet); "
              f"{f.t_end.isna().mean():.0%} ohne Ende (nächster Flare begann vorher)")

    # Eine Reihe für 2017 bis heute: GOES-16 bis zu seinem letzten Tag, danach GOES-18
    cut = fl[16].t_peak.max()
    allf = pd.concat([fl[16], fl[18][fl[18].t_peak > cut]], ignore_index=True)
    print(f"\nGemeinsame Reihe: {len(allf)} Flares von {allf.t_peak.min():%Y-%m} bis {allf.t_peak.max():%Y-%m} "
          f"(GOES-16 bis {cut:%Y-%m-%d}, danach GOES-18)")
    print("\nDie zehn stärksten Flares:")
    print(allf.nlargest(10, "F")[["t_peak", "klasse", "anstieg", "abfall", "bg", "sat"]].to_string(index=False))
    s.allf, s.cut = allf, cut


def rate(s):
    """Flares pro Monat gegen die Sonnenfleckenzahl, mit Poisson-Regression N = k·R^β."""
    allf, ssn, cut = s.allf, s.ssn, s.cut
    allf["monat"] = allf.t_peak.dt.to_period("M")
    rate = allf.groupby("monat").F.agg(C=lambda x: (x >= 1e-6).sum(), M=lambda x: (x >= 1e-5).sum(),
                                       X=lambda x: (x >= 1e-4).sum())
    rate = rate.iloc[1:-1].join(ssn.sn, how="inner")      # angebrochene erste und letzte Monate weglassen
    print(f"{len(rate)} Monate von {rate.index[0]} bis {rate.index[-1]}")
    for c in ("C", "M", "X"):
        rho, p = spearmanr(rate.sn, rate[c])
        print(f"≥{c}1 gegen Sonnenfleckenzahl: Spearman ρ = {rho:.2f}")

    # Poisson-Regression N = k·R^β für die M-Flares (alle Monate haben R > 0)
    R, N = rate.sn.values, rate.M.values
    nll = lambda q: np.sum(np.exp(q[0]) * R ** q[1] - N * (q[0] + q[1] * np.log(R)))
    res = minimize(nll, [np.log(0.01), 1.5], method="BFGS")
    k_fit, beta = np.exp(res.x[0]), res.x[1]
    lam = k_fit * R ** beta
    disp = np.sum((N - lam) ** 2 / lam) / (len(N) - 2)
    beta_err = np.sqrt(res.hess_inv[1, 1])
    print(f"M-Flares pro Monat = {k_fit:.4f} · R^{beta:.2f} (± {beta_err:.2f} unter Poisson-Annahme)")
    print(f"χ²/dof = {disp:.1f}: die Varianz ist {disp:.0f}-mal so groß wie bei Poisson; realistischer Fehler von β ≈ ± {beta_err * np.sqrt(disp):.2f}")
    print("\nFlares pro Jahr:")
    yearly = allf.groupby(allf.t_peak.dt.year).F.agg(
        C=lambda x: ((x >= 1e-6) & (x < 1e-5)).sum(), M=lambda x: ((x >= 1e-5) & (x < 1e-4)).sum(), X=lambda x: (x >= 1e-4).sum())
    yearly["SN"] = ssn.groupby("jahr").sn.mean().reindex(yearly.index).round(0)
    print(yearly.T.to_string())

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.2), gridspec_kw={"width_ratios": [2, 1]})
    x = rate.index.to_timestamp()
    axes[0].plot(x, rate.sn, c="black", lw=1.5, label="Sonnenfleckenzahl")
    axes[0].bar(x, rate.M, width=25, color="tab:orange", label="M-Flares und stärker")
    axes[0].plot(x[rate.X > 0], rate.X[rate.X > 0] * 10, "o", c="tab:red", ms=4, label="X-Flares × 10")
    axes[0].plot(x, rate.C / 2, c="tab:blue", lw=1, label="C-Flares und stärker / 2")
    axes[0].axvline(cut, c="0.5", ls=":", lw=1)
    axes[0].text(cut, axes[0].get_ylim()[1] * 0.95, " GOES-16 | GOES-18", fontsize=8, va="top")
    axes[0].set_ylabel("pro Monat")
    axes[0].set_title("Flares pro Monat und Sonnenfleckenzahl")
    axes[0].legend(fontsize=8, loc="upper left")
    axes[1].scatter(rate.sn, rate.M, s=12, c="tab:orange")
    rr = np.linspace(1, rate.sn.max(), 200)
    axes[1].plot(rr, k_fit * rr ** beta, c="black", label=f"N = {k_fit:.4f}·R^{beta:.2f}")
    axes[1].set_xlabel("Sonnenfleckenzahl R")
    axes[1].set_ylabel("M-Flares pro Monat")
    axes[1].set_title("Poisson-Regression")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()


def powerlaw_fit(x, xmins):
    """MLE-Exponent und KS-Abstand für jede Schwelle; Ergebnis mit dem kleinsten Abstand."""
    x = np.sort(x[np.isfinite(x) & (x > 0)])
    rows = []
    for xm in xmins:
        y = x[x >= xm]
        n = len(y)
        a = 1 + n / np.sum(np.log(y / xm))
        D = np.max(np.abs(np.arange(1, n + 1) / n - (1 - (y / xm) ** (1 - a))))
        rows.append((xm, a, (a - 1) / np.sqrt(n), n, D))
    scan = pd.DataFrame(rows, columns=["F_min", "alpha", "fehler", "n", "D"])
    return scan, scan.loc[scan.D.idxmin()]


def powerlaw(s):
    """Potenzgesetz der Spitzenflüsse mit und ohne Hintergrund; der Hintergrund pro Jahr."""
    allf = s.allf
    xmins = np.logspace(-6.5, -4.5, 41)
    fits = {}
    for label, col in (("Spitzenfluss F", "F"), ("ohne Hintergrund ΔF", "dF")):
        scan, best = powerlaw_fit(allf[col].values, xmins)
        fits[label] = (scan, best, col)
        print(f"{label:<22} F_min = {best.F_min:.1e} W/m² ({goes_class(np.array([best.F_min]))[0]}),  "
              f"α = {best.alpha:.3f} ± {best.fehler:.3f},  n = {best.n:.0f},  D = {best.D:.3f}")

    # Hintergrund: Anteil der Flares, deren Hintergrund über C1 lag
    bg_year = allf.groupby(allf.t_peak.dt.year).bg.agg(median="median", ueber_C1=lambda b: (b > 1e-6).mean())
    print("\nHintergrund am Flarestart (Median) und Anteil über C1:")
    print(bg_year.T.to_string(float_format=lambda v: f"{v:.1e}" if v < 1e-3 else f"{v:.2f}"))

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
    for (label, (scan, best, col)), c in zip(fits.items(), ("black", "tab:blue")):
        x = np.sort(allf[col].dropna().values)
        x = x[x > 0]
        ccdf = 1 - np.arange(len(x)) / len(x)
        axes[0].loglog(x, ccdf, c=c, lw=1, label=label)
        xx = np.logspace(np.log10(best.F_min), np.log10(x.max()), 50)
        frac = best.n / len(x)
        axes[0].loglog(xx, frac * (xx / best.F_min) ** (1 - best.alpha), c=c, ls="--", lw=1.2,
                       label=f"α = {best.alpha:.2f} ab {best.F_min:.1e}")
        axes[1].semilogx(scan.F_min, scan.alpha, c=c, label=label)
        axes[2].semilogx(scan.F_min, scan.D, c=c, label=label)
    axes[0].set_xlabel("Fluss [W/m²]")
    axes[0].set_ylabel("Anteil mit größerem Fluss")
    axes[0].set_title("Komplementäre Verteilungsfunktion")
    axes[0].legend(fontsize=7)
    axes[1].set_xlabel("Schwelle F_min [W/m²]")
    axes[1].set_ylabel("α")
    axes[1].set_title("Exponent je nach Schwelle")
    axes[2].set_xlabel("Schwelle F_min [W/m²]")
    axes[2].set_ylabel("KS-Abstand D")
    axes[2].set_title("Wahl der Schwelle")
    for ax in axes[1:]:
        ax.legend(fontsize=7)
    fig.tight_layout()
    plt.show()
    s.fits = fits


def timing(s):
    """Anstieg und Abfall nach Klasse."""
    allf = s.allf
    cls = pd.cut(allf.F, [1e-7, 1e-6, 1e-5, 1e-4, 1e-2], labels=["B", "C", "M", "X"], right=False)
    summary = allf.groupby(cls, observed=True)[["anstieg", "abfall"]].median()
    summary["n"] = allf.groupby(cls, observed=True).size()
    print("Median in Minuten (Abfall = Maximum bis Hälfte über dem Hintergrund):")
    print(summary.to_string())
    ok = allf.abfall.notna()
    rho_r, _ = spearmanr(np.log10(allf.F), allf.anstieg)
    rho_d, _ = spearmanr(np.log10(allf.F[ok]), allf.abfall[ok])
    print(f"\nSpearman: log F gegen Anstieg ρ = {rho_r:.2f}, gegen Abfall ρ = {rho_d:.2f}")
    print(f"Anteil der Flares, die schneller ansteigen als abfallen: {(allf.anstieg[ok] < allf.abfall[ok]).mean():.0%}")

    fig, axes = plt.subplots(1, 2, figsize=(12, 3.8))
    for ax, col, title in zip(axes, ("anstieg", "abfall"), ("Anstieg: Start bis Maximum", "Abfall: Maximum bis halbe Höhe")):
        data = [allf.loc[(cls == c) & allf[col].notna(), col] for c in "BCMX"]
        ax.boxplot(data, showfliers=False)
        ax.set_xticks(range(1, 5), list("BCMX"))
        ax.set_xlabel("Klasse")
        ax.set_ylabel("Minuten")
        ax.set_title(title)
    fig.tight_layout()
    plt.show()


def lightcurve(s, start="11:30", end="14:00"):
    """Die Lichtkurve des X-Flares am event_day: Maximum, Klasse, exponentieller Abfall, Härteverhältnis."""
    fl, EVENT_DAY = s.fl, s.event_day
    lc = avg1m(18, EVENT_DAY)
    lc = lc[(lc.index > f"{EVENT_DAY} {start}") & (lc.index < f"{EVENT_DAY} {end}")]
    good = (lc.xrsb_flag == 0) & (lc.xrsa_flag == 0)
    lc = lc[good]
    t_p = lc.xrsb_flux.idxmax()
    F_p = lc.xrsb_flux.max()
    row = fl[18].loc[(fl[18].t_peak - t_p).abs().idxmin()]
    print(f"Eigenes Maximum: {t_p:%H:%M} UT, F = {F_p:.3e} W/m² → {goes_class(np.array([F_p]))[0]}")
    print(f"Flare-Liste GOES-18: Start {row.t_start:%H:%M}, Maximum {row.t_peak:%H:%M}, Ende {row.t_end:%H:%M}, "
          f"Klasse {row.klasse}, Hintergrund {row.bg:.1e}")

    # Exponentielles Abklingen in der ersten Stunde nach dem Maximum
    dec = lc[(lc.index >= t_p) & (lc.index < t_p + pd.Timedelta("60min"))]
    xm = (dec.index - t_p).total_seconds() / 60
    model = lambda x, A, tau, bgf: bgf + A * np.exp(-x / tau)
    # relative Fehler: sonst bestimmen allein die ersten Minuten mit dem höchsten Fluss den Fit
    (A, tau, bgf), cov = curve_fit(model, xm, dec.xrsb_flux, p0=[F_p, 10, row.bg], sigma=dec.xrsb_flux)
    tau_err = np.sqrt(cov[1, 1])
    rel = np.sqrt(np.mean((dec.xrsb_flux / model(xm, A, tau, bgf) - 1) ** 2))
    half = lc[(lc.index > t_p) & (lc.xrsb_flux < (F_p + row.bg) / 2)].index[0]
    print(f"Abklingzeit τ = {tau:.1f} ± {tau_err:.1f} min, Hintergrund danach {bgf:.1e} W/m², relative Abweichung {rel:.1%}")
    print(f"Halbe Höhe: nach Modell τ·ln2 = {tau * np.log(2):.1f} min, gemessen {(half - t_p).total_seconds() / 60:.0f} min "
          f"(Liste: Ende nach {row.abfall:.0f} min)")

    ratio = lc.xrsa_flux / lc.xrsb_flux
    deriv = lc.xrsb_flux.diff() / 60                 # W/m² pro Sekunde
    t_ratio, t_deriv = ratio.idxmax(), deriv.idxmax()
    print(f"Härteverhältnis A/B: Maximum {ratio.max():.2f} um {t_ratio:%H:%M}, am Flare-Maximum {ratio[t_p]:.2f}")
    print(f"Steilster Anstieg von XRS-B um {t_deriv:%H:%M}, {(t_p - t_deriv).total_seconds() / 60:.0f} min vor dem Maximum")

    fig, axes = plt.subplots(3, 1, figsize=(11, 8), sharex=True, gridspec_kw={"height_ratios": [2, 1, 1]})
    axes[0].semilogy(lc.index, lc.xrsb_flux, c="tab:red", label="XRS-B 0.1–0.8 nm")
    axes[0].semilogy(lc.index, lc.xrsa_flux, c="tab:blue", label="XRS-A 0.05–0.4 nm")
    axes[0].semilogy(dec.index, model(xm, A, tau, bgf), c="black", ls="--", lw=1, label=f"exponentieller Abfall, τ = {tau:.1f} min")
    for lvl, name in zip((1e-6, 1e-5, 1e-4), "CMX"):
        axes[0].axhline(lvl, c="0.6", lw=0.5)
        axes[0].text(lc.index[0], lvl * 1.15, name, fontsize=8, color="0.4")
    for tt, name in ((row.t_start, "Start"), (row.t_peak, "Maximum"), (row.t_end, "Ende")):
        for ax in axes:
            ax.axvline(tt, c="0.5", ls=":", lw=0.8)
        axes[0].text(tt, 2e-3, name, fontsize=8, rotation=90, va="top")
    axes[0].set_ylim(1e-7, 3e-3)
    axes[0].set_ylabel("Fluss [W/m²]")
    axes[0].set_title(f"GOES-18 am {EVENT_DAY}: {goes_class(np.array([F_p]))[0]}")
    axes[0].legend(fontsize=8, loc="center right")
    axes[1].plot(ratio.index, ratio, c="tab:purple")
    axes[1].set_ylabel("XRS-A / XRS-B")
    axes[2].plot(deriv.index, deriv * 1e6, c="tab:green")
    axes[2].set_ylabel("dF/dt [µW/m²/s]")
    axes[2].set_xlabel("Zeit [UT]")
    fig.tight_layout()
    plt.show()
    s.F_p = F_p


def compare(s):
    """GOES-16 gegen GOES-18 in der Überlappung, fehlende Flares, der X-Flare in drei Quellen."""
    fl, fits, F_p = s.fl, s.fits, s.F_p
    f16, f18 = fl[16], fl[18]
    t0, t1 = f18.t_peak.min(), f16.t_peak.max()
    a = f18[(f18.t_peak >= t0) & (f18.t_peak <= t1)].sort_values("t_peak")
    b = f16[(f16.t_peak >= t0) & (f16.t_peak <= t1)].sort_values("t_peak")
    m = pd.merge_asof(a, b[["t_peak", "F", "klasse"]].rename(columns={"t_peak": "t16", "F": "F16", "klasse": "klasse16"}),
                      left_on="t_peak", right_on="t16", direction="nearest", tolerance=pd.Timedelta("3min"))
    both = m.dropna(subset=["F16"])
    q = both.F / both.F16
    print(f"Überlappung {t0:%Y-%m-%d} bis {t1:%Y-%m-%d}: GOES-18 {len(a)} Flares, GOES-16 {len(b)}; "
          f"{len(both)} gemeinsam (Maximum höchstens 3 min auseinander)")
    print(f"Spitzenfluss GOES-18 / GOES-16: Median {q.median():.4f}, mittlere 50 % {q.quantile(.25):.4f} bis {q.quantile(.75):.4f}")
    print(f"Gleiche Klasse bei {np.mean(both.klasse == both.klasse16):.0%} der gemeinsamen Flares")

    only18 = m[m.F16.isna() & (m.F >= 1e-5)]
    print(f"\nM- und X-Flares nur bei GOES-18: {len(only18)}")

    # Warum fehlen sie bei GOES-16? Die Datenmarken der 1-Minuten-Werte zeigen es (lädt je Tag 0.3 MB).
    def reason(tp):
        g16 = avg1m(16, f"{tp:%Y-%m-%d}")
        w = g16.xrsb_flag[(g16.index > tp - pd.Timedelta("20min")) & (g16.index < tp + pd.Timedelta("5min"))]
        w = w.fillna(2).astype(int)                  # fehlende Marke wie schlechte Daten behandeln
        if (w & 1).any():
            return "Erdschatten (Finsternis)"
        if (w & 2).any() or w.empty:
            return "schlechte oder fehlende Daten"
        return "Daten gut, Flare nicht erkannt"
    only18 = only18.assign(grund=[reason(tp) for tp in only18.t_peak], stunde=only18.t_peak.dt.hour)
    print(only18.groupby("grund").agg(n=("klasse", "size"), stärkster=("F", "max"),
                                      stunden_UT=("stunde", lambda h: sorted(set(h)))).to_string())
    big = only18.loc[only18.F.idxmax()]
    print(f"Stärkster: {big.klasse} am {big.t_peak:%Y-%m-%d %H:%M} – {big.grund}")

    # Der X-Flare vom event_day in beiden Listen und in der Echtzeitmeldung
    ev = both.loc[both.F.idxmax()]
    print(f"\n{'Quelle':<44}{'Fluss [W/m²]':>14}{'Klasse':>8}")
    print(f"{'eigene Klasse aus den Minutenwerten (GOES-18)':<44}{F_p:>14.3e}{goes_class(np.array([F_p]))[0]:>8}")
    print(f"{'Flare-Liste GOES-18':<44}{ev.F:>14.3e}{ev.klasse:>8}")
    print(f"{'Flare-Liste GOES-16':<44}{ev.F16:>14.3e}{ev.klasse16:>8}")
    print(f"{'NOAA SWPC Echtzeit (auch in HEK)':<44}{9.0e-4:>14.3e}{'X9.0':>8}")
    best = fits["ohne Hintergrund ΔF"][1]
    print(f"\nExponent der Spitzenflüsse ohne Hintergrund: α = {best.alpha:.2f} ± {best.fehler:.2f}; "
          f"Aschwanden & Freeland (2012), 37 Jahre GOES: α ≈ 1.98")

    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.hist(q, bins=np.linspace(0.95, 1.05, 81), color="0.4")
    ax.axvline(1, c="tab:red", lw=1)
    ax.set_xlabel("Spitzenfluss GOES-18 / GOES-16")
    ax.set_ylabel("Flares")
    ax.set_title(f"{len(both)} gemeinsame Flares")
    fig.tight_layout()
    plt.show()
