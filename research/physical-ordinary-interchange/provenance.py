"""Checker-only affine provenance beside unchanged Boolean tape cells."""
from contextlib import contextmanager

import source
source.activate()
from records import Tape
from words import ONE, ZERO, need


class Provenance:
    def __init__(self, inputs):
        self.constant = 1 << inputs
        self.cells = {}
        owner = self
        class Bit(int):
            def __new__(cls, value, mask):
                result = int.__new__(cls, value)
                result.mask = mask
                return result

            def __xor__(self, other):
                need(other in (ZERO, ONE), "Boolean payload XOR")
                mask = other.mask if isinstance(other, Bit) else owner.constant * int(other)
                return Bit(int(self) ^ int(other), self.mask ^ mask)

            __rxor__ = __xor__
        self.Bit = Bit

    def mark(self, tape):
        tape.rewind()
        position = 1
        while tape.read() in (ZERO, ONE):
            self.cells[(id(tape), position)] = 1 << (position-1)
            tape.step(1)
            position += 1
        tape.rewind()

    def masks(self, tape, length):
        return tuple(self.cells.get((id(tape), position),
                                    self.constant * int(tape.cells[position]))
                     for position in range(1, length+1))

    @contextmanager
    def installed(self):
        read, write = Tape.read, Tape.write
        observer = self
        def observed_read(tape):
            value = read(tape)
            mask = observer.cells.get((id(tape), tape.head))
            return observer.Bit(value, mask) if mask is not None else value

        def observed_write(tape, value):
            write(tape, value)
            key = id(tape), tape.head
            if isinstance(value, observer.Bit):
                observer.cells[key] = value.mask
            else:
                observer.cells.pop(key, None)

        Tape.read, Tape.write = observed_read, observed_write
        try:
            yield self
        finally:
            Tape.read, Tape.write = read, write
