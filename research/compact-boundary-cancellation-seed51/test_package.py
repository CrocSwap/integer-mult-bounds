"""Relocated replay and four independently injected package faults."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REL = HERE.relative_to(ROOT)


def run(root):
    return subprocess.run([sys.executable, '-I', '-O', '-B', str(root / REL / 'verify.py')],
                          cwd=root, capture_output=True, text=True)


with tempfile.TemporaryDirectory(prefix='compact-boundary-') as tmp:
    dest = Path(tmp)
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for name in pins['files']:
        target = dest / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / name).read_bytes())
    shutil.copytree(HERE, dest / REL, ignore=shutil.ignore_patterns('__pycache__'))
    clean = run(dest)
    if clean.returncode != 0:
        raise RuntimeError(clean.stdout + clean.stderr)
    verifier = dest / REL / 'verify.py'
    original = verifier.read_text()
    source = dest / 'notes/compact-control-movement.tex'
    original_source = source.read_bytes()
    receipt = dest / REL / 'RESULT.json'
    original_receipt = receipt.read_bytes()
    faults = [
        ('source drift', source, original_source + b'\nsource drift\n'),
        ('receipt drift', receipt, original_receipt.replace(b'40800', b'40801')),
        ('formula sign', verifier, original.replace('correction = 2 *', 'correction = -2 *').encode()),
        ('repair sign', verifier, original.replace('a - 2 * (1 << G)', 'a + 2 * (1 << G)').encode()),
    ]
    for name, target, replacement in faults:
        before = target.read_bytes()
        if replacement == before:
            raise RuntimeError('Fault injection did not change bytes: ' + name)
        target.write_bytes(replacement)
        failed = run(dest)
        target.write_bytes(before)
        if failed.returncode == 0:
            raise RuntimeError('Fault was accepted: ' + name)
    print('PASS_COMPACT_BOUNDARY_PACKAGE relocated_isolated_optimized=PASS faults=4')
