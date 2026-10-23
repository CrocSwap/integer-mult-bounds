"""Exact residual bank routes for the kernel word; chafreaky with OpenAI Codex.

The stored integer rows divided by two are an orthonormal basis. Entrance
rows span E; the remaining rows span E-perp. A coordinate permutation sends
the latter to the assigned contiguous block in a width-64 bank. This gives
an explicit rational isometry, with only powers of two in denominators.
"""
from collections import Counter, deque
from tile_m import tile


def placement(widths):
    by_width = {}
    for rep in range(8):
        for helper, width in enumerate(widths):
            assert 0 < width <= 8
            by_width.setdefault(width, deque()).append((rep, helper))
    patterns = tile({w: len(q) for w, q in by_width.items()}, 64)
    result = {}
    bank = 0
    for widths_in_bank, count in patterns:
        for _ in range(count):
            offset = 0
            for width in widths_in_bank:
                key = by_width[width].popleft()
                result[key] = (bank, offset, width)
                offset += width
            assert offset == 64
            bank += 1
    assert all(not q for q in by_width.values())
    assert len(result) == 8 * len(widths)
    return result, bank


def validate_isometries(rows, frames, roots, dimensions):
    seen = set()
    dot = lambda a, b: sum(x*y for x, y in zip(a, b))
    for record in rows:
        f = record['frame']
        assert f not in seen
        seen.add(f)
        e = record['entrance_rank']
        assert e == dimensions[f] and record['denominator'] == 2
        basis = record['entrance_basis'] + record['residual_basis']
        matrix = record['orthogonal_rows_numerator']
        assert len(basis) == len(matrix) == 8
        assert matrix == [roots[i] for i in basis]
        assert all(len(r) == 8 and all(type(x) is int for x in r) for r in matrix)
        assert all(dot(a,b) == 4*(i==j) for i,a in enumerate(matrix) for j,b in enumerate(matrix))
        # The first e rows span precisely the frame, not only its dimension.
        for i in frames[f]:
            assert sum(dot(roots[i], q)**2 for q in matrix[:e]) == 4*dot(roots[i], roots[i])
        assert len(record['entrance_basis']) == e
        # This selected family needs coordinate permutations only. Checking the
        # elementary reduction also bounds the literal route cost and primes.
        reduced = [[x // 2 for x in row] for row in matrix]
        assert all(x % 2 == 0 for row in matrix for x in row)
        operations = record['gaussian_reduction']
        assert len(operations) <= 7
        for kind, i, j, scalar in operations:
            assert kind == 'swap' and scalar is None and 0 <= i < 8 and 0 <= j < 8
            reduced[i], reduced[j] = reduced[j], reduced[i]
        assert reduced == [[int(i == j) for j in range(8)] for i in range(8)]
    return seen
