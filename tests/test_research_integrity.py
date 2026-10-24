"""Regression checks for failures that could invalidate the study.

Accepted labels/reviewer names in these fixtures are synthetic test metadata,
not claims that research examples have been reviewed.
"""

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from turkish_morphology.config import load_config, require_pinned_models
from turkish_morphology.data.validation import (
    load_jsonl, probe_training_records, validate_records,
)
from turkish_morphology.experiments import prepare_run, sha256


REPO = Path(__file__).resolve().parents[1]
SOURCE = {
    "sources": [{
        "source_id": "synthetic-fixture", "title": "Unit-test fixtures only",
        "location": "tests/test_research_integrity.py", "version": "test-v1",
        "license": "Synthetic internal test fixture", "redistribution": "test-only",
        "approved_for_research": True, "role": "Simulate approval in isolated tests",
    }]
}


def release_fixture() -> list[dict]:
    records = []
    for split, roots in (("train", ("ev", "döp")), ("dev", ("göl", "zöp")), ("test", ("taş", "nıp"))):
        for kind, root in zip(("real", "nonce"), roots):
            records.append({
                "schema_version": "0.1.0", "id": f"{split}-{kind}",
                "root_id": f"root-{split}-{kind}", "pair_id": f"pair-{split}",
                "root": root, "root_type": kind, "surface": root,
                "segments": [root], "morphemes": [],
                "features": {"Number": "Sing", "Case": "Nom", "Possession": "No", "Person[psor]": None, "Number[psor]": None},
                "split": split, "validation_status": "accepted",
                "screening_status": "passed" if kind == "nonce" else "not_applicable",
                "source_id": "synthetic-fixture", "reviewers": ["test-reviewer-a", "test-reviewer-b"],
                "notes": "Synthetic fixture; not an accepted research observation.",
            })
    return records


class DatasetIntegrityTests(unittest.TestCase):
    def test_examples_are_staging_only(self):
        records = load_jsonl(REPO / "data/examples/nominal.jsonl")
        sources = json.loads((REPO / "data/source_registry.json").read_text(encoding="utf-8"))
        self.assertTrue(validate_records(records, sources=sources).valid)
        release = validate_records(records, release=True, sources=sources)
        self.assertFalse(release.valid)
        self.assertTrue(any("accepted" in error for error in release.errors))
        self.assertTrue(any("screening" in error for error in release.errors))

    def test_complete_fixture_passes_selected_release_checks(self):
        report = validate_records(release_fixture(), release=True, sources=SOURCE)
        self.assertEqual(report.errors, [])
        self.assertEqual((report.records, report.roots, report.pairs), (6, 6, 3))

    def test_root_id_leakage_is_rejected(self):
        records = release_fixture()
        records[2]["root_id"] = records[0]["root_id"]
        report = validate_records(records)
        self.assertTrue(any("root_id leakage" in error for error in report.errors))

    def test_pair_leakage_is_rejected_even_when_roots_differ(self):
        records = release_fixture()
        records[2]["pair_id"] = records[0]["pair_id"]
        report = validate_records(records)
        self.assertTrue(any("pair_id leakage" in error for error in report.errors))

    def test_surface_overlap_is_rejected_even_under_different_ids(self):
        records = release_fixture()
        records[2].update(root="ev", surface="ev", segments=["ev"])
        report = validate_records(records)
        self.assertTrue(any("surface leakage" in error for error in report.errors))
        self.assertTrue(any("multiple root IDs" in error for error in report.errors))

    def test_nfc_equivalent_spellings_cannot_bypass_checks(self):
        records = release_fixture()
        records[2].update(root="go\u0308l", surface="go\u0308l", segments=["go\u0308l"])
        report = validate_records(records)
        self.assertTrue(any("Unicode NFC" in error for error in report.errors))

    def test_dotless_i_is_preserved_as_valid_turkish_text(self):
        records = release_fixture()
        records[0].update(root="ışık", surface="ışık", segments=["ışık"])
        self.assertTrue(validate_records(records).valid)

    def test_feature_morpheme_disagreement_is_rejected(self):
        records = release_fixture()
        records[0]["features"]["Number"] = "Plur"
        self.assertTrue(any("morphemes must match" in error for error in validate_records(records).errors))

    def test_possessor_number_is_not_noun_number(self):
        record = load_jsonl(REPO / "data/examples/nominal.jsonl")[0]
        record.update(surface="gölümüzden", segments=["göl", "ümüz", "den"], morphemes=["POSS_1PL", "ABL"])
        record["features"]["Number"] = "Sing"
        self.assertTrue(validate_records([record]).valid)
        record["features"]["Number[psor]"] = "Sing"
        self.assertFalse(validate_records([record]).valid)

    def test_unpossessed_form_cannot_carry_possessor_labels(self):
        records = release_fixture()
        records[0]["features"]["Person[psor]"] = "1"
        self.assertFalse(validate_records(records).valid)

    def test_release_requires_review_and_approved_sources(self):
        records = release_fixture()
        records[0]["reviewers"] = ["test-reviewer-a"]
        sources = deepcopy(SOURCE)
        sources["sources"][0]["approved_for_research"] = False
        report = validate_records(records, release=True, sources=sources)
        self.assertTrue(any("two distinct" in error for error in report.errors))
        self.assertTrue(any("not approved" in error for error in report.errors))

    def test_training_selector_excludes_nonce_audit_members(self):
        selected = probe_training_records(release_fixture())
        self.assertEqual([record["id"] for record in selected], ["train-real"])

    def test_training_selector_rejects_pending_real_forms(self):
        records = release_fixture()
        records[0]["validation_status"] = "pending"
        with self.assertRaisesRegex(ValueError, "unaccepted"):
            probe_training_records(records)

    def test_missing_pair_member_is_not_release_ready(self):
        report = validate_records(release_fixture()[:-1], release=True, sources=SOURCE)
        self.assertTrue(any("one real and one nonce" in error for error in report.errors))


