#!/usr/bin/env python3
"""Corroborate the one-gap obstruction in PROOF.md.

The identity is the written argument. These checks fail closed if the
normalized coefficient, the leaf-to-leaf block, or the five rank-8 maps
disagree with that argument. They do not search other interleavings.
"""

import random


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


def left_factor(pure, projector, index, value):
    """Left-multiply by I+(value+1) P."""
    x = value ^ 1
    out = [row[:] for row in pure]
    if not x:
        return out
    n = len(pure)
    for a in range(len(index)):
        acc = [0] * n
        for b in range(len(index)):
            entry = projector[a][b]
            if not entry:
                continue
            table = MUL[MUL[x][entry]]
            source = pure[index[b]]
            for j in range(n):
                if source[j]:
                    acc[j] ^= table[source[j]]
        dest = out[index[a]]
        for j in range(n):
            dest[j] ^= acc[j]
    return out


def ad_dense(state, projector, value):
    x = value ^ 1
    y = MUL[x][INV[value]]
    ps = dense_mm(projector, state)
    sp = dense_mm(state, projector)
    psp = dense_mm(ps, projector)
    xy = MUL[x][y]
    out = [row[:] for row in state]
    for i in range(len(state)):
        for j in range(len(state)):
            out[i][j] ^= MUL[x][ps[i][j]] ^ MUL[y][sp[i][j]] ^ MUL[xy][psp[i][j]]
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


def word(g, width, pair, maps, order, placement):
    """Stage 0 holds every thin map between its halves. Later stages are adjacent.

    order is 'A-then-A' or 'A-prime-first'. placement is 'internal' or 'after'.
    """
    first, first_query, second, second_query = pair
    calls = []

    def emit(stage, projector, query):
        calls.append(("full", submatrix(projector, support(stage, g, width)), support(stage, g, width), query, stage))

    if order == "A-then-A":
        halves = ((first, first_query), (second, second_query))
    elif order == "A-prime-first":
        halves = ((second, second_query), (first, first_query))
    else:
        raise SystemExit("unknown half order")
    emit(0, embed(halves[0][0], 0, g, width), embed(halves[0][1], 0, g, width))
    if placement == "internal":
        calls.extend(("thin", matrix) for matrix in maps)
    emit(0, embed(halves[1][0], 0, g, width), embed(halves[1][1], 0, g, width))
    if placement == "after":
        calls.extend(("thin", matrix) for matrix in maps)
    for stage in range(1, g):
        emit(stage, embed(first, stage, g, width), embed(first_query, stage, g, width))
        emit(stage, embed(second, stage, g, width), embed(second_query, stage, g, width))
    return calls


def run(calls, values):
    size = len(next(call[3] for call in calls if call[0] == "full"))
    state = zeros(size)
    pure = eye(size)
    for call in calls:
        if call[0] == "full":
            _, projector, index, query, stage = call
            state = add(ad_fast(state, projector, index, values[stage]), query)
            pure = left_factor(pure, projector, index, values[stage])
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


def predicted_into_leaf0(off, values, leaf):
    """Leaf 0 <- leaf t equals (D0+1) * D_t^{-1} * B."""
    scalar = MUL[values[0] ^ 1][INV[values[leaf]]]
    return scale(off, scalar)


def predicted_out_of_leaf0(off, values, leaf):
    """Leaf t <- leaf 0 equals D_t * (D0+1) * D0^{-1} * B."""
    y = MUL[values[0] ^ 1][INV[values[0]]]
    scalar = MUL[values[leaf]][y]
    return scale(off, scalar)


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
    for bundle in BUNDLES:
        require(len(bundle) == 4 and len(set(bundle)) == 4, "a bundle is not four distinct coordinates")
        for coord in bundle:
            cover[coord] += 1
        matrix = coordinate_map(g, width, bundle)
        require(rank(matrix) == q, "a coordinate bundle does not have rank q")
        maps.append(matrix)
    require(all(count % 2 == 1 for count in cover), "coordinate coverage is not odd")
    require(len(maps) == 5, "the word does not have five thin maps")
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
            state = add(ad_dense(state, projector, value), query)
        else:
            deriv = add(deriv, dense_mm(rest[0], pure))
            state = add(state, rest[0])
    return pure, dense_mm(deriv, invert(pure)), state


