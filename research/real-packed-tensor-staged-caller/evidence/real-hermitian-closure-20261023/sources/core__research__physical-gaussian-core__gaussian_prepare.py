"""Fixed-role page preparation and explicit production-parameter binding."""
from gaussian_sources import active
active()
from cardinal_counts import Count, positive
from encoded import compare, subtract
from gaussian_axis import Axis
from gaussian_rationals import Rational
from gaussian_window import Window
from records import Tape
from ring_words import Signed, add, difference, fits
from router_metadata import ceiling_log, owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, erase_marker, initialize_marker,
                     sealed_constructors)
from twiddle_setup import quotient
from words import BLANK, RIGHT, need


def endpoint(s, t, target):
    with owned(target.copy(), Signed(Count.literal(1))) as (twice, one):
        twice.magnitude.multiply_small(2)
        with owned(difference(twice, one)) as (shifted,):
            numerator = Signed(Count.product(shifted.magnitude, s), shifted.negative)
    denominator = Count(t)
    denominator.multiply_small(2)
    with owned(Rational(numerator, denominator)) as (value,):
        return value.integer_part(True)


class ProductionPlan:
    def __init__(self, s, t, d, u, p, target_start, target_length, core_start, core_length):
        self.fields = {}
        try:
            for value in (s, t, d, u, p, target_length, core_length):
                positive(value)
            with owned(Count.literal(101)) as (minimum,):
                need(compare(p, minimum) >= 0, "production Gaussian target precision at least101")
            fits(s, p)
            fits(t, p)
            with owned(Count(p)) as (descriptor_width,):
                descriptor_width.increment()
                descriptor_width.increment()
                for value in (target_start.magnitude, target_length, core_start.magnitude, core_length):
                    fits(value, descriptor_width)
            need(compare(s, t) < 0, "production Gaussian expanding axis")
            with owned(Count(s)) as (twice_s,):
                twice_s.multiply_small(2)
                need(compare(t, twice_s) < 0, "production near-one Gaussian axis")
            with owned(Count(p)) as (eight_p,):
                eight_p.multiply_small(8)
                with owned(ceiling_log(eight_p)) as (minimum_u,):
                    need(compare(u, minimum_u) >= 0, "production logarithmic Gaussian concentration")
            with owned(Count.product(u, d)) as (normalization,):
                need(compare(normalization, p) <= 0, "production Gaussian similarity guard")
            with owned(subtract(t, s)) as (gap,):
                with owned(Count.product(d, gap)) as (lower,):
                    lower.multiply_small(4)
                    need(compare(lower, s) > 0, "production strict lower axis-ratio bound")
                with owned(Count(d), Count.literal(1)) as (twice_d, one):
                    twice_d.multiply_small(2)
                    with owned(subtract(twice_d, one)) as (factor,):
                        with owned(Count.product(factor, gap)) as (upper,):
                            need(compare(upper, s) < 0, "production strict upper axis-ratio bound")
            self.keep("P", Count(p))
            self.P.multiply_small(32768)
            with owned(Count(p)) as (numerator,):
                numerator.multiply_small(16)
                with owned(quotient(numerator, u, True)) as (target,):
                    self.keep("w", Count.literal(0))
                    while True:
                        with owned(Count.product(self.w, self.w)) as (square,):
                            if compare(square, target) >= 0:
                                break
                        self.w.increment()
            self.w.increment()
            self.w.increment()
            with owned(Count(self.w), Count.literal(2)) as (minimum_d, two):
                minimum_d.multiply_small(4)
                minimum_d.add(two)
                need(compare(d, minimum_d) > 0, "production cell/band separation")
            self.keep("start", endpoint(s, t, target_start))
            with owned(Signed(Count(target_length))) as (length,):
                with owned(add(target_start, length)) as (end,):
                    self.keep("end", endpoint(s, t, end))
            with owned(difference(self.end, self.start)) as (length,):
                need(not length.negative and not length.magnitude.zero(), "production nonempty principal window")
                self.keep("m", Count(length.magnitude))
            with owned(Count(self.m)) as (covered,):
                covered.add(self.w)
                need(compare(covered, s) < 0, "production principal complement gap")
            with owned(Count.product(p, p)) as (squared,):
                self.keep("margin", Count.product(squared, self.w))
                self.margin.multiply_small(512)
            with owned(difference(core_start, self.start)) as (left,):
                need(not left.negative and compare(left.magnitude, self.margin) > 0,
                     "production left core halo exceeds locality radius")
            with owned(Signed(Count(core_length))) as (length,):
                with owned(add(core_start, length)) as (core_end,):
                    with owned(difference(self.end, core_end)) as (right,):
                        need(not right.negative and compare(right.magnitude, self.margin) > 0,
                             "production right core halo exceeds locality radius")
        except BaseException:
            self.close()
            raise

    def keep(self, name, value):
        need(name not in self.fields, "one production Gaussian parameter role")
        self.fields[name] = value
        return value

    def __getattr__(self, name):
        return self.fields[name]

    def close(self):
        for value in reversed(tuple(self.fields.values())):
            value.close()
        self.fields.clear()


