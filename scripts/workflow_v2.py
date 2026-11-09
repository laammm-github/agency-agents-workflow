"""Versioned workflow records and gates. No executor, permissions or tool attestation."""
import copy
import json
from datetime import datetime, timezone
from pathlib import Path

import jsonschema
try:
    from . import team
except ImportError:
    import team

SCHEMA = team.schema_directory() / 'workflow-v2.schema.json'
require = team.require
ContractError = team.ContractError
RECORDS = {'requirements': 'requirement_id', 'tasks': 'task_id', 'artifacts': 'artifact_id',
           'evidence': 'evidence_id', 'handoffs': 'stage_id', 'defects': 'defect_id',
           'decisions': 'decision_id', 'releases': 'release_id', 'incidents': 'incident_id'}
MIN_CHECKS = {'DEVELOPMENT': {'test', 'review'}, 'INTEGRATION': {'integration', 'review'},
              'DOCUMENTATION': {'inspection'}, 'RESEARCH': {'inspection'}}


def now():
    return datetime.now(timezone.utc).isoformat()


def schema_errors(value, record='checkpoint'):
    schema = json.loads(SCHEMA.read_text(encoding='utf-8'))
    schema['$ref'] = '#/$defs/' + record
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    return [f"{'/'.join(map(str, e.absolute_path))}: {e.message}" for e in validator.iter_errors(value)]


def fresh(project_id, workspace, evidence_policy_version=2):
    state = team.fresh(project_id, workspace)
    state.update(schema_version=2, updated_at=now(), events=[], role_reads=[], evidence_policy_version=evidence_policy_version,
                 candidate={'candidate_id': 'unprepared', 'manifest': {}, 'integration_evidence_refs': []})
    return state


def check_hashes(workspace, hashes):
    for relative, expected in hashes.items():
        path = team.inside(workspace, relative)
        require(path.is_file() and team.digest(path) == expected, 'Missing or changed input: ' + relative)


def versions(state, task):
    req = team.index(state['requirements'], 'requirement_id')
    return {rid: req[rid]['version'] for rid in task['requirement_ids']}


def source_hashes(state):
    return {a['path']: a['sha256'] for a in team.current_artifacts(state)
            if a['category'] in {'SOURCE', 'CONFIG', 'BUILD'}}


def baseline_hashes(state):
    return {a['path']: a['sha256'] for a in team.current_artifacts(state) if a['category'] != 'RUNTIME'}


def matching(state, task, evidence):
    return (evidence['task_id'] == task['task_id']
            and evidence['requirement_versions'] == versions(state, task)
            and evidence['input_hashes'] == task['input_hashes'])


def passed(state, task):
    evidence = team.index(state['evidence'], 'evidence_id')
    return [evidence[eid] for eid in task['evidence_refs']
            if matching(state, task, evidence[eid]) and evidence[eid]['outcome'] == 'PASS'
            and not (state.get('evidence_policy_version', 1) == 2
                     and evidence[eid]['check'] == 'review'
                     and evidence[eid]['review_kind'] == 'ROLE_PHASE'
                     and evidence[eid]['provenance'] != 'MODEL_JUDGMENT')
            and (evidence[eid]['provenance'] != 'MODEL_JUDGMENT'
                 or (state.get('evidence_policy_version', 1) == 2
                     and evidence[eid]['check'] == 'review'
                     and evidence[eid]['review_kind'] == 'ROLE_PHASE'
                     and review_supported(state, task, evidence[eid])))]


def review_supported(state, task, review, current=True):
    """A role judgment can certify a review, never a test or tool observation."""
    refs = review.get('supporting_evidence_refs', [])
    records = team.index(state['evidence'], 'evidence_id')
    return bool(refs) and all(
        ref in records and (not current or ref in task['evidence_refs'])
        and records[ref]['check'] == 'inspection'
        and records[ref]['provenance'] != 'MODEL_JUDGMENT'
        and records[ref]['outcome'] == 'PASS'
        and all(records[ref][field] == review[field] for field in ['task_id','requirement_versions','input_hashes'])
        and (not current or matching(state, task, records[ref]))
        and team.evidence_time(records[ref]) <= team.evidence_time(review)
        for ref in refs)


