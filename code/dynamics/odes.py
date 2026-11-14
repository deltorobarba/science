"""Differentialgleichungen: exakte Lösungen, lineare Systeme, Integratoren und Energie, steife Gleichungen, Eigenwertprobleme, Wärmeleitung, Wellengleichung und CFL, Schrödinger-Gleichung und Floquet-Theorie.

Für dynamics.ipynb aus differentialequations.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, exact_solutions, linear_systems, integrators, stiff, eigenvalue_problem, heat, wave_cfl, schroedinger, floquet.
"""
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.linalg import expm, eigh_tridiagonal
from IPython.display import display


def load():
    """6. Daten (Zellen 4 von differentialequations.ipynb)."""
    global integrate_oscillator, rk4
    # Alles hier (numpy, scipy, sympy, matplotlib) ist in Colab vorinstalliert

    def rk4(f, t, y, h):
        k1 = f(t, y)
        k2 = f(t + h / 2, y + h / 2 * k1)
        k3 = f(t + h / 2, y + h / 2 * k2)
        k4 = f(t + h, y + h * k3)
        return y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)

    def integrate_oscillator(method, h, T):
        """x'' = −x mit x(0) = 1, v(0) = 0; gibt Zeiten, x und Energie zurück."""
        n = int(round(T / h))
        x, v = 1.0, 0.0
        xs, es = [x], [0.5 * (x * x + v * v)]
        for _ in range(n):
            if method == "Euler":
                x, v = x + h * v, v - h * x
            elif method == "symplektischer Euler":
                v = v - h * x
                x = x + h * v
            elif method == "Störmer-Verlet":
                v_half = v - h / 2 * x
                x = x + h * v_half
                v = v_half - h / 2 * x
            elif method == "Runge-Kutta 4":
                x, v = rk4(lambda t, y: np.array([y[1], -y[0]]), 0.0, np.array([x, v]), h)
            xs.append(x)
            es.append(0.5 * (x * x + v * v))
        return np.arange(n + 1) * h, np.array(xs), np.array(es)

    print("Werkzeuge bereit")


def exact_solutions():
    """7. Exakte Lösungen mit sympy (Zellen 6 von differentialequations.ipynb)."""
    global K_, N0, Nf, gam, logi, osc, r_, sol_logi, sol_osc, t, w0, x
    t = sp.symbols("t", positive=True)
    gam, w0, r_, K_, N0 = sp.symbols("gamma omega_0 r K N_0", positive=True)
    x = sp.Function("x")
    Nf = sp.Function("N")

    osc = sp.Eq(x(t).diff(t, 2) + 2 * gam * x(t).diff(t) + w0 ** 2 * x(t), 0)
    sol_osc = sp.dsolve(osc, x(t))
    print("Gedämpfter Oszillator:")
    display(sol_osc)
    print("Aperiodischer Grenzfall γ = ω₀:")
    display(sp.dsolve(osc.subs(gam, w0), x(t)))

    logi = sp.Eq(Nf(t).diff(t), r_ * Nf(t) * (1 - Nf(t) / K_))
    sol_logi = sp.dsolve(logi, Nf(t), ics={Nf(0): N0})
    print("Logistische Gleichung mit N(0) = N₀:")
    display(sp.simplify(sol_logi))
    print("Probe durch Einsetzen (checkodesol):", sp.checkodesol(osc, sol_osc)[0], sp.checkodesol(logi, sol_logi)[0])


