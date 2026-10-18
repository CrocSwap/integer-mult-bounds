"""Authenticated complete routes with an independent physical-I/O observer."""

import atexit
import hashlib
import json
import sys
from contextlib import ExitStack
from fractions import Fraction
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PREDECESSOR = ROOT / "research/selected-bit-fast-primitives"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    rows = json.loads((PACKAGE / "SOURCES.json").read_bytes())["files"]
    require(0 < len(rows) <= 64, "bounded source inventory")
    seen, data, total = set(), {}, 0
    for row in rows:
        if row["usage"] != "input":
            continue
        name = row["path"]
        require(
            name not in seen and not Path(name).is_absolute(), "unique relative input"
        )
        require(".." not in Path(name).parts, "contained input")
        seen.add(name)
        target = ROOT / name
        require(target.is_file() and not target.is_symlink(), "regular input: " + name)
        size = target.stat().st_size
        require(size <= 32 * 1024 * 1024, "bounded input size")
        total += size
        require(total <= 64 * 1024 * 1024, "bounded total source bytes")
        body = target.read_bytes()
        require(
            hashlib.sha256(body).hexdigest() == row["sha256"], "source hash: " + name
        )
        data[name] = body
    return data


def load_module(name, data):
    relative = "research/selected-bit-fast-primitives/" + name + ".py"
    require(relative in data, "declared executable source: " + name)
    path = ROOT / relative
    result = ModuleType(name)
    result.__file__ = str(path)
    sys.modules[name] = result
    # Complete authenticated modules, not edited ASTs or cached bytecode.
    exec(compile(data[relative], str(path), "exec"), result.__dict__)  # noqa: S102
    return result


def close():
    for name in ("source", "stage_sources"):
        temporary = getattr(sys.modules.get(name), "_temporary", None)
        if temporary is not None:
            temporary.cleanup()


def load():
    data = authenticate()
    names = ("stage_sources", "compile_routes", "kernels", "high_route", "stage")
    require(not any(name in sys.modules for name in names), "cold audit namespace")
    stage_sources = load_module("stage_sources", data)
    try:
        _source, retained, _data = stage_sources.activate()
    except BaseException:
        close()
        raise
    atexit.register(close)
    for name in ("compile_routes", "kernels", "high_route", "stage"):
        load_module(name, data)
    names = (
        "cardinal_counts",
        "directory",
        "low_codes",
        "macro_code",
        "ordinary",
        "physical_words",
        "records",
        "routes",
        "scratch_pool",
        "stream",
        "words",
    )
    modules = {name: __import__(name) for name in names}
    return SimpleNamespace(
        **modules,
        retained=retained,
        stage=sys.modules["stage"],
        registry=sys.modules["compile_routes"].Registry,
    )


class Trace:
    """Count actual Tape methods once, not their aliasing Word/Lease meters."""

    def __init__(self, runtime, native):
        self.runtime, self.native = runtime, native
        self.operations = 0

    def wrap(self, method):
        def counted(*args, **kwargs):
            self.operations += 1
            return method(*args, **kwargs)

        return counted

    def snapshot(self):
        parking = self.native.runtime.numerical
        extra = sum(
            counts[key]
            for counts in (parking.codec_counts, parking.machine.counts)
            for key in ("reads", "writes", "moves")
        )
        return self.operations + extra

    def installed(self):
        stack = ExitStack()
        tape = self.runtime.records.Tape
        for name in ("read", "write", "step"):
            stack.enter_context(
                patch.object(tape, name, self.wrap(getattr(tape, name)))
            )
        return stack


def native_fixture(runtime, q):
    return runtime.ordinary.Ordinary(
        q,
        SimpleNamespace(codes=SimpleNamespace(q=q)),
        SimpleNamespace(families=0),
        (runtime.macro_code.Code((("unreachable",),), 0),),
        capacity=64,
    )


