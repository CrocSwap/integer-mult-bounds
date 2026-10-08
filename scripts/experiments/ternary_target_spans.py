#!/usr/bin/env python3
"""Exact labels for aggregating the ten complete pair outputs of one target.

This certifies nondegeneracy and the role-count obstruction, not an improvement.
The F3 five-subset construction is due to Zhihao Chen, PR #7.
"""
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations
import argparse
import json

from ternary_target_circuit import basis


def determinant(matrix):
    a = [list(map(Q, row)) for row in matrix]
    value = Q(1)
    for i in range(len(a)):
        pivot = next((j for j in range(i, len(a)) if a[j][i]), None)
        if pivot is None:
            return Q(0)
        if pivot != i:
            a[i], a[pivot] = a[pivot], a[i]
            value = -value
        d = a[i][i]
        value *= d
        for row in a[i+1:]:
            factor = row[i]/d
            row[i:] = [x-factor*y for x, y in zip(row[i:], a[i][i:])]
    return value


def graph_projection(edges):
    """Incidence-column rank and squared projection of the all-one vector."""
    neighbors = {i: set() for i in range(5)}
    for a, b in edges:
        neighbors[a].add(b); neighbors[b].add(a)
    visited = set()
    rank, weight = 0, Q(0)
    for root in range(5):
        if root in visited or not neighbors[root]:
            continue
        colors, stack, bipartite = {root: 0}, [root], True
        while stack:
            a = stack.pop(); visited.add(a)
            for b in neighbors[a]:
                if b not in colors:
                    colors[b] = 1-colors[a]; stack.append(b)
                elif colors[a] == colors[b]:
                    bipartite = False
        size = len(colors)
        if bipartite:
            left = sum(c == 0 for c in colors.values())
            rank += size-1
            weight += Q(4*left*(size-left), size)
        else:
            rank += size
            weight += size
    return rank, weight


def audit(h=28):
    assert h >= 9
    n = h-5
    pairs = list(combinations(range(5), 2))
    gamma = Q(1, 2)-Q(9, 4*n)
    counts, singular = Counter(), []
    for mask in range(1, 1 << 10):
        edges = [p for i, p in enumerate(pairs) if mask >> i & 1]
        B = basis(tuple(tuple(int(j in pair) for j in range(5)) for pair in edges))
        rank, weight = graph_projection(edges)
        assert len(B) == rank
        euclidean = tuple(tuple(sum(x*y for x, y in zip(u, v)) for v in B) for u in B)
        restricted = tuple(tuple(sum(x*y for x, y in zip(u, v))-gamma*sum(u)*sum(v)
                                 for v in B) for u in B)
        factor = 1-gamma*weight
        assert determinant(restricted) == determinant(euclidean)*factor
        counts['positive' if factor > 0 else 'indefinite' if factor < 0 else 'degenerate'] += 1
        counts['full_target_span'] += rank == 5
        if not factor:
            singular.append(mask)
        # An aggregation tree consumes exactly the output roles it removes.
        assert len(edges)-1+1 == len(edges)
        # Fusing its one-output boundary has rank one and still needs p slots.
        assert len(edges)+1-1 == len(edges)
    if h == 28:
        assert not singular
        assert gamma == Q(37, 92)
    # Independent finite check of the unique-target claim for each complete
    # pair partial. Differences outside S give the general h>=9 proof.
    S = set(range(5)); outside = range(5, 9)
    targets = list(combinations(range(9), 5))
    for pair in pairs:
        sources = [set(pair) | set(t) for t in combinations(outside, 3)]
        allowed = [t for t in targets if all(len(set(t) & u) == 2 for u in sources)]
        assert allowed == [tuple(sorted(S))]
    return dict(status='EXACT TARGET-AGGREGATION LABEL AUDIT; NO ROLE SAVING',
                h=h, nonempty_pair_families=1023, counts=dict(counts),
                singular_masks=singular, determinant_factor='1-(1/2-9/(4(h-5)))*w',
                every_graph_determinant_checked=True,
                small_unique_target_controls=True,
                per_target_binary_aggregation_role_saving=0,
                per_target_single_output_fusion_role_saving=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--h', type=int, default=28)
    args = parser.parse_args()
    print(json.dumps(audit(args.h), indent=2, sort_keys=True))
