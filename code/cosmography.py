"""Kosmographie für approximation.ipynb: die Leuchtkraftentfernung als Taylor-Reihe in z und ihre Grenzen bei Pantheon+.

Die Entfernung einer Supernova hängt in jeder Kosmologie bei kleinem z nur von wenigen Zahlen ab: H₀, der Abbremsung q₀
und dem Ruck j₀ (Visser 2004). Wie weit diese Reihe trägt, bestimmen Verzweigungspunkte von E(z) = H(z)/H₀ in der
komplexen Ebene. Die Reihenkoeffizienten des flachen ΛCDM-Modells werden mit Potenzreihen-Arithmetik berechnet (beliebige
Ordnung), auch in der Variablen y = z/(1+z) (Cattoën und Visser 2007). Daten: Pantheon+ über `pantheon.load`
(1701 Lichtkurven mit voller Kovarianz aus Statistik und Systematik); angepasst wird mit dieser Kovarianz.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares

import pantheon


# ---- Potenzreihen (Koeffizienten c[0], c[1], … für c[0] + c[1] z + …)

def _pow(s, a, N):
    """(Reihe s)^a mit s[0] ≠ 0, auf N Koeffizienten (Rekursion von J. C. P. Miller)."""
    s = np.concatenate([s, np.zeros(max(0, N - len(s)))])
    p = np.zeros(N)
    p[0] = s[0] ** a
    for n in range(1, N):
        k = np.arange(1, n + 1)
        p[n] = np.sum((a * k - (n - k)) * s[k] * p[n - k]) / (n * s[0])
    return p


def series_z(om, N=40):
    """Koeffizienten von H₀ d_L/c = (1+z) ∫₀^z dz'/E(z') im flachen ΛCDM mit E² = Ω_m(1+z)³ + 1 − Ω_m."""
    inv_e = _pow(np.array([1, 3 * om, 3 * om, om]), -0.5, N)
    integral = np.zeros(N)
    integral[1:] = inv_e[:-1] / np.arange(1, N)
    return np.convolve([1, 1], integral)[:N]


def series_y(c, N=40):
    """Dieselbe Reihe in y = z/(1+z): z = y + y² + y³ + … einsetzen und neu ordnen."""
    zy = np.zeros(N)
    zy[1:] = 1
    out, power = np.zeros(N), np.zeros(N)
    power[0] = 1
    for k in range(N):
        out += c[k] * power
        power = np.convolve(power, zy)[:N]
    return out


def branch_points(om):
    """Nullstellen von E²(z) = Ω_m(1+z)³ + 1 − Ω_m: dort hat 1/E Verzweigungspunkte."""
    return np.roots([om, 3 * om, 3 * om, 1])


def exact(z, om, nodes=60):
    """H₀ d_L/c im flachen ΛCDM; das Integral mit Gauß-Legendre (60 Knoten, auf Maschinengenauigkeit)."""
    z = np.asarray(z, float)
    u, w = np.polynomial.legendre.leggauss(nodes)
    zp = z[..., None] * (u + 1) / 2
    integral = (z / 2) * np.sum(w / np.sqrt(om * (1 + zp) ** 3 + 1 - om), axis=-1)
    return (1 + z) * integral


# ---- Anpassung an Pantheon+

def _model(kind, p, z, zhel):
    """H₀ d_L/c für ΛCDM (p = Ω_m) oder die Reihe dritter Ordnung in z bzw. y (p = q₀, j₀); (1 + z_hel) D_M."""
    if kind == "lcdm":
        return exact(z, p[0]) / (1 + z) * (1 + zhel)
    q0, j0 = p
    if kind == "z":
        d = z + 0.5 * (1 - q0) * z ** 2 - (1 - q0 - 3 * q0 ** 2 + j0) / 6 * z ** 3
    else:
        y = z / (1 + z)
        d = y + 0.5 * (3 - q0) * y ** 2 + (11 - 5 * q0 + 3 * q0 ** 2 - j0) / 6 * y ** 3
    return d / (1 + z) * (1 + zhel)


def fit(sn, cov, kind, zmax, zmin=0.01):
    """Anpassung mit voller Kovarianz an alle Supernovae mit zmin < z < zmax; die Konstante schluckt M_B und H₀.

    Gibt (Parameter, Fehler, χ², Zahl der Supernovae) zurück, ohne die Konstante.
    """
    z, zhel, m = sn["zHD"].values, sn["zHEL"].values, sn["m_b_corr"].values
    idx = np.flatnonzero((z > zmin) & (z < zmax))
    L = np.linalg.cholesky(cov[np.ix_(idx, idx)])
    p0 = [0.3] if kind == "lcdm" else [-0.5, 1.0]

    def resid(p):
        d = np.clip(_model(kind, p[1:], z[idx], zhel[idx]), 1e-9, None)
        return np.linalg.solve(L, m[idx] - p[0] - 5 * np.log10(d))

    sol = least_squares(resid, [np.mean(m[idx] - 5 * np.log10(z[idx]))] + p0)
    err = np.sqrt(np.diag(np.linalg.inv(sol.jac.T @ sol.jac)))
    return sol.x[1:], err[1:], 2 * sol.cost, len(idx)


def plot_cosmography(sn, cov, zmaxs=(0.15, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.3), orders=(3, 8, 24)):
    """Links: Fehler der Reihen in z und y gegen das exakte ΛCDM; rechts: q₀ aus der Reihe in z gegen die größte Rotverschiebung."""
    (om,), (om_err,), chi2, n = fit(sn, cov, "lcdm", 10)
    q0_ref, q0_ref_err = 1.5 * om - 1, 1.5 * om_err
    print(f"ΛCDM an alle {n} Supernovae mit z > 0.01: Ω_m = {om:.3f} ± {om_err:.3f}, also q₀ = 3Ω_m/2 − 1 = "
          f"{q0_ref:.3f} ± {q0_ref_err:.3f} und j₀ = 1 (χ² = {chi2:.0f})")
    bp = branch_points(om)
    r_z = np.min(np.abs(bp))
    r_y = np.min(np.abs(bp / (1 + bp)))
    zmax_data = sn["zHD"].max()
    print(f"Verzweigungspunkte von E(z) bei z = {bp[np.argmin(np.abs(bp))]:.2f} und konjugiert: Konvergenzradius in z "
          f"{r_z:.2f}, in y = z/(1+z) {r_y:.2f}; die Daten reichen bis z = {zmax_data:.2f}, also y = {zmax_data / (1 + zmax_data):.2f}")
    cz = series_z(om)
    cy = series_y(cz)
    zz = np.linspace(0.005, 2.4, 1200)
    ex = exact(zz, om)
    k1, k2 = np.searchsorted(zz, [1.0, 2.26])
    for o in orders:
        ez = np.abs(np.polyval(cz[:o + 1][::-1], zz) / ex - 1)
        ey = np.abs(np.polyval(cy[:o + 1][::-1], zz / (1 + zz)) / ex - 1)
        print(f"  Ordnung {o:2d}: relativer Fehler bei z = 1 und 2.26: Reihe in z {ez[k1]:.1e} und {ez[k2]:.1e}, "
              f"Reihe in y {ey[k1]:.1e} und {ey[k2]:.1e}")
    print("q₀ aus der Reihe dritter Ordnung (q₀ und j₀ frei) gegen die größte Rotverschiebung der Auswahl:")
    res = []
    for zmax in zmaxs:
        (q, j), (qe, je), c2, n = fit(sn, cov, "z", zmax)
        res.append((zmax, q, qe))
        print(f"  z < {zmax:3.2f}: {n:4d} Supernovae, q₀ = {q:+.2f} ± {qe:.2f}, j₀ = {j:+.1f} ± {je:.1f}, "
              f"Abstand zu ΛCDM {(q - q0_ref) / np.hypot(qe, q0_ref_err):+.1f} σ")
    (q, j), (qe, je), _, _ = fit(sn, cov, "y", 10)
    print(f"  dieselbe Reihe in y an alle Daten: q₀ = {q:+.2f} ± {qe:.2f}, j₀ = {j:+.1f} ± {je:.1f}")
    res = np.array(res)

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    ax = axes[0]
    colors = ["tab:orange", "tab:green", "tab:purple"]
    for o, c in zip(orders, colors):
        ax.semilogy(zz, np.abs(np.polyval(cz[:o + 1][::-1], zz) / ex - 1), color=c, lw=1.4, label=f"Reihe in z, Ordnung {o}")
        ax.semilogy(zz, np.abs(np.polyval(cy[:o + 1][::-1], zz / (1 + zz)) / ex - 1), color=c, lw=1, ls="--",
                    label=f"Reihe in y, Ordnung {o}")
    ax.axvline(r_z, color="black", ls=":", lw=1)
    ax.text(r_z + 0.03, 1e-14, f"Radius in z: {r_z:.2f}", fontsize=8)
    zs = sn["zHD"][sn["zHD"] > 0.01]
    ax.plot(zs, np.full(len(zs), 3e-16), "|", color="grey", ms=12, alpha=0.4, label="je Strich eine Supernova")
    ax.set_ylim(1e-16, 1e7)
    ax.set_xlabel("Rotverschiebung z")
    ax.set_ylabel("|Reihe / exakt − 1|")
    ax.set_title(f"ΛCDM mit Ω_m = {om:.2f}: Reihen gegen die exakte Entfernung", fontsize=10)
    ax.legend(fontsize=7, ncol=2, loc="upper left")
    ax = axes[1]
    ax.axhspan(q0_ref - q0_ref_err, q0_ref + q0_ref_err, color="tab:red", alpha=0.2, label=f"ΛCDM, alle Daten: q₀ = {q0_ref:.2f}".replace("-", "−"))
    ax.errorbar(res[:, 0], res[:, 1], yerr=res[:, 2], fmt="o-", color="black", capsize=3, label="Reihe in z, dritte Ordnung")
    ax.axvline(r_z, color="black", ls=":", lw=1)
    ax.set_xscale("log")
    ax.set_xticks(res[:, 0], [f"{v:g}" for v in res[:, 0]])
    ax.set_xlabel("größte Rotverschiebung der Auswahl")
    ax.set_ylabel("Abbremsung q₀")
    ax.set_title("Wenige Daten: großer Fehler. Viele Daten: Verzerrung durch den Abbruch", fontsize=10)
    ax.legend(fontsize=8, loc="lower left")
    fig.tight_layout()
    plt.show()
    return om, res
