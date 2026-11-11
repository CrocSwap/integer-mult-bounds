#!/usr/bin/env python3
"""Check the two-prefix leaf-column expansion in PROOF.md.

The identities are the written argument. These checks recompute the same
matrix polynomials and compare them with the literal conjugated word.
They raise SystemExit on failure, so python -O does not drop them.
One field point is not an input.
"""

from itertools import permutations


def require(ok, message):
    if not ok:
        raise SystemExit(message)


# Laurent polynomials over GF(2). A polynomial is the set of monomials
# with coefficient 1. Exponents are D0, D1, D2, D3, D4, and may be negative.
NVAR = 5
ZERO = frozenset()


def mono(var=None, exp=1):
    exponents = [0] * NVAR
    if var is not None:
        exponents[var] = exp
    return frozenset((tuple(exponents),))


ONE = mono()


def add(left, right):
    return left ^ right


def mul(left, right):
    if not left or not right:
        return ZERO
    total = {}
    for left_exp in left:
        for right_exp in right:
            combined = tuple(a + b for a, b in zip(left_exp, right_exp))
            total[combined] = total.get(combined, 0) ^ 1
    return frozenset(exp for exp, bit in total.items() if bit)


def x_of(stage):
    """D_stage + 1."""
    return add(mono(stage, 1), ONE)


def y_of(stage):
    """1 + D_stage^{-1} = (D_stage + 1) D_stage^{-1}."""
    return add(mono(stage, -1), ONE)


def uses_var(poly, var):
    return any(exp[var] for exp in poly)


def set_var_one(poly, var):
    """Substitute D_var = 1, cancelling in characteristic 2."""
    total = {}
    for exp in poly:
        reduced = list(exp)
        reduced[var] = 0
        key = tuple(reduced)
        total[key] = total.get(key, 0) ^ 1
    return frozenset(exp for exp, bit in total.items() if bit)


def show_poly(poly):
    if not poly:
        return "0"
    parts = []
    for exp in sorted(poly):
        factors = []
        for index, power in enumerate(exp):
            if power:
                factors.append("D%d" % index + ("" if power == 1 else "^%d" % power))
        parts.append("*".join(factors) if factors else "1")
    return "+".join(parts)


def zeros(n):
    return [[ZERO] * n for _ in range(n)]


def eye(n):
    return [[ONE if i == j else ZERO for j in range(n)] for i in range(n)]


def add_mat(left, right):
    return [[left[i][j] ^ right[i][j] for j in range(len(left))] for i in range(len(left))]


def scale_mat(scalar, matrix):
    return [[mul(scalar, entry) for entry in row] for row in matrix]


def mul_mat(left, right):
    width = len(right[0])
    mid = len(right)
    out = [[ZERO] * width for _ in range(len(left))]
    for i, row in enumerate(left):
        dest = out[i]
        for k, entry in enumerate(row):
            if not entry:
                continue
            source = right[k]
            for j in range(width):
                if source[j]:
                    dest[j] = dest[j] ^ mul(entry, source[j])
    return out


def mat_eq(left, right):
    return left == right


def witness(left, right):
    for i, row in enumerate(left):
        for j, entry in enumerate(row):
            if entry != right[i][j]:
                return "entry (%d,%d): got %s expected %s" % (
                    i, j, show_poly(entry), show_poly(right[i][j]))
    return "no differing entry"


def require_mat(left, right, message):
    require(mat_eq(left, right), message + "; " + witness(left, right))


def bits(pattern):
    matrix = zeros(2)
    matrix[0][0] = ONE if pattern[0] else ZERO
    matrix[0][1] = ONE if pattern[1] else ZERO
    matrix[1][0] = ONE if pattern[2] else ZERO
    matrix[1][1] = ONE if pattern[3] else ZERO
    return matrix


def pack_b(top, bottom):
    q = len(top)
    matrix = zeros(2 * q)
    for i in range(q):
        for j in range(q):
            matrix[i][q + j] = top[i][j]
            matrix[q + i][j] = bottom[i][j]
    return matrix


