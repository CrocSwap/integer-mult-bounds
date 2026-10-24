"""Encoded radix geometry for exact recovery through Q_p(fg/r)."""
from fft_word_sources import active
active()
from cardinal_counts import Count
from encoded import compare, divide, subtract
from ring_words import power_two
from router_metadata import ceiling_log, owned
from words import need


def ceiling_divide(numerator, denominator):
    result, remainder = divide(numerator, denominator)
    try:
        if not remainder.zero():
            result.increment()
        return result
    except BaseException:
        result.close()
        raise
    finally:
        remainder.close()


class WordPlan:
    def __init__(self, width):
        self.n = width
        self.fields = {}

    def keep(self, name, value):
        need(name not in self.fields, "one FFT-word numerical role")
        self.fields[name] = value
        return value

    def __getattr__(self, name):
        return self.fields[name]

    def compile(self):
        with owned(Count.literal(2)) as (two,):
            need(compare(self.n, two) >= 0, "FFT-word extent at least two")
        self.keep("one", Count.literal(1))
        self.keep("b", ceiling_log(self.n))
        self.keep("q", ceiling_divide(self.n, self.b))
        with owned(Count(self.q)) as (twice,):
            twice.multiply_small(2)
            self.keep("ell", ceiling_log(twice))
        self.keep("r", power_two(self.ell))
        self.keep("p", Count(self.b))
        self.p.multiply_small(2)
        self.p.add(self.ell)
        self.keep("component", Count(self.p))
        self.component.increment()
        self.component.increment()
        self.keep("shift", subtract(self.p, self.b))
        self.keep("output_bits", Count(self.n))
        self.output_bits.multiply_small(2)
        with owned(Count(self.r)) as (records,):
            records.multiply_small(2)
            with owned(subtract(records, self.q)) as (zeros,):
                self.keep("padding_bits", Count.product(zeros, self.component))
                self.padding_bits.multiply_small(2)
        self.keep("dummy_bits", Count.product(self.r, self.component))
        self.dummy_bits.multiply_small(2)
        with owned(subtract(self.p, self.one)) as (exponent,):
            self.keep("coefficient_limit", power_two(exponent))

    def close(self):
        for value in reversed(tuple(self.fields.values())):
            value.close()
        self.fields.clear()
