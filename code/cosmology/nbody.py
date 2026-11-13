"""Eine eigene N-Körper-Simulation (Particle-Mesh mit numba): Anfangsspektrum, kosmisches Netz, Wachstum, BAO-Peak, Dichte in Kugeln und die Seltenheit der KBC-Leere.

Für cosmology.ipynb aus cosmology_nbody.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, initial_spectrum, cosmic_web, growth_check, bao_in_simulation, sphere_variance, sphere_distribution, kbc_rarity, void_environments, local_h0, literature.
Downloads und Cache: data/cosmology/ (`cosmodata.py`).
"""
import cosmodata                                      # zuerst: Cache-Ordner für astropy
import time
import numpy as np
import matplotlib.pyplot as plt
import scipy.fft as sf
from numba import njit, prange
from scipy import integrate, stats


def load():
    """25. Daten (Zellen 5, 7, 9 von cosmology_nbody.ipynb)."""
    global A, AMP, A_BIG, A_SMALL, BIG, E, HASLBAUER_SIGMA, KBC, KH, LNK, LOCALVOID_SIGMA, PLANCK
    global R_HORIZON, R_KBC, SEED, SMALL, S_EH, T_NW, T_W, WU_HUTERER, _, _g, accel, assign
    global cic_window, d, density, dt, f_growth, fft, gather, growth, ifft, in_spheres, initial_conditions, k_nl
    global kgrid, lab, offsets, plin, power, s, sigma_lin, simulate, t0, t1, t2, transfer_eh
    global window
    PLANCK = dict(h=0.674, Om=0.315, Ob=0.0493, ns=0.965, s8=0.811, Tcmb=2.7255)
    KBC = dict(delta=-0.46, err=0.06, R=300.0)          # Keenan et al. 2013 in der Form von Haslbauer et al. 2020 [Mpc]
    R_KBC = KBC["R"] * PLANCK["h"]                      # 202 Mpc/h
    HASLBAUER_SIGMA = 6.04                              # Spannung der KBC-Leere mit ΛCDM (MXXL), Haslbauer et al. 2020
    LOCALVOID_SIGMA = 7.2                               # lineare Theorie mit Messfehler, cosmology_localvoid
    WU_HUTERER = 0.31 / 73.0                            # σ(H₀,lokal)/H₀ für eine Stichprobe von Supernovae, Wu & Huterer 2017
    R_HORIZON = 14200.0                                 # mitbewegter Radius des beobachtbaren Universums [Mpc]
    SEED = 1


    def transfer_eh(k, p=PLANCK, wiggles=True):
        # Transferfunktion von Eisenstein & Hu (1998); k in h/Mpc. Ohne Wellen: Gl. 29–31 (glatte Form)
        h, om, ob = p["h"], p["Om"] * p["h"] ** 2, p["Ob"] * p["h"] ** 2
        fb, fc, th = p["Ob"] / p["Om"], 1 - p["Ob"] / p["Om"], p["Tcmb"] / 2.7
        kk = k * h                                                                # 1/Mpc
        zeq, keq = 2.50e4 * om * th**-4, 7.46e-2 * om * th**-2
        b1, b2 = 0.313 * om**-0.419 * (1 + 0.607 * om**0.674), 0.238 * om**0.223
        zd = 1291 * om**0.251 / (1 + 0.659 * om**0.828) * (1 + b1 * ob**b2)
        Rb = lambda z: 31.5 * ob * th**-4 * (1000 / z)
        Rd, Req = Rb(zd), Rb(zeq)
        s = 2 / (3 * keq) * np.sqrt(6 / Req) * np.log((np.sqrt(1 + Rd) + np.sqrt(Rd + Req)) / (1 + np.sqrt(Req)))   # Schallhorizont [Mpc]
        if not wiggles:
            a_g = 1 - 0.328 * np.log(431 * om) * fb + 0.38 * np.log(22.3 * om) * fb**2
            g_eff = p["Om"] * h * (a_g + (1 - a_g) / (1 + (0.43 * kk * s) ** 4))
            q = k * th**2 / g_eff
            L0 = np.log(2 * np.e + 1.8 * q)
            return L0 / (L0 + (14.2 + 731 / (1 + 62.5 * q)) * q * q), s
        q = kk / (13.41 * keq)
        ksilk = 1.6 * ob**0.52 * om**0.73 * (1 + (10.4 * om) ** -0.95)
        a1 = (46.9 * om) ** 0.670 * (1 + (32.1 * om) ** -0.532)
        a2 = (12.0 * om) ** 0.424 * (1 + (45.0 * om) ** -0.582)
        alpha_c = a1**-fb * a2 ** (-fb**3)
        bb1, bb2 = 0.944 / (1 + (458 * om) ** -0.708), (0.395 * om) ** -0.0266
        beta_c = 1 / (1 + bb1 * (fc**bb2 - 1))

        def T0(al, be):
            L = np.log(np.e + 1.8 * be * q)
            return L / (L + (14.2 / al + 386 / (1 + 69.9 * q**1.08)) * q * q)

        f = 1 / (1 + (kk * s / 5.4) ** 4)
        Tc = f * T0(1, beta_c) + (1 - f) * T0(alpha_c, beta_c)
        y = (1 + zeq) / (1 + zd)
        Gy = y * (-6 * np.sqrt(1 + y) + (2 + 3 * y) * np.log((np.sqrt(1 + y) + 1) / (np.sqrt(1 + y) - 1)))
        alpha_b = 2.07 * keq * s * (1 + Rd) ** -0.75 * Gy
        beta_b = 0.5 + fb + (3 - 2 * fb) * np.sqrt((17.2 * om) ** 2 + 1)
        s_t = s / (1 + (8.41 * om**0.435 / (kk * s)) ** 3) ** (1 / 3)
        x = kk * s_t
        Tb = (T0(1, 1) / (1 + (kk * s / 5.2) ** 2) + alpha_b / (1 + (beta_b / (kk * s)) ** 3) * np.exp(-((kk / ksilk) ** 1.4))) * np.sin(x) / x
        return fb * Tb + fc * Tc, s


    LNK = np.linspace(np.log(1e-5), np.log(1e3), 20000)
    KH = np.exp(LNK)
    window = lambda x: 3 * (np.sin(x) - x * np.cos(x)) / x**3
    T_W, S_EH = transfer_eh(KH)
    T_NW, _ = transfer_eh(KH, wiggles=False)
    AMP = PLANCK["s8"] ** 2 / np.trapz(KH**3 * KH ** PLANCK["ns"] * T_W**2 * window(8 * KH) ** 2 / (2 * np.pi**2), LNK)


    def plin(k, wiggles=True):
        # lineares Spektrum bei z = 0 [(Mpc/h)³]
        return AMP * np.exp(np.interp(np.log(k), LNK, np.log(KH ** PLANCK["ns"] * (T_W if wiggles else T_NW) ** 2)))


    def sigma_lin(R):
        return np.sqrt(np.trapz(KH**3 * plin(KH) * window(KH * R) ** 2 / (2 * np.pi**2), LNK))


    E = lambda a: np.sqrt(PLANCK["Om"] / a**3 + 1 - PLANCK["Om"])
    _g = lambda a: E(a) * integrate.quad(lambda x: 1 / (x * E(x)) ** 3, 0, a)[0]
    growth = lambda a: _g(a) / _g(1.0)
    f_growth = lambda a, e=1e-4: (np.log(growth(a * (1 + e))) - np.log(growth(a * (1 - e)))) / (2 * e)

    k_nl = np.exp(np.interp(0.0, np.log(KH**3 * plin(KH) / (2 * np.pi**2)), LNK))
    print(f"σ₈ = {sigma_lin(8.0):.3f}; Schallhorizont (Eisenstein & Hu) {S_EH:.1f} Mpc = {S_EH * PLANCK['h']:.1f} Mpc/h; "
          f"Δ² = 1 bei k = {k_nl:.3f} h/Mpc; D(a = 0.02) = {growth(0.02):.4f}, f(z = 0) = {f_growth(1.0):.3f}")
    print(f"σ(R) linear: 8 Mpc/h {sigma_lin(8):.3f}, 30 Mpc/h {sigma_lin(30):.3f}, 100 Mpc/h {sigma_lin(100):.4f}, 300 Mpc = {R_KBC:.0f} Mpc/h {sigma_lin(R_KBC):.4f}")

    @njit(cache=False)
    def assign(pos, Ng, w):
        # CIC: Masse (Gewicht w) jedes Teilchens anteilig auf die 8 nächsten Gitterpunkte
        rho = np.zeros((Ng, Ng, Ng), np.float64)
        for p in range(pos.shape[0]):
            x, y, z = pos[p, 0], pos[p, 1], pos[p, 2]
            i, j, k = int(np.floor(x)), int(np.floor(y)), int(np.floor(z))
            dx, dy, dz = x - i, y - j, z - k
            i0, j0, k0 = i % Ng, j % Ng, k % Ng
            i1, j1, k1 = (i0 + 1) % Ng, (j0 + 1) % Ng, (k0 + 1) % Ng
            m = w[p]
            rho[i0, j0, k0] += m * (1 - dx) * (1 - dy) * (1 - dz)
            rho[i1, j0, k0] += m * dx * (1 - dy) * (1 - dz)
            rho[i0, j1, k0] += m * (1 - dx) * dy * (1 - dz)
            rho[i0, j0, k1] += m * (1 - dx) * (1 - dy) * dz
            rho[i1, j1, k0] += m * dx * dy * (1 - dz)
            rho[i1, j0, k1] += m * dx * (1 - dy) * dz
            rho[i0, j1, k1] += m * (1 - dx) * dy * dz
            rho[i1, j1, k1] += m * dx * dy * dz
        return rho


    @njit(parallel=True, cache=False)
    def gather(gx, gy, gz, pos):
        # CIC rückwärts: Feldwerte an den Orten der Teilchen
        Ng = gx.shape[0]
        out = np.empty((pos.shape[0], 3), np.float32)
        for p in prange(pos.shape[0]):
            x, y, z = pos[p, 0], pos[p, 1], pos[p, 2]
            i, j, k = int(np.floor(x)), int(np.floor(y)), int(np.floor(z))
            dx, dy, dz = x - i, y - j, z - k
            i0, j0, k0 = i % Ng, j % Ng, k % Ng
            i1, j1, k1 = (i0 + 1) % Ng, (j0 + 1) % Ng, (k0 + 1) % Ng
            w = ((1 - dx) * (1 - dy) * (1 - dz), dx * (1 - dy) * (1 - dz), (1 - dx) * dy * (1 - dz), (1 - dx) * (1 - dy) * dz,
                 dx * dy * (1 - dz), dx * (1 - dy) * dz, (1 - dx) * dy * dz, dx * dy * dz)
            for c, g in enumerate((gx, gy, gz)):
                out[p, c] = (w[0] * g[i0, j0, k0] + w[1] * g[i1, j0, k0] + w[2] * g[i0, j1, k0] + w[3] * g[i0, j0, k1]
                             + w[4] * g[i1, j1, k0] + w[5] * g[i1, j0, k1] + w[6] * g[i0, j1, k1] + w[7] * g[i1, j1, k1])
        return out


    fft = lambda a: sf.rfftn(a, workers=-1)
    ifft = lambda a, n: sf.irfftn(a, s=(n, n, n), workers=-1).astype(np.float32)


    def kgrid(n):
        k, kz = 2 * np.pi * sf.fftfreq(n), 2 * np.pi * sf.rfftfreq(n)
        return k[:, None, None], k[None, :, None], kz[None, None, :]


    def cic_window(n):
        kx, ky, kz = kgrid(n)
        s = lambda q: np.sinc(q / (2 * np.pi))
        return (s(kx) * s(ky) * s(kz)) ** 2


    def density(pos, Ng):
        return (assign(pos, Ng, np.ones(len(pos), np.float32)) * (Ng**3 / len(pos)) - 1).astype(np.float32)


    def initial_conditions(N, L, a_i, seed=SEED):
        # gaußisches Feld mit P(k) bei a_i, Teilchen nach Zel'dovich verschoben (Längen in Gitterzellen, N_g = N)
        w = np.random.default_rng(seed).standard_normal((N, N, N)).astype(np.float32)
        kx, ky, kz = kgrid(N)
        k2 = kx**2 + ky**2 + kz**2
        amp = np.sqrt(plin(np.maximum(np.sqrt(k2) * N / L, 1e-6)) * N**3 / L**3) * growth(a_i)
        amp[0, 0, 0] = 0
        dk = fft(w) * amp
        k2[0, 0, 0] = 1
        q = (np.arange(N, dtype=np.float32) + 0.5)
        grid = np.meshgrid(q, q, q, indexing="ij")
        pos = np.empty((N**3, 3), np.float32)
        mom = np.empty((N**3, 3), np.float32)
        for j, kj in enumerate((kx, ky, kz)):
            psi = ifft(1j * kj / k2 * dk, N).ravel()
            pos[:, j] = (grid[j].ravel() + psi) % N
            mom[:, j] = a_i**2 * f_growth(a_i) * E(a_i) * psi
        return pos, mom, ifft(dk, N) / growth(a_i)       # lineares Feld, auf z = 0 hochgerechnet


    def accel(pos, Ng, a):
        delta = density(pos, Ng)
        kx, ky, kz = kgrid(Ng)
        k2 = kx**2 + ky**2 + kz**2
        k2[0, 0, 0] = 1
        phik = -1.5 * PLANCK["Om"] / a * fft(delta) / k2 / cic_window(Ng) ** 2      # mit Entfaltung beider CIC-Schritte
        phik[0, 0, 0] = 0
        g = [ifft(-1j * np.where(np.abs(kj) > np.pi - 1e-6, 0.0, kj) * phik, Ng) for kj in (kx, ky, kz)]
        return gather(g[0], g[1], g[2], pos), delta


    def simulate(N, L, A, snapshots=()):
        # Kick-Drift-Kick über die Stützstellen A des Skalenfaktors
        pos, mom, delta_lin = initial_conditions(N, L, A[0])
        kick = lambda a1, a2: integrate.quad(lambda a: 1 / (a * E(a)), a1, a2)[0]
        drift = lambda a1, a2: integrate.quad(lambda a: 1 / (a**3 * E(a)), a1, a2)[0]
        g, delta = accel(pos, N, A[0])
        snaps = {}
        for a0, a1 in zip(A[:-1], A[1:]):
            ah = 0.5 * (a0 + a1)
            mom += g * kick(a0, ah)
            pos = (pos + mom * drift(a0, a1)) % N
            g, delta = accel(pos, N, a1)
            mom += g * kick(ah, a1)
            if any(abs(a1 - s) < 1e-9 for s in snapshots):
                snaps[round(a1, 6)] = delta.copy()
        snaps[1.0] = delta
        return dict(N=N, L=L, pos=pos, mom=mom, delta=delta, delta_lin=delta_lin, snaps=snaps,
                    m_particle=0.315 * 2.775e11 * (L / N) ** 3)


    def power(delta, L, nbins=36, deconv=True):
        # Spektrum auf dem Gitter; bei Feldern aus Teilchen (CIC) wird das Fenster entfaltet; Moden der halben rfft-Ebene doppelt gezählt
        n = delta.shape[0]
        kx, ky, kz = kgrid(n)
        k = np.sqrt(kx**2 + ky**2 + kz**2) * n / L
        p = np.abs(fft(delta) / (cic_window(n) if deconv else 1.0)) ** 2 * L**3 / n**6
        mult = np.full(k.shape, 2.0)
        mult[..., 0] = mult[..., -1] = 1
        bins = np.geomspace(2 * np.pi / L, np.pi * n / L, nbins + 1)
        i = np.digitize(k.ravel(), bins)
        cnt = np.bincount(i, mult.ravel(), nbins + 2)[1:-1]
        sk = np.bincount(i, (k * mult).ravel(), nbins + 2)[1:-1]
        sp = np.bincount(i, (p * mult).ravel(), nbins + 2)[1:-1]
        ok = cnt > 0
        return sk[ok] / cnt[ok], sp[ok] / cnt[ok]


    def offsets(n, L):
        # vorzeichenbehaftete Abstände auf dem periodischen Gitter [Mpc/h] und ihr Betrag
        s = np.where(np.arange(n) <= n // 2, np.arange(n), np.arange(n) - n).astype(np.float32) * L / n
        U = np.meshgrid(s, s, s, indexing="ij")
        return U, np.sqrt(U[0]**2 + U[1]**2 + U[2]**2)


    def in_spheres(field, L, R, rmin=0.0):
        # Mittel eines Feldes in der Kugel (oder Schale rmin..R) um jeden Gitterpunkt
        n = field.shape[0]
        _, r = offsets(n, L)
        K = ((r <= R) & (r >= rmin)).astype(np.float32)
        return ifft(fft(field) * fft(K / K.sum()), n)

    A_BIG = np.geomspace(0.02, 1.0, 31)
    A_SMALL = np.concatenate([np.geomspace(0.02, 0.1, 11), np.linspace(0.1, 1.0, 37)[1:]])
    t0 = time.time()
    BIG = simulate(256, 2000.0, A_BIG)
    t1 = time.time()
    SMALL = simulate(256, 250.0, A_SMALL, snapshots=(0.25, 0.5))
    t2 = time.time()
    for lab, s, dt, A in [("großer Würfel", BIG, t1 - t0, A_BIG), ("kleiner Würfel", SMALL, t2 - t1, A_SMALL)]:
        d = s["delta"]
        print(f"{lab}: L = {s['L']:.0f} Mpc/h, {s['N']}³ Teilchen zu je {s['m_particle']:.2e} M☉/h, {len(A) - 1} Schritte in {dt:.0f} s; "
              f"δ auf dem Gitter: σ = {d.std():.2f}, Maximum {d.max():.0f}, leere Zellen {np.mean(d <= -0.999):.1%}")


def initial_spectrum():
    """26. Das Spektrum am Anfang (Zellen 11 von cosmology_nbody.ipynb)."""
    global D2, ax, ax2, col, fig, k, kk, lab, m, p, s
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.6))
    D2 = lambda k, w=True: k**3 * plin(k, w) / (2 * np.pi**2)
    kk = np.geomspace(1e-3, 10, 600)
    ax.loglog(kk, D2(kk), color="k", lw=2, label="linear, mit akustischen Wellen")
    ax.loglog(kk, D2(kk, False), color="0.5", ls="--", label="linear, ohne Wellen")
    ax.axhline(1, color="C3", lw=0.8)
    for s, col, lab in [(BIG, "C0", "großer Würfel"), (SMALL, "C1", "kleiner Würfel")]:
        ax.axvspan(2 * np.pi / s["L"], np.pi * s["N"] / s["L"], color=col, alpha=0.15, label=f"{lab}: {2 * np.pi / s['L']:.4f} bis {np.pi * s['N'] / s['L']:.2f} h/Mpc")
    ax.axvline(k_nl, color="C3", ls=":", label=f"Δ² = 1 bei k = {k_nl:.2f} h/Mpc")
    ax.set_ylim(1e-6, 1e3)
    ax.set_xlabel("Wellenzahl $k$ [h/Mpc]")
    ax.set_ylabel(r"$\Delta^2(k) = k^3 P(k) / 2\pi^2$")
    ax.set_title("Das lineare Spektrum heute und die Bereiche der beiden Würfel", fontsize=10)
    ax.legend(fontsize=9, loc="upper left")
    for s, col, lab in [(BIG, "C0", "großer Würfel"), (SMALL, "C1", "kleiner Würfel")]:
        k, p = power(s["delta_lin"], s["L"], deconv=False)
        ax2.semilogx(k, p / plin(k), "o-", color=col, ms=4, label=lab)
    ax2.axhline(1, color="k", lw=0.8)
    ax2.set_ylim(0, 2.5)
    ax2.set_xlabel("Wellenzahl $k$ [h/Mpc]")
    ax2.set_ylabel("gemessen / Eingabe")
    ax2.set_title("Spektrum der Anfangsbedingungen (auf z = 0 hochgerechnet)", fontsize=10)
    ax2.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    for s, lab in [(BIG, "groß"), (SMALL, "klein")]:
        k, p = power(s["delta_lin"], s["L"], deconv=False)
        m = (k > 5 * 2 * np.pi / s["L"]) & (k < 0.3 * np.pi * s["N"] / s["L"])
        print(f"Würfel {lab}: Anfangsspektrum / Eingabe = {np.mean(p[m] / plin(k[m])):.3f} ± {np.std(p[m] / plin(k[m])):.3f} "
              f"(Bins mit 5 k_f < k < 0.3 k_Nyq); Zelle {s['L'] / s['N']:.2f} Mpc/h")
    print(f"nichtlinear ab k = {k_nl:.2f} h/Mpc, also auf Skalen unter 2π/k = {2 * np.pi / k_nl:.0f} Mpc/h; σ₈ = {sigma_lin(8):.3f}")


