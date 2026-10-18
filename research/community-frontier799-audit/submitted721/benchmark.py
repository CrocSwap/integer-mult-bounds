#!/usr/bin/env python3
"""Compare the entire offline verifier, in fresh processes on the same checkout.

Unix resource metrics; no third-party dependencies. Output is evidence, not a
portable performance threshold. Requires the recorded base Git object locally.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BASE = '66849e1475c930fd7732b1a0067ffee7e1e95f60'
SOURCE = 'scripts/verify_pr_reconciliation.py'
WORKER = r'''
import contextlib, hashlib, io, json, resource, sys, time
source = sys.stdin.read()
if int(sys.argv[1]):
    limit = int(sys.argv[1]) * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
output = io.StringIO()
start = time.perf_counter()
with contextlib.redirect_stdout(output):
    exec(compile(source, '<reconciliation-benchmark>', 'exec'),
         {'__name__': '__main__', '__file__': 'scripts/verify_pr_reconciliation.py'})
seconds = time.perf_counter() - start
rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
print(json.dumps({'seconds': seconds,
                  'peak_rss_bytes': rss * (1 if sys.platform == 'darwin' else 1024),
                  'stdout_sha256': hashlib.sha256(output.getvalue().encode()).hexdigest()}))
'''


def run(source, limit=0):
    result = subprocess.run([sys.executable, '-B', '-c', WORKER, str(limit)],
                            cwd=ROOT, input=source, text=True, capture_output=True)
    if result.returncode:
        return {'returncode': result.returncode, 'stderr': result.stderr}
    return dict(returncode=0, **json.loads(result.stdout))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rounds', type=int, default=5)
    parser.add_argument('--memory-limit-mib', type=int, default=0,
                        help='also try each verifier once under this RLIMIT_AS')
    args = parser.parse_args()
    if args.rounds < 1 or args.memory_limit_mib < 0:
        parser.error('rounds must be positive and memory limit nonnegative')
    sources = {
        'before': subprocess.check_output(['git', 'show', f'{BASE}:{SOURCE}'],
                                          cwd=ROOT, text=True),
        'after': (ROOT / SOURCE).read_text(),
    }
    samples = {name: [] for name in sources}
    for i in range(args.rounds):
        # Alternate order to reduce systematic warm-cache/order bias.
        for name in (['before', 'after'] if i % 2 == 0 else ['after', 'before']):
            result = run(sources[name])
            if result['returncode']:
                raise RuntimeError(f'{name} failed: {result}')
            samples[name].append(result)
    hashes = {row['stdout_sha256'] for rows in samples.values() for row in rows}
    if len(hashes) != 1:
        raise RuntimeError('Before/after verifier output differs')
    package = ROOT / 'research/coordinated-frames-and-entrance-banks'
    manifest_bytes = (package / 'BASELINE.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    report = {
        'base_commit': BASE, 'python': sys.version, 'platform': platform.platform(),
        'source_sha256': {k: hashlib.sha256(v.encode()).hexdigest() for k, v in sources.items()},
        'manifest_sha256': hashlib.sha256(manifest_bytes).hexdigest(),
        'archive_sha256': manifest['archive_sha256'], 'files': manifest['files'],
        'rounds': args.rounds, 'order': 'alternating before/after, then after/before',
        'coverage': 'entire offline verifier; identical stdout in every successful run',
        'samples': samples,
        'medians': {name: {metric: statistics.median(r[metric] for r in rows)
                           for metric in ['seconds', 'peak_rss_bytes']}
                    for name, rows in samples.items()},
    }
    if args.memory_limit_mib:
        report['memory_limit_mib'] = args.memory_limit_mib
        report['limited_runs'] = {name: run(source, args.memory_limit_mib)
                                  for name, source in sources.items()}
        for result in report['limited_runs'].values():
            if not result['returncode'] and result['stdout_sha256'] not in hashes:
                raise RuntimeError('Memory-limited verifier output differs')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
