"""Ein Gravitationswellen-Ereignis nach Wahl (bis 2026-11-18 gw150914.py, fest GW150914, das erste gemessene Signal):
Steckbrief aus dem Katalog von gwtc.py, LIGO-Rohdaten von H1 und L1 über GWOSC, Rauschspektrum, Whitening und Bandpass, Q-Transformation, Chirp-Masse aus der Zeit-Frequenz-Kurve und Vergleich mit dem Katalog.

Für gravitational_waves.ipynb aus gw150914.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, raw_data, noise_spectrum, whitened, spectrogram, chirp_mass, robustness, catalog_check.
Downloads und Cache: data/gravitational_waves/ (`gwdata.py`).
"""
import gwdata                                         # zuerst: Cache-Ordner für astropy (auch für gwpy)
import numpy as np
import matplotlib.pyplot as plt
from gwosc.api import fetch_event_json
from gwosc.datasets import event_gps
from gwpy.timeseries import TimeSeries
from astropy.time import Time

GWPY_STIL = {k: v for k, v in plt.rcParams.items() if v != gwdata.RC_VORHER.get(k)}   # was gwpy beim Import umgestellt hat
plt.rcParams.update(gwdata.RC_VORHER)                # die übrigen Teile von astrophysics.ipynb behalten ihren Plotstil


def _steckbrief(event, gps):
    """Werte des Ereignisses aus dem bereinigten Katalog (gwtc.selection), wenn es dort steht."""
    import gwtc
    cat = getattr(gwtc, "cat", None)
    row = None if cat is None else cat[(cat["name"] == event) | cat["name"].str.startswith(event + "_")]
    if row is None or len(row) == 0:
        print(f"{event}: nicht im bereinigten Katalog (gwtc.selection); die Daten werden trotzdem geladen")
        return
    r = row.iloc[0]
    print(f"Ereignis:    {r['name']}  (Katalog {r['katalog']}, Kampagne {r['kampagne']}, Typ {r['typ']})")
    print(f"Zeit:        {Time(float(gps), format='gps').utc.iso[:19]} UTC")
    if r["typ"] != "ohne Parameter":
        print(f"Massen:      m1 = {r['m1']:.1f} M☉, m2 = {r['m2']:.1f} M☉ (im Ruhesystem der Quelle); "
              f"Chirp-Masse {r['mc']:.1f} M☉, Endmasse {r['m_end']:.1f} M☉")
        print(f"Entfernung:  D_L = {r['dl']:.0f} Mpc, z = {r['z']:.2f}")
    far = f", Fehlalarmrate {r['far']:.1e} pro Jahr" if np.isfinite(r["far"]) else ""
    print(f"Signal:      Netzwerk-SNR {r['snr']:.1f}{far}")


def load(event="GW150914", detectors=("H1", "L1")):
    """49. Ein Ereignis wählen: Steckbrief und 32 s Messdaten um das Ereignis (Zellen 5 von gw150914.ipynb)."""
    global EREIGNIS, daten, gps, ifo
    plt.rcParams.update(GWPY_STIL)                   # die Daten im Plotstil von gwpy (wie im früheren Notebook)
    EREIGNIS = event
    gps = event_gps(EREIGNIS)
    _steckbrief(EREIGNIS, gps)
    print("GPS-Zeit des Ereignisses:", gps)

    daten = {}
    for ifo in detectors:
        daten[ifo] = TimeSeries.fetch_open_data(ifo, gps - 16, gps + 16, sample_rate=4096, cache=True)
        print(f"{ifo}: {daten[ifo].duration.value:.0f} s, {daten[ifo].sample_rate.value:.0f} Hz")


def raw_data():
    """50. Rohdaten (Zellen 8 von gw150914.ipynb)."""
    global ax, fig, h, ifo
    fig, ax = plt.subplots(figsize=(10, 3.5))
    for ifo in daten:
        h = daten[ifo]
        ax.plot(h.times.value - gps, h.value, lw=0.6, label=ifo)
    ax.set_xlabel("Zeit relativ zum Ereignis [s]")
    ax.set_ylabel("Strain")
    ax.set_title(f"{EREIGNIS}: Rohdaten")
    ax.legend()
    plt.show()


