#!/usr/bin/env python3
"""Compare complete cold-process owner checks on identical pinned artifacts."""
import argparse
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
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


def worker(engine, output):
    spec = importlib.util.spec_from_file_location('footprint_adapter', HERE / 'adapter.py')
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)
    adapter.check_pins()
    with redirect_stdout(io.StringIO()) as log:
        adapter.execute(engine, output)
    usage = resource.getrusage(resource.RUSAGE_SELF)
    rss = usage.ru_maxrss * (1 if sys.platform == 'darwin' else 1024)
    print(json.dumps({'engine': engine, 'cpu_seconds': usage.ru_utime + usage.ru_stime,
                      'peak_rss_bytes': rss,
                      'receipt_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
                      'stdout': log.getvalue()}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pairs', type=int, default=15)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--worker', choices=('reference', 'bitset'), help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.out.exists():
        raise SystemExit('Use a fresh output path')
    if sys.platform not in ('darwin', 'linux'):
        raise SystemExit('Peak RSS reporting supports macOS and Linux only')
    if args.worker:
        worker(args.worker, args.out)
        return
    if args.pairs < 1:
        raise SystemExit('Use a positive pair count')
    checks = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'verify.py')],
                            text=True, capture_output=True, check=True)
    samples = []
    expected_receipt = None
    expected_stdout = None
    with tempfile.TemporaryDirectory(prefix='owner-footprint-timing-') as directory:
        for pair in range(args.pairs):
            order = ['reference', 'bitset']
            if (89 + pair) % 2:
                order.reverse()
            for engine in order:
                output = Path(directory) / f'{pair}-{engine}.json'
                start = time.perf_counter()
                result = subprocess.run([sys.executable, '-I', '-B', str(Path(__file__).resolve()),
                                         '--worker', engine, '--out', str(output)],
                                        text=True, capture_output=True, check=True)
                wall = time.perf_counter() - start
                sample = json.loads(result.stdout)
                receipt = output.read_bytes()
                if expected_receipt is None:
                    expected_receipt, expected_stdout = receipt, sample['stdout']
                if receipt != expected_receipt or sample['stdout'] != expected_stdout:
                    raise ValueError('Complete checker receipts or diagnostics differ')
                samples.append(dict(pair=pair, wall_seconds=wall, **sample))
    medians = {engine: {metric: statistics.median(row[metric] for row in samples
                                                 if row['engine'] == engine)
                        for metric in ('wall_seconds', 'cpu_seconds', 'peak_rss_bytes')}
               for engine in ('reference', 'bitset')}
    result = {
        'status': 'PASS_PR727_INDEPENDENT_BENCHMARK',
        'base_commit': '66849e1475c930fd7732b1a0067ffee7e1e95f60',
        'assignment_seed': 89,
        'candidate_pr': 727,
        'candidate_head': '71ba94c981477b3527ef21dd0f8140e795a7664d',
        'python': sys.version,
        'executable': sys.executable,
        'platform': platform.platform(),
        'pairs': args.pairs,
        'method': 'Alternating fresh processes, seed 89 selects bitset first. Complete checker, '
                  'imports and identical source admission included in wall time. OS file caches '
                  'are not flushed; no timing threshold. No construction cold replay.',
        'checks': checks.stdout.strip(),
        'implementation_sha256': {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                                  for name in ('adapter.py', 'verify.py', 'benchmark.py', 'sweep.py', 'SOURCES.json')},
        'medians': medians,
        'wall_speedup': medians['reference']['wall_seconds'] / medians['bitset']['wall_seconds'],
        'peak_rss_reduction_fraction': 1 - medians['bitset']['peak_rss_bytes'] / medians['reference']['peak_rss_bytes'],
        'receipt_sha256': hashlib.sha256(expected_receipt).hexdigest(),
        'samples': samples,
    }
    with args.out.open('x') as output:
        output.write(json.dumps(result, indent=2) + '\n')
    print(checks.stdout.strip())
    print(result['status'], json.dumps(medians), 'wall_speedup=', result['wall_speedup'])


if __name__ == '__main__':
    main()
