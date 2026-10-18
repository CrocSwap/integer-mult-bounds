#!/usr/bin/env python3
"""Joint retained numerical/count backing in the unchanged native ADD."""

import argparse
import hashlib
import json
import sys
import types
import weakref
from contextlib import contextmanager
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[1]
PREFIX = "research/selected-adapter-caller-entry/vendor/"
MANIFEST_SHA256 = "af8fc7b5d58320a680a3b3539f6e09a11085e20a815c16fb47c905f15d2d51e8"
MODULES = ("words", "records", "stream", "cardinality", "counts")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(repo=REPO):
    raw_manifest = (PACKAGE / "SOURCES.json").read_bytes()
    require(
        hashlib.sha256(raw_manifest).hexdigest() == MANIFEST_SHA256, "manifest identity"
    )
    manifest = json.loads(raw_manifest)
    data = {}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        raw = (repo / row["path"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "source SHA256")
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw)
        require(blob.hexdigest() == row["git_blob"], "source Git blob")
        data[row["path"]] = raw
    require(all(PREFIX + name + ".py" in data for name in MODULES), "source inventory")
    return data


@contextmanager
def source_modules(repo=REPO):
    data = authenticate(repo)
    absent = object()
    previous = {name: sys.modules.get(name, absent) for name in MODULES}
    loaded = {}
    try:
        for name in MODULES:
            path = PREFIX + name + ".py"
            module = types.ModuleType(name)
            module.__file__ = str(repo / path)
            sys.modules[name] = module
            exec(compile(data[path], module.__file__, "exec"), module.__dict__)
            loaded[name] = module
        yield types.SimpleNamespace(**loaded)
    finally:
        for name, old in previous.items():
            if old is absent:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = old


class Census:
    """Weak references observe count arrays without extending their lifetimes."""

    def __init__(self, arenas):
        self.arenas = arenas
        self.tapes = weakref.WeakValueDictionary()
        self.baseline = {}
        self.active = False
        self.phase = "setup"
        self.peak = self.samples = 0
        self.live_peak = 0
        self.witness = None
        self.phases = {}
        self.limit = None

    def observe(self):
        if not self.active:
            return
        require(len(self.tapes) <= 24, "bounded count inventory")
        for identity, size in self.baseline.items():
            require(
                len(self.tapes[identity].cells) == size, "entry count backing unchanged"
            )
        count = sum(len(t.cells) for t in self.tapes.values())
        numerical = sum(
            len(w.cells) for a in self.arenas for w in [a.template, *a.words]
        )
        live_cells = sum(
            len(a.template.cells) + sum(len(a.words[s].cells) for s in a.live)
            for a in self.arenas
        )
        require(all(len(a.words) <= 64 for a in self.arenas), "bounded numerical slots")
        total = count + numerical
        if total > self.peak:
            self.witness = {
                "count": count,
                "numerical": numerical,
                "live_cells": live_cells,
                "phase": self.phase,
            }
        self.peak = max(self.peak, total)
        self.live_peak = max(self.live_peak, count + live_cells)
        self.phases[self.phase] = max(self.phases.get(self.phase, 0), total)
        self.samples += 1
        require(self.samples <= 500_000, "bounded observer events")
        require(self.limit is None or total <= self.limit, "joint backing quota")

    def start(self, limit=None):
        self.baseline = {identity: len(t.cells) for identity, t in self.tapes.items()}
        self.active, self.limit, self.phase = True, limit, "native"
        self.observe()

    def tape_type(self, original):
        census = self

        class Observed(original):
            def __init__(self):
                super().__init__()
                census.tapes[id(self)] = self
                census.observe()

            def write(self, symbol):
                super().write(symbol)
                census.observe()

        return Observed


