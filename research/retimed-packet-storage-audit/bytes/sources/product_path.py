"""Multiply signed binary integers with the thin square geometry and the stock-funded services."""

from contextlib import ExitStack, closing
from functools import cache, partial
from io import BytesIO
from pathlib import Path
from itertools import accumulate
from math import prod
from tempfile import TemporaryFile

from source_inputs import activate

PRIOR, SOURCES = activate()

from complex_stage import native_h
from binary_io import carry_to_tape, magnitude_bits, magnitude_limbs
from crt_tree import CRTTree
from ordinary import ordinary_swap
from outer_schedule import first_mixing_layer, parameters, square_axes
from striped_tensor import crt_tape, hadamard_tape
from streaming_routes import erase, read_exact
from multiply import fourier, signed_leaf
from short_product import native_product
from spool import Field, transfer


@cache
def installed_scalar():
    library = Path(__file__).resolve().with_name("short_product.so")
    return native_product(library) if library.is_file() else None


def scalar_product(engine):
    engine = installed_scalar() if engine is None else engine
    return fourier().word_product if engine is None else partial(signed_leaf, engine=engine)


def number(stream, size):
    return int.from_bytes(read_exact(stream, size), "little", signed=True)


def put(stream, z, size):
    for x in z:
        stream.write(x.to_bytes(size, "little", signed=True))


def original_positions(sides, widths):
    extents = tuple(1 << x for x in widths)
    coords = [0] * len(sides)
    for _ in range(prod(extents)):
        yield all(x < r for x, r in zip(coords, sides, strict=True))
        for j, cap in enumerate(extents):
            coords[j] += 1
            if coords[j] < cap:
                break
            coords[j] = 0


def truncate(x, shift):
    return (1 if x >= 0 else -1) * (abs(x) >> shift)


def tensor_diagonal(tape, size, grid, tables):
    sides = [len(v) for v in tables]
    total = prod(sides)
    suffix = [grid.one] * (len(sides) + 1)
    pos = [0] * len(sides)
    for j in range(len(sides) - 1, 0, -1):
        suffix[j] = grid.multiply(tables[j][0], suffix[j + 1])
    tape.seek(0)
    for i in range(total):
        diagonal = grid.multiply(tables[0][pos[0]], suffix[1])
        if diagonal == grid.one:
            tape.seek(2 * size, 1)
        else:
            z = (number(tape, size), number(tape, size))
            tape.seek(-2 * size, 1)
            put(tape, grid.multiply(diagonal, z), size)
        if i + 1 < total:
            j = 0
            while pos[j] + 1 == sides[j]:
                pos[j] = 0
                j += 1
            pos[j] += 1
            for k in range(j, 0, -1):
                suffix[k] = grid.multiply(tables[k][pos[k]], suffix[k + 1])


