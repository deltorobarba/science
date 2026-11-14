"""Komplexe Netzwerke: Erdős-Rényi, Watts-Strogatz und Barabási-Albert, Riesenkomponente, kleine Welt, Spektren, Epidemien und Kuramoto-Synchronisation.

Für stochastics.ipynb aus complexnetworks.ipynb übernommen: Jede Funktion ist eine Zelle des alten Notebooks (Code wörtlich).
Die Funktionen teilen ihre Variablen über Modulvariablen wie die Zellen eines Notebooks und laufen deshalb
in dieser Reihenfolge: load, degree_distributions, giant_component, small_world, network_spectra, epidemics, kuramoto.
"""
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from scipy.integrate import trapezoid
from scipy.stats import poisson as poisson_dist


def load():
    """22. Daten (Zellen 4, 6 von complexnetworks.ipynb)."""
    global G, K_MEAN, N, N_vis, SEED, ax, axes, c, colors, deg, fig, giant_fraction
    global graphs, layout, layouts, models, name, pos, rng, small_graphs
    # Alles hier (numpy, networkx, matplotlib) ist in Colab vorinstalliert

    rng = np.random.default_rng(2)
    SEED = 2
    N, K_MEAN = 3000, 6

    def models(N, k_mean, seed=SEED):
        return {"Erdős–Rényi": nx.fast_gnp_random_graph(N, k_mean / (N - 1), seed=seed),
                "Watts–Strogatz (p = 0.1)": nx.watts_strogatz_graph(N, k_mean, 0.1, seed=seed),
                "Barabási–Albert (m = 3)": nx.barabasi_albert_graph(N, k_mean // 2, seed=seed)}

    def giant_fraction(G):
        return max((len(c) for c in nx.connected_components(G)), default=0) / G.number_of_nodes()

    graphs = models(N, K_MEAN)
    for name, G in graphs.items():
        deg = np.array([d for _, d in G.degree()])
        print(f"{name:26s}: {G.number_of_edges()} Kanten, ⟨k⟩ = {deg.mean():.2f}, ⟨k²⟩ = {np.mean(deg ** 2):.1f}, größter Grad {deg.max()}")

    # Visualisierung kleinerer Graphen (N = 30, ⟨k⟩ = 6), um die Topologie direkt zu erkennen
    N_vis = 100
    small_graphs = models(N_vis, K_MEAN)
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.6))
    colors = ["tab:blue", "tab:green", "tab:red"]
    layouts = ["spring", "circular", "spring"]

    for ax, (name, G), c, layout in zip(axes, small_graphs.items(), colors, layouts):
        deg = np.array([d for _, d in G.degree()])
        pos = nx.circular_layout(G) if layout == "circular" else nx.spring_layout(G, k=0.55, seed=SEED)
        nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.32, edge_color="gray", width=1.0)
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=25 + 22 * deg, node_color=c,
                               alpha=0.88, edgecolors="white", linewidths=0.8)
        ax.set_title(f"{name}\n⟨k⟩ = {deg.mean():.1f}, max k = {deg.max()}", fontsize=10)
        ax.axis("off")

    fig.suptitle(f"Topologischer Vergleich der drei Modelle (N = {N_vis}, Knotengröße ∝ Grad k)", fontsize=12)
    fig.tight_layout()
    plt.show()


