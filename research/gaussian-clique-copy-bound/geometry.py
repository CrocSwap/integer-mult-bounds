"""Exact Gaussian E8 geometry, using only Python's standard library.

Coordinates are doubled E8 roots. A Gaussian line is the rational real plane
spanned by r and J(r); a Gaussian flat's real dimension is twice its rank.
"""

from collections import Counter
from fractions import Fraction
from functools import reduce
from itertools import combinations, product
from math import gcd


def doubled_roots():
    roots = set()
    for i, j in combinations(range(8), 2):
        for a, b in product((-2, 2), repeat=2):
            root = [0] * 8
            root[i], root[j] = a, b
            roots.add(tuple(root))
    roots.update(signs for signs in product((-1, 1), repeat=8)
                 if sum(x < 0 for x in signs) % 2 == 0)
    return tuple(sorted(roots))


def J(row):
    return tuple(x for i in range(0, 8, 2) for x in (-row[i + 1], row[i]))


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def gaussian_lines():
    roots = doubled_roots()
    root_set = set(roots)
    assert len(roots) == 240
    assert all(dot(r, r) == 8 and J(r) in root_set for r in roots)
    assert all(J(J(r)) == tuple(-x for x in r) for r in roots)
    orbits = {min(r, J(r), tuple(-x for x in r),
                  tuple(-x for x in J(r))) for r in roots}
    assert len(orbits) == 60
    return tuple(sorted(orbits))


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def nonorthogonality(lines):
    return tuple(sum(1 << j for j, right in enumerate(lines)
                     if i != j and (dot(left, right) or dot(left, J(right))))
                 for i, left in enumerate(lines))


def maximal_cliques(adjacency):
    """Exhaustive pivoted Bron--Kerbosch, returning vertex bitmasks."""
    found = []

    def visit(clique, possible, excluded):
        if not (possible | excluded):
            found.append(clique)
            return
        pivot = max(bits(possible | excluded),
                    key=lambda i: (possible & adjacency[i]).bit_count())
        candidates = possible & ~adjacency[pivot]
        for vertex in bits(candidates):
            bit = 1 << vertex
            visit(clique | bit, possible & adjacency[vertex],
                  excluded & adjacency[vertex])
            possible &= ~bit
            excluded |= bit

    visit(0, (1 << len(adjacency)) - 1, 0)
    return tuple(sorted(found))


