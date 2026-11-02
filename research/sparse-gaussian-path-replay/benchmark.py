"""Five alternating fresh-process complete-command measurements. Apache-2.0."""

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from adapter import authenticate, require


def timed(script):
    environment = os.environ.copy()
    environment.pop('PYTHONOPTIMIZE', None)
    with tempfile.TemporaryDirectory(prefix='sparse-benchmark-pyc-') as cache:
        command = [sys.executable, '-I', '-S', '-W', 'error', '-B', '-X',
                   'pycache_prefix='+cache, str(script)]
        start = time.perf_counter_ns()
        result = subprocess.run(command, env=environment, capture_output=True,
                                timeout=30, check=False)
        elapsed = time.perf_counter_ns()-start
    require(result.returncode == 0 and not result.stderr,
            'Benchmark command failed: '+result.stderr.decode(errors='replace')[-1500:])
    return elapsed, result.stdout


def source_hashes():
    root = HERE.parents[1]
    sources = json.loads((HERE/'SOURCES.json').read_text())
    paths = [root/row['path'] for row in sources['files'] if row['usage'] == 'input']
    paths += [HERE/name for name in ('adapter.py', 'sparse_product.py', 'benchmark.py',
                                    'SOURCES.json')]
    require(len(paths) == 21, 'Benchmark source inventory bound')
    return {str(path.relative_to(root)): sha256(path.read_bytes()).hexdigest()
            for path in paths}


def measure():
    source = authenticate()
    samples = {'reference': [], 'sparse': []}
    order, expected = [], None
    load_before = os.getloadavg()
    for pair in range(5):
        for name, script in (('reference', source/'verify.py'),
                             ('sparse', HERE/'adapter.py')):
            elapsed, output = timed(script)
            if expected is None:
                expected = output
            require(output == expected, 'Benchmark complete-output mismatch')
            samples[name].append(elapsed)
            order.append([pair, name])
    summaries = {name: {'median_ns': statistics.median(values),
                        'min_ns': min(values), 'max_ns': max(values)}
                 for name, values in samples.items()}
    return {'schema': 'complete-sparse-gaussian-benchmark/v1', 'errors': 0,
            'python': sys.version, 'platform': platform.platform(),
            'cpu_count': os.cpu_count(), 'load_before': load_before,
            'load_after': os.getloadavg(), 'samples_ns': samples, 'order': order,
            'summary': summaries, 'stdout_sha256': sha256(expected).hexdigest(),
            'source_sha256': source_hashes()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    target = args.output.expanduser().resolve()
    require(not target.is_relative_to(HERE.parents[1]), 'Write measurements outside checkout')
    require(not target.exists(), 'Refuse to overwrite an existing measurement')
    report = measure()
    with target.open('x') as handle:
        handle.write(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'measurement': str(target), 'summary': report['summary'],
                      'errors': report['errors']}, sort_keys=True))


if __name__ == '__main__':
    main()