def noise_spectrum():
    """Rauschspektrum (Zellen 11 von gw150914.ipynb)."""
    global asd, ax, fig, ifo
    fig, ax = plt.subplots(figsize=(9, 4.5))
    for ifo in daten:
        asd = daten[ifo].asd(fftlength=4, overlap=2)
        ax.loglog(asd.frequencies.value, asd.value, lw=0.8, label=ifo)
    ax.set_xlim(10, 2000)
    ax.set_ylim(1e-24, 1e-19)
    ax.set_xlabel("Frequenz [Hz]")
    ax.set_ylabel("Amplitudenspektraldichte [1/√Hz]")
    ax.set_title(f"Rauschspektrum um {EREIGNIS}")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    plt.show()


def whitened():
    """51. Whitening und Bandpass (Zellen 14 von gw150914.ipynb)."""
    global VERSATZ, VORZEICHEN, ax, fig, gefiltert, h1, l1
    gefiltert = {ifo: daten[ifo].whiten(4, 2).bandpass(35, 350) for ifo in daten}
    h1 = gefiltert["H1"].crop(gps - 0.2, gps + 0.05)
    l1 = gefiltert["L1"].crop(gps - 0.2, gps + 0.05)

    # Versatz und Vorzeichen aus der Kreuzkorrelation innerhalb der Lichtlaufzeit (10 ms); bis 2026-11-18 fest
    # 6.9 ms und −1, die veröffentlichten Werte für GW150914
    fs = h1.sample_rate.value
    m = int(0.010 * fs)
    x, y = h1.value, l1.value
    lags = np.arange(-m, m + 1)
    norm = np.sqrt(np.dot(x[m:-m], x[m:-m]) * np.dot(y[m:-m], y[m:-m]))
    cc = np.array([np.dot(x[m:-m], np.roll(y, k)[m:-m]) for k in lags]) / norm
    best = np.argmax(np.abs(cc))
    VERSATZ, VORZEICHEN = lags[best] / fs, np.sign(cc[best])
    print(f"Kreuzkorrelation: L1 um {VERSATZ * 1e3:+.1f} ms verschoben, Vorzeichen {VORZEICHEN:+.0f}, "
          f"Korrelation {cc[best]:+.2f}")

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(h1.times.value - gps, h1.value, label="H1")
    ax.plot(l1.times.value - gps + VERSATZ, VORZEICHEN * l1.value,
            label=f"L1, um {abs(VERSATZ) * 1e3:.1f} ms verschoben" + (" und invertiert" if VORZEICHEN < 0 else ""))
    ax.set_xlim(-0.2, 0.05)
    ax.set_xlabel("Zeit relativ zum Ereignis [s]")
    ax.set_ylabel("Strain, geweißt (Einheiten des Rauschens)")
    ax.set_title(f"{EREIGNIS} nach Whitening und Bandpass")
    ax.legend()
    plt.show()


def spectrogram():
    """52. Zeit-Frequenz-Bild (Zellen 17 von gw150914.ipynb)."""
    global ax, plot, qt
    qt = daten["H1"].q_transform(outseg=(gps - 0.3, gps + 0.05), qrange=(4, 64), frange=(20, 500))

    plot = qt.plot(figsize=(10, 4.5))
    ax = plot.gca()
    ax.set_xscale("seconds", epoch=gps)
    ax.set_yscale("log")
    ax.set_ylabel("Frequenz [Hz]")
    ax.set_title(f"H1: Q-Transformation um {EREIGNIS}")
    ax.colorbar(label="Normierte Energie", clim=(0, 25))
    plt.show()
    plt.style.use("default")      # der nächste Teil (Sonne) zeigt wieder den Stil von matplotlib, wie bisher nach gwtc.load


