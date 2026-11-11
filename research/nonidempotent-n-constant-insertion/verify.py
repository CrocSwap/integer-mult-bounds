#!/usr/bin/env python3
"""Constant insertion beside the non-idempotent factor N of PR #7027.

The stage-0 coefficient of e in (I + x N)(I + e R), multiplied by the
remaining factors of the exhibited word, is never I. Failures raise
SystemExit, so python -O still fails closed.
"""

from __future__ import annotations

N_BITS = (1, 4, 0, 0)
B_BITS = (0, 2, 0, 0)
C_BITS = (0, 4, 4, 8)
EYE_BITS = (1, 2, 4, 8)
E11_BITS = (1, 0, 0, 0)
E22_BITS = (0, 2, 0, 0)
E33_E44_BITS = (0, 0, 4, 8)

# Univariate polynomials in F_2[x]: bit k is the coefficient of x^k.
ONE = 0b1
X = 0b10
ONE_PLUS_X = 0b11


def fail(message):
    raise SystemExit("FAIL: " + message)


def require(ok, message):
    if not ok:
        fail(message)


def pdeg(poly):
    return -1 if poly == 0 else poly.bit_length() - 1


def pmul(left, right):
    out = 0
    shift = 0
    while right:
        if right & 1:
            out ^= left << shift
        right >>= 1
        shift += 1
    return out


def pdiv(dividend, divisor):
    """Exact quotient in F_2[x]. Fails when the remainder is nonzero."""
    require(divisor != 0, "division by zero")
    quotient = 0
    remainder = dividend
    degree = pdeg(divisor)
    while remainder and pdeg(remainder) >= degree:
        shift = pdeg(remainder) - degree
        quotient ^= 1 << shift
        remainder ^= divisor << shift
    require(remainder == 0, "not an exact quotient in F_2[x]")
    return quotient


def bits_matrix(rows):
    return tuple(
        tuple((rows[i] >> j) & 1 for j in range(4))
        for i in range(4)
    )


def gate_from_bits(rows):
    matrix = []
    for i in range(4):
        line = []
        for j in range(4):
            entry = ONE if i == j else 0
            if (rows[i] >> j) & 1:
                entry ^= X
            line.append(entry)
        matrix.append(tuple(line))
    return tuple(matrix)


def constant_matrix(rows):
    return tuple(
        tuple(((rows[i] >> j) & 1) * ONE for j in range(4))
        for i in range(4)
    )


def mul4(left, right):
    out = []
    for i in range(4):
        line = []
        for j in range(4):
            acc = 0
            for k in range(4):
                acc ^= pmul(left[i][k], right[k][j])
            line.append(acc)
        out.append(tuple(line))
    return tuple(out)


def scale_identity(poly):
    return tuple(
        tuple(poly if i == j else 0 for j in range(4))
        for i in range(4)
    )


def unit_bits(row, col):
    rows = [0, 0, 0, 0]
    rows[row] = 1 << col
    return tuple(rows)


def mul_bits(left, right):
    out = []
    for i in range(4):
        acc = 0
        for k in range(4):
            if (left[i] >> k) & 1:
                acc ^= right[k]
        out.append(acc)
    return tuple(out)


def check_arithmetic():
    require(pmul(ONE_PLUS_X, ONE) == ONE_PLUS_X, "(1+x)*1")
    require(pmul(ONE_PLUS_X, X) == 0b110, "(1+x)*x = x+x^2")
    require(pmul(ONE_PLUS_X, ONE_PLUS_X) == 0b101, "(1+x)^2 = 1+x^2")
    require(pdiv(ONE_PLUS_X, ONE_PLUS_X) == ONE, "cancel 1+x")
    require(pdiv(0, ONE_PLUS_X) == 0, "zero quotient")
    require(pdiv(pmul(ONE_PLUS_X, ONE_PLUS_X), ONE_PLUS_X) == ONE_PLUS_X, "cancel one factor")
    caught = False
    try:
        pdiv(ONE, ONE_PLUS_X)
    except SystemExit:
        caught = True
    require(caught, "1+x divided 1")
    for degree in range(12):
        monomial = 1 << degree
        product = pmul(ONE_PLUS_X, monomial)
        require(product == monomial ^ (monomial << 1), "leading term of (1+x) x^k")
        require(pdeg(product) == degree + 1, "degree rises")
        require(product != ONE, "a monomial multiple was 1")
    for poly in range(1, 64):
        require(pdeg(pmul(ONE_PLUS_X, poly)) == pdeg(poly) + 1, "degree formula")


