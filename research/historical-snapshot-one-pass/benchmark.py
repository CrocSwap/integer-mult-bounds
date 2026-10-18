#!/usr/bin/env python3
"""Compare complete historical snapshot setup on one shared working fixture.

Apache-2.0. The baseline retains Dennis's historical-overlay implementation.
No mathematical checks or source authentication are cached or skipped.
"""
import argparse
import hashlib
import importlib.util
import json
import platform
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
BASE = 'bcdf338bf10ed70f1b3a0325fdd429677920d089'
SCRIPT = 'scripts/replay_historical_check.py'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True,
                          check=True, timeout=60).stdout


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, 'Cannot load ' + str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def baseline_module(directory):
    raw = git('show', BASE + ':' + SCRIPT)
    sources = json.loads((PACKAGE / 'SOURCES.json').read_bytes())
    pins = [row for row in sources['files'] if row['path'] == SCRIPT]
    require(len(pins) == 1 and sources['base_commit'] == BASE, 'Baseline provenance differs')
    require(hashlib.sha256(raw).hexdigest() == pins[0]['sha256'], 'Baseline source differs')
    path = directory / 'baseline.py'
    require(path.write_bytes(raw) == len(raw), 'Incomplete baseline write')
    return load_module('historical_snapshot_baseline', path)


def snapshot(module, paths, directory):
    target = directory / 'repo'
    start = time.perf_counter()
    expected = module.materialize(ROOT, target, module.CONFIG['skip-clones-tests'],
                                  paths, ROOT / 'scripts/historical-ci-inputs')
    seconds = time.perf_counter() - start
    # Re-read every destination outside the timed setup. This is the unchanged
    # post-replay gate, not a comparison of self-reported hash maps alone.
    module.verify_unchanged(target, expected)
    require(set(expected) == set(paths), 'Tracked-file coverage differs')
    return expected, seconds


def benchmark(pairs):
    paths = [name.decode('utf-8') for name in
             git('ls-tree', '-r', '--name-only', '-z', BASE).split(b'\0') if name]
    require(paths and len(paths) == len(set(paths)), 'Invalid baseline file inventory')
    largest = max((ROOT / name).stat().st_size for name in paths)
    sizes = sum((ROOT / name).stat().st_size for name in paths)
    candidate = load_module('historical_snapshot_candidate', ROOT / SCRIPT)
    rows, reference = [], None
    with tempfile.TemporaryDirectory(prefix='historical-copy-benchmark-') as td:
        baseline = baseline_module(Path(td))
        for pair in range(pairs):
            order = [('baseline', baseline), ('candidate', candidate)]
            if pair % 2:
                order.reverse()
            for label, module in order:
                with tempfile.TemporaryDirectory(prefix='historical-copy-run-') as output:
                    expected, seconds = snapshot(module, paths, Path(output))
                if reference is None:
                    reference = expected
                require(expected == reference, 'Snapshot bytes or coverage changed')
                rows.append({'pair': pair + 1, 'implementation': label, 'seconds': seconds})
                print(label, pair + 1, f'{seconds:.6f}s', flush=True)
    before = statistics.median(row['seconds'] for row in rows if row['implementation'] == 'baseline')
    after = statistics.median(row['seconds'] for row in rows if row['implementation'] == 'candidate')
    return {'status': 'PASS_IDENTICAL_HISTORICAL_SNAPSHOTS', 'base_commit': BASE,
                'python': sys.version, 'platform': platform.platform(), 'pairs': pairs,
                'files': len(paths), 'source_bytes': sizes, 'largest_source_bytes': largest,
                'snapshot_sha256': hashlib.sha256(json.dumps(reference, sort_keys=True).encode()).hexdigest(),
                'baseline_source_sha256': hashlib.sha256(git('show', BASE + ':' + SCRIPT)).hexdigest(),
                'candidate_source_sha256': hashlib.sha256((ROOT / SCRIPT).read_bytes()).hexdigest(),
                'runs': rows, 'baseline_median_seconds': before, 'candidate_median_seconds': after,
                'median_speedup': before / after,
                'scope': 'Setup only; same baseline path list and working bytes in both implementations. '
                      'Every copied destination rehashed after timing. No supplier replay or new kappa.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pairs', type=int, choices=range(1, 6), default=3)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    require(args.out is None or not args.out.exists(), 'Refusing to overwrite benchmark evidence')
    result = benchmark(args.pairs)
    text = json.dumps(result, indent=2) + '\n'
    if args.out is None:
        print(text, end='')
    else:
        with args.out.open('x', encoding='utf-8') as stream:
            require(stream.write(text) == len(text), 'Incomplete benchmark receipt')


if __name__ == '__main__':
    main()