def cosmic_web():
    """27. Das kosmische Netz entsteht (Zellen 14 von cosmology_nbody.ipynb)."""
    global L, STATS2, a, ax, axs, d, dmax, fig, im, img, m_hi, m_lo
    global n, thick, v_hi, v_lo
    fig, axs = plt.subplots(1, 3, figsize=(17, 6))
    n, L = SMALL["N"], SMALL["L"]
    thick = int(20 / (L / n))
    STATS2 = {}
    for ax, a in zip(axs, [0.25, 0.5, 1.0]):
        d = SMALL["snaps"][a]
        img = np.log10(np.maximum(1 + d[:thick].mean(axis=0), 1e-2))
        im = ax.imshow(img.T, origin="lower", extent=[0, L, 0, L], cmap="inferno", vmin=-1, vmax=2)
        ax.set_title(f"z = {1 / a - 1:.0f}: Scheibe von {thick * L / n:.0f} Mpc/h Dicke", fontsize=10)
        ax.set_xlabel("x [Mpc/h]")
        STATS2[a] = (np.mean(d > 9), np.mean((1 + d) * (d > 9)), np.mean(d < -0.5), np.mean((1 + d) * (d < -0.5)), d.max())
    axs[0].set_ylabel("y [Mpc/h]")
    fig.colorbar(im, ax=axs, shrink=0.8, label=r"$\log_{10}(1 + \delta)$, gemittelt über die Scheibe")
    plt.show()

    for a, (v_hi, m_hi, v_lo, m_lo, dmax) in STATS2.items():
        print(f"z = {1 / a - 1:.0f}: δ > 9 in {v_hi:.2%} des Volumens mit {m_hi:.1%} der Masse; δ < −0.5 in {v_lo:.1%} des Volumens mit {m_lo:.1%} der Masse; "
              f"dichteste Zelle δ = {dmax:.0f}")