def check_shapes():
    require(mul_bits(N_BITS, N_BITS) == E11_BITS, "N^2 = E_11")
    require(mul_bits(N_BITS, N_BITS) != N_BITS, "N is not idempotent")
    require(mul_bits(B_BITS, B_BITS) == B_BITS, "exhibited middle factor")
    gate_n = gate_from_bits(N_BITS)
    gate_b = gate_from_bits(B_BITS)
    gate_c = gate_from_bits(C_BITS)
    hand_n = (
        (ONE_PLUS_X, 0, 0, 0),
        (0, ONE, X, 0),
        (0, 0, ONE, 0),
        (0, 0, 0, ONE),
    )
    hand_m = (
        (ONE, 0, 0, 0),
        (0, ONE_PLUS_X, pmul(X, ONE_PLUS_X), 0),
        (0, 0, ONE_PLUS_X, 0),
        (0, 0, 0, ONE_PLUS_X),
    )
    require(gate_n == hand_n, "I+xN shape")
    require(gate_n[0] == (ONE_PLUS_X, 0, 0, 0), "row 0 of I+xN")
    tail = mul4(gate_b, gate_c)
    require(tail == hand_m, "tail (I+xB)(I+xC)")
    require(tuple(tail[i][0] for i in range(4)) == (ONE, 0, 0, 0), "tail column 0")
    product = mul4(gate_n, tail)
    require(product == scale_identity(ONE_PLUS_X), "stage-0 triple is (1+x) I_4")
    # The diagonal identity would say every diagonal scales by R_ii (1+x).
    # Position (1, 1) of the right-hand coefficient sees R_21 as well.
    skewed = constant_matrix(unit_bits(2, 1))
    skewed_coeff = mul4(mul4(gate_n, skewed), tail)
    require(skewed_coeff[1][1] == pmul(X, ONE_PLUS_X), "E_21 reaches position (1,1)")
    require(skewed_coeff[1][1] != 0, "diagonal identity does not describe N")
    return gate_n, tail


def closed_forms():
    """Hand formulas for K = (I + x N) R (I + x B)(I + x C)."""
    xx = pmul(ONE_PLUS_X, ONE_PLUS_X)
    x_xx = pmul(X, xx)
    x1 = pmul(X, ONE_PLUS_X)
    x2 = pmul(X, x1)
    return {
        (0, 0): {(0, 0): ONE_PLUS_X},
        (0, 1): {(0, 1): xx},
        (0, 2): {(0, 1): x_xx, (0, 2): xx},
        (0, 3): {(0, 3): xx},
        (1, 0): {(1, 0): ONE, (2, 0): X},
        (1, 1): {(1, 1): ONE_PLUS_X, (2, 1): x1},
        (1, 2): {(1, 1): x1, (1, 2): ONE_PLUS_X, (2, 1): x2, (2, 2): x1},
        (1, 3): {(1, 3): ONE_PLUS_X, (2, 3): x1},
        (2, 0): {(2, 0): ONE},
        (2, 1): {(2, 1): ONE_PLUS_X},
        (2, 2): {(2, 1): x1, (2, 2): ONE_PLUS_X},
        (2, 3): {(2, 3): ONE_PLUS_X},
        (3, 0): {(3, 0): ONE},
        (3, 1): {(3, 1): ONE_PLUS_X},
        (3, 2): {(3, 1): x1, (3, 2): ONE_PLUS_X},
        (3, 3): {(3, 3): ONE_PLUS_X},
    }


def forms_from_units(gate_n, tail):
    forms = {(i, j): {} for i in range(4) for j in range(4)}
    for row in range(4):
        for col in range(4):
            coeff = mul4(mul4(gate_n, constant_matrix(unit_bits(row, col))), tail)
            for i in range(4):
                for j in range(4):
                    if coeff[i][j]:
                        forms[(i, j)][(row, col)] = coeff[i][j]
    return forms


