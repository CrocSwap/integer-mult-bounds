#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Sequential replay of the local kappa=0.1 investigation, not a supplier test."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def check_files(receipt):
    for name, expected in receipt['files'].items():
        require(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,
                'bundle source or receipt changed: '+name)
    for name, expected in receipt['base_files'].items():
        raw = subprocess.check_output(['git','show',receipt['base_commit']+':'+name],cwd=ROOT)
        require(hashlib.sha256(raw).hexdigest()==expected, 'base object changed: '+name)
        require((ROOT/name).read_bytes()==raw, 'selected/base working file changed: '+name)


def main():
    receipt = json.loads((HERE/'REPLAY.json').read_text())
    check_files(receipt)
    env = os.environ.copy()
    env.pop('PYTHONOPTIMIZE',None)
    with tempfile.TemporaryDirectory(prefix='kappa01-replay-') as temp:
        for index, args in enumerate(receipt['commands']):
            cmd = [sys.executable,'-I','-O','-B','-X',f'pycache_prefix={temp}/{index}',*args]
            result = subprocess.run(cmd,cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,timeout=180)
            require(result.returncode==0, 'replay failed: '+str(args)+'\n'+result.stdout)
            lines = [line for line in result.stdout.splitlines() if line.startswith('PASS')]
            require(lines, 'missing result marker: '+str(args))
            print(lines[-1],flush=True)
    check_files(receipt)
    print(f"PASS_KAPPA01_REPAIR_BUNDLE exact_scoped_replays={len(receipt['commands'])} selected_unchanged no_new_kappa")


if __name__=='__main__':
    main()
