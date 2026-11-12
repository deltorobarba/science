"""Quantenzustände für reconstruction.ipynb (Tomographie, Classical Shadows) und principal_axes.ipynb (Schmidt-Zerlegung).

Alles simuliert mit numpy und scipy (keine Downloads, kein Quanten-SDK). Teil 1: Ein reiner Zustand aus q Qubits hat
4^q − 1 Pauli-Erwartungswerte; gemessen wird nur eine zufällige Auswahl, jeweils mit endlich vielen Schüssen.
Rekonstruiert wird linear (fehlende Werte = 0, das Gegenstück zum Dirty Image) und mit der Annahme „Rang 1“
(projizierter Gradientenabstieg, wie Compressed Sensing für Matrizen). Teil 2: Classical Shadows (Huang, Kueng,
Preskill 2020) sagen viele Erwartungswerte des Grundzustands einer Ising-Kette voraus, ohne den Zustand zu
rekonstruieren. Teil 3: Die Schmidt-Zerlegung ist die Singulärwertzerlegung eines Zustands über einen Schnitt; ihre
Koeffizienten sind die Hauptachsen des Zustands, wie bei einer PCA.
"""
import itertools
import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix, identity, kron
from scipy.sparse.linalg import eigsh

PAULI = {"I": np.eye(2), "X": np.array([[0, 1], [1, 0]]), "Y": np.array([[0, -1j], [1j, 0]]), "Z": np.diag([1.0, -1.0])}


# ---- Teil 1: Tomographie aus einer Auswahl von Pauli-Erwartungswerten

def pauli_basis(q):
    """Alle 4^q − 1 Pauli-Strings ohne die Identität: Namen und Matrizen (Form (4^q − 1, 2^q, 2^q))."""
    names = ["".join(p) for p in itertools.product("IXYZ", repeat=q)][1:]
    mats = []
    for name in names:
        m = np.array([[1.0]])
        for c in name:
            m = np.kron(m, PAULI[c])
        mats.append(m)
    return names, np.array(mats)


def random_pure_state(q, seed=0):
    """Zufälliger reiner Zustand (gleichverteilt auf der Einheitssphäre, Haar-Maß) mit 2^q Amplituden."""
    rng = np.random.default_rng(seed)
    psi = rng.normal(size=2 ** q) + 1j * rng.normal(size=2 ** q)
    return psi / np.linalg.norm(psi)


def measure(psi, mats, shots, seed=0):
    """Erwartungswert jedes Pauli-Strings aus `shots` Messungen mit Ergebnis ±1 (Binomialverteilung)."""
    rng = np.random.default_rng(seed)
    exact = np.einsum("i,pij,j->p", psi.conj(), mats, psi).real
    return 2 * rng.binomial(shots, (1 + exact) / 2) / shots - 1


def linear_inversion(mats, y):
    """ρ = (I + Σ_P y_P P) / d über die gemessenen P; nicht gemessene Erwartungswerte zählen als 0."""
    d = mats.shape[1]
    return (np.eye(d) + np.einsum("p,pij->ij", y, mats)) / d


def low_rank(mats, y, rank=1, n_iter=100):
    """Zustand mit Rang `rank`, der zu den gemessenen Erwartungswerten passt (Singular Value Projection).

    Je Schritt: Gradientenschritt auf Σ (Tr(P ρ) − y_P)², Schrittweite (d² − 1)/m, dann auf die Matrizen mit Rang
    `rank`, positiven Eigenwerten und Spur 1 projizieren (die größten Eigenwerte behalten).
    """
    m, d = len(y), mats.shape[1]
    rho = linear_inversion(mats, y)
    for _ in range(n_iter):
        r = y - np.einsum("pij,ji->p", mats, rho).real
        rho = rho + (d * d - 1) / m * np.einsum("p,pij->ij", r, mats) / d
        w, V = np.linalg.eigh(rho)
        w, V = np.clip(w[-rank:], 0, None), V[:, -rank:]
        rho = (V * (w / w.sum())) @ V.conj().T
    return rho


def fidelity(psi, rho):
    """⟨ψ|ρ|ψ⟩: Wahrscheinlichkeit, dass ρ einen Test auf den Zustand ψ besteht (1 = gleich)."""
    return float(np.real(psi.conj() @ rho @ psi))


