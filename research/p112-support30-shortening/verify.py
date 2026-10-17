"""Replay the P112 support-thirty shortening lemma without Git or network."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
PREDECESSOR = ROOT / "research/p112-mixed-edge-simplex"
DATA = "research/one-sided-six-multisets/data/data.txt"
LIVE = (
    DATA,
    "research/p112-mixed-edge-simplex/mixed.py",
    "research/p112-mixed-edge-simplex/vendor/geometry.py",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_bytes(path):
    require(
        path.is_file() and not path.is_symlink() and path.stat().st_size <= 2_000_000,
        f"invalid input: {path}",
    )
    return path.read_bytes()


def bind_sources(root=ROOT):
    sources = json.loads(read_bytes(PACKAGE / "SOURCES.json"))
    pins = [row for row in sources["files"] if row["usage"] == "input"]
    require(
        tuple(sorted(row["path"] for row in pins)) == tuple(sorted(LIVE)),
        "live-input inventory differs",
    )
    for row in pins:
        raw = read_bytes(root / row["path"])
        require(
            hashlib.sha256(raw).hexdigest() == row["sha256"],
            f"changed live input: {row['path']}",
        )
        blob = hashlib.sha1(
            b"blob " + str(len(raw)).encode() + b"\0" + raw, usedforsecurity=False
        ).hexdigest()
        require(blob == row["git_blob"], "live Git blob differs")
    return {row["path"]: row["sha256"] for row in pins}


# Authenticate the inherited source before importing it. No third-party packages.
INPUT_HASHES = bind_sources()
# Keep package-local modules ahead of names used by the predecessor package.
sys.path.insert(1, str(PREDECESSOR))
from bound import (  # noqa: E402
    mixed_bound,
    orthogonal_frames,
    root_bound,
    shortening_contract,
)
from mixed import alphabet, anchor_orbit, compatibility, intersections  # noqa: E402
from vendor.geometry import (  # noqa: E402
    chamber_receipt,
    frame_lines,
    root_data,
    root_plane_receipt,
)


def receipt():
    roots, points, labels, coordinates = root_data()
    lines = read_bytes(ROOT / DATA).decode("utf-8").splitlines()
    require(tuple(map(int, lines[0].split())) == labels, "P112 labels differ")
    require(
        tuple(tuple(map(int, row.split())) for row in lines[2:114]) == points,
        "P112 root coordinates differ",
    )
    directions, normals, histogram = alphabet(roots, points)
    require(
        anchor_orbit(roots, frame_lines(), normals) == 128,
        "incomplete puncture-preserving anchor orbit",
    )
    vertices = intersections(directions)
    adjacency = compatibility(vertices, directions)
    frames = orthogonal_frames(roots)
    return {
        "schema": "p112-support30-shortening/v1",
        "input_sha256": INPUT_HASHES,
        "alphabet": {"directions": len(directions), "D7_support_histogram": histogram},
        "graph": {"vertices_doubled": vertices, "adjacency": adjacency},
        "mixed": mixed_bound(vertices, adjacency, points),
        "root": root_bound(roots, frames),
        "frame_sha256": hashlib.sha256(json.dumps(frames).encode()).hexdigest(),
        "chamber": chamber_receipt(roots, points, coordinates),
        "root_planes": root_plane_receipt(roots),
        "contract": shortening_contract(30, (20,) * 6, 5),
    }


def check_receipt(actual, expected):
    require(
        json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
        "committed mathematical receipt differs",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, help="new evidence file outside checkout"
    )
    args = parser.parse_args()
    actual = receipt()
    if args.output is None:
        check_receipt(actual, json.loads(read_bytes(PACKAGE / "RESULT.json")))
    else:
        output = args.output.expanduser().resolve()
        require(not output.is_relative_to(ROOT), "output must be outside checkout")
        with output.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(actual, indent=2) + "\n")
    print(
        "PASS_SUPPORT30_SHORTENING mixed=121 root=122 allowance=120 "
        "four_cliques=4459 independent=3136 frames=2025 no_new_kappa"
    )


if __name__ == "__main__":
    main()