def growth_check():
    """28. Wächst die Simulation richtig? (Zellen 17 von cosmology_nbody.ipynb)."""
    global NL, RATIO_BIG, a, ax, ax2, col, fig, k, k0, k0s, k1, keep
    global knl_a, m, p, p0, p0s, p1, r
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.6))
    k0, p0 = power(BIG["delta_lin"], BIG["L"], deconv=False)
    k1, p1 = power(BIG["delta"], BIG["L"])
    RATIO_BIG = p1 / p0
    ax.semilogx(k1, RATIO_BIG, "o-", color="C0", ms=4, label="großer Würfel, z = 0")
    ax.axvline(0.2 * np.pi * BIG["N"] / BIG["L"], color="0.5", ls=":", label="ein Fünftel der Nyquist-Wellenzahl")
    ax.axvline(k_nl, color="C3", ls=":", label=r"$\Delta^2_\mathrm{lin} = 1$")
    ax.axhline(1, color="k", lw=0.8)
    ax.set_ylim(0.8, 1.6)
    ax.set_xlabel("Wellenzahl $k$ [h/Mpc]")
    ax.set_ylabel(r"$P_\mathrm{Sim} / (D^2 P_\mathrm{Anfang})$, Mode für Mode")
    ax.set_title("Großer Würfel: lineares Wachstum auf großen Skalen", fontsize=10)
    ax.legend(fontsize=9)
    k0s, p0s = power(SMALL["delta_lin"], SMALL["L"], deconv=False)
    NL = {}
    for a, col in [(0.25, "C2"), (0.5, "C1"), (1.0, "C3")]:
        k, p = power(SMALL["snaps"][a], SMALL["L"])
        keep = k < 0.5 * np.pi * SMALL["N"] / SMALL["L"]                        # bis zur halben Nyquist-Wellenzahl
        NL[a] = (k[keep], (p - SMALL["L"] ** 3 / SMALL["N"] ** 3)[keep] / (p0s[keep] * growth(a) ** 2))   # ohne Schrotrauschen V/N
        k = k[keep]
        knl_a = np.exp(np.interp(0.0, np.log(KH**3 * plin(KH) * growth(a) ** 2 / (2 * np.pi**2)), LNK))
        ax2.loglog(k, NL[a][1], "o-", color=col, ms=4, label=f"z = {1 / a - 1:.0f}")
        ax2.axvline(knl_a, color=col, ls=":", lw=1)
    ax2.axvline(0.2 * np.pi * SMALL["N"] / SMALL["L"], color="0.5", ls=":", label="ein Fünftel der Nyquist-Wellenzahl")
    ax2.axhline(1, color="k", lw=0.8)
    ax2.set_xlabel("Wellenzahl $k$ [h/Mpc]")
    ax2.set_ylabel(r"$P_\mathrm{Sim} / (D^2 P_\mathrm{Anfang})$")
    ax2.set_yticks([0.8, 1, 2, 5, 10])
    ax2.set_yticklabels(["0.8", "1", "2", "5", "10"])
    ax2.set_title(r"Kleiner Würfel: nichtlineares Wachstum (gepunktet: $\Delta^2_\mathrm{lin} = 1$)", fontsize=10)
    ax2.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    m = k1 < 0.1
    print(f"großer Würfel, k < 0.1 h/Mpc: Verhältnis {RATIO_BIG[m].mean():.3f} ± {RATIO_BIG[m].std():.3f} ({m.sum()} Bins); bei k = 0.2: {np.interp(0.2, k1, RATIO_BIG):.2f}")
    for a, (k, r) in NL.items():
        print(f"kleiner Würfel z = {1 / a - 1:.0f}: Verhältnis bei k = 0.1: {np.interp(0.1, k, r):.2f}, k = 0.3: {np.interp(0.3, k, r):.2f}, "
              f"k = 1: {np.interp(1.0, k, r):.2f}, k = {k[-1]:.1f}: {r[-1]:.1f}")


