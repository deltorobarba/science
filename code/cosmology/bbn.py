"""Die Nukleosynthese im Urknall mit einem eigenen Reaktionsnetz: Neutronen, Deuterium-Engpass, Schramm-Diagramm, Baryonendichte, Helium und das Lithiumproblem.

Für cosmology.ipynb aus cosmology_bbn.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, temperature_time, neutrons_protons, deuterium_bottleneck, network, code_check, schramm, reaction_errors, baryon_density, rate_sets, helium_neutrinos, lithium, literature.
Downloads und Cache: data/cosmology/ (`cosmodata.py`).
"""
import cosmodata                                      # zuerst: Cache-Ordner für astropy
import time
import urllib.request
from collections import Counter
from math import factorial
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate, interpolate, optimize


def load():
    """86. Daten (Zellen 4, 6 von cosmology_bbn.ipynb)."""
    global ASTRODATA, BBN_DIR, BORN_CORR, C_PHOTO, DB, DH_OBS, G, HBAR, HE3_OBS, I_VAC, KB, LABEL
    global LI_OBS, LX, MASS, MBAR, ME, MPL, MU_MEV, NA, NACRE, NGAM0, NPR, NR
    global NRE, NUC, OMEGA_LIT, P, P0, P1, PITROU_21, PITROU_BORN, PITROU_FULL, PLANCK_NEFF, PLANCK_OB, PRIMAT
    global PRYM, PRYM_TAB, Q, Q_NP, R, R0, R1, REAC, RHO_C_H2, SP, SR, STOICH
    global T0, TAU_BEAM, TAU_BOTTLE, TAU_N, YP_OBS, ZN, _, _BG, _Ev, _I, a, b
    global background, detailed_balance, download, eplus, g, j08, k, load_rates, name, nse, omega_to_eta, r_test
    global run, sym, t_a, t_b, t_c, weak_integrals, x
    ASTRODATA = cosmodata.DATA
    BBN_DIR = ASTRODATA / "bbn"
    PRYM = "https://raw.githubusercontent.com/vallima/PRyMordial/main/"

    # Physik (MeV, s, cm)
    ME, Q_NP = 0.51099895, 1.29333236                  # Elektronenmasse, m_n − m_p [MeV]
    MPL, HBAR, KB = 1.220890e22, 6.582119569e-22, 8.617333262e-11   # Planck-Masse [MeV], ħ [MeV s], k_B [MeV/K]
    T0 = 2.7255 * KB                                   # Photonentemperatur heute [MeV]
    NGAM0 = 2 * 1.2020569 / np.pi**2 * (T0 / (HBAR * 2.99792458e10)) ** 3    # Photonen heute [cm⁻³]
    NA, MU_MEV, C_PHOTO = 6.02214076e23, 931.49410242, 9.8686e9
    MBAR = 1.00602 * 1.66053907e-24                    # mittlere Masse pro Baryon bei Y_p ≈ 0.247 [g]
    RHO_C_H2 = 1.87834e-29                             # kritische Dichte / h² [g/cm³]

    # Messwerte und Vergleichswerte
    TAU_N = (878.4, 0.5)                               # Lebensdauer des Neutrons [s], PDG 2023
    TAU_BOTTLE, TAU_BEAM = (877.75, 0.34), (887.7, 2.3)   # UCNτ (Gonzalez et al. 2021), Strahl (Yue et al. 2013)
    DH_OBS = (2.527e-5, 0.030e-5)                      # Cooke, Pettini & Steidel 2018
    YP_OBS = (0.2453, 0.0034)                          # Aver et al. 2021
    LI_OBS = (1.58e-10, 0.086 * np.log(10))            # Sbordone et al. 2010: A(Li) = 2.199 ± 0.086 (Fehler im ln)
    HE3_OBS = (1.1e-5, 0.2e-5)                         # Bania, Rood & Balser 2002 (Obergrenze für den Urwert)
    PLANCK_OB, PLANCK_NEFF = (0.02237, 0.00015), (2.99, 0.17)    # Planck 2018 (TT,TE,EE+lowE+lensing; N_eff mit BAO)
    # Born-Näherung und vollständige Rechnung von PRIMAT (Pitrou et al. 2018, Tab. V; ω_b = 0.02225, τ_n = 879.5 s, N_ν = 3)
    PITROU_BORN = dict(Yp=0.24262, DH=2.423e-5, He3H=1.069e-5, Li7H=5.635e-10)
    PITROU_FULL = dict(Yp=0.24709, DH=2.459e-5, He3H=1.074e-5, Li7H=5.670e-10)
    PITROU_21 = dict(Yp=0.24721, DH=2.439e-5, He3H=1.039e-5, Li7H=5.464e-10)   # Pitrou et al. 2021, Tab. 2: ω_b = 0.02242, τ_n = 879.4 s
    OMEGA_LIT = {"Cooke et al. 2018 (d(p,γ) theoretisch)": (0.02166, 0.00019), "Cooke et al. 2018 (d(p,γ) gemessen)": (0.02235, 0.00037),
                 "Pitrou et al. 2021 (PRIMAT)": (0.02195, 0.00022), "Schöneberg 2024 (PRyMordial; Vorgabe in cosmology_bao)": (0.02218, 0.00055),
                 "Peakhöhen (cosmology_cmbpeaks)": (0.02294, 0.00069)}

    REAC = [("npdg", ["n", "p"], ["d"]), ("dpHe3g", ["d", "p"], ["He3"]), ("ddHe3n", ["d", "d"], ["He3", "n"]),
            ("ddtp", ["d", "d"], ["t", "p"]), ("tpag", ["t", "p"], ["He4"]), ("tdan", ["t", "d"], ["He4", "n"]),
            ("taLi7g", ["t", "He4"], ["Li7"]), ("He3ntp", ["He3", "n"], ["t", "p"]), ("He3dap", ["He3", "d"], ["He4", "p"]),
            ("He3aBe7g", ["He3", "He4"], ["Be7"]), ("Be7nLi7p", ["Be7", "n"], ["Li7", "p"]), ("Li7paa", ["Li7", "p"], ["He4", "He4"])]
    LABEL = {"npdg": "n(p,γ)d", "dpHe3g": "d(p,γ)³He", "ddHe3n": "d(d,n)³He", "ddtp": "d(d,p)t", "tpag": "t(p,γ)⁴He",
             "tdan": "t(d,n)⁴He", "taLi7g": "t(α,γ)⁷Li", "He3ntp": "³He(n,p)t", "He3dap": "³He(d,p)⁴He",
             "He3aBe7g": "³He(α,γ)⁷Be", "Be7nLi7p": "⁷Be(n,p)⁷Li", "Li7paa": "⁷Li(p,α)⁴He"}
    NR = len(REAC)
    LX = np.linspace(np.log(1e-3), np.log(10.0), 500)  # gemeinsames Gitter in ln T₉


    def download(url, path, timeout=120):
        path = Path(path)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            with urllib.request.urlopen(url, timeout=timeout) as r:
                data = r.read()
            if not data.lstrip()[:1] in (b"#", b"0", b"1", b"2", b"3", b"4", b"5", b"6", b"7", b"8", b"9"):
                raise OSError(f"{path.name}: unerwarteter Inhalt")
            path.write_bytes(data)
        return path


    def load_rates(folder):
        # ln N_A<σv> und ln(Fehlerfaktor) jeder Reaktion auf dem gemeinsamen Gitter
        lr, le = [], []
        for name, _, _ in REAC:
            d = np.loadtxt(download(f"{PRYM}PRyMrates/nuclear/{folder}/{name}.txt", BBN_DIR / folder / f"{name}.txt"))
            lr.append(np.interp(LX, np.log(d[:, 0]), np.log(d[:, 1])))
            le.append(np.interp(LX, np.log(d[:, 0]), np.log(d[:, 2])))
        return np.array(lr), np.array(le)


    PRIMAT = load_rates("key_primat_rates")
    NACRE = load_rates("key_nacreii_rates")
    PRYM_TAB = np.loadtxt(download(PRYM + "PRyM_Yp_DH_cosmoMC_2023.dat", BBN_DIR / "PRyM_Yp_DH_cosmoMC_2023.dat"))

    j08 = np.argmin(abs(LX - np.log(0.8)))
    print(f"{NR} Reaktionen in zwei Kompilationen, T₉ = {np.exp(LX[0]):.3f} bis {np.exp(LX[-1]):.0f}; Ergebnistabelle von PRyMordial: {len(PRYM_TAB)} Zeilen "
          f"(ω_b {PRYM_TAB[:, 0].min():.3f} bis {PRYM_TAB[:, 0].max():.3f}, ΔN_eff {PRYM_TAB[:, 2].min():.0f} bis {PRYM_TAB[:, 2].max():.0f})")
    print(f"{'Reaktion':12s} {'PRIMAT':>11s} {'NACRE II':>11s} {'Verhältnis':>10s} {'Fehlerfaktor PRIMAT':>20s}   (bei T₉ = 0.8)")
    for k, (name, _, _) in enumerate(REAC):
        a, b = np.exp(PRIMAT[0][k, j08]), np.exp(NACRE[0][k, j08])
        print(f"{LABEL[name]:12s} {a:11.4g} {b:11.4g} {b / a:10.4f} {np.exp(PRIMAT[1][k, j08]):20.4f}")

    NUC = ["n", "p", "d", "t", "He3", "He4", "Li7", "Be7"]
    MASS = dict(n=1.00866492, p=1.00727647, d=2.01355321, t=3.01550071, He3=3.01493225, He4=4.00150618, Li7=7.01435799, Be7=7.01473482)   # Kernmassen [u]
    G = dict(n=2, p=2, d=3, t=2, He3=2, He4=1, Li7=4, Be7=4)                    # 2J + 1
    ZN = dict(n=(0, 1), p=(1, 0), d=(1, 1), t=(1, 2), He3=(2, 1), He4=(2, 2), Li7=(3, 4), Be7=(4, 3))
    BORN_CORR = dict(Yp=PITROU_FULL["Yp"] - PITROU_BORN["Yp"], DH=PITROU_FULL["DH"] / PITROU_BORN["DH"],
                     He3H=PITROU_FULL["He3H"] / PITROU_BORN["He3H"], Li7H=PITROU_FULL["Li7H"] / PITROU_BORN["Li7H"])
    sym = lambda L: np.prod([factorial(k) for k in Counter(L).values()])      # gleiche Teilchen: 1/(1 + δ)


    def detailed_balance(R, P):
        # Rückreaktion = α T₉^β exp(γ/T₉) × Hinreaktion
        Q = (sum(MASS[x] for x in R) - sum(MASS[x] for x in P)) * MU_MEV
        a = np.prod([G[x] for x in R]) / np.prod([G[x] for x in P]) * (np.prod([MASS[x] for x in R]) / np.prod([MASS[x] for x in P])) ** 1.5
        if len(P) == 1:
            return C_PHOTO * a / sym(R), 1.5, -Q / (KB * 1e9), Q
        return a * sym(P) / sym(R), 0.0, -Q / (KB * 1e9), Q


    DB = np.array([detailed_balance(R, P) for _, R, P in REAC])
    _I = lambda L: [NUC.index(x) for x in L] + [8] * (2 - len(L))             # Index 8: Platzhalter mit dem Wert 1
    R0, R1 = np.array([_I(R) for _, R, _ in REAC]).T
    P0, P1 = np.array([_I(P) for _, _, P in REAC]).T
    NRE, NPR = np.array([len(R) for _, R, _ in REAC]), np.array([len(P) for _, _, P in REAC])
    SR, SP = np.array([sym(R) for _, R, _ in REAC]), np.array([sym(P) for _, _, P in REAC])
    STOICH = np.zeros((8, NR))
    for k, (_, R, P) in enumerate(REAC):
        for x in R: STOICH[NUC.index(x), k] -= 1
        for x in P: STOICH[NUC.index(x), k] += 1


    def eplus(T):
        # Energiedichte und Druck der Elektronen und Positronen (g = 4) bei T [MeV]
        p = np.linspace(0, 30, 3001)[1:] * T
        E = np.sqrt(p**2 + ME**2)
        f = 1 / (np.exp(np.minimum(E / T, 700)) + 1)
        return 4 / (2 * np.pi**2) * np.trapz(p**2 * E * f, p), 4 / (2 * np.pi**2) * np.trapz(p**4 / (3 * E) * f, p)


    def weak_integrals(T, Tnu):
        # Die Integrale für n → p und p → n (ohne den Faktor K)
        E = np.linspace(ME, ME + 60 * max(T, Tnu) + 5, 20001)[1:]
        w = np.sqrt(E**2 - ME**2) * E
        fe = lambda e: 1 / (np.exp(np.clip(e / T, -700, 700)) + 1)
        fn = lambda e: 1 / (np.exp(np.clip(e / Tnu, -700, 700)) + 1)
        hi, lo = E > Q_NP, E < Q_NP
        n2p = (np.where(hi, w * (E - Q_NP)**2 * (1 - fe(E)) * fn(E - Q_NP), 0) + w * (E + Q_NP)**2 * fe(E) * (1 - fn(E + Q_NP))
               + np.where(lo, w * (Q_NP - E)**2 * (1 - fe(E)) * (1 - fn(Q_NP - E)), 0))
        p2n = (np.where(hi, w * (E - Q_NP)**2 * fe(E) * (1 - fn(E - Q_NP)), 0) + w * (E + Q_NP)**2 * (1 - fe(E)) * fn(E + Q_NP)
               + np.where(lo, w * (Q_NP - E)**2 * fe(E) * fn(Q_NP - E), 0))
        return np.trapz(n2p, E), np.trapz(p2n, E)


    _Ev = np.linspace(ME, Q_NP, 20001)
    I_VAC = np.trapz(np.sqrt(_Ev**2 - ME**2) * _Ev * (Q_NP - _Ev)**2, _Ev)    # Zerfall im Vakuum: λ = K I_VAC = 1/τ_n
    _BG = {}


    def background(neff=3.0, n=1500):
        if neff in _BG:
            return _BG[neff]
        Tnu = np.geomspace(30.0, 1e-3, n)
        s_hi = 2 * np.pi**2 / 45 * 5.5                 # Entropie von γ und e± pro T_ν³, solange T = T_ν
        s_tot = lambda T_: 4 * np.pi**2 / 45 * T_**3 + sum(eplus(T_)) / T_
        T = np.array([optimize.brentq(lambda T_: s_tot(T_) - s_hi * tn**3, tn * 0.99, tn * 1.5) for tn in Tnu])
        rho = np.pi**2 / 15 * T**4 + np.array([eplus(x)[0] for x in T]) + neff * 7 / 8 * np.pi**2 / 15 * Tnu**4
        H = np.sqrt(8 * np.pi * rho / 3) / MPL / HBAR                       # [1/s]
        t = integrate.cumulative_trapezoid(1 / H, -np.log(Tnu), initial=0) + 1 / (2 * H[0])
        W = np.array([weak_integrals(a, b) for a, b in zip(T, Tnu)]) / I_VAC   # schwache Raten mal τ_n
        _BG[neff] = dict(Tnu=Tnu, T=T, H=H, t=t, lt=np.log(t), W=W, neff=neff)
        return _BG[neff]


    def omega_to_eta(ob):
        return ob * RHO_C_H2 / MBAR / NGAM0


    def nse(Xn, T, nb):
        # Saha-Gleichgewicht aller Kerne bei T [MeV] und Baryonendichte nb [cm⁻³]
        T9 = T / KB / 1e9
        nq = lambda m: NA * C_PHOTO * T9**1.5 * m**1.5
        Y = np.zeros(8)
        Y[0], Y[1] = Xn, 1 - Xn
        for i, A in enumerate(NUC[2:], start=2):
            Z, N = ZN[A]
            BA = (Z * MASS["p"] + N * MASS["n"] - MASS[A]) * MU_MEV
            Y[i] = G[A] * nq(MASS[A]) / nb * (Y[1] * nb / (G["p"] * nq(MASS["p"]))) ** Z * (Y[0] * nb / (G["n"] * nq(MASS["n"]))) ** N * np.exp(min(BA / T, 700))
        return np.maximum(Y, 1e-300)


    def run(omega_b, rates=PRIMAT, neff=3.0, tau_n=TAU_N[0], fac=None, full=False, T_start=3.0, T_end=0.01 * KB * 1e9):
        bg = background(neff)
        eta = omega_to_eta(omega_b)
        Tnu0 = (4 / 11) ** (1 / 3) * T0
        LR = rates[0] + (np.log(fac) if fac is not None else 0.0)
        lt, lT, lTn = bg["lt"], np.log(bg["T"]), np.log(bg["Tnu"])
        lnp, lpn = np.log(bg["W"][:, 0] / tau_n), np.log(np.maximum(bg["W"][:, 1], 1e-300) / tau_n)
        rows = np.arange(NR)

        def coeffs(x):                                 # x = ln t
            T = np.exp(np.interp(x, lt, lT))
            T9 = T / KB / 1e9
            u = (np.log(min(max(T9, 1.0001e-3), 9.999)) - LX[0]) / (LX[1] - LX[0])
            j = int(u)
            f = np.exp(LR[:, j] * (1 - (u - j)) + LR[:, j + 1] * (u - j))   # über T₉ = 10 bleibt die Hinrate fest
            rho = eta * NGAM0 * (np.exp(np.interp(x, lt, lTn)) / Tnu0) ** 3 / NA    # n_b / N_A [mol/cm³]
            F = rho ** (NRE - 1) * f / SR
            B = rho ** (NPR - 1) * f * DB[:, 0] * T9 ** DB[:, 1] * np.exp(np.maximum(DB[:, 2] / T9, -700)) / SP
            return np.exp(np.interp(x, lt, lnp)), np.exp(np.interp(x, lt, lpn)), F, B

        def rhs(x, Y):
            l1, l2, F, B = coeffs(x)
            Ye = np.append(Y, 1.0)
            dY = STOICH @ (F * Ye[R0] * Ye[R1] - B * Ye[P0] * Ye[P1])
            w = l1 * Y[0] - l2 * Y[1]
            dY[0] -= w
            dY[1] += w
            return np.exp(x) * dY

        def jac(x, Y):
            l1, l2, F, B = coeffs(x)
            Ye = np.append(Y, 1.0)
            D = np.zeros((NR, 9))
            np.add.at(D, (rows, R0), F * Ye[R1]); np.add.at(D, (rows, R1), F * Ye[R0])
            np.add.at(D, (rows, P0), -B * Ye[P1]); np.add.at(D, (rows, P1), -B * Ye[P0])
            J = STOICH @ D[:, :8]
            J[0, 0] -= l1; J[0, 1] += l2; J[1, 0] += l1; J[1, 1] -= l2
            return np.exp(x) * J

        x_of_T = lambda Tq: np.interp(np.log(Tq), lT[::-1], lt[::-1])
        x0, x1 = x_of_T(T_start), x_of_T(T_end)
        l1, l2, _, _ = coeffs(x0)
        Y0 = nse(l2 / (l1 + l2), T_start, eta * NGAM0 * (np.exp(np.interp(x0, lt, lTn)) / Tnu0) ** 3)
        sol = integrate.solve_ivp(rhs, (x0, x1), Y0, method="Radau", jac=jac, rtol=1e-6, atol=1e-28, dense_output=full)
        if not sol.success:
            raise RuntimeError(sol.message)
        Y = sol.y[:, -1]
        born = dict(Yp=4 * Y[5], DH=Y[2] / Y[1], He3H=(Y[3] + Y[4]) / Y[1], Li7H=(Y[6] + Y[7]) / Y[1])   # t → ³He, ⁷Be → ⁷Li
        out = dict(Yp=born["Yp"] + BORN_CORR["Yp"], **{k: born[k] * BORN_CORR[k] for k in ("DH", "He3H", "Li7H")})
        return dict(**out, born=born, eta=eta, Y=Y, sol=sol if full else None, bg=bg)


    t_a = time.time(); background(3.0); t_b = time.time(); r_test = run(PLANCK_OB[0]); t_c = time.time()
    print(f"Hintergrund {t_b - t_a:.1f} s, ein Lauf {t_c - t_b:.2f} s; η₁₀ = {1e10 * omega_to_eta(1.0):.2f} ω_b")
    print(f"{'Reaktion':12s} {'Q [MeV]':>8s} {'α':>11s} {'β':>4s} {'γ':>9s}   (Rückreaktion aus dem detaillierten Gleichgewicht)")
    for (name, _, _), (a, b, g, Q) in zip(REAC, DB):
        print(f"{LABEL[name]:12s} {Q:8.3f} {a:11.4g} {b:4.1f} {g:9.3f}")


