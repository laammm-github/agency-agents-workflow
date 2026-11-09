"""Regression coverage for evidence-based Windows checkpoint lock guidance."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WindowsCheckpointLockGuidanceTests(unittest.TestCase):
    def test_skill_warns_about_mutable_checkpoint_preview_locks(self):
        text = (ROOT / "skills" / "agency-workflow" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("mcp__desktop_commander_mcp__read_file", text)
        self.assertIn("WinError 5", text)
        self.assertIn("checkpoint.json", text)
        self.assertIn("Get-Content", text)
        self.assertIn("Do not kill a shared MCP server process", text)

    def test_reference_preserves_lock_safety_and_handover_gate(self):
        text = (ROOT / "skills" / "agency-workflow" / "references" / "workflow-v2.md").read_text(encoding="utf-8")
        self.assertIn("Windows read-tool file-handle regression", text)
        self.assertIn("host-specific evidence", text)
        self.assertIn("do not create final README.md/REVIEW.md", text)
        self.assertIn("do not force-terminate", text.lower())


if __name__ == "__main__":
    unittest.main()
