# SPDX-License-Identifier: Apache-2.0
"""Finite certificate checks; full literal and release replays are separate."""
import sys
if not __debug__ or sys.flags.optimize:
    raise RuntimeError('Assertions must be enabled for scientific replay')
import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def main():
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    for row in sources['files']:
        if row['usage'] != 'input':
            continue
        path = REPO / row['path']
        if path.is_symlink() or not path.is_file():
            raise ValueError('missing regular input: ' + row['path'])
        if hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('changed source: ' + row['path'])
    env = dict(os.environ, OWNER_SOURCE_REPO=str(REPO),
               PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1',
               OMP_NUM_THREADS='1')
    for key in ('PYTHONPATH', 'PYTHONOPTIMIZE', 'WITNESS_SPEC',
                'WITNESS_RECORD', 'WITNESS_DISCOVER'):
        env.pop(key, None)
    for name in ('owners/verify_owner.py', 'owners/test_owner_guards.py',
                 'test_replay_guards.py', 'test_entry_auth.py',
                 'verify_evidence.py', 'test_evidence.py'):
        command = [sys.executable, '-B', str(HERE / name)]
        if name == 'test_entry_auth.py':
            command += ['--t8-package', str(REPO / 'research/t8-rank7-two-swaps')]
        subprocess.run(command, env=env, check=True)
    print('PASS_T530_FINITE_AND_STORED_RELEASE_NOT_FRESH_FULL_REPLAY')


if __name__ == '__main__':
    main()
