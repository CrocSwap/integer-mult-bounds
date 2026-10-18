#!/usr/bin/env python3
"""Exact source lifetimes and complete finite payload checks.

Ross Richardson with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parent
SNAPSHOT_SHA256 = "ada7f261c95a2766b996a7c80052920b4290391999f3c68baf8c2db35b1cceec"
MODULES = ("words", "records", "stream", "cardinality", "counts", "directory")


def require(test, message):
    if not test:
        raise ValueError(message)


def load(root=ROOT):
    raw = (root / "SNAPSHOT.json").read_bytes()
    require(hashlib.sha256(raw).hexdigest() == SNAPSHOT_SHA256, "snapshot identity")
    snapshot = json.loads(raw)
    expected = {f"vendor/{x}.py" for x in MODULES} | {"vendor/NOTICE.md"}
    require({x["path"] for x in snapshot["files"]} == expected, "complete source inventory")
    require(len(snapshot["files"]) == len(expected), "unique source inventory")
    source = {}
    for item in snapshot["files"]:
        path = root / item["path"]
        data = path.read_bytes()
        require(hashlib.sha256(data).hexdigest() == item["sha256"], "source hash: " + item["path"])
        source[path.stem] = data
    result = {}
    # Authenticate all bytes first; compile exact bytes without using pyc caches.
    for name in MODULES:
        module = types.ModuleType(name)
        module.__file__ = str(root / "vendor" / (name + ".py"))
        sys.modules[name] = module
        exec(compile(source[name], module.__file__, "exec"), module.__dict__)
        result[name] = module
    return types.SimpleNamespace(**result)


def observed_arena(words, bits):
    class Observed(words.Arena):
        def __init__(self):
            super().__init__(bits, capacity=5000)
            self.base = None
            self.peak = 0
            self.allocations = 0
            self.cell_scans = 0

        def zero(self):
            out = super().zero()
            if self.base is not None:
                excess = len(self.live) - len(self.base)
                if excess > self.peak and (excess <= 20 or excess == 4096):
                    occupied = sum(symbol != words.BLANK for word in
                                   [self.template] + [self.words[s] for s in self.live]
                                   for symbol in word.cells[1:])
                    require(occupied == (len(self.live) + 1) * (self.bits + 1),
                            "literal occupied-cell census including template")
                    self.cell_scans += 1
                self.peak = max(self.peak, excess)
                self.allocations += 1
            return out

        def start(self):
            self.base = snapshot(self)
            self.peak = self.allocations = 0
            self.cell_scans = 0

    return Observed()


def snapshot(arena):
    return {slot: (bytes(arena.words[slot].cells), arena.words[slot].head)
            for slot in arena.live}


def restored(arena):
    require(snapshot(arena) == arena.base, "borrowed live slots, values and heads restored")
    require(arena.template.head == 1, "template head restored")
    for slot in arena.available:
        word = arena.words[slot]
        require(word.head == 1 and all(x == 4 for x in word.cells[1:]), "freed slots literally erased")


def tape_data(tape):
    # Checker-only cell decoding, never used to control source execution.
    result = []
    for symbol in tape.cells[1:]:
        if symbol == 4:
            break
        result.append(symbol)
    return result


def stream_case(m, modulus, coefficient, extents, bits, callback_peak=1,
                callback_indices=0, bad_callback=None):
    arena = observed_arena(m.words, modulus.bit_length() + 1)
    index = observed_arena(m.words, 12)
    mod = arena.literal(modulus)
    ring = m.words.Ring(mod)
    for value in (0, 1, modulus + 1):
        arena.literal(value)
        index.literal(value)
    values = []
    for n in extents:
        value = m.counts.Count.literal(n)
        values.append(value.marginal())
        value.close()
    source = m.records.Tape()
    for bit in bits:
        source.append(bit)
    source.rewind()
    original = bytes(source.cells)
    arena.start()
    index.start()
    calls = []

    def prepare():
        require(snapshot(arena) == arena.base and snapshot(index) == index.base,
                "callback starts at the common numerical baseline")
        calls.append(len(arena.live))
        if bad_callback == "borrowed":
            return ring.one
        temporary = [arena.zero() for _ in range(callback_peak)]
        it = [index.zero() for _ in range(callback_indices)]
        arena.free_many(*temporary)
        index.free_many(*it)
        answer = arena.literal(coefficient)
        if bad_callback == "leak":
            arena.zero()
        if bad_callback == "different" and len(calls) == 2:
            arena.free(answer)
            answer = arena.literal((coefficient + 1) % modulus)
        return answer

    out, _ = m.stream.add_pass(source, ring, *values, prepare)
    actual = tape_data(out)
    expected = [None] * len(bits)
    before, middle, suffix = extents
    for a, x, b, y, s in itertools.product(range(before), range(modulus), range(middle),
                                         range(modulus), range(suffix)):
        old = ((((a * modulus + x) * middle + b) * modulus + y) * suffix + s)
        new = ((((a * modulus + x) * middle + b) * modulus + (y + coefficient*x) % modulus) * suffix + s)
        expected[new] = bits[old]
    require(actual == expected, "complete Boolean ADD permutation")
    require(len(calls) == 2, "split and merge each call the coefficient")
    require(bytes(source.cells) == original and source.head == 1, "input payload preserved")
    restored(arena)
    restored(index)
    require(arena.peak <= max(callback_peak, 6), "max-composed residue bound")
    require(index.peak <= callback_indices, "stream adds no index Words")
    result = {"modulus": modulus, "coefficient": coefficient, "extents": list(extents),
              "payload_bits": len(bits), "residue_peak": arena.peak,
              "index_peak": index.peak, "callback_peak": callback_peak,
              "callback_indices": callback_indices, "allocations": arena.allocations,
              "cell_scans": arena.cell_scans + index.cell_scans}
    out.clear()
    for value in values:
        value.close()
    return result


def directory_case(m, dimension, q, width, depth, old_count):
    modulus = q ** width
    arena = observed_arena(m.words, modulus.bit_length() + 1)
    index = observed_arena(m.words, 12)
    ring = m.words.Ring(arena.literal(modulus))
    vocabulary = types.SimpleNamespace(q=q, dimension=dimension, bits=2, limit=4)
    context = m.directory.Context(ring, vocabulary)
    fields = index.literal(depth)
    for n in (0, 1, modulus):
        arena.literal(n)
        index.literal(n)
    old = m.records.Tape()
    records = []
    cap = q ** (width - 1)
    for record in range(old_count):
        symbols = []
        for field in range(depth):
            code = (record + field) % vocabulary.limit
            # Independent direct record encoding; no source append_word helper.
            symbols += [(code >> j) & 1 for j in range(vocabulary.bits)] + [5]
            for coordinate in range(dimension * dimension):
                value = (record + field + coordinate) % cap
                symbols += [(value >> j) & 1 for j in range(arena.bits)] + [5]
            symbols += [6]
        records.append(symbols)
        for symbol in symbols:
            old.append(symbol)
    old.rewind()
    old_bytes = bytes(old.cells)
    count = m.counts.Count.literal(old_count)
    arena.start()
    index.start()
    output, emitted = m.directory.produce(old, fields, count, 3, context)
    expected = []
    for prefix in records:
        for highs in itertools.product(range(cap), repeat=dimension * dimension):
            expected.extend(prefix)
            expected.extend([1, 1, 5])
            for value in highs:
                expected.extend([(value >> j) & 1 for j in range(arena.bits)] + [5])
            expected.append(6)
    require(tape_data(output) == expected, "complete directory and high-field lexicographic order")
    expected_count = old_count * cap ** (dimension * dimension)
    encoded_count = sum(bit << j for j, bit in enumerate(tape_data(emitted.tape)[:-1]))
    require(encoded_count == expected_count, "complete directory multiplicity")
    require(bytes(old.cells) == old_bytes and old.head == 1, "old directory preserved")
    restored(arena)
    restored(index)
    require(arena.peak == max(dimension * dimension, 6), "sharp directory numerical peak")
    require(index.peak == 0, "directory allocates no index Words")
    result = {"dimension": dimension, "q": q, "width": width, "depth": depth,
              "old_count": old_count, "records": expected_count, "symbols": len(expected),
              "residue_peak": arena.peak, "index_peak": index.peak,
              "allocations": arena.allocations, "cell_scans": arena.cell_scans + index.cell_scans}
    output.clear()
    emitted.close()
    count.close()
    return result


def rejection(action, label):
    try:
        action()
    except (ValueError, IndexError):
        return label
    raise ValueError("control was accepted: " + label)


def calculate():
    m = load()
    streams = []
    # Every one-hot input: all Boolean inputs follow by literal bit copying.
    for modulus in (3, 5):
        n = modulus * modulus
        for coefficient in range(modulus):
            for hot in range(n):
                streams.append(stream_case(m, modulus, coefficient, (1, 1, 1),
                                           [int(j == hot) for j in range(n)]))
    basis_cases = len(streams)
    for modulus in (3, 5, 7, 9):
        for coefficient in range(modulus):
            for extents in ((2, 1, 1), (1, 2, 2), (2, 2, 3)):
                n = modulus * modulus
                for x in extents:
                    n *= x
                bits = [((j*j + 7*j + j//3 + coefficient) % 11) % 2 for j in range(n)]
                streams.append(stream_case(m, modulus, coefficient, extents, bits))
    for r, i in ((1, 0), (6, 2), (7, 3), (19, 5)):
        streams.append(stream_case(m, 5, 2, (1, 1, 1), [j % 2 for j in range(25)], r, i))
    directories = [directory_case(m, *args) for args in
                   ((1, 3, 1, 0, 1), (1, 3, 2, 2, 2), (2, 3, 2, 1, 2),
                    (2, 5, 1, 2, 2), (3, 3, 1, 1, 2), (64, 3, 1, 0, 1),
                    (64, 3, 1, 2, 2))]
    witness = stream_case(m, 5, 2, (1, 1, 1), [j % 2 for j in range(25)])
    require(witness["residue_peak"] == 6, "six-Word literal attainment")
    controls = [rejection(lambda: require(witness["residue_peak"] <= 5, "underbudget"),
                          "five-residue-stream-underbudget"),
                rejection(lambda: require(directories[-1]["residue_peak"] <= 4095, "underbudget"),
                          "4095-residue-directory-underbudget")]
    for defect in ("borrowed", "leak", "different"):
        controls.append(rejection(lambda d=defect: stream_case(m, 5, 2, (1, 1, 1),
                                  [j % 2 for j in range(25)], bad_callback=d),
                                  "callback-" + defect))
    return {"schema_version": 1, "status": "PASS", "source_snapshot_sha256": SNAPSHOT_SHA256,
            "stream_basis_cases": basis_cases, "stream_cases": len(streams),
            "stream_payload_bits": sum(x["payload_bits"] for x in streams),
            "stream_allocation_events": sum(x["allocations"] for x in streams),
            "literal_cell_scans": sum(x["cell_scans"] for x in streams + directories),
            "stream_max_without_callback_scratch": max(x["residue_peak"] for x in streams if x["callback_peak"] == 1),
            "composition_cases": streams[-4:], "sharp_stream_witness": witness,
            "directory_cases": directories, "controls_rejected": controls,
            "scope": "Successful source-level numerical content only; no total caller, backing capacity, physical cost, supplier or kappa claim."}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = calculate()
    if args.emit:
        print(json.dumps(result, indent=2))
    else:
        expected = json.loads((ROOT / "RESULT.json").read_text())
        require(canonical(result) == canonical(expected), "complete typed receipt equality")
        print("PASS_STREAM_DIRECTORY_NUMERICAL_AUDIT", result["stream_cases"], "stream cases;",
              len(result["directory_cases"]), "directory cases;", len(result["controls_rejected"]), "controls")


if __name__ == "__main__":
    main()
