"""Ein Bell-Zustand auf echter Hardware für reconstruction.ipynb: was eine Messbasis verrät, Tomographie aus neun Basen.

Zwei Qubits im Zustand |Φ⁺⟩ = (|00⟩ + |11⟩)/√2, präpariert mit Hadamard und CNOT. Ein Zwei-Qubit-Zustand hat 15
Pauli-Erwartungswerte; eine Messung in einer Produktbasis (z. B. Z auf beiden Qubits) liefert davon nur drei. Die
Tomographie misst alle neun Basen {X, Y, Z}², dazu vier Kalibrier-Schaltkreise für die Konfusionsmatrix der Auslese.

Messdaten: Zählungen von IBM-Quantencomputern (Konstanten unten, mit Datum, Gerät und Job-ID). `run_ibm` wiederholt
den Lauf; es braucht qiskit, qiskit-ibm-runtime und einen IBM-Token und importiert qiskit erst beim Aufruf, die
Auswertung läuft ohne qiskit. Schlüsselkonvention wie in qiskit: "b1b0", rechts steht Qubit 0.
"""
import itertools
import json
from datetime import date

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import nnls

from tomography import PAULI

KEYS = ["00", "01", "10", "11"]                             # Messergebnis "b1b0"
SETTINGS = ["".join(p) for p in itertools.product("XYZ", repeat=2)]   # Basis für Qubit 0, dann Qubit 1
PAULIS = ["".join(p) for p in itertools.product("IXYZ", repeat=2)][1:]  # 15 Strings, Zeichen 0 für Qubit 0

# Erster Lauf (Notebook bellstatepreparation, 2026-09-11): nur die Z-Basis, 100 Schüsse auf ibm_aachen
ZZ_2026_09_11 = {"backend": "ibm_aachen", "date": "2026-09-11", "shots": 100,
                 "counts": {"11": 54, "00": 42, "01": 2, "10": 2}}

# Tomographie (2026-11-12): neun Basen und vier Kalibrierungen zu je 1000 Schüssen auf ibm_aachen, 6 s Rechenzeit
AACHEN_2026_11_12 = {"backend": "ibm_aachen", "date": "2026-11-12", "job_id": "dbqtp2kim45s738hefh0", "qubits": [0, 1],
                     "shots": 1000, "counts": {
                         "bell_XX": {"00": 501, "01": 15, "10": 14, "11": 470},
                         "bell_XY": {"00": 237, "01": 261, "10": 244, "11": 258},
                         "bell_XZ": {"00": 257, "01": 267, "10": 237, "11": 239},
                         "bell_YX": {"00": 283, "01": 230, "10": 238, "11": 249},
                         "bell_YY": {"00": 19, "01": 485, "10": 481, "11": 15},
                         "bell_YZ": {"00": 265, "01": 253, "10": 264, "11": 218},
                         "bell_ZX": {"00": 265, "01": 240, "10": 252, "11": 243},
                         "bell_ZY": {"00": 267, "01": 223, "10": 262, "11": 248},
                         "bell_ZZ": {"00": 502, "01": 11, "10": 15, "11": 472},
                         "cal_00": {"00": 975, "01": 17, "10": 8, "11": 0},
                         "cal_01": {"00": 13, "01": 969, "10": 0, "11": 18},
                         "cal_10": {"00": 13, "01": 0, "10": 977, "11": 10},
                         "cal_11": {"00": 0, "01": 14, "10": 12, "11": 974}}}


# ---- Theorie: Zustände und Pauli-Werte

def pauli_matrix(p):
    """4 × 4-Matrix eines Pauli-Strings "AB" (A auf Qubit 0, B auf Qubit 1); Qubit 1 ist der linke Tensorfaktor."""
    return np.kron(PAULI[p[1]], PAULI[p[0]])


def expectations_of(rho):
    """Alle 15 Pauli-Erwartungswerte Tr(ρ P)."""
    return {p: float(np.real(np.trace(rho @ pauli_matrix(p)))) for p in PAULIS}


