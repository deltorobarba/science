"""Vier Algebren aus einer für heisenbergweyl.ipynb: Tensoralgebra T(V) geteilt durch ein Ideal aus Grad 2.

Ein Element der Tensoralgebra ist eine Summe von Wörtern in den Erzeugern e_1 … e_m (ohne Regeln, nicht kommutativ).
Das Ideal wird als Ersetzungsregel benutzt: Steht ein größerer Buchstabe vor einem kleineren, wird getauscht,
    e_i e_j → s · e_j e_i + B_ij · 1   (i > j),        und bei s = −1 zusätzlich   e_i e_i → B_ii / 2.
Zwei Schalter: das Vorzeichen s des Tauschs und die Form B. Sie ergeben die vier Algebren
    s = +1, B = 0: symmetrische Algebra Sym(V) (Polynome, klassisch)
    s = +1, B = ω antisymmetrisch: Weyl-Algebra (Bosonen, [q, p] = iħ)
    s = −1, B = 0: äußere Algebra Λ(V) (Differentialformen)
    s = −1, B = 2g symmetrisch: Clifford-Algebra (Fermionen, Majoranas mit γ_i γ_j + γ_j γ_i = 2 δ_ij).
Zum Zählen großer Lie-Algebren dienen die geschlossenen Formen derselben Regel (normal geordnetes Produkt q^a p^b in der
Weyl-Algebra, Monome als Bitmasken in der Clifford-Algebra); `check_closed_forms` vergleicht sie mit der Ersetzungsregel.
"""
from collections import defaultdict
from math import comb, factorial

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, NullFormatter, ScalarFormatter


class Algebra:
    """T(V)/I mit Erzeugern `names`, Tauschvorzeichen s und Form B (Matrix m × m)."""

    def __init__(self, names, s, B):
        self.names, self.s, self.B = list(names), s, np.asarray(B, complex)

    def normal(self, elem):
        """Wendet die Ersetzungsregel an, bis jedes Wort aufsteigend geordnet ist; gibt {Wort: Koeffizient} zurück."""
        out, todo = defaultdict(complex), list(elem.items())
        while todo:
            w, c = todo.pop()
            for k in range(len(w) - 1):
                i, j = w[k], w[k + 1]
                if i > j:
                    todo.append((w[:k] + (j, i) + w[k + 2:], self.s * c))
                    if self.B[i, j] != 0:
                        todo.append((w[:k] + w[k + 2:], self.B[i, j] * c))
                    break
                if i == j and self.s == -1:
                    if self.B[i, i] != 0:
                        todo.append((w[:k] + w[k + 2:], self.B[i, i] / 2 * c))
                    break
            else:
                out[w] += c
        return {w: c for w, c in out.items() if abs(c) > 1e-12}

    def word(self, text):
        """'qp' oder 'q p' → Element mit diesem einen Wort."""
        return {tuple(self.names.index(ch) for ch in text.replace(" ", "")): 1.0}

    def add(self, *elems, coeffs=None):
        out = defaultdict(complex)
        for e, a in zip(elems, coeffs or [1] * len(elems)):
            for w, c in e.items():
                out[w] += a * c
        return {w: c for w, c in out.items() if abs(c) > 1e-12}

    def mul(self, a, b):
        out = defaultdict(complex)
        for u, c in a.items():
            for v, d in b.items():
                out[u + v] += c * d
        return self.normal(out)

    def comm(self, a, b):
        return self.add(self.mul(a, b), self.mul(b, a), coeffs=[1, -1])

    def show(self, e):
        """Lesbare Form, z. B. q² + 2·qp + p² − i."""
        if not e:
            return "0"
        sup = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
        parts = []
        for w, c in sorted(e.items(), key=lambda t: (-len(t[0]), t[0])):
            c = complex(np.round(c, 10))
            mono, k = "", 0
            while k < len(w):
                r = k
                while r < len(w) and w[r] == w[k]:
                    r += 1
                mono += self.names[w[k]] + (str(r - k).translate(sup) if r - k > 1 else "")
                k = r
            if c.imag == 0:
                num, neg = f"{abs(c.real):g}", c.real < 0
                term = mono if (num == "1" and mono) else (num + "·" + mono if mono else num)
            elif c.real == 0:
                num, neg = f"{abs(c.imag):g}", c.imag < 0
                term = ("i" if num == "1" else num + "i") + ("·" + mono if mono else "")
            else:
                neg, term = False, f"({c.real:g}{c.imag:+g}i)" + ("·" + mono if mono else "")
            parts.append(("− " if neg else "+ ") + term)
        out = " ".join(parts)
        return out[2:] if out.startswith("+ ") else "−" + out[2:]


