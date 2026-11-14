"""Gruppentheorie: Verknüpfungstafeln, Gruppen kleiner Ordnung, Untergruppen und Normalteiler, Burnside und Isomere, symmetrische Gruppe, Zauberwürfel, einfache und sporadische Gruppen, Monster, Punkt- und Tapetengruppen, Pauli- und Clifford-Gruppe.

Für algebra.ipynb aus grouptheory.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, cayley_tables, order_8_12, counting_groups, s4_lattice, burnside, chemical_isomers, symmetric_group, rubik, units_mod_n, simple_groups, sporadic_groups, monster_moonshine, point_groups, crystals, pauli_clifford, rotations.
"""
import importlib.util, subprocess, sys
import itertools, time
from collections import Counter
from math import gcd, factorial
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from scipy import stats
from scipy.spatial.transform import Rotation
from sympy import factorint, totient
from sympy.functions.combinatorial.numbers import partition, reduced_totient
from sympy.combinatorics import Permutation, PermutationGroup
from sympy.combinatorics.named_groups import SymmetricGroup, AlternatingGroup, RubikGroup
from rdkit import Chem
from rdkit.Chem import Draw, rdDepictor
from rdkit.Geometry import Point2D


def load():
    """1. Daten (Zellen 4 von grouptheory.ipynb)."""
    global cayley_table, element_order, fmt, invariants, is_simple, key, matrix_group, rot2
    def key(M):
        """Gerundeter Schlüssel einer Matrix, damit gleiche Gruppenelemente als gleich erkannt werden."""
        return tuple(np.round(np.asarray(M, dtype=complex).ravel(), 8))
    def matrix_group(gens):
        """Alle Elemente der von den Matrizen gens erzeugten endlichen Gruppe (Abschluss unter Multiplikation); das Einselement zuerst."""
        I = np.eye(len(gens[0]), dtype=complex)
        elems, frontier = {key(I): I}, [I]
        while frontier:
            new = []
            for A in frontier:
                for g in gens:
                    B = g @ A
                    if key(B) not in elems:
                        elems[key(B)] = B
                        new.append(B)
            frontier = new
        return list(elems.values())
    def element_order(M):
        I, P, k = np.eye(len(M)), np.array(M, dtype=complex), 1
        while not np.allclose(P, I):
            P, k = P @ M, k + 1
        return k
    def cayley_table(elems):
        """Verknüpfungstafel: Eintrag (i, j) ist der Index von elems[i] · elems[j]."""
        index = {key(E): i for i, E in enumerate(elems)}
        return np.array([[index[key(A @ B)] for B in elems] for A in elems])
    def invariants(elems):
        """Ordnungsstatistik, Zentrum, Kommutatoruntergruppe und Zahl der Konjugationsklassen einer Matrixgruppe."""
        n = len(elems)
        orders = [element_order(E) for E in elems]
        center = [A for A in elems if all(np.allclose(A @ B, B @ A) for B in elems)]
        comms = [A @ B @ np.linalg.inv(A) @ np.linalg.inv(B) for A in elems for B in elems]
        derived = matrix_group(list({key(C): C for C in comms}.values()))
        classes, seen = 0, set()
        for A in elems:
            if key(A) in seen:
                continue
            classes += 1
            seen |= {key(B @ A @ np.linalg.inv(B)) for B in elems}
        return dict(order=n, orders=orders, center=len(center), derived=len(derived), classes=classes,
                    abelian=len(center) == n)
    def is_simple(G):
        """Eine Permutationsgruppe ist einfach, wenn der Normalabschluss jedes Elements ≠ 1 schon die ganze Gruppe ist."""
        n = G.order()
        for cls in G.conjugacy_classes():
            g = next(iter(cls))
            if not g.is_Identity and G.normal_closure(PermutationGroup([g])).order() != n:
                return False
        return n > 1
    def fmt(n):
        """Ganze Zahl mit Leerzeichen als Tausendertrennzeichen."""
        return f"{int(n):,}".replace(",", " ")
    def rot2(angle):
        c, s = np.cos(angle), np.sin(angle)
        return np.array([[c, -s], [s, c]])
    print("Werkzeuge bereit: Matrixgruppen, Ordnungen, Verknüpfungstafeln, Invarianten, Einfachheitstest")


def cayley_tables():
    """2. Verknüpfungstafeln kleiner Gruppen (Zellen 6 von grouptheory.ipynb)."""
    global G, T, X, Y, Z, assoc, ax, axes, fig, groups1, i, j
    global latin, name, perm
    X = np.array([[0, 1], [1, 0]]); Y = np.array([[0, -1j], [1j, 0]]); Z = np.array([[1, 0], [0, -1]])
    perm = lambda p: np.eye(len(p))[list(p)]
    groups1 = {
        "ℤ₆ (Drehungen um 60°)": matrix_group([rot2(np.pi / 3)]),
        "S₃ (Permutationen von 3 Dingen)": matrix_group([perm([1, 0, 2]), perm([1, 2, 0])]),
        "D₄ (Symmetrien des Quadrats)": matrix_group([rot2(np.pi / 2), np.diag([1.0, -1.0])]),
        "Q₈ (Quaternionen, ±1, ±iX, ±iY, ±iZ)": matrix_group([1j * X, 1j * Z]),
    }
    fig, axes = plt.subplots(1, 4, figsize=(18, 4.6))
    for ax, (name, G) in zip(axes, groups1.items()):
        T = cayley_table(G)
        ax.imshow(T, cmap="tab20", vmin=0, vmax=19)
        for i in range(len(G)):
            for j in range(len(G)):
                ax.text(j, i, T[i, j], ha="center", va="center", fontsize=8)
        ax.set_title(f"{name}, Ordnung {len(G)}", fontsize=10)
        ax.set_xlabel("rechter Faktor b")
        ax.set_ylabel("linker Faktor a")
    plt.tight_layout()
    plt.show()

    for name, G in groups1.items():
        T = cayley_table(G)
        latin = all(len(set(row)) == len(G) for row in T) and all(len(set(col)) == len(G) for col in T.T)
        assoc = all(np.allclose((A @ B) @ C, A @ (B @ C)) for A in G for B in G for C in G)
        print(f"{name:38s}: Ordnung {len(G):2d}; lateinisches Quadrat {latin}; assoziativ {assoc}; "
              f"Tafel symmetrisch (abelsch) {np.array_equal(T, T.T)}; Elementordnungen {sorted(element_order(E) for E in G)}")


def order_8_12():
    """3. Gruppen der Ordnung 8 und 12 unterscheiden (Zellen 9 von grouptheory.ipynb)."""
    global G, ax, axes, block, fam, fig, i, inv, name, o, order12, order8
    global possible, prof, w, width
    def block(*ms):
        n = sum(len(m) for m in ms)
        out, k = np.zeros((n, n), dtype=complex), 0
        for m in ms:
            out[k:k + len(m), k:k + len(m)] = m
            k += len(m)
        return out

    w = np.exp(1j * np.pi / 3)
    order8 = {
        "ℤ₈": matrix_group([rot2(np.pi / 4)]),
        "ℤ₄ × ℤ₂": matrix_group([block(rot2(np.pi / 2), np.eye(1)), block(np.eye(2), -np.eye(1))]),
        "ℤ₂³": matrix_group([np.diag([-1.0, 1, 1]), np.diag([1.0, -1, 1]), np.diag([1.0, 1, -1])]),
        "D₄": groups1["D₄ (Symmetrien des Quadrats)"],
        "Q₈": groups1["Q₈ (Quaternionen, ±1, ±iX, ±iY, ±iZ)"],
    }
    order12 = {
        "ℤ₁₂": matrix_group([rot2(np.pi / 6)]),
        "ℤ₆ × ℤ₂": matrix_group([block(rot2(np.pi / 3), np.eye(1)), block(np.eye(2), -np.eye(1))]),
        "A₄": matrix_group([perm([1, 2, 0, 3]), perm([1, 0, 3, 2])]),
        "D₆": matrix_group([rot2(np.pi / 3), np.diag([1.0, -1.0])]),
        "Dic₃": matrix_group([np.diag([w, np.conj(w)]), np.array([[0, 1], [-1, 0]])]),
    }
    fig, axes = plt.subplots(1, 2, figsize=(16, 4.3))
    for ax, fam, possible in [(axes[0], order8, [1, 2, 4, 8]), (axes[1], order12, [1, 2, 3, 4, 6, 12])]:
        width = 0.8 / len(fam)
        for i, (name, G) in enumerate(fam.items()):
            o = [element_order(E) for E in G]
            ax.bar(np.arange(len(possible)) + (i - len(fam) / 2 + 0.5) * width, [o.count(d) for d in possible], width, label=name)
        ax.set_xticks(range(len(possible)), possible)
        ax.set_xlabel("Ordnung des Elements")
        ax.set_ylabel("Zahl der Elemente")
        ax.legend(fontsize=8)
    axes[0].set_title("Die fünf Gruppen der Ordnung 8", fontsize=10)
    axes[1].set_title("Die fünf Gruppen der Ordnung 12", fontsize=10)
    plt.tight_layout()
    plt.show()

    print(f"{'Gruppe':9s} {'Ordnung':>7s} {'abelsch':>8s} {'|Zentrum|':>10s} {'|[G,G]|':>8s} {'Klassen':>8s}   Elementordnungen")
    for fam in (order8, order12):
        for name, G in fam.items():
            inv = invariants(G)
            prof = {d: inv["orders"].count(d) for d in sorted(set(inv["orders"]))}
            print(f"{name:9s} {inv['order']:7d} {str(inv['abelian']):>8s} {inv['center']:10d} {inv['derived']:8d} {inv['classes']:8d}   {prof}")


