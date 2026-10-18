#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Standalone Git-free package replay and non-overwrite controls."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, why):
    if not ok:
        raise ValueError(why)


def digests(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def main():
    with tempfile.TemporaryDirectory(prefix='packed-export-') as td:
        root = Path(td)/'checkout'
        package = root/'research'/HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        for entry in json.loads((HERE/'SOURCES.json').read_bytes())['files']:
            if entry['usage'] != 'input':
                continue
            path = entry['path']
            target = root/path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT/path).read_bytes())
        before = digests(root)
        run = subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'verify.py')],
                             cwd=root, capture_output=True, text=True, timeout=180)
        need(run.returncode == 0, run.stdout+run.stderr)
        need('PASS_PACKED_CLIFFORD_GATE_TABLE_INTEGRATION' in run.stdout, 'export marker')
        need(before == digests(root), 'export files changed')
        existing = Path(td)/'already-exists.json'
        existing.write_bytes(b'keep me\n')
        run = subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'adapter.py'),
                              '--out', str(existing)], cwd=root, capture_output=True, text=True, timeout=10)
        need(run.returncode != 0 and 'output already exists' in run.stderr, 'existing output refusal')
        need(existing.read_bytes() == b'keep me\n', 'existing output changed')
        need(before == digests(root), 'negative export files changed')
    print('PASS_PACKED_TABLE_GIT_FREE_EXPORT_AND_NONOVERWRITE')


if __name__ == '__main__':
    main()
