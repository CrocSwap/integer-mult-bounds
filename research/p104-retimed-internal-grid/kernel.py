"""Exact fixed-grid Gaussian execution and a direct canonical-chart oracle.

Gaussian kernels and canonical chart formulas follow Nick Petalas / PR2772.
This adaptation precompiles wrapper plans and rejects every inexact division.
Apache-2.0. No compiler or predecessor Python implementation is imported.
"""

from fractions import Fraction

N = 512
ZERO = ((0, 0),) * N


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rotate(z, phase):
    a, b = z
    return ((a, b), (-b, a), (-a, -b), (b, -a))[phase % 4]


def plan(record):
    """An affine permutation and a quadratic Z4 phase are a Clifford monomial."""
    need(
        set(record)
        == {"matrix_rows", "offset", "linear_Z4", "quadratic_rows", "phase"},
        "monomial schema",
    )
    rows, linear, quadratic = (
        record[k] for k in ("matrix_rows", "linear_Z4", "quadratic_rows")
    )
    need(len(rows) == len(linear) == len(quadratic) == 9, "monomial dimension")
    need(all(type(x) is int and 0 <= x < N for x in rows + quadratic), "binary rows")
    need(all(type(x) is int and 0 <= x < 4 for x in linear), "linear phase")
    need(type(record["offset"]) is int and 0 <= record["offset"] < N, "offset")
    need(type(record["phase"]) is int and 0 <= record["phase"] < 4, "global phase")
    out = []
    for x in range(N):
        y = record["offset"] ^ sum(
            ((x & row).bit_count() % 2) << j for j, row in enumerate(rows)
        )
        phase = record["phase"]
        for j in range(9):
            if (x >> j) & 1:
                phase += (
                    linear[j]
                    + 2 * (quadratic[j] & x & ~((1 << (j + 1)) - 1)).bit_count()
                )
        out.append((y, phase % 4))
    need(sorted(y for y, _ in out) == list(range(N)), "monomial bijection")
    return tuple(out)


def permute(vector, mapping):
    out = list(ZERO)
    for x, (y, phase) in enumerate(mapping):
        out[y] = rotate(vector[x], phase)
    return tuple(out)


def c_stage(vector, bit, sign=1):
    """Write complete disjoint pairs only after both exact divisions succeed."""
    out = list(vector)
    for x in range(N):
        if x & (1 << bit):
            continue
        y = x ^ (1 << bit)
        a, b = vector[x]
        c, d = vector[y]
        numerators = (
            a - sign * b + c + sign * d,
            b + sign * a + d - sign * c,
            a + sign * b + c - sign * d,
            b - sign * a + d + sign * c,
        )
        need(all(v % 2 == 0 for v in numerators), "inexact internal halving")
        p, q, r, s = (v // 2 for v in numerators)
        out[x], out[y] = (p, q), (r, s)
    return tuple(out)


def native(vector, recipe):
    if vector == ZERO:
        return vector
    rank, left, right = recipe
    vector = permute(vector, right)
    for bit in range(rank):
        vector = c_stage(vector, bit)
    return permute(vector, left)


def add(target, source, coefficient):
    c = Fraction(coefficient)
    out = []
    for (a, b), (x, y) in zip(target, source, strict=True):
        u, v = x * c.numerator, y * c.numerator
        need(u % c.denominator == v % c.denominator == 0, "inexact scalar product")
        out.append((a + u // c.denominator, b + v // c.denominator))
    return tuple(out)


def canonical(frame):
    """Canonical Gamma chart directly from its binary basis, not a native recipe."""
    columns, span = [], {0}
    for value in tuple(frame) + tuple(1 << j for j in range(9)):
        if value not in span:
            columns.append(value)
            span |= {x ^ value for x in span}
    need(len(columns) == 9, "canonical basis")
    permutation = []
    for x in range(N):
        y = 0
        for j, value in enumerate(columns):
            if (x >> j) & 1:
                y ^= value
        permutation.append(y)
    inverse = [0] * N
    for x, y in enumerate(permutation):
        inverse[y] = x
    basis = [inverse[1 << j] for j in range(9)]
    quadratic = [
        (1 << i) ^ sum(((a & b).bit_count() % 2) << j for j, b in enumerate(basis))
        for i, a in enumerate(basis)
    ]
    phases = []
    for x in range(N):
        phase = sum((quadratic[j] >> j) & 1 for j in range(9) if (x >> j) & 1)
        phase += 2 * sum(
            (quadratic[j] & x & ~((1 << (j + 1)) - 1)).bit_count()
            for j in range(9)
            if (x >> j) & 1
        )
        phases.append(phase % 4)
    return tuple(permutation), tuple(inverse), tuple(phases)


def chart(vector, frame, inverse=False):
    if vector == ZERO or not frame:
        return vector
    if len(frame) != 9:
        p, inv, phase = canonical(frame)
        vector = permute(vector, tuple((inv[x], phase[x]) for x in range(N)))
    for bit in range(len(frame)):
        vector = c_stage(vector, bit, 1 if inverse else -1)
    if len(frame) != 9:
        vector = permute(vector, tuple((p[x], -phase[p[x]]) for x in range(N)))
    return vector
