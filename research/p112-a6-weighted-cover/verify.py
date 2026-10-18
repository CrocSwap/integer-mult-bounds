"""Replay the characteristic-zero P112 3,4,6^8 weighted-cover exclusion."""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from bound import all_root_six, application, mixed_six
from vendor.geometry import (
    chamber_receipt,
    flat_capacity,
    frame_lines,
    require,
    root_data,
    root_plane_receipt,
)
from vendor.mixed import alphabet, anchor_orbit, compatibility, intersections
from weighted import weighted_cover

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
DATA = "research/one-sided-six-multisets/data/data.txt"
RETAINED = frozenset(("geometry.py", "mixed.py", "bk2b.py", "LICENSE",
                      "PREDECESSOR-NOTICE.md", "ROOT-SIMPLEX-PROOF.md",
                      "TWOSIDE-NOTES.md"))


def read_bytes(path):
    require(len(path.parts) <= 32, "input path depth")
    require(not any(p.is_symlink() for p in (path, *path.parents)), "linked input")
    require(path.is_file() and path.stat().st_size <= 2_000_000,
            f"missing or oversized input: {path}")
    return path.read_bytes()


def bind_sources(package=PACKAGE):
    sources = json.loads(read_bytes(package / "SOURCES.json"))
    rows = sources["retained_files"]
    require(len(rows) == 7, "retained source inventory size")
    require({row["local_path"] for row in rows}
            == {"vendor/" + name for name in RETAINED}, "retained source inventory")
    for row in rows:
        raw = read_bytes(package / row["local_path"])
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "changed retained source")
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw,
                            usedforsecurity=False).hexdigest()
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
    result = subprocess.run(
        [sys.executable, "-I", "-B", str(PACKAGE / "vendor/bk2b.py")],
        cwd=PACKAGE, capture_output=True, text=True, check=True, timeout=120,
    )
    require(not result.stderr and len(result.stdout) <= 4096, "unexpected original output")
    rows = [tuple(map(int, line.split())) for line in result.stdout.splitlines()]
    require(len(rows) == 24 and all(len(row) == 4 for row in rows), "original table shape")
    require([(r[0], r[1]) for r in rows]
            == [(b, t) for b in range(5, 9) for t in range(1, 7)], "original table order")
    require(rows[9][2] == 69, "original (6,4) cell changed")
    return rows


def graph_digest(vertices, adjacency):
    raw = json.dumps({"vertices_doubled": vertices, "adjacency": adjacency},
                     sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def receipt():
    sources = bind_sources()
    roots, points, labels, coordinates = root_data()
    digest = bind_data(ROOT / DATA, points, labels, sources)
    directions, normals, norm_four_histogram = alphabet(roots, points)
    symmetries = anchor_orbit(roots, frame_lines(), normals)
    vertices = intersections(directions)
    adjacency = compatibility(vertices, directions)
    root_bound = all_root_six(roots)
    return {
        "schema": "p112-a6-weighted-cover/v1", "input_sha256": digest,
        "alphabet": {"root_lines": 120, "D7_normal_lines": 1080,
                     "D7_support_histogram": norm_four_histogram,
                     "eligible_nonroots": len(normals), "directions": len(directions),
                     "anchor_symmetries": symmetries},
        "graph": {"vertices": len(vertices), "edges": 595,
                  "sha256": graph_digest(vertices, adjacency)},
        "mixed": mixed_six(vertices, adjacency, points),
        "all_root": root_bound, "application": application(),
        "weighted": weighted_cover(roots, coordinates, root_bound["representative"]),
        "chamber": chamber_receipt(roots, points, coordinates),
        "root_planes": root_plane_receipt(roots),
        "six_flat_capacity": flat_capacity(labels, 6),
        "original_table": predecessor_table(),
    }


def check_receipt(actual, expected):
    require(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "committed mathematical receipt differs")


def publish_receipt(result, output):
    if output is None:
        check_receipt(result, json.loads(read_bytes(PACKAGE / "RESULT.json")))
        return
    destination = output.expanduser().resolve()
    require(not destination.is_relative_to(ROOT), "output must be outside checkout")
    with destination.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write fresh external evidence, no overwrite")
    args = parser.parse_args()
    publish_receipt(receipt(), args.output)
    print("PASS_A6_WEIGHTED_COVER profile=3,4,6^8 mixed=142 root=141 allowance=140 margin=1")


if __name__ == "__main__":
    main()
