"""Quantum Imaging für limits_of_knowledge.ipynb: Rayleighs Fluch, SPADE und der Nachweis schwacher Begleiter.

Zwei inkohärente Punktquellen hinter einer Optik mit gaußscher Punktbildfunktion der Breite σ (alle Längen in σ). Eine
Kamera zählt Photonen nach Ort, SPADE (Spatial-Mode Demultiplexing) sortiert sie nach Hermite-Gauß-Moden. Verglichen
werden die Fisher-Information pro Photon mit der Quanten-Fisher-Information 1/(4σ²) (Tsang, Nair, Lu 2016), Schätzungen
des Abstands per Monte Carlo und die Fehlerexponenten beim Nachweis eines schwachen Begleiters (Huang, Lupo 2021).
Dazu die Abstände bekannter Exoplaneten aus dem NASA Exoplanet Archive (TAP, mit Cache; Ausweich: exoplanet.eu).
"""
import io
import time
from math import factorial
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt

X = np.linspace(-12, 12, 20001)                 # Ort auf dem Detektor [σ]
DX = X[1] - X[0]
QFI = 0.25                                      # Quanten-Fisher-Information pro Photon für den Abstand [1/σ²]


def _n(x):
    """Ganze Zahl mit Leerzeichen als Tausendertrenner (10 000); nur die Zahl, nie den ganzen Satz ersetzen."""
    return f"{x:,.0f}".replace(",", " ")


def gauss(u):
    return np.exp(-u ** 2 / 2) / np.sqrt(2 * np.pi)


def hg_probs(x0, q_max=40):
    """Wahrscheinlichkeit, dass ein Photon einer Quelle bei x0 in der Hermite-Gauß-Mode q landet: e^(−Q) Q^q / q!, Q = x0²/4."""
    Q = x0 ** 2 / 4
    q = np.arange(q_max)
    return np.exp(-Q) * Q ** q / np.array([factorial(k) for k in q], dtype=float)


def fisher_camera(theta):
    """Fisher-Information pro Photon einer idealen Kamera, zwei gleich helle Quellen bei ±θ/2."""
    p = 0.5 * (gauss(X - theta / 2) + gauss(X + theta / 2))
    dp = 0.25 * ((X - theta / 2) * gauss(X - theta / 2) - (X + theta / 2) * gauss(X + theta / 2))
    return float(np.sum(dp ** 2 / np.maximum(p, 1e-300)) * DX)


def fisher_spade(theta, crosstalk=0.0, h=1e-5):
    """Fisher-Information pro Photon der Modenzählung; crosstalk = Anteil der Photonen aus Mode 0, der in Mode 1 landet."""
    def probs(t):
        P = hg_probs(t / 2)
        return np.r_[P[0] * (1 - crosstalk), P[1] + P[0] * crosstalk, P[2:]]
    lo = max(theta - h, 0)
    p, dp = probs(theta), (probs(theta + h) - probs(lo)) / (theta + h - lo)
    return float(np.sum(dp[p > 0] ** 2 / p[p > 0]))


