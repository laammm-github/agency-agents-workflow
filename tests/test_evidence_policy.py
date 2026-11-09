"""Regression for a model summary incorrectly accepted as a raw tool return."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts import team, workflow_v2 as workflow
from test_workflow_v2 import completed, evidence, fixture


class EvidencePolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def captured(self, state, eid, check, response, **overrides):
        record = evidence(state, self.root, eid, check,
                          artifact_ref=eid+'.json', tool='fixture-tool', **overrides)
        capture = dict(capture_version=1, tool=record['tool'], arguments={'path': str(self.root/'app.txt')},
                       response=response, observed_at=record['timestamp'], input_hashes=record['input_hashes'])
        if check == 'inspection':
            capture['observed_paths'] = ['app.txt']
        path = self.root/record['artifact_ref']
        path.write_text(json.dumps(capture), encoding='utf-8')
        record['output_sha256'] = team.digest(path)
        return record

    def strict_completed(self):
        state = fixture(self.root)
        state['evidence_policy_version'] = 2
        for status in ['PREFLIGHT','EXECUTING','VERIFYING']:
            state = team.transition(state, 'T1', status)
        source = self.captured(state, 'SOURCE', 'inspection',
            {'content':[{'type':'text','text':'source'}], 'isError':False}, exit_code=None, kind='file_read')
        test = self.captured(state, 'TEST', 'test', {'exit_code':0, 'output':'synthetic unit fixture'})
        (self.root/'review.md').write_text('ROLE_PHASE review conclusion; synthetic fixture, not host acceptance.', encoding='utf-8')
        review = evidence(state, self.root, 'REVIEW', 'review', provenance='MODEL_JUDGMENT',
            exit_code=None, kind='review', artifact_ref='review.md', supporting_evidence_refs=['SOURCE'],
            output_sha256=team.digest(self.root/'review.md'))
        final = self.captured(state, 'FINAL', 'integration',
            {'success':True, 'status':'completed', 'data':{'exitCode':0, 'stdout':{'text':'synthetic fixture'}, 'stderr':{'text':''}}})
        state['evidence'] = [source,test,review,final]
        state['tasks'][0]['evidence_refs'] = [record['evidence_id'] for record in state['evidence']]
        state['candidate']['integration_evidence_refs'] = ['FINAL']
        return team.transition(state, 'T1', 'COMPLETED')

    def test_bare_model_summary_cannot_certify_raw_test_or_readback(self):
        state = completed(self.root)
        state['evidence_policy_version'] = 2
        (self.root/'output.txt').write_text('Backend: first test failed; after code change exit 0. Observed tool.', encoding='utf-8')
        for record in state['evidence']:
            record['output_sha256'] = team.digest(self.root/'output.txt')
        with self.assertRaisesRegex(team.ContractError, 'capture|ROLE_PHASE'):
            team.readiness(state, 'v1')

    def test_legacy_v2_keeps_original_read_and_gate_path(self):
        state = completed(self.root)
        state.pop('evidence_policy_version', None)
        self.assertEqual(team.readiness(state, 'v1')['verdict'], 'PASS')

    def test_role_judgment_with_current_raw_source_observation_can_complete(self):
        state = self.strict_completed()
        self.assertEqual(team.readiness(state, 'v1')['verdict'], 'PASS')
        self.assertEqual(next(e for e in workflow.passed(state,state['tasks'][0]) if e['check']=='review')['provenance'], 'MODEL_JUDGMENT')

    def test_model_judgment_cannot_replace_execution(self):
        state = self.strict_completed()
        state['evidence'][1]['provenance'] = 'MODEL_JUDGMENT'
        with self.assertRaisesRegex(team.ContractError, 'mode verification'):
            team.readiness(state, 'v1')

    def test_bare_summary_cannot_be_used_for_test_with_legitimate_role_review(self):
        state = self.strict_completed()
        record = state['evidence'][1]
        path = self.root/record['artifact_ref']
        path.write_text('Backend passed; observed tool. This is a model summary.', encoding='utf-8')
        record['output_sha256'] = team.digest(path)
        with self.assertRaisesRegex(team.ContractError, 'Raw tool capture'):
            team.readiness(state, 'v1')

    def test_role_review_cannot_borrow_stale_source_observation(self):
        state = self.strict_completed()
        state['evidence'][0]['input_hashes'] = {'app.txt':'b'*64}
        with self.assertRaisesRegex(team.ContractError, 'supporting source'):
            team.readiness(state, 'v1')

    def test_failed_running_or_exitless_execution_cannot_be_labeled_pass(self):
        cases = [({'exit_code':1,'output':'failed'},0),
                 ({'success':True,'status':'completed','data':{'state':'running','exitCode':None}},None),
                 ({'content':[{'type':'text','text':'PASS'}]},None)]
        for response, exit_code in cases:
            with self.subTest(response=response):
                state = self.strict_completed()
                record = state['evidence'][1]
                path = self.root/record['artifact_ref']
                capture = json.loads(path.read_text(encoding='utf-8'))
                capture['response'] = response
                path.write_text(json.dumps(capture),encoding='utf-8')
                record['output_sha256'] = team.digest(path)
                record['exit_code'] = exit_code
                with self.assertRaises(team.ContractError): team.readiness(state,'v1')

    def test_capture_cannot_be_rebound_to_another_input_version(self):
        state = self.strict_completed()
        record = state['evidence'][1]
        path = self.root/record['artifact_ref']
        capture = json.loads(path.read_text(encoding='utf-8'))
        capture['input_hashes'] = {'app.txt':'b'*64}
        path.write_text(json.dumps(capture),encoding='utf-8')
        record['output_sha256'] = team.digest(path)
        with self.assertRaisesRegex(team.ContractError, 'input hashes mismatch'):
            team.readiness(state,'v1')

    def test_capture_tool_timestamp_and_exit_code_must_match_record(self):
        for field,value in [('tool','invented-composite'),('observed_at','2001-01-01T00:00:00Z')]:
            state = self.strict_completed()
            record = state['evidence'][1]
            path = self.root/record['artifact_ref']
            capture = json.loads(path.read_text(encoding='utf-8'));capture[field]=value
            path.write_text(json.dumps(capture),encoding='utf-8');record['output_sha256']=team.digest(path)
            with self.assertRaises(team.ContractError): team.readiness(state,'v1')
        state=self.strict_completed();state['evidence'][1]['exit_code']=None;state['evidence'][1]['kind']='verification'
        with self.assertRaisesRegex(team.ContractError, 'exit code differs'):
            team.readiness(state,'v1')

    def test_model_review_needs_actual_source_paths_not_summary_readback(self):
        state=self.strict_completed();record=state['evidence'][0];path=self.root/record['artifact_ref']
        capture=json.loads(path.read_text(encoding='utf-8'));capture['observed_paths']=['model-summary.md']
        path.write_text(json.dumps(capture),encoding='utf-8');record['output_sha256']=team.digest(path)
        with self.assertRaisesRegex(team.ContractError,'observed paths'):
            team.readiness(state,'v1')
        capture.pop('observed_paths');path.write_text(json.dumps(capture),encoding='utf-8');record['output_sha256']=team.digest(path)
        with self.assertRaisesRegex(team.ContractError,'source paths'):
            team.readiness(state,'v1')

    def test_raw_failure_is_not_overruled_by_a_successful_wrapper_exit(self):
        state=self.strict_completed();record=state['evidence'][1];path=self.root/record['artifact_ref']
        capture=json.loads(path.read_text(encoding='utf-8'))
        capture['response']={'isError':False,'structuredContent':{'success':False,'status':'failed','data':{'exitCode':0}}}
        path.write_text(json.dumps(capture),encoding='utf-8');record['output_sha256']=team.digest(path)
        with self.assertRaisesRegex(team.ContractError,'Captured tool failed'):
            team.readiness(state,'v1')

    def test_policy_downgrade_is_not_a_silent_update(self):
        state=workflow.fresh('fixture',self.root)
        self.assertEqual(state['evidence_policy_version'],2)
        before=team.checkpoint(state,'test authorization')
        downgraded=copy.deepcopy(state);downgraded.pop('evidence_policy_version');downgraded['revision']+=1;downgraded['updated_at']=workflow.now()
        proposal=team.checkpoint(downgraded,'test authorization')
        with self.assertRaisesRegex(team.ContractError, 'explicit migration'):
            workflow.update(before,proposal)

    def test_requirement_change_retains_historical_role_review_without_recertifying_it(self):
        state=self.strict_completed();previous=copy.deepcopy(state['evidence'])
        changed=team.change_requirement(state,'R1','changed acceptance scope')
        self.assertEqual(changed['evidence'],previous)
        self.assertEqual(changed['tasks'][0]['status'],'PLANNED')
        self.assertEqual(workflow.passed(changed,changed['tasks'][0]),[])
        team.load_state(team.checkpoint(changed,'test authorization'))

    def test_missing_dependency_tool_output_blocks_start_and_source_preflight(self):
        state=self.strict_completed();task=copy.deepcopy(state['tasks'][0])
        task.update(task_id='T2',status='PLANNED',dependencies=['T1'],evidence_refs=[],
                    passed_acceptance_ids=[],handoff_refs=['H1'])
        state['tasks'].append(task)
        state['handoffs']=[dict(schema_version=2,project_id='fixture',revision=state['revision'],updated_at=workflow.now(),
            stage_id='H1',requirement_ids=['R1'],acceptance_ids=['A1'],producer_role=task['owner_role'],consumer_role=task['owner_role'],
            artifact_refs=['F1'],evidence_refs=['TEST','REVIEW'],open_questions=[],next_preconditions=[],authorization_ref='test authorization',risks=[],
            producer_task_id='T1',consumer_task_id='T2',resolved=True,requirement_versions={'R1':1})]
        state=team.transition(state,'T2','PREFLIGHT')
        path=self.root/'TEST.json';original=path.read_bytes();path.unlink()
        with self.assertRaisesRegex(team.ContractError,'tool output'):
            team.transition(state,'T2','EXECUTING')
        path.write_bytes(original);state=team.transition(state,'T2','EXECUTING');path.unlink()
        document=team.checkpoint(state,'test authorization')
        with self.assertRaisesRegex(team.ContractError,'tool output'):
            workflow.preflight(document,'T2',purpose='implementation',write_paths=['app.txt'])


    def test_explicit_legacy_policy_upgrade_preserves_history_and_reopens_tasks(self):
        state=completed(self.root);state.pop('evidence_policy_version',None)
        original=team.checkpoint(state,'test authorization')
        reopened=workflow.invalidate(state,'T1','Explicit policy migration requires new raw captures')
        reopened['tasks'][0]['evidence_refs']=[]
        reopened['evidence_policy_version']=2
        proposal=team.checkpoint(reopened,'test authorization')
        migrated=workflow.migrate(original,proposal)
        self.assertEqual(migrated['state']['legacy_snapshot'],original)
        self.assertEqual(migrated['state']['evidence'],original['state']['evidence'])
        self.assertEqual(migrated['state']['events'][:len(state['events'])],state['events'])
        self.assertEqual(migrated['state']['tasks'][0]['status'],'PLANNED')
        self.assertNotIn('evidence_policy_version',original['state'])
        with self.assertRaises(team.ContractError):team.readiness(migrated['state'],'v1')

    def test_policy_migration_cannot_recertify_legacy_summary_or_changed_inputs(self):
        state=completed(self.root);original=team.checkpoint(state,'test authorization')
        upgraded=copy.deepcopy(state);upgraded['evidence_policy_version']=2
        with self.assertRaises(team.ContractError):
            workflow.migrate(original,team.checkpoint(upgraded,'test authorization'))
        reopened=workflow.invalidate(state,'T1','Explicit migration')
        reopened['tasks'][0]['evidence_refs']=[];reopened['evidence_policy_version']=2
        proposal=team.checkpoint(reopened,'test authorization')
        (self.root/'app.txt').write_text('external change',encoding='utf-8')
        with self.assertRaisesRegex(team.ContractError,'Missing or changed input'):
            workflow.migrate(original,proposal)

    def test_replaced_historical_output_blocks_even_when_not_currently_referenced(self):
        state=self.strict_completed()
        record=self.captured(state,'HISTORICAL','inspection',{'content':[{'type':'text','text':'old actual read fixture'}]},exit_code=None,kind='file_read')
        state['evidence'].append(record)
        (self.root/record['artifact_ref']).write_text('overwritten historical return',encoding='utf-8')
        with self.assertRaisesRegex(team.ContractError,'historical tool output'):
            team.readiness(state,'v1')