def temperature_time():
    """87. Temperatur und Zeit in den ersten Minuten (Zellen 8 von cosmology_bbn.ipynb)."""
    global BG, Tq, ax, ax2, fig, i, lab, t_of_T, tt
    BG = background(3.0)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.6))
    ax.loglog(BG["t"], BG["T"], color="C3", lw=2, label="Photonen $T$")
    ax.loglog(BG["t"], BG["Tnu"], color="C0", lw=2, ls="--", label=r"Neutrinos $T_\nu$")
    tt = np.geomspace(BG["t"][0], BG["t"][-1], 200)
    ax.loglog(tt, np.sqrt(0.738 / tt), color="0.5", ls=":", label=r"reine Strahlung, $g_* = 10.75$: $t = 0.74$ s (MeV/$T$)²")
    ax.loglog(tt, np.sqrt(1.32 / tt), color="k", ls=":", label=r"reine Strahlung, $g_* = 3.36$: $t = 1.32$ s (MeV/$T$)²")
    for Tq, lab in [(0.7, "Neutronen frieren aus"), (0.07, "Helium entsteht")]:
        ax.axhline(Tq, color="0.7", lw=0.8)
        ax.text(2e-3, Tq * 1.1, lab, fontsize=9)
    ax.set_xlim(BG["t"][0], 1e5)
    ax.set_ylim(5e-3, 30)
    ax.set_xlabel("Zeit $t$ [s]")
    ax.set_ylabel("Temperatur $kT$ [MeV]")
    ax.set_title("Temperatur und Zeit nach dem Urknall", fontsize=10)
    ax.legend(fontsize=9)
    ax2.semilogx(BG["T"], BG["Tnu"] / BG["T"], color="C0", lw=2)
    ax2.axhline((4 / 11) ** (1 / 3), color="k", ls="--", label=r"$(4/11)^{1/3} = 0.7138$")
    ax2.axvline(ME, color="0.6", ls=":", label=r"$m_e$ = 0.511 MeV")
    ax2.set_xlim(20, 5e-3)
    ax2.set_xlabel("Photonentemperatur $kT$ [MeV]")
    ax2.set_ylabel(r"$T_\nu / T$")
    ax2.set_title("Die Zerstrahlung von Elektronen und Positronen heizt nur die Photonen", fontsize=10)
    ax2.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    t_of_T = lambda Tq: np.exp(np.interp(np.log(Tq), np.log(BG["T"][::-1]), BG["lt"][::-1]))
    for Tq in [1.0, 0.5, 0.1, 0.07, 0.01]:
        i = np.argmin(abs(BG["T"] - Tq))
        print(f"T = {Tq:5.2f} MeV ({Tq / KB / 1e9:6.2f}·10⁹ K): t = {t_of_T(Tq):8.1f} s, T_ν/T = {BG['Tnu'][i] / BG['T'][i]:.4f}")
    print(f"am Ende T/T_ν = {BG['T'][-1] / BG['Tnu'][-1]:.5f}, erwartet (11/4)^(1/3) = {(11 / 4) ** (1 / 3):.5f}; "
          f"einfache Formel bei 0.1 MeV: {1.32 / 0.1**2:.0f} s")


