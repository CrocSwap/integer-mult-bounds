#!/usr/bin/env python3
"""Check the consecutive paired-star rank obstruction at g=31, q=26.

The argument is a proof under the hypotheses in PROOF.md. It is not a search
over words, not a finite census of the profile, and not a heuristic. The
g=3 F2 censuses are not inputs and are not re-run.
"""

from __future__ import annotations

import sys

G = 31
Q = 26
MAPS = 5


def add(*args):
    out = {}
    for item in args:
        for key, value in item.items():
            if value:
                out[key] = out.get(key, 0) ^ 1
    return {key: value for key, value in out.items() if value}


def reduce_word(word, use_ba):
    counts = {}

    def rec(seq, depth=0):
        if depth > 80:
            raise RuntimeError("reduction depth exceeded")
        text = "".join(seq)
        if "AA" in text:
            index = text.index("AA")
            rec(seq[:index] + ["A"] + seq[index + 2 :], depth + 1)
            return
        if use_ba and "BA" in text:
            index = text.index("BA")
            rec(seq[:index] + ["B"] + seq[index + 2 :], depth + 1)
            rec(seq[:index] + ["A", "B"] + seq[index + 2 :], depth + 1)
            return
        counts[text] = counts.get(text, 0) + 1

    rec(list(word))
    return {key: value % 2 for key, value in counts.items() if value % 2}


def multiply(left, right, use_ba):
    out = {}
    for left_word, left_value in left.items():
        if not left_value:
            continue
        for right_word, right_value in right.items():
            if not right_value:
                continue
            for word, coeff in reduce_word(left_word + right_word, use_ba).items():
                if coeff:
                    out[word] = out.get(word, 0) ^ 1
    return {key: value for key, value in out.items() if value}


def matrix_multiply(left, right, use_ba):
    size = len(left)
    return [
        [
            add(
                *[
                    multiply(left[row][mid], right[mid][col], use_ba)
                    for mid in range(size)
                ]
            )
            for col in range(size)
        ]
        for row in range(size)
    ]


def matrix_add(*matrices):
    size = len(matrices[0])
    return [
        [add(*[matrix[row][col] for matrix in matrices]) for col in range(size)]
        for row in range(size)
    ]


def zero_matrix():
    return [[{}, {}], [{}, {}]]


def local_identities(use_ba):
    """Both half orders multiply to the scalar stage factor iff the relations hold."""
    one = {"": 1}
    a = {"A": 1}
    b = {"B": 1}
    projector = [[add(a, b), b], [b, add(a, b)]]
    image = [[a, a], [a, a]]
    complement = [[add(one, a, b), b], [b, add(one, a, b)]]
    complement_image = [[add(one, a), add(one, a)], [add(one, a), add(one, a)]]
    identity = [[one, {}], [{}, one]]
    support = [[one, one], [one, one]]

    def pure_ok(first, second):
        total = matrix_add(first, second)
        square = matrix_multiply(first, second, use_ba)
        return total == identity and square == zero_matrix()

    def e_parts(left_p, left_r, right_p, right_r):
        degree0 = matrix_add(left_r, right_r)
        degree1 = matrix_add(
            left_r,
            matrix_multiply(left_r, right_p, use_ba),
            right_r,
            matrix_multiply(left_p, right_r, use_ba),
        )
        degree2 = matrix_add(
            matrix_multiply(left_r, right_p, use_ba),
            matrix_multiply(left_p, right_r, use_ba),
        )
        return degree0, degree1, degree2

    relation = add(reduce_word("BA", use_ba), reduce_word("AB", use_ba), {"B": 1})
    projector_square = matrix_multiply(projector, projector, use_ba)
    forward = e_parts(complement, complement_image, projector, image)
    reverse = e_parts(projector, image, complement, complement_image)
    expected = (support, support, zero_matrix())
    return (
        relation == {}
        and projector_square == projector
        and pure_ok(projector, complement)
        and pure_ok(complement, projector)
        and forward == expected
        and reverse == expected
    )


def empty(size):
    return [[None] * size for _ in range(size)]


