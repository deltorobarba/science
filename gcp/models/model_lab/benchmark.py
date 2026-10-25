"""Speed and latency measurements over streaming responses.

TTFT (time to first token) is the time until the first streamed chunk arrives. For models that think
before answering it includes the thinking, which is why the token count of the thinking is recorded too.
"""

import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from . import config

SPEED_PROMPTS = {
    "Reasoning & Math": "Ein Zug fährt mit 120 km/h von A nach B (300 km). Ein zweiter Zug startet 30 Minuten später mit 150 km/h von B nach A. Wann und wo begegnen sie sich? Erkläre Schritt für Schritt.",
    "Code Generation": "Schreibe eine Python-Funktion mit Type Hints und Docstring, die einen Text einliest und die 3 häufigsten Wörter (ohne Stopwords) zurückgibt.",
    "Summarization": "Fasse die Kernunterschiede zwischen RAG (Retrieval-Augmented Generation) und Fine-Tuning in genau 3 prägnanten Bullet Points zusammen.",
}
LATENCY_PROMPT = "Erkläre kurz das Prinzip der Quantenverschränkung in genau 3 Sätzen."


@dataclass
class StreamResult:
    ttft: float | None
    total: float
    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    thinking_tokens: int | None = None

    @property
    def tokens_per_second(self) -> float | None:
        """Output tokens per second after the first chunk."""
        generation_time = self.total - (self.ttft or 0.0)
        if not self.output_tokens or generation_time <= 0:
            return None
        return self.output_tokens / generation_time


def measure_stream(chunks: Iterable, start: float, clock: Callable[[], float] = time.perf_counter) -> StreamResult:
    ttft, parts, last = None, [], None
    for chunk in chunks:
        if ttft is None:
            ttft = clock() - start
        if getattr(chunk, "text", None):
            parts.append(chunk.text)
        last = chunk
    total = clock() - start
    usage = getattr(last, "usage_metadata", None)
    return StreamResult(
        ttft=ttft,
        total=total,
        text="".join(parts),
        input_tokens=getattr(usage, "prompt_token_count", None),
        output_tokens=getattr(usage, "candidates_token_count", None),
        thinking_tokens=getattr(usage, "thoughts_token_count", None),
    )


def stream_once(client, model: str, prompt: str) -> StreamResult:
    start = time.perf_counter()
    return measure_stream(client.models.generate_content_stream(model=config.resolve(model), contents=prompt), start)


def speed_benchmark(client, models: list[str], prompts: dict[str, str]) -> tuple[pd.DataFrame, dict]:
    rows, outputs = [], {}
    for category, prompt in prompts.items():
        print(f"🚀 {category}")
        outputs[category] = {}
        for model in models:
            try:
                r = stream_once(client, model, prompt)
            except Exception as e:  # one failing model must not stop the comparison
                print(f"   ❌ {model}: {e}")
                continue
            outputs[category][model] = r.text
            tps = r.tokens_per_second
            rows.append({
                "Kategorie": category,
                "Modell": config.resolve(model).split("/")[-1],
                "TTFT (s)": round(r.ttft, 2) if r.ttft is not None else None,
                "Gesamtzeit (s)": round(r.total, 2),
                "Output Tokens": r.output_tokens,
                "Thinking Tokens": r.thinking_tokens,
                "TPS": round(tps, 1) if tps else None,
            })
            ttft = f"{r.ttft:.2f}s" if r.ttft is not None else "–"
            print(f"   ✅ {model}: TTFT {ttft}, gesamt {r.total:.2f}s, Thinking Tokens {r.thinking_tokens}")
    return pd.DataFrame(rows), outputs


def latency_runs(client, model: str, prompt: str, runs: int, pause: float = 1.0) -> pd.DataFrame:
    rows = []
    for i in range(1, runs + 1):
        try:
            r = stream_once(client, model, prompt)
            rows.append({"Run": i, "TTFT (s)": r.ttft if r.ttft is not None else r.total, "Gesamtzeit (s)": r.total})
            print(f"   Run {i:02d}/{runs}: TTFT {rows[-1]['TTFT (s)']:.2f}s | gesamt {r.total:.2f}s")
        except Exception as e:
            print(f"   ❌ Run {i}: {e}")
        if i < runs:
            time.sleep(pause)  # avoid API burst limits
    return pd.DataFrame(rows)


def latency_stats(runs: pd.DataFrame) -> pd.DataFrame:
    """Min, P50, mean, P90, P95, P99 and max per column. The median, not the mean, shows the typical run."""
    def column(values: pd.Series) -> list[float]:
        return [values.min(), np.percentile(values, 50), values.mean(), np.percentile(values, 90),
                np.percentile(values, 95), np.percentile(values, 99), values.max()]

    return pd.DataFrame({
        "Metrik": ["Min", "P50 (Median)", "Mean", "P90", "P95", "P99", "Max"],
        "TTFT (s)": column(runs["TTFT (s)"]),
        "Gesamtzeit (s)": column(runs["Gesamtzeit (s)"]),
    }).round(3)


def plot_latency(runs: pd.DataFrame, model: str, path: Path) -> Path:
    import matplotlib

    matplotlib.use("Agg")  # write a file, no window
    import matplotlib.pyplot as plt

    p50, p90 = np.percentile(runs["Gesamtzeit (s)"], 50), np.percentile(runs["Gesamtzeit (s)"], 90)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    ax1.plot(runs["Run"], runs["Gesamtzeit (s)"], marker="o", color="#E65100", label="Gesamtzeit (s)", linewidth=2)
    ax1.plot(runs["Run"], runs["TTFT (s)"], marker="s", color="#1E88E5", label="TTFT (s)", linewidth=2)
    ax1.axhline(p50, color="#E65100", linestyle="--", alpha=0.7, label=f"Gesamt P50 ({p50:.2f}s)")
    ax1.axhline(p90, color="#D32F2F", linestyle=":", alpha=0.8, label=f"Gesamt P90 ({p90:.2f}s)")
    ax1.set(title=f"Latenz über {len(runs)} Runs ({model})", xlabel="Run", ylabel="Zeit (s)")
    ax1.set_xticks(runs["Run"])  # whole runs only
    ax1.grid(True, linestyle="--", alpha=0.4)
    ax1.legend(loc="upper left")
    box = ax2.boxplot([runs["TTFT (s)"], runs["Gesamtzeit (s)"]], tick_labels=["TTFT", "Gesamtzeit"],
                      patch_artist=True, widths=0.4)
    for patch, color in zip(box["boxes"], ["#90CAF9", "#FFCC80"]):
        patch.set_facecolor(color)
    ax2.set(title="Verteilung (Boxplot)", ylabel="Zeit (s)")
    ax2.grid(True, linestyle="--", alpha=0.4)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path
