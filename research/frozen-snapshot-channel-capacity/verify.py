#!/usr/bin/env python3
"""Exact finite corroboration of the frozen-snapshot capacity theorem.

Produced by Nick Petalas. Apache-2.0.
The scientific computation imports no predecessor executable.
"""
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, permutations, product
from math import gcd
from pathlib import Path
import json
import platform

MAX_DIM = 6
MAX_BITS = 256
PRIMES = (3, 5, 7, 11, 13, 17, 19, 23, 29, 31)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def matrix(rows, columns=None):
    require(0 < len(rows) <= MAX_DIM, 'row bound')
    n = len(rows[0]) if columns is None else columns
    require(0 <= n <= MAX_DIM, 'column bound')
    require(all(len(row) == n for row in rows), 'rectangular matrix')
    require(all(type(x) is int and x.bit_length() <= MAX_BITS
                for row in rows for x in row), 'integer coefficient bound')
    return tuple(tuple(row) for row in rows)


def identity(n):
    require(0 < n <= MAX_DIM, 'identity dimension')
    return matrix([[int(i == j) for j in range(n)] for i in range(n)])


def multiply(a, b):
    require(len(a[0]) == len(b), 'matrix product dimensions')
    return matrix([[sum(x * y for x, y in zip(row, col))
                    for col in zip(*b)] for row in a])


def determinant(a):
    n = len(a)
    require(0 < n <= MAX_DIM and all(len(row) == n for row in a),
            'determinant dimensions')
    total = 0
    for order in permutations(range(n)):
        inversions = sum(order[i] > order[j] for i in range(n)
                         for j in range(i + 1, n))
        term = (-1) ** inversions
        for i in range(n):
            term *= a[i][order[i]]
        total += term
    return total


def divisors(a):
    """All determinantal divisors, with d_0=1, in a bounded matrix."""
    result = [1]
    for size in range(1, min(len(a), len(a[0])) + 1):
        value = 0
        for rows in combinations(range(len(a)), size):
            for cols in combinations(range(len(a[0])), size):
                minor = [[a[i][j] for j in cols] for i in rows]
                value = gcd(value, determinant(minor))
        result.append(value)
    return result


def capacity(a):
    d = divisors(a)
    return max(k for k, value in enumerate(d)
               if value > 0 and value & (value - 1) == 0)


def field_rank(a, prime=None):
    """Independent elimination over Q or one of the declared prime fields."""
    require(prime is None or prime in PRIMES, 'prime domain')
    b = [[Fraction(x) if prime is None else x % prime for x in row]
         for row in a]
    rank = 0
    for col in range(len(a[0])):
        pivot = next((i for i in range(rank, len(a)) if b[i][col]), None)
        if pivot is None:
            continue
        b[rank], b[pivot] = b[pivot], b[rank]
        scale = 1 / b[rank][col] if prime is None else pow(b[rank][col], -1, prime)
        b[rank] = [x * scale for x in b[rank]]
        if prime is not None:
            b[rank] = [x % prime for x in b[rank]]
        for i in range(len(a)):
            if i != rank:
                factor = b[i][col]
                b[i] = [x - factor * y for x, y in zip(b[i], b[rank])]
                if prime is not None:
                    b[i] = [x % prime for x in b[i]]
        rank += 1
        if rank == len(a):
            break
    return rank


def bezout(a, b):
    """Bounded extended Euclid on signed integer inputs."""
    require(max(abs(a), abs(b)).bit_length() <= MAX_BITS, 'Euclid input bound')
    old_r, r, old_s, s, old_t, t = abs(a), abs(b), 1, 0, 0, 1
    for _ in range(2 * MAX_BITS + 2):
        if r == 0:
            u = old_s if a >= 0 else -old_s
            v = old_t if b >= 0 else -old_t
            require(u * a + v * b == old_r, 'Bezout identity')
            return old_r, u, v
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    raise ValueError('Euclid iteration bound')


