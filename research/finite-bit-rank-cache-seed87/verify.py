#!/usr/bin/env python3
"""Complete differential replay and bounded same-input performance experiment.

Sagar Thakrar, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import random
import statistics
import subprocess
import sys
import time
import unittest

from adapter import ROOT, SOURCE, checked_source, load_checker

PACKAGE = Path(__file__).resolve().parent
TESTS = ('finite_bit_contract', 'fano_completion', 'rank_product_core',
         'block_core', 'shared_core', 'subset_core_family', 'positive_side_core')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def fixtures(checker):
    from audit_joint_frames import add, eye, matrix
    from audit_rank_product_core import controls
    from experiments.block_core import check_block_pair, compile_block
    from experiments.fano_completion import cases
    from experiments.rank_product_core import compile_core
    from audit_cyclic_topology import cyclic_seed

    groups = {'fano': [], 'rank_product': [], 'block_core': [], 'rational': []}
    for name, program in cases():
        groups['fano'].append((name, checker.zero_frame_candidate(program['W'], program['gates'])))
    for name, rows, vectors, form in controls():
        groups['rank_product'].append((name, compile_core(rows, vectors, form)[0]))
    for matching in (None, [1, 0]):
        candidate, _ = compile_block(check_block_pair([3, 3], eye(4), 2), matching)
        groups['block_core'].append((str(matching), candidate))
    rng = random.Random(87)
    for m in (2, 3, 4, 8):
        for count in (1, 3, 17):
            candidate = checker.zero_frame_candidate(4, cyclic_seed(4, star=True), m)
            bank = [matrix([[Q(rng.randrange(-3, 4), rng.randrange(1, 6))
                             for _ in range(m)] for _ in range(m)]) for _ in range(count)]
            candidate['source_frames'] = [bank[i % count] for i in range(4)]
            for w, out in enumerate(candidate['rho']):
                candidate['sink_frames'][out] = add(candidate['source_frames'][w], eye(m))
            for index, gate in enumerate(candidate['gates']):
                gate['frame'] = bank[index % count]
            groups['rational'].append((f'm{m}-bank{count}', candidate))
    return groups


def negative_controls(checker):
    from audit_cyclic_topology import swap_word
    from audit_joint_frames import eye
    candidate = checker.zero_frame_candidate(3, swap_word(0, 1))
    initial = checker.inspect_candidate(candidate, False)
    candidate['gates'][1]['frame'] = eye(2)
    changed = checker.inspect_candidate(candidate, False)
    require(changed['edge_ranks'] != initial['edge_ranks'], 'stale between-call frame cache')
    candidate['gates'][1]['frame'] = ((0, 0), (0, 0))
    require(checker.inspect_candidate(candidate, False) == initial, 'cache survives restoration')
    controls = []
    mutations = (
        ('endpoint', lambda c: c['sink_frames'].__setitem__(2, ((0, 0), (0, 0)))),
        ('permutation', lambda c: c['rho'].__setitem__(0, 0)),
        ('scalar', lambda c: c['gates'][0]['xors'].clear()),
        ('float', lambda c: c['gates'][0].__setitem__('frame', ((0.0, 0), (0, 0)))),
        ('dimension', lambda c: c['gates'][0].__setitem__('frame', ((0,),))),
        ('gate port', lambda c: c['gates'][0].__setitem__('roles', [0, 0])),
        ('missing terminal', lambda c: c['source_frames'].pop()),
        ('zero denominator', lambda c: c['gates'][0].__setitem__('frame', (('1/0', 0), (0, 0)))),
    )
    for name, mutate in mutations:
        bad = deepcopy(candidate)
        mutate(bad)
        try:
            checker.inspect_candidate(bad, False)
        except (ValueError, ZeroDivisionError) as error:
            controls.append([name, type(error).__name__, str(error)])
        else:
            raise ValueError('accepted corruption: ' + name)
    try:
        checker.inspect_candidate(candidate)
    except ValueError as error:
        controls.append(['strict deficit', type(error).__name__, str(error)])
    else:
        raise ValueError('accepted equality control as strict deficit')
    for suffix in (b'\n', b' # changed source'):
        try:
            checked_source(SOURCE.read_bytes() + suffix, True)
        except ValueError:
            controls.append(['source pin', 'ValueError', 'source drift rejected'])
        else:
            raise ValueError('accepted source drift')
    return {'rejections': controls, 'mutation_before': initial, 'mutation_after': changed}


def worker(engine, tests=False):
    require(sys.flags.optimize == 0, 'worker requires enabled Python assertions')
    checker = load_checker(engine == 'cached')
    # Install before importing callers so their normal imports use this engine.
    sys.modules['finite_bit_contract'] = checker
    if tests:
        suite = unittest.TestSuite()
        for name in TESTS:
            suite.addTests(unittest.defaultTestLoader.discover(str(ROOT / 'tests'),
                                                              pattern='test_' + name + '.py'))
        result = unittest.TextTestRunner(verbosity=1).run(suite)
        require(result.wasSuccessful(), 'existing tests failed')
        return {'tests_run': result.testsRun}
    groups = fixtures(checker)
    receipts, seconds, rank_calls = {}, {}, {}
    original_rank = checker.rank
    for group, candidates in groups.items():
        original_rank.cache_clear()
        started = time.perf_counter()
        receipts[group] = [[name, checker.inspect_candidate(c, False)] for name, c in candidates]
        seconds[group] = time.perf_counter() - started
        info = original_rank.cache_info()
        rank_calls[group] = {'calls': info.hits + info.misses, 'eliminations': info.misses}
    from audit_fano_completion import certificate
    original_rank.cache_clear()
    started = time.perf_counter()
    receipts['complete_fano_audit'] = certificate()
    seconds['complete_fano_audit'] = time.perf_counter() - started
    receipts['controls'] = negative_controls(checker)
    return {'receipts': receipts, 'seconds': seconds, 'rank_calls': rank_calls}


def child(engine, tests=False):
    argv = [sys.executable, '-B', str(Path(__file__).resolve()), '--worker', engine]
    if tests:
        argv.append('--tests')
    environment = dict(os.environ, PYTHONHASHSEED='0', PYTHONOPTIMIZE='0')
    process = subprocess.run(argv, cwd=ROOT, env=environment, text=True,
                             capture_output=True, timeout=300)
    require(process.returncode == 0, process.stderr or process.stdout)
    return json.loads(process.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', choices=('reference', 'cached'))
    parser.add_argument('--tests', action='store_true')
    parser.add_argument('--pairs', type=int, default=1)
    args = parser.parse_args()
    if args.worker:
        print(json.dumps(worker(args.worker, args.tests), sort_keys=True))
        return
    require(1 <= args.pairs <= 9, 'use one to nine fresh-process pairs')
    sources = json.loads((PACKAGE / 'SOURCES.json').read_text())
    for row in sources['files']:
        if row['usage'] == 'input':
            require(sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                    'source drift: ' + row['path'])
    pairs, expected = [], None
    for index in range(args.pairs):
        order = ('reference', 'cached') if index % 2 == 0 else ('cached', 'reference')
        pair = {engine: child(engine) for engine in order}
        require(pair['reference']['receipts'] == pair['cached']['receipts'], 'full receipt mismatch')
        digest = sha256(canonical(pair['reference']['receipts'])).hexdigest()
        if expected is None:
            expected = digest
        require(expected == digest, 'receipt changed between runs')
        pairs.append({'order': order, **{engine: {k: v for k, v in pair[engine].items()
                                                if k != 'receipts'} for engine in order}})
    tests = {engine: child(engine, True) for engine in ('reference', 'cached')}
    require(tests['reference'] == tests['cached'], 'test coverage mismatch')
    ratios = {}
    for group in pairs[0]['reference']['seconds']:
        old = statistics.median(p['reference']['seconds'][group] for p in pairs)
        new = statistics.median(p['cached']['seconds'][group] for p in pairs)
        ratios[group] = {'reference_median_seconds': old, 'cached_median_seconds': new,
                         'speedup': old / new}
    print(json.dumps({'status': 'PASS_FINITE_BIT_TRANSITION_CACHE', 'assignment_seed': 87,
                      'python': sys.version, 'platform': platform.platform(),
                      'receipt_sha256': expected, 'tests': tests, 'measurements': pairs,
                      'medians': ratios, 'scope': 'Exact verifier tooling; no new kappa.'},
                     indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
