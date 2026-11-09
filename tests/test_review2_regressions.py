import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import team
from test_team import completed, sample

ROOT = Path(__file__).resolve().parents[1]


class RerunTests(unittest.TestCase):
 def test_older_equal_missing_invalid_or_naive_pass_cannot_clear_failure(self):
  for timestamp in ['2026-10-28T08:00:00Z', '2026-10-28T08:01:00Z', None, 'invalid', '2026-10-28T08:02:00']:
   with self.subTest(timestamp=timestamp):
    state = completed(ROOT)
    state['evidence'][0].update(timestamp=timestamp, supersedes=['FAIL1'])
    state['evidence'].append(dict(state['evidence'][0], evidence_id='FAIL1', outcome='FAIL', exit_code=1, timestamp='2026-10-28T08:01:00Z', supersedes=[]))
    with self.assertRaisesRegex(team.ContractError, 'later timestamped PASS'):
     team.readiness(state, 'v1')

 def test_missing_failure_time_requires_investigation(self):
  state = completed(ROOT)
  failure = dict(state['evidence'][0], evidence_id='FAIL1', outcome='FAIL', exit_code=1)
  state['evidence'].append(failure)
  state['evidence'][0].update(timestamp='2026-10-28T08:02:00Z', supersedes=['FAIL1'])
  with self.assertRaisesRegex(team.ContractError, 'Unresolved'):
   team.readiness(state, 'v1')

 def test_rerun_compares_instants_across_timezones(self):
  state = completed(ROOT)
  state['evidence'][0].update(timestamp='2026-10-28T16:01:00+08:00', supersedes=['FAIL1'])
  state['evidence'].append(dict(state['evidence'][0], evidence_id='FAIL1', outcome='FAIL', exit_code=1, timestamp='2026-10-28T08:00:00Z', supersedes=[]))
  self.assertEqual(team.readiness(state, 'v1')['verdict'], 'PASS')


class ArtifactHistoryTests(unittest.TestCase):
 def history(self):
  state = completed(ROOT)
  state['artifacts'].insert(0, dict(artifact_id='F0', path='README.md', sha256='a'*64))
  state['artifacts'][1]['supersedes'] = 'F0'
  return state

 def test_current_version_passes_with_history_in_either_order(self):
  for reverse in [False, True]:
   state = self.history()
   if reverse: state['artifacts'].reverse()
   before = copy.deepcopy(state)
   self.assertEqual(team.readiness(state, 'v1')['verdict'], 'PASS')
   document = team.checkpoint(state, 'test-only')
   self.assertEqual(document['expected_hashes'], {'README.md': team.digest(ROOT/'README.md')})
   self.assertEqual(team.resume(document, ROOT)['status'], 'PREFLIGHT')
   self.assertEqual(state, before)

 def test_changed_current_version_still_blocks(self):
  state = self.history()
  state['artifacts'][1]['sha256'] = 'b'*64
  with self.assertRaisesRegex(team.ContractError, 'changed artifact'):
   team.readiness(state, 'v1')

 def test_invalid_history_does_not_hide_artifacts(self):
  for case in ['missing', 'cycle', 'fork', 'ambiguous-path']:
   with self.subTest(case=case):
    state = self.history()
    if case == 'missing': state['artifacts'][1]['supersedes'] = 'missing'
    if case == 'cycle': state['artifacts'][0]['supersedes'] = 'F1'
    if case == 'fork': state['artifacts'].append(dict(state['artifacts'][1], artifact_id='F2'))
    if case == 'ambiguous-path': del state['artifacts'][1]['supersedes']
    with self.assertRaises(team.ContractError): team.validate(state)


