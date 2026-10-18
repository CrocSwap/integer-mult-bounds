#!/usr/bin/env python3
"""Independent support-keyed reconstruction of the selected tensor contraction.

Copyright 2026 Curtis Dransfield. Apache-2.0.
Prepared with substantial OpenAI Codex assistance. The tensor recurrence,
first-decomposition interning rule and balanced sum order originate in
Douglas R. Colkitt's retained disjoint-tensor work, with its Codex disclosure.

This implementation imports no repository code and does not subclass the
producer. Formal coefficient supports themselves are the DAG keys; integer
node numbers are reconstructed only to compare the exact retained digest.
The inherited descendant DP is recomputed from its stated recurrence.
"""
from functools import cache
from hashlib import sha256
from itertools import combinations
import json
from math import comb


def require(condition, message):
    if not condition:
        raise ValueError(message)


@cache
def choose_subsets(points, size):
    return tuple(sum(1 << point for point in subset) for subset in combinations(points, size))


def channels(n, left, a, b):
    right = n-left
    for j in range(max(0, b-right), min(left, b)+1):
        for i in range(max(0, a-right), min(left, a)+1):
            if i+j <= left and a-i+b-j <= right:
                yield i, j


def order_costs(left, right, a, b, i, j):
    ca = descendant_plan(left, i, j)[0]
    cb = descendant_plan(right, a-i, b-j)[0]
    return (comb(right, a-i)*ca + comb(left, j)*cb,
            comb(left, i)*cb + comb(right, b-j)*ca)


def split_bound(n, a, b, left, flip=None):
    cost = 0
    per_target_size = {}
    for i, j in channels(n, left, a, b):
        alternatives = order_costs(left, n-left, a, b, i, j)
        cost += max(alternatives) if flip == (i, j) else min(alternatives)
        per_target_size[j] = per_target_size.get(j, 0) + 1
    for j, parts in per_target_size.items():
        cost += comb(left, j)*comb(n-left, b-j)*(parts-1)
    return cost


