"""Literal finite-alphabet scans. Variable lengths are short Count tapes.
No coordinate, dimension, stream cardinality or tape address is decoded.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from cardinal_counts import Count
from compact_counts import copy_bits
from encoded import compare, subtract
from router_metadata import indices, owned
from session import borrowed_tape
from words import BLANK, LEFT, RIGHT, need
PART_END, BLOCK_START, BLOCK_END = 5, 6, 7


def bit(source, *destinations, erase=False):
    value = source.read()
    need(value in (0, 1), 'complete binary transport field')
    if erase:
        source.write(BLANK)
    source.step(1)
    for target in destinations:
        target.append(value)
    return value


def symbol(source, expected):
    need(source.read() == expected, 'transport delimiter')
    source.step(1)


def move(tape, length, direction=1):
    for _ in indices(length):
        tape.step(direction)


def skip_bits(source, length):
    for _ in indices(length):
        bit(source)


def copy_until(source, target, end=BLANK, erase=False):
    while source.read() != end:
        bit(source, target, erase=erase)


def zeros(target, length, overwrite=False):
    for _ in indices(length):
        if overwrite:
            target.write(0)
            target.step(1)
        else:
            target.append(0)


def big(source, width, *destinations):
    value = Count.literal(0)
    try:
        for _ in indices(width):
            digit = bit(source, *destinations)
            value.multiply_small(2)
            if digit:
                value.increment()
        return value
    except BaseException:
        value.close()
        raise


def put_big(value, target, width, overwrite=False):
    with owned(Count(value), Count.literal(0)) as (scratch, digits):
        scratch.msb()
        while scratch.read() != LEFT:
            need(scratch.read() in (0, 1), 'canonical count digits')
            digits.increment()
            scratch.step(-1)
        scratch.step(1)
        need(compare(digits, width) <= 0, 'transport integer fits field')
        scratch.msb()
        with owned(subtract(width, digits)) as (padding,):
            zeros(target, padding, overwrite)
        while scratch.read() != LEFT:
            digit = scratch.read()
            if overwrite:
                target.write(digit)
                target.step(1)
            else:
                target.append(digit)
            scratch.step(-1)
        scratch.step(1)


def read_count(source):
    value = Count.literal(0)
    raw = borrowed_tape(value.tape)
    raw.clear()
    seen = False
    more_than_one = False
    last = 0
    try:
        while source.read() != RIGHT:
            more_than_one = seen
            last = bit(source, raw)
            seen = True
        need(seen and (not more_than_one or last == 1), 'canonical catalogue count')
        raw.append(RIGHT)
        source.step(1)
        value.rewind()
        return value
    except BaseException:
        value.close()
        raise


def put_count(value, target):
    value.rewind()
    try:
        while value.read() != RIGHT:
            digit = value.read()
            need(digit in (0, 1), 'canonical serialized count')
            target.append(digit)
            value.step(1)
        target.append(RIGHT)
    finally:
        value.rewind()


def rewind_block(tape):
    need(tape.read() == BLOCK_END, 'local block end before rewind')
    tape.step(-1)
    while tape.read() != BLOCK_START:
        need(tape.read() in (0, 1), 'binary local block body')
        tape.step(-1)
    tape.step(1)


def top_block(tape):
    need(tape.read() == BLANK, 'stack append origin')
    tape.step(-1)
    need(tape.read() == BLOCK_END, 'nonempty completed stack block')
    rewind_block(tape)


def stack_empty(tape):
    need(tape.read() == BLANK, 'stack top is blank')
    tape.step(-1)
    answer = tape.read() == LEFT
    tape.step(1)
    return answer


def copy_record(source, target, width, erase=False):
    if erase:
        for _ in indices(width):
            bit(source, target, erase=True)
    else:
        copy_bits(source, target, width)


def same_context(source, catalogue, target=None):
    while source.read() in (0, 1):
        digit = bit(source)
        need(bit(catalogue) == digit, 'same complete microbox/source context')
        if target is not None:
            target.append(digit)
    need(source.read() == catalogue.read() == PART_END,
         'same complete context-key extent')
    source.step(1)
    catalogue.step(1)
    if target is not None:
        target.append(PART_END)


def skip_context(tape):
    while tape.read() in (0, 1):
        bit(tape)
    symbol(tape, PART_END)


def pop_block(tape):
    need(tape.read() == BLOCK_END, 'complete block before pop')
    tape.write(BLANK); tape.step(-1)
    while tape.read() != BLOCK_START:
        need(tape.read() in (0, 1), 'binary popped block body')
        tape.write(BLANK); tape.step(-1)
    tape.write(BLANK)
