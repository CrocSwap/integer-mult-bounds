"""Prefix-major leaf/XOR fusion on encoded complete-prefix domains.

JoyboyBrian; substantial OpenAI Codex assistance; Apache-2.0.
Uses Jose Manuel / David Arias's packet interpreter and consumer unchanged.
"""
from types import SimpleNamespace
from cardinal_counts import Count, positive
from records import Tape, RECORD_END
from stream import Counter
from words import BLANK, ZERO, ONE, need
import packet_engine, episode


def read_prefix_owned(source, field_count):
    """The source raw-prefix loop, with explicit owned cleanup on truncation."""
    output, remaining = Tape(), Counter(field_count)
    try:
        while not remaining.finished:
            while source.read() != RECORD_END:
                symbol = source.read()
                need(symbol != BLANK, 'complete fused raw prefix')
                output.append(symbol); source.step(1)
            output.append(RECORD_END); source.step(1); remaining.decrement()
        output.rewind()
        return output
    except ValueError:
        output.clear()
        raise
    finally:
        remaining.close()


def copy_exact(source, target, count):
    """Encoded bit copy; the local counter is owned even on short input."""
    remaining = Counter(count)
    try:
        while not remaining.finished:
            bit = source.read()
            need(bit in (ZERO, ONE), 'complete fused Boolean fibre')
            target.append(bit); source.step(1); remaining.decrement()
    finally:
        remaining.close()


def run(source, target, events, layout, prefix_directory, prefix_count,
        field_count, coefficient, context, old_count, observe=None):
    """Return owned XOR result, preserving canonical borrowed entry heads.

    events() yields the same closed leaf trace every time. Coefficients are
    deterministic in the current complete prefix and restore borrowed state.
    The supplied directory is the original complete producer's output.
    """
    need(len({id(source), id(target), id(prefix_directory)}) == 3,
         'distinct fused borrowed roles')
    positive(prefix_count); positive(old_count); positive(context.highs)
    expected = Count.product(old_count, context.highs)
    try:
        need(prefix_count.equals(expected), 'complete fused prefix product')
    finally:
        expected.close()
    fibre, single, output = layout.fibre(), Count.literal(1), Tape()
    remaining = Counter(prefix_count)
    source.rewind(); target.rewind(); prefix_directory.rewind()
    try:
        while not remaining.finished:
            fields, left, right, returned, consumed = None, Tape(), Tape(), None, None
            try:
                fields = read_prefix_owned(prefix_directory, field_count)
                copy_exact(source, left, fibre); copy_exact(target, right, fibre)
                left.rewind(); right.rewind()
                returned = packet_engine.run(left, events(), layout, fields, single,
                                             field_count, coefficient)
                need(returned is not left, 'owned completed fused child')
                if observe is not None: observe(returned)
                consumed = episode.xor_packet(returned, right,
                    SimpleNamespace(highs=single), single, fibre)
                copy_exact(consumed, output, fibre)
                need(consumed.read() == BLANK, 'complete fused local consumer')
            finally:
                if consumed is not None: consumed.clear()
                if returned is not None and returned is not left: returned.clear()
                left.clear(); right.clear()
                if fields is not None: fields.clear()
            remaining.decrement()
        need(source.read() == target.read() == prefix_directory.read() == BLANK,
             'complete fused input packet and directory')
        output.rewind()
        return output
    except ValueError:
        output.clear()
        raise
    finally:
        remaining.close(); single.close(); fibre.close()
        source.rewind(); target.rewind(); prefix_directory.rewind()
