"""Hauptachsen und Zufallsmatrizen für principal_axes.ipynb: wann eine Achse Signal ist, und PCA gegen Autoencoder.

Marchenko-Pastur-Gesetz (Eigenwerte reinen Rauschens), das Spiked-Modell mit der BBP-Schwelle (Baik, Ben Arous, Péché
2005: ab welcher Stärke ein Signal als eigene Achse aus dem Rauschen tritt), ein linearer Autoencoder in numpy (mit Adam
trainiert) und Hauptwinkel zwischen Unterräumen. Keine Downloads.
"""
import numpy as np
import matplotlib.pyplot as plt


def mp_edges(gamma, sigma2=1.0):
    """Ränder des Marchenko-Pastur-Bandes für γ = p/n ≤ 1: σ²(1 ∓ √γ)²."""
    return sigma2 * (1 - np.sqrt(gamma)) ** 2, sigma2 * (1 + np.sqrt(gamma)) ** 2


def mp_density(x, gamma, sigma2=1.0):
    """Dichte der Eigenwerte der Stichproben-Kovarianz von reinem Rauschen (p Merkmale, n Proben, γ = p/n)."""
    a, b = mp_edges(gamma, sigma2)
    x = np.asarray(x, dtype=float)
    out = np.zeros_like(x)
    m = (x > a) & (x < b)
    out[m] = np.sqrt((b - x[m]) * (x[m] - a)) / (2 * np.pi * sigma2 * gamma * x[m])
    return out


def sample_eigs(p, n, spike=0.0, seed=0):
    """Eigenwerte (absteigend) und oberster Eigenvektor der Stichproben-Kovarianz von n Proben aus N(0, I + spike·v vᵀ).

    v ist der erste Einheitsvektor; zurück kommt auch die Überlappung |⟨v̂, v⟩|² des obersten Eigenvektors mit v.
    """
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, p))
    X[:, 0] *= np.sqrt(1 + spike)
    w, V = np.linalg.eigh(X.T @ X / n)
    return w[::-1], V[0, -1] ** 2


def bbp_theory(spike, gamma):
    """Grenzwerte für n → ∞: oberster Eigenwert und Überlappung |⟨v̂, v⟩|², je nach Stärke ℓ über oder unter √γ."""
    l = np.asarray(spike, dtype=float)
    over = l > np.sqrt(gamma)
    top = np.where(over, (1 + l) * (1 + gamma / np.where(over, l, 1)), (1 + np.sqrt(gamma)) ** 2)
    overlap = np.where(over, (1 - gamma / np.where(over, l, 1) ** 2) / (1 + gamma / np.where(over, l, 1)), 0.0)
    return top, overlap


def spike_study(p, n, spikes, trials=20, show=(0.3, 1.0), seed=0):
    """Eigenwerte reinen Rauschens gegen Marchenko-Pastur und die Überlappung gegen die Stärke ℓ eines Signals."""
    gamma = p / n
    a, b = mp_edges(gamma)
    w0, _ = sample_eigs(p, n, seed=seed)
    print(f"p = {p} Merkmale, n = {n} Proben, γ = {gamma:.2f}: Marchenko-Pastur-Band {a:.2f} bis {b:.2f}, "
          f"gemessen {w0.min():.2f} bis {w0.max():.2f}; BBP-Schwelle √γ = {np.sqrt(gamma):.2f}")
    tops = {l: sample_eigs(p, n, l, seed=seed + 1)[0][0] for l in show}
    for l, t in tops.items():
        print(f"  Signal ℓ = {l}: oberster Eigenwert {t:.2f} (Theorie {bbp_theory(l, gamma)[0]:.2f})")
    over = np.array([[sample_eigs(p, n, l, seed=seed + 100 + t)[1] for t in range(trials)] for l in spikes])
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.6))
    axes[0].hist(w0, bins=40, density=True, color="lightgrey", edgecolor="grey", label="Eigenwerte, reines Rauschen")
    xx = np.linspace(0, b * 1.05, 400)
    axes[0].plot(xx, mp_density(xx, gamma), color="black", label="Marchenko-Pastur")
    for (l, t), c in zip(tops.items(), ["tab:blue", "tab:red"]):
        axes[0].axvline(t, color=c, lw=2, label=f"oberster Eigenwert mit Signal ℓ = {l}")
    axes[0].set_xlim(0, max(b, *tops.values()) * 1.08)
    axes[0].set_xlabel("Eigenwert der Stichproben-Kovarianz")
    axes[0].set_ylabel("Dichte")
    axes[0].set_title(f"Rauschen hat auch Achsen: {p} Merkmale, {n} Proben", fontsize=10)
    axes[0].legend(fontsize=8)
    ll = np.linspace(0.01, max(spikes), 300)
    axes[1].plot(ll, bbp_theory(ll, gamma)[1], color="black", label="Theorie (n → ∞)")
    axes[1].errorbar(spikes, over.mean(1), yerr=over.std(1), fmt="o", color="tab:red", ms=4, label=f"Simulation ({trials} Läufe)")
    axes[1].axvline(np.sqrt(gamma), color="grey", ls="--", lw=1, label=f"Schwelle √γ = {np.sqrt(gamma):.2f}")
    axes[1].set_xlabel("Stärke ℓ des Signals (Varianz entlang v ist 1 + ℓ)")
    axes[1].set_ylabel("|⟨v̂, v⟩|²: wie gut die oberste Achse v trifft")
    axes[1].set_title("BBP-Übergang: Unter der Schwelle zeigt die oberste Achse ins Leere", fontsize=10)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    plt.show()


