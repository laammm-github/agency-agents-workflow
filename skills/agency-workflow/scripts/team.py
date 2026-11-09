"""Deterministic project-state validation. Not an execution or authorization service."""
import argparse
import copy
import hashlib
import json
import os
import tempfile
import jsonschema
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

def v2():
 from importlib import import_module
 return import_module('scripts.workflow_v2' if __package__ else 'workflow_v2')

STATUSES = {"PLANNED", "PREFLIGHT", "EXECUTING", "VERIFYING", "COMPLETED", "BLOCKED", "FAILED", "UNKNOWN", "NEEDS_REVIEW"}
TRANSITIONS = {
 "PLANNED": {"PREFLIGHT", "BLOCKED"}, "PREFLIGHT": {"EXECUTING", "BLOCKED", "UNKNOWN"},
 "EXECUTING": {"VERIFYING", "FAILED", "UNKNOWN", "NEEDS_REVIEW"},
 "VERIFYING": {"COMPLETED", "FAILED", "BLOCKED"},
 "BLOCKED": {"PREFLIGHT"}, "FAILED": {"PREFLIGHT"}, "UNKNOWN": {"NEEDS_REVIEW", "PREFLIGHT"},
 "NEEDS_REVIEW": {"PREFLIGHT"}, "COMPLETED": set()}

class ContractError(ValueError):
 pass

def require(condition, message):
 if not condition:
  raise ContractError(message)

def digest(path):
 return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def schema_directory():
 root = Path(__file__).resolve().parents[1]
 repository = root / 'skills/agency-workflow/references/schemas'
 return repository if repository.is_dir() else root / 'references/schemas'

def inside(root, relative):
 root = Path(root).resolve()
 require(not Path(relative).is_absolute() and ".." not in Path(relative).parts, "Unsafe relative path")
 path = (root / relative).resolve()
 require(path.is_relative_to(root), "Path escapes project")
 return path

def fresh(project_id, workspace):
 return {"schema_version": 1, "revision": 0, "project_id": project_id,
         "workspace": str(Path(workspace).resolve()), "requirements": [], "tasks": [],
         "artifacts": [], "evidence": [], "defects": [], "decisions": [],
         "releases": [], "incidents": [], "handoffs": [], "pending_operations": []}

def index(records, key):
 require(all(isinstance(x, dict) and isinstance(x.get(key), str) and x[key] for x in records), "Missing ID: " + key)
 result = {x[key]: x for x in records}
 require(len(result) == len(records), "Duplicate ID: " + key)
 return result

def current_artifacts(state):
 artifacts = index(state["artifacts"], "artifact_id")
 successors = {}
 for aid, artifact in artifacts.items():
  old = artifact.get("supersedes")
  if old is not None:
   require(old in artifacts and old != aid, "Invalid artifact supersedes reference")
   require(old not in successors, "Ambiguous artifact successors")
   successors[old] = aid
 visited = set()
 for aid in artifacts:
  chain = set()
  while aid not in visited:
   require(aid not in chain, "Artifact supersedes cycle")
   chain.add(aid)
   if aid not in successors: break
   aid = successors[aid]
  visited.update(chain)
 active = [a for aid, a in artifacts.items() if aid not in successors]
 paths = [inside(state["workspace"], a["path"]) for a in active]
 require(len(paths) == len(set(paths)), "Ambiguous current artifact path; declare supersedes")
 return active

def artifact_hashes(state):
 return {a["path"]: a["sha256"] for a in current_artifacts(state)}

def evidence_time(record):
 try:
  value = datetime.fromisoformat(record["timestamp"])
  return value if value.utcoffset() is not None else None
 except (KeyError, TypeError, ValueError):
  return None

def hash_baseline(state, expected_hashes):
 require(isinstance(expected_hashes, dict), "Invalid hash baseline")
 for relative, sha in expected_hashes.items():
  inside(state["workspace"], relative)
  require(isinstance(sha, str) and len(sha) == 64 and all(c in "0123456789abcdef" for c in sha), "Invalid baseline hash")
 required = artifact_hashes(state)
 require(set(required) <= set(expected_hashes), "Incomplete hash coverage")
 require(all(expected_hashes[k] == v for k, v in required.items()), "Hashes differ from checkpoint")
 return expected_hashes

