"""Regression for the final task-board readiness gate (isolated helper copy only)."""
import tempfile
import unittest
import subprocess
import sys
from pathlib import Path
from scripts import team, workflow_v2 as workflow
from test_workflow_v2 import completed

class FinalBoardReadinessTests(unittest.TestCase):
    def test_cli_atomic_report_and_rejects_escaped_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "project"
            root.mkdir()
            state = completed(root)
            checkpoint = root / "checkpoint.json"
            team.save(checkpoint, team.checkpoint(state, "test authorization"))
            before = team.digest(checkpoint)
            cli = Path(__file__).resolve().parents[1] / "scripts" / "team.py"
            command = [sys.executable, "-B", str(cli), "report", str(checkpoint),
                       "--markdown", "--expected-digest", before, "--output"]
            outside = Path(directory) / "outside.md"
            refused = subprocess.run(command+[str(outside)], text=True, capture_output=True, timeout=20)
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("workspace/TASKS.md", refused.stderr)
            self.assertFalse(outside.exists())
            result = subprocess.run(command+[str(root/"TASKS.md")], text=True, capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((root/"TASKS.md").read_text(encoding="utf-8"), workflow.report(state))
            self.assertEqual(team.digest(checkpoint), before)
            self.assertEqual(team.readiness(state, "v1")["verdict"], "PASS")

    def test_existing_stale_board_rejects_ready_and_fresh_projection_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = completed(root)
            board = root / "TASKS.md"
            expected = workflow.report(state)
            board.write_text(expected.replace(
                f"Revision: {state['revision']}", "Revision: 0"), encoding="utf-8")
            with self.assertRaisesRegex(team.ContractError, "Stale final live task board"):
                team.readiness(state, "v1")
            board.write_text(expected, encoding="utf-8")
            self.assertEqual(team.readiness(state, "v1")["verdict"], "PASS")

if __name__ == "__main__":
    unittest.main()