@contextmanager
def observed(m, arenas):
    census = Census(arenas)
    owners = (m.stream, m.cardinality, m.counts)
    tapes = [module.Tape for module in owners]
    original_zero = m.words.Arena.zero

    def zero(arena):
        result = original_zero(arena)
        census.observe()
        return result

    try:
        for module, tape in zip(owners, tapes, strict=True):
            module.Tape = census.tape_type(tape)
        m.words.Arena.zero = zero
        yield census
    finally:
        m.words.Arena.zero = original_zero
        for module, tape in zip(owners, tapes, strict=True):
            module.Tape = tape


def envelope(extents, modulus, arenas, scratch, index_scratch, count_scratch):
    p, middle, suffix = (x.bit_length() + 3 for x in extents)
    r = modulus.bit_length() + 3
    copy = r + (2 * suffix if extents[2] > 1 else 0)
    counters = p + r + middle + max(middle, copy)
    residue, index = arenas
    nr = max(len(residue.words), len(residue.live) + max(scratch, 6))
    ni = max(len(index.words), len(index.live) + index_scratch)
    numerical = (nr + 1) * (residue.bits + 2) + (ni + 1) * (index.bits + 2)
    return counters, numerical, max(counters, count_scratch) + numerical


def warm(arena, slots):
    require(0 <= slots <= 40, "bounded warm history")
    temporary = [arena.zero() for _ in range(slots)]
    arena.free_many(*temporary)


