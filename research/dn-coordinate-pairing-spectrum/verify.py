#!/usr/bin/env python3
"""Exact finite tests of the all-n argument in README; no third-party code."""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from math import comb
from pathlib import Path
from random import Random

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def roots(n):
    result = []
    for i, j in combinations(range(n), 2):
        for sign in (1, -1):
            row = [0] * n
            row[i], row[j] = 2, 2 * sign
            result.append(tuple(row))
    return result


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def rank(rows):
    pivots = {}
    for value in rows:
        while value:
            bit = value.bit_length()-1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)


def span_rank(rows):
    """Independent exponential row-span cardinality, small blocks only."""
    span = {0}
    for row in rows:
        span |= {x ^ row for x in tuple(span)}
    return len(span).bit_length()-1


def supports(rs):
    return [sum(1 << i for i, r in enumerate(rs) if r[j])
            for j in range(len(rs[0]))]


def price(rows, masks, live, ranker=rank):
    return sum(ranker([row & block for i, row in enumerate(rows)
                       if block >> i & 1]) for support in masks
               if (block := support & live))


def admissible(rs, rows):
    size = len(rs)
    need(len(rows) == size, 'pairing shape')
    for i, row in enumerate(rows):
        need(type(row) is int and 0 <= row < 1 << size, 'pairing binary shape')
        need(row >> i & 1, 'pairing diagonal')
        for j, r in enumerate(rs):
            need(i == j or not (row >> j & 1) or dot(rs[i], r) == 0,
                 'pairing forced zero')


def geometry(rs):
    edges = [frozenset(i for i, x in enumerate(r) if x) for r in rs]
    counts = Counter(edges)
    e = len(counts)
    m = sum(v == 2 for v in counts.values())
    d = sum(not a & b for a, b in combinations(edges, 2))
    return e, m, d, edges


def predicted(rs, rows):
    e, m, d, edges = geometry(rs)
    bad = sum(edges[i] == edges[j] and
              not ((rows[i] >> j & 1) and (rows[j] >> i & 1))
              for i, j in combinations(range(len(rs)), 2))
    return 2*e+2*bad


def relevant_census(n, independent=False):
    """7 states/edge; disjoint-edge entries are zero representatives."""
    rs = roots(n)
    masks = supports(rs)
    edge_count = len(rs)//2
    hist = {}
    symmetric = {}
    checked = 0
    # (live signs, forward mate bit, reverse mate bit)
    states = ((0, 0, 0), (1, 0, 0), (2, 0, 0),
              (3, 1, 1), (3, 0, 0), (3, 0, 1), (3, 1, 0))
    for word in product(range(7), repeat=edge_count):
        live, e, m, bad = 0, 0, 0, 0
        rows = [1 << i for i in range(len(rs))]
        sym = True
        for t, state in enumerate(word):
            occupied, a, b = states[state]
            live |= occupied << (2*t)
            e += bool(occupied)
            m += occupied == 3
            bad += occupied == 3 and not (a and b)
            rows[2*t] |= a << (2*t+1)
            rows[2*t+1] |= b << (2*t)
            sym &= a == b
        if not live:
            continue
        actual = price(rows, masks, live)
        need(actual == 2*e+2*bad, 'relevant cost mismatch')
        if independent:
            need(price(rows, masks, live, span_rank) == actual, 'row-span mismatch')
        hist.setdefault(live, Counter())[actual] += 1
        if sym:
            symmetric.setdefault(live, Counter())[actual] += 1
        checked += 1
    for live, costs in hist.items():
        occupancy = [(live >> (2*t)) & 3 for t in range(edge_count)]
        e, m = sum(bool(x) for x in occupancy), occupancy.count(3)
        need(dict(costs) == {2*e+2*k: comb(m, k)*3**k for k in range(m+1)},
             'directed polynomial mismatch')
        need(dict(symmetric[live]) == {2*e+2*k: comb(m, k) for k in range(m+1)},
             'symmetric polynomial mismatch')
    need(checked == 7**edge_count-1 and len(hist) == 4**edge_count-1,
         'census domain mismatch')
    return {'n': n, 'punctures': len(hist), 'relevant_pairings': checked,
            'symmetric_relevant_pairings': sum(sum(x.values()) for x in symmetric.values()),
            'independent_row_span': independent}


