"""Committed packet identity only; no original execution or semantic approval."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
manifest = json.loads((ROOT/'ARTIFACTS.json').read_text())
expected = {}
for row in manifest['files']:
    name = row['path']
    if name in expected or name.startswith('/') or any(x in ('','.','..') for x in name.split('/')):
        raise ValueError('invalid packet identity path')
    path = ROOT/name
    if path.is_symlink() or not path.is_file():
        raise ValueError('packet input is absent or aliased: '+name)
    raw = path.read_bytes()
    if len(raw)!=row['bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256']:
        raise ValueError('packet identity differs: '+name)
    expected[name] = row
actual = {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()
          and '__pycache__' not in p.parts and p.name!='ARTIFACTS.json'}
if actual!=set(expected):
    raise ValueError('packet file set differs')
print('PASS packet byte identities; full_C05=false full_V03=false original_execution=false')
