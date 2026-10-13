# SPDX-License-Identifier: Apache-2.0
"""Alternating fresh-process timings; compares every complete output exactly."""
import argparse
import hashlib
import json
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import adapter as A


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pairs', type=int, default=7)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    A.require(args.pairs >= 3, 'Use at least three alternating pairs')
    A.require(not args.out.exists(), 'Output path must be fresh')
    expected = json.loads((HERE / 'EXPECTED.json').read_text())
    result = dict(status='PASS_R420_RREF_BENCHMARK', python=sys.version,
                  platform=platform.platform(), machine=platform.machine(),
                  timing_scope='fresh worker process including imports/pins; warm OS caches, not flushed',
                  source_pins=json.loads((HERE / 'SOURCES.json').read_text()),
                  code_sha256={p.relative_to(HERE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in sorted(HERE.rglob('*.py'))}, pairs=args.pairs, workloads={})
    for suite, expected_hash in [('check', expected['complete_check_sha256']),
                                  ('controls', expected['controls_sha256'])]:
        records = []
        for pair in range(args.pairs):
            outputs = {}
            for engine in (('reference', 'integer') if pair % 2 == 0 else ('integer', 'reference')):
                command = [sys.executable, '-I', '-B', str(HERE / 'worker.py'), engine, suite]
                start = time.perf_counter()
                child = subprocess.run(command, capture_output=True, check=True)
                elapsed = time.perf_counter() - start
                A.require(not child.stderr, 'Unexpected benchmark stderr')
                fingerprint = hashlib.sha256(child.stdout).hexdigest()
                A.require(fingerprint == expected_hash, 'Benchmark receipt differs from verified receipt')
                outputs[engine] = child.stdout
                records.append(dict(pair=pair, engine=engine, seconds=elapsed, stdout_sha256=fingerprint))
            A.require(outputs['reference'] == outputs['integer'], 'Pair outputs differ')
        medians = {engine: statistics.median(r['seconds'] for r in records if r['engine'] == engine)
                   for engine in ('reference', 'integer')}
        result['workloads'][suite] = dict(records=records, median_seconds=medians,
                                          speedup=medians['reference']/medians['integer'])
    with args.out.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True); stream.write('\n')
    print(result['status'])
    for suite, data in result['workloads'].items():
        print(suite, data['median_seconds'], 'speedup', data['speedup'])


if __name__ == '__main__':
    main()
