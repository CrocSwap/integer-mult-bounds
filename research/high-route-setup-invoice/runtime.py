# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 thakrarsagar. Developed with substantial OpenAI Codex assistance.
"""Authenticated observation of unchanged PR2915 complete cube execution.

The retained PR2982 observer supplies source loading, physical meters, fixtures
and the independent q-adic endpoint oracle. Its broad authentication callback
is replaced only while loading, by this package's already checked byte closure.
No executed high-route, kernel, adapter or nested machine code is rewritten.
"""

from contextlib import ExitStack
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REFERENCE = "research/high-route-prefix-cost/runtime.py"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(root=ROOT):
    data = {}
    for pin in json.loads((HERE / "SOURCES.json").read_bytes())["files"]:
        if pin["usage"] != "input":
            continue
        name = pin["path"]
        require(not Path(name).is_absolute() and ".." not in Path(name).parts,
                "relative source path")
        body = (Path(root) / name).read_bytes()
        require(hashlib.sha256(body).hexdigest() == pin["sha256"], "source hash: " + name)
        data[name] = body
    return data


def load():
    data = authenticate()
    reference = ModuleType("high_route_prefix_reference")
    reference.__file__ = str(ROOT / REFERENCE)
    exec(compile(data[REFERENCE], reference.__file__, "exec"), reference.__dict__)
    try:
        with patch.object(reference, "authenticate", return_value=data):
            modules = reference.load()
    except BaseException:
        reference.close()
        raise
    return SimpleNamespace(reference=reference, modules=modules)


def close(loaded):
    loaded.reference.close()


def prepare(loaded, *, kind="ordered", q=3, width=2, fibre=1,
            capacity=64, pattern=0):
    require(kind in ("identity", "ordered", "reversed", "mixed", "negate", "scale", "half"),
            "fixture word kind")
    require(type(capacity) is int and 32 <= capacity <= 80, "fixture bank capacity")
    ref, rt = loaded.reference, loaded.modules
    state = ref.prepare(rt, 1, q, width, fibre, False, pattern)
    state.loaded = loaded
    state.parameters = dict(kind=kind, q=q, width=width, fibre=fibre,
                            capacity=capacity, pattern=pattern)
    words = {
        "identity": (),
        "ordered": (("add", 1, 0, Fraction(1)),),
        "reversed": (("add", 0, 1, Fraction(1)),),
        "mixed": (("add", 0, 1, Fraction(1, 2)),
                  ("scale", 1, 1, Fraction(-2)), ("swap", 0, 1, Fraction(1))),
        "negate": (("scale", 1, 1, Fraction(-1)),),
        "scale": (("scale", 1, 1, Fraction(-2)),),
        "half": (("scale", 1, 1, Fraction(1, 2)),),
    }
    state.word = words[kind]
    state.chart = rt.retained.replay(state.word, 2)
    registry = rt.registry(2)
    registry.register(state.chart, state.word)
    state.adapter.registry = registry
    state.route = rt.routes.compile_route(((1, 0), (0, 1)), state.chart, state.codes)
    if capacity != 64:
        require(not state.adapter.high_bank.live and not state.adapter.high_bank.initialized,
                "replace only an erased fixture bank")
        state.adapter.high_bank = rt.physical_words.PhysicalArena(capacity)
        state.adapter.high_bank.erase_owned()
    return state


