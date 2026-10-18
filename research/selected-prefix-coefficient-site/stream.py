"""Complete-fibre later-target ADD, adapted from PR2171/2234/2364.

All payload reads, writes, erasures and moves use single-symbol tape methods.
The coefficient callback runs at the actual split/merge preparation site.
"""
from tapes import Tape, need


def copy(source, target, count):
    for _ in range(count):
        bit = source.read()
        need(bit in (0, 1), "opaque payload bit")
        target.append(bit)
        source.move(1)


def copy_blocks(source, target, blocks, suffix_bits):
    for _ in range(blocks):
        copy(source, target, suffix_bits)


def add_site(source, prefixes, modulus, before, middle, suffix_bits, coefficient):
    need(min(prefixes, before, middle, suffix_bits) > 0 and modulus > 1,
         "complete coefficient-site extents")
    left, right, out = Tape(), Tape(), Tape()
    for prefix in range(prefixes):
        c = coefficient(prefix)
        for _before in range(before):
            for x in range(modulus):
                offset = c*x % modulus
                for _middle in range(middle):
                    copy_blocks(source, left, modulus-offset, suffix_bits)
                    copy_blocks(source, right, offset, suffix_bits)
    need(source.read() is None, "complete split input")
    source.rewind()
    left.rewind()
    right.rewind()
    for prefix in range(prefixes):
        c = coefficient(prefix)
        for _before in range(before):
            for x in range(modulus):
                offset = c*x % modulus
                for _middle in range(middle):
                    copy_blocks(right, out, offset, suffix_bits)
                    copy_blocks(left, out, modulus-offset, suffix_bits)
    need(left.read() is None and right.read() is None, "complete split scratch consumption")
    left.clear()
    right.clear()
    need(left.cells == right.cells == {0: "^"}, "erase split scratch")
    out.rewind()
    return out, {name: dict(tape.meter) for name, tape in
                 (("input", source), ("left", left), ("right", right), ("output", out))}