def linear_systems():
    """8. Lineare Systeme: Matrixexponential und Phasenporträts (Zellen 9 von differentialequations.ipynb)."""
    global A, U, V, Xg, Yg, ax, axes, cases, err, fig, mu, name
    global num, path, ts, x0
    cases = {"stabiler Knoten": np.array([[-1.0, 0.0], [0.0, -3.0]]),
             "Sattel": np.array([[1.0, 0.0], [0.0, -1.0]]),
             "stabile Spirale": np.array([[-0.3, 1.0], [-1.0, -0.3]]),
             "Zentrum": np.array([[0.0, 1.0], [-1.0, 0.0]])}
    fig, axes = plt.subplots(1, 4, figsize=(18, 4.4))
    Xg, Yg = np.meshgrid(np.linspace(-2, 2, 25), np.linspace(-2, 2, 25))
    for ax, (name, A) in zip(axes, cases.items()):
        U, V = A[0, 0] * Xg + A[0, 1] * Yg, A[1, 0] * Xg + A[1, 1] * Yg
        ax.streamplot(Xg, Yg, U, V, color="lightgrey", density=1.0)
        x0 = np.array([1.5, 1.0])
        ts = np.linspace(0, 6, 200)
        path = np.array([expm(A * s) @ x0 for s in ts])
        ax.plot(*path.T, c="tab:red", lw=2, label="e^{At} x₀")
        num = solve_ivp(lambda s, y: A @ y, [0, 6], x0, t_eval=ts, rtol=1e-10, atol=1e-12)
        err = np.max(np.abs(num.y.T - path))
        mu = np.linalg.eigvals(A)
        ax.set_title(f"{name}\nEigenwerte {np.round(mu, 2)}; Abweichung zu solve_ivp {err:.0e}", fontsize=9)
        ax.set_xlim(-2, 2); ax.set_ylim(-2, 2)
        ax.set_xlabel("x₁"); ax.set_ylabel("x₂")
        ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    plt.show()
    for name, A in cases.items():
        print(f"{name:16s}: Spur τ = {np.trace(A):+.1f}, Determinante Δ = {np.linalg.det(A):+.2f}, τ² − 4Δ = {np.trace(A) ** 2 - 4 * np.linalg.det(A):+.2f}")


def integrators():
    """9. Integratoren: Energie über lange Zeiten und Ordnung der Konvergenz (Zellen 12 von differentialequations.ipynb)."""
    global COLORS, METHODS, axes, c, e_end, errs, es, fig, hs, m, orders, ts
    global xs
    METHODS = ["Euler", "symplektischer Euler", "Störmer-Verlet", "Runge-Kutta 4"]
    COLORS = ["tab:red", "tab:orange", "tab:green", "tab:blue"]
    fig, axes = plt.subplots(1, 2, figsize=(15, 4.8))
    for m, c in zip(METHODS, COLORS):
        ts, xs, es = integrate_oscillator(m, 0.1, 200)
        axes[0].semilogy(ts, np.abs(es / 0.5 - 1) + 1e-16, c=c, lw=1, label=m)
    axes[0].set_xlabel("Zeit t (Einheiten von 1/ω)")
    axes[0].set_ylabel("|E(t)/E(0) − 1|")
    axes[0].set_title("Relativer Energiefehler, h = 0.1")
    axes[0].legend(fontsize=8)

    hs = np.array([0.04, 0.02, 0.01, 0.005, 0.0025])
    orders = {}
    for m, c in zip(METHODS, COLORS):
        errs = [abs(integrate_oscillator(m, h, 10)[1][-1] - np.cos(10)) for h in hs]
        orders[m] = np.polyfit(np.log(hs), np.log(errs), 1)[0]
        axes[1].loglog(hs, errs, "o-", c=c, label=f"{m}: Steigung {orders[m]:.2f}")
    axes[1].set_xlabel("Schrittweite h")
    axes[1].set_ylabel("|x(10) − cos 10|")
    axes[1].set_title("Konvergenzordnung")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()
    for m in METHODS:
        e_end = integrate_oscillator(m, 0.1, 200)[2][-1] / 0.5
        print(f"{m:21s}: Ordnung {orders[m]:.2f};  E(200)/E(0) = {e_end:.4g}")
    print(f"Vorhersage für Euler: (1 + h²)^(T/h) = {(1 + 0.01) ** 2000:.4g}")


