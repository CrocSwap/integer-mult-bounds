"""Authenticate and replay the scoped cold-host restoration package."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent


def authenticate():
    manifest = json.loads((PACKAGE / 'MANIFEST.json').read_text())
    if manifest.get('schema') != 'sha256-package-files-v1':
        raise ValueError('unknown manifest schema')
    for name, expected in manifest['files'].items():
        path = Path(name)
        if path.is_absolute() or '..' in path.parts or str(path) != name:
            raise ValueError('noncanonical manifest path')
        content = (PACKAGE / path).read_bytes()
        if hashlib.sha256(content).hexdigest() != expected['sha256'] or len(content) != expected['bytes']:
            raise ValueError('package input changed: ' + name)
    return len(manifest['files'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--part', choices=('all','operator','direct','hyperplanes','pricing'), default='all')
    args = parser.parse_args()
    if not 1 <= args.workers <= 24:
        raise ValueError('workers must be between 1 and 24')
    count = authenticate()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1',
               OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', NUMEXPR_NUM_THREADS='1')
    env.pop('PYTHONOPTIMIZE', None)
    parts = ['operator','direct','hyperplanes','pricing'] if args.part == 'all' else [args.part]
    # -B disables cache writes, not reads. A fresh cache namespace ensures
    # imports use the authenticated source even beside a stale matching .pyc.
    with tempfile.TemporaryDirectory(prefix='cold-host-replay-') as cache:
        for part in parts:
            command = [sys.executable, '-I', '-S', '-B', '-X',
                       'pycache_prefix=' + cache,
                       str(PACKAGE / part / 'verify.py')]
            if part in ('direct','hyperplanes'):
                command += ['--workers',str(args.workers)]
            result = subprocess.run(command, env=env, check=False)
            if result.returncode:
                raise SystemExit(result.returncode)
    print(json.dumps({'status':'PASS_COLD_HOST_RESTORATION_SCOPED_PACKAGE',
                      'authenticated_files':count,'parts':parts,
                      'claim':'No new kappa; algebra/frame fixture, scoped direct-undo obstruction and exact pattern budgets.'},sort_keys=True))


if __name__ == '__main__':
    main()
