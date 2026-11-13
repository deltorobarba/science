"""Optimal steuern für stability.ipynb: eine Raumsonde am instabilen Punkt L2 halten und denselben Regler ohne Modell lernen.

Teil 1: die Bewegung nahe dem Lagrange-Punkt L2 von Sonne und Erde (eingeschränktes Dreikörperproblem, mitrotierendes
System, Bewegung in der Ebene der Erdbahn), linearisiert. Zustand: Abweichung x (von der Sonne weg) und y (in Laufrichtung
der Erde) in 1000 km, Geschwindigkeiten in m/s; Steuerung u: Schub als Beschleunigung in (m/s) je Tag; ein Schritt ist ein
Tag. Der lineare quadratische Regler (LQR) minimiert J = Σ (|r|² + R·|u|²) und findet u = −K·x über die Riccati-Gleichung.
Teil 2: Q-Learning mit Politik-Iteration (Bradtke, Ydstie und Barto 1994). Der Lernende kennt das Modell nicht, er ruft nur
den Simulator auf (Zustand und Schub hinein, nächster Zustand heraus) und sieht die Kosten. Für einen linearen Regler ist die
Q-Funktion quadratisch, Q(x, u) = zᵀHz mit z = (x, u); die Bellman-Gleichung wird für H per kleinste Quadrate gelöst, dann
wird der Regler verbessert, K = H_uu⁻¹·H_ux.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, NullFormatter, ScalarFormatter
from scipy.linalg import expm, solve_discrete_are
from scipy.optimize import brentq

MU = 3.040e-6                       # Masse von Erde und Mond relativ zur Gesamtmasse
AU_KM = 1.495978707e8
YEAR_D = 365.256                    # siderisches Jahr in Tagen
T_D = YEAR_D / (2 * np.pi)          # Zeiteinheit des Dreikörperproblems in Tagen (58.1)
V_MS = AU_KM * 1e3 / (T_D * 86400)  # Geschwindigkeitseinheit in m/s (29.8 km/s)


def l2_model(mu=MU, dt=1.0):
    """Linearisierte Bewegung um L2. Gibt (A in 1/Tag, Ad, Bd für Schritte von dt Tagen, Abstand L2–Erde in km) zurück."""
    f = lambda x: x - (1 - mu) * (x + mu) / abs(x + mu) ** 3 - mu * (x - 1 + mu) / abs(x - 1 + mu) ** 3
    xl = brentq(f, 1 - mu + 1e-6, 1.1)
    r1, r2 = xl + mu, xl - 1 + mu
    uxx = 1 + 2 * (1 - mu) / r1 ** 3 + 2 * mu / r2 ** 3
    uyy = 1 - (1 - mu) / r1 ** 3 - mu / r2 ** 3
    A = np.array([[0, 0, 1, 0], [0, 0, 0, 1], [uxx, 0, 0, 2], [0, uyy, -2, 0]])      # Einheiten: AU, Jahr/2π
    D = np.diag([AU_KM / 1e3, AU_KM / 1e3, V_MS, V_MS])
    A = D @ A @ np.linalg.inv(D) / T_D                                                 # 1000 km, m/s, Tage
    B = np.vstack([np.zeros((2, 2)), np.eye(2)])
    M = expm(np.block([[A, B], [np.zeros((2, 6))]]) * dt)                             # Schub einen Tag lang konstant
    return A, M[:4, :4], M[:4, 4:], r2 * AU_KM


Q_POS = np.diag([1.0, 1.0, 0.0, 0.0])          # nur die Abweichung im Ort kostet


def lqr(Ad, Bd, R, Q=Q_POS):
    """Diskreter LQR: Regler K mit u = −K·x aus der Riccati-Gleichung."""
    P = solve_discrete_are(Ad, Bd, Q, R * np.eye(Bd.shape[1]))
    return np.linalg.solve(R * np.eye(Bd.shape[1]) + Bd.T @ P @ Bd, Bd.T @ P @ Ad)


def simulate(Ad, Bd, K, x0, days=365):
    """Bahn und Schub für u = −K·x; K = None heißt ohne Steuerung."""
    x = np.empty((days + 1, 4))
    u = np.zeros((days, 2))
    x[0] = x0
    for k in range(days):
        if K is not None:
            u[k] = -K @ x[k]
        x[k + 1] = Ad @ x[k] + Bd @ u[k]
    return x, u


def score(Ad, Bd, K, x0, days=365):
    """Über ein Jahr: Treibstoff Δv = Σ|u|·1 Tag [cm/s], mittlere Abweichung [km] und mittlerer Schub [mm/s je Tag].

    „Mittel“ heißt Wurzel aus dem Mittel der Quadrate: So misst der LQR, und nur so liegt kein Regler unter seiner Front.
    """
    x, u = simulate(Ad, Bd, K, x0, days)
    return (100 * np.linalg.norm(u, axis=1).sum(), 1e3 * np.sqrt(np.mean(np.sum(x[:, :2] ** 2, axis=1))),
            1e3 * np.sqrt(np.mean(np.sum(u ** 2, axis=1))))


def hand_controller(kp=0.05, kd=0.3):
    """Ein einfacher Regler von Hand: Feder und Dämpfer in jeder Richtung, u = −kp·r − kd·v."""
    return np.hstack([kp * np.eye(2), kd * np.eye(2)])


def features(z):
    """Quadratische Merkmale z_i·z_j (i ≤ j) für die Q-Funktion zᵀHz."""
    i, j = np.triu_indices(z.shape[-1])
    return z[..., i] * z[..., j] * np.where(i == j, 1.0, 2.0)


def q_learning(step, K0, R, iterations=8, samples=100, noise=0.0, seed=0):
    """Politik-Iteration nur mit Aufrufen des Simulators step(x, u). Gibt die Regler K_0, K_1, … zurück."""
    rng = np.random.default_rng(seed)
    n, m = K0.shape[1], K0.shape[0]
    iu = np.triu_indices(n + m)
    Ks = [K0]
    for _ in range(iterations):
        K = Ks[-1]
        x = rng.normal(scale=[0.1, 0.1, 0.05, 0.05], size=(samples, n))       # Zustände, Größenordnung 100 km und 5 cm/s
        u = rng.normal(scale=0.01, size=(samples, m))                          # erkundender Schub
        x1 = step(x, u) + noise * rng.normal(size=(samples, n))
        cost = np.einsum("ki,ij,kj->k", x, Q_POS, x) + R * np.sum(u ** 2, axis=1)
        z, z1 = np.hstack([x, u]), np.hstack([x1, -x1 @ K.T])
        h = np.linalg.lstsq(features(z) - features(z1), cost, rcond=None)[0]   # Bellman: Q(z) = Kosten + Q(z')
        H = np.zeros((n + m, n + m))
        H[iu] = h
        H = H + H.T - np.diag(np.diag(H))
        Ks.append(np.linalg.solve(H[n:, n:], H[n:, :n]))                       # besserer Regler
    return Ks


def plot_control(Rs=np.geomspace(0.1, 1e4, 26), show=(1e4, 1.0), R_learn=100.0, x0=(0.1, 0.0, 0.0, 0.0), days=365):
    """Links die Abweichung mit und ohne Regler, rechts Schub gegen Abweichung mit dem Pfad des Q-Learnings."""
    Rs = np.asarray(Rs, float)
    x0 = np.asarray(x0, float)
    A, Ad, Bd, dist = l2_model()
    ev = np.linalg.eigvals(A)
    lam, omega = ev.real.max(), np.abs(ev.imag).max()
    print(f"L2 liegt {dist / 1e6:.2f} Mio km hinter der Erde. Eigenwerte der linearisierten Bewegung: ±{lam:.4f} und "
          f"±{omega:.4f}i je Tag")
    print(f"  Ohne Steuerung wächst eine Abweichung alle {1 / lam:.1f} Tage um den Faktor e (verdoppelt sich in "
          f"{np.log(2) / lam:.1f} Tagen); die Schwingung hat die Periode {2 * np.pi / omega:.0f} Tage.")
    d0 = 1e3 * np.linalg.norm(x0[:2])
    print(f"Optimale Regler (LQR) für eine Abweichung von {d0:.0f} km, ein Jahr lang; Raten = Logarithmus der Eigenwerte "
          f"im geschlossenen Kreis je Tag (alle negativ: stabil):")
    for R in show:
        K = lqr(Ad, Bd, R)
        dv, rms, urms = score(Ad, Bd, K, x0, days)
        rates = np.unique(np.round(np.log(np.abs(np.linalg.eigvals(Ad - Bd @ K))), 4))
        print(f"  R = {R:g}: Δv = {dv:.1f} cm/s, mittlere Abweichung {rms:.1f} km, mittlerer Schub {urms:.2f} mm/s je Tag; "
              f"Raten " + ", ".join(f"{r:+.4f}" for r in rates))
    K_hand = hand_controller()
    hand = score(Ad, Bd, K_hand, x0, days)
    print(f"  Regler von Hand: Δv = {hand[0]:.1f} cm/s, mittlere Abweichung {hand[1]:.1f} km, mittlerer Schub {hand[2]:.2f} mm/s je Tag")

    step = lambda x, u: x @ Ad.T + u @ Bd.T            # der Simulator: das Einzige, was der Lernende vom System kennt
    Ks = q_learning(step, K_hand, R_learn)
    K_star = lqr(Ad, Bd, R_learn)
    err = [np.linalg.norm(K - K_star) / np.linalg.norm(K_star) for K in Ks]
    print(f"Q-Learning ohne Modell (R = {R_learn:g}, 100 Übergänge je Iteration), relativer Abstand zum Regler aus der "
          f"Riccati-Gleichung: " + ", ".join(f"{e:.0e}" for e in err))
    front = np.array([score(Ad, Bd, lqr(Ad, Bd, R), x0, days) for R in Rs])
    path = np.array([score(Ad, Bd, K, x0, days) for K in Ks])

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    ax = axes[0]
    t = np.arange(days + 1)
    x, _ = simulate(Ad, Bd, None, x0, days)
    r = 1e3 * np.linalg.norm(x[:, :2], axis=1)
    keep = r < 1e5                                     # darüber gilt die lineare Näherung nicht mehr
    ax.semilogy(t[keep], r[keep], color="black", lw=2, label=f"ohne Steuerung: ×e alle {1 / lam:.0f} Tage")
    for R, c, name in zip(show, ["tab:green", "tab:red"], ["sparsam", "schnell"]):
        x, u = simulate(Ad, Bd, lqr(Ad, Bd, R), x0, days)
        ax.semilogy(t, 1e3 * np.linalg.norm(x[:, :2], axis=1), color=c, lw=1.8,
                    label=f"LQR {name} (R = {R:g}): Δv = {100 * np.linalg.norm(u, axis=1).sum():.1f} cm/s")
    x, u = simulate(Ad, Bd, K_hand, x0, days)
    ax.semilogy(t, 1e3 * np.linalg.norm(x[:, :2], axis=1), color="tab:blue", lw=1.4, ls="--",
                label=f"Regler von Hand: Δv = {100 * np.linalg.norm(u, axis=1).sum():.1f} cm/s")
    ax.set_ylim(1e-2, 1e5)
    ax.set_xlabel("Zeit [Tage]")
    ax.set_ylabel("Abstand von L2 [km]")
    ax.set_title(f"Eine Abweichung von {d0:.0f} km am instabilen Punkt L2", fontsize=10)
    ax.legend(fontsize=8, loc="upper right")
    ax = axes[1]
    ax.loglog(front[:, 2], front[:, 1], "o-", color="black", ms=3, label=f"optimale Regler (LQR, R von {Rs[0]:g} bis {Rs[-1]:g})")
    ax.plot(path[:, 2], path[:, 1], "s-", color="tab:purple", ms=5, label=f"Q-Learning ohne Modell (R = {R_learn:g}), Iteration 0, 1, 2, …")
    ax.plot(hand[2], hand[1], "*", color="tab:blue", ms=14, label="Start: Regler von Hand")
    goal = score(Ad, Bd, K_star, x0, days)
    ax.plot(goal[2], goal[1], "o", mfc="none", mec="tab:purple", ms=14, mew=1.5, label=f"Ziel: LQR mit R = {R_learn:g}")
    for axis in (ax.xaxis, ax.yaxis):                    # Zahlen 1, 2, 3, 5, 10, … statt Zehnerpotenzen
        axis.set_major_locator(LogLocator(subs=(1.0, 2.0, 3.0, 5.0)))
        axis.set_major_formatter(ScalarFormatter())
        axis.set_minor_formatter(NullFormatter())
    ax.set_xlabel("mittlerer Schub [mm/s je Tag]")
    ax.set_ylabel("mittlere Abweichung [km]")
    ax.set_title("Kein Regler liegt unter der Front: weniger Abweichung kostet mehr Schub", fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()
    return K_star, Ks