def bao_in_simulation():
    """29. Der BAO-Peak in der Simulation (Zellen 20 von cosmology_nbody.ipynb)."""
    global L, RG, U, XI, ax, bao_peak, bins, cnt, d, fig, i100, ib
    global lab, n, rc, w, xi, xi_th
    n, L = BIG["N"], BIG["L"]
    U, RG = offsets(n, L)
    bins = np.arange(16.0, 204.0, 4.0)
    rc = 0.5 * (bins[1:] + bins[:-1])
    ib = np.digitize(RG.ravel(), bins)
    cnt = np.bincount(ib, minlength=len(bins) + 1)[1:-1]
    XI = {}
    for lab, d, w in [("Simulation z = 0", BIG["delta"], cic_window(n)), ("Anfangsfeld (linear)", BIG["delta_lin"], 1.0)]:
        xi = ifft(np.abs(fft(d) / w) ** 2, n) / n**3
        XI[lab] = np.bincount(ib, xi.ravel(), len(bins) + 1)[1:-1] / cnt
    xi_th = {w: np.array([np.trapz(KH**3 * plin(KH, w) * np.exp(-(KH / 1.0) ** 2) * np.sinc(KH * r / np.pi) / (2 * np.pi**2), LNK) for r in rc])
             for w in (True, False)}


    def bao_peak(xi):
        m = (rc > 80) & (rc < 120)
        y = (rc**2 * xi)[m]
        j = np.clip(np.argmax(y), 1, m.sum() - 2)
        c = np.polyfit(rc[m][j - 1:j + 2], y[j - 1:j + 2], 2)
        return -c[1] / (2 * c[0])


    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(rc, rc**2 * xi_th[True], color="k", lw=2, label="linear mit Wellen (Theorie)")
    ax.plot(rc, rc**2 * xi_th[False], color="0.5", ls="--", label="linear ohne Wellen")
    ax.plot(rc, rc**2 * XI["Anfangsfeld (linear)"], "s", color="C0", ms=4, label="Anfangsfeld dieses Würfels, auf z = 0 hochgerechnet")
    ax.plot(rc, rc**2 * XI["Simulation z = 0"], "o-", color="C3", ms=5, label="Simulation z = 0")
    ax.axvline(S_EH * PLANCK["h"], color="C2", ls=":", label=f"Schallhorizont (Eisenstein & Hu) {S_EH * PLANCK['h']:.1f} Mpc/h")
    ax.set_xlabel("Abstand $r$ [Mpc/h]")
    ax.set_ylabel(r"$r^2\,\xi(r)$ [(Mpc/h)²]")
    ax.set_title("Der akustische Peak in der Korrelationsfunktion (großer Würfel)", fontsize=10)
    ax.legend(fontsize=9)
    plt.show()

    for lab, xi in [("Theorie linear", xi_th[True]), ("Anfangsfeld", XI["Anfangsfeld (linear)"]), ("Simulation z = 0", XI["Simulation z = 0"])]:
        i100 = np.argmin(abs(rc - 102))
        print(f"{lab:17s}: Peak bei {bao_peak(xi):6.1f} Mpc/h, r²ξ bei 102 Mpc/h = {rc[i100]**2 * xi[i100]:5.1f}")
    print(f"mittlere Verschiebung der Teilchen seit dem Anfang (linear, 3D): {np.sqrt(np.trapz(KH * plin(KH) / (2 * np.pi**2), LNK)):.1f} Mpc/h")


