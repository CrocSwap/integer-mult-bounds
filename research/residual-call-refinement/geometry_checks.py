"""Check the retained encoded Layout on complete small physical geometries."""

from itertools import product

import specification as spec


def one(dimension, columns, remainder, i, k, half):
    from cardinal_counts import Count
    from check_support import inspect_count
    from layout import Layout
    from numeric import Geometry
    from plan import Plan
    from words import Arena, Ring

    n = dimension * columns + remainder
    size = columns // 2 if half else columns
    if not size:
        return None
    first = k * columns if half else i * columns
    second = (k + 1) * columns - size if half else k * columns
    # Project integer coordinate labels directly into the original body.
    core = dimension * columns
    positions = list(range(core)) + list(range(2 * n - core, 2 * n))
    a, b = positions[first], positions[second]
    expected, region = spec.spectator_extents(n, 2, 5, 3, a, b, size)
    arena, indices = Arena(3, 128), Arena(12, 128)
    modulus = arena.input(3)
    ring = Ring(modulus)
    words = [indices.input(v) for v in (columns, 0, n, first, second, size)]
    page = Geometry(
        Plan(dimension, 1, False, ()), indices, words[0], words[1], 23, object()
    )
    counts = [Count.literal(v) for v in (2, 5, 3)]
    layout = Layout(page, words[2], ring, 3, *counts)
    try:
        result = layout.child_extents(*words[3:], before=counts[0])
        try:
            actual = tuple(inspect_count(x) for x in result)
        finally:
            for value in result:
                value.close()
        target = tuple(coefficient * 3**exponent for coefficient, exponent in expected)
        spec.need(actual == target, "encoded child spectator partition")
        spec.need(
            actual[0] * actual[1] * actual[2] * 3 ** (2 * size)
            == 2 * 5 * 3 * 3 ** (2 * n),
            "complete child volume conservation",
        )
        return region, columns - 2 * size if half else None
    finally:
        layout.close()
        page.close()
        for value in counts:
            value.close()
        indices.free_many(*words)
        ring.close()
        arena.free(modulus)
        spec.need(not indices.live and not arena.live, "geometry fixture cleanup")


def run():
    regions = [0, 0, 0]
    odd = even = cases = 0
    for dimension, columns in product((2, 3), (1, 2, 3, 5)):
        for remainder in range(dimension):
            for i, k in ((0, 1), (dimension, dimension + 1), (0, dimension)):
                for half in (False, True):
                    if half and (i < dimension) != (k < dimension):
                        continue
                    result = one(dimension, columns, remainder, i, k, half)
                    if result is None:
                        continue
                    region, middle = result
                    cases += 1
                    regions[region] += 1
                    odd += middle == 1
                    even += middle == 0
    return {
        "cases": cases,
        "gap_before_between_after": regions,
        "odd_reset_spectators": odd,
        "even_reset_spectators": even,
    }
