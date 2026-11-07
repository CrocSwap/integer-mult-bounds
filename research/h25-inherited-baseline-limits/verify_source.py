"""Bounded package byte integrity only; imports no retained implementation."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
manifest = json.loads((root / 'MANIFEST.json').read_text())
expected = manifest['files']
if not 1 <= len(expected) <= 64:
    raise ValueError('bounded package inventory required')
actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p.name != 'MANIFEST.json'}
if actual != set(expected):
    raise ValueError('package file inventory differs')
for name, row in expected.items():
    relative = Path(name)
    path = root / relative
    if relative.is_absolute() or '..' in relative.parts or path.is_symlink():
        raise ValueError('regular canonical source path required')
    size = path.stat().st_size
    if size != row['bytes'] or size > 1048576:
        raise ValueError('bounded exact source length required')
    if hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
        raise ValueError('source bytes differ')
print('PASS bounded source-package byte integrity; no implementation imported')
