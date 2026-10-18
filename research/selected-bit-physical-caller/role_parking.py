"""Fixed canonical stream roles and finite control on the shared parking tape.

The caller supplies dense role bodies over the retained record alphabet and
finishes numerical restoration before restoring this enclosing stream frame.
The codec reads no payload length or physical head coordinate into control.
"""
import loader
loader.activate()
from records import Tape
from words import BLANK, LEFT, ONE, ZERO, need

BODY = (0, 1, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13)


class RoleParking:
    def __init__(self, numerical_codec, roles):
        self.port = numerical_codec
        self.roles = tuple(roles)
        need(len({id(tape) for tape in self.roles}) == len(self.roles),
             "distinct permanent stream roles")

    def park(self):
        port = self.port
        port._empty_port()
        port._command("begin")
        for tape in self.roles:
            tape.rewind()
            while True:
                symbol = tape.read()
                if symbol == BLANK:
                    break
                need(symbol in BODY, "dense fixed-alphabet role body")
                for shift in range(4):
                    port._put_bit((symbol >> shift) & 1)
                tape.write(BLANK)
                tape.step(1)
            tape.rewind()
            port._write(1, "$")
            port._rewind_port()
            port._command("push")
        port._empty_port()

    def restore(self):
        port = self.port
        port._empty_port()
        # The record count and order are fixed at compilation, including empty
        # roles. No unbounded handle or record-count decoder is necessary.
        for tape in reversed(self.roles):
            tape.rewind()
            need(tape.read() == BLANK, "child clears canonical roles before return")
            port._command("pop")
            while port._read(1) != "$":
                symbol = 0
                for shift in range(4):
                    symbol |= port._take_bit() << shift
                need(symbol in BODY, "restored fixed-alphabet role symbol")
                tape.append(symbol)
            port._write(1, "_")
            port._rewind_port()
            tape.rewind()
        port._command("end")
        port._empty_port()


class FiniteFields:
    """A fixed schema for source labels, slot labels and continuation states.

    Bounds belong to the compiled fixed-q source. Runtime dimensions, residue
    values, tape extents and recursion depth must use encoded data roles.
    """
    def __init__(self, bounds):
        self.bounds = tuple(bounds)
        need(all(type(bound) is int and bound > 0 for bound in self.bounds),
             "positive compile-time finite-field bounds")
        self.widths = tuple(max(1, (bound - 1).bit_length()) for bound in self.bounds)

    def write(self, tape, values):
        need(len(values) == len(self.bounds), "finite continuation arity")
        tape.rewind()
        need(tape.read() == BLANK, "empty finite-control destination")
        for value, bound, width in zip(values, self.bounds, self.widths):
            need(type(value) is int and 0 <= value < bound, "finite continuation label")
            for shift in range(width):
                tape.append((value >> shift) & 1)
        tape.rewind()

    def read(self, tape):
        tape.rewind()
        values = []
        for bound, width in zip(self.bounds, self.widths):
            value = 0
            for shift in range(width):
                bit = tape.read()
                need(bit in (ZERO, ONE), "complete finite-control bit field")
                value |= bit << shift
                tape.step(1)
            need(value < bound, "admitted finite continuation label")
            values.append(value)
        need(tape.read() == BLANK, "exact finite-control record extent")
        tape.rewind()
        return tuple(values)


def transfer(source, target):
    """Move a complete owned result to its permanent canonical destination."""
    need(source is not target, "distinct result and canonical destination")
    target.clear()
    source.rewind()
    while source.read() != BLANK:
        symbol = source.read()
        need(symbol in BODY, "dense transferred body")
        target.append(symbol)
        source.write(BLANK)
        source.step(1)
    source.rewind()
    target.rewind()
