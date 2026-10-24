# Nominal dataset contract v0.1.0

The machine-readable contract is [nominal_record.schema.json](../src/turkish_morphology/resources/nominal_record.schema.json). Data files use UTF-8 JSON Lines: one record per line. No real dataset has been accepted yet.

| Field | Meaning |
| --- | --- |
| `schema_version` | `0.1.0` for this contract. |
| `id` | Globally unique example identifier within a dataset. |
| `root_id` | Stable identity for one root across its full paradigm. |
| `pair_id` | Matched real/nonce family; the partitioning and bootstrap unit. |
| `root` / `root_type` | Lowercase alphabetic NFC root string and `real` or `nonce`. |
| `surface` | Lowercase alphabetic NFC inflected word. |
| `segments` | Root followed by surface suffix segments; concatenation must equal `surface`. |
| `morphemes` | Canonical suffix IDs only, excluding the root, in application order. |
| `features` | The five targets below. |
| `split` | `unassigned`, `train`, `dev`, or `test`. |
| `validation_status` | `pending`, `accepted`, or `rejected`; acceptance comes from review. |
| `screening_status` | `not_applicable` for real roots; `pending`, `passed`, or `rejected` for nonce roots. |
| `source_id` | Key in `data/source_registry.json`. |
| `reviewers` | Names/IDs of actual reviewers; empty until review occurs. |
| `notes` | Ambiguities, screening evidence location, exclusions, or review context. |

## Targets

- `Number`: `Sing` or `Plur`, describing the noun.
- `Case`: `Nom`, `Acc`, `Dat`, `Loc`, `Abl`, or `Gen`.
- `Possession`: project-defined `Yes` or `No`.
- `Person[psor]`: `1`, `2`, or `3` when possessed, otherwise JSON `null`.
- `Number[psor]`: `Sing` or `Plur` when possessed, otherwise JSON `null`.

Canonical suffix IDs in the pilot are `PL`, one of `POSS_1SG`, `POSS_2SG`, `POSS_3SG`, `POSS_1PL`, `POSS_2PL`, `POSS_3PL`, and one of `ACC`, `DAT`, `LOC`, `ABL`, `GEN`. Nominative and singular nouns have no corresponding overt suffix ID. Use legal noun → plural → possessive → case order. Surface allomorphs remain in `segments`.

The initial contract requires `segments[0] == root` and `len(segments) == len(morphemes) + 1`; it therefore supports regular roots without stem alternation. A form such as `kitap → kitabı` needs explicit underlying-root/surface-stem alignment and a new contract version before admission. This restriction avoids silently conflating roots and surface stems.

## Validation levels

```powershell
python -m turkish_morphology validate-data data/examples/nominal.jsonl
python -m turkish_morphology validate-data data/processed/nominal-v0.jsonl --release
```

Ordinary validation checks schema, NFC text, segmentation, feature/morpheme consistency, duplicate IDs/surfaces, root identity, and cross-partition root/pair/surface leakage. It accepts pending/unassigned records for construction work.

Release validation additionally requires train/dev/test partitions, at least two distinct actual reviewer entries per record, acceptance, passed nonce screening, and source approval metadata. Pair inventories must contain exactly one real and one nonce root, including all their inflections. Split membership assigns root families; it does not itself authorize every record for fitting. Nonce members of training pairs remain audit records. `probe_training_records` selects accepted real-root training forms only.

These checks do not certify class balance, sample size, phonotactics, vowel harmony, corpus absence, composition-holdout coverage, or human-review quality. Those need separate documented audits.

Keep original reference sources unchanged in `data/raw/`; write derived records to `data/processed/`. Frozen split manifests belong in `data/splits/` and must list dataset version/hash, condition, seed, pair/root/example IDs, and holdout rules. Their construction is an assigned implementation task.

## Source registry and review

Every accepted source must record its title, location, version or retrieval date, license/terms, allowed redistribution, and screening role. The initial registry contains only the illustrative example source and has no approved research-data source.

For each released nonce root, retain exact screening resources/versions, queried root and inflections, results, and reviewer decisions. `screening_status=passed` is a human-audited record, not proof of absence in encoder pretraining. Review each candidate with at least two team members and resolve disagreements before marking it accepted.
