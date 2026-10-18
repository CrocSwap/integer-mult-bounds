#!/usr/bin/env python3
"""Alternate fresh-process full checker runs; require byte-identical receipts."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time

from common import HERE, SOURCE, verify_sources


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pairs', type=int, default=5)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    verify_sources()
    if args.pairs < 2 or args.out.exists():
        raise ValueError('Use at least two pairs and a fresh output file')
    records = []
    with tempfile.TemporaryDirectory(prefix='clifford-state-benchmark-') as tmp:
        for pair in range(args.pairs):
            order = ('reference', 'fast') if pair % 2 == 0 else ('fast', 'reference')
            for engine in order:
                out = Path(tmp) / f'{pair}-{engine}.json'
                command = [sys.executable, '-B', str(HERE / 'run.py'),
                           '--engine', engine, '--out', str(out)]
                start = time.perf_counter()
                run = subprocess.run(command, capture_output=True, text=True)
                elapsed = time.perf_counter() - start
                if run.returncode:
                    raise RuntimeError(run.stdout + run.stderr)
                digest = hashlib.sha256(out.read_bytes()).hexdigest()
                if digest != SOURCE['expected_receipt_sha256']:
                    raise ValueError('Full checker output differs from the pinned reference')
                records.append(dict(pair=pair, engine=engine, seconds=elapsed,
                                    receipt_sha256=digest))
                print(engine, f'{elapsed:.6f}s', flush=True)
    medians = {engine: statistics.median(r['seconds'] for r in records
                                        if r['engine'] == engine)
               for engine in ('reference', 'fast')}
    result = dict(status='PASS_EXACT_FULL_HELPER_CHECK_AB', base_commit=SOURCE['base_commit'],
                  python=sys.version, platform=platform.platform(), machine=platform.machine(),
                  processor=platform.processor(), cpu_count=os.cpu_count(), seed=86,
                  scope='Archived selected native inputs; unchanged full helper-interface checker. '
                        'Fresh process for each run; OS caches not flushed. No full supplier replay.',
                  source_files=SOURCE['files'], trials=records, median_seconds=medians,
                  median_speedup=medians['reference']/medians['fast'])
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print('PASS exact receipts; median speedup:', result['median_speedup'])


if __name__ == '__main__':
    main()
