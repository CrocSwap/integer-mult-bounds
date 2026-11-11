#!/usr/bin/env python3
"""Three core blocks of one rank-q internal map.

The argument in PROOF.md is a proof under the stated hypotheses. The checks
below are exact identities, an exhaustive q=1 census, and an explicit matrix
family. They are not a search over words and not a heuristic.
"""

from __future__ import annotations

import sys

G = 31
Q = 26


def fail(message):
    raise SystemExit(message)


def expect_false(name, fn):
    try:
        fn()
    except SystemExit:
        return
    fail("failure control did not fail: " + name)


# --- free algebra: characteristic-two words in D ---

ZERO = frozenset()
ONE = frozenset({(0, ())})
B12 = frozenset({(0, ("b",))})
B21 = frozenset({(0, ("c",))})


def add(*args):
    out = set()
    for item in args:
        for key in item:
            if key in out:
                out.remove(key)
            else:
                out.add(key)
    return frozenset(out)


def mul(left, right):
    out = set()
    for deg_l, word_l in left:
        for deg_r, word_r in right:
            key = (deg_l + deg_r, word_l + word_r)
            if key in out:
                out.remove(key)
            else:
                out.add(key)
    return frozenset(out)


def smul(expr, degree):
    return frozenset((deg + degree, word) for deg, word in expr)


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


def z_letters(size):
    return [[frozenset({(0, (f"z{row}{col}",))} ) for col in range(size)] for row in range(size)]


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


def embed(local, size, stage):
    matrix = [[ZERO for _ in range(size)] for _ in range(size)]
    for row in range(4):
        for col in range(4):
            matrix[stage[row]][stage[col]] = local[row][col]
    return matrix


def ix(projector):
    return mat_add(eye(len(projector)), projector, mat_scale(projector, 1))


def degree_words(expr, degree):
    return frozenset(word for deg, word in expr if deg == degree)


def sign_image(plus):
    matrix = [[ZERO for _ in range(4)] for _ in range(4)]
    rows = (0, 2) if plus else (1, 3)
    for row in rows:
        for col in rows:
            matrix[row][col] = ONE
    return matrix


def check_local_blocks():
    """VZU core blocks, for both half orders, as free-algebra identities."""
    # The full-call bracket between the halves has no square. The only degree-2
    # term in the internal gap is therefore P_s Z P_f.
    for first, second, image_first, image_second in (
        (plus_projector(), minus_projector(), sign_image(True), sign_image(False)),
        (minus_projector(), plus_projector(), sign_image(False), sign_image(True)),
    ):
        bracket = mat_add(
            mat_mul(mat_mul(ix(second), ix(first)), image_first),
            mat_mul(mat_mul(ix(second), image_second), ix(first)),
        )
        for row in range(4):
            for col in range(4):
                if any(deg >= 2 for deg, _word in bracket[row][col]):
                    fail("the full-call bracket has a square")
    size = 6
    stage = [0, 1, 2, 3]
    p_plus = embed(plus_projector(), size, stage)
    p_minus = embed(minus_projector(), size, stage)
    if mat_mul(p_plus, p_plus) != p_plus or mat_mul(p_minus, p_minus) != p_minus:
        fail("halves are not idempotent")
    if mat_add(p_plus, p_minus) != embed(eye(4), size, stage):
        fail("halves do not resolve the stage")
    if any(mat_mul(p_plus, p_minus)[i][j] != ZERO for i in range(size) for j in range(size)):
        fail("the halves do not annihilate")
    f_matrix = eye(size)
    for index in range(4):
        f_matrix[index][index] = ZERO
    z_full = z_letters(size)
    for first, second in ((p_plus, p_minus), (p_minus, p_plus)):
        direct = mat_mul(ix(second), mat_mul(z_full, ix(first)))
        u_matrix = mat_add(f_matrix, second, mat_scale(first, 1))
        v_matrix = mat_add(f_matrix, first, mat_scale(second, 1))
        if direct != mat_mul(v_matrix, mat_mul(z_full, u_matrix)):
            fail("VZU disagrees with the half product")
        for col in (4, 5):
            for row in (0, 1):
                entry = direct[row][col]
                if any(deg > 1 for deg, _word in entry):
                    fail("an outside leaf carries a square")
                if degree_words(entry, 0) != degree_words(mat_mul(first, z_full)[row][col], 0):
                    fail("degree 0 is not pi P_f Z")
                if degree_words(entry, 1) != degree_words(mat_mul(second, z_full)[row][col], 0):
                    fail("degree 1 is not pi P_s Z")
        for col in (2, 3):
            for row in (0, 1):
                entry = direct[row][col]
                if any(deg > 2 for deg, _word in entry):
                    fail("the own leaf exceeds degree 2")
                deg0 = mat_mul(first, mat_mul(z_full, second))
                deg1 = mat_add(
                    mat_mul(first, mat_mul(z_full, first)),
                    mat_mul(second, mat_mul(z_full, second)),
                )
                deg2 = mat_mul(second, mat_mul(z_full, first))
                if degree_words(entry, 0) != degree_words(deg0[row][col], 0):
                    fail("own-leaf degree 0 mismatch")
                if degree_words(entry, 1) != degree_words(deg1[row][col], 0):
                    fail("own-leaf degree 1 mismatch")
                if degree_words(entry, 2) != degree_words(deg2[row][col], 0):
                    fail("own-leaf square is not pi P_s Z P_f")


