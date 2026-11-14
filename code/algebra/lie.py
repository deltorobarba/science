"""Lie-Gruppen, Lie-Algebren und Darstellungstheorie: Tangentialraum, Exponentialabbildung, BCH, Trotter, Lie-Gruppen-Integratoren, Killing-Form, Wurzelsysteme und E8, dynamische Lie-Algebren, Charaktertafeln, Molekülschwingungen, Spin j, Clebsch-Gordan, SU(3) und Schur-Weyl.

Für algebra.ipynb aus lie.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, tangent_space, exponential, exp_limits, bch_formula, trotter_formulas, integrators, killing_form, root_systems, dynamical_lie_algebras, character_tables, molecular_vibrations, spin_j, cg_coefficients, su3, schur_weyl.
"""
import itertools, time
from fractions import Fraction
from math import comb, factorial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from scipy.linalg import expm, logm, det as sdet
from scipy.integrate import solve_ivp
from scipy import stats
from scipy.special import lpmv
from sympy import Rational
from sympy.combinatorics import Permutation, PermutationGroup
from sympy.combinatorics.named_groups import SymmetricGroup, AlternatingGroup, DihedralGroup
from sympy.physics.quantum.cg import CG
from sympy.physics.quantum.spin import Rotation
from sympy.liealgebras.cartan_type import CartanType


def load():
    """51. Daten (Zellen 4 von lie.ipynb)."""
    global PX, PY, PZ, character_table, comm, gell_mann, hat, killing, rodrigues, site_op, spin_matrices, structure_constants
    # Alles hier (numpy, scipy, sympy, matplotlib) ist in Colab vorinstalliert

    PX = np.array([[0, 1], [1, 0]], complex); PY = np.array([[0, -1j], [1j, 0]]); PZ = np.diag([1, -1]).astype(complex)

    def comm(A, B):
        return A @ B - B @ A

    def hat(w):
        """Vektor ω ∈ ℝ³ → schiefsymmetrische Matrix [ω]× ∈ so(3) mit [ω]× v = ω × v."""
        return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])

    def rodrigues(w):
        """exp([ω]×) in geschlossener Form: Drehung um die Achse ω/|ω| um den Winkel |ω|."""
        th, K = np.linalg.norm(w), hat(w)
        if th < 1e-12:
            return np.eye(3) + K
        return np.eye(3) + np.sin(th) / th * K + (1 - np.cos(th)) / th ** 2 * K @ K

    def site_op(P, i, n):
        """Der 2×2-Operator P auf Qubit i einer Kette aus n Qubits (Identität auf den übrigen)."""
        out = np.array([[1.0 + 0j]])
        for k in range(n):
            out = np.kron(out, P if k == i else np.eye(2))
        return out

    def spin_matrices(j):
        """Spin-j-Darstellung von su(2) in der Basis |j,j⟩, …, |j,−j⟩: J₊|m⟩ = √(j(j+1) − m(m+1)) |m+1⟩."""
        m = np.arange(j, -j - 1, -1)
        Jp = np.diag(np.sqrt(j * (j + 1) - m[1:] * (m[1:] + 1)), 1).astype(complex)
        return (Jp + Jp.T) / 2, (Jp - Jp.T) / 2j, np.diag(m).astype(complex), Jp

    def gell_mann():
        l = np.zeros((8, 3, 3), complex)
        for a, (i, k) in enumerate([(0, 1), (0, 2), (1, 2)]):
            b = [0, 3, 5][a]
            l[b][i, k] = l[b][k, i] = 1
            l[b + 1][i, k], l[b + 1][k, i] = -1j, 1j
        l[2] = np.diag([1, -1, 0]); l[7] = np.diag([1, 1, -2]) / np.sqrt(3)
        return l

    def structure_constants(basis):
        """c[i, j, k] mit [e_i, e_j] = Σ_k c_ijk e_k (Koeffizienten aus einem linearen Gleichungssystem)."""
        B = np.array([b.ravel() for b in basis]).T
        return np.array([[np.linalg.lstsq(B, comm(a, b).ravel(), rcond=None)[0] for b in basis] for a in basis])

    def killing(basis):
        """Killing-Form K_il = tr(ad e_i · ad e_l) und die Matrizen der adjungierten Darstellung, (ad e_i)_kj = c_ijk."""
        ad = np.transpose(structure_constants(basis), (0, 2, 1))
        return np.real(np.einsum("ikj,ljk->il", ad, ad)), ad

    def character_table(n, mul, inv):
        """Charaktertafel einer endlichen Gruppe mit Elementen 0, …, n−1 (mul(i, j) und inv(i) liefern Indizes).
    Die Klassensummen multiplizieren sich mit ganzzahligen Klassenkonstanten; deren gemeinsame Eigenvektoren
    sind die Werte ω_χ(C) = |C|·χ(g)/χ(1) der irreduziblen Charaktere (Burnside 1911)."""
        M = np.array([[mul(i, j) for j in range(n)] for i in range(n)])
        I = np.array([inv(i) for i in range(n)])
        e = next(i for i in range(n) if all(M[i, j] == j for j in range(n)))
        seen, classes = set(), []
        for g in range(n):
            if g not in seen:
                c = sorted({M[M[h, g], I[h]] for h in range(n)})
                seen.update(c)
                classes.append(c)
        classes.sort(key=lambda c: (e not in c, len(c), c[0]))
        cls_of = np.empty(n, int)
        for k, c in enumerate(classes):
            cls_of[c] = k
        r, sizes = len(classes), np.array([len(c) for c in classes])
        C = np.zeros((r, r, r))                      # C[i, j, k] = #{x ∈ C_i : x⁻¹z ∈ C_j} für ein festes z ∈ C_k
        for k in range(r):
            z = classes[k][0]
            for i in range(r):
                for x in classes[i]:
                    C[i, cls_of[M[I[x], z]], k] += 1
        A = np.tensordot(np.random.default_rng(0).normal(size=r), C, axes=(0, 0))   # zufällige Kombination: trennt alle Eigenvektoren
        _, V = np.linalg.eig(A)
        V = V / V[0]
        chi = np.array([V[:, t] * np.sqrt(n / np.sum(np.abs(V[:, t]) ** 2 / sizes)) / sizes for t in range(r)])
        chi = np.where(np.abs(chi.imag) < 1e-9, chi.real, chi)
        order = sorted(range(r), key=lambda t: (round(chi[t, 0].real), -round(float(np.sum(chi[t].real * sizes)), 6), tuple(-np.round(chi[t].real, 6))))
        return chi[order], classes, sizes

    print("Werkzeuge bereit: Kommutator, so(3) und Rodrigues, Qubit-Operatoren, Spin j, Gell-Mann, Killing-Form, Charaktertafel")


def tangent_space():
    """52. Von der Gruppe zur Algebra: der Tangentialraum an der Eins (Zellen 6 von lie.ipynb)."""
    global Jsym, Xa, Xg, Xt, ax, axes, bins, c, constraint, dims, eps, eta
    global f, fig, formula, g, lab, pairs, res_comm, res_prod, rng, skew_res, slope, st
    global t, tangent_dim, th, v, viol_sl, viol_so
    rng = np.random.default_rng(1)
    Jsym = lambda n: np.block([[np.zeros((n, n)), np.eye(n)], [-np.eye(n), np.zeros((n, n))]])
    eta = np.diag([-1.0, 1, 1, 1])

    def constraint(name, n):
        """(Matrixgröße, komplex?, F) mit G = {g : F(g) = 0}; F liefert einen reellen Vektor."""
        cplx = lambda A: np.r_[A.real.ravel(), A.imag.ravel()]
        if name == "SO(n)":
            return n, False, lambda g: (g.T @ g - np.eye(n)).ravel()
        if name == "SL(n,ℝ)":
            return n, False, lambda g: np.array([np.linalg.det(g) - 1])
        if name == "U(n)":
            return n, True, lambda g: cplx(g.conj().T @ g - np.eye(n))
        if name == "SU(n)":
            return n, True, lambda g: np.r_[cplx(g.conj().T @ g - np.eye(n)), cplx(np.array([sdet(g) - 1]))]
        if name == "Sp(2n,ℝ)":
            return 2 * n, False, lambda g: (g.T @ Jsym(n) @ g - Jsym(n)).ravel()
        if name == "SO(1,3)":
            return 4, False, lambda g: (g.T @ eta @ g - eta).ravel()

    def tangent_dim(name, n, h=1e-6):
        N, is_c, F = constraint(name, n)
        dirs = [np.eye(N * N)[k].reshape(N, N) for k in range(N * N)]
        if is_c:
            dirs = dirs + [1j * d for d in dirs]
        Jac = np.array([(F(np.eye(N) + h * d) - F(np.eye(N) - h * d)) / (2 * h) for d in dirs]).T
        return len(dirs) - np.linalg.matrix_rank(Jac, tol=1e-6)

    formula = {"SO(n)": lambda n: n * (n - 1) // 2, "SL(n,ℝ)": lambda n: n * n - 1, "U(n)": lambda n: n * n,
               "SU(n)": lambda n: n * n - 1, "Sp(2n,ℝ)": lambda n: n * (2 * n + 1)}
    dims = {g: [tangent_dim(g, n) for n in range(2, 6)] for g in formula}

    eps = np.logspace(-6, -1, 30)
    Xa = rng.normal(size=(3, 3)); Xa = Xa - Xa.T          # in so(3)
    Xg = rng.normal(size=(3, 3))                           # beliebig
    Xt = rng.normal(size=(3, 3)); Xt -= np.trace(Xt) / 3 * np.eye(3)   # spurfrei: in sl(3)
    viol_so = lambda X: [np.linalg.norm((np.eye(3) + e * X).T @ (np.eye(3) + e * X) - np.eye(3)) for e in eps]
    viol_sl = lambda X: [abs(np.linalg.det(np.eye(3) + e * X) - 1) for e in eps]
    slope = lambda v: np.polyfit(np.log(eps), np.log(v), 1)[0]

    pairs = rng.normal(size=(2000, 2, 4, 4)); pairs = pairs - np.transpose(pairs, (0, 1, 3, 2))
    skew_res = lambda Z: np.linalg.norm(Z + Z.T) / np.linalg.norm(Z)
    res_comm = np.array([skew_res(comm(X, Y)) for X, Y in pairs])
    res_prod = np.array([skew_res(X @ Y) for X, Y in pairs])

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.6))
    t = np.linspace(0, 2 * np.pi, 300)
    ax = axes[0]
    ax.plot(np.cos(t), np.sin(t), "k-", label="SO(2) ≅ U(1): Einheitskreis e^(iθ)")
    ax.plot([1, 1], [-1.3, 1.3], "C0--", label="Tangente an der Eins: 1 + iθ (Lie-Algebra iℝ)")
    for th, c in ((0.6, "C1"), (1.2, "C2")):
        ax.plot(1, th, "o", color=c, ms=7)
        ax.plot(np.cos(th), np.sin(th), "s", color=c, ms=7, label=f"θ = {th}: 1 + iθ (Kreis) und e^(iθ) (Quadrat)")
    ax.annotate("", xy=(1, 0.45), xytext=(1, 0), arrowprops=dict(arrowstyle="->", color="C3", lw=2))
    ax.plot([], [], color="C3", lw=2, label="X = i: Element der Lie-Algebra")
    ax.set_aspect("equal"); ax.set_xlim(-1.3, 3.6); ax.set_ylim(-1.4, 1.4)
    ax.set_xlabel("Re"); ax.set_ylabel("Im")
    ax.set_title("SO(2) und seine Lie-Algebra: Kreis und Tangente", fontsize=10)
    ax.legend(fontsize=7, loc="lower right")
    ax = axes[1]
    for v, lab, st in ((viol_so(Xa), "‖(1+εX)ᵀ(1+εX) − 1‖, X ∈ so(3)", "o-"), (viol_so(Xg), "‖(1+εX)ᵀ(1+εX) − 1‖, X beliebig", "o--"),
                       (viol_sl(Xt), "|det(1+εX) − 1|, X ∈ sl(3)", "s-"), (viol_sl(Xg), "|det(1+εX) − 1|, X beliebig", "s--")):
        ax.loglog(eps, v, st, ms=3, label=f"{lab} (Steigung {slope(v):.2f})")
    ax.set_xlabel("ε")
    ax.set_ylabel("Verletzung der Gruppenbedingung")
    ax.set_title("Liegt X in der Lie-Algebra, ist der Fehler von zweiter Ordnung", fontsize=10)
    ax.legend(fontsize=7)
    ax = axes[2]
    bins = np.linspace(-17.5, 1, 60)
    ax.hist(np.log10(np.maximum(res_comm, 1e-17)), bins=bins, alpha=0.7, label="[X, Y] (Kommutator; exakt 0 bei −17 eingetragen)")
    ax.hist(np.log10(res_prod), bins=bins, alpha=0.7, label="XY (Produkt)")
    ax.set_xlabel("log₁₀ ‖Z + Zᵀ‖ / ‖Z‖  (−17: schiefsymmetrisch, 0: weit weg von so(4))")
    ax.set_ylabel("Anzahl Paare")
    ax.set_title("Der Kommutator bleibt in so(4), das Produkt nicht", fontsize=10)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print("Dimension des Tangentialraums (numerisch) und Formel, n = 2, 3, 4, 5:")
    for g, f in formula.items():
        print(f"  {g:9s} {dims[g]}   Formel {[f(n) for n in range(2, 6)]}")
    print(f"  SO(1,3)   {tangent_dim('SO(1,3)', 4)}   (3 Drehungen + 3 Boosts)")
    print(f"Kommutator: größter Abstand von so(4) {res_comm.max():.1e};  Produkt: kleinster Abstand {res_prod.min():.2f}")