def sphere_variance():
    """30. Wie stark schwankt die Dichte in Kugeln? (Zellen 23 von cosmology_nbody.ipynb)."""
    global L, R, R_BIG, R_SMALL, Rs, SIG, ax, ax2, col, fig, lab, rr
    global s, sl, sn
    R_SMALL = np.array([3, 4, 6, 8, 12, 16, 25, 40])
    R_BIG = np.array([30, 40, 60, 80, 100, 150, R_KBC, 250])
    SIG = {}
    for s, Rs in [(SMALL, R_SMALL), (BIG, R_BIG)]:
        for R in Rs:
            SIG[(s["L"], float(R))] = (in_spheres(s["delta"], s["L"], R).std(), in_spheres(s["delta_lin"], s["L"], R).std())
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.6))
    rr = np.geomspace(2, 400, 200)
    ax.loglog(rr, [sigma_lin(r) for r in rr], color="k", lw=2, label="linear (Theorie)")
    for s, Rs, col, lab in [(SMALL, R_SMALL, "C1", "kleiner Würfel"), (BIG, R_BIG, "C0", "großer Würfel")]:
        ax.loglog(Rs, [SIG[(s["L"], float(R))][0] for R in Rs], "o", color=col, ms=7, label=f"Simulation z = 0, {lab}")
        ax.loglog(Rs, [SIG[(s["L"], float(R))][1] for R in Rs], "x", color=col, ms=7, label=f"Anfangsfeld, {lab}")
        ax2.semilogx(Rs, [SIG[(s["L"], float(R))][0] / SIG[(s["L"], float(R))][1] for R in Rs], "o-", color=col, ms=6, label=lab)
    ax.axvline(R_KBC, color="C3", ls=":", label="300 Mpc (KBC-Leere)")
    ax.set_xlabel("Radius $R$ [Mpc/h]")
    ax.set_ylabel(r"$\sigma(R)$")
    ax.set_title("Streuung der mittleren Dichte in Kugeln", fontsize=10)
    ax.legend(fontsize=9)
    ax2.axhline(1, color="k", lw=0.8)
    ax2.set_xlabel("Radius $R$ [Mpc/h]")
    ax2.set_ylabel(r"$\sigma_\mathrm{Sim} / \sigma_\mathrm{Anfangsfeld}$")
    ax2.set_title("Nichtlineare Verstärkung, Mode für Mode", fontsize=10)
    ax2.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    for (L, R), (sn, sl) in SIG.items():
        print(f"L = {L:6.0f}, R = {R:5.0f} Mpc/h: σ Simulation {sn:.4f}, Anfangsfeld {sl:.4f}, Theorie {sigma_lin(R):.4f}; Verhältnis {sn / sl:.3f}")


