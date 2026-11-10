"""Complete binary fields by two sequential rectangle-padding passes."""
from contextlib import ExitStack

import source
_loader, padding, _outer = source.activate()
from cardinal_counts import Count, positive
from directory import append_tape
from encoded import compare, subtract
from ordinary import radix_power
from records import Tape
from role_parking import transfer
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from words import BLANK, LEFT, need


class Binary:
    """Borrow one completed radix-q engine; preserve arbitrary spectators."""
    def __init__(self, native):
        self.native = native
        self.pool = ScratchPool(96)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        self.closed = False

    def run(self, payload, width, prefixes, gap, suffix):
        need(self.output.read() == BLANK and borrowed_tape(payload) is not self.output,
             "distinct empty binary output")
        if self.closed:
            self.output.step(-1)
            marker = self.output.read()
            need(marker in (LEFT, BLANK), "consumed binary output origin")
            if marker == BLANK:
                self.output.write(LEFT)
            self.output.step(1)
            for tape in self.pool.tapes:
                initialize_marker(tape)
            self.closed = False
        for value in (prefixes, gap, suffix):
            positive(value)
        with sealed_constructors(), self.scope.installed(), ExitStack() as cleanup:
            owns_return_marker = False
            if width.zero():
                append_tape(borrowed_tape(payload), self.output)
                self.output.rewind()
                if not self.native.closed:
                    self.native.finish(False)
                    owns_return_marker = True
            else:
                binary = radix_power(width, 2)
                radix, digits = Count.literal(1), Count.literal(0)
                for value in (binary, radix, digits):
                    cleanup.callback(value.close)
                while compare(radix, binary) < 0:
                    radix.multiply_small(self.native.q)
                    digits.increment()
                added = subtract(radix, binary)
                middle = Count.product(gap, binary)
                first_body = Count.product(middle, suffix)
                middle.close()
                middle = Count.product(prefixes, radix)
                second_prefixes = Count.product(middle, gap)
                middle.close()
                for value in (added, first_body, second_prefixes):
                    cleanup.callback(value.close)
                first = padding.transform(borrowed_tape(payload), prefixes, binary, added, first_body)
                try:
                    padded = padding.transform(first, second_prefixes, binary, added, suffix)
                finally:
                    first.clear()
                try:
                    with self.scope.suspended():
                        returned = self.native.run(borrowed_tape(padded), borrowed_count(digits),
                                                   borrowed_count(prefixes), borrowed_count(gap),
                                                   borrowed_count(suffix))
                    owns_return_marker = True
                finally:
                    padded.clear()
                try:
                    first = padding.transform(returned, second_prefixes, binary, added, suffix,
                                              restricting=True)
                finally:
                    returned.clear()
                try:
                    result = padding.transform(first, prefixes, binary, added, first_body,
                                               restricting=True)
                finally:
                    first.clear()
                transfer(result, self.output)
                result.clear()
            # A consumed child output is now owned scratch of the binary caller.
            if owns_return_marker:
                erase_marker(self.native.output)
        self.pool.empty()
        for tape in self.pool.tapes:
            erase_marker(tape)
        self.closed = True
        return self.output
