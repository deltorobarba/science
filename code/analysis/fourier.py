"""Harmonische Analysis: Abfall der Koeffizienten, Gibbs, Parseval, Fourier-Paare, Unschärfe, Faltung, Poisson-Summe, FFT, Abtasttheorem, Fenster, Spektrogramm, Wavelets, Wärmeleitung, Beugung und Fourier auf endlichen Gruppen.

Für analysis.ipynb aus fourieranalysis.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, smoothness_decay, gibbs_phenomenon, parseval, transform_pairs, uncertainty, convolution, poisson_summation, dft_fft, sampling, leakage, spectrogram, wavelets, heat_equation, diffraction, finite_groups.
"""
import time
from fractions import Fraction
import numpy as np
import matplotlib.pyplot as plt
from scipy import fft as sfft, integrate, signal, special
from math import gcd


def load():
    """16. Daten (Zellen 4 von fourieranalysis.ipynb)."""
    global continuous_ft, fourier_coefficients, partial_sum, spread
    # Alles hier (numpy, scipy, matplotlib) ist in Colab vorinstalliert

    def fourier_coefficients(f, K, M=2 ** 14):
        """Fourier-Koeffizienten c_k (k = −K … K) einer 2π-periodischen Funktion aus M Abtastwerten auf [−π, π)."""
        x = -np.pi + 2 * np.pi * np.arange(M) / M
        k = np.arange(-K, K + 1)
        return k, np.fft.fft(f(x))[k % M] / M * (-1.0) ** k        # Faktor (−1)^k, weil das Gitter bei −π beginnt

    def partial_sum(k, c, x, weights=None):
        """Fourier-Partialsumme Σ w_k c_k e^{ikx}; mit Gewichten w_k z. B. das Fejér-Mittel."""
        w = np.ones_like(c) if weights is None else weights
        return np.real(np.exp(1j * np.outer(x, k)) @ (w * c))

    def continuous_ft(fx, x):
        """Fourier-Transformation f̂(ξ) = ∫ f(x) e^{−2πixξ} dx, genähert mit der FFT auf einem gleichmäßigen Gitter x."""
        dx = x[1] - x[0]
        xi = np.fft.fftshift(np.fft.fftfreq(len(x), dx))
        return xi, dx * np.exp(-2j * np.pi * xi * x[0]) * np.fft.fftshift(np.fft.fft(fx))

    def spread(values, grid):
        """Breite (Standardabweichung) der Verteilung |f|² auf einem Gitter."""
        p = np.abs(values) ** 2
        p = p / p.sum()
        mean = np.sum(grid * p)
        return np.sqrt(np.sum((grid - mean) ** 2 * p))

    print("Werkzeuge bereit: Fourier-Koeffizienten, Partialsummen, Fourier-Transformation per FFT, Breite einer Verteilung")


def smoothness_decay():
    """17. Glattheit und der Abfall der Fourier-Koeffizienten (Zellen 6 von fourieranalysis.ipynb)."""
    global K, Ns, _, axes, c, ck, coef, colors, err, ex, exact, f
    global fig, funcs, k, keep, kk, ls, mag, name, near, odd, p, ratio
    global slope, x, xe
    funcs = {
        "Rechteck (Sprung)": lambda x: np.sign(x) * (np.abs(x) < np.pi),
        "Dreieck |x| (Knick)": lambda x: np.abs(x),
        "x(π − |x|) (Sprung erst in f'')": lambda x: x * (np.pi - np.abs(x)),
        "Poisson-Kern r = 0.5 (analytisch)": lambda x: 0.75 / (1.25 - np.cos(x)),
    }
    exact = [lambda k: 2 / (np.pi * k), lambda k: 2 / (np.pi * k ** 2), lambda k: 4 / (np.pi * k ** 3), lambda k: 0.5 ** k]
    K = 400
    x = np.linspace(-np.pi, np.pi, 4001)
    colors = ["tab:blue", "tab:orange", "tab:green", "tab:red"]
    coef = {name: fourier_coefficients(f, K) for name, f in funcs.items()}

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    for (name, f), c in zip(funcs.items(), colors):
        k, ck = coef[name]
        axes[0].plot(x, f(x), c=c, lw=1, ls="--")
        axes[0].plot(x, partial_sum(k[np.abs(k) <= 5], ck[np.abs(k) <= 5], x), c=c, lw=1.5, label=name)
    axes[0].set_xlabel("x")
    axes[0].set_ylabel("f(x)")
    axes[0].set_title("Gestrichelt f, durchgezogen die Partialsumme bis |k| = 5", fontsize=10)
    axes[0].legend(fontsize=7)
    kk = np.arange(1, K + 1)
    for (name, _), c, ex in zip(funcs.items(), colors, exact):
        k, ck = coef[name]
        mag = np.abs(ck[K + 1:])
        keep = mag > 1e-15
        axes[1].loglog(kk[keep], mag[keep], ".", c=c, ms=3, label=name)
    for p, ls in zip([1, 2, 3], [":", "--", "-."]):
        axes[1].loglog(kk, 0.6 * kk ** -float(p), "k", ls=ls, lw=0.8, label=f"∝ 1/k^{p}")
    axes[1].set_ylim(1e-12, 3)
    axes[1].set_xlabel("Frequenz k")
    axes[1].set_ylabel("|c_k|")
    axes[1].set_title("Je glatter f, desto schneller fallen die Koeffizienten", fontsize=10)
    axes[1].legend(fontsize=7, ncol=2)
    Ns = np.unique(np.round(np.geomspace(1, 300, 30)).astype(int))
    near = np.geomspace(1e-7, 0.1, 300)
    xe = np.sort(np.r_[x, near, -near, np.pi - near, -np.pi + near])   # mit Punkten dicht an den Sprungstellen 0 und ±π
    for (name, f), c in zip(funcs.items(), colors):
        k, ck = coef[name]
        err = [np.max(np.abs(f(xe) - partial_sum(k[np.abs(k) <= N], ck[np.abs(k) <= N], xe))) for N in Ns]
        axes[2].loglog(Ns, err, "o-", c=c, ms=3, label=name)
    axes[2].set_xlabel("Zahl der Frequenzen N")
    axes[2].set_ylabel("größter Fehler max |f − S_N|")
    axes[2].set_title("Fehler der Partialsumme S_N", fontsize=10)
    axes[2].legend(fontsize=7)
    plt.tight_layout()
    plt.show()

    odd = np.arange(11, 202, 2)
    for (name, _), ex in zip(funcs.items(), exact):
        k, ck = coef[name]
        if "Poisson" in name:
            ratio = np.abs(ck[K + 11]) / np.abs(ck[K + 10])
            print(f"{name:34s}: c_11/c_10 = {ratio:.4f} (Theorie r = 0.5), |c_20| = {abs(ck[K + 20]):.2e} (Theorie {0.5 ** 20:.2e})")
        else:
            slope = np.polyfit(np.log(odd), np.log(np.abs(ck[K + odd])), 1)[0]
            print(f"{name:34s}: Steigung von log|c_k| gegen log k: {slope:.3f};  |c_11| = {abs(ck[K + 11]):.5f} (Formel {ex(11):.5f})")


