"""Standardsirenen: H0 aus GW170817 und seiner Galaxie NGC 4993, Neigung der Bahn, Jet als Winkelmesser und wie viele Sirenen man braucht.

Für cosmology.ipynb aus cosmology_sirens.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, distance_inclination, host_galaxy, distance_prior, h0_siren, h0_inclination, jet, peculiar_velocity, how_many, literature.
Downloads und Cache: data/cosmology/ (`cosmodata.py`).
"""
import cosmodata                                      # zuerst: Cache-Ordner für astropy
import os
import urllib.request
from pathlib import Path
import h5py
import numpy as np
import matplotlib.pyplot as plt


def load():
    """36. Daten (Zellen 4, 6 von cosmology_sirens.ipynb)."""
    global ABBOTT17, ASTRODATA, COSI, D, GWTC3, GW_DIR, H, HOTOKEZAKA19, JET, OTHERS, PE, PE_URL
    global PLANCK, PRIOR, SH0ES, SIG_VP, SIG_VR, V_P, V_R, download, f, fmt, hi, k
    global lo, med, posterior, summary
    ASTRODATA = cosmodata.DATA


    PE_URL = "https://dcc.ligo.org/public/0157/P1800370/005/GW170817_GWTC-1.hdf5"
    GW_DIR = ASTRODATA / "gwosc"
    V_R, SIG_VR = 3327.0, 72.0                                # Gruppe um NGC 4993, CMB-System [km/s]
    V_P, SIG_VP = 310.0, 150.0                                # Eigenbewegung (6dF) mit vorsichtigem Fehler
    JET = (0.25, 0.45, 41.0)                                  # 0.25 < θ_obs · d/41 Mpc < 0.45 rad
    PLANCK, SH0ES = (67.36, 0.54), (73.04, 1.04)
    ABBOTT17 = (70.0, 12.0, 8.0)                              # MAP, +, − (68.3 %)
    HOTOKEZAKA19 = (68.9, 4.6, 4.5)                           # Median, +, − (hydrodynamisches Jet-Modell)
    GWTC3 = {"GWTC-3: Massenverteilung + GW170817": (68.0, 12.0, 8.0), "GWTC-3: Galaxienkatalog": (68.0, 8.0, 6.0)}
    OTHERS = {"Inverse Leiter: DESI + BBN": (68.53, 0.60, 0.60), "Kosmische Chronometer (ΛCDM)": (66.99, 5.5, 5.5)}
    H = np.linspace(20, 200, 3601)                            # Gitter für H₀ [km/s/Mpc]


    def download(url, path, check, timeout=300):
        path = Path(path)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            with urllib.request.urlopen(url, timeout=timeout) as r:
                data = r.read()
            if not check(data):
                raise OSError(f"{path.name}: unerwarteter Inhalt")
            path.write_bytes(data)
        return path


    with h5py.File(download(PE_URL, GW_DIR / "GW170817_GWTC-1.hdf5", lambda d: d[:8] == b"\x89HDF\r\n\x1a\n"), "r") as f:
        PE = {k: f[f"IMRPhenomPv2NRT_{k}Spin_posterior"][()] for k in ("low", "high")}
        PRIOR = f["IMRPhenomPv2NRT_lowSpin_prior"][()]
    D = {k: v["luminosity_distance_Mpc"] for k, v in PE.items()}
    COSI = {k: v["costheta_jn"] for k, v in PE.items()}

    for k in ("low", "high"):
        lo, med, hi = np.percentile(D[k], [5, 50, 95])
        print(f"{'kleine' if k == 'low' else 'große':6s} Spins: {len(D[k])} Stichproben, d = {med:.1f} +{hi - med:.1f}/−{med - lo:.1f} Mpc (90 %), "
              f"cos θ_JN = {np.median(COSI[k]):.2f}, Himmel fest bei RA = {np.degrees(np.median(PE[k]['right_ascension'])):.2f}°, "
              f"Dec = {np.degrees(np.median(PE[k]['declination'])):.2f}°")
    print(f"Prior: {len(PRIOR)} Stichproben, d von {PRIOR['luminosity_distance_Mpc'].min():.1f} bis {PRIOR['luminosity_distance_Mpc'].max():.1f} Mpc")

    def posterior(d, w=None, v_r=V_R, v_p=V_P, sig_vp=SIG_VP, prior="log"):
        # p(H₀) ∝ p(H₀) Σ_i w_i N(v_r − H₀ d_i; ⟨v_p⟩, √(σ_vr² + σ_vp²)); die Stichproben tragen schon den Prior p(d) ∝ d²
        w = np.ones_like(d) if w is None else w
        s = np.hypot(SIG_VR, sig_vp)
        like = np.concatenate([np.exp(-0.5 * ((v_r - np.outer(Hb, d) - v_p) / s) ** 2) @ w for Hb in np.array_split(H, 40)])   # in Blöcken
        p = like / H if prior == "log" else like
        return p / np.trapz(p, H)


    def summary(p):
        dh = H[1] - H[0]
        order = np.argsort(p)[::-1]
        inside = order[:np.searchsorted(np.cumsum(p[order]) * dh, 0.683) + 1]
        c = np.cumsum(p) * dh
        med, lo, hi = np.interp([0.5, 0.16, 0.84], c, H)
        return dict(map=H[np.argmax(p)], hpd=(H[inside].min(), H[inside].max()), med=med, q=(lo, hi))


    def fmt(s):
        return (f"MAP {s['map']:.1f} +{s['hpd'][1] - s['map']:.1f}/−{s['map'] - s['hpd'][0]:.1f}; "
                f"Median {s['med']:.1f} +{s['q'][1] - s['med']:.1f}/−{s['med'] - s['q'][0]:.1f}")


    print(f"Hubble-Geschwindigkeit v_H = v_r − ⟨v_p⟩ = {V_R - V_P:.0f} ± {np.hypot(SIG_VR, SIG_VP):.0f} km/s")


