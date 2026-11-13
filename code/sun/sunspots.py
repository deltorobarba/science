"""Der Sonnenfleckenzyklus für sun.ipynb: 13-Monats-Glättung, Minima und Maxima, Periodogramm, Kurvenform jedes Zyklus
(Hathaway), Waldmeier-Effekt, Prognose für Zyklus 25 und Vergleich mit der offiziellen Reihe.

Daten: monatliche Sonnenfleckenzahl seit 1749 und ihre offizielle Glättung von SILSO (`sundata.silso`). Alle Schritte
teilen sich ein Zustandsobjekt, das `load` anlegt.
"""
from types import SimpleNamespace

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.optimize import curve_fit, brentq
from scipy.stats import t as student_t
from astropy.timeseries import LombScargle

import sundata

C_SHAPE = 0.71                        # Formparameter c der Hathaway-Kurve


def load(refresh=False):
    """Monatsmittel und offizielle Glättung; Stand der Reihe."""
    monthly = sundata.silso("snmtotcsv", refresh)          # Monatsmittel
    official = sundata.silso("snmstotcsv", refresh)        # offizielle 13-Monats-Glättung
    t, sn = monthly.t.values, monthly.sn.values

    last = monthly.iloc[-1]
    last_def = monthly[monthly.definitiv == 1].iloc[-1]
    last_sm = official.dropna(subset=["sn"]).iloc[-1]

    def ym(row):
        return f"{int(row.jahr)}-{int(row.monat):02d}"
    print(f"Monatsmittel:  {len(monthly)} Monate, {ym(monthly.iloc[0])} bis {ym(last)} (letzter Wert {last.sn:.1f})")
    print(f"Endgültig bis: {ym(last_def)}; danach vorläufig")
    print(f"Offiziell geglättet bis {ym(last_sm)} ({last_sm.sn:.1f})")
    print(f"Höchstes Monatsmittel: {np.nanmax(sn):.1f} ({t[np.nanargmax(sn)]:.2f})")
    return SimpleNamespace(monthly=monthly, official=official, t=t, sn=sn)


def H(f):
    """Übertragungsfunktion der 13-Monats-Glättung (Gewichte 1/24, 1/12, …, 1/12, 1/24) bei der Frequenz f [1/Monat]."""
    return np.cos(np.pi * f) * np.sin(12 * np.pi * f) / (12 * np.sin(np.pi * f))


def smoothing(s):
    """Eigene 13-Monats-Glättung gegen die offizielle, und welche Perioden sie durchlässt."""
    t, sn, official = s.t, s.sn, s.official
    w = np.r_[0.5, np.ones(11), 0.5] / 12
    own = np.convolve(sn, w, mode="same")
    own[:6] = own[-6:] = np.nan               # am Rand fehlen Nachbarmonate

    diff = own - official.sn.values
    print(f"Eigene minus offizielle Glättung: max |Δ| = {np.nanmax(np.abs(diff)):.3f}, "
          f"RMS = {np.sqrt(np.nanmean(diff ** 2)):.3f}  (SILSO rundet auf 0.1)")
    for months in (132, 60, 24, 12, 6):
        print(f"Periode {months:>3} Monate: H = {H(1 / months):+.3f}")
    peak_month, peak_smooth = np.nanmax(sn), np.nanmax(own)
    print(f"Höchstes Monatsmittel {peak_month:.1f} gegen höchsten geglätteten Wert {peak_smooth:.1f}")

    fig, axes = plt.subplots(1, 2, figsize=(13, 3.8), gridspec_kw={"width_ratios": [2, 1]})
    sel = t > 1996
    axes[0].plot(t[sel], sn[sel], c="0.7", lw=0.8, label="Monatsmittel")
    axes[0].plot(t[sel], own[sel], c="black", lw=1.8, label="eigene 13-Monats-Glättung")
    axes[0].plot(official.t[sel], official.sn[sel], c="tab:orange", lw=1, ls="--", label="offizielle Glättung")
    axes[0].set_xlabel("Jahr")
    axes[0].set_ylabel("Sonnenfleckenzahl")
    axes[0].set_title("Zyklen 23 bis 25")
    axes[0].legend(fontsize=8)
    f = np.linspace(1e-4, 0.5, 2000)
    axes[1].plot(1 / f, np.abs(H(f)), c="black")
    axes[1].set_xscale("log")
    axes[1].set_xlabel("Periode [Monate]")
    axes[1].set_ylabel("|H|")
    axes[1].set_title("Übertragungsfunktion der Glättung")
    for p in (12, 6, 4, 3):
        axes[1].axvline(p, c="tab:red", lw=0.5, ls=":")
    fig.tight_layout()
    plt.show()
    s.own = own


