"""Encoded ordinary interchange around the sealed p=1 reversed caller."""
from contextlib import ExitStack

import source
_loader, _padding, outer = source.activate()
from bitstream import atom_swap
from cardinal_counts import Count, positive
from directory import append_tape
from encoded import Profile, compare, select
from physical_words import PhysicalArena
from records import Program, RECORD_END, ROOT, Tape, append_word
from role_parking import transfer
from scratch_pool import ScratchPool
from session import (OuterScope, RootSession, borrowed_count, borrowed_tape,
                     erase_marker, initialize_marker, sealed_constructors)
from stream import Counter
from words import BLANK, LEFT, Ring, need


def radix_power(exponent, q):
    result, remaining = Count.literal(1), Counter(exponent)
    try:
        while not remaining.finished:
            result.multiply_small(q)
            remaining.decrement()
        return result
    except BaseException:
        result.close()
        raise
    finally:
        remaining.close()


def ring_from_count(bank, maximum, cleanup):
    bank.prepare(maximum)
    modulus = bank.load(maximum)
    cleanup.callback(bank.free, modulus)
    ring = Ring(modulus)
    cleanup.callback(ring.close)
    return ring


def unit_program(indices, ring, size, depth, code_bits):
    program = Program(indices, ring.arena, code_bits)
    program.tape.append(ROOT)
    for word in (size, ring.one, depth):
        append_word(program.tape, word)
    program.tape.append(RECORD_END)
    program.tape.rewind()
    return program


class Ordinary:
    """One fixed inventory, reusable after the caller consumes each output.

    q, profile, source code and register capacities are compiled constants.
    run() selects the body from the encoded original width. execute_plan() is
    an interface hook for declared small grammars; production uses run().
    Successful admitted execution closes its owned state. No interrupted-macro
    recovery guarantee is part of this mathematical interface.
    """
    def __init__(self, q, binding, topology, programs, capacity=1 << 24,
                 profile=Profile(), fixture_index_floor=0, observe=None):
        need(type(q) is int and q >= 2 and binding.codes.q == q, "one compiled radix")
        need(1 <= profile.child_rank < profile.dimension and profile.row_factor >= 1,
             "contracting compiled stock profile")
        if fixture_index_floor:
            need(binding.cutoff == 2, "index-floor exception belongs only to the reduced fixture")
        self.q, self.binding, self.profile = q, binding, profile
        self.fixture_index_floor = fixture_index_floor
        self.banks = tuple(PhysicalArena(capacity) for _ in range(4))
        self.runtime = RootSession(binding, topology, programs,
                                   PhysicalArena(capacity), PhysicalArena(capacity))
        self.pool = ScratchPool(q*q+256)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        self.closed = False
        self.last_fitted = None  # Observer only.
        self.observe = observe  # Checker-only; its return value never controls execution.

    def rearm(self):
        need(self.closed and self.output.read() == BLANK, "consume previous ordinary output")
        self.output.step(-1)
        marker = self.output.read()
        need(marker in (LEFT, BLANK), "consumed ordinary output origin")
        if marker == BLANK:
            self.output.write(LEFT)
        self.output.step(1)
        for tape in self.pool.tapes:
            initialize_marker(tape)
        for bank in self.banks:
            for word in (*bank.words, bank.template):
                initialize_marker(word.tape)
        self.runtime.rearm()
        self.closed = False

    def finish(self, fitted):
        self.pool.empty()
        self.runtime.finish(2 if fitted else 0)
        for bank in self.banks:
            bank.erase_owned()
        for tape in self.pool.tapes:
            erase_marker(tape)
        self.closed, self.last_fitted = True, fitted

    def fallback(self, payload, original, prefixes, gap, suffix):
        with ExitStack() as cleanup:
            modulus = radix_power(original, self.q)
            cleanup.callback(modulus.close)
            ring = ring_from_count(self.banks[0], modulus, cleanup)
            extents = [value.marginal() for value in (prefixes, gap, suffix)]
            for value in extents:
                cleanup.callback(value.close)
            return atom_swap(payload, ring, self.q, *extents)

    def fitted(self, payload, plan, prefixes, gap, suffix):
        with ExitStack() as cleanup:
            modulus = radix_power(plan["width"], self.q)
            remainder = radix_power(plan["remainder"], self.q)
            one = Count.literal(1)
            for value in (modulus, remainder, one):
                cleanup.callback(value.close)
            ring = ring_from_count(self.banks[0], modulus, cleanup)
            high = ring_from_count(self.banks[1], plan["rows"], cleanup)
            tail = (None if plan["remainder"].zero() else
                    ring_from_count(self.banks[2], remainder, cleanup))
            index_maximum = Count(plan["body"])
            cleanup.callback(index_maximum.close)
            if self.fixture_index_floor:
                floor = Count.literal(self.fixture_index_floor)
                if compare(index_maximum, floor) < 0:
                    index_maximum.close()
                    index_maximum = Count(floor)
                    cleanup.callback(index_maximum.close)
                floor.close()
            indices = self.banks[3]
            indices.prepare(index_maximum)
            size, depth = indices.load(plan["body"]), indices.zero()
            cleanup.callback(indices.free_many, size, depth)
            self.runtime.arena.prepare(modulus)
            self.runtime.indices.prepare(index_maximum)
            program = unit_program(indices, ring, size, depth, self.binding.codes.bits)
            directory = self.pool.acquire()
            cleanup.callback(program.tape.clear)
            cleanup.callback(directory.clear)
            actual_gap = Count.product(remainder, gap)
            following = Count.product(actual_gap, plan["rows"])
            actual_gap.close()
            actual_gap = following
            actual_suffix = Count.product(remainder, suffix)
            cleanup.callback(actual_gap.close)
            cleanup.callback(actual_suffix.close)

            def callee(padded, rows):
                if self.observe is not None:
                    self.observe("before", borrowed_tape(padded), None)
                with self.scope.suspended():
                    returned = self.runtime.run(
                        borrowed_tape(padded), borrowed_tape(directory), borrowed_tape(program.tape),
                        ring.modulus, size, depth, borrowed_count(prefixes), borrowed_count(rows),
                        borrowed_count(one), borrowed_count(actual_gap), borrowed_count(actual_suffix))
                if self.observe is not None:
                    self.observe("after", borrowed_tape(padded), returned)
                return returned

            return outer.interchange(payload, size, ring, high, self.q, prefixes, gap, suffix,
                                     plan["stock"], callee, remainder_ring=tail)

    def execute_plan(self, payload, original, prefixes, gap, suffix, plan_factory):
        if self.closed:
            self.rearm()
        need(self.output.read() == BLANK and borrowed_tape(payload) is not self.output,
             "distinct empty ordinary output port")
        for value in (original, prefixes, gap, suffix):
            positive(value)
        with sealed_constructors(), self.scope.installed():
            plan = plan_factory()
            try:
                result = (self.fitted(borrowed_tape(payload), plan, prefixes, gap, suffix)
                          if plan["fits"] else
                          self.fallback(borrowed_tape(payload), original, prefixes, gap, suffix))
                transfer(result, self.output)
                result.clear()  # The literal transfer erases cells but does not end a lease.
            finally:
                for name, value in plan.items():
                    if name != "fits":
                        value.close()
            self.finish(plan["fits"])
        return self.output

    def run(self, payload, original, prefixes, gap, suffix):
        return self.execute_plan(payload, original, prefixes, gap, suffix,
                                 lambda: select(original, self.q, self.profile))
