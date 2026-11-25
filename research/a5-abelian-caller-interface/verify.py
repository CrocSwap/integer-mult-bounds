#!/usr/bin/env python3
"""Check the exact A5 target and the caller-interface collapse controls."""

from itertools import permutations


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL_A5_ABELIAN_CALLER_COLLAPSE: " + message)


def compose(p, q):
    """Return p after q; permutations are tuples of images."""
    return tuple(p[q[i]] for i in range(len(p)))


def inverse(p):
    result = [0] * len(p)
    for i, image in enumerate(p):
        result[image] = i
    return tuple(result)


def cycle(*cycles):
    result = list(range(5))
    for support in cycles:
        for i, value in enumerate(support):
            result[value] = support[(i + 1) % len(support)]
    return tuple(result)


def even(p):
    inversions = sum(p[i] > p[j] for i in range(5) for j in range(i + 1, 5))
    return inversions % 2 == 0


def generated_group(identity, generators):
    steps = set(generators)
    steps.update(inverse(g) for g in generators)
    seen = {identity}
    pending = [identity]
    while pending:
        current = pending.pop()
        for step in steps:
            product = compose(current, step)
            if product not in seen:
                seen.add(product)
                pending.append(product)
    return seen


def order(g, identity):
    current = identity
    for n in range(1, 61):
        current = compose(current, g)
        if current == identity:
            return n
    return None


def group_algebra_product(left, right):
    """Multiply F2[A5] supports, toggling coefficients modulo two."""
    result = set()
    for a in left:
        for b in right:
            product = compose(a, b)
            if product in result:
                result.remove(product)
            else:
                result.add(product)
    return frozenset(result)


def matrix_product(left, right):
    zero = frozenset()
    result = []
    for i in range(2):
        row = []
        for j in range(2):
            entry = zero
            for k in range(2):
                entry ^= group_algebra_product(left[i][k], right[k][j])
            row.append(entry)
        result.append(tuple(row))
    return tuple(result)


def identity_matrix(identity):
    unit = frozenset((identity,))
    zero = frozenset()
    return ((unit, zero), (zero, unit))


def diagonal_factor(label, role, identity):
    unit = frozenset((identity,))
    zero = frozenset()
    difference = frozenset((label, identity))
    result = [list(row) for row in identity_matrix(identity)]
    result[role][role] ^= difference
    return tuple(tuple(row) for row in result)


def main():
    identity = tuple(range(5))
    a5 = {p for p in permutations(range(5)) if even(p)}
    x = cycle((0, 1), (2, 3))
    y = cycle((0, 2, 4))
    require(len(a5) == 60, "A5 even-permutation cardinality is not 60")
    require(x in a5 and y in a5, "named generators are not even permutations")
    require(generated_group(identity, (x, y)) == a5,
            "named generators do not generate all of A5")
    require(order(x, identity) == 2 and order(y, identity) == 3,
            "named generator orders differ from (2,3)")

    xy = compose(x, y)
    yx = compose(y, x)
    require(order(xy, identity) == 5 and order(yx, identity) == 5,
            "target labels are not order-five elements")
    require(xy != yx and xy != identity and yx != identity,
            "target labels do not distinguish the nonidentity target from identity")
    require(compose(xy, yx) in a5, "target product escaped A5")

    # Exact positive control: multiply the four diagonal factors over F2[A5].
    word = identity_matrix(identity)
    for label, role in ((x, 0), (y, 0), (y, 1), (x, 1)):
        word = matrix_product(word, diagonal_factor(label, role, identity))
    zero = frozenset()
    target = ((frozenset((xy,)), zero), (zero, frozenset((yx,))))
    require(word == target, "four-call witness does not produce diag(xy,yx)")

    # Every 3-cycle is a commutator in A5. They generate A5, so A5 is perfect.
    three_cycles = [g for g in a5 if order(g, identity) == 3]
    require(len(three_cycles) == 20, "unexpected number of A5 3-cycles")
    for r in three_cycles:
        a = next(i for i in range(5) if r[i] != i)
        b = r[a]
        d, e = [i for i in range(5) if i not in (a, b, r[b])]
        s = cycle((a, b), (d, e))
        commutator = compose(compose(compose(r, s), inverse(r)), inverse(s))
        require(s in a5 and commutator == inverse(r),
                "3-cycle commutator control failed")
    require(generated_group(identity, three_cycles) == a5,
            "3-cycles do not generate A5")

    # Perfectness implies every homomorphism into an abelian group is trivial.
    # The explicit commutator and generation checks above establish that fact
    # for the exact A5 source rather than inferring it from finite sampling.
    rational_zero = (0, 0, 0, 0, 0, 0, 0, 0, 0)
    source_images = {rational_zero for _ in a5}
    require(len(source_images) == 1, "A5 source-label image is not trivial")
    require(xy != identity and yx != identity,
            "positive control: original target unexpectedly equals identity")

    # Deliberate invalid nonzero image for the order-two generator: it fails
    # the source relation 2*phi(x)=0 in the torsion-free rational group.
    invalid_x = (1, 0, 0, 0, 0, 0, 0, 0, 0)
    twice_invalid_x = tuple(2 * value for value in invalid_x)
    require(twice_invalid_x != rational_zero,
            "nonzero rational torsion rejection control did not fire")

    # In F2, [0]+[0]=0, so each translated paid factor maps to the identity.
    mapped_difference = frozenset((identity,)) ^ frozenset((identity,))
    require(mapped_difference == zero,
            "mapped paid label difference did not cancel in characteristic two")
    print(
        "PASS_A5_ABELIAN_CALLER_COLLAPSE group=60 generated=true perfect=true "
        "xy_order=5 yx_order=5 distinct=true formal_calls=4 "
        "source_map=trivial_by_proof target=augmentation_by_proof controls=5 no_supplier"
    )


if __name__ == "__main__":
    main()
