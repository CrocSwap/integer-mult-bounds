#!/usr/bin/env python3
"""Replay the same-cut count/counter envelope on authenticated native ADD."""

import argparse
import ast
import hashlib
import itertools
import json
import sys
import types
import weakref
from contextlib import contextmanager
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[1]
SOURCE = "research/selected-layout-numerical-lifetime/vendor/"
MANIFEST_SHA256 = "201b041ceeab3bbede9aacb951f2dcfe4b1f95d7f9786b29519641a84ce698dd"
MODULES = (
    "words",
    "records",
    "stream",
    "cardinality",
    "counts",
    "cardinal_counts",
    "layout",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(repo=REPO):
    raw = (PACKAGE / "SOURCES.json").read_bytes()
    require(hashlib.sha256(raw).hexdigest() == MANIFEST_SHA256, "manifest identity")
    entries = [row for row in json.loads(raw)["files"] if row["usage"] == "input"]
    expected = {
        SOURCE + name + ".py" for name in (*MODULES, "numeric", "stream_runner")
    }
    expected.add(SOURCE + "NOTICE.md")
    require(len(entries) == len(expected), "unique source inventory")
    require({row["path"] for row in entries} == expected, "complete source inventory")
    data = {}
    for row in entries:
        content = (repo / row["path"]).read_bytes()
        require(hashlib.sha256(content).hexdigest() == row["sha256"], "source hash")
        blob = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content)
        require(blob.hexdigest() == row["git_blob"], "source Git blob")
        data[Path(row["path"]).stem] = content
    return data


def extract(data, name, kind, scope):
    nodes = [
        node
        for node in ast.parse(data).body
        if isinstance(node, kind) and node.name == name
    ]
    require(len(nodes) == 1, "one authenticated source definition")
    exec(
        compile(ast.Module(body=nodes, type_ignores=[]), "native/" + name, "exec"),
        scope,
    )
    return scope[name]


@contextmanager
def source_modules(repo=REPO):
    data = authenticate(repo)
    absent = object()
    previous = {name: sys.modules.get(name, absent) for name in MODULES}
    modules = {}
    try:
        for name in MODULES:
            module = types.ModuleType(name)
            module.__file__ = str(repo / (SOURCE + name + ".py"))
            sys.modules[name] = module
            exec(compile(data[name], module.__file__, "exec"), module.__dict__)
            modules[name] = module
        scope = {"Unsigned": modules["words"].Unsigned, "need": require}
        modules["Geometry"] = extract(data["numeric"], "Geometry", ast.ClassDef, scope)
        scope = {"need": require, "add_pass": modules["stream"].add_pass}
        modules["action"] = extract(
            data["stream_runner"], "action", ast.FunctionDef, scope
        )
        yield types.SimpleNamespace(**modules)
    finally:
        for name, old in previous.items():
            if old is absent:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = old


class Census:
    """Weak observation cannot extend a source tape's lifetime."""

    def __init__(self):
        self.roots = weakref.WeakValueDictionary()
        self.base = set()
        self.base_lengths = {}
        self.phase = "setup"
        self.peaks = {}
        self.peak = self.samples = 0
        self.limit = None

    def observe(self):
        require(len(self.roots) <= 32, "bounded tape inventory")
        total = 0
        for identity, tape in self.roots.items():
            require(len(tape.cells) <= 2048, "bounded tape extent")
            if identity not in self.base:
                total += len(tape.cells)
            else:
                require(
                    len(tape.cells) == self.base_lengths[identity],
                    "unchanged entry backing",
                )
        self.peak = max(self.peak, total)
        self.peaks[self.phase] = max(self.peaks.get(self.phase, 0), total)
        self.samples += 1
        require(self.samples <= 2_000_000, "bounded sample count")
        require(self.limit is None or total <= self.limit, "count backing quota")

    def start(self, limit=None):
        self.base = set(self.roots)
        self.base_lengths = {
            identity: len(tape.cells) for identity, tape in self.roots.items()
        }
        self.phase = "preparation"
        self.peaks = {}
        self.peak = self.samples = 0
        self.limit = limit

    def tape_type(self, original):
        census = self

        class Observed(original):
            def __init__(self):
                super().__init__()
                census.roots[id(self)] = self
                census.observe()

            def write(self, symbol):
                super().write(symbol)
                census.observe()

        return Observed


@contextmanager
def counted(m):
    census = Census()
    owners = (m.cardinality, m.counts, m.stream)
    originals = [module.Tape for module in owners]
    old_extents = m.layout.Layout.extents

    def extents(layout, *positions):
        result = old_extents(layout, *positions)
        census.observe()
        census.phase = "native"
        return result

    try:
        for module, original in zip(owners, originals, strict=True):
            module.Tape = census.tape_type(original)
        m.layout.Layout.extents = extents
        yield census
    finally:
        m.layout.Layout.extents = old_extents
        for module, original in zip(owners, originals, strict=True):
            module.Tape = original


def extent_values(modulus, n, spectators, first, last):
    before, gap, suffix = spectators
    return [
        before * modulus**first * (gap if first >= n else 1),
        modulus ** (last - first - 1) * (gap if first < n <= last else 1),
        suffix * modulus ** (2 * n - last - 1) * (gap if last < n else 1),
    ]