@cache
def descendant_plan(n, a, b):
    require(0 <= a <= n and 0 <= b <= n, 'Invalid subset dimensions')
    if a+b > n:
        return 0, 'empty'
    if a == 0:
        return 0, 'copy'
    if b == 0:
        return comb(n, a)-1, 'sum'
    best = comb(n, b)*(comb(n-b, a)-1), 'rows'
    for left in range(1, n//2+1):
        candidate = split_bound(n, a, b, left)
        if candidate < best[0]:
            best = candidate, left
    return best


def reconstruct(h, root_split, flip=None):
    require(type(h) is int and h >= 6, 'Use integer h >= 6')
    require(type(root_split) is int and 1 <= root_split <= h//2, 'Invalid root split')
    require(flip is None or flip in tuple(channels(h, root_split, 3, 3)), 'Infeasible root channel')
    inputs = choose_subsets(tuple(range(h)), 3)
    input_supports = tuple(1 << index for index in range(len(inputs)))
    # A support is the identity of a formal sum, rather than an integer ID
    # whose support is stored elsewhere. First decomposition is retained.
    decomposition = {0: None, **{support: None for support in input_supports}}
    births = list(decomposition)
    identifiers = {support: index for index, support in enumerate(births)}
    flips_executed = 0

    def merge(left, right):
        if not left:
            return right
        if not right:
            return left
        require(left & right == 0, 'Non-disjoint formal addition')
        result = left | right
        if result not in decomposition:
            decomposition[result] = left, right
            identifiers[result] = len(births)
            births.append(result)
        return result

    def balanced_sum(values):
        if not values:
            return 0
        if len(values) == 1:
            return values[0]
        middle = len(values)//2
        return merge(balanced_sum(values[:middle]), balanced_sum(values[middle:]))

    def contract(points, a, b, values, root=False):
        nonlocal flips_executed
        n = len(points)
        method = root_split if root else descendant_plan(n, a, b)[1]
        targets = choose_subsets(points, b)
        if method == 'empty':
            return dict.fromkeys(targets, 0)
        if method == 'copy':
            return dict.fromkeys(targets, values[0])
        if method == 'sum':
            return {0: balanced_sum(list(values.values()))}
        if method == 'rows':
            return {target: balanced_sum([values[source] for source in choose_subsets(points, a)
                                           if source & target == 0]) for target in targets}
        left, right = points[:method], points[method:]
        buckets = {target: [] for target in targets}
        for i, j in channels(n, len(left), a, b):
            first_cost, second_cost = order_costs(len(left), len(right), a, b, i, j)
            left_first = first_cost <= second_cost
            if root and flip == (i, j):
                left_first = not left_first
                flips_executed += 1
            # One generic two-factor contraction handles both orders. This
            # replaces the original producer's two separate branch bodies.
            if left_first:
                first, second = (left, i, j), (right, a-i, b-j)
            else:
                first, second = (right, a-i, b-j), (left, i, j)
            p1, a1, b1 = first
            p2, a2, b2 = second
            intermediate = {}
            for source2 in choose_subsets(p2, a2):
                section = {source1: values[source1 | source2] for source1 in choose_subsets(p1, a1)}
                intermediate[source2] = contract(p1, a1, b1, section)
            for target1 in choose_subsets(p1, b1):
                section = {source2: row[target1] for source2, row in intermediate.items()}
                for target2, support in contract(p2, a2, b2, section).items():
                    buckets[target1 | target2].append(support)
        return {target: balanced_sum(terms) for target, terms in buckets.items()}

    outputs = contract(tuple(range(h)), 3, 3, dict(zip(inputs, input_supports)), root=True)
    require(flips_executed == int(flip is not None), 'Wrong number of root overrides')
    active = set()
    pending = list(outputs.values())
    while pending:
        support = pending.pop()
        if support == 0 or support in active:
            continue
        active.add(support)
        if decomposition[support] is not None:
            pending.extend(decomposition[support])
    additions = sum(decomposition[support] is not None for support in active)
    width = (len(inputs)+7)//8
    output_digest = sha256()
    for target in inputs:
        expected = sum(1 << index for index, source in enumerate(inputs) if source & target == 0)
        require(outputs[target] == expected, 'Complete integer coefficient map failed')
        output_digest.update(outputs[target].to_bytes(width, 'little'))
    rows = []
    for support in sorted(active, key=identifiers.__getitem__):
        parents = decomposition[support]
        parent_ids = None if parents is None else [identifiers[p] for p in parents]
        if parent_ids is not None:
            require(all(p < identifiers[support] for p in parent_ids), 'Birth order is not acyclic')
        rows.append([identifiers[support], parent_ids, str(support)])
    dag_digest = sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest()
    unshared = split_bound(h, 3, 3, root_split, flip)
    require(additions <= unshared, 'Interned additions exceed unshared upper bound')
    return dict(h=h, root_split=root_split, flip=flip, additions=additions,
                outputs=len(outputs), roles=additions+len(outputs),
                unshared_recurrence_additions=unshared, root_flips_executed=flips_executed,
                descendant_overrides=0, coefficient_positions_checked=len(inputs)**2,
                all_integer_output_coefficients_exact=True, all_created_additions_disjoint=True,
                dag_sha256=dag_digest, output_support_sha256=output_digest.hexdigest(),
                output_encoding='Lexicographic triples; fixed-width little-endian packed support rows',
                method='Fresh support-keyed interner, own DP and generic factor-order contraction; no repository imports')


def independent_check():
    results = [reconstruct(22, 11), reconstruct(22, 11, (1, 1)),
               reconstruct(8, 4, (1, 1)), reconstruct(10, 5, (1, 1))]
    require([result['additions'] for result in results[:2]] == [31929, 30708],
            'Independent h22 baseline/winner counts differ')
    return dict(status='PASS_INDEPENDENT_ROOT_CONTRACTION', results=results,
                scope='Selected and baseline maps/counts only; no independent phase or full scalar network replay')


if __name__ == '__main__':
    print(json.dumps(independent_check(), indent=2, sort_keys=True))
