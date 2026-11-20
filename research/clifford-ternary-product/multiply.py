"""Multiply two ordinary little-endian bit records with certified Clifford admission."""

from pathlib import Path
from functools import cache
from importlib.util import module_from_spec, spec_from_file_location
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from contraction import product_passes
from delivery import deliver
from operand import recognise_sparse
from sectors import control_sites, recognise_sectors, sector_product
from templates import admit, assemble, pack, unpack


def geometry(length):
    m, extent = 0, 1
    while extent < length:
        m += 1
        extent *= 3
    width = 1 << (m // 2)
    return m, width, max(1, length // width)


@cache
def fallback_source():
    source = HERE / "vendor/direct-fourier/product.py"
    spec = spec_from_file_location("ternary_fallback_product", source)
    product = module_from_spec(spec)
    before = sys.path.copy()
    try:
        spec.loader.exec_module(product)
    finally:
        sys.path[:] = before
    return product


def fourier_fallback(a, b, length):
    """Run the pinned controller with the caller's physical repository root."""
    product = fallback_source()
    p, rectangle, count, _ = product.controller_shape(length)
    if count:
        widths = product.production_widths(rectangle, count)
        sides = product.select_squares(widths)
        if sides is not None:
            machine = product.Multiplier(sides, p // 6, product.production_precision(p, widths),
                                         source_root=HERE.parents[1])
            return machine.multiply(a, b)[0]
    return product.word_product(a, b)


def multiply_bits(left, right, *, evidence=None):
    """Return canonical low-first product bits. Zero has the single bit zero."""
    if any(bit not in (0, 1) for bit in left) or any(bit not in (0, 1) for bit in right):
        raise ValueError("Use bytes containing literal zero and one bits")
    length = max(1, len(left), len(right))
    m, width, count = geometry(length)
    choices = (recognise_sparse, recognise_sectors) if control_sites(m) else (recognise_sparse,)
    for fit in choices:
        a = admit(left, m, width, count, fit)
        b = admit(right, m, width, count, fit) if a is not None else None
        if a is None or b is None:
            continue
        movement = {} if evidence is not None else None
        if fit is recognise_sparse:
            route = "clifford"
            product = deliver(product_passes(a.chart, b.chart), stats=movement)
        else:
            route = "clifford-sectors"
            product = sector_product(a.chart, b.chart, stats=movement)
        if evidence is not None:
            evidence.update(route=route, sites=m, template_bits=width,
                            repetitions=count, shifts=[a.shift, b.shift],
                            signs=[a.sign, b.sign], delivery=movement)
        return assemble(product, a, b, width, count)
    if evidence is not None:
        evidence.update(route="ordinary", sites=m)
    value = fourier_fallback(pack(left), pack(right), length)
    return unpack(value, max(1, value.bit_length()))


def multiply_integer(a, b, *, evidence=None):
    left = unpack(abs(a), max(1, abs(a).bit_length()))
    right = unpack(abs(b), max(1, abs(b).bit_length()))
    value = pack(multiply_bits(left, right, evidence=evidence))
    return -value if (a < 0) != (b < 0) else value


if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left", type=lambda s: int(s, 0))
    parser.add_argument("right", type=lambda s: int(s, 0))
    args = parser.parse_args()
    receipt = {}
    value = multiply_integer(args.left, args.right, evidence=receipt)
    print(value)
    print(json.dumps(receipt, sort_keys=True))