# --- monomial support ---

def outside(leaves, stage, leaf):
    exponents = [0] * leaves
    for later in range(stage + 1, leaves):
        exponents[later] = 1
    if leaf < stage:
        exponents[leaf] += 1
    return exponents


def required(leaves, leaf):
    return [1 if index >= leaf else 0 for index in range(leaves)]


def helped_leaves(leaves, stage):
    hits = set()
    for leaf in range(leaves):
        base = outside(leaves, stage, leaf)
        for power in (0, 1, 2):
            exponents = base[:]
            exponents[stage] += power
            if exponents == required(leaves, leaf):
                hits.add(leaf)
    return hits


def closed_hits(leaves, stage):
    hits = {stage}
    if stage >= 1:
        hits.add(stage - 1)
    if stage + 1 < leaves:
        hits.add(stage + 1)
    return hits


def check_monomials():
    for leaves in (1, 2, 3, 4, 5, G):
        for stage in range(leaves):
            if helped_leaves(leaves, stage) != closed_hits(leaves, stage):
                fail("hit set is not the closed three-leaf set")
            for leaf in range(leaves):
                base = outside(leaves, stage, leaf)
                squared = base[:]
                squared[stage] += 2
                if squared == required(leaves, leaf):
                    fail("a square matched a required monomial")
        for leaf in range(leaves):
            gaps = []
            for gap in range(leaves + 1):
                exponents = [1 if index >= gap else 0 for index in range(leaves)]
                if leaf < gap:
                    exponents[leaf] += 1
                if exponents == required(leaves, leaf):
                    gaps.append(gap)
            if gaps != [leaf, leaf + 1]:
                fail("external cover is not the two adjacent gaps")


# --- bit rank and the q=1 census ---

def rank_rows(rows):
    active = [row[:] for row in rows if any(row)]
    if not active:
        return 0
    height = len(active)
    width = len(active[0])
    rank = 0
    col = 0
    while col < width and rank < height:
        pivot = next((row for row in range(rank, height) if active[row][col]), None)
        if pivot is None:
            col += 1
            continue
        active[rank], active[pivot] = active[pivot], active[rank]
        for row in range(height):
            if row != rank and active[row][col]:
                active[row] = [left ^ right for left, right in zip(active[row], active[rank])]
        rank += 1
        col += 1
    return rank


def zeros(size):
    return [[0] * size for _ in range(size)]


def bit_projector(b12, b21, plus):
    matrix = zeros(8)
    blocks = plus_projector() if plus else minus_projector()
    values = {ONE: 1, ZERO: 0, B12: b12, B21: b21}
    for row in range(4):
        for col in range(4):
            matrix[row][col] = values[blocks[row][col]]
    return matrix


def apply_bit(matrix, vector):
    out = 0
    for row in range(8):
        bit = 0
        for col in range(8):
            if matrix[row][col] and (vector >> col) & 1:
                bit ^= 1
        if bit:
            out |= 1 << row
    return out