def envelope(extents, modulus, index_bits, callback=0):
    widths = [value.bit_length() for value in extents]
    ss, ww = sum(width + 2 for width in widths), max(widths)
    returned = sum(width + 3 for width in widths)
    pp, mm, suffix = (width + 3 for width in widths)
    rr = modulus.bit_length() + 3
    copy = rr + (2 * suffix if extents[2] > 1 else 0)
    counters = pp + rr + mm + max(mm, copy)
    preparation = ss + max(index_bits + 2, 3 * ww + 9)
    return {
        "E": preparation,
        "R": returned,
        "C": counters,
        "H": callback,
        "bound": max(preparation, returned + max(counters, callback)),
    }


def setup(m, q, width, n, spectators, index_bits, alias):
    require(q in (3, 5) and width in (1, 2) and n in (1, 2), "bounded geometry")
    require(index_bits in (8, 12, 64, 256), "bounded index padding")
    require(
        len(spectators) == 3 and all(1 <= x <= 8 for x in spectators),
        "bounded spectators",
    )
    require(not alias or spectators == (1, 1, 1), "alias fixture domain")
    modulus = q**width
    arena = m.words.Arena(modulus.bit_length() + 1, capacity=64)
    index = m.words.Arena(index_bits, capacity=64)
    columns, depth, parent = (index.literal(x) for x in (1, 0, n))
    geometry = m.Geometry(
        types.SimpleNamespace(dimension=n), index, columns, depth, 0, object()
    )
    counts = [m.cardinal_counts.Count.literal(x) for x in spectators]
    if alias:
        counts = [counts[0]] * 3
    layout = m.layout.Layout(
        geometry, parent, m.words.Ring(arena.literal(modulus)), q, *counts
    )
    return types.SimpleNamespace(**locals())


def snapshot(counts):
    return [(bytes(count.tape.cells), count.tape.head) for count in counts]


def callback_body(m, case, coefficient, callback_bits, retained):
    if callback_bits:
        count = m.cardinal_counts.Count.literal(1 << (callback_bits - 1))
        counter = m.stream.Counter(count)
        counter.close()
        count.close()
        if retained is not None:
            # Deliberately invalid owner: cleared arrays survive both callbacks.
            retained.extend((count.tape, counter.tape))
    return case.arena.literal(coefficient)


def oracle(bits, extents, modulus, coefficient):
    before, middle, suffix = extents
    expected = [0] * len(bits)
    for outer, x, mid, y, tail in itertools.product(
        range(before), range(modulus), range(middle), range(modulus), range(suffix)
    ):
        old = (((outer * modulus + x) * middle + mid) * modulus + y) * suffix + tail
        new_y = (y + coefficient * x) % modulus
        new = (((outer * modulus + x) * middle + mid) * modulus + new_y) * suffix + tail
        expected[new] = bits[old]
    return expected


