"""Multiply two signed integers with a length-only controller."""

from functools import cache
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
FOURIER = HERE / "retained" / "fourier"
sys.path.insert(0, str(HERE))
from short_product import MAX_TRANSFORM, native_product, reference_product


def source_module(name, filename):
    spec = spec_from_file_location(name, filename)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


geometry = source_module("bounded_square_geometry", FOURIER / "square_geometry.py")


@cache
def fourier():
    before = sys.path.copy()
    try:
        return source_module("bounded_fourier_product", FOURIER / "product.py")
    finally:
        sys.path[:] = before


@cache
def receiver():
    from row_crt import two_axis_crt

    class Multiplier(fourier().Multiplier):
        def crt(self, field, reverse=False):
            if len(self.sides) == 2 and max(self.widths) <= 9:
                return two_axis_crt(self, field, reverse)
            return super().crt(field, reverse)

    return Multiplier


def packed_length(value):
    return (value.bit_length()+7)//8


def short_by_long(small, large):
    """Stream a bounded multiplier across the longer operand's 192-bit limbs."""
    source = large.to_bytes(packed_length(large),"little")
    out = bytearray()
    carry = 0
    mask = (1 << 192)-1
    for offset in range(0,len(source),24):
        limb = int.from_bytes(source[offset:offset+24],"little")
        value = limb*small+carry
        out.extend((value & mask).to_bytes(24,"little"))
        carry = value >> 192
    out.extend(carry.to_bytes(packed_length(carry),"little"))
    return int.from_bytes(out,"little")


def finite_product(a, b, transform=reference_product, *, max_transform=MAX_TRANSFORM):
    """Use three proper children above the largest admitted transform."""
    if min(a, b) < 0:
        raise ValueError("The finite dispatcher requires magnitudes")
    n = max(a.bit_length(), b.bit_length())
    if not a or not b:
        return 0
    if n <= 192:
        return a*b
    if min(a.bit_length(),b.bit_length()) <= 192:
        return short_by_long(a,b) if a <= b else short_by_long(b,a)
    count = (a.bit_length()+15)//16 + (b.bit_length()+15)//16 - 1
    if n >= 4096 and count <= max_transform:
        x = a.to_bytes(packed_length(a), "little")
        y = b.to_bytes(packed_length(b), "little")
        return int.from_bytes(transform(x, y), "little")
    h = (n+1)//2
    mask = (1 << h)-1
    a1, a0 = a >> h, a & mask
    b1, b0 = b >> h, b & mask
    hi = finite_product(a1, b1, transform, max_transform=max_transform)
    lo = finite_product(a0, b0, transform, max_transform=max_transform)
    delta_a, delta_b = a1-a0, b1-b0
    delta = finite_product(abs(delta_a), abs(delta_b), transform, max_transform=max_transform)
    if (delta_a < 0) != (delta_b < 0):
        delta = -delta
    return (hi << (2*h)) + ((hi+lo-delta) << h) + lo


@cache
def installed_engine():
    library = HERE / "short_product.so"
    return native_product(library) if library.is_file() else None


def signed_leaf(left, right, engine):
    value = finite_product(abs(left), abs(right), engine)
    return -value if (left < 0) != (right < 0) else value


def multiply(left, right, transform=None):
    """Return the exact signed product for every input length."""
    a, b = abs(left), abs(right)
    if not a or not b:
        return 0
    p, length, count, _ = geometry.controller_shape(max(a.bit_length(), b.bit_length()))
    engine = installed_engine() if transform is None else transform
    if count:
        widths = geometry.production_widths(length, count)
        sides = geometry.select_squares(widths)
        if sides is not None:
            program = fourier()
            scalar = (lambda x,y:signed_leaf(x,y,engine)) if engine else program.word_product
            machine = receiver()(sides, p//6, program.production_precision(p, widths),
                                 source_root=HERE.parents[1], scalar_product=scalar)
            result = machine.multiply(a, b)[0]
            return -result if (left < 0) != (right < 0) else result
    result = finite_product(a, b, engine) if engine else fourier().word_product(a, b)
    return -result if (left < 0) != (right < 0) else result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left", type=lambda s:int(s, 0))
    parser.add_argument("right", type=lambda s:int(s, 0))
    parser.add_argument("--library", type=Path)
    args = parser.parse_args()
    engine = native_product(args.library) if args.library else None
    print(hex(multiply(args.left, args.right, engine)))
