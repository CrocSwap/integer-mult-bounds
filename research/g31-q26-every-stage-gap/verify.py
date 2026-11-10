#!/usr/bin/env python3
"""Every-stage internal gaps miss total thin rank 130 at g=31, q=26.

The argument is a proof under the schedule hypothesis in PROOF.md. The
exponent comparison is an exhaustive check of a finite monomial domain. The
q=1 rank comparison is an exhaustive census of 4 by 4 matrices over F_2.
Neither one is a heuristic, and the census is not an input to the bound 403.
"""

from __future__ import annotations

import sys

G = 31
Q = 26
MAPS = 5


def fail(message):
    raise SystemExit(message)


def expect_false(name, fn):
    try:
        fn()
    except SystemExit:
        return
    fail("failure control did not fail: " + name)


# --- noncommutative polynomials in one stage variable, char 2 ---

ZERO = {}
ONE = {(0, ()): 1}
B12 = {(0, ("b",)): 1}
B21 = {(0, ("c",)): 1}


def add(*args):
    out = {}
    for item in args:
        for key, value in item.items():
            if value:
                out[key] = out.get(key, 0) ^ 1
    return {key: value for key, value in out.items() if value}


def mul(left, right):
    out = {}
    for (deg_l, word_l), value_l in left.items():
        if not value_l:
            continue
        for (deg_r, word_r), value_r in right.items():
            if not value_r:
                continue
            key = (deg_l + deg_r, word_l + word_r)
            out[key] = out.get(key, 0) ^ 1
    return {key: value for key, value in out.items() if value}


def smul(expr, degree):
    return {(deg + degree, word): value for (deg, word), value in expr.items()}


def mat_add(*matrices):
    size = len(matrices[0])
    return [
        [add(*[matrix[row][col] for matrix in matrices]) for col in range(size)]
        for row in range(size)
    ]


def mat_mul(left, right):
    size = len(left)
    return [
        [
            add(*[mul(left[row][mid], right[mid][col]) for mid in range(size)])
            for col in range(size)
        ]
        for row in range(size)
    ]


def mat_scale(matrix, degree):
    return [[smul(matrix[row][col], degree) for col in range(len(matrix))] for row in range(len(matrix))]


def eye(size):
    return [[ONE if row == col else ZERO for col in range(size)] for row in range(size)]


def letter(name):
    return {(0, (name,)): 1}


def z_letters(size):
    return [[letter(f"z{row}{col}") for col in range(size)] for row in range(size)]


def plus_projector():
    return [
        [ONE, B12, ZERO, B12],
        [B21, ZERO, B21, ZERO],
        [ZERO, B12, ONE, B12],
        [B21, ZERO, B21, ZERO],
    ]


def minus_projector():
    return [
        [ZERO, B12, ZERO, B12],
        [B21, ONE, B21, ZERO],
        [ZERO, B12, ZERO, B12],
        [B21, ZERO, B21, ONE],
    ]


def sign_image(plus_sign):
    matrix = [[ZERO for _ in range(4)] for _ in range(4)]
    indices = (0, 2) if plus_sign else (1, 3)
    for row in indices:
        for col in indices:
            matrix[row][col] = ONE
    return matrix


def ix(projector):
    return mat_add(eye(len(projector)), projector, mat_scale(projector, 1))


def degree_slice(expr, degree):
    return {(0, word): 1 for (deg, word) in expr if deg == degree and expr[(deg, word)]}


