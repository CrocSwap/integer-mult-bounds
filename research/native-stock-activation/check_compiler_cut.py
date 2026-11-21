"""Replay fresh and older cover packets through a real archived compiler base plan."""

import argparse
import sys
from io import BytesIO
from math import prod
from pathlib import Path

from check_module_atoms import expected_packet, pack, payload, scalar, unpack


def run_checks(predecessor):
    sys.path.insert(0, str(predecessor.resolve()))
    from compiler_cut import base_ordinary, base_reversed, move_frame, source_rule
    from module_atoms import balanced_widths
    from streaming_routes import cold_swap_tape
    from ternary_frames import covered_factors

    rule = source_rule()
    assert rule.ambient == 134**480
    assert (len(rule.word.targets), len(rule.word.paid)) == (20706, 107460)
    for site, axis in ((2, 0), (5, 0), (12, 3), (30, 1)):
        raw = move_frame(site)
        assert raw.size == 8 and len(raw.mask) == 1
        for i in range(8):
            vector = [int(i == j) for j in range(8)]
            expected = [int(i == axis == j) for j in range(8)]
            assert raw.project(vector, 9) == expected
    raw = move_frame(16)
    line = (0, 1, -1, 0, 1, 0, 0, 1)
    for i in range(8):
        vector = [int(i == j) for j in range(8)]
        assert raw.project(vector, 9) == [7 * line[i] * x % 9 for x in line]

    layout = balanced_widths(2)
    dims = (48, 9, 9, 9, 9)
    data = payload(prod(dims))
    prior = {}

    def charged(s, t, digits, p, g, block):
        prior[digits] = prior.get(digits, 0) + 1
        cold_swap_tape(s, t, digits, p, g, block)

    result = BytesIO()
    base_ordinary(
        BytesIO(data), result, layout, 2, stopped_limit=2, suffix_bytes=4, previous_swap=charged
    )
    expected = expected_packet(data, dims, lambda l, h0, h1, t0, t1: (l, t0, t1, h0, h1))
    assert result.getvalue() == expected
    print(
        f"two archived base plans, true product atoms: {len(data) // 4} independent records, {prior}",
        flush=True,
    )

    layout = balanced_widths(1)
    dims = (48, 3**4, 3**4)
    data = payload(prod(dims))
    result = BytesIO()
    prior.clear()
    base_reversed(
        BytesIO(data), result, layout, 2, 2, stopped_limit=3, suffix_bytes=4, previous_swap=charged
    )

    def reverse4(x):
        return pack(unpack(x, [3] * 4)[::-1], [3] * 4)

    expected = expected_packet(data, dims, lambda l, h, t: (l, reverse4(t), reverse4(h)))
    assert result.getvalue() == expected
    print(
        f"archived two-axis plan with two aligned columns: {len(data) // 4} independent records, {prior}",
        flush=True,
    )

    layout = balanced_widths(3)
    dims = (2, 3, 81, 27, 27)
    data = payload(prod(dims))
    result = BytesIO()
    prior.clear()

    def ancestral_weight(group, old, column, axis):
        a, b, c, d = unpack(old, [3] * 4)
        g = [[1 + 3 * a, 3 * b], [3 * c, 1 + 3 * d]]
        u, v = covered_factors(((1, 1), (2, -1)), g, 2)
        return u[0] * v[0] % 9

    base_reversed(
        BytesIO(data),
        result,
        layout,
        1,
        older=81,
        stopped_limit=2,
        suffix_bytes=4,
        previous_swap=charged,
        ancestor_weights=ancestral_weight,
    )
    bases = [9, 3]

    def actual_parent_weight(old):
        a, b, c, d = unpack(old, [3] * 4)
        A, B, C, D = 1 + 3 * a, 3 * b, 3 * c, 1 + 3 * d
        return (A + B) * (2 * D + C) * pow(A * D - B * C, -1, 9) % 9

    def covered_image(low, high, old, first, second):
        weight = actual_parent_weight(old)
        h = pack(scalar(weight, unpack(second, bases), bases), bases)
        t = pack(scalar(pow(weight, -1, 9), unpack(first, bases), bases), bases)
        return low, high, old, h, t

    expected = expected_packet(data, dims, covered_image)
    assert result.getvalue() == expected
    assert {actual_parent_weight(old) for old in range(81)} == {2, 5, 8}
    print(
        f"two genuine lows, three current highs, all 81 previous highs: {len(data) // 4} independent records, {prior}",
        flush=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("predecessor", type=Path)
    run_checks(parser.parse_args().predecessor)
