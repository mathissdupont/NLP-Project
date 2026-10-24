# Environment records

`pyproject.toml` defines a lightweight foundation dependency and an optional ML stack. The foundation can be tested independently of model downloads or GPUs.

`foundation-py314-windows.lock.txt` records the third-party foundation versions actually checked on Windows/Python 3.14.2. It is not an ML, CUDA, or cross-platform lockfile. Recreate that foundation with:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements/foundation-py314-windows.lock.txt
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
```

After the first successful extraction/probing pilot, create a separate tested ML environment record, including Python, package versions, platform, GPU/driver/CUDA where relevant, and exact model revisions. Keep failed environment combinations in the pilot notes. A `pip freeze` record alone cannot reproduce operating-system libraries or GPU determinism.

`ml-macos-arm64-py312-tested.txt` records the current ML environment associated
with the BERTurk CPU/MPS reports. See [Issue #7 validation](../docs/ISSUE_7_VALIDATION.md)
for results, reproduction commands, platform limits, and remaining gaps. This is
a version snapshot, not a hash-locked or cross-platform environment.
