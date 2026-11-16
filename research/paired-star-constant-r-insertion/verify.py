#!/usr/bin/env python3
"""Constant insertion beside the exhibited valuation-1 factor.

The nine diagonal gates of the #7027 idempotent triple multiply to
product_j (I + x_j E_j). Inserting I + e R beside the stage-0 factor
I + x E_11, with e^2 = 0 and e central, keeps that pure product. No matrix
R with entries in F_2[x, y, z] makes the coefficient of e equal to I.
The only such matrix that makes the coefficient equal the pure product is
R = I. Every constant matrix supported on the stage-0 block fails both
equations. Failures raise SystemExit, so python -O still fails closed.
"""

from __future__ import annotations

ONE = 1
MONO = (1 << 1, 1 << 3, 1 << 9)
SHIFT = (ONE ^ MONO[0], ONE ^ MONO[1], ONE ^ MONO[2])
LOCAL = ((1, 0, 0, 0), (0, 2, 0, 0), (0, 0, 4, 8))
IDENTITY4 = 1 | (2 << 4) | (4 << 8) | (8 << 12)


def fail(message):
    raise SystemExit("FAIL: " + message)


def require(ok, message):
    if not ok:
        fail(message)


def mul_table():
    table = [0] * (27 * 27)
    for left in range(27):
        a0, a1, a2 = left % 3, (left // 3) % 3, left // 9
        for right in range(27):
            b0, b1, b2 = right % 3, (right // 3) % 3, right // 9
            c0, c1, c2 = a0 + b0, a1 + b1, a2 + b2
            if c0 < 3 and c1 < 3 and c2 < 3:
                table[left * 27 + right] = 1 << (c0 + 3 * c1 + 9 * c2)
            else:
                table[left * 27 + right] = -1
    return table


MUL = mul_table()


def pmul(left, right):
    out = 0
    rest = left
    while rest:
        bit = rest & -rest
        row = (bit.bit_length() - 1) * 27
        other = right
        while other:
            obit = other & -other
            term = MUL[row + obit.bit_length() - 1]
            if term < 0:
                fail("polynomial degree escaped the checked bound")
            out ^= term
            other ^= obit
        rest ^= bit
    return out


def evaluate(poly, x, y, z):
    total = 0
    for a in range(3):
        for b in range(3):
            for c in range(3):
                if (poly >> (a + 3 * b + 9 * c)) & 1:
                    if (a == 0 or x == 1) and (b == 0 or y == 1) and (c == 0 or z == 1):
                        total ^= 1
    return total


def stage_coords(stage):
    leaf = 2 * (stage + 1)
    return (0, 1, leaf, leaf + 1)


def diagonal_gate(positions, variable):
    mono = MONO[variable]
    rows = []
    for i in range(8):
        row = []
        for j in range(8):
            if i != j:
                row.append(0)
            else:
                row.append((ONE ^ mono) if i in positions else ONE)
        rows.append(tuple(row))
    return tuple(rows)


def embed(rows, stage):
    coords = stage_coords(stage)
    out = [0] * 8
    for i in range(4):
        for j in range(4):
            if (rows[i] >> j) & 1:
                out[coords[i]] |= 1 << coords[j]
    return tuple(out)


def gate_from_bits(bit_rows, variable):
    mono = MONO[variable]
    rows = []
    for i in range(8):
        row = []
        for j in range(8):
            poly = ONE if i == j else 0
            if (bit_rows[i] >> j) & 1:
                poly ^= mono
            row.append(poly)
        rows.append(tuple(row))
    return tuple(rows)


def nine_gates():
    gates = []
    for stage in range(3):
        coords = stage_coords(stage)
        for local in LOCAL:
            positions = []
            embedded = embed(local, stage)
            for row in range(4):
                for col in range(4):
                    if (local[row] >> col) & 1:
                        positions.append(coords[row])
            built = diagonal_gate(tuple(positions), stage)
            require(built == gate_from_bits(embedded, stage), "bit embedding disagreed")
            gates.append(built)
    require(len(gates) == 9, "nine gates")
    return tuple(gates)


def is_diagonal(matrix):
    return all(matrix[i][j] == 0 for i in range(8) for j in range(8) if i != j)


def diagonal_entries(matrix):
    require(is_diagonal(matrix), "expected a diagonal gate")
    return tuple(matrix[i][i] for i in range(8))


def matmul(left, right):
    out = [[0] * 8 for _ in range(8)]
    for i in range(8):
        for k in range(8):
            factor = left[i][k]
            if not factor:
                continue
            source = right[k]
            dest = out[i]
            for j in range(8):
                if source[j]:
                    dest[j] ^= pmul(factor, source[j])
    return tuple(tuple(row) for row in out)


def add_mat(left, right):
    return tuple(tuple(left[i][j] ^ right[i][j] for j in range(8)) for i in range(8))


def zero_matrix():
    return tuple(tuple(0 for _ in range(8)) for _ in range(8))


def eye_matrix():
    return tuple(tuple(ONE if i == j else 0 for j in range(8)) for i in range(8))


def unit_matrix(row, col):
    return tuple(tuple(ONE if i == row and j == col else 0 for j in range(8)) for i in range(8))


def multiply_all(factors):
    acc = factors[0]
    for factor in factors[1:]:
        acc = matmul(acc, factor)
    return acc


def expected_pure():
    core = pmul(pmul(SHIFT[0], SHIFT[1]), SHIFT[2])
    entries = []
    for index in range(8):
        if index < 2:
            entries.append(core)
        elif index < 4:
            entries.append(SHIFT[0])
        elif index < 6:
            entries.append(SHIFT[1])
        else:
            entries.append(SHIFT[2])
    return tuple(entries)


def support_gates():
    return tuple(diagonal_gate(stage_coords(stage), stage) for stage in range(3))


def scales(gates, index, side):
    if side == "right":
        left, right = gates[: index + 1], gates[index + 1 :]
    elif side == "left":
        left, right = gates[:index], gates[index:]
    else:
        fail("unknown side")
    row = [ONE] * 8
    for gate in left:
        diag = diagonal_entries(gate)
        row = [pmul(row[i], diag[i]) for i in range(8)]
    col = [ONE] * 8
    for gate in right:
        diag = diagonal_entries(gate)
        col = [pmul(col[i], diag[i]) for i in range(8)]
    return tuple(row), tuple(col)


def coefficient_entry(row_scale, col_scale, i, j, bit):
    if not bit:
        return 0
    return pmul(row_scale[i], col_scale[j])


def matrix_from_scales(row_scale, col_scale, bits):
    rows = []
    for i in range(8):
        row = []
        for j in range(8):
            row.append(coefficient_entry(row_scale, col_scale, i, j, (bits[i] >> j) & 1))
        rows.append(tuple(row))
    return tuple(rows)


def constant_bits(matrix):
    rows = []
    for i in range(8):
        value = 0
        for j in range(8):
            entry = matrix[i][j]
            if entry == ONE:
                value |= 1 << j
            elif entry != 0:
                return None
        rows.append(value)
    return tuple(rows)


def affine_mul(left, right):
    pure = matmul(left[0], right[0])
    coeff = add_mat(matmul(left[0], right[1]), matmul(left[1], right[0]))
    return pure, coeff


def as_pure(gate):
    return gate, zero_matrix()


def as_insertion(constant):
    return eye_matrix(), constant


def multiply_affine(factors):
    acc = factors[0]
    for factor in factors[1:]:
        acc = affine_mul(acc, factor)
    return acc


def insert(gates, index, side, constant):
    pure = [as_pure(gate) for gate in gates]
    insertion = as_insertion(constant)
    if side == "right":
        pure.insert(index + 1, insertion)
    else:
        pure.insert(index, insertion)
    return multiply_affine(tuple(pure))


def block_bits(code):
    rows = [0] * 8
    for local in range(4):
        nibble = (code >> (4 * local)) & 15
        rows[local] = nibble
    return tuple(rows)


def matches(row_scale, col_scale, bits, target_diag, identity):
    for i in range(8):
        for j in range(8):
            actual = coefficient_entry(row_scale, col_scale, i, j, (bits[i] >> j) & 1)
            if identity:
                expected = ONE if i == j else 0
            else:
                expected = target_diag[i] if i == j else 0
            if actual != expected:
                return False
    return True


def census(row_scale, col_scale, target_diag):
    identity_hits = []
    pure_hits = []
    for code in range(65536):
        bits = block_bits(code)
        if matches(row_scale, col_scale, bits, target_diag, True):
            identity_hits.append(code)
        if matches(row_scale, col_scale, bits, target_diag, False):
            pure_hits.append(code)
    return identity_hits, pure_hits


def local_scales(side):
    # Stage-0 gates A, B, C in that order. Slots beside A are the assigned ones.
    d1 = (SHIFT[0], ONE, ONE, ONE)
    rest = (ONE, SHIFT[0], SHIFT[0], SHIFT[0])
    whole = tuple(pmul(d1[i], rest[i]) for i in range(4))
    if side == "right":
        return d1, rest
    if side == "left":
        return (ONE, ONE, ONE, ONE), whole
    fail("unknown local side")


def local_entry(row_scale, col_scale, code, i, j):
    nibble = (code >> (4 * i)) & 15
    if ((nibble >> j) & 1) == 0:
        return 0
    return pmul(row_scale[i], col_scale[j])


def local_census(side):
    row_scale, col_scale = local_scales(side)
    identity_hits = []
    pure_hits = []
    pure_target = SHIFT[0]
    for code in range(65536):
        identity = True
        pure = True
        for i in range(4):
            for j in range(4):
                actual = local_entry(row_scale, col_scale, code, i, j)
                if actual != (ONE if i == j else 0):
                    identity = False
                if actual != (pure_target if i == j else 0):
                    pure = False
        if identity:
            identity_hits.append(code)
        if pure:
            pure_hits.append(code)
    return identity_hits, pure_hits


def check_arithmetic():
    require(pmul(SHIFT[0], SHIFT[0]) == (ONE ^ (1 << 2)), "(1+x)^2 = 1+x^2")
    require(pmul(SHIFT[0], SHIFT[0]) != ONE, "(1+x)^2 is not 1")
    require(SHIFT[0] ^ SHIFT[0] == 0, "characteristic two cancels 1+x")
    require(evaluate(SHIFT[0], 1, 0, 0) == 0, "1+x vanishes at x=1")
    require(evaluate(ONE, 1, 0, 0) == 1, "the constant 1 does not vanish")
    require(len(range(65536)) == 65536, "the block domain has 65536 matrices")
    require(IDENTITY4 == 33825, "local identity code")


def check_pure_word(gates):
    expected = expected_pure()
    require(all(entry != ONE for entry in expected), "pure diagonal is not I")
    require(evaluate(expected[0], 1, 0, 0) == 0, "core monomial vanishes at x=1")
    product = multiply_all(gates)
    support = multiply_all(support_gates())
    require(product == support, "nine gates differ from product_j (I+x_j E_j)")
    require(diagonal_entries(product) == expected, "pure diagonal monomials")
    require(multiply_all(gates[:-1]) != product, "dropping a gate preserved the pure word")
    altered = list(expected)
    altered[0] = SHIFT[0]
    require(tuple(altered) != expected, "control monomial was not actually different")
    return expected


def check_formula(gates, index, side, pure):
    row_scale, col_scale = scales(gates, index, side)
    for i in range(8):
        require(pmul(row_scale[i], col_scale[i]) == pure[i], "diagonal scales missed the pure product")
        require(row_scale[i] != 0 and col_scale[i] != 0, "a scale vanished")
    for row in range(8):
        for col in range(8):
            unit = unit_matrix(row, col)
            _pure, coeff = insert(gates, index, side, unit)
            predicted = zero_matrix()
            predicted = list(list(line) for line in predicted)
            predicted[row][col] = pmul(row_scale[row], col_scale[col])
            predicted = tuple(tuple(line) for line in predicted)
            require(coeff == predicted, "scale formula missed a matrix unit")
            require(_pure == multiply_all(gates), "insertion changed the pure product")
    identity = eye_matrix()
    pure_part, coeff = insert(gates, index, side, identity)
    require(pure_part == multiply_all(gates), "R=I changed the pure product")
    require(diagonal_entries(coeff) == pure and is_diagonal(coeff), "R=I missed the pure coefficient")
    require(coeff != eye_matrix(), "R=I made the coefficient equal to I")
    return row_scale, col_scale


def check_block_census(row_scale, col_scale, pure):
    identity_hits, pure_hits = census(row_scale, col_scale, pure)
    require(identity_hits == [], "a stage-supported matrix made the coefficient I")
    require(pure_hits == [], "a stage-supported matrix made the coefficient the pure product")
    embedded_identity = block_bits(IDENTITY4)
    require(not matches(row_scale, col_scale, embedded_identity, pure, True), "embedded I_4 passed as I")
    require(not matches(row_scale, col_scale, embedded_identity, pure, False), "embedded I_4 passed as P")
    return 65536


def two_factor_entry(code, i, j, side):
    nibble_row = (code >> (4 * i)) & 15
    bit = (nibble_row >> j) & 1
    if not bit:
        return 0
    if side == "right":
        return SHIFT[0] if i == 0 else ONE
    return SHIFT[0] if j == 0 else ONE


def local_matrix(entries):
    return tuple(tuple(entries[i][j] for j in range(4)) for i in range(4))


def mul4(left, right):
    out = [[0] * 4 for _ in range(4)]
    for i in range(4):
        for k in range(4):
            factor = left[i][k]
            if not factor:
                continue
            for j in range(4):
                if right[k][j]:
                    out[i][j] ^= pmul(factor, right[k][j])
    return tuple(tuple(row) for row in out)


def stage_factor():
    return local_matrix([[SHIFT[0] if i == j == 0 else (ONE if i == j else 0) for j in range(4)] for i in range(4)])


def local_unit(code):
    return local_matrix([[ONE if ((code >> (4 * i)) & 15) >> j & 1 else 0 for j in range(4)] for i in range(4)])


def check_local():
    for side in ("right", "left"):
        identity_hits, pure_hits = local_census(side)
        require(identity_hits == [], "local coefficient I had a constant solution")
        require(pure_hits == [IDENTITY4], "local pure target was not exactly I_4")
    # Named expansion: (I + x E_11)(I + e R) and (I + e R)(I + x E_11), before B and C.
    for code in range(65536):
        for side in ("right", "left"):
            hit = True
            for i in range(4):
                for j in range(4):
                    if two_factor_entry(code, i, j, side) != (ONE if i == j else 0):
                        hit = False
            require(not hit, "two-factor expansion hit coefficient I")
    identity_right = [two_factor_entry(IDENTITY4, i, i, "right") for i in range(4)]
    require(identity_right == [SHIFT[0], ONE, ONE, ONE], "two-factor identity coefficient")
    factor = stage_factor()
    for row in range(4):
        for col in range(4):
            code = 1 << (4 * row + col)
            unit = local_unit(code)
            right = mul4(factor, unit)
            left = mul4(unit, factor)
            for i in range(4):
                for j in range(4):
                    require(right[i][j] == two_factor_entry(code, i, j, "right"), "local right formula")
                    require(left[i][j] == two_factor_entry(code, i, j, "left"), "local left formula")
    return 65536


def check_linearity(gates):
    left = add_mat(unit_matrix(0, 0), unit_matrix(1, 2))
    _pure, separate = insert(gates, 0, "right", unit_matrix(0, 0))
    _pure, other = insert(gates, 0, "right", unit_matrix(1, 2))
    _pure, together = insert(gates, 0, "right", left)
    require(together == add_mat(separate, other), "coefficient map was not linear")


def check_two_insertions(gates, pure):
    first = as_insertion(eye_matrix())
    second = as_insertion(eye_matrix())
    factors = [as_pure(gate) for gate in gates]
    factors.insert(1, first)
    factors.insert(3, second)
    pure_part, coeff = multiply_affine(tuple(factors))
    require(pure_part == multiply_all(gates), "two insertions changed the pure product")
    require(coeff == zero_matrix(), "two copies of I did not cancel in characteristic two")
    require(tuple(ONE for _ in range(8)) != pure, "cancellation control compared equal polynomials")


def check_reversed(gates, pure):
    reversed_gates = tuple(reversed(gates))
    index = len(reversed_gates) - 1
    require(diagonal_entries(reversed_gates[index])[0] == SHIFT[0], "reversed word lost E_11")
    for side in ("left", "right"):
        check_formula(reversed_gates, index, side, pure)


def main():
    check_arithmetic()
    gates = nine_gates()
    pure = check_pure_word(gates)
    counted = 0
    for side in ("right", "left"):
        row_scale, col_scale = check_formula(gates, 0, side, pure)
        counted += check_block_census(row_scale, col_scale, pure)
    local_count = check_local()
    check_linearity(gates)
    check_two_insertions(gates, pure)
    check_reversed(gates, pure)
    require(counted == 131072 and local_count == 65536, "census domain size")
    print(
        "pure=product_j(I+x_j E_j) "
        "local_identity_hits=0 local_pure_hits=1 "
        "block_identity_hits=0 block_pure_hits=0 "
        "block_matrices=65536 sides=2 units=64 "
        "endpoint_witness=I"
    )
    print("PASS_PAIRED_STAR_CONSTANT_R_INSERTION")


if __name__ == "__main__":
    main()
