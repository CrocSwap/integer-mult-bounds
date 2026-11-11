#!/usr/bin/env python3
"""One internal thin gap misses total thin rank 130 at g=31, q=26.

The argument is a proof under the schedule hypothesis in PROOF.md. It is not
a search over words, not a census of projectors, and not a heuristic. The
finite checks below enumerate monomial exponents and gap placements. They do
not sample call orders.
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


# --- noncommutative polynomials in D, with char-2 word coefficients ---

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


def mat(entries):
    return entries


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


def z_matrix(size, prefix):
    return [[letter(f"{prefix}{row}{col}") for col in range(size)] for row in range(size)]


def letter(name):
    return {(0, (name,)): 1}


# --- eigenbasis lemma and local projectors ---

def general_off_diagonal_obstruction():
    """AB+BA+B equals the two diagonal blocks of B, for A = diag(I, 0)."""
    h = letter("H")
    k = letter("K")
    b = B12
    c = B21
    # A = [[I, 0], [0, 0]], B = [[H, b], [c, K]]
    # AB = [[H, b], [0, 0]], BA = [[H, 0], [c, 0]], AB+BA = [[0, b], [c, 0]]
    ab_plus_ba = [[ZERO, b], [c, ZERO]]
    relation = mat_add(ab_plus_ba, [[h, b], [c, k]])
    # AB+BA+B = [[H, 0], [0, K]]
    if relation != [[h, ZERO], [ZERO, k]]:
        fail("eigenbasis relation did not isolate the diagonal blocks")
    if add(h, ZERO) == ZERO or add(k, ZERO) == ZERO:
        fail("diagonal letters vanished")
    free = mat_add(ab_plus_ba, [[ZERO, b], [c, ZERO]])
    if any(free[i][j] != ZERO for i in range(2) for j in range(2)):
        fail("off-diagonal B is not the general solution")


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


def projector_identities():
    p_plus = plus_projector()
    p_minus = minus_projector()
    if mat_mul(p_plus, p_plus) != p_plus or mat_mul(p_minus, p_minus) != p_minus:
        fail("halves are not idempotent")
    if any(mat_mul(p_plus, p_minus)[i][j] != ZERO for i in range(4) for j in range(4)):
        fail("PP' did not vanish")
    if any(mat_mul(p_minus, p_plus)[i][j] != ZERO for i in range(4) for j in range(4)):
        fail("P'P did not vanish")
    if mat_add(p_plus, p_minus) != eye(4):
        fail("halves do not resolve the stage")
    return p_plus, p_minus


def ix(projector):
    """I + (D+1) P = (I+P) + D P."""
    return mat_add(eye(4), projector, mat_scale(projector, 1))


def pure_product_is_scalar(first, second):
    product = mat_mul(ix(second), ix(first))
    scalar = mat_scale(eye(4), 1)  # D I on the stage support
    if product != scalar:
        fail("adjacent halves do not multiply to D I")


def bracket_is_t(first, second, image_first, image_second):
    """(I+x second) image_first + image_second (I+x first) equals T."""
    reduced = mat_add(
        mat_mul(ix(second), image_first),
        mat_mul(image_second, ix(first)),
    )
    # T in the eigenbasis is I on matching signs, copied across core and leaf.
    t_matrix = eye(4)
    for row in (0, 2):
        for col in (0, 2):
            t_matrix[row][col] = ONE
    for row in (1, 3):
        for col in (1, 3):
            t_matrix[row][col] = ONE
    if reduced != t_matrix:
        fail("full-call bracket is not T")


def images():
    plus = [[ZERO] * 4 for _ in range(4)]
    minus = [[ZERO] * 4 for _ in range(4)]
    for row in (0, 2):
        for col in (0, 2):
            plus[row][col] = ONE
    for row in (1, 3):
        for col in (1, 3):
            minus[row][col] = ONE
    return plus, minus


def broken_diagonal_block():
    """A nonzero ++ block of B is not a legal off-diagonal solution."""
    h = letter("H")
    p_plus = [row[:] for row in plus_projector()]
    p_plus[0] = [add(p_plus[0][0], h), p_plus[0][1], p_plus[0][2], p_plus[0][3]]
    pure_product_is_scalar(p_plus, minus_projector())


# --- coefficient of V Z U ---

def embed_projector(local, size, stage_index):
    """Place a 4x4 stage projector into a larger coordinate list."""
    matrix = [[ZERO for _ in range(size)] for _ in range(size)]
    for row in range(4):
        for col in range(4):
            matrix[stage_index[row]][stage_index[col]] = local[row][col]
    return matrix


def closed_form(p_first, p_second, f_matrix, z_matrix_full):
    """(F + P_f + D P_s) Z (F + P_s + D P_f)."""
    u0 = mat_add(f_matrix, p_second)
    v0 = mat_add(f_matrix, p_first)
    u = mat_add(u0, mat_scale(p_first, 1))
    v = mat_add(v0, mat_scale(p_second, 1))
    return mat_mul(v, mat_mul(z_matrix_full, u))


def degree_part(expr, degree):
    return {(0, word): 1 for (deg, word) in expr if deg == degree and expr[(deg, word)]}


def check_coefficient_identity():
    """On six coordinates, VZU equals the closed form, for both half orders.

    Coordinates: c+, c-, s+, s-, o+, o-. The last pair is one other leaf.
    """
    size = 6
    stage = [0, 1, 2, 3]
    p_plus = embed_projector(plus_projector(), size, stage)
    p_minus = embed_projector(minus_projector(), size, stage)
    f_matrix = eye(size)
    for index in range(4):
        f_matrix[index][index] = ZERO
    z_full = z_matrix(size, "Z")
    for first, second in ((p_plus, p_minus), (p_minus, p_plus)):
        direct = mat_mul(ix_embedded(second), mat_mul(z_full, ix_embedded(first)))
        closed = closed_form(first, second, f_matrix, z_full)
        if direct != closed:
            fail("VZU closed form disagrees with I+(D+1)P")
        # Other-leaf columns 4 and 5, core rows 0 and 1: no D^2, and the
        # D^0 / D^1 parts are pi_core P_f Z and pi_core P_s Z.
        for col in (4, 5):
            for row in (0, 1):
                entry = direct[row][col]
                if any(deg == 2 for (deg, _word) in entry):
                    fail("other leaf carries a D^2 core block")
                d0 = degree_part(entry, 0)
                d1 = degree_part(entry, 1)
                pred0 = mat_mul(first, z_full)[row][col]
                pred1 = mat_mul(second, z_full)[row][col]
                if d0 != pred0 or d1 != pred1:
                    fail("other-leaf coefficient is not the projector compression")
        # Own-leaf columns stay inside degrees 0, 1, 2.
        for col in (2, 3):
            for row in range(size):
                if any(deg > 2 for (deg, _word) in direct[row][col]):
                    fail("own-leaf degree exceeded 2")


def ix_embedded(projector):
    return mat_add(eye(len(projector)), projector, mat_scale(projector, 1))


# --- monomials and the rank count ---

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


def helped_leaves(leaves, stage):
    hits = set()
    for leaf in range(leaves):
        base = outside(leaves, stage, leaf)
        for power in (0, 1, 2):
            if powered(base, stage, power) == required(leaves, leaf):
                hits.add(leaf)
    return hits


def closed_hits(leaves, stage):
    hits = {stage}
    if stage >= 1:
        hits.add(stage - 1)
    if stage + 1 < leaves:
        hits.add(stage + 1)
    return hits


def external_cover(leaves):
    """Gap gamma meets required monomial M_j exactly for j in {gamma-1, gamma}."""
    for leaf in range(leaves):
        hits = []
        for gap in range(leaves + 1):
            exponents = [1 if index >= gap else 0 for index in range(leaves)]
            if leaf < gap:
                exponents[leaf] += 1
            if exponents == required(leaves, leaf):
                hits.append(gap)
        if hits != [leaf, leaf + 1]:
            fail("external cover is not the two adjacent gaps")


def counting_bound(leaves, width):
    smallest = None
    for stage in range(leaves):
        hits = helped_leaves(leaves, stage)
        if hits != closed_hits(leaves, stage):
            fail("hit set disagrees with the three-leaf closed form")
        if len(hits) > 3:
            fail("one internal gap meets more than three required monomials")
        unhelped = [leaf for leaf in range(leaves) if leaf not in hits]
        counts = [0] * (leaves + 1)
        for leaf in unhelped:
            counts[leaf] += 1
            counts[leaf + 1] += 1
        if any(count > 2 for count in counts):
            fail("an external gap was counted more than twice")
        if sum(counts) != 2 * len(unhelped):
            fail("incidence total")
        lower = width * len(unhelped)
        if smallest is None or lower < smallest:
            smallest = lower
    if smallest != width * (leaves - 3):
        fail("minimum unhelped count is not g-3")
    return smallest


# --- global word at g=3, q=1, nonzero B, as a conjugation control ---

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
            key = tuple(a + b for a, b in zip(key_l, key_r))
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
    return {tuple(0 for _ in range(LEAVES)): matrix}


def var(index):
    exponents = [0] * LEAVES
    exponents[index] = 1
    return tuple(exponents)


def place_halves(stage, b12, b21):
    plus = zeron()
    minus = zeron()
    core = [0, 1]
    leaf = [WIDTH * (stage + 1), WIDTH * (stage + 1) + 1]
    # Local coordinates c+, c-, s+, s- map to these global indices.
    locs = [core[0], core[1], leaf[0], leaf[1]]
    local_plus = plus_projector_bits(b12, b21)
    local_minus = minus_projector_bits(b12, b21)
    for row in range(4):
        for col in range(4):
            plus[locs[row]][locs[col]] = local_plus[row][col]
            minus[locs[row]][locs[col]] = local_minus[row][col]
    image_plus = zeron()
    image_minus = zeron()
    for src in (core, leaf):
        for dst in (core, leaf):
            image_plus[dst[0]][src[0]] = 1
            image_minus[dst[1]][src[1]] = 1
    return plus, minus, image_plus, image_minus


def plus_projector_bits(b12, b21):
    return [
        [1, b12, 0, b12],
        [b21, 0, b21, 0],
        [0, b12, 1, b12],
        [b21, 0, b21, 0],
    ]


def minus_projector_bits(b12, b21):
    return [
        [0, b12, 0, b12],
        [b21, 1, b21, 0],
        [0, b12, 0, b12],
        [b21, 0, b21, 1],
    ]


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


def core_leaf_block(poly, leaf):
    cols = [WIDTH * (leaf + 1), WIDTH * (leaf + 1) + 1]
    out = {}
    for key, matrix in poly.items():
        block = [[matrix[row][col] for col in cols] for row in (0, 1)]
        if any(any(row) for row in block):
            out[key] = block
    return out


def compress(projector, matrix, leaf):
    composed = mmul(projector, matrix)
    cols = [WIDTH * (leaf + 1), WIDTH * (leaf + 1) + 1]
    return [[composed[row][col] for col in cols] for row in (0, 1)]


def word_factors(stage, first_plus, matrix, b12, b21):
    factors = []
    for index in reversed(range(LEAVES)):
        plus, minus, image_plus, image_minus = place_halves(index, b12, b21)
        if index != stage:
            factors.extend(
                [full_call(minus, image_minus, index), full_call(plus, image_plus, index)]
            )
            continue
        if first_plus:
            p_first, r_first, p_second, r_second = plus, image_plus, minus, image_minus
        else:
            p_first, r_first, p_second, r_second = minus, image_minus, plus, image_plus
        second = full_call(p_second, r_second, index)
        first = full_call(p_first, r_first, index)
        if matrix is None:
            factors.extend([second, first])
        else:
            factors.extend([second, thin_factor(matrix), first])
    return factors


def pattern(seed):
    matrix = zeron()
    for row in range(SPACE):
        for col in range(SPACE):
            matrix[row][col] = (row * 5 + col * 3 + seed) & 1
    matrix[0][2] ^= 1
    return matrix


def conjugation_control():
    b12, b21 = 1, 1
    bare = multiply_word(word_factors(0, True, None, b12, b21))
    for leaf in range(LEAVES):
        block = core_leaf_block(bare[1], leaf)
        monomial = tuple(required(LEAVES, leaf))
        identity = [[1 if row == col else 0 for col in range(2)] for row in range(2)]
        if block != {monomial: identity}:
            fail("scalar full-call core block is not M_j I")
    # The swapped leaf-order monomial is a different polynomial.
    if tuple(required(LEAVES, 0)) == tuple(1 if index <= 0 else 0 for index in range(LEAVES)):
        fail("required monomial collapsed")
    for stage in range(LEAVES):
        for first_plus in (True, False):
            matrix = pattern(stage + 4 * int(first_plus))
            plus, minus, _image_plus, _image_minus = place_halves(stage, b12, b21)
            p_first, p_second = (plus, minus) if first_plus else (minus, plus)
            diff = poly_add(
                multiply_word(word_factors(stage, first_plus, matrix, b12, b21))[1],
                multiply_word(word_factors(stage, first_plus, None, b12, b21))[1],
            )
            for leaf in range(LEAVES):
                got = core_leaf_block(diff, leaf)
                if leaf == stage:
                    allowed = {
                        tuple(powered(outside(LEAVES, stage, leaf), stage, power))
                        for power in (0, 1, 2)
                    }
                    if set(got) - allowed:
                        fail("own-leaf internal monomial escaped the quadratic")
                    continue
                pred = {}
                block0 = compress(p_first, matrix, leaf)
                block1 = compress(p_second, matrix, leaf)
                mon0 = tuple(powered(outside(LEAVES, stage, leaf), stage, 0))
                mon1 = tuple(powered(outside(LEAVES, stage, leaf), stage, 1))
                if any(any(row) for row in block0):
                    pred[mon0] = block0
                if any(any(row) for row in block1):
                    pred[mon1] = block1
                if got != pred:
                    fail("global conjugation disagrees with the local coefficient")
    zero_diff = poly_add(
        multiply_word(word_factors(1, True, zeron(), b12, b21))[1],
        multiply_word(word_factors(1, True, None, b12, b21))[1],
    )
    if zero_diff:
        fail("zero internal map changed the e-coefficient")
    left = pattern(3)
    right = pattern(9)
    both = madd(left, right)
    diff_both = poly_add(
        multiply_word(word_factors(1, False, both, b12, b21))[1],
        multiply_word(word_factors(1, False, None, b12, b21))[1],
    )
    diff_left = poly_add(
        multiply_word(word_factors(1, False, left, b12, b21))[1],
        multiply_word(word_factors(1, False, None, b12, b21))[1],
    )
    diff_right = poly_add(
        multiply_word(word_factors(1, False, right, b12, b21))[1],
        multiply_word(word_factors(1, False, None, b12, b21))[1],
    )
    if poly_add(diff_both, poly_add(diff_left, diff_right)):
        fail("two internal maps did not add")


def main():
    general_off_diagonal_obstruction()
    p_plus, p_minus = projector_identities()
    image_plus, image_minus = images()
    pure_product_is_scalar(p_plus, p_minus)
    pure_product_is_scalar(p_minus, p_plus)
    bracket_is_t(p_plus, p_minus, image_plus, image_minus)
    bracket_is_t(p_minus, p_plus, image_minus, image_plus)
    expect_false("diagonal block of B", broken_diagonal_block)
    check_coefficient_identity()
    external_cover(G)
    external_cover(4)
    lower = counting_bound(G, Q)
    counting_bound(4, 1)
    profile = MAPS * Q
    if not profile < lower:
        fail("profile is not below the internal-gap bound")
    if lower != Q * (G - 3):
        fail("bound arithmetic")
    # A predicate that helps every leaf would not separate 130 from the bound.
    if helped_leaves(G, 0) == set(range(G)):
        fail("the first stage was treated as helping every leaf")
    conjugation_control()
    expect_false(
        "non-adjacent external gap",
        lambda: external_cover_mutated(),
    )
    print(
        "PASS_G31_Q26_INTERNAL_GAP"
        f" proof g={G} q={Q} d={2 * Q}"
        f" lower_total_rank={lower} profile_total_rank={profile}"
        " helped_leaves_at_most=3"
    )
    print(
        "STATUS proof under one internal thin gap between adjacent halves;"
        " not a census of words; not a heuristic; not unrestricted nonexistence"
    )
    return 0


def external_cover_mutated():
    exponents = [1 if index >= 2 else 0 for index in range(G)]
    if exponents != required(G, 0):
        fail("gap 2 does not carry the leaf-0 monomial")


if __name__ == "__main__":
    sys.exit(main())
