#!/usr/bin/env python3
"""Exact level-uniform continuation histories on authenticated PR2697 code."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path
from types import ModuleType

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PREDECESSOR = ROOT / "research/selected-continuation-storage"
HEAD = "a53fdf4bcbe33c6732f0bec1badc8c023380f9d1"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def dimensions(depth, index_bits, residue_bits):
    need(type(depth) is int and 0 <= depth <= 1_000_000, "bounded depth")
    need(
        all(type(b) is int and 2 <= b <= 1_000_000 for b in (index_bits, residue_bits)),
        "bounded fixed word lengths",
    )
    return 2 * index_bits + 4, residue_bits + 3


def envelope(depth, index_bits, residue_bits):
    a, b = dimensions(depth, index_bits, residue_bits)
    if depth == 0:
        return 2 * a + 2 * b + 2
    if a >= b:
        return (depth + 2) * a + (2 * depth + 2) * b + 2
    return (depth - 1) * a + (2 * depth + 5) * b + 2


def capacities(modes, index_bits, residue_bits):
    """Modes are ordered from the rootward/bottom level to the requested level."""
    need(type(modes) is str and len(modes) <= 6, "bounded mode word")
    need(all(mode in "GBLRTU" for mode in modes), "known level grammar")
    a, b = dimensions(len(modes), index_bits, residue_bits)
    pending, values, reverse = a, b, a
    for mode in modes:
        if mode == "U":
            pending, values, reverse = a, b, a
        elif mode == "G":
            pending, reverse = max(a, b + pending), max(reverse, b)
        elif mode == "B":
            pending, values, reverse = a + b + pending, b + values, max(reverse, b)
        elif mode == "L":
            pending, values = max(a + 2 * b, b + pending), b + values
            reverse = max(reverse, b)
        elif mode == "R":
            pending, values = 2 * b + pending, max(values, 2 * b)
            reverse = max(reverse, b)
        else:
            pending, values, reverse = max(a, 3 * b), 2 * b, max(a, b)
    need(pending >= a and values >= b, "initial request and final return retained")
    return pending + 1, reverse, values + 1, b


def authenticate():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    inputs = [item for item in manifest["files"] if item["usage"] == "input"]
    expected = {"README.md", "verify.py", "SNAPSHOT.json"} | {
        "vendor/" + name
        for name in (
            "words.py",
            "records.py",
            "matrices.py",
            "controller.py",
            "NOTICE.md",
        )
    }
    need(len(inputs) == len(expected), "closed input inventory")
    for item in inputs:
        path = Path(item["path"])
        relative = path.relative_to("research/selected-continuation-storage").as_posix()
        need(relative in expected, "unique declared input")
        expected.remove(relative)
        source = ROOT / path
        need(source.is_file() and not source.is_symlink(), "regular source input")
        need(source.stat().st_size <= 1_000_000, "bounded source file")
        raw = source.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == item["sha256"], "input SHA256")
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(blob == item["git_blob"], "input Git blob")
    need(not expected, "complete input inventory")
    snapshot = json.loads((PREDECESSOR / "SNAPSHOT.json").read_text())
    need(snapshot["head"] == HEAD, "scientific source head")
    module = ModuleType("continuation_fixture")
    path = PREDECESSOR / "verify.py"
    module.__file__ = str(path)
    # Every nonstandard input is authenticated before source execution.
    exec(
        compile(path.read_bytes(), str(path), "exec", dont_inherit=True),
        module.__dict__,
    )
    return module


def observer_type(predecessor, expected, warm, quota, collected):
    class Exact(predecessor.Census):
        def __init__(self, records, stacks, direct=False):
            super().__init__(records, stacks, direct)
            for tape, length in zip(self.tapes, warm, strict=True):
                tape.cells.extend([records.BLANK] * (length - len(tape.cells)))
            self.entry = tuple(len(tape.cells) for tape in self.tapes)
            self.expected = tuple(
                max(k, c) for k, c in zip(warm, expected, strict=True)
            )
            collected.append(self)

        def __enter__(self):
            try:
                return super().__enter__()
            except Exception:
                super().__exit__()
                raise

        def scan(self):
            super().scan()
            actual = tuple(len(tape.cells) for tape in self.tapes)
            need(
                all(k <= c for k, c in zip(actual, self.expected, strict=True)),
                "exact directional capacity",
            )
            if quota is not None:
                need(sum(actual) <= quota, "joint capacity")

        def write(self, tape, symbol):
            if id(tape) in self.identities:
                position = self.tapes.index(tape)
                proposed = max(len(tape.cells), tape.head + 1)
                need(proposed <= self.expected[position], "exact directional capacity")
                if quota is not None:
                    other = sum(len(t.cells) for t in self.tapes if t is not tape)
                    need(other + proposed <= quota, "joint capacity")
            super().write(tape, symbol)

    return Exact


def fixture_capacities(modes, residue_bits, literal, warm, repeats, quota):
    need(type(modes) is str and len(modes) <= 6, "bounded fixture modes")
    need(
        type(residue_bits) is int and 2 <= residue_bits <= 128, "fixture residue width"
    )
    need(type(repeats) is int and repeats in (1, 2), "bounded repetition")
    need(
        quota is None or (type(quota) is int and 0 <= quota <= 1_000_000),
        "bounded optional quota",
    )
    need(
        len(warm) == 4 and all(type(k) is int and 1 <= k <= 1024 for k in warm),
        "four bounded entry extents",
    )
    need(
        type(literal) is bool
        and (
            not literal
            or (set(modes) <= {"B"} and len(modes) <= 2 and residue_bits == 3)
        ),
        "declared literal GL64 fixture",
    )
    depth = len(modes)
    index_bits = 6 * (depth + 1) + 2 if literal else max(8, 6 * depth + 2)
    return index_bits, capacities(modes, index_bits, residue_bits)


def execute(
    predecessor,
    modules,
    modes,
    residue_bits,
    *,
    literal=False,
    warm=(1, 1, 1, 1),
    repeats=1,
    quota=None,
):
    index_bits, expected = fixture_capacities(
        modes, residue_bits, literal, warm, repeats, quota
    )
    depth = len(modes)
    collected = []
    census, bound = predecessor.Census, predecessor.bound
    weight = modules[2].Callback.weight

    def warm_bound(h, i, r):
        live, backing = bound(h, i, r)
        return live, max(
            backing, sum(max(k, c) for k, c in zip(warm, expected, strict=True))
        )

    def repeated(callback, coordinate):
        for _ in range(repeats - 1):
            value = weight(callback, coordinate)
            callback.residue.free(value)
        return weight(callback, coordinate)

    predecessor.Census = observer_type(predecessor, expected, warm, quota, collected)
    predecessor.bound = warm_bound
    modules[2].Callback.weight = repeated
    try:
        result = (
            predecessor.literal_case(modules, depth)
            if literal
            else predecessor.run_case(modules, modes, residue_bits)
        )
    finally:
        predecessor.Census, predecessor.bound = census, bound
        modules[2].Callback.weight = weight
    need(len(collected) == 1, "one callback observer")
    observed = collected[0]
    lengths = tuple(len(tape.cells) for tape in observed.tapes)
    need(lengths == observed.expected, "exact four historical maxima")
    return {
        "modes": modes,
        "I": index_bits,
        "R": residue_bits,
        "lengths": lengths,
        "backing": sum(lengths),
        "fresh_envelope": envelope(depth, index_bits, residue_bits),
        "entry": observed.entry,
        "writes": result["writes"],
        "repeats": repeats,
        "literal_gl64": literal,
    }


def controls(predecessor, modules):
    try:
        execute(predecessor, modules, "TB", 32, quota=348)
    except ValueError as error:
        need(str(error) == "joint capacity", "actual one-cell-short rejection")
    else:
        raise ValueError("one-cell-short quota accepted")
    # These are actual earlier Tape.write maxima, not invented padded lengths.
    first = execute(predecessor, modules, "TR", 32)
    second = execute(predecessor, modules, "TB", 32, warm=first["lengths"])
    need(first["lengths"] == (176, 35, 71, 35), "mixed first history")
    need(
        second["backing"] == 352 > second["fresh_envelope"],
        "changed-grammar history rejects",
    )
    return {
        "short_quota_rejected": 348,
        "changed_grammar_first": first,
        "changed_grammar_second": second,
        "nonuniform": nonuniform_control(predecessor, modules),
    }


def nonuniform_control(predecessor, modules):
    """Deliberately change fixture metadata between equal-level requests."""
    factory, census = predecessor.synthetic_class, predecessor.Census
    collected = []

    def varying_factory(controller):
        class Varying(factory(controller)):
            def step(self, level):
                if level.inspect() == 2:
                    visit = getattr(self, "level_two_visits", 0)
                    need(visit < 2, "two nonuniform level-two requests")
                    self.level_two_visits = visit + 1
                    self.modes = "T" + ("R" if visit == 0 else "B") + "B"
                return super().step(level)

        return Varying

    class Capture(census):
        def __init__(self, records, stacks, direct=False):
            super().__init__(records, stacks, direct)
            collected.append(self)

    predecessor.synthetic_class, predecessor.Census = varying_factory, Capture
    try:
        result = predecessor.run_case(modules, "TBB", 64)
    finally:
        predecessor.synthetic_class, predecessor.Census = factory, census
    need(len(collected) == 1, "one nonuniform observer")
    lengths = tuple(len(tape.cells) for tape in collected[0].tapes)
    need(lengths == (447, 67, 269, 67), "literal nonuniform historical maxima")
    limit = envelope(3, 20, 64)
    need(sum(lengths) == 850 > limit == 827, "nonuniform grammar rejects envelope")
    return {
        "lengths": lengths,
        "backing": sum(lengths),
        "uniform_envelope": limit,
        "writes": result["writes"],
        "scope": "Changed fixture metadata; not a fixed Program.",
    }


def verify():
    predecessor = authenticate()
    names = ("words", "records", "matrices", "controller")
    need(not any(name in sys.modules for name in names), "no preloaded runtime modules")
    modules = predecessor.load_source()
    try:
        cases = []
        for depth in range(4):
            for mode_tuple in itertools.product("GBLRTU", repeat=depth):
                for residue_bits in (4, 32):
                    modes = "".join(mode_tuple)
                    case = execute(predecessor, modules, modes, residue_bits)
                    need(case["backing"] <= case["fresh_envelope"], "uniform envelope")
                    cases.append(case)
        sharp = []
        for depth in range(1, 7):
            for residue_bits, modes in (
                (4, "B" * depth),
                (128, "T" + "B" * (depth - 1)),
            ):
                case = execute(predecessor, modules, modes, residue_bits)
                need(case["backing"] == case["fresh_envelope"], "attaining grammar")
                sharp.append(case)
        literal = [
            execute(predecessor, modules, "B" * d, 3, literal=True) for d in range(3)
        ]
        repeated = execute(predecessor, modules, "TB", 32, repeats=2)
        warm = execute(predecessor, modules, "TB", 32, warm=(700, 2, 300, 1))
        return {
            "status": "PASS_SELECTED_CONTINUATION_JOINT_MAX",
            "source_head": HEAD,
            "synthetic_cases": len(cases),
            "writes": sum(c["writes"] for c in cases),
            "sharp": sharp,
            "literal_gl64": literal,
            "repeated": repeated,
            "warm": warm,
            "controls": controls(predecessor, modules),
            "scope": "Successful level-uniform fixed-program continuation arrays; no total reserve or new kappa.",
        }
    finally:
        for name in names:
            sys.modules.pop(name, None)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    actual = verify()
    if not args.emit:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        need(
            json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "complete typed receipt",
        )
    print(json.dumps(actual, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