def distance_inclination():
    """37. Entfernung und Neigung aus der Welle (Zellen 8 von cosmology_sirens.ipynb)."""
    global ax, ax2, bins, col, fig, k, lab, p16, p5, p50, p84, p95
    global r, sc
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.6))
    bins = np.linspace(0, 80, 81)
    ax.hist(PRIOR["luminosity_distance_Mpc"], bins=bins, density=True, color="0.8", label="Prior (∝ d²)")
    for k, col, lab in [("low", "C0", "kleine Spins"), ("high", "C1", "große Spins")]:
        ax.hist(D[k], bins=bins, density=True, histtype="step", lw=2, color=col, label=f"Posterior, {lab}")
    ax.set_xlabel("Leuchtkraftentfernung d [Mpc]")
    ax.set_ylabel("Wahrscheinlichkeitsdichte [1/Mpc]")
    ax.set_title("Wie weit ist GW170817 entfernt?", fontsize=10)
    ax.legend(fontsize=9)
    sc = ax2.scatter(COSI["low"], D["low"], s=3, c=np.abs(COSI["low"]), cmap="viridis", alpha=0.6)
    ax2.set_xlabel(r"$\cos\theta_{JN}$")
    ax2.set_ylabel("Leuchtkraftentfernung d [Mpc]")
    ax2.set_title("Je schräger die Bahn, desto näher (kleine Spins)", fontsize=10)
    plt.colorbar(sc, ax=ax2, label=r"$|\cos\theta_{JN}|$")
    plt.tight_layout()
    plt.show()

    for k in ("low", "high"):
        p5, p16, p50, p84, p95 = np.percentile(D[k], [5, 16, 50, 84, 95])
        r = np.corrcoef(np.abs(COSI[k]), D[k])[0, 1]
        print(f"{'kleine' if k == 'low' else 'große':6s} Spins: d = {p50:.1f} Mpc, 68 %: {p16:.1f} bis {p84:.1f}, 90 %: {p5:.1f} bis {p95:.1f}; "
              f"Korrelation von d und |cos θ_JN|: {r:+.2f}; Anteil mit |cos θ_JN| > 0.9: {np.mean(np.abs(COSI[k]) > 0.9):.2f}")


