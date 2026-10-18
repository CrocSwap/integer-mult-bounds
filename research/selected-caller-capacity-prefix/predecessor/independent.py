"""Independent source-trace census; no import of the primary verifier.

This finite checker authenticates all exported source, executes the original
trace generator, and compares it with a separate integer event oracle. It does
not execute coefficient callbacks or the enormous selected Boolean payload.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PIN = "69ee10977b78aacd151042b8be962363e2690a6a019e8e93bedd4b130daa853a"
ORDER = ("words records matrices controller forms plan numeric trace stream "
         "cardinality counts cardinal_counts bitstream stream_runner packet "
         "layout directory packet_engine consumer").split()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate_and_load():
    manifest = (ROOT / "evidence/PR2801-SNAPSHOT.json").read_bytes()
    require(hashlib.sha256(manifest).hexdigest() == PIN, "manifest identity")
    records = json.loads(manifest)
    require(records["head"] == "a53fdf4bcbe33c6732f0bec1badc8c023380f9d1",
            "scientific runtime head")
    authenticated = {}
    for entry in records["files"]:
        source = (ROOT / entry["path"]).read_bytes()
        require(hashlib.sha256(source).hexdigest() == entry["sha256"],
                "source SHA256: " + entry["path"])
        blob = b"blob " + str(len(source)).encode("ascii") + b"\0" + source
        require(hashlib.sha1(blob).hexdigest() == entry["git_blob"],
                "source Git blob: " + entry["path"])
        authenticated[entry["path"]] = source
    modules = {}
    for name in ORDER:
        require(name not in sys.modules, "isolated source module: " + name)
        module = types.ModuleType(name)
        module.__file__ = str(ROOT / "vendor" / (name + ".py"))
        sys.modules[name] = module
        source = authenticated["vendor/" + name + ".py"]
        exec(compile(source, module.__file__, "exec"), module.__dict__)  # noqa: S102
        modules[name] = module
    return modules


def snapshots(arena):
    return {slot: (bytes(arena.words[slot].cells), arena.words[slot].head)
            for slot in arena.live}


def restored(arena, saved):
    require(snapshots(arena) == saved, "entry numerical residents restored")
    for word in arena.words:
        if word.slot not in arena.live:
            require(word.head == 1 and all(x == 4 for x in word.cells[1:]),
                    "freed numerical content erased")


def encode_event(event):
    first = event.first.inspect()
    second = None if event.second is None else event.second.inspect()
    if event.kind in ("enter", "return"):
        return (event.kind, first, second, event.width.inspect(),
                event.depth.inspect(), event.child_kind, event.field,
                event.reverse, event.half)
    if event.request is None:
        return event.kind, first, second
    request = event.request
    return (event.kind, first, second, request.kind, request.coordinate.inspect(),
            request.child_kind, request.field, request.reverse,
            request.negative_inverse, request.half)


def child_oracle(first, second, width, kind, field=0, reverse=False,
                 fallback=False):
    boundary = (first, second, width, 4, kind, field, reverse, False)
    yield ("enter", *boundary), 12 + fallback
    for coordinate in range(width):
        left, right = first + coordinate, second + width - 1 - coordinate
        for stage in range(8):
            if stage in (0, 2, 4, 6):
                yield ("atom_swap", left, right), 17 + fallback
            elif stage == 7:
                yield ("sign", right, None), 16 + fallback
            else:
                event = ("add", right, left, "child", coordinate, kind,
                         field, reverse, stage == 3, False)
                yield event, 18 + fallback
    yield ("return", *boundary), 12 + fallback


def fallback_oracle(commands):
    for command in commands:
        if command.kind == "child":
            kind = command.reference.kind
            field = command.target if kind == "pair" else 0
            reverse = command.target >= 64 if kind == "pair" else False
            yield from child_oracle(command.target, command.source, 1, kind,
                                    field, reverse, fallback=True)
        elif command.kind == "sign":
            yield ("sign", command.target, None), 10
        else:
            event = ("add", command.target, command.source, "adapter", 0,
                     "", 0, False, False, False)
            yield event, 12


def fixture(modules, plan):
    words, numeric, layout = (modules[name] for name in ("words", "numeric", "layout"))
    indices, residues = words.Arena(9, 64), words.Arena(3, 64)
    modulus = residues.literal(3)
    ring = words.Ring(modulus)
    parent, depth = indices.literal(127), indices.literal(3)
    baseline = snapshots(indices)
    columns, fields = indices.literal(1), indices.literal(4)
    geometry = numeric.Geometry(plan, indices, columns, depth, 0, object())
    count = modules["cardinal_counts"].Count.literal(1)
    physical = layout.Layout(geometry, parent, ring, 3, count, count, count)
    persistent = snapshots(indices)
    require(len(persistent) - len(baseline) == 8, "eight caller index residents")
    require(indices.meter.peak_live - len(baseline) == 9, "layout setup transient peak")
    indices.meter.peak_live = len(indices.live)
    return indices, residues, ring, baseline, persistent, geometry, physical, fields, count


def dispose(state):
    indices, residues, ring, baseline, _, geometry, physical, fields, count = state
    physical.close()
    geometry.close()
    indices.free_many(geometry.columns, fields)
    restored(indices, baseline)
    count.close()
    ring.close()
    residues.free(ring.modulus)
    require(not residues.live, "residue fixture cleanup")


def check_trace(modules, plan, oracle, charge=None):
    state = fixture(modules, plan)
    indices, residues, _, baseline, persistent, geometry = state[:6]
    residue_saved = snapshots(residues)
    trace = modules["trace"].execute(geometry)
    count, observed = 0, set()
    try:
        for actual, expected in itertools.zip_longest(trace, oracle):
            require(actual is not None and expected is not None, "exact event count")
            encoded, excess = expected
            require(encode_event(actual) == encoded, "independent integer event semantics")
            live = len(indices.live) - len(baseline)
            require(live == excess, "exact suspended caller index census")
            require(charge is None or live <= charge, "semantic undercharge rejected")
            for slot, data in persistent.items():
                word = indices.words[slot]
                require((bytes(word.cells), word.head) == data, "borrowed caller restored")
            require(snapshots(residues) == residue_saved, "trace allocates no residues")
            count += 1
            observed.add((actual.kind, live))
    finally:
        trace.close()
        restored(indices, persistent)
        peak = indices.meter.peak_live - len(baseline)
        dispose(state)
    return count, peak, sorted(observed)


def expect_failure(operation, message):
    try:
        operation()
    except ValueError as error:
        require(message in str(error), "expected semantic defect")
        return
    raise ValueError("undetected semantic defect: " + message)


def restoration_controls(modules, plan):
    state = fixture(modules, plan)
    indices, _, _, _, persistent, geometry = state[:6]
    trace = modules["trace"].execute(geometry)
    next(trace)
    expect_failure(lambda: restored(indices, persistent), "entry numerical residents")
    trace.close()
    restored(indices, persistent)
    word = indices.words[next(iter(persistent))]
    original = word.cells[1]
    word.cells[1] ^= 1
    expect_failure(lambda: restored(indices, persistent), "entry numerical residents")
    word.cells[1] = original
    word.head = 2
    expect_failure(lambda: restored(indices, persistent), "entry numerical residents")
    word.head = 1
    restored(indices, persistent)
    dispose(state)


def phase_ledger():
    phases = {
        "directory": (4096, 0),
        "caller setup": (0, 9),
        "initial frame validation": (12, 8 + 15),
        "fibre construction": (6, 8),
        "trace construction and suspension": (0, 19),
        "child ADD extents": (6, 19 + 4),
        "child atom swap extents": (6, 18 + 4),
        "child sign extents": (6, 17 + 3),
        "non-ADD execution": (6, 18),
        "child ADD traversal": (1 + 1 + 4, 19),
        "good child callback": (20494, 18 + 22),
        "fallback child callback": (20494, 19 + 22),
        "adapter whole action": (37672, 34),
    }
    rectangles = ((37672, 34), (20494, 41))
    for phase, point in phases.items():
        require(any(all(x <= y for x, y in zip(point, bound, strict=True)) for bound in rectangles),
                "weighted envelope: " + phase)
    return phases


def main():
    modules = authenticate_and_load()
    model = modules["plan"]
    good_events, good_peak = 0, 0
    for rank in range(1, 43):
        plan = model.Plan(64, rank, True, ())
        oracle = child_oracle(0, 128 - rank, rank, "good")
        count, peak, _ = check_trace(modules, plan, oracle)
        good_events += count
        good_peak = max(good_peak, peak)
    commands = []
    for kind in ("unit", "pair"):
        for first in range(127):
            for second in range(first + 1, 128):
                commands.append(model.Command("child", first, second, model.Reference(kind)))
    for target in range(1, 128):
        for source in range(target):
            commands.append(model.Command("add", target, source, model.Reference("shear")))
    commands.extend(model.Command("sign", field, -1, model.Reference("fixed"))
                    for field in range(128))
    fallback = model.Plan(64, 1, False, tuple(commands))
    count, peak, observed = check_trace(modules, fallback, fallback_oracle(commands))
    require(good_events == 7308 and count == 170816, "complete finite label coverage")
    require(good_peak == 18 and peak == 19, "including pre-yield allocation peaks")
    single = model.Plan(64, 1, False, (commands[0],))
    expect_failure(lambda: check_trace(modules, single, fallback_oracle(single.commands), 18),
                   "semantic undercharge")
    restoration_controls(modules, single)
    print(json.dumps({"scientific_runtime": "a53fdf4bcbe33c6732f0bec1badc8c023380f9d1",
                      "good_ranks": [1, 42], "good_events": good_events,
                      "good_peak_indices": good_peak, "fallback_events": count,
                      "fallback_peak_indices": peak, "fallback_observations": observed,
                      "controls": ["undercharge", "missing_close", "borrowed_bytes", "borrowed_head"],
                      "conditional_phase_ledger": phase_ledger()}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
