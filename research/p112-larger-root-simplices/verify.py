"""Replay larger-simplex geometry, source bindings and the three exclusions."""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from simplex import TARGETS, cover_audit, simplex_fixture, survivor_rows, target_bound
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


def bounded_bytes(path, limit=2_000_000):
    require(path.is_file() and not path.is_symlink() and path.stat().st_size <= limit,
            f"missing, linked or oversized input: {path}")
    return path.read_bytes()


def bind_sources(package=PACKAGE):
    sources = json.loads(bounded_bytes(package / "SOURCES.json"))
    retained = sources["retained_files"]
    require(1 <= len(retained) <= 10, "invalid retained-source inventory")
    require(len({row["local_path"] for row in retained}) == len(retained),
            "duplicate retained source")
    for row in retained:
        path = Path(row["local_path"])
        require(len(path.parts) == 2 and path.parts[0] == "vendor" and ".." not in path.parts,
                "invalid retained-source path")
        raw = bounded_bytes(package / path)
        require(hashlib.sha256(raw).hexdigest() == row["sha256"],
                f"changed retained source: {path}")
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(blob == row["git_blob"], f"changed retained Git bytes: {path}")
    return sources


def bind_data(path, points, labels, sources):
    pins = [row for row in sources["files"] if row["usage"] == "input"]
    require(len(pins) == 1 and pins[0]["path"] == DATA, "live-input inventory")
    raw = bounded_bytes(path)
    digest = hashlib.sha256(raw).hexdigest()
    require(digest == pins[0]["sha256"], "changed P112 input")
    rows = raw.decode("utf-8").splitlines()
    require(len(rows) >= 114, "truncated P112 input")
    require(tuple(map(int, rows[0].split())) == labels, "P112 label binding")
    require(tuple(tuple(map(int, row.split())) for row in rows[2:114]) == points,
            "P112 root binding")
    return digest


def predecessor_table():
    result = subprocess.run([sys.executable, "-I", "-B", str(PACKAGE / "vendor/bk2b.py")],
                            cwd=PACKAGE, capture_output=True, text=True, check=True,
                            timeout=120)
    require(not result.stderr and len(result.stdout) <= 4096, "unexpected predecessor output")
    rows = [tuple(map(int, line.split())) for line in result.stdout.splitlines()]
    require(len(rows) == 24 and all(len(row) == 4 for row in rows), "incomplete original table")
    require([(r[0], r[1]) for r in rows] == [(b, t) for b in range(5, 9) for t in range(1, 7)],
            "original table cell order")
    return rows


def exclusion_receipt(table):
    rows = []
    for b, expected in ((6, 69), (7, 154), (8, 251)):
        survivors = survivor_rows(b)
        require(len(survivors) == expected and TARGETS[b] in survivors,
                "target is not in the stated original residue")
        require(next(r[2] for r in table if r[:2] == (b, 4)) == len(survivors),
                "original and new survivor counts disagree")
        audit = cover_audit(TARGETS[b])
        require(audit["minimum_separate_deletion_budget"] == 14
                and audit["rank_four_anchor_minimum_budget"] is None,
                "prior cover/anchor overlap boundary changed")
        rows.append({**target_bound(b), "original_cell_survivors": len(survivors),
                     "weight_cover_audit": audit})
    require([r["margin"] for r in rows] == [9, 4, 12], "three contradiction margins")
    return rows


def receipt(data_path=ROOT / DATA):
    sources = bind_sources()
    roots, points, labels, coordinates = root_data()
    digest = bind_data(data_path, points, labels, sources)
    table = predecessor_table()
    return {"schema": "p112-larger-root-simplices/v1", "input_sha256": digest,
            "chamber": chamber_receipt(roots, points, coordinates),
            "root_planes": root_plane_receipt(roots),
            "flat_capacities": [flat_capacity(labels, d) for d in (5, 6)],
            "fixtures": {str(b): simplex_fixture(roots, points, b) for b in TARGETS},
            "original_survivor_table": table, "exclusions": exclusion_receipt(table)}


def check_receipt(actual, expected):
    # Canonical JSON also normalizes the original table's internal tuples.
    require(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "committed mathematical receipt differs")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a new external receipt")
    args = parser.parse_args()
    result = receipt()
    if args.output is None:
        check_receipt(result, json.loads(bounded_bytes(PACKAGE / "RESULT.json")))
    else:
        path = args.output.expanduser().resolve()
        require(not path.is_relative_to(ROOT), "receipt output must be outside checkout")
        with path.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    print("PASS_LARGER_ROOT_SIMPLICES margins=9,4,12 flats=4097782 root_pairs=7140")


if __name__ == "__main__":
    main()
