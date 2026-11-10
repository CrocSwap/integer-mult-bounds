#!/usr/bin/env python3
"""Pure products of one nested pair and one crossed pair.

Evidence class: a proof in the paired-star projector algebra for the nested
schedule and for crossed schedules with B=0, plus one constructive pure-product
witness at q=26. Not a census of projectors or words, not a heuristic search,
and not an endpoint witness. No kappa change.

The first-applied factor is the rightmost factor. Characteristic two.
"""

from __future__ import annotations

from functools import lru_cache
import sys

G = 31
Q = 26
KAPPA = "781451/250000000"
MAPS = 5


def tok(kind, stage):
    return (kind, stage)


@lru_cache(maxsize=None)
def reduce_word(word, use_ba):
    letters = list(word)
    for index in range(len(letters) - 1):
        left, right = letters[index], letters[index + 1]
        if left[1] != right[1]:
            continue
        if left[0] == 0 and right[0] == 0:
            return reduce_word(tuple(letters[:index] + [left] + letters[index + 2 :]), use_ba)
        if use_ba and left[0] == 1 and right[0] == 0:
            branch_b = tuple(letters[:index] + [left] + letters[index + 2 :])
            branch_ab = tuple(letters[:index] + [right, left] + letters[index + 2 :])
            return reduce_word(branch_b, use_ba) ^ reduce_word(branch_ab, use_ba)
    return frozenset((word,))


def add_poly(*parts):
    out = set()
    for part in parts:
        out.symmetric_difference_update(part)
    return frozenset(out)


def mul_poly(left, right, use_ba=True):
    out = set()
    for xe, ye, word in left:
        for xf, yf, other in right:
            for reduced in reduce_word(word + other, use_ba):
                key = (xe + xf, ye + yf, reduced)
                if key in out:
                    out.remove(key)
                else:
                    out.add(key)
    return frozenset(out)


def mono(xexp, yexp, word=()):
    return frozenset(((xexp, yexp, word),))


def zero():
    return frozenset()


def one():
    return mono(0, 0, ())


def word_poly(kind, stage, xexp=0, yexp=0):
    return mono(xexp, yexp, (tok(kind, stage),))


def stage_var(stage, power=1):
    if stage == 0:
        return mono(power, 0, ())
    if stage == 1:
        return mono(0, power, ())
    raise AssertionError(stage)


def mat_zero(size):
    return [[zero() for _ in range(size)] for _ in range(size)]


def mat_id(size):
    matrix = mat_zero(size)
    for index in range(size):
        matrix[index][index] = one()
    return matrix


def mat_add(left, right):
    size = len(left)
    return [
        [add_poly(left[row][col], right[row][col]) for col in range(size)]
        for row in range(size)
    ]


def mat_mul(left, right, use_ba=True):
    size = len(left)
    out = mat_zero(size)
    for row in range(size):
        for col in range(size):
            acc = zero()
            for mid in range(size):
                acc = add_poly(acc, mul_poly(left[row][mid], right[mid][col], use_ba))
            out[row][col] = acc
    return out


def pure_factor(stage, primed, leaves, use_b=True, use_ba=True):
    size = leaves + 1
    matrix = mat_zero(size)
    for index in range(size):
        matrix[index][index] = one()
    a = word_poly(0, stage)
    b = word_poly(1, stage) if use_b else zero()
    diagonal = add_poly(a, b) if not primed else add_poly(one(), a, b)
    var = stage_var(stage)
    leaf = stage + 1

    def place(row, col, poly):
        matrix[row][col] = add_poly(matrix[row][col], mul_poly(var, poly, use_ba))

    place(0, 0, diagonal)
    place(leaf, leaf, diagonal)
    place(0, leaf, b)
    place(leaf, 0, b)
    return matrix


def multiply_word(calls, leaves=2, use_ba=True):
    acc = mat_id(leaves + 1)
    for stage, primed, use_b in calls:
        acc = mat_mul(pure_factor(stage, primed, leaves, use_b, use_ba), acc, use_ba)
    return acc