def validate(state):
 if state.get('schema_version') == 2: return v2().validate_state(state)
 require(state.get("schema_version") == 1, "Unsupported schema version")
 require(type(state.get("revision")) is int and state["revision"] >= 0, "Invalid revision")
 require(bool(state.get("project_id")) and bool(state.get("workspace")), "Missing project identity")
 req = index(state["requirements"], "requirement_id")
 tasks = index(state["tasks"], "task_id")
 ev = index(state["evidence"], "evidence_id")
 artifacts = index(state["artifacts"], "artifact_id")
 for a in artifacts.values():
  inside(state["workspace"], a["path"])
  require(len(a.get("sha256", "")) == 64, "Missing artifact hash")
 current_artifacts(state)
 for e in ev.values():
  require(e.get("outcome") in {"PASS", "FAIL", "BLOCKED", "UNKNOWN"}, "Invalid evidence outcome")
  require(bool(e.get("tool")) and bool(e.get("artifact_ref")), "Evidence must reference actual tool output")
  require((e.get("kind") == "command" and type(e.get("exit_code")) is int) or (e.get("kind") != "command" and e.get("exit_code") is None), "Invalid exit code")
  require(not(e["outcome"] == "PASS" and e.get("kind") == "command" and e["exit_code"] != 0), "Failed command cannot pass")
 visited = set()
 def visit(tid, stack):
  if tid in visited: return
  require(tid not in stack, "Dependency cycle")
  require(tid in tasks, "Missing dependency")
  for dep in tasks[tid].get("dependencies", []):
   visit(dep, stack | {tid})
  visited.add(tid)
 for tid, t in tasks.items():
  require(t.get("status") in STATUSES and bool(t.get("owner_role")), "Invalid task status or owner")
  require(bool(t.get("requirement_ids")) and all(x in req for x in t["requirement_ids"]), "Missing requirement")
  require(bool(t.get("acceptance_ids")), "Missing acceptance criteria")
  visit(tid, set())
  for eid in t.get("evidence_refs", []):
   require(eid in ev, "Missing evidence")
  if t["status"] in {"EXECUTING", "VERIFYING", "COMPLETED"}:
   require(all(tasks[x]["status"] == "COMPLETED" for x in t.get("dependencies", [])), "Dependency incomplete")
  if t["status"] == "COMPLETED":
   require(bool(t.get("evidence_refs")), "Completion needs evidence")
   require(all(ev[x]["outcome"] == "PASS" for x in t["evidence_refs"]), "Failed evidence blocks completion")
   for eid in t["evidence_refs"]:
    require(ev[eid].get("task_id") == tid, "Evidence belongs to another task")
   covered = {a for eid in t["evidence_refs"] for a in ev[eid].get("acceptance_ids", [])}
   require(set(t["acceptance_ids"]) <= covered, "Evidence does not cover acceptance")
   require(set(t["acceptance_ids"]) <= set(t.get("passed_acceptance_ids", [])), "Acceptance incomplete")
   require(bool(t.get("artifact_refs")) and all(x in artifacts for x in t["artifact_refs"]), "Missing deliverable")
 for defect in state["defects"]:
  if defect["status"] == "CLOSED":
   refs = defect.get("regression_evidence", [])
   require(bool(refs) and all(x in ev and ev[x]["outcome"] == "PASS" for x in refs), "Defect needs regression evidence")
 return state

def transition(state, task_id, status):
 if state.get('schema_version') == 2: return v2().transition(state, task_id, status)
 result = copy.deepcopy(validate(state))
 task = index(result["tasks"], "task_id")[task_id]
 require(status in TRANSITIONS[task["status"]], "Illegal transition")
 task["status"] = status
 result["revision"] += 1
 return validate(result)

