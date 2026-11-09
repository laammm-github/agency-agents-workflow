import copy
import json
import tempfile
import unittest
from pathlib import Path
from scripts.team import fresh, validate, transition, change_requirement, readiness, resume, save, digest, inside, ContractError

def sample(root):
 s = fresh("teaching", root)
 s["requirements"] = [{"requirement_id": "R1", "version": 1, "acceptance_ids": ["A1"]}]
 s["tasks"] = [{"task_id": "T1", "owner_role": "developer", "requirement_ids": ["R1"], "acceptance_ids": ["A1"], "dependencies": [], "status": "PLANNED"}]
 return s

def completed(root):
 s = sample(root)
 s["evidence"] = [{"evidence_id": "E1", "tool": "test-fixture", "kind": "command", "exit_code": 0, "outcome": "PASS", "artifact_ref": "teaching output", "candidate": "v1", "task_id": "T1", "acceptance_ids": ["A1"]}]
 s["artifacts"] = [{"artifact_id": "F1", "path": "README.md", "sha256": digest(Path(root)/"README.md")}]
 s["tasks"][0].update(status="COMPLETED", evidence_refs=["E1"], artifact_refs=["F1"], passed_acceptance_ids=["A1"])
 return s

class TeamTests(unittest.TestCase):
 def test_completion_requires_evidence(self):
  s = sample(".");s["tasks"][0]["status"] = "COMPLETED"
  with self.assertRaises(ContractError):validate(s)
 def test_cycle(self):
  s = sample(".");s["tasks"][0]["dependencies"] = ["T1"]
  with self.assertRaises(ContractError):validate(s)
 def test_missing_dependency(self):
  s = sample(".");s["tasks"][0]["dependencies"] = ["missing"]
  with self.assertRaises(ContractError):validate(s)
 def test_duplicate_id(self):
  s = sample(".");s["tasks"].append(copy.deepcopy(s["tasks"][0]))
  with self.assertRaises(ContractError):validate(s)
 def test_failed_exit_cannot_pass(self):
  s = completed(".");s["evidence"][0]["exit_code"] = 1
  with self.assertRaises(ContractError):validate(s)
 def test_noncommand_exit_is_null(self):
  s = completed(".");s["evidence"][0]["kind"] = "read"
  with self.assertRaises(ContractError):validate(s)
 def test_transitions(self):
  s=sample(".")
  for status in ["PREFLIGHT","EXECUTING","VERIFYING"]:s=transition(s,"T1",status)
  self.assertEqual(s["revision"],3)
  with self.assertRaises(ContractError):transition(s,"T1","COMPLETED")
 def test_no_direct_completion(self):
  with self.assertRaises(ContractError):transition(sample("."),"T1","COMPLETED")
 def test_change_invalidates_transitive_acceptance(self):
  s=completed(".");t=copy.deepcopy(s["tasks"][0]);t.update(task_id="T2",dependencies=["T1"]);s["tasks"].append(t)
  t["evidence_refs"]=["E2"];s["evidence"].append(dict(s["evidence"][0],evidence_id="E2",task_id="T2"))
  changed=change_requirement(s,"R1","changed API")
  self.assertTrue(all(t["status"]=="PLANNED" and not t["passed_acceptance_ids"] for t in changed["tasks"]))
  self.assertEqual(s["requirements"][0]["version"],1)
 def test_ready_is_not_deployed(self):
  self.assertFalse(readiness(completed("."),"v1")["deployed"])
 def test_stale_candidate(self):
  with self.assertRaises(ContractError):readiness(completed("."),"v2")
 def test_open_defect(self):
  s=completed(".");s["defects"]=[{"status":"OPEN"}]
  with self.assertRaises(ContractError):readiness(s,"v1")
 def test_closed_defect_requires_regression(self):
  s=completed(".");s["defects"]=[{"status":"CLOSED"}]
  with self.assertRaises(ContractError):validate(s)
 def test_unknown_side_effect(self):
  s=completed(".");s["pending_operations"]=["deployment"]
  with self.assertRaises(ContractError):resume(s,".",{})
 def test_external_change(self):
  with tempfile.TemporaryDirectory() as directory:
   p=Path(directory)/"app.py";p.write_text("one");expected={"app.py":digest(p)};s=sample(directory)
   self.assertTrue(resume(s,directory,expected)["authorization_recheck_required"])
   p.write_text("two")
   with self.assertRaises(ContractError):resume(s,directory,expected)
 def test_paths(self):
  with self.assertRaises(ContractError):inside(".","../outside")
 def test_checkpoint_compare_before_write(self):
  with tempfile.TemporaryDirectory() as directory:
   p=Path(directory)/"state.json";s=sample(directory);save(p,s);h=digest(p)
   save(p,s,h)
   p.write_text("external change")
   with self.assertRaises(ContractError):save(p,s,h)
 def test_unsupported_schema(self):
  s=sample(".");s["schema_version"]=2
  with self.assertRaises(ContractError):validate(s)

if __name__=="__main__":unittest.main()
