#!/usr/bin/env python3
"""Literal numerical-word lifetime checks against independent integer oracles."""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

BOUNDS = {"divide": 4, "add": 2, "subtract": 2,
          "negate": 3, "multiply": 4, "inverse": 10}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def admit_sources():
    records = json.loads((ROOT / "SNAPSHOTS.json").read_text())
    require(records["source_pr"] == 2697 and records["source_commit"] ==
            "a53fdf4bcbe33c6732f0bec1badc8c023380f9d1", "scientific dependency")
    require(len(records["files"]) == 2, "complete snapshot inventory")
    require({r["local_path"] for r in records["files"]} ==
            {"vendor/words.py", "vendor/NOTICE.md"}, "snapshot paths")
    original_paths = {"vendor/words.py": "research/selected-bit-node/vendor/words.py",
                      "vendor/NOTICE.md": "research/selected-bit-node/NOTICE.md"}
    for record in records["files"]:
        require(record["source_path"] == original_paths[record["local_path"]],
                "original source path")
        payload = (ROOT / record["local_path"]).read_bytes()
        require(hashlib.sha256(payload).hexdigest() == record["sha256"],
                "snapshot SHA256: " + record["local_path"])
        header = f"blob {len(payload)}\0".encode()
        require(hashlib.sha1(header + payload).hexdigest() == record["git_blob"],
                "snapshot Git blob: " + record["local_path"])


def authenticated_arithmetic():
    """Authenticate snapshot bytes before executing any predecessor code."""
    admit_sources()
    sys.path.insert(0, str(ROOT / "vendor"))
    from words import BLANK, Arena, Ring, Unsigned
    return Arena, BLANK, Ring, Unsigned


Arena, BLANK, Ring, Unsigned = authenticated_arithmetic()


class TrackedArena(Arena):
    """Observe completed allocations, where occupied-word maxima occur."""
    def __init__(self, bits):
        super().__init__(bits, capacity=64)
        self.entry = 0
        self.peak = 0
        self.budget = 64
        self.census = False
        self.occupied_peak = 0

    def zero(self):
        word = super().zero()
        live = len(self.live)
        self.peak = max(self.peak, live)
        require(live <= self.entry + self.budget, "scratch word budget")
        if self.census:
            occupied = sum(cell != BLANK for item in self.words
                           for cell in item.cells[1:])
            occupied += sum(cell != BLANK for cell in self.template.cells[1:])
            require(occupied == (live + 1) * (self.bits + 1),
                    "direct occupied-cell census")
            self.occupied_peak = max(self.occupied_peak, occupied)
        return word


def expected(operation, modulus, x, y):
    if operation == "divide":
        return divmod(x, y)
    if operation == "add":
        return (x + y) % modulus
    if operation == "subtract":
        return (x - y) % modulus
    if operation == "negate":
        return (-x) % modulus
    if operation == "multiply":
        return (x * y) % modulus
    require(operation == "inverse", "known arithmetic operation")
    return pow(x, -1, modulus) if math.gcd(x, modulus) == 1 else None


def execute(operation, ring, a, b):
    if operation == "divide":
        return Unsigned(ring.arena).divmod(a, b)
    if operation == "add":
        return ring.add(a, b)
    if operation == "subtract":
        return ring.subtract(a, b)
    if operation == "negate":
        return ring.negate(a)
    if operation == "multiply":
        return ring.multiply(a, b)
    require(operation == "inverse", "known arithmetic operation")
    return ring.inverse(a)


def check_case(operation, modulus, x, y=0, *, alias=False,
               padding=0, census=False, budget=None):
    require(operation in BOUNDS and 2 <= modulus <= 65535, "finite fixture modulus")
    require(0 <= padding <= 7, "bounded borrowed padding")
    arena = TrackedArena(modulus.bit_length() + 1)
    mod = arena.literal(modulus)
    ring = Ring(mod)
    a = arena.literal(x)
    b = a if alias or operation in ("negate", "inverse") else arena.literal(y)
    extra = [arena.literal(i % modulus) for i in range(padding)]
    protected = frozenset(arena.live)
    before = {slot: bytes(arena.words[slot].cells) for slot in protected}
    arena.entry = arena.peak = len(protected)
    arena.budget = BOUNDS[operation] if budget is None else budget
    arena.census = census
    result = execute(operation, ring, a, b)
    outputs = result if isinstance(result, tuple) else (() if result is None else (result,))
    observed = tuple(word.inspect() for word in outputs)
    observed = observed if operation == "divide" else (observed[0] if outputs else None)
    require(observed == expected(operation, modulus, x, x if alias else y),
            "independent integer result")
    require(len(arena.live) == len(protected) + len(outputs), "result ownership")
    for slot in protected:
        require(bytes(arena.words[slot].cells) == before[slot] and
                arena.words[slot].head == 1, "borrowed operand preservation")
    peak = arena.peak - arena.entry
    occupied = arena.occupied_peak
    for word in outputs:
        arena.free(word)
    require(frozenset(arena.live) == protected, "scratch cleanup")
    arena.census = False
    arena.entry, arena.budget = 0, 64
    arena.free_many(a, *extra)
    if b is not a:
        arena.free(b)
    ring.close()
    arena.free(mod)
    require(not arena.live, "fixture ownership cleanup")
    require(all(cell == BLANK for word in arena.words for cell in word.cells[1:]),
            "freed words are erased")
    return {"peak": peak, "occupied": occupied, "borrowed": len(protected),
            "bits": arena.bits, "result": observed}


