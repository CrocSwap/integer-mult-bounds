"""Star-configuration graphs G_Gamma and the exact dual-certificate arithmetic.

Standard library only.  Vertices of G_Gamma are numbered: points 0..n-1 (the
vertices of Gamma), then pair n+e for the e-th listed edge of Gamma.  A point is
adjacent to the pairs containing it, two pairs are adjacent iff they are
disjoint, and two points are never adjacent (the definition of PR #7114,
section 8).  Vertex sets are bit masks.
"""
from fractions import Fraction
from itertools import permutations

MAX_POINTS = 6
MAX_VERTICES = 15


class CheckError(ValueError):
    """A certificate or graph failed an exact check."""


def require(condition, message):
    """Raise CheckError unless condition holds (active under -O as well)."""
    if not condition:
        raise CheckError(str(message))


def check_gamma(n, edges):
    """Reject anything but a simple graph on points 0..n-1 within the size caps."""
    require(1 <= n <= MAX_POINTS, n)
    require(n + len(edges) <= MAX_VERTICES, (n, len(edges)))
    seen = set()
    for a, b in edges:
        require(0 <= a < n and 0 <= b < n and a != b, (a, b))
        key = frozenset((a, b))
        require(key not in seen, (a, b))
        seen.add(key)
    return seen


def neighbour_masks(n, edges):
    """Return the neighbour mask of every vertex of G_Gamma."""
    check_gamma(n, edges)
    total = n + len(edges)
    masks = [0] * total
    for e, (a, b) in enumerate(edges):
        for point in (a, b):
            masks[point] |= 1 << (n + e)
            masks[n + e] |= 1 << point
        for f, (c, d) in enumerate(edges):
            if f != e and len({a, b, c, d}) == 4:
                masks[n + e] |= 1 << (n + f)
    return masks


def close(mask, nbrs):
    """Decoding closure: add every vertex whose neighbours all lie in the set."""
    total = len(nbrs)
    current = mask
    for _ in range(total + 1):
        grown = current
        for v in range(total):
            if not (current >> v) & 1 and (nbrs[v] & ~current) == 0:
                grown |= 1 << v
        if grown == current:
            return current
        current = grown
    raise CheckError("closure did not stabilise")


def vertex_permutations(n, edges):
    """Permutations of G_Gamma induced by the automorphisms of Gamma."""
    edge_index = {frozenset(e): i for i, e in enumerate(edges)}
    require(len(edge_index) == len(edges), "check failed")
    found = []
    for p in permutations(range(n)):
        images = [edge_index.get(frozenset((p[a], p[b]))) for a, b in edges]
        if None not in images:
            found.append(list(p) + [n + i for i in images])
    require(found and found[0] == list(range(n + len(edges))), "check failed")
    return found


def image(perm, mask):
    """Image of a vertex set under a vertex permutation."""
    out = 0
    for v, w in enumerate(perm):
        if (mask >> v) & 1:
            out |= 1 << w
    return out


def certificate_terms(entry, perm):
    """One certificate entry, moved by perm, as (coefficients, right-hand side).

    ["M", S, v]    : f(S) - f(S+v) >= -1          (a vertex adds at most one)
    ["S", S, i, j] : f(S+i) + f(S+j) - f(S+i+j) - f(S) >= 0   (submodularity)
    Both hold for every vertex set S and vertices outside S, so the moved entry
    is a valid inequality whether or not perm is an automorphism.
    """
    kind, base = entry[0], image(perm, entry[1])
    moved = [perm[v] for v in entry[2:]]
    require(len(set(moved)) == len(moved), "check failed")
    for v in moved:
        require(not (base >> v) & 1, entry)
    if kind == "M":
        require(len(moved) == 1, entry)
        return [(base, 1), (base | 1 << moved[0], -1)], -1
    require(kind == "S" and len(moved) == 2, entry)
    i, j = moved
    return [(base | 1 << i, 1), (base | 1 << j, 1),
            (base | 1 << i | 1 << j, -1), (base, -1)], 0


def certified_bound(n, edges, certificate):
    """Exact lower bound on f(empty set) proved by a group-averaged certificate.

    Returns the bound, or raises CheckError if the nonnegative combination
    does not reduce to f(closure of empty) - c f(V) >= rhs.
    """
    nbrs = neighbour_masks(n, edges)
    total = len(nbrs)
    full = (1 << total) - 1
    group = vertex_permutations(n, edges)
    cache = {}
    coefficient = {}
    rhs = Fraction(0)
    for entry, text in certificate:
        require(0 <= entry[1] <= full, entry)
        require(all(0 <= v < total for v in entry[2:]), entry)
        weight = Fraction(text)
        require(weight > 0, (entry, text))
        share = weight / len(group)
        for perm in group:
            terms, constant = certificate_terms(entry, perm)
            rhs += share * constant
            for mask, sign in terms:
                if mask not in cache:
                    cache[mask] = close(mask, nbrs)
                key = cache[mask]
                coefficient[key] = coefficient.get(key, Fraction(0)) + share * sign
    empty = close(0, nbrs)
    left = {key: value for key, value in coefficient.items() if value != 0}
    require(left.get(empty) == 1, "coefficient of f(empty) is not 1")
    require(set(left) <= {empty, full}, "certificate leaves other sets")
    return rhs - left.get(full, Fraction(0)) * total


def gram_pattern(n, edges):
    """Integer 1-block pattern of rank at most n+1 (PR #7114, Corollary 12).

    Labels in Z^(n+1) with the form diag(1,...,1,-1): x_c = e_c for a point and
    x_T = e_c + e_d + e_last for a pair T = cd.  Returns the Gram matrix.
    """
    labels = []
    for c in range(n):
        labels.append([1 if i == c else 0 for i in range(n + 1)])
    for a, b in edges:
        labels.append([1 if i in (a, b, n) else 0 for i in range(n + 1)])
    form = [1] * n + [-1]
    return [[sum(x[i] * form[i] * y[i] for i in range(n + 1)) for y in labels]
            for x in labels]


def is_pattern(matrix, nbrs):
    """Unit diagonal and zeros on non-adjacent pairs, as integers."""
    total = len(nbrs)
    for a in range(total):
        if matrix[a][a] != 1:
            return False
        for b in range(total):
            if a != b and not (nbrs[a] >> b) & 1 and matrix[a][b] != 0:
                return False
    return True
