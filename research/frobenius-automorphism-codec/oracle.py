"""Literal sparse-polynomial substitution, independent of the codec layout."""

from itertools import permutations

from linear import require


def multiply(field, cutoffs, left, right):
    result = {}
    for a, x in left.items():
        for b, y in right.items():
            exponent = tuple(s + t for s, t in zip(a, b))
            if all(s < t for s, t in zip(exponent, cutoffs)):
                value = field.add(result.get(exponent, 0), field.mul(x, y))
                if value:
                    result[exponent] = value
                else:
                    result.pop(exponent, None)
    return result


def power(field, cutoffs, value, exponent):
    require(0 <= exponent <= 64, "power capacity")
    result = {tuple(0 for _ in cutoffs): 1}
    for _ in range(exponent):
        result = multiply(field, cutoffs, result, value)
    return result


def substitute(field, cutoffs, images, exponent):
    result = {tuple(0 for _ in cutoffs): 1}
    for image, degree in zip(images, exponent):
        result = multiply(field, cutoffs, result, power(field, cutoffs, image, degree))
    return result


def determinant(field, columns):
    """Leibniz formula, separate from the ordered-basis elimination."""
    n = len(columns)
    require(n <= 4, "determinant capacity")
    result = 0
    for permutation in permutations(range(n)):
        inversions = sum(permutation[i] > permutation[j]
                         for i in range(n) for j in range(i + 1, n))
        term = 1
        for j, i in enumerate(permutation):
            term = field.mul(term, columns[j][i])
        result = field.add(result, field.neg(term) if inversions % 2 else term)
    return result


def binary_rank(columns):
    """Integer XOR elimination, not the field RREF used by the codec."""
    pivots = {}
    for column in columns:
        value = sum(x << i for i, x in enumerate(column))
        for bit in range(len(column) - 1, -1, -1):
            if value & (1 << bit):
                if bit in pivots:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    return len(pivots)


def column_rank(field, columns):
    """Normalize sparse leading columns instead of reducing the transposed rows."""
    pivots = {}
    for column in columns:
        value = list(column)
        for i in range(len(value)):
            if not value[i]:
                continue
            if i in pivots:
                scale = field.neg(value[i])
                value = [field.add(x, field.mul(scale, y))
                         for x, y in zip(value, pivots[i])]
            else:
                inverse = field.inv(value[i])
                pivots[i] = tuple(field.mul(inverse, x) for x in value)
                break
    return len(pivots)


def inspect(codec, images, all_products=False):
    field = codec.field
    sparse = tuple({a: x for a, x in zip(codec.monomials, image) if x} for image in images)
    for image, cutoff in zip(sparse, codec.cutoffs):
        require(not power(field, codec.cutoffs, image, cutoff), "literal relation failed")
    substitutions = tuple(substitute(field, codec.cutoffs, sparse, a) for a in codec.monomials)
    columns = tuple(tuple(image.get(a, 0) for a in codec.monomials) for image in substitutions)
    if field.q == 2:
        require(binary_rank(columns) == codec.n, "literal binary substitution singular")
    elif codec.n <= 4:
        require(determinant(field, columns) != 0, "literal substitution determinant zero")
    else:
        require(column_rank(field, columns) == codec.n, "literal substitution singular")
    checked = 0
    if all_products:
        for a, left in zip(codec.monomials, substitutions):
            for b, right in zip(codec.monomials, substitutions):
                exponent = tuple(s + t for s, t in zip(a, b))
                expected = (substitute(field, codec.cutoffs, sparse, exponent)
                            if all(s < t for s, t in zip(exponent, codec.cutoffs)) else {})
                require(multiply(field, codec.cutoffs, left, right) == expected,
                        "literal product not preserved")
                checked += 1
    return checked
