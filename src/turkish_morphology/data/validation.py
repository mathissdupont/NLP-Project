"""Structural checks; these do not replace linguistic review or coverage audits."""

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from importlib.resources import files
import json
from pathlib import Path
import unicodedata

from jsonschema import Draft202012Validator


@dataclass
class ValidationReport:
    records: int = 0
    roots: int = 0
    pairs: int = 0
    split_counts: dict = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.errors


def load_jsonl(path: Path) -> list[dict]:
    """Read UTF-8/UTF-8-BOM JSONL with useful line-number errors."""
    records = []
    with path.open(encoding="utf-8-sig") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: {exc.msg}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"{path}:{line_number}: record must be an object")
            records.append(record)
    return records


def validate_records(
    records: list[dict], *, release: bool = False, sources: dict | None = None
) -> ValidationReport:
    schema = json.loads(
        files("turkish_morphology").joinpath("resources/nominal_record.schema.json")
        .read_text(encoding="utf-8")
    )
    validator = Draft202012Validator(schema)
    report = ValidationReport(records=len(records))
    if not records:
        report.errors.append("Dataset is empty.")
        return report

    source_index = {}
    if sources is not None:
        entries = sources.get("sources") if isinstance(sources, dict) else None
        if not isinstance(entries, list) or not all(
            isinstance(item, dict) and isinstance(item.get("source_id"), str)
            for item in entries
        ):
            report.errors.append("Source registry must contain source objects with IDs.")
        else:
            source_index = {item["source_id"]: item for item in entries}
            if len(source_index) != len(entries):
                report.errors.append("Source registry contains duplicate source IDs.")
    if release and sources is None:
        report.errors.append("Release validation requires a source registry.")

    seen_ids = set()
    seen_surfaces = set()
    root_identity = {}
    root_string_identity = {}
    partition_maps = {key: {} for key in ("root_id", "root", "pair_id", "surface")}
    pair_roots = defaultdict(lambda: {"real": set(), "nonce": set()})
    split_counts = Counter()

    for index, record in enumerate(records, 1):
        label = record.get("id", f"record-{index}") if isinstance(record, dict) else f"record-{index}"
        problems = list(validator.iter_errors(record))
        if problems:
            for problem in problems:
                location = ".".join(str(part) for part in problem.absolute_path) or "record"
                report.errors.append(f"{label}: {location}: {problem.message}")
            continue

        def error(message: str) -> None:
            report.errors.append(f"{label}: {message}")

        if record["id"] in seen_ids:
            error("duplicate example ID")
        seen_ids.add(record["id"])

        for field_name in ("root", "surface"):
            value = record[field_name]
            if unicodedata.normalize("NFC", value) != value:
                error(f"{field_name} must use Unicode NFC")
            lowered = value.translate(str.maketrans({"I": "ı", "İ": "i"})).lower()
            if lowered != value or not value.isalpha():
                error(f"{field_name} must be a lowercase alphabetic word")
        if any(unicodedata.normalize("NFC", part) != part for part in record["segments"]):
            error("segments must use Unicode NFC")
        if record["segments"][0] != record["root"]:
            error("first segment must equal the root; stem alternation is outside schema v0.1.0")
        if "".join(record["segments"]) != record["surface"]:
            error("segments do not concatenate to surface")
        if len(record["segments"]) != len(record["morphemes"]) + 1:
            error("each suffix morpheme must have one surface segment")

        features = record["features"]
        possessed = features["Possession"] == "Yes"
        person, number = features["Person[psor]"], features["Number[psor]"]
        if possessed != (person is not None and number is not None):
            error("possession and possessor feature applicability disagree")
        if not possessed and (person is not None or number is not None):
            error("unpossessed nouns must have null possessor features")
        expected = ["PL"] if features["Number"] == "Plur" else []
        if possessed and person is not None and number is not None:
            expected.append(f"POSS_{person}{'SG' if number == 'Sing' else 'PL'}")
        if features["Case"] != "Nom":
            expected.append(features["Case"].upper())
        if record["morphemes"] != expected:
            error(f"morphemes must match feature labels and order: expected {expected}")

        identity = (record["root"], record["root_type"], record["pair_id"])
        previous = root_identity.setdefault(record["root_id"], identity)
        if previous != identity:
            error("root_id maps to inconsistent root/type/pair metadata")
        previous_id = root_string_identity.setdefault(record["root"], record["root_id"])
        if previous_id != record["root_id"]:
            error("same root string has multiple root IDs")
        pair_roots[record["pair_id"]][record["root_type"]].add(record["root_id"])

        surface_key = unicodedata.normalize("NFC", record["surface"])
        if surface_key in seen_surfaces:
            error("duplicate surface form; resolve duplicate weighting or ambiguity")
        seen_surfaces.add(surface_key)
        split = record["split"]
        split_counts[split] += 1
        if split != "unassigned":
            for key, partitions in partition_maps.items():
                value = unicodedata.normalize("NFC", record[key])
                previous_split = partitions.setdefault(value, split)
                if previous_split != split:
                    error(f"{key} leakage: {value!r} occurs in {previous_split} and {split}")

        if record["root_type"] == "real" and record["screening_status"] != "not_applicable":
            error("real roots require screening_status=not_applicable")
        if record["root_type"] == "nonce" and record["screening_status"] == "not_applicable":
            error("nonce roots require an explicit screening status")

        if sources is not None and record["source_id"] not in source_index:
            error("source_id is missing from the source registry")
        if release:
            if split == "unassigned":
                error("release records must have an assigned split")
            if record["validation_status"] != "accepted":
                error("release records must be accepted after review")
            if len(record["reviewers"]) < 2:
                error("release records require at least two distinct reviewers")
            if record["root_type"] == "nonce" and record["screening_status"] != "passed":
                error("release nonce records require passed screening")
            source = source_index.get(record["source_id"], {})
            if source.get("approved_for_research") is not True:
                error("source is not approved for research")
            for source_field in ("title", "location", "version", "license", "redistribution", "role"):
                if not isinstance(source.get(source_field), str) or not source[source_field].strip():
                    error(f"approved source is missing {source_field}")

    if release:
        for pair_id, groups in pair_roots.items():
            if len(groups["real"]) != 1 or len(groups["nonce"]) != 1:
                report.errors.append(f"{pair_id}: release pairs require one real and one nonce root")
        for split in ("train", "dev", "test"):
            if split_counts[split] == 0:
                report.errors.append(f"Release is missing the {split} partition.")

    report.roots = len(root_identity)
    report.pairs = len(pair_roots)
    report.split_counts = dict(split_counts)
    return report


def probe_training_records(records: list[dict]) -> list[dict]:
    """Select real-only training input; split membership is a pair assignment."""
    selected = [r for r in records if r["split"] == "train" and r["root_type"] == "real"]
    if not selected:
        raise ValueError("No real-root probe training records are available.")
    if any(r["validation_status"] != "accepted" for r in selected):
        raise ValueError("Probe training cannot use unaccepted records.")
    return selected
