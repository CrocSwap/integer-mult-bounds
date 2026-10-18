#!/usr/bin/env python3
"""Alternating fresh-process A/B timings; every full receipt must agree."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def timed_run(mode, kind, h):
    command = [sys.executable, '-I', '-B', str(PACKAGE / 'accelerator.py'),
               '--mode', mode, '--kind', kind, '--h', str(h)]
    start = time.perf_counter()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=True)
    elapsed = time.perf_counter()-start
    return elapsed, json.loads(result.stdout)


def benchmark(pairs):
    cases = []
    for kind, h in (('certificate', 25), ('screen', 25), ('screen', 28)):
        samples = []
        reference_receipt = None
        for pair in range(pairs):
            order = ('reference', 'accelerated') if pair % 2 == 0 else ('accelerated', 'reference')
            sample = {'order': list(order)}
            for mode in order:
                seconds, result = timed_run(mode, kind, h)
                if reference_receipt is None:
                    reference_receipt = result
                if json.dumps(result, sort_keys=True) != json.dumps(reference_receipt, sort_keys=True):
                    raise ValueError('Timed receipts differ')
                sample[mode+'_wall_seconds'] = seconds
            samples.append(sample)
        reference = statistics.median(s['reference_wall_seconds'] for s in samples)
        accelerated = statistics.median(s['accelerated_wall_seconds'] for s in samples)
        canonical = json.dumps(reference_receipt, sort_keys=True, separators=(',', ':')).encode()
        cases.append({'kind': kind, 'h': h, 'pairs': pairs, 'samples': samples,
                      'reference_median_wall_seconds': reference,
                      'accelerated_median_wall_seconds': accelerated,
                      'median_ratio': reference/accelerated,
                      'receipt_sha256': sha256(canonical).hexdigest(),
                      'receipt': reference_receipt})
    return {'status': 'PASS_IDENTICAL_SPARSE_FUSION_BENCHMARK_RECEIPTS',
            'recorded_at_utc': datetime.now(timezone.utc).isoformat(),
            'base_commit': 'f567884aeb8851b6e794af1184119a3bfbe1e631',
            'environment': {'python': sys.version, 'executable': sys.executable,
                            'platform': platform.platform(), 'machine': platform.machine()},
            'timing_scope': 'Fresh process wall time, including startup, source hashing, imports, exact checks and JSON serialization. No timing threshold; OS caches not flushed and host not isolated.',
            'source_manifest_sha256': sha256((PACKAGE/'SOURCES.json').read_bytes()).hexdigest(),
            'implementation_sha256': {p.name: sha256(p.read_bytes()).hexdigest()
                                      for p in (PACKAGE/'accelerator.py', PACKAGE/'benchmark.py')},
            'cases': cases}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pairs', type=int, default=5)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.pairs < 1:
        parser.error('--pairs must be positive')
    if args.output.exists():
        parser.error('Output already exists; use a fresh path')
    result = benchmark(args.pairs)
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    for case in result['cases']:
        print(f"{case['kind']} h={case['h']} reference={case['reference_median_wall_seconds']:.6f}s accelerated={case['accelerated_median_wall_seconds']:.6f}s ratio={case['median_ratio']:.3f}x")
    print(result['status'])


if __name__ == '__main__':
    main()
