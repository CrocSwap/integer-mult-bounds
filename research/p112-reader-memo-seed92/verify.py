#!/usr/bin/env python3
"""Opt-in exact reader-form memoization for Mihir Srivastava's PR845 replay.

Charan (@theon199), with substantial OpenAI Codex assistance. Apache-2.0.
The frozen predecessor is imported unchanged only after live source admission.
"""

import argparse
from functools import lru_cache
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
ROOT = HERE.parents[1]
SUBJECT = 'research/p112-single-lift'
LIVE_INPUTS = {
    SUBJECT + '/' + name for name in (
        'verify.py', 'geometry.py', 'RESULTS.json', 'SOURCES.json',
        'reference-geometry.json', 'reference/pr717_e8model.py',
        'reference/PR717-NOTICE.md', 'independent_check.py',
    )
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def encoded(value):
    """Type-sensitive equality for every field, including booleans and numbers."""
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      allow_nan=False).encode('utf-8')


def no_duplicates(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, 'duplicate JSON key: ' + key)
        out[key] = value
    return out


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'),
                      object_pairs_hook=no_duplicates)


def source_admission(root, manifest=None):
    manifest = read_json(HERE / 'SOURCES.json') if manifest is None else manifest
    inputs = [p for p in manifest['files'] if p['usage'] == 'input']
    require(len(inputs) == len(LIVE_INPUTS)
            and {p['path'] for p in inputs} == LIVE_INPUTS,
            'complete live input inventory')
    root = root.resolve()
    for pin in inputs:
        path = (root / pin['path']).resolve()
        require(path.is_relative_to(root) and path.is_file(),
                'missing or escaped source: ' + pin['path'])
        require(hashlib.sha256(path.read_bytes()).hexdigest() == pin['sha256'],
                'source drift: ' + pin['path'])
    return inputs


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def subject(root):
    source_admission(root)
    directory = root / SUBJECT
    # The original verifier uses `from geometry import ...`. Bind that import
    # to its admitted file even under -I or in a relocated checkout.
    load_module('geometry', directory / 'geometry.py')
    return load_module('pr845_reader_memo_subject', directory / 'verify.py')


class ConstraintMemo:
    """Compile exact reader values once, then build every original constraint.

    Snapshot all ordered bases and labels on each call. The fixed-size built-in
    integer envelope avoids bool/float cache aliases and bounds each table to
    896 integers; other inputs use the original constraint builder. Coefficients
    and X are never cached. Mutating either immediately changes the generated
    rows. A four-table LRU bound limits storage without dropping any constraint.
    """

    def __init__(self, original, evaluate, maxsize=4):
        require(type(maxsize) is int and maxsize > 0, 'positive integer cache bound')
        self.original = original

        @lru_cache(maxsize=maxsize)
        def prepare(spaces, labels):
            return tuple(tuple(evaluate(space, label) for space in spaces)
                         for label in labels)

        self.cached = prepare

    def __call__(self, coefficients, data, spaces):
        # Do not consume generators or custom containers that the original
        # builder may read lazily. Optimize the admitted JSON/list domain only.
        if (type(spaces) not in (list, tuple)
                or any(type(space) not in (list, tuple) for space in spaces)
                or type(data['labels']) not in (list, tuple)
                or type(coefficients) not in (list, tuple)):
            return self.original(coefficients, data, spaces)
        bases = tuple(tuple(space) for space in spaces)
        labels = tuple(data['labels'])
        if (len(bases) != 8 or any(len(basis) != 8 for basis in bases)
                or len(labels) != 112 or len(coefficients) != 8
                or any(type(q) is not int for basis in bases for q in basis)
                or any(type(label) is not int for label in labels)):
            return self.original(coefficients, data, spaces)
        values_by_port = self.cached(bases, labels)
        active = [j for j, value in enumerate(coefficients) if value]
        rows = []
        for values, evaluations in zip(data['X'], values_by_port):
            for sign in (-1, 1):
                row = 0
                for block, j in enumerate(active):
                    if values[j] * coefficients[j] == sign:
                        row |= evaluations[j] << (8 * block)
                rows.append(row)
        return rows


def compare(actual, expected, context):
    require(encoded(actual) == encoded(expected), 'complete certificate mismatch: ' + context)


