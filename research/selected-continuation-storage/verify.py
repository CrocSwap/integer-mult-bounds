#!/usr/bin/env python3
"""Source-bound continuation-space checks, including literal tape writes."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace

PACKAGE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticated_exports():
    manifest = json.loads((PACKAGE / "SNAPSHOT.json").read_text())
    names = {"words.py", "records.py", "matrices.py", "controller.py", "NOTICE.md"}
    need(len(manifest["files"]) == 5, "five exact source exports")
    need({Path(item["path"]).name for item in manifest["files"]} == names,
         "closed source inventory")
    exports = {}
    for item in manifest["files"]:
        path = PACKAGE / item["path"]
        need(path.parent == PACKAGE / "vendor", "local source path")
        raw = path.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == item["sha256"], "source SHA256")
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(blob == item["git_blob"], "source Git blob")
        exports[path.name] = raw
    return manifest, exports


def sources():
    manifest, _exports = authenticated_exports()
    return manifest["head"]


def load_source():
    _manifest, exports = authenticated_exports()
    names = ("words", "records", "matrices", "controller")
    need(not any(name in sys.modules for name in names), "no preloaded source modules")
    try:
        for name in names:
            path = PACKAGE / "vendor" / (name + ".py")
            module = ModuleType(name)
            module.__file__ = str(path)
            sys.modules[name] = module
            # Execute the bytes just authenticated, bypassing all .pyc caches.
            exec(compile(exports[name + ".py"], str(path), "exec", dont_inherit=True), module.__dict__)
    except Exception:
        for name in names:
            sys.modules.pop(name, None)
        raise
    return sys.modules["words"], sys.modules["records"], sys.modules["controller"]


def bound(depth, index_bits, residue_bits):
    need(type(depth) is int and 0 <= depth <= 1_000_000, "bounded nonnegative depth")
    need(all(type(bits) is int and 2 <= bits <= 1_000_000
             for bits in (index_bits, residue_bits)), "positive fixed word extents")
    request, scalar = 2 * index_bits + 4, residue_bits + 3
    largest = max(request, scalar)
    live = (depth + 1) * largest + depth * scalar
    return live, 2 * live + largest + scalar + 2


def check_receipt(actual, expected):
    need(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
         "fixed typed result receipt")


class Census:
    """Incremental content meter checked against literal cells at every pop."""

    def __init__(self, records, stacks, direct=False):
        self.records, self.stacks = records, stacks
        self.direct = direct
        self.tapes = tuple(tape for stack in stacks for tape in (stack.tape, stack.reverse))
        self.identities = {id(tape) for tape in self.tapes}
        self.live = self.peak = self.backing_peak = self.writes = self.pops = 0
        self.original_write, self.original_pop = records.Tape.write, records.Stack.pop

    def scan(self):
        literal = sum(symbol not in (self.records.LEFT, self.records.BLANK)
                      for tape in self.tapes for symbol in tape.cells)
        need(literal == self.live, "incremental meter agrees with direct cells")
        self.backing_peak = max(self.backing_peak, sum(len(tape.cells) for tape in self.tapes))

    def write(self, tape, symbol):
        if id(tape) not in self.identities:
            self.original_write(tape, symbol)
            return
        before = tape.cells[tape.head] if tape.head < len(tape.cells) else self.records.BLANK
        self.original_write(tape, symbol)
        excluded = (self.records.LEFT, self.records.BLANK)
        self.live += int(symbol not in excluded) - int(before not in excluded)
        self.peak = max(self.peak, self.live)
        self.backing_peak = max(self.backing_peak, sum(len(t.cells) for t in self.tapes))
        self.writes += 1
        if self.direct:
            self.scan()

    def pop(self, stack):
        result = self.original_pop(stack)
        if stack in self.stacks:
            self.scan()
            self.pops += 1
        return result

    def __enter__(self):
        self.records.Tape.write = lambda tape, symbol: self.write(tape, symbol)
        self.records.Stack.pop = lambda stack: self.pop(stack)
        self.scan()
        return self

    def __exit__(self, *_exception):
        self.records.Tape.write = self.original_write
        self.records.Stack.pop = self.original_pop


def synthetic_class(controller):
    class Synthetic(controller.Callback):
        """Only step/preparation oracles are replaced; weight is literal."""

        def step(self, level):
            k = level.inspect()
            mode = self.modes[k - 1]
            kind = controller.GOOD_KIND if mode == "G" else (
                controller.UNIT_KIND if mode == "U" else controller.PAIR_KIND)
            field = 64 if mode in "RT" else 0
            parent = self.index.literal(64 ** (len(self.modes) - k + 1))
            child = self.index.literal(64 ** (len(self.modes) - k))
            return (kind, k, 1, field, int(field >= 64), 0), parent, child, self.index.copy(child)

        def prepare(self, _slot, code, _scope):
            return self.modes[code - 1]

    return Synthetic


class Tables:
    """Finite unit tables for control coverage, not GL64 preparation evidence."""

    def __init__(self, ring):
        self.ring = ring

    def good_pivots(self, _mode, _rank):
        return [self.ring.arena.copy(self.ring.one)]

    def free(self, _table):
        pass  # The finite mode tag owns no numerical words.

    def fallback(self, mode):
        permutation = list(range(66))
        a, b = {"B": (0, 1), "L": (0, 64), "R": (64, 0), "T": (64, 65)}[mode]
        permutation[a], permutation[b] = b, a
        return [self.ring.arena.copy(self.ring.one) for _ in range(66)], permutation


def run_case(modules, modes, residue_bits):
    words, records, controller = modules
    depth, index_bits = len(modes), max(8, 6 * len(modes) + 2)
    indices, residues = words.Arena(index_bits, 256), words.Arena(residue_bits, 256)
    modulus = residues.literal(1 << (residue_bits - 2))
    ring = words.Ring(modulus)
    cls = synthetic_class(controller)
    callback = cls.__new__(cls)
    callback.index, callback.residue = indices, residues
    callback.raw, callback.ring = words.Unsigned(indices), ring
    callback.matrices, callback.modes = Tables(ring), modes
    callback.one_index = indices.literal(1)
    callback.depth, callback.root_size = indices.literal(depth), indices.literal(64 ** depth)
    callback.final_size = indices.literal(1)
    callback.root_unit = residues.copy(ring.one)
    callback.pending, callback.values = records.Stack(indices, residues), records.Stack(indices, residues)
    coordinate = indices.zero()
    saved_index, saved_residue = set(indices.live), set(residues.live)
    with Census(records, (callback.pending, callback.values)) as census:
        result = callback.weight(coordinate)
        need(result.inspect() == 1, "literal returned unit")
        residues.free(result)
        census.scan()
        need(census.live == 0, "all serialized continuation symbols erased")
        need(all(tape.head == 1 for tape in census.tapes), "all four stack heads restored")
    need(indices.live == saved_index and residues.live == saved_residue, "no numerical temporary leak")
    live, backing = bound(depth, index_bits, residue_bits)
    need(census.peak <= live and census.backing_peak <= backing, "continuation bounds")
    for arena in (indices, residues):
        arena.rollback(set())
    return {"modes": modes, "I": index_bits, "R": residue_bits, "peak": census.peak,
            "backing": census.backing_peak, "bound": live, "backing_bound": backing,
            "writes": census.writes, "pops": census.pops}


def rejection_controls(modules):
    words, records, _controller = modules
    indices, residues = words.Arena(8, 16), words.Arena(32, 16)
    stack = records.Stack(indices, residues)
    first, second = indices.literal(1), indices.literal(2)
    stack.push(records.VALUE, first, second)
    source_size = sum(symbol not in (records.LEFT, records.BLANK) for symbol in stack.tape.cells)
    # Omit pop's source erasures; the delimiter slack cannot pay for this copy.
    for symbol in reversed(stack.tape.cells[1:-1]):
        stack.reverse.append(symbol)
    duplicated = sum(symbol not in (records.LEFT, records.BLANK)
                     for tape in (stack.tape, stack.reverse) for symbol in tape.cells)
    need(source_size == 20 and duplicated > source_size, "missing-erasure control rejects")
    for bad in ((-1, 8, 8), (True, 8, 8), (1, 1, 8), (1, 8, False)):
        try:
            bound(*bad)
        except ValueError:
            continue
        raise ValueError("invalid domain accepted")
    return 5


def literal_setup(modules, depth):
    words, records, _controller = modules
    size = 64 ** (depth + 1)
    indices, residues = words.Arena(size.bit_length() + 1), words.Arena(3)
    modulus = residues.literal(3)
    ring = words.Ring(modulus)
    identity = tuple(tuple(int(i == j) for j in range(64)) for i in range(64))
    header = [list(row) for row in identity]
    for i in range(64):
        header[i][0] = int(i in (0, 1))
        header[i][1] = int(i == 2)
        header[i][2] = int(i == 1)
    specification = SimpleNamespace(
        code=0, good=False, low=tuple(map(tuple, header)),
        template=SimpleNamespace(q=3, rank=2, preparation=identity))
    program = records.Program.fixture(indices, residues, size, 1, [(1, 0, 2, 0, 0, 0)] * depth)
    fields = records.Fields.fixture(indices, residues, [(0, [[0] * 64 for _ in range(64)])
                                                       for _ in range(depth)])
    return indices, residues, ring, modulus, specification, program, fields


def literal_case(modules, depth):
    words, records, controller = modules
    indices, residues, ring, modulus, specification, program, fields = literal_setup(modules, depth)
    before = bytes(program.tape.cells), bytes(fields.tape.cells)
    coordinate, expected = indices.zero(), residues.literal(1 if depth == 0 else 2)
    entry = set(indices.live), set(residues.live)
    original_inspect = words.Word.inspect
    words.Word.inspect = lambda _word: need(False, "runtime fixture decoding forbidden")
    try:
        callback = controller.Callback(ring, indices, program, fields, {0: specification}, 0,
                                       allow_fallback=True, leaf=True)
        original_fallback = callback.matrices.fallback
        permutations = []

        def fallback(projector):
            diagonal, permutation = original_fallback(projector)
            need(permutation[0] == 1, "two actual GL64 ancestor requests")
            permutations.append(permutation[0])
            return diagonal, permutation

        callback.matrices.fallback = fallback
        with Census(records, (callback.pending, callback.values), direct=True) as census:
            result = callback.weight(coordinate)
            need(ring.raw.compare(result, expected) == 0, "literal GL64 returned coefficient")
            residues.free(result)
            callback.close()
            census.scan()
            need(census.live == 0 and all(tape.head == 1 for tape in census.tapes),
                 "GL64 serialized cleanup and head restoration")
    finally:
        words.Word.inspect = original_inspect
    need(entry == (set(indices.live), set(residues.live)), "GL64 numerical ownership restored")
    need(before == (bytes(program.tape.cells), bytes(fields.tape.cells)) and
         program.tape.head == fields.tape.head == 1, "serialized program/fields preserved")
    live, backing = bound(depth, indices.bits, residues.bits)
    need(census.peak == live and census.backing_peak <= backing, "literal GL64 saturation")
    need(len(permutations) == 2 ** depth - 1, "complete binary fallback count")
    for tape in (program.tape, fields.tape):
        tape.clear()
    indices.free(coordinate)
    residues.free(expected)
    ring.close()
    residues.free(modulus)
    need(not indices.live and not residues.live, "literal fixture complete cleanup")
    return {"depth": depth, "I": indices.bits, "R": residues.bits,
            "peak": census.peak, "bound": live, "backing": census.backing_peak,
            "backing_bound": backing, "fallback_calls": len(permutations),
            "expected_coefficient": 1 if depth == 0 else 2, "writes": census.writes}


def verify():
    modules = load_source()
    cases = []
    for depth in range(4):
        for modes in itertools.product("GBLRTU", repeat=depth):
            for residue_bits in (4, 32):
                cases.append(run_case(modules, "".join(modes), residue_bits))
    for depth in (4, 5, 6):
        for residue_bits in (4, 128):
            cases.append(run_case(modules, "B" * depth, residue_bits))
    sharp = [case for case in cases if case["modes"] and set(case["modes"]) == {"B"}]
    need(all(case["peak"] == case["bound"] for case in sharp), "binary grammar attains live bound")
    need(any(case["backing"] > case["peak"] + 4 for case in sharp),
         "retained backing is not the live-symbol bound")
    controls = rejection_controls(modules)
    literal = [literal_case(modules, depth) for depth in range(3)]
    return {"status": "PASS_SELECTED_CONTINUATION_STORAGE", "source_head": sources(),
            "synthetic_cases": len(cases), "sharp_binary_cases": len(sharp),
            "observed_stack_writes": sum(case["writes"] for case in cases),
            "observed_pops": sum(case["pops"] for case in cases),
            "rejection_controls": controls,
            "literal_gl64": literal,
            "largest_binary": [case for case in cases if case["modes"] == "B" * 6],
            "scope": "Four continuation tapes per evaluator; all-depth written proof, synthetic control and literal GL64 fixtures. No supplier admission."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--sources-only", action="store_true")
    args = parser.parse_args()
    if args.sources_only:
        print(sources())
        return
    result = verify()
    if not args.emit:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        check_receipt(result, expected)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
