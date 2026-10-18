"""Complete-family access for the source-compiled first selected prefix."""
import prefix_sources
prefix_sources.activate()
from cardinal_counts import Count, positive
from compact_counts import append_bits, copy_bits
from records import Tape
from scalar_engine import ScalarEngine
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from signed_linear import CoefficientDomainError
from stream import Counter
from words import BLANK, LEFT, ONE, ZERO, need


def skip_bits(source, count):
    remaining = Counter(count)
    try:
        while not remaining.finished:
            need(source.read() in (ZERO, ONE), "complete skipped family body")
            source.step(1)
            remaining.decrement()
    finally:
        remaining.close()


class PrefixEngine:
    """Compile fixed source owners before receiving any encoded payload."""
    def __init__(self):
        from selected_binding import compile_selected
        self.binding = compile_selected()
        self.families = self.binding["families"]
        self.target = self.binding["target"]
        self.source = self.binding["source"]
        self.literals = (("scale", -1, 2, "scratch"), ("add", 1, 2, "scratch"))
        self.scalar = ScalarEngine(self.literals)
        self.pool = ScratchPool(64)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        for tape in (*self.pool.tapes, self.output):
            erase_marker(tape)
        self.closed = True

    def rearm(self):
        need(self.closed and self.output.read() == BLANK and not self.pool.live,
             "consume previous selected-prefix return")
        self.output.step(-1)
        need(self.output.read() in (LEFT, BLANK), "prefix output origin")
        self.output.write(LEFT)
        self.output.step(1)
        for tape in self.pool.tapes:
            initialize_marker(tape)
        self.closed = False

    def scalar_return(self, literal, target, source, width, count):
        self.scalar.select(literal)
        with self.scope.suspended():
            returned = self.scalar.run(borrowed_tape(target),
                                       None if source is None else borrowed_tape(source),
                                       borrowed_count(width), borrowed_count(count))
        result = self.pool.acquire()
        append_bits(returned, result)
        result.rewind()
        returned.clear()
        erase_marker(returned)
        return result

    def run(self, bank, width, gaussians):
        positive(width)
        positive(gaussians)
        bank = borrowed_tape(bank)
        need(bank is not self.output, "distinct borrowed bank and protected return")
        self.rearm()
        extent = left = right = middle = updated = None
        failure = None
        with sealed_constructors(), self.scope.installed():
            try:
                extent = Count.product(gaussians, width)
                extent.multiply_small(2)
                left, right = self.pool.acquire(), self.pool.acquire()
                bank.rewind()
                # The family loop belongs to the finite selected compilation.
                # Only the Count-controlled body length varies with the input.
                for family in range(self.families):
                    if family == self.target:
                        copy_bits(bank, left, extent)
                    elif family == self.source:
                        copy_bits(bank, right, extent)
                    else:
                        skip_bits(bank, extent)
                need(bank.read() == BLANK, "complete selected bank extent")
                bank.rewind()
                left.rewind()
                right.rewind()
                middle = self.scalar_return(self.literals[0], left, None, width, gaussians)
                left.clear()
                updated = self.scalar_return(self.literals[1], middle, right, width, gaussians)
                middle.clear()
                right.clear()
                for family in range(self.families):
                    if family == self.target:
                        skip_bits(bank, extent)
                        copy_bits(updated, self.output, extent)
                        need(updated.read() == BLANK, "complete selected replacement")
                    else:
                        copy_bits(bank, self.output, extent)
                need(bank.read() == BLANK, "complete replacement bank")
            except CoefficientDomainError as error:
                failure = error
            finally:
                bank.rewind()
                for tape in (left, right, middle, updated):
                    if tape is not None:
                        tape.clear()
                if extent is not None:
                    extent.close()
                self.pool.empty()
        for tape in self.pool.tapes:
            erase_marker(tape)
        self.output.rewind()
        self.closed = True
        if failure is not None:
            self.output.clear()
            erase_marker(self.output)
            raise failure
        return self.output

    def commit(self, owned_bank):
        """Caller-authorized replacement; close before any recursive boundary."""
        bank = borrowed_tape(owned_bank)
        need(self.closed and bank is not self.output and self.output.read() in (ZERO, ONE),
             "completed nonempty prefix return for commit")
        bank.clear()
        append_bits(self.output, bank)
        bank.rewind()
        self.output.clear()
        erase_marker(self.output)


def selected_extent(unused_rows, body_gaussians):
    """N=Gamma*U*body; return one encoded whole-family cardinality."""
    from selected_binding import GAMMA
    positive(unused_rows)
    positive(body_gaussians)
    result = Count.product(unused_rows, body_gaussians)
    gamma = Count.literal(GAMMA)
    try:
        expanded = Count.product(gamma, result)
        return expanded
    finally:
        result.close()
        gamma.close()
