"""Compare full sequential packets with independently calculated address permutations."""

import argparse
import sys
from fractions import Fraction
from io import BytesIO
from itertools import product
from math import prod
from pathlib import Path


def payload(records):
    return b"".join(
        ((i * 2654435761 + 1701) % (1 << 32)).to_bytes(4, "big") for i in range(records)
    )


def unpack(index, bases):
    digits = []
    for base in reversed(bases):
        index, remainder = divmod(index, base)
        digits.append(remainder)
    assert index == 0
    return list(reversed(digits))


def pack(digits, bases):
    index = 0
    for value, base in zip(digits, bases, strict=True):
        assert 0 <= value < base
        index = index * base + value
    return index


def expected_packet(data, dims, destination):
    expect = bytearray(len(data))
    seen = set()
    for source, value in enumerate(product(*(range(x) for x in dims))):
        target = pack(destination(*value), dims)
        assert target not in seen
        seen.add(target)
        expect[4 * target : 4 * target + 4] = data[4 * source : 4 * source + 4]
    assert len(seen) == len(data) // 4
    return expect


def scalar(value, x, bases):
    return [value * t % q for t, q in zip(x, bases, strict=True)]


def add(x, y, bases):
    return [(a + b) % q for a, b, q in zip(x, y, bases, strict=True)]


