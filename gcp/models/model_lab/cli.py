"""Command line: uv run model-lab <command> --help"""

import argparse
from datetime import datetime
from pathlib import Path

from . import benchmark, clients, config, evaluation, garden

DEFAULT_COMPARISON = ["gemini-3.8-flash", "deepseek"]


def cmd_models(args) -> None:
    for short, model_id in config.MODELS.items():
        print(f"{short:14} {model_id}")


def cmd_ask(args) -> None:
    if args.sdk == "openai":
        print(clients.ask_openai(args.model, args.prompt))
    else:
        print(clients.ask_genai(args.model, args.prompt, tuned=args.tuned, system_instruction=args.system))


def cmd_speed(args) -> None:
    prompts = {k: v for k, v in benchmark.SPEED_PROMPTS.items() if not args.category or k == args.category}
    table, outputs = benchmark.speed_benchmark(clients.genai_client(), args.models, prompts)
    print("\n" + table.to_string(index=False))
    if args.judge and len(args.models) >= 2:
        for category, answers in outputs.items():
            a, b = (answers.get(m) for m in args.models[:2])
            if a and b:
                print(f"\n⚖️ Richter ({args.judge}) – {category}: A = {args.models[0]}, B = {args.models[1]}")
                print(evaluation.judge_pairwise(clients.genai_client(), prompts[category], a, b, args.judge))


def cmd_latency(args) -> None:
    print(f"🚀 {args.model}: {args.runs} Läufe")
    runs = benchmark.latency_runs(clients.genai_client(), args.model, args.prompt, args.runs)
    if runs.empty:
        raise SystemExit("Keine erfolgreichen Läufe.")
    print("\n" + benchmark.latency_stats(runs).to_string(index=False))
    if not args.no_plot:
        name = f"latency_{config.resolve(args.model).split('/')[-1]}_{datetime.now():%Y%m%d-%H%M%S}.png"
        print("Plot:", benchmark.plot_latency(runs, args.model, Path("results") / name))


def cmd_evaluate(args) -> None:
    prompts = evaluation.EVAL_PROMPTS[: args.limit]
    print(f"Rubrik-Evaluation: {len(prompts)} Prompts, Modelle {args.models}")
    result = evaluation.rubric_comparison(args.models, prompts)
    print("\n" + evaluation.summarize(result, args.models))


def cmd_garden(args) -> None:
    if args.action == "options":
        print(garden.deploy_options(args.model_id))
        return
    spec = dict(garden.DEFAULT_DEPLOYMENT, machine_type=args.machine, accelerator_type=args.accelerator,
                accelerator_count=args.count)
    endpoint = args.endpoint or args.model_id.split("@")[-1] + "-endpoint"
    print(f"Deploy {args.model_id} -> {endpoint} in {config.DEPLOY_PROJECT}/{config.DEPLOY_REGION}: {spec}")
    if not args.yes:
        raise SystemExit("⚠️  Kostet ab sofort GPU-Stunden, bis der Endpoint gelöscht wird. Zum Ausführen --yes angeben.")
    result = garden.deploy(args.model_id, endpoint_display_name=endpoint, **spec)
    print("✅ Endpoint:", getattr(result, "resource_name", result))


def main() -> None:
    parser = argparse.ArgumentParser(prog="model-lab", description="Models on Google Cloud: call, benchmark, evaluate, deploy.")
    sub = parser.add_subparsers(required=True)

    p = sub.add_parser("models", help="model catalog (short names)")
    p.set_defaults(func=cmd_models)

    p = sub.add_parser("ask", help="one prompt to one model")
    p.add_argument("model", help="short name (see 'models') or full model ID")
    p.add_argument("prompt")
    p.add_argument("--sdk", choices=["genai", "openai"], default="genai")
    p.add_argument("--tuned", action="store_true", help="GenAI SDK with all generation parameters set (temperature, top_p, ...)")
    p.add_argument("--system", help="system instruction (GenAI SDK)")
    p.set_defaults(func=cmd_ask)

    p = sub.add_parser("speed", help="TTFT, total time, tokens and TPS per model and prompt category")
    p.add_argument("--models", nargs="+", default=DEFAULT_COMPARISON)
    p.add_argument("--category", choices=list(benchmark.SPEED_PROMPTS), help="only this category")
    p.add_argument("--judge", metavar="MODEL", help="let MODEL compare the answers of the first two models")
    p.set_defaults(func=cmd_speed)

    p = sub.add_parser("latency", help="N runs of one model: percentiles P50-P99 and a plot in results/")
    p.add_argument("--model", default="deepseek")
    p.add_argument("--runs", type=int, default=10)
    p.add_argument("--prompt", default=benchmark.LATENCY_PROMPT)
    p.add_argument("--no-plot", action="store_true")
    p.set_defaults(func=cmd_latency)

    p = sub.add_parser("evaluate", help="rubric-based quality comparison (Gen AI evaluation service)")
    p.add_argument("--models", nargs="+", default=DEFAULT_COMPARISON)
    p.add_argument("--limit", type=int, default=len(evaluation.EVAL_PROMPTS), help="number of prompts (cost)")
    p.set_defaults(func=cmd_evaluate)

    p = sub.add_parser("garden", help="Model Garden: deployment options or deploy (costs!)")
    p.add_argument("action", choices=["options", "deploy"])
    p.add_argument("model_id", nargs="?", default="google/gemma4@gemma-4-26b-a4b-it")
    p.add_argument("--machine", default=garden.DEFAULT_DEPLOYMENT["machine_type"])
    p.add_argument("--accelerator", default=garden.DEFAULT_DEPLOYMENT["accelerator_type"])
    p.add_argument("--count", type=int, default=garden.DEFAULT_DEPLOYMENT["accelerator_count"])
    p.add_argument("--endpoint", help="endpoint display name")
    p.add_argument("--yes", action="store_true", help="really deploy")
    p.set_defaults(func=cmd_garden)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