def primitive(row):
    divisor = reduce(gcd, row, 0)
    if not divisor:
        return tuple(row)
    if next(x for x in row if x) < 0:
        divisor = -divisor
    return tuple(x // divisor for x in row)


def remainder(row, basis):
    row = tuple(row)
    for old in basis:
        pivot = next(i for i, x in enumerate(old) if x)
        if row[pivot]:
            row = primitive(tuple(old[pivot] * x - row[pivot] * y
                                  for x, y in zip(row, old)))
    return row


def canonical_basis(rows):
    """Canonical rational row space via primitive integer elimination."""
    basis = []
    for row in rows:
        row = primitive(remainder(row, basis))
        if not any(row):
            continue
        pivot = next(i for i, x in enumerate(row) if x)
        basis = [primitive(tuple(row[pivot] * x - old[pivot] * y
                                 for x, y in zip(old, row)))
                 if old[pivot] else old for old in basis]
        basis.append(row)
        basis.sort(key=lambda old: next(i for i, x in enumerate(old) if x))
    return tuple(basis)


def gaussian_flats(lines):
    """All root-generated Gaussian flats, grouped by rank.

    Each item is (line_mask, canonical_real_basis). Extending every rank-r
    flat by every line outside it exhausts the rank-(r+1) flats.
    """
    levels = {0: ((0, ()),)}
    for rank in range(1, 4):
        spaces = set()
        for mask, basis in levels[rank - 1]:
            for i, line in enumerate(lines):
                if not (mask >> i) & 1:
                    spaces.add(canonical_basis((*basis, line, J(line))))
        flats = []
        for basis in spaces:
            assert len(basis) == 2 * rank
            mask = sum(1 << i for i, line in enumerate(lines)
                       if not any(remainder(line, basis)))
            flats.append((mask, basis))
        assert len({mask for mask, _ in flats}) == len(flats)
        levels[rank] = tuple(sorted(flats))
    full_basis = canonical_basis(lines)
    assert len(full_basis) == 8
    levels[4] = (((1 << len(lines)) - 1, full_basis),)
    return levels


def clique_hits(flat_mask, cliques):
    return sum(1 << i for i, clique in enumerate(cliques) if flat_mask & clique)


def pairing_rank(left_basis, right_basis):
    """Gaussian rank of the Hermitian pairing between two Gaussian flats."""
    real_rank = len(canonical_basis(tuple(dot(left, right) for right in right_basis)
                                    for left in left_basis))
    assert real_rank % 2 == 0
    return real_rank // 2


def self_check():
    """Cross-check integer elimination and the sharp witness independently."""
    def fraction_rank(rows):
        rows = [list(map(Fraction, row)) for row in rows]
        rank = 0
        for column in range(len(rows[0]) if rows else 0):
            pivot = next((i for i in range(rank, len(rows))
                          if rows[i][column]), None)
            if pivot is None:
                continue
            rows[rank], rows[pivot] = rows[pivot], rows[rank]
            divisor = rows[rank][column]
            rows[rank] = [value / divisor for value in rows[rank]]
            for i in range(rank + 1, len(rows)):
                scale = rows[i][column]
                rows[i] = [x - scale * y for x, y in zip(rows[i], rows[rank])]
            rank += 1
        return rank

    cases = (
        ((), 0),
        (((0, 0, 0),), 0),
        (((2, 4, 6), (3, 6, 9)), 1),
        (((1, 1), (1, -1)), 2),
        (((1, 0, 1), (0, 1, 1), (1, 1, 0)), 3),
    )
    for rows, expected in cases:
        basis = canonical_basis(rows)
        assert len(basis) == fraction_rank(rows) == expected
        assert canonical_basis(reversed(rows)) == basis
        assert canonical_basis((*rows, *rows)) == basis

    lines = gaussian_lines()
    left = (0, 1, 2, 11, 12, 45)
    right = (0, 3, 4, 5, 6, 7, 8, 9, 10, 54, 55, 56, 57, 58, 59)
    left_rows = tuple(row for i in left for row in (lines[i], J(lines[i])))
    right_rows = tuple(row for i in right for row in (lines[i], J(lines[i])))
    gram = tuple(tuple(dot(a, b) for b in right_rows) for a in left_rows)
    assert fraction_rank(left_rows) == 4
    assert fraction_rank(right_rows) == 6
    assert fraction_rank(gram) == 2
    assert pairing_rank(canonical_basis(left_rows), canonical_basis(right_rows)) == 1


if __name__ == "__main__":
    self_check()
    lines = gaussian_lines()
    graph = nonorthogonality(lines)
    cliques = maximal_cliques(graph)
    maximum = max(clique.bit_count() for clique in cliques)
    maximum_cliques = tuple(c for c in cliques if c.bit_count() == maximum)
    assert len(cliques) == len(set(cliques))
    assert all(all((clique ^ (1 << i)) & ~graph[i] == 0 for i in bits(clique))
               for clique in cliques)
    print("roots", len(doubled_roots()), "lines", len(lines))
    print("nonorthogonal degrees", dict(Counter(mask.bit_count() for mask in graph)))
    print("maximal clique size census", dict(sorted(Counter(c.bit_count() for c in cliques).items())))
    for rank, flats in gaussian_flats(lines).items():
        census = Counter((mask.bit_count(), clique_hits(mask, maximum_cliques).bit_count())
                         for mask, _ in flats)
        print("rank", rank, "flats", len(flats), "(size, max-cliques-hit): multiplicity", dict(sorted(census.items())))
