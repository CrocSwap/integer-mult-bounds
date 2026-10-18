"""Independent, authenticated pending-allocation witnesses for caller sites.

No primary or predecessor verifier is imported. The unchanged source loader is
itself SHA256-pinned before its authenticated-byte runtime is used. These are
finite component/trace witnesses, not full Boolean Consumer.apply executions.
Written all-domain accounting is in INDEPENDENT.md. Apache-2.0; prepared with
OpenAI Codex assistance as a separate storage-lifetimes audit.
"""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
from types import ModuleType, SimpleNamespace


ROOT = Path(__file__).resolve().parent
LOADER_SHA256 = "4c002dd32ee258ddb230e030c66a266792087c2be5c3b4532aa53370a2a972e9"


def require(condition, message):
    if not condition:
        raise ValueError(message)


@contextmanager
def runtime():
    path = ROOT / "predecessor/runtime.py"
    data = path.read_bytes()
    require(hashlib.sha256(data).hexdigest() == LOADER_SHA256,
            "independent source-loader hash")
    module = ModuleType("independent_authenticated_runtime")
    module.__file__ = str(path)
    exec(compile(data, str(path), "exec"), module.__dict__)
    with module.runtime() as source:
        yield source


def arena_type(words):
    class DemandArena(words.Arena):
        def __init__(self, bits):
            super().__init__(bits)
            self.baseline = None
            self.pending_peak = 0
            self.inventory_failures = []

        def start(self, allowance, baseline=None):
            self.baseline = len(self.live) if baseline is None else baseline
            self.pending_peak = len(self.live) - self.baseline
            self.inventory_failures = []
            self.capacity = self.baseline + allowance
            require(len(self.words) <= self.capacity, "warm entry fits literal quota")

        def zero(self):
            if self.baseline is not None:
                demand = len(self.live) + 1 - self.baseline
                self.pending_peak = max(self.pending_peak, demand)
                if not self.available and len(self.words) >= self.capacity:
                    self.inventory_failures.append(demand)
            # The literal unchanged guard raises; no artificial rejection seam.
            return super().zero()

    return DemandArena


def snapshot(arena):
    return {slot: (bytes(arena.words[slot].cells), arena.words[slot].head)
            for slot in arena.live}


def restored(arena, entry):
    require(snapshot(arena) == entry, "restored entry ownership, cells and heads")
    require(len(arena.available) == len(set(arena.available)), "unique free slots")
    require(set(arena.live).isdisjoint(arena.available), "partition disjointness")
    require(set(arena.live) | set(arena.available) == set(range(len(arena.words))),
            "complete slot partition")
    for slot in arena.available:
        word = arena.words[slot]
        require(word.head == 1 and all(bit == 4 for bit in word.cells[1:]),
                "released numerical content erased")


def expect_failure(arena, demand, operation):
    try:
        operation()
    except ValueError:
        require(arena.inventory_failures == [demand],
                "one literal inventory rejection at the expected pending request")
        return
    raise ValueError("undercharged literal quota was accepted")


def marginal(source, value):
    count = source.counts.Count.literal(value)
    out = count.marginal()
    count.close()
    return out


def tape(source, length):
    out = source.records.Tape()
    for k in range(length):
        out.append((k ^ (k >> 1)) & 1)
    out.rewind()
    return out


def ring_fixture(source, modulus):
    arena = arena_type(source.words)(modulus.bit_length() + 1)
    ring = source.words.Ring(arena.input(modulus))
    arena.input(0)  # A charged unrelated entry resident.
    return arena, ring


def directory_witness(source, undercharge=False):
    arena, ring = ring_fixture(source, 3)
    vocabulary = SimpleNamespace(q=3, dimension=64, bits=1, limit=2)
    context = source.directory.Context(ring, vocabulary)
    entry = snapshot(arena)
    arena.start(4095 if undercharge else 4096)
    if undercharge:
        expect_failure(arena, 4096, lambda: source.directory.Odometer(context))
    else:
        odometer = source.directory.Odometer(context)
        require(arena.pending_peak == 4096, "complete Odometer constructor demand")
        odometer.close()
        restored(arena, entry)
    return arena.pending_peak


def radix_witness(source, undercharge=False):
    arena, ring = ring_fixture(source, 27)
    entry = snapshot(arena)
    arena.start(5 if undercharge else 6)
    operation = lambda: sum(1 for _ in source.cardinality.radix_power(ring, 3))
    if undercharge:
        expect_failure(arena, 6, operation)
    else:
        require(operation() == 3, "all three literal radix divisions")
        require(arena.pending_peak == 6, "radix constructor/division demand")
        restored(arena, entry)
    return arena.pending_peak


