#!/usr/bin/env python3
"""Corroborate the after-stage-0 block identities in PROOF.md.

The identities are the written argument. These checks fail closed if the
normalized leaf block, the column-space obstruction, the five named bundles,
or the coordinate witness disagree with that argument. They do not search
other supports.
"""

MUL = [[0] * 16 for _ in range(16)]
INV = [0] * 16


def require(ok, message):
    if not ok:
        raise SystemExit(message)


def _mul_raw(left, right):
    product = 0
    for _ in range(4):
        if right & 1:
            product ^= left
        right >>= 1
        high = left & 8
        left = (left << 1) & 15
        if high:
            left ^= 3
    return product


for _left in range(16):
    for _right in range(16):
        MUL[_left][_right] = _mul_raw(_left, _right)
for _left in range(1, 16):
    for _right in range(1, 16):
        if MUL[_left][_right] == 1:
            INV[_left] = _right

# The five rank-8 bundles of the g=13, q=8 word. Coordinates 0 and 1 lie in
# three bundles and every other coordinate lies in one.
BUNDLES = (
    (0, 1, 2, 3),
    (0, 1, 4, 5),
    (0, 1, 6, 7),
    (8, 9, 10, 11),
    (12, 13, 14, 15),
)
WITNESS = (0, 2, 8, 9)
POINTS = (
    tuple(range(2, 15)),
    (6, 10, 3, 5, 7, 9, 11, 13, 14, 2, 4, 8, 12),
)


def zeros(size):
    return [[0] * size for _ in range(size)]


def eye(size):
    matrix = zeros(size)
    for i in range(size):
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


def nonzero(matrix):
    return any(any(row) for row in matrix)


def frame(q, use_off_diagonal):
    """A = diag(I_q, 0), and B = E_{0,q} + E_{q+1,2} when the off-diagonal is on."""
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


def local_pair(proj_a, off):
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


def support(leaf, width):
    return list(range(width)) + [width * (leaf + 1) + i for i in range(width)]


def embed(local, leaf, g, width):
    size = width * (g + 1)
    matrix = zeros(size)
    index = support(leaf, width)
    for a, row in enumerate(index):
        for b, col in enumerate(index):
            matrix[row][col] = local[a][b]
    return matrix


def submatrix(full, index):
    return [[full[index[i]][index[j]] for j in range(len(index))] for i in range(len(index))]


def ad_fast(state, projector, index, value):
    """Conjugate by I+(value+1) P on the coordinates in index."""
    length = len(index)
    size = len(state)
    ex = value ^ 1
    why = MUL[ex][INV[value]]
    ex_why = MUL[ex][why]
    out = [row[:] for row in state]
    if ex or ex_why:
        ps = [[0] * size for _ in range(length)]
        for a in range(length):
            dest = ps[a]
            for b in range(length):
                entry = projector[a][b]
                if not entry:
                    continue
                table = MUL[entry]
                source = state[index[b]]
                for j in range(size):
                    if source[j]:
                        dest[j] ^= table[source[j]]
        if ex:
            table = MUL[ex]
            for a in range(length):
                dest = out[index[a]]
                source = ps[a]
                for j in range(size):
                    if source[j]:
                        dest[j] ^= table[source[j]]
        if ex_why:
            for a in range(length):
                dest = out[index[a]]
                source = ps[a]
                for b in range(length):
                    entry = source[index[b]]
                    if not entry:
                        continue
                    table = MUL[MUL[ex_why][entry]]
                    row = projector[b]
                    for c in range(length):
                        if row[c]:
                            dest[index[c]] ^= table[row[c]]
    if why:
        for c in range(length):
            for i in range(size):
                acc = 0
                source = state[i]
                for b in range(length):
                    entry = projector[b][c]
                    if entry and source[index[b]]:
                        acc ^= MUL[entry][source[index[b]]]
                if acc:
                    out[i][index[c]] ^= MUL[why][acc]
    return out


