#!/usr/bin/env python3
"""The named V45 frame is one triple intersection.

The checker compares that span with three hyperplanes. It does not rerun a
fresh-extraction search.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_V45_TRIPLE_INTERSECTION span=128 no_new_kappa"
SELECTED = "836330098538459/500000000000000000"
GENERATORS = (256, 128, 64, 35, 16, 11, 5)
NORMALS = (7, 42, 45)


def fail(message):
    raise SystemExit("FAIL_V45_TRIPLE_INTERSECTION " + message)


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


def main():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(selected["kappa"] == SELECTED, "selected kappa moved")
    require(NORMALS[0] ^ NORMALS[1] == NORMALS[2], "the normals do not close")
    for generator in GENERATORS:
        require(all(dot(generator, normal) == 0 for normal in NORMALS), "a generator left a hyperplane")
    reached = span_of(GENERATORS)
    require(len(reached) == 128, "the span left dimension 7")
    intersection = {
        point for point in range(512)
        if all(dot(point, normal) == 0 for normal in NORMALS[:2])
    }
    require(intersection == reached, "the span missed the intersection")
    receipt = json.loads((PACKAGE / "RESULT.json").read_text())
    require(receipt["generators"] == list(GENERATORS), "receipt generators")
    require(receipt["normals"] == list(NORMALS), "receipt normals")
    require(receipt["span"] == 128, "receipt span")
    require(receipt["no_new_kappa"] is True, "kappa flag")
    print(MARKER)


if __name__ == "__main__":
    main()