def two_stage_target(leaves=2):
    matrix = mat_id(leaves + 1)
    core = one()
    for stage in range(leaves):
        factor = add_poly(one(), stage_var(stage))
        core = mul_poly(factor, core)
        matrix[stage + 1][stage + 1] = factor
    matrix[0][0] = core
    return matrix


def nested_closed_form(outer):
    """Error of a nested pair whose outer stage is `outer` and whose inner stage is adjacent."""
    other = 1 - outer
    a = word_poly(0, outer)
    b = word_poly(1, outer)
    bb = mul_poly(b, b)
    ab = mul_poly(a, b)
    # Outer variable is x when outer=0 and y when outer=1.
    if outer == 0:
        diag = mono(2, 1)
        off_low = mono(1, 1)
        off_high = mono(2, 1)
    else:
        diag = mono(1, 2)
        off_low = mono(1, 1)
        off_high = mono(1, 2)
    diagonal = mul_poly(diag, bb)
    off = add_poly(
        mul_poly(off_low, b),
        mul_poly(off_high, add_poly(b, ab, bb)),
    )
    size = 3
    matrix = mat_zero(size)
    matrix[0][0] = diagonal
    matrix[outer + 1][outer + 1] = diagonal
    matrix[0][outer + 1] = off
    matrix[outer + 1][0] = off
    # The inner leaf is untouched by this error.
    if other not in (0, 1):
        raise AssertionError(other)
    return matrix


def crossed_b0_closed_form():
    """Core error xy[A0,A1](I+y A1)(I+x A0) for order stage0, stage1, stage0', stage1'."""
    a0 = word_poly(0, 0)
    a1 = word_poly(0, 1)
    comm = add_poly(mul_poly(a0, a1), mul_poly(a1, a0))
    right = mul_poly(add_poly(one(), mul_poly(mono(0, 1), a1)), add_poly(one(), mul_poly(mono(1, 0), a0)))
    core = mul_poly(mono(1, 1), mul_poly(comm, right))
    matrix = mat_zero(3)
    matrix[0][0] = core
    return matrix


def coeff(poly, xexp, yexp):
    return add_poly(*(mono(0, 0, word) for xe, ye, word in poly if xe == xexp and ye == yexp))


# --- explicit matrices over GF(2) -------------------------------------------------


def eye(dim):
    return tuple(1 << index for index in range(dim))


def zero_mat(dim):
    return tuple(0 for _ in range(dim))


def is_zero(mat):
    return all(row == 0 for row in mat)


def xor_mat(left, right):
    return tuple(a ^ b for a, b in zip(left, right))


def matmul(left, right):
    dim = len(left)
    columns = [0] * dim
    for row in range(dim):
        bits = right[row]
        column = 0
        while bits:
            low = bits & -bits
            columns[low.bit_length() - 1] |= 1 << row
            bits ^= low
    out = []
    for row_bits in left:
        acc = 0
        for col in range(dim):
            if (row_bits & columns[col]).bit_count() & 1:
                acc |= 1 << col
        out.append(acc)
    return tuple(out)


def mat_rank(rows):
    matrix = list(rows)
    width = len(rows)
    used = 0
    rank = 0
    for col in range(width):
        pivot = next(
            (row for row in range(width) if (used >> row) & 1 == 0 and (matrix[row] >> col) & 1),
            None,
        )
        if pivot is None:
            continue
        used |= 1 << pivot
        rank += 1
        pivot_row = matrix[pivot]
        for row in range(width):
            if row != pivot and (matrix[row] >> col) & 1:
                matrix[row] ^= pivot_row
    return rank


def direct_sum(block, copies):
    small = len(block)
    dim = small * copies
    out = [0] * dim
    for copy in range(copies):
        shift = copy * small
        for row in range(small):
            out[shift + row] = block[row] << shift
    return tuple(out)


def rows_from_bits(bit_rows):
    """bit_rows is a list of strings of 0/1, row-major, column 0 on the left."""
    dim = len(bit_rows)
    out = []
    for text in bit_rows:
        if len(text) != dim:
            raise AssertionError("square bit rows required")
        acc = 0
        for col, bit in enumerate(text):
            if bit == "1":
                acc |= 1 << col
        out.append(acc)
    return tuple(out)


