# Opt-in BERTurk inference smoke check

This checks model loading and a single Turkish sentence on an explicitly selected
CPU or MPS device. It does not implement token alignment, pooling, dataset
extraction, probing, or Issue #8. It is outside automatic foundation discovery
and CI. Offline command/import/report regression tests run in CI, including a
Windows job, without ML packages or model downloads. A passing foundation suite
is not evidence of successful inference.

Run from the repository root with the ML environment interpreter:

```sh
PYTHONPATH=src .venv-ml/bin/python -m turkish_morphology.ml_smoke --device cpu
PYTHONPATH=src .venv-ml/bin/python -m turkish_morphology.ml_smoke --device mps
```

By default, these commands only use cached Hugging Face files and fail if the
pinned artifacts are missing. When model downloads are authorized, explicitly
add `--allow-download`. This can download full model weights. Implementation-time checks were offline;
subsequent CPU/MPS reports and their limits are documented in
[ISSUE_7_VALIDATION.md](ISSUE_7_VALIDATION.md).

Both AutoTokenizer and AutoModel receive the same checkpoint and exact revision
from the `berturk` entry in `configs/pilot.toml`. Safetensors weights are required.
The model runs in eval mode under inference_mode. The check validates the
last-hidden-state shape, finite tensor outputs, and output device. MPS must be
available; CPU fallback is never selected. Unset PYTORCH_ENABLE_MPS_FALLBACK
before requesting MPS if it was set to 1.

JSON reports default to Git-ignored `results/ml-smoke/`, with unique filenames.
They include status/errors, package/Python versions, hardware/device, revisions,
token count, combined tokenizer/model loading and device-transfer time, and a
single forward-pass time. MPS timings synchronize before and after the pass.
There is no warmup or benchmark claim. Memory includes process peak RSS (not
current RSS) and available MPS allocator/driver counters. Hardware-query failures
are recorded rather than replaced with assumed values. These measurements do not
represent total free system memory or guarantee reproducibility. `--output`
can select another directory; ensure that directory is ignored before use.

The optional Unix `resource` module supplies peak RSS when available. On Windows,
or if the query fails, RSS and its unit are JSON `null` and the report includes
`process_peak_rss_unavailable`. Missing RSS does not prevent CPU inference or
other available memory counters from being recorded.

On Windows, after installing the ML environment, run from PowerShell:

```powershell
.\.venv-ml\Scripts\python.exe -m turkish_morphology.ml_smoke --help
.\.venv-ml\Scripts\python.exe -m turkish_morphology.ml_smoke --device cpu
```

## Editable import diagnosis

Earlier installation failed before the project could be installed. At the time
of this implementation, pip metadata does show an editable project installation,
but importing without PYTHONPATH still fails. The editable .pth file contains
the correct src path and a real newline, but has macOS UF_HIDDEN set
(st_flags=32832; UF_HIDDEN=32768). This Python's site.addpackage explicitly skips
hidden .pth files. Consequently, src is absent from sys.path. This is an
environment file-attribute problem, not evidence of a pyproject packaging bug.
No environment file attributes were changed in this step.

Use the explicit PYTHONPATH commands above as a temporary workaround. A future
repair should clear UF_HIDDEN on the editable .pth file and verify import without
PYTHONPATH, using the same environment interpreter. Earlier failed installation
also explains why no import was possible before editable metadata existed.

Offline validation (no model loading):

```sh
PYTHONPATH=src .venv-ml/bin/python -B -m turkish_morphology.ml_smoke --help
PYTHONPATH=src .venv-ml/bin/python -B -m unittest discover -s tests -v
```
