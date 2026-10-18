"""Replay the P112 eleven-piece (7,4) support-union exclusion."""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from census import application, mixed_receipt
from union import root_receipt
from vendor import mixed
from vendor.geometry import (
    chamber_receipt,
    flat_capacity,
    frame_lines,
    require,
    root_data,
    root_plane_receipt,
)

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
DATA = "research/one-sided-six-multisets/data/data.txt"


def read_bytes(path):
    require(
        path.is_file() and not path.is_symlink() and path.stat().st_size <= 2_000_000,
        f"missing, linked or oversized input: {path}",
    )
    return path.read_bytes()


def bind_sources(package=PACKAGE):
    sources = json.loads(read_bytes(package / "SOURCES.json"))
    rows = sources["retained_files"]
    require(
        len(rows) == 5 and len({row["local_path"] for row in rows}) == 5,
        "retained source inventory changed",
    )
    for row in rows:
        path = Path(row["local_path"])
        require(
            len(path.parts) == 2
            and path.parts[0] == "vendor"
            and ".." not in path.parts,
            "invalid retained path",
        )
        raw = read_bytes(package / path)
        require(
            hashlib.sha256(raw).hexdigest() == row["sha256"], "changed retained source"
        )
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
    require(
        len(lines) >= 114 and tuple(map(int, lines[0].split())) == labels,
        "P112 labels differ",
    )
    require(
        tuple(tuple(map(int, line.split())) for line in lines[2:114]) == points,
        "P112 roots differ",
    )
    return digest


def predecessor_table():
    result = subprocess.run(
        [sys.executable, "-I", "-B", str(PACKAGE / "vendor/bk2b.py")],
        cwd=PACKAGE,
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
        len(rows) == 24 and all(len(row) == 4 for row in rows), "original table shape"
    )
    require(
        [(r[0], r[1]) for r in rows]
        == [(b, t) for b in range(5, 9) for t in range(1, 7)],
        "original cell order changed",
    )
    return rows


def receipt():
    sources = bind_sources()
    roots, points, labels, coordinates = root_data()
    digest = bind_data(ROOT / DATA, points, labels, sources)
    directions, normals, norm_histogram = mixed.alphabet(roots, points)
    symmetry_count = mixed.anchor_orbit(roots, frame_lines(), normals)
    vertices = mixed.intersections(directions)
    adjacency = mixed.compatibility(vertices, directions)
    root_result, candidates, costs = root_receipt(roots, coordinates)
    app, table = application(), predecessor_table()
    require(
        table[15][2] == app["original_survivors"],
        "original (7,4) survivor count differs",
    )
    result = {
        "schema": "p112-eight-vertex-union/v1",
        "input_sha256": digest,
        "alphabet": {
            "directions": len(directions),
            "eligible_nonroots": len(normals),
            "D7_support_histogram": norm_histogram,
            "anchor_symmetries": symmetry_count,
        },
        "mixed": mixed_receipt(vertices, adjacency, points),
        "all_root": root_result,
        "application": app,
        "original_table": table,
        "chamber": chamber_receipt(roots, points, coordinates),
        "root_planes": root_plane_receipt(roots),
        "six_flat_capacity": flat_capacity(labels, 6),
    }
    return result, candidates, costs, vertices, adjacency, points


def check_receipt(actual, expected):
    require(
        json.loads(json.dumps(actual)) == json.loads(json.dumps(expected)),
        "committed mathematical receipt differs",
    )


def write_result(result, output):
    destination = output.expanduser().resolve()
    require(not destination.is_relative_to(ROOT), "output must be outside checkout")
    with destination.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="create a fresh external receipt")
    args = parser.parse_args()
    result = receipt()[0]
    if args.output is None:
        check_receipt(result, json.loads(read_bytes(PACKAGE / "RESULT.json")))
    else:
        write_result(result, args.output)
    print(
        "PASS_EIGHT_VERTEX_UNION profile=4,5^2,6^8 mixed_lower=162 "
        "all_root_lower=162 allowance=160 margin=2 no_new_kappa"
    )


if __name__ == "__main__":
    main()