def chirp_mass():
    """Die Chirp-Masse (Zellen 20 von gw150914.ipynb)."""
    global G, M_SONNE, M_chirp, S, a, ax1, ax2, b, c, chirp_frequenz, chirp_suche, fig
    global im, massen, t, t_c, tau, zeiten_c
    G, c, M_SONNE = 6.674e-11, 2.998e8, 1.989e30


    def chirp_frequenz(tau, M_chirp):
        """Newtonscher Chirp: Frequenz tau Sekunden vor der Verschmelzung, Chirp-Masse in Sonnenmassen."""
        X = G * M_chirp * M_SONNE / c**3                  # G·M/c³ in Sekunden
        return (1 / np.pi) * (5 / (256 * tau)) ** (3 / 8) * X ** (-5 / 8)


    def chirp_suche(qt, massen, zeiten_c, tau_min=0.01, tau_max=0.15):
        """Mittlere Energie der Q-Transformation entlang der vorhergesagten Kurve, für jedes Paar (M, t_c)."""
        t = qt.times.value - gps
        f = qt.frequencies.value
        E = qt.value                                       # Form: (Zeit, Frequenz)
        S = np.zeros((len(massen), len(zeiten_c)))
        for a, M in enumerate(massen):
            for b, tc in enumerate(zeiten_c):
                tau = tc - t
                m = (tau > tau_min) & (tau < tau_max)      # nur der Teil vor der Verschmelzung
                fi = np.searchsorted(f, chirp_frequenz(tau[m], M)).clip(0, len(f) - 1)
                S[a, b] = E[np.where(m)[0], fi].mean()
        return S


    massen = np.arange(15, 60.1, 0.5)                      # Chirp-Masse in Sonnenmassen
    zeiten_c = np.arange(-0.02, 0.05, 0.001)               # Verschmelzungszeit relativ zu gps in Sekunden
    S = chirp_suche(qt, massen, zeiten_c)
    a, b = np.unravel_index(np.argmax(S), S.shape)
    M_chirp, t_c = massen[a], zeiten_c[b]
    print(f"H1: Chirp-Masse im Detektorsystem {M_chirp:.1f} Sonnenmassen, Verschmelzung bei {1000 * t_c:.0f} ms")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.5))
    im = ax1.pcolormesh(1000 * zeiten_c, massen, S, shading="auto")
    ax1.plot(1000 * t_c, M_chirp, "w+", ms=14, mew=2)
    ax1.set_xlabel("Verschmelzungszeit t_c [ms]")
    ax1.set_ylabel("Chirp-Masse [Sonnenmassen]")
    ax1.set_title("Mittlere Energie entlang der Chirp-Kurve")
    fig.colorbar(im, ax=ax1)

    t = qt.times.value - gps
    ax2.pcolormesh(t, qt.frequencies.value, qt.value.T, shading="auto", vmax=25)
    tau = np.linspace(0.15, 0.01, 200)
    ax2.plot(t_c - tau, chirp_frequenz(tau, M_chirp), "w--", lw=2, label=f"Newtonscher Chirp, {M_chirp:.1f} Sonnenmassen")
    ax2.set_yscale("log")
    ax2.set_ylim(20, 500)
    ax2.set_xlabel("Zeit relativ zum Ereignis [s]")
    ax2.set_ylabel("Frequenz [Hz]")
    ax2.set_title("H1: Q-Transformation mit der besten Chirp-Kurve")
    ax2.legend(loc="upper left")
    plt.tight_layout()
    plt.show()


def robustness():
    """Die Chirp-Masse (Zellen 23 von gw150914.ipynb)."""
    global M_, M_mittel, M_streuung, S_, ifo, q, tau_max, tau_min, werte
    werte = []
    for ifo in ["H1", "L1"]:
        q = daten[ifo].q_transform(outseg=(gps - 0.3, gps + 0.05), qrange=(4, 64), frange=(20, 500))
        for tau_min, tau_max in [(0.01, 0.15), (0.02, 0.2)]:
            S_ = chirp_suche(q, massen, zeiten_c, tau_min, tau_max)
            M_ = massen[np.unravel_index(np.argmax(S_), S_.shape)[0]]
            werte.append(M_)
            print(f"{ifo}, tau von {tau_min} bis {tau_max} s: {M_:.1f} Sonnenmassen")
    M_mittel, M_streuung = np.mean(werte), np.std(werte)
    print(f"Eigene Messung: {M_mittel:.1f} ± {M_streuung:.1f} Sonnenmassen (Mittelwert und Streuung der vier Werte)")


def catalog_check():
    """Vergleich mit dem Katalog (Zellen 26 von gw150914.ipynb)."""
    global Mc_quelle, eintraege, schluessel, z
    eintraege = fetch_event_json(EREIGNIS)["events"]
    schluessel = sorted(eintraege)[-1]                     # neueste Version des Katalogeintrags
    Mc_quelle, z = eintraege[schluessel]["chirp_mass_source"], eintraege[schluessel]["redshift"]
    print(f"Katalog ({schluessel}): Chirp-Masse der Quelle {Mc_quelle:.1f}, Rotverschiebung z = {z:.2f}")
    print(f"Katalog im Detektorsystem, (1 + z) · M: {(1 + z) * Mc_quelle:.1f} Sonnenmassen")
    print(f"Eigene Messung:                        {M_mittel:.1f} ± {M_streuung:.1f} Sonnenmassen")