PHI_PLUS = np.array([1, 0, 0, 1]) / np.sqrt(2)
CANDIDATES = {"|Φ⁺⟩ = (|00⟩ + |11⟩)/√2": np.outer(PHI_PLUS, PHI_PLUS),
              "|Φ⁻⟩ = (|00⟩ − |11⟩)/√2": np.outer([1, 0, 0, -1], [1, 0, 0, -1]) / 2,
              "Gemisch ½|00⟩⟨00| + ½|11⟩⟨11|": np.diag([0.5, 0, 0, 0.5])}


# ---- Auswertung von Zählungen

def probabilities(counts):
    """Wahrscheinlichkeiten in der Reihenfolge KEYS aus einem Dict von Zählungen."""
    n = np.array([counts.get(k, 0) for k in KEYS], dtype=float)
    return n / n.sum()


def outcome_sign(key, qubit):
    """Eigenwert ±1 des gemessenen Qubits: Bit 0 → +1, Bit 1 → −1."""
    return 1 - 2 * int(key[-1 - qubit])


def expectations(setting_probs):
    """Pauli-Erwartungswerte aus den Wahrscheinlichkeiten je Basis; jeder String aus allen Basen, die zu ihm passen.

    Beispiel: ⟨ZI⟩ steckt in den Basen ZX, ZY und ZZ (Qubit 0 in Z), gemittelt über alle drei.
    """
    out = {}
    for p in PAULIS:
        vals = []
        for s, prob in setting_probs.items():
            if all(a in ("I", b) for a, b in zip(p, s)):
                signs = [np.prod([outcome_sign(k, q) for q in range(2) if p[q] != "I"]) for k in KEYS]
                vals.append(float(np.dot(prob, signs)))
        if vals:
            out[p] = float(np.mean(vals))
    return out


def linear_inversion(E):
    """ρ = (I + Σ ⟨P⟩ P) / 4 über alle gemessenen Pauli-Strings; kann negative Eigenwerte haben."""
    rho = np.eye(4, dtype=complex)
    for p, v in E.items():
        rho = rho + v * pauli_matrix(p)
    return rho / 4


def _projector(setting, key):
    """Projektor auf das Ergebnis `key` in der Basis `setting`."""
    ops = [(np.eye(2) + outcome_sign(key, q) * PAULI[setting[q]]) / 2 for q in range(2)]
    return np.kron(ops[1], ops[0])


def maximum_likelihood(setting_probs, steps=500):
    """Physikalischer Zustand (positiv, Spur 1), unter dem die gemessenen Häufigkeiten am wahrscheinlichsten sind (Hradil)."""
    proj = {(s, k): _projector(s, k) for s in setting_probs for k in KEYS}
    rho = np.eye(4, dtype=complex) / 4
    for _ in range(steps):
        R = np.zeros((4, 4), dtype=complex)
        for s, prob in setting_probs.items():
            for k, f in zip(KEYS, prob):
                p = max(np.real(np.trace(proj[s, k] @ rho)), 1e-12)
                R += f / p * proj[s, k]
        rho = R @ rho @ R
        rho /= np.real(np.trace(rho))
    return rho


def fidelity(rho, psi=PHI_PLUS):
    return float(np.real(psi.conj() @ rho @ psi))


def confusion_matrix(cal_counts):
    """A[gemessen, präpariert] aus den vier Kalibrier-Läufen (Spalte j: Häufigkeiten, wenn KEYS[j] präpariert wurde)."""
    return np.column_stack([probabilities(cal_counts[k]) for k in KEYS])


def correct(p, A, method="nnls"):
    """Auslesefehler herausrechnen: A x = p lösen. "invert": direkt (x kann negativ werden); "nnls": mit x ≥ 0, Σx = 1."""
    if method == "invert":
        return np.linalg.solve(A, p)
    w = 100.0                                          # starkes Gewicht für die Bedingung Σx = 1
    x, _ = nnls(np.vstack([A, w * np.ones(4)]), np.concatenate([p, [w]]))
    return x / x.sum()


