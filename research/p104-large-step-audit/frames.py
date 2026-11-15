#!/usr/bin/env python3
"""Optimistic contact-corridor bounds; no new supplier or kappa is certified.

Hao Yan, with substantial OpenAI Codex assistance. Apache-2.0.
See PROOF.md for the relaxation and the precise applicability conditions.
"""
from collections import Counter
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import runpy

if not __debug__:
    raise RuntimeError('Assertions are proof checks; run without -O.')
HERE = Path(__file__).resolve().parent
SOURCE = 'df1fc415915abd8d0f1bbfe8ad530c02f9cd82692f548ed2817ba6bd948fc55c'
TARGETS = ('.0046502223357', '.0046530568657')


def span(vectors):
    result = {0}
    for v in vectors:
        result |= {x ^ v for x in result}
    return frozenset(result)


def dimension(space):
    d = len(space).bit_length() - 1
    assert len(space) == 1 << d
    return d


def join(a, b):
    if a <= b:
        return b
    result = set(a)
    for v in b:
        if v not in result:
            result |= {x ^ v for x in result}
    return frozenset(result)


def corridors(word, free_helpers):
    n = word['public']
    mains = (set(word['live']) | {r + 112 for r in word['live']}
             | set(word['hosted']['X2']) | set(word['hosted']['Y2']))
    helpers = set(range(n)) - mains
    assert len(mains) == 400 and len(helpers) == 1101
    frames = [span(v) for v in word['frames']]
    assert all(dimension(s) == len(v) for s, v in zip(frames, word['frames']))
    fixed = mains if free_helpers else set(range(n))
    ops = [e for e in word['program'] if e[0] != 'MOVE']
    lower = [None] * len(ops)
    upper = lower.copy()
    cur = [frames[f] if r in fixed else frozenset({0})
           for r, f in enumerate(word['initial'])] + [None] * word['owned_fields']
    j = 0
    for e in word['program']:
        op, d = e[:2]
        if op == 'MOVE':
            if d >= n:
                assert cur[d] == frames[e[2]]
                cur[d] = frames[e[3]]
            continue
        if op in ('ADD', 'COPY'):
            s = e[2]
            z = frames[e[4]] if d >= n or s >= n else join(cur[d], cur[s])
            assert cur[d] <= z and cur[s] <= z and z <= frames[e[4]]
            cur[d] = cur[s] = lower[j] = z
        elif op == 'SCALE':
            lower[j] = cur[d]
        elif op == 'INIT':
            assert cur[d] is None
            cur[d] = frames[e[2]]
        elif op == 'CLEAR':
            assert cur[d] == frames[e[2]]
            cur[d] = None
        else:
            raise ValueError(op)
        j += 1
    cur = [frames[f] if r in fixed else frozenset(range(512))
           for r, f in enumerate(word['final'])] + [None] * word['owned_fields']
    j = len(ops) - 1
    for e in reversed(word['program']):
        op, d = e[:2]
        if op == 'MOVE':
            if d >= n:
                assert cur[d] == frames[e[3]]
                cur[d] = frames[e[2]]
            continue
        if op in ('ADD', 'COPY'):
            s = e[2]
            z = frames[e[4]] if d >= n or s >= n else cur[d] & cur[s]
            assert frames[e[4]] <= z and z <= cur[d] and z <= cur[s]
            cur[d] = cur[s] = upper[j] = z
        elif op == 'SCALE':
            upper[j] = cur[d]
        elif op == 'CLEAR':
            assert cur[d] is None
            cur[d] = frames[e[2]]
        elif op == 'INIT':
            assert cur[d] == frames[e[2]]
            cur[d] = None
        j -= 1
    paths = [[(len(word['frames'][f]),) * 2] if r in fixed else [(0, 9)]
             for r, f in enumerate(word['initial'])]
    widths = Counter()
    for j, e in enumerate(ops):
        if e[0] not in ('ADD', 'COPY', 'SCALE'):
            continue
        assert lower[j] <= upper[j]
        a, b = dimension(lower[j]), dimension(upper[j])
        widths[b - a] += 1
        for r in e[1:3] if e[0] in ('ADD', 'COPY') else e[1:2]:
            if r < n:
                paths[r].append((a, b))
    for r, f in enumerate(word['final']):
        paths[r].append((len(word['frames'][f]),) * 2 if r in fixed else (0, 9))
    return paths, widths, helpers


def minimum_net_cost(path, powers, productive):
    """Enclose min_path(sum H(gaps) - H(end-start) if productive)."""
    a, b = path[0]
    dp = {(d, d): (0, 0) for d in range(a, b + 1)}
    transitions = 0
    for a, b in path[1:]:
        new = {}
        for (start, previous), (x, y) in dp.items():
            for d in range(max(a, previous), b + 1):
                value = x + powers[d - previous][0], y + powers[d - previous][1]
                key = start, d
                transitions += 1
                if key not in new:
                    new[key] = value
                else:
                    new[key] = min(new[key][0], value[0]), min(new[key][1], value[1])
        dp = new
    values = []
    for (start, d), (x, y) in dp.items():
        if productive:
            x -= powers[d - start][1]
            y -= powers[d - start][0]
        values.append((x, y))
    return ((min(x for x, _ in values), min(y for _, y in values))
            if values else None), transitions


