"""Command-line interface.

Examples:
    # Check a dataset for schema errors without running anything
    python -m evaluation_lab validate datasets/sample_eval_cases.jsonl

    # Grade recorded responses (offline)
    python -m evaluation_lab run datasets/sample_eval_cases.jsonl \\
        --responses datasets/sample_responses.jsonl --out results/

    # Query a local model served by LM Studio
    python -m evaluation_lab run datasets/sample_eval_cases.jsonl \\
        --base-url http://localhost:1234/v1 --model <model-name> --out results/
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .clients import OpenAICompatibleClient, ReplayClient
from .dataset import DatasetError, load_cases, load_responses
from .runner import render_markdown_report, run_evaluation, summarize, write_results_jsonl


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="evaluation_lab", description="AI Evaluation Lab runner")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="validate a dataset file")
    validate.add_argument("dataset")

    run = sub.add_parser("run", help="run an evaluation")
    run.add_argument("dataset")
    source = run.add_mutually_exclusive_group(required=True)
    source.add_argument("--responses", help="JSONL of recorded responses (offline)")
    source.add_argument("--base-url", help="OpenAI-compatible base URL, e.g. http://localhost:1234/v1")
    run.add_argument("--model", help="model name (required with --base-url)")
    run.add_argument("--out", default="results", help="output directory (default: results/)")
    run.add_argument("--title", default="Evaluation Report")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "validate":
            cases = load_cases(args.dataset)
            print(f"OK: {len(cases)} valid cases in {args.dataset}")
            return 0
        return _run(args)
    except DatasetError as exc:
        print(f"Dataset error: {exc}", file=sys.stderr)
        return 2


def _run(args: argparse.Namespace) -> int:
    cases = load_cases(args.dataset)

    if args.responses:
        client = ReplayClient(load_responses(args.responses))
        source_note = f"recorded responses from `{Path(args.responses).as_posix()}`"
    else:
        if not args.model:
            print("--model is required with --base-url", file=sys.stderr)
            return 2
        client = OpenAICompatibleClient(base_url=args.base_url, model=args.model)
        source_note = f"live model `{args.model}` at `{args.base_url}` (temperature 0)"

    results = run_evaluation(cases, client)

    out_dir = Path(args.out)
    write_results_jsonl(results, out_dir / "results.jsonl")
    report = render_markdown_report(results, title=args.title, source_note=source_note)
    (out_dir / "report.md").write_text(report, encoding="utf-8", newline="\n")

    print(json.dumps(summarize(results), indent=2))
    print(f"Wrote {out_dir / 'results.jsonl'} and {out_dir / 'report.md'}")
    # Exit code reflects evaluation outcome so CI can gate on it if desired.
    return 0 if all(r.passed for r in results) else 1