def left_factor(pure, projector, index, value):
    ex = value ^ 1
    out = [row[:] for row in pure]
    if not ex:
        return out
    size = len(pure)
    for a in range(len(index)):
        acc = [0] * size
        for b in range(len(index)):
            entry = projector[a][b]
            if not entry:
                continue
            table = MUL[MUL[ex][entry]]
            source = pure[index[b]]
            for j in range(size):
                if source[j]:
                    acc[j] ^= table[source[j]]
        dest = out[index[a]]
        for j in range(size):
            dest[j] ^= acc[j]
    return out


def conj_dense(state, projector, value):
    ex = value ^ 1
    why = MUL[ex][INV[value]]
    ex_why = MUL[ex][why]
    ps = dense_mm(projector, state)
    sp = dense_mm(state, projector)
    psp = dense_mm(ps, projector)
    out = [row[:] for row in state]
    size = len(state)
    for i in range(size):
        for j in range(size):
            out[i][j] ^= MUL[ex][ps[i][j]] ^ MUL[why][sp[i][j]] ^ MUL[ex_why][psp[i][j]]
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


def leaf_block(g, width, leaf_out, leaf_in, small):
    """Rows of leaf_out, columns of leaf_in."""
    size = width * (g + 1)
    matrix = zeros(size)
    row0 = width * (leaf_out + 1)
    col0 = width * (leaf_in + 1)
    for i in range(width):
        for j in range(width):
            matrix[row0 + i][col0 + j] = small[i][j]
    return matrix


def zero_columns(matrix, columns):
    out = [row[:] for row in matrix]
    for col in columns:
        for row in out:
            row[col] = 0
    return out


def zero_rows(matrix, rows):
    out = [row[:] for row in matrix]
    for row in rows:
        out[row] = [0] * len(matrix)
    return out


def functional_on_columns(matrix, coords):
    """Sum the selected coordinates of each column. Coefficients are 1."""
    values = []
    width = len(matrix)
    for col in range(width):
        acc = 0
        for row in coords:
            acc ^= matrix[row][col]
        values.append(acc)
    return values


def split_word(g, width, pair, internal, after, order):
    """Stage 0 holds `internal` between its halves and `after` once both are done."""
    first, first_query, second, second_query = pair
    if order == "A-then-A":
        halves = ((first, first_query), (second, second_query))
    elif order == "A-prime-first":
        halves = ((second, second_query), (first, first_query))
    else:
        raise SystemExit("unknown half order")
    calls = []

    def emit(stage, projector, query):
        calls.append((
            "full",
            submatrix(projector, support(stage, width)),
            support(stage, width),
            query,
            stage,
            projector,
        ))

    emit(0, embed(halves[0][0], 0, g, width), embed(halves[0][1], 0, g, width))
    for matrix in internal:
        calls.append(("thin", matrix))
    emit(0, embed(halves[1][0], 0, g, width), embed(halves[1][1], 0, g, width))
    for matrix in after:
        calls.append(("thin", matrix))
    for stage in range(1, g):
        emit(stage, embed(first, stage, g, width), embed(first_query, stage, g, width))
        emit(stage, embed(second, stage, g, width), embed(second_query, stage, g, width))
    return calls


def run(calls, values, dense=False):
    size = len(calls[0][5] if calls[0][0] == "full" else calls[2][5])
    state = zeros(size)
    pure = eye(size)
    for call in calls:
        if call[0] == "full":
            _, projector, index, query, stage, full = call
            value = values[stage]
            if dense:
                state = add(conj_dense(state, full, value), query)
                pure = left_factor(pure, projector, index, value)
            else:
                state = add(ad_fast(state, projector, index, value), query)
                pure = left_factor(pure, projector, index, value)
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


def into_leaf0(off, values, leaf, transported):
    """D_leaf^{-1} (D_0+1) times the transported block."""
    scalar = MUL[values[0] ^ 1][INV[values[leaf]]]
    return scale(transported, scalar)


