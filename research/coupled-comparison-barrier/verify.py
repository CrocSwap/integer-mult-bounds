#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check coupled comparison-barrier updates with exact independent solves."""
from fractions import Fraction as Q
from itertools import permutations, product, combinations
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def det(a):
    n = len(a); total = Q(0)
    for p in permutations(range(n)):
        term = Q((-1)**sum(p[i] > p[j] for i in range(n) for j in range(i+1, n)))
        for i in range(n):
            term *= a[i][p[i]]
        total += term
    return total


def cramer(a, b):
    d = det(a); need(d != 0, 'singular matrix')
    return [det([[b[i] if j == k else a[i][j] for j in range(len(a))]
                 for i in range(len(a))])/d for k in range(len(a))]


def solve(a, b):
    n = len(a); rows = [list(r) + [b[i]] for i, r in enumerate(a)]
    for j in range(n):
        k = next(k for k in range(j, n) if rows[k][j])
        rows[j], rows[k] = rows[k], rows[j]
        d = rows[j][j]; rows[j] = [x/d for x in rows[j]]
        for k in range(n):
            if k != j:
                d = rows[k][j]; rows[k] = [x-d*y for x, y in zip(rows[k], rows[j])]
    return [r[-1] for r in rows]


M = [[Q(4), Q(-1), Q(0)], [Q(-1, 3), Q(5), Q(-1, 2)], [Q(0), Q(-1, 4), Q(3)]]


def run():
    directions = [(i, j) for i in range(3) for j in range(3) if i != j]
    h = solve(M, [Q(1)]*3)
    need(h == [Q(49,156), Q(10,39), Q(83,234)], 'retained source fixture')
    prepared = [solve(M, [Q(k == i) for k in range(3)]) for i in range(3)]
    safe = unsafe = windows = 0
    for d0, d1 in combinations(directions, 2):
        for s, t in product((Q(0), Q(1,2), Q(2), Q(8), Q(20)), repeat=2):
            ds = (d0, d1); ts = (s, t)
            x = [[prepared[ds[j][0]][i]*ts[j] for j in range(2)] for i in range(3)]
            c = [[x[ds[i][1]][j] for j in range(2)] for i in range(2)]
            small = [[Q(i == j)-c[i][j] for j in range(2)] for i in range(2)]
            admissible = c[0][0] < 1 and c[1][1] < 1 and det(small) > 0
            a = [r[:] for r in M]
            for (i,j), tau in zip(ds, ts):
                a[i][j] -= tau
            principal_positive = all(det([[a[i][j] for j in J] for i in J]) > 0
                                     for k in range(1,4) for J in combinations(range(3),k))
            need(admissible == principal_positive, 'coupling criterion versus all principal minors')
            if not admissible:
                unsafe += 1
                continue
            y = solve(small, [h[d0[1]], h[d1[1]]])
            updated = [h[i]+sum(x[i][j]*y[j] for j in range(2)) for i in range(3)]
            need(updated == cramer(a, [Q(1)]*3), 'prepared update versus fresh Cramer solve')
            for k in range(1, 4):
                for J in combinations(range(3), k):
                    block = [[a[i][j] for j in J] for i in J]
                    for signs in product((-1,1), repeat=k):
                        e = cramer(block, list(map(Q,signs)))
                        need(all(abs(v) <= updated[i] for i,v in zip(J,e)), 'principal-window residual')
                        windows += 1
            safe += 1
    for s in (Q(0), Q(1), Q(8), Q(20)):
        t = (Q(119,2)/(1+s)-1)/3
        a = [r[:] for r in M];a[0][1]-=s;a[1][0]-=t
        need(det(a) == 0, 'exact coupled threshold')
    need(8 < Q(117,2) and 2 < Q(39,2) and (1+8)*(1+3*2) > Q(119,2), 'separate checks miss coupling')
    need((1+3)*(1+3*3) < Q(119,2), 'safe joint fixture')
    return dict(status='PASS_COUPLED_BARRIER', safe_updates=safe, unsafe_updates=unsafe,
                window_vertices=windows, singular_thresholds=4,
                independent_safety_foil=True, no_new_kappa=True)


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True))