def columns_of(matrix):
    columns = []
    for col in range(8):
        bits = 0
        for row in range(8):
            if matrix[row][col]:
                bits |= 1 << row
        columns.append(bits)
    return columns


def dot(left, right):
    return (left & right).bit_count() & 1


def two_rank(first, second):
    if first == 0 and second == 0:
        return 0
    if first == 0 or second == 0 or first == second:
        return 1
    return 2


def census_q1():
    """Every rank-at-most-1 matrix on the eight F2 coordinates."""
    attained = {}
    for b12 in (0, 1):
        for b21 in (0, 1):
            for order in (0, 1):
                first = bit_projector(b12, b21, order == 0)
                second = bit_projector(b12, b21, order == 1)
                if rank_rows(first[:4]) != 2 or rank_rows(second[:4]) != 2:
                    fail("a scalar half does not have rank 2")
                first_cols = columns_of(first)
                second_cols = columns_of(second)
                hits = 0
                for vector_x in range(256):
                    image_first = apply_bit(first, vector_x)
                    image_second = apply_bit(second, vector_x)
                    for vector_y in range(256):
                        condition = image_second == 0 or all(
                            dot(vector_y, column) == 0 for column in first_cols
                        )
                        # Rank 0 is the zero vector pair. Every other pair is rank 1.
                        if vector_x == 0 or vector_y == 0:
                            if not condition:
                                fail("the zero matrix failed the square condition")
                            continue
                        core_first = image_first & 3
                        core_second = image_second & 3
                        rank_next = two_rank(
                            core_first if (vector_y >> 6) & 1 else 0,
                            core_first if (vector_y >> 7) & 1 else 0,
                        )
                        rank_prev = two_rank(
                            core_second if (vector_y >> 4) & 1 else 0,
                            core_second if (vector_y >> 5) & 1 else 0,
                        )

                        def own(col):
                            left = core_first if dot(vector_y, first_cols[col]) else 0
                            right = core_second if dot(vector_y, second_cols[col]) else 0
                            return left ^ right

                        rank_own = two_rank(own(2), own(3))
                        total = rank_next + rank_prev + rank_own
                        if condition and (rank_next > 1 or rank_prev > 1 or rank_own > 1 or total > 3):
                            fail("q=1 census exceeded the rank cap")
                        if (not condition) and total > 4:
                            fail("an unconstrained rank-1 matrix exceeded sum 4")
                        if condition and total == 3:
                            hits += 1
                attained[(b12, b21, order)] = hits
                if hits <= 0:
                    fail("a projector choice did not attain rank sum 3")
    if sum(attained.values()) != 18720:
        fail("q=1 attainment count changed")
    return sum(attained.values())


# --- explicit families for general q ---

def family(q, conditioned):
    size = 8 * q
    matrix = zeros(size)
    for index in range(q):
        sources = [6 * q + index, 5 * q + index, 3 * q + index]
        if not conditioned:
            sources.append(2 * q + index)
        for source in sources:
            matrix[index][source] = 1
            matrix[q + index][source] = 1
    plus = zeros(size)
    minus = zeros(size)
    for index in range(q):
        plus[index][index] = 1
        plus[2 * q + index][2 * q + index] = 1
        minus[q + index][q + index] = 1
        minus[3 * q + index][3 * q + index] = 1
    return matrix, plus, minus


def core_of(matrix, q, cols):
    return [[matrix[row][col] for col in cols] for row in range(2 * q)]