def tool_capture(state, evidence):
    """Check a saved return's structure/status, without authenticating its origin."""
    path = team.inside(state['workspace'], evidence['artifact_ref'])
    try:
        capture = json.loads(path.read_text(encoding='utf-8-sig'))
    except (ValueError, UnicodeError) as error:
        raise ContractError('Raw tool capture must be JSON, not a model summary') from error
    errors = schema_errors(capture, 'tool_capture')
    require(not errors, 'Invalid raw tool capture: ' + '; '.join(errors))
    require(capture['tool'] == evidence['tool'], 'Capture tool mismatch')
    require(capture['input_hashes'] == evidence['input_hashes'], 'Capture input hashes mismatch')
    require(team.evidence_time({'timestamp': capture['observed_at']}) == team.evidence_time(evidence), 'Capture observation time mismatch')
    require(set(capture.get('observed_paths', [])) <= set(evidence['input_hashes']), 'Capture observed paths are not verified inputs')
    raw = capture['response']
    require(raw.get('isError') is not True, 'Captured tool returned an error')
    payload = raw.get('structuredContent', raw)
    require(isinstance(payload, dict), 'Captured tool payload must be an object')
    data = payload.get('data', {})
    data = data if isinstance(data, dict) else {}
    layers = [raw, payload, data]
    require(not any(layer.get('success') is False for layer in layers), 'Captured tool failed')
    states = {str(layer[key]).lower() for layer in layers for key in ['status', 'state'] if key in layer}
    require(not states & {'failed','error','unknown','running','pending','queued','started','cancelled','canceled','timed_out','partial'}, 'Captured tool is not a completed successful observation')
    exits = [layer[key] for layer in layers for key in ['exit_code','exitCode'] if layer.get(key) is not None]
    if exits:
        require(all(type(code) is int and code == 0 for code in exits), 'Captured execution exit code is not zero')
        require(evidence['exit_code'] == exits[0], 'Evidence exit code differs from actual capture')
    else:
        require(evidence['exit_code'] is None, 'Do not invent an exit code absent from the tool return')
    terminal_verdict = any(layer.get('verdict') == 'PASS' for layer in layers)
    if evidence['check'] in {'test','integration','security'}:
        require(exits or terminal_verdict, 'Capture lacks an actual terminal exit code or verifier verdict')
    else:
        observed = (exits or terminal_verdict or any(layer.get('success') is True for layer in layers)
                    or bool(states & {'completed','succeeded','success','passed'})
                    or (isinstance(raw.get('content'), list) and bool(raw['content'])))
        require(observed, 'Capture lacks an observable tool result')
    return capture


def unresolved(state, task):
    good = passed(state, task)
    # Changing the declared inputs must not erase an unresolved failure. A repair
    # may change inputs, but its current PASS must explicitly supersede that failure.
    return [e for e in state['evidence'] if e['task_id'] == task['task_id']
            and e['requirement_versions'] == versions(state, task) and e['outcome'] != 'PASS'
            and not any(e['evidence_id'] in p['supersedes'] and p['check'] == e['check']
                        and set(e['acceptance_ids']) <= set(p['acceptance_ids'])
                        and team.evidence_time(p) > team.evidence_time(e) for p in good)]


