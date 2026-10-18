#!/usr/bin/env python3
"""Check frozen Layout lifetimes, exact cardinalities and successful erasure."""

import argparse
import ast
import hashlib
import itertools
import json
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SNAPSHOT_HASH = "36accc9be7b4f8550baf42102780dc112b57afb094cc32aa577b40bfd70daba5"
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


def load(root=ROOT):
    raw = (root / "SNAPSHOT.json").read_bytes()
    require(hashlib.sha256(raw).hexdigest() == SNAPSHOT_HASH, "snapshot identity")
    files = json.loads(raw)["files"]
    expected = {f"vendor/{name}.py" for name in (*MODULES, "numeric")} | {
        "vendor/NOTICE.md",
        "vendor/stream_runner.py",
        "evidence/CALLER-ENTRY.md",
    }
    require(len(files) == len(expected), "unique source inventory")
    require({item["path"] for item in files} == expected, "complete source inventory")
    source = {}
    for item in files:
        data = (root / item["path"]).read_bytes()
        require(
            hashlib.sha256(data).hexdigest() == item["sha256"],
            "source hash: " + item["path"],
        )
        source[Path(item["path"]).stem] = data
    result = {}
    for name in MODULES:
        module = types.ModuleType(name)
        module.__file__ = str(root / "vendor" / (name + ".py"))
        sys.modules[name] = module
        exec(compile(source[name], module.__file__, "exec"), module.__dict__)  # noqa: S102
        result[name] = module
    # Execute the unchanged Geometry class only. The other numeric.py classes
    # require unrelated form/coefficient modules, outside this component's scope.
    classes = [
        node
        for node in ast.parse(source["numeric"]).body
        if isinstance(node, ast.ClassDef) and node.name == "Geometry"
    ]
    require(len(classes) == 1, "one frozen Geometry class")
    scope = {"Unsigned": result["words"].Unsigned, "need": result["words"].need}
    tree = ast.Module(body=classes, type_ignores=[])
    exec(compile(tree, str(root / "vendor/numeric.py"), "exec"), scope)  # noqa: S102
    result["Geometry"] = scope["Geometry"]
    return types.SimpleNamespace(**result)


def snapshot(arena):
    return {
        slot: (bytes(arena.words[slot].cells), arena.words[slot].head)
        for slot in arena.live
    }


def observed_arena(words, bits):
    class Observed(words.Arena):
        def __init__(self):
            super().__init__(bits, capacity=64)
            self.base = None
            self.peak = self.events = self.scans = 0
            self.limit = 64

        def zero(self):
            result = super().zero()
            if self.base is not None:
                excess = len(self.live) - len(self.base)
                require(excess <= self.limit, "numerical allowance exceeded")
                require(self.events < 30000, "allocation-event capacity")
                self.events += 1
                if excess > self.peak:
                    self.peak = excess
                    occupied = sum(
                        c != words.BLANK
                        for word in [self.template, *self.words]
                        for c in word.cells[1:]
                    )
                    require(
                        occupied == (len(self.live) + 1) * (self.bits + 1),
                        "literal occupied symbols including template",
                    )
                    self.scans += 1
            return result

        def start(self, limit):
            self.base = snapshot(self)
            self.peak = self.events = self.scans = 0
            self.limit = limit

    return Observed()


def restored(arena):
    require(snapshot(arena) == arena.base, "entry slots, contents and heads restored")
    require(arena.template.head == 1, "template head restored")
    for slot in arena.available:
        word = arena.words[slot]
        require(
            word.head == 1 and all(c == 4 for c in word.cells[1:]),
            "freed backing slots literally erased",
        )


def natural_value(value):
    cells = value.tape.cells
    require(value.tape.head == 1, "cardinality head restored")
    end = cells.index(3, 1)
    require(all(c in (0, 1) for c in cells[1:end]), "binary cardinality")
    return sum(c << bit for bit, c in enumerate(cells[1:end]))


def setup(m, dimension, columns, parent, q, width, embedded, borrowed):
    require(1 <= dimension <= 64 and 1 <= columns <= 3, "bounded fixture geometry")
    require(dimension * columns <= parent <= 127, "bounded fixture parent")
    require(
        q in (3, 5) and width in (1, 2) and borrowed in (0, 3),
        "bounded fixture context",
    )
    modulus = q**width
    residue = observed_arena(m.words, modulus.bit_length() + 1)
    index = observed_arena(m.words, max(8, (2 * parent).bit_length() + 1))
    ring = m.words.Ring(residue.literal(modulus))
    for n in range(borrowed):
        residue.literal(n % modulus)
        index.literal(n)
    col, depth, size = (index.literal(n) for n in (columns, 0, parent))
    geometry = m.Geometry(
        types.SimpleNamespace(dimension=dimension), index, col, depth, 0, object()
    )
    counts = [m.cardinal_counts.Count.literal(n) for n in (2, 3, 5)]
    case = types.SimpleNamespace(**locals())
    case.arguments = (geometry, size, ring, q, *counts)
    return case


def check_constructor(case, limit=4):
    case.residue.start(0)
    case.index.start(limit)
    base = case.index.base
    layout = case.m.layout.Layout(*case.arguments, embedded=case.embedded)
    require(
        case.index.peak == 4 and len(case.index.live) == len(base) + 3,
        "constructor peak four and retained three",
    )
    require(
        [x.inspect() for x in (layout.core, layout.extra, layout.total)]
        == [
            case.dimension * case.columns,
            2 * (case.parent - case.dimension * case.columns),
            2 * case.parent,
        ],
        "exact constructor geometry",
    )
    restored(case.residue)
    require(
        all(
            (bytes(case.index.words[s].cells), case.index.words[s].head) == v
            for s, v in base.items()
        ),
        "constructor preserves borrowed indices",
    )
    return layout


