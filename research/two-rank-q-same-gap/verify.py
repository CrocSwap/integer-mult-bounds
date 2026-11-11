#!/usr/bin/env python3
"""Two rank-at-most-q maps in one paired-star internal gap.

Proof checks over GF(2), plus one exhaustive q=1 census. Checks raise
SystemExit, so python -O does not drop them. No kappa is computed.
"""

from __future__ import annotations

G = 31
Q = 26


def fail(message):
    raise SystemExit(message)


def expect_fail(name, fn):
    try:
        fn()
    except SystemExit:
        return
    fail("control did not fail: " + name)


def zeros(rows, cols=None):
    width = rows if cols is None else cols
    return [[0] * width for _ in range(rows)]


def eye(size):
    return [[1 if row == col else 0 for col in range(size)] for row in range(size)]


def mat_add(left, right):
    return [[a ^ b for a, b in zip(row_a, row_b)] for row_a, row_b in zip(left, right)]


def mat_mul(left, right):
    rows = len(left)
    mid = len(right)
    cols = len(right[0])
    out = zeros(rows, cols)
    for i in range(rows):
        for k in range(mid):
            if left[i][k]:
                row = out[i]
                src = right[k]
                for j in range(cols):
                    row[j] ^= src[j]
    return out


def is_zero(matrix):
    return all(entry == 0 for row in matrix for entry in row)


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
                active[row] = [a ^ b for a, b in zip(active[row], active[rank])]
        rank += 1
        col += 1
    return rank


def block_matrix(q, blocks):
    """Place a 4-by-4 array of q-by-q blocks into the stage coordinates."""
    size = 8 * q
    matrix = zeros(size)
    for block_row in range(4):
        for block_col in range(4):
            block = blocks[block_row][block_col]
            for row in range(q):
                for col in range(q):
                    matrix[block_row * q + row][block_col * q + col] = block[row][col]
    return matrix


def half(q, plus, b12, b21):
    zero = zeros(q)
    ident = eye(q)
    if plus:
        blocks = (
            (ident, b12, zero, b12),
            (b21, zero, b21, zero),
            (zero, b12, ident, b12),
            (b21, zero, b21, zero),
        )
    else:
        blocks = (
            (zero, b12, zero, b12),
            (b21, ident, b21, zero),
            (zero, b12, zero, b12),
            (b21, zero, b21, ident),
        )
    return block_matrix(q, blocks)


def scalar_block(q, bit):
    return [[bit if row == col else 0 for col in range(q)] for row in range(q)]


def projectors(q, b12_bit, b21_bit, plus_first):
    b12 = scalar_block(q, b12_bit)
    b21 = scalar_block(q, b21_bit)
    if plus_first:
        return half(q, True, b12, b21), half(q, False, b12, b21)
    return half(q, False, b12, b21), half(q, True, b12, b21)


def at(q, block, index):
    return block * q + index


def put(matrix, row, col):
    matrix[row][col] ^= 1


def witness_pair(q, plus_first):
    """Two rank-q maps. Each kills im P_f. Their three core blocks sum to I."""
    size = 8 * q
    first = zeros(size)
    second = zeros(size)
    for index in range(q):
        c_plus = at(q, 0, index)
        c_minus = at(q, 1, index)
        s_plus = at(q, 2, index)
        s_minus = at(q, 3, index)
        p_plus = at(q, 4, index)
        p_minus = at(q, 5, index)
        n_plus = at(q, 6, index)
        n_minus = at(q, 7, index)
        if plus_first:
            for col in (c_minus, s_minus, p_minus, n_plus):
                put(first, c_plus, col)
            for col in (c_plus, c_minus, s_plus, p_plus, n_plus, n_minus):
                put(second, c_plus, col)
                put(second, c_minus, col)
        else:
            for col in (c_plus, s_plus, p_plus, n_minus):
                put(first, c_plus, col)
            for col in (c_minus, s_plus, s_minus, p_plus, p_minus, n_plus):
                put(second, c_plus, col)
                put(second, c_minus, col)
    return first, second


