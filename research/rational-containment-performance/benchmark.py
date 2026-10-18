"""Sequential alternating fresh-process benchmarks; no timing pass threshold."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import statistics
import subprocess
import sys
import tempfile
import time

PACKAGE = Path(__file__).resolve().parent
EXPECTED = 'faa0f9c0159a6e70d4e2cfcdb4012ea62ef350bd26b81312d11da4a770f8b218'


def benchmark(pairs, cpu=None):
    samples = []
    payload = None
    with tempfile.TemporaryDirectory(prefix='containment-benchmark-') as temporary:
        for pair in range(pairs):
            order = ('reference', 'annihilator') if pair % 2 == 0 else ('annihilator', 'reference')
            for engine in order:
                output = Path(temporary) / f'{pair}-{engine}.json'
                command = [sys.executable, '-I', '-B', str(PACKAGE / 'adapter.py'),
                           '--engine', engine, '--output', str(output)]
                if cpu is not None:
                    command.extend(('--cpu', str(cpu)))
                before = resource.getrusage(resource.RUSAGE_CHILDREN)
                started = time.perf_counter()
                result = subprocess.run(command, text=True, capture_output=True, timeout=120)
                wall = time.perf_counter() - started
                after = resource.getrusage(resource.RUSAGE_CHILDREN)
                if result.returncode:
                    raise RuntimeError(result.stderr + result.stdout)
                record = json.loads(output.read_text())
                actual = record['result']
                digest = hashlib.sha256(json.dumps(actual, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
                if digest != EXPECTED or record['result_sha256'] != digest:
                    raise ValueError('Benchmark mathematical payload drift')
                if payload is None:
                    payload = actual
                elif payload != actual:
                    raise ValueError('Complete benchmark payload disagreement')
                samples.append(dict(pair=pair, engine=engine, process_wall_seconds=wall,
                                    child_cpu_seconds=(after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime),
                                    audit_seconds=float(record['audit_seconds']), peak_rss_kib=record['peak_rss_kib'],
                                    result_sha256=digest))
    medians = {engine: {field: statistics.median(s[field] for s in samples if s['engine'] == engine)
                       for field in ('process_wall_seconds', 'child_cpu_seconds', 'audit_seconds', 'peak_rss_kib')}
               for engine in ('reference', 'annihilator')}
    source_hashes = {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
                     for name in ('kernel.py', 'adapter.py', 'benchmark.py', 'SOURCES.json')}
    return dict(status='PASS_RATIONAL_CONTAINMENT_BENCHMARK', pairs=pairs, samples=samples,
                medians=medians, process_wall_ratio=medians['reference']['process_wall_seconds'] / medians['annihilator']['process_wall_seconds'],
                python=sys.version, platform=platform.platform(), machine=platform.machine(), cpu=cpu,
                source_sha256=source_hashes, result=payload, result_sha256=EXPECTED,
                scope='Complete unchanged h=10/h=12 benchmark, fresh processes and application caches; OS caches not flushed; no timing threshold.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pairs', type=int, default=7)
    parser.add_argument('--cpu', type=int)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.pairs < 1 or args.output.exists():
        raise SystemExit('Require positive pairs and a fresh output path')
    record = benchmark(args.pairs, args.cpu)
    with args.output.open('x') as stream:
        stream.write(json.dumps(record, indent=2) + '\n')
    print(json.dumps({key: record[key] for key in ('status', 'pairs', 'medians', 'process_wall_ratio', 'result_sha256')}, indent=2))
