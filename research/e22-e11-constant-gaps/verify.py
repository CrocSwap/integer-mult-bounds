#!/usr/bin/env python3
"""Constant pairs after stage-0 E_22 and stage-1 E_11.

In the nine diagonal gates of the #7027 word, place constant F_2 matrices
R and S in the gap after stage-0 E_22 and the gap after stage-1 E_11.
The scalar e is central and e^2 = 0. This checker proves which pairs make
the coefficient of e equal the pure product P, counts that set, and shows
the coefficient is never I. Failures raise SystemExit, so python -O still
fails closed.

The 2^30 pairs are not listed. Each of the 64 positions has a two-bit
equation, solved exhaustively, and the equations separate.
"""

from __future__ import annotations

ZERO = frozenset()
ONE = frozenset([(0, 0, 0)])
X = frozenset([(0, 0, 0), (1, 0, 0)])  # 1 + x
Y = frozenset([(0, 0, 0), (0, 1, 0)])  # 1 + y
Z = frozenset([(0, 0, 0), (0, 0, 1)])  # 1 + z
MONO_X = frozenset([(1, 0, 0)])
MONO_Y = frozenset([(0, 1, 0)])
MONO_X_PLUS_Y = frozenset([(1, 0, 0), (0, 1, 0)])


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
    """kind 0, 1, 2 are the historical E_11, E_22 and E_33+E_44 gates."""
    leaf = 2 * (stage + 1)
    if kind == 0:
        positions = (0,)
    elif kind == 1:
        positions = (1,)
    elif kind == 2:
        positions = (leaf, leaf + 1)
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
    return (core, core, X, X, Y, Y, Z, Z)


def literal_diagonal(spec):
    return tuple(spec[index] for index in range(8))


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


def bits_matrix(entries):
    rows = []
    for row in range(8):
        value = 0
        for col in range(8):
            if (row, col) in entries:
                value |= 1 << col
        rows.append(value)
    return tuple(rows)


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


def matrices_equal(left, right):
    return all(left[i][j] == right[i][j] for i in range(8) for j in range(8))


def scale_entry(left, right, row, col):
    return pmul(left[row], right[col])


def eye_bits():
    return bits_matrix({(index, index) for index in range(8)})