def validate_state(state):
    # Validate the same complete records used by the public checkpoint, even before export.
    errors = schema_errors(state, 'state')
    require(not errors, 'Invalid v2 records:\n' + '\n'.join(errors))
    indexes = {key: team.index(state[key], field) for key, field in RECORDS.items()}
    catalog_path = SCHEMA.parent.parent / 'agent-catalog.json'
    catalog = {r['corpus_id']: r for r in json.loads(catalog_path.read_text(encoding='utf-8'))}
    for read in state['role_reads']:
        require(read['role_id'] in catalog, 'Unknown role source')
        role = catalog[read['role_id']]
        require(read['path'] == role['path'] and read['sha256'] == role['content_sha256'], 'Role source mismatch')
    for key in RECORDS:
        for record in state[key]:
            require(record['project_id'] == state['project_id'], 'Foreign project record')
            require(record['revision'] <= state['revision'], 'Record revision exceeds state')
            for field, target in [('requirement_ids','requirements'),('task_ids','tasks'),('artifact_refs','artifacts'),('evidence_refs','evidence')]:
                if field in record:
                    require(set(record[field]) <= set(indexes[target]), 'Missing record reference: ' + field)
    # Retain the proven v1 ID/dependency/deliverable checks without changing its API.
    legacy = copy.deepcopy(state)
    legacy['schema_version'] = 1
    team.validate(legacy)
    for e in state['evidence']:
        require(e['task_id'] in indexes['tasks'], 'Evidence task missing')
        require(set(e['supersedes']) <= set(indexes['evidence']) and e['evidence_id'] not in e['supersedes'], 'Invalid evidence supersedes')
        require(set(e['requirement_versions']) <= set(indexes['requirements']), 'Evidence requirement missing')
        team.inside(state['workspace'], e['artifact_ref'])
        for path in e['input_hashes']: team.inside(state['workspace'], path)
        if e['check'] == 'review': require(e['review_kind'] != 'NOT_APPLICABLE', 'Review kind missing')
        if (state.get('evidence_policy_version', 1) == 2 and e['check'] == 'review'
                and e['review_kind'] == 'ROLE_PHASE'
                and e['evidence_id'] in indexes['tasks'][e['task_id']]['evidence_refs']
                and matching(state, indexes['tasks'][e['task_id']], e)):
            require(e['provenance'] == 'MODEL_JUDGMENT', 'ROLE_PHASE conclusions are MODEL_JUDGMENT; store source observations separately')
            require(e['exit_code'] is None, 'MODEL_JUDGMENT does not have an execution exit code')
            if e['outcome'] == 'PASS':
                require(review_supported(state, indexes['tasks'][e['task_id']], e, current=False), 'ROLE_PHASE review needs matching supporting source observations')
    for h in state['handoffs']:
        require(h['producer_task_id'] in indexes['tasks'] and h['consumer_task_id'] in indexes['tasks'], 'Handoff task missing')
        require(set(h['artifact_refs']) <= set(indexes['artifacts']) and set(h['evidence_refs']) <= set(indexes['evidence']), 'Handoff reference missing')
        require(set(h['requirement_ids']) <= set(indexes['requirements']), 'Handoff requirement missing')
        require(h['producer_role'] == indexes['tasks'][h['producer_task_id']]['owner_role']
                and h['consumer_role'] == indexes['tasks'][h['consumer_task_id']]['owner_role'], 'Handoff role mismatch')
    for task in state['tasks']:
        require(MIN_CHECKS[task['mode']] <= set(task['required_checks']), 'Required mode checks missing')
        require(set(task['handoff_refs']) <= set(indexes['handoffs']), 'Missing task handoff')
        require(set(task['acceptance_ids']) <= {a for rid in task['requirement_ids'] for a in indexes['requirements'][rid]['acceptance_ids']}, 'Foreign acceptance ID')
        for path in task['input_hashes']: team.inside(state['workspace'], path)
        for path in task.get('write_paths',[]): team.inside(state['workspace'], path)
        if task['status'] in {'EXECUTING', 'VERIFYING', 'COMPLETED'}:
            require(any(r['role_id'] == task['owner_role'] for r in state['role_reads']), 'Missing role usage record')
            if task['mode'] in {'DEVELOPMENT', 'INTEGRATION'}:
                require(task['input_hashes'], 'Development verification input hashes missing')
            for dep in task['dependencies']:
                incoming = [indexes['handoffs'][hid] for hid in task['handoff_refs']]
                require(any(h['producer_task_id'] == dep and h['consumer_task_id'] == task['task_id'] and h['resolved']
                            and h['requirement_versions'] == versions(state, indexes['tasks'][dep])
                            and h['artifact_refs'] and set(h['artifact_refs']) <= set(indexes['tasks'][dep]['artifact_refs'])
                            and h['evidence_refs'] and set(h['evidence_refs']) <= {e['evidence_id'] for e in passed(state,indexes['tasks'][dep])}
                            for h in incoming), 'Missing or stale dependency handoff')
        if task['status'] == 'COMPLETED':
            good = passed(state, task)
            require(set(task['required_checks']) <= {e['check'] for e in good}, 'Missing mode verification')
            require(set(task['acceptance_ids']) <= {a for e in good for a in e['acceptance_ids']}, 'Missing current acceptance evidence')
            require(not unresolved(state, task), 'Unresolved QA failure')
            for aid in task['artifact_refs']:
                artifact = indexes['artifacts'][aid]
                if (artifact['category'] in {'SOURCE','CONFIG','BUILD'}
                        or (state.get('evidence_policy_version', 1) == 2 and artifact['category'] == 'DOCUMENT')):
                    require(task['input_hashes'].get(artifact['path']) == artifact['sha256'], 'Verified inputs omit task deliverable')
            history = [e for e in state['events'] if e['task_id'] == task['task_id']]
            require(history and history[-1]['to'] == 'COMPLETED', 'Missing task transition history')
            require(history[-1]['evidence_refs'] == task['evidence_refs'], 'Completion evidence cannot be attached retrospectively')
            completed_at = team.evidence_time({'timestamp': history[-1]['timestamp']})
            require(all(team.evidence_time(e) <= completed_at for e in good), 'Evidence postdates completion')
            reset = max((i for i,e in enumerate(history) if e['to'] == 'PLANNED'), default=-1)
            started = next((e for e in history[reset+1:] if e['to'] == 'EXECUTING'), None)
            require(started is not None, 'Task execution event missing')
            started_at = team.evidence_time({'timestamp':started['timestamp']})
            require(all(team.evidence_time(e) >= started_at for e in good), 'Evidence predates task execution; rerun inside the actual task')
    previous_revision = 0
    last_status = {}
    for event in state['events']:
        require(event['task_id'] in indexes['tasks'] and set(event['evidence_refs']) <= set(indexes['evidence']), 'Event reference missing')
        require(previous_revision < event['revision'] <= state['revision'], 'Event revisions must increase')
        invalidation = event.get('reason_ref') in indexes['decisions'] and event['to'] == 'PLANNED'
        if invalidation:
            decision = indexes['decisions'][event['reason_ref']]
            require(event['task_id'] in decision['affected_tasks'], 'Invalid change propagation event')
        require(event['from'] == last_status.get(event['task_id'], 'PLANNED')
                and (invalidation or event['to'] in team.TRANSITIONS[event['from']]), 'Invalid transition history')
        if event['to'] in {'EXECUTING', 'VERIFYING', 'COMPLETED'}:
            require(all(last_status.get(dep) == 'COMPLETED' for dep in event['dependencies']), 'Dependency was not complete at execution time')
        previous_revision = event['revision']; last_status[event['task_id']] = event['to']
    for tid, status in last_status.items():
        require(indexes['tasks'][tid]['status'] == status, 'Task and event status disagree')
    for task in state['tasks']:
        require(task['status'] == 'PLANNED' or task['task_id'] in last_status, 'Task history missing')
        if task['status'] != 'PLANNED':
            latest = next(e for e in reversed(state['events']) if e['task_id'] == task['task_id'])
            require(latest['dependencies'] == task['dependencies'], 'Invalidate task before changing dependencies')
    for defect in state['defects']:
        require(defect['fix_task_id'] in indexes['tasks'], 'Defect fix task missing')
        if defect['status'] == 'CLOSED':
            fix = indexes['tasks'][defect['fix_task_id']]
            require(fix['status'] == 'COMPLETED' and defect['regression_evidence']
                    and set(defect['regression_evidence']) <= {e['evidence_id'] for e in passed(state,fix) if e['check'] in {'test','integration'}}, 'Defect needs current matching regression')
    for path in state['candidate']['manifest']: team.inside(state['workspace'], path)
    require(set(state['candidate']['integration_evidence_refs']) <= set(indexes['evidence']), 'Candidate evidence missing')
    return state


