"""Was ein klassischer Rechner schafft, für heisenbergweyl.ipynb: Grad 2 kostet polynomiell, ab Grad 3 bzw. 4 exponentiell.

Teil 1, Qubits: Clifford+T im Heisenberg-Bild. Die Messgröße O = Z_0 wird rückwärts durch die Schaltung geschoben,
O → G† O G. Ein Clifford-Gatter (H, S, CNOT, Grad 2) macht aus einem Pauli-String wieder genau einen; ein T-Gatter
(e^(−iπZ/8), Grad 3 im Sinn der Clifford-Hierarchie) macht aus X oder Y zwei Strings: T†XT = (X − Y)/√2, T†YT = (X + Y)/√2.
Pauli-Strings als Bitmasken (x, z) für bis zu 64 Qubits; ⟨0…0|O|0…0⟩ ist die Summe der Koeffizienten der Strings ohne X
und Y. Geprüft gegen einen Zustandsvektor.
Teil 2, Fermionen: dieselbe Dynamik (Kette mit Hüpfen J = 1, Start mit Teilchen auf den geraden Plätzen) frei, also
quadratisch, über die L×L-Korrelationsmatrix, und mit Hubbard-Wechselwirkung U n↑n↓ (Grad 4) exakt im Block mit L/2
Teilchen je Spin (Dimension C(L, L/2)²). Bei U = 0 müssen beide übereinstimmen.
"""
import time
from itertools import combinations
from math import comb

import numpy as np
import matplotlib.pyplot as plt
from scipy import sparse
from scipy.sparse.linalg import expm_multiply


# ---- Teil 1: Clifford+T als Pauli-Pfade

def random_circuit(n, layers, t_count, seed=0, window=0.75):
    """Ziegelmauer aus zufälligen H, S und CNOT; t_count T-Gatter an zufälligen Stellen im ersten Teil `window`.

    Im Heisenberg-Bild läuft die Messgröße von hinten nach vorn; im letzten Viertel ist sie noch lokal und ein T-Gatter
    träfe meist I oder Z. Weiter vorn ist sie über alle Qubits verteilt."""
    rng = np.random.default_rng(seed)
    gates = []
    for layer in range(layers):
        for q in range(n):
            g = rng.choice(["H", "S", "HS", "SH"])
            gates += [(ch, q) for ch in g]
        for q in range(layer % 2, n - 1, 2):
            gates.append(("CX", q, q + 1) if rng.random() < 0.5 else ("CX", q + 1, q))
    for pos, q in zip(sorted(rng.integers(0, int(window * len(gates)), t_count)), rng.integers(0, n, t_count)):
        gates.insert(int(pos), ("T", int(q)))
    return gates


def heisenberg(gates, n, observable_qubit=0):
    """Schiebt Z_q rückwärts durch die Schaltung. Gibt ⟨0|U†ZU|0⟩ und die größte Zahl gleichzeitiger Pauli-Strings."""
    one = np.uint64(1)
    x = np.zeros(1, np.uint64)
    z = np.array([one << np.uint64(observable_qubit)], np.uint64)
    c = np.ones(1)
    peak = 1
    for g in reversed(gates):
        if g[0] == "CX":
            a, b = np.uint64(g[1]), np.uint64(g[2])
            xa, za, xb, zb = (x >> a) & one, (z >> a) & one, (x >> b) & one, (z >> b) & one
            flip = xa & zb & (xb ^ za ^ one)
            c = np.where(flip == one, -c, c)
            x = x ^ (xa << b)
            z = z ^ (zb << a)
            continue
        q = np.uint64(g[1])
        xq, zq = (x >> q) & one, (z >> q) & one
        if g[0] == "H":                                       # X ↔ Z, Y → −Y
            c = np.where(xq & zq == one, -c, c)
            x = (x & ~(one << q)) | (zq << q)
            z = (z & ~(one << q)) | (xq << q)
        elif g[0] == "S":                                     # S†XS = −Y, S†YS = X
            c = np.where(xq & (zq ^ one) == one, -c, c)
            z = z ^ (xq << q)
        elif g[0] == "T":                                     # T†XT = (X − Y)/√2, T†YT = (X + Y)/√2
            br = xq == one
            if br.any():
                s = 1 / np.sqrt(2)
                cx = c[br] * s                                # Anteil X
                cy = np.where(zq[br] == one, c[br], -c[br]) * s   # Anteil Y
                x = np.concatenate([x[~br], x[br], x[br]])
                z = np.concatenate([z[~br], z[br] & ~(one << q), z[br] | (one << q)])
                c = np.concatenate([c[~br], cx, cy])
                key = np.stack([x, z], axis=1)
                key, inv = np.unique(key, axis=0, return_inverse=True)
                c = np.bincount(inv.ravel(), weights=c)
                keep = np.abs(c) > 1e-14
                x, z, c = key[keep, 0], key[keep, 1], c[keep]
                peak = max(peak, len(c))
    return c[x == 0].sum(), peak


