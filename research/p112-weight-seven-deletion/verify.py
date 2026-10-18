#!/usr/bin/env python3
"""Replay the P112 nine-piece obstruction and its weight-seven application."""

import argparse
import hashlib
import json
from collections import Counter
from itertools import combinations
from pathlib import Path

from geometry import (canonical, chamber_receipt, dot, flat_capacity, require,
                      root_data, root_plane_receipt)
from obstruction import application, coordinate_bound

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
DATA = "research/one-sided-six-multisets/data/data.txt"
RETAINED_PATHS = ("geometry.py", "vendor/COORDINATE-PROOF.md", "vendor/bk2b.py",
                  "vendor/TWOSIDE-NOTES.md")


def bound_sources():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    rows = sources["retained_sources"]
    require(tuple(row["local_path"] for row in rows) == RETAINED_PATHS,
            "retained-source inventory")
    for row in rows:
        path = PACKAGE / row["local_path"]
        require(path.is_file() and not path.is_symlink()
                and path.stat().st_size <= 100_000, "missing/large retained source")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(digest == row["sha256"], "changed retained source")
    return {row["local_path"]: row["sha256"] for row in rows}


def bind_data(path, points, labels):
    require(path.is_file() and not path.is_symlink()
            and path.stat().st_size <= 2_000_000, "missing/large P112 input")
    raw = path.read_bytes()
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pins = [row for row in sources["files"] if row["usage"] == "input"]
    require(len(pins) == 1 and pins[0]["path"] == DATA, "live-input inventory")
    digest = hashlib.sha256(raw).hexdigest()
    require(digest == pins[0]["sha256"], "changed P112 input")
    rows = raw.decode("utf-8").splitlines()
    require(len(rows) >= 114, "truncated P112 input")
    require(tuple(map(int, rows[0].split())) == labels, "P112 label binding")
    require(tuple(tuple(map(int, row.split())) for row in rows[2:114]) == points,
            "P112 root binding")
    return digest


def simplex_control(roots, points):
    """A literal A5 fixture, not an enumeration of every root simplex."""
    vertices = [(0,) * 8]
    for i in range(1, 6):
        vertex = [0] * 8
        vertex[0], vertex[i] = -2, 2
        vertices.append(tuple(vertex))
    edges = [canonical(tuple(x - y for x, y in zip(a, b, strict=True)))
             for a, b in combinations(vertices, 2)]
    require(len(set(edges)) == 15 and all(edge in roots for edge in edges),
            "A5 fixture edges")
    histogram = Counter()
    for point in points:
        values = [dot(point, vertex) for vertex in vertices]
        histogram[sum(a != b for a, b in combinations(values, 2))] += 1
    require(max(histogram) == 9, "nine-edge sharpness")
    return {"vertices": vertices,
            "live_edge_histogram": {str(k): v for k, v in sorted(histogram.items())}}


def endpoint_controls():
    """Exhaust every equality pattern on six endpoints, with zero distinguished."""
    from itertools import product

    histogram = Counter()
    for values in product(range(7), repeat=6):
        nonzero = sum(value != 0 for value in values)
        unequal = sum(a != b for a, b in combinations(values, 2))
        require(unequal <= 4 * nonzero + 1, "coordinate inequality")
        histogram[nonzero] += 1
    boundary = coordinate_bound(26, [20] * 6)
    require(not boundary["excluded"] and boundary["margin"] == -5,
            "losing support boundary")
    return {"value_assignments": sum(histogram.values()),
            "nonzero_histogram": {str(k): v for k, v in sorted(histogram.items())},
            "losing_small_support_26": boundary}


def receipt():
    retained = bound_sources()
    roots, points, labels, coordinates = root_data()
    return {"schema": "p112-weight-seven-deletion/v1", "retained_sources": retained,
            "input_sha256": bind_data(ROOT / DATA, points, labels),
            "chamber": chamber_receipt(roots, points, coordinates),
            "root_planes": root_plane_receipt(roots),
            "flat_capacities": [flat_capacity(labels, d) for d in (5, 6)],
            "simplex_control": simplex_control(roots, points),
            "endpoint_controls": endpoint_controls(), "application": application()}


def publish_receipt(result, output):
    serialized = json.dumps(result, indent=2) + "\n"
    if output is None:
        expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
        require(json.loads(serialized) == expected, "committed receipt differs")
        return
    output = output.expanduser().resolve()
    require(not output.is_relative_to(ROOT), "output must be outside checkout")
    with output.open("x", encoding="utf-8") as stream:
        stream.write(serialized)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a new external receipt")
    args = parser.parse_args()
    result = receipt()
    publish_receipt(result, args.output)
    flats = sum(row["subspaces"] for row in result["flat_capacities"])
    print("PASS_P112_WEIGHT_SEVEN_DELETION new_profiles=1 margin=11 "
          f"flats={flats} errors=0")


if __name__ == "__main__":
    main()