def change_requirement(state, requirement_id, description):
 if state.get('schema_version') == 2: return v2().change_requirement(state, requirement_id, description)
 result = copy.deepcopy(validate(state))
 req = index(result["requirements"], "requirement_id")[requirement_id]
 result["decisions"].append({"requirement_id": requirement_id, "previous": copy.deepcopy(req), "reason": description})
 req["version"] = req.get("version", 1) + 1
 req["description"] = description
 affected = {t["task_id"] for t in result["tasks"] if requirement_id in t["requirement_ids"]}
 while True:
  extended = affected | {t["task_id"] for t in result["tasks"] if set(t.get("dependencies", [])) & affected}
  if extended == affected: break
  affected = extended
 for t in result["tasks"]:
  if t["task_id"] in affected:
   t["status"] = "PLANNED"
   t["passed_acceptance_ids"] = []
 result["revision"] += 1
 return validate(result)

def readiness(state, candidate):
 if state.get('schema_version') == 2: return v2().readiness(state, candidate)
 validate(state)
 require(bool(candidate), "Missing candidate")
 require(bool(state["tasks"]) and all(t["status"] == "COMPLETED" for t in state["tasks"]), "Unfinished work")
 require(not state["pending_operations"], "Unknown side effects")
 require(all(d["status"] == "CLOSED" for d in state["defects"] if d.get("blocking", True)), "Blocking defects")
 evidence = index(state["evidence"], "evidence_id")
 for task in state["tasks"]:
  require(all(evidence[e].get("candidate") == candidate for e in task["evidence_refs"]), "Stale candidate evidence")
 for requirement in state["requirements"]:
  criteria = set(requirement.get("acceptance_ids", []))
  require(bool(criteria), "Requirement missing acceptance criteria")
  covered = {a for t in state["tasks"] if requirement["requirement_id"] in t["requirement_ids"] for a in t["acceptance_ids"]}
  require(criteria <= covered, "Unimplemented requirement")
 for artifact in current_artifacts(state):
  path = inside(state["workspace"], artifact["path"])
  require(path.is_file() and digest(path) == artifact["sha256"], "Missing or changed artifact")
 # A failure remains blocking unless a matching successful rerun explicitly supersedes it.
 evidence = index(state["evidence"], "evidence_id")
 referenced = {eid for task in state["tasks"] for eid in task.get("evidence_refs", [])}
 for failed in evidence.values():
  if failed.get("candidate") != candidate or failed["outcome"] == "PASS": continue
  replacements = [e for e in evidence.values() if failed["evidence_id"] in e.get("supersedes", [])]
  failed_at = evidence_time(failed)
  resolved = False
  for replacement in replacements:
   rerun_at = evidence_time(replacement)
   if (replacement["outcome"] == "PASS" and replacement.get("candidate") == candidate
       and replacement.get("task_id") == failed.get("task_id")
       and set(failed.get("acceptance_ids", [])) <= set(replacement.get("acceptance_ids", []))
       and replacement["evidence_id"] in referenced
       and failed_at is not None and rerun_at is not None and rerun_at > failed_at):
    resolved = True
    break
  require(resolved, "Unresolved failing evidence; needs a later timestamped PASS rerun")
 return {"verdict": "PASS", "candidate": candidate, "deployed": False}

def resume(document, workspace, expected_hashes=None):
 if document.get('schema_version') == 2: return v2().resume(document, workspace, expected_hashes)
 state = load_state(document)
 require(Path(workspace).resolve() == Path(state["workspace"]).resolve(), "Wrong workspace")
 require(not state["pending_operations"], "Resolve unknown side effects before resume")
 if "state" in document:
  stored = document["expected_hashes"]
  if expected_hashes is None:
   expected_hashes = stored
  else:
   require(set(stored) <= set(expected_hashes), "Incomplete checkpoint baseline coverage")
   require(all(expected_hashes[k] == v for k, v in stored.items()), "Hashes differ from checkpoint baseline")
 hash_baseline(state, expected_hashes)
 for relative, expected in expected_hashes.items():
  require(digest(inside(workspace, relative)) == expected, "External modification: " + relative)
 return {"status": "PREFLIGHT", "authorization_recheck_required": True}

