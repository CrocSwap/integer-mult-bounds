#!/usr/bin/env python3
"""Alternate complete original and adapted audits in fresh processes."""
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
    parser.add_argument('--pairs', type=int, default=5)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.pairs < 1 or args.output.exists():
        parser.error('Require positive pairs and a new output path')
    samples = []
    receipts = set()
    manifests = set()
    for pair in range(args.pairs):
        order = ('baseline', 'propagated') if pair % 2 == 0 else ('propagated', 'baseline')
        for engine in order:
            command = [sys.executable, '-I', '-B', str(HERE / 'verify.py'), '--engine', engine]
            start = time.perf_counter()
            proc = subprocess.run(command, capture_output=True, text=True, check=True)
            elapsed = time.perf_counter() - start
            result = json.loads(proc.stdout)
            if (result['status'] != 'PASS_DISJOINT_FRAME_UNIONS' or
                    result['scope'] != 'complete_historical_audit' or result['engine'] != engine):
                raise ValueError('Unexpected benchmark receipt')
            receipts.add(result['receipt_sha256'])
            manifests.add(result['source_manifest_sha256'])
            samples.append(dict(pair=pair, wall_seconds=elapsed, **result))
            print(pair, engine, f'{elapsed:.6f}s', flush=True)
    if len(receipts) != 1 or len(manifests) != 1:
        raise ValueError('Benchmark receipts or sources differ')
    medians = {engine: statistics.median(x['wall_seconds'] for x in samples if x['engine'] == engine)
               for engine in ('baseline', 'propagated')}
    result = dict(status='PASS_IDENTICAL_COMPLETE_CERTIFICATES', assignment_seed=88,
                  pairs=args.pairs, fresh_processes=True, python=sys.version,
                  platform=platform.platform(), machine=platform.machine(),
                  clock='time.perf_counter', median_wall_seconds=medians,
                  speedup=medians['baseline']/medians['propagated'], samples=samples,
                  implementation_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in (HERE/'accelerator.py', HERE/'verify.py', HERE/'benchmark.py')},
                  note='Local descriptive timings, not a speed threshold. Each complete audit '
                       'includes source admission and byte-identical certificate comparison.')
    with args.output.open('x') as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'], medians, 'speedup', result['speedup'])


if __name__ == '__main__':
    main()