def plot_rayleigh(thetas=(0.25, 1.0, 3.0)):
    """Links: was die Kamera sieht; rechts: Fisher-Information pro Photon gegen den Abstand, Kamera gegen Quantengrenze."""
    th = np.logspace(-2, 0.8, 60)
    fc = np.array([fisher_camera(t) for t in th])
    for t in [0.1, 0.5, 1.0]:
        print(f"θ = {t:.1f}σ: Fisher-Information pro Photon, Kamera {fisher_camera(t):.4f} (Näherung θ²/8 = {t ** 2 / 8:.4f}), "
              f"Quantengrenze {QFI:.2f} [1/σ²]; für 10 % Genauigkeit braucht die Kamera "
              f"{_n(1 / (fisher_camera(t) * (0.1 * t) ** 2))} Photonen, die Quantengrenze {_n(1 / (QFI * (0.1 * t) ** 2))}")
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.6))
    for t, c in zip(thetas, ["tab:red", "tab:orange", "tab:green"]):
        axes[0].plot(X, 0.5 * (gauss(X - t / 2) + gauss(X + t / 2)), color=c, label=f"Abstand θ = {t}σ")
        axes[0].plot([-t / 2, t / 2], [0.42, 0.42], "|", color=c, ms=12, mew=2)
    axes[0].set_xlim(-5, 5)
    axes[0].set_xlabel("Ort auf dem Detektor [σ]")
    axes[0].set_ylabel("Helligkeit (Summe beider Quellen)")
    axes[0].set_title("Was die Kamera sieht: unter etwa 1σ verschmelzen zwei Sterne", fontsize=10)
    axes[0].legend(fontsize=8)
    axes[1].loglog(th, fc, color="tab:blue", lw=2, label="Kamera (Photonen nach Ort)")
    axes[1].loglog(th, th ** 2 / 8, color="tab:blue", ls=":", lw=1, label="Näherung θ²/8: geht gegen null")
    axes[1].axhline(QFI, color="tab:red", lw=2, label="Quantengrenze 1/4 (bei jedem Abstand)")
    axes[1].set_xlabel("Abstand der beiden Quellen θ [σ]")
    axes[1].set_ylabel("Fisher-Information pro Photon [1/σ²]")
    axes[1].set_title("Rayleighs Fluch: die Kamera verliert die Information", fontsize=10)
    axes[1].legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    plt.show()


def estimate(theta, photons, trials=300, seed=0, bins=400):
    """Abstand aus `photons` Photonen schätzen, Kamera (Maximum-Likelihood auf dem Histogramm) und SPADE (Mittel der Moden)."""
    rng = np.random.default_rng(seed)
    grid = np.linspace(0, 4, 801)
    edges = np.linspace(-8, 8, bins + 1)
    mid = (edges[1:] + edges[:-1]) / 2
    pk = np.array([0.5 * (gauss(mid - g / 2) + gauss(mid + g / 2)) for g in grid]) * (edges[1] - edges[0])
    logpk = np.log(np.maximum(pk, 1e-300))
    cam, spa = [], []
    for _ in range(trials):
        sign = rng.choice([-1, 1], photons)
        pos = rng.normal(sign * theta / 2, 1.0)
        counts, _ = np.histogram(pos, edges)
        cam.append(grid[np.argmax(logpk @ counts)])
        q = rng.poisson(theta ** 2 / 16, photons)                       # Modenzahl jedes Photons, Q = (θ/2)²/4
        spa.append(4 * np.sqrt(q.mean()))
    return np.array(cam), np.array(spa)