def controls(root):
    """Exercise cache invalidation and fault detection outside the timed runs."""
    module = subject(root)
    data = module.build()
    spaces = [module.reader_space([r[j] for r in data['X']], data['duals'])
              for j in range(8)]
    original = module.constraint_rows
    memo = ConstraintMemo(original, module.evaluate)
    signs = (1,) * 8
    baseline = original(signs, data, spaces)
    require(memo(signs, data, spaces) == baseline, 'initial compiled rows')
    passed = []

    def changed_rows(name, changed_data, changed_spaces, changed_signs=signs):
        expected = original(changed_signs, changed_data, changed_spaces)
        require(expected != baseline, 'ineffective control: ' + name)
        require(memo(changed_signs, changed_data, changed_spaces) == expected,
                'stale compiled table: ' + name)
        require(memo(signs, data, spaces) == baseline, 'restore after ' + name)
        passed.append(name)

    changed_spaces = [list(space) for space in spaces]
    changed_spaces[0].reverse()
    changed_rows('ordered basis permutation', data, changed_spaces)
    # Mutate the SAME list objects after warming them, then restore them.
    memo(signs, data, changed_spaces)
    changed_spaces[0][0] ^= 1
    changed_rows('in-place basis mutation', data, changed_spaces)
    changed_data = {**data, 'labels': list(data['labels'])}
    changed_data['labels'][0] ^= 1
    changed_rows('in-place label mutation', changed_data, spaces)
    changed_data = {**data, 'X': [list(row) for row in data['X']]}
    column = next(j for j, value in enumerate(changed_data['X'][0]) if value)
    changed_data['X'][0][column] = 0
    changed_rows('uncached X coordinate mutation', changed_data, spaces)
    changed_rows('uncached coefficient mutation', data, spaces, (-1,) + signs[1:])

    def must_fail(name, operation, error=ValueError):
        try:
            operation()
        except error:
            passed.append(name)
        else:
            raise ValueError('accepted fault: ' + name)

    changed_spaces = [list(space) for space in spaces]
    changed_spaces[0][0] = float(changed_spaces[0][0])
    must_fail('integer-equal float basis still rejects',
              lambda: memo(signs, data, changed_spaces), TypeError)
    changed_data = {**data, 'labels': list(data['labels'])}
    changed_data['labels'][0] = float(changed_data['labels'][0])
    must_fail('integer-equal float label still rejects',
              lambda: memo(signs, changed_data, spaces), TypeError)

    # Table eviction affects only recomputation. Use the real source builder.
    small = ConstraintMemo(original, module.evaluate, maxsize=1)
    small(signs, data, spaces)
    alternate = [list(reversed(space)) for space in spaces]
    require(small(signs, data, alternate) == original(signs, data, alternate),
            'evicted alternate input')
    require(small(signs, data, spaces) == baseline
            and small.cached.cache_info().misses == 3, 'exact eviction/recomputation')
    passed.append('bounded eviction and recomputation')

    # These faults can preserve ranks. The complete row-stream digest detects
    # them rather than accepting a rank-only or histogram-only comparison.
    correct = module.case_certificate(signs, data, spaces)
    for name, corrupt in (
        ('omitted constraint row', lambda rows: rows[1:]),
        ('exchanged sign-row order', lambda rows: [r for i in range(0, len(rows), 2)
                                                for r in (rows[i+1], rows[i])]),
    ):
        module.constraint_rows = lambda c, d, s, f=corrupt: f(original(c, d, s))
        must_fail(name, lambda: compare(module.case_certificate(signs, data, spaces),
                                       correct, name))
    module.constraint_rows = lambda c, d, s: [0] * len(original(c, d, s))
    must_fail('erased reader values', lambda: module.case_certificate(signs, data, spaces))
    module.constraint_rows = original
    false = {**correct, 'rank': 63.0}
    must_fail('type-sensitive rank receipt', lambda: compare(false, correct, 'rank type'))
    manifest = read_json(HERE / 'SOURCES.json')
    incomplete = {**manifest, 'files': [p for p in manifest['files']
                                      if p['path'] != SUBJECT + '/geometry.py']}
    must_fail('omitted live source pin', lambda: source_admission(root, incomplete))
    return passed


