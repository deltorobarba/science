"""Grenzen des Wissens für limits_of_knowledge.ipynb: Heisenberg-Grenze, Rechengrenze (LPN) und Statistik von Evaluationen.

Alles simuliert, keine Downloads. Metrologie: Quanten-Fisher-Information von N Qubits im Produktzustand und im
GHZ-Zustand, mit und ohne Dephasierung (geschlossene Formeln, numerisch an Dichtematrizen geprüft). Rechengrenze:
Learning Parity with Noise, wie viele Beispiele die Information enthalten (Shannon) und wie lange die Suche dauert.
Evaluation: wie viele Testaufgaben zwei KI-Agenten trennen, und pass@k gegen pass^k.
"""
import time

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm


def _n(x):
    """Zahl mit Leerzeichen als Tausendertrenner; nur die Zahl, nie den ganzen Satz ersetzen."""
    return f"{x:,.0f}".replace(",", " ")


# ---- Heisenberg-Grenze und Rauschen

def fisher_phase(N, gt, ghz):
    """Quanten-Fisher-Information für eine Phase: Produkt N·e^(−2γt), GHZ N²·e^(−2Nγt) (gt = γ·t)."""
    return N ** 2 * np.exp(-2 * N * gt) if ghz else N * np.exp(-2 * gt)


def best_rate(N, gamma, ghz, T=1.0):
    """Gesamte Fisher-Information für eine Frequenz ω (φ = ω t) bei Gesamtzeit T und bester Messdauer t.

    Wiederholungen T/t, je t²·F_φ(t): zusammen T·t·F_φ(t); das Maximum liegt bei t = 1/(2γ) bzw. 1/(2Nγ).
    """
    t = 1 / (2 * N * gamma) if ghz else 1 / (2 * gamma)
    return T * t * fisher_phase(N, gamma * t, ghz), t


def plot_metrology(N_max=100, gamma=1.0):
    """Links ohne Rauschen (Standardgrenze gegen Heisenberg-Grenze), rechts mit Dephasierung bei bester Messdauer."""
    N = np.arange(1, N_max + 1)
    sql, hl = 1 / np.sqrt(N), 1 / N
    prod = np.array([best_rate(n, gamma, False)[0] for n in N])
    ghz = np.array([best_rate(n, gamma, True)[0] for n in N])
    fixed = np.array([1.0 * (1 / (2 * gamma)) * fisher_phase(n, 0.5, True) for n in N])   # GHZ mit t = 1/(2γ)
    print(f"Ohne Rauschen, N = {N_max} Qubits: Standardgrenze Δφ = {sql[-1]:.3f}, Heisenberg-Grenze {hl[-1]:.3f} "
          f"({sql[-1] / hl[-1]:.0f}-mal genauer)")
    print(f"Mit Dephasierung γ, Gesamtzeit T = 1/γ, beste Messdauer: Δω Produkt {1 / np.sqrt(prod[-1]):.4f} γ, "
          f"GHZ {1 / np.sqrt(ghz[-1]):.4f} γ (Verhältnis {np.sqrt(prod[-1] / ghz[-1]):.2f}); beste Messdauer GHZ "
          f"{best_rate(N_max, gamma, True)[1]:.4f}/γ statt {best_rate(N_max, gamma, False)[1]:.1f}/γ")
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.6))
    axes[0].loglog(N, sql, color="tab:blue", lw=2, label="Produktzustand: Standardgrenze 1/√N")
    axes[0].loglog(N, hl, color="tab:red", lw=2, label="GHZ-Zustand: Heisenberg-Grenze 1/N")
    axes[0].set_xlabel("Zahl der Qubits N")
    axes[0].set_ylabel("kleinster Fehler Δφ einer Messung [rad]")
    axes[0].set_title("Ohne Rauschen: Verschränkung gewinnt √N", fontsize=10)
    axes[0].legend(fontsize=8)
    axes[1].loglog(N, 1 / np.sqrt(prod), color="tab:blue", lw=2, label="Produktzustand, beste Messdauer")
    axes[1].loglog(N, 1 / np.sqrt(ghz), color="tab:red", lw=2, ls="--", label="GHZ-Zustand, beste Messdauer")
    axes[1].loglog(N, 1 / np.sqrt(fixed), color="tab:red", lw=1, ls=":", label="GHZ mit der Messdauer des Produktzustands")
    axes[1].set_xlabel("Zahl der Qubits N")
    axes[1].set_ylabel("Fehler der Frequenz Δω [γ] bei Gesamtzeit 1/γ")
    axes[1].set_ylim(0.1, 20)
    axes[1].set_title("Mit Dephasierung: derselbe Fehler, der Vorteil ist weg", fontsize=10)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()