def host_galaxy():
    """38. Die Galaxie und ihre Geschwindigkeit (Zellen 11 von cosmology_sirens.ipynb)."""
    global H0, ax, col, dd, fig, lab, p16, p50, p84, v_h
    p16, p50, p84 = np.percentile(D["low"], [16, 50, 84])
    v_h = V_R - V_P
    dd = np.linspace(0, 100, 2)
    fig, ax = plt.subplots(figsize=(11, 6.5))
    for H0, col, lab in [(PLANCK[0], "C3", "Planck, H₀ = 67.36"), (SH0ES[0], "C2", "SH0ES, H₀ = 73.04")]:
        ax.plot(dd, H0 * dd, color=col, lw=1.4, label=lab)
    ax.errorbar(p50, V_R, xerr=[[p50 - p16], [p84 - p50]], yerr=SIG_VR, fmt="s", color="0.5", ms=8, capsize=4, label="GW170817, gemessene v_r")
    ax.errorbar(p50, v_h, xerr=[[p50 - p16], [p84 - p50]], yerr=np.hypot(SIG_VR, SIG_VP), fmt="o", color="C0", ms=9, capsize=4,
                label="GW170817, Hubble-Geschwindigkeit v_H")
    ax.set_xlim(0, 80)
    ax.set_ylim(0, 6000)
    ax.set_xlabel("Entfernung aus der Gravitationswelle [Mpc]")
    ax.set_ylabel("Geschwindigkeit im Ruhesystem der Hintergrundstrahlung [km/s]")
    ax.set_title("GW170817 im Hubble-Diagramm", fontsize=10)
    ax.legend(fontsize=9)
    plt.show()

    print(f"v_H = {v_h:.0f} ± {np.hypot(SIG_VR, SIG_VP):.0f} km/s (Eigenbewegung {100 * V_P / V_R:.0f} % von v_r)")
    print(f"grob H₀ = v_H/d: {v_h / p50:.1f} beim Median d = {p50:.1f} Mpc, {v_h / p84:.1f} bis {v_h / p16:.1f} für das 68-%-Intervall der Entfernung")
    print(f"Planck verlangt d = {v_h / PLANCK[0]:.1f} Mpc, SH0ES d = {v_h / SH0ES[0]:.1f} Mpc")


def distance_prior():
    """39. Vom Prior der Entfernung zum Prior auf H₀ (Zellen 14 von cosmology_sirens.ipynb)."""
    global POST, ax, c, col, fig, lab, naive, p
    naive = np.histogram(v_h / D["low"], bins=H[::20], density=True)
    POST = {"Standard (Prior ∝ 1/H₀)": posterior(D["low"]), "flacher Prior": posterior(D["low"], prior="flat")}
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.stairs(naive[0], naive[1], color="0.5", lw=1.5, label="naiv: v_H/d_i, ohne Geschwindigkeitsfehler")
    for (lab, p), col in zip(POST.items(), ["C0", "C1"]):
        ax.plot(H, p, color=col, lw=1.8, label=lab)
    ax.set_xlim(40, 160)
    ax.set_xlabel("H₀ [km/s/Mpc]")
    ax.set_ylabel("Posterior-Dichte")
    ax.set_title("Was der Prior aus derselben Messung macht (kleine Spins)", fontsize=10)
    ax.legend(fontsize=9)
    plt.show()

    c = naive[1][:-1] + np.diff(naive[1]) / 2
    print(f"naiv: Maximum bei {c[np.argmax(naive[0])]:.1f}, Median {np.median(v_h / D['low']):.1f}")
    for lab, p in POST.items():
        print(f"{lab:24s}: {fmt(summary(p))}")


