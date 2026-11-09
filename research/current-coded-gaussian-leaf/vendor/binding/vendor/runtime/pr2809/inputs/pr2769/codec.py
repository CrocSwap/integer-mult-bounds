"""Two fixed tapes park and restore two finite numerical register banks.

Word values and parking depth stay on tapes. Bank/slot labels and the live
maps range over fixed finite inventories. Counters below are observations.
"""
from parking_machine import HALTS, Machine
from words import LEFT, ONE, RIGHT, ZERO, need


class BankParking:
    def __init__(self, residue_arena, index_arena, machine=None):
        self.arenas = (residue_arena, index_arena)
        need(residue_arena is not index_arena, "two distinct fixed numerical banks")
        self.capacities = tuple(arena.capacity for arena in self.arenas)
        self.slot_bits = tuple(max(1, (capacity-1).bit_length()) for capacity in self.capacities)
        self.machine = Machine(packet={0: "^"}, heads=(0, 1)) if machine is None else machine
        self.codec_counts = dict(reads=0, writes=0, moves=0, slot_tests=0, commands=0)

    def _read(self, tape):
        self.codec_counts["reads"] += 1
        return self.machine.tapes[tape].get(self.machine.heads[tape], "_")

    def _write(self, tape, symbol):
        self.codec_counts["writes"] += 1
        position = self.machine.heads[tape]
        if symbol == "_":
            self.machine.tapes[tape].pop(position, None)
        else:
            self.machine.tapes[tape][position] = symbol

    def _move(self, tape, direction):
        need(direction in (-1, 1), "unit codec head movement")
        self.codec_counts["moves"] += 1
        self.machine.heads[tape] += direction

    def _command(self, command):
        need(self.machine.state == "done", "parking controller is at a completed boundary")
        self.codec_counts["commands"] += 1
        self.machine.state = command
        while self.machine.state not in HALTS:
            self.machine.step()
        need(self.machine.state == "done", "matched parking command completes")

    def _empty_port(self):
        need(self._read(1) == "_", "empty packet port before bank operation")
        self._move(1, -1)
        try:
            need(self._read(1) == "^", "packet port starts after its left marker")
        finally:
            self._move(1, 1)

    def _put_bit(self, bit):
        need(bit in (ZERO, ONE) and self._read(1) == "_", "append a bit to an empty port cell")
        self._write(1, "1" if bit else "0")
        self._move(1, 1)

    def _take_bit(self):
        symbol = self._read(1)
        need(symbol in ("0", "1"), "complete binary register record")
        self._write(1, "_")
        self._move(1, 1)
        return int(symbol == "1")

    def _rewind_port(self):
        self._move(1, -1)
        while self._read(1) != "^":
            self._move(1, -1)
        self._move(1, 1)

    def _supply(self, bank, slot, word):
        self._put_bit(bank)
        for bit in range(self.slot_bits[bank]):
            self._put_bit((slot >> bit) & 1)
        word.rewind()
        while True:
            bit = word.read()
            if bit == RIGHT:
                break
            need(bit in (ZERO, ONE), "live numerical word has a complete binary extent")
            self._put_bit(bit)
            word.step(1)
        word.rewind()
        need(self._read(1) == "_", "empty packet terminator cell")
        self._write(1, "$")
        self._rewind_port()

    def park(self, keep=(frozenset(), frozenset())):
        """Park all parent slots except separately owned child input grants.

        A caller can copy modulus/width/depth into fresh slots and grant those
        copies to the child. It must close the grants before restore().
        """
        need(len(keep) == 2 and all(arena.capacity == capacity
             for arena, capacity in zip(self.arenas, self.capacities)), "fixed bank inventory")
        for bank, arena in enumerate(self.arenas):
            need(all(type(slot) is int and slot in arena.live for slot in keep[bank]),
                 "child grants are live fixed slot labels")
        self._empty_port()
        self._command("begin")
        for bank, arena in enumerate(self.arenas):
            for slot in range(self.capacities[bank]):
                self.codec_counts["slot_tests"] += 1
                if slot in arena.live and slot not in keep[bank]:
                    word = arena.words[slot]
                    need(word.slot == slot and word.arena is arena, "stable physical numerical role")
                    self._supply(bank, slot, word)
                    self._command("push")
                    arena.free(word)
            need(arena.live == set(keep[bank]), "only declared child grants remain in the bank")
        self._empty_port()

    def _restore_word(self):
        bank = self._take_bit()
        slot = 0
        for bit in range(self.slot_bits[bank]):
            slot |= self._take_bit() << bit
        arena = self.arenas[bank]
        need(slot < self.capacities[bank] and slot < len(arena.words) and
             slot not in arena.live and slot in arena.available, "original parent slot is free")
        # The allocator's finite free map may change order. The original
        # Word object/slot must survive; relabelling another object is invalid.
        arena.available.remove(slot)
        arena.available.append(slot)
        word = arena.zero()
        need(word is arena.words[slot] and word.slot == slot, "restore the original slot object")
        while word.read() != RIGHT:
            word.write(self._take_bit())
            word.step(1)
        need(self._read(1) == "$", "stored numerical word matches the fixed template extent")
        self._write(1, "_")
        self._rewind_port()
        word.rewind()

    def restore(self):
        """Restore the latest owned frame in a well-bracketed command stream."""
        need(all(arena.capacity == capacity for arena, capacity in zip(self.arenas, self.capacities)),
             "restore uses the same fixed numerical bank inventory")
        need(all(not arena.live for arena in self.arenas),
             "child clears its grants and numerical work before parent restoration")
        self._empty_port()
        while True:
            self._move(0, -1)
            symbol = self._read(0)
            self._move(0, 1)
            if symbol == "F":
                self._command("end")
                self._empty_port()
                return
            need(symbol in ("0", "1", "R"), "owned frame or matched register record")
            self._command("pop")
            self._restore_word()
