import json
import unittest
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parents[1]/"skills/agency-workflow"
class SchemaTests(unittest.TestCase):
 def test_all_templates_have_schema(self):
  for p in (ROOT/"assets/templates").glob("*.json"):
   schema=json.loads((ROOT/"references/schemas"/(p.stem+".schema.json")).read_text())
   data=json.loads(p.read_text())
   # Placeholders deliberately cannot pass enum gates without observed values.
   if p.stem=="work-item":data["status"]="PLANNED"
   if p.stem=="defect":data["status"]="OPEN"
   if p.stem=="evidence":data["outcome"]="UNKNOWN"
   jsonschema.validate(data,schema)
   data["schema_version"]=2
   with self.assertRaises(jsonschema.ValidationError):jsonschema.validate(data,schema)
 def test_missing_owner_rejected(self):
  schema=json.loads((ROOT/"references/schemas/work-item.schema.json").read_text());data=json.loads((ROOT/"assets/templates/work-item.json").read_text());del data["owner_role"]
  with self.assertRaises(jsonschema.ValidationError):jsonschema.validate(data,schema)