def checkpoint(state, authorization_ref, expected_hashes=None, previous=None):
 if state.get('schema_version') == 2: return v2().checkpoint(state, authorization_ref, expected_hashes, previous)
 validate(state)
 if previous is not None:
  load_state(previous)
  require(all(previous[k] == state[k] for k in ["project_id", "workspace"]), "Wrong previous checkpoint")
  require(previous["revision"] <= state["revision"], "Checkpoint revision moved backwards")
  if expected_hashes is None: expected_hashes = previous["expected_hashes"]
 hashes = dict(expected_hashes or {})
 for path, sha in artifact_hashes(state).items():
  require(path not in hashes or hashes[path] == sha, "Conflicting artifact baseline; explicitly rebaseline")
  hashes[path] = sha
 hash_baseline(state, hashes)
 metadata = {"milestone": "active", "last_confirmed_action": None, "next_preconditions": []}
 if previous is not None:
  metadata.update({k: copy.deepcopy(previous[k]) for k in metadata})
 return {"schema_version": 1, "project_id": state["project_id"], "workspace": state["workspace"],
         "revision": state["revision"], "expected_hashes": hashes,
         "pending_operations": copy.deepcopy(state["pending_operations"]),
         "authorization_ref": authorization_ref, **metadata,
         "tasks": [t["task_id"] for t in state["tasks"]],
         "artifacts": [a["artifact_id"] for a in state["artifacts"]],
         "evidence_refs": [e["evidence_id"] for e in state["evidence"]],
         "updated_at": datetime.now(timezone.utc).isoformat(), "state": copy.deepcopy(state)}

def load_state(document):
 if document.get('schema_version') == 2: return v2().load_state(document)
 if "state" not in document:
  require("requirements" in document, "Legacy index-only checkpoint needs explicit migration with source records")
  return validate(document)
 import jsonschema
 schema_path = schema_directory() / 'checkpoint.schema.json'
 jsonschema.validate(document, json.loads(schema_path.read_text(encoding="utf-8")))
 state = validate(document["state"])
 for key in ["project_id", "workspace", "revision", "pending_operations"]:
  require(state[key] == document[key], "Checkpoint metadata mismatch: " + key)
 require(document["tasks"] == [t["task_id"] for t in state["tasks"]], "Checkpoint task index mismatch")
 require(document["artifacts"] == [a["artifact_id"] for a in state["artifacts"]], "Checkpoint artifact index mismatch")
 hash_baseline(state, document["expected_hashes"])
 return state

@contextmanager
def writer_lock(path):
 # OS locks are released on exit/crash. The persistent marker file is not ownership.
 with path.open("a+b") as handle:
  handle.seek(0, 2)
  if handle.tell() == 0: handle.write(b"0"); handle.flush()
  handle.seek(0)
  if os.name == "nt":
   import msvcrt
   msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
  else:
   import fcntl
   fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
  try: yield
  finally:
   handle.seek(0)
   if os.name == "nt": msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
   else: fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

def save(path, state, expected_digest=None):
 load_state(state)
 path = Path(path)
 if state.get('schema_version') == 2:
  require(path.resolve().is_relative_to(Path(state['workspace']).resolve()), 'Checkpoint must stay inside project')
  require(all(inside(state['workspace'], relative) != path.resolve() for relative in state['expected_hashes']), 'Checkpoint must not hash itself')
  require(all(inside(state['workspace'], a['path']) != path.resolve() for a in state['state']['artifacts']), 'Checkpoint must not register itself as an artifact')
 temporary = None
 with writer_lock(path.with_suffix(path.suffix + ".lock")):
  if path.exists():
   require(expected_digest is not None and digest(path) == expected_digest, "Stale checkpoint")
   previous = json.loads(path.read_text(encoding='utf-8'))
   require(previous.get('schema_version') == state.get('schema_version'), 'Use explicit migration to a new file')
   if state.get('schema_version') == 2: v2().immutable_history(previous, state)
  try:
   with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, prefix=path.name+".", suffix=".tmp", delete=False, encoding="utf-8") as out:
    temporary = Path(out.name)
    json.dump(state, out, ensure_ascii=False, indent=2)
    out.flush(); os.fsync(out.fileno())
   written_digest = digest(temporary)
   os.replace(temporary, path)
  finally:
   if temporary is not None and temporary.exists(): temporary.unlink()
  return written_digest

