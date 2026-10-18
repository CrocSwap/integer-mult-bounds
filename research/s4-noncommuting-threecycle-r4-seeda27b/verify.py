#!/usr/bin/env python3
"""Exact radius-three search in the declared F2[S4], four-role alphabet."""

from functools import lru_cache
from hashlib import sha256
from itertools import permutations


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL_S4_NONCOMMUTING_R4: " + message)


R = 4
PERMS = tuple(permutations(range(4)))
PERM_INDEX = {p: i for i, p in enumerate(PERMS)}
GROUP_MUL = tuple(
    tuple(PERM_INDEX[tuple(p[q[k]] for k in range(4))] for q in PERMS)
    for p in PERMS
)
E_PERM = PERM_INDEX[(0, 1, 2, 3)]
E = 1 << E_PERM


def permutation(images):
    return PERM_INDEX[tuple(images)]


S1 = permutation((1, 0, 2, 3))  # (12)
S2 = permutation((0, 2, 1, 3))  # (23)
S3 = permutation((0, 1, 3, 2))  # (34)
LABELS = (S1, S2, S3)
G1 = GROUP_MUL[S1][S2]
G2 = GROUP_MUL[S2][S3]
G1_WORDS = (G1, (S1, S2))
G1_INVERSE_WORDS = (GROUP_MUL[S2][S1], (S2, S1))
G2_WORDS = (G2, (S2, S3))
G2_INVERSE_WORDS = (GROUP_MUL[S3][S2], (S3, S2))
TWO_LETTER_CYCLES = (
    G1_WORDS, G1_INVERSE_WORDS, G2_WORDS, G2_INVERSE_WORDS,
)


@lru_cache(maxsize=None)
def group_algebra_product(left, right):
    """Multiply two F2[S4] elements encoded as 24-bit coefficient masks."""
    answer = 0
    a = left
    while a:
        bit_a = a & -a
        a ^= bit_a
        i = bit_a.bit_length() - 1
        b = right
        while b:
            bit_b = b & -b
            b ^= bit_b
            j = bit_b.bit_length() - 1
            answer ^= 1 << GROUP_MUL[i][j]
    return answer


IDENTITY = tuple(
    E if i == j else 0 for i in range(R) for j in range(R)
)


def matrix_product(left, right):
    """Multiply 4 by 4 matrices over the noncommutative group algebra."""
    result = []
    for i in range(R):
        for j in range(R):
            value = 0
            for k in range(R):
                value ^= group_algebra_product(left[R * i + k], right[R * k + j])
            result.append(value)
    return tuple(result)


def rank_one_idempotents():
    """Return xy^T over F2 for all nonzero x,y with y^T x=1."""
    rows = []
    for x in range(1, 1 << R):
        for y in range(1, 1 << R):
            if (x & y).bit_count() & 1:
                rows.append(tuple(
                    int(bool((x >> i) & 1) and bool((y >> j) & 1))
                    for i in range(R) for j in range(R)
                ))
    return tuple(rows)


IDEMPOTENTS = rank_one_idempotents()


def paid_factor(label, idempotent):
    """Return I+([s]+[e])N over F2[S4]."""
    delta = E ^ (1 << label)
    return tuple(
        IDENTITY[index] ^ (delta if idempotent[index] else 0)
        for index in range(R * R)
    )


FACTOR_LABELS = tuple((label, n) for label in LABELS for n in IDEMPOTENTS)
FACTORS = tuple(paid_factor(label, n) for label, n in FACTOR_LABELS)
FACTOR_INDEX = {label: i for i, label in enumerate(FACTOR_LABELS)}


def diagonal(entries):
    return tuple(
        entries[i] if i == j else 0
        for i in range(R) for j in range(R)
    )


TARGETS = tuple(
    (a, b, diagonal((1 << a, 1 << b, E, E)), word_a, word_b)
    for a, word_a in TWO_LETTER_CYCLES
    for b, word_b in TWO_LETTER_CYCLES
    if a != b and GROUP_MUL[a][b] != GROUP_MUL[b][a]
)


