#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bounded discovery only; exact independent replay is supplied separately."""
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json


def dot(a, b):
    return (a & b).bit_count() & 1


def span(basis):
    out = [0]
    for b in basis:
        out += [v ^ b for v in out]
    return frozenset(out)


def subspaces(n):
    for d in range(n + 1):
        for pivots in combinations(range(n), d):
            slots = [(i, j) for i, p in enumerate(pivots)
                     for j in range(p + 1, n) if j not in pivots]
            for assignment in range(1 << len(slots)):
                basis = [1 << p for p in pivots]
                for k, (i, j) in enumerate(slots):
                    if assignment >> k & 1:
                        basis[i] |= 1 << j
                yield tuple(basis)


def orthogonal(basis, n):
    return frozenset(v for v in range(1 << n)
                     if all(not dot(v, b) for b in basis))


def kernel(s, t):
    k = (s & t).bit_count()
    return (1 if k == 0 else -1) if k % 2 == 0 else 0


def discover(n):
    if n != 6:
        raise ValueError('this certified experiment is restricted to dimension six')
    triples = sorted(sum(1 << k for k in c) for c in combinations(range(n), 3))
    pairs = list(combinations(triples, 2))
    geometric = {(a, b): set() for a in pairs for b in pairs
                 if all(not dot(s, t) for s in a for t in b)}
    relaxed = {r: set() for r in geometric}
    frames = Counter()
    for basis in subspaces(n):
        frames['all'] += 1
        u, v = span(basis), orthogonal(basis, n)
        if u & v != {0}:
            continue
        frames['nondegenerate'] += 1
        ss = [s for s in triples if s in u]
        tt = [t for t in triples if t in v]
        for a in combinations(ss, 2):
            for b in combinations(tt, 2):
                relaxed[a, b].add(len(basis))
        ss = [s for s in ss if any(x.bit_count() % 2 and not dot(x, s) for x in u)]
        tt = [t for t in tt if any(x.bit_count() % 2 and not dot(x, t) for x in v)]
        for a in combinations(ss, 2):
            for b in combinations(tt, 2):
                geometric[a, b].add(len(basis))
    groups = Counter()
    records = []
    for (a, b), ranks in geometric.items():
        rankone = kernel(a[0], b[0]) * kernel(a[1], b[1]) == kernel(a[0], b[1]) * kernel(a[1], b[0])
        common = bool((span(a) & span(b)) - {0})
        key = (dot(*a), dot(*b), rankone, common, tuple(sorted(relaxed[a, b])), tuple(sorted(ranks)))
        groups[key] += 1
        records.append([list(a), list(b), rankone, common,
                        sorted(relaxed[a, b]), sorted(ranks)])
    payload = json.dumps(sorted(records), separators=(',', ':')).encode('ascii')
    return {
        'schema': 'complex-parity-frame-census-v1',
        'base_commit': '66849e1475c930fd7732b1a0067ffee7e1e95f60',
        'assignment_seed': 35,
        'ambient_dimension': n,
        'labels': triples,
        'pair_convention': 'unordered within each side; source and target sides distinguished',
        'subspaces': dict(frames),
        'orthogonal_rectangles': len(geometric),
        'scalar_rank_one_rectangles': sum(v for k, v in groups.items() if k[2]),
        'admissible_rank_one_rectangles': sum(v for k, v in groups.items() if k[2] and k[-1]),
        'classes': [dict(source_pair_dot=k[0], target_pair_dot=k[1],
                         scalar_rank_one=k[2], common_span_nonzero=k[3],
                         separating_dimensions=list(k[4]), admissible_dimensions=list(k[5]),
                         count=v) for k, v in sorted(groups.items())],
        'all_rectangle_records_sha256': sha256(payload).hexdigest(),
        'coverage': 'All 2825 subspaces and all ordered pairs of unordered triple pairs in F2^6; no timeout or sampling.',
        'kappa_claim': None,
    }


if __name__ == '__main__':
    print(json.dumps(discover(6), indent=2))