def worker(root, engine, output):
    module = subject(root)
    memo = None
    if engine == 'memo':
        memo = ConstraintMemo(module.constraint_rows, module.evaluate)
        module.constraint_rows = memo
    started = time.perf_counter()
    result = module.run()
    seconds = time.perf_counter() - started
    expected = read_json(root / SUBJECT / 'RESULTS.json')
    compare(result, expected, engine)
    stats = memo.cached.cache_info()._asdict() if memo is not None else None
    payload = {'engine': engine, 'run_seconds': seconds, 'cache': stats,
               'certificate_sha256': hashlib.sha256(encoded(result)).hexdigest(),
               'certificate': result}
    # Never truncate an existing output, including when a caller repeats a run.
    with output.open('x', encoding='utf-8') as stream:
        json.dump(payload, stream, sort_keys=True)
        stream.write('\n')
    print('PASS_P112_READER_MEMO_ENGINE engine=' + engine)


def run_worker(root, engine, output, optimized=False):
    argv = [sys.executable, '-I', '-B']
    if optimized:
        argv.append('-O')
    argv += [str(HERE / 'verify.py'), '--engine', engine,
             '--root', str(root), '--output', str(output)]
    started = time.perf_counter()
    completed = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, timeout=120)
    elapsed = time.perf_counter() - started
    require(completed.returncode == 0,
            engine + ' worker failed: ' + completed.stdout + completed.stderr)
    payload = read_json(output)
    require(payload['engine'] == engine, 'worker engine binding')
    return payload, elapsed


def audit(root, pairs):
    require(type(pairs) is int and 1 <= pairs <= 9, 'pairs must be in 1..9')
    source_admission(root)
    expected = read_json(root / SUBJECT / 'RESULTS.json')
    certificate_digest = hashlib.sha256(encoded(expected)).hexdigest()
    passed_controls = controls(root)
    samples = []
    with tempfile.TemporaryDirectory(prefix='p112 reader memo ') as directory:
        work = Path(directory)
        for pair in range(pairs):
            order = ['reference', 'memo'] if pair % 2 == 0 else ['memo', 'reference']
            sample = {'order': order}
            for engine in order:
                payload, seconds = run_worker(root, engine, work / f'{pair}-{engine}.json')
                compare(payload['certificate'], expected, engine + ' full replay')
                sample[engine] = {'process_seconds': seconds,
                                  'run_seconds': payload['run_seconds'],
                                  'cache': payload['cache']}
                if engine == 'memo':
                    stats = payload['cache']
                    require(stats['hits'] > 0 and 0 < stats['currsize'] <= 4,
                            'memo path actually exercised with bounded storage')
            samples.append(sample)
    result = {'status': 'PASS_P112_READER_MEMO', 'certificate_sha256': certificate_digest,
              'support_certificates': len(expected['support_certificates']),
              'sign_cases': len(expected['cases']), 'conflicting_kernels': 128,
              'inherited_controls': len(expected['controls']['rejected']),
              'package_controls': passed_controls, 'pairs': samples,
              'environment': {'python': platform.python_version(),
                              'implementation': platform.python_implementation(),
                              'system': platform.system(), 'machine': platform.machine()}}
    for field in ('process_seconds', 'run_seconds'):
        baseline = statistics.median(s['reference'][field] for s in samples)
        candidate = statistics.median(s['memo'][field] for s in samples)
        result['median_' + field] = {'reference': baseline, 'memo': candidate,
                                    'ratio': baseline / candidate}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--pairs', type=int, default=1,
                        help='1..9 alternating fresh-process pairs; timings are not a pass gate')
    parser.add_argument('--report', type=Path, help='create a new timing report after all checks')
    parser.add_argument('--engine', choices=('compare', 'reference', 'memo'), default='compare',
                        help='compare both engines, or run one complete admitted replay')
    parser.add_argument('--output', type=Path, help='create a new full-certificate file for one engine')
    args = parser.parse_args()
    root = args.root.resolve()
    if args.engine != 'compare':
        require(args.output is not None and args.report is None,
                'single engine requires --output and excludes --report')
        worker(root, args.engine, args.output)
        return
    require(args.output is None, '--output requires a single engine')
    result = audit(root, args.pairs)
    if args.report is not None:
        with args.report.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, sort_keys=True, indent=2)
            stream.write('\n')
    print('PASS_P112_READER_MEMO supports=511 signs=3272 conflicting_kernels=128 '
          f'inherited_controls=9 controls={len(result["package_controls"])} '
          f'pairs={args.pairs} complete_certificate={result["certificate_sha256"]}')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        print('FAIL_P112_READER_MEMO: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
