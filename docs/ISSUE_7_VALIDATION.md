# Issue #7 validation and pre-PR audit

Audit date: 2026-10-24 (Europe/Istanbul). The live GitHub Issue #7 description
was read with `gh issue view 7 --repo mathissdupont/NLP-Project --json title,body,state`.
This documents existing reports; inference was not rerun during this audit.

## Actual BERTurk reports

| Field | CPU | MPS |
| --- | --- | --- |
| Local report | `results/ml-smoke/20261024T170341-04cb5965.json` | `results/ml-smoke/20261024T170642-fa846760.json` |
| Start (Europe/Istanbul) | 2026-10-24 20:03:41 | 2026-10-24 20:06:42 |
| Status | passed | passed |
| Downloads permitted | true | false |
| Token count (including specials) | 12 | 12 |
| last_hidden_state | [1, 12, 768] | [1, 12, 768] |
| pooler_output | [1, 768] | [1, 768] |
| Tokenizer/model loading + device transfer (s) | 52.101770583 | 0.820384916 |
| Forward pass (s) | 0.076121875 | 0.697331083 |
| Process peak RSS before load (bytes) | 429326336 | 433684480 |
| Process peak RSS after forward (bytes) | 1074184192 | 498728960 |
| MPS tensor allocations before/after (bytes) | not applicable | 0 / 442780416 |
| MPS driver allocations before/after (bytes) | not applicable | 393216 / 1084882944 |
| MPS recommended maximum memory (bytes) | not applicable | 11453251584 |

Both reports identify `dbmdz/bert-base-turkish-cased`, with model and tokenizer
revision equal to `b6e1de16c983e0f2c70664591ea3f22810072608`, `BertTokenizer`,
`BertModel`, and input `Bugün İstanbul'da güzel bir gün geçiriyoruz.`
The smoke implementation checks finite tensor outputs, output device, and hidden
shape before recording passed. Reports contain shape summaries, not raw tensors;
this audit validates report consistency, not tensor values independently.

The CPU run permits downloads and is consistent with a first-download run, but
`allow_download=true` does not prove that files were actually downloaded. No
network/cache-hit log or byte count is present. The MPS report records
`allow_download=false`; the implementation uses local_files_only, so this is
cached loading. Loading measurements include tokenizer/model loading and device
transfer; they do not isolate network time.

These single runs have no warmup, repetitions, or comparable cache conditions.
They are not a reliable CPU/GPU benchmark and establish no speed ranking.
Process peak RSS is a process lifetime high-water mark, not current RSS or GPU
usage. MPS tensor/driver counters describe different allocations, not independent
physical memory pools. Apple M1 uses unified memory: do not sum these counters
with RSS. Recommended maximum memory is not measured free memory.

Report SHA-256 identities:

- CPU: `216e4f6ca8bdbb52e4eaf6f91b2fd1dca3e38bf78941cc39629b43c50dd8b7b1`
- MPS: `82521b710fada101f06087575ce92d5f8855c4da5dd521ff595ab9ddeaee5e48`

## Environment and reproduction

Both reports: Python 3.12.12, macOS 15.7.3 arm64, Apple M1, 8 logical CPUs,
17179869184 bytes RAM (16 GiB). Package versions agree:

| Package | Version |
| --- | --- |
| torch | 2.14.1 |
| transformers | 5.20.2 |
| tokenizers | 0.23.3 |
| huggingface-hub | 2.3.0 |
| safetensors | 0.8.0 |
| numpy | 2.5.4 |
| sentencepiece | 0.2.2 |

`requirements/ml-macos-arm64-py312-tested.txt` records the current complete
installed distribution versions, excluding the editable project. Current versions
of the seven report packages match the reports. This snapshot was collected at
audit time, not embedded in the original reports. `pip check` reports no broken
requirements. It is not a portable lockfile or a proof of fresh-environment
reproduction; package sources, wheel hashes and OS components are not locked.

CUDA is not applicable to this Apple M1 machine. Current PyTorch reports
`torch.version.cuda=None`, CUDA unavailable, and MPS built=True. The supplied
report establishes a successful prior MPS run; the audit sandbox currently
reports MPS available=False. Do not substitute the sandbox result for the prior
run or claim MPS works in every execution context. Metal/MPS drivers are supplied
with macOS; no separate driver version or Metal version was captured in the
reports. macOS 15.7.3 build 24G419 was recorded in the earlier hardware inventory.

To recreate on an appropriate Mac (installation/downloads are future actions):

