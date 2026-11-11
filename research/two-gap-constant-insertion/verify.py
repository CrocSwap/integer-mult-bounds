#!/usr/bin/env python3
"""Two constant insertions after the stage-0 gates E_11 and E_22.

The nine diagonal gates of the #7027 word multiply to the pure product P.
Constant matrices R and S may be inserted in the two gaps immediately after
the stage-0 factors I + x E_11 and I + x E_22. The scalar e is central and
e^2 = 0. This checker proves which pairs make the coefficient of e equal P,
counts that set, and shows the coefficient is never I. Failures raise
SystemExit, so python -O still fails closed.
"""

from __future__ import annotations

# Polynomials are frozensets of exponent triples over F_2[x, y, z].
ZERO = frozenset()
ONE = frozenset([(0, 0, 0)])
X = frozenset([(0, 0, 0), (1, 0, 0)])
Y = frozenset([(0, 0, 0), (0, 1, 0)])
Z = frozenset([(0, 0, 0), (0, 0, 1)])
MONO_X = frozenset([(1, 0, 0)])


def fail(message):
    raise SystemExit("FAIL: " + message)


def require(ok, message):
    if not ok:
        fail(message)


def padd(left, right):
    return (left - right) | (right - left)


def pmul(left, right):
    if not left or not right:
        return ZERO
    out = set()
    for a, b, c in left:
        for d, e, f in right:
            term = (a + d, b + e, c + f)
            if term in out:
                out.remove(term)
            else:
                out.add(term)
    return frozenset(out)


def stage_shift(stage):
    return (X, Y, Z)[stage]


def gate_diagonal(stage, kind):
    """Diagonal of one stage gate. kind 0, 1, 2 are E_11, E_22, E_33+E_44."""
    leaf = 2 * (stage + 1)
    coords = (0, 1, leaf, leaf + 1)
    if kind == 0:
        positions = (coords[0],)
    elif kind == 1:
        positions = (coords[1],)
    elif kind == 2:
        positions = (coords[2], coords[3])
    else:
        fail("unknown gate kind")
    factor = stage_shift(stage)
    return tuple(factor if index in positions else ONE for index in range(8))


def nine_diagonals():
    gates = tuple(
        gate_diagonal(stage, kind) for stage in range(3) for kind in range(3)
    )
    require(len(gates) == 9, "nine gates")
    return gates


def accumulate(gates):
    acc = [ONE] * 8
    for gate in gates:
        acc = [pmul(acc[index], gate[index]) for index in range(8)]
    return tuple(acc)


def pure_closed_form():
    core = pmul(pmul(X, Y), Z)
    return (
        core,
        core,
        X,
        X,
        Y,
        Y,
        Z,
        Z,
    )


def scales(gates, passed):
    """Left and right diagonal scales for the gap after `passed` gates."""
    return accumulate(gates[:passed]), accumulate(gates[passed:])


def scale_entry(left, right, row, col):
    return pmul(left[row], right[col])


def bits_matrix(entries):
    rows = []
    for row in range(8):
        value = 0
        for col in range(8):
            if (row, col) in entries:
                value |= 1 << col
        rows.append(value)
    return tuple(rows)


def eye_bits():
    return bits_matrix({(index, index) for index in range(8)})


def matmul(left, right):
    out = [[ZERO] * 8 for _ in range(8)]
    for i in range(8):
        for k in range(8):
            factor = left[i][k]
            if not factor:
                continue
            source = right[k]
            dest = out[i]
            for j in range(8):
                if source[j]:
                    dest[j] = padd(dest[j], pmul(factor, source[j]))
    return tuple(tuple(row) for row in out)


def diagonal_matrix(diag):
    return tuple(
        tuple(diag[i] if i == j else ZERO for j in range(8)) for i in range(8)
    )


def constant_matrix(bits):
    return tuple(
        tuple(ONE if (bits[i] >> j) & 1 else ZERO for j in range(8))
        for i in range(8)
    )


def product_of(diags):
    acc = diagonal_matrix(tuple(ONE for _ in range(8)))
    for diag in diags:
        acc = matmul(acc, diagonal_matrix(diag))
    return acc


