"""Checker-only native observations and source-bit provenance."""
from contextlib import contextmanager
from records import Tape
from words import BLANK, LEFT, ONE, RIGHT, ZERO, Word, need


@contextmanager
def no_decode():
    previous = Word.inspect
    def reject(_word):
        raise ValueError("runtime numerical decoding")
    Word.inspect = reject
    try:
        yield
    finally:
        Word.inspect = previous


def inspect_count(value):
    value.rewind()
    result, bit = 0, 0
    while value.read() != RIGHT:
        result |= value.read() << bit
        bit += 1
        value.step(1)
    value.rewind()
    return result


def bits(tape):
    end = len(tape.cells)
    while end > 1 and tape.cells[end-1] == BLANK:
        end -= 1
    return bytes(tape.cells[1:end])


def audit(arena, live=()):
    need(arena.live == {word.slot for word in live}, "exact numerical ownership")
    need(arena.template.head == 1, "restored numerical template")
    for word in arena.words:
        need(word.head == 1, "restored numerical head")
        if word.slot not in arena.live:
            need(word.cells[0] == LEFT and all(x == BLANK for x in word.cells[1:]), "erased numeric work")


def payload(length, seed=0):
    tape = Tape()
    for i in range(length):
        tape.append(((i*7+seed*11) ^ (i >> 3) ^ (i >> 7)) & 1)
    tape.rewind()
    return tape


class Origins:
    def __init__(self):
        self.last, self.live, self.erased = None, set(), 0
        audit_state = self
        class Control(Tape):
            def __init__(self):
                super().__init__()
                audit_state.live.add(self)

            def clear(self):
                super().clear()
                need(self.head == 1 and not bits(self), "erased encoded control work")
                if self in audit_state.live:
                    audit_state.live.remove(self)
                    audit_state.erased += 1
        class Tagged(Tape):
            def __init__(self):
                super().__init__()
                self.origins = {}
                audit_state.live.add(self)

            def read(self):
                value = super().read()
                if self.head in self.origins:
                    audit_state.last = self.origins[self.head]
                return value

            def write(self, value):
                super().write(value)
                if value == BLANK:
                    self.origins.pop(self.head, None)
                elif value in (ZERO, ONE) and audit_state.last is not None:
                    self.origins[self.head] = audit_state.last

            def clear(self):
                super().clear()
                need(self.head == 1 and not self.origins and not bits(self), "erased route scratch")
                if self in audit_state.live:
                    audit_state.live.remove(self)
                    audit_state.erased += 1
        self.factory = Tagged
        self.control_factory = Control

    def source(self, length):
        tape = self.factory()
        for i in range(length):
            tape.append(((i*13) ^ (i >> 2)) & 1)
        tape.origins = {i+1:i for i in range(length)}
        tape.rewind()
        return tape


def reject(function, message):
    try:
        function()
    except ValueError:
        return message
    raise ValueError("missing rejection: "+message)