def controls():
    # Exact integer prices: compare both ordinary and coupled endpoint-credit DP
    # with exhaustive enumeration, including an infeasible forced descent.
    prices = {r: (r * 20 - r * r, r * 20 - r * r) for r in range(10)}
    fixtures = [[(0, 0), (0, 2), (1, 3), (3, 3)],
                [(0, 2), (1, 3), (2, 4)], [(2, 2), (1, 1)]]
    for path in fixtures:
        for productive in (False, True):
            values = []
            for ds in product(*(range(a, b + 1) for a, b in path)):
                if any(a > b for a, b in zip(ds, ds[1:])):
                    continue
                cost = sum(prices[b - a][0] for a, b in zip(ds, ds[1:]))
                values.append(cost - (prices[ds[-1] - ds[0]][0] if productive else 0))
            expected = (min(values),) * 2 if values else None
            assert minimum_net_cost(path, prices, productive)[0] == expected
    return {'ordinary_and_coupled_dp_equal_exhaustive': True,
            'forced_descent_rejected': True}


def audit():
    word = json.loads(gzip.decompress((HERE / 'retained/7613/word.json.gz').read_bytes()))
    canonical = hashlib.sha256(json.dumps(word, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    assert canonical == SOURCE
    invoice = json.loads((HERE / 'retained/7613/invoice-new.json').read_text())
    paid = {int(r): v for r, v in invoice['paid'].items()}
    targets = {int(r): v for r, v in invoice['targets'].items()}
    old_public = Counter()
    for e in word['program']:
        if e[0] == 'MOVE' and not e[4]:
            a, b = (span(word['frames'][f]) for f in e[2:4])
            assert a <= b
            old_public[dimension(b) - dimension(a)] += 1
    fixed_paid = {r: paid.get(r, 0) - 17 * old_public[r] for r in paid.keys() | old_public.keys()}
    assert min(fixed_paid.values()) >= 0
    engine = runpy.run_path(str(HERE / 'retained/interval_gate.py'))
    B = engine['B']
    cases = []
    for free in (False, True):
        paths, widths, helpers = corridors(word, free)
        old_helper = Counter(len(word['frames'][word['final'][r]])
                             - len(word['frames'][word['initial'][r]]) for r in helpers)
        remaining = {r: targets.get(r, 0) - (17 * old_helper[r] if free else 0)
                     for r in targets.keys() | old_helper.keys()}
        assert min(remaining.values()) >= 0
        for target in TARGETS:
            C = Q(target)
            powers = {r: engine['power'](r, C) for r in range(1, 10)}
            powers[0] = (0, 0)
            lo = hi = transitions = 0
            for r, path in enumerate(paths):
                value, count = minimum_net_cost(path, powers, free and r in helpers)
                assert value is not None
                lo += value[0]
                hi += value[1]
                transitions += count
            t = engine['moment']({r: v for r, v in remaining.items() if v}, C)
            p = engine['moment']({r: v for r, v in fixed_paid.items() if v}, C)
            margin = t[0] - p[1] - 17 * hi, t[1] - p[0] - 17 * lo
            assert margin[1] < 0
            baseline = engine['moment'](old_public, C)
            old_credit = engine['moment'](old_helper, C) if free else (0, 0)
            assert lo <= baseline[1] - old_credit[0]
            cases.append(dict(mode='free_helper_endpoints' if free else 'fixed_endpoints',
                              target=target, public_fields=word['public'],
                              contact_dimension_width_counts=dict(sorted(widths.items())),
                              dp_transitions=transitions,
                              native_net_cost_interval=[str(Q(x, B)) for x in (lo, hi)],
                              full_target_minus_paid_interval=[str(Q(x, B)) for x in margin],
                              approximate_margin=[float(Q(x, B)) for x in margin],
                              target_fails_relaxed_moment=True))
    return dict(status='PASS_SCOPED_CONTACT_FRAME_BOUNDS_NO_KAPPA_GAIN',
                source_canonical_sha256=canonical, cases=cases, controls=controls())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true', help='Regenerate deterministic receipt')
    args = parser.parse_args()
    result = audit()
    output = HERE / 'frames.json'
    if args.write:
        output.write_text(json.dumps(result, indent=2) + '\n')
    else:
        assert json.loads(output.read_text()) == json.loads(json.dumps(result))
    print(result['status'])
    for case in result['cases']:
        print(case['mode'], case['target'], case['approximate_margin'])