class Preparation:
    def __init__(self):
        self.pool = ScratchPool(1024)
        self.scope = OuterScope(self.pool)
        self.parameter_pool = ScratchPool(128)
        self.parameter_scope = OuterScope(self.parameter_pool)
        self.output = Tape()
        self.closed = True
        self.calls = 0
        for value in (*self.pool.tapes, *self.parameter_pool.tapes, self.output):
            erase_marker(value)

    def run_explicit(self, s, t, u, w, p, precision, target_start, target_length, core_start, core_length):
        """Prepare the declared finite grid; the production method fixes its domain."""
        s, t, u, w, p, precision, target_length, core_length = (borrowed_count(value) for value in
            (s, t, u, w, p, precision, target_length, core_length))
        target_start = Signed(borrowed_count(target_start.magnitude), target_start.negative)
        core_start = Signed(borrowed_count(core_start.magnitude), core_start.negative)
        parameters = (s, t, u, w, p, precision, target_length, core_length,
                      target_start.magnitude, core_start.magnitude)
        need(all(value.tape not in (*self.pool.tapes, self.output) for value in parameters),
             "external Gaussian preparation parameters")
        need(self.closed and not self.pool.live and self.output.read() == BLANK,
             "consume prior Gaussian prepared page")
        for value in (s, t, u, w, p, precision, target_length, core_length):
            positive(value)
        need(compare(p, precision) <= 0, "Gaussian preparation work precision covers target")
        for value in (*self.pool.tapes, self.output):
            initialize_marker(value)
        self.closed = False
        axis = window = None
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    axis = Axis(s, t, u, w, precision, self.pool)
                    window = Window(axis, target_start, target_length, core_start, core_length, p, self.pool)
                    window.page.rewind()
                    while window.page.read() != BLANK:
                        value = window.page.read()
                        need(value in (0, 1, RIGHT), "canonical complete Gaussian page alphabet")
                        self.output.append(value)
                        window.page.step(1)
                    self.calls += 1
                    succeeded = True
                finally:
                    if window is not None:
                        window.close()
                    if axis is not None:
                        axis.close()
                    for value in parameters:
                        value.rewind()
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

    def run_production(self, s, t, d, u, p, target_start, target_length, core_start, core_length):
        need(self.closed and not self.pool.live and not self.parameter_pool.live and self.output.read() == BLANK,
             "consume prior production Gaussian page")
        parameters = tuple(borrowed_count(value) for value in (s, t, d, u, p, target_length, core_length))
        s, t, d, u, p, target_length, core_length = parameters
        target_start = Signed(borrowed_count(target_start.magnitude), target_start.negative)
        core_start = Signed(borrowed_count(core_start.magnitude), core_start.negative)
        need(all(value.tape not in (*self.parameter_pool.tapes, *self.pool.tapes, self.output)
                 for value in (*parameters, target_start.magnitude, core_start.magnitude)),
             "external production Gaussian parameters")
        for value in self.parameter_pool.tapes:
            initialize_marker(value)
        plan = None
        try:
            with sealed_constructors(), self.parameter_scope.installed():
                try:
                    plan = ProductionPlan(s, t, d, u, p, target_start, target_length, core_start, core_length)
                    with self.parameter_scope.suspended():
                        return self.run_explicit(s, t, u, plan.w, p, plan.P,
                                                 target_start, target_length, core_start, core_length)
                finally:
                    if plan is not None:
                        plan.close()
                    for value in (*parameters, target_start.magnitude, core_start.magnitude):
                        value.rewind()
                    self.parameter_pool.empty()
        finally:
            for value in self.parameter_pool.tapes:
                erase_marker(value)
