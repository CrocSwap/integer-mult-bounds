"""Sequential continuation primitive; no frame objects or numeric return offsets.

The controller uses only Tape.read/write/move. Tape's sparse dictionary, absolute
head, counters and visited set implement the test machine, not controller state.
Prepared for mihir-s-05 with substantial OpenAI Codex assistance. Apache-2.0.
"""

from dataclasses import dataclass

BLANK = '_'
LEFT = '|'
BITS = ('0', '1')
ALPHABET = frozenset((BLANK, LEFT, '0', '1', '[', ':', 'u', ';', ']'))
ROLES = 16


def need(value, message):
    if not value:
        raise ValueError(message)


@dataclass
class Meter:
    reads: int = 0
    writes: int = 0
    moves: int = 0

    @property
    def total(self):
        return self.reads + self.writes + self.moves


class Tape:
    """Unit-action simulator. Constructor and snapshots are fixture operations."""

    def __init__(self, meter, prefix='', data='', offset=0):
        need(all(c in ALPHABET - {BLANK} for c in prefix), 'fixture prefix')
        need(all(c in BITS for c in data), 'fixture binary data')
        need(0 <= offset <= len(data), 'fixture head')
        self._cells = dict(enumerate(prefix + LEFT + data))
        self._head = len(prefix) + 1 + offset
        self._meter = meter
        self._visited = {self._head}

    def read(self):
        self._meter.reads += 1
        self._visited.add(self._head)
        return self._cells.get(self._head, BLANK)

    def write(self, symbol):
        need(symbol in ALPHABET, 'fixed alphabet')
        self._meter.writes += 1
        self._visited.add(self._head)
        if symbol == BLANK:
            self._cells.pop(self._head, None)
        else:
            self._cells[self._head] = symbol

    def move(self, direction):
        need(direction in (-1, 1), 'unit move')
        need(self._head + direction >= 0, 'left tape boundary')
        self._head += direction
        self._meter.moves += 1
        self._visited.add(self._head)

    def snapshot(self):
        return self._head, tuple(sorted(self._cells.items()))


def emit(tape, symbol):
    need(tape.read() == BLANK, 'append requires blank')
    tape.write(symbol)
    tape.move(1)


def take(stack):
    stack.move(-1)
    symbol = stack.read()
    stack.write(BLANK)
    return symbol


def rewind(tape, erased=False):
    """Return to the nearest local delimiter, paying every backward move."""
    while True:
        tape.move(-1)
        symbol = tape.read()
        if symbol == LEFT:
            tape.move(1)
            return
        need(symbol == BLANK if erased else symbol in BITS,
             'local rewind alphabet')


def clear(tape):
    """Erase a contiguous local binary segment from any head in its extent."""
    rewind(tape)
    while True:
        symbol = tape.read()
        if symbol == BLANK:
            break
        need(symbol in BITS, 'local clear alphabet')
        tape.write(BLANK)
        tape.move(1)
    rewind(tape, erased=True)


class Controller:
    """Nineteen fixed tapes and a 16-bit live-role mask, at every nesting depth.

    No method accesses the simulator's private cells, head, meter or snapshots.
    Role indices, symbols and the mask range over fixed finite sets. The caller
    supplies well-formed local segments and properly nested successful calls.
    """

    def __init__(self, payload, control, descriptor, reverse, occupied):
        need(len(payload) == ROLES, 'sixteen payload roles')
        need(0 <= occupied < 1 << ROLES, 'finite occupancy mask')
        self.payload = tuple(payload)
        self.control = control
        self.descriptor = descriptor
        self.reverse = reverse
        self.occupied = occupied

    def push(self):
        # Entry: control at its blank top, descriptor at its local beginning,
        # reverse scratch empty. Descriptor is consumed into the new frame.
        emit(self.control, '[')
        while True:
            symbol = self.descriptor.read()
            if symbol == BLANK:
                break
            need(symbol in BITS, 'binary descriptor')
            emit(self.control, symbol)
            self.descriptor.write(BLANK)
            self.descriptor.move(1)
        rewind(self.descriptor, erased=True)
        emit(self.control, ':')
        for role in range(ROLES):
            present = (self.occupied >> role) & 1
            emit(self.control, '1' if present else '0')
            tape = self.payload[role]
            while True:
                symbol = tape.read()
                if symbol == BLANK:
                    break
                need(symbol in BITS, 'binary parent payload')
                need(present, 'absent role must be empty')
                tape.move(1)
                emit(self.control, 'u')
            tape.write(LEFT)
            tape.move(1)
            emit(self.control, ';')
        emit(self.control, ']')
        self.occupied = 0

    def pop(self):
        # Retire current child work first. Any designated child result must
        # have been delivered by the caller before this destructive cleanup.
        for tape in self.payload:
            clear(tape)
        clear(self.descriptor)
        need(self.reverse.read() == BLANK, 'reverse scratch empty')
        need(take(self.control) == ']', 'frame top delimiter')
        self.occupied = 0
        for role in reversed(range(ROLES)):
            need(take(self.control) == ';', 'role terminator')
            tape = self.payload[role]
            tape.move(-1)
            need(tape.read() == LEFT, 'payload suspension delimiter')
            tape.write(BLANK)
            symbol = take(self.control)
            while symbol == 'u':
                tape.move(-1)
                need(tape.read() in BITS, 'return distance within parent')
                symbol = take(self.control)
            need(symbol in BITS, 'role presence flag')
            if symbol == '1':
                self.occupied |= 1 << role
        need(take(self.control) == ':', 'descriptor terminator')
        symbol = take(self.control)
        while symbol in BITS:
            emit(self.reverse, symbol)
            symbol = take(self.control)
        need(symbol == '[', 'frame beginning delimiter')
        # Reverse once more by physical movement, reconstructing forward order.
        while True:
            self.reverse.move(-1)
            symbol = self.reverse.read()
            if symbol == LEFT:
                break
            need(symbol in BITS, 'reverse scratch alphabet')
            self.reverse.write(BLANK)
            emit(self.descriptor, symbol)
        self.reverse.move(1)
        rewind(self.descriptor)


def action_bound(descriptor_bits, return_distance, child_bits):
    """Conservative read/write/unit-move bound for one matched push/pop."""
    need(min(descriptor_bits, return_distance, child_bits) >= 0, 'bound domain')
    return 24 * descriptor_bits + 12 * return_distance + 32 * ROLES + 64 + 8 * child_bits