def exponential():
    """53. Die Exponentialabbildung: von der Algebra zurück in die Gruppe (Zellen 9 von lie.ipynb)."""
    global A0, K, V_, X, X1, Xs2, Y1, ax, axes, boost, c, err_sl2
    global exp_sl2, exp_taylor, fig, k, kinds, lab, nb, ok, orb, p, phi0, reach
    global rng, s, starts, taylor_err, terms, tt, tt_ell, v_rel, via_eig, via_ode, w3, w_
    rng = np.random.default_rng(2)
    def exp_taylor(X, terms):
        out, term = np.eye(len(X)), np.eye(len(X))
        for k in range(1, terms):
            term = term @ X / k
            out = out + term
        return out

    A0 = rng.normal(size=(4, 4)); A0 = A0 - A0.T; A0 /= np.linalg.norm(A0, 2)        # schiefsymmetrisch, Spektralnorm 1
    terms = np.arange(1, 91)
    taylor_err = {s: np.array([np.linalg.norm(exp_taylor(s * A0, k) - expm(s * A0), 2) for k in terms]) for s in (1, 5, 20)}
    w_, V_ = np.linalg.eig(A0)
    via_eig = (V_ @ np.diag(np.exp(w_)) @ np.linalg.inv(V_)).real
    via_ode = solve_ivp(lambda t, y: (A0 @ y.reshape(4, 4)).ravel(), (0, 1), np.eye(4).ravel(), rtol=1e-12, atol=1e-12).y[:, -1].reshape(4, 4)
    Xs2 = rng.normal(size=(500, 2, 2)); Xs2[:, 1, 1] = -Xs2[:, 0, 0]
    def exp_sl2(X):
        d = -np.linalg.det(X) + 0j
        r = np.sqrt(d)
        return np.real(np.cosh(r) * np.eye(2) + (np.sinh(r) / r if abs(r) > 1e-12 else 1) * X)
    err_sl2 = max(np.abs(exp_sl2(X) - expm(X)).max() for X in Xs2)
    w3 = rng.normal(size=3)
    X1, Y1 = rng.normal(size=(2, 3, 3))

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.6))
    ax = axes[0]
    for s, c in zip(taylor_err, ("C0", "C1", "C2")):
        ax.semilogy(terms, taylor_err[s] + 1e-17, color=c, label=f"‖X‖ = {s}")
    ax.set_xlabel("Zahl der Terme der Taylor-Reihe")
    ax.set_ylabel("Fehler ‖Reihe − expm‖")
    ax.set_title("Taylor-Reihe: erst Anstieg, dann Konvergenz, am Ende Rundung", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[1]
    tt = np.linspace(-2.2, 2.2, 300)
    tt_ell = np.linspace(0, 2 * np.pi / np.sqrt(0.5), 300)       # eine volle Periode der Ellipse
    kinds = [("elliptisch, δ < 0", np.array([[0, 1.0], [-0.5, 0]]), [(0.6, 0), (1.2, 0)], "C0"),
             ("parabolisch, δ = 0", np.array([[0, 1.0], [0, 0]]), [(0, 0.4), (0, -0.8)], "C1"),
             ("hyperbolisch, δ > 0", np.array([[0.7, 0], [0, -0.7]]), [(0.3, 0.9), (-0.5, -0.6)], "C2")]
    for lab, X, starts, c in kinds:
        for k, p in enumerate(starts):
            orb = np.array([expm(s * X) @ np.array(p) for s in (tt_ell if lab.startswith("ell") else tt)])
            ax.plot(orb[:, 0], orb[:, 1], color=c, label=lab if k == 0 else None)
            ax.plot(*p, "o", color=c, ms=4)
    ax.set_xlim(-2.5, 2.5); ax.set_ylim(-2, 2); ax.set_aspect("equal")
    ax.set_xlabel("x"); ax.set_ylabel("y")
    ax.set_title("Bahnen von e^(tX) in SL(2,ℝ): Ellipse, Gerade, Hyperbel", fontsize=10)
    ax.legend(fontsize=8, loc="upper left")
    ax = axes[2]
    phi0 = np.arctanh(0.5)
    K = np.array([[0, 1.0], [1, 0]])
    nb = np.arange(1, 11)
    boost = [np.linalg.matrix_power(expm(phi0 * K), k) for k in nb]
    v_rel = np.array([B[1, 0] / B[0, 0] for B in boost])
    ax.plot(nb, 0.5 * nb, "s--", label="Galilei: v = n · 0.5c")
    ax.plot(nb, v_rel, "o-", label="Lorentz: n Boosts hintereinander")
    ax.plot(nb, np.tanh(nb * phi0), "k:", label="tanh(n · artanh 0.5)")
    ax.axhline(1, color="grey", lw=0.8)
    ax.set_ylim(0, 2.2)
    ax.set_xlabel("Zahl n der Boosts mit je 0.5c")
    ax.set_ylabel("Gesamtgeschwindigkeit / c")
    ax.set_title("Rapiditäten addieren sich: e^(φK)ⁿ = e^(nφK)", fontsize=10)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    for s in taylor_err:
        ok = taylor_err[s] < 1e-10
        reach = f"ab {int(terms[np.argmax(ok)])} Termen" if ok.any() else "nie"
        print(f"‖X‖ = {s:2d}: größter Term ‖X‖ᵏ/k! = {max(s ** k / factorial(k) for k in range(60)):.1e}, Fehler < 1e-10: {reach}, "
              f"bester Fehler {taylor_err[s].min():.1e} (nach {int(terms[np.argmin(taylor_err[s])])} Termen)")
    print(f"Vier Wege für ‖X‖ = 1: |Taylor(30) − expm| = {np.abs(exp_taylor(A0, 30) - expm(A0)).max():.1e}, |Eigenzerlegung − expm| = "
          f"{np.abs(via_eig - expm(A0)).max():.1e}, |Differentialgleichung − expm| = {np.abs(via_ode - expm(A0)).max():.1e}")
    print(f"Formel cosh√δ·1 + sinh√δ/√δ·X für 500 zufällige X ∈ sl(2,ℝ): größte Abweichung {err_sl2:.1e};  Rodrigues gegen expm: {np.abs(rodrigues(w3) - expm(hat(w3))).max():.1e}")
    print(f"det e^X = e^(tr X): {np.linalg.det(expm(X1)):.6f} = {np.exp(np.trace(X1)):.6f};  e^(sX)e^(tX) = e^((s+t)X): {np.allclose(expm(0.3 * X1) @ expm(0.9 * X1), expm(1.2 * X1))};  "
          f"e^(X+Y) = e^X e^Y für nicht vertauschende X, Y: {np.allclose(expm(X1 + Y1), expm(X1) @ expm(Y1))}")
    print(f"Zwei Boosts mit 0.5c: {v_rel[1]:.4f}c (Formel (0.5 + 0.5)/(1 + 0.25) = 0.8c), zehn Boosts: {v_rel[-1]:.6f}c")


def exp_limits():
    """54. Grenzen der Exponentialabbildung: Surjektivität und Logarithmus (Zellen 12 von lie.ipynb)."""
    global Jrot, L, L_target, U_haar, Xs3, antiherm, ax, axes, dd, delta3, fig, log_err
    global product, recovered, rng, target, th, thetas, tr3, tr_formula
    rng = np.random.default_rng(3)
    Xs3 = rng.normal(scale=1.5, size=(20000, 2, 2)); Xs3[:, 1, 1] = -Xs3[:, 0, 0]
    delta3 = -np.linalg.det(Xs3)
    tr3 = np.array([np.trace(expm(X)) for X in Xs3])
    dd = np.linspace(delta3.min(), delta3.max(), 600)
    tr_formula = np.where(dd >= 0, 2 * np.cosh(np.sqrt(np.abs(dd))), 2 * np.cos(np.sqrt(np.abs(dd))))
    target = np.diag([-2.0, -0.5])
    L_target = logm(target)
    Jrot = np.array([[0, 1.0], [-1, 0]])
    product = expm(np.pi * Jrot) @ expm(np.diag([np.log(2), -np.log(2)]))
    thetas = np.linspace(0.01, 2 * np.pi - 0.01, 300)
    recovered = []
    for th in thetas:
        L = logm(rodrigues([0, 0, th])).real
        recovered.append(np.linalg.norm([L[2, 1], L[0, 2], L[1, 0]]))
    recovered = np.array(recovered)
    U_haar = stats.unitary_group.rvs(4, size=200, random_state=rng)
    log_err = max(np.abs(expm(logm(U)) - U).max() for U in U_haar)
    antiherm = max(np.abs(logm(U) + logm(U).conj().T).max() for U in U_haar)

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
    ax = axes[0]
    ax.scatter(delta3, tr3, s=2, alpha=0.3, label="tr e^X für 20 000 zufällige X ∈ sl(2,ℝ)")
    ax.plot(dd, tr_formula, "k-", lw=1, label="2cosh√δ bzw. 2cos√(−δ)")
    ax.axhline(-2, color="C3", ls="--", label="untere Grenze −2")
    ax.plot(0, -2.5, "r*", ms=14, label="diag(−2, −½): Spur −2.5")
    ax.set_xlim(-21, 6); ax.set_ylim(-4, 12)
    ax.set_xlabel("δ = −det X")
    ax.set_ylabel("Spur von e^X")
    ax.set_title("In SL(2,ℝ) ist die Spur eines Exponentials nie kleiner als −2", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[1]
    ax.plot(thetas, thetas, "k:", label="wahrer Drehwinkel θ")
    ax.plot(thetas, recovered, "C0-", lw=2, label="Drehwinkel aus dem Hauptwert von log R")
    ax.axvline(np.pi, color="grey", ls="--")
    ax.set_xlabel("Drehwinkel θ um die z-Achse")
    ax.set_ylabel("|log R| (Drehwinkel)")
    ax.set_title("Der Logarithmus einer Drehung springt bei θ = π auf die Gegenachse", fontsize=10)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"Kleinste Spur unter 20 000 Exponentialen: {tr3.min():.4f} (Grenze −2);  Formel und expm stimmen überein: {np.allclose(tr3, np.where(delta3 >= 0, 2 * np.cosh(np.sqrt(np.abs(delta3))), 2 * np.cos(np.sqrt(np.abs(delta3)))))}")
    print(f"logm(diag(−2, −½)) = {np.round(L_target, 4).tolist()}: reell? {np.allclose(L_target.imag, 0)}")
    print(f"Aber diag(−2, −½) = e^(πJ) · e^(diag(ln 2, −ln 2)): {np.allclose(product, target)};  e^(2πJ) = 1: {np.allclose(expm(2 * np.pi * Jrot), np.eye(2))}")
    print(f"Haar-zufällige U ∈ U(4): |e^(log U) − U| ≤ {log_err:.1e}, log U antihermitesch bis auf {antiherm:.1e}")
    print(f"Drehwinkel aus dem Logarithmus bei θ = 0.9π, 1.1π, 1.5π: {[round(float(np.interp(a * np.pi, thetas, recovered)) / np.pi, 4) for a in (0.9, 1.1, 1.5)]} · π")


def bch_formula():
    """55. Die Baker-Campbell-Hausdorff-Formel (Zellen 15 von lie.ipynb)."""
    global A, A0, B, B0, P3, Q3, Z, ax, axes, bch, bch_err, e
    global eps4, fig, heis, i1, i3, k, rng, slopes4, small
    rng = np.random.default_rng(4)
    A0, B0 = rng.normal(size=(2, 4, 4)); A0 /= np.linalg.norm(A0, 2); B0 /= np.linalg.norm(B0, 2)

    def bch(A, B, order):
        Z = A + B
        if order >= 2:
            Z = Z + comm(A, B) / 2
        if order >= 3:
            Z = Z + (comm(A, comm(A, B)) + comm(B, comm(B, A))) / 12
        if order >= 4:
            Z = Z - comm(B, comm(A, comm(A, B))) / 24
        return Z

    eps4 = np.logspace(-3, 0.5, 36)
    bch_err = {k: [] for k in (1, 2, 3, 4)}
    for e in eps4:
        A, B = e * A0, e * B0
        Z = logm(expm(A) @ expm(B))
        for k in bch_err:
            bch_err[k].append(np.linalg.norm(Z - bch(A, B, k), 2))
    bch_err = {k: np.array(v) for k, v in bch_err.items()}
    slopes4 = {}
    for k in bch_err:
        small = (eps4 < 0.1) & (bch_err[k] > 1e-12)          # unterhalb von 1e-12 begrenzt die Rundung in logm
        slopes4[k] = np.polyfit(np.log(eps4[small]), np.log(bch_err[k][small]), 1)[0]
    P3 = np.zeros((3, 3)); P3[0, 1] = 1
    Q3 = np.zeros((3, 3)); Q3[1, 2] = 1
    heis = {k: [] for k in (1, 2)}
    for e in eps4:
        A, B = e * 1.3 * P3, e * 0.8 * Q3
        Z = logm(expm(A) @ expm(B)).real
        for k in heis:
            heis[k].append(np.linalg.norm(Z - bch(A, B, k), 2))

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
    ax = axes[0]
    for k in bch_err:
        ax.loglog(eps4, bch_err[k] + 1e-17, "o-", ms=3, label=f"bis Ordnung {k}: Steigung {slopes4[k]:.2f}")
    ax.axvline(np.log(2) / 2, color="grey", ls=":", label="‖A‖ + ‖B‖ = ln 2")
    ax.set_xlabel("ε  (‖A‖ = ‖B‖ = ε)")
    ax.set_ylabel("Fehler ‖log(e^A e^B) − BCH‖")
    ax.set_title("BCH-Reihe für zufällige 4×4-Matrizen", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[1]
    ax.loglog(eps4, np.array(heis[1]) + 1e-17, "o-", ms=3, label="A + B")
    ax.loglog(eps4, np.array(heis[2]) + 1e-17, "s-", ms=3, label="A + B + ½[A, B]")
    ax.set_xlabel("ε")
    ax.set_ylabel("Fehler")
    ax.set_title("Heisenberg-Algebra: die Reihe bricht nach ½[A, B] ab", fontsize=10)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print("Steigungen für ε < 0.1, Fehler > 1e-12 (Theorie: Ordnung + 1):", {k: round(float(v), 3) for k, v in slopes4.items()})
    i1 = np.argmin(np.abs(eps4 - 0.1)); i3 = np.argmin(np.abs(eps4 - 2.0))
    print(f"Fehler bei ε = {eps4[i1]:.3f}: {[f'{bch_err[k][i1]:.1e}' for k in bch_err]};  bei ε = {eps4[i3]:.2f}: {[f'{bch_err[k][i3]:.1e}' for k in bch_err]}")
    print(f"Heisenberg: größter Fehler mit ½[A, B] {max(heis[2]):.1e}, ohne {max(heis[1]):.1e};  [A, B] vertauscht mit A und B: "
          f"{np.allclose(comm(P3, comm(P3, Q3)), 0) and np.allclose(comm(Q3, comm(P3, Q3)), 0)}")


def trotter_formulas():
    """56. Trotter-Produktformeln: Quantensimulation mit einfachen Bausteinen (Zellen 18 von lie.ipynb)."""
    global A_diag, B_op, H_tfim, S2, S4, U_exact, Zs, axes, comm_norm, cost, eA, eB
    global f, fig, h_field, i10, i20, n_q, name, need, ok, p_s, steps, t_sim
    global terr, trotter, tslopes
    n_q, h_field, t_sim = 8, 1.0, 2.0
    Zs = [site_op(PZ, i, n_q) for i in range(n_q)]
    A_diag = -np.real(sum(np.diag(Zs[i] @ Zs[i + 1]) for i in range(n_q - 1)))
    B_op = -h_field * sum(site_op(PX, i, n_q) for i in range(n_q))
    H_tfim = np.diag(A_diag) + B_op
    U_exact = expm(-1j * H_tfim * t_sim)
    eA = lambda tau: np.diag(np.exp(-1j * A_diag * tau))
    def eB(tau):
        r = np.cos(h_field * tau) * np.eye(2) + 1j * np.sin(h_field * tau) * PX   # e^{+i h τ X}, weil B = −h ΣX
        out = np.array([[1.0 + 0j]])
        for _ in range(n_q):
            out = np.kron(out, r)
        return out
    S2 = lambda tau: eA(tau / 2) @ eB(tau) @ eA(tau / 2)
    p_s = 1 / (4 - 4 ** (1 / 3))
    S4 = lambda tau: S2(p_s * tau) @ S2(p_s * tau) @ S2((1 - 4 * p_s) * tau) @ S2(p_s * tau) @ S2(p_s * tau)
    steps = np.array([1, 2, 3, 4, 5, 7, 10, 14, 20, 28, 40, 56, 80, 100, 140, 200, 280, 400, 560, 800, 1000])
    trotter = {"1. Ordnung (Lie-Trotter)": (lambda n: np.linalg.matrix_power(eA(t_sim / n) @ eB(t_sim / n), n), lambda n: 2 * n),
               "2. Ordnung (Strang)": (lambda n: np.linalg.matrix_power(S2(t_sim / n), n), lambda n: 2 * n + 1),
               "4. Ordnung (Suzuki)": (lambda n: np.linalg.matrix_power(S4(t_sim / n), n), lambda n: 10 * n + 1)}
    terr = {name: np.array([np.linalg.norm(f(n) - U_exact, 2) for n in steps]) for name, (f, _) in trotter.items()}
    comm_norm = np.linalg.norm(comm(np.diag(A_diag), B_op), 2)
    tslopes = {}
    for name in terr:
        ok = (terr[name] > 1e-11) & (steps >= 4)
        tslopes[name] = np.polyfit(np.log(steps[ok]), np.log(terr[name][ok]), 1)[0]

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
    for name, (f, cost) in trotter.items():
        axes[0].loglog(steps, terr[name], "o-", ms=3, label=f"{name}: Steigung {tslopes[name]:.2f}")
        axes[1].loglog([cost(n) for n in steps], terr[name], "o-", ms=3, label=name)
    axes[0].loglog(steps, t_sim ** 2 / (2 * steps) * comm_norm, "k:", label="Schranke t²‖[A,B]‖/(2n)")
    axes[0].set_xlabel("Zahl der Trotter-Schritte n")
    axes[0].set_ylabel("Fehler ‖U_n − e^(−iHt)‖")
    axes[0].set_title("Ising-Kette, 8 Qubits, t = 2", fontsize=10)
    axes[0].legend(fontsize=8)
    axes[1].set_xlabel("Zahl der Exponentialfaktoren (Schaltkreislänge)")
    axes[1].set_ylabel("Fehler")
    axes[1].set_title("Für hohe Genauigkeit gewinnt die Formel 4. Ordnung", fontsize=10)
    axes[1].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print("Steigungen:", {k: round(float(v), 2) for k, v in tslopes.items()})
    for name, (f, cost) in trotter.items():
        i10, i20 = list(steps).index(10), list(steps).index(20)
        need = next((cost(n) for n, e in zip(steps, terr[name]) if e < 1e-6), None)
        need = need if need is not None else f"mehr als {cost(steps[-1])} (bei n = 1000 noch {terr[name][-1]:.1e})"
        print(f"{name:26s} n = 10: {terr[name][i10]:.2e}, n = 20: {terr[name][i20]:.2e} (Faktor {terr[name][i10] / terr[name][i20]:.1f});  Faktoren für Fehler < 1e-6: {need}")
    print(f"‖[A, B]‖ = {comm_norm:.2f};  Schranke 1. Ordnung bei n = 100: {t_sim ** 2 / 200 * comm_norm:.3f}, gemessen {terr['1. Ordnung (Lie-Trotter)'][list(steps).index(100)]:.3f}")


def integrators():
    """57. Lie-Gruppen-Integratoren: Drehbewegungen, ohne die Gruppe zu verlassen (Zellen 21 von lie.ipynb)."""
    global R_exact6, Rex, a6, axes, b6, e, err6, fig, h6, half6, integrate6, methods6
    global name, omega6, orth6, paths6, rk4_step, t6, w2
    a6, b6 = np.array([0.6, 0.0, 0.8]), np.array([0.0, 0.0, 1.5])
    omega6 = lambda t: rodrigues(-t * b6) @ a6 + b6
    R_exact6 = lambda t: rodrigues(t * a6) @ rodrigues(t * b6)

    def integrate6(step, h, T=30.0):
        R, out = np.eye(3), []
        for k in range(int(round(T / h))):
            R = step(R, k * h, h)
            out.append(R)
        return np.array(out)

    def rk4_step(R, t, h):
        f = lambda s, M: M @ hat(omega6(s))
        k1 = f(t, R); k2 = f(t + h / 2, R + h / 2 * k1); k3 = f(t + h / 2, R + h / 2 * k2); k4 = f(t + h, R + h * k3)
        return R + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)

    methods6 = {"explizites Euler-Verfahren": lambda R, t, h: R + h * R @ hat(omega6(t)),
                "Runge-Kutta 4": rk4_step,
                "Lie-Euler: R·exp(h[ω(t)])": lambda R, t, h: R @ rodrigues(h * omega6(t)),
                "Lie-Mittelpunkt: R·exp(h[ω(t + h/2)])": lambda R, t, h: R @ rodrigues(h * omega6(t + h / 2))}
    h6 = 0.01
    t6 = h6 * np.arange(1, 3001)
    Rex = np.array([R_exact6(t) for t in t6])
    paths6 = {name: integrate6(f, h6) for name, f in methods6.items()}
    orth6 = {name: np.linalg.norm(np.transpose(P, (0, 2, 1)) @ P - np.eye(3), axis=(1, 2)) for name, P in paths6.items()}
    err6 = {name: np.linalg.norm(P - Rex, axis=(1, 2)) for name, P in paths6.items()}
    half6 = {name: np.linalg.norm(integrate6(methods6[name], h6 / 2)[-1] - Rex[-1]) for name in list(methods6)[2:]}

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
    for name in methods6:
        axes[0].semilogy(t6, orth6[name] + 1e-17, label=name)
        axes[1].semilogy(t6, err6[name] + 1e-17, label=name)
    axes[0].set_xlabel("Zeit t (s)")
    axes[0].set_ylabel("Abstand von SO(3): ‖RᵀR − 1‖")
    axes[0].set_title("Nur die Lie-Verfahren bleiben in der Drehgruppe", fontsize=10)
    axes[0].legend(fontsize=8)
    axes[1].set_xlabel("Zeit t (s)")
    axes[1].set_ylabel("Fehler ‖R − R_exakt‖")
    axes[1].set_title("Fehler gegen die exakte Taumelbewegung, h = 0.01 s", fontsize=10)
    axes[1].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"|ω| = {np.linalg.norm(omega6(0)):.3f} rad/s für alle t (Schwankung {np.ptp([np.linalg.norm(omega6(t)) for t in t6]):.0e}); nur die Richtung im Körper ändert sich")
    for name in methods6:
        print(f"{name:40s} nach 30 s: Abstand von SO(3) {orth6[name][-1]:.1e}, Fehler {err6[name][-1]:.1e}, det R = {np.linalg.det(paths6[name][-1]):.6f}")
    for name, e in half6.items():
        print(f"{name:40s} halbe Schrittweite: Fehler {e:.2e}, Verhältnis {err6[name][-1] / e:.2f}")
    w2 = np.linalg.norm(omega6(0)) ** 2
    print(f"Euler: det R wächst pro Schritt um 1 + h²|ω|²; Vorhersage (1 + h²|ω|²)^3000 = {(1 + h6 ** 2 * w2) ** 3000:.3f}, gemessen {np.linalg.det(paths6['explizites Euler-Verfahren'][-1]):.3f}; "
          f"Singulärwerte {np.round(np.linalg.svd(paths6['explizites Euler-Verfahren'][-1], compute_uv=False), 3).tolist()}")


