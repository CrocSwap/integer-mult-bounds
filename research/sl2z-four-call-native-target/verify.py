#!/usr/bin/env python3
"""Verify the exact four-call SL2(Z) shear target and its scoped minimum."""

from itertools import product


IDENTITY = (1, 0, 0, 1)
X = (1, 1, 0, 1)
XI = (1, -1, 0, 1)
Y = (1, 0, 1, 1)
YI = (1, 0, -1, 1)
ALPHABET = (X, XI, Y, YI)
EXPECTED = (5, 2, 2, 1)
P = ((1, 0), (0, 0))


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def mul(a, b):
    a00, a01, a10, a11 = a
    b00, b01, b10, b11 = b
    return (
        a00 * b00 + a01 * b10,
        a00 * b01 + a01 * b11,
        a10 * b00 + a11 * b10,
        a10 * b01 + a11 * b11,
    )


def det(a):
    return a[0] * a[3] - a[1] * a[2]


def scalar_product(a, b):
    return tuple(
        tuple(sum(a[i][k] * b[k][j] for k in range(2)) % 2 for j in range(2))
        for i in range(2)
    )


def word_product(word):
    out = IDENTITY
    for label in word:
        out = mul(out, label)
    return out


def xor_term(dst, key, bit):
    value = dst.get(key, 0) ^ bit
    if value:
        dst[key] = value
    else:
        dst.pop(key, None)


def matrix_product(a, b):
    out = [[{}, {}], [{}, {}]]
    for i in range(2):
        for k in range(2):
            for j in range(2):
                for g, coefficient_a in a[i][k].items():
                    for h, coefficient_b in b[k][j].items():
                        key = mul(g, h)
                        xor_term(out[i][j], key, coefficient_a & coefficient_b)
    return out


def paid_factor(g, n):
    """Build I + ([g] + [e]) N over F2[G]."""
    out = [[{IDENTITY: 1}, {}], [{}, {IDENTITY: 1}]]
    for i in range(2):
        for j in range(2):
            if n[i][j]:
                xor_term(out[i][j], IDENTITY, 1)
                xor_term(out[i][j], g, 1)
    return out


def target_matrix(g):
    return [
        [{g: 1}, {}],
        [{}, {IDENTITY: 1}],
    ]


def all_short_words():
    words = []
    for length in range(4):
        words.extend(product(ALPHABET, repeat=length))
    return words


def main():
    need(mul(X, XI) == IDENTITY and mul(XI, X) == IDENTITY, "X inverse mismatch")
    need(mul(Y, YI) == IDENTITY and mul(YI, Y) == IDENTITY, "Y inverse mismatch")
    need(det(X) == det(XI) == det(Y) == det(YI) == 1, "a label is not unimodular")
    for label in ALPHABET:
        difference = (
            label[0] - IDENTITY[0],
            label[1] - IDENTITY[1],
            label[2] - IDENTITY[2],
            label[3] - IDENTITY[3],
        )
        need(difference != (0, 0, 0, 0), "zero label difference")
        need(det(difference) == 0, "label difference is not rank one")
    need(mul(X, Y) != mul(Y, X), "the address group did not test noncommutativity")
    need(scalar_product(P, P) == P, "chosen register frame is not idempotent")
    need(sum(sum(row) for row in P) == 1 and det((P[0][0], P[0][1], P[1][0], P[1][1])) == 0,
         "chosen register frame is not rank one")

    b = mul(mul(X, X), mul(Y, Y))
    need(b == EXPECTED, "target matrix mismatch")
    difference = tuple(b[i] - IDENTITY[i] for i in range(4))
    need(det(b) == 1 and det(difference) == -4, "target rank/determinant mismatch")

    shorter = all_short_words()
    need(len(shorter) == 85, "wrong bounded word count")
    need(all(word_product(word) != b for word in shorter), "target occurs at length at most three")
    radius3 = {word_product(word) for word in shorter}
    need(b not in radius3, "target entered the radius-three word ball")

    factors = [paid_factor(g, P) for g in (X, X, Y, Y)]
    result = factors[0]
    for factor in factors[1:]:
        result = matrix_product(result, factor)
    expected = target_matrix(b)
    need(result == expected, "full group-algebra endpoint mismatch")

    for omitted in range(4):
        damaged = [factor for index, factor in enumerate(factors) if index != omitted]
        value = damaged[0]
        for factor in damaged[1:]:
            value = matrix_product(value, factor)
        need(value != expected, "omitted-call control was accepted")
    wrong_middle = [paid_factor(g, P) for g in (X, X, YI, Y)]
    value = wrong_middle[0]
    for factor in wrong_middle[1:]:
        value = matrix_product(value, factor)
    need(value != expected, "wrong-label control was accepted")
    wrong_role = [paid_factor(g, P) for g in (Y, Y, X, X)]
    value = wrong_role[0]
    for factor in wrong_role[1:]:
        value = matrix_product(value, factor)
    need(value != expected, "reversed target control was accepted")

    print(
        "PASS_SL2Z_FOUR_CALL_TARGET "
        "alphabet=4 roles=2 calls=4 shorter_words=85 "
        f"distinct_radius3={len(radius3)} rank1_labels=4 "
        "restoration_calls=0 omitted_controls=4 wrong_label=1 wrong_order=1 "
        "no_new_kappa"
    )


if __name__ == "__main__":
    main()
