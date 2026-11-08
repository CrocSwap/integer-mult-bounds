"""Separately paid emission of prepared folded factors and descriptors.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
Host integers are preparation values. Online payloads enter FoldedSolve
only as borrowed physical tapes, never through this preparation routine.
"""
from gaussian_sources import active
active()
from cardinal_counts import Count
from records import Tape
from ring_words import Signed, write_signed
from router_metadata import owned
from session import erase_marker


def emit(values, width):
    tape = Tape()
    try:
        for value in values:
            with owned(Signed(Count.literal(abs(value)), value < 0)) as (word,):
                write_signed(word, tape, width)
        tape.rewind()
        return tape
    except BaseException:
        tape.clear()
        erase_marker(tape)
        raise


class EncodedFactors:
    """Two persistent factor banks and five distinct descriptor tapes."""
    def __init__(self, plan, right_hand_sides):
        if type(right_hand_sides) is not int or right_hand_sides < 1:
            raise ValueError("positive prepared RHS count")
        self.counts, self.streams = (), ()
        try:
            for value in (plan['n'], right_hand_sides, plan['band'],
                          plan['width'], plan['precision']):
                self.counts += (Count.literal(value),)
            for name in ('lower', 'upper'):
                self.streams += (emit(plan[name], self.counts[3]),)
        except BaseException:
            self.close()
            raise

    def close(self):
        for tape in self.streams:
            tape.clear()
            erase_marker(tape)
        self.streams = ()
        for count in self.counts:
            count.close()
            erase_marker(count.tape)
        self.counts = ()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