def legal_pair(projector, off):
    return matmul(projector, projector) == projector and xor_mat(
        matmul(projector, off), matmul(off, projector)
    ) == off


def poly_add(left, right):
    out = dict(left)
    for key, value in right.items():
        merged = xor_mat(out[key], value) if key in out else value
        if is_zero(merged):
            out.pop(key, None)
        else:
            out[key] = merged
    return out


def poly_mul(left, right):
    out = {}
    for left_exp, left_mat in left.items():
        for right_exp, right_mat in right.items():
            key = tuple(a + b for a, b in zip(left_exp, right_exp))
            prod = matmul(left_mat, right_mat)
            merged = xor_mat(out[key], prod) if key in out else prod
            if is_zero(merged):
                out.pop(key, None)
            else:
                out[key] = merged
    return out


def block_mul(left, right):
    size = len(left)
    out = [[None] * size for _ in range(size)]
    for row in range(size):
        for col in range(size):
            acc = {}
            for mid in range(size):
                acc = poly_add(acc, poly_mul(left[row][mid], right[mid][col]))
            out[row][col] = acc
    return out


def exp_of(stage, nstages, power=1):
    return tuple(power if index == stage else 0 for index in range(nstages))


def stage_factor_matrix(projector, off, primed, stage, nstages):
    dim = len(projector)
    size = nstages + 1
    if primed:
        diagonal = xor_mat(xor_mat(eye(dim), projector), off)
    else:
        diagonal = xor_mat(projector, off)
    zero_exp = exp_of(0, nstages, 0)
    var = exp_of(stage, nstages)
    blocks = [[{} for _ in range(size)] for _ in range(size)]
    for index in range(size):
        blocks[index][index] = {zero_exp: eye(dim)}

    def add(row, col, matrix):
        if is_zero(matrix):
            return
        current = blocks[row][col]
        merged = xor_mat(current[var], matrix) if var in current else matrix
        if is_zero(merged):
            current.pop(var, None)
        else:
            current[var] = merged

    leaf = stage + 1
    add(0, 0, diagonal)
    add(leaf, leaf, diagonal)
    add(0, leaf, off)
    add(leaf, 0, off)
    return blocks


def identity_blocks(nstages, dim):
    size = nstages + 1
    zero_exp = exp_of(0, nstages, 0)
    blocks = [[{} for _ in range(size)] for _ in range(size)]
    for index in range(size):
        blocks[index][index] = {zero_exp: eye(dim)}
    return blocks


def multiply_calls(stages, calls):
    nstages = len(stages)
    dim = len(stages[0][0])
    acc = identity_blocks(nstages, dim)
    for stage, primed in calls:
        projector, off = stages[stage]
        acc = block_mul(stage_factor_matrix(projector, off, primed, stage, nstages), acc)
    return acc


def target_blocks(nstages, dim):
    zero_exp = exp_of(0, nstages, 0)
    blocks = identity_blocks(nstages, dim)
    core = {zero_exp: eye(dim)}
    for stage in range(nstages):
        var = exp_of(stage, nstages)
        factor = poly_add({zero_exp: eye(dim)}, {var: eye(dim)})
        core = poly_mul(factor, core)
        blocks[stage + 1][stage + 1] = factor
    blocks[0][0] = core
    return blocks


def blocks_equal(left, right):
    if len(left) != len(right):
        return False
    for row in range(len(left)):
        for col in range(len(left)):
            if poly_add(left[row][col], right[row][col]) != {}:
                return False
    return True


def full_projector(projector, off):
    """P on core ⊕ leaf, with the legal block form."""
    dim = len(projector)
    diagonal = xor_mat(projector, off)
    rows = [0] * (2 * dim)
    for index in range(dim):
        rows[index] = diagonal[index] | (off[index] << dim)
        rows[dim + index] = off[index] | (diagonal[index] << dim)
    return tuple(rows)