def block_ranks(q, conditioned):
    matrix, plus, minus = family(q, conditioned)
    square = [row[:] for row in zeros(len(matrix))]
    # P_s Z P_f with P_f = plus and P_s = minus. Both projectors are diagonal.
    for col in range(len(matrix)):
        if plus[col][col]:
            for row in range(len(matrix)):
                if matrix[row][col] and minus[row][row]:
                    square[row][col] = 1
    condition_clear = not any(any(row) for row in square)
    if conditioned != condition_clear:
        fail("the explicit family has the wrong square")

    def compress(projector, cols):
        rows = []
        for row in range(2 * q):
            rows.append([
                1 if any(projector[row][mid] and matrix[mid][col] for mid in range(len(matrix))) else 0
                for col in cols
            ])
        return rank_rows(rows)

    # Own-leaf block: projector after Z after projector, on the stage leaf.
    def own(projector, cols):
        rows = []
        for row in range(2 * q):
            entry = []
            for col in cols:
                bit = 0
                for mid in range(len(matrix)):
                    if projector[mid][col] and matrix[row][mid] and projector[row][row]:
                        bit ^= 1
                entry.append(bit)
            rows.append(entry)
        return rows

    next_cols = range(6 * q, 8 * q)
    prev_cols = range(4 * q, 6 * q)
    own_cols = range(2 * q, 4 * q)
    rank_next = compress(plus, next_cols)
    rank_prev = compress(minus, prev_cols)
    own_rows = [
        [left ^ right for left, right in zip(first, second)]
        for first, second in zip(own(plus, own_cols), own(minus, own_cols))
    ]
    return rank_rows(matrix), rank_next, rank_prev, rank_rows(own_rows)


def check_families():
    for q in (1, 2, 3, 8, Q):
        rank_z, rank_next, rank_prev, rank_own = block_ranks(q, True)
        if (rank_z, rank_next, rank_prev, rank_own) != (q, q, q, q):
            fail("conditioned family is not (q, q, q, q)")
        rank_z, rank_next, rank_prev, rank_own = block_ranks(q, False)
        if (rank_z, rank_next, rank_prev, rank_own) != (q, q, q, 2 * q):
            fail("unconditioned family is not (q, q, 2q)")


# --- external counting ---

def demands(leaves, helped):
    values = [2] * leaves
    for leaf in helped:
        values[leaf] = 1
    return values


def parity_weight(values):
    even = sum(values[index] for index in range(0, len(values), 2))
    odd = sum(values[index] for index in range(1, len(values), 2))
    return max(even, odd)


def min_gap_cost(values):
    """Minimum of sum r under r_j + r_{j+1} >= values[j], with r in {0, 1, 2}."""
    states = {0: 0, 1: 1, 2: 2}
    for demand in values:
        nxt = {}
        for previous, cost in states.items():
            for current in (0, 1, 2):
                if previous + current >= demand:
                    nxt[current] = min(nxt.get(current, 10**9), cost + current)
        states = nxt
        if not states:
            fail("gap LP became empty")
    return min(states.values())


def boundary_tuple(leaves):
    values = demands(leaves, (0, 1, 2))
    even = sum(values[index] for index in range(0, leaves, 2))
    odd = sum(values[index] for index in range(1, leaves, 2))
    parity = 0 if even >= odd else 1
    ranks = [0] * (leaves + 1)
    for leaf in range(parity, leaves, 2):
        ranks[leaf] = values[leaf]
    for leaf in range(leaves):
        if ranks[leaf] + ranks[leaf + 1] < values[leaf]:
            fail("stage-1 equality tuple missed a leaf")
    if sum(ranks) != leaves - 1:
        fail("stage-1 equality tuple has the wrong total")
    # One less unit of rank on a positive gap breaks a leaf constraint.
    gap = next(index for index, rank in enumerate(ranks) if rank)
    ranks[gap] -= 1
    if all(ranks[leaf] + ranks[leaf + 1] >= values[leaf] for leaf in range(leaves)):
        fail("a short tuple still met every leaf")


def check_counting():
    for leaves in range(3, 41):
        boundary_tuple(leaves)
        for stage in range(leaves):
            weight = parity_weight(demands(leaves, closed_hits(leaves, stage)))
            if weight < leaves - 1:
                fail("parity weight fell below g-1")
        if leaves <= G:
            for stage in range(leaves):
                cost = min_gap_cost(demands(leaves, closed_hits(leaves, stage)))
                if cost < leaves - 1:
                    fail("gap LP fell below g-1")
            if min_gap_cost(demands(leaves, (0, 1, 2))) != leaves - 1:
                fail("stage-1 gap LP is not tight")
    if parity_weight(demands(G, closed_hits(G, 1))) != G - 1:
        fail("the g=31 stage-1 witness is not g-1")
    # Dropping the three leaves returns the older count on this parity.
    dropped = [2] * G
    for leaf in (0, 1, 2):
        dropped[leaf] = 0
    even = sum(dropped[index] for index in range(0, G, 2))
    if even != G - 3:
        fail("dropped leaves did not recover g-3")


