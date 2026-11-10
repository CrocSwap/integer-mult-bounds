#!/usr/bin/env python3
"""Valuation-1 factors outside the T-commutant of a paired-star stage.

Every 4-by-4 matrix over F_2 that commutes with T has even (1+x)-valuation.
Explicit triples, including one idempotent triple of valuations 1, 1 and 2,
multiply to I+x I_4. The same diagonal gates meet the pure three-stage
operator on the eight-dimensional core-plus-leaves space. Failures raise
SystemExit, so python -O still fails closed.
"""

from __future__ import annotations

import itertools

EYE = (1, 2, 4, 8)
ZERO = (0, 0, 0, 0)
T_MATRIX = (5, 10, 5, 10)
S_MATRIX = (1, 2, 5, 10)
DIAGONAL_A = (1, 0, 0, 0)
DIAGONAL_B = (0, 2, 0, 0)
DIAGONAL_C = (0, 0, 4, 8)
NONIDEM_A = (1, 4, 0, 0)
NONIDEM_B = (0, 2, 0, 0)
NONIDEM_C = (0, 4, 4, 8)
ONE_POLY = {(0, 0, 0): 1}


def fail(message):
    raise SystemExit("FAIL: " + message)


def require(ok, message):
    if not ok:
        fail(message)


def pmul(left, right):
    out = 0
    while left:
        bit = left & -left
        out ^= right << (bit.bit_length() - 1)
        left ^= bit
    return out


def mul_bits(left, right):
    rows = []
    for row in left:
        value = 0
        rest = row
        while rest:
            bit = rest & -rest
            value ^= right[bit.bit_length() - 1]
            rest ^= bit
        rows.append(value)
    return tuple(rows)


def add_bits(left, right):
    return tuple(a ^ b for a, b in zip(left, right))


def rows_from_bits(bits):
    return tuple((bits >> (4 * row)) & 15 for row in range(4))