def commutator_weight(left, right):
    return sum((a ^ b).bit_count() for a, b in zip(matmul(left, right), matmul(right, left)))


def joint_projector(projector, off, stage, nstages):
    """Embed one stage projector on core ⊕ all leaves. Other leaves stay zero."""
    dim = len(projector)
    size = nstages + 1
    rows = [0] * (dim * size)
    diagonal = xor_mat(projector, off)
    leaf = stage + 1

    def paint(block_row, block_col, block):
        for index in range(dim):
            rows[block_row * dim + index] |= block[index] << (block_col * dim)

    paint(0, 0, diagonal)
    paint(leaf, leaf, diagonal)
    paint(0, leaf, off)
    paint(leaf, 0, off)
    return tuple(rows)


def joint_commutator(left_stage, right_stage, nstages):
    left = joint_projector(left_stage[0], left_stage[1], 0, nstages)
    right = joint_projector(right_stage[0], right_stage[1], 1, nstages)
    return commutator_weight(left, right)


def flat_factor(projector, off, primed, stage, nstages, dim):
    """Flat operator I + x_stage P on core ⊕ every leaf. Returns (pure constant, terms)."""
    size = nstages + 1
    n = dim * size
    base = eye(n)
    diagonal = xor_mat(xor_mat(eye(dim), projector), off) if primed else xor_mat(projector, off)
    update = [0] * n

    def paint(block_row, block_col, block):
        for index in range(dim):
            update[block_row * dim + index] |= block[index] << (block_col * dim)

    leaf = stage + 1
    paint(0, 0, diagonal)
    paint(leaf, leaf, diagonal)
    paint(0, leaf, off)
    paint(leaf, 0, off)
    return base, tuple(update)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def symbolic_checks():
    adjacent = (
        (0, False, True),
        (0, True, True),
        (1, False, True),
        (1, True, True),
    )
    require(multiply_word(adjacent) == two_stage_target(), "adjacent pure product")
    reverse = (
        (0, True, True),
        (0, False, True),
        (1, True, True),
        (1, False, True),
    )
    require(multiply_word(reverse) == two_stage_target(), "reversed adjacent halves")
    single = multiply_word(((0, False, True), (0, True, True)), leaves=1)
    expect = mat_id(2)
    scalar = add_poly(one(), stage_var(0))
    expect[0][0] = scalar
    expect[1][1] = scalar
    require(single == expect, "one adjacent stage is the scalar factor")
    single_reverse = multiply_word(((0, True, True), (0, False, True)), leaves=1)
    require(single_reverse == expect, "reversed adjacent stage is the scalar factor")
    broken = multiply_word(((0, False, True), (0, True, True)), leaves=1, use_ba=False)
    require(broken != expect, "dropped BA relation must spoil the stage factor")

    nested_orders = (
        ((0, False, True), (1, False, True), (1, True, True), (0, True, True)),
        ((0, False, True), (1, True, True), (1, False, True), (0, True, True)),
    )
    closed = nested_closed_form(0)
    for calls in nested_orders:
        got = mat_add(multiply_word(calls), two_stage_target())
        require(got == closed, "nested error formula")
    # The outer labeling A -> I+A swaps the two outer calls. The image of the
    # off-diagonal formula is xy B + x^2 y (AB + B^2); the xy term is still B.
    outer_swap = (
        (0, True, True),
        (1, False, True),
        (1, True, True),
        (0, False, True),
    )
    swapped_nested = mat_add(multiply_word(outer_swap), two_stage_target())
    require(coeff(swapped_nested[0][1], 1, 1) == word_poly(1, 0), "swapped nest keeps xy B")
    require(swapped_nested[0][0] == closed[0][0], "swapped nest keeps the diagonal B^2 term")
    swapped_off = add_poly(
        mul_poly(mono(1, 1), word_poly(1, 0)),
        mul_poly(
            mono(2, 1),
            add_poly(mul_poly(word_poly(0, 0), word_poly(1, 0)), mul_poly(word_poly(1, 0), word_poly(1, 0))),
        ),
    )
    require(swapped_nested[0][1] == swapped_off, "swapped nest off-diagonal formula")
    require(swapped_nested[1][0] == swapped_off, "swapped nest leaf-to-core formula")
    outer_one = (
        (1, False, True),
        (0, False, True),
        (0, True, True),
        (1, True, True),
    )
    got_one = mat_add(multiply_word(outer_one), two_stage_target())
    require(got_one == nested_closed_form(1), "nested formula with the other outer stage")
    require(coeff(closed[0][1], 1, 1) == word_poly(1, 0), "nested xy coefficient is the outer B")
    require(closed != mat_zero(3), "nested error is not the zero word")
    # Every labeling of the two complementary calls. Inner B stays free.
    for outer_first in (False, True):
        for inner_first in (False, True):
            error = mat_add(
                multiply_word(
                    (
                        (0, outer_first, True),
                        (1, inner_first, True),
                        (1, not inner_first, True),
                        (0, not outer_first, True),
                    )
                ),
                two_stage_target(),
            )
            require(coeff(error[0][1], 1, 1) == word_poly(1, 0), "nested xy coefficient")
            require(
                multiply_word(
                    (
                        (0, outer_first, False),
                        (1, inner_first, True),
                        (1, not inner_first, True),
                        (0, not outer_first, False),
                    )
                )
                == two_stage_target(),
                "nested matches for every labeling when the outer B vanishes",
            )

    crossed = (
        (0, False, False),
        (1, False, False),
        (0, True, False),
        (1, True, False),
    )
    crossed_error = mat_add(multiply_word(crossed), two_stage_target())
    require(crossed_error == crossed_b0_closed_form(), "crossed B=0 error formula")
    require(
        coeff(crossed_error[0][0], 1, 1)
        == add_poly(mul_poly(word_poly(0, 0), word_poly(0, 1)), mul_poly(word_poly(0, 1), word_poly(0, 0))),
        "crossed xy coefficient is the commutator",
    )
    commutator = add_poly(
        mul_poly(word_poly(0, 0), word_poly(0, 1)),
        mul_poly(word_poly(0, 1), word_poly(0, 0)),
    )
    # Stage 0 starts first and the two intervals cross. Every complement labeling
    # has core coefficient xy equal to the commutator.
    for first_primed in (False, True):
        for other_primed in (False, True):
            error = mat_add(
                multiply_word(
                    (
                        (0, first_primed, False),
                        (1, other_primed, False),
                        (0, not first_primed, False),
                        (1, not other_primed, False),
                    )
                ),
                two_stage_target(),
            )
            require(coeff(error[0][0], 1, 1) == commutator, "crossed xy coefficient")
            require(error != mat_zero(3), "crossed B=0 product is not an identity")