def projector_and_call_identities():
    p_plus = plus_projector()
    p_minus = minus_projector()
    if mat_mul(p_plus, p_plus) != p_plus or mat_mul(p_minus, p_minus) != p_minus:
        fail("halves are not idempotent")
    if mat_mul(p_plus, p_minus) != [[ZERO] * 4 for _ in range(4)]:
        fail("PP' did not vanish")
    if mat_mul(p_minus, p_plus) != [[ZERO] * 4 for _ in range(4)]:
        fail("P'P did not vanish")
    if mat_add(p_plus, p_minus) != eye(4):
        fail("halves do not resolve the stage")
    for first_plus, p_first, p_second in (
        (True, p_plus, p_minus),
        (False, p_minus, p_plus),
    ):
        if mat_mul(ix(p_second), ix(p_first)) != mat_scale(eye(4), 1):
            fail("adjacent halves do not multiply to D I")
        image_first = sign_image(first_plus)
        image_second = sign_image(not first_plus)
        pure = mat_mul(ix(p_second), ix(p_first))
        coeff = mat_add(
            mat_mul(ix(p_second), mat_mul(ix(p_first), image_first)),
            mat_mul(mat_mul(ix(p_second), image_second), ix(p_first)),
        )
        if pure != mat_scale(eye(4), 1):
            fail("full-call pure product is not D I")
        expect = {(1, ()): 1}
        for row in range(2):
            for col in range(2):
                if coeff[row][col + 2] != (expect if row == col else ZERO):
                    fail("core-to-leaf block of two halves is not D I")
                if coeff[row + 2][col] != (expect if row == col else ZERO):
                    fail("leaf-to-core block of two halves is not D I")
    # A diagonal block of B is not a legal off-diagonal solution.
    broken = [row[:] for row in p_plus]
    broken[0] = [add(broken[0][0], letter("H")), broken[0][1], broken[0][2], broken[0][3]]
    if mat_mul(ix(p_minus), ix(broken)) == mat_scale(eye(4), 1):
        fail("a diagonal block of B still multiplied to D I")


def degree_one_is_two_sandwiches():
    """Own-leaf degree 1 equals pi_core (Z P_f + P_s Z), and degree 2 is P_s Z P_f."""
    z_matrix = z_letters(4)
    for p_first, p_second in (
        (plus_projector(), minus_projector()),
        (minus_projector(), plus_projector()),
    ):
        direct = mat_mul(ix(p_second), mat_mul(z_matrix, ix(p_first)))
        square = mat_mul(p_second, mat_mul(z_matrix, p_first))
        formula = mat_add(mat_mul(z_matrix, p_first), mat_mul(p_second, z_matrix))
        for row in range(4):
            for col in range(4):
                if any(deg > 2 for (deg, _word) in direct[row][col]):
                    fail("stage degree exceeded 2")
                if degree_slice(direct[row][col], 2) != square[row][col]:
                    fail("D^2 coefficient is not P_s Z P_f")
        for row in range(2):
            for col in (2, 3):
                if degree_slice(direct[row][col], 1) != formula[row][col]:
                    fail("degree-1 core-to-leaf block is not the two-sandwich form")


def other_leaf_has_no_square():
    """One coordinate outside the stage carries no D^2 core block."""
    size = 5
    stage = [0, 1, 2, 3]
    z_matrix = z_letters(size)

    def embed(local):
        matrix = [[ZERO for _ in range(size)] for _ in range(size)]
        for row in range(4):
            for col in range(4):
                matrix[stage[row]][stage[col]] = local[row][col]
        return matrix

    for local_first, local_second in (
        (plus_projector(), minus_projector()),
        (minus_projector(), plus_projector()),
    ):
        p_first = embed(local_first)
        p_second = embed(local_second)
        direct = mat_mul(ix(p_second), mat_mul(z_matrix, ix(p_first)))
        for row in range(2):
            entry = direct[row][4]
            if any(deg == 2 for (deg, _word) in entry):
                fail("other leaf carries a D^2 core block")
            if degree_slice(entry, 0) != mat_mul(p_first, z_matrix)[row][4]:
                fail("other-leaf degree 0 is not pi_core P_f Z")
            if degree_slice(entry, 1) != mat_mul(p_second, z_matrix)[row][4]:
                fail("other-leaf degree 1 is not pi_core P_s Z")


# --- monomial weights ---

def outside(leaves, stage, leaf):
    exponents = [0] * leaves
    for later in range(stage + 1, leaves):
        exponents[later] = 1
    if leaf < stage:
        exponents[leaf] += 1
    return exponents


def required(leaves, leaf):
    return [1 if index >= leaf else 0 for index in range(leaves)]


def powered(base, stage, power):
    exponents = base[:]
    exponents[stage] += power
    return exponents


