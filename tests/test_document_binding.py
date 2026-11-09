import json
import tempfile
import unittest
from pathlib import Path

from scripts import team, workflow_v2 as workflow
from test_workflow_v2 import fixture, evidence


class DocumentBindingTests(unittest.TestCase):
    def document(self, root, bound, mode='DOCUMENTATION'):
        state = fixture(root, mode=mode)
        state['evidence_policy_version'] = 2
        state['artifacts'][0]['category'] = 'DOCUMENT'
        if not bound:
            state['tasks'][0]['input_hashes'] = {}
        for status in ['PREFLIGHT', 'EXECUTING', 'VERIFYING']:
            state = team.transition(state, 'T1', status)
        record = evidence(state, root, 'READ', 'inspection', artifact_ref='capture.json',
                          kind='file_read', exit_code=None, review_kind='NOT_APPLICABLE')
        capture = dict(capture_version=1, tool=record['tool'], arguments={'path': str(root/'app.txt')},
                       response={'success': True, 'status': 'completed', 'data': {'content': 'source'}},
                       observed_at=record['timestamp'], input_hashes=record['input_hashes'])
        (root/'capture.json').write_text(json.dumps(capture), encoding='utf-8')
        record['output_sha256'] = team.digest(root/'capture.json')
        state['evidence'] = [record]
        state['tasks'][0]['evidence_refs'] = ['READ']
        return state

    def test_document_completion_rejects_unbound_deliverable(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = self.document(Path(tmp), False)
            with self.assertRaisesRegex(team.ContractError, 'Verified inputs omit task deliverable'):
                team.transition(state, 'T1', 'COMPLETED')

    def test_document_inspection_completes_without_code_test(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = self.document(Path(tmp), True)
            state = team.transition(state, 'T1', 'COMPLETED')
            self.assertEqual(state['tasks'][0]['status'], 'COMPLETED')
            self.assertEqual({e['check'] for e in state['evidence']}, {'inspection'})

    def test_research_document_output_also_binds_its_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = self.document(Path(tmp), False, mode='RESEARCH')
            with self.assertRaisesRegex(team.ContractError, 'Verified inputs omit task deliverable'):
                team.transition(state, 'T1', 'COMPLETED')