def killing_form():
    """58. Strukturkonstanten, adjungierte Darstellung und Killing-Form (Zellen 24 von lie.ipynb)."""
    global Ad_err, E, Kf, Th, V7, Xr, _, ad, adT, ad_su3, algebras, ax
    global axes, basis, c, centre, coef, d, ev, fig, info7, jac, k, lab
    global lam, left, m_, name, names7, nonzero, p_, r, rng, roots7, series, sig
    global sig_arr, span_basis, tol, w7, xs7, z_
    def span_basis(mats, tol=1e-9):
        if len(mats) == 0:
            return []
        M = np.array([m.ravel() for m in mats])
        _, s, vh = np.linalg.svd(M, full_matrices=False)
        r = int(np.sum(s > tol * max(1.0, s[0])))
        return [vh[k].reshape(mats[0].shape) for k in range(r)]

    def series(basis, kind):
        """Dimensionen der abgeleiteten Reihe ('derived') oder der absteigenden Zentralreihe ('lower')."""
        g = span_basis(basis)
        cur, dims_ = g, [len(g)]
        for _ in range(6):
            new = span_basis([comm(a, b) for a, b in itertools.combinations(cur, 2)] if kind == "derived" else [comm(a, b) for a in g for b in cur])
            if len(new) == len(cur):
                break
            cur = new
            dims_.append(len(cur))
            if not cur:
                break
        return dims_

    E = lambda i, j, n: np.eye(n)[:, [i]] @ np.eye(n)[[j], :]
    lam = gell_mann()
    algebras = {
        "so(3)": [hat(v) for v in np.eye(3)],
        "su(2)": [-0.5j * P for P in (PX, PY, PZ)],
        "su(3)": [-0.5j * l for l in lam],
        "so(4)": [E(i, j, 4) - E(j, i, 4) for i, j in itertools.combinations(range(4), 2)],
        "sl(2,ℝ)": [np.diag([1.0, -1]), E(0, 1, 2), E(1, 0, 2)],
        "so(1,3)": [E(i, j, 4) - E(j, i, 4) for i, j in itertools.combinations(range(1, 4), 2)] + [E(0, i, 4) + E(i, 0, 4) for i in range(1, 4)],
        "se(2)": [E(1, 0, 3) - E(0, 1, 3), E(0, 2, 3), E(1, 2, 3)],
        "aff(1)": [E(0, 0, 2), E(0, 1, 2)],
        "h₃ (Heisenberg)": [E(0, 1, 3), E(1, 2, 3), E(0, 2, 3)],
    }
    info7 = {}
    for name, basis in algebras.items():
        Kf, ad = killing(basis)
        ev = np.linalg.eigvalsh(Kf)
        tol = 1e-9 * max(1, np.abs(ev).max())
        sig = (int(np.sum(ev > tol)), int(np.sum(ev < -tol)), int(np.sum(np.abs(ev) <= tol)))
        jac = max(np.abs(comm(x, comm(y, z)) + comm(y, comm(z, x)) + comm(z, comm(x, y))).max() for x, y, z in itertools.combinations(basis, 3)) if len(basis) >= 3 else 0.0
        centre = len(basis) - np.linalg.matrix_rank(np.array([a.ravel() for a in ad]).T, tol=1e-9)
        info7[name] = dict(dim=len(basis), sig=sig, jac=jac, derived=series(basis, "derived"), lower=series(basis, "lower"), centre=centre)

    Th = lam / 2                                         # hermitesche Basis: [T_a, T_b] = i f_abc T_c
    _, adT = killing(list(Th))
    w7, V7 = np.linalg.eigh(adT[2] + 0.37 * adT[7])
    roots7 = np.array([[np.real(v.conj() @ adT[2] @ v), np.real(v.conj() @ adT[7] @ v)] for v in V7.T])
    rng = np.random.default_rng(7)
    xs7 = rng.normal(size=8)
    Xr = sum(x * b for x, b in zip(xs7, algebras["su(3)"]))
    _, ad_su3 = killing(algebras["su(3)"])
    coef = lambda M: np.real(np.linalg.lstsq(np.array([b.ravel() for b in algebras["su(3)"]]).T, M.ravel(), rcond=None)[0])
    Ad_err = max(np.abs(coef(expm(Xr) @ Y @ expm(-Xr)) - expm(np.real(np.tensordot(xs7, ad_su3, axes=(0, 0)))) @ np.eye(8)[k]).max() for k, Y in enumerate(algebras["su(3)"]))

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8), gridspec_kw={"width_ratios": [1, 1.3]})
    ax = axes[0]
    nonzero = np.linalg.norm(roots7, axis=1) > 1e-6
    for r in roots7[nonzero]:
        ax.annotate("", xy=r, xytext=(0, 0), arrowprops=dict(arrowstyle="->", color="C0", lw=1.8))
    ax.plot(*roots7[nonzero].T, "o", color="C0", label="Wurzeln: Eigenwerte ≠ 0")
    ax.plot(0, 0, "s", color="C3", ms=9, label=f"Eigenwert 0, {int(np.sum(~nonzero))}-fach (T₃ und T₈)")
    for r in roots7[nonzero]:
        ax.text(r[0] * 1.15, r[1] * 1.15 + (0.12 if abs(r[1]) < 1e-6 else 0.08 * np.sign(r[1])), f"({r[0]:.2f}, {r[1]:.2f})", ha="center", va="center", fontsize=7)
    ax.set_aspect("equal"); ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.3, 1.3)
    ax.set_xlabel("Eigenwert von ad(T₃)")
    ax.set_ylabel("Eigenwert von ad(T₈)")
    ax.set_title("su(3): gleichzeitige Eigenwerte von ad(T₃), ad(T₈)", fontsize=10)
    ax.legend(fontsize=8, loc="lower right")
    ax = axes[1]
    names7 = list(info7)
    sig_arr = np.array([info7[n]["sig"] for n in names7])
    left = np.zeros(len(names7))
    for k, (lab, c) in enumerate([("positiv", "C3"), ("negativ", "C0"), ("null", "lightgrey")]):
        ax.barh(names7, sig_arr[:, k], left=left, color=c, label=lab)
        left += sig_arr[:, k]
    ax.invert_yaxis()
    ax.set_xlabel("Zahl der Eigenwerte der Killing-Form")
    ax.set_title("Signatur der Killing-Form", fontsize=10)
    ax.legend(fontsize=8, loc="lower right")
    plt.tight_layout()
    plt.show()

    print(f"{'Algebra':16s} dim  Signatur (+,−,0)  halbeinfach  kompakt  abgeleitete Reihe  Zentralreihe  Zentrum  Jacobi-Fehler")
    for name, d in info7.items():
        p_, m_, z_ = d["sig"]
        print(f"{name:16s} {d['dim']:3d}  {str(d['sig']):17s} {str(z_ == 0):11s}  {str(z_ == 0 and p_ == 0):7s}  {str(d['derived']):18s} {str(d['lower']):13s} {d['centre']:6d}   {d['jac']:.0e}")
    print("Wurzeln von su(3) (Eigenwerte von ad T₃, ad T₈):", sorted(map(tuple, np.round(roots7[nonzero], 4))))
    print(f"Ad(e^X) = e^(ad X) in su(3): größte Abweichung {Ad_err:.1e};  Killing-Form von su(3) in der Basis −iλ/2: Diagonale {np.round(np.diag(killing(algebras['su(3)'])[0]), 6).tolist()}")