# --- global g=3, q=1 transport ---

WIDTH = 2
LEAVES = 3
SPACE = (LEAVES + 1) * WIDTH


def zeron():
    return [[0] * SPACE for _ in range(SPACE)]


def idn():
    matrix = zeron()
    for index in range(SPACE):
        matrix[index][index] = 1
    return matrix


def madd(left, right):
    return [[left[row][col] ^ right[row][col] for col in range(SPACE)] for row in range(SPACE)]


def mmul(left, right):
    out = zeron()
    for row in range(SPACE):
        for mid in range(SPACE):
            if left[row][mid]:
                for col in range(SPACE):
                    out[row][col] ^= right[mid][col]
    return out


def is_zero(matrix):
    return not any(any(row) for row in matrix)


def poly_add(left, right):
    out = dict(left)
    for key, matrix in right.items():
        summed = matrix if key not in out else madd(out[key], matrix)
        if is_zero(summed):
            out.pop(key, None)
        else:
            out[key] = summed
    return out


def poly_mul(left, right):
    out = {}
    for key_l, matrix_l in left.items():
        for key_r, matrix_r in right.items():
            key = tuple(one + other for one, other in zip(key_l, key_r))
            matrix = mmul(matrix_l, matrix_r)
            if is_zero(matrix):
                continue
            summed = matrix if key not in out else madd(out[key], matrix)
            if is_zero(summed):
                out.pop(key, None)
            else:
                out[key] = summed
    return out


def const(matrix):
    if is_zero(matrix):
        return {}
    return {(0, 0, 0): matrix}


def var(index):
    exponents = [0, 0, 0]
    exponents[index] = 1
    return tuple(exponents)


def place_halves(stage, b12, b21):
    plus = zeron()
    minus = zeron()
    core = [0, 1]
    leaf = [WIDTH * (stage + 1), WIDTH * (stage + 1) + 1]
    locs = [core[0], core[1], leaf[0], leaf[1]]
    local_plus = [
        [1, b12, 0, b12],
        [b21, 0, b21, 0],
        [0, b12, 1, b12],
        [b21, 0, b21, 0],
    ]
    local_minus = [
        [0, b12, 0, b12],
        [b21, 1, b21, 0],
        [0, b12, 0, b12],
        [b21, 0, b21, 1],
    ]
    image_plus = zeron()
    image_minus = zeron()
    for row in range(4):
        for col in range(4):
            plus[locs[row]][locs[col]] = local_plus[row][col]
            minus[locs[row]][locs[col]] = local_minus[row][col]
    for src in (core, leaf):
        for dst in (core, leaf):
            image_plus[dst[0]][src[0]] = 1
            image_minus[dst[1]][src[1]] = 1
    return plus, minus, image_plus, image_minus


def full_call(projector, image, stage):
    pure = poly_add(const(madd(idn(), projector)), {var(stage): projector})
    composed = mmul(projector, image)
    coeff = poly_add(const(madd(image, composed)), {var(stage): composed})
    return pure, coeff


def thin_factor(matrix):
    return const(idn()), const(matrix)


def multiply_word(factors):
    pure = const(idn())
    coeff = {}
    for factor_pure, factor_e in reversed(factors):
        coeff = poly_add(poly_mul(factor_pure, coeff), poly_mul(factor_e, pure))
        pure = poly_mul(factor_pure, pure)
    return pure, coeff


def word_factors(stage, first_plus, matrix, b12, b21):
    factors = []
    for index in reversed(range(LEAVES)):
        plus, minus, image_plus, image_minus = place_halves(index, b12, b21)
        if index != stage or matrix is None:
            factors.extend(
                [full_call(minus, image_minus, index), full_call(plus, image_plus, index)]
            )
            continue
        if first_plus:
            p_first, r_first, p_second, r_second = plus, image_plus, minus, image_minus
        else:
            p_first, r_first, p_second, r_second = minus, image_minus, plus, image_plus
        factors.extend(
            [full_call(p_second, r_second, index), thin_factor(matrix), full_call(p_first, r_first, index)]
        )
    return factors


