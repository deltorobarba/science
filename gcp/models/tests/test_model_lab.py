"""Offline tests: no Google Cloud calls."""

from types import SimpleNamespace

import google.auth
import pandas as pd
import pytest

from model_lab import benchmark, clients, config, evaluation


def fake_clock(*times):
    values = iter(times)
    return lambda: next(values)


def chunk(text, usage=None):
    return SimpleNamespace(text=text, usage_metadata=usage)


def test_measure_stream_ttft_total_tokens_and_tps():
    usage = SimpleNamespace(prompt_token_count=12, candidates_token_count=100, thoughts_token_count=40)
    chunks = [chunk("Hallo "), chunk("Welt"), chunk(None, usage)]
    # clock: first chunk at 2 s, end at 12 s (start = 0)
    result = benchmark.measure_stream(chunks, start=0.0, clock=fake_clock(2.0, 12.0))
    assert result.ttft == 2.0
    assert result.total == 12.0
    assert result.text == "Hallo Welt"
    assert (result.output_tokens, result.thinking_tokens) == (100, 40)
    assert result.tokens_per_second == pytest.approx(10.0)  # 100 tokens in the 10 s after the first chunk


def test_measure_stream_without_chunks():
    result = benchmark.measure_stream([], start=0.0, clock=fake_clock(3.0))
    assert result.ttft is None and result.tokens_per_second is None


def test_latency_stats_median_is_not_the_mean():
    runs = pd.DataFrame({"TTFT (s)": [0.3] * 9 + [5.0], "Gesamtzeit (s)": [1.0] * 9 + [6.0]})
    stats = benchmark.latency_stats(runs).set_index("Metrik")
    assert stats.loc["P50 (Median)", "TTFT (s)"] == 0.3
    assert stats.loc["Mean", "TTFT (s)"] == pytest.approx(0.77)  # one outlier pulls the mean up
    assert stats.loc["Max", "Gesamtzeit (s)"] == 6.0


def test_resolve_short_names_and_full_ids():
    assert config.resolve("deepseek") == "deepseek-ai/deepseek-v4.1-flash-maas"
    assert config.resolve("gemini-3.8-flash") == "gemini-3.8-flash"


def test_openai_client_uses_vertex_endpoint_and_access_token(monkeypatch):
    class FakeCredentials:
        token = "ya29.test"

        def refresh(self, request):
            pass

    monkeypatch.setattr(google.auth, "default", lambda scopes=None: (FakeCredentials(), "p"))
    monkeypatch.setattr(config, "PROJECT_ID", "my-project")
    monkeypatch.setattr(config, "MODEL_LOCATION", "global")
    client = clients.openai_client()
    assert str(client.base_url).startswith(
        "https://aiplatform.googleapis.com/v1/projects/my-project/locations/global/endpoints/openapi")
    assert client.api_key == "ya29.test"


def test_judge_prompt_contains_question_and_both_answers():
    text = evaluation.judge_prompt("Frage?", "Antwort eins", "Antwort zwei")
    assert "Frage?" in text and "Antwort eins" in text and "Antwort zwei" in text
