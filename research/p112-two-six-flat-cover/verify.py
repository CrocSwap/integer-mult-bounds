"""Certify the sharp fifteen-line supplement for two P112 six-flats."""

import argparse
import hashlib
import json
import subprocess
import sys
from itertools import combinations
from pathlib import Path

from cover import all_root_covers, six_flat_masks
from independent import affine_masks, check_witness
from vendor.geometry import chamber_receipt, require, root_data

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
DATA = "research/one-sided-six-multisets/data/data.txt"
PROFILE = (2, 3, 4) + (6,) * 8


def read_file(path):
    require(
        path.is_file() and not path.is_symlink() and path.stat().st_size <= 2_000_000,
        f"missing, linked or oversized file: {path}",
    )
    return path.read_bytes()


def bind_sources(package=PACKAGE):
    sources = json.loads(read_file(package / "SOURCES.json"))
    retained = sources["retained_files"]
    require(
        len(retained) == 4
        and {r["local_path"] for r in retained}
        == {
            "vendor/geometry.py",
            "vendor/bk2b.py",
            "vendor/NOTICE.md",
            "vendor/LICENSE",
        },
        "retained-source inventory differs",
    )
    for row in retained:
        raw = read_file(package / row["local_path"])
        blob = hashlib.sha1(
            b"blob " + str(len(raw)).encode() + b"\0" + raw, usedforsecurity=False
        ).hexdigest()
        require(
            hashlib.sha256(raw).hexdigest() == row["sha256"]
            and blob == row["git_blob"],
            "retained-source bytes differ",
        )
    return sources


def bind_data(raw, points, labels, sources):
    pins = [r for r in sources["files"] if r["usage"] == "input"]
    require(len(pins) == 1 and pins[0]["path"] == DATA, "live-input inventory differs")
    digest = hashlib.sha256(raw).hexdigest()
    require(digest == pins[0]["sha256"], "P112 source bytes differ")
    lines = raw.decode("utf-8").splitlines()
    require(
        len(lines) >= 114 and tuple(map(int, lines[0].split())) == labels,
        "P112 labels differ",
    )
    require(
        tuple(tuple(map(int, line.split())) for line in lines[2:114]) == points,
        "P112 root coordinates differ",
    )
    return digest


def application():
    # Independently transcribe the fixed profile's necessary size and BK/BK7 gates.
    cap = {2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}
    prefixes = [sum(cap[w] for w in PROFILE[: 5 + level]) for level in range(1, 7)]
    require(prefixes == [74, 94, 114, 134, 154, 174], "application prefix capacities")
    require(
        all(a >= b for a, b in zip(prefixes, (53, 78, 92, 100, 106, 109), strict=True)),
        "profile fails necessary code support gates",
    )
    require(sum(w - 2 for w in PROFILE) == 35, "profile excess")
    basis = (2, 3, 4, 6, 6)
    require(
        sum(cap[w] for w in basis) == 54 and sum(cap[w] for w in basis[:3]) == 14,
        "preferred basis allowance",
    )
    run = subprocess.run(  # noqa: S603 - fixed hash-bound source; see ENGINEERING.md
        [sys.executable, "-I", "-B", str(PACKAGE / "vendor/bk2b.py")],
        capture_output=True,
        text=True,
        check=True,
        timeout=120,
    )
    require(not run.stderr and len(run.stdout) <= 4096, "original filter output")
    table = [list(map(int, line.split())) for line in run.stdout.splitlines()]
    require(
        len(table) == 24
        and all(len(row) == 4 for row in table)
        and [row[:2] for row in table]
        == [[b, t] for b in range(5, 9) for t in range(1, 7)]
        and table[10] == [6, 5, 174, 1],
        "original TWOSIDE table differs",
    )
    # Neither weight-packing rule applies to the five smallest pieces.
    require(
        sum(PROFILE[:5]) > 7 and sum(PROFILE[:5]) > 12,
        "original basis-kill rule applies",
    )
    return {
        "profile": PROFILE,
        "b": 6,
        "t": 5,
        "raw_excess": 35,
        "prefix_capacities": prefixes,
        "preferred_basis": basis,
        "basis_support_cap": 54,
        "extra_cap": 14,
        "remaining_weights": (6,) * 6,
        "minimum_five_piece_support_cap": min(
            sum(cap[w] for w in group) for group in combinations(PROFILE, 5)
        ),
        "original_table": table,
    }


def receipt():
    sources = bind_sources()
    roots, points, labels, coordinates = root_data()
    digest = bind_data(read_file(ROOT / DATA), points, labels, sources)
    masks, primary = six_flat_masks(labels)
    other, independent = affine_masks(labels)
    require(masks == other, "independent complete flat enumerations disagree")
    rows = all_root_covers(roots, points, labels, masks)
    require(all(check_witness(points, labels, row) for row in rows), "witness checks")
    return {
        "schema": "p112-two-six-flat-cover/v1",
        "input_sha256": digest,
        "primary_census": primary,
        "independent_census": independent,
        "flat_mask_sha256": hashlib.sha256(str(masks).encode()).hexdigest(),
        "root_covers": rows,
        "minimum_extra_lines": 15,
        "chamber": chamber_receipt(roots, points, coordinates),
        "application": application(),
    }


def check_receipt(actual, expected):
    require(json.loads(json.dumps(actual)) == expected, "committed receipt differs")


def write_result(result, output):
    output = output.expanduser().resolve()
    require(not output.is_relative_to(ROOT), "output must be outside the checkout")
    with output.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="create a fresh external receipt")
    args = parser.parse_args()
    result = receipt()
    if args.output is None:
        check_receipt(result, json.loads(read_file(PACKAGE / "RESULT.json")))
    else:
        write_result(result, args.output)
    print(
        "PASS_P112_TWO_SIX_FLAT_COVER roots=120 maximum_covered=38 minimum_extra=15 "
        "quotient_basis_cap=54 extra_cap=14"
    )


if __name__ == "__main__":
    main()
