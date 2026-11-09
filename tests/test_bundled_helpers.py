import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import team, package
from test_workflow_v2 import fixture

ROOT=Path(__file__).resolve().parents[1]


class BundledHelperTests(unittest.TestCase):
    def test_helpers_execute_outside_source_repository(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name); tools=root/'tools'; project=root/'project'; project.mkdir()
            bundle=ROOT/'skills/agency-workflow'
            shutil.copytree(bundle/'scripts',tools/'scripts')
            shutil.copytree(bundle/'references/schemas',tools/'references/schemas')
            shutil.copy2(bundle/'references/agent-catalog.json',tools/'references/agent-catalog.json')
            checkpoint=project/'checkpoint.json'
            command=[sys.executable,'-B',str(tools/'scripts/team.py')]
            result=subprocess.run(command+['init',str(checkpoint),'--workspace',str(project),
                 '--project-id','independent','--authorization-ref','explicit test-only authorization'],
                 cwd=project,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(checkpoint.read_text(encoding='utf-8'))['schema_version'],2)
            # Use a fixture at a new path, retaining the initialized checkpoint.
            state=fixture(project);state['evidence_policy_version']=2
            for status in ['PREFLIGHT','EXECUTING']:state=team.transition(state,'T1',status)
            check2=project/'check2.json';team.save(check2,team.checkpoint(state,'test authorization'))
            runner=[sys.executable,'-B',str(tools/'scripts/check_runner.py'),str(check2),
                '--expected-digest',team.digest(check2),'--task-id','T1','--evidence-id','F1',
                '--output','evidence/F1.json','--argv-json',json.dumps([sys.executable,'-c','raise SystemExit(4)'])]
            result=subprocess.run(runner,cwd=project,capture_output=True,text=True)
            self.assertEqual(result.returncode,1,result.stderr)
            self.assertEqual(json.loads(result.stdout)['exit_code'],4)
            saved=json.loads(check2.read_text(encoding='utf-8'))['state']
            self.assertEqual(saved['tasks'][0]['status'],'FAILED')
            self.assertEqual(saved['evidence'][-1]['outcome'],'FAIL')
            # An actual schema-1 envelope must also load via the bundled schema.
            legacy=fixture(project);legacy['schema_version']=1
            v1=project/'legacy.json';team.save(v1,team.checkpoint(legacy,'legacy test authorization'))
            result=subprocess.run(command+['validate',str(v1)],cwd=project,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)

    def test_package_rejects_helper_drift(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name)
            for entry in ['plugin.json','package-files.json']:
                shutil.copy2(ROOT/entry,root/entry)
            for entry in ['skills','tests','scripts']:
                shutil.copytree(ROOT/entry,root/entry,ignore=shutil.ignore_patterns('__pycache__'))
            (root/'skills/agency-workflow/scripts/check_runner.py').write_text('changed',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'differs from canonical'):
                package.build(root)
