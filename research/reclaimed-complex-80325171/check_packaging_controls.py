"""Bounded negative tests of packaging pins only; no scientific checker runs."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

if not __debug__ or os.environ.get('PYTHONOPTIMIZE'):
    raise RuntimeError('Assertions must be enabled')
ROOT = Path(__file__).resolve().parent
started = time.monotonic()
results = []
cases = [
    ('scientific_source', 'research/explore_complex_ceiling_breakthrough/pr97_port/sources/frames.py', 'Scientific source binding mismatch'),
    ('administrative_bytes', 'pool/frontier/PR97_f5f9c56/ADOPTION.json', 'Administrative provenance amendment mismatch'),
]
for label, relative, expected in cases:
    with tempfile.TemporaryDirectory(prefix='reclaimed-pin-negative-') as tmp:
        target = Path(tmp)
        manifest = json.loads((ROOT / 'RELEASE_MANIFEST.json').read_text())
        for entry in manifest['files']:
            dest = target / entry['path']
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / entry['path'], dest)
        changed = target / relative
        raw = changed.read_bytes() + b'\n'
        changed.write_bytes(raw)
        # Deliberately refresh only the outer packaging hash, to exercise the
        # independent inner source/adoption pin rather than the outer manifest.
        for entry in manifest['files']:
            if entry['path'] == relative:
                entry.update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        (target / 'RELEASE_MANIFEST.json').write_text(json.dumps(manifest))
        proc = subprocess.run([sys.executable, str(target / 'run_checks.py')], capture_output=True, text=True, timeout=10)
        if proc.returncode == 0 or expected not in proc.stderr:
            raise RuntimeError((label, proc.returncode, proc.stdout, proc.stderr))
        results.append(dict(control=label, rejected=True, expected_reason=expected))
for flag in ('-O', '-OO'):
    proc = subprocess.run([sys.executable, flag, str(ROOT / 'run_checks.py')], capture_output=True, text=True, timeout=10)
    if proc.returncode == 0 or 'Assertions must be enabled' not in proc.stderr:
        raise RuntimeError(('optimization_control', flag, proc.stderr))
    results.append(dict(control=flag, rejected_before_read=True))
print(json.dumps(dict(status='PASS',scope='Packaging pins and launch guards only; no scientific replay',controls=results,seconds=time.monotonic()-started),indent=2))