def internal_weights(leaves, stage):
    """Map each helped leaf to its rank weight. Own leaf costs 2, neighbors 1."""
    weights = {}
    for leaf in range(leaves):
        base = outside(leaves, stage, leaf)
        matched = []
        for power in (0, 1, 2):
            if powered(base, stage, power) == required(leaves, leaf):
                matched.append(power)
        if not matched:
            continue
        if matched != [1] and matched != [0]:
            fail("a leaf matched two powers or a square: " + str((stage, leaf, matched)))
        power = matched[0]
        if leaf == stage:
            if power != 1:
                fail("own leaf matched on a power other than 1")
            weights[leaf] = 2
        elif leaf == stage - 1:
            if power != 1:
                fail("previous leaf matched on a power other than 1")
            weights[leaf] = 1
        elif leaf == stage + 1:
            if power != 0:
                fail("next leaf matched on a power other than 0")
            weights[leaf] = 1
        else:
            fail("internal gap met a leaf outside {t-1, t, t+1}")
    return weights


def external_weights(leaves, gap):
    weights = {}
    for leaf in range(leaves):
        exponents = [1 if index >= gap else 0 for index in range(leaves)]
        if leaf < gap:
            exponents[leaf] += 1
        if exponents == required(leaves, leaf):
            weights[leaf] = 1
    return weights


def square_multipliers(leaves, stage):
    """Nonzero monomials multiplying the four blocks of P_s Z P_f."""
    later = [1 if index > stage else 0 for index in range(leaves)]
    earlier = [1 if index < stage else 0 for index in range(leaves)]
    both = [1 if index != stage else 0 for index in range(leaves)]
    constant = [0] * leaves
    return {
        "core_from_leaf": later,
        "leaf_from_leaf": constant,
        "core_from_core": both,
        "leaf_from_core": earlier,
    }


def counting_bound(leaves, width):
    heaviest = 0
    attained_four = False
    for stage in range(leaves):
        weights = internal_weights(leaves, stage)
        expected = {stage}
        if stage >= 1:
            expected.add(stage - 1)
        if stage + 1 < leaves:
            expected.add(stage + 1)
        if set(weights) != expected:
            fail("hit set disagrees with the three-leaf closed form")
        total = sum(weights.values())
        if stage in (0, leaves - 1):
            if total != 3:
                fail("an endpoint stage does not have weight 3")
        elif total != 4:
            fail("an interior stage does not have weight 4")
        else:
            attained_four = True
        heaviest = max(heaviest, total)
        for name, exponents in square_multipliers(leaves, stage).items():
            squared = exponents[:]
            squared[stage] += 2
            for leaf in range(leaves):
                if squared == required(leaves, leaf):
                    fail("a square multiplier equals a required monomial " + name)
    if not attained_four:
        fail("no interior stage attained weight 4")
    for gap in range(leaves + 1):
        weights = external_weights(leaves, gap)
        expected = []
        if gap - 1 >= 0:
            expected.append(gap - 1)
        if gap < leaves:
            expected.append(gap)
        if sorted(weights) != expected:
            fail("external cover is not the two adjacent leaves")
        if sum(weights.values()) > 2:
            fail("an external gap has weight above 2")
    if heaviest != 4:
        fail("maximum weight is not 4")
    if (2 * width * leaves) % heaviest != 0:
        fail("the rank quotient is not integral")
    return (2 * width * leaves) // heaviest


# --- q=26 local block, B = 0 ---

def zeros(size):
    return [[0 for _ in range(size)] for _ in range(size)]


def mat_mul_bits(left, right):
    size = len(left)
    out = zeros(size)
    for row in range(size):
        for mid in range(size):
            if left[row][mid]:
                for col in range(size):
                    out[row][col] ^= right[mid][col]
    return out


def mat_add_bits(left, right):
    return [[left[row][col] ^ right[row][col] for col in range(len(left))] for row in range(len(left))]


def rank_bits(matrix):
    rows = [row[:] for row in matrix]
    height = len(rows)
    width = len(rows[0])
    rank = 0
    for col in range(width):
        pivot = None
        for row in range(rank, height):
            if rows[row][col]:
                pivot = row
                break
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for row in range(height):
            if row != rank and rows[row][col]:
                for entry in range(width):
                    rows[row][entry] ^= rows[rank][entry]
        rank += 1
    return rank


