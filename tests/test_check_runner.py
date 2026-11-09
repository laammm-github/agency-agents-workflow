"""Actual bounded subprocesses, not simulated host acceptance."""
import base64
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import team, workflow_v2 as workflow, check_runner
from test_workflow_v2 import fixture


class CheckRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.checkpoint = self.root/'checkpoint.json'
        s = fixture(self.root)
        s['evidence_policy_version'] = 2
        for status in ['PREFLIGHT', 'EXECUTING']:
            s = workflow.transition(s, 'T1', status)
        team.save(self.checkpoint, workflow.checkpoint(s, 'test authorization'))

    def tearDown(self):
        self.temp.cleanup()

    def state(self):
        return team.load_state(team.read_document(self.checkpoint)[0])

    def run_child(self, eid, source, **kwargs):
        return check_runner.run_check(self.checkpoint, team.digest(self.checkpoint), 'T1', eid,
              'evidence/'+eid+'.json', [sys.executable, '-B', '-c', source], **kwargs)

    def test_failure_is_saved_before_return_and_repair(self):
        result = self.run_child('FAIL1', "import sys; print('failed check'); sys.exit(3)")
        self.assertEqual(result['exit_code'], 3)
        s = self.state()
        self.assertEqual(s['tasks'][0]['status'], 'FAILED')
        self.assertFalse(s['pending_operations'])
        self.assertEqual(s['evidence'][-1]['outcome'], 'FAIL')
        self.assertEqual(s['events'][-1]['to'], 'FAILED')
        saved = json.loads((self.root/'evidence/FAIL1.json').read_text(encoding='utf-8'))
        self.assertEqual(saved['response']['exit_code'], 3)
        self.assertEqual(base64.b64decode(saved['response']['stdout_base64']), b'failed check\r\n' if sys.platform=='win32' else b'failed check\n')
        # A later check cannot run until the controlled repair transitions occur.
        with self.assertRaisesRegex(team.ContractError, 'EXECUTING'):
            self.run_child('PASS1', 'pass')
        doc, digest = team.read_document(self.checkpoint)
        s = workflow.transition(s, 'T1', 'PREFLIGHT')
        s = workflow.transition(s, 'T1', 'EXECUTING')
        team.save(self.checkpoint, workflow.checkpoint(s, doc['authorization_ref'], previous=doc), digest)
        self.run_child('PASS1', 'pass', supersedes=['FAIL1'])
        s = self.state()
        self.assertFalse(workflow.unresolved(s, s['tasks'][0]))
        self.assertEqual(s['evidence'][0]['outcome'], 'FAIL')
        self.assertEqual(s['evidence'][-1]['supersedes'], ['FAIL1'])
        workflow.verify_task_files(s,s['tasks'][0])

    def test_pending_intent_is_visible_to_real_child(self):
        source="import json,pathlib; d=json.loads(pathlib.Path('checkpoint.json').read_text(encoding='utf-8')); assert d['pending_operations']; assert d['pending_operations']==d['state']['pending_operations']"
        self.assertEqual(self.run_child('PASS1',source)['outcome'], 'PASS')
        s=self.state()
        self.assertFalse(s['pending_operations'])
        workflow.verify_task_files(s,s['tasks'][0])

    def test_timeout_keeps_unknown_intent_and_blocks_resume(self):
        result=self.run_child('TIMEOUT1', 'import time; time.sleep(2)', timeout=.1)
        self.assertEqual(result['outcome'],'UNKNOWN')
        doc,_=team.read_document(self.checkpoint)
        self.assertTrue(doc['pending_operations'])
        with self.assertRaisesRegex(team.ContractError,'unknown side effects'):
            workflow.resume(doc,str(self.root))
        with self.assertRaisesRegex(team.ContractError,'Unknown side effects'):
            self.run_child('REPLAY','pass')

    def test_existing_output_blocks_execution(self):
        (self.root/'evidence').mkdir()
        (self.root/'evidence/PASS1.json').write_text('existing',encoding='utf-8')
        original=team.digest(self.checkpoint)
        with self.assertRaisesRegex(team.ContractError,'already exists'):
            self.run_child('PASS1', "from pathlib import Path; Path('should-not-exist').touch()")
        self.assertFalse((self.root/'should-not-exist').exists())
        self.assertEqual(team.digest(self.checkpoint),original)

    def test_changed_input_during_check_preserves_capture_and_pending(self):
        with self.assertRaisesRegex(team.ContractError,'changed input'):
            self.run_child('CHANGE1', "from pathlib import Path; Path('app.txt').write_text('changed')")
        self.assertTrue((self.root/'evidence/CHANGE1.json').exists())
        s=self.state()
        self.assertTrue(s['pending_operations'])
        self.assertFalse(s['evidence'])

    def test_conflicting_checkpoint_is_not_adopted(self):
        source="import json,pathlib; p=pathlib.Path('checkpoint.json'); d=json.loads(p.read_text(encoding='utf-8')); d['external_writer']='present'; p.write_text(json.dumps(d),encoding='utf-8')"
        with self.assertRaisesRegex(team.ContractError,'Stale checkpoint'):
            self.run_child('CHANGE1',source)
        d=json.loads(self.checkpoint.read_text(encoding='utf-8'))
        self.assertEqual(d['external_writer'],'present')
        self.assertTrue(d['pending_operations'])
        self.assertFalse(d['state']['evidence'])
        self.assertTrue((self.root/'evidence/CHANGE1.json').exists())

    def test_stale_digest_prevents_any_execution(self):
        with self.assertRaisesRegex(team.ContractError,'Stale checkpoint'):
            check_runner.run_check(self.checkpoint,'0'*64,'T1','P1','evidence/P1.json',
              [sys.executable,'-c',"from pathlib import Path; Path('side-effect').touch()"])
        self.assertFalse((self.root/'side-effect').exists())

    def test_launch_failure_is_unknown_without_automatic_retry(self):
        result=check_runner.run_check(self.checkpoint,team.digest(self.checkpoint),'T1','P1','evidence/P1.json',
                                    [str(self.root/'missing-executable')])
        self.assertEqual(result['outcome'],'UNKNOWN')
        self.assertTrue(self.state()['pending_operations'])

    def test_cli_nonzero_saves_failure_before_host_receives_exit(self):
        script=Path(check_runner.__file__).resolve()
        process=__import__('subprocess').run([sys.executable,'-B',str(script),str(self.checkpoint),
            '--expected-digest',team.digest(self.checkpoint),'--task-id','T1','--evidence-id','CLI1',
            '--output','evidence/CLI1.json','--argv-json',json.dumps([sys.executable,'-c','raise SystemExit(5)'])],
            capture_output=True,text=True)
        self.assertEqual(process.returncode,1,process.stderr)
        self.assertEqual(json.loads(process.stdout)['exit_code'],5)
        self.assertEqual(self.state()['tasks'][0]['status'],'FAILED')

    def test_initial_save_failure_prevents_child(self):
        original=team.digest(self.checkpoint)
        with patch.object(team,'save',side_effect=PermissionError('test-only save denial')):
            with self.assertRaises(PermissionError):
                self.run_child('P1',"from pathlib import Path; Path('effect').touch()")
        self.assertFalse((self.root/'effect').exists())
        self.assertEqual(team.digest(self.checkpoint),original)

    def test_result_commit_failure_keeps_intent_and_raw_output(self):
        save=team.save; calls=[]
        def fail_second(*args,**kwargs):
            calls.append(1)
            if len(calls)==2: raise PermissionError('test-only result commit denial')
            return save(*args,**kwargs)
        with patch.object(team,'save',side_effect=fail_second):
            with self.assertRaises(PermissionError): self.run_child('P1','print(123)')
        self.assertTrue(self.state()['pending_operations'])
        self.assertFalse(self.state()['evidence'])
        self.assertEqual(json.loads((self.root/'evidence/P1.json').read_text(encoding='utf-8'))['response']['exit_code'],0)

    def test_invalid_metadata_cannot_execute(self):
        with self.assertRaisesRegex(team.ContractError,'nonempty'):
            self.run_child('',"from pathlib import Path; Path('effect').touch()")
        self.assertFalse((self.root/'effect').exists())

    def test_omitted_supersedes_does_not_erase_failed_history(self):
        self.run_child('F1','raise SystemExit(1)')
        doc,digest=team.read_document(self.checkpoint);s=team.load_state(doc)
        for status in ['PREFLIGHT','EXECUTING']:s=workflow.transition(s,'T1',status)
        team.save(self.checkpoint,workflow.checkpoint(s,doc['authorization_ref'],previous=doc),digest)
        self.run_child('P1','pass')
        s=self.state()
        self.assertEqual([x['evidence_id'] for x in workflow.unresolved(s,s['tasks'][0])],['F1'])
        self.assertIn('F1', s['tasks'][0]['evidence_refs'])

    def test_superseding_pass_retires_current_failed_reference_not_history(self):
        failed=self.run_child('F1','raise SystemExit(7)')
        self.assertEqual(failed['outcome'],'FAIL')
        doc,digest=team.read_document(self.checkpoint)
        state=team.load_state(doc)
        self.assertIn('F1', state['tasks'][0]['evidence_refs'])
        for status in ['PREFLIGHT','EXECUTING']:
            state=workflow.transition(state,'T1',status)
        team.save(self.checkpoint,workflow.checkpoint(state,doc['authorization_ref'],previous=doc),digest)
        passed=self.run_child('P1','pass',supersedes=['F1'])
        self.assertEqual(passed['outcome'],'PASS')
        state=self.state()
        self.assertNotIn('F1',state['tasks'][0]['evidence_refs'])
        self.assertIn('P1',state['tasks'][0]['evidence_refs'])
        historical={e['evidence_id']:e for e in state['evidence']}
        self.assertEqual(historical['F1']['outcome'],'FAIL')
        self.assertEqual(historical['P1']['supersedes'],['F1'])
        self.assertTrue((self.root/'evidence/F1.json').is_file())
        self.assertEqual(workflow.unresolved(state,state['tasks'][0]),[])

    def test_committed_digest_is_not_a_later_external_write(self):
        document,old=team.read_document(self.checkpoint)
        document['revision']+=1;document['state']['revision']+=1
        replace=team.os.replace
        def replace_then_external(source,destination):
            replace(source,destination)
            Path(destination).write_bytes(b'external uncooperative writer')
        with patch.object(team.os,'replace',side_effect=replace_then_external):
            committed=team.save(self.checkpoint,document,old)
        self.assertNotEqual(committed,team.digest(self.checkpoint))
        with self.assertRaisesRegex(team.ContractError,'Stale checkpoint'):
            team.check_snapshot(self.checkpoint,committed)

    def test_cli_argv_file_and_outside_scope_rejection(self):
        script=Path(check_runner.__file__).resolve()
        before=team.digest(self.checkpoint)
        args=[sys.executable,'-B',str(script),str(self.checkpoint),'--expected-digest',before,
              '--task-id','T1','--evidence-id','P1','--output','evidence/P1.json','--argv-file']
        with tempfile.TemporaryDirectory() as outside:
            path=Path(outside)/'args.json';path.write_text(json.dumps([sys.executable,'-c','pass']),encoding='utf-8')
            result=__import__('subprocess').run(args+[str(path)],cwd=self.root,capture_output=True,text=True)
            self.assertEqual(result.returncode,1)
            self.assertIn('must stay inside project',result.stderr)
            self.assertEqual(team.digest(self.checkpoint),before)
        path=self.root/'args.json';path.write_text(json.dumps([sys.executable,'-c','print(123)']),encoding='utf-8')
        result=__import__('subprocess').run(args+[str(path)],cwd=self.root,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(self.state()['evidence'][-1]['outcome'],'PASS')


if __name__=='__main__': unittest.main()