def root_systems():
    """59. Wurzelsysteme, Dynkin-Diagramme und E₈ (Zellen 27 von lie.ipynb)."""
    global Cox, E8s, F4_simple, G8, R8, R_, S_, Vc, W_, Wd, _, a
    global ax, cartan, degrees, dg, dim, dmax, dynkin, fig, gs, hh, is_simple, k
    global name, nb_i, nb_j, nr, plane, r, rad8, rank2, reflect, root_system, s, same
    global sc, segs, sym_simple, sympy_F4, t, table8, vc, wc, weyl_order, xy8
    def reflect(v, a):
        return v - 2 * (v @ a) / (a @ a) * a

    def root_system(simple):
        simple = [np.asarray(a, float) for a in simple]
        roots = {tuple(np.round(a, 9)) for a in simple}
        frontier = list(roots)
        while frontier:
            new = []
            for r in frontier:
                for a in simple:
                    s = tuple(np.round(reflect(np.array(r), a), 9))
                    if s not in roots:
                        roots.add(s); new.append(s)
            frontier = new
        return np.array(sorted(roots))

    def cartan(simple):
        S = np.asarray(simple, float)
        return np.round(2 * (S @ S.T) / np.diag(S @ S.T)[None, :]).astype(int)      # a_ij = 2(α_i, α_j)/(α_j, α_j), wie in sympy

    def weyl_order(simple):
        """Größe der Bahn eines allgemeinen Vektors unter den einfachen Spiegelungen = |W|."""
        simple = [np.asarray(a, float) for a in simple]
        v0 = np.array([np.sqrt(k + 2) + 0.1 * k * k for k in range(len(simple[0]))])
        seen, frontier = {tuple(np.round(v0, 7))}, [v0]
        while frontier:
            new = []
            for v in frontier:
                for a in simple:
                    w = reflect(v, a)
                    key = tuple(np.round(w, 7))
                    if key not in seen:
                        seen.add(key); new.append(w)
            frontier = new
        return len(seen)

    F4_simple = [np.array([0, 1, -1, 0.]), np.array([0, 0, 1, -1.]), np.array([0, 0, 0, 1.]), np.array([0.5, -0.5, -0.5, -0.5])]
    def sym_simple(t):
        """Einfache Wurzeln aus sympy; für F₄ von Hand, weil sympy 1.14 dort Wurzeln liefert, die nicht zu seiner eigenen Cartan-Matrix passen."""
        if t == "F4":
            return F4_simple
        return [np.array(CartanType(t).simple_root(i + 1), dtype=float) for i in range(CartanType(t).rank())]
    sympy_F4 = [np.array(CartanType("F4").simple_root(i + 1), dtype=float) for i in range(4)]
    degrees = {"A4": [2, 3, 4, 5], "B4": [2, 4, 6, 8], "C4": [2, 4, 6, 8], "D5": [2, 4, 5, 6, 8], "G2": [2, 6], "F4": [2, 6, 8, 12],
               "E6": [2, 5, 6, 8, 9, 12], "E7": [2, 6, 8, 10, 12, 14, 18], "E8": [2, 8, 12, 14, 18, 20, 24, 30]}
    table8 = []
    for t, dg in degrees.items():
        S_ = sym_simple(t)
        R_ = root_system(S_)
        W_ = weyl_order(S_) if len(S_) <= 6 else None
        table8.append((t, len(S_), len(R_), len(R_) + len(S_), W_, int(np.prod(dg)), len(R_) // len(S_), max(dg),
                       np.array_equal(cartan(S_), np.array(CartanType(t).cartan_matrix().tolist(), dtype=int)), cartan(S_)))
    rank2 = {"A₁×A₁ (so(4))": [[1, 0], [0, 1]], "A₂ (su(3))": [[1, 0], [-0.5, np.sqrt(3) / 2]],
             "B₂ (so(5))": [[1, -1], [0, 1]], "G₂": [[1, 0], [-1.5, np.sqrt(3) / 2]]}
    E8s = sym_simple("E8")
    R8 = root_system(E8s)
    Cox = np.eye(8)
    for a in E8s:
        Cox = Cox @ (np.eye(8) - 2 * np.outer(a, a) / (a @ a))
    wc, Vc = np.linalg.eig(Cox)
    vc = Vc[:, np.argmin(np.abs(wc - np.exp(2j * np.pi / 30)))]
    plane, _ = np.linalg.qr(np.c_[vc.real, vc.imag])
    xy8 = R8 @ plane
    rad8 = np.round(np.hypot(*xy8.T), 6)
    G8 = R8 @ R8.T
    nb_i, nb_j = np.where(np.triu(np.isclose(G8, 1)))

    def dynkin(ax, C, x0, y0, name, dx=0.55):
        r = len(C)
        adj = {i: [j for j in range(r) if j != i and C[i][j] != 0] for i in range(r)}
        def bfs(s):
            dist, prev, q = {s: 0}, {s: None}, [s]
            for u in q:
                for v in adj[u]:
                    if v not in dist:
                        dist[v], prev[v] = dist[u] + 1, u
                        q.append(v)
            return max(dist, key=dist.get), prev
        a_, _ = bfs(0)
        b_, prev = bfs(a_)
        path = [b_]
        while prev[path[-1]] is not None:
            path.append(prev[path[-1]])
        pos = {v: (x0 + k * dx, y0) for k, v in enumerate(path)}
        for v in range(r):
            if v not in pos:
                u = next(w for w in adj[v] if w in pos)
                pos[v] = (pos[u][0], y0 - 0.45)
        for i, j in itertools.combinations(range(r), 2):
            lines = C[i][j] * C[j][i]
            if lines == 0:
                continue
            (xa, ya), (xb, yb) = pos[i], pos[j]
            for o in np.linspace(-0.06, 0.06, lines) if lines > 1 else [0]:
                ax.plot([xa, xb], [ya + o, yb + o], "k-", lw=1)
            if lines > 1:
                src, dst = (pos[i], pos[j]) if abs(C[i][j]) > abs(C[j][i]) else (pos[j], pos[i])
                mx, my = (src[0] + dst[0]) / 2, (src[1] + dst[1]) / 2
                sgn = np.sign(dst[0] - src[0]) or 1
                ax.plot([mx - 0.07 * sgn, mx + 0.05 * sgn, mx - 0.07 * sgn], [my + 0.12, my, my - 0.12], "k-", lw=1.2)
        for v, (px, py) in pos.items():
            ax.plot(px, py, "o", ms=8, mfc="white", mec="k")
        ax.text(x0 - 0.35, y0, name, ha="right", va="center", fontsize=10)

    fig = plt.figure(figsize=(18, 10))
    gs = fig.add_gridspec(2, 4, height_ratios=[1, 1.45])
    for k, (name, s) in enumerate(rank2.items()):
        ax = fig.add_subplot(gs[0, k])
        R_ = root_system(s)
        for r in R_:
            ax.plot([-1.9 * r[1], 1.9 * r[1]], [1.9 * r[0], -1.9 * r[0]], color="lightgrey", lw=0.6, zorder=0)
            is_simple = any(np.allclose(r, si) for si in np.asarray(s, float))
            ax.annotate("", xy=r, xytext=(0, 0), arrowprops=dict(arrowstyle="->", color="C3" if is_simple else "C0", lw=2 if is_simple else 1.3))
        ax.plot([], [], color="C3", lw=2, label="einfache Wurzeln")
        ax.plot([], [], color="lightgrey", lw=0.6, label="Spiegelebenen")
        ax.set_xlim(-2, 2); ax.set_ylim(-2, 2); ax.set_aspect("equal")
        ax.set_title(f"{name}: {len(R_)} Wurzeln, Weyl-Gruppe {weyl_order(s)}", fontsize=10)
        ax.set_xlabel("x"); ax.set_ylabel("y")
        ax.legend(fontsize=7, loc="lower left")
    ax = fig.add_subplot(gs[1, :2])
    segs = np.stack([xy8[nb_i], xy8[nb_j]], axis=1)
    ax.add_collection(LineCollection(segs, colors="grey", linewidths=0.15, alpha=0.35))
    sc = ax.scatter(*xy8.T, c=rad8, cmap="viridis", s=18, zorder=3)
    ax.set_aspect("equal"); ax.autoscale()
    ax.set_xlabel("Koordinate 1 der Coxeter-Ebene"); ax.set_ylabel("Koordinate 2")
    ax.set_title(f"E₈: {len(R8)} Wurzeln projiziert, Kanten zwischen Wurzeln mit Skalarprodukt 1 ({len(nb_i)})", fontsize=10)
    plt.colorbar(sc, ax=ax, shrink=0.8, label="Abstand vom Mittelpunkt")
    ax = fig.add_subplot(gs[1, 2:])
    for k, t in enumerate(["A4", "B4", "C4", "D5"]):
        dynkin(ax, cartan(sym_simple(t)), 0.6, -1.25 * k, f"{t[0]}{chr(0x2080 + int(t[1]))}")
    for k, t in enumerate(["G2", "F4", "E6", "E7", "E8"]):
        dynkin(ax, cartan(sym_simple(t)), 4.0, -1.0 * k, f"{t[0]}{chr(0x2080 + int(t[1]))}")
    ax.set_xlim(-0.6, 8.3); ax.set_ylim(-4.8, 0.5)
    ax.set_axis_off()
    ax.set_title("Dynkin-Diagramme aus den berechneten Cartan-Matrizen (Pfeil zur kürzeren Wurzel)", fontsize=10)
    plt.tight_layout()
    plt.show()

    print("Typ  Rang  Wurzeln  Dimension  |W| (Bahn)   Produkt der Grade  h = Wurzeln/Rang  größter Grad  Cartan-Matrix = sympy")
    for t, r, nr, dim, W_, Wd, hh, dmax, same, _ in table8:
        print(f"{t:4s} {r:4d} {nr:8d} {dim:10d}  {('–' if W_ is None else f'{W_:,}'.replace(',', ' ')):>11s}  {f'{Wd:,}'.replace(',', ' '):>17s} {hh:17d} {dmax:13d}   {same}")
    print(f"E₈: Längenquadrate {sorted(set(np.round(np.sum(R8 ** 2, axis=1), 6)))}, Skalarprodukte {sorted(set(np.round(G8.ravel(), 6)))}, Nachbarn pro Wurzel {int(np.isclose(G8, 1).sum(axis=1)[0])}")
    print(f"Eigenwerte des Coxeter-Elements: e^(2πi·m/30) mit m = {sorted(int(round(a)) % 30 for a in np.angle(wc) * 30 / (2 * np.pi))}")
    print(f"Projektion: {len(set(rad8))} Ringe mit je {sorted(set(np.unique(rad8, return_counts=True)[1].tolist()))} Wurzeln")
    print("Cartan-Matrix von G₂:", table8[4][-1].tolist(), " von F₄:", table8[5][-1].tolist())
    print(f"sympy-Wurzeln für F₄: Cartan-Matrix {cartan(sympy_F4).tolist()}, {len(root_system(sympy_F4))} Wurzeln statt 48")