def counting_groups():
    """4. Wie viele Gruppen gibt es? (Zellen 12 von grouptheory.ipynb)."""
    global a000001, ab, abelian_count, allg, axes, c, fig, k_, kinds, kk, ks, label
    global n, powers_of_two, pq, pred, v
    # Zahl der Gruppen der Ordnung n, n = 1 … 130 (OEIS A000001, berechnet mit der SmallGroups-Bibliothek von GAP)
    a000001 = [1, 1, 1, 2, 1, 2, 1, 5, 2, 2, 1, 5, 1, 2, 1, 14, 1, 5, 1, 5, 2, 2, 1, 15, 2, 2, 5, 4, 1, 4, 1, 51, 1, 2, 1, 14,
               1, 2, 2, 14, 1, 6, 1, 4, 2, 2, 1, 52, 2, 5, 1, 5, 1, 15, 2, 13, 2, 2, 1, 13, 1, 2, 4, 267, 1, 4, 1, 5, 1, 4, 1,
               50, 1, 2, 3, 4, 1, 6, 1, 52, 15, 2, 1, 15, 1, 2, 1, 12, 1, 10, 1, 4, 2, 2, 1, 231, 1, 5, 2, 16, 1, 4, 1, 14,
               2, 2, 1, 45, 1, 6, 2, 43, 1, 6, 1, 5, 4, 2, 1, 47, 2, 2, 1, 4, 5, 16, 1, 2328, 2, 4]
    powers_of_two = {1: 1, 2: 1, 4: 2, 8: 5, 16: 14, 32: 51, 64: 267, 128: 2328, 256: 56092, 512: 10494213, 1024: 49487367289}

    def abelian_count(n):
        """Zahl der abelschen Gruppen der Ordnung n: Produkt der Partitionszahlen der Primzahlexponenten."""
        out = 1
        for e in factorint(n).values():
            out *= int(partition(e))
        return out

    n = np.arange(1, 131)
    ab = np.array([abelian_count(int(k)) for k in n])
    allg = np.array(a000001)
    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    axes[0].bar(n, allg, color="tab:blue", label="alle Gruppen")
    axes[0].bar(n, ab, color="tab:orange", alpha=0.9, label="davon abelsch")
    axes[0].set_yscale("log")
    axes[0].set_xlabel("Ordnung n")
    axes[0].set_ylabel("Zahl der Gruppen")
    axes[0].set_title("Gruppen der Ordnung n ≤ 130", fontsize=10)
    axes[0].legend(fontsize=8)
    kinds = {"Primzahl p": [k for k in n if len(factorint(int(k))) == 1 and list(factorint(int(k)).values())[0] == 1],
             "p²": [k for k in n if len(factorint(int(k))) == 1 and list(factorint(int(k)).values())[0] == 2],
             "p·q (p < q)": [k for k in n if sorted(factorint(int(k)).values()) == [1, 1]],
             "Zweierpotenz 2^k, k ≥ 3": [k for k in n if k >= 8 and (k & (k - 1)) == 0]}
    for (label, ks), c in zip(kinds.items(), ["tab:green", "tab:purple", "tab:orange", "tab:red"]):
        ks = np.array(ks)
        axes[1].plot(ks, allg[ks - 1], "o", c=c, ms=5, label=label)
    axes[1].set_yscale("log")
    axes[1].set_xlabel("Ordnung n")
    axes[1].set_ylabel("Zahl der Gruppen")
    axes[1].set_title("Die Primfaktorzerlegung bestimmt fast alles", fontsize=10)
    axes[1].legend(fontsize=8)
    kk = np.array(list(powers_of_two))
    axes[2].semilogy(np.log2(kk), list(powers_of_two.values()), "o-")
    for k_, v in powers_of_two.items():
        if k_ >= 64:
            axes[2].annotate(fmt(v), (np.log2(k_), v), textcoords="offset points", xytext=(-75, 2), fontsize=7)
    axes[2].set_xlabel("k (Ordnung 2^k)")
    axes[2].set_ylabel("Zahl der Gruppen")
    axes[2].set_title("Explosion bei Zweierpotenzen", fontsize=10)
    plt.tight_layout()
    plt.show()

    pq = kinds["p·q (p < q)"]
    pred = [2 if (max(factorint(int(k))) - 1) % min(factorint(int(k))) == 0 else 1 for k in pq]
    print(f"Ordnung p (Primzahl): immer genau {set(allg[np.array(kinds['Primzahl p']) - 1])} Gruppe;  Ordnung p²: immer {set(allg[np.array(kinds['p²']) - 1])}")
    print(f"Ordnung p·q: Vorhersage 2 wenn p | q − 1, sonst 1 – stimmt für alle {len(pq)} Fälle bis 130: {list(allg[np.array(pq) - 1]) == pred}")
    print(f"Gruppen der Ordnung ≤ 130: {allg.sum()}, davon Ordnung 128: {allg[127]} ({allg[127] / allg.sum():.0%}); abelsch insgesamt {ab.sum()}")


def s4_lattice():
    """5. Untergruppen, Lagrange und Normalteiler: der Verband von S₄ (Zellen 15 von grouptheory.ipynb)."""
    global A4, H, S, S4, T, V4, a4_subs, axes, cosets, counts, divisors, els
    global fig, g, h, i, levels, lv, normal, pos, row, size, subgroups, subs
    S4 = SymmetricGroup(4)
    els = list(S4.generate())
    subgroups = {}
    for g, h in itertools.combinations_with_replacement(els, 2):                     # jede Untergruppe von S₄ wird von zwei Elementen erzeugt
        H = PermutationGroup([g, h])
        subgroups[frozenset(tuple(p.array_form) for p in H.generate())] = H
    subs = sorted(subgroups, key=len)
    normal = [S for S in subs if all(frozenset(tuple((x * Permutation(list(s)) * x ** -1).array_form) for s in S) == S for x in S4.generators)]

    fig, axes = plt.subplots(1, 2, figsize=(17, 5.2), gridspec_kw={"width_ratios": [2.3, 1]})
    levels = sorted({len(S) for S in subs})
    pos = {}
    for lv, size in enumerate(levels):
        row = [S for S in subs if len(S) == size]
        for i, S in enumerate(row):
            pos[S] = ((i - (len(row) - 1) / 2) * 1.0, lv)
    for S in subs:
        for T in subs:
            if len(T) > len(S) and S < T and not any(S < U < T for U in subs):  # nur direkte Inklusionen
                axes[0].plot([pos[S][0], pos[T][0]], [pos[S][1], pos[T][1]], color="grey", lw=0.5, zorder=1)
    for S in subs:
        axes[0].scatter(*pos[S], s=140, c="tab:red" if S in normal else "tab:blue", zorder=2, edgecolor="k")
    axes[0].set_yticks(range(len(levels)), [f"Ordnung {s}" for s in levels])
    axes[0].set_xticks([])
    axes[0].set_title(f"Alle {len(subs)} Untergruppen von S₄ (rot: Normalteiler)", fontsize=10)
    A4 = AlternatingGroup(4)
    a4_subs = {frozenset(tuple(p.array_form) for p in PermutationGroup([g, h]).generate())
               for g, h in itertools.combinations_with_replacement(list(A4.generate()), 2)}
    divisors = [d for d in range(1, 13) if 12 % d == 0]
    counts = [sum(1 for S in a4_subs if len(S) == d) for d in divisors]
    axes[1].bar([str(d) for d in divisors], counts, color=["tab:blue" if c else "tab:red" for c in counts])
    axes[1].set_xlabel("Teiler d von 12")
    axes[1].set_ylabel("Zahl der Untergruppen der Ordnung d")
    axes[1].set_title("A₄: keine Untergruppe der Ordnung 6", fontsize=10)
    axes[1].set_yticks(range(0, max(counts) + 1))
    plt.tight_layout()
    plt.show()

    print("Untergruppen von S₄ nach Ordnung:", {s: sum(1 for S in subs if len(S) == s) for s in levels}, f"– alle Ordnungen teilen 24: {all(24 % len(S) == 0 for S in subs)}")
    print("Normalteiler von S₄ (Ordnungen):", [len(S) for S in normal])
    V4 = next(S for S in normal if len(S) == 4)
    cosets = {frozenset(tuple((Permutation(list(v)) * g).array_form) for v in V4) for g in els}
    print(f"S₄/V₄: {len(cosets)} Nebenklassen; die Faktorgruppe ist nicht abelsch und damit ≅ S₃")
    print("Untergruppen von A₄ nach Ordnung:", dict(zip(divisors, counts)))