def projector_a(q):
    matrix = zeros(2 * q)
    for i in range(q):
        matrix[i][i] = ONE
    return matrix


def legal_relation(diag, off):
    """AB + BA = B, equivalently AB + BA + B = 0 in characteristic 2."""
    mixed = add_mat(mul_mat(diag, off), mul_mat(off, diag))
    return mat_eq(add_mat(mixed, off), zeros(len(off)))


def square_is_zero(matrix):
    return mat_eq(mul_mat(matrix, matrix), zeros(len(matrix)))


def frames():
    """Three legal pairs. One has B^2 = 0 and one has B^2 = I."""
    generic = pack_b(bits((1, 1, 0, 1)), bits((1, 0, 1, 1)))
    sparse = pack_b(bits((1, 0, 0, 0)), bits((0, 0, 1, 0)))
    exhibited = zeros(16)
    exhibited[0][8] = ONE
    exhibited[9][2] = ONE
    square = zeros(16)
    for i in range(8):
        square[i][8 + i] = ONE
        square[8 + i][i] = ONE
    return (
        ("q2-generic", projector_a(2), generic),
        ("q2-sparse", projector_a(2), sparse),
        ("q8-exhibited", projector_a(8), exhibited),
        ("q8-square", projector_a(8), square),
    )


def stage3_column(diag, off):
    """Leaf-1 column through both halves of stage 3, starting from T_1.

    The entering core block is I and the entering leaf-3 block is 0.
    Returns the core block and the leaf-3 block after the second half.
    """
    complement = add_mat(eye(len(diag)), diag)
    scalar = x_of(3)
    core = add_mat(eye(len(diag)), scale_mat(scalar, add_mat(diag, off)))
    leaf3 = scale_mat(scalar, off)
    mixed = add_mat(complement, off)
    core_out = add_mat(
        core,
        add_mat(
            mul_mat(scale_mat(scalar, mixed), core),
            mul_mat(scale_mat(scalar, off), leaf3),
        ),
    )
    leaf3_out = add_mat(
        leaf3,
        add_mat(
            mul_mat(scale_mat(scalar, off), core),
            mul_mat(scale_mat(scalar, mixed), leaf3),
        ),
    )
    return core_out, leaf3_out


def stage0_leaf(diag, off, core_in, add_swap):
    """Block into leaf 0 from a column whose leaf-0 block enters as 0.

    `core_in` is the core block of that column. The first return value is
    the block after the first half. The second is the block after the
    optional core/leaf swap and the second half.
    """
    complement = add_mat(eye(len(diag)), diag)
    scalar = x_of(0)
    leaf0 = mul_mat(scale_mat(scalar, off), core_in)
    core = mul_mat(add_mat(eye(len(diag)), scale_mat(scalar, add_mat(diag, off))), core_in)
    if add_swap:
        core = add_mat(core, eye(len(diag)))
    mixed = add_mat(complement, off)
    final = add_mat(
        leaf0,
        add_mat(
            mul_mat(scale_mat(scalar, off), core),
            mul_mat(scale_mat(scalar, mixed), leaf0),
        ),
    )
    return leaf0, final


def opposite_leaf(diag, off):
    """Block from leaf 0 into the earlier prefix leaf, recomputed in blocks.

    Entering data are the row identities proved for order stage 1 then
    stage 3: S(leaf 1, core) = D3^{-1} I and S(leaf 1, leaf 0) = 0.
    Returns the block after the first half and the block after K and the
    second half.
    """
    width = len(diag)
    complement = add_mat(eye(width), diag)
    scalar_y = y_of(0)
    inverse = mono(3, -1)
    row_core = scale_mat(inverse, eye(width))
    # First half: row_leaf1 is fixed, and Minv sends leaf 0 to y B on the core.
    after_first = mul_mat(row_core, scale_mat(scalar_y, off))
    row_core = add_mat(
        mul_mat(row_core, add_mat(eye(width), scale_mat(scalar_y, add_mat(diag, off)))),
        eye(width),
    )
    row_leaf0 = after_first
    mixed = add_mat(complement, off)
    image_core = scale_mat(scalar_y, off)
    image_leaf0 = add_mat(eye(width), scale_mat(scalar_y, mixed))
    final = add_mat(mul_mat(row_core, image_core), mul_mat(row_leaf0, image_leaf0))
    return after_first, final