def sphere_distribution():
    """31. Die Verteilung der Dichte in Kugeln (Zellen 26 von cosmology_nbody.ipynb)."""
    global CASES6, PDF, R, ax, axs, c, d, e, fig, h, hi, lo
    global med, mn, mode, s, s2, sg, sk, x
    CASES6 = [(SMALL, 8.0), (SMALL, 25.0), (BIG, 100.0), (BIG, R_KBC)]
    fig, axs = plt.subplots(1, 4, figsize=(18, 4.8))
    PDF = {}
    for ax, (s, R) in zip(axs, CASES6):
        d = in_spheres(s["delta"], s["L"], R).ravel()
        sg = d.std()
        lo, hi = max(-1, d.min()), np.percentile(d, 99.9)
        h, e = np.histogram(d, bins=120, range=(lo, hi), density=True)
        c = 0.5 * (e[1:] + e[:-1])
        s2 = np.log(1 + sg**2)
        x = np.linspace(lo, hi, 400)
        ax.plot(c, h, color="k", lw=1.8, label="Simulation")
        ax.plot(x, stats.norm.pdf(x, 0, sg), color="C0", ls="--", label="Gauß")
        ax.plot(x, stats.lognorm.pdf(1 + x, np.sqrt(s2), scale=np.exp(-s2 / 2)), color="C3", ls=":", lw=2, label="lognormal")
        ax.axvline(0, color="0.6", lw=0.8)
        ax.set_title(f"R = {R:.0f} Mpc/h (σ = {sg:.3f})", fontsize=10)
        ax.set_xlabel(r"$\delta_R$")
        PDF[R] = (sg, stats.skew(d), np.median(d), c[np.argmax(h)], d.min())
    axs[0].set_ylabel("Wahrscheinlichkeitsdichte")
    axs[0].legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    for R, (sg, sk, med, mode, mn) in PDF.items():
        print(f"R = {R:5.0f} Mpc/h: σ = {sg:.3f}, Schiefe {sk:+.2f}, Median {med:+.3f}, häufigster Wert {mode:+.3f}, kleinster Wert {mn:+.3f} ({mn / sg:.1f}σ)")


def kbc_rarity():
    """32. Wie selten ist die KBC-Leere? (Zellen 29 von cosmology_nbody.ipynb)."""
    global D202, NU_KBC, NU_KBC_ERR, N_BOX, N_UNIVERSE, SIG202, ax, ax2, col, fig, lab, nu
    global nus, p_sf, v, x
    D202 = in_spheres(BIG["delta"], BIG["L"], R_KBC).ravel()
    SIG202 = D202.std()
    N_BOX = BIG["L"] ** 3 / (4 / 3 * np.pi * R_KBC**3)
    N_UNIVERSE = (R_HORIZON / KBC["R"]) ** 3
    NU_KBC = abs(KBC["delta"]) / SIG202
    NU_KBC_ERR = abs(KBC["delta"]) / np.hypot(SIG202, KBC["err"])
    p_sf = lambda nu: np.exp(stats.norm.logsf(nu))
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.6))
    ax.hist(D202 / SIG202, bins=100, density=True, color="C0", alpha=0.6, label="Simulation (alle Gitterpunkte)")
    x = np.linspace(-5, 5, 300)
    ax.plot(x, stats.norm.pdf(x), color="k", lw=1.5, label="Gauß")
    ax.axvline(D202.min() / SIG202, color="C3", ls="--", label=f"leerste Kugel: δ = {D202.min():.3f}")
    ax.set_xlabel(r"$\delta_R / \sigma$ für R = 300 Mpc")
    ax.set_ylabel("Wahrscheinlichkeitsdichte")
    ax.set_title(f"Dichte in Kugeln von 300 Mpc (σ = {SIG202:.4f})", fontsize=10)
    ax.legend(fontsize=9)
    nu = np.linspace(0, 22, 500)
    ax2.semilogy(nu, p_sf(nu), color="k", lw=1.5, label="Gauß")
    nus = np.linspace(0, abs(D202.min()) / SIG202, 60)
    ax2.semilogy(nus, [np.mean(D202 <= -v * SIG202) for v in nus], color="C0", lw=3, label="Simulation")
    ax2.axhline(1 / N_UNIVERSE, color="0.4", ls=":", label=f"einmal im beobachtbaren Universum (1/{N_UNIVERSE:.1e})")
    for v, col, lab in [(NU_KBC, "C3", "KBC ohne Messfehler"), (NU_KBC_ERR, "C1", "KBC mit Messfehler 0.06"), (HASLBAUER_SIGMA, "C2", "Haslbauer et al. 2020")]:
        ax2.axvline(v, color=col, ls="--", label=f"{lab}: {v:.1f}σ")
    ax2.set_ylim(1e-100, 2)
    ax2.set_xlabel(r"$\nu$ (Standardabweichungen unter dem Mittel)")
    ax2.set_ylabel(r"Wahrscheinlichkeit $P(\delta \leq -\nu\sigma)$")
    ax2.set_title("Wie selten ist eine Leere dieser Tiefe?", fontsize=10)
    ax2.legend(fontsize=9, loc="lower left")
    plt.tight_layout()
    plt.show()

    print(f"σ(300 Mpc) = {SIG202:.4f} (linear {sigma_lin(R_KBC):.4f}); Schiefe {stats.skew(D202):+.3f}; leerste Kugel δ = {D202.min():+.4f} = {D202.min() / SIG202:.2f}σ; "
          f"unabhängige Kugeln im Würfel ≈ {N_BOX:.0f}, im beobachtbaren Universum ≈ {N_UNIVERSE:.2e}")
    for lab, v in [("KBC ohne Messfehler", NU_KBC), ("KBC mit Messfehler", NU_KBC_ERR)]:
        print(f"{lab}: {v:.1f}σ, p = {p_sf(v):.1e}, erwartete Zahl im beobachtbaren Universum {N_UNIVERSE * p_sf(v):.1e}")
    print(f"nötige Tiefe für p = 1/{N_UNIVERSE:.0e}: δ = {-stats.norm.isf(1 / N_UNIVERSE) * SIG202:.3f}")


