"""Compare the direct physical routes with dense rational coordinate actions."""

from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from functools import cache
from io import BytesIO
from math import prod
from pathlib import Path
import sys


def main():
    parser = ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("predecessor", type=Path)
    args = parser.parse_args()
    sys.path.extend((str(args.source.resolve()), str(args.predecessor.resolve())))
    from check_module_atoms import expected_packet, payload
    from direct_body import direct_line, direct_route
    from factored_frames import Frame, inverse_word
    from growing_binary import Weighted
    from module_atoms import component_widths
    from same_order_body import SameOrderBody
    from streaming_routes import cold_swap_tape
    from ternary_frames import identity, inverse, multiply, residue

    calls = Counter()

    def previous(src, dst, digits, prefix, gap, suffix):
        calls[digits] += 1
        cold_swap_tape(src, dst, digits, prefix, gap, suffix)

    class DirectBase(SameOrderBody, Weighted):
        def __init__(self, n, layout):
            super().__init__(n, layout, previous)
            self.stock = self.owners

    def direct_model(matrix, model, f, widths, old, values):
        n = len(matrix)
        sides = [3**w for w in widths]

        @cache
        def split(x):
            remain = x
            parts = [0] * len(sides)
            for i in reversed(range(len(sides))):
                remain, parts[i] = divmod(remain, sides[i])
            return parts

        out = [0] * len(values)
        for side_index, q in enumerate(sides):
            coeffs = [[residue(c, q) for c in row] for row in matrix]
            for j in range(f):
                a = [model(old, k * f + j, q) for k in range(n)]
                for h, x in enumerate(coeffs):
                    r = (
                        sum(
                            c * split(values[k * f + j])[side_index] * pow(a[k], -1, q)
                            for k, c in enumerate(x)
                        )
                        % q
                    )
                    off = h * f + j
                    out[off] = out[off] * q + r * a[h] % q
        return tuple(out)

    def weight(old, axis, modulus=81):
        units = (1, 2, 4, 5, 7, 8)
        return units[(3 * old + axis) % len(units)] % modulus

    def ones(_old, _axis, _q):
        return 1

    word = (
        ("add", 0, 1, Fraction(-1, 2)),
        ("scale", 1, Fraction(-5, 4)),
        ("swap", 0, 1),
        ("add", 1, 0, Fraction(5, 7)),
        ("scale", 0, Fraction(2, 5)),
    )
    cases = (
        (2, 1, (1, 1, 0, 0), word),
        (3, 1, (1, 1, 0, 0), word + (("add", 2, 1, Fraction(-2, 5)),)),
        (2, 2, (1, 1, 0, 0), word),
        (2, 1, (1, 2, 0, 0), word),
        (2, 1, (2, 1, 0, 0), word),
    )
    for n, f, layout, program in cases:
        core = DirectBase(n, layout)
        w = list(component_widths(layout))
        A = 3 ** sum(w)
        specs = [identity(n) for _ in program]
        S = identity(n)
        for E, (kind, i, *d) in zip(specs, program, strict=True):
            if kind == "add":
                E[d[0]][i] = d[1]
            elif kind == "swap":
                E[i], E[d[0]] = E[d[0]], E[i]
            else:
                E[i][i] = d[0]
            S = multiply(S, E)
        mat = inverse(S)

        @cache
        def dest(bank, old, coordinates):
            return direct_model(mat, weight if bank == "H" else ones, f, w, old, coordinates)

        dims = (2, 2) + (A,) * (n * f) + (2,) + (A,) * (n * f)

        def mapped(unused, old, *body):
            return (
                unused,
                old,
                *dest("H", old, tuple(body[: n * f])),
                body[n * f],
                *dest("T", old, tuple(body[n * f + 1 :])),
            )

        data = payload(prod(dims))
        # Change each reached address before undo. A paired false identity would fail here.
        entered = BytesIO()
        calls.clear()
        direct_route(core, BytesIO(data), entered, program, f, 2, 2, 2, 4, weight)
        assert entered.getvalue() == expected_packet(data, dims, mapped)
        changed = bytearray(entered.getvalue())
        for i in range(0, len(changed), 4):
            changed[i] ^= (i // 4 * 119 + 11) % 256
        back = BytesIO()
        direct_route(
            core, BytesIO(changed), back, tuple(inverse_word(program)), f, 2, 2, 2, 4, weight
        )
        assert expected_packet(back.getvalue(), dims, mapped) == changed
        print(
            "body",
            n,
            f,
            w,
            prod(dims),
            "records",
            dict(calls),
            "earlier swaps",
            core.last_storage,
            flush=True,
        )

    # A real rank-one site can bypass all entrance and exit matching in the direct mode.
    n, f = 3, 1
    core = DirectBase(n, (1, 1, 0, 0))
    frame = Frame(n, word + (("add", 1, 2, Fraction(2)),), (1,))
    dims = (2, 2) + (3,) * n + (2,) + (3,) * n
    data = payload(prod(dims))
    got = BytesIO()
    calls.clear()
    direct_line(core, BytesIO(data), got, frame, f, 2, 2, 2, 4, weight)
    u, v = frame.covered_line(identity(3), 1)

    def placed(r, old, *body):
        h, g, t = body[:n], body[n], body[n + 1 :]
        a = [weight(old, j, 3) for j in range(n)]
        delta = sum(
            vv * (tt - pow(aa, -1, 3) * hh) for vv, tt, aa, hh in zip(v, t, a, h, strict=True)
        )
        return (
            r,
            old,
            *((x + aa * uu * delta) % 3 for x, aa, uu in zip(h, a, u, strict=True)),
            g,
            *((x - uu * delta) % 3 for x, uu in zip(t, u, strict=True)),
        )

    assert got.getvalue() == expected_packet(data, dims, placed)
    print(
        "non-coordinate compiled line",
        prod(dims),
        "records",
        dict(calls),
        "earlier swaps",
        core.last_storage,
    )


if __name__ == "__main__":
    main()