def tomography_scan(q, ms, shots, trials=5, seed=0):
    """Fidelity linear und mit Rang 1 gegen die Zahl m der gemessenen Pauli-Strings (Mittel über `trials`)."""
    names, mats = pauli_basis(q)
    rng = np.random.default_rng(seed)
    out = {"linear": np.zeros(len(ms)), "Rang 1": np.zeros(len(ms))}
    for t in range(trials):
        psi = random_pure_state(q, seed=seed + t)
        y_all = measure(psi, mats, shots, seed=seed + 100 + t)
        for j, m in enumerate(ms):
            sel = rng.choice(len(mats), m, replace=False)
            out["linear"][j] += fidelity(psi, linear_inversion(mats[sel], y_all[sel])) / trials
            out["Rang 1"][j] += fidelity(psi, low_rank(mats[sel], y_all[sel])) / trials
    d = 2 ** q
    print(f"{q} Qubits: Dichtematrix mit {d * d - 1} reellen Zahlen, reiner Zustand mit {2 * d - 2} Parametern")
    for m, fl, fr in zip(ms, out["linear"], out["Rang 1"]):
        print(f"  m = {m:4d} Pauli-Strings ({m / (d * d - 1):4.0%}): Fidelity linear {fl:.2f}, mit Rang 1 {fr:.2f}")
    return out


def plot_tomography(q, ms, scan, shots):
    """Fidelity gegen die Zahl der gemessenen Pauli-Strings; Linien bei 2·2^q − 2 (Zahl der Parameter) und 4^q − 1."""
    d = 2 ** q
    fig, ax = plt.subplots(figsize=(10, 4.5))
    for (name, f), c in zip(scan.items(), ["tab:blue", "tab:red"]):
        ax.plot(ms, f, "o-", ms=4, color=c, label=f"{name} rekonstruiert")
    ax.axvline(2 * d - 2, color="grey", ls="--", lw=1, label=f"{2 * d - 2} = reelle Parameter eines reinen Zustands")
    ax.axvline(d * d - 1, color="black", ls=":", lw=1, label=f"{d * d - 1} = alle Pauli-Strings")
    ax.set_xscale("log")
    ax.set_xticks([20, 50, 100, 200, 500, 1000], ["20", "50", "100", "200", "500", "1000"])
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("Zahl m der gemessenen Pauli-Strings")
    ax.set_ylabel("Fidelity ⟨ψ|ρ̂|ψ⟩")
    ax.set_title(f"{q} Qubits, zufälliger reiner Zustand, je Pauli-String {shots} Schüsse", fontsize=10)
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    plt.show()


# ---- Teil 2: Classical Shadows

def ising_ground_state(q, h=1.0, J=1.0):
    """Grundzustand der offenen Ising-Kette H = −J Σ Z_i Z_{i+1} − h Σ X_i (h = J: kritischer Punkt)."""
    X, Z = csr_matrix(PAULI["X"]), csr_matrix(PAULI["Z"])

    def op(single, i):
        return kron(kron(identity(2 ** i), single), identity(2 ** (q - i - 1)), format="csr")

    H = sum(-J * op(Z, i) @ op(Z, i + 1) for i in range(q - 1)) + sum(-h * op(X, i) for i in range(q))
    _, v = eigsh(H, k=1, which="SA")
    return v[:, 0].astype(complex)


def expect(psi, q, pauli):
    """Exakter Erwartungswert eines Pauli-Strings, gegeben als {Qubit: "X"/"Y"/"Z"}."""
    phi = psi.reshape([2] * q)
    for i, c in pauli.items():
        phi = np.moveaxis(np.tensordot(PAULI[c], phi, axes=([1], [i])), 0, i)
    return float(np.real(np.vdot(psi, phi.ravel())))


# Drehungen vor der Messung in der Z-Basis: X-Basis über Hadamard, Y-Basis über H·S†
_ROT = {0: np.array([[1, 1], [1, -1]]) / np.sqrt(2), 1: np.array([[1, -1j], [1, 1j]]) / np.sqrt(2), 2: np.eye(2)}
BASIS = "XYZ"