def check_expansion():
    frames_seen = []
    for name, diag, off in frames():
        require(legal_relation(diag, off), name + " violates AB+BA=B")
        require(legal_relation(add_mat(eye(len(diag)), diag), off), name + " complement violates the relation")
        core, leaf3 = stage3_column(diag, off)
        require_mat(core, scale_mat(mono(3, 1), eye(len(diag))), name + " core column is not D3 I after U_3")
        require_mat(leaf3, zeros(len(diag)), name + " leaf-3 entry of the leaf-1 column survived U_3")
        for half_name, half in (("A", diag), ("A-prime", add_mat(eye(len(diag)), diag))):
            mid, final = stage0_leaf(half, off, core, True)
            target = scale_mat(x_of(0), off)
            carried = scale_mat(mul(x_of(0), mono(3, 1)), off)
            require_mat(mid, carried, name + " " + half_name + " first half is not (D0+1) D3 B")
            require(not mat_eq(mid, target), name + " " + half_name + " first half collapsed to (D0+1) B")
            require_mat(final, target, name + " " + half_name + " final block is not (D0+1) B")
            blinded = [[set_var_one(entry, 3) for entry in row] for row in mid]
            require_mat(blinded, target, name + " D3=1 did not hide the extra factor")
            without = stage0_leaf(half, off, core, False)[1]
            require_mat(without, zeros(len(diag)), name + " " + half_name + " without K did not vanish")
            require(not mat_eq(without, target), name + " without K still equalled (D0+1) B")
        for half_name, half in (("A", diag), ("A-prime", add_mat(eye(len(diag)), diag))):
            early, closed = opposite_leaf(half, off)
            require_mat(
                early,
                scale_mat(mul(y_of(0), mono(3, -1)), off),
                name + " " + half_name + " opposite block after the first half is not y D3^{-1} B",
            )
            require_mat(closed, scale_mat(y_of(0), off), name + " " + half_name + " opposite block is not y B")
        frames_seen.append((name, square_is_zero(off)))
    squares = {flag for _, flag in frames_seen}
    require(True in squares and False in squares, "the frames did not include both B^2=0 and B^2≠0")
    # The relation is necessary: I is idempotent on the diagonal slot and illegal as B.
    illegal = eye(4)
    diag = projector_a(2)
    require(not legal_relation(diag, illegal), "I unexpectedly satisfied AB+BA=B")
    core, _leaf3 = stage3_column(diag, illegal)
    _mid, final = stage0_leaf(diag, illegal, core, True)
    require(not mat_eq(final, scale_mat(x_of(0), illegal)), "illegal B still closed to (D0+1) B")
    zero = zeros(4)
    core, leaf3 = stage3_column(diag, zero)
    _mid, final = stage0_leaf(diag, zero, core, True)
    require_mat(final, zeros(4), "B=0 produced a nonzero leaf block")
    require_mat(leaf3, zeros(4), "B=0 produced a leaf-3 column entry")


def pack(diag, off):
    width = len(diag)
    projector = zeros(2 * width)
    query = zeros(2 * width)
    mixed = add_mat(diag, off)
    for i in range(width):
        for j in range(width):
            projector[i][j] = mixed[i][j]
            projector[i][width + j] = off[i][j]
            projector[width + i][j] = off[i][j]
            projector[width + i][width + j] = mixed[i][j]
            query[i][j] = query[i][width + j] = diag[i][j]
            query[width + i][j] = query[width + i][width + j] = diag[i][j]
    return projector, query


