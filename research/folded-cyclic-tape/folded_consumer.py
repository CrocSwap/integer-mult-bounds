"""Physical fold/solve/unfold on the authenticated Gaussian tape cohort.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Folding is inherited from #4879; BandedSolve and word arithmetic are #3851.
"""
from gaussian_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import copy_bits
from encoded import compare
from gaussian_boundary import BandedSolve
from gaussian_rows import reverse_records
from records import Tape
from router_metadata import indices, owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from words import BLANK, LEFT, need


def origin(tape):
    """Inspect the preceding delimiter through paid local tape operations."""
    tape.step(-1)
    correct = tape.read() == LEFT
    tape.step(1)
    need(correct, "canonical folded input origin")


def fold(line, reverse, target, length, width):
    """Copy 0,n-1,1,n-2,... without decoding an index or payload word."""
    reverse_records(line, reverse, length, width)
    line.rewind()
    reverse.rewind()
    front = True
    try:
        for _ in indices(length):
            copy_bits(line if front else reverse, target, width)
            front = not front
    finally:
        line.rewind()
        reverse.rewind()
        target.rewind()


def unfold(source, front, back, reverse, target, length, width):
    """Split alternating records, reverse the back half, concatenate."""
    source.rewind()
    first = True
    with owned(Count.literal(0), Count.literal(0)) as (nf, nb):
        for _ in indices(length):
            copy_bits(source, front if first else back, width)
            (nf if first else nb).increment()
            first = not first
        need(source.read() == BLANK, "exact folded child output extent")
        source.rewind()
        front.rewind()
        back.rewind()
        reverse_records(back, reverse, nb, width)
        with owned(Count.product(nf, width)) as (bits,):
            copy_bits(front, target, bits)
        with owned(Count.product(nb, width)) as (bits,):
            copy_bits(reverse, target, bits)
        need(front.read() == reverse.read() == BLANK, "complete unfolded halves")
        front.rewind()
        back.rewind()
        reverse.rewind()


class FoldedSolve:
    """One fixed owner, borrowed folded factors, RHS-major original order."""
    def __init__(self, solver=None):
        self.solver = BandedSolve() if solver is None else solver
        self.pool = ScratchPool(128)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        self.closed = True
        self.pending = False
        self.calls = 0
        for value in (*self.pool.tapes, self.output):
            erase_marker(value)

    def private_tapes(self):
        child = self.solver
        return (*self.pool.tapes, self.output, *child.pool.tapes, child.output,
                *child.word.pool.tapes, child.word.output, *child.word.canonical,
                *child.word.base.pool.tapes, *child.word.product.pool.tapes,
                *child.word.product.word.pool.tapes,
                *child.word.product.twiddles.pool.tapes)

    def consume(self):
        need(self.closed and self.pending, "one pending folded output")
        self.output.clear()
        erase_marker(self.output)
        self.pending = False

    def run(self, lower, upper, rhs, length, count, band, width, precision):
        ports = tuple(borrowed_tape(v) for v in (lower, upper, rhs))
        meta = tuple(borrowed_count(v) for v in
                     (length, count, band, width, precision))
        lower, upper, rhs = ports
        length, count, band, width, precision = meta
        tapes = ports + tuple(v.tape for v in meta)
        forbidden = self.private_tapes()
        need(len({id(v) for v in tapes}) == len(tapes)
             and all(v not in forbidden for v in tapes), "distinct external folded ports")
        for value in tapes:
            origin(value)
        for value in (length, count, band, width):
            positive(value)
        need(compare(precision, width) < 0, "folded fractional width")
        need(self.closed and not self.pending and not self.pool.live,
             "consume prior folded output")
        need(self.output.read() == BLANK, "blank folded output origin")
        self.solver.idle()
        need(self.solver.output.read() == BLANK, "consumed scalar child output")
        for value in (*self.pool.tapes, self.output):
            initialize_marker(value)
        self.closed = False
        line = reverse = folded = front = back = back_reverse = None
        succeeded = False
        child_pending = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    line, reverse, folded, front, back, back_reverse = (
                        self.pool.acquire() for _ in range(6))
                    with owned(Count.product(length, width)) as (line_bits,):
                        for _ in indices(count):
                            copy_bits(rhs, line, line_bits)
                            line.rewind()
                            fold(line, reverse, folded, length, width)
                            with self.scope.suspended():
                                result = self.solver.run(lower, upper, folded,
                                                        length, band, width, precision)
                            child_pending = True
                            unfold(result, front, back, back_reverse, self.output,
                                   length, width)
                            result.clear()
                            erase_marker(result)
                            child_pending = False
                            self.solver.idle()
                            for value in (line, reverse, folded, front, back, back_reverse):
                                borrowed_tape(value).clear()
                        need(rhs.read() == BLANK, "complete RHS-major folded input")
                    self.calls += 1
                    succeeded = True
                    self.pending = True
                finally:
                    for value in (line, reverse, folded, front, back, back_reverse):
                        if value is not None:
                            value.clear()
                    if child_pending:
                        self.solver.output.clear()
                        erase_marker(self.solver.output)
                    for value in (*ports, *meta):
                        value.rewind()
                    self.pool.empty()
        finally:
            for value in self.pool.tapes:
                erase_marker(value)
            self.output.rewind()
            if not succeeded:
                self.output.clear()
                erase_marker(self.output)
                self.pending = False
            self.closed = True
        return self.output
