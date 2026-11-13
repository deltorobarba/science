"""Diskrete Heisenberg-Weyl-Gruppe für heisenbergweyl.ipynb: Clock und Shift eines Qudits, Weyl-Operatoren D(q, p),
ihre symplektische Phase, Clifford-Gatter als symplektische Matrizen und die diskrete Wigner-Funktion.

Für ungerades d: ζ = e^(2πi/d), Z = diag(ζ^k), X|k⟩ = |k+1 mod d⟩, D(q, p) = τ^(qp) X^q Z^p mit τ = ζ^((d+1)/2). Dieses τ
erfüllt τ² = ζ wie e^(iπ/d), ist aber selbst eine d-te Einheitswurzel; nur so ist D periodisch in q und p (mod d).
Diskrete Wigner-Funktion nach Wootters (1987) und Gross (2006): W(a) = Tr(A(a) ρ)/d mit A(a) = D(a) A(0) D(a)†,
A(0) = Σ_a D(a)/d (die Parität |k⟩ → |−k⟩).
"""
from itertools import product

import numpy as np


def clock_shift(d):
    zeta = np.exp(2j * np.pi / d)
    return np.diag(zeta ** np.arange(d)), np.roll(np.eye(d), 1, axis=0), zeta


def tau(d, half=False):
    """Halbe Phase: ζ^((d+1)/2) (periodisch) oder, mit half=True, e^(iπ/d) (die übliche Schreibweise)."""
    return np.exp(1j * np.pi / d) if half else np.exp(2j * np.pi / d * ((d + 1) // 2))


def displacement(d, q, p, t=None):
    Z, X, _ = clock_shift(d)
    t = tau(d) if t is None else t
    return t ** (q * p) * np.linalg.matrix_power(X, q % d) @ np.linalg.matrix_power(Z, p % d)


def omega(a, b, d):
    """Symplektisches Produkt ω(a, b) = q p' − q' p (mod d)."""
    return (a[0] * b[1] - b[0] * a[1]) % d


def fourier(d):
    zeta = np.exp(2j * np.pi / d)
    return zeta ** np.outer(np.arange(d), np.arange(d)) / np.sqrt(d)


def phase_gate(d):
    """Diskretes Phasengatter |k⟩ → τ^(k²)|k⟩ (Scherung in der Phasenebene)."""
    return np.diag(tau(d) ** (np.arange(d) ** 2))


def symplectic_action(U, d):
    """Matrix M mit U D(a) U† ∝ D(M a): die Wirkung eines Clifford-Gatters auf die Gitterpunkte (q, p)."""
    def image(a):
        V = U @ displacement(d, *a) @ U.conj().T
        for q, p in product(range(d), repeat=2):
            ov = np.trace(displacement(d, q, p).conj().T @ V) / d
            if abs(abs(ov) - 1) < 1e-9:
                return q, p
        raise ValueError("kein Clifford-Gatter")
    return np.array([image((1, 0)), image((0, 1))]).T % d


def group_order(gens, d):
    """Zahl der Elemente der von 2×2-Matrizen erzeugten Gruppe (mod d)."""
    seen = {tuple(np.eye(2, dtype=int).ravel())}
    todo = [np.eye(2, dtype=int)]
    while todo:
        M = todo.pop()
        for G in gens:
            N = (G @ M) % d
            key = tuple(N.ravel())
            if key not in seen:
                seen.add(key)
                todo.append(N)
    return len(seen)


def checks(d=5):
    """Prüft die Weyl-Relation, die symplektische Phase, die Basis und die Clifford-Wirkung; druckt die Ergebnisse."""
    Z, X, zeta = clock_shift(d)
    print(f"Qudit mit d = {d}: ZX = ζXZ {np.allclose(Z @ X, zeta * X @ Z)}; det(ZXZ⁻¹X⁻¹) = "
          f"{np.linalg.det(Z @ X @ np.linalg.inv(Z) @ np.linalg.inv(X)).real:.6f} = det(ζ·1) = ζ^d = 1")
    pts = list(product(range(d), repeat=2))
    for t, name in ((tau(d), "τ = ζ^((d+1)/2)"), (tau(d, half=True), "τ = e^(iπ/d)")):
        D = {a: displacement(d, *a, t=t) for a in pts}
        cocycle = all(np.allclose(D[a] @ D[b], t ** (-omega(a, b, d) if t == tau(d) else -(a[0] * b[1] - b[0] * a[1]))
                                  * displacement(d, a[0] + b[0], a[1] + b[1], t=t)) for a in pts for b in pts)
        periodic = np.allclose(displacement(d, 1 + d, 1, t=t), displacement(d, 1, 1, t=t))
        print(f"  {name}: D(a)D(b) = τ^(−ω(a,b)) D(a+b) für alle {d ** 4} Paare: {cocycle}; D(q+d, p) = D(q, p): {periodic}")
    D = {a: displacement(d, *a) for a in pts}
    G = np.array([[np.trace(D[a].conj().T @ D[b]) / d for b in pts] for a in pts])
    comm = all(np.allclose(D[a] @ D[b] @ D[a].conj().T @ D[b].conj().T, zeta ** (-omega(a, b, d)) * np.eye(d))
               for a in pts for b in pts)
    print(f"  Tr(D(a)† D(b))/d = δ_ab: {np.allclose(G, np.eye(d * d))} ({d * d} Operatoren, Basis aller {d}×{d}-Matrizen); "
          f"Gruppenkommutator D(a)D(b)D(a)†D(b)† = ζ^(−ω(a,b))·1: {comm}")
    F, S = fourier(d), phase_gate(d)
    MF, MS = symplectic_action(F, d), symplectic_action(S, d)
    det = lambda M: int(round(np.linalg.det(M))) % d
    print(f"  Fourier F: (q, p) → M·(q, p) mit M = {MF.tolist()} (det {det(MF)}, M⁴ = 1: "
          f"{np.array_equal(np.linalg.matrix_power(MF, 4) % d, np.eye(2))}): eine Vierteldrehung des Gitters")
    print(f"  Phasengatter S: M = {MS.tolist()} (det {det(MS)}): eine Scherung p → p + q")
    print(f"  F und S erzeugen {group_order([MF, MS], d)} symplektische Matrizen; |SL(2, Z_{d})| = d(d²−1) = {d * (d * d - 1)}")
    return MF, MS


def wigner(psi, d):
    """Diskrete Wigner-Funktion W[q, p] eines reinen Zustands (d ungerade)."""
    pts = list(product(range(d), repeat=2))
    A0 = sum(displacement(d, *a) for a in pts) / d
    rho = np.outer(psi, psi.conj())
    W = np.zeros((d, d))
    for q, p in pts:
        D = displacement(d, q, p)
        W[q, p] = np.real(np.trace(D @ A0 @ D.conj().T @ rho)) / d
    return W


def stabilizer_states(d):
    """Die d(d+1) Stabilisatorzustände eines Qudits (d prim): Eigenzustände von Z und von X Z^m."""
    Z, X, _ = clock_shift(d)
    out = []
    for M in [Z] + [X @ np.linalg.matrix_power(Z, m) for m in range(d)]:
        _, V = np.linalg.eig(M)
        out += [V[:, k] / np.linalg.norm(V[:, k]) for k in range(d)]
    return out


def mana(W):
    """Mana = ln Σ|W| (Veitch und andere 2014): 0 genau dann, wenn W ≥ 0."""
    return np.log(np.abs(W).sum())
