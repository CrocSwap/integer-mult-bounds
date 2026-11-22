"""Verify the submitted package's exact file inventory and SHA256 bindings."""
from hashlib import sha256
import json
from pathlib import Path

root = Path(__file__).resolve().parent
expected = json.loads((root / 'MANIFEST.json').read_text())
actual = {
    p.relative_to(root).as_posix(): sha256(p.read_bytes()).hexdigest()
    for p in root.rglob('*')
    if p.is_file() and '__pycache__' not in p.parts
    and p != root / 'MANIFEST.json'
}
if actual != expected:
    missing = sorted(expected.keys() - actual.keys())
    extra = sorted(actual.keys() - expected.keys())
    changed = sorted(k for k in expected.keys() & actual.keys() if expected[k] != actual[k])
    raise SystemExit(f'Manifest mismatch: missing={missing}, extra={extra}, changed={changed}')
print(f'PASS package manifest: {len(actual)} files')
