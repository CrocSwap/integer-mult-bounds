"""Reproduce the P112 A3 rank-six shortening theorem and one profile exclusion."""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from a3_geometry import (
    chamber_receipt,
    flat_capacity,
    require,
    root_data,
    root_plane_receipt,
)
from a3_model import (
    application,
    frame_receipt,
    label_action_receipt,
    original_survivors,
)

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
        len(retained) == 1 and retained[0]["local_path"] == "a3_geometry.py",
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
        "original cell order",
    )
    require(
        next(r[2] for r in rows if r[:2] == (6, 3)) == 17, "target-cell count changed"
    )
    return rows


def receipt():
    sources = bind_sources()
    roots, points, labels, coordinates = root_data()
    bind_data(points, labels)
    full_labels = tuple(
        1 | sum((int(x) % 2) << (i + 1) for i, x in enumerate(row))
        for row in coordinates
    )
    return {
        "schema": "p112-a3-rank-six-shortening/v1",
        "base_commit": sources["base_commit"],
        "a3": frame_receipt(roots, full_labels),
        "application": application(),
        "historical_survivors": original_survivors(),
        "original_table": original_table(),
        "chamber": chamber_receipt(roots, points, coordinates),
        "root_planes": root_plane_receipt(roots),
        "binary_label_action": label_action_receipt(roots, full_labels),
        "six_flat_capacity": flat_capacity(labels, 6),
        "new_kappa": False,
    }


def check_receipt(actual, expected):
    require(
        json.loads(json.dumps(actual)) == expected,
        "committed mathematical receipt differs",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="create a new external receipt")
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
        "PASS_A3_RANK_SIX_SHORTENING support=22 exclusions=1 "
        "frames=2025 extremal=60 binary_spans=240 flats=788035 errors=0"
    )


if __name__ == "__main__":
    main()