def projector_ok(projector, off, rank):
    require(legal_pair(projector, off), "projector relations")
    require(mat_rank(projector) == rank, "half rank")
    require(mat_rank(xor_mat(projector, eye(len(projector)))) == rank, "complement rank")
    full = full_projector(projector, off)
    require(matmul(full, full) == full, "block projector idempotent")
    require(mat_rank(full) == len(projector), "block projector rank")


def nested_pair_2():
    """Equal halves on F2^2. A0 and A1 do not commute. B_bad is legal and nonzero."""
    a0 = rows_from_bits(("10", "00"))
    a1 = rows_from_bits(("11", "00"))
    b_bad = rows_from_bits(("01", "10"))
    b0 = zero_mat(2)
    require(not is_zero(xor_mat(matmul(a0, a1), matmul(a1, a0))), "seed idempotents commute")
    return a0, a1, b0, b_bad


def crossed_seed_4():
    a0 = rows_from_bits(("1000", "0100", "0000", "0000"))
    a1 = rows_from_bits(("1000", "0000", "0010", "0000"))
    b0 = zero_mat(4)
    b1 = rows_from_bits(("0100", "1000", "0000", "0000"))
    return [(a0, b0), (a1, b1)]


def composition_seed_4():
    """Nested noncommuting pair, then the crossed witness, on one F2^4 core."""
    a0 = rows_from_bits(("1000", "0000", "0010", "0000"))
    a1 = rows_from_bits(("1100", "0000", "0010", "0000"))
    b0 = zero_mat(4)
    crossed = crossed_seed_4()
    return [(a0, b0), (a1, b0), crossed[0], crossed[1]]


