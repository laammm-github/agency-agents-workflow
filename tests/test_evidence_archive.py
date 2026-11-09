"""Safe archive catalog regression tests: synthetic workspace only."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.evidence_archive import (
    archive_tree_counts, create_plan, digest, markdown_report, snapshot_project,
    valid_relative, verify, write_new_json,
)


class EvidenceArchiveTests(unittest.TestCase):
    def setUp(self):
        self.repo = Path(__file__).resolve().parents[1]
        self.tmp = tempfile.TemporaryDirectory(prefix="archive-index-test-", dir=self.repo / "build")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        (self.root / "docs").mkdir(parents=True)
        self.base = self.root / "build" / "host-workflow-v2"
        self.base.mkdir(parents=True)
        for rel in ["docs/STATUS.md", "docs/TASKS.md", "docs/ACCEPTANCE_MATRIX.md",
                    "plugin.json", "package-files.json"]:
            p = self.root / rel
            p.write_text("test baseline\n", encoding="utf8")
        (self.base / "runs.json").write_text('{"trial-01":{"status":"READY PASS"}}\n', encoding="utf8")
        (self.base / "old-review.pending").write_text("retain this failed proposal", encoding="utf8")
        self.trial = self.base / "trial-01"
        self.trial.mkdir()
        (self.trial / "source.py").write_text("print('frozen')\n", encoding="utf8")
        (self.trial / "evidence").mkdir()
        (self.trial / "evidence" / "raw.json").write_text('{"status":"completed","success":true}', encoding="utf8")
        sha_source = hashlib.sha256((self.trial / "source.py").read_bytes()).hexdigest()
        sha_evidence = hashlib.sha256((self.trial / "evidence" / "raw.json").read_bytes()).hexdigest()
        checkpoint = {
            "revision": 4, "updated_at": "2026-11-09T00:00:00+00:00",
            "pending_operations": [], "state": {
                "tasks": [{"task_id": "DESIGN", "status": "COMPLETED"}],
                "candidate": {"candidate_id": "c1", "manifest": {"source.py": sha_source}},
                "evidence": [{"evidence_id": "e1", "task_id": "DESIGN",
                              "check": "inspection", "outcome": "PASS",
                              "provenance": "HOST_RETURN", "artifact_ref": "evidence/raw.json",
                              "output_sha256": sha_evidence}],
            }
        }
        (self.trial / "checkpoint.json").write_text(json.dumps(checkpoint), encoding="utf8")
        (self.trial / "TASKS.md").write_text("# trial-01\nRevision: 4\n", encoding="utf8")
        active = self.base / "trial-02"
        active.mkdir()
        checkpoint["revision"] = 2
        checkpoint["state"]["tasks"][0]["status"] = "EXECUTING"
        checkpoint["state"]["evidence"] = []
        checkpoint["state"]["candidate"] = {"candidate_id": "c2", "manifest": {"not-yet.py": "x" * 64}}
        (active / "checkpoint.json").write_text(json.dumps(checkpoint), encoding="utf8")
        (self.base / "trial-01-observed").mkdir()

    def test_index_preserves_completed_and_defers_active(self):
        snapshot = snapshot_project(self.root)
        self.assertEqual(snapshot["schema"], "agency-evidence-catalog/v1")
        self.assertEqual(snapshot["counts"]["trial_related_directories"], 3)
        entries = {Path(x["path"]).name: x for x in snapshot["trials"]}
        completed = entries["trial-01"]
        self.assertEqual(completed["verification_level"], "COMPLETED_READ_ONLY")
        self.assertTrue(completed["candidate"]["files"][0]["sha256_matches"])
        self.assertTrue(completed["evidence"][0]["sha256_matches"])
        self.assertTrue(completed["task_board"]["contains_revision"])
        self.assertEqual(entries["trial-02"]["verification_level"], "INCOMPLETE_METADATA_ONLY")
        self.assertNotIn("observed_sha256", entries["trial-02"]["candidate"]["files"][0])
        self.assertEqual(entries["trial-01-observed"]["verification_level"], "UNVERIFIED_NO_CHECKPOINT")
        self.assertEqual(verify(snapshot)["finding_count"], 0)

    def test_cleanup_plan_never_deletes_or_moves(self):
        snapshot = snapshot_project(self.root)
        plan = create_plan(snapshot)
        self.assertEqual(plan["automatic_deletion_candidates"], [])
        self.assertEqual(plan["destructive_actions_performed"], 0)
        self.assertEqual(plan["reversible_actions_performed"], 0)
        self.assertEqual(len(plan["review_only"]), 1)
        self.assertTrue((self.base / "old-review.pending").is_file())

    def test_snapshot_exclusive_output_and_readback(self):
        snapshot = snapshot_project(self.root)
        path = self.root / "build" / "archive-index" / "snapshot.json"
        written = write_new_json(path, snapshot, self.root)
        self.assertEqual(written["sha256"], digest(path.read_bytes()))
        self.assertEqual(json.loads(path.read_text(encoding="utf8"))["schema"], snapshot["schema"])
        with self.assertRaises(FileExistsError):
            write_new_json(path, snapshot, self.root)
        with self.assertRaises(ValueError):
            write_new_json(Path(self.tmp.name) / "outside.json", snapshot, self.root)

    def test_verification_finds_changes_and_never_restores_over_original(self):
        snapshot = snapshot_project(self.root)
        (self.trial / "source.py").write_text("tampered", encoding="utf8")
        result = verify(snapshot)
        issues = {(x["path"], x["issue"]) for x in result["findings"]}
        self.assertIn(("build/host-workflow-v2/trial-01/source.py", "CANDIDATE_CHANGED"), issues)
        self.assertTrue((self.trial / "evidence" / "raw.json").is_file())
        self.assertEqual((self.trial / "source.py").read_text(encoding="utf8"), "tampered")

    def test_evidence_path_escaping_is_rejected(self):
        self.assertIsNone(valid_relative(self.trial, "../runs.json"))
        self.assertIsNone(valid_relative(self.trial, "evidence\\raw.json"))
        self.assertIsNone(valid_relative(self.trial, ""))
        self.assertIsNotNone(valid_relative(self.trial, "evidence/raw.json"))

    def test_historical_artifact_id_alias_resolves_without_rewriting_checkpoint(self):
        checkpoint = self.trial / "checkpoint.json"
        obj = json.loads(checkpoint.read_text(encoding="utf8"))
        original_hash = hashlib.sha256((self.trial / "evidence" / "raw.json").read_bytes()).hexdigest()
        obj["state"]["artifacts"] = [
            {"artifact_id": "A-DESIGN", "path": "evidence/raw.json", "sha256": original_hash}
        ]
        obj["state"]["evidence"][0]["artifact_ref"] = "A-DESIGN"
        checkpoint.write_text(json.dumps(obj), encoding="utf8")
        before = checkpoint.read_bytes()
        snapshot = snapshot_project(self.root)
        record = next(x for x in snapshot["trials"] if x["path"].endswith("/trial-01"))["evidence"][0]
        self.assertEqual(record["artifact_ref"], "A-DESIGN")
        self.assertEqual(record["resolved_path"], "evidence/raw.json")
        self.assertEqual(record["resolution"], "ARTIFACT_ID_ALIAS")
        self.assertTrue(record["sha256_matches"])
        self.assertEqual(verify(snapshot)["finding_count"], 0)
        self.assertEqual(checkpoint.read_bytes(), before)

    def test_markdown_report_links_trials_without_claiming_authenticated_success(self):
        snapshot = snapshot_project(self.root)
        rendered = markdown_report(snapshot)
        self.assertIn("../host-workflow-v2/trial-01/checkpoint.json", rendered)
        self.assertIn("trial-02", rendered)
        self.assertIn("不独立证明宿主工具来源", rendered)
        self.assertIn("原始 FAIL", rendered)

    def test_counts_include_cache_without_deleting_it(self):
        cache = self.trial / "__pycache__"
        cache.mkdir()
        (cache / "fake.pyc").write_bytes(b"cached bytes")
        counts, bytes_total, warnings = archive_tree_counts(self.trial)
        self.assertGreaterEqual(counts["cache_files"], 1)
        self.assertEqual(warnings, [])
        self.assertGreater(bytes_total, 0)
        self.assertTrue((cache / "fake.pyc").is_file())


if __name__ == "__main__":
    unittest.main()