def direct_fidelity(E):
    """Fidelity mit |Φ⁺⟩ aus nur drei Basen: |Φ⁺⟩⟨Φ⁺| = (II + XX − YY + ZZ)/4, also F = (1 + ⟨XX⟩ − ⟨YY⟩ + ⟨ZZ⟩)/4."""
    return (1 + E["XX"] - E["YY"] + E["ZZ"]) / 4


# ---- Schritt 7: eine Messbasis

def one_basis(data=ZZ_2026_09_11):
    """Was die Z-Basis allein verrät: drei von 15 Pauli-Werten, und welche Zustände dazu passen."""
    c, n = data["counts"], data["shots"]
    E = expectations({"ZZ": probabilities(c)})
    corr = (c.get("00", 0) + c.get("11", 0)) / n
    print(f"{data['backend']}, {data['date']}: {n} Schüsse in der Z-Basis: " + ", ".join(f"{k}: {c.get(k, 0)}" for k in KEYS))
    print(f"Gemessen sind 3 von 15 Pauli-Werten: " + ", ".join(f"⟨{p}⟩ = {E[p]:+.2f}" for p in E)
          + f" (Unsicherheit je etwa ±{1 / np.sqrt(n):.2f})")
    print(f"Korrelierte Ergebnisse (00 oder 11): {corr:.0%}; das ist nur eine obere Schranke der Fidelity mit |Φ⁺⟩")
    for name, rho in CANDIDATES.items():
        Ec = expectations_of(rho)
        print(f"  {name:32s} ⟨ZI⟩ = {Ec['ZI']:+.0f}, ⟨IZ⟩ = {Ec['IZ']:+.0f}, ⟨ZZ⟩ = {Ec['ZZ']:+.0f};  "
              f"aber ⟨XX⟩ = {Ec['XX']:+.0f}, ⟨YY⟩ = {Ec['YY']:+.0f}")
    fig, ax = plt.subplots(figsize=(13, 4.5))
    x = np.arange(len(PAULIS))
    measured = [p in E for p in PAULIS]
    for i, m in enumerate(measured):
        if not m:
            ax.axvspan(i - 0.5, i + 0.5, color="0.92", zorder=0)
    ax.bar([i for i in x if measured[i]], [E[p] for p in PAULIS if p in E], width=0.6, color="tab:blue",
           yerr=1 / np.sqrt(n), capsize=4, label=f"gemessen ({n} Schüsse)")
    for (name, rho), (mk, c) in zip(CANDIDATES.items(), [("o", "tab:red"), ("s", "tab:green"), ("D", "black")]):
        Ec = expectations_of(rho)
        ax.plot(x, [Ec[p] for p in PAULIS], mk, ms=7, mfc="none", mec=c, mew=1.5, label=name)
    ax.axhline(0, color="grey", lw=0.6)
    ax.set_xticks(x, PAULIS)
    ax.set_xlabel("Pauli-String (Zeichen 1: Qubit 0, Zeichen 2: Qubit 1); grau: in der Z-Basis nicht gemessen")
    ax.set_ylabel("Erwartungswert")
    ax.set_ylim(-1.25, 1.65)
    ax.set_title("Eine Messbasis: drei Werte gemessen, zwölf unbekannt; drei verschiedene Zustände passen", fontsize=10)
    ax.legend(fontsize=8, ncol=4, loc="upper center")
    fig.tight_layout()
    plt.show()
    return E


# ---- Schritt 8: Tomographie aus neun Basen

