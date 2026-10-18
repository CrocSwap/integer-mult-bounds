#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Reject proof-relevant mutations even after refreshing the local inventory.

These controls exercise release/source and cold-provenance bindings, rather
than just the outer package's file-integrity check. AI assistance: OpenAI Codex.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent.parent


def read(path):
    return json.loads(path.read_bytes())


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    outcomes = []
    controls = [
        ('admitted-spec', 'inputs/admitted-outer/new/SPEC.json', 'actual admitted outer bytes: new/SPEC.json'),
        ('baseline-freshness', 'evidence/BASELINE-RESULT.json', 'cold baseline freshness'),
    ]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONOPTIMIZE', None)
    env.pop('PYTHONPATH', None)
    for name, target, expected in controls:
        with tempfile.TemporaryDirectory(prefix='t185-control-') as root:
            changed = Path(root) / 'package'
            shutil.copytree(PACKAGE, changed)
            path = changed / target
            data = read(path)
            if name == 'admitted-spec':
                data['expected']['live'] += 1
            else:
                data['fresh_retained_bootstrap'] = False
            write(path, data)
            manifest = read(changed / 'PACKAGE-MANIFEST.json')
            manifest[target] = hashlib.sha256(path.read_bytes()).hexdigest()
            write(changed / 'PACKAGE-MANIFEST.json', manifest)
            process = subprocess.run([sys.executable, '-B', str(changed / 'verify.py')],
                                     cwd=root, env=env, capture_output=True, text=True,
                                     timeout=120)
            if process.returncode == 0 or expected not in process.stderr:
                raise ValueError(f'{name}: control did not reject for the intended reason: '
                                 f'{process.returncode}\n{process.stdout}\n{process.stderr}')
            outcomes.append(dict(control=name, exit_code=process.returncode, rejection=expected))
    print(json.dumps(dict(status='PASS_RELEASE_BINDING_REJECTION_CONTROLS', controls=outcomes), indent=2))


if __name__ == '__main__':
    main()
