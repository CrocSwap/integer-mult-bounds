"""Replay the finite geometry, five ten-piece exclusions and overlap controls."""

import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path

from beta import beta_receipt
from geometry import (canonical, chamber_receipt, dot, flat_capacity, require,
                      root_data, root_plane_receipt)

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
DATA = "research/one-sided-six-multisets/data/data.txt"


def bind_data(path, points, labels):
    require(path.is_file() and path.stat().st_size <= 2_000_000, "missing/large P112 input")
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


def simplex_control(roots, points):
    """Sharp fixture, supplementary to the universal proof in PROOF.md."""
    vertices = [(0,) * 8]
    for i in range(1, 6):
        vertex = [0] * 8
        vertex[0], vertex[i] = -2, 2
        vertices.append(tuple(vertex))
    edges = [canonical(tuple(x - y for x, y in zip(a, b, strict=True)))
             for a, b in combinations(vertices, 2)]
    require(len(set(edges)) == 15 and all(edge in roots for edge in edges), "A5 fixture")
    histogram = [0] * 16
    for point in points:
        values = [dot(point, vertex) for vertex in vertices]
        count = sum(a != b for a, b in combinations(values, 2))
        histogram[count] += 1
    require(max(i for i, n in enumerate(histogram) if n) == 9, "nine-edge sharpness")
    return {"vertices": vertices, "histogram": histogram}


def receipt():
    roots, points, labels, coordinates = root_data()
    return {"schema": "p112-ten-piece-simplex/v1",
            "input_sha256": bind_data(ROOT / DATA, points, labels),
            "chamber": chamber_receipt(roots, points, coordinates),
            "root_planes": root_plane_receipt(roots),
            "flat_capacities": [flat_capacity(labels, d) for d in (5, 6)],
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
    rows = result["beta"]["new_exclusions"]
    margins = ",".join(str(row["margin"]) for row in rows)
    flats = sum(row["subspaces"] for row in result["flat_capacities"])
    print(f"PASS_P112_TEN_PIECE_SIMPLEX new_exclusions={len(rows)} "
          f"margins={margins} flats={flats} errors=0")


if __name__ == "__main__":
    main()
