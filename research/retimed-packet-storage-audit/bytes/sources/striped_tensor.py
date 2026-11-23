"""Place a full tensor factor on slices of one unselected address axis."""

from dataclasses import dataclass

from stripe_route import striped_in_place


@dataclass(frozen=True)
class Spectator:
    prefixes: int
    stripes: int
    block: int
    packed_width: int
    selected: tuple


def spectator_layout(axis_widths, selected, stripe_bits):
    """Remove high bits from a single unused axis. Low address bits come first."""
    widths = tuple(axis_widths)
    offsets = []
    total = 0
    for width in widths:
        if width < 1:
            raise ValueError("An original address axis must contain at least one bit")
        offsets.append(total)
        total += width
    if (
        stripe_bits < 0
        or len(set(selected)) != len(selected)
        or any(p < 0 or p >= total for p in selected)
    ):
        raise ValueError("Invalid Hadamard positions or stripe size")
    unused = [
        (width, start)
        for width, start in zip(widths, offsets, strict=True)
        if all(not start <= p < start + width for p in selected)
    ]
    width, start = max(unused, default=(0, 0))
    bits = min(stripe_bits, width)
    low = start + width - bits
    high = low + bits
    reduced = tuple(p - bits if p >= high else p for p in selected)
    return Spectator(1 << (total - high), 1 << bits, 1 << low, total - bits, reduced)


def hadamard_tape(bank, axis_widths, selected, public_bits, word_bytes, apply):
    """Apply the complete numerical operator on each reduced rectangular tape."""
    if public_bits < 1 or word_bytes < 1:
        raise ValueError("The numerical record and public precision must be positive")
    layout = spectator_layout(axis_widths, selected, (public_bits + 1).bit_length() // 2)

    def run(source, target, width):
        if width != layout.block * word_bytes:
            raise ArithmeticError("The stripe does not contain complete numerical words")
        apply(source, target, layout.packed_width, layout.selected, word_bytes)

    striped_in_place(
        bank, layout.prefixes, layout.stripes * layout.block * word_bytes, layout.stripes, run
    )


def crt_tape(bank, records, word_bytes, public_bits, route):
    """Preserve every address and distribute the opaque numeric representation in stripes."""
    if public_bits < 1 or word_bytes < 1:
        raise ValueError("The complete CRT record and public precision must be positive")
    stripes = min(word_bytes, 1 << ((public_bits + 1).bit_length() // 2))
    striped_in_place(bank, records, word_bytes, stripes, route)


def hadamard_words(data, layout, apply):
    """Execute the same contiguous reads and writes on signed finite reference words."""
    if len(data) != layout.prefixes * layout.stripes * layout.block:
        raise ValueError("Wrong complete numerical extent")
    stride = layout.block * layout.stripes
    for j in range(layout.stripes):
        start = j * layout.block
        packed = []
        for _ in range(layout.prefixes):
            packed.extend(data[start : start + layout.block])
            start += stride
        apply(packed, (1 << bit for bit in layout.selected))
        start = j * layout.block
        for p in range(0, len(packed), layout.block):
            data[start : start + layout.block] = packed[p : p + layout.block]
            start += stride
