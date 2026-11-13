"""Ausfrieren der Neutronen für stability.ipynb: wann das frühe Universum aufhört, seinen Anfang zu vergessen.

Neutronen und Protonen wandeln sich durch schwache Reaktionen ineinander um (n + νₑ ↔ p + e⁻, n + e⁺ ↔ p + ν̄ₑ, n ↔ p + e⁻ + ν̄ₑ).
Eine Abweichung vom Gleichgewicht klingt mit der Rate Γ = λ_np + λ_pn ab, solange Γ größer ist als die Expansionsrate H;
danach friert der Neutronenanteil ein und sinkt nur noch durch den Zerfall. Raten in Born-Näherung (Phasenraum-Integrale,
normiert auf die Lebensdauer des Neutrons), Hintergrund mit Elektronen und Positronen und dem Aufheizen der Photonen bei
ihrer Zerstrahlung. Helium entsteht, sobald Deuterium nicht mehr sofort zerfällt: grob nach der Saha-Gleichung, genauer
in einer vollständigen Rechnung mit allen Kernreaktionen (Raten von PRIMAT, Born-Näherung), in der die Hälfte des Heliums
bei T = 0.072 MeV entsteht (Y_p = 0.2425). Vergleich: PRIMAT (Pitrou und andere 2021) Y_p = 0.2472,
Beobachtung (Aver und andere 2021) Y_p = 0.2453 ± 0.0034; Planck 2018: ω_b = 0.02237.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate, optimize

ME, Q = 0.51099895, 1.29333236                     # Elektronenmasse, m_n − m_p [MeV]
MPL, HBAR = 1.220890e22, 6.582119569e-22           # Planck-Masse [MeV], ħ [MeV s]
TAU_N = 878.4                                      # Lebensdauer des Neutrons [s] (PDG 2023)
B_D, M_N = 2.224566, 938.92                        # Bindungsenergie des Deuterons, Nukleonmasse [MeV]
YP_OBS, YP_PRIMAT = (0.2453, 0.0034), 0.2472
ETA = 6.1e-10                                      # Baryonen je Photon aus ω_b = 0.02237 (Planck 2018)
T_HELIUM = 0.072                                   # Hälfte des Heliums im vollständigen Netzwerk [MeV]


def _trapz(y, x):
    return integrate.trapezoid(y, x)


def eplus(T):
    """Energiedichte und Druck der Elektronen und Positronen bei der Temperatur T [MeV]."""
    p = np.linspace(0, 30, 3001)[1:] * T
    E = np.sqrt(p ** 2 + ME ** 2)
    f = 1 / (np.exp(np.minimum(E / T, 700)) + 1)
    return 4 / (2 * np.pi ** 2) * _trapz(p ** 2 * E * f, p), 4 / (2 * np.pi ** 2) * _trapz(p ** 4 / (3 * E) * f, p)


def weak(T, Tnu):
    """Phasenraum-Integrale für n → p und p → n bei Photonentemperatur T und Neutrinotemperatur Tnu."""
    E = np.linspace(ME, ME + 60 * max(T, Tnu) + 5, 20001)[1:]
    w = np.sqrt(E ** 2 - ME ** 2) * E
    fe = lambda e: 1 / (np.exp(np.clip(e / T, -700, 700)) + 1)
    fn = lambda e: 1 / (np.exp(np.clip(e / Tnu, -700, 700)) + 1)
    hi, lo = E > Q, E < Q
    n2p = (np.where(hi, w * (E - Q) ** 2 * (1 - fe(E)) * fn(E - Q), 0) + w * (E + Q) ** 2 * fe(E) * (1 - fn(E + Q))
           + np.where(lo, w * (Q - E) ** 2 * (1 - fe(E)) * (1 - fn(Q - E)), 0))
    p2n = (np.where(hi, w * (E - Q) ** 2 * fe(E) * (1 - fn(E - Q)), 0) + w * (E + Q) ** 2 * (1 - fe(E)) * fn(E + Q)
           + np.where(lo, w * (Q - E) ** 2 * fe(E) * fn(Q - E), 0))
    return _trapz(n2p, E), _trapz(p2n, E)


def background(n=600):
    """Temperaturen, Hubble-Rate, Zeit und schwache Raten von T_ν = 30 MeV bis 0.01 MeV."""
    E = np.linspace(ME, Q, 20001)
    i_vac = _trapz(np.sqrt(E ** 2 - ME ** 2) * E * (Q - E) ** 2, E)          # Zerfall im Vakuum, ergibt 1/τ_n
    Tnu = np.geomspace(30.0, 1e-2, n)
    s_hi = 2 * np.pi ** 2 / 45 * 5.5                                          # Entropie von γ und e± je T_ν³ (vorher)
    s_tot = lambda T: 4 * np.pi ** 2 / 45 * T ** 3 + sum(eplus(T)) / T
    T = np.array([optimize.brentq(lambda x: s_tot(x) - s_hi * tn ** 3, tn * 0.99, tn * 1.5) for tn in Tnu])
    rho = np.pi ** 2 / 15 * T ** 4 + np.array([eplus(x)[0] for x in T]) + 3 * 7 / 8 * np.pi ** 2 / 15 * Tnu ** 4
    H = np.sqrt(8 * np.pi * rho / 3) / MPL / HBAR                             # [1/s]
    t = integrate.cumulative_trapezoid(1 / H, -np.log(Tnu), initial=0) + 1 / (2 * H[0])
    W = np.array([weak(a, b) for a, b in zip(T, Tnu)]) / i_vac / TAU_N        # [1/s]
    return dict(T=T, Tnu=Tnu, H=H, t=t, lam_np=W[:, 0], lam_pn=W[:, 1])


def neutrons(bg):
    """Neutronenanteil X_n(t) aus dX/dt = λ_pn (1 − X) − λ_np X, Start im Gleichgewicht."""
    lt = np.log(bg["t"])
    lnp = lambda x: np.interp(x, lt, bg["lam_np"])
    lpn = lambda x: np.interp(x, lt, bg["lam_pn"])
    X0 = bg["lam_pn"][0] / (bg["lam_np"][0] + bg["lam_pn"][0])
    sol = integrate.solve_ivp(lambda x, X: np.exp(x) * (lpn(x) * (1 - X) - lnp(x) * X), (lt[0], lt[-1]), [X0],
                              t_eval=lt, method="LSODA", rtol=1e-8, atol=1e-12)
    return sol.y[0]


def t_nucleosynthesis(T_grid):
    """Temperatur, bei der Deuterium nach Saha nicht mehr sofort zerfällt: X_d/(X_n X_p) = 1."""
    f = lambda T: (np.log(0.75 * 2 * 1.2020569 / np.pi ** 2 * (4 * np.pi) ** 1.5 * ETA)
                   + 1.5 * np.log(T / M_N) + B_D / T)
    return optimize.brentq(f, 0.03, 0.2)


def plot_freezeout():
    """Links die Raten gegen die Expansion, rechts der Neutronenanteil mit dem Gleichgewicht."""
    bg = background()
    X = neutrons(bg)
    T, t = bg["T"], bg["t"]
    gamma = bg["lam_np"] + bg["lam_pn"]
    i_f = int(np.argmax(gamma < bg["H"]))
    T_saha = t_nucleosynthesis(T)
    i_s = int(np.argmin(np.abs(T - T_saha)))
    i_n = int(np.argmin(np.abs(T - T_HELIUM)))
    Xeq = 1 / (1 + np.exp(Q / T))
    at = lambda arr, Tq: np.interp(np.log(Tq), np.log(T[::-1]), arr[::-1])     # auf die Temperatur interpoliert
    Yp = 2 * at(X, T_HELIUM)
    print(f"Ausfrieren (Γ = λ_np + λ_pn fällt unter H): T = {T[i_f]:.2f} MeV, t = {t[i_f]:.2f} s; "
          f"Neutronenanteil {X[i_f]:.3f}, im Gleichgewicht wären es {Xeq[i_f]:.3f}")
    for Tq in (3.0, 1.0, 0.5):
        k = int(np.argmin(np.abs(T - Tq)))
        print(f"  T = {T[k]:.2f} MeV: Γ/H = {gamma[k] / bg['H'][k]:8.2f}, X_n = {X[k]:.3f}, Gleichgewicht {Xeq[k]:.3f}")
    print(f"Helium entsteht (fast alle Neutronen enden in Helium-4, also Y_p = 2 X_n):")
    print(f"  grob nach Saha (X_d = X_n X_p) bei T = {T_saha:.3f} MeV, t = {at(t, T_saha):.0f} s: X_n = {at(X, T_saha):.3f}, "
          f"Y_p = {2 * at(X, T_saha):.3f}")
    print(f"  wie im vollständigen Netzwerk bei T = {T_HELIUM} MeV, t = {at(t, T_HELIUM):.0f} s: X_n = {Yp / 2:.4f}, Y_p = {Yp:.3f}")
    print(f"  zum Vergleich: PRIMAT {YP_PRIMAT}, Beobachtung {YP_OBS[0]} ± {YP_OBS[1]}; ohne Ausfrieren (immer im "
          f"Gleichgewicht) wären es {2 * Xeq[i_n]:.0e}")
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    ax = axes[0]
    ax.loglog(T, gamma, color="tab:blue", lw=2, label="Umwandlungsrate Γ = λ_np + λ_pn")
    ax.loglog(T, bg["H"], color="black", lw=2, ls="--", label="Expansionsrate H")
    ax.axhline(1 / TAU_N, color="grey", ls=":", label="Zerfall im Vakuum 1/τ_n")
    ax.axvline(T[i_f], color="tab:red", lw=1)
    ax.text(T[i_f] * 0.93, 1e2, f"Ausfrieren\n{T[i_f]:.2f} MeV", color="tab:red", fontsize=9, ha="right")
    ax.set_xlim(10, 0.03)
    ax.set_ylim(1e-4, 1e4)
    ax.set_xlabel("Temperatur kT [MeV]")
    ax.set_ylabel("Rate [1/s]")
    ax.set_title("Solange Γ > H, klingt jede Abweichung ab; danach bleibt sie", fontsize=10)
    ax.legend(fontsize=8, loc="lower left")
    ax = axes[1]
    ax.semilogx(T, Xeq, color="grey", ls="--", label="Gleichgewicht 1/(1 + e^(Q/T))")
    ax.semilogx(T, X, color="tab:blue", lw=2, label="Neutronenanteil X_n")
    ax.axvline(T[i_f], color="tab:red", lw=1, label="Ausfrieren")
    ax.axvline(T_HELIUM, color="tab:green", lw=1, label=f"Helium entsteht ({T_HELIUM} MeV, {at(t, T_HELIUM):.0f} s)")
    ax.plot(T_HELIUM, Yp / 2, "o", color="tab:green")
    ax.set_xlim(10, 0.03)
    ax.set_ylim(0, 0.5)
    ax.set_xlabel("Temperatur kT [MeV]")
    ax.set_ylabel("Anteil der Neutronen")
    ax.set_title(f"Das Gedächtnis der ersten Sekunde: Y_p = {Yp:.3f} (beobachtet {YP_OBS[0]})", fontsize=10)
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    plt.show()
    return Yp