def execute(state):
    """Measure one full cube and its disposal, with disjoint charged tolls."""
    ref, rt = state.loaded.reference, state.runtime
    high = sys.modules["high_route"]
    kernels = sys.modules["kernels"]
    count = rt.cardinal_counts.Count
    trace = ref.Trace(rt, state.native)
    tolls, natives, extents, clears, cuts = [], [], [], [], []
    extent_owners, payloads = {}, {}
    depth = 0
    first = True

    def payload_cut(label, result=None):
        if result is not None:
            payloads[id(result)] = result
        active = sum(value.active for value in payloads.values())
        cuts.append(dict(at=label, owned_payload_outputs=active))

    def factory():
        nonlocal first
        result = state.scope.acquire()
        if first:
            payload_cut("initial-copy", result)
            first = False
        return result

    def toll(name, original):
        def observed(*args, **kwargs):
            nonlocal depth
            source = args[0]
            source_tape = getattr(source, "physical", source)
            original_bytes = bytes(source_tape.cells)
            require(source.head == 1, "callee borrowed input enters at origin")
            before = trace.snapshot()
            depth += 1
            try:
                result = original(*args, **kwargs)
            finally:
                depth -= 1
            cost = trace.snapshot() - before
            require(result is not source and result.physical is not source_tape,
                    "distinct owned callee output")
            require(source.head == result.head == 1 and
                    bytes(source_tape.cells) == original_bytes,
                    "callee preserves borrowed input and returns both heads")
            cells = result.physical.cells
            require(all(symbol in (rt.words.ZERO, rt.words.ONE)
                        for symbol in cells[1:state.bits + 1]) and
                    len(cells) >= state.bits + 1 and
                    all(symbol == rt.words.BLANK for symbol in cells[state.bits + 1:]),
                    "callee returns a complete dense cube")
            tolls.append(dict(kind=name, traffic=cost))
            payload_cut(name + "-return", result)
            return result
        return observed

    original_native = state.native.run

    def native(*args, **kwargs):
        before = trace.snapshot()
        result = original_native(*args, **kwargs)
        natives.append(dict(traffic=trace.snapshot() - before, fitted=state.native.last_fitted))
        return result

    original_extents = high.extents

    def extent(*args, **kwargs):
        before = trace.snapshot()
        result = original_extents(*args, **kwargs)
        first_index = args[3]
        second_index = args[4] if len(args) > 4 else kwargs.get("second")
        row = dict(first=first_index, second=second_index,
                   create=trace.snapshot() - before, close=0)
        extents.append(row)
        for value in result:
            extent_owners[id(value)] = (value, row)
        return result

    original_close = count.close

    def count_close(value):
        before = trace.snapshot()
        result = original_close(value)
        if id(value) in extent_owners:
            extent_owners[id(value)][1]["close"] += trace.snapshot() - before
        return result

    original_clear = rt.scratch_pool.Lease.clear

    def clear(value):
        observed = id(value) in payloads and value.active and depth == 0
        before = trace.snapshot()
        result = original_clear(value)
        if observed:
            clears.append(trace.snapshot() - before)
        return result

    originals = tuple(bytes(tape.cells) for tape in ref.borrowed_tapes(state))
    tapes = ref.physical_tapes(state)
    operations = state.adapter.registry.compile(state.route)
    with ExitStack() as stack:
        stack.enter_context(trace.installed())
        stack.enter_context(patch.object(state.native, "run", native))
        stack.enter_context(patch.object(state.adapter, "swap", toll("swap", state.adapter.swap)))
        stack.enter_context(patch.object(high, "extents", extent))
        stack.enter_context(patch.object(count, "close", count_close))
        stack.enter_context(patch.object(rt.scratch_pool.Lease, "clear", clear))
        for name in ("added", "doubled", "negated", "translated"):
            stack.enter_context(patch.object(kernels, name, toll(name, getattr(kernels, name))))
        stack.enter_context(state.scope.install())
        before, raw = trace.snapshot(), ref.meters(tapes, trace)
        output = high.execute(state.source, state.route, state.context, state.fibre,
                              state.adapter, factory)
        traffic = trace.snapshot() - before
        require(traffic == ref.meters(tapes, trace) - raw, "raw meter/observer agreement")
        measured_clears = list(clears)
        try:
            ref.completed_boundary(state, output, originals)
        finally:
            before_dispose = trace.snapshot()
            output.clear()
            disposal = trace.snapshot() - before_dispose
            state.pool.empty()
    toll_total = sum(row["traffic"] for row in tolls)
    return dict(
        parameters=state.parameters,
        dimension=state.route.dimension,
        high_modulus=state.q ** (state.width - 1),
        input_digits=(state.q ** state.width).bit_length() + 1,
        volume=state.bits,
        operations=[list(operation) for operation in operations],
        traffic=traffic,
        setup_traffic=traffic - toll_total,
        tolls=tolls,
        native_intervals=natives,
        extents=extents,
        intermediate_clears=measured_clears,
        disposal=disposal,
        output_payload_peak=max(row["owned_payload_outputs"] for row in cuts),
        output_payload_cuts=cuts,
        boundary="complete endpoint, borrowed bytes/heads, high-bank erasure, owned return",
    )


def cleanup(state):
    # Harness cleanup also handles deliberately broken test executions. These
    # operations are never included in a successful source invoice.
    for lease in list(state.pool.live.values()):
        lease.clear()
    state.loaded.reference.cleanup(state)


def run_case(loaded, **parameters):
    state = prepare(loaded, **parameters)
    try:
        return execute(state)
    finally:
        cleanup(state)
