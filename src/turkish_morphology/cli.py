"""Small, honest commands for the research foundation."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

from .config import load_config
from .data.validation import load_jsonl, validate_records
from .experiments import prepare_run


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Turkish morphology research foundation")
    commands = parser.add_subparsers(dest="command", required=True)
    config_parser = commands.add_parser("check-config", help="Check a proposed configuration; no models are loaded")
    config_parser.add_argument("config", type=Path)
    data_parser = commands.add_parser("validate-data", help="Validate JSONL structure and selected integrity constraints")
    data_parser.add_argument("dataset", type=Path)
    data_parser.add_argument("--release", action="store_true")
    data_parser.add_argument("--sources", type=Path, default=Path("data/source_registry.json"))
    run_parser = commands.add_parser("prepare-run", help="Snapshot approved inputs; does not perform training")
    run_parser.add_argument("--config", type=Path, required=True)
    run_parser.add_argument("--dataset", type=Path, required=True)
    run_parser.add_argument("--sources", type=Path, default=Path("data/source_registry.json"))
    run_parser.add_argument("--output", type=Path, default=Path("results/runs"))
    args = parser.parse_args(argv)
    try:
        if args.command == "check-config":
            config = load_config(args.config)
            enabled = [model for model in config["models"] if model["enabled"]]
            print(json.dumps({
                "valid": True, "experiment": config["experiment"]["name"],
                "enabled_models": enabled, "training_performed": False,
                "note": "Design validation only; pinned revisions and released data are needed for run preparation.",
            }, ensure_ascii=False, indent=2))
            return 0
        if args.command == "validate-data":
            sources = json.loads(args.sources.read_text(encoding="utf-8-sig"))
            report = validate_records(load_jsonl(args.dataset), release=args.release, sources=sources)
            print(json.dumps({"valid": report.valid, "release": args.release, **asdict(report)}, ensure_ascii=False, indent=2))
            return 0 if report.valid else 1
        run_dir = prepare_run(args.config, args.dataset, args.sources, args.output)
        print(f"Prepared inputs at {run_dir}; no training or evaluation performed.")
        return 0
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
