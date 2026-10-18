"""Replay the three-endpoint P112 singleton-shortening certificate."""

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
sys.path.insert(0, str(PACKAGE))  # Explicit package imports also work under -I.

from model import (
    application,
    binary_rank,
    original_survivors,
    singleton_classes,
    singleton_hyperplane_receipt,
    support_lower,
    transport_receipt,
)
from vendor.geometry import (
    chamber_receipt,
    flat_capacity,
    require,
    root_data,
    root_plane_receipt,
)

DATA = "research/one-sided-six-multisets/data/data.txt"


def bounded_bytes(path, limit=2_000_000):
    require(
        path.is_file() and not path.is_symlink() and path.stat().st_size <= limit,
        f"missing, linked or oversized input: {path}",
    )
    return path.read_bytes()


def bind_sources(package=PACKAGE):
    sources = json.loads(bounded_bytes(package / "SOURCES.json", 32_768))
    pins = [r for r in sources["files"] if r["usage"] == "input"]
    require(len(pins) == 5 and len(sources["retained_files"]) == 3, "source inventory")
    for row in pins:
        raw = bounded_bytes(ROOT / row["path"])
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "changed live source")
    for row in sources["retained_files"]:
        path = Path(row["local_path"])
        require(len(path.parts) == 2 and path.parts[0] == "vendor", "retained path")
        raw = bounded_bytes(package / path)
        require(
            hashlib.sha256(raw).hexdigest() == row["sha256"], "changed retained source"
        )
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(blob == row["git_blob"], "retained Git blob mismatch")
    return sources


def bind_data(points, labels, sources):
    raw = bounded_bytes(ROOT / DATA)
    rows = raw.decode("utf-8").splitlines()
    require(len(rows) >= 114, "truncated P112 input")
    require(tuple(map(int, rows[0].split())) == labels, "P112 label binding")
    require(
        tuple(tuple(map(int, r.split())) for r in rows[2:114]) == points,
        "P112 root binding",
    )
    digest = hashlib.sha256(raw).hexdigest()
    require(
        any(r["path"] == DATA and r["sha256"] == digest for r in sources["files"]),
        "P112 source hash",
    )
    return digest


def original_label_binding(points, labels):
    raw = bounded_bytes(PACKAGE / "vendor/bx_data.json", 32_768)
    original = json.loads(raw, parse_float=Fraction)
    require(len(original["LAB"]) == len(original["L"]) == 112, "original P112 sizes")
    original_points = []
    for row in original["L"]:
        scaled = tuple(2 * x for x in row)
        require(
            len(scaled) == 8 and all(x.denominator == 1 for x in scaled),
            "original rational root coordinates",
        )
        integers = tuple(map(int, scaled))
        original_points.append(max(integers, tuple(-x for x in integers)))
    require(set(original_points) == set(points), "original/live root set mismatch")
    current = dict(zip(points, labels, strict=True))
    pivots = {}
    for before, root in zip(original["LAB"], original_points, strict=True):
        require(type(before) is int and 0 < before < 512, "original binary label")
        after = current[root]
        for bit in range(8, -1, -1):
            if before & (1 << bit):
                if bit in pivots:
                    old, new = pivots[bit]
                    before, after = before ^ old, after ^ new
                else:
                    pivots[bit] = (before, after)
                    break
        else:
            require(before == after == 0, "original label map is not linear")
    require(len(pivots) == 9, "original labels do not span nine dimensions")
    columns = []
    for i in range(9):
        before, after = 1 << i, 0
        for bit in range(8, -1, -1):
            if before & (1 << bit):
                old, new = pivots[bit]
                before, after = before ^ old, after ^ new
        require(before == 0, "label-map basis reduction")
        columns.append(after)
    require(binary_rank(columns) == 9, "singular original/current label map")
    return {
        "origin_commit": "708f0ad8928c383de8294aea3c126e9461d2066d",
        "sha256": hashlib.sha256(raw).hexdigest(),
        "root_lines": 112,
        "binary_map_columns": columns,
        "binary_map_rank": 9,
    }


def historical_control():
    # The child does not inherit the parent's interpreter cache-prefix option.
    with tempfile.TemporaryDirectory(prefix="a2-historical-") as cache:
        result = subprocess.run(
            [
                sys.executable,
                "-X",
                f"pycache_prefix={cache}",
                "-I",
                "-B",
                str(PACKAGE / "historical_control.py"),
            ],
            cwd=PACKAGE,
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )
    require(not result.stderr and len(result.stdout) <= 4096, "historical output")
    lines = result.stdout.splitlines()
    require(
        len(lines) == 25 and lines[-1] == "PASS_HISTORICAL_CALLER True False 35",
        "literal predecessor caller rejected",
    )
    table = [tuple(map(int, line.split())) for line in lines[:-1]]
    require(len(table) == 24 and all(len(r) == 4 for r in table), "historical table")
    require(
        next(r for r in table if r[:2] == (6, 5)) == (6, 5, 174, 1),
        "historical target cell",
    )
    return table


def receipt():
    sources = bind_sources()
    roots, points, labels, coordinates = root_data()
    digest = bind_data(points, labels, sources)
    full_labels, transport = transport_receipt(roots, coordinates)
    classes, doubles = singleton_classes(roots)
    historical = historical_control()
    survivors = original_survivors()
    return {
        "schema": "p112-a2-singleton-shortening/v1",
        "input_sha256": digest,
        "chamber": chamber_receipt(roots, points, coordinates),
        "root_planes": root_plane_receipt(roots),
        "live_flat_capacities": [flat_capacity(labels, d) for d in (5, 6)],
        "transport": transport,
        "singleton_classes": [s.bit_count() for s in classes],
        "double_coordinates": doubles.bit_count(),
        "singleton_hyperplanes": singleton_hyperplane_receipt(full_labels, classes),
        "support_bounds": {str(s): support_lower(s) for s in (18, 21, 22)},
        "original_label_binding": original_label_binding(points, labels),
        "original_survivor_table": historical,
        "original_target_survivors": [list(w) for w in survivors],
        "application": application(),
    }


def check_receipt(actual, expected):
    require(
        json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
        "committed mathematical receipt differs",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="create a fresh external receipt")
    args = parser.parse_args()
    path = None if args.output is None else args.output.expanduser().resolve()
    if path is not None:
        require(
            not path.is_relative_to(ROOT), "receipt output must be outside checkout"
        )
        require(not path.exists(), "receipt output already exists")
    result = receipt()
    if path is None:
        check_receipt(result, json.loads(bounded_bytes(PACKAGE / "RESULT.json")))
    else:
        with path.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    print(
        "PASS_P112_A2_SINGLETON_SHORTENING support21_lower62 profile_lower68 "
        "endpoint_allowance60 singleton_cap16 restrictions381"
    )


if __name__ == "__main__":
    main()