def plot_estimates(theta=0.4, photons=10000, trials=300):
    """Histogramm der Schätzwerte beider Verfahren mit den Cramér-Rao-Schranken."""
    cam, spa = estimate(theta, photons, trials)
    crb_c = 1 / np.sqrt(photons * fisher_camera(theta))
    crb_s = 1 / np.sqrt(photons * QFI)
    rm = lambda e: np.sqrt(np.mean((e - theta) ** 2))
    print(f"Wahrer Abstand θ = {theta}σ, {_n(photons)} Photonen, {trials} Wiederholungen")
    print(f"  Kamera: mittlerer Fehler {rm(cam):.3f}σ, Cramér-Rao-Schranke {crb_c:.3f}σ; "
          f"{np.mean(cam == 0):.0%} der Schätzungen landen bei θ̂ = 0")
    print(f"  SPADE:  mittlerer Fehler {rm(spa):.3f}σ, Quanten-Cramér-Rao-Schranke {crb_s:.3f}σ "
          f"({rm(cam) / rm(spa):.0f}-mal genauer als die Kamera)")
    fig, ax = plt.subplots(figsize=(10, 4.4))
    bins = np.linspace(0, max(1.0, 2.5 * theta), 60)
    ax.hist(cam, bins=bins, alpha=0.6, color="tab:blue", label=f"Kamera (Fehler {rm(cam):.3f}σ)")
    ax.hist(spa, bins=bins, alpha=0.6, color="tab:red", label=f"SPADE (Fehler {rm(spa):.3f}σ)")
    ax.axvline(theta, color="black", lw=1.5, label=f"wahrer Abstand {theta}σ")
    ax.set_xlabel("geschätzter Abstand θ̂ [σ]")
    ax.set_ylabel("Anzahl der Wiederholungen")
    ax.set_title(f"Abstand zweier Quellen aus je {_n(photons)} Photonen", fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()
    return cam, spa


def exponent_camera(eps, theta):
    """Fehlerexponent pro Photon der Kamera für 'Stern allein' gegen 'Stern + Begleiter mit Anteil eps bei θ': D(p0 ‖ p1)."""
    p0 = gauss(X)
    return float(-np.sum(p0 * np.log1p(eps * np.expm1((2 * X * theta - theta ** 2) / 2))) * DX)


def exponent_spade(eps, theta, crosstalk=0.0):
    """Fehlerexponent pro Photon für SPADE, auf den Lichtschwerpunkt ausgerichtet; Ergebnis 'Mode 0' gegen 'andere Mode'.

    crosstalk: Anteil der Photonen aus Mode 0, die der Sortierer in eine andere Mode schickt (Fehler des Geräts).
    """
    p1_0 = (1 - eps) * hg_probs(-eps * theta)[0] + eps * hg_probs((1 - eps) * theta)[0]
    a0, a1 = 1 - crosstalk, (1 - crosstalk) * p1_0
    return float(a0 * np.log(a0 / a1) + ((1 - a0) * np.log((1 - a0) / (1 - a1)) if crosstalk > 0 else 0.0))


def plot_detection(eps_list=(1e-2, 1e-4), crosstalk=1e-3, theta_show=0.3):
    """Fehlerexponenten gegen den Abstand; dazu die Photonen für 99.9 % Sicherheit bei theta_show."""
    th = np.logspace(-2, 0.7, 60)
    print(f"Photonen für 99.9 % Nachweissicherheit (ln 1000 / Exponent) bei θ = {theta_show}σ:")
    for eps in eps_list:
        dc, ds, dx = exponent_camera(eps, theta_show), exponent_spade(eps, theta_show), exponent_spade(eps, theta_show, crosstalk)
        print(f"  Helligkeit ε = {eps:g}: Kamera {np.log(1e3) / dc:.1e}, SPADE {np.log(1e3) / ds:.1e}, "
              f"SPADE mit {crosstalk:g} Übersprechen {np.log(1e3) / dx:.1e}; Gewinn von SPADE {ds / dc:.0f}-fach")
    fig, ax = plt.subplots(figsize=(10, 5))
    for eps, c in zip(eps_list, ["tab:blue", "tab:red"]):
        ax.loglog(th, [exponent_camera(eps, t) for t in th], c=c, ls="--", label=f"Kamera, ε = {eps:g}")
        ax.loglog(th, [exponent_spade(eps, t) for t in th], c=c, lw=2, label=f"SPADE, ε = {eps:g}")
        ax.loglog(th, [exponent_spade(eps, t, crosstalk) for t in th], c=c, lw=1, ls="-.",
                  label=f"SPADE mit Übersprechen {crosstalk:g}, ε = {eps:g}")
    ax.set_xlabel("Abstand Stern–Begleiter θ [σ]")
    ax.set_ylabel("Fehlerexponent pro Photon")
    ax.set_ylim(1e-14, 1e-1)
    ax.set_title("Einen schwachen Begleiter nachweisen: je größer der Exponent, desto weniger Photonen", fontsize=10)
    ax.legend(fontsize=7, loc="lower right")
    fig.tight_layout()
    plt.show()


def planets(cache):
    """Große Halbachse und Entfernung aller bekannten Planeten (NASA Exoplanet Archive, sonst exoplanet.eu), mit Cache."""
    path = Path(cache) / "planets.csv"
    if path.exists():
        return pd.read_csv(path)
    head = {"User-Agent": "Mozilla/5.0 (science notebook)"}           # ohne Kennung blockt die Firewall des Archivs
    sources = [("NASA Exoplanet Archive", "https://exoplanetarchive.ipac.caltech.edu/TAP/sync",
                {"query": "select pl_name, pl_orbsmax, sy_dist, disc_method from pscomppars", "format": "csv"},
                {"pl_name": "name", "pl_orbsmax": "a_au", "sy_dist": "d_pc", "disc_method": "method"}),
               ("exoplanet.eu", "https://exoplanet.eu/catalog/csv/", None,
                {"name": "name", "semi_major_axis": "a_au", "star_distance": "d_pc", "detection_type": "method"})]
    for name, url, params, cols in sources:
        for i in range(2):
            try:
                r = requests.get(url, params=params, headers=head, timeout=180)
                if r.ok and not r.text.lstrip().startswith("<"):
                    df = pd.read_csv(io.StringIO(r.text))[list(cols)].rename(columns=cols)
                    df["source"] = name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    df.to_csv(path, index=False)
                    return df
            except (requests.RequestException, KeyError, pd.errors.ParserError):
                pass
            time.sleep(3)
    raise OSError("Kein Planetenkatalog erreichbar")


def plot_planets(df, lam_um=1.6, telescopes=(("8 m (VLT)", 8.0), ("39 m (ELT)", 39.0))):
    """Größter Winkelabstand a/d jedes Planeten in Einheiten von λ/D, für zwei Teleskope."""
    df = df.dropna(subset=["a_au", "d_pc"])
    sep_mas = df["a_au"] / df["d_pc"] * 1000                            # 1 AU in 1 pc = 1 Bogensekunde
    print(f"{_n(len(df))} Planeten mit Bahn und Entfernung ({df['source'].iloc[0]})")
    fig, ax = plt.subplots(figsize=(10, 4.6))
    for (name, D), c in zip(telescopes, ["tab:blue", "tab:purple"]):
        lod = lam_um * 1e-6 / D * 206265e3                              # λ/D in Millibogensekunden
        r = sep_mas / lod
        print(f"  {name:11s} λ/D = {lod:4.1f} mas bei {lam_um} µm: {(r < 1).mean():.0%} der Planeten näher als λ/D, "
              f"{(r < 3).mean():.0%} näher als 3 λ/D")
        ax.hist(r, bins=np.logspace(-4, 4, 70), histtype="step", lw=1.5, color=c, label=f"{name}: λ/D = {lod:.1f} mas")
    ax.axvspan(1e-4, 1, color="red", alpha=0.08, label="unter der Beugungsgrenze λ/D")
    ax.axvline(3, color="grey", ls=":", label="typischer innerer Arbeitswinkel eines Koronographen (≈ 3 λ/D)")
    ax.set_xscale("log")
    ax.set_xlabel(f"größter Abstand Planet–Stern a/d [λ/D bei {lam_um} µm]")
    ax.set_ylabel("Anzahl bekannter Planeten")
    ax.set_title("Fast alle bekannten Exoplaneten liegen unter der Beugungsgrenze", fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()
    examples = {"Proxima Cen b": "Proxima Cen b", "eps Eri b": "eps Eri b", "51 Peg b": "51 Peg b"}
    for label, key in examples.items():
        hit = df[df["name"].astype(str).str.strip() == key]
        if len(hit):
            h = hit.iloc[0]
            print(f"  {label}: a = {h['a_au']:.3g} AU, d = {h['d_pc']:.3g} pc, größter Abstand {h['a_au'] / h['d_pc'] * 1000:.1f} mas")
