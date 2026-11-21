"""Use striped CRTs and every complete striped numerical H in a Fourier product."""

import argparse
from collections import Counter
from io import BytesIO
from itertools import combinations
from pathlib import Path
from random import Random
import sys

from striped_tensor import crt_tape, hadamard_tape, hadamard_words, spectator_layout


def execute(predecessor, root, finite_product, library):
    sys.path[:0] = [str(predecessor), str(finite_product)]
    from multiply import fourier

    numerical = fourier()
    from tensor_word import hadamard, product_diagonal
    from split_crt_product import SplitTranspose, physical_crt

    rng = Random(124781)
    width = (2, 3, 2)
    words = [rng.randrange(-10000, 10000) for _ in range(1 << sum(width))]
    source = b"".join(i.to_bytes(4, "little", signed=True) for i in words)
    cases = 0
    for selected in combinations(range(sum(width)), 2):

        def apply(src, dst, kept_width, picked, size):
            row = [
                (int.from_bytes(src.read(size), "little", signed=True), 0)
                for _ in range(1 << kept_width)
            ]
            hadamard(row, (1 << j for j in picked))
            for x, _ in row:
                dst.write(x.to_bytes(size, "little", signed=True))

        bank = BytesIO(b"head" + source + b"tail")
        bank.seek(4)
        hadamard_tape(bank, width, selected, 48, 4, apply)
        expected = [(x, 0) for x in words]
        hadamard(expected, (1 << j for j in selected))
        result = b"".join(x.to_bytes(4, "little", signed=True) for x, _ in expected)
        assert bank.tell() == 4 and bank.getvalue() == b"head" + result + b"tail"
        cases += 1
    print("arbitrary guarded numerical H tape comparisons", cases, flush=True)

    primitive = SplitTranspose(library)
    counts = Counter()

    class Tensor:
        def __init__(self, original, public_bits):
            self.original = original
            self.widths = tuple(t.bit_length() - 1 for t in original.sides)
            self.stripe_bits = (public_bits + 1).bit_length() // 2
            self.plans = {}

        def apply(self, values, opposite=False):
            old = self.original
            data = [(a, -b) for a, b in values] if opposite else list(values)
            product_diagonal(data, old.entrance, old.grid)
            for schedule in old.jobs:
                for _ in range(2):
                    for tables, target in schedule:
                        product_diagonal(data, tables, old.grid)
                        if target:
                            if target not in self.plans:
                                selected = tuple(x.bit_length() - 1 for x in target)
                                self.plans[target] = spectator_layout(
                                    self.widths, selected, self.stripe_bits
                                )
                            layout = self.plans[target]
                            hadamard_words(data, layout, hadamard)
                            counts["H_" + str(layout.stripes) + "_stripes"] += 1
            product_diagonal(data, old.exit, old.grid)
            return [(a, -b) for a, b in data] if opposite else data

    class Product(numerical.Multiplier):
        def crt(self, field, reverse=False):
            scalar = isinstance(field[0], int)
            channels = 1 if scalar else 2
            size = (self.grid.bits + 4 + 7) // 8
            word = channels * size
            stripes = min(word, 1 << ((self.public_bits + 1).bit_length() // 2))
            raw = (x for item in field for x in ((item,) if scalar else item))
            bank = BytesIO(b"".join(x.to_bytes(size, "little", signed=True) for x in raw))

            def route(source, target, chunk):
                parts = [int.from_bytes(source.read(chunk), "little") for _ in field]
                placed = physical_crt(self, parts, primitive, reverse)
                for part in placed:
                    target.write(part.to_bytes(chunk, "little"))

            crt_tape(bank, len(field), word, self.public_bits, route)
            result = []
            for _ in field:
                components = tuple(
                    int.from_bytes(bank.read(size), "little", signed=True) for _ in range(channels)
                )
                result.append(components[0] if scalar else components)
            counts["inverse_CRT" if reverse else "forward_CRT"] += 1
            counts["CRT_stripes"] += stripes
            return result

    machine = Product((3, 5), 8, 136, source_root=root)
    machine.transform = Tensor(machine.transform, machine.public_bits)
    value, coeffs = machine.multiply(741503, 466013)
    assert value == 345550037539 and coeffs == [11811, 10996, 4152, 868, 77] + [0] * 10
    assert counts["H_4_stripes"] + counts["H_8_stripes"] == 3 * 52416
    assert counts["forward_CRT"] == 2 and counts["inverse_CRT"] == 1 and counts["CRT_stripes"] == 24
    print(
        "all-striped Fourier product", value, "CRT, H and carry", sorted(counts.items()), flush=True
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("predecessor", type=Path)
    parser.add_argument("root", type=Path)
    parser.add_argument("product_evidence", type=Path)
    parser.add_argument("library", type=Path)
    args = parser.parse_args()
    execute(
        args.predecessor.resolve(),
        args.root.resolve(),
        args.product_evidence.resolve(),
        args.library.resolve(),
    )
