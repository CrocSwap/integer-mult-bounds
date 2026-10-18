"""Replay exact dependencies and controls for the P112 quotient-parity theorem."""

import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path

from geometry import (
    canonical,
    chamber_receipt,
    dot,
    flat_capacity,
    require,
    root_data,
    root_plane_receipt,
)
from quotient import application, matching_receipt, original_filter_control

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
DATA = "research/one-sided-six-multisets/data/data.txt"


def bind_data(path, points, labels):
    require(path.is_file() and path.stat().st_size <= 2_000_000, "missing/large input")
    raw = path.read_bytes()
    pins = json.loads((PACKAGE / "SOURCES.json").read_text())["files"]
    live = [row for row in pins if row["usage"] == "input"]
    require(len(live) == 1 and live[0]["path"] == DATA, "live-input inventory")
    digest = hashlib.sha256(raw).hexdigest()
    require(digest == live[0]["sha256"], "changed P112 input")
    rows = raw.decode("utf-8").splitlines()
    require(len(rows) >= 114, "truncated P112 input")
    require(tuple(map(int, rows[0].split())) == labels, "label binding")
    require(tuple(tuple(map(int, row.split())) for row in rows[2:114]) == points,
            "root binding")
    return digest


def simplex_control(roots, points):
    vertices = [(0,) * 8]
    for i in range(1, 6):
        vertex = [0] * 8
        vertex[0], vertex[i] = -2, 2
        vertices.append(tuple(vertex))
    edges = [canonical(tuple(x - y for x, y in zip(a, b, strict=True)))
             for a, b in combinations(vertices, 2)]
    require(len(set(edges)) == 15 and all(e in roots for e in edges), "A5 fixture")
    histogram = [0] * 16
    for point in points:
        values = [dot(point, vertex) for vertex in vertices]
        histogram[sum(a != b for a, b in combinations(values, 2))] += 1
    require(max(i for i, n in enumerate(histogram) if n) == 9, "A5 incidence cap")
    return {"vertices": vertices, "incidence_histogram": histogram}


def receipt():
    roots, points, labels, coordinates = root_data()
    return {"schema": "p112-quotient-parity/v1",
            "input_sha256": bind_data(ROOT / DATA, points, labels),
            "chamber": chamber_receipt(roots, points, coordinates),
            "root_planes": root_plane_receipt(roots),
            "five_flat_capacity": flat_capacity(labels, 5),
            "simplex_control": simplex_control(roots, points),
            "odd_matching": matching_receipt(), "application": application(),
            "original_filter_control": original_filter_control()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a new external receipt")
    args = parser.parse_args()
    result = receipt()
    if args.output is None:
        require(json.loads(json.dumps(result))
                == json.loads((PACKAGE / "RESULT.json").read_text()),
                "committed receipt differs")
    else:
        output = args.output.expanduser().resolve()
        require(not output.is_relative_to(ROOT), "output must be outside checkout")
        with output.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    print("PASS_P112_QUOTIENT_PARITY exclusions=1 margin=39 "
          "flats=3309747 root_planes=7140 matchings=232 errors=0")


if __name__ == "__main__":
    main()