def four_algebras(hbar=1.0):
    """Die vier Algebren mit zwei Erzeugern (q, p bzw. γ1, γ2), als Dictionary Name → Algebra."""
    w = np.array([[0, 1j * hbar], [-1j * hbar, 0]])        # [q, p] = iħ  →  p q → q p − iħ
    g = 2 * np.eye(2)                                     # γ_i γ_j + γ_j γ_i = 2 δ_ij
    return {"Sym(V), klassisch": Algebra("qp", +1, np.zeros((2, 2))),
            "Weyl, Bosonen": Algebra("qp", +1, w),
            "Λ(V), Formen": Algebra("ab", -1, np.zeros((2, 2))),
            "Clifford, Fermionen": Algebra("ab", -1, g)}


def degree(e):
    return max((len(w) for w in e), default=-1)


# ---- geschlossene Formen der Regeln, zum Zählen

def weyl_mul(a, b, hbar=1.0):
    """Produkt normal geordneter Polynome {(a, b): c} für q^a p^b: p^b q^c = Σ_k k!·C(b,k)·C(c,k)·(−iħ)^k q^(c−k) p^(b−k)."""
    out = defaultdict(complex)
    for (a1, b1), c1 in a.items():
        for (a2, b2), c2 in b.items():
            for k in range(min(b1, a2) + 1):
                out[(a1 + a2 - k, b1 + b2 - k)] += c1 * c2 * factorial(k) * comb(b1, k) * comb(a2, k) * (-1j * hbar) ** k
    return {m: c for m, c in out.items() if abs(c) > 1e-12}


def weyl_comm(a, b):
    x, y = weyl_mul(a, b), weyl_mul(b, a)
    out = {m: x.get(m, 0) - y.get(m, 0) for m in set(x) | set(y)}
    return {m: c for m, c in out.items() if abs(c) > 1e-12}


def _independent(elems):
    """Linear unabhängige Auswahl (Gram-Schmidt auf den Koeffizientenvektoren)."""
    keys = sorted({m for e in elems for m in e})
    idx = {m: i for i, m in enumerate(keys)}
    basis, keep = [], []
    for e in elems:
        v = np.zeros(len(keys), complex)
        for m, c in e.items():
            v[idx[m]] = c
        for b in basis:
            v = v - (b.conj() @ v) * b
        n = np.linalg.norm(v)
        if n > 1e-9 * max(1.0, max(abs(c) for c in e.values())):
            basis.append(v / n)
            keep.append(e)
    return keep


def boson_closure(generators, depth=5):
    """Dimension des Raums aus den Erzeugern und ihren verschachtelten Kommutatoren je Tiefe, und der höchste Grad."""
    S = _independent(list(generators))
    dims, degs = [len(S)], [max(a + b for e in S for (a, b) in e)]
    for _ in range(depth):
        new = [weyl_comm(x, y) for i, x in enumerate(S) for y in S[i + 1:]]
        S = _independent(S + [e for e in new if e])
        dims.append(len(S))
        degs.append(max(a + b for e in S for (a, b) in e))
    return dims, degs