def extrema(s):
    """Minima und Maxima der Glättung, Zykluslängen, Anstieg und Abfall."""
    t, sn, own = s.t, s.sn, s.own
    ok = np.isfinite(own)
    tt, yy = t[ok], own[ok]
    # Ein Zyklus dauert mindestens 7 Jahre; die Prominenz 30 trennt echte Extrema von Zacken
    i_max, _ = find_peaks(yy, distance=7 * 12, prominence=30)
    i_min, _ = find_peaks(-yy, distance=7 * 12, prominence=30)
    t_min, a_min = tt[i_min], yy[i_min]
    t_max, a_max = tt[i_max], yy[i_max]

    rows = []
    for k, tm in enumerate(t_min):                       # Minimum k eröffnet Zyklus k+1 (Zyklus 1 ab 1755)
        nxt = t_min[k + 1] if k + 1 < len(t_min) else np.nan
        m = (t_max > tm) & ((t_max < nxt) | np.isnan(nxt))
        rows.append(dict(zyklus=k + 1, t_min=tm, sn_min=a_min[k],
                         t_max=t_max[m][0] if m.any() else np.nan, sn_max=a_max[m][0] if m.any() else np.nan,
                         laenge=nxt - tm))
    cyc = pd.DataFrame(rows)
    cyc["anstieg"] = cyc.t_max - cyc.t_min
    cyc["abfall"] = cyc.laenge - cyc.anstieg
    pd.set_option("display.width", 160)
    print(cyc.round(2).to_string(index=False))

    done = cyc.dropna(subset=["laenge"])
    print(f"\n{len(done)} abgeschlossene Zyklen: Länge {done.laenge.mean():.2f} ± {done.laenge.std(ddof=1):.2f} Jahre "
          f"(kürzester {done.laenge.min():.1f}, längster {done.laenge.max():.1f})")
    print(f"Anstieg {done.anstieg.mean():.2f} ± {done.anstieg.std(ddof=1):.2f} Jahre, "
          f"Abfall {done.abfall.mean():.2f} ± {done.abfall.std(ddof=1):.2f} Jahre")
    print(f"Maxima: {cyc.sn_max.min():.0f} (Zyklus {cyc.zyklus[cyc.sn_max.idxmin()]}) bis "
          f"{cyc.sn_max.max():.0f} (Zyklus {cyc.zyklus[cyc.sn_max.idxmax()]})")

    fig, ax = plt.subplots(figsize=(14, 4))
    ax.plot(t, sn, c="0.75", lw=0.5)
    ax.plot(t, own, c="black", lw=1.2)
    ax.plot(t_min, a_min, "v", c="tab:blue", ms=5, label="Minimum")
    ax.plot(t_max, a_max, "^", c="tab:red", ms=5, label="Maximum")
    for _, r in cyc.dropna(subset=["t_max"]).iterrows():
        ax.text(r.t_max, r.sn_max + 25, f"{r.zyklus:.0f}", ha="center", fontsize=8)
    ax.axvspan(1790, 1830, color="tab:blue", alpha=0.08, label="Dalton-Minimum")
    ax.set_xlabel("Jahr")
    ax.set_ylabel("Sonnenfleckenzahl")
    ax.set_title("Sonnenfleckenzahl 1749 bis heute mit Zyklusnummern")
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    plt.show()
    s.__dict__.update(cyc=cyc, done=done, t_min=t_min, a_min=a_min, t_max=t_max)


