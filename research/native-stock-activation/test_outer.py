"""Check the controller inequalities and trace two pinned source circuits."""

import json
from math import gcd, prod
from pathlib import Path
import sys
from outer_schedule import (
    Shape,
    ceil_log2,
    exponent_receipt,
    first_mixing_layer,
    in_physical_source,
    periodic_source,
    source_placement,
    square_axes,
)


def all_shape_checks():
    verified = 0
    for exponent in range(31, 1537):
        for offset in (0, 1, 4, 7):
            p = (1 << exponent) + offset
            s = ceil_log2(p + 2)
            length = p // 12
            width = 64 * s * s
            count = 1 << ((length // width).bit_length() - 1)
            sh = Shape(p, length, count)
            ell = (length + count - 1) // count
            prec = sh.precision()
            sp = ceil_log2(prec + 2)
            assert ell <= 128 * s * s
            assert prec < (1 << 20) * p
            # The interval has more bases than the sieve can reject.
            assert width // 2 - 6 - s >= 3 + s * (8 * s + 2)
            if s < 64:
                continue
            assert sp <= s + 20
            g = 4 * sp + 6
            assert g <= 6 * s
            k = 128 * g
            assert k <= width
            h = max(1, count // (1024 * s))
            support = 2 * h * k
            assert 2 * (support + 1) * sp**2 < length
            assert 9 * support * g + sp**2 < length
            cguard, rmax, field = sh.crt_control()
            if s < 512:
                continue
            assert field * 101 >= length
            # Bound the entire packet even at the maximal possible log2(M)=s.
            body = h * ell
            rows = 448 * (4 * s + 1)
            payload = body + rows + 3 * h * g + sp**2
            sliced = length - s // 2
            assert 4 * payload < length and (sliced - body) // 2 >= payload
            assert field <= length // 100
            assert rmax * 51200 >= count
            assert count // 2 > (1 << 46) * ell**3
            number_of_mixing_depths = 40000 * (ell + 2) ** 6
            guaranteed = min(h, count // (2 * number_of_mixing_depths))
            assert guaranteed >= 1 << (s - 100 - 16 * ceil_log2(s))
            assert (1 << 48) * (s + 1) ** 6 < 1 << (s - 9)
            verified += 1
    return verified


def source_cases(root, package):
    sys.path.insert(0, str(package))
    from root_gate_plan import load_compiler
    from spectral import fourier_axis
    from square_geometry import select_squares
    from product import Multiplier

    compiler = load_compiler(root)
    tracings = []
    for r, t in ((3, 4), (5, 8)):
        for direction in (-1, 1):
            axis = fourier_axis(compiler, r, t, direction, 60)
            tag = first_mixing_layer(axis.layers)
            # Propagate a true unit column independently, through the two passes.
            state = compiler.exact.Vec([1] + [0] * (t - 1))
            first = None
            for rep in (0, 1):
                for j, gates in enumerate(axis.layers):
                    state, _ = compiler.exact.apply([gates], state)
                    if first is None and sum(z != 0 for z in state) > 1:
                        first = rep, j
            assert tag == first
            tracings.append([r, t, direction, *tag])
    # Every wire initially contains a distinct value in the retained route
    # test. The final product test uses two true operands and the two-root word.
    machine = Multiplier((5, 7), 8, 136, source_root=root)
    assert machine.multiply(741503, 466013)[0] == 345550037539
    squares = 0
    for width in (20, 21, 24, 26, 27, 28, 31, 38, 51, 66, 96):
        ws = (width + 1,) * 3 + (width,) * 5
        reference = select_squares(ws)
        try:
            ours = tuple(square_axes(ws))
        except ValueError:
            assert reference is None
            continue
        assert list(ours) == reference
        assert all(gcd(r, prod(ours[:i])) == 1 for i, r in enumerate(ours))
        assert 4 * prod(ours) >= 3 * (1 << sum(ws))
        squares += len(ours)
    return tracings, squares


def placement_checks():
    tested = 0
    for rank in range(20, 269):
        for source in range(5, rank // 4 + 1):
            period = 1 << ceil_log2((4 * (rank // 4) + source - 1) // source)
            for j in range(period):
                selected = list(periodic_source(rank, source, j))
                assert all(a < b for a, b in zip(selected, selected[1:]))
                assert selected[-1] - selected[0] + 1 > len(selected)
                slots = list(range(rank))
                route = source_placement(rank, selected)
                assert route
                for a, b in route:
                    slots[a], slots[b] = slots[b], slots[a]
                assert slots[:source] == selected
                for a, b in reversed(route):
                    slots[a], slots[b] = slots[b], slots[a]
                assert slots == list(range(rank))
                tested += 1

    def swap(data, a, b, width):
        locations = (1 << width) - 1
        result = [None] * len(data)
        for pos, value in enumerate(data):
            bits = ((pos >> a) ^ (pos >> b)) & locations
            result[pos ^ (bits << a) ^ (bits << b)] = value
        return result

    def apply_positive(data, bits):
        # Use twice the native C, with exact arbitrary Gaussian integer inputs.
        out = list(data)
        for bit in bits:
            step = 1 << bit
            previous = out
            out = []
            for i, (a, b) in enumerate(previous):
                c, d = previous[i ^ step]
                out.append((a - b + c + d, a + b - c + d))
        return out

    # Every K-1 neighbor and every unselected slot has independent test data.
    for rank, repeated, window in ((8, 1, 2), (8, 2, 1), (4, 2, 2)):
        data = [(i - 30, 2 * i + 1) for i in range(1 << (rank * repeated * window))]
        for j in range(4):
            selected = tuple(periodic_source(rank, rank // 4, j))
            before = list(data)
            actual = in_physical_source(
                data,
                selected,
                rank,
                repeated,
                window,
                swap,
                lambda field, active: apply_positive(field, (i * window for i in range(active))),
            )
            expected = apply_positive(
                data, ((a * repeated + c) * window for a in selected for c in range(repeated))
            )
            assert actual == expected and before == data
    return tested


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("pinned_fourier_package", type=Path)
    opts = parser.parse_args()
    traces, squares = source_cases(opts.repo.resolve(), opts.pinned_fourier_package.resolve())
    binary_rank = 240000000000000
    bottom = (25000 * (2 * binary_rank + 12) + 24902) // 24903
    top = bottom + 5 * (2 * binary_rank + 12)
    result = {
        "exact_controller_shape_checks": all_shape_checks(),
        "genuine_branch_source_cases": traces,
        "admitted_source_squares": squares,
        "two_root_product": 345550037539,
        "finite_product_method": "retained numerical gate interpreter",
        "noncontiguous_genuine_source_placements": placement_checks(),
        "outer_receipt_at_p_4096_E6": exponent_receipt(top + 13, binary_rank, 3300000000, top),
        "strong_connected_receipt_at_p_N16": exponent_receipt(
            16 * binary_rank + 1, binary_rank, 3300000000, top
        ),
    }
    print(json.dumps(result, indent=2))
