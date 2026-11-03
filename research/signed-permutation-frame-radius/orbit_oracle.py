"""Independent literal two-dimensional orbit optimization using integers only.

No radius formula, quantizer, inverse routine or predecessor code is imported.
Produced by Nick Petalas. Apache-2.0.
"""

from itertools import product


def frames(p):
    """Build the eight conjugated signed permutations by closed 2x2 algebra."""
    a, b = p[0]
    c, d = p[1]
    determinant = a * d - b * c
    if abs(determinant) != 1:
        raise ValueError("oracle requires a unimodular 2x2 frame")
    inverse = ((d // determinant, -b // determinant),
               (-c // determinant, a // determinant))
    result = []
    for swap, first, second in product((False, True), (-1, 1), (-1, 1)):
        s = ((0, first), (second, 0)) if swap else ((first, 0), (0, second))
        left = tuple(tuple(sum(p[i][k] * s[k][j] for k in range(2))
                           for j in range(2)) for i in range(2))
        result.append(tuple(tuple(sum(left[i][k] * inverse[k][j]
                                      for k in range(2)) for j in range(2))
                            for i in range(2)))
    if len(set(result)) != 8:
        raise ValueError("oracle group has duplicate frames")
    return tuple(result)


def image(g, point):
    x, y = point
    return (g[0][0] * x + g[0][1] * y, g[1][0] * x + g[1][1] * y)


def optimize(group, numerator, denominator, incumbent):
    """Return minimum scaled whole-orbit radius and enumerated box size.

    Any better output lies in the entrance box given by the incumbent radius.
    Stabilizer constraints are tested literally on every candidate output.
    """
    if len(group) != 8 or not 2 <= denominator <= 11:
        raise ValueError("oracle fixture limits exceeded")
    stabilizer = tuple(g for g in group if image(g, numerator) == numerator)
    if any(image(g, incumbent) != incumbent for g in stabilizer):
        raise ValueError("incumbent violates point stabilizer")
    residual = tuple(denominator * z - x for z, x in zip(incumbent, numerator))
    bound = max(abs(entry) for g in group for entry in image(g, residual))
    if bound > 128:
        raise ValueError("oracle radius cap exceeded")
    axes = tuple(range(-((bound - x) // denominator),
                       (x + bound) // denominator + 1) for x in numerator)
    if any(len(axis) > 129 for axis in axes):
        raise ValueError("oracle candidate capacity exceeded")
    best = bound
    candidates = 0
    for candidate in product(*axes):
        candidates += 1
        if any(image(g, candidate) != candidate for g in stabilizer):
            continue
        error = tuple(denominator * z - x
                      for z, x in zip(candidate, numerator))
        cost = max(abs(entry) for g in group for entry in image(g, error))
        best = min(best, cost)
    return best, candidates