def b0_projectors(width):
    size = 4 * width
    plus = zeros(size)
    minus = zeros(size)
    for index in range(width):
        plus[index][index] = 1
        plus[2 * width + index][2 * width + index] = 1
        minus[width + index][width + index] = 1
        minus[3 * width + index][3 * width + index] = 1
    return plus, minus


def leaf_to_core(width):
    size = 4 * width
    matrix = zeros(size)
    for index in range(width):
        matrix[index][2 * width + index] = 1
        matrix[width + index][3 * width + index] = 1
    return matrix


def core_leaf_block(matrix, width):
    return [
        [matrix[row][2 * width + col] for col in range(2 * width)]
        for row in range(2 * width)
    ]


def identity(width):
    return [[1 if row == col else 0 for col in range(width)] for row in range(width)]


def local_identity_control(width):
    plus, minus = b0_projectors(width)
    matrix = leaf_to_core(width)
    for p_first, p_second in ((plus, minus), (minus, plus)):
        square = mat_mul_bits(p_second, mat_mul_bits(matrix, p_first))
        if any(any(row) for row in square):
            fail("leaf-to-core identity has a square")
        degree = mat_add_bits(
            mat_mul_bits(p_first, mat_mul_bits(matrix, p_first)),
            mat_mul_bits(p_second, mat_mul_bits(matrix, p_second)),
        )
        if core_leaf_block(degree, width) != identity(2 * width):
            fail("degree-1 block of the leaf-to-core identity is not I")
    if rank_bits(matrix) != 2 * width:
        fail("leaf-to-core identity does not have rank 2q")


# --- exhaustive q=1 census ---

def rows_from_bits(b12, b21, plus_sign):
    if plus_sign:
        return (
            1 | (b12 << 1) | (b12 << 3),
            (b21) | (b21 << 2),
            (b12 << 1) | (1 << 2) | (b12 << 3),
            b21 | (b21 << 2),
        )
    return (
        (b12 << 1) | (b12 << 3),
        b21 | (1 << 1) | (b21 << 2),
        (b12 << 1) | (b12 << 3),
        b21 | (b21 << 2) | (1 << 3),
    )


def mul_rows(left, right):
    out = [0, 0, 0, 0]
    for row in range(4):
        bits = left[row]
        acc = 0
        if bits & 1:
            acc ^= right[0]
        if bits & 2:
            acc ^= right[1]
        if bits & 4:
            acc ^= right[2]
        if bits & 8:
            acc ^= right[3]
        out[row] = acc
    return (out[0], out[1], out[2], out[3])


def add_rows(left, right):
    return tuple(left[index] ^ right[index] for index in range(4))


def rank_rows(rows):
    active = list(rows)
    rank = 0
    for col in range(4):
        bit = 1 << col
        pivot = None
        for row in range(rank, len(active)):
            if active[row] & bit:
                pivot = row
                break
        if pivot is None:
            continue
        active[rank], active[pivot] = active[pivot], active[rank]
        for row in range(len(active)):
            if row != rank and (active[row] & bit):
                active[row] ^= active[rank]
        rank += 1
    return rank


def rank_core_leaf(rows):
    """Rank of core rows 0, 1 on leaf columns 2, 3."""
    top = ((rows[0] >> 2) & 3)
    bottom = ((rows[1] >> 2) & 3)
    if top == 0 and bottom == 0:
        return 0
    if top == 0 or bottom == 0 or top == bottom:
        return 1
    return 2


def q1_rank_census():
    squarefree = 0
    excess_without_square = False
    for b12 in (0, 1):
        for b21 in (0, 1):
            for first_plus in (True, False):
                p_first = rows_from_bits(b12, b21, first_plus)
                p_second = rows_from_bits(b12, b21, not first_plus)
                for code in range(1 << 16):
                    matrix = (
                        code & 15,
                        (code >> 4) & 15,
                        (code >> 8) & 15,
                        (code >> 12) & 15,
                    )
                    square = mul_rows(p_second, mul_rows(matrix, p_first))
                    degree = add_rows(
                        mul_rows(p_first, mul_rows(matrix, p_first)),
                        mul_rows(p_second, mul_rows(matrix, p_second)),
                    )
                    block_rank = rank_core_leaf(degree)
                    matrix_rank = rank_rows(matrix)
                    if square == (0, 0, 0, 0):
                        squarefree += 1
                        if block_rank > matrix_rank:
                            fail("square-free q=1 block outranks Z")
                    elif block_rank > matrix_rank:
                        excess_without_square = True
    if squarefree != 8 * 4096:
        fail("square-free q=1 count changed")
    if not excess_without_square:
        fail("no q=1 matrix realized the factor-2 excess")