def snapshots(psi, q, n, seed=0):
    """n Schnappschüsse: jedes Qubit in einer zufälligen Pauli-Basis messen. Gibt Basen (n, q) und Ergebnisse ±1 zurück."""
    rng = np.random.default_rng(seed)
    bases = rng.integers(0, 3, size=(n, q))
    outcomes = np.empty((n, q), dtype=int)
    for s in range(n):
        phi = psi.reshape([2] * q)
        for i in range(q):
            phi = np.moveaxis(np.tensordot(_ROT[bases[s, i]], phi, axes=([1], [i])), 0, i)
        p = np.abs(phi.ravel()) ** 2
        k = rng.choice(2 ** q, p=p / p.sum())
        bits = (k >> np.arange(q - 1, -1, -1)) & 1                   # Qubit 0 ist das höchste Bit
        outcomes[s] = 1 - 2 * bits
    return bases, outcomes


def shadow_estimate(bases, outcomes, pauli):
    """Schätzwert eines Pauli-Strings aus den Schnappschüssen: Mittel von 3^w · Π Ergebnis, wenn alle Basen passen, sonst 0."""
    idx = list(pauli)
    want = np.array([BASIS.index(c) for c in pauli.values()])
    match = np.all(bases[:, idx] == want, axis=1)
    return float(np.mean(match * 3.0 ** len(idx) * np.prod(outcomes[:, idx], axis=1)))


