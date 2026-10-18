"""Execute the pinned caller's numerical lifetime, with opaque payload seams."""

from collections import Counter
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import patch

from verify import need


class Specifications(dict):
    def __init__(self, specification, plan):
        super().__init__({0: specification})
        self.fixed_plan = plan
        self.catalogue = SimpleNamespace(requests=[SimpleNamespace(kind="LOCAL")])

    def bind(self, request_id, common, low):
        need(request_id == 0 and common and low == self[0].low, "fixed fixture source")
        return self[0]

    def plan(self, code):
        need(code == 0, "fixed fixture plan")
        return self.fixed_plan


def fixture(modules, good, rank, width, depth, borrowed):
    need(
        rank in (1, 42) and width in (64, 127) and depth in (0, 4),
        "bounded source fixture",
    )
    need(borrowed in (3, 7) and (good or rank == 1), "bounded fixture residents")
    w = modules.words
    residues = w.Arena(3, 8192)
    indices = w.Arena(max(8, (width * 64**depth).bit_length() + 1), 128)
    ring = w.Ring(residues.literal(3))
    identity = tuple(tuple(int(i == j) for j in range(64)) for i in range(64))
    low = [list(row) for row in identity]
    if not good:
        low[0], low[63] = low[63], low[0]
    low = tuple(map(tuple, low))
    template = SimpleNamespace(q=3, rank=rank, preparation=identity)
    spec = SimpleNamespace(code=0, good=good, low=low, template=template)
    projector = [
        [int(i == j and (i < rank if good else i == 63)) for j in range(64)]
        for i in range(64)
    ]
    plan = modules.plan.compile_plan(projector, rank, 3, good)
    specs = Specifications(spec, plan)
    codes = SimpleNamespace(q=3, dimension=64, bits=8, limit=256)
    context = modules.directory.Context(ring, codes)
    root = width * 64**depth
    if depth:
        specs[1] = SimpleNamespace(
            code=1,
            good=True,
            low=identity,
            template=SimpleNamespace(q=3, rank=1, preparation=identity),
        )
    events = [(0, 1, 1, 0, 0, 0)] * depth
    program = modules.records.Program.fixture(
        indices, residues, root, 2, events, code_bits=8
    )
    zero_high = [[0] * 64 for _ in range(64)]
    fields = modules.records.Fields.fixture(
        indices, residues, [(1, zero_high)] * depth, code_bits=8
    )
    parent_size, level = indices.literal(width), indices.literal(depth)
    residents = [residues.literal(i % 3) for i in range(borrowed)]
    index_residents = [indices.literal(i) for i in range(borrowed)]
    counts = [modules.cardinal_counts.Count.literal(1) for _ in range(4)]
    consumer = modules.consumer.Consumer(
        context, indices, program, specs, parent_size, level
    )
    return SimpleNamespace(**locals())


def saved_state(case):
    return tuple(
        {s: bytes(a.words[s].cells) for s in a.live}
        for a in (case.residues, case.indices)
    )


