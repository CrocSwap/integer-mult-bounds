#!/usr/bin/env python3
"""Checks for the proof that one constant thin map misses g=3 for every q.

PROOF.md is the argument. This file locks the matrix identities that argument
uses, the two-map word that shows the contract is nonempty, and the one-map
words that the forced matrix fails. It does not search projectors or call
orders, and it does not claim an exhaustive census.
"""

from __future__ import annotations

import json
from pathlib import Path


def fail(message):
    raise SystemExit("FAIL: " + message)


def require(ok, message):
    if not ok:
        fail(message)


def eye(n):
    return tuple(tuple(1 if i == j else 0 for j in range(n)) for i in range(n))


def zeros(n, m=None):
    width = n if m is None else m
    return tuple(tuple(0 for _ in range(width)) for _ in range(n))


def mat_add(left, right):
    return tuple(
        tuple(left[i][j] ^ right[i][j] for j in range(len(left[0])))
        for i in range(len(left))
    )


def mat_mul(left, right):
    width = len(right[0])
    shared = len(right)
    out = []
    for row in left:
        acc = [0] * width
        for t, bit in enumerate(row):
            if bit:
                src = right[t]
                for j in range(width):
                    acc[j] ^= src[j]
        out.append(tuple(acc))
    return tuple(out)


def mat_scale_poly(matrix, poly):
    return tuple(tuple(poly if entry else 0 for entry in row) for row in matrix)


