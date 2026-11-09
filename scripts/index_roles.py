"""Index a fixed upstream archive as data; never execute upstream scripts."""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
import yaml

def parse_role(text, source):
 if not text.startswith("---\n") and not text.startswith("---\r\n"):return None
 front=yaml.safe_load(text.split("---",2)[1])
 if not isinstance(front,dict) or not all(isinstance(front.get(x),str) and front[x].strip() for x in ["name","description"]):
  raise ValueError("Invalid role frontmatter: "+source)
 return dict(corpus_id=Path(source).stem,codex_slug=re.sub(r"[^a-z0-9]+","-",front["name"].lower()).strip("-"),name=front["name"],description=front["description"],source_path=source)

def scan(archive):
 with zipfile.ZipFile(archive) as z:
  prefix=z.namelist()[0].split("/")[0]+"/"
  divisions=json.loads(z.read(prefix+"divisions.json"))["divisions"]
  rows=[]
  for n in z.namelist():
   relative=n.removeprefix(prefix)
   if relative.split("/")[0] in divisions and relative.endswith(".md"):
    text=z.read(n).decode("utf-8-sig")
    role=parse_role(text,relative)
    if role:rows.append(role)
  ids={r["corpus_id"] for r in rows}
  if len(ids)!=len(rows):raise ValueError("Duplicate corpus ID")
  books=json.loads(z.read(prefix+"strategy/runbooks.json"))["runbooks"]
  missing={a for b in books for g in b["roster"] for a in g["agents"] if a not in ids}
  if missing:raise ValueError("Missing runbook roles: "+repr(missing))
  slugs={}
  for r in rows:slugs.setdefault(r["codex_slug"],[]).append(r["source_path"])
  return {"roles":rows,"runbooks":len(books),"duplicate_slugs":{k:v for k,v in slugs.items() if len(v)>1},"archive_sha256":hashlib.sha256(Path(archive).read_bytes()).hexdigest()}

if __name__=="__main__":
 parser=argparse.ArgumentParser();parser.add_argument("archive",type=Path);parser.add_argument("--output",type=Path,required=True);args=parser.parse_args()
 result=scan(args.archive);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
 print(json.dumps({"roles":len(result["roles"]),"runbooks":result["runbooks"],"duplicate_slugs":result["duplicate_slugs"]}))
 if result["duplicate_slugs"]:raise SystemExit(1)