def embed(local, leaf, g, width):
    size = width * (g + 1)
    matrix = zeros(size)
    index = list(range(width)) + [width * (leaf + 1) + i for i in range(width)]
    for a, row in enumerate(index):
        for b, col in enumerate(index):
            matrix[row][col] = local[a][b]
    return matrix


def full_swap(g, width):
    size = width * (g + 1)
    matrix = zeros(size)
    for leaf in range(g):
        for i in range(width):
            matrix[i][width * (leaf + 1) + i] = ONE
            matrix[width * (leaf + 1) + i][i] = ONE
    return matrix


def apply_half(state, projector, query, leaf, stage, g, width):
    embedded_p = embed(projector, leaf, g, width)
    embedded_r = embed(query, leaf, g, width)
    size = len(state)
    forward = add_mat(eye(size), scale_mat(x_of(stage), embedded_p))
    backward = add_mat(eye(size), scale_mat(y_of(stage), embedded_p))
    return add_mat(mul_mat(forward, mul_mat(state, backward)), embedded_r)


def block(state, row_leaf, col_leaf, width):
    def span(leaf):
        if leaf < 0:
            return range(width)
        return range(width * (leaf + 1), width * (leaf + 2))

    rows = list(span(row_leaf))
    cols = list(span(col_leaf))
    return [[state[row][col] for col in cols] for row in rows]


def literal_word(g, width, diag, off, prefix, open_prime, swapped):
    """Complete `prefix` in order, open stage 0 around K, then the tail."""
    first_p, first_r = pack(diag, off)
    second_p, second_r = pack(add_mat(eye(width), diag), off)
    state = zeros(width * (g + 1))

    def halves(stage):
        ordered = ((first_p, first_r), (second_p, second_r))
        if stage in swapped:
            return (ordered[1], ordered[0])
        return ordered

    for stage in prefix:
        for projector, query in halves(stage):
            state = apply_half(state, projector, query, stage, stage, g, width)
    opening = halves(0)
    if open_prime:
        opening = (opening[1], opening[0])
    state = apply_half(state, opening[0][0], opening[0][1], 0, 0, g, width)
    midpoint = state
    state = add_mat(state, full_swap(g, width))
    state = apply_half(state, opening[1][0], opening[1][1], 0, 0, g, width)
    closed = state
    for stage in range(1, g):
        if stage not in prefix:
            for projector, query in halves(stage):
                state = apply_half(state, projector, query, stage, stage, g, width)
    return midpoint, closed, state


def check_literal_words():
    g = 5
    width = 4
    checked = 0
    for name, pattern_top, pattern_bottom in (
        ("generic", (1, 1, 0, 1), (1, 0, 1, 1)),
        ("sparse", (1, 0, 0, 0), (0, 0, 1, 0)),
    ):
        diag = projector_a(2)
        off = pack_b(bits(pattern_top), bits(pattern_bottom))
        require(legal_relation(diag, off), name + " literal frame is illegal")
        target = scale_mat(x_of(0), off)
        zero = zeros(width)
        for earlier, later in permutations(range(1, g), 2):
            carried = scale_mat(mul(x_of(0), mono(later, 1)), off)
            opposite_mid = scale_mat(mul(y_of(0), mono(later, -1)), off)
            opposite = scale_mat(y_of(0), off)
            tails = [stage for stage in range(1, g) if stage not in (earlier, later)]
            tail_prediction = scale_mat(mul(x_of(0), mono(tails[0], -1)), off)
            for open_prime in (False, True):
                for swap_earlier in (False, True):
                    for swap_later in (False, True):
                        swapped = set()
                        if swap_earlier:
                            swapped.add(earlier)
                        if swap_later:
                            swapped.add(later)
                        mid, closed, final = literal_word(
                            g, width, diag, off, (earlier, later), open_prime, swapped)
                        label = "%s prefix %d then %d prime=%s swap=%s" % (
                            name, earlier, later, open_prime, sorted(swapped))
                        require_mat(block(mid, 0, earlier, width), carried,
                                    label + " first-half block missed (D0+1) D_later B")
                        require_mat(block(mid, 0, later, width), target,
                                    label + " later leaf was scaled before stage 0")
                        require_mat(block(mid, earlier, 0, width), opposite_mid,
                                    label + " opposite first-half block changed")
                        require_mat(block(closed, 0, earlier, width), target,
                                    label + " closed block is not (D0+1) B")
                        require_mat(block(final, 0, earlier, width), target,
                                    label + " tail changed the earlier leaf block")
                        require_mat(block(final, 0, later, width), target,
                                    label + " later leaf block is not (D0+1) B")
                        require_mat(block(final, earlier, 0, width), opposite,
                                    label + " opposite block is not y B")
                        require_mat(block(final, later, 0, width), opposite,
                                    label + " later opposite block is not y B")
                        require_mat(block(final, earlier, later, width), zero,
                                    label + " block between prefix leaves is nonzero")
                        require_mat(block(final, later, earlier, width), zero,
                                    label + " reverse prefix-leaf block is nonzero")
                        require_mat(block(final, 0, tails[0], width), tail_prediction,
                                    label + " tail leaf left the section-5 formula")
                        require(not mat_eq(block(final, 0, tails[0], width), target),
                                label + " tail leaf lost its D_t^{-1}")
                        checked += 1
    require(checked == 2 * 12 * 8, "literal schedule count changed: %d" % checked)


