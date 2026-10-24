"""Local PR2250 payload views; continuation metadata uses a Python stack oracle."""
from contextlib import contextmanager
import weakref


def need(condition, message):
    if not condition:
        raise ValueError(message)


class DataView:
    def __init__(self, tape):
        self.tape = tape

    def __len__(self):
        return self.tape.size

    def __bytes__(self):
        t = self.tape
        return bytes(t.arena.backings[t.slot][t.origin:t.origin + t.size])


class Arena:
    """Sixteen physical payload tapes, with a stack delimiter on each tape.

    Initial ancestors and origins are caller-supplied entry state. child
    models subsequent payload origins by local movement. Frame metadata and
    boundaries come from a Python oracle, not an implemented physical control tape.
    """
    slots = 16

    def __init__(self, meter, ancestors):
        need(len(ancestors) == self.slots, 'sixteen physical tapes')
        self.meter = meter
        self.backings = [bytearray(x) + bytearray((2,)) for x in ancestors]
        self.origins = [len(x) + 1 for x in ancestors]
        self.live = [None] * self.slots
        self.depth = 0
        self.peak = 0
        self.payload_boundary_steps = 0
        self.descriptor_transport_model_steps = 0
        # shortcut: Python frame-boundary oracle, replace for a physical continuation.
        self.frames = []

    def tape(self, meter, data=b''):
        need(meter is self.meter, 'one physical meter')
        slot = next((i for i, t in enumerate(self.live) if t is None or t() is None), None)
        need(slot is not None, 'fixed tape inventory exhausted')
        need(len(self.backings[slot]) == self.origins[slot], 'retired role must be empty')
        t = Segment(self, slot, self.origins[slot], self.depth)
        self.live[slot] = weakref.ref(t)
        self.peak = max(self.peak, sum(x is not None and x() is not None for x in self.live))
        # Initial payload writes are charged, unlike the retained constructor.
        t.write(data)
        t.rewind()
        return t

    @contextmanager
    def child(self, descriptor):
        need(all(b in (0, 1) for b in descriptor), 'binary continuation descriptor')
        parents = [r() if r else None for r in self.live]
        header = bytearray()
        for t in parents:
            for value in (int(t is not None), t.size if t else 0, t.head if t else 0):
                bits = bin(value)[2:]
                header.extend([1] * len(bits) + [0])
                header.extend(int(bit) for bit in bits)
        descriptor = bytes(header) + bytes(descriptor)
        old = (self.origins[:], parents, descriptor)
        self.frames.append(old)
        for i, ref in enumerate(self.live):
            t = ref() if ref else None
            size, head = (t.size, t.head) if t else (0, 0)
            # Move to the local end, then write/cross a fresh delimiter.
            self.meter.moves += size - head + 1
            self.meter.writes += 1
            self.payload_boundary_steps += size - head + 2
            self.backings[i].append(2)
            self.origins[i] += size + 1
        self.depth += 1
        self.live = [None] * self.slots
        # Conditional byte-transport model: physical frame location/cleanup is unimplemented.
        self.meter.writes += len(descriptor)
        self.meter.moves += len(descriptor)
        self.descriptor_transport_model_steps += 2 * len(descriptor)
        try:
            yield bytes(descriptor)
        finally:
            for ref in tuple(self.live):
                t = ref() if ref else None
                if t is not None:
                    t.erase()
                    t.closed = True
            origins, parents, saved = self.frames.pop()
            position = 0
            restored = []
            for _ in range(self.slots):
                row = []
                for _ in range(3):
                    width = 0
                    while position < len(saved) and saved[position] == 1:
                        width += 1
                        position += 1
                    need(width > 0 and position < len(saved), 'continuation header delimiter')
                    position += 1
                    need(position + width <= len(saved), 'complete continuation header')
                    value = 0
                    for bit in saved[position:position + width]:
                        value = 2 * value + bit
                    position += width
                    row.append(value)
                restored.append(row)
            for i, t in enumerate(parents):
                need(len(self.backings[i]) == self.origins[i], 'child work fully retired')
                need(self.backings[i][-1] == 2, 'local delimiter retained')
                self.backings[i].pop()
                present, size, head = restored[i]
                need(present == int(t is not None), 'restored role presence')
                need(0 <= head <= size, 'restored role bounds')
                if t:
                    need(t.size == size, 'parked role extent')
                    t.head = head
                distance = size - head
                self.meter.moves += distance + 1
                self.meter.erases += 1
                self.payload_boundary_steps += distance + 2
            self.origins = origins
            self.live = [weakref.ref(t) if t else None for t in parents]
            self.depth -= 1
            need(saved[position:] == descriptor[len(header):], 'return descriptor restored')
            self.meter.reads += len(saved)
            self.meter.erases += len(saved)
            self.meter.moves += 2 * len(saved)
            self.descriptor_transport_model_steps += 4 * len(saved)


class Segment:
    def __init__(self, arena, slot, origin, depth):
        self.arena, self.slot, self.origin, self.depth = arena, slot, origin, depth
        self.meter = arena.meter
        self.head = self.size = 0
        self.closed = False

    @property
    def data(self):
        return DataView(self)

    def active(self):
        need(not self.closed and self.depth == self.arena.depth, 'active local segment')

    def read(self, size):
        self.active()
        need(0 <= size <= self.size - self.head, 'sequential read boundary')
        start = self.origin + self.head
        value = self.arena.backings[self.slot][start:start + size]
        self.head += size
        self.meter.reads += size
        self.meter.moves += size
        return value

    def write(self, value):
        self.active()
        need(self.head == self.size, 'append-only output')
        need(all(b in (0, 1) for b in value), 'binary payload alphabet')
        self.arena.backings[self.slot].extend(value)
        self.head += len(value)
        self.size += len(value)
        self.meter.writes += len(value)
        self.meter.moves += len(value)

    def rewind(self):
        self.active()
        self.meter.moves += self.head
        self.head = 0

    def finish(self):
        self.active()
        need(self.head == self.size, 'complete sequential consumption')

    def erase(self):
        self.rewind()
        self.meter.erases += self.size
        self.meter.moves += 2 * self.size
        del self.arena.backings[self.slot][self.origin:]
        self.size = self.head = 0
