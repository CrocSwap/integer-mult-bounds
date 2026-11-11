#!/usr/bin/env python3
"""Constant pairs after stage-2 E_22 and the stage-2 leaf gate.

In the nine diagonal gates of the #7027 word, place constant F_2 matrices
R and S in the gap after stage-2 E_22 and the gap after the stage-2 leaf
gate. The scalar e is central and e^2 = 0. The nine-gate word ends at that
leaf, so the factor after S is the empty product I. This checker proves
which pairs make the coefficient of e equal the pure product P, counts
that set, and shows the coefficient is never I. Failures raise SystemExit,
so python -O still fails closed.

The 2^40 pairs are not listed. Each of the 64 positions has a two-bit
equation, solved exhaustively, and the equations separate. The count and
the matched positions differ from PR #7287.
"""

from __future__ import annotations

ZERO = frozenset()
ONE = frozenset([(0, 0, 0)])
X = frozenset([(0, 0, 0), (1, 0, 0)])  # 1 + x
Y = frozenset([(0, 0, 0), (0, 1, 0)])  # 1 + y
Z = frozenset([(0, 0, 0), (0, 0, 1)])  # 1 + z
MONO_Z = frozenset([(0, 0, 1)])


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
    """kind 0, 1, 2 are the historical E_11, E_22 and leaf gates."""
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
    require(
        gates[7] == literal_diagonal(tuple(Z if index == 1 else ONE for index in range(8))),
        "stage-2 E_22 does not multiply only coordinate 1 by 1+z",
    )
    require(
        gates[8] == literal_diagonal(tuple(Z if index in (6, 7) else ONE for index in range(8))),
        "stage-2 leaf gate does not multiply coordinates 6 and 7 by 1+z",
    )

    pure = accumulate(gates)
    require(pure == pure_closed_form(), "pure product is not the closed form")
    require(all(entry not in (ZERO, ONE) for entry in pure),
            "a pure diagonal entry is 0 or 1")
    require(matrices_equal(product_of(gates), diagonal_matrix(pure)),
            "matrix product of the nine gates is not the pure diagonal")

    # Slots: after gate index 7 (stage-2 E_22) and after gate index 8
    # (stage-2 leaf). The word ends at index 8, so the suffix after S is empty.
    # PR #7287 uses the slots after indices 4 and 6.
    require(8 < 9, "the two slots are ordered")
    left_r = accumulate(gates[:8])
    middle = accumulate(gates[8:9])
    right_s = accumulate(gates[9:])
    right_r = accumulate(gates[8:])
    left_s = accumulate(gates[:9])
    core = pmul(pmul(X, Y), Z)
    expected_left = (core, core, X, X, Y, Y, ONE, ONE)
    expected_middle = (ONE, ONE, ONE, ONE, ONE, ONE, Z, Z)
    expected_right = (ONE, ONE, ONE, ONE, ONE, ONE, ONE, ONE)
    require(left_r == expected_left,
            "left diagonal is not diag((1+x)(1+y)(1+z), (1+x)(1+y)(1+z), 1+x, 1+x, 1+y, 1+y, 1, 1)")
    require(middle == expected_middle,
            "middle diagonal is not diag(1, 1, 1, 1, 1, 1, 1+z, 1+z)")
    require(right_s == expected_right,
            "the suffix after the leaf gate is not the empty product I")
    require(product_of(()) == diagonal_matrix(expected_right),
            "the empty matrix product is not I")
    for index in range(8):
        require(pmul(left_r[index], pmul(middle[index], right_s[index])) == pure[index],
                "L M T does not recover P")
        require(right_r[index] == pmul(middle[index], right_s[index]),
                "the first right factor is not M T")
        require(left_s[index] == pmul(left_r[index], middle[index]),
                "the second left factor is not L M")
        require(left_r[index] != ZERO and middle[index] != ZERO and right_s[index] != ZERO,
                "a prefix, middle or suffix entry vanished")

    require(padd(ONE, Z) == MONO_Z and MONO_Z != ZERO, "1+(1+z) vanished")
    value_set = {ONE, Z}
    require(set(middle) == value_set, "middle diagonal uses a value outside {1, 1+z}")
    levels = {
        Z: [index for index in range(8) if middle[index] == Z],
        ONE: [index for index in range(8) if middle[index] == ONE],
    }
    require(levels[Z] == [6, 7], "the 1+z level is not coordinates 6 and 7")
    require(levels[ONE] == [0, 1, 2, 3, 4, 5],
            "the 1 level is not coordinates 0, 1, 2, 3, 4, 5")

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
        for group in (levels[Z], levels[ONE])
        for row in group
        for col in group
        if row != col
    ]
    require(
        set(matched) == set(expected_matched) and len(matched) == len(set(expected_matched)),
        "matched positions are not the off-diagonal level-set pairs",
    )
    require(len(matched) == 32 and len(blocked) == 24, "split is not 32 matched and 24 blocked")
    # PR #7287 frees (1, 6) and blocks (1, 4). This middle diagonal reverses that.
    require((1, 4) in matched, "coordinate pair (1, 4) is blocked, but it is free for this slot pair")
    require((0, 1) in matched, "coordinate pair (0, 1) is blocked, but it is free for this slot pair")
    require((6, 7) in matched, "coordinate pair (6, 7) is blocked, but it is free for this slot pair")
    require((1, 6) in blocked, "coordinate pair (1, 6) is free, but it is blocked for this slot pair")
    require((0, 6) in blocked, "coordinate pair (0, 6) is free, but it is blocked for this slot pair")
    predecessor_matched = {
        (row, col)
        for group in ([4, 5], [1, 2, 3, 6, 7])
        for row in group
        for col in group
        if row != col
    }
    require(set(matched) != predecessor_matched,
            "matched positions reproduced the PR #7287 level sets")
    require(len(predecessor_matched) == 22, "the cited PR #7287 matched count is not 22")

    for passed in (8, 9):
        left_diags = gates[:passed]
        right_diags = gates[passed:]
        for row in range(8):
            for col in range(8):
                direct = coefficient(left_diags, bits_matrix({(row, col)}), right_diags)
                expect = [[ZERO] * 8 for _ in range(8)]
                expect[row][col] = scale_entry(
                    accumulate(left_diags), accumulate(right_diags), row, col)
                require(
                    matrices_equal(direct, tuple(tuple(item) for item in expect)),
                    "unit coefficient disagreed with the scale formula",
                )

    unit_sum = bits_matrix({(6, 7), (0, 1)})
    added = coefficient(gates[:8], unit_sum, gates[8:])
    separate = [[ZERO] * 8 for _ in range(8)]
    for row, col in ((6, 7), (0, 1)):
        piece = coefficient(gates[:8], bits_matrix({(row, col)}), gates[8:])
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
    require(choices == 2 ** 40 and free_bits == 40, "solution count is not 2^40")
    require(choices != 2 ** 30, "solution count reproduced the PR #7287 count")
    require(8 + 32 + 24 == 64, "the 64 positions were not partitioned")

    pure_m = diagonal_matrix(pure)
    identity = diagonal_matrix(tuple(ONE for _ in range(8)))

    def pair_coefficient(first_bits, second_bits):
        left = coefficient(gates[:8], first_bits, gates[8:])
        right = coefficient(gates[:9], second_bits, gates[9:])
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
    for entries in ({(6, 7)}, {(0, 1)}, {(6, 7), (7, 6)}):
        both = bits_matrix(entries)
        witness = pair_coefficient(split_with(entries), both)
        require(matrices_equal(witness, pure_m),
                "a both-nonzero level-set witness missed the pure product")
        require(not matrices_equal(witness, identity),
                "a both-nonzero witness produced the identity")
        witnesses += 1
    require(witnesses == 3, "both-nonzero witness count changed")

    blocked_pair = pair_coefficient(split_with({(1, 6)}), bits_matrix({(1, 6)}))
    require(not matrices_equal(blocked_pair, pure_m),
            "blocked pair (1, 6) reproduced the pure product")
    unequal = pair_coefficient(split_with({(6, 7)}), zero)
    require(not matrices_equal(unequal, pure_m),
            "unequal bits on a matched position reproduced the pure product")
    mixed = pair_coefficient(
        split_with({(6, 7), (1, 6)}),
        bits_matrix({(6, 7), (1, 6)}),
    )
    require(not matrices_equal(mixed, pure_m),
            "a matched bit plus a blocked bit reproduced the pure product")

    for row in range(8):
        for first_bit in (0, 1):
            for second_bit in (0, 1):
                require(entry_value(row, row, first_bit, second_bit) != ONE,
                        "a diagonal entry equalled 1")

    print("PASS_STAGE2_E22_LEAF_GAPS")
    print("matched_off_diagonal", len(matched))
    print("blocked_off_diagonal", len(blocked))
    print("level_1_plus_z", len(levels[Z]))
    print("level_one", len(levels[ONE]))
    print("solution_pairs", "2^40")
    print("witness_both_nonzero", witnesses)
    print("coefficient_equals_I", 0)
    print("distinguished_from_stage1_e22_stage2_e11", 1)


if __name__ == "__main__":
    main()
