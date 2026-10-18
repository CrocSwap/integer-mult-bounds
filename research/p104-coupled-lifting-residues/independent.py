"""Check the prefix lattice indices without importing its basis algorithm.

For every ideal prefix U_j, require each paired component of U_j(z) to
have even difference. Assemble these rational linear congruences together,
scaled to a common modulus M = 2**(rank//2 + 1). The desired index is the
size of the image of that integer matrix over Z/MZ.

Minimum-valuation pivots diagonalize this matrix over Z/MZ. Unit row
scaling and elementary row/column operations preserve its image size.
After clearing a pivot column, clearing its row leaves the remaining
submatrix unchanged, so the latter column operations need not be stored.
Each pivot 2**v contributes the cyclic factor M/2**v.

All ranks are bounded by seven. Python integer/list allocation is a managed
runtime deviation from fixed steady-operation storage. At most 896 rows of
256 residues are retained, plus two 256-by-256 ideal-prefix matrices and
bounded row scratch. No predecessor or primary implementation is imported.
"""

import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def congruences(rank):
    """Return the scaled simultaneous prefix constraints and their modulus."""
    need(type(rank) is int and 1 <= rank <= 7, "rank must be in 1..7")
    n = 1 << rank
    dimension = 2 * n
    modulus = 1 << (rank // 2 + 1)
    prefix = [[int(i == j) for j in range(dimension)] for i in range(dimension)]
    rows = []
    for stage in range(rank):
        denominator = 1 << (stage + 1)
        following = [None] * dimension
        for a in range(n):
            if a >> stage & 1:
                continue
            b = a ^ (1 << stage)
            ar, ai, br, bi = (
                prefix[2 * a],
                prefix[2 * a + 1],
                prefix[2 * b],
                prefix[2 * b + 1],
            )
            for left, right in ((ar, br), (ai, bi)):
                numerators = [
                    modulus * (x - y) for x, y in zip(left, right, strict=True)
                ]
                need(
                    all(x % denominator == 0 for x in numerators),
                    "common modulus does not clear a prefix denominator",
                )
                rows.append([(x // denominator) % modulus for x in numerators])
            following[2 * a] = [
                x - y + z + w for x, y, z, w in zip(ar, ai, br, bi, strict=True)
            ]
            following[2 * a + 1] = [
                y + x + w - z for x, y, z, w in zip(ar, ai, br, bi, strict=True)
            ]
            following[2 * b] = [
                x + y + z - w for x, y, z, w in zip(ar, ai, br, bi, strict=True)
            ]
            following[2 * b + 1] = [
                y - x + w + z for x, y, z, w in zip(ar, ai, br, bi, strict=True)
            ]
        need(all(row is not None for row in following), "incomplete ideal stage")
        prefix = following
    need(len(rows) == rank * n, "constraint count")
    return rows, modulus


def minimum_pivot(matrix, start):
    """Find a remaining nonzero entry with smallest 2-adic valuation."""
    best = None
    for i in range(start, len(matrix)):
        for j in range(start, len(matrix[0])):
            value = matrix[i][j]
            if value == 0:
                continue
            valuation = (value & -value).bit_length() - 1
            if best is None or valuation < best[0]:
                best = valuation, i, j
            if valuation == 0:
                return best
    return best


def quotient_factors(matrix, modulus):
    """Consume the matrix and return the kernel quotient's cyclic factors."""
    dimension = len(matrix[0])
    factors = {}
    pivots = 0
    for k in range(min(len(matrix), dimension)):
        best = minimum_pivot(matrix, k)
        if best is None:
            break
        valuation, i, j = best
        matrix[k], matrix[i] = matrix[i], matrix[k]
        for row in matrix:
            row[k], row[j] = row[j], row[k]
        pivot = 1 << valuation
        inverse_unit = pow(matrix[k][k] // pivot, -1, modulus)
        matrix[k] = [(value * inverse_unit) % modulus for value in matrix[k]]
        need(matrix[k][k] == pivot, "pivot normalization")
        for i in range(k + 1, len(matrix)):
            need(matrix[i][k] % pivot == 0, "pivot does not divide column")
            factor = matrix[i][k] // pivot
            if factor:
                matrix[i] = [
                    (x - factor * y) % modulus
                    for x, y in zip(matrix[i], matrix[k], strict=True)
                ]
            need(matrix[i][k] == 0, "column elimination")
        order = modulus // pivot
        factors[order] = factors.get(order, 0) + 1
        pivots += 1
    factors[1] = dimension - pivots
    return dict(sorted(factors.items()))


def verify():
    expected = (2, 6, 15, 34, 75, 161, 343)
    results = []
    for rank, exponent in enumerate(expected, 1):
        matrix, modulus = congruences(rank)
        factors = quotient_factors(matrix, modulus)
        actual = sum(
            (order.bit_length() - 1) * count for order, count in factors.items()
        )
        need(actual == exponent, f"rank {rank}: index exponent {actual}")
        results.append(dict(rank=rank, index_log2=actual, quotient_factors=factors))
    need(
        results[-1]["quotient_factors"] == {1: 36, 2: 125, 4: 70, 8: 22, 16: 3},
        "rank-seven invariant factors",
    )
    return results


if __name__ == "__main__":
    print(json.dumps(dict(status="PASS", ranks=verify()), indent=2))
