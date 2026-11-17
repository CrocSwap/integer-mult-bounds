"""Exact polynomial budgets for a common acyclic interaction support."""

from fractions import Fraction


MAX_DIMENSION = 16
MAX_STEPS = 32
MAX_HEIGHT_BITS = 256


def nonnegative(value):
    """Validate the bounded rational interface; floats are not certificates."""
    if type(value) not in (int, Fraction):
        raise ValueError("expected an integer or Fraction")
    value = Fraction(value)
    if value < 0:
        raise ValueError("expected a nonnegative bound")
    if max(value.numerator.bit_length(), value.denominator.bit_length()) > MAX_HEIGHT_BITS:
        raise ValueError("rational height exceeds capacity")
    return value


def coefficients(norms, depth):
    """Return elementary and complete homogeneous coefficients through depth."""
    if type(depth) is not int or not 0 <= depth < MAX_DIMENSION:
        raise ValueError("depth exceeds capacity")
    if type(norms) not in (tuple, list) or len(norms) > MAX_STEPS:
        raise ValueError("step count exceeds capacity")
    values = tuple(nonnegative(value) for value in norms)
    elementary = [Fraction(1)] + [Fraction(0)] * depth
    homogeneous = elementary.copy()
    for value in values:
        for degree in range(depth, 0, -1):
            elementary[degree] += value * elementary[degree - 1]
        for degree in range(1, depth + 1):
            homogeneous[degree] += value * homogeneous[degree - 1]
    return tuple(elementary), tuple(homogeneous)


def envelopes(norms, depth):
    """Return the sharp forward and inverse norm envelopes."""
    elementary, homogeneous = coefficients(norms, depth)
    return sum(elementary), sum(homogeneous)


def trajectory_budget(norms, depth, input_norm, noise_norms):
    """Bound z_j-x, with noise added after each interaction factor."""
    forward, _ = envelopes(norms, depth)
    initial = nonnegative(input_norm)
    if type(noise_norms) not in (tuple, list) or len(noise_norms) != len(norms):
        raise ValueError("one noise bound is required per step")
    noise = tuple(nonnegative(value) for value in noise_norms)
    bound = (forward - 1) * initial
    for index, value in enumerate(noise):
        suffix, _ = envelopes(norms[index + 1 :], depth)
        bound += suffix * value
    return bound


def support_depth(matrices, dimension):
    """Certify the longest path of the union of all nonzero matrix supports."""
    if type(dimension) is not int or not 1 <= dimension <= MAX_DIMENSION:
        raise ValueError("dimension exceeds capacity")
    if type(matrices) not in (tuple, list) or len(matrices) > MAX_STEPS:
        raise ValueError("step count exceeds capacity")
    edges = [[False] * dimension for _ in range(dimension)]
    for matrix in matrices:
        if type(matrix) not in (tuple, list) or len(matrix) != dimension:
            raise ValueError("matrix has wrong row count")
        for row, entries in enumerate(matrix):
            if type(entries) not in (tuple, list) or len(entries) != dimension:
                raise ValueError("matrix has wrong column count")
            for column, value in enumerate(entries):
                if type(value) not in (int, Fraction):
                    raise ValueError("matrix entries must be rational")
                nonnegative(abs(value))
                edges[column][row] |= value != 0
    indegree = [sum(edges[source][target] for source in range(dimension))
                for target in range(dimension)]
    distance = [0] * dimension
    removed = [False] * dimension
    for _ in range(dimension):
        ready = [vertex for vertex in range(dimension)
                 if not removed[vertex] and indegree[vertex] == 0]
        if not ready:
            raise ValueError("interaction supports contain a directed cycle")
        vertex = ready[0]
        removed[vertex] = True
        for target in range(dimension):
            if edges[vertex][target]:
                indegree[target] -= 1
                distance[target] = max(distance[target], distance[vertex] + 1)
    return max(distance)
