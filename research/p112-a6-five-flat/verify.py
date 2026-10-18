"""Exact replay of the characteristic-zero P112 profile 5,6^8 exclusion."""

import argparse
import hashlib
import json
import subprocess
import sys
from itertools import combinations_with_replacement, product
from pathlib import Path

from cover_transfer import exhaustive_transfer
from vendor.cover import weighted_cover
from vendor.endpoint import all_root_six, mixed_six
from vendor.geometry import (
    chamber_receipt,
    flat_capacity,
    frame_lines,
    require,
    root_data,
    root_plane_receipt,
)
from vendor.mixed import alphabet, anchor_orbit, compatibility, intersections

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
DATA = "research/one-sided-six-multisets/data/data.txt"
PROFILE = (5,) + (6,) * 8
CAP = {2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}


def read_bytes(path):
    require(path.is_file() and not path.is_symlink(), "missing/linked input: " + str(path))
    require(path.stat().st_size <= 2_000_000, "oversized input: " + str(path))
    return path.read_bytes()


def bind_sources():
    sources = json.loads(read_bytes(PACKAGE / "SOURCES.json"))
    rows = sources["retained_files"]
    expected = {"geometry.py", "mixed.py", "cover.py", "endpoint.py", "bk2b.py",
                "PREDECESSOR-PROOF.md", "PREDECESSOR-NOTICE.md", "LICENSE",
                "TWOSIDE-NOTES.md", "ROOT-SIMPLEX-PROOF.md"}
    require(len(rows) == 10 and {r["local_path"] for r in rows}
            == {"vendor/" + name for name in expected}, "retained source inventory")
    for row in rows:
        raw = read_bytes(PACKAGE / row["local_path"])
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "retained SHA256")
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw,
                            usedforsecurity=False).hexdigest()
        require(blob == row["git_blob"], "retained Git blob")
    return sources


def bind_data(path, points, labels, sources):
    pins = [row for row in sources["files"] if row["usage"] == "input"]
    require(len(pins) == 1 and pins[0]["path"] == DATA, "live-input inventory")
    raw = read_bytes(path)
    digest = hashlib.sha256(raw).hexdigest()
    require(digest == pins[0]["sha256"], "changed P112 input")
    lines = raw.decode("utf-8").splitlines()
    require(len(lines) >= 114, "truncated P112 input")
    require(tuple(map(int, lines[0].split())) == labels, "P112 labels differ")
    require(tuple(tuple(map(int, line.split())) for line in lines[2:114]) == points,
            "P112 roots differ")
    return digest


def original_survivors():
    """Separate transcription of the original (6,3) weight filter."""
    distance = (0, 53, 78, 92, 100, 106, 109)
    survivors = []
    for size in range(6, 10):
        for weights in combinations_with_replacement(range(2, 8), size):
            if sum(w - 2 for w in weights) >= 36:
                continue
            feasible = True
            for level in range(1, 7):
                prefix = weights[:size - 6 + level]
                total = sum(CAP[w] for w in prefix)
                target = sum(32 if w == 7 else CAP[w] for w in prefix)
                if ((level == 1 and target < 53 and total < 73)
                        or (level == 2 and target < 78 and total < 82)
                        or (level >= 3 and total < distance[level])):
                    feasible = False
                    break
            basis = weights[:size - 6]
            killed = False
            if sum(CAP[w] for w in basis) < 53:
                killed = sum(basis) <= 7 or any(
                    all(sum(w for w, a in zip(basis, assignment, strict=True) if a == k)
                        <= 6 for k in (0, 1))
                    for assignment in product((0, 1), repeat=len(basis))
                )
            if feasible and not killed:
                survivors.append(weights)
    require(len(survivors) == 17 and PROFILE in survivors, "original (6,3) residue")
    return survivors


def application():
    survivors = original_survivors()
    no_seven = [row for row in survivors if max(row) <= 6]
    require(len(no_seven) == 6 and all(len(row) == 9 for row in no_seven),
            "original rank-at-most-six residue")
    require(all(all(a <= b for a, b in zip(row, PROFILE, strict=True))
                for row in no_seven), "componentwise consequence")
    small, endpoints = CAP[5] + CAP[6], 7 * CAP[6]
    require(small == 32 and small + 20 < 53 and small + 40 == 72,
            "quotient and edge hypotheses")
    return {"cell": [6, 3], "weights": PROFILE, "small_weights": [5, 6],
            "small_support_cap": small, "quotient_basis_cap": small + 20,
            "edge_support_cap": small + 40, "endpoint_allowance": endpoints,
            "mixed_lower": 142, "root_lower": 141,
            "original_survivors": len(survivors),
            "original_no_seven_profiles": no_seven,
            "scope": "One maximal profile; six original no-seven profiles dominated."
            " Earlier exclusions may already cover some dominated profiles."}


def predecessor_table():
    result = subprocess.run([sys.executable, "-I", "-B", str(PACKAGE / "vendor/bk2b.py")],
                            capture_output=True, text=True, check=True, timeout=120)
    require(not result.stderr and len(result.stdout) <= 4096, "original table output")
    rows = [tuple(map(int, line.split())) for line in result.stdout.splitlines()]
    require(len(rows) == 24 and all(len(row) == 4 for row in rows), "table dimensions")
    require([(r[0], r[1]) for r in rows]
            == [(b, t) for b in range(5, 9) for t in range(1, 7)], "table order")
    require(rows[8][2] == 17, "original (6,3) count")
    return rows


def receipt():
    sources = bind_sources()
    roots, points, labels, coordinates = root_data()
    digest = bind_data(ROOT / DATA, points, labels, sources)
    directions, normals, normal_histogram = alphabet(roots, points)
    symmetries = anchor_orbit(roots, frame_lines(), normals)
    vertices = intersections(directions)
    adjacency = compatibility(vertices, directions)
    root_bound = all_root_six(roots)
    return {
        "schema": "p112-a6-five-flat/v1", "input_sha256": digest,
        "alphabet": {"directions": len(directions), "anchor_symmetries": symmetries,
                     "D7_support_histogram": normal_histogram},
        "mixed": mixed_six(vertices, adjacency, points),
        "all_root": root_bound,
        "weighted": weighted_cover(roots, coordinates, root_bound["representative"]),
        "chamber": chamber_receipt(roots, points, coordinates),
        "root_planes": root_plane_receipt(roots),
        "flat_capacities": [flat_capacity(labels, d) for d in (5, 6)],
        "cover_transfer": exhaustive_transfer(),
        "application": application(), "original_table": predecessor_table(),
    }


def check_receipt(actual, expected):
    require(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "committed mathematical receipt differs")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a new external receipt")
    args = parser.parse_args()
    result = receipt()
    if args.output is None:
        check_receipt(result, json.loads(read_bytes(PACKAGE / "RESULT.json")))
    else:
        output = args.output.expanduser().resolve()
        require(not output.is_relative_to(ROOT), "receipt output must be outside checkout")
        with output.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    print("PASS_A6_FIVE_FLAT profile=5,6^8 mixed=142 root=141 allowance=140 errors=0"
          " six_flats=788035 five_flats=3309747 frames=2025 transfer_subsets=64839")


if __name__ == "__main__":
    main()
