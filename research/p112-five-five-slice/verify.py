#!/usr/bin/env python3
"""Source-bound replay of the P112 five-five deletion argument."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from collections import Counter
from itertools import combinations, combinations_with_replacement, product
from math import comb
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PROFILE = (5, 5) + (6,) * 6 + (7,)
CAP = {2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    require(path.stat().st_size <= 200_000, "JSON capacity exceeded")
    return json.loads(path.read_text())


def check_sources(root=ROOT, package=PACKAGE):
    manifest = read_json(package / "SOURCES.json")
    hashes = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            path = root / row["path"]
            require(path.stat().st_size <= 2_000_000, "input capacity exceeded")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            require(digest == row["sha256"], "changed live input")
            hashes[row["path"]] = digest
    for row in manifest["retained_files"]:
        path = package / row["local_path"]
        require(path.stat().st_size <= 100_000, "retained source capacity exceeded")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(digest == row["sha256"], "changed retained source")
        hashes[row["local_path"]] = digest
    return hashes


def bind_input(points, labels, root=ROOT):
    path = root / "research/one-sided-six-multisets/data/data.txt"
    with path.open() as stream:
        source_labels = tuple(map(int, stream.readline().split()))
        frame_labels = tuple(map(int, stream.readline().split()))
        source_points = tuple(
            tuple(map(int, stream.readline().split())) for _ in range(112)
        )
    require(
        source_labels == labels and source_points == points,
        "root/label source order mismatch",
    )
    require(
        len(frame_labels) == 8 and len(set(frame_labels)) == 8, "source frame inventory"
    )


def root_star(roots):
    from vendor.geometry import dot
    from vendor.mixed import root_extensions

    level, steps = [()], []
    for rank in range(5):
        following = []
        for prefix in level:
            representatives, sizes = root_extensions(prefix, roots)
            steps.append({"rank": rank, "orbit_sizes": sizes})
            following.extend((*prefix, v) for v in representatives)
        level = following
    require(len(level) == 1, "incomplete A5 star orbit coverage")
    require(
        [s["orbit_sizes"] for s in steps] == [[240], [56], [27], [16], [10]],
        "A5 extension orbit sizes changed",
    )
    star = level[0]
    require(
        all(
            dot(a, b) == (8 if i == j else 4)
            for i, a in enumerate(star)
            for j, b in enumerate(star)
        ),
        "A5 star Gram matrix",
    )
    costs = tuple(
        6 - max(Counter((0, *(dot(r, v) for v in star))).values()) for r in roots
    )
    return star, costs, steps


def closed_form_spectrum():
    """Count the explicit star e0+e1,...,e0+e5 by the two root classes."""
    integer = Counter({0: 2, 1: 24, 2: 30})
    half = Counter()
    for positive in range(6):
        half[min(positive, 6 - positive)] += 2 * comb(5, positive)
    require(
        sum(integer.values()) == 56 and sum(half.values()) == 64, "root-class count"
    )
    return integer + half


def support_invoice(costs, small_support=24, endpoint_cap=20):
    require(
        len(costs) == 120 and all(type(c) is int and 0 <= c <= 3 for c in costs),
        "A5 cost domain",
    )
    require(
        type(small_support) is int
        and 0 <= small_support <= 112
        and type(endpoint_cap) is int
        and 0 <= endpoint_cap <= 112,
        "support-cap domain",
    )
    require(small_support + endpoint_cap < 53, "quotient independence not certified")
    require(small_support + 2 * endpoint_cap < 70, "root-only edges not certified")
    removed = 8 + small_support
    lower = sum(sorted(costs)[: 120 - removed])
    allowance = 6 * endpoint_cap
    require(lower > allowance, "endpoint budget does not contradict")
    # PR3169's coordinate-incidence inequality, for six endpoints.
    edge_lower = 15 * 53
    edge_upper = 112 + 8 * small_support + 4 * allowance
    require(edge_lower > edge_upper, "coordinate-incidence control does not contradict")
    return {
        "small_support_cap": small_support,
        "quotient_support_cap": small_support + endpoint_cap,
        "edge_support_cap": small_support + 2 * endpoint_cap,
        "removed_full_root_coordinates": removed,
        "full_cost": sum(costs),
        "endpoint_lower": lower,
        "endpoint_allowance": allowance,
        "endpoint_margin": lower - allowance,
        "coordinate_lower": edge_lower,
        "coordinate_upper": edge_upper,
        "coordinate_margin": edge_lower - edge_upper,
    }


def original_survivors():
    """Separate transcription of the historical (6,3) necessary filters."""
    distance = (0, 53, 78, 92, 100, 106, 109)
    rows, examined = [], 0
    for size in range(6, 10):
        for weights in combinations_with_replacement(range(2, 8), size):
            examined += 1
            if sum(w - 2 for w in weights) >= 36:
                continue
            feasible = True
            for level in range(1, 7):
                prefix = weights[: size - 6 + level]
                total = sum(CAP[w] for w in prefix)
                target = sum(32 if w == 7 else CAP[w] for w in prefix)
                if (
                    (level == 1 and target < 53 and total < 73)
                    or (level == 2 and target < 78 and total < 82)
                    or (level >= 3 and total < distance[level])
                ):
                    feasible = False
                    break
            basis = weights[: size - 6]
            killed = False
            if sum(CAP[w] for w in basis) < 53:
                killed = sum(basis) <= 7 or any(
                    all(
                        sum(
                            w
                            for w, g in zip(basis, assignment, strict=True)
                            if g == group
                        )
                        <= 6
                        for group in (0, 1)
                    )
                    for assignment in product(range(2), repeat=len(basis))
                )
            if feasible and not killed:
                rows.append(weights)
    require(len(rows) == 17 and PROFILE in rows, "historical (6,3) residue changed")
    return {
        "examined": examined,
        "profiles": rows,
        "target": PROFILE,
        "target_excess": sum(w - 2 for w in PROFILE),
        "strict_excess_threshold": 36,
    }


def predecessor_control(package=PACKAGE):
    env = dict(os.environ)
    env.pop("PYTHONOPTIMIZE", None)
    result = subprocess.run(
        [sys.executable, "-B", str(package / "vendor/bk2b.py")],
        capture_output=True,
        text=True,
        timeout=45,
        check=True,
        env=env,
    )
    require(not result.stderr, "historical filter wrote diagnostics")
    rows = [tuple(map(int, line.split())) for line in result.stdout.splitlines()]
    require(
        len(rows) == 24 and (6, 3, 17, 1) in rows,
        "unaltered historical filter count mismatch",
    )
    return {"cells": len(rows), "target_cell": [6, 3, 17, 1]}


def weight_cover_obligation():
    candidates = []
    for basis in sorted(set(combinations(PROFILE, 3))):
        support = sum(CAP[w] for w in basis)
        if support >= 53:
            continue
        budgets = []
        for assignment in product(range(3), repeat=3):
            if all(
                sum(w for w, g in zip(basis, assignment, strict=True) if g == j) <= 6
                for j in (0, 1)
            ):
                budgets.append(
                    sum(
                        CAP[w] for w, g in zip(basis, assignment, strict=True) if g == 2
                    )
                )
        require(budgets, "missing weight-cover partition")
        candidates.append(
            {"basis": basis, "support_cap": support, "minimum_paid_cuts": min(budgets)}
        )
    require(
        [row["basis"] for row in candidates] == [(5, 5, 6), (5, 6, 6)],
        "weight-certified quotient bases changed",
    )
    require(
        all(row["minimum_paid_cuts"] == 12 for row in candidates),
        "old weight-only cover obligation changed",
    )
    return candidates


def receipt(root=ROOT, package=PACKAGE):
    hashes = check_sources(root, package)
    from vendor import geometry

    roots, points, labels, coordinates = geometry.root_data()
    bind_input(points, labels, root)
    chamber = geometry.chamber_receipt(roots, points, coordinates)
    planes = geometry.root_plane_receipt(roots)
    capacities = [geometry.flat_capacity(labels, d) for d in (5, 6)]
    star, costs, steps = root_star(roots)
    spectrum = Counter(costs)
    require(
        spectrum == closed_form_spectrum() == {0: 4, 1: 36, 2: 60, 3: 20},
        "A5 spectrum disagrees with separate root-class count",
    )
    return {
        "schema": "p112-five-five-slice/v1",
        "source_sha256": hashes,
        "chamber": chamber,
        "root_planes": planes,
        "capacities": capacities,
        "A5": {
            "steps": steps,
            "star": star,
            "spectrum": dict(sorted(spectrum.items())),
        },
        "invoice": support_invoice(costs),
        "historical": original_survivors(),
        "original_filter_control": predecessor_control(package),
        "weight_only_old_cover": weight_cover_obligation(),
        "deletion": {
            "pieces_before": 9,
            "pieces_after": 8,
            "intersection_before_at_least": 6,
            "intersection_after_at_least": 5,
            "impossible_remaining_weights": [5, 5] + [6] * 6,
        },
    }


def compare_receipt(actual, expected):
    canonical = json.loads(json.dumps(actual))
    require(canonical == expected, "receipt mismatch")


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
        compare_receipt(actual, read_json(PACKAGE / "RESULT.json"))
    else:
        with args.output.open("x") as stream:
            stream.write(json.dumps(actual, indent=2) + "\n")
    print("PASS_P112_FIVE_FIVE_SLICE: 132 > 120; profile 5,5,6^6,7 excluded")


if __name__ == "__main__":
    main()
