#!/usr/bin/env python3
"""Alternating fresh-process A/B of the complete pinned historical audit.

Copyright 2026 Curtis Dransfield, substantial OpenAI Codex assistance.
Apache-2.0. Timing is observational; certificate equality is mandatory.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pairs', type=int, default=3)
    parser.add_argument('--out', type=Path, required=True, help='fresh JSON result file')
    args = parser.parse_args()
    if args.pairs < 1 or args.out.exists() or sys.flags.optimize:
        parser.error('Use positive pairs, enabled assertions and a fresh output file')
    expected = (ROOT / 'certificates/quadratic-affine-vectors.json').read_bytes()
    result = dict(started_utc=datetime.now(timezone.utc).isoformat(),
                  python=sys.version, executable=sys.executable, platform=platform.platform(),
                  machine=platform.machine(), pairs=args.pairs,
                  timing_scope='Fresh serial child wall time including interpreter, imports, source checks, complete audit, certificate comparison and output',
                  os_caches_flushed=False, samples=[],
                  source_manifest_sha256=sha256((HERE / 'SOURCES.json').read_bytes()).hexdigest(),
                  implementation_sha256={p.name: sha256(p.read_bytes()).hexdigest()
                                         for p in (HERE / 'packed.py', HERE / 'replay.py', Path(__file__))})
    with tempfile.TemporaryDirectory(prefix='quadratic-affine-benchmark-') as tmp:
        for pair in range(args.pairs):
            order = ('original', 'packed') if pair % 2 == 0 else ('packed', 'original')
            for engine in order:
                out = Path(tmp) / f'{pair}-{engine}.json'
                command = [sys.executable, '-I', '-B', str(HERE / 'replay.py'),
                           '--engine', engine, '--out', str(out)]
                print(f'RUN pair={pair + 1} engine={engine}', flush=True)
                start = time.perf_counter()
                completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
                elapsed = time.perf_counter() - start
                if completed.returncode:
                    raise RuntimeError(f'{engine} failed: {completed.stdout}\n{completed.stderr}')
                if out.read_bytes() != expected:
                    raise ValueError('Benchmark certificate mismatch')
                result['samples'].append(dict(pair=pair + 1, engine=engine, wall_seconds=elapsed,
                    certificate_sha256=sha256(out.read_bytes()).hexdigest(),
                    stdout=completed.stdout, stderr=completed.stderr, returncode=completed.returncode))
                print(f'PASS pair={pair + 1} engine={engine} seconds={elapsed:.6f}', flush=True)
    medians = {engine: statistics.median(s['wall_seconds'] for s in result['samples']
                                        if s['engine'] == engine) for engine in ('original', 'packed')}
    result.update(median_seconds=medians,
                  observed_speedup=medians['original'] / medians['packed'],
                  finished_utc=datetime.now(timezone.utc).isoformat())
    with args.out.open('x') as out:
        out.write(json.dumps(result, indent=2) + '\n')
    print('PASS_QUADRATIC_AFFINE_BENCHMARK certificates_equal=true ' +
          f"observed_speedup={result['observed_speedup']:.3f}")


if __name__ == '__main__':
    main()
