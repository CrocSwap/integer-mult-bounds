"""Check the finite split-atom swap and its use by two forward CRTs and the inverse."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
from pathlib import Path
from random import Random
import sys

from split_crt_product import BODY, LOWS, SIDE, SplitTranspose, physical_crt


def reference_crt(field, sides, widths, reverse):
    a, b = sides
    nx, ny = widths
    result = [None] * len(field)
    for y in range(ny):
        for x in range(nx):
            offset = (0 if x >= a else x) * pow(a, -1, b)
            dy = (y + (-offset if reverse else offset)) % b if y < b else y
            result[dy * nx + x] = field[y * nx + x]
    return result


def leaf_check(transpose):
    """Check each low before the complementary boundary can cancel an error."""
    source = b"".join(i.to_bytes(2, "little") for i in range(BODY))
    low = 0
    for a, b, c, d in product(range(3), repeat=4):
        det = (a * d - b * c) % 3
        if not det:
            continue
        h = pow(det, -1, 3)
        u, v = (a, c), (d * h, -b * h)
        out = bytearray(source)
        transpose.run(out, 2, transpose.programs[low][0])
        for i, coordinates in enumerate(product(range(3), repeat=8)):
            dest = list(coordinates)
            for j in (0, 1):
                change = v[0] * (coordinates[6 + j] - coordinates[j])
                change += v[1] * (coordinates[4 + j] - coordinates[2 + j])
                for k, factor in enumerate(u):
                    dest[2 * k + j] = (coordinates[2 * k + j] + factor * change) % 3
                    t = 6 - 2 * k + j
                    dest[t] = (coordinates[t] - factor * change) % 3
            index = 0
            for digit in dest:
                index = 3 * index + digit
            assert int.from_bytes(out[2 * index : 2 * index + 2], "little") == i
        low += 1
    assert low == LOWS
    print("independent rank-one checks", low * BODY, "addresses", flush=True)


def check(predecessor, root, library, *, product_only=False):
    sys.path.insert(0, str(predecessor))
    from multiply import fourier

    base = fourier()
    transpose = SplitTranspose(library)

    if not product_only:
        leaf_check(transpose)
        transpose.stats.clear()
        suffix = 3
        source = Random(688526).randbytes(LOWS * BODY * suffix)
        result = transpose.apply(source, suffix)
        for owner in range(LOWS):
            for x in range(SIDE):
                for y in range(SIDE):
                    old = (owner * BODY + y * SIDE + x) * suffix
                    new = (owner * BODY + x * SIDE + y) * suffix
                    assert result[new : new + suffix] == source[old : old + suffix]
        print(
            "arbitrary swap",
            len(source) // suffix,
            "three-byte records",
            sha256(result).hexdigest(),
            flush=True,
        )
        print("swap counts", sorted(transpose.stats.items()), flush=True)

    class Product(base.Multiplier):
        def crt(self, field, reverse=False):
            output = physical_crt(self, field, transpose, reverse)
            assert output == reference_crt(field, self.sides, self.widths, reverse)
            self.changed += sum(old != new for old, new in zip(field, output, strict=True))
            return output

    machine = Product((3, 5), 8, 136, source_root=root)
    machine.changed = 0
    if not product_only:
        dirty = [(i * (1 << 127) - 19, -i * (1 << 125) + 7) for i in range(32)]
        changed = machine.crt(dirty)
        assert changed != dirty and machine.crt(changed, True) == dirty

        class Idle:
            stats = Counter()

            @staticmethod
            def apply(data, suffix):
                return data

        try:
            unswitched = physical_crt(machine, dirty, Idle(), False)
        except ArithmeticError as error:
            assert "dirty retired" in str(error)
        else:
            assert unswitched != changed
        print("omitting both placements fails the dirty CRT check", flush=True)
    transpose.stats.clear()
    machine.changed = 0
    cases = (
        [(741503, 466013)]
        if product_only
        else [
            (741503, 466013),
            (-65535, 65535),
            (0, (1 << 64) - 1),
            ((1 << 55) - 1, -(1 << 59) + 37),
        ]
    )
    for a, b in cases:
        value, coefficients = machine.multiply(a, b)
        assert value == a * b
        da = [(abs(a) >> (8 * k)) & 255 for k in range((abs(a).bit_length() + 7) // 8)]
        db = [(abs(b) >> (8 * k)) & 255 for k in range((abs(b).bit_length() + 7) // 8)]
        expected = [0] * 15
        for i, u in enumerate(da):
            for j, v in enumerate(db):
                expected[i + j] += u * v
        assert coefficients == expected
        print("product", a, b, value, "coefficients", coefficients, flush=True)
    assert machine.changed and transpose.stats["forward_crt"] == 2 * len(cases)
    assert transpose.stats["inverse_crt"] == len(cases)
    assert transpose.stats["right_routes"] == 24 * len(cases)
    assert transpose.stats["leading_leaves"] > 0 and transpose.stats["nonleading_leaves"] > 0
    print(
        "product counts",
        sorted(transpose.stats.items()),
        "changed CRT entries",
        machine.changed,
        flush=True,
    )
    print("complete H calls per transform", machine.transform.h_calls, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("predecessor", type=Path)
    parser.add_argument("source_root", type=Path)
    parser.add_argument("library", type=Path)
    parser.add_argument("--product-only", action="store_true")
    args = parser.parse_args()
    check(
        args.predecessor.resolve(),
        args.source_root.resolve(),
        args.library.resolve(),
        product_only=args.product_only,
    )
