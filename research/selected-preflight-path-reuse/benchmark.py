#!/usr/bin/env python3
"""Alternating fresh-process timings; no performance pass threshold or result cache.

Arham Tahir with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

from verify import HERE, ROOT, check_sources, load, require


def worker(engine):
    sources = check_sources()
    for name, expected in sources['benchmark_sources'].items():
        require(sha256((ROOT / name).read_bytes()).hexdigest() == expected,
                'Benchmark fixture changed: ' + name)
    path = ROOT / 'scripts/verify_selected_result.py' if engine == 'baseline' else HERE / 'candidate.py'
    checker = load('measured_preflight', path)
    record = json.loads((ROOT / 'certificates/selected-result.json').read_text())
    start = time.perf_counter()
    kappa = checker.check(record)
    elapsed = time.perf_counter() - start
    print(json.dumps(dict(engine=engine, seconds=elapsed, kappa=str(kappa))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pairs', type=int, default=7)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--worker', choices=('baseline', 'candidate'), help=argparse.SUPPRESS)
    args = parser.parse_args()
    require(not sys.flags.optimize, 'Assertions must remain enabled')
    if args.worker:
        worker(args.worker)
        return
    require(3 <= args.pairs <= 30, 'Use 3..30 alternating pairs')
    require(args.out is not None and not args.out.exists(), 'Use a fresh --out file')
    sources = check_sources()
    # Verify the full fixture once before measuring; no cold-disk timing claim.
    env = os.environ.copy()
    env.pop('PYTHONOPTIMIZE', None)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    def run(engine):
        start = time.perf_counter()
        result = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()),
                                 '--worker', engine], cwd=ROOT, env=env,
                                capture_output=True, text=True, timeout=30, check=True)
        return dict(json.loads(result.stdout), process_seconds=time.perf_counter() - start)
    run('baseline')
    rows = []
    for pair in range(args.pairs):
        for engine in (('baseline', 'candidate') if pair % 2 == 0 else ('candidate', 'baseline')):
            row = run(engine)
            require(row['kappa'] == '836330098538459/500000000000000000', 'Result differs')
            rows.append(dict(pair=pair, **row))
    medians = {engine: statistics.median(row['seconds'] for row in rows if row['engine'] == engine)
               for engine in ('baseline', 'candidate')}
    process_medians = {engine: statistics.median(row['process_seconds'] for row in rows if row['engine'] == engine)
                       for engine in ('baseline', 'candidate')}
    receipt = dict(scope='Selected source-binding check only; complete inputs, warm filesystem, fresh Python process per sample; excludes startup/import/source-pin overhead.',
                   base_commit=sources['base_commit'], python=sys.version,
                   platform=platform.platform(), machine=platform.machine(),
                   generated_at_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                   candidate_sha256=sha256((HERE / 'candidate.py').read_bytes()).hexdigest(),
                   baseline_sha256=sources['live_sources']['scripts/verify_selected_result.py'],
                   benchmark_sources=sources['benchmark_sources'], samples=rows,
                   median_seconds=medians, ratio=medians['baseline'] / medians['candidate'],
                   median_process_seconds=process_medians,
                   process_ratio=process_medians['baseline'] / process_medians['candidate'],
                   timing_is_acceptance_gate=False)
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(median_seconds=medians, ratio=receipt['ratio'])))


if __name__ == '__main__':
    main()