def neutrons_protons():
    """88. Neutronen und Protonen (Zellen 11 von cosmology_bbn.ipynb)."""
    global MAIN, TS, T_F, T_HE, Tq, XN_ALL, XN_F, XN_FREE, YS, ax, ax2, fig
    global i_f, lam_np, lam_pn, late, tS, t_F, xs
    MAIN = run(PLANCK_OB[0], full=True)
    xs = np.linspace(MAIN["sol"].t[0], MAIN["sol"].t[-1], 6000)
    YS = MAIN["sol"].sol(xs)
    TS = np.exp(np.interp(xs, BG["lt"], np.log(BG["T"])))
    tS = np.exp(xs)
    XN_FREE = YS[0]
    XN_ALL = YS[0] + YS[2] + 2 * YS[3] + YS[4] + 2 * YS[5] + 4 * YS[6] + 3 * YS[7]   # alle Neutronen, frei und gebunden
    lam_np, lam_pn = BG["W"][:, 0] / TAU_N[0], BG["W"][:, 1] / TAU_N[0]
    i_f = np.argmax(lam_np + lam_pn < BG["H"])
    T_F, t_F = BG["T"][i_f], BG["t"][i_f]
    XN_F = np.interp(np.log(t_F), xs, XN_ALL)

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.6))
    ax.loglog(BG["T"], lam_np, color="C0", lw=2, label=r"$\lambda_{n\to p}$")
    ax.loglog(BG["T"], lam_pn, color="C3", lw=2, label=r"$\lambda_{p\to n}$")
    ax.loglog(BG["T"], BG["H"], color="k", lw=2, ls="--", label="Hubble-Rate $H$")
    ax.axhline(1 / TAU_N[0], color="0.5", ls=":", label=r"Zerfall im Vakuum $1/\tau_n$")
    ax.axvline(T_F, color="0.6", lw=1)
    ax.text(T_F * 0.95, 1e2, f" Ausfrieren\n {T_F:.2f} MeV", fontsize=9)
    ax.set_xlim(10, 0.02)
    ax.set_ylim(1e-5, 1e4)
    ax.set_xlabel("Photonentemperatur $kT$ [MeV]")
    ax.set_ylabel("Rate [1/s]")
    ax.set_title("Schwache Reaktionen gegen die Expansion", fontsize=10)
    ax.legend(fontsize=9)
    ax2.semilogx(TS, 1 / (1 + np.exp(np.minimum(Q_NP / TS, 700))), color="0.5", ls="--", label=r"Gleichgewicht $1/(1+e^{Q/T})$")
    ax2.semilogx(TS, XN_ALL, color="C0", lw=2, label="Netzwerk: alle Neutronen")
    ax2.semilogx(TS, XN_FREE, color="C0", lw=1, ls=":", label="Netzwerk: freie Neutronen")
    late = tS > t_F
    ax2.semilogx(TS[late], XN_F * np.exp(-(tS[late] - t_F) / TAU_N[0]), color="C2", ls="-.", label="nur Zerfall nach dem Ausfrieren")
    ax2.set_xlim(3, 0.02)
    ax2.set_ylim(0, 0.45)
    ax2.set_xlabel("Photonentemperatur $kT$ [MeV]")
    ax2.set_ylabel("Anteil der Neutronen $X_n$")
    ax2.set_title("Wie viele Neutronen bleiben übrig?", fontsize=10)
    ax2.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    T_HE = TS[np.argmax(4 * YS[5] > 0.5 * 4 * YS[5][-1])]
    print(f"Ausfrieren (λ_np + λ_pn = H): T = {T_F:.3f} MeV, t = {t_F:.2f} s; X_n = {XN_F:.4f}, im Gleichgewicht wären es {1 / (1 + np.exp(Q_NP / T_F)):.4f}")
    for Tq in [1.0, 0.3, 0.1, T_HE]:
        print(f"T = {Tq:.3f} MeV: t = {t_of_T(Tq):6.1f} s, X_n = {np.interp(np.log(Tq), np.log(TS[::-1]), XN_ALL[::-1]):.4f}")
    print(f"Zerfall allein vom Ausfrieren bis zur Hälfte des Heliums: X_n = {XN_F * np.exp(-(t_of_T(T_HE) - t_F) / TAU_N[0]):.4f}; "
          f"2 X_n = {2 * np.interp(np.log(T_HE), np.log(TS[::-1]), XN_ALL[::-1]):.4f}, Y_p (Born) = {MAIN['born']['Yp']:.4f}")


