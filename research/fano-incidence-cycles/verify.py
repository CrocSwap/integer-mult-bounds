#!/usr/bin/env python3
"""Six-cycles in the Fano point-line graph.

The checker enumerates this incidence graph. It does not replay a centre window.
"""

import hashlib
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_FANO_INCIDENCE_CYCLES cycles=28 no_new_kappa"
LINES = ((0, 1, 3), (1, 2, 4), (2, 3, 5), (3, 4, 6), (4, 5, 0), (5, 6, 1), (6, 0, 2))


def fail(message):
    raise SystemExit("FAIL_FANO_INCIDENCE_CYCLES " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def incidence():
    adjacent = defaultdict(set)
    for index, line in enumerate(LINES):
        for point in line:
            adjacent[point].add(7 + index)
            adjacent[7 + index].add(point)
    return adjacent


def canonical(cycle):
    rotations = []
    for start in range(6):
        rotations.append(cycle[start:] + cycle[:start])
    reversed_cycle = cycle[::-1]
    for start in range(6):
        rotations.append(reversed_cycle[start:] + reversed_cycle[:start])
    return min(rotations)


def six_cycles(adjacent):
    found = set()

    def walk(path):
        if len(path) == 6:
            if path[0] in adjacent[path[-1]] and len(set(path)) == 6:
                found.add(canonical(path))
            return
        for nxt in adjacent[path[-1]]:
            if nxt not in path:
                walk(path + (nxt,))

    for start in range(14):
        walk((start,))
    return found


def evaluate():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")

    require(len(LINES) == 7 and all(len(line) == 3 for line in LINES), "the line count moved")
    for left in range(7):
        for right in range(left + 1, 7):
            contain = [line for line in LINES if left in line and right in line]
            require(len(contain) == 1, "a point pair left its line")
    for left in range(7):
        for right in range(left + 1, 7):
            meet = set(LINES[left]) & set(LINES[right])
            require(len(meet) == 1, "a line pair left its point")

    adjacent = incidence()
    require(all(len(adjacent[vertex]) == 3 for vertex in range(14)), "a degree moved")
    cycles = six_cycles(adjacent)
    require(len(cycles) == 28, "the six-cycle count moved")
    through = [0] * 14
    for cycle in cycles:
        for vertex in cycle:
            through[vertex] += 1
    require(through == [12] * 14, "a vertex left its twelve cycles")
    require(3 * (3 - 1) ** 2 == 12, "the degree formula moved")
    require(14 * 12 == 28 * 6, "the cycle handshaking moved")
    return {
        "points": 7,
        "lines": 7,
        "degree": 3,
        "six_cycles": 28,
        "cycles_per_vertex": 12,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
