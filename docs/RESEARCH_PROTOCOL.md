# Research protocol v0.1

**State:** Draft for team review, created 2026-10-24. This is a local protocol record, not an external preregistration. No model results have been inspected for this project.

## Scope and estimands

Use frozen encoders and supervised linear probes to study the accessibility of nominal `Number`, `Case`, `Possession`, `Person[psor]`, and `Number[psor]`. Possessor targets are evaluated only on possessed examples. Verbal morphology and sentence contexts are extensions after the core study.

The primary comparison is the difference in per-feature macro-F1 between held-out real roots and screened nonce roots, using the same probe and matched feature support. Report absolute scores, class counts, and baseline performance alongside each gap. The unit of lexical independence is the matched root pair.

## Pilot versus main study

The pilot is for debugging, annotator agreement, class coverage, and compute estimation. It begins with BERTurk, isolated words, mean pooling, and the proposed settings in `configs/pilot.toml`. The example records in `data/examples/` are schema demonstrations, not pilot observations.

Before the main study, record the final inventory size, source licenses, exclusion rules, validation procedure, split assignment seed(s), composition holdouts, hyperparameter search, and primary comparisons. Exclude pilot root families from the main test set. Record the frozen protocol/data/config hashes before opening main-test outputs.

## Dataset integrity

- All inflections of a root remain in one train/dev/test partition.
- Both members of a matched real/nonce pair remain in one partition; derivatives share the same pair ID.
- Root IDs and normalized root strings must agree on partition membership.
- Identical surface forms cannot cross partitions, even under different IDs.
- Retain Turkish characters; use Unicode NFC. Do not apply generic ASCII conversion or English-style case folding to Turkish roots.
- Only accepted forms enter a release; nonce acceptance also requires documented screening.
- Surface ambiguity must be identified by morphological review. The pilot will exclude unresolved ambiguous analyses from isolated-word classification. Exact duplicate forms are rejected within a release to prevent repeated weighting; an ambiguity-aware extension needs a versioned schema/protocol change.
- Pair counts, class distributions, feature-bundle support, suffix/allomorph coverage, and fragmentation are reported before modeling. A structural validator cannot establish linguistic correctness or adequate statistical support.

## Extraction and fitting

Pin each enabled checkpoint and tokenizer to the same verified commit revision for the initial study. Record any later divergence explicitly. Keep encoders frozen and in evaluation mode; disable gradient accumulation for feature extraction. Preserve example IDs and token offsets. Reject truncation or unknown-token cases that destroy target-word alignment, and report exclusions per model.

Use all non-special target-word subwords for mean pooling. Treat the embedding output as layer 0. Train a separate regularized linear classifier per feature/layer; fit transformations on the training set only. Select regularization and any headline layer on development data, with equal search budgets. Publish all layer profiles.

Train the root-generalization and real-to-nonce probes on real roots only. A record's split is its root-pair assignment: nonce members of training pairs can be retained in the dataset for audit, but must not enter probe fitting. The `probe_training_records` selector returns only accepted real-root training forms. The future fitting pipeline must use this selector after release validation.

## Conditions and controls

1. **Root generalization:** Held-out real roots with familiar bundles.
2. **Real-to-nonce:** Nonce roots paired with held-out real roots and matched on target support.
3. **Composition holdout:** New bundles whose constituent labels/morphemes are supported in training; use separate dev/test holdouts. Publish a bundle-coverage audit. The foundation validator does not yet implement this audit.
4. **Controls:** Majority, character n-gram, tokenization-only, layer 0, random encoder, and a separate word-type-overlap random-label diagnostic. Report protocol differences explicitly.

## Metrics and uncertainty

Macro-F1 is primary; accuracy, per-class F1, confusion matrices, and support counts are secondary. Fix each task's label inventory before evaluation. Do not let absent predictions change which labels enter macro-F1. Flag unsupported labels rather than averaging them away.

The initial target is five seeded runs and 2,000 paired root-pair bootstrap replicates at 95% confidence. Treat seed variation and bootstrap uncertainty separately: report per-seed estimates and an explicitly defined aggregation. Resample the same paired root units for both sides of a transfer comparison. Do not pool inflected forms as independent observations or describe layer-wide exploratory patterns as a single confirmatory significance test.

## Research records and stopping

Stop the core study after the frozen matrix is complete or the documented compute budget is exhausted; do not stop based on a favorable result. Log missing/failed runs and rerun causes. Each prepared run gets a manifest; training code must separately mark completion only after outputs and checks exist.

`prepare-run` creates a **prepared** directory and snapshots inputs; it does not train an encoder/probe, test GPU determinism, or create results. The main-study pipeline, class-support audits, composition checks, inference, and statistics remain implementation work.

Interpret probing as decodability, not proof of causal use, human-like rule learning, or absence of memorization. Differences among checkpoints are observational comparisons with pretraining/tokenizer/size confounds.