def deuterium_bottleneck():
    """89. Der Engpass beim Deuterium (Zellen 14 von cosmology_bbn.ipynb)."""
    global TNU0, TNU_T, TT, T_D, XN_T, ax, col, eta, f, fig, i_max, nb
    global xn_eq, yd
    TNU0 = (4 / 11) ** (1 / 3) * T0
    TT = np.geomspace(0.5, 0.03, 300)
    XN_T = np.interp(np.log(TT), np.log(TS[::-1]), XN_FREE[::-1])
    TNU_T = np.exp(np.interp(np.log(TT), np.log(BG["T"][::-1]), np.log(BG["Tnu"][::-1])))
    fig, ax = plt.subplots(figsize=(12, 6))
    T_D = {}
    for f, col in [(0.1, "C2"), (1.0, "C0"), (10.0, "C3")]:
        eta = f * MAIN["eta"]
        nb = eta * NGAM0 * (TNU_T / TNU0) ** 3
        xn_eq = np.interp(np.log(TT), np.log(TS[::-1]), XN_ALL[::-1])          # Neutronen, als wären sie noch alle frei
        yd = np.array([nse(x, T, n)[2] for x, T, n in zip(xn_eq, TT, nb)])
        T_D[f] = TT[np.argmax(yd > 1e-3 * xn_eq)]
        ax.loglog(TT, 2 * yd, color=col, ls="--", label=f"Saha, η = {f:g} × Planck: Deuterium ab {T_D[f]:.3f} MeV")
    ax.loglog(TS, 2 * YS[2], color="k", lw=2, label="Netzwerk (Planck): Deuterium")
    ax.loglog(TS, 4 * YS[5], color="C1", lw=2, label="Netzwerk (Planck): Helium-4")
    ax.set_xlim(0.5, 0.03)
    ax.set_xticks([0.5, 0.3, 0.2, 0.1, 0.07, 0.05, 0.03])
    ax.set_xticklabels(["0.5", "0.3", "0.2", "0.1", "0.07", "0.05", "0.03"])
    ax.set_ylim(1e-12, 1)
    ax.set_xlabel("Photonentemperatur $kT$ [MeV]")
    ax.set_ylabel("Massenanteil")
    ax.set_title("Deuterium im Gleichgewicht mit den Photonen und im Netzwerk", fontsize=10)
    ax.legend(fontsize=9)
    plt.show()

    i_max = np.argmax(YS[2])
    print(f"Netzwerk: Deuterium am häufigsten bei T = {TS[i_max]:.4f} MeV (t = {tS[i_max]:.0f} s), Massenanteil {2 * YS[2][i_max]:.2e}; "
          f"die Hälfte des Heliums steht bei T = {T_HE:.4f} MeV (t = {t_of_T(T_HE):.0f} s)")
    print(f"B_d/T dort: {2.2246 / T_HE:.1f}; ln(1/η) = {np.log(1 / MAIN['eta']):.1f}")
    for f in T_D:
        print(f"η = {f:4g} × Planck: Saha-Deuterium erreicht 10⁻³ der Neutronen bei T = {T_D[f]:.4f} MeV (t = {t_of_T(T_D[f]):.0f} s)")


