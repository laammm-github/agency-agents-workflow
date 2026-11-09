import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import team, workflow_v2 as workflow

ROOT = Path(__file__).resolve().parents[1]
ROLE = 'engineering-frontend-developer'


def fixture(root, mode='DEVELOPMENT'):
    (root/'app.txt').write_text('source', encoding='utf-8')
    (root/'output.txt').write_text('observed fixture output', encoding='utf-8')
    state = workflow.fresh('fixture', root, evidence_policy_version=1)
    stamp = state['updated_at']
    common = dict(schema_version=2, project_id='fixture', revision=0, updated_at=stamp)
    state['requirements'] = [dict(common, requirement_id='R1', version=1, description='fixture requirement',
        acceptance_ids=['A1'], open_questions=[], source='test fixture', non_goals=[], priority='P1', confirmation_ref='test authorization')]
    checks = sorted(workflow.MIN_CHECKS[mode])
    state['tasks'] = [dict(common, task_id='T1', requirement_ids=['R1'], owner_role=ROLE, dependencies=[],
        acceptance_ids=['A1'], artifact_refs=['F1'], evidence_refs=[], status='PLANNED', deliverables=['app.txt'],
        blocker_refs=[], passed_acceptance_ids=[], mode=mode, required_checks=checks,
        input_hashes={'app.txt':team.digest(root/'app.txt')}, handoff_refs=[])]
    state['artifacts'] = [dict(common, artifact_id='F1', path='app.txt', sha256=team.digest(root/'app.txt'),
        requirement_ids=['R1'], task_ids=['T1'], version='v1', producer=ROLE, supersedes=None, category='SOURCE')]
    catalog = json.loads((ROOT/'skills/agency-workflow/references/agent-catalog.json').read_text(encoding='utf-8'))
    role = next(r for r in catalog if r['corpus_id'] == ROLE)
    state['role_reads'] = [dict(role_id=ROLE, path=role['path'], sha256=role['content_sha256'],
                               observation='UNVERIFIED', evidence_ref='test-fixture-role-guidance')]
    state['candidate'] = dict(candidate_id='v1', manifest=workflow.source_hashes(state), integration_evidence_refs=[])
    return state


def evidence(state, root, eid, check, **overrides):
    result = dict(schema_version=2, project_id='fixture', revision=state['revision'], updated_at=state['updated_at'],
        evidence_id=eid, tool='fixture-tool', kind='command', exit_code=0, candidate='v1', outcome='PASS',
        artifact_ref='output.txt', timestamp=workflow.now(), task_id='T1', target_scope='fixture', operation='fixture verification',
        mutates=False, summary='test-only simulated evidence, not host acceptance', acceptance_ids=['A1'], supersedes=[],
        requirement_versions={'R1':1}, input_hashes=state['tasks'][0]['input_hashes'].copy(), check=check,
        provenance='HOST_RETURN', review_kind='ROLE_PHASE' if check=='review' else 'NOT_APPLICABLE',
        output_sha256=team.digest(root/'output.txt'))
    result.update(overrides)
    return result


def completed(root, mode='DEVELOPMENT'):
    state = fixture(root, mode)
    for status in ['PREFLIGHT', 'EXECUTING', 'VERIFYING']:
        state = team.transition(state, 'T1', status)
    for check in state['tasks'][0]['required_checks']:
        eid = 'E-'+check
        state['evidence'].append(evidence(state, root, eid, check))
        state['tasks'][0]['evidence_refs'].append(eid)
    state['evidence'].append(evidence(state, root, 'E-final', 'integration'))
    state['tasks'][0]['evidence_refs'].append('E-final')
    state['candidate']['integration_evidence_refs'] = ['E-final']
    return team.transition(state, 'T1', 'COMPLETED')


