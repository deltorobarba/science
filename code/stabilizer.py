"""Clifford-Schaltkreise für symmetries.ipynb: Gottesman–Knill mit einem Tableau-Simulator, gegen einen Zustandsvektor.

Die Clifford-Gatter (H, S, CNOT) bilden Pauli-Operatoren wieder auf Pauli-Operatoren ab; sie sind die Symmetrien der
Pauli-Gruppe. Ein Zustand aus solchen Gattern ist deshalb durch n Pauli-Strings bestimmt, die ihn festhalten
(Stabilisatoren), statt durch 2^n Amplituden. Der Tableau-Simulator folgt Aaronson und Gottesman (2004, „CHP“): 2n Zeilen
aus Bits für X- und Z-Anteile und ein Vorzeichen. Zum Prüfen dient ein einfacher Zustandsvektor-Simulator in numpy.
"""
import time

import numpy as np
import matplotlib.pyplot as plt


class Tableau:
    """Stabilizer-Zustand von n Qubits, Start |0…0⟩. Zeilen 0…n−1 Destabilisatoren, n…2n−1 Stabilisatoren, 2n Hilfszeile."""

    def __init__(self, n, seed=0):
        self.n = n
        self.x = np.zeros((2 * n + 1, n), dtype=bool)
        self.z = np.zeros((2 * n + 1, n), dtype=bool)
        self.r = np.zeros(2 * n + 1, dtype=bool)
        self.x[np.arange(n), np.arange(n)] = True
        self.z[np.arange(n) + n, np.arange(n)] = True
        self.rng = np.random.default_rng(seed)

    def h(self, a):
        self.r ^= self.x[:, a] & self.z[:, a]
        self.x[:, a], self.z[:, a] = self.z[:, a].copy(), self.x[:, a].copy()

    def s(self, a):
        self.r ^= self.x[:, a] & self.z[:, a]
        self.z[:, a] ^= self.x[:, a]

    def cnot(self, a, b):
        self.r ^= self.x[:, a] & self.z[:, b] & ~(self.x[:, b] ^ self.z[:, a])
        self.x[:, b] ^= self.x[:, a]
        self.z[:, a] ^= self.z[:, b]

    def _rowsum(self, h, i):
        """Zeile h := Zeile i · Zeile h, mit dem Vorzeichen aus den Phasen der Pauli-Produkte."""
        x1, z1, x2, z2 = self.x[i].astype(int), self.z[i].astype(int), self.x[h].astype(int), self.z[h].astype(int)
        g = np.where((x1 == 1) & (z1 == 1), z2 - x2,
            np.where((x1 == 1) & (z1 == 0), z2 * (2 * x2 - 1),
            np.where((x1 == 0) & (z1 == 1), x2 * (1 - 2 * z2), 0)))
        total = 2 * int(self.r[h]) + 2 * int(self.r[i]) + int(g.sum())
        self.r[h] = (total % 4) == 2
        self.x[h] ^= self.x[i]
        self.z[h] ^= self.z[i]

    def measure(self, a):
        """Qubit a in der Z-Basis messen; gibt 0 oder 1 zurück und ändert den Zustand wie eine echte Messung."""
        n = self.n
        p = np.flatnonzero(self.x[n:2 * n, a])
        if len(p):                                            # Ergebnis zufällig
            p = int(p[0]) + n
            for i in np.flatnonzero(self.x[:2 * n, a]):
                if i != p:
                    self._rowsum(i, p)
            self.x[p - n], self.z[p - n], self.r[p - n] = self.x[p].copy(), self.z[p].copy(), self.r[p]
            self.x[p] = False
            self.z[p] = False
            self.z[p, a] = True
            self.r[p] = self.rng.random() < 0.5
            return int(self.r[p])
        self.x[2 * n] = False                                 # Ergebnis fest: aus den Stabilisatoren zusammensetzen
        self.z[2 * n] = False
        self.r[2 * n] = False
        for i in np.flatnonzero(self.x[:n, a]):
            self._rowsum(2 * n, i + n)
        return int(self.r[2 * n])

    def stabilizers(self):
        """Die n Stabilisatoren als Text, etwa '+XXZI' (Zeichen j gehört zu Qubit j)."""
        out = []
        for i in range(self.n, 2 * self.n):
            p = "".join("IXZY"[int(xx) + 2 * int(zz)] for xx, zz in zip(self.x[i], self.z[i]))
            out.append(("-" if self.r[i] else "+") + p)
        return out


# ---- Zustandsvektor zum Prüfen

def _apply(psi, n, gate, *q):
    psi = psi.reshape([2] * n)
    if gate == "cnot":
        a, b = q
        idx = [slice(None)] * n
        idx[a] = 1
        sub = psi[tuple(idx)]
        axis = b if b < a else b - 1
        psi = psi.copy()
        psi[tuple(idx)] = np.flip(sub, axis=axis)
        return psi.reshape(-1)
    U = {"h": np.array([[1, 1], [1, -1]]) / np.sqrt(2), "s": np.diag([1, 1j])}[gate]
    return np.moveaxis(np.tensordot(U, psi, axes=([1], [q[0]])), 0, q[0]).reshape(-1)