def read_document(path, expected_digest=None):
 """Read one cooperative snapshot; never ignore an explicit caller baseline."""
 path = Path(path)
 with writer_lock(path.with_suffix(path.suffix + '.lock')):
  raw = path.read_bytes()
  snapshot_digest = hashlib.sha256(raw).hexdigest()
  require(expected_digest is None or snapshot_digest == expected_digest, 'Stale checkpoint')
  document = json.loads(raw.decode('utf-8'))
  require(digest(path) == snapshot_digest, 'Stale checkpoint: changed while reading')
 return document, snapshot_digest

def check_snapshot(path, expected_digest):
 path = Path(path)
 with writer_lock(path.with_suffix(path.suffix + '.lock')):
  require(path.is_file() and digest(path) == expected_digest, 'Stale checkpoint: changed during operation')

def write_task_board(state_path, expected_digest, state, destination, projection):
  """Generate only workspace TASKS.md, using a staged atomic replacement."""
  output = inside(state['workspace'], 'TASKS.md')
  require(Path(destination).resolve() == output, 'Report output must be workspace/TASKS.md')
  require(output != Path(state_path).resolve(), 'Cannot overwrite checkpoint with report')
  require(not output.is_symlink(), 'Task board symlink is not authorized')
  if output.exists():
   require(output.is_file() and output.read_text(encoding='utf-8-sig').startswith('# ' + state['project_id'] + '\n'),
           'Existing task board is not a generated project projection')
  with writer_lock(Path(state_path).with_suffix(Path(state_path).suffix + '.lock')):
   require(digest(state_path) == expected_digest, 'Stale checkpoint: report source changed')
   with tempfile.NamedTemporaryFile(mode='w', dir=output.parent, prefix='TASKS.md.proposal-',
                                    suffix='.tmp', encoding='utf-8', newline='\n', delete=False) as temp:
    proposal = Path(temp.name)
    temp.write(projection)
   try:
    os.replace(proposal, output)
   except OSError as error:
    raise ContractError(f'Task board atomic replace failed; proposal preserved at {proposal}: {error}')
  require(output.read_text(encoding='utf-8-sig').replace('\r\n', '\n') == projection,
          'Task board readback differs from checkpoint projection')
  return {'report_saved': True, 'path': str(output), 'sha256': digest(output), 'checkpoint_digest': expected_digest}