def dynamical_lie_algebras():
    """60. Dynamische Lie-Algebren: Was ein Quantenschaltkreis erreicht und wo Barren Plateaus entstehen (Zellen 30 von lie.ipynb)."""
    global _, ax, axes, c, chain, depth6, dla_dims, dla_sets, f, fig, gate_data, gens
    global key, lie_closure, mk, n, name, ns9, ns_var, parity, pauli, random_circuits, rng, theo9
    global v, var9, var_theory
    def parity(v):
        v = np.array(v, dtype=np.int64)
        for s in (32, 16, 8, 4, 2, 1):
            v = v ^ (v >> s)
        return v & 1

    def pauli(s):
        """'XZIY' → (x, z) als Bitmasken; Qubit k ist Bit k. X: x = 1, Z: z = 1, Y: beide."""
        return sum(1 << k for k, c in enumerate(s) if c in "XY"), sum(1 << k for k, c in enumerate(s) if c in "ZY")

    def lie_closure(gens, n):
        """Lie-Abschluss von Pauli-Strings: antikommutieren zwei, ist ihr Kommutator (bis auf 2i) ihr Produkt (x₁⊕x₂, z₁⊕z₂)."""
        present = np.zeros(4 ** n, bool)
        X = np.array([g[0] for g in gens], np.int64); Z = np.array([g[1] for g in gens], np.int64)
        _, first = np.unique((X << n) | Z, return_index=True)
        X, Z = X[np.sort(first)], Z[np.sort(first)]
        present[(X << n) | Z] = True
        k = 0
        while k < len(X):
            anti = parity((X[k] & Z) ^ (Z[k] & X)) == 1
            cx, cz = X[anti] ^ X[k], Z[anti] ^ Z[k]
            code = (cx << n) | cz
            new = ~present[code]
            if new.any():
                code_new, idx = np.unique(code[new], return_index=True)
                present[code_new] = True
                X = np.concatenate([X, cx[new][idx]]); Z = np.concatenate([Z, cz[new][idx]])
            k += 1
        return X, Z

    def chain(n, *terms, ring=False):
        gens = []
        for t in terms:
            if len(t) == 1:
                gens += [pauli("I" * i + t + "I" * (n - i - 1)) for i in range(n)]
            else:
                gens += [pauli("I" * i + t + "I" * (n - i - 2)) for i in range(n - 1)]
                if ring and n > 2:
                    gens.append(pauli(t[1] + "I" * (n - 2) + t[0]))
        return gens

    dla_sets = {"X (ungekoppelt)": (lambda n: chain(n, "X"), lambda n: n),
                "X, Y (ungekoppelt)": (lambda n: chain(n, "X", "Y"), lambda n: 3 * n),
                "X, ZZ: Ising-Kette, Linie": (lambda n: chain(n, "X", "ZZ"), lambda n: n * (2 * n - 1)),
                "X, ZZ: Ising-Kette, Ring": (lambda n: chain(n, "X", "ZZ", ring=True), lambda n: 2 * n * (2 * n - 1) if n >= 3 else n * (2 * n - 1)),
                "X, Z, ZZ: universell": (lambda n: chain(n, "X", "Z", "ZZ"), lambda n: 4 ** n - 1)}
    ns9 = np.arange(2, 8)
    dla_dims = {name: [len(lie_closure(f(int(n)), int(n))[0]) for n in ns9] for name, (f, _) in dla_sets.items()}

    def gate_data(x, z, n):
        c = np.arange(2 ** n)
        return c ^ x, (1j) ** bin(x & z).count("1") * (-1.0) ** parity((c ^ x) & z)     # P|b⟩ = i^{|x∧z|}(−1)^{|b∧z|}|b⊕x⟩

    def random_circuits(gens, n, layers, samples, rng):
        data = [gate_data(x, z, n) for x, z in gens]
        perm_o, ph_o = gate_data(*pauli("X" + "I" * (n - 1)), n)
        psi = np.zeros((samples, 2 ** n), complex); psi[:, 0] = 1
        var_by_layer = []
        for _ in range(layers):
            for perm, ph in data:
                th = rng.uniform(0, 2 * np.pi, samples)[:, None]
                psi = np.cos(th) * psi - 1j * np.sin(th) * (ph * psi[:, perm])
            var_by_layer.append(np.real(np.sum(psi.conj() * (ph_o * psi[:, perm_o]), axis=1)).var())
        return np.array(var_by_layer)

    def var_theory(gens, n):
        X, Z = lie_closure(gens, n)
        in_g = np.any((X == pauli("X" + "I" * (n - 1))[0]) & (Z == 0))
        return np.sum(X == 0) / len(X) if in_g else np.nan          # ‖O_g‖² = 2ⁿ, ‖ρ_g‖² = (Zahl der Z-Strings in g)/2ⁿ

    rng = np.random.default_rng(9)
    ns_var = np.arange(3, 8)
    var9 = {"so(2n): X, ZZ": [], "su(2ⁿ): X, Z, ZZ": []}
    theo9 = {k: [] for k in var9}
    depth6 = {}
    for n in ns_var:
        for key, gens in (("so(2n): X, ZZ", chain(int(n), "X", "ZZ")), ("su(2ⁿ): X, Z, ZZ", chain(int(n), "X", "Z", "ZZ"))):
            v = random_circuits(gens, int(n), 16 * int(n), 1500, rng)
            var9[key].append(v[-4 * int(n):].mean())          # Mittel über das letzte Viertel der Schichten
            theo9[key].append(var_theory(gens, int(n)))
            if n == 6:
                depth6[key] = v

    fig, axes = plt.subplots(1, 3, figsize=(18, 4.7))
    ax = axes[0]
    for (name, (_, f)), mk in zip(dla_sets.items(), "osd^v"):
        ax.semilogy(ns9, dla_dims[name], mk, ms=7, label=name)
        ax.semilogy(ns9, [f(int(n)) for n in ns9], "k:", lw=0.8)
    ax.set_xlabel("Zahl der Qubits n")
    ax.set_ylabel("dim g (punktiert: Formel)")
    ax.set_title("Dimension der dynamischen Lie-Algebra", fontsize=10)
    ax.legend(fontsize=7)
    ax = axes[1]
    for key, c in zip(depth6, ("C0", "C1")):
        ax.semilogy(np.arange(1, len(depth6[key]) + 1), depth6[key], color=c, label=f"{key}, gemessen")
        ax.axhline(theo9[key][list(ns_var).index(6)], color=c, ls="--", lw=1, label=f"{key}, Formel")
    ax.set_xlabel("Zahl der Schichten")
    ax.set_ylabel("Var⟨X₁⟩ über 1500 Schaltkreise")
    ax.set_title("n = 6: Mit der Tiefe erreicht die Varianz ihr Plateau", fontsize=10)
    ax.legend(fontsize=7)
    ax = axes[2]
    for key, c in zip(var9, ("C0", "C1")):
        ax.semilogy(ns_var, var9[key], "o", color=c, ms=7, label=f"{key}, gemessen")
        ax.semilogy(ns_var, theo9[key], "-", color=c, lw=1, label=f"{key}: ‖O_g‖²‖ρ_g‖²/dim g")
    ax.set_xticks(ns_var)
    ax.set_xlabel("Zahl der Qubits n")
    ax.set_ylabel("Var⟨X₁⟩ tiefer Zufallsschaltkreise")
    ax.set_title("Kleine DLA: polynomielle Varianz; volle su(2ⁿ): exponentiell klein", fontsize=10)
    ax.legend(fontsize=7)
    plt.tight_layout()
    plt.show()

    print("dim g für n = 2 … 7:")
    for name, (_, f) in dla_sets.items():
        print(f"  {name:28s} {dla_dims[name]}   Formel {[f(int(n)) for n in ns9]}")
    print("Varianz, n = 3 … 7:")
    for key in var9:
        print(f"  {key:18s} gemessen {[f'{v:.4f}' for v in var9[key]]}")
        print(f"  {'':18s} Formel   {[f'{v:.4f}' for v in theo9[key]]}")
    print(f"Verhältnis der Varianzen bei n = 7: {var9['so(2n): X, ZZ'][-1] / var9['su(2ⁿ): X, Z, ZZ'][-1]:.1f}")


def character_tables():
    """61. Charaktertafeln endlicher Gruppen (Zellen 33 von lie.ipynb)."""
    global G, Q8, _, ax, axes, ch, chi, chi4, cl4, classes, cols, dims_
    global els, els4, fig, fmt_char, groups10, i, inv, j, lab, m, mul, n_
    global name, orders, perm_chars, perm_group_data, reps4, rows, sizes, sz4, tables10, vmax
    def perm_group_data(G):
        els = list(G.generate())
        idx = {tuple(g.array_form): i for i, g in enumerate(els)}
        return els, (lambda i, j: idx[tuple((els[i] * els[j]).array_form)]), (lambda i: idx[tuple((~els[i]).array_form)])

    def fmt_char(z):
        z = complex(z)
        gold = (1 + 5 ** 0.5) / 2
        named = {"ω": np.exp(2j * np.pi / 3), "ω²": np.exp(-2j * np.pi / 3), "φ": gold, "1−φ": 1 - gold, "i": 1j, "−i": -1j}
        for s, v in named.items():
            if abs(z - v) < 1e-8:
                return s
        if abs(z) < 1e-8:
            return "0"
        return f"{z.real:.0f}".replace("-", "−") if abs(z.imag) < 1e-8 and abs(z.real - round(z.real)) < 1e-8 else f"{z.real:.2f}"

    Q8 = PermutationGroup([Permutation([[0, 1, 2, 3], [4, 5, 6, 7]]), Permutation([[0, 4, 2, 6], [1, 7, 3, 5]])])   # i und j als Permutationen
    groups10 = {"S₃": SymmetricGroup(3), "D₄": DihedralGroup(4), "Q₈": Q8, "A₄": AlternatingGroup(4), "S₄": SymmetricGroup(4), "A₅": AlternatingGroup(5)}
    tables10 = {}
    for name, G in groups10.items():
        els, mul, inv = perm_group_data(G)
        chi, classes, sizes = character_table(len(els), mul, inv)
        orders = [els[c[0]].order() for c in classes]
        tables10[name] = (chi, classes, sizes, orders, els)

    fig, axes = plt.subplots(2, 3, figsize=(17, 9))
    for ax, (name, (chi, classes, sizes, orders, els)) in zip(axes.ravel(), tables10.items()):
        vmax = np.abs(chi.real).max()
        ax.imshow(chi.real, cmap="RdBu_r", vmin=-vmax, vmax=vmax)
        for i in range(chi.shape[0]):
            for j in range(chi.shape[1]):
                ax.text(j, i, fmt_char(chi[i, j]), ha="center", va="center", fontsize=10, color="white" if abs(chi[i, j].real) > 0.55 * vmax else "black")
        ax.set_xticks(range(len(sizes)), [f"{s}×\nOrd. {o}" for s, o in zip(sizes, orders)], fontsize=8)
        ax.set_yticks(range(len(sizes)), [f"χ{k + 1} (Grad {int(round(chi[k, 0].real))})" for k in range(len(sizes))], fontsize=8)
        ax.set_title(f"{name}: {len(els)} Elemente, {len(sizes)} Klassen", fontsize=10)
        ax.set_xlabel("Klasse: Größe und Elementordnung")
    plt.tight_layout()
    plt.show()

    for name, (chi, classes, sizes, orders, els) in tables10.items():
        n_ = len(els)
        rows = (chi * sizes) @ chi.conj().T / n_
        cols = chi.conj().T @ chi
        dims_ = [int(round(d.real)) for d in chi[:, 0]]
        print(f"{name}: Grade {dims_}, Σd² = {sum(d * d for d in dims_)} = |G| = {n_}, Grade teilen |G|: {all(n_ % d == 0 for d in dims_)}, "
              f"Zeilen orthonormal: {np.allclose(rows, np.eye(len(sizes)))}, Spalten orthogonal: {np.allclose(cols, np.diag(n_ / sizes))}, "
              f"Elemente der Ordnung 2: {sum(g.order() == 2 for g in els)}")
    print("Tafeln von D₄ und Q₈ gleich:", np.allclose(tables10["D₄"][0], tables10["Q₈"][0]))
    chi4, cl4, sz4, _, els4 = tables10["S₄"]
    reps4 = [els4[c[0]] for c in cl4]
    perm_chars = {"4 Ecken": [sum(g(i) == i for i in range(4)) for g in reps4],
                  "6 Kanten": [sum({g(a), g(b)} == {a, b} for a, b in itertools.combinations(range(4), 2)) for g in reps4],
                  "regulär (24)": [24 if g.is_Identity else 0 for g in reps4]}
    for lab, ch in perm_chars.items():
        m = np.real(np.round((chi4.conj() * sz4) @ np.array(ch) / 24, 6))
        print(f"S₄ auf {lab:12s}: Charakter {ch}, Vielfachheiten der irreduziblen (Grade {[int(round(d.real)) for d in chi4[:, 0]]}): {m.astype(int).tolist()}")


