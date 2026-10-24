"""Snapshot experiment inputs. This module never trains models or writes scores."""

from datetime import datetime, timezone
import hashlib
from importlib import metadata
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from uuid import uuid4

from .config import load_config, require_pinned_models
from .data.validation import load_jsonl, probe_training_records, validate_records


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_state(directory: Path) -> dict:
    def git(*arguments: str) -> str | None:
        try:
            result = subprocess.run(
                ["git", "-C", str(directory), *arguments],
                capture_output=True, text=True, check=False, timeout=10,
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except (OSError, subprocess.TimeoutExpired):
            return None

    status = git("status", "--porcelain")
    return {"commit": git("rev-parse", "HEAD"), "dirty": bool(status) if status is not None else None}


def prepare_run(config_path: Path, dataset_path: Path, sources_path: Path, output: Path) -> Path:
    config = load_config(config_path)
    require_pinned_models(config)
    if config["data"]["condition"] != "root_generalization":
        raise ValueError("Composition-holdout coverage auditing is not implemented; use a separately audited pipeline.")
    # Validate the copied bytes so that the manifest describes the actual run inputs.
    # No run is marked complete, even if all preparation checks pass.
    timestamp = datetime.now(timezone.utc)
    run_id = f"{timestamp:%Y%m%dT%H%M%S%fZ}-{uuid4().hex[:8]}"
    output.mkdir(parents=True, exist_ok=True)
    run_dir = output / run_id
    run_dir.mkdir()
    try:
        shutil.copyfile(config_path, run_dir / "config.toml")
        shutil.copyfile(dataset_path, run_dir / "dataset.jsonl")
        shutil.copyfile(sources_path, run_dir / "sources.json")
        snapshot_config = load_config(run_dir / "config.toml")
        require_pinned_models(snapshot_config)
        if snapshot_config != config:
            raise ValueError("Configuration changed during preparation; retry with stable inputs.")
        records = load_jsonl(run_dir / "dataset.jsonl")
        sources = json.loads((run_dir / "sources.json").read_text(encoding="utf-8-sig"))
        report = validate_records(records, release=True, sources=sources)
        if not report.valid:
            raise ValueError("Dataset is not releasable:\n" + "\n".join(report.errors))
        training = probe_training_records(records)
        environment = sorted(
            [{"name": dist.metadata["Name"], "version": dist.version} for dist in metadata.distributions()],
            key=lambda item: (item["name"] or "").lower(),
        )
        manifest = {
            "manifest_version": "0.1.0",
            "run_id": run_id,
            "status": "prepared",
            "created_at_utc": timestamp.isoformat(),
            "experiment": snapshot_config["experiment"],
            "models": [model for model in snapshot_config["models"] if model["enabled"]],
            "inputs": {
                name: {"file": filename, "sha256": sha256(run_dir / filename)}
                for name, filename in (("config", "config.toml"), ("dataset", "dataset.jsonl"), ("sources", "sources.json"))
            },
            "dataset_summary": {
                "records": report.records, "roots": report.roots, "pairs": report.pairs,
                "split_counts": report.split_counts, "probe_training_records": len(training),
            },
            "code": git_state(config_path.resolve().parent),
            "environment": {"python": sys.version, "platform": platform.platform(), "packages": environment},
            "limitations": [
                "No training or evaluation has been performed.",
                "Revision format is checked; checkpoint existence and tokenizer identity are not verified online.",
                "Class/bundle support, main-test isolation, linguistic validity, and GPU determinism require separate audits.",
            ],
        }
        with (run_dir / "manifest.json").open("x", encoding="utf-8") as stream:
            json.dump(manifest, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    except Exception:
        # Preserve failure evidence without disguising it as a prepared experiment.
        (run_dir / "PREPARATION_FAILED.txt").write_text(
            "Preparation failed. No completed experiment or valid manifest is implied.\n", encoding="utf-8"
        )
        raise
    return run_dir