def periodogram(s):
    """Lomb-Scargle-Periodogramm der Monatsmittel über 3 bis 150 Jahre."""
    t, sn, done = s.t, s.sn, s.done
    good = np.isfinite(sn)
    freq = np.linspace(1 / 150, 1 / 3, 20000)          # Perioden 3 bis 150 Jahre
    power = LombScargle(t[good], sn[good]).power(freq)
    P_best = 1 / freq[np.argmax(power)]
    half = power > power.max() / 2
    near = np.abs(1 / freq - P_best) < 3
    fwhm = np.ptp(1 / freq[half & near])
    T_total = np.ptp(t[good])
    print(f"Höchster Peak: P = {P_best:.2f} Jahre, Leistung {power.max():.2f}")
    print(f"Halbwertsbreite des Peaks: {fwhm:.2f} Jahre; erwartet etwa P²/T = {P_best ** 2 / T_total:.2f} Jahre")
    print(f"Mittlere Zykluslänge (Schritt 3): {done.laenge.mean():.2f} Jahre, Streuung ± {done.laenge.std(ddof=1):.2f}")

    pk, _ = find_peaks(power, prominence=0.01)          # weitere lokale Maxima
    top = pk[np.argsort(power[pk])[::-1][:6]]
    print("Die sechs höchsten Peaks:", ", ".join(f"{1 / freq[i]:.1f} J ({power[i]:.2f})" for i in top))

    fig, ax = plt.subplots(figsize=(11, 3.8))
    ax.plot(1 / freq, power, c="black", lw=1)
    ax.axvspan(done.laenge.min(), done.laenge.max(), color="tab:orange", alpha=0.15,
               label="Spanne der einzelnen Zykluslängen")
    ax.axvline(P_best, c="tab:red", ls="--", lw=1, label=f"Peak {P_best:.2f} Jahre")
    ax.set_xscale("log")
    ax.set_xlabel("Periode [Jahre]")
    ax.set_ylabel("Lomb-Scargle-Leistung")
    ax.set_title("Periodogramm der monatlichen Sonnenfleckenzahl")
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()


def hathaway(x_t, a, b, t0, c=C_SHAPE):
    """Kurvenform eines Zyklus nach Hathaway, Wilson und Reichmann (1994)."""
    x = np.clip(x_t - t0, 0, None)
    with np.errstate(over="ignore"):
        return a * x ** 3 / (np.exp(x ** 2 / b ** 2) - c)


def shapes(s):
    """Hathaway-Kurve an jeden Zyklus anpassen."""
    t, sn, own, cyc = s.t, s.sn, s.own, s.cyc
    # Maximum der Kurve: e^u (3 - 2u) = 3c
    u_star = brentq(lambda u: np.exp(u) * (3 - 2 * u) - 3 * C_SHAPE, 0.1, 1.49)
    k_rise, k_amp = np.sqrt(u_star), u_star ** 1.5 / (np.exp(u_star) - C_SHAPE)
    print(f"u* = {u_star:.3f}:  Maximum bei t0 + {k_rise:.3f}·b,  Höhe {k_amp:.3f}·a·b³")

    fits = []
    for k, r in cyc.iterrows():
        hi = r.t_min + r.laenge if np.isfinite(r.laenge) else t[-1] + 0.01
        m = (t >= r.t_min) & (t < hi) & np.isfinite(sn)
        p, cov = curve_fit(hathaway, t[m], sn[m], p0=[3, 4, r.t_min - 0.3], maxfev=20000)
        resid = sn[m] - hathaway(t[m], *p)
        fits.append(dict(zyklus=r.zyklus, a=p[0], b=p[1], t0=p[2], a_err=np.sqrt(cov[0, 0]),
                         t_max_fit=p[2] + k_rise * p[1], A_fit=k_amp * p[0] * p[1] ** 3,
                         rms=np.sqrt(np.mean(resid ** 2)), n=m.sum()))
    fits = pd.DataFrame(fits)
    print(fits.round(2).to_string(index=False))
    print(f"\nMittel über die Zyklen 1-24: b = {fits.b[:24].mean():.2f} ± {fits.b[:24].std(ddof=1):.2f} Jahre, "
          f"Streuung der Monatswerte um die Kurve {fits.rms[:24].mean():.0f}")

    fig, axes = plt.subplots(5, 5, figsize=(15, 11), sharey=True)
    for ax, (_, r), (_, fp) in zip(axes.flat, cyc.iterrows(), fits.iterrows()):
        hi = r.t_min + r.laenge if np.isfinite(r.laenge) else t[-1]
        m = (t >= r.t_min - 1) & (t <= hi + 1)
        ax.plot(t[m], sn[m], c="0.7", lw=0.6)
        ax.plot(t[m], own[m], c="black", lw=1)
        tf = np.linspace(r.t_min, hi, 300)
        ax.plot(tf, hathaway(tf, fp.a, fp.b, fp.t0), c="tab:red", lw=1.5)
        ax.set_title(f"Zyklus {r.zyklus:.0f} ({r.t_min:.0f})", fontsize=9)
        ax.tick_params(labelsize=7)
    fig.suptitle("Monatsmittel (grau), 13-Monats-Glättung (schwarz) und Hathaway-Kurve (rot)")
    fig.tight_layout()
    plt.show()
    s.fits = fits