def word_product(indices):
    result = IDENTITY
    for index in indices:
        result = matrix_product(result, FACTORS[index])
    return result


def encoded_state(matrix):
    """Canonical 48-byte encoding: row-major, 3-byte big-endian entries."""
    return b"".join(value.to_bytes(3, "big") for value in matrix)


def main():
    require(len(PERMS) == 24 and len(IDEMPOTENTS) == 120,
            "S4 basis or rank-one idempotent count changed")
    require(len(FACTORS) == 360, "paid generator count changed")
    require(len(TARGETS) == 8,
            "ordered noncommuting two-letter cycle family changed")
    require(GROUP_MUL[E_PERM][S1] == S1 and GROUP_MUL[S1][E_PERM] == S1,
            "permutation identity control failed")
    require(GROUP_MUL[G1][G2] != GROUP_MUL[G2][G1],
            "declared target 3-cycles unexpectedly commute")
    require(all(matrix_product(factor, factor) == IDENTITY for factor in FACTORS),
            "a paid factor is not involutive")

    # Diagonal idempotents place the two cycle words in roles zero and one.
    e00 = tuple(int(i == 0 and j == 0) for i in range(R) for j in range(R))
    e11 = tuple(int(i == 1 and j == 1) for i in range(R) for j in range(R))
    # Positive control: one paid factor realizes diag([s1],[e],[e],[e]).
    one_call_target = diagonal((1 << S1, E, E, E))
    require(FACTORS[FACTOR_INDEX[(S1, e00)]] == one_call_target,
            "one-call positive control failed")

    # Every ordered noncommuting pair of two-letter 3-cycles has a direct
    # four-call word, and every single-call deletion from that word fails.
    target_matrices = []
    for a, b, target, word_a, word_b in TARGETS:
        direct = tuple(FACTOR_INDEX[(label, e00)] for label in word_a)
        direct += tuple(FACTOR_INDEX[(label, e11)] for label in word_b)
        require(word_product(direct) == target,
                "four-call direct construction failed for a target pair")
        for omitted in range(4):
            shorter = direct[:omitted] + direct[omitted + 1:]
            require(word_product(shorter) != target,
                    "one-call omission unexpectedly preserved a target")
        target_matrices.append(target)

    # An altered second target catches a mistaken cycle or coordinate label.
    altered_target = diagonal((1 << G1, 1 << G1, E, E))
    require(word_product((
        FACTOR_INDEX[(S1, e00)], FACTOR_INDEX[(S2, e00)],
        FACTOR_INDEX[(S2, e11)], FACTOR_INDEX[(S3, e11)],
    )) != altered_target, "target mutation control failed")

    # Complete radius-two ball: every ordered pair, including repeats.
    pair_products = set()
    for left in FACTORS:
        for right in FACTORS:
            pair_products.add(matrix_product(left, right))
    require(len(pair_products) == 87016,
            "ordered-pair state count changed")
    pair_digest = sha256(b"".join(sorted(encoded_state(state) for state in pair_products))).hexdigest()
    require(pair_digest == "cc18ab4f9e58731f43f42ed0fd791531696836385f9435c6328cbbe36651f2f7",
            "deterministic complete pair-state digest changed: " + pair_digest)

    total_right_meet_misses = 0
    for target in target_matrices:
        require(target not in pair_products,
                "a target has a zero-, one-, or two-call representation")
        require(target not in FACTORS,
                "a target has a one-call representation")

        # If T=A*B*C and C^2=I, then T*C=A*B. Check all C and all targets.
        for last in FACTORS:
            require(matrix_product(target, last) not in pair_products,
                    "a three-call word exists in the complete meet")
            total_right_meet_misses += 1
    require(total_right_meet_misses == 2880,
            "the complete target-side meet count changed")

    print(
        "PASS_S4_NONCOMMUTING_R4 "
        "rank_one_idempotents=120 factors=360 ordered_pairs=129600 "
        f"pair_states={len(pair_products)} target_pairs={len(target_matrices)} "
        f"radius3_misses={total_right_meet_misses} pair_sha256={pair_digest} direct_calls=4"
    )


if __name__ == "__main__":
    main()