# ---- Linearer Autoencoder gegen PCA

def pca_basis(X, k):
    """Die k obersten Hauptachsen (Spalten) der Zeilen von X (Proben × Merkmale, schon zentriert)."""
    return np.linalg.svd(X, full_matrices=False)[2][:k].T


def recon_error(X, W):
    """Mittlerer quadratischer Fehler je Probe, wenn X auf die Spalten von W projiziert wird (W orthonormal)."""
    return float(np.mean(np.sum((X - X @ W @ W.T) ** 2, axis=1)))


def linear_autoencoder(X, k, steps=3000, lr=0.01, seed=0):
    """Lineares Netz x → D E x mit Engpass k, trainiert mit Adam auf ½·mittlerem ‖x − D E x‖². Gibt E, D und den Verlauf."""
    rng = np.random.default_rng(seed)
    n, p = X.shape
    params = [rng.normal(scale=0.1, size=(k, p)), rng.normal(scale=0.1, size=(p, k))]
    m = [np.zeros_like(q) for q in params]
    v = [np.zeros_like(q) for q in params]
    verlauf = []
    for t in range(1, steps + 1):
        E, D = params
        Z = X @ E.T
        R = Z @ D.T - X                                  # Fehler der Rekonstruktion
        verlauf.append(float(np.mean(np.sum(R ** 2, axis=1))))
        gD = R.T @ Z / n
        gE = (R @ D).T @ X / n
        for i, g in enumerate([gE, gD]):
            m[i] = 0.9 * m[i] + 0.1 * g
            v[i] = 0.999 * v[i] + 0.001 * g * g
            params[i] = params[i] - lr * (m[i] / (1 - 0.9 ** t)) / (np.sqrt(v[i] / (1 - 0.999 ** t)) + 1e-8)
    return params[0], params[1], np.array(verlauf)


def principal_cosines(A, B):
    """Kosinus der Hauptwinkel zwischen den Spaltenräumen von A und B (1 = gleiche Richtung)."""
    qa, qb = np.linalg.qr(A)[0], np.linalg.qr(B)[0]
    return np.linalg.svd(qa.T @ qb, compute_uv=False)


def autoencoder_study(X, k, train_frac=0.7, steps=3000):
    """PCA und linearer Autoencoder auf den ersten `train_frac` der Proben, getestet auf dem Rest (spätere Zeiten)."""
    n_train = int(train_frac * len(X))
    mu = X[:n_train].mean(axis=0)
    Xtr, Xte = X[:n_train] - mu, X[n_train:] - mu
    W = pca_basis(Xtr, k)
    E, D, verlauf = linear_autoencoder(Xtr, k, steps=steps)
    Wae = np.linalg.qr(D)[0]
    cos = principal_cosines(W, D)
    mix = np.abs(W.T @ (D / np.linalg.norm(D, axis=0)))
    var_tr, var_te = np.mean(np.sum(Xtr ** 2, 1)), np.mean(np.sum(Xte ** 2, 1))
    print(f"{X.shape[1]} Merkmale, Training {n_train} Proben, Test {len(X) - n_train} spätere Proben, Engpass k = {k}")
    print(f"  Training: PCA erklärt {1 - recon_error(Xtr, W) / var_tr:.1%} der Varianz, Autoencoder "
          f"{1 - verlauf[-1] / var_tr:.1%} (nach {steps} Schritten)")
    print(f"  Test:     PCA {1 - recon_error(Xte, W) / var_te:.1%}, Autoencoder {1 - recon_error(Xte, Wae) / var_te:.1%}")
    print("  Kosinus der Hauptwinkel zwischen den Unterräumen: " + ", ".join(f"{c:.4f}" for c in cos))
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.6), gridspec_kw={"width_ratios": [1.6, 1]})
    axes[0].plot(np.arange(1, steps + 1), verlauf, color="tab:red", label="linearer Autoencoder (Training)")
    axes[0].set_ylim(0, verlauf[0] * 1.05)
    axes[0].axhline(recon_error(Xtr, W), color="black", ls="--", label=f"PCA mit {k} Achsen (Training)")
    axes[0].set_xlabel("Trainingsschritt (Adam)")
    axes[0].set_ylabel("mittlerer Fehler ‖x − x̂‖² je Probe")
    axes[0].set_title("Der Autoencoder lernt sich an das PCA-Optimum heran, nicht darunter", fontsize=10)
    axes[0].legend(fontsize=9)
    im = axes[1].imshow(mix, cmap="viridis", vmin=0, vmax=1)
    axes[1].set_xticks(range(k), [f"AE {i + 1}" for i in range(k)])
    axes[1].set_yticks(range(k), [f"PCA {i + 1}" for i in range(k)])
    axes[1].set_title("|Kosinus| zwischen PCA-Achsen und Autoencoder-Achsen", fontsize=10)
    fig.colorbar(im, ax=axes[1], fraction=0.046)
    fig.tight_layout()
    plt.show()
    return W, D
