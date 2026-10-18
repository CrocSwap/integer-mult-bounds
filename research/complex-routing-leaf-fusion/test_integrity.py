#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Git-free read-only replay and fail-closed public-entrypoint controls."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def inventory(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def call(package, args, expected_code=0, reason=None):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PATH='')
    env.pop('PYTHONOPTIMIZE', None)
    process = subprocess.run([sys.executable, '-I', '-B', *args], cwd=package.parent,
                             env=env, capture_output=True, text=True, timeout=220)
    if expected_code == 0:
        need(process.returncode == 0, 'public replay failed: ' + process.stderr[-2000:])
    else:
        need(process.returncode != 0, 'public entry accepted corruption')
        need(reason in process.stderr + process.stdout, 'wrong failure reason: ' + process.stderr[-2000:])


def main():
    with tempfile.TemporaryDirectory(prefix='routing-leaf-export-') as directory:
        target = Path(directory) / 'relocated-package'
        shutil.copytree(HERE, target, ignore=shutil.ignore_patterns('__pycache__'))
        baseline = inventory(target)
        call(target, [str(target/'verify.py')])
        need(inventory(target) == baseline, 'successful verification wrote package files')
        # A valid source comment change is still an unauthenticated input change.
        path = target/'vendor/pr2751/independent_local.py'
        original = path.read_bytes()
        path.write_bytes(original+b'\n# unauthenticated change\n')
        call(target, [str(target/'verify.py')], 1, 'predecessor SHA256')
        path.write_bytes(original)
        # Keep the profitable claimed profile but remove the actual frame edit.
        path = target/'inputs/WORD-base.json.gz'
        original = path.read_bytes()
        value = json.loads(gzip.decompress(original))
        value['B'][1151][-1] = [259,132,66,36,16,9]
        path.write_bytes(gzip.compress(json.dumps(value).encode(), mtime=0))
        call(target, [str(target/'verify.py')], 1, 'complete generated word equality')
        path.write_bytes(original)
        # JSON numeric equality must not conflate an integer receipt with float.
        path = target/'RESULT.json'
        original = path.read_bytes()
        value = json.loads(original)
        value['calls'] = float(value['calls'])
        path.write_text(json.dumps(value))
        call(target, [str(target/'verify.py')], 1, 'complete typed RESULT.json equality')
        path.write_bytes(original)
        call(target, ['-O', str(target/'verify.py')], 1, 'run without -O')
        out = Path(directory)/'existing-output'
        out.mkdir()
        (out/'sentinel').write_text('must survive')
        call(target, [str(target/'generate.py'), '--source', str(target/'vendor/pr2751'),
                      '--out', str(out)], 1, 'Output directory must be fresh')
        need((out/'sentinel').read_text() == 'must survive', 'generator replaced output')
        need(inventory(target) == baseline, 'failure controls changed restored package')
    print('PASS_ROUTING_LEAF_INTEGRITY Git-free=1 source=1 omitted-frame=1 typed-receipt=1 optimized-refusal=1 output-preservation=1')


if __name__ == '__main__':
    main()