def physical(position, case):
    core = case.dimension * case.columns
    return position + (
        2 * (case.parent - core) if case.embedded and position >= core else 0
    )


def expected_extents(case, first, second):
    a = physical(first, case)
    b = physical(second, case) if second is not None else a
    pre = 2 * case.modulus**a * (3 if a >= case.parent else 1)
    tail = 5 * case.modulus ** (2 * case.parent - b - 1) * (3 if b < case.parent else 1)
    exponents = [a, 2 * case.parent - b - 1]
    if second is None:
        return [pre, tail], exponents
    exponent = b - a - 1
    middle = case.modulus**exponent * (3 if a < case.parent <= b else 1)
    return [pre, middle, tail], [*exponents, exponent]


def extents_case(case, layout, first, second, limits=None):
    # Event positions, Geometry, Layout and unrelated Words are ALL entry residents.
    case.residue.base = case.index.base = None
    a = case.index.literal(first)
    b = None if second is None else case.index.literal(second)
    expected, exponents = expected_extents(case, first, second)
    bound = (6 if any(exponents) else 0, 3 if b is None else 4)
    for arena, limit in zip((case.residue, case.index), limits or bound, strict=True):
        arena.start(limit)
    result = layout.extents(a, b)
    require(
        [natural_value(x) for x in result] == expected,
        "exact extent cardinalities and gap",
    )
    for value, integer in zip(result, expected, strict=True):
        require(
            value.tape.cells[integer.bit_length() + 1] == 0
            and value.tape.cells[integer.bit_length() + 2] == 3,
            "separately canonical extent margin",
        )
        value.close()
    for arena in (case.residue, case.index):
        restored(arena)
    peaks = [case.residue.peak, case.index.peak]
    require(peaks == list(bound), "sharp per-call extent peaks")
    record = {
        "first": first,
        "second": second,
        "peaks": peaks,
        "allocations": case.residue.events + case.index.events,
    }
    case.residue.base = case.index.base = None
    case.index.free(a)
    if b is not None:
        case.index.free(b)
    return record


def check_fibre(case, layout):
    case.residue.start(6)
    case.index.start(0)
    value = layout.fibre()
    require(
        natural_value(value) == 30 * case.modulus ** (2 * case.parent),
        "exact full fibre",
    )
    value.close()
    for arena in (case.residue, case.index):
        restored(arena)
    require((case.residue.peak, case.index.peak) == (6, 0), "sharp fibre peaks")


def check_physical(case, layout, positions):
    for position in positions:
        case.index.base = None
        word = case.index.literal(position)
        case.index.start(1)
        result = layout.physical(word)
        require(result.inspect() == physical(position, case), "literal physical atom")
        require(case.index.peak == 1, "one physical index result")
        case.index.free(result)
        restored(case.index)
        case.index.base = None
        case.index.free(word)


def run_fixture(m, specification):
    case = setup(m, *specification)
    case.residue.start(64)
    case.index.start(64)
    original = (case.residue.base, case.index.base)
    layout = check_constructor(case)
    length = 2 * (case.dimension * case.columns if case.embedded else case.parent)
    positions = (
        list(range(length))
        if length <= 6
        else sorted({0, 1, length // 2 - 1, length // 2, length - 1})
    )
    check_physical(case, layout, positions)
    rows = [extents_case(case, layout, a, None) for a in positions]
    rows += [
        extents_case(case, layout, a, b)
        for a, b in itertools.combinations(positions, 2)
    ]
    check_fibre(case, layout)
    case.residue.start(0)
    case.index.start(0)
    layout.close()
    for arena, baseline in zip((case.residue, case.index), original, strict=True):
        arena.base = baseline
        restored(arena)
    return {
        "parameters": list(specification),
        "extent_calls": len(rows),
        "physical_calls": len(positions),
        "zero_residue_calls": sum(row["peaks"][0] == 0 for row in rows),
        "unary_calls": sum(row["second"] is None for row in rows),
        "allocations": sum(row["allocations"] for row in rows),
        "constructor_peaks": [0, 4],
        "constructor_retained": [0, 3],
        "fibre_peaks": [6, 0],
    }


def calculate(m):
    shapes = ((1, 1, 1), (2, 1, 3), (3, 2, 7), (64, 1, 64), (64, 1, 127))
    cases = [
        run_fixture(m, (*shape, q, width, embedded, borrowed))
        for shape in shapes
        for q, width in ((3, 1), (3, 2), (5, 1))
        for embedded, borrowed in ((True, 0), (True, 3), (False, 3))
    ]
    return {
        "status": "PASS_SELECTED_LAYOUT_NUMERICAL_LIFETIME",
        "fixtures": cases,
        "fixture_count": len(cases),
        "extent_calls": sum(row["extent_calls"] for row in cases),
        "physical_calls": sum(row["physical_calls"] for row in cases),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    actual = calculate(load())
    if args.emit:
        print(json.dumps(actual, indent=2))
    else:
        expected = json.loads((ROOT / "RESULT.json").read_text())
        require(
            json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "complete typed receipt",
        )
        print(
            actual["status"],
            "fixtures=" + str(actual["fixture_count"]),
            "extents=" + str(actual["extent_calls"]),
        )


if __name__ == "__main__":
    main()