def network():
    """90. Das Netzwerk: die ersten zwanzig Minuten (Zellen 17 von cosmology_bbn.ipynb)."""
    global A, NAMES, a, ax, b, c, fig, i, j, lab, top
    fig, ax = plt.subplots(figsize=(13, 6.5))
    A = [1, 1, 2, 3, 3, 4, 7, 7]
    NAMES = ["n", "p", "d", "t", "³He", "⁴He", "⁷Li", "⁷Be"]
    for i, (a, lab) in enumerate(zip(A, NAMES)):
        ax.loglog(tS, np.maximum(a * YS[i], 1e-30), lw=2, color=f"C{i}", label=lab)
    ax.set_xlim(1, tS[-1])
    ax.set_ylim(1e-14, 2)
    ax.set_xlabel("Zeit $t$ [s]")
    ax.set_ylabel("Massenanteil $X_i$")
    ax.set_title(f"Die Entstehung der leichten Kerne (ω_b = {PLANCK_OB[0]})", fontsize=10)
    ax.legend(fontsize=9, ncol=2, loc="lower left")
    top = ax.secondary_xaxis("top", functions=(lambda t: np.interp(np.log(np.maximum(t, 1e-3)), BG["lt"], BG["T"]),
                                                lambda T: np.exp(np.interp(-np.log(np.maximum(T, 1e-6)), -np.log(BG["T"]), BG["lt"]))))
    top.set_xticks([1.0, 0.3, 0.1, 0.05, 0.03, 0.01])
    top.set_xticklabels(["1", "0.3", "0.1", "0.05", "0.03", "0.01"])
    top.set_xlabel("Photonentemperatur $kT$ [MeV]")
    plt.show()

    for i in [2, 3, 4, 6, 7]:
        lab = NAMES[i]
        j = np.argmax(YS[i])
        print(f"{lab:4s}: höchster Massenanteil {A[i] * YS[i][j]:.2e} bei t = {tS[j]:6.0f} s, am Ende {A[i] * YS[i][-1]:.2e}")
    b, c = MAIN["born"], MAIN
    print(f"Born:       Y_p = {b['Yp']:.5f}, D/H = {b['DH']:.4e}, ³He/H = {b['He3H']:.4e}, ⁷Li/H = {b['Li7H']:.3e}")
    print(f"korrigiert: Y_p = {c['Yp']:.5f}, D/H = {c['DH']:.4e}, ³He/H = {c['He3H']:.4e}, ⁷Li/H = {c['Li7H']:.3e}; "
          f"⁷Li stammt zu {YS[7][-1] / (YS[6][-1] + YS[7][-1]):.0%} aus ⁷Be")
    print("PRIMAT (Pitrou et al. 2021, ω_b = 0.02242, τ_n = 879.4 s): Y_p = 0.24721, D/H = 2.439e-05, ³He/H = 1.039e-05, ⁷Li/H = 5.464e-10")


def code_check():
    """91. Prüfung gegen einen vollständigen Code (Zellen 20 von cosmology_bbn.ipynb)."""
    global OB_V, VAL, a, ax, ax2, col, d1, d2, dn, f, fig, fmt
    global k, lab, m, ob, r, r_21, r_born, v
    r_born = run(0.02225, neff=3.0, tau_n=879.5)["born"]
    r_21 = run(0.02242, tau_n=879.4)
    print(f"{'':6s} {'eigen Born':>11s} {'Pitrou 2018 Born':>17s} {'Abw.':>8s} | {'eigen korr.':>11s} {'Pitrou 2021':>12s} {'Abw.':>8s}")
    for k, f in [("Yp", 1), ("DH", 1e5), ("He3H", 1e5), ("Li7H", 1e10)]:
        d1 = r_born[k] - PITROU_BORN[k] if k == "Yp" else r_born[k] / PITROU_BORN[k] - 1
        d2 = r_21[k] - PITROU_21[k] if k == "Yp" else r_21[k] / PITROU_21[k] - 1
        fmt = (lambda d: f"{d:+8.5f}") if k == "Yp" else (lambda d: f"{100 * d:+7.2f}%")
        print(f"{k:6s} {f * r_born[k]:11.5f} {f * PITROU_BORN[k]:17.5f} {fmt(d1)} | {f * r_21[k]:11.5f} {f * PITROU_21[k]:12.5f} {fmt(d2)}")

    OB_V = [0.020, 0.021, 0.022, 0.023, 0.024]
    VAL = {}
    for dn in [-1.0, 0.0, 1.0]:
        for ob in OB_V:
            m = np.isclose(PRYM_TAB[:, 0], ob) & np.isclose(PRYM_TAB[:, 2], dn)
            r = run(ob, rates=NACRE, neff=3.0 + dn)
            VAL[(dn, ob)] = (r["Yp"] - PRYM_TAB[m][0, 4], r["DH"] / PRYM_TAB[m][0, 6] - 1, PRYM_TAB[m][0, 7] / PRYM_TAB[m][0, 6])
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.4))
    for dn, col in [(-1.0, "C0"), (0.0, "k"), (1.0, "C3")]:
        ax.plot(OB_V, [VAL[(dn, o)][0] for o in OB_V], "o-", color=col, label=f"ΔN_eff = {dn:+.0f}")
        ax2.plot(OB_V, [100 * VAL[(dn, o)][1] for o in OB_V], "o-", color=col, label=f"ΔN_eff = {dn:+.0f}")
    ax.axhspan(-YP_OBS[1], YP_OBS[1], color="C1", alpha=0.15, label="Fehler der Beobachtung (Aver et al.)")
    ax2.axhspan(-100 * DH_OBS[1] / DH_OBS[0], 100 * DH_OBS[1] / DH_OBS[0], color="C1", alpha=0.15, label="Fehler der Beobachtung (Cooke et al.)")
    ax2.axhspan(-100 * np.median([v[2] for v in VAL.values()]), 100 * np.median([v[2] for v in VAL.values()]), color="0.5", alpha=0.2,
                label="Fehler aus den Raten (PRyMordial)")
    for a, lab in [(ax, r"$Y_p$ eigen − PRyMordial"), (ax2, "D/H eigen / PRyMordial − 1 [%]")]:
        a.axhline(0, color="0.5", lw=0.8)
        a.set_xlabel(r"$\omega_b$")
        a.set_ylabel(lab)
        a.legend(fontsize=9)
    ax.set_ylim(-0.004, 0.004)
    ax2.set_ylim(-5, 5)
    ax.set_title("Helium: eigenes Netzwerk mit Korrekturen gegen PRyMordial (NACRE II)", fontsize=10)
    ax2.set_title("Deuterium: eigenes Netzwerk mit Korrekturen gegen PRyMordial (NACRE II)", fontsize=10)
    plt.tight_layout()
    plt.show()
    for dn in [-1.0, 0.0, 1.0]:
        v = np.array([VAL[(dn, o)][:2] for o in OB_V])
        print(f"ΔN_eff = {dn:+.0f}: Y_p {v[:, 0].min():+.5f} bis {v[:, 0].max():+.5f}, D/H {100 * v[:, 1].min():+.2f} % bis {100 * v[:, 1].max():+.2f} %")


def schramm():
    """92. Das Schramm-Diagramm (Zellen 23 von cosmology_bbn.ipynb)."""
    global ETA10, OB_S, SCH, SY, a, axs, cross, eta_pl, fig, k, lab, top
    global v, y
    ETA10 = np.linspace(1, 10, 16)
    OB_S = ETA10 / (1e10 * omega_to_eta(1.0))
    SCH = [run(o) for o in OB_S]
    SY = {k: np.array([s[k] for s in SCH]) for k in ("Yp", "DH", "He3H", "Li7H")}
    fig, axs = plt.subplots(3, 1, figsize=(11, 12), sharex=True, gridspec_kw=dict(height_ratios=[1, 1.3, 1]))
    eta_pl = 1e10 * omega_to_eta(np.array([PLANCK_OB[0] - PLANCK_OB[1], PLANCK_OB[0] + PLANCK_OB[1]]))
    axs[0].plot(ETA10, SY["Yp"], color="C1", lw=2, label=r"$Y_p$ (⁴He)")
    axs[0].axhspan(YP_OBS[0] - YP_OBS[1], YP_OBS[0] + YP_OBS[1], color="C1", alpha=0.25, label="Aver et al. 2021")
    axs[0].set_ylabel(r"$Y_p$")
    axs[1].semilogy(ETA10, SY["DH"], color="C0", lw=2, label="D/H")
    axs[1].axhspan(DH_OBS[0] - DH_OBS[1], DH_OBS[0] + DH_OBS[1], color="C0", alpha=0.35, label="Cooke et al. 2018")
    axs[1].semilogy(ETA10, SY["He3H"], color="C2", lw=2, label="³He/H")
    axs[1].axhspan(HE3_OBS[0] - HE3_OBS[1], HE3_OBS[0] + HE3_OBS[1], color="C2", alpha=0.25, label="Bania et al. 2002 (Obergrenze)")
    axs[1].set_ylabel("Anzahl relativ zu H")
    axs[2].semilogy(ETA10, SY["Li7H"], color="C3", lw=2, label="⁷Li/H")
    axs[2].axhspan(LI_OBS[0] * np.exp(-LI_OBS[1]), LI_OBS[0] * np.exp(LI_OBS[1]), color="C3", alpha=0.25, label="Sbordone et al. 2010 (Spite-Plateau)")
    axs[2].set_ylabel("Anzahl relativ zu H")
    axs[2].set_xlabel(r"$\eta_{10} = 10^{10}\, n_b / n_\gamma$")
    for a in axs:
        a.axvspan(*eta_pl, color="k", alpha=0.25)
        a.legend(fontsize=9, loc="best")
    axs[0].text(eta_pl[1] + 0.1, SY["Yp"].min() + 0.002, "Planck", fontsize=9)
    top = axs[0].secondary_xaxis("top", functions=(lambda e: e / (1e10 * omega_to_eta(1.0)), lambda o: o * 1e10 * omega_to_eta(1.0)))
    top.set_xlabel(r"$\omega_b = \Omega_b h^2$")
    axs[0].set_title("Die leichten Kerne aus dem Urknall gegen die Beobachtung (Raten: PRIMAT)", fontsize=10)
    plt.tight_layout()
    plt.show()

    for k, (v, lab) in {"Yp": (YP_OBS[0], "Y_p"), "DH": (DH_OBS[0], "D/H"), "He3H": (HE3_OBS[0], "³He/H"), "Li7H": (LI_OBS[0], "⁷Li/H")}.items():
        y = SY[k] - v if k == "Yp" else np.log(SY[k] / v)
        cross = [ETA10[i] - y[i] * (ETA10[i + 1] - ETA10[i]) / (y[i + 1] - y[i]) for i in range(len(y) - 1) if y[i] * y[i + 1] < 0]
        print(f"{lab:6s}: Beobachtung getroffen bei η₁₀ = " + (", ".join(f"{c:.2f} (ω_b = {c / (1e10 * omega_to_eta(1.0)):.4f})" for c in cross) or "nirgends")
              + f"; Spanne über η₁₀ = 1 bis 10: {SY[k].min():.3g} bis {SY[k].max():.3g}")
    print(f"Planck: η₁₀ = {1e10 * omega_to_eta(PLANCK_OB[0]):.3f}")


