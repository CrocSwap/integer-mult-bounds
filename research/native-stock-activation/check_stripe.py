"""Check unaligned bit records, preserved tape regions and a signed Fourier product."""

import argparse
from io import BytesIO
from pathlib import Path
from random import Random
import sys

from stripe_route import stripe_count, striped_exchange, striped_in_place, striped_packed_bits


def cold_binary(source, target, e, prefix, gap, piece):
    from streaming_routes import copy_bytes, erase, work_tapes

    with work_tapes(6) as (current, other, *buckets):
        copy_bytes(source, current, prefix * gap * piece << (2 * e))
        for j in range(e):
            current.seek(0)
            block = piece << (e - 1 - j)
            middle = gap << (e - 1)
            for _ in range(prefix << j):
                for a in range(2):
                    for _ in range(middle):
                        for b in range(2):
                            copy_bytes(current, buckets[2 * b + a], block)
                for b in range(2):
                    for a in range(2):
                        buckets[2 * b + a].seek(0)
                    for _ in range(middle):
                        for a in range(2):
                            copy_bytes(buckets[2 * b + a], other, block)
                for bucket in buckets:
                    erase(bucket)
            erase(current)
            current, other = other, current
        current.seek(0)
        copy_bytes(current, target, prefix * gap * piece << (2 * e))


def positions(width, prefix, gap):
    side = 1 << width
    for p in range(prefix):
        for x in range(side):
            for d in range(gap):
                for y in range(side):
                    yield ((p * side + y) * gap + d) * side + x


def abis():
    rng = Random(642188)
    tests = 0
    p, g = 2, 3
    for width in (0, 1, 4):
        count = p * g << (2 * width)
        destinations = tuple(positions(width, p, g))
        for suffix in (1, 7, 9, 13):
            for first in (0, 3, 6):
                size = (first + count * suffix + 7) // 8
                data = rng.randbytes(size)
                bits = int.from_bytes(data, "little")
                expected = bits
                mask = (1 << suffix) - 1
                for i, j in enumerate(destinations):
                    value = (bits >> (first + i * suffix)) & mask
                    dst = first + j * suffix
                    expected = (expected & ~(mask << dst)) | (value << dst)
                bank = BytesIO(b"begin" + data + b"end")
                bank.seek(5)
                striped_packed_bits(bank, width, p, g, suffix, cold_binary, first_bit=first)
                assert bank.tell() == 5
                assert bank.getvalue() == b"begin" + expected.to_bytes(size, "little") + b"end"
                tests += 1
        source = rng.randbytes(count * 5)
        bank = BytesIO(b"head" + source + b"tail")
        bank.seek(4)
        striped_exchange(bank, width, p, g, 5, cold_binary)
        assert bank.tell() == 4
        for i, j in enumerate(destinations):
            assert bank.getvalue()[4 + j * 5 : 9 + j * 5] == source[5 * i : 5 * i + 5]
        assert bank.getvalue()[:4] == b"head" and bank.getvalue()[-4:] == b"tail"
        tests += 1

    class Owner:
        def __init__(self, raw):
            self.io = BytesIO(raw)

        def seek(self, position):
            self.io.seek(position)

        def tell(self):
            return self.io.tell()

        def read(self, size):
            return self.io.read(size)

        def write(self, data):
            return self.io.write(data)

    def rewind_after(source, target, e, p, g, size):
        cold_binary(source, target, e, p, g, size)
        source.seek(0)
        target.seek(0)

    bank = Owner(b"head" + bytes(range(16)) + b"tail")
    bank.seek(4)
    striped_exchange(bank, 1, 1, 1, 4, rewind_after)
    assert bank.tell() == 4
    assert (
        bank.io.getvalue()
        == b"head" + bytes([0, 1, 2, 3, 8, 9, 10, 11, 4, 5, 6, 7, 12, 13, 14, 15]) + b"tail"
    )
    tests += 1
    print("public byte and unaligned-bit ABI cases", tests, flush=True)


def product_check(root, lib):
    from multiply import fourier
    from split_crt_product import BODY, LOWS, SplitTranspose, physical_crt

    primitive = SplitTranspose(lib)

    class StripeRows:
        stats = primitive.stats
        widths = []

        def apply(self, data, suffix):
            bank = BytesIO(data)
            # Each of the two equal fields consists of four ternary digits.
            stripes = stripe_count(4, suffix)
            self.widths.append((suffix, stripes))

            def run(source, target, width):
                target.write(primitive.apply(source.read(), width))

            striped_in_place(bank, LOWS * BODY, suffix, stripes, run)
            return bank.getvalue()

    rows = StripeRows()

    class Product(fourier().Multiplier):
        def crt(self, field, reverse=False):
            return physical_crt(self, field, rows, reverse)

    # The wider private grid gives more than a byte per true low, even on inverse CRT.
    machine = Product((3, 5), 8, 384, source_root=root)
    value, coefficients = machine.multiply(741503, 466013)
    assert value == 345550037539
    assert coefficients == [11811, 10996, 4152, 868, 77] + [0] * 10
    assert rows.widths == [(3, 2)] * 4 + [(2, 2)] * 2
    assert rows.stats["forward_crt"] == 2 and rows.stats["inverse_crt"] == 1
    print(
        "striped numerical product",
        value,
        "record bytes and stripe counts",
        rows.widths,
        flush=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("predecessor", type=Path)
    parser.add_argument("root", type=Path)
    parser.add_argument("product_evidence", type=Path)
    parser.add_argument("library", type=Path)
    args = parser.parse_args()
    sys.path[:0] = [str(args.predecessor.resolve()), str(args.product_evidence.resolve())]
    abis()
    product_check(args.root.resolve(), args.library.resolve())
