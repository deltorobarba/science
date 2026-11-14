"""Funktionalanalysis und Operatortheorie: unendliche Dimensionen, schwache Konvergenz, Hahn-Banach, Riesz und Sobolev, kompakte und unbeschränkte Operatoren, Spektrum, Weyl-Gesetz, Stone, Stone-von Neumann, Koopman und Operator-Lernen.

Für analysis.ipynb aus functionalanalysis.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, infinite_dimensions, weak_convergence, hahn_banach, riesz_sobolev, bounded_unbounded, compact_operators, spectrum_types, finite_sections, spectral_measure, unbounded_operators, weyl_law, stone_theorem, stone_von_neumann, koopman, operator_learning.
"""
import itertools, time
from math import factorial
import numpy as np
import matplotlib.pyplot as plt
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy.linalg import expm, eigh, eigh_tridiagonal, toeplitz, svdvals
from scipy.integrate import solve_ivp
from scipy.special import jn_zeros


def load():
    """32. Daten (Zellen 4 von functionalanalysis.ipynb)."""
    global grid01, integral_operator, l2, opnorm
    # Alles hier (numpy, scipy, matplotlib) ist in Colab vorinstalliert

    def grid01(n):
        """Mittelpunkte und Gewichte der Mittelpunktsregel auf [0, 1]."""
        return (np.arange(n) + 0.5) / n, np.full(n, 1 / n)

    def l2(f, w):
        """L²-Norm einer auf dem Gitter gegebenen Funktion (Quadraturgewichte w)."""
        return np.sqrt(np.sum(w * np.abs(f) ** 2))

    def integral_operator(kernel, n):
        """Nyström-Matrix von (Kf)(x) = ∫₀¹ k(x, y) f(y) dy auf n Mittelpunkten; dazu Gitter und Gewichte."""
        x, w = grid01(n)
        return kernel(x[:, None], x[None, :]) * w[None, :], x, w

    def opnorm(A):
        """Spektralnorm: der größte Singulärwert."""
        return np.linalg.norm(A, 2)

    print("Werkzeuge bereit: Gitter, L²-Norm, Nyström-Matrix, Operatornorm")


def infinite_dimensions():
    """33. Unendlich viele Dimensionen: Kompaktheit und Normen (Zellen 6 von functionalanalysis.ipynb)."""
    global E30, N, Nn, ax, axes, c, d, dist, fig, gram, i, im
    global lab, off, p, phi, pnorm, ps, r, seqx, seqy, wq, xq
    ps = [1, 1.5, 2, 4, np.inf]
    phi = np.linspace(0, 2 * np.pi, 600)
    Nn = np.unique(np.r_[np.logspace(0, 5, 40).astype(int), 10, 1000, 100000])
    pnorm = lambda v, p: np.max(np.abs(v)) if p == np.inf else np.sum(np.abs(v) ** p) ** (1 / p)
    seqx = {p: [pnorm(np.full(N, 1 / N), p) for N in Nn] for p in (1, 2, np.inf)}
    seqy = {p: [pnorm(1 / np.arange(1, N + 1), p) for N in Nn] for p in (1, 2, np.inf)}
    xq, wq = grid01(20000)
    E30 = np.array([np.sqrt(2) * np.sin(n * np.pi * xq) for n in range(1, 31)])
    gram = (E30 * wq) @ E30.T
    dist = np.sqrt(np.maximum(np.diag(gram)[:, None] + np.diag(gram)[None, :] - 2 * gram, 0))

    fig, axes = plt.subplots(1, 3, figsize=(18, 4.8))
    ax = axes[0]
    for p, c in zip(ps, ("C0", "C1", "C2", "C3", "C4")):
        d = np.c_[np.cos(phi), np.sin(phi)]
        r = 1 / np.array([pnorm(v, p) for v in d])
        ax.plot(r * d[:, 0], r * d[:, 1], color=c, label=f"p = {'∞' if p == np.inf else p}")
    ax.set_aspect("equal")
    ax.set_xlabel("x₁"); ax.set_ylabel("x₂")
    ax.set_title("Einheitskugeln ‖x‖_p ≤ 1 in der Ebene", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[1]
    for p, c in zip((1, 2, np.inf), ("C0", "C1", "C2")):
        lab = "∞" if p == np.inf else p
        ax.loglog(Nn, seqx[p], "-", color=c, label=f"x_N = (1/N, …, 1/N): ‖·‖_{lab}")
        ax.loglog(Nn, seqy[p], "--", color=c, label=f"y_N = (1, 1/2, …, 1/N): ‖·‖_{lab}")
    ax.set_xlabel("Zahl der Einträge N")
    ax.set_ylabel("Norm")
    ax.set_title("Dieselbe Folge, drei Normen, drei Antworten", fontsize=10)
    ax.legend(fontsize=7)
    ax = axes[2]
    im = ax.imshow(dist, cmap="viridis", extent=[0.5, 30.5, 30.5, 0.5])
    plt.colorbar(im, ax=ax, label="‖e_m − e_n‖ in L²")
    ax.set_xlabel("n"); ax.set_ylabel("m")
    ax.set_title("Abstände der Orthonormalfolge √2 sin(nπx)", fontsize=10)
    plt.tight_layout()
    plt.show()

    off = dist[~np.eye(30, dtype=bool)]
    print(f"Abstände e_m − e_n (m ≠ n): kleinster {off.min():.6f}, größter {off.max():.6f}, √2 = {np.sqrt(2):.6f};  Normen der e_n: {np.diag(gram).min():.6f} bis {np.diag(gram).max():.6f}")
    for N in (10, 1000, 100000):
        i = np.argmin(np.abs(Nn - N))
        print(f"N = {Nn[i]:6d}: x_N hat ‖·‖₁ = {seqx[1][i]:.4f}, ‖·‖₂ = {seqx[2][i]:.4f}, ‖·‖_∞ = {seqx[np.inf][i]:.5f};  "
              f"y_N hat ‖·‖₁ = {seqy[1][i]:.4f}, ‖·‖₂ = {seqy[2][i]:.4f} (Grenze π/√6 = {np.pi / np.sqrt(6):.4f})")


def weak_convergence():
    """34. Schwache Konvergenz und Vollständigkeit (Zellen 9 von functionalanalysis.ipynb)."""
    global ax, axes, c, cauchy, d_l2, d_sup, fig, fseq, gauss, inner, k, nn
    global norms2, ns2, sq_inner, step, tests, v, w2, win, ws01, x2, xs01, xx
    global yy
    x2 = np.linspace(0, 2 * np.pi, 200001)
    w2 = np.full_like(x2, x2[1] - x2[0]); w2[[0, -1]] /= 2
    tests = {"Rechteck auf [1, 2] (Sprung)": ((x2 >= 1) & (x2 <= 2)).astype(float),
             "Dreieck um 2 (Knick)": np.maximum(0, 1 - np.abs(x2 - 2)),
             "Gauß-Glocke um 2.5 (glatt)": np.exp(-2 * (x2 - 2.5) ** 2)}
    ns2 = np.arange(1, 201)
    inner = {k: np.array([abs(np.sum(w2 * np.sin(n * x2) * g)) for n in ns2]) for k, g in tests.items()}
    norms2 = np.array([np.sqrt(np.sum(w2 * np.sin(n * x2) ** 2)) for n in ns2])
    gauss = tests["Gauß-Glocke um 2.5 (glatt)"]
    sq_inner = {n: np.sum(w2 * np.sin(n * x2) ** 2 * gauss) for n in (1, 5, 20, 100)}
    xs01 = np.linspace(0, 1, 100001); ws01 = np.full_like(xs01, xs01[1] - xs01[0]); ws01[[0, -1]] /= 2
    step = (xs01 > 0.5).astype(float)
    nn = np.unique(np.logspace(0, 4, 30).astype(int))
    fseq = lambda n: 0.5 * (1 + np.tanh(n * (xs01 - 0.5)))
    d_l2 = np.array([l2(fseq(n) - step, ws01) for n in nn])
    d_sup = np.array([np.max(np.abs(fseq(n) - step)) for n in nn])
    cauchy = [l2(fseq(n) - fseq(2 * n), ws01) for n in (10, 100, 1000)]

    fig, axes = plt.subplots(1, 3, figsize=(18, 4.8))
    ax = axes[0]
    for (k, v), c in zip(inner.items(), ("C0", "C1", "C2")):
        ax.loglog(ns2, v + 1e-17, ".", color=c, ms=3, label=f"|⟨sin(nx), g⟩|, g = {k}")
    ax.loglog(ns2, norms2, "k-", label="‖sin(nx)‖ = √π")
    ax.loglog(ns2, 1.0 / ns2, "C0:", lw=1, label="∝ 1/n")
    ax.loglog(ns2, 1.0 / ns2 ** 2, "C1:", lw=1, label="∝ 1/n²")
    ax.set_ylim(1e-12, 5)
    ax.set_xlabel("n"); ax.set_ylabel("Betrag")
    ax.set_title("sin(nx) geht schwach gegen 0, die Norm bleibt", fontsize=10)
    ax.legend(fontsize=7)
    ax = axes[1]
    xx = np.linspace(0, 2 * np.pi, 4000)
    win = int(len(xx) * (np.pi / 20) / (2 * np.pi))
    ax.plot(xx, np.sin(20 * xx) ** 2, color="C0", lw=0.6, label="sin²(20x)")
    yy = np.sin(20 * xx) ** 2
    ax.plot(xx, np.convolve(np.r_[yy[-win:], yy, yy[:win]], np.ones(win) / win, mode="same")[win:-win], "C3", lw=2, label="gleitendes Mittel über eine Periode")
    ax.axhline(0.5, color="k", ls="--", label="schwacher Grenzwert ½")
    ax.set_xlim(0, 2 * np.pi)
    ax.set_xlabel("x"); ax.set_ylabel("Wert")
    ax.set_title("sin²(nx) geht schwach gegen ½, nicht gegen 0²", fontsize=10)
    ax.legend(fontsize=8, loc="lower right")
    ax = axes[2]
    ax.loglog(nn, d_l2, "o-", ms=3, label="‖f_n − Sprung‖₂")
    ax.loglog(nn, d_sup, "s-", ms=3, label="‖f_n − Sprung‖_∞")
    ax.loglog(nn, d_l2[0] * np.sqrt(nn[0] / nn), "k:", label="∝ n^(−1/2)")
    ax.set_xlabel("n (Steilheit von tanh)")
    ax.set_ylabel("Abstand zur Sprungfunktion")
    ax.set_title("Stetige Funktionen mit unstetigem L²-Grenzwert", fontsize=10)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    for k, v in inner.items():
        print(f"{k:30s} |⟨sin(nx), g⟩| bei n = 10, 100, 200: {v[9]:.2e}, {v[99]:.2e}, {v[199]:.2e}")
    print(f"‖sin(nx)‖ zwischen {norms2.min():.6f} und {norms2.max():.6f} (√π = {np.sqrt(np.pi):.6f})")
    print(f"⟨sin²(nx), g⟩ für die Gauß-Glocke, n = 1, 5, 20, 100: {[round(float(v), 6) for v in sq_inner.values()]};  ½∫g = {0.5 * np.sum(w2 * gauss):.6f}")
    print(f"L²-Abstand zum Sprung bei n = 10, 100, 1000: {[f'{l2(fseq(n) - step, ws01):.4f}' for n in (10, 100, 1000)]};  Supremumsabstand immer {d_sup.min():.4f}")
    print(f"Cauchy in L²: ‖f_n − f_2n‖₂ für n = 10, 100, 1000: {[f'{c:.4f}' for c in cauchy]}")


def hahn_banach():
    """35. Hahn-Banach: eine Hyperebene trennt Verschränkung ab (Zellen 12 von functionalanalysis.ipynb)."""
    global P, Q, W_phi, W_psi, ax, axes, bins, cls, ent, ev, fig, i
    global j, mix, partial_transpose, pg, phi_p, prod, psi_m, r, rand_ket, rand_product, rand_state, rng
    global states, w_ent, w_ent_both, w_mix, w_prod, werner_ent, werner_p
    rng = np.random.default_rng(3)
    psi_m = np.array([0, 1, -1, 0]) / np.sqrt(2)
    phi_p = np.array([1, 0, 0, 1]) / np.sqrt(2)
    W_psi = 0.5 * np.eye(4) - np.outer(psi_m, psi_m)
    W_phi = 0.5 * np.eye(4) - np.outer(phi_p, phi_p)
    def partial_transpose(r):
        return r.reshape(2, 2, 2, 2).transpose(0, 3, 2, 1).reshape(4, 4)
    def rand_ket(d):
        v = rng.normal(size=d) + 1j * rng.normal(size=d)
        return v / np.linalg.norm(v)
    def rand_product():
        v = np.kron(rand_ket(2), rand_ket(2))
        return np.outer(v, v.conj())
    prod = [rand_product() for _ in range(20000)]
    mix = [sum(wt * rand_product() for wt in rng.dirichlet(np.ones(4))) for _ in range(20000)]
    def rand_state():
        G = rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4))
        r = G @ G.conj().T
        return r / np.trace(r)
    states = [rand_state() for _ in range(20000)]
    ent = [r for r in states if np.linalg.eigvalsh(partial_transpose(r)).min() < -1e-12]
    ev = lambda W, rs: np.array([np.real(np.trace(W @ r)) for r in rs])
    w_prod, w_mix, w_ent = ev(W_psi, prod), ev(W_psi, mix), ev(W_psi, ent)
    w_ent_both = np.minimum(w_ent, ev(W_phi, ent))
    pg = np.linspace(-0.4, 1.1, 201)
    P, Q = np.meshgrid(pg, pg)
    cls = np.full(P.shape, np.nan)
    for i in range(P.shape[0]):
        for j in range(P.shape[1]):
            r = P[i, j] * np.outer(psi_m, psi_m) + Q[i, j] * np.outer(phi_p, phi_p) + (1 - P[i, j] - Q[i, j]) * np.eye(4) / 4
            if np.linalg.eigvalsh(r).min() < -1e-12:
                continue
            cls[i, j] = 0 if np.linalg.eigvalsh(partial_transpose(r)).min() >= -1e-12 else 1
    werner_p = np.linspace(0, 1, 1001)
    werner_ent = werner_p[[np.linalg.eigvalsh(partial_transpose(p_ * np.outer(psi_m, psi_m) + (1 - p_) * np.eye(4) / 4)).min() < -1e-12 for p_ in werner_p]].min()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.2))
    ax = axes[0]
    ax.contourf(P, Q, cls, levels=[-0.5, 0.5, 1.5], colors=["#b7d7f0", "#f4b6b6"])
    ax.plot(pg, 3 * pg - 1, "C3-", lw=2, label="Zeuge W_Ψ⁻: tr(Wρ) = 0")
    ax.plot(3 * pg - 1, pg, "C2-", lw=2, label="Zeuge W_Φ⁺: tr(Wρ) = 0")
    ax.plot(werner_p, 0 * werner_p, "k-", lw=1)
    ax.plot(1 / 3, 0, "ko", ms=6, label="Werner-Zustand p = 1/3")
    ax.fill([], [], color="#b7d7f0", label="separabel (positive partielle Transposition)")
    ax.fill([], [], color="#f4b6b6", label="verschränkt")
    ax.set_xlim(-0.4, 1.1); ax.set_ylim(-0.4, 1.1)
    ax.set_xlabel("p (Gewicht von |Ψ⁻⟩)"); ax.set_ylabel("q (Gewicht von |Φ⁺⟩)")
    ax.set_title("Schnitt durch die Zwei-Qubit-Zustände: Hyperebenen trennen", fontsize=10)
    ax.legend(fontsize=7, loc="upper right")
    ax = axes[1]
    bins = np.linspace(-0.6, 0.6, 80)
    ax.hist(w_prod, bins=bins, alpha=0.6, density=True, label="zufällige Produktzustände")
    ax.hist(w_mix, bins=bins, alpha=0.6, density=True, label="Mischungen von Produktzuständen")
    ax.hist(w_ent, bins=bins, alpha=0.6, density=True, label="verschränkte Zufallszustände")
    ax.axvline(0, color="k", lw=1)
    ax.set_xlabel("tr(W_Ψ⁻ σ)")
    ax.set_ylabel("Dichte")
    ax.set_title("Der Zeuge ist auf allen separablen Zuständen ≥ 0", fontsize=10)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"tr(Wσ): kleinster Wert auf 20 000 Produktzuständen {w_prod.min():.2e}, auf 20 000 Mischungen {w_mix.min():.4f}")
    print(f"Werner-Zustand: verschränkt ab p = {werner_ent:.3f} (Theorie 1/3), tr(Wρ_p) = 1/4 − 3p/4 bei p = 0.5: {np.real(np.trace(W_psi @ (0.5 * np.outer(psi_m, psi_m) + 0.5 * np.eye(4) / 4))):.4f}")
    print(f"Zufällige Zustände: {len(ent) / len(states):.3f} verschränkt; davon erkennt W_Ψ⁻ {np.mean(w_ent < 0):.3f}, W_Ψ⁻ oder W_Φ⁺ zusammen {np.mean(w_ent_both < 0):.3f}")