def reaction_errors():
    """93. Welche Reaktionen den Fehler bestimmen (Zellen 26 von cosmology_bbn.ipynb)."""
    global CONTR, MC, NUC_ERR, OB_REF, SENS, _, a, ax, ax2, base, fac, fig
    global k, lab, m, n, name, names, q, r, rng, t, y, z
    OB_REF = PLANCK_OB[0]
    base = MAIN
    CONTR, SENS = {}, {}
    for k, (name, _, _) in enumerate(REAC):
        fac = np.ones((NR, len(LX)))
        fac[k] = np.exp(PRIMAT[1][k])
        r = run(OB_REF, fac=fac)
        CONTR[name] = dict(DH=np.log(r["DH"] / base["DH"]), Li7H=np.log(r["Li7H"] / base["Li7H"]), Yp=r["Yp"] - base["Yp"], He3H=np.log(r["He3H"] / base["He3H"]))
        fac[k] = 1.05
        SENS[name] = np.log(run(OB_REF, fac=fac)["DH"] / base["DH"]) / np.log(1.05)
    r = run(OB_REF, tau_n=TAU_N[0] + TAU_N[1])
    CONTR["τ_n"] = dict(DH=np.log(r["DH"] / base["DH"]), Li7H=np.log(r["Li7H"] / base["Li7H"]), Yp=r["Yp"] - base["Yp"], He3H=np.log(r["He3H"] / base["He3H"]))
    NUC_ERR = {q: np.sqrt(sum(v[q] ** 2 for v in CONTR.values())) for q in ("DH", "Li7H", "Yp", "He3H")}

    rng = np.random.default_rng(7)
    MC = []
    for _ in range(60):
        z = rng.standard_normal(NR)
        m = run(OB_REF, fac=np.exp(z[:, None] * PRIMAT[1]), tau_n=TAU_N[0] + TAU_N[1] * rng.standard_normal())
        MC.append((np.log(m["DH"]), np.log(m["Li7H"]), m["Yp"]))
    MC = np.array(MC)

    names = list(CONTR)
    lab = [LABEL.get(n, n) for n in names]
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.8), sharey=True)
    y = np.arange(len(names))
    ax.barh(y, [100 * CONTR[n]["DH"] for n in names], color="C0")
    ax2.barh(y, [100 * CONTR[n]["Li7H"] for n in names], color="C3")
    ax.set_yticks(y)
    ax.set_yticklabels(lab)
    ax.invert_yaxis()
    for a, q, t in [(ax, "DH", "D/H"), (ax2, "Li7H", "⁷Li/H")]:
        a.axvline(0, color="0.5", lw=0.8)
        a.set_xlabel(f"Änderung von {t} bei +1σ der Rate [%]")
        a.set_title(f"{t}: Fehler aus der Kernphysik {100 * NUC_ERR[q]:.2f} % (linear)", fontsize=10)
    plt.tight_layout()
    plt.show()

    for n in sorted(names, key=lambda n: -abs(CONTR[n]["DH"]))[:5]:
        print(f"{LABEL.get(n, n):12s}: D/H {100 * CONTR[n]['DH']:+.2f} % (1σ)" + (f", Empfindlichkeit {SENS[n]:+.3f}" if n in SENS else ""))
    print(f"Fehler aus der Kernphysik, linear: D/H {100 * NUC_ERR['DH']:.2f} %, ³He/H {100 * NUC_ERR['He3H']:.2f} %, ⁷Li/H {100 * NUC_ERR['Li7H']:.2f} %, "
          f"Y_p {NUC_ERR['Yp']:.5f} (davon τ_n {abs(CONTR['τ_n']['Yp']):.5f})")
    print(f"Monte Carlo (60): D/H {100 * MC[:, 0].std():.2f} %, ⁷Li/H {100 * MC[:, 1].std():.2f} %, Y_p {MC[:, 2].std():.5f}")


def baryon_density():
    """94. Die Baryonendichte aus Deuterium (Zellen 29 von cosmology_bbn.ipynb)."""
    global DH_G, DH_PL, OB_D, OB_G, SIG_D, SIG_NUC, SIG_OBS, SLOPE, ax, ax2, dh, fig
    global gauss, of, og, spl
    OB_G = np.linspace(0.0205, 0.0235, 7)
    DH_G = np.array([run(o)["DH"] for o in OB_G])
    spl = interpolate.CubicSpline(np.log(OB_G), np.log(DH_G))
    SLOPE = spl(np.log(PLANCK_OB[0]), 1)
    OB_D = np.exp(optimize.brentq(lambda x: spl(x) - np.log(DH_OBS[0]), np.log(OB_G[0]), np.log(OB_G[-1])))
    SIG_OBS = OB_D * (DH_OBS[1] / DH_OBS[0]) / abs(SLOPE)
    SIG_NUC = OB_D * NUC_ERR["DH"] / abs(SLOPE)
    SIG_D = np.hypot(SIG_OBS, SIG_NUC)
    DH_PL = np.exp(spl(np.log(PLANCK_OB[0])))

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.6))
    of = np.linspace(OB_G[0], OB_G[-1], 300)
    dh = np.exp(spl(np.log(of)))
    ax.plot(of, 1e5 * dh, color="C0", lw=2, label="eigenes Netzwerk (PRIMAT)")
    ax.fill_between(of, 1e5 * dh * np.exp(-NUC_ERR["DH"]), 1e5 * dh * np.exp(NUC_ERR["DH"]), color="C0", alpha=0.25, label="Fehler aus der Kernphysik")
    ax.plot(OB_G, 1e5 * DH_G, "o", color="C0")
    ax.axhspan(1e5 * (DH_OBS[0] - DH_OBS[1]), 1e5 * (DH_OBS[0] + DH_OBS[1]), color="C1", alpha=0.35, label="Cooke et al. 2018")
    ax.axvspan(PLANCK_OB[0] - PLANCK_OB[1], PLANCK_OB[0] + PLANCK_OB[1], color="k", alpha=0.2, label="Planck 2018")
    ax.axvline(OB_D, color="C1", ls="--")
    ax.set_xlabel(r"$\omega_b$")
    ax.set_ylabel(r"D/H [$10^{-5}$]")
    ax.set_title("Deuterium als Waage für die Baryonen", fontsize=10)
    ax.legend(fontsize=9)
    og = np.linspace(0.0210, 0.0230, 600)
    gauss = lambda m, s: np.exp(-0.5 * ((og - m) / s) ** 2) / (s * np.sqrt(2 * np.pi))
    ax2.plot(og, gauss(OB_D, SIG_OBS), color="C1", ls="--", label=f"nur Messung: {OB_D:.5f} ± {SIG_OBS:.5f}")
    ax2.plot(og, gauss(OB_D, SIG_D), color="C1", lw=2, label=f"Messung + Kernphysik: ± {SIG_D:.5f}")
    ax2.plot(og, gauss(*PLANCK_OB), color="k", lw=2, label=f"Planck 2018: {PLANCK_OB[0]} ± {PLANCK_OB[1]}")
    ax2.set_xlabel(r"$\omega_b$")
    ax2.set_ylabel("Wahrscheinlichkeitsdichte")
    ax2.set_title("Nukleosynthese und Hintergrundstrahlung", fontsize=10)
    ax2.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    print(f"D/H ∝ ω_b^{SLOPE:.3f}; D/H bei ω_b von Planck = {DH_PL:.4e} ({(DH_OBS[0] - DH_PL) / np.hypot(DH_OBS[1], DH_PL * NUC_ERR['DH']):+.1f}σ gegen Cooke et al.)")
    print(f"ω_b aus D/H = {OB_D:.5f} ± {SIG_OBS:.5f} (Messung) ± {SIG_NUC:.5f} (Kernphysik) = {OB_D:.5f} ± {SIG_D:.5f}; η₁₀ = {1e10 * omega_to_eta(OB_D):.3f}")
    print(f"gegen Planck: {(OB_D - PLANCK_OB[0]) / np.hypot(SIG_D, PLANCK_OB[1]):+.1f}σ")


