"""A finite C1/B1 boundary that keeps the preceding caller on its A0 paths."""
from contextlib import contextmanager

import stage_sources
stage_sources.activate()
from cardinal_counts import Count
from cardinality import radix_power
from directory import append_tape
from physical_words import PhysicalArena
from macro_machine import Machine
from records import Tape
import routes
from session import (borrowed_count, borrowed_tape, erase_marker, initialize_marker,
                     sealed_constructors, RootSession)
import stream_runner
from words import BLANK, need

BASE_SWAP = stream_runner.atom_swap
BASE_CUBE = routes.route_cube


class StagePool:
    """Keep one parent factory scope live while the earlier stage is suspended."""
    def __init__(self, base, adapter):
        need(stream_runner.atom_swap is BASE_SWAP and routes.route_cube is BASE_CUBE,
             "compile successor scopes from the sealed base bindings")
        self.base, self.adapter = base, adapter
        self.manager = None
        self.original_swap = stream_runner.atom_swap
        self.original_cube = routes.route_cube
        adapter.scope = self

    def __getattr__(self, name):
        return getattr(self.base, name)

    def enable(self):
        need(self.manager is None, "one active successor factory scope")
        need(stream_runner.atom_swap is self.original_swap and routes.route_cube is self.original_cube,
             "enter successor from restored preceding bindings")
        self.manager = self.base.install()
        self.manager.__enter__()
        stream_runner.atom_swap = self.adapter.swap
        routes.route_cube = self.adapter.route_cube

    def disable(self):
        need(self.manager is not None, "active successor factory scope")
        stream_runner.atom_swap = self.original_swap
        routes.route_cube = self.original_cube
        manager, self.manager = self.manager, None
        manager.__exit__(None, None, None)

    @contextmanager
    def install(self):
        with sealed_constructors():
            self.adapter.start()
            self.enable()
            try:
                yield self
            finally:
                self.disable()

    @contextmanager
    def suspended(self):
        self.disable()
        need(stream_runner.atom_swap is self.original_swap and routes.route_cube is self.original_cube,
             "preceding stage retains both elementary bindings")
        self.adapter.in_base = True
        try:
            yield
        finally:
            self.adapter.in_base = False
            self.enable()


class Adapter:
    def __init__(self, native, registry, capacity=1 << 24):
        self.native, self.registry, self.q = native, registry, native.q
        self.scope = None
        self.in_base = False
        self.ready = True
        self.high_bank = PhysicalArena(capacity)
        self.high_bank.erase_owned()
        # The borrowed baseline is empty native work plus one initialized output
        # port, whether the following root actually reaches an interchange.
        self.native.finish(False)
        self.calls = dict(swaps=0, cubes=0)  # Checker observations only.

    def start(self):
        if not self.ready:
            initialize_marker(self.native.output)
            self.ready = True

    def close(self):
        need(not self.in_base and self.native.closed and self.native.output.read() == BLANK,
             "completed preceding stage at successor boundary")
        if self.ready:
            erase_marker(self.native.output)
            self.ready = False

    def swap(self, source, ring, q, before, middle, suffix):
        need(not self.in_base and self.scope is not None and q == self.q,
             "successor primitive cannot re-enter from its preceding stage")
        width = Count.literal(0)
        extents = [Count(value) for value in (before, middle, suffix)]
        try:
            for _ in radix_power(ring, q):
                width.increment()
            with self.scope.suspended():
                returned = self.native.run(borrowed_tape(source), borrowed_count(width),
                                           *(borrowed_count(value) for value in extents))
            result = self.scope.acquire()
            try:
                append_tape(returned, result)
                result.rewind()
            except BaseException:
                result.clear()
                raise
            finally:
                returned.clear()
            self.calls["swaps"] += 1
            return result
        finally:
            width.close()
            for value in extents:
                value.close()

    def route_cube(self, source, route, context, fibre, factory=None):
        need(not self.in_base and self.scope is not None, "successor route stage")
        from high_route import execute
        result = execute(source, route, context, fibre, self,
                         self.scope.acquire if factory is None else factory)
        self.calls["cubes"] += 1
        return result


class SuccessorSession(RootSession):
    def finish(self, expected=2):
        super().finish(expected)
        self.pool.adapter.close()


class SuccessorMachine(Machine):
    def erase_work(self):
        super().erase_work()
        self.pool.adapter.close()


def configure(runtime, native, registry):
    """Specialize a fresh fixed inventory before reading any numerical input."""
    need(runtime.context is None and not runtime.arena.live and not runtime.indices.live,
         "compile the successor before root loading")
    need(not isinstance(runtime.pool, StagePool), "one stage specialization")
    # The extra fixed allowance covers the adapter's live cardinalities while
    # source completed-block scratch remains available.
    runtime.pool.tapes += tuple(Tape() for _ in range(128))
    adapter = Adapter(native, registry, capacity=runtime.arena.capacity)
    runtime.pool = StagePool(runtime.pool, adapter)
    return runtime


def successor_session(binding, topology, programs, arena, indices, native, registry):
    return configure(SuccessorSession(binding, topology, programs, arena, indices), native, registry)


def successor_machine(binding, topology, programs, arena, indices, native, registry, observe=None):
    return configure(SuccessorMachine(binding, topology, programs, arena, indices, observe), native, registry)


def promote_ordinary(ordinary, native, registry):
    """Reuse the fresh outer wrapper's actual roles in its C1 root session.

    Only the finite controller view changes; no physical tape or Word role is
    copied, abandoned or allocated as a function of input size.
    """
    current = ordinary.runtime
    runtime = object.__new__(SuccessorSession)
    runtime.__dict__.update(current.__dict__)
    ordinary.runtime = configure(runtime, native, registry)
    return ordinary
