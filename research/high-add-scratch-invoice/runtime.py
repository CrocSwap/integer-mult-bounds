"""Authenticate and observe complete frozen modules, without source edits."""

import atexit
import hashlib
import json
import sys
from contextlib import ExitStack
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

from invoice import require

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def authenticate(rows=None):
    if rows is None:
        rows = json.loads((PACKAGE / "SOURCES.json").read_bytes())["files"]
    require(0 < len(rows) <= 64, "bounded input inventory")
    bodies = {}
    for row in rows:
        if row["usage"] != "input":
            continue
        name = row["path"]
        require(name not in bodies and not Path(name).is_absolute()
                and ".." not in Path(name).parts, "unique contained source")
        path = ROOT / name
        require(path.is_file() and not path.is_symlink(), "regular source: " + name)
        require(path.stat().st_size < 32 * 1024 * 1024, "bounded source file")
        body = path.read_bytes()
        require(hashlib.sha256(body).hexdigest() == row["sha256"], "source hash: " + name)
        bodies[name] = body
    require(sum(map(len, bodies.values())) < 64 * 1024 * 1024, "bounded input bytes")
    return bodies


def module(name, relative, data):
    result = ModuleType(name)
    result.__file__ = str(ROOT / relative)
    sys.modules[name] = result
    exec(compile(data[relative], result.__file__, "exec"), result.__dict__)
    return result


def close():
    for name in ("source", "stage_sources"):
        temporary = getattr(sys.modules.get(name), "_temporary", None)
        if temporary is not None:
            temporary.cleanup()


def load():
    data = authenticate()
    require("stage_sources" not in sys.modules, "cold source namespace")
    prefix = "research/selected-bit-fast-primitives/"
    stage = module("stage_sources", prefix + "stage_sources.py", data)
    try:
        stage.activate()
        kernels = module("kernels", prefix + "kernels.py", data)
        import physical_words
        import scratch_pool
        require(Path(scratch_pool.__file__).read_bytes() ==
                data["research/selected-bit-physical-caller/scratch_pool.py"],
                "actual retained pool bytes")
        require(Path(physical_words.__file__).read_bytes() ==
                data["research/physical-ordinary-interchange/physical_words.py"],
                "actual retained physical arena bytes")
    except BaseException:
        close()
        raise
    atexit.register(close)
    names = ("words", "records", "stream", "cardinality", "cardinal_counts")
    return SimpleNamespace(kernels=kernels, pool=scratch_pool, physical=physical_words,
                           **{name: sys.modules[name] for name in names})


class Traffic:
    """Raw physical methods counted once; nested arithmetic intervals are disjoint."""

    def __init__(self, rt):
        self.rt, self.total, self.arithmetic, self.depth = rt, 0, 0, 0
        self.intervals = {}

    def operation(self, method):
        def observed(*args, **kwargs):
            self.total += 1
            return method(*args, **kwargs)
        return observed

    def numerical(self, name, method):
        def observed(*args, **kwargs):
            outer, start = self.depth == 0, self.total
            self.depth += 1
            try:
                return method(*args, **kwargs)
            finally:
                self.depth -= 1
                if outer:
                    elapsed = self.total - start
                    self.arithmetic += elapsed
                    item = self.intervals.setdefault(name, [0, 0, 0])
                    item[0] += 1
                    item[1] += elapsed
                    item[2] = max(item[2], elapsed)
        return observed

    def installed(self):
        stack = ExitStack()
        for name in ("read", "write", "step"):
            cls = self.rt.records.Tape
            stack.enter_context(patch.object(cls, name, self.operation(getattr(cls, name))))
        targets = [(self.rt.kernels, "fixed_coefficient"),
                   (self.rt.words.Ring, "multiply")]
        targets += [(self.rt.words.Unsigned, n) for n in
                    ("compare", "subtract_exact", "increment_in_place")]
        targets += [(self.rt.words.Arena, n) for n in ("zero", "free", "free_many")]
        for owner, name in targets:
            stack.enter_context(patch.object(owner, name,
                                self.numerical(name, getattr(owner, name))))
        return stack


def encoded(tape):
    physical = getattr(tape, "physical", tape)
    return bytes(physical.cells), physical.head


def physical_total(tapes):
    unique = {id(tape): tape for tape in tapes}
    return sum(t.meter.reads + t.meter.writes + t.meter.moves for t in unique.values())


def prepare(rt, q, before, middle, suffix, coefficient, spare, occupied, pooled,
            numerical_capacity=8, basis=None, numerical_occupied=0):
    require(q <= 129 and before <= 4 and middle <= 4 and suffix <= 5, "fixture caps")
    require(before * middle * q * q * suffix <= 100000, "payload cap")
    require(coefficient in (-4, -2, -1, 1, 2, 4), "selected coefficient alphabet")
    bank = rt.physical.PhysicalArena(numerical_capacity)
    Count = rt.cardinal_counts.Count
    value = Count.literal(q)
    bank.prepare(value)
    modulus = bank.load(value)
    ring = rt.words.Ring(modulus)
    value.close()
    for _ in range(numerical_occupied):
        bank.literal(q - 1)
    extents = [Count.literal(v) for v in (before, middle, suffix)]
    pool = rt.pool.ScratchPool(spare + occupied)
    held = [pool.acquire() for _ in range(occupied)]
    require(not pooled or held, "pooled source already owned")
    source = held[0] if pooled else rt.records.Tape()
    for address in range(before * middle * q * q * suffix):
        value = (address * 11 ^ address // 3 ^ 5) & 1 if basis is None else int(address == basis)
        source.append(value)
    source.rewind()
    for lease in held[int(pooled):]:
        lease.append(1)
        lease.append(0)
        lease.rewind()
    tapes = [getattr(source, "physical", source), *pool.tapes, bank.template.tape]
    tapes += [word.tape for word in bank.words] + [v.tape for v in extents]
    return SimpleNamespace(bank=bank, modulus=modulus, ring=ring, extents=extents,
                           pool=pool, held=held, source=source, tapes=tapes)


def endpoint(fixture, output, q, before, middle, suffix, coefficient):
    original = encoded(fixture.source)[0]
    expected = bytearray(before * q * middle * q * suffix)
    for address in range(len(expected)):
        rest, tail = divmod(address, suffix)
        rest, y = divmod(rest, q)
        rest, gap = divmod(rest, middle)
        prefix, x = divmod(rest, q)
        target = ((((prefix * q + x) * middle + gap) * q
                   + (y + coefficient * x) % q) * suffix + tail)
        expected[target] = original[address + 1]
    actual = encoded(output)[0]
    require(actual[1:len(expected) + 1] == expected, "complete modular ADD endpoint")
    require(all(v == 4 for v in actual[len(expected) + 1:]), "no extra output body")
    require(fixture.source.head == output.head == 1, "canonical endpoint heads")


def dispose(fixture, output=None):
    if output is not None:
        output.clear()
    # Failure controls clean their fixture explicitly; no source exception theorem.
    for lease in list(fixture.pool.live.values()):
        lease.clear()
    fixture.pool.empty()
    if fixture.source not in fixture.held:
        fixture.source.clear()
    for count in fixture.extents:
        count.close()
    fixture.bank.rollback(set())
    fixture.bank.erase_owned()
