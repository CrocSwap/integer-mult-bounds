#!/usr/bin/env python3
"""Independent polynomial-product replay. Cinna Davis / OpenAI Codex; Apache-2.0."""
import hashlib
import json
from itertools import product
from pathlib import Path
from random import Random
from constructor import Ring, identity, need, scalar_two_factors, three_factors


def mul(a, b, p, d):
    coefficients = [0] * (2*d-1)
    for i in range(d):
        for j in range(d):
            coefficients[i+j] += ((a // p**i) % p) * ((b // p**j) % p)
    return sum((coefficients[i] % p) * p**i for i in range(d))


def add(values, p, d):
    values = list(values)
    return sum((sum((a // p**i) % p for a in values) % p) * p**i for i in range(d))


def mm(a, b, p, d):
    return [[add((mul(x, y, p, d) for x, y in zip(row, column)), p, d)
             for column in zip(*b)] for row in a]


def execute(factors, p, d):
    out = identity(len(factors[0]))
    for factor in reversed(factors):
        out = mm(factor, out, p, d)
    return out


def rank(matrix, p):
    a = [[x % p for x in row] for row in matrix]
    r = 0
    for j in range(len(a[0])):
        pivot = next((i for i in range(r, len(a)) if a[i][j]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        inverse = pow(a[r][j], -1, p)
        a[r] = [x*inverse % p for x in a[r]]
        for i in range(len(a)):
            if i != r:
                c = a[i][j]
                a[i] = [(x-c*y) % p for x, y in zip(a[i], a[r])]
        r += 1
    return r


def cost(target, p, d):
    if all(x < p for row in target for x in row) and rank(target, p) == 2:
        return 0
    for x, y in product(range(p), repeat=2):
        if x or y:
            w = mm(target, [[x], [y]], p, d)
            if all(row[0] < p for row in w) and any(row[0] for row in w):
                return 1
    return 2


def skeleton(factors):
    m = len(factors[0]) // 2
    for factor, column in zip(factors, (0, 1, 0)):
        for i in range(2*m):
            for j in range((1-column)*m, (2-column)*m):
                need(factor[i][j] == int(i == j), 'illegal paid block column')


def check(ring, target):
    factors = three_factors(ring, target)
    skeleton(factors)
    need(execute(factors, ring.p, ring.d) == target, 'three-factor endpoint')
    return factors


def run():
    rng = Random(0xC1A1A20261023)
    scalar, samples, dirty, controls = [], 0, 0, 0
    for p, d in ((2, 1), (2, 2), (2, 3), (2, 4), (3, 1), (3, 2), (5, 1), (7, 1)):
        ring, counts = Ring(p, d), [0, 0, 0]
        for entries in product(range(ring.size), repeat=4):
            target = [list(entries[:2]), list(entries[2:])]
            need(execute(scalar_two_factors(ring, target), p, d) == target, 'scalar endpoint')
            counts[cost(target, p, d)] += 1
        scalar.append({'p': p, 'd': d, 'targets': ring.size**4, 'costs': counts})
        for _ in range(16):
            check(ring, [[rng.randrange(ring.size) for _ in range(2)] for _ in range(2)])
            samples += 1
    # Enumerate the entire one-factor/free-map orbit independently in two rings.
    for d in (2, 3):
        ring = Ring(2, d)
        free = [[list(e[:2]), list(e[2:])] for e in product(range(2), repeat=4)
                if (e[0]*e[3]-e[1]*e[2]) % 2]
        one = set()
        for u in product(range(ring.size), repeat=2):
            for y in ((0, 1), (1, 0), (1, 1)):
                factor = [[add((int(i == j), mul(u[i], y[j], 2, d)), 2, d)
                           for j in range(2)] for i in range(2)]
                for s in free:
                    one.add(tuple(x for row in mm(factor, s, 2, d) for x in row))
        for e in product(range(ring.size), repeat=4):
            need((e in one) == (cost([list(e[:2]), list(e[2:])], 2, d) <= 1), 'one-factor orbit')
    components = []
    for p, d, m, count in ((2, 2, 2, 192), (2, 4, 2, 96), (3, 2, 2, 96),
                           (2, 3, 3, 48), (3, 1, 3, 16)):
        ring = Ring(p, d)
        for index in range(count):
            target = [[rng.randrange(ring.size) for _ in range(2*m)] for _ in range(2*m)]
            if index % 4 == 0:
                target[:m] = [[ring.mul(ring.p if d > 1 else 0, x) for x in row]
                              for row in target[:m]]
            if index % 11 == 0:
                target = [[0]*(2*m) for _ in range(2*m)]
            factors = check(ring, target)
            samples += 1
            if index < 8:
                v = [[rng.randrange(ring.size)] for _ in range(2*m)]
                actual = v
                for factor in reversed(factors):
                    actual = mm(factor, actual, p, d)
                need(actual == mm(target, v, p, d), 'dirty input')
                dirty += 1
            if p == 2 and index == 1:
                components.append((ring, target, factors))
    need(len(components) == 3, 'product components')
    for ring, target, factors in components:
        skeleton(factors)
        need(execute(factors, ring.p, ring.d) == target, 'common product word')
    sharp = [[1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 1, 0], [1, 0, 1, 0]]
    need(rank(sharp, 2) == 2, 'sharp target rank')
    for phi in ((1, 0), (0, 1), (1, 1)):
        row = [[(phi[0]*sharp[i][j]+phi[1]*sharp[i+2][j]) % 2
                for j in range(4)] for i in range(2)]
        for t in ((1, 0), (0, 1), (1, 1)):
            cut = [[(t[0]*row[i][j]+t[1]*row[i][j+2]) % 2 for j in range(2)] for i in range(2)]
            need(rank(row, 2) == 2 and rank(cut, 2) == 1, 'nine-chart sharpness')
    for d in (1, 2, 3, 4, 5):
        check(Ring(2, d), sharp)
        samples += 1
    fixture = [[1, 2, 3, 4], [5, 6, 7, 8], [2, 1, 4, 3], [8, 5, 1, 7]]
    factors = check(Ring(3, 2), fixture)
    samples += 1
    for changed in (factors[::-1], factors[:2], factors[1:], (factors[0], factors[0], factors[2])):
        need(execute(changed, 3, 2) != fixture, 'mutation unexpectedly passes')
        controls += 1
    for thunk in (lambda: Ring(4, 2), lambda: Ring(2, 0), lambda: Ring(True, 2),
                  lambda: Ring(2, 2).unit_inverse(2),
                  lambda: three_factors(Ring(2, 2), [[True, 0], [0, 1]]),
                  lambda: three_factors(Ring(2, 2), [[0, 1, 0]])):
        try:
            thunk()
        except ValueError:
            controls += 1
        else:
            raise ValueError('invalid input accepted')
    need(mul(2, 2, 3, 2) == 1 and (2*2) % 9 != mul(2, 2, 3, 2), 'integer modulus mutant')
    controls += 1
    base = Path(__file__).resolve().parent
    files = sorted(p for p in base.iterdir() if p.is_file() and p.suffix in ('.py', '.md', '.json'))
    print(json.dumps({'status': 'PASS_CHAIN_RING_COMMON_WORDS', 'scalar_domains': scalar,
                      'scalar_targets': sum(x['targets'] for x in scalar), 'three_factor_cases': samples,
                      'dirty_inputs': dirty, 'controls': controls, 'sharp_charts_rejected': 9,
                      'files': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
                      'scope': 'Bounded corroboration of algebraic proof; no native supplier or new kappa.'},
                     sort_keys=True))


if __name__ == '__main__':
    run()
