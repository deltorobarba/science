"""LIGO-Rauschen für principal_axes.ipynb: Hauptachsen stationären Rauschens und Whitening von GW150914.

Daten: die öffentlichen 32-s-Ausschnitte um GW150914 (Hanford H1 und Livingston L1, 4096 Hz, je etwa 1 MB) vom Gravitational
Wave Open Science Center (gwosc.org), als HDF5 mit requests geladen (urllib scheitert lokal am Zertifikat). Das Modul
schneidet das Rauschen in kurze Abschnitte, zerlegt ihre Kovarianz in Hauptachsen und vergleicht sie mit dem
Leistungsspektrum (Welch), und es macht das Whitening: jede Fourier-Komponente durch die Wurzel ihres Spektrums teilen.
"""
import time
from pathlib import Path

import h5py
import numpy as np
import requests
import matplotlib.pyplot as plt
from scipy import signal

URL = "https://gwosc.org/eventapi/json/GWTC-1-confident/GW150914/v3/"
FILES = {"H1": "H-H1_GWOSC_4KHZ_R1-1126259447-32.hdf5", "L1": "L-L1_GWOSC_4KHZ_R1-1126259447-32.hdf5"}
GPS_EVENT = 1126259462.4                          # Zeitpunkt der Verschmelzung (GPS-Sekunden)


def load(cache):
    """Beide Detektoren laden (Cache in `cache`). Gibt {Detektor: Strain}, die Abtastrate und die Zeit relativ zum Ereignis."""
    cache = Path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    out = {}
    for ifo, fname in FILES.items():
        path = cache / fname
        for i in range(3):
            if path.exists():
                break
            try:
                d = requests.get(URL + fname, timeout=60).content
                if d[:4] == b"\x89HDF":
                    path.write_bytes(d)
            except requests.RequestException:
                time.sleep(2 * (i + 1))
        with h5py.File(path) as h:
            out[ifo] = h["strain/Strain"][()]
            fs = 1 / h["strain/Strain"].attrs["Xspacing"]
            t0 = h["meta/GPSstart"][()]
    t = np.arange(len(out["H1"])) / fs + t0 - GPS_EVENT
    print(f"GW150914: {len(out)} Detektoren, je {len(t) / fs:.0f} s mit {fs:.0f} Hz; Strain streut um {out['H1'].std():.1e}")
    return out, fs, t


def segment_axes(x, fs, t, length=128, gap=2.0):
    """Rauschen in Abschnitte zu `length` Samples schneiden (ohne ±gap s um das Ereignis), Kovarianz zerlegen.

    Gibt Eigenwerte und -vektoren (absteigend), die Frequenz jedes Eigenvektors (Maximum seines Spektrums) und die
    Zahl der Abschnitte zurück.
    """
    ok = np.abs(t) > gap
    segs = np.array([x[i:i + length] for i in range(0, len(x) - length, length) if ok[i:i + length].all()])
    segs = segs - segs.mean(axis=1, keepdims=True)
    w, V = np.linalg.eigh(segs.T @ segs / len(segs))
    w, V = w[::-1], V[:, ::-1]
    F = np.abs(np.fft.rfft(V, n=8 * length, axis=0))
    freq = np.fft.rfftfreq(8 * length, 1 / fs)[np.argmax(F, axis=0)]
    return w, V, freq, len(segs)


def psd(x, fs, seconds=4):
    """Einseitiges Leistungsspektrum nach Welch (Abschnitte von `seconds` s), in 1/Hz."""
    return signal.welch(x, fs, nperseg=int(seconds * fs))


