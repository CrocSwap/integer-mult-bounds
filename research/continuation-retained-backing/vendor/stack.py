"""Delimited continuation on a fixed number of sequential tapes.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The source interface follows JoyboyBrian and Jose Manuel's tape packages.
"""
from dataclasses import dataclass

ZERO, ONE, LEFT, SEP, END, BASE, BLANK = range(7)


def need(ok, message):
    if not ok:
        raise ValueError(message)


@dataclass
class Counts:
    reads: int = 0
    writes: int = 0
    moves: int = 0

    @property
    def total(self):
        return self.reads + self.writes + self.moves


class Tape:
    """Hardware model. Only read, write and unit move are algorithm operations."""
    def __init__(self, prefix=(), marker=LEFT, counts=None):
        self.cells = list(prefix) + [marker]
        self.head = len(self.cells)
        self.floor = self.head - 1
        self.minimum = self.head
        self.counts = counts if counts is not None else Counts()

    def read(self):
        self.counts.reads += 1
        self.minimum = min(self.minimum, self.head)
        need(self.head >= self.floor, 'ancestor prefix accessed')
        return self.cells[self.head] if self.head < len(self.cells) else BLANK

    def write(self, value):
        need(value in range(7), 'finite tape alphabet')
        need(self.head >= self.floor, 'ancestor prefix overwritten')
        self.counts.writes += 1
        while len(self.cells) <= self.head:
            self.cells.append(BLANK)
        self.cells[self.head] = value

    def move(self, direction):
        need(direction in (-1, 1), 'unit move')
        self.counts.moves += 1
        self.head += direction
        need(self.head >= self.floor, 'ancestor prefix crossed')


def emit(tape, symbol):
    tape.write(symbol)
    tape.move(1)


def rewind(tape, marker):
    tape.move(-1)
    while tape.read() != marker:
        tape.move(-1)
    tape.move(1)


def clear_descriptor(tape):
    """Entry and exit are at the descriptor origin."""
    while (symbol := tape.read()) != BLANK:
        need(symbol in (ZERO, ONE), 'binary descriptor')
        emit(tape, BLANK)
    rewind(tape, BASE)


class Stack:
    """No saved frame, parent pointer, frame size or origin is stored here."""
    def __init__(self, payloads, control, descriptor):
        self.payloads = tuple(payloads)
        self.control = control
        self.descriptor = descriptor

    def push(self, present):
        need(len(present) == len(self.payloads), 'fixed role bitmap')
        c = self.control
        need(c.read() == BLANK, 'control at free top')
        emit(c, LEFT)
        for tape, occupied in zip(self.payloads, present):
            need(type(occupied) is bool, 'role presence bit')
            emit(c, int(occupied))
            tape.move(-1)
            while (symbol := tape.read()) != LEFT:
                need(symbol in (ZERO, ONE), 'binary prefix before current head')
                emit(c, ONE)
                tape.move(-1)
            emit(c, ZERO)
            tape.move(1)
            if not occupied:
                need(tape.read() == BLANK, 'absent role is empty')
            while (symbol := tape.read()) != BLANK:
                need(symbol in (ZERO, ONE), 'binary parent payload')
                tape.move(1)
            emit(tape, LEFT)
        emit(c, SEP)
        d = self.descriptor
        while (symbol := d.read()) != BLANK:
            need(symbol in (ZERO, ONE), 'binary descriptor')
            emit(c, symbol)
            emit(d, BLANK)
        rewind(d, BASE)
        emit(c, END)

    def pop(self):
        """Child payloads are empty at their origins; clear its descriptor.

        Returned sizes/heads are observer counts for the source API adapter.
        No branch or tape move uses those counts.
        """
        clear_descriptor(self.descriptor)
        c = self.control
        c.move(-1)
        need(c.read() == END, 'complete control frame')
        c.move(-1)
        while (symbol := c.read()) != LEFT:
            need(symbol in (ZERO, ONE, SEP), 'frame start before ancestor boundary')
            c.move(-1)
        emit(c, BLANK)
        state = []
        for tape in self.payloads:
            present = c.read()
            need(present in (ZERO, ONE), 'role presence bit')
            emit(c, BLANK)
            need(tape.read() == BLANK, 'child payload is retired')
            tape.move(-1)
            need(tape.read() == LEFT, 'child delimiter')
            tape.write(BLANK)
            tape.move(-1)
            size = 0
            while (symbol := tape.read()) != LEFT:
                need(symbol in (ZERO, ONE), 'parked parent payload')
                size += 1
                tape.move(-1)
            tape.move(1)
            if not present:
                need(tape.read() == BLANK, 'absent parent role is empty')
            head = 0
            while (symbol := c.read()) == ONE:
                need(tape.read() in (ZERO, ONE), 'saved head is within payload')
                tape.move(1)
                head += 1
                emit(c, BLANK)
            need(symbol == ZERO, 'terminated unary head')
            emit(c, BLANK)
            state.append((bool(present), size, head))
        need(c.read() == SEP, 'complete fixed-role header')
        emit(c, BLANK)
        d = self.descriptor
        while (symbol := c.read()) != END:
            need(symbol in (ZERO, ONE), 'binary saved descriptor')
            emit(d, symbol)
            emit(c, BLANK)
        c.write(BLANK)
        c.move(-1)
        while c.read() == BLANK:
            c.move(-1)
        need(c.read() in (BASE, END), 'previous control top')
        c.move(1)
        rewind(d, BASE)
        return state
