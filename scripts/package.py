"""Validate and build a deterministic, skills-only portable ZIP."""
import hashlib
import json
import re
import zipfile
from pathlib import Path
import jsonschema
import yaml
ROOT = Path(__file__).resolve().parents[1]

def build(root=ROOT):
    root = Path(root)
    manifest = json.loads((root / 'plugin.json').read_text(encoding='utf-8'))
    schema_path = root / 'tests/schemas/plugin.schema.json'
    lock = json.loads((root / 'tests/schemas/lock.json').read_text())
    if not hashlib.sha256(schema_path.read_bytes()).hexdigest() == lock['sha256']:
        raise ValueError('Package validation failed')
    jsonschema.validators.validator_for(json.loads(schema_path.read_text())).check_schema(json.loads(schema_path.read_text()))
    jsonschema.validate(manifest, json.loads(schema_path.read_text()))
    if 'apps' in manifest.get('extensions', {}).get('com.openai', {}):
        raise ValueError('Package validation failed')
    if (root / '.app.json').exists():
        raise ValueError('Package validation failed')
    skill_root = root / 'skills/agency-workflow'
    entries = [root / 'plugin.json', *sorted((root / 'skills').rglob('*'))]
    files = [p for p in entries if p.is_file()]
    allowed = set(json.loads((root / 'package-files.json').read_text(encoding='utf-8')))
    discovered = {p.relative_to(root).as_posix() for p in files}
    if discovered != allowed:
        raise ValueError('Package allowlist mismatch; missing=' + repr(sorted(allowed - discovered)) + '; unexpected=' + repr(sorted(discovered - allowed)))
    for helper in ['team.py','workflow_v2.py','check_runner.py']:
        if (skill_root/'scripts'/helper).read_bytes() != (root/'scripts'/helper).read_bytes():
            raise ValueError('Bundled helper differs from canonical source: ' + helper)
    names = set()
    for p in entries:
        if p.is_symlink():
            raise ValueError('Symlink not permitted')
        if not p.resolve().is_relative_to(root.resolve()):
            raise ValueError('Path escape')
    for p in files:
        name = p.relative_to(root).as_posix()
        if any((part.startswith('.') for part in Path(name).parts)):
            raise ValueError('Hidden file forbidden')
        if name.casefold() in names:
            raise ValueError('Case-insensitive duplicate')
        names.add(name.casefold())
        if any((x in p.parts for x in ['node_modules', '.git', '__pycache__'])):
            raise ValueError('Package validation failed')
        content = p.read_text(encoding='utf-8')
        if re.search('(?:(?<![A-Za-z0-9])[A-Za-z]:[\\\\/]|sk-proj-[A-Za-z0-9]{16,}|-----BEGIN PRIVATE KEY)', content):
            raise ValueError('Private path or credential')
    for p in (root / 'skills').glob('*/SKILL.md'):
        front = yaml.safe_load(p.read_text(encoding='utf-8').split('---', 2)[1])
        if not (front['name'] == 'agency-workflow' and isinstance(front['description'], str)):
            raise ValueError('Package validation failed')
    if not len(list((root / 'skills').glob('*/SKILL.md'))) == 1:
        raise ValueError('Package validation failed')
    catalog = json.loads((skill_root / 'references/agent-catalog.json').read_text(encoding='utf-8'))
    if not len({r['codex_slug'] for r in catalog}) == len(catalog) == 18:
        raise ValueError('Package validation failed')
    for r in catalog:
        p = skill_root / 'references' / r['path']
        if not hashlib.sha256(p.read_bytes()).hexdigest() == r['content_sha256']:
            raise ValueError('Package validation failed')
    routes = json.loads((skill_root / 'references/routes.json').read_text())
    for route in routes:
        if not (skill_root / 'references' / route['path']).is_file():
            raise ValueError('Package validation failed')
        if not set(route['roles']) <= {r['corpus_id'] for r in catalog}:
            raise ValueError('Package validation failed')
    for p in (skill_root / 'references/schemas').glob('*.json'):
        jsonschema.Draft202012Validator.check_schema(json.loads(p.read_text()))
    output = root / 'build/agency-workflow-plugin.zip'
    output.parent.mkdir(exist_ok=True)
    inventory = {}
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for p in files:
            data = p.read_bytes()
            name = p.relative_to(root).as_posix()
            entry = zipfile.ZipInfo(name, (2020, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, data)
            inventory[name] = hashlib.sha256(data).hexdigest()
    with zipfile.ZipFile(output) as archive:
        if not (archive.testzip() is None and 'plugin.json' in archive.namelist()):
            raise ValueError('Package validation failed')
    (output.parent / 'package-inventory.json').write_text(json.dumps(inventory, indent=2), encoding='utf-8')
    return {'path': str(output), 'files': len(inventory), 'sha256': hashlib.sha256(output.read_bytes()).hexdigest()}
if __name__ == '__main__':
    print(json.dumps(build(), indent=2))
