"""Passive ordinary-file/source-map integrity; never execute archived sources."""
from pathlib import Path
import hashlib
import json

p = Path(__file__).resolve().parent
m = json.loads((p / 'MANIFEST.json').read_bytes())
actual = {str(f.relative_to(p)) for f in p.rglob('*') if f.is_file()}
assert actual == set(m['files']) | {'MANIFEST.json'}
for name, row in m['files'].items():
    f = p / name
    assert f.is_file() and not f.is_symlink() and f.resolve().is_relative_to(p)
    raw = f.read_bytes()
    assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], name
s = json.loads((p / 'SOURCE-MAP.json').read_bytes())
subject = json.loads((p / s['manifest_path']).read_bytes())
for section in ('source_pins', 'profiles'):
    for role, row in subject[section].items():
        entry = s['mapping'][row['path']]
        raw = (p / entry['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == row['sha256'] == entry['sha256']
assert len(subject['source_pins']) == 61 and len(subject['profiles']) == 7
assert subject['source_pins']['runner'] == subject['source_pins']['common_runner']
assert subject['execution_permission'] is False and s['execution_permission'] is False
print(json.dumps({'files_verified':len(m['files']), 'source_roles':61, 'profiles':7, 'historical_control_references':len(subject['control_pins']), 'candidate_execution':False}, sort_keys=True))
