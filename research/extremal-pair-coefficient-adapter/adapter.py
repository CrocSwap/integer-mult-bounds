"""Four direct encoded decay calls for two extremal source-pair tables.
Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Reuses unchanged JoyboyBrian/jmbarrancoml Gaussian scalar/runtime sources.
SPDX-License-Identifier: Apache-2.0
"""
from gaussian_sources import active
active()
from cardinal_counts import Count, positive
from encoded import compare, subtract
from gaussian_exponentials import Exponentials
from gaussian_rationals import Rational
from ring_words import Signed, power_two
from router_metadata import owned
from words import need


class Tables:
    """Own the precision Count and eight row-major numerator Counts."""
    def __init__(self, precision, entries):
        self.precision = precision
        self.entries = tuple(entries)

    def close(self):
        for value in reversed(self.entries):
            value.close()
        self.precision.close()


def decay(exponentials, square_alpha, numerator_factor, denominator):
    numerator = Signed(Count.product(square_alpha, numerator_factor))
    try:
        copied_denominator = Count(denominator)
    except BaseException:
        numerator.close()
        raise
    with owned(Rational(numerator, copied_denominator, False)) as (argument,):
        return exponentials.coefficient(argument, False, None)


def produce(p, alpha, s1, t1, s2, t2):
    """Borrow canonical head-at-one Counts; return nine distinct owned Counts.
    Domain: p,alpha>0,1<s_i<t_i<2s_i,alpha^2<=4p.
    Source-prime/alpha admission for A12 is a separate caller premise.
    """
    for value in (p, alpha, s1, t1, s2, t2):
        positive(value)
    outputs = []
    exponentials = None
    with owned(Count.literal(1), Count.literal(8), Count(p), Count(p),
               Count.product(alpha, alpha)) as (one, eight, precision, four_p, square_alpha):
        four_p.multiply_small(4)
        need(compare(square_alpha, four_p) <= 0, "polynomial extremal setup alpha guard")
        precision.add(eight)
        for source, target in ((s1,t1),(s2,t2)):
            with owned(Count(source)) as (twice_source,):
                twice_source.multiply_small(2)
                need(compare(one,source)<0 and compare(source,target)<0
                     and compare(target,twice_source)<0, "strict extremal source ratio")
        with owned(Count(square_alpha)) as (argument_bound,):
            argument_bound.multiply_small(2)
            try:
                exponentials = Exponentials(precision, argument_bound)
                outputs.append(Count(precision))
                for source, target in ((s1,t1),(s2,t2)):
                    with owned(subtract(target,source),Count(source)) as (A,twice_source):
                        A.multiply_small(2)
                        A.increment()
                        twice_source.multiply_small(2)
                        with owned(subtract(twice_source,one)) as (B,):
                            outputs.append(power_two(precision))
                            outputs.append(decay(exponentials,square_alpha,A,source))
                            outputs.append(decay(exponentials,square_alpha,B,source))
                            outputs.append(power_two(precision))
                result = Tables(outputs[0], outputs[1:])
                outputs = []
                return result
            finally:
                for value in reversed(outputs):
                    value.close()
                if exponentials is not None:
                    exponentials.close()
