# SPDX-License-Identifier: Apache-2.0
"""Exhaustive bit-packed interpreter checks of serialized circuit templates."""

from bitadder import apply, require


def bit_column(values, index):
    require(len(values) <= 65_536, "bounded truth column")
    packed = bytearray((len(values) + 7) // 8)
    for position, value in enumerate(values):
        packed[position // 8] |= ((value >> index) & 1) << (position % 8)
    return int.from_bytes(packed, "little")


def check_truth(gates, width, numerator, denominator):
    require(1 <= width <= 8, "bounded exhaustive width")
    modulus = 1 << width
    sources, targets, expected = [], [], []
    first = -modulus // 2
    first += (-first) % denominator
    for source in range(first, modulus // 2, denominator):
        for target in range(modulus):
            sources.append(source)
            targets.append(target)
            expected.append((target + numerator * source // denominator) % modulus)
    count = len(sources)
    require(count <= 65_536, "bounded distinct aligned truth inputs")
    wires = {
        (bank, i): bit_column(values, i)
        for bank, values in (("s", sources), ("t", targets))
        for i in range(width)
    }
    wires.update({("c", i): 0 for i in range(width - 1)})
    after = apply(gates, wires, width)
    for i in range(width):
        require(after["s", i] == wires["s", i], "exhaustive source preservation")
        require(after["t", i] == bit_column(expected, i), "exhaustive modular ADD")
    require(all(after["c", i] == 0 for i in range(width - 1)), "exhaustive carries")
    return count


def decode(gates):
    require(isinstance(gates, list) and len(gates) <= 20_000, "serialized gates")
    return [(gate[0], *[tuple(wire) for wire in gate[1:]]) for gate in gates]