# ---- Rechengrenze: Learning Parity with Noise

_PAR = np.array([bin(i).count("1") & 1 for i in range(1 << 16)], dtype=np.uint8)   # Parität jeder 16-Bit-Zahl


def _parity(x):
    x = x.astype(np.int64)
    return _PAR[x & 0xFFFF] ^ _PAR[(x >> 16) & 0xFFFF]


def lpn(n, m, eta, rng):
    """m Beispiele (a, b) mit b = a·s ⊕ Rauschen: a zufällige n-Bit-Zahl, s geheim, Rauschen mit Wahrscheinlichkeit eta."""
    s = int(rng.integers(0, 1 << n))
    a = rng.integers(0, 1 << n, m)
    b = _parity(a & s) ^ (rng.random(m) < eta)
    return s, a, b


def brute_force(n, a, b, chunk=4096):
    """Maximum-Likelihood: alle 2^n Kandidaten prüfen, den mit den meisten Übereinstimmungen nehmen."""
    best, best_s = -1, -1
    for lo in range(0, 1 << n, chunk):
        cand = np.arange(lo, min(lo + chunk, 1 << n))
        agree = (_parity(cand[:, None] & a[None, :]) == b[None, :]).sum(axis=1)
        k = int(np.argmax(agree))
        if agree[k] > best:
            best, best_s = int(agree[k]), int(cand[k])
    return best_s


def shannon_samples(n, eta):
    """Beispiele für eine sichere Erkennung: Jedes Beispiel trägt höchstens 1 − H(eta) Bit über s, gebraucht werden n Bit."""
    H = -eta * np.log2(eta) - (1 - eta) * np.log2(1 - eta)
    return n / (1 - H)


def plot_lpn(ns=(8, 12, 16), eta=0.125, trials=20, ns_time=(10, 12, 14, 16, 18, 20), seed=0):
    """Links: Erfolg der Suche gegen die Zahl der Beispiele; rechts: Rechenzeit der Suche gegen n."""
    rng = np.random.default_rng(seed)
    H = -eta * np.log2(eta) - (1 - eta) * np.log2(1 - eta)
    print(f"Rauschen eta = {eta}: ein Beispiel trägt höchstens 1 − H(eta) = {1 - H:.3f} Bit, gebraucht werden n Bit; "
          "mit m Beispielen ist die Trefferquote höchstens (m(1 − H) + 1)/n (Fano)")
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.6))
    for n, c in zip(ns, ["tab:green", "tab:blue", "tab:purple"]):
        ms = np.unique(np.linspace(n, 6 * n, 11).astype(int))
        rate = []
        for m in ms:
            ok = 0
            for _ in range(trials):
                s, a, b = lpn(n, m, eta, rng)
                ok += brute_force(n, a, b) == s
            rate.append(ok / trials)
        m50 = float(np.interp(0.5, rate, ms)) if max(rate) >= 0.5 else float("nan")
        print(f"  n = {n:2d}: Hälfte gefunden ab etwa {m50:.0f} Beispielen; sicher erst ab etwa n/(1 − H) = "
              f"{shannon_samples(n, eta):.0f}; Fano-Grenze bei {m50:.0f} Beispielen {min(1, (m50 * (1 - H) + 1) / n):.2f}")
        axes[0].plot(ms, rate, "o-", ms=4, color=c, label=f"n = {n} Bit (Punkte: Suche)")
        mm = np.linspace(ms[0], ms[-1], 100)
        axes[0].plot(mm, np.minimum(1, (mm * (1 - H) + 1) / n), color=c, ls="--", lw=1)
        axes[0].axvline(shannon_samples(n, eta), color=c, ls=":", lw=1)
    axes[0].set_xlabel("Zahl der Beispiele m")
    axes[0].set_ylabel("Anteil richtig gefundener Geheimnisse")
    axes[0].set_title(f"Die Information ist da (gestrichelt: Fano-Grenze, gepunktet: n/(1 − H)), Rauschen {eta}", fontsize=10)
    axes[0].legend(fontsize=8)
    times = []
    for n in ns_time:
        s, a, b = lpn(n, 4 * n, eta, rng)
        t0 = time.perf_counter()
        brute_force(n, a, b)
        times.append(time.perf_counter() - t0)
    times = np.array(times)
    k, c0 = np.polyfit(ns_time, np.log2(times), 1)
    for n in [40, 64, 128]:
        sec = 2 ** (c0 + k * n)
        print(f"  Suche bei n = {n}: etwa {sec:.1e} s = {sec / 3.15e7:.1e} Jahre (hochgerechnet)")
    print(f"  gemessen: Rechenzeit wächst wie 2^({k:.2f}·n); n = {ns_time[-1]} braucht {times[-1]:.1f} s")
    axes[1].semilogy(ns_time, times, "o-", color="tab:red", label="Suche über alle 2ⁿ Kandidaten (gemessen)")
    nn = np.arange(ns_time[0], 41)
    axes[1].semilogy(nn, 2 ** (c0 + k * nn), color="tab:red", ls=":", label=f"hochgerechnet: 2^({k:.2f}·n)")
    axes[1].set_xlabel("Länge des Geheimnisses n [Bit]")
    axes[1].set_ylabel("Rechenzeit [s]")
    axes[1].set_title("Aber sie herauszuholen kostet exponentielle Zeit", fontsize=10)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()


