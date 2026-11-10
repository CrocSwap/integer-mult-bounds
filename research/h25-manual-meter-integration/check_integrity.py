"""Archive byte integrity only; imports no archived source or runtime modules."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
inventory = json.loads((ROOT / 'INVENTORY.json').read_text(encoding='utf-8'))
expected = {row['path']: row for row in inventory['files']}
actual = {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()}
if actual != set(expected) | {'INVENTORY.json', 'SHA256SUMS'}:
    raise SystemExit('archive file-set mismatch')
for name, row in expected.items():
    p = ROOT / name
    if p.is_symlink() or not p.is_file():
        raise SystemExit('nonregular archive member: ' + name)
    raw = p.read_bytes()
    git_blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    if len(raw) != row['bytes'] or hashlib.sha256(raw).hexdigest() != row['sha256'] or git_blob != row['git_blob']:
        raise SystemExit('archive byte mismatch: ' + name)
lines = (ROOT / 'SHA256SUMS').read_text(encoding='utf-8').splitlines()
observed = {}
for line in lines:
    digest, name = line.split('  ', 1)
    if name in observed or name not in actual or name == 'SHA256SUMS':
        raise SystemExit('invalid checksum member')
    observed[name] = digest
if set(observed) != actual - {'SHA256SUMS'}:
    raise SystemExit('checksum file-set mismatch')
for name, digest in observed.items():
    if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
        raise SystemExit('checksum mismatch: ' + name)
print('PASS archive byte integrity: ' + str(len(actual)) + ' files; no runtime or scientific credit')
