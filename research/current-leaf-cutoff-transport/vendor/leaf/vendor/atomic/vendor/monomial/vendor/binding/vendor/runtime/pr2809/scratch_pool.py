"""Reusable physical stream tapes for completed, nonrecursive source blocks.

Each lease has an explicit end. A repeated cleanup of an ended lease cannot
erase a later borrower of the same physical role. No lease crosses CALL.
"""
from contextlib import contextmanager
import sys
from types import FunctionType

import loader
loader.activate()
from records import Tape
from words import Arena, BLANK, LEFT, Meter, need


class Lease:
    def __init__(self, pool, slot):
        self.pool, self.slot, self.active = pool, slot, True
        self.physical = pool.tapes[slot]
        self.meter = Meter()

    def owned(self):
        need(self.active and self.pool.live.get(self.slot) is self, "live scratch lease")
        return self.physical

    @property
    def head(self):
        return self.owned().head

    def read(self):
        if not self.active:
            raise ValueError("live scratch lease")
        self.meter.reads += 1
        return self.physical.read()

    def write(self, symbol):
        if not self.active:
            raise ValueError("live scratch lease")
        self.meter.writes += 1
        self.physical.write(symbol)

    def step(self, direction):
        if not self.active:
            raise ValueError("live scratch lease")
        self.meter.moves += 1
        self.physical.step(direction)

    def append(self, symbol):
        self.operation(self.physical.append, symbol)

    def rewind(self):
        self.operation(self.physical.rewind)

    def operation(self, method, *args):
        """Run the same literal tape loop without a lease wrapper at each cell.

        Counter differences update only the observer's lease meter; the method
        still performs its real reads, writes and unit moves on the physical tape.
        """
        if not self.active:
            raise ValueError("live scratch lease")
        meter = self.physical.meter
        before = meter.reads, meter.writes, meter.moves
        try:
            return method(*args)
        finally:
            self.meter.reads += meter.reads - before[0]
            self.meter.writes += meter.writes - before[1]
            self.meter.moves += meter.moves - before[2]

    def clear(self):
        if not self.active:
            return
        self.operation(self.physical.clear)
        self.active = False
        del self.pool.live[self.slot]


class ScratchPool:
    def __init__(self, capacity):
        need(type(capacity) is int and capacity > 0, "fixed scratch capacity")
        self.tapes = tuple(Tape() for _ in range(capacity))
        self.live = {}
        self.peak = self.allocations = 0  # Checker observations, never selectors.

    def acquire(self):
        for slot, tape in enumerate(self.tapes):
            if slot not in self.live:
                # clear()'s rewind supplies the origin invariant. No physical
                # head coordinate enters the allocator's finite slot choice.
                need(tape.read() == BLANK, "empty scratch role before reuse")
                lease = Lease(self, slot)
                self.live[slot] = lease
                self.peak = max(self.peak, len(self.live))
                self.allocations += 1
                return lease
        raise ValueError("fixed scratch role inventory exhausted")

    def empty(self):
        need(not self.live, "completed macro closes all scratch leases")
        for tape in self.tapes:
            need(tape.read() == BLANK, "completed macro leaves scratch bodies empty")
            tape.step(-1)
            need(tape.read() == LEFT, "completed scratch head stands after LEFT")
            tape.step(1)

    @contextmanager
    def install(self):
        """Specialize only the authenticated source's Tape allocation sites.

        Defaults retain the original Tape class object after imports; specialize
        those defaults as well as module globals. Restore the process namespace
        on exit. This adapter never changes a frozen file.
        """
        import controller
        saved = []
        for module in tuple(sys.modules.values()):
            path = getattr(module, "__file__", None)
            if path is None or not str(path).startswith(str(loader.CALLER)):
                continue
            for name, value in tuple(vars(module).items()):
                if value is Tape:
                    saved.append((module, name, value))
                    setattr(module, name, self.acquire)
                elif isinstance(value, FunctionType) and value.__defaults__:
                    old = value.__defaults__
                    if any(item is Tape for item in old):
                        saved.append((value, "__defaults__", old))
                        value.__defaults__ = tuple(self.acquire if item is Tape else item for item in old)
        original_close = controller.Callback.close
        original_tape_init, original_arena_init = Tape.__init__, Arena.__init__
        def close(callback):
            original_close(callback)
            # The source's close ends these borrows but leaves their empty Tape
            # objects to the host allocator. End the four physical leases here.
            for stack in (callback.pending, callback.values):
                stack.tape.clear()
                stack.reverse.clear()
        controller.Callback.close = close
        def forbid_tape(_self, *_args, **_kwargs):
            raise ValueError("physical Tape allocation inside a completed macro")
        def forbid_arena(_self, *_args, **_kwargs):
            raise ValueError("numerical Arena allocation inside a completed macro")
        Tape.__init__, Arena.__init__ = forbid_tape, forbid_arena
        try:
            yield self
        finally:
            Tape.__init__, Arena.__init__ = original_tape_init, original_arena_init
            controller.Callback.close = original_close
            for owner, name, value in reversed(saved):
                setattr(owner, name, value)