def _envelope(state, authorization_ref, hashes, previous=None):
    metadata = {'milestone': 'active', 'last_confirmed_action': None, 'next_preconditions': []}
    if previous:
        metadata.update({key: copy.deepcopy(previous[key]) for key in metadata})
    return dict(schema_version=2, project_id=state['project_id'], workspace=state['workspace'], revision=state['revision'],
                expected_hashes=copy.deepcopy(hashes), pending_operations=copy.deepcopy(state['pending_operations']),
                authorization_ref=authorization_ref, tasks=[t['task_id'] for t in state['tasks']],
                artifacts=[a['artifact_id'] for a in state['artifacts']], evidence_refs=[e['evidence_id'] for e in state['evidence']],
                updated_at=state['updated_at'], state=copy.deepcopy(state), **metadata)


def checkpoint(state, authorization_ref, expected_hashes=None, previous=None):
    validate_state(state)
    if previous:
        load_state(previous)
        require(previous['project_id'] == state['project_id'] and previous['workspace'] == state['workspace'], 'Wrong checkpoint identity')
    hashes = dict(previous['expected_hashes'] if previous and expected_hashes is None else expected_hashes or {})
    for path, sha in baseline_hashes(state).items():
        require(path not in hashes or hashes[path] == sha, 'Conflicting baseline; explicitly rebaseline')
        hashes[path] = sha
    doc = _envelope(state, authorization_ref, hashes, previous)
    load_state(doc)
    return doc