def main():
    gates = nine_diagonals()
    # Literal supports, independent of the kind index inside gate_diagonal.
    require(
        gates[1] == literal_diagonal(tuple(X if index == 1 else ONE for index in range(8))),
        "stage-0 E_22 does not multiply only coordinate 1 by 1+x",
    )
    require(
        gates[2] == literal_diagonal(tuple(X if index in (2, 3) else ONE for index in range(8))),
        "stage-0 leaf gate does not multiply coordinates 2 and 3 by 1+x",
    )
    require(
        gates[3] == literal_diagonal(tuple(Y if index == 0 else ONE for index in range(8))),
        "stage-1 E_11 does not multiply only coordinate 0 by 1+y",
    )
    require(gates[0][0] == X and all(gates[0][index] == ONE for index in range(1, 8)),
            "stage-0 E_11 does not multiply only coordinate 0 by 1+x")

    pure = accumulate(gates)
    require(pure == pure_closed_form(), "pure product is not the closed form")
    require(all(entry not in (ZERO, ONE) for entry in pure),
            "a pure diagonal entry is 0 or 1")
    require(matrices_equal(product_of(gates), diagonal_matrix(pure)),
            "matrix product of the nine gates is not the pure diagonal")

    # Slots: after the 2nd gate (stage-0 E_22) and after the 4th (stage-1 E_11).
    # PR #7103 uses the slots after the 1st and 2nd gates.
    require(2 < 4, "the two slots are ordered")
    left_r = accumulate(gates[:2])
    middle = accumulate(gates[2:4])
    right_s = accumulate(gates[4:])
    right_r = accumulate(gates[2:])
    left_s = accumulate(gates[:4])
    expected_middle = (Y, ONE, X, X, ONE, ONE, ONE, ONE)
    require(middle == expected_middle, "middle diagonal is not diag(1+y, 1, 1+x, 1+x, 1, 1, 1, 1)")
    for index in range(8):
        require(pmul(left_r[index], pmul(middle[index], right_s[index])) == pure[index],
                "L M T does not recover P")
        require(right_r[index] == pmul(middle[index], right_s[index]),
                "the first right factor is not M T")
        require(left_s[index] == pmul(left_r[index], middle[index]),
                "the second left factor is not L M")
        require(left_r[index] != ZERO and right_s[index] != ZERO and middle[index] != ZERO,
                "a prefix, middle or suffix entry vanished")

    # Distinct middle values are pairwise nonzero under addition.
    require(padd(ONE, X) == MONO_X and padd(ONE, Y) == MONO_Y, "1+(1+x) or 1+(1+y) vanished")
    require(padd(X, Y) == MONO_X_PLUS_Y and MONO_X_PLUS_Y != ZERO, " (1+x)+(1+y) vanished")
    value_set = {ONE, X, Y}
    require(set(middle) == value_set, "middle diagonal uses a value outside {1, 1+x, 1+y}")
    levels = {
        Y: [index for index in range(8) if middle[index] == Y],
        X: [index for index in range(8) if middle[index] == X],
        ONE: [index for index in range(8) if middle[index] == ONE],
    }
    require(levels[Y] == [0], "the 1+y level is not coordinate 0")
    require(levels[X] == [2, 3], "the 1+x level is not coordinates 2 and 3")
    require(levels[ONE] == [1, 4, 5, 6, 7], "the 1 level is not coordinates 1, 4, 5, 6, 7")

    matched = []
    blocked = []
    for row in range(8):
        for col in range(8):
            common = pmul(left_r[row], right_s[col])
            first = scale_entry(left_r, right_r, row, col)
            second = scale_entry(left_s, right_s, row, col)
            require(common != ZERO, "the cancelled factor c_ij vanished")
            require(first == pmul(common, middle[col]), "a_ij is not c_ij M_j")
            require(second == pmul(common, middle[row]), "b_ij is not c_ij M_i")
            require((first == second) == (middle[row] == middle[col]),
                    "scale equality is not middle-diagonal equality")
            require(first != ZERO and second != ZERO, "a gap scale vanished")
            if row == col:
                require(first == pure[row] == second, "diagonal scale is not P_ii")
                continue
            if middle[row] == middle[col]:
                matched.append((row, col))
            else:
                blocked.append((row, col))
                require(padd(first, second) != ZERO, "distinct middle values became equal scales")

    expected_matched = [
        (row, col)
        for group in (levels[X], levels[ONE])
        for row in group
        for col in group
        if row != col
    ]
    require(
        set(matched) == set(expected_matched) and len(matched) == len(set(expected_matched)),
        "matched positions are not the off-diagonal level-set pairs",
    )
    require(len(matched) == 22 and len(blocked) == 34, "split is not 22 matched and 34 blocked")
    require((0, 2) in blocked, "coordinate pair (0, 2) is free, but it is blocked for this slot pair")
    require((1, 4) in matched, "coordinate pair (1, 4) is blocked, but it is free for this slot pair")
    require(len(matched) != 42, "this split reproduced the #7103 count")

    # Every matrix unit's direct product agrees with the scale formula.
    for passed, left_diag, right_diag in (
        (2, left_r, right_r),
        (4, left_s, right_s),
    ):
        left_diags = gates[:passed]
        right_diags = gates[passed:]
        for row in range(8):
            for col in range(8):
                direct = coefficient(left_diags, bits_matrix({(row, col)}), right_diags)
                expect = [[ZERO] * 8 for _ in range(8)]
                expect[row][col] = scale_entry(left_diag, right_diag, row, col)
                require(
                    matrices_equal(direct, tuple(tuple(item) for item in expect)),
                    "unit coefficient disagreed with the scale formula",
                )

    unit_sum = bits_matrix({(1, 4), (2, 3)})
    added = coefficient(gates[:2], unit_sum, gates[2:])
    separate = [[ZERO] * 8 for _ in range(8)]
    for row, col in ((1, 4), (2, 3)):
        piece = coefficient(gates[:2], bits_matrix({(row, col)}), gates[2:])
        for i in range(8):
            for j in range(8):
                separate[i][j] = padd(separate[i][j], piece[i][j])
    require(matrices_equal(added, tuple(tuple(item) for item in separate)),
            "coefficient map is not additive on a two-unit sum")

    def entry_value(row, col, first_bit, second_bit):
        value = ZERO
        if first_bit:
            value = padd(value, scale_entry(left_r, right_r, row, col))
        if second_bit:
            value = padd(value, scale_entry(left_s, right_s, row, col))
        return value

    def predicted(row, col):
        if row == col:
            return {(1, 0), (0, 1)}
        if middle[row] == middle[col]:
            return {(0, 0), (1, 1)}
        return {(0, 0)}

    choices = 1
    free_bits = 0
    for row in range(8):
        for col in range(8):
            target = pure[row] if row == col else ZERO
            found = set()
            for first_bit in (0, 1):
                for second_bit in (0, 1):
                    value = entry_value(row, col, first_bit, second_bit)
                    if row == col:
                        require(value in (ZERO, pure[row]),
                                "a diagonal coefficient left {0, P_ii}")
                    if value == target:
                        found.add((first_bit, second_bit))
            require(found == predicted(row, col),
                    "scalar solutions disagreed with the middle-diagonal rule")
            choices *= len(found)
            if len(found) == 2:
                free_bits += 1
            else:
                require(len(found) == 1, "a position had neither one nor two solutions")
    require(choices == 2 ** 30 and free_bits == 30, "solution count is not 2^30")
    require(8 + 22 + 34 == 64, "the 64 positions were not partitioned")

    pure_m = diagonal_matrix(pure)
    identity = diagonal_matrix(tuple(ONE for _ in range(8)))

    def pair_coefficient(first_bits, second_bits):
        left = coefficient(gates[:2], first_bits, gates[2:])
        right = coefficient(gates[:4], second_bits, gates[4:])
        return tuple(
            tuple(padd(left[i][j], right[i][j]) for j in range(8))
            for i in range(8)
        )

    eye = eye_bits()
    zero = bits_matrix(set())
    require(matrices_equal(pair_coefficient(eye, zero), pure_m),
            "(I, 0) does not reproduce the pure product")
    require(matrices_equal(pair_coefficient(zero, eye), pure_m),
            "(0, I) does not reproduce the pure product")
    require(not matrices_equal(pair_coefficient(eye, eye), pure_m),
            "(I, I) reproduced the pure product")
    require(not matrices_equal(pair_coefficient(eye, zero), identity),
            "(I, 0) reproduced the identity")

    def split_with(entries):
        return bits_matrix({(index, index) for index in range(8)} | set(entries))

    witnesses = 0
    for entries in ({(1, 4)}, {(2, 3)}, {(1, 4), (4, 1)}):
        both = bits_matrix(entries)
        witness = pair_coefficient(split_with(entries), both)
        require(matrices_equal(witness, pure_m),
                "a both-nonzero level-set witness missed the pure product")
        require(not matrices_equal(witness, identity),
                "a both-nonzero witness produced the identity")
        witnesses += 1
    require(witnesses == 3, "both-nonzero witness count changed")

    blocked_pair = pair_coefficient(split_with({(0, 2)}), bits_matrix({(0, 2)}))
    require(not matrices_equal(blocked_pair, pure_m),
            "blocked pair (0, 2) reproduced the pure product")
    unequal = pair_coefficient(split_with({(1, 4)}), zero)
    require(not matrices_equal(unequal, pure_m),
            "unequal bits on a matched position reproduced the pure product")
    mixed = pair_coefficient(
        split_with({(1, 4), (0, 2)}),
        bits_matrix({(1, 4), (0, 2)}),
    )
    require(not matrices_equal(mixed, pure_m),
            "a matched bit plus a blocked bit reproduced the pure product")

    # Every constant pair has diagonal entries in {0, P_ii}, hence none equals I.
    for row in range(8):
        for first_bit in (0, 1):
            for second_bit in (0, 1):
                require(entry_value(row, row, first_bit, second_bit) != ONE,
                        "a diagonal entry equalled 1")

    print("PASS_E22_E11_CONSTANT_GAPS")
    print("matched_off_diagonal", len(matched))
    print("blocked_off_diagonal", len(blocked))
    print("level_1_plus_y", len(levels[Y]))
    print("level_1_plus_x", len(levels[X]))
    print("level_one", len(levels[ONE]))
    print("solution_pairs", "2^30")
    print("witness_both_nonzero", witnesses)
    print("coefficient_equals_I", 0)
    print("distinguished_from_stage0_adjacent_pair", 1)


if __name__ == "__main__":
    main()
