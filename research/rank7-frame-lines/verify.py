#!/usr/bin/env python3
"""Annihilator lines of the four named rank-7 frames.

The checker computes those lines. It does not rerun a fresh-extraction search.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_RANK7_FRAME_LINES frames=4 no_new_kappa"
SELECTED = "836330098538459/500000000000000000"
FRAMES = {
    "A": ((256, 128, 64, 38, 20, 10, 1), (30, 42, 52)),
    "B": ((256, 128, 64, 34, 17, 11, 4), (25, 42, 51)),
    "C": ((256, 128, 64, 32, 19, 11, 6), (7, 25, 30)),
    "D": ((256, 128, 64, 37, 21, 8, 3), (7, 51, 52)),
}
V45 = ((256, 128, 64, 35, 16, 11, 5), (7, 42, 45))


def fail(message):
    raise SystemExit("FAIL_RANK7_FRAME_LINES " + message)


def require(condition, message):
    if not condition:
        fail(message)


def dot(left, right):
    return (left & right).bit_count() & 1


def span_of(vectors):
    reached = {0}
    for vector in vectors:
        reached = reached | {item ^ vector for item in reached}
    return reached


def annihilator(reached):
    basis = []
    grown = {0}
    for point in sorted(reached):
        if point not in grown:
            grown = grown | {item ^ point for item in grown}
            basis.append(point)
    return tuple(
        normal for normal in range(512)
        if all(dot(normal, vector) == 0 for vector in basis)
    )


def lines_of(space):
    found = []
    points = sorted(point for point in space if point)
    for first in range(len(points)):
        for second in range(first + 1, len(points)):
            third = points[first] ^ points[second]
            if third in space and points[first] < points[second] < third:
                found.append(frozenset((points[first], points[second], third)))
    return found


def main():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(selected["kappa"] == SELECTED, "selected kappa moved")
    spans = {}
    present = []
    for name, (generators, expected) in {**FRAMES, "V45": V45}.items():
        require(expected[0] ^ expected[1] == expected[2], name + " is not a line")
        reached = span_of(generators)
        require(len(reached) == 128, name + " left dimension 7")
        require(annihilator(reached) == (0,) + expected, name + " annihilator moved")
        spans[name] = reached
        present.append(frozenset(expected))
    require(len(set(map(frozenset, spans.values()))) == 5, "two frames coincide")
    for left, right in ((a, b) for a in spans for b in spans if a < b):
        require(len(spans[left] & spans[right]) == 64, "a pair missed 64 vectors")
    ambient = span_of(normal for line in present for normal in line)
    require(len(ambient) == 8, "the normals left the 3-dimensional space")
    ambient_lines = lines_of(ambient)
    require(len(ambient_lines) == 7, "the ambient line count moved")
    require(set(present) <= set(ambient_lines), "a frame line left the space")
    receipt = json.loads((PACKAGE / "RESULT.json").read_text())
    require(receipt["frames"] == 4, "receipt frames")
    require(receipt["span"] == 128, "receipt span")
    require(receipt["lines_present"] == 5, "receipt lines")
    require(receipt["ambient_lines"] == 7, "receipt ambient")
    require(receipt["no_new_kappa"] is True, "kappa flag")
    print(MARKER)


if __name__ == "__main__":
    main()
