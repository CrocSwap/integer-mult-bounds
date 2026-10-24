"""Bind retained sequential source calls to the delimited stack.

The source's fixed lexical role schedule remains an inherited premise.
Weak references simulate allocation; push/pop never consult that registry.
Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from contextlib import contextmanager
import weakref
from stack import BASE, BLANK, LEFT, Counts, Stack, Tape, clear_descriptor, emit, need, rewind


class View:
    def __init__(self, role):
        self.role = role

    def __len__(self):
        return self.role.arena.sizes[self.role.slot]

    def __bytes__(self):
        # Test oracle only. The retained algorithms use len(data), never this.
        role = self.role
        tape = role.arena.payloads[role.slot]
        start = tape.head - role.head
        return bytes(tape.cells[start:start + len(self)])


class Arena:
    slots = 16

    def __init__(self, ancestors, control_prefix=()):
        need(len(ancestors) == self.slots, 'sixteen payload roles')
        self.counts = Counts()
        self.payloads = [Tape(x, counts=self.counts) for x in ancestors]
        self.control = Tape(control_prefix, BASE, self.counts)
        self.descriptor = Tape((), BASE, self.counts)
        self.stack = Stack(self.payloads, self.control, self.descriptor)
        self.present = [False] * self.slots
        self.sizes = [0] * self.slots
        self.heads = [0] * self.slots
        self.owners = weakref.WeakValueDictionary()
        self.depth = 0
        self.peak = 0
        self.boundary_steps = 0

    def tape(self, meter, data=b''):
        for i in range(self.slots):
            if self.present[i] and (self.depth, i) not in self.owners:
                need(self.sizes[i] == 0, 'retired source role is empty')
                self.present[i] = False
        slot = next((i for i, occupied in enumerate(self.present) if not occupied), None)
        need(slot is not None, 'fixed role inventory')
        need(self.sizes[slot] == 0, 'free role is empty')
        self.present[slot] = True
        self.peak = max(self.peak, sum(self.present))
        role = Role(self, slot, self.depth, meter)
        self.owners[self.depth, slot] = role
        role.write(data)
        role.rewind()
        return role

    def set_descriptor(self, bits):
        clear_descriptor(self.descriptor)
        for bit in bits:
            need(bit in (0, 1), 'binary descriptor input')
            emit(self.descriptor, bit)
        rewind(self.descriptor, BASE)

    def erase_slot(self, slot):
        tape = self.payloads[slot]
        rewind(tape, LEFT)
        while (symbol := tape.read()) != BLANK:
            need(symbol in (0, 1), 'binary current payload')
            emit(tape, BLANK)
        rewind(tape, LEFT)
        self.sizes[slot] = self.heads[slot] = 0

    @contextmanager
    def child(self):
        before = self.counts.total
        self.stack.push(self.present)
        self.boundary_steps += self.counts.total - before
        self.present = [False] * self.slots
        self.sizes = [0] * self.slots
        self.heads = [0] * self.slots
        self.depth += 1
        try:
            yield
        finally:
            # Child retirement is charged separately from stack operations.
            for slot in range(self.slots):
                self.erase_slot(slot)
            before = self.counts.total
            state = self.stack.pop()
            self.boundary_steps += self.counts.total - before
            self.present = [x[0] for x in state]
            self.sizes = [x[1] for x in state]
            self.heads = [x[2] for x in state]
            self.depth -= 1


class Role:
    def __init__(self, arena, slot, depth, meter):
        self.arena, self.slot, self.depth, self.meter = arena, slot, depth, meter

    @property
    def data(self):
        return View(self)

    @property
    def head(self):
        return self.arena.heads[self.slot]

    def active(self):
        need(self.depth == self.arena.depth and self.arena.present[self.slot], 'active role')

    def read(self, size):
        self.active()
        a = self.arena
        need(0 <= size <= a.sizes[self.slot] - self.head, 'sequential read boundary')
        out = bytearray()
        tape = a.payloads[self.slot]
        for _ in range(size):
            bit = tape.read()
            need(bit in (0, 1), 'binary current payload')
            out.append(bit)
            tape.move(1)
        a.heads[self.slot] += size
        return out

    def write(self, value):
        self.active()
        a = self.arena
        need(self.head == a.sizes[self.slot], 'append-only role')
        tape = a.payloads[self.slot]
        for bit in value:
            need(bit in (0, 1), 'binary current payload')
            need(tape.read() == BLANK, 'append at free cell')
            emit(tape, bit)
            a.sizes[self.slot] += 1
            a.heads[self.slot] += 1

    def rewind(self):
        self.active()
        rewind(self.arena.payloads[self.slot], LEFT)
        self.arena.heads[self.slot] = 0

    def finish(self):
        self.active()
        need(self.head == self.arena.sizes[self.slot], 'complete sequential consumption')

    def erase(self):
        self.active()
        self.arena.erase_slot(self.slot)
