"""Physical ordinary wrapper and root with compact436's finite program labels."""
from compact_banks import ReservedArena
from compact_digits import atom_swap
from compact_nodes import CompactNodeOperations
from compact_outer import CompactFitted
from contextlib import ExitStack
from encoded import Profile
from macro_machine import CAPSULE, NAMES, codec
from ordinary import Ordinary, radix_power, ring_from_count
from records import Tape
from role_parking import FiniteFields, RoleParking
from scratch_pool import ScratchPool
from session import OuterScope, RootSession
from words import BLANK, need


class CompactRoot(CompactNodeOperations, RootSession):
    def __init__(self, binding, topology, programs, arena, indices):
        self.binding, self.topology, self.programs = binding, topology, tuple(programs)
        self.arena, self.indices = arena, indices
        staged = max(program.staged_roles for program in programs)
        labels = (*NAMES, *(("family", i) for i in range(topology.families)),
                  *(("stage", i) for i in range(staged)))
        self.roles = {label: Tape() for label in labels}
        self.handoff = {label: Tape() for label in CAPSULE}
        self.output = Tape()
        self.pool = ScratchPool(256)
        self.numerical = codec.BankParking(arena, indices)
        self.streams = RoleParking(self.numerical, self.roles.values())
        self.header = FiniteFields((2, len(programs), max(p.extent for p in programs),
                                   arena.capacity, arena.capacity, arena.capacity,
                                   indices.capacity, indices.capacity))
        self.context = self.program = self.size = self.depth = None
        self.geometry_state = None
        self.pc = self.mode = self.completed_roots = 0
        self.root, self.closed = True, False
        self.observe = None
        self.counts = dict(macros=0, residuals=0, calls=0, returns=0)

    def rearm(self):
        super().rearm()
        for bank in (self.arena,self.indices):
            bank.rearm_dormant()

    def run(self, *args, **kwargs):
        need(not self.closed and self.output.read() == BLANK, "owned root and empty output")
        with self.pool.install():
            self.load_root(*args, **kwargs)
            while True:
                self.boundary()
                operation, successor = self.programs[self.mode].step(self.pc)
                # call() encodes pc + 1 before it transfers control to the child.
                self.pc = successor - 1
                action = self.dispatch(operation)
                self.counts["macros"] += 1
                if action == "done":
                    break
                if action == "next":
                    self.pc = successor
            self.pool.empty()
            need(self.numerical.machine.tapes == [{}, {0: "^"}], "complete physical stack return")
            self.erase_work()
        return self.output


class CompactOrdinary(CompactFitted, Ordinary):
    def __init__(self, q, binding, topology, programs, capacity=1 << 24,
                 profile=Profile(), fixture_index_floor=0):
        need(type(q) is int and q >= 2 and binding.codes.q == q, "one compiled radix")
        need(1 <= profile.child_rank < profile.dimension and profile.row_factor >= 1,
             "contracting compiled stock profile")
        if fixture_index_floor:
            need(binding.cutoff == 2, "reduced index-floor fixture")
        self.q, self.binding, self.profile = q, binding, profile
        self.fixture_index_floor = fixture_index_floor
        self.banks = tuple(ReservedArena(capacity) for _ in range(4))
        self.runtime = CompactRoot(binding, topology, programs,
                                   ReservedArena(capacity), ReservedArena(capacity))
        self.pool = ScratchPool(512)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        self.closed, self.last_fitted, self.observe = False, None, None

    def rearm(self):
        super().rearm()
        for bank in self.banks:
            bank.rearm_dormant()

    def fallback(self, payload, original, prefixes, gap, suffix):
        with ExitStack() as cleanup:
            modulus = radix_power(original, self.q)
            cleanup.callback(modulus.close)
            ring = ring_from_count(self.banks[0], modulus, cleanup)
            extents = [value.marginal() for value in (prefixes, gap, suffix)]
            for value in extents:
                cleanup.callback(value.close)
            return atom_swap(payload, ring, self.q, *extents, self.pool.acquire)