def identity_monomials(size):
    matrix = empty(size)
    for index in range(size):
        matrix[index][index] = 0
    return matrix


def combine_monomial(left, right):
    if left & right:
        raise AssertionError("stage variables are not square-free")
    return left | right


def multiply_monomials(left, right):
    size = len(left)
    out = empty(size)
    for row in range(size):
        for mid in range(size):
            if left[row][mid] is None:
                continue
            for col in range(size):
                if right[mid][col] is None:
                    continue
                prod = combine_monomial(left[row][mid], right[mid][col])
                current = out[row][col]
                if current is None:
                    out[row][col] = prod
                elif current == prod:
                    out[row][col] = None
                else:
                    raise AssertionError("two distinct monomials landed in one entry")
    return out


def add_monomials(left, right):
    size = len(left)
    out = empty(size)
    for row in range(size):
        for col in range(size):
            x, y = left[row][col], right[row][col]
            if x is None:
                out[row][col] = y
            elif y is None:
                out[row][col] = x
            elif x == y:
                out[row][col] = None
            else:
                raise AssertionError("char-2 sum of distinct monomials")
    return out


def stage_factor(leaves, stage):
    size = leaves + 1
    pure = identity_monomials(size)
    variable = 1 << stage
    pure[0][0] = variable
    pure[stage + 1][stage + 1] = variable
    coefficient = empty(size)
    coefficient[0][0] = variable
    coefficient[0][stage + 1] = variable
    coefficient[stage + 1][0] = variable
    coefficient[stage + 1][stage + 1] = variable
    return pure, coefficient


def full_calls(leaves):
    size = leaves + 1
    pure = identity_monomials(size)
    coefficient = empty(size)
    for stage in range(leaves):
        factor, extra = stage_factor(leaves, stage)
        coefficient = add_monomials(
            multiply_monomials(factor, coefficient),
            multiply_monomials(extra, pure),
        )
        pure = multiply_monomials(factor, pure)
    return pure, coefficient


def required_monomial(leaves, stage):
    return ((1 << leaves) - 1) ^ ((1 << stage) - 1)


def gap_monomial(leaves, gap, stage):
    mask = 0
    for later in range(gap, leaves):
        mask |= 1 << later
    if stage < gap:
        mask |= 1 << stage
    return mask


def thin_contribution(leaves, gap, stage):
    """Core-to-leaf block from a constant identity block placed at this gap."""
    size = leaves + 1
    pure = identity_monomials(size)
    coefficient = empty(size)

    def place():
        nonlocal coefficient, pure
        update = empty(size)
        update[0][stage + 1] = 0
        coefficient = add_monomials(coefficient, multiply_monomials(update, pure))

    if gap == 0:
        place()
    for index in range(leaves):
        factor, _extra = stage_factor(leaves, index)
        coefficient = multiply_monomials(factor, coefficient)
        pure = multiply_monomials(factor, pure)
        if gap == index + 1:
            place()
    return coefficient[0][stage + 1]


def check_scalar_schedule(leaves):
    pure, coefficient = full_calls(leaves)
    all_variables = (1 << leaves) - 1
    if pure[0][0] != all_variables:
        raise AssertionError("core pure product")
    if leaves % 2 == 1:
        if coefficient[0][0] != all_variables:
            raise AssertionError("odd core diagonal")
    elif coefficient[0][0] is not None:
        raise AssertionError("even core diagonal")
    seen = {}
    for stage in range(leaves):
        monomial = required_monomial(leaves, stage)
        if pure[stage + 1][stage + 1] != (1 << stage):
            raise AssertionError("leaf pure factor")
        if pure[0][stage + 1] is not None or pure[stage + 1][0] is not None:
            raise AssertionError("pure product is not diagonal")
        if coefficient[0][stage + 1] != monomial:
            raise AssertionError("full-call core-leaf monomial")
        if coefficient[stage + 1][stage + 1] != (1 << stage):
            raise AssertionError("leaf diagonal")
        if coefficient[stage + 1][0] != (1 << (stage + 1)) - 1:
            raise AssertionError("leaf-core monomial")
        matches = []
        for gap in range(leaves + 1):
            got = thin_contribution(leaves, gap, stage)
            expect = gap_monomial(leaves, gap, stage)
            if got != expect:
                raise AssertionError((leaves, gap, stage, got, expect))
            seen.setdefault((stage, got), []).append(gap)
            if got == monomial:
                matches.append(gap)
        if matches != [stage, stage + 1]:
            raise AssertionError(("cover", stage, matches))
        for (owner, mask), gaps in seen.items():
            if owner == stage and mask != monomial and len(gaps) != 1:
                raise AssertionError(("private monomial repeated", stage, mask, gaps))
    for row in range(1, leaves + 1):
        for col in range(1, leaves + 1):
            if row != col and coefficient[row][col] is not None:
                raise AssertionError("leaf-leaf full-call entry")