def statevector(gates, n, observable_qubit=0):
    """⟨Z_q⟩ nach der Schaltung, mit dem vollen Zustandsvektor (2^n Amplituden) zum Prüfen."""
    psi = np.zeros(2 ** n, complex)
    psi[0] = 1
    psi = psi.reshape([2] * n)                                # Achse n−1−q gehört zu Qubit q
    H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
    one = {"H": H, "S": np.diag([1, 1j]), "T": np.diag([1, np.exp(1j * np.pi / 4)])}
    ax = lambda q: n - 1 - q
    for g in gates:
        if g[0] == "CX":
            a, b = ax(g[1]), ax(g[2])
            idx = [slice(None)] * n
            idx[a] = 1
            sub = psi[tuple(idx)]
            psi[tuple(idx)] = np.flip(sub, axis=b - (b > a))
        else:
            psi = np.moveaxis(np.tensordot(one[g[0]], psi, axes=([1], [ax(g[1])])), 0, ax(g[1]))
    p = np.abs(psi) ** 2
    return p.take(0, axis=ax(observable_qubit)).sum() - p.take(1, axis=ax(observable_qubit)).sum()


# ---- Teil 2: freie Fermionen gegen Hubbard

def free_imbalance(L, times, J=1.0):
    """Imbalance (gerade minus ungerade Plätze)/Teilchenzahl für freie Fermionen über die L×L-Matrix."""
    h = -J * (np.eye(L, k=1) + np.eye(L, k=-1))
    E, V = np.linalg.eigh(h)
    n0 = (np.arange(L) % 2 == 0).astype(float)
    sign = np.where(np.arange(L) % 2 == 0, 1.0, -1.0)
    out = []
    for t in times:
        U = (V * np.exp(-1j * E * t)) @ V.T
        out.append(sign @ (np.abs(U) ** 2 @ n0) / n0.sum())
    return np.array(out)


