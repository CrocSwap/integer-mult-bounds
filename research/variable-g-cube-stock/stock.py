"""Bounded prefix reuse for the cited physical-H tape program.

The seven physical bit arrays are allocated once. Logical tape lengths may
change between rounds; butterfly auxiliaries are reused after each blank return.
"""

from __future__ import annotations

NAMES = ("source", "scratch", "root", "consumer", "low", "high", "paired")
AUXILIARIES = NAMES[4:]
MAX_CELLS = 1 << 20
MAX_ROUNDS = 16


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


class Prefix:
    """A fixed backing array with an explicitly bounded active prefix."""

    def __init__(self, backing):
        self.backing = backing
        self.length = len(backing)

    def __len__(self):
        return self.length

    def __iter__(self):
        for index in range(self.length):
            yield self.backing[index]

    def __getitem__(self, index):
        if isinstance(index, slice):
            return [self.backing[i] for i in range(*index.indices(self.length))]
        require(type(index) is int and 0 <= index < self.length, "prefix index")
        return self.backing[index]

    def __setitem__(self, index, value):
        require(type(index) is int and 0 <= index < self.length, "prefix index")
        require(type(value) is int and value in (0, 1), "prefix bit")
        self.backing[index] = value

    def __eq__(self, other):
        if not isinstance(other, (list, tuple, Prefix)) or len(other) != self.length:
            return False
        return all(a == b for a, b in zip(self, other))

    def activate(self, length):
        require(type(length) is int and 0 <= length <= len(self.backing), "prefix capacity")
        require(not any(self.backing[length:]), "dirty inactive tail")
        self.length = length


def geometry(engine, ell, flags, k, p):
    require(type(ell) is int and 2 <= ell <= 4, "layout bound")
    require(isinstance(flags, tuple) and 1 <= len(flags) <= 3, "axis bound")
    require(all(type(flag) is bool for flag in flags), "axis flags")
    require(type(k) is int and 1 <= k < ell, "chunk bound")
    require(type(p) is int and 1 <= p <= 16, "precision bound")
    machine = engine.TypedActualWidthH(ell, flags, k, p)
    require(len(machine.physical) <= 9, "address bound")
    counts = tuple(len(machine.matched_bits(h)) for h in machine.levels)
    records, coefficients = 1 << len(machine.physical), 1 << ell
    components = 2 * records * coefficients
    packet, work = p + 2, p + max(counts) + 2
    lengths = (components * packet, components * work, components * packet,
               components * packet, components * work // 2,
               components * work // 2, components * work)
    require(sum(lengths) <= MAX_CELLS, "stock capacity")
    require(sum(lengths) == 6 * records * coefficients * (packet + work), "stock formula")
    return machine, dict(zip(NAMES, lengths))


class Inventory:
    def __init__(self, engine, lengths):
        self.engine = engine
        self.tapes = {name: engine.Tape(lengths[name]) for name in NAMES}
        self.views = {name: Prefix(self.tapes[name].cells) for name in NAMES}
        for name in NAMES:
            self.tapes[name].cells = self.views[name]
        self.cells = sum(lengths.values())
        self.order = ()
        self.index = 0
        self.requests = []

    def begin(self, g):
        require(type(g) is int and 1 <= g <= 3, "selected-bit bound")
        self.order = NAMES[:4] + AUXILIARIES * g
        self.index = 0
        self.requests = []

    def allocate(self, length):
        require(self.index < len(self.order), "inventory exhausted")
        name = self.order[self.index]
        tape, view = self.tapes[name], self.views[name]
        require(tape.head == 0, "allocation head")
        if name != "source":
            require(not any(view.backing), "allocation dirt")
        view.activate(length)
        tape.read = tape.write = tape.move = 0
        self.requests.append((name, length))
        self.index += 1
        return tape

    def reset_outputs(self):
        bills = {}
        for name in ("root", "consumer"):
            tape = self.tapes[name]
            require(tape.head == 0, "reset head")
            before = tape.read, tape.write, tape.move
            self.engine._blank_tape(tape)
            bills[name] = tuple(now - old for now, old in zip(
                (tape.read, tape.write, tape.move), before))
            require(bills[name] == (0, len(tape.cells), 2 * (len(tape.cells) - 1)),
                    "reset bill")
            require(not any(tape.cells) and tape.head == 0, "output reset")
        return bills

    def check_return(self):
        require(self.index == len(self.order), "allocation count")
        for name in NAMES:
            tape, view = self.tapes[name], self.views[name]
            require(tape.cells is view and tape.head == 0, "inventory return")
            require(not any(view.backing[view.length:]), "dirty inactive tail")
            if name in ("scratch",) + AUXILIARIES:
                require(not any(view.backing), "work return")


def run_schedule(engine, ell, flags, k, p, rounds):
    """Return verification snapshots; only the latest physical outputs stay live.

    Execution is serial. The module-local Tape binding is restored on every exit.
    Host snapshots and scalar control objects are outside the tape-cell model.
    """
    require(isinstance(rounds, (list, tuple)) and 1 <= len(rounds) <= MAX_ROUNDS,
            "schedule bound")
    machine, lengths = geometry(engine, ell, flags, k, p)
    inventory = Inventory(engine, lengths)
    real_tape = engine.Tape
    results = []
    try:
        engine.Tape = inventory.allocate
        for index, (h, cube) in enumerate(rounds):
            reset = inventory.reset_outputs() if index else None
            inventory.begin(len(machine.matched_bits(h)))
            call = engine.TypedActualWidthH(ell, flags, k, p)
            decoded, ledger, info = call.run(cube, h, source_order="physical")
            inventory.check_return()
            results.append({"h": h, "decoded": decoded, "ledger": ledger,
                            "info": info, "reset": reset,
                            "requests": tuple(inventory.requests),
                            "root": tuple(inventory.views["root"]),
                            "consumer": tuple(inventory.views["consumer"]),
                            "source": tuple(inventory.views["source"])})
    finally:
        engine.Tape = real_tape
    return {"cells": inventory.cells, "lengths": lengths, "rounds": results}
