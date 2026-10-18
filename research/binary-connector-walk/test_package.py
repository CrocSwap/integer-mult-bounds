#!/usr/bin/env python3
"""Relocation, regeneration and tamper tests. Apache-2.0; see NOTICE.md."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def run(path, script):
    return subprocess.run([sys.executable, '-I', '-O', '-B', str(path/script)],
                          cwd=path.parent, capture_output=True, text=True)


with tempfile.TemporaryDirectory(prefix='binary-connector-check-') as temporary:
    package = Path(temporary)/'relocated'
    shutil.copytree(ROOT, package)
    original = (package/'CERTIFICATE.json').read_bytes()
    rebuilt = run(package, 'search.py')
    need(rebuilt.returncode == 0, rebuilt.stderr)
    need((package/'CERTIFICATE.json').read_bytes() == original, 'deterministic full search')
    checked = run(package, 'verify.py')
    need(checked.returncode == 0, checked.stderr)
    for name in ('CERTIFICATE.json', 'EXPECTED.json', 'SOURCES.json', 'references/PR889-README.md'):
        path = package/name
        saved = path.read_bytes()
        if name == 'CERTIFICATE.json':
            obj = json.loads(saved); obj['witnesses']['51'] = ''; path.write_text(json.dumps(obj))
        elif name == 'EXPECTED.json':
            obj = json.loads(saved); obj['cycle']['calls'] = 10; path.write_text(json.dumps(obj))
        elif name == 'SOURCES.json':
            obj = json.loads(saved); obj['retained_references'][0]['sha256'] = '0'*64; path.write_text(json.dumps(obj))
        else:
            path.write_bytes(saved+b'changed source\n')
        result = run(package, 'verify.py')
        need(result.returncode != 0, 'tampered file accepted: '+name)
        path.write_bytes(saved)
print('PASS_BINARY_CONNECTOR_PACKAGE relocation=1 regeneration=1 corruptions=4')
