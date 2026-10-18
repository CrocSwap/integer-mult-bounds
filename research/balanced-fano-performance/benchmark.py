#!/usr/bin/env python3
"""Sequential fresh-process A/B of the complete fixed balanced-Fano search.

Uses only the standard library. Run on macOS or Linux; no timing threshold is
an acceptance criterion. Every sample must reproduce the pinned exact result.
Wentao Li, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import hashlib
import json
import os
import platform
from pathlib import Path
import random
import resource
import statistics
import subprocess
import sys
import time

from common import HERE, ROOT, canonical, load_baseline, source_pins


def worker(mode):
    pins = source_pins()
    if mode == 'baseline':
        module = load_baseline()
    else:
        from experiments import balanced_fano as module
    model = module.balanced_fano()
    wall = time.perf_counter()
    cpu = time.process_time()
    result = module.existence(model['W'], model['pairs'], model['prescribed'])
    cpu = time.process_time() - cpu
    wall = time.perf_counter() - wall
    if canonical(result) != canonical(pins['expected_result']):
        raise ValueError(f'{mode} did not reproduce the complete pinned result')
    return {
        'mode': mode,
        'wall_seconds': wall,
        'cpu_seconds': cpu,
        'peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                          * (1 if sys.platform == 'darwin' else 1024),
        'result_sha256': hashlib.sha256(canonical(result)).hexdigest(),
        'input_sha256': hashlib.sha256(canonical(model)).hexdigest(),
    }


def benchmark(rounds):
    pins = source_pins()
    env = dict(os.environ, PYTHONHASHSEED='91', PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONOPTIMIZE', None)
    first = random.Random(91).randrange(2)
    modes = ('baseline', 'packed')
    samples = []
    for trial in range(rounds):
        order = modes if (first + trial) % 2 == 0 else tuple(reversed(modes))
        for mode in order:
            start = time.perf_counter()
            process = subprocess.run(
                [sys.executable, '-B', str(HERE / 'benchmark.py'), '--worker', mode],
                cwd=ROOT, env=env, text=True, capture_output=True, check=True)
            sample = json.loads(process.stdout)
            sample['process_wall_seconds'] = time.perf_counter() - start
            sample['round'] = trial + 1
            samples.append(sample)
            print(f'round {trial + 1}: {mode} {sample["wall_seconds"]:.3f}s',
                  file=sys.stderr, flush=True)
    if len({r['result_sha256'] for r in samples}) != 1 or len({r['input_sha256'] for r in samples}) != 1:
        raise ValueError('Benchmark inputs or exact outputs differ')
    medians = {
        mode: {field: statistics.median(r[field] for r in samples if r['mode'] == mode)
               for field in ('wall_seconds', 'cpu_seconds', 'process_wall_seconds', 'peak_rss_bytes')}
        for mode in modes
    }
    return {
        'status': 'PASS_IDENTICAL_COMPLETE_RESULTS',
        'scope': 'Fixed W=10, 14-gate existence search; not the complete repository suite or selected-frontier replay',
        'base_commit': pins['base_commit'],
        'assignment_seed': 91,
        'rounds': rounds,
        'environment': {
            'python': sys.version,
            'executable': sys.executable,
            'platform': platform.platform(),
            'machine': platform.machine(),
            'cpu_count': os.cpu_count(),
            'python_hash_seed': env['PYTHONHASHSEED'],
        },
        'method': 'Fresh process for each sample, sequential alternating order; caches not flushed, no CPU affinity',
        'source_sha256': {
            name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in ('scripts/experiments/balanced_fano.py',
                         'research/balanced-fano-performance/baseline.py',
                         'research/balanced-fano-performance/common.py',
                         'research/balanced-fano-performance/benchmark.py',
                         'research/balanced-fano-performance/SOURCE.json')
        },
        'expected_result': pins['expected_result'],
        'samples': samples,
        'medians': medians,
        'wall_speedup': medians['baseline']['wall_seconds'] / medians['packed']['wall_seconds'],
        'peak_rss_reduction_fraction': 1 - medians['packed']['peak_rss_bytes'] / medians['baseline']['peak_rss_bytes'],
    }


def main():
    if sys.flags.optimize:
        raise SystemExit('Run the benchmark with assertions enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rounds', type=int, default=5)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--worker', choices=('baseline', 'packed'), help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.rounds < 1:
        parser.error('--rounds must be positive')
    if args.output and args.output.exists():
        parser.error('--output must be a fresh path')
    result = worker(args.worker) if args.worker else benchmark(args.rounds)
    rendered = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        with args.output.open('x') as stream:
            stream.write(rendered)
    else:
        print(rendered, end='')


if __name__ == '__main__':
    main()