def degree_distributions():
    """23. Gradverteilungen (Zellen 9 von complexnetworks.ipynb)."""
    global G, axes, c, ccdf, deg, deg_ba, fig, k_ref, kk, ks, name, slope
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    for (name, G), c in zip(graphs.items(), ["tab:blue", "tab:green", "tab:red"]):
        deg = np.array([d for _, d in G.degree()])
        ks = np.arange(1, deg.max() + 1)
        axes[0].plot(ks, [np.mean(deg == k) for k in ks], "o", ms=3, c=c, label=name)
        ccdf = [np.mean(deg >= k) for k in ks]
        axes[1].loglog(ks, ccdf, "-", c=c, label=name)
    kk = np.arange(1, 40)
    axes[0].plot(kk, poisson_dist.pmf(kk, K_MEAN), c="black", lw=1, label=f"Poisson, ⟨k⟩ = {K_MEAN}")
    axes[0].set_xlim(0, 30)
    axes[0].set_xlabel("Grad k")
    axes[0].set_ylabel("Anteil P(k)")
    axes[0].set_title("Gradverteilung (linear)")
    axes[0].legend(fontsize=8)
    k_ref = np.logspace(np.log10(3), 2, 50)
    axes[1].loglog(k_ref, (3 / k_ref) ** 2, c="black", ls="--", label="(m/k)², m = 3")
    axes[1].set_xlabel("Grad k")
    axes[1].set_ylabel("Anteil der Knoten mit Grad ≥ k")
    axes[1].set_title("Komplementäre Verteilungsfunktion (log-log)")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()

    deg_ba = np.array([d for _, d in graphs["Barabási–Albert (m = 3)"].degree()])
    ks = np.arange(6, 60)
    slope = np.polyfit(np.log(ks), np.log([np.mean(deg_ba >= k) for k in ks]), 1)[0]
    print(f"Barabási–Albert: Steigung der komplementären Verteilung zwischen k = 6 und 60: {slope:.2f}  "
          f"(Theorie −2, also P(k) ∝ k^{slope - 1:.2f})")


def giant_component():
    """24. Die Riesenkomponente (Zellen 12 von complexnetworks.ipynb)."""
    global S_sim, ax, fig, giant_theory, k, k_grid
    def giant_theory(k):
        S = 1.0
        for _ in range(500):
            S = 1 - np.exp(-k * S)
        return S if k > 1 else 0.0

    k_grid = np.linspace(0.1, 4, 30)
    S_sim = [np.mean([giant_fraction(nx.fast_gnp_random_graph(10_000, k / 9999, seed=s)) for s in range(5)]) for k in k_grid]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(k_grid, S_sim, "o", label="Simulation, N = 10 000")
    ax.plot(k_grid, [giant_theory(k) for k in k_grid], c="black", label="S = 1 − exp(−⟨k⟩S)")
    ax.axvline(1, color="tab:red", ls=":", label="Schwelle ⟨k⟩ = 1")
    ax.set_xlabel("mittlerer Grad ⟨k⟩")
    ax.set_ylabel("Anteil der Knoten in der größten Komponente")
    ax.set_title("Entstehung der Riesenkomponente im Erdős–Rényi-Graphen")
    ax.legend()
    fig.tight_layout()
    plt.show()
    for k in [0.5, 1.0, 1.5, 2.0, 3.0]:
        print(f"⟨k⟩ = {k}: Simulation {np.mean([giant_fraction(nx.fast_gnp_random_graph(10_000, k / 9999, seed=s)) for s in range(5)]):.3f}, Theorie {giant_theory(k):.3f}")


def small_world():
    """25. Die kleine Welt (Zellen 15 von complexnetworks.ipynb)."""
    global C0, Cs, G, L0, Ls, ax, fig, i, p, ps
    ps = np.logspace(-4, 0, 13)
    L0 = nx.average_shortest_path_length(nx.watts_strogatz_graph(1000, 10, 0.0, seed=SEED))
    C0 = nx.average_clustering(nx.watts_strogatz_graph(1000, 10, 0.0, seed=SEED))
    Ls, Cs = [], []
    for p in ps:
        G = nx.connected_watts_strogatz_graph(1000, 10, p, seed=SEED)
        Ls.append(nx.average_shortest_path_length(G) / L0)
        Cs.append(nx.average_clustering(G) / C0)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.semilogx(ps, Ls, "o-", label="mittlere Weglänge L(p)/L(0)")
    ax.semilogx(ps, Cs, "s-", label="Clusterkoeffizient C(p)/C(0)")
    ax.set_xlabel("Wahrscheinlichkeit p, eine Kante umzulegen")
    ax.set_ylabel("relativ zum Ring")
    ax.set_title("Watts–Strogatz: kurze Wege bei hoher Clusterung")
    ax.legend()
    fig.tight_layout()
    plt.show()
    print(f"Ring: L(0) = {L0:.1f} (N/2k = {1000 / 20:.0f}), C(0) = {C0:.3f} (3(k−2)/4(k−1) = {3 * 8 / 36:.3f})")
    i = np.argmin(np.abs(ps - 0.01))
    print(f"bei p = {ps[i]:.3f}: L/L(0) = {Ls[i]:.2f}, C/C(0) = {Cs[i]:.2f}")


