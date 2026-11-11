#!/usr/bin/env python3
"""Corroborate the stage-not-first block identity in PROOF.md.

The identities are the written argument. These checks fail closed if the
normalized coefficient or the leaf-to-leaf blocks disagree with that
argument. They do not enumerate opening orders.
"""


def require(ok, message):
    if not ok:
        raise SystemExit(message)


MUL = [[0] * 16 for _ in range(16)]
INV = [0] * 16


def _mul_raw(a, b):
    product = 0
    for _ in range(4):
        if b & 1:
            product ^= a
        b >>= 1
        high = a & 8
        a = (a << 1) & 15
        if high:
            a ^= 3
    return product


for left in range(16):
    for right in range(16):
        MUL[left][right] = _mul_raw(left, right)
for left in range(1, 16):
    for right in range(1, 16):
        if MUL[left][right] == 1:
            INV[left] = right

# Four-coordinate bundles. Coordinates 0 and 1 lie in three bundles and
# every other coordinate lies in one, so the sum is the full core/leaf swap.
BUNDLES = (
    (0, 1, 2, 3),
    (0, 1, 4, 5),
    (0, 1, 6, 7),
    (8, 9, 10, 11),
    (12, 13, 14, 15),
)


def zeros(n):
    return [[0] * n for _ in range(n)]


def eye(n):
    matrix = zeros(n)
    for i in range(n):
        matrix[i][i] = 1
    return matrix


def add(left, right):
    return [[left[i][j] ^ right[i][j] for j in range(len(left))] for i in range(len(left))]


def scale(matrix, scalar):
    row = MUL[scalar]
    return [[row[value] for value in line] for line in matrix]


def dense_mm(left, right):
    size = len(left)
    out = zeros(size)
    for i in range(size):
        dest = out[i]
        for k in range(size):
            if not left[i][k]:
                continue
            table = MUL[left[i][k]]
            source = right[k]
            for j in range(size):
                if source[j]:
                    dest[j] ^= table[source[j]]
    return out


def invert(matrix):
    size = len(matrix)
    augmented = [matrix[i][:] + [1 if i == j else 0 for j in range(size)] for i in range(size)]
    for col in range(size):
        pivot = next((row for row in range(col, size) if augmented[row][col]), None)
        require(pivot is not None, "singular matrix in the small cross-check")
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        inv_pivot = INV[augmented[col][col]]
        augmented[col] = [MUL[inv_pivot][value] for value in augmented[col]]
        for row in range(size):
            if row != col and augmented[row][col]:
                factor = augmented[row][col]
                augmented[row] = [
                    augmented[row][j] ^ MUL[factor][augmented[col][j]] for j in range(2 * size)
                ]
    return [row[size:] for row in augmented]


def rank(matrix):
    rows = [line[:] for line in matrix]
    height = len(rows)
    width = len(rows[0])
    found = 0
    row = 0
    col = 0
    while row < height and col < width:
        pivot = next((i for i in range(row, height) if rows[i][col]), None)
        if pivot is None:
            col += 1
            continue
        rows[row], rows[pivot] = rows[pivot], rows[row]
        inv_pivot = INV[rows[row][col]]
        rows[row] = [MUL[inv_pivot][value] for value in rows[row]]
        for other in range(height):
            if other != row and rows[other][col]:
                factor = rows[other][col]
                rows[other] = [
                    rows[other][j] ^ MUL[factor][rows[row][j]] for j in range(width)
                ]
        found += 1
        row += 1
        col += 1
    return found


def block(matrix, row, col, size):
    return [line[col:col + size] for line in matrix[row:row + size]]


def local_pair(proj_a, off):
    """Return (P, R, P', R') for A' = I+A and the same off-diagonal block."""
    width = len(proj_a)
    complement = [line[:] for line in proj_a]
    for i in range(width):
        complement[i][i] ^= 1

    def pack(diagonal, corner):
        projector = zeros(2 * width)
        query = zeros(2 * width)
        mixed = add(diagonal, corner)
        for i in range(width):
            for j in range(width):
                projector[i][j] = mixed[i][j]
                projector[i][width + j] = corner[i][j]
                projector[width + i][j] = corner[i][j]
                projector[width + i][width + j] = mixed[i][j]
                query[i][j] = query[i][width + j] = diagonal[i][j]
                query[width + i][j] = query[width + i][width + j] = diagonal[i][j]
        return projector, query

    first, first_query = pack(proj_a, off)
    second, second_query = pack(complement, off)
    return first, first_query, second, second_query