def load_state(document):
    errors = schema_errors(document)
    require(not errors, 'Invalid v2 checkpoint:\n' + '\n'.join(errors))
    state = validate_state(document['state'])
    expected = _envelope(state, document['authorization_ref'], document['expected_hashes'])
    for key in ['schema_version', 'project_id', 'workspace', 'revision', 'pending_operations', 'tasks', 'artifacts', 'evidence_refs']:
        require(document[key] == expected[key], 'Checkpoint metadata mismatch: ' + key)
    for path, sha in baseline_hashes(state).items():
        require(document['expected_hashes'].get(path) == sha, 'Incomplete or conflicting saved baseline')
    for path in document['expected_hashes']: team.inside(state['workspace'], path)
    return state


def resume(document, workspace, expected_hashes=None):
    state = load_state(document)
    require(Path(workspace).resolve() == Path(state['workspace']).resolve(), 'Wrong workspace')
    require(not state['pending_operations'], 'Resolve unknown side effects before resume')
    stored = document['expected_hashes']
    if expected_hashes is not None:
        require(all(expected_hashes.get(k) == v for k, v in stored.items()), 'Incomplete or conflicting saved baseline')
    check_hashes(workspace, expected_hashes if expected_hashes is not None else stored)
    return {'status': 'PREFLIGHT', 'authorization_recheck_required': True}


def verify_task_files(state, task):
    if state.get('evidence_policy_version', 1) == 2:
        for record in state['evidence']:
            if record.get('output_sha256'):
                path = team.inside(state['workspace'], record['artifact_ref'])
                require(path.is_file() and team.digest(path) == record['output_sha256'], 'Missing or changed historical tool output: ' + record['evidence_id'])
    check_hashes(state['workspace'], task['input_hashes'])
    for evidence in passed(state, task):
        path = team.inside(state['workspace'], evidence['artifact_ref'])
        require(path.is_file() and team.digest(path) == evidence['output_sha256'], 'Missing or changed tool output')
        if state.get('evidence_policy_version', 1) == 2:
            if evidence['provenance'] != 'MODEL_JUDGMENT':
                tool_capture(state, evidence)
            else:
                records = team.index(state['evidence'], 'evidence_id')
                captures = [tool_capture(state, records[ref]) for ref in evidence['supporting_evidence_refs']]
                require(any(capture.get('observed_paths') for capture in captures), 'ROLE_PHASE review needs captured source paths')


def verify_dependency_files(state, task):
    if state.get('evidence_policy_version', 1) != 2:
        return
    tasks = team.index(state['tasks'], 'task_id')
    pending, checked = list(task['dependencies']), set()
    while pending:
        task_id = pending.pop()
        if task_id in checked:
            continue
        dependency = tasks[task_id]
        require(dependency['status'] == 'COMPLETED', 'Dependency not complete')
        verify_task_files(state, dependency)
        checked.add(task_id)
        pending.extend(dependency['dependencies'])


def preflight(document, task_id, purpose='stage', write_paths=None):
    state = load_state(document)
    tasks = team.index(state['tasks'], 'task_id')
    require(state['requirements'] and task_id in tasks, 'Persist requirements and tasks before implementation')
    require(tasks[task_id]['status'] == 'EXECUTING', 'Advance dependency-ready task to EXECUTING before implementation')
    require(not state['pending_operations'], 'Unknown side effects block implementation')
    require(purpose in {'stage','implementation'}, 'Unknown preflight purpose')
    if purpose == 'implementation':
        require(tasks[task_id]['mode'] in {'DEVELOPMENT','INTEGRATION'}, 'Implementation requires its own development/integration task; design execution is insufficient')
        require(write_paths, 'Implementation preflight needs explicit write paths')
        declared = {team.inside(state['workspace'], p) for p in tasks[task_id].get('write_paths',tasks[task_id]['deliverables'])}
        require(all(team.inside(state['workspace'], p) in declared for p in write_paths), 'Write path is not declared by this task')
    check_hashes(state['workspace'], document['expected_hashes'])
    check_hashes(state['workspace'], tasks[task_id]['input_hashes'])
    verify_dependency_files(state, tasks[task_id])
    return {'record_gate':'PASS','task_id':task_id,'revision':state['revision'],'purpose':purpose,
            'source_task_ready':purpose == 'implementation','write_paths':write_paths or [],
            'workspace':state['workspace'],'authorization_recheck_required':True,
            'scope':'saved records/files only; not tool authorization or write interception'}


