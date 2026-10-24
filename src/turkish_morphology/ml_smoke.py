"""Explicit, opt-in BERTurk inference check; never imported by foundation commands."""

import argparse
from datetime import datetime, timezone
from importlib import metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from time import perf_counter
from uuid import uuid4

try:
    import resource
except ImportError:
    resource = None

from .config import load_config, require_pinned_models


def hardware():
    info = {"platform": platform.platform(), "architecture": platform.machine(),
            "cpu": platform.processor(), "logical_cpu_count": os.cpu_count()}
    if sys.platform == "darwin":
        for key, name in (("machdep.cpu.brand_string", "chip"), ("hw.memsize", "ram_bytes")):
            try:
                result = subprocess.run(["sysctl", "-n", key], capture_output=True,
                                        text=True, timeout=5, check=True)
                info[name] = result.stdout.strip()
            except (OSError, subprocess.SubprocessError) as exc:
                info[name] = {"unavailable": str(exc)}
    return info


def memory(torch, device):
    result = {"process_peak_rss": None, "process_peak_rss_unit": None}
    if resource is None:
        result["process_peak_rss_unavailable"] = "The resource module is unavailable on this platform."
    else:
        try:
            result["process_peak_rss"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            result["process_peak_rss_unit"] = "bytes" if sys.platform == "darwin" else "KiB"
        except (OSError, ValueError) as exc:
            result["process_peak_rss_unavailable"] = str(exc)
    if device == "mps":
        for name in ("current_allocated_memory", "driver_allocated_memory", "recommended_max_memory"):
            try:
                result[name + "_bytes"] = getattr(torch.mps, name)()
            except (AttributeError, RuntimeError) as exc:
                result[name] = {"unavailable": str(exc)}
    return result


def run_smoke(config_path, device, output, allow_download=False):
    config = load_config(config_path)
    selected = [m for m in config["models"] if m["name"] == "berturk"]
    if len(selected) != 1:
        raise ValueError("Exactly one berturk model is required.")
    model_config = dict(selected[0], enabled=True)
    require_pinned_models({"models": [model_config]})
    report = {"status": "failed", "created_at_utc": datetime.now(timezone.utc).isoformat(),
              "python": sys.version, "executable": sys.executable, "hardware": hardware(),
              "device": device, "checkpoint": model_config["checkpoint"],
              "model_revision": model_config["revision"],
              "tokenizer_revision": model_config["revision"],
              "allow_download": allow_download, "packages": {}}
    output.mkdir(parents=True, exist_ok=True)
    report_path = output / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid4().hex[:8] + ".json")
    try:
        for name in ("torch", "transformers", "tokenizers", "huggingface-hub", "safetensors", "numpy", "sentencepiece"):
            try:
                report["packages"][name] = metadata.version(name)
            except metadata.PackageNotFoundError:
                report["packages"][name] = None
        import torch
        if device == "mps":
            if os.environ.get("PYTORCH_ENABLE_MPS_FALLBACK") == "1":
                raise ValueError("Disable PYTORCH_ENABLE_MPS_FALLBACK; CPU fallback is forbidden.")
            if not torch.backends.mps.is_available():
                raise RuntimeError("MPS is unavailable; CPU fallback is forbidden.")
        from transformers import AutoModel, AutoTokenizer
        report["memory_before_load"] = memory(torch, device)
        kwargs = {"revision": model_config["revision"], "local_files_only": not allow_download}
        start = perf_counter()
        tokenizer = AutoTokenizer.from_pretrained(model_config["checkpoint"], **kwargs)
        model = AutoModel.from_pretrained(model_config["checkpoint"], use_safetensors=True, **kwargs)
        model.eval()
        model.to(device)
        if device == "mps":
            torch.mps.synchronize()
        report["model_and_tokenizer_loading_seconds"] = perf_counter() - start
        sentence = "Bugün İstanbul'da güzel bir gün geçiriyoruz."
        inputs = tokenizer(sentence, return_tensors="pt", truncation=False)
        inputs = {key: value.to(device) for key, value in inputs.items()}
        token_count = inputs["input_ids"].shape[1]
        report.update(sentence=sentence, token_count=token_count,
                      tokenizer_class=type(tokenizer).__name__, model_class=type(model).__name__)
        if device == "mps":
            torch.mps.synchronize()
        start = perf_counter()
        with torch.inference_mode():
            outputs = model(**inputs)
        if device == "mps":
            torch.mps.synchronize()
        report["forward_seconds"] = perf_counter() - start
        hidden = outputs.last_hidden_state
        expected = (1, token_count, model.config.hidden_size)
        if tuple(hidden.shape) != expected:
            raise ValueError(f"Unexpected hidden shape: {tuple(hidden.shape)} != {expected}")
        checked = {}
        for name, value in outputs.items():
            if torch.is_tensor(value):
                if value.device.type != device:
                    raise ValueError(f"{name} is on {value.device}, expected {device}")
                if not torch.isfinite(value).all().item():
                    raise ValueError(f"Non-finite values in {name}")
                checked[name] = list(value.shape)
        report.update(status="passed", output_shapes=checked,
                      memory_after_forward=memory(torch, device))
    except Exception as exc:
        report["error"] = {"type": type(exc).__name__, "message": str(exc)}
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report_path, report["status"] == "passed"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/pilot.toml"))
    parser.add_argument("--device", choices=("cpu", "mps"), required=True)
    parser.add_argument("--output", type=Path, default=Path("results/ml-smoke"))
    parser.add_argument("--allow-download", action="store_true", help="Explicitly permit Hugging Face downloads")
    args = parser.parse_args(argv)
    try:
        path, passed = run_smoke(args.config, args.device, args.output, args.allow_download)
        print(f"{'Passed' if passed else 'Failed'}: {path}")
        return 0 if passed else 1
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