def counting_identity(leaves):
    """Every basis vector proves the double count used by the rank sum."""
    for position in range(leaves + 1):
        ranks = [1 if index == position else 0 for index in range(leaves + 1)]
        leaf_sum = sum(ranks[stage] + ranks[stage + 1] for stage in range(leaves))
        weighted = ranks[0] + ranks[leaves] + 2 * sum(ranks[1:leaves])
        if leaf_sum != weighted:
            raise AssertionError("gap incidence count")
        if weighted > 2 * sum(ranks):
            raise AssertionError("incidence exceeds two per gap")


def gf2_rank(rows):
    matrix = [row[:] for row in rows]
    size = len(matrix)
    width = len(matrix[0])
    rank = 0
    used = set()
    for col in range(width):
        pivot = next(
            (row for row in range(size) if row not in used and matrix[row][col]),
            None,
        )
        if pivot is None:
            continue
        used.add(pivot)
        rank += 1
        for row in range(size):
            if row != pivot and matrix[row][col]:
                matrix[row] = [a ^ b for a, b in zip(matrix[row], matrix[pivot])]
    return rank


def check_rank_arithmetic():
    target = 2 * Q
    identity = [[1 if row == col else 0 for col in range(target)] for row in range(target)]
    if gf2_rank(identity) != target:
        raise AssertionError("identity rank")
    short = [[1 if row == col else 0 for col in range(target)] for row in range(Q)]
    short.extend([[0] * target for _ in range(Q)])
    if gf2_rank(short) != Q:
        raise AssertionError("rank-q fixture")
    lower = Q * G
    profile = MAPS * Q
    commuting = ((G + 1) // 2) * (4 * Q)
    if not profile < lower <= commuting:
        raise AssertionError((profile, lower, commuting))
    if Q + Q != target:
        raise AssertionError("two rank-q blocks do not add to the identity rank")
    if not Q < target:
        raise AssertionError("one rank-q block meets the identity rank")


def expect_false(name, fn):
    if fn():
        raise AssertionError("failure control did not fail: " + name)


def main():
    if not local_identities(True):
        raise SystemExit("local stage identities failed")
    expect_false("dropped BA relation", lambda: local_identities(False))
    for leaves in (1, 2, 3, 4, G):
        check_scalar_schedule(leaves)
        counting_identity(leaves)
    check_rank_arithmetic()
    # A corrupted cover predicate is not the proved adjacent pair.
    false_matches = [
        gap
        for gap in range(G + 1)
        if gap_monomial(G, gap, 0) == required_monomial(G, 0)
    ]
    if false_matches != [0, 1]:
        raise SystemExit("leaf 0 cover changed")
    if gap_monomial(G, 2, 0) == required_monomial(G, 0):
        raise SystemExit("a nonadjacent gap matched the required monomial")
    lower = Q * G
    profile = MAPS * Q
    print(
        "PASS_G31_Q26_CONSECUTIVE_RANK"
        f" proof g={G} q={Q} d={2 * Q} lower_total_rank={lower}"
        f" profile_total_rank={profile}"
    )
    print(
        "STATUS proof under consecutive halves and no internal thin map;"
        " not a census; not a heuristic; not unrestricted nonexistence"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