def rate_sets():
    """95. Zwei Sätze von Raten (Zellen 32 von cosmology_bbn.ipynb)."""
    global KEY4, OB_VAR, T9, VARIANTS, ax, ax2, col, fig, i, idx4, k, l
    global labs, mixed, ref, w
    KEY4 = ["npdg", "dpHe3g", "ddHe3n", "ddtp"]
    idx4 = [[n for n, _, _ in REAC].index(k) for k in KEY4]
    ref = run(OB_D)["DH"]
    VARIANTS = {"PRIMAT (alle Raten)": PRIMAT, "NACRE II (alle Raten)": NACRE}
    for k, i in zip(KEY4, idx4):
        mixed = PRIMAT[0].copy()
        mixed[i] = NACRE[0][i]
        VARIANTS[f"PRIMAT, nur {LABEL[k]} aus NACRE II"] = (mixed, PRIMAT[1])
    OB_VAR = {lab: OB_D * (run(OB_D, rates=r)["DH"] / ref) ** (1 / abs(SLOPE)) for lab, r in VARIANTS.items()}

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.6), gridspec_kw=dict(width_ratios=[1, 1.15]))
    T9 = np.exp(LX)
    for k, i, col in zip(KEY4, idx4, ["C0", "C1", "C2", "C3"]):
        ax.semilogx(T9, np.exp(NACRE[0][i] - PRIMAT[0][i]), color=col, lw=2, label=LABEL[k])
    ax.axvspan(0.4, 1.0, color="0.85")
    ax.axhline(1, color="0.5", lw=0.8)
    ax.set_xlim(0.05, 5)
    ax.set_ylim(0.85, 1.15)
    ax.set_xlabel(r"$T_9$")
    ax.set_ylabel("Rate NACRE II / PRIMAT")
    ax.set_title("Wo sich die Kompilationen unterscheiden", fontsize=10)
    ax.legend(fontsize=9)
    labs = list(OB_VAR)
    ax2.errorbar([OB_VAR[l] for l in labs], -np.arange(len(labs)), xerr=SIG_D, fmt="o", color="C0", capsize=4)
    ax2.axvspan(PLANCK_OB[0] - PLANCK_OB[1], PLANCK_OB[0] + PLANCK_OB[1], color="k", alpha=0.2, label="Planck 2018")
    ax2.set_yticks(-np.arange(len(labs)))
    ax2.set_yticklabels(labs, fontsize=9)
    ax2.set_xlabel(r"$\omega_b$ aus D/H (Cooke et al. 2018)")
    ax2.set_title("Wie die Wahl der Raten die Baryonendichte verschiebt", fontsize=10)
    ax2.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    w = (T9 > 0.4) & (T9 < 1.0)
    for k, i in zip(KEY4, idx4):
        print(f"{LABEL[k]:12s}: NACRE II / PRIMAT im Fenster T₉ = 0.4–1.0: {np.exp(NACRE[0][i] - PRIMAT[0][i])[w].mean():.4f}")
    for l in labs:
        print(f"{l:38s}: ω_b = {OB_VAR[l]:.5f} ({(OB_VAR[l] - PLANCK_OB[0]) / np.hypot(SIG_D, PLANCK_OB[1]):+.1f}σ gegen Planck)")


def helium_neutrinos():
    """96. Helium und die Zahl der Neutrinoarten (Zellen 35 von cosmology_bbn.ipynb)."""
    global CHI, DLNDH, DN, DYDN, GD, GY, L, NEFF, OB_DY, OB_N, YP_TAU, ax
    global ax2, dd, dn, dn_f, fig, i, iD, iY, j, lab, lev, m
    global ob, ob_f, pN, pO, r, sD, sY, y
    DN = np.array([-1.0, -0.5, 0.0, 0.5, 1.0])
    OB_N = np.linspace(0.0205, 0.0235, 7)
    GY = np.zeros((len(DN), len(OB_N)))
    GD = np.zeros_like(GY)
    for i, dn in enumerate(DN):
        for j, ob in enumerate(OB_N):
            r = run(ob, neff=3.0 + dn)
            GY[i, j], GD[i, j] = r["Yp"], r["DH"]
    iY = interpolate.RectBivariateSpline(DN, OB_N, GY)
    iD = interpolate.RectBivariateSpline(DN, np.log(OB_N), np.log(GD))
    YP_TAU = {lab: run(OB_D, tau_n=tau[0])["Yp"] for lab, tau in [("Speicher", TAU_BOTTLE), ("Strahl", TAU_BEAM)]}

    dn_f, ob_f = np.linspace(-1, 1, 401), np.linspace(0.0205, 0.0235, 401)
    sY = np.hypot(YP_OBS[1], NUC_ERR["Yp"])
    sD = np.hypot(DH_OBS[1] / DH_OBS[0], NUC_ERR["DH"])
    CHI = ((iY(dn_f, ob_f) - YP_OBS[0]) / sY) ** 2 + ((iD(dn_f, np.log(ob_f)) - np.log(DH_OBS[0])) / sD) ** 2
    L = np.exp(-0.5 * (CHI - CHI.min()))
    pN, pO = L.sum(1) / L.sum(), L.sum(0) / L.sum()
    NEFF = (3.044 + (dn_f * pN).sum(), np.sqrt(((dn_f - (dn_f * pN).sum()) ** 2 * pN).sum()))
    OB_DY = ((ob_f * pO).sum(), np.sqrt(((ob_f - (ob_f * pO).sum()) ** 2 * pO).sum()))
    DYDN = np.polyfit(DN, GY[:, 3], 1)[0]
    DLNDH = np.polyfit(DN, np.log(GD[:, 3]), 1)[0]

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.8))
    dd = np.linspace(-1, 1, 100)
    ax.plot(3.044 + dd, iY(dd, [OB_D])[:, 0], color="C1", lw=2, label=f"eigenes Netzwerk, ω_b = {OB_D:.5f}")
    ax.axhspan(YP_OBS[0] - YP_OBS[1], YP_OBS[0] + YP_OBS[1], color="C1", alpha=0.2, label="Aver et al. 2021")
    for (lab, y), m in zip(YP_TAU.items(), ["v", "^"]):
        ax.plot(3.044, y, m, color="k", ms=9, label=f"τ_n gemessen im {lab}: Y_p = {y:.4f}")
    ax.set_xlabel(r"$N_\mathrm{eff}$")
    ax.set_ylabel(r"$Y_p$")
    ax.set_title("Helium als Uhr der Expansion", fontsize=10)
    ax.legend(fontsize=9)
    lev = [CHI.min() + 2.30, CHI.min() + 6.18]
    ax2.contourf(ob_f, 3.044 + dn_f, CHI, levels=[CHI.min(), lev[0], lev[1]], colors=["C0", "lightsteelblue"], alpha=0.8)
    ax2.contour(ob_f, 3.044 + dn_f, iY(dn_f, ob_f), levels=[YP_OBS[0]], colors="C1", linestyles="--")
    ax2.contour(ob_f, 3.044 + dn_f, iD(dn_f, np.log(ob_f)), levels=[np.log(DH_OBS[0])], colors="C2", linestyles="--")
    ax2.errorbar(*PLANCK_OB[:1], PLANCK_NEFF[0], xerr=PLANCK_OB[1], yerr=PLANCK_NEFF[1], fmt="s", color="k", capsize=4, label="Planck 2018")
    ax2.plot([], [], color="C1", ls="--", label="Y_p = Messung")
    ax2.plot([], [], color="C2", ls="--", label="D/H = Messung")
    ax2.set_xlabel(r"$\omega_b$")
    ax2.set_ylabel(r"$N_\mathrm{eff}$")
    ax2.set_title("Deuterium und Helium zusammen (68 % und 95 %)", fontsize=10)
    ax2.legend(fontsize=9, loc="upper left")
    plt.tight_layout()
    plt.show()

    print(f"bei ω_b = {OB_N[3]}: dY_p/dN_eff = {DYDN:.4f}, d ln(D/H)/dN_eff = {DLNDH:.3f}")
    print(f"τ_n: Speicher {TAU_BOTTLE[0]} s → Y_p = {YP_TAU['Speicher']:.5f}, Strahl {TAU_BEAM[0]} s → Y_p = {YP_TAU['Strahl']:.5f}, Unterschied {YP_TAU['Strahl'] - YP_TAU['Speicher']:.5f}")
    print(f"D/H + Y_p: N_eff = {NEFF[0]:.2f} ± {NEFF[1]:.2f}, ω_b = {OB_DY[0]:.5f} ± {OB_DY[1]:.5f}; χ²_min = {CHI.min():.2f}; "
          f"gegen Planck (N_eff {PLANCK_NEFF[0]} ± {PLANCK_NEFF[1]}): {(NEFF[0] - PLANCK_NEFF[0]) / np.hypot(NEFF[1], PLANCK_NEFF[1]):+.1f}σ")


