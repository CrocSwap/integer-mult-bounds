"""Replay support26 A4 shortening and two actual TWOSIDE exclusions."""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from a4_geometry import (
    chamber_receipt,
    flat_capacity,
    require,
    root_data,
    root_plane_receipt,
)
from model import PROFILES, a4_receipt, application, cover_audit, original_survivors

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
DATA = "research/one-sided-six-multisets/data/data.txt"
ORIGINAL = "research/p112-simplex-coordinate-bound/vendor/bk2b.py"


def read_bytes(path):
    require(
        path.is_file() and not path.is_symlink() and path.stat().st_size <= 2_000_000,
        f"missing, linked or oversized input: {path}",
    )
    return path.read_bytes()


def bind_sources(package=PACKAGE, root=ROOT):
    sources = json.loads(read_bytes(package / "SOURCES.json"))
    inputs = [r for r in sources["files"] if r["usage"] == "input"]
    require(
        {r["path"] for r in inputs} == {DATA, ORIGINAL}, "live-input inventory changed"
    )
    retained = sources["retained_files"]
    require(
        len(retained) == 1 and retained[0]["local_path"] == "a4_geometry.py",
        "retained geometry inventory changed",
    )
    for row in inputs + retained:
        path = (
            package / row["local_path"] if "local_path" in row else root / row["path"]
        )
        raw = read_bytes(path)
        require(
            hashlib.sha256(raw).hexdigest() == row["sha256"], "changed source bytes"
        )
        blob = hashlib.sha1(
            b"blob " + str(len(raw)).encode() + b"\0" + raw, usedforsecurity=False
        ).hexdigest()
        require(blob == row["git_blob"], "changed source Git bytes")
    return sources


def bind_data(points, labels):
    lines = read_bytes(ROOT / DATA).decode("utf-8").splitlines()
    require(len(lines) >= 114, "truncated P112 data")
    require(tuple(map(int, lines[0].split())) == labels, "P112 labels differ")
    require(
        tuple(tuple(map(int, line.split())) for line in lines[2:114]) == points,
        "P112 root order differs",
    )


def original_table():
    result = subprocess.run(
        [sys.executable, "-I", "-B", str(ROOT / ORIGINAL)],
        capture_output=True,
        text=True,
        check=True,
        timeout=120,
    )
    require(
        not result.stderr and len(result.stdout) <= 4096, "unexpected original output"
    )
    rows = [tuple(map(int, line.split())) for line in result.stdout.splitlines()]
    require(
        len(rows) == 24 and all(len(r) == 4 for r in rows), "incomplete original table"
    )
    require(
        [(r[0], r[1]) for r in rows]
        == [(b, t) for b in range(5, 9) for t in range(1, 7)],
        "original cell order changed",
    )
    require(
        next(r[2] for r in rows if r[:2] == (6, 3)) == 17,
        "original target-cell count changed",
    )
    return rows


def receipt():
    sources = bind_sources()
    roots, points, labels, coordinates = root_data()
    bind_data(points, labels)
    original = original_survivors()
    require(
        all(w in original for w in PROFILES), "target absent from historical residue"
    )
    return {
        "schema": "p112-a4-shortening/v1",
        "base_commit": sources["base_commit"],
        "a4": a4_receipt(roots),
        "applications": [application(w) for w in PROFILES],
        "historical_survivors": original,
        "original_table": original_table(),
        "weight_cover_audits": [cover_audit(w) for w in PROFILES],
        "chamber": chamber_receipt(roots, points, coordinates),
        "root_planes": root_plane_receipt(roots),
        "flat_capacities": [flat_capacity(labels, d) for d in (5, 6)],
    }


def check_receipt(actual, expected):
    require(
        json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
        "committed mathematical receipt differs",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, help="write a new receipt outside the checkout"
    )
    args = parser.parse_args()
    result = receipt()
    if args.output is None:
        check_receipt(result, json.loads(read_bytes(PACKAGE / "RESULT.json")))
    else:
        output = args.output.expanduser().resolve()
        require(not output.is_relative_to(ROOT), "output must be outside checkout")
        with output.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    print(
        "PASS_A4_SHORTENING support=26 exclusions=2 margins=6,14 "
        "A4_orbits=1 flats=4097782"
    )


if __name__ == "__main__":
    main()