class WorkflowV2Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name)
    def tearDown(self): self.temp.cleanup()

    def test_roundtrip_full_schema_and_resume(self):
        state = completed(self.root); doc = team.checkpoint(state, 'test authorization')
        self.assertEqual(team.load_state(doc), state)
        self.assertEqual(team.resume(doc, self.root)['status'], 'PREFLIGHT')
        self.assertEqual(team.readiness(state, 'v1')['verdict'], 'PASS')

    def test_missing_full_record_fields_rejected(self):
        state = fixture(self.root); del state['requirements'][0]['confirmation_ref']
        with self.assertRaisesRegex(team.ContractError, 'confirmation_ref'): team.validate(state)

    def test_document_and_research_do_not_require_code_tests(self):
        for mode in ['DOCUMENTATION', 'RESEARCH']:
            state = completed(self.root, mode)
            self.assertEqual(state['tasks'][0]['required_checks'], ['inspection'])

    def test_development_cannot_omit_mode_gate(self):
        state = fixture(self.root); state['tasks'][0]['required_checks'] = ['inspection']
        with self.assertRaisesRegex(team.ContractError, 'mode checks'): team.validate(state)

    def test_failed_or_model_only_evidence_cannot_complete(self):
        state = completed(self.root)
        state['evidence'][0]['provenance'] = 'MODEL_JUDGMENT'
        with self.assertRaises(team.ContractError): team.validate(state)
        state['evidence'][0]['provenance'] = 'HOST_RETURN'
        state['evidence'].append(evidence(state,self.root,'F','test',outcome='FAIL',exit_code=1))
        with self.assertRaisesRegex(team.ContractError, 'QA failure'): team.validate(state)

    def test_stale_requirement_or_input_evidence_rejected(self):
        for field, value in [('requirement_versions', {'R1':2}), ('input_hashes', {})]:
            state = completed(self.root); state['evidence'][0][field] = value
            with self.assertRaises(team.ContractError): team.validate(state)

    def test_output_tampering_blocks_readiness(self):
        state = completed(self.root); (self.root/'output.txt').write_text('changed')
        with self.assertRaisesRegex(team.ContractError, 'tool output'): team.readiness(state,'v1')

    def test_final_candidate_integration_cannot_be_reused_for_other_candidate(self):
        state = completed(self.root)
        state['candidate']['candidate_id'] = 'v2'
        with self.assertRaisesRegex(team.ContractError, 'integration'): team.readiness(state,'v2')
        state['evidence'][-1]['candidate'] = 'v2'
        self.assertEqual(team.readiness(state,'v2')['verdict'],'PASS')
        self.assertEqual(state['evidence'][0]['candidate'],'v1')

    def test_incomplete_candidate_and_external_change_block(self):
        state = completed(self.root); state['candidate']['manifest'] = {}
        with self.assertRaisesRegex(team.ContractError, 'manifest'): team.readiness(state,'v1')
        doc = team.checkpoint(state,'test authorization')
        (self.root/'app.txt').write_text('external edit')
        with self.assertRaisesRegex(team.ContractError, 'changed input'): team.resume(doc,self.root)

    def test_completion_needs_history_and_matching_projection(self):
        state = completed(self.root); state['events'] = []
        with self.assertRaisesRegex(team.ContractError, 'history'): team.validate(state)
        doc = team.checkpoint(completed(self.root),'test authorization'); doc['evidence_refs'] = []
        with self.assertRaisesRegex(team.ContractError, 'metadata'): team.load_state(doc)

    def test_change_invalidates_tasks_and_final_gate_preserving_history(self):
        state = completed(self.root); before = copy.deepcopy(state['evidence'])
        changed = team.change_requirement(state,'R1','updated requirement')
        self.assertEqual(changed['tasks'][0]['status'],'PLANNED')
        self.assertEqual(changed['requirements'][0]['version'],2)
        self.assertEqual(changed['evidence'],before)
        self.assertFalse(changed['candidate']['integration_evidence_refs'])
        self.assertEqual(changed['decisions'][0]['previous'],state['requirements'][0])

    def test_dependencies_need_explicit_resolved_handoff(self):
        state = completed(self.root)
        task = copy.deepcopy(state['tasks'][0]); task.update(task_id='T2', status='PREFLIGHT', dependencies=['T1'], evidence_refs=[], passed_acceptance_ids=[])
        state['revision'] += 1
        state['events'].append(dict(task_id='T2', **{'from':'PLANNED'}, to='PREFLIGHT', revision=state['revision'],timestamp=workflow.now(),evidence_refs=[],dependencies=['T1']))
        state['tasks'].append(task)
        with self.assertRaisesRegex(team.ContractError,'handoff'): team.transition(state,'T2','EXECUTING')
        common=dict(schema_version=2,project_id='fixture',revision=state['revision'],updated_at=workflow.now())
        state['handoffs']=[dict(common,stage_id='H1',requirement_ids=['R1'],acceptance_ids=['A1'],producer_role=ROLE,consumer_role=ROLE,
            artifact_refs=['F1'],evidence_refs=['E-test'],open_questions=[],next_preconditions=[],authorization_ref='test authorization',risks=[],
            producer_task_id='T1',consumer_task_id='T2',resolved=True,requirement_versions={'R1':1})]
        task['handoff_refs']=['H1']
        self.assertEqual(team.transition(state,'T2','EXECUTING')['tasks'][1]['status'],'EXECUTING')

    def test_three_repairs_then_block_execution(self):
        state = fixture(self.root)
        for i in range(4):
            for status in ['PREFLIGHT','EXECUTING','FAILED']: state=team.transition(state,'T1',status)
        state=team.transition(state,'T1','PREFLIGHT')
        with self.assertRaisesRegex(team.ContractError,'exhausted'):team.transition(state,'T1','EXECUTING')

    def test_save_preserves_evidence_and_old_checkpoint_on_error(self):
        doc=team.checkpoint(completed(self.root),'test authorization'); path=self.root/'checkpoint.json'
        team.save(path,doc); before=team.digest(path)
        changed=copy.deepcopy(doc);changed['state']['revision']+=1;changed['revision']+=1
        changed['state']['evidence'][0]['summary']='rewritten'
        with self.assertRaisesRegex(team.ContractError,'immutable'):team.save(path,changed,before)
        self.assertEqual(team.digest(path),before)
        with self.assertRaisesRegex(team.ContractError,'Stale'):team.save(path,changed,'a'*64)

    def test_migration_requires_complete_proposal_and_keeps_source(self):
        old=team.fresh('fixture',self.root)
        doc=team.checkpoint(workflow.fresh('fixture',self.root),'test authorization')
        migrated=workflow.migrate(old,doc)
        self.assertEqual(migrated['state']['legacy_snapshot'],old)
        broken=copy.deepcopy(doc);del broken['authorization_ref']
        with self.assertRaisesRegex(team.ContractError,'authorization_ref'):workflow.migrate(old,broken)

    def test_report_is_state_projection_and_unknown_actions_block_resume(self):
        state=completed(self.root)
        self.assertIn('| T1 | '+ROLE+' | COMPLETED |',workflow.report(state))
        # PLANNED records can preserve unknown operations for investigation.
        state=fixture(self.root);state['pending_operations']=['unknown deployment']
        doc=team.checkpoint(state,'test authorization')
        with self.assertRaisesRegex(team.ContractError,'unknown side effects'):team.resume(doc,self.root)

    def test_cli_v2_default_and_explicit_v1(self):
        for version in [1,2]:
            path=self.root/f'v{version}.json'
            result=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/team.py'),'init',str(path),'--workspace',str(self.root),
                '--project-id','fixture','--authorization-ref','test authorization','--schema-version',str(version)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(path.read_text(encoding='utf-8'))['schema_version'],version)

    def test_input_invalidation_keeps_requirement_and_other_history(self):
        state=completed(self.root)
        changed=workflow.invalidate(state,'T1','observed code change')
        self.assertEqual(changed['requirements'],state['requirements'])
        self.assertEqual(changed['evidence'],state['evidence'])
        self.assertEqual(changed['tasks'][0]['status'],'PLANNED')
        self.assertEqual(changed['events'][:len(state['events'])],state['events'])

    def test_v2_template_after_replacing_observed_values(self):
        doc=json.loads((ROOT/'skills/agency-workflow/assets/templates/v2/checkpoint.json').read_text(encoding='utf-8'))
        doc.update(project_id='fixture',workspace=str(self.root),updated_at=workflow.now(),authorization_ref='test authorization')
        doc['state'].update(project_id=doc['project_id'],workspace=doc['workspace'],updated_at=doc['updated_at'])
        self.assertFalse(workflow.schema_errors(doc))
        self.assertEqual(team.load_state(doc)['tasks'],[])

    def test_unknown_operation_can_be_saved_but_blocks_execution(self):
        state=fixture(self.root)
        for status in ['PREFLIGHT','EXECUTING']:state=team.transition(state,'T1',status)
        state['pending_operations']=['unknown prior tool side effect']
        doc=team.checkpoint(state,'test authorization')
        self.assertEqual(team.load_state(doc)['pending_operations'],state['pending_operations'])
        with self.assertRaisesRegex(team.ContractError,'unknown side effects'):team.resume(doc,self.root)

    def test_save_cannot_rewrite_or_drop_historical_artifacts(self):
        state=fixture(self.root);doc=team.checkpoint(state,'test authorization')
        changed=copy.deepcopy(doc);changed['revision']+=1;changed['state']['revision']+=1
        changed['state']['artifacts'][0]['version']='rewritten-history'
        with self.assertRaisesRegex(team.ContractError,'immutable'):workflow.immutable_history(doc,changed)

    def test_defect_cannot_close_using_review_as_regression(self):
        state=completed(self.root)
        common=dict(schema_version=2,project_id='fixture',revision=state['revision'],updated_at=workflow.now())
        state['defects']=[dict(common,defect_id='D1',status='CLOSED',blocking=True,reproduction='fixture',expected='pass',actual='failed',
            owner_role=ROLE,fix_task_id='T1',regression_evidence=['E-review'],severity='P1',candidate='v1',evidence_refs=['E-review'])]
        with self.assertRaisesRegex(team.ContractError,'matching regression'):team.validate(state)
        state['defects'][0]['regression_evidence']=['E-test']
        self.assertEqual(team.readiness(state,'v1')['verdict'],'PASS')

    def test_wrong_check_cannot_supersede_failure(self):
        state=fixture(self.root)
        for status in ['PREFLIGHT','EXECUTING','VERIFYING']:state=team.transition(state,'T1',status)
        state['evidence']=[evidence(state,self.root,'F','test',outcome='FAIL',exit_code=1,timestamp='2026-01-01T00:00:00Z'),
            evidence(state,self.root,'P-test','test'),evidence(state,self.root,'P-review','review',supersedes=['F'])]
        state['tasks'][0]['evidence_refs']=['P-test','P-review']
        with self.assertRaisesRegex(team.ContractError,'QA failure'):team.transition(state,'T1','COMPLETED')
        state['evidence'][1]['supersedes']=['F']
        self.assertEqual(team.transition(state,'T1','COMPLETED')['tasks'][0]['status'],'COMPLETED')

    def test_empty_checkpoint_is_not_implementation_preflight(self):
        doc=team.checkpoint(workflow.fresh('fixture',self.root),'test authorization')
        with self.assertRaisesRegex(team.ContractError,'Persist requirements'):workflow.preflight(doc,'T1')
        state=fixture(self.root)
        with self.assertRaisesRegex(team.ContractError,'EXECUTING'):workflow.preflight(team.checkpoint(state,'test authorization'),'T1')
        for status in ['PREFLIGHT','EXECUTING']:state=team.transition(state,'T1',status)
        self.assertEqual(workflow.preflight(team.checkpoint(state,'test authorization'),'T1')['record_gate'],'PASS')

    def test_verified_inputs_must_cover_task_source_deliverables(self):
        state=completed(self.root)
        state['tasks'][0]['input_hashes']={}
        for e in state['evidence']:e['input_hashes']={}
        with self.assertRaises(team.ContractError):team.validate(state)

    def test_input_change_cannot_discard_unresolved_failure(self):
        state=fixture(self.root)
        for status in ['PREFLIGHT','EXECUTING','VERIFYING']:state=team.transition(state,'T1',status)
        failure=evidence(state,self.root,'F','test',outcome='FAIL',exit_code=1,timestamp='2026-01-01T00:00:00Z')
        state['tasks'][0]['input_hashes']['output.txt']=team.digest(self.root/'output.txt')
        state['evidence']=[failure,evidence(state,self.root,'P-test','test'),evidence(state,self.root,'P-review','review')]
        state['tasks'][0]['evidence_refs']=['P-test','P-review']
        with self.assertRaisesRegex(team.ContractError,'QA failure'):team.transition(state,'T1','COMPLETED')
        state['evidence'][1]['supersedes']=['F']
        self.assertEqual(team.transition(state,'T1','COMPLETED')['tasks'][0]['status'],'COMPLETED')

    def test_checkpoint_cannot_escape_or_include_its_own_hash(self):
        state=workflow.fresh('fixture',self.root);doc=team.checkpoint(state,'test authorization')
        outside=self.root.parent/(self.root.name+'-outside.json')
        with self.assertRaisesRegex(team.ContractError,'inside project'):team.save(outside,doc)
        self.assertFalse(outside.exists())
        path=self.root/'checkpoint.json';team.save(path,doc);before=team.digest(path)
        state['revision']+=1
        circular=team.checkpoint(state,'test authorization',{'checkpoint.json':before})
        with self.assertRaisesRegex(team.ContractError,'hash itself'):team.save(path,circular,before)
        self.assertEqual(team.digest(path),before)

    def test_design_preflight_cannot_certify_source_writes(self):
        state=fixture(self.root,'DOCUMENTATION')
        for status in ['PREFLIGHT','EXECUTING']:state=team.transition(state,'T1',status)
        doc=team.checkpoint(state,'test authorization')
        self.assertFalse(workflow.preflight(doc,'T1')['source_task_ready'])
        with self.assertRaisesRegex(team.ContractError,'development/integration'):
            workflow.preflight(doc,'T1','implementation',['app.txt'])
        state=fixture(self.root)
        for status in ['PREFLIGHT','EXECUTING']:state=team.transition(state,'T1',status)
        doc=team.checkpoint(state,'test authorization')
        self.assertTrue(workflow.preflight(doc,'T1','implementation',['app.txt'])['source_task_ready'])
        with self.assertRaisesRegex(team.ContractError,'not declared'):
            workflow.preflight(doc,'T1','implementation',['other.py'])

    def test_checks_before_task_execution_cannot_be_attached_later(self):
        state=completed(self.root)
        state['evidence'][0]['timestamp']='2026-01-01T00:00:00Z'
        with self.assertRaisesRegex(team.ContractError,'predates task execution'):team.validate(state)

    def test_final_integration_requires_current_requirement_binding(self):
        state=completed(self.root)
        state['evidence'][-1]['requirement_versions']={'R1':2}
        with self.assertRaisesRegex(team.ContractError,'final candidate integration'):
            team.readiness(state,'v1')

    def test_read_commands_reject_stale_expected_digest(self):
        path=self.root/'checkpoint.json'
        team.save(path,team.checkpoint(completed(self.root),'test authorization'))
        for operation in ['validate','report','resume']:
            args=[sys.executable,'-B',str(ROOT/'scripts/team.py'),operation,str(path),
                  '--expected-digest','a'*64]
            if operation=='resume': args+=['--workspace',str(self.root)]
            result=subprocess.run(args,capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0,operation+' accepted stale checkpoint')
            self.assertIn('Stale checkpoint',result.stderr)
            args[args.index('--expected-digest')+1]=team.digest(path)
            result=subprocess.run(args,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(result.stdout)['checkpoint_digest'],team.digest(path))

    def test_read_command_honors_active_checkpoint_writer(self):
        path=self.root/'checkpoint.json'
        team.save(path,team.checkpoint(completed(self.root),'test authorization'))
        with team.writer_lock(path.with_suffix(path.suffix+'.lock')):
            result=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/team.py'),'validate',str(path)],
                                  capture_output=True,text=True,timeout=10)
        self.assertNotEqual(result.returncode,0,'read bypassed active checkpoint writer')
