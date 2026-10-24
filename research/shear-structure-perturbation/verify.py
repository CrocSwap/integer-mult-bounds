#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check ordered shear perturbation bounds with exact rational matrices."""
from fractions import Fraction as F
from itertools import product
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def add(a, b):
    return [[x + y for x, y in zip(r, s)] for r, s in zip(a, b)]


def scale(a, t):
    return [[t * x for x in r] for r in a]


def mul(a, b):
    return [[sum(x * y for x, y in zip(r, c)) for c in zip(*b)] for r in a]


def norm(a):
    return max(sum(abs(x) for x in r) for r in a)


def inv(a):
    n = len(a)
    rows = [list(r) + s for r, s in zip(a, eye(n))]
    for j in range(n):
        k = next((k for k in range(j, n) if rows[k][j]), None)
        need(k is not None, 'singular matrix')
        rows[j], rows[k] = rows[k], rows[j]
        pivot = rows[j][j]
        rows[j] = [x / pivot for x in rows[j]]
        for k in range(n):
            if k != j:
                t = rows[k][j]
                rows[k] = [x - t * y for x, y in zip(rows[k], rows[j])]
    return [r[n:] for r in rows]


def run():
    counts = dict(circuits=0, prefixes=0, noise_steps=0, large_budget=0)
    for n, repeats, error in product((2, 3), (1, 2, 3), (F(0), F(1, 8), F(1), F(3))):
        data = []
        for i in range(4 * repeats):
            r, c = (i % n, (i + 1) % n)
            nil = [[F(0) for _ in range(n)] for _ in range(n)]
            nil[r][c] = 1
            a = F((-1) ** i * (i + 1), 3)
            e = (-1) ** (i // 2) * error
            data.append((nil, a, e))
        exact = [eye(n)]
        changed = [eye(n)]
        ds = []
        ps = [F(1)]
        for nil, a, e in data:
            ds.append(scale(mul(mul(inv(exact[-1]), nil), exact[-1]), e))
            exact.append(mul(add(eye(n), scale(nil, a)), exact[-1]))
            changed.append(mul(add(eye(n), scale(nil, a + e)), changed[-1]))
            ps.append(ps[-1] * (1 + norm(ds[-1])))
        bound = max(norm(z) for p in exact for z in (p, inv(p)))
        rel = eye(n)
        initial = [[F((-1) ** i, i + 1)] for i in range(n)]
        y = initial
        noise_terms = []
        for j, ((nil, a, e), d) in enumerate(zip(data, ds), 1):
            need(norm(mul(d, d)) == 0, 'nilpotent interaction error')
            rel = mul(add(eye(n), d), rel)
            need(changed[j] == mul(exact[j], rel), 'ordered interaction identity')
            need(norm(changed[j]) <= bound * ps[j], 'forward prefix')
            need(norm(inv(changed[j])) <= bound * ps[j], 'inverse prefix')
            need(norm(add(changed[j], scale(exact[j], -1))) <= bound * (ps[j] - 1), 'forward defect')
            need(norm(add(inv(changed[j]), scale(inv(exact[j]), -1))) <= bound * (ps[j] - 1), 'inverse defect')
            noise = [[F((-1) ** (i + j), 7 + j)] for i in range(n)]
            y = add(mul(add(eye(n), scale(nil, a + e)), y), noise)
            noise_terms.append(norm(mul(inv(exact[j]), noise)))
            allowance = bound * ((ps[j] - 1) * norm(initial) + sum(ps[j] / ps[i] * v for i, v in enumerate(noise_terms, 1)))
            need(norm(add(y, scale(mul(exact[j], initial), -1))) <= allowance, 'noise propagation')
            counts['prefixes'] += 1
            counts['noise_steps'] += 1
        counts['circuits'] += 1
        counts['large_budget'] += sum(map(norm, ds)) >= 1
    # These fixtures distinguish the hypotheses from stronger false claims.
    n = [[F(0), F(1)], [F(0), F(0)]]
    need(inv(add(eye(2), scale(n, 100))) == add(eye(2), scale(n, -100)), 'large error stays invertible')
    singular = [[F(0), F(0)], [F(0), F(1)]]
    try:
        inv(singular)
    except ValueError:
        pass
    else:
        raise ValueError('arbitrary-entry singular control')
    m = [[F(0), F(0)], [F(1), F(0)]]
    need(mul(add(eye(2), n), add(eye(2), m)) != add(eye(2), add(n, m)), 'higher order cannot be dropped')
    need(mul(add(eye(2), n), add(eye(2), m)) != mul(add(eye(2), m), add(eye(2), n)), 'order matters')
    # The exact endpoint is I but its intermediate scale is large.
    u = add(eye(2), scale(n, 100))
    v = add(eye(2), m)
    need(norm(mul(mul(inv(u), v), u)) > norm(v), 'endpoint bound does not bound prefixes')
    counts['controls'] = 5
    return dict(status='PASS_SHEAR_PERTURBATION', **counts, no_new_kappa=True)


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True))