def network_spectra():
    """26. Spektren: der Halbkreis im Zufallsgraphen und Gemeinschaften aus dem Fiedler-Vektor (Zellen 18 von complexnetworks.ipynb)."""
    global A, G_sbm, Lap, N_sp, P, V, accuracy, axes, ev, fiedler, fig, guess
    global order, p_sp, radius, sizes, truth, w, xs
    N_sp, p_sp = 2000, 0.01
    A = nx.to_numpy_array(nx.fast_gnp_random_graph(N_sp, p_sp, seed=SEED))
    ev = np.linalg.eigvalsh(A)
    radius = 2 * np.sqrt(N_sp * p_sp * (1 - p_sp))

    sizes, P = [200, 200], [[0.05, 0.01], [0.01, 0.05]]
    G_sbm = nx.stochastic_block_model(sizes, P, seed=SEED)
    truth = np.array([G_sbm.nodes[i]["block"] for i in G_sbm.nodes])
    Lap = nx.laplacian_matrix(G_sbm).toarray().astype(float)
    w, V = np.linalg.eigh(Lap)
    fiedler = V[:, 1]
    guess = (fiedler > 0).astype(int)
    accuracy = max(np.mean(guess == truth), np.mean(guess != truth))

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    axes[0].hist(ev[:-1], bins=60, density=True, alpha=0.6, label="Eigenwerte (ohne den größten)")
    xs = np.linspace(-radius, radius, 300)
    axes[0].plot(xs, 2 * np.sqrt(radius ** 2 - xs ** 2) / (np.pi * radius ** 2), c="black", label=f"Halbkreis, Radius 2√(Np(1−p)) = {radius:.2f}")
    axes[0].set_xlabel("Eigenwert der Adjazenzmatrix")
    axes[0].set_ylabel("Dichte")
    axes[0].set_title(f"Erdős–Rényi, N = {N_sp}, p = {p_sp}; größter Eigenwert {ev[-1]:.1f} (Np = {N_sp * p_sp:.0f})")
    axes[0].legend(fontsize=8)
    order = np.argsort(truth, kind="stable")
    axes[1].plot(fiedler[order], ".", ms=4)
    axes[1].axhline(0, color="black", lw=0.8)
    axes[1].axvline(200, color="tab:red", ls=":", label="Grenze der wahren Gruppen")
    axes[1].set_xlabel("Knoten (nach wahrer Gruppe sortiert)")
    axes[1].set_ylabel("Eintrag des Fiedler-Vektors")
    axes[1].set_title(f"Blockmodell: Vorzeichen ordnen {accuracy:.0%} der Knoten richtig zu")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()
    print(f"Adjazenz-Spektrum: Rand des Halbkreises {radius:.2f}, beobachtet {ev[-2]:.2f} bis {ev[0]:.2f}; größter Eigenwert {ev[-1]:.2f} ≈ Np + 1 = {N_sp * p_sp + 1:.0f}")
    print(f"Laplace-Spektrum des Blockmodells: kleinste Eigenwerte {np.round(w[:4], 3)}; Fiedler-Vektor ordnet {accuracy:.1%} richtig zu")


