#!/usr/bin/env python3
"""Alternating fresh-process A/B of the original CLI and mask adapter."""
import argparse
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
sp = importlib.util.spec_from_file_location('verify', HERE / 'verify.py')
V = importlib.util.module_from_spec(sp)
sp.loader.exec_module(V)
A = V.A
try:
    import resource
except ImportError:
    resource = None


def child_cpu():
    if resource is None:
        return None
    r = resource.getrusage(resource.RUSAGE_CHILDREN)
    return r.ru_utime + r.ru_stime


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pairs', type=int, default=31)
    ap.add_argument('--out', type=Path, required=True, help='New result file; never overwritten')
    args = ap.parse_args()
    A.require(3 <= args.pairs <= 101, 'pairs must be in [3,101]')
    A.require(not args.out.exists(), 'output must not already exist')
    A.check_pins()
    expected = (HERE / 'evidence/EXPECTED.json').read_bytes()
    rows = []
    with tempfile.TemporaryDirectory(prefix='owner masks benchmark ') as tmp:
        for i in range(args.pairs):
            order = ('sets', 'masks') if (91 + i) % 2 else ('masks', 'sets')
            for engine in order:
                out = Path(tmp) / ('%d-%s.json' % (i, engine))
                cmd = V.command(A.ROOT, engine, out, direct=engine == 'sets')
                cpu0 = child_cpu()
                start = time.perf_counter_ns()
                r = subprocess.run(cmd, capture_output=True, timeout=30)
                elapsed = (time.perf_counter_ns() - start) / 1e9
                cpu1 = child_cpu()
                A.require(r.returncode == 0, r.stderr.decode())
                A.require(r.stdout == b'PASS independent map and exact moments\n' and not r.stderr,
                          'checker diagnostics changed')
                A.require(out.read_bytes() == expected, 'complete checker receipt changed')
                rows.append(dict(pair=i, engine=engine, wall_seconds=elapsed,
                                 child_cpu_seconds=None if cpu0 is None else cpu1 - cpu0))
    A.check_pins()
    medians = {engine: statistics.median(row['wall_seconds'] for row in rows if row['engine'] == engine)
               for engine in ('sets', 'masks')}
    paired = [next(r['wall_seconds'] for r in rows if r['pair'] == i and r['engine'] == 'sets') /
              next(r['wall_seconds'] for r in rows if r['pair'] == i and r['engine'] == 'masks')
              for i in range(args.pairs)]
    code = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(HERE.glob('*.py'))}
    receipt = dict(status='PASS_OWNER_FOOTPRINT_BENCHMARK',
                   utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   python=sys.version, executable=sys.executable, platform=platform.platform(),
                   pairs=args.pairs, order='alternating; sets first when (91 + pair) % 2 != 0',
                   reference='unchanged pinned checker, direct CLI',
                   candidate='adapter CLI including source pin validation and counted substitution',
                   process='fresh interpreter each sample; same archived inputs; OS caches not flushed',
                   code_sha256=code,
                   origins_sha256=hashlib.sha256((HERE / 'ORIGINS.json').read_bytes()).hexdigest(),
                   expected_receipt_sha256=hashlib.sha256(expected).hexdigest(),
                   median_wall_seconds=medians,
                   ratio_of_medians=medians['sets'] / medians['masks'],
                   wall_time_reduction_percent=100 * (1 - medians['masks'] / medians['sets']),
                   median_paired_speedup=statistics.median(paired),
                   pairs_masks_faster=sum(r > 1 for r in paired), samples=rows,
                   scope='Independent owner checker only, not full supplier replay or multiplication runtime.')
    with args.out.open('x') as f:
        json.dump(receipt, f, indent=2)
        f.write('\n')
    print('PASS_OWNER_FOOTPRINT_BENCHMARK', json.dumps(medians),
          'ratio_of_medians=%.3f' % receipt['ratio_of_medians'])


if __name__ == '__main__':
    main()