def transition(state, task_id, status):
    result = copy.deepcopy(validate_state(state))
    task = team.index(result['tasks'], 'task_id')[task_id]
    require(status in team.TRANSITIONS[task['status']], 'Illegal transition')
    if status in {'EXECUTING', 'COMPLETED'}:
        require(not result['pending_operations'], 'Unknown side effects block execution')
        verify_task_files(result, task)
        verify_dependency_files(result, task)
    if status == 'EXECUTING':
        require(not any(indexed['open_questions'] for indexed in result['requirements'] if indexed['requirement_id'] in task['requirement_ids']), 'Unresolved requirement questions')
        history = [e for e in result['events'] if e['task_id'] == task_id]
        reset = max((i for i,e in enumerate(history) if e['to']=='PLANNED'), default=-1)
        retries = sum(e['to'] == 'EXECUTING' for e in history[reset+1:])
        require(retries < 4, 'Three repair attempts exhausted; investigate blocker')
    result['revision'] += 1; result['updated_at'] = now()
    result['events'].append(dict(task_id=task_id, **{'from': task['status']}, to=status, revision=result['revision'], timestamp=result['updated_at'], evidence_refs=list(task['evidence_refs']), dependencies=list(task['dependencies'])))
    task.update(status=status, revision=result['revision'], updated_at=result['updated_at'])
    if status == 'COMPLETED': task['passed_acceptance_ids'] = list(task['acceptance_ids'])
    return validate_state(result)


def readiness(state, candidate):
    validate_state(state)
    require(state['tasks'] and all(t['status'] == 'COMPLETED' for t in state['tasks']), 'Unfinished work')
    require(not state['pending_operations'], 'Unknown side effects')
    require(all(d['status'] == 'CLOSED' for d in state['defects'] if d.get('blocking', True)), 'Blocking defects')
    for requirement in state['requirements']:
        covered = {a for t in state['tasks'] if requirement['requirement_id'] in t['requirement_ids'] for a in t['acceptance_ids']}
        require(requirement['acceptance_ids'] and set(requirement['acceptance_ids']) <= covered, 'Unimplemented requirement')
    fixed = state['candidate']
    require(candidate == fixed['candidate_id'] and fixed['manifest'] and fixed['manifest'] == source_hashes(state), 'Candidate manifest mismatch')
    check_hashes(state['workspace'], fixed['manifest'])
    check_hashes(state['workspace'], baseline_hashes(state))
    for task in state['tasks']: verify_task_files(state, task)
    # The final generated task board is a live state projection, not candidate source.
    board = team.inside(state['workspace'], 'TASKS.md')
    board_required = board.exists() or any(
        t['task_id'] in {'DELIVERY', 'HANDOVER'} for t in state['tasks'])
    if board_required:
        require(board.is_file(), 'Missing final live task board TASKS.md')
        actual = board.read_text(encoding='utf-8-sig').replace('\r\n', '\n').strip()
        require(actual == report(state).strip(),
                'Stale final live task board TASKS.md: regenerate from latest checkpoint')
    evidence = team.index(state['evidence'], 'evidence_id')
    require(any(evidence[eid]['outcome'] == 'PASS' and evidence[eid]['provenance'] != 'MODEL_JUDGMENT'
                and evidence[eid]['check'] == 'integration' and evidence[eid]['candidate'] == candidate
                and evidence[eid]['input_hashes'] == fixed['manifest']
                and evidence[eid] in passed(state, team.index(state['tasks'], 'task_id')[evidence[eid]['task_id']])
                for eid in fixed['integration_evidence_refs']), 'Missing final candidate integration verification')
    result = {'verdict': 'PASS', 'candidate': candidate, 'deployed': False,
              'scope': 'record consistency and file checks; tool execution is not authenticated'}
    if state.get('evidence_policy_version', 1) == 2:
        result.update(evidence_policy_version=2, raw_capture_gate='PASS', execution_authentication='UNKNOWN',
                      scope='records, file hashes and captured-return structure/status; origin and execution are not independently authenticated')
    return result


