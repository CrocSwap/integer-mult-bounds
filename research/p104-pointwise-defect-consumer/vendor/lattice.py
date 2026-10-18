"""Prefix-parity translation lattices, real coordinates interleaved by address.

Finite reference domain: ranks 1..7 and at most 4096 input magnitude bits.
The README's equivariance proof has no magnitude restriction. Apache-2.0.
"""

MAX_RANK = 7
MAX_BITS = 4096


def need(condition, message):
    if not condition:
        raise ValueError(message)


def dimension(rank):
    need(type(rank) is int and 1 <= rank <= MAX_RANK, "rank must be in 1..7")
    return 2 << rank


def vector(value, rank, max_bits=MAX_BITS):
    d = dimension(rank)
    need(len(value) == d, "real vector dimension")
    need(
        all(type(x) is int and x.bit_length() <= max_bits for x in value),
        "signed integer magnitude limit",
    )
    return list(value)


def stage(rows, bit):
    """Apply an ideal Gaussian butterfly to columns; require exact division."""
    d = len(rows)
    result = [None] * d
    for a in range(d // 2):
        if (a >> bit) & 1:
            continue
        b = a ^ (1 << bit)
        ar, ai, br, bi = rows[2 * a], rows[2 * a + 1], rows[2 * b], rows[2 * b + 1]
        signs = ((1, -1, 1, 1), (1, 1, -1, 1), (1, 1, 1, -1), (-1, 1, 1, 1))
        for target, coefficients in zip(
            (2 * a, 2 * a + 1, 2 * b, 2 * b + 1), signs, strict=True
        ):
            numerator = [
                sum(x * c for x, c in zip(values, coefficients, strict=True))
                for values in zip(ar, ai, br, bi, strict=True)
            ]
            need(all(x % 2 == 0 for x in numerator), "nonintegral ideal stage")
            result[target] = [x // 2 for x in numerator]
    return result


def restrict(rows, first, second):
    """Intersect the column lattice with one parity kernel; return index log2."""
    odd = [j for j in range(len(rows[0])) if (rows[first][j] - rows[second][j]) % 2]
    if not odd:
        return 0
    pivot = odd[0]
    for row in rows:
        for other in odd[1:]:
            row[other] -= row[pivot]
        row[pivot] *= 2
    return 1


def index_counts(rank):
    """Exact successive intersection, with one basis in current output space."""
    d = dimension(rank)
    rows = [[int(i == j) for j in range(d)] for i in range(d)]
    counts = []
    for bit in range(rank):
        count = 0
        for a in range(d // 2):
            if (a >> bit) & 1:
                continue
            b = a ^ (1 << bit)
            for component in range(2):
                count += restrict(rows, 2 * a + component, 2 * b + component)
        rows = stage(rows, bit)
        counts.append(count)
    return counts


def prefix_member(columns, rank):
    """Check every column against all prefix constraints, without basis search."""
    d = dimension(rank)
    need(len(columns) == d and all(len(row) == d for row in columns), "basis shape")
    rows = [row[:] for row in columns]
    for bit in range(rank):
        for a in range(d // 2):
            if (a >> bit) & 1:
                continue
            b = a ^ (1 << bit)
            for c in range(2):
                need(
                    all(
                        (x - y) % 2 == 0
                        for x, y in zip(rows[2 * a + c], rows[2 * b + c], strict=True)
                    ),
                    "basis violates prefix parity",
                )
        rows = stage(rows, bit)
    return rows


def validate_basis(rows, rank=7):
    d = dimension(rank)
    need(type(rows) is list and len(rows) == d, "basis rows")
    need(all(type(row) is list and len(row) == d for row in rows), "basis columns")
    need(
        all(type(x) is int and -16 <= x <= 16 for row in rows for x in row),
        "bounded integer basis entries",
    )
    need(all(rows[i][i] in (1, 2, 4, 8, 16) for i in range(d)), "basis diagonal")
    need(all(rows[i][j] == 0 for i in range(d) for j in range(i)), "upper triangular")
    need(
        all(0 <= rows[i][j] < rows[i][i] for i in range(d) for j in range(i + 1, d)),
        "Hermite row reduction",
    )
    prefix_member(rows, rank)
    exponent = sum(rows[i][i].bit_length() - 1 for i in range(d))
    need(
        exponent == sum(index_counts(rank)),
        "basis index is not the full prefix lattice",
    )
    return rows


def canonical(value, basis):
    """Upper-triangular lattice division, including Euclidean signed division."""
    remainder = vector(value, 7)
    need(len(basis) == len(remainder), "validated basis dimension")
    for j in reversed(range(len(remainder))):
        quotient = remainder[j] // basis[j][j]
        for i in range(j + 1):
            remainder[i] -= quotient * basis[i][j]
    need(all(0 <= x < basis[i][i] for i, x in enumerate(remainder)), "residue ranges")
    return remainder


def ideal(value, rank):
    """Independent integer numerator evaluation of U, with exact final division."""
    # A signed Euclidean low-bit split can increase magnitude by one bit.
    result = vector(value, rank, max_bits=MAX_BITS + 1)
    for bit in range(rank):
        for a in range(len(result) // 2):
            if (a >> bit) & 1:
                continue
            b = a ^ (1 << bit)
            ar, ai, br, bi = (
                result[2 * a],
                result[2 * a + 1],
                result[2 * b],
                result[2 * b + 1],
            )
            result[2 * a], result[2 * a + 1] = ar - ai + br + bi, ar + ai - br + bi
            result[2 * b], result[2 * b + 1] = ar + ai + br - bi, -ar + ai + br + bi
    divisor = 1 << rank
    need(all(x % divisor == 0 for x in result), "nonintegral ideal output")
    return [x // divisor for x in result]


def lift(value, rank, inverse=False):
    """Literal floor word, separated from all rational/basis computations."""
    result = vector(value, rank)
    for bit in reversed(range(rank)) if inverse else range(rank):
        for a in range(len(result) // 2):
            if (a >> bit) & 1:
                continue
            b = a ^ (1 << bit)
            dr, di = (
                result[2 * a] - result[2 * b],
                result[2 * a + 1] - result[2 * b + 1],
            )
            sr, si = result[2 * b] + dr // 2, result[2 * b + 1] + di // 2
            dr, di = (di, -dr) if inverse else (-di, dr)
            br, bi = sr - dr // 2, si - di // 2
            result[2 * a], result[2 * a + 1] = br + dr, bi + di
            result[2 * b], result[2 * b + 1] = br, bi
    return result


def split(value, basis):
    """Executable domain reduction, with all extra narrow linear work explicit."""
    original = vector(value, 7)
    small = [x % 16 for x in original]
    remainder = canonical(small, basis)
    wide_shift = [x - s for x, s in zip(original, small, strict=True)]
    narrow_shift = [s - r for s, r in zip(small, remainder, strict=True)]
    wide = ideal(wide_shift, 7)
    correction = ideal(narrow_shift, 7)
    narrow = lift(remainder, 7)
    return [a + b + c for a, b, c in zip(wide, correction, narrow, strict=True)]
