"""Replay one eleven-piece P112 profile exclusion with exact arithmetic."""

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from itertools import combinations, combinations_with_replacement, product
from pathlib import Path

from vendor.geometry import (
    chamber_receipt,
    dot,
    flat_capacity,
    frame_lines,
    require,
    root_data,
    root_plane_receipt,
)
from vendor.mixed import (
    ANCHOR,
    alphabet,
    anchor_orbit,
    cliques,
    compatibility,
    intersections,
    rational_rank,
    root_extensions,
)

PACKAGE = Path(__file__).resolve().parent
DATA = "research/one-sided-six-multisets/data/data.txt"
PROFILE = (2, 3, 4, 4, 4, 4, 6, 6, 6, 6, 6)
CAP = {2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}


def read_bytes(path):
    require(path.is_file() and not path.is_symlink(), f"missing/linked input {path}")
    require(path.stat().st_size <= 2_000_000, f"oversized input {path}")
    return path.read_bytes()


def bind_sources():
    sources = json.loads(read_bytes(PACKAGE / "SOURCES.json"))
    rows = sources["retained_files"]
    require(len(rows) == 7, "retained source inventory")
    require(len({r["local_path"] for r in rows}) == 7, "duplicate retained source")
    for row in rows:
        path = Path(row["local_path"])
        require(len(path.parts) == 2 and path.parts[0] == "vendor", "retained path")
        raw = read_bytes(PACKAGE / path)
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "retained hash")
        header = b"blob " + str(len(raw)).encode() + b"\0"
        require(
            hashlib.sha1(header + raw, usedforsecurity=False).hexdigest()
            == row["git_blob"],
            "Git blob",
        )
    return sources


def bind_data(path, points, labels, sources):
    rows = [r for r in sources["files"] if r["usage"] == "input"]
    require(len(rows) == 1 and rows[0]["path"] == DATA, "live input inventory")
    raw = read_bytes(path)
    require(hashlib.sha256(raw).hexdigest() == rows[0]["sha256"], "P112 data hash")
    lines = raw.decode().splitlines()
    require(tuple(map(int, lines[0].split())) == labels, "P112 labels")
    parsed = tuple(tuple(map(int, line.split())) for line in lines[2:114])
    require(parsed == points, "P112 root coordinates")
    return rows[0]["sha256"]


def support_costs(rows, points):
    require(len(rows) == 5 and len(points) in (112, 120), "six-vertex dimensions")
    costs = []
    for point in points:
        values = (0, *(dot(point, row) for row in rows))
        costs.append(6 - max(Counter(values).values()))
    return costs


def mixed_census(vertices, adjacency, points):
    anchor = tuple(2 * x for x in ANCHOR)
    ranks, bounds = Counter(), Counter()
    minimum, witness = 1000, None
    for chosen in cliques(adjacency, 4):
        rows = (anchor, *(vertices[i] for i in chosen))
        rank = rational_rank(rows)
        ranks[rank] += 1
        if rank != 5:
            continue
        costs = support_costs(rows, points)
        lower = sum(sorted(costs)[:82])
        bounds[lower] += 1
        if lower < minimum:
            minimum = lower
            order = sorted(range(112), key=lambda i: (-costs[i], i))
            witness = {
                "vertices_doubled": rows,
                "cuts": order[:30],
                "spectrum": dict(sorted(Counter(costs).items())),
            }
    require(ranks == {3: 63, 4: 1260, 5: 3136}, "four-clique rank inventory")
    expected = {121: 448, 122: 112, 123: 560, 124: 560, 125: 560, 133: 784, 134: 112}
    require(bounds == expected and minimum == 121, "mixed support floor")
    return {
        "rank_histogram": ranks,
        "support_histogram": bounds,
        "minimum_after_30_cuts": minimum,
        "witness": witness,
    }


def root_census(roots):
    level, steps = [()], []
    for rank in range(5):
        following = []
        for prefix in level:
            representatives, sizes = root_extensions(prefix, roots)
            steps.append({"rank": rank, "orbit_sizes": sizes})
            following.extend((*prefix, row) for row in representatives)
        level = following
    require(len(level) == 1, "A5 orbit inventory")
    costs = support_costs(level[0], roots)
    spectrum = dict(sorted(Counter(costs).items()))
    require(spectrum == {0: 4, 1: 36, 2: 60, 3: 20}, "A5 spectrum")
    lower = sum(sorted(costs)[:82])  # Relax eight frame and thirty live cuts.
    require(lower == 120, "root support floor")
    return {
        "steps": steps,
        "spectrum": spectrum,
        "minimum_after_38_full_root_cuts": lower,
        "star": level[0],
    }


