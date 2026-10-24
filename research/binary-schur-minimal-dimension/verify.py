#!/usr/bin/env python3
"""Exact binary checks for the written minimal-dimension theorem in README.md.

Matrices are tuples of row bitsets: bit j is column j, acting on column vectors.
No predecessor verifier or third-party arithmetic is imported. Finite checks
corroborate, but do not replace, the proof for every d >= 2.
lee-phys, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return tuple(1 << i for i in range(n))


def add(a, b):
    require(len(a) == len(b), "addition row count")
    return tuple(x ^ y for x, y in zip(a, b))


def multiply(a, b):
    result = []
    for row in a:
        total = 0
        while row:
            bit = row & -row
            total ^= b[bit.bit_length() - 1]
            row ^= bit
        result.append(total)
    return tuple(result)


def rank(a):
    pivots = {}
    for row in a:
        while row:
            col = row.bit_length() - 1
            if col not in pivots:
                pivots[col] = row
                break
            row ^= pivots[col]
    return len(pivots)


def inverse(a):
    n = len(a)
    rows = [row | (1 << (n + i)) for i, row in enumerate(a)]
    for col in range(n):
        pivot = next((i for i in range(col, n) if (rows[i] >> col) & 1), None)
        if pivot is None:
            return None
        rows[col], rows[pivot] = rows[pivot], rows[col]
        for i in range(n):
            if i != col and (rows[i] >> col) & 1:
                rows[i] ^= rows[col]
    return tuple(row >> n for row in rows)


def block(a, r0, r1, c0, c1):
    return tuple((row >> c0) & ((1 << (c1 - c0)) - 1) for row in a[r0:r1])


def direct_sum(parts):
    rows, offset = [], 0
    for part in parts:
        rows.extend(row << offset for row in part)
        offset += len(part)
    return tuple(rows)


def join_blocks(grid, d):
    return tuple(sum(part[i] << (j * d) for j, part in enumerate(row))
                 for row in grid for i in range(d))


T2 = (2, 3)  # rows 01, 11; T2^2 + T2 + I = 0
T3 = (4, 5, 2)  # rows 001, 101, 010; T3^3 + T3 + I = 0


def seed(d):
    require(type(d) is int and d >= 2, "seed dimension must be at least two")
    return direct_sum(([T3] if d % 2 else []) + [T2] * ((d - 3) // 2 if d % 2 else d // 2))


def pair_from_t(t):
    d = len(t)
    unit, zero = identity(d), (0,) * d
    a = add(unit, t)
    p = join_blocks(((a, a, t), (t, t, t), (zero, zero, unit)), d)
    q = join_blocks(((a, t, a), (zero, unit, zero), (t, t, t)), d)
    return p, q


def schur(a, d):
    n = len(a)
    pivot_inverse = inverse(block(a, 0, d, 0, d))
    require(pivot_inverse is not None, "singular leading block")
    return add(block(a, d, n, d, n),
               multiply(multiply(block(a, d, n, 0, d), pivot_inverse),
                        block(a, 0, d, d, n)))


def check_pair(p, q, d):
    """Check the stated properties from full matrices, not their construction."""
    n = len(p)
    require(0 < d < n and len(q) == n, "invalid common split")
    require(all(type(row) is int and 0 <= row < 1 << n for row in p + q),
            "invalid binary square matrix")
    require(multiply(p, p) == p, "P is not idempotent")
    require(multiply(q, q) == q, "Q is not idempotent")
    require(multiply(p, q) == multiply(q, p), "P and Q do not commute")
    s, z = schur(p, d), schur(q, d)
    require(multiply(s, s) == s and multiply(z, z) == z, "Schur idempotence")
    require(rank(p) == rank(q) == 2 * d, "projector rank")
    c = add(multiply(s, z), multiply(z, s))
    require(rank(c) == 2 * d, "Schur commutator rank")
    return s, z, c


def check_family(t):
    d = len(t)
    unit, zero = identity(d), (0,) * d
    ai = inverse(add(unit, t))
    require(inverse(t) is not None and ai is not None, "T and I+T must be invertible")
    p, q = pair_from_t(t)
    s, z, c = check_pair(p, q, d)
    r = multiply(t, ai)
    require(s == join_blocks(((zero, r), (zero, unit)), d), "S block formula")
    require(z == join_blocks(((unit, zero), (r, zero)), d), "Z block formula")
    require(add(r, unit) == ai, "R+I inverse identity")
    r2, ri2 = multiply(r, r), multiply(add(r, unit), add(r, unit))
    diagonal = multiply(r2, ri2)
    require(multiply(c, c) == direct_sum((diagonal, diagonal)), "commutator square")
    require(rank(diagonal) == d, "square block invertibility")
    return p, q, c


def parse_rows(rows):
    return tuple(sum(int(bit) << j for j, bit in enumerate(row)) for row in rows)


P9 = parse_rows(("101101001", "111111101", "011011010", "001001001", "101101101",
                 "010010010", "000000100", "000000010", "000000001"))
Q9 = parse_rows(("101001101", "111101111", "011010011", "000100000", "000010000",
                 "000001000", "001001001", "101101101", "010010010"))
C6 = parse_rows(("101111", "111100", "011110", "111101", "100111", "110011"))


def rejection(label, p, q, d, expected):
    try:
        check_pair(p, q, d)
    except ValueError as exc:
        require(str(exc) == expected, label + ": wrong rejection: " + str(exc))
        return label
    raise ValueError(label + ": invalid pair accepted")


def controls():
    p, q = pair_from_t(identity(3))
    rejected = [rejection("singular_pivot", p, q, 3, "singular leading block")]
    p, q = pair_from_t((0, 0, 0))
    rejected.append(rejection("zero_T", p, q, 3, "Schur commutator rank"))
    p, q = pair_from_t(direct_sum((T2, (0,))))
    rejected.append(rejection("nonzero_singular_T", p, q, 3, "Schur commutator rank"))
    rejected.append(rejection("identical_projectors", P9, P9, 3, "Schur commutator rank"))
    damaged = (P9[0] ^ 1,) + P9[1:]
    rejected.append(rejection("broken_idempotence", damaged, Q9, 3, "P is not idempotent"))
    # Conjugate Q alone by the permutation swapping its first two coordinates.
    swap = (2, 1) + identity(9)[2:]
    changed_q = multiply(multiply(swap, Q9), swap)
    require(multiply(changed_q, changed_q) == changed_q, "control remains idempotent")
    require(inverse(block(changed_q, 0, 3, 0, 3)) is not None, "control keeps its pivot")
    rejected.append(rejection("noncommuting_projectors", P9, changed_q, 3,
                              "P and Q do not commute"))
    return rejected


def main():
    require(add(add(multiply(T2, T2), T2), identity(2)) == (0,) * 2, "quadratic seed")
    require(add(add(multiply(multiply(T3, T3), T3), T3), identity(3)) == (0,) * 3,
            "cubic seed")
    require(check_pair(P9, Q9, 3)[2] == C6, "literal d=3 witness")
    require(pair_from_t(T3) == (P9, Q9), "literal and constructed witness agree")

    examples = []
    for d in range(2, 13):
        p, q, c = check_family(seed(d))
        examples.append({"d": d, "n": len(p), "commutator_rank": rank(c)})
    # A zero padding illustrates attainment in every larger ambient dimension.
    check_pair(direct_sum((P9, (0,))), direct_sum((Q9, (0,))), 3)

    exhaustive = {}
    for d in (2, 3):
        accepted = 0
        for bits in range(1 << (d * d)):
            t = tuple((bits >> (i * d)) & ((1 << d) - 1) for i in range(d))
            if inverse(t) is not None and inverse(add(t, identity(d))) is not None:
                check_family(t)
                accepted += 1
        require(accepted == {2: 2, 3: 48}[d], "exhaustive seed count")
        exhaustive[str(d)] = {"all_T": 1 << (d * d), "admissible_T": accepted}
    print(json.dumps({"status": "PASS_BINARY_SCHUR_MINIMAL_DIMENSION",
                      "theorem_scope": "Written proof: n_min(d)=3d for every d>=2 over F2",
                      "finite_examples": examples, "exhaustive_seed_checks": exhaustive,
                      "rejected_controls": controls(), "new_kappa_claimed": False}, indent=2))


if __name__ == "__main__":
    main()
