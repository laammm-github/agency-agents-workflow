import unittest
from scripts.index_roles import parse_role
class IndexTests(unittest.TestCase):
 def test_multiline_and_dual_identity(self):
  r=parse_role('---\nname: Frontend Developer\ndescription: |\n  Multi line\n  description\n---\nBody','engineering/engineering-frontend-developer.md')
  self.assertEqual(r['corpus_id'],'engineering-frontend-developer');self.assertEqual(r['codex_slug'],'frontend-developer');self.assertIn('Multi line',r['description'])
 def test_nonrole_ignored(self):self.assertIsNone(parse_role('# Runbook','strategy/runbooks/x.md'))
 def test_missing_field(self):
  with self.assertRaises(ValueError):parse_role('---\nname: Test\n---\nBody','test.md')
