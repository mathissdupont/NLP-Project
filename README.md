# Do Language Models Learn Turkish Morphology Compositionally or Lexically?

**A controlled, layer-wise probing study of Turkish morphological generalization in BERTurk, mBERT, and XLM-R.**

**Status:** Research design and tested infrastructure · **Course:** Natural Language Processing · **Language under study:** Turkish

**Repository:** [mathissdupont/NLP-Project](https://github.com/mathissdupont/NLP-Project)

> Can a model recover the grammatical structure of a Turkish word built from a root it is unlikely to have encountered before?

This project investigates whether morphological information in pretrained Transformer encoders transfers from real Turkish words to novel, linguistically plausible word forms. We compare representations of real and artificial (*nonce*) roots, probe individual model layers, and test generalization under controlled data splits.

The project begins as an undergraduate NLP course project, with the goal of developing a reproducible empirical study and an English-language research paper. The repository contains research plans, an installable Python foundation, data-integrity checks, configuration/run-record utilities, and a manuscript skeleton. Research datasets, encoder extraction, probe fitting, and empirical results are not yet available. All scientific experiments below are proposed.

**Navigate:** [Motivation](#motivation) · [Research questions](#research-questions) · [Experimental design](#experimental-design) · [Evaluation](#evaluation-and-interpretation) · [Roadmap](#roadmap) · [References](#references) · [Team](#team)

**Start working:** [Setup and contribution guide](CONTRIBUTING.md) · [Team assignments (Türkçe)](docs/TEAM_PLAN.md) · [Research protocol](docs/RESEARCH_PROTOCOL.md) · [Data contract](docs/DATA_SPEC.md) · [Literature matrix](docs/LITERATURE_REVIEW.md)

**Track work:** [Research tracker #1](https://github.com/mathissdupont/NLP-Project/issues/1) · [Issue/dependency index](docs/ISSUE_INDEX.md) · [Issue and PR workflow (Türkçe)](docs/GITHUB_WORKFLOW.md) · [Milestones](https://github.com/mathissdupont/NLP-Project/milestones)

## Quick start

From the repository root, with Python 3.11 or newer:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m turkish_morphology check-config configs/pilot.toml
.\.venv\Scripts\python.exe -m turkish_morphology validate-data data/examples/nominal.jsonl
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

On macOS/Linux use `.venv/bin/python` for the environment's interpreter. The lightweight foundation downloads no pretrained models. [CONTRIBUTING.md](CONTRIBUTING.md) explains the optional ML environment and workflow.

The included example records are illustrative, pending review, and unassigned. They pass staging validation and intentionally fail release validation. `configs/pilot.toml` starts with BERTurk enabled; checkpoint revisions are deliberately `UNRESOLVED` until verified.

## Motivation

Turkish provides a useful setting for studying morphological generalization: a single root can combine with multiple suffixes to express number, possession, case, and other grammatical distinctions. A model might represent these distinctions in ways that transfer to unfamiliar roots, while also benefiting from familiar word forms and surface patterns.

Consider the following illustrative nominal paradigm:

| Structure | Real-root example | Nonce-root example | Intended interpretation |
| --- | --- | --- | --- |
| Root | `göl` | `zöp` | A singular, unpossessed noun |
| Root + plural | `göller` | `zöpler` | Plural entities |
| Root + plural + 1PL possessive | `göllerimiz` | `zöplerimiz` | Our plural entities |
| Root + plural + 1PL possessive + ablative | `göllerimizden` | `zöplerimizden` | From our plural entities |

Here, `göl` means “lake”; `zöp` is an illustrative artificial root with no intended lexical meaning. It must pass the same screening as every other nonce candidate before inclusion in the dataset.

```text
zöp       + ler       + imiz        + den
ROOT        PLURAL      POSS.1PL      ABLATIVE
```

The plural suffix describes the possessed entities; the possessive suffix identifies a first-person plural possessor. These are separate annotation targets.

**Working distinction:** Compositional generalization means transferring morphological distinctions to new roots or held-out combinations of familiar morphemes. Lexical dependence means benefiting from familiar roots or complete word forms. These mechanisms can coexist; our experiments will measure generalization patterns rather than assume a strict either/or explanation.

## Research questions

| ID | Question | Planned evidence |
| --- | --- | --- |
| RQ1 | Does morphological information transfer from real words to nonce words? | Train probes on real-root forms; evaluate on held-out real-root and nonce-root forms. |
| RQ2 | Where is morphological information accessible within each encoder? | Compare the embedding output and every Transformer layer using the same probing protocol. |
| RQ3 | Do models generalize to new combinations of familiar morphemes? | Hold out selected feature bundles while retaining their constituent feature values in probe training. |
| RQ4 | How do suffix-chain length and tokenization relate to generalization? | Report scores by morphological complexity and tokenizer fragmentation, alongside surface-form baselines. |
| RQ5 | How do Turkish-specific and multilingual encoders differ? | Evaluate all three checkpoints on the same examples and split manifests. |

We hypothesize that nonce words and held-out combinations will be harder than familiar patterns, and that results will depend on layer, morphological feature, and subword segmentation. These are hypotheses to test, not reported findings.

## Positioning and intended contribution

[Ismayilzada et al. (2025)](https://aclanthology.org/2025.naacl-long.59/) already investigate morphological compositional generalization in Turkish and Finnish, including novel roots, using generative and discriminative tasks with instruction-tuned multilingual language models. Our study builds on this research direction.

Our intended focus is **layer-wise diagnostic probing of frozen pretrained encoders**, with explicit controls for root leakage, probe capacity, and tokenization. The planned outputs are:

- A documented real/nonce evaluation dataset with morphological annotations and reproducible splits.
- A comparison of morphological feature accessibility across BERTurk, mBERT, and XLM-R layers.
- An analysis of transfer gaps, held-out combinations, and surface-form confounds.
- Reproducible experiment configurations, analysis scripts, and a paper reporting positive, negative, or mixed findings.

The precise novelty claim will be refined after a broader literature review. No claim of being the first study is made here.

## Experimental design

### 1. Models

| Model | Planned checkpoint | Role |
| --- | --- | --- |
| BERTurk | [`dbmdz/bert-base-turkish-cased`](https://huggingface.co/dbmdz/bert-base-turkish-cased) | Turkish-specific encoder |
| mBERT | [`google-bert/bert-base-multilingual-cased`](https://huggingface.co/google-bert/bert-base-multilingual-cased) | Multilingual BERT encoder |
| XLM-R | [`FacebookAI/xlm-roberta-base`](https://huggingface.co/FacebookAI/xlm-roberta-base) | Multilingual XLM-RoBERTa encoder |

All encoders will remain frozen; only diagnostic classifiers will be trained. We will record checkpoint and tokenizer revisions and evaluate models sequentially to keep the initial study feasible.

These checkpoints differ in pretraining data, vocabulary, and model size. A performance difference alone will therefore not establish a causal effect of monolingual versus multilingual pretraining.

### 2. Dataset construction

The core study will use **controlled nominal inflection**. Verbal morphology will be a separate extension, so that tense and subject agreement are not incorrectly assigned to the nominal examples above.

| Scope | Targets | Notes |
| --- | --- | --- |
| Core | `Number` | Number of the noun: singular or plural. |
| Core | `Case` | Initially nominative, accusative, dative, locative, ablative, and genitive. |
| Core | Possession presence | A project-defined binary label; distinct from a UD feature named `Poss`. |
| Core | `Person[psor]`, `Number[psor]` | Person and number of the possessor; evaluated on possessed forms. |
| Extension | `Person`, `Number`, `Tense`, `Polarity` | A separately validated verbal dataset, if time permits. |

Feature names will follow [Universal Dependencies conventions](https://universaldependencies.org/treebanks/tr_gb/index.html) where applicable. The full annotation specification will state how absent, inapplicable, and ambiguous values are handled.

Planned construction procedure:

1. **Select real roots.** Assemble a documented noun inventory with source and license information. Begin with regular inflectional classes and record exclusions.
2. **Generate nonce candidates.** Produce pronounceable Turkish-like roots across vowel-harmony classes and root-ending types. Match real and nonce groups on relevant orthographic properties, including length and final-vowel class.
3. **Screen candidates.** Check roots and generated forms against the selected lexicon and available reference corpora. Reject known words, obvious proper names, and unintended recognizable forms; record the resources used.
4. **Generate paradigms.** Apply legal suffix order, vowel harmony, consonant alternations, and buffer consonants. Store underlying morphemes separately from their surface realizations.
5. **Validate and balance.** Review generated forms with Turkish-speaking annotators. Use a morphological tool such as [Zemberek](https://github.com/ahmetaa/zemberek-nlp) as an additional check where supported; failure to recognize an unknown root is not itself evidence of an invalid form. Balance feature values and document ambiguous or excluded forms.
6. **Freeze the dataset.** Save a versioned inventory, generation seed, split manifests, and validation decisions before running the main experiments.

**Nonce does not mean provably unseen during pretraining.** The full pretraining corpora may not be accessible, and artificial strings can occur accidentally. We will describe these forms as *screened nonce forms*, document the screening, and avoid claiming verified absence from pretraining.

The initial dataset size will be chosen after a pilot establishes annotation effort, class coverage, tokenization behavior, and compute cost. No sample counts are fixed yet.

The first implemented data contract supports regular roots whose surface stem equals the underlying root. Stem alternations require an explicit alignment extension before admission; the broader generation goals above will be implemented in stages. See [the versioned data specification](docs/DATA_SPEC.md).

### 3. Generalization splits

The terms *seen* and *unseen* below refer to **probe training**, not to encoder pretraining.

| Condition | Probe training | Evaluation | Purpose |
| --- | --- | --- | --- |
| Root generalization | Real-root forms | Different real roots with familiar feature bundles | Establish transfer beyond training-root identity. |
| Real-to-nonce transfer | The same real-root training set | Screened nonce roots with matched feature bundles | Measure transfer to artificial lexical material. |
| Composition holdout | Forms using selected feature bundles | Held-out bundles on unseen real and nonce roots | Test recombination of familiar morphological components. |

For the root-generalization and real-to-nonce conditions, training, development, and test roots will be disjoint. Every inflected form of a root will stay in one partition. Matched real/nonce root pairs will be assigned together, and any nonce forms derived from a real root will remain in that root's partition. Exact duplicate surface forms will be checked across partitions.

For composition holdouts, the held-out bundles will be absent from probe training, while every tested feature value and constituent morpheme remains represented there. Development will use separate held-out bundles; the test holdouts will not guide model selection. We will publish coverage checks so that an unseen combination is not confused with an unseen label.

The primary experiment will use isolated words to limit contextual cues. A later robustness check may use grammatical sentence templates. Such a check will separate template families across partitions and include context controls to assess whether surrounding words reveal the target label.

### 4. Representation extraction and probing

```text
Validated real / nonce paradigms
               ↓
      Frozen split manifests
               ↓
  Model-specific tokenization
               ↓
Frozen encoder: embedding output + every layer
               ↓
      Target-word subword pooling
               ↓
    One linear probe per feature and layer
               ↓
 Transfer, composition, and error analysis
```

- **Representation:** Mean-pool the target word's subword vectors at each layer, excluding special tokens. First-subword and last-subword pooling will be secondary ablations.
- **Layer indexing:** Treat the embedding output as layer 0 and record Transformer layers separately.
- **Probe:** Use regularized linear classifiers as the primary diagnostic probes. Tune regularization on development data with the same search budget across models and layers.
- **Training protocol:** Keep encoders in evaluation mode and use identical dataset partitions. Fit any preprocessing on probe-training data only.
- **Feature handling:** Train a separate classifier for each applicable target. Evaluate possessor person and number on possessed forms so that absence of possession cannot dominate their scores.
- **Model selection:** Select any headline layer using development data. Report all layer-wise test scores without presenting the best test layer as a preselected result.

### 5. Baselines and controls

| Baseline or control | What it helps assess |
| --- | --- |
| Majority-class predictor | Class imbalance and a minimum performance reference. |
| Character n-gram classifier | How much can be recovered directly from spelling and suffix patterns. |
| Tokenization-only features | Whether subword counts or lengths alone correlate with labels. |
| Layer-0 representation probe | How much information is already accessible before Transformer contextualization. |
| Randomly initialized encoder | What the architecture and tokenizer make accessible without learned encoder weights. |
| Consistent random word-type labels | Probe memorization capacity, following the control-task approach of Hewitt and Liang (2019). |

Word-type control labels will be fixed within each control run. To make memorization measurable, we will use a separately identified word-type-overlap diagnostic; root-disjoint random-label scores alone cannot measure memorization of training word types. This diagnostic will remain separate from the main generalization results.

Tokenizer pieces will not be treated as linguistic morphemes. We will record fragmentation for every model and inspect both stratified results and subsets with comparable fragmentation. Orthographic matching will not be assumed to equalize tokenization across models.

## Evaluation and interpretation

**Primary metric:** Macro-F1 for each morphological feature. We will also report accuracy, per-class scores, confusion matrices, and evaluation support counts. Different feature tasks will remain separate rather than being merged into one unexplained score.

For each model, layer, and feature, define the descriptive transfer gap:

```text
Transfer gap = Macro-F1(held-out real roots) − Macro-F1(nonce roots)
```

Both evaluations will use the same trained probe, comparable feature distributions, and the same label inventory. A smaller gap indicates closer performance on real and nonce forms; it is meaningful only alongside the absolute scores and baselines. A model performing poorly on both groups can also have a small gap.

The main analysis will include:

- **Layer profiles:** Feature-wise scores across encoder depth, for real and nonce forms.
- **Composition results:** Scores on held-out bundles, alongside simpler root-generalization conditions.
- **Complexity breakdowns:** Performance by suffix-chain length, harmony class, and relevant root-ending type.
- **Tokenization analysis:** Fragmentation distributions, associated error patterns, and comparisons with surface-form baselines.
- **Uncertainty:** A target of five seeded runs covering split/probe randomness, plus 95% confidence intervals from root-level bootstrap resampling. Matched real/nonce comparisons will resample root pairs together. Any reduced protocol will be disclosed.

**Interpretation boundary:** Successful probing shows that a classifier can recover a feature from a representation. It does not by itself show that the encoder uses that feature in a downstream decision, implements a human-like grammatical rule, or never memorizes words. Strong nonce and composition-holdout results, especially beyond surface-form and random-encoder baselines, would support a narrower claim of transferable morphological information. Weak transfer would establish a limitation under this protocol, not prove that lexical memorization is the only mechanism.

## Reproducibility and repository plan

The foundation is organized as follows. Subpackages for extraction, fitting, and statistical evaluation contain handoff notes; their scientific implementations remain to be written.

```text
NLP-Project/
├── README.md
├── CONTRIBUTING.md     # Setup, review, and handoff workflow
├── pyproject.toml      # Installable package and optional ML dependencies
├── configs/            # Proposed pilot configuration
├── data/
│   ├── raw/            # Source inventories and provenance
│   ├── processed/      # Validated forms and morphological annotations
│   ├── splits/         # Frozen split manifests (not yet generated)
│   ├── examples/       # Illustrative JSONL, not research observations
│   └── source_registry.json
├── docs/               # Team plan, protocol, data spec, literature, logs
├── src/turkish_morphology/
│   ├── cli.py          # Config checks, data validation, run preparation
│   ├── config.py       # Initial configuration contract
│   ├── experiments.py  # Input snapshots and prepared-run manifests
│   ├── resources/      # Versioned nominal JSON Schema
│   ├── data/           # Integrity checks and real-only training selector
│   ├── representations/ # Extraction work package
│   ├── probing/        # Classifier/baseline work package
│   └── evaluation/     # Metrics/statistics work package
├── tests/              # Leakage and reproducibility regression checks
├── requirements/       # Tested foundation environment record
├── notebooks/          # Exploratory analyses
├── results/            # Metrics, figures, and experiment manifests
└── paper/              # LaTeX manuscript skeleton and verified BibTeX
```

The foundation uses Python and JSON Schema validation. The intended model stack is PyTorch, Hugging Face Transformers, scikit-learn, and standard data-analysis libraries. Model-stack versions will be locked after a successful hardware-specific pilot; the foundation environment record does not imply that model extraction has been tested.

The available commands are:

```powershell
python -m turkish_morphology check-config configs/pilot.toml
python -m turkish_morphology validate-data data/processed/nominal-v0.jsonl --release
python -m turkish_morphology prepare-run --config configs/pilot.toml --dataset data/processed/nominal-v0.jsonl
```

The last two commands require a dataset that has not been built yet. `prepare-run` additionally requires verified commit revisions and approved source metadata; it snapshots config/data/sources, hashes them, and records environment/Git metadata with status `prepared`. It does not perform training or produce scores. Explicit `--dataset` input is authoritative for the snapshot even if the proposed config names another file.

Each experiment should record dataset hashes, split manifests, checkpoint/tokenizer revisions, random seeds, probe settings, pooling choices, dependency versions, hardware, runtime, and the code revision. Cached representations should identify the exact dataset and model revisions that produced them. Keep design changes in [the decision log](docs/DECISIONS.md) and completed work in [the contribution record](docs/CONTRIBUTIONS.md).

Source datasets, pretrained checkpoints, and generated project materials may have different licenses. Their provenance and redistribution terms will be documented before release. A project license has not yet been selected.

## Roadmap

- [x] Define the initial research question, candidate models, and experimental protocol.
- [x] Create the repository foundation, initial team plan, data contract, validation utilities, and manuscript skeleton.
- [ ] Review related work and refine the contribution relative to existing Turkish morphology studies.
- [ ] Finalize nominal feature definitions, ambiguity handling, and data-source licenses.
- [ ] Build and manually validate a small real/nonce pilot dataset.
- [ ] Run a BERTurk pilot with linear and surface-form baselines; estimate runtime and storage.
- [ ] Freeze dataset versions, root partitions, and composition holdouts.
- [ ] Implement reproducible extraction and probing across all three encoders.
- [ ] Complete control experiments, uncertainty estimates, and error analysis.
- [ ] Add verbal morphology and sentence-context experiments if the core study is complete.
- [ ] Write the manuscript and release the permitted data, code, and result artifacts.

## Paper direction

The working paper title is the project title above. **English is the planned manuscript and repository language**, to make the methods and findings accessible to the international NLP community. Turkish examples will retain their original spelling and receive English glosses. Course-specific language requirements can be accommodated separately.

The manuscript will develop through: Introduction → Related Work → Dataset and Validation → Experimental Protocol → Results → Discussion and Limitations → Conclusion. Dataset construction details, annotation decisions, hyperparameters, and additional layer-wise results will be included in appendices where appropriate.

The paper will report what the experiments actually support. Negative or mixed findings are valid outcomes; publication readiness will depend on methodological quality, evidence, and positioning against related work.

## References

- **Ismayilzada et al. (2025).** [Evaluating Morphological Compositional Generalization in Large Language Models.](https://aclanthology.org/2025.naacl-long.59/) NAACL. Closely related work on Turkish/Finnish morphology, novel roots, and compositional generalization.
- **Hewitt and Liang (2019).** [Designing and Interpreting Probes with Control Tasks.](https://aclanthology.org/D19-1275/) EMNLP-IJCNLP. Motivation for probe-capacity controls and careful interpretation.
- **Pimentel et al. (2020).** [Information-Theoretic Probing for Linguistic Structure.](https://aclanthology.org/2020.acl-main.420/) ACL. An information-theoretic perspective on what probing measures.
- **BERTurk model documentation.** [dbmdz/bert-base-turkish-cased.](https://huggingface.co/dbmdz/bert-base-turkish-cased)
- **Multilingual BERT model documentation.** [google-bert/bert-base-multilingual-cased.](https://huggingface.co/google-bert/bert-base-multilingual-cased)
- **XLM-R model documentation.** [FacebookAI/xlm-roberta-base.](https://huggingface.co/FacebookAI/xlm-roberta-base)
- **Universal Dependencies.** [Turkish feature overview](https://universaldependencies.org/tr/feat/index.html) and [Turkish-GB feature inventory.](https://universaldependencies.org/treebanks/tr_gb/index.html)
- **Zemberek-NLP.** [Turkish NLP tools, including morphological analysis and generation.](https://github.com/ahmetaa/zemberek-nlp)

## Team

| Member | Student ID | Initial work-package lead | Cross-reviewer |
| --- | --- | --- | --- |
| Halil Abacı | 220401025 | Data, morphology, screening, and split construction | Fatmanur |
| Fatmanur Bulut | 230401034 | Encoders, token alignment, and layer representations | Samet |
| Samet Ünsal | 220401082 | Probing, baselines, evaluation, and integration | Halil |

The [team plan](docs/TEAM_PLAN.md) defines concrete deliverables, paper sections, handoffs, and a proposed first seven working days. The allocation is an initial proposal for team review; literature review, morphological validation, and manuscript discussion are shared responsibilities.

Prepared for the **Natural Language Processing** course. Individual contributions and manuscript authorship order will be documented as the project develops; the listing above does not establish an authorship order.