class ConfigurationAndRunTests(unittest.TestCase):
    def test_proposed_config_is_valid_but_not_revision_pinned(self):
        config = load_config(REPO / "configs/pilot.toml")
        with self.assertRaisesRegex(ValueError, "verified"):
            require_pinned_models(config)

    def test_model_selection_on_test_data_is_rejected(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "config.toml"
            text = (REPO / "configs/pilot.toml").read_text(encoding="utf-8")
            path.write_text(text.replace('selection_split = "dev"', 'selection_split = "test"'), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "dev partition"):
                load_config(path)

    def test_prepare_run_snapshots_inputs_without_fabricating_results(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            config_path, dataset_path, source_path = root / "config.toml", root / "dataset.jsonl", root / "sources.json"
            # Syntactically pinned fake revisions are for offline tests only.
            text = (REPO / "configs/pilot.toml").read_text(encoding="utf-8")
            config_path.write_text(text.replace("UNRESOLVED", "a" * 40), encoding="utf-8")
            dataset_path.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in release_fixture()) + "\n", encoding="utf-8")
            source_path.write_text(json.dumps(SOURCE), encoding="utf-8")
            run_dir = prepare_run(config_path, dataset_path, source_path, root / "runs")
            manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], "prepared")
            self.assertNotIn("metrics", manifest)
            self.assertEqual(manifest["dataset_summary"]["probe_training_records"], 1)
            for entry in manifest["inputs"].values():
                self.assertEqual(entry["sha256"], sha256(run_dir / entry["file"]))
            original_hash = manifest["inputs"]["dataset"]["sha256"]
            dataset_path.write_text("changed after preparation", encoding="utf-8")
            self.assertEqual(sha256(run_dir / "dataset.jsonl"), original_hash)

    def test_unpinned_preparation_fails_before_creating_a_run(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "runs"
            with self.assertRaisesRegex(ValueError, "verified"):
                prepare_run(REPO / "configs/pilot.toml", Path("missing.jsonl"), Path("missing-sources.json"), output)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