def plot_axes(x, fs, t, length=128, show=4):
    """Links die obersten Hauptachsen als Kurven, rechts jeder Eigenwert bei seiner Frequenz über dem Welch-Spektrum."""
    w, V, freq, n = segment_axes(x, fs, t, length)
    f, P = psd(x, fs, seconds=length * 4 / fs)
    pos = w > 0
    ratio = w[pos] / (np.interp(freq[pos], f, P) * fs / 2)
    print(f"{n} Abschnitte zu {length} Samples ({length / fs * 1000:.0f} ms), Kovarianz {length} × {length}")
    print("Oberste Achsen bei " + ", ".join(f"{fr:.0f} Hz" for fr in freq[:8]))
    print(f"Eigenwert / (Spektrum · fs/2) an der Frequenz der Achse: Median {np.median(ratio):.2f}, "
          f"mittlere Hälfte {np.percentile(ratio, 25):.2f} bis {np.percentile(ratio, 75):.2f}")
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    ms = np.arange(length) / fs * 1000
    for i in range(show):
        axes[0].plot(ms, V[:, i] - 0.35 * i, lw=1.2, label=f"Achse {i + 1}: {freq[i]:.0f} Hz")
    axes[0].set_xlabel("Zeit im Abschnitt [ms]")
    axes[0].set_yticks([])
    axes[0].set_title("Die obersten Hauptachsen des Rauschens (H1), versetzt gezeichnet", fontsize=10)
    axes[0].legend(fontsize=8, loc="upper right")
    m = (f > 8) & (f < fs / 2 * 0.85)
    axes[1].loglog(f[m], P[m] * fs / 2, color="black", lw=1, label="Welch-Spektrum · fs/2")
    sel = pos & (freq > 8) & (freq < fs / 2 * 0.85)
    axes[1].loglog(freq[sel], w[sel], "o", ms=3, color="tab:red", label="Eigenwert bei der Frequenz seiner Achse")
    axes[1].set_xlabel("Frequenz [Hz]")
    axes[1].set_ylabel("Varianz je Achse [Strain²]")
    axes[1].set_title("Eigenwerte der Kovarianz = Leistungsspektrum", fontsize=10)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()


def whiten(x, fs, seconds=4):
    """Jede Fourier-Komponente durch √(Spektrum · fs/2) teilen: das Rauschen hat danach in jeder Achse Varianz 1."""
    f, P = psd(x, fs, seconds)
    X = np.fft.rfft(x * signal.windows.tukey(len(x), 0.1))
    fr = np.fft.rfftfreq(len(x), 1 / fs)
    return np.fft.irfft(X / np.sqrt(np.interp(fr, f, P) * fs / 2), n=len(x))


def bandpass(x, fs, lo=35, hi=350):
    b, a = signal.butter(4, [lo, hi], btype="band", fs=fs)
    return signal.filtfilt(b, a, x)


def plot_whitening(data, fs, t, lo=35, hi=350, length=128, window=0.2):
    """Oben der rohe Strain um das Ereignis, unten beide Detektoren nach Whitening und Bandpass; dazu der Weißtest."""
    white = {ifo: whiten(x, fs) for ifo, x in data.items()}
    quiet = (np.abs(t) > 2) & (t > t[0] + 2) & (t < t[-1] - 2)          # ohne Ereignis und Ränder
    segs = np.array([white["H1"][i:i + length] for i in range(0, len(t) - length, length) if quiet[i:i + length].all()])
    segs = segs - segs.mean(axis=1, keepdims=True)
    ev = np.linalg.eigvalsh(segs.T @ segs / len(segs))[1:] / white["H1"][quiet].var()   # der kleinste ist 0 (Mittelwert)
    g = length / len(segs)
    print(f"Weißtest (H1): Eigenwerte der Kovarianz nach dem Whitening {ev.min():.2f} bis {ev.max():.2f}, "
          f"Marchenko-Pastur für weißes Rauschen {(1 - np.sqrt(g)) ** 2:.2f} bis {(1 + np.sqrt(g)) ** 2:.2f} (γ = {g:.2f})")
    bp = {ifo: bandpass(w, fs, lo, hi) for ifo, w in white.items()}
    near = np.abs(t) < window
    lag = np.arange(-60, 61)
    cc = [np.corrcoef(bp["H1"][near], -np.roll(bp["L1"], k)[near])[0, 1] for k in lag]
    shift = lag[int(np.argmax(cc))]
    for ifo in bp:
        print(f"  {ifo}: größter Ausschlag {np.abs(bp[ifo][near]).max() / bp[ifo][quiet].std():.1f} σ des Rauschens")
    print(f"  L1 kommt {shift / fs * 1000:.1f} ms früher an, mit umgekehrtem Vorzeichen (Korrelation {max(cc):.2f})")
    fig, axes = plt.subplots(2, 1, figsize=(12, 6.5), sharex=True)
    axes[0].plot(t[near], data["H1"][near], color="grey", lw=0.8)
    axes[0].set_ylabel("Strain (roh)")
    axes[0].set_title("H1 roh: das tieffrequente Rauschen verdeckt alles", fontsize=10)
    axes[1].plot(t[near], bp["H1"][near], color="tab:red", lw=1, label="H1 (Hanford)")
    axes[1].plot(t[near], -np.roll(bp["L1"], shift)[near], color="tab:blue", lw=1, alpha=0.8,
                 label=f"L1 (Livingston), um {shift / fs * 1000:.1f} ms verschoben und umgedreht")
    axes[1].set_xlabel("Zeit relativ zu GPS 1126259462.4 [s]")
    axes[1].set_ylabel("nach Whitening [σ]")
    axes[1].set_title(f"Nach Whitening und Bandpass {lo} bis {hi} Hz: GW150914", fontsize=10)
    axes[1].legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    plt.show()