def callback_witness(source, mode, undercharge=False):
    arena, ring = ring_fixture(source, 5)
    root = {"zero": 64, "unit": 4096, "half": 8192}[mode]
    indices = arena_type(source.words)(root.bit_length() + 1)
    indices.input(0)  # Charged unrelated index.
    events = [] if mode == "zero" else [(2, 0, 1, 0, 0, int(mode == "half"))]
    program = source.records.Program.fixture(indices, arena, root, 2, events, code_bits=1)
    high = tuple((0,) * 64 for _ in range(64))
    fields = source.records.Fields.fixture(indices, arena, [(0, high)] * (len(events) + 1), code_bits=1)
    spec = SimpleNamespace(code=0, good=False, template=SimpleNamespace(q=5, rank=1))
    expected = {"zero": 10, "unit": 14, "half": 15}[mode]
    entries = snapshot(arena), snapshot(indices)
    arena.start(12)
    indices.start(expected - int(undercharge))
    operation = lambda: source.controller.Callback(ring, indices, program, fields, {0: spec}, 0,
                                                  allow_fallback=True)
    if undercharge:
        expect_failure(indices, expected, operation)
        # These chosen failures occur inside the constructor's abort guard.
        restored(arena, entries[0])
        restored(indices, entries[1])
    else:
        callback = operation()
        require((arena.pending_peak, indices.pending_peak) == (12, expected),
                "literal validation-constructor peaks")
        callback.close()
        restored(arena, entries[0])
        restored(indices, entries[1])
    return [arena.pending_peak, indices.pending_peak]


def setup(source, plan, quota=64):
    arena, ring = ring_fixture(source, 3)
    indices = arena_type(source.words)(9)
    parent, depth = indices.input(127), indices.input(3)
    indices.input(0)
    entry = snapshot(indices)
    indices.start(quota)
    columns, fields = indices.literal(1), indices.literal(4)
    geometry = source.numeric.Geometry(plan, indices, columns, depth, 0, object())
    extents = [source.cardinal_counts.Count.literal(1) for _ in range(3)]
    layout = source.layout.Layout(geometry, parent, ring, 3, *extents)
    return arena, indices, geometry, layout, columns, fields, extents, entry


def setup_witness(source, undercharge=False):
    plan = source.plan.Plan(64, 1, True, ())
    if undercharge:
        # Keep the arena visible even if the constructor fails before returning.
        arena, ring = ring_fixture(source, 3)
        indices = arena_type(source.words)(9)
        parent, depth = indices.input(127), indices.input(3)
        indices.start(8)
        columns, fields = indices.literal(1), indices.literal(4)
        geometry = source.numeric.Geometry(plan, indices, columns, depth, 0, object())
        extents = [source.cardinal_counts.Count.literal(1) for _ in range(3)]
        expect_failure(indices, 9, lambda: source.layout.Layout(geometry, parent, ring, 3, *extents))
        return indices.pending_peak
    arena, indices, geometry, layout, columns, fields, extents, entry = setup(source, plan, 9)
    require(indices.pending_peak == 9, "Layout constructor transient")
    layout.close(); geometry.close(); indices.free_many(columns, fields)
    for extent in extents:
        extent.close()
    restored(indices, entry)
    return indices.pending_peak


def extents_witness(source, binary, undercharge=False):
    plan = source.plan.Plan(64, 1, True, ())
    arena, indices, geometry, layout, columns, fields, extents, _entry = setup(source, plan)
    first, second = indices.input(0), indices.input(127)
    entries = snapshot(arena), snapshot(indices)
    expected = 4 if binary else 3
    arena.start(6)
    indices.start(expected - int(undercharge))
    operation = lambda: layout.extents(first, second) if binary else layout.extents(first)
    if undercharge:
        expect_failure(indices, expected, operation)
    else:
        result = operation()
        require((arena.pending_peak, indices.pending_peak) == (6, expected),
                "Layout extents pending maxima")
        for value in result:
            value.close()
        restored(arena, entries[0]); restored(indices, entries[1])
    return [arena.pending_peak, indices.pending_peak]