def stiff():
    """10. Eine steife Gleichung (Zellen 15 von differentialequations.ipynb)."""
    global LAM, ax, euler_explicit, euler_implicit, f_stiff, fig, h, ls, method, s, ts, tt
    global y, y_exact
    LAM = 1000.0
    f_stiff = lambda t, y: -LAM * (y - np.cos(t))
    y_exact = lambda t: (LAM ** 2 * np.cos(t) + LAM * np.sin(t)) / (LAM ** 2 + 1)      # Lösung nach dem Einschwingen

    def euler_explicit(h, T=1.0):
        ts = np.arange(0, T + h / 2, h); y = np.empty_like(ts); y[0] = 0.0
        for i in range(len(ts) - 1):
            y[i + 1] = y[i] + h * f_stiff(ts[i], y[i])
        return ts, y

    def euler_implicit(h, T=1.0):
        ts = np.arange(0, T + h / 2, h); y = np.empty_like(ts); y[0] = 0.0
        for i in range(len(ts) - 1):                                       # lineare Gleichung, direkt nach y_(n+1) aufgelöst
            y[i + 1] = (y[i] + h * LAM * np.cos(ts[i + 1])) / (1 + h * LAM)
        return ts, y

    fig, ax = plt.subplots(figsize=(10, 4.5))
    for h, ls in [(0.0019, "-"), (0.0021, "--")]:
        ts, y = euler_explicit(h, 0.15)
        ax.plot(ts, y, ls, label=f"explizit, h = {h} ({'stabil' if h < 2 / LAM else 'instabil'})")
    ts, y = euler_implicit(0.02, 1.0)
    ax.plot(ts, y, "o", ms=4, label="implizit, h = 0.02")
    tt = np.linspace(0, 1, 400)
    ax.plot(tt, y_exact(tt), c="black", lw=1, label="Lösung nach dem Einschwingen")
    ax.set_ylim(-0.5, 2)
    ax.set_xlabel("Zeit t")
    ax.set_ylabel("y(t)")
    ax.set_title("Steife Gleichung y' = −1000 (y − cos t)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()

    for method in ["RK45", "Radau"]:
        s = solve_ivp(f_stiff, [0, 10], [0.0], method=method, rtol=1e-6, atol=1e-9)
        print(f"solve_ivp {method:5s}: {s.nfev:6d} Auswertungen der rechten Seite, Fehler am Ende {abs(s.y[0, -1] - y_exact(10)):.1e}")


def eigenvalue_problem():
    """11. Ein Eigenwertproblem: der quantenmechanische Oszillator (Zellen 18 von differentialequations.ipynb)."""
    global E, Em, _, axes, d, dx, dxs, errs, fig, m, n, ns_pts
    global oscillator_levels, psi, slope, xg
    def oscillator_levels(n_points, L=10.0):
        xg = np.linspace(-L, L, n_points)
        dx = xg[1] - xg[0]
        diag = 1 / dx ** 2 + 0.5 * xg ** 2
        off = -0.5 / dx ** 2 * np.ones(n_points - 1)
        E, psi = eigh_tridiagonal(diag, off, select="i", select_range=(0, 5))
        return xg, dx, E, psi

    xg, dx, E, psi = oscillator_levels(2000)
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    axes[0].plot(xg, 0.5 * xg ** 2, c="black", lw=1, label="Potential x²/2")
    for n in range(4):
        axes[0].plot(xg, E[n] + 0.8 * psi[:, n] / np.max(np.abs(psi[:, n])), label=f"n = {n}, E = {E[n]:.5f}")
    axes[0].set_xlim(-5, 5); axes[0].set_ylim(0, 5)
    axes[0].set_xlabel("x (Einheiten von √(ħ/mω))")
    axes[0].set_ylabel("Energie (ħω) und Wellenfunktion")
    axes[0].set_title("Eigenzustände aus finiten Differenzen")
    axes[0].legend(fontsize=8)
    ns_pts = np.array([100, 200, 400, 800, 1600])
    errs, dxs = [], []
    for m in ns_pts:
        _, d, Em, _ = oscillator_levels(m)
        dxs.append(d); errs.append(abs(Em[3] - 3.5))
    slope = np.polyfit(np.log(dxs), np.log(errs), 1)[0]
    axes[1].loglog(dxs, errs, "o-", label=f"Fehler von E₃, Steigung {slope:.2f}")
    axes[1].set_xlabel("Gitterabstand Δx")
    axes[1].set_ylabel("|E₃ − 3.5|")
    axes[1].set_title("Konvergenz")
    axes[1].legend()
    fig.tight_layout()
    plt.show()
    print("Niedrigste Energien:", np.round(E, 5), "(exakt 0.5, 1.5, 2.5, …)")
    print(f"Fehler von E₃ fällt wie Δx^{slope:.2f}")


def heat():
    """12. Wärmeleitung: Fourier-Reihe gegen finite Differenzen (Zellen 21 von differentialequations.ipynb)."""
    global NX, axes, c, dxh, fig, fourier_heat, ftcs, r, t_, u, u0, xf
    global xh
    NX = 51
    xh = np.linspace(0, 1, NX)
    dxh = xh[1] - xh[0]
    u0 = ((xh > 0.25) & (xh < 0.75)).astype(float)

    def fourier_heat(x, t, n_terms=400):
        n = np.arange(1, n_terms + 1)[:, None]
        bn = 2 / (n * np.pi) * (np.cos(n * np.pi * 0.25) - np.cos(n * np.pi * 0.75))   # b_n der Stufe
        return np.sum(bn * np.sin(n * np.pi * x) * np.exp(-(n * np.pi) ** 2 * t), axis=0)

    def ftcs(r, t_end):
        dt = r * dxh ** 2
        u = u0.copy()
        for _ in range(int(round(t_end / dt))):
            u[1:-1] = u[1:-1] + r * (u[2:] - 2 * u[1:-1] + u[:-2])
        return u

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    xf = np.linspace(0, 1, 400)
    for t_, c in zip([0.0, 0.002, 0.01, 0.04], ["black", "tab:blue", "tab:green", "tab:red"]):
        axes[0].plot(xf, fourier_heat(xf, t_) if t_ > 0 else ((xf > 0.25) & (xf < 0.75)).astype(float), c=c, lw=1, label=f"Fourier, t = {t_}")
        if t_ > 0:
            axes[0].plot(xh, ftcs(0.4, t_), "o", ms=3, c=c, label=f"FTCS r = 0.4, t = {t_}")
    axes[0].set_xlabel("Ort x")
    axes[0].set_ylabel("Temperatur u")
    axes[0].set_title("Wärmeleitung einer Stufe")
    axes[0].legend(fontsize=7, ncol=2)
    axes[1].plot(xh, ftcs(0.4, 0.01), "o-", ms=3, label="r = 0.40 (stabil)")
    axes[1].plot(xh, ftcs(0.55, 0.01), "s-", ms=3, label="r = 0.55 (instabil)")
    axes[1].set_ylim(-1.5, 1.5)
    axes[1].set_xlabel("Ort x")
    axes[1].set_ylabel("Temperatur u bei t = 0.01")
    axes[1].set_title("Stabilitätsgrenze r = αΔt/Δx² ≤ 1/2")
    axes[1].legend()
    fig.tight_layout()
    plt.show()
    for r in [0.4, 0.5, 0.55]:
        u = ftcs(r, 0.04)
        print(f"r = {r}: größte Abweichung von der Fourier-Lösung bei t = 0.04: {np.max(np.abs(u - fourier_heat(xh, 0.04))):.1e}")


def wave_cfl():
    """13. Die Wellengleichung und die CFL-Bedingung (Zellen 24 von differentialequations.ipynb)."""
    global C, NXW, axes, c, dxw, fig, leapfrog, pluck, t_, tt_, u, wave_exact
    global xw
    NXW = 201
    xw = np.linspace(0, 1, NXW)
    dxw = xw[1] - xw[0]
    pluck = np.where(xw < 0.3, xw / 0.3, (1 - xw) / 0.7) * 0.1

    def wave_exact(x, t, n_terms=600):
        n = np.arange(1, n_terms + 1)[:, None]
        bn = 0.2 * np.sin(n * np.pi * 0.3) / (0.3 * 0.7 * (n * np.pi) ** 2)       # Fourier-Koeffizienten des Dreiecks
        return np.sum(bn * np.sin(n * np.pi * x) * np.cos(n * np.pi * t), axis=0)

    def leapfrog(C, t_end):
        dt = C * dxw
        steps = int(round(t_end / dt))
        u_prev = pluck.copy()
        u = pluck.copy()
        u[1:-1] = pluck[1:-1] + 0.5 * C ** 2 * (pluck[2:] - 2 * pluck[1:-1] + pluck[:-2])   # erster Schritt, Anfangsgeschwindigkeit 0
        for _ in range(steps - 1):
            u_new = np.zeros_like(u)
            u_new[1:-1] = 2 * u[1:-1] - u_prev[1:-1] + C ** 2 * (u[2:] - 2 * u[1:-1] + u[:-2])
            u_prev, u = u, u_new
        return u, steps * dt

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    for t_, c in zip([0.0, 0.2, 0.5, 0.8], ["black", "tab:blue", "tab:green", "tab:red"]):
        axes[0].plot(xw, wave_exact(xw, t_), c=c, lw=1, label=f"exakt, t = {t_}")
        if t_ > 0:
            u, tt_ = leapfrog(1.0, t_)
            axes[0].plot(xw[::5], u[::5], "o", ms=3, c=c, label=f"Leapfrog C = 1, t = {tt_:.2f}")
    axes[0].set_xlabel("Ort x")
    axes[0].set_ylabel("Auslenkung u")
    axes[0].set_title("Gezupfte Saite: zwei Wellen laufen auseinander")
    axes[0].legend(fontsize=7, ncol=2)
    for C, c in [(1.0, "tab:blue"), (0.9, "tab:green"), (1.02, "tab:red")]:
        u, tt_ = leapfrog(C, 1.0)
        axes[1].plot(xw, u, c=c, label=f"C = {C}, t = {tt_:.3f}")
    axes[1].set_ylim(-0.15, 0.15)
    axes[1].set_xlabel("Ort x")
    axes[1].set_ylabel("Auslenkung u")
    axes[1].set_title("Courant-Zahl C = cΔt/Δx")
    axes[1].legend()
    fig.tight_layout()
    plt.show()
    for C in [1.0, 0.9, 1.02]:
        u, tt_ = leapfrog(C, 1.0)
        print(f"C = {C}: größte Abweichung von der exakten Lösung bei t = {tt_:.3f}: {np.max(np.abs(u - wave_exact(xw, tt_))):.1e}")


def schroedinger():
    """14. Die Schrödinger-Gleichung: Tunneln durch eine Barriere (Zellen 27 von differentialequations.ipynb)."""
    global A_BAR, DT, EE, K0, NXS, P_trans, SIG, T_END, T_avg, T_plane, V, V0
    global X0, axes, c, dens, dxs_, fig, half_V, k, kinetic, kk, norms, psi
    global snapshots, step, t_, t_now, weights, xs_
    NXS, dxs_ = 4096, 0.1
    xs_ = (np.arange(NXS) - NXS // 2) * dxs_            # Gitter so gelegt, dass die Barriere genau 40 Zellen = 4.0 breit ist
    k = 2 * np.pi * np.fft.fftfreq(NXS, d=dxs_)
    V0, A_BAR, SIG, K0, X0 = 0.6, 4.0, 10.0, 1.0, -60.0
    V = np.where((xs_ >= 0) & (xs_ < A_BAR - dxs_ / 2), V0, 0.0)
    psi = np.exp(-(xs_ - X0) ** 2 / (4 * SIG ** 2) + 1j * K0 * xs_)
    psi /= np.sqrt(np.sum(np.abs(psi) ** 2) * dxs_)

    DT, T_END = 0.05, 130.0
    half_V = np.exp(-1j * V * DT / 2)
    kinetic = np.exp(-1j * k ** 2 / 2 * DT)
    snapshots = {}
    norms = []
    for step in range(int(T_END / DT) + 1):
        t_now = step * DT
        if any(abs(t_now - s) < DT / 2 for s in (0, 50, 75, 130)):
            snapshots[round(t_now)] = np.abs(psi) ** 2
        psi = half_V * np.fft.ifft(kinetic * np.fft.fft(half_V * psi))
        norms.append(np.sum(np.abs(psi) ** 2) * dxs_)
    P_trans = np.sum(np.abs(psi[xs_ > A_BAR]) ** 2) * dxs_

    def T_plane(E):
        if abs(E - V0) < 1e-12:                          # Grenzfall E = V0
            return 1 / (1 + V0 * A_BAR ** 2 / 2)
        if E < V0:
            kap = np.sqrt(2 * (V0 - E))
            return 1 / (1 + V0 ** 2 * np.sinh(kap * A_BAR) ** 2 / (4 * E * (V0 - E)))
        kp = np.sqrt(2 * (E - V0))
        return 1 / (1 + V0 ** 2 * np.sin(kp * A_BAR) ** 2 / (4 * E * (E - V0)))

    kk = np.linspace(K0 - 6 / (2 * SIG), K0 + 6 / (2 * SIG), 2001)
    weights = np.exp(-2 * SIG ** 2 * (kk - K0) ** 2)
    T_avg = np.sum(weights * np.array([T_plane(q ** 2 / 2) for q in kk])) / np.sum(weights)

    fig, axes = plt.subplots(1, 2, figsize=(15, 4.8))
    for (t_, dens), c in zip(sorted(snapshots.items()), ["black", "tab:blue", "tab:green", "tab:red"]):
        axes[0].plot(xs_, dens, c=c, lw=1, label=f"t = {t_}")
    axes[0].fill_between(xs_, 0, V / V0 * 0.04, color="grey", alpha=0.3, label="Barriere (Höhe 0.6, maßstabsfrei)")
    axes[0].set_xlim(-120, 120)
    axes[0].set_xlabel("Ort x (ħ = m = 1)")
    axes[0].set_ylabel("|ψ(x, t)|²")
    axes[0].set_title("Wellenpaket an einer Barriere")
    axes[0].legend(fontsize=8)
    EE = np.linspace(0.05, 1.2, 300)
    axes[1].semilogy(EE, [T_plane(e) for e in EE], c="black", label="Transmission einer ebenen Welle")
    axes[1].axvline(V0, color="grey", ls=":", label="Barrierenhöhe")
    axes[1].plot([K0 ** 2 / 2], [P_trans], "o", c="tab:red", ms=8, label=f"Wellenpaket (Split-Step): {P_trans:.4f}")
    axes[1].set_xlabel("Energie E")
    axes[1].set_ylabel("Transmission")
    axes[1].set_title("Tunneln: Paket gegen Formel")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()
    print(f"Transmittierter Anteil (Split-Step): {P_trans:.4f}")
    print(f"Formel bei E = 0.5: {T_plane(0.5):.4f};  über die Impulsverteilung des Pakets gemittelt: {T_avg:.4f}")
    print(f"Norm: größte Abweichung von 1 über {len(norms)} Schritte: {np.max(np.abs(np.array(norms) - 1)):.1e}")


def floquet():
    """15. Floquet-Theorie: die Stabilitätskarte der Mathieu-Gleichung (Zellen 30 von differentialequations.ipynb)."""
    global Aa, Qq, Y, a_flat, a_vals, ax, det, edges, fig, h, i, mathieu_rhs
    global n, n_steps, q_flat, q_vals, row, stable, trace
    a_vals = np.linspace(-2, 12, 281)
    q_vals = np.linspace(0, 8, 161)
    Aa, Qq = np.meshgrid(a_vals, q_vals)
    a_flat, q_flat = Aa.ravel(), Qq.ravel()

    def mathieu_rhs(t, Y):
        x1, v1, x2, v2 = Y
        w2 = a_flat - 2 * q_flat * np.cos(2 * t)
        return np.array([v1, -w2 * x1, v2, -w2 * x2])

    Y = np.array([np.ones_like(a_flat), np.zeros_like(a_flat), np.zeros_like(a_flat), np.ones_like(a_flat)])
    n_steps = 800
    h = np.pi / n_steps
    for i in range(n_steps):
        Y = rk4(mathieu_rhs, i * h, Y, h)
    trace = (Y[0] + Y[3]).reshape(Aa.shape)                 # tr M = x1(π) + v2(π)
    det = (Y[0] * Y[3] - Y[1] * Y[2]).reshape(Aa.shape)     # sollte 1 sein
    stable = np.abs(trace) < 2

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.contourf(Qq, Aa, stable, levels=[-0.5, 0.5, 1.5], colors=["tab:red", "white"], alpha=0.6)
    ax.contour(Qq, Aa, np.abs(trace) - 2, levels=[0], colors="black", linewidths=0.8)
    for n in range(4):
        ax.plot(0, n ** 2, "o", c="black", ms=6)
        ax.annotate(f"a = {n}²", (0, n ** 2), xytext=(6, 4), textcoords="offset points", fontsize=8)
    ax.set_xlabel("Stärke der Modulation q")
    ax.set_ylabel("Parameter a (Quadrat der Eigenfrequenz)")
    ax.set_title("Mathieu-Gleichung: rot = instabil (|tr M| > 2), weiß = stabil")
    fig.tight_layout()
    plt.show()
    print(f"Determinante der Monodromiematrix: {det.min():.10f} bis {det.max():.10f} (Theorie 1)")
    row = ~stable[np.argmin(np.abs(q_vals - 2.0))]                  # instabile a-Werte bei q = 2
    edges = np.flatnonzero(np.diff(np.r_[0, row.astype(int), 0]))
    print("Instabile Bereiche bei q = 2:", ", ".join(f"a ∈ [{a_vals[s]:.2f}, {a_vals[e - 1]:.2f}]" for s, e in zip(edges[::2], edges[1::2])))