def waldmeier(s):
    """Anstiegszeit gegen Höhe des Maximums und der Zusammenhang der Formparameter b(a)."""
    d = s.cyc.merge(s.fits, on="zyklus")[:24]               # nur abgeschlossene Zyklen
    n = len(d)

    def corr_test(x, y):
        r = np.corrcoef(x, y)[0, 1]
        tval = r * np.sqrt((n - 2) / (1 - r ** 2))
        return r, 2 * student_t.sf(abs(tval), n - 2)

    r1, p1 = corr_test(d.anstieg, d.sn_max)
    r2, p2 = corr_test(d.laenge, d.sn_max)
    print(f"Anstiegszeit gegen Maximum: r = {r1:+.2f}, p = {p1:.1e}  (n = {n})")
    print(f"Zykluslänge gegen Maximum:  r = {r2:+.2f}, p = {p2:.2f}")

    X = np.c_[np.ones(n), d.a ** -0.25]
    (b0, b1), *_ = np.linalg.lstsq(X, d.b, rcond=None)
    b_rms = np.std(d.b - X @ np.r_[b0, b1], ddof=2)
    print(f"Zusammenhang b(a) = {b0:.2f} + {b1:.2f}·a^(-1/4)  [Jahre], Streuung ± {b_rms:.2f} Jahre")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    axes[0].scatter(d.sn_max, d.anstieg, c="black", s=18)
    for _, r in d.iterrows():
        axes[0].annotate(f"{r.zyklus:.0f}", (r.sn_max, r.anstieg), fontsize=7, xytext=(3, 2), textcoords="offset points")
    cf = np.polyfit(d.sn_max, d.anstieg, 1)
    xs = np.linspace(d.sn_max.min(), d.sn_max.max(), 10)
    axes[0].plot(xs, np.polyval(cf, xs), c="tab:red", lw=1, label=f"Gerade, r = {r1:.2f}")
    axes[0].set_xlabel("Maximum der geglätteten Sonnenfleckenzahl")
    axes[0].set_ylabel("Anstieg Minimum → Maximum [Jahre]")
    axes[0].set_title("Waldmeier-Effekt")
    axes[0].legend(fontsize=8)
    axes[1].scatter(d.a, d.b, c="black", s=18)
    aa = np.linspace(d.a.min() * 0.9, d.a.max() * 1.05, 100)
    axes[1].plot(aa, b0 + b1 * aa ** -0.25, c="tab:red", lw=1, label="b = b0 + b1·a^(-1/4)")
    axes[1].set_xlabel("a [Sonnenflecken / Jahr³]")
    axes[1].set_ylabel("b [Jahre]")
    axes[1].set_title("Die Formparameter hängen zusammen")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()
    s.b0, s.b1 = b0, b1


