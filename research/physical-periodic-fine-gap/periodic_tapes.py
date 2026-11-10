"""Separately paid physical emission of the certified periodic source pages.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Host integers occur only in input-independent preparation and its serialization.
"""
from gaussian_sources import active
active()
from cardinal_counts import Count
from gaussian_rationals import write_count
from records import Tape
from ring_words import Signed, write_signed
from router_metadata import owned
from session import erase_marker
from words import need

NAMES = ("Finv", "F", "mu_minus", "mu_plus", "residual_minus", "residual_plus")


def emit(values, target, width):
    for value in values:
        with owned(Signed(Count.literal(abs(value)), value < 0)) as (word,):
            write_signed(word, target, width)


class EncodedPeriodicPages:
    def __init__(self, bundle):
        self.counts, self.streams, self.other = (), (), ()
        try:
            p, folded = bundle.plan, bundle.folded_plan
            for value in (p.source_size, p.target_size, p.boundary_size, len(bundle.runs),
                          p.band, p.W, p.f, folded['width'], folded['precision']):
                self.counts += (Count.literal(value),)
            for _ in NAMES:
                self.streams += (Tape(),)
            for _ in range(7):
                self.other += (Tape(),)
            (self.target_mask, self.boundary_mask, self.headers, self.sb,
             self.k, self.lower, self.upper) = self.other
            for target, values in ((self.target_mask, bundle.target_mask),
                                   (self.boundary_mask, bundle.boundary_mask)):
                for value in values:
                    need(value in (0, 1), "prepared binary mask")
                    target.append(value)
            for run in bundle.runs:
                native = run.native
                need(len(native.streams['residual_minus']) == len(native.streams['residual_plus']),
                     "equal residual page extents")
                for value in (*run.header, len(native.streams['residual_minus'])):
                    with owned(Count.literal(value)) as (count,):
                        write_count(count, self.headers)
                with owned(Count.literal(native.plan.W)) as (width,):
                    for name, target in zip(NAMES, self.streams):
                        emit(native.streams[name], target, width)
            for values, target, width in ((bundle.sb_coefficients, self.sb, self.counts[5]),
                         (bundle.k_coefficients, self.k, self.counts[5]),
                         (folded['lower'], self.lower, self.counts[7]),
                         (folded['upper'], self.upper, self.counts[7])):
                emit(values, target, width)
            for tape in (*self.streams, *self.other):
                tape.rewind()
        except BaseException:
            self.close()
            raise

    def ports(self):
        return (*self.streams, *self.other, *(v.tape for v in self.counts))

    def close(self):
        for tape in (*self.streams, *self.other):
            tape.clear(); erase_marker(tape)
        self.streams, self.other = (), ()
        for count in self.counts:
            count.close(); erase_marker(count.tape)
        self.counts = ()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
