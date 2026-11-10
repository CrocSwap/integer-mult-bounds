"""Compact numerical fields on canonical Count tapes, without decoded indices."""
import native_sources
native_sources.activate()
from cardinal_counts import Count
from encoded import compare, divide, subtract
from session import borrowed_tape
from stream import Counter
from words import BLANK, ONE, RIGHT, ZERO, need


def power_two(exponent):
    result, remaining = Count.literal(1), Counter(exponent)
    try:
        while not remaining.finished:
            result.multiply_small(2)
            remaining.decrement()
        return result
    except BaseException:
        result.close()
        raise
    finally:
        remaining.close()


def shifted(value, amount, left=True):
    result, remaining = Count(value), Counter(amount)
    try:
        while not remaining.finished:
            if left:
                result.multiply_small(2)
            else:
                result.divide_small(2)
            remaining.decrement()
        return result
    except BaseException:
        result.close()
        raise
    finally:
        remaining.close()


def bit_slice(value, start, width):
    """Read a variable bit window; fill positions above its end with zero."""
    offset, remaining = Counter(start), Counter(width)
    result = Count.literal(0)
    borrowed_tape(result.tape).clear()
    value.rewind()
    try:
        while not offset.finished:
            if value.read() != RIGHT:
                need(value.read() in (ZERO, ONE), "bit-window source digit")
                value.step(1)
            offset.decrement()
        while not remaining.finished:
            ended = value.read() == RIGHT
            bit = ZERO if ended else value.read()
            need(bit in (ZERO, ONE), "bit-window digit")
            result.tape.append(bit)
            if not ended:
                value.step(1)
            remaining.decrement()
        result.tape.append(RIGHT)
        result.normalize()
        return result
    except BaseException:
        result.close()
        raise
    finally:
        value.rewind()
        offset.close()
        remaining.close()


def bit_at(value, position):
    one = Count.literal(1)
    try:
        selected = bit_slice(value, position, one)
        try:
            bit = selected.read()
            need(bit in (ZERO, ONE), "one-bit finite control")
            return bit
        finally:
            selected.close()
    finally:
        one.close()


def bit_xor(left, right):
    if left is right or left.tape is right.tape:
        left.rewind()
        return Count.literal(0)
    result = Count.literal(0)
    borrowed_tape(result.tape).clear()
    left.rewind()
    right.rewind()
    try:
        while left.read() != RIGHT or right.read() != RIGHT:
            a_end, b_end = left.read() == RIGHT, right.read() == RIGHT
            a, b = ZERO if a_end else left.read(), ZERO if b_end else right.read()
            need(a in (ZERO, ONE) and b in (ZERO, ONE), "binary XOR digits")
            result.tape.append(a ^ b)
            if not a_end:
                left.step(1)
            if not b_end:
                right.step(1)
        result.tape.append(RIGHT)
        result.normalize()
        return result
    except BaseException:
        result.close()
        raise
    finally:
        left.rewind()
        right.rewind()


def reduced(value, modulus):
    quotient, remainder = divide(value, modulus)
    quotient.close()
    return remainder


def add_mod(left, right, modulus):
    total = Count(left)
    try:
        total.add(right)
        return reduced(total, modulus)
    finally:
        total.close()


def negate_mod(value, modulus):
    need(compare(value, modulus) < 0, "canonical modular operand")
    return Count.literal(0) if value.zero() else subtract(modulus, value)


def read_fixed(source, width):
    """Consume exactly width binary cells and return one canonical Count."""
    result, remaining = Count.literal(0), Counter(width)
    borrowed_tape(result.tape).clear()
    try:
        while not remaining.finished:
            bit = source.read()
            need(bit in (ZERO, ONE), "complete fixed-width binary key")
            result.tape.append(bit)
            source.step(1)
            remaining.decrement()
        result.tape.append(RIGHT)
        result.normalize()
        return result
    except BaseException:
        result.close()
        raise
    finally:
        remaining.close()


def write_fixed(value, target, width):
    remaining = Counter(width)
    value.rewind()
    try:
        while not remaining.finished:
            ended = value.read() == RIGHT
            bit = ZERO if ended else value.read()
            need(bit in (ZERO, ONE), "fixed-width key digit")
            target.append(bit)
            if not ended:
                value.step(1)
            remaining.decrement()
        need(value.read() == RIGHT or value.zero(), "key fits declared width")
    finally:
        value.rewind()
        remaining.close()


def copy_bits(source, target, count):
    remaining = Counter(count)
    try:
        while not remaining.finished:
            bit = source.read()
            need(bit in (ZERO, ONE), "complete opaque binary payload")
            target.append(bit)
            source.step(1)
            remaining.decrement()
    finally:
        remaining.close()


def append_bits(source, target):
    source.rewind()
    try:
        while source.read() != BLANK:
            bit = source.read()
            need(bit in (ZERO, ONE), "opaque binary stream alphabet")
            target.append(bit)
            source.step(1)
    finally:
        source.rewind()