def forecast(s, years=(1.5, 2, 3, 4)):
    """Zyklus 25 aus seinen ersten Jahren vorhersagen (Hathaway-Kurve mit b aus a)."""
    t, sn, own, cyc, fits, b0, b1 = s.t, s.sn, s.own, s.cyc, s.fits, s.b0, s.b1

    def hathaway1(x_t, a, t0):
        return hathaway(x_t, a, b0 + b1 * a ** -0.25, t0)

    t_start25 = cyc.t_min.iloc[24]
    full = fits.iloc[24]
    truth_t, truth_A = cyc.t_max.iloc[24], cyc.sn_max.iloc[24]
    tf = np.linspace(t_start25, t_start25 + 11, 600)
    fig, ax = plt.subplots(figsize=(11, 4.2))
    m_all = t >= t_start25 - 0.5
    ax.plot(t[m_all], sn[m_all], c="0.7", lw=0.8, label="Monatsmittel")
    ax.plot(t[m_all], own[m_all], c="black", lw=1.5, label="13-Monats-Glättung")
    forecasts = []
    for yrs, col in zip(years, ("tab:purple", "tab:blue", "tab:green", "tab:orange", "tab:brown")):
        m = (t >= t_start25) & (t < t_start25 + yrs)
        p, cov = curve_fit(hathaway1, t[m], sn[m], p0=[3, t_start25 - 0.3], bounds=([0.05, t_start25 - 3], [50, t_start25 + 2]))
        f = hathaway1(tf, *p)
        # Unsicherheit der Höhe aus der Kovarianz (Monte Carlo über a und t0)
        draws = np.random.default_rng(1).multivariate_normal(p, cov, 400)
        draws = draws[draws[:, 0] > 0]
        peaks = [hathaway1(tf, *q).max() for q in draws]
        forecasts.append(dict(jahre=yrs, a=p[0], t0=p[1], maximum=f.max(), fehler=np.std(peaks), zeitpunkt=tf[np.argmax(f)]))
        ax.plot(tf, f, c=col, lw=1.3, label=f"Prognose aus {yrs} Jahren: {f.max():.0f} ± {np.std(peaks):.0f}")
        ax.axvline(t_start25 + yrs, c=col, lw=0.6, ls=":")
    ax.plot(tf, hathaway(tf, full.a, full.b, full.t0), c="tab:red", lw=1, ls="--", label=f"Fit an alle Daten: {full.A_fit:.0f}")
    ax.plot(2025 + 6.5 / 12, 115, "s", c="tab:brown", ms=8, label="NOAA/NASA-Panel 2019: 115 im Juli 2025")
    ax.set_xlabel("Jahr")
    ax.set_ylabel("Sonnenfleckenzahl")
    ax.set_title("Zyklus 25: Prognosen aus den ersten Jahren")
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    plt.show()

    fc = pd.DataFrame(forecasts)
    print(fc.round(2).to_string(index=False))
    print(f"\nBeobachtet (geglättet): Maximum {truth_A:.1f} bei {truth_t:.2f};  Fit an alle Daten: {full.A_fit:.1f} bei {full.t_max_fit:.2f}")
    s.fc, s.full = fc, full


def compare(s):
    """Eigene Extrema gegen die offizielle Glättung; Zyklus 25 gegen die Vorhersage des NOAA/NASA-Panels von 2019."""
    official, t_min, a_min, t_max, fc, full = s.official, s.t_min, s.a_min, s.t_max, s.fc, s.full
    o = official.dropna(subset=["sn"])
    oi_max, _ = find_peaks(o.sn.values, distance=7 * 12, prominence=30)
    oi_min, _ = find_peaks(-o.sn.values, distance=7 * 12, prominence=30)
    o_tmax, o_tmin = o.t.values[oi_max], o.t.values[oi_min]
    print(f"Offizielle Reihe: {len(o_tmin)} Minima, {len(o_tmax)} Maxima;  eigene: {len(t_min)} Minima, {len(t_max)} Maxima")
    if len(o_tmin) == len(t_min) and len(o_tmax) == len(t_max):
        print(f"Größte Abweichung der Daten: Minima {np.max(np.abs(o_tmin - t_min)) * 12:.0f} Monate, "
              f"Maxima {np.max(np.abs(o_tmax - t_max)) * 12:.0f} Monate")
        for k in np.flatnonzero(np.abs(o_tmin - t_min) > 0.01):
            print(f"  Minimum vor Zyklus {k + 1}: eigene {t_min[k]:.2f} ({a_min[k]:.2f}), "
                  f"offiziell {o_tmin[k]:.2f} ({o.sn.values[oi_min[k]]:.1f})")

    print("\nZyklus 25")
    print(f"{'':<36}{'Maximum':>10}{'Zeitpunkt':>12}")
    print(f"{'NOAA/NASA-Panel (Dezember 2019)':<36}{'115':>10}{'2025.54':>12}   (Spanne 105-125, ± 8 Monate)")
    for _, r in fc.iterrows():
        print(f"{'eigene Prognose aus ' + str(r.jahre) + ' Jahren':<36}{r.maximum:>10.0f}{r.zeitpunkt:>12.2f}")
    print(f"{'eigener Fit an alle Daten':<36}{full.A_fit:>10.0f}{full.t_max_fit:>12.2f}")
    print(f"{'offizielle Glättung (beobachtet)':<36}{o.sn.values[oi_max[-1]]:>10.1f}{o_tmax[-1]:>12.2f}")