def h0_siren():
    """40. H₀ aus GW170817 (Zellen 17 von cosmology_sirens.ipynb)."""
    global P4, S4, ax, col, e, fig, hi, k, lab, lo, m, pr
    global v
    P4 = {k: posterior(D[k]) for k in ("low", "high")}
    S4 = {k: summary(p) for k, p in P4.items()}
    fig, ax = plt.subplots(figsize=(11, 6))
    for k, col, lab in [("low", "C0", "kleine Spins"), ("high", "C1", "große Spins")]:
        ax.plot(H, P4[k], color=col, lw=1.8, label=f"GW170817, {lab}")
        lo, hi = S4[k]["hpd"]
        m = (H >= lo) & (H <= hi)
        ax.fill_between(H[m], 0, P4[k][m], color=col, alpha=0.2)
    for (v, e), col, lab in [(PLANCK, "C3", "Planck"), (SH0ES, "C2", "SH0ES")]:
        ax.axvspan(v - e, v + e, color=col, alpha=0.3, label=lab)
    ax.set_xlim(40, 140)
    ax.set_xlabel("H₀ [km/s/Mpc]")
    ax.set_ylabel("Posterior-Dichte")
    ax.set_title("Die Hubble-Konstante aus einer Gravitationswelle (68.3 % schattiert)", fontsize=10)
    ax.legend(fontsize=9)
    plt.show()

    for k in ("low", "high"):
        pr = np.interp(SH0ES[0], H, P4[k]) / np.interp(PLANCK[0], H, P4[k])
        print(f"{'kleine' if k == 'low' else 'große':6s} Spins: {fmt(S4[k])}; p(73.04)/p(67.36) = {pr:.2f}")
    print(f"Abbott et al. 2017: MAP {ABBOTT17[0]} +{ABBOTT17[1]}/−{ABBOTT17[2]}")


def h0_inclination():
    """41. H₀ und die Neigung der Bahn (Zellen 20 von cosmology_sirens.ipynb)."""
    global ANG, G, W, ax, ax2, c2, cc, ci, col, cum, cw, e
    global e_, fig, h2, hi, hist, lab, lev, lo, order, s, v, val
    global w_
    ci = COSI["low"]
    s = np.hypot(SIG_VR, SIG_VP)
    h2 = np.linspace(40, 140, 101)
    c2 = np.linspace(-1, -0.2, 41)
    W = np.exp(-0.5 * ((V_R - V_P - np.outer(h2, D["low"])) / s) ** 2) / h2[:, None]   # (H₀, Stichprobe)
    G = np.array([[W[i, (ci >= c2[j]) & (ci < c2[j + 1])].sum() for j in range(len(c2) - 1)] for i in range(len(h2))])
    G /= G.sum()
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.8))
    v = np.sort(G.ravel())[::-1]
    cum = np.cumsum(v)
    lev = [v[np.searchsorted(cum, f)] for f in (0.954, 0.683)]
    cc = (c2[1:] + c2[:-1]) / 2
    ax.contourf(h2, cc, G.T, levels=lev + [G.max()], colors=["lightsteelblue", "C0"], alpha=0.8)
    for (val, e), col, lab in [(PLANCK, "C3", "Planck"), (SH0ES, "C2", "SH0ES")]:
        ax.axvspan(val - e, val + e, color=col, alpha=0.35, label=lab)
    ax.plot([], [], color="C0", lw=8, label="68.3 %")
    ax.plot([], [], color="lightsteelblue", lw=8, label="95.4 %")
    ax.set_xlabel("H₀ [km/s/Mpc]")
    ax.set_ylabel(r"$\cos\iota$")
    ax.set_title("H₀ und Neigung gemeinsam (kleine Spins)", fontsize=10)
    ax.legend(fontsize=9, loc="upper right")
    ANG = {}
    for lab, w_, col in [("H₀ frei", W.sum(axis=0), "C0"),
                         ("H₀ = 67.36 (Planck)", np.exp(-0.5 * ((V_R - V_P - PLANCK[0] * D["low"]) / s) ** 2), "C3"),
                         ("H₀ = 73.04 (SH0ES)", np.exp(-0.5 * ((V_R - V_P - SH0ES[0] * D["low"]) / s) ** 2), "C2")]:
        hist, e_ = np.histogram(ci, bins=np.linspace(-1, -0.2, 33), weights=w_, density=True)
        ax2.stairs(hist, e_, color=col, lw=1.8, label=lab)
        order = np.argsort(ci)
        cw = np.cumsum(w_[order]) / w_.sum()
        lo, hi = np.interp([0.16, 0.84], cw, ci[order])
        ANG[lab] = (lo, hi)
    ax2.set_xlabel(r"$\cos\iota$")
    ax2.set_ylabel("Posterior-Dichte")
    ax2.set_title("Welche Neigung zu welchem H₀ gehört", fontsize=10)
    ax2.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    for lab, (lo, hi) in ANG.items():
        print(f"{lab:20s}: cos ι von {lo:.3f} bis {hi:.3f} (68 %), also ι von {np.degrees(np.arccos(hi)):.0f}° bis {np.degrees(np.arccos(lo)):.0f}°")