def epidemics():
    """27. Epidemien: Erdős–Rényi gegen skalenfrei (Zellen 21 von complexnetworks.ipynb)."""
    global G, Tc, Ts, ax, c, deg, fig, name, nets, percolated_giant, sizes_
    def percolated_giant(G, T, rng):
        keep = [e for e in G.edges() if rng.random() < T]
        H = nx.Graph()
        H.add_nodes_from(G.nodes())
        H.add_edges_from(keep)
        return giant_fraction(H)

    nets = {"Erdős–Rényi": nx.fast_gnp_random_graph(20_000, 4 / 19_999, seed=SEED),
            "Barabási–Albert": nx.barabasi_albert_graph(20_000, 2, seed=SEED)}
    Ts = np.linspace(0.0, 0.6, 31)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    for (name, G), c in zip(nets.items(), ["tab:blue", "tab:red"]):
        deg = np.array([d for _, d in G.degree()])
        Tc = deg.mean() / (np.mean(deg ** 2) - deg.mean())
        sizes_ = [np.mean([percolated_giant(G, T, rng) for _ in range(5)]) for T in Ts]
        ax.plot(Ts, sizes_, "o-", ms=3, c=c, label=f"{name}: ⟨k⟩ = {deg.mean():.1f}, ⟨k²⟩ = {np.mean(deg ** 2):.0f}")
        ax.axvline(Tc, color=c, ls=":", label=f"Schwelle T_c = ⟨k⟩/(⟨k²⟩ − ⟨k⟩) = {Tc:.3f}")
        print(f"{name:16s}: T_c (Theorie) = {Tc:.3f};  Endgröße bei T = 0.2: {np.mean([percolated_giant(G, 0.2, rng) for _ in range(5)]):.3f}")
    ax.set_xlabel("Transmissibilität T (Wahrscheinlichkeit der Übertragung pro Kante)")
    ax.set_ylabel("Anteil der Infizierten bei einem großen Ausbruch")
    ax.set_title("Epidemie als Kantenperkolation")
    ax.legend(fontsize=8)
    fig.tight_layout()
    plt.show()


def kuramoto():
    """28. Synchronisation: das Kuramoto-Modell (Zellen 24 von complexnetworks.ipynb)."""
    global K, K_fine, Kc, Ks, N_osc, ax, fig, kuramoto_r, omega, r_K, r_theory
    N_osc = 2000
    omega = rng.normal(0, 1, N_osc)
    Kc = 2 / (np.pi * (1 / np.sqrt(2 * np.pi)))

    def kuramoto_r(K, T=200.0, dt=0.05):
        theta = rng.uniform(0, 2 * np.pi, N_osc)
        rs = []
        for step in range(int(T / dt)):
            z = np.mean(np.exp(1j * theta))                        # r e^{iψ}
            theta += dt * (omega + K * np.abs(z) * np.sin(np.angle(z) - theta))
            if step * dt > T / 2:
                rs.append(np.abs(z))
        return np.mean(rs)

    Ks = np.linspace(0, 4, 21)
    r_K = [kuramoto_r(K) for K in Ks]
    K_fine = np.linspace(Kc, 4, 200)

    def r_theory(K):
        """Selbstkonsistenz r = K r ∫ cos²φ g(K r sin φ) dφ für die Normalverteilung, gelöst durch Bisektion."""
        phi = np.linspace(-np.pi / 2, np.pi / 2, 2001)
        g = lambda w: np.exp(-w ** 2 / 2) / np.sqrt(2 * np.pi)
        f = lambda r: K * trapezoid(np.cos(phi) ** 2 * g(K * r * np.sin(phi)), phi) - 1
        lo, hi = 1e-9, 1.0
        if f(lo) < 0:
            return 0.0
        for _ in range(60):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if f(mid) > 0 else (lo, mid)
        return lo

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(Ks, r_K, "o", label=f"Simulation, N = {N_osc}")
    ax.plot(K_fine, [r_theory(K) for K in K_fine], c="black", label="Selbstkonsistenz (N → ∞)")
    ax.axvline(Kc, color="tab:red", ls=":", label=f"K_c = 2/(π g(0)) = {Kc:.2f}")
    ax.set_xlabel("Kopplungsstärke K")
    ax.set_ylabel("Ordnungsparameter r")
    ax.set_title("Kuramoto: Einsetzen der Synchronisation")
    ax.legend()
    fig.tight_layout()
    plt.show()
    for K in [1.0, 2.0, 3.0]:
        print(f"K = {K}: Simulation r = {r_K[np.argmin(np.abs(Ks - K))]:.3f}, Theorie {r_theory(K):.3f}")
