"""Bounded source-isolated replay; --physical includes the five-minute witness."""
import argparse
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
        raise ValueError(message)


def science(row):
    historical = {'seconds', 'publication', 'public_core_commit', 'draft_publication_blocker'}
    return {k: v for k, v in row.items() if k not in historical}


def run(name, optimized=False, physical=False):
    with tempfile.TemporaryDirectory(prefix='core-halo-source-replay-') as temp:
        temp = Path(temp)
        env = dict(os.environ)
        env.pop('PYTHONOPTIMIZE', None)
        env['PYTHONPYCACHEPREFIX'] = str(temp / 'bytecode')
        command = [sys.executable, '-B', '-X', 'pycache_prefix=' + str(temp / 'bytecode')]
        if optimized:
            command.append('-O')
        command.append(str(HERE / name))
        if physical:
            command += ['--output', str(temp / 'actual.json')]
        proc = subprocess.run(command, cwd=ROOT, env=env, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=600 if physical else 120)
        require(proc.returncode == 0, 'child failed: ' + name + '\n' + proc.stderr[-4000:])
        lines = proc.stdout.splitlines()
        if physical:
            require('PASS_ACTUAL_CORE_SOURCE_BRIDGE' in lines, 'missing physical completion marker')
            actual = json.loads((temp / 'actual.json').read_text())
            expected = json.loads((HERE / 'evidence/actual-core.json').read_text())
        else:
            require(lines and lines[-1].startswith('PASS_'), 'missing replay completion marker')
            actual = json.loads(lines[0])
            short = 'codec' if 'codec' in name else 'binding'
            expected = json.loads((HERE / 'evidence' / (short + '.json')).read_text())
        require(science(actual) == science(expected), 'scientific or machine-operation receipt changed: ' + name)
        return {'command': name, 'optimized': optimized, 'status': actual['status']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--physical', action='store_true',
                        help='include the actual packed native Core witness; allow 600 seconds')
    args = parser.parse_args()
    rows = []
    for optimized in (False, True):
        for name in ('verify_codec.py', 'verify_binding.py'):
            rows.append(run(name, optimized))
    if args.physical:
        rows.append(run('verify_actual_core.py', physical=True))
    print(json.dumps({'status': 'PASS_CORE_HALO_REPLAY', 'checks': rows,
                      'physical_reexecuted': args.physical, 'no_new_kappa': True}, sort_keys=True))


if __name__ == '__main__':
    main()
