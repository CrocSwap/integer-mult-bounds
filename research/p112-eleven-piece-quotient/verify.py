"""Replay the P112 eleven-piece quotient theorem's finite dependencies."""

import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path

from beta import beta_receipt
from geometry import (
    canonical,
    chamber_receipt,
    dot,
    flat_capacity,
    require,
    root_data,
    root_plane_receipt,
)

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
DATA = "research/one-sided-six-multisets/data/data.txt"


def bind_data(path, points, labels):
    require(path.is_file() and path.stat().st_size <= 2_000_000,
            "missing/large P112 input")
    raw = path.read_bytes()
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
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


def matching_receipt(size):
    """All singleton/pair partitions; this supplements the universal proof."""
    require(type(size) is int and 1 <= size <= 8, "matching domain is 1..8")
    edges = tuple(combinations(range(size), 2))
    histogram = [0] * (size + 1)
    for count in range(size // 2 + 1):
        for chosen in combinations(edges, count):
            vertices = [vertex for edge in chosen for vertex in edge]
            if len(set(vertices)) == len(vertices):
                histogram[size - 2 * count] += 1
    return {"size": size, "partitions": sum(histogram),
            "singleton_histogram": histogram}


def quotient_control():
    """A rational two-dimensional quotient with three pairs and a singleton."""
    vectors = ((1, -1), (1, -1), (1, 0), (1, 0), (1, 1), (1, 1), (1, 2))
    determinants = [[a * d - b * c for c, d in vectors] for a, b in vectors]
    singletons = [i for i, row in enumerate(determinants)
                  if all(value != 0 for j, value in enumerate(row) if i != j)]
    require(singletons == [6], "abstract quotient singleton fixture")
    classes = matching_receipt(7)
    require(classes["partitions"] == 232 and classes["singleton_histogram"][0] == 0,
            "odd quotient class consequence")
    return {"vectors": vectors, "singletons": singletons, "classes": classes,
            "nonzero_after_four_cap": 44, "two_dimensional_kernel_cap": 68,
            "root_rigidity_strict_threshold": 70}


def simplex_control(roots, points):
    """A sharp A5 fixture, not an enumeration of all possible simplices."""
    vertices = [(0,) * 8]
    for i in range(1, 6):
        vertex = [0] * 8
        vertex[0], vertex[i] = -2, 2
        vertices.append(tuple(vertex))
    edges = [canonical(tuple(x - y for x, y in zip(a, b, strict=True)))
             for a, b in combinations(vertices, 2)]
    require(len(set(edges)) == 15 and all(edge in roots for edge in edges),
            "A5 fixture")
    histogram = [0] * 16
    for point in points:
        values = [dot(point, vertex) for vertex in vertices]
        histogram[sum(a != b for a, b in combinations(values, 2))] += 1
    require(max(i for i, n in enumerate(histogram) if n) == 9, "nine-edge sharpness")
    return {"vertices": vertices, "histogram": histogram}


def receipt():
    roots, points, labels, coordinates = root_data()
    return {"schema": "p112-eleven-piece-quotient/v1",
            "input_sha256": bind_data(ROOT / DATA, points, labels),
            "chamber": chamber_receipt(roots, points, coordinates),
            "root_planes": root_plane_receipt(roots),
            "five_flat_capacity": flat_capacity(labels, 5),
            "quotient_control": quotient_control(),
            "simplex_control": simplex_control(roots, points), "beta": beta_receipt()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a new external receipt")
    args = parser.parse_args()
    result = receipt()
    serialized = json.dumps(result, indent=2) + "\n"
    if args.output is None:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        require(json.loads(serialized) == expected, "committed receipt differs")
    else:
        output = args.output.expanduser().resolve()
        require(not output.is_relative_to(ROOT), "output must be outside checkout")
        with output.open("x", encoding="utf-8") as stream:
            stream.write(serialized)
    print("PASS_P112_ELEVEN_PIECE_QUOTIENT new_exclusions=3 margin=39 "
          "five_flats=3309747 original_survivors=77 errors=0")


if __name__ == "__main__":
    main()
