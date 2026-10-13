#!/usr/bin/env python3
"""Before/after benchmark and receipt-equivalence check for run_isolated_tests.

Before: runs every test module with the exact sequential command the
pre-change runner used, capturing each module's stdout/stderr bytes.
After: runs the concurrent scheduler from scripts/run_isolated_tests.py
(run_modules) over the same modules with the same commands.

Then it compares per-module exit codes and byte streams. unittest -v
embeds a wall-clock field ("Ran N tests in T.TTTs") in stderr, so stderr
is compared both raw and with that single field normalized; stdout is
compared raw. The failing-module sets must match exactly.

Usage: python3 -B research/agent-07-verifeng-seed88/benchmark.py
Requires --output /fresh/path.json; preserves submitted evidence.
All differences remaining after unittest timing normalization fail acceptance;
same-mode nondeterminism is diagnostic only.
"""
import argparse
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TIMING = re.compile(r'in \d+\.\d+s')


def load_runner():
    spec = spec_from_file_location('run_isolated_tests', ROOT / 'scripts' / 'run_isolated_tests.py')
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(data):
    return sha256(data).hexdigest()


def normalize(data):
    return TIMING.sub('in T', data.decode('utf-8', errors='replace')).encode()


def record(results):
    out = {}
    for path, code, stdout, stderr in results:
        out[path.name] = {
            'code': code,
            'stdout_sha256': digest(stdout),
            'stderr_sha256': digest(stderr),
            'stderr_normalized_sha256': digest(normalize(stderr)),
        }
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit('Output already exists')
    if args.workers < 1:
        parser.error('--workers must be positive')
    runner = load_runner()
    files = sorted((ROOT / 'tests').glob('test*.py'))
    workers = min(len(files), args.workers)

    sequential = []
    start = time.perf_counter()
    for path in files:
        result = subprocess.run(
            runner.module_command(sys.executable, ROOT / 'tests', path.name),
            cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sequential.append((path, result.returncode, result.stdout, result.stderr))
    seq_wall = time.perf_counter() - start

    start = time.perf_counter()
    concurrent = runner.run_modules(files, workers=workers)
    par_wall = time.perf_counter() - start

    seq_rec, par_rec = record(sequential), record(concurrent)
    mismatches = []
    code_mismatches = []
    raw_equal = normalized_equal = 0
    for path in files:
        s, p = seq_rec[path.name], par_rec[path.name]
        if s['code'] != p['code']:
            code_mismatches.append(path.name)
        if s['stdout_sha256'] == p['stdout_sha256'] and s['stderr_sha256'] == p['stderr_sha256']:
            raw_equal += 1
        if s['stdout_sha256'] == p['stdout_sha256'] and s['stderr_normalized_sha256'] == p['stderr_normalized_sha256']:
            normalized_equal += 1
        else:
            mismatches.append(path.name)

    # A module whose receipts differ between schedules is acceptable only if its
    # output is nondeterministic across two runs of the SAME schedule as well
    # (for example a failing traceback embedding a random temporary path).
    inherent = []
    scheduling_driven = []
    for name in mismatches:
        runs = []
        for _ in range(2):
            result = subprocess.run(
                runner.module_command(sys.executable, ROOT / 'tests', name),
                cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            runs.append((result.returncode, result.stdout, result.stderr))
        same = (runs[0][0] == runs[1][0] and runs[0][1] == runs[1][1]
                and normalize(runs[0][2]) == normalize(runs[1][2]))
        (inherent if not same else scheduling_driven).append(name)

    evidence = {
        'runner': 'scripts/run_isolated_tests.py',
        'baseline': 'per-module sequential command of the pre-change runner (identical commands, sequential scheduling)',
        'python': sys.version.split()[0],
        'cpu_count': os.cpu_count(),
        'workers': workers,
        'modules': len(files),
        'sequential_wall_seconds': round(seq_wall, 2),
        'concurrent_wall_seconds': round(par_wall, 2),
        'speedup': round(seq_wall / par_wall, 2) if par_wall else None,
        'raw_equal_modules': raw_equal,
        'normalized_equal_modules': normalized_equal,
        'code_mismatches': code_mismatches,
        'receipt_mismatches': mismatches,
        'inherently_nondeterministic': inherent,
        'scheduling_driven_mismatches': scheduling_driven,
        'sequential_failing': sorted(n for n, r in seq_rec.items() if r['code']),
        'concurrent_failing': sorted(n for n, r in par_rec.items() if r['code']),
        'per_module_sequential': seq_rec,
        'per_module_concurrent': par_rec,
    }
    with args.output.open('x') as stream:
        stream.write(json.dumps(evidence, indent=1) + '\n')
    print(json.dumps({k: v for k, v in evidence.items()
                      if not k.startswith('per_module')}, indent=1))
    if code_mismatches or mismatches:
        raise SystemExit('scheduling changed behavior: %r %r' % (code_mismatches, scheduling_driven))
    print('PASS identical exit codes (%d modules); receipts identical for %d modules '
          'modulo the unittest timing field; %d module(s) inherently nondeterministic '
          'across same-mode runs: %r' % (len(files), normalized_equal, len(inherent), inherent))


if __name__ == '__main__':
    main()
