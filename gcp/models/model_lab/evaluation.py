"""Two ways to judge answer quality: a pairwise LLM judge and rubric-based evaluation (Gen AI evaluation service).

Docs: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/evaluation-overview
"""

import pandas as pd
import vertexai

# Not `from vertexai import types`: in aiplatform 2.6 that re-exports the metric loaders of the new
# `agentplatform` package, which the vertexai evaluation client cannot resolve ("could not be resolved as an
# API Predefined Metric"). The loaders under vertexai._genai match the client.
from vertexai._genai.types import RubricMetric

from . import config

JUDGE_TEMPLATE = """
Du bist ein unparteiischer KI-Schiedsrichter. Bewerte die folgenden zwei Antworten auf die gegebene Frage.
Frage: {prompt}

--- Antwort A ---
{answer_a}

--- Antwort B ---
{answer_b}

Bewerte beide Antworten nach Genauigkeit, Struktur und Logik (Punkte 1-10).
Erkläre kurz deine Entscheidung und küre einen Gewinner (A, B oder Unentschieden).
"""

EVAL_PROMPTS = [
    "Explain the difference between correlation and causation, and provide a real-world example where confusing the two could lead to poor decision-making.",
    "Write a Python function that finds the longest palindromic substring in a given string. Include comments explaining your approach and time complexity.",
    "A train leaves Station A at 9:00 AM traveling at 60 mph toward Station B. Another train leaves Station B at 10:00 AM traveling at 80 mph toward Station A. If the stations are 280 miles apart, at what time do the trains meet?",
    "Analyze the ethical implications of using AI in hiring decisions. Present arguments from multiple perspectives and discuss potential safeguards.",
    "Translate the following sentence to French, Spanish, and German, then explain any cultural nuances that might affect the translation: 'The early bird catches the worm, but the second mouse gets the cheese.'",
    "Create a short story (200 words) that includes these elements: a mysterious package, a lighthouse keeper, and a revelation that changes everything. The story should have a clear beginning, middle, and end.",
    "Compare and contrast the economic theories of Adam Smith and Karl Marx. How would each theorist likely view modern gig economy platforms like Uber?",
    "Debug this code and explain what's wrong: def fibonacci(n): if n <= 1: return n else: return fibonacci(n-1) + fibonacci(n-2) + fibonacci(n-3)",
    "You're a manager and an employee consistently delivers excellent work but is frequently late to meetings. Write a constructive feedback message addressing this issue while maintaining morale.",
    "Explain how transformer architecture works in machine learning to someone with basic programming knowledge but no ML background. Use an analogy to clarify the concept of attention mechanisms.",
]


def judge_prompt(prompt: str, answer_a: str, answer_b: str) -> str:
    return JUDGE_TEMPLATE.format(prompt=prompt, answer_a=answer_a, answer_b=answer_b)


def judge_pairwise(client, prompt: str, answer_a: str, answer_b: str, judge_model: str) -> str:
    response = client.models.generate_content(model=config.resolve(judge_model), contents=judge_prompt(prompt, answer_a, answer_b))
    return response.text or ""


def rubric_comparison(models: list[str], prompts: list[str]):
    """Generate rubrics per prompt, let every model answer, then grade all answers against the rubrics."""
    client = vertexai.Client(project=config.PROJECT_ID, location=config.MODEL_LOCATION)
    with_rubrics = client.evals.generate_rubrics(
        src=pd.DataFrame({"prompt": prompts}),
        rubric_group_name="general_quality_rubrics",
        predefined_spec_name=RubricMetric.GENERAL_QUALITY,
    )
    datasets = []
    for model in models:
        print(f"   Inferenz: {model}")
        datasets.append(client.evals.run_inference(model=config.resolve(model), src=with_rubrics))
    return client.evals.evaluate(
        dataset=datasets,
        metrics=[RubricMetric.GENERAL_QUALITY(rubric_group_name="general_quality_rubrics")],
    )


def summarize(result, models: list[str]) -> str:
    """Plain-text summary of an EvaluationResult (the notebook used result.show())."""
    lines = []
    for metric in result.summary_metrics or []:
        lines.append(f"{metric.metric_name}: Mittelwert {metric.mean_score}, Pass-Rate {metric.pass_rate}, "
                     f"gültig {metric.num_cases_valid}/{metric.num_cases_total}")
    if result.win_rates:
        lines.append(f"Win rates ({' vs. '.join(models)}): {result.win_rates}")
    return "\n".join(lines) or "(keine Zusammenfassung im Ergebnis)"