def gf2_rank(rows):
    active = [row for row in rows if row]
    rank = 0
    while active:
        pivot = max(active)
        bit = pivot.bit_length() - 1
        rank += 1
        active = [row ^ pivot if (row >> bit) & 1 else row for row in active if row != pivot]
    return rank


def coordinate_map(g, width, coords):
    size = width * (g + 1)
    rows = [0] * size
    for coord in coords:
        for leaf in range(g):
            column = width * (leaf + 1) + coord
            rows[coord] |= 1 << column
            rows[column] |= 1 << coord
    return rows


def check_bundles():
    g = 13
    width = 16
    bundles = (
        (0, 1, 2, 3),
        (0, 1, 4, 5),
        (0, 1, 6, 7),
        (8, 9, 10, 11),
        (12, 13, 14, 15),
    )
    total = [0] * (width * (g + 1))
    rank_sum = 0
    for coords in bundles:
        rows = coordinate_map(g, width, coords)
        found = gf2_rank(rows)
        require(found == 8, "a bundle rank is %d, not 8" % found)
        rank_sum += found
        total = [left ^ right for left, right in zip(total, rows)]
    require(rank_sum == 40, "the five bundle ranks do not sum to 40")
    require(total == coordinate_map(g, width, range(width)), "the five bundles do not sum to K")
    require(gf2_rank(total) == 32, "K does not have rank 32")
    diag = projector_a(8)
    off = zeros(16)
    off[0][8] = ONE
    off[9][2] = ONE
    require(legal_relation(diag, off), "the exhibited g=13 frame is illegal")
    require(not mat_eq(mul_mat(diag, off), mul_mat(off, diag)), "the exhibited frame commutes")
    require(not mat_eq(off, zeros(16)), "the exhibited B vanished")


def check_projector_inverse():
    diag = projector_a(2)
    off = pack_b(bits((1, 1, 0, 1)), bits((1, 0, 1, 1)))
    for projector, _query in (pack(diag, off), pack(add_mat(eye(4), diag), off)):
        square = mul_mat(projector, projector)
        require_mat(square, projector, "a stage projector is not idempotent")
        forward = add_mat(eye(len(projector)), scale_mat(x_of(0), projector))
        backward = add_mat(eye(len(projector)), scale_mat(y_of(0), projector))
        require_mat(mul_mat(forward, backward), eye(len(projector)), "(I+xP)(I+yP) is not I")


def main():
    check_projector_inverse()
    check_expansion()
    check_literal_words()
    check_bundles()
    print("PASS_PAIRED_STAR_G13_TWO_PREFIX_LEAF")


if __name__ == "__main__":
    main()
