#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Alternating fresh-process benchmarks of the same complete PR3168 check."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import resource
import statistics
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load_adapter():
    spec = importlib.util.spec_from_file_location('adapter', HERE / 'adapter.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pairs', type=int, default=3)
    ap.add_argument('--out', type=Path)
    ap.add_argument('--worker', choices=('reference', 'tables'))
    args = ap.parse_args()
    if args.worker:
        adapter = load_adapter()
        start = time.perf_counter()
        result = adapter.run(args.worker)
        seconds = time.perf_counter() - start
        usage = resource.getrusage(resource.RUSAGE_SELF)
        print(json.dumps(dict(engine=args.worker, seconds=seconds,
                             max_rss=usage.ru_maxrss,
                             receipt_sha256=hashlib.sha256(result).hexdigest())))
        return
    if not 1 <= args.pairs <= 7 or args.out is None or args.out.exists():
        raise SystemExit('use 1..7 pairs and a fresh --out path')
    samples = []
    for pair in range(args.pairs):
        order = ('tables', 'reference') if (91 + pair) % 2 else ('reference', 'tables')
        for engine in order:
            start = time.perf_counter()
            child = subprocess.run([sys.executable, '-I', '-B', str(Path(__file__).resolve()),
                                    '--worker', engine], cwd=ROOT, capture_output=True,
                                   text=True, check=True, timeout=300)
            row = json.loads(child.stdout)
            row.update(pair=pair, process_seconds=time.perf_counter() - start)
            samples.append(row)
            print(engine, row['process_seconds'], flush=True)
    if len({x['receipt_sha256'] for x in samples}) != 1:
        raise ValueError('complete receipts differ')
    medians = {engine: statistics.median(x['process_seconds'] for x in samples if x['engine'] == engine)
               for engine in ('reference', 'tables')}
    files = ('adapter.py', 'kernel.py', 'benchmark.py', 'SOURCES.json')
    result = dict(status='PASS_IDENTICAL_COMPLETE_FANO_BENCHMARK', pairs=args.pairs,
                  seed=91, samples=samples, median_process_seconds=medians,
                  speedup=medians['reference'] / medians['tables'],
                  python=sys.version, platform=platform.platform(),
                  rss_units='bytes' if sys.platform == 'darwin' else 'KiB (Linux)',
                  code_sha256={f: hashlib.sha256((HERE / f).read_bytes()).hexdigest() for f in files},
                  scope='Whole PR3168 check, pins, route derivation, full census, Fano searches and controls; fresh processes, warm filesystem caches; no full supplier replay.')
    with args.out.open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(result['status'], result['speedup'])


if __name__ == '__main__':
    main()
