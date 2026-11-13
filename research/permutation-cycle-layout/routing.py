"""Exact fixed-width wire-permutation tensor trains. Apache-2.0."""

from itertools import product

MAX_SITES = 64
MAX_LOCAL_DIMENSION = 16
MAX_EXPLICIT_SITES = 6
MAX_EXPLICIT_STATES = 64


def check_permutation(permutation):
    """Validate the bounded source-to-destination permutation interface."""
    n = len(permutation)
    if not 1 <= n <= MAX_SITES:
        raise ValueError("site count must be in 1..64")
    if any(type(v) is not int for v in permutation):
        raise ValueError("site labels must be integers")
    if sorted(permutation) != list(range(n)):
        raise ValueError("not a permutation of the site labels")


def check_layout(permutation, order, dimension):
    check_permutation(permutation)
    if type(dimension) is not int or not 2 <= dimension <= MAX_LOCAL_DIMENSION:
        raise ValueError("local dimension must be in 2..16")
    if len(order) != len(permutation) or any(type(v) is not int for v in order):
        raise ValueError("invalid simultaneous column order")
    if sorted(order) != list(range(len(permutation))):
        raise ValueError("column order must permute the site labels")


def cycle_order(permutation):
    """List disjoint directed cycles consecutively, in their directed order."""
    check_permutation(permutation)
    n = len(permutation)
    seen = [False] * n
    order = []
    for start in range(n):
        if seen[start]:
            continue
        site = start
        for _ in range(n):
            if seen[site]:
                break
            seen[site] = True
            order.append(site)
            site = permutation[site]
        if site != start:
            raise RuntimeError("cycle traversal did not close")
    if len(order) != n:
        raise RuntimeError("cycle order omitted a site")
    return tuple(order)


def cut_profile(permutation, order, dimension):
    """Return outgoing-wire counts and predicted exact bonds, including ends."""
    check_layout(permutation, order, dimension)
    left = set()
    counts = [0]
    for site in order:
        left.add(site)
        counts.append(sum(permutation[v] not in left for v in left))
    return tuple(counts), tuple(dimension ** (2 * c) for c in counts)


def wire_frontiers(permutation, order, dimension):
    """The state at a cut labels every directed wire crossing that cut."""
    check_layout(permutation, order, dimension)
    left = set()
    frontiers = [()]
    for site in order:
        left.add(site)
        frontiers.append(tuple(i for i, j in enumerate(permutation)
                               if (i in left) != (j in left)))
    return tuple(frontiers)


def local_factor(permutation, site, left, right, before, after, x, y):
    """One 0/1 tensor entry; local physical indices are input x and output y."""
    old = dict(zip(left, before, strict=True))
    new = dict(zip(right, after, strict=True))
    for edge, destination in enumerate(permutation):
        values = []
        if edge in old:
            values.append(old[edge])
        if edge in new:
            values.append(new[edge])
        if edge == site:
            values.append(x)
        if destination == site:
            values.append(y)
        if values and any(value != values[0] for value in values):
            return 0
    return 1


def make_train(permutation, order, dimension):
    """Materialize a bounded fixed-width train, with both endpoint bonds one."""
    check_layout(permutation, order, dimension)
    if len(permutation) > MAX_EXPLICIT_SITES:
        raise ValueError("explicit train limited to six sites")
    frontiers = wire_frontiers(permutation, order, dimension)
    if any(dimension ** len(f) > MAX_EXPLICIT_STATES for f in frontiers):
        raise ValueError("explicit virtual state cap exceeded")
    states = [tuple(product(range(dimension), repeat=len(f))) for f in frontiers]
    train = []
    for step, site in enumerate(order):
        tables = {}
        for y, x in product(range(dimension), repeat=2):
            tables[y, x] = tuple(tuple(local_factor(
                permutation, site, frontiers[step], frontiers[step + 1],
                before, after, x, y) for after in states[step + 1])
                for before in states[step])
        train.append(tables)
    return tuple(train)


def train_entry(train, order, x, y):
    """Contract supplied local matrices, without using the routing formula."""
    row = (1,)
    for tables, site in zip(train, order, strict=True):
        matrix = tables[y[site], x[site]]
        row = tuple(sum(a * b for a, b in zip(row, column, strict=True))
                    for column in zip(*matrix, strict=True))
    if len(row) != 1:
        raise ValueError("tensor train has an open right endpoint")
    return row[0]
