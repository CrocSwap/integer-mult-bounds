"""A fixed numerical bank with an implicit empty state for each unused port."""
from physical_words import PhysicalArena, PhysicalWord
from records import Tape
from words import BLANK, LEFT, Meter, need


class FreeSlots:
    def __init__(self, capacity):
        self.capacity = capacity
        self.first_unused = 0
        self.freed = []

    def __bool__(self):
        return bool(self.freed) or self.first_unused < self.capacity

    def pop(self):
        if self.freed:
            return self.freed.pop()
        need(self.first_unused < self.capacity, "fixed numerical role capacity")
        slot = self.first_unused
        self.first_unused += 1
        return slot

    def append(self, slot):
        need(0 <= slot < self.first_unused, "release a reserved numerical port")
        self.freed.append(slot)

    def __contains__(self, slot):
        return slot in self.freed or self.first_unused <= slot < self.capacity

    def remove(self, slot):
        # BankParking restores only labels that it previously parked and freed.
        self.freed.remove(slot)


class WordPort:
    """A view of the tape at a fixed bank coordinate. Only four operations move data."""
    read, write, step = Tape.read, Tape.write, Tape.step

    def __init__(self, marker):
        self.cells, self.head, self.meter = bytearray([marker]), 1, Meter()


class ReservedWord(PhysicalWord):
    def __init__(self, arena, slot):
        self.arena, self.slot, self.tape = arena, slot, WordPort(arena.dormant_marker)


class ReservedWords:
    def __init__(self, arena):
        self.arena = arena
        self.touched = {}

    def __len__(self):
        return self.arena.capacity

    def __getitem__(self, slot):
        need(0 <= slot < len(self), "valid fixed bank label")
        if slot not in self.touched:
            need(self.arena.initialized, "first use of an initialized bank port")
            self.touched[slot] = ReservedWord(self.arena,slot)
        return self.touched[slot]

    def __iter__(self):
        # All other cells equal the bank's uniform unused-marker phase.
        return iter(self.touched.values())


class ReservedArena(PhysicalArena):
    def __init__(self, capacity):
        need(type(capacity) is int and 0 < capacity <= 1 << 24, "fixed numerical bank")
        self.capacity, self.meter = capacity, Meter()
        self.words, self.available = ReservedWords(self), FreeSlots(capacity)
        self.live, self.initialized = set(), False
        self.dormant_marker = LEFT
        self.template = PhysicalWord(self, -1)

    def erase_owned(self):
        super().erase_owned()
        self.dormant_marker = BLANK

    def rearm_dormant(self):
        need(self.dormant_marker == BLANK, "erased dormant bank origins")
        self.template.step(-1)
        need(self.template.read() == LEFT, "rearmed template marks the new session")
        self.template.step(1)
        self.dormant_marker = LEFT