def check_fast_matches_dense():
    proj, off, pair = check_frame(1, True)
    width = 2
    g = 2
    values = (2, 3)
    matrix = full_swap(g, width)
    calls = word(g, width, pair, [matrix], "A-then-A", "internal")
    pure, state = run(calls, values)
    full_calls = []
    first, first_query, second, second_query = pair
    full_calls.append(("full", embed(first, 0, g, width), embed(first_query, 0, g, width), 0))
    full_calls.append(("thin", matrix))
    full_calls.append(("full", embed(second, 0, g, width), embed(second_query, 0, g, width), 0))
    for stage in range(1, g):
        full_calls.append(("full", embed(first, stage, g, width), embed(first_query, stage, g, width), stage))
        full_calls.append(("full", embed(second, stage, g, width), embed(second_query, stage, g, width), stage))
    pure_d, coeff, state_d = dense_endpoint(full_calls, values)
    require(pure == pure_d and state == state_d and state == coeff,
            "fast normalized coefficient disagrees with the dual-number word")
    require(pure == target(values, g, width), "the small pure product missed the target")
    rng = random.Random(13)
    size = width * (g + 1)
    sample = [[rng.randrange(16) for _ in range(size)] for _ in range(size)]
    index = support(0, g, width)
    require(
        ad_fast(sample, submatrix(embed(first, 0, g, width), index), index, 5)
        == ad_dense(sample, embed(first, 0, g, width), 5),
        "fast conjugation disagrees with the dense formula",
    )
    # A completed pair scales regions. One half does not.
    probe = zeros(size)
    probe[width][2 * width] = 1
    scaled = ad_fast(
        ad_fast(probe, submatrix(embed(first, 1, g, width), support(1, g, width)), support(1, g, width), values[1]),
        submatrix(embed(second, 1, g, width), support(1, g, width)),
        support(1, g, width),
        values[1],
    )
    expect = zeros(size)
    expect[width][2 * width] = INV[values[1]]
    require(scaled == expect, "a completed pair did not scale leaf 0 <- leaf 1 by D_1^{-1}")
    once = ad_fast(probe, submatrix(embed(second, 1, g, width), support(1, g, width)), support(1, g, width), values[1])
    require(once != expect and once != probe, "one half acted as a scalar stage factor")


def check_positive_internal_word():
    """One leaf: the swap between the halves meets the endpoint. No second leaf exists."""
    proj, off, pair = check_frame(1, True)
    width = 2
    matrix = full_swap(1, width)
    for values in ((2,), (5,), (1,)):
        pure, state = run(word(1, width, pair, [matrix], "A-then-A", "internal"), values)
        require(pure == target(values, 1, width) and state == eye(width * 2),
                "the one-leaf internal swap missed the endpoint")


def check_profile():
    g, q = 13, 8
    width = 2 * q
    _, off, pair = check_frame(q, True)
    maps = check_maps(g, q)
    points = (
        tuple(range(2, 15)),
        (6, 10, 3, 5, 7, 9, 11, 13, 14, 2, 4, 8, 12),
    )
    require(all(len(point) == g and all(point) and point[0] != 1 for point in points),
            "a test point is not an invertible specialization with D0 != 1")
    ones = (1,) * g
    for order in ("A-then-A", "A-prime-first"):
        calls = word(g, width, pair, maps, order, "internal")
        pure, state = run(calls, ones)
        require(pure == target(ones, g, width) and state == eye(width * (g + 1)),
                "the maps forced by every D_j = 1 missed that specialization")
        for values in points:
            pure, state = run(calls, values)
            require(pure == target(values, g, width), "thin maps changed the pure product")
            require(state != eye(width * (g + 1)), "an internal five-map word met the endpoint")
            for leaf in (1, g - 1):
                got_in = block(state, width, width * (leaf + 1), width)
                got_out = block(state, width * (leaf + 1), width, width)
                pred_in = predicted_into_leaf0(off, values, leaf)
                pred_out = predicted_out_of_leaf0(off, values, leaf)
                require(got_in == pred_in and got_out == pred_out,
                        "leaf-to-leaf block disagrees with (D0+1) B transport")
                require(nonzero(got_in) and nonzero(got_out),
                        "the obstructing block vanished at a point with D0 != 1")
    # The same maps after both halves do not produce this block.
    pure, state = run(word(g, width, pair, maps, "A-then-A", "after"), points[0])
    require(pure == target(points[0], g, width), "the external-gap control changed the pure product")
    external = block(state, width, width * 2, width)
    require(external == zeros(width), "a map after both halves still produced the internal block")
    # B = 0 makes this particular block zero. That case is the commuting theorem.
    _, zero_off, commuting = check_frame(q, False)
    pure, state = run(word(g, width, commuting, maps, "A-then-A", "internal"), points[0])
    require(block(state, width, width * 2, width) == zeros(width),
            "B = 0 still produced a leaf-to-leaf block")
    require(predicted_into_leaf0(zero_off, points[0], 1) == zeros(width),
            "the B = 0 prediction is not zero")


def main():
    check_fast_matches_dense()
    check_positive_internal_word()
    check_profile()
    print("PASS_PAIRED_STAR_G13_Q8_INTERNAL_GAP")


if __name__ == "__main__":
    main()
