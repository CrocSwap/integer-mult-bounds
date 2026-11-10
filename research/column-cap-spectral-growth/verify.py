"""Exact finite corroboration; the universal theorem is in PROOF.md."""
from fractions import Fraction as Q
from itertools import product
import json
from math import isqrt
import random


def need(ok, message):
    if not ok:
        raise ValueError(message)


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def inverse(a):
    n = len(a)
    w = [list(row) + unit for row, unit in zip(a, eye(n))]
    for j in range(n):
        p = next((i for i in range(j, n) if w[i][j]), None)
        need(p is not None, 'singular')
        w[j], w[p] = w[p], w[j]
        z = w[j][j]
        w[j] = [x/z for x in w[j]]
        for i in range(n):
            if i != j:
                z = w[i][j]
                w[i] = [x-z*y for x, y in zip(w[i], w[j])]
    return [row[n:] for row in w]


def mm(a, b):
    return [[sum(x*y for x, y in zip(row, col))
             for col in zip(*b)] for row in a]


def apply(a, x):
    return [sum(v*w for v, w in zip(row, x)) for row in a]


def norm2(x):
    return sum(v*v for v in x)


def caps(e, m, rho):
    return (max(sum(map(abs, row)) for row in e) <= rho
            and max(sum(map(abs, col)) for col in zip(*e)) <= m*rho)


def upper(n, m, rho):
    s = isqrt(m)
    need(s*s == m, 'rational fixtures require square branching')
    a = rho*s
    k, size = 0, 1
    while size < n:
        k, size = k+1, size*m
    split = sum(a**j for j in range(k)) + a**k/(1-rho)
    return min(split, 1/(1-a)) if a < 1 else split


def positive_semidefinite(a):
    # Symmetric Schur elimination is an exact Sylvester/LDL test.
    w = [row[:] for row in a]
    for k in range(len(w)):
        need(w[k][k] >= 0, 'negative Euclidean certificate')
        if w[k][k] == 0:
            need(all(w[i][k] == 0 for i in range(k+1, len(w))),
                 'nonzero column at zero pivot')
            continue
        for i in range(k+1, len(w)):
            for j in range(k+1, len(w)):
                w[i][j] -= w[i][k]*w[k][j]/w[k][k]


def certify(e, m, rho):
    n = len(e)
    need(caps(e, m, rho), 'caps')
    h = [[Q(i == j)-e[i][j] for j in range(n)] for i in range(n)]
    r = inverse(h)
    need(mm(h, r) == eye(n) == mm(r, h), 'two inverse identities')
    gram = mm(list(map(list, zip(*r))), r)
    u = upper(n, m, rho)
    positive_semidefinite([[u*u*Q(i == j)-gram[i][j]
                       for j in range(n)] for i in range(n)])
    return r


