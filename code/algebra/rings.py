"""Ringe, Körper und kommutative Algebra: Restklassenringe, euklidischer Algorithmus und chinesischer Restsatz, Gaußsche Zahlen, endliche Körper, Reed-Solomon, Gröbner-Basen, Körpererweiterungen, Galois-Gruppen, p-adische Zahlen, Reziprozität, Quaternionen, Smith-Normalform und Post-Quanten-Kryptographie.

Für algebra.ipynb aus rings_fields.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, residue_rings, euclid_crt, gaussian_integers, irreducible_polys, finite_fields, reed_solomon, groebner_bases, field_extensions, galois, padic, reciprocity, quaternions, smith_form, post_quantum.
"""
import itertools, time, warnings
from math import gcd, isqrt, log
import numpy as np
import matplotlib.pyplot as plt
from sympy import (symbols, Poly, Matrix, ZZ, factor_list, groebner, minimal_polynomial, sqrt, cos, pi, primerange,
                   isprime, factorint, totient, mobius, Rational, real_roots, solve)
from sympy.polys.numberfields.galoisgroups import galois_group
from sympy.matrices.normalforms import smith_normal_form
from sympy.ntheory import sqrt_mod, primitive_root, n_order
from sympy.functions.combinatorial.numbers import legendre_symbol
from sympy.utilities.exceptions import SymPyDeprecationWarning
from sympy.ntheory.modular import crt


def load():
    """18. Daten (Zellen 4 von rings_fields.ipynb)."""
    global polymul_mod, rank_mod_p, solve_mod_p, x, y
    # Alles hier (numpy, scipy, sympy, matplotlib) ist in Colab vorinstalliert
    warnings.filterwarnings("ignore", category=SymPyDeprecationWarning)   # sympy vergleicht intern Restklassen (factor_list modulo p); harmlos
    x, y = symbols("x y")

    def solve_mod_p(A, b, p):
        """Löst A·z = b über dem Körper 𝔽_p mit Gauß-Elimination; freie Variablen werden 0 gesetzt. Gibt None zurück, wenn das System widersprüchlich ist."""
        M = np.concatenate([np.array(A, dtype=np.int64) % p, np.array(b, dtype=np.int64).reshape(-1, 1) % p], axis=1)
        rows, cols = M.shape[0], M.shape[1] - 1
        pivots, r = [], 0
        for c in range(cols):
            nz = [i for i in range(r, rows) if M[i, c]]
            if not nz:
                continue
            M[[r, nz[0]]] = M[[nz[0], r]]
            M[r] = M[r] * pow(int(M[r, c]), -1, p) % p
            for i in range(rows):
                if i != r and M[i, c]:
                    M[i] = (M[i] - M[i, c] * M[r]) % p
            pivots.append(c)
            r += 1
            if r == rows:
                break
        if any(M[i, -1] for i in range(r, rows)):
            return None
        z = np.zeros(cols, dtype=np.int64)
        for i, c in enumerate(pivots):
            z[c] = M[i, -1]
        return z

    def rank_mod_p(M, p):
        """Rang einer ganzzahligen Matrix über 𝔽_p (Gauß-Elimination)."""
        M = np.array(M, dtype=np.int64) % p
        r = 0
        for c in range(M.shape[1]):
            nz = [i for i in range(r, M.shape[0]) if M[i, c]]
            if not nz:
                continue
            M[[r, nz[0]]] = M[[nz[0], r]]
            M[r] = M[r] * pow(int(M[r, c]), -1, p) % p
            for i in range(M.shape[0]):
                if i != r and M[i, c]:
                    M[i] = (M[i] - M[i, c] * M[r]) % p
            r += 1
        return r

    def polymul_mod(a, b, q, n):
        """Produkt im Ring ℤ_q[x]/(xⁿ + 1): gewöhnliches Produkt, dann xⁿ = −1 einsetzen."""
        full = np.convolve(a, b)
        out = full[:n].copy()
        out[:len(full) - n] -= full[n:]
        return out % q

    print("Werkzeuge bereit: lineare Gleichungssysteme und Rang über 𝔽_p, Multiplikation in ℤ_q[x]/(xⁿ + 1)")


def residue_rings():
    """19. Die Restklassenringe ℤₙ: Einheiten, Nullteiler, Körper (Zellen 6 von rings_fields.ipynb)."""
    global T, ax, axes, fig, idem, m, nil, ns, prime_mask, rad, ring_stats, stats_n
    global u, z, zc, zr
    def ring_stats(n):
        units = sum(1 for a in range(n) if gcd(a, n) == 1)
        zero_div = sum(1 for a in range(1, n) if any(a * b % n == 0 for b in range(1, n)))
        nilpotent = sum(1 for a in range(n) if pow(a, n, n) == 0)
        idempotent = sum(1 for a in range(n) if a * a % n == a)
        return units, zero_div, nilpotent, idempotent

    ns = np.arange(2, 61)
    stats_n = np.array([ring_stats(int(m)) for m in ns])
    fig, axes = plt.subplots(1, 3, figsize=(17, 4.6))
    for ax, m in zip(axes[:2], (12, 13)):
        T = np.outer(np.arange(m), np.arange(m)) % m
        ax.imshow(T, cmap="viridis")
        zr, zc = np.where((T == 0) & (np.arange(m)[:, None] > 0) & (np.arange(m)[None, :] > 0))
        ax.plot(zc, zr, "rx", ms=7, label="a·b = 0 mit a, b ≠ 0")
        ax.set_title(f"Multiplikationstafel von ℤ_{m}" + (" (Körper)" if isprime(m) else ""), fontsize=10)
        ax.set_xlabel("b"); ax.set_ylabel("a")
        ax.legend(fontsize=8, loc="lower right")
    prime_mask = np.array([isprime(int(m)) for m in ns])
    axes[2].plot(ns, stats_n[:, 0], "o-", ms=3, label="Einheiten φ(n)")
    axes[2].plot(ns, stats_n[:, 1], "s-", ms=3, label="Nullteiler ≠ 0")
    axes[2].plot(ns, stats_n[:, 2], "^-", ms=3, label="nilpotente Elemente")
    axes[2].plot(ns[prime_mask], stats_n[prime_mask, 0], "k*", ms=8, label="n prim: alles ≠ 0 ist Einheit")
    axes[2].set_xlabel("n")
    axes[2].set_ylabel("Anzahl")
    axes[2].set_title("Einheiten und Nullteiler in ℤₙ", fontsize=10)
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    rad = lambda m: int(np.prod(list(factorint(m).keys())))
    print("n  Einheiten  Nullteiler≠0  nilpotent  idempotent")
    for m in (12, 13, 30, 32, 60):
        u, z, nil, idem = ring_stats(m)
        print(f"{m:2d} {u:9d} {z:13d} {nil:10d} {idem:11d}   (φ = {int(totient(m))}, n/rad(n) = {m // rad(m)}, 2^ω(n) = {2 ** len(factorint(m))})")
    print(f"Jedes Element ≠ 0 ist Einheit oder Nullteiler: {all(stats_n[:, 0] + stats_n[:, 1] == ns - 1)};  ℤₙ ist Körper genau für n prim: "
          f"{all((stats_n[:, 1] == 0) == prime_mask)}")