# --- g=3, q=1 assembly ---

WIDTH = 2
LEAVES = 3
SPACE = (LEAVES + 1) * WIDTH


def g_zero():
    return [[0] * SPACE for _ in range(SPACE)]


def g_eye():
    matrix = g_zero()
    for index in range(SPACE):
        matrix[index][index] = 1
    return matrix


def g_mul(left, right):
    out = g_zero()
    for row in range(SPACE):
        for mid in range(SPACE):
            if left[row][mid]:
                for col in range(SPACE):
                    out[row][col] ^= right[mid][col]
    return out


def g_add(left, right):
    return [[left[row][col] ^ right[row][col] for col in range(SPACE)] for row in range(SPACE)]


def g_is_zero(matrix):
    return not any(any(row) for row in matrix)


def poly_add(left, right):
    out = dict(left)
    for key, matrix in right.items():
        summed = matrix if key not in out else g_add(out[key], matrix)
        if g_is_zero(summed):
            out.pop(key, None)
        else:
            out[key] = summed
    return out


def poly_mul(left, right):
    out = {}
    for key_l, matrix_l in left.items():
        for key_r, matrix_r in right.items():
            key = tuple(a + b for a, b in zip(key_l, key_r))
            matrix = g_mul(matrix_l, matrix_r)
            if g_is_zero(matrix):
                continue
            summed = matrix if key not in out else g_add(out[key], matrix)
            if g_is_zero(summed):
                out.pop(key, None)
            else:
                out[key] = summed
    return out


def g_const(matrix):
    if g_is_zero(matrix):
        return {}
    return {tuple(0 for _ in range(LEAVES)): matrix}


def g_var(index):
    exponents = [0] * LEAVES
    exponents[index] = 1
    return tuple(exponents)


def local_halves(b12, b21):
    plus = [
        [1, b12, 0, b12],
        [b21, 0, b21, 0],
        [0, b12, 1, b12],
        [b21, 0, b21, 0],
    ]
    minus = [
        [0, b12, 0, b12],
        [b21, 1, b21, 0],
        [0, b12, 0, b12],
        [b21, 0, b21, 1],
    ]
    return plus, minus


def embed_local(local, stage):
    matrix = g_zero()
    locs = [0, 1, WIDTH * (stage + 1), WIDTH * (stage + 1) + 1]
    for row in range(4):
        for col in range(4):
            matrix[locs[row]][locs[col]] = local[row][col]
    return matrix


def embed_sign(plus_sign, stage):
    matrix = g_zero()
    locs = [0, 1, WIDTH * (stage + 1), WIDTH * (stage + 1) + 1]
    indices = (0, 2) if plus_sign else (1, 3)
    for row in indices:
        for col in indices:
            matrix[locs[row]][locs[col]] = 1
    return matrix


def full_call(projector, image, stage):
    pure = poly_add(g_const(g_add(g_eye(), projector)), {g_var(stage): projector})
    composed = g_mul(projector, image)
    coeff = poly_add(g_const(g_add(image, composed)), {g_var(stage): composed})
    return pure, coeff


def thin_factor(matrix):
    return g_const(g_eye()), g_const(matrix)


def multiply_word(factors):
    pure = g_const(g_eye())
    coeff = {}
    for factor_pure, factor_e in reversed(factors):
        coeff = poly_add(poly_mul(factor_pure, coeff), poly_mul(factor_e, pure))
        pure = poly_mul(factor_pure, pure)
    return pure, coeff


def stage_factors(stage, first_plus, matrix, b12, b21):
    plus, minus = local_halves(b12, b21)
    if first_plus:
        p_first, p_second = plus, minus
    else:
        p_first, p_second = minus, plus
    factors = [
        full_call(embed_local(p_second, stage), embed_sign(not first_plus, stage), stage)
    ]
    if matrix is not None:
        factors.append(thin_factor(matrix))
    factors.append(full_call(embed_local(p_first, stage), embed_sign(first_plus, stage), stage))
    return factors


