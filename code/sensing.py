"""Compressed Sensing für reconstruction.ipynb: dünnbesetzte Signale aus zu wenigen linearen Messungen.

Gesucht ist x mit n Einträgen, gemessen wird y = A x mit m < n Zeilen. Das Modul erzeugt Testprobleme, löst sie mit
kleinster ℓ2-Norm (Pseudoinverse), mit kleinster ℓ1-Norm (Basis Pursuit als lineares Programm, scipy/HiGHS) und mit
FISTA (ℓ1-regularisierte kleinste Quadrate für große Operatoren, z. B. Fourier-Messungen), und misst den
Phasenübergang: ab wie vielen Messungen die Rekonstruktion exakt wird. Keine Downloads.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog


def problem(n, k, m, seed=0):
    """Zufällige Messmatrix A (m × n, Gauß, Spalten etwa Länge 1), k-dünnbesetztes x, Messungen y = A x."""
    rng = np.random.default_rng(seed)
    A = rng.normal(size=(m, n)) / np.sqrt(m)
    x = np.zeros(n)
    x[rng.choice(n, k, replace=False)] = rng.choice([-1, 1], k) * rng.uniform(0.5, 1.5, k)
    return A, x, A @ x


def min_norm(A, y):
    """Lösung mit kleinster ℓ2-Norm, x = A⁺ y: erfüllt alle Messungen, verteilt die Energie auf alle Einträge."""
    return np.linalg.pinv(A) @ y


def basis_pursuit(A, y):
    """Lösung mit kleinster ℓ1-Norm unter A x = y, als lineares Programm mit x = u − v, u, v ≥ 0."""
    m, n = A.shape
    res = linprog(np.ones(2 * n), A_eq=np.hstack([A, -A]), b_eq=y, bounds=(0, None), method="highs")
    if res.status != 0:
        return np.full(n, np.nan)
    return res.x[:n] - res.x[n:]


def fista(forward, adjoint, y, shape, lam, n_iter=300, positive=True, seed=0):
    """Minimiert ½‖A x − y‖² + λ‖x‖₁ (mit x ≥ 0, wenn positive) für einen Operator A (forward, adjoint).

    Schrittweite 1/L mit L = ‖A‖² aus einer Potenzmethode. Gibt x und den Verlauf des Residuums ‖A x − y‖ zurück.
    """
    rng = np.random.default_rng(seed)
    v = rng.normal(size=shape)
    for _ in range(30):                                   # Potenzmethode für den größten Eigenwert von AᵀA
        v = adjoint(forward(v))
        L = np.linalg.norm(v)
        v /= L
    x = z = np.zeros(shape)
    t = 1.0
    verlauf = []
    for _ in range(n_iter):
        r = forward(z) - y
        g = z - adjoint(r) / L
        x_neu = np.maximum(g - lam / L, 0) if positive else np.sign(g) * np.maximum(np.abs(g) - lam / L, 0)
        t_neu = (1 + np.sqrt(1 + 4 * t * t)) / 2
        z = x_neu + (t - 1) / t_neu * (x_neu - x)
        x, t = x_neu, t_neu
        verlauf.append(np.linalg.norm(r))
    return x, np.array(verlauf)


def rel_error(x_hat, x):
    return np.linalg.norm(x_hat - x) / np.linalg.norm(x)


def phase_transition(n, ks, ms, trials=20, tol=1e-4, seed=0):
    """Anteil exakter Rekonstruktionen (relativer Fehler < tol) mit Basis Pursuit, je k (Zeilen) und m (Spalten).

    Gibt die Anteile und je k die Schwelle m₅₀ zurück, ab der die Hälfte der Versuche gelingt (linear interpoliert).
    """
    rate = np.zeros((len(ks), len(ms)))
    for i, k in enumerate(ks):
        for j, m in enumerate(ms):
            ok = 0
            for t in range(trials):
                A, x, y = problem(n, k, m, seed=seed + 1000 * t + 7 * m + k)
                ok += rel_error(basis_pursuit(A, y), x) < tol
            rate[i, j] = ok / trials
    m50 = [float(np.interp(0.5, r, ms)) for r in rate]
    for k, m in zip(ks, m50):
        print(f"k = {k:2d}: Hälfte exakt ab m ≈ {m:.0f} Messungen = {m / k:.1f} · k  (ln(n/k) = {np.log(n / k):.1f})")
    return rate, m50


def plot_recovery(x, estimates, title):
    """Links die Geometrie in 2D (eine Messung, zwei Unbekannte), rechts wahres Signal und Rekonstruktionen als Stäbe."""
    fig = plt.figure(figsize=(14, 5.6))
    gs = fig.add_gridspec(len(estimates) + 1, 2, width_ratios=[1, 2.6])
    ax = fig.add_subplot(gs[:, 0])
    a, y = np.array([0.4, 1.0]), 1.0                                # Messung 0.4·x₁ + x₂ = 1
    x2 = a * y / (a @ a)                                            # Lösung mit kleinster ℓ2-Norm
    t = np.linspace(-1.5, 2.5, 2)
    ax.plot(t, (y - a[0] * t) / a[1], color="black", lw=1.5, label="alle Lösungen von 0.4·x₁ + x₂ = 1")
    phi = np.linspace(0, 2 * np.pi, 200)
    ax.plot(np.linalg.norm(x2) * np.cos(phi), np.linalg.norm(x2) * np.sin(phi), color="tab:blue", label="kleinste ℓ2-Kugel")
    ax.plot([1, 0, -1, 0, 1], [0, 1, 0, -1, 0], color="tab:red", label="kleinste ℓ1-Kugel")
    ax.plot(*x2, "o", color="tab:blue", ms=8)
    ax.plot(0, 1, "o", color="tab:red", ms=8)
    ax.annotate(f"ℓ2: ({x2[0]:.2f}, {x2[1]:.2f})", x2, xytext=(12, -16), textcoords="offset points", color="tab:blue")
    ax.annotate("ℓ1: (0, 1)", (0, 1), xytext=(-62, 10), textcoords="offset points", color="tab:red")
    ax.axhline(0, color="grey", lw=0.5)
    ax.axvline(0, color="grey", lw=0.5)
    ax.set_xlim(-1.4, 1.6)
    ax.set_ylim(-1.4, 1.6)
    ax.set_aspect("equal")
    ax.set_xlabel("x₁")
    ax.set_ylabel("x₂")
    ax.set_title("Zwei Unbekannte, eine Messung", fontsize=10)
    ax.legend(fontsize=8, loc="lower left")
    reihen = [("wahres Signal", x, "black")] + [(name, e, c) for (name, e), c in zip(estimates.items(), ["tab:blue", "tab:red", "tab:green"])]
    for i, (name, e, c) in enumerate(reihen):
        ax = fig.add_subplot(gs[i, 1])
        ax.vlines(np.arange(len(e)), 0, e, color=c, lw=1.2)
        ax.plot(np.flatnonzero(x), x[x != 0], "o", mfc="none", mec="black", ms=6)
        ax.axhline(0, color="grey", lw=0.5)
        ax.set_ylim(-1.7, 1.7)
        fehler = "" if e is x else f"   (relativer Fehler {rel_error(e, x):.1%})"
        ax.set_title(name + fehler, fontsize=10, loc="left")
        ax.set_ylabel("Wert")
        if i < len(reihen) - 1:
            ax.set_xticklabels([])
    ax.set_xlabel("Index i des Eintrags x_i (Kreise: wahre Einträge ungleich null)")
    fig.suptitle(title, fontsize=11)
    fig.tight_layout()
    plt.show()


def plot_transition(n, ks, ms, rate, m50):
    """Erfolgsquote gegen die Zahl der Messungen, je Dünnbesetztheit k; gestrichelt die Untergrenze m = k."""
    fig, ax = plt.subplots(figsize=(10, 4.5))
    for k, r, m, c in zip(ks, rate, m50, plt.cm.viridis(np.linspace(0.1, 0.8, len(ks)))):
        ax.plot(ms, r, "o-", ms=4, color=c, label=f"k = {k}: Schwelle bei m ≈ {m:.0f}")
        ax.axvline(k, color=c, ls="--", lw=1)
    ax.axhline(0.5, color="grey", lw=0.5)
    ax.set_xlabel("Zahl der Messungen m")
    ax.set_ylabel("Anteil exakter Rekonstruktionen")
    ax.set_title(f"Basis Pursuit, n = {n} Unbekannte; gestrichelt m = k (weniger Messungen als Werte reichen nie)",
                 fontsize=10)
    ax.legend(fontsize=9, loc="lower right")
    fig.tight_layout()
    plt.show()
