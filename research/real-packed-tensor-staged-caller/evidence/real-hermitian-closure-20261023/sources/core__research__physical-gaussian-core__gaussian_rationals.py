"""Reduced exact setup rationals on encoded tapes; no host payload integers."""
from gaussian_sources import active
active()
from cardinal_counts import Count, positive
from encoded import compare, divide
from ring_words import Signed, add, difference, left_shift
from router_metadata import owned
from session import borrowed_tape
from words import RIGHT, need


def exact_quotient(numerator, denominator):
    quotient, remainder = divide(numerator, denominator)
    try:
        need(remainder.zero(), "exact rational integer division")
        return quotient
    except BaseException:
        quotient.close()
        raise
    finally:
        remainder.close()


def gcd(first, second):
    left, right = Count(first), Count(second)
    try:
        while not right.zero():
            quotient, remainder = divide(left, right)
            quotient.close()
            left.close()
            left, right = right, remainder
        result, left = left, None
        return result
    finally:
        if left is not None:
            left.close()
        right.close()


def signed_product(first, second):
    return Signed(Count.product(first.magnitude, second.magnitude),
                  first.negative != second.negative)


class Rational:
    """Own the signed numerator and positive denominator; reduce on creation."""
    def __init__(self, numerator, denominator, reduce=True):
        self.numerator, self.denominator = numerator, denominator
        try:
            positive(denominator)
            if reduce:
                with owned(gcd(numerator.magnitude, denominator)) as (common,):
                    new_n = exact_quotient(numerator.magnitude, common)
                    try:
                        new_d = exact_quotient(denominator, common)
                    except BaseException:
                        new_n.close()
                        raise
                self.numerator = Signed(new_n, numerator.negative)
                self.denominator = new_d
                numerator.close()
                denominator.close()
        except BaseException:
            self.close()
            raise

    @classmethod
    def literal(cls, value):
        need(type(value) is int and -16 <= value <= 16, "fixed rational program literal")
        return cls(Signed(Count.literal(abs(value)), value < 0), Count.literal(1), False)

    @classmethod
    def integer(cls, value):
        return cls(value.copy(), Count.literal(1), False)

    def close(self):
        self.numerator.close()
        self.denominator.close()

    def copy(self):
        return Rational(self.numerator.copy(), Count(self.denominator), False)

    def negated(self):
        return Rational(self.numerator.negated(), Count(self.denominator), False)

    def plus(self, other, subtract=False):
        with owned(Signed(Count.product(self.numerator.magnitude, other.denominator),
                          self.numerator.negative)) as (left,):
            with owned(Signed(Count.product(other.numerator.magnitude, self.denominator),
                              other.numerator.negative)) as (right,):
                numerator = difference(left, right) if subtract else add(left, right)
        try:
            denominator = Count.product(self.denominator, other.denominator)
        except BaseException:
            numerator.close()
            raise
        return Rational(numerator, denominator)

    def minus(self, other):
        return self.plus(other, True)

    def times(self, other):
        numerator = signed_product(self.numerator, other.numerator)
        try:
            denominator = Count.product(self.denominator, other.denominator)
        except BaseException:
            numerator.close()
            raise
        return Rational(numerator, denominator)

    def over(self, other):
        need(not other.numerator.magnitude.zero(), "nonzero rational divisor")
        numerator = Signed(Count.product(self.numerator.magnitude, other.denominator),
                           self.numerator.negative != other.numerator.negative)
        try:
            denominator = Count.product(self.denominator, other.numerator.magnitude)
        except BaseException:
            numerator.close()
            raise
        return Rational(numerator, denominator)

    def reciprocal(self):
        need(not self.numerator.magnitude.zero(), "nonzero rational reciprocal")
        return Rational(Signed(Count(self.denominator), self.numerator.negative),
                        Count(self.numerator.magnitude), False)

    def compare(self, other):
        if self.numerator.negative != other.numerator.negative:
            return -1 if self.numerator.negative else 1
        with owned(Count.product(self.numerator.magnitude, other.denominator)) as (left,):
            with owned(Count.product(other.numerator.magnitude, self.denominator)) as (right,):
                order = compare(left, right)
        return -order if self.numerator.negative else order

    def rounded(self, precision):
        with owned(left_shift(self.numerator.magnitude, precision)) as (scaled,):
            quotient, remainder = divide(scaled, self.denominator)
        remainder.close()
        return Signed(quotient, self.numerator.negative)

    def integer_part(self, ceiling=False):
        quotient, remainder = divide(self.numerator.magnitude, self.denominator)
        try:
            if not remainder.zero() and ceiling != self.numerator.negative:
                quotient.increment()
            return Signed(quotient, self.numerator.negative)
        except BaseException:
            quotient.close()
            raise
        finally:
            remainder.close()


def write_count(value, target):
    value.rewind()
    try:
        while value.read() != RIGHT:
            bit = value.read()
            need(bit in (0, 1), "canonical rational record digit")
            target.append(bit)
            value.step(1)
        target.append(RIGHT)
    finally:
        value.rewind()


def read_count(source):
    result = Count.literal(0)
    borrowed_tape(result.tape).clear()
    seen = multiple = False
    last = 0
    try:
        while source.read() != RIGHT:
            bit = source.read()
            need(bit in (0, 1), "complete rational record digit")
            multiple, seen, last = seen, True, bit
            result.tape.append(bit)
            source.step(1)
        need(seen and (last == 1 or not multiple), "canonical rational record extent")
        source.step(1)
        result.tape.append(RIGHT)
        result.rewind()
        return result
    except BaseException:
        result.close()
        raise


def write_rational(value, target):
    target.append(int(value.numerator.negative))
    write_count(value.numerator.magnitude, target)
    write_count(value.denominator, target)


def read_rational(source):
    sign = source.read()
    need(sign in (0, 1), "rational record sign")
    source.step(1)
    numerator = read_count(source)
    try:
        need(not sign or not numerator.zero(), "canonical rational zero sign")
        denominator = read_count(source)
    except BaseException:
        numerator.close()
        raise
    return Rational(Signed(numerator, bool(sign)), denominator, False)


def transfer_record(source, target=None):
    """Consume one serialized rational without constructing numerical carriers."""
    sign = source.read()
    need(sign in (0, 1), "rational stream sign")
    if target is not None:
        target.append(sign)
    source.step(1)
    for _ in range(2):
        seen = multiple = False
        last = 0
        while source.read() != RIGHT:
            bit = source.read()
            need(bit in (0, 1), "complete rational stream")
            multiple, seen, last = seen, True, bit
            if target is not None:
                target.append(bit)
            source.step(1)
        need(seen and (last == 1 or not multiple), "canonical rational stream extent")
        if target is not None:
            target.append(RIGHT)
        source.step(1)
