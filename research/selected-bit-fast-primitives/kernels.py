"""Literal linear high-field passes; low carries belong to compilation."""
import stage_sources
stage_sources.activate()
from bitstream import copy_bits, translate_one
from cardinal_counts import Count, positive
from linear_sign import sign_address
from routes import copy_rows
from stream import Counter, add_pass
from words import BLANK, need


def doubled(source, ring, before, suffix, factory, inverse=False):
    """x -> 2x or x -> x/2 modulo odd Q, by two monotone streams."""
    positive(before)
    positive(suffix)
    half = Count(ring.modulus)
    need(half.divide_small(2) == 1, "odd high modulus")
    even = Count(half)
    even.increment()
    left, right, output = factory(), factory(), factory()
    try:
        for merging in (False, True):
            outer = Counter(before)
            try:
                while not outer.finished:
                    alternating = merging != inverse
                    if alternating:
                        pairs = Counter(half)
                        try:
                            while not pairs.finished:
                                copy_bits(left if merging else source, output if merging else left, suffix)
                                copy_bits(right if merging else source, output if merging else right, suffix)
                                pairs.decrement()
                            copy_bits(left if merging else source, output if merging else left, suffix)
                        finally:
                            pairs.close()
                    elif merging:
                        copy_rows(left, output, even, suffix)
                        copy_rows(right, output, half, suffix)
                    else:
                        copy_rows(source, left, even, suffix)
                        copy_rows(source, right, half, suffix)
                    outer.decrement()
            finally:
                outer.close()
            if not merging:
                need(source.read() == BLANK, "complete high scaling input")
                source.rewind()
                left.rewind()
                right.rewind()
        need(left.read() == right.read() == BLANK, "complete high scaling streams")
        output.rewind()
        return output
    except BaseException:
        output.clear()
        raise
    finally:
        source.rewind()
        left.clear()
        right.clear()
        half.close()
        even.close()


def negated(source, ring, q, before, suffix):
    pre, tail = before.marginal(), suffix.marginal()
    try:
        return sign_address(source, ring, q, pre, tail)
    finally:
        pre.close()
        tail.close()


def translated(source, ring, q, before, suffix, amount):
    """A compiled bounded carry, using retained +1 and sign passes."""
    need(type(amount) is int and 0 < abs(amount) <= 4, "fixed selected carry")
    pre, tail = before.marginal(), suffix.marginal()
    current = source
    try:
        for _ in range(abs(amount)):
            if amount < 0:
                following = sign_address(current, ring, q, pre, tail)
                if current is not source:
                    current.clear()
                current = following
            following = translate_one(current, ring, pre, tail)
            if current is not source:
                current.clear()
            current = following
            if amount < 0:
                following = sign_address(current, ring, q, pre, tail)
                current.clear()
                current = following
        result, current = current, None
        return result
    finally:
        pre.close()
        tail.close()
        if current is not None and current is not source:
            current.clear()


def fixed_coefficient(ring, coefficient):
    need(type(coefficient) is int and coefficient in (-4, -2, -1, 1, 2, 4), "fixed dyadic numerator")
    literal = ring.arena.literal(abs(coefficient))
    quotient, value = ring.raw.divmod(literal, ring.modulus)
    ring.arena.free_many(literal, quotient)
    if coefficient < 0:
        following = ring.negate(value)
        ring.arena.free(value)
        value = following
    return value


def added(source, ring, before, middle, suffix, coefficient):
    operands = [value.marginal() for value in (before, middle, suffix)]
    try:
        output, _meter = add_pass(source, ring, *operands, lambda: fixed_coefficient(ring, coefficient))
        return output
    finally:
        for value in operands:
            value.close()
