"""Replay the eleven-piece P112 (7,4) weighted-flat-pair exclusion."""

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

from bound import application, exceptional_bound, mixed_seven, root_types
from vendor.geometry import (
    chamber_receipt,
    frame_lines,
    require,
    root_data,
    root_plane_receipt,
)
from vendor.mixed import alphabet, anchor_orbit, compatibility, intersections

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
        len(rows) == 8 and len({row["local_path"] for row in rows}) == 8,
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
        "P112 label order differs",
    )
    require(
        tuple(tuple(map(int, line.split())) for line in lines[2:114]) == points,
        "P112 root order differs",
    )
    return digest


def full_labels(coordinates):
    require(
        len(coordinates) == 120
        and all(x.denominator == 1 for row in coordinates for x in row),
        "simple-root integral coordinates",
    )
    return tuple(
        1 | sum((int(x) % 2) << (i + 1) for i, x in enumerate(row))
        for row in coordinates
    )


def predecessor_table():
    result = subprocess.run(
        [sys.executable, "-I", "-B", str(PACKAGE / "vendor/bk2b.py")],
        cwd=PACKAGE,
        capture_output=True,
        text=True,
        check=True,
        timeout=120,
    )
    require(not result.stderr and len(result.stdout) <= 4096, "original output bound")
    rows = [tuple(map(int, line.split())) for line in result.stdout.splitlines()]
    require(
        len(rows) == 24 and all(len(row) == 4 for row in rows), "original table shape"
    )
    require(
        [(r[0], r[1]) for r in rows]
        == [(b, t) for b in range(5, 9) for t in range(1, 7)],
        "original cell order",
    )
    require(rows[15][2] == 154, "original (7,4) cell changed")
    return rows


def receipt():
    sources = bind_sources()
    roots, points, labels, coordinates = root_data()
    digest = bind_data(ROOT / DATA, points, labels, sources)
    directions, normals, norm_histogram = alphabet(roots, points)
    anchor_symmetries = anchor_orbit(roots, frame_lines(), normals)
    vertices = intersections(directions)
    adjacency = compatibility(vertices, directions)
    prefixes, costs, steps = root_types(roots)
    graph = {"vertices_doubled": vertices, "adjacency": adjacency}
    return {
        "schema": "p112-weighted-flat-pair/v1",
        "input_sha256": digest,
        "alphabet": {
            "directions": len(directions),
            "norm_four_supports": norm_histogram,
            "anchor_symmetries": anchor_symmetries,
        },
        "graph_sha256": hashlib.sha256(
            json.dumps(graph, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "mixed": mixed_seven(vertices, adjacency, points),
        "root": {
            "steps": steps,
            "representatives": prefixes,
            "spectra": [dict(sorted(Counter(row).items())) for row in costs],
            "ordinary_lower": 168,
            "arbitrary_deletion_control": 158,
        },
        "exceptional": exceptional_bound(
            roots, full_labels(coordinates), prefixes[1], costs[1]
        ),
        "application": application(),
        "chamber": chamber_receipt(roots, points, coordinates),
        "root_planes": root_plane_receipt(roots),
        "original_table": predecessor_table(),
    }


def check_receipt(actual, expected):
    require(
        json.loads(json.dumps(actual)) == expected,
        "committed mathematical receipt differs",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a fresh external receipt")
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
        "PASS_WEIGHTED_FLAT_PAIR profile=4,5^2,6^8 mixed_lower=162 "
        "ordinary_root_lower=168 exceptional_root_lower=162 allowance=160 margin=2"
    )


if __name__ == "__main__":
    main()