def tree(m, h, rho):
    n = sum(m**i for i in range(h+1))
    e = [[Q(0) for _ in range(n)] for _ in range(n)]
    for v in range(1, n):
        e[v][(v-1)//m] = rho
    return e


def paths(m, n, rho):
    r = eye(n)
    for v in range(1, n):
        p, value = v, Q(1)
        while p:
            p, value = (p-1)//m, value*rho
            r[v][p] = value
    return r


def tree_checks():
    count = 0
    for m, hs, rhos in [(4, range(3), [Q(1,4), Q(1,2), Q(3,4)]),
                         (9, range(2), [Q(1,6), Q(1,3), Q(2,3)])]:
        s = isqrt(m)
        for h, rho in product(hs, rhos):
            e = tree(m, h, rho)
            r = certify(e, m, rho)
            need(r == paths(m, len(e), rho), 'tree path inverse')
            need(all(e[i][i] == 0 for i in range(len(e))), 'zero diagonal')
            levels, start = [], 0
            for l in range(h+1):
                v = [Q(0)]*len(e)
                for i in range(start, start+m**l):
                    v[i] = Q(1, s**l)
                levels.append(v)
                start += m**l
            for l, v in enumerate(levels):
                target = ([rho*s*x for x in levels[l+1]] if l < h
                          else [Q(0)]*len(e))
                need(apply(e, v) == target, 'radial shift')
            x = [sum(v[i] for v in levels) for i in range(len(e))]
            a = rho*s
            ratio = sum(sum(a**j for j in range(i+1))**2
                        for i in range(h+1))/Q(h+1)
            need(norm2(apply(r, x))/norm2(x) == ratio, 'coherent ratio')
            count += 1
    return count


def matrix_checks():
    count = 0
    for n in range(1, 5):
        for mapping in product(range(n), repeat=n):
            for rho in [Q(1,4), Q(1,2), Q(3,4)]:
                e = [[rho*Q(j == mapping[i]) for j in range(n)]
                     for i in range(n)]
                certify(e, 4, rho)
                count += 1
    rng = random.Random(68146788)
    for _ in range(96):
        n, rho = rng.randrange(2, 7), rng.choice([Q(1,4), Q(1,2), Q(3,4)])
        e = []
        for i in range(n):
            row = [rng.randrange(-3, 4) for _ in range(n)]
            den = max(1, sum(map(abs, row)))
            e.append([rho*x/den for x in row])
        # Some concentrated columns exceed the cap; rescale them uniformly.
        factor = max(Q(1), max(sum(map(abs, c)) for c in zip(*e))/(4*rho))
        certify([[x/factor for x in row] for row in e], 4, rho)
        count += 1
    return count


def phase_checks():
    count = 0
    for rho in [Q(1,4), Q(1,2), Q(3,4)]:
        n = 8
        # Each column has at most four predecessors, with nonzero self-loop.
        base = [[rho*Q(j == i//4) for j in range(n)] for i in range(n)]
        for offset in range(4):
            real = [[Q(0)]*(2*n) for _ in range(2*n)]
            for i in range(n):
                for j in range(n):
                    phase = (i*(offset+1)-j*(offset+1)) % 4
                    re, im = [(1,0),(0,1),(-1,0),(0,-1)][phase]
                    value = base[i][j]
                    real[i][j] = real[i+n][j+n] = value*re
                    real[i+n][j] = value*im
                    real[i][j+n] = -value*im
            # Realification preserves the complex Euclidean operator norm.
            certify(real, 4, rho)
            count += 1
    return count


def radial_checks():
    count = 0
    for m, s in [(4,2), (9,3), (16,4)]:
        for h in [1,2,4,8,16,32,64]:
            H = h+1
            for a in [Q(1,2), Q(1), Q(3,2)]:
                rho = a/s
                need(0 < rho < 1, 'valid rho')
                # Independent triangular recurrence, not powers of the dense tree.
                y, prev = [], Q(0)
                for _ in range(H):
                    prev = 1+a*prev
                    y.append(prev)
                ratio = norm2(y)/H
                explicit = sum(sum(a**j for j in range(i+1))**2
                               for i in range(H))/H
                need(ratio == explicit, 'radial geometric identity')
                if a == 1:
                    need(ratio == Q((H+1)*(2*H+1), 6), 'critical exact value')
                n = sum(m**i for i in range(H))
                need(ratio <= upper(n, m, rho)**2, 'large-tree bound')
                count += 1
    return count


def controls():
    bad = [[Q(0), Q(3,4)], [Q(0), Q(0)]]
    need(not caps(bad, 4, Q(1,2)), 'row-cap rejection')
    bad = [[Q(1,2)]+[Q(0)]*4 for _ in range(5)]
    need(not caps(bad, 4, Q(1,2)), 'column-cap rejection')
    e = tree(4, 1, Q(1,2))
    r = paths(4, len(e), Q(1,2))
    e[1][0] = 0
    need(inverse([[Q(i == j)-e[i][j] for j in range(len(e))]
                  for i in range(len(e))]) != r, 'deleted-edge detection')
    H = 17
    coherent = Q((H+1)*(2*H+1), 6)
    need(coherent > H, 'single-column estimate misses coherent growth')
    need(Q(14,3) > 4, 'dimension-21 critical tree refutes row-gap 2-norm <= 2')
    need(upper(85, 4, Q(1,4)) <= 2, '1-norm critical point is subcritical here')
    return 6


if __name__ == '__main__':
    receipt = dict(dense_trees=tree_checks(), cap_matrices=matrix_checks(),
                   virtual_radial_cases=radial_checks(), complex_phase_cases=phase_checks(),
                   controls=controls())
    print('PASS_COLUMN_CAP_SPECTRAL_GROWTH '+json.dumps(receipt, sort_keys=True))