def predecessor_witness(q, complementary_sources):
    """The rank-q witness of PR #7053, or the same pattern on the other leaf halves."""
    size = 8 * q
    matrix = zeros(size)
    for index in range(q):
        if complementary_sources:
            sources = (at(q, 7, index), at(q, 4, index), at(q, 2, index))
        else:
            sources = (at(q, 6, index), at(q, 5, index), at(q, 3, index))
        for source in sources:
            put(matrix, at(q, 0, index), source)
            put(matrix, at(q, 1, index), source)
    return matrix


def core_slice(matrix, q, col_start):
    return [row[col_start:col_start + 2 * q] for row in matrix[: 2 * q]]


def three_blocks(matrix, first, second, q):
    nxt = mat_mul(first, matrix)
    prev = mat_mul(second, matrix)
    pinch = mat_add(
        mat_mul(first, mat_mul(matrix, first)),
        mat_mul(second, mat_mul(matrix, second)),
    )
    return core_slice(nxt, q, 6 * q), core_slice(prev, q, 4 * q), core_slice(pinch, q, 2 * q)


def square_clear(matrix, first, second):
    return is_zero(mat_mul(second, mat_mul(matrix, first)))


def require_identity_pair(q, plus_first):
    first, second = projectors(q, 1, 1, plus_first)
    if mat_mul(first, first) != first or mat_mul(second, second) != second:
        fail("halves are not idempotent")
    if not is_zero(mat_mul(first, second)) or not is_zero(mat_mul(second, first)):
        fail("halves do not annihilate")
    stage = eye(4 * q)
    top = [row[: 4 * q] for row in mat_add(first, second)[: 4 * q]]
    if top != stage:
        fail("halves do not resolve the stage")
    left, right = witness_pair(q, plus_first)
    for name, matrix in (("first", left), ("second", right)):
        if not square_clear(matrix, first, second):
            fail(name + " map failed P_s Z P_f = 0")
        if rank_rows(matrix) != q:
            fail(name + " map does not have rank q")
    total = mat_add(left, right)
    if not square_clear(total, first, second):
        fail("the sum failed P_s Z P_f = 0")
    if rank_rows(total) != 2 * q:
        fail("the sum does not have rank 2q")
    ident = eye(2 * q)
    blocks = three_blocks(total, first, second, q)
    names = ("next", "previous", "own")
    for name, block in zip(names, blocks):
        if block != ident:
            fail(name + " block is not I_2q")
    # One map alone cannot fill a block: each block of each summand has rank q.
    for matrix in (left, right):
        for block in three_blocks(matrix, first, second, q):
            if rank_rows(block) != q:
                fail("a single summand block is not rank q")
    return left


def check_identity_family():
    for q in (1, 2, 3, 8, Q):
        for plus_first in (True, False):
            require_identity_pair(q, plus_first)


def check_direct_sum_shape():
    """Every index of the q-witness is the q=1 witness, with no cross terms."""
    for plus_first in (True, False):
        seed_left, seed_right = witness_pair(1, plus_first)
        left, right = witness_pair(Q, plus_first)
        for matrix, seed in ((left, seed_left), (right, seed_right)):
            for index in range(Q):
                for block_row in range(8):
                    for block_col in range(8):
                        entry = matrix[at(Q, block_row, index)][at(Q, block_col, index)]
                        if entry != seed[block_row][block_col]:
                            fail("index slice differs from the q=1 witness")
            for row in range(8 * Q):
                for col in range(8 * Q):
                    if (row % Q) != (col % Q) and matrix[row][col]:
                        fail("witness has a cross term")