def gibbs_phenomenon():
    """18. Das Gibbs-Phänomen und die Fejér-Mittel (Zellen 9 von fourieranalysis.ipynb)."""
    global D, F, N, Ns, axes, c, ck, fejer_weights, fig, gibbs, k, leb
    global m, over_F, over_S, square, xf, xl, xs, xz
    square = funcs["Rechteck (Sprung)"]
    k, ck = fourier_coefficients(square, 2000, M=2 ** 18)                # feines Gitter, damit auch c_2000 genau ist
    xz = np.linspace(-0.3, 1.0, 3000)

    def fejer_weights(k, N):
        return np.clip(1 - np.abs(k) / (N + 1), 0, None)

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    axes[0].plot(xz, square(xz), "k-", lw=1, label="Rechteck")
    for N, c in zip([10, 50, 250], ["tab:blue", "tab:orange", "tab:green"]):
        m = np.abs(k) <= N
        axes[0].plot(xz, partial_sum(k[m], ck[m], xz), c=c, lw=1, label=f"S_{N}")
    m = np.abs(k) <= 250
    axes[0].plot(xz, partial_sum(k[m], ck[m], xz, fejer_weights(k[m], 250)), "r--", lw=1.5, label="Fejér-Mittel σ_250")
    axes[0].axhline(2 / np.pi * special.sici(np.pi)[0], color="grey", ls=":", lw=1, label="Gibbs-Grenze 1.179")
    axes[0].set_xlabel("x")
    axes[0].set_ylabel("Wert")
    axes[0].set_title("Überschwingen am Sprung wandert, bleibt aber gleich hoch", fontsize=10)
    axes[0].legend(fontsize=7)
    xs = np.linspace(-np.pi, np.pi, 4001)
    N = 10
    with np.errstate(invalid="ignore", divide="ignore"):
        D = np.where(np.abs(xs) < 1e-12, 2 * N + 1, np.sin((N + 0.5) * xs) / np.sin(xs / 2))
        F = np.where(np.abs(xs) < 1e-12, N + 1, (np.sin((N + 1) * xs / 2) / np.sin(xs / 2)) ** 2 / (N + 1))
    axes[1].plot(xs, D, label=f"Dirichlet-Kern D_{N} (S_N = f ∗ D_N)")
    axes[1].plot(xs, F, label=f"Fejér-Kern F_{N} (σ_N = f ∗ F_N), ≥ 0")
    axes[1].axhline(0, color="grey", lw=0.5)
    axes[1].set_xlabel("x")
    axes[1].set_title(f"Die beiden Kerne für N = {N}", fontsize=10)
    axes[1].legend(fontsize=8)
    Ns = np.unique(np.round(np.geomspace(5, 1000, 25)).astype(int))
    over_S, over_F, leb = [], [], []
    for N in Ns:
        xf = np.linspace(1e-6, 6 * np.pi / (N + 1), 3000)
        m = np.abs(k) <= N
        over_S.append(partial_sum(k[m], ck[m], xf).max())
        over_F.append(partial_sum(k[m], ck[m], xf, fejer_weights(k[m], N)).max())
        xl = np.linspace(-np.pi, np.pi, 200_001)[1:]
        with np.errstate(invalid="ignore", divide="ignore"):
            leb.append(np.mean(np.abs(np.sin((N + 0.5) * xl) / np.sin(xl / 2))))
    axes[2].semilogx(Ns, over_S, "o-", ms=3, label="max S_N (nahe am Sprung)")
    axes[2].semilogx(Ns, over_F, "s-", ms=3, label="max σ_N (Fejér)")
    axes[2].axhline(2 / np.pi * special.sici(np.pi)[0], color="k", ls="--", lw=1, label="(2/π)·Si(π) = 1.179")
    axes[2].set_xlabel("N")
    axes[2].set_ylabel("Maximum der Näherung")
    axes[2].set_title("Das Überschwingen verschwindet nicht", fontsize=10)
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    gibbs = 2 / np.pi * special.sici(np.pi)[0]
    print(f"Maximum von S_N bei N = {Ns[0]}, {Ns[12]}, {Ns[-1]}: {over_S[0]:.4f}, {over_S[12]:.4f}, {over_S[-1]:.4f}  (Grenzwert (2/π)Si(π) = {gibbs:.5f})")
    print(f"Überschwingen in Prozent des Sprungs 2: {(over_S[-1] - 1) / 2:.2%}  (Theorie {(gibbs - 1) / 2:.2%});  Fejér-Maximum höchstens {max(over_F):.4f}")
    print(f"Lebesgue-Konstanten (1/2π)∫|D_N| bei N = {Ns[0]}, {Ns[12]}, {Ns[-1]}: {leb[0]:.3f}, {leb[12]:.3f}, {leb[-1]:.3f}  "
          f"(Näherung (4/π²) ln N + 1.27: {4 / np.pi ** 2 * np.log(Ns[0]) + 1.27:.3f}, {4 / np.pi ** 2 * np.log(Ns[12]) + 1.27:.3f}, {4 / np.pi ** 2 * np.log(Ns[-1]) + 1.27:.3f})")


def parseval():
    """19. Parseval und das Basel-Problem (Zellen 12 von fourieranalysis.ipynb)."""
    global M, Ns, axes, c, ck, e_F, e_S, f, fig, k, l2, m
    global n, name, odd_k, parabola, partial_sum_grid, sawtooth, share, tail, tests, xg, xm
    xg = np.linspace(-np.pi, np.pi, 8193)
    sawtooth = lambda x: x * (np.abs(x) < np.pi)
    parabola = lambda x: x ** 2
    M = 2 ** 18
    xm = -np.pi + 2 * np.pi * np.arange(M) / M                        # feines periodisches Gitter für die Fehlerintegrale

    def partial_sum_grid(k, c):
        """Partialsumme auf dem Gitter xm über eine inverse FFT (schnell auch für viele Punkte)."""
        C = np.zeros(M, dtype=complex)
        C[k % M] = c * (-1.0) ** k
        return np.real(np.fft.ifft(C) * M)

    def tail(name, N):
        """Exakte Energie der weggelassenen Koeffizienten Σ_{|k|>N} |c_k|² (über die Polygamma-Funktion)."""
        if name.startswith("Säge"):
            return 2 * special.polygamma(1, N + 1)
        if name.startswith("Parabel"):
            return 8 * special.polygamma(3, N + 1) / 6
        m = N + 1 if N % 2 == 0 else N + 2                            # erste ungerade Zahl über N
        return 8 / np.pi ** 2 * special.polygamma(1, m / 2) / 4

    tests = [("Sägezahn x", sawtooth), ("Parabel x²", parabola), ("Rechteck", square)]
    Ns = np.unique(np.round(np.geomspace(1, 200, 20)).astype(int))

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    for (name, f), c in zip(tests, ["tab:blue", "tab:orange", "tab:green"]):
        k, ck = fourier_coefficients(f, 200, M=M)
        l2 = [np.mean((f(xm) - partial_sum_grid(k[np.abs(k) <= N], ck[np.abs(k) <= N])) ** 2) for N in Ns]
        axes[0].loglog(Ns, l2, "o", c=c, ms=4, label=f"{name}: gemessen")
        axes[0].loglog(Ns, [tail(name, N) for N in Ns], "-", c=c, lw=1, label=f"{name}: Σ_|k|>N |c_k|² exakt")
    axes[0].set_xlabel("N")
    axes[0].set_ylabel("mittlerer quadratischer Fehler")
    axes[0].set_title("L²-Fehler = Energie der weggelassenen Koeffizienten", fontsize=10)
    axes[0].legend(fontsize=7)
    n = np.arange(1, 10_001)
    axes[1].loglog(n, np.pi ** 2 / 6 - np.cumsum(1 / n ** 2), label="π²/6 − Σ_{k≤n} 1/k²")
    axes[1].loglog(n, np.pi ** 4 / 90 - np.cumsum(1 / n ** 4.0), label="π⁴/90 − Σ_{k≤n} 1/k⁴")
    axes[1].loglog(n, 1 / n, "k:", lw=1, label="1/n")
    axes[1].loglog(n, 1 / (3 * n ** 3.0), "k--", lw=1, label="1/(3n³)")
    axes[1].set_ylim(1e-13, 1)
    axes[1].set_xlabel("Zahl der Summanden n")
    axes[1].set_ylabel("Abstand zum Grenzwert")
    axes[1].set_title("Aus Parseval: ζ(2) = π²/6 und ζ(4) = π⁴/90", fontsize=10)
    axes[1].legend(fontsize=8)
    k, ck = fourier_coefficients(square, 400)
    odd_k = np.arange(1, 30, 2)
    share = 2 * np.abs(ck[400 + odd_k]) ** 2
    axes[2].bar(odd_k, share, width=1.2, alpha=0.7, label="Anteil der Harmonischen k an der Energie")
    axes[2].plot(odd_k, np.cumsum(share), "ko-", ms=3, label="Summe bis k")
    axes[2].set_xlabel("Harmonische k (nur ungerade)")
    axes[2].set_ylabel("Anteil an (1/2π)∫f² = 1")
    axes[2].set_title("Rechteck: Energie in den Harmonischen", fontsize=10)
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    k, ck = fourier_coefficients(sawtooth, 400)
    print(f"Sägezahn: (1/2π)∫x² = {integrate.trapezoid(xg ** 2, xg) / (2 * np.pi):.6f} = π²/3 = {np.pi ** 2 / 3:.6f};  Σ|c_k|² über |k| ≤ 400 = {np.sum(np.abs(ck) ** 2):.6f}, "
          f"fehlender Rest Σ_|k|>400 1/k² = {2 * special.polygamma(1, 401):.6f}")
    print(f"Daraus ζ(2) = π²/6 = {np.pi ** 2 / 6:.6f};  Σ 1/k² bis 10 000 = {np.sum(1 / n ** 2):.6f}")
    print(f"Daraus ζ(4) = π⁴/90 = {np.pi ** 4 / 90:.8f};  Σ 1/k⁴ bis 10 000 = {np.sum(1 / n ** 4.0):.8f}")
    print(f"Rechteck: Grundton trägt {share[0]:.4f} der Energie (Theorie 8/π² = {8 / np.pi ** 2:.4f}), bis k = 5: {np.cumsum(share)[2]:.4f}")
    k, ck = fourier_coefficients(square, 400)
    m = np.abs(k) <= 10
    e_S = np.mean((square(xm) - partial_sum_grid(k[m], ck[m])) ** 2)
    e_F = np.mean((square(xm) - partial_sum_grid(k[m], ck[m] * fejer_weights(k[m], 10))) ** 2)
    print(f"Rechteck, N = 10: L²-Fehler der Partialsumme {e_S:.4f} (exakt {tail('Rechteck', 10):.4f}), des Fejér-Mittels {e_F:.4f} (die Partialsumme ist die beste L²-Näherung)")


