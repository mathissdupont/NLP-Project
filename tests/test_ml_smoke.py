"""Offline smoke-command regressions; no ML packages or model downloads required."""

from contextlib import nullcontext
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from turkish_morphology import ml_smoke


REPO = Path(__file__).resolve().parents[1]


class SmokePortabilityTests(unittest.TestCase):
    def test_help_imports_no_ml_packages(self):
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(REPO / "src") + os.pathsep + environment.get("PYTHONPATH", "")
        result = subprocess.run(
            [sys.executable, "-c", (
                "import sys; from turkish_morphology import ml_smoke; "
                "assert 'torch' not in sys.modules; "
                "assert 'transformers' not in sys.modules; "
                "ml_smoke.main(['--help'])"
            )],
            cwd=REPO, env=environment, capture_output=True, text=True, timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--device", result.stdout)

    def test_unavailable_rss_does_not_require_resource(self):
        with patch.object(ml_smoke, "resource", None):
            measurement = ml_smoke.memory(None, "cpu")
        self.assertIsNone(measurement["process_peak_rss"])
        self.assertIsNone(measurement["process_peak_rss_unit"])
        self.assertIn("process_peak_rss_unavailable", measurement)

    def test_failed_rss_query_is_reported_without_aborting(self):
        fake_resource = SimpleNamespace(RUSAGE_SELF=0, getrusage=Mock(side_effect=OSError("query unavailable")))
        with patch.object(ml_smoke, "resource", fake_resource):
            measurement = ml_smoke.memory(None, "cpu")
        self.assertIsNone(measurement["process_peak_rss"])
        self.assertIn("query unavailable", measurement["process_peak_rss_unavailable"])

    def test_unix_rss_preserves_platform_units(self):
        fake_resource = SimpleNamespace(RUSAGE_SELF=0, getrusage=Mock(return_value=SimpleNamespace(ru_maxrss=123)))
        for platform, unit in (("darwin", "bytes"), ("linux", "KiB")):
            with self.subTest(platform=platform), patch.object(ml_smoke, "resource", fake_resource), patch.object(ml_smoke.sys, "platform", platform):
                measurement = ml_smoke.memory(None, "cpu")
            self.assertEqual(measurement["process_peak_rss"], 123)
            self.assertEqual(measurement["process_peak_rss_unit"], unit)

    def test_missing_rss_preserves_mps_counters(self):
        torch = SimpleNamespace(mps=SimpleNamespace(
            current_allocated_memory=lambda: 1,
            driver_allocated_memory=lambda: 2,
            recommended_max_memory=lambda: 3,
        ))
        with patch.object(ml_smoke, "resource", None):
            measurement = ml_smoke.memory(torch, "mps")
        self.assertIsNone(measurement["process_peak_rss"])
        self.assertEqual(measurement["current_allocated_memory_bytes"], 1)
        self.assertEqual(measurement["driver_allocated_memory_bytes"], 2)

    def test_cpu_path_can_finish_without_resource_and_without_downloads(self):
        class Tensor:
            def __init__(self, shape):
                self.shape = shape
                self.device = SimpleNamespace(type="cpu")

            def to(self, device):
                if device != "cpu":
                    raise AssertionError("This fixture only supports CPU.")
                return self

        class Outputs(dict):
            @property
            def last_hidden_state(self):
                return self["last_hidden_state"]

        # These objects exercise command/report flow, not actual model inference.
        torch = SimpleNamespace(
            inference_mode=nullcontext,
            is_tensor=lambda value: isinstance(value, Tensor),
            isfinite=lambda value: SimpleNamespace(all=lambda: SimpleNamespace(item=lambda: True)),
        )
        tokenizer = Mock(return_value={"input_ids": Tensor((1, 3)), "attention_mask": Tensor((1, 3))})
        model = Mock(return_value=Outputs(last_hidden_state=Tensor((1, 3, 4))))
        model.config = SimpleNamespace(hidden_size=4)
        tokenizer_loader = Mock(return_value=tokenizer)
        model_loader = Mock(return_value=model)
        transformers = SimpleNamespace(
            AutoTokenizer=SimpleNamespace(from_pretrained=tokenizer_loader),
            AutoModel=SimpleNamespace(from_pretrained=model_loader),
        )
        with TemporaryDirectory() as directory, patch.object(ml_smoke, "resource", None), patch.object(ml_smoke, "hardware", return_value={"fixture": True}), patch.dict(sys.modules, {"torch": torch, "transformers": transformers}):
            path, passed = ml_smoke.run_smoke(REPO / "configs/pilot.toml", "cpu", Path(directory))
            report = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(passed)
        self.assertEqual(report["status"], "passed")
        self.assertIsNone(report["memory_after_forward"]["process_peak_rss"])
        self.assertFalse(report["allow_download"])
        self.assertTrue(tokenizer_loader.call_args.kwargs["local_files_only"])
        self.assertTrue(model_loader.call_args.kwargs["local_files_only"])
        self.assertEqual(tokenizer_loader.call_args.kwargs["revision"], model_loader.call_args.kwargs["revision"])
        model.eval.assert_called_once()
        model.to.assert_called_once_with("cpu")


if __name__ == "__main__":
    unittest.main()
