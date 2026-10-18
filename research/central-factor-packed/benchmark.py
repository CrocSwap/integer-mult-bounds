#!/usr/bin/env python3
"""Alternate fresh processes on identical pinned inputs, without a speed gate."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pairs', type=int, default=3)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.pairs < 1 or args.output.exists():
        parser.error('Require positive pairs and a new output path')
    samples = []
    for scope in ('factor', 'complete_historical_audit'):
        receipts = set()
        for pair in range(args.pairs):
            order = ('baseline', 'packed') if pair % 2 == 0 else ('packed', 'baseline')
            for engine in order:
                command = [sys.executable, '-I', '-B', str(HERE / 'verify.py'), '--engine', engine]
                if scope == 'factor':
                    command.append('--factor-only')
                start = time.perf_counter()
                proc = subprocess.run(command, capture_output=True, text=True, check=True)
                elapsed = time.perf_counter() - start
                result = json.loads(proc.stdout)
                if result['scope'] != scope or result['status'] != 'PASS_CENTRAL_FACTOR_PACKED':
                    raise ValueError('Unexpected benchmark receipt')
                receipts.add(result['receipt_sha256'])
                samples.append(dict(pair=pair, wall_seconds=elapsed, **result))
                print(scope, pair, engine, f'{elapsed:.6f}s', flush=True)
        if len(receipts) != 1:
            raise ValueError('Engines produced different receipts')
    medians = {}
    for scope in ('factor', 'complete_historical_audit'):
        times = {engine: statistics.median(x['wall_seconds'] for x in samples
                 if x['scope'] == scope and x['engine'] == engine)
                 for engine in ('baseline', 'packed')}
        medians[scope] = dict(times, speedup=times['baseline'] / times['packed'])
    result = dict(assignment_seed=93, pairs=args.pairs, fresh_processes=True,
                  python=sys.version, platform=platform.platform(), machine=platform.machine(),
                  clock='time.perf_counter', median_wall_seconds=medians, samples=samples,
                  implementation_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in (HERE / 'packed.py', HERE / 'verify.py', HERE / 'benchmark.py')},
                  note='Descriptive local timing; no performance pass/fail threshold. '
                       'Complete audit includes source admission and full certificate comparison.')
    with args.output.open('x') as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
