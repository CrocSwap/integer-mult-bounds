"""Separate finite implementation: dense scalars and per-entry exponent sets.

This module does not import the primary verifier or predecessor implementations.
Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
from itertools import permutations


def check(ok, reason):
    if not ok:
        raise ValueError("independent: " + reason)


def rows(code, n):
    return [[(code >> (i * n + j)) & 1 for j in range(n)] for i in range(n)]


def binary_rank(a):
    a = [row[:] for row in a]
    r = 0
    for c in range(len(a[0])):
        p = next((i for i in range(r, len(a)) if a[i][c]), None)
        if p is None:
            continue
        a[p], a[r] = a[r], a[p]
        for i in range(len(a)):
            if i != r and a[i][c]:
                a[i] = [x ^ y for x, y in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def scalar_mul(a, b):
    n = len(a)
    return [[sum(a[i][k] * b[k][j] for k in range(n)) % 2
             for j in range(n)] for i in range(n)]


def rational_rank(a):
    """Fraction-free elimination, clearing each row's denominators first."""
    from math import gcd, lcm
    work = []
    for row in a:
        den = lcm(*(Fraction(x).denominator for x in row))
        work.append([int(Fraction(x) * den) for x in row])
    r = 0
    if not work:
        return r
    for c in range(len(work[0])):
        p = next((i for i in range(r, len(work)) if work[i][c]), None)
        if p is None:
            continue
        work[r], work[p] = work[p], work[r]
        for i in range(r + 1, len(work)):
            if work[i][c]:
                u, v = work[r][c], work[i][c]
                work[i] = [u * x - v * y for x, y in zip(work[i], work[r])]
                g = 0
                for x in work[i]:
                    g = gcd(g, x)
                if g:
                    work[i] = [x // g for x in work[i]]
        r += 1
        if r == len(work):
            break
    return r


def multiply(a, b):
    """Matrix entries are sets of exponents; addition is symmetric difference."""
    n = len(a)
    out = [[set() for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            cell = out[i][j]
            for k in range(n):
                for x in a[i][k]:
                    for y in b[k][j]:
                        term = tuple(u + v for u, v in zip(x, y))
                        if term in cell:
                            cell.remove(term)
                        else:
                            cell.add(term)
    return out


def call(a, p):
    n = len(p)
    zero = (Fraction(0),) * len(a)
    out = [[{zero} if i == j else set() for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            if p[i][j]:
                out[i][j] ^= {zero}
                out[i][j] ^= {a}
    return out


def word(ops, n, dimension):
    zero = (Fraction(0),) * dimension
    acc = [[{zero} if i == j else set() for j in range(n)] for i in range(n)]
    for a, p in ops:
        acc = multiply(acc, call(a, rows(p, n)))
    return acc


def check_structure(expected):
    n = expected["registers"]
    groups = {}
    catalogue = []
    # Exhaust all 2^(n*n) matrices instead of enumerating outer products.
    for code in range(1 << (n * n)):
        p = rows(code, n)
        if binary_rank(p) == 1 and scalar_mul(p, p) == p:
            catalogue.append(code)
            pattern = tuple((i, j) for i in range(n) for j in range(n)
                            if i != j and p[i][j])
            groups.setdefault(pattern, []).append(p)
    check(len(catalogue) == expected["projectors"], "projector census")
    check(len(groups) == expected["off_diagonal_patterns"], "pattern census")
    import hashlib, json
    check(hashlib.sha256(json.dumps(catalogue).encode()).hexdigest()
          == expected["projectors_sha256"], "complete catalogue identity")
    cyclic = 0
    noncommuting = 0
    for pattern, pool in groups.items():
        orders = [order for order in permutations(range(n))
                  if all(order.index(i) < order.index(j) for i, j in pattern)]
        if orders:
            check(all(sum(p[i][i] for i in range(n)) == 1 for p in pool),
                  "acyclic diagonal count")
        else:
            cyclic += 1
            check(len(pool) == 1, "cyclic pattern uniqueness")
        for p in pool:
            for k in range(n):
                e = [[int(i == k == j) for j in range(n)] for i in range(n)]
                constant = [[{(Fraction(0),)} if x else set() for x in row] for row in e]
                q = multiply(multiply(call((Fraction(1),), p), constant),
                             call((Fraction(-1),), p))
                off = [q[i][j] for i in range(n) for j in range(n) if i != j]
                incident = any(p[k][j] or p[j][k] for j in range(n) if j != k)
                check(any(off) == incident, "conjugation off-diagonal support")
                if incident:
                    noncommuting += 1
                    check({(Fraction(0),), (Fraction(1),)} in off or
                          {(Fraction(0),), (Fraction(-1),)} in off,
                          "conjugation monomial witness")
    check(cyclic == expected["cyclic_patterns"], "cyclic pattern count")
    check(noncommuting == expected["noncommuting_conjugations"], "active conjugation count")


def check_word(name, fixture, packed_product, expected):
    n, m, ops, diagonal, scope = fixture
    check(len(ops) - rational_rank([a for a, _ in ops]) == expected["relation_nullity"],
          name + " frame relations")
    for a, code in ops:
        check(rational_rank([a[i * m:(i + 1) * m] for i in range(m)]) == 1,
              name + " address rank")
        p = rows(code, n)
        check(binary_rank(p) == 1 and scalar_mul(p, p) == p, name + " scalar admissibility")
    actual = word(ops, n, m * m)
    for i in range(n):
        for j in range(n):
            expected_cell = {a for a, code in packed_product.items()
                             if (code >> (i * n + j)) & 1}
            check(actual[i][j] == expected_cell, name + " exact formal coefficients")
    is_diagonal = all(not actual[i][j] for i in range(n) for j in range(n) if i != j)
    is_diagonal &= all(len(actual[i][i]) == 1 for i in range(n))
    check(is_diagonal == diagonal, name + " endpoint")
    if diagonal:
        ranks = []
        for i in range(n):
            target = next(iter(actual[i][i]))
            ranks.append(rational_rank([target[j * m:(j + 1) * m] for j in range(m)]))
        check(ranks == expected["target_ranks"], name + " target rank bill")


def check_controls():
    a = (Fraction(1),) + (Fraction(0),) * 15
    rank_two = rows(1 | (1 << 5), 4)
    check(binary_rank(rank_two) == 2, "rank-two exclusion")
    endpoint = call(a, rank_two)
    check(endpoint[0][0] == endpoint[1][1] == {a}, "rank-two bill counterexample")
    check(call(a, rows(1, 4)) != call(tuple(3 * x for x in a), rows(1, 4)),
          "integer address identity must not use parity")