def molecular_vibrations():
    """62. Molekülschwingungen: IR- und Raman-Auswahlregeln aus der Charaktertafel (Zellen 36 von lie.ipynb)."""
    global act, ax, axes, buckyball, c, c60_ir, c60_raman, cat, cats, class_name, counts11, elem_order
    global fig, fixed_axis, gold, ir, k, lab, modes, molecules11, mulliken, name, r, ra
    global ringpts, row, symmetry_ops, td, terms, v, v_, vals, vib11, vibrations, x_, xpos
    def symmetry_ops(types, X, tol=1e-4):
        """Alle orthogonalen Abbildungen, die das Molekül auf sich abbilden (aus dem Notebook Gruppentheorie)."""
        X = X - X.mean(axis=0)
        idx = [i for i in range(len(X)) if np.linalg.norm(X[i]) > 1e-8]
        a = idx[0]
        b = next(j for j in idx if np.linalg.norm(np.cross(X[a], X[j])) > 1e-6)
        ops = []
        for a2, b2 in itertools.product(range(len(X)), repeat=2):
            if types[a2] != types[a] or types[b2] != types[b]:
                continue
            if abs(np.linalg.norm(X[a2]) - np.linalg.norm(X[a])) > tol or abs(np.linalg.norm(X[b2]) - np.linalg.norm(X[b])) > tol or abs(X[a2] @ X[b2] - X[a] @ X[b]) > tol:
                continue
            Fm = np.c_[X[a], X[b], np.cross(X[a], X[b])]
            for sgn in (1, -1):
                R = np.c_[X[a2], X[b2], sgn * np.cross(X[a2], X[b2])] @ np.linalg.inv(Fm)
                dist = np.linalg.norm((X @ R.T)[:, None, :] - X[None, :, :], axis=2)
                j = dist.argmin(axis=1)
                if dist[np.arange(len(X)), j].max() < tol and all(types[i] == types[k] for i, k in enumerate(j)) and not any(np.allclose(R, S, atol=1e-6) for S in ops):
                    ops.append(R)
        return ops

    def elem_order(R):
        P, k = R.copy(), 1
        while not np.allclose(P, np.eye(3), atol=1e-6):
            P, k = P @ R, k + 1
        return k

    def fixed_axis(R, ev):
        w, v = np.linalg.eig(R)
        return np.real(v[:, np.argmin(np.abs(w - ev))])

    def class_name(R):
        if np.linalg.det(R) > 0:
            return "E" if np.allclose(R, np.eye(3)) else f"C{elem_order(R)}"
        if np.allclose(R, -np.eye(3)):
            return "i"
        return "σ" if np.isclose(np.trace(R), 1) else f"S{elem_order(R)}"

    def mulliken(chi, reps, sizes, Xc):
        """Mulliken-Symbole nach den Regeln der Spektroskopie (Hauptachse, Inversion, C₂ senkrecht durch Atome, σ_v, C₄/S₄, C₅)."""
        det = [np.linalg.det(R) for R in reps]
        order = [elem_order(R) for R in reps]
        proper = [k for k in range(len(reps)) if det[k] > 0]
        n_max = max(order[k] for k in proper)
        principal = next(k for k in proper if order[k] == n_max and np.isclose(np.trace(reps[k]), 1 + 2 * np.cos(2 * np.pi / n_max)))
        cubic = sum(sizes[k] for k in proper if order[k] == 3) >= 8
        inv = next((k for k in range(len(reps)) if np.allclose(reps[k], -np.eye(3))), None)
        ord4 = next((k for k in range(len(reps)) if order[k] == 4), None)
        c5 = next((k for k in proper if order[k] == 5 and np.trace(reps[k]) > 1.5), None)
        ax_ = fixed_axis(reps[principal], 1)
        def atoms_on(k):
            if det[k] > 0:
                a = fixed_axis(reps[k], 1)
                return sum(np.linalg.norm(np.cross(p, a)) < 1e-3 and np.linalg.norm(p) > 1e-3 for p in Xc)
            return sum(abs(p @ fixed_axis(reps[k], -1)) < 1e-3 for p in Xc)
        c2perp = [k for k in proper if order[k] == 2 and abs(fixed_axis(reps[k], 1) @ ax_) < 1e-6]
        sig_v = [k for k in range(len(reps)) if det[k] < 0 and np.isclose(np.trace(reps[k]), 1) and abs(fixed_axis(reps[k], -1) @ ax_) < 1e-6]
        ref = ord4 if cubic else (max(c2perp, key=atoms_on) if c2perp else (min(sig_v, key=atoms_on) if sig_v else None))
        labels = []
        for row in chi:
            d = int(round(row[0].real))
            letter = ("A" if cubic or np.isclose(row[principal].real, 1) else "B") if d == 1 else {2: "E", 3: "T", 4: "G", 5: "H"}[d]
            labels.append([letter, "", "" if inv is None else ("g" if row[inv].real > 0 else "u")])
        for t, row in enumerate(chi):
            L, _, par = labels[t]
            same = [s for s in range(len(chi)) if labels[s][0] == L and labels[s][2] == par]
            if len(same) < 2:
                continue
            if L == "E":
                labels[t][1] = str(int(round(np.arccos(np.clip(row[principal].real / 2, -1, 1)) * n_max / (2 * np.pi))))
            elif L == "T":
                labels[t][1] = "1" if (row[ord4].real > 0 if ord4 is not None else row[c5].real > 0) else "2"
            else:
                labels[t][1] = ("1" if row[ref].real > 0 else "2") if ref is not None else str(same.index(t) + 1)
        sub = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
        return [L + s.translate(sub) + p for L, s, p in labels]

    def vibrations(types, X):
        X = np.array(X, float)
        ops = symmetry_ops(types, X)
        key = lambda R: tuple(np.round(R, 5).ravel() + 0.0)
        index = {key(R): i for i, R in enumerate(ops)}
        chi, classes, sizes = character_table(len(ops), lambda i, j: index[key(ops[i] @ ops[j])], lambda i: index[key(ops[i].T)])
        reps = [ops[c[0]] for c in classes]
        Xc = X - X.mean(axis=0)
        labels = mulliken(chi, reps, sizes, Xc)
        fixed = np.array([sum(np.linalg.norm(R @ p - p) < 1e-4 for p in Xc) for R in reps])
        trR = np.array([np.trace(R) for R in reps]); detR = np.array([np.linalg.det(R) for R in reps])
        mult = lambda gam: np.rint(np.real((chi.conj() * sizes) @ gam / len(ops))).astype(int)
        vib = mult(fixed * trR - trR - detR * trR)
        ir = mult(trR) > 0
        raman = mult((trR ** 2 + np.array([np.trace(R @ R) for R in reps])) / 2) > 0
        return dict(group=len(ops), chi=chi, sizes=sizes, reps=reps, labels=labels, vib=vib, ir=ir, raman=raman)

    gold = (1 + 5 ** 0.5) / 2
    def buckyball():
        pts = set()
        for v in [(0, 1, 3 * gold), (1, 2 + gold, 2 * gold), (gold, 2, gold ** 3)]:
            for sh in range(3):
                w = v[sh:] + v[:sh]
                for sg in itertools.product([1, -1], repeat=3):
                    pts.add(tuple(round(s * x, 9) for s, x in zip(sg, w)))
        return (np.array(sorted(pts)) * 0.7).tolist()
    ringpts = lambda r, k: [[r * np.cos(2 * np.pi * i / k), r * np.sin(2 * np.pi * i / k), 0] for i in range(k)]
    molecules11 = {
        "H₂O (C₂ᵥ)": (["O", "H", "H"], [[0, 0, 0.117], [0.757, 0, -0.469], [-0.757, 0, -0.469]]),
        "NH₃ (C₃ᵥ)": (["N", "H", "H", "H"], [[0, 0, 0.38]] + ringpts(0.94, 3)),
        "CH₄ (T_d)": (["C"] + ["H"] * 4, (np.array([[0, 0, 0], [1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]]) * 0.63).tolist()),
        "SF₆ (O_h)": (["S"] + ["F"] * 6, [[0, 0, 0], [1.56, 0, 0], [-1.56, 0, 0], [0, 1.56, 0], [0, -1.56, 0], [0, 0, 1.56], [0, 0, -1.56]]),
        "C₆H₆ (D₆h)": (["C"] * 6 + ["H"] * 6, ringpts(1.39, 6) + ringpts(2.48, 6)),
        "C₆₀ (I_h)": (["C"] * 60, buckyball()),
    }
    vib11 = {name: vibrations(*m) for name, m in molecules11.items()}
    c60_ir = [527, 577, 1183, 1429]                                       # T₁u (Krätschmer et al. 1990)
    c60_raman = {"A_g": [496, 1470], "H_g": [273, 437, 710, 774, 1099, 1250, 1428, 1575]}   # Bethune et al. 1991

    fig, axes = plt.subplots(1, 2, figsize=(16, 4.8), gridspec_kw={"width_ratios": [1.15, 1]})
    ax = axes[0]
    cats = ["IR-aktiv", "Raman-aktiv", "beides", "stumm"]
    counts11 = {}
    for name, r in vib11.items():
        v, ir, ra = r["vib"], r["ir"], r["raman"]
        counts11[name] = [int(v[ir].sum()), int(v[ra].sum()), int(v[ir & ra].sum()), int(v[~ir & ~ra].sum())]
    xpos = np.arange(len(vib11))
    for k, (cat, c) in enumerate(zip(cats, ("C3", "C0", "C4", "grey"))):
        vals = [counts11[n][k] for n in vib11]
        ax.bar(xpos + (k - 1.5) * 0.2, vals, 0.2, color=c, label=cat)
        for x_, v_ in zip(xpos, vals):
            ax.text(x_ + (k - 1.5) * 0.2, v_ + 0.4, str(v_), ha="center", fontsize=7)
    ax.set_xticks(xpos, list(vib11), fontsize=8)
    ax.set_ylabel("Zahl verschiedener Frequenzen")
    ax.set_title("Wie viele Linien zeigen IR- und Raman-Spektrum?", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[1]
    ax.vlines(c60_ir, 0, 1, color="C3", lw=2.5, label="IR: 4 Linien (T₁u)")
    ax.vlines(c60_raman["A_g"], -1, 0, color="C0", lw=2.5, label="Raman: 2 Linien A_g")
    ax.vlines(c60_raman["H_g"], -1, 0, color="C2", lw=2.5, label="Raman: 8 Linien H_g")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_yticks([-0.5, 0.5], ["Raman", "IR"])
    ax.set_xlabel("Wellenzahl (cm⁻¹)")
    ax.set_title("C₆₀: gemessene Linien, nach Symmetrie getrennt", fontsize=10)
    ax.legend(fontsize=8, loc="upper center")
    plt.tight_layout()
    plt.show()

    for name, r in vib11.items():
        terms = " + ".join(f"{m if m > 1 else ''}{l}" for l, m in zip(r["labels"], r["vib"]) if m > 0)
        modes = int(sum(m * round(c[0].real) for m, c in zip(r["vib"], r["chi"])))
        act = lambda mask: ", ".join(l for l, m, a in zip(r["labels"], r["vib"], mask) if a and m > 0)
        print(f"{name:12s} Gruppe {r['group']:3d}: Γ_vib = {terms}  ({modes} Schwingungen, {int(r['vib'].sum())} Frequenzen); IR: {act(r['ir'])}; Raman: {act(r['raman'])}")
    td = vib11["CH₄ (T_d)"]
    print("\nCharaktertafel von T_d, aus den Symmetrieoperationen von CH₄ berechnet:")
    print("       " + "".join(f"{f'{s}{class_name(R)}':>7s}" for s, R in zip(td["sizes"], td["reps"])))
    for lab, row in zip(td["labels"], td["chi"]):
        print(f"{lab:6s} " + "".join(f"{fmt_char(v):>7s}" for v in row))
    print(f"\nC₆₀: Raman-Linien {sorted(c60_raman['A_g'] + c60_raman['H_g'])}, IR-Linien {c60_ir}; dieselbe Wellenzahl in beiden Listen: {sorted(set(c60_ir) & set(c60_raman['A_g'] + c60_raman['H_g']))}")


def spin_j():
    """63. Spin j: die irreduziblen Darstellungen von SU(2) (Zellen 39 von lie.ipynb)."""
    global Jp, Jx, Jy, Jz, R_, ax, axes, beta, beta12, c, c1, c2
    global chi_j, d, d_half, de, derr, dsym, fig, im, j, j12, jlist, m12
    global ms, orth12, p_binom, p_sg, psi12, r2, rot2pi, spin_checks, th12, thq, wg, wq
    global xg
    spin_checks = []
    for j in (0.5, 1, 1.5, 2, 5):
        Jx, Jy, Jz, Jp = spin_matrices(j)
        d = 2 * j + 1
        c1 = np.abs(comm(Jx, Jy) - 1j * Jz).max()
        c2 = np.abs(Jx @ Jx + Jy @ Jy + Jz @ Jz - j * (j + 1) * np.eye(int(d))).max()
        rot2pi = np.real(np.diag(expm(-2j * np.pi * Jz)))[0]
        if j <= 2:
            beta = 0.7
            ms = np.arange(j, -j - 1, -1)
            R_ = lambda q: Rational(int(round(2 * q)), 2)
            dsym = np.array([[complex(Rotation.d(R_(j), R_(a), R_(b), beta).doit().evalf()) for b in ms] for a in ms])
            derr = np.abs(expm(-1j * beta * Jy) - dsym).max()
        else:
            derr = np.nan
        spin_checks.append((j, int(d), c1, c2, rot2pi, derr))

    j12 = 10
    Jx, Jy, Jz, Jp = spin_matrices(j12)
    m12 = np.arange(j12, -j12 - 1, -1)
    d_half = np.abs(expm(-1j * np.pi / 2 * Jy)) ** 2
    beta12 = np.pi / 3
    psi12 = expm(-1j * beta12 * Jy)[:, 0]                     # Spalte von |j, j⟩
    p_sg = np.abs(psi12) ** 2
    p_binom = np.array([comb(2 * j12, int(j12 + m)) * np.cos(beta12 / 2) ** (2 * (j12 + m)) * np.sin(beta12 / 2) ** (2 * (j12 - m)) for m in m12])
    th12 = np.linspace(1e-4, 4 * np.pi - 1e-4, 1000)
    chi_j = lambda j, th: np.sin((2 * j + 1) * th / 2) / np.sin(th / 2)
    xg, wg = np.polynomial.legendre.leggauss(200)
    thq = np.pi * (xg + 1); wq = np.pi * wg
    jlist = [0, 0.5, 1, 1.5, 2, 2.5, 3]
    orth12 = np.array([[np.sum(wq * chi_j(a, thq) * chi_j(b, thq) * np.sin(thq / 2) ** 2 / np.pi) for b in jlist] for a in jlist])

    fig, axes = plt.subplots(1, 3, figsize=(18, 4.8))
    ax = axes[0]
    im = ax.imshow(d_half, cmap="magma", extent=[j12 + 0.5, -j12 - 0.5, -j12 - 0.5, j12 + 0.5])
    ax.set_xlabel("Anfangswert m′")
    ax.set_ylabel("Endwert m")
    ax.set_title("|d¹⁰_mm′(π/2)|²: Drehung eines Spins 10 um 90°", fontsize=10)
    plt.colorbar(im, ax=ax, shrink=0.85, label="Wahrscheinlichkeit")
    ax = axes[1]
    ax.bar(m12, p_sg, width=0.8, alpha=0.7, label="|⟨10, m| e^(−iβJ_y) |10, 10⟩|²")
    ax.plot(m12, p_binom, "ko", ms=4, label="Binomialverteilung, 20 Spins ½")
    ax.axvline(j12 * np.cos(beta12), color="C3", ls="--", label=f"Mittelwert j·cos β = {j12 * np.cos(beta12):.1f}")
    ax.set_xlabel("Messwert m")
    ax.set_ylabel("Wahrscheinlichkeit")
    ax.set_title("Stern-Gerlach: Spin 10, um β = 60° gedreht", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[2]
    for j, c in zip((0, 0.5, 1, 1.5), ("k", "C0", "C1", "C2")):
        ax.plot(th12 / np.pi, chi_j(j, th12), color=c, label=f"χ_{Fraction(j)}(θ)")
    ax.plot(th12 / np.pi, 4 * np.sin(th12 / 2) ** 2, "C3:", label="4·sin²(θ/2) (Haar-Dichte, skaliert)")
    ax.axvline(2, color="grey", lw=0.8)
    ax.set_xlabel("Drehwinkel θ / π")
    ax.set_ylabel("Charakter")
    ax.set_title("Halbzahlige Charaktere haben die Periode 4π", fontsize=10)
    ax.legend(fontsize=8, loc="lower left")
    plt.tight_layout()
    plt.show()

    print("  j  dim  |[Jx,Jy] − iJz|   |J² − j(j+1)|   e^(−2πiJz)   |d − sympy|")
    for j, d, c1, c2, r2, de in spin_checks:
        print(f"{j:4.1f} {d:4d}  {c1:14.1e}  {c2:14.1e}  {r2:+10.0f}   {'–' if np.isnan(de) else f'{de:.1e}'}")
    print(f"Stern-Gerlach: wahrscheinlichstes m = {int(m12[np.argmax(p_sg)])} (P = {p_sg.max():.3f}), Mittelwert {np.sum(m12 * p_sg):.4f}, |P − Binomial| ≤ {np.abs(p_sg - p_binom).max():.1e}")
    print(f"Charaktere χ_j, j = 0 … 3, orthonormal mit der Dichte sin²(θ/2)/π: größte Abweichung von der Einheitsmatrix {np.abs(orth12 - np.eye(len(jlist))).max():.1e}")


def cg_coefficients():
    """64. Clebsch-Gordan-Koeffizienten, Wigner-Eckart und die Auswahlregeln der Atomphysik (Zellen 42 von lie.ipynb)."""
    global CG11, Js, Mplus, Mz, R_, Y, Y4, Ylm, a, ax, axes, b
    global braket, cg_err, clebsch_gordan, cnt, cols11, e_, edges, err, fig, i, j1, j2
    global k, l, lm, lm4, m, m1s, m2s, mel, nplus, nz, overlap, phg
    global r, ratios, rule_p, rule_z, st, st11, thg, vm, we, wgt, wq13, xq
    def clebsch_gordan(j1, j2):
        """Gekoppelte Zustände |J M⟩ als Vektoren in der Produktbasis |m1⟩⊗|m2⟩ (m absteigend), Condon-Shortley-Phase."""
        _, _, Jz1, Jp1 = spin_matrices(j1); _, _, Jz2, Jp2 = spin_matrices(j2)
        d1, d2 = len(Jz1), len(Jz2)
        Jm = np.real(np.kron(Jp1.T, np.eye(d2)) + np.kron(np.eye(d1), Jp2.T))
        Mtot = np.real(np.diag(np.kron(Jz1, np.eye(d2)) + np.kron(np.eye(d1), Jz2)))
        states, J = {}, j1 + j2
        while J >= abs(j1 - j2) - 1e-9:
            sub = np.eye(d1 * d2)[:, np.isclose(Mtot, J)]
            for (Jo, Mo), v in states.items():
                if np.isclose(Mo, J):
                    sub = sub - np.outer(v, v @ sub)
            v = np.linalg.svd(sub)[0][:, 0]
            v = v * np.sign(v[np.argmax(np.abs(v) > 1e-9)])           # erster Eintrag (größtes m1) positiv
            M = J
            while M >= -J - 1e-9:
                states[(J, M)] = v
                v = Jm @ v
                v = v / np.linalg.norm(v) if np.linalg.norm(v) > 1e-12 else v
                M -= 1
            J -= 1
        return states

    R_ = lambda q: Rational(int(round(2 * q)), 2)
    cg_err = {}
    for j1, j2 in ((0.5, 0.5), (1, 1), (1.5, 1), (2, 1.5)):
        st = clebsch_gordan(j1, j2)
        m1s, m2s = np.arange(j1, -j1 - 1, -1), np.arange(j2, -j2 - 1, -1)
        cg_err[(j1, j2)] = (len(st), sorted({J for J, _ in st}), max(abs(v[a * len(m2s) + b] - float(CG(R_(j1), R_(m1), R_(j2), R_(m2), R_(J), R_(M)).doit()))
                                                              for (J, M), v in st.items() for a, m1 in enumerate(m1s) for b, m2 in enumerate(m2s)))
    st11 = clebsch_gordan(1, 1)
    cols11 = sorted(st11, key=lambda k: (-k[0], -k[1]))
    CG11 = np.array([st11[k] for k in cols11]).T

    def Ylm(l, m, th, ph):
        if m < 0:
            return (-1) ** m * np.conj(Ylm(l, -m, th, ph))
        norm = np.sqrt((2 * l + 1) / (4 * np.pi) * factorial(l - m) / factorial(l + m))
        return norm * lpmv(m, l, np.cos(th)) * np.exp(1j * m * ph)

    xq, wq13 = np.polynomial.legendre.leggauss(40)
    thg = np.arccos(xq)[:, None]; phg = np.linspace(0, 2 * np.pi, 64, endpoint=False)[None, :]
    wgt = wq13[:, None] * (2 * np.pi / 64)
    lm = [(l, m) for l in range(4) for m in range(-l, l + 1)]
    Y = {k: Ylm(*k, thg, phg) for k in lm}
    braket = lambda f: np.array([[np.sum(wgt * np.conj(Y[a]) * f * Y[b]) for b in lm] for a in lm])
    overlap = braket(np.ones_like(thg * phg))
    Mz = braket(np.cos(thg) + 0 * phg)
    Mplus = braket(np.sin(thg) * np.exp(1j * phg))
    nz = [(a, b) for a in range(len(lm)) for b in range(len(lm)) if abs(Mz[a, b]) > 1e-10]
    nplus = [(a, b) for a in range(len(lm)) for b in range(len(lm)) if abs(Mplus[a, b]) > 1e-10]
    rule_z = all(abs(lm[a][0] - lm[b][0]) == 1 and lm[a][1] == lm[b][1] for a, b in nz)
    rule_p = all(abs(lm[a][0] - lm[b][0]) == 1 and lm[a][1] == lm[b][1] + 1 for a, b in nplus)
    lm4 = [(l, m) for l in range(6) for m in range(-l, l + 1)]
    Y4 = {k: Ylm(*k, thg, phg) for k in lm4}
    we = {}
    for l in range(1, 5):
        ratios = []
        for m in range(-l, l + 1):
            mel = np.real(np.sum(wgt * np.conj(Y4[(l + 1, m)]) * np.cos(thg) * Y4[(l, m)]))
            ratios.append(mel / float(CG(l, m, 1, 0, l + 1, m).doit()))
        we[l] = np.array(ratios)

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    ax = axes[0]
    vm = np.abs(CG11).max()
    ax.imshow(CG11, cmap="RdBu_r", vmin=-vm, vmax=vm)
    for i in range(9):
        for k in range(9):
            if abs(CG11[i, k]) > 1e-9:
                ax.text(k, i, f"{CG11[i, k]:.2f}", ha="center", va="center", fontsize=7)
    ax.set_xticks(range(9), [f"|{int(J)},{int(M):+d}⟩" for J, M in cols11], fontsize=7, rotation=60)
    ax.set_yticks(range(9), [f"|{m1:+d}⟩|{m2:+d}⟩" for m1 in (1, 0, -1) for m2 in (1, 0, -1)], fontsize=7)
    ax.set_xlabel("gekoppelt |J, M⟩: J = 2, 1, 0")
    ax.set_ylabel("ungekoppelt |m₁⟩|m₂⟩")
    ax.set_title("Clebsch-Gordan-Matrix 1 ⊗ 1 = 2 ⊕ 1 ⊕ 0", fontsize=10)
    ax = axes[1]
    ax.imshow(np.abs(Mz) + np.abs(Mplus), cmap="Greys")
    for a, b in nz:
        ax.plot(b, a, "s", color="C0", ms=5)
    for a, b in nplus:
        ax.plot(b, a, "o", color="C3", ms=4)
    ax.plot([], [], "s", color="C0", label="⟨l′m′|cos θ|lm⟩ ≠ 0: Δl = ±1, Δm = 0")
    ax.plot([], [], "o", color="C3", label="⟨l′m′|sin θ e^(iφ)|lm⟩ ≠ 0: Δl = ±1, Δm = +1")
    edges = np.cumsum([2 * l + 1 for l in range(4)])[:-1] - 0.5
    for e_ in edges:
        ax.axhline(e_, color="grey", lw=0.5); ax.axvline(e_, color="grey", lw=0.5)
    ax.set_xticks([0, 2, 6, 12], ["s", "p", "d", "f"]); ax.set_yticks([0, 2, 6, 12], ["s", "p", "d", "f"])
    ax.set_xlabel("Anfangszustand |l, m⟩"); ax.set_ylabel("Endzustand ⟨l′, m′|")
    ax.set_title("Dipol-Matrixelemente für l, l′ ≤ 3", fontsize=10)
    ax.legend(fontsize=7, loc="upper right")
    ax = axes[2]
    for l, r in we.items():
        ax.plot(range(-l, l + 1), r, "o-", label=f"l = {l} → l′ = {l + 1}")
    ax.set_xlabel("magnetische Quantenzahl m")
    ax.set_ylabel("⟨l+1, m|cos θ|l, m⟩ / ⟨l m; 1 0|l+1 m⟩")
    ax.set_title("Wigner-Eckart: das Verhältnis hängt nicht von m ab", fontsize=10)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    for (j1, j2), (cnt, Js, err) in cg_err.items():
        print(f"{Fraction(j1)} ⊗ {Fraction(j2)}: {cnt} Zustände = Σ(2J+1) über J = {', '.join(str(Fraction(J)) for J in Js)};  größte Abweichung von sympy {err:.1e}")
    print(f"Kugelflächenfunktionen bis l = 3 orthonormal (Quadratur): {np.allclose(overlap, np.eye(len(lm)))}")
    print(f"cos θ: {len(nz)} von {len(lm) ** 2} Matrixelementen ≠ 0, alle mit Δl = ±1 und Δm = 0: {rule_z};  sin θ e^(iφ): {len(nplus)} ≠ 0, alle mit Δl = ±1, Δm = +1: {rule_p}")
    print("Reduzierte Matrixelemente (Verhältnis, Streuung über m):", {l: (round(float(r.mean()), 6), float(f"{r.std():.1e}")) for l, r in we.items()})
    print(f"Beispiel ⟨1,0|cos θ|0,0⟩ = {np.real(Mz[lm.index((1, 0)), lm.index((0, 0))]):.6f} (Formel 1/√3 = {1 / np.sqrt(3):.6f});  ⟨0,0|cos θ|0,0⟩ = {abs(Mz[0, 0]):.1e}")


def su3():
    """65. SU(3) und der Achtfache Weg (Zellen 45 von lie.ipynb)."""
    global G, Q, T3s, W, W10, W3, W3b, W8, ax, axes, c, casimir_of
    global cnt, comm_err, decomp14, dim_of, done, err, ev, f_abc, fig, fitM, fitY, icpt14
    global irrep_name, k, kind, ksum, label, lam, legend14, mass10, n_, name, names, octet
    global parts, qfmt, reps14, sets, slope14, title, vals, w, weights, y_, yy
    lam = gell_mann()
    T3s = lam / 2
    f_abc = np.real(-2j * np.einsum("aij,bjk,cki->abc", T3s, T3s, T3s) + 2j * np.einsum("bij,ajk,cki->abc", T3s, T3s, T3s))   # f_abc = −2i tr([T_a, T_b] T_c)
    ksum = lambda A, B: np.kron(A, np.eye(len(B))) + np.kron(np.eye(len(A)), B)
    reps14 = {"3": T3s, "3̄": -T3s.conj(), "8": -1j * f_abc}
    reps14["3⊗3̄"] = np.array([ksum(T3s[a], -T3s[a].conj()) for a in range(8)])
    reps14["3⊗3"] = np.array([ksum(T3s[a], T3s[a]) for a in range(8)])
    reps14["3⊗3⊗3"] = np.array([ksum(ksum(T3s[a], T3s[a]), T3s[a]) for a in range(8)])
    casimir_of = lambda p, q: (p * p + q * q + p * q + 3 * p + 3 * q) / 3
    dim_of = lambda p, q: (p + 1) * (q + 1) * (p + q + 2) // 2
    irrep_name = {round(casimir_of(p, q), 6): (nm, dim_of(p, q)) for p, q, nm in [(0, 0, "1"), (1, 0, "3 bzw. 3̄"), (1, 1, "8"), (2, 0, "6 bzw. 6̄"), (3, 0, "10")]}
    def qfmt(Q):
        fr = Fraction(Q).limit_denominator(3)
        return "0" if fr == 0 else ("+" if fr > 0 else "−") + str(abs(fr))

    def weights(G, C2_value=None):
        C2 = sum(G[a] @ G[a] for a in range(8))
        w, V = np.linalg.eigh(C2)
        P = V[:, np.isclose(w, C2_value)] if C2_value is not None else V
        H = P.conj().T @ (G[2] + 0.37 * G[7]) @ P
        _, U = np.linalg.eigh(H)
        B = P @ U
        return np.array([[np.real(b.conj() @ G[2] @ b), np.real(b.conj() @ G[7] @ b) * 2 / np.sqrt(3)] for b in B.T])

    decomp14 = {}
    for name, G in reps14.items():
        comm_err = max(np.abs(comm(G[a], G[b]) - 1j * np.tensordot(f_abc[a, b], G, axes=(0, 0))).max() for a in range(8) for b in range(8))
        ev = np.round(np.linalg.eigvalsh(sum(G[a] @ G[a] for a in range(8))), 6)
        vals, cnt = np.unique(ev, return_counts=True)
        decomp14[name] = (comm_err, [(irrep_name[v][0], int(c) // irrep_name[v][1]) for v, c in zip(vals, cnt)])
    W3, W3b, W8 = weights(reps14["3"]), weights(reps14["3̄"]), weights(reps14["8"])
    W10 = weights(reps14["3⊗3⊗3"], 6.0)
    names = {"3": {(0.5, 1 / 3): "u", (-0.5, 1 / 3): "d", (0, -2 / 3): "s"},
             "3̄": {(-0.5, -1 / 3): "ū", (0.5, -1 / 3): "d̄", (0, 2 / 3): "s̄"},
             "8": {(0.5, 1): "p", (-0.5, 1): "n", (1, 0): "Σ⁺", (-1, 0): "Σ⁻", (0, 0): "Σ⁰, Λ", (0.5, -1): "Ξ⁰", (-0.5, -1): "Ξ⁻"},
             "10": {(-1.5, 1): "Δ⁻", (-0.5, 1): "Δ⁰", (0.5, 1): "Δ⁺", (1.5, 1): "Δ⁺⁺", (-1, 0): "Σ*⁻", (0, 0): "Σ*⁰", (1, 0): "Σ*⁺",
                    (-0.5, -1): "Ξ*⁻", (0.5, -1): "Ξ*⁰", (0, -2): "Ω⁻"}}
    def label(kind, w):
        return next((s for (a, b), s in names[kind].items() if abs(w[0] - a) < 1e-6 and abs(w[1] - b) < 1e-6), "?")
    mass10 = {1: 1232, 0: 1385, -1: 1533, -2: 1672}          # MeV: Δ(1232), Σ(1385), Ξ(1530), Ω⁻; gerundete PDG-Mittelwerte
    fitY = np.array([1, 0, -1]); fitM = np.array([mass10[y] for y in fitY])
    slope14, icpt14 = np.polyfit(fitY, fitM, 1)
    octet = {"N": 939, "Λ": 1116, "Σ": 1193, "Ξ": 1318}

    fig, axes = plt.subplots(1, 4, figsize=(20, 4.8))
    legend14 = {"3": "Quarks u, d, s", "3̄": "Antiquarks ū, d̄, s̄", "8": "Gewichte des Oktetts", "10": "Gewichte des Dekupletts"}
    for ax, (title, sets) in zip(axes[:3], [("Quarks 3 und Antiquarks 3̄", [("3", W3, "C0"), ("3̄", W3b, "C3")]),
                                            ("Baryonen-Oktett 8 (Spin ½)", [("8", W8, "C2")]),
                                            ("Baryonen-Dekuplett 10 (Spin 3/2)", [("10", W10, "C4")])]):
        for kind, W, c in sets:
            ax.plot(*W.T, "o", color=c, ms=10, alpha=0.75, label=legend14[kind])
            done = set()
            for w in W:
                k = (round(w[0], 4), round(w[1], 4))
                if k in done:
                    ax.plot(*w, "o", ms=17, mfc="none", mec=c)
                    continue
                done.add(k)
                Q = w[0] + w[1] / 2
                ax.text(w[0], w[1] + 0.17, f"{label(kind, w)} (Q = {qfmt(Q)})", ha="center", fontsize=8)
        ax.axhline(0, color="grey", lw=0.5); ax.axvline(0, color="grey", lw=0.5)
        ax.set_xlim(-2, 2); ax.set_ylim(-2.5, 1.6)
        ax.set_xlabel("Isospin T₃"); ax.set_ylabel("Hyperladung Y")
        ax.set_title(title, fontsize=10)
        ax.legend(fontsize=8, loc="lower left")
    ax = axes[3]
    ax.plot(list(mass10), list(mass10.values()), "ko", ms=8, label="gemessen (PDG, gerundet)")
    yy = np.linspace(-2.2, 1.2, 10)
    ax.plot(yy, slope14 * yy + icpt14, "C3--", label=f"Gerade durch Δ, Σ*, Ξ*: Abstand {abs(slope14):.0f} MeV")
    ax.plot(-2, slope14 * -2 + icpt14, "C3*", ms=14, label=f"Vorhersage Ω⁻: {slope14 * -2 + icpt14:.0f} MeV")
    for y_, n_ in zip(mass10, ("Δ", "Σ*", "Ξ*", "Ω⁻")):
        ax.text(y_ + 0.08, mass10[y_] + 12, n_, fontsize=9)
    ax.set_xlabel("Hyperladung Y")
    ax.set_ylabel("Masse (MeV)")
    ax.set_title("Dekuplett: gleiche Massenabstände (Gell-Mann-Okubo)", fontsize=10)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    for name, (err, parts) in decomp14.items():
        print(f"{name:6s}: Vertauschungsfehler {err:.0e};  Zerlegung über C₂: " + " ⊕ ".join(f"{m}×{d}" if m > 1 else d for d, m in parts))
    print(f"Dimensionsformel (p+1)(q+1)(p+q+2)/2: " + ", ".join(f"({p},{q}) → {dim_of(p, q)}" for p, q in [(1, 0), (1, 1), (2, 0), (3, 0), (2, 2), (3, 3)]))
    print(f"Strukturkonstanten: f₁₂₃ = {f_abc[0, 1, 2]:.4f}, f₁₄₇ = {f_abc[0, 3, 6]:.4f}, f₄₅₈ = {f_abc[3, 4, 7]:.4f} (√3/2 = {np.sqrt(3) / 2:.4f})")
    print(f"Dekuplett: {len(W10)} Zustände; Massenabstände {[mass10[-k] - mass10[1 - k] for k in range(3)]} MeV; Vorhersage Ω⁻ {slope14 * -2 + icpt14:.0f} MeV, gemessen {mass10[-2]} MeV")
    print(f"Oktett, Gell-Mann-Okubo (N + Ξ)/2 = {(octet['N'] + octet['Ξ']) / 2:.1f} MeV gegen (3Λ + Σ)/4 = {(3 * octet['Λ'] + octet['Σ']) / 4:.1f} MeV")


def schur_weyl():
    """66. Schur-Weyl-Dualität: Gesamtspin von n Qubits und Mittelung über U(d) (Zellen 48 von lie.ipynb)."""
    global A15, F15, G15, N15, Ns, UU, Us, a, alpha15, ax, axes, b
    global beta15, c, checks15, d15, dim_ok, fig, form, hook, hook_dim, j, j10, jj
    global m, m10, mult_formula, n, n10, n_, num, ok, rng, running, samples15, share
    global spin_multiplicities, tw_err, tw_slope, twirl_exact
    def spin_multiplicities(n):
        S = [sum(site_op(P, i, n) for i in range(n)) / 2 for P in (PX, PY, PZ)]
        ev = np.linalg.eigvalsh(np.real(sum(s @ s for s in S)))
        js = (-1 + np.sqrt(1 + 4 * np.round(ev, 6))) / 2
        vals, cnt = np.unique(np.round(js * 2) / 2, return_counts=True)
        return {float(j): int(c // (2 * j + 1)) for j, c in zip(vals, cnt)}

    def mult_formula(n, j):
        k = int(round(n / 2 - j))
        return int(round((2 * j + 1) / (n / 2 + j + 1) * comb(n, k)))

    def hook_dim(rows):
        n_ = sum(rows)
        cols = [sum(1 for r in rows if r > c) for c in range(rows[0])]
        hooks = [rows[i] - c + cols[c] - i - 1 for i in range(len(rows)) for c in range(rows[i])]
        return factorial(n_) // int(np.prod(hooks))

    checks15 = []
    for n in range(1, 9):
        num = spin_multiplicities(n)
        form = {j: mult_formula(n, j) for j in num}
        hook = {j: hook_dim([int(n / 2 + j), int(n / 2 - j)] if n / 2 - j > 0 else [n]) for j in num}
        checks15.append((n, num, num == form == hook, sum(m * (2 * j + 1) for j, m in num.items()) == 2 ** n))
    rng = np.random.default_rng(15)
    d15 = 3
    G15 = rng.normal(size=(d15 * d15, d15 * d15)) + 1j * rng.normal(size=(d15 * d15, d15 * d15))
    A15 = (G15 + G15.conj().T) / 2                           # hermitesch, damit α und β reell sind
    F15 = np.zeros((d15 * d15, d15 * d15))
    for a, b in itertools.product(range(d15), repeat=2):
        F15[b * d15 + a, a * d15 + b] = 1
    alpha15 = (np.trace(A15) - np.trace(A15 @ F15) / d15) / (d15 ** 2 - 1)
    beta15 = (np.trace(A15 @ F15) - np.trace(A15) / d15) / (d15 ** 2 - 1)
    twirl_exact = alpha15 * np.eye(d15 * d15) + beta15 * F15
    N15 = 20000
    Us = stats.unitary_group.rvs(d15, size=N15, random_state=rng)
    UU = np.einsum("nij,nkl->nikjl", Us, Us).reshape(N15, d15 * d15, d15 * d15)
    samples15 = UU @ A15 @ np.conj(np.transpose(UU, (0, 2, 1)))
    running = np.cumsum(samples15, axis=0) / np.arange(1, N15 + 1)[:, None, None]
    Ns = np.unique(np.logspace(1, np.log10(N15), 30).astype(int))
    tw_err = np.array([np.linalg.norm(running[k - 1] - twirl_exact) for k in Ns])
    tw_slope = np.polyfit(np.log(Ns), np.log(tw_err), 1)[0]

    fig, axes = plt.subplots(1, 3, figsize=(18, 4.7))
    ax = axes[0]
    n10 = 10
    j10 = np.arange(n10 / 2, -0.1, -1)
    m10 = np.array([mult_formula(n10, j) for j in j10])
    ax.bar(j10 - 0.18, m10, width=0.36, label="Vielfachheit m_j = dim der Sₙ-Darstellung")
    ax.bar(j10 + 0.18, m10 * (2 * j10 + 1), width=0.36, color="C1", label="m_j · (2j+1): Anteil an 2¹⁰ = 1024")
    for j, m in zip(j10, m10):
        ax.text(j - 0.18, m + 5, str(m), ha="center", fontsize=8)
        ax.text(j + 0.18, m * (2 * j + 1) + 5, str(int(m * (2 * j + 1))), ha="center", fontsize=8)
    ax.set_ylim(0, 440)
    ax.set_xlabel("Gesamtspin j")
    ax.set_ylabel("Anzahl")
    ax.set_title("10 Qubits: welcher Gesamtspin wie oft", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[1]
    for n_, c in zip((10, 40, 100, 400), ("C0", "C1", "C2", "C3")):
        jj = np.arange(n_ / 2, -0.1, -1)
        share = np.array([mult_formula(n_, j) * (2 * j + 1) for j in jj], float) / 2 ** n_
        ax.plot(jj / np.sqrt(n_), share * np.sqrt(n_), "-", color=c, label=f"n = {n_}")
    ax.set_xlim(0, 3)
    ax.set_xlabel("j / √n")
    ax.set_ylabel("Anteil an 2ⁿ, mal √n")
    ax.set_title("Die meisten Zustände haben j ≈ √(n/2), nicht n/2", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[2]
    ax.loglog(Ns, tw_err, "o-", ms=3, label=f"Monte-Carlo-Twirl, Steigung {tw_slope:.2f}")
    ax.loglog(Ns, tw_err[0] * np.sqrt(Ns[0] / Ns), "k:", label="∝ 1/√N")
    ax.set_xlabel("Zahl N der Haar-zufälligen U ∈ U(3)")
    ax.set_ylabel("‖Mittel − (α·1 + β·F)‖")
    ax.set_title("Twirl über U ⊗ U konvergiert gegen α·1 + β·SWAP", fontsize=10)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    for n, num, ok, dim_ok in checks15:
        print(f"n = {n}: Vielfachheiten {dict(sorted(num.items(), reverse=True))}  = Formel = Hakenlänge: {ok},  Σ m_j(2j+1) = 2ⁿ: {dim_ok}")
    print(f"n = 10: {[mult_formula(10, j) for j in j10]} für j = {j10.tolist()}")
    print(f"Twirl auf zwei Qutrits: α = {alpha15.real:.4f}, β = {beta15.real:.4f};  nach {N15} Stichproben Abweichung {tw_err[-1]:.4f} (Steigung {tw_slope:.2f}), "
          f"Spur bleibt erhalten: {np.isclose(np.trace(running[-1]), np.trace(A15))}")
