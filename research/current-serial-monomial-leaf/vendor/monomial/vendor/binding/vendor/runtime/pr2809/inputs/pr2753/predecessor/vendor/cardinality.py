"""Canonical unbounded binary cardinalities on one sequential tape each."""
from records import Tape
from stream import Counter
from words import BLANK, LEFT, ONE, RIGHT, ZERO, need


class Natural:
    def __init__(self, source=None):
        self.tape = Tape()
        if source is None:
            self.tape.append(ONE)
        else:
            source.rewind()
            while source.read() != RIGHT:
                bit = source.read()
                need(bit in (ZERO, ONE), "binary cardinality input")
                self.tape.append(bit)
                source.step(1)
            source.rewind()
        self.tape.append(RIGHT)
        self.normalize()

    def read(self):
        return self.tape.read()

    def step(self, direction):
        self.tape.step(direction)

    def rewind(self):
        self.tape.rewind()

    def msb(self):
        self.rewind()
        while self.read() != RIGHT:
            self.step(1)
        self.step(-1)

    def normalize(self):
        self.rewind()
        while self.read() != RIGHT:
            self.step(1)
        self.step(-1)
        while self.read() == ZERO:
            self.tape.write(RIGHT)
            self.step(1)
            self.tape.write(BLANK)
            self.step(-1)
            self.step(-1)
        if self.read() == LEFT:
            self.step(1)
            self.tape.write(ZERO)
            self.step(1)
            self.tape.write(RIGHT)
        self.rewind()

    def multiply_small(self, constant):
        """The multiplier and bounded carry belong to fixed finite control."""
        need(constant >= 2, "fixed cardinality multiplier")
        carry = 0
        while self.read() != RIGHT:
            total = constant*self.read()+carry
            self.tape.write(total & 1)
            carry = total >> 1
            self.step(1)
        while carry:
            self.tape.write(carry & 1)
            carry >>= 1
            self.step(1)
        self.tape.write(RIGHT)
        self.rewind()

    def divide_small(self, constant):
        self.msb()
        remainder = 0
        while self.read() != LEFT:
            remainder = 2*remainder+self.read()
            if remainder >= constant:
                self.tape.write(ONE)
                remainder -= constant
            else:
                self.tape.write(ZERO)
            self.step(-1)
        self.step(1)
        self.normalize()
        return remainder

    def marginal(self):
        """Copy with one high zero bit for the retained ADD input contract."""
        result = Natural(self)
        result.msb()
        result.step(1)
        result.tape.write(ZERO)
        result.step(1)
        result.tape.write(RIGHT)
        result.rewind()
        return result

    def close(self):
        self.tape.clear()


def radix_power(ring, q):
    """Yield once per radix-q digit of M=q^w, without decoding w."""
    arena = ring.arena
    divisor, power = arena.literal(q), arena.copy(ring.modulus)
    try:
        while ring.raw.compare(power, ring.one) > 0:
            quotient, remainder = ring.raw.divmod(power, divisor)
            need(remainder.zero() and not quotient.zero(), "cardinality prime-power context")
            arena.free_many(power, remainder)
            power = quotient
            yield
        need(ring.raw.compare(power, ring.one) == 0, "complete radix exponent")
    finally:
        arena.free_many(divisor, power)


def multiply_atom_power(value, exponent, ring, q):
    count = Counter(exponent)
    try:
        while not count.finished:
            for _ in radix_power(ring, q):
                value.multiply_small(q)
            count.decrement()
    finally:
        count.close()


def digit_suffix(value, ring, q):
    """Multiply by q^(w-1), preserving an arbitrary spectator factor."""
    first = True
    for _ in radix_power(ring, q):
        if first:
            first = False
        else:
            value.multiply_small(q)
