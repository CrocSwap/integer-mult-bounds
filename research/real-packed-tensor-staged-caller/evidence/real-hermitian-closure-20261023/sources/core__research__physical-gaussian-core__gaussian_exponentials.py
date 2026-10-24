"""Directed real Gaussian coefficients from encoded Machin/Taylor intervals."""
from contextlib import closing
from gaussian_sources import active
active()
from cardinal_counts import Count, positive
from encoded import compare, subtract
from gaussian_rationals import Rational
from ring_words import Signed, power_two, right_shift
from router_metadata import ceiling_log, indices, owned
from twiddle_setup import pi_interval, quotient
from words import RIGHT, need


def ceil_shift(value, amount):
    result = right_shift(value, amount)
    value.rewind()
    discarded = False
    try:
        for _ in indices(amount):
            if value.read() != RIGHT:
                bit = value.read()
                need(bit in (0, 1), "binary directed shift")
                discarded = discarded or bit == 1
                value.step(1)
        if discarded:
            result.increment()
        return result
    except BaseException:
        result.close()
        raise
    finally:
        value.rewind()


class Exponentials:
    """Prepare once per axis; bound all nonnegative rational arguments."""
    def __init__(self, precision, argument_bound):
        positive(precision)
        positive(argument_bound)
        self.precision, self.argument_bound = precision, argument_bound
        self.fields = {}
        self.calls = 0
        self.taylor_steps = 0
        self.early_stops = 0
        try:
            self.keep("X", Count(argument_bound))
            self.X.multiply_small(4)
            with owned(Count(self.X)) as (eight_bound,):
                eight_bound.increment()
                eight_bound.multiply_small(8)
                self.keep("k", ceiling_log(eight_bound))
            with owned(Count(precision), Count.literal(16)) as (height, sixteen):
                height.add(self.X)
                height.add(self.k)
                height.add(sixteen)
                with owned(ceiling_log(height)) as (log_height,):
                    self.keep("R", Count(precision))
                    with owned(Count(self.X), Count(self.k), Count(log_height),
                               Count.literal(64)) as (x, k, logarithm, guard):
                        x.multiply_small(4)
                        k.multiply_small(4)
                        logarithm.multiply_small(2)
                        for value in (x, k, logarithm, guard):
                            self.R.add(value)
            self.keep("shift", subtract(self.R, precision))
            self.keep("unit", power_two(self.R))
            self.keep("J", Count(self.R))
            if self.J.divide_small(4):
                self.J.increment()
            self.keep("terms", Count(self.R))
            if self.terms.divide_small(3):
                self.terms.increment()
            with owned(Count.literal(8)) as (eight,):
                self.J.add(eight)
                self.terms.add(eight)
            lower, upper = pi_interval(self.unit, self.J)
            self.keep("pi_lower", lower)
            self.keep("pi_upper", upper)
            with owned(Count(self.unit), Count(self.unit)) as (three, four):
                three.multiply_small(3)
                four.multiply_small(4)
                need(not lower.negative and not upper.negative
                     and compare(three, lower.magnitude) < 0
                     and compare(upper.magnitude, four) < 0,
                     "positive certified Gaussian pi interval")
        except BaseException:
            self.close()
            raise

    def keep(self, name, value):
        need(name not in self.fields, "one Gaussian exponential setup role")
        self.fields[name] = value
        return value

    def __getattr__(self, name):
        return self.fields[name]

    def close(self):
        for value in reversed(tuple(self.fields.values())):
            value.close()
        self.fields.clear()

    def positive_interval(self, argument):
        need(not argument.numerator.negative, "nonnegative Gaussian decay argument")
        with owned(Signed(Count(self.argument_bound))) as (bound,):
            with owned(Rational.integer(bound)) as (maximum,):
                need(argument.compare(maximum) <= 0, "Gaussian argument within prepared bound")
        with owned(Count.product(argument.numerator.magnitude, self.pi_lower.magnitude)) as (product,):
            lower = quotient(product, argument.denominator)
        try:
            with owned(Count.product(argument.numerator.magnitude, self.pi_upper.magnitude)) as (product,):
                upper = quotient(product, argument.denominator, True)
        except BaseException:
            lower.close()
            raise
        try:
            y_lower = right_shift(lower, self.k)
            try:
                y_upper = ceil_shift(upper, self.k)
            except BaseException:
                y_lower.close()
                raise
        finally:
            lower.close()
            upper.close()
        term_lower = term_upper = total_lower = total_upper = degree = None
        try:
            with owned(Count(y_upper)) as (eight_y,):
                eight_y.multiply_small(8)
                need(compare(eight_y, self.unit) <= 0, "Gaussian Taylor range at most one eighth")
            term_lower, term_upper = Count(self.unit), Count(self.unit)
            total_lower, total_upper = Count(self.unit), Count(self.unit)
            degree = Count.literal(1)
            with owned(Count.literal(1)) as (one,):
                with closing(indices(self.terms)) as steps:
                    for _ in steps:
                        with owned(Count.product(term_lower, y_lower)) as (product,):
                            with owned(right_shift(product, self.R)) as (scaled,):
                                following_lower = quotient(scaled, degree)
                        try:
                            with owned(Count.product(term_upper, y_upper)) as (product,):
                                with owned(ceil_shift(product, self.R)) as (scaled,):
                                    following_upper = quotient(scaled, degree, True)
                        except BaseException:
                            following_lower.close()
                            raise
                        term_lower.close()
                        term_upper.close()
                        term_lower, term_upper = following_lower, following_upper
                        total_lower.add(term_lower)
                        total_upper.add(term_upper)
                        self.taylor_steps += 1
                        if compare(term_upper, one) <= 0:
                            self.early_stops += 1
                            break
                        degree.increment()
            # At early exit the tail is <=h/7; after all terms, 3*terms>R gives <h.
            total_upper.increment()
            for _ in indices(self.k):
                with owned(Count.product(total_lower, total_lower)) as (square,):
                    following_lower = right_shift(square, self.R)
                try:
                    with owned(Count.product(total_upper, total_upper)) as (square,):
                        following_upper = ceil_shift(square, self.R)
                except BaseException:
                    following_lower.close()
                    raise
                total_lower.close()
                total_upper.close()
                total_lower, total_upper = following_lower, following_upper
            with owned(subtract(total_upper, total_lower), power_two(self.shift)) as (spread, unit):
                need(compare(spread, unit) < 0, "certified exponential interval below target unit")
            result = total_lower, total_upper
            total_lower = total_upper = None
            return result
        finally:
            for value in (y_lower, y_upper, term_lower, term_upper, total_lower, total_upper, degree):
                if value is not None:
                    value.close()

    def grid_interval(self, argument, positive_exponent=False, binary_scale=None):
        need(type(positive_exponent) is bool, "finite exponential sign")
        lower, upper = self.positive_interval(argument)
        try:
            if not positive_exponent:
                with owned(Count.product(self.unit, self.unit)) as (squared_unit,):
                    following_lower = quotient(squared_unit, upper)
                    try:
                        following_upper = quotient(squared_unit, lower, True)
                    except BaseException:
                        following_lower.close()
                        raise
                lower.close()
                upper.close()
                lower, upper = following_lower, following_upper
            with owned(Count(self.shift)) as (shift,):
                if binary_scale is not None:
                    shift.add(binary_scale)
                result_lower = right_shift(lower, shift)
                try:
                    result_upper = ceil_shift(upper, shift)
                except BaseException:
                    result_lower.close()
                    raise
            try:
                with owned(subtract(result_upper, result_lower), Count.literal(3)) as (spread, three):
                    need(compare(spread, three) <= 0, "Gaussian coefficient enclosure below four ulps")
                self.calls += 1
                return result_lower, result_upper
            except BaseException:
                result_lower.close()
                result_upper.close()
                raise
        finally:
            lower.close()
            upper.close()

    def coefficient(self, argument, positive_exponent=False, binary_scale=None):
        lower, upper = self.grid_interval(argument, positive_exponent, binary_scale)
        upper.close()
        return lower
