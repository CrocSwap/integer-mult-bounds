"""Unbounded setup integers on canonical binary Count tapes."""
from dataclasses import dataclass

import source
source.activate()
from cardinal_counts import Count, positive
from stream import Counter
from words import LEFT, ONE, RIGHT, ZERO, need


def compare(left, right):
    if left is right or left.tape is right.tape:
        return 0
    left.rewind()
    right.rewind()
    order = 0
    try:
        while left.read() != RIGHT and right.read() != RIGHT:
            a, b = left.read(), right.read()
            need(a in (ZERO, ONE) and b in (ZERO, ONE), "binary comparison digits")
            if a != b:
                order = 1 if a == ONE else -1
            left.step(1)
            right.step(1)
        if left.read() != RIGHT:
            return 1
        if right.read() != RIGHT:
            return -1
        return order
    finally:
        left.rewind()
        right.rewind()


def subtract(left, right):
    need(compare(left, right) >= 0, "nonnegative setup difference")
    result = Count(left)
    right.rewind()
    borrow = 0
    try:
        while result.read() != RIGHT:
            done = right.read() == RIGHT
            difference = result.read() - (ZERO if done else right.read()) - borrow
            borrow = int(difference < 0)
            result.tape.write(difference + 2 * borrow)
            result.step(1)
            if not done:
                right.step(1)
        need(not borrow and right.read() == RIGHT, "complete setup subtraction")
        result.normalize()
        return result
    except BaseException:
        result.close()
        raise
    finally:
        right.rewind()


def divide(numerator, denominator):
    positive(denominator)
    divisor = Count(denominator)
    quotient, remainder = Count.literal(0), Count.literal(0)
    numerator.msb()
    try:
        while numerator.read() != LEFT:
            bit = numerator.read()
            need(bit in (ZERO, ONE), "division numerator digit")
            quotient.multiply_small(2)
            remainder.multiply_small(2)
            if bit == ONE:
                remainder.increment()
            if compare(remainder, divisor) >= 0:
                following = subtract(remainder, divisor)
                remainder.close()
                remainder = following
                quotient.increment()
            numerator.step(-1)
        numerator.step(1)
        return quotient, remainder
    except BaseException:
        quotient.close()
        remainder.close()
        raise
    finally:
        numerator.rewind()
        divisor.close()


def product(left, right, cap=None):
    if cap is not None:
        if (compare(left, cap) >= 0 and not right.zero()
                or compare(right, cap) >= 0 and not left.zero()):
            return Count(cap)
    value = Count.product(left, right)
    if cap is not None and compare(value, cap) > 0:
        value.close()
        return Count(cap)
    return value


def fixed_power(value, exponent, cap=None):
    """Exponent is a compiled source constant; optional saturation is exact."""
    need(type(exponent) is int and exponent >= 0, "fixed source exponent")
    result, factor = Count.literal(1), Count(value)
    try:
        while exponent:
            if exponent & 1:
                following = product(result, factor, cap)
                result.close()
                result = following
            exponent >>= 1
            if exponent:
                following = product(factor, factor, cap)
                factor.close()
                factor = following
        return result
    except BaseException:
        result.close()
        raise
    finally:
        factor.close()


def atom_width(original, numerator=17, denominator=10000):
    """Least w with w^denominator >= e^numerator, by encoded bisection."""
    positive(original)
    target = fixed_power(original, numerator)
    low, high = Count.literal(1), Count(original)
    try:
        while compare(low, high) < 0:
            middle = Count(low)
            middle.add(high)
            middle.divide_small(2)
            power = fixed_power(middle, denominator, target)
            above = compare(power, target) >= 0
            power.close()
            if above:
                high.close()
                high = middle
            else:
                low.close()
                middle.increment()
                low = middle
        result, low = low, None
        return result
    finally:
        if low is not None:
            low.close()
        high.close()
        target.close()


@dataclass(frozen=True)
class Profile:
    numerator: int = 17
    denominator: int = 10000
    dimension: int = 64
    child_rank: int = 42
    row_factor: int = 269241600


def select(original, q, profile=Profile()):
    """Return owned encoded parameters; q/profile are compile-time constants."""
    width = atom_width(original, profile.numerator, profile.denominator)
    dimension, one = Count.literal(profile.dimension), Count.literal(1)
    cursor, depth = Count(original), Count.literal(0)
    stock, rows, borrowed = Count.literal(1), Count.literal(1), Count.literal(0)
    body, remainder = Count.literal(0), Count.literal(0)
    try:
        while compare(cursor, dimension) >= 0:
            cursor.divide_small(profile.dimension)
            if profile.child_rank != 1:
                cursor.multiply_small(profile.child_rank)
            depth.increment()
        if not depth.zero():
            order = 1
            for position in range(profile.dimension):
                order *= q ** profile.dimension - q ** position
            level = Count.literal(profile.row_factor * order)
            digits = subtract(width, one)
            repeats = Counter(digits)
            digits.close()
            try:
                while not repeats.finished:
                    level.multiply_small(q ** (profile.dimension ** 2))
                    repeats.decrement()
                levels = Counter(depth)
                try:
                    while not levels.finished:
                        following = Count.product(stock, level)
                        stock.close()
                        stock = following
                        levels.decrement()
                finally:
                    levels.close()
            finally:
                level.close()
                repeats.close()
        while compare(rows, stock) < 0:
            rows.multiply_small(q)
            borrowed.increment()
        twice = Count(borrowed)
        twice.multiply_small(2)
        fits = compare(twice, original) < 0
        twice.close()
        if fits:
            remaining = subtract(original, borrowed)
            body.close()
            remainder.close()
            try:
                body, remainder = divide(remaining, width)
            finally:
                remaining.close()
            fits = compare(body, dimension) >= 0
        return dict(fits=fits, width=width, depth=depth, stock=stock,
                    rows=rows, borrowed=borrowed, body=body, remainder=remainder)
    except BaseException:
        for value in (width, depth, stock, rows, borrowed, body, remainder):
            value.close()
        raise
    finally:
        dimension.close()
        one.close()
        cursor.close()