def support(leaf, g, width):
    return list(range(width)) + [width * (leaf + 1) + i for i in range(width)]


def embed(local, leaf, g, width):
    size = width * (g + 1)
    matrix = zeros(size)
    index = support(leaf, g, width)
    for a, row in enumerate(index):
        for b, col in enumerate(index):
            matrix[row][col] = local[a][b]
    return matrix


def frame(q, use_off_diagonal):
    """A = diag(I_q, 0), and B = [[0, C], [D, 0]] with one nonzero corner."""
    width = 2 * q
    proj = zeros(width)
    off = zeros(width)
    for i in range(q):
        proj[i][i] = 1
    if use_off_diagonal:
        off[0][q] = 1
        if q > 2:
            off[q + 1][2] = 1
    return proj, off


def submatrix(full, index):
    return [[full[index[i]][index[j]] for j in range(len(index))] for i in range(len(index))]


def ad_fast(state, projector, index, value):
    """Conjugate by I+(value+1) P. P is the projector restricted to index."""
    m = len(index)
    n = len(state)
    x = value ^ 1
    y = MUL[x][INV[value]]
    xy = MUL[x][y]
    out = [row[:] for row in state]
    if not x and not y:
        return out
    if x or xy:
        ps = [[0] * n for _ in range(m)]
        for a in range(m):
            dest = ps[a]
            for b in range(m):
                entry = projector[a][b]
                if not entry:
                    continue
                table = MUL[entry]
                source = state[index[b]]
                for j in range(n):
                    if source[j]:
                        dest[j] ^= table[source[j]]
        if x:
            table = MUL[x]
            for a in range(m):
                dest = out[index[a]]
                source = ps[a]
                for j in range(n):
                    if source[j]:
                        dest[j] ^= table[source[j]]
        if xy:
            for a in range(m):
                dest = out[index[a]]
                source = ps[a]
                for b in range(m):
                    entry = source[index[b]]
                    if not entry:
                        continue
                    table = MUL[MUL[xy][entry]]
                    row = projector[b]
                    for c in range(m):
                        if row[c]:
                            dest[index[c]] ^= table[row[c]]
    if y:
        for c in range(m):
            for i in range(n):
                acc = 0
                source = state[i]
                for b in range(m):
                    entry = projector[b][c]
                    if entry and source[index[b]]:
                        acc ^= MUL[entry][source[index[b]]]
                if acc:
                    out[i][index[c]] ^= MUL[y][acc]
    return out


def coordinate_map(g, width, coords):
    size = width * (g + 1)
    matrix = zeros(size)
    for coord in coords:
        for leaf in range(g):
            column = width * (leaf + 1) + coord
            matrix[coord][column] ^= 1
            matrix[column][coord] ^= 1
    return matrix


def full_swap(g, width):
    return coordinate_map(g, width, range(width))