# ---- Statistik von Evaluationen: Signal oder Zufall

def tasks_needed(p1, p2, alpha=0.05, power=0.8):
    """Aufgaben je Agent, um p1 von p2 mit Irrtum alpha (zweiseitig) und Trennschärfe power zu unterscheiden (z-Test)."""
    pb = (p1 + p2) / 2
    za, zb = norm.ppf(1 - alpha / 2), norm.ppf(power)
    return (za * np.sqrt(2 * pb * (1 - pb)) + zb * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / (p1 - p2) ** 2


def detect_rate(p1, p2, n, trials=4000, alpha=0.05, seed=0):
    """Anteil der Wiederholungen, in denen der z-Test bei n Aufgaben je Agent einen Unterschied findet."""
    rng = np.random.default_rng(seed)
    k1, k2 = rng.binomial(n, p1, trials), rng.binomial(n, p2, trials)
    pb = (k1 + k2) / (2 * n)
    z = (k2 - k1) / n / np.sqrt(np.maximum(2 * pb * (1 - pb) / n, 1e-12))
    return float(np.mean(np.abs(z) > norm.ppf(1 - alpha / 2)))


def plot_evaluation(p=0.70, deltas=(0.05, 0.10), ks=range(1, 21)):
    """Links: Trennschärfe gegen die Zahl der Aufgaben; rechts: pass@k und pass^k gegen k."""
    print(f"Ein Agent mit Erfolgsquote {p}: Fisher-Information je Aufgabe 1/(p(1 − p)) = {1 / (p * (1 - p)):.2f}, "
          f"also Standardfehler √(p(1 − p)/N): bei 100 Aufgaben ±{np.sqrt(p * (1 - p) / 100):.3f}, "
          f"bei 1000 ±{np.sqrt(p * (1 - p) / 1000):.3f}")
    for d in deltas:
        n = tasks_needed(p, p + d)
        print(f"  {p:.2f} gegen {p + d:.2f}: {_n(np.ceil(n))} Aufgaben je Agent für 80 % Trennschärfe "
              f"(simuliert: {detect_rate(p, p + d, int(np.ceil(n))):.0%})")
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.6))
    ns = np.unique(np.logspace(1, 3.7, 30).astype(int))
    for d, c in zip(deltas, ["tab:blue", "tab:red"]):
        axes[0].semilogx(ns, [detect_rate(p, p + d, n) for n in ns], "o-", ms=3, color=c, label=f"{p:.2f} gegen {p + d:.2f}")
        axes[0].axvline(tasks_needed(p, p + d), color=c, ls=":", lw=1)
    axes[0].axhline(0.8, color="grey", lw=0.6)
    axes[0].set_xlabel("Zahl der Aufgaben je Agent")
    axes[0].set_ylabel("Anteil der Läufe, die den Unterschied finden")
    axes[0].set_title("Signal oder Zufall: wie viele Aufgaben eine Evaluation braucht", fontsize=10)
    axes[0].legend(fontsize=8)
    k = np.array(list(ks))
    for q, c in zip([0.7, 0.9], ["tab:green", "tab:purple"]):
        axes[1].plot(k, 1 - (1 - q) ** k, "-", color=c, lw=2, label=f"pass@k, p = {q}: mindestens einer von k gelingt")
        axes[1].plot(k, q ** k, "--", color=c, lw=2, label=f"pass^k, p = {q}: alle k gelingen")
    axes[1].set_xlabel("Zahl der Versuche k")
    axes[1].set_ylabel("Wahrscheinlichkeit")
    axes[1].set_title("Dieselbe Erfolgsquote, zwei sehr verschiedene Kennzahlen", fontsize=10)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()
    print(f"  pass@5 und pass^5 bei p = 0.7: {1 - 0.3 ** 5:.3f} und {0.7 ** 5:.3f}; bei p = 0.9: {1 - 0.1 ** 5:.5f} und {0.9 ** 5:.3f}")