# ---- Der Chirp im Zeit-Frequenz-Bild

G, C, MSUN = 6.674e-11, 2.998e8, 1.989e30


def scalogram(w, fs, freqs, q=8):
    """Energie je Zeit und Frequenz: Bandpass mit einem Gauß der Breite f/q um jede Frequenz (Morlet-Wavelet).

    Ein Wellenpaket enthält dann etwa q Schwingungen, wie bei der Q-Transformation von LIGO.
    """
    X = np.fft.rfft(w)
    fr = np.fft.rfftfreq(len(w), 1 / fs)
    out = np.empty((len(freqs), len(w)))
    for i, f0 in enumerate(freqs):
        band = X * np.exp(-0.5 * ((fr - f0) / (f0 / q)) ** 2)
        out[i] = np.abs(np.fft.ifft(np.concatenate([band, np.zeros(len(w) - len(fr))]) * 2)) ** 2
    return out


def chirp_frequency(tau, mchirp):
    """Newtonsche Frequenz der Gravitationswelle τ Sekunden vor der Verschmelzung, Chirp-Masse in Sonnenmassen."""
    m = mchirp * MSUN * G / C ** 3                       # Chirp-Masse als Zeit [s]
    return (5 / (256 * tau)) ** 0.375 * m ** -0.625 / np.pi


def plot_chirp(data, fs, t, mchirp=31, fmin=20, fmax=512, before=0.35, after=0.1):
    """Zeit-Frequenz-Bild beider Detektoren nach dem Whitening, darüber die Newtonsche Chirp-Kurve.

    Energie normiert auf ihren Median im ruhigen Rauschen (1 = typisches Rauschen). Die Verschmelzung wird als Zeitpunkt
    der größten Energie genommen.
    """
    freqs = np.geomspace(fmin, fmax, 120)
    quiet = (np.abs(t) > 2) & (t > t[0] + 2) & (t < t[-1] - 2)
    show = (t > -before) & (t < after)
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8), sharey=True)
    for ax, (ifo, x) in zip(axes, data.items()):
        S = scalogram(whiten(x, fs), fs, freqs)
        S /= np.median(S[:, quiet], axis=1, keepdims=True)
        i, j = np.unravel_index(np.argmax(S[:, show]), S[:, show].shape)
        tc = t[show][j]
        tau = np.array([0.1, 0.05])
        ridge = [freqs[np.argmax(S[:, np.argmin(np.abs(t - (tc - d)))])] for d in tau]
        print(f"{ifo}: größte Energie {S[:, show].max():.0f}-mal das Rauschen bei {freqs[i]:.0f} Hz, t = {tc * 1000:+.1f} ms; "
              f"0.1 s und 0.05 s davor bei {ridge[0]:.0f} und {ridge[1]:.0f} Hz "
              f"(Newton mit {mchirp} Sonnenmassen: {chirp_frequency(0.1, mchirp):.0f} und {chirp_frequency(0.05, mchirp):.0f} Hz)")
        im = ax.pcolormesh(t[show], freqs, S[:, show], shading="auto", cmap="viridis", vmax=25)
        tt = np.linspace(tc - before + 0.01, tc - 0.004, 200)
        fc = chirp_frequency(tc - tt, mchirp)
        ok = (fc > fmin) & (fc < fmax)
        ax.plot(tt[ok], fc[ok], "w--", lw=1.2, label=f"Newton, Chirp-Masse {mchirp} M☉")
        ax.set_yscale("log")
        ax.set_yticks([20, 50, 100, 200, 500], ["20", "50", "100", "200", "500"])
        ax.set_xlabel("Zeit relativ zu GPS 1126259462.4 [s]")
        ax.set_title(f"{ifo}: Energie nach dem Whitening", fontsize=10)
        ax.legend(fontsize=8, loc="upper left")
    axes[0].set_ylabel("Frequenz [Hz]")
    fig.colorbar(im, ax=axes, fraction=0.03, label="Energie / Median im Rauschen")
    plt.show()