def shadow_study(psi, q, bases, outcomes, n_show, ns, weights=(1, 2, 3, 4)):
    """Schätzt alle ⟨Z_i Z_j⟩ aus den ersten n_show Schnappschüssen und misst den Fehler gegen N je Gewicht w.

    Für jedes w die Strings aus w benachbarten X oder w benachbarten Z; Fehler gemittelt über alle Strings und über
    getrennte Blöcke von N Schnappschüssen. Druckt die Zahlen und zeichnet beide Bilder.
    """
    pairs = [(i, j) for i in range(q) for j in range(i + 1, q)]
    dist = np.array([j - i for i, j in pairs])
    exact_zz = np.array([expect(psi, q, {i: "Z", j: "Z"}) for i, j in pairs])
    shadow_zz = np.array([shadow_estimate(bases[:n_show], outcomes[:n_show], {i: "Z", j: "Z"}) for i, j in pairs])
    errors = {}
    for w in weights:
        obs = [{s + k: c for k in range(w)} for s in range(q - w + 1) for c in "XZ"]
        ex = np.array([expect(psi, q, o) for o in obs])
        err = []
        for n in ns:
            blocks = [slice(b * n, (b + 1) * n) for b in range(min(len(bases) // n, 10))]
            err.append(np.mean([[abs(shadow_estimate(bases[b], outcomes[b], o) - x) for o, x in zip(obs, ex)] for b in blocks]))
        errors[w] = np.array(err)
    n_pauli = f"{4 ** q - 1:,}".replace(",", " ")
    print(f"{q} Qubits: Der Zustand hat 2^{q} = {2 ** q} Amplituden, die Dichtematrix {n_pauli} Pauli-Erwartungswerte")
    print(f"Aus {n_show} Schnappschüssen alle {len(pairs)} Korrelationen ⟨Z_i Z_j⟩: "
          f"mittlerer Fehler {np.mean(np.abs(shadow_zz - exact_zz)):.3f}, größter {np.max(np.abs(shadow_zz - exact_zz)):.3f}")
    for w, err in errors.items():
        print(f"  Gewicht {w}: Fehler " + ", ".join(f"{e:.3f} (N = {n})" for n, e in zip(ns, err))
              + f";  Theorie √(2/π)·√(3^w/N) bei N = {ns[-1]}: {np.sqrt(2 / np.pi * 3 ** w / ns[-1]):.3f}")
    plot_shadows(q, dist, exact_zz, shadow_zz, n_show, ns, errors)
    return exact_zz, shadow_zz, errors


def plot_shadows(q, dist, exact_zz, shadow_zz, n_used, ns, errors):
    """Links: ⟨Z_i Z_j⟩ gegen den Abstand, exakt und aus den Schnappschüssen. Rechts: Fehler gegen die Zahl der Schnappschüsse."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    axes[0].plot(dist, exact_zz, "o", ms=9, mfc="none", color="black", label="exakt")
    axes[0].plot(dist, shadow_zz, ".", ms=7, color="tab:red", label=f"aus {n_used} Schnappschüssen")
    axes[0].set_xlabel("Abstand |i − j| der Qubits")
    axes[0].set_ylabel("⟨Z_i Z_j⟩")
    axes[0].set_title(f"Korrelationen im Grundzustand der Ising-Kette ({q} Qubits, h = J)", fontsize=10)
    axes[0].legend(fontsize=9)
    for (w, err), c in zip(errors.items(), plt.cm.viridis(np.linspace(0.1, 0.8, len(errors)))):
        axes[1].loglog(ns, err, "o-", ms=4, color=c, label=f"Gewicht w = {w}")
        axes[1].loglog(ns, np.sqrt(2 / np.pi * 3.0 ** w / np.array(ns)), "--", lw=0.8, color=c)
    ticks = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1]
    axes[1].set_yticks(ticks, [str(t) for t in ticks])
    axes[1].set_xlabel("Zahl N der Schnappschüsse")
    axes[1].set_ylabel("mittlerer Fehler |Schätzwert − exakt|")
    axes[1].set_title("Fehler gegen Schnappschüsse; gestrichelt √(2/π)·√(3^w/N)", fontsize=10)
    axes[1].legend(fontsize=9)
    fig.tight_layout()
    plt.show()


# ---- Teil 3: Schmidt-Zerlegung = Singulärwertzerlegung eines Zustands (principal_axes.ipynb)

def ghz_state(q):
    """GHZ-Zustand (|00…0⟩ + |11…1⟩)/√2."""
    psi = np.zeros(2 ** q, dtype=complex)
    psi[0] = psi[-1] = 1 / np.sqrt(2)
    return psi


def schmidt(psi, q, cut):
    """Schmidt-Koeffizienten (absteigend) für den Schnitt nach `cut` Qubits: Singulärwerte von ψ als 2^cut × 2^(q−cut)-Matrix.

    Ihre Quadrate sind die Eigenwerte der reduzierten Dichtematrix ρ_A = M M†, also die Varianzen entlang der
    Hauptachsen des Zustands; ihre Summe ist 1.
    """
    return np.linalg.svd(psi.reshape(2 ** cut, 2 ** (q - cut)), compute_uv=False)


def entanglement_entropy(s):
    """Von-Neumann-Entropie −Σ s² ln s² der Schmidt-Koeffizienten (0 = Produktzustand)."""
    p = s ** 2
    p = p[p > 1e-15]
    return float(-(p * np.log(p)).sum())


def schmidt_study(q, states, keep=0.999):
    """Schmidt-Spektrum am mittleren Schnitt für mehrere Zustände: wie viele Achsen tragen den Zustand?"""
    cut = q // 2
    print(f"{q} Qubits, Schnitt in der Mitte: höchstens {2 ** cut} Schmidt-Achsen, "
          f"größte mögliche Entropie ln {2 ** cut} = {np.log(2 ** cut):.2f}")
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.6))
    for (name, psi), c in zip(states.items(), ["tab:green", "tab:red", "tab:purple", "black"]):
        s = schmidt(psi, q, cut)
        p = s ** 2
        chi = int(np.searchsorted(np.cumsum(p), keep) + 1)
        print(f"  {name:32s} Entropie {entanglement_entropy(s):.3f}; {chi:2d} Achsen tragen {keep:.1%} des Gewichts")
        idx = np.arange(1, len(p) + 1)
        axes[0].semilogy(idx, np.maximum(p, 1e-16), "o-", ms=3, color=c, label=name)
        axes[1].semilogx(idx, np.cumsum(p), "o-", ms=3, color=c, label=name)
    axes[0].set_ylim(1e-14, 2)
    axes[0].set_xlabel("Index i der Schmidt-Achse")
    axes[0].set_ylabel("Gewicht s_i² (Eigenwert von ρ_A)")
    axes[0].set_title("Schmidt-Spektrum: die Eigenwerte der reduzierten Dichtematrix", fontsize=10)
    axes[0].legend(fontsize=8)
    axes[1].axhline(keep, color="grey", ls="--", lw=1)
    axes[1].set_xlabel("Zahl der behaltenen Achsen χ")
    axes[1].set_ylabel("behaltenes Gewicht Σ s_i² (Fidelity der Kürzung)")
    axes[1].set_title("Wie bei der PCA: erklärter Anteil gegen Zahl der Achsen", fontsize=10)
    axes[1].legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    plt.show()
