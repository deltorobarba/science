"""Die verborgene Symmetrie der Kepler-Bahn für symmetries.ipynb: Laplace-Runge-Lenz-Vektor und Periheldrehung.

Im Kraftgesetz 1/r² ist neben dem Drehimpuls (Drehsymmetrie, Noether) auch der Laplace-Runge-Lenz-Vektor erhalten; er
zeigt zum Perihel, und deshalb schließen sich die Bahnen. Diese zusätzliche, verborgene Symmetrie (die Gruppe SO(4))
bricht jede Abweichung vom 1/r²-Gesetz. Die allgemeine Relativitätstheorie fügt in erster Ordnung einen Term 3h²/(c² r⁴)
hinzu (h = Drehimpuls pro Masse); das Perihel dreht sich dann je Umlauf um 6πGM/(c² a (1 − e²)). Numerisch integriert mit
scipy (DOP853), in Einheiten GM = a = 1; dazu die Zahlen für Merkur. Keine Downloads.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

GM_SUN = 1.32712440018e20       # m³/s²
C = 299792458.0
AU = 1.495978707e11
MERCURY = dict(a=0.387098 * AU, e=0.205630, period_days=87.9691)


def orbit(e=0.2056, alpha=0.0, orbits=10, rtol=1e-12):
    """Bahn mit Kraft −r̂/r² (1 + alpha/r²), Start im Perihel; GM = a = 1. Gibt Zeit, Ort, Geschwindigkeit zurück."""
    rp = 1 - e
    vp = np.sqrt((1 + e) / (1 - e))                          # Geschwindigkeit im Perihel (GM = a = 1)
    def f(t, y):
        x, yy, vx, vy = y
        r2 = x * x + yy * yy
        r = np.sqrt(r2)
        k = (1 + alpha / r2) / (r2 * r)
        return [vx, vy, -k * x, -k * yy]
    def perihelion(t, y):                                    # Radialgeschwindigkeit wechselt von − nach +
        return y[0] * y[2] + y[1] * y[3]
    perihelion.direction = 1
    T = 2 * np.pi * orbits * (1 + 2 * alpha)                  # etwas länger, damit alle Durchgänge drin sind
    sol = solve_ivp(f, (0, T), [rp, 0, 0, vp], method="DOP853", rtol=rtol, atol=1e-14, events=perihelion,
                    t_eval=np.linspace(0, T, 2000 * orbits))
    peri = np.unwrap(np.arctan2(sol.y_events[0][:, 1], sol.y_events[0][:, 0]))
    return sol.t, sol.y[:2].T, sol.y[2:].T, peri


def runge_lenz_angle(pos, vel):
    """Richtung des Laplace-Runge-Lenz-Vektors A = v × L − r̂ (pro Masse, GM = 1) in der Bahnebene."""
    L = pos[:, 0] * vel[:, 1] - pos[:, 1] * vel[:, 0]
    r = np.linalg.norm(pos, axis=1)
    Ax = vel[:, 1] * L - pos[:, 0] / r
    Ay = -vel[:, 0] * L - pos[:, 1] / r
    return np.unwrap(np.arctan2(Ay, Ax)), np.hypot(Ax, Ay), L


def precession(e, alpha, orbits=10):
    """Drehung des Perihels je Umlauf aus den exakten Perihel-Durchgängen (Steigung der Winkel)."""
    peri = orbit(e, alpha, orbits)[3]
    return float(np.polyfit(np.arange(1, len(peri) + 1), peri, 1)[0])


def plot_precession(e=0.2056, alpha=0.01, orbits=10):
    """Newton (geschlossen) gegen Kraft mit Zusatzterm (Rosette); Drehung des Perihels je Umlauf gegen die Formel."""
    t0, p0, v0, peri0 = orbit(e, 0.0, orbits)
    t1, p1, v1, peri1 = orbit(e, alpha, orbits)
    ang0, A0, L0 = runge_lenz_angle(p0, v0)
    ang1, A1, L1 = runge_lenz_angle(p1, v1)
    per_orbit = precession(e, alpha, orbits)
    theory = 2 * np.pi * alpha / (1 - e ** 2) ** 2           # 6π GM/(c² a(1−e²)) mit alpha = 3h²/c², h² = a(1 − e²)
    print(f"Newton (1/r²), {orbits} Umläufe: Richtung des Runge-Lenz-Vektors ändert sich um {np.ptp(ang0):.1e} rad, "
          f"Betrag um {np.ptp(A0):.1e}, Drehimpuls um {np.ptp(L0):.1e}")
    print(f"Mit Zusatzterm alpha = {alpha}: Perihel dreht sich je Umlauf um {per_orbit:.5f} rad, "
          f"Formel 2π·alpha/(1 − e²)² = {theory:.5f} rad; Drehimpuls bleibt erhalten (Änderung {np.ptp(L1):.1e})")
    for al in [alpha / 10, alpha / 100]:
        print(f"  alpha = {al:g}: {precession(e, al, orbits):.3e} rad je Umlauf, Formel {2 * np.pi * al / (1 - e ** 2) ** 2:.3e} "
              f"(Verhältnis {precession(e, al, orbits) / (2 * np.pi * al / (1 - e ** 2) ** 2):.4f})")
    a, ecc = MERCURY["a"], MERCURY["e"]
    dphi = 6 * np.pi * GM_SUN / (C ** 2 * a * (1 - ecc ** 2))
    n_century = 36525 / MERCURY["period_days"]
    arcsec = np.rad2deg(dphi * n_century) * 3600
    print(f"Merkur: {dphi:.3e} rad je Umlauf, {n_century:.1f} Umläufe je Jahrhundert → {arcsec:.2f}″ pro Jahrhundert "
          "(beobachtet nach Abzug der anderen Planeten: etwa 43″)")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), gridspec_kw={"width_ratios": [1, 1.3]})
    axes[0].plot(p0[:, 0], p0[:, 1], color="tab:blue", lw=1.5, label="Newton: dieselbe Ellipse bei jedem Umlauf")
    axes[0].plot(p1[:, 0], p1[:, 1], color="tab:red", lw=0.7, alpha=0.8, label=f"mit Zusatzterm (alpha = {alpha})")
    axes[0].plot(0, 0, "*", color="orange", ms=14)
    axes[0].set_aspect("equal")
    axes[0].set_xlabel("x [a]")
    axes[0].set_ylabel("y [a]")
    axes[0].set_title("Bahn: geschlossen oder Rosette", fontsize=10)
    axes[0].legend(fontsize=8, loc="lower left")
    n0 = t0 / (2 * np.pi)
    k = np.arange(1, len(peri1) + 1)
    axes[1].plot(np.arange(1, len(peri0) + 1), peri0 - peri0[0], "o-", color="tab:blue", label="Newton: Perihel fest")
    axes[1].plot(k, peri1 - peri1[0] + per_orbit, "o-", color="tab:red", label="mit Zusatzterm: Perihel wandert")
    axes[1].plot(k, theory * k, color="black", ls=":", label="Formel: 6πGM/(c²a(1 − e²)) je Umlauf")
    axes[1].set_xlabel("Perihel-Durchgang")
    axes[1].set_ylabel("Richtung des Perihels [rad]")
    axes[1].set_title("Die verborgene Symmetrie bricht: das Perihel wandert", fontsize=10)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()
