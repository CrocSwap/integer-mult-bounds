"""Exact O(n log²(n+2)) word multiplication with an acyclic FFT dependency."""
from fft_word_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import append_bits
from encoded import compare
from fft_word_codec import pack, unpack
from fft_word_plan import WordPlan
from records import Tape
from ring_engine import RingProduct
from ring_words import fits
from router_metadata import owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from word_product import WordProduct
from words import BLANK, need


class FftWord:
    def __init__(self, base_bits=16):
        need(type(base_bits) is int and base_bits >= 2, "fixed FFT-word base cutoff")
        self.base_bits = base_bits
        self.base, self.product = WordProduct(), RingProduct()
        self.pool = ScratchPool(256)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        self.a = self.b = None
        self.closed = True
        self.calls = dict(base=0, fft=0)
        # Inspection-only canonical roles; each child manages its own markers.
        self.canonical = (*self.base.canonical, self.base.output, self.product.output,
                          *self.product.word.canonical, self.product.word.output,
                          self.product.twiddles.output)
        for value in (*self.pool.tapes, self.output):
            erase_marker(value)

    def idle(self):
        self.product.idle()
        need(self.base.closed and not self.base.pool.live
             and self.product.closed and not self.product.pool.live
             and all(value.read() == BLANK for value in self.canonical),
             "consumed FFT-word children")

    def run(self, first, second, width):
        first, second, width = (borrowed_count(v) for v in (first, second, width))
        need(all(v.tape not in (*self.canonical, *self.pool.tapes, self.output)
                 for v in (first, second, width)), "borrowed external FFT-word ports")
        need(self.closed and not self.pool.live and self.output.read() == BLANK
             and self.a is self.b is None, "consume prior FFT-word output")
        positive(width)
        self.idle()
        for value in (*self.pool.tapes, self.output):
            initialize_marker(value)
        self.closed = False
        plan = None
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    fits(first, width)
                    fits(second, width)
                    with owned(Count.literal(self.base_bits)) as (cutoff,):
                        small = compare(width, cutoff) <= 0
                    if small:
                        with self.scope.suspended():
                            returned = self.base.run(first, second, width)
                        try:
                            append_bits(returned, self.output)
                        finally:
                            returned.clear()
                            erase_marker(returned)
                        self.calls["base"] += 1
                    else:
                        plan = WordPlan(width)
                        plan.compile()
                        self.a = pack(first, plan, self.pool)
                        self.b = pack(second, plan, self.pool)
                        with self.scope.suspended():
                            returned = self.product.run(borrowed_tape(self.a), borrowed_tape(self.b),
                                *(borrowed_count(v) for v in (plan.one, plan.p, plan.ell, plan.one)))
                        try:
                            unpack(returned, self.output, plan)
                        finally:
                            returned.clear()
                            erase_marker(returned)
                        self.calls["fft"] += 1
                    self.idle()
                    succeeded = True
                finally:
                    for value in (first, second, width):
                        value.rewind()
                    for value in (self.a, self.b):
                        if value is not None:
                            value.clear()
                    self.a = self.b = None
                    if plan is not None:
                        plan.close()
                    self.pool.empty()
        finally:
            for value in self.pool.tapes:
                erase_marker(value)
            self.output.rewind()
            if not succeeded:
                self.output.clear()
                erase_marker(self.output)
            self.closed = True
        return self.output