def rank(matrix):
    rows = [list(row) for row in matrix]
    if not rows:
        return 0
    width = len(rows[0])
    rank_value = 0
    for col in range(width):
        pivot = next((i for i in range(rank_value, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[rank_value], rows[pivot] = rows[pivot], rows[rank_value]
        for i in range(len(rows)):
            if i != rank_value and rows[i][col]:
                for j in range(width):
                    rows[i][j] ^= rows[rank_value][j]
        rank_value += 1
    return rank_value


def poly_mul(left, right):
    out = 0
    while right:
        if right & 1:
            out ^= left
        left <<= 1
        right >>= 1
    return out


def poly_pow(base, exp):
    out = 1
    while exp:
        if exp & 1:
            out = poly_mul(out, base)
        base = poly_mul(base, base)
        exp >>= 1
    return out


def leibniz_det(matrix):
    """Determinant in F2[x]. Each entry is a bitmask polynomial.

    In characteristic 2 every permutation sign is 1, so the sum runs over all
    permutations. n <= 4 keeps the 24-term expansion immediate.
    """
    import itertools

    size = len(matrix)
    require(size <= 4, "Leibniz determinant is registered only for n <= 4")
    det = 0
    for perm in itertools.permutations(range(size)):
        prod = 1
        for row, col in enumerate(perm):
            prod = poly_mul(prod, matrix[row][col])
        det ^= prod
    return det


def diag_idempotent(q):
    d = 2 * q
    rows = []
    for i in range(d):
        rows.append(tuple(1 if i == j and i < q else 0 for j in range(d)))
    return tuple(rows)


def exchange_b(q):
    """B swaps basis vector 0 with basis vector q and fixes the rest."""
    d = 2 * q
    rows = [[0] * d for _ in range(d)]
    rows[q][0] = 1
    rows[0][q] = 1
    return tuple(tuple(row) for row in rows)


def legal_pair(q, use_b):
    a = diag_idempotent(q)
    b = exchange_b(q) if use_b else zeros(2 * q)
    complement = mat_add(eye(2 * q), a)
    require(mat_mul(a, a) == a, "A is not idempotent")
    require(rank(a) == q, "A does not have rank q")
    require(mat_add(mat_mul(a, b), mat_mul(b, a)) == b, "AB+BA=B failed")
    require(mat_mul(a, complement) == zeros(2 * q), "halves do not annihilate")
    return a, b, complement


def block_matrix(blocks, g, d):
    n = (g + 1) * d
    rows = [[0] * n for _ in range(n)]
    for (bi, bj), block in blocks.items():
        for r in range(d):
            for c in range(d):
                rows[bi * d + r][bj * d + c] = block[r][c]
    return tuple(tuple(row) for row in rows)


def local_p(a, b):
    mixed = mat_add(a, b)
    return ((mixed, b), (b, mixed))


def local_r(a):
    return ((a, a), (a, a))


def stage_matrix(local, stage, g, d):
    blocks = {}
    leaf = stage + 1
    (tl, tr), (bl, br) = local
    blocks[(0, 0)] = tl
    blocks[(0, leaf)] = tr
    blocks[(leaf, 0)] = bl
    blocks[(leaf, leaf)] = br
    return block_matrix(blocks, g, d)


def stage_t(stage, g, d):
    ident = eye(d)
    return stage_matrix(((ident, ident), (ident, ident)), stage, g, d)


def stage_e(stage, g, d):
    ident = eye(d)
    zero = zeros(d)
    return stage_matrix(((ident, zero), (zero, ident)), stage, g, d)


def thin_k(g, d):
    """I + sum_j T_j, the unique constant thin sum at every D_j = 1."""
    n = (g + 1) * d
    acc = eye(n)
    for stage in range(g):
        acc = mat_add(acc, stage_t(stage, g, d))
    return acc


def leaf_column(matrix, leaf, g, d):
    n_blocks = g + 1
    start = leaf * d
    cols = []
    for row_block in range(n_blocks):
        block = []
        for r in range(d):
            block.append(tuple(matrix[row_block * d + r][start + c] for c in range(d)))
        cols.append(tuple(block))
    return tuple(cols)


def columns_identical(matrix, g, d):
    first = leaf_column(matrix, 1, g, d)
    return all(leaf_column(matrix, leaf, g, d) == first for leaf in range(2, g + 1))


def summed_commutator_block(p_mat, m_mat, stage, leaf, d):
    comm = mat_add(mat_mul(p_mat, m_mat), mat_mul(m_mat, p_mat))
    core = 0
    own = stage + 1
    dest = leaf + 1
    out = []
    for r in range(d):
        row = []
        for c in range(d):
            value = comm[core * d + r][dest * d + c] ^ comm[own * d + r][dest * d + c]
            row.append(value)
        out.append(tuple(row))
    return tuple(out)


def predicted_block(a, m_mat, stage, leaf, d):
    own = stage + 1
    dest = leaf + 1
    mixed = []
    for r in range(d):
        mixed.append(
            tuple(
                m_mat[0 * d + r][dest * d + c] ^ m_mat[own * d + r][dest * d + c]
                for c in range(d)
            )
        )
    return mat_mul(a, tuple(mixed))


def probe_matrix(n, seed):
    rows = []
    for i in range(n):
        rows.append(tuple((seed * (i + 3) + 5 * j + 1) & 1 for j in range(n)))
    return tuple(rows)


# Polynomial words. Keys are (e_flag, degree tuple). Values are 0-1 matrices.
def poly_add(left, right):
    out = dict(left)
    for key, value in right.items():
        prev = out.get(key)
        if prev is None:
            out[key] = value
        else:
            summed = mat_add(prev, value)
            if any(any(row) for row in summed):
                out[key] = summed
            else:
                del out[key]
    return out


def poly_matmul(left, right):
    out = {}
    for (e_l, deg_l), mat_l in left.items():
        for (e_r, deg_r), mat_r in right.items():
            if e_l + e_r > 1:
                continue
            key = (e_l + e_r, tuple(a + b for a, b in zip(deg_l, deg_r)))
            prod = mat_mul(mat_l, mat_r)
            prev = out.get(key)
            if prev is None:
                if any(any(row) for row in prod):
                    out[key] = prod
            else:
                summed = mat_add(prev, prod)
                if any(any(row) for row in summed):
                    out[key] = summed
                else:
                    del out[key]
    return out


def full_factor(stage, proj, read, g):
    """(I+(D+1)P)(I+e R) = I+(D+1)P + e D R when PR = RP = R."""
    require(mat_mul(proj, read) == read, "PR = R failed")
    require(mat_mul(read, proj) == read, "RP = R failed")
    n = len(proj)
    ident = eye(n)
    degree = tuple(1 if i == stage else 0 for i in range(g))
    zero = tuple(0 for _ in range(g))
    return {
        (0, zero): mat_add(ident, proj),
        (0, degree): proj,
        (1, degree): read,
    }


def thin_factor(mat, g):
    zero = tuple(0 for _ in range(g))
    return {(0, zero): eye(len(mat)), (1, zero): mat}


def target_word(g, d):
    n = (g + 1) * d
    zero = tuple(0 for _ in range(g))
    word = {(0, zero): eye(n), (1, zero): eye(n)}
    for stage in range(g):
        support = stage_e(stage, g, d)
        degree = tuple(1 if i == stage else 0 for i in range(g))
        factor = {
            (0, zero): mat_add(eye(n), support),
            (0, degree): support,
        }
        word = poly_matmul(factor, word)
    return word


def sharp_thin(stage, g, d, core_identity):
    blocks = {}
    ident = eye(d)
    leaves = [stage] if stage + 1 == g else [stage, stage + 1]
    for leaf in leaves:
        blocks[(0, leaf + 1)] = ident
        blocks[(leaf + 1, 0)] = ident
    if core_identity:
        blocks[(0, 0)] = ident
    return block_matrix(blocks, g, d)


def sharp_word(g, q, use_b):
    d = 2 * q
    a, b, complement = legal_pair(q, use_b)
    factors = []
    for stage in range(g):
        for half in (a, complement):
            proj = stage_matrix(local_p(half, b), stage, g, d)
            read = stage_matrix(local_r(half), stage, g, d)
            factors.append(full_factor(stage, proj, read, g))
        if stage % 2 == 0:
            factors.append(thin_factor(sharp_thin(stage, g, d, core_identity=(g % 2 == 0 and stage == 0)), g))
    word = {(0, tuple(0 for _ in range(g))): eye((g + 1) * d)}
    for factor in factors:
        word = poly_matmul(factor, word)
    return word


def one_map_word(g, q, use_b, order, gap, z_mat):
    d = 2 * q
    a, b, complement = legal_pair(q, use_b)
    calls = []
    for stage, half_name in order:
        half = a if half_name == 0 else complement
        proj = stage_matrix(local_p(half, b), stage, g, d)
        read = stage_matrix(local_r(half), stage, g, d)
        calls.append(full_factor(stage, proj, read, g))
    factors = list(calls)
    factors.insert(gap, thin_factor(z_mat, g))
    word = {(0, tuple(0 for _ in range(g))): eye((g + 1) * d)}
    for factor in factors:
        word = poly_matmul(factor, word)
    return word


def adjacent_order(g):
    order = []
    for stage in range(g):
        order.append((stage, 0))
        order.append((stage, 1))
    return tuple(order)


def check_selected_record():
    path = Path("certificates/selected-result.json")
    record = json.loads(path.read_text(encoding="utf-8"))
    require(record["kappa"] == "781451/250000000", "selected kappa changed")
    require(record["decimal"] == "0.003125804", "selected decimal changed")


def check_k_shape():
    checked = 0
    for g in (3, 4, 5):
        for q in (1, 2, 8):
            d = 2 * q
            k_mat = thin_k(g, d)
            require(columns_identical(k_mat, g, d), "K leaf columns differ")
            require(rank(k_mat) == 2 * d, "rank K is not 2d")
            # Every leaf column is I in the core and 0 on leaves.
            column = leaf_column(k_mat, 1, g, d)
            require(column[0] == eye(d), "core block of a leaf column is not I")
            for leaf in range(1, g + 1):
                require(column[leaf] == zeros(d), "a leaf block of a leaf column is nonzero")
            checked += 1
    # A forged column must be detected. This is the failure control for the
    # identical-column test, not a second mathematical claim.
    k_mat = thin_k(3, 2)
    forged = [list(row) for row in k_mat]
    forged[0][2] ^= 1
    require(not columns_identical(tuple(tuple(row) for row in forged), 3, 2), "forged column was accepted")
    return checked


def check_determinant_gap():
    """(1+x)^{3d} and (1+x)^d differ, and det(I+xA) matches the rank formula."""
    cases = 0
    for q in (1, 2):
        d = 2 * q
        a, b, complement = legal_pair(q, use_b=True)
        for half in (a, complement):
            matrix = []
            for i in range(d):
                row = []
                for j in range(d):
                    entry = 1 if i == j else 0
                    if half[i][j]:
                        entry ^= 0b10  # x
                    row.append(entry)
                matrix.append(tuple(row))
            require(leibniz_det(tuple(matrix)) == poly_pow(0b11, rank(half)), "det(I+xA) left the rank formula")
        low = poly_pow(0b11, d)
        high = poly_pow(0b11, 3 * d)
        require(low != high, "determinant degrees collapsed")
        require(high != poly_mul(low, low), "a squared low degree was treated as the three-stage determinant")
        cases += 1
    # The same polynomial inequality at the port counts named by the open profiles.
    for d in (2, 4, 16, 52):
        require(poly_pow(0b11, 3 * d) != poly_pow(0b11, d), "degree gap failed")
    return cases


def check_b_cancellation():
    """The summed core+leaf row of [P, M] equals A(M_core + M_leaf), with B present."""
    checked = 0
    for q in (1, 2):
        d = 2 * q
        g = 3
        a, b, _complement = legal_pair(q, use_b=True)
        proj = stage_matrix(local_p(a, b), 0, g, d)
        read = stage_matrix(local_r(a), 0, g, d)
        require(mat_mul(proj, proj) == proj, "P is not a projector")
        require(mat_mul(proj, read) == read and mat_mul(read, proj) == read, "R is not fixed by P")
        other = stage_matrix(local_p(a, b), 1, g, d)
        require(mat_mul(proj, other) != mat_mul(other, proj), "nonzero B still commuted across stages")
        matrices = (
            probe_matrix((g + 1) * d, 1),
            probe_matrix((g + 1) * d, 2),
            thin_k(g, d),
            stage_t(1, g, d),
            stage_t(2, g, d),
        )
        for m_mat in matrices:
            for leaf in (1, 2):
                got = summed_commutator_block(proj, m_mat, 0, leaf, d)
                expect = predicted_block(a, m_mat, 0, leaf, d)
                require(got == expect, "B failed to cancel in the summed commutator")
                checked += 1
        # On K the predicted block is A itself, for every foreign leaf.
        k_mat = thin_k(g, d)
        for leaf in (1, 2):
            require(predicted_block(a, k_mat, 0, leaf, d) == a, "K did not contribute A on every leaf")
    zero_b = zeros(2)
    a = diag_idempotent(1)
    require(mat_add(mat_mul(a, zero_b), mat_mul(zero_b, a)) == zero_b, "zero B broke the legal relation")
    bad = eye(2)
    require(mat_add(mat_mul(a, bad), mat_mul(bad, a)) != bad, "illegal B was accepted")
    return checked


def check_telescope():
    """If AS = 0 then (I+xA)(I+xS) = I+x(A+S). Three full stages do not have det (1+x)^d."""
    a = ((1, 0), (0, 0))
    s = ((0, 0), (0, 1))
    require(mat_mul(a, s) == zeros(2), "telescope hypothesis AS=0 was not met")
    ax = ((0b11, 0), (0, 1))  # I+xA
    sx = ((1, 0), (0, 0b11))  # I+xS
    got = tuple(tuple(poly_mul(ax[i][0], sx[0][j]) ^ poly_mul(ax[i][1], sx[1][j]) for j in range(2)) for i in range(2))
    # I + x(A+S) = diag(1+x, 1+x)
    expect = ((0b11, 0), (0, 0b11))
    require(got == expect, "telescope identity failed")
    # One stage of complementary halves multiplies to (1+x)I.
    # Three copies multiply to (1+x)^3 I, which is not (1+x)I.
    one = 0b11
    three = poly_pow(one, 3)
    require(three == 0b1111, "(1+x)^3 left 1+x+x^2+x^3")
    require(three != one, "three stages collapsed to one stage")
    return True


def check_words():
    results = {}
    for use_b in (False, True):
        for g, q in ((2, 1), (3, 1), (3, 2)):
            got = sharp_word(g, q, use_b)
            expect = target_word(g, 2 * q)
            require(got == expect, "sharp word missed the endpoint at g=%d q=%d b=%s" % (g, q, use_b))
        # Deleting one thin map from the g=3 word misses the endpoint.
        d = 2
        g = 3
        a, b, complement = legal_pair(1, use_b)
        factors = []
        for stage in range(g):
            for half in (a, complement):
                proj = stage_matrix(local_p(half, b), stage, g, d)
                read = stage_matrix(local_r(half), stage, g, d)
                factors.append(full_factor(stage, proj, read, g))
            if stage % 2 == 0:
                factors.append(
                    thin_factor(sharp_thin(stage, g, d, core_identity=False), g)
                )
        # Drop the first thin factor. It sits after the two calls of stage 0.
        dropped = factors[:2] + factors[3:]
        word = {(0, (0, 0, 0)): eye(8)}
        for factor in dropped:
            word = poly_matmul(factor, word)
        require(word != target_word(3, 2), "deleting a thin map still met the endpoint")
    # One forced map K fails on the adjacent schedule, in every gap, and on
    # one interleaved schedule. These are controls for the forced matrix, not
    # a census.
    failures = 0
    k_mat = thin_k(3, 2)
    order = adjacent_order(3)
    for gap in range(7):
        for use_b in (False, True):
            got = one_map_word(3, 1, use_b, order, gap, k_mat)
            require(got != target_word(3, 2), "adjacent one-map word met the endpoint")
            failures += 1
    interleaved = ((0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (2, 1))
    for use_b in (False, True):
        got = one_map_word(3, 1, use_b, interleaved, 3, k_mat)
        require(got != target_word(3, 2), "interleaved one-map word met the endpoint")
        failures += 1
    # q=2, one adjacent gap and one interleaved gap, nonzero B.
    k4 = thin_k(3, 4)
    got = one_map_word(3, 2, True, adjacent_order(3), 2, k4)
    require(got != target_word(3, 4), "q=2 adjacent one-map word met the endpoint")
    got = one_map_word(3, 2, True, interleaved, 4, k4)
    require(got != target_word(3, 4), "q=2 interleaved one-map word met the endpoint")
    failures += 2
    # At D=(1,1,1) the forced K matches the e coefficient for an adjacent word,
    # and a zero map does not. The polynomial identity still fails, which the
    # comparisons above already required.
    point = evaluate(one_map_word(3, 1, True, order, 0, k_mat), (1, 1, 1))
    require(point == evaluate(target_word(3, 2), (1, 1, 1)), "K missed the D=1 point")
    zero_point = evaluate(one_map_word(3, 1, True, order, 0, zeros(8)), (1, 1, 1))
    require(zero_point != evaluate(target_word(3, 2), (1, 1, 1)), "the zero map survived D=1")
    results["one_map_controls"] = failures
    results["sharp_pairs"] = 6
    return results


def evaluate(word, values):
    """Evaluate a word at 0-1 points. A positive degree vanishes at 0 and is 1 at 1."""
    n = len(next(iter(word.values())))
    pure = zeros(n)
    deriv = zeros(n)
    for (flag, degrees), matrix in word.items():
        coeff = 1
        for degree, value in zip(degrees, values):
            if degree and value == 0:
                coeff = 0
                break
        if coeff == 0:
            continue
        if flag:
            deriv = mat_add(deriv, matrix)
        else:
            pure = mat_add(pure, matrix)
    return pure, deriv


def main():
    check_selected_record()
    k_cases = check_k_shape()
    det_cases = check_determinant_gap()
    commutators = check_b_cancellation()
    check_telescope()
    words = check_words()
    # g=2 is the positive control that one map can succeed when there are not
    # three leaves. sharp_word already required that equality.
    require(words["sharp_pairs"] == 6, "sharp-word count drifted")
    print(
        "PASS_PAIRED_STAR_ONE_THIN_EVERY_Q"
        " k_shapes=%d det_pairs=%d commutator_blocks=%d one_map_controls=%d"
        % (k_cases, det_cases, commutators, words["one_map_controls"])
    )
    print("evidence_class=proof kappa=781451/250000000")


if __name__ == "__main__":
    main()