def tomography_study(data):
    """Pauli-Werte roh und ohne Auslesefehler, Rekonstruktion linear und Maximum-Likelihood, direkte Fidelity."""
    c = data["counts"]
    A = confusion_matrix({k: c["cal_" + k] for k in KEYS})
    raw = {s: probabilities(c["bell_" + s]) for s in SETTINGS}
    fixed = {s: correct(p, A) for s, p in raw.items()}
    print(f"{data['backend']}, {data['date']} (Job {data.get('job_id', '?')}), Qubits {data.get('qubits', '?')}: "
          f"9 Basen und 4 Kalibrierungen zu je {data['shots']} Schüssen")
    print("Konfusionsmatrix der Auslese (Spalte: präpariert 00, 01, 10, 11; Zeile: gemessen):")
    for k, row in zip(KEYS, A):
        print(f"  {k}: " + "  ".join(f"{v:.3f}" for v in row))
    results = {}
    for label, probs in [("roh", raw), ("ohne Auslesefehler", fixed)]:
        E = expectations(probs)
        rl, rm = linear_inversion(E), maximum_likelihood(probs)
        lam = np.linalg.eigvalsh(rl)
        results[label] = dict(E=E, linear=rl, mle=rm)
        if label == "roh":                          # Binomialstreuung der Rohdaten; die Korrektur macht sie eher größer
            sigma = np.sqrt(sum((1 - E[p] ** 2) / data["shots"] for p in ["XX", "YY", "ZZ"])) / 4
        print(f"{label}: direkte Fidelity aus XX, YY, ZZ {direct_fidelity(E):.3f} ± {sigma:.3f}; linear {fidelity(rl):.3f} "
              f"(kleinster Eigenwert {lam.min():+.3f}); Maximum-Likelihood {fidelity(rm):.3f}, "
              f"Reinheit Tr ρ² {np.real(np.trace(rm @ rm)):.3f}")
    inv = {s: correct(p, A, "invert") for s, p in raw.items()}
    neg = sum((v < 0).sum() for v in inv.values())
    print(f"Einfaches Invertieren von A gibt {neg} negative Wahrscheinlichkeiten in 36 Werten; mit x ≥ 0 keine")
    ideal = expectations_of(CANDIDATES["|Φ⁺⟩ = (|00⟩ + |11⟩)/√2"])
    fig, axes = plt.subplots(1, 2, figsize=(15, 4.8), gridspec_kw={"width_ratios": [1.7, 1]})
    x = np.arange(len(PAULIS))
    axes[0].bar(x - 0.2, [results["roh"]["E"][p] for p in PAULIS], width=0.4, color="tab:blue", label="roh")
    axes[0].bar(x + 0.2, [results["ohne Auslesefehler"]["E"][p] for p in PAULIS], width=0.4, color="tab:orange",
                label="ohne Auslesefehler")
    axes[0].plot(x, [ideal[p] for p in PAULIS], "o", ms=8, mfc="none", mec="tab:red", mew=1.5, label="ideal |Φ⁺⟩")
    axes[0].axhline(0, color="grey", lw=0.6)
    axes[0].set_xticks(x, PAULIS)
    axes[0].set_ylim(-1.15, 1.15)
    axes[0].set_xlabel("Pauli-String (Zeichen 1: Qubit 0, Zeichen 2: Qubit 1)")
    axes[0].set_ylabel("Erwartungswert")
    axes[0].set_title("Alle 15 Pauli-Werte aus neun Basen", fontsize=10)
    axes[0].legend(fontsize=8, loc="lower left")
    rm = results["ohne Auslesefehler"]["mle"]
    im = axes[1].imshow(np.real(rm), cmap="RdBu_r", vmin=-0.55, vmax=0.55)
    for i in range(4):
        for j in range(4):
            axes[1].text(j, i, f"{np.real(rm[i, j]):+.2f}", ha="center", va="center", fontsize=9)
    labels = ["|00⟩", "|01⟩", "|10⟩", "|11⟩"]
    axes[1].set_xticks(range(4), labels)
    axes[1].set_yticks(range(4), labels)
    axes[1].set_title(f"Re ρ (Maximum-Likelihood), Fidelity {fidelity(rm):.3f}", fontsize=10)
    fig.colorbar(im, ax=axes[1], fraction=0.046)
    fig.tight_layout()
    plt.show()
    return results