def check_forms(gate_n, tail):
    expected = closed_forms()
    actual = forms_from_units(gate_n, tail)
    for i in range(4):
        for j in range(4):
            require(actual[(i, j)] == expected[(i, j)], "closed form " + str((i, j)))
    require(actual[(0, 0)] == {(0, 0): ONE_PLUS_X}, "K_00 = (1+x) R_00")
    # Linearity over F_2 and over the coefficient x.
    combined_bits = [0, 0, 0, 0]
    combined_bits[0] |= 1 << 0
    combined_bits[1] |= 1 << 2
    direct = mul4(mul4(gate_n, constant_matrix(tuple(combined_bits))), tail)
    left = mul4(mul4(gate_n, constant_matrix(unit_bits(0, 0))), tail)
    right = mul4(mul4(gate_n, constant_matrix(unit_bits(1, 2))), tail)
    summed = tuple(
        tuple(left[i][j] ^ right[i][j] for j in range(4))
        for i in range(4)
    )
    require(direct == summed, "coefficient is additive")
    scaled = tuple(tuple(pmul(X, left[i][j]) for j in range(4)) for i in range(4))
    x_unit = tuple(
        tuple(pmul(X, constant_matrix(unit_bits(0, 0))[i][j]) for j in range(4))
        for i in range(4)
    )
    require(mul4(mul4(gate_n, x_unit), tail) == scaled, "coefficient is F_2[x]-linear")
    pure = mul4(gate_n, tail)
    for row in range(4):
        for col in range(4):
            left = mul4(constant_matrix(unit_bits(row, col)), pure)
            expect = tuple(
                tuple(
                    ONE_PLUS_X if i == row and j == col else 0
                    for j in range(4)
                )
                for i in range(4)
            )
            require(left == expect, "left coefficient scales the inserted unit")


def apply_known(form, known):
    acc = 0
    rest = {}
    for var, coeff in form.items():
        if var in known:
            acc ^= pmul(coeff, known[var])
        else:
            rest[var] = coeff
    return rest, acc


def solve_pure_target(forms):
    """Execute the written cancellation order for K = (1+x) I_4."""
    target = {(i, j): (ONE_PLUS_X if i == j else 0) for i in range(4) for j in range(4)}
    known = {}
    order = [
        (2, 0), (3, 0), (1, 0), (0, 0),
        (2, 1), (3, 1), (1, 1),
        (2, 3), (1, 3), (3, 3),
        (0, 1), (0, 3), (0, 2),
        (2, 2), (3, 2), (1, 2),
    ]
    for key in order:
        rest, acc = apply_known(forms[key], known)
        rhs = target[key] ^ acc
        require(len(rest) == 1, "cancellation order is not triangular at " + str(key))
        (var, pivot), = rest.items()
        require(var == key, "pivot variable " + str(key))
        require(pivot != 0, "zero pivot")
        value = pdiv(rhs, pivot)
        require(value in (0, ONE), "nonconstant quotient " + str(key))
        known[var] = value
    require(len(known) == 16, "a matrix entry was not determined")
    for i in range(4):
        for j in range(4):
            require(known[(i, j)] == (ONE if i == j else 0), "pure target solution")
    # The same first pivot blocks the identity, before any later entry is used.
    rest, acc = apply_known(forms[(0, 0)], {})
    require(rest == {(0, 0): ONE_PLUS_X} and acc == 0, "identity pivot")
    caught = False
    try:
        pdiv(ONE, ONE_PLUS_X)
    except SystemExit:
        caught = True
    require(caught, "(1+x) R_00 = 1 had a polynomial solution")
    return known


def check_right_identity_for_any_tail(gate_n):
    """K_00 = (1+x) (R M)_00 for every trailing M, from row 0 of I+xN."""
    tails = [
        scale_identity(ONE),
        constant_matrix((15, 15, 15, 15)),
        constant_matrix(unit_bits(2, 0)),
        mul4(gate_from_bits(B_BITS), gate_from_bits(C_BITS)),
    ]
    for tail in tails:
        for row in range(4):
            for col in range(4):
                matrix_r = constant_matrix(unit_bits(row, col))
                coeff = mul4(mul4(gate_n, matrix_r), tail)
                mixed = mul4(matrix_r, tail)
                require(coeff[0][0] == pmul(ONE_PLUS_X, mixed[0][0]), "general (0,0) entry")


