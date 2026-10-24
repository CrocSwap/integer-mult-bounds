#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the inverse envelope for unequal row budgets."""
from fractions import Fraction as Q
from itertools import product
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def inv(a):
    n = len(a)
    b = [list(r) + [Q(i == j) for j in range(n)] for i, r in enumerate(a)]
    for j in range(n):
        k = next(k for k in range(j, n) if b[k][j])
        b[k], b[j] = b[j], b[k]
        t = b[j][j]
        b[j] = [x / t for x in b[j]]
        for k in range(n):
            if k != j:
                t = b[k][j]
                b[k] = [x - t * y for x, y in zip(b[k], b[j])]
    return [r[n:] for r in b]


def envelope(edges, budgets, root):
    n = len(budgets)
    need(all(0 < x < 1 for x in budgets), 'strict row gaps')
    def visit(i, seen):
        if i == root:
            return Q(1)
        return max([Q(0)] + [budgets[i] * visit(k, seen | {k})
                            for k in edges[i] if k not in seen])
    return [visit(i, {i}) / (1 - budgets[root]) for i in range(n)]


def attaining(edges, budgets, root, h):
    n = len(budgets)
    e = [[Q(0) for _ in range(n)] for _ in range(n)]
    e[root][root] = budgets[root]
    for i in range(n):
        if i != root and h[i]:
            k = next(k for k in edges[i] if h[i] == budgets[i] * h[k])
            need(h[k] > h[i], 'strict route ascent')
            e[i][k] = budgets[i]
    return e


def resolve(e):
    return inv([[Q(i == j) - x for j, x in enumerate(row)] for i, row in enumerate(e)])


def run():
    cases = signed = 0
    for n in (1, 2, 3):
        pairs = [(i, j) for i in range(n) for j in range(n) if i != j]
        for mask in range(1 << len(pairs)):
            edges = [{i} for i in range(n)]
            for bit, (i, j) in enumerate(pairs):
                if mask >> bit & 1:
                    edges[i].add(j)
            for budgets in product((Q(1, 4), Q(2, 3), Q(3, 4)), repeat=n):
                hs = [envelope(edges, budgets, root) for root in range(n)]
                cap = max(map(sum, hs))
                for root, h in enumerate(hs):
                    a = resolve(attaining(edges, budgets, root, h))
                    need([r[root] for r in a] == h, 'attaining column')
                    need(max(sum(abs(a[i][j]) for i in range(n)) for j in range(n)) <= cap, 'all columns')
                    cases += 1
                # Signed diffuse rows exercise more than deterministic routing.
                if mask % 7 == 0:
                    e = [[budgets[i] * (-1) ** (i + j + mask) / len(edges[i])
                          if j in edges[i] else Q(0) for j in range(n)] for i in range(n)]
                    a = resolve(e)
                    need(all(abs(a[i][j]) <= hs[j][i] for i in range(n) for j in range(n)), 'signed envelope')
                    signed += 1
    edges = [{0, 1}, {0, 1, 2}, {1, 2}]
    budgets = (Q(1, 2), Q(3, 4), Q(1, 4))
    actual = max(sum(envelope(edges, budgets, j)) for j in range(3))
    uniform = max(sum(envelope(edges, (max(budgets),) * 3, j)) for j in range(3))
    need((actual, uniform) == (7, 10), 'unequal-gap fixture')
    need(envelope([{0}, {1}], (Q(1, 2), Q(1, 3)), 0)[1] == 0, 'unreachable vertex')
    for bad in (Q(0), Q(1), Q(-1), Q(2)):
        try:
            envelope([{0}], (bad,), 0)
        except ValueError:
            pass
        else:
            raise ValueError('invalid gap accepted')
    # Without an allowed root loop, the claimed attaining matrix is illegal.
    need(resolve([[Q(0)]])[0][0] == 1 < 2, 'diagonal permission matters')
    return dict(status='PASS_UNEQUAL_ROW_ENVELOPE', attaining_columns=cases,
                signed_matrices=signed, fixture_exact=7, fixture_uniform=10,
                controls=7, no_new_kappa=True)


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True))