def word_factors(choices, b12, b21):
    """choices is a list of (first_plus, matrix or None), stage 0 first applied."""
    factors = []
    for stage in reversed(range(LEAVES)):
        first_plus, matrix = choices[stage]
        factors.extend(stage_factors(stage, first_plus, matrix, b12, b21))
    return factors


def core_leaf_polynomial(coeff):
    out = {}
    for key, matrix in coeff.items():
        for leaf in range(LEAVES):
            cols = [WIDTH * (leaf + 1), WIDTH * (leaf + 1) + 1]
            block = [[matrix[row][col] for col in cols] for row in (0, 1)]
            if any(any(row) for row in block):
                out[(leaf, key)] = block
    return out


def predict_one(stage, first_plus, matrix, b12, b21):
    plus, minus = local_halves(b12, b21)
    p_first = plus if first_plus else minus
    p_second = minus if first_plus else plus
    p_f = embed_local(p_first, stage)
    p_s = embed_local(p_second, stage)
    complement = g_eye()
    for index in (0, 1, WIDTH * (stage + 1), WIDTH * (stage + 1) + 1):
        complement[index][index] = 0
    b0 = g_mul(g_mul(g_add(complement, p_f), matrix), g_add(complement, p_s))
    b1 = g_add(
        g_mul(g_mul(g_add(complement, p_f), matrix), p_f),
        g_mul(g_mul(p_s, matrix), g_add(complement, p_s)),
    )
    b2 = g_mul(g_mul(p_s, matrix), p_f)
    predicted = {}
    for leaf in range(LEAVES):
        cols = [WIDTH * (leaf + 1), WIDTH * (leaf + 1) + 1]
        if leaf == stage:
            parts = ((0, b0), (1, b1), (2, b2))
        else:
            parts = (
                (0, g_mul(p_f, matrix)),
                (1, g_mul(p_s, matrix)),
            )
        base = outside(LEAVES, stage, leaf)
        for power, source in parts:
            block = [[source[row][col] for col in cols] for row in (0, 1)]
            if any(any(entry) for entry in block):
                exponents = base[:]
                exponents[stage] += power
                predicted[(leaf, tuple(exponents))] = block
    return predicted


def blocks_equal(left, right):
    if set(left) != set(right):
        return False
    for key in left:
        if left[key] != right[key]:
            return False
    return True


def pattern(seed):
    matrix = g_zero()
    for row in range(SPACE):
        for col in range(SPACE):
            matrix[row][col] = (row * 5 + col * 3 + seed) & 1
    matrix[0][2] ^= 1
    return matrix