def main():
 parser = argparse.ArgumentParser(description=__doc__)
 parser.add_argument("operation", choices=["validate", "ready", "init", "next", "report", "change", "transition", "resume", "update", "migrate", "invalidate", "preflight"])
 parser.add_argument("state", type=Path)
 parser.add_argument("--candidate")
 parser.add_argument("--workspace", type=Path)
 parser.add_argument("--project-id")
 parser.add_argument("--authorization-ref")
 parser.add_argument("--expected-digest")
 parser.add_argument("--task-id")
 parser.add_argument("--status")
 parser.add_argument("--requirement-id")
 parser.add_argument("--description")
 parser.add_argument("--hashes", type=Path)
 parser.add_argument('--schema-version', type=int, choices=[1,2], default=2)
 parser.add_argument('--proposal', type=Path)
 parser.add_argument('--output', type=Path)
 parser.add_argument('--markdown', action='store_true')
 parser.add_argument('--purpose', choices=['stage','implementation'], default='stage')
 parser.add_argument('--write-path', action='append', default=[])
 args = parser.parse_args()
 try:
  if args.operation == "init":
   require(args.workspace and args.project_id and args.authorization_ref, "Init requires workspace, project ID and authorization reference")
   require(args.state.resolve().is_relative_to(args.workspace.resolve()), "State must be inside authorized project")
   require(not args.state.exists(), "Project state already exists")
   require(args.state.parent.exists(), "Create authorized state directory explicitly first")
   if args.schema_version == 2:
    state = checkpoint(v2().fresh(args.project_id, args.workspace), args.authorization_ref)
   else:
    state = fresh(args.project_id, args.workspace)
    state['authorization_ref'] = args.authorization_ref
   saved_digest = save(args.state, state)
   result = {"initialized": True, "digest": saved_digest}
  else:
   document, snapshot_digest = read_document(args.state, args.expected_digest)
   state = load_state(document)
   if args.operation == 'preflight':
    require(document.get('schema_version') == 2 and args.task_id, 'Preflight requires v2 and --task-id')
    result=v2().preflight(document,args.task_id,args.purpose,args.write_path)
   elif args.operation == 'migrate':
    require(args.proposal and args.output, 'Migration needs --proposal and a new --output')
    require(args.output.resolve() != args.state.resolve() and not args.output.exists(), 'Migration must preserve source and existing outputs')
    require(args.output.resolve().is_relative_to(Path(state['workspace']).resolve()), 'Migration output escapes project')
    migrated = v2().migrate(document, json.loads(args.proposal.read_text(encoding='utf-8')))
    with writer_lock(args.state.with_suffix(args.state.suffix + '.lock')):
     require(digest(args.state) == snapshot_digest, 'Stale checkpoint: migration source changed')
     saved_digest = save(args.output, migrated)
    result={'migrated':True,'output':str(args.output),'digest':saved_digest}
   elif args.operation == 'update':
    require(document.get('schema_version') == 2 and args.proposal and args.expected_digest, 'Update requires v2 proposal and expected digest')
    proposal = json.loads(args.proposal.read_text(encoding='utf-8'))
    saved_digest = save(args.state, v2().update(document, proposal), args.expected_digest)
    result={'revision':proposal['revision'],'digest':saved_digest}
   elif args.operation == "ready":result=readiness(state,args.candidate)
   elif args.operation == "resume":
    require(args.workspace and (args.hashes or "state" in document), "Resume needs workspace and expected hashes")
    result=resume(document,args.workspace,json.loads(args.hashes.read_text(encoding="utf-8")) if args.hashes else None)
   elif args.operation in {"change", "transition", "invalidate"}:
    require(args.expected_digest is not None, "Mutation requires expected digest")
    if args.operation == 'invalidate':
     require(state.get('schema_version') == 2 and args.task_id and args.description, 'Invalidate requires v2 task and reason')
     changed=v2().invalidate(state,args.task_id,args.description)
    elif args.operation == "change":
     require(args.requirement_id and args.description, "Change needs requirement and description")
     changed=change_requirement(state,args.requirement_id,args.description)
    else:
     require(args.task_id and args.status, "Transition needs task and status")
     changed=transition(state,args.task_id,args.status)
    saved_digest = save(args.state,checkpoint(changed,document["authorization_ref"],previous=document) if "state" in document else changed,args.expected_digest)
    result={"revision":changed["revision"],"digest":saved_digest}
   elif args.operation == "next":
    tasks=index(state["tasks"],"task_id")
    result={"ready_tasks":[t["task_id"] for t in tasks.values() if t["status"] == "PLANNED" and all(tasks[d]["status"] == "COMPLETED" for d in t.get("dependencies",[]))]}
   elif args.operation == "report":
    if args.markdown:
     require(state.get('schema_version') == 2, 'Markdown projection requires v2')
     projection = v2().report(state)
     check_snapshot(args.state, snapshot_digest)
     if args.output:
      result = write_task_board(args.state, snapshot_digest, state, args.output, projection)
      print(json.dumps(result, ensure_ascii=False));return
     print(projection + '\nCheckpoint SHA256: ' + snapshot_digest);return
    result={"project_id":state["project_id"],"revision":state["revision"],"tasks":{t["task_id"]:t["status"] for t in state["tasks"]},"pending_operations":state["pending_operations"],"scope":"recorded state; not independent proof of execution"}
   else:
    if state.get('schema_version') == 2 and state.get('evidence_policy_version',1) == 2:
     for task in state['tasks']:
      if task['status']=='COMPLETED': v2().verify_task_files(state,task)
     result={'valid':True,'evidence_policy_version':2,'scope':'records and completed-task capture files; execution origin unauthenticated'}
    else:result={"valid":True}
   if args.operation in {'validate','ready','next','report','resume','preflight'}:
    check_snapshot(args.state, snapshot_digest)
    if document.get('schema_version') == 2: result['checkpoint_digest'] = snapshot_digest
  print(json.dumps(result,ensure_ascii=False))
 except (ContractError, KeyError, TypeError, OSError, ValueError, jsonschema.ValidationError) as error:
  parser.exit(1, str(error) + "\n")

if __name__ == "__main__":
 main()
