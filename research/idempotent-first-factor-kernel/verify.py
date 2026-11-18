#!/usr/bin/env python3
"""Check the kernel classification with two finite constructions."""

from collections import Counter
from functools import cache
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys


def require(ok, message):
    if not ok:
        raise ValueError(message)


def apply(matrix, vector):
    return sum(((row & vector).bit_count() % 2) << i
               for i, row in enumerate(matrix))


def mul(left, right):
    out = []
    for row in left:
        value = 0
        for j, other in enumerate(right):
            if row >> j & 1:
                value ^= other
        out.append(value)
    return tuple(out)


def add(*matrices):
    out = [0] * len(matrices[0])
    for matrix in matrices:
        out = [a ^ b for a, b in zip(out, matrix)]
    return tuple(out)


def identity(n):
    return tuple(1 << i for i in range(n))


def rows(code, n):
    return tuple((code >> (n * i)) & ((1 << n) - 1) for i in range(n))


def code(matrix):
    return sum(row << (len(matrix) * i) for i, row in enumerate(matrix))


def span(vectors):
    values = {0}
    for vector in vectors:
        values |= {x ^ vector for x in values}
    return frozenset(values)


@cache
def subspaces(n):
    found = {frozenset({0})}
    pending = [frozenset({0})]
    while pending:
        space = pending.pop()
        for vector in range(1, 1 << n):
            if vector in space:
                continue
            extended = space | {x ^ vector for x in space}
            if extended not in found:
                found.add(extended)
                pending.append(extended)
    return tuple(sorted(found, key=lambda s: (len(s), sorted(s))))


def basis(space):
    out = []
    known = frozenset({0})
    for vector in sorted(space):
        if vector not in known:
            out.append(vector)
            known = span(out)
    return tuple(out)


def complement(space, n):
    known = space
    out = []
    for i in range(n):
        vector = 1 << i
        if vector not in known:
            out.append(vector)
            known |= {x ^ vector for x in known}
    require(len(known) == 1 << n, 'complement does not span')
    return tuple(out)


def from_basis(domain, images, n):
    table = {0: 0}
    for vector, image in zip(domain, images):
        require(vector not in table, 'domain is not a basis')
        table.update({x ^ vector: y ^ image for x, y in list(table.items())})
    require(len(table) == 1 << n, 'domain misses a coordinate')
    return tuple(sum(((table[1 << j] >> i) & 1) << j for j in range(n))
                 for i in range(n))


def construct(n, r):
    """Use fixed complements for every invariant kernel. Keep no duplicates."""
    built = {}
    for ku in subspaces(r):
        for small_kw in subspaces(n - r):
            kw = frozenset(x << r for x in small_kw)
            kernel = frozenset(x ^ y for x in ku for y in kw)
            q1 = complement(ku, r)
            q0 = tuple(x << r for x in complement(small_kw, n - r))
            kb = basis(ku) + basis(kw)
            values = sorted(kernel)
            for f1 in product(values, repeat=len(q1)):
                if len(span(f1)) != 1 << len(q1):
                    continue
                for f0 in product(values, repeat=len(q0)):
                    matrix = from_basis(kb + q1 + q0,
                                        (0,) * len(kb) + f1
                                        + tuple(x ^ y for x, y in zip(q0, f0)), n)
                    require(matrix not in built, 'parameterization repeats a matrix')
                    actual = frozenset(x for x in range(1 << n) if not apply(matrix, x))
                    require(actual == kernel, 'constructed kernel differs')
                    built[matrix] = (len(ku).bit_length() - 1,
                                     len(kw).bit_length() - 1)
    return built


@cache
def gaussian(n, k):
    if k < 0 or k > n:
        return 0
    if k in (0, n):
        return 1
    return gaussian(n - 1, k) + (1 << (n - k)) * gaussian(n - 1, k - 1)


def parameter_count(n, r, u, v):
    injections = 1
    for i in range(r - u):
        injections *= (1 << (u + v)) - (1 << i)
    return (gaussian(r, u) * gaussian(n - r, v)
            * (1 << ((u + v) * (n - r - v))) * injections)


def counts(n, r):
    by_rank = [0] * (n + 1)
    for u in range(r + 1):
        for v in range(n - r + 1):
            by_rank[n - u - v] += parameter_count(n, r, u, v)
    one = sum(parameter_count(n, r, r, v) for v in range(n - r + 1))
    m = n - r
    both = sum(gaussian(m, j) * (1 << (j * (m - j))) for j in range(m + 1))
    total = sum(by_rank)
    return {'total': total, 'rank_B': by_rank, 'both_idempotent': both,
            'only_B_idempotent': one - both, 'only_C_idempotent': one - both,
            'neither_idempotent': total - 2 * one + both}


def polynomial_product(a, b, c):
    """Multiply entry polynomials directly, without the coefficient criterion."""
    n = len(a)
    acc = [[int(i == j) for j in range(n)] for i in range(n)]
    for matrix in (a, b, c):
        out = [[0] * n for _ in range(n)]
        for i in range(n):
            for k in range(n):
                value = acc[i][k]
                out[i][k] ^= value
                for j in range(n):
                    if matrix[k] >> j & 1:
                        out[i][j] ^= value << 1
        acc = out
    return tuple(tuple(row) for row in acc)


