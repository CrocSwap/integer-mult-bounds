#!/usr/bin/env python3
"""Reconstruct the A5 shortening certificate, using only pinned finite inputs."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
DATA = "research/one-sided-six-multisets/data/data.txt"
FILTER = "research/p112-five-five-slice/vendor/bk2b.py"
ORIGINAL_COUNTS = (
    (0, 0, 4, 15, 38, 77),
    (0, 1, 17, 69, 174, 364),
    (0, 2, 37, 154, 403, 885),
    (0, 3, 60, 251, 684, 1556),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    require(path.stat().st_size <= 200_000, "JSON capacity exceeded")
    return json.loads(path.read_text())


def check_sources(root=ROOT, package=PACKAGE):
    manifest = read_json(package / "SOURCES.json")
    live = [row for row in manifest["files"] if row["usage"] == "input"]
    require({row["path"] for row in live} == {DATA, FILTER}, "live input inventory")
    require(
        len(live) == 2 and len(manifest["retained_files"]) == 3,
        "source inventory capacity",
    )
    hashes = {}
    for row in live:
        path = root / row["path"]
        require(path.stat().st_size <= 2_000_000, "live input capacity")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(digest == row["sha256"], "changed live input")
        hashes[row["path"]] = digest
    names = {"vendor/geometry.py", "vendor/NOTICE.md", "vendor/LICENSE"}
    require(
        {r["local_path"] for r in manifest["retained_files"]} == names,
        "retained source inventory",
    )
    for row in manifest["retained_files"]:
        path = package / row["local_path"]
        require(path.stat().st_size <= 50_000, "retained source capacity")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(digest == row["sha256"], "changed retained source")
        hashes[row["local_path"]] = digest
    boundary = manifest["package_boundary"]
    require(boundary["path"] == "vendor/__init__.py", "package boundary path")
    initializer = package / boundary["path"]
    require(initializer.stat().st_size == 0, "package initializer must be empty")
    digest = hashlib.sha256(initializer.read_bytes()).hexdigest()
    require(digest == boundary["sha256"], "package boundary hash")
    hashes[boundary["path"]] = digest
    return hashes


def bind_data(points, labels, root=ROOT):
    with (root / DATA).open() as stream:
        source_labels = tuple(map(int, stream.readline().split()))
        frame_labels = tuple(map(int, stream.readline().split()))
        source_points = tuple(
            tuple(map(int, stream.readline().split())) for _ in range(112)
        )
    require(
        source_labels == labels and source_points == points,
        "root/label source order mismatch",
    )
    require(len(frame_labels) == len(set(frame_labels)) == 8, "source frame inventory")


def original_filter(root=ROOT):
    env = dict(os.environ)
    env.pop("PYTHONOPTIMIZE", None)
    result = subprocess.run(
        [sys.executable, "-B", str(root / FILTER)],
        capture_output=True,
        text=True,
        timeout=45,
        check=True,
        env=env,
    )
    require(not result.stderr, "original filter diagnostics")
    rows = [tuple(map(int, row.split())) for row in result.stdout.splitlines()]
    expected = [
        (b, t, count, int(count != 0))
        for b, counts in enumerate(ORIGINAL_COUNTS, start=5)
        for t, count in enumerate(counts, start=1)
    ]
    require(rows == expected, "original filter count mismatch")
    return {"cells": len(rows), "target_cell": [6, 4, 69, 1], "rows": rows}


def application(costs):
    from a5 import certify_slice
    from history import CAP, PROFILE

    small, retained, deleted = PROFILE[:3], PROFILE[:-1], PROFILE[-1:]
    require(
        retained[3:] == (6,) * 6 and sum(CAP[w] for w in small) == 26,
        "actual retained support contract",
    )
    return {
        "profile": PROFILE,
        "deleted": deleted,
        "retained": retained,
        "dimension_before_at_least": 6,
        "dimension_after_at_least": 5,
        "small_pieces": small,
        "invoice": certify_slice(costs, 26),
    }


def receipt(root=ROOT, package=PACKAGE):
    hashes = check_sources(root, package)
    from a5 import certify_slice, invoice, star_costs
    from history import historical_profiles, weight_only_covers
    from vendor import geometry

    roots, points, labels, coordinates = geometry.root_data()
    bind_data(points, labels, root)
    chamber = geometry.chamber_receipt(roots, points, coordinates)
    planes = geometry.root_plane_receipt(roots)
    capacities = [geometry.flat_capacity(labels, d) for d in (5, 6)]
    star, costs, steps = star_costs(roots)
    covers = weight_only_covers()
    require(
        len(covers) == 1
        and covers[0]["minimum_paid_cut_budgets"] == {"6": 14, "7": 12},
        "named prior cover audit changed",
    )
    require(covers[0]["nonbasis"] == [6] * 5 + [7], "nonbasis ranks changed")
    return {
        "schema": "p112-a5-shortening/v1",
        "source_sha256": hashes,
        "chamber": chamber,
        "root_planes": planes,
        "capacities": capacities,
        "A5": {
            "star": star,
            "steps": steps,
            "spectrum": dict(sorted(Counter(costs).items())),
        },
        "slice_29": certify_slice(costs, 29),
        "arithmetic_boundary_30": invoice(costs, 30),
        "application": application(costs),
        "historical": historical_profiles(),
        "original_filter": original_filter(root),
        "prior_covers": covers,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a fresh external receipt")
    args = parser.parse_args()
    if args.output is not None:
        destination = args.output.resolve()
        require(
            not destination.is_relative_to(ROOT.resolve()),
            "receipt output must be outside the checkout",
        )
        require(not destination.exists(), "refusing to overwrite receipt")
    actual = receipt()
    if args.output is None:
        require(
            json.loads(json.dumps(actual)) == read_json(PACKAGE / "RESULT.json"),
            "receipt mismatch",
        )
    else:
        with args.output.open("x") as stream:
            stream.write(json.dumps(actual, indent=2) + "\n")
    print(
        "PASS_P112_A5_SHORTENING errors=0 historical_profiles=69 "
        "slice29=122>120 target26=128>120; no_new_kappa"
    )


if __name__ == "__main__":
    main()
