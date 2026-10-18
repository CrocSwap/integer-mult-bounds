"""Exact rational geometry for the 40 Eisenstein E8 lines (standard library).

Jonathan Lam, with substantial OpenAI Codex assistance; Apache-2.0.
The order-three construction is credited to GamingPuzzled's PR620.
No predecessor implementation is imported or executed.
"""

from itertools import combinations, product
from math import gcd
from functools import reduce


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def primitive(row):
    d = reduce(gcd, row, 0)
    if not d:
        return tuple(row)
    first = next(x for x in row if x)
    if first < 0:
        d = -d
    return tuple(x // d for x in row)


def echelon(rows):
    """Canonical integer-scaled RREF; only exact integer operations."""
    pivots = {}
    for row in rows:
        row = primitive(row)
        for p, b in sorted(pivots.items()):
            if row[p]:
                row = primitive(tuple(b[p] * x - row[p] * y
                                      for x, y in zip(row, b)))
        if any(row):
            pivots[next(i for i, x in enumerate(row) if x)] = row
    for p in sorted(pivots, reverse=True):
        b = pivots[p]
        for q in sorted(pivots):
            if q < p and pivots[q][p]:
                row = pivots[q]
                pivots[q] = primitive(tuple(b[p] * x - row[p] * y
                                             for x, y in zip(row, b)))
    return tuple(pivots[p] for p in sorted(pivots))


def contains(basis, row):
    for b in basis:
        p = next(i for i, x in enumerate(b) if x)
        if row[p]:
            row = primitive(tuple(b[p] * x - row[p] * y
                                  for x, y in zip(row, b)))
    return not any(row)


def roots():
    """PR620's standard root-line order, followed by the negatives."""
    candidates = []
    for i, j in combinations(range(8), 2):
        for a, b in product((2, -2), repeat=2):
            row = [0] * 8
            row[i], row[j] = a, b
            candidates.append(tuple(row))
    candidates += [s for s in product((1, -1), repeat=8)
                   if s.count(-1) % 2 == 0]
    lines, seen = [], set()
    for r in candidates:
        if r not in seen and tuple(-x for x in r) not in seen:
            seen.add(r)
            lines.append(r)
    return lines + [tuple(-x for x in r) for r in lines]


def reflection(row, root):
    # Roots have squared norm eight: s_a(x) = x - <x,a>a/4.
    numerator = tuple(4 * x - dot(row, root) * a
                      for x, a in zip(row, root))
    require(all(x % 4 == 0 for x in numerator), 'nonintegral root reflection')
    return tuple(x // 4 for x in numerator)


def geometry():
    rr = roots()
    require(len(rr) == len(set(rr)) == 240, 'root count')
    require(all(dot(r, r) == 8 for r in rr), 'root norm')
    pairs = []
    for a in rr:
        if len(pairs) == 4:
            break
        if any(dot(a, x) for pair in pairs for x in pair):
            continue
        for b in rr:
            if dot(a, b) == -4 and not any(dot(b, x) for pair in pairs for x in pair):
                pairs.append((a, b))
                break
    require(len(pairs) == 4, 'four orthogonal A2 planes')

    def rotate(row):
        # The four plane actions commute; s_a s_b acts rightmost first.
        for a, b in reversed(pairs):
            row = reflection(reflection(row, b), a)
        return row

    rotated = {r: rotate(r) for r in rr}
    require(set(rotated.values()) == set(rr), 'root permutation')
    require(all(rotated[rotated[rotated[r]]] == r for r in rr), 'order three')
    require(all(all(x + y + z == 0 for x, y, z in zip(r, rotated[r], rotated[rotated[r]]))
                for r in rr), 'J squared plus J plus I')
    require(all(dot(r, s) == dot(rotated[r], rotated[s]) for r in rr for s in rr),
            'orthogonal action')
    seen, reps, images, orbits = set(), [], [], []
    for r in rr:
        if r in seen:
            continue
        orbit = {r, rotated[r], rotated[rotated[r]]}
        orbit |= {tuple(-x for x in t) for t in tuple(orbit)}
        basis = echelon((r, rotated[r]))
        require(len(basis) == 2, 'line rational rank')
        require(orbit == {s for s in rr if contains(basis, s)}, 'line orbit completeness')
        require(len(orbit) == 6 and not (orbit & seen), 'six-root partition')
        seen |= orbit
        reps.append(r)
        images.append(rotated[r])
        orbits.append(sorted(orbit))
    require(len(reps) == 40, 'Eisenstein line count')
    adjacent = []
    for i, r in enumerate(reps):
        mask = sum(1 << j for j, s in enumerate(reps)
                   if j != i and (dot(r, s) or dot(r, images[j])))
        adjacent.append(mask)
    require(all(m.bit_count() == 27 for m in adjacent), 'nonorthogonal degree')
    return reps, images, adjacent, pairs, orbits


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def maximal_cliques(adjacent):
    """Bron--Kerbosch with a deterministic pivot; all maximal cliques."""
    out = []

    def visit(chosen, possible, excluded):
        if not (possible | excluded):
            out.append(chosen)
            return
        pivot = max(bits(possible | excluded),
                    key=lambda i: (possible & adjacent[i]).bit_count())
        for i in list(bits(possible & ~adjacent[pivot])):
            bit = 1 << i
            visit(chosen | bit, possible & adjacent[i], excluded & adjacent[i])
            possible ^= bit
            excluded |= bit

    visit(0, (1 << len(adjacent)) - 1, 0)
    return sorted(out)


def all_cliques(adjacent):
    """Every nonempty clique exactly once, by increasing vertex order."""
    result = []

    def extend(chosen, possible):
        while possible:
            bit = possible & -possible
            possible ^= bit
            i = bit.bit_length() - 1
            result.append(chosen | bit)
            extend(chosen | bit, possible & adjacent[i])

    extend(0, (1 << len(adjacent)) - 1)
    return sorted(result)


def flats(reps, images):
    """Generate every line-spanned flat, by adjoining a line to each rank."""
    all_flats = [(0, (), ())]
    level = {(): ()}
    for degree in range(1, 5):
        new = {}
        for basis, generators in level.items():
            for i, r in enumerate(reps):
                if not contains(basis, r):
                    enlarged = echelon(basis + (r, images[i]))
                    require(len(enlarged) == 2 * degree, 'flat rank increment')
                    new.setdefault(enlarged, generators + (i,))
        for basis, generators in new.items():
            mask = sum(1 << i for i, r in enumerate(reps) if contains(basis, r))
            require(all(contains(basis, images[i]) for i in bits(mask)), 'J-invariant flat')
            all_flats.append((mask, basis, generators))
        level = new
    require(len(level) == 1, 'one full flat')
    require(len({m for m, _, _ in all_flats}) == len(all_flats), 'distinct flat closures')
    return sorted(all_flats, key=lambda f: (len(f[1]), f[0]))


def pairing_rank(basis_a, basis_b):
    rank = len(echelon(tuple(tuple(dot(a, b) for b in basis_b) for a in basis_a)))
    require(rank % 2 == 0, 'odd rational pairing rank')
    return rank // 2
