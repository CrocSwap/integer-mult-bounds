#!/usr/bin/env python3
"""Independent tiny-field spectral check; no author/predecessor imports.

Characteristic polynomials use determinant permutations; zero-primary index
uses literal vector kernels. Written independently by the session lead for
@CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from itertools import permutations, product
import json


def mul(a, b, field):
    if field == 2:
        return a & b
    # F4 = F2[x]/(x^2+x+1), polynomial-bit encoding.
    p = (a if b & 1 else 0) ^ (a << 1 if b & 2 else 0)
    return p ^ (7 if p & 4 else 0)


def polynomial_product(a, b, field):
    c = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i + j] ^= mul(x, y, field)
    return c


def characteristic(matrix, field):
    n = len(matrix)
    answer = [0] * (n + 1)
    for order in permutations(range(n)):
        term = [1]
        for i, j in enumerate(order):
            term = polynomial_product(term, [matrix[i][j], 1] if i == j else [matrix[i][j]], field)
        for i, value in enumerate(term):
            answer[i] ^= value
    return tuple(answer)


def apply(matrix, vector, field):
    result = []
    for row in matrix:
        value = 0
        for a, b in zip(row, vector):
            value ^= mul(a, b, field)
        result.append(value)
    return tuple(result)


def invariants(matrix, field):
    cp = characteristic(matrix, field)
    z = next(i for i, a in enumerate(cp) if a)
    if z == 0:
        return 0, 0
    images = list(product(range(field), repeat=len(matrix)))
    for exponent in range(1, len(matrix) + 1):
        images = [apply(matrix, vector, field) for vector in images]
        if sum(not any(vector) for vector in images) == field**z:
            return z, exponent
    raise RuntimeError("kernel did not reach characteristic multiplicity")


def census(field, n):
    # Cache only independently computed (z, nu0); rank variations change B.
    profiles = {}
    for data in product(range(field), repeat=n*n):
        a = tuple(tuple(data[n*i:n*(i+1)]) for i in range(n))
        profiles[data] = invariants(a, field)
    best, counts = [-1]*(n+1), [0]*(n+1)
    general_best, general_counts = [-1]*(n+1), [0]*(n+1)
    for k in range(n+1):
        for data, (za, ca) in profiles.items():
            other = tuple(value ^ int(i//n == i % n and i//n < k)
                          for i, value in enumerate(data))
            zb, cb = profiles[other]
            if ca <= 2 and cb <= 2:
                general_best[k] = max(general_best[k], za+zb)
                general_counts[k] += 1
            if k == n-1:
                for cap in range(max(1, ca, cb), n+1):
                    best[cap] = max(best[cap], za+zb)
                    counts[cap] += 1
    expected = [n + cap - (cap % 2 == 0) for cap in range(1, n + 1)]
    if best[1:] != expected:
        raise ValueError((field, n, best, expected))
    if general_best != [2*n-k for k in range(n+1)]:
        raise ValueError((field, n, general_best))
    return {"field": field, "dimension": n, "matrices": field**(n*n),
            "maximum": best[1:], "admissible_counts": counts[1:],
            "cap_two_all_rank_maximum": general_best,
            "cap_two_all_rank_admissible_counts": general_counts,
            "cap_two_all_rank_pairs": (n+1)*field**(n*n)}


def main():
    # The polynomial method detects algebraic, not geometric multiplicity.
    nilpotent = ((0, 1), (0, 0))
    if invariants(nilpotent, 2) != (2, 2):
        raise ValueError("nilpotent control")
    if characteristic(((2,),), 4) != (2, 1):
        raise ValueError("nonbinary field control")
    rows = [census(2, n) for n in range(1, 5)] + [census(4, n) for n in range(1, 3)]
    print(json.dumps({"status": "PASS_INDEPENDENT_CAPPED_SPECTRUM", "censuses": rows}, sort_keys=True))


if __name__ == "__main__":
    main()