def change_requirement(state, requirement_id, description):
    result = copy.deepcopy(validate_state(state))
    requirement = team.index(result['requirements'], 'requirement_id')[requirement_id]
    previous = copy.deepcopy(requirement)
    affected = {t['task_id'] for t in result['tasks'] if requirement_id in t['requirement_ids']}
    while True:
        extended = affected | {t['task_id'] for t in result['tasks'] if set(t['dependencies']) & affected}
        if extended == affected: break
        affected = extended
    result['revision'] += 1; result['updated_at'] = now()
    requirement.update(version=requirement['version'] + 1, description=description,
                       revision=result['revision'], updated_at=result['updated_at'])
    decision_id = 'change-' + str(result['revision'])
    result['decisions'].append(dict(schema_version=2, decision_id=decision_id, requirement_id=requirement_id,
        previous=previous, reason=description, affected_tasks=sorted(affected),
        authorization_ref=previous['confirmation_ref'], new_version=requirement['version'],
        affected_artifacts=sorted({a for t in result['tasks'] if t['task_id'] in affected for a in t['artifact_refs']}),
        affected_tests=sorted({e for t in result['tasks'] if t['task_id'] in affected for e in t['evidence_refs']}),
        gates_to_revalidate=['task-acceptance', 'final-integration'], project_id=result['project_id'],
        revision=result['revision'], updated_at=result['updated_at']))
    for task in result['tasks']:
        if task['task_id'] not in affected: continue
        result['revision'] += 1
        result['events'].append(dict(task_id=task['task_id'], **{'from':task['status']}, to='PLANNED',
            revision=result['revision'], timestamp=result['updated_at'], evidence_refs=list(task['evidence_refs']), reason_ref=decision_id, dependencies=list(task['dependencies'])))
        task.update(status='PLANNED', passed_acceptance_ids=[], revision=result['revision'], updated_at=result['updated_at'])
    result['candidate']['integration_evidence_refs'] = []
    return validate_state(result)


def invalidate(state, task_id, reason):
    """Reopen impacted code work without inventing a business requirement change."""
    result = copy.deepcopy(validate_state(state))
    tasks = team.index(result['tasks'], 'task_id')
    require(task_id in tasks and reason.strip(), 'Invalidation needs task and observed reason')
    affected = {task_id}
    while True:
        extended = affected | {t['task_id'] for t in result['tasks'] if set(t['dependencies']) & affected}
        if extended == affected: break
        affected = extended
    requirement = team.index(result['requirements'], 'requirement_id')[tasks[task_id]['requirement_ids'][0]]
    result['revision'] += 1; result['updated_at'] = now()
    decision_id = 'invalidate-' + str(result['revision'])
    result['decisions'].append(dict(schema_version=2, decision_id=decision_id, requirement_id=requirement['requirement_id'],
        previous=copy.deepcopy(requirement), reason=reason, affected_tasks=sorted(affected),
        authorization_ref=requirement['confirmation_ref'], new_version=requirement['version'],
        affected_artifacts=sorted({a for tid in affected for a in tasks[tid]['artifact_refs']}),
        affected_tests=sorted({e for tid in affected for e in tasks[tid]['evidence_refs']}),
        gates_to_revalidate=['task-acceptance','final-integration'],project_id=result['project_id'],
        revision=result['revision'],updated_at=result['updated_at']))
    for tid in sorted(affected):
        task=tasks[tid];result['revision']+=1
        result['events'].append(dict(task_id=tid,**{'from':task['status']},to='PLANNED',revision=result['revision'],
            timestamp=result['updated_at'],evidence_refs=list(task['evidence_refs']),reason_ref=decision_id,dependencies=list(task['dependencies'])))
        task.update(status='PLANNED',passed_acceptance_ids=[],revision=result['revision'],updated_at=result['updated_at'])
    result['candidate']['integration_evidence_refs']=[]
    return validate_state(result)