def prepare(runtime, prefixes, q, width, fibre_value, inverse, pattern):
    require(type(prefixes) is int and 1 <= prefixes <= 17, "fixture prefix range")
    require(q in (3, 5) and type(q) is int, "fixture radix")
    require(type(width) is int and 1 <= width <= 3, "fixture width")
    require(type(fibre_value) is int and 1 <= fibre_value <= 3, "fixture fibre")
    require(
        type(inverse) is bool and type(pattern) is int and pattern in (0, 1),
        "fixture variant",
    )
    bits = q ** (4 * (width - 1)) * fibre_value
    require(prefixes * bits <= 100000, "fixture volume limit")
    codes = runtime.low_codes.LowCodes(q, 2, 1)
    word = (
        ("add", 0, 1, Fraction(1, 2)),
        ("scale", 1, 1, Fraction(-2)),
        ("swap", 0, 1, Fraction(1)),
    )
    if inverse:
        word = sys.modules["compile_routes"].inverse_word(word)
    chart = runtime.retained.replay(word, 2)
    registry = runtime.registry(2)
    registry.register(chart, word)
    route = runtime.routes.compile_route(((1, 0), (0, 1)), chart, codes)
    count = runtime.cardinal_counts.Count
    maximum = count.literal(q**width)
    bank = runtime.physical_words.PhysicalArena(64)
    bank.prepare(maximum)
    modulus = bank.load(maximum)
    ring = runtime.words.Ring(modulus)
    context = runtime.directory.Context(ring, codes)
    old_count, fibre = count.literal(prefixes), count.literal(fibre_value)
    source = runtime.records.Tape()
    initial = bytes(
        ((i * 13 ^ i // 3 ^ 5) & 1) ^ pattern for i in range(prefixes * bits)
    )
    for bit in initial:
        source.append(bit)
    source.rewind()
    native = native_fixture(runtime, q)
    adapter = runtime.stage.Adapter(native, registry, capacity=64)
    pool = runtime.scratch_pool.ScratchPool(q * q + 256)
    scope = runtime.stage.StagePool(pool, adapter)
    return SimpleNamespace(**locals())


def physical_tapes(state):
    native, machine = state.native, state.native.runtime
    tapes = [
        state.source,
        state.maximum.tape,
        state.context.highs.tape,
        state.old_count.tape,
        state.fibre.tape,
        native.output,
        machine.output,
    ]
    tapes.extend(
        (
            *state.pool.tapes,
            *native.pool.tapes,
            *machine.pool.tapes,
            *machine.roles.values(),
            *machine.handoff.values(),
        )
    )
    for bank in (
        state.bank,
        state.adapter.high_bank,
        *native.banks,
        machine.arena,
        machine.indices,
    ):
        tapes.extend(word.tape for word in (*bank.words, bank.template))
    return tuple({id(tape): tape for tape in tapes}.values())


def meters(tapes, trace):
    parking = trace.native.runtime.numerical
    return sum(
        meter.reads + meter.writes + meter.moves for meter in (t.meter for t in tapes)
    ) + sum(
        counts[key]
        for counts in (parking.codec_counts, parking.machine.counts)
        for key in ("reads", "writes", "moves")
    )


def endpoint(state, output):
    """Direct full q-adic matrix multiplication, independent of factor execution."""
    q, width, fibre = state.q, state.width, state.fibre_value
    high, modulus = q ** (width - 1), q**width
    lifted = [
        [int(x.numerator * pow(x.denominator, -1, modulus)) % modulus for x in row]
        for row in state.chart
    ]
    expected = bytearray(len(state.initial))
    for ordinal in range(high**4):
        digits, remaining = [0] * 4, ordinal
        for position in range(3, -1, -1):
            remaining, digits[position] = divmod(remaining, high)
        matrix = [
            [int(i == j) + q * digits[2 * i + j] for j in range(2)] for i in range(2)
        ]
        target = 0
        for i in range(2):
            for j in range(2):
                value = sum(matrix[i][k] * lifted[k][j] for k in range(2)) % modulus
                target = target * high + (value - state.route.target_low[i][j]) // q
        for prefix in range(state.prefixes):
            for suffix in range(fibre):
                origin = prefix * state.bits + ordinal * fibre + suffix
                destination = prefix * state.bits + target * fibre + suffix
                expected[destination] = state.initial[origin]
    require(
        bytes(output.physical.cells[1 : len(expected) + 1]) == expected,
        "affine endpoint",
    )
    require(
        all(
            bit == state.runtime.words.BLANK
            for bit in output.physical.cells[len(expected) + 1 :]
        ),
        "output extent",
    )
    require(
        bytes(state.source.cells[1 : len(expected) + 1]) == state.initial,
        "borrowed input",
    )
    require(state.source.head == output.head == 1, "canonical endpoint heads")


def borrowed_tapes(state):
    return (
        state.source,
        state.old_count.tape,
        state.fibre.tape,
        state.context.highs.tape,
        state.modulus.tape,
        state.ring.one.tape,
        state.context.cap.tape,
    )


def completed_boundary(state, output, originals):
    borrowed = borrowed_tapes(state)
    require(state.pool.live == {output.slot: output}, "only returned output is owned")
    require(
        tuple(bytes(tape.cells) for tape in borrowed) == originals,
        "all borrowed input and context bytes preserved",
    )
    require(all(tape.head == 1 for tape in borrowed), "all borrowed heads returned")
    require(
        not state.adapter.high_bank.live and not state.adapter.high_bank.initialized,
        "complete high-bank teardown",
    )
    require(
        state.native.closed and state.native.output.read() == state.runtime.words.BLANK,
        "completed and consumed native output",
    )
    endpoint(state, output)


def execute(state, prefix_probe=False):
    runtime, native = state.runtime, state.native
    trace, calls, cubes = Trace(runtime, native), [], []
    original_run = native.run

    def observed(*args, **kwargs):
        start = trace.snapshot()
        result = original_run(*args, **kwargs)
        calls.append(dict(traffic=trace.snapshot() - start, fitted=native.last_fitted))
        return result

    original_cube = state.adapter.route_cube

    def observed_cube(*args, **kwargs):
        if prefix_probe:
            # Deliberate C^2 cost mutant outside the cube invoice.
            for _ in range(state.prefixes):
                state.source.read()
        before = trace.snapshot()
        result = original_cube(*args, **kwargs)
        cubes.append(trace.snapshot() - before)
        return result

    tapes = physical_tapes(state)
    originals = tuple(bytes(tape.cells) for tape in borrowed_tapes(state))
    # StagePool rebinds routes.route_cube after every B1 return. Observe the
    # stable adapter method so later prefixes cannot silently escape the census.
    with (
        trace.installed(),
        patch.object(native, "run", observed),
        patch.object(state.adapter, "route_cube", observed_cube),
        state.scope.install(),
    ):
        # Entry deltas exclude native construction/initial marker erasure.
        start, raw = trace.snapshot(), meters(tapes, trace)
        output = runtime.routes.route_packet(
            state.source, state.route, state.context, state.old_count, state.fibre
        )
        traffic = trace.snapshot() - start
        require(traffic == meters(tapes, trace) - raw, "raw meter/observer agreement")
        try:
            # Oracle and ownership probes are outside the measured interval.
            completed_boundary(state, output, originals)
        finally:
            disposal_start = trace.snapshot()
            output.clear()
            disposal = trace.snapshot() - disposal_start
            require(disposal == 5 * len(state.initial) + 7, "exact output disposal")
            state.pool.empty()
    return traffic, disposal, calls, cubes


def cleanup(state):
    state.adapter.close()
    state.context.close()
    state.ring.close()
    state.bank.free(state.modulus)
    state.bank.erase_owned()
    for value in (state.maximum, state.old_count, state.fibre):
        value.close()
    state.source.clear()
    require(
        not state.bank.live and not state.adapter.high_bank.live,
        "closed numerical work",
    )


def run_case(
    runtime,
    prefixes,
    q=3,
    width=2,
    fibre_value=1,
    inverse=False,
    pattern=0,
    prefix_probe=False,
):
    state = prepare(runtime, prefixes, q, width, fibre_value, inverse, pattern)
    try:
        traffic, disposal, calls, cubes = execute(state, prefix_probe)
        require(len(calls) == state.adapter.calls["swaps"], "all reached B1 intervals")
        require(
            len(cubes) == state.adapter.calls["cubes"] == prefixes,
            "one observed cube per prefix",
        )
        require(
            all(row["fitted"] is False for row in calls),
            "declared elementary B1 fixtures",
        )
        return dict(
            prefixes=prefixes,
            q=q,
            width=width,
            fibre=fibre_value,
            inverse=inverse,
            pattern=pattern,
            cube_bits=state.bits,
            traffic=traffic,
            disposed_traffic=traffic + disposal,
            cube_traffic=sum(cubes),
            wrapper_traffic=traffic - sum(cubes),
            native_calls=len(calls),
            native_traffic=sum(row["traffic"] for row in calls),
            native_trace_sha256=hashlib.sha256(
                json.dumps(calls, sort_keys=True).encode()
            ).hexdigest(),
            pool_peak=state.pool.peak,
        )
    finally:
        cleanup(state)
