#!/usr/bin/env python3
"""Compare pinned Cartesian replay with pruning; timings are not thresholds."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import platform
from statistics import median
import subprocess
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[2]
BASE = '7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261'
SOURCE = 'scripts/experiments/signed_sparse_core.py'
SOURCE_HASH = '21da8e1de5ab6ac8479183326c2000313d24b47cc5be2f46b4fe6ac3cd59779f'
sys.path.insert(0, str(ROOT / 'scripts'))
import experiments.signed_sparse_core as core
from audit_signed_sparse import certificate
from prepare_layers import serializable


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def digest(value):
    return sha256(json.dumps(serializable(value), sort_keys=True,
                             separators=(',', ':')).encode()).hexdigest()


def compare_timed(before, after, repeats):
    samples = [[], []]
    reference = before()
    require(reference == after(), 'Before/after output mismatch')
    for turn in range(repeats):
        for index in ((0, 1) if turn % 2 == 0 else (1, 0)):
            start = perf_counter()
            value = (before, after)[index]()
            elapsed = perf_counter() - start
            require(value == reference, 'Repeated output mismatch')
            samples[index].append(elapsed)
    old, new = map(median, samples)
    return dict(payload_sha256=digest(reference), before_seconds=samples[0],
                after_seconds=samples[1], median_speedup=old/new)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--repeats', type=int, default=7)
    args = parser.parse_args()
    require(args.repeats > 0, 'Positive repeat count required')
    old_source = subprocess.check_output(['git', 'show', f'{BASE}:{SOURCE}'], cwd=ROOT)
    require(sha256(old_source).hexdigest() == SOURCE_HASH, 'Baseline source pin mismatch')
    namespace = {'__name__': 'signed_sparse_baseline'}
    exec(compile(old_source, f'{BASE}:{SOURCE}', 'exec'), namespace)
    old = namespace['coefficient_terms']
    new = core.coefficient_terms
    rows = []
    for q in (2, 4, 8):
        for h in range(q, 9):
            row = dict(h=h, q=q, terms=len(list(new(h, q))))
            row.update(compare_timed(lambda: list(old(h, q)),
                                     lambda: list(new(h, q)), args.repeats))
            rows.append(row)

    def audit(enumerator):
        core.coefficient_terms = enumerator
        try:
            result = certificate()
            # This field describes source bytes, not a mathematical result.
            result.pop('source_sha256')
            return result
        finally:
            core.coefficient_terms = new

    full = compare_timed(lambda: audit(old), lambda: audit(new), args.repeats)
    committed = json.loads((ROOT / 'certificates/signed-sparse-core.json').read_text())
    committed.pop('source_sha256')
    require(digest(committed) == full['payload_sha256'], 'Committed certificate mismatch')
    subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests',
                    '-p', 'test_signed_sparse*.py', '-v'], cwd=ROOT, check=True)
    result = dict(status='PASS', base=BASE, assignment_seed=92,
                  baseline_source_sha256=SOURCE_HASH,
                  optimized_source_sha256=sha256((ROOT / SOURCE).read_bytes()).hexdigest(),
                  python=sys.version, platform=platform.platform(), repeats=args.repeats,
                  enumeration=rows, full_audit=full,
                  scope='Identical ordered terms and complete historical certificate payload; no new kappa')
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print('PASS 13 ordered streams; full historical certificate unchanged; 10 regression tests')
    print(f"Full-audit median speedup: {full['median_speedup']:.3f}x")


if __name__ == '__main__':
    main()
