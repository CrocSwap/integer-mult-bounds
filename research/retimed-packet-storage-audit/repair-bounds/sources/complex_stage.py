"""Apply the priced complex word to complete contiguous numerical windows."""

from functools import cache


def entrance(L, active_low, h, window, row_bits, digit, suffix):
    """Find a disjoint whole packet for both controls, true stock and the active field."""
    body = h * window
    ctr = h * digit
    total = row_bits + 3 * ctr + body + suffix
    left, right = active_low, L - active_low - body
    if max(left, right) < total:
        raise ValueError("The exterior cannot house a complete numerical source")
    start = 0 if left >= right else active_low + body
    back = start + suffix
    y = back + ctr
    t = y + body
    u = t + ctr
    return back, y, t, u, u + ctr + row_bits


@cache
def production_supplier():
    from source_inputs import activate
    from tagged_sources import read_words
    from raw48 import Artifacts, ComplexRaw
    from positive import Positive

    _, root = activate()
    _, word = read_words()
    artifacts = Artifacts(root / "research/grade14-native-realization")
    factory = lambda fields, cols, **kw: ComplexRaw(artifacts, fields, cols, **kw)
    return Positive(word, factory, 1 << 3_300_000_000)


def native_h(field, low, h, window, offset, p, swap, supplier=None):
    """Run H on h adjacent complete windows at one common bit significance."""
    from compact_columns import Columns
    from positive import Positive

    digit = 4 * (p + 1).bit_length() + 6
    native = (supplier is not None or h.bit_length() - 1 >= 3_300_000_000) and window >= 128 * digit
    if not native:
        # This positive call stops before it reads a compiler descriptor.
        primitive = Positive(None, None, h)
        columns = Columns(window, offset, digit, 0, 0, 0, 0, swap)
        primitive.hadamard(field, low, h, columns)
        return

    supplier = supplier or production_supplier()
    layers, power = 2, 1
    while power < h + 1:
        layers += 1
        power *= supplier.carrier
    stock_bits = (supplier.owners.bit_length() - 1) * layers
    suffix = (p + 1).bit_length() ** 2
    place_and_apply(field, low, h, window, offset, stock_bits, digit, suffix, swap, supplier)


def place_and_apply(field, low, h, window, offset, stock_bits, digit, suffix, swap, supplier):
    """Move the complete pack, apply the supplier to each exterior slab, and return."""
    from compact_columns import Columns
    from spool import Field, scratch, transfer

    back, place, front_t, front_u, box = entrance(
        field.ambient_bits, low, h, window, stock_bits, digit, suffix
    )
    columns = Columns(window, offset, digit, front_u, front_t, back, back, swap)
    field.swap(low, place, h * window, swap)
    with scratch() as source, scratch() as output:
        field.stream.seek(0)
        transfer(field.stream, source, field.count * field.record)
        source.seek(0)
        for _ in range(1 << (field.ambient_bits - box)):
            slab = Field(box, field.component_bytes)
            extent = slab.count * slab.record
            transfer(source, slab.stream, extent)
            supplier.hadamard(slab, place, h, columns)
            slab.stream.seek(0)
            transfer(slab.stream, output, extent)
            slab.retire()
        output.seek(0)
        field.stream.seek(0)
        transfer(output, field.stream, field.count * field.record)
    field.swap(low, place, h * window, swap)