def build_word(g, width, pair, maps, open_order, prefix, swap_completed=()):
    """Complete prefix stages, open stage 0 around the thin maps, then the tail.

    prefix is a tuple of stages other than 0. swap_completed exchanges the
    halves of those completed stages. The empty prefix is the stage-0-first
    word, used only as a separation control.
    """
    first, first_query, second, second_query = pair
    if open_order == "A-then-A":
        open_halves = ((first, first_query), (second, second_query))
    elif open_order == "A-prime-first":
        open_halves = ((second, second_query), (first, first_query))
    else:
        raise SystemExit("unknown half order")
    prefix = tuple(prefix)
    require(0 not in prefix and len(prefix) == len(set(prefix)), "the prefix repeats stage 0 or itself")
    require(all(1 <= stage < g for stage in prefix), "a prefix stage is outside 1..g-1")
    calls = []

    def emit(stage, local_projector, local_query):
        embedded = embed(local_projector, stage, g, width)
        index = support(stage, g, width)
        calls.append((
            "full",
            submatrix(embedded, index),
            index,
            embed(local_query, stage, g, width),
            stage,
        ))

    def adjacent(stage):
        halves = ((first, first_query), (second, second_query))
        if stage in swap_completed:
            halves = (halves[1], halves[0])
        emit(stage, halves[0][0], halves[0][1])
        emit(stage, halves[1][0], halves[1][1])

    for stage in prefix:
        adjacent(stage)
    emit(0, open_halves[0][0], open_halves[0][1])
    calls.extend(("thin", matrix) for matrix in maps)
    emit(0, open_halves[1][0], open_halves[1][1])
    for stage in range(1, g):
        if stage not in prefix:
            adjacent(stage)
    return calls


def run(calls, values):
    size = len(next(call[3] for call in calls if call[0] == "full"))
    state = zeros(size)
    pure = eye(size)
    for call in calls:
        if call[0] == "full":
            _, projector, index, query, stage = call
            state = add(ad_fast(state, projector, index, values[stage]), query)
            value = values[stage] ^ 1
            if value:
                pure_rows = pure
                pure = [row[:] for row in pure_rows]
                for a in range(len(index)):
                    acc = [0] * size
                    for b in range(len(index)):
                        entry = projector[a][b]
                        if not entry:
                            continue
                        table = MUL[MUL[value][entry]]
                        source = pure_rows[index[b]]
                        for j in range(size):
                            if source[j]:
                                acc[j] ^= table[source[j]]
                    dest = pure[index[a]]
                    for j in range(size):
                        dest[j] ^= acc[j]
        else:
            state = add(state, call[1])
    return pure, state


def target(values, g, width):
    size = width * (g + 1)
    matrix = zeros(size)
    product = 1
    for value in values:
        product = MUL[product][value]
    for i in range(width):
        matrix[i][i] = product
        for leaf in range(g):
            matrix[width * (leaf + 1) + i][width * (leaf + 1) + i] = values[leaf]
    return matrix


def tail_scalar(values, leaf):
    """(D0+1) * D_leaf^{-1}, the section 5 factor into leaf 0."""
    return MUL[values[0] ^ 1][INV[values[leaf]]]


def predicted_tail(off, values, leaf):
    return scale(off, tail_scalar(values, leaf))


def predicted_prefix_leaf(off, values):
    """(D0+1) B, the section 6 block from the single prefix leaf."""
    return scale(off, values[0] ^ 1)


def predicted_out_of_tail(off, values, leaf):
    y = MUL[values[0] ^ 1][INV[values[0]]]
    return scale(off, MUL[values[leaf]][y])


def predicted_out_of_prefix(off, values):
    y = MUL[values[0] ^ 1][INV[values[0]]]
    return scale(off, y)


def nonzero(matrix):
    return any(any(row) for row in matrix)


def check_frame(q, use_off_diagonal):
    proj, off = frame(q, use_off_diagonal)
    width = 2 * q
    require(dense_mm(proj, proj) == proj, "A is not idempotent")
    require(add(dense_mm(proj, off), dense_mm(off, proj)) == off, "AB+BA is not B")
    first, _, second, _ = local_pair(proj, off)
    require(dense_mm(first, first) == first and dense_mm(second, second) == second, "half is not a projector")
    require(add(first, second) == eye(2 * width), "halves do not resolve the stage support")
    require(dense_mm(first, second) == zeros(2 * width), "halves do not annihilate")
    require(dense_mm(second, first) == zeros(2 * width), "the opposite half product is not zero")
    if use_off_diagonal:
        require(nonzero(off), "the noncommuting example has B = 0")
        left = embed(first, 0, 2, width)
        right = embed(first, 1, 2, width)
        require(dense_mm(left, right) != dense_mm(right, left), "stage projectors commute")
    else:
        require(not nonzero(off), "the commuting control has nonzero B")
    return proj, off, local_pair(proj, off)