def original_survivors():
    distance = (0, 53, 78, 92, 100, 106)
    survivors = []
    for size in range(5, 12):
        for weights in combinations_with_replacement(range(2, 8), size):
            if sum(w - 2 for w in weights) >= 30:
                continue
            feasible = True
            for level in range(1, 6):
                prefix = weights[: size - 5 + level]
                total = sum(CAP[w] for w in prefix)
                target = sum(32 if w == 7 else CAP[w] for w in prefix)
                if (
                    (level == 1 and target < 53 and total < 73)
                    or (level == 2 and target < 78 and total < 82)
                    or (level >= 3 and total < distance[level])
                ):
                    feasible = False
            basis = weights[: size - 5]
            killed = False
            if sum(CAP[w] for w in basis) < 53:
                killed = sum(basis) <= 7 or any(
                    all(
                        sum(w for w, a in zip(basis, assignment, strict=True) if a == k)
                        <= 6
                        for k in (0, 1)
                    )
                    for assignment in product((0, 1), repeat=len(basis))
                )
            if feasible and not killed:
                survivors.append(weights)
    require(len(survivors) == 77 and PROFILE in survivors, "original residue")
    return survivors


def application():
    survivors = original_survivors()
    choices = []
    for basis in sorted(set(combinations(PROFILE, 6))):
        if sum(CAP[w] for w in basis) >= 53:
            continue
        for assignment in product(range(3), repeat=6):
            if all(
                sum(w for w, a in zip(basis, assignment, strict=True) if a == k) <= 6
                for k in (0, 1)
            ):
                choices.append(
                    sum(
                        CAP[w] for w, a in zip(basis, assignment, strict=True) if a == 2
                    )
                )
    require(min(choices) == 20, "earlier weight-only deletion route")
    selected = (2, 3, 4, 4, 4)
    endpoints = (4, 6, 6, 6, 6, 6)
    require(sorted(selected + endpoints) == list(PROFILE), "piece partition")
    small, allowance = sum(CAP[w] for w in selected), sum(CAP[w] for w in endpoints)
    require(small == 30 and allowance == 108 and small + 20 < 53, "quotient budget")
    return {
        "weights": PROFILE,
        "cell": [5, 6],
        "original_survivors": len(survivors),
        "small_support_cap": small,
        "edge_support_cap": 70,
        "endpoint_allowance": allowance,
        "mixed_lower": 121,
        "root_lower": 120,
        "minimum_weight_only_two_flat_cuts": min(choices),
    }


def build(data):
    sources = bind_sources()
    roots, points, labels, coordinates = root_data()
    data_hash = bind_data(data, points, labels, sources)
    chamber = chamber_receipt(roots, points, coordinates)
    planes = root_plane_receipt(roots)
    capacity = flat_capacity(labels, 6)
    directions, normals, histogram = alphabet(roots, points)
    orbit = anchor_orbit(roots, frame_lines(), normals)
    vertices = intersections(directions)
    adjacency = compatibility(vertices, directions)
    predecessor = subprocess.run(
        [sys.executable, "-I", "-B", str(PACKAGE / "vendor/bk2b.py")],
        capture_output=True,
        text=True,
        check=True,
        timeout=120,
    )
    require("5 6 77 1" in predecessor.stdout.splitlines(), "pinned BK table")
    return {
        "data_sha256": data_hash,
        "chamber": chamber,
        "root_planes": planes,
        "six_flat_capacity": capacity,
        "D7_support_histogram": histogram,
        "anchor_orbit": orbit,
        "vertices_doubled": vertices,
        "adjacency": adjacency,
        "mixed": mixed_census(vertices, adjacency, points),
        "root": root_census(roots),
        "application": application(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=PACKAGE.parent.parent / DATA)
    parser.add_argument(
        "--write", type=Path, help="write a receipt to an external path"
    )
    args = parser.parse_args()
    result = build(args.data)
    canonical = json.loads(json.dumps(result))
    if args.write:
        args.write.write_text(json.dumps(canonical, indent=2, sort_keys=True) + "\n")
    else:
        require(
            canonical == json.loads(read_bytes(PACKAGE / "RESULT.json")),
            "receipt differs",
        )
    print(
        "PASS_P112_SIX_VERTEX_BUDGET mixed=121 root=120 allowance=108 "
        "profile=2,3,4^4,6^5"
    )


if __name__ == "__main__":
    main()
