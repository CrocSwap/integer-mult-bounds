#!/usr/bin/env python3
"""Replay the finite certificates supporting the scoped mathematical proofs."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from geometry.verify_geometry import verify as verify_geometry
from search.six_plane_certificate import certificate as six_plane_certificate


def require(condition, message):
    if not condition:
        raise ValueError(message)


def same_saved(actual, path):
    expected = json.loads(path.read_text())
    require(json.loads(json.dumps(actual)) == expected,
            f"Rebuilt certificate differs from {path.name}")


def main():
    require(not sys.flags.optimize, "Run without -O: the exact checks use assertions.")
    sources = json.loads((HERE / "SOURCES.json").read_text())
    repository = HERE.parents[1]
    for source in sources["retained_files"]:
        actual = hashlib.sha256((repository / source["path"]).read_bytes()).hexdigest()
        require(actual == source["sha256"], f"Changed source: {source['path']}")
    print("PASS: retained source pins", flush=True)
    geometry = verify_geometry()
    same_saved(geometry, HERE / "geometry" / "verification.json")
    print("PASS: exact geometry, cost-60 decoder, and hyperplane coefficient identity", flush=True)
    six = six_plane_certificate()
    same_saved(six, HERE / "search" / "six_plane_certificate.json")
    print("PASS: six-plane incidence identities and exact rectangle audit", flush=True)
    require(geometry["line_coordinates_sha256"] == six["line_coordinates_sha256"],
            "Certificate coordinate orders differ")
    print("PASS: Gaussian E8 scoped copy-cost obstructions; unrestricted optimum remains open.")


if __name__ == "__main__":
    main()