def rank4(matrix):
    rows = list(matrix)
    rank = 0
    for col in range(4):
        pivot = next((i for i in range(rank, 4) if (rows[i] >> col) & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(4):
            if i != rank and (rows[i] >> col) & 1:
                rows[i] ^= rows[rank]
        rank += 1
    return rank


def gate4(matrix):
    rows = []
    for i in range(4):
        row = []
        for j in range(4):
            poly = 1 if i == j else 0
            if (matrix[i] >> j) & 1:
                poly ^= 2
            row.append(poly)
        rows.append(tuple(row))
    return tuple(rows)


def mul4(left, right):
    out = [[0] * 4 for _ in range(4)]
    for i in range(4):
        for k in range(4):
            factor = left[i][k]
            if not factor:
                continue
            for j in range(4):
                out[i][j] ^= pmul(factor, right[k][j])
    return tuple(tuple(row) for row in out)


def det_rows(matrix):
    total = 0
    for perm in itertools.permutations(range(len(matrix))):
        prod = 1
        for row, col in enumerate(perm):
            prod = pmul(prod, matrix[row][col])
            if prod == 0:
                break
        total ^= prod
    return total


def minor4(matrix, drop_row, drop_col):
    rows = []
    for row in range(4):
        if row == drop_row:
            continue
        rows.append(tuple(matrix[row][col] for col in range(4) if col != drop_col))
    return tuple(rows)


def det_laplace(matrix):
    total = 0
    for col in range(4):
        total ^= pmul(matrix[0][col], det_rows(minor4(matrix, 0, col)))
    return total


def valuation(poly):
    """(1+x)-adic valuation in F_2[x]. The zero polynomial is rejected."""
    if poly == 0:
        fail("zero polynomial has no finite valuation")
    value = 0
    while poly.bit_count() % 2 == 0:
        quotient = 0
        previous = 0
        for index in range(poly.bit_length()):
            current = ((poly >> index) & 1) ^ previous
            if current:
                quotient |= 1 << index
            previous = current
        if previous != 0:
            fail("polynomial was not divisible by 1+x")
        poly = quotient
        value += 1
        if value > 8:
            fail("valuation did not terminate")
    return value


def commutes_with_t(matrix):
    return mul_bits(T_MATRIX, matrix) == mul_bits(matrix, T_MATRIX)


def mat2(bits):
    return (
        (bits & 1, (bits >> 1) & 1),
        ((bits >> 2) & 1, (bits >> 3) & 1),
    )


def add2(left, right):
    return tuple(tuple(left[r][c] ^ right[r][c] for c in range(2)) for r in range(2))


def pack_blocks(top_left, top_right, bottom_left, bottom_right):
    blocks = (
        (top_left, top_right),
        (bottom_left, bottom_right),
    )
    rows = []
    for block_row in range(2):
        for r in range(2):
            mask = 0
            for block_col in range(2):
                block = blocks[block_row][block_col]
                for c in range(2):
                    if block[r][c]:
                        mask |= 1 << (2 * block_col + c)
            rows.append(mask)
    return tuple(rows)


def det2_poly(block):
    trace = block[0][0] ^ block[1][1]
    det = (block[0][0] & block[1][1]) ^ (block[0][1] & block[1][0])
    return 1 ^ ((trace & 1) << 1) ^ ((det & 1) << 2)


def factor_valuations(triple):
    return tuple(valuation(det_rows(gate4(matrix))) for matrix in triple)


def product_is_target(triple):
    target = gate4(EYE)
    acc = gate4(triple[0])
    for matrix in triple[1:]:
        acc = mul4(acc, gate4(matrix))
    return acc == target


def on_kernel_of_e11(matrix):
    if matrix[0] != 0:
        return False
    return all((row & 1) == 0 for row in matrix)


def add_poly(left, right):
    out = dict(left)
    for key in right:
        if key in out:
            del out[key]
        else:
            out[key] = 1
    return out


def mul_poly(left, right):
    out = {}
    for left_key in left:
        for right_key in right:
            key = tuple(left_key[i] + right_key[i] for i in range(3))
            if key in out:
                del out[key]
            else:
                out[key] = 1
    return out


def mul8(left, right):
    out = []
    for i in range(8):
        row = []
        for j in range(8):
            acc = {}
            for k in range(8):
                factor = left[i][k]
                if factor:
                    acc = add_poly(acc, mul_poly(factor, right[k][j]))
            row.append(acc)
        out.append(tuple(row))
    return tuple(out)


def stage_coords(stage):
    leaf = 2 * (stage + 1)
    return (0, 1, leaf, leaf + 1)


def embed(rows, stage):
    coords = stage_coords(stage)
    out = [0] * 8
    for i in range(4):
        for j in range(4):
            if (rows[i] >> j) & 1:
                out[coords[i]] |= 1 << coords[j]
    return tuple(out)


def support_e(stage):
    rows = [0] * 8
    rows[0] = 1
    rows[1] = 2
    leaf = 2 * (stage + 1)
    rows[leaf] = 1 << leaf
    rows[leaf + 1] = 1 << (leaf + 1)
    return tuple(rows)


def gate8(bit_rows, variable):
    one = dict(ONE_POLY)
    mono_key = [0, 0, 0]
    mono_key[variable] = 1
    mono = {tuple(mono_key): 1}
    matrix = []
    for i in range(8):
        row = []
        for j in range(8):
            poly = dict(one) if i == j else {}
            if (bit_rows[i] >> j) & 1:
                poly = add_poly(poly, mono)
            row.append(poly)
        matrix.append(tuple(row))
    return tuple(matrix)


def multiply_all(factors):
    acc = factors[0]
    for factor in factors[1:]:
        acc = mul8(acc, factor)
    return acc


def block_supported(rows, stage):
    coords = stage_coords(stage)
    allowed = 0
    for coord in coords:
        allowed |= 1 << coord
    outside_mask = ((1 << 8) - 1) ^ allowed
    for index in range(8):
        if index not in coords and rows[index] != 0:
            return False
        if rows[index] & outside_mask:
            return False
    return True


def check_arithmetic():
    require(len(tuple(itertools.permutations(range(4)))) == 24, "S4 has 24 permutations")
    require(mul_bits(S_MATRIX, S_MATRIX) == EYE, "S^2 = I")
    require(mul_bits(T_MATRIX, T_MATRIX) == ZERO, "T^2 = 0")
    require(det_rows(gate4(EYE)) == 0b10001, "det(I+xI) = (1+x)^4 = 1+x^4")
    require(valuation(1) == 0, "val(1)")
    require(valuation(0b11) == 1, "val(1+x)")
    require(valuation(0b101) == 2, "val((1+x)^2)")
    require(valuation(0b10001) == 4, "val((1+x)^4)")
    swap = ((0, 1, 0, 0), (1, 0, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))
    require(det_rows(swap) == 1, "char-2 determinant has no signs")
    require(det_rows(swap) == det_laplace(swap), "Laplace agrees on a transposition")


def check_explicit_triples():
    diagonal = (DIAGONAL_A, DIAGONAL_B, DIAGONAL_C)
    nonidem = (NONIDEM_A, NONIDEM_B, NONIDEM_C)
    require(product_is_target(diagonal), "diagonal triple missed I+x I_4")
    require(product_is_target(nonidem), "non-idempotent triple missed I+x I_4")
    require(factor_valuations(diagonal) == (1, 1, 2), "diagonal valuations")
    require(factor_valuations(nonidem) == (1, 1, 2), "non-idempotent valuations")
    require(all(mul_bits(m, m) == m for m in diagonal), "diagonal factors are idempotent")
    require(mul_bits(NONIDEM_A, NONIDEM_A) != NONIDEM_A, "leading factor is not idempotent")
    require(rank4(DIAGONAL_A) == 1 and rank4(DIAGONAL_B) == 1 and rank4(DIAGONAL_C) == 2, "diagonal ranks")
    require(all(not commutes_with_t(m) for m in diagonal), "a diagonal factor commutes with T")
    require(not commutes_with_t(NONIDEM_A), "non-idempotent factor commutes with T")
    orders = 0
    for perm in itertools.permutations(diagonal):
        require(product_is_target(perm), "a diagonal order missed the target")
        orders += 1
    require(orders == 6, "six diagonal orders")
    short = (DIAGONAL_A, DIAGONAL_B, (0, 0, 4, 0))
    require(factor_valuations(short) == (1, 1, 1), "three rank-1 valuations")
    require(not product_is_target(short), "valuations 1+1+1 met the target")
    repeated = (DIAGONAL_A, DIAGONAL_A, DIAGONAL_A)
    require(not product_is_target(repeated), "E11 cubed met the target")


def check_commutant():
    zero2 = ((0, 0), (0, 0))
    distinct_a_one = 0
    distinct_a_square = 0
    for bits in range(16):
        poly = det2_poly(mat2(bits))
        distinct_a_one += poly == 3
        distinct_a_square += poly == 5
    require((distinct_a_one, distinct_a_square) == (6, 4), "2-by-2 determinant buckets")
    seen = set()
    histogram = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    projectors = 0
    square_bucket = 0
    linear_bucket = 0
    for w_bits in range(16):
        w_block = mat2(w_bits)
        for x_bits in range(16):
            x_block = mat2(x_bits)
            matrix = pack_blocks(w_block, x_block, x_block, w_block)
            seen.add(matrix)
            require(commutes_with_t(matrix), "parametrized matrix does not commute with T")
            a_block = add2(w_block, x_block)
            triangular = pack_blocks(a_block, x_block, zero2, a_block)
            require(mul_bits(mul_bits(S_MATRIX, matrix), S_MATRIX) == triangular, "S M S")
            closed = pmul(det2_poly(a_block), det2_poly(a_block))
            determinant = det_rows(gate4(matrix))
            require(determinant == det_rows(gate4(triangular)) == closed, "commutant determinant")
            value = valuation(determinant)
            require(value % 2 == 0 and value in histogram, "commutant valuation is even")
            histogram[value] += 1
            projectors += mul_bits(matrix, matrix) == matrix
            square_bucket += det2_poly(a_block) == 5
            linear_bucket += det2_poly(a_block) == 3
    require(len(seen) == 256, "commutant parametrization is not bijective")
    require(histogram == {0: 96, 1: 0, 2: 96, 3: 0, 4: 64}, "commutant histogram")
    require(projectors == 26, "commutant projector count")
    require(linear_bucket == 6 * 16 and square_bucket == 4 * 16, "bucket times free B")
    contrast = pack_blocks(mat2(1), zero2, zero2, mat2(1))
    require(commutes_with_t(contrast) and mul_bits(contrast, contrast) == contrast, "rank-1 call")
    require(valuation(det_rows(gate4(contrast))) == 2, "T-commuting projector valuation")
    nonprojector = pack_blocks(zero2, mat2(1), mat2(1), zero2)
    require(commutes_with_t(nonprojector), "commutant non-projector")
    require(mul_bits(nonprojector, nonprojector) != nonprojector, "non-projector was idempotent")
    require(valuation(det_rows(gate4(nonprojector))) == 2, "dropping idempotence inside T")
    require(not product_is_target((contrast, DIAGONAL_B, DIAGONAL_C)), "commutant factor repaired the triple")
    return seen


def check_all_matrices(commutant):
    histogram = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    rank_histogram = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    idempotents = []
    valuation_one_in_commutant = 0
    for bits in range(1 << 16):
        matrix = rows_from_bits(bits)
        gate = gate4(matrix)
        determinant = det_rows(gate)
        require(determinant == det_laplace(gate), "Leibniz and Laplace disagree")
        require(determinant & 1 == 1, "constant term of det(I+xM)")
        value = valuation(determinant)
        require(value in histogram, "valuation left 0..4")
        histogram[value] += 1
        if value == 1 and matrix in commutant:
            valuation_one_in_commutant += 1
        if mul_bits(matrix, matrix) == matrix:
            rank = rank4(matrix)
            require(value == rank, "idempotent valuation differs from rank")
            rank_histogram[rank] += 1
            idempotents.append(matrix)
    require(histogram == {0: 20160, 1: 20160, 2: 13440, 3: 7680, 4: 4096}, "matrix histogram")
    require(sum(histogram.values()) == 65536, "matrix census missed a bit pattern")
    require(rank_histogram == {0: 1, 1: 120, 2: 560, 3: 120, 4: 1}, "idempotent ranks")
    require(len(idempotents) == 802, "idempotent count")
    require(valuation_one_in_commutant == 0, "a commutant matrix has valuation 1")
    return idempotents


def check_idempotent_slice(idempotents):
    gates = {matrix: gate4(matrix) for matrix in idempotents}
    target = gates[EYE]
    first = DIAGONAL_A
    require(first in gates, "E11 is not idempotent")
    hits = 0
    for middle in idempotents:
        left = mul4(gates[first], gates[middle])
        for right in idempotents:
            if mul4(left, gates[right]) != target:
                continue
            hits += 1
            require(mul_bits(first, middle) == ZERO and mul_bits(middle, first) == ZERO, "solution is not orthogonal")
            require(right == add_bits(add_bits(EYE, first), middle), "solution missed C=I+A+B")
            require(on_kernel_of_e11(middle), "middle factor meets the image of E11")
    kernel_idempotents = sum(on_kernel_of_e11(matrix) for matrix in idempotents)
    require(hits == 58 and kernel_idempotents == 58, "E11 idempotent slice")


def coefficient_vanishes(first, middle):
    right = add_bits(add_bits(EYE, first), middle)
    cross = mul_bits(first, middle)
    mixed = add_bits(first, middle)
    quadratic = add_bits(cross, mul_bits(mixed, right))
    cubic = mul_bits(cross, right)
    return quadratic == ZERO and cubic == ZERO


def check_nonidempotent_slice():
    hits = 0
    middle_commutes = 0
    right_commutes = 0
    gate_first = gate4(NONIDEM_A)
    target = gate4(EYE)
    for bits in range(1 << 16):
        middle = rows_from_bits(bits)
        right = add_bits(add_bits(EYE, NONIDEM_A), middle)
        product = mul4(mul4(gate_first, gate4(middle)), gate4(right))
        equations = coefficient_vanishes(NONIDEM_A, middle)
        require((product == target) == equations, "coefficient equations disagree with the product")
        if product != target:
            continue
        hits += 1
        middle_commutes += commutes_with_t(middle)
        right_commutes += commutes_with_t(right)
    require(hits == 128, "non-idempotent slice count")
    require(middle_commutes == 3 and right_commutes == 0, "commutant companions in the slice")
    require(coefficient_vanishes(NONIDEM_A, NONIDEM_B), "exhibited middle factor missed the slice")


def expected_pure_diagonal():
    def shift(variable):
        key = [0, 0, 0]
        key[variable] = 1
        return add_poly(ONE_POLY, {tuple(key): 1})

    xy = mul_poly(shift(0), shift(1))
    core = mul_poly(xy, shift(2))
    expected = []
    for row in range(8):
        line = []
        for col in range(8):
            poly = {}
            if row == col and row < 2:
                poly = core
            elif row == col and row < 4:
                poly = shift(0)
            elif row == col and row < 6:
                poly = shift(1)
            elif row == col:
                poly = shift(2)
            line.append(poly)
        expected.append(tuple(line))
    return tuple(expected)


def check_pure_word():
    diagonal = (DIAGONAL_A, DIAGONAL_B, DIAGONAL_C)
    factors = []
    for stage in range(3):
        require(embed(EYE, stage) == support_e(stage), "E embedding")
        for matrix in diagonal:
            embedded = embed(matrix, stage)
            require(block_supported(embedded, stage), "diagonal factor left its stage block")
            factors.append(gate8(embedded, stage))
    word = multiply_all(tuple(factors))
    target_factors = tuple(gate8(support_e(stage), stage) for stage in range(3))
    require(word == multiply_all(target_factors) == expected_pure_diagonal(), "pure three-stage word")
    require(multiply_all(tuple(factors[:-1])) != word, "dropping a factor left the pure word")
    nonidem = (NONIDEM_A, NONIDEM_B, NONIDEM_C)
    stage_factors = []
    for matrix in nonidem:
        embedded = embed(matrix, 0)
        require(block_supported(embedded, 0), "non-idempotent factor left stage 0")
        stage_factors.append(gate8(embedded, 0))
    require(multiply_all(tuple(stage_factors)) == gate8(support_e(0), 0), "stage-0 non-idempotent embedding")


def main():
    check_arithmetic()
    check_explicit_triples()
    commutant = check_commutant()
    idempotents = check_all_matrices(commutant)
    check_idempotent_slice(idempotents)
    check_nonidempotent_slice()
    check_pure_word()
    print(
        "commutant=256 histogram=0:96,1:0,2:96,4:64 projectors=26 "
        "matrices=65536 histogram=0:20160,1:20160,2:13440,3:7680,4:4096 "
        "idempotents=802 ranks=0:1,1:120,2:560,3:120,4:1 "
        "e11_idempotent_solutions=58 nonidempotent_slice=128 "
        "pure_word_stages=3"
    )
    print("PASS_PAIRED_STAR_VALUATION_ONE_FACTOR")


if __name__ == "__main__":
    main()