def transform_pairs():
    """20. Fourier-Transformation: Paare und Eigenfunktionen (Zellen 15 von fourieranalysis.ipynb)."""
    global F, H, axes, back, c, fhat, fig, fx, h, hermite_function, lam, n
    global name, pairs, sel, x, xi
    x = np.linspace(-20, 20, 2 ** 14, endpoint=False)
    pairs = [
        ("Gauß e^(−πx²)", np.exp(-np.pi * x ** 2), lambda s: np.exp(-np.pi * s ** 2)),
        ("Rechteck auf [−½, ½]", (np.abs(x) < 0.5).astype(float), lambda s: np.sinc(s)),
        ("Laplace e^(−|x|)", np.exp(-np.abs(x)), lambda s: 2 / (1 + 4 * np.pi ** 2 * s ** 2)),
    ]

    def hermite_function(n, x):
        """Hermite-Funktion H_n(√(2π) x) e^{−πx²}, normiert; Eigenfunktion der Fourier-Transformation."""
        h = special.eval_hermite(n, np.sqrt(2 * np.pi) * x) * np.exp(-np.pi * x ** 2)
        return h / np.sqrt(np.sum(h ** 2) * (x[1] - x[0]))

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    for (name, fx, fhat), c in zip(pairs, ["tab:blue", "tab:orange", "tab:green"]):
        axes[0].plot(x, fx, c=c, label=name)
        xi, F = continuous_ft(fx, x)
        sel = np.abs(xi) <= 3
        axes[1].plot(xi[sel][::6], F.real[sel][::6], "o", c=c, ms=3)
        axes[1].plot(xi[sel], fhat(xi[sel]), "-", c=c, lw=1, label=f"{name} → exakt")
    axes[0].set_xlim(-3, 3)
    axes[0].set_xlabel("x")
    axes[0].set_ylabel("f(x)")
    axes[0].set_title("Drei Funktionen", fontsize=10)
    axes[0].legend(fontsize=8)
    axes[1].axhline(0, color="grey", lw=0.5)
    axes[1].set_xlabel("Frequenz ξ")
    axes[1].set_ylabel("f̂(ξ)")
    axes[1].set_title("Transformierte: Punkte per FFT, Linien exakt", fontsize=10)
    axes[1].legend(fontsize=8)
    for n, c in zip(range(4), ["tab:blue", "tab:orange", "tab:green", "tab:red"]):
        h = hermite_function(n, x)
        xi, H = continuous_ft(h, x)
        axes[2].plot(x, h, c=c, lw=1.2, label=f"h_{n}, Eigenwert (−i)^{n} = {['1', '−i', '−1', 'i'][n]}")
        back = np.interp(x, xi, (H / (-1j) ** n).real)
        axes[2].plot(x[::160], back[::160], "o", c=c, ms=3)
    axes[2].set_xlim(-2.5, 2.5)
    axes[2].set_xlabel("x bzw. ξ")
    axes[2].set_title("Hermite-Funktionen: ĥ_n = (−i)ⁿ h_n (Punkte: ĥ_n / (−i)ⁿ)", fontsize=10)
    axes[2].legend(fontsize=7)
    plt.tight_layout()
    plt.show()

    for name, fx, fhat in pairs:
        xi, F = continuous_ft(fx, x)
        sel = np.abs(xi) <= 3
        print(f"{name:22s}: größter Fehler der FFT-Näherung für |ξ| ≤ 3: {np.max(np.abs(F[sel] - fhat(xi[sel]))):.1e};  "
              f"Plancherel ∫|f|² = {np.sum(np.abs(fx) ** 2) * (x[1] - x[0]):.6f}, ∫|f̂|² = {np.sum(np.abs(F) ** 2) * (xi[1] - xi[0]):.6f}")
    lam = []
    for n in range(8):
        h = hermite_function(n, x)
        xi, H = continuous_ft(h, x)
        lam.append(np.sum(np.conj(h) * np.interp(x, xi, H.real) + 1j * np.conj(h) * np.interp(x, xi, H.imag)) * (x[1] - x[0]))
    print("Eigenwerte ⟨h_n, ĥ_n⟩ für n = 0 … 7: " + ", ".join(f"{z.real:+.3f}{z.imag:+.3f}i" for z in lam))


def uncertainty():
    """21. Unschärfeprinzipien (Zellen 18 von fourieranalysis.ipynb)."""
    global F, N, _, a, axes, bound, comb, combs, d, ds_random, ds_struct, dxs
    global f, fig, fx, gauss_pts, n, name, names, products, random_pts, rng, s, shapes
    global ss, theory, wave_packets, x, xi
    rng = np.random.default_rng(5)
    x = np.linspace(-40, 40, 2 ** 15, endpoint=False)
    bound = 1 / (4 * np.pi)
    shapes = {
        "Gauß": np.exp(-np.pi * x ** 2),
        "Dreieck": np.clip(1 - np.abs(x), 0, None),
        "Laplace e^(−|x|)": np.exp(-np.abs(x)),
        "Gauß mit Chirp": np.exp(-np.pi * x ** 2 * (1 + 2j)),
    }
    theory = {"Gauß": 1.0, "Dreieck": np.sqrt(0.1) * np.sqrt(3) / (2 * np.pi) / bound, "Laplace e^(−|x|)": np.sqrt(0.5) / (2 * np.pi) / bound, "Gauß mit Chirp": np.sqrt(5)}
    products = {}
    for name, fx in shapes.items():
        xi, F = continuous_ft(fx, x)
        products[name] = spread(fx, x) * spread(F, xi)

    def wave_packets(rng):
        """Summe von drei Gaußschen Wellenpaketen mit zufälliger Lage, Breite und Frequenz."""
        f = np.zeros_like(x, dtype=complex)
        for _ in range(3):
            a, x0, nu = rng.uniform(0.3, 3), rng.uniform(-4, 4), rng.uniform(-2, 2)
            f += rng.normal() * np.exp(-np.pi * ((x - x0) / a) ** 2 + 2j * np.pi * nu * x)
        return f

    random_pts = []
    for _ in range(300):
        fx = wave_packets(rng)
        xi, F = continuous_ft(fx, x)
        random_pts.append((spread(fx, x), spread(F, xi)))
    random_pts = np.array(random_pts)
    gauss_pts = []
    for a in np.geomspace(0.2, 5, 9):
        fx = np.exp(-np.pi * (x / a) ** 2)
        xi, F = continuous_ft(fx, x)
        gauss_pts.append((spread(fx, x), spread(F, xi)))
    gauss_pts = np.array(gauss_pts)

    N = 64
    ds_random = []                                                    # zufällige dünne Vektoren: fast immer volle DFT
    for _ in range(400):
        s = rng.integers(1, N + 1)
        f = np.zeros(N, dtype=complex)
        f[rng.choice(N, s, replace=False)] = rng.normal(size=s) + 1j * rng.normal(size=s)
        ds_random.append((s, np.sum(np.abs(np.fft.fft(f)) > 1e-9)))
    ds_random = np.array(ds_random)
    ds_struct = []                                                    # Summen von 1–3 verschobenen, modulierten Kämmen
    for _ in range(400):
        f = np.zeros(N, dtype=complex)
        for _ in range(rng.integers(1, 4)):
            d = rng.choice([2, 4, 8, 16, 32])
            comb = np.zeros(N)
            comb[rng.integers(d)::d] = 1
            f += rng.normal() * comb * np.exp(2j * np.pi * rng.integers(N) * np.arange(N) / N)
        ds_struct.append((np.sum(np.abs(f) > 1e-9), np.sum(np.abs(np.fft.fft(f)) > 1e-9)))
    ds_struct = np.array(ds_struct)
    combs = []
    for d in [1, 2, 4, 8, 16, 32, 64]:
        f = np.zeros(N)
        f[::d] = 1
        combs.append((np.sum(f != 0), np.sum(np.abs(np.fft.fft(f)) > 1e-9)))
    combs = np.array(combs)

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    names = list(products)
    axes[0].bar(names, [products[n] / bound for n in names], alpha=0.7, label="gemessen")
    axes[0].plot(names, [theory[n] for n in names], "ko", label="Theorie")
    axes[0].axhline(1, color="tab:red", ls="--", label="Untergrenze 1/(4π)")
    axes[0].set_ylabel("Δx · Δξ in Einheiten von 1/(4π)")
    axes[0].set_title("Nur die Gauß-Funktion erreicht die Grenze", fontsize=10)
    axes[0].legend(fontsize=8)
    axes[1].loglog(random_pts[:, 0], random_pts[:, 1], ".", ms=4, alpha=0.6, label="300 zufällige Wellenpakete")
    axes[1].loglog(gauss_pts[:, 0], gauss_pts[:, 1], "o", c="tab:red", ms=5, label="Gauß-Funktionen")
    dxs = np.geomspace(0.03, 10, 50)
    axes[1].loglog(dxs, bound / dxs, "k--", lw=1, label="Δx · Δξ = 1/(4π)")
    axes[1].set_xlabel("Breite Δx")
    axes[1].set_ylabel("Breite Δξ")
    axes[1].set_title("Kein Signal liegt unter der Hyperbel", fontsize=10)
    axes[1].legend(fontsize=8)
    axes[2].plot(ds_struct[:, 0], ds_struct[:, 1], ".", ms=5, alpha=0.5, label="Summen von 1–3 Kämmen (verschoben, moduliert)")
    axes[2].plot(ds_random[:, 0], ds_random[:, 1], "x", c="grey", ms=3, alpha=0.5, label="zufällige dünne Vektoren")
    axes[2].plot(combs[:, 0], combs[:, 1], "o", c="tab:red", ms=6, label="Dirac-Kämme (Gleichheit)")
    ss = np.linspace(1, N, 200)
    axes[2].plot(ss, N / ss, "k--", lw=1, label=f"|supp f| · |supp f̂| = N = {N}")
    axes[2].set_xscale("log", base=2)
    axes[2].set_yscale("log", base=2)
    axes[2].set_xlabel("Zahl der Einträge ≠ 0 in f")
    axes[2].set_ylabel("Zahl der Einträge ≠ 0 in der DFT")
    axes[2].set_title("Donoho-Stark auf ℤ_64", fontsize=10)
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    for n in names:
        print(f"{n:17s}: Δx·Δξ = {products[n]:.4f} = {products[n] / bound:.3f} × 1/(4π)  (Theorie {theory[n]:.3f})")
    print(f"Zufällige Wellenpakete: kleinstes Produkt {np.min(random_pts[:, 0] * random_pts[:, 1]) / bound:.3f} × 1/(4π)")
    print(f"Donoho-Stark: kleinstes |supp f|·|supp f̂| bei den Kammsummen {np.min(ds_struct[:, 0] * ds_struct[:, 1])}, bei den reinen Kämmen {sorted(set(combs[:, 0] * combs[:, 1]))}; "
          f"zufällige dünne Vektoren mit voller DFT (64 Einträge ≠ 0): {np.mean(ds_random[:, 1] == N):.0%}")