def run(predecessor):
    sys.path.insert(0, str(predecessor.resolve()))
    from module_atoms import (
        balanced_widths,
        chart_width,
        component_widths,
        lower_tape,
        ordinary_shell,
        rank_one_column,
        stage_layout,
        weighted_pair,
    )
    from streaming_routes import cold_swap_tape, regular, right_route, work_tapes
    from ternary_frames import covered_factors

    for w in range(1, 110):
        for floor in range(1, w + 1):
            shape = balanced_widths(w, floor)
            sizes = list(component_widths(shape))
            assert sum(sizes) == w and max(sizes) - min(sizes) <= 1
            assert max(sizes) == chart_width(shape)
            assert w**97 <= (2 * max(sizes)) ** 100
            assert min(sizes) >= floor
            assert chart_width(stage_layout(w**250, floor - 1)) == max(sizes)

    lower_cases = pair_cases = lower_records = 0
    for w in (1, 2, 3, 4):
        shape = balanced_widths(w)
        bases = [3**t for t in component_widths(shape)]
        side = prod(bases)
        dims = (2, side, 3, side, 2)
        data = payload(prod(dims))
        for multiplier in ([2, -3], [4, 7]):

            def move(p, x, d, y, s):
                result = add(
                    unpack(y, bases), scalar(multiplier[p], unpack(x, bases), bases), bases
                )
                return (p, x, d, pack(result, bases), s)

            out = BytesIO()
            lower_tape(BytesIO(data), out, shape, 2, 3, 8, lambda p: multiplier[p])
            assert out.getvalue() == expected_packet(data, dims, move)
            lower_cases += 1
            lower_records += prod(dims)
        if w <= 3:
            weights = (2, 4)
            calls = []

            def previous(s, t, digits, p, g, block):
                calls.append((digits, p, g, block))
                cold_swap_tape(s, t, digits, p, g, block)

            def swap(p, x, d, y, s):
                a = weights[p]
                first = pack(scalar(a, unpack(y, bases), bases), bases)
                second = pack(scalar(pow(a, -1, max(bases)), unpack(x, bases), bases), bases)
                return p, first, d, second, s

            out = BytesIO()
            weighted_pair(BytesIO(data), out, shape, 2, 3, 8, lambda p: weights[p], previous)
            assert out.getvalue() == expected_packet(data, dims, swap)
            assert calls == [(w, 2, 3, 8)] * 2
            pair_cases += 1

    leaf_cases = leaf_records = leaf_children = 0
    for w, native, low, weights in (
        (2, ((1, 0), (1, 0)), [[0, 1], [1, 0]], (2, 1)),
        (2, ((1, 1), (2, -1)), [[1, 1], [0, 1]], (1, 2)),
        (1, ((1, 1), (2, -1)), [[0, 1], [1, 1]], (2, 2)),
        (3, ((1, 1), (2, -1)), [[1, 3], [0, 1]], (4, 7)),
    ):
        shape = balanced_widths(w)
        bases = [3**t for t in component_widths(shape)]
        side = prod(bases)
        exponent = chart_width(shape)
        u, v = covered_factors(native, low, exponent)
        n = len(u)
        dims = [side] * (2 * n)
        data = payload(prod(dims))
        calls = []

        def previous(s, t, digits, p, g, block):
            calls.append(digits)
            cold_swap_tape(s, t, digits, p, g, block)

        def target(*values):
            by_component = [unpack(value, bases) for value in values]
            for j, q in enumerate(bases):
                head = [by_component[i][j] * pow(weights[i], -1, q) % q for i in range(n)]
                tail = [by_component[2 * n - 1 - i][j] for i in range(n)]
                change = sum(vi * (y - x) for vi, y, x in zip(v, tail, head, strict=True))
                for i in range(n):
                    by_component[i][j] = weights[i] * (head[i] + u[i] * change) % q
                    by_component[2 * n - 1 - i][j] = (tail[i] - u[i] * change) % q
            return [pack(value, bases) for value in by_component]

        out = BytesIO()
        rank_one_column(BytesIO(data), out, shape, u, v, weights, 4, previous)
        assert out.getvalue() == expected_packet(data, dims, target)
        pivot = next(i for i, (x, y) in enumerate(zip(u, v, strict=True)) if x * y % 3)
        assert calls == [w] * (18 if pivot else 2)
        leaf_cases += 1
        leaf_records += prod(dims)
        leaf_children += len(calls)

    # A real full chart at u=2, used by the different-sized (2,1)-trit components.
    shape = balanced_widths(3, 1)
    assert tuple(component_widths(shape)) == (2, 1)
    u = chart_width(shape)
    lows = [m for m in product(range(3), repeat=4) if regular(m, 2)]
    highs = list(product(range(3), repeat=4))
    dims = [len(lows), len(highs), 2]
    data = payload(prod(dims))
    word = [("add", 1, 0, Fraction(1, 2)), ("swap", 0, 1)]
    inverse = [("swap", 0, 1), ("add", 1, 0, Fraction(-1, 2))]

    def route(l, h, s):
        mat = [(v + 3 * a) % 9 for v, a in zip(lows[l], highs[h], strict=True)]
        x, y, z, t = mat
        result = ((y + 5 * x) % 9, x, (t + 5 * z) % 9, z)
        low = tuple(v % 3 for v in result)
        high = tuple(v // 3 for v in result)
        return lows.index(low), highs.index(high), s

    out = BytesIO()
    right_route(BytesIO(data), out, 2, u, 1, 8, word, previous_swap=cold_swap_tape)
    assert out.getvalue() == expected_packet(data, dims, route)
    restored = BytesIO()
    right_route(
        BytesIO(out.getvalue()), restored, 2, u, 1, 8, inverse, previous_swap=cold_swap_tape
    )
    assert restored.getvalue() == data
    # The old scalar ring has 81 times as many lifts per true low at this finite point.
    assert 3 ** (4 * (3 - 1)) // len(highs) == 81

    # Each F is the chronological product for two complementary, disjoint projections.
    # Both calls execute the full native column and its actual stopped children.
    shape = balanced_widths(2)
    dims = (9, 9, 3, 9, 9)
    data = payload(prod(dims))
    prior_calls = []

    def previous(s, t, digits, p, g, block):
        prior_calls.append(digits)
        cold_swap_tape(s, t, digits, p, g, block)

    def reverse(s, t):
        with work_tapes(1) as (mid,):
            rank_one_column(s, mid, shape, [1, 0], [1, 0], [1, 1], 4, previous, gap=3)
            mid.seek(0)
            rank_one_column(mid, t, shape, [0, 1], [0, 1], [1, 1], 4, previous, gap=3)

    ordinary = BytesIO()
    ordinary_shell(BytesIO(data), ordinary, shape, 2, 1, 3, 4, reverse)
    direct = expected_packet(data, dims, lambda a, b, d, c, e: (c, e, d, a, b))
    assert ordinary.getvalue() == direct
    assert prior_calls == [2] * 40
    print(f"lower passes: {lower_cases} packets, {lower_records} independent records")
    print(f"weighted pairs: {pair_cases} packets, two whole-atom swaps per packet")
    print(
        f"native leaves: {leaf_cases} packets, {leaf_records} records, {leaf_children} preceding swaps"
    )
    print(
        f"lifted chart: {len(lows)} genuine lows x {len(highs)} highs x 2 records, forward and inverse"
    )
    print(
        f"ordinary shell: {len(direct) // 4} records, two full returns, {len(prior_calls)} preceding swaps"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("predecessor", type=Path)
    run(parser.parse_args().predecessor)