def check_constant_census(gate_n, tail):
    target_i = scale_identity(ONE)
    target_p = scale_identity(ONE_PLUS_X)
    pure = mul4(gate_n, tail)
    hits_i_right = hits_i_left = hits_p_right = hits_p_left = 0
    pure_witness = None
    visited = 0
    for bits in range(1 << 16):
        visited += 1
        rows = tuple((bits >> (4 * row)) & 15 for row in range(4))
        matrix_r = constant_matrix(rows)
        right = mul4(mul4(gate_n, matrix_r), tail)
        left = mul4(matrix_r, pure)
        hits_i_right += right == target_i
        hits_i_left += left == target_i
        if right == target_p:
            hits_p_right += 1
            pure_witness = rows
        hits_p_left += left == target_p
    require(visited == 65536, "constant census missed a matrix")
    require(hits_i_right == 0 and hits_i_left == 0, "a constant made the coefficient I")
    require(hits_p_right == 1 and hits_p_left == 1, "pure-target count")
    require(pure_witness == EYE_BITS, "pure-target witness")
    zero = constant_matrix((0, 0, 0, 0))
    require(mul4(mul4(gate_n, zero), tail) == scale_identity(0), "zero insertion")
    bumped = [1, 2, 4, 8]
    bumped[0] = 1 | 2
    require(
        mul4(mul4(gate_n, constant_matrix(tuple(bumped))), tail) != target_p,
        "I+E_01 met the pure target",
    )
    return hits_i_right, hits_p_right


# Multivariate polynomials: tuple of exponent triples (a, b, c) for x^a y^b z^c.


def madd(left, right):
    support = set(left)
    for exp in right:
        if exp in support:
            support.remove(exp)
        else:
            support.add(exp)
    return tuple(sorted(support))


def mmul(left, right):
    acc = {}
    for a1, b1, c1 in left:
        for a2, b2, c2 in right:
            exp = (a1 + a2, b1 + b2, c1 + c2)
            acc[exp] = acc.get(exp, 0) ^ 1
    return tuple(sorted(exp for exp, bit in acc.items() if bit))


M_ONE = ((0, 0, 0),)


def mmono(index):
    exp = [0, 0, 0]
    exp[index] = 1
    return (tuple(exp),)


def mscale(poly, size):
    return tuple(
        tuple(poly if i == j else () for j in range(size))
        for i in range(size)
    )


def mmul_mat(left, right):
    size = len(left)
    out = []
    for i in range(size):
        line = []
        for j in range(size):
            acc = ()
            for k in range(size):
                acc = madd(acc, mmul(left[i][k], right[k][j]))
            line.append(acc)
        out.append(tuple(line))
    return tuple(out)


def embed_bits(rows, stage):
    coords = (0, 1, 2 * (stage + 1), 2 * (stage + 1) + 1)
    out = [0] * 8
    for i in range(4):
        for j in range(4):
            if (rows[i] >> j) & 1:
                out[coords[i]] |= 1 << coords[j]
    return tuple(out)


def gate8(bit_rows, variable):
    mono = mmono(variable)
    matrix = []
    for i in range(8):
        line = []
        for j in range(8):
            entry = M_ONE if i == j else ()
            if (bit_rows[i] >> j) & 1:
                entry = madd(entry, mono)
            line.append(entry)
        matrix.append(tuple(line))
    return tuple(matrix)


def unit8(row, col):
    matrix = [[() for _ in range(8)] for _ in range(8)]
    matrix[row][col] = M_ONE
    return tuple(tuple(line) for line in matrix)


def evaluate_at_one_zero_zero(poly):
    acc = 0
    for a, b, c in poly:
        if b == 0 and c == 0:
            acc ^= 1
    return acc


def multiply_all(factors):
    acc = factors[0]
    for factor in factors[1:]:
        acc = mmul_mat(acc, factor)
    return acc