def fermion_closure(modes, quartic=True):
    """Dimension der Lie-Algebra aus allen quadratischen Majorana-Monomen γ_i γ_j (und einem quartischen γ0γ1γ2γ3).

    Monome als Bitmasken: γ_A γ_B = (−1)^(|A||B| − |A∩B|) γ_B γ_A. Der Kommutator zweier Monome ist null oder ein Vielfaches
    von γ_(A xor B); die erzeugte Lie-Algebra wird deshalb von Monomen aufgespannt, und Zählen heißt Masken sammeln.
    """
    m = 2 * modes
    gens = [(1 << i) | (1 << j) for i in range(m) for j in range(i + 1, m)]
    if quartic and m >= 4:
        gens.append(0b1111)
    found = set(gens)
    table = np.array([bin(i).count("1") for i in range(1 << 16)], dtype=np.int64)
    pop = lambda x: table[x & 0xFFFF] + table[(x >> 16) & 0xFFFF]
    frontier = list(found)
    while frontier:
        arr = np.array(sorted(found), dtype=np.int64)
        pa = pop(arr)
        new = set()
        for A in frontier:
            odd = (int(pop(np.int64(A))) * pa - pop(arr & A)) % 2 == 1
            new.update(int(x) for x in (arr[odd] ^ A))
        frontier = [x for x in new if x not in found]
        found.update(frontier)
    return len(found)


def clifford_mul_mask(A, B):
    """Produkt zweier Majorana-Monome als Bitmasken: Vorzeichen aus dem Sortieren, gleiche Buchstaben werden zu 1."""
    sign, a = 1, A
    for j in range(B.bit_length()):
        if B >> j & 1:
            if bin(a >> (j + 1)).count("1") % 2:             # γ_j an allen größeren Buchstaben von a vorbeischieben
                sign = -sign
            a ^= 1 << j
    return sign, a


def check_closed_forms(max_deg=4, seed=0):
    """Vergleicht die geschlossenen Formen mit der Ersetzungsregel an zufälligen Monomen; gibt die größte Abweichung."""
    rng = np.random.default_rng(seed)
    alg = four_algebras()
    W, C = alg["Weyl, Bosonen"], Algebra("abcdef", -1, 2 * np.eye(6))
    err = 0.0
    for _ in range(40):
        a, b, c, d = rng.integers(0, max_deg + 1, 4)
        x = W.mul(W.word("q" * a + "p" * b), W.word("q" * c + "p" * d))
        y = weyl_mul({(a, b): 1}, {(c, d): 1})
        x = {(w.count(0), w.count(1)): v for w, v in x.items()}
        err = max(err, max(abs(x.get(k, 0) - y.get(k, 0)) for k in set(x) | set(y)))
        A, B = (int(v) for v in rng.integers(0, 64, 2))
        lett = lambda M: "".join("abcdef"[i] for i in range(6) if M >> i & 1)
        z = C.mul(C.word(lett(A)), C.word(lett(B)))
        s, M = clifford_mul_mask(A, B)
        err = max(err, abs(z.get(tuple(i for i in range(6) if M >> i & 1), 0) - s))
    return err


def degree_drop(pairs=600, max_deg=5, seed=0):
    """Grad des Kommutators zweier zufälliger Monome (Weyl; Clifford nur gerade Monome), verglichen mit a + b."""
    rng = np.random.default_rng(seed)
    res = {"Weyl": [], "Clifford": []}
    for _ in range(pairs):
        a, b, c, d = rng.integers(0, max_deg + 1, 4)
        k = weyl_comm({(a, b): 1}, {(c, d): 1})
        if k:
            res["Weyl"].append(max(x + y for x, y in k) - (a + b + c + d))
        A, B = (int(v) for v in rng.integers(1, 1 << 10, 2))
        if bin(A).count("1") % 2 or bin(B).count("1") % 2:      # nur gerade Operatoren (Paritätsauswahlregel)
            continue
        s1, M = clifford_mul_mask(A, B)
        s2, _ = clifford_mul_mask(B, A)
        if s1 != s2:
            res["Clifford"].append(bin(M).count("1") - bin(A).count("1") - bin(B).count("1"))
    return {k: np.array(v) for k, v in res.items()}


