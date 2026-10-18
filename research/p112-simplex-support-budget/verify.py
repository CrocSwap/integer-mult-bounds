"""Replay four P112 exclusions using exact root-simplex support spectra."""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from model import application_rows, simplex_receipt
from vendor.geometry import (
    chamber_receipt,
    flat_capacity,
    require,
    root_data,
    root_plane_receipt,
)

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
DATA = "research/one-sided-six-multisets/data/data.txt"


def read_bytes(path):
    require(path.is_file() and not path.is_symlink() and path.stat().st_size <= 2_000_000,
            f"missing, linked or oversized input: {path}")
    return path.read_bytes()


def bind_sources(package=PACKAGE):
    sources = json.loads(read_bytes(package / "SOURCES.json"))
    rows = sources["retained_files"]
    require(len(rows) == 7 and len({r["local_path"] for r in rows}) == 7,
            "retained source inventory changed")
    for row in rows:
        path = Path(row["local_path"])
        require(len(path.parts) == 2 and path.parts[0] == "vendor" and ".." not in path.parts,
                "invalid retained path")
        raw = read_bytes(package / path)
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "changed retained source")
        blob = hashlib.sha1(
            b"blob " + str(len(raw)).encode() + b"\0" + raw, usedforsecurity=False
        ).hexdigest()
        require(blob == row["git_blob"], "changed retained Git bytes")
    return sources


def bind_data(path, points, labels, sources):
    pins = [row for row in sources["files"] if row["usage"] == "input"]
    require(len(pins) == 1 and pins[0]["path"] == DATA, "live-input inventory changed")
    raw = read_bytes(path)
    digest = hashlib.sha256(raw).hexdigest()
    require(digest == pins[0]["sha256"], "changed P112 data")
    lines = raw.decode("utf-8").splitlines()
    require(len(lines) >= 114, "truncated P112 input")
    require(tuple(map(int, lines[0].split())) == labels, "P112 labels differ")
    require(tuple(tuple(map(int, line.split())) for line in lines[2:114]) == points,
            "P112 roots differ")
    return digest


def predecessor_table():
    result = subprocess.run([sys.executable, "-I", "-B", str(PACKAGE / "vendor/bk2b.py")],
                            cwd=PACKAGE, capture_output=True, text=True, check=True,
                            timeout=120)
    require(not result.stderr and len(result.stdout) <= 4096, "unexpected original output")
    rows = [tuple(map(int, line.split())) for line in result.stdout.splitlines()]
    require(len(rows) == 24 and all(len(row) == 4 for row in rows), "incomplete original table")
    require([(r[0], r[1]) for r in rows] == [(b, t) for b in range(5, 9) for t in range(1, 7)],
            "original cell order changed")
    require([r[2] for r in rows if r[1] == 4 and r[0] in (6, 7)] == [69, 154],
            "original target-cell counts changed")
    return rows


def receipt():
    sources = bind_sources()
    roots, points, labels, coordinates = root_data()
    digest = bind_data(ROOT / DATA, points, labels, sources)
    simplices = simplex_receipt(roots)
    return {"schema": "p112-simplex-support-budget/v1", "input_sha256": digest,
            "simplices": simplices, "applications": application_rows(simplices["spectra"]),
            "chamber": chamber_receipt(roots, points, coordinates),
            "root_planes": root_plane_receipt(roots),
            "flat_capacities": [flat_capacity(labels, dimension) for dimension in (5, 6)],
            "original_table": predecessor_table()}


def check_receipt(actual, expected):
    require(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "committed mathematical receipt differs")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a fresh receipt outside the checkout")
    args = parser.parse_args()
    result = receipt()
    if args.output is None:
        check_receipt(result, json.loads(read_bytes(PACKAGE / "RESULT.json")))
    else:
        output = args.output.expanduser().resolve()
        require(not output.is_relative_to(ROOT), "output must be outside checkout")
        with output.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    print("PASS_SIMPLEX_SUPPORT_BUDGET exclusions=4 margins=5,5,6,6 "
          "A6_orbits=1 A7_orbits=2 flats=4097782")


if __name__ == "__main__":
    main()