def check_embedded_word():
    gate_n = gate8(embed_bits(N_BITS, 0), 0)
    require(gate_n[0][0] == madd(M_ONE, mmono(0)), "embedded (0,0) entry")
    require(all(gate_n[0][j] == () for j in range(1, 8)), "embedded row 0")
    tail_factors = [gate8(embed_bits(B_BITS, 0), 0), gate8(embed_bits(C_BITS, 0), 0)]
    for stage, variable in ((1, 1), (2, 2)):
        for factor in (E11_BITS, E22_BITS, E33_E44_BITS):
            tail_factors.append(gate8(embed_bits(factor, stage), variable))
    tail = multiply_all(tuple(tail_factors))
    pure = mmul_mat(gate_n, tail)
    one_x = madd(M_ONE, mmono(0))
    one_y = madd(M_ONE, mmono(1))
    one_z = madd(M_ONE, mmono(2))
    core = mmul(one_x, mmul(one_y, one_z))
    expected_diag = {
        0: core,
        1: core,
        2: one_x,
        3: one_x,
        4: one_y,
        5: one_y,
        6: one_z,
        7: one_z,
    }
    for i in range(8):
        for j in range(8):
            expect = expected_diag[i] if i == j else ()
            require(pure[i][j] == expect, "embedded pure diagonal")
    factor = core
    extra_tails = (mscale(M_ONE, 8), unit8(2, 0))
    for row in range(8):
        for col in range(8):
            matrix_r = unit8(row, col)
            coeff = mmul_mat(mmul_mat(gate_n, matrix_r), tail)
            expect = factor if (row, col) == (0, 0) else ()
            require(coeff[0][0] == expect, "embedded right unit")
            for extra in extra_tails:
                mixed = mmul_mat(matrix_r, extra)
                general = mmul_mat(mmul_mat(gate_n, matrix_r), extra)
                require(
                    general[0][0] == mmul(madd(M_ONE, mmono(0)), mixed[0][0]),
                    "embedded (0,0) entry for an arbitrary tail",
                )
            left = mmul_mat(unit8(row, col), pure)
            left_expect = pure[col][0] if row == 0 else ()
            require(left[0][0] == left_expect, "embedded left unit")
    summed_r = [list(row) for row in unit8(0, 0)]
    summed_r[3][5] = M_ONE
    summed = tuple(tuple(line) for line in summed_r)
    direct = mmul_mat(mmul_mat(gate_n, summed), tail)
    parts = madd(
        mmul_mat(mmul_mat(gate_n, unit8(0, 0)), tail)[0][0],
        mmul_mat(mmul_mat(gate_n, unit8(3, 5)), tail)[0][0],
    )
    require(direct[0][0] == parts == factor, "embedded linearity")
    # Column 0 of the pure-product equation forces R e_0 = e_0. It does not
    # solve the other seven columns.
    t = mmul(one_y, one_z)
    column_forms = [{} for _ in range(8)]
    for row in range(8):
        for col in range(8):
            coeff = mmul_mat(mmul_mat(gate_n, unit8(row, col)), tail)
            for i in range(8):
                if coeff[i][0]:
                    column_forms[i][(row, col)] = coeff[i][0]
    require(column_forms[0] == {(0, 0): factor}, "column-0 form at row 0")
    require(
        column_forms[1] == {(1, 0): t, (2, 0): mmul(mmono(0), t)},
        "column-0 form at row 1",
    )
    require(column_forms[2] == {(2, 0): t}, "column-0 form at row 2")
    require(column_forms[3] == {(3, 0): t}, "column-0 form at row 3")
    for i in range(4, 8):
        require(column_forms[i] == {(i, 0): t}, "column-0 form at row " + str(i))
    require(evaluate_at_one_zero_zero(M_ONE) == 1, "evaluation of 1")
    require(evaluate_at_one_zero_zero(one_x) == 0, "evaluation of 1+x")
    require(evaluate_at_one_zero_zero(factor) == 0, "evaluation of the core factor")
    require(t != (), "later-stage factor is nonzero")
    return factor


def main():
    check_arithmetic()
    gate_n, tail = check_shapes()
    check_forms(gate_n, tail)
    forms = forms_from_units(gate_n, tail)
    solve_pure_target(forms)
    check_right_identity_for_any_tail(gate_n)
    hits_i, hits_p = check_constant_census(gate_n, tail)
    check_embedded_word()
    print(
        "stage0_constant_census=65536 identity_hits=%d pure_target_hits=%d "
        "embedded_units=64"
        % (hits_i, hits_p)
    )
    print("PASS_NONIDEMPOTENT_N_CONSTANT_INSERTION")


if __name__ == "__main__":
    main()