class EntryProbe:
    def __init__(self, case, bounds, retain_extra, event_capacity=200000):
        self.case, self.bounds, self.retain_extra = case, bounds, retain_extra
        need(case.residues is not case.indices, "distinct numerical arenas")
        need(1 <= event_capacity <= 200000, "bounded event capacity")
        self.event_capacity = event_capacity
        self.saved = saved_state(case)
        self.entry = [len(a.live) for a in (case.residues, case.indices)]
        self.entries, self.trace_entries, self.extents, self.scans = (
            Counter(),
            Counter(),
            0,
            0,
        )
        self.events = 0
        self.original_action = case.modules.stream_runner.action

    def check_inventory(self):
        arenas = self.case.residues, self.case.indices
        extra = [len(a.live) - b for a, b in zip(arenas, self.entry, strict=True)]
        need(
            all(a <= b for a, b in zip(extra, self.bounds, strict=True)),
            "caller entry budget",
        )
        need(extra == [0, 12], "exact caller entry inventory")
        return arenas

    def coefficient(
        self, _plan, ring, _indices, _program, _fields, _specs, _code, request
    ):
        need(request.kind == "adapter", "only adapter coefficient bodies are probed")
        for arena, saved in zip(self.check_inventory(), self.saved, strict=True):
            need(
                all(bytes(arena.words[s].cells) == value for s, value in saved.items()),
                "entry residents preserved at callback",
            )
            need(
                all(arena.words[s].head == 1 for s in arena.live),
                "callback numerical heads",
            )
            occupied = sum(
                c not in (self.case.modules.words.LEFT, self.case.modules.words.BLANK)
                for word in (*arena.words, arena.template)
                for c in word.cells
            )
            need(
                occupied == (len(arena.live) + 1) * (arena.bits + 1),
                "literal occupied content",
            )
        self.scans += 2
        self.entries[(request.reference.kind, request.reverse_adapter)] += 1
        return ring.arena.copy(ring.one)

    def add_pass(self, _source, ring, _before, _middle, _suffix, prepare, **_kwargs):
        extra = self.case.indices.zero() if self.retain_extra else None
        try:
            for _ in range(2):
                result = prepare()
                ring.arena.free(result)
        finally:
            if extra is not None:
                self.case.indices.free(extra)
        return self.case.modules.records.Tape(), {}

    def action(self, source, event, layout, coefficient, factory):
        if event.kind != "add" or event.request.kind != "adapter":
            return self.case.modules.records.Tape()
        self.check_inventory()
        key = event.request.reference.kind, event.request.reverse_adapter
        self.trace_entries[key] += 1
        if key not in self.entries:
            self.extents += 1
            return self.original_action(source, event, layout, coefficient, factory)
        return self.case.modules.records.Tape()

    def bounded_trace(self, geometry):
        iterator = self.case.modules.trace.execute(geometry)
        try:
            for position in range(self.event_capacity + 1):
                try:
                    event = next(iterator)
                except StopIteration:
                    return
                need(position < self.event_capacity, "trace event capacity")
                self.events += 1
                yield event
        finally:
            iterator.close()

    def prefix(self, directory, _fields):
        # This fixture has exactly one complete prefix. Its numerical decode
        # was exercised by Consumer.apply's unmodified validation Callback.
        # The coefficient spy never reads these serialized fields.
        directory.head = len(directory.cells)
        return self.case.modules.records.Tape()

    def install(self, stack):
        m = self.case.modules
        stack.enter_context(
            patch.object(m.consumer, "selected_coefficient", self.coefficient)
        )
        stack.enter_context(patch.object(m.packet_engine, "action", self.action))
        stack.enter_context(
            patch.object(m.packet_engine, "copy_bits", lambda *_args: None)
        )
        stack.enter_context(patch.object(m.stream_runner, "add_pass", self.add_pass))
        stack.enter_context(patch.object(m.consumer, "execute", self.bounded_trace))
        stack.enter_context(patch.object(m.packet_engine, "read_prefix", self.prefix))
        # Record movement is outside the numerical-slot claim. Avoid walking
        # the same 4096-word directory after every source trace event.
        stack.enter_context(
            patch.object(
                m.records.Tape, "rewind", lambda tape: setattr(tape, "head", 1)
            )
        )


def finished_record(case, meter, tapes):
    need(
        saved_state(case) == meter.saved,
        "caller restores numerical entry live sets and values",
    )
    need(
        (bytes(case.program.tape.cells), bytes(case.fields.tape.cells)) == tapes,
        "caller preserves serialized inputs",
    )
    need(
        case.program.tape.head == case.fields.tape.head == 1,
        "caller restores input heads",
    )
    expected = {
        (kind, reverse)
        for kind in ("head", "tail", "cross")
        for reverse in (False, True)
    }
    if not case.good:
        expected = {("shear", False)}
    need(set(meter.entries) == expected, "all adapter source paths exercised")
    return {
        "good": case.good,
        "rank": case.rank,
        "width": case.width,
        "depth": case.depth,
        "borrowed": case.borrowed,
        "entry": meter.entry,
        "extra": [0, 12],
        "total_trace_events": meter.events,
        "adapter_trace_events": sum(meter.trace_entries.values()),
        "callback_samples": sum(meter.entries.values()),
        "extent_paths": meter.extents,
        "literal_cell_scans": meter.scans,
    }


def run_case(
    modules,
    good=True,
    rank=1,
    width=64,
    depth=0,
    borrowed=3,
    bounds=(0, 12),
    retain_extra=False,
    event_capacity=200000,
):
    case = fixture(modules, good, rank, width, depth, borrowed)
    meter = EntryProbe(case, bounds, retain_extra, event_capacity)
    tapes = bytes(case.program.tape.cells), bytes(case.fields.tape.cells)
    source = modules.records.Tape()
    try:
        with ExitStack() as stack:
            meter.install(stack)
            result = case.consumer.apply(
                source, 0, True, case.low, case.fields.tape, *case.counts
            )
            result.clear()
        return finished_record(case, meter, tapes)
    except ValueError:
        # Check the source's own unwinding before fixture rollback can hide it.
        need(
            saved_state(case) == meter.saved,
            "caller failure cleanup before fixture teardown",
        )
        need(
            (bytes(case.program.tape.cells), bytes(case.fields.tape.cells)) == tapes,
            "caller failure preserves inputs",
        )
        raise
    finally:
        source.clear()
        case.program.tape.clear()
        case.fields.tape.clear()
        for value in case.counts:
            value.close()
        case.context.close()
        case.residues.rollback(set())
        case.indices.rollback(set())