def target(n):
    return tuple(tuple(3 * int(i == j) for j in range(n)) for i in range(n))


def census(a, expected):
    n = len(a)
    eye, zero = identity(n), (0,) * n
    accepted = set()
    hist = Counter()
    ranks = Counter()
    failures = Counter()
    for integer in range(1 << (n * n)):
        b = rows(integer, n)
        c = add(eye, a, b)
        raw = polynomial_product(a, b, c) == target(n)
        reduced = mul(b, c) == zero
        require(raw == reduced, 'raw polynomial product differs from BC criterion')
        require(raw == (b in expected), 'kernel construction differs from raw product')
        if not raw:
            failures['rejected'] += 1
            continue
        accepted.add(b)
        idem_b, idem_c = mul(b, b) == b, mul(c, c) == c
        require(idem_b == (mul(b, a) == zero), 'B idempotence criterion')
        require(idem_c == (mul(a, b) == zero), 'C idempotence criterion')
        hist[f'{int(idem_b)}{int(idem_c)}'] += 1
        rank = len({apply(b, x) for x in range(1 << n)}).bit_length() - 1
        ranks[rank] += 1
    integers = sorted(code(b) for b in accepted)
    digest = sha256(''.join(f'{i}\n' for i in integers).encode()).hexdigest()
    actual = {'total': len(accepted), 'rank_B': [ranks[i] for i in range(n + 1)],
              'both_idempotent': hist['11'], 'only_B_idempotent': hist['10'],
              'only_C_idempotent': hist['01'], 'neither_idempotent': hist['00']}
    return actual | {'matrices': 1 << (n * n), 'rejected': failures['rejected'],
                     'accepted_sha256': digest}


def run():
    receipts = []
    for n in range(1, 5):
        for r in range(n + 1):
            a = tuple(1 << i if i < r else 0 for i in range(n))
            built = construct(n, r)
            actual = census(a, built)
            formula = counts(n, r)
            require(all(actual[k] == value for k, value in formula.items()), 'count formula')
            strata = Counter(built.values())
            for u in range(r + 1):
                for v in range(n - r + 1):
                    require(strata[u, v] == parameter_count(n, r, u, v), 'kernel stratum count')
            receipts.append({'n': n, 'rank_A': r, **actual})
    p = (1, 3, 4, 8)
    named = (1, 1, 0, 0)
    require(mul(p, p) == identity(4), 'named basis is not its own inverse')
    require(mul(mul(p, (1, 0, 0, 0)), p) == named, 'named basis does not conjugate A')
    transported = {mul(mul(p, b), p) for b in construct(4, 1)}
    named_result = census(named, transported)
    require(named_result['accepted_sha256'] ==
            '07a59d5644b30bf5c78ec67fd58bdee01cc1048fc5dc20ea574fffe3e4ec5659',
            'PR7223 named-matrix fingerprint differs')

    # Rank two permits two non-idempotent remaining factors.
    a, b = (1, 2, 0, 0), (2, 0, 0, 0)
    c = add(identity(4), a, b)
    require(polynomial_product(a, b, c) == target(4), 'rank-two witness misses target')
    require(mul(b, b) != b and mul(c, c) != c, 'rank-two witness is not discriminating')
    require(polynomial_product(a, b, add(c, (1, 0, 0, 0))) != target(4), 'changed C accepted')
    require(polynomial_product(b, (0,) * 4, add(identity(4), b)) != target(4),
            'non-idempotent A control accepted')
    # Non-injective f1 enlarges the declared kernel and must not be counted there.
    require(parameter_count(4, 2, 0, 0) == 0, 'impossible injection counted')
    require((0, 0, 0, 0) in construct(4, 4), 'zero map missing at A=I')
    require(construct(4, 4)[(0, 0, 0, 0)] == (4, 0), 'zero map assigned wrong kernel')
    for n in range(1, 13):
        for r in range(n + 1):
            result = counts(n, r)
            require(all(v >= 0 for k, v in result.items() if k != 'rank_B'), 'negative class count')
            if r == 1:
                require(result['neither_idempotent'] == 0, 'rank-one specialization')
    return {'canonical_censuses': receipts, 'named_census': named_result,
            'rank_two_witness': {'A': a, 'B': b, 'C': c},
            'formula_domain': '1 <= n <= 12, 0 <= r <= n',
            'scope': 'All-rank proof; complete raw-product censuses only through n=4.'}


def main():
    result = json.loads(json.dumps(run()))
    if sys.argv[1:] == ['--emit']:
        print(json.dumps(result, indent=2))
        return
    require(not sys.argv[1:], 'unknown arguments')
    expected = json.loads(Path(__file__).with_name('RESULT.json').read_text())
    require(result == expected, 'receipt differs')
    visits = sum(r['matrices'] for r in result['canonical_censuses']) + result['named_census']['matrices']
    print('PASS_IDEMPOTENT_FIRST_FACTOR_KERNEL', 'raw_matrix_cases=' + str(visits))


if __name__ == '__main__':
    main()
