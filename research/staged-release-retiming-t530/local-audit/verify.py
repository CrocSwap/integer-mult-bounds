#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Run the self-contained local retiming audit; Python standard library only."""
from pathlib import Path
import argparse
import tempfile
import hashlib
import json
import os
import subprocess
import sys

HERE = Path(__file__).resolve().parent

def need(condition, explanation):
    if not condition:
        raise RuntimeError(explanation)

def main():
    need(__debug__, 'Run without Python optimization: assertions must remain enabled.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='Fresh output directory outside this package; default: a temporary directory.')
    args = parser.parse_args()
    if args.out is None:
        out = Path(tempfile.mkdtemp(prefix='retiming-local-'))
    else:
        out = args.out.resolve()
        need(not out.exists(), 'Fresh --out directory required')
        need(out != HERE and HERE not in out.parents, 'Output must be outside the package')
        out.mkdir(parents=True)
    manifest = json.loads((HERE / 'MANIFEST.json').read_text())
    for name, expected in manifest['sha256'].items():
        path = HERE / name
        need(path.is_file(), 'Missing input: ' + name)
        need(hashlib.sha256(path.read_bytes()).hexdigest() == expected, 'SHA256 mismatch: ' + name)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1')
    env.pop('PYTHONOPTIMIZE', None)
    stages = []
    def run(name, script, *args):
        command = [sys.executable, '-I', '-B', str(HERE / script), *map(str, args)]
        result = subprocess.run(command, cwd=HERE, env=env, capture_output=True, text=True)
        log = result.stdout + result.stderr
        (out / (name + '.log')).write_text(log)
        need(result.returncode == 0, name + ' failed; see ' + str(out / (name + '.log')))
        stages.append(dict(stage=name, exit_code=result.returncode))
        print('PASS', name, flush=True)
    run('independent-minimal-proof', 'check_retiming_independent.py', '--out', out / 'RETIME-INDEPENDENT.json')
    for mode in ('base', 'extra'):
        receipt = out / ('free-operator-' + mode + '.json')
        run('free-operator-' + mode, 'vendor/audit_local.py', '--word', HERE / 'words' / ('RETIMED644-660-' + mode + '.json.gz'), '--output', receipt)
        audit = json.loads(receipt.read_text())
        need(audit['status'] == 'PASS_INDEPENDENT_EXACT_BORROWING_WORD', 'Incorrect free-operator status')
        need(audit['orientations'] == {'forward': 'PASS', 'dual': 'PASS'}, 'Incomplete orientation coverage')
        need(audit['checked_columns'] == 632 and audit['zero_buffers'] == 91, 'Incomplete input coverage')
    run('semantic-negative-controls', 'check_retiming_negative.py', '--out', out / 'negative')
    receipt = dict(status='PASS_PORTABLE_LOCAL_RETIMING_AUDIT', stages=stages,
                   pinned_files=len(manifest['sha256']),
                   scope='Fresh minimal scalar/frame proof, exact free-operator replay for both suppliers, semantic negative controls, and authenticated prior complete native receipts. Global owner/physical/outer admission and a fresh full native rerun are outside this capsule.')
    (out / 'VERIFY.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], flush=True)
    print('Fresh evidence:', out, flush=True)

if __name__ == '__main__':
    main()