def out_of_leaf0(off, values, leaf, transported):
    """D_leaf (D_0+1) D_0^{-1} times the transported block."""
    scalar = MUL[values[leaf]][MUL[values[0] ^ 1][INV[values[0]]]]
    return scale(transported, scalar)


def second_diagonal(order, proj, complement):
    """Diagonal factor of the half that stands after the internal gap."""
    if order == "A-then-A":
        return complement
    if order == "A-prime-first":
        return proj
    raise SystemExit("unknown half order")


def check_pair(q):
    proj, off = frame(q, True)
    width = 2 * q
    complement = [row[:] for row in proj]
    for i in range(width):
        complement[i][i] ^= 1
    require(dense_mm(proj, proj) == proj, "A is not idempotent")
    require(add(dense_mm(proj, off), dense_mm(off, proj)) == off, "AB+BA is not B")
    require(
        [(i, j) for i in range(width) for j in range(width) if off[i][j]] == [(0, q), (q + 1, 2)],
        "B is not the two-corner witness",
    )
    first, first_query, second, second_query = local_pair(proj, off)
    require(dense_mm(first, second) == zeros(2 * width), "halves do not annihilate")
    require(dense_mm(second, first) == zeros(2 * width), "the opposite half product is not zero")
    require(add(first, second) == eye(2 * width), "halves do not resolve the stage support")
    require(dense_mm(second, first_query) == zeros(2 * width), "P' R is not zero")
    require(dense_mm(first_query, second) == zeros(2 * width), "R P' is not zero")
    require(dense_mm(first, second_query) == zeros(2 * width), "P R' is not zero")
    require(dense_mm(second_query, first) == zeros(2 * width), "R' P is not zero")
    swap = zeros(2 * width)
    for i in range(width):
        swap[i][width + i] = 1
        swap[width + i][i] = 1
    require(dense_mm(first, swap) == dense_mm(swap, first), "J_0 does not commute with P")
    require(dense_mm(second, swap) == dense_mm(swap, second), "J_0 does not commute with P'")
    stage_a = embed(first, 0, 2, width)
    stage_b = embed(first, 1, 2, width)
    require(dense_mm(stage_a, stage_b) != dense_mm(stage_b, stage_a), "stage projectors commute")
    zero_proj, zero_off = frame(q, False)
    require(not nonzero(zero_off), "the commuting control has nonzero B")
    return proj, complement, off, local_pair(proj, off), local_pair(zero_proj, zero_off)


def check_functionals(proj, complement, off):
    """phi and psi are the written obstructions to (A_Q+B) C = B."""
    width = len(proj)
    require(width == 16, "the column-space certificate is stated for q=8")
    plus = add(proj, off)
    plus_prime = add(complement, off)
    phi = functional_on_columns(plus, (2, 9))
    phi_b = functional_on_columns(off, (2, 9))
    require(all(value == 0 for value in phi), "phi does not vanish on the columns of A+B")
    require(phi_b[2] == 1 and all(value == 0 for i, value in enumerate(phi_b) if i != 2),
            "phi does not separate column 2 of B")
    psi = functional_on_columns(plus_prime, (0, 8))
    psi_b = functional_on_columns(off, (0, 8))
    require(all(value == 0 for value in psi), "psi does not vanish on the columns of A'+B")
    require(psi_b[8] == 1 and all(value == 0 for i, value in enumerate(psi_b) if i != 8),
            "psi does not separate column 8 of B")
    concrete = eye(width)
    for i in range(8, width):
        concrete[i][i] = 0
    for operator in (plus, plus_prime):
        image = dense_mm(operator, concrete)
        require(nonzero(add(off, image)), "the exhibited rank-8 block landed in the image")


