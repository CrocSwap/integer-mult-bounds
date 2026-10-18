"""Reuse a completed physical root while its outer owner retains templates."""
from contextlib import contextmanager
from types import FunctionType

import source
_loader, padding, outer = source.activate()
from macro_machine import Machine
from records import Tape
from scratch_pool import Lease
from cardinal_counts import Count
from words import Arena, BLANK, LEFT, need


def erase_marker(tape):
    need(tape.read() == BLANK, "empty body before owned marker erasure")
    tape.step(-1)
    need(tape.read() == LEFT, "owned marker at the local origin")
    tape.write(BLANK)
    tape.step(1)


def initialize_marker(tape):
    need(tape.read() == BLANK, "empty body before marker initialization")
    tape.step(-1)
    need(tape.read() == BLANK, "blank owned origin")
    tape.write(LEFT)
    tape.step(1)


def borrowed_tape(tape):
    """Expose the physical input without transferring an outer lease's ownership.

    Machine.commit consumes Lease results. Root input ports are borrowed, so
    they must carry physical views even when the outer owner uses a lease.
    """
    return tape.owned() if isinstance(tape, Lease) else tape


def borrowed_count(count):
    view = object.__new__(Count)
    view.tape = borrowed_tape(count.tape)
    return view


@contextmanager
def sealed_constructors():
    original_tape, original_arena = Tape.__init__, Arena.__init__
    def forbidden(*_args, **_kwargs):
        raise ValueError("physical allocation inside the ordinary invocation")
    Tape.__init__ = Arena.__init__ = forbidden
    try:
        yield
    finally:
        Tape.__init__, Arena.__init__ = original_tape, original_arena


class OuterScope:
    """Suspend allocation-site specialization without ending any live lease."""
    def __init__(self, pool):
        self.pool = pool
        self.manager = self.transform = None

    def enable(self):
        need(self.manager is None, "one active outer factory scope")
        self.manager = self.pool.install()
        self.manager.__enter__()
        self.transform = padding.transform
        namespace = dict(self.transform.__globals__)
        namespace["Tape"] = self.pool.acquire
        # Preserve complete()'s nominal Tape ownership checks. Only transform's
        # immutable constructor site receives the fixed-role factory.
        padding.transform = FunctionType(self.transform.__code__, namespace,
                                         self.transform.__name__, self.transform.__defaults__,
                                         self.transform.__closure__)

    def disable(self):
        need(self.manager is not None, "active outer factory scope")
        padding.transform = self.transform
        manager, self.manager = self.manager, None
        manager.__exit__(None, None, None)

    @contextmanager
    def installed(self):
        self.enable()
        try:
            yield self
        finally:
            self.disable()

    @contextmanager
    def suspended(self):
        self.disable()
        try:
            yield
        finally:
            self.enable()


class RootSession(Machine):
    """Borrow initialized role/bank templates for two completed root calls.

    The outer invocation owns these markers and erases them once at its end.
    A successful F return restores the supplied initialized workspace state.
    This does not provide recovery from an interrupted or failing inner macro.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.completed_roots = 0

    def erase_work(self):
        need(not self.arena.live and not self.indices.live and not self.pool.live,
             "completed root returns empty banks and scratch leases")
        need(self.numerical.machine.tapes == [{}, {0: "^"}], "completed root returns parking baseline")
        for tape in (*self.roles.values(), *self.handoff.values()):
            need(tape.read() == BLANK, "completed root returns empty role bodies")
            tape.step(-1)
            need(tape.read() == LEFT, "session retains its initialized role marker")
            tape.step(1)
        self.completed_roots += 1

    def run(self, *args, **kwargs):
        need(self.output.read() == BLANK, "consume prior root output before reuse")
        return super().run(*args, **kwargs)

    def finish(self, expected=2):
        need(self.completed_roots == expected and self.output.read() == BLANK,
             "expected completed and consumed ordinary-wrapper calls")
        need(not self.arena.live and not self.indices.live and not self.pool.live,
             "empty numerical and scratch roles at session end")
        if hasattr(self.arena, "erase_owned"):
            for tape in (*self.roles.values(), *self.handoff.values(), *self.pool.tapes):
                erase_marker(tape)
            self.arena.erase_owned()
            self.indices.erase_owned()
            self.numerical._empty_port()
            self.numerical._move(1, -1)
            self.numerical._write(1, "_")
            self.numerical._move(1, 1)
            self.closed = True
        else:
            Machine.erase_work(self)
        erase_marker(self.output)

    def rearm(self):
        need(self.closed and hasattr(self.arena, "erase_owned"), "closed physical session")
        for tape in (*self.roles.values(), *self.handoff.values(), *self.pool.tapes, self.output):
            initialize_marker(tape)
        for bank in (self.arena, self.indices):
            need(not bank.live and not bank.initialized, "blank numerical session")
            for word in (*bank.words, bank.template):
                initialize_marker(word.tape)
        self.numerical._move(1, -1)
        need(self.numerical._read(1) == "_", "blank owned parking origin")
        self.numerical._write(1, "^")
        self.numerical._move(1, 1)
        self.closed, self.completed_roots = False, 0
