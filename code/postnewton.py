"""Post-Newton-Reihe für approximation.ipynb: der Chirp von GW150914 als Taylor-Reihe in v/c und wo sie versagt.

Die Frequenz einer Gravitationswelle wächst, weil das Paar Energie abstrahlt. In der Variablen x = (v/c)² = (πGMf/c³)^(2/3)
gilt dx/dt = (64η/5M) x⁵ [1 + a₁x + a₁.₅x^1.5 + …] (Variante TaylorT4: Fluss durch Ableitung der Energie geteilt, als Reihe
entwickelt). Die Koeffizienten bis 3.5PN stammen aus Blanchet (Living Reviews in Relativity 17, 2, 2014, Gl. 233 und 314);
geprüft wurde, dass ihre Division die Koeffizienten von Buonanno und anderen (2009, Phys. Rev. D 80, 084043) ergibt, und
dass die Newtonsche Ordnung für zwei Neutronensterne die 16 031 Zyklen ab 10 Hz aus Blanchets Tabelle trifft. Massen von
GW150914 im Detektor gemessen (rotverschoben): 39 und 32 Sonnenmassen (LIGO 2016).
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import cumulative_trapezoid, trapezoid

G, C, MSUN = 6.674e-11, 2.998e8, 1.989e30
EULER_GAMMA = 0.5772156649015329
ORDERS = (0, 1, 1.5, 2, 2.5, 3, 3.5)


def coefficients(eta, x):
    """Koeffizienten a_k der Reihe für dx/dt bei Massenverhältnis η = m₁m₂/M²; 3PN enthält ln(16x)."""
    pi = np.pi
    return {0: 1.0,
            1: -743 / 336 - 11 / 4 * eta,
            1.5: 4 * pi,
            2: 34103 / 18144 + 13661 / 2016 * eta + 59 / 18 * eta ** 2,
            2.5: -(4159 / 672 + 189 / 8 * eta) * pi,
            3: (16447322263 / 139708800 - 1712 / 105 * EULER_GAMMA + 16 / 3 * pi ** 2 - 856 / 105 * np.log(16 * x)
                + (-56198689 / 217728 + 451 / 48 * pi ** 2) * eta + 541 / 896 * eta ** 2 - 5605 / 2592 * eta ** 3),
            3.5: (-4415 / 4032 + 358675 / 6048 * eta + 91495 / 1512 * eta ** 2) * pi}


def inspiral(m1, m2, f_start, order, n=4000):
    """Frequenz der Welle gegen die Zeit ab f_start bis zur innersten stabilen Bahn (x = 1/6), bis zur gegebenen Ordnung.

    Gibt (t [s], f [Hz], Zahl der Zyklen der Welle) zurück.
    """
    M = (m1 + m2) * MSUN * G / C ** 3
    eta = m1 * m2 / (m1 + m2) ** 2
    x = np.linspace((np.pi * M * f_start) ** (2 / 3), 1 / 6, n)
    a = coefficients(eta, x)
    s = sum(a[k] * x ** k for k in ORDERS if k <= order)
    dxdt = 64 * eta / (5 * M) * x ** 5 * s
    t = cumulative_trapezoid(1 / dxdt, x, initial=0)
    f = x ** 1.5 / (np.pi * M)
    cycles = trapezoid(f / dxdt, x)
    return t, f, cycles


def plot_chirp_orders(m1=39, m2=32, f_start=20, compare=(1.4, 1.4, 10), name="GW150914"):
    """Links die Korrekturterme relativ zu Newton gegen die Frequenz, rechts f(t) für jede Ordnung bis zur letzten stabilen Bahn."""
    M = (m1 + m2) * MSUN * G / C ** 3
    eta = m1 * m2 / (m1 + m2) ** 2
    f_isco = 6 ** -1.5 / (np.pi * M)
    print(f"{name} mit {m1} und {m2} Sonnenmassen: Chirp-Masse {(m1 + m2) * eta ** 0.6:.1f}, η = {eta:.4f}; "
          f"von {f_start} Hz (v/c = {(np.pi * M * f_start) ** (1 / 3):.2f}) bis zur letzten stabilen Bahn bei "
          f"{f_isco:.0f} Hz (v/c = {6 ** -0.5:.2f})")
    runs = {o: inspiral(m1, m2, f_start, o) for o in ORDERS}
    prev = None
    for o, (t, f, cyc) in runs.items():
        step = "" if prev is None else f", Änderung {cyc - prev:+.1f}"
        print(f"  bis {o:3g}PN: {t[-1]:.3f} s und {cyc:5.1f} Zyklen bis {f_isco:.0f} Hz{step}")
        prev = cyc
    a1, a2, fs = compare
    cyc = [inspiral(a1, a2, fs, o)[2] for o in ORDERS]
    print(f"Zum Vergleich zwei Neutronensterne mit {a1} und {a2} Sonnenmassen ab {fs} Hz: "
          + ", ".join(f"{o:g}PN {c:,.0f}".replace(",", " ") for o, c in zip(ORDERS, cyc))
          + f" Zyklen; der letzte Schritt ändert {cyc[-1] - cyc[-2]:+.1f}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    ax = axes[0]
    x = np.linspace((np.pi * M * f_start) ** (2 / 3), 1 / 6, 400)
    f = x ** 1.5 / (np.pi * M)
    a = coefficients(eta, x)
    colors = dict(zip(ORDERS[1:], ["tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown", "tab:pink"]))
    for o in ORDERS[1:]:
        ax.plot(f, a[o] * x ** o, color=colors[o], lw=1.6, label=f"{o:g}PN: a·(v/c)^{2 * o:g}")
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xlabel("Frequenz der Welle [Hz]")
    ax.set_ylabel("Korrektur relativ zur Newtonschen Ordnung")
    ax.set_title("Die Korrekturen wachsen mit v/c: am Ende sind sie nicht mehr klein", fontsize=10)
    ax.legend(fontsize=8, ncol=2)
    top = ax.secondary_xaxis("top", functions=(lambda ff: (np.pi * M * np.maximum(ff, 1e-3)) ** (1 / 3),
                                               lambda v: np.maximum(v, 1e-3) ** 3 / (np.pi * M)))
    top.set_xlabel("v/c")
    ax = axes[1]
    for o, c in zip(ORDERS, ["black"] + list(colors.values())):
        t, ff, cyc = runs[o]
        ax.plot(t, ff, color=c, lw=2 if o == 0 else 1.3, label=f"bis {o:g}PN: {cyc:.1f} Zyklen")
        ax.plot(t[-1], ff[-1], "o", color=c, ms=5)
    ax.set_xlabel(f"Zeit seit {f_start} Hz [s]")
    ax.set_ylabel("Frequenz der Welle [Hz]")
    ax.set_title(f"{name} bis zur letzten stabilen Bahn ({f_isco:.0f} Hz)", fontsize=10)
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    plt.show()
    return runs