def euclid_crt():
    """20. Der euklidische Algorithmus, Bézout und der chinesische Restsatz (Zellen 9 von rings_fields.ipynb)."""
    global a_, axes, b_, big, euclid_steps, extended_euclid, fib, fig, g_, grid, grid2, i
    global inv, j, lnN, m1, m2, mean_steps, rng, s_, sizes, slope, t_, v
    global worst
    rng = np.random.default_rng(2)

    def euclid_steps(a, b):
        k = 0
        while b:
            a, b, k = b, a % b, k + 1
        return k

    def extended_euclid(a, b):
        """Gibt (g, s, t) mit g = ggT(a, b) = s·a + t·b zurück."""
        s0, s1, t0, t1 = 1, 0, 0, 1
        while b:
            qq = a // b
            a, b = b, a - qq * b
            s0, s1, t0, t1 = s1, s0 - qq * s1, t1, t0 - qq * t1
        return a, s0, t0

    sizes = [10 ** k for k in range(2, 13)]
    mean_steps = [np.mean([euclid_steps(int(rng.integers(1, Nn)), int(rng.integers(1, Nn))) for _ in range(4000)]) for Nn in sizes]
    fib = [1, 1]
    while len(fib) < 60:
        fib.append(fib[-1] + fib[-2])
    worst = [(fib[k + 1], euclid_steps(fib[k + 1], fib[k])) for k in range(1, 58)]

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.6))
    axes[0].semilogx(sizes, mean_steps, "o", label="Mittel über zufällige Paare < N")
    lnN = np.log(np.array(sizes, dtype=float))
    slope = 12 * np.log(2) / np.pi ** 2
    axes[0].semilogx(sizes, slope * lnN + (np.mean(mean_steps) - slope * lnN.mean()), "k--", label="Steigung 12 ln 2 / π² = 0.843 pro ln N")
    axes[0].semilogx([w[0] for w in worst], [w[1] for w in worst], "r.", ms=4, label="Fibonacci-Paare (schlechtester Fall)")
    axes[0].set_xlim(50, 3e12)
    axes[0].set_xlabel("Größe N der Zahlen")
    axes[0].set_ylabel("Zahl der Divisionsschritte")
    axes[0].set_title("Euklid braucht nur logarithmisch viele Schritte", fontsize=10)
    axes[0].legend(fontsize=8)
    m1, m2 = 3, 5
    grid = np.full((m1, m2), -1)
    for v in range(m1 * m2):
        grid[v % m1, v % m2] = v
    axes[1].imshow(grid, cmap="viridis")
    for i in range(m1):
        for j in range(m2):
            axes[1].text(j, i, grid[i, j], ha="center", va="center", color="w", fontsize=12)
    axes[1].set_xticks(range(m2)); axes[1].set_yticks(range(m1))
    axes[1].set_xlabel("x mod 5"); axes[1].set_ylabel("x mod 3")
    axes[1].set_title("ℤ₁₅ ≅ ℤ₃ × ℤ₅: jedes Paar genau einmal", fontsize=10)
    m1, m2 = 4, 6
    grid2 = np.full((m1, m2), -1)
    for v in range(24):
        grid2[v % m1, v % m2] = v if grid2[v % m1, v % m2] < 0 else grid2[v % m1, v % m2]
    axes[2].imshow(np.where(grid2 < 0, np.nan, grid2), cmap="viridis")
    for i in range(m1):
        for j in range(m2):
            axes[2].text(j, i, "–" if grid2[i, j] < 0 else grid2[i, j], ha="center", va="center", color="k" if grid2[i, j] < 0 else "w", fontsize=12)
    axes[2].set_xticks(range(m2)); axes[2].set_yticks(range(m1))
    axes[2].set_xlabel("x mod 6"); axes[2].set_ylabel("x mod 4")
    axes[2].set_title("ggT(4, 6) = 2: nur die Hälfte der Paare wird getroffen", fontsize=10)
    plt.tight_layout()
    plt.show()

    a_, b_ = 240, 46
    g_, s_, t_ = extended_euclid(a_, b_)
    print(f"ggT({a_}, {b_}) = {g_} = {s_}·{a_} + {t_}·{b_}  (Bézout)")
    big = 2 ** 127 - 1
    inv = pow(65537, -1, big)
    print(f"Inverses von 65537 modulo 2¹²⁷ − 1: {inv}, Probe 65537·inv mod m = {65537 * inv % big};  Schritte: {euclid_steps(big, 65537)}")
    print(f"Gemessene Steigung der mittleren Schrittzahl: {np.polyfit(lnN, mean_steps, 1)[0]:.3f} pro ln N (Theorie 12 ln 2/π² = {slope:.3f})")
    print(f"Schlechtester Fall: F₅₈ = {fib[57]} und F₅₇ brauchen {euclid_steps(fib[57], fib[56])} Schritte (Lamé: höchstens 5 × Zahl der Dezimalstellen = {5 * len(str(fib[56]))})")
    print(f"Chinesischer Restsatz: x ≡ 2 (mod 3), x ≡ 3 (mod 5), x ≡ 2 (mod 7) → x = {crt([3, 5, 7], [2, 3, 2])[0]} (mod 105)")