def saturated_kernel(c):
    """An integer basis, also a full D-basis, of ker(c)."""
    q = identity(len(c[0]))
    for equation in c:
        if not q[0]:
            break
        row = multiply((equation,), q)[0]
        if not any(row):
            continue
        width = len(row)
        change = [list(r) for r in identity(width)]
        current = list(row)
        for j in range(1, width):
            a, b = current[0], current[j]
            g, u, v = bezout(a, b)
            if g == 0:
                continue
            for i in range(width):
                x, y = change[i][0], change[i][j]
                change[i][0] = u * x + v * y
                change[i][j] = -(b // g) * x + (a // g) * y
            current[0], current[j] = g, 0
        if width == 1:
            q = matrix([[] for _ in q])
        else:
            reduced = matrix([r[1:] for r in change])
            q = multiply(q, reduced)
    require(not any(x for row in multiply(c, q) for x in row), 'kernel equation')
    return q


def check_pair(k, c):
    require(len(k[0]) == len(c[0]), 'pair dimensions')
    q = saturated_kernel(c)
    r = field_rank(c)
    width = len(q[0])
    require(width == len(c[0]) - r, 'kernel dimension')
    require(divisors(q)[-1] == 1, 'kernel saturation')
    constrained = multiply(k, q)
    before, after = capacity(k), capacity(constrained)
    require(max(0, before - r) <= after <= before, 'capacity envelope')
    for a in (k, constrained):
        profile = [field_rank(a)] + [field_rank(a, p) for p in PRIMES]
        require(capacity(a) == min(profile), 'determinantal versus prime capacity')
    return before, after


def census():
    counts = {'one_snapshot_pairs': 0, 'two_snapshot_pairs': 0,
              'strict_losses': 0, 'loss_without_rational_rank_drop': 0}
    for values in product((-1, 0, 1, 3), repeat=4):
        k = matrix((values[:2], values[2:]))
        for row in product((-1, 0, 1, 3), repeat=2):
            c = matrix((row,))
            before, after = check_pair(k, c)
            counts['one_snapshot_pairs'] += 1
            if before > after:
                counts['strict_losses'] += 1
                if field_rank(k) == field_rank(multiply(k, saturated_kernel(c))):
                    counts['loss_without_rational_rank_drop'] += 1
    for kv in product((-1, 0, 1), repeat=4):
        k = matrix((kv[:2], kv[2:]))
        for cv in product((-1, 0, 1), repeat=4):
            check_pair(k, matrix((cv[:2], cv[2:])))
            counts['two_snapshot_pairs'] += 1
    return counts


def sharp_families():
    cases = 0
    for c in range(1, 4):
        for r in range(1, 4):
            for loss in range(min(c, r) + 1):
                for p in (3, 5, 7):
                    k = matrix([[int(i == j) for j in range(c + r)]
                                for i in range(c)])
                    constraints = [[0] * (c + r) for _ in range(r)]
                    for j in range(r):
                        constraints[j][c + j] = p if j < loss else 1
                        if j < loss:
                            constraints[j][j] = 1
                    constraints = matrix(constraints)
                    q = saturated_kernel(constraints)
                    require(field_rank(constraints) == r, 'sharp constraint rank')
                    require(field_rank(multiply(k, q)) == c, 'sharp rational rank')
                    require(capacity(k) == c, 'sharp initial capacity')
                    require(capacity(multiply(k, q)) == c - loss, 'sharp exact loss')
                    require(divisors(q)[-1] == 1, 'sharp saturated kernel')
                    cases += 1
    return cases


def dirty_word():
    cases = updates = 0
    for x, h0, h1 in product(range(-3, 4), repeat=3):
        original = (h0, h1)
        snapshot = h0 + 3 * h1
        for _ in range(3):
            h0 += x
            updates += 1
        h1 -= x
        updates += 1
        require(h0 + 3 * h1 == snapshot, 'live snapshot at reading cut')
        require(h0 - original[0] == 3 * x, 'restricted source response')
        h1 += x
        updates += 1
        for _ in range(3):
            h0 -= x
            updates += 1
        require((h0, h1) == original, 'arbitrary dirty restoration')
        require(h0 + 3 * h1 == snapshot, 'live snapshot at ERASE')
        cases += 1
    return {'dirty_inputs': cases, 'unit_add_updates': updates}


def controls():
    labels = []
    k = matrix(((1, 0),))
    c = matrix(((1, 3),))
    require(check_pair(k, c) == (1, 0), 'modular loss fixture')
    labels.append('rational-rank-only overcounts')
    require(capacity(multiply(k, matrix(((3,), (-1,))))) == 0,
            'unit-free constrained response')
    labels.append('unconstrained direction violates snapshot')
    require(multiply(c, matrix(((1,), (0,)))) == ((1,),), 'snapshot violation')
    wrong_kernel = matrix(((0,), (3,)))
    require(divisors(wrong_kernel)[-1] == 3, 'nonsaturated basis detectable')
    require(capacity(multiply(matrix(((0, 1),)), wrong_kernel)) == 0,
            'nonsaturated false loss')
    require(check_pair(matrix(((0, 1),)), matrix(((3, 0),))) == (1, 1),
            'primitive correct restriction')
    labels.append('nonsaturated kernel gives false loss')
    require(check_pair(k, matrix(((3, 0),))) == (1, 0), 'saturate before reduction')
    require(field_rank(matrix(((3, 0),)), 3) == 0, 'reduction-first rank collapse')
    labels.append('reduction before saturation overcounts')
    require(check_pair(k, matrix(((0, 0),))) == (1, 1), 'zero snapshot')
    labels.append('zero snapshot preserves capacity')
    require(check_pair(identity(2), identity(2)) == (2, 0), 'full snapshot')
    labels.append('full snapshot removes all directions')
    require(check_pair(k, matrix(((1, 3), (2, 6)))) == (1, 0), 'dependent rows')
    labels.append('dependent copies count by rank')
    for label, rows in [('ragged matrix', ((1,), (1, 2))),
                        ('noninteger coefficient', ((Fraction(1, 2),),)),
                        ('dimension overflow', (tuple(range(7)),)),
                        ('coefficient overflow', ((1 << MAX_BITS,),))]:
        try:
            matrix(rows)
        except ValueError:
            labels.append(label)
        else:
            raise ValueError('failed input control: ' + label)
    return labels


def main():
    result = census()
    result['sharp_family_cases'] = sharp_families()
    result.update(dirty_word())
    result['controls'] = controls()
    result['environment'] = {'implementation': platform.python_implementation(),
                             'python': platform.python_version()}
    package = Path(__file__).resolve().parent
    result['source_sha256'] = {p.name: sha256(p.read_bytes()).hexdigest()
                               for p in sorted(package.iterdir()) if p.is_file()}
    print(json.dumps(result, sort_keys=True, indent=2))
    print('PASS_FROZEN_SNAPSHOT_CHANNEL_CAPACITY')


if __name__ == '__main__':
    main()