def assembly_control():
    for b12 in (0, 1):
        for b21 in (0, 1):
            bare_choices = [(True, None) for _ in range(LEAVES)]
            bare = core_leaf_polynomial(multiply_word(word_factors(bare_choices, b12, b21))[1])
            block = [[1 if row == col else 0 for col in range(2)] for row in range(2)]
            expected_bare = {
                (leaf, tuple(required(LEAVES, leaf))): block for leaf in range(LEAVES)
            }
            if bare != expected_bare:
                fail("bare full calls do not contribute M_j I")
            mixed = [(stage == 1, None) for stage in range(LEAVES)]
            mixed_blocks = core_leaf_polynomial(multiply_word(word_factors(mixed, b12, b21))[1])
            if mixed_blocks != bare:
                fail("a mixed half order changed the bare core-to-leaf blocks")
            for stage in range(LEAVES):
                for first_plus in (True, False):
                    matrix = pattern(stage + 4 * int(first_plus) + 8 * b12 + 2 * b21)
                    choices = [(True, None) for _ in range(LEAVES)]
                    choices[stage] = (first_plus, matrix)
                    got = core_leaf_polynomial(
                        poly_add(
                            multiply_word(word_factors(choices, b12, b21))[1],
                            multiply_word(word_factors(bare_choices, b12, b21))[1],
                        )
                    )
                    if not blocks_equal(got, predict_one(stage, first_plus, matrix, b12, b21)):
                        fail("global core-to-leaf polynomial disagrees with lambda")
            left = pattern(1)
            right = pattern(2)
            both = g_add(left, right)
            single = [(True, None) for _ in range(LEAVES)]
            pair = [(True, None) for _ in range(LEAVES)]
            pair[0] = (True, left)
            pair[1] = (False, right)
            # Adding the maps inside one gap is separate from two stages.
            gap_choices = [(True, None) for _ in range(LEAVES)]
            gap_choices[1] = (False, both)
            gap_left = [(True, None) for _ in range(LEAVES)]
            gap_left[1] = (False, left)
            gap_right = [(True, None) for _ in range(LEAVES)]
            gap_right[1] = (False, right)
            bare_coeff = multiply_word(word_factors(single, b12, b21))[1]
            diff_both = poly_add(multiply_word(word_factors(gap_choices, b12, b21))[1], bare_coeff)
            diff_left = poly_add(multiply_word(word_factors(gap_left, b12, b21))[1], bare_coeff)
            diff_right = poly_add(multiply_word(word_factors(gap_right, b12, b21))[1], bare_coeff)
            if poly_add(diff_both, poly_add(diff_left, diff_right)):
                fail("two maps in one gap did not add")
            zero_choices = [(True, g_zero()) for _ in range(LEAVES)]
            if poly_add(multiply_word(word_factors(zero_choices, b12, b21))[1], bare_coeff):
                fail("zero internal maps changed the e coefficient")
            two = poly_add(multiply_word(word_factors(pair, b12, b21))[1], bare_coeff)
            one_left = poly_add(
                multiply_word(word_factors([(True, left), (True, None), (True, None)], b12, b21))[1],
                bare_coeff,
            )
            one_right = poly_add(
                multiply_word(word_factors([(True, None), (False, right), (True, None)], b12, b21))[1],
                bare_coeff,
            )
            if poly_add(two, poly_add(one_left, one_right)):
                fail("internal maps at two stages did not add")
    # B = 0, leaf-to-core identity in every stage cancels every core-to-leaf block.
    stages = []
    for stage in range(LEAVES):
        matrix = g_zero()
        matrix[0][WIDTH * (stage + 1)] = 1
        matrix[1][WIDTH * (stage + 1) + 1] = 1
        stages.append((True, matrix))
    cancelled = core_leaf_polynomial(multiply_word(word_factors(stages, 0, 0))[1])
    if cancelled:
        fail("leaf-to-core identities left a core-to-leaf monomial")


def gap_two_does_not_carry_leaf_zero():
    exponents = [1 if index >= 2 else 0 for index in range(G)]
    if exponents != required(G, 0):
        fail("gap 2 does not carry the leaf-0 monomial")


def weight_16_does_not_separate():
    if 16 * (MAPS * Q) >= 2 * Q * G:
        fail("weight 16 does not separate 130 from 2 q g")


def main():
    projector_and_call_identities()
    degree_one_is_two_sandwiches()
    other_leaf_has_no_square()
    lower = counting_bound(G, Q)
    counting_bound(4, 1)
    if lower != Q * G // 2:
        fail("bound arithmetic")
    if 4 * lower != 2 * Q * G:
        fail("weight 4 does not recover 2 q g")
    profile = MAPS * Q
    if not profile < lower:
        fail("profile is not below the every-stage bound")
    if lower == Q * (G - 3):
        fail("the every-stage bound collapsed to the one-gap bound")
    local_identity_control(Q)
    local_identity_control(1)
    q1_rank_census()
    assembly_control()
    expect_false("non-adjacent external gap", gap_two_does_not_carry_leaf_zero)
    expect_false("weight 16 separates", weight_16_does_not_separate)
    print(
        "PASS_G31_Q26_EVERY_STAGE_GAP"
        f" proof g={G} q={Q} d={2 * Q}"
        f" lower_total_rank={lower} profile_total_rank={profile}"
        " max_weight=4"
    )
    print(
        "STATUS proof under one internal thin gap in every ordered stage;"
        " q=1 square-free rank comparison is an exhaustive 4-by-4 census;"
        " not a heuristic; not unrestricted nonexistence; no kappa change"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
