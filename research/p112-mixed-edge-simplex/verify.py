"""Replay the P112 twelve-piece (8,4) mixed-edge simplex exclusion."""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from mixed import (
    all_root_census,
    alphabet,
    anchor_orbit,
    application,
    compatibility,
    intersections,
    mixed_census,
)
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
        len(rows) == 6 and len({row["local_path"] for row in rows}) == 6,
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
    require(len(lines) >= 114, "truncated P112 input")
    require(tuple(map(int, lines[0].split())) == labels, "P112 labels differ")
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
    require(rows[21][2] == 251, "original (8,4) cell changed")
    return rows


def receipt():
    sources = bind_sources()
    roots, points, labels, coordinates = root_data()
    digest = bind_data(ROOT / DATA, points, labels, sources)
    directions, normals, norm_four_histogram = alphabet(roots, points)
    symmetry_count = anchor_orbit(roots, frame_lines(), normals)
    vertices = intersections(directions)
    adjacency = compatibility(vertices, directions)
    graph_bytes = json.dumps(
        {"vertices_doubled": vertices, "adjacency": adjacency},
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return {
        "schema": "p112-mixed-edge-simplex/v1",
        "input_sha256": digest,
        "alphabet": {
            "root_lines": 120,
            "D7_normal_lines": 1080,
            "D7_support_histogram": norm_four_histogram,
            "eligible_nonroots": len(normals),
            "directions": len(directions),
            "anchor_symmetries": symmetry_count,
        },
        "graph": {
            "vertices": len(vertices),
            "edges": 595,
            "sha256": hashlib.sha256(graph_bytes).hexdigest(),
        },
        "mixed": mixed_census(vertices, adjacency, points),
        "all_root": all_root_census(roots),
        "application": application(),
        "chamber": chamber_receipt(roots, points, coordinates),
        "root_planes": root_plane_receipt(roots),
        "flat_capacities": [flat_capacity(labels, dimension) for dimension in (5, 6)],
        "original_table": predecessor_table(),
    }


def check_receipt(actual, expected):
    require(
        json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
        "committed mathematical receipt differs",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, help="write fresh evidence outside the checkout"
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
        "PASS_MIXED_EDGE_SIMPLEX profile=4,5^2,6^9 directions=248 vertices=58 "
        "rank8_cliques=608 mixed_lower=182 all_root_lower=204 allowance=180 margin=2"
    )


if __name__ == "__main__":
    main()