def lithium():
    """97. Das Lithiumproblem (Zellen 38 von cosmology_bbn.ipynb)."""
    global FACS, LI_D, LI_FAC, ax, ax2, col, f, fac, fig, j08, k, lf
    global lv, name, need, v, vals
    LI_D = run(OB_D)["Li7H"]
    FACS = np.array([0.1, 0.25, 0.5, 1.0, 2.0, 4.0, 10.0])
    LI_FAC = {}
    for name in ["He3aBe7g", "Be7nLi7p"]:
        k = [n for n, _, _ in REAC].index(name)
        vals = []
        for f in FACS:
            fac = np.ones((NR, len(LX)))
            fac[k] = f
            vals.append(run(OB_D, fac=fac)["Li7H"])
        LI_FAC[name] = np.array(vals)

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.6))
    ax.loglog(OB_S, SY["Li7H"], color="C3", lw=2, label="eigenes Netzwerk (PRIMAT)")
    ax.fill_between(OB_S, SY["Li7H"] * np.exp(-NUC_ERR["Li7H"]), SY["Li7H"] * np.exp(NUC_ERR["Li7H"]), color="C3", alpha=0.25)
    ax.axhspan(LI_OBS[0] * np.exp(-LI_OBS[1]), LI_OBS[0] * np.exp(LI_OBS[1]), color="0.5", alpha=0.3, label="Spite-Plateau (Sbordone et al. 2010)")
    ax.axvspan(OB_D - SIG_D, OB_D + SIG_D, color="C0", alpha=0.3, label="ω_b aus Deuterium (Schritt 94)")
    ax.set_xlabel(r"$\omega_b$")
    ax.set_ylabel("⁷Li/H")
    ax.set_title("Lithium: Vorhersage und Sterne", fontsize=10)
    ax.legend(fontsize=9)
    for (name, v), col in zip(LI_FAC.items(), ["C1", "C2"]):
        ax2.loglog(FACS, v, "o-", color=col, lw=2, label=LABEL[name])
    ax2.axhspan(LI_OBS[0] * np.exp(-LI_OBS[1]), LI_OBS[0] * np.exp(LI_OBS[1]), color="0.5", alpha=0.3, label="Spite-Plateau")
    ax2.set_xlabel("Faktor auf die Rate")
    ax2.set_ylabel("⁷Li/H")
    ax2.set_title(f"Was eine falsche Kernrate ausrichten müsste (ω_b = {OB_D:.5f})", fontsize=10)
    ax2.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    print(f"⁷Li/H bei ω_b aus D/H: {LI_D:.3e} ± {100 * NUC_ERR['Li7H']:.1f} % (Kernphysik); Spite-Plateau {LI_OBS[0]:.2e}: "
          f"Faktor {LI_D / LI_OBS[0]:.2f}, {np.log(LI_D / LI_OBS[0]) / np.hypot(LI_OBS[1], NUC_ERR['Li7H']):.1f}σ")
    j08 = np.argmin(abs(LX - np.log(0.5)))
    for name, v in LI_FAC.items():
        lv, lf = np.log(v), np.log(FACS)
        need = np.exp(np.interp(np.log(LI_OBS[0]), lv if lv[0] < lv[-1] else lv[::-1], lf if lv[0] < lv[-1] else lf[::-1], left=np.nan, right=np.nan))
        k = [n for n, _, _ in REAC].index(name)
        print(f"{LABEL[name]:12s}: ⁷Li/H ∝ Rate^{np.polyfit(lf, lv, 1)[0]:+.2f}; nötiger Faktor {need:.2f}, gemessener Fehlerfaktor bei T₉ = 0.5: {np.exp(PRIMAT[1][k, j08]):.3f}")


def literature():
    """98. Gegen die veröffentlichten Werte (Zellen 41 von cosmology_bbn.ipynb)."""
    global H0_BAO, OWN, _, ax, col, e, fig, i, lab, rows, v
    OWN = {"eigen: D/H, PRIMAT": (OB_D, SIG_D), "eigen: D/H, NACRE II": (OB_VAR["NACRE II (alle Raten)"], SIG_D),
           "eigen: D/H + Y_p, N_eff frei": OB_DY}
    rows = [(k, *v, "C0") for k, v in OWN.items()] + [(k, *v, "0.3") for k, v in OMEGA_LIT.items()] + [("Planck 2018", *PLANCK_OB, "k")]
    fig, ax = plt.subplots(figsize=(12, 6.2))
    for i, (lab, v, e, col) in enumerate(rows):
        ax.errorbar(v, -i, xerr=e, fmt="o", color=col, ms=7, capsize=4)
    ax.axvspan(PLANCK_OB[0] - PLANCK_OB[1], PLANCK_OB[0] + PLANCK_OB[1], color="k", alpha=0.15)
    ax.set_yticks(-np.arange(len(rows)))
    ax.set_yticklabels([r[0] for r in rows], fontsize=9.5)
    ax.set_xlabel(r"$\omega_b = \Omega_b h^2$")
    ax.set_title("Die Baryonendichte aus der Nukleosynthese und aus der Hintergrundstrahlung", fontsize=10)
    plt.tight_layout()
    plt.show()

    for lab, v, e, _ in rows[:-1]:
        print(f"{lab:55s}: ω_b = {v:.5f} ± {e:.5f}; gegen Planck {(v - PLANCK_OB[0]) / np.hypot(e, PLANCK_OB[1]):+.1f}σ")
    H0_BAO = 68.53                                       # cosmology_bao: BAO + BBN mit ω_b = 0.02218
    print(f"H₀ aus BAO + BBN mit dem eigenen ω_b statt 0.02218: etwa {H0_BAO * (OB_D / 0.02218) ** (0.128 / 0.493):.2f} statt {H0_BAO} km/s/Mpc")
