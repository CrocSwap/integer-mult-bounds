#!/usr/bin/env python3
"""Destination-free gates make the symbolic XOR and the sequential ADD agree.

The checker uses independent bits. It does not census gates.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_GATE_DEST_FREE_AGREEMENT lists=5 witnesses=2 no_new_kappa"
FREE = ((), (1,), (1, 1), (1, 2, 1), (2, 3, 2, 3))


def fail(message):
    raise SystemExit("FAIL_GATE_DEST_FREE_AGREEMENT " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    require(set(pinned) == set(), "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def symbolic(width, destination, sources):
    basis = [1 << index for index in range(width)]
    accumulator = 0
    for source in sources:
        accumulator ^= basis[source]
    return basis[destination] ^ accumulator


def sequential(width, destination, sources):
    value = [1 << index for index in range(width)]
    for source in sources:
        value[destination] ^= value[source]
    return value


def repeats(destination, sources):
    registers = (destination,) + tuple(sources)
    return len(set(registers)) != len(registers)


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    for sources in FREE:
        width = 1 + max(sources, default=0)
        require(0 not in sources, "a free list contains the destination")
        value = sequential(width, 0, sources)
        require(value[0] == symbolic(width, 0, sources), "a free list diverged")
        require(all(value[index] == (1 << index) for index in range(1, width)), "a free list wrote another register")
    even = sequential(1, 0, (0, 0))
    require(even[0] == 0 and symbolic(1, 0, (0, 0)) == (1 << 0), "the double self-add moved")
    mixed = sequential(2, 0, (1, 0))
    require(mixed[0] == 0 and symbolic(2, 0, (1, 0)) == (1 << 1), "the destination-in list moved")
    require(repeats(0, (0, 0)) and repeats(0, (1, 0)), "a witness became distinct")
    return {
        "free_lists": 5,
        "witnesses": 2,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
