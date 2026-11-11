#!/usr/bin/env python3
"""One other legal off-diagonal block at A = diag(I_8, 0).

B = E_{0,8} + E_{8,0} satisfies both (A+B)C = B and (A'+B)C' = B.
In the after-stage-0 split the matching block cancels leaf 0 <- leaf 1.
The named pair E_{0,8}+E_{9,2} remains a separate obstruction.

Checks raise SystemExit, so python -O does not drop them.
"""

WIDTH = 16
LEAVES = 3
SPACE = WIDTH * (1 + LEAVES)
LEAF0 = WIDTH
LEAF1 = 2 * WIDTH
LEAF2 = 3 * WIDTH

# F_4 = F_2[t]/(t^2+t+1). Elements are 0, 1, t=2, t+1=3.
MUL = (
    (0, 0, 0, 0),
    (0, 1, 2, 3),
    (0, 2, 3, 1),
    (0, 3, 1, 2),
)
INV = {1: 1, 2: 3, 3: 2}


def require(ok, message):
    if not ok:
        raise SystemExit(message)


def zeros(size):
    return [[0] * size for _ in range(size)]


def eye(size):
    matrix = zeros(size)
    for i in range(size):
        matrix[i][i] = 1
    return matrix


def unit(row, col, size=WIDTH):
    matrix = zeros(size)
    matrix[row][col] = 1
    return matrix


def add(left, right):
    return [[x ^ y for x, y in zip(row, other)] for row, other in zip(left, right)]


def scale(matrix, scalar):
    return [[MUL[scalar][entry] for entry in row] for row in matrix]


def matmul(left, right):
    size = len(left)
    out = zeros(size)
    for i in range(size):
        for k in range(size):
            factor = left[i][k]
            if factor:
                source = right[k]
                dest = out[i]
                for j in range(size):
                    dest[j] ^= MUL[factor][source[j]]
    return out


def equal(left, right):
    return left == right


def nonzero(matrix):
    return any(entry for row in matrix for entry in row)


def support(matrix):
    return [(i, j) for i, row in enumerate(matrix) for j, entry in enumerate(row) if entry]


def subblock(matrix, row, col, size=WIDTH):
    return [line[col:col + size] for line in matrix[row:row + size]]


def place(matrix, row, col, block):
    for i, line in enumerate(block):
        matrix[row + i][col:col + len(line)] = line