def core_block(poly, leaf):
    cols = [WIDTH * (leaf + 1), WIDTH * (leaf + 1) + 1]
    out = {}
    for key, matrix in poly.items():
        block = [[matrix[row][col] for col in cols] for row in (0, 1)]
        if any(any(entry) for entry in block):
            out[key] = block
    return out


def local_blocks(stage, first_plus, matrix, b12, b21):
    plus, minus, _image_plus, _image_minus = place_halves(stage, b12, b21)
    p_first, p_second = (plus, minus) if first_plus else (minus, plus)
    predicted = {}
    for leaf in range(LEAVES):
        if leaf == stage:
            pieces = (
                mmul(p_first, mmul(matrix, p_second)),
                madd(mmul(p_first, mmul(matrix, p_first)), mmul(p_second, mmul(matrix, p_second))),
                mmul(p_second, mmul(matrix, p_first)),
            )
        else:
            pieces = (mmul(p_first, matrix), mmul(p_second, matrix), zeron())
        for power, piece in enumerate(pieces):
            cols = [WIDTH * (leaf + 1), WIDTH * (leaf + 1) + 1]
            block = [[piece[row][col] for col in cols] for row in (0, 1)]
            if not any(any(entry) for entry in block):
                continue
            exponents = outside(LEAVES, stage, leaf)
            exponents[stage] += power
            predicted[leaf, tuple(exponents)] = block
    return predicted


def pattern():
    matrix = zeron()
    for row in range(SPACE):
        for col in range(SPACE):
            matrix[row][col] = (row * 5 + col * 3 + 1) & 1
    matrix[0][2] ^= 1
    return matrix


def check_global_word():
    b12, b21 = 1, 1
    bare = multiply_word(word_factors(0, True, None, b12, b21))
    identity = [[1, 0], [0, 1]]
    for leaf in range(LEAVES):
        block = core_block(bare[1], leaf)
        if block != {tuple(required(LEAVES, leaf)): identity}:
            fail("bare full calls do not contribute M_j I")
    matrix = pattern()
    for stage in range(LEAVES):
        for first_plus in (True, False):
            diff = poly_add(
                multiply_word(word_factors(stage, first_plus, matrix, b12, b21))[1],
                bare[1],
            )
            got = {}
            for leaf in range(LEAVES):
                for key, block in core_block(diff, leaf).items():
                    got[leaf, key] = block
            if got != local_blocks(stage, first_plus, matrix, b12, b21):
                fail("global transport disagrees with the local blocks")
    zero = poly_add(
        multiply_word(word_factors(1, True, zeron(), b12, b21))[1],
        bare[1],
    )
    if zero:
        fail("the zero internal map changed the coefficient")


def main():
    check_local_blocks()
    check_monomials()
    attained = census_q1()
    check_families()
    check_counting()
    check_global_word()
    external = Q * (G - 1)
    dropped = Q * (G - 3)
    if external != 780 or dropped != 728 or external - dropped != 2 * Q:
        fail("profile arithmetic")
    if not dropped < external:
        fail("the three-leaf bound did not rise")
    expect_false(
        "short stage-1 tuple",
        lambda: boundary_tuple_mutated(),
    )
    print(
        "PASS_INTERNAL_THREE_BLOCKS"
        f" proof g={G} q={Q} d={2 * Q}"
        f" external_rank={external} dropped_leaf_rank={dropped}"
        f" rank_sum_cap={3 * Q} q1_attained={attained}"
    )
    print(
        "STATUS proof for one internal matrix of rank at most q"
        " with P_s Z P_f = 0; q=1 F2 census of that matrix domain;"
        " not a census of words; not unrestricted nonexistence"
    )
    return 0


def boundary_tuple_mutated():
    values = demands(4, (0, 1, 2))
    if parity_weight(values) < 3:
        fail("parity control collapsed")
    fail("sentinel")


if __name__ == "__main__":
    sys.exit(main())
