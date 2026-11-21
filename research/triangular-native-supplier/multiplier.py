"""Multiply signed binary tapes through completed normalized Fourier packs."""

from io import BytesIO

from retained import install

install()

from binary_io import magnitude_bits
from outer_schedule import parameters, square_axes
from product_path import Product as RetainedProduct
from product_path import multiply_tapes as stopped_or_retained
from product_path import number, put, tensor_diagonal
from triangular_ordinary import ordinary_swap


def precision(public, extent, count):
    """Fund intervals within one normalized pack and the sum of all its endpoint errors."""
    maximum = (extent + count - 1) // count
    active = max(1, count // (1024 * (public + 1).bit_length()))
    amplification = 4096 * active * (maximum + 6)
    stages = 20000 * (count + 1) * (maximum + 2) ** 6 + 2 * count
    return (
        public
        + 3
        + 8 * amplification
        + 4 * (stages * (count + 1)).bit_length()
        + (count + 1).bit_length()
        + 64
    )


class Product(RetainedProduct):
    def __init__(self, sides, b, P, exchange=ordinary_swap, *, engine=None):
        super().__init__(sides, b, P, exchange, engine=engine)

    def transform(self, tape, opposite=False):
        def conjugate():
            tape.seek(0)
            for _ in range(self.total):
                tape.seek(self.wide, 1)
                value = number(tape, self.wide)
                tape.seek(-self.wide, 1)
                put(tape, (-value,), self.wide)

        if opposite:
            conjugate()
        for start, end, layers in self.packs:

            def diagonal(active):
                tables = self.idles.copy()
                tables[start:end] = active
                tensor_diagonal(tape, self.wide, self.grid, tables)

            diagonal(self.entrance[start:end])
            for _ in range(2):
                for layer in layers:
                    bit = layer[0][0]
                    if any(row[0] != bit for row in layer):
                        raise ArithmeticError("The pack contains different physical significances")
                    diagonal([row[1] for row in layer])
                    if bit is not None:
                        self.h(tape, start, end, bit)
            diagonal(self.exit[start:end])
        if opposite:
            conjugate()


def multiply_tapes(
    left,
    left_bytes,
    right,
    right_bytes,
    output,
    *,
    left_negative=False,
    right_negative=False,
    engine=None,
):
    """Return the sign and byte count. Preserve both signed-magnitude input intervals."""
    if output is left or output is right:
        raise ValueError("The product needs a separate output owner")
    lengths = magnitude_bits(left, left_bytes), magnitude_bits(right, right_bytes)
    shape = parameters(max(lengths))
    if shape is None:
        return stopped_or_retained(
            left,
            left_bytes,
            right,
            right_bytes,
            output,
            left_negative=left_negative,
            right_negative=right_negative,
            engine=engine,
        )
    sides = tuple(square_axes(shape.axes()))
    P = precision(shape.public, shape.extent_bits, shape.count)
    machine = Product(sides, shape.public // 6, P, engine=engine)
    sign, size, _ = machine._multiply_tapes(
        left, right, output, lengths, left_negative != right_negative, False
    )
    return sign, size


def multiply(left, right, *, engine=None):
    raw = [abs(x).to_bytes((abs(x).bit_length() + 7) // 8, "little") for x in (left, right)]
    out = BytesIO()
    sign, _ = multiply_tapes(
        BytesIO(raw[0]),
        len(raw[0]),
        BytesIO(raw[1]),
        len(raw[1]),
        out,
        left_negative=left < 0,
        right_negative=right < 0,
        engine=engine,
    )
    value = int.from_bytes(out.getvalue(), "little")
    return -value if sign else value


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description=__doc__)
    parser.add_argument("left", type=lambda x: int(x, 0))
    parser.add_argument("right", type=lambda x: int(x, 0))
    args = parser.parse_args()
    print(multiply(args.left, args.right))
