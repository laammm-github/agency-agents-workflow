import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import jsonschema
from scripts import team
from scripts.package import build
from test_team import completed, sample
ROOT=Path(__file__).resolve().parents[1]

class GateRegressions(unittest.TestCase):
 def test_missing_requirement_blocks(self):
  state=completed(ROOT);state['requirements'].append({'requirement_id':'R2','acceptance_ids':['A2']})
  with self.assertRaisesRegex(team.ContractError,'Unimplemented'):team.readiness(state,'v1')
 def test_foreign_evidence_blocks(self):
  state=completed(ROOT);state['evidence'][0]['task_id']='T2'
  with self.assertRaisesRegex(team.ContractError,'another task'):team.readiness(state,'v1')
 def test_uncovered_acceptance_blocks(self):
  state=completed(ROOT);state['evidence'][0]['acceptance_ids']=['unrelated']
  with self.assertRaisesRegex(team.ContractError,'does not cover'):team.readiness(state,'v1')
 def test_unreferenced_failure_blocks_and_explicit_rerun_resolves(self):
  state=completed(ROOT);state['evidence'][0]['timestamp']='2026-10-28T08:00:00Z'
  failure=dict(state['evidence'][0],evidence_id='FAIL1',outcome='FAIL',exit_code=1,timestamp='2026-10-28T08:01:00Z');state['evidence'].append(failure)
  with self.assertRaisesRegex(team.ContractError,'Unresolved'):team.readiness(state,'v1')
  before=copy.deepcopy(state['evidence'])
  state['evidence'].append(dict(state['evidence'][0],evidence_id='RERUN1',timestamp='2026-10-28T08:02:00Z',supersedes=['FAIL1']))
  state['tasks'][0]['evidence_refs']=['RERUN1']
  self.assertEqual(team.readiness(state,'v1')['verdict'],'PASS')
  self.assertEqual(state['evidence'][:2],before)
 def test_missing_and_changed_artifact_blocks(self):
  for path,sha in [('nonexistent-review-artifact','a'*64),('README.md','a'*64)]:
   state=completed(ROOT);state['artifacts'][0].update(path=path,sha256=sha)
   with self.assertRaisesRegex(team.ContractError,'artifact'):team.readiness(state,'v1')
 def test_requirement_description_updated(self):
  state=sample(ROOT);state['requirements'][0]['description']='old'
  changed=team.change_requirement(state,'R1','new')
  self.assertEqual(changed['requirements'][0]['description'],'new')
  self.assertEqual(changed['decisions'][0]['previous']['description'],'old')
 def test_empty_resume_hash_map_blocks(self):
  with self.assertRaisesRegex(team.ContractError,'coverage'):team.resume(completed(ROOT),ROOT,{})
 def test_public_checkpoint_roundtrip(self):
  state=completed(ROOT);document=team.checkpoint(state,'test-only-authorization')
  jsonschema.validate(document,json.loads((ROOT/'skills/agency-workflow/references/schemas/checkpoint.schema.json').read_text()))
  loaded=team.load_state(document)
  self.assertEqual(loaded,state);self.assertTrue(team.resume(loaded,ROOT,document['expected_hashes'])['authorization_recheck_required'])
  document['tasks']=[]
  with self.assertRaises(team.ContractError):team.load_state(document)
 def test_evidence_schema_rejects_failed_command_pass(self):
  schema=json.loads((ROOT/'skills/agency-workflow/references/schemas/evidence.schema.json').read_text());data=json.loads((ROOT/'skills/agency-workflow/assets/templates/evidence.json').read_text());data.update(kind='command',exit_code=1,outcome='PASS')
  with self.assertRaises(jsonschema.ValidationError):jsonschema.validate(data,schema)
 def test_shared_graph_is_linear(self):
  state=sample(ROOT);state['tasks']=[]
  for layer in range(40):
   for side in range(2):state['tasks'].append(dict(task_id=f'{layer}-{side}',requirement_ids=['R1'],acceptance_ids=['A1'],owner_role='developer',status='PLANNED',dependencies=[] if layer==0 else [f'{layer-1}-0',f'{layer-1}-1']))
  original=team.require
  with patch.object(team,'require',wraps=original) as checks:team.validate(state);self.assertLess(checks.call_count,5000)
 def test_legacy_markers_and_failed_write_do_not_wedge(self):
  with tempfile.TemporaryDirectory() as folder:
   target=Path(folder)/'state.json';state=sample(folder);team.save(target,state);before=team.digest(target)
   target.with_suffix('.json.tmp').write_text('legacy interrupted write')
   with patch.object(team.json,'dump',side_effect=OSError('injected disk failure')):
    with self.assertRaises(OSError):team.save(target,state,before)
   self.assertEqual(team.digest(target),before)
   team.save(target,state,before)
   self.assertEqual(team.digest(target),before)
 def test_process_crash_releases_writer_lock(self):
  with tempfile.TemporaryDirectory() as folder:
   target=Path(folder)/'state.json'
   code='from scripts.team import writer_lock;from pathlib import Path;import os\nwith writer_lock(Path('+repr(str(target.with_suffix('.json.lock')))+')): os._exit(7)'
   result=subprocess.run([sys.executable,'-c',code],cwd=ROOT,timeout=10)
   self.assertEqual(result.returncode,7);team.save(target,sample(folder))

class PackagingRegressions(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
  for name in ['plugin.json','package-files.json']:shutil.copy2(ROOT/name,self.root/name)
  shutil.copytree(ROOT/'skills',self.root/'skills');shutil.copytree(ROOT/'tests/schemas',self.root/'tests/schemas')
 def tearDown(self):self.temp.cleanup()
 def test_secret_file_rejected(self):
  (self.root/'skills/agency-workflow/.env').write_text('DB_PASSWORD=example-only')
  with self.assertRaisesRegex(ValueError,'allowlist'):build(self.root)
 def test_missing_resource_rejected(self):
  (self.root/'skills/agency-workflow/assets/templates/checkpoint.json').rename(self.root/'removed-template.json')
  with self.assertRaisesRegex(ValueError,'allowlist'):build(self.root)
 def test_optimized_python_still_rejects_extra_file(self):
  (self.root/'skills/agency-workflow/.env').write_text('DB_PASSWORD=example-only')
  code='from scripts.package import build;build('+repr(str(self.root))+')'
  result=subprocess.run([sys.executable,'-O','-c',code],cwd=ROOT,capture_output=True,text=True,timeout=20)
  self.assertNotEqual(result.returncode,0);self.assertIn('allowlist',result.stderr)
 def test_browser_dependency_declared(self):
  requirements=(ROOT/'requirements-dev.txt').read_text();self.assertRegex(requirements,r'(?m)^playwright==[0-9]')
