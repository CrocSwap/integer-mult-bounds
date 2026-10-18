"""Independent finite F2 oracle using complete vector sets, not elimination.

Vectors are integer masks in an explicitly specified ambient dimension.
Subspaces are frozensets containing every vector, including zero.  The bounded
enumerator covers ambient dimensions zero through six; all other helpers work
with any nonnegative ambient dimension that the caller can enumerate.
"""

from functools import cache


def _dimension(n):
    if not isinstance(n, int) or isinstance(n, bool) or n < 0:
        raise ValueError("Ambient dimension must be a nonnegative integer")
    return n


def _vector(vector, n):
    if (not isinstance(vector, int) or isinstance(vector, bool)
            or not 0 <= vector < (1 << n)):
        raise ValueError("Vector must be an integer mask in the ambient space")
    return vector


def _vectors(vectors, n):
    _dimension(n)
    try:
        return frozenset(_vector(vector, n) for vector in vectors)
    except TypeError as error:
        raise ValueError("Vectors must be iterable") from error


@cache
def _check_space(space, n):
    if 0 not in space or any(a ^ b not in space for a in space for b in space):
        raise ValueError("A subspace must contain zero and be closed under XOR")
    return space


def _space(vectors, n):
    return _check_space(_vectors(vectors, n), n)


@cache
def _dot(a, b, n):
    # Each coordinate contributes separately; no population count is used.
    value = 0
    for coordinate in range(n):
        value ^= ((a >> coordinate) & 1) * ((b >> coordinate) & 1)
    return value


def dot(a, b, n):
    """Compute the binary scalar product by explicit coordinate iteration."""
    _dimension(n)
    return _dot(_vector(a, n), _vector(b, n), n)


def span(rows, n):
    """Return every XOR combination of the supplied vectors."""
    rows = _vectors(rows, n)
    result = frozenset({0})
    for vector in sorted(rows):
        if vector not in result:
            result = result | frozenset(value ^ vector for value in result)
    return result


def _space_order(space):
    return len(space), tuple(sorted(space))


def list_subspaces(n):
    """Enumerate all subspaces of F2^n, ordered by size and sorted vectors.

    Each next layer is obtained by adjoining every vector outside each space
    in the preceding layer, taking its complete XOR closure, and deduplicating
    equal vector sets.  No choice of pivots or row reduction is involved.
    """
    _dimension(n)
    if n > 6:
        raise ValueError("Exhaustive enumeration is bounded to dimension six")
    return _list_subspaces(n)


@cache
def _list_subspaces(n):
    layer = (frozenset({0}),)
    result = []
    for dimension in range(n + 1):
        result.extend(layer)
        if dimension == n:
            break
        extensions = set()
        for space in layer:
            for vector in range(1, 1 << n):
                if vector not in space:
                    extensions.add(space | frozenset(x ^ vector for x in space))
        layer = tuple(sorted(extensions, key=_space_order))
    return tuple(result)


@cache
def _basis(space, n):
    generated = frozenset({0})
    result = []
    for vector in sorted(space):
        if vector not in generated:
            result.append(vector)
            generated = generated | frozenset(x ^ vector for x in generated)
    return tuple(result)


def basis(space, n):
    """Choose deterministic representatives by greedy closure membership."""
    return _basis(_space(space, n), n)


@cache
def _radical(space, n):
    return frozenset(x for x in space if all(_dot(x, y, n) == 0 for y in space))


def radical(space, n):
    """Return the radical by testing all vectors against the full space."""
    return _radical(_space(space, n), n)


@cache
def _classification(space, n):
    alternating = all(_dot(x, x, n) == 0 for x in space)
    return (len(space).bit_length() - 1, _radical(space, n) == frozenset({0}),
            alternating)


def classify(space, n):
    """Classify the restricted form, including the nondegenerate zero space."""
    dimension, nondegenerate, alternating = _classification(_space(space, n), n)
    return dict(dimension=dimension, nondegenerate=nondegenerate,
                nonalternating=not alternating, alternating=alternating)


@cache
def _characteristic_vectors(space, n):
    return tuple(v for v in sorted(space)
                 if all(_dot(v, x, n) == _dot(x, x, n) for x in space))


def characteristic_vectors(space, n):
    """Find every characteristic vector by exhaustively testing candidates."""
    return _characteristic_vectors(_space(space, n), n)


def characteristic(space, n):
    """Return the unique characteristic vector of a nondegenerate space."""
    space = _space(space, n)
    if _radical(space, n) != frozenset({0}):
        raise ValueError("A unique characteristic vector needs a nondegenerate space")
    candidates = _characteristic_vectors(space, n)
    if len(candidates) != 1:
        raise ValueError("The space does not have a unique characteristic vector")
    return candidates[0]


@cache
def _project(space, vector, n):
    representatives = _basis(space, n)
    candidates = tuple(candidate for candidate in sorted(space)
                       if all(_dot(candidate, b, n) == _dot(vector, b, n)
                              for b in representatives))
    if len(candidates) != 1:
        raise ValueError("Orthogonal projection needs a nondegenerate space")
    return candidates[0]


def project(space, vector, n):
    """Find the unique vector in the space with matching basis pairings."""
    space = _space(space, n)
    vector = _vector(vector, n)
    return _project(space, vector, n)


def residual(lower, upper, n):
    """Return U intersect A-perp for nested complete vector sets A <= U."""
    lower, upper = _space(lower, n), _space(upper, n)
    if not lower <= upper:
        raise ValueError("Residual spaces must be nested")
    return frozenset(x for x in upper if all(_dot(x, a, n) == 0 for a in lower))
