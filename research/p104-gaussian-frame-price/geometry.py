"""Intervals and two-step flags of labeled binary subspaces, represented by point masks."""

from functools import cache

FULL = (1 << 512) - 1
ZERO = 1


def space_mask(basis):
    points = {0}
    for vector in basis:
        if not 0 < vector < 512 or vector in points:
            raise ValueError("The supplied vectors are dependent or exceed nine axes")
        points.update([v ^ vector for v in points])
    return sum(1 << v for v in points)


def elements(space):
    while space:
        bit = space & -space
        yield bit.bit_length() - 1
        space ^= bit


def dimension(space):
    size = space.bit_count()
    assert size and size.bit_count() == 1
    return size.bit_length() - 1


def included(smaller, larger):
    return smaller & larger == smaller


@cache
def join(first, second):
    if included(first, second):
        return second
    for vector in elements(second):
        if not first & (1 << vector):
            others = [v ^ vector for v in elements(first)]
            first |= sum(1 << u for u in others)
    return first


@cache
def gaussian(n, k):
    if not 0 <= k <= n:
        return 0
    a = b = 1
    for j in range(k):
        a *= 2**n - 2**j
        b *= 2**k - 2**j
    assert a % b == 0
    return a // b


def endpoint_options(site, other, paid, starts, ends, ranks, subspaces):
    """Return every possible dimension and its exact lower/upper interval."""
    neighbors = (set(paid[site]) | set(starts[site]) | set(ends[site])) - {other}
    options = []
    for rank in range(10):
        if any(ranks[h] == rank for h in neighbors):
            continue
        if any(ranks[h] <= rank for h in starts[site]):
            continue
        if any(ranks[h] >= rank for h in ends[site]):
            continue
        low, high = ZERO, FULL
        for h in neighbors:
            if ranks[h] < rank:
                low = join(low, subspaces[h])
            else:
                high &= subspaces[h]
        if included(low, high) and dimension(low) <= rank <= dimension(high):
            options.append((rank, low, high))
    return options


def space_count(option):
    rank, low, high = option
    return gaussian(dimension(high) - dimension(low), rank - dimension(low))


def flags(smaller, larger):
    """Count X < Y in two independent subspace intervals with fixed ranks."""
    u, a, b = smaller
    v, e, f = larger
    assert u < v
    c = b & f
    if not included(a, c) or dimension(c) < u:
        return 0
    d = dimension(a & e)
    n = dimension(c) - dimension(a)
    k = u - dimension(a)
    p = dimension(c & e) - d
    total = 0
    for ell in range(max(0, k - n + p), min(k, p) + 1):
        joined_rank = dimension(e) + u - d - ell
        choices_x = gaussian(p, ell) * gaussian(n - p, k - ell) * 2**((p - ell) * (k - ell))
        total += choices_x * gaussian(dimension(f) - joined_rank, v - joined_rank)
    return total


def finite_control():
    """Compare the formula against explicit pairs for every interval in F2^3."""
    seen = {frozenset([0])}
    for rank in range(3):
        for a in list(seen):
            if len(a) == 2**rank:
                for vector in set(range(8)) - a:
                    seen.add(frozenset(a | {j ^ vector for j in a}))
    spaces = sorted(sum(1 << v for v in a) for a in seen)
    intervals = [(d, a, b) for a in spaces for b in spaces if included(a, b)
                 for d in range(dimension(a), dimension(b) + 1)]
    members = {i: [v for v in spaces if dimension(v) == i[0]
                   and included(i[1], v) and included(v, i[2])] for i in intervals}
    checks = positive = 0
    for i in intervals:
        for j in intervals:
            if i[0] < j[0]:
                literal = sum(included(x, y) for x in members[i] for y in members[j])
                assert flags(i, j) == literal
                checks += 1
                positive += bool(literal)
    assert (len(spaces), checks, positive) == (16, 5956, 4948)
    return checks