def _pauli_apply(psi, n, label):
    P = {"I": np.eye(2), "X": np.array([[0, 1], [1, 0]]), "Y": np.array([[0, -1j], [1j, 0]]), "Z": np.diag([1, -1])}
    sign = -1 if label[0] == "-" else 1
    out = psi.reshape([2] * n).astype(complex)
    for j, c in enumerate(label[1:]):
        if c != "I":
            out = np.moveaxis(np.tensordot(P[c], out, axes=([1], [j])), 0, j)
    return sign * out.reshape(-1)


def random_circuit(n, depth, rng):
    gates = []
    for _ in range(depth):
        g = rng.choice(["h", "s", "cnot"])
        if g == "cnot":
            a, b = rng.choice(n, 2, replace=False)
            gates.append(("cnot", int(a), int(b)))
        else:
            gates.append((g, int(rng.integers(n))))
    return gates


def check(n=8, depth=60, circuits=20, seed=0):
    """Zufällige Clifford-Schaltkreise: Hält jeder Stabilisator des Tableaus den Zustandsvektor fest (g|ψ⟩ = |ψ⟩)?"""
    rng = np.random.default_rng(seed)
    worst = 0.0
    for c in range(circuits):
        T = Tableau(n)
        psi = np.zeros(2 ** n, complex)
        psi[0] = 1
        for g in random_circuit(n, depth, rng):
            getattr(T, g[0])(*g[1:])
            psi = _apply(psi, n, *g)
        for st in T.stabilizers():
            worst = max(worst, np.max(np.abs(_pauli_apply(psi, n, st) - psi)))
    return worst


def ghz(T):
    T.h(0)
    for q in range(1, T.n):
        T.cnot(q - 1, q)


def plot_scaling(ns_tab=(10, 30, 100, 300, 1000), ns_vec=(10, 14, 18, 20, 22, 24), seed=0):
    """GHZ-Zustand präparieren und alle Qubits messen: Rechenzeit Tableau gegen Zustandsvektor."""
    worst = check()
    print(f"Prüfung an 20 zufälligen Clifford-Schaltkreisen mit 8 Qubits: größte Abweichung von g|ψ⟩ = |ψ⟩ {worst:.1e}")
    T = Tableau(5, seed)
    ghz(T)
    print("Stabilisatoren des GHZ-Zustands mit 5 Qubits: " + ", ".join(T.stabilizers()))
    outs = [T.measure(q) for q in range(5)]
    print(f"Messung aller 5 Qubits: {outs} (alle gleich, wie beim GHZ-Zustand)")
    t_tab = []
    for n in ns_tab:
        T = Tableau(n, seed)
        t0 = time.perf_counter()
        ghz(T)
        outs = [T.measure(q) for q in range(n)]
        t_tab.append(time.perf_counter() - t0)
        assert len(set(outs)) == 1
    t_vec = []
    for n in ns_vec:
        psi = np.zeros(2 ** n, complex)
        psi[0] = 1
        t0 = time.perf_counter()
        psi = _apply(psi, n, "h", 0)
        for q in range(1, n):
            psi = _apply(psi, n, "cnot", q - 1, q)
        t_vec.append(time.perf_counter() - t0)
    k_tab = np.polyfit(np.log(ns_tab[2:]), np.log(t_tab[2:]), 1)[0]
    k_vec = np.polyfit(ns_vec[2:], np.log2(t_vec[2:]), 1)[0]
    print("Tableau:       " + ", ".join(f"{n} Qubits {t:.3f} s" for n, t in zip(ns_tab, t_tab))
          + f"; wächst etwa wie n^{k_tab:.1f}")
    print("Zustandsvektor: " + ", ".join(f"{n} Qubits {t:.3f} s" for n, t in zip(ns_vec, t_vec))
          + f"; wächst etwa wie 2^({k_vec:.2f}·n)")
    print(f"Speicher: Zustandsvektor bei 50 Qubits {16 * 2 ** 50 / 1e15:.0f} Petabyte, Tableau bei 1000 Qubits "
          f"{2 * 1000 * 2001 / 8 / 1e6:.1f} Megabyte")
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.loglog(ns_tab, t_tab, "o-", color="tab:blue", label=f"Tableau (2n Pauli-Strings): etwa n^{k_tab:.1f}")
    ax.loglog(ns_vec, t_vec, "s-", color="tab:red", label="Zustandsvektor (2ⁿ Amplituden): exponentiell")
    ax.set_xlabel("Zahl der Qubits n")
    ax.set_ylabel("Rechenzeit [s]")
    ax.set_title("GHZ-Zustand präparieren und messen: Symmetrie macht aus 2ⁿ Zahlen 2n²", fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()