def check_maps(g, q):
    width = 2 * q
    cover = [0] * width
    maps = []
    rank_sum = 0
    for bundle in BUNDLES:
        require(len(bundle) == 4 and len(set(bundle)) == 4, "a bundle is not four distinct coordinates")
        for coord in bundle:
            cover[coord] += 1
        matrix = coordinate_map(g, width, bundle)
        bundle_rank = rank(matrix)
        require(bundle_rank == q, "a coordinate bundle does not have rank q")
        rank_sum += bundle_rank
        maps.append(matrix)
    require(all(count % 2 == 1 for count in cover), "coordinate coverage is not odd")
    require(len(maps) == 5 and rank_sum == 5 * q, "the word does not have five rank-q maps")
    total = zeros(width * (g + 1))
    for matrix in maps:
        total = add(total, matrix)
    require(total == full_swap(g, width), "the five maps do not sum to the D=1 swap")
    require(rank(total) == 2 * width, "the forced swap does not have rank 2d")
    return maps


def dense_endpoint(calls_full, values):
    """Dual-number word on already embedded full matrices. Small controls only."""
    size = len(calls_full[0][1])
    pure, deriv = eye(size), zeros(size)
    state = zeros(size)
    for kind, *rest in calls_full:
        if kind == "full":
            projector, query, stage = rest
            value = values[stage]
            x = value ^ 1
            pp = dense_mm(projector, pure)
            pd = dense_mm(projector, deriv)
            rp = dense_mm(query, pure)
            pure = [[pure[i][j] ^ MUL[x][pp[i][j]] for j in range(size)] for i in range(size)]
            deriv = [
                [deriv[i][j] ^ MUL[x][pd[i][j]] ^ MUL[value][rp[i][j]] for j in range(size)]
                for i in range(size)
            ]
            embedded_index = support(stage, len(values), size // (len(values) + 1))
            # The fast updater is compared on the normalized state, not re-derived here.
            state = add(ad_fast(state, submatrix(projector, embedded_index), embedded_index, value), query)
        else:
            deriv = add(deriv, dense_mm(rest[0], pure))
            state = add(state, rest[0])
    return pure, dense_mm(deriv, invert(pure)), state


def check_fast_matches_dense():
    proj, off, pair = check_frame(1, True)
    width = 2
    g = 3
    values = (2, 3, 4)
    matrix = full_swap(g, width)
    require(matrix == coordinate_map(g, width, range(width)), "the small swap is not K")
    calls = build_word(g, width, pair, [matrix], "A-then-A", (1,))
    pure, state = run(calls, values)
    first, first_query, second, second_query = pair
    full_calls = []

    def emit(stage, local_projector, local_query):
        full_calls.append(("full", embed(local_projector, stage, g, width), embed(local_query, stage, g, width), stage))

    emit(1, first, first_query)
    emit(1, second, second_query)
    emit(0, first, first_query)
    full_calls.append(("thin", matrix))
    emit(0, second, second_query)
    emit(2, first, first_query)
    emit(2, second, second_query)
    pure_d, coeff, state_d = dense_endpoint(full_calls, values)
    require(pure == pure_d and state == coeff and state == state_d,
            "fast normalized coefficient disagrees with the dual-number word")
    require(pure == target(values, g, width), "the small pure product missed the target")
    got = block(state, width, width * 3, width)
    require(got == predicted_tail(off, values, 2) and nonzero(got),
            "the small tail leaf missed (D0+1) D2^{-1} B")


def check_profile():
    g, q = 13, 8
    width = 2 * q
    _, off, pair = check_frame(q, True)
    maps = check_maps(g, q)
    points = (
        tuple(range(2, 15)),
        (6, 10, 3, 5, 7, 9, 11, 13, 14, 2, 4, 8, 12),
    )
    require(tail_scalar(points[0], 2) == 4, "the first tail scalar is not 4")
    require(tail_scalar(points[1], 2) == 12, "the second tail scalar is not 12")
    require(all(
        len(point) == g and all(point) and point[0] != 1 and point[1] != 1 and point[2] != 1
        for point in points
    ), "a test point is not invertible with D0, D1, and D2 all different from 1")
    ones = (1,) * g
    prefix = (1,)
    for order in ("A-then-A", "A-prime-first"):
        calls = build_word(g, width, pair, maps, order, prefix)
        pure, state = run(calls, ones)
        require(pure == target(ones, g, width) and state == eye(width * (g + 1)),
                "the maps forced by every D_j = 1 missed that specialization")
        for values in points:
            pure, state = run(calls, values)
            require(pure == target(values, g, width), "thin maps changed the pure product")
            require(state != eye(width * (g + 1)), "a stage-1 prefix word met the endpoint")
            got_tail = block(state, width, width * 3, width)
            got_prefix = block(state, width, width * 2, width)
            require(got_tail == predicted_tail(off, values, 2),
                    "leaf 0 <- leaf 2 disagrees with (D0+1) D2^{-1} B")
            require(block(state, width * 3, width, width) == predicted_out_of_tail(off, values, 2),
                    "leaf 2 <- leaf 0 disagrees with the tail transport")
            require(got_prefix == predicted_prefix_leaf(off, values),
                    "leaf 0 <- leaf 1 disagrees with (D0+1) B")
            require(block(state, width * 2, width, width) == predicted_out_of_prefix(off, values),
                    "leaf 1 <- leaf 0 disagrees with (D0+1) D0^{-1} B")
            require(nonzero(got_tail) and nonzero(got_prefix),
                    "an obstructing block vanished at D0 != 1")
            require(got_prefix != predicted_tail(off, values, 1),
                    "the prefix leaf still carried the stage-0-first factor D1^{-1}")
            alt = (values[0], 1) + values[2:]
            pure_alt, state_alt = run(calls, alt)
            require(state_alt == state, "the normalized coefficient depends on D1")
            require(pure_alt != pure and pure_alt == target(alt, g, width),
                    "replacing D1 by 1 did not change the pure product")
    swapped = build_word(g, width, pair, maps, "A-then-A", prefix, swap_completed=(1,))
    _, swapped_state = run(swapped, points[0])
    _, direct_state = run(build_word(g, width, pair, maps, "A-then-A", prefix), points[0])
    require(swapped_state == direct_state, "exchanging the halves of stage 1 changed S")

    # The stage-0-first word shares leaf 2 and not leaf 1.
    _, first_stage = run(build_word(g, width, pair, maps, "A-then-A", ()), points[0])
    require(block(first_stage, width, width * 3, width) == block(direct_state, width, width * 3, width),
            "moving stage 1 changed the leaf-2 block")
    require(block(first_stage, width, width * 2, width) != block(direct_state, width, width * 2, width),
            "moving stage 1 left the leaf-1 block on the old formula")
    require(block(first_stage, width, width * 2, width) == predicted_tail(off, points[0], 1),
            "the separation control did not reproduce the stage-0-first leaf-1 block")

    # One two-stage prefix, both orders. Leaf 2 is still a tail leaf.
    for two_prefix in ((1, 3), (3, 1)):
        pure_two, two_state = run(build_word(g, width, pair, maps, "A-then-A", two_prefix), points[0])
        require(pure_two == target(points[0], g, width), "a two-stage prefix changed the pure product")
        require(two_state != eye(width * (g + 1)), "a two-stage prefix met the endpoint")
        require(block(two_state, width, width * 3, width) == predicted_tail(off, points[0], 2),
                "a two-stage prefix changed the tail leaf block")

    _, zero_off, commuting = check_frame(q, False)
    _, quiet = run(build_word(g, width, commuting, maps, "A-then-A", prefix), points[0])
    require(block(quiet, width, width * 3, width) == zeros(width),
            "B = 0 still produced a leaf-to-leaf block")
    require(predicted_tail(zero_off, points[0], 2) == zeros(width),
            "the B = 0 prediction is not zero")


def main():
    check_fast_matches_dense()
    check_profile()
    print("PASS_PAIRED_STAR_G13_STAGE_NOT_FIRST")


if __name__ == "__main__":
    main()