def trace_witness(source, good, rank=1, undercharge=False):
    # Good commands come from the literal finite compiler. The fallback word is
    # a small control-path superset, not an asserted admitted normal form.
    if good:
        low = [[int(i == j and i < rank) for j in range(64)] for i in range(64)]
        plan = source.plan.compile_plan(low, rank, 3, True)
    else:
        commands = []
        for first, second in ((0, 1), (0, 64), (63, 64), (64, 127), (126, 127)):
            for kind in ("unit", "pair"):
                commands.append(source.plan.Command("child", first, second, source.plan.Reference(kind)))
        commands += [source.plan.Command("add", 127, 0, source.plan.Reference("shear")),
                     source.plan.Command("sign", 127, -1, source.plan.Reference("fixed"))]
        plan = source.plan.Plan(64, rank, False, tuple(commands))
    arena, indices, geometry, layout, columns, fields, extents, original_entry = setup(source, plan)
    engine_entry = snapshot(indices)
    expected = 18 if good else 19
    indices.start(expected - int(undercharge), baseline=len(original_entry))
    events = source.trace.execute(geometry)
    counts = {"enter": 0, "return": 0, "child_add": 0, "adapter_add": 0,
              "atom_swap": 0, "sign": 0}

    def consume():
        for event in events:
            if event.kind == "add":
                category = event.request.kind + "_add"
                if event.request.kind == "child":
                    require(len(indices.live) - len(original_entry) == expected,
                            "child callback-entry live census")
            else:
                category = event.kind
            counts[category] += 1
        events.close()

    if undercharge:
        expect_failure(indices, expected, consume)
    else:
        consume()
        require(indices.pending_peak == expected, "trace complete pending peak")
        require(counts["enter"] == counts["return"] > 0, "closed child boundaries")
        restored(indices, engine_entry)
        layout.close(); geometry.close(); indices.free_many(columns, fields)
        for extent in extents:
            extent.close()
        restored(indices, original_entry)
    return {"peak": indices.pending_peak, "events": counts}


def primitive_witness(source, kind, undercharge=False):
    modulus, q = (5, 5) if kind == "add" else (9, 3)
    arena, ring = ring_fixture(source, modulus)
    entry = snapshot(arena)
    extents = [marginal(source, 1) for _ in range(3 if kind != "sign" else 2)]
    source_tape = tape(source, modulus if kind == "sign" else modulus * modulus)
    arena.start(5 if undercharge else 6)
    if kind == "add":
        operation = lambda: source.stream.add_pass(source_tape, ring, *extents,
                                                  lambda: arena.literal(2))[0]
    elif kind == "swap":
        operation = lambda: source.bitstream.atom_swap(source_tape, ring, q, *extents)
    else:
        operation = lambda: source.bitstream.sign_address(source_tape, ring, q, *extents)
    if undercharge:
        expect_failure(arena, 6, operation)
    else:
        output = operation()
        require(arena.pending_peak == 6, "literal primitive pending peak")
        restored(arena, entry)
        output.clear(); source_tape.clear()
        for extent in extents:
            extent.close()
    return arena.pending_peak


def main():
    with runtime() as source:
        results = {
            "directory_constructor": directory_witness(source),
            "radix": radix_witness(source),
            "setup": setup_witness(source),
            "validation": {mode: callback_witness(source, mode) for mode in ("zero", "unit", "half")},
            "extents": {str(binary): extents_witness(source, binary) for binary in (False, True)},
            "good_traces": {str(rank): trace_witness(source, True, rank) for rank in (1, 21, 42)},
            "fallback_trace": trace_witness(source, False),
            "primitives": {kind: primitive_witness(source, kind) for kind in ("add", "swap", "sign")},
        }
        controls = {
            "directory": directory_witness(source, True),
            "radix": radix_witness(source, True),
            "setup": setup_witness(source, True),
            "validation": {mode: callback_witness(source, mode, True) for mode in ("zero", "unit", "half")},
            "extents": {str(binary): extents_witness(source, binary, True) for binary in (False, True)},
            "good_trace": trace_witness(source, True, 1, True)["peak"],
            "fallback_trace": trace_witness(source, False, undercharge=True)["peak"],
            "primitives": {kind: primitive_witness(source, kind, True) for kind in ("add", "swap", "sign")},
        }
    print(json.dumps({"status": "pass", "finite_witnesses": results,
                      "one_slot_short_literal_rejections": controls,
                      "limits": "component/trace witnesses; no full payload, coefficient replay, catalogue admission or kernel proof"},
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