class CheckpointTests(unittest.TestCase):
 def cli(self, *args):
  return subprocess.run([sys.executable, '-B', 'scripts/team.py', *map(str, args)], cwd=ROOT, capture_output=True, text=True, encoding='utf-8', timeout=10)

 def write(self, path, data):
  path.write_text(json.dumps(data), encoding='utf-8')

 def test_cli_cannot_omit_or_replace_saved_nonartifact_baseline(self):
  with tempfile.TemporaryDirectory() as folder:
   root = Path(folder)
   baseline = root/'source.txt'; baseline.write_text('before')
   document = team.checkpoint(sample(root), 'test-only', {'source.txt': team.digest(baseline)})
   statefile = root/'checkpoint.json'; self.write(statefile, document)
   baseline.write_text('after')
   hashes = root/'hashes.json'
   for supplied in [{}, {'source.txt': team.digest(baseline)}]:
    self.write(hashes, supplied)
    result = self.cli('resume', statefile, '--workspace', root, '--hashes', hashes)
    self.assertEqual(result.returncode, 1, result.stdout)
    self.assertIn('baseline', result.stderr)
   result = self.cli('resume', statefile, '--workspace', root)
   self.assertEqual(result.returncode, 1, result.stdout)
   self.assertIn('External modification', result.stderr)

 def test_public_checkpoint_resumes_from_saved_baseline(self):
  with tempfile.TemporaryDirectory() as folder:
   root = Path(folder); source = root/'source.txt'; source.write_text('unchanged')
   document = team.checkpoint(sample(root), 'test-only', {'source.txt': team.digest(source)})
   statefile = root/'checkpoint.json'; self.write(statefile, document)
   result = self.cli('resume', statefile, '--workspace', root)
   self.assertEqual(result.returncode, 0, result.stderr)
   self.assertEqual(json.loads(result.stdout)['status'], 'PREFLIGHT')
   self.assertTrue(json.loads(result.stdout)['authorization_recheck_required'])

 def test_public_checkpoint_checks_nonartifact_baseline_with_artifacts(self):
  state = completed(ROOT)
  document = team.checkpoint(state, 'test-only', {'plugin.json': 'a'*64})
  with self.assertRaisesRegex(team.ContractError, 'baseline coverage'):
   team.resume(document, ROOT, {'README.md': team.digest(ROOT/'README.md')})
  with self.assertRaisesRegex(team.ContractError, 'External modification'):
   team.resume(document, ROOT)

 def test_incomplete_or_conflicting_public_checkpoint_is_rejected(self):
  document = team.checkpoint(completed(ROOT), 'test-only')
  document['expected_hashes'] = {}
  with self.assertRaisesRegex(team.ContractError, 'coverage'): team.load_state(document)
  with self.assertRaisesRegex(team.ContractError, 'Conflicting'):
   team.checkpoint(completed(ROOT), 'test-only', {'README.md': 'a'*64})

 def test_cli_change_and_transition_preserve_resume_metadata(self):
  for operation in ['transition', 'change']:
   with self.subTest(operation=operation), tempfile.TemporaryDirectory() as folder:
    root = Path(folder); baseline = root/'source.txt'; baseline.write_text('unchanged')
    document = team.checkpoint(sample(root), 'test-only', {'source.txt': team.digest(baseline)})
    metadata = dict(milestone='release', last_confirmed_action='tool-call-42', next_preconditions=['Inspect deployment target'])
    document.update(copy.deepcopy(metadata))
    statefile = root/'checkpoint.json'; self.write(statefile, document)
    before = team.digest(statefile)
    arguments = ['--task-id', 'T1', '--status', 'PREFLIGHT'] if operation == 'transition' else ['--requirement-id', 'R1', '--description', 'new description']
    result = self.cli(operation, statefile, '--expected-digest', before, *arguments)
    self.assertEqual(result.returncode, 0, result.stderr)
    saved = json.loads(statefile.read_text(encoding='utf-8'))
    self.assertEqual({key: saved[key] for key in metadata}, metadata)
    self.assertEqual(saved['expected_hashes'], document['expected_hashes'])
    self.assertEqual(saved['authorization_ref'], document['authorization_ref'])
    self.assertEqual(saved['revision'], 1)
    self.assertEqual(team.load_state(saved)['revision'], 1)
    self.assertNotEqual(team.digest(statefile), before)
    self.assertEqual(document['revision'], 0)