def burnside():
    """6. Gruppenoperationen zählen: Burnside und chemische Isomere (Zellen 18 von grouptheory.ipynb)."""
    global D, axes, brace, brute, burnside_isomers, cube, cube_perms, faces, fig, fixed, formula, hexagon
    global isomers, k, ks, m, neck, necklaces, ns, orbits, turn_x, turn_z
    hexagon = [tuple((i + r) % 6 for i in range(6)) for r in range(6)] + [tuple((r - i) % 6 for i in range(6)) for r in range(6)]   # D₆ auf 6 Ecken

    def orbits(patterns, group):
        """Bahnen einer Permutationsgruppe auf Färbungen: Vertreter = kleinste Färbung der Bahn."""
        return {min(tuple(p[g[i]] for i in range(len(p))) for g in group) for p in patterns}

    isomers = [len([o for o in orbits(itertools.product([0, 1], repeat=6), hexagon) if sum(o) == k]) for k in range(7)]
    burnside_isomers = []
    for k in range(7):
        fixed = [sum(1 for p in itertools.product([0, 1], repeat=6) if sum(p) == k and all(p[g[i]] == p[i] for i in range(6))) for g in hexagon]
        burnside_isomers.append(sum(fixed) / len(hexagon))

    faces = {"U": 0, "D": 1, "F": 2, "B": 3, "L": 4, "R": 5}
    turn_x = [2, 3, 1, 0, 4, 5]; turn_z = [4, 5, 2, 3, 1, 0]                            # Vierteldrehungen des Würfels als Permutation der Seiten
    cube = matrix_group([perm(turn_x), perm(turn_z)])
    cube_perms = [tuple(int(np.argmax(np.real(P[:, j]))) for j in range(6)) for P in cube]
    ks = range(1, 7)
    brute = [len(orbits(itertools.product(range(k), repeat=6), cube_perms)) if k <= 4 else None for k in ks]
    formula = [(k ** 6 + 3 * k ** 4 + 12 * k ** 3 + 8 * k ** 2) // 24 for k in ks]

    def necklaces(n, k=2):
        return sum(int(totient(d)) * k ** (n // d) for d in range(1, n + 1) if n % d == 0) // n

    ns = np.arange(1, 17)
    neck = [necklaces(int(m)) for m in ns]
    brace = []
    for m in ns:
        m = int(m)
        D = [tuple((i + r) % m for i in range(m)) for r in range(m)] + [tuple((r - i) % m for i in range(m)) for r in range(m)]
        brace.append(len(orbits(itertools.product([0, 1], repeat=m), D)) if m <= 12 else None)

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    axes[0].bar(range(7), [len([p for p in itertools.product([0, 1], repeat=6) if sum(p) == k]) for k in range(7)], color="lightgrey", label="Stellungen ohne Symmetrie: C(6, k)")
    axes[0].bar(range(7), isomers, color="tab:blue", label="verschiedene Moleküle (Bahnen von D₆)")
    axes[0].set_xlabel("Zahl k der Chloratome in C₆H₆₋ₖClₖ")
    axes[0].set_ylabel("Anzahl")
    axes[0].set_title("Isomere der Chlorbenzole", fontsize=10)
    axes[0].legend(fontsize=8)
    axes[1].semilogy(list(ks), [k ** 6 for k in ks], "s--", c="grey", label="alle Färbungen k⁶")
    axes[1].semilogy(list(ks), formula, "o-", label="Burnside: (k⁶ + 3k⁴ + 12k³ + 8k²)/24")
    axes[1].semilogy([k for k, b in zip(ks, brute) if b], [b for b in brute if b], "kx", ms=10, label="durchgezählt")
    axes[1].set_xlabel("Zahl der Farben k")
    axes[1].set_ylabel("Anzahl")
    axes[1].set_title("Färbungen der Würfelseiten bis auf Drehung", fontsize=10)
    axes[1].legend(fontsize=8)
    axes[2].semilogy(ns, 2.0 ** ns, "s--", c="grey", label="alle Ketten 2ⁿ")
    axes[2].semilogy(ns, neck, "o-", label="bis auf Drehung (Halsketten)")
    axes[2].semilogy(ns[:12], brace[:12], "^-", label="bis auf Drehung und Spiegelung (Armbänder)")
    axes[2].set_xlabel("Zahl n der Perlen (2 Farben)")
    axes[2].set_ylabel("Anzahl")
    axes[2].set_title("Halsketten: Bahnen von ℤₙ und Dₙ", fontsize=10)
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"Chlorbenzole C₆H₆₋ₖClₖ für k = 0 … 6: {isomers} (Burnside {[int(b) for b in burnside_isomers]}), zusammen {sum(isomers)}")
    print(f"Drehgruppe des Würfels: {len(cube)} Elemente; Färbungen mit k = 1 … 4 Farben durchgezählt {brute[:4]}, Burnside {formula[:4]}")
    print(f"Halsketten mit 2 Farben, n = 6, 10, 16: {neck[5]}, {neck[9]}, {neck[15]};  Armbänder n = 6, 10: {brace[5]}, {brace[9]}")


def chemical_isomers():
    """7. Gruppenoperationen zählen: Burnside und chemische Isomere (Zellen 21 von grouptheory.ipynb)."""
    global ax, axes, chlorobenzene, dichloro, fig, mol, name, opts, orbit_size, p, per_k, pos
    global smiles
    def chlorobenzene(p):
        """Benzolring als RDKit-Molekül; an Ecke i sitzt ein Chloratom statt Wasserstoff, wenn p[i] = 1. Ecke 1 oben, dann im Uhrzeigersinn."""
        mol = Chem.MolFromSmiles("".join("c" + ("1" if i in (0, 5) else "") + ("(Cl)" if x else "") for i, x in enumerate(p)))
        ring = [a.GetIdx() for a in mol.GetAtoms() if a.GetSymbol() == "C"]
        for i, idx in enumerate(ring):
            mol.GetAtomWithIdx(idx).SetProp("atomNote", str(i + 1))                  # Ringposition als kleine Zahl im Bild
        angle = np.pi / 2 - np.pi / 3 * np.arange(6)
        rdDepictor.Compute2DCoords(mol, coordMap={idx: Point2D(1.5 * np.cos(a), 1.5 * np.sin(a)) for idx, a in zip(ring, angle)})
        return mol

    dichloro = [("ortho", "1,2", (1, 1, 0, 0, 0, 0)), ("meta", "1,3", (1, 0, 1, 0, 0, 0)), ("para", "1,4", (1, 0, 0, 1, 0, 0))]
    opts = Draw.MolDrawOptions()
    opts.fixedBondLength = 50                                                        # gleicher Maßstab in allen drei Bildern

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))
    for ax, (name, pos, p) in zip(axes, dichloro):
        mol = chlorobenzene(p)
        ax.imshow(Draw.MolToImage(mol, size=(400, 400), options=opts))
        ax.set_title(f"{pos}-Dichlorbenzol ({name})\nkanonische SMILES: {Chem.MolToSmiles(mol)}", fontsize=10)
        ax.axis("off")
    plt.tight_layout()
    plt.show()

    smiles = {p: Chem.MolToSmiles(chlorobenzene(p)) for p in itertools.product([0, 1], repeat=6)}   # alle 2⁶ Muster
    per_k = [len({s for p, s in smiles.items() if sum(p) == k}) for k in range(7)]
    orbit_size = Counter(s for p, s in smiles.items() if sum(p) == 2)
    print(f"RDKit: aus {len(smiles)} Mustern werden {len(set(smiles.values()))} verschiedene Moleküle, für k = 0 … 6: {per_k} (Burnside {isomers})")
    print("Stellungen je Dichlorbenzol (Bahngröße): " + ", ".join(f"{name} {orbit_size[Chem.MolToSmiles(chlorobenzene(p))]}" for name, pos, p in dichloro))


