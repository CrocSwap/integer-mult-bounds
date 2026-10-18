"""Run the authenticated complete PR2915 loader and actual scratch installer."""

import atexit
import hashlib
import json
import sys
import types
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    rows = json.loads((PACKAGE / "SOURCES.json").read_bytes())["files"]
    require(0 < len(rows) <= 64, "bounded source inventory")
    data = {}
    for row in rows:
        if row["usage"] != "input":
            continue
        path = row["path"]
        require(path not in data and not Path(path).is_absolute(), "relative source")
        require(".." not in Path(path).parts, "contained source")
        target = ROOT / path
        require(target.stat().st_size <= 32 * 1024 * 1024, "source size limit")
        body = target.read_bytes()
        require(hashlib.sha256(body).hexdigest() == row["sha256"], "source: " + path)
        data[path] = body
    return data


def module(name, path, body):
    result = types.ModuleType(name)
    result.__file__ = str(path)
    sys.modules[name] = result
    # Authenticated complete modules, not rewritten function nodes.
    exec(compile(body, str(path), "exec"), result.__dict__)  # noqa: S102
    return result


def load():
    data = authenticate()
    require("stage_sources" not in sys.modules, "cold runtime namespace")
    path = "research/selected-bit-fast-primitives/stage_sources.py"
    stage = module("stage_sources", ROOT / path, data[path])
    stage.activate()
    path = "research/selected-bit-fast-primitives/kernels.py"
    kernels = module("kernels", ROOT / path, data[path])
    import scratch_pool

    expected = data["research/selected-bit-physical-caller/scratch_pool.py"]
    require(Path(scratch_pool.__file__).read_bytes() == expected, "actual pool bytes")
    path = "research/high-scaling-total-traffic/traffic.py"
    invoice = module("scaling_invoice", ROOT / path, data[path])
    atexit.register(close)
    return types.SimpleNamespace(
        kernels=kernels,
        pool=scratch_pool,
        words=sys.modules["words"],
        records=sys.modules["records"],
        count=sys.modules["cardinal_counts"].Count,
        invoice=invoice,
    )


def close():
    """Explicitly release both unchanged loaders' temporary source exports."""
    for name in ("source", "stage_sources"):
        owner = sys.modules.get(name)
        temporary = getattr(owner, "_temporary", None)
        if temporary is not None:
            temporary.cleanup()


def total(arena, pool, borrowed):
    """Count physical objects once; Lease.meter is an aliasing observer."""
    tapes = {id(tape): tape for tape in (*pool.tapes, *borrowed)}
    meters = [arena.meter, *(tape.meter for tape in tapes.values())]
    return sum(m.reads + m.writes + m.moves for m in meters)


def prepare(runtime, q, b, s, spare, occupied, pooled_source):
    require(type(q) is int and 3 <= q <= 129 and q % 2 == 1, "fixture modulus")
    require(all(type(n) is int and 1 <= n <= 8 for n in (b, s)), "fixture extents")
    require(q * b * s <= 10000, "fixture volume")
    require(type(spare) is int and 1 <= spare <= 10, "fixture spare roles")
    require(type(occupied) is int and 0 <= occupied <= 4, "fixture occupied roles")
    require(not pooled_source or occupied > 0, "pooled source owns an entry role")
    arena = runtime.words.Arena(q.bit_length() + 1, capacity=8)
    modulus = arena.input(q)
    ring = runtime.words.Ring(modulus)
    before, suffix = runtime.count.literal(b), runtime.count.literal(s)
    pool = runtime.pool.ScratchPool(spare + occupied)
    held = [pool.acquire() for _ in range(occupied)]
    source = held[0] if pooled_source else runtime.records.Tape()
    for address in range(q * b * s):
        source.append((address * 11 ^ address // 3 ^ 5) & 1)
    source.rewind()
    return arena, modulus, ring, before, suffix, pool, held, source


def endpoint(source, output, q, b, s, inverse):
    original = source.physical if hasattr(source, "physical") else source
    expected = bytearray(q * b * s)
    factor = pow(2, -1, q) if inverse else 2
    for address in range(len(expected)):
        block, tail = divmod(address, s)
        prefix, value = divmod(block, q)
        target = (prefix * q + factor * value % q) * s + tail
        expected[target] = original.cells[address + 1]
    require(bytes(output.physical.cells[1 : len(expected) + 1]) == expected, "endpoint")
    require(source.head == output.head == 1, "rewound endpoint")


def checked_row(runtime, pool, q, b, s, inverse, occupied, measured, entry_allocations):
    logical = sum(runtime.invoice.invoice(q, b, s).values())
    acquisitions = pool.allocations - entry_allocations
    require(acquisitions == runtime.invoice.allocations(q, b, s), "acquisition census")
    require(measured == logical + acquisitions, "physical invoice")
    require(pool.peak == occupied + 7 + (s > 1), "exact free inventory")
    require(measured < 530 * q * b * s, "uniform physical tape bound")
    return {
        "q": q,
        "b": b,
        "s": s,
        "inverse": inverse,
        "occupied": occupied,
        "traffic": measured,
        "logical": logical,
        "acquisitions": acquisitions,
        "peak": pool.peak,
    }


def run(runtime, q, b, s, inverse=False, spare=None, occupied=0, pooled_source=False):
    spare = 7 + (s > 1) if spare is None else spare
    state = prepare(runtime, q, b, s, spare, occupied, pooled_source)
    arena, modulus, ring, before, suffix, pool, held, source = state
    physical_source = source.physical if pooled_source else source
    borrowed = [before.tape, suffix.tape, physical_source]
    snapshots = [bytes(t.cells) for t in (*borrowed, modulus)]
    entry_live, entry_allocations = dict(pool.live), pool.allocations
    started = total(arena, pool, borrowed)
    with pool.install():
        output = runtime.kernels.doubled(
            source, ring, before, suffix, pool.acquire, inverse
        )
        measured = total(arena, pool, borrowed) - started
        require(
            [bytes(t.cells) for t in (*borrowed, modulus)] == snapshots,
            "borrowed bytes",
        )
        require(all(t.head == 1 for t in (*borrowed, modulus)), "borrowed heads")
        require(
            pool.live == {**entry_live, output.slot: output}, "only output retained"
        )
        require(arena.live == {modulus.slot, ring.one.slot}, "numerical residents")
        endpoint(source, output, q, b, s, inverse)
        row = checked_row(
            runtime, pool, q, b, s, inverse, occupied, measured, entry_allocations
        )
        row["pooled_source"] = pooled_source
        output.clear()
        require(pool.live == entry_live, "entry lease owners restored")
    for lease in held:
        lease.clear()
    pool.empty()
    source.clear()
    before.close()
    suffix.close()
    ring.close()
    arena.free(modulus)
    require(not arena.live, "fixture numerical cleanup")
    return row