def finite_census():
    counts = {name: 0 for name in BOUNDS}
    peaks = {name: 0 for name in BOUNDS}
    for modulus in range(2, 20):
        for x in range(modulus):
            for name in ("negate", "inverse"):
                case = check_case(name, modulus, x)
                counts[name] += 1
                peaks[name] = max(peaks[name], case["peak"])
            for y in range(modulus):
                for name in ("add", "subtract", "multiply"):
                    case = check_case(name, modulus, x, y)
                    counts[name] += 1
                    peaks[name] = max(peaks[name], case["peak"])
        for x in range(2 * modulus):
            for y in range(1, modulus):
                case = check_case("divide", modulus, x, y)
                counts["divide"] += 1
                peaks["divide"] = max(peaks["divide"], case["peak"])
    require(peaks == BOUNDS, "all six scratch bounds attained")
    return counts, peaks


def alias_and_width_cases():
    count = 0
    for modulus in (5, 9, 17, 33, 257, 4097, 65535):
        for name in ("add", "subtract", "multiply", "divide"):
            check_case(name, modulus, 2, alias=True, census=True, padding=7)
            count += 1
        for x in (0, 1, 2, modulus - 1):
            check_case("inverse", modulus, x, census=True, padding=7)
            count += 1
    return count


def rollback_control():
    arena = TrackedArena(4)
    mod = arena.literal(5)
    ring = Ring(mod)
    a = arena.literal(2)
    protected = frozenset(arena.live)
    arena.entry = arena.peak = len(protected)
    arena.budget = 9
    try:
        ring.inverse(a)
    except ValueError as error:
        require(str(error) == "scratch word budget", "named underbudget failure")
    else:
        raise ValueError("nine-word inverse budget accepted")
    require(len(arena.live) > len(protected), "failure requires caller rollback")
    arena.rollback(protected)
    require(frozenset(arena.live) == protected, "explicit rollback ownership")
    require(a.inspect() == 2 and mod.inspect() == 5 and ring.one.inspect() == 1,
            "rollback preserves borrowed values")
    arena.entry, arena.budget = 0, 64
    arena.free(a)
    ring.close()
    arena.free(mod)
    require(not arena.live, "rollback fixture cleanup")


def verify():
    admit_sources()
    counts, peaks = finite_census()
    wide = alias_and_width_cases()
    witness = check_case("inverse", 5, 2, census=True)
    require(witness == {"peak": 10, "occupied": 70, "borrowed": 3,
                        "bits": 4, "result": 3}, "sharp inverse witness")
    padded = check_case("inverse", 5, 2, census=True, padding=7)
    require(padded["occupied"] == 105 and padded["peak"] == 10,
            "unrelated borrowed words remain charged")
    nonunit = check_case("inverse", 15, 6, census=True)
    require(nonunit["peak"] == 10 and nonunit["result"] is None,
            "sharp nonunit cleanup witness")
    rollback_control()
    return {"bounds": peaks, "finite_cases": counts, "alias_and_width_cases": wide,
            "inverse_witness": witness, "nonunit_peak": nonunit["peak"],
            "scope": "Arithmetic scratch only; no total caller reserve or new kappa."}


def main():
    require(sys.argv[1:] in ([], ["--write"]), "usage: verify.py [--write]")
    result = verify()
    path = ROOT / "RESULT.json"
    if sys.argv[1:] == ["--write"]:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(json.loads(path.read_text()) == result, "fixed arithmetic receipt")
    print("PASS_SELECTED_WORD_SCRATCH inverse=10_words sharp_M5_a2 "
          f"cases={sum(result['finite_cases'].values())} "
          f"alias_width={result['alias_and_width_cases']} no_new_kappa")


if __name__ == "__main__":
    main()
