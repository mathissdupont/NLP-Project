# Working on this research project

Start with [the team plan](docs/TEAM_PLAN.md), [the research protocol](docs/RESEARCH_PROTOCOL.md), and [the data contract](docs/DATA_SPEC.md).

Work is tracked in [the issue index](docs/ISSUE_INDEX.md) and [GitHub tracker #1](https://github.com/mathissdupont/NLP-Project/issues/1). Follow the [issue/PR workflow](docs/GITHUB_WORKFLOW.md) for native blockers, owner labels, peer review, and CI.

## Local setup

Run from the repository root. The foundation requires Python 3.11 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m turkish_morphology check-config configs/pilot.toml
.\.venv\Scripts\python.exe -m turkish_morphology validate-data data/examples/nominal.jsonl
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

On macOS/Linux, replace `.\.venv\Scripts\python.exe` with `.venv/bin/python`. Activation is optional. The example dataset is illustrative and intentionally fails release validation.

Install the optional model stack only when implementing extraction/probing:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[ml]"
```

The foundation and ML environments are distinct milestones. Record and lock the actual working ML environment after a hardware-compatible pilot; declaring optional dependencies does not establish that they work together on every Python/CUDA combination. See [environment records](requirements/README.md).

## Collaboration

Use issue-numbered branches such as `data/5-nonce-pilot`, `models/8-token-alignment`, or `eval/12-linear-probe`. Link completed work with `Closes #NUMBER` in the PR and use Draft PRs while prerequisite work remains. A work package is complete when its code, relevant scientific checks, documentation, and reviewer feedback are resolved. Each member reviews the adjacent work package listed in the team plan.

The public repository is [mathissdupont/NLP-Project](https://github.com/mathissdupont/NLP-Project), with `main` as the default branch and `origin` as the shared remote. Clone it to work locally:

```text
git clone https://github.com/mathissdupont/NLP-Project.git
cd NLP-Project
```

Review changes through local diffs and GitHub pull requests. Do not edit frozen data or overwrite a completed run: create a new version/run and describe the reason. Keep test data out of hyperparameter tuning and manual model selection.

Implementation belongs in `src/turkish_morphology/`; notebooks explore and visualize reusable outputs. Keep machine-specific paths out of configuration. Run the foundation checks before handing off changes and add targeted tests for errors that would invalidate scientific conclusions.

## Research records

- Record design changes in [DECISIONS.md](docs/DECISIONS.md), including whether test results were already inspected.
- Track actual contributions in [CONTRIBUTIONS.md](docs/CONTRIBUTIONS.md); a planned task is not completed work.
- Add papers to [LITERATURE_REVIEW.md](docs/LITERATURE_REVIEW.md) and verified citations to `paper/references.bib`.
- Record sources and redistribution terms in `data/source_registry.json` before accepting data.
- Run `validate-data PATH --release` before freezing a dataset. This checks structure and selected integrity constraints, not linguistic correctness or every research-design requirement.
- Keep large/raw files and model caches outside Git. Small approved data releases and split manifests can later be explicitly tracked after provenance review.

No project license or publication venue has been selected yet.