def symmetric_group():
    """8. Die symmetrische Gruppe: Zyklen, Vorzeichen und zufällige Permutationen (Zellen 24 von grouptheory.ipynb)."""
    global H, P, Pm, axes, cyc, cycle_lengths, exact_longest, fig, fixed, j, kk, longest
    global loyd, mask, n_cyc, n_fix, nn, rng, rng_cyc
    rng = np.random.default_rng(6)

    def cycle_lengths(p):
        seen, out = np.zeros(len(p), bool), []
        for i in range(len(p)):
            if not seen[i]:
                L, j = 0, i
                while not seen[j]:
                    seen[j], j, L = True, p[j], L + 1
                out.append(L)
        return out

    nn = np.arange(1, 31)
    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    axes[0].semilogy(nn, [factorial(int(k)) for k in nn], "s-", label="Ordnung n!")
    axes[0].semilogy(nn, [int(partition(int(k))) for k in nn], "o-", label="Konjugationsklassen = Partitionen p(n)")
    axes[0].set_xlabel("n")
    axes[0].set_ylabel("Anzahl")
    axes[0].set_title("Sₙ: Elemente und Konjugationsklassen", fontsize=10)
    axes[0].legend(fontsize=8)
    n_fix = 100
    P = np.argsort(rng.random((100_000, n_fix)), axis=1)
    fixed = (P == np.arange(n_fix)).sum(axis=1)
    kk = np.arange(0, 8)
    axes[1].bar(kk, [np.mean(fixed == k) for k in kk], alpha=0.6, label=f"gemessen, n = {n_fix}")
    axes[1].plot(kk, stats.poisson.pmf(kk, 1), "ko", label="Poisson(1): e⁻¹/k!")
    axes[1].set_xlabel("Zahl der Fixpunkte")
    axes[1].set_ylabel("Anteil")
    axes[1].set_title("Fixpunkte einer zufälligen Permutation", fontsize=10)
    axes[1].legend(fontsize=8)
    n_cyc = 300
    rng_cyc = np.random.default_rng(1)                                # eigener Generator für die Zyklenstatistik
    cyc = [cycle_lengths(rng_cyc.permutation(n_cyc)) for _ in range(50_000)]
    longest = np.array([max(c) for c in cyc]) / n_cyc
    axes[2].hist(longest, bins=40, density=True, alpha=0.6)
    axes[2].axvline(0.6243, color="k", ls="--", label="Golomb-Dickman λ = 0.6243")
    axes[2].axvline(0.5, color="grey", ls=":", label="halbe Länge")
    axes[2].set_xlabel("Länge des längsten Zyklus / n")
    axes[2].set_ylabel("Dichte")
    axes[2].set_title(f"Längster Zyklus, n = {n_cyc}", fontsize=10)
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    H = sum(1 / k for k in range(1, n_cyc + 1))
    Pm = np.zeros((n_cyc + 1, n_cyc + 1)); Pm[0, :] = 1                # Pm[j, m]: Wahrscheinlichkeit, dass alle Zyklen einer Permutation von j Elementen ≤ m sind
    mask = (np.arange(1, n_cyc + 1)[:, None] <= np.arange(n_cyc + 1)[None, :]).astype(float)
    for j in range(1, n_cyc + 1):
        Pm[j] = (Pm[j - 1::-1][:j] * mask[:j]).sum(axis=0) / j
    exact_longest = sum(1 - Pm[n_cyc, m] for m in range(n_cyc)) / n_cyc
    print(f"Fixpunktfreie Permutationen (Derangements): {np.mean(fixed == 0):.4f}  (Theorie 1/e = {np.exp(-1):.4f});  mittlere Fixpunktzahl {fixed.mean():.3f} (Theorie 1)")
    print(f"Mittlere Zahl der Zyklen bei n = {n_cyc}: {np.mean([len(c) for c in cyc]):.3f} (Theorie H_n = {H:.3f});  längster Zyklus im Mittel {longest.mean():.4f}·n (exakt für n = {n_cyc}: {exact_longest:.4f}, für n → ∞: 0.6243); "
          f"Anteil mit einem Zyklus länger als n/2: {np.mean(longest > 0.5):.3f} (exakt {1 - Pm[n_cyc, n_cyc // 2]:.4f}, für n → ∞: ln 2 = {np.log(2):.3f})")
    loyd = list(range(15)); loyd[13], loyd[14] = loyd[14], loyd[13]
    print(f"15-Puzzle: Vertauschen von 14 und 15 bei Leerfeld unten rechts ist eine Permutation mit Vorzeichen {Permutation(loyd).signature():+d} → nicht lösbar")


def rubik():
    """9. Der Zauberwürfel als Permutationsgruppe (Zellen 27 von grouptheory.ipynb)."""
    global D, F, R, _, axes, cnt, corner_faces, cube_group, fig, i, names, order
    global rng, s, sample_orders, sequences, top, vals
    rng = np.random.default_rng(7)
    cube_group = RubikGroup(3)                                        # sympy: 54 Felder; Erzeuger F, R, D und die drei Mittelscheiben
    F, R, D = cube_group.generators[0], cube_group.generators[2], cube_group.generators[4]
    order = int(cube_group.order())
    corner_faces = int(PermutationGroup([F, R, D]).order())
    sample_orders = []
    for _ in range(5000):
        sample_orders.append(cube_group.random().order())
    sample_orders = np.array(sample_orders)
    sequences = {"F": F, "F R": F * R, "F R F⁻¹ R⁻¹": F * R * F ** -1 * R ** -1, "F² R²": F ** 2 * R ** 2,
                 "F R D": F * R * D, "F R² D³": F * R ** 2 * D ** 3, "F R⁻¹": F * R ** -1}

    fig, axes = plt.subplots(1, 2, figsize=(16, 4.3))
    vals, cnt = np.unique(sample_orders, return_counts=True)
    top = np.argsort(cnt)[::-1][:20]
    axes[0].bar([str(v) for v in vals[top]], cnt[top] / len(sample_orders))
    axes[0].set_xlabel("Ordnung eines zufälligen Würfelzustands (die 20 häufigsten)")
    axes[0].set_ylabel("Anteil")
    axes[0].set_title("Wie oft muss man eine zufällige Zugfolge wiederholen?", fontsize=10)
    axes[0].tick_params(axis="x", labelsize=8)
    names = list(sequences)
    axes[1].barh(names, [sequences[s].order() for s in names])
    for i, s in enumerate(names):
        axes[1].text(sequences[s].order() + 2, i, str(sequences[s].order()), va="center", fontsize=9)
    axes[1].set_xlabel("Ordnung (Wiederholungen bis zum Ausgangszustand)")
    axes[1].set_title("Ordnung bekannter Zugfolgen", fontsize=10)
    plt.tight_layout()
    plt.show()

    print(f"Ordnung der Würfelgruppe: {fmt(order)} = {' · '.join(f'{p}^{e}' for p, e in factorint(order).items())}")
    print(f"Zerlegt man den Würfel und setzt ihn beliebig zusammen, gibt es 12-mal so viele Zustände: {fmt(12 * order)}")
    print(f"Nur die drei Seiten F, R, D (an einer Ecke): Untergruppe der Ordnung {fmt(corner_faces)}, Index {fmt(order // corner_faces)}")
    print(f"5000 Zufallszustände: größte Ordnung {sample_orders.max()} (Maximum der Gruppe: 1260), Median {int(np.median(sample_orders))}, Anteil mit Ordnung ≤ 12: {np.mean(sample_orders <= 12):.3f}")


def units_mod_n():
    """10. Abelsche Gruppen: die Einheitengruppe modulo n (Zellen 30 von grouptheory.ipynb)."""
    global a, axes, cyclic, divs, fig, g, gauss_cyclic, k, lam, ns, order_counts, p
    global phi, powers, y
    ns = np.arange(2, 301)
    phi = np.array([int(totient(int(k))) for k in ns])
    lam = np.array([int(reduced_totient(int(k))) for k in ns])
    cyclic = lam == phi

    def gauss_cyclic(n):
        """Gauß: (ℤ/nℤ)^× ist zyklisch genau für n = 1, 2, 4, p^k und 2p^k (p ungerade Primzahl)."""
        f = factorint(n)
        if n in (2, 4):
            return True
        odd = [p for p in f if p != 2]
        return len(odd) == 1 and f.get(2, 0) <= 1

    p, g = 101, 2
    powers = [pow(g, x, p) for x in range(p - 1)]
    divs = [d for d in range(1, p) if (p - 1) % d == 0]
    order_counts = {d: 0 for d in divs}
    for a in range(1, p):
        k, y = 1, a
        while y != 1:
            y, k = y * a % p, k + 1
        order_counts[k] += 1

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    axes[0].plot(ns[~cyclic], phi[~cyclic], ".", c="grey", ms=4, label="nicht zyklisch")
    axes[0].plot(ns[cyclic], phi[cyclic], "o", c="tab:red", ms=3, label="zyklisch (es gibt eine Primitivwurzel)")
    axes[0].set_xlabel("n")
    axes[0].set_ylabel("|(ℤ/nℤ)^×| = φ(n)")
    axes[0].set_title("Einheitengruppen modulo n", fontsize=10)
    axes[0].legend(fontsize=8)
    axes[1].plot(range(p - 1), powers, ".", ms=5)
    axes[1].set_xlabel("Exponent x")
    axes[1].set_ylabel(f"{g}^x mod {p}")
    axes[1].set_title(f"Potenzen der Primitivwurzel {g} modulo {p}", fontsize=10)
    axes[2].bar([str(d) for d in divs], [order_counts[d] for d in divs], alpha=0.6, label="gemessen")
    axes[2].plot([str(d) for d in divs], [int(totient(d)) for d in divs], "ko", label="φ(d)")
    axes[2].set_xlabel(f"Elementordnung d (Teiler von {p - 1})")
    axes[2].set_ylabel("Zahl der Elemente")
    axes[2].set_title(f"(ℤ/{p}ℤ)^× ≅ ℤ_{p - 1}", fontsize=10)
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"Zyklisch für n ≤ 300: {cyclic.sum()} von {len(ns)} Werten; Gauß' Kriterium stimmt für alle: {all(c == gauss_cyclic(int(k)) for k, c in zip(ns, cyclic))}")
    print(f"Beispiele: (ℤ/8ℤ)^× hat φ = 4, Exponent λ = {int(reduced_totient(8))} → ℤ₂ × ℤ₂;  (ℤ/15ℤ)^× hat φ = 8, λ = {int(reduced_totient(15))} → ℤ₂ × ℤ₄;  (ℤ/{p}ℤ)^× ist zyklisch mit Erzeuger {g}: {len(set(powers)) == p - 1}")
    print(f"Elementordnungen in (ℤ/{p}ℤ)^×: {order_counts}  (Theorie φ(d) für jeden Teiler d)")


