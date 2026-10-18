#!/usr/bin/env python3
"""Source-bound P112 unequal-endpoint deletion replay. Apache-2.0."""

# Copyright 2026 Nick Petalas

import argparse
import hashlib
import json
import sys
from collections import Counter
from itertools import combinations, product
from pathlib import Path

from ledger import coordinate_invoice, historical_inventory, require

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
PREDECESSOR = "research/p112-weight-seven-deletion"
INPUTS = ("research/one-sided-six-multisets/data/data.txt",
          f"{PREDECESSOR}/geometry.py",
          f"{PREDECESSOR}/vendor/COORDINATE-PROOF.md",
          f"{PREDECESSOR}/vendor/bk2b.py")


def bound_inputs():
    pins = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    rows = [row for row in pins["files"] if row["usage"] == "input"]
    require(tuple(row["path"] for row in rows) == INPUTS, "input inventory differs")
    result = {}
    for row in rows:
        path = ROOT / row["path"]
        require(path.is_file() and not path.is_symlink()
                and path.stat().st_size <= 2_000_000, "missing/large input")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(digest == row["sha256"], "input hash differs")
        result[row["path"]] = digest
    return result


def geometric_receipt():
    """Reuse the unchanged, authenticated module, not a new geometry census."""
    sys.path.insert(0, str(ROOT / PREDECESSOR))
    try:
        import geometry
    finally:
        sys.path.pop(0)
    roots, points, labels, coordinates = geometry.root_data()
    raw = (ROOT / INPUTS[0]).read_text(encoding="utf-8").splitlines()
    require(tuple(map(int, raw[0].split())) == labels, "P112 label binding")
    require(tuple(tuple(map(int, row.split())) for row in raw[2:114]) == points,
            "P112 coordinate binding")
    return {"chamber": geometry.chamber_receipt(roots, points, coordinates),
            "root_planes": geometry.root_plane_receipt(roots),
            "flat_capacities": [geometry.flat_capacity(labels, d) for d in (5, 6)]}


def endpoint_receipt():
    """Seven symbols realize every equality pattern of six values and zero."""
    histogram = Counter()
    for values in product(range(7), repeat=6):
        nonzero = sum(value != 0 for value in values)
        unequal = sum(a != b for a, b in combinations(values, 2))
        require(unequal <= 4 * nonzero + 1, "endpoint inequality")
        histogram[nonzero] += 1
    losing = coordinate_invoice(28, (20,) * 6)
    require(not losing["excluded"] and losing["margin"] == -21,
            "uniform-endpoint losing control")
    return {"equality_assignments": sum(histogram.values()),
            "nonzero_histogram": {str(k): v for k, v in sorted(histogram.items())},
            "uniform_endpoint_control": losing}


def receipt():
    pins = bound_inputs()
    return {"schema": "p112-unequal-endpoint-deletion/v1", "input_sha256": pins,
            "geometry": geometric_receipt(), "endpoints": endpoint_receipt(),
            "historical_inventory": historical_inventory()}


def publish(result, output):
    serialized = json.dumps(result, indent=2) + "\n"
    if output is None:
        expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
        require(result == expected, "committed receipt differs")
        return
    require(output.is_absolute(), "output must be absolute")
    output = output.resolve()
    require(not output.is_relative_to(ROOT), "output must be outside checkout")
    with output.open("x", encoding="utf-8") as stream:
        stream.write(serialized)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="new absolute external receipt")
    args = parser.parse_args()
    publish(receipt(), args.output)
    print("PASS_P112_UNEQUAL_ENDPOINT_DELETION profiles=2 margin=11 errors=0")


if __name__ == "__main__":
    main()