def outside_stage(dim):
    """Equal halves with B^2 = I, on a core of dimension dim = 2q."""
    half = dim // 2
    projector = tuple((1 << index) if index < half else 0 for index in range(dim))
    off = tuple((1 << (index + half)) if index < half else (1 << (index - half)) for index in range(dim))
    return projector, off


def scale_pair(pair, copies):
    projector, off = pair
    return direct_sum(projector, copies), direct_sum(off, copies)


def matrix_checks():
    a0, a1, b_clear, b_bad = nested_pair_2()
    for projector, off in ((a0, b_clear), (a1, b_clear), (a0, b_bad)):
        projector_ok(projector, off, 1)
    require(joint_commutator((a0, b_clear), (a1, b_clear), 2) > 0, "nested projectors commute")
    require(joint_commutator((a0, b_bad), (a1, b_clear), 2) > 0, "bad nested projectors commute")

    copies = Q  # d=2 copies give core dimension 2Q and half-rank Q
    big_clear = [scale_pair((a0, b_clear), copies), scale_pair((a1, b_clear), copies)]
    big_bad = [scale_pair((a0, b_bad), copies), scale_pair((a1, b_clear), copies)]
    for stages in (big_clear, big_bad):
        for projector, off in stages:
            projector_ok(projector, off, Q)
    nested_calls = [(0, False), (1, False), (1, True), (0, True)]
    require(
        blocks_equal(multiply_calls(big_clear, nested_calls), target_blocks(2, 2 * Q)),
        "q=26 nested pure product with outer B=0",
    )
    bad_product = multiply_calls(big_bad, nested_calls)
    require(not blocks_equal(bad_product, target_blocks(2, 2 * Q)), "q=26 nested pure product with outer B nonzero")
    # xy coefficient of core-to-leaf0 equals the outer B matrix.
    leaf_poly = bad_product[0][1]
    xy = exp_of(0, 2)  # wrong: xy is (1,1), not a single stage
    xy = (1, 1)
    require(leaf_poly.get(xy) == big_bad[0][1], "q=26 nested xy block is the outer B")

    # B^2=0 but B nonzero still fails, and still has xy coefficient B.
    b_nil = rows_from_bits(("01", "00"))
    projector_ok(a0, b_nil, 1)
    nil_stages = [scale_pair((a0, b_nil), copies), scale_pair((a1, b_clear), copies)]
    nil_product = multiply_calls(nil_stages, nested_calls)
    require(nil_product[0][1].get((1, 1)) == nil_stages[0][1], "nilpotent outer B still appears at xy")
    require(not blocks_equal(nil_product, target_blocks(2, 2 * Q)), "nilpotent outer B meets the nested target")

    seed = crossed_seed_4()
    for projector, off in seed:
        projector_ok(projector, off, 2)
    seed_calls = [(0, False), (1, False), (0, True), (1, True)]
    require(blocks_equal(multiply_calls(seed, seed_calls), target_blocks(2, 4)), "4x4 crossed witness")
    seed_weight = joint_commutator(seed[0], seed[1], 2)
    require(seed_weight > 0, "crossed witness projectors commute")
    crossed_big = [scale_pair(seed[0], 13), scale_pair(seed[1], 13)]
    for projector, off in crossed_big:
        projector_ok(projector, off, Q)
    require(len(crossed_big[0][0]) == 2 * Q, "crossed witness core dimension")
    require(
        blocks_equal(multiply_calls(crossed_big, seed_calls), target_blocks(2, 2 * Q)),
        "q=26 crossed pure-product witness",
    )
    big_weight = joint_commutator(crossed_big[0], crossed_big[1], 2)
    require(big_weight == 13 * seed_weight, "direct sum dropped part of the commutator")

    # B=0 crossed order fails exactly on this noncommuting family, at q=26.
    fail_calls = [(0, False), (1, False), (0, True), (1, True)]
    require(
        not blocks_equal(multiply_calls(big_clear, fail_calls), target_blocks(2, 2 * Q)),
        "noncommuting B=0 crossed product matches",
    )
    # The same matrices in adjacent order match, with or without the bad off-diagonal block.
    adjacent = [(0, False), (0, True), (1, False), (1, True)]
    require(blocks_equal(multiply_calls(big_bad, adjacent), target_blocks(2, 2 * Q)), "adjacent order with B nonzero")

    # Commuting B=0 projectors match in the crossed order. Use a common eigenbasis.
    c0 = rows_from_bits(("1000", "0100", "0000", "0000"))
    c1 = rows_from_bits(("1000", "0000", "0010", "0000"))
    z4 = zero_mat(4)
    projector_ok(c0, z4, 2)
    projector_ok(c1, z4, 2)
    require(matmul(c0, c1) == matmul(c1, c0), "diagonal witness does not commute")
    commuting = [scale_pair((c0, z4), 13), scale_pair((c1, z4), 13)]
    require(
        blocks_equal(multiply_calls(commuting, seed_calls), target_blocks(2, 2 * Q)),
        "commuting B=0 crossed product",
    )
    for first_primed in (False, True):
        for other_primed in (False, True):
            order = [
                (0, first_primed),
                (1, other_primed),
                (0, not first_primed),
                (1, not other_primed),
            ]
            require(
                blocks_equal(multiply_calls(commuting, order), target_blocks(2, 2 * Q)),
                "commuting B=0 crossed labeling",
            )
            require(
                not blocks_equal(multiply_calls(big_clear, order), target_blocks(2, 2 * Q)),
                "noncommuting B=0 crossed labeling",
            )

    # One nested pair followed by one crossed pair, then one adjacent stage outside.
    comp = composition_seed_4()
    for projector, off in comp:
        projector_ok(projector, off, 2)
    require(joint_commutator(comp[0], comp[1], 2) > 0, "composition nested pair commutes")
    require(joint_commutator(comp[2], comp[3], 2) > 0, "composition crossed pair commutes")
    comp_big = [scale_pair(pair, 13) for pair in comp]
    for projector, off in comp_big:
        projector_ok(projector, off, Q)
    comp_calls = [
        (0, False),
        (1, False),
        (1, True),
        (0, True),
        (2, False),
        (3, False),
        (2, True),
        (3, True),
    ]
    require(
        blocks_equal(multiply_calls(comp_big, comp_calls), target_blocks(4, 2 * Q)),
        "q=26 product of one nested pair and one crossed pair",
    )
    outer_a, outer_b = outside_stage(2 * Q)
    projector_ok(outer_a, outer_b, Q)
    with_outside = comp_big + [(outer_a, outer_b)]
    outside_after = comp_calls + [(4, False), (4, True)]
    outside_before = [(4, False), (4, True)] + comp_calls
    require(
        blocks_equal(multiply_calls(with_outside, outside_after), target_blocks(5, 2 * Q)),
        "adjacent stage after the pure product",
    )
    require(
        blocks_equal(multiply_calls(with_outside, outside_before), target_blocks(5, 2 * Q)),
        "adjacent stage before the pure product",
    )

    # The bad nested error survives an adjacent stage on either side.
    bad_with = big_bad + [(outer_a, outer_b)]
    bad_after = nested_calls + [(2, False), (2, True)]
    bad_before = [(2, False), (2, True)] + nested_calls
    after = multiply_calls(bad_with, bad_after)
    before = multiply_calls(bad_with, bad_before)
    require(not blocks_equal(after, target_blocks(3, 2 * Q)), "outside stage repairs a bad nest")
    require(not blocks_equal(before, target_blocks(3, 2 * Q)), "leading stage repairs a bad nest")
    # Outside applied last multiplies the core row by (1+z).
    require(after[0][1].get((1, 1, 0)) == big_bad[0][1], "left scalar constant term")
    require(after[0][1].get((1, 1, 1)) == big_bad[0][1], "left scalar z term")
    # Outside applied first multiplies the leaf0 column by I, so the block is unchanged.
    require(before[0][1].get((1, 1, 0)) == big_bad[0][1], "right scalar kept the outer B")
    require((1, 1, 1) not in before[0][1], "right scalar leaked into the core-leaf block")