def hubbard_imbalance(L, times, U=4.0, J=1.0):
    """Dieselbe Imbalance der Spin-↑-Teilchen im Hubbard-Modell, exakt im Block mit L/2 Teilchen je Spin."""
    states = np.array([sum(1 << i for i in c) for c in combinations(range(L), L // 2)])
    index = {s: k for k, s in enumerate(states)}
    rows, cols = [], []
    for k, s in enumerate(states):
        for i in range(L - 1):
            if ((s >> i) & 1) != ((s >> (i + 1)) & 1):
                rows.append(index[s ^ (1 << i) ^ (1 << (i + 1))])
                cols.append(k)
    m = len(states)
    T = sparse.csr_matrix((-J * np.ones(len(rows)), (rows, cols)), shape=(m, m))
    I = sparse.identity(m, format="csr")
    bits = (states[:, None] >> np.arange(L)) & 1
    double = (bits @ bits.T).ravel()                          # Doppelbesetzungen für (↑-Zustand, ↓-Zustand)
    H = sparse.kron(T, I) + sparse.kron(I, T) + U * sparse.diags(double.astype(float))
    up0 = index[sum(1 << i for i in range(0, L, 2))]
    dn0 = index[sum(1 << i for i in range(1, L, 2))]
    psi0 = np.zeros(m * m, complex)
    psi0[up0 * m + dn0] = 1
    psis = expm_multiply(-1j * H, psi0, start=times[0], stop=times[-1], num=len(times), endpoint=True)
    sign = np.where(np.arange(L) % 2 == 0, 1.0, -1.0)
    up_imb = bits @ sign / (L // 2)                           # Imbalance je ↑-Zustand
    return np.array([(np.abs(p.reshape(m, m)) ** 2).sum(axis=1) @ up_imb for p in psis]), m * m


def validate(circuits=40, n=6, layers=6, t_count=6, seed=0):
    """Größte Abweichung zwischen Pauli-Pfaden und Zustandsvektor über viele kleine Schaltungen und alle Qubits."""
    worst, nonzero = 0.0, 0
    for k in range(circuits):
        g = random_circuit(n, layers, t_count, seed + k, window=1.0)
        for q in range(n):
            a, _ = heisenberg(g, n, q)
            worst = max(worst, abs(a - statevector(g, n, q)))
            nonzero += abs(a) > 1e-9
    return worst, nonzero, circuits * n


def plot_simulability(n=24, layers=60, t_counts=range(0, 37, 4), repeats=6, L_free=(4, 8, 16, 32, 64, 128, 256, 512, 1024),
                      L_hub=(4, 6, 8, 10, 12), U=4.0, t_max=10.0, seed=0):
    """Links: Pauli-Strings und Rechenzeit gegen die Zahl der T-Gatter; rechts: Rechenzeit freier und wechselwirkender Fermionen."""
    t_counts = list(t_counts)
    worst, nonzero, total = validate(seed=seed)
    print(f"Prüfung: {total} Erwartungswerte ⟨Z_q⟩ aus 40 Schaltungen mit 6 Qubits und 6 T-Gattern ({nonzero} davon ≠ 0), "
          f"Pauli-Pfade gegen Zustandsvektor: größte Abweichung {worst:.0e}")
    peaks, secs = [], []
    for t in t_counts:
        pk, sc = [], []
        for r in range(repeats):
            gates = random_circuit(n, layers, t, seed + 100 + r)
            t0 = time.perf_counter()
            pk.append(heisenberg(gates, n, n // 2)[1])         # Messgröße Z in der Mitte der Kette
            sc.append(time.perf_counter() - t0)
        peaks.append(np.exp(np.mean(np.log(pk))))             # geometrisches Mittel
        secs.append(np.mean(sc))
    alpha = np.polyfit(t_counts[len(t_counts) // 2:], np.log2(peaks[len(t_counts) // 2:]), 1)[0]
    print(f"{n} Qubits, Messgröße Z auf Qubit {n // 2}, {layers} Lagen Clifford-Gatter ({len(random_circuit(n, layers, 0, seed))} Gatter); ein Zustandsvektor "
          f"bräuchte 2^{n} = {2 ** n:.1e} Amplituden. Mittel über {repeats} Schaltungen je Zahl der T-Gatter:")
    print("  T-Gatter | Pauli-Strings (höchstens gleichzeitig) | Rechenzeit")
    for t, pk, sc in zip(t_counts, peaks, secs):
        print(f"  {t:8d} | {pk:10.0f} | {sc * 1e3:8.1f} ms")
    print(f"  Anstieg in der zweiten Hälfte: Faktor 2^{alpha:.2f} = {2 ** alpha:.2f} je T-Gatter")
    times = np.linspace(0, t_max, 41)
    I_free = free_imbalance(8, times)
    I_hub0, _ = hubbard_imbalance(8, times, U=0.0)
    print(f"Fermionen, L = 8: Hubbard mit U = 0 gegen freie Rechnung, größte Abweichung der Imbalance {np.max(np.abs(I_free - I_hub0)):.1e}")
    tf, th, dims = [], [], []
    for L in L_free:
        t0 = time.perf_counter()
        free_imbalance(L, times)
        tf.append(time.perf_counter() - t0)
    for L in L_hub:
        t0 = time.perf_counter()
        I_hub, dim = hubbard_imbalance(L, times, U=U)
        th.append(time.perf_counter() - t0)
        dims.append(dim)
    print("  frei (L×L-Matrix): " + ", ".join(f"L = {L}: {s * 1e3:.0f} ms" for L, s in zip(L_free, tf)))
    print(f"  Hubbard U = {U:g} (Dimension C(L, L/2)²): " + ", ".join(f"L = {L}: {d:,} Zustände, {s:.2f} s".replace(",", " ")
                                                                   for L, d, s in zip(L_hub, dims, th)))
    print(f"  Imbalance bei t = {t_max:g}, L = {L_hub[-1]}: frei {free_imbalance(L_hub[-1], times)[-1]:+.3f}, mit U = {U:g} {I_hub[-1]:+.3f}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    ax = axes[0]
    ax.semilogy(t_counts, peaks, "o-", color="tab:red", label=f"Pauli-Strings, {n} Qubits (Mittel über {repeats} Schaltungen)")
    tc = np.array(t_counts)
    ax.semilogy(tc, peaks[-1] * 2.0 ** (alpha * (tc - tc[-1])), ":", color="grey", label=f"Faktor {2 ** alpha:.2f} je T-Gatter")
    ax.set_xlabel("Zahl der T-Gatter t (Clifford-Gatter beliebig viele)")
    ax.set_ylabel("Pauli-Strings im Heisenberg-Bild")
    tw = ax.twinx()
    tw.semilogy(t_counts, np.array(secs) * 1e3, "s--", color="tab:blue", ms=4, label="Rechenzeit")
    tw.set_ylabel("Rechenzeit [ms]", color="tab:blue")
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = tw.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=8, loc="upper left")
    ax.set_title("Clifford-Gatter kosten nichts, jedes T-Gatter vervielfacht die Arbeit", fontsize=10)
    ax = axes[1]
    ax.loglog(L_free, tf, "o-", color="tab:green", label="frei (Grad 2): L×L-Matrix")
    ax.loglog(L_hub, th, "s-", color="tab:red", label=f"Hubbard (Grad 4), U = {U:g}: exakt")
    for L, d, s in zip(L_hub, dims, th):
        ax.annotate(f"{d:,}".replace(",", " "), (L, s), textcoords="offset points", xytext=(4, -10), fontsize=7, color="tab:red")
    ax.set_xlabel("Zahl der Plätze L")
    ax.set_ylabel(f"Rechenzeit für {len(times)} Zeitpunkte [s]")
    ax.set_title(f"Fermionen: frei bis L = {L_free[-1]} in Sekunden, wechselwirkend bei L = {L_hub[-1]} am Ende", fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()
    return peaks, tf, th