def convolution():
    """22. Der Faltungssatz (Zellen 21 von fourieranalysis.ipynb)."""
    global L, _, a, axes, b, best, circular, clean, direct, f, fig, fun
    global kernel, lin_same, linear, m, n, noisy, rng, sizes, store, t, t0, t_direct
    global t_fft, tk, via_fft
    rng = np.random.default_rng(6)
    n = 2000
    t = np.arange(n) / n
    clean = np.where(t > 0.5, 1.0, 0.0) + 0.5 * np.sin(2 * np.pi * 3 * t)
    noisy = clean + 0.3 * rng.normal(size=n)
    tk = np.arange(-200, 201) / n
    kernel = np.exp(-tk ** 2 / (2 * 0.01 ** 2))
    kernel /= kernel.sum()
    direct = np.convolve(noisy, kernel, mode="same")
    via_fft = signal.fftconvolve(noisy, kernel, mode="same")
    L = n + len(kernel) - 1
    circular = np.real(np.fft.ifft(np.fft.fft(noisy) * np.fft.fft(kernel, n)))           # ohne Auffüllen mit Nullen
    linear = np.real(np.fft.ifft(np.fft.fft(noisy, L) * np.fft.fft(kernel, L)))            # mit Auffüllen

    sizes = 2 ** np.arange(6, 16)
    t_direct, t_fft = [], []
    for m in sizes:
        a, b = rng.normal(size=m), rng.normal(size=m)
        for store, fun in [(t_direct, np.convolve), (t_fft, signal.fftconvolve)]:
            best = np.inf
            for _ in range(3):
                t0 = time.perf_counter(); fun(a, b); best = min(best, time.perf_counter() - t0)
            store.append(best)

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    axes[0].plot(t, noisy, lw=0.5, alpha=0.6, label="verrauschtes Signal")
    axes[0].plot(t, direct, lw=1.5, label="gefaltet mit Gauß-Kern (σ = 0.01)")
    axes[0].plot(t, clean, "k--", lw=1, label="ohne Rauschen")
    axes[0].set_xlabel("t")
    axes[0].set_title("Glätten = Falten mit einem Kern", fontsize=10)
    axes[0].legend(fontsize=8)
    f = np.fft.rfftfreq(n, 1 / n)
    axes[1].semilogy(f, np.abs(np.fft.rfft(noisy)), lw=0.6, label="|Spektrum des Signals|")
    axes[1].semilogy(f, np.abs(np.fft.rfft(kernel, n)) * 300, lw=1.5, label="|Spektrum des Kerns| × 300")
    axes[1].semilogy(f, np.abs(np.fft.rfft(direct)), lw=0.8, label="|Spektrum des Ergebnisses|")
    axes[1].set_xlim(0, 300)
    axes[1].set_ylim(1e-3, 3e3)
    axes[1].set_xlabel("Frequenz [Schwingungen pro Signallänge]")
    axes[1].set_title("Im Spektrum: Faltung = Multiplikation", fontsize=10)
    axes[1].legend(fontsize=8)
    axes[2].loglog(sizes, t_direct, "o-", label="direkt, O(N²)")
    axes[2].loglog(sizes, t_fft, "s-", label="über die FFT, O(N log N)")
    axes[2].set_xlabel("Länge N beider Folgen")
    axes[2].set_ylabel("Rechenzeit [s]")
    axes[2].set_title("Rechenzeit der Faltung", fontsize=10)
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"Direkte Faltung gegen FFT-Faltung: größter Unterschied {np.max(np.abs(direct - via_fft)):.1e}")
    lin_same = linear[len(kernel) // 2: len(kernel) // 2 + n]
    print(f"FFT mit Auffüllen gegen direkt: {np.max(np.abs(lin_same - direct)):.1e};  ohne Auffüllen (zyklisch): {np.max(np.abs(np.roll(circular, -(len(kernel) // 2)) - direct)):.2f} (Fehler an den Rändern)")
    print(f"Rechenzeit bei N = {sizes[-1]}: direkt {t_direct[-1] * 1e3:.1f} ms, FFT {t_fft[-1] * 1e3:.2f} ms, Verhältnis {t_direct[-1] / t_fft[-1]:.0f}")


def poisson_summation():
    """23. Die Poissonsche Summenformel (Zellen 24 von fourieranalysis.ipynb)."""
    global Kk, Nn, a, axes, exact_sum, fig, i, left, left_partial, right, right_partial, t
    global theta_terms, ts
    def theta_terms(t, side, tol=1e-15):
        """Partialsummen beider Seiten von Σ e^{−πn²t} = t^{−1/2} Σ e^{−πk²/t}; gibt Wert und nötige Termzahl zurück."""
        s = 1.0 if side == "links" else 1 / np.sqrt(t)
        a = t if side == "links" else 1 / t
        pref = 1.0 if side == "links" else 1 / np.sqrt(t)
        for n in range(1, 100_000):
            term = 2 * pref * np.exp(-np.pi * n ** 2 * a)
            s += term
            if term < tol * s:
                return s, n
        return s, n

    ts = np.geomspace(0.01, 100, 41)
    left = np.array([theta_terms(t, "links") for t in ts])
    right = np.array([theta_terms(t, "rechts") for t in ts])

    a = 1.0
    exact_sum = np.pi / a / np.tanh(np.pi * a)
    Nn = np.arange(1, 2001)
    left_partial = 1 / a ** 2 + 2 * np.cumsum(1 / (Nn ** 2 + a ** 2))
    Kk = np.arange(0, 8)
    right_partial = np.pi / a * (1 + 2 * np.cumsum(np.r_[0, np.exp(-2 * np.pi * a * Kk[1:])]))

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    axes[0].loglog(ts, left[:, 0], "o", ms=4, label="links: Σ e^(−πn²t)")
    axes[0].loglog(ts, right[:, 0], "-", label="rechts: t^(−½) Σ e^(−πk²/t)")
    axes[0].set_xlabel("t")
    axes[0].set_ylabel("θ(t)")
    axes[0].set_title("Jacobis Theta-Identität", fontsize=10)
    axes[0].legend(fontsize=8)
    axes[1].loglog(ts, left[:, 1], "o-", ms=3, label="Terme links")
    axes[1].loglog(ts, right[:, 1], "s-", ms=3, label="Terme rechts")
    axes[1].set_xlabel("t")
    axes[1].set_ylabel("nötige Terme für 15 Stellen")
    axes[1].set_title("Wo eine Seite langsam ist, ist die andere schnell", fontsize=10)
    axes[1].legend(fontsize=8)
    axes[2].semilogy(Nn, np.abs(left_partial - exact_sum), label="Σ 1/(n² + 1) direkt, bis |n| ≤ N")
    axes[2].semilogy(Kk, np.maximum(np.abs(right_partial - exact_sum), 1e-17), "s-", label="Poisson-Seite (π/a) Σ e^(−2πa|k|), bis |k| ≤ K")
    axes[2].set_xscale("symlog", linthresh=10)
    axes[2].set_xlabel("Zahl der Terme N bzw. K")
    axes[2].set_ylabel("Fehler gegen (π/a)·coth(πa)")
    axes[2].set_title("Langsame Summe, schnelle Poisson-Seite", fontsize=10)
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    for t in (0.01, 1.0, 100.0):
        i = np.argmin(np.abs(ts - t))
        print(f"t = {ts[i]:6.2f}: links {left[i, 0]:.15f} ({left[i, 1]:.0f} Terme), rechts {right[i, 0]:.15f} ({right[i, 1]:.0f} Terme)")
    print(f"Σ_n 1/(n² + 1): exakt π·coth(π) = {exact_sum:.12f}; direkt mit |n| ≤ 2000: Fehler {abs(left_partial[-1] - exact_sum):.1e}; "
          f"Poisson-Seite mit |k| ≤ 7: Fehler {abs(right_partial[-1] - exact_sum):.1e}")


def dft_fft():
    """24. Diskrete Fourier-Transformation und FFT (Zellen 27 von fourieranalysis.ipynb)."""
    global F16, M, _, axes, best, cands, counts, dft_matrix, ev, fft_radix2, fig, fun
    global im, lab, labels, m, mk, name, rng, sizes, t0, th, times, v
    global z
    def fft_radix2(x):
        """Cooley-Tukey-FFT für Längen 2^m: zerlegt in gerade und ungerade Indizes und setzt zwei halbe DFTs zusammen."""
        n = len(x)
        if n == 1:
            return x.astype(complex)
        even, odd = fft_radix2(x[0::2]), fft_radix2(x[1::2])
        twiddle = np.exp(-2j * np.pi * np.arange(n // 2) / n) * odd
        return np.concatenate([even + twiddle, even - twiddle])

    def dft_matrix(n):
        j = np.arange(n)
        return np.exp(-2j * np.pi * np.outer(j, j) / n)

    rng = np.random.default_rng(8)
    F16 = dft_matrix(16) / 4
    ev = np.linalg.eigvals(F16)
    labels = {1: "1", -1: "−1", -1j: "−i", 1j: "i"}
    counts = {lab: int(np.sum(np.abs(ev - z) < 1e-8)) for z, lab in labels.items()}

    sizes = 2 ** np.arange(4, 15)
    times = {"Matrix · Vektor": [], "eigene FFT (Python)": [], "np.fft.fft": []}
    for m in sizes:
        v = rng.normal(size=m) + 1j * rng.normal(size=m)
        cands = [("np.fft.fft", lambda: np.fft.fft(v)), ("eigene FFT (Python)", lambda: fft_radix2(v))]
        if m <= 2048:
            M = dft_matrix(m)
            cands.append(("Matrix · Vektor", lambda: M @ v))
        for name, fun in cands:
            best = np.inf
            for _ in range(3):
                t0 = time.perf_counter(); fun(); best = min(best, time.perf_counter() - t0)
            times[name].append(best)

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    im = axes[0].imshow(dft_matrix(32).real, cmap="RdBu", vmin=-1, vmax=1)
    axes[0].set_title("Realteil der DFT-Matrix, N = 32: cos(2πjk/N)", fontsize=10)
    axes[0].set_xlabel("Spalte k")
    axes[0].set_ylabel("Zeile j")
    plt.colorbar(im, ax=axes[0], fraction=0.046)
    th = np.linspace(0, 2 * np.pi, 200)
    axes[1].plot(np.cos(th), np.sin(th), color="grey", lw=0.5)
    axes[1].plot(ev.real, ev.imag, "o", ms=8)
    for z, lab in labels.items():
        axes[1].annotate(f"{lab}: {counts[lab]}×", (complex(z).real, complex(z).imag), textcoords="offset points", xytext=(8, 8), fontsize=9)
    axes[1].set_aspect("equal")
    axes[1].set_xlim(-1.5, 1.5); axes[1].set_ylim(-1.5, 1.5)
    axes[1].set_xlabel("Realteil")
    axes[1].set_ylabel("Imaginärteil")
    axes[1].set_title("Eigenwerte der unitären DFT, N = 16", fontsize=10)
    for name, mk in zip(times, ["o-", "s-", "^-"]):
        axes[2].loglog(sizes[:len(times[name])], times[name], mk, ms=4, label=name)
    axes[2].loglog(sizes, 2e-9 * sizes ** 2.0, "k:", lw=1, label="∝ N²")
    axes[2].loglog(sizes, 3e-9 * sizes * np.log2(sizes), "k--", lw=1, label="∝ N log N")
    axes[2].set_xlabel("Länge N")
    axes[2].set_ylabel("Rechenzeit [s]")
    axes[2].set_title("Matrix-Vektor gegen FFT", fontsize=10)
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    v = rng.normal(size=1024)
    print(f"Unitär: ‖F F* − I‖ = {np.linalg.norm(F16 @ F16.conj().T - np.eye(16)):.1e};  F⁴ = I: {np.allclose(np.linalg.matrix_power(F16, 4), np.eye(16))};  "
          f"F² kehrt die Indizes um (j → −j mod N): {np.allclose(np.linalg.matrix_power(F16, 2), np.eye(16)[(-np.arange(16)) % 16])}")
    print(f"Vielfachheiten der Eigenwerte für N = 16: {counts}")
    print(f"Eigene FFT gegen np.fft.fft (N = 1024): größter Unterschied {np.max(np.abs(fft_radix2(v) - np.fft.fft(v))):.1e}")
    print(f"Operationen bei N = 2^14: N² = {16384 ** 2:.2e}, N·log₂N = {16384 * 14:.2e}; Zeit eigene FFT {times['eigene FFT (Python)'][-1] * 1e3:.1f} ms, np.fft {times['np.fft.fft'][-1] * 1e3:.3f} ms")


def sampling():
    """25. Abtasttheorem und Aliasing (Zellen 30 von fourieranalysis.ipynb)."""
    global apparent_frequency, axes, band_limited, c, fig, folded, freqs, fs, kf, r, recon, seen
    global sinc_reconstruct, tc, te, tn
    fs = 10.0
    tc = np.linspace(0, 1, 2001)
    tn = np.arange(0, 1.0001, 1 / fs)

    def apparent_frequency(f, fs, T=20.0):
        """Frequenz des stärksten FFT-Gipfels eines mit fs abgetasteten Sinus der Frequenz f."""
        tt = np.arange(0, T, 1 / fs)
        spec = np.abs(np.fft.rfft(np.sin(2 * np.pi * f * tt + 0.3) * np.hanning(len(tt))))
        return np.fft.rfftfreq(len(tt), 1 / fs)[np.argmax(spec)]

    freqs = np.linspace(0.25, 29.75, 119)
    seen = [apparent_frequency(f, fs) for f in freqs]
    folded = np.abs(freqs - fs * np.round(freqs / fs))

    def band_limited(t):
        return np.sin(2 * np.pi * 1.3 * t) + 0.5 * np.cos(2 * np.pi * 3.7 * t + 1) + 0.3 * np.sin(2 * np.pi * 4.6 * t)

    def sinc_reconstruct(fs, t_eval, T=200.0):
        tn = np.arange(-T, T, 1 / fs)
        return np.sinc(fs * t_eval[:, None] - fs * tn[None, :]) @ band_limited(tn)

    te = np.linspace(-2, 2, 801)
    recon = {r: sinc_reconstruct(r, te) for r in (20.0, 10.0, 6.0)}

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    axes[0].plot(tc, np.sin(2 * np.pi * 7 * tc), lw=1, label="Sinus mit 7 Hz")
    axes[0].plot(tc, -np.sin(2 * np.pi * 3 * tc), "--", lw=1.5, label="Alias: Sinus mit 3 Hz (Vorzeichen gedreht)")
    axes[0].plot(tn, np.sin(2 * np.pi * 7 * tn), "ko", ms=6, label=f"Abtastwerte, f_s = {fs:.0f} Hz")
    axes[0].set_xlabel("Zeit t [s]")
    axes[0].set_title("7 Hz und 3 Hz haben dieselben Abtastwerte", fontsize=10)
    axes[0].legend(fontsize=7, loc="lower left")
    axes[1].plot(freqs, seen, "o", ms=3, label="Gipfel im FFT-Spektrum")
    axes[1].plot(freqs, folded, "k-", lw=1, label="|f − f_s · round(f / f_s)|")
    for kf in range(1, 4):
        axes[1].axvline(kf * fs / 2, color="grey", ls=":", lw=0.8)
    axes[1].set_xlabel("wahre Frequenz f [Hz]")
    axes[1].set_ylabel("gesehene Frequenz [Hz]")
    axes[1].set_title("Spiegelung an der Nyquist-Frequenz f_s/2 = 5 Hz", fontsize=10)
    axes[1].legend(fontsize=8)
    axes[2].plot(te, band_limited(te), "k-", lw=2, label="Signal (höchste Frequenz 4.6 Hz)")
    for r, c in zip((10.0, 6.0), ["tab:green", "tab:red"]):
        axes[2].plot(te, recon[r], c=c, lw=1, label=f"sinc-Rekonstruktion aus f_s = {r:.0f} Hz")
    axes[2].set_xlabel("Zeit t [s]")
    axes[2].set_title("Whittaker-Shannon: über 2 · 4.6 Hz exakt, darunter falsch", fontsize=10)
    axes[2].legend(fontsize=7)
    plt.tight_layout()
    plt.show()

    print(f"Gesehene Frequenzen bei f_s = 10 Hz: 7 Hz → {apparent_frequency(7, fs):.2f} Hz, 12 Hz → {apparent_frequency(12, fs):.2f} Hz, 18.5 Hz → {apparent_frequency(18.5, fs):.2f} Hz")
    for r in (20.0, 10.0, 6.0):
        print(f"f_s = {r:4.0f} Hz ({'über' if r > 9.2 else 'unter'} 2 · 4.6 = 9.2 Hz): größter Rekonstruktionsfehler auf [−2, 2] = {np.max(np.abs(recon[r] - band_limited(te))):.1e}")


def leakage():
    """26. Leckeffekt und Fensterfunktionen (Zellen 33 von fourieranalysis.ipynb)."""
    global S, S0, W, W_db, axes, bins, c, f, f0, fig, first_null, fs
    global i61, n, name, pad, psl, scallop, sel, spectrum_db, stats_w, t, w, width
    global windows, x
    fs, n = 1000, 1000
    t = np.arange(n) / fs
    x = np.sin(2 * np.pi * 50.3 * t) + 1e-3 * np.sin(2 * np.pi * 61 * t)              # starker Ton neben einem um 60 dB schwächeren
    windows = {"Rechteck": np.ones(n), "Hann": signal.windows.hann(n, sym=False), "Blackman-Harris": signal.windows.blackmanharris(n, sym=False)}
    pad = 16 * n

    def spectrum_db(x, w):
        S = np.abs(np.fft.rfft(x * w, pad)) / (w.sum() / 2)               # so normiert, dass ein Ton der Amplitude 1 bei 0 dB liegt
        return np.fft.rfftfreq(pad, 1 / fs), 20 * np.log10(np.maximum(S, 1e-12))

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    for (name, w), c in zip(windows.items(), ["tab:blue", "tab:orange", "tab:green"]):
        f, S = spectrum_db(x, w)
        sel = (f > 30) & (f < 80)
        axes[0].plot(f[sel], S[sel], c=c, lw=1, label=name)
    axes[0].axvline(61, color="grey", ls=":", lw=1)
    axes[0].annotate("schwacher Ton\n61 Hz, −60 dB", (61, -60), xytext=(66, -25), fontsize=8, arrowprops=dict(arrowstyle="->"))
    axes[0].set_ylim(-140, 5)
    axes[0].set_xlabel("Frequenz [Hz]")
    axes[0].set_ylabel("Pegel [dB]")
    axes[0].set_title("Starker Ton bei 50.3 Hz, schwacher bei 61 Hz", fontsize=10)
    axes[0].legend(fontsize=8)
    for (name, w), c in zip(windows.items(), ["tab:blue", "tab:orange", "tab:green"]):
        axes[1].plot(t, w, c=c, label=name)
    axes[1].set_xlabel("Zeit [s]")
    axes[1].set_ylabel("Gewicht w(t)")
    axes[1].set_title("Die drei Fenster", fontsize=10)
    axes[1].legend(fontsize=8)
    stats_w = {}
    for (name, w), c in zip(windows.items(), ["tab:blue", "tab:orange", "tab:green"]):
        W = np.abs(np.fft.fft(w, 64 * n))
        W_db = 20 * np.log10(np.maximum(W / W[0], 1e-12))
        bins = np.arange(64 * n) / 64
        sel = bins <= 20
        axes[2].plot(bins[sel], W_db[sel], c=c, lw=1, label=name)
        first_null = np.argmax(np.diff(W_db[: 64 * 20]) > 0)          # erstes Minimum = Ende der Hauptkeule
        stats_w[name] = (W_db[first_null:64 * 20].max(), 2 * bins[first_null], 20 * np.log10(W[32] / W[0]))
    axes[2].set_ylim(-140, 5)
    axes[2].set_xlabel("Abstand vom Ton [Frequenzbins = 1/T]")
    axes[2].set_ylabel("Pegel [dB]")
    axes[2].set_title("Spektrum der Fenster: Hauptkeule und Nebenkeulen", fontsize=10)
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    for name, w in windows.items():
        f, S = spectrum_db(x, w)
        f0, S0 = spectrum_db(np.sin(2 * np.pi * 50.3 * t), w)
        i61 = np.argmin(np.abs(f - 61))
        psl, width, scallop = stats_w[name]
        print(f"{name:15s}: höchste Nebenkeule {psl:6.1f} dB, Hauptkeule {width:.1f} Bins breit, Verlust bei halbem Bin {scallop:5.2f} dB; "
              f"bei 61 Hz: {S[i61]:6.1f} dB mit, {S0[i61]:6.1f} dB ohne schwachen Ton")


def spectrogram():
    """27. Zeit-Frequenz-Analyse: das Spektrogramm (Zellen 36 von fourieranalysis.ipynb)."""
    global S, T, above, ax, axes, band, c, cut, dip, e, f, fig
    global fs, i, nper, specs, stft, t, tt, x
    fs, T = 4000, 2.0
    t = np.arange(int(fs * T)) / fs
    x = (np.sin(2 * np.pi * 200 * t) + np.sin(2 * np.pi * 215 * t)                      # zwei nahe Töne
         + 0.7 * np.sin(2 * np.pi * (400 * t + 125 * t ** 2))                           # Chirp von 400 auf 900 Hz
         + 5 * np.exp(-((t - 1.0) / 0.0005) ** 2))                                      # kurzer Klick bei t = 1 s
    specs = {}
    for nper in (128, 2048):
        stft = signal.ShortTimeFFT(signal.windows.hann(nper), hop=nper // 8, fs=fs, scale_to="psd")
        specs[nper] = (stft.f, stft.t(len(x)), stft.spectrogram(x))

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    for ax, nper in zip(axes[:2], (128, 2048)):
        f, tt, S = specs[nper]
        ax.pcolormesh(tt, f, 10 * np.log10(S + 1e-12), shading="auto", vmin=-80, vmax=-10, cmap="magma")
        ax.set_ylim(0, 1100)
        ax.set_xlim(0.3, T - 0.3)                                     # an den Rändern ragt das lange Fenster über das Signal hinaus
        ax.set_xlabel("Zeit [s]")
        ax.set_ylabel("Frequenz [Hz]")
        ax.set_title(f"Fenster {nper / fs * 1000:.0f} ms: Δt ≈ {nper / fs * 1000:.0f} ms, Δf ≈ {fs / nper:.1f} Hz", fontsize=10)
    for nper, c in zip((128, 2048), ["tab:blue", "tab:orange"]):
        f, tt, S = specs[nper]
        i = np.argmin(np.abs(tt - 0.5))
        axes[2].plot(f, 10 * np.log10(S[:, i] / S[:, i].max()), c=c, label=f"Fenster {nper / fs * 1000:.0f} ms")
    axes[2].set_xlim(150, 260)
    axes[2].set_ylim(-60, 3)
    axes[2].set_xlabel("Frequenz [Hz]")
    axes[2].set_ylabel("Pegel relativ zum Maximum [dB]")
    axes[2].set_title("Schnitt bei t = 0.5 s: 200 und 215 Hz getrennt?", fontsize=10)
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    for nper in (128, 2048):
        f, tt, S = specs[nper]
        band = (f > 1000) & (f < 1400)
        e = S[band].sum(axis=0)
        above = tt[e > e.max() / 2]
        i = np.argmin(np.abs(tt - 0.5))
        cut = S[(f >= 195) & (f <= 220), i]
        dip = 10 * np.log10(S[np.argmin(np.abs(f - 207.5)), i] / cut.max())
        print(f"Fenster {nper:4d} Punkte ({nper / fs * 1000:3.0f} ms): Frequenzauflösung f_s/N = {fs / nper:5.1f} Hz; Klick oberhalb halber Höhe {(above.max() - above.min()) * 1000:5.1f} ms lang; "
              f"Einbruch zwischen 200 und 215 Hz: {dip:6.1f} dB")


def wavelets():
    """28. Wavelets gegen Fourier: wer braucht weniger Koeffizienten? (Zellen 39 von fourieranalysis.ipynb)."""
    global axes, bases, basis, blocks, c, fig, fracs, fwd, haar_dwt, haar_idwt, inv, jumps
    global keep_largest, ls, mag, n, rel_error, s, smooth, sname, u
    def haar_dwt(x):
        """Orthonormale Haar-Wavelet-Transformation über alle Stufen (Länge 2^m). Gibt die Koeffizienten als ein Vektor zurück."""
        a, out = x.astype(float), []
        while len(a) > 1:
            out.append((a[0::2] - a[1::2]) / np.sqrt(2))                  # Details (Wavelet-Koeffizienten) dieser Stufe
            a = (a[0::2] + a[1::2]) / np.sqrt(2)                           # Mittelwerte (Skalierungskoeffizienten)
        return np.concatenate([a] + out[::-1])

    def haar_idwt(c):
        a, pos = c[:1], 1
        while pos < len(c):
            d = c[pos:2 * pos]
            nxt = np.empty(2 * pos)
            nxt[0::2], nxt[1::2] = (a + d) / np.sqrt(2), (a - d) / np.sqrt(2)
            a, pos = nxt, 2 * pos
        return a

    def keep_largest(c, frac):
        m = max(1, int(round(frac * len(c))))
        out = np.zeros_like(c)
        idx = np.argsort(np.abs(c))[-m:]
        out[idx] = c[idx]
        return out

    n = 1024
    u = np.arange(n) / n
    jumps = [(0.1, 2.0), (0.13, -3.0), (0.32, 1.5), (0.45, 2.5), (0.6, -2.0), (0.65, 3.0), (0.78, -1.5), (0.82, 1.0)]
    blocks = sum(h * (u >= p) for p, h in jumps)
    smooth = np.exp(-((u - 0.3) / 0.08) ** 2) + 0.6 * np.exp(-((u - 0.7) / 0.12) ** 2) + 0.3 * np.cos(4 * np.pi * u)
    bases = {"DCT (Fourier, wie JPEG)": (lambda s: sfft.dct(s, norm="ortho"), lambda c: sfft.idct(c, norm="ortho")),
             "Haar-Wavelets": (haar_dwt, haar_idwt)}
    fracs = np.geomspace(0.005, 0.3, 20)

    def rel_error(s, basis, frac):
        fwd, inv = bases[basis]
        return np.linalg.norm(inv(keep_largest(fwd(s), frac)) - s) / np.linalg.norm(s)

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    axes[0].plot(u, blocks, "k-", lw=2, label="Blocksignal")
    for basis, c in zip(bases, ["tab:blue", "tab:red"]):
        fwd, inv = bases[basis]
        axes[0].plot(u, inv(keep_largest(fwd(blocks), 0.06)), c=c, lw=1, label=f"{basis}, 6 % der Koeffizienten")
    axes[0].set_xlabel("x")
    axes[0].set_title("Sprünge: Haar trifft, DCT schwingt", fontsize=10)
    axes[0].legend(fontsize=7)
    for (sname, s), ls in zip([("Blöcke", blocks), ("glatt", smooth)], ["-", "--"]):
        for basis, c in zip(bases, ["tab:blue", "tab:red"]):
            mag = np.sort(np.abs(bases[basis][0](s)))[::-1]
            axes[1].loglog(np.arange(1, n + 1), mag / mag[0], c=c, ls=ls, lw=1.2, label=f"{sname}, {basis}")
    axes[1].set_ylim(1e-8, 2)
    axes[1].set_xlabel("Rang (der größte zuerst)")
    axes[1].set_ylabel("|Koeffizient| / größter")
    axes[1].set_title("Sortierte Koeffizienten: wie schnell fallen sie?", fontsize=10)
    axes[1].legend(fontsize=7)
    for (sname, s), ls in zip([("Blöcke", blocks), ("glatt", smooth)], ["-", "--"]):
        for basis, c in zip(bases, ["tab:blue", "tab:red"]):
            axes[2].loglog(fracs, [rel_error(s, basis, fr) for fr in fracs], c=c, ls=ls, marker="o", ms=3, label=f"{sname}, {basis}")
    axes[2].set_xlabel("Anteil der behaltenen Koeffizienten")
    axes[2].set_ylabel("relativer Fehler")
    axes[2].set_title("Kompression: Fehler gegen Anteil", fontsize=10)
    axes[2].legend(fontsize=7)
    plt.tight_layout()
    plt.show()

    print(f"Haar ist orthonormal: Rücktransformation exakt bis {np.max(np.abs(haar_idwt(haar_dwt(blocks)) - blocks)):.1e}, Energie erhalten {np.allclose(np.sum(haar_dwt(blocks) ** 2), np.sum(blocks ** 2))}")
    for sname, s in [("Blöcke", blocks), ("glatt", smooth)]:
        print(f"{sname:6s}: relativer Fehler mit 6 % (3 %) der Koeffizienten: DCT {rel_error(s, 'DCT (Fourier, wie JPEG)', 0.06):.2e} ({rel_error(s, 'DCT (Fourier, wie JPEG)', 0.03):.2e}), "
              f"Haar {rel_error(s, 'Haar-Wavelets', 0.06):.2e} ({rel_error(s, 'Haar-Wavelets', 0.03):.2e}); "
              f"Haar-Koeffizienten ≠ 0: {np.sum(np.abs(haar_dwt(s)) > 1e-10)} von {n}")


def heat_equation():
    """29. Die Wärmeleitungsgleichung: Fouriers ursprüngliches Problem (Zellen 42 von fourieranalysis.ipynb)."""
    global D, _, amp, axes, c, c0, ck, dt, dx, factor, fig, heat_kernel_images
    global heat_spectral, k, kk, n, sel, times, ts, tt, u, u0, x
    n, D = 256, 1.0
    x = 2 * np.pi * np.arange(n) / n
    u0 = (np.abs(x - np.pi) < 1).astype(float)                        # heißes Stück in der Mitte eines Rings
    k = np.fft.fftfreq(n, 1 / n)
    c0 = np.fft.fft(u0) / n

    def heat_spectral(t):
        return np.real(np.fft.ifft(c0 * np.exp(-D * k ** 2 * t) * n))

    def heat_kernel_images(t, images=20):
        """Lösung als Faltung mit der periodisierten Gauß-Funktion (Summe über Spiegelbilder, Poissonsche Summenformel)."""
        dxg = 2 * np.pi / n
        d = x[:, None] - x[None, :]
        G = sum(np.exp(-(d + 2 * np.pi * m) ** 2 / (4 * D * t)) for m in range(-images, images + 1)) / np.sqrt(4 * np.pi * D * t)
        return G @ u0 * dxg

    times = [0, 0.001, 0.01, 0.05, 0.2, 1.0]
    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    for tt, c in zip(times, plt.cm.plasma(np.linspace(0, 0.85, len(times)))):
        axes[0].plot(x, heat_spectral(tt), c=c, label=f"t = {tt}")
        ck = np.abs(c0 * np.exp(-D * k ** 2 * tt))[: n // 2]
        sel = ck > 1e-16
        axes[1].semilogy(np.arange(n // 2)[sel], ck[sel], ".", c=c, ms=3, label=f"t = {tt}")
    axes[0].set_xlabel("Ort x auf dem Ring")
    axes[0].set_ylabel("Temperatur u(x, t)")
    axes[0].set_title("Wärmeleitung auf einem Ring", fontsize=10)
    axes[0].legend(fontsize=8)
    axes[1].set_xlabel("Frequenz k")
    axes[1].set_ylabel("|c_k(t)|")
    axes[1].set_title("Jede Mode zerfällt wie e^(−Dk²t): hohe zuerst", fontsize=10)
    axes[1].legend(fontsize=8)
    ts = np.linspace(0, 2, 200)
    for kk, c in zip([1, 2, 3, 5], ["tab:blue", "tab:orange", "tab:green", "tab:red"]):
        amp = [np.abs(np.fft.fft(heat_spectral(tt))[kk]) / n for tt in ts]
        axes[2].semilogy(ts, amp, c=c, lw=2, alpha=0.6, label=f"k = {kk} (gemessen)")
        axes[2].semilogy(ts, np.abs(c0[kk]) * np.exp(-D * kk ** 2 * ts), "k--", lw=0.8)
    axes[2].set_ylim(1e-8, 1)
    axes[2].set_xlabel("Zeit t")
    axes[2].set_ylabel("|c_k(t)|")
    axes[2].set_title("Zerfallsraten Dk² (gestrichelt: Theorie)", fontsize=10)
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    for tt in (0.01, 0.2):
        print(f"t = {tt}: Fourier-Lösung gegen Faltung mit dem periodisierten Gauß-Kern: größter Unterschied {np.max(np.abs(heat_spectral(tt) - heat_kernel_images(tt))):.1e}")
    print(f"Mittelwert bleibt erhalten: {u0.mean():.6f} → {heat_spectral(1.0).mean():.6f};  Abweichung vom Mittelwert bei t = 2 und 3: "
          f"{np.max(np.abs(heat_spectral(2.0) - u0.mean())):.5f}, {np.max(np.abs(heat_spectral(3.0) - u0.mean())):.5f} (Verhältnis {np.max(np.abs(heat_spectral(3.0) - u0.mean())) / np.max(np.abs(heat_spectral(2.0) - u0.mean())):.4f}, Theorie e^−1 = {np.exp(-1):.4f})")
    dx = 2 * np.pi / n
    for factor in (0.45, 0.55):
        u, dt = u0.copy(), factor * dx ** 2 / D
        for _ in range(400):
            u = u + D * dt / dx ** 2 * (np.roll(u, 1) - 2 * u + np.roll(u, -1))
        print(f"Explizites Differenzenverfahren mit dt = {factor} · dx²/D, 400 Schritte: max |u| = {np.max(np.abs(u)):.3g} ({'stabil' if np.max(np.abs(u)) <= 1 else 'instabil'})")


def diffraction():
    """30. Beugung: Fourier-Optik in zwei Dimensionen (Zellen 45 von fourieranalysis.ipynb)."""
    global I, I_circ, I_slit, L, R, X, Y, airy, ap, axes, circle, counts
    global cut, d, ext_k, ext_x, far_field, fig, first_zero, inner, mins, n, name, radial
    global rbins, rc, row, sel, slits, sums, theory_slit, w, which, xi, xs
    n, L = 1024, 51.2
    xs = (np.arange(n) - n // 2 + 0.5) * L / n                       # Pixelmitten bei ±0.025, ±0.075, …: Spaltränder fallen zwischen Pixel
    X, Y = np.meshgrid(xs, xs)
    circle = (X ** 2 + Y ** 2 <= 1.0).astype(float)                   # kreisförmige Öffnung, Radius a = 1 (Durchmesser D = 2)
    w, d = 0.2, 1.0
    slits = ((np.abs(np.abs(X) - d / 2) < w / 2) & (np.abs(Y) < 4)).astype(float)   # Doppelspalt: Breite w, Abstand d
    xi = np.fft.fftshift(np.fft.fftfreq(n, L / n))

    def far_field(aperture):
        """Intensität im Fernfeld = |2D-Fourier-Transformierte der Öffnung|², auf das Maximum normiert."""
        I = np.abs(np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(aperture)))) ** 2
        return I / I.max()

    I_circ, I_slit = far_field(circle), far_field(slits)
    R = np.hypot(*np.meshgrid(xi, xi))
    rbins = np.arange(0, 2.0001, 2 * (xi[1] - xi[0]))
    which = np.digitize(R.ravel(), rbins)
    sums = np.bincount(which, weights=I_circ.ravel(), minlength=len(rbins) + 1)[1:len(rbins)]
    counts = np.bincount(which, minlength=len(rbins) + 1)[1:len(rbins)]
    rc = 0.5 * (rbins[1:] + rbins[:-1])[counts > 0]
    radial = sums[counts > 0] / counts[counts > 0]                  # Mittel über Ringe der Breite zweier Frequenzschritte
    with np.errstate(invalid="ignore", divide="ignore"):
        airy = np.where(rc > 0, (2 * special.j1(2 * np.pi * rc) / (2 * np.pi * rc)) ** 2, 1.0)
    cut = I_slit[n // 2]
    theory_slit = np.cos(np.pi * d * xi) ** 2 * np.sinc(w * xi) ** 2

    fig, axes = plt.subplots(2, 3, figsize=(17, 8.6))
    ext_x, ext_k = [xs[0], xs[-1], xs[0], xs[-1]], [xi[0], xi[-1], xi[0], xi[-1]]
    for row, (ap, I, name) in enumerate([(circle, I_circ, "Kreisöffnung, Radius 1"), (slits, I_slit, f"Doppelspalt, Breite {w}, Abstand {d}")]):
        axes[row, 0].imshow(ap, extent=ext_x, cmap="gray", origin="lower")
        axes[row, 0].set_xlim(-3, 3)
        axes[row, 0].set_ylim(-3, 3) if row == 0 else axes[row, 0].set_ylim(-5, 5)
        axes[row, 0].set_title(f"Öffnung: {name}", fontsize=10)
        axes[row, 0].set_xlabel("x"); axes[row, 0].set_ylabel("y")
        axes[row, 1].imshow(np.log10(I + 1e-8), extent=ext_k, cmap="inferno", origin="lower", vmin=-5, vmax=0)
        axes[row, 1].set_xlim(-3, 3); axes[row, 1].set_ylim(-3, 3)
        axes[row, 1].set_title("Beugungsbild log₁₀ |FT|²", fontsize=10)
        axes[row, 1].set_xlabel("Raumfrequenz ξ_x"); axes[row, 1].set_ylabel("Raumfrequenz ξ_y")
    axes[0, 2].semilogy(rc, radial, "o", ms=3, label="gemessen (Mittel über Ringe)")
    axes[0, 2].semilogy(rc, airy, "k-", lw=1, label="Airy: [2J₁(2πρ)/(2πρ)]²")
    axes[0, 2].axvline(0.6098, color="tab:red", ls="--", lw=1, label="erster dunkler Ring ρ = 1.22/D")
    axes[0, 2].set_ylim(1e-6, 1.5)
    axes[0, 2].set_xlabel("radiale Raumfrequenz ρ")
    axes[0, 2].set_ylabel("Intensität")
    axes[0, 2].set_title("Kreis: Airy-Scheibchen", fontsize=10)
    axes[0, 2].legend(fontsize=8)
    sel = np.abs(xi) <= 6
    axes[1, 2].plot(xi[sel], cut[sel], lw=1, label="gemessen (Schnitt ξ_y = 0)")
    axes[1, 2].plot(xi[sel], theory_slit[sel], "k--", lw=1, label="cos²(πdξ) · sinc²(wξ)")
    axes[1, 2].plot(xi[sel], np.sinc(w * xi[sel]) ** 2, ":", c="grey", label="Hülle sinc²(wξ): ein Spalt")
    axes[1, 2].set_xlabel("Raumfrequenz ξ_x")
    axes[1, 2].set_ylabel("Intensität")
    axes[1, 2].set_title("Doppelspalt: Streifen im Abstand 1/d", fontsize=10)
    axes[1, 2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    inner = (rc > 0.3) & (rc < 0.8)
    first_zero = rc[inner][np.argmin(radial[inner])]
    print(f"Erster dunkler Ring: gemessen bei ρ = {first_zero:.3f} (Raster {rbins[1] - rbins[0]:.3f}), Theorie 3.8317/(2πa) = {3.8317 / (2 * np.pi):.4f} = 1.22/D")
    print(f"Anteil der Energie im zentralen Scheibchen: {I_circ[R < 0.6098].sum() / I_circ.sum():.3f} (Theorie 0.838)")
    mins = xi[sel][1:-1][(cut[sel][1:-1] < cut[sel][:-2]) & (cut[sel][1:-1] < cut[sel][2:])]
    print(f"Doppelspalt: Minima bei ξ = {np.round(mins[np.abs(mins) < 3], 3)} (Theorie ±0.5, ±1.5, ±2.5: Abstand 1/d = {1 / d})")


def finite_groups():
    """31. Harmonische Analysis auf endlichen Gruppen: Hyperwürfel und Periodenfindung (Zellen 48 von fourieranalysis.ipynb)."""
    global H, M, Nq, P, axes, base, bits, boolean, f, fhat, fig, fr
    global fx, h, i, infl, j, level, name, nbits, near, pm, r, rng
    global val, walsh_hadamard, wdt, weights, wv, xs_int, y
    def walsh_hadamard(f):
        """Schnelle Walsh-Hadamard-Transformation: Σ_x f(x) (−1)^{S·x} für alle S, in n · 2^n Schritten."""
        a, h = np.array(f, dtype=float), 1
        while h < len(a):
            a = a.reshape(-1, 2 * h)
            left, right = a[:, :h].copy(), a[:, h:].copy()
            a[:, :h], a[:, h:] = left + right, left - right
            a, h = a.reshape(-1), 2 * h
        return a

    rng = np.random.default_rng(15)
    nbits = 9
    xs_int = np.arange(2 ** nbits)
    bits = (xs_int[:, None] >> np.arange(nbits)) & 1
    pm = 1 - 2 * bits                                                 # Bits als ±1
    boolean = {
        "Diktator x₁": pm[:, 0],
        "Mehrheit von 9": np.sign(pm.sum(axis=1)),
        "Parität x₁⋯x₉": np.prod(pm, axis=1),
        "zufällige Funktion": rng.choice([-1, 1], size=2 ** nbits),
    }
    level = bits.sum(axis=1)                                          # |S| für den Index S
    weights = {}
    for name, f in boolean.items():
        fhat = walsh_hadamard(f) / 2 ** nbits
        weights[name] = np.array([np.sum(fhat[level == j] ** 2) for j in range(nbits + 1)])

    Nq, M, base = 512, 21, 2
    fx = np.array([pow(base, int(v), M) for v in range(Nq)])
    P = np.zeros(Nq)
    for val in np.unique(fx):
        P += np.abs(np.fft.fft((fx == val).astype(float))) ** 2
    P /= Nq ** 2
    r = 6

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    H = np.array([walsh_hadamard(row) for row in np.eye(16)])
    axes[0].imshow(H, cmap="gray")
    axes[0].set_title("Charaktere von ℤ₂⁴: Walsh-Hadamard-Matrix (16 × 16)", fontsize=10)
    axes[0].set_xlabel("x")
    axes[0].set_ylabel("S")
    wdt = 0.2
    for i, (name, wv) in enumerate(weights.items()):
        axes[1].bar(np.arange(nbits + 1) + (i - 1.5) * wdt, wv, width=wdt, label=name)
    axes[1].set_xlabel("Stufe |S| (Zahl der Variablen im Charakter)")
    axes[1].set_ylabel("Fourier-Gewicht Σ_{|S|=k} f̂(S)²")
    axes[1].set_title("Boolesche Funktionen auf {−1, 1}⁹", fontsize=10)
    axes[1].legend(fontsize=8)
    axes[2].plot(np.arange(Nq), P, lw=0.8)
    for j in range(r):
        axes[2].axvline(j * Nq / r, color="tab:red", ls=":", lw=0.8)
    axes[2].set_xlabel("Messwert y")
    axes[2].set_ylabel("Wahrscheinlichkeit")
    axes[2].set_title(f"Fourier-Abtastung von 2^x mod {M} auf ℤ_{Nq}: Gipfel bei j·{Nq}/{r}", fontsize=10)
    plt.tight_layout()
    plt.show()

    for name, wv in weights.items():
        infl = np.sum(np.arange(nbits + 1) * wv)
        print(f"{name:18s}: Σ f̂(S)² = {wv.sum():.3f};  Gewicht auf Stufe 1: {wv[1]:.3f};  Gesamteinfluss Σ|S| f̂(S)² = {infl:.3f}")
    print(f"Mehrheit: Stufe-1-Gewicht exakt 9·(C(8,4)/2⁸)² = {9 * (special.comb(8, 4) / 2 ** 8) ** 2:.3f}, für n → ∞ gegen 2/π = {2 / np.pi:.3f}")
    near = np.zeros(Nq, bool)
    for j in range(r):
        near[[int(np.floor(j * Nq / r)) % Nq, int(np.ceil(j * Nq / r)) % Nq]] = True
    print(f"Periode von 2^x mod {M}: {r}; Wahrscheinlichkeit, einen der beiden nächsten Werte zu j·{Nq}/{r} zu messen: {P[near].sum():.3f}")
    h = pow(base, r // 2, M)
    print(f"Aus r = {r}: {base}^{r // 2} mod {M} = {h};  ggT({h} − 1, {M}) = {gcd(h - 1, M)},  ggT({h} + 1, {M}) = {gcd(h + 1, M)}  →  {M} = {gcd(h + 1, M)} · {gcd(h - 1, M)}")
    for y in (85, 171, 427):
        fr = Fraction(y, Nq).limit_denominator(M)
        print(f"Messwert y = {y}: y/{Nq} ≈ {fr} → Nenner {fr.denominator}" + ("  (Teiler von r; ein zweiter Messwert gibt r = 6)" if fr.denominator != r else "  (= Periode)"))