def execute(
    m, case, census, positions, coefficient, callback_bits, retained, bound, origin
):
    extents = extent_values(case.modulus, case.n, case.spectators, *positions)
    volume = case.modulus**2
    for extent in extents:
        volume *= extent
    require(volume <= 4096, "bounded complete payload")
    require(origin is None or 0 <= origin < volume, "bounded origin plane")
    bits = [
        ((i * 13 + i // 3) % 7) & 1 if origin is None else int(i == origin)
        for i in range(volume)
    ]
    source = m.records.Tape()
    for bit in bits:
        source.append(bit)
    source.rewind()
    original = bytes(source.cells)
    first, last = (case.index.literal(x) for x in positions)
    event = types.SimpleNamespace(
        kind="add", first=last, second=first, request=object()
    )
    calls = []

    def prepare(_request):
        calls.append(1)
        require(len(calls) <= 2, "exactly two coefficient requests")
        census.phase = "callback"
        result = callback_body(m, case, coefficient, callback_bits, retained)
        census.observe()
        census.phase = "native"
        return result

    census.start(bound)
    borrowed = snapshot(case.counts)
    live = (set(case.arena.live), set(case.index.live))
    output = m.action(source, event, case.layout, prepare)
    require(
        list(output.cells[1:]) == oracle(bits, extents, case.modulus, coefficient),
        "complete ADD endpoint",
    )
    require(
        bytes(source.cells) == original and source.head == 1,
        "borrowed payload restored",
    )
    require(snapshot(case.counts) == borrowed, "borrowed counts restored")
    require(
        (set(case.arena.live), set(case.index.live)) == live,
        "numerical live-slot baseline restored",
    )
    require(len(calls) == 2, "both native traversals reached")
    return volume


def check_phases(census, budget, retained):
    prep, native = census.peaks["preparation"], census.peaks["native"]
    require(prep <= budget["E"], "preparation component")
    require(native >= budget["R"] + budget["C"], "attained native countdown component")
    if retained is None:
        require(native == budget["R"] + budget["C"], "exact joined native phase")
        require(
            census.peaks["callback"] == budget["R"] + budget["H"],
            "exact joined callback phase",
        )
        require(
            census.peak == max(prep, budget["R"] + max(budget["C"], budget["H"])),
            "exact phase maximum",
        )
        require(set(census.roots) == census.base, "all private count tapes released")
    else:
        require(
            census.peak > budget["bound"], "clearing alone refutes phase separation"
        )
        require(len(retained) == 4, "both callbacks escaped")
        require(
            all(all(c == 4 for c in tape.cells[1:]) for tape in retained),
            "escaped arrays cleared",
        )


def fixture(
    m,
    q=3,
    width=1,
    n=1,
    spectators=(1, 1, 1),
    positions=(0, 1),
    index_bits=12,
    coefficient=1,
    callback_bits=0,
    alias=False,
    escape=False,
    quota=None,
    origin=None,
):
    require(0 <= positions[0] < positions[1] < 2 * n, "ordered ADD positions")
    require(0 <= coefficient < q**width, "canonical coefficient")
    require(callback_bits in (0, 1, 4, 32, 128), "bounded callback fixture")
    with counted(m) as census:
        case = setup(m, q, width, n, spectators, index_bits, alias)
        extents = extent_values(case.modulus, n, spectators, *positions)
        hh = 2 * (callback_bits + 2) if callback_bits else 0
        budget = envelope(extents, case.modulus, index_bits, hh)
        retained = [] if escape else None
        limit = budget["bound"] if quota is None and not escape else quota
        volume = execute(
            m,
            case,
            census,
            positions,
            coefficient,
            callback_bits,
            retained,
            limit,
            origin,
        )
        check_phases(census, budget, retained)
        result = {
            "q": q,
            "width": width,
            "n": n,
            "spectators": list(spectators),
            "positions": list(positions),
            "I": index_bits,
            "coefficient": coefficient,
            "callback_bits": callback_bits,
            "alias": alias,
            "origin": origin,
            "volume": volume,
            "K": sum(census.base_lengths.values()),
            **budget,
            "preparation_peak": census.peaks["preparation"],
            "native_peak": census.peaks["native"],
            "callback_peak": census.peaks["callback"],
            "peak": census.peak,
        }
        if retained is not None:
            retained.clear()
        case.layout.close()
        case.geometry.close()
        return result


def rejected(operation, phrase):
    try:
        operation()
    except ValueError as error:
        require(phrase in str(error), "named control rejection")
        return
    raise ValueError("control incorrectly accepted")


def run():
    with source_modules() as m:
        rows = [
            fixture(
                m,
                spectators=spectators,
                coefficient=coefficient,
                index_bits=padding,
                callback_bits=callback,
            )
            for spectators, coefficient, padding, callback in itertools.product(
                ((1, 1, 1), (2, 3, 2), (1, 8, 1)), range(3), (8, 64), (0, 4, 32)
            )
        ]
        rows += [
            fixture(m, n=2, positions=positions, callback_bits=4)
            for positions in ((0, 1), (0, 3), (2, 3))
        ]
        rows += [fixture(m, q=q, width=w) for q, w in ((5, 1), (3, 2))]
        rows += [fixture(m, alias=True), fixture(m, index_bits=256)]
        rows += [fixture(m, origin=origin) for origin in range(9)]
        escaping = fixture(m, callback_bits=32, escape=True)
        exact = rows[0]
        rejected(
            lambda: fixture(m, index_bits=8, coefficient=0, quota=exact["peak"] - 1),
            "count backing quota",
        )
        rejected(lambda: fixture(m, positions=(1, 0)), "ordered ADD positions")
        rejected(lambda: fixture(m, coefficient=3), "canonical coefficient")
        rejected(
            lambda: fixture(m, alias=True, spectators=(2, 1, 1)), "alias fixture domain"
        )
        require(
            any(r["peak"] > r["E"] for r in rows), "preparation-only budget refuted"
        )
        require(
            any(r["peak"] > max(r["E"], r["C"], r["H"]) for r in rows),
            "omitted retained marginals refuted",
        )
        require(
            any(r["peak"] < r["E"] + r["C"] + r["H"] for r in rows),
            "disjoint phase peaks need not add",
        )
        require(
            any(r["preparation_peak"] > r["R"] + max(r["C"], r["H"]) for r in rows),
            "omitted preparation refuted",
        )
    return {
        "status": "PASS_SELECTED_ADD_COUNT_PHASE_ENVELOPE",
        "fixtures": rows,
        "escaping_callback": escaping,
        "controls": 8,
        "no_new_kappa": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write", action="store_true", help="regenerate this package's RESULT.json"
    )
    args = parser.parse_args()
    result = run()
    path = PACKAGE / "RESULT.json"
    if args.write:
        path.write_text(json.dumps(result, indent=2) + "\n")
    else:
        require(
            json.dumps(json.loads(path.read_text()), sort_keys=True)
            == json.dumps(result, sort_keys=True),
            "exact typed replay receipt",
        )
    print(
        f"{result['status']} fixtures={len(result['fixtures'])} "
        f"controls={result['controls']} no_new_kappa"
    )


if __name__ == "__main__":
    main()