def report(state):
    validate_state(state)
    lines = [f"# {state['project_id']}", f"Revision: {state['revision']}", '', '| Task | Role | Status | Evidence |', '|---|---|---|---|']
    for task in state['tasks']:
        cells = [task['task_id'], task['owner_role'], task['status'], ', '.join(task['evidence_refs'])]
        lines.append('| ' + ' | '.join(c.replace('|', '\\|').replace('\n', ' ') for c in cells) + ' |')
    lines += ['', 'Recorded state only; not independent proof of tool execution.',
              f"Unknown operations: {len(state['pending_operations'])}",
              f"Unverified role reads: {sum(r['observation'] == 'UNVERIFIED' for r in state['role_reads'])}"]
    if state.get('evidence_policy_version', 1) == 2:
        lines.append('Evidence policy: 2; captured tool returns and supported ROLE_PHASE judgments; execution origin unauthenticated.')
    return '\n'.join(lines) + '\n'


def migrate(legacy_document, proposal):
    old = team.load_state(legacy_document)
    policy_upgrade = old['schema_version'] == 2
    require(old['schema_version'] == 1 or (policy_upgrade and old.get('evidence_policy_version', 1) == 1), 'Migration source must be v1 or legacy v2 evidence policy')
    if policy_upgrade:
        check_hashes(old['workspace'], legacy_document['expected_hashes'])
    new = copy.deepcopy(proposal)
    require(new.get('schema_version') == 2, 'Migration requires explicit v2 proposal')
    require(isinstance(new.get('state'), dict), 'Migration proposal missing complete state')
    new['state']['legacy_snapshot'] = copy.deepcopy(legacy_document)
    state = load_state(new)
    if policy_upgrade:
        require(state.get('evidence_policy_version') == 2, 'Policy migration requires explicit evidence policy 2')
        require(state['events'][:len(old['events'])] == old['events'], 'Migration dropped transition history')
        require(state['role_reads'][:len(old['role_reads'])] == old['role_reads'], 'Migration dropped role observations')
        require(new['authorization_ref'] == legacy_document['authorization_ref'], 'Migration changed authorization')
    for key in ['project_id', 'workspace', 'pending_operations']:
        require(state[key] == old[key], 'Migration changed identity or unknown operations: ' + key)
    for key, field in RECORDS.items():
        new_ids = team.index(state[key], field)
        for record in old[key]:
            require(record[field] in new_ids, 'Migration dropped record: ' + record[field])
            for name, value in record.items():
                if name not in ({'schema_version', 'revision', 'updated_at', 'status', 'passed_acceptance_ids'}
                                | ({'evidence_refs'} if policy_upgrade and key == 'tasks' else set())):
                    require(new_ids[record[field]].get(name) == value, 'Migration changed original field: ' + name)
    if policy_upgrade:
        for task in state['tasks']:
            if task['status'] == 'COMPLETED':
                verify_task_files(state, task)
    return new


def immutable_history(previous, document):
    old, new = load_state(previous), load_state(document)
    require(new['revision'] > old['revision'], 'Revision must increase')
    require(new['events'][:len(old['events'])] == old['events'], 'Transition history is immutable')
    require(previous['project_id'] == document['project_id'] and previous['workspace'] == document['workspace'], 'Wrong checkpoint identity')
    require(previous['authorization_ref'] == document['authorization_ref'], 'Authorization changes need an explicit new project scope')
    require(new.get('evidence_policy_version', 1) == old.get('evidence_policy_version', 1), 'Evidence policy changes require explicit migration')
    for key in ['evidence', 'artifacts', 'handoffs', 'decisions']:
        records = team.index(new[key], RECORDS[key])
        for record in old[key]:
            require(records.get(record[RECORDS[key]]) == record, key + ' history is immutable')
    if 'legacy_snapshot' in old:
        require(new.get('legacy_snapshot') == old['legacy_snapshot'], 'Migration source is immutable')


def update(previous, proposal):
    old, new = load_state(previous), load_state(proposal)
    immutable_history(previous, proposal)
    require(old['events'] == new['events'], 'Use transition for status changes')
    requirements = team.index(new['requirements'], 'requirement_id')
    for record in old['requirements']:
        require(requirements.get(record['requirement_id']) == record, 'Use change for requirement changes')
    old_tasks = team.index(old['tasks'], 'task_id'); new_tasks = team.index(new['tasks'], 'task_id')
    require(set(old_tasks) <= set(new_tasks), 'Cannot delete task history')
    for tid, task in new_tasks.items():
        require(task['status'] == old_tasks.get(tid, {'status': 'PLANNED'})['status'], 'Use transition for status changes')
        if tid in old_tasks and task['status'] == 'COMPLETED':
            require(task == old_tasks[tid], 'Invalidate completed task before changing its records')
    return proposal
