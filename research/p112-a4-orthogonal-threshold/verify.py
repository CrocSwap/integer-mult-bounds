"""Replay the sharp five-endpoint P112 support threshold with exact arithmetic."""

import argparse
import hashlib
import json
from pathlib import Path

from algebra import require
from geometry import chamber_receipt, root_data, root_plane_receipt
from model import orbit_receipt, scalar_receipt, witness_receipt

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parent.parent
ORIGIN = "research/p112-ten-piece-simplex/geometry.py"


def read_json(path):
    require(path.is_file() and not path.is_symlink(), "missing or linked JSON")
    require(path.stat().st_size <= 100_000, "oversized JSON")
    return json.loads(path.read_bytes())


def bind_sources():
    manifest = read_json(PACKAGE / "SOURCES.json")
    rows = [r for r in manifest["files"] if r["path"] == ORIGIN]
    require(len(rows) == 1 and rows[0]["usage"] == "provenance", "geometry provenance")
    retained = manifest["retained_geometry"]
    require(
        retained["local_path"] == "geometry.py" and retained["origin_path"] == ORIGIN,
        "retained geometry path",
    )
    require(
        retained["origin_commit"] == manifest["base_commit"], "geometry origin commit"
    )
    path = PACKAGE / "geometry.py"
    require(path.is_file() and not path.is_symlink(), "missing or linked geometry")
    require(path.stat().st_size <= 20_000, "geometry capacity")
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    blob = hashlib.sha1(
        b"blob " + str(len(raw)).encode() + b"\0" + raw, usedforsecurity=False
    ).hexdigest()
    require(digest == retained["sha256"] == rows[0]["sha256"], "geometry hash")
    require(blob == retained["git_blob"] == rows[0]["git_blob"], "geometry Git blob")


def build():
    bind_sources()
    roots, points, labels, coordinates = root_data()
    result = {
        "schema": "p112-a4-orthogonal-threshold/v1",
        "errors": 0,
        "field": "every characteristic-zero field",
        "chamber": chamber_receipt(roots, points, coordinates),
        "root_planes": root_plane_receipt(roots),
        "a4": orbit_receipt(roots),
        "analytic": scalar_receipt(),
        "witness": witness_receipt(
            roots, points, labels, read_json(PACKAGE / "WITNESS.json")
        ),
        "shortening_threshold": 28,
        "endpoint_support_allowance": 100,
        "required_support_at_28": 101,
        "counterexample_common_support": 29,
        "new_historical_profile_exclusions_claimed": 0,
    }
    return json.loads(json.dumps(result))


def check_receipt(actual, expected):
    require(actual == expected, "committed receipt differs")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a new external receipt")
    args = parser.parse_args()
    result = build()
    if args.output:
        output = args.output.expanduser().resolve()
        require(not output.is_relative_to(REPO), "external output only")
        with output.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        check_receipt(result, read_json(PACKAGE / "RESULT.json"))
    print(
        "PASS_P112_A4_THRESHOLD support=28 demand=101 allowance=100 "
        "counterexample=29 intersection=4 errors=0"
    )


if __name__ == "__main__":
    main()