def jet():
    """42. Der Jet als Winkelmesser (Zellen 23 von cosmology_sirens.ipynb)."""
    global JET_RESULTS, ax, ax2, col, dd, e, fig, k, keep, lab, lim, pj
    global sj, theta, v, x
    JET_RESULTS = {}
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.8))
    for k, col in [("low", "C0"), ("high", "C1")]:
        theta = np.pi - np.arccos(COSI[k])
        x = theta * D[k] / JET[2]
        keep = (x > JET[0]) & (x < JET[1])
        pj = posterior(D[k], w=keep.astype(float))
        JET_RESULTS[k] = (keep, pj, summary(pj), theta)
        if k == "low":
            ax.scatter(D[k][~keep], np.degrees(theta[~keep]), s=3, color="0.7", label="ausgeschlossen")
            ax.scatter(D[k][keep], np.degrees(theta[keep]), s=3, color="C0", label="mit dem Jet verträglich")
    dd = np.linspace(10, 60, 100)
    for lim in JET[:2]:
        ax.plot(dd, np.degrees(lim * JET[2] / dd), color="k", ls="--", lw=1)
    ax.set_ylim(0, 90)
    ax.set_xlabel("Leuchtkraftentfernung d [Mpc]")
    ax.set_ylabel(r"Beobachtungswinkel $\theta_\mathrm{obs} = 180° - \theta_{JN}$ [°]")
    ax.set_title("Das erlaubte Band aus der Bewegung des Jets (kleine Spins)", fontsize=10)
    ax.legend(fontsize=9, markerscale=4)
    ax2.plot(H, P4["low"], color="0.5", lw=1.5, label="nur Gravitationswelle (Schritt 40)")
    for k, col, lab in [("low", "C0", "kleine Spins"), ("high", "C1", "große Spins")]:
        ax2.plot(H, JET_RESULTS[k][1], color=col, lw=1.8, label=f"mit dem Jet, {lab}")
    ax2.errorbar(HOTOKEZAKA19[0], 0.01, xerr=[[HOTOKEZAKA19[2]], [HOTOKEZAKA19[1]]], fmt="s", color="k", capsize=4, label="Hotokezaka et al. 2019")
    for (v, e), col, lab in [(PLANCK, "C3", "Planck"), (SH0ES, "C2", "SH0ES")]:
        ax2.axvspan(v - e, v + e, color=col, alpha=0.3, label=lab)
    ax2.set_xlim(40, 120)
    ax2.set_xlabel("H₀ [km/s/Mpc]")
    ax2.set_ylabel("Posterior-Dichte")
    ax2.set_title("H₀ mit dem Beobachtungswinkel des Jets", fontsize=10)
    ax2.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    for k in ("low", "high"):
        keep, pj, sj, theta = JET_RESULTS[k]
        print(f"{'kleine' if k == 'low' else 'große':6s} Spins: {keep.sum()} von {len(keep)} Stichproben bleiben; d = {np.median(D[k][keep]):.1f} Mpc "
              f"(68 %: {np.percentile(D[k][keep], 16):.1f} bis {np.percentile(D[k][keep], 84):.1f}), θ_obs = {np.degrees(np.median(theta[keep])):.1f}°; "
              f"H₀: {fmt(sj)}")
    print(f"Hotokezaka et al. 2019: Median {HOTOKEZAKA19[0]} +{HOTOKEZAKA19[1]}/−{HOTOKEZAKA19[2]}")


