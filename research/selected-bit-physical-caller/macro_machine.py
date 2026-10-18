"""One active frame, fixed stream roles and an encoded parent continuation."""
from contextlib import contextmanager

import loader
codec = loader.activate()
from cardinal_counts import Count, positive
from cardinality import multiply_atom_power
from directory import Context, append_tape, produce
from driver import xor_family
from episode import xor_packet
import fresh_rows
from layout import Layout
from macro_binding import view
from numeric import Geometry
from packet import read_prefix
import packet_engine
import peel
from plan import Request
from records import Program, Tape
from recursive_call import copy_word
from residual_blocks import events as block_events
from role_parking import FiniteFields, RoleParking, transfer
from routes import copy_rows, route_packet
from scratch_pool import Lease, ScratchPool
from selection import gather, scatter
from stream import Counter
from trace import child
from words import BLANK, LEFT, Ring, Unsigned, need


NAMES = ("source", "peeled", "old_directory", "program", "old_count", "rows",
         "before", "gap", "suffix", "unused", "leading", "fibre", "highs",
         "family_rows", "directory", "prefixes", "current", "copy_source", "idle", "swap", "header")
CAPSULE = ("source", "old_directory", "program", "old_count", "rows", "before", "gap", "suffix")


class Machine:
    def __init__(self, binding, topology, programs, arena, indices, observe=None):
        self.binding, self.topology, self.programs = binding, topology, tuple(programs)
        self.arena, self.indices = arena, indices
        staged = max(program.staged_roles for program in programs)
        labels = (*NAMES, *(("family", i) for i in range(topology.families)),
                  *(("stage", i) for i in range(staged)))
        self.roles = {label: Tape() for label in labels}
        self.handoff = {label: Tape() for label in CAPSULE}
        self.output = Tape()
        self.pool = ScratchPool(binding.codes.q ** 2 + 128)
        self.numerical = codec.BankParking(arena, indices)
        self.streams = RoleParking(self.numerical, self.roles.values())
        self.header = FiniteFields((2, len(programs), max(len(p.operations) for p in programs),
                                   arena.capacity, arena.capacity, arena.capacity,
                                   indices.capacity, indices.capacity))
        self.context = self.program = self.size = self.depth = None
        self.geometry_state = None
        self.pc = self.mode = 0
        self.root = True
        self.closed = False
        self.observe = observe  # Checker-only; the controller never reads its result.
        self.counts = dict(macros=0, residuals=0, calls=0, returns=0)  # Observers only.

    def tape(self, label):
        return self.roles[label]

    def count(self, label):
        result = object.__new__(Count)
        result.tape = self.tape(label)
        return result

    def commit(self, result, label):
        target = self.tape(label)
        if result is target:
            return
        target.clear()
        append_tape(result, target)
        target.rewind()
        if isinstance(result, Lease):
            result.clear()

    def save_count(self, value, label):
        self.commit(value.tape, label)
        value.close()

    def new_context(self, modulus, size, depth):
        ring = Ring(modulus)
        context = Context(ring, self.binding.codes)
        self.save_count(context.highs, "highs")
        context.highs = self.count("highs")
        self.context, self.size, self.depth = context, size, depth
        self.program = view(Program, self, self.tape("program"))

    def restore_context(self, labels):
        modulus, one, cap, size, depth = labels
        ring = object.__new__(Ring)
        ring.arena, ring.raw = self.arena, Unsigned(self.arena)
        ring.modulus, ring.one = self.arena.words[modulus], self.arena.words[one]
        context = object.__new__(Context)
        context.ring, context.arena, context.raw = ring, self.arena, ring.raw
        context.codes = self.binding.codes
        context.q, context.dimension = context.codes.q, context.codes.dimension
        context.cap, context.highs = self.arena.words[cap], self.count("highs")
        self.context = context
        self.size, self.depth = self.indices.words[size], self.indices.words[depth]
        self.program = view(Program, self, self.tape("program"))

    def boundary(self):
        self.pool.empty()
        for tape in self.roles.values():
            tape.step(-1)
            need(tape.read() == LEFT, "completed canonical head stands after LEFT")
            tape.step(1)
        ring = self.context.ring
        expected_indices = {self.size.slot, self.depth.slot}
        if self.geometry_state is not None:
            _definition, page, layout, fields, columns = self.geometry_state
            expected_indices.update(word.slot for word in
                                    (columns, page.one, page.two, page.leaf_cutoff, fields,
                                     layout.core, layout.extra, layout.total))
        need(self.arena.live == {ring.modulus.slot, ring.one.slot, self.context.cap.slot} and
             self.indices.live == expected_indices,
             "only declared persistent and active geometry words at a completed macro")

    @contextmanager
    def geometry(self, definition):
        if self.geometry_state is not None:
            owner, page, layout, fields, _columns = self.geometry_state
            need(owner is definition, "one active residual geometry")
            yield page, layout, fields
            return
        divisor = self.indices.literal(self.context.dimension)
        columns, remainder = Unsigned(self.indices).divmod(self.size, divisor)
        self.indices.free_many(divisor, remainder)
        page = Geometry(definition.plan, self.indices, columns, self.depth, definition.code, self.program)
        if self.binding.cutoff != 64:
            self.indices.free(page.leaf_cutoff)
            page.leaf_cutoff = self.indices.literal(self.binding.cutoff)
        layout = Layout(page, self.size, self.context.ring, self.context.q,
                        self.count("leading"), self.count("gap"), self.count("suffix"))
        fields = page.plus(self.depth, page.one)
        self.geometry_state = definition, page, layout, fields, columns
        yield page, layout, fields

    def close_geometry(self):
        if self.geometry_state is None:
            return
        _definition, page, layout, fields, columns = self.geometry_state
        self.geometry_state = None
        self.indices.free(fields)
        layout.close()
        page.close()
        self.indices.free(columns)

    def node(self):
        divisor = self.indices.literal(self.context.dimension)
        columns, remainder = Unsigned(self.indices).divmod(self.size, divisor)
        valid = not columns.zero()
        self.indices.free_many(divisor, columns, remainder)
        need(valid, "complete internal node width")
        for label in ("old_count", "rows", "before", "gap", "suffix"):
            self.count(label).normalize()
            positive(self.count(label))
        # Preserve source ingress validation before the first payload operation.
        first = read_prefix(self.tape("old_directory"), self.depth)
        self.tape("old_directory").rewind()
        zero = self.indices.zero()
        incoming = self.binding.incoming(self)
        try:
            value = incoming.coefficient(first, Request("incoming", zero))
            self.arena.free(value)
        finally:
            first.clear()
            self.indices.free(zero)
        unused = fresh_rows.quotient(self.count("rows"), self.context, self.topology.families)
        self.save_count(unused, "unused")
        stock = Count(self.count("unused"))
        try:
            need(stock.divide_small(self.binding.stock_multiple) == 0, "compatible fresh stock factor")
        finally:
            stock.close()
        self.save_count(Count.product(self.count("unused"), self.count("before")), "leading")
        fibre = Count.product(self.count("leading"), self.count("gap"))
        total = Unsigned(self.indices).times_small(self.size, 2)
        multiply_atom_power(fibre, total, self.context.ring, self.context.q)
        self.indices.free(total)
        complete = Count.product(fibre, self.count("suffix"))
        fibre.close()
        self.save_count(complete, "fibre")
        peeled = peel.run(self.tape("source"), self.context, self.indices, self.size, self.depth,
                          self.program, self.tape("old_directory"), self.count("old_count"),
                          self.count("rows"), self.count("before"), self.count("gap"),
                          self.count("suffix"), incoming)
        self.commit(peeled, "peeled")
        self.save_count(fresh_rows.family_rows(self.context), "family_rows")
        source = self.tape("peeled")
        outer = Counter(self.count("old_count"))
        try:
            while not outer.finished:
                for family in range(self.topology.families):
                    copy_rows(source, self.tape(("family", family)), self.count("family_rows"), self.count("fibre"))
                outer.decrement()
            need(source.read() == BLANK, "complete canonical fresh-row split")
        finally:
            outer.close()
            source.rewind()
            for family in range(self.topology.families):
                self.tape(("family", family)).rewind()

    def residual_begin(self, role, definition):
        self.binding.check_stock(self)
        directory, prefixes = produce(self.tape("old_directory"), self.depth, self.count("old_count"),
                                      definition.code, self.context)
        self.commit(directory, "directory")
        self.save_count(prefixes, "prefixes")
        with self.geometry(definition) as (_page, _layout, fields):
            first = read_prefix(self.tape("directory"), fields)
            self.tape("directory").rewind()
            try:
                self.binding.validate_residual(self, definition, first)
            finally:
                first.clear()
        self.commit(self.tape(role), "current")
        self.counts["residuals"] += 1
        if self.observe is not None:
            self.observe(self, "residual_begin", definition, role)

    def prepare_child(self, definition, event, layout, fields):
        need(event.parent_identity is self.program and
             event.source_code == definition.code == layout.geometry.source_code,
             "recursive gate belongs to the current program and source")
        raw = Unsigned(self.indices)
        need(raw.compare(event.width, self.size) < 0, "strict child contraction")
        extents = layout.child_extents(event.first, event.second, event.width, before=self.count("before"))
        first = read_prefix(self.tape("directory"), fields)
        self.tape("directory").rewind()
        program = None
        try:
            program = self.binding.child_program(self, definition, event, first)
            inputs = (self.tape("current"), self.tape("directory"), program,
                      self.tape("prefixes"), self.tape("unused"), *(extent.tape for extent in extents))
            for label, source in zip(CAPSULE, inputs):
                target = self.handoff[label]
                need(target.read() == BLANK, "empty fixed child handoff port")
                append_tape(source, target)
                target.rewind()
            return (self.arena.copy(self.context.ring.modulus),
                    self.indices.copy(event.width), self.indices.copy(event.depth))
        finally:
            if program is not None:
                program.clear()
            first.clear()
            for extent in extents:
                extent.close()

    def block(self, definition, block):
        grants = None
        with self.geometry(definition) as (page, layout, fields):
            if block[0] == "axis":
                axis = block[1]
                trace = child(page, page.raw.times_small(page.columns, axis),
                              page.raw.times_small(page.columns, 3 - axis),
                              self.indices.copy(page.columns), "good")
            else:
                trace = block_events(page, block)
            try:
                first = next(trace, None)
                if first is not None and first.kind == "enter" and page.raw.compare(first.width, page.leaf_cutoff) >= 0:
                    grants = self.prepare_child(definition, first, layout, fields)
                else:
                    def complete_events():
                        if first is not None:
                            yield first
                        yield from trace
                    result = packet_engine.run(self.tape("current"), complete_events(), layout,
                                               self.tape("directory"), self.count("prefixes"), fields,
                                               lambda prefix, request: self.binding.coefficient(self, definition, prefix, request))
                    self.commit(result, "current")
            finally:
                trace.close()
        if grants is not None:
            self.close_geometry()
            self.call(grants)
            return True
        return False

    def call(self, grants):
        self.pool.empty()
        need(self.geometry_state is None, "close derived geometry before the recursive cut")
        ring = self.context.ring
        self.header.write(self.tape("header"), (int(self.root), self.mode, self.pc + 1,
                          ring.modulus.slot, ring.one.slot, self.context.cap.slot,
                          self.size.slot, self.depth.slot))
        self.streams.park()
        modulus, size, depth = grants
        self.numerical.park(({modulus.slot}, {size.slot, depth.slot}))
        for label in CAPSULE:
            transfer(self.handoff[label], self.tape(label))
        self.new_context(modulus, size, depth)
        self.root, self.mode, self.pc = False, self.binding.child_mode, 0
        self.counts["calls"] += 1

    def close_frame(self):
        self.close_geometry()
        ring = self.context.ring
        self.context.close()
        ring.close()
        self.arena.free(ring.modulus)
        self.indices.free_many(self.size, self.depth)
        for tape in self.roles.values():
            tape.clear()
        self.pool.empty()
        need(not self.arena.live and not self.indices.live, "child numerical cleanup before restoration")

    def returned(self):
        families = {i: self.tape(("family", i)) for i in range(self.topology.families)}
        result = fresh_rows.merge(families, self.context, self.topology.families,
                                 self.count("old_count"), self.count("fibre"))
        need(self.output.read() == BLANK, "empty protected return port")
        append_tape(result, self.output)
        self.output.rewind()
        result.clear()
        return self.complete_return()

    def complete_return(self):
        """Return the already completed protected output through one frame."""
        self.close_frame()
        if self.root:
            return True
        self.numerical.restore()
        self.streams.restore()
        root, self.mode, self.pc, *labels = self.header.read(self.tape("header"))
        self.root = bool(root)
        self.tape("header").clear()
        self.restore_context(labels)
        transfer(self.output, self.tape("current"))
        self.counts["returns"] += 1
        return False

    def dispatch(self, operation):
        kind, *args = operation
        context, old_count, fibre = self.context, self.count("old_count"), self.count("fibre")
        if kind == "node":
            self.node()
        elif kind == "residual_begin":
            self.residual_begin(*args)
        elif kind == "block":
            if self.block(*args):
                return "jump"
        elif kind == "residual_end":
            self.close_geometry()
            transfer(self.tape("current"), self.tape(args[0]))
            self.tape("directory").clear()
            self.tape("prefixes").clear()
            if self.observe is not None:
                self.observe(self, "residual_end", args[1], args[0])
        elif kind == "gather_route":
            role, family, low, route = args
            selected = gather(self.tape(("family", family)), context, old_count, low, fibre)
            try:
                self.commit(route_packet(selected, route, context, old_count, fibre), role)
            finally:
                selected.clear()
        elif kind == "route_scatter":
            role, family, low, route = args
            result = route_packet(self.tape(role), route, context, old_count, fibre)
            try:
                changed = scatter(self.tape(("family", family)), result, context, old_count, low, fibre)
                self.commit(changed, ("family", family))
            finally:
                result.clear()
        elif kind == "gather":
            role, family, low = args
            self.commit(gather(self.tape(("family", family)), context, old_count, low, fibre), role)
        elif kind == "scatter":
            role, family, low = args
            self.commit(scatter(self.tape(("family", family)), self.tape(role), context, old_count, low, fibre), ("family", family))
        elif kind == "xor":
            target, source = args
            self.commit(xor_packet(self.tape(source), self.tape(target), context, old_count, fibre), target)
        elif kind == "family_xor":
            target, source = args
            self.commit(xor_family(self.tape(("family", source)), self.tape(("family", target)),
                                   old_count, self.count("family_rows"), fibre), ("family", target))
        elif kind == "exchange":
            first, second = (("family", index) for index in args)
            transfer(self.tape(first), self.tape("swap"))
            transfer(self.tape(second), self.tape(first))
            transfer(self.tape("swap"), self.tape(second))
        elif kind == "copy":
            self.commit(self.tape(args[0]), args[1])
            if self.observe is not None:
                self.observe(self, "copy_source", *args)
        elif kind == "move":
            transfer(self.tape(args[0]), self.tape(args[1]))
        elif kind == "clear":
            self.tape(args[0]).clear()
        elif kind == "checkpoint":
            if self.observe is not None:
                self.observe(self, *args)
        else:
            need(kind == "return", "closed finite macro alphabet")
            return "done" if self.returned() else "jump"
        return "next"

    def load_root(self, source, directory, program, modulus, size, depth, old_count, rows, before, gap, suffix, mode=0):
        need(not self.arena.live and not self.indices.live, "empty supplied working banks")
        inputs = (source, directory, program, old_count.tape, rows.tape, before.tape, gap.tape, suffix.tape)
        owned = (*self.roles.values(), *self.handoff.values(), self.output, *self.pool.tapes)
        need(all(input_tape is not work_tape for input_tape in inputs for work_tape in owned),
             "borrowed root input ports are outside the reusable working bank")
        for label, tape in zip(CAPSULE, inputs):
            self.commit(tape, label)
        self.new_context(copy_word(modulus, self.arena), copy_word(size, self.indices), copy_word(depth, self.indices))
        self.mode, self.pc, self.root = mode, 0, True

    def run(self, source, directory, program, modulus, size, depth, old_count, rows, before, gap, suffix, mode=0):
        need(not self.closed, "one owned root invocation per machine initialization")
        with self.pool.install():
            self.load_root(source, directory, program, modulus, size, depth, old_count, rows, before, gap, suffix, mode)
            while True:
                self.boundary()
                operation = self.programs[self.mode].operations[self.pc]
                action = self.dispatch(operation)
                self.counts["macros"] += 1
                if action == "done":
                    break
                if action == "next":
                    self.pc += 1
            self.pool.empty()
            need(self.numerical.machine.tapes == [{}, {0: "^"}], "complete physical stack return")
            self.erase_work()
        return self.output

    def erase_work(self):
        """Erase permanent owned markers/templates at the final root return."""
        need(not self.arena.live and not self.indices.live and not self.pool.live,
             "root cleanup follows complete frame and scratch cleanup")
        def marker(tape):
            tape.step(-1)
            need(tape.read() == LEFT, "owned work marker at the known origin")
            tape.write(BLANK)
            tape.step(1)
        for tape in (*self.roles.values(), *self.handoff.values(), *self.pool.tapes):
            need(tape.read() == BLANK, "empty body before owned marker erasure")
            marker(tape)
        for arena in (self.arena, self.indices):
            for word in arena.words:
                marker(word)
            arena.template.erase()
            marker(arena.template)
        self.numerical._empty_port()
        self.numerical._move(1, -1)
        self.numerical._write(1, "_")
        self.numerical._move(1, 1)
        self.closed = True