def check_dense_match():
    """The fast updater agrees with dense conjugation on a 3-leaf split word."""
    q = 4
    width = 2 * q
    g = 3
    proj, off = frame(q, True)
    complement = [row[:] for row in proj]
    for i in range(width):
        complement[i][i] ^= 1
    pair = local_pair(proj, off)
    small_c = eye(width)
    for i in range(q, width):
        small_c[i][i] = 0
    correction = leaf_block(g, width, 0, 1, small_c)
    internal = add(full_swap(g, width), correction)
    values = (2, 3, 4)
    for order in ("A-then-A", "A-prime-first"):
        calls = split_word(g, width, pair, [internal], [correction], order)
        pure_fast, state_fast = run(calls, values, dense=False)
        pure_dense, state_dense = run(calls, values, dense=True)
        require(pure_fast == pure_dense == target(values, g, width),
                "the small pure product disagreed")
        require(state_fast == state_dense, "fast conjugation disagreed with the dense formula")
        aq = second_diagonal(order, proj, complement)
        transported = add(off, dense_mm(add(aq, off), small_c))
        got = block(state_fast, width, 2 * width, width)
        require(got == into_leaf0(off, values, 1, transported),
                "the small split word missed the leaf-supported formula")


def leaf_to_leaf(state, width, g, source, dest):
    return block(state, width * (dest + 1), width * (source + 1), width)


