"""Reconstruct the exact geometry and compare the committed proof receipt."""

import argparse
import hashlib
import json
from pathlib import Path

from geometry import (chamber_receipt, flat_capacity, require, root_data,
                      root_plane_receipt)
from simplex import SHAPES, obstruction, simplex_receipt

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


def receipt(data_path):
    roots, points, labels, coordinates = root_data()
    digest = bind_data(data_path, points, labels)
    rows = [obstruction(*shape) for shape in SHAPES]
    require([row["contradiction_margin"] for row in rows] == [15, 1],
            "two exact contradiction margins")
    return {"schema": "p112-root-simplex-exclusion/v1", "input_sha256": digest,
            "chamber": chamber_receipt(roots, points, coordinates),
            "root_planes": root_plane_receipt(roots),
            "flat_capacities": [flat_capacity(labels, d) for d in (5, 6)],
            "simplex_control": simplex_receipt(roots, points), "exclusions": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a new receipt instead of comparing")
    args = parser.parse_args()
    result = receipt(ROOT / DATA)
    if args.output is None:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        require(result == expected, "committed mathematical receipt differs")
    else:
        output = args.output.expanduser().resolve()
        require(not output.is_relative_to(ROOT), "receipt output must be outside checkout")
        with output.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    print("PASS_ROOT_SIMPLEX_EXCLUSIONS margins=15,1 flats=4097782 root_pairs=7140")


if __name__ == "__main__":
    main()