def plot_algebras(depth=5, modes=(3, 4, 5, 6, 7)):
    """Ausgabe: dasselbe Produkt in vier Algebren, Grad-Abfall; Bilder: Abschluss bei Bosonen und Fermionen."""
    alg = four_algebras()
    print("Dasselbe Wort in vier Quotienten von T(V) (zwei Erzeuger):")
    for name, A in alg.items():
        x, y = A.names
        e = A.add(A.word(x), A.word(y))
        sq = A.mul(e, e)
        print(f"  {name:22s} ({x} + {y})² = {A.show(sq):24s}  {y}{x} = {A.show(A.normal(A.word(y + x)))}")
    print(f"Geschlossene Formen gegen die Ersetzungsregel: größte Abweichung {check_closed_forms():.0e}")
    drop = degree_drop()
    for k, v in drop.items():
        print(f"  {k}: {len(v)} Paare mit Kommutator ≠ 0; Grad des Kommutators minus (Grad A + Grad B): "
              + ", ".join(f"{d:+d} in {np.sum(v == d)}" for d in sorted(set(v), reverse=True)))
    q, p, one = (1, 0), (0, 1), (0, 0)
    sets = {"{q, p}": [{q: 1}, {p: 1}],
            "{q², p²}": [{(2, 0): 1}, {(0, 2): 1}],
            "{q², p², qp, q, p}": [{(2, 0): 1}, {(0, 2): 1}, {(1, 1): 1}, {q: 1}, {p: 1}],
            "{q², p², q³}": [{(2, 0): 1}, {(0, 2): 1}, {(3, 0): 1}]}
    bos = {k: boson_closure(v, depth) for k, v in sets.items()}
    print("Bosonen, eine Mode: Dimension der erzeugten Lie-Algebra je Tiefe der verschachtelten Kommutatoren (höchster Grad)")
    for k, (d, g) in bos.items():
        print(f"  {k:20s}: " + ", ".join(f"{a} ({b})" for a, b in zip(d, g)))
    fer = {n: (fermion_closure(n, quartic=False), fermion_closure(n)) for n in modes}
    print("Fermionen, n Moden (2n Majoranas): Grad 2 allein | Grad 2 und ein Term γ0γ1γ2γ3 vom Grad 4")
    for n, (a, b) in fer.items():
        print(f"  n = {n}: {a:5d} (so({2 * n}) hat {n * (2 * n - 1)}) | {b:5d} (gerade Monome ohne 1 und Parität: {2 ** (2 * n - 1) - 2})")

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    ax = axes[0]
    styles = [("tab:blue", "--", "s", 9), ("tab:green", "-", "o", 5), ("tab:purple", "-", "o", 5), ("tab:red", "-", "o", 5)]
    for (k, (d, g)), (c, ls, mk, ms) in zip(bos.items(), styles):
        ax.semilogy(range(len(d)), d, ls, marker=mk, ms=ms, mfc="none" if mk == "s" else c, color=c,
                    label=f"{k}, höchster Grad am Ende {g[-1]}")
    ax.yaxis.set_major_locator(LogLocator(subs=(1.0, 2.0, 5.0)))
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_xlabel("Tiefe der verschachtelten Kommutatoren")
    ax.set_ylabel("Dimension der erzeugten Lie-Algebra")
    ax.set_title("Bosonen (Weyl-Algebra): Grad ≤ 2 schließt, Grad 3 wächst", fontsize=10)
    ax.legend(fontsize=8)
    ax = axes[1]
    ns = np.array(list(fer))
    ax.semilogy(ns, [fer[n][0] for n in ns], "o-", color="tab:green", label="nur Grad 2: so(2n), n(2n−1)")
    ax.semilogy(ns, [fer[n][1] for n in ns], "s-", color="tab:red", label="mit einem Term vom Grad 4")
    ax.semilogy(ns, 2.0 ** (2 * ns - 1) - 2, ":", color="grey", lw=2, label="2^(2n−1) − 2: alle geraden Monome außer 1 und Parität")
    ax.set_xticks(ns)
    ax.set_xlabel("Zahl der fermionischen Moden n")
    ax.set_ylabel("Dimension der erzeugten Lie-Algebra")
    ax.set_title("Fermionen (Clifford-Algebra): Grad 2 polynomiell, Grad 4 exponentiell", fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()
    return bos, fer