def simple_groups():
    """11. Einfache Gruppen: die Bausteine (Zellen 33 von grouptheory.ipynb)."""
    global G, M11, M12, PSL27, a7, an, axes, b7, c, c7, d, ds
    global dt, fam_color, fig, formula_orders, i, mat, name, nm, o, pl, prime_powers, psl2
    global results, s, small_simple, solv, t0, tests
    a7 = Permutation([[0, 1, 2, 3, 4, 5, 6]]); b7 = Permutation([[1, 2, 4], [3, 6, 5]], size=7); c7 = Permutation([[1, 6], [2, 3]], size=7)
    PSL27 = PermutationGroup([a7, b7, c7])                               # PSL(2,7) ≅ GL(3,2): Symmetrien der Fano-Ebene
    M12 = PermutationGroup([Permutation([[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]], size=12), Permutation([[2, 6, 10, 7], [3, 9, 4, 5]], size=12),
                            Permutation([[0, 11], [1, 10], [2, 5], [3, 7], [4, 8], [6, 9]], size=12)])
    M11 = M12.stabilizer(11)
    tests = {"ℤ₇": PermutationGroup([a7]), "S₄": SymmetricGroup(4), "S₅": SymmetricGroup(5), "A₅": AlternatingGroup(5),
             "A₆": AlternatingGroup(6), "PSL(2,7)": PSL27, "M₁₁": M11, "M₁₂": M12}
    results = {}
    for name, G in tests.items():
        t0 = time.time()
        results[name] = (int(G.order()), is_simple(G), G.is_solvable, [int(H.order()) for H in G.derived_series()], time.time() - t0)

    # alle nichtabelschen einfachen Gruppen der Ordnung < 30 000 (Wikipedia, „List of finite simple groups“, vollständig unter 100 000)
    small_simple = [(60, "A₅"), (168, "PSL(2,7)"), (360, "A₆"), (504, "PSL(2,8)"), (660, "PSL(2,11)"), (1092, "PSL(2,13)"), (2448, "PSL(2,17)"),
                    (2520, "A₇"), (3420, "PSL(2,19)"), (4080, "PSL(2,16)"), (5616, "PSL(3,3)"), (6048, "PSU(3,3)"), (6072, "PSL(2,23)"),
                    (7800, "PSL(2,25)"), (7920, "M₁₁"), (9828, "PSL(2,27)"), (12180, "PSL(2,29)"), (14880, "PSL(2,31)"), (20160, "A₈"),
                    (20160, "PSL(3,4)"), (25308, "PSL(2,37)"), (25920, "PSp(4,3)"), (29120, "Sz(8)")]
    psl2 = lambda q: q * (q * q - 1) // gcd(2, q - 1)
    prime_powers = [q for q in range(4, 40) if len(factorint(q)) == 1]
    formula_orders = sorted({psl2(q) for q in prime_powers if psl2(q) < 30000} | {factorial(k) // 2 for k in range(5, 9)})

    fig, axes = plt.subplots(1, 2, figsize=(16, 4.6))
    fam_color = lambda nm: "tab:orange" if nm.startswith("A") else ("tab:blue" if nm.startswith("PSL(2") else ("tab:purple" if nm.startswith("M") else "tab:green"))
    for i, (o, nm) in enumerate(small_simple):
        axes[0].bar(i, o, color=fam_color(nm))
        axes[0].text(i, o * 1.08, nm, rotation=90, ha="center", va="bottom", fontsize=7)
    axes[0].set_yscale("log")
    axes[0].set_ylim(30, 2e5)
    axes[0].set_xticks([])
    axes[0].set_ylabel("Ordnung")
    axes[0].set_title("Alle nichtabelschen einfachen Gruppen unter 30 000", fontsize=10)
    for nm, c in [("alternierend Aₙ", "tab:orange"), ("PSL(2,q)", "tab:blue"), ("andere vom Lie-Typ", "tab:green"), ("sporadisch", "tab:purple")]:
        axes[0].bar(0, 0, color=c, label=nm)
    axes[0].legend(fontsize=8, loc="upper left")
    an = [(k, factorial(k) // 2) for k in range(5, 31)]
    pl = [(q + 1, psl2(q)) for q in [p for p in range(5, 200) if len(factorint(p)) == 1 and list(factorint(p).values())[0] == 1]]
    mat = [(11, 7920, "M₁₁"), (12, 95040, "M₁₂"), (22, 443520, "M₂₂"), (23, 10200960, "M₂₃"), (24, 244823040, "M₂₄")]
    axes[1].semilogy([k for k, _ in an], [o for _, o in an], "o-", c="tab:orange", label="Aₙ auf n Punkten: n!/2")
    axes[1].semilogy([d for d, _ in pl], [o for _, o in pl], ".-", c="tab:blue", label="PSL(2,p) auf p + 1 Punkten: p(p²−1)/2")
    axes[1].semilogy([d for d, _, _ in mat], [o for _, o, _ in mat], "s", c="tab:purple", ms=7, label="Mathieu-Gruppen")
    for d, o, nm in mat:
        axes[1].annotate(nm, (d, o), textcoords="offset points", xytext=(6, -10), fontsize=8)
    axes[1].set_xlim(0, 60)
    axes[1].set_xlabel("Zahl der Punkte, auf denen die Gruppe als Permutationsgruppe wirkt")
    axes[1].set_ylabel("Ordnung")
    axes[1].set_title("Wie groß sind einfache Gruppen auf gleich vielen Punkten?", fontsize=10)
    axes[1].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"{'Gruppe':9s} {'Ordnung':>7s} {'einfach':>8s} {'auflösbar':>10s}   Kommutatorreihe (Ordnungen)")
    for name, (o, s, solv, ds, dt) in results.items():
        print(f"{name:9s} {o:7d} {str(s):>8s} {str(solv):>10s}   {ds}")
    print(f"Ordnungen aus den Formeln für Aₙ und PSL(2,q) unter 30 000: alle in der Liste: {set(formula_orders) <= {o for o, _ in small_simple}}; "
          f"die kleinste Ordnung mit zwei verschiedenen einfachen Gruppen ist 20 160 (A₈ und PSL(3,4))")


def sporadic_groups():
    """12. Sporadische Gruppen: Mathieu-Gruppen und der Golay-Code (Zellen 36 von grouptheory.ipynb)."""
    global G, M22, M23, M24, QR, axes, basis, c, codewords, colors_sp, fig, gf2_rowspace
    global invariant, lab, mathieu, name, order_sp, rows, s24, shift, sporadic, t24, u24, v
    global wc, weights, wv
    sporadic = [  # (Name, Ordnung, Familie)  nach Griess: 1., 2., 3. Generation der „Happy Family“ und Parias
        ("M₁₁", 7920, 1), ("M₁₂", 95040, 1), ("M₂₂", 443520, 1), ("M₂₃", 10200960, 1), ("M₂₄", 244823040, 1),
        ("J₂", 604800, 2), ("HS", 44352000, 2), ("McL", 898128000, 2), ("Co₃", 495766656000, 2), ("Co₂", 42305421312000, 2),
        ("Suz", 448345497600, 2), ("Co₁", 4157776806543360000, 2),
        ("He", 4030387200, 3), ("Fi₂₂", 64561751654400, 3), ("HN", 273030912000000, 3), ("Th", 90745943887872000, 3),
        ("Fi₂₃", 4089470473293004800, 3), ("Fi₂₄′", 1255205709190661721292800, 3), ("B", 4154781481226426191177580544000000, 3),
        ("M", 808017424794512875886459904961710757005754368000000000, 3),
        ("J₁", 175560, 0), ("J₃", 50232960, 0), ("Ru", 145926144000, 0), ("O'N", 460815505920, 0), ("Ly", 51765179004000000, 0),
        ("J₄", 86775571046077562880, 0)]
    s24 = Permutation([list(range(23))], size=24)
    t24 = Permutation([[2, 16, 9, 6, 8], [3, 12, 13, 18, 4], [7, 17, 10, 11, 22], [14, 19, 21, 20, 15]], size=24)
    u24 = Permutation([[23, 0], [1, 22], [2, 11], [3, 15], [4, 17], [5, 9], [6, 19], [7, 13], [8, 20], [10, 16], [12, 21], [14, 18]], size=24)
    M24 = PermutationGroup([s24, t24, u24])                           # Punkte 0 … 22 und ∞ = 23
    M23 = M24.stabilizer(23)
    M22 = M23.stabilizer(22)
    mathieu = {"M₁₁": M11, "M₁₂": M12, "M₂₂": M22, "M₂₃": M23, "M₂₄": M24}

    def gf2_rowspace(M):
        """Zeilenstufenform über GF(2): gibt eine Basis des Zeilenraums zurück."""
        M, r = M.copy() % 2, 0
        for c in range(M.shape[1]):
            piv = [i for i in range(r, len(M)) if M[i, c]]
            if piv:
                M[[r, piv[0]]] = M[[piv[0], r]]
                for i in range(len(M)):
                    if i != r and M[i, c]:
                        M[i] ^= M[r]
                r += 1
        return M[:r]

    QR = sorted({(i * i) % 23 for i in range(1, 23)})                 # quadratische Reste modulo 23
    rows = []
    for shift in range(23):
        v = np.zeros(24, dtype=int)
        v[[(q + shift) % 23 for q in QR + [0]]] = 1
        v[23] = v[:23].sum() % 2
        rows.append(v)
    basis = gf2_rowspace(np.array(rows + [np.ones(24, dtype=int)]))   # erweiterter Golay-Code: 12 Basisvektoren
    codewords = np.array([np.array(c) @ basis % 2 for c in itertools.product([0, 1], repeat=len(basis))])
    weights = codewords.sum(axis=1)
    invariant = [len(gf2_rowspace(np.vstack([basis, basis[:, [g.array_form.index(j) for j in range(24)]]]))) == len(basis) for g in (s24, t24, u24)]

    fig, axes = plt.subplots(1, 2, figsize=(16, 4.6), gridspec_kw={"width_ratios": [2, 1]})
    order_sp = sorted(sporadic, key=lambda s: s[1])
    colors_sp = {1: "tab:blue", 2: "tab:green", 3: "tab:red", 0: "tab:grey"}
    axes[0].bar([s[0] for s in order_sp], [np.log10(float(s[1])) for s in order_sp], color=[colors_sp[s[2]] for s in order_sp])
    for lab, c in [("1. Generation (Mathieu)", "tab:blue"), ("2. Generation (Leech-Gitter)", "tab:green"), ("3. Generation (im Monster)", "tab:red"), ("Parias", "tab:grey")]:
        axes[0].bar(0, 0, color=c, label=lab)
    axes[0].set_ylabel("log₁₀ der Ordnung")
    axes[0].set_title("Die 26 sporadischen Gruppen", fontsize=10)
    axes[0].tick_params(axis="x", rotation=60, labelsize=8)
    axes[0].legend(fontsize=8)
    wv, wc = np.unique(weights, return_counts=True)
    axes[1].bar([str(v) for v in wv], wc)
    for v, c in zip(wv, wc):
        axes[1].text(str(v), c * 1.02, str(c), ha="center", fontsize=9)
    axes[1].set_xlabel("Gewicht (Zahl der Einsen)")
    axes[1].set_ylabel("Zahl der Codewörter")
    axes[1].set_title(f"Golay-Code: {len(codewords)} Wörter der Länge 24", fontsize=10)
    plt.tight_layout()
    plt.show()

    for name, G in mathieu.items():
        print(f"{name}: Ordnung {fmt(G.order()):>11s}  (Liste: {fmt(dict((s[0], s[1]) for s in sporadic)[name])})")
    print(f"Transitivität: M₁₂ ist {M12.transitivity_degree}-fach, M₂₄ ist {M24.transitivity_degree}-fach transitiv")
    print(f"Golay-Code: Gewichte {dict(zip(wv.tolist(), wc.tolist()))}, kleinster Abstand {weights[weights > 0].min()} → korrigiert 3 Fehler; die drei Erzeuger von M₂₄ erhalten den Code: {invariant}")
    print(f"Ordnung des Monsters: {sporadic[19][1]:.3e};  Verhältnis Monster / M₂₄ = {sporadic[19][1] / 244823040:.1e}")


def monster_moonshine():
    """13. Das Monster und Moonshine (Zellen 39 von grouptheory.ipynb)."""
    global E4, E4cube, N, _, axes, c, coeffs, decomp, e, eta24, fig, fm
    global i, inv, jq, k, ks, m, monster, p, r, series_mul, sigma3, total
    N = 30
    def series_mul(a, b):
        return [sum(a[i] * b[k - i] for i in range(k + 1)) for k in range(N + 1)]

    sigma3 = lambda m: sum(d ** 3 for d in range(1, m + 1) if m % d == 0)
    E4 = [1] + [240 * sigma3(m) for m in range(1, N + 1)]           # Eisenstein-Reihe E₄ = 1 + 240 Σ σ₃(n) qⁿ
    eta24 = [1] + [0] * N                                             # Π (1 − qⁿ)²⁴, ganzzahlig
    for m in range(1, N + 1):
        for _ in range(24):
            eta24 = [eta24[k] - (eta24[k - m] if k >= m else 0) for k in range(N + 1)]
    E4cube = series_mul(series_mul(E4, E4), E4)
    inv = [1] + [0] * N                                               # 1 / Π(1 − qⁿ)²⁴ als Reihe
    for k in range(1, N + 1):
        inv[k] = -sum(eta24[i] * inv[k - i] for i in range(1, k + 1))
    jq = series_mul(E4cube, inv)                                      # j(q) = q⁻¹ · E₄³ / Π(1 − qⁿ)²⁴; jq[k] ist der Koeffizient von q^(k−1)
    c = {k - 1: jq[k] for k in range(N + 1)}
    c[0] -= 744                                                       # j − 744: der konstante Term wird abgezogen
    r = [1, 196883, 21296876, 842609326, 18538750076, 19360062527, 293553734298]   # Dimensionen der kleinsten Darstellungen des Monsters
    decomp = {1: [1, 1], 2: [1, 1, 1], 3: [2, 2, 1, 1], 4: [3, 3, 1, 2, 1]}
    monster = sporadic[19][1]
    fm = factorint(monster)

    fig, axes = plt.subplots(1, 2, figsize=(16, 4.3))
    ks = np.arange(1, N)
    axes[0].semilogy(ks, [c[k] for k in ks], "o", label="Koeffizient c(n) von j(q)")
    axes[0].semilogy(ks, np.exp(4 * np.pi * np.sqrt(ks)) / (np.sqrt(2) * ks ** 0.75), "k--", lw=1, label="e^(4π√n) / (√2 n^(3/4))")
    axes[0].set_xlabel("n")
    axes[0].set_ylabel("c(n)")
    axes[0].set_title("j(q) = 1/q + 744 + 196884 q + 21493760 q² + …", fontsize=10)
    axes[0].legend(fontsize=8)
    axes[1].bar([str(p) for p in fm], list(fm.values()), color="tab:red")
    for i, (p, e) in enumerate(fm.items()):
        axes[1].text(i, e + 0.5, str(e), ha="center", fontsize=8)
    axes[1].set_xlabel("Primzahl p")
    axes[1].set_ylabel("Exponent in |M|")
    axes[1].set_title("|M| = 2⁴⁶ · 3²⁰ · 5⁹ · … · 71: genau die 15 supersingulären Primzahlen", fontsize=10)
    plt.tight_layout()
    plt.show()

    print(f"j(q) − 744 = 1/q + " + " + ".join(f"{c[k]} q^{k}" for k in range(1, 5)) + " + …")
    for k, coeffs in decomp.items():
        total = sum(a * b for a, b in zip(coeffs, r))
        print(f"c({k}) = {c[k]:>12d} = " + " + ".join(f"{a}·{b}" for a, b in zip(coeffs, r)) + f"  →  {total == c[k]}")
    print(f"|M| = {monster} ≈ {monster:.2e};  Primfaktoren: {sorted(fm)}")
    print(f"c(25)/Asymptotik = {c[25] / (np.exp(4 * np.pi * 5) / (np.sqrt(2) * 25 ** 0.75)):.4f}")


def point_groups():
    """14. Punktgruppen von Molekülen (Zellen 42 von grouptheory.ipynb)."""
    global C, Xc, Xm, a5_gen, atom_color, ax, bonds, buckyball, cayley, coords, dC, dmat
    global fig, g, gold, i, inv_, lim, mi, molecules, name, o, ops, p_
    global pg, point_group, pr, q_, ring, rotation_order, s_, symmetry_ops, table, types
    def symmetry_ops(types, X, tol=1e-4):
        """Alle orthogonalen Abbildungen, die das Molekül (Atomsorten types, Koordinaten X) auf sich abbilden.
    Zwei nicht kollineare Atome a, b und ihr Kreuzprodukt legen eine solche Abbildung fest; probiert werden alle passenden Bildpaare."""
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
                Yx = X @ R.T
                dist = np.linalg.norm(Yx[:, None, :] - X[None, :, :], axis=2)
                j = dist.argmin(axis=1)
                if dist[np.arange(len(X)), j].max() < tol and all(types[i] == types[k] for i, k in enumerate(j)) and not any(np.allclose(R, S, atol=1e-6) for S in ops):
                    ops.append(R)
        return ops

    def rotation_order(R):
        angle = np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1))
        return 1 if angle < 1e-6 else int(round(2 * np.pi / angle))

    def point_group(ops):
        """Schoenflies-Symbol aus der Liste der Symmetrieoperationen."""
        proper = [R for R in ops if np.linalg.det(R) > 0]
        improper = [R for R in ops if np.linalg.det(R) < 0]
        inversion = any(np.allclose(R, -np.eye(3)) for R in ops)
        mirrors = [R for R in improper if np.isclose(np.trace(R), 1)]
        if len(proper) == 60:
            return "Ih" if inversion else "I"
        if len(proper) == 24 and max(rotation_order(R) for R in proper) == 4:
            return "Oh" if inversion else "O"
        if len(proper) == 12 and sum(rotation_order(R) == 3 for R in proper) == 8:
            return ("Th" if inversion else "Td") if improper else "T"
        n = max(rotation_order(R) for R in proper)
        if n == 1:
            return "Cs" if mirrors else ("Ci" if inversion else "C1")
        main = next(R for R in proper if rotation_order(R) == n)
        w_, v_ = np.linalg.eig(main)
        axis = np.real(v_[:, np.argmin(np.abs(w_ - 1))])
        perp_c2 = [R for R in proper if rotation_order(R) == 2 and abs(np.real(np.linalg.eig(R)[1][:, np.argmin(np.abs(np.linalg.eig(R)[0] - 1))]) @ axis) < 1e-6]
        normals = [np.real(np.linalg.eig(R)[1][:, np.argmin(np.abs(np.linalg.eig(R)[0] + 1))]) for R in mirrors]
        sigma_h = any(abs(abs(nv @ axis) - 1) < 1e-6 for nv in normals)
        sigma_v = any(abs(nv @ axis) < 1e-6 for nv in normals)
        letter = "D" if len(perp_c2) == n else "C"
        if sigma_h:
            return f"{letter}{n}h"
        if sigma_v:
            return f"{letter}{n}{'d' if letter == 'D' else 'v'}"
        if improper and letter == "C":
            return f"S{2 * n}"
        return f"{letter}{n}"

    gold = (1 + 5 ** 0.5) / 2
    def buckyball():
        """C₆₀: alle zyklischen Vertauschungen von (0, ±1, ±3φ), (±1, ±(2+φ), ±2φ), (±φ, ±2, ±φ³)."""
        pts = set()
        for v in [(0, 1, 3 * gold), (1, 2 + gold, 2 * gold), (gold, 2, gold ** 3)]:
            for sh in range(3):
                w3 = v[sh:] + v[:sh]
                for sg in itertools.product([1, -1], repeat=3):
                    pts.add(tuple(round(s * x, 9) for s, x in zip(sg, w3)))
        return np.array(sorted(pts)) * 0.7

    ring = lambda r, k, z=0.0, off=0.0: [[r * np.cos(2 * np.pi * i / k + off), r * np.sin(2 * np.pi * i / k + off), z] for i in range(k)]
    molecules = {
        "H₂O": (["O", "H", "H"], [[0, 0, 0.117], [0.757, 0, -0.469], [-0.757, 0, -0.469]]),
        "H₂O₂": (["O", "O", "H", "H"], [[0.74, 0, 0], [-0.74, 0, 0], [0.98, 0.9 * np.cos(0.97), 0.9 * np.sin(0.97)], [-0.98, 0.9 * np.cos(0.97), -0.9 * np.sin(0.97)]]),
        "NH₃": (["N", "H", "H", "H"], [[0, 0, 0.38]] + ring(0.94, 3)),
        "Ethan (gestaffelt)": (["C", "C"] + ["H"] * 6, [[0, 0, 0.77], [0, 0, -0.77]] + ring(1.02, 3, 1.16) + ring(1.02, 3, -1.16, np.pi / 3)),
        "CH₄": (["C"] + ["H"] * 4, (np.array([[0, 0, 0], [1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]]) * 0.63).tolist()),
        "Benzol C₆H₆": (["C"] * 6 + ["H"] * 6, ring(1.39, 6) + ring(2.48, 6)),
        "SF₆": (["S"] + ["F"] * 6, [[0, 0, 0], [1.56, 0, 0], [-1.56, 0, 0], [0, 1.56, 0], [0, -1.56, 0], [0, 0, 1.56], [0, 0, -1.56]]),
        "C₆₀ (Fulleren)": (["C"] * 60, buckyball().tolist()),
    }
    atom_color = {"H": "lightgrey", "C": "black", "N": "tab:blue", "O": "tab:red", "S": "gold", "F": "tab:green"}
    fig = plt.figure(figsize=(18, 8.5))
    table = []
    for i, (name, (types, coords)) in enumerate(molecules.items()):
        Xm = np.array(coords, dtype=float)
        ops = symmetry_ops(types, Xm)
        pg = point_group(ops)
        table.append((name, len(ops), sum(np.linalg.det(R) > 0 for R in ops), any(np.allclose(R, -np.eye(3)) for R in ops),
                      sum(np.linalg.det(R) < 0 and np.isclose(np.trace(R), 1) for R in ops), pg))
        ax = fig.add_subplot(2, 4, i + 1, projection="3d")
        Xc = Xm - Xm.mean(axis=0)
        dmat = np.linalg.norm(Xc[:, None] - Xc[None], axis=2)
        for p_, q_ in itertools.combinations(range(len(Xc)), 2):
            if dmat[p_, q_] < 1.75 and not (types[p_] == "H" and types[q_] == "H"):
                ax.plot(*Xc[[p_, q_]].T, color="grey", lw=1)
        ax.scatter(*Xc.T, c=[atom_color[t] for t in types], s=[60 if t == "H" else 120 for t in types], edgecolor="k", depthshade=False)
        ax.set_title(f"{name}: {pg}, Ordnung {len(ops)}", fontsize=10)
        ax.set_box_aspect([1, 1, 1])
        lim = np.abs(Xc).max() * 1.05
        ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_zlim(-lim, lim)
        ax.view_init(elev=20, azim=35)
        ax.set_axis_off()
    plt.tight_layout()
    plt.show()

    a5_gen = (Permutation([[0, 1, 2, 3, 4]]), Permutation([[0, 1], [2, 3]], size=5))      # Erzeuger der Ordnungen 5 und 2, Produkt der Ordnung 3
    cayley = nx.Graph()
    for g in PermutationGroup(list(a5_gen)).generate():
        for s_ in a5_gen:
            cayley.add_edge(tuple(g.array_form), tuple((g * s_).array_form))
    C = np.array(molecules["C₆₀ (Fulleren)"][1])
    dC = np.linalg.norm(C[:, None] - C[None], axis=2)
    bonds = nx.Graph([(i, j) for i in range(60) for j in range(i + 1, 60) if dC[i, j] < 1.75])
    print(f"Cayley-Graph von A₅ ({cayley.number_of_nodes()} Ecken, {cayley.number_of_edges()} Kanten) isomorph zum C₆₀-Gerüst ({bonds.number_of_nodes()}, {bonds.number_of_edges()}): {nx.is_isomorphic(cayley, bonds)}")
    print(f"{'Molekül':20s} {'Ordnung':>7s} {'Drehungen':>9s} {'Inversion':>9s} {'Spiegel':>7s}  Punktgruppe   chiral")
    for name, o, pr, inv_, mi, pg in table:
        print(f"{name:20s} {o:7d} {pr:9d} {str(inv_):>9s} {mi:7d}  {pg:12s}  {'ja' if o == pr else 'nein'}")


def crystals():
    """15. Kristalle: die kristallographische Einschränkung und Tapetengruppen (Zellen 45 von grouptheory.ipynb)."""
    global C3ops, D4ops, D6ops, allowed, axes, fig, mirror, motif, nr, s_, trace, wallpaper
    nr = np.arange(1, 13)
    trace = 2 * np.cos(2 * np.pi / nr)
    allowed = np.isclose(trace, np.round(trace))

    def wallpaper(ax, point_ops, a1, a2, motif, color, reps=3):
        """Zeichnet ein Muster: Motiv × Punktgruppe, dann über das Gitter verschoben."""
        for m, n_ in itertools.product(range(-reps, reps + 1), repeat=2):
            t = m * np.array(a1) + n_ * np.array(a2)
            for Rm in point_ops:
                pts = motif @ Rm.T + t
                ax.plot(pts[:, 0], pts[:, 1], color=color, lw=1)
        ax.set_aspect("equal")
        ax.set_xlim(-2.2, 2.2); ax.set_ylim(-2.2, 2.2)
        ax.set_xticks([]); ax.set_yticks([])

    s_ = np.linspace(0, 1, 60)
    motif = np.c_[0.12 + 0.3 * s_, 0.05 + 0.12 * np.sin(3 * np.pi * s_) * s_]
    mirror = np.diag([1.0, -1.0])
    D4ops = [np.real(M) for M in matrix_group([rot2(np.pi / 2), mirror])]
    D6ops = [np.real(M) for M in matrix_group([rot2(np.pi / 3), mirror])]
    C3ops = [np.real(M) for M in matrix_group([rot2(2 * np.pi / 3)])]

    fig, axes = plt.subplots(1, 4, figsize=(19, 4.6))
    axes[0].bar(nr, trace, color=["tab:green" if a else "tab:red" for a in allowed])
    axes[0].axhline(0, color="k", lw=0.5)
    axes[0].set_xticks(nr)
    axes[0].set_xlabel("Drehordnung n (Drehung um 360°/n)")
    axes[0].set_ylabel("Spur 2·cos(2π/n)")
    axes[0].set_title("Grün: ganzzahlig, also mit einem Gitter verträglich", fontsize=10)
    wallpaper(axes[1], D4ops, (1, 0), (0, 1), motif, "tab:blue")
    axes[1].set_title(f"p4m: Quadratgitter, Punktgruppe D₄ ({len(D4ops)} Operationen)", fontsize=10)
    wallpaper(axes[2], D6ops, (1, 0), (0.5, np.sqrt(3) / 2), motif * 0.75, "tab:red")
    axes[2].set_title(f"p6m: Sechseckgitter, Punktgruppe D₆ ({len(D6ops)})", fontsize=10)
    wallpaper(axes[3], C3ops, (1, 0), (0.5, np.sqrt(3) / 2), motif * 0.9, "tab:purple")
    axes[3].set_title(f"p3: nur Drehungen um 120° ({len(C3ops)}), keine Spiegel", fontsize=10)
    plt.tight_layout()
    plt.show()

    print(f"Mit einem Gitter verträgliche Drehordnungen: {list(nr[allowed])}  (2cos(2π/n) ganzzahlig)")
    print(f"Zum Beispiel n = 5: 2cos(72°) = {2 * np.cos(2 * np.pi / 5):.6f} = (√5 − 1)/2, nicht ganzzahlig → kein Kristall mit fünfzähliger Achse")
    print("Bekannte Anzahlen: 10 Punktgruppen und 17 Tapetengruppen in der Ebene; 32 Kristallklassen, 14 Bravais-Gitter und 230 Raumgruppen im Raum")


def pauli_clifford():
    """16. Gruppen in der Quanteninformation: Pauli- und Clifford-Gruppe (Zellen 48 von grouptheory.ipynb)."""
    global Hd, I2, Rb, Sg, U, V, ang, axes, axis, bloch, classes, clifford
    global clifford_size, comm, fig, frontier, gen, new, pauli_group, paulis3, phase_free_key, qubits, s4_classes
    I2 = np.eye(2)
    Hd = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
    Sg = np.diag([1, 1j])
    pauli_group = matrix_group([X, Y, Z])                             # mit den Phasen ±1, ±i

    def phase_free_key(U):
        k = np.argmax(np.abs(U.ravel()) > 1e-9)
        return key(U / (U.ravel()[k] / abs(U.ravel()[k])))

    clifford, frontier = {phase_free_key(I2): I2}, [I2]               # Clifford-Gruppe ohne globale Phase, erzeugt von H und S
    while frontier:
        new = []
        for U in frontier:
            for gen in (Hd, Sg):
                V = gen @ U
                if phase_free_key(V) not in clifford:
                    clifford[phase_free_key(V)] = V
                    new.append(V)
        frontier = new
    paulis3 = [X, Y, Z]
    bloch = [np.real(np.array([[np.trace(paulis3[i] @ U @ paulis3[j] @ U.conj().T) / 2 for j in range(3)] for i in range(3)])) for U in clifford.values()]
    classes = {"Identität": 0, "120° (Ecken-Achse)": 0, "90° (Flächen-Achse)": 0, "180° (Flächen-Achse)": 0, "180° (Kanten-Achse)": 0}
    for Rb in bloch:
        ang = np.degrees(np.arccos(np.clip((np.trace(Rb) - 1) / 2, -1, 1)))
        axis = Rotation.from_matrix(Rb).as_rotvec()
        if ang < 1:
            classes["Identität"] += 1
        elif abs(ang - 120) < 1:
            classes["120° (Ecken-Achse)"] += 1
        elif abs(ang - 90) < 1:
            classes["90° (Flächen-Achse)"] += 1
        elif np.sum(np.abs(axis) > 1e-6) == 1:
            classes["180° (Flächen-Achse)"] += 1
        else:
            classes["180° (Kanten-Achse)"] += 1
    s4_classes = {"Identität": 1, "3-Zyklen": 8, "4-Zyklen": 6, "Doppeltranspositionen": 3, "Transpositionen": 6}
    qubits = np.arange(1, 9)
    clifford_size = [float(2 ** (n * n + 2 * n) * np.prod([4 ** j - 1 for j in range(1, n + 1)], dtype=object)) for n in map(int, qubits)]

    fig, axes = plt.subplots(1, 2, figsize=(16, 4.3))
    axes[0].bar(list(classes), list(classes.values()), alpha=0.7, label="Clifford-Gruppe (Drehungen der Bloch-Kugel)")
    axes[0].plot(list(classes), list(s4_classes.values()), "ko", ms=8, label="Klassengrößen von S₄")
    axes[0].set_ylabel("Zahl der Elemente")
    axes[0].set_title(f"Die {len(clifford)} Clifford-Operationen sind die Drehungen des Oktaeders", fontsize=10)
    axes[0].tick_params(axis="x", labelsize=8)
    axes[0].legend(fontsize=8)
    axes[1].semilogy(qubits, clifford_size, "o-", label="Clifford-Gruppe (ohne Phase)")
    axes[1].semilogy(qubits, 4.0 ** qubits, "s-", label="Pauli-Gruppe (ohne Phase): 4ⁿ")
    axes[1].set_xlabel("Zahl der Qubits n")
    axes[1].set_ylabel("Zahl der Elemente")
    axes[1].set_title("Größe der Gruppen mit der Zahl der Qubits", fontsize=10)
    axes[1].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    comm = sum(1 for A in pauli_group for B in pauli_group if np.allclose(A @ B, B @ A))
    print(f"Pauli-Gruppe mit Phasen: {len(pauli_group)} Elemente; Paare, die vertauschen: {comm} von {len(pauli_group) ** 2}; ohne Phase bleibt ℤ₂ × ℤ₂ (4 Elemente)")
    print(f"Clifford-Gruppe eines Qubits ohne Phase: {len(clifford)} Elemente;  Klassen nach Drehwinkel {classes}")
    print(f"Größe der n-Qubit-Clifford-Gruppe (ohne Phase): n = 1: {clifford_size[0]:.0f}, n = 2: {clifford_size[1]:.0f}, n = 3: {clifford_size[2]:.0f}")


def rotations():
    """17. Lie-Gruppen: zufällige Drehungen und die doppelte Überlagerung (Zellen 51 von grouptheory.ipynb)."""
    global U2pi, alpha, axes, dims, euler, euler_angles, f, fig, haar, haar_angles, lab, mk
    global nd, rng, th
    rng = np.random.default_rng(15)
    haar = stats.special_ortho_group.rvs(3, size=50_000, random_state=rng)
    haar_angles = Rotation.from_matrix(haar).magnitude()
    euler = rng.uniform([0, 0, 0], [2 * np.pi, np.pi, 2 * np.pi], size=(50_000, 3))   # gleichverteilte Euler-Winkel: nicht gleichverteilt auf SO(3)
    euler_angles = Rotation.from_euler("zyz", euler).magnitude()
    th = np.linspace(0, np.pi, 200)
    alpha = np.linspace(0, 4 * np.pi, 400)
    dims = {"GL(n,ℝ): n²": lambda n: n * n, "SL(n,ℝ): n² − 1": lambda n: n * n - 1, "SO(n): n(n−1)/2": lambda n: n * (n - 1) // 2,
            "U(n): n²": lambda n: n * n, "SU(n): n² − 1": lambda n: n * n - 1, "Sp(2n,ℝ): n(2n+1)": lambda n: n * (2 * n + 1)}

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.3))
    axes[0].hist(haar_angles, bins=50, density=True, alpha=0.6, label="Haar-Maß (scipy special_ortho_group)")
    axes[0].hist(euler_angles, bins=50, density=True, histtype="step", lw=1.5, label="gleichverteilte Euler-Winkel")
    axes[0].plot(th, (1 - np.cos(th)) / np.pi, "k-", label="(1 − cos θ)/π")
    axes[0].set_xlabel("Drehwinkel θ")
    axes[0].set_ylabel("Dichte")
    axes[0].set_title("Zufällige Drehungen in SO(3)", fontsize=10)
    axes[0].legend(fontsize=8)
    axes[1].plot(alpha / np.pi, 1 + 2 * np.cos(alpha), label="SO(3): Spur der Drehmatrix 1 + 2cos α")
    axes[1].plot(alpha / np.pi, 2 * np.cos(alpha / 2), label="SU(2): Spur von e^(−iαZ/2) = 2cos(α/2)")
    axes[1].axvline(2, color="grey", ls=":")
    axes[1].set_xlabel("Drehwinkel α / π")
    axes[1].set_ylabel("Spur")
    axes[1].set_title("Nach 360° ist die Drehung zurück, der Spin hat das Vorzeichen gewechselt", fontsize=10)
    axes[1].legend(fontsize=8)
    nd = np.arange(1, 9)
    for (lab, f), mk in zip(dims.items(), "osd^v<"):
        axes[2].plot(nd, [f(int(k)) for k in nd], marker=mk, label=lab)
    axes[2].set_xlabel("n")
    axes[2].set_ylabel("Dimension (Zahl der Parameter)")
    axes[2].set_title("Dimensionen der klassischen Lie-Gruppen", fontsize=10)
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    U2pi = np.diag([np.exp(-1j * np.pi), np.exp(1j * np.pi)])
    print(f"Mittlerer Drehwinkel: Haar {haar_angles.mean():.4f} (Theorie π/2 + 2/π = {np.pi / 2 + 2 / np.pi:.4f}), gleichverteilte Euler-Winkel {euler_angles.mean():.4f}")
    print(f"Kolmogorov-Smirnov gegen (1 − cos θ)/π: Haar p = {stats.kstest(haar_angles, lambda t: (t - np.sin(t)) / np.pi).pvalue:.2f}, Euler p = {stats.kstest(euler_angles, lambda t: (t - np.sin(t)) / np.pi).pvalue:.1e}")
    print(f"SU(2): Drehung um 2π ergibt {np.round(np.real(U2pi), 6).tolist()} = −1, erst 4π ergibt +1;  Haar-zufällige SO(3)-Matrizen orthogonal mit Determinante 1: "
          f"{np.allclose(haar[0] @ haar[0].T, np.eye(3)) and np.isclose(np.linalg.det(haar[0]), 1)}")