class Product:
    def __init__(self, sides, b, P, exchange=ordinary_swap, *, engine=None):
        if b < 5 or P < 6 * b or not sides or len(sides) & (len(sides) - 1):
            raise ValueError("Invalid public precision or square tensor shape")
        package = fourier()
        from tensor_word import local_schedule

        compiler = package.load_compiler(SOURCES)
        routes = package.load_routes(SOURCES)
        self.grid = package.Grid(P, scalar_product(engine))
        self.b, self.p, self.P = b, 6 * b, P
        self.exchange = exchange
        records = []
        for side in sides:
            bits = (side - 1).bit_length()
            axis = package.fourier_axis(compiler, side, 1 << bits, -1, P + 8)
            key = (-bits, first_mixing_layer(axis.layers))
            records.append((key, side, axis))
        records.sort(key=lambda row: row[0])
        self.sides = tuple(row[1] for row in records)
        self.widths = tuple(-row[0][0] for row in records)
        self.size = prod(sides)
        if self.size > 1 << b:
            raise ValueError("The true tensor exceeds its public radix")
        self.total = 1 << sum(self.widths)
        self.starts = list(accumulate(self.widths, initial=0))
        self.tree = CRTTree(self.sides, self.widths, self.p, routes.benes, exchange)
        self.wide = (2 * P + 40 + 7) // 8
        self.short = (self.p + 4 + 7) // 8
        self.h_calls = 0
        self.entrance = [tuple(map(self.grid.word, a.entrance)) for _, _, a in records]
        self.exit = [tuple(map(self.grid.word, a.exit)) for _, _, a in records]
        self.idles = [(self.grid.one,) * (1 << ell) for ell in self.widths]
        limit = max(1, len(sides) // (1024 * (self.p + 1).bit_length()))
        self.packs = []
        start = 0
        while start < len(records):
            end = start + 1
            key = records[start][0]
            while end < len(records) and end - start < limit and records[end][0] == key:
                end += 1
            axes = [r[2] for r in records[start:end]]
            depth = max(len(a.layers) for a in axes)
            words = [local_schedule(a, depth, compiler, routes, self.grid) for a in axes]
            self.packs.append((start, end, tuple(zip(*words, strict=True))))
            start = end

    def write_operand(self, tape, source, length):
        with closing(magnitude_limbs(source, length, self.b)) as stream:
            for valid in original_positions(self.sides, self.widths):
                digit = next(stream, 0) if valid else 0
                put(tape, (digit << (self.P - self.b - 2), 0), self.wide)
            if next(stream, None) is not None:
                raise ValueError("The true tensor lacks input coefficient positions")
        tape.seek(0)
        crt_tape(tape, self.total, 2 * self.wide, self.p, lambda s, d, w: self.tree.apply(s, d, w))

    def h(self, tape, start, end, bit):
        positions = tuple(self.starts[i] + bit for i in range(start, end))

        def one(s, d, L, selected, record):
            if end - start != len(selected):
                raise ArithmeticError("The true H pack lost a selected axis")
            # Tiny fields are the explicitly stopped direct kernel.
            # The same operator runs through C and its physical phases above this fixed cap.
            if L <= 12 and len(selected) < 16:
                values = [(number(s, self.wide), number(s, self.wide)) for _ in range(1 << L)]
                for pos in selected:
                    half = 1 << pos
                    for k in range(0, len(values), 2 * half):
                        for j in range(k, k + half):
                            x, y = values[j]
                            u, v = values[j + half]
                            values[j], values[j + half] = (x + u, y + v), (x - u, y - v)
                for z in values:
                    put(d, z, self.wide)
                return
            f = Field(L, self.wide)
            transfer(s, f.stream, (1 << L) * record)
            native_h(
                f, selected[0] - bit, len(selected), self.widths[start], bit, self.P, self.exchange
            )
            f.stream.seek(0)
            transfer(f.stream, d, (1 << L) * record)
            f.retire()

        tape.seek(0)
        hadamard_tape(tape, self.widths, positions, self.p, 2 * self.wide, one)
        self.h_calls += 1

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
        tensor_diagonal(tape, self.wide, self.grid, self.entrance)
        for start, end, layers in self.packs:
            for _ in range(2):
                for layer in layers:
                    bit = layer[0][0]
                    if any(entry[0] != bit for entry in layer):
                        raise ArithmeticError("Mismatched selected significance")
                    tables = self.idles.copy()
                    tables[start:end] = [entry[1] for entry in layer]
                    tensor_diagonal(tape, self.wide, self.grid, tables)
                    if bit is not None:
                        self.h(tape, start, end, bit)
        tensor_diagonal(tape, self.wide, self.grid, self.exit)
        if opposite:
            conjugate()

    def _multiply_tapes(self, left, right, output, lengths, negative, coefficients):
        b, p, P = self.b, self.p, self.P
        digit_counts = tuple((length + b - 1) // b for length in lengths)
        if max(*digit_counts, sum(digit_counts) - 1) > self.size:
            raise ValueError("The linear convolution would wrap on this tensor")
        with ExitStack() as stack:

            def tape():
                handle = stack.enter_context(TemporaryFile())
                stack.callback(erase, handle)
                return handle

            work, parked = tape(), tape()
            self.write_operand(work, left, lengths[0])
            self.transform(work)
            work.seek(0)
            for _ in range(self.total):
                put(
                    parked, (truncate(number(work, self.wide), P - p) for _ in range(2)), self.short
                )
            erase(work)
            self.write_operand(work, right, lengths[1])
            self.transform(work)
            work.seek(0)
            parked.seek(0)
            mul = self.grid.scalar_product
            for _ in range(self.total):
                a, c = number(parked, self.short), number(parked, self.short)
                d, f = (truncate(number(work, self.wide), P - p) for _ in range(2))
                re = truncate(mul(a, d) - mul(c, f), p) << (P - p)
                im = truncate(mul(a, f) + mul(c, d), p) << (P - p)
                work.seek(-2 * self.wide, 1)
                put(work, (re, im), self.wide)
            erase(parked)
            self.transform(work, opposite=True)
            work.seek(0)
            gain = (4 * (1 << b) * self.size) ** 2
            for _ in range(self.total):
                center = truncate(number(work, self.wide), P - p)
                work.seek(self.wide, 1)
                coeff = (2 * mul(gain, center) + (1 << p)) >> (p + 1)
                put(parked, (coeff,), self.short)
            erase(work)
            parked.seek(0)
            crt_tape(
                parked, self.total, self.short, p, lambda s, d, w: self.tree.apply(s, d, w, True)
            )
            parked.seek(0)
            values = [] if coefficients else None

            def recovered():
                for valid in original_positions(self.sides, self.widths):
                    value = number(parked, self.short)
                    if valid:
                        if coefficients:
                            values.append(value)
                        yield value

            count = carry_to_tape(output, recovered(), b)
            return bool(negative and all(lengths)), count, values

    def multiply_tapes(
        self,
        left,
        left_bytes,
        right,
        right_bytes,
        output,
        *,
        left_negative=False,
        right_negative=False,
        coefficients=False,
    ):
        if left is output or right is output:
            raise ValueError("The product needs a separate output owner")
        lengths = magnitude_bits(left, left_bytes), magnitude_bits(right, right_bytes)
        return self._multiply_tapes(
            left, right, output, lengths, left_negative != right_negative, coefficients
        )

    def multiply(self, left, right, *, coefficients=False):
        a, b = (abs(x).to_bytes((abs(x).bit_length() + 7) // 8, "little") for x in (left, right))
        output = BytesIO()
        negative, _, values = self.multiply_tapes(
            BytesIO(a),
            len(a),
            BytesIO(b),
            len(b),
            output,
            left_negative=left < 0,
            right_negative=right < 0,
            coefficients=coefficients,
        )
        value = int.from_bytes(output.getvalue(), "little")
        return (-value if negative else value), values


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
    """Multiply two signed magnitude intervals. Return the output sign and byte count."""
    if left is output or right is output:
        raise ValueError("The product needs a separate output owner")
    lengths = magnitude_bits(left, left_bytes), magnitude_bits(right, right_bytes)
    negative = left_negative != right_negative
    shape = parameters(max(lengths))
    if shape is None:
        a, b = (
            sum(magnitude_limbs(source, length, max(1, length)))
            for source, length in zip((left, right), lengths, strict=True)
        )
        value = scalar_product(engine)(a, b)
        raw = value.to_bytes(max(1, (value.bit_length() + 7) // 8), "little")
        output.write(raw)
        return bool(negative and all(lengths)), len(raw)
    sides = tuple(square_axes(shape.axes()))
    machine = Product(sides, shape.public // 6, shape.precision(), engine=engine)
    sign, size, _ = machine._multiply_tapes(left, right, output, lengths, negative, False)
    return sign, size


def multiply(left, right, engine=None):
    n = max(abs(left).bit_length(), abs(right).bit_length())
    shape = parameters(n)
    if shape is None:
        return scalar_product(engine)(left, right)
    sides = tuple(square_axes(shape.axes()))
    return Product(sides, shape.public // 6, shape.precision(), engine=engine).multiply(
        left, right
    )[0]


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description=__doc__)
    for name in ("left", "right"):
        parser.add_argument(name, type=lambda v: int(v, 0))
    parser.add_argument("--library", type=Path)
    args = parser.parse_args()
    print(
        hex(multiply(args.left, args.right, native_product(args.library) if args.library else None))
    )
