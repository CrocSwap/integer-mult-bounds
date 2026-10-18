#!/usr/bin/env python3
"""Exact finite search for the four-role mixed-target D8 word."""
def require(condition, message):
    if not condition:
        raise AssertionError(message)


def group_data():
    # a=(0 1)(2 3), b=(1 2); their product has order four.
    a = (1, 0, 3, 2)
    b = (0, 2, 1, 3)

    def compose(x, y):
        return tuple(x[y[i]] for i in range(4))

    identity = tuple(range(4))
    group = {identity, a, b}
    changed = True
    while changed:
        changed = False
        for x in tuple(group):
            for y in tuple(group):
                z = compose(x, y)
                if z not in group:
                    group.add(z)
                    changed = True
    ordered = sorted(group)
    index = {g: i for i, g in enumerate(ordered)}
    table = [[index[compose(x, y)] for y in ordered] for x in ordered]
    ai, bi, ei = index[a], index[b], index[identity]
    abi, bai = table[ai][bi], table[bi][ai]
    require(len(ordered) == 8, "the generated subgroup is not order eight")
    require(table[ai][ai] == ei and table[bi][bi] == ei, "generators are not involutions")
    p = ei
    square = table[abi][abi]
    require(square != ei, "ab does not have order four")
    for _ in range(4):
        p = table[abi][p]
    require(p == ei and table[abi][ei] != ei, "ab does not have order four")
    require(abi != bai, "ab and ba unexpectedly commute")
    return ordered, table, ai, bi, abi, bai, ei


def algebra_product_table(group_table, order):
    size = 1 << order
    table = [[0] * size for _ in range(size)]
    for x in range(size):
        xb = [i for i in range(order) if (x >> i) & 1]
        for y in range(size):
            out = 0
            for i in xb:
                for j in range(order):
                    if (y >> j) & 1:
                        out ^= 1 << group_table[i][j]
            table[x][y] = out
    return table


def main():
    group, product, a, b, ab, ba, e = group_data()
    algebra = algebra_product_table(product, len(group))

    def identity_matrix():
        return tuple((1 << e) if row == col else 0
                     for row in range(4) for col in range(4))

    ident = identity_matrix()

    def multiply(left, right):
        out = [0] * 16
        for row in range(4):
            for col in range(4):
                value = 0
                for k in range(4):
                    value ^= algebra[left[4 * row + k]][right[4 * k + col]]
                out[4 * row + col] = value
        return tuple(out)

    # N=x y^T, with x,y nonzero and y^T x=1: exactly 120 idempotents.
    idempotents = []
    for x in range(1, 16):
        for y in range(1, 16):
            if (x & y).bit_count() % 2:
                idempotents.append(tuple(((x >> row) & 1) & ((y >> col) & 1)
                                         for row in range(4) for col in range(4)))
    require(len(idempotents) == 120, "rank-one idempotent count mismatch")

    def paid(label, n):
        delta = (1 << label) ^ (1 << e)
        return tuple(ident[q] ^ algebra[delta][n[q]] for q in range(16))

    factors = [paid(label, n) for label in (a, b) for n in idempotents]
    require(len(factors) == 240, "paid alphabet count mismatch")
    require(all(multiply(f, f) == ident for f in factors),
            "a paid factor is not an involution")

    def coordinate(k):
        return tuple(int(row == col == k) for row in range(4) for col in range(4))

    def diagonal(labels):
        return tuple((1 << labels[col]) if row == col else 0
                     for row in range(4) for col in range(4))

    target = diagonal((a, ab, ba, e))
    word = [paid(a, coordinate(0)), paid(a, coordinate(1)),
            paid(b, coordinate(1)), paid(b, coordinate(2)),
            paid(a, coordinate(2))]
    value = ident
    for factor in word:
        value = multiply(value, factor)
    require(value == target, "five-factor positive construction failed")

    # Order-sensitive and admissibility controls.
    wrong_middle = [paid(a, coordinate(0)), paid(b, coordinate(1)),
                    paid(a, coordinate(1)), paid(b, coordinate(2)),
                    paid(a, coordinate(2))]
    value = ident
    for factor in wrong_middle:
        value = multiply(value, factor)
    require(value != target, "swapped ab/ba order control was missed")
    bad_n = tuple(int(row == 0 and col == 1) for row in range(4) for col in range(4))
    require(bad_n not in idempotents, "non-idempotent control entered the alphabet")
    bad_n_square = tuple(sum(bad_n[4 * row + k] * bad_n[4 * k + col]
                             for k in range(4)) % 2
                         for row in range(4) for col in range(4))
    require(bad_n_square != bad_n, "negative-control matrix is idempotent")
    require(any(multiply(paid(a, coordinate(k)), paid(a, coordinate(k))) == ident
                for k in range(4)), "involution control failed")
    for omitted in range(len(word)):
        shortened = ident
        for j, factor in enumerate(word):
            if j != omitted:
                shortened = multiply(shortened, factor)
        require(shortened != target, "drop-one-call control unexpectedly passes")

    # Every pair state retains one ordered factor pair as a witness.
    pairs = {}
    for i, left in enumerate(factors):
        for j, right in enumerate(factors):
            pairs.setdefault(multiply(left, right), (i, j))

    # Check every length 0, 1, 2, and 3 word.
    q0 = target == ident
    q1 = target in factors
    q2 = target in pairs
    q3 = any(multiply(first, target) in pairs for first in factors)

    # For a length-four word A B C D=T, put Q=C D. Since every paid
    # factor is self-inverse, A B must equal T Q^{-1}=T D C.
    q4 = None
    for q, (k, ell) in pairs.items():
        q_inverse = multiply(factors[ell], factors[k])
        left_pair = multiply(target, q_inverse)
        if left_pair in pairs:
            q4 = (pairs[left_pair], (k, ell))
            break

    require(not q0 and not q1 and not q2 and not q3 and q4 is None,
            "a word of at most four factors was found")
    print("PASS_D8_MIXED_TARGET min=5 roles=4 group_order=8 generators=2 "
          f"idempotents={len(idempotents)} factors={len(factors)} "
          f"pair_states={len(pairs)} words_le4=0 controls=7 no_new_kappa")


if __name__ == "__main__":
    main()
