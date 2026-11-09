"""Unbounded cardinalities; only compiled finite constants enter host control."""
from cardinality import Natural, digit_suffix
from records import Tape
from words import ONE, RIGHT, ZERO, need


class Count(Natural):
    @classmethod
    def literal(cls, value):
        """Compile a fixed cardinality, never decode a runtime operand."""
        need(isinstance(value, int) and value >= 0, "compiled cardinality")
        tape = Tape()
        for bit in range(max(1, value.bit_length())):
            tape.append((value >> bit) & 1)
        tape.append(RIGHT)
        tape.rewind()
        result = cls(tape)
        tape.clear()
        return result

    def increment(self):
        self.rewind()
        while self.read() == ONE:
            self.tape.write(ZERO)
            self.step(1)
        if self.read() == RIGHT:
            self.tape.write(ONE)
            self.step(1)
            self.tape.write(RIGHT)
        else:
            need(self.read() == ZERO, "canonical count digit")
            self.tape.write(ONE)
        self.rewind()

    def equals(self, other):
        self.rewind()
        other.rewind()
        same = True
        while self.read() != RIGHT and other.read() != RIGHT:
            same = same and self.read() == other.read()
            self.step(1)
            other.step(1)
        same = same and self.read() == other.read() == RIGHT
        self.rewind()
        other.rewind()
        return same


def high_power(value, ring, q, dimension):
    for _ in range(dimension*dimension):
        digit_suffix(value, ring, q)


def high_count(ring, q, dimension):
    result = Count.literal(1)
    high_power(result, ring, q, dimension)
    return result
