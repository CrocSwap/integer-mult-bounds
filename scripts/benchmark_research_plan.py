#!/usr/bin/env python3
"""Compare complete replay plans on the same stable checkout.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import runpy
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--baseline', required=True, help='Git commit with the previous planner')
    parser.add_argument('--samples', type=int, default=3)
    args = parser.parse_args()
    if args.samples < 1:
        parser.error('--samples must be positive')
    source = ROOT / 'scripts/research_package.py'
    current = runpy.run_path(str(source))
    git = current['git']
    baseline = git(ROOT, 'rev-parse', '--verify', args.baseline + '^{commit}').decode().strip()
    raw = git(ROOT, 'show', baseline + ':scripts/research_package.py')
    previous = {'__file__': str(source), '__name__': 'baseline_planner'}
    exec(compile(raw, str(source), 'exec'), previous)
    names = git(ROOT, 'ls-files', '-z').decode().split('\0')
    cases = {
        'all-tracked': names,
        'shared-control': ['scripts/research_package.py'],
        'package-file': ['research/joint-helper-lattice/RESULT.json'],
        'unrelated': ['README.md'],
    }
    report = {
        'baseline': baseline,
        'head': git(ROOT, 'rev-parse', 'HEAD').decode().strip(),
        'python': sys.version,
        'platform': platform.platform(),
        'source_sha256': {
            'before': hashlib.sha256(raw).hexdigest(),
            'after': hashlib.sha256(source.read_bytes()).hexdigest(),
        },
        'scope': 'Complete plan equality on one stable checkout; no verifier runs.',
        'cases': {},
    }
    for name, changed in cases.items():
        durations = {'before': [], 'after': []}
        expected = None
        for sample in range(args.samples):
            order = [('before', previous), ('after', current)]
            if sample % 2:
                order.reverse()
            for label, module in order:
                start = time.perf_counter()
                result = module['plan_details'](ROOT, changed)
                durations[label].append(time.perf_counter() - start)
                if expected is None:
                    expected = result
                elif result != expected:
                    raise ValueError('plan or explanation changed: ' + name)
        encoded = json.dumps(expected, sort_keys=True, separators=(',', ':')).encode()
        report['cases'][name] = {
            'changed_paths': len(set(changed) - {''}),
            'selected_packages': len(expected),
            'complete_plan_sha256': hashlib.sha256(encoded).hexdigest(),
            'seconds': durations,
            'median_ratio': statistics.median(durations['before']) / statistics.median(durations['after']),
        }
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