def peculiar_velocity():
    """43. Wie viel die Eigenbewegung ausmacht (Zellen 26 von cosmology_sirens.ipynb)."""
    global CASES, VP, ax, col, fig, keep, lab, p, s_, sp, vp
    keep = JET_RESULTS["low"][0].astype(float)
    CASES = {"Standard: 310 ± 150": (310, 150), "nur 6dF-Fehler: 310 ± 69": (310, 69), "2M++: 280 ± 150": (280, 150),
             "ohne Korrektur: 0 ± 150": (0, 150), "doppelte Unsicherheit: 310 ± 300": (310, 300)}
    fig, ax = plt.subplots(figsize=(11, 6))
    VP = {}
    for (lab, (vp, sp)), col in zip(CASES.items(), ["C0", "C1", "C2", "C3", "C4"]):
        p = posterior(D["low"], w=keep, v_p=vp, sig_vp=sp)
        VP[lab] = summary(p)
        ax.plot(H, p, color=col, lw=1.8, label=lab)
    ax.set_xlim(50, 100)
    ax.set_xlabel("H₀ [km/s/Mpc]")
    ax.set_ylabel("Posterior-Dichte")
    ax.set_title("H₀ mit dem Jet für verschiedene Eigenbewegungen von NGC 4993", fontsize=10)
    ax.legend(fontsize=9, title="⟨v_p⟩ ± σ [km/s]")
    plt.show()

    for lab, s_ in VP.items():
        print(f"{lab:34s}: {fmt(s_)}; Breite des 68-%-Intervalls {s_['hpd'][1] - s_['hpd'][0]:.1f}")


def how_many():
    """44. Wie viele Sirenen braucht man? (Zellen 29 von cosmology_sirens.ipynb)."""
    global FORECAST, NS, _, ax, col, draw, fig, lab, lnH, logp, med, n
    global n2, p, q, rng, shifts, sm, tot, w_, widths
    rng = np.random.default_rng(8)
    NS = np.array([1, 2, 3, 5, 10, 20, 50, 100, 200])
    lnH = np.log(H)


    def draw(p, n):
        c = np.cumsum(p)
        return np.interp(rng.random(n), c / c[-1], H)


    FORECAST = {}
    for lab, p in [("nur Gravitationswelle", P4["low"]), ("mit dem Jet", JET_RESULTS["low"][1])]:
        med = summary(p)["med"]
        logp = np.log(p + 1e-300)
        widths = []
        for n in NS:
            w_ = []
            for _ in range(100):
                shifts = np.log(draw(p, n) / med)
                tot = sum(np.interp(lnH - s_, lnH, logp, left=-700, right=-700) for s_ in shifts)
                q = np.exp(tot - tot.max())
                q /= np.trapz(q, H)
                sm = summary(q)
                w_.append((sm["hpd"][1] - sm["hpd"][0]) / 2 / sm["map"])
            widths.append(np.mean(w_))
        FORECAST[lab] = np.array(widths)

    fig, ax = plt.subplots(figsize=(11, 6))
    for (lab, w_), col in zip(FORECAST.items(), ["C0", "C3"]):
        ax.plot(NS, 100 * w_, "o-", color=col, ms=6, label=lab)
        ax.plot(NS, 100 * w_[0] / np.sqrt(NS), color=col, ls=":", lw=1.2, label=f"{lab}: σ₁/√N")
    ax.axhline(2, color="k", lw=1)
    ax.text(1.05, 2.15, "2 %", fontsize=10)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Zahl der Ereignisse N")
    ax.set_ylabel("relativer Fehler von H₀ (68 %, halbe Breite) [%]")
    ax.set_title("Wie viele Ereignisse wie GW170817 für 2 %?", fontsize=10)
    ax.legend(fontsize=9)
    plt.show()

    for lab, w_ in FORECAST.items():
        n2 = np.interp(np.log(0.02), np.log(w_[::-1]), np.log(NS[::-1]))
        print(f"{lab:22s}: " + ", ".join(f"N = {n}: {100 * x:.1f} %" for n, x in zip(NS, w_)) + f"; 2 % bei N ≈ {np.exp(n2):.0f}")