def coefficient(left_diags, bits, right_diags):
    return matmul(
        matmul(product_of(left_diags), constant_matrix(bits)),
        product_of(right_diags),
    )


def pure_matrix(diag):
    return diagonal_matrix(diag)


def matrices_equal(left, right):
    return all(
        left[i][j] == right[i][j] for i in range(8) for j in range(8)
    )


def is_zero_bits(bits):
    return all(row == 0 for row in bits)


def classify(first, second):
    """Return forced and free off-diagonal positions for the two gaps."""
    matched = []
    blocked = []
    for row in range(8):
        for col in range(8):
            if row == col:
                continue
            left = scale_entry(first[0], first[1], row, col)
            right = scale_entry(second[0], second[1], row, col)
            require(left != ZERO and right != ZERO, "a gap scale vanished")
            if left == right:
                matched.append((row, col))
            else:
                blocked.append((row, col))
    return matched, blocked


def admits(row, col, first_bit, second_bit, matched):
    if row == col:
        return first_bit ^ second_bit == 1
    if (row, col) in matched:
        return first_bit == second_bit
    return first_bit == 0 and second_bit == 0


def main():
    gates = nine_diagonals()
    pure = accumulate(gates)
    require(pure == pure_closed_form(), "pure product is not the closed form")
    require(all(entry not in (ZERO, ONE) for entry in pure),
            "a pure diagonal entry is 0 or 1")
    # Stage-0 E_22 is the second gate and moves only coordinate 1.
    require(gates[1] == tuple(X if index == 1 else ONE for index in range(8)),
            "stage-0 E_22 is not the coordinate-1 factor")

    first = scales(gates, 1)
    second = scales(gates, 2)
    for gap in (first, second):
        for index in range(8):
            require(scale_entry(gap[0], gap[1], index, index) == pure[index],
                    "diagonal scale is not the pure entry")

    matched, blocked = classify(first, second)
    require(len(matched) == 42 and len(blocked) == 14,
            "off-diagonal split is not 42 matched and 14 blocked")
    require(
        blocked == [(row, col) for row in range(8) for col in range(8)
                    if row != col and (row == 1 or col == 1)],
        "blocked positions are not exactly the pairs that meet coordinate 1",
    )
    for row, col in matched:
        left = scale_entry(first[0], first[1], row, col)
        right = scale_entry(second[0], second[1], row, col)
        require(left == right, "matched scales disagreed")
    for row, col in blocked:
        left = scale_entry(first[0], first[1], row, col)
        right = scale_entry(second[0], second[1], row, col)
        if row == 1:
            require(right == pmul(left, X), "row-1 scale was not multiplied by 1+x")
        else:
            require(col == 1 and left == pmul(right, X),
                    "column-1 scale was not multiplied by 1+x")
        require(pmul(left, MONO_X) != ZERO and left != right,
                "distinct scales became linearly dependent")

    # Every matrix unit's direct product agrees with the scale formula.
    for passed, gap in ((1, first), (2, second)):
        left_diags = gates[:passed]
        right_diags = gates[passed:]
        for row in range(8):
            for col in range(8):
                direct = coefficient(left_diags, bits_matrix({(row, col)}), right_diags)
                expect = [[ZERO] * 8 for _ in range(8)]
                expect[row][col] = scale_entry(gap[0], gap[1], row, col)
                require(matrices_equal(direct, tuple(tuple(item) for item in expect)),
                        "unit coefficient disagreed with the scale formula")
    # Linearity: the coefficient of a sum is the sum of the coefficients.
    unit_sum = bits_matrix({(0, 0), (0, 2)})
    added = coefficient(gates[:1], unit_sum, gates[1:])
    separate = [[ZERO] * 8 for _ in range(8)]
    for row, col in ((0, 0), (0, 2)):
        piece = coefficient(gates[:1], bits_matrix({(row, col)}), gates[1:])
        for i in range(8):
            for j in range(8):
                separate[i][j] = padd(separate[i][j], piece[i][j])
    require(matrices_equal(added, tuple(tuple(item) for item in separate)),
            "coefficient map is not linear on a two-unit sum")

    pure_m = pure_matrix(pure)
    identity = pure_matrix(tuple(ONE for _ in range(8)))

    def pair_coefficient(first_bits, second_bits):
        left = coefficient(gates[:1], first_bits, gates[1:])
        right = coefficient(gates[:2], second_bits, gates[2:])
        return tuple(
            tuple(padd(left[i][j], right[i][j]) for j in range(8)) for i in range(8)
        )

    eye = eye_bits()
    zero = bits_matrix(set())
    require(matrices_equal(pair_coefficient(eye, zero), pure_m),
            "(I, 0) does not reproduce the pure product")
    require(matrices_equal(pair_coefficient(zero, eye), pure_m),
            "(0, I) does not reproduce the pure product")
    require(not matrices_equal(pair_coefficient(eye, eye), pure_m),
            "two identities reproduced the pure product")
    require(not matrices_equal(pair_coefficient(eye, zero), identity),
            "(I, 0) reproduced the identity")

    both = bits_matrix({(0, 2)})
    split = bits_matrix({(index, index) for index in range(8)} | {(0, 2)})
    require(not is_zero_bits(split) and not is_zero_bits(both),
            "the both-nonzero witness collapsed")
    witness = pair_coefficient(split, both)
    require(matrices_equal(witness, pure_m),
            "the both-nonzero witness missed the pure product")
    require(not matrices_equal(witness, identity),
            "the both-nonzero witness produced the identity")

    blocked_bits = bits_matrix({(0, 1)})
    blocked_pair = pair_coefficient(eye, blocked_bits)
    # Diagonal of eye plus a zero diagonal is legal, but (0, 1) is blocked.
    # Put the off-diagonal on both matrices and keep a legal diagonal split.
    illegal = pair_coefficient(
        bits_matrix({(index, index) for index in range(8)} | {(0, 1)}),
        bits_matrix({(0, 1)}),
    )
    require(not matrices_equal(illegal, pure_m),
            "a coordinate-1 off-diagonal pair reproduced the pure product")
    require(not matrices_equal(blocked_pair, pure_m),
            "one blocked off-diagonal with only one diagonal identity worked")

    # Spot-check one accepted free choice and one rejected choice in each
    # off-diagonal family. Necessity for every pair is the scale identity
    # above, not this sample.
    for row, col in ((2, 3), (0, 2), (4, 7)):
        require((row, col) in matched, "expected a matched position")
        accepted = pair_coefficient(
            bits_matrix({(index, index) for index in range(8)} | {(row, col)}),
            bits_matrix({(row, col)}),
        )
        rejected = pair_coefficient(
            bits_matrix({(index, index) for index in range(8)} | {(row, col)}),
            zero,
        )
        require(matrices_equal(accepted, pure_m), "matched bits were rejected")
        require(not matrices_equal(rejected, pure_m), "unequal matched bits passed")
    for row, col in ((1, 2), (0, 1), (3, 1)):
        require((row, col) in blocked, "expected a blocked position")
        rejected = pair_coefficient(
            bits_matrix({(index, index) for index in range(8)} | {(row, col)}),
            bits_matrix({(row, col)}),
        )
        require(not matrices_equal(rejected, pure_m), "blocked bits were accepted")

    solution_bits = 8 + len(matched)
    require(solution_bits == 50, "solution count is not 2^50")
    require(8 + 42 + 14 == 64, "the 64 matrix positions were not partitioned")
    for row in range(8):
        for col in range(8):
            require(
                admits(row, col, 1, 0, set(matched)) == (row == col),
                "the single identity is not admitted exactly on the diagonal",
            )

    print("PASS_TWO_GAP_CONSTANT_INSERTION")
    print("matched_off_diagonal", len(matched))
    print("blocked_off_diagonal", len(blocked))
    print("solution_pairs", "2^50")
    print("witness_both_nonzero", 1)
    print("coefficient_equals_I", 0)


if __name__ == "__main__":
    main()