def payload(m, modulus, extents, basis=None):
    size = extents[0] * modulus * extents[1] * modulus * extents[2]
    require(size <= 1024, "bounded complete fibre")
    data = [(i * 7 + i // 3 + 1) % 2 for i in range(size)]
    if basis is not None:
        require(0 <= basis < size, "basis address")
        data = [int(i == basis) for i in range(size)]
    tape = m.records.Tape()
    for bit in data:
        tape.append(bit)
    tape.rewind()
    return tape, data


def expected_payload(data, modulus, extents, coefficient):
    before, middle, suffix = extents
    result = [None] * len(data)
    for address, bit in enumerate(data):
        prefix, tail = divmod(address, suffix)
        prefix, y = divmod(prefix, modulus)
        prefix, gap = divmod(prefix, middle)
        outer, x = divmod(prefix, modulus)
        require(outer < before, "complete oracle address")
        target = (
            ((outer * modulus + x) * middle + gap) * modulus
            + (y + coefficient * x) % modulus
        ) * suffix + tail
        require(result[target] is None, "oracle is a permutation")
        result[target] = bit
    return result


def coefficient_callback(
    m, ring, index, operand, count, scratch, index_scratch, escaped, census
):
    def callback():
        census.phase = "callback"
        result = ring.inverse(operand)
        require(result is not None, "unit inverse callback")
        indices = [index.zero() for _ in range(index_scratch)]
        counters = [m.stream.Counter(count) for _ in range(scratch)]
        for counter in counters:
            counter.close()
            if escaped is not None:
                escaped.append(counter.tape)
        if counters:
            del counter
        del counters
        index.free_many(*indices)
        census.observe()
        census.phase = "native"
        return result

    return callback


def setup_case(m, modulus, warm_slots, residents):
    residue = m.words.Arena(modulus.bit_length() + 1, 64)
    index = m.words.Arena(16, 64)
    warm(residue, warm_slots)
    warm(index, warm_slots // 2)
    ring = m.words.Ring(residue.literal(modulus))
    operand = residue.literal(2)
    for _ in range(residents):
        residue.literal(1)
        index.literal(1)
    return residue, index, ring, operand


def check_return(arenas, counts, before, output, expected):
    require(list(output.cells[1:]) == expected, "ADD oracle")
    after = tuple({s: bytes(a.words[s].cells) for s in a.live} for a in arenas)
    require(before == after, "borrowed numerical ownership and values")
    require(
        all(w.head == 1 for a in arenas for w in a.words), "restored numerical heads"
    )
    require(all(x.tape.head == 1 for x in counts), "restored extent heads")


def measurement(census, arenas, parameters, count, numerical, bound):
    if not parameters["retained"]:
        require(census.peak <= bound, "proved joint envelope")
        require(set(census.tapes) == set(census.baseline), "private count release")
    return {
        **parameters,
        "K": sum(census.baseline.values()),
        "C": count,
        "N": numerical,
        "bound": bound,
        "peak": census.peak,
        "phases": census.phases,
        "slots": [len(a.words) for a in arenas],
        "live_peak": census.live_peak,
        "witness": census.witness,
    }


def run_case(
    m,
    extents=(1, 1, 1),
    warm_slots=0,
    index_scratch=0,
    count_scratch=0,
    retain=False,
    quota=None,
    modulus=5,
    residents=0,
    basis=None,
    alias=False,
):
    require(all(1 <= x <= 2 for x in extents), "bounded spectator extents")
    require(count_scratch in (0, 1, 2) and 0 <= index_scratch <= 10, "callback domain")
    require(modulus in (3, 5, 9) and residents in (0, 3, 7), "ring/resident domain")
    require(not alias or extents == (1, 1, 1), "equal alias extents")
    parameters = {
        "extents": list(extents),
        "warm": warm_slots,
        "index_scratch": index_scratch,
        "modulus": modulus,
        "residents": residents,
        "basis": basis,
        "alias": alias,
        "count_scratch": count_scratch,
        "retained": retain,
    }
    residue, index, ring, operand = setup_case(m, modulus, warm_slots, residents)
    arenas = residue, index
    with observed(m, arenas) as census:
        counts = [m.counts.Count.literal(x).marginal() for x in extents]
        if alias:
            counts = [counts[0]] * 3
        count = m.counts.Count.literal((1 << 32) - 1) if count_scratch else None
        before = tuple({s: bytes(a.words[s].cells) for s in a.live} for a in arenas)
        c, n, private = envelope(
            extents, modulus, arenas, 10, index_scratch, count_scratch * 34
        )
        k = sum(len(t.cells) for t in census.tapes.values())
        source, data = payload(m, modulus, extents, basis)
        escaped = [] if retain else None
        callback = coefficient_callback(
            m,
            ring,
            index,
            operand,
            count,
            count_scratch,
            index_scratch,
            escaped,
            census,
        )
        census.start(quota)
        output, _meter = m.stream.add_pass(source, ring, *counts, callback)
        census.observe()
        expected = expected_payload(data, modulus, extents, pow(2, -1, modulus))
        check_return(arenas, counts, before, output, expected)
        return measurement(census, arenas, parameters, c, n, k + private)


def replay():
    with source_modules() as m:
        cases = [
            run_case(m, extents=e, warm_slots=w, index_scratch=i, count_scratch=c)
            for e in ((1, 1, 1), (2, 1, 2), (1, 2, 2))
            for w, i, c in ((0, 0, 0), (0, 10, 0), (32, 0, 0), (0, 0, 2))
        ]
        sharp = cases[0]
        require(sharp["peak"] == sharp["bound"], "joint bound attained")
        require(
            sharp["phases"]["native"] > sharp["phases"]["callback"],
            "retained numeric arrays coexist with native countdowns",
        )
        require(sharp["peak"] > sharp["live_peak"], "live phases undercount backing")
        cases.extend(run_case(m, modulus=q) for q in (3, 9))
        cases.append(run_case(m, residents=7))
        cases.append(run_case(m, alias=True))
        cases.extend(run_case(m, basis=i) for i in range(25))
        escaped = run_case(m, count_scratch=2, retain=True)
        require(escaped["peak"] > escaped["bound"], "capture defeats release premise")
    return {"cases": cases, "escaped": escaped}


def check_receipt(actual, expected):
    require(
        json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
        "fixed typed result receipt",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = replay()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        check_receipt(result, expected)
        print("PASS_SELECTED_ADD_JOINT_BACKING cases=41 capture_control=1")


if __name__ == "__main__":
    main()