def dual_mul(left, right):
    """Polynomials whose coefficients are dual numbers a + e b, with e^2 = 0."""
    out = {}
    for left_exp, (left_pure, left_eps) in left.items():
        for right_exp, (right_pure, right_eps) in right.items():
            key = tuple(a + b for a, b in zip(left_exp, right_exp))
            pure = matmul(left_pure, right_pure)
            eps = xor_mat(matmul(left_pure, right_eps), matmul(left_eps, right_pure))
            current = out.get(key)
            if current is not None:
                pure = xor_mat(current[0], pure)
                eps = xor_mat(current[1], eps)
            if is_zero(pure) and is_zero(eps):
                out.pop(key, None)
            else:
                out[key] = (pure, eps)
    return out


def thin_map_does_not_change_pure_part():
    """I+eZ has pure part I, so it cannot repair a pure-product failure."""
    a0, a1, b_clear, b_bad = nested_pair_2()
    stages = [(a0, b_bad), (a1, b_clear)]
    dim = 2
    nstages = 2
    width = dim * (nstages + 1)
    calls = [(0, False), (1, False), (1, True), (0, True)]
    # Nonzero thin map: the identity on the whole space. Rank is larger than q.
    z_matrix = eye(width)

    def full_factor(stage, primed):
        projector, off = stages[stage]
        base, update = flat_factor(projector, off, primed, stage, nstages, dim)
        var = exp_of(stage, nstages)
        zero_exp = exp_of(0, nstages, 0)
        return {zero_exp: (base, zero_mat(width)), var: (update, zero_mat(width))}

    def thin_factor():
        zero_exp = exp_of(0, nstages, 0)
        return {zero_exp: (eye(width), z_matrix)}

    acc = {exp_of(0, nstages, 0): (eye(width), zero_mat(width))}
    bare = {exp_of(0, nstages, 0): (eye(width), zero_mat(width))}
    for index, (stage, primed) in enumerate(calls):
        if index == 2:
            acc = dual_mul(thin_factor(), acc)
        factor = full_factor(stage, primed)
        acc = dual_mul(factor, acc)
        bare = dual_mul(factor, bare)
    for key, (pure, _eps) in acc.items():
        require(key in bare and bare[key][0] == pure, "thin map changed a pure coefficient")
    for key, (pure, _eps) in bare.items():
        require(key in acc and acc[key][0] == pure, "thin map dropped a pure coefficient")
    # The inserted map really is visible in the e coefficient.
    require(any(not is_zero(eps) for _pure, eps in acc.values()), "thin map was not seen at order e")
    # And the pure part is the failed nested product, already proved nonzero at xy.
    xy = (1, 1)
    require(xy in acc and not is_zero(acc[xy][0]), "pure failure disappeared at the xy term")


def main():
    require(KAPPA == "781451/250000000", "selected frontier constant")
    require(MAPS * Q == 130 and Q * G == 806, "profile arithmetic")
    symbolic_checks()
    matrix_checks()
    thin_map_does_not_change_pure_part()
    print(
        "PASS_G31_Q26_NESTED_CROSSED_PURE"
        f" proof g={G} q={Q} d={2 * Q}"
        " nested_iff_outer_B_zero=1"
        " crossed_B0_iff_commute=1"
        " crossed_pure_witness=1"
        " nested_then_crossed_pure_match=1"
        " endpoint=open"
        f" kappa={KAPPA}"
    )
    print(
        "STATUS proof of the pure-product step;"
        " constructive pure-product witness;"
        " not an endpoint witness;"
        " not a census;"
        " not a heuristic;"
        " not unrestricted nonexistence"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