def d5_punctures():
    rs = roots(5)
    masks = supports(rs)
    rows = [sum(1 << j for j, b in enumerate(rs) if i == j or dot(a, b) == 0)
            for i, a in enumerate(rs)]
    admissible(rs, rows)
    lookup = []
    for support in masks:
        indices = [i for i in range(20) if support >> i & 1]
        table = {}
        for local in range(1 << len(indices)):
            live = sum(1 << i for bit, i in enumerate(indices) if local >> bit & 1)
            selected = [row & live for i, row in enumerate(rows) if live >> i & 1]
            value = rank(selected)
            need(value == span_rank(selected), 'D5 independent subblock rank')
            table[live] = value
        lookup.append(table)
    even = sum(1 << (2*t) for t in range(10))
    hist = Counter()
    for live in range(1, 1 << 20):
        actual = sum(table[live & support] for table, support in zip(lookup, masks))
        edges = ((live | (live >> 1)) & even).bit_count()
        single = ((live ^ (live >> 1)) & even).bit_count()
        need(actual == 2*edges and actual-live.bit_count() == single,
             'D5 puncture minimum mismatch')
        hist[actual-live.bit_count()] += 1
    expected = {j: 2**10*comb(10, j)-(j == 0) for j in range(11)}
    need(dict(hist) == expected, 'D5 puncture histogram')
    return {'punctures': sum(hist.values()), 'ties': hist[0],
            'minimum_minus_v_histogram': dict(sorted(hist.items())),
            'direct_subblock_ranks': sum(len(t) for t in lookup),
            'roots_sha256': sha256(json.dumps(rs, separators=(',', ':')).encode()).hexdigest()}


def random_pairings():
    rng = Random(2026101513)
    checked = 0
    for n in range(2, 11):
        all_roots = roots(n)
        for trial in range(40):
            rs = [r for r in all_roots if trial == 0 or rng.randrange(4)]
            if not rs:
                rs = all_roots[:1]
            rows = [sum(1 << j for j, b in enumerate(rs)
                        if i == j or (dot(a, b) == 0 and rng.randrange(2)))
                    for i, a in enumerate(rs)]
            admissible(rs, rows)
            need(price(rows, supports(rs), (1 << len(rs))-1) == predicted(rs, rows),
                 'arbitrary directed pairing mismatch')
            checked += 1
    return checked


def controls():
    rs = roots(3)
    all_ones = [(1 << len(rs))-1] * len(rs)
    need(price(all_ones, supports(rs), (1 << len(rs))-1) == 3 < len(rs),
         'inadmissible gain control')
    try:
        admissible(rs, all_ones)
    except ValueError as exc:
        need(str(exc) == 'pairing forced zero', 'wrong inadmissibility control')
    else:
        raise ValueError('nonorthogonal pairing accepted')
    try:
        admissible(roots(2), [0, 2])
    except ValueError as exc:
        need(str(exc) == 'pairing diagonal', 'wrong diagonal control')
    else:
        raise ValueError('zero diagonal accepted')
    mate_costs = []
    for a, b in product(range(2), repeat=2):
        rows = [1 | a << 1, 2 | b]
        admissible(roots(2), rows)
        mate_costs.append(price(rows, supports(roots(2)), 3))
    need(mate_costs == [4, 4, 4, 2], 'directed mate control')
    # Same singleton Gram [8]; changed factor supports p=(1,0), q=(8,0).
    need(dot((2, 2), (2, 2)) == dot((1, 0), (8, 0)) == 8,
         'basis boundary identity')
    standard = price([1], [1, 1], 1)
    changed = rank([1]) + rank([])
    need((standard, changed) == (2, 1), 'fixed-basis boundary control')
    return {'invalid_forced_zero_rejected': True, 'invalid_diagonal_rejected': True,
            'directed_mate_costs_00_01_10_11': mate_costs,
            'same_singleton_gram_standard_changed_costs': [standard, changed]}


def compute():
    full = {}
    for n in range(2, 11):
        rs = roots(n)
        e, m, d, _ = geometry(rs)
        need(d == 12*comb(n, 4), 'disjoint-root count')
        full[n] = {'v': len(rs), 'minimum': 2*e, 'complete_pairs': m,
                   'disjoint_root_pairs': d, 'directed_optimizers': 2**(2*d),
                   'symmetric_optimizers': 2**d, 'tied_punctures': 2**e-1}
    return {'schema_version': 1, 'scope': 'fixed standard D_n coordinate Gram decoder',
            'formula': 'cost=2e+2k; directed polynomial=2^(2d)*z^(2e)*(1+3z^2)^m',
            'relevant_censuses': [relevant_census(3, True), relevant_census(4)],
            'd5': d5_punctures(), 'directed_sample_cases': random_pairings(),
            'full_families': full, 'controls': controls()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = compute()
    encoded = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if args.out:
        with args.out.open('x', encoding='utf-8', newline='\n') as output:
            output.write(encoded)
    else:
        need(json.loads((HERE/'RESULT.json').read_text()) == json.loads(encoded),
             'complete receipt mismatch')
    print('PASS_DN_PAIRING_SPECTRUM D4_relevant_pairings=117648 D5_punctures=1048575 ties=1023')


if __name__ == '__main__':
    main()