def rank(matrix):
    rows = [row[:] for row in matrix]
    lead = 0
    for col in range(len(rows[0])):
        pivot = next((i for i in range(lead, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[lead], rows[pivot] = rows[pivot], rows[lead]
        inverse = INV[rows[lead][col]]
        rows[lead] = [MUL[inverse][entry] for entry in rows[lead]]
        for i, row in enumerate(rows):
            if i != lead and row[col]:
                factor = row[col]
                rows[i] = [entry ^ MUL[factor][rows[lead][j]] for j, entry in enumerate(row)]
        lead += 1
    return lead


def projection():
    matrix = zeros(WIDTH)
    for i in range(8):
        matrix[i][i] = 1
    return matrix


def complement(diag):
    return add(eye(WIDTH), diag)


def embed(diag, corner, leaf):
    """Stage projector on the core and one leaf, inside the four-block space."""
    matrix = zeros(SPACE)
    mixed = add(diag, corner)
    for i in range(WIDTH):
        for j in range(WIDTH):
            matrix[i][j] = mixed[i][j]
            matrix[i][leaf + j] = corner[i][j]
            matrix[leaf + i][j] = corner[i][j]
            matrix[leaf + i][leaf + j] = mixed[i][j]
    return matrix


def query(diag, leaf):
    matrix = zeros(SPACE)
    for i in range(WIDTH):
        for j in range(WIDTH):
            matrix[i][j] = diag[i][j]
            matrix[i][leaf + j] = diag[i][j]
            matrix[leaf + i][j] = diag[i][j]
            matrix[leaf + i][leaf + j] = diag[i][j]
    return matrix


def swap():
    matrix = zeros(SPACE)
    for leaf in (LEAF0, LEAF1, LEAF2):
        for i in range(WIDTH):
            matrix[i][leaf + i] = 1
            matrix[leaf + i][i] = 1
    return matrix


def correction(forward, backward):
    matrix = zeros(SPACE)
    place(matrix, LEAF0, LEAF1, forward)
    place(matrix, LEAF1, LEAF0, backward)
    return matrix


def full_call(state, diag, corner, leaf, value):
    projector = embed(diag, corner, leaf)
    factor = value ^ 1
    forward = add(eye(SPACE), scale(projector, factor))
    backward = add(eye(SPACE), scale(projector, MUL[factor][INV[value]]))
    require(equal(matmul(forward, backward), eye(SPACE)), "a half call is not invertible")
    return add(matmul(forward, matmul(state, backward)), query(diag, leaf))


def completed_stage(state, leaf, value, first):
    state = full_call(state, first, CORNER, leaf, value)
    return full_call(state, complement(first), CORNER, leaf, value)


def gap_word(second, forward, backward, values):
    """After-stage-0 split on core and leaves 0, 1, 2, then stages 1 and 2."""
    state = full_call(zeros(SPACE), complement(second), CORNER, LEAF0, values[0])
    state = add(state, add(SWAP, correction(forward, backward)))
    state = full_call(state, second, CORNER, LEAF0, values[0])
    state = add(state, correction(forward, backward))
    state = completed_stage(state, LEAF1, values[1], PROJ)
    return completed_stage(state, LEAF2, values[2], PROJ)


def integer_product(left, right):
    size = len(left)
    out = [[0] * size for _ in range(size)]
    for i in range(size):
        for k in range(size):
            if left[i][k]:
                for j in range(size):
                    out[i][j] += left[i][k] * right[k][j]
    return out


def column(matrix, index):
    return [row[index] for row in matrix]


PROJ = projection()
COMP = complement(PROJ)
CORNER = add(unit(0, 8), unit(8, 0))
NAMED = add(unit(0, 8), unit(9, 2))
SOLVE = add(add(unit(0, 0), unit(8, 0)), unit(8, 8))
SOLVE_COMP = add(add(unit(0, 0), unit(0, 8)), unit(8, 8))
SWAP = swap()
ZERO = zeros(WIDTH)


def check_algebra():
    require(equal(matmul(PROJ, PROJ), PROJ), "A is not idempotent")
    require(equal(COMP, add(eye(WIDTH), PROJ)), "A' is not I+A")
    require(equal(add(matmul(PROJ, CORNER), matmul(CORNER, PROJ)), CORNER), "AB+BA is not B")
    require(
        equal(add(matmul(COMP, CORNER), matmul(CORNER, COMP)), CORNER),
        "A'B+BA' is not B",
    )
    require(nonzero(CORNER), "B is zero")
    require(CORNER != NAMED, "B repeats the named pair")
    require(CORNER[8][0] == 1 and NAMED[8][0] == 0, "the transposition corner was not set")
    require(CORNER[9][2] == 0 and NAMED[9][2] == 1, "the named corner was not distinguished")
    require(equal(matmul(add(PROJ, CORNER), SOLVE), CORNER), "(A+B)C is not B")
    require(equal(matmul(add(COMP, CORNER), SOLVE_COMP), CORNER), "(A'+B)C' is not B")
    require(not equal(matmul(add(PROJ, CORNER), SOLVE_COMP), CORNER), "C' solves the A equation")
    require(not equal(matmul(add(COMP, CORNER), SOLVE), CORNER), "C solves the A' equation")
    require(not equal(matmul(add(PROJ, CORNER), ZERO), CORNER), "the zero matrix solves (A+B)C=B")
    require(rank(CORNER) == 2, "B does not have rank 2")
    require(rank(add(PROJ, CORNER)) == 9, "A+B does not have rank 9")
    require(rank(add(COMP, CORNER)) == 9, "A'+B does not have rank 9")

    summed = [[PROJ[i][j] + CORNER[i][j] for j in range(WIDTH)] for i in range(WIDTH)]
    product = integer_product(summed, SOLVE)
    require(product[0][0] == 2, "the integer product does not witness characteristic 2")
    require(product[8][0] == 1 and product[0][8] == 1, "the integer support of B moved")


def check_named_obstruction():
    mixed = add(PROJ, NAMED)
    for index in range(WIDTH):
        vector = column(mixed, index)
        require(vector[2] ^ vector[9] == 0, "phi fails to vanish on a column of A+B_0")
    separated = column(NAMED, 2)
    require(separated[2] ^ separated[9] == 1, "phi does not separate column 2 of B_0")
    mixed = add(COMP, NAMED)
    for index in range(WIDTH):
        vector = column(mixed, index)
        require(vector[0] ^ vector[8] == 0, "psi fails to vanish on a column of A'+B_0")
    separated = column(NAMED, 8)
    require(separated[0] ^ separated[8] == 1, "psi does not separate column 8 of B_0")


def check_half_relations():
    for diag in (PROJ, COMP):
        projector = embed(diag, CORNER, LEAF0)
        require(equal(matmul(projector, projector), projector), "a half projector is not idempotent")
    left = embed(PROJ, CORNER, LEAF0)
    right = embed(COMP, CORNER, LEAF0)
    require(equal(matmul(left, right), zeros(SPACE)), "the two halves do not multiply to zero")
    require(equal(matmul(right, left), zeros(SPACE)), "the swapped halves do not multiply to zero")
    require(equal(add(left, right), eye_on_support(LEAF0)), "the two halves do not resolve the stage")
    query_a = query(PROJ, LEAF0)
    query_c = query(COMP, LEAF0)
    require(equal(matmul(right, query_a), zeros(SPACE)), "P'R is not zero")
    require(equal(matmul(query_a, right), zeros(SPACE)), "RP' is not zero")
    require(equal(matmul(left, query_c), zeros(SPACE)), "PR' is not zero")
    require(equal(matmul(query_c, left), zeros(SPACE)), "R'P is not zero")


def eye_on_support(leaf):
    matrix = zeros(SPACE)
    for index in list(range(WIDTH)) + list(range(leaf, leaf + WIDTH)):
        matrix[index][index] = 1
    return matrix


def check_schedule():
    noise = unit(3, 4)
    values = ((2, 3, 2), (3, 2, 3))
    orders = ((PROJ, SOLVE, "A"), (COMP, SOLVE_COMP, "A'"))
    for spec in values:
        for second, solution, label in orders:
            done = gap_word(second, solution, ZERO, spec)
            got = subblock(done, LEAF0, LEAF1)
            require(not nonzero(got), "the matching block left leaf 0 <- leaf 1 nonzero for " + label)
            plain = gap_word(second, ZERO, ZERO, spec)
            raw = subblock(plain, LEAF0, LEAF1)
            expected = scale(CORNER, MUL[INV[spec[1]]][spec[0] ^ 1])
            require(equal(raw, expected), "the empty correction missed D_1^{-1}(D_0+1)B for " + label)
            require(nonzero(raw), "the empty correction cancelled the block for " + label)
            other = SOLVE_COMP if second is PROJ else SOLVE
            wrong = subblock(gap_word(second, other, ZERO, spec), LEAF0, LEAF1)
            require(nonzero(wrong), "the opposite witness cancelled the block for " + label)
            hidden = subblock(gap_word(second, solution, noise, spec), LEAF0, LEAF1)
            require(equal(hidden, got), "the opposite block E changed leaf 0 <- leaf 1 for " + label)
            opposite = subblock(gap_word(second, solution, ZERO, spec), LEAF1, LEAF0)
            require(nonzero(opposite), "E=0 made the opposite leaf block zero for " + label)
    for spec in values:
        for second, solution in ((PROJ, SOLVE), (COMP, SOLVE_COMP)):
            for stage_first in (PROJ, COMP):
                state = replay_with_stage_order(second, solution, ZERO, spec, stage_first)
                require(
                    not nonzero(subblock(state, LEAF0, LEAF1)),
                    "changing the stage-1 half order restored the leaf block",
                )


def replay_with_stage_order(second, forward, backward, values, stage_first):
    state = full_call(zeros(SPACE), complement(second), CORNER, LEAF0, values[0])
    state = add(state, add(SWAP, correction(forward, backward)))
    state = full_call(state, second, CORNER, LEAF0, values[0])
    state = add(state, correction(forward, backward))
    state = completed_stage(state, LEAF1, values[1], stage_first)
    return completed_stage(state, LEAF2, values[2], stage_first)


def main():
    check_algebra()
    check_named_obstruction()
    check_half_relations()
    check_schedule()
    print("PASS_PAIRED_STAR_TRANSPOSE_CORNER")


if __name__ == "__main__":
    main()
