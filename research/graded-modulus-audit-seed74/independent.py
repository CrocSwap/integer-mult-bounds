"""Small, independent exhaustive oracle for mixed-radix grade aliases.

This file intentionally imports neither the predecessor packing implementation
nor this contribution's structural theorem checker.  Its grade calculation
uses a flattened-index floor formula, not a recurrence for grade weights:

    grade(x) = x - sum(x // P_j for j in range(1, D))  (mod T).

Here P_j is the product of the first j radices.  Expanding each floor in
mixed-radix digits gives the predecessor's weights, including radix-one axes.
Carries are obtained by ordinary column addition; no subset-sum description
of attainable carry counts is used.  This is finite evidence, not an all-shape
proof.  The deliberately small N <= 100 domain keeps quadratic replay bounded.
"""

from itertools import product
from math import prod


MAX_POINTS = 100


def _shape(shape):
    try:
        result = tuple(shape)
    except TypeError as exc:
        raise ValueError("shape must be a nonempty iterable of positive integers") from exc
    if not result or any(type(n) is not int or n < 1 for n in result):
        raise ValueError("shape must be a nonempty iterable of positive integers")
    if prod(result) > MAX_POINTS:
        raise ValueError(f"independent oracle is limited to N <= {MAX_POINTS}")
    return result


def _table(shape):
    strides = []
    size = 1
    for radix in shape:
        strides.append(size)
        size *= radix
    # product() gives lexicographic coordinate order, irrespective of flattening.
    coordinates = tuple(product(*(range(n) for n in shape)))
    indices = tuple(sum(digit * step for digit, step in zip(v, strides))
                    for v in coordinates)
    return size, tuple(strides), coordinates, indices


def _grade(index, strides, modulus):
    return (index - sum(index // step for step in strides[1:])) % modulus


def _unflatten(index, shape):
    remainder = index
    digits = []
    for radix in shape:
        remainder, digit = divmod(remainder, radix)
        digits.append(digit)
    if remainder:
        raise RuntimeError("internal oracle error: index is outside the box")
    return tuple(digits)


def _carry_digits(a, b, shape):
    incoming = 0
    carries = []
    for left, right, radix in zip(a, b, shape):
        outgoing, _ = divmod(left + right + incoming, radix)
        if outgoing not in (0, 1):
            raise RuntimeError("internal oracle error: a carry is not binary")
        carries.append(outgoing)
        incoming = outgoing
    if carries[-1]:
        raise RuntimeError("internal oracle error: below-N sum has a final carry")
    return tuple(carries[:-1])


def census(shape, T):
    """Exhaust all ordered pairs with I(a)+I(b)<N for one shape/modulus.

    ``invalid_pairs`` counts componentwise sums outside the box, restricted to
    this below-N domain.  ``accepted_invalid_pairs`` counts precisely those
    invalid pairs whose grades nevertheless agree.  ``first_bad_alias`` is the
    first such pair in lexicographic (a,b) order, or None.  All dictionary
    contents can be serialized directly as JSON.
    """
    shape = _shape(shape)
    if type(T) is not int or T < 1:
        raise ValueError("T must be a positive integer")
    N, strides, coordinates, indices = _table(shape)
    below_n_pairs = invalid_pairs = accepted_invalid_pairs = 0
    first_bad_alias = None
    for a, index_a in zip(coordinates, indices):
        for b, index_b in zip(coordinates, indices):
            index_sum = index_a + index_b
            if index_sum >= N:
                continue
            below_n_pairs += 1
            component_sum = tuple(x + y for x, y in zip(a, b))
            invalid = any(digit >= radix for digit, radix in zip(component_sum, shape))
            c = _unflatten(index_sum, shape)
            carries = _carry_digits(a, b, shape)
            if invalid != bool(sum(carries)):
                raise RuntimeError("internal oracle error: geometric/carry disagreement")
            grade_a = _grade(index_a, strides, T)
            grade_b = _grade(index_b, strides, T)
            grade_c = _grade(index_sum, strides, T)
            accepted = (grade_a + grade_b) % T == grade_c
            if not invalid and not accepted:
                raise RuntimeError("internal oracle error: a valid pair was rejected")
            if not invalid:
                continue
            invalid_pairs += 1
            if not accepted:
                continue
            accepted_invalid_pairs += 1
            if first_bad_alias is None:
                first_bad_alias = {
                    "a": list(a), "b": list(b), "c": list(c),
                    "component_sum": list(component_sum),
                    "index_a": index_a, "index_b": index_b,
                    "index_c": index_sum, "index_sum": index_sum,
                    "grade_a": grade_a, "grade_b": grade_b, "grade_c": grade_c,
                    "grade_sum": grade_a + grade_b,
                    "carry_count": sum(carries), "carries": list(carries),
                }
    if below_n_pairs != N * (N + 1) // 2:
        raise RuntimeError("internal oracle error: exhaustive pair count is wrong")
    return {
        "shape": list(shape), "modulus": T, "N": N,
        "below_n_pairs": below_n_pairs, "invalid_pairs": invalid_pairs,
        "accepted_invalid_pairs": accepted_invalid_pairs,
        "first_bad_alias": first_bad_alias,
    }


def attainable_counts(shape):
    """Return all attained internal carry counts, including zero, by replay."""
    shape = _shape(shape)
    N, _, coordinates, indices = _table(shape)
    counts = set()
    for a, index_a in zip(coordinates, indices):
        for b, index_b in zip(coordinates, indices):
            if index_a + index_b < N:
                counts.add(sum(_carry_digits(a, b, shape)))
    return tuple(sorted(counts))


def self_check():
    """Explicit checks remain active under python -O."""
    expected_counts = {
        (4,): (0,),
        (1, 1, 1): (0,),
        (2, 3): (0, 1),
        (2, 1, 2): (0, 2),
        (2, 2, 1): (0, 1),
        (2, 1, 2, 1, 2): (0, 2, 4),
    }
    for shape, expected in expected_counts.items():
        actual = attainable_counts(shape)
        if actual != expected:
            raise RuntimeError(f"carry census failed for {shape}: {actual} != {expected}")
    bad = census((2, 1, 2), 2)
    if (bad["below_n_pairs"], bad["invalid_pairs"], bad["accepted_invalid_pairs"]) != (10, 1, 1):
        raise RuntimeError("known alias pair census failed")
    witness = bad["first_bad_alias"]
    if (witness["a"], witness["b"], witness["c"], witness["carry_count"]) != (
        [1, 0, 0], [1, 0, 0], [0, 0, 1], 2
    ):
        raise RuntimeError("known alias witness failed")
    for shape, modulus in (((2, 1, 2), 3), ((2, 1, 2, 1, 2), 3), ((4,), 1)):
        if census(shape, modulus)["accepted_invalid_pairs"]:
            raise RuntimeError(f"known safe modulus failed for {shape}, {modulus}")
    for shape, modulus in (((), 1), ((0,), 1), ((True,), 1), ((101,), 1), ((2,), 0), ((2,), True)):
        try:
            census(shape, modulus)
        except ValueError:
            continue
        raise RuntimeError(f"invalid arguments accepted: {shape}, {modulus}")


if __name__ == "__main__":
    self_check()
    print("PASS: independent mixed-radix oracle self-checks")
