"""Binary-counted complete-fibre ADD using an encoded coefficient callback.

Each arbitrary spectator extent has its own canonical word length. None
enters the coefficient context. Payload bits remain opaque to the arithmetic.
"""
from records import Tape
from words import BLANK, LEFT, ONE, RIGHT, ZERO, need


class Counter:
    """Canonical variable-length countdown with amortized ripple movement."""
    def __init__(self, word):
        self.tape = Tape()
        word.rewind()
        while word.read() != RIGHT:
            self.tape.append(word.read())
            word.step(1)
        word.rewind()
        self.tape.append(RIGHT)
        self.tape.step(-1)
        self.tape.step(-1)
        while self.tape.read() == ZERO:
            self.tape.write(RIGHT)
            self.tape.step(1)
            self.tape.write(BLANK)
            self.tape.step(-1)
            self.tape.step(-1)
        self.finished = self.tape.read() == LEFT
        if self.finished:
            self.tape.step(1)
            self.tape.write(ZERO)
            self.tape.step(1)
            self.tape.write(RIGHT)
        self.tape.rewind()

    def decrement(self):
        need(not self.finished, "positive countdown")
        tape = self.tape
        while tape.read() == ZERO:
            tape.write(ONE)
            tape.step(1)
        need(tape.read() == ONE, "canonical positive counter")
        tape.write(ZERO)
        tape.step(1)
        if tape.read() == RIGHT:
            tape.write(BLANK)
            tape.step(-1)
            tape.step(-1)
            if tape.read() == LEFT:
                tape.step(1)
                tape.write(ZERO)
                tape.step(1)
                tape.write(RIGHT)
                self.finished = True
            else:
                tape.step(1)
                tape.write(RIGHT)
        tape.rewind()

    def close(self):
        self.tape.clear()


def positive_extent(word):
    """Reject padding inherited from a different, larger spectator extent."""
    word.msb()
    margin = word.read()
    word.step(-1)
    significant = word.read()
    word.rewind()
    need(margin == ZERO and significant == ONE, "separately canonical positive spectator extent")


def one_bit_suffix(word):
    """Recognize the fixed encodings of one, without decoding a cardinality."""
    word.rewind()
    if word.read() != ONE:
        return False
    word.step(1)
    if word.read() == ZERO:
        word.step(1)
    result = word.read() == RIGHT
    word.rewind()
    return result


def copy_blocks(source, target, count, suffix, observe):
    blocks = Counter(count)
    single = one_bit_suffix(suffix)
    while not blocks.finished:
        if single:
            bit = source.read()
            need(bit in (ZERO, ONE), "opaque payload bit")
            target.append(bit)
            source.step(1)
        else:
            bits = Counter(suffix)
            while not bits.finished:
                bit = source.read()
                need(bit in (ZERO, ONE), "opaque payload bit")
                target.append(bit)
                source.step(1)
                bits.decrement()
            bits.close()
            observe(bits)
        blocks.decrement()
    blocks.close()
    observe(blocks)


def add_pass(source, ring, before, middle, suffix, prepare_coefficient, payload_factory=Tape):
    for extent in (before, middle, suffix):
        positive_extent(extent)
    left, right, out = payload_factory(), payload_factory(), payload_factory()
    totals = {"reads": 0, "writes": 0, "moves": 0}
    def observe(counter):
        # External meter only; no count controls execution.
        for key in totals:
            totals[key] += getattr(counter.tape.meter, key)
    def traverse(merge):
        coefficient = prepare_coefficient()
        need(ring.raw.compare(coefficient, ring.modulus) < 0, "canonical encoded coefficient")
        outer = Counter(before)
        while not outer.finished:
            x = ring.arena.zero()
            sources = Counter(ring.modulus)
            while not sources.finished:
                offset = ring.multiply(coefficient, x)
                leading = ring.raw.subtract_exact(ring.modulus, offset)
                mid = Counter(middle)
                while not mid.finished:
                    if merge:
                        copy_blocks(right, out, offset, suffix, observe)
                        copy_blocks(left, out, leading, suffix, observe)
                    else:
                        copy_blocks(source, left, leading, suffix, observe)
                        copy_blocks(source, right, offset, suffix, observe)
                    mid.decrement()
                mid.close()
                observe(mid)
                ring.arena.free_many(offset, leading)
                sources.decrement()
                if not sources.finished:
                    ring.raw.increment_in_place(x)
            sources.close()
            observe(sources)
            ring.arena.free(x)
            outer.decrement()
        outer.close()
        observe(outer)
        ring.arena.free(coefficient)
    traverse(False)
    need(source.read() == BLANK, "complete input extent")
    source.rewind()
    left.rewind()
    right.rewind()
    traverse(True)
    need(left.read() == right.read() == BLANK, "complete split consumption")
    left.clear()
    right.clear()
    out.rewind()
    return out, {"counters": totals, "left": left.meter.record(), "right": right.meter.record(),
                 "output": out.meter.record()}