def riesz_sobolev():
    """36. Riesz-Darstellung, Sobolev-Raum und Kern-Hilberträume (Zellen 15 von functionalanalysis.ipynb)."""
    global B, Kxz, Kzz, a_, alpha, ax, axes, c, cb, ell, ev_, ew
    global f4, f4p, f_, f_big, fig, g, gp, kH1, keep, kg, krr, lam
    global lam_, nrm, r_h1, r_l2, rep_err, repro, rng, s, sig, w4, x0, x4
    global xd, xt, y0, yd, z
    x4 = np.linspace(0, 1, 40001)
    w4 = np.full_like(x4, x4[1] - x4[0]); w4[[0, -1]] /= 2
    kH1 = lambda x0: np.cosh(np.minimum(x4, x0)) * np.cosh(1 - np.maximum(x4, x0)) / np.sinh(1)
    x0 = 0.3
    sig = np.logspace(-3.3, -0.5, 30)
    r_l2, r_h1 = [], []
    for s in sig:
        g = np.exp(-(x4 - x0) ** 2 / (2 * s * s)); gp = -(x4 - x0) / s ** 2 * g
        r_l2.append(1 / l2(g, w4)); r_h1.append(1 / np.sqrt(np.sum(w4 * (g ** 2 + gp ** 2))))
    f4 = np.sin(3 * x4) + x4 ** 2; f4p = 3 * np.cos(3 * x4) + 2 * x4
    repro = {y0: (np.sum(w4 * (f4 * kH1(y0) + f4p * np.gradient(kH1(y0), x4))), np.sin(3 * y0) + y0 ** 2) for y0 in (0.0, 0.3, 0.7, 1.0)}
    rng = np.random.default_rng(4)
    xd = np.sort(rng.uniform(0, 1, 20)); yd = np.sin(2 * np.pi * xd) + 0.15 * rng.normal(size=20)
    ell = 0.1
    kg = lambda a, b: np.exp(-(a[:, None] - b[None, :]) ** 2 / (2 * ell * ell))
    xt = np.linspace(0, 1, 501)
    krr = {}
    for lam in (1e-4, 1e-2, 1.0):
        alpha = np.linalg.solve(kg(xd, xd) + lam * np.eye(20), yd)
        krr[lam] = (kg(xt, xd) @ alpha, alpha, float(alpha @ kg(xd, xd) @ alpha))
    z = np.r_[np.linspace(0, 1, 201), xd]                       # viel größerer Ansatzraum: 221 Kernfunktionen
    lam = 1e-2
    Kzz, Kxz = kg(z, z), kg(xd, z)
    ew, ev_ = np.linalg.eigh(Kzz)
    keep = ew > 1e-10 * ew.max()
    B = ev_[:, keep] / np.sqrt(ew[keep])                        # Koordinaten, in denen die RKHS-Norm die euklidische ist
    cb = np.linalg.solve((Kxz @ B).T @ (Kxz @ B) + lam * np.eye(keep.sum()), (Kxz @ B).T @ yd)
    f_big = kg(xt, z) @ (B @ cb)
    rep_err = np.abs(f_big - krr[lam][0]).max()

    fig, axes = plt.subplots(1, 3, figsize=(18, 4.8))
    ax = axes[0]
    ax.loglog(sig, r_l2, "o-", ms=3, label="|g(x₀)| / ‖g‖_L²")
    ax.loglog(sig, r_h1, "s-", ms=3, label="|g(x₀)| / ‖g‖_H¹")
    ax.axhline(np.sqrt(kH1(x0)[np.argmin(np.abs(x4 - x0))]), color="C1", ls="--", label="Schranke √k(x₀, x₀) in H¹")
    ax.set_xlabel("Breite σ der Spitze")
    ax.set_ylabel("Wert an x₀ geteilt durch die Norm")
    ax.set_title("Punktauswertung: unbeschränkt in L², beschränkt in H¹", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[1]
    for y0, c in zip((0.0, 0.3, 0.7, 1.0), ("C0", "C1", "C2", "C3")):
        ax.plot(x4, kH1(y0), color=c, label=f"k({y0}, ·)")
    ax.set_xlabel("x"); ax.set_ylabel("k(x₀, x)")
    ax.set_title("Riesz-Vektoren der Punktauswertung in H¹(0, 1)", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[2]
    ax.plot(xd, yd, "ko", ms=4, label="Daten (20 Punkte)")
    ax.plot(xt, np.sin(2 * np.pi * xt), "k:", label="sin(2πx)")
    for (lam_, (f_, a_, nrm)), c in zip(krr.items(), ("C0", "C1", "C2")):
        ax.plot(xt, f_, color=c, label=f"λ = {lam_:g}: ‖f‖²_H = {nrm:.1f}")
    ax.set_xlabel("x"); ax.set_ylabel("f(x)")
    ax.set_title("Kern-Ridge-Regression: f = Σ αᵢ k(xᵢ, ·)", fontsize=10)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print("Reproduzierende Eigenschaft in H¹: " + ", ".join(f"x₀ = {y0}: ⟨k, f⟩ = {a:.8f}, f(x₀) = {b:.8f}" for y0, (a, b) in repro.items()))
    print(f"Spitze mit σ = {sig[0]:.1e}: Verhältnis in L² {r_l2[0]:.1f}, in H¹ {r_h1[0]:.4f};  Schranke √k(x₀,x₀) = {np.sqrt(np.cosh(x0) * np.cosh(1 - x0) / np.sinh(1)):.4f}")
    print(f"Representer-Theorem (λ = 0.01): Minimierung über 221 Kernfunktionen weicht von der Lösung mit 20 um höchstens {rep_err:.1e} ab")
    print("Fehler gegen sin(2πx) auf [0, 1]: " + ", ".join(f"λ = {k_:g}: {np.sqrt(np.mean((v[0] - np.sin(2 * np.pi * xt)) ** 2)):.3f}" for k_, v in krr.items()))


def bounded_unbounded():
    """37. Beschränkt oder unbeschränkt: Ableitung, Green-Operator, Neumann-Reihe, Fredholm (Zellen 18 von functionalanalysis.ipynb)."""
    global D, G, K5, ax, axes, c, check, check_l, errs, f5, fig, h
    global j, k, lam, lams, n, neumann, normD, normK, ns5, overlap, term, u
    global u_direct, unorm, w5, ww5, x5, xx5
    G = lambda x, y: np.minimum(x, y) * (1 - np.maximum(x, y))
    ns5 = np.array([10, 20, 50, 100, 200, 400, 800])
    normD, normK = [], []
    for n in ns5:
        h = 1 / n
        D = (np.eye(n, k=1) - np.eye(n)) / h
        normD.append(opnorm(D))
        normK.append(opnorm(integral_operator(G, n)[0]))
    K5, x5, w5 = integral_operator(G, 400)
    f5 = np.ones(400)
    neumann = {}
    for lam in (5.0, 9.0, 12.0):
        u_direct = np.linalg.solve(np.eye(400) - lam * K5, f5)
        term, u, errs = f5.copy(), np.zeros(400), []
        for j in range(60):
            u = u + term
            term = lam * K5 @ term
            errs.append(l2(u - u_direct, w5) / l2(u_direct, w5))
        neumann[lam] = np.array(errs)
    lams = np.linspace(0.01, 120, 6000)
    xx5 = np.linspace(0, 1, 2001); ww5 = np.full_like(xx5, xx5[1] - xx5[0]); ww5[[0, -1]] /= 2
    unorm = np.array([l2(np.cos(np.sqrt(l) * (xx5 - 0.5)) / np.cos(np.sqrt(l) / 2), ww5) for l in lams])
    check_l = [20.0, 50.0, 100.0]
    check = [l2(np.linalg.solve(np.eye(400) - l * K5, f5) - np.cos(np.sqrt(l) * (x5 - 0.5)) / np.cos(np.sqrt(l) / 2), w5) for l in check_l]
    overlap = [abs(np.sum(w5 * np.sqrt(2) * np.sin(k * np.pi * x5))) for k in (1, 2, 3, 4)]

    fig, axes = plt.subplots(1, 3, figsize=(18, 4.8))
    ax = axes[0]
    ax.loglog(ns5, normD, "o-", label="‖D_n‖ (Ableitung)")
    ax.loglog(ns5, 2 * ns5, "k:", label="2n")
    ax.loglog(ns5, normK, "s-", label="‖K_n‖ (Green-Operator)")
    ax.axhline(1 / np.pi ** 2, color="C1", ls="--", label="1/π²")
    ax.set_xlabel("Zahl der Gitterpunkte n")
    ax.set_ylabel("Operatornorm")
    ax.set_title("Die Ableitung ist unbeschränkt, ihre Umkehrung nicht", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[1]
    for lam, c in zip(neumann, ("C0", "C1", "C3")):
        ax.semilogy(np.arange(1, 61), neumann[lam], color=c, label=f"λ = {lam:g} (λ/π² = {lam / np.pi ** 2:.2f})")
    ax.set_xlabel("Zahl der Glieder der Neumann-Reihe")
    ax.set_ylabel("relativer Fehler")
    ax.set_title("Neumann-Reihe: konvergent nur für |λ| < π²", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[2]
    ax.semilogy(lams, unorm, "C0-", lw=1, label="‖u‖ für f = 1")
    for k, c in ((1, "C3"), (2, "grey"), (3, "C3")):
        ax.axvline((k * np.pi) ** 2, color=c, ls="--", lw=1, label=f"λ = ({k}π)² = {(k * np.pi) ** 2:.1f}" + (" (f senkrecht auf sin 2πx)" if k == 2 else ""))
    ax.set_ylim(0.5, 1e4)
    ax.set_xlabel("λ"); ax.set_ylabel("‖u‖ (L²)")
    ax.set_title("Fredholm-Alternative: Resonanz nur, wo f nicht senkrecht steht", fontsize=10)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"‖D_n‖ für n = {ns5.tolist()}: {[round(v, 1) for v in normD]};  ‖K_n‖: {[round(v, 5) for v in normK]}  (1/π² = {1 / np.pi ** 2:.5f})")
    print("Neumann-Reihe nach 60 Gliedern: " + ", ".join(f"λ = {k:g}: {v[-1]:.1e}" for k, v in neumann.items()))
    print(f"Nyström-Lösung gegen exakte Formel bei λ = {check_l}: Abweichung {[f'{c:.1e}' for c in check]}")
    print(f"Überlappung ⟨1, √2 sin(kπx)⟩ für k = 1 … 4: {[round(o, 6) for o in overlap]}  (Formel 2√2/(kπ) für ungerade k)")


def compact_operators():
    """38. Kompakte Operatoren: Mercer und Karhunen-Loève (Zellen 21 von functionalanalysis.ipynb)."""
    global Kn, M, VB, V_, _, ax, axes, c, eig6, fig, k, k_
    global kernels6, kk, lamB, lam_, lam_exact, name, order, paths, pos, rng, sgn, w6
    global x6, xi
    kernels6 = {"Brownsche Bewegung: min(s, t)": lambda s, t: np.minimum(s, t),
                "Ornstein-Uhlenbeck: e^(−|s−t|/0.2)": lambda s, t: np.exp(-np.abs(s - t) / 0.2),
                "Gauß: e^(−(s−t)²/(2·0.1²))": lambda s, t: np.exp(-(s - t) ** 2 / 0.02)}
    eig6 = {}
    for name, k in kernels6.items():
        Kn, x6, w6 = integral_operator(k, 1000)
        lam_, V_ = np.linalg.eigh(Kn)
        order = np.argsort(lam_)[::-1]
        eig6[name] = (lam_[order], V_[:, order] * np.sqrt(1000))     # Eigenfunktionen L²-normiert
    lamB, VB = eig6["Brownsche Bewegung: min(s, t)"]
    kk = np.arange(1, 1001)
    lam_exact = 1 / ((kk - 0.5) ** 2 * np.pi ** 2)
    rng = np.random.default_rng(6)
    xi = rng.normal(size=1000)
    paths = {M: (VB[:, :M] * np.sqrt(np.maximum(lamB[:M], 0))) @ xi[:M] for M in (5, 20, 200)}

    fig, axes = plt.subplots(1, 3, figsize=(18, 4.8))
    ax = axes[0]
    for (name, (lam_, _)), c in zip(eig6.items(), ("C0", "C1", "C2")):
        pos = lam_[lam_ > 1e-16]
        ax.loglog(np.arange(1, len(pos) + 1), pos, ".", ms=3, color=c, label=name)
    ax.loglog(kk, lam_exact, "k:", lw=1, label="1/((k − ½)²π²)")
    ax.set_ylim(1e-16, 2)
    ax.set_xlabel("Nummer k des Eigenwerts")
    ax.set_ylabel("Eigenwert λ_k")
    ax.set_title("Kompakte Operatoren: Eigenwerte gegen 0, je glatter, desto schneller", fontsize=10)
    ax.legend(fontsize=7)
    ax = axes[1]
    for k_, c in zip(range(4), ("C0", "C1", "C2", "C3")):
        sgn = np.sign(VB[50, k_])
        ax.plot(x6, sgn * VB[:, k_], color=c, lw=2, alpha=0.6, label=f"Eigenfunktion {k_ + 1}")
        ax.plot(x6, np.sqrt(2) * np.sin((k_ + 0.5) * np.pi * x6), "k:", lw=1)
    ax.plot([], [], "k:", label="√2 sin((k − ½)πt)")
    ax.set_xlabel("t"); ax.set_ylabel("e_k(t)")
    ax.set_title("Eigenfunktionen des Kovarianzoperators der Brownschen Bewegung", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[2]
    for M, c in zip(paths, ("C0", "C1", "C2")):
        ax.plot(x6, paths[M], color=c, lw=1.5 if M < 200 else 0.8, label=f"{M} Glieder")
    ax.set_xlabel("t"); ax.set_ylabel("B(t)")
    ax.set_title("Brownsche Bewegung aus der Karhunen-Loève-Zerlegung", fontsize=10)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"Brownsche Bewegung, Eigenwerte 1 … 4: {np.round(lamB[:4], 6).tolist()};  Formel: {np.round(lam_exact[:4], 6).tolist()}")
    print(f"Spur Σλ = {lamB.sum():.6f} (Theorie 1/2), Σλ² = {np.sum(lamB ** 2):.6f} (Theorie 1/6 = {1 / 6:.6f})")
    print("Anteil der Varianz in den ersten 1, 5, 20 Gliedern: " + ", ".join(f"{lamB[:M].sum() / lamB.sum():.4f}" for M in (1, 5, 20)) + f"  (8/π² = {8 / np.pi ** 2:.4f})")
    for name, (lam_, _) in eig6.items():
        print(f"{name:36s} λ₁ = {lam_[0]:.4f}, λ₁₀/λ₁ = {lam_[9] / lam_[0]:.2e}, λ₃₀/λ₁ = {lam_[29] / lam_[0]:.2e}")


def spectrum_types():
    """39. Arten des Spektrums: Volterra, Multiplikation, Shift (Zellen 24 von functionalanalysis.ipynb)."""
    global K7, Ns7, Sx, V7, ax, axes, bound, c, fig, gel_K, gel_V, h7
    global lam, lam7, lower, n7, norms_v, overlap7, perp, psi, pw, resid, rng, s
    global sigs, w7, x7, xr
    n7 = 400
    h7 = 1 / n7
    V7 = (np.tril(np.ones((n7, n7)), -1) + 0.5 * np.eye(n7)) * h7         # Volterra mit Trapez-Gewichten
    K7 = integral_operator(G, n7)[0]
    pw = np.arange(1, 31)
    gel_V = np.array([opnorm(np.linalg.matrix_power(V7, k)) ** (1 / k) for k in pw])
    gel_K = np.array([opnorm(np.linalg.matrix_power(K7, k)) ** (1 / k) for k in pw])
    bound = np.array([(1 / factorial(k)) ** (1 / k) for k in pw])
    x7, w7 = grid01(20000)
    sigs = np.logspace(-3, -0.7, 25)
    resid, overlap7 = [], []
    for s in sigs:
        psi = np.exp(-(x7 - 0.5) ** 2 / (4 * s * s)); psi /= l2(psi, w7)
        resid.append(l2((x7 - 0.5) * psi, w7)); overlap7.append(np.sum(w7 * psi))
    Ns7 = np.arange(1, 2001)
    norms_v = {lam: np.cumsum(lam ** (2 * (Ns7 - 1))) for lam in (0.5, 0.9, 0.99, 1.0)}
    rng = np.random.default_rng(7)
    xr = np.r_[rng.normal(size=50), np.zeros(450)]
    Sx = np.r_[0, xr[:-1]]
    lam7 = 0.6
    perp = np.dot(lam7 ** np.arange(500), Sx - lam7 * xr)
    lower = np.linalg.norm(Sx - lam7 * xr) / np.linalg.norm(xr)

    fig, axes = plt.subplots(1, 3, figsize=(18, 4.8))
    ax = axes[0]
    ax.semilogy(pw, gel_V, "o-", ms=3, label="Volterra: ‖Vⁿ‖^(1/n)")
    ax.semilogy(pw, bound, "k:", label="(1/n!)^(1/n) ≈ e/n")
    ax.semilogy(pw, gel_K, "s-", ms=3, label="Green-Operator: ‖Kⁿ‖^(1/n)")
    ax.axhline(1 / np.pi ** 2, color="C1", ls="--", lw=1, label="1/π²")
    ax.set_xlabel("Potenz n")
    ax.set_ylabel("‖Aⁿ‖^(1/n)")
    ax.set_title("Gelfand-Formel: Volterra hat Spektralradius 0", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[1]
    ax.loglog(sigs, resid, "o-", ms=3, label="‖(M − 0.5)ψ_σ‖")
    ax.loglog(sigs, sigs / np.sqrt(2), "k:", label="σ/√2")
    ax.loglog(sigs, overlap7, "s-", ms=3, label="⟨ψ_σ, 1⟩ (geht schwach gegen 0)")
    ax.set_xlabel("Breite σ")
    ax.set_ylabel("Betrag")
    ax.set_title("Multiplikationsoperator: Weyl-Folge statt Eigenvektor", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[2]
    for lam, c in zip(norms_v, ("C0", "C1", "C2", "C3")):
        ax.loglog(Ns7, norms_v[lam], color=c, label=f"λ = {lam}: Grenzwert {'∞' if lam == 1 else f'{1 / (1 - lam * lam):.2f}'}")
    ax.set_xlabel("Zahl N der Komponenten von v_λ = (1, λ, λ², …)")
    ax.set_ylabel("‖v_λ‖² (abgeschnitten)")
    ax.set_title("Linksshift: Eigenvektoren für |λ| < 1", fontsize=10)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"Volterra: ‖V‖ = {opnorm(V7):.5f} (2/π = {2 / np.pi:.5f}), ‖V⁵‖ = {opnorm(np.linalg.matrix_power(V7, 5)):.2e} ≤ 1/5! = {1 / 120:.2e}, ‖V³⁰‖^(1/30) = {gel_V[-1]:.4f}")
    print(f"Green-Operator: ‖K³⁰‖^(1/30) = {gel_K[-1]:.5f} (1/π² = {1 / np.pi ** 2:.5f}); die Matrix-Eigenwerte des diskreten Volterra-Operators sind alle h/2 = {h7 / 2}")
    print(f"Weyl-Folge: Rest bei σ = 0.001: {resid[0]:.2e}, Skalarprodukt mit 1: {overlap7[0]:.2e}")
    print(f"Rechtsshift, λ = {lam7}: ⟨v_λ, (S − λ)x⟩ = {perp:.1e} für zufälliges x; ‖(S − λ)x‖/‖x‖ = {lower:.3f} ≥ 1 − λ = {1 - lam7:.1f}")


def finite_sections():
    """40. Endliche Abschnitte täuschen: Toeplitz-Operatoren und Pseudospektren (Zellen 27 von functionalanalysis.ipynb)."""
    global M, P_, T8, Tsym, ax, axes, c, cs, ell_dist, eps, ev_exact, ev_np
    global fig, g, growth, gx, gy, k, ks, n8, name, out, pert, rng
    global smin, symbol, th8, z
    n8 = 60
    T8 = toeplitz(np.r_[0, 1.0, np.zeros(n8 - 2)], np.r_[0, 0.25, np.zeros(n8 - 2)])
    Tsym = toeplitz(np.r_[0, 0.5, np.zeros(n8 - 2)])
    ev_exact = np.cos(np.arange(1, n8 + 1) * np.pi / (n8 + 1))
    ev_np = np.linalg.eigvals(T8)
    rng = np.random.default_rng(8)
    pert = {eps: np.concatenate([np.linalg.eigvals(T8 + eps * rng.normal(size=T8.shape) / np.sqrt(n8)) for _ in range(20)]) for eps in (1e-10, 1e-6)}
    th8 = np.linspace(0, 2 * np.pi, 400)
    symbol = np.exp(1j * th8) + 0.25 * np.exp(-1j * th8)
    gx, gy = np.linspace(-1.6, 1.6, 81), np.linspace(-1.1, 1.1, 57)
    smin = np.array([[svdvals((a + 1j * b) * np.eye(n8) - T8)[-1] for a in gx] for b in gy])
    ks = np.arange(0, 301)
    growth = {}
    for name, M in (("nicht normal: T/1.1", T8 / 1.1), ("normal, gleiche Eigenwerte: T_sym/1.1", Tsym / 1.1)):
        P_, out = np.eye(n8), []
        for k in ks:
            out.append(opnorm(P_))
            P_ = P_ @ M
        growth[name] = np.array(out)
    ell_dist = lambda z: np.abs((z.real / 1.25) ** 2 + (z.imag / 0.75) ** 2 - 1)

    fig, axes = plt.subplots(1, 3, figsize=(18, 4.8))
    ax = axes[0]
    ax.plot(symbol.real, symbol.imag, "k-", lw=1, label="Symbol a(θ): Rand des Spektrums des Operators")
    ax.plot(pert[1e-6].real, pert[1e-6].imag, ".", color="C2", ms=2, label="Störung 10⁻⁶ (20 Matrizen)")
    ax.plot(pert[1e-10].real, pert[1e-10].imag, ".", color="C1", ms=2, label="Störung 10⁻¹⁰ (20 Matrizen)")
    ax.plot(ev_np.real, ev_np.imag, "x", color="C3", ms=4, label="numpy, ungestört")
    ax.plot(ev_exact, 0 * ev_exact, "o", color="C0", ms=3, label="exakt: cos(kπ/61)")
    ax.set_aspect("equal")
    ax.set_xlabel("Re z"); ax.set_ylabel("Im z")
    ax.set_ylim(-0.85, 1.35)
    ax.set_title("Eigenwerte von T₆₀: exakt reell, gestört auf Kurven zur Ellipse hin", fontsize=10)
    ax.legend(fontsize=7, loc="upper center", ncol=2)
    ax = axes[1]
    cs = ax.contour(gx, gy, np.log10(smin), levels=[-10, -8, -6, -4, -2, -1], cmap="viridis")
    ax.clabel(cs, fmt=lambda v: f"10^{int(v)}", fontsize=7)
    ax.plot(symbol.real, symbol.imag, "k--", lw=1, label="Symbol a(θ)")
    ax.plot(ev_exact, 0 * ev_exact, "o", color="C0", ms=2, label="Eigenwerte")
    ax.set_aspect("equal")
    ax.set_xlabel("Re z"); ax.set_ylabel("Im z")
    ax.set_title("ε-Pseudospektren von T₆₀: Höhenlinien von σ_min(z − T)", fontsize=10)
    ax.legend(fontsize=7, loc="lower right")
    ax = axes[2]
    for name, c in zip(growth, ("C3", "C0")):
        ax.semilogy(ks, growth[name], color=c, label=name)
    ax.semilogy(ks, (np.cos(np.pi / 61) / 1.1) ** ks, "k:", label="Spektralradius^k")
    ax.semilogy(ks[:80], (1.25 / 1.1) ** ks[:80], "C3:", label="(1.25/1.1)^k")
    ax.set_xlabel("Potenz k")
    ax.set_ylabel("‖A^k‖")
    ax.set_title("Gleiche Eigenwerte, ganz anderes Verhalten", fontsize=10)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"numpy-Eigenwerte von T₆₀: größter Imaginärteil {np.abs(ev_np.imag).max():.2e}, größter Fehler gegen cos(kπ/61) {np.abs(np.sort(ev_np.real) - np.sort(ev_exact)).max():.2e}")
    for eps, z in pert.items():
        print(f"Störung {eps:.0e}: mittlerer Betrag {np.abs(z).mean():.3f}, Median des Abstands zur Ellipse (relativ) {np.median(ell_dist(z)):.3f}, größter Imaginärteil {np.abs(z.imag).max():.3f}")
    for name, g in growth.items():
        print(f"{name:38s} max ‖A^k‖ = {g.max():.3g} bei k = {int(ks[np.argmax(g)])}, ‖A³⁰⁰‖ = {g[-1]:.2e}")
    print(f"σ_min(z − T₆₀) bei z = 0.5i (innerhalb der Ellipse, weit weg von allen Eigenwerten): {svdvals(0.5j * np.eye(n8) - T8)[-1]:.2e}")


def spectral_measure():
    """41. Spektralmaß: gebundene Zustände und kontinuierliches Spektrum (Zellen 30 von functionalanalysis.ipynb)."""
    global E, E640, Egrid, L, Ls9, U, V9, amp, amp_b, ax, axes, bound
    global box_spectrum, c, fig, h9, lam9, late, levels, n, p, p640, packet, psi
    global spec9, tt9, x
    lam9 = 2.5
    V9 = lambda x: -lam9 * (lam9 + 1) / 2 / np.cosh(x) ** 2
    h9 = 0.03
    def box_spectrum(L, Emax=10.0):
        x = np.arange(-L / 2 + h9, L / 2 - h9 / 2, h9)
        E, U = eigh_tridiagonal(1 / h9 ** 2 + V9(x), -0.5 / h9 ** 2 * np.ones(len(x) - 1), select="v", select_range=(-10, Emax))
        return x, E, U / np.sqrt(h9)
    packet = lambda x: np.exp(-x ** 2 / (2 * 0.6 ** 2)) * np.exp(2.5j * x)
    spec9 = {}
    for L in (40, 120, 320):
        x, E, U = box_spectrum(L)
        psi = packet(x); psi /= np.sqrt(h9 * np.sum(np.abs(psi) ** 2))
        c = h9 * (U.T @ psi)
        spec9[L] = (E, np.abs(c) ** 2)
    Ls9 = np.array([20, 30, 40, 60, 80, 120, 160])
    levels = {L: box_spectrum(L, Emax=1.5)[1] for L in Ls9}
    E640, p640 = spec9[320]
    bound = E640 < 0
    tt9 = np.linspace(0, 40, 801)
    amp = np.array([np.sum(p640 * np.exp(-1j * E640 * t)) for t in tt9])
    amp_b = np.array([np.sum(p640[bound] * np.exp(-1j * E640[bound] * t)) for t in tt9])
    Egrid = np.linspace(-3.5, 10, 2000)

    fig, axes = plt.subplots(1, 3, figsize=(18, 4.8))
    ax = axes[0]
    for L in Ls9:
        E = levels[L]
        ax.plot(np.full(len(E), L), E, "_", ms=12, color="C0")
        ax.plot(np.full((E < 0).sum(), L), E[E < 0], "_", ms=14, mew=2, color="C3")
    for n in range(3):
        ax.axhline(-(lam9 - n) ** 2 / 2, color="C3", ls=":", lw=0.8)
    ax.plot([], [], "_", color="C3", mew=2, label="gebundene Zustände (exakt: −3.125, −1.125, −0.125)")
    ax.plot([], [], "_", color="C0", label="Kasten-Zustände des Kontinuums")
    ax.set_xlabel("Kastenlänge L")
    ax.set_ylabel("Energie E")
    ax.set_title("Gebundene Energien bleiben, das Kontinuum verdichtet sich", fontsize=10)
    ax.legend(fontsize=7, loc="upper right")
    ax = axes[1]
    for L, c in zip(spec9, ("C1", "C2", "C0")):
        E, p = spec9[L]
        ax.step(np.r_[Egrid[0], E, Egrid[-1]], np.r_[0, np.cumsum(p), 1], where="post", color=c, label=f"L = {L}: {len(E)} Zustände bis E = 10")
    for n in range(3):
        ax.axvline(-(lam9 - n) ** 2 / 2, color="C3", ls=":", lw=0.8)
    ax.set_xlabel("Energie E")
    ax.set_ylabel("μ_ψ((−∞, E])")
    ax.set_title("Spektralmaß des Wellenpakets: Sprünge und stetiger Teil", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[2]
    ax.plot(tt9, np.abs(amp) ** 2, "C0", label="Überlebenswahrscheinlichkeit (L = 320)")
    ax.plot(tt9, np.abs(amp_b) ** 2, "C3--", label="nur gebundene Zustände")
    ax.axhline(np.sum(p640[bound] ** 2), color="k", ls=":", label="Zeitmittel Σ|c_n|⁴ der gebundenen")
    ax.set_xlabel("Zeit t")
    ax.set_ylabel("|⟨ψ|e^(−iHt)ψ⟩|²")
    ax.set_title("Der kontinuierliche Anteil zerfließt, der gebundene bleibt", fontsize=10)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"Gebundene Energien (L = 320): {np.round(E640[bound], 4).tolist()};  exakt {[-(lam9 - n) ** 2 / 2 for n in range(3)]}")
    print(f"Gewicht des Pakets auf den gebundenen Zuständen: {np.round(p640[bound], 4).tolist()}, zusammen {p640[bound].sum():.4f};  Kontinuum {p640[~bound].sum():.4f}")
    for L, (E, p) in spec9.items():
        print(f"L = {L:3d}: {len(E)} Eigenwerte bis E = 10, kleinste positive Energie {E[E > 0].min():.4f}, gebundenes Gewicht {p[E < 0].sum():.4f}")
    late = tt9 > 20
    print(f"Überlebenswahrscheinlichkeit für t > 20: gemessen im Mittel {np.mean(np.abs(amp[late]) ** 2):.4f}, nur gebunden {np.mean(np.abs(amp_b[late]) ** 2):.4f};  größte Abweichung {np.abs(np.abs(amp[late]) ** 2 - np.abs(amp_b[late]) ** 2).max():.4f}")


def unbounded_operators():
    """42. Unbeschränkte Operatoren: Definitionsbereich und selbstadjungierte Erweiterungen (Zellen 33 von functionalanalysis.ipynb)."""
    global E_, Pth, V_, Vr, ax, axes, er, fig, half, herm, i90, j
    global k, kap, kappas, mom_ev, n_r, nrm0, pk, ring, ring0, rob, rob_ex, robin_exact
    global robin_ground, th, thetas, tt10, twisted, wh, xh, xr10
    def twisted(n, theta, kind):
        """−i d/dx (kind = "p", zentrale Differenzen) oder −d²/dx² (kind = "L") auf [0, 1] mit ψ(1) = e^(iθ)ψ(0)."""
        h = 1 / n
        M = np.zeros((n, n), complex)
        for j in range(n):
            jp, jm = (j + 1) % n, (j - 1) % n
            fp = np.exp(1j * theta) if j == n - 1 else 1
            fm = np.exp(-1j * theta) if j == 0 else 1
            if kind == "p":
                M[j, jp] += -1j / (2 * h) * fp
                M[j, jm] += 1j / (2 * h) * fm
            else:
                M[j, j] += 2 / h ** 2
                M[j, jp] += -fp / h ** 2
                M[j, jm] += -fm / h ** 2
        return M
    thetas = np.linspace(0.05, 2 * np.pi - 0.05, 60)
    mom_ev = []
    for th in thetas:
        E_, V_ = np.linalg.eigh(twisted(400, th, "L"))
        mom_ev.append(np.sort(np.real(np.einsum("ij,ik,kj->j", V_[:, :7].conj(), twisted(400, th, "p"), V_[:, :7]))))
    mom_ev = np.array(mom_ev)
    herm = max(np.abs(twisted(400, th, k_) - twisted(400, th, k_).conj().T).max() for th in (0.3, 2.0) for k_ in ("p", "L"))
    def robin_ground(kappa, n=1500):
        h = 1 / n
        A = (2 * np.eye(n + 1) - np.eye(n + 1, k=1) - np.eye(n + 1, k=-1))
        A[0, 1] = A[n, n - 1] = -2
        A[0, 0] = A[n, n] = 2 + 2 * h * kappa
        d = np.ones(n + 1); d[[0, -1]] = 0.5
        S = (np.sqrt(d)[:, None] * A / np.sqrt(d)[None, :]) / h ** 2
        return np.sort(np.linalg.eigvalsh((S + S.T) / 2))[:2]
    def robin_exact(kappa):
        from scipy.optimize import brentq
        if kappa > 0:
            k = brentq(lambda k: k * np.tan(k / 2) - kappa, 1e-9, np.pi - 1e-9)
            return k * k
        if kappa < 0:
            q = brentq(lambda q: q * np.tanh(q / 2) + kappa, 1e-9, 50)
            return -q * q
        return 0.0
    kappas = np.r_[np.linspace(-4, 0, 9)[:-1], np.linspace(0, 40, 21)]
    rob = np.array([robin_ground(k) for k in kappas])
    rob_ex = np.array([robin_exact(k) for k in kappas])
    tt10 = np.linspace(0, 8, 161)
    xh = np.linspace(0, 30, 30001); wh = np.full_like(xh, xh[1] - xh[0]); wh[[0, -1]] /= 2
    pk = lambda x: np.exp(-(x - 5) ** 2 / 2)
    nrm0 = l2(pk(xh), wh)
    half = [l2(pk(xh + t), wh) / nrm0 for t in tt10]
    n_r = 400; xr10 = (np.arange(n_r) + 0.5) / n_r
    Pth = twisted(n_r, 1.0, "p")
    er, Vr = np.linalg.eigh(Pth)
    ring0 = np.exp(-(xr10 - 0.5) ** 2 / 0.005).astype(complex)
    ring = [np.linalg.norm(Vr @ (np.exp(-1j * t * er) * (Vr.conj().T @ ring0))) / np.linalg.norm(ring0) for t in tt10]

    fig, axes = plt.subplots(1, 3, figsize=(18, 4.8))
    ax = axes[0]
    for k in range(-4, 5):
        ax.plot(thetas, 2 * np.pi * k + thetas, "k:", lw=0.8)
    ax.plot(thetas, mom_ev, ".", color="C0", ms=3)
    ax.plot([], [], ".", color="C0", label="Impuls ⟨v, p v⟩ der 7 tiefsten Eigenvektoren")
    ax.plot([], [], "k:", label="2πk + θ")
    ax.set_ylim(-22, 26)
    ax.set_xlabel("Randphase θ in ψ(1) = e^(iθ)ψ(0)")
    ax.set_ylabel("Eigenwert von p")
    ax.set_title("Impuls auf [0, 1]: jede Phase θ ein anderer Operator", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[1]
    ax.plot(kappas, rob[:, 0], "o", ms=4, label="kleinster Eigenwert (Diskretisierung)")
    ax.plot(kappas, rob_ex, "k-", lw=1, label="exakt: k·tan(k/2) = κ bzw. q·tanh(q/2) = −κ")
    ax.axhline(np.pi ** 2, color="C3", ls="--", label="Dirichlet: π²")
    ax.axhline(0, color="C2", ls="--", label="Neumann: 0")
    ax.set_xlabel("Robin-Parameter κ")
    ax.set_ylabel("kleinster Eigenwert von −d²/dx²")
    ax.set_title("Laplace-Operator: Randbedingung bestimmt das Spektrum", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[2]
    ax.plot(tt10, np.ones_like(tt10), "k-", label="ganze Gerade ℝ")
    ax.plot(tt10, ring, "C2--", label="[0, 1] mit ψ(1) = e^(iθ)ψ(0)")
    ax.plot(tt10, half, "C3-", label="Halbgerade [0, ∞)")
    ax.set_ylim(-0.05, 1.1)
    ax.set_xlabel("Verschiebung a nach links")
    ax.set_ylabel("‖U(a)ψ‖ / ‖ψ‖")
    ax.set_title("Auf der Halbgeraden gibt es keine unitäre Verschiebungsgruppe", fontsize=10)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    i90 = np.argmin(np.abs(thetas - np.pi / 2))
    print(f"Diskretisierte Operatoren hermitesch für jedes θ (Fehler {herm:.0e}); Impulse bei θ = {thetas[i90]:.3f}: {np.round(mom_ev[i90], 3).tolist()}, "
          f"exakt {np.round(np.sort([2 * np.pi * k + thetas[i90] for k in (-3, -2, -1, 0, 1, 2, 3)]), 3).tolist()}")
    for kap in (-2.0, 0.0, 5.0, 40.0):
        j = np.argmin(np.abs(kappas - kap))
        print(f"Robin κ = {kappas[j]:5.1f}: kleinster Eigenwert {rob[j, 0]:8.4f}, exakt {rob_ex[j]:8.4f}")
    print(f"Defektfunktionen e^(−x), e^(x): Norm² auf [0, 1] {0.5 * (1 - np.exp(-2)):.4f} und {0.5 * (np.exp(2) - 1):.4f}; auf [0, 30] {0.5 * (1 - np.exp(-60)):.4f} und {0.5 * (np.exp(60) - 1):.2e}")
    print(f"Verschiebung um a = 8: Norm auf der Halbgeraden {half[-1]:.2e}, auf dem Ring {ring[-1]:.6f}")


def weyl_law():
    """43. Das Weyl-Gesetz: Was man aus den Eigenwerten einer Trommel hört (Zellen 36 von functionalanalysis.ipynb)."""
    global M11, X, Z, a11, ax, axes, c, ev, evk, fig, fits, j
    global lab, lam_ax, lam_s, lmax, lshape_eigs, nL, name, names, r11, rest, scale, spectra
    global truth, ts, xb
    M11 = 150
    spectra = {"Quadrat": np.sort([np.pi ** 2 * (m * m + n * n) for m in range(1, M11) for n in range(1, M11)])}
    r11 = 1 / np.sqrt(np.pi)
    spectra["Kreis"] = np.sort(np.concatenate([jn_zeros(0, 160) ** 2] + [np.repeat(jn_zeros(m, 160) ** 2, 2) for m in range(1, 160)])) / r11 ** 2
    a11 = np.sqrt(4 / np.sqrt(3))
    spectra["Dreieck"] = np.sort([16 * np.pi ** 2 / (9 * a11 * a11) * (m * m + m * n + n * n) for m in range(1, M11) for n in range(1, M11)])
    def lshape_eigs(n, k):
        s = 1 / np.sqrt(3); h = s / n; N = 2 * n
        inside = np.zeros((N + 1, N + 1), bool)
        inside[1:N, 1:N] = True
        inside[n:, n:] = False
        idx = -np.ones(inside.shape, int); idx[inside] = np.arange(inside.sum())
        rows, cols, vals = [], [], []
        for i, j in zip(*np.where(inside)):
            p = idx[i, j]
            rows.append(p); cols.append(p); vals.append(4 / h ** 2)
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = idx[i + di, j + dj]
                if q >= 0:
                    rows.append(p); cols.append(q); vals.append(-1 / h ** 2)
        A = sp.csr_matrix((vals, (rows, cols)))
        return np.sort(spla.eigsh(A, k=k, sigma=0, which="LM", return_eigenvectors=False)), A.shape[0]
    spectra["L-Form"], nL = lshape_eigs(120, 300)
    truth = {"Quadrat": (1, 4, 1 / 4), "Kreis": (1, 2 * np.sqrt(np.pi), 1 / 6), "Dreieck": (1, 3 * a11, 1 / 3), "L-Form": (1, 8 / np.sqrt(3), 5 / 18)}
    fits = {}
    for name, ev in spectra.items():
        lmax = ev[-1] if name == "L-Form" else 40000
        ts = np.linspace(8 / lmax, 25 / lmax, 40)
        Z = np.array([np.sum(np.exp(-ev * t)) for t in ts])
        X = np.c_[1 / (4 * np.pi * ts), -1 / (8 * np.sqrt(np.pi * ts)), np.ones_like(ts)]
        fits[name] = np.linalg.lstsq(X, Z, rcond=None)[0]

    fig, axes = plt.subplots(1, 3, figsize=(18, 4.8))
    ax = axes[0]
    lam_ax = np.linspace(1, 3000, 2000)
    evk = spectra["Kreis"]
    ax.step(evk[evk < 3000], np.arange(1, (evk < 3000).sum() + 1), where="post", color="C0", label="N(λ), Kreis der Fläche 1")
    ax.plot(lam_ax, lam_ax / (4 * np.pi), "k--", label="λ/4π (Weyl)")
    ax.plot(lam_ax, lam_ax / (4 * np.pi) - truth["Kreis"][1] * np.sqrt(lam_ax) / (4 * np.pi), "C3:", label="λ/4π − |∂Ω|√λ/4π")
    ax.set_xlabel("λ"); ax.set_ylabel("Zahl der Eigenwerte ≤ λ")
    ax.set_title("Zählfunktion des Kreises und Weyl-Gesetz", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[1]
    for (name, ev), c in zip(spectra.items(), ("C0", "C1", "C2", "C3")):
        lam_s = ev[ev < (ev[-1] if name == "L-Form" else 6000)]
        rest = (np.arange(1, len(lam_s) + 1) - lam_s / (4 * np.pi)) / np.sqrt(lam_s)
        ax.plot(lam_s, rest, ".", ms=2, color=c, alpha=0.5)
        ax.axhline(-truth[name][1] / (4 * np.pi), color=c, lw=1.5, label=f"{name}: −Umfang/4π = {-truth[name][1] / (4 * np.pi):.3f}")
    ax.set_ylim(-0.6, 0.3)
    ax.set_xlabel("λ"); ax.set_ylabel("(N(λ) − λ/4π) / √λ")
    ax.set_title("Der Rest nach dem Weyl-Term misst den Umfang", fontsize=10)
    ax.legend(fontsize=7)
    ax = axes[2]
    names = list(spectra)
    xb = np.arange(len(names))
    for j, (lab, c) in enumerate(zip(("Fläche", "Umfang / 4", "Eckenterm c₀ × 3"), ("C0", "C1", "C2"))):
        scale = (1, 0.25, 3)[j]
        ax.bar(xb + (j - 1) * 0.27, [truth[n][j] * scale for n in names], 0.27, color=c, alpha=0.35)
        ax.plot(xb + (j - 1) * 0.27, [fits[n][j] * scale for n in names], "o", color=c, ms=7, label=f"{lab}: Balken wahr, Punkt geschätzt")
    ax.set_xticks(xb, names)
    ax.set_ylabel("Wert (skaliert)")
    ax.set_title("Aus dem Spektrum gehört: Fläche, Umfang, Ecken", fontsize=10)
    ax.legend(fontsize=7, loc="upper left")
    plt.tight_layout()
    plt.show()

    print(f"L-Form: {nL} Gitterpunkte, kleinster Eigenwert {spectra['L-Form'][0]:.4f} (Literatur für die L-Form aus Einheitsquadraten 9.6397, mal 3 = 28.919)")
    print("Form       Fläche (Fit / wahr)   Umfang (Fit / wahr)    c₀ (Fit / wahr)")
    for name in names:
        print(f"{name:9s}  {fits[name][0]:.4f} / {truth[name][0]:.4f}      {fits[name][1]:.4f} / {truth[name][1]:.4f}       {fits[name][2]:.4f} / {truth[name][2]:.4f}")


def stone_theorem():
    """44. Der Satz von Stone: unitäre Gruppen und ihre Erzeuger (Zellen 39 von functionalanalysis.ipynb)."""
    global E12, F12, H12, L12, N12, T12, V12, aa, al, ax, axes, c
    global dq_g, dq_r, f12, fig, frft, g_half, gaussf, h12, kg12, opn, osc_ratio, rectf
    global shift_g, shift_r, ws12, xg12, xs12
    xs12 = np.linspace(-12, 12, 240001)
    ws12 = np.full_like(xs12, xs12[1] - xs12[0]); ws12[[0, -1]] /= 2
    gaussf = lambda x: np.exp(-x ** 2 / 2)
    rectf = lambda x: ((x > -1) & (x < 1)).astype(float)
    aa = np.logspace(-3, 0, 25)
    shift_g = np.array([l2(gaussf(xs12 - a) - gaussf(xs12), ws12) for a in aa]) / l2(gaussf(xs12), ws12)
    shift_r = np.array([l2(rectf(xs12 - a) - rectf(xs12), ws12) for a in aa]) / l2(rectf(xs12), ws12)
    def osc_ratio(a):
        f = np.sin(np.pi * xs12 / a) * np.exp(-xs12 ** 2 / 50)
        return l2(np.sin(np.pi * (xs12 - a) / a) * np.exp(-(xs12 - a) ** 2 / 50) - f, ws12) / l2(f, ws12)
    opn = np.array([osc_ratio(a) for a in aa])
    dq_g = np.array([l2((gaussf(xs12 - a) - gaussf(xs12)) / a - xs12 * gaussf(xs12), ws12) for a in aa])     # −ψ' = x e^{−x²/2}
    dq_r = np.array([l2((rectf(xs12 - a) - rectf(xs12)) / a, ws12) for a in aa])
    N12, L12 = 512, 16
    xg12 = np.linspace(-L12, L12, N12, endpoint=False); h12 = xg12[1] - xg12[0]
    kg12 = 2 * np.pi * np.fft.fftfreq(N12, h12)
    T12 = np.real(np.fft.ifft(kg12[:, None] ** 2 * np.fft.fft(np.eye(N12), axis=0), axis=0)) / 2
    H12 = (T12 + T12.T) / 2 + np.diag(xg12 ** 2) / 2
    E12, V12 = eigh(H12)
    frft = lambda al, f: (V12 * np.exp(-1j * al * (E12 - 0.5))) @ (V12.T @ f)
    f12 = 0.5 * (np.tanh(4 * (xg12 + 1)) - np.tanh(4 * (xg12 - 1)))
    F12 = np.array([np.sum(f12 * np.exp(-1j * k * xg12)) * h12 / np.sqrt(2 * np.pi) for k in xg12])     # Fourier-Transformation an den Stellen k = x

    fig, axes = plt.subplots(1, 3, figsize=(18, 4.8))
    ax = axes[0]
    ax.loglog(aa, shift_g, "o-", ms=3, label="Gauß-Funktion: ‖U(a)ψ − ψ‖/‖ψ‖")
    ax.loglog(aa, shift_r, "s-", ms=3, label="Rechteck: ‖U(a)ψ − ψ‖/‖ψ‖")
    ax.loglog(aa, opn, "^-", ms=3, label="Testfunktion sin(πx/a): fast ‖U(a) − 1‖")
    ax.loglog(aa, aa * l2(xs12 * gaussf(xs12), ws12) / l2(gaussf(xs12), ws12), "C0:", label="a‖ψ′‖/‖ψ‖")
    ax.loglog(aa, np.sqrt(aa), "C1:", label="√a (Sprünge)")
    ax.set_xlabel("Verschiebung a")
    ax.set_ylabel("relative Änderung")
    ax.set_title("Stark stetig für jedes ψ, aber ‖U(a) − 1‖ = 2", fontsize=10)
    ax.legend(fontsize=7)
    ax = axes[1]
    ax.loglog(aa, dq_g, "o-", ms=3, label="Gauß-Funktion: ‖(U(a)ψ − ψ)/a + ψ′‖")
    ax.loglog(aa, dq_r, "s-", ms=3, label="Rechteck: ‖(U(a)ψ − ψ)/a‖")
    ax.loglog(aa, np.sqrt(2 / aa), "C1:", label="√(2/a)")
    ax.set_xlabel("Verschiebung a")
    ax.set_ylabel("Norm")
    ax.set_title("Erzeuger nur auf dem Definitionsbereich", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[2]
    for al, c in zip((0, np.pi / 8, np.pi / 4, 3 * np.pi / 8, np.pi / 2), ("k", "C0", "C1", "C2", "C3")):
        ax.plot(xg12, np.abs(frft(al, f12)), color=c, label=f"α = {al / np.pi:.3f}π")
    ax.plot(xg12, np.abs(F12), "k:", lw=2, label="|Fourier-Transformation|")
    ax.set_xlim(-8, 8)
    ax.set_xlabel("x (bei α = π/2: Frequenz k)")
    ax.set_ylabel("|e^(−iα(H − ½)) f|")
    ax.set_title("Gebrochene Fourier-Transformation: vom Rechteck zum sinc", fontsize=10)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    g_half = frft(np.pi / 2, f12)
    print(f"Oszillator auf dem Gitter: kleinste Eigenwerte {np.round(E12[:5], 6).tolist()}, E₄₀ = {E12[40]:.4f}")
    print(f"e^(−iπ/2 (H − ½)) f gegen die Fourier-Transformation: größte Abweichung {np.abs(g_half - F12).max():.1e};  α = π gibt f(−x): {np.abs(frft(np.pi, f12) - f12[(-np.arange(N12)) % N12]).max():.1e}")
    print(f"Verschiebung a = {aa[0]:.0e}: Gauß {shift_g[0]:.2e}, Rechteck {shift_r[0]:.2e} (√a = {np.sqrt(aa[0]):.2e});  Testfunktion bei a = 0.01, 0.1, 1: {np.round(opn[[8, 16, -1]], 4).tolist()}")
    print(f"Differenzenquotient bei a = {aa[0]:.0e}: Gauß-Fehler {dq_g[0]:.2e}, Rechteck {dq_r[0]:.1f} (√(2/a) = {np.sqrt(2 / aa[0]):.1f})")


def stone_von_neumann():
    """45. Stone-von Neumann: [x, p] = i lässt sich nicht mit Matrizen darstellen (Zellen 42 von functionalanalysis.ipynb)."""
    global D, N, N60, Nw, Q_, R_, S13, U13, V13, Wr, Xs, Zc
    global _, a, a10, a60, ax, axes, basis, c, comm10, e, evV, ex60
    global fig, herm_nodes, inter_err, ladder, ok, om, p10, rng, rs, v0, vac, vecV
    global weyl, x10, xx13
    def ladder(N):
        return np.diag(np.sqrt(np.arange(1, N)), 1)
    a10 = ladder(10)
    x10 = (a10 + a10.T) / np.sqrt(2); p10 = (a10 - a10.T) / (1j * np.sqrt(2))
    comm10 = np.diag(x10 @ p10 - p10 @ x10) / 1j
    rs = np.linspace(0.25, 8, 32)
    weyl = {}
    for N in (20, 40, 80):
        a = ladder(N)
        D = lambda al: expm(al * a.T - np.conj(al) * a)
        vac = np.zeros(N); vac[0] = 1
        weyl[N] = np.array([np.linalg.norm(D(r) @ D(1j * r) @ vac - np.exp(1j * np.imag(r * np.conj(1j * r))) * D(r + 1j * r) @ vac) for r in rs])
    N60 = 200
    a60 = ladder(N60)
    ex60 = np.linalg.eigvalsh((a60 + a60.T) / np.sqrt(2))
    herm_nodes = np.polynomial.hermite.hermgauss(N60)[0]
    Nw = 12
    om = np.exp(2j * np.pi / Nw)
    Xs = np.roll(np.eye(Nw), 1, axis=0); Zc = np.diag(om ** np.arange(Nw))
    rng = np.random.default_rng(13)
    Q_, R_ = np.linalg.qr(rng.normal(size=(Nw, Nw)) + 1j * rng.normal(size=(Nw, Nw)))
    Wr = Q_ * (np.diag(R_) / np.abs(np.diag(R_)))
    U13, V13 = Wr @ Xs @ Wr.conj().T, Wr @ Zc @ Wr.conj().T
    evV, vecV = np.linalg.eig(V13)
    v0 = vecV[:, np.argmin(np.abs(evV - 1))]
    v0 = v0 / np.linalg.norm(v0)
    basis = [v0]
    for _ in range(Nw - 1):
        basis.append(U13 @ basis[-1])
    S13 = np.array(basis).conj()                                 # Zeilen: Basisvektoren, S U S† = Schiebung, S V S† = Takt
    inter_err = max(np.abs(S13 @ U13 @ S13.conj().T - Xs).max(), np.abs(S13 @ V13 @ S13.conj().T - Zc).max())

    fig, axes = plt.subplots(1, 3, figsize=(18, 4.8))
    ax = axes[0]
    ax.bar(np.arange(10), np.real(comm10), color=["C0"] * 9 + ["C3"])
    ax.axhline(1, color="k", ls="--", lw=1, label="[x, p] = i verlangt überall 1")
    ax.set_xlabel("Zustand n des Oszillators")
    ax.set_ylabel("Diagonale von [x_N, p_N] / i")
    ax.set_title(f"N = 10: Spur = {np.real(comm10).sum():.0f}, der letzte Zustand gleicht aus", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[1]
    for N, c in zip(weyl, ("C0", "C1", "C2")):
        ax.semilogy(rs ** 2 * 2, weyl[N] + 1e-17, "o-", ms=3, color=c, label=f"N = {N}")
        ax.axvline(N, color=c, ls=":", lw=1)
    ax.set_xlabel("|α + β|² = 2r² (mittlere Photonenzahl des Ergebnisses)")
    ax.set_ylabel("Fehler der Weyl-Relation auf |0⟩")
    ax.set_title("Abgeschnitten gilt die Weyl-Relation nur für |α|² ≪ N", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[2]
    xx13 = np.linspace(-np.sqrt(2 * N60), np.sqrt(2 * N60), 400)
    ax.hist(ex60, bins=np.linspace(-np.sqrt(2 * N60), np.sqrt(2 * N60), 21), alpha=0.6, label=f"Eigenwerte von x_N, N = {N60}")
    ax.plot(xx13, np.sqrt(2 * N60 - xx13 ** 2) / np.pi * (2 * np.sqrt(2 * N60) / 20), "k-", label="Halbkreis √(2N − x²)/π")
    ax.set_xlabel("Eigenwert von x_N")
    ax.set_ylabel("Anzahl pro Klasse")
    ax.set_title("Endliche Matrix, dicht gepacktes Spektrum statt ℝ", fontsize=10)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"Diagonale von [x₁₀, p₁₀]/i: {np.round(np.real(comm10), 6).tolist()}, Spur {np.real(comm10).sum():.1e}")
    for N, e in weyl.items():
        ok = rs[e < 1e-6]
        print(f"N = {N}: Weyl-Relation auf |0⟩ besser als 1e-6 bis 2r² = {2 * ok.max() ** 2:.1f}, Fehler bei 2r² = 128: {e[-1]:.3f}")
    print(f"Eigenwerte von x_N (N = {N60}) gleich den Hermite-Nullstellen (Gauß-Hermite-Knoten): {np.abs(np.sort(ex60) - np.sort(herm_nodes)).max():.1e};  größter {ex60.max():.3f}, √(2N) = {np.sqrt(2 * N60):.3f}")
    print(f"Endliches Weyl-Paar (N = 12), zufällig gedreht: VU = ωUV bis auf {np.abs(V13 @ U13 - om * U13 @ V13).max():.1e};  "
          f"rekonstruierte Verflechtung S mit S U S† = X, S V S† = Z: Fehler {inter_err:.1e}")


def koopman():
    """46. Der Koopman-Operator: nichtlineare Dynamik als lineare Abbildung (Zellen 45 von functionalanalysis.ipynb)."""
    global A_dmd, K_edmd, Xd, Yd, _, ax, axes, dt14, fig, flow14, la14, lift
    global mu14, pred_dmd, pred_edmd, rate, rng, sol, t_test, tr, trajs, truth14, v, xs14
    global z_test
    mu14, la14 = -0.05, -1.0
    flow14 = lambda t, z: [mu14 * z[0], la14 * (z[1] - z[0] ** 2)]
    dt14 = 0.1
    rng = np.random.default_rng(14)
    Xd, Yd, trajs = [], [], []
    for _ in range(30):
        sol = solve_ivp(flow14, (0, 10), rng.uniform(-1.5, 1.5, 2), t_eval=np.arange(0, 10 + 1e-9, dt14), rtol=1e-10, atol=1e-12).y
        trajs.append(sol); Xd.append(sol[:, :-1]); Yd.append(sol[:, 1:])
    Xd, Yd = np.hstack(Xd), np.hstack(Yd)
    A_dmd = Yd @ np.linalg.pinv(Xd)
    lift = lambda Z: np.vstack([Z[0], Z[1], Z[0] ** 2])
    K_edmd = lift(Yd) @ np.linalg.pinv(lift(Xd))
    rate = lambda M: np.sort(np.log(np.linalg.eigvals(M).astype(complex)).real / dt14)
    z_test = np.array([1.2, -1.0])
    t_test = np.arange(0, 20 + 1e-9, dt14)
    truth14 = solve_ivp(flow14, (0, 20), z_test, t_eval=t_test, rtol=1e-10, atol=1e-12).y
    pred_dmd = np.array([np.linalg.matrix_power(A_dmd, k) @ z_test for k in range(len(t_test))]).T
    pred_edmd = np.array([np.linalg.matrix_power(K_edmd, k) @ lift(z_test[:, None])[:, 0] for k in range(len(t_test))]).T[:2]

    fig, axes = plt.subplots(1, 3, figsize=(18, 4.8))
    ax = axes[0]
    for tr in trajs[:15]:
        ax.plot(tr[0], tr[1], "C0-", lw=0.8, alpha=0.7)
    xs14 = np.linspace(-1.5, 1.5, 200)
    ax.plot(xs14, la14 / (la14 - 2 * mu14) * xs14 ** 2, "C3--", lw=2, label="langsame Mannigfaltigkeit x₂ = λ/(λ − 2μ) x₁²")
    ax.set_xlabel("x₁"); ax.set_ylabel("x₂")
    ax.set_title("Trajektorien: schneller Fall auf die Parabel, dann langsam", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[1]
    ax.plot(rate(A_dmd), np.full(2, 1), "o", ms=10, label="DMD mit (x₁, x₂)")
    ax.plot(rate(K_edmd), np.full(3, 0), "s", ms=10, label="EDMD mit (x₁, x₂, x₁²)")
    for v in (mu14, la14, 2 * mu14):
        ax.axvline(v, color="k", ls=":", lw=1)
    ax.set_yticks([0, 1], ["EDMD", "DMD"]); ax.set_ylim(-0.7, 1.7)
    ax.set_xlabel("Rate log(Eigenwert)/Δt (gepunktet: μ, λ, 2μ)")
    ax.set_title("Raten der gelernten linearen Modelle", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[2]
    ax.plot(t_test, truth14[1], "k-", lw=2, label="wahre Lösung x₂(t)")
    ax.plot(t_test, pred_dmd[1], "C0--", label="Vorhersage DMD")
    ax.plot(t_test, pred_edmd[1], "C1:", lw=2, label="Vorhersage EDMD")
    ax.set_xlabel("Zeit t"); ax.set_ylabel("x₂")
    ax.set_title("Vorhersage einer neuen Trajektorie aus x(0) = (1.2, −1)", fontsize=10)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"Raten DMD: {np.round(rate(A_dmd), 4).tolist()};  EDMD: {np.round(rate(K_edmd), 6).tolist()};  exakt: {sorted([mu14, la14, 2 * mu14])}")
    print(f"Vorhersagefehler max |x₂| über t ∈ [0, 20]: DMD {np.abs(pred_dmd[1] - truth14[1]).max():.3f}, EDMD {np.abs(pred_edmd[1] - truth14[1]).max():.1e}")
    print(f"EDMD-Matrix (gerundet):\n{np.round(K_edmd, 4)}")


def operator_learning():
    """47. Operator-Lernen: eine Abbildung zwischen Funktionsräumen aus Beispielen (Zellen 48 von functionalanalysis.ipynb)."""
    global F, F40, F_fine, F_test, T15, U, U40, U_fine, U_test, Wm, apply_multiplier, ax
    global axes, e1, e2, err_mat, err_mult, fig, fit_multiplier, heat_pairs, kk15, kmax15, ks15, m
    global m40, n, ns15, pred_fine, rep, rng, xf
    T15, kmax15 = 0.05, 20
    ks15 = np.arange(1, kmax15 + 1)
    rng = np.random.default_rng(15)
    def heat_pairs(n, N):
        c = (rng.normal(size=(n, kmax15)) + 1j * rng.normal(size=(n, kmax15))) / (1 + ks15) ** 1.5
        xs = 2 * np.pi * np.arange(N) / N
        basis = np.exp(1j * np.outer(ks15, xs))
        return np.real(c @ basis), np.real((c * np.exp(-ks15 ** 2 * T15)) @ basis)
    def fit_multiplier(F, U):
        Fh, Uh = np.fft.rfft(F, axis=1), np.fft.rfft(U, axis=1)
        return np.array([np.vdot(Fh[:, k], Uh[:, k]) / max(np.vdot(Fh[:, k], Fh[:, k]).real, 1e-30) for k in range(Fh.shape[1])])
    def apply_multiplier(m, F):
        N = F.shape[1]
        mm = np.zeros(N // 2 + 1, complex); mm[:min(len(m), N // 2 + 1)] = m[:N // 2 + 1]
        return np.fft.irfft(np.fft.rfft(F, axis=1) * mm[None, :], n=N, axis=1)
    F_test, U_test = heat_pairs(200, 64)
    F_fine, U_fine = heat_pairs(1, 256)
    ns15 = np.array([2, 4, 8, 16, 32, 64, 128, 256])
    err_mult, err_mat = [], []
    for n in ns15:
        e1, e2 = [], []
        for rep in range(5):
            F, U = heat_pairs(n, 64)
            U = U + 1e-3 * rng.normal(size=U.shape)
            m = fit_multiplier(F, U)
            e1.append(np.linalg.norm(apply_multiplier(m, F_test) - U_test) / np.linalg.norm(U_test))
            Wm = U.T @ F @ np.linalg.inv(F.T @ F + 1e-6 * np.eye(64))
            e2.append(np.linalg.norm(F_test @ Wm.T - U_test) / np.linalg.norm(U_test))
        err_mult.append(np.median(e1)); err_mat.append(np.median(e2))
    F40, U40 = heat_pairs(40, 64)
    m40 = fit_multiplier(F40, U40 + 1e-3 * rng.normal(size=U40.shape))
    pred_fine = apply_multiplier(m40, F_fine)

    fig, axes = plt.subplots(1, 3, figsize=(18, 4.8))
    ax = axes[0]
    kk15 = np.arange(len(m40))
    ax.semilogy(kk15[1:kmax15 + 1], np.abs(m40[1:kmax15 + 1]), "o", label="gelernt aus 40 Paaren")
    ax.semilogy(kk15[1:kmax15 + 1], np.exp(-kk15[1:kmax15 + 1] ** 2 * T15), "k-", label="exakt e^(−k²T)")
    ax.set_xlabel("Frequenz k")
    ax.set_ylabel("|m(k)|")
    ax.set_title("Gelernter Fourier-Multiplikator der Wärmeleitung", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[1]
    xf = 2 * np.pi * np.arange(256) / 256
    ax.plot(xf, F_fine[0], "C7-", lw=1, label="Eingabe f (256 Punkte)")
    ax.plot(xf, U_fine[0], "k-", lw=2, label="wahre Lösung u = e^(TΔ) f")
    ax.plot(xf, pred_fine[0], "C1--", lw=2, label="Vorhersage (auf 64 Punkten gelernt)")
    ax.set_xlabel("x"); ax.set_ylabel("Wert")
    ax.set_title("Auflösungsunabhängig: gelernt auf 64, angewandt auf 256 Punkte", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[2]
    ax.loglog(ns15, err_mult, "o-", label="Fourier-Multiplikator (33 Parameter)")
    ax.loglog(ns15, err_mat, "s-", label="volle 64×64-Matrix (4096 Parameter)")
    ax.axvline(40, color="grey", ls=":", lw=1, label="40 = Dimension des Eingaberaums")
    ax.set_xlabel("Zahl der Trainingspaare n")
    ax.set_ylabel("relativer Testfehler (Median aus 5)")
    ax.set_title("Mit der richtigen Struktur reichen wenige Beispiele", fontsize=10)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"Multiplikator k = 1 … 5: {np.round(m40[1:6].real, 4).tolist()};  exakt {np.round(np.exp(-np.arange(1, 6) ** 2 * T15), 4).tolist()}")
    print(f"Fehler auf dem feinen Gitter (256 Punkte): {np.linalg.norm(pred_fine - U_fine) / np.linalg.norm(U_fine):.2e}")
    print("Testfehler Multiplikator / Matrix: " + ", ".join(f"n = {n}: {a:.1e} / {b:.1e}" for n, a, b in zip(ns15, err_mult, err_mat)))