def void_environments():
    """33. Wo Leeren dieser Tiefe häufig sind (Zellen 32 von cosmology_nbody.ipynb)."""
    global FRAC, L_, R, R1, Rs, ax, cells, col, d, do, fig, fo
    global fr, j, lab, mo, mr, pts, rng, s
    rng = np.random.default_rng(8)
    FRAC = {}
    for s, Rs in [(SMALL, [3, 4, 6, 8, 12, 16, 20, 25, 30, 40]), (BIG, [30, 40, 50, 60, 80, 100])]:
        cells = np.floor(s["pos"][rng.choice(len(s["pos"]), 200_000, replace=False)]).astype(int) % s["N"]
        for R in Rs:
            d = in_spheres(s["delta"], s["L"], R)
            do = d[cells[:, 0], cells[:, 1], cells[:, 2]]
            FRAC[(s["L"], R)] = (np.mean(d <= KBC["delta"]), np.mean(do <= KBC["delta"]), np.median(d), np.median(do))
    fig, ax = plt.subplots(figsize=(12, 6))
    for L_, col, lab in [(SMALL["L"], "C1", "kleiner Würfel"), (BIG["L"], "C0", "großer Würfel")]:
        Rs = [R for (L2, R) in FRAC if L2 == L_]
        ax.semilogy(Rs, [max(FRAC[(L_, R)][0], 1e-7) for R in Rs], "o-", color=col, label=f"um zufällige Punkte, {lab}")
        ax.semilogy(Rs, [max(FRAC[(L_, R)][1], 1e-7) for R in Rs], "s--", color=col, label=f"um Teilchen (Beobachter in Materie), {lab}")
    ax.axhline(0.01, color="0.5", ls=":", label="1 %")
    ax.set_ylim(1e-6, 1)
    ax.set_xlabel("Radius $R$ [Mpc/h]")
    ax.set_ylabel(r"Anteil der Kugeln mit $\delta_R \leq -0.46$")
    ax.set_title("Leeren so tief wie die KBC-Leere: häufig nur auf kleinen Skalen", fontsize=10)
    ax.legend(fontsize=9)
    plt.show()

    for j, lab in [(0, "zufällige Punkte"), (1, "Beobachter in Materie")]:
        pts = sorted((R, v[j]) for (L_, R), v in FRAC.items() if (L_ == SMALL["L"] and R <= 30) or (L_ == BIG["L"] and R > 30))
        R1 = np.exp(np.interp(np.log(0.01), np.log([max(p, 1e-9) for _, p in pts])[::-1], np.log([R for R, _ in pts])[::-1]))
        print(f"{lab:22s}: Anteil 1 % bei R = {R1:.0f} Mpc/h ({R1 / PLANCK['h']:.0f} Mpc); " +
              ", ".join(f"R = {R}: {p:.2%}" for R, p in pts if R in (8, 16, 25, 40, 60)))
    for (L_, R), (fr, fo, mr, mo) in FRAC.items():
        if R in (8, 25) and L_ == SMALL["L"] or R == 60:
            print(f"R = {R} Mpc/h: Median δ_R um zufällige Punkte {mr:+.3f}, um Teilchen {mo:+.3f}")