def check_singular_cap():
    """pi_core P_+ has image dimension q + rank(B21), for several explicit B."""
    q = 4
    samples = (
        (zeros(q), 0),
        (eye(q), q),
        ([[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], 1),
        ([[1, 1, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0]], 3),
    )
    for b21, expected in samples:
        for b12, _rank in samples:
            plus = half(q, True, b12, b21)
            minus = half(q, False, b12, b21)
            plus_rank = rank_rows(plus[: 2 * q])
            minus_rank = rank_rows(minus[: 2 * q])
            if plus_rank != q + expected:
                fail("pi_core P_+ rank is not q + rank(B21)")
            if minus_rank != q + rank_rows(b12):
                fail("pi_core P_- rank is not q + rank(B12)")
            if expected < q and plus_rank >= 2 * q:
                fail("singular B21 had full core image")


def check_first_step():
    """Complementary copies of the PR #7053 witness do not reach rank 2q."""
    for q in (1, 2, Q):
        first, second = projectors(q, 0, 0, True)
        original = predecessor_witness(q, False)
        shifted = predecessor_witness(q, True)
        if not square_clear(original, first, second):
            fail("the rank-q witness failed the square condition")
        ranks = tuple(rank_rows(block) for block in three_blocks(original, first, second, q))
        if ranks != (q, q, q):
            fail("the rank-q witness blocks are not (q, q, q)")
        if square_clear(shifted, first, second):
            fail("the complementary-source copy unexpectedly satisfied the square condition")
        summed = mat_add(original, shifted)
        if square_clear(summed, first, second):
            fail("the complementary-source sum unexpectedly satisfied the square condition")
        sum_ranks = tuple(rank_rows(block) for block in three_blocks(summed, first, second, q))
        if sum_ranks[0] == 2 * q or sum_ranks[1] == 2 * q:
            fail("complementary sources reached rank 2q on an outside block")
        if sum_ranks[0] != q or sum_ranks[1] != q:
            fail("complementary-source outside blocks are not rank q")
        # Image split onto the two core halves. The minus copy is not admissible.
        plus_only = zeros(8 * q)
        minus_only = zeros(8 * q)
        for index in range(q):
            for source in (at(q, 6, index), at(q, 5, index), at(q, 3, index)):
                put(plus_only, at(q, 0, index), source)
            for source in (at(q, 7, index), at(q, 4, index), at(q, 2, index)):
                put(minus_only, at(q, 1, index), source)
        if not square_clear(plus_only, first, second):
            fail("the plus-core copy failed the square condition")
        if square_clear(minus_only, first, second):
            fail("the minus-core copy unexpectedly satisfied the square condition")
        split = mat_add(plus_only, minus_only)
        split_ranks = tuple(rank_rows(block) for block in three_blocks(split, first, second, q))
        if split_ranks[0] >= 2 * q or split_ranks[1] >= 2 * q or split_ranks[2] >= 2 * q:
            fail("complementary core directions reached rank 2q")


def helped_leaves(leaves, stage):
    values = []
    if stage > 0:
        values.append(stage - 1)
    values.append(stage)
    if stage + 1 < leaves:
        values.append(stage + 1)
    return values


def full_cancel_demands(leaves, stage):
    values = [2] * leaves
    for leaf in helped_leaves(leaves, stage):
        values[leaf] = 0
    return values


def parity_coefficient(values):
    even = sum(values[index] for index in range(0, len(values), 2))
    odd = sum(values[index] for index in range(1, len(values), 2))
    return max(even, odd)


def predicted_coefficient(leaves, stage):
    if leaves % 2 == 0:
        return leaves - 2
    if stage % 2 == 0:
        return leaves - 1
    return leaves - 3


def run_lengths(leaves, stage):
    """Unhelped leaves form a left run and a right run, separated by the helped block."""
    helped = helped_leaves(leaves, stage)
    left = helped[0]
    right = leaves - 1 - helped[-1]
    return left, right


def cover_tuple(leaves, stage):
    """Weight-2 gaps: ceil(m/2) on each unhelped run, on disjoint gap sets."""
    left, right = run_lengths(leaves, stage)
    helped = helped_leaves(leaves, stage)
    ranks = [0] * (leaves + 1)
    for offset in range(0, left, 2):
        ranks[offset + 1] = 2
    start = helped[-1] + 1
    for offset in range(0, right, 2):
        ranks[start + offset + 1] = 2
    return ranks


def check_counting():
    for leaves in range(3, 41):
        for stage in range(leaves):
            values = full_cancel_demands(leaves, stage)
            coefficient = parity_coefficient(values)
            if coefficient != predicted_coefficient(leaves, stage):
                fail("parity coefficient mismatch at g=%d stage=%d" % (leaves, stage))
            left, right = run_lengths(leaves, stage)
            hits = (left + 1) // 2 + (right + 1) // 2
            if 2 * hits != coefficient:
                fail("hitting-set size differs from the heavier parity")
            ranks = cover_tuple(leaves, stage)
            for leaf in range(leaves):
                if ranks[leaf] + ranks[leaf + 1] < values[leaf]:
                    fail("cover tuple missed a leaf")
            if sum(ranks) != coefficient:
                fail("cover tuple has the wrong total")
            for gap, rank in enumerate(ranks):
                if rank == 0:
                    continue
                trial = ranks[:]
                trial[gap] -= 1
                if all(trial[leaf] + trial[leaf + 1] >= values[leaf] for leaf in range(leaves)):
                    fail("a minimum tuple had a spare gap")
        if leaves % 2 == 1:
            for stage in range(0, leaves, 2):
                values = full_cancel_demands(leaves, stage)
                unhelped_even = sum(1 for leaf in range(0, leaves, 2) if values[leaf] == 2)
                if 2 * unhelped_even != leaves - 1:
                    fail("even stage unhelped count is not g-1")
    if predicted_coefficient(G, 1) != G - 3 or predicted_coefficient(G, 2) != G - 1:
        fail("g=31 coefficients changed")
    if (G - 3) * Q != 728 or (G - 1) * Q != 780:
        fail("profile ranks changed")


def bits_of(matrix):
    columns = []
    for col in range(8):
        value = 0
        for row in range(8):
            if matrix[row][col]:
                value |= 1 << row
        columns.append(value)
    return columns


def span_basis(columns):
    basis = []
    for column in columns:
        value = column
        for pivot in basis:
            if value & pivot[0]:
                value ^= pivot[1]
        if value:
            lead = value & -value
            basis.append((lead, value))
    return basis


def in_span(vector, basis):
    value = vector
    for lead, row in basis:
        if value & lead:
            value ^= row
    return value == 0


def dot(left, right):
    return (left & right).bit_count() & 1


def projected_core(columns, vector):
    """Core coordinates of a projector applied to a vector."""
    out = 0
    bit = vector
    index = 0
    while bit:
        if bit & 1:
            out ^= columns[index]
        bit >>= 1
        index += 1
    return out & 3


def own_block(image, functional, first_cols, second_cols):
    """Own-leaf core block of the rank-1 map image * functional^T."""

    def pinch(col):
        left = projected_core(first_cols, image) if dot(functional, first_cols[col]) else 0
        right = projected_core(second_cols, image) if dot(functional, second_cols[col]) else 0
        return left ^ right

    return [[(pinch(col) >> row) & 1 for col in (2, 3)] for row in range(2)]


def census_q1():
    """Every rank-at-most-1 matrix on the eight F2 coordinates."""
    admissible = 0
    own_exceed = 0
    for b12 in (0, 1):
        for b21 in (0, 1):
            for plus_first in (0, 1):
                first, second = projectors(1, b12, b21, plus_first == 1)
                if rank_rows(first) != 2 or rank_rows(second) != 2:
                    fail("a scalar half does not have rank 2")
                first_cols = bits_of(first)
                second_cols = bits_of(second)
                basis = span_basis(first_cols)
                for image in range(256):
                    for functional in range(256):
                        if image == 0 or functional == 0:
                            continue
                        # P_s Z P_f = 0 iff the stage part of the image lies in
                        # im P_f, or the functional kills im P_f. Outside-leaf
                        # coordinates of the image are free.
                        conditioned = in_span(image & 15, basis) or all(
                            dot(functional, column) == 0 for column in first_cols
                        )
                        if not conditioned:
                            continue
                        admissible += 1
                        own = own_block(image, functional, first_cols, second_cols)
                        if rank_rows(own) > 1:
                            own_exceed += 1
    if own_exceed:
        fail("q=1 census: a conditioned rank-1 own block exceeded rank 1")
    # im P_f has dimension 2 inside the stage and is zero outside it, so 2^2
    # stage vectors times 2^4 outside vectors, excluding zero, meet the image
    # branch. The annihilator of that plane in the dual of F^8 has 2^{6}-1
    # nonzero functionals. Inclusion-exclusion over the two branches:
    good_images = (1 << 2) * (1 << 4) - 1
    good_functionals = (1 << 6) - 1
    per_half = good_images * 255 + (255 - good_images) * good_functionals
    if admissible != 8 * per_half:
        fail("q=1 admissible count changed: %d" % admissible)
    # The exhibited identity pair sits in this finite domain.
    for plus_first, seeds in (
        (True, ((1, 106), (3, 215))),
        (False, ((1, 149), (3, 126))),
    ):
        first, second = projectors(1, 1, 1, plus_first)
        first_cols = bits_of(first)
        second_cols = bits_of(second)
        basis = span_basis(first_cols)
        for image, functional in seeds:
            if image == 0 or functional == 0:
                fail("seed is not rank 1")
            if not (in_span(image & 15, basis) or all(dot(functional, column) == 0 for column in first_cols)):
                fail("identity seed is outside the conditioned domain")
            matrix = [
                [((image >> row) & 1) & ((functional >> col) & 1) for col in range(8)]
                for row in range(8)
            ]
            dense_own = three_blocks(matrix, first, second, 1)[2]
            if dense_own != own_block(image, functional, first_cols, second_cols):
                fail("bit own block disagrees with dense multiplication")


def check_condition_agreement():
    """The rank-1 stage-image test agrees with dense P_s Z P_f = 0."""
    first, second = projectors(1, 1, 1, True)
    first_cols = bits_of(first)
    basis = span_basis(first_cols)
    for image in range(256):
        for functional in range(256):
            if image == 0 or functional == 0:
                continue
            bit = in_span(image & 15, basis) or all(
                dot(functional, column) == 0 for column in first_cols
            )
            matrix = [
                [((image >> row) & 1) & ((functional >> col) & 1) for col in range(8)]
                for row in range(8)
            ]
            if bit != square_clear(matrix, first, second):
                fail("rank-1 square test disagrees with dense multiplication")


def check_controls():
    def cleared_column():
        first, second = projectors(1, 1, 1, True)
        left, right = witness_pair(1, True)
        left[0][6] = 0
        block = three_blocks(mat_add(left, right), first, second, 1)[0]
        if block != eye(2):
            fail("mutated next block is not I")

    def zero_matrix_still_identity():
        first, second = projectors(Q, 1, 1, True)
        _left, right = witness_pair(Q, True)
        if three_blocks(right, first, second, Q)[0] != eye(2 * Q):
            fail("one map is not the next identity")

    expect_fail("cleared column", cleared_column)
    expect_fail("single map", zero_matrix_still_identity)


def main():
    check_identity_family()
    check_direct_sum_shape()
    check_singular_cap()
    check_first_step()
    check_counting()
    census_q1()
    check_condition_agreement()
    check_controls()
    print(
        "PASS_TWO_RANK_Q_SAME_GAP"
        " blocks=I_2q"
        " singular_next_cap=q+rank(B21)"
        " odd_stage_external=%d"
        " even_stage_external=%d"
        " uniform_q(g-1)_lift=does_not"
        " kappa=363005817/100000000000"
        % ((G - 3) * Q, (G - 1) * Q)
    )


if __name__ == "__main__":
    main()