```sh
/opt/homebrew/bin/python3.12 -m venv .venv-ml
.venv-ml/bin/python -m pip install -r requirements/ml-macos-arm64-py312-tested.txt
.venv-ml/bin/python -m pip install --no-deps -e .
.venv-ml/bin/python -m pip check
PYTHONPATH=src .venv-ml/bin/python -m turkish_morphology.ml_smoke --device cpu --allow-download
PYTHONPATH=src .venv-ml/bin/python -m turkish_morphology.ml_smoke --device mps
```

See ML_SMOKE.md for the editable .pth UF_HIDDEN problem and temporary PYTHONPATH
workaround. That issue remains unresolved in the current environment. A clean
reinstallation and full reproduction from this new snapshot were not performed.

## Hub content verification

On 2026-10-24 at 19:43:55–19:43:58 Europe/Istanbul, each model's Hub API
`/api/models/{id}/revision/main` supplied its SHA. A second request to
`/api/models/{id}/revision/{SHA}` returned the same SHA; its siblings listed the
files below. Small config.json and tokenizer_config.json files were read from
`/{id}/resolve/{SHA}/...`. Weight payloads were not downloaded for that check.
This records the earlier verification; Hub requests were not repeated here.

| Model | Verified SHA | Model artifacts | Tokenizer artifacts |
| --- | --- | --- | --- |
| dbmdz/bert-base-turkish-cased | b6e1de16c983e0f2c70664591ea3f22810072608 | config.json, model.safetensors, pytorch_model.bin | tokenizer_config.json, vocab.txt |
| google-bert/bert-base-multilingual-cased | 3f076fdb1ab68d5b2880cb87a0886f315b8146f8 | config.json, model.safetensors, pytorch_model.bin | tokenizer_config.json, tokenizer.json, vocab.txt |
| FacebookAI/xlm-roberta-base | e73636d4f797dec63c3081bb6ed5c7b0bb3f2089 | config.json, model.safetensors, pytorch_model.bin | tokenizer_config.json, tokenizer.json, sentencepiece.bpe.model |

All three model/tokenizer pairs can reference their shared pinned commit. Only
BERTurk has actual inference reports; mBERT/XLM-R inference is not claimed.

## Acceptance audit

| Live Issue #7 requirement | Evidence / assessment |
| --- | --- |
| CPU/GPU smoke, hardware, time/memory | Both passed reports above; MPS is the Apple GPU backend. |
| Determine all three commits and replace UNRESOLVED | Hub content verification above and configs/pilot.toml. |
| Record working dependencies/Python/CUDA/driver | Report versions + separate ML snapshot; CUDA not applicable; macOS known, separate Metal driver version not recorded. |
| Real BERTurk load and forward | Both report passed; not rerun in this audit. |
| Hashes verified against Hub contents | SHA-specific API lists and config reads, not merely regex checks. |
| ML outputs/environment tests separate from foundation | Dedicated module, explicit execution only; no ML imports in foundation command paths; reports and .venv-ml ignored. |

Core acceptance evidence is present. The change is suitable for reviewer
inspection, with the import workaround, sandbox MPS limitation and untested
fresh-environment reproduction disclosed. Do not describe this as a portable,
fully reproduced ML environment. Local JSON evidence is ignored and will not
appear in a PR: this tracked summary preserves metrics and hashes, but reviewers
need the original reports shared separately if independent artifact inspection
is required. No PR was opened; human review remains pending. Issue #8 extraction,
alignment and pooling are not implemented by this work.

## Executed pre-PR checks

- `PYTHONPATH=src .venv-ml/bin/python -B -m unittest discover -s tests -v`: 25 passed.
- `PYTHONPATH=src .venv-ml/bin/python -B -m turkish_morphology check-config configs/pilot.toml`: valid.
- `PYTHONPATH=src .venv-ml/bin/python -B -m turkish_morphology validate-data data/examples/nominal.jsonl`: staging valid, two records; not a research release.
- `PYTHONPATH=src .venv-ml/bin/python -B -m turkish_morphology.ml_smoke --help`: passed.
- Offline mock checks: importing smoke does not import torch/transformers; unavailable MPS produces a failed report, shared revisions and downloads-disabled default preserved. No actual inference in these checks.
- `.venv-ml/bin/python -B -m pip check`: no broken requirements (non-writable pip cache warning only).
- `git diff --check`: clean. Foundation lockfile unchanged.
- Both reports match `results/ml-smoke/` ignore rule; generated files remain local.
- Changed/untracked text scanned for private-key, GitHub/Hugging Face token and AWS access-key patterns: no matches. Pattern scanning is not a comprehensive secret audit.
- Branch remains `feature/issue-7-ml-environment`; only expected source, configuration, test, documentation and environment-record changes are visible. No commit, push or PR performed.
