#!/usr/bin/env python3
"""Exact checks for the scoped C4 root-lifting result.

The main four-register lower bound is proved by the augmentation-filtration
case split in README.md.  This script checks every finite matrix lemma used by
that split, the four-call witness, and an exhaustive three-register/two-call
pilot search.
"""

from itertools import product


def ident(n):
    return tuple(1 << i for i in range(n))


def add(a, b):
    return tuple(x ^ y for x, y in zip(a, b))


def rank(a, n):
    rows = list(a)
    r = 0
    for col in range(n):
        pivot = next((j for j in range(r, n) if (rows[j] >> col) & 1), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        for j in range(n):
            if j != r and ((rows[j] >> col) & 1):
                rows[j] ^= rows[r]
        r += 1
    return r


def mmul_f2(a, b, n):
    out = []
    for row in a:
        value = 0
        for k in range(n):
            if (row >> k) & 1:
                value ^= b[k]
        out.append(value)
    return tuple(out)


def rank_one_idempotents(n):
    out = []
    for x in range(1, 1 << n):
        for y in range(1, 1 << n):
            if (x & y).bit_count() & 1:
                out.append(tuple(y if ((x >> i) & 1) else 0 for i in range(n)))
    assert len(out) == len(set(out))
    assert all(rank(a, n) == 1 and mmul_f2(a, a, n) == a for a in out)
    return tuple(out)


def ring_mul(a, b):
    """Multiply coefficient masks in F2[C4], using exponents modulo four."""
    out = 0
    for i in range(4):
        if (a >> i) & 1:
            for j in range(4):
                if (b >> j) & 1:
                    out ^= 1 << ((i + j) % 4)
    return out


def identity_ring(n):
    return tuple(tuple(1 if i == j else 0 for j in range(n)) for i in range(n))


def mmul_ring(a, b, n):
    out = [[0] * n for _ in range(n)]
    for i in range(n):
        for k in range(n):
            if a[i][k]:
                for j in range(n):
                    out[i][j] ^= ring_mul(a[i][k], b[k][j])
    return tuple(tuple(row) for row in out)


def factor(exponent, projector, n):
    # I + ([g**exponent] + [e]) N in the group basis of C4.
    delta = (1 << exponent) ^ 1
    out = [list(row) for row in identity_ring(n)]
    for i in range(n):
        for j in range(n):
            if (projector[i] >> j) & 1:
                out[i][j] ^= delta
    return tuple(tuple(row) for row in out)


def target(n):
    # diag([g^2], ..., [g^2]) in the group basis of C4.
    return tuple(tuple((1 << 2) if i == j else 0 for j in range(n)) for i in range(n))


def pilot_three_registers():
    n = 3
    projectors = rank_one_idempotents(n)
    wanted = target(n)
    tested = 0
    hits = []
    for length in range(3):
        for labels in product((1, 2, 3), repeat=length):
            for word in product(projectors, repeat=length):
                value = identity_ring(n)
                for exponent, projector in zip(labels, word):
                    value = mmul_ring(value, factor(exponent, projector, n), n)
                tested += 1
                if value == wanted:
                    hits.append((labels, word))
    assert tested == 1 + 84 + 7056
    assert not hits

    # Positive control: one output really is the direct one-call target.
    e11 = (1, 0, 0)
    one_output = tuple(
        tuple((1 << 2) if (i == j == 0) else (1 if i == j else 0) for j in range(n))
        for i in range(n)
    )
    assert factor(2, e11, n) == one_output
    return 7056, len(projectors)


def check_four_register_obstruction():
    n = 4
    projectors = rank_one_idempotents(n)
    assert len(projectors) == 120
    zero = tuple(0 for _ in range(n))
    eye = ident(n)

    # For three epsilon-order-one terms, the epsilon coefficient can vanish
    # only if N1 + N2 = N3. Check the finite rank-one/idempotent obstruction
    # for every ordered pair.
    rank_one_pair_sums = 0
    pair_sums = set()
    for a in projectors:
        for b in projectors:
            s = add(a, b)
            pair_sums.add(s)
            if rank(s, n) == 1:
                rank_one_pair_sums += 1
                assert mmul_f2(s, s, n) != s
    projector_set = set(projectors)
    assert not (pair_sums & projector_set)

    # The epsilon^2 coefficient cannot be I when it is a sum of at most three
    # rank-one matrices. These set checks exhaust those sums exactly.
    assert eye not in set(projectors)
    assert eye not in pair_sums
    assert all(add(eye, a) not in pair_sums for a in projectors)

    # I + N has rank three for every rank-one idempotent N. This rules out the
    # remaining two-odd-factor coefficient cases cN + M = I.
    for a in projectors:
        assert rank(add(eye, a), n) == 3

    # Enumerate all active label patterns through length three. The algebraic
    # cases in README.md are: zero odd labels -> at most three N's sum to I;
    # one odd label -> nonzero epsilon coefficient; two odd labels -> equal
    # projectors, then cN or cN+M cannot be I; three odd labels -> an
    # impossible sum of three idempotents equal to zero.
    patterns = 0
    for length in range(1, 4):
        for labels in product((1, 2, 3), repeat=length):
            patterns += 1
            odd = [s for s in labels if s in (1, 3)]
            if len(odd) == 0:
                if length == 1:
                    assert eye not in projector_set
                elif length == 2:
                    assert eye not in pair_sums
                else:
                    assert all(add(eye, a) not in pair_sums for a in projectors)
            elif len(odd) == 1:
                assert all(a != zero for a in projectors)
            elif len(odd) == 2:
                e3_count = sum(s == 3 for s in odd)
                c = (1 + e3_count) & 1  # pair product plus epsilon^2 terms
                if length == 2:
                    assert not c or eye not in set(projectors)
                else:
                    assert len(labels) == 3 and labels.count(2) == 1
                    if c == 0:
                        assert eye not in set(projectors)
                    else:
                        assert all(add(a, b) != eye for a in projectors for b in projectors)
            else:
                assert len(odd) == 3
                assert not (pair_sums & projector_set)
    assert patterns == 3 + 9 + 27

    # Four-call upper witness: four disjoint coordinate idempotents at g^2.
    direct = identity_ring(n)
    for i in range(n):
        eii = tuple((1 << i) if row == i else 0 for row in range(n))
        direct = mmul_ring(direct, factor(2, eii, n), n)
    assert direct == target(n)

    # Removing one direct call changes one diagonal entry.
    short = identity_ring(n)
    for i in range(1, n):
        eii = tuple((1 << i) if row == i else 0 for row in range(n))
        short = mmul_ring(short, factor(2, eii, n), n)
    assert short != target(n)

    # If rank-one is relaxed, the one-call factor with N=I produces the target.
    # This is the negative control for the operation-rank hypothesis.
    assert rank(eye, n) == n
    assert factor(2, eye, n) == target(n)
    return len(projectors), len(pair_sums), rank_one_pair_sums, patterns


def main():
    # C4 law and its augmentation coordinates: eps = [g]+1, eps^4 = 0.
    assert ring_mul(1 << 3, 1 << 1) == 1
    eps = (1 << 1) ^ 1
    eps2 = ring_mul(eps, eps)
    eps3 = ring_mul(eps2, eps)
    assert eps2 == ((1 << 2) ^ 1)
    assert ring_mul(eps3, eps) == 0
    assert ((1 << 3) ^ 1) == eps ^ eps2 ^ eps3

    pair_words, pilot_projectors = pilot_three_registers()
    projectors, pair_sums, rank_one_pair_sums, patterns = check_four_register_obstruction()
    print(
        "PASS_C4_ROOT_LIFT_OBSTRUCTION "
        f"n=4 labels=3 rank_one_idempotents={projectors} "
        f"label_patterns={patterns} pair_sums={pair_sums} "
        f"rank_one_pair_sums={rank_one_pair_sums} "
        f"pilot_n3_pair_words={pair_words}/{pilot_projectors**2 * 9} "
        "minimum_calls=4 kappa=none"
    )


if __name__ == "__main__":
    main()