def check_profile():
    g, q = 13, 8
    width = 2 * q
    proj, complement, off, pair, commuting = check_pair(q)
    check_functionals(proj, complement, off)
    check_dense_match()
    require(all(len(point) == g and all(point) and point[0] != 1 for point in POINTS),
            "a test point is not an invertible specialization with D0 != 1")
    ones = (1,) * g
    swap = full_swap(g, width)
    concrete = eye(width)
    for i in range(8, width):
        concrete[i][i] = 0
    other = zeros(width)
    other[0][1] = 1
    correction = leaf_block(g, width, 0, 1, concrete)
    varied = add(correction, leaf_block(g, width, 1, 0, other))
    require(rank(correction) == 8, "the leaf-supported example does not have rank 8")
    maps = []
    cover = [0] * width
    for bundle in BUNDLES:
        require(len(bundle) == 4 and len(set(bundle)) == 4, "a bundle is not four coordinates")
        for coord in bundle:
            cover[coord] += 1
        matrix = coordinate_map(g, width, bundle)
        require(rank(matrix) == 8, "a named bundle does not have rank 8")
        masked = zero_columns(off, bundle)
        require(nonzero(masked), "a named bundle contains both nonzero columns of B")
        require(2 not in bundle or 8 not in bundle, "a named bundle contains both columns 2 and 8")
        maps.append(matrix)
    require(all(count % 2 == 1 for count in cover), "bundle coverage is not odd")
    total = zeros(width * (g + 1))
    for matrix in maps:
        total = add(total, matrix)
    require(total == swap, "the five bundles do not sum to the D=1 swap")
    witness = coordinate_map(g, width, WITNESS)
    require(rank(witness) == q, "the coordinate witness does not have rank 8")
    require(not nonzero(zero_columns(off, WITNESS)), "columns 2 and 8 of B survived the witness")
    require(not nonzero(zero_rows(off, WITNESS)), "rows 0 and 9 of B survived the witness")

    for order in ("A-then-A", "A-prime-first"):
        aq = second_diagonal(order, proj, complement)
        transported = add(off, dense_mm(add(aq, off), concrete))
        require(nonzero(transported), "the leaf-supported transport vanished before scaling")
        calls = split_word(g, width, pair, [add(swap, correction)], [correction], order)
        varied_calls = split_word(g, width, pair, [add(swap, varied)], [varied], order)
        pure, state = run(calls, ones)
        require(pure == target(ones, g, width) and state == eye(width * (g + 1)),
                "the balanced leaf insertion missed the D_j=1 swap")
        for values in POINTS:
            pure, state = run(calls, values)
            pure_v, state_v = run(varied_calls, values)
            require(pure == pure_v == target(values, g, width), "a thin map changed the pure product")
            got = leaf_to_leaf(state, width, g, 1, 0)
            require(got == into_leaf0(off, values, 1, transported),
                    "leaf 0 <- leaf 1 disagreed with the leaf-supported formula")
            require(leaf_to_leaf(state_v, width, g, 1, 0) == got,
                    "the opposite leaf block changed leaf 0 <- leaf 1")
            require(nonzero(got), "the leaf-supported block vanished at D0 != 1")
            for leaf in (2, g - 1):
                other_block = leaf_to_leaf(state, width, g, leaf, 0)
                require(other_block == into_leaf0(off, values, leaf, off),
                        "a leaf outside the support did not keep the uncorrected block")
                require(leaf_to_leaf(state_v, width, g, leaf, 0) == other_block,
                        "the opposite block changed a different leaf")
        bare = split_word(g, width, pair, [swap], [], order)
        pure, state = run(bare, POINTS[0])
        require(leaf_to_leaf(state, width, g, 1, 0) == into_leaf0(off, POINTS[0], 1, off),
                "the empty after-gap did not recover the uncorrected block")
        zero_calls = split_word(g, width, commuting, [swap], [], order)
        _, zero_state = run(zero_calls, POINTS[0])
        require(leaf_to_leaf(zero_state, width, g, 1, 0) == zeros(width),
                "B = 0 produced a leaf block with no correction")
        zero_corrected = split_word(
            g, width, commuting, [add(swap, correction)], [correction], order,
        )
        _, zero_moved = run(zero_corrected, POINTS[0])
        zero_transport = dense_mm(aq, concrete)
        require(
            leaf_to_leaf(zero_moved, width, g, 1, 0)
            == into_leaf0(off, POINTS[0], 1, zero_transport),
            "B = 0 disagreed with the same transport formula",
        )

        for bundle, matrix in zip(BUNDLES, maps):
            bundle_calls = split_word(g, width, pair, [add(swap, matrix)], [matrix], order)
            pure, state = run(bundle_calls, ones)
            require(pure == target(ones, g, width) and state == eye(width * (g + 1)),
                    "moving one named bundle missed the D_j=1 swap")
            masked_columns = zero_columns(off, bundle)
            masked_rows = zero_rows(off, bundle)
            for values in POINTS:
                pure, state = run(bundle_calls, values)
                require(pure == target(values, g, width), "a bundle changed the pure product")
                for leaf in (1, g - 1):
                    got = leaf_to_leaf(state, width, g, leaf, 0)
                    back = leaf_to_leaf(state, width, g, 0, leaf)
                    require(got == into_leaf0(off, values, leaf, masked_columns),
                            "a named bundle disagreed with B restricted to its complement")
                    require(back == out_of_leaf0(off, values, leaf, masked_rows),
                            "the opposite bundle block disagreed with the row restriction")
                    require(nonzero(got), "a named bundle cancelled leaf 0 <- leaf t")

        witness_calls = split_word(g, width, pair, [add(swap, witness)], [witness], order)
        pure, state = run(witness_calls, ones)
        require(pure == target(ones, g, width) and state == eye(width * (g + 1)),
                "the coordinate witness missed the D_j=1 swap")
        partner_calls = split_word(
            g, width, pair,
            [add(add(swap, witness), correction)],
            [add(witness, correction)],
            order,
        )
        for values in POINTS:
            pure, state = run(witness_calls, values)
            require(pure == target(values, g, width), "the witness changed the pure product")
            require(state != eye(width * (g + 1)), "the witness met the endpoint")
            for source in range(g):
                for dest in range(g):
                    if source == dest:
                        continue
                    require(leaf_to_leaf(state, width, g, source, dest) == zeros(width),
                            "the witness left a leaf-to-leaf block")
            residual = add(state, eye(width * (g + 1)))
            require(rank(residual) == 32, "the witness defect does not have rank 32")
            _, partner = run(partner_calls, values)
            difference = add(partner, state)
            require(rank(difference) <= 16, "a balanced rank-8 partner moved the state by rank above 16")
            require(partner != eye(width * (g + 1)), "a balanced rank-8 partner met the endpoint")


def main():
    check_profile()
    print("PASS_PAIRED_STAR_G13_AFTER_STAGE0_BLOCK")


if __name__ == "__main__":
    main()
