"""Multiply signed binary tapes with the installed single-band native suppliers."""

from argparse import ArgumentParser
from functools import cache, partial
from io import BytesIO

from upstream import HERE, install

install()
from band_positive import Positive
from binary_io import magnitude_bits, magnitude_limbs
from calibration import COMPACT, PROFILES
from inputs.triangular.multiplier import Product as PackProduct, precision
from linear_geometry import parameters, square_sides
from ordinary_carrier import ordinary_swap
from positive_dispatch import h_pack
from product_path import scalar_product
from raw48 import ComplexRaw


@cache
def production_supplier(rank_log):
    from strong_complex import artifacts, word

    _, _, _, source = install()
    data = HERE / "inputs"
    atlas = artifacts(source / "research/grade14-native-realization", data)
    native = word(atlas.graph, atlas.layout)

    def physical(fields, columns, **kw):
        return ComplexRaw(atlas, fields, columns, **kw)

    return Positive(native, physical, 1 << rank_log)


def prepare_native(profile=COMPACT):
    """Generate the fixed native programs. The tape caller can also install each at first use."""
    from binary_receiver import source_planner

    binary = source_planner(profile.power, profile.floor)
    streams = [binary.image(1 << log_rank) for log_rank in profile.rank_logs]
    positive = production_supplier(profile.complex_log)
    if positive.owners <= 1:
        raise ArithmeticError("The numerical carrier needs independent rows")
    streams.append(positive.planner.image(positive.carrier))
    return tuple(streams)


class Product(PackProduct):
    def __init__(self, sides, b, P, exchange=None, *, engine=None, profile=COMPACT):
        self.profile = profile
        exchange = partial(ordinary_swap, profile=profile) if exchange is None else exchange
        super().__init__(sides, b, P, exchange, engine=engine)

    def h(self, tape, start, end, bit):
        h_pack(
            self,
            tape,
            start,
            end,
            bit,
            self.profile.complex_log,
            partial(production_supplier, self.profile.complex_log),
        )


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
    profile=COMPACT,
):
    """Return the sign and length of the product. Restore both input heads."""
    if output is left or output is right:
        raise ValueError("The product needs a separate output owner")
    lengths = magnitude_bits(left, left_bytes), magnitude_bits(right, right_bytes)
    negative = left_negative != right_negative
    shape = parameters(max(lengths))
    if shape is None:
        a, b = (
            sum(magnitude_limbs(src, size, max(1, size)))
            for src, size in zip((left, right), lengths, strict=True)
        )
        result = scalar_product(engine)(a, b)
        raw = result.to_bytes(max(1, (result.bit_length() + 7) // 8), "little")
        output.write(raw)
        return bool(negative and all(lengths)), len(raw)
    sides = tuple(square_sides(shape))
    machine = Product(
        sides,
        shape.public // 6,
        precision(shape.public, shape.extent_bits, shape.count),
        engine=engine,
        profile=profile,
    )
    sign, size, _ = machine._multiply_tapes(left, right, output, lengths, negative, False)
    return sign, size


def multiply(left, right, *, profile=COMPACT):
    raw = [abs(v).to_bytes((abs(v).bit_length() + 7) // 8, "little") for v in (left, right)]
    out = BytesIO()
    sign, _ = multiply_tapes(
        BytesIO(raw[0]),
        len(raw[0]),
        BytesIO(raw[1]),
        len(raw[1]),
        out,
        left_negative=left < 0,
        right_negative=right < 0,
        profile=profile,
    )
    value = int.from_bytes(out.getvalue(), "little")
    return -value if sign else value


if __name__ == "__main__":
    args = ArgumentParser(description=__doc__)
    args.add_argument("left", type=lambda x: int(x, 0))
    args.add_argument("right", type=lambda x: int(x, 0))
    args.add_argument("--profile", choices=PROFILES, default="compact")
    call = args.parse_args()
    print(multiply(call.left, call.right, profile=PROFILES[call.profile]))
