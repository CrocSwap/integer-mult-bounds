"""Linear-traffic address negation on complete atom fibres.

The source shape is [before][M][suffix], M = ring.modulus.  No atom value
or spectator cardinality is decoded into host control.  Each nonzero atom
slice is copied forwards, while slice starts are visited in reverse order.
"""
from bitstream import copy_bits
from records import Tape
from stream import Counter, positive_extent
from words import BLANK, need


def move_slices(source, count, suffix, direction):
    """Move count complete slices by charged unit head movements."""
    blocks = Counter(count)
    try:
        while not blocks.finished:
            bits = Counter(suffix)
            try:
                while not bits.finished:
                    source.step(direction)
                    bits.decrement()
            finally:
                bits.close()
            blocks.decrement()
    finally:
        blocks.close()


def sign_address(source, ring, q, before, suffix):
    """Pull back x -> -x mod M, preserving source and resetting both heads.

    q is retained for the old public signature; the permutation needs only
    M >= 2. Source-head moves, including the final rewind, are at most 6V,
    where V = before*M*suffix. Numerical counter setup has its usual
    amortized binary-counting charge and is not hidden in this move bound.
    """
    del q
    positive_extent(before)
    positive_extent(suffix)
    two = ring.arena.literal(2)
    leading = ring.raw.subtract_exact(ring.modulus, two)
    nonzero = ring.raw.subtract_exact(ring.modulus, ring.one)
    output = Tape()
    outer = Counter(before)
    try:
        while not outer.finished:
            # Preserve the zero slice, then reach the final nonzero slice.
            copy_bits(source, output, suffix)
            move_slices(source, leading, suffix, 1)
            remaining = Counter(nonzero)
            try:
                while not remaining.finished:
                    copy_bits(source, output, suffix)
                    remaining.decrement()
                    if not remaining.finished:
                        # Two is finite control. Copying a padded residue word
                        # for this count once per atom would cost O(V log M)
                        # when suffix=1.
                        for _ in range(2):
                            backwards=Counter(suffix)
                            try:
                                while not backwards.finished:
                                    source.step(-1)
                                    backwards.decrement()
                            finally:backwards.close()
            finally:
                remaining.close()
            # We finished just after slice 1; advance to the next outer row.
            move_slices(source, leading, suffix, 1)
            outer.decrement()
        need(source.read() == BLANK, "complete linear sign input")
        source.rewind()
        output.rewind()
        return output
    except ValueError:
        output.clear()
        raise
    finally:
        source.rewind()
        outer.close()
        ring.arena.free_many(two, leading, nonzero)
