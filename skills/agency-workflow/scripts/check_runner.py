"""One-shot local QA with saved intent/result. No daemon, authorization or sandbox."""
import argparse
import base64
import copy
import json
import os
import subprocess
import sys
import time
from pathlib import Path

if __package__:
    from . import team, workflow_v2 as workflow
else:
    import team
    import workflow_v2 as workflow


def run_check(checkpoint, expected_digest, task_id, evidence_id, output, command,
              check='test', acceptance_ids=None, supersedes=None, timeout=60):
    document, snapshot = team.read_document(Path(checkpoint), expected_digest)
    state = team.load_state(document)
    team.require(state.get('evidence_policy_version') == 2, 'Runner requires v2 evidence policy 2')
    task = team.index(state['tasks'], 'task_id')[task_id]
    team.require(task['status'] == 'EXECUTING', 'QA requires an EXECUTING task')
    workflow.preflight(document, task_id, 'stage')
    workflow.verify_task_files(state, task)
    team.require(check in {'test', 'integration', 'security'}, 'Unsupported executable check')
    team.require(isinstance(command, list) and command and all(isinstance(x, str) and x for x in command), 'Use a nonempty argv list')
    team.require(0 < timeout <= 300, 'Timeout must be within 0..300 seconds')
    team.require(isinstance(evidence_id, str) and bool(evidence_id), 'Evidence ID must be nonempty')
    team.require(evidence_id not in team.index(state['evidence'], 'evidence_id'), 'Evidence ID already exists')
    acceptance_ids = list(task['acceptance_ids'] if acceptance_ids is None else acceptance_ids)
    team.require(acceptance_ids and all(isinstance(x,str) and x for x in acceptance_ids)
                 and len(acceptance_ids)==len(set(acceptance_ids))
                 and set(acceptance_ids) <= set(task['acceptance_ids']), 'Check acceptance IDs must belong to task')
    supersedes = list(supersedes or [])
    team.require(all(isinstance(x,str) and x for x in supersedes) and len(supersedes)==len(set(supersedes)), 'Invalid superseded failure IDs')
    records = team.index(state['evidence'], 'evidence_id')
    team.require(all(ref in records and records[ref]['task_id'] == task_id
                     and records[ref]['check'] == check and records[ref]['outcome'] != 'PASS'
                     and set(records[ref]['acceptance_ids']) <= set(acceptance_ids)
                     for ref in supersedes), 'Invalid superseded failure')
    relative = Path(output)
    team.require(relative.parts and relative.parts[0] == 'evidence' and relative.suffix == '.json', 'Capture must be a unique evidence/*.json')
    capture_path = team.inside(state['workspace'], output)
    team.require(not capture_path.exists(), 'Capture already exists; no replay or overwrite')
    capture_path.parent.mkdir(parents=True, exist_ok=True)
    inputs = copy.deepcopy(task['input_hashes'])
    team.require(inputs, 'Verification input hashes must be nonempty')
    artifacts = team.index(state['artifacts'], 'artifact_id')
    for reference in task['artifact_refs']:
        artifact = artifacts[reference]
        if artifact['category'] in {'SOURCE','CONFIG','BUILD','DOCUMENT'}:
            team.require(inputs.get(artifact['path']) == artifact['sha256'], 'Verification inputs omit task deliverable')
    workflow.check_hashes(state['workspace'], inputs)
    # Save intent with compare-and-lock BEFORE the child starts. A lost outcome
    # remains pending, including the launch/commit gap; never automatically replay.
    pending = copy.deepcopy(state)
    pending['revision'] += 1
    pending['updated_at'] = workflow.now()
    intent = 'LOCAL_QA ' + json.dumps(dict(evidence_id=evidence_id, task_id=task_id,
                 argv=command, cwd=state['workspace'], capture=output, check=check,
                 acceptance_ids=acceptance_ids, started_at=pending['updated_at']), sort_keys=True)
    pending['pending_operations'].append(intent)
    pending_doc = workflow.checkpoint(pending, document['authorization_ref'], previous=document)
    pending_digest = team.save(Path(checkpoint), pending_doc, snapshot)
    team.check_snapshot(Path(checkpoint), pending_digest)
    workflow.check_hashes(state['workspace'], inputs)
    start = workflow.now()
    started_clock = time.monotonic()
    unknown = False
    try:
        process = subprocess.run(command, cwd=state['workspace'], shell=False,
                                 capture_output=True, timeout=timeout)
        code, stdout, stderr = process.returncode, process.stdout, process.stderr
    except subprocess.TimeoutExpired as error:
        unknown = True
        code, stdout, stderr = None, error.stdout or b'', error.stderr or b''
    except OSError as error:
        # The adapter cannot prove that an arbitrary launch failure had no side
        # effects. Keep the intent and preserve the actual exception.
        unknown = True
        code, stdout, stderr = None, b'', str(error).encode('utf-8')
    observed = workflow.now()
    capture = dict(capture_version=1, tool='python.subprocess.run',
        arguments=dict(args=command, cwd=state['workspace'], shell=False, timeout=timeout),
        response=dict(success=code == 0 and not unknown,
                      status='unknown' if unknown else ('completed' if code == 0 else 'failed'),
                      exit_code=code, stdout=stdout.decode('utf-8', errors='replace'),
                      stderr=stderr.decode('utf-8', errors='replace'),
                      stdout_base64=base64.b64encode(stdout).decode('ascii'),
                      stderr_base64=base64.b64encode(stderr).decode('ascii'),
                      text_encoding='utf-8; replacement characters possible; base64 retains exact bytes',
                      started_at=start, ended_at=observed,
                      duration_ms=int((time.monotonic()-started_clock)*1000)),
        observed_at=observed, input_hashes=inputs)
    # Exclusive creation, even if another actor created the path during execution.
    with capture_path.open('x', encoding='utf-8') as stream:
        json.dump(capture, stream, ensure_ascii=False, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    team.check_snapshot(Path(checkpoint), pending_digest)
    workflow.check_hashes(state['workspace'], inputs)
    if unknown:
        return dict(outcome='UNKNOWN', exit_code=None, capture=output,
                    checkpoint_pending=True, reason='Inspect actual effects; do not replay')
    result = copy.deepcopy(pending)
    result['pending_operations'].remove(intent)
    result['revision'] += 1
    result['updated_at'] = observed
    evidence = dict(schema_version=2, project_id=state['project_id'], revision=result['revision'],
        updated_at=observed, evidence_id=evidence_id, tool='python.subprocess.run', kind='command',
        exit_code=code, candidate=state['candidate']['candidate_id'], outcome='PASS' if code == 0 else 'FAIL',
        artifact_ref=output, timestamp=observed, task_id=task_id, target_scope=state['workspace'],
        operation='One-shot local QA argv execution', mutates=True,
        summary='Actual local child-process return; outer host call and independent audit are separate',
        acceptance_ids=acceptance_ids, supersedes=supersedes if code == 0 else [],
        requirement_versions=workflow.versions(state, task), input_hashes=inputs, check=check,
        provenance='HOST_RETURN', review_kind='NOT_APPLICABLE', output_sha256=team.digest(capture_path))
    result['evidence'].append(evidence)
    current_task = team.index(result['tasks'], 'task_id')[task_id]
    if code == 0 and supersedes:
        # Keep immutable FAIL records in state.evidence and their raw captures.
        # Only a later, explicitly matching PASS retires failed evidence from
        # the task's *current* references, allowing honest completion checks.
        retired = set(supersedes)
        current_task['evidence_refs'] = [ref for ref in current_task['evidence_refs']
                                         if ref not in retired]
    current_task['evidence_refs'].append(evidence_id)
    if code != 0:
        result = workflow.transition(result, task_id, 'FAILED')
    final = workflow.checkpoint(result, document['authorization_ref'], previous=pending_doc)
    workflow.immutable_history(pending_doc, final)
    final_digest = team.save(Path(checkpoint), final, pending_digest)
    return dict(outcome=evidence['outcome'], exit_code=code, evidence_id=evidence_id,
                capture=output, checkpoint_digest=final_digest, revision=result['revision'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('checkpoint', type=Path)
    parser.add_argument('--expected-digest', required=True)
    parser.add_argument('--task-id', required=True)
    parser.add_argument('--evidence-id', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--check', choices=['test','integration','security'], default='test')
    parser.add_argument('--acceptance-id', action='append')
    parser.add_argument('--supersedes', action='append', default=[])
    parser.add_argument('--timeout', type=float, default=60)
    invocation=parser.add_mutually_exclusive_group(required=True)
    invocation.add_argument('--argv-json', help='JSON argv array; shell=False')
    invocation.add_argument('--argv-file', type=Path, help='UTF-8 JSON argv array within project')
    args = parser.parse_args()
    try:
        if args.argv_file is not None:
            document,_ = team.read_document(args.checkpoint, args.expected_digest)
            state=team.load_state(document)
            path=args.argv_file.resolve()
            team.require(path.is_relative_to(Path(state['workspace']).resolve()), 'Argv file must stay inside project')
            command=json.loads(path.read_text(encoding='utf-8-sig'))
        else:
            command=json.loads(args.argv_json)
        result = run_check(args.checkpoint, args.expected_digest, args.task_id, args.evidence_id,
                           args.output, command, args.check,
                           args.acceptance_id, args.supersedes, args.timeout)
        print(json.dumps(result, ensure_ascii=True))
        return 0 if result['outcome'] == 'PASS' else 1
    except (team.ContractError, OSError, ValueError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
