"""Replay the P112 2,4,5^9 exclusion and sharp D7 saturated-support packing."""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from model import (
    application_receipt,
    binary_rank,
    bits,
    frame_receipt,
    packing_receipt,
    saturated_flats,
)
from vendor.geometry import chamber_receipt, require, root_data, root_plane_receipt

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
        {row["local_path"] for row in rows}
        == {
            "vendor/geometry.py",
            "vendor/bk2b.py",
            "vendor/PREDECESSOR-NOTICE.md",
            "vendor/LICENSE",
        }
        and len(rows) == 4,
        "retained source inventory changed",
    )
    for row in rows:
        raw = read_bytes(package / row["local_path"])
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
    require(digest == pins[0]["sha256"], "changed P112 input")
    lines = raw.decode("utf-8").splitlines()
    require(len(lines) >= 114, "truncated P112 input")
    require(tuple(map(int, lines[0].split())) == labels, "P112 labels differ")
    require(
        tuple(tuple(map(int, line.split())) for line in lines[2:114]) == points,
        "P112 roots differ",
    )
    return digest


def original_table():
    result = subprocess.run(
        [sys.executable, "-I", "-B", str(PACKAGE / "vendor/bk2b.py")],
        capture_output=True,
        text=True,
        check=True,
        timeout=120,
    )
    require(
        not result.stderr and len(result.stdout) <= 4096, "original output boundary"
    )
    rows = [tuple(map(int, line.split())) for line in result.stdout.splitlines()]
    require(
        len(rows) == 24
        and [(row[0], row[1]) for row in rows]
        == [(b, t) for b in range(5, 9) for t in range(1, 7)],
        "original table domain",
    )
    require(
        all(len(row) == 4 for row in rows) and rows[5][2] == 77,
        "original (5,6) survivor count changed",
    )
    return rows


def receipt():
    sources = bind_sources()
    roots, points, labels, coordinates = root_data()
    digest = bind_data(ROOT / DATA, points, labels, sources)
    support, frame, full_labels, frames = frame_receipt(roots, coordinates)
    saturated, flats = saturated_flats(full_labels, support)
    candidates = tuple(mask for mask in saturated if not mask & frame)
    require(len(candidates) == 756, "live saturated-support inventory changed")
    require(
        all(
            binary_rank(tuple(full_labels[i] for i in bits(mask, 120))) == 5
            for mask in candidates
        ),
        "saturated support rank changed",
    )
    packing = packing_receipt(candidates)
    require(
        (packing["edges"], packing["triangles"]) == (16464, 30016),
        "packing graph changed",
    )
    inventory = json.dumps(
        [bits(mask, 120) for mask in candidates], separators=(",", ":")
    )
    return {
        "schema": "p112-d7-saturation/v1",
        "input_sha256": digest,
        "frames": frames,
        "full120_flats": flats,
        "packing": packing,
        "candidate_sha256": hashlib.sha256(inventory.encode()).hexdigest(),
        "application": application_receipt(),
        "chamber": chamber_receipt(roots, points, coordinates),
        "root_planes": root_plane_receipt(roots),
        "original_table": original_table(),
    }


def check_receipt(actual, expected):
    require(
        json.loads(json.dumps(actual)) == json.loads(json.dumps(expected)),
        "committed mathematical receipt differs",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="create a fresh external receipt")
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
        "PASS_P112_D7_SATURATION exclusion=2,4,5^9 frames=240 "
        "flats=3309747 packing=3 required=5"
    )


if __name__ == "__main__":
    main()