# ---- Simulation zum Testen (ohne qiskit) und der Lauf auf echter Hardware

def simulate(shots=1000, depol=0.05, flip=(0.01, 0.03), seed=0):
    """Zählungen wie von der Hardware: Bell-Zustand mit Depolarisation, Auslese kippt Bit 0 und Bit 1 mit Wahrscheinlichkeit flip."""
    rng = np.random.default_rng(seed)
    rho = (1 - depol) * CANDIDATES["|Φ⁺⟩ = (|00⟩ + |11⟩)/√2"] + depol * np.eye(4) / 4
    F = np.zeros((4, 4))                                  # F[gemessen, wahr]
    for j, kt in enumerate(KEYS):
        for i, km in enumerate(KEYS):
            F[i, j] = np.prod([flip[q] if km[-1 - q] != kt[-1 - q] else 1 - flip[q] for q in range(2)])
    counts = {}
    for s in SETTINGS:
        p = np.clip([np.real(np.trace(_projector(s, k) @ rho)) for k in KEYS], 0, None)
        counts["bell_" + s] = dict(zip(KEYS, rng.multinomial(shots, F @ (p / p.sum())).tolist()))
    for j, k in enumerate(KEYS):
        counts["cal_" + k] = dict(zip(KEYS, rng.multinomial(shots, F[:, j]).tolist()))
    return {"backend": "Simulation", "date": str(date.today()), "shots": shots, "counts": counts}


def circuits():
    """Die 13 Schaltkreise: Bell-Zustand in den neun Basen (vor der Messung gedreht) und vier Kalibrierungen."""
    from qiskit import QuantumCircuit
    out = {}
    for s in SETTINGS:
        qc = QuantumCircuit(2, 2, name="bell_" + s)
        qc.h(0)
        qc.cx(0, 1)
        for q, b in enumerate(s):
            if b == "X":
                qc.h(q)
            elif b == "Y":
                qc.sdg(q)
                qc.h(q)
        qc.measure([0, 1], [0, 1])
        out["bell_" + s] = qc
    for k in KEYS:
        qc = QuantumCircuit(2, 2, name="cal_" + k)
        for q in range(2):
            if k[-1 - q] == "1":
                qc.x(q)
        qc.measure([0, 1], [0, 1])
        out["cal_" + k] = qc
    return out


def run_ibm(token=None, shots=1000, backend_name="ibm_aachen"):
    """Alle 13 Schaltkreise in einem Job auf einem IBM-Quantencomputer, auf denselben zwei physikalischen Qubits.

    Ohne `token` nimmt qiskit das gespeicherte Konto (QiskitRuntimeService.save_account). Achtung: Je nach Tarif kostet
    die Rechenzeit Geld. Gibt die Daten als Dict zurück und druckt sie als eine JSON-Zeile (zum Kopieren oben).
    """
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token) if token else QiskitRuntimeService()
    names = [b.name for b in service.backends(simulator=False, operational=True)]
    print("Verfügbare Geräte:", ", ".join(names))
    backend = (service.backend(backend_name) if backend_name in names
               else service.least_busy(simulator=False, operational=True))
    circs = circuits()
    first = generate_preset_pass_manager(optimization_level=1, backend=backend).run(circs["bell_ZZ"])
    qubits = [int(q) for q in first.layout.final_index_layout()[:2]]
    pm = generate_preset_pass_manager(optimization_level=1, backend=backend, initial_layout=qubits)
    isa = [pm.run(c) for c in circs.values()]
    job = SamplerV2(mode=backend).run(isa, shots=shots)
    print(f"Job {job.job_id()} an {backend.name}, physikalische Qubits {qubits}; warte auf das Ergebnis …")
    res = job.result()
    data = {"backend": backend.name, "date": str(date.today()), "job_id": job.job_id(), "qubits": qubits,
            "shots": shots, "counts": {name: r.data.c.get_counts() for name, r in zip(circs, res)}}
    print(json.dumps(data))
    return data