def local_h0():
    """34. Die lokale Hubble-Konstante (Zellen 35 von cosmology_nbody.ipynb)."""
    global DH202, DHL202, DLK, F_KBC, HL, K2, Kj, L, MOM, MOM_LIN, R, RHOK
    global Rs, SLOPE, Ug, ax, ax2, dH, dHl, fig, k2, kx, ky, kz
    global n, norm, sub, w, xx
    n, L = BIG["N"], BIG["L"]
    norm = n**3 / len(BIG["pos"])
    MOM = [fft((assign(BIG["pos"], n, np.ascontiguousarray(BIG["mom"][:, j])) * norm).astype(np.float32)) for j in range(3)]
    RHOK = fft(1 + BIG["delta"])
    kx, ky, kz = kgrid(n)
    k2 = kx**2 + ky**2 + kz**2
    k2[0, 0, 0] = 1
    DLK = fft(BIG["delta_lin"])
    MOM_LIN = [fft(ifft(1j * kj / k2 * DLK, n) * f_growth(1.0)) for kj in (kx, ky, kz)]      # p = f ψ bei a = 1 (Gittereinheiten)
    Ug = [u * n / L for u in U]                                                               # Abstände in Gitterzellen
    HL = {}
    for R in [50, 100, 150, R_KBC]:
        w = ((RG >= 10) & (RG <= R)).astype(np.float32)
        Kj = [fft(-u * w) for u in Ug]
        K2 = fft((Ug[0]**2 + Ug[1]**2 + Ug[2]**2) * w)
        dH = sum(ifft(MOM[j] * Kj[j], n) for j in range(3)) / ifft(RHOK * K2, n)
        dHl = sum(ifft(MOM_LIN[j] * Kj[j], n) for j in range(3)) / float(((Ug[0]**2 + Ug[1]**2 + Ug[2]**2) * w).sum())
        HL[R] = (dH, dHl)
    DH202, DHL202 = HL[R_KBC]
    SLOPE = np.polyfit(D202[::11], DH202.ravel()[::11], 1)[0]
    F_KBC = -f_growth(1.0) * KBC["delta"] / 3
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.8))
    Rs = list(HL)
    ax.semilogy(Rs, [100 * HL[R][0].std() for R in Rs], "o-", color="C0", ms=7, label="Simulation")
    ax.semilogy(Rs, [100 * HL[R][1].std() for R in Rs], "x--", color="k", ms=8, label="lineares Geschwindigkeitsfeld")
    ax.axhline(100 * F_KBC, color="C3", ls="--", label=f"KBC-Leere, linear: +{100 * F_KBC:.1f} %")
    ax.axhline(100 * (73.0 / 67.4 - 1), color="C1", ls=":", label="73 statt 67.4 km/s/Mpc: +8.3 %")
    ax.set_xlabel("Radius $R$ der Messung [Mpc/h]")
    ax.set_ylabel(r"Streuung von $\delta H / H_0$ [%]")
    ax.set_yticks([0.3, 0.5, 1, 2, 5, 10])
    ax.set_yticklabels(["0.3", "0.5", "1", "2", "5", "10"])
    ax.set_ylim(0.3, 12)
    ax.set_title("Wie stark streut die lokal gemessene Hubble-Konstante?", fontsize=10)
    ax.legend(fontsize=9)
    sub = np.random.default_rng(9).choice(D202.size, 30000, replace=False)
    ax2.plot(D202[sub], 100 * DH202.ravel()[sub], ",", color="C0", alpha=0.5)
    xx = np.linspace(-0.6, 0.15, 10)
    ax2.plot(xx, -100 * f_growth(1.0) * xx / 3, color="k", lw=1.2, label=r"linear: $-f\delta/3$")
    ax2.errorbar(KBC["delta"], 100 * F_KBC, xerr=KBC["err"], fmt="*", color="C3", ms=14, label="KBC-Leere")
    ax2.set_xlabel(r"mittlere Dichte in der Kugel $\delta_R$ (R = 300 Mpc)")
    ax2.set_ylabel(r"$\delta H / H_0$ [%]")
    ax2.set_title("Lokale Hubble-Konstante und Dichte um den Beobachter (R = 300 Mpc)", fontsize=10)
    ax2.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    for R, (dH, dHl) in HL.items():
        print(f"R = {R:5.0f} Mpc/h ({R / PLANCK['h']:3.0f} Mpc): σ(δH/H₀) = {100 * dH.std():.3f} % (linear {100 * dHl.std():.3f} %), größter Wert {100 * dH.max():+.2f} %")
    print(f"Steigung δH/H₀ gegen δ_R bei 300 Mpc: {SLOPE:+.3f} (−f/3 = {-f_growth(1.0) / 3:+.3f}); KBC verlangt +{100 * F_KBC:.1f} % = {F_KBC / DH202.std():.0f}σ")


def literature():
    """35. Gegen die veröffentlichten Werte (Zellen 38 von cosmology_nbody.ipynb)."""
    global _, ax, ax2, fig, lab, rows, v
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(16, 5.4))
    rows = [("eigene Simulation, ohne Messfehler", NU_KBC, "C0"), ("eigene Simulation, Messfehler 0.06", NU_KBC_ERR, "C0"),
            ("lineare Theorie (cosmology_localvoid)", LOCALVOID_SIGMA, "0.4"), ("Haslbauer et al. 2020 (MXXL)", HASLBAUER_SIGMA, "0.4")]
    ax.barh(np.arange(len(rows)), [r[1] for r in rows], color=[r[2] for r in rows])
    ax.set_yticks(np.arange(len(rows)))
    ax.set_yticklabels([r[0] for r in rows], fontsize=9.5)
    ax.invert_yaxis()
    ax.axvline(5, color="C3", ls=":", label="5σ")
    ax.set_xlabel("Spannung der KBC-Leere mit ΛCDM [σ]")
    ax.set_title("Wie unwahrscheinlich ist die KBC-Leere?", fontsize=10)
    ax.legend(fontsize=9)
    ax2.plot([R / PLANCK["h"] for R in HL], [100 * HL[R][0].std() for R in HL], "o-", color="C0", ms=7, label="eigene Simulation (Schale 10 Mpc/h bis R)")
    ax2.axhline(100 * WU_HUTERER, color="0.4", ls="--", label=f"Wu & Huterer 2017: {100 * WU_HUTERER:.2f} % (Supernovae, z = 0.023–0.15)")
    ax2.axhline(100 * (73.0 / 67.4 - 1), color="C1", ls=":", label="73 statt 67.4: +8.3 %")
    ax2.set_yscale("log")
    ax2.set_yticks([0.3, 0.5, 1, 2, 5, 10])
    ax2.set_yticklabels(["0.3", "0.5", "1", "2", "5", "10"])
    ax2.set_ylim(0.3, 12)
    ax2.set_xlabel("Radius $R$ [Mpc]")
    ax2.set_ylabel(r"Streuung der lokalen $H_0$ [%]")
    ax2.set_title("Kosmische Varianz der Hubble-Konstante", fontsize=10)
    ax2.legend(fontsize=9)
    plt.tight_layout()
    plt.show()

    for lab, v, _ in rows:
        print(f"{lab:40s}: {v:5.1f}σ")
    print(f"σ(H₀,lokal) bei 300 Mpc: {100 * DH202.std():.2f} %, Wu & Huterer {100 * WU_HUTERER:.2f} %; nötig für die Spannung: 8.3 % = {0.083 / DH202.std():.0f}σ")