def literature():
    """45. Gegen die veröffentlichten Werte und die anderen Wege (Zellen 32 von cosmology_sirens.ipynb)."""
    global ax, col, em, ep, fig, i, lab, own, rows, to_p, to_s, v
    own = {"eigen: nur Gravitationswelle": (S4["low"]["map"], S4["low"]["hpd"][1] - S4["low"]["map"], S4["low"]["map"] - S4["low"]["hpd"][0]),
           "eigen: mit dem Jet": (JET_RESULTS["low"][2]["map"], JET_RESULTS["low"][2]["hpd"][1] - JET_RESULTS["low"][2]["map"],
                                  JET_RESULTS["low"][2]["map"] - JET_RESULTS["low"][2]["hpd"][0])}
    rows = [(k, *v, "C0") for k, v in own.items()]
    rows += [("Abbott et al. 2017", *ABBOTT17, "k"), ("Hotokezaka et al. 2019 (Jet)", *HOTOKEZAKA19, "k")]
    rows += [(k, *v, "k") for k, v in GWTC3.items()]
    rows += [(k, *v, "0.5") for k, v in OTHERS.items()]
    rows += [("Planck 2018", PLANCK[0], PLANCK[1], PLANCK[1], "C3"), ("SH0ES", SH0ES[0], SH0ES[1], SH0ES[1], "C2")]
    fig, ax = plt.subplots(figsize=(12, 6.5))
    for i, (lab, v, ep, em, col) in enumerate(rows):
        ax.errorbar(v, -i, xerr=[[em], [ep]], fmt="o", color=col, ms=7, capsize=4)
    ax.set_yticks(-np.arange(len(rows)))
    ax.set_yticklabels([r[0] for r in rows], fontsize=9.5)
    ax.axvspan(PLANCK[0] - PLANCK[1], PLANCK[0] + PLANCK[1], color="C3", alpha=0.15)
    ax.axvspan(SH0ES[0] - SH0ES[1], SH0ES[0] + SH0ES[1], color="C2", alpha=0.15)
    ax.set_xlabel("H₀ [km/s/Mpc]")
    ax.set_title("Standardsirenen zwischen frühem Universum und Entfernungsleiter", fontsize=10)
    plt.tight_layout()
    plt.show()

    for lab, (v, ep, em) in own.items():
        to_p = (v - PLANCK[0]) / np.hypot(em if v > PLANCK[0] else ep, PLANCK[1])
        to_s = (v - SH0ES[0]) / np.hypot(ep if v < SH0ES[0] else em, SH0ES[1])
        print(f"{lab:30s}: H₀ = {v:.1f} +{ep:.1f}/−{em:.1f}; gegen Planck {to_p:+.1f} σ, gegen SH0ES {to_s:+.1f} σ")