def gaussian_integers():
    """21. Gaußsche Zahlen, eindeutige Zerlegung und Klassenzahlen (Zellen 12 von rings_fields.ipynb)."""
    global DD, Ds, R, axes, class_number, fig, fundamental, g_arr, gp, h1, hs, is_gaussian_prime
    global norms5, primes, two_squares
    def is_gaussian_prime(a, b):
        """a + bi ist Gaußsche Primzahl: Norm prim, oder eine Komponente 0 und die andere prim ≡ 3 mod 4."""
        if a == 0 or b == 0:
            c = abs(a + b)
            return isprime(c) and c % 4 == 3
        return isprime(a * a + b * b)

    R = 40
    gp = [(a, b) for a in range(-R, R + 1) for b in range(-R, R + 1) if is_gaussian_prime(a, b)]

    def class_number(D):
        """Klassenzahl h(−D): Zahl der reduzierten primitiven quadratischen Formen ax² + bxy + cy² mit b² − 4ac = −D."""
        h = 0
        for a in range(1, isqrt(D // 3) + 1):
            for b in range(-a + 1, a + 1):
                if (b * b + D) % (4 * a):
                    continue
                c = (b * b + D) // (4 * a)
                if c < a or (c == a and b < 0) or gcd(gcd(a, abs(b)), c) != 1:
                    continue
                h += 1
        return h

    def fundamental(D):
        if D % 4 == 3:
            return all(D % (p * p) for p in range(2, isqrt(D) + 1))
        if D % 4 == 0:
            m = D // 4
            return m % 4 in (1, 2) and all(m % (p * p) for p in range(2, isqrt(m) + 1))
        return False

    Ds = [D for D in range(3, 2001) if fundamental(D)]
    hs = np.array([class_number(D) for D in Ds])
    fig, axes = plt.subplots(1, 2, figsize=(16, 5.2), gridspec_kw={"width_ratios": [1, 1.5]})
    g_arr = np.array(gp)
    axes[0].plot(g_arr[:, 0], g_arr[:, 1], "s", ms=2.5)
    axes[0].set_aspect("equal")
    axes[0].set_xlabel("Realteil a"); axes[0].set_ylabel("Imaginärteil b")
    axes[0].set_title(f"Gaußsche Primzahlen a + bi mit |a|, |b| ≤ {R}", fontsize=10)
    axes[1].plot(Ds, hs, ".", ms=4, label="h(−D)")
    h1 = [D for D, h in zip(Ds, hs) if h == 1]
    axes[1].plot(h1, [1] * len(h1), "r*", ms=10, label=f"Klassenzahl 1: D = {h1}")
    DD = np.linspace(3, 2000, 200)
    axes[1].plot(DD, np.sqrt(DD) / np.pi, "k--", lw=1, label="√D / π (Größenordnung)")
    axes[1].set_xlabel("D (Diskriminante −D)")
    axes[1].set_ylabel("Klassenzahl")
    axes[1].set_title("Wie stark versagt die eindeutige Zerlegung in ℚ(√−D)?", fontsize=10)
    axes[1].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    primes = list(primerange(3, 1000))
    two_squares = {p: next(((a, isqrt(p - a * a)) for a in range(1, isqrt(p) + 1) if isqrt(p - a * a) ** 2 == p - a * a), None) for p in primes}
    print(f"Fermat: Primzahl p < 1000 ist Summe zweier Quadrate genau dann, wenn p ≡ 1 mod 4: {all((two_squares[p] is not None) == (p % 4 == 1) for p in primes)};  "
          f"z. B. 13 = {two_squares[13][0]}² + {two_squares[13][1]}², 97 = {two_squares[97][0]}² + {two_squares[97][1]}²")
    norms5 = {a * a + 5 * b * b for a in range(-5, 6) for b in range(-3, 4)}
    print(f"ℤ[√−5]: 6 = 2·3 = (1 + √−5)(1 − √−5); Normen 4·9 = 6·6; Elemente mit Norm 2 oder 3: {'gefunden' if (2 in norms5 or 3 in norms5) else 'keine'} → 2, 3, 1 ± √−5 sind unzerlegbar, die Zerlegung ist nicht eindeutig")
    print(f"Klassenzahlen: h(−4) = {class_number(4)} (ℤ[i]), h(−20) = {class_number(20)} (ℤ[√−5]), h(−163) = {class_number(163)};  Klassenzahl 1 für D ≤ 2000: {h1}")


def irreducible_polys():
    """22. Polynomringe: irreduzible Polynome über endlichen Körpern (Zellen 15 von rings_fields.ipynb)."""
    global axes, brute, c, cases, count_irreducible, degs, fig, gauss_formula, labels, ns_, p, patterns
    def count_irreducible(p, n):
        """Zählt die normierten irreduziblen Polynome vom Grad n über 𝔽_p durch Ausprobieren."""
        cnt = 0
        for coeffs in itertools.product(range(p), repeat=n):
            if Poly([1, *coeffs], x, modulus=p).is_irreducible:
                cnt += 1
        return cnt

    def gauss_formula(p, n):
        return sum(int(mobius(d)) * p ** (n // d) for d in range(1, n + 1) if n % d == 0) // n

    cases = {2: range(1, 11), 3: range(1, 7), 5: range(1, 5)}
    brute = {p: [count_irreducible(p, n) for n in ns_] for p, ns_ in cases.items()}
    patterns = {}
    for p in primerange(3, 400):
        degs = tuple(sorted(Poly(f, x).degree() for f, _ in factor_list(x ** 4 + 1, modulus=p)[1]))
        patterns.setdefault(degs, []).append(p)

    fig, axes = plt.subplots(1, 2, figsize=(16, 4.6))
    for (p, ns_), c in zip(cases.items(), ["tab:blue", "tab:orange", "tab:green"]):
        ns_ = list(ns_)
        axes[0].semilogy(ns_, brute[p], "o", c=c, ms=6, label=f"𝔽_{p}: durchgezählt")
        axes[0].semilogy(ns_, [gauss_formula(p, n) for n in ns_], "-", c=c, lw=1, label=f"𝔽_{p}: Formel (1/n) Σ μ(d) p^(n/d)")
        axes[0].semilogy(ns_, [p ** n / n for n in ns_], ":", c=c, lw=1)
    axes[0].set_xlabel("Grad n")
    axes[0].set_ylabel("Zahl der normierten irreduziblen Polynome")
    axes[0].set_title("Irreduzible Polynome: etwa pⁿ/n (gepunktet)", fontsize=10)
    axes[0].legend(fontsize=7)
    labels = [" + ".join(map(str, k)) for k in patterns]
    axes[1].bar(labels, [len(v) for v in patterns.values()])
    axes[1].set_xlabel("Grade der Faktoren von x⁴ + 1 modulo p")
    axes[1].set_ylabel("Zahl der Primzahlen p < 400")
    axes[1].set_title("x⁴ + 1 ist über ℚ irreduzibel, modulo jeder Primzahl aber zerlegbar", fontsize=10)
    plt.tight_layout()
    plt.show()

    for p, ns_ in cases.items():
        print(f"𝔽_{p}: durchgezählt {brute[p]};  Formel stimmt: {brute[p] == [gauss_formula(p, n) for n in ns_]}")
    print(f"x⁴ + 1 über ℚ irreduzibel: {Poly(x ** 4 + 1, x).is_irreducible};  Zerlegungstypen modulo p < 400: " + ", ".join(f"{k}: {len(v)}" for k, v in patterns.items())
          + f";  irreduzibel modulo einer ungeraden Primzahl: {(4,) in patterns}")
    print(f"Beispiele: x⁴ + 1 ≡ {' · '.join(str(f.as_expr()) for f, _ in factor_list(x ** 4 + 1, modulus=7)[1])} (mod 7), ≡ {' · '.join(str(f.as_expr()) for f, _ in factor_list(x ** 4 + 1, modulus=17)[1])} (mod 17)")


def finite_fields():
    """23. Endliche Körper: 𝔽₁₆ ist nicht ℤ₁₆ (Zellen 18 von rings_fields.ipynb)."""
    global MOD, T16, Z16, _, a, ax, axes, d15, fig, frob, gf16_mul, k
    global name, orders, powers, subfield4, v, zc, zr
    MOD = 0b10011                                                     # x⁴ + x + 1, irreduzibel über 𝔽₂

    def gf16_mul(a, b):
        """Multiplikation in 𝔽₁₆ = 𝔽₂[x]/(x⁴ + x + 1); Elemente als 4-Bit-Zahlen (Bit i = Koeffizient von xⁱ)."""
        r = 0
        while b:
            if b & 1:
                r ^= a
            b >>= 1
            a <<= 1
            if a & 0b10000:
                a ^= MOD
        return r

    T16 = np.array([[gf16_mul(a, b) for b in range(16)] for a in range(16)])
    Z16 = np.outer(np.arange(16), np.arange(16)) % 16
    powers = [1]
    for _ in range(15):
        powers.append(gf16_mul(powers[-1], 0b10))                      # Potenzen von x
    orders = {}
    for a in range(1, 16):
        k, v = 1, a
        while v != 1:
            v, k = gf16_mul(v, a), k + 1
        orders[a] = k
    frob = [gf16_mul(a, a) for a in range(16)]
    subfield4 = [a for a in range(16) if gf16_mul(gf16_mul(a, a), gf16_mul(a, a)) == a]

    def name(a):
        terms = [("x³", 8), ("x²", 4), ("x", 2), ("1", 1)]
        return " + ".join(t for t, bit in terms if a & bit) or "0"

    fig, axes = plt.subplots(1, 3, figsize=(17, 4.8))
    axes[0].imshow(Z16, cmap="viridis")
    zr, zc = np.where((Z16 == 0) & (np.arange(16)[:, None] > 0) & (np.arange(16)[None, :] > 0))
    axes[0].plot(zc, zr, "rx", ms=6, label="Nullteiler")
    axes[0].set_title("ℤ₁₆: Multiplikation modulo 16", fontsize=10)
    axes[0].legend(fontsize=8, loc="lower right")
    axes[1].imshow(T16, cmap="viridis")
    axes[1].set_title("𝔽₁₆: Multiplikation von Polynomen mod x⁴ + x + 1", fontsize=10)
    for ax in axes[:2]:
        ax.set_xlabel("b"); ax.set_ylabel("a")
    d15 = [1, 3, 5, 15]
    axes[2].bar([str(d) for d in d15], [sum(1 for v in orders.values() if v == d) for d in d15], alpha=0.6, label="gemessen")
    axes[2].plot([str(d) for d in d15], [int(totient(d)) for d in d15], "ko", label="φ(d)")
    axes[2].set_xlabel("Ordnung in der multiplikativen Gruppe 𝔽₁₆^×")
    axes[2].set_ylabel("Zahl der Elemente")
    axes[2].set_title("𝔽₁₆^× ist zyklisch mit 15 Elementen", fontsize=10)
    axes[2].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print("Potenzen von x in 𝔽₁₆: " + ", ".join(f"x^{k} = {name(v)}" for k, v in enumerate(powers[:8])) + ", …")
    print(f"x hat Ordnung {orders[2]} (primitives Element); alle 15 Elemente ≠ 0 kommen als Potenz vor: {sorted(powers[:15]) == list(range(1, 16))}")
    print(f"Nullteiler: ℤ₁₆ hat {len(zr)} Paare (a, b ≠ 0) mit a·b = 0, 𝔽₁₆ hat {int(np.sum(T16[1:, 1:] == 0))};  Charakteristik 2: a + a = 0 für alle a")
    print(f"Frobenius a ↦ a² ist bijektiv: {sorted(frob) == list(range(16))};  Teilkörper 𝔽₄ = {{a : a⁴ = a}} = {[name(a) for a in subfield4]}")


def reed_solomon():
    """24. Reed-Solomon-Codes: Fehlerkorrektur mit Polynomen (Zellen 21 von rings_fields.ipynb)."""
    global _, alphas, axes, berlekamp_welch, bottom, c, cw, dec, e, es, fig, k_rs
    global lab, msg, n_rs, p, poly_divmod, pos, r, results, rng, rs_encode, t_rs, vals
    rng = np.random.default_rng(6)
    p, n_rs, k_rs = 929, 30, 20                                       # 𝔽₉₂₉ wie im Barcode PDF417; Codewortlänge 30, Nachricht 20 Symbole
    t_rs = (n_rs - k_rs) // 2
    alphas = np.arange(1, n_rs + 1)

    def rs_encode(msg):
        """Codewort = Werte des Nachrichtenpolynoms m₀ + m₁a + … an n Stellen a."""
        V = np.array([[pow(int(a), j, p) for j in range(k_rs)] for a in alphas])
        return V @ msg % p

    def poly_divmod(num, den):
        """Polynomdivision über 𝔽_p (Koeffizienten aufsteigend)."""
        num = list(num); out = [0] * max(len(num) - len(den) + 1, 1)
        inv_lead = pow(int(den[-1]), -1, p)
        for i in range(len(num) - len(den), -1, -1):
            coef = num[i + len(den) - 1] * inv_lead % p
            out[i] = coef
            for j, dj in enumerate(den):
                num[i + j] = (num[i + j] - coef * dj) % p
        return np.array(out), np.array(num[:len(den) - 1])

    def berlekamp_welch(r):
        """Dekodiert mit Berlekamp-Welch: sucht E (normiert, Grad t) und Q (Grad < k + t) mit Q(aᵢ) = rᵢ·E(aᵢ), dann P = Q/E."""
        A, b = [], []
        for a, ri in zip(alphas, r):
            a = int(a)
            rowQ = [pow(a, j, p) for j in range(k_rs + t_rs)]
            rowE = [(-int(ri) * pow(a, j, p)) % p for j in range(t_rs)]
            A.append(rowQ + rowE)
            b.append(int(ri) * pow(a, t_rs, p) % p)
        z = solve_mod_p(A, b, p)
        if z is None:
            return None
        Q, E = z[:k_rs + t_rs], np.r_[z[k_rs + t_rs:], 1]
        P, rem = poly_divmod(Q, E)
        return P[:k_rs] if not np.any(rem % p) else None

    results = {e: {"richtig": 0, "Fehler erkannt": 0, "falsch dekodiert": 0} for e in range(0, 11)}
    for e, _ in itertools.product(range(0, 11), range(150)):
        msg = rng.integers(0, p, k_rs)
        cw = rs_encode(msg)
        r = cw.copy()
        pos = rng.choice(n_rs, e, replace=False)
        r[pos] = (r[pos] + rng.integers(1, p, e)) % p
        dec = berlekamp_welch(r)
        if dec is None:
            results[e]["Fehler erkannt"] += 1
        elif np.array_equal(dec % p, msg):
            results[e]["richtig"] += 1
        else:
            results[e]["falsch dekodiert"] += 1

    msg = rng.integers(0, p, k_rs); cw = rs_encode(msg); r = cw.copy()
    pos = rng.choice(n_rs, t_rs, replace=False); r[pos] = (r[pos] + rng.integers(1, p, t_rs)) % p
    fig, axes = plt.subplots(1, 2, figsize=(16, 4.6))
    es = list(results)
    bottom = np.zeros(len(es))
    for lab, c in [("richtig", "tab:green"), ("Fehler erkannt", "tab:orange"), ("falsch dekodiert", "tab:red")]:
        vals = np.array([results[e][lab] / 150 for e in es])
        axes[0].bar(es, vals, bottom=bottom, color=c, label=lab)
        bottom += vals
    axes[0].axvline(t_rs + 0.5, color="k", ls="--", label=f"Grenze t = (n − k)/2 = {t_rs}")
    axes[0].set_xlabel("Zahl der verfälschten Symbole")
    axes[0].set_ylabel("Anteil von 150 Versuchen")
    axes[0].set_title(f"Reed-Solomon über 𝔽_{p}: n = {n_rs}, k = {k_rs}", fontsize=10)
    axes[0].legend(fontsize=8)
    axes[1].plot(alphas, cw, "o-", ms=4, label="gesendetes Codewort")
    axes[1].plot(alphas[pos], r[pos], "rx", ms=10, label=f"{t_rs} verfälschte Symbole")
    axes[1].plot(alphas, rs_encode(berlekamp_welch(r)), "k.", ms=5, label="nach der Dekodierung")
    axes[1].set_xlabel("Stelle a (Auswertungspunkt)")
    axes[1].set_ylabel("Symbolwert (0 … 928)")
    axes[1].set_title("Ein Codewort mit 5 Fehlern wird vollständig repariert", fontsize=10)
    axes[1].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"Parameter: n = {n_rs}, k = {k_rs}, Mindestabstand n − k + 1 = {n_rs - k_rs + 1} (Singleton-Schranke erreicht), korrigiert t = {t_rs} Fehler")
    for e in (0, 3, 5, 6, 8, 10):
        print(f"{e:2d} Fehler: " + ", ".join(f"{lab} {v}" for lab, v in results[e].items()))


def groebner_bases():
    """25. Gröbner-Basen: Polynomgleichungen systematisch lösen (Zellen 24 von rings_fields.ipynb)."""
    global G1, G2, arms, axes, c, c1, c2, c2_val, eqs, fig, g, j1
    global j2, l1, l2, lab, s1, s2, s2v, sols1, th1, th2, tt, tx
    global ty, xs_, ys
    G1 = groebner([x ** 2 + y ** 2 - 4, x * y - 1], x, y, order="lex")
    ys = [float(rt) for rt in real_roots(Poly(G1.exprs[-1], y))]
    sols1 = [(1 / yy, yy) for yy in ys]                                # aus xy = 1 folgt x = 1/y

    c1, s1, c2, s2 = symbols("c1 s1 c2 s2")
    l1, l2, tx, ty = 2, Rational(3, 2), Rational(11, 5), Rational(7, 5)
    eqs = [c1 ** 2 + s1 ** 2 - 1, c2 ** 2 + s2 ** 2 - 1,
           l1 * c1 + l2 * (c1 * c2 - s1 * s2) - tx, l1 * s1 + l2 * (s1 * c2 + c1 * s2) - ty]
    G2 = groebner(eqs, c1, s1, s2, c2, order="lex")
    c2_val = float(solve(G2.exprs[-1], c2)[0])                          # letztes Basispolynom ist linear in c2
    arms = []
    for s2v in (np.sqrt(1 - c2_val ** 2), -np.sqrt(1 - c2_val ** 2)):
        th2 = np.arctan2(s2v, c2_val)
        th1 = np.arctan2(float(ty), float(tx)) - np.arctan2(float(l2) * s2v, float(l1) + float(l2) * c2_val)
        arms.append((th1, th2))

    fig, axes = plt.subplots(1, 2, figsize=(15, 5.2))
    tt = np.linspace(0, 2 * np.pi, 400)
    axes[0].plot(2 * np.cos(tt), 2 * np.sin(tt), label="x² + y² = 4")
    xs_ = np.linspace(0.2, 2.5, 200)
    axes[0].plot(xs_, 1 / xs_, "tab:orange", label="xy = 1"); axes[0].plot(-xs_, -1 / xs_, "tab:orange")
    axes[0].plot([s[0] for s in sols1], [s[1] for s in sols1], "ko", ms=8, label="Lösungen aus der Gröbner-Basis")
    axes[0].set_aspect("equal"); axes[0].set_xlim(-2.6, 2.6); axes[0].set_ylim(-2.6, 2.6)
    axes[0].set_title("Kreis und Hyperbel: vier Schnittpunkte", fontsize=10)
    axes[0].legend(fontsize=8)
    for (th1, th2), c, lab in zip(arms, ["tab:blue", "tab:red"], ["Ellbogen unten (θ₂ > 0)", "Ellbogen oben (θ₂ < 0)"]):
        j1 = np.array([float(l1) * np.cos(th1), float(l1) * np.sin(th1)])
        j2 = j1 + float(l2) * np.array([np.cos(th1 + th2), np.sin(th1 + th2)])
        axes[1].plot([0, j1[0], j2[0]], [0, j1[1], j2[1]], "o-", c=c, lw=3, ms=8, label=lab)
    axes[1].plot(float(tx), float(ty), "k*", ms=16, label="Ziel (2.2, 1.4)")
    axes[1].set_aspect("equal"); axes[1].set_xlim(-0.5, 3.2); axes[1].set_ylim(-0.8, 2.6)
    axes[1].set_title("Inverse Kinematik eines Roboterarms: zwei Lösungen", fontsize=10)
    axes[1].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print("Gröbner-Basis (lex, x > y) für {x² + y² − 4, xy − 1}:", [str(g) for g in G1.exprs])
    print(f"Letztes Polynom hängt nur von y ab; seine Nullstellen y = {[round(v, 4) for v in ys]};  Probe x² + y² = {[round(s[0] ** 2 + s[1] ** 2, 10) for s in sols1]}")
    print("Gröbner-Basis des Roboterarms (lex, c1 > s1 > s2 > c2):")
    for g in G2.exprs:
        print("   ", g)
    print(f"Daraus c2 = {c2_val:.4f}, s2 = ±{np.sqrt(1 - c2_val ** 2):.4f};  Winkel (θ₁, θ₂) in Grad: " + ", ".join(f"({np.degrees(a):.1f}, {np.degrees(b):.1f})" for a, b in arms))


def field_extensions():
    """26. Körpererweiterungen und Konstruktionen mit Zirkel und Lineal (Zellen 27 von rings_fields.ipynb)."""
    global ang, axes, check_deg, constructible, d_, deg, dx, examples, fig, gauss17, k, m
    global minpolys, mp, ngon, s17
    ngon = np.arange(3, 61)
    deg = np.array([int(totient(int(m))) // 2 for m in ngon])          # Grad von cos(2π/n) über ℚ
    constructible = np.array([d & (d - 1) == 0 for d in deg])
    check_deg = {m: Poly(minimal_polynomial(cos(2 * pi / m), x), x).degree() for m in (5, 7, 9, 17)}
    examples = {"√2 + √3": sqrt(2) + sqrt(3), "∛2 (Würfelverdopplung)": 2 ** Rational(1, 3), "cos 20° (Dreiteilung von 60°)": cos(pi / 9),
                "cos(2π/7) (Siebeneck)": cos(2 * pi / 7), "cos(2π/17) (Siebzehneck)": cos(2 * pi / 17)}
    minpolys = {k: minimal_polynomial(v, x) for k, v in examples.items()}
    s17 = np.sqrt(17)
    gauss17 = (-1 + s17 + np.sqrt(34 - 2 * s17) + 2 * np.sqrt(17 + 3 * s17 - np.sqrt(34 - 2 * s17) - 2 * np.sqrt(34 + 2 * s17))) / 16

    fig, axes = plt.subplots(1, 2, figsize=(16, 4.8), gridspec_kw={"width_ratios": [2, 1]})
    axes[0].bar(ngon, deg, color=np.where(constructible, "tab:green", "tab:red"))
    axes[0].set_yscale("log", base=2)
    axes[0].set_xlabel("Eckenzahl n des regelmäßigen Vielecks")
    axes[0].set_ylabel("Grad [ℚ(cos 2π/n) : ℚ] = φ(n)/2")
    axes[0].set_title("Grün: Grad ist Zweierpotenz → mit Zirkel und Lineal konstruierbar", fontsize=10)
    for m, dx in ((7, -10), (9, 10), (17, 0)):
        axes[0].annotate(f"n = {m}", (m, deg[m - 3]), textcoords="offset points", xytext=(dx, 6), ha="center", fontsize=8)
    ang = 2 * np.pi * np.arange(18) / 17
    axes[1].plot(np.cos(ang), np.sin(ang), "o-", c="tab:green", ms=4)
    axes[1].plot([0, gauss17], [0, 0], "k--", lw=1)
    axes[1].plot(gauss17, 0, "k|", ms=20)
    axes[1].set_aspect("equal")
    axes[1].set_title("Gauß 1796: das Siebzehneck", fontsize=10)
    axes[1].set_xticks([]); axes[1].set_yticks([])
    plt.tight_layout()
    plt.show()

    print("Konstruierbare Vielecke bis 60:", list(ngon[constructible]))
    print("Gradformel φ(n)/2 gegen Minimalpolynom von cos(2π/n):", {m: (int(totient(m)) // 2, d) for m, d in check_deg.items()})
    for k, mp in minpolys.items():
        d_ = Poly(mp, x).degree()
        print(f"{k:32s}: Minimalpolynom {mp}, Grad {d_} → {'konstruierbar' if d_ & (d_ - 1) == 0 else 'nicht konstruierbar'}")
    print(f"Gauß' Formel für cos(2π/17) mit verschachtelten Quadratwurzeln: {gauss17:.15f}, direkt {np.cos(2 * np.pi / 17):.15f}")


def galois():
    """27. Galois-Gruppen und die Zerlegung modulo Primzahlen (Zellen 30 von rings_fields.ipynb)."""
    global G, P, _, ax, axes, ct, cycle_type, data9, deg_, dev, disc, elements
    global f, fig, freq, g, keys, lab, name_, nm, order_, p, polys9, primes9
    global seen_types, total, types
    polys9 = {"x³ − 2": x ** 3 - 2, "x⁴ − 10x² + 1": x ** 4 - 10 * x ** 2 + 1, "x⁴ + 1": x ** 4 + 1, "x⁵ − x − 1": x ** 5 - x - 1, "x⁵ − 2": x ** 5 - 2}
    primes9 = list(primerange(3, 6000))

    def cycle_type(perm, n):
        seen, out = set(), []
        for i in range(n):
            if i not in seen:
                L, j = 0, i
                while j not in seen:
                    seen.add(j); j = perm(j); L += 1
                out.append(L)
        return tuple(sorted(out))

    data9 = {}
    for name_, f in polys9.items():
        P = Poly(f, x)
        G, _ = galois_group(P)
        deg_ = P.degree()
        elements = list(G.generate())
        types = {}
        for g in elements:
            ct = cycle_type(lambda i: g.array_form[i] if i < len(g.array_form) else i, deg_)
            types[ct] = types.get(ct, 0) + 1
        disc = int(P.discriminant())
        seen_types = {}
        for p in primes9:
            if disc % p == 0:
                continue
            ct = tuple(sorted(Poly(g_, x).degree() for g_, e_ in factor_list(f, modulus=p)[1] for _ in range(e_)))
            seen_types[ct] = seen_types.get(ct, 0) + 1
        total = sum(seen_types.values())
        data9[name_] = (G, len(elements), types, {k: v / total for k, v in seen_types.items()})

    fig, axes = plt.subplots(1, 2, figsize=(17, 4.6), gridspec_kw={"width_ratios": [1, 2]})
    for ax, nm in zip(axes, ["x³ − 2", "x⁵ − x − 1"]):
        G, order_, types, freq = data9[nm]
        keys = sorted(types, key=lambda k: (len(k), k))
        lab = [" ".join(map(str, k)) for k in keys]
        ax.bar(np.arange(len(keys)) - 0.2, [types[k] / order_ for k in keys], 0.4, label="Anteil in der Galois-Gruppe")
        ax.bar(np.arange(len(keys)) + 0.2, [freq.get(k, 0) for k in keys], 0.4, label=f"Anteil der Primzahlen < 6000")
        ax.set_xticks(range(len(keys)), lab)
        ax.set_xlabel("Grade der Faktoren mod p = Zyklentyp")
        ax.set_ylabel("Anteil")
        ax.set_title(f"{nm}: Galois-Gruppe der Ordnung {order_}", fontsize=10)
        ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    for nm, (G, order_, types, freq) in data9.items():
        dev = max(abs(types.get(k, 0) / order_ - freq.get(k, 0)) for k in set(types) | set(freq))
        print(f"{nm:14s}: Galois-Gruppe Ordnung {order_:3d}, auflösbar {G.is_solvable};  Zyklentypen {dict(sorted(types.items()))};  größte Abweichung der Primzahl-Anteile {dev:.3f}")
    print(f"x⁵ − x − 1: Anteil der Primzahlen, modulo derer das Polynom irreduzibel bleibt: {data9['x⁵ − x − 1'][3].get((5,), 0):.3f} (Theorie 24/120 = 0.200)")


def padic():
    """28. p-adische Zahlen und das Henselsche Lemma (Zellen 33 von rings_fields.ipynb)."""
    global K, _, axes, digits7, fig, i5, it, mod, newton, p7, partial, r_
    global root, vp, xk
    def vp(n, p):
        """p-adische Bewertung: wie oft p die ganze Zahl n ≠ 0 teilt."""
        if n == 0:
            return np.inf
        k = 0
        while n % p == 0:
            n //= p; k += 1
        return k

    p7, K = 7, 40
    xk, mod, newton = 3, 7, []                                         # 3² = 9 ≡ 2 mod 7
    for it in range(6):
        newton.append((it, mod, vp(xk * xk - 2, p7)))
        mod = mod * mod
        xk = (xk - (xk * xk - 2) * pow(2 * xk, -1, mod)) % mod         # Newton-Schritt modulo p^(2^k)
    root = xk % 7 ** K
    digits7 = []
    r_ = root
    for _ in range(K):
        digits7.append(r_ % 7); r_ //= 7
    partial = [sum(2 ** j for j in range(m)) for m in range(1, 41)]

    fig, axes = plt.subplots(1, 2, figsize=(16, 4.6))
    axes[0].semilogy([n_[0] for n_ in newton], [7.0 ** -n_[2] for n_ in newton], "o-", label="|x_k² − 2|₇ = 7^(−v₇)")
    axes[0].set_xlabel("Newton-Schritt k")
    axes[0].set_ylabel("7-adischer Betrag des Fehlers")
    axes[0].set_title("Hensel-Lifting: die Genauigkeit verdoppelt sich", fontsize=10)
    axes[0].legend(fontsize=8)
    axes[1].semilogy(range(1, 41), [2.0 ** -vp(s + 1, 2) for s in partial], "o", ms=4, label="|1 + 2 + … + 2^(m−1) − (−1)|₂")
    axes[1].semilogy(range(1, 41), [float(s + 1) for s in partial], "s", ms=3, c="grey", label="gewöhnlicher Abstand zu −1")
    axes[1].set_xlabel("Zahl der Summanden m")
    axes[1].set_ylabel("Abstand")
    axes[1].set_title("1 + 2 + 4 + 8 + … = −1 in ℚ₂", fontsize=10)
    axes[1].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print("Hensel für x² = 2 in ℤ₇: (Schritt, Modul, v₇(x² − 2)) =", [(a, f"7^{vp(m, 7)}", v) for a, m, v in newton])
    print(f"√2 in ℤ₇, letzte Stellen zuerst: …{''.join(map(str, digits7[::-1][-20:]))} (Basis 7);  Probe: (√2)² − 2 durch 7^{K} teilbar: {(root * root - 2) % 7 ** K == 0}")
    i5 = sqrt_mod(-1, 5 ** 20, all_roots=True)
    print(f"√−1 existiert in ℤ₅ (2² ≡ −1 mod 5): Lösungen modulo 5²⁰: {sorted(i5)[:2]};  in ℤ₃ nicht: {sqrt_mod(-1, 3) is None}")


def reciprocity():
    """29. Quadratische Reste, Reziprozität und Gauß-Summen (Zellen 36 von rings_fields.ipynb)."""
    global axes, fig, g2, g3, gauss_sum, leg, mask1, odd_primes, p101, pow_mod_array, ps, recip
    odd_primes = list(primerange(3, 400))
    recip = all(legendre_symbol(p, q) * legendre_symbol(q, p) == (-1) ** (((p - 1) // 2) * ((q - 1) // 2))
                for p, q in itertools.combinations(odd_primes, 2))
    ps = np.array(list(primerange(5, 3000)))

    def gauss_sum(p, k):
        xs_ = np.arange(p, dtype=np.int64)
        return np.abs(np.exp(2j * np.pi * (pow_mod_array(xs_, k, p)) / p).sum())

    def pow_mod_array(a, k, p):
        out = np.ones_like(a)
        for _ in range(k):
            out = out * a % p
        return out

    g2 = np.array([gauss_sum(int(p), 2) for p in ps]) / np.sqrt(ps)
    g3 = np.array([gauss_sum(int(p), 3) for p in ps]) / np.sqrt(ps)
    p101 = 101
    leg = [legendre_symbol(a, p101) for a in range(1, p101)]

    fig, axes = plt.subplots(1, 2, figsize=(16, 4.6))
    axes[0].bar(range(1, p101), leg, color=["tab:blue" if v > 0 else "tab:red" for v in leg], width=1.0)
    axes[0].set_xlabel("a")
    axes[0].set_ylabel("Legendre-Symbol (a/101)")
    axes[0].set_title("Quadratische Reste modulo 101: genau die Hälfte", fontsize=10)
    axes[1].plot(ps, g2, ".", ms=3, label="|Σ e^(2πi x²/p)| / √p")
    mask1 = ps % 3 == 1
    axes[1].plot(ps[mask1], g3[mask1], ".", ms=3, label="|Σ e^(2πi x³/p)| / √p, p ≡ 1 mod 3")
    axes[1].plot(ps[~mask1], g3[~mask1], ".", ms=3, label="dasselbe, p ≡ 2 mod 3")
    axes[1].axhline(2, color="k", ls="--", lw=1, label="Weil-Schranke 2")
    axes[1].set_xlabel("Primzahl p")
    axes[1].set_ylabel("Betrag / √p")
    axes[1].set_title("Gauß-Summen: quadratisch genau √p, kubisch höchstens 2√p", fontsize=10)
    axes[1].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"Quadratisches Reziprozitätsgesetz für alle {len(odd_primes) * (len(odd_primes) - 1) // 2} Paare ungerader Primzahlen < 400: {recip}")
    print(f"Quadratische Reste mod 101: {sum(1 for v in leg if v > 0)} von 100;  (−1/101) = {legendre_symbol(-1 % 101, 101)} (101 ≡ 1 mod 4), (2/101) = {legendre_symbol(2, 101)} (101 ≡ 5 mod 8)")
    print(f"Quadratische Gauß-Summe / √p: min {g2.min():.6f}, max {g2.max():.6f};  kubisch: p ≡ 2 mod 3 max {g3[~mask1].max():.1e}, p ≡ 1 mod 3 max {g3[mask1].max():.4f} (≤ 2)")


def quaternions():
    """30. Nichtkommutative Ringe: Matrizen und Quaternionen (Zellen 39 von rings_fields.ipynb)."""
    global MT, axes, c, cnt, commuting, fig, frac_invertible, i_, idem, idx, j_, k_
    global mats, n_, nilp, norm, q, qa, qb, qmul, rng, sampled, units, zero_div
    mats = [np.array(m).reshape(2, 2) for m in itertools.product([0, 1], repeat=4)]   # alle 16 Matrizen über 𝔽₂
    idx = {m.tobytes(): i for i, m in enumerate(mats)}
    MT = np.array([[idx[(A @ B % 2).tobytes()] for B in mats] for A in mats])
    units = [i for i, A in enumerate(mats) if round(np.linalg.det(A)) % 2 == 1]
    zero_div = [i for i, A in enumerate(mats) if i not in units and A.any()]
    nilp = [i for i, A in enumerate(mats) if not (A @ A % 2).any()]
    idem = [i for i, A in enumerate(mats) if np.array_equal(A @ A % 2, A)]
    commuting = sum(1 for i in range(16) for j in range(16) if MT[i, j] == MT[j, i])

    def frac_invertible(q, n):
        return np.prod([1 - q ** (-k) for k in range(1, n + 1)])

    rng = np.random.default_rng(12)
    sampled = {}
    for q in (2, 3):
        sampled[q] = []
        for n_ in range(1, 9):
            cnt = sum(rank_mod_p(rng.integers(0, q, (n_, n_)), q) == n_ for _ in range(4000))
            sampled[q].append(cnt / 4000)

    def qmul(a, b):
        """Quaternionenprodukt (w, x, y, z)."""
        w1, x1, y1, z1 = a; w2, x2, y2, z2 = b
        return np.array([w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2, w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
                         w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2, w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2])

    fig, axes = plt.subplots(1, 2, figsize=(16, 4.8))
    axes[0].imshow(MT, cmap="viridis")
    axes[0].set_title(f"M₂(𝔽₂): Multiplikationstafel der 16 Matrizen ({commuting} von 256 Paaren vertauschen)", fontsize=10)
    axes[0].set_xlabel("B"); axes[0].set_ylabel("A")
    for q, c in [(2, "tab:blue"), (3, "tab:orange")]:
        axes[1].plot(range(1, 9), sampled[q], "o", c=c, label=f"𝔽_{q}: Stichprobe")
        axes[1].plot(range(1, 9), [frac_invertible(q, n_) for n_ in range(1, 9)], "-", c=c, label=f"𝔽_{q}: Π (1 − q^(−k))")
    axes[1].axhline(frac_invertible(2, 60), color="tab:blue", ls=":", lw=1)
    axes[1].set_xlabel("Matrixgröße n")
    axes[1].set_ylabel("Anteil invertierbarer Matrizen")
    axes[1].set_title("Einheiten in Mₙ(𝔽_q): |GL(n, q)| / q^(n²)", fontsize=10)
    axes[1].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"M₂(𝔽₂): {len(units)} Einheiten (= |GL(2,2)| = 6 ≅ S₃), {len(zero_div)} Nullteiler ≠ 0, {len(nilp)} nilpotente (A² = 0), {len(idem)} idempotente (A² = A)")
    i_, j_, k_ = np.array([0, 1, 0, 0]), np.array([0, 0, 1, 0]), np.array([0, 0, 0, 1])
    print(f"Quaternionen: ij = {qmul(i_, j_)}, ji = {qmul(j_, i_)} (nicht kommutativ), i² = j² = k² = ijk = {qmul(qmul(i_, j_), k_)[0]:.0f}")
    qa = np.array([1.0, 2.0, -1.0, 0.5]); qb = np.array([0.3, -1.0, 2.0, 1.0])
    norm = lambda q_: np.sqrt(q_ @ q_)
    print(f"Norm ist multiplikativ: |ab| = {norm(qmul(qa, qb)):.6f} = |a|·|b| = {norm(qa) * norm(qb):.6f} → jedes q ≠ 0 hat das Inverse q*/|q|² (Schiefkörper)")
    print(f"Anteil invertierbarer n×n-Matrizen über 𝔽₂ für n → ∞: {frac_invertible(2, 60):.4f}")


def smith_form():
    """31. Moduln über ℤ: Smith-Normalform und Homologie (Zellen 42 von rings_fields.ipynb)."""
    global A13, H, S13, axes, boundary, c, fig, h, homology, i, k_, names_
    global nm, surfaces, w_
    A13 = Matrix([[2, 4, 4], [-6, 6, 12], [10, 4, 16]])
    S13 = smith_normal_form(A13, domain=ZZ)

    def boundary(simplices_k, simplices_km1):
        """Randmatrix ∂: Kanten bzw. Dreiecke → Seiten, mit Vorzeichen (−1)^i für die weggelassene i-te Ecke."""
        index = {s: i for i, s in enumerate(simplices_km1)}
        D = np.zeros((len(simplices_km1), len(simplices_k)), dtype=int)
        for j, s in enumerate(simplices_k):
            for i in range(len(s)):
                D[index[s[:i] + s[i + 1:]], j] = (-1) ** i
        return D

    def homology(triangles):
        tri = sorted(tuple(sorted(t)) for t in triangles)
        edges = sorted({e for t in tri for e in itertools.combinations(t, 2)})
        verts = sorted({(v,) for t in tri for v in t})
        d1, d2 = boundary(edges, verts), boundary(tri, edges)
        snf1 = [abs(int(v)) for v in smith_normal_form(Matrix(d1), domain=ZZ).diagonal() if v != 0]
        snf2 = [abs(int(v)) for v in smith_normal_form(Matrix(d2), domain=ZZ).diagonal() if v != 0]
        r1, r2 = len(snf1), len(snf2)
        betti = (len(verts) - r1, len(edges) - r1 - r2, len(tri) - r2)
        torsion1 = [d for d in snf2 if d > 1]
        return dict(V=len(verts), E=len(edges), F=len(tri), betti=betti, torsion=torsion1, euler=len(verts) - len(edges) + len(tri), d2=d2)

    surfaces = {
        "Kugel (Tetraederrand)": [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)],
        "Torus (7 Ecken)": [(i, (i + 1) % 7, (i + 3) % 7) for i in range(7)] + [(i, (i + 2) % 7, (i + 3) % 7) for i in range(7)],
        "projektive Ebene (6 Ecken)": [(1, 2, 3), (1, 3, 4), (1, 4, 5), (1, 5, 6), (1, 6, 2), (2, 3, 5), (3, 4, 6), (4, 5, 2), (5, 6, 3), (6, 2, 4)],
    }
    H = {nm: homology(tr) for nm, tr in surfaces.items()}

    fig, axes = plt.subplots(1, 2, figsize=(16, 4.8), gridspec_kw={"width_ratios": [1.2, 1]})
    axes[0].imshow(H["projektive Ebene (6 Ecken)"]["d2"], cmap="RdBu", vmin=-1, vmax=1)
    axes[0].set_xlabel("Dreieck"); axes[0].set_ylabel("Kante")
    axes[0].set_title("Randmatrix ∂₂ der projektiven Ebene (rot −1, blau +1)", fontsize=10)
    names_ = list(H)
    w_ = 0.25
    for k_, c in zip(range(3), ["tab:blue", "tab:orange", "tab:green"]):
        axes[1].bar(np.arange(3) + (k_ - 1) * w_, [H[nm]["betti"][k_] for nm in names_], w_, color=c, label=f"Betti-Zahl b_{k_}")
    for i, nm in enumerate(names_):
        if H[nm]["torsion"]:
            axes[1].annotate(f"Torsion ℤ_{H[nm]['torsion'][0]} in H₁", (i, 0.1), ha="center", fontsize=9, color="tab:red")
    axes[1].set_xticks(range(3), [n.split(" (")[0] for n in names_])
    axes[1].set_ylabel("Rang")
    axes[1].set_title("Homologie aus der Smith-Normalform", fontsize=10)
    axes[1].legend(fontsize=8)
    plt.tight_layout()
    plt.show()

    print(f"Relationenmatrix A = {A13.tolist()}: Smith-Normalform diag{tuple(int(v) for v in S13.diagonal())} → ℤ³/Zeilen(A) ≅ ℤ₂ × ℤ₂ × ℤ₁₅₆, Ordnung {int(np.prod([int(v) for v in S13.diagonal()]))} = |det A| = {abs(A13.det())}")
    for nm, h in H.items():
        print(f"{nm:28s}: E − K + F = {h['V']} − {h['E']} + {h['F']} = {h['euler']};  Betti (b₀, b₁, b₂) = {h['betti']};  Torsion in H₁: {h['torsion'] or 'keine'}")


def post_quantum():
    """32. Polynomringe in der Post-Quanten-Kryptographie (Zellen 45 von rings_fields.ipynb)."""
    global A_, B_, Vinv, Vm, axes, cbd, centered, err2, etas, fig, intt, inv_n
    global inv_psi, noise2, nq, ntt, prod_ntt, psi, q, q_ntt, rates, rlwe_trial, rng, sgn
    global tw, w_
    rng = np.random.default_rng(14)
    nq, q = 256, 3329                                                  # Parameter von ML-KEM (Kyber)

    def cbd(eta, size):
        """Zentrierte Binomialverteilung: Summe von eta Münzwürfen minus Summe von eta Münzwürfen."""
        return rng.binomial(eta, 0.5, size) - rng.binomial(eta, 0.5, size)

    def centered(v):
        return ((v + q // 2) % q) - q // 2

    def rlwe_trial(eta, n_msgs=20):
        """Schlüssel erzeugen, n_msgs Nachrichten zu je 256 Bit verschlüsseln und entschlüsseln; gibt Bitfehler und Rauschen zurück."""
        a = rng.integers(0, q, nq)
        s, e = cbd(eta, nq), cbd(eta, nq)
        b = (polymul_mod(a, s, q, nq) + e) % q                        # öffentlicher Schlüssel (a, b = a·s + e)
        errors, noise = 0, []
        for _ in range(n_msgs):
            m = rng.integers(0, 2, nq)
            r, e1, e2 = cbd(eta, nq), cbd(eta, nq), cbd(eta, nq)
            u = (polymul_mod(a, r, q, nq) + e1) % q
            v = (polymul_mod(b, r, q, nq) + e2 + (q + 1) // 2 * m) % q
            d = centered(v - polymul_mod(u, s, q, nq))                # = Rauschen + ⌈q/2⌋·m
            m_dec = (np.abs(d) > q // 4).astype(int)
            errors += int(np.sum(m_dec != m))
            noise.extend(centered(d - (q + 1) // 2 * m).tolist())
        return errors / (n_msgs * nq), np.array(noise)

    err2, noise2 = rlwe_trial(2)
    etas = [2, 8, 16, 24, 32, 40, 48, 56, 64]
    rates = [rlwe_trial(e, 10)[0] for e in etas]
    psi, q_ntt = 7, 7681                                               # NTT-Prüfung mit q = 7681 (hat 512-te Einheitswurzeln)
    psi = next(g for g in range(2, q_ntt) if pow(g, 256, q_ntt) == q_ntt - 1)
    A_ = rng.integers(0, q_ntt, nq); B_ = rng.integers(0, q_ntt, nq)
    w_ = pow(psi, 2, q_ntt)
    Vm = np.array([[pow(w_, i * j, q_ntt) for j in range(nq)] for i in range(nq)], dtype=object)
    tw = np.array([pow(psi, j, q_ntt) for j in range(nq)], dtype=object)
    ntt = lambda a: Vm.dot(a * tw % q_ntt) % q_ntt
    inv_n, inv_psi = pow(nq, -1, q_ntt), pow(psi, -1, q_ntt)
    Vinv = np.array([[pow(w_, -i * j % (2 * nq), q_ntt) for j in range(nq)] for i in range(nq)], dtype=object)
    intt = lambda A: (Vinv.dot(A) % q_ntt * inv_n % q_ntt) * np.array([pow(inv_psi, j, q_ntt) for j in range(nq)], dtype=object) % q_ntt
    prod_ntt = intt(ntt(A_.astype(object)) * ntt(B_.astype(object)) % q_ntt).astype(np.int64)

    fig, axes = plt.subplots(1, 2, figsize=(16, 4.6))
    axes[0].hist(noise2, bins=np.arange(-120, 121, 4), density=True, alpha=0.7, label="Rauschen nach dem Entschlüsseln (η = 2)")
    for sgn in (-1, 1):
        axes[0].axvline(sgn * q / 4, color="k", ls="--", lw=1)
    axes[0].set_xlim(-q / 2, q / 2)
    axes[0].set_xlabel("Rauschwert (zentriert modulo q = 3329)")
    axes[0].set_ylabel("Dichte")
    axes[0].set_title("Das Rauschen bleibt weit innerhalb ±q/4 (gestrichelt)", fontsize=10)
    axes[0].legend(fontsize=8)
    axes[1].plot(etas, rates, "o-")
    axes[1].set_xlabel("Rauschparameter η")
    axes[1].set_ylabel("Anteil falsch entschlüsselter Bits")
    axes[1].set_title("Zu viel Rauschen zerstört die Entschlüsselung", fontsize=10)
    plt.tight_layout()
    plt.show()

    print(f"Ring ℤ_{q}[x]/(x^{nq} + 1): 256-Bit-Nachrichten mit η = 2: Bitfehlerrate {err2:.4f};  Rauschen: Standardabweichung {noise2.std():.1f}, größter Betrag {np.abs(noise2).max()} (Grenze q/4 = {q / 4:.0f})")
    print("Bitfehlerrate gegen η: " + ", ".join(f"η = {e}: {r_:.4f}" for e, r_ in zip(etas, rates)))
    print(f"Negazyklische NTT mit q = {q_ntt}, ψ = {psi} (ψ²⁵⁶ ≡ −1): Produkt über NTT = Produkt direkt: {np.array_equal(prod_ntt, polymul_mod(A_, B_, q_ntt, nq))}")
